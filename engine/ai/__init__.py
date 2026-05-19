"""Hội Đồng Tư Vấn Trí Tuệ (Sages Council) — multi-agent AI for cosmology interpretation.

Architecture:
- Providers: abstract LLM backends (ZAI / DeepSeek / Anthropic / Mock)
- Registry: runtime key management; UI can swap keys without restart
- Agents: one per cosmology school, each with editable Persona prompt
- Orchestrator (Trọng tài, default Claude Opus): chooses agents + runs 3-round debate
- Storage: SQLite for prompt overrides + debate logs

Reference: docs/sages-council-architecture.md (this session's design)
"""

from .registry import ProviderRegistry, get_registry

__all__ = ["ProviderRegistry", "get_registry"]
