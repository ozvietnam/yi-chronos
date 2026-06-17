#!/usr/bin/env python3
"""P0 — migrate dữ liệu user từ các file SQLite rời → 1 Postgres (RLS).

Chạy 1 lần khi cutover sang Postgres. Idempotent ở mức "chạy lại sau khi TRUNCATE"
(không tự dedup; mục đích là cutover sạch). Có --dry-run (chỉ đọc + báo cáo) và
verify số dòng nguồn↔đích cuối cùng.

Dùng:
  DATABASE_URL=postgresql+psycopg://yi_app:app@host:5432/yi  \
  python scripts/migrate_sqlite_to_postgres.py --apply-schema --truncate

Nguồn (mặc định theo layout hiện tại):
  data/yi_users/users.sqlite3   → users, user_persons, user_castings,
                                   user_favorites, user_subscriptions
  data/yi_hermes/memory.sqlite3 → user_facts, chat_summaries, glossary_views
"""
from __future__ import annotations

import argparse
import json as _json
import sqlite3
from pathlib import Path

from sqlalchemy import text

from engine.db import apply_schema, get_engine, is_postgres, session_scope

ROOT = Path(__file__).resolve().parent.parent


def _json_or_none(v):
    """Chuẩn hoá giá trị cho cột JSONB: '' / chuỗi không-phải-JSON / None → NULL.
    Tránh `CAST('' AS JSONB)` làm abort cả batch (dữ liệu cũ có thể rỗng)."""
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return _json.dumps(v, ensure_ascii=False)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            _json.loads(s)
        except (ValueError, TypeError):
            return None
        return s
    return None

# (sqlite_file, table, columns, json_columns)
PLAN = [
    ("data/yi_users/users.sqlite3", "users",
     ["user_id", "email", "display_name", "password_hash", "password_salt",
      "role", "default_person_id", "created_at", "last_login_at",
      "must_change_password", "is_suspended", "suspended_at", "suspend_reason",
      "firebase_uid", "phone"], set()),
    ("data/yi_users/users.sqlite3", "user_persons",
     ["id", "user_id", "person_key", "name", "relationship", "gender",
      "birth_datetime_local", "birth_year", "timezone", "birth_place", "notes",
      "created_at", "updated_at"], set()),
    ("data/yi_users/users.sqlite3", "user_castings",
     ["id", "user_id", "method", "subject_person_key", "question", "input_json",
      "result_json", "verdict", "tags", "note", "algo_version", "created_at"],
     {"input_json", "result_json"}),
    ("data/yi_users/users.sqlite3", "user_favorites",
     ["id", "user_id", "kind", "label", "payload_json", "created_at"],
     {"payload_json"}),
    ("data/yi_users/users.sqlite3", "user_subscriptions",
     ["id", "user_id", "feature_id", "tier", "enabled", "expires_at",
      "remaining_uses", "total_uses", "granted_by", "granted_at", "notes"], set()),
    ("data/yi_users/users.sqlite3", "audit_log",
     ["id", "user_id", "actor_user_id", "action", "target_email", "ip_address",
      "user_agent", "details_json", "created_at"], {"details_json"}),
    ("data/yi_users/users.sqlite3", "user_publications",
     ["id", "user_id", "person_key", "pub_type", "title", "file_dir", "formats",
      "total_chars", "cost_usd", "provider", "model", "version", "generated_at",
      "status", "notes"], {"formats"}),
    ("data/yi_users/users.sqlite3", "publication_shares",
     ["id", "publication_id", "token", "created_by", "created_at", "expires_at",
      "access_count", "max_accesses", "note"], set()),
    # sessions: KHÔNG migrate (ephemeral — user đăng nhập lại sau cutover).
    ("data/yi_hermes/memory.sqlite3", "user_facts",
     ["id", "user_id", "fact", "category", "confidence", "source_session_id",
      "notes", "extracted_at"], set()),
    ("data/yi_hermes/memory.sqlite3", "chat_summaries",
     ["id", "user_id", "session_id", "summary", "key_topics", "chart_data_hash",
      "created_at"], {"key_topics"}),
    ("data/yi_hermes/memory.sqlite3", "glossary_views",
     ["id", "user_id", "term_vi", "viewed_at"], set()),
]

SERIAL_TABLES = ["users", "user_persons", "user_castings", "user_favorites",
                 "user_subscriptions", "audit_log", "user_publications",
                 "publication_shares", "user_facts", "chat_summaries",
                 "glossary_views"]


def _sqlite_rows(db_path: Path, table: str, cols: list[str]):
    if not db_path.exists():
        return None  # nguồn không tồn tại → bỏ qua (báo cáo)
    con = sqlite3.connect(db_path)
    try:
        have = {r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}
        if not have:
            return None
        use = [c for c in cols if c in have]
        rows = con.execute(f"SELECT {', '.join(use)} FROM {table}").fetchall()
        return use, rows
    finally:
        con.close()


def migrate(*, dry_run: bool, do_schema: bool, truncate: bool) -> int:
    if not is_postgres():
        raise SystemExit("DATABASE_URL phải trỏ Postgres để migrate (hiện đang SQLite).")

    if do_schema and not dry_run:
        with get_engine().begin() as conn:
            apply_schema(conn)
        print("• schema applied")

    report: list[tuple[str, int, int]] = []
    for rel, table, cols, json_cols in PLAN:
        src = _sqlite_rows(ROOT / rel, table, cols)
        if src is None:
            print(f"  - {table}: nguồn trống/không có ({rel}) → bỏ qua")
            report.append((table, 0, 0))
            continue
        use_cols, rows = src
        n_src = len(rows)
        if dry_run:
            print(f"  - {table}: {n_src} dòng (dry-run, không ghi)")
            report.append((table, n_src, -1))
            continue

        with session_scope(service=True) as conn:
            # SQLite lưu timestamp text ở UTC (CURRENT_TIMESTAMP) → ép phiên UTC để
            # text→TIMESTAMPTZ không bị dịch theo TZ server (lệch +7h ở VN).
            conn.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            if truncate:
                conn.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE"))
            if rows:
                # JSONB: cast text json trong VALUES; cột khác bind thường.
                placeholders = []
                for c in use_cols:
                    placeholders.append(f"CAST(:{c} AS JSONB)" if c in json_cols else f":{c}")
                # ON CONFLICT DO NOTHING → chạy lại an toàn (không trùng PK) kể cả
                # khi KHÔNG --truncate (idempotent cutover, không cần dedup tay).
                sql = (f"INSERT INTO {table} ({', '.join(use_cols)}) "
                       f"VALUES ({', '.join(placeholders)}) ON CONFLICT DO NOTHING")
                params = []
                for r in rows:
                    d = dict(zip(use_cols, r))
                    for jc in json_cols:
                        if jc in d:
                            d[jc] = _json_or_none(d[jc])
                    params.append(d)
                conn.execute(text(sql), params)
        print(f"  ✓ {table}: copied {n_src}")
        report.append((table, n_src, n_src))

    # Sửa sequence sau khi chèn id tường minh (tránh trùng PK về sau).
    if not dry_run:
        with session_scope(service=True) as conn:
            for t in SERIAL_TABLES:
                conn.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{t}','id'), "
                    f"COALESCE((SELECT MAX(id) FROM {t}),1), true)"
                )) if t != "users" else conn.execute(text(
                    "SELECT setval(pg_get_serial_sequence('users','user_id'), "
                    "COALESCE((SELECT MAX(user_id) FROM users),1), true)"
                ))
        print("• sequences synced")

    # Verify đếm dòng nguồn ↔ đích.
    if not dry_run:
        print("\n=== VERIFY (source vs postgres) ===")
        ok = True
        with session_scope(service=True) as conn:
            for table, n_src, _ in report:
                n_dst = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                # Cutover sạch: đích PHẢI bằng nguồn. n_dst != n_src (kể cả lớn hơn =
                # double-load) đều là MISMATCH — '>=' cũ che mất nhân đôi dữ liệu.
                mark = "OK" if n_dst == n_src else "MISMATCH"
                if n_dst != n_src:
                    ok = False
                print(f"  {mark:9} {table}: src={n_src} dst={n_dst}")
        print("RESULT:", "ALL OK" if ok else "HAS MISMATCH")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="chỉ đọc + báo cáo, không ghi")
    ap.add_argument("--apply-schema", action="store_true", help="chạy schema.sql trước")
    ap.add_argument("--truncate", action="store_true", help="TRUNCATE bảng đích trước khi chèn")
    a = ap.parse_args()
    raise SystemExit(migrate(dry_run=a.dry_run, do_schema=a.apply_schema, truncate=a.truncate))
