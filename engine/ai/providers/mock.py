"""Mock LLM provider — deterministic, for tests + no-key dev mode.

When the user has NO real LLM keys configured, the council falls back to Mock
so the workflow can still be inspected end-to-end. Mock responses are
canned-but-realistic Vietnamese readings based on simple chart inspection.
"""

from __future__ import annotations

import hashlib

from .base import LLMProvider, LLMResponse


class MockProvider(LLMProvider):
    """Deterministic placeholder. Returns canned Vietnamese readings."""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def display_name(self) -> str:
        return "Mock (deterministic, no API key)"

    @property
    def default_model(self) -> str:
        return "mock-v1"

    @property
    def available_models(self) -> list[str]:
        return ["mock-v1"]

    @property
    def is_configured(self) -> bool:
        return True

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        # Inspect the last user message to determine if this is an agent call
        # or an orchestrator call, then return a canned response.
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        system = next(
            (m["content"] for m in messages if m["role"] == "system"),
            "",
        )

        digest = hashlib.sha1((system + last_user).encode("utf-8")).hexdigest()[:8]

        # Heuristic: if system prompt mentions "Trọng tài", give orchestrator format.
        if "Trọng tài" in system or "orchestrator" in system.lower() or "chủ tọa" in system.lower():
            content = self._mock_orchestrator(last_user, digest)
        else:
            content = self._mock_agent(system, last_user, digest)

        return LLMResponse(
            content=content,
            provider=self.name,
            model="mock-v1",
            prompt_tokens=sum(len(m["content"]) for m in messages) // 4,
            completion_tokens=len(content) // 4,
            total_tokens=0,
            raw={"mock_digest": digest},
        )

    def _mock_agent(self, system: str, user: str, digest: str) -> str:
        # Pull agent school name from system prompt (e.g. "Agent Tử Vi")
        school = "Đông"
        for s in ("Tử Vi", "Bát Tự", "Hà Lạc", "Liên Hoa", "Lục Hào",
                  "Mai Hoa", "Chiêm tinh Tây"):
            if s in system:
                school = s
                break
        return (
            f"[MOCK • Agent {school} • #{digest}]\n\n"
            "**Nhận định**: Lá số có tín hiệu hỗn hợp — vài cung thuận, vài cung "
            "cần cẩn trọng. (Đây là mock response — paste API key thật vào để có "
            "phân tích thực.)\n\n"
            "**Bằng chứng từ chart**:\n"
            "- Tín hiệu 1 (mock)\n"
            "- Tín hiệu 2 (mock)\n\n"
            "**Khuyến nghị**:\n"
            "- Hành động cụ thể (mock)\n"
            "- Tránh điều này (mock)\n\n"
            "*(Mock provider — không có giá trị thực, chỉ minh họa data flow.)*"
        )

    def _mock_orchestrator(self, user: str, digest: str) -> str:
        return (
            f"[MOCK • Trọng tài • #{digest}]\n\n"
            "## Tổng hợp\n"
            "Các agent đã đưa ra nhận định độc lập về câu hỏi của anh. "
            "Có 2 điểm đồng thuận và 1 điểm cần làm rõ thêm.\n\n"
            "## Đồng thuận\n"
            "- Điểm A (mock)\n"
            "- Điểm B (mock)\n\n"
            "## Mâu thuẫn cần phân định\n"
            "- Đông cho rằng X, Tây cho rằng Y — cần xem xét hoàn cảnh cụ thể.\n\n"
            "## Actionable Insights\n"
            "- **Nên làm**: hành động cụ thể (mock)\n"
            "- **Tránh**: điều cần tránh (mock)\n"
            "- **Thời điểm**: gợi ý timing (mock)\n\n"
            "*(Mock provider — paste Claude key vào để có Trọng tài thực.)*"
        )
