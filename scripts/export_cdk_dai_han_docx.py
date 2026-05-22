"""Export 8 vòng Đại Hạn CDK → Word docx."""
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
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else PROJECT_ROOT / f"data/published/CDK_DaiHan_8Vong_{person_slug}.docx"

    cache_dir = PROJECT_ROOT / "data/yi_publishing/analysis_cache"
    cache_file = None
    for uid_dir in cache_dir.glob("u*"):
        for prefix in [f"cdk_cung_{person_slug}_DAI_HAN_8_VONG", f"cdk_cung__{person_slug}_DAI_HAN_8_VONG"]:
            p = uid_dir / prefix / "luan_cung.json"
            if p.exists():
                cache_file = p
                break
        if cache_file:
            break
    if not cache_file:
        print(f"❌ Cache not found for {person_slug}")
        sys.exit(1)
    print(f"📂 Loading: {cache_file}")
    with cache_file.open() as f:
        data = json.load(f)

    dh = data.get("dai_han", {})
    cycles = data.get("dai_han_cycles", [])
    person_name = data.get("person_name", "Vô danh")
    menh_branch = data.get("menh_branch", "?")
    provider = data.get("provider", "?")
    gen_at = data.get("generated_at", 0)
    gen_dt = datetime.fromtimestamp(gen_at).strftime("%d/%m/%Y %H:%M") if gen_at else "?"
    tokens = data.get("tokens", {})

    # Compute current cycle
    try:
        born_year = 1988
        current_age = datetime.now().year - born_year
        current_cycle_idx = None
        for c in cycles:
            if c.get("start_age", 0) <= current_age <= c.get("end_age", 0):
                current_cycle_idx = c.get("cycle_index")
                break
    except Exception:
        current_age = "?"
        current_cycle_idx = None

    lines = [
        f"# ĐẠI HẠN 8 VÒNG · CHIẾU ĐỞM KINH",
        f"",
        f"## Chủ nhân: {person_name}",
        f"",
        f"_Luận chi tiết **80 năm cuộc đời** qua **8 vòng Đại Hạn** (mỗi vòng 10 năm)._",
        f"_Theo paradigm Iron Rule #6 — đọc đồng dạng, không dự đoán cứng._",
        f"",
        f"---",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Mệnh CDK | **{menh_branch}** ({BRANCH_CON_GIAP.get(menh_branch, '?')}) |",
        f"| Tuổi hiện tại | ~{current_age} |",
        f"| Vòng đại hạn hiện tại | **Vòng {current_cycle_idx}** (cung {next((c['branch'] for c in cycles if c.get('cycle_index') == current_cycle_idx), '?')}) |",
        f"| Provider | {provider} |",
        f"| Sinh thành | {gen_dt} |",
        f"| Tokens | {tokens.get('prompt', '?')} prompt + {tokens.get('completion', '?')} completion |",
        f"",
        f"---",
        f"",
        f"## 📜 Lời mở đầu",
        f"",
        f"> _\"Đẩu số chí huyền chí vi, lý chỉ dị minh. Cẩu hoặc bất sát kỳ cơ, **cánh vong kỳ biến**, tắc số chi tạo hóa viễn hĩ.\"_ — Trần Đoàn",
        f"",
        f"_Nếu chỉ xét lớp **CƠ** (12 cung tại điểm sinh) mà quên lớp **BIẾN** (Đại Hạn vận động theo thời gian) thì tạo hóa của số sẽ vuột mất._",
        f"",
        f"Bản này luận chi tiết **8 vòng đại hạn 10 năm/cung**. Khi đại hạn đi qua cung nào, các sao tại cung đó **kích hoạt** — chi phối vận khí 10 năm ấy.",
        f"",
        f"---",
        f"",
        f"## 🗺️ Tổng quan 8 vòng",
        f"",
        f"| Vòng | Tuổi | Cung đại hạn | Con giáp |",
        f"|---|---|---|---|",
    ]
    for c in cycles:
        idx = c.get("cycle_index", "?")
        br = c.get("branch", "?")
        s = c.get("start_age", "?")
        e = c.get("end_age", "?")
        marker = " ⭐ HIỆN TẠI" if idx == current_cycle_idx else (" (Mệnh gốc)" if br == menh_branch and idx != current_cycle_idx else "")
        lines.append(f"| Vòng {idx}{marker} | {s}-{e} | **{br}** | {BRANCH_CON_GIAP.get(br, '?')} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 8 vòng chi tiết
    for c in cycles:
        idx = c.get("cycle_index", "?")
        br = c.get("branch", "?")
        s = c.get("start_age", "?")
        e = c.get("end_age", "?")
        try:
            year_start = born_year + s
            year_end = born_year + e
            year_range_str = f" ({year_start}-{year_end})"
        except Exception:
            year_range_str = ""
        vong_key = f"vong_{idx}"
        v = dh.get(vong_key, {})
        is_current = idx == current_cycle_idx
        is_menh_cycle = br == menh_branch
        marker = ""
        if is_current:
            marker = " ⭐ (HIỆN TẠI)"
        elif is_menh_cycle:
            marker = " (đi qua cung Mệnh)"

        lines.append(f"# Vòng {idx}{marker} — Tuổi {s}-{e}{year_range_str}")
        lines.append("")
        lines.append(f"**Đại hạn đóng tại cung {br} ({BRANCH_CON_GIAP.get(br, '?')})**")
        lines.append("")
        if isinstance(v, dict):
            if v.get("tong_quan"):
                lines.append(f"## 1. Tổng quan giai đoạn")
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
        else:
            lines.append("⚠️ _Vòng này chưa được luận giải._")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend([
        f"",
        f"# 🙏 Lời kết",
        f"",
        f"8 vòng đại hạn = **nhịp đập cuộc đời**. Mỗi vòng có vận khí riêng, ",
        f"không có vòng nào toàn cát hay toàn hung. ",
        f"",
        f"Quan trọng nhất: **CƠ + BIẾN cộng hưởng**. Cùng sao Lộc, nếu đại hạn đi qua cung đắc địa = phú quý; ",
        f"nếu đi qua cung kỵ = gặp họa. Vì thế, biết mình đang ở vòng nào + cung nào → biết cách ứng xử.",
        f"",
        f"Tinh thần Iron Rule #6: _\"Thập bát tinh chuyển, tại nhân biến thông\"_ — sao chỉ vận hành, ",
        f"con người là người **biến thông**. Anh có quyền chọn phản ứng trong mỗi giai đoạn.",
        f"",
        f"---",
        f"",
        f"_© YI-CHRONOS · Đại Hạn 8 vòng CDK · {datetime.now().strftime('%d/%m/%Y %H:%M')}_",
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
