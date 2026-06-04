"""AI Chat — Q&A với context lá số Bát Tự.

User hỏi câu về lá số → LLM trả lời với context = tất cả luận giải engines đã chạy.

Paradigm (Iron Rule #4+6): System prompt CỨNG paradigm guard — LLM phải reply
theo tone "đọc đồng dạng", KHÔNG predict. Không cho phép LLM "bịa" số mệnh.

Architecture:
1. Cast Bát Tự + run all luận giải engines
2. Compose dense context (compressed JSON / structured text) — fit LLM context window
3. System prompt với paradigm guard + context
4. User message + history → LLM
5. Return response + tokens
"""

from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT_TEMPLATE = """Anh là một trợ lý am hiểu **Bát Tự / Tử Bình** + **Bát Tự Hà Lạc** (paradigm Đông phương).

NGUYÊN TẮC CỐT YẾU (KHÔNG VI PHẠM):
1. Tử Bình KHÔNG dự đoán "sẽ giàu" / "sẽ thành công" / "sẽ ốm năm X".
2. Tử Bình phản chiếu cấu trúc khí bẩm sinh + lưu biến → giúp người TRI MỆNH → cân bằng (Bổ).
3. Mệnh cố kết, Vận lưu biến. Quan hệ là dòng chảy có ý thức, không định sẵn.
4. Khi user hỏi "sẽ giàu khi nào" hay "có ly hôn không" — TRẢ LỜI: "Tôi không dự đoán kết quả. Tôi đọc cấu hình khí + xu hướng. Quyết định là của Anh."
5. Trả lời ngắn gọn (2-4 đoạn), tone trầm tĩnh, paradigm-aligned.
6. Khi có cảnh báo (warning patterns) — nêu actionable hóa giải, KHÔNG gây lo sợ.
7. Source: Thiệu Vĩ Hoa, Trần Viên (Tử Bình), Học Năng (Hà Lạc).

CONTEXT LÁ SỐ CỦA USER (data dày — chỉ cite khi liên quan câu hỏi):

{LASO_CONTEXT}

Hướng dẫn trả lời:
- Trước tiên xác định câu hỏi user thuộc domain nào (Tài/Quan/Hôn nhân/Sức khỏe/...).
- Lấy relevant data từ context, KHÔNG kể toàn bộ.
- Trả lời cô đọng, có cite source khi cần (vd "theo Thiệu Vĩ Hoa Chương 3...").
- Kết bằng 1 câu paradigm: "Tri mệnh để chọn cách đi, không để biết kết quả."
"""


def _compose_laso_context(bat_tu_state: dict, luan: dict | None = None,
                          ha_lac_luan: dict | None = None) -> str:
    """Compose compact lá số context for LLM.

    Format: short structured key-value text. Cắt bớt verbose narrative,
    giữ structured data (Tứ Trụ, Cách Cục, Dụng Thần, ...).
    """
    pillars = bat_tu_state["tu_tru"]["pillars"]
    dm = bat_tu_state["tu_tru"]["day_master"]
    cc = bat_tu_state.get("cach_cuc", {})
    dt = bat_tu_state.get("dung_than", {})
    ngu_hanh = bat_tu_state["ngu_hanh"]
    dm_assess = ngu_hanh["day_master_assessment"]

    ctx_parts = []
    # 1. Tứ Trụ
    ctx_parts.append(
        f"TỨ TRỤ: {pillars['year']['stem']} {pillars['year']['branch']} / "
        f"{pillars['month']['stem']} {pillars['month']['branch']} / "
        f"{pillars['day']['stem']} {pillars['day']['branch']} / "
        f"{pillars['hour']['stem']} {pillars['hour']['branch']}"
    )
    ctx_parts.append(
        f"NHẬT CHỦ: {dm['stem']} ({dm['element']}), "
        f"cường độ = {dm_assess['strength_tag']} "
        f"(label: {dm_assess['strength_label']}, "
        f"support={dm_assess.get('support_score', 0)}, drain={dm_assess.get('drain_score', 0)})"
    )

    # 2. Ngũ hành counts
    ctx_parts.append(f"NGŨ HÀNH counts: {ngu_hanh['counts']}")

    # 3. Cách Cục
    if cc:
        ctx_parts.append(f"CÁCH CỤC: {cc.get('cach_name', '')} — {cc.get('polarity', '')}")
        ctx_parts.append(f"  essence: {cc.get('essence', '')}")
        ctx_parts.append(f"  hợp: {cc.get('favorable', '')}")
        ctx_parts.append(f"  kỵ: {cc.get('ky', '')}")

    # 4. Extreme pattern (nếu có)
    ext = bat_tu_state.get("extreme_pattern")
    if ext:
        ctx_parts.append(f"EXTREME PATTERN: {ext['name']} — {ext['essence'][:200]}")
        ctx_parts.append(
            f"  → Dụng/Hỷ/Kỵ Thần OVERRIDE: "
            f"{ext['dung_than_element']}/{ext['hy_than_element']}/{ext['ky_than_element']}"
        )
    else:
        # 5. Dụng/Hỷ/Kỵ Thần (only normal cases)
        ctx_parts.append(
            f"DỤNG THẦN: {dt.get('dung_than_element', '')} "
            f"(role: {dt.get('dung_than_role_vi', '')})"
        )
        ctx_parts.append(f"HỶ THẦN: {dt.get('hy_than_element', '')}")
        ctx_parts.append(f"KỴ THẦN: {dt.get('ky_than_element', '')}")

    # 6. Đại Vận current
    if luan and luan.get("dai_van_current") and luan["dai_van_current"].get("current_cycle"):
        c = luan["dai_van_current"]["current_cycle"]
        ctx_parts.append(
            f"ĐẠI VẬN HIỆN TẠI: {c['stem']} {c['branch']} "
            f"(tuổi {c['start_age']}-{c['end_age']}) — "
            f"{luan['dai_van_current']['narrative'][:120]}"
        )

    # 7. Favorable + warnings (nếu có)
    if luan:
        if luan.get("favorable_combinations"):
            fc_names = [f["name"] for f in luan["favorable_combinations"]]
            ctx_parts.append(f"FAVORABLE PATTERNS: {fc_names}")
        if luan.get("warnings"):
            w_names = [w["name"] for w in luan["warnings"]]
            ctx_parts.append(f"WARNINGS: {w_names}")

    # 8. Thần sát top 3
    than_sat = bat_tu_state.get("than_sat", [])
    if than_sat:
        ts_names = [s.get("name") for s in than_sat[:5]]
        ctx_parts.append(f"THẦN SÁT: {ts_names}")

    # 9. Hà Lạc summary
    if ha_lac_luan:
        t = ha_lac_luan["tien_thien_luan"]
        h = ha_lac_luan["hau_thien_luan"]
        ctx_parts.append(
            f"HÀ LẠC: Tiên thiên={t['name_vi']} (quẻ {t['king_wen']}), "
            f"Hậu thiên={h['name_vi']} (quẻ {h['king_wen']}) — "
            f"comparison: {ha_lac_luan['comparison']['pattern']}"
        )
        if ha_lac_luan["trajectory_luan"].get("current"):
            cur = ha_lac_luan["trajectory_luan"]["current"]
            ctx_parts.append(
                f"  Tuổi hiện tại → giai đoạn {cur['stage_index']}/12 "
                f"({cur['hexagram']} hào {cur['line_position']}, {cur['polarity']})"
            )

    # 10. RAG — trích nguyên văn từ kho sách phục chế (FTS5, #18). Nối "corpus
    # chết" passages vào luận giải: grounding để LLM cite thư tịch, KHÔNG bịa.
    try:
        from engine.yi_wiki.store import get_store

        terms = [t for t in (
            cc.get("cach_name", ""),
            dm.get("element", ""),
            dt.get("dung_than_element", ""),
        ) if t]
        query = " ".join(terms)
        passages = get_store().search_passages(query, limit=2) if query.strip() else []
        if passages:
            ctx_parts.append(
                "TRÍCH NGUYÊN VĂN THƯ TỊCH (tham khảo — cite khi liên quan, KHÔNG bịa thêm):"
            )
            for p in passages:
                excerpt = " ".join((p.get("raw_text") or "").split())[:350]
                ctx_parts.append(
                    f"  • [{p.get('corpus_id', '')} tr.{p.get('page_start', '')}] {excerpt}"
                )
    except Exception:
        pass  # corpus là tùy chọn — chat vẫn chạy nếu wiki DB không có

    return "\n".join(ctx_parts)


METHOD_ID = "bat_tu_ai_chat_v1"


def chat_about_chart(
    bat_tu_state: dict,
    user_question: str,
    *,
    history: list[dict] | None = None,
    luan_giai: dict | None = None,
    ha_lac_luan: dict | None = None,
    provider_preferred: list[str] | None = None,
    max_tokens: int = 800,
) -> dict:
    """User Q&A about their Bát Tự chart.

    Args:
        bat_tu_state: Output of cast_bat_tu()
        user_question: User's natural language question
        history: Optional list of prior {role, content} messages
        luan_giai: Optional output of compose_luan_giai() — provides richer context
        ha_lac_luan: Optional Hà Lạc luận giải
        provider_preferred: Order to try providers (default: mock + cheap)
        max_tokens: Response length cap

    Returns:
        Dict with response + provider info + tokens.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")
    if not user_question or not user_question.strip():
        raise ValueError("user_question is empty")

    # Compose context
    laso_ctx = _compose_laso_context(bat_tu_state, luan_giai, ha_lac_luan)
    system_msg = SYSTEM_PROMPT_TEMPLATE.format(LASO_CONTEXT=laso_ctx)

    # Build messages
    messages = [{"role": "system", "content": system_msg}]
    if history:
        for h in history[-6:]:  # keep last 6 turns
            if h.get("role") in {"user", "assistant"} and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_question})

    # Pick provider — prefer free/cheap first
    from engine.ai.registry import get_registry
    registry = get_registry()
    if provider_preferred is None:
        provider_preferred = ["ollama", "openrouter", "gemini", "zai", "deepseek",
                              "minimax", "anthropic", "mock"]
    provider = registry.first_configured(provider_preferred)

    try:
        response = provider.chat(
            messages=messages,
            temperature=0.4,  # paradigm-strict tone — low temp
            max_tokens=max_tokens,
        )
        return {
            "method_id": METHOD_ID,
            "question": user_question,
            "answer": response.content,
            "provider": response.provider,
            "model": response.model,
            "tokens": {
                "prompt": response.prompt_tokens,
                "completion": response.completion_tokens,
                "total": response.total_tokens,
            },
            "context_size": len(laso_ctx),
        }
    except Exception as e:
        # Mark provider unhealthy, fallback to mock
        registry.mark_unhealthy(provider.name, str(e))
        mock = registry._providers.get("mock")
        if mock:
            response = mock.chat(messages=messages, max_tokens=max_tokens)
            return {
                "method_id": METHOD_ID,
                "question": user_question,
                "answer": response.content,
                "provider": "mock (fallback)",
                "model": response.model,
                "tokens": {
                    "prompt": response.prompt_tokens,
                    "completion": response.completion_tokens,
                    "total": response.total_tokens,
                },
                "context_size": len(laso_ctx),
                "fallback_reason": str(e),
            }
        raise
