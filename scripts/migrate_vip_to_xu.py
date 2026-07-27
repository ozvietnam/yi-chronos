#!/usr/bin/env python3
"""Migration: GÓI VIP → 1000 XU (Anh chốt 2026-07-27 "thống nhất 1 hệ tiền tệ").

Mỗi user từng được cấp gói VIP (`user_subscriptions`) nhận **1000 xu** vào ví trung tâm,
thay cho gói đã gỡ. AN TOÀN:
  · IDEMPOTENT — dùng `ref=migrate_vip:<uid>`; chạy lại KHÔNG cộng trùng.
  · DRY-RUN mặc định; phải `--commit` mới ghi.
  · KHÔNG xoá/sửa `user_subscriptions` (giữ làm sổ audit).

Dùng:
    python3 scripts/migrate_vip_to_xu.py                 # xem trước
    python3 scripts/migrate_vip_to_xu.py --commit        # thực thi
    python3 scripts/migrate_vip_to_xu.py --amount 1000   # đổi mức cấp
Chạy trên PROD: đặt DATABASE_URL trỏ Postgres prod trước khi chạy.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import text

from engine import xu_wallet
from engine.db import database_url, session_scope

GRANT_REASON = "migrate_vip"


def _is_pg(conn) -> bool:
    try:
        return conn.engine.dialect.name == "postgresql"
    except Exception:
        return False


def _vip_users() -> list[tuple]:
    """(user_id, email, role, danh sách feature) của user CÓ gói VIP còn bật."""
    with session_scope(service=True) as conn:
        agg = "STRING_AGG(s.feature_id, ',')" if _is_pg(conn) else "GROUP_CONCAT(s.feature_id)"
        rows = conn.execute(text(
            f"""SELECT s.user_id, u.email, u.role, {agg} AS feats
                  FROM user_subscriptions s
                  LEFT JOIN users u ON u.user_id = s.user_id
                 WHERE s.enabled = 1
                 GROUP BY s.user_id, u.email, u.role
                 ORDER BY s.user_id"""
        )).fetchall()
    return [tuple(r) for r in rows]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="ghi thật (mặc định dry-run)")
    ap.add_argument("--amount", type=int, default=1000, help="số xu cấp mỗi user (mặc định 1000)")
    args = ap.parse_args()

    print(f"DB: {database_url()}", file=sys.stderr)
    try:
        users = _vip_users()
    except Exception as e:
        print(f"❌ Không đọc được user_subscriptions: {e}")
        return 1

    if not users:
        print("Không có user nào đang giữ gói VIP → không cần cấp xu.")
        return 0

    print(f"\n=== VIP → {args.amount} XU · {len(users)} user ===")
    granted = skipped = 0
    for uid, email, role, feats in users:
        before = xu_wallet.get_balance(uid)
        tag = " (owner — vốn đã miễn phí)" if role == "owner" else ""
        if not args.commit:
            print(f"  [DRY] user {uid} {email or ''}{tag}: ví {before} → {before + args.amount}"
                  f"  | gói: {feats}")
            continue
        after = xu_wallet.grant(uid, args.amount, GRANT_REASON, ref=f"{GRANT_REASON}:{uid}")
        if after == before:
            skipped += 1
            print(f"  ⏭  user {uid} {email or ''}: đã cấp trước đó (idempotent), ví {after}")
        else:
            granted += 1
            print(f"  ✅ user {uid} {email or ''}{tag}: ví {before} → {after}")

    if args.commit:
        print(f"\n💾 XONG: cấp mới {granted} · bỏ qua (đã cấp) {skipped}")
    else:
        print("\n(DRY-RUN — thêm --commit để thực thi.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
