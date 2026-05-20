"""Export phê mệnh sâu JSON → .docx (Word) cho Anh đọc offline.

Usage:
  .venv/bin/python3 scripts/export_phe_menh_sau_docx.py <cache_json_path> [output.docx]
"""
from __future__ import annotations

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SECTION_LABELS = {
    "dinh_thoi_khac":     ("1. ĐỊNH THỜI KHẮC", "Phân tích thời điểm sinh — giờ, can chi, vị trí khí số"),
    "khoi_bat_tu":        ("2. KHỞI BÁT TỰ — Tứ Trụ", "Tứ trụ năm-tháng-ngày-giờ + ngũ hành"),
    "lap_cach_dung_than": ("3. LẬP CÁCH · DỤNG THẦN", "Đối chiếu Phú Thái Vi 545 cách cục, xác định dụng-hỉ-kỵ thần"),
    "bai_tinh_than":      ("4. BÀI TINH THẦN", "14 chính tinh + Tứ Hóa + phụ-sát tinh theo 12 cung"),
    "lap_toa_menh":       ("5. LẬP TỌA MỆNH", "Tam phương tứ chính — cấu trúc Tâm-Tính-Mệnh"),
    "dai_van_phan_tich":  ("6. ĐẠI VẬN PHÂN TÍCH", "8 vòng đời 10 năm — cung-sao-tuổi cụ thể"),
    "dai_han_luu_nien":   ("7. ĐẠI HẠN + LƯU NIÊN", "Đại hạn hiện tại + Lưu niên 5 năm gần"),
    "tu_hoa_dien_giai":   ("8. TỨ HÓA DIỄN GIẢI SÂU", "Lộc-Quyền-Khoa-Kỵ năm sinh × đại vận × lưu niên"),
    "hi_ky_canh_bao":     ("9. HỈ KỴ + CẢNH BÁO ĐẢO HẠN", "Sao hỉ — Sao kỵ — Safety patterns"),
    "ket_tam_an":         ("10. KẾT TÂM AN", "Bài cát hung + paradigm 'bất khả chấp nhất'"),
}


def build_markdown(cache: dict) -> str:
    """Build clean markdown từ cache JSON."""
    phe = cache.get("phe_menh_sau", {})
    person = cache.get("person_name", "Vô danh")
    provider = cache.get("provider", "?")
    model = cache.get("model", "?")
    gen_at = cache.get("generated_at", 0)
    gen_dt = datetime.fromtimestamp(gen_at).strftime("%d/%m/%Y %H:%M") if gen_at else "—"
    avg_len = cache.get("avg_length_chars", 0)
    total_chars = sum(cache.get("section_lengths", {}).values())
    tokens = cache.get("tokens", {})

    lines = [
        f"# PHÊ MỆNH SÂU — TỬ VI ĐẨU SỐ",
        f"",
        f"## Chủ nhân: {person}",
        f"",
        f"_Theo 10 BƯỚC METHODOLOGY của Trần Đoàn (Hi Di tiên sinh) — Tử Vi Đẩu Số Toàn Thư Quyển 4_",
        f"",
        f"---",
        f"",
        f"**Thông tin biên soạn:**",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Người luận giải | YI-CHRONOS Sage (AI) |",
        f"| LLM Provider | {provider} ({model}) |",
        f"| Tổng số chữ | {total_chars:,} chars (~{total_chars//4:,} từ Tiếng Việt) |",
        f"| Trung bình mỗi mục | {avg_len:,} chars |",
        f"| Tokens dùng | {tokens.get('total', 0):,} |",
        f"| Sinh thành lúc | {gen_dt} |",
        f"",
        f"---",
        f"",
        f"## ⚠️ Lời mở đầu — Paradigm",
        f"",
        f"> _\"Đẩu số chí huyền chí vi, lý chỉ dị minh. Cẩu hoặc bất sát kỳ cơ, cánh vong kỳ biến, tắc số chi tạo hóa viễn hĩ.\"_",
        f"> — **Trần Đoàn**, Phú Thái Vi (Tử Vi Đẩu Số Toàn Thư)",
        f"",
        f"_Đẩu số tuy huyền vi sâu xa, nhưng nguyên lý vẫn có thể làm sáng tỏ. Nếu chẳng xét cơ huyền, lại quên biến hóa, thì cái tạo hóa của số sẽ vuột mất._",
        f"",
        f"**Bản phê mệnh này KHÔNG phải dự đoán cứng.** Tử Vi là môn **đọc đồng dạng** — cấu trúc lá số phản chiếu cấu trúc tâm-thiên-thân của chủ nhân tại điểm sinh. Người đọc cần giữ tâm tỉnh thức: **\"Thập bát tinh chuyển, tại nhân biến thông\"** (mười tám sao vận động, nhưng then chốt ở lòng người).",
        f"",
        f"---",
        f"",
        f"# MƯỜI BƯỚC LUẬN GIẢI",
        f"",
    ]

    # Render each section
    for key, (label, desc) in SECTION_LABELS.items():
        content = phe.get(key, "").strip()
        char_count = len(content)
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f"_{desc}_")
        lines.append("")
        lines.append(f"<small>**{char_count:,} chars**</small>")
        lines.append("")
        if not content:
            lines.append("⚠️ _Mục này chưa được biên soạn._")
            lines.append("")
            continue
        # Try to detect Hán-Việt verse lines vs Vietnamese prose
        # Heuristic: lines that are short (< 80 chars) and contain no period mid-line = verse
        for para in content.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            # Check if verse-like (multiple short lines with capitalized starts, no commas separating sentences)
            sublines = [l.strip() for l in para.split("\n") if l.strip()]
            verse_like = (
                len(sublines) >= 2
                and all(len(l) < 80 for l in sublines)
                and all(l.endswith((",", ".", "?", "!", "—", "…", "")) for l in sublines)
            )
            if verse_like and len(sublines) >= 3:
                # Render as blockquote (verse)
                for l in sublines:
                    lines.append(f"> _{l}_")
                lines.append(f">")
            else:
                lines.append(para)
            lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.extend([
        f"",
        f"# 📜 Lời kết của người biên soạn",
        f"",
        f"Bản phê mệnh này được biên soạn theo paradigm Iron Rule #6 (CLAUDE.md YI-CHRONOS):",
        f"",
        f"1. **Đẩu số là môn ĐỌC ĐỒNG DẠNG** — không phải fortune-telling",
        f"2. **CƠ + BIẾN** — kết hợp lớp gốc (14 chính tinh + 12 cung) với lớp biến (Đại Vận + Lưu Niên)",
        f"3. **\"Mỗ\" pattern** — khi nói về tương lai, dùng \"mỗ niên mỗ tinh nghi thận\" (không predict cứng)",
        f"4. **Paradigm bất khả chấp nhất** (Q4 p0299): không có lá số nào tuyệt đối định mệnh",
        f"",
        f"Người đọc nên kết hợp bản này với **TÂM TỈNH THỨC** — lá số phản chiếu cấu trúc, nhưng then chốt là biến thông trong tâm chủ nhân.",
        f"",
        f"---",
        f"",
        f"_© YI-CHRONOS — Nhà xuất bản Đông phương học AI-driven_",
        f"_Sinh thành: {gen_dt} · Provider: {provider} ({model})_",
        f"",
    ])
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: export_phe_menh_sau_docx.py <cache.json> [output.docx]")
        sys.exit(1)
    cache_path = Path(sys.argv[1])
    if not cache_path.exists():
        print(f"❌ Cache not found: {cache_path}")
        sys.exit(1)

    with cache_path.open() as f:
        cache = json.load(f)

    md_text = build_markdown(cache)
    person_slug = (cache.get("person_key") or "anonymous").replace("/", "_")

    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path(f"/Users/ozvietnamdesktop/Desktop/yi/data/published/phe_menh_sau_{person_slug}.docx")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write markdown intermediate (for debug)
    md_path = out_path.with_suffix(".md")
    md_path.write_text(md_text, encoding="utf-8")
    print(f"📝 Markdown: {md_path}")

    # Convert via pandoc → docx
    result = subprocess.run(
        [
            "pandoc",
            str(md_path),
            "-o", str(out_path),
            "--from", "markdown+pipe_tables+blank_before_blockquote",
            "--to", "docx",
            "--standalone",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ Pandoc fail:\n{result.stderr}")
        sys.exit(1)
    print(f"📄 DOCX: {out_path}")
    print(f"   Size: {out_path.stat().st_size:,} bytes")
    print(f"   Sections: {len([k for k in cache.get('phe_menh_sau', {}) if not k.startswith('_')])}/10")


if __name__ == "__main__":
    main()
