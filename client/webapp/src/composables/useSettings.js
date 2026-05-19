// Composable cho Settings / AI Providers
// Gọi backend: /api/ai/providers/*

const API_BASE = (import.meta.env.VITE_API_BASE || "").trim().replace(/\/+$/, "");

async function jget(path) {
  const r = await fetch(`${API_BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${path}`);
  return r.json();
}

async function jpost(path, body = {}) {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body)
  });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status}: ${path}\n${text.slice(0, 200)}`);
  }
  return r.json();
}

export async function listProviders() {
  return jget("/api/ai/providers");
}

export async function setProviderKey(name, apiKey) {
  return jpost(`/api/ai/providers/${name}/key`, { api_key: apiKey });
}

export async function setProviderNotes(name, { planType = null, notes = null } = {}) {
  return jpost(`/api/ai/providers/${name}/notes`, {
    plan_type: planType,
    notes
  });
}

export async function testProvider(name, { model = null, prompt = null } = {}) {
  const body = {};
  if (model) body.model = model;
  if (prompt) body.prompt = prompt;
  return jpost(`/api/ai/providers/${name}/test`, body);
}

export async function resetProviderHealth() {
  return jpost("/api/ai/providers/reset-health");
}

// Plan-type labels for UI
export const PLAN_TYPE_LABEL = {
  coding_plan: {
    label: "🎟️ Coding Plan",
    color: "#a78bfa",
    desc: "Subscription bao gồm code/API (Claude Code Pro, Cursor, ...)"
  },
  api_pay_per_token: {
    label: "💳 API trả theo token",
    color: "#fbbf24",
    desc: "Pay-per-use, tính token (DeepSeek, OpenAI standard, ZAI, ...)"
  },
  free_tier: {
    label: "🆓 Free tier",
    color: "#86efac",
    desc: "Có quota miễn phí, có thể bị limit (Anthropic free, Gemini free, ...)"
  },
  local: {
    label: "🏠 Local",
    color: "#60a5fa",
    desc: "Self-hosted, không tốn tiền (Ollama, llama.cpp, ...)"
  }
};

export const PROVIDER_DISPLAY = {
  zai: { name: "ZhipuAI / GLM-4.5", website: "https://open.bigmodel.cn" },
  deepseek: { name: "DeepSeek (V3 / R1)", website: "https://platform.deepseek.com" },
  anthropic: { name: "Anthropic Claude", website: "https://console.anthropic.com" },
  minimax: { name: "MiniMax / Hailuo (M2 + Coding Plan)", website: "https://platform.minimax.io" },
  gemini: { name: "Google Gemini (AI Studio — free)", website: "https://aistudio.google.com/apikey" },
  openrouter: { name: "OpenRouter (gateway 200+ models, free tier)", website: "https://openrouter.ai/keys" },
  ollama: { name: "Ollama (local, free)", website: "https://ollama.com" },
  mock: { name: "Mock (test)", website: null }
};
