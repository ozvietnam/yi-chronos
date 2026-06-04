"""Embedding helper for wiki vector retrieval (#18 Phase 2).

Default embedder = LM Studio (OpenAI-compatible, local) running nomic-embed-text.
Query-time degrades safely: hosts without an embedder (e.g. the prod VPS) simply
skip vector search and use FTS5. Same model MUST be used for offline corpus
embedding and query-time, so both go through here.

Config via env:
  YI_EMBED_BASE_URL  (default http://localhost:1234/v1 — LM Studio)
  YI_EMBED_MODEL     (default text-embedding-nomic-embed-text-v1.5)
"""
from __future__ import annotations

import json
import os
import urllib.request

EMBED_BASE_URL = os.environ.get("YI_EMBED_BASE_URL", "http://localhost:1234/v1").rstrip("/")
EMBED_MODEL = os.environ.get("YI_EMBED_MODEL", "text-embedding-nomic-embed-text-v1.5")
EMBED_DIM = int(os.environ.get("YI_EMBED_DIM", "768"))


def embed_texts(texts: list[str], timeout: float = 60.0) -> list[list[float]] | None:
    """Embed a batch of texts. Returns vectors, or None if the embedder is
    unreachable (caller falls back to FTS5)."""
    texts = [t for t in (texts or []) if t and t.strip()]
    if not texts:
        return []
    body = json.dumps({"model": EMBED_MODEL, "input": texts}).encode("utf-8")
    req = urllib.request.Request(
        f"{EMBED_BASE_URL}/embeddings",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        # OpenAI-compatible: {"data": [{"embedding": [...]}, ...]} preserving order
        return [row["embedding"] for row in data["data"]]
    except Exception:
        return None


def embed_one(text: str, timeout: float = 30.0) -> list[float] | None:
    vecs = embed_texts([text], timeout=timeout)
    return vecs[0] if vecs else None


def is_available() -> bool:
    """True if an embedder responds (used to decide vector vs FTS5-only)."""
    return embed_one("ping", timeout=5.0) is not None
