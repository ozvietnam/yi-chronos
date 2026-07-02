#!/usr/bin/env python3
"""Tầng 3 dây chuyền duyệt atoms — ÁP VERDICT + LIÊN KẾT THẦN KINH.

Anh ủy quyền 2026-07-02 ("bung agent ra duyệt cho anh"). Nguồn verdict:
- Tầng 1/1.5 (máy tất định): bảng atom_ai_review.pass1_label (AUTO_PASS/AUTO_REJECT/GRAY)
- Tầng 2 (Claude agents + đối kháng): file JSON verdicts (pass/fix/reject/needs_founder)

Chính sách áp (audit đầy đủ trong atom_ai_review):
- PASS  → founder_verified=1, confidence=0.93  (phân biệt tay-Anh 0.98 — sage vẫn ưu tiên fv=1)
- FIX   → cập nhật question/quote theo agent (bản gốc lưu agent_fix_json), fv=1, conf=0.90
- REJECT→ founder_verified=-1, confidence=0.0  (chỉ những reject ĐÃ qua đối kháng)
- NEEDS_FOUNDER → fv=0 giữ nguyên — đội chờ Anh thu về nhúm nhỏ, bàn duyệt hết hỗn độn.

Liên kết thần kinh:
- atom (fv=1) → concept_index qua subject_identifiers (norm match canonical_vi/zh/aliases)
  ghi atom_relations (from_atom_id → to_concept_id, type 'nói-về', extracted_by atom_linker_v1).
  build_obsidian không ảnh hưởng (nó chỉ đọc hàng from_concept_id NOT NULL).

Usage:
  .venv/bin/python3 scripts/atom_review_apply.py --verdicts <file.json> [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from datetime import datetime
from pathlib import Path

DB = "data/yi_wiki/wiki.sqlite3"
_WS = re.compile(r"\s+")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return _WS.sub(" ", s).strip().lower().replace("đ", "d")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    verdicts = json.loads(Path(a.verdicts).read_text(encoding="utf-8"))
    if isinstance(verdicts, dict):
        verdicts = verdicts.get("verdicts") or []
    print(f"agent verdicts: {len(verdicts)}")

    db = sqlite3.connect(DB)
    db.execute("PRAGMA busy_timeout=30000")
    cur = db.cursor()
    now = datetime.now().isoformat(timespec="seconds")

    # ── 1. áp verdict agent (vùng GRAY) ──────────────────────────────────────
    n_agent = {"pass": 0, "fix": 0, "reject": 0, "needs_founder": 0}
    for v in verdicts:
        aid = v.get("atom_id")
        vd = v.get("verdict")
        if not aid or vd not in n_agent:
            continue
        n_agent[vd] += 1
        cur.execute("""UPDATE atom_ai_review SET agent_verdict=?, agent_reason=?,
                       agent_fix_json=?, applied_at=? WHERE atom_id=?""",
                    (vd, v.get("reason"),
                     json.dumps({k: v[k] for k in ("fix_question", "fix_quote") if v.get(k)},
                                ensure_ascii=False) if (v.get("fix_question") or v.get("fix_quote")) else None,
                     now, aid))
        if a.dry_run:
            continue
        if vd == "pass":
            cur.execute("UPDATE atomic_questions SET founder_verified=1, confidence=0.93 WHERE atom_id=?", (aid,))
        elif vd == "fix":
            if v.get("fix_question"):
                cur.execute("UPDATE atomic_questions SET question_text=? WHERE atom_id=?",
                            (v["fix_question"], aid))
            if v.get("fix_quote"):
                cur.execute("UPDATE atomic_questions SET source_quote=? WHERE atom_id=?",
                            (v["fix_quote"], aid))
            cur.execute("UPDATE atomic_questions SET founder_verified=1, confidence=0.90 WHERE atom_id=?", (aid,))
        elif vd == "reject":
            cur.execute("UPDATE atomic_questions SET founder_verified=-1, confidence=0.0 WHERE atom_id=?", (aid,))
        # needs_founder: giữ fv=0

    # ── 2. áp nhãn máy (AUTO_PASS / AUTO_REJECT chưa áp) ─────────────────────
    if not a.dry_run:
        cur.execute("""UPDATE atomic_questions SET founder_verified=1, confidence=0.93
                       WHERE founder_verified=0 AND atom_id IN
                         (SELECT atom_id FROM atom_ai_review
                          WHERE pass1_label='AUTO_PASS' AND agent_verdict IS NULL)""")
        n_auto_pass = cur.rowcount
        cur.execute("""UPDATE atomic_questions SET founder_verified=-1, confidence=0.0
                       WHERE founder_verified=0 AND atom_id IN
                         (SELECT atom_id FROM atom_ai_review
                          WHERE pass1_label='AUTO_REJECT' AND agent_verdict IS NULL)""")
        n_auto_rej = cur.rowcount
        cur.execute("""UPDATE atom_ai_review SET applied_at=?
                       WHERE applied_at IS NULL AND pass1_label IN ('AUTO_PASS','AUTO_REJECT')""",
                    (now,))
    else:
        n_auto_pass = n_auto_rej = 0
    db.commit()
    print(f"áp agent: {n_agent}")
    print(f"áp máy: AUTO_PASS={n_auto_pass}, AUTO_REJECT={n_auto_rej}")

    # ── 3. liên kết thần kinh: atom(fv=1) → concept ──────────────────────────
    def _aliases(a) -> list:
        if not a:
            return []
        try:
            v = json.loads(a)
            return v if isinstance(v, list) else [str(v)]
        except Exception:
            return [x.strip() for x in str(a).split(",") if x.strip()]

    lookup: dict[str, int] = {}
    for cid, cv, cz, aliases in cur.execute(
            "SELECT concept_id, canonical_vi, canonical_zh, aliases FROM concept_index"):
        for t in [cv, cz] + _aliases(aliases):
            if t and len(str(t)) >= 2:
                lookup.setdefault(norm(str(t)), cid)
    print(f"concept lookup: {len(lookup)} tên")

    existing = {(r[0], r[1]) for r in cur.execute(
        "SELECT from_atom_id, to_concept_id FROM atom_relations "
        "WHERE extracted_by='atom_linker_v1'")}
    rows = cur.execute("""SELECT atom_id, subject_identifiers FROM atomic_questions
                          WHERE founder_verified=1""").fetchall()
    ins, miss = [], 0
    for aid, subj in rows:
        try:
            names = json.loads(subj) if subj else []
        except Exception:
            continue
        for nm_raw in names:
            cid = lookup.get(norm(str(nm_raw)))
            if cid is None:
                miss += 1
                continue
            if (aid, cid) in existing:
                continue
            existing.add((aid, cid))
            # to_atom_id NOT NULL → mirror concept id (convention wiki_connect_v1);
            # from_concept_id để NULL nên build_obsidian bỏ qua (chỉ đọc concept→concept).
            ins.append((aid, cid, cid, "nói-về",
                        f"subject '{nm_raw}' khớp concept #{cid}", 0.9,
                        "atom_linker_v1", now))
    if not a.dry_run and ins:
        cur.executemany("""INSERT INTO atom_relations
                           (from_atom_id, to_atom_id, to_concept_id, relation_type, rationale,
                            confidence, extracted_by, created_at)
                           VALUES (?,?,?,?,?,?,?,?)""", ins)
        db.commit()
    print(f"liên kết atom→concept MỚI: {len(ins)} (subject không khớp concept: {miss})")

    # ── 4. tổng kết trạng thái kho ───────────────────────────────────────────
    print("\n═══ KHO SAU KHI ÁP ═══")
    for r in cur.execute("SELECT founder_verified, COUNT(*) FROM atomic_questions GROUP BY 1"):
        print(f"  fv={r[0]}: {r[1]}")
    nrel, = cur.execute("SELECT COUNT(*) FROM atom_relations").fetchone()
    print(f"  atom_relations tổng: {nrel}")
    print("  integrity:", db.execute("PRAGMA integrity_check").fetchone()[0])


if __name__ == "__main__":
    main()
