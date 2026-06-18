"""Provider Registry — singleton holding all LLM provider instances.

UI can:
- List providers + their status (configured? available models?)
- Set API key at runtime (POST /api/ai/providers/:name/key)
- Set notes / plan_type per provider (POST /api/ai/providers/:name/notes)
- Pick which provider drives which agent (POST /api/ai/agents/:id/provider)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock

from .providers import (
    AnthropicProvider,
    DeepSeekProvider,
    GeminiProvider,
    LLMProvider,
    LMStudioProvider,
    MiniMaxProvider,
    MockProvider,
    OllamaProvider,
    OpenRouterProvider,
    ZaiProvider,
)


def _load_env_local() -> None:
    """Best-effort load of .env.local into os.environ."""
    try:
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".env.local",
        )
        if not os.path.exists(env_path):
            return
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# Notes file — persists across restarts (NOT API keys, those stay in env vars)
_NOTES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ai_provider_notes.json"
# Keys file — gitignored, chmod 600. Persist API keys across server restarts so
# anh không phải re-paste mỗi lần.
_KEYS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ai_keys.json"


class ProviderRegistry:
    """Holds LLM provider instances. Thread-safe key updates."""

    def __init__(self):
        _load_env_local()
        self._providers: dict[str, LLMProvider] = {
            "zai":         ZaiProvider(),
            "deepseek":    DeepSeekProvider(),
            "anthropic":   AnthropicProvider(),
            "minimax":     MiniMaxProvider(),
            "gemini":      GeminiProvider(),
            "openrouter":  OpenRouterProvider(),
            "ollama":      OllamaProvider(),
            "lmstudio":    LMStudioProvider(),
            "mock":        MockProvider(),
        }
        self._lock = Lock()
        self._unhealthy: set[str] = set()
        self._unhealthy_reasons: dict[str, str] = {}
        self._notes: dict[str, dict] = self._load_notes()
        # Load persisted keys & inject into providers
        self._load_persisted_keys()

    # ─── Provider notes (persists) ──────────────────────────────────────

    def _load_notes(self) -> dict:
        try:
            if _NOTES_PATH.exists():
                return json.loads(_NOTES_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _save_notes(self) -> None:
        try:
            _NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
            _NOTES_PATH.write_text(
                json.dumps(self._notes, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ─── Key persistence (gitignored data/ai_keys.json) ─────────────────

    def _load_persisted_keys(self) -> None:
        """Load saved API keys from disk → inject into provider instances."""
        try:
            if _KEYS_PATH.exists():
                keys = json.loads(_KEYS_PATH.read_text(encoding="utf-8"))
                for name, key in keys.items():
                    if name in self._providers and key:
                        try:
                            self._providers[name].set_api_key(key)
                        except Exception:
                            pass
        except Exception:
            pass

    def _save_persisted_keys(self, name: str, key: str) -> None:
        """Persist key to disk (chmod 600). Wipes if key is empty."""
        try:
            _KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
            existing: dict = {}
            if _KEYS_PATH.exists():
                try:
                    existing = json.loads(_KEYS_PATH.read_text(encoding="utf-8"))
                except Exception:
                    existing = {}
            if key:
                existing[name] = key
            else:
                existing.pop(name, None)
            _KEYS_PATH.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            try:
                _KEYS_PATH.chmod(0o600)
            except Exception:
                pass
        except Exception:
            pass

    def get_notes(self, name: str) -> dict:
        return self._notes.get(name, {"plan_type": None, "notes": None})

    def set_notes(self, name: str, *, plan_type: str | None = None,
                  notes: str | None = None) -> dict:
        """Update notes/plan_type for a provider. Persists to disk."""
        with self._lock:
            if name not in self._providers:
                raise KeyError(f"Unknown provider: {name!r}")
            current = self._notes.get(name, {})
            if plan_type is not None:
                current["plan_type"] = plan_type
            if notes is not None:
                current["notes"] = notes
            self._notes[name] = current
            self._save_notes()
            return current

    def list_providers(self) -> list[dict]:
        out = []
        for p in self._providers.values():
            entry = p.status()
            # Merge notes + plan_type
            n = self.get_notes(entry["name"])
            entry["plan_type"] = n.get("plan_type")
            entry["notes"] = n.get("notes")
            entry["is_unhealthy"] = self.is_unhealthy(entry["name"])
            entry["unhealthy_reason"] = self._unhealthy_reasons.get(entry["name"])
            out.append(entry)
        return out

    def get(self, name: str) -> LLMProvider:
        if name not in self._providers:
            raise KeyError(f"Unknown provider: {name!r}")
        return self._providers[name]

    def set_api_key(self, name: str, key: str) -> dict:
        with self._lock:
            p = self.get(name)
            p.set_api_key(key)
            # Persist to data/ai_keys.json (gitignored, chmod 600)
            self._save_persisted_keys(name, key)
            return p.status()

    def first_configured(self, preferred_order: list[str]) -> LLMProvider:
        """Return the first provider in `preferred_order` that's configured,
        falling back to Mock if none.

        Skips providers marked as "unhealthy" this session (e.g. 1113 no balance,
        401 invalid key) — tracked via `_unhealthy` set.
        """
        for name in preferred_order:
            if name in self._providers and self._providers[name].is_configured:
                if name in self._unhealthy:
                    continue
                return self._providers[name]
        return self._providers["mock"]

    def mark_unhealthy(self, name: str, reason: str = "") -> None:
        """Mark a provider as unhealthy for this session (fallback to next)."""
        self._unhealthy.add(name)
        self._unhealthy_reasons[name] = reason

    def is_unhealthy(self, name: str) -> bool:
        return name in self._unhealthy

    def reset_health(self) -> None:
        """Clear all unhealthy marks (e.g. after user re-pastes key)."""
        self._unhealthy.clear()
        self._unhealthy_reasons.clear()


_registry_instance: ProviderRegistry | None = None
_registry_lock = Lock()


def get_registry() -> ProviderRegistry:
    """Lazy singleton."""
    global _registry_instance
    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = ProviderRegistry()
    return _registry_instance
