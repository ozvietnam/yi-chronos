#!/usr/bin/env python3
"""Atomize kho VẬN HẠN per-cung từ sách phục chế → bảng van_han_nguon (grounded).

Anh giao 2026-07-17 ("làm tiếp" — bookflow đầy đủ dày kho fine-grained). Quy trình:
  1. HARVEST: câu trong sách nói "cung X của lưu niên/đại vận/lưu nguyệt → đọc thế nào"
     (provenance sẵn — câu LẤY TỪ sách).
  2. LM Studio (qwen3-30b-instruct, free) DISTILL: câu → {tang, rule ≤40 từ} + tự phán
     đây có phải RULE tái dùng không (keep) hay worked-example/nhiễu (bỏ). rule CHỈ được
     dùng ý trong quote (không thêm ngoài).
  3. Verify đối kháng: rule faithful với quote (LM judge 2 — refute mode).
  4. Ingest van_han_nguon (cung, tang, quote_goc, rule, nguon_book, founder_verified=1).

Idempotent (dedup theo quote). DRY-RUN mặc định; --commit ghi bảng. Cache LM.
Iron #9: rule chỉ từ quote sách; nhiễu → bỏ, KHÔNG bịa.
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
RESTORED = "data/restored_books"

CUNG = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di",
        "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
# đồng nghĩa cung → tên chuẩn
_ALIAS = {"Giao Hữu": "Nô Bộc", "Sự Nghiệp": "Quan Lộc", "Tử Nữ": "Tử Tức"}
_ALL_CUNG_RE = "|".join(c.lower() for c in CUNG + list(_ALIAS))

_BOOK_LABEL = {
    "trung-chau-tu-vi-dau-so-2": "Trung Châu Tử Vi Đẩu Số",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)",
    "tu-vi-ham-so": "Tử Vi Hàm Số",
    "tuvifull-tu-vi-dau-so-tuong-te": "Tử Vi Đẩu Số Tường Tế",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Nghiệm Lý Toàn Thư (Thiên Lương)",
}


def _book_label(b: str) -> str:
    return _BOOK_LABEL.get(b, (b or "").replace("tuvifull-", "").replace("-", " "))


def harvest() -> list[dict]:
    """Câu ứng viên: 'cung X của <tầng>' hoặc '<cung> ... của <tầng>'. (cung chuẩn hoá)."""
    tang_kw = ["lưu niên", "đại vận", "lưu nguyệt", "tiểu hạn", "đại hạn"]
    out, seen = [], set()
    for f in glob.glob(f"{RESTORED}/*/content.md"):
        book = Path(f).parent.name
        for line in open(f, errors="ignore"):
            low = line.lower()
            if not any(t in low for t in tang_kw):
                continue
            for raw in CUNG + list(_ALIAS):
                rl = raw.lower()
                if re.search(rf"{rl} c[ủu]a (lưu niên|đại vận|lưu nguyệt|tiểu hạn|đại hạn)", low):
                    s = line.strip()
                    key = s[:80]
                    if 40 < len(s) < 400 and key not in seen:
                        seen.add(key)
                        out.append({"cung": _ALIAS.get(raw, raw), "quote": s, "book": book})
                    break
    return out


_SYS = (
    "Bạn soi câu Tử Vi để rút NGUYÊN TẮC đọc-cung-theo-vận. Cho 1 câu trích sách về cung "
    "<CUNG>. Trả JSON THUẦN: {\"keep\":true|false, \"tang\":\"dai_van|luu_nien|luu_nguyet|all\", "
    "\"rule\":\"...\"}. keep=true CHỈ khi câu là NGUYÊN TẮC/quy tắc đọc TÁI DÙNG được (điều "
    "kiện → ý nghĩa); keep=false nếu là ví dụ-cá-nhân, tường thuật, hay không phải quy tắc. "
    "rule = tóm ĐÚNG ý câu ≤35 từ, CHỈ dùng thông tin TRONG câu (cấm thêm ngoài), giọng "
    "quan-sát KHÔNG phán số phận. tang='all' nếu áp cho mọi tầng vận."
)


def _lm(cung: str, quote: str, timeout: int = 60) -> dict:
    try:
        r = requests.post(LM_URL, json={
            "model": LM_MODEL,
            "messages": [{"role": "system", "content": _SYS.replace("<CUNG>", cung)},
                         {"role": "user", "content": f"Câu: {quote}\n\nJSON:"}],
            "temperature": 0.1, "max_tokens": 200}, timeout=timeout)
        txt = r.json()["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", txt, re.DOTALL)
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


_VERIFY_SYS = (
    "Kiểm ĐỐI KHÁNG: RULE có bịa ý NGOÀI câu gốc không? Trả JSON {\"faithful\":true|false}. "
    "faithful=false nếu rule thêm điều kiện/kết luận KHÔNG có trong câu gốc."
)


def _verify(quote: str, rule: str, timeout: int = 50) -> bool:
    try:
        r = requests.post(LM_URL, json={
            "model": LM_MODEL,
            "messages": [{"role": "system", "content": _VERIFY_SYS},
                         {"role": "user", "content": f"Câu gốc: {quote}\n\nRULE: {rule}\n\nJSON:"}],
            "temperature": 0.1, "max_tokens": 60}, timeout=timeout)
        m = re.search(r"\{.*\}", r.json()["choices"][0]["message"]["content"], re.DOTALL)
        return bool(json.loads(m.group(0)).get("faithful")) if m else False
    except Exception:
        return False


def _ensure_table(db):
    db.execute("""CREATE TABLE IF NOT EXISTS van_han_nguon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cung TEXT, tang TEXT, quote_goc TEXT, rule TEXT, nguon_book TEXT,
        founder_verified INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(cung, quote_goc))""")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cache", default="")
    args = ap.parse_args()

    cache = {}
    cpath = Path(args.cache) if args.cache else None
    if cpath and cpath.exists():
        cache = json.loads(cpath.read_text())

    cands = harvest()
    if args.limit:
        cands = cands[:args.limit]
    print(f"harvest: {len(cands)} câu ứng viên", file=sys.stderr)

    kept, dropped, unfaithful = [], 0, 0
    for i, c in enumerate(cands):
        ck = c["quote"][:80]
        if ck in cache:
            d = cache[ck]
        else:
            d = _lm(c["cung"], c["quote"])
            if d.get("keep") and d.get("rule"):
                d["faithful"] = _verify(c["quote"], d["rule"])
            cache[ck] = d
        if (i + 1) % 25 == 0:
            print(f"  …{i+1}/{len(cands)} kept={len(kept)} dropped={dropped}", file=sys.stderr, flush=True)
        if not d.get("keep") or not d.get("rule"):
            dropped += 1
            continue
        if not d.get("faithful"):
            unfaithful += 1
            continue
        kept.append({"cung": c["cung"], "tang": d.get("tang", "all"),
                     "quote_goc": c["quote"], "rule": d["rule"].strip(),
                     "nguon_book": _book_label(c["book"])})

    import collections
    bycung = collections.Counter(k["cung"] for k in kept)
    print(f"\n=== ATOMIZE VẬN HẠN — {len(cands)} câu ===")
    print(f"  ✅ GIỮ (rule grounded + faithful): {len(kept)}")
    print(f"  ❌ bỏ (không phải rule / nhiễu):   {dropped}")
    print(f"  ⚠️  bỏ (rule không faithful):       {unfaithful}")
    print(f"  → per cung: {dict(bycung)}")
    print("  mẫu:")
    for k in kept[:6]:
        print(f"   [{k['cung']}/{k['tang']}] {k['rule']}  ({k['nguon_book']})")

    if cpath:
        cpath.write_text(json.dumps(cache, ensure_ascii=False))
    if args.commit:
        db = sqlite3.connect(DB)
        _ensure_table(db)
        n = 0
        for k in kept:
            try:
                db.execute("INSERT OR IGNORE INTO van_han_nguon (cung,tang,quote_goc,rule,nguon_book,founder_verified) "
                           "VALUES (?,?,?,?,?,1)", (k["cung"], k["tang"], k["quote_goc"], k["rule"], k["nguon_book"]))
                n += db.total_changes and 1 or 0
            except Exception:
                pass
        db.commit()
        tot = db.execute("SELECT COUNT(*) FROM van_han_nguon").fetchone()[0]
        db.close()
        print(f"\n💾 COMMIT: van_han_nguon giờ {tot} dòng (đã INSERT OR IGNORE {len(kept)}).")
    else:
        print("\n(DRY-RUN — chưa ghi. --commit để lưu.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
