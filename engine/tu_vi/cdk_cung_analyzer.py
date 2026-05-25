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


# ─── Bulk luận 12 cung trong 2 batches song song ─────────────────────────────

SYSTEM_PROMPT_BULK = """Bạn là chuyên gia **Chiếu Đởm Kinh** (照胆经) — giảng giải lá số CDK cho NGƯỜI VIỆT BÌNH THƯỜNG.

🎯 NHIỆM VỤ: Luận giải **6 cung** trong 1 batch (cùng một lá số).

⚠️ ĐỐI TƯỢNG ĐỌC: Người Việt không biết Hán-Việt. Văn phong:
- Tiếng Việt thuần hiện đại, dễ hiểu
- Mỗi thuật ngữ Hán-Việt LẦN ĐẦU phải giải nghĩa trong ngoặc đơn
- Mỗi cung viết **NGẮN GỌN** (~1200-1800 chars Việt) — tập trung điểm quan trọng nhất
- Có ví dụ đời sống cụ thể, không sa đà cổ văn
- Paradigm CDK = đọc đồng dạng (Iron Rule #6), KHÔNG predict cứng

📋 OUTPUT JSON THUẦN — 1 object, mỗi cung là 1 key, value là object 3 sections:
{
  "<chi 1>": {
    "ban_chat_va_quan_he": "Bản chất cung + quan hệ với Mệnh (~400-600 chars).",
    "sao_dong_y_nghia": "Phi Tinh đóng tại cung + ý nghĩa (đắc/thất vị, cát/hung) (~500-800 chars).",
    "ap_dung_loi_khuyen": "Áp dụng đời sống + lời khuyên ngắn 2-3 điểm (~400-600 chars)."
  },
  "<chi 2>": {...},
  ...
}

QUY TẮC:
- BẮT ĐẦU output bằng `{`, KẾT THÚC bằng `}`. KHÔNG ``` fence, KHÔNG preamble.
- Newline trong string dùng \\n. Quote " escape thành \\".
- 6 keys CHÍNH XÁC đúng tên 6 chi của batch này.
- Mỗi value là object với 3 fields: ban_chat_va_quan_he, sao_dong_y_nghia, ap_dung_loi_khuyen.
"""


def _build_bulk_context(person, batch_branches: list[str], cdk_chart: dict, nhap_cot: dict) -> str:
    """Build context cho 1 batch 6 cung."""
    menh_branch = cdk_chart.get("menh_branch")
    nhap_cot_by_star = {item["star"]: item for item in nhap_cot.get("per_star_tong_doan", [])}
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    # Mệnh stars list
    menh_stars = []
    for star, b in (cdk_chart.get("stars") or {}).items():
        if b == menh_branch:
            full = NAME_MAP.get(star, star)
            menh_stars.append(f"{star} ({full})")

    lines = [
        f"━━━ THÔNG TIN LÁ SỐ CDK ━━━",
        f"  • Chủ nhân: {person.name} | Sinh: {person.birth_datetime_local}",
        f"  • Mệnh CDK đóng tại: **{menh_branch}**",
        f"  • Sao thủ Mệnh: {', '.join(menh_stars) or '(không)'}",
        f"  • Tam hợp với Mệnh:",
    ]
    cuc_name = None
    for c, members in TAM_HOP_CUC.items():
        if menh_branch in members:
            cuc_name = c
            lines.append(f"      Tam hợp {c} cục: {' + '.join(members)}")
            break
    menh_idx = BRANCHES_ORDER.index(menh_branch) if menh_branch in BRANCHES_ORDER else -1
    if menh_idx >= 0:
        xung = BRANCHES_ORDER[(menh_idx + 6) % 12]
        lines.append(f"  • Xung chiếu Mệnh: {xung}")
    lines.append("")
    lines.append(f"━━━ 6 CUNG CẦN LUẬN GIẢI BATCH NÀY ━━━")
    for b in batch_branches:
        info = BRANCH_INFO.get(b, {})
        rel = "MỆNH" if b == menh_branch else (
            "tam hợp" if cuc_name and b in TAM_HOP_CUC.get(cuc_name, []) else
            ("xung chiếu" if menh_idx >= 0 and BRANCHES_ORDER.index(b) == (menh_idx + 6) % 12 else "phụ trợ")
        )
        # Stars at this branch
        stars_at = []
        for star, br in (cdk_chart.get("stars") or {}).items():
            if br == b:
                full = NAME_MAP.get(star, star)
                item = nhap_cot_by_star.get(full, {})
                is_hy = b in (item.get("hy_cung") or [])
                cat = item.get("category", "?")
                stars_at.append(f"{star} ({full}) — {cat}{' — HỶ' if is_hy else ' — thất vị' if item else ''}")
        lines.append(f"")
        lines.append(f"  ▸ Cung **{b}** ({info.get('conGiap', '?')})  [{rel}]")
        lines.append(f"     Giờ: {info.get('gio', '?')} | Phương: {info.get('phuongVi', '?')} | {info.get('ngu_hanh', '?')}-{info.get('am_duong', '?')}")
        lines.append(f"     Ý nghĩa khoảnh khắc: {info.get('y_nghia', '?')}")
        if stars_at:
            for s in stars_at:
                lines.append(f"     ⭐ {s}")
        else:
            lines.append(f"     (không có Phi Tinh đóng)")
    return "\n".join(lines)


def _call_one_batch(person, batch_branches: list[str], cdk_chart: dict, nhap_cot: dict) -> dict:
    """Call DeepSeek for 1 batch of 6 branches. Returns dict {branch: {3 sections}}."""
    context = _build_bulk_context(person, batch_branches, cdk_chart, nhap_cot)
    user_prompt = f"""{context}

Viết luận giải cho 6 cung trên — output JSON 6 keys chính xác:
{{
{chr(10).join(f'  "{b}": {{"ban_chat_va_quan_he": "...", "sao_dong_y_nghia": "...", "ap_dung_loi_khuyen": "..."}}' + ("," if i < len(batch_branches) - 1 else "") for i, b in enumerate(batch_branches))}
}}

Tổng độ dài batch này khoảng 8000-12000 chars Việt cho 6 cung × 3 sections."""

    from engine.ai.registry import get_registry
    registry = get_registry()
    chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
    candidates = []
    for n in chain:
        try:
            p = registry.get(n)
            if p and p.is_configured and not registry.is_unhealthy(n):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return {"_error": "No provider configured"}

    resp = None
    last_err = None
    provider_used = None
    for cand in candidates:
        try:
            resp = cand.chat(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_BULK},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
                max_tokens=12000,
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
        return {"_error": last_err or "All providers failed"}

    content = resp.content if hasattr(resp, "content") else str(resp)
    if "```" in content:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if m:
            content = m.group(1)
        else:
            content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        try:
            start = content.find("{"); end = content.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end + 1])
        except Exception:
            pass
    if parsed is None:
        cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        try:
            start = cleaned.find("{"); end = cleaned.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(cleaned[start:end + 1])
        except Exception:
            parsed = {"_parse_error": True, "_raw": content}

    return {
        "_provider": provider_used.name if provider_used else None,
        "_prompt_tokens": getattr(resp, "prompt_tokens", 0) or 0,
        "_completion_tokens": getattr(resp, "completion_tokens", 0) or 0,
        "_branches": batch_branches,
        "data": parsed,
    }


def luan_toan_bo_cung(person, force: bool = False) -> dict:
    """Luận TOÀN BỘ 12 cung trong 2 batches × 6 cung (parallel).

    Returns: {status, results: {Tý: {...}, Sửu: {...}, ...}, total_time, fresh_calls, provider, tokens}
    """
    import concurrent.futures

    # Cast CDK + load Nhập Cốt once
    try:
        cdk_chart = _cdk_engine_cast(person)
    except Exception as e:
        return {"status": "error", "message": f"CDK cast failed: {e}"}
    nhap_cot = _load_nhap_cot()

    # Check cache for each cung — only fetch missing ones
    results: dict[str, dict] = {}
    missing: list[str] = []
    for b in BRANCHES_ORDER:
        cache_p = _cache_path(person.person_key, person.user_id, b)
        if not force and cache_p.exists():
            try:
                with cache_p.open() as f:
                    cached = json.load(f)
                # Normalize to bulk schema (3 sections)
                lc = cached.get("luan_cung", {})
                if lc and isinstance(lc, dict):
                    # Merge per-cung 5-section format → 3-section format for UI consistency
                    results[b] = {
                        "ban_chat_va_quan_he": lc.get("ban_chat_cung") or lc.get("ban_chat_va_quan_he", "") + (("\n\n" + lc.get("quan_he_voi_menh", "")) if lc.get("quan_he_voi_menh") else ""),
                        "sao_dong_y_nghia": lc.get("sao_thu_cung") or lc.get("sao_dong_y_nghia", ""),
                        "ap_dung_loi_khuyen": (lc.get("ap_dung_doi_song", "") + ("\n\n**Lời khuyên:**\n" + lc.get("loi_khuyen", "") if lc.get("loi_khuyen") else "")) or lc.get("ap_dung_loi_khuyen", ""),
                        "_from_cache": True,
                    }
                    continue
            except Exception:
                pass
        missing.append(b)

    fresh_calls = 0
    provider_used = None
    total_prompt_tokens = 0
    total_completion_tokens = 0

    if missing:
        # Split missing into 2 batches (or fewer if <6 missing)
        batch_size = max(6, (len(missing) + 1) // 2)
        batches = [missing[i:i + batch_size] for i in range(0, len(missing), batch_size)]

        # SERIAL with retry-on-empty (tránh rate limit DeepSeek + retry nếu LLM trả empty)
        batch_results = []
        for batch_idx, batch in enumerate(batches):
            print(f"📡 Batch {batch_idx + 1}/{len(batches)}: gen {batch}...")
            attempts = 0
            batch_result = None
            while attempts < 3:
                attempts += 1
                br = _call_one_batch(person, batch, cdk_chart, nhap_cot)
                # Check if empty
                d = br.get("data", {})
                normalized = {k.strip(): v for k, v in d.items() if isinstance(k, str)} if isinstance(d, dict) else {}
                if br.get("_error"):
                    print(f"   ⚠ Attempt {attempts} error: {br.get('_error')[:100]}")
                    if attempts < 3:
                        import time as _t; _t.sleep(2)
                        continue
                if not normalized or all(not v for v in normalized.values()):
                    print(f"   ⚠ Attempt {attempts}: empty response (keys={list(normalized.keys())}). Retrying...")
                    if attempts < 3:
                        import time as _t; _t.sleep(3)
                        continue
                # Success
                br["data"] = normalized
                batch_result = br
                print(f"   ✓ Batch {batch_idx + 1} OK ({len(normalized)} cung)")
                break
            if batch_result is None:
                # Give up — record error but don't fail entire bulk
                print(f"   ❌ Batch {batch_idx + 1} failed after 3 attempts")
                batch_result = {"data": {}, "_branches": batch, "_provider": None,
                                "_prompt_tokens": 0, "_completion_tokens": 0,
                                "_error": "Empty after 3 retries"}
            batch_results.append(batch_result)

        # Process all batches
        for batch_result in batch_results:
                if batch_result.get("_error") and not batch_result.get("data"):
                    continue  # Skip failed batches
                provider_used = batch_result.get("_provider", provider_used)
                total_prompt_tokens += batch_result.get("_prompt_tokens", 0)
                total_completion_tokens += batch_result.get("_completion_tokens", 0)
                batch_data = batch_result.get("data", {})
                # Normalize keys (strip whitespace, handle accent variants)
                normalized = {}
                for k, v in (batch_data.items() if isinstance(batch_data, dict) else []):
                    if isinstance(k, str):
                        normalized[k.strip()] = v
                batch_data = normalized
                for b in batch_result.get("_branches", []):
                    cung_data = batch_data.get(b) or batch_data.get(b.strip()) or {}
                    if not cung_data or not isinstance(cung_data, dict):
                        print(f"⚠ Bulk: cung {b!r} không có data trong batch. LLM keys: {list(batch_data.keys())}")
                    if isinstance(cung_data, dict) and not cung_data.get("_parse_error") and cung_data:
                        results[b] = cung_data
                        results[b]["_from_cache"] = False
                        fresh_calls += 1
                        # Save individual cache (compat with per-cung lookup)
                        try:
                            cache_p = _cache_path(person.person_key, person.user_id, b)
                            cache_p.parent.mkdir(parents=True, exist_ok=True)
                            # Save in BOTH formats for backward compat
                            save_data = {
                                "status": "ok",
                                "person_key": person.person_key,
                                "person_name": person.name,
                                "branch": b,
                                "menh_branch": cdk_chart.get("menh_branch"),
                                "generated_at": int(time.time()),
                                "provider": batch_result.get("_provider"),
                                "model": "v4_pro_bulk",
                                "luan_cung": {
                                    # Keep 3-section bulk format
                                    "ban_chat_cung": cung_data.get("ban_chat_va_quan_he", ""),
                                    "sao_thu_cung": cung_data.get("sao_dong_y_nghia", ""),
                                    "quan_he_voi_menh": "",
                                    "ap_dung_doi_song": cung_data.get("ap_dung_loi_khuyen", ""),
                                    "loi_khuyen": "",
                                    "_compact": True,
                                },
                                "luan_cung_compact": cung_data,  # 3-section format
                            }
                            with cache_p.open("w") as f:
                                json.dump(save_data, f, ensure_ascii=False, indent=2)
                        except Exception as e:
                            print(f"⚠ Cache save {b} failed: {e}")
                    else:
                        results[b] = {"_parse_error": True}

    # Auto-extract wiki (use combined text)
    try:
        from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
        combined = {}
        for b, sections in results.items():
            if isinstance(sections, dict):
                combined[f"cung_{b}"] = " ".join(
                    str(v) for k, v in sections.items() if not k.startswith("_") and isinstance(v, str)
                )
        adapter = {
            "status": "ok",
            "person_name": person.name,
            "person_key": person.person_key,
            "generated_at": int(time.time()),
            "provider": provider_used or "?",
            "phe_menh_sau": combined,
        }
        extract_phe_menh_to_wiki(adapter, verbose=False)
    except Exception as e:
        print(f"⚠ Wiki extract failed: {e}")

    return {
        "status": "ok",
        "person_key": person.person_key,
        "person_name": person.name,
        "menh_branch": cdk_chart.get("menh_branch"),
        "results": results,
        "fresh_calls": fresh_calls,
        "cached_count": 12 - fresh_calls,
        "provider": provider_used,
        "tokens": {"prompt": total_prompt_tokens, "completion": total_completion_tokens},
        "generated_at": int(time.time()),
    }


# ─── TỔNG ĐOÁN CẢ CUỘC ĐỜI (synthesis CƠ + BIẾN) ──────────────────────────────

SYSTEM_PROMPT_TONG_DOAN = """Bạn là chuyên gia **Chiếu Đởm Kinh** giảng giải TỔNG ĐOÁN CẢ CUỘC ĐỜI cho một người Việt bình thường.

🎯 NHIỆM VỤ: Dựa vào 12 cung CDK (lớp CƠ, đã luận sẵn) + 8 vòng Đại Hạn (lớp BIẾN), viết **bản tổng đoán cuộc đời xuyên 4 giai đoạn**.

⚠️ ĐỐI TƯỢNG ĐỌC: Người Việt không biết Hán-Việt. Văn phong:
- Tiếng Việt thuần hiện đại, gần gũi như tâm sự với người thân
- Mỗi thuật ngữ Hán-Việt LẦN ĐẦU phải giải nghĩa trong ngoặc đơn
- Có ví dụ đời sống, so sánh thực tế
- Paradigm Iron Rule #6: **ĐỌC ĐỒNG DẠNG, KHÔNG PREDICT CỨNG**
- Dùng "có xu hướng", "dễ", "thường", "mỗ niên" khi nói về tương lai
- TUYỆT ĐỐI tránh "anh SẼ thành công năm X", "anh PHẢI gặp thất bại"

📋 OUTPUT JSON THUẦN — 6 keys CHÍNH XÁC:
{
  "tong_quan_cuoc_doi": "Bản chất tổng thể cuộc đời, lá số nói gì về anh (~600-900 chars).",
  "bon_giai_doan_doi": "**4 giai đoạn đời** theo 8 vòng Đại Hạn (mỗi 2 vòng = 1 giai đoạn). Viết liền mạch, không tách bullet nhỏ. Phân ra rõ: 'Sơ niên - Thiếu niên (1-20)', 'Thanh niên (21-40)', 'Trung niên (41-60)', 'Lão thành (61-80+)'. Mỗi giai đoạn ~600-800 chars Việt, có dẫn cung Đại Hạn cụ thể. Tổng ~2500-3200 chars.",
  "cach_chinh_cuoc_doi": "Cách cục lớn nhất chi phối toàn đời (Mệnh có sao gì, tam hợp gì, xung chiếu gì), 'CEO mẫu kỷ luật' hay 'nghệ sĩ tự do', v.v. (~500-700 chars).",
  "dinh_va_day": "Đỉnh cao + Đáy (thử thách lớn) trong đời. Khi nào, ở giai đoạn nào (~400-600 chars).",
  "loi_khuyen_xuyen_doi": "5-7 lời khuyên cụ thể, actionable, áp dụng cho cả đời (~500-700 chars).",
  "ket_tam_an": "Lời kết theo paradigm Iron Rule #6 — 'thập bát tinh chuyển, tại nhân biến thông'. Khuyên anh giữ tâm tỉnh thức (~300-450 chars)."
}

QUY TẮC:
- BẮT ĐẦU bằng `{`, KẾT THÚC bằng `}`. KHÔNG ``` fence, KHÔNG preamble.
- Newline trong string dùng \\n. Quote " escape thành \\".
- Tổng 4500-6500 chars Việt cho 6 sections.
"""


def _build_tong_doan_context(person, cdk_chart: dict, cung_summaries: dict, nhap_cot: dict) -> str:
    """Build context cho synthesis: 12 cung tóm tắt + 8 đại hạn + chart."""
    menh_branch = cdk_chart.get("menh_branch")
    nhap_cot_by_star = {item["star"]: item for item in nhap_cot.get("per_star_tong_doan", [])}
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    # Mệnh stars
    menh_stars = []
    for star, b in (cdk_chart.get("stars") or {}).items():
        if b == menh_branch:
            full = NAME_MAP.get(star, star)
            item = nhap_cot_by_star.get(full, {})
            is_hy = menh_branch in (item.get("hy_cung") or [])
            menh_stars.append(f"{star} ({full}, {item.get('category', '?')}, {'hỷ' if is_hy else 'thất vị'})")

    # Tam hợp
    cuc_name = None
    for c, members in TAM_HOP_CUC.items():
        if menh_branch in members:
            cuc_name = c
            tam_hop = members
            break
    else:
        tam_hop = []
    menh_idx = BRANCHES_ORDER.index(menh_branch) if menh_branch in BRANCHES_ORDER else -1
    xung = BRANCHES_ORDER[(menh_idx + 6) % 12] if menh_idx >= 0 else None

    lines = [
        f"╔══════════════════════════════════════════════════════════════╗",
        f"║ TỔNG ĐOÁN CẢ CUỘC ĐỜI — CHIẾU ĐỞM KINH",
        f"╠══════════════════════════════════════════════════════════════╣",
        f"║ Chủ nhân: {person.name}",
        f"║ Sinh: {person.birth_datetime_local}, giới: {person.gender}",
        f"╚══════════════════════════════════════════════════════════════╝",
        "",
        f"━━━ LỚP CƠ (cố định cả đời) ━━━",
        f"  Mệnh CDK: **{menh_branch}**",
        f"  Sao thủ Mệnh: {', '.join(menh_stars) or '(không)'}",
        f"  Tam hợp {cuc_name} cục: {' + '.join(tam_hop) if tam_hop else '?'}",
        f"  Xung chiếu Mệnh: {xung or '?'}",
        "",
        f"━━━ 12 CUNG ĐÃ LUẬN SẴN (lớp CƠ chi tiết) ━━━",
    ]
    for b in BRANCHES_ORDER:
        info = BRANCH_INFO.get(b, {})
        stars_at = [k for k, v in (cdk_chart.get("stars") or {}).items() if v == b]
        is_menh = b == menh_branch
        marker = " ⭐ MỆNH" if is_menh else (" (tam hợp)" if b in tam_hop and not is_menh else (" (xung chiếu)" if b == xung else ""))
        lines.append(f"\n  ▸ {b} ({info.get('conGiap', '?')}){marker}")
        lines.append(f"     Sao đóng: {', '.join(stars_at) or '(không)'}")
        # Compact summary từ cache (~200 chars)
        summary = cung_summaries.get(b, {})
        if summary:
            ban_chat = summary.get("ban_chat_va_quan_he", "")[:300]
            lines.append(f"     Bản chất: {ban_chat}...")

    # Đại Hạn
    lines.append("")
    lines.append(f"━━━ 8 VÒNG ĐẠI HẠN (lớp BIẾN) ━━━")
    dai_han = cdk_chart.get("dai_han_cycles", [])
    for c in dai_han:
        idx = c.get("cycle_index", "?")
        br = c.get("branch", "?")
        s = c.get("start_age", "?")
        e = c.get("end_age", "?")
        info = BRANCH_INFO.get(br, {})
        stars_at_br = [k for k, v in (cdk_chart.get("stars") or {}).items() if v == br]
        lines.append(f"  Vòng {idx} ({s}-{e} tuổi): đại hạn đi qua cung {br} ({info.get('conGiap', '?')}, {info.get('ngu_hanh', '?')}/{info.get('am_duong', '?')})")
        lines.append(f"     Sao tại {br}: {', '.join(stars_at_br) or '(không)'}")

    # Compute current age
    from datetime import datetime
    try:
        born = datetime.fromisoformat(person.birth_datetime_local)
        current_age = datetime.now().year - born.year
        lines.append("")
        lines.append(f"  ⏰ Hiện tại Anh ~{current_age} tuổi → đang trong vòng đại hạn nào? (LLM tự xác định)")
    except Exception:
        pass

    return "\n".join(lines)


def tong_doan_ca_doi(person, force: bool = False) -> dict:
    """Tổng đoán cả cuộc đời — synthesis CƠ (12 cung) + BIẾN (8 đại hạn) bằng DeepSeek V4 Pro.

    Returns {status, tong_doan: {6 sections}, provider, tokens, cost_usd, ...}
    """
    cache_p = _cache_path(person.person_key, person.user_id, "TONG_DOAN_CA_DOI")
    if not force and cache_p.exists():
        try:
            with cache_p.open() as f:
                cached = json.load(f)
            cached["from_cache"] = True
            return cached
        except Exception:
            pass

    try:
        cdk_chart = _cdk_engine_cast(person)
    except Exception as e:
        return {"status": "error", "message": f"CDK cast failed: {e}"}
    nhap_cot = _load_nhap_cot()

    # Load 12 cung from cache (if available)
    cung_summaries = {}
    for b in BRANCHES_ORDER:
        cp = _cache_path(person.person_key, person.user_id, b)
        if cp.exists():
            try:
                with cp.open() as f:
                    cached_b = json.load(f)
                lc = cached_b.get("luan_cung_compact") or {}
                if lc.get("ban_chat_va_quan_he"):
                    cung_summaries[b] = lc
            except Exception:
                pass

    if len(cung_summaries) < 12:
        return {"status": "error", "message": f"Cần luận 12 cung trước. Hiện chỉ có {len(cung_summaries)}/12 cung trong cache. Hãy chạy luan_toan_bo_cung trước."}

    context = _build_tong_doan_context(person, cdk_chart, cung_summaries, nhap_cot)

    user_prompt = f"""{context}

Viết TỔNG ĐOÁN CẢ CUỘC ĐỜI theo schema JSON 6 keys. Văn phong Việt thuần, có ví dụ đời sống.

QUAN TRỌNG:
- Synthesis cả CƠ (12 cung) + BIẾN (8 đại hạn).
- Đừng lặp lại từng cung — anh đã có 12 cung riêng. Hãy NÓI VỀ NHỊP ĐỜI, các giai đoạn lớn.
- Dùng "có xu hướng", "thường", "mỗ niên" — KHÔNG predict cứng.
- Tổng 4500-6500 chars Việt cho 6 sections."""

    from engine.ai.registry import get_registry
    registry = get_registry()
    chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
    candidates = []
    for n in chain:
        try:
            p = registry.get(n)
            if p and p.is_configured and not registry.is_unhealthy(n):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return {"status": "error", "message": "No LLM provider configured"}

    resp = None
    last_err = None
    provider_used = None
    for cand in candidates:
        try:
            resp = cand.chat(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TONG_DOAN},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.55,
                max_tokens=12000,
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
        return {"status": "error", "message": f"All providers failed: {last_err}"}

    content = resp.content if hasattr(resp, "content") else str(resp)
    if "```" in content:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if m:
            content = m.group(1)
        else:
            content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        try:
            start = content.find("{"); end = content.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end + 1])
        except Exception:
            pass
    if parsed is None:
        cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        try:
            start = cleaned.find("{"); end = cleaned.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(cleaned[start:end + 1])
        except Exception:
            parsed = {"tong_quan_cuoc_doi": content, "_parse_error": True}

    prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
    completion_tokens = getattr(resp, "completion_tokens", 0) or 0
    cost = getattr(resp, "cost_usd", 0) or 0

    data = {
        "status": "ok",
        "person_key": person.person_key,
        "person_name": person.name,
        "menh_branch": cdk_chart.get("menh_branch"),
        "generated_at": int(time.time()),
        "provider": provider_used.name,
        "model": "v4_pro_synthesis",
        "cost_usd": round(cost, 6),
        "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
        "tong_doan": parsed,
        "paradigm_note": "Tổng đoán cuộc đời CDK — synthesis CƠ (12 cung) + BIẾN (8 đại hạn) bằng DeepSeek V4 Pro. Iron Rule #6: đọc đồng dạng, không predict.",
    }
    try:
        cache_p.parent.mkdir(parents=True, exist_ok=True)
        with cache_p.open("w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ Cache save failed: {e}")

    # Auto-extract wiki
    try:
        from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
        adapter = {
            "status": "ok",
            "person_name": person.name,
            "person_key": person.person_key,
            "generated_at": data["generated_at"],
            "provider": data["provider"],
            "phe_menh_sau": parsed,
        }
        result = extract_phe_menh_to_wiki(adapter, verbose=False)
        data["wiki_extracted"] = {
            "added_quotes": result.get("added_quotes", 0),
            "added_cach_cuc": result.get("added_cach_cuc", 0),
        }
    except Exception as e:
        data["wiki_extracted"] = {"error": str(e)}

    return data


# ─── ĐẠI HẠN 8 VÒNG (80 năm cuộc đời) ──────────────────────────────────

SYSTEM_PROMPT_DAI_HAN = """Bạn là chuyên gia **Chiếu Đởm Kinh** giảng giải **8 vòng Đại Hạn 10 năm** cho NGƯỜI VIỆT BÌNH THƯỜNG.

🎯 NHIỆM VỤ: Cho 8 vòng đại hạn (mỗi vòng 10 năm, đi qua 1 cung địa chi), luận sâu từng vòng.

⚠️ ĐỐI TƯỢNG ĐỌC: Người Việt không biết Hán-Việt. Văn phong:
- Tiếng Việt thuần hiện đại, gần gũi
- Mỗi thuật ngữ Hán-Việt LẦN ĐẦU giải nghĩa trong ngoặc đơn
- Có ví dụ đời sống cụ thể
- Paradigm Iron Rule #6: ĐỌC ĐỒNG DẠNG, KHÔNG PREDICT CỨNG
- Dùng "có xu hướng", "thường", "mỗ niên" — KHÔNG khẳng định tuyệt đối
- Nhấn mạnh "đối xứng": vòng đại hạn đi qua cung X = vận khí cung X kích hoạt

📋 OUTPUT JSON THUẦN — 1 object với 8 keys "vong_1" → "vong_8":
{
  "vong_1": {
    "tong_quan": "Bản chất 10 năm này, cung đi qua và sao đóng tại đó (~250-400 chars)",
    "co_hoi_thach_thuc": "Cơ hội cụ thể + thử thách phải đối mặt + tương tác với Mệnh (~400-700 chars)",
    "loi_khuyen": "2-3 lời khuyên actionable cho giai đoạn này (~200-350 chars)"
  },
  "vong_2": {...}, ...
  "vong_8": {...}
}

QUY TẮC:
- BẮT ĐẦU `{`, KẾT THÚC `}`. KHÔNG ``` fence.
- Newline trong string dùng \\n. Quote " escape thành \\".
- 8 keys CHÍNH XÁC: vong_1, vong_2, ..., vong_8.
- Mỗi vòng ~900-1400 chars tổng. Tổng 8 vòng ~7500-11000 chars.
"""


def _build_dai_han_context(person, cdk_chart: dict, cung_summaries: dict, nhap_cot: dict) -> str:
    """Build context cho luận 8 vòng đại hạn."""
    menh = cdk_chart.get("menh_branch")
    dai_han = cdk_chart.get("dai_han_cycles", [])
    nhap_cot_by_star = {item["star"]: item for item in nhap_cot.get("per_star_tong_doan", [])}
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    cuc_name = None
    for c, members in TAM_HOP_CUC.items():
        if menh in members:
            cuc_name = c
            tam_hop = members
            break
    else:
        tam_hop = []
    menh_idx = BRANCHES_ORDER.index(menh) if menh in BRANCHES_ORDER else -1
    xung_chieu = BRANCHES_ORDER[(menh_idx + 6) % 12] if menh_idx >= 0 else None

    # Current age
    from datetime import datetime
    try:
        born = datetime.fromisoformat(person.birth_datetime_local)
        current_age = datetime.now().year - born.year
    except Exception:
        current_age = "?"

    lines = [
        f"╔═══════════════════════════════════════════════════════════════╗",
        f"║ LUẬN 8 VÒNG ĐẠI HẠN — CHIẾU ĐỞM KINH",
        f"╠═══════════════════════════════════════════════════════════════╣",
        f"║ Chủ nhân: {person.name}",
        f"║ Sinh: {person.birth_datetime_local} ({person.gender})",
        f"║ Hiện tại: ~{current_age} tuổi",
        f"╚═══════════════════════════════════════════════════════════════╝",
        "",
        f"━━━ THÔNG TIN LÁ SỐ ━━━",
        f"  Mệnh CDK: **{menh}**",
        f"  Tam hợp {cuc_name} cục: {' + '.join(tam_hop) if tam_hop else '?'}",
        f"  Xung chiếu: {xung_chieu}",
        "",
        f"━━━ 8 VÒNG ĐẠI HẠN ━━━",
    ]
    for c in dai_han:
        idx = c.get("cycle_index", "?")
        br = c.get("branch", "?")
        s = c.get("start_age", "?")
        e = c.get("end_age", "?")
        info = BRANCH_INFO.get(br, {})
        # Sao tại branch này
        stars_at_br = [(k, NAME_MAP.get(k, k)) for k, v in (cdk_chart.get("stars") or {}).items() if v == br]
        is_menh = br == menh
        is_xung = br == xung_chieu
        is_tam_hop = br in tam_hop and not is_menh
        flag = " ⭐ (qua cung Mệnh)" if is_menh else (" (xung chiếu Mệnh)" if is_xung else (" (tam hợp với Mệnh)" if is_tam_hop else ""))

        lines.append(f"\n  ▸ Vòng {idx} ({s}-{e} tuổi): qua cung **{br}** ({info.get('conGiap', '?')}, {info.get('ngu_hanh', '?')}/{info.get('am_duong', '?')}){flag}")
        if stars_at_br:
            for short, full in stars_at_br:
                item = nhap_cot_by_star.get(full, {})
                is_hy = br in (item.get("hy_cung") or [])
                cat = item.get("category", "?")
                vd = (item.get("verdict_summary") or "")[:120]
                lines.append(f"      ⭐ {short} ({full}) — {cat}{' — đắc HỶ' if is_hy else ' — thất vị'}: {vd}")
        else:
            lines.append(f"      (không có Phi Tinh đóng tại {br})")
        # Summary từ cache nếu có
        summary = cung_summaries.get(br)
        if summary:
            bc = summary.get("ban_chat_va_quan_he", "")[:200]
            if bc:
                lines.append(f"      📖 Bản chất cung này (đã luận trước): {bc}...")

    if isinstance(current_age, int):
        current_cycle = next((c for c in dai_han if c.get("start_age", 0) <= current_age <= c.get("end_age", 0)), None)
        if current_cycle:
            lines.append(f"\n  ⏰ Hiện tại Anh đang ở **Vòng {current_cycle.get('cycle_index')}** (tuổi {current_cycle.get('start_age')}-{current_cycle.get('end_age')}) — cung {current_cycle.get('branch')}.")

    return "\n".join(lines)


def luan_dai_han_8_vong(person, force: bool = False) -> dict:
    """Luận chi tiết 8 vòng đại hạn — synthesis bằng DeepSeek V4 Pro.

    Returns {status, dai_han: {vong_1, ..., vong_8}, provider, tokens, ...}
    """
    cache_p = _cache_path(person.person_key, person.user_id, "DAI_HAN_8_VONG")
    if not force and cache_p.exists():
        try:
            with cache_p.open() as f:
                cached = json.load(f)
            cached["from_cache"] = True
            return cached
        except Exception:
            pass

    try:
        cdk_chart = _cdk_engine_cast(person)
    except Exception as e:
        return {"status": "error", "message": f"CDK cast failed: {e}"}
    nhap_cot = _load_nhap_cot()

    # Load 12 cung summaries (best context)
    cung_summaries = {}
    for b in BRANCHES_ORDER:
        cp = _cache_path(person.person_key, person.user_id, b)
        if cp.exists():
            try:
                with cp.open() as f:
                    cached_b = json.load(f)
                lc = cached_b.get("luan_cung_compact") or {}
                if lc.get("ban_chat_va_quan_he"):
                    cung_summaries[b] = lc
            except Exception:
                pass

    context = _build_dai_han_context(person, cdk_chart, cung_summaries, nhap_cot)
    user_prompt = f"""{context}

Viết luận chi tiết 8 vòng đại hạn theo schema JSON 8 keys (vong_1 → vong_8).
Mỗi vòng 3 fields: tong_quan + co_hoi_thach_thuc + loi_khuyen.

QUAN TRỌNG:
- Mỗi vòng ~900-1400 chars Việt thuần
- Cụ thể cung đi qua + sao đóng + tương tác Mệnh
- Có ví dụ đời sống thực
- Dùng "mỗ" pattern khi nói tương lai
- KHÔNG predict cứng năm cụ thể"""

    from engine.ai.registry import get_registry
    registry = get_registry()
    chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
    candidates = []
    for n in chain:
        try:
            p = registry.get(n)
            if p and p.is_configured and not registry.is_unhealthy(n):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return {"status": "error", "message": "No LLM provider configured"}

    resp = None
    last_err = None
    provider_used = None
    # Retry up to 3 times
    for attempt in range(3):
        for cand in candidates:
            if registry.is_unhealthy(cand.name):
                continue
            try:
                resp = cand.chat(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_DAI_HAN},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=16000,
                )
                provider_used = cand
                break
            except Exception as e:
                err_str = str(e)
                last_err = f"{cand.name}: {err_str[:200]}"
                if any(sig in err_str for sig in ["401", "403", "1113", "invalid", "Authentication", "balance", "quota"]):
                    registry.mark_unhealthy(cand.name, err_str[:100])
                continue
        if resp is not None:
            break
        import time as _t; _t.sleep(2)
    if resp is None:
        return {"status": "error", "message": f"All providers failed: {last_err}"}

    content = resp.content if hasattr(resp, "content") else str(resp)
    if "```" in content:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if m:
            content = m.group(1)
        else:
            content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        try:
            start = content.find("{"); end = content.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end + 1])
        except Exception:
            pass
    if parsed is None:
        cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        try:
            start = cleaned.find("{"); end = cleaned.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(cleaned[start:end + 1])
        except Exception:
            parsed = {"_parse_error": True, "_raw": content}

    prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
    completion_tokens = getattr(resp, "completion_tokens", 0) or 0
    cost = getattr(resp, "cost_usd", 0) or 0

    data = {
        "status": "ok",
        "person_key": person.person_key,
        "person_name": person.name,
        "menh_branch": cdk_chart.get("menh_branch"),
        "dai_han_cycles": cdk_chart.get("dai_han_cycles", []),
        "generated_at": int(time.time()),
        "provider": provider_used.name,
        "model": "v4_pro_dai_han",
        "cost_usd": round(cost, 6),
        "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
        "dai_han": parsed,
        "paradigm_note": "Luận 8 vòng đại hạn CDK bằng DeepSeek V4 Pro — Iron Rule #6 đọc đồng dạng, không predict.",
    }
    try:
        cache_p.parent.mkdir(parents=True, exist_ok=True)
        with cache_p.open("w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ Cache save failed: {e}")

    # Auto wiki extract
    try:
        from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
        adapter = {
            "status": "ok",
            "person_name": person.name,
            "person_key": person.person_key,
            "generated_at": data["generated_at"],
            "provider": data["provider"],
            "phe_menh_sau": parsed,
        }
        result = extract_phe_menh_to_wiki(adapter, verbose=False)
        data["wiki_extracted"] = {
            "added_quotes": result.get("added_quotes", 0),
            "added_cach_cuc": result.get("added_cach_cuc", 0),
        }
    except Exception as e:
        data["wiki_extracted"] = {"error": str(e)}

    return data


# ─── LƯU NIÊN 10 NĂM ──────────────────────────────────────────────────

SYSTEM_PROMPT_LUU_NIEN = """Bạn là chuyên gia **Chiếu Đởm Kinh** giảng giải **Lưu Niên** (mỗi năm cụ thể) cho NGƯỜI VIỆT BÌNH THƯỜNG.

🎯 NHIỆM VỤ: Cho **10 năm liên tiếp** (mỗi năm có can-chi riêng + lưu Thái Tuế vào cung nào), luận từng năm.

⚠️ ĐỐI TƯỢNG ĐỌC: Người Việt không biết Hán-Việt. Văn phong:
- Tiếng Việt thuần hiện đại, gần gũi
- Mỗi thuật ngữ Hán-Việt LẦN ĐẦU giải nghĩa trong ngoặc
- Có ví dụ đời sống cụ thể, áp dụng cho user (sự nghiệp / sức khỏe / quan hệ)
- Paradigm Iron Rule #6: ĐỌC ĐỒNG DẠNG, KHÔNG predict cứng
- Dùng "có xu hướng", "cần chú ý", "thường" — KHÔNG khẳng định tuyệt đối
- Mỗi năm có TUỔI cụ thể của user — nhắc rõ

📋 OUTPUT JSON THUẦN — 1 object với 10 keys "nam_2026" → "nam_2035" (tùy năm thực):
{
  "nam_<YEAR>": {
    "tong_quan": "Bản chất năm này — can-chi, lưu Thái Tuế cung nào, đại hạn nào (~300-450 chars)",
    "co_hoi_thach_thuc": "Cơ hội cụ thể + thử thách trong năm + tương tác với Mệnh (~400-600 chars)",
    "loi_khuyen": "2-3 lời khuyên actionable cho năm này (~200-300 chars)"
  },
  ...
}

QUY TẮC:
- BẮT ĐẦU `{`, KẾT THÚC `}`. KHÔNG ``` fence.
- Newline trong string dùng \\n. Quote " escape thành \\".
- 10 keys chính xác đúng năm.
- Mỗi năm ~900-1300 chars. Tổng ~9000-13000 chars cho 10 năm.
"""


def _compute_luu_nien_years(person, num_years: int = 10) -> list[dict]:
    """Compute can-chi + lưu Thái Tuế (cung trên lá số) cho N năm tới."""
    from core.chronos import calculate_chronos_state
    from datetime import datetime
    try:
        born = datetime.fromisoformat(person.birth_datetime_local)
        born_year = born.year
    except Exception:
        born_year = 1988
    current_year = datetime.now().year
    years = []
    for offset in range(num_years):
        year = current_year + offset
        try:
            c = calculate_chronos_state(f"{year}-01-01T12:00:00", person.timezone or "Asia/Ho_Chi_Minh")
            parts = c.ganzhi.year.split()
            can = parts[0] if parts else "?"
            chi = parts[1] if len(parts) > 1 else "?"
        except Exception:
            can, chi = "?", "?"
        age = year - born_year
        years.append({
            "year": year,
            "can": can,
            "chi": chi,
            "can_chi": f"{can} {chi}",
            "age": age,
            "luu_thai_tue_branch": chi,  # Thái Tuế = chi năm hiện tại
        })
    return years


def _build_luu_nien_context(person, cdk_chart: dict, years: list[dict], cung_summaries: dict) -> str:
    """Build context cho luận lưu niên."""
    menh = cdk_chart.get("menh_branch")
    dai_han = cdk_chart.get("dai_han_cycles", [])
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    cuc_name = None
    for c, members in TAM_HOP_CUC.items():
        if menh in members:
            cuc_name = c
            tam_hop = members
            break
    else:
        tam_hop = []
    menh_idx = BRANCHES_ORDER.index(menh) if menh in BRANCHES_ORDER else -1
    xung_chieu = BRANCHES_ORDER[(menh_idx + 6) % 12] if menh_idx >= 0 else None

    lines = [
        f"━━━ THÔNG TIN LÁ SỐ ━━━",
        f"  Chủ nhân: {person.name}",
        f"  Sinh: {person.birth_datetime_local}",
        f"  Mệnh CDK: **{menh}** | Tam hợp {cuc_name}: {' + '.join(tam_hop) if tam_hop else '?'} | Xung chiếu: {xung_chieu}",
        "",
        f"━━━ 10 NĂM TỚI ━━━",
    ]
    for y in years:
        chi = y["chi"]
        info = BRANCH_INFO.get(chi, {})
        # Stars at lưu Thái Tuế chi
        stars_at_chi = [(k, NAME_MAP.get(k, k)) for k, v in (cdk_chart.get("stars") or {}).items() if v == chi]
        # Quan hệ với Mệnh
        rel = "MỆNH" if chi == menh else (
            f"tam hợp {cuc_name}" if chi in tam_hop and chi != menh else (
                "xung chiếu Mệnh" if chi == xung_chieu else "phụ trợ")
        )
        # Đại Hạn nào đang ở
        current_dh = next((c for c in dai_han if c.get("start_age", 0) <= y["age"] <= c.get("end_age", 0)), None)
        dh_str = f"Đại Hạn vòng {current_dh.get('cycle_index')} ({current_dh.get('branch')})" if current_dh else "?"
        lines.append(f"\n  ▸ Năm {y['year']} (**{y['can_chi']}**) — tuổi {y['age']}")
        lines.append(f"      Lưu Thái Tuế tại **{chi}** ({info.get('conGiap', '?')}) — quan hệ với Mệnh: {rel}")
        lines.append(f"      {dh_str}")
        if stars_at_chi:
            for short, full in stars_at_chi:
                lines.append(f"      Sao tại {chi}: {short} ({full})")
        else:
            lines.append(f"      Không có Phi Tinh đóng tại {chi}")
    return "\n".join(lines)


def luan_luu_nien_10_nam(person, num_years: int = 10, force: bool = False) -> dict:
    """Luận Lưu Niên 10 năm tới — 1 LLM call."""
    cache_key = f"LUU_NIEN_{num_years}_NAM"
    cache_p = _cache_path(person.person_key, person.user_id, cache_key)
    if not force and cache_p.exists():
        try:
            with cache_p.open() as f:
                cached = json.load(f)
            cached["from_cache"] = True
            return cached
        except Exception:
            pass

    try:
        cdk_chart = _cdk_engine_cast(person)
    except Exception as e:
        return {"status": "error", "message": f"CDK cast failed: {e}"}

    years = _compute_luu_nien_years(person, num_years)
    if not years:
        return {"status": "error", "message": "Cannot compute years"}

    # Load 12 cung summaries (compact context)
    cung_summaries = {}
    for b in BRANCHES_ORDER:
        cp = _cache_path(person.person_key, person.user_id, b)
        if cp.exists():
            try:
                with cp.open() as f:
                    cached_b = json.load(f)
                lc = cached_b.get("luan_cung_compact") or {}
                if lc.get("ban_chat_va_quan_he"):
                    cung_summaries[b] = lc
            except Exception:
                pass

    context = _build_luu_nien_context(person, cdk_chart, years, cung_summaries)
    year_keys = [f"nam_{y['year']}" for y in years]
    schema_lines = ",\n  ".join(f'"{k}": {{"tong_quan": "...", "co_hoi_thach_thuc": "...", "loi_khuyen": "..."}}' for k in year_keys)

    user_prompt = f"""{context}

Viết luận giải 10 năm liên tiếp theo schema JSON với {len(year_keys)} keys CHÍNH XÁC:
{{
  {schema_lines}
}}

QUAN TRỌNG:
- Mỗi năm 3 fields: tong_quan + co_hoi_thach_thuc + loi_khuyen
- Mỗi năm ~900-1300 chars Việt thuần
- Cụ thể: nhắc rõ tuổi user trong năm đó, can-chi năm, lưu Thái Tuế cung nào
- Dùng "có xu hướng", "cần chú ý" — KHÔNG predict cứng tháng/sự kiện
- Liên kết với Đại Hạn đang ở (kết hợp lớp BIẾN)"""

    from engine.ai.registry import get_registry
    registry = get_registry()
    chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
    candidates = []
    for n in chain:
        try:
            p = registry.get(n)
            if p and p.is_configured and not registry.is_unhealthy(n):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return {"status": "error", "message": "No LLM provider configured"}

    resp = None
    last_err = None
    provider_used = None
    for attempt in range(3):
        for cand in candidates:
            if registry.is_unhealthy(cand.name):
                continue
            try:
                resp = cand.chat(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_LUU_NIEN},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=16000,
                )
                provider_used = cand
                break
            except Exception as e:
                err_str = str(e)
                last_err = f"{cand.name}: {err_str[:200]}"
                if any(sig in err_str for sig in ["401", "403", "1113", "invalid", "Authentication", "balance", "quota"]):
                    registry.mark_unhealthy(cand.name, err_str[:100])
                continue
        if resp is not None:
            break
        import time as _t; _t.sleep(2)
    if resp is None:
        return {"status": "error", "message": f"All providers failed: {last_err}"}

    content = resp.content if hasattr(resp, "content") else str(resp)
    if "```" in content:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if m:
            content = m.group(1)
        else:
            content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        try:
            start = content.find("{"); end = content.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end + 1])
        except Exception:
            pass
    if parsed is None:
        cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
        try:
            start = cleaned.find("{"); end = cleaned.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(cleaned[start:end + 1])
        except Exception:
            parsed = {"_parse_error": True, "_raw": content}

    prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
    completion_tokens = getattr(resp, "completion_tokens", 0) or 0
    cost = getattr(resp, "cost_usd", 0) or 0

    data = {
        "status": "ok",
        "person_key": person.person_key,
        "person_name": person.name,
        "menh_branch": cdk_chart.get("menh_branch"),
        "years": years,  # raw years meta
        "generated_at": int(time.time()),
        "provider": provider_used.name,
        "model": "v4_pro_luu_nien",
        "cost_usd": round(cost, 6),
        "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
        "luu_nien": parsed,
        "num_years": num_years,
        "paradigm_note": "Lưu Niên 10 năm CDK — Iron Rule #6 đọc đồng dạng, không predict cứng.",
    }
    try:
        cache_p.parent.mkdir(parents=True, exist_ok=True)
        with cache_p.open("w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ Cache save failed: {e}")

    # Auto wiki extract
    try:
        from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
        adapter = {
            "status": "ok",
            "person_name": person.name,
            "person_key": person.person_key,
            "generated_at": data["generated_at"],
            "provider": data["provider"],
            "phe_menh_sau": parsed,
        }
        result = extract_phe_menh_to_wiki(adapter, verbose=False)
        data["wiki_extracted"] = {
            "added_quotes": result.get("added_quotes", 0),
            "added_cach_cuc": result.get("added_cach_cuc", 0),
        }
    except Exception as e:
        data["wiki_extracted"] = {"error": str(e)}

    return data
