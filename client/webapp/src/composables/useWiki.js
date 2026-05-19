// useWiki — fetch wrappers cho /api/yi-wiki/*

const BASE = "/api/yi-wiki";

async function _get(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`);
  const d = await r.json();
  if (d.status !== "ok") throw new Error(d.message || "wiki API error");
  return d;
}

export const getStats = () => _get("/stats").then(d => d.stats);
export const getLineage = () => _get("/lineage").then(d => d.tiers);
export const getAuthor = (id) => _get(`/authors/${id}`);
export const getConcepts = () => _get("/concepts").then(d => d.concepts);
export const getMethods = (authorId) =>
  _get(`/methods${authorId ? `?author_id=${authorId}` : ""}`).then(d => d.methods);
export const getPassages = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return _get(`/passages${qs ? `?${qs}` : ""}`).then(d => d.passages);
};

export const TIER_COLOR = {
  0: "#fbbf24",  // gold — Master
  1: "#f87171",  // red — Teacher
  2: "#60a5fa",  // blue — Direct disciple
  3: "#a78bfa",  // purple — Contemporary
  4: "#34d399",  // green — Minh-Thanh
  5: "#94a3b8",  // gray — Modern
};
