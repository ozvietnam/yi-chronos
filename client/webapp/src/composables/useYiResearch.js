// Composable cho YI-Research — autonomous research agent

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

export async function runResearch({
  query,
  provider = "ollama",
  model = "qwen3:32b",
  retriever = "duckduckgo",
  catalogSync = true,
  catalogApply = false
} = {}) {
  return jpost("/api/yi-research/run", {
    query,
    provider,
    model,
    retriever,
    catalog_sync: catalogSync,
    catalog_apply: catalogApply
  });
}

export async function getResearchJob(jobId) {
  return jget(`/api/yi-research/jobs/${jobId}`);
}

export async function listResearchJobs({ limit = 30, status = null } = {}) {
  const q = new URLSearchParams({ limit: String(limit) });
  if (status) q.set("status", status);
  return jget(`/api/yi-research/jobs?${q}`);
}

export async function getResearchReport(jobId) {
  return jget(`/api/yi-research/reports/${jobId}`);
}

export async function applyResearchCatalog(jobId) {
  return jpost(`/api/yi-research/jobs/${jobId}/catalog-apply`);
}

export const RESEARCH_STATUS_LABEL = {
  pending:  { label: "⏳ Chờ", color: "#94a3b8" },
  running:  { label: "🔄 Đang chạy", color: "#fbbf24" },
  done:     { label: "✓ Xong", color: "#86efac" },
  error:    { label: "✗ Lỗi", color: "#f87171" }
};

export const RESEARCH_PROVIDERS = [
  { value: "ollama", label: "🏠 Ollama (local, free)", defaultModel: "qwen3:32b" },
  { value: "minimax", label: "🚀 MiniMax (Coding Plan)", defaultModel: "MiniMax-M2" },
  { value: "deepseek", label: "💎 DeepSeek (paid, fast)", defaultModel: "deepseek-chat" },
  { value: "openrouter", label: "🌐 OpenRouter (free tier)", defaultModel: "openai/gpt-oss-120b:free" },
  { value: "gemini", label: "🔍 Google Gemini (free)", defaultModel: "gemini-2.5-flash" }
];

export const RESEARCH_RETRIEVERS = [
  { value: "duckduckgo", label: "🦆 DuckDuckGo (free)" },
  { value: "tavily", label: "🔎 Tavily (cần API key)" },
  { value: "exa", label: "🧠 Exa (semantic)" },
  { value: "google", label: "Google" },
  { value: "bing", label: "Bing" }
];
