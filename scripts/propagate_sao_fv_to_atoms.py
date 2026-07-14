#!/usr/bin/env python3
"""Truyền verdict duyệt đối kháng (sao_noi_dung.founder_verified) xuống atom RAG.

2603 atom `extracted_by='sao_noi_dung_v1'` trong atomic_questions ĐANG gắn fv=1 hàng
loạt (kể cả 165 dòng BỊA + 602 dòng TREO mà pipeline verify_sao_noi_dung.py vừa bắt).
Retriever council/sage lọc `founder_verified >= 0` → atom bịa (nếu để fv=1) VẪN lọt.

Fix: đồng bộ atom.fv = sao_noi_dung.fv của dòng nguồn. 165 bịa → -1 (retriever loại);
602 treo → 0 (honest, vẫn retrieve được vì filter >=0 — không phải bịa); 1836 giữ 1.

Khớp atom↔row: source_quote == quote_goc. 109 nhóm quote_goc TRÙNG → disambiguate bằng
`dich_thuan_viet` (question_text nhúng phần đầu dich). CHỈ đổi khi khớp DUY NHẤT — nhập
nhằng thì bỏ qua (log), KHÔNG đoán bừa.

Idempotent. DRY-RUN mặc định. --commit mới ghi.
"""
from __future__ import annotations

import argparse
import sqlite3

DB = "data/yi_wiki/wiki.sqlite3"


def _norm(s: str) -> str:
    return " ".join((s or "").split())[:50].lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    # atom sao_noi_dung_v1: index theo source_quote → [(atom_id, question_text_norm)]
    atoms: dict[str, list[tuple]] = {}
    for r in db.execute(
        "SELECT atom_id, source_quote, question_text FROM atomic_questions "
        "WHERE extracted_by='sao_noi_dung_v1'"):
        atoms.setdefault(r["source_quote"] or "", []).append(
            (r["atom_id"], (r["question_text"] or "").lower()))

    # MIRROR toàn bộ: atom.fv = sao_noi_dung.fv của dòng nguồn (idempotent — dòng đã
    # khớp sẵn thì UPDATE no-op). Xử tất cả để cứu-rồi (0→1) cũng đồng bộ xuống atom.
    rows = db.execute(
        "SELECT quote_goc, dich_thuan_viet, founder_verified FROM sao_noi_dung").fetchall()

    updates: list[tuple] = []
    stats = {"matched": 0, "ambiguous": 0, "no_atom": 0, "to_-1": 0, "to_0": 0, "to_1": 0}
    for r in rows:
        cands = atoms.get(r["quote_goc"] or "", [])
        if not cands:
            stats["no_atom"] += 1
            continue
        dich_key = _norm(r["dich_thuan_viet"])
        # khớp: atom có question_text chứa phần đầu dich (disambiguate quote trùng)
        hits = [aid for aid, qt in cands if dich_key and dich_key in qt] if dich_key else []
        if len(hits) != 1:
            # nếu chỉ 1 candidate cho quote này thì vẫn khớp được (không trùng)
            if len(cands) == 1:
                hits = [cands[0][0]]
            else:
                stats["ambiguous"] += 1
                continue
        updates.append((r["founder_verified"], hits[0]))
        stats[{1: "to_1", 0: "to_0", -1: "to_-1"}[r["founder_verified"]]] += 1
        stats["matched"] += 1

    print("=== MIRROR verdict sao_noi_dung → atom RAG ===")
    print(f"  sao_noi_dung rows: {len(rows)}")
    print(f"  khớp atom duy nhất: {stats['matched']}  (→1: {stats['to_1']} · →0: {stats['to_0']} · →-1: {stats['to_-1']})")
    print(f"  nhập nhằng (bỏ qua):  {stats['ambiguous']}")
    print(f"  không thấy atom:      {stats['no_atom']}")

    # trước/sau distribution
    before = db.execute(
        "SELECT founder_verified,COUNT(*) FROM atomic_questions "
        "WHERE extracted_by='sao_noi_dung_v1' GROUP BY founder_verified").fetchall()
    print(f"  atom fv TRƯỚC: {[tuple(x) for x in before]}")

    if args.commit:
        db.executemany(
            "UPDATE atomic_questions SET founder_verified=? WHERE atom_id=?", updates)
        db.commit()
        after = db.execute(
            "SELECT founder_verified,COUNT(*) FROM atomic_questions "
            "WHERE extracted_by='sao_noi_dung_v1' GROUP BY founder_verified").fetchall()
        print(f"  atom fv SAU:   {[tuple(x) for x in after]}")
        print(f"💾 COMMIT: cập nhật {len(updates)} atom.")
    else:
        print("(DRY-RUN — chưa ghi. Thêm --commit để lưu.)")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
