"""Export Tổng đoán cả cuộc đời CDK → Word docx."""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")

SECTIONS = [
    ("tong_quan_cuoc_doi", "I. TỔNG QUAN CUỘC ĐỜI", "Bản chất cuộc đời theo lá số CDK"),
    ("bon_giai_doan_doi", "II. BỐN GIAI ĐOẠN ĐỜI", "Theo 8 vòng Đại Hạn 10 năm/cung"),
    ("cach_chinh_cuoc_doi", "III. CÁCH CHÍNH CUỘC ĐỜI", "Cách cục lớn nhất chi phối toàn đời"),
    ("dinh_va_day", "IV. ĐỈNH CAO & ĐÁY THỬ THÁCH", "Khoảnh khắc bứt phá + thử thách"),
    ("loi_khuyen_xuyen_doi", "V. LỜI KHUYÊN XUYÊN ĐỜI", "5-7 lời khuyên cụ thể, actionable"),
    ("ket_tam_an", "VI. KẾT TÂM AN", "Paradigm Iron Rule #6"),
]


def main():
    person_slug = sys.argv[1] if len(sys.argv) >= 2 else "_founder_cdk_dau"
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else PROJECT_ROOT / f"data/published/CDK_TongDoanCuocDoi_{person_slug}.docx"

    # Find cache
    cache_dir = PROJECT_ROOT / "data/yi_publishing/analysis_cache"
    cache_file = None
    for uid_dir in cache_dir.glob("u*"):
        for prefix in [f"cdk_cung_{person_slug}_TONG_DOAN_CA_DOI", f"cdk_cung__{person_slug}_TONG_DOAN_CA_DOI"]:
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

    td = data.get("tong_doan", {})
    person_name = data.get("person_name", "Vô danh")
    menh_branch = data.get("menh_branch", "?")
    provider = data.get("provider", "?")
    gen_at = data.get("generated_at", 0)
    gen_dt = datetime.fromtimestamp(gen_at).strftime("%d/%m/%Y %H:%M") if gen_at else "?"
    tokens = data.get("tokens", {})

    lines = [
        f"# TỔNG ĐOÁN CUỘC ĐỜI · CHIẾU ĐỞM KINH",
        f"",
        f"## Chủ nhân: {person_name}",
        f"",
        f"_Bản synthesis: lớp **CƠ** (12 cung tiên thiên) + lớp **BIẾN** (8 vòng Đại Hạn 10 năm/cung)_",
        f"_Theo paradigm Iron Rule #6 — đọc đồng dạng, không dự đoán cứng._",
        f"",
        f"---",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Mệnh CDK | **{menh_branch}** |",
        f"| Người luận giải | YI-CHRONOS DeepSeek V4 Pro |",
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
        f"_Nếu chỉ xét lớp **CƠ** (cấu trúc 12 cung tại điểm sinh) mà quên lớp **BIẾN** (Đại Hạn vận động theo thời gian) thì \"tạo hóa của số sẽ vuột mất\"._",
        f"",
        f"Bản này là **synthesis cả 2 lớp** — vẽ ra nhịp đời xuyên 8 vòng Đại Hạn, với cách cục chính, đỉnh-đáy, lời khuyên xuyên đời.",
        f"",
        f"---",
        f"",
    ]
    for key, label, desc in SECTIONS:
        content = td.get(key, "").strip()
        lines.append(f"# {label}")
        lines.append(f"")
        lines.append(f"_{desc}_")
        lines.append(f"")
        if not content:
            lines.append("⚠️ _Phần này chưa được biên soạn._")
        else:
            lines.append(content)
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    lines.extend([
        f"",
        f"# 🙏 Lời kết người biên soạn",
        f"",
        f"Bản tổng đoán này được sinh bởi **DeepSeek V4 Pro** theo paradigm YI-CHRONOS Iron Rule #6:",
        f"",
        f"1. **Đẩu số = đọc đồng dạng**, không phải dự đoán cứng",
        f"2. **CƠ + BIẾN** kết hợp — lá số là tấm gương, Đại Hạn là nhịp thời gian",
        f"3. **\"Mỗ\" pattern** khi nói tương lai — \"có xu hướng\", \"thường\", không khẳng định tuyệt đối",
        f"4. **Paradigm \"bất khả chấp nhất\"** (Q4 p0299): _\"Thập bát tinh chuyển, tại nhân biến thông\"_ — sao vận hành, người biến đổi",
        f"",
        f"Người đọc nên kết hợp với **TÂM TỈNH THỨC** — lá số chỉ là bản đồ, Anh là người cầm la bàn.",
        f"",
        f"---",
        f"",
        f"_© YI-CHRONOS · Chiếu Đởm Kinh · Tổng đoán cuộc đời · {datetime.now().strftime('%d/%m/%Y')}_",
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
