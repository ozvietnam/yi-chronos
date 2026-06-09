"""Section Runner — Atomize 1 section sequential theo manifest.yaml.

Nguyên tắc anh đặt 2026-06-09:
- Test từng section, rút kinh nghiệm
- KHÔNG parallel toàn cuốn
- KHÔNG nhảy hệ phái

Usage:
    python3 -m engine.atomization.section_runner --book trung-chau-tu-vi-dau-so-2 --section 4.1.1
    python3 -m engine.atomization.section_runner --book trung-chau-tu-vi-dau-so-2 --section 4.1.1 --dry-run
    python3 -m engine.atomization.section_runner --book trung-chau-tu-vi-dau-so-2 --list
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.atomization.atomizer import Atomizer  # noqa: E402

DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


# Mini YAML parser (no PyYAML dep)
RE_SECTION_ID = re.compile(r'^\s*-\s*id:\s*"([^"]+)"\s*$')
RE_FIELD = re.compile(r'^\s*(\w+):\s*(.*)$')
RE_LIST_VAL = re.compile(r'^\s*-\s+(.*)$')


def parse_manifest(manifest_path: Path) -> list[dict]:
    """Parse simple YAML manifest written by section_detector."""
    sections = []
    current: dict = {}
    in_sections = False

    for line in manifest_path.read_text(encoding="utf-8").split("\n"):
        if line.strip() == "sections:":
            in_sections = True
            continue
        if not in_sections:
            continue
        m_id = RE_SECTION_ID.match(line)
        if m_id:
            if current:
                sections.append(current)
            current = {"id": m_id.group(1)}
            continue
        if not current:
            continue
        m_field = RE_FIELD.match(line)
        if m_field:
            key = m_field.group(1)
            val = m_field.group(2).strip()
            if key in ("id",):
                continue
            # Parse value
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("[") and val.endswith("]"):
                # list of quoted strings
                items = re.findall(r'"([^"]*)"', val)
                val = items
            elif val.isdigit():
                val = int(val)
            current[key] = val
    if current:
        sections.append(current)
    return sections


def find_section(sections: list[dict], section_id: str) -> dict | None:
    for s in sections:
        if s["id"] == section_id:
            return s
    return None


def list_sections(sections: list[dict]) -> None:
    print(f"{'Section':>10}  {'Pages':>14}  {'N':>4}  Title")
    print("-" * 80)
    for s in sections:
        pages = f"p{s['page_start']:04d}-p{s['page_end']:04d}"
        title = s.get("title", "")[:50]
        n = s.get("n_pages", "?")
        print(f"{s['id']:>10}  {pages:>14}  {n:>4}  {title}")


def get_or_create_chunks(book: str, section_id: str, page_start: int, page_end: int) -> list[tuple[int, int, str]]:
    """Return [(chunk_id, page, text)] for section. Tag chunks_v2.section_id."""
    conn = sqlite3.connect(DB)
    pages_dir = PROJECT_ROOT / "data" / "restored_books" / book / "pages"

    rows = []
    for page in range(page_start, page_end + 1):
        path = pages_dir / f"p{page:04d}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if len(text) < 50:
            continue

        # Check if chunk already exists for this book + page
        existing = conn.execute(
            "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=?",
            (book, page),
        ).fetchone()
        if existing:
            chunk_id = existing[0]
            # Update section_id if not set or different
            conn.execute("UPDATE chunks_v2 SET section_id=? WHERE chunk_id=?", (section_id, chunk_id))
        else:
            cur = conn.execute(
                """INSERT INTO chunks_v2 (book_corpus_id, page_start, page_end, text, section_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (book, page, page, text, section_id),
            )
            chunk_id = int(cur.lastrowid)
        rows.append((chunk_id, page, text))
    conn.commit()
    conn.close()
    return rows


def is_chunk_atomized(chunk_id: int) -> bool:
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "SELECT COUNT(*) FROM chunk_classifications WHERE chunk_id=?", (chunk_id,)
    ).fetchone()[0]
    conn.close()
    return n > 0


def run_section(book: str, section_id: str, dry_run: bool = False) -> None:
    manifest_path = PROJECT_ROOT / "data" / "restored_books" / book / "manifest.yaml"
    if not manifest_path.exists():
        sys.exit(f"❌ Manifest not found: {manifest_path}\nRun: python3 -m engine.atomization.section_detector --book {book}")

    sections = parse_manifest(manifest_path)
    section = find_section(sections, section_id)
    if not section:
        sys.exit(f"❌ Section {section_id} not found in manifest")

    print(f"📖 Book: {book}")
    print(f"🔖 Section {section['id']}: {section.get('title', '')}")
    print(f"📄 Pages: p{section['page_start']:04d} → p{section['page_end']:04d} "
          f"({section.get('n_pages', '?')} pages)")
    if section.get("stars"):
        print(f"⭐ Stars: {section['stars']}")
    if section.get("palaces"):
        print(f"🏛 Palaces: {section['palaces']}")
    print()

    # Get/create chunks
    chunks = get_or_create_chunks(
        book, section_id, int(section["page_start"]), int(section["page_end"])
    )
    print(f"📦 {len(chunks)} chunks in section (tagged section_id={section_id})")

    pending = [(cid, p, t) for cid, p, t in chunks if not is_chunk_atomized(cid)]
    skipped = len(chunks) - len(pending)
    print(f"   ⏭ Skipped (already atomized): {skipped}")
    print(f"   📋 Pending: {len(pending)}")

    if dry_run:
        print("\n[DRY-RUN] Stop here. Use without --dry-run to atomize.")
        return

    if not pending:
        print("✅ Nothing to atomize")
        return

    atomizer = Atomizer()
    print(f"\n🔧 Atomizer: {atomizer.provider.name}/{atomizer.model}\n")

    t_start = time.time()
    total_atoms = 0
    total_tokens = 0
    success = 0
    fail = 0

    for idx, (chunk_id, page, text) in enumerate(pending, 1):
        t1 = time.time()
        print(f"  [{idx}/{len(pending)}] chunk_id={chunk_id} p{page:04d} ({len(text)} chars)...", end="", flush=True)
        result = atomizer.atomize_chunk(chunk_id, text, book, skip_if_exists=True)
        d = time.time() - t1
        if result.error:
            print(f" ❌ {d:.1f}s · {result.error[:80]}")
            fail += 1
        else:
            n = len(result.atomic_questions)
            print(f" ✅ {d:.1f}s · {n} atoms · {result.total_tokens} tok")
            success += 1
            total_atoms += n
            total_tokens += result.total_tokens

            # Tag atomic_questions with section_id
            conn = sqlite3.connect(DB)
            conn.execute(
                "UPDATE atomic_questions SET section_id=? WHERE chunk_id=?",
                (section_id, chunk_id),
            )
            conn.commit()
            conn.close()

    elapsed = time.time() - t_start
    print(f"\n{'═'*60}")
    print(f"✅ Section {section_id} DONE")
    print(f"   Success: {success}/{len(pending)} · Fail: {fail}")
    print(f"   Total atomic Q: {total_atoms}")
    print(f"   Total tokens: {total_tokens}")
    print(f"   Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"   Avg/chunk: {elapsed/max(success,1):.1f}s · {total_atoms/max(success,1):.1f} atoms")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--book", required=True)
    p.add_argument("--section", help="vd 4.1.1")
    p.add_argument("--list", action="store_true", help="list all sections")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    manifest = PROJECT_ROOT / "data" / "restored_books" / args.book / "manifest.yaml"
    if not manifest.exists():
        sys.exit(f"❌ Manifest not found. Run section_detector first.")

    sections = parse_manifest(manifest)
    if args.list:
        list_sections(sections)
        return
    if not args.section:
        sys.exit("❌ Provide --section <id> or --list")
    run_section(args.book, args.section, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
