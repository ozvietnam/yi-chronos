#!/usr/bin/env python3
"""Normalize atom schemas — handle variant fields from different sub-agents.

Variants seen:
- question_id vs atom_id vs id
- source_page vs page
- question vs concept vs Q
- source_quote consistent
- tags (some missing)
- confidence (default 0.85)
- extracted_by (default sub-agent-bam-sach)
"""
import json
import sys
from pathlib import Path


def normalize(atom: dict) -> dict:
    """Return normalized atom or None if invalid."""
    out = dict(atom)  # shallow copy

    # question_id <- atom_id / id
    if not out.get("question_id"):
        out["question_id"] = atom.get("atom_id") or atom.get("id") or ""

    # source_page <- page
    if out.get("source_page") is None:
        out["source_page"] = atom.get("page")

    # Convert "44-45" range → 44
    sp = out.get("source_page")
    if isinstance(sp, str) and "-" in sp:
        try:
            out["source_page"] = int(sp.split("-")[0])
        except ValueError:
            pass
    elif isinstance(sp, list) and sp:
        out["source_page"] = sp[0]

    # question <- concept / Q
    if not out.get("question"):
        out["question"] = atom.get("concept") or atom.get("Q") or ""

    # Defaults
    if not out.get("tags"):
        out["tags"] = []
    if not out.get("confidence"):
        out["confidence"] = 0.85
    if not out.get("extracted_by"):
        out["extracted_by"] = "sub-agent-bam-sach"

    # Skip if no source_page or source_quote
    if not isinstance(out.get("source_page"), int) or not (out.get("source_quote") or "").strip():
        return None

    return out


def normalize_file(path: Path) -> int:
    """Return count of normalized atoms."""
    data = json.loads(path.read_text(encoding="utf-8"))
    atoms = data.get("atoms") or []
    normalized = []
    skipped = 0
    for a in atoms:
        n = normalize(a)
        if n:
            normalized.append(n)
        else:
            skipped += 1
    data["atoms"] = normalized
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(normalized), skipped


def main():
    if len(sys.argv) < 2:
        print("Usage: normalize_atom_schemas.py <dir_or_file>")
        sys.exit(1)
    target = Path(sys.argv[1])
    files = sorted(target.glob("*.json")) if target.is_dir() else [target]
    for f in files:
        try:
            n, sk = normalize_file(f)
            print(f"  ✅ {f.name}: normalized={n} skipped={sk}")
        except Exception as e:
            print(f"  ❌ {f.name}: {e}")


if __name__ == "__main__":
    main()
