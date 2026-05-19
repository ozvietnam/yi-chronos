"""feed_sages — Augment sage SOUL.md với reference library từ wiki SQLite.

Mỗi sage có SOUL.md là system prompt. Em add section "📚 Reference Library"
chứa top concepts/methods/cases liên quan đến chuyên môn sage đó.

USAGE:
    python3 -m engine.yi_translation.feed_sages
"""
from __future__ import annotations

import sqlite3
import shutil
import time
import json
from dataclasses import dataclass
from pathlib import Path

WIKI_DB = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3")
PROFILES_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/hermes_yi/profiles")
SKILLS_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/hermes_yi/skills")

REFERENCE_MARKER_START = "<!-- YI-WIKI-AUTOSYNC:BEGIN -->"
REFERENCE_MARKER_END = "<!-- YI-WIKI-AUTOSYNC:END -->"


# ⭐⭐⭐ Mai Hoa CORE TEACHINGS — từ thâm nhuần Quyển 3 (2026-05-18)
# Đây là nội dung TĨNH (không từ wiki query) — chứa cốt lõi Tổ sư mà sage phải nắm
MAI_HOA_CORE_TEACHINGS = """### 🌸 CỐT LÕI MAI HOA — VẬN PHÁP THI của Tổ sư (Q3 tr.78)

> _"Một vật vốn có một thân, một thân lại có một trời đất._
> _Biết rằng **muôn việc đều sẵn nơi ta**, mới dám đặt nền móng cho **Tam Tài**."_
>
> _"Trời từ một điểm mà phân hóa tạo hóa, người nơi tâm khởi lên mưu lược._
> _Tiên nhân cũng có hai lối nói, đạo chẳng truyền suông chỉ tại người."_

🌟 **Mai Hoa là MÔN HỌC ĐỒNG DẠNG** (isomorphic system). Cấu trúc vũ trụ = cấu trúc người = cấu trúc khoảnh khắc. Người và vũ trụ NGANG NHAU (Tam Tài).

→ Mai Hoa **KHÔNG dự đoán tương lai** — Mai Hoa **đọc tiểu vũ trụ hiện tại** để hiểu đại vũ trụ vận hành.

→ Khi user hỏi, bậc trí giả KHÔNG output "Cát/Hung/dự đoán outcome" — output là **"Tâm Anh đang ở đâu? Vũ trụ đang nói gì qua khoảnh khắc này?"**

---

### 📋 4 BƯỚC ĐOÁN QUẺ chính thức (Q3 tr.112-114)

**BƯỚC 1 — LỜI QUẺ + LỜI HÀO** (Kinh Dịch)
- Tra 64 quẻ và lời hào động trong Chu Dịch

**BƯỚC 2 — THỂ-DỤNG + NGŨ HÀNH sinh khắc**
- Thể quẻ = bản thân người hỏi
- Dụng quẻ = việc đang xem
- Dụng sinh Thể / tương hòa → CÁT
- Thể sinh Dụng (tiết khí) / tương khắc → HUNG

**BƯỚC 3 — NGOẠI ỨNG (Khắc-Ứng)**
- Hiện tượng bất thường xảy ra LÚC user khởi quẻ
- ⭐ **BẮT BUỘC hỏi user**: "Lúc Anh nghĩ về việc này, có hiện tượng gì bất thường không?
  (chim bay/đậu, vật rơi, tiếng động, lời nghe được, vật vỡ/khuyết...)"
- Điềm lành → cứu thêm. Điềm dữ → cảnh báo.

**BƯỚC 4 — TƯ THẾ THÂN THỂ**
- ⭐ **BẮT BUỘC hỏi user**: "Lúc Anh nghĩ về việc này, Anh đang ngồi / đi / chạy / nằm?"
- Mapping tốc độ thành công:
  - **Nằm** → chậm nhất
  - **Ngồi** → chậm trễ
  - **Đứng** → trung bình
  - **Đi bộ** → nhanh
  - **Chạy bộ** → rất nhanh

**🎯 PRIORITY (Q3 tr.114)**: _"Lấy quẻ Dịch làm chủ, lấy quan hệ khắc ứng làm thứ yếu."_
- Quẻ + Khắc ứng đều CÁT → đại cát đại lợi
- Quẻ + Khắc ứng đều HUNG → vô cùng ác liệt
- Một cát một hung → **LẤY LỜI QUẺ LÀM CHỦ**, tổng hợp các yếu tố khác

---

### 🔗 MAPPING Bát Quái ↔ Vạn vật (Q3 tr.102-104)

**Cơ thể người** (Hệ Tự Hạ: Phục Hy "lấy gần từ thân thể"):
- Càn 1 = đầu | Đoài 2 = lưỡi | Ly 3 = mắt | Chấn 4 = chân
- Tốn 5 = đùi | Khảm 6 = tai | Cấn 7 = tay | Khôn 8 = bụng

→ Nếu user nói "sờ tai" → Khảm. "Giậm chân" → Chấn. "Nháy mắt" → Ly.

**Đồ vật cầm trên tay**:
- Kim loại → Càn | Gỗ → Chấn | Vật liên quan nước → Khảm | Lửa → Ly
- Đất/gốm → Khôn | Đá → Cấn

**Màu áo** (Q3 tr.102):
- Càn 1 = vàng kim | Đoài 2 = trắng | Ly 3 = đỏ | Chấn 4 = xanh lam
- Tốn 5 = xanh biếc | Khảm 6 = đen | Cấn 7 = nâu | Khôn 8 = vàng

**Động vật đơn lẻ** (Q3 tr.90):
- Ngựa → Càn | Dê → Đoài | Rùa → Ly | Rắn → Chấn
- Gà → Tốn | Cá → Khảm | Chó → Cấn | Trâu → Khôn
- ⚠️ Phải con đơn lẻ. Bầy đàn KHÔNG dùng được.

---

### 🌀 BIẾN THÔNG CONTEXTUAL (Q3 tr.114) — Master vs Beginner

Tổ sư cảnh báo: _"Chỉ luận số mà không luận lý = **bàn chuyện trên giấy, cố chấp một chiều**."_

**CONTEXT điều chỉnh TƯỢNG SỐ**:
- Quẻ Chấn trong YẾN TIỆC → rồng không có → dùng **cá chép** thay
- Quẻ Chấn vào MÙA ĐÔNG → sấm không có → dùng **gió mạnh gào thét** thay
- Quẻ Càn vào MÙA ĐÔNG (Kim sát phạt) → có thể là **băng tuyết**, không phải "trời quang"

→ Sage TỐI THIỂU phải biết hỏi: "Context user là gì?" trước khi áp tượng cố định.

---

### 🪷 QUY TẮC TÂM của Tổ sư (Q3 tr.106-107)

1. **"Không nghi không bói"** — chỉ khi gặp việc đặc biệt
2. **"Một việc chỉ bói một lần"** — KHÔNG bói lại cùng việc → xúc phạm thần linh
3. **"Một câu hỏi → một phép → một quẻ"** — nếu user hỏi nhiều thứ, TÁCH ra hỏi từng phép
4. **"Đạo lý bói toán, cốt ở biến thông. Nằm ở sự huyền diệu của TÂM DỊCH"** (Q3 tr.110)

"""


@dataclass
class SageFeedSpec:
    profile_name: str
    title_vi: str
    concept_filter: str   # SQL WHERE clause để chọn concepts
    concept_limit: int
    case_filter: str
    case_limit: int
    method_filter: str
    method_limit: int
    intro_blurb: str
    match_and_cite_protocol: bool = False  # Mai Hoa cần check pattern + cite Tổ sư
    # ⭐ v0.14 18/5 — output target: nếu skill_relpath set → ghi auto-sync ra skill file
    # riêng (data/hermes_yi/skills/<skill_relpath>) thay vì append vào SOUL.md.
    # SOUL.md giữ "WHO + HOW", skill giữ "WHAT KNOWLEDGE".
    skill_relpath: str | None = None
    skill_routing_mode: str = "long"  # Gemini 1M context (free)
    skill_description: str = ""


# Specs cho mỗi sage
SAGE_SPECS = [
    SageFeedSpec(
        profile_name="mai-hoa-sage",
        title_vi="Mai Hoa Dịch Số",
        skill_relpath="mai-hoa/q3-wiki-citations.md",
        skill_routing_mode="long",
        skill_description="Kho dẫn chứng Mai Hoa Quyển 3 (图解梅花易数) — concepts, methods, cases Tổ sư. Load khi sage cần trích dẫn sâu.",
        concept_filter=(
            "first_seen_corpus = 'thieu-khang-tiet-tq' "
            "AND short_note IS NOT NULL AND length(short_note) >= 40 "
            # Loại bỏ thuật ngữ quá generic
            "AND canonical_vi NOT IN ('Trung Quốc', 'Bắc Tống', 'Tống', 'Nam Tống')"
        ),
        concept_limit=25,
        case_filter=(
            "source_book LIKE 'thieu-khang-tiet-tq%' "
            "AND output_actual IS NOT NULL "
            "AND output_actual != '' "
            "AND output_actual NOT LIKE '%Không ghi rõ%' "
            "AND length(historical_event) > 20"
        ),
        case_limit=8,
        method_filter=(
            "notes LIKE 'Trích từ Quyển 3%' "
            "AND procedure_steps != '[]' "
            "AND length(procedure_steps) > 50"
        ),
        method_limit=12,
        intro_blurb=(
            "Đây là kho tham khảo từ sách **图解梅花易数** (Đồ Giải Mai Hoa Dịch Số) "
            "do Thang Hành Dịch biên soạn. Bậc trí giả có thể trích dẫn các khái niệm, "
            "phương pháp và ví dụ Tổ sư khi diễn giải quẻ cho người hỏi."
        ),
        match_and_cite_protocol=True,
    ),
    SageFeedSpec(
        profile_name="tu-vi-sage",
        title_vi="Tử Vi Đẩu Số",
        concept_filter=(
            "first_seen_corpus = 'thieu-khang-tiet-tq' "
            "AND (canonical_vi LIKE '%Tử Vi%' OR canonical_zh LIKE '%紫微%' "
            "     OR canonical_vi LIKE '%cung%' OR canonical_vi LIKE '%Cung%' "
            "     OR canonical_vi LIKE '%Mệnh%' OR canonical_vi LIKE '%Thân%' "
            "     OR canonical_vi LIKE '%đại vận%' OR canonical_vi LIKE '%Đại Vận%') "
            "AND short_note IS NOT NULL AND length(short_note) >= 30"
        ),
        concept_limit=12,
        case_filter="1=0",  # Tử Vi sage không cần case study Mai Hoa
        case_limit=0,
        method_filter="1=0",
        method_limit=0,
        intro_blurb=(
            "Đây là kho tham khảo các thuật ngữ Tử Vi Đẩu Số được trích từ sách "
            "**图解梅花易数** chapter 紫微斗数 (pp.56-66). Có thể dùng khi gặp khái niệm "
            "cung Mệnh/Thân, Đại Vận, hoặc các sao trong lá số."
        ),
    ),
]


def query_concepts(con: sqlite3.Connection, spec: SageFeedSpec) -> list[dict]:
    cur = con.cursor()
    rows = cur.execute(
        f"SELECT canonical_vi, canonical_zh, aliases, short_note "
        f"FROM concept_index "
        f"WHERE {spec.concept_filter} "
        f"ORDER BY length(short_note) DESC "
        f"LIMIT {spec.concept_limit}"
    ).fetchall()
    return [
        {
            "vi": r[0],
            "zh": r[1] or "",
            "aliases": json.loads(r[2]) if r[2] else [],
            "note": r[3],
        }
        for r in rows
    ]


def query_cases(con: sqlite3.Connection, spec: SageFeedSpec) -> list[dict]:
    if spec.case_limit == 0:
        return []
    cur = con.cursor()
    rows = cur.execute(
        f"SELECT historical_event, inputs_recorded, output_predicted, output_actual, source_book "
        f"FROM case_studies "
        f"WHERE {spec.case_filter} "
        f"ORDER BY length(output_actual) DESC "
        f"LIMIT {spec.case_limit}"
    ).fetchall()
    return [
        {
            "event": r[0],
            "inputs": r[1] or "",
            "predicted": r[2] or "",
            "actual": r[3] or "",
            "source": r[4] or "",
        }
        for r in rows
    ]


def query_methods(con: sqlite3.Connection, spec: SageFeedSpec) -> list[dict]:
    if spec.method_limit == 0:
        return []
    cur = con.cursor()
    rows = cur.execute(
        f"SELECT name_vi, name_zh, domain, procedure_steps "
        f"FROM methods "
        f"WHERE {spec.method_filter} "
        f"ORDER BY length(procedure_steps) DESC "
        f"LIMIT {spec.method_limit}"
    ).fetchall()
    out = []
    for r in rows:
        try:
            steps = json.loads(r[3]) if r[3] else []
        except Exception:
            steps = []
        if steps:
            out.append({
                "name_vi": r[0],
                "name_zh": r[1] or "",
                "domain": r[2] or "",
                "steps": steps,
            })
    return out


def format_reference_section(
    spec: SageFeedSpec,
    concepts: list[dict],
    cases: list[dict],
    methods: list[dict],
) -> str:
    """Render reference section markdown."""
    lines = [REFERENCE_MARKER_START, ""]
    lines.append(f"## 📚 Kho tham khảo {spec.title_vi} (auto-sync từ wiki)")
    lines.append("")
    lines.append(spec.intro_blurb)
    lines.append("")
    lines.append(f"_Auto-generated {time.strftime('%Y-%m-%d %H:%M')}. KHÔNG edit thủ công vùng giữa các marker — sẽ bị overwrite lần sync sau._")
    lines.append("")

    # ⭐⭐⭐ Mai Hoa CORE TEACHINGS (chỉ inject vào mai-hoa-sage)
    if spec.match_and_cite_protocol:
        lines.append(MAI_HOA_CORE_TEACHINGS)
        lines.append("")

    if spec.match_and_cite_protocol:
        lines.append("### 🎯 QUY TRÌNH BẮT BUỘC khi user pose 1 quẻ Mai Hoa")
        lines.append("")
        lines.append("**Trước khi viết section READ, em PHẢI thực hiện 4 bước sau:**")
        lines.append("")
        lines.append("**BƯỚC 1 — SCAN:** Đọc kỹ phần \"📜 Ví dụ Tổ sư\" phía dưới.")
        lines.append("")
        lines.append("**BƯỚC 2 — MATCH:** Kiểm tra có case Tổ sư nào khớp ≥ 70% với input user không?")
        lines.append("  Tiêu chí match (mỗi tiêu chí 25%):")
        lines.append("  - Cùng kiểu **trigger / quan vật** (chim, hoa, tiếng động, màu, người, vật rơi…)")
        lines.append("  - Cùng **giờ/ngày chi** hoặc chi tương cận")
        lines.append("  - Cùng **loại câu hỏi** (cát/hung, người/việc, sự kiện sắp xảy ra)")
        lines.append("  - Cùng **quẻ Chánh/Hổ/Biến** hoặc 1 trong 3 trùng")
        lines.append("")
        lines.append("**BƯỚC 3 — CITE (nếu match ≥ 70%):** TRONG SECTION READ, BẮT BUỘC trích dẫn theo format:")
        lines.append("")
        lines.append("> 📜 **Pattern Tổ sư đã ghi:** \"[event Tổ sư]\" — predict \"[output_predicted]\" → thực tế \"[output_actual]\" _(nguồn: [source_book])_.")
        lines.append("> ")
        lines.append("> **Áp dụng cho user:** [tương đồng với case Tổ sư ở điểm X, khác ở điểm Y] → diễn giải tinh chỉnh là …")
        lines.append("")
        lines.append("**BƯỚC 4 — INDEPENDENT (nếu match < 70%):** Diễn giải bình thường, KHÔNG bịa case Tổ sư không có thật.")
        lines.append("")
        lines.append("⚠️ **Tuyệt đối tránh:** trả lời quẻ mà KHÔNG scan ví dụ Tổ sư trước. Đây là lỗi của tân môn đệ.")
        lines.append("")
        lines.append("⚠️ **Tuyệt đối tránh:** bịa case Tổ sư. Chỉ trích dẫn từ list dưới đây.")
        lines.append("")

    if concepts:
        lines.append("### 💎 Concepts cốt lõi")
        lines.append("")
        for c in concepts:
            zh = f" ({c['zh']})" if c['zh'] else ""
            aliases = ""
            if c["aliases"]:
                aliases = f" _aka {', '.join(c['aliases'])}_"
            lines.append(f"- **{c['vi']}**{zh}{aliases}: {c['note']}")
        lines.append("")

    if methods:
        lines.append("### 🛠️ Phương pháp Mai Hoa")
        lines.append("")
        for m in methods:
            zh = f" ({m['name_zh']})" if m["name_zh"] else ""
            lines.append(f"#### {m['name_vi']}{zh}")
            if m["domain"]:
                lines.append(f"_Domain: {m['domain']}_")
            lines.append("")
            for i, step in enumerate(m["steps"], 1):
                lines.append(f"{i}. {step}")
            lines.append("")

    if cases:
        lines.append("### 📜 Ví dụ Tổ sư (học pattern Mai Hoa)")
        lines.append("")
        for cs in cases:
            lines.append(f"- **{cs['event']}**")
            if cs["inputs"]:
                lines.append(f"  - Inputs: {cs['inputs']}")
            if cs["predicted"]:
                lines.append(f"  - Dự đoán: {cs['predicted']}")
            if cs["actual"]:
                lines.append(f"  - Thực tế: {cs['actual']}")
            if cs["source"]:
                lines.append(f"  - Nguồn: `{cs['source']}`")
        lines.append("")

    lines.append(REFERENCE_MARKER_END)
    return "\n".join(lines)


def apply_to_soul(soul_path: Path, reference: str) -> dict:
    """Insert/replace reference section in SOUL.md.

    Idempotent: nếu đã có marker → replace giữa marker.
    Nếu chưa có → append cuối file.
    """
    text = soul_path.read_text()
    if REFERENCE_MARKER_START in text and REFERENCE_MARKER_END in text:
        # Replace existing
        start = text.index(REFERENCE_MARKER_START)
        end = text.index(REFERENCE_MARKER_END) + len(REFERENCE_MARKER_END)
        new_text = text[:start] + reference + text[end:]
        action = "replaced"
    else:
        # Append
        new_text = text.rstrip() + "\n\n" + reference + "\n"
        action = "appended"
    soul_path.write_text(new_text)
    return {"action": action, "new_length": len(new_text), "old_length": len(text)}


def apply_to_skill(skill_path: Path, reference: str, spec: SageFeedSpec) -> dict:
    """⭐ v0.14 18/5 — Write auto-sync reference to skill file (NOT SOUL.md).

    Pattern: 'SOUL = WHO + HOW to think' / 'Skill = WHAT knowledge'.
    Skill file format follows Hermes SKILL_ROUTING_GUIDE.md (YAML frontmatter).

    SOUL.md gets a small pointer (skill manifest line) instead of 20k chars dump.
    """
    skill_path.parent.mkdir(parents=True, exist_ok=True)

    # YAML frontmatter per Hermes spec
    frontmatter = (
        "---\n"
        f"name: {skill_path.stem}\n"
        f"description: {spec.skill_description or 'Auto-synced knowledge dump from YI wiki'}\n"
        "metadata:\n"
        "  hermes:\n"
        f"    tags: [{spec.profile_name.replace('-sage','').replace('-','_')}, Reference, AutoSync, LongContext]\n"
        f"    routing_mode: {spec.skill_routing_mode}\n"
        "  source: engine/yi_translation/feed_sages.py\n"
        f"  auto_generated_at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "---\n\n"
    )
    full_text = frontmatter + f"# {spec.title_vi} — Kho dẫn chứng (auto-sync wiki)\n\n" + reference
    old_len = skill_path.read_text().__len__() if skill_path.exists() else 0
    skill_path.write_text(full_text)
    return {
        "action": "wrote_skill",
        "skill_path": str(skill_path),
        "new_length": len(full_text),
        "old_length": old_len,
    }


def feed_all_sages(*, dry_run: bool = False) -> dict:
    con = sqlite3.connect(WIKI_DB)
    try:
        results = {}
        for spec in SAGE_SPECS:
            sage_dir = PROFILES_ROOT / spec.profile_name
            soul = sage_dir / "SOUL.md"
            if not soul.exists():
                results[spec.profile_name] = {"error": f"SOUL.md not found at {soul}"}
                continue

            concepts = query_concepts(con, spec)
            cases = query_cases(con, spec)
            methods = query_methods(con, spec)
            reference = format_reference_section(spec, concepts, cases, methods)

            if dry_run:
                results[spec.profile_name] = {
                    "dry_run": True,
                    "concepts": len(concepts),
                    "methods": len(methods),
                    "cases": len(cases),
                    "reference_chars": len(reference),
                    "preview_first_lines": reference.split("\n")[:8],
                }
                continue

            # Backup SOUL
            backup = soul.with_suffix(f".md.bak-{int(time.time())}")
            shutil.copy2(soul, backup)

            if spec.skill_relpath:
                # ⭐ v0.14 — write auto-sync to skill file, strip from SOUL
                skill_path = SKILLS_ROOT / spec.skill_relpath
                r = apply_to_skill(skill_path, reference, spec)
                # Also strip existing auto-sync block from SOUL (one-time migration)
                soul_text = soul.read_text()
                if REFERENCE_MARKER_START in soul_text and REFERENCE_MARKER_END in soul_text:
                    start = soul_text.index(REFERENCE_MARKER_START)
                    end = soul_text.index(REFERENCE_MARKER_END) + len(REFERENCE_MARKER_END)
                    # Replace block with pointer
                    pointer = (
                        f"<!-- v0.14: Kho dẫn chứng đã tách → skills/{spec.skill_relpath} -->\n"
                        f"## 📚 Kho dẫn chứng — TÁCH RA SKILL\n\n"
                        f"Phần kho khái niệm/case Tổ sư (~20k chars) đã tách thành skill\n"
                        f"**`{spec.skill_relpath}`** (routing: `{spec.skill_routing_mode}`, Hermes load on-demand).\n\n"
                        f"Sage load skill này KHI cần trích dẫn sâu, KHÔNG load mỗi turn → tiết kiệm context.\n"
                    )
                    new_soul = soul_text[:start] + pointer + soul_text[end:]
                    soul.write_text(new_soul)
                    r["soul_stripped"] = True
                    r["soul_old_length"] = len(soul_text)
                    r["soul_new_length"] = len(new_soul)
            else:
                # Default: append to SOUL.md (legacy behavior)
                r = apply_to_soul(soul, reference)

            r.update({
                "concepts_injected": len(concepts),
                "methods_injected": len(methods),
                "cases_injected": len(cases),
                "backup": str(backup),
            })
            results[spec.profile_name] = r
        return results
    finally:
        con.close()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    result = feed_all_sages(dry_run=args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
