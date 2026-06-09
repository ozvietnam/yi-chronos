#!/usr/bin/env python3
"""Export atoms ra MD review cho anh tick ✅/⚠/❌.

Usage:
  python3 scripts/export_review_md.py 5.1.6 5.1.7 ... → docs/design/atoms-review-cung-menh-v2.md
"""
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
OUT = PROJECT_ROOT / "docs" / "design" / "atoms-review-cung-menh-v2-2026-06-09.md"


def fetch_atoms(conn: sqlite3.Connection, section_id: str):
    cur = conn.execute(
        """
        SELECT a.atom_id, a.question_text, a.source_quote, a.from_template,
               c.han_viet_explain, c.viet_thuan, c.nguyen_ly, c.vi_du_doi_song, c.iron_rule_warning,
               (SELECT page_start FROM chunks_v2 WHERE chunk_id = a.chunk_id) as page
        FROM atomic_questions a
        LEFT JOIN atom_commentaries c ON c.atom_id = a.atom_id
        WHERE a.section_id = ?
          AND a.extracted_by = 'sub-agent-bam-sach'
        ORDER BY a.atom_id
        """,
        (section_id,),
    )
    return cur.fetchall()


def render_atom(row) -> str:
    atom_id, q, sq, qid, hanviet, vt, ngly, vidu, warn, page = row
    out = [f"### [ ] {qid or atom_id} — p{page}"]
    out.append(f"**❓ Câu hỏi**: {q}")
    out.append("")
    out.append(f"**📜 Source quote (NGUYÊN VĂN, p{page})**:")
    out.append(f"> {sq}")
    out.append("")
    if hanviet:
        out.append(f"**📖 Hán-Việt giải**: {hanviet}")
    out.append(f"**🇻🇳 Việt thuần (paraphrase)**: {vt}")
    if ngly:
        out.append(f"**💡 Nguyên lý**: {ngly}")
    if vidu:
        out.append(f"**🎬 Ví dụ đời sống**: {vidu}")
    if warn:
        out.append(f"**⚠ Iron Rule warning**: {warn}")
    out.append("")
    out.append("**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ")
    out.append("")
    out.append("---")
    return "\n".join(out)


def main():
    sections = sys.argv[1:]
    if not sections:
        print("Usage: export_review_md.py <section_id> [section_id ...]")
        sys.exit(1)

    conn = sqlite3.connect(DB)
    lines = [
        "# ATOMS REVIEW — CUNG MỆNH v2 (sub-agent bám sách)",
        "",
        "**Ngày**: 2026-06-09",
        "**Sách**: Trung Châu Tử Vi Đẩu Số Q2 (Vương Đình Chỉ)",
        "**Quy trình**: 7 sub-agents parallel đọc text → JSON → ingest DB",
        "**Quality**: `viet_thuan` 100% PARAPHRASE source_quote, `nguyen_ly`/`vi_du` NULL nếu sách không nói",
        "",
        "## Hướng dẫn anh review",
        "",
        "Mỗi atom có ô tick `[ ]`. Anh đánh:",
        "- **✅ đúng paradigm** — atom đúng, để confidence 0.85 → upgrade 0.95",
        "- **⚠ cần sửa** — note lý do, em sửa",
        "- **❌ ẨU bỏ** — em xóa khỏi DB",
        "",
        "Không cần review hết 1 lần — anh tick được bao nhiêu thì em xử bấy nhiêu.",
        "",
        "---",
        "",
    ]

    grand_total = 0
    for sec in sorted(sections):
        atoms = fetch_atoms(conn, sec)
        if not atoms:
            continue
        # Section title from manifest
        import yaml
        m = yaml.safe_load(open(PROJECT_ROOT / "data/restored_books/trung-chau-tu-vi-dau-so-2/manifest.yaml"))
        title = next((s.get("title", sec) for s in m.get("sections", []) if str(s.get("id")) == sec), sec)
        lines.append(f"## Section {sec} — {title} ({len(atoms)} atoms)")
        lines.append("")
        for atom in atoms:
            lines.append(render_atom(atom))
        grand_total += len(atoms)

    lines.insert(0, f"_Tổng: **{grand_total} atoms** / {len(sections)} sections_")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {OUT} — {grand_total} atoms / {len(sections)} sections")
    print(f"   Size: {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
