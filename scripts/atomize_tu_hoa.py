#!/usr/bin/env python3
"""Atomize khung TỨ HÓA PHI TINH từ 'Tinh Hoa Tập Thành' + sách Tứ Hóa → bảng tu_hoa_nguon.

Bước 2 của trụ cột phi-tinh (Anh 2026-07-17). Phục vụ engine `van_han.phi_hoa()`: mỗi thế
tự-hóa / trùng-phùng có câu luận TRÍCH SÁCH đích danh (không chỉ nhãn khung).

Harvest FOCUSED (chỉ rule khung, không text chung): tự hóa · song lộc · lộc-kỵ/kỵ-xung ·
trùng phùng · nghĩa từng Hóa. LM Studio distill {loai, key, rule} + verify đối kháng
faithful → tu_hoa_nguon. Idempotent, DRY-RUN mặc định.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sqlite3
import sys
from pathlib import Path

import requests

DB = "data/yi_wiki/wiki.sqlite3"
LM_URL = "http://localhost:1234/v1/chat/completions"
LM_MODEL = "qwen3-30b-a3b-instruct-2507-mlx"
BOOKS = ("tinh-hoa", "tvdstt2", "tuong-te", "tap-chi-khhb", "tinh-thanh")

# loại rule + mẫu nhận diện (tập trung khung phi tinh)
_PATTERNS = {
    "tu_hoa": re.compile(r"tự hóa (lộc|quyền|khoa|kị|kỵ)"),
    "song_loc": re.compile(r"song lộc"),
    "loc_ky_xung": re.compile(r"(lộc kị|lộc kỵ|kị xung|kỵ xung|lộc.{0,6}xung.{0,6}kị)"),
    "trung_phung": re.compile(r"trùng phùng"),
    "hoa_nghia": re.compile(r"^(hóa lộc|hóa quyền|hóa khoa|hóa kị|hóa kỵ)\b"),
}
_IND = ("chủ", "là ", "thì ", "nghĩa", "biểu", "cho thấy", "tức", "dễ", "phá",
        "cát", "hung", "tốt", "xấu", "nên", "ắt")


def _book_label(book: str) -> str:
    if "tinh-hoa" in book:
        return "Tử Vi Đẩu Số Tinh Hoa Tập Thành"
    if "tvdstt2" in book:
        return "Tử Vi Đẩu Số Toàn Thư (q2)"
    if "tuong-te" in book:
        return "Tử Vi Đẩu Số Tường Tế"
    if "tap-chi-khhb" in book:
        return "Tạp chí KHHB (trước 1975)"
    if "tinh-thanh" in book:
        return "Đẩu Số Tinh Thành"
    return book.replace("tuvifull-", "").replace("-", " ")


def harvest() -> list[dict]:
    out, seen = [], set()
    for f in glob.glob("data/restored_books/*/content.md"):
        book = Path(f).parent.name
        if not any(b in book for b in BOOKS):
            continue
        for line in open(f, errors="ignore"):
            low = line.lower()
            s = line.strip()
            if not (40 < len(s) < 260):
                continue
            if not any(i in low for i in _IND):
                continue
            for loai, pat in _PATTERNS.items():
                if pat.search(low):
                    k = s[:70]
                    if k not in seen:
                        seen.add(k)
                        out.append({"loai": loai, "quote": s, "book": book})
                    break
    return out


_SYS = (
    "Bạn soi câu Tử Vi phái TỨ HÓA để rút NGUYÊN TẮC diễn giải. Câu nói về khung <LOAI>. "
    "Trả JSON THUẦN: {\"keep\":true|false, \"rule\":\"...\"}. keep=true CHỈ khi câu là "
    "QUY TẮC/nghĩa TÁI DÙNG được về Tứ Hóa (tự hóa / song lộc / lộc-kỵ xung / trùng phùng "
    "/ nghĩa một Hóa); keep=false nếu là ví dụ-cá-nhân, tường thuật, không phải quy tắc. "
    "rule = tóm ĐÚNG ý ≤35 từ, CHỈ dùng thông tin TRONG câu, giọng quan-sát không phán số phận."
)
_VSYS = "Kiểm ĐỐI KHÁNG: RULE có bịa ý NGOÀI câu gốc không? Trả JSON {\"faithful\":true|false}."


def _lm(sys: str, user: str, timeout=60) -> dict:
    try:
        r = requests.post(LM_URL, json={"model": LM_MODEL, "messages": [
            {"role": "system", "content": sys}, {"role": "user", "content": user}],
            "temperature": 0.1, "max_tokens": 200}, timeout=timeout)
        m = re.search(r"\{.*\}", r.json()["choices"][0]["message"]["content"], re.DOTALL)
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cache", default="")
    args = ap.parse_args()
    cache, cpath = {}, (Path(args.cache) if args.cache else None)
    if cpath and cpath.exists():
        cache = json.loads(cpath.read_text())

    cands = harvest()
    if args.limit:
        cands = cands[:args.limit]
    print(f"harvest: {len(cands)} câu ứng viên", file=sys.stderr)
    import collections
    print("  theo loại:", dict(collections.Counter(c["loai"] for c in cands)), file=sys.stderr)

    kept, dropped, unfaithful = [], 0, 0
    for i, c in enumerate(cands):
        ck = c["quote"][:80]
        if ck in cache:
            d = cache[ck]
        else:
            d = _lm(_SYS.replace("<LOAI>", c["loai"]), f"Câu: {c['quote']}\n\nJSON:")
            if d.get("keep") and d.get("rule"):
                d["faithful"] = bool(_lm(_VSYS, f"Câu gốc: {c['quote']}\n\nRULE: {d['rule']}\n\nJSON:").get("faithful"))
            cache[ck] = d
        if (i + 1) % 40 == 0:
            print(f"  …{i+1}/{len(cands)} kept={len(kept)}", file=sys.stderr, flush=True)
        if not d.get("keep") or not d.get("rule"):
            dropped += 1
            continue
        if not d.get("faithful"):
            unfaithful += 1
            continue
        kept.append({"loai": c["loai"], "quote_goc": c["quote"],
                     "rule": d["rule"].strip(), "nguon_book": _book_label(c["book"])})

    print(f"\n=== ATOMIZE TỨ HÓA — {len(cands)} câu ===")
    print(f"  ✅ GIỮ: {len(kept)} · ❌ bỏ nhiễu: {dropped} · ⚠️ không-faithful: {unfaithful}")
    print(f"  theo loại: {dict(collections.Counter(k['loai'] for k in kept))}")
    for k in kept[:6]:
        print(f"   [{k['loai']}] {k['rule']}  ({k['nguon_book']})")

    if cpath:
        cpath.write_text(json.dumps(cache, ensure_ascii=False))
    if args.commit:
        db = sqlite3.connect(DB)
        db.execute("""CREATE TABLE IF NOT EXISTS tu_hoa_nguon (
            id INTEGER PRIMARY KEY AUTOINCREMENT, loai TEXT, quote_goc TEXT, rule TEXT,
            nguon_book TEXT, founder_verified INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(loai, quote_goc))""")
        db.executemany("INSERT OR IGNORE INTO tu_hoa_nguon (loai,quote_goc,rule,nguon_book,founder_verified) "
                       "VALUES (?,?,?,?,1)", [(k["loai"], k["quote_goc"], k["rule"], k["nguon_book"]) for k in kept])
        db.commit()
        tot = db.execute("SELECT COUNT(*) FROM tu_hoa_nguon").fetchone()[0]
        db.close()
        print(f"\n💾 COMMIT: tu_hoa_nguon giờ {tot} dòng.")
    else:
        print("\n(DRY-RUN — --commit để lưu.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
