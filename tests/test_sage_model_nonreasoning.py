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


# ── T4: behavioral — phe_menh() (99xu deep_reading) ép model non-reasoning ────
# kể cả khi provider được chọn là MiniMax (mặc định M3 reasoning, gây RỖNG).

def test_phe_menh_pins_nonreasoning_model_even_when_minimax_selected(monkeypatch):
    import engine.tu_vi.analyzer as az
    from engine.ai.council import _SAGE_FAST_MODEL

    captured: dict = {}

    class _Resp:
        content = ('{"khai_de":"a","menh_than":"b","dai_van":"c",'
                   '"canh_bao":"d","ket_tam_an":"e"}')
        provider = "minimax"
        model = "MiniMax-M2.7-highspeed"
        prompt_tokens = 10
        completion_tokens = 20
        total_tokens = 30
        cost_usd = 0.0

    class _Prov:
        name = "minimax"
        default_model = "MiniMax-M3"   # reasoning default = bẫy gây rỗng

        def chat(self, *, messages, model=None, **kw):
            captured["model"] = model
            return _Resp()

    # Bypass cache I/O + ép provider chain chọn fake minimax.
    monkeypatch.setattr(az, "_cache_load", lambda *a, **k: None)
    monkeypatch.setattr(az, "_cache_save", lambda *a, **k: None)
    from engine.ai.registry import get_registry
    monkeypatch.setattr(get_registry(), "first_configured", lambda order: _Prov())

    pp = az.Person(person_key="self", name="", birth_datetime_local="1988-06-05T23:30:00",
                   gender="nam", timezone="Asia/Ho_Chi_Minh", user_id=None)
    out = az.TuViAnalyzer(pp, force=True).phe_menh()

    assert out.get("status") == "ok"
    # Đã ép model non-reasoning (KHÔNG để None → provider tự rơi về M3 reasoning).
    assert captured["model"] == _SAGE_FAST_MODEL["minimax"] == "MiniMax-M2.7-highspeed"
    assert captured["model"] not in REASONING_MODELS
