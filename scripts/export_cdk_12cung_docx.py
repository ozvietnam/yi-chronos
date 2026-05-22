"""Export 12 cung Chiếu Đởm Kinh cache → .docx Word cho Anh đọc offline.

Usage:
  .venv/bin/python3 scripts/export_cdk_12cung_docx.py <person_key> [output.docx]
"""
from __future__ import annotations

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
CACHE_ROOT = PROJECT_ROOT / "data/yi_publishing/analysis_cache"

BRANCHES_ORDER = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

BRANCH_VI = {
    "Tý":   "Chuột — 23h-01h — phương Bắc — Thủy/Dương",
    "Sửu":  "Trâu — 01h-03h — phương Bắc-Đông Bắc — Thổ/Âm",
    "Dần":  "Hổ — 03h-05h — phương Đông-Đông Bắc — Mộc/Dương",
    "Mão":  "Mèo/Thỏ — 05h-07h — phương Đông — Mộc/Âm",
    "Thìn": "Rồng — 07h-09h — phương Đông-Đông Nam — Thổ/Dương",
    "Tỵ":   "Rắn — 09h-11h — phương Nam-Đông Nam — Hỏa/Âm",
    "Ngọ":  "Ngựa — 11h-13h — phương Nam — Hỏa/Dương",
    "Mùi":  "Dê — 13h-15h — phương Nam-Tây Nam — Thổ/Âm",
    "Thân": "Khỉ — 15h-17h — phương Tây-Tây Nam — Kim/Dương",
    "Dậu":  "Gà — 17h-19h — phương Tây — Kim/Âm",
    "Tuất": "Chó — 19h-21h — phương Tây-Tây Bắc — Thổ/Dương",
    "Hợi":  "Lợn — 21h-23h — phương Bắc-Tây Bắc — Thủy/Âm",
}


def find_cache_dir(person_slug: str) -> Path:
    """Find cache base dir for person."""
    # Try u1 first (most common)
    for uid_dir in CACHE_ROOT.glob("u*"):
        if (uid_dir / f"cdk_cung_{person_slug}_Tý").exists():
            return uid_dir
        if (uid_dir / f"cdk_cung__{person_slug}_Tý").exists():
            return uid_dir
    return CACHE_ROOT / "u1"


def load_cache(base_dir: Path, person_slug: str, branch: str) -> dict | None:
    """Load 1 cung cache, return luan_cung_compact dict."""
    # Try both prefix patterns
    for prefix in [f"cdk_cung_{person_slug}_{branch}", f"cdk_cung__{person_slug}_{branch}"]:
        p = base_dir / prefix / "luan_cung.json"
        if p.exists():
            with p.open() as f:
                j = json.load(f)
            compact = j.get("luan_cung_compact") or {}
            # Also check legacy 5-section format
            if not compact.get("ban_chat_va_quan_he"):
                legacy = j.get("luan_cung", {})
                if legacy and not legacy.get("_compact"):
                    return {
                        "_legacy": True,
                        "ban_chat_va_quan_he": legacy.get("ban_chat_cung", ""),
                        "sao_dong_y_nghia": legacy.get("sao_thu_cung", ""),
                        "ap_dung_loi_khuyen": (legacy.get("quan_he_voi_menh", "") + "\n\n" + legacy.get("ap_dung_doi_song", "") + "\n\n**Lời khuyên:**\n" + legacy.get("loi_khuyen", "")).strip(),
                        "provider": j.get("provider"),
                        "generated_at": j.get("generated_at"),
                    }
            compact["provider"] = j.get("provider")
            compact["generated_at"] = j.get("generated_at")
            compact["menh_branch"] = j.get("menh_branch")
            compact["person_name"] = j.get("person_name")
            return compact
    return None


def build_markdown(person_slug: str, person_name: str, menh_branch: str | None, cung_data: dict) -> str:
    """Build full markdown for 12 cung."""
    lines = [
        f"# LUẬN GIẢI 12 CUNG · CHIẾU ĐỞM KINH",
        f"",
        f"## Chủ nhân: {person_name}",
        f"",
        f"_Hệ Chiếu Đởm Kinh (照胆经) — phái khác Tử Vi Đẩu Số 14 chính tinh._",
        f"_Sử dụng 18 Phi Tinh với convention âm-dương đảo, lập theo Q4 p0269-p0299._",
        f"",
        f"---",
        f"",
    ]
    if menh_branch:
        lines.append(f"**MỆNH CDK của anh: {menh_branch}** ({BRANCH_VI.get(menh_branch, '?')})")
        lines.append(f"")
    # Generated meta
    first = next((d for d in cung_data.values() if d), None)
    if first:
        gen_at = first.get("generated_at", 0)
        if gen_at:
            dt = datetime.fromtimestamp(gen_at).strftime("%d/%m/%Y %H:%M")
            lines.append(f"_Sinh thành: {dt} · Provider: {first.get('provider', '?')}_")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# Lời mở đầu — Paradigm CDK")
    lines.append("")
    lines.append("> _\"Đẩu số chí huyền chí vi, lý chỉ dị minh.\"_")
    lines.append("")
    lines.append("Chiếu Đởm Kinh là một phái khác của Tử Vi Đẩu Số. Khác với 14 chính tinh chính thống, ")
    lines.append("phái này dùng **18 Phi Tinh** và convention **âm-dương đảo**. ")
    lines.append("Mỗi cung địa chi mang năng lượng riêng đồng dạng với con giáp, giờ, phương vị, ngũ hành.")
    lines.append("")
    lines.append("**Lưu ý:** Đây là **đọc đồng dạng**, KHÔNG phải dự đoán cứng. ")
    lines.append("Lá số phản chiếu cấu trúc, người là người quyết định.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 12 cung in canonical order
    for branch in BRANCHES_ORDER:
        data = cung_data.get(branch)
        if not data:
            continue
        is_menh = branch == menh_branch
        marker = " ⭐ (MỆNH)" if is_menh else ""
        lines.append(f"# {branch}{marker} — {BRANCH_VI.get(branch, '?')}")
        lines.append(f"")
        ban_chat = data.get("ban_chat_va_quan_he", "").strip()
        sao = data.get("sao_dong_y_nghia", "").strip()
        ap_dung = data.get("ap_dung_loi_khuyen", "").strip()
        if ban_chat:
            lines.append(f"## 1. Bản chất cung & Quan hệ với Mệnh")
            lines.append(f"")
            lines.append(ban_chat)
            lines.append(f"")
        if sao:
            lines.append(f"## 2. Phi Tinh đóng tại đây & Ý nghĩa")
            lines.append(f"")
            lines.append(sao)
            lines.append(f"")
        if ap_dung:
            lines.append(f"## 3. Áp dụng đời sống & Lời khuyên")
            lines.append(f"")
            lines.append(ap_dung)
            lines.append(f"")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append("")
    lines.append("# 📜 Lời kết")
    lines.append("")
    lines.append("Bản luận giải 12 cung CDK này được sinh bởi **DeepSeek V4 Pro** ")
    lines.append("theo paradigm Iron Rule #6 của YI-CHRONOS: **đọc đồng dạng, không predict cứng**.")
    lines.append("")
    lines.append("Mỗi cung gồm 3 lớp giải thích:")
    lines.append("1. **Bản chất cung & Quan hệ với Mệnh** — năng lượng nền + vị trí trong lá số")
    lines.append("2. **Phi Tinh đóng tại đây & Ý nghĩa** — sao gì, đắc/thất vị, cát/hung")
    lines.append("3. **Áp dụng đời sống & Lời khuyên** — ý nghĩa thực tế + lời khuyên cụ thể")
    lines.append("")
    lines.append("Người đọc nên kết hợp với **TÂM TỈNH THỨC** — lá số là tấm gương, người là người cầm la bàn.")
    lines.append("")
    lines.append(f"_© YI-CHRONOS · Chiếu Đởm Kinh 12 cung · Exported {datetime.now().strftime('%d/%m/%Y %H:%M')}_")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        person_slug = "_founder_cdk_dau"
    else:
        person_slug = sys.argv[1]
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else PROJECT_ROOT / f"data/published/CDK_12Cung_{person_slug}.docx"

    base_dir = find_cache_dir(person_slug)
    print(f"📂 Cache dir: {base_dir}")

    cung_data = {}
    person_name = "Vô danh"
    menh_branch = None
    for branch in BRANCHES_ORDER:
        d = load_cache(base_dir, person_slug, branch)
        if d:
            cung_data[branch] = d
            person_name = d.get("person_name", person_name)
            menh_branch = d.get("menh_branch", menh_branch)
            total = (
                len(d.get("ban_chat_va_quan_he", "")) +
                len(d.get("sao_dong_y_nghia", "")) +
                len(d.get("ap_dung_loi_khuyen", ""))
            )
            print(f"  ✅ {branch}: {total} chars")
        else:
            print(f"  ❌ {branch}: cache missing")

    if not cung_data:
        print("❌ Không tìm thấy cache nào.")
        sys.exit(1)

    md = build_markdown(person_slug, person_name, menh_branch, cung_data)
    md_path = output_path.with_suffix(".md")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    print(f"📝 Markdown: {md_path} ({len(md):,} chars)")

    # pandoc → docx
    result = subprocess.run(
        ["pandoc", str(md_path), "-o", str(output_path),
         "--from", "markdown+pipe_tables+blank_before_blockquote",
         "--to", "docx",
         "--standalone"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ Pandoc fail:\n{result.stderr}")
        sys.exit(1)
    print(f"📄 DOCX: {output_path} ({output_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
