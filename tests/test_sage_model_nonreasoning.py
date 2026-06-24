"""Sage ANSWER paths phải dùng model KHÔNG-reasoning.

Gốc lỗi (prod 2026-06-24): model reasoning (deepseek-v4-pro, MiniMax-M3, R1) khi gặp prompt
sage lớn (persona + chart + RAG) đốt sạch max_tokens vào <think> → content RỖNG (len=0) →
"answer_failed" / luận "chung chung". Bộ test này KHOÁ bất biến: mọi đường sinh-câu-trả-lời
chọn model non-reasoning. (deep_reading/test_deep_reading.py mock generation nên KHÔNG bắt
được lỗi này — đây là chỗ bù.)
"""
from __future__ import annotations

# Model reasoning đã biết — KHÔNG được dùng cho đường trả lời sage.
REASONING_MODELS = {
    "deepseek-v4-pro", "deepseek-reasoner",
    "MiniMax-M3", "MiniMax-M1", "MiniMax-M2",
}


class _FakeProvider:
    def __init__(self, name: str, default_model: str):
        self.name = name
        self.default_model = default_model


# ── T1: root fix — deepseek default = deepseek-chat ───────────────────────────

def test_deepseek_default_is_nonreasoning():
    from engine.ai.providers.deepseek import DeepSeekProvider
    p = DeepSeekProvider(api_key="sk-test")
    assert p.default_model == "deepseek-chat"
    assert p.default_model not in REASONING_MODELS
    # v4-pro vẫn KHẢ DỤNG (truyền tường minh) nhưng KHÔNG là default.
    assert "deepseek-v4-pro" in p.available_models


# ── T2: bảng _SAGE_FAST_MODEL toàn non-reasoning ──────────────────────────────

def test_sage_fast_model_table_all_nonreasoning():
    from engine.ai.council import _SAGE_FAST_MODEL
    assert _SAGE_FAST_MODEL["deepseek"] == "deepseek-chat"
    assert _SAGE_FAST_MODEL["minimax"] == "MiniMax-M2.7-highspeed"
    for prov, model in _SAGE_FAST_MODEL.items():
        assert model not in REASONING_MODELS, f"{prov} maps to reasoning model {model}"


# ── T3: helper sage_model() — nguồn sự thật duy nhất ──────────────────────────

def test_sage_model_maps_reasoning_to_nonreasoning():
    from engine.ai.council import sage_model
    # deepseek-v4-pro (reasoning) → deepseek-chat
    assert sage_model(_FakeProvider("deepseek", "deepseek-v4-pro")) == "deepseek-chat"
    # MiniMax-M3 (reasoning) → M2.7-highspeed
    assert sage_model(_FakeProvider("minimax", "MiniMax-M3")) == "MiniMax-M2.7-highspeed"


def test_sage_model_passthrough_for_nonreasoning_provider():
    from engine.ai.council import sage_model
    # Provider ngoài map (gemini/openrouter) — default đã non-reasoning → trả default.
    assert sage_model(_FakeProvider("gemini", "gemini-2.5-flash")) == "gemini-2.5-flash"
    # fallback (model caller có sẵn) được ưu tiên hơn default khi provider ngoài map.
    assert sage_model(_FakeProvider("openrouter", "z-ai/glm-4.5-air:free"),
                      "z-ai/glm-4.5-air:free") == "z-ai/glm-4.5-air:free"


def test_sage_model_never_returns_reasoning():
    from engine.ai.council import sage_model
    for name, dflt in [("deepseek", "deepseek-v4-pro"), ("minimax", "MiniMax-M3"),
                       ("zai", "glm-4.5-flash"), ("anthropic", "claude-sonnet-4-5-20250929")]:
        assert sage_model(_FakeProvider(name, dflt)) not in REASONING_MODELS


# ── T4/T5: behavioral — phe_menh() (99xu deep_reading) ───────────────────────
# Lỗi gốc (đo prod 2026-06-24): chain minimax-ĐẦU → M2.7-highspeed vẫn <think> ăn token →
# content RỖNG (raw 11750ch think → strip → len0). deepseek-chat tin cậy (JSON 16s). Fix:
# chain deepseek-ĐẦU + ÉP sage_model + NHẬN provider đầu tiên content KHÔNG rỗng.


class _RecProvider:
    """Provider giả ghi lại model được truyền + trả content cố định."""
    def __init__(self, name, content, default_model="x-default"):
        self.name = name
        self.default_model = default_model
        self.is_configured = True
        self._content = content
        self.calls: list = []

    def chat(self, *, messages, model=None, **kw):
        self.calls.append(model)
        return type("R", (), {
            "content": self._content, "provider": self.name, "model": "ret",
            "prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2, "cost_usd": 0.0,
        })()


def _install_fake_registry(monkeypatch, providers: dict):
    from engine.ai.registry import get_registry
    reg = get_registry()
    monkeypatch.setattr(reg, "get", lambda n: providers[n])          # KeyError nếu thiếu → loop bỏ qua
    monkeypatch.setattr(reg, "is_unhealthy", lambda n: False)
    monkeypatch.setattr(reg, "mark_unhealthy", lambda *a, **k: None, raising=False)


def _founder_person(az):
    return az.Person(person_key="self", name="", birth_datetime_local="1988-06-05T23:30:00",
                     gender="nam", timezone="Asia/Ho_Chi_Minh", user_id=None)


def test_phe_menh_prefers_deepseek_and_pins_chat(monkeypatch):
    import engine.tu_vi.analyzer as az
    monkeypatch.setattr(az, "_cache_load", lambda *a, **k: None)
    monkeypatch.setattr(az, "_cache_save", lambda *a, **k: None)
    ds = _RecProvider("deepseek",
                      '{"khai_de":"a","menh_than":"b","dai_van":"c","canh_bao":"d","ket_tam_an":"e"}',
                      default_model="deepseek-v4-pro")   # reasoning default = bẫy
    _install_fake_registry(monkeypatch, {"deepseek": ds})

    out = az.TuViAnalyzer(_founder_person(az), force=True).phe_menh()
    assert out.get("status") == "ok" and out.get("provider") == "deepseek"
    # Ép deepseek-chat (non-reasoning) — KHÔNG để None/v4-pro.
    assert ds.calls == ["deepseek-chat"]
    assert "deepseek-v4-pro" not in ds.calls


def test_phe_menh_falls_through_on_empty_content(monkeypatch):
    """Provider trả status-ok nhưng content RỖNG (reasoning ăn token) → nhảy provider kế."""
    import engine.tu_vi.analyzer as az
    monkeypatch.setattr(az, "_cache_load", lambda *a, **k: None)
    monkeypatch.setattr(az, "_cache_save", lambda *a, **k: None)
    empty = _RecProvider("deepseek", "", default_model="deepseek-v4-pro")     # rỗng
    good = _RecProvider("gemini", '{"khai_de":"X"}', default_model="gemini-2.5-flash")
    _install_fake_registry(monkeypatch, {"deepseek": empty, "gemini": good})

    out = az.TuViAnalyzer(_founder_person(az), force=True).phe_menh()
    assert out.get("status") == "ok" and out.get("provider") == "gemini"   # đã fallback khỏi rỗng
    assert empty.calls and good.calls                                       # cả hai được thử
