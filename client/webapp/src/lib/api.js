/**
 * VITE_API_BASE = origin backend, KHÔNG thêm /api (path request đã có /api/...).
 * Chuẩn hóa để tránh lỗi 404 do URL dạng .../api/api/luc-hao/cast khi ai đó ghi nhầm .../api.
 */
function normalizeApiBase(raw) {
  if (!raw) return "";
  let s = raw.trim().replace(/\/+$/, "");
  if (s.endsWith("/api")) {
    s = s.slice(0, -4).replace(/\/+$/, "");
  }
  return s;
}

const API_BASE = normalizeApiBase((import.meta.env.VITE_API_BASE || "").trim());

export function getApiBaseDisplay() {
  return API_BASE || "(để trống VITE_API_BASE → gọi /api… qua Vite proxy)";
}

/** Hướng xử lý khi :8000 bị app khác chiếm hoặc proxy trỏ nhầm. */
export function portMismatchSetupHint() {
  return [
    "• Xem process nào đang nghe cổng:  lsof -nP -iTCP:8000 -sTCP:LISTEN",
    "• Hoặc chạy YI-CHRONOS trên cổng khác (ví dụ 8010):",
    "    source .venv/bin/activate && python -m uvicorn api.main:app --host 127.0.0.1 --port 8010",
    "• Trong client/webapp tạo .env.development.local:",
    "    VITE_DEV_PROXY_TARGET=http://127.0.0.1:8010",
    "  (và nếu gọi trực tiếp API, thêm) VITE_API_BASE=http://127.0.0.1:8010",
    "• Khởi động lại npm run dev sau khi sửa .env."
  ].join("\n");
}

/**
 * GET /api/health — xác minh server đích là YI-CHRONOS (tránh app khác chiếm cổng).
 * @returns {Promise<{ ok: boolean; reason?: string; message?: string; health?: object; status?: number; snippet?: string; data?: object }>}
 */
export async function probeYiChronosBackend() {
  const url = `${API_BASE}/api/health`;
  try {
    const response = await fetch(url, { method: "GET", headers: { Accept: "application/json" } });
    const text = await response.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      return {
        ok: false,
        reason: "not_json",
        status: response.status,
        message:
          "Phản hồi /api/health không phải JSON — thường là process khác (không phải YI-CHRONOS) đang chiếm cổng backend.",
        snippet: text.replace(/\s+/g, " ").slice(0, 200),
      };
    }
    if (!response.ok) {
      return {
        ok: false,
        reason: "http_error",
        status: response.status,
        message: `GET /api/health trả HTTP ${response.status}. Backend đích không phục vụ đúng API YI.`,
        data,
      };
    }
    const looksYi =
      data &&
      data.status === "ok" &&
      typeof data.algorithm_version === "string" &&
      data.algorithm_version.length > 0 &&
      typeof data.ziwei_ruleset_id === "string";
    if (looksYi) {
      return { ok: true, reason: null, health: data };
    }
    return {
      ok: false,
      reason: "foreign_json",
      message: "Nhận được JSON nhưng không khớp YI-CHRONOS (thiếu trường health chuẩn).",
      data,
    };
  } catch (err) {
    const name = err?.name || "Error";
    const message = err?.message || String(err);
    return {
      ok: false,
      reason: "network",
      message: `${name}: ${message}`,
      detail: "Không kết nối được tới backend (URL hiện tại có thể sai hoặc server chưa bật).",
    };
  }
}

function isHttp404(err) {
  return err instanceof Error && /HTTP 404\b/.test(err.message);
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  let response;
  try {
    response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
  } catch (err) {
    const name = err?.name || "NetworkError";
    const message = err?.message || String(err);
    throw new Error(
      `${name}: ${message}. URL: ${url || path}. Backend cần chạy tại http://127.0.0.1:8000 (vd: ./scripts/dev-up.sh) hoặc đặt VITE_API_BASE đúng.`,
    );
  }
  const text = await response.text();
  if (!response.ok) {
    let detail = text;
    try {
      detail = JSON.stringify(JSON.parse(text));
    } catch {
      /* plain text body */
    }
    throw new Error(`HTTP ${response.status}: ${detail}`);
  }
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Phản hồi không phải JSON: ${text.slice(0, 200)}`);
  }
}

export function getUniverseNow() {
  return request("/api/universe-now");
}

export function getPlanetPositions() {
  return request("/api/planet-positions");
}

export function getSkyNow({ at = null, lat = null, lon = null } = {}) {
  const params = new URLSearchParams();
  if (at) params.set("at", at);
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  const qs = params.toString();
  return request(`/api/sky-now${qs ? `?${qs}` : ""}`);
}

export function getNatalUniverse({ at, lat = null, lon = null, tzHours = 7 }) {
  const params = new URLSearchParams({ at });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  if (tzHours !== null && tzHours !== "") params.set("tz_hours", String(tzHours));
  return request(`/api/natal-universe?${params.toString()}`);
}

export function getLuuNguyet({ at, lat = null, lon = null, tzHours = 7, yearStart = null, yearEnd = null }) {
  const params = new URLSearchParams({ at });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  if (tzHours !== null && tzHours !== "") params.set("tz_hours", String(tzHours));
  if (yearStart !== null) params.set("year_start", String(yearStart));
  if (yearEnd !== null) params.set("year_end", String(yearEnd));
  return request(`/api/tu-vi/luu-nguyet?${params.toString()}`);
}

export function getLifeTimeline({ birthAt, spanYears = 90 }) {
  const params = new URLSearchParams({ birth_at: birthAt, span_years: String(spanYears) });
  return request(`/api/life-timeline?${params.toString()}`);
}

export function getTransitHits({ birthAt, lat = null, lon = null, spanYears = 90 }) {
  const params = new URLSearchParams({ birth_at: birthAt, span_years: String(spanYears) });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/transit-hits?${params.toString()}`);
}

export function getSolarReturns({ birthAt, lat = null, lon = null, spanYears = 90 }) {
  const params = new URLSearchParams({ birth_at: birthAt, span_years: String(spanYears) });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/solar-returns?${params.toString()}`);
}

export function getProgressedChart({ birthAt, atAge, lat = null, lon = null }) {
  const params = new URLSearchParams({ birth_at: birthAt, at_age: String(atAge) });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/progressed-chart?${params.toString()}`);
}

export function getProgressedMoonTimeline({ birthAt, spanYears = 90 }) {
  const params = new URLSearchParams({ birth_at: birthAt, span_years: String(spanYears) });
  return request(`/api/progressed-moon-timeline?${params.toString()}`);
}

export function getLunarReturns({ birthAt, fromAt = null, count = 12, lat = null, lon = null }) {
  const params = new URLSearchParams({ birth_at: birthAt, count: String(count) });
  if (fromAt) params.set("from_at", fromAt);
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/lunar-returns?${params.toString()}`);
}

export function getSolarArcHits({ birthAt, lat = null, lon = null, spanYears = 90 }) {
  const params = new URLSearchParams({ birth_at: birthAt, span_years: String(spanYears) });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/solar-arc-hits?${params.toString()}`);
}

export function getEclipses({ birthAt, lat = null, lon = null, spanYears = 90, onlyActivated = true }) {
  const params = new URLSearchParams({
    birth_at: birthAt,
    span_years: String(spanYears),
    only_activated: String(onlyActivated)
  });
  if (lat !== null && lat !== "") params.set("lat", lat);
  if (lon !== null && lon !== "") params.set("lon", lon);
  return request(`/api/eclipses?${params.toString()}`);
}

export function getYiNarrative({ datetimeLocal = null, timezone = "Asia/Ho_Chi_Minh" } = {}) {
  const params = new URLSearchParams({ timezone });
  if (datetimeLocal) params.set("datetime_local", datetimeLocal);
  return request(`/api/yi-narrative?${params.toString()}`);
}

export function getYiDiepSequence({ datetimeLocal = null, timezone = "Asia/Ho_Chi_Minh", diepCount = 5 } = {}) {
  const params = new URLSearchParams({ timezone, diep_count: String(diepCount) });
  if (datetimeLocal) params.set("datetime_local", datetimeLocal);
  return request(`/api/yi-diep-sequence?${params.toString()}`);
}

export function getPersonalQuai({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh" }) {
  const params = new URLSearchParams({ birth_datetime_local: birthDatetimeLocal, timezone });
  return request(`/api/personal-quai?${params.toString()}`);
}

export function getVanTrongVan({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", startDate = null, spanDays = 30 }) {
  const params = new URLSearchParams({
    birth_datetime_local: birthDatetimeLocal,
    timezone,
    span_days: String(spanDays),
  });
  if (startDate) params.set("start_date", startDate);
  return request(`/api/van-trong-van?${params.toString()}`);
}

// ============================================================================
// GPS Phase 3 — Prescriptive layer (EXPERIMENTAL, single-user gate)
// ============================================================================

export function getGpsDay({ birthDatetimeLocal, targetDate, timezone = "Asia/Ho_Chi_Minh", minScore = 55 }) {
  const params = new URLSearchParams({
    birth_datetime_local: birthDatetimeLocal,
    target_date: targetDate,
    timezone,
    min_score: String(minScore),
  });
  return request(`/api/gps-day?${params.toString()}`);
}

export function gpsPreRegister({ birthDatetimeLocal, targetDate, timezone = "Asia/Ho_Chi_Minh", minScore = 70 }) {
  return request("/api/gps-pre-register", {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      target_date: targetDate,
      timezone,
      min_score: minScore,
    }),
  });
}

export function getGpsPredictions({ profileHash, status = null, limit = 200 }) {
  const params = new URLSearchParams({ profile_hash: profileHash, limit: String(limit) });
  if (status) params.set("status", status);
  return request(`/api/gps-predictions?${params.toString()}`);
}

export function submitGpsPredictionFeedback({ predictionId, responseEnum, confidenceEnum = "unsure", actualOutcome = null }) {
  return request("/api/gps-prediction-feedback", {
    method: "POST",
    body: JSON.stringify({
      prediction_id: predictionId,
      response_enum: responseEnum,
      confidence_enum: confidenceEnum,
      actual_outcome: actualOutcome,
    }),
  });
}

export function getGpsAccuracy({ profileHash }) {
  const params = new URLSearchParams({ profile_hash: profileHash });
  return request(`/api/gps-accuracy?${params.toString()}`);
}

export function postFamilyResonance({ members, weddingDatetimeLocal = null, weddingTimezone = "Asia/Ho_Chi_Minh" }) {
  return request("/api/family-resonance", {
    method: "POST",
    body: JSON.stringify({
      members,
      wedding_datetime_local: weddingDatetimeLocal,
      wedding_timezone: weddingTimezone,
    }),
  });
}

export function postVanTrongVanWithFamily({ birthDatetimeLocal, members = [], timezone = "Asia/Ho_Chi_Minh", startDate = null, spanDays = 30 }) {
  return request("/api/van-trong-van-with-family", {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      start_date: startDate,
      span_days: spanDays,
      members,
    }),
  });
}

export function postGpsDayWithFamily({ birthDatetimeLocal, targetDate, members = [], timezone = "Asia/Ho_Chi_Minh", minScore = 55 }) {
  return request("/api/gps-day-with-family", {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      target_date: targetDate,
      timezone,
      min_score: minScore,
      members,
    }),
  });
}

export function postGpsPreRegisterWithFamily({ birthDatetimeLocal, targetDate, members = [], timezone = "Asia/Ho_Chi_Minh", minScore = 70 }) {
  return request("/api/gps-pre-register-with-family", {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      target_date: targetDate,
      timezone,
      min_score: minScore,
      members,
    }),
  });
}

export function getActiveRuleset() {
  return request("/api/ruleset/active");
}

export function submitPersonalProfile(payload) {
  return request("/api/personal-profile", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function submitFeedback(payload) {
  return request("/api/feedback", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function convertCalendar(payload) {
  return request("/api/calendar-convert", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function compareBasic(payload) {
  return request("/api/compare-basic", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function castLienHoa({ numberRightHand, numberLeftHand, questionText = "", gender = "nam" }) {
  return request("/api/lien-hoa/cast", {
    method: "POST",
    body: JSON.stringify({
      number_right_hand: numberRightHand,
      number_left_hand: numberLeftHand,
      question_text: questionText,
      gender,
    }),
  });
}

/**
 * Ưu tiên POST /api/luc-hao/cast. Nếu 404 (backend cũ hoặc sai route), fallback POST /calculate
 * cùng payload — endpoint này có từ đầu và cũng embed luc_hao_state.
 */
export async function castLucHao(payload) {
  try {
    return await request("/api/luc-hao/cast", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  } catch (err) {
    if (!isHttp404(err)) throw err;
    const full = await request("/calculate", {
      method: "POST",
      body: JSON.stringify({
        datetime_local: payload.datetime_local,
        timezone: payload.timezone,
        question_text: payload.question_text,
        interaction_signal: payload.interaction_signal
      })
    });
    if (!full.luc_hao_state) throw err;
    return {
      timezone: payload.timezone ?? full.timezone ?? "Asia/Ho_Chi_Minh",
      algorithm_version: full.algorithm_version,
      ziwei_school: full.ziwei_school,
      ziwei_ruleset_id: full.ziwei_ruleset_id,
      ziwei_ruleset_label: full.ziwei_ruleset_label,
      luc_hao_state: full.luc_hao_state
    };
  }
}

/** Gợi ý tiếng Việt khi call Lục Hào thất bại (404 thường do sai process trên cổng đích). */
export function lucHaoFailureHint(originalError) {
  const msg = originalError instanceof Error ? originalError.message : String(originalError || "");
  const head = "Không gọi được API Lục Hào. Kiểm tra backend rồi gieo lại.";
  const baseLine = `\n\nĐịa chỉ API: ${getApiBaseDisplay()}\n\n${portMismatchSetupHint()}`;
  if (/HTTP 404\b/.test(msg)) {
    return `${head}\n${msg}\n\nGợi ý (404): Cổng backend đích không có route YI-CHRONOS — thường do process khác đã chiếm cổng (thường :8000) hoặc VITE_API_BASE / VITE_DEV_PROXY_TARGET trỏ nhầm.\nChạy đúng app từ thư mục gốc repo:\n  source .venv/bin/activate && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000${baseLine}`;
  }
  if (/Phản hồi không phải JSON/i.test(msg) || /not valid JSON/i.test(msg)) {
    return `${head}\n${msg}\n\nGợi ý: Phản hồi không phải JSON thường là HTML của app khác trên cùng cổng.${baseLine}`;
  }
  if (/Failed to fetch|Load failed|NetworkError|ECONNREFUSED|Network request failed/i.test(msg)) {
    return `${head}\n${msg}\n\nGợi ý: Không kết nối được backend — kiểm tra đã bật uvicorn và cổng trùng với proxy.${baseLine}`;
  }
  return `${head}\n${msg}${baseLine}`;
}

export function saveLucHaoCase(payload) {
  return request("/api/luc-hao/save-case", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function submitLucHaoFeedback(payload) {
  return request("/api/luc-hao/feedback", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getHexagramInterpretationV2(kingWenIndex) {
  return request(`/api/hexagram-interpretation-v2/${kingWenIndex}`);
}

export function getHexagramBySlug(slug) {
  return request(`/api/hexagram-by-slug/${encodeURIComponent(slug)}`);
}

export function getHexagramSlugs() {
  return request(`/api/hexagram-slugs`);
}

export function castBatTu({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/cast`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuLuanGiai({
  birthDatetimeLocal,
  timezone = "Asia/Ho_Chi_Minh",
  gender = "nam",
  currentAge = null,
}) {
  return request(`/api/bat-tu/luan-giai`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
      current_age: currentAge,
    }),
  });
}

export function batTuLuuNien({
  birthDatetimeLocal,
  timezone = "Asia/Ho_Chi_Minh",
  gender = "nam",
  currentAge = null,
  targetYear = null,
  includeLuuNguyet = true,
}) {
  return request(`/api/bat-tu/luu-nien`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
      current_age: currentAge,
      target_year: targetYear,
      include_luu_nguyet: includeLuuNguyet,
    }),
  });
}

export function batTuHonNhan({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/hon-nhan`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuSuNghiep({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/su-nghiep`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuTaiVan({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/tai-van`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuSucKhoe({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/suc-khoe`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuBaoMenhPDF({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  // Returns a PDF blob URL the caller can open / download
  return fetch(`/api/bat-tu/bao-menh-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const blob = await r.blob();
    return URL.createObjectURL(blob);
  });
}

export function dongYMonthlyHealth({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam", year = 2026 }) {
  return request(`/api/dong-y/monthly-health`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone, gender, year,
    }),
  });
}

export function dongYFull({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam", chanThuong = "" }) {
  return request(`/api/dong-y/full`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone, gender,
      chan_thuong: chanThuong,
    }),
  });
}

export function batTuSucKhoeSau({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam", chanThuong = "", currentAge = null }) {
  return request(`/api/bat-tu/suc-khoe-sau`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
      chan_thuong: chanThuong,
      current_age: currentAge,
    }),
  });
}

export function batTuLuanGiaiSoiNhieuSach({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/bat-tu/luan-giai-soi-nhieu-sach`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function batTuGlossaryLookup(key) {
  return request(`/api/bat-tu/glossary/${encodeURIComponent(key)}`);
}

export function haLacLuanGiai({
  birthDatetimeLocal,
  timezone = "Asia/Ho_Chi_Minh",
  gender = "nam",
  currentAge = null,
}) {
  return request(`/api/ha-lac/luan-giai`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
      current_age: currentAge,
    }),
  });
}

export function castHaLac({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/ha-lac/cast`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function haLacLuanGiaiSau({
  birthDatetimeLocal,
  timezone = "Asia/Ho_Chi_Minh",
  gender = "nam",
}) {
  return request(`/api/ha-lac/luan-giai-sau`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

export function getTuViChinhTinhList() {
  return request("/api/tu-vi/chinh-tinh");
}

export function getTuViChinhTinh(starId) {
  return request(`/api/tu-vi/chinh-tinh/${encodeURIComponent(starId)}`);
}

export function castTuViLaSo({ birthDatetimeLocal, timezone = "Asia/Ho_Chi_Minh", gender = "nam" }) {
  return request(`/api/tu-vi/cast`, {
    method: "POST",
    body: JSON.stringify({
      birth_datetime_local: birthDatetimeLocal,
      timezone,
      gender,
    }),
  });
}

// ─── YI-Hermes API ─────────────────────────────────────────────────────────

/**
 * Lập lá số Thần Số Học Pythagoras (Decoz) từ TÊN + NGÀY SINH.
 * @param {{ name: string, birthDate: string, system?: string, includeChaldean?: boolean, targetYear?: number|null, targetMonth?: number|null, targetDay?: number|null, currentName?: string|null, nameOrder?: string }} p
 */
export function castThanSo({
  name,
  birthDate,
  system = "pythagorean",
  includeChaldean = true,
  targetYear = null,
  targetMonth = null,
  targetDay = null,
  currentName = null,
  nameOrder = "vn",
}) {
  return request("/api/than-so/cast", {
    method: "POST",
    body: JSON.stringify({
      name,
      birth_date: birthDate,
      system,
      include_chaldean: includeChaldean,
      target_year: targetYear,
      target_month: targetMonth,
      target_day: targetDay,
      current_name: currentName,
      name_order: nameOrder,
    }),
  });
}

export function thanSoGlossary() {
  return request("/api/than-so/glossary");
}

export function yiHermesChat({ userMessage, context = {}, history = [] }) {
  return request(`/api/yi-hermes/chat`, {
    method: "POST",
    body: JSON.stringify({
      user_message: userMessage,
      context,
      history,
    }),
  });
}

export function yiHermesModules() {
  return request(`/api/yi-hermes/modules`);
}

export function yiHermesGlossaryList(module = null) {
  const qs = module ? `?module=${encodeURIComponent(module)}` : "";
  return request(`/api/yi-hermes/glossary${qs}`);
}

export function yiHermesGlossarySearch(query) {
  return request(`/api/yi-hermes/glossary/search?q=${encodeURIComponent(query)}`);
}

export function yiHermesGlossaryGet(termVi) {
  return request(`/api/yi-hermes/glossary/term/${encodeURIComponent(termVi)}`);
}

/**
 * H6.0 — hỏi Hermes (trả lời nhanh 1-sage) cho user đang đăng nhập.
 * Đồng bộ: trả {status:"done", answer, sage, ...} | {status:"out_of_scope", reply}
 * | {status:"denied"|"budget_exceeded"|...}. Yêu cầu đăng nhập (cookie phiên same-origin).
 */
export function hermesAsk({ question, personKey = "self" }) {
  return request("/api/hermes/ask", {
    method: "POST",
    body: JSON.stringify({ question, person_key: personKey }),
  });
}
