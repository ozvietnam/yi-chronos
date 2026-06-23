"""Sage Agents — each represents one cosmology school.

An agent:
1. Has an `id` (e.g. "tu_vi") + display name.
2. Loads its Persona prompt via prompt_store (default or user override).
3. Knows which chart data it operates on (chart_data key path).
4. Calls an LLM provider with `{persona system prompt + user question + chart data}`.
5. Returns a structured `AgentResponse`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from .prompt_store import AGENT_IDS, AGENT_METADATA, get_prompt
from .providers import LLMProvider, ProviderError


@dataclass(frozen=True)
class AgentResponse:
    """One agent's contribution to the council."""

    agent_id: str
    agent_name_vi: str
    provider: str
    model: str
    content: str          # markdown answer
    error: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def _stringify_chart(chart_data: dict) -> str:
    """Pretty-format chart data for the agent's user message.

    Trims very large fields (like full 12-cycle Đại Vận with details) to keep
    prompt size manageable.
    """
    if not chart_data:
        return "(không có dữ liệu chart)"
    try:
        return json.dumps(chart_data, ensure_ascii=False, indent=2)[:6000]
    except Exception:
        return str(chart_data)[:6000]


def _user_message_for_agent(
    *,
    question: str,
    chart_data: dict,
    round_label: str | None = None,
    challenges: str | None = None,
    expert_context: str | None = None,
) -> str:
    """Compose the user-role message for one agent."""
    parts = []
    if round_label:
        parts.append(f"## VÒNG {round_label}")
    parts.append("## CÂU HỎI CỦA USER\n" + (question or "(không có câu hỏi cụ thể, hãy đưa nhận định tổng quan)"))
    parts.append("## DỮ LIỆU CHART TỪ ENGINE\n```json\n" + _stringify_chart(chart_data) + "\n```")
    if expert_context:
        parts.append(expert_context)
    if challenges:
        parts.append("## CÂU HỎI CHẤT VẤN TỪ TRỌNG TÀI\n" + challenges)
        parts.append(
            "Hãy phản hồi cụ thể vào câu hỏi chất vấn, hoặc bảo vệ quan điểm "
            "ban đầu nếu thấy đúng. Không sáo ngữ."
        )
    elif expert_context:
        parts.append(
            "Hãy đưa nhận định theo format đã định trong Persona — bám dữ liệu chart VÀ "
            "DẪN cụ thể tri thức sâu từ sách ở trên (tên cách/sao/nguyên lý + trích), "
            "không bịa, không nói chung chung."
        )
    else:
        parts.append(
            "Hãy đưa nhận định theo format đã định trong Persona — "
            "ngắn gọn, dựa CHỈ trên dữ liệu chart đã cho, không bịa."
        )
    return "\n\n".join(parts)


def run_agent(
    *,
    agent_id: str,
    provider: LLMProvider,
    model: str | None,
    question: str,
    chart_data: dict,
    round_label: str | None = None,
    challenges: str | None = None,
    max_tokens: int = 1200,
    temperature: float = 0.6,
) -> AgentResponse:
    """Execute one agent → return AgentResponse."""
    if agent_id not in AGENT_IDS:
        raise ValueError(f"Unknown agent_id: {agent_id!r}")

    persona = get_prompt(agent_id)
    # RAG grounding: vòng đầu (chưa có chất vấn) → bơm tri thức sâu trích sách cho sage
    # luận như chuyên gia, dẫn cụ thể. Best-effort, không chặn nếu lỗi/thiếu DB.
    expert_ctx = ""
    if not challenges:
        try:
            from .expert_context import build_expert_context
            expert_ctx = build_expert_context(question, agent_id)
        except Exception:
            expert_ctx = ""
    user_msg = _user_message_for_agent(
        question=question,
        chart_data=chart_data,
        round_label=round_label,
        challenges=challenges,
        expert_context=expert_ctx,
    )

    meta = AGENT_METADATA[agent_id]
    try:
        resp = provider.chat(
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_msg},
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return AgentResponse(
            agent_id=agent_id,
            agent_name_vi=meta["name_vi"],
            provider=resp.provider,
            model=resp.model,
            content=resp.content,
            prompt_tokens=resp.prompt_tokens,
            completion_tokens=resp.completion_tokens,
            total_tokens=resp.total_tokens,
        )
    except ProviderError as e:
        # Mark unhealthy + retry with mock so user sees output instead of empty.
        from .registry import get_registry

        reg = get_registry()
        reg.mark_unhealthy(provider.name, str(e))
        original_error = f"{provider.name}: {e}"

        # Retry with Mock so the council flow doesn't break.
        if provider.name != "mock":
            try:
                mock = reg.get("mock")
                resp = mock.chat(
                    messages=[
                        {"role": "system", "content": persona},
                        {"role": "user", "content": user_msg},
                    ],
                    model="mock-v1",
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return AgentResponse(
                    agent_id=agent_id,
                    agent_name_vi=meta["name_vi"],
                    provider="mock",
                    model="mock-v1",
                    content=resp.content,
                    error=f"Fell back to Mock ({original_error})",
                    prompt_tokens=resp.prompt_tokens,
                    completion_tokens=resp.completion_tokens,
                    total_tokens=resp.total_tokens,
                )
            except Exception:
                pass

        return AgentResponse(
            agent_id=agent_id,
            agent_name_vi=meta["name_vi"],
            provider=provider.name,
            model=model or provider.default_model,
            content="",
            error=original_error,
        )
