"""Extract cách cục + concepts mới từ phê mệnh sâu V4 Pro → wiki.

Đọc:  data/yi_publishing/analysis_cache/u1/<person>/phe_menh_sau.json
Ghi:  data/yi_wiki/wiki.sqlite3 (concept_index)
       data/tu_vi/cach_cuc_from_deepseek_v4pro.json (structured cache cục)
       data/tu_vi/phu_corpus_from_deepseek_v4pro.json (verbatim quotes)

Strategy:
- Regex-extract quotes Hán-Việt verbatim từ pattern: "Phú vân: ..." hoặc 「...」
- Heuristic: 4-8 chữ phrases with classical syntax → cách cục names
- De-dupe vs existing concept_index canonical_vi
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path

WIKI_DB = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3")
CORPUS_ID = "luan-giai-sau-deepseek-v4-pro"


def load_phe_menh(cache_path: Path) -> dict:
    with cache_path.open() as f:
        return json.load(f)


def extract_quotes(text: str) -> list[dict]:
    """Extract verbatim quotes:
    - "Phú vân: ..." or "Cổ phú: ..." or "Phú: ..."
    - "...": quoted strings with Hán-Việt only (no Latin chars in quote body)
    """
    quotes = []
    # Pattern 1: Phú/Cổ phú/Cổ ngữ + quoted body
    pat1 = re.compile(r'(?:Phú vân|Cổ phú|Cổ ngữ|Phú|Phú gọi|Trần Đoàn vị|Cổ nhân vị)\s*[::]\s*[""""]([^""""]{6,200})[""""]', re.UNICODE)
    for m in pat1.finditer(text):
        body = m.group(1).strip()
        if body:
            quotes.append({"text": body, "type": "phu_quote", "context": text[max(0, m.start()-100):m.start()][:100]})
    # Pattern 2: Bare quoted Hán-Việt phrases
    pat2 = re.compile(r'[""""]([^""""]{6,150})[""""]', re.UNICODE)
    for m in pat2.finditer(text):
        body = m.group(1).strip()
        # Skip if mostly Latin or has too many punctuation
        if re.search(r'[a-zA-Z]', body) or len(body) < 6:
            continue
        # Avoid double-capture from pattern 1
        if any(q["text"] == body for q in quotes):
            continue
        quotes.append({"text": body, "type": "embedded_quote", "context": ""})
    return quotes


def extract_cach_cuc_names(text: str) -> list[str]:
    """Extract cách cục names — heuristic:
    - Phrases ending with 'cách' or 'cục': "X cách", "X cục"
    - "Kỳ N, ... cách." patterns
    - Star compound names: "A B đồng cung", "A B C hội tụ"
    """
    names = set()
    # Pattern: capitalized 4-8 char phrase + "cách" / "cục"
    pat = re.compile(r'([\"""][A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴ][^""""]{4,60})\1?\s*(?:chi\s+)?(?:cách|cục)', re.UNICODE)
    for m in pat.finditer(text):
        name = m.group(1).strip(' """"')
        names.add(name)
    # Simpler: phrases followed by "cách"
    pat2 = re.compile(r'(?:^|[\.,;:\s])([A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰÝỲỶỸỴ][\wÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]{4,40})\s+(?:chi\s+)?cách\b', re.UNICODE)
    for m in pat2.finditer(text):
        name = m.group(1).strip()
        if len(name) >= 4 and len(name) <= 50:
            names.add(name + " cách")
    return sorted(names)


def existing_concepts(db: sqlite3.Connection) -> set[str]:
    rows = db.execute("SELECT canonical_vi FROM concept_index").fetchall()
    return {r[0].strip().lower() for r in rows if r[0]}


def add_concept(db: sqlite3.Connection, *, canonical_vi: str, short_note: str, category: str,
                aliases: list = None, source_section: str = ""):
    now = int(time.time())
    db.execute(
        """INSERT INTO concept_index
           (canonical_vi, canonical_zh, aliases, mentioned_in_passages, short_note,
            first_seen_corpus, first_seen_page, created_at, category, corpora, school)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            canonical_vi,
            "",
            json.dumps(aliases or [], ensure_ascii=False),
            json.dumps([f"{CORPUS_ID}:{source_section}"], ensure_ascii=False),
            short_note[:500],
            CORPUS_ID,
            None,
            now,
            category,
            json.dumps([CORPUS_ID], ensure_ascii=False),
            "tu_vi",
        ),
    )


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: extract_phe_menh_sau_to_wiki.py <cache.json>")
        sys.exit(1)
    cache_path = Path(sys.argv[1])
    cache = load_phe_menh(cache_path)
    person = cache.get("person_name", "?")
    phe = cache.get("phe_menh_sau", {})
    print(f"📚 Loaded: {person} ({len(phe)} sections, {sum(len(v) if isinstance(v, str) else 0 for v in phe.values()):,} chars)")
    print()

    # 1. Extract per-section
    all_quotes = []
    all_cach_cuc = []
    for section_key, section_text in phe.items():
        if section_key.startswith("_") or not isinstance(section_text, str):
            continue
        quotes = extract_quotes(section_text)
        cach_cuc = extract_cach_cuc_names(section_text)
        for q in quotes:
            q["section"] = section_key
            all_quotes.append(q)
        for cc in cach_cuc:
            all_cach_cuc.append({"name": cc, "section": section_key})
        print(f"  {section_key}: {len(quotes)} quotes, {len(cach_cuc)} cách cục candidates")

    # 2. Dedup
    seen_q = set()
    unique_quotes = []
    for q in all_quotes:
        key = q["text"].strip().lower()
        if key in seen_q:
            continue
        seen_q.add(key)
        unique_quotes.append(q)

    seen_c = set()
    unique_cc = []
    for cc in all_cach_cuc:
        key = cc["name"].strip().lower()
        if key in seen_c:
            continue
        seen_c.add(key)
        unique_cc.append(cc)

    print()
    print(f"📊 Total unique:")
    print(f"   Quotes Hán-Việt: {len(unique_quotes)}")
    print(f"   Cách cục names:  {len(unique_cc)}")
    print()

    # 3. Save structured outputs
    out_dir = Path("/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi")
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes_file = out_dir / "phu_corpus_from_deepseek_v4pro.json"
    with quotes_file.open("w") as f:
        json.dump({
            "source": str(cache_path),
            "person": person,
            "generated_at_unix": cache.get("generated_at"),
            "provider": cache.get("provider"),
            "quotes": unique_quotes,
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 Quotes corpus: {quotes_file}")

    cc_file = out_dir / "cach_cuc_from_deepseek_v4pro.json"
    with cc_file.open("w") as f:
        json.dump({
            "source": str(cache_path),
            "person": person,
            "generated_at_unix": cache.get("generated_at"),
            "provider": cache.get("provider"),
            "cach_cuc_candidates": unique_cc,
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 Cách cục candidates: {cc_file}")

    # 4. Add NEW concepts to wiki
    db = sqlite3.connect(WIKI_DB)
    existing = existing_concepts(db)
    print()
    print(f"📖 Wiki has {len(existing)} existing concepts (lowercased keys)")

    added_quotes = 0
    for q in unique_quotes:
        name = q["text"]
        if name.lower().strip() in existing:
            continue
        # Quote = "phú" category
        add_concept(
            db,
            canonical_vi=name,
            short_note=f"Phú thi Hán-Việt từ luận giải sâu V4 Pro (section: {q['section']})",
            category="phú",
            aliases=[],
            source_section=q["section"],
        )
        existing.add(name.lower().strip())
        added_quotes += 1

    added_cc = 0
    for cc in unique_cc:
        name = cc["name"]
        if name.lower().strip() in existing:
            continue
        # Cách cục
        add_concept(
            db,
            canonical_vi=name,
            short_note=f"Cách cục Tử Vi (luận giải V4 Pro — section: {cc['section']})",
            category="cách cục",
            aliases=[],
            source_section=cc["section"],
        )
        existing.add(name.lower().strip())
        added_cc += 1

    db.commit()
    db.close()

    print()
    print(f"✅ Wiki updated:")
    print(f"   + {added_quotes} phú quotes (verbatim Hán-Việt)")
    print(f"   + {added_cc} cách cục names")
    print(f"   Skipped: {len(unique_quotes) - added_quotes + len(unique_cc) - added_cc} (already in wiki)")


if __name__ == "__main__":
    main()
