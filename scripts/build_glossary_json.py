"""Build static glossary JSON cho frontend tooltip.

Extract từ wiki:
- 14 chính tinh + phụ tinh + sát tinh + thần sát (category='sao')
- 12 cung (category='cung')
- Tứ hóa (category='hóa')
- Cách cục thường gặp (category='cách cục' or 'biến cách')
- Phú thi tiêu biểu (category='phú', short)

Output: data/yi_wiki/glossary_tu_vi.json
Format:
  {
    "sao": {"Tử Vi": {"zh": "紫微", "note": "..."}, ...},
    "cung": {...},
    "hoa": {...},
    "cach_cuc": {...},
    "version": 1, "generated_at": ...
  }
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

WIKI_DB = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3")
OUT_JSON = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/glossary_tu_vi.json")


def fetch_by_category(db, category: str, school_filter: bool = True) -> dict:
    """Return {canonical_vi: {zh, note, aliases}}."""
    sql = """SELECT canonical_vi, canonical_zh, short_note, aliases FROM concept_index
             WHERE category = ?"""
    params = [category]
    if school_filter:
        sql += " AND (school = 'tu_vi' OR school IS NULL)"
    rows = db.execute(sql, params).fetchall()
    out = {}
    for r in rows:
        name = (r[0] or "").strip()
        if not name:
            continue
        zh = r[1] or ""
        note = (r[2] or "").strip()
        try:
            aliases = json.loads(r[3]) if r[3] else []
        except Exception:
            aliases = []
        # Skip really long entries (these are phú thi, not glossary terms)
        if len(name) > 40:
            continue
        out[name] = {"zh": zh, "note": note[:300], "aliases": aliases}
    return out


def main():
    db = sqlite3.connect(WIKI_DB)
    glossary = {
        "sao": fetch_by_category(db, "sao"),
        "cung": fetch_by_category(db, "cung"),
        "hoa": fetch_by_category(db, "hóa"),
        "cach_cuc": fetch_by_category(db, "cách cục"),
        "bien_cach": fetch_by_category(db, "biến cách"),
        "version": 2,
        "generated_at": int(time.time()),
        "generated_at_human": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    db.close()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    print(f"✅ Wrote {OUT_JSON}")
    print(f"   Sao: {len(glossary['sao'])} entries")
    print(f"   Cung: {len(glossary['cung'])} entries")
    print(f"   Hóa: {len(glossary['hoa'])} entries")
    print(f"   Cách cục: {len(glossary['cach_cuc'])} entries")
    print(f"   Biến cách: {len(glossary['bien_cach'])} entries")
    print(f"   Total: {sum(len(glossary[k]) for k in ['sao','cung','hoa','cach_cuc','bien_cach'])} terms")
    print(f"   File size: {OUT_JSON.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
