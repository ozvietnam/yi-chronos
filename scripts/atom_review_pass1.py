#!/usr/bin/env python3
"""Tầng 1 dây chuyền duyệt atoms — MÁY LỌC TẤT ĐỊNH (0 LLM), CHỈ GẮN NHÃN.

Anh ủy quyền 2026-07-02: "bung agent ra duyệt cho anh... bàn duyệt như mớ hỗn độn".
Dây chuyền 3 tầng: (1) máy lọc này → (2) agent Claude duyệt vùng GRAY → (3) áp verdict
+ liên kết thần kinh. Tầng này KHÔNG sửa atomic_questions — ghi nhãn vào bảng audit
`atom_ai_review` (bài học wiki-node-cleanup: pass 1 an toàn chỉ gắn nhãn, 0 xóa).

Nhãn:
- AUTO_PASS   : quote CÓ THẬT trong chunk nguồn (grounded) + câu hỏi sạch + subject hợp lệ
                + không cờ paradigm + không trùng → đủ điều kiện máy xác nhận.
- AUTO_REJECT : CHỈ rác chắc chắn — bản-thừa-trùng-y-hệt / quote rỗng / OCR vỡ nặng /
                question rác. KHÔNG reject vì unground (quote có thể là BẢN DỊCH của
                chunk gốc Hán → tầng agent xét, thà giữ nhầm hơn xóa nhầm).
- GRAY        : còn lại → tầng 2 (agent).

Chạy: .venv/bin/python3 scripts/atom_review_pass1.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from datetime import datetime

DB = "data/yi_wiki/wiki.sqlite3"
BATCH = "pass1-2026-07-02"

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[，。、；：「」『』（）()\[\]【】.,;:!?\"'—–\-…·]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    s = _PUNCT.sub("", s)
    return _WS.sub("", s).lower()


def token_overlap(a: str, b: str) -> float:
    """Tỷ lệ ký tự-2-gram của a có trong b (đo 'quote nằm trong chunk' chịu OCR lệch)."""
    if not a or not b:
        return 0.0
    grams = {a[i:i + 2] for i in range(len(a) - 1)} or {a}
    hit = sum(1 for g in grams if g in b)
    return hit / len(grams)


def ocr_junk_ratio(s: str) -> float:
    if not s:
        return 1.0
    junk = sum(1 for ch in s if ch in "��\x00" or (ch.isascii() and not ch.isprintable()))
    return junk / len(s)


def main() -> None:
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS atom_ai_review (
        atom_id INTEGER PRIMARY KEY,
        pass1_label TEXT,           -- AUTO_PASS / AUTO_REJECT / GRAY
        pass1_reasons TEXT,         -- JSON list lý do
        ground_score REAL,          -- 0..1 quote khớp chunk
        agent_verdict TEXT,         -- tầng 2 điền: pass/fix/reject/needs_founder
        agent_reason TEXT,
        agent_fix_json TEXT,
        applied_at TEXT,            -- tầng 3 điền khi áp vào atomic_questions
        batch TEXT, created_at TEXT)""")
    db.commit()

    # paradigm guard (import trong main để script chạy được cả khi engine đổi)
    try:
        from engine.hermes_guard import paradigm_violations
    except Exception:
        def paradigm_violations(_):  # type: ignore
            return []

    rows = cur.execute("""SELECT a.atom_id, a.question_text, a.source_quote,
                                 a.subject_identifiers, a.founder_verified, c.text
                          FROM atomic_questions a JOIN chunks_v2 c ON a.chunk_id=c.chunk_id
                          """).fetchall()
    print(f"nạp {len(rows)} atoms (join chunk)")

    # trùng y hệt: giữ atom_id nhỏ nhất
    seen: dict[tuple, int] = {}
    dup_extra: set[int] = set()
    for aid, q, quote, *_ in rows:
        key = (norm(q or ""), norm(quote or ""))
        if key in seen:
            dup_extra.add(aid)
        else:
            seen[key] = aid

    now = datetime.now().isoformat(timespec="seconds")
    counts = {"AUTO_PASS": 0, "AUTO_REJECT": 0, "GRAY": 0, "SKIP_FV": 0}
    out = []
    chunk_cache: dict[int, str] = {}

    for aid, q, quote, subj, fv, chunk_text in rows:
        if fv == -1:                       # đã bị loại từ trước — giữ nguyên, không đụng
            counts["SKIP_FV"] += 1
            continue
        reasons = []
        nq, nquote = norm(q or ""), norm(quote or "")
        nchunk = chunk_cache.get(id(chunk_text))
        if nchunk is None:
            nchunk = norm(chunk_text or "")
            chunk_cache[id(chunk_text)] = nchunk

        # ── rác chắc chắn ──
        if aid in dup_extra:
            reasons.append("dup_exact_extra")
        if not nquote:
            reasons.append("quote_rong")
        if ocr_junk_ratio(q or "") > 0.15 or ocr_junk_ratio(quote or "") > 0.15:
            reasons.append("ocr_vo_nang")
        if len(nq) < 8:
            reasons.append("question_qua_ngan")
        if any(t in (q or "") for t in ("TODO", "FIXME", "[MOCK]", "lorem")):
            reasons.append("question_placeholder")
        if reasons:
            out.append((aid, "AUTO_REJECT", json.dumps(reasons, ensure_ascii=False), 0.0,
                        BATCH, now))
            counts["AUTO_REJECT"] += 1
            continue

        # ── groundedness: quote nằm trong chunk? ──
        if nquote and nquote in nchunk:
            score = 1.0
        else:
            score = token_overlap(nquote[:400], nchunk)

        flags = paradigm_violations((q or "") + " " + (quote or ""))
        subj_ok = False
        try:
            sj = json.loads(subj) if subj else []
            subj_ok = bool(sj)
        except Exception:
            subj_ok = False

        if score >= 0.9 and not flags and subj_ok and len(nquote) >= 12:
            out.append((aid, "AUTO_PASS", json.dumps(["grounded", f"score={score:.2f}"],
                                                     ensure_ascii=False), score, BATCH, now))
            counts["AUTO_PASS"] += 1
        else:
            why = []
            if score < 0.9:
                why.append(f"ground={score:.2f}")
            if flags:
                why.append(f"paradigm={flags[:2]}")
            if not subj_ok:
                why.append("subject_thieu")
            if len(nquote) < 12:
                why.append("quote_ngan")
            out.append((aid, "GRAY", json.dumps(why, ensure_ascii=False), score, BATCH, now))
            counts["GRAY"] += 1

    cur.executemany("""INSERT INTO atom_ai_review
                       (atom_id, pass1_label, pass1_reasons, ground_score, batch, created_at)
                       VALUES (?,?,?,?,?,?)
                       ON CONFLICT(atom_id) DO UPDATE SET pass1_label=excluded.pass1_label,
                         pass1_reasons=excluded.pass1_reasons, ground_score=excluded.ground_score,
                         batch=excluded.batch""", out)
    db.commit()
    print("PHÂN LOẠI:", json.dumps(counts, ensure_ascii=False))
    # phân bố GRAY theo lý do chính (để cắt việc tầng 2)
    for r in cur.execute("""SELECT substr(pass1_reasons,1,40), COUNT(*) FROM atom_ai_review
                            WHERE pass1_label='GRAY' GROUP BY 1 ORDER BY 2 DESC LIMIT 8"""):
        print(f"  GRAY {r[1]:6d}  {r[0]}")


if __name__ == "__main__":
    main()
