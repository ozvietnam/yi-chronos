#!/usr/bin/env python3
"""Duyệt ĐỐI KHÁNG kho sao_noi_dung (B4 vòng sao) — Anh chốt 2026-07-03.

Anh ủy quyền em tự duyệt lô atom máy-sinh, VERIFY ĐỐI KHÁNG TRƯỚC ([[feedback_la_so_gon_wiki_sau]]).
2 lớp đối kháng, đặt founder_verified=1 CHỈ khi qua CẢ HAI:

  Lớp 1 — PROVENANCE (xác định, free): quote_goc có THẬT trong sách nguồn không?
    → chống bịa quote (rủi ro #1 quote-or-silence). Khớp shingle với text sách
    (chunks_v2 theo book_corpus_id, fallback data/restored_books/<book>/content.md).

  Lớp 2 — LLM ĐỐI KHÁNG (LM Studio qwen3-30b-instruct, free local): bản DỊCH
    (dich_thuan_viet) có TRUNG THÀNH với quote_goc không, hay thêm/bịa ý mới?

Quyết: provenance>=THRESH AND verdict='faithful' → founder_verified=1 (duyệt).
       provenance FAIL rõ (quote Việt không có trong sách) HOẶC verdict='fabricated'
         → founder_verified=-1 (loại, ghi log).
       còn lại → 0 (treo, chưa đủ chắc để hiện).

Idempotent. Mặc định DRY-RUN (chỉ in thống kê). --commit mới ghi DB.
Iron #7: KHÔNG đụng file DB gitignored qua git; ghi trực tiếp sqlite.

Dùng:
  python3 scripts/verify_sao_noi_dung.py --lop def                 # dry-run def
  python3 scripts/verify_sao_noi_dung.py --lop def --commit        # ghi kết quả
  python3 scripts/verify_sao_noi_dung.py --lop def --limit 20      # thử 20 dòng
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import requests

DB = "data/yi_wiki/wiki.sqlite3"
LM_URL = "http://localhost:1234/v1/chat/completions"
LM_MODEL = "qwen3-30b-a3b-instruct-2507-mlx"
PROV_THRESH = 0.85          # shingle-coverage tối thiểu coi là "quote có trong sách"
PROV_ABSENT = 0.15          # nguồn ĐỦ DÀY mà dưới mức này = quote gần như VẮNG → loại
MIN_SOURCE = 20000          # ký tự tối thiểu để coi nguồn "đủ dày để kết luận vắng/có"
RECOVER_PROV = 0.30         # --recover: quote khớp MỘT PHẦN (paraphrase có cấu trúc, chứa
                            # '...'/'|' làm vỡ verbatim NHƯNG nội dung có trong sách) → grounded-đủ
RESTORED_DIR = Path("data/restored_books")

_VN = ("àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ")
_KEEP = re.compile(r"[^0-9a-z" + _VN + r"一-鿿]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    return _KEEP.sub("", s)


def shingles(s: str, k: int = 8, step: int = 3):
    return [s[i:i + k] for i in range(0, max(0, len(s) - k + 1), step)] or ([s] if s else [])


# ── Lớp 1: provenance ─────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _book_text(db_path: str) -> dict[str, str]:
    db = sqlite3.connect(db_path)
    out: dict[str, list[str]] = {}
    for b, t in db.execute("SELECT book_corpus_id, text FROM chunks_v2"):
        out.setdefault(b, []).append(t or "")
    db.close()
    return {b: norm(" ".join(v)) for b, v in out.items()}


@lru_cache(maxsize=64)
def _restored_text(book: str) -> str:
    p = RESTORED_DIR / book / "content.md"
    if not p.exists():
        return ""
    try:
        return norm(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return ""


def provenance(quote: str, book: str) -> tuple[float, str, int]:
    """Trả (score, source_used, source_len). score = tỉ lệ shingle quote thấy trong sách.

    source_len = độ dày text nguồn (để phân biệt 'sách mỏng không kết luận được' vs
    'sách dày mà quote vắng = nghi bịa'). Iron #9 / feedback_quote_or_silence: KHÔNG
    loại oan quote thật chỉ vì em thiếu bản index của sách đó.
    """
    q = norm(quote)
    if len(q) < 12:
        return (-1.0, "too_short", 0)
    txt = _book_text(DB).get(book, "")
    used = "chunks_v2"
    if len(txt) < MIN_SOURCE:                       # chunks mỏng → thử restored content.md
        rtxt = _restored_text(book)
        if len(rtxt) > len(txt):
            txt, used = rtxt, "content.md"
    if not txt:
        return (-2.0, "no_source", 0)
    sh = shingles(q)
    hit = sum(1 for x in sh if x in txt)
    return (hit / len(sh), used, len(txt))


# ── Lớp 2: LLM đối kháng ──────────────────────────────────────────────────────
_SYS = (
    "Bạn là người soi xét ĐỐI KHÁNG bản dịch Tử Vi Hán-Việt. Nhiệm vụ DUY NHẤT: "
    "phát hiện bản DỊCH có THÊM ý / BỊA nghĩa / SAI lệch so với QUOTE gốc không. "
    "KHÔNG khen. Nghi ngờ mặc định. Chỉ trả JSON thuần: "
    '{\"verdict\":\"faithful|drift|fabricated\",\"reason\":\"tiếng Việt, <25 từ\"}. '
    "faithful=dịch sát, không thêm ý; drift=thêm/bớt nhẹ nhưng không sai gốc; "
    "fabricated=bịa ý mới KHÔNG có trong quote gốc, hoặc mâu thuẫn quote gốc."
)


def llm_judge(quote: str, dich: str, timeout: int = 90) -> tuple[str, str]:
    user = f"QUOTE gốc:\n{quote}\n\nBẢN DỊCH:\n{dich}\n\nSoi đối kháng. Trả JSON."
    try:
        r = requests.post(LM_URL, json={
            "model": LM_MODEL,
            "messages": [{"role": "system", "content": _SYS}, {"role": "user", "content": user}],
            "temperature": 0.1, "max_tokens": 250,
        }, timeout=timeout)
        txt = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return ("error", f"llm_call:{str(e)[:60]}")
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    if not m:
        return ("error", "no_json")
    try:
        d = json.loads(m.group(0))
        v = str(d.get("verdict", "")).lower()
        if v not in ("faithful", "drift", "fabricated"):
            return ("error", f"bad_verdict:{v}")
        return (v, str(d.get("reason", ""))[:120])
    except Exception:
        return ("error", "json_parse")


# ── Quyết định ────────────────────────────────────────────────────────────────
def decide(prov: float, src_len: int, verdict: str) -> int:
    """→ founder_verified: 1 duyệt · -1 loại · 0 treo.

    Chỉ LOẠI khi có bằng chứng: (a) nguồn ĐỦ DÀY mà quote gần-như-vắng (nghi bịa quote),
    hoặc (b) LLM bắt dịch BỊA ý. Thiếu nguồn / mỏng / mơ hồ → TREO (không loại oan).
    """
    if verdict == "fabricated":                       # dịch bịa ý mới → loại
        return -1
    if src_len >= MIN_SOURCE and 0 <= prov < PROV_ABSENT:
        return -1                                     # sách dày mà quote vắng → nghi bịa quote
    if prov >= PROV_THRESH and verdict in ("faithful", "drift"):
        return 1        # DUYỆT: quote thật + dịch KHÔNG bịa (drift = gloss lành, có quote gốc kèm)
    return 0                                          # còn lại: treo (chưa đủ chắc/thiếu nguồn)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lop", default="def", choices=["def", "cung", "ket_hop", "all"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--no-llm", action="store_true", help="chỉ chạy lớp provenance")
    ap.add_argument("--cache", default="", help="đường dẫn json cache verdict LLM (tái dùng qua lần chạy)")
    ap.add_argument("--recover", action="store_true",
                    help="CỨU dòng TREO (fv=0): hạ ngưỡng provenance→0.30 (nhận paraphrase grounded), "
                         "vẫn qua LLM judge. CHỈ nâng 0→1, KHÔNG đụng ±1 sẵn có.")
    args = ap.parse_args()

    import hashlib
    cache: dict = {}
    cache_path = Path(args.cache) if args.cache else None
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}

    def _ckey(rid, quote, dich) -> str:
        h = hashlib.md5((str(quote) + "||" + str(dich)).encode()).hexdigest()[:12]
        return f"{rid}:{h}"

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    if args.recover:
        # CỨU: chỉ dòng TREO (fv=0), mọi lớp.
        where, params = "WHERE founder_verified=0", ()
    elif args.lop == "all":
        where, params = "", ()
    else:
        where, params = "WHERE lop=?", (args.lop,)
    q = f"SELECT id, sao_vi, lop, quote_goc, dich_thuan_viet, nguon_book FROM sao_noi_dung {where} ORDER BY id"
    rows = db.execute(q, params).fetchall()
    if args.limit:
        rows = rows[:args.limit]
    llm_gate = RECOVER_PROV if args.recover else PROV_THRESH

    counts = {"approve": 0, "reject": 0, "hold": 0}
    reject_log, approve_by_sao = [], {}
    updates = []
    for i, r in enumerate(rows):
        prov, src, slen = provenance(r["quote_goc"], r["nguon_book"])
        verdict, reason = ("skip", "no-llm")
        # LLM chỉ chạy khi provenance đủ ngưỡng (tiết kiệm) + có bản dịch
        if not args.no_llm and prov >= llm_gate and (r["dich_thuan_viet"] or "").strip():
            ck = _ckey(r["id"], r["quote_goc"], r["dich_thuan_viet"])
            if ck in cache:
                verdict, reason = cache[ck]["verdict"], cache[ck]["reason"]
            else:
                verdict, reason = llm_judge(r["quote_goc"] or "", r["dich_thuan_viet"] or "")
                if verdict != "error":
                    cache[ck] = {"verdict": verdict, "reason": reason}
        if args.no_llm:
            eff = "faithful"                       # chế độ chỉ-provenance
        elif verdict in ("skip", "error"):
            eff = "drift"                           # không kiểm được dịch → treo (nếu prov không loại)
        else:
            eff = verdict
        if args.recover:
            # CỨU: nội dung có-mặt (prov>=0.30) + dịch không bịa → nâng 0→1; còn lại GIỮ treo.
            fv = 1 if (prov >= RECOVER_PROV and eff in ("faithful", "drift")) else 0
        else:
            fv = decide(prov, slen, eff)
        if fv == 1:
            counts["approve"] += 1
            approve_by_sao[r["sao_vi"]] = approve_by_sao.get(r["sao_vi"], 0) + 1
        elif fv == -1:
            counts["reject"] += 1
            if len(reject_log) < 40:
                reject_log.append((r["sao_vi"], r["nguon_book"], round(prov, 2), verdict, reason,
                                   (r["quote_goc"] or "")[:70]))
        else:
            counts["hold"] += 1
        updates.append((fv, r["id"]))
        if (i + 1) % 50 == 0:
            print(f"  …{i+1}/{len(rows)}  approve={counts['approve']} reject={counts['reject']} hold={counts['hold']}",
                  file=sys.stderr, flush=True)

    print(f"\n=== LỚP {args.lop} — {len(rows)} dòng ===")
    print(f"  ✅ DUYỆT (fv=1):  {counts['approve']}")
    print(f"  ❌ LOẠI  (fv=-1): {counts['reject']}")
    print(f"  ⏳ TREO  (fv=0):  {counts['hold']}")
    print(f"  → sao có ≥1 dòng duyệt: {len(approve_by_sao)}/104")
    print("\n=== mẫu LOẠI (đối kháng bắt được) ===")
    for e in reject_log[:15]:
        print("  ", e)

    if cache_path:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False))
        print(f"  (cache verdict: {len(cache)} mục → {cache_path})")

    if args.commit:
        db.executemany("UPDATE sao_noi_dung SET founder_verified=? WHERE id=?", updates)
        db.commit()
        print(f"\n💾 COMMIT: cập nhật {len(updates)} dòng founder_verified.")
    else:
        print("\n(DRY-RUN — chưa ghi DB. Thêm --commit để lưu.)")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
