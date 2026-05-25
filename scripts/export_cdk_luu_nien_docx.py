"""Export Lưu Niên 10 năm CDK → Word docx."""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
BRANCH_CON_GIAP = {
    "Tý": "Chuột", "Sửu": "Trâu", "Dần": "Hổ", "Mão": "Mèo/Thỏ",
    "Thìn": "Rồng", "Tỵ": "Rắn", "Ngọ": "Ngựa", "Mùi": "Dê",
    "Thân": "Khỉ", "Dậu": "Gà", "Tuất": "Chó", "Hợi": "Lợn",
}


def main():
    person_slug = sys.argv[1] if len(sys.argv) >= 2 else "_founder_cdk_dau"
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else PROJECT_ROOT / f"data/published/CDK_LuuNien_10nam_{person_slug}.docx"

    cache_dir = PROJECT_ROOT / "data/yi_publishing/analysis_cache"
    cache_file = None
    for uid_dir in cache_dir.glob("u*"):
        for prefix in [f"cdk_cung_{person_slug}_LUU_NIEN_10_NAM", f"cdk_cung__{person_slug}_LUU_NIEN_10_NAM"]:
            p = uid_dir / prefix / "luan_cung.json"
            if p.exists():
                cache_file = p
                break
        if cache_file:
            break
    if not cache_file:
        print(f"❌ Cache not found")
        sys.exit(1)
    print(f"📂 Loading: {cache_file}")
    with cache_file.open() as f:
        data = json.load(f)

    ln = data.get("luu_nien", {})
    years_meta = data.get("years", [])
    person_name = data.get("person_name", "?")
    menh_branch = data.get("menh_branch", "?")
    provider = data.get("provider", "?")
    gen_at = data.get("generated_at", 0)
    gen_dt = datetime.fromtimestamp(gen_at).strftime("%d/%m/%Y %H:%M") if gen_at else "?"
    tokens = data.get("tokens", {})
    this_year = datetime.now().year

    lines = [
        f"# LƯU NIÊN 10 NĂM · CHIẾU ĐỞM KINH",
        f"",
        f"## Chủ nhân: {person_name}",
        f"",
        f"_Luận vận khí **từng năm** trong 10 năm tới — kết hợp can-chi năm + lưu Thái Tuế cung + đại hạn._",
        f"_Theo paradigm Iron Rule #6 — đọc đồng dạng, không dự đoán cứng._",
        f"",
        f"---",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Mệnh CDK | **{menh_branch}** ({BRANCH_CON_GIAP.get(menh_branch, '?')}) |",
        f"| Năm bắt đầu | {years_meta[0]['year'] if years_meta else '?'} |",
        f"| Năm kết thúc | {years_meta[-1]['year'] if years_meta else '?'} |",
        f"| Provider | {provider} |",
        f"| Sinh thành | {gen_dt} |",
        f"| Tokens | {tokens.get('prompt', '?')} prompt + {tokens.get('completion', '?')} completion |",
        f"",
        f"---",
        f"",
        f"## 📅 Tổng quan 10 năm",
        f"",
        f"| Năm | Can chi | Tuổi | Thái Tuế cung |",
        f"|---|---|---|---|",
    ]
    for y in years_meta:
        is_current = y["year"] == this_year
        marker = " ⭐ HIỆN TẠI" if is_current else ""
        lines.append(f"| **{y['year']}**{marker} | {y['can_chi']} | {y['age']} | {y['luu_thai_tue_branch']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 10 năm chi tiết
    for y in years_meta:
        is_current = y["year"] == this_year
        marker = " ⭐ (NĂM HIỆN TẠI)" if is_current else ""
        v = ln.get(f"nam_{y['year']}", {})

        lines.append(f"# Năm {y['year']}{marker} — {y['can_chi']}")
        lines.append("")
        lines.append(f"**Tuổi {y['age']} · Lưu Thái Tuế cung {y['luu_thai_tue_branch']} ({BRANCH_CON_GIAP.get(y['luu_thai_tue_branch'], '?')})**")
        lines.append("")
        if isinstance(v, dict):
            if v.get("tong_quan"):
                lines.append(f"## 1. Tổng quan năm")
                lines.append("")
                lines.append(v["tong_quan"])
                lines.append("")
            if v.get("co_hoi_thach_thuc"):
                lines.append(f"## 2. Cơ hội & Thử thách")
                lines.append("")
                lines.append(v["co_hoi_thach_thuc"])
                lines.append("")
            if v.get("loi_khuyen"):
                lines.append(f"## 3. Lời khuyên")
                lines.append("")
                lines.append(v["loi_khuyen"])
                lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend([
        f"",
        f"# 🙏 Lời kết",
        f"",
        f"10 năm = **nhịp đập ngắn hạn** của cuộc đời. Mỗi năm có vận khí riêng, ",
        f"không có năm nào toàn cát hay toàn hung.",
        f"",
        f"Quan trọng: **CƠ + ĐẠI HẠN + LƯU NIÊN cộng hưởng**. Cùng năm Bính Ngọ, ",
        f"người đại hạn Lộc đắc địa = năm phát; người đại hạn Kỵ thất vị = năm khó.",
        f"",
        f"Iron Rule #6: _\"Thập bát tinh chuyển, tại nhân biến thông\"_ — sao chỉ vận hành, ",
        f"con người là người **biến thông**. Mỗi năm, anh có quyền chọn phản ứng.",
        f"",
        f"---",
        f"",
        f"_© YI-CHRONOS · Lưu Niên 10 năm CDK · {datetime.now().strftime('%d/%m/%Y %H:%M')}_",
    ])

    md = "\n".join(lines)
    md_path = output_path.with_suffix(".md")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    print(f"📝 Markdown: {md_path} ({len(md):,} chars)")

    result = subprocess.run(
        ["pandoc", str(md_path), "-o", str(output_path),
         "--from", "markdown+pipe_tables+blank_before_blockquote",
         "--to", "docx", "--standalone"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ {result.stderr}"); sys.exit(1)
    print(f"📄 DOCX: {output_path} ({output_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
