"""yi_translation — Hán hiện đại → Việt cho corpus phục chế.

Primary: DeepSeek-chat (quality ⭐⭐⭐⭐⭐, ~$0.003/page).
Fallback: Ollama qwen2.5-coder:14b (local, free).

Decision log: docs/design/SPIKE-TRANSLATION-2026-05-17.md
"""
from .zh_to_vi import (
    translate_chunk,
    translate_page,
    translate_corpus,
    TRANSLATION_GLOSSARY,
)

__all__ = [
    "translate_chunk",
    "translate_page",
    "translate_corpus",
    "TRANSLATION_GLOSSARY",
]
