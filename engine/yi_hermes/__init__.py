"""YI-Hermes — concierge agent embedded in YI-CHRONOS.

NOT to be confused with the user's existing Hermes service on their Mac
(separate namespace, separate DB, separate process).

Role:
- Tiếp khách (concierge multi-turn chat)
- Tạo profile (conversational onboarding)
- Hiểu các module nội tại (module librarian via introspection)
- Phát triển từ điển tiếng Việt (glossary builder)
- Skill generator + blind-spot detector (Phase 3)

Public API: see api/main.py /api/yi-hermes/*
"""

from .chat import HermesChat, HermesContext
from .context import (
    assemble_system_context,
    context_summary,
    get_founder_profile,
    get_founder_soul_keys,
    get_manifest,
    is_founder,
    reload_files as reload_context_files,
    update_founder_profile,
    update_manifest,
)
from .glossary import (
    GlossaryStore,
    GlossaryTerm,
    get_glossary_store,
)
from .librarian import (
    ModuleLibrarian,
    ModuleSummary,
    get_librarian,
)
from .memory import (
    CATEGORIES,
    ChatSummary,
    UserFact,
    add_fact,
    add_summary,
    build_memory_context,
    delete_fact,
    fact_categories_summary,
    list_facts,
    list_summaries,
    log_glossary_view,
    search_summaries,
    session_signals_from_turns,
    top_viewed_terms,
)
from .soul import (
    DEFAULT_SOUL,
    SoulProfile,
    evolve_soul,
    get_soul,
    reset_soul,
    save_soul,
    update_soul,
)


__all__ = [
    "CATEGORIES",
    "ChatSummary",
    "DEFAULT_SOUL",
    "GlossaryStore",
    "GlossaryTerm",
    "HermesChat",
    "HermesContext",
    "ModuleLibrarian",
    "ModuleSummary",
    "SoulProfile",
    "UserFact",
    "add_fact",
    "add_summary",
    "assemble_system_context",
    "build_memory_context",
    "context_summary",
    "delete_fact",
    "evolve_soul",
    "fact_categories_summary",
    "get_founder_profile",
    "get_founder_soul_keys",
    "get_manifest",
    "is_founder",
    "reload_context_files",
    "update_founder_profile",
    "update_manifest",
    "get_glossary_store",
    "get_librarian",
    "get_soul",
    "list_facts",
    "list_summaries",
    "log_glossary_view",
    "reset_soul",
    "save_soul",
    "search_summaries",
    "session_signals_from_turns",
    "top_viewed_terms",
    "update_soul",
]
