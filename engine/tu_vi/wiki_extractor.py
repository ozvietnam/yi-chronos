"""Auto-extract concepts/cách cục từ phê mệnh sâu output → wiki.sqlite3.

Workflow:
1. Sau mỗi lần `phe_menh_sau()` gen mới → hook gọi `extract_phe_menh_to_wiki(data)`
2. Parse 10 sections, extract:
   - Hán-Việt quote phrases (between curly/straight quotes, 6-150 chars, no Latin)
   - "X cách" / "X cục" patterns (cách cục names)
   - Sao + cung pairs (cross-ref existing concepts)
3. De-dupe vs existing concept_index (canonical_vi lowercase match)
4. Upsert NEW only with corpus_id = "luan-giai-deepseek-v4-pro"

Idempotent: chạy nhiều lần OK, không trùng lặp.
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Optional

WIKI_DB = Path(__file__).resolve().parent.parent.parent / "data/yi_wiki/wiki.sqlite3"
CORPUS_ID = "luan-giai-deepseek-v4-pro"


def _existing_canonical_vi(db: sqlite3.Connection) -> set[str]:
    """Set of all canonical_vi (lowercased trimmed) currently in wiki."""
    rows = db.execute("SELECT canonical_vi FROM concept_index").fetchall()
    return {r[0].strip().lower() for r in rows if r[0]}


def _extract_quotes(text: str) -> list[dict]:
    """Extract Hán-Việt verbatim quotes — supports multi-line + multiple quote chars."""
    quotes = []
    # All Vietnamese quote variations: straight " ' curly “ ” „ ‟ « »
    QUOTE_CHARS = r'["‘’‚‛“”„‟«»`]'
    # Pattern 1: Lead phrase + colon + quoted block (multiline OK with DOTALL)
    pat1 = re.compile(
        rf'(?:Phú\s+vân|Cổ\s+phú|Cổ\s+ngữ|Cổ\s+nhân\s+vị|Cổ\s+nhân\s+nói|Cổ\s+nhân\s+dạy|Cổ\s+huấn|Trần\s+Đoàn\s+vị|Đẩu\s+Số|Toàn\s+Thư)\s*[::]\s*{QUOTE_CHARS}([^{QUOTE_CHARS[1:-1]}]{{6,400}}){QUOTE_CHARS}',
        re.UNICODE | re.DOTALL,
    )
    for m in pat1.finditer(text):
        body = m.group(1).strip()
        if body:
            quotes.append({"text": body, "type": "phu_quote"})
    # Pattern 2: bare quoted block (multi-line, 12-400 chars) — Hán-Việt heavy
    pat2 = re.compile(rf'{QUOTE_CHARS}([^{QUOTE_CHARS[1:-1]}]{{12,400}}){QUOTE_CHARS}', re.UNICODE | re.DOTALL)
    # Filter words that disqualify a quote as "modern Vietnamese commentary"
    MODERN_VI_DISQUALIFIERS = {
        'anh', 'em', 'bạn', 'tôi', 'lời khuyên', 'ví dụ', 'tức là', 'nghĩa là',
        'theo em', 'theo tôi', 'hãy', 'nên', 'cần phải', 'bạn ơi', 'anh ơi',
    }
    for m in pat2.finditer(text):
        body = m.group(1).strip()
        if any(q["text"] == body for q in quotes):
            continue
        # Skip too short (real classical phú = 12+ chars)
        if len(body) < 12:
            continue
        # Avoid markdown wrappers / starts with punctuation
        if body[0] in '*-#(.,;:[' or body.startswith('**'):
            continue
        if '**' in body:  # markdown bold inside — not classical
            continue
        # Avoid ending mid-sentence
        if body.endswith((',', ':', ';', '–', '(', 'và', 'của', 'là', 'nhưng', 'mà', 'với', 'cùng', 'thì', 'rồi', 'được', 'gặp')):
            continue
        # Skip if contains digits (numerical metadata, not phú thi)
        if re.search(r'\d', body):
            continue
        # Skip if starts with lowercase Vietnamese (fragment from middle of sentence)
        first_char = body[0]
        if first_char.isalpha() and first_char.islower():
            continue
        # Skip if pure English (no Vietnamese diacritic at all)
        viet_diacritic = sum(1 for c in body if c.isalpha() and ord(c) > 127)
        if viet_diacritic < 4:  # at least 4 Vietnamese-diacritic chars
            continue
        # Detect modern Vietnamese commentary (disqualifiers)
        body_lower = body.lower()
        if any(d in body_lower for d in MODERN_VI_DISQUALIFIERS):
            continue
        # Heuristic classical: should have at least 4 Vietnamese words
        words = re.split(r'[\s,.;\n—–\-]+', body)
        words = [w for w in words if w]
        if len(words) < 4:
            continue
        avg_word_len = sum(len(w) for w in words) / len(words)
        if avg_word_len > 12:  # super-long words = probably URLs/code
            continue
        # Classical phú vần điệu: many short words (4-7 chars avg)
        if avg_word_len > 6.5:  # commentary tends to longer Vietnamese words
            continue
        quotes.append({"text": body, "type": "embedded_quote"})
    return quotes


def _extract_cach_cuc_names(text: str) -> list[str]:
    """Extract cách cục names. Pattern: ChữHoa(...)+ "cách" or "cục"."""
    names = set()
    cap = "ÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
    char_class = rf"[\w{cap}]"
    # Pattern in quotes
    pat = re.compile(rf"[“\"”„]([A-Z{cap}]{char_class}{{3,55}})[”\"“„]\s+(?:chi\s+)?cách\b", re.UNICODE)
    for m in pat.finditer(text):
        n = m.group(1).strip()
        if 4 <= len(n) <= 60:
            names.add(n + " cách")
    # Pattern bare: "Mệnh cách X cách" — REQUIRE 2+ capitalized words (avoid "Những cách", "đời cách")
    pat2 = re.compile(rf"(?:^|[\.,;:\s\n])([A-Z{cap}]{char_class}{{3,40}})\s+(?:chi\s+)?cách\b", re.UNICODE)
    # Common Vietnamese modifiers that should NOT lead a cách cục name
    NON_CACH_PREFIXES = {
        'Những', 'Các', 'Mọi', 'Một', 'Vài', 'Nhiều', 'Cả', 'Anh', 'Em', 'Bạn',
        'Tôi', 'Chúng', 'Họ', 'Như', 'Nếu', 'Khi', 'Thì', 'Đến', 'Ngày', 'Cách',
        'Đây', 'Đó', 'Kia', 'Theo', 'Sau', 'Trước', 'Trong', 'Ngoài',
    }
    for m in pat2.finditer(text):
        n = m.group(1).strip()
        words = n.split()
        # Skip modern Vietnamese pronouns + counters
        if words[0] in NON_CACH_PREFIXES:
            continue
        cap_words = [w for w in words if w and w[0].isupper()]
        # Require 2+ capitalized words (proper noun pattern: "Tử Vi cách", "Phúc Lộc cách")
        if len(cap_words) >= 2 and 4 <= len(n) <= 50:
            names.add(n + " cách")
    return sorted(names)


def _add_concept(
    db: sqlite3.Connection,
    *,
    canonical_vi: str,
    short_note: str,
    category: str,
    source_section: str,
):
    """Insert new concept into concept_index."""
    now = int(time.time())
    db.execute(
        """INSERT INTO concept_index
           (canonical_vi, canonical_zh, aliases, mentioned_in_passages, short_note,
            first_seen_corpus, first_seen_page, created_at, category, corpora, school)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            canonical_vi[:200],
            "",
            json.dumps([], ensure_ascii=False),
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


def extract_phe_menh_to_wiki(phe_menh_data: dict, *, db_path: Optional[Path] = None,
                              verbose: bool = False) -> dict:
    """Extract concepts từ phe_menh_sau result → wiki.

    Args:
        phe_menh_data: dict trả về từ TuViAnalyzer.phe_menh_sau()
        db_path: optional override wiki DB path
        verbose: print stats

    Returns:
        {"added_quotes": int, "added_cach_cuc": int, "skipped": int, "person": str}
    """
    if not phe_menh_data or phe_menh_data.get("status") != "ok":
        return {"added_quotes": 0, "added_cach_cuc": 0, "skipped": 0, "error": "no-data"}

    phe = phe_menh_data.get("phe_menh_sau", {})
    person = phe_menh_data.get("person_name", "?")

    # Collect per-section
    all_quotes = []
    all_cach = []
    for section_key, section_text in phe.items():
        if section_key.startswith("_") or not isinstance(section_text, str):
            continue
        for q in _extract_quotes(section_text):
            q["section"] = section_key
            all_quotes.append(q)
        for cc in _extract_cach_cuc_names(section_text):
            all_cach.append({"name": cc, "section": section_key})

    # Dedup
    seen_q = set()
    unique_quotes = []
    for q in all_quotes:
        key = q["text"].strip().lower()
        if key in seen_q:
            continue
        seen_q.add(key)
        unique_quotes.append(q)

    seen_c = set()
    unique_cach = []
    for cc in all_cach:
        key = cc["name"].strip().lower()
        if key in seen_c:
            continue
        seen_c.add(key)
        unique_cach.append(cc)

    # DB upsert
    db = sqlite3.connect(str(db_path or WIKI_DB))
    existing = _existing_canonical_vi(db)
    added_quotes = 0
    skipped_quotes = 0
    for q in unique_quotes:
        if q["text"].strip().lower() in existing:
            skipped_quotes += 1
            continue
        _add_concept(
            db,
            canonical_vi=q["text"],
            short_note=f"Phú thi Hán-Việt — phê mệnh sâu V4 Pro (section: {q['section']}, người: {person})",
            category="phú",
            source_section=q["section"],
        )
        existing.add(q["text"].strip().lower())
        added_quotes += 1

    added_cach = 0
    skipped_cach = 0
    for cc in unique_cach:
        if cc["name"].strip().lower() in existing:
            skipped_cach += 1
            continue
        _add_concept(
            db,
            canonical_vi=cc["name"],
            short_note=f"Cách cục Tử Vi — phê mệnh sâu V4 Pro (section: {cc['section']}, người: {person})",
            category="cách cục",
            source_section=cc["section"],
        )
        existing.add(cc["name"].strip().lower())
        added_cach += 1

    db.commit()
    db.close()

    result = {
        "person": person,
        "extracted_quotes": len(unique_quotes),
        "extracted_cach_cuc": len(unique_cach),
        "added_quotes": added_quotes,
        "added_cach_cuc": added_cach,
        "skipped_quotes": skipped_quotes,
        "skipped_cach_cuc": skipped_cach,
        "corpus_id": CORPUS_ID,
    }
    if verbose:
        print(f"📚 Wiki extraction for {person}:")
        print(f"   Quotes: {added_quotes} added, {skipped_quotes} skipped (already in wiki)")
        print(f"   Cách cục: {added_cach} added, {skipped_cach} skipped")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: wiki_extractor.py <cache_json_path>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    r = extract_phe_menh_to_wiki(data, verbose=True)
    print()
    print(json.dumps(r, ensure_ascii=False, indent=2))
