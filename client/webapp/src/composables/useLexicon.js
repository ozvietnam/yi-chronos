// Composable cho YI-Lexicon API
// Gọi backend: /api/yi-lexicon/...

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

// ─── Stats ──────────────────────────────────────────────────────────────────

export async function getLexiconStats() {
  return jget("/api/yi-lexicon/stats");
}

// ─── Concepts ───────────────────────────────────────────────────────────────

export async function searchConcepts(q, { schools = null, limit = 30 } = {}) {
  const params = new URLSearchParams({ q, limit: String(limit) });
  if (schools && schools.length) params.set("schools", schools.join(","));
  return jget(`/api/yi-lexicon/concepts?${params.toString()}`);
}

export async function getConcept(conceptId) {
  return jget(`/api/yi-lexicon/concepts/${conceptId}`);
}

export async function reverseLookup(dimType, dimValue, { limit = 50 } = {}) {
  const params = new URLSearchParams({
    dim_type: dimType,
    dim_value: dimValue,
    limit: String(limit)
  });
  return jget(`/api/yi-lexicon/reverse-lookup?${params.toString()}`);
}

// ─── Conflicts ──────────────────────────────────────────────────────────────

export async function listConflicts(status = "open", limit = 50) {
  return jget(`/api/yi-lexicon/conflicts?status=${status}&limit=${limit}`);
}

export async function resolveConflict(conflictGroupId, { primaryMappingId = null, status = "resolved", anhNote = "" } = {}) {
  return jpost(`/api/yi-lexicon/conflicts/${conflictGroupId}/resolve`, {
    primary_mapping_id: primaryMappingId,
    status,
    anh_note: anhNote
  });
}

// ─── Distill queue ──────────────────────────────────────────────────────────

export async function getDistillQueue(status = null, limit = 100) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status) params.set("status", status);
  return jget(`/api/yi-lexicon/distill-queue?${params.toString()}`);
}

export async function resolveDistillItem(itemId, { status, reviewerNote = "" }) {
  return jpost(`/api/yi-lexicon/distill-queue/${itemId}/resolve`, {
    status,
    reviewer_note: reviewerNote
  });
}

// ─── Tiers + Reading Plan ──────────────────────────────────────────────────

export async function getTierManifest() {
  return jget("/api/yi-lexicon/tiers/manifest");
}

export async function getCurrentReadingWeek() {
  return jget("/api/yi-lexicon/tiers/current-week");
}

// ─── Interpret observation (Mai Hoa quan vật) ───────────────────────────────

export async function interpretObservation(text, schools = null) {
  return jpost("/api/yi-lexicon/interpret", { text, schools });
}

// ─── Library / Thủ thư ─────────────────────────────────────────────────────

async function jpatch(path, body = {}) {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body)
  });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status}: ${path}\n${text.slice(0, 200)}`);
  }
  return r.json();
}

export async function getLibrary({ tier = null, status = null, school = null } = {}) {
  const params = new URLSearchParams();
  if (tier) params.set("tier", tier);
  if (status) params.set("status", status);
  if (school) params.set("school", school);
  const q = params.toString();
  return jget(`/api/yi-lexicon/library${q ? "?" + q : ""}`);
}

export async function getLibraryStats() {
  return jget("/api/yi-lexicon/library/stats");
}

export async function getBook(corpusId) {
  return jget(`/api/yi-lexicon/library/books/${corpusId}`);
}

export async function updateBook(corpusId, patch) {
  return jpatch(`/api/yi-lexicon/library/books/${corpusId}`, patch);
}

export async function analyzeBook(filePath, { ocrPages = 6, skipLlm = false, register = true } = {}) {
  return jpost("/api/yi-lexicon/library/analyze", {
    file_path: filePath,
    ocr_pages: ocrPages,
    skip_llm: skipLlm,
    register
  });
}

export async function syncLibrary({ skipLlm = true } = {}) {
  return jpost(`/api/yi-lexicon/library/sync?skip_llm=${skipLlm}`);
}

export async function scanLibrary({ skipLlm = true, limit = null } = {}) {
  const params = new URLSearchParams({ skip_llm: String(skipLlm) });
  if (limit) params.set("limit", String(limit));
  return jget(`/api/yi-lexicon/library/scan?${params.toString()}`);
}

export async function listSchools() {
  return jget("/api/yi-lexicon/schools");
}

export async function addSchool({ key, viLabel, color = "#94a3b8" }) {
  return jpost("/api/yi-lexicon/schools", { key, vi_label: viLabel, color });
}

// ─── Restoration (Phase A — phục chế sách scan) ────────────────────────────

export async function restoreBook(corpusId, {
  pageStart = null, pageEnd = null, maxPages = null, skipLlm = false, dpi = 240
} = {}) {
  return jpost("/api/yi-lexicon/restore", {
    corpus_id: corpusId,
    page_start: pageStart,
    page_end: pageEnd,
    max_pages: maxPages,
    skip_llm: skipLlm,
    dpi
  });
}

export async function getRestoredOverview(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}`);
}

export async function getRestoredPage(corpusId, pageNo, { fmt = "html", lang = "zh" } = {}) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/page/${pageNo}?format=${fmt}&lang=${lang}`);
}

export async function getTranslationStatus(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/translation-status`);
}

export async function getRestoredWikilinks(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/wikilinks`);
}

export async function getRestoredFigures(corpusId, { status = null } = {}) {
  const qs = status ? `?status=${status}` : "";
  return jget(`/api/yi-lexicon/restored/${corpusId}/figures${qs}`);
}

async function jpatch2(path, body = {}) {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${path}`);
  return r.json();
}

export async function updateRestoredFigure(corpusId, figureId, patch) {
  return jpatch2(`/api/yi-lexicon/restored/${corpusId}/figures/${figureId}`, patch);
}

export async function getRestoredHashtags(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/hashtags`);
}

export async function getRestoredPersons(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/persons`);
}

export async function searchRestoredBook(corpusId, { hashtag = null, person = null, que = null, q = null } = {}) {
  const params = new URLSearchParams();
  if (hashtag) params.set("hashtag", hashtag);
  if (person) params.set("person", person);
  if (que) params.set("que", que);
  if (q) params.set("q", q);
  return jget(`/api/yi-lexicon/restored/${corpusId}/search?${params}`);
}

export const FIGURE_TYPE_LABEL = {
  ha_do: "🗺️ Hà Đồ",
  lac_thu: "🔲 Lạc Thư",
  bat_quai_tien_thien: "☯️ Bát Quái Tiên Thiên",
  bat_quai_hau_thien: "☯️ Bát Quái Hậu Thiên",
  am_duong: "☯ Vòng Âm Dương",
  que_hexagram: "📊 Quẻ Hexagram",
  bang_que: "📋 Bảng quẻ",
  so_do_ngu_hanh: "🌳 Sơ đồ Ngũ Hành",
  bieu_do_tu_vi: "🪐 Lá số Tử Vi",
  bang: "📊 Bảng dữ liệu",
  image: "🖼️ Ảnh",
  khac: "❓ Hình khác"
};

export const REDRAW_STATUS_LABEL = {
  none: { label: "—", color: "#64748b" },
  needs_redraw: { label: "🎨 Cần vẽ lại", color: "#fbbf24" },
  in_progress: { label: "✏️ Đang vẽ", color: "#60a5fa" },
  done: { label: "✓ Đã vẽ", color: "#86efac" },
  skip: { label: "Bỏ qua", color: "#94a3b8" }
};

export function restoredFigureUrl(corpusId, figureId) {
  return `${API_BASE}/api/yi-lexicon/restored/${corpusId}/figure/${figureId}`;
}

export async function getRestorationPlan(corpusId) {
  return jget(`/api/yi-lexicon/restored/${corpusId}/plan`);
}

export async function createRestorationPlan(corpusId, { overwrite = false, samplePages = null } = {}) {
  return jpost("/api/yi-lexicon/restored/plan", {
    corpus_id: corpusId,
    overwrite,
    sample_pages: samplePages
  });
}

export async function advancePlanPhase(corpusId, toPhase) {
  return jpost("/api/yi-lexicon/restored/plan/advance", {
    corpus_id: corpusId,
    to_phase: toPhase
  });
}

export async function markPlanBatch(corpusId, batchId, { status, pagesDone = null, notes = "" } = {}) {
  return jpost("/api/yi-lexicon/restored/plan/batch", {
    corpus_id: corpusId,
    batch_id: batchId,
    status,
    pages_done: pagesDone,
    notes
  });
}

export async function appendPlanNote(corpusId, note, { target = "general" } = {}) {
  return jpost("/api/yi-lexicon/restored/plan/note", {
    corpus_id: corpusId,
    note,
    target
  });
}

export const PHASE_LABEL = {
  1: { label: "Phase 1 — Phục dựng nguyên văn", color: "#fbbf24", short: "P1" },
  2: { label: "Phase 2 — Đọc kỹ đọc sâu", color: "#60a5fa", short: "P2" },
  3: { label: "Phase 3 — Wiki + Mapping", color: "#86efac", short: "P3" }
};

export const PHASE_STATUS_LABEL = {
  not_started: { label: "Chưa bắt đầu", color: "#64748b" },
  in_progress: { label: "Đang chạy", color: "#fbbf24" },
  done: { label: "Xong", color: "#86efac" }
};

export const BATCH_STATUS_LABEL = {
  pending:     { label: "Chờ", color: "#94a3b8", icon: "○" },
  in_progress: { label: "Đang chạy", color: "#fbbf24", icon: "◐" },
  done:        { label: "Xong", color: "#86efac", icon: "●" },
  failed:      { label: "Lỗi", color: "#f87171", icon: "✗" }
};

export const RESTORED_STATUS_LABEL = {
  none:    { label: "Chưa phục chế", color: "#64748b" },
  pending: { label: "Đang phục chế", color: "#fbbf24" },
  partial: { label: "Phục chế 1 phần", color: "#60a5fa" },
  done:    { label: "Đã phục chế",   color: "#86efac" },
  error:   { label: "Lỗi",            color: "#f87171" }
};

export const RESTORE_METHOD_LABEL = {
  text_layer:  { label: "📖 Text-layer",  color: "#86efac", icon: "📖", desc: "PDF có text embed → MarkItDown extract trực tiếp (rất nhanh)" },
  hybrid:      { label: "🔀 Hybrid",     color: "#fbbf24", icon: "🔀", desc: "Text + Scan mix — MarkItDown + OCR fallback" },
  pure_scan:   { label: "📷 Pure scan",  color: "#f87171", icon: "📷", desc: "Scan thuần — phải OCR qua qwen-vl" },
  unknown:     { label: "❓ Chưa probe", color: "#94a3b8", icon: "❓", desc: "Bấm 🔍 để probe text layer" }
};

export async function scanLibraryTextLayers({ onlyUnprobed = false } = {}) {
  return jpost(`/api/yi-lexicon/library/scan-text-layers?only_unprobed=${onlyUnprobed}`);
}

export async function classifyBookTextLayer(corpusId) {
  return jget(`/api/yi-lexicon/library/classify/${corpusId}`);
}

export const COPYRIGHT_LABEL = {
  public_domain:   { label: "Public Domain", color: "#86efac", icon: "✓" },
  internal_only:   { label: "Nội bộ", color: "#fbbf24", icon: "🔒" },
  consent_pending: { label: "Chờ duyệt bản quyền", color: "#94a3b8", icon: "⏳" }
};

// ─── Helper labels ─────────────────────────────────────────────────────────

export const STATUS_LABEL = {
  queued:  { label: "Chờ đọc",    color: "#94a3b8" },
  reading: { label: "Đang đọc",   color: "#fbbf24" },
  done:    { label: "Đã xong",    color: "#86efac" },
  skip:    { label: "Bỏ qua",     color: "#64748b" },
  error:   { label: "Lỗi",        color: "#f87171" }
};

export const TIER_DESCRIPTION = {
  S: "Kinh điển gốc (Kinh Dịch, Nội Kinh) — uy tín tuyệt đối",
  A: "Kinh điển trường phái — Trích Thiên Tủy, Tăng San Bốc Dịch...",
  B: "Học giả VN hiện đại — Nguyễn Duy Cần, Thiệu Vĩ Hoa...",
  C: "Đại chúng / sách mẫu / blog tổng hợp"
};

// ─── Helper labels ──────────────────────────────────────────────────────────

export const TIER_LABEL = {
  S: { label: "Tier S", color: "#7dd3fc", note: "Canonical — không tranh cãi" },
  A: { label: "Tier A", color: "#a78bfa", note: "Kinh điển trường phái" },
  B: { label: "Tier B", color: "#fbbf24", note: "Modern/Vietnamese" },
  C: { label: "Tier C", color: "#94a3b8", note: "Đại chúng / cross-ref" }
};

export const SCHOOL_LABEL = {
  common: "Chung",
  mai_hoa: "Mai Hoa",
  luc_hao: "Lục Hào",
  lien_hoa: "Liên Hoa",
  bat_tu: "Bát Tự",
  tu_vi: "Tử Vi",
  ha_lac: "Hà Lạc",
  chiem_tinh: "Chiêm tinh"
};

export const DIM_TYPE_LABEL = {
  bat_quai: "Bát Quái",
  ngu_hanh: "Ngũ Hành",
  am_duong: "Âm Dương",
  thien_can: "Thiên Can",
  dia_chi: "Địa Chi",
  tiet_khi: "Tiết Khí",
  hexagram: "Quẻ Hexagram",
  thap_than: "Thập Thần",
  than_sat: "Thần Sát",
  cung_tu_vi: "Cung Tử Vi",
  huong: "Hướng",
  mua: "Mùa",
  tang_phu: "Tạng Phủ",
  thoi: "Thời",
  khac: "Khác",
  other: "Khác"
};
