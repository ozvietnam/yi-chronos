"""CDK Cung Analyzer — luận giải sâu từng cung Chiếu Đởm Kinh bằng DeepSeek V4 Pro.

Strategy:
- Input: Person + branch (Tý/Sửu/.../Hợi)
- Engine cast CDK chart → biết Mệnh, sao đóng, relationship
- Build rich context: branch info Việt thuần + sao tại đó + Nhập Cốt verdicts + tam hợp/xung chiếu
- Call DeepSeek V4 Pro → 5 sections JSON
- Cache + auto-extract wiki (in-process hook)

Output schema:
  {
    "ban_chat_cung": "...",     # Bản chất năng lượng cung
    "sao_thu_cung": "...",      # Phân tích Phi Tinh đóng
    "quan_he_voi_menh": "...",  # Tam hợp / xung chiếu / phụ trợ
    "ap_dung_doi_song": "...",  # Ý nghĩa thực tế cho user
    "loi_khuyen": "...",        # Lời khuyên cụ thể
  }
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional

# Branch info Việt thuần (mirror frontend BRANCH_INFO)
BRANCH_INFO = {
    "Tý":   {"conGiap": "Chuột",  "gio": "23h00–01h00 (nửa đêm)",  "phuongVi": "Bắc",         "ngu_hanh": "Thủy", "am_duong": "Dương", "y_nghia": "Khởi đầu chu kỳ. Hạt giống ngủ chờ nảy mầm."},
    "Sửu":  {"conGiap": "Trâu",   "gio": "01h00–03h00 (gần sáng)", "phuongVi": "Bắc-Đông Bắc","ngu_hanh": "Thổ",  "am_duong": "Âm",    "y_nghia": "Nuôi dưỡng trong đất, chờ vươn lên."},
    "Dần":  {"conGiap": "Hổ",     "gio": "03h00–05h00 (rạng đông)","phuongVi": "Đông-Đông Bắc","ngu_hanh": "Mộc","am_duong": "Dương", "y_nghia": "Mầm cây nhú, hổ vươn vai sau giấc dài."},
    "Mão":  {"conGiap": "Mèo/Thỏ","gio": "05h00–07h00 (sáng sớm)", "phuongVi": "Đông",        "ngu_hanh": "Mộc",  "am_duong": "Âm",    "y_nghia": "Mặt trời mọc, cây đâm chồi, mềm mại kiên trì."},
    "Thìn": {"conGiap": "Rồng",   "gio": "07h00–09h00 (đầu ngày)", "phuongVi": "Đông-Đông Nam","ngu_hanh":"Thổ", "am_duong": "Dương", "y_nghia": "Sương tan, rồng cuộn mây, tích năng lượng."},
    "Tỵ":   {"conGiap": "Rắn",    "gio": "09h00–11h00 (giữa sáng)","phuongVi": "Nam-Đông Nam","ngu_hanh": "Hỏa", "am_duong": "Âm",    "y_nghia": "Rắn ra hang sưởi ấm, thông minh biến hóa."},
    "Ngọ":  {"conGiap": "Ngựa",   "gio": "11h00–13h00 (giữa trưa)","phuongVi": "Nam",         "ngu_hanh": "Hỏa", "am_duong": "Dương", "y_nghia": "Đỉnh Dương, ngựa phi nước đại."},
    "Mùi":  {"conGiap": "Dê",     "gio": "13h00–15h00 (xế trưa)",  "phuongVi": "Nam-Tây Nam", "ngu_hanh": "Thổ", "am_duong": "Âm",    "y_nghia": "Dê ăn cỏ ngon, thư thái."},
    "Thân": {"conGiap": "Khỉ",    "gio": "15h00–17h00 (xế chiều)", "phuongVi": "Tây-Tây Nam", "ngu_hanh": "Kim", "am_duong": "Dương", "y_nghia": "Khỉ chuyền cành, tinh ranh linh hoạt."},
    "Dậu":  {"conGiap": "Gà",     "gio": "17h00–19h00 (chiều tà)", "phuongVi": "Tây",         "ngu_hanh": "Kim", "am_duong": "Âm",    "y_nghia": "Gà về chuồng, thu mình kết thúc chu kỳ."},
    "Tuất": {"conGiap": "Chó",    "gio": "19h00–21h00 (chập tối)", "phuongVi": "Tây-Tây Bắc", "ngu_hanh": "Thổ", "am_duong": "Dương", "y_nghia": "Chó canh nhà, trung thành cảnh giác."},
    "Hợi":  {"conGiap": "Lợn",    "gio": "21h00–23h00 (đêm khuya)","phuongVi": "Bắc-Tây Bắc", "ngu_hanh": "Thủy","am_duong": "Âm",    "y_nghia": "Lợn ngủ no, tích lũy cho chu kỳ mới."},
}

TAM_HOP_CUC = {
    "Thủy": ["Thân", "Tý", "Thìn"],
    "Mộc":  ["Hợi", "Mão", "Mùi"],
    "Hỏa":  ["Dần", "Ngọ", "Tuất"],
    "Kim":  ["Tỵ", "Dậu", "Sửu"],
}
BRANCHES_ORDER = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


SYSTEM_PROMPT = """Bạn là chuyên gia **Chiếu Đởm Kinh** (照胆经) — paradigm phụ của Tử Vi Đẩu Số, dùng 18 Phi Tinh khác 14 chính tinh.

🎯 NHIỆM VỤ: Giảng giải ý nghĩa một CUNG cụ thể (1 trong 12 địa chi) trong lá số CDK của user.

⚠️ ĐỐI TƯỢNG ĐỌC: **NGƯỜI VIỆT BÌNH THƯỜNG**, không biết Hán-Việt. Văn phong:
- Tiếng Việt thuần hiện đại, gần gũi như đang nói chuyện
- Mỗi từ Hán-Việt LẦN ĐẦU phải giải nghĩa trong ngoặc đơn ngay
- Có ví dụ đời sống cụ thể, không sa đà cổ văn
- KHÔNG predict cứng — paradigm CDK là **đọc đồng dạng** (Iron Rule #6)

📋 OUTPUT JSON THUẦN — 5 keys CHÍNH XÁC:
{
  "ban_chat_cung": "Bản chất năng lượng vùng cung này — gắn với con giáp, giờ, phương vị, ngũ hành. ~300-500 chữ Việt.",
  "sao_thu_cung": "Phân tích Phi Tinh đang đóng tại đây (nếu có). Mỗi sao: tên, ý nghĩa, đắc/thất vị, cát/hung. Nếu không có sao → giải thích vùng tĩnh. ~400-600 chữ.",
  "quan_he_voi_menh": "Cung này có quan hệ gì với Mệnh CDK của user? Là Mệnh / tam hợp / xung chiếu / phụ trợ. Ý nghĩa quan hệ. ~250-400 chữ.",
  "ap_dung_doi_song": "Cụ thể trong cuộc sống user nghĩa là gì? Ví dụ thực tế (sự nghiệp / sức khỏe / quan hệ). So sánh với người không có cấu trúc tương tự. ~400-700 chữ.",
  "loi_khuyen": "3-5 lời khuyên cụ thể, actionable. Tránh chung chung. ~200-400 chữ."
}

QUY TẮC:
- BẮT ĐẦU output bằng `{`, KẾT THÚC bằng `}`. KHÔNG markdown fence, KHÔNG preamble.
- Newline trong string dùng \\n. Quote " escape thành \\".
- Mỗi value là STRING đơn (không nested object).
- Tổng độ dài 1500-2500 chars Việt cho cả 5 sections.
"""


def _cdk_engine_cast(person) -> dict:
    """Cast CDK chart for person."""
    from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
    from core.chronos import calculate_chronos_state
    from datetime import datetime

    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone or "Asia/Ho_Chi_Minh")
    _d, m_str, _y = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]
    return cast_chieu_dom_kinh(
        year_stem=year_parts[0],
        year_branch=year_parts[1],
        lunar_month=int(m_str),
        hour_branch=hour_branch,
        gender=person.gender,
    )


def _load_nhap_cot() -> dict:
    """Load Nhập Cốt Tiên Kinh verdicts."""
    p = Path(__file__).resolve().parent.parent.parent / "data/tu_vi/nhap_cot_tien_kinh_tong_doan.json"
    if not p.exists():
        return {"per_star_tong_doan": []}
    with p.open() as f:
        return json.load(f)


def _build_context(person, branch: str, cdk_chart: dict, nhap_cot: dict) -> str:
    """Build rich context Việt thuần cho DeepSeek prompt."""
    info = BRANCH_INFO.get(branch, {})
    menh_branch = cdk_chart.get("menh_branch")

    # Determine relationship
    rel = "phụ trợ"
    rel_detail = "Bình thường, không tương tác trực tiếp với Mệnh."
    menh_idx = BRANCHES_ORDER.index(menh_branch) if menh_branch in BRANCHES_ORDER else -1
    branch_idx = BRANCHES_ORDER.index(branch) if branch in BRANCHES_ORDER else -1
    cuc_name = None
    if branch == menh_branch:
        rel = "Mệnh"
        rel_detail = f"Đây CHÍNH LÀ cung Mệnh CDK của user."
    elif menh_idx >= 0 and branch_idx >= 0 and (branch_idx + 6) % 12 == menh_idx:
        rel = "xung chiếu"
        rel_detail = f"Đối diện 180° với Mệnh — áp lực ngược, lực kéo."
    else:
        for c_name, members in TAM_HOP_CUC.items():
            if menh_branch in members and branch in members and branch != menh_branch:
                rel = "tam hợp"
                cuc_name = c_name
                rel_detail = f"Tam hợp {c_name} cục với Mệnh — phối hợp tốt, hỗ trợ tăng cường."
                break

    # Stars at this branch
    stars_here = []
    nhap_cot_by_star = {item["star"]: item for item in nhap_cot.get("per_star_tong_doan", [])}
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    for star, b in (cdk_chart.get("stars") or {}).items():
        if b != branch:
            continue
        full = NAME_MAP.get(star, star)
        item = nhap_cot_by_star.get(full, {})
        is_hy = branch in (item.get("hy_cung") or [])
        stars_here.append({
            "name": star,
            "full_name": full,
            "category": item.get("category", "?"),
            "is_hy": is_hy,
            "verdict": (item.get("verdict_summary") or "")[:400],
            "source": item.get("source_ref", ""),
        })

    # Mệnh stars (cho context)
    menh_stars = []
    for star, b in (cdk_chart.get("stars") or {}).items():
        if b == menh_branch:
            full = NAME_MAP.get(star, star)
            menh_stars.append(f"{star} ({full})")

    lines = [
        f"╔════════════════════════════════════════════════════════════════╗",
        f"║ LUẬN GIẢI CUNG CDK CHO USER",
        f"╠════════════════════════════════════════════════════════════════╣",
        f"║ Tên user: {person.name}",
        f"║ Sinh: {person.birth_datetime_local}, giới: {person.gender}",
        f"╚════════════════════════════════════════════════════════════════╝",
        "",
        f"━━━ THÔNG TIN LÁ SỐ CDK ━━━",
        f"  • Mệnh CDK của user đóng tại: **{menh_branch}**",
        f"  • Các sao thủ Mệnh: {', '.join(menh_stars) or '(không có)'}",
        f"  • Năm sinh: {cdk_chart.get('year_stem', '')} {cdk_chart.get('year_branch', '')}",
        "",
        f"━━━ CUNG CẦN LUẬN GIẢI: {branch} ━━━",
        f"  • Con giáp: {info.get('conGiap', '?')}",
        f"  • Giờ trong ngày: {info.get('gio', '?')}",
        f"  • Phương vị: {info.get('phuongVi', '?')}",
        f"  • Ngũ hành: {info.get('ngu_hanh', '?')} · Âm-Dương: {info.get('am_duong', '?')}",
        f"  • Ý nghĩa khoảnh khắc: {info.get('y_nghia', '?')}",
        "",
        f"━━━ QUAN HỆ VỚI MỆNH ━━━",
        f"  • Loại quan hệ: **{rel}**",
        f"  • Chi tiết: {rel_detail}",
    ]
    if cuc_name:
        lines.append(f"  • Tam hợp cục: {cuc_name} ({' + '.join(TAM_HOP_CUC[cuc_name])})")

    lines.append("")
    lines.append(f"━━━ PHI TINH ĐÓNG TẠI {branch} ({len(stars_here)} sao) ━━━")
    if not stars_here:
        lines.append("  (không có Phi Tinh nào đóng tại đây — vùng tĩnh, chỉ kích hoạt khi Đại Hạn chạm)")
    else:
        for s in stars_here:
            flag = "ĐẮC ĐỊA (hỷ cung)" if s["is_hy"] else "THẤT VỊ (không thuộc hỷ cung)"
            lines.append(f"  ⭐ {s['name']} ({s['full_name']}) — nhóm {s['category']} — {flag}")
            lines.append(f"     Verdict (Nhập Cốt Tiên Kinh): {s['verdict']}")
            if s['source']:
                lines.append(f"     Source: {s['source']}")

    return "\n".join(lines)


def _cache_path(person_key: str, user_id: Optional[int], branch: str) -> Path:
    uid = f"u{user_id}" if user_id else "anonymous"
    safe_pk = re.sub(r"[^a-zA-Z0-9_-]+", "_", person_key or "anon")
    return Path(__file__).resolve().parent.parent.parent / "data/yi_publishing/analysis_cache" / uid / f"cdk_cung_{safe_pk}_{branch}" / "luan_cung.json"


def luan_cdk_cung(person, branch: str, force: bool = False) -> dict:
    """Luận giải sâu một cung CDK bằng DeepSeek V4 Pro.

    Args:
        person: Person object (engine.tu_vi.analyzer.Person)
        branch: Tên địa chi (Tý/Sửu/.../Hợi)
        force: bypass cache

    Returns:
        {status, luan_cung: {5 sections}, provider, tokens, cost_usd, ...}
    """
    if branch not in BRANCHES_ORDER:
        return {"status": "error", "message": f"Invalid branch: {branch}"}

    # Cache check
    cache_p = _cache_path(person.person_key, person.user_id, branch)
    if not force and cache_p.exists():
        try:
            with cache_p.open() as f:
                cached = json.load(f)
            cached["from_cache"] = True
            return cached
        except Exception:
            pass

    # Cast CDK + load Nhập Cốt
    try:
        cdk_chart = _cdk_engine_cast(person)
    except Exception as e:
        return {"status": "error", "message": f"CDK cast failed: {e}"}
    nhap_cot = _load_nhap_cot()

    # Build prompt context
    context = _build_context(person, branch, cdk_chart, nhap_cot)

    user_prompt = f"""{context}

Viết luận giải SÂU cung {branch} theo 5 sections (output JSON đúng schema 5 keys).
Đối tượng đọc: người Việt bình thường — văn phong dễ hiểu, có ví dụ đời sống, mỗi từ Hán-Việt lần đầu phải giải nghĩa.

Schema bắt buộc:
{{
  "ban_chat_cung": "...",
  "sao_thu_cung": "...",
  "quan_he_voi_menh": "...",
  "ap_dung_doi_song": "...",
  "loi_khuyen": "..."
}}"""

    # Provider chain
    from engine.ai.registry import get_registry
    registry = get_registry()
    provider_chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
    candidate_providers = []
    for name in provider_chain:
        try:
            p = registry.get(name)
            if p and p.is_configured and not registry.is_unhealthy(name):
                candidate_providers.append(p)
        except Exception:
            pass
    if not candidate_providers:
        return {"status": "error", "message": "No LLM provider configured"}

    resp = None
    last_err = None
    tried = []
    for cand in candidate_providers:
        tried.append(cand.name)
        try:
            resp = cand.chat(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
                max_tokens=8000,
            )
            provider_used = cand
            break
        except Exception as e:
            err_str = str(e)
            last_err = f"{cand.name}: {err_str[:200]}"
            if any(sig in err_str for sig in ["401", "403", "1113", "invalid", "Authentication", "balance", "quota"]):
                registry.mark_unhealthy(cand.name, err_str[:100])
            continue
    if resp is None:
        return {"status": "error", "message": f"All providers failed. Tried: {tried}. Last: {last_err}"}

    content = resp.content if hasattr(resp, "content") else str(resp)
    # Strip markdown fences
    if "```" in content:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if m:
            content = m.group(1)
        else:
            content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))

    luan_cung = None
    try:
        luan_cung = json.loads(content)
    except Exception:
        try:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                luan_cung = json.loads(content[start:end + 1])
        except Exception:
            pass
    if luan_cung is None:
        # Last-ditch: smart-quote cleanup
        cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        try:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                luan_cung = json.loads(cleaned[start:end + 1])
        except Exception:
            luan_cung = {"ban_chat_cung": content, "_parse_error": True}

    prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
    completion_tokens = getattr(resp, "completion_tokens", 0) or 0
    cost = getattr(resp, "cost_usd", 0) or 0

    data = {
        "status": "ok",
        "person_key": person.person_key,
        "person_name": person.name,
        "branch": branch,
        "menh_branch": cdk_chart.get("menh_branch"),
        "generated_at": int(time.time()),
        "provider": provider_used.name,
        "model": "v4_pro",
        "cost_usd": round(cost, 6),
        "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
        "luan_cung": luan_cung,
        "paradigm_note": "Luận giải cung CDK bằng DeepSeek V4 Pro — paradigm Iron Rule #6 (đọc đồng dạng, không predict).",
    }
    # Save cache
    try:
        cache_p.parent.mkdir(parents=True, exist_ok=True)
        with cache_p.open("w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ Cache save failed: {e}")

    # Auto-extract → wiki (in-process hook, reuse existing extractor)
    try:
        from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
        adapter = {
            "status": "ok",
            "person_name": person.name,
            "person_key": person.person_key,
            "generated_at": data["generated_at"],
            "provider": data["provider"],
            "phe_menh_sau": luan_cung,  # extractor checks this key
        }
        result = extract_phe_menh_to_wiki(adapter, verbose=False)
        data["wiki_extracted"] = {
            "added_quotes": result.get("added_quotes", 0),
            "added_cach_cuc": result.get("added_cach_cuc", 0),
        }
    except Exception as e:
        data["wiki_extracted"] = {"error": str(e)}

    return data
