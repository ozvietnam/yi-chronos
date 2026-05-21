<script setup>
/**
 * TuViLaSoPanel — full Tử Vi lá số rendering.
 *
 * Traditional 4×4 grid where outer 12 cells = 12 địa chi positions:
 *   Row 0 (top):    Tỵ  Ngọ  Mùi  Thân
 *   Row 1:          Thìn  ─── center ───  Dậu
 *   Row 2:          Mão   ─── center ───  Tuất
 *   Row 3 (bottom): Dần  Sửu  Tý   Hợi
 *
 * Center 2×2 holds metadata (Mệnh, Cục, Đại Vận, etc.).
 */

import { computed, ref } from "vue";
import { castTuViLaSo } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import { saveCasting, activePerson } from "../stores/userDataStore.js";
import { isAuthenticated } from "../stores/authStore.js";
import PhuThaiViModal from "./PhuThaiViModal.vue";
import CachCucPanel from "./CachCucPanel.vue";
import DaiVanPanel from "./DaiVanPanel.vue";
import LuuNienPanel from "./LuuNienPanel.vue";
import TuViPersonSwitcher from "./TuViPersonSwitcher.vue";

const inputBirth = ref("");
const inputGender = ref("nam");
const inputTimezone = ref("Asia/Ho_Chi_Minh");
const inputTargetYear = ref(new Date().getFullYear());
const data = ref(null);
const interpretation = ref(null);
const luuTru = ref(null);
const cungReading = ref(null);  // ⭐ Q1 Phú + Q3 sao×cung per palace
const cungLoading = ref(false);
const caseStudies = ref(null);   // ⭐ Lá số mẫu lịch sử Q3+Q4
const caseLoading = ref(false);
const chartStrength = ref(null);  // ⭐ Miếu Vượng Hãm score (Q2 p0102)
const safetyCheck = ref(null);    // ⭐ Psychological safety patterns
const pheMenh = ref(null);        // ⭐ Phê mệnh phú thi (Q4 Khang Tiết)
const pheMenhLoading = ref(false);
const pheMenhSau = ref(null);     // ⭐ VIP1 — Luận giải sâu (DeepSeek Pro)
const pheMenhSauLoading = ref(false);
const collapsedSections = ref(new Set());  // ⭐ collapsible 10 sections phê mệnh sâu
const vipFeatures = ref(null);    // ⭐ VIP subscriptions for current user
const thienQuanArchetype = ref(null);  // ⭐ Q4 Thiên Quán 36 archetypes
const loading = ref(false);
const errorMsg = ref("");
const expandedPalace = ref(null);
const showPhuThaiVi = ref(false);  // Phú Thái Vi modal
const showCachCuc = ref(false);    // Cách cục đọc sâu modal
const showDaiVan = ref(false);     // 12 Đại Vận modal
const showLuuNien = ref(false);    // Lưu Niên 2026-2030 modal

useActivePersonBirth(inputBirth);

// Branch index → (row, col) in 4×4 grid (clockwise from Tỵ at top-left).
const BRANCH_TO_GRID = {
  5:  [0, 0],   // Tỵ
  6:  [0, 1],   // Ngọ
  7:  [0, 2],   // Mùi
  8:  [0, 3],   // Thân
  9:  [1, 3],   // Dậu
  10: [2, 3],   // Tuất
  11: [3, 3],   // Hợi
  0:  [3, 2],   // Tý
  1:  [3, 1],   // Sửu
  2:  [3, 0],   // Dần
  3:  [2, 0],   // Mão
  4:  [1, 0],   // Thìn
};

const HOA_LABEL = { "Lộc": "L", "Quyền": "Q", "Khoa": "K", "Kỵ": "K" };
const HOA_COLOR = Object.freeze({
  "Lộc":  "#5ab07a",
  "Quyền": "#e8c95a",
  "Khoa": "#5be5d3",
  "Kỵ":   "#d65a4a",
});

const BRANCH_NAMES = ['Tý','Sửu','Dần','Mão','Thìn','Tỵ','Ngọ','Mùi','Thân','Dậu','Tuất','Hợi'];

// Ngũ hành của 12 địa chi
const BRANCH_ELEMENT = ['Thủy','Thổ','Mộc','Mộc','Thổ','Hỏa','Hỏa','Thổ','Kim','Kim','Thổ','Thủy'];
const ELEMENT_COLOR  = { 'Thủy':'#60a5fa','Mộc':'#4ade80','Hỏa':'#f87171','Kim':'#fbbf24','Thổ':'#d97706' };

// Ngũ hành chính tinh (dùng để tô màu tên sao)
const CHINH_TINH_HANH = {
  'Tử Vi':'Thổ','Thiên Cơ':'Mộc','Thái Dương':'Hỏa','Vũ Khúc':'Kim','Thiên Đồng':'Thủy','Liêm Trinh':'Hỏa',
  'Thiên Phủ':'Thổ','Thái Âm':'Thủy','Tham Lang':'Mộc','Cự Môn':'Thủy','Thiên Tướng':'Thủy','Thiên Lương':'Thổ',
  'Thất Sát':'Kim','Phá Quân':'Thủy',
};

// Thiên Mã: năm chi → chi Thiên Mã
// Dần/Ngọ/Tuất→Thân(8), Thân/Tý/Thìn→Dần(2), Tỵ/Dậu/Sửu→Hợi(11), Hợi/Mão/Mùi→Tỵ(5)
const THIEN_MA_MAP = { 2:8, 6:8, 10:8, 8:2, 0:2, 4:2, 5:11, 9:11, 1:11, 11:5, 3:5, 7:5 };

async function castChart() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập sinh thần.";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const payload = {
      birth_datetime_local: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
      include_interpretation: true,
      target_year: inputTargetYear.value || null,
    };
    const resp = await fetch("/api/tu-vi/cast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json());
    data.value = resp.la_so;
    interpretation.value = resp.interpretation || null;
    luuTru.value = resp.luu_tru_year || null;

    // ⭐ Load Q1 Phú + Q3 sao×cung passages (background, non-blocking)
    loadCungReading();
    loadCaseStudies();
    loadChartStrength();
    loadSafetyCheck();
    loadThienQuanArchetype();
    loadVipFeatures();

    // Auto-save to user_castings (silent — only if logged in)
    if (isAuthenticated.value && resp.la_so) {
      const verdict = resp.la_so.menh_branch
        ? `Mệnh ${resp.la_so.menh_branch} · ${resp.la_so.cuc_name || ""} · ${resp.la_so.menh_chu || ""}`
        : "";
      saveCasting({
        method: "tu_vi",
        subject_person_key: activePerson.value?.person_key || null,
        question: null,
        input_json: payload,
        result_json: resp,
        verdict: verdict.trim() || null,
      });
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function reset() {
  data.value = null;
  interpretation.value = null;
  luuTru.value = null;
  cungReading.value = null;
  expandedPalace.value = null;
  errorMsg.value = "";
}

async function loadCungReading() {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  cungLoading.value = true;
  try {
    // Try cache first
    let resp = await fetch(`/api/tu-vi/analyze/${encodeURIComponent(personKey)}/cung_reading`)
      .then((r) => r.json());
    // If not cached, generate
    if (resp.status !== "ok") {
      resp = await fetch("/api/tu-vi/analyze/cung_reading", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ person_key: personKey }),
      }).then((r) => r.json());
    }
    if (resp.status === "ok") {
      cungReading.value = resp;
    }
  } catch (e) {
    console.error("loadCungReading failed:", e);
  } finally {
    cungLoading.value = false;
  }
}

async function loadPheMenh(force = false) {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  pheMenhLoading.value = true;
  try {
    // Try cache first
    let resp = await fetch(`/api/tu-vi/analyze/${encodeURIComponent(personKey)}/phe_menh`)
      .then((r) => r.json());
    if (resp.status !== "ok" || force) {
      resp = await fetch("/api/tu-vi/analyze/phe_menh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ person_key: personKey, force }),
      }).then((r) => r.json());
    }
    if (resp.status === "ok") pheMenh.value = resp;
    else pheMenh.value = { error: resp.message || "Tạo phê mệnh thất bại" };
  } catch (e) {
    pheMenh.value = { error: String(e.message || e) };
  } finally {
    pheMenhLoading.value = false;
  }
}

async function loadVipFeatures() {
  try {
    const resp = await fetch("/api/user/my-vip-features").then((r) => r.json());
    if (resp.status === "ok") vipFeatures.value = resp;
  } catch (e) { /* silent */ }
}

function vipFeatureStatus(featureId) {
  if (!vipFeatures.value) return { hasAccess: false };
  const sub = (vipFeatures.value.subscriptions || []).find((s) => s.feature_id === featureId);
  if (!sub) return { hasAccess: false, reason: "no_subscription" };
  if (!sub.enabled) return { hasAccess: false, reason: "disabled", subscription: sub };
  const now = Math.floor(Date.now() / 1000);
  if (sub.expires_at && now > sub.expires_at) return { hasAccess: false, reason: "expired", subscription: sub };
  if (sub.remaining_uses !== null && sub.remaining_uses <= 0) return { hasAccess: false, reason: "no_uses_left", subscription: sub };
  return { hasAccess: true, subscription: sub };
}

async function loadPheMenhSau(force = false) {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  pheMenhSauLoading.value = true;
  try {
    let resp = await fetch(`/api/tu-vi/analyze/${encodeURIComponent(personKey)}/phe_menh_sau`).then((r) => r.json()).catch(() => ({status:"not_cached"}));
    if (resp.status !== "ok" || force) {
      resp = await fetch("/api/tu-vi/phe-menh-sau", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ person_key: personKey, force }),
      }).then((r) => r.json());
    }
    if (resp.status === "ok") {
      pheMenhSau.value = resp;
      loadVipFeatures(); // reload to update remaining_uses
    } else {
      pheMenhSau.value = { error: resp.message || resp.detail || "Tạo phê mệnh sâu thất bại" };
    }
  } catch (e) {
    pheMenhSau.value = { error: String(e.message || e) };
  } finally {
    pheMenhSauLoading.value = false;
  }
}

// ⭐ Phê mệnh sâu UI helpers — collapse / copy / format markdown 3-layer
function togglePmsSection(key) {
  const s = collapsedSections.value;
  if (s.has(key)) {
    s.delete(key);
  } else {
    s.add(key);
  }
  collapsedSections.value = new Set(s);  // trigger reactivity
}

async function copyPmsSection(key, content) {
  try {
    const title = {
      dinh_thoi_khac: "1. Định thời khắc",
      khoi_bat_tu: "2. Khởi Bát Tự",
      lap_cach_dung_than: "3. Lập cách · Dụng thần",
      bai_tinh_than: "4. Bài tinh thần",
      lap_toa_menh: "5. Lập tọa Mệnh",
      dai_van_phan_tich: "6. Đại Vận phân tích",
      dai_han_luu_nien: "7. Đại Hạn + Lưu Niên",
      tu_hoa_dien_giai: "8. Tứ Hóa diễn giải",
      hi_ky_canh_bao: "9. Hỉ kỵ + Cảnh báo",
      ket_tam_an: "10. Kết tâm an",
    }[key] || key;
    await navigator.clipboard.writeText(`## ${title}\n\n${content}`);
  } catch (e) {
    console.warn("Copy failed", e);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/** Format markdown 3-layer cho phê mệnh sâu output.
 * - Lines bắt đầu "📜 Cổ huấn" hoặc "📜 ..." → blockquote class pms-classical
 * - Lines bắt đầu "📜 Dịch nghĩa" → italic translation
 * - "**...**" → <strong>
 * - "_..._" → <em>
 * - Hán-Việt term in (...) → highlight
 * - Paragraph breaks on \n\n
 */
function formatPmsContent(text) {
  if (!text || typeof text !== "string") return "";
  let html = escapeHtml(text);
  // Bold **...**
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  // Italic _..._
  html = html.replace(/(^|\s)_([^_\n]+)_/g, "$1<em>$2</em>");
  // Highlight giải nghĩa Hán-Việt: pattern (Xxx — yyy) hoặc (Xxx, yyy)
  html = html.replace(/\(([A-ZÀ-Ỹ][^()]{2,80})\)/g, '<span class="pms-gloss">($1)</span>');
  // Split into paragraphs
  const paragraphs = html.split(/\n\n+/);
  const out = [];
  for (const para of paragraphs) {
    const trimmed = para.trim();
    if (!trimmed) continue;
    // Check if paragraph is "📜 ..." — classical block
    if (trimmed.startsWith("📜")) {
      // Detect Dịch nghĩa vs Cổ huấn
      const isDichNghia = trimmed.includes("Dịch nghĩa") || trimmed.includes("dịch nghĩa");
      out.push(`<blockquote class="${isDichNghia ? 'pms-translation' : 'pms-classical'}">${trimmed.replace(/\n/g, "<br/>")}</blockquote>`);
    } else if (/^[A-ZÀ-Ỹ][^\n]{2,40}:?$/m.test(trimmed.split("\n")[0]) && trimmed.split("\n")[0].length < 60) {
      // Possible heading-like line
      const lines = trimmed.split("\n");
      const head = lines[0];
      const rest = lines.slice(1).join("\n");
      out.push(`<p class="pms-subhead"><strong>${head}</strong></p>`);
      if (rest.trim()) {
        out.push(`<p>${rest.replace(/\n/g, "<br/>")}</p>`);
      }
    } else {
      out.push(`<p>${trimmed.replace(/\n/g, "<br/>")}</p>`);
    }
  }
  return out.join("\n");
}

async function loadThienQuanArchetype() {
  // Use birth_datetime_local to derive hour + khắc
  if (!data.value) return;
  const birth = inputBirth.value;
  if (!birth) return;
  // Parse hour from birth — heuristic khắc by minute
  const time = birth.split("T")[1] || "";
  const [hh, mm] = time.split(":").map(Number);
  if (isNaN(hh)) return;
  // Map hour → chi (rough): 23-1=Tý, 1-3=Sửu, ...
  const hourBranches = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"];
  let hourIdx;
  if (hh === 23 || hh === 0) hourIdx = 0;
  else hourIdx = Math.floor((hh + 1) / 2) % 12;
  const hour = hourBranches[hourIdx];
  // Khắc by minute: 0-19 thượng, 20-39 trung, 40-59 hạ
  const khac = mm < 20 ? "thượng" : mm < 40 ? "trung" : "hạ";
  try {
    const resp = await fetch(`/api/tu-vi/q4/thien-quan-archetype/${encodeURIComponent(hour)}/${encodeURIComponent(khac)}`)
      .then((r) => r.json());
    if (resp.status === "ok") {
      thienQuanArchetype.value = { ...resp.archetype, hour, khac };
    }
  } catch (e) { /* silent */ }
}

async function loadSafetyCheck() {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  try {
    const resp = await fetch("/api/tu-vi/safety-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_key: personKey }),
    }).then((r) => r.json());
    if (resp.status === "ok") safetyCheck.value = resp;
  } catch (e) { /* silent */ }
}

async function loadChartStrength() {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  try {
    const resp = await fetch("/api/tu-vi/chart-strength", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_key: personKey }),
    }).then((r) => r.json());
    if (resp.status === "ok") chartStrength.value = resp;
  } catch (e) { console.error("loadChartStrength failed:", e); }
}

async function loadCaseStudies() {
  const personKey = activePerson.value?.person_key;
  if (!personKey) return;
  caseLoading.value = true;
  try {
    const resp = await fetch("/api/tu-vi/case-studies/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_key: personKey }),
    }).then((r) => r.json());
    if (resp.status === "ok") {
      caseStudies.value = resp;
    }
  } catch (e) {
    console.error("loadCaseStudies failed:", e);
  } finally {
    caseLoading.value = false;
  }
}

function formatSolarDateTime(iso) {
  if (!iso) return "";
  const [d, t] = iso.split("T");
  if (!d) return iso;
  const [y, m, day] = d.split("-");
  const time = (t || "").slice(0, 5);
  return time ? `${day}/${m}/${y} ${time}` : `${day}/${m}/${y}`;
}

// Đại Vận lookup: branch_index → cycle info {start_age, end_age, cycle_index}
const dvByBranch = computed(() => {
  if (!data.value) return {};
  const out = {};
  for (const c of data.value.dai_van) out[c.branch_index] = c;
  return out;
});

// Thiên Mã branch index (từ năm chi)
const thienMaBranch = computed(() => {
  if (!data.value) return null;
  const idx = BRANCH_NAMES.indexOf(data.value.year_branch);
  return idx >= 0 ? THIEN_MA_MAP[idx] : null;
});

// ── Derived: build per-cell content (palace info + stars at that branch).
const cellByBranch = computed(() => {
  if (!data.value) return {};
  const out = {};
  for (let i = 0; i < 12; i++) out[i] = { palace: null, chinh: [], phu: [], sat: [], hoa: [] };

  // Palace assignment.
  for (const p of data.value.palaces) {
    out[p.branch_index].palace = p;
  }

  // Star → branch reverse maps.
  const stars = data.value.chinh_tinh;
  const phu = data.value.phu_tinh;
  const sat = data.value.sat_tinh;
  const tuhoa = data.value.tu_hoa;
  // Star name → hoa label
  const starHoa = {};
  for (const [hoa, star] of Object.entries(tuhoa)) {
    starHoa[star] = hoa;
  }

  for (const [name, idx] of Object.entries(stars)) {
    const hoa = starHoa[name];
    out[idx].chinh.push({ name, hoa });
  }
  for (const [name, idx] of Object.entries(phu)) {
    const hoa = starHoa[name];
    out[idx].phu.push({ name, hoa });
  }
  for (const [name, idx] of Object.entries(sat)) {
    out[idx].sat.push({ name });
  }
  // Thiên Mã (computed từ năm chi)
  if (thienMaBranch.value !== null) {
    out[thienMaBranch.value].sat.push({ name: 'Thiên Mã' });
  }

  // Q2 sao bộ — thâm nhuần Quyển 2 (12 sao Thái Tuế + 10 sao phụ)
  // Init q2 array per cell
  for (let i = 0; i < 12; i++) out[i].q2 = out[i].q2 || [];
  const thaiTueBelt = data.value.thai_tue_belt || {};
  for (const [name, idx] of Object.entries(thaiTueBelt)) {
    out[idx].q2.push({ name, group: "thai_tue" });
  }
  const saoQ2 = data.value.sao_q2 || {};
  for (const [name, idx] of Object.entries(saoQ2)) {
    out[idx].q2.push({ name, group: "phu_q2" });
  }

  return out;
});

const grid = computed(() => {
  if (!data.value) return [];
  // 4x4 grid: each cell is either { type: 'palace', cell: ... } or { type: 'center' }.
  const out = Array.from({ length: 4 }, () => Array(4).fill(null));
  for (const [branchIdx, [r, c]] of Object.entries(BRANCH_TO_GRID)) {
    out[r][c] = { type: "palace", branchIndex: +branchIdx, ...cellByBranch.value[+branchIdx] };
  }
  // Center 2x2:
  out[1][1] = { type: "center-tl" };
  out[1][2] = { type: "center-tr" };
  out[2][1] = { type: "center-bl" };
  out[2][2] = { type: "center-br" };
  return out;
});
</script>

<template>
  <section class="panel tvls-panel">
    <div class="panel-title">
      <span>Tử Vi Lá Số — An Sao Bắc Phái</span>
      <small>{{ data?.method_id || "tu_vi_an_sao_bac_phai_v1" }}</small>
    </div>

    <p class="intro-note">
      Lá số Tử Vi đầy đủ: <b>14 chính tinh + 6 phụ tinh + 7 sát tinh + Tứ Hóa</b> đặt vào
      <b>12 cung</b> dựa trên Thiên Can năm, tháng âm, ngày âm, giờ sinh. Engine tham chiếu
      <em>iztro (MIT)</em> + sách Tử Vi Sài Gòn / xemtuong.net.
    </p>

    <TuViPersonSwitcher />

    <div class="tvls-form">
      <label>
        <span>Sinh thần</span>
        <input v-model="inputBirth" type="datetime-local" />
      </label>
      <label>
        <span>Giới tính</span>
        <select v-model="inputGender">
          <option value="nam">TA Nam</option>
          <option value="nữ">TA Nữ</option>
        </select>
      </label>
      <label>
        <span>Múi giờ</span>
        <input v-model="inputTimezone" type="text" />
      </label>
      <label>
        <span>Năm xem vận (lưu trú)</span>
        <input v-model.number="inputTargetYear" type="number" min="1900" max="2100" />
      </label>
      <div class="tvls-actions">
        <button class="apply-btn" @click="castChart" :disabled="loading">
          {{ loading ? "Đang an sao..." : "An sao lá số" }}
        </button>
        <button v-if="data" class="secondary-btn" @click="reset" type="button">✕ An lại</button>
        <button class="phu-btn" type="button" @click="showPhuThaiVi = true"
                title="Đọc Phú Thái Vi — nền tảng học thuyết Tử Vi Đẩu Số (Trần Đoàn)">
          📜 Phú Thái Vi
        </button>
        <button class="cach-cuc-btn" type="button" @click="showCachCuc = true"
                title="Cách cục lá số anh + đối chiếu vợ chồng — phân tích đọc sâu">
          🪐 Cách cục đọc sâu
        </button>
        <button class="dai-van-btn" type="button" @click="showDaiVan = true"
                title="12 Đại Vận của anh — từ 5 tuổi đến 124 tuổi, mỗi vận 10 năm">
          🌗 12 Đại Vận
        </button>
        <button class="luu-nien-btn" type="button" @click="showLuuNien = true"
                title="Vận năm 2026-2030 chi tiết (Đại Vận + Tiểu Hạn kết hợp)">
          📅 Lưu Niên 5 năm
        </button>
      </div>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <!-- ── Lá số 4×4 grid ─────────────────────────────────────────── -->
    <template v-if="data">
      <!-- Sinh thần dương + âm -->
      <div class="tv-birth-summary">
        <span class="tv-bs-item">
          <span class="tv-bs-label">☀ Dương</span>
          <span class="tv-bs-val">{{ formatSolarDateTime(inputBirth) }}</span>
        </span>
        <span class="tv-bs-item">
          <span class="tv-bs-label">🌙 Âm</span>
          <span class="tv-bs-val">
            ngày {{ data.lunar_day }} tháng {{ data.lunar_month }} năm {{ data.year_stem }} {{ data.year_branch }}
          </span>
        </span>
        <span class="tv-bs-item">
          <span class="tv-bs-label">⏰ Giờ</span>
          <span class="tv-bs-val">{{ data.hour_branch }} ({{ data.gender }})</span>
        </span>
      </div>

      <div class="laso-grid">
        <template v-for="(row, r) in grid" :key="r">
          <div
            v-for="(cell, c) in row"
            :key="`${r}-${c}`"
            class="laso-cell"
            :class="{
              center: cell.type?.startsWith('center'),
              [`pos-${cell.branchIndex}`]: cell.type === 'palace',
              'is-menh': cell.palace?.name === 'Mệnh',
              'is-than': cell.branchIndex === data.than_index,
            }"
          >
            <template v-if="cell.type === 'palace'">
              <!-- Header: element chip · branch — palace name — DV age -->
              <header class="cell-head">
                <div class="cell-head-left">
                  <span class="elem-chip"
                    :style="{ background: ELEMENT_COLOR[BRANCH_ELEMENT[cell.branchIndex]] + '30',
                              color: ELEMENT_COLOR[BRANCH_ELEMENT[cell.branchIndex]],
                              borderColor: ELEMENT_COLOR[BRANCH_ELEMENT[cell.branchIndex]] + '60' }">
                    {{ BRANCH_ELEMENT[cell.branchIndex][0] }}
                  </span>
                  <span class="cell-branch">{{ BRANCH_NAMES[cell.branchIndex] }}</span>
                </div>
                <span class="cell-palace"
                  :class="{ 'is-menh-label': cell.palace?.name === 'Mệnh',
                             'is-than-label': cell.branchIndex === data.than_index && cell.palace?.name !== 'Mệnh' }">
                  {{ cell.palace?.name }}
                  <span v-if="cell.palace?.name === 'Mệnh' && cell.branchIndex === data.than_index"> ·身</span>
                </span>
                <span v-if="dvByBranch[cell.branchIndex]" class="dv-age-badge">
                  {{ dvByBranch[cell.branchIndex].start_age }}
                </span>
              </header>

              <!-- Chính tinh — lớn, có màu ngũ hành -->
              <ul class="stars chinh">
                <li v-for="s in cell.chinh" :key="s.name" class="star chinh-tinh"
                    :style="{ color: ELEMENT_COLOR[CHINH_TINH_HANH[s.name]] || '#f5e6b1' }">
                  {{ s.name }}
                  <span v-if="s.hoa" class="hoa-badge"
                    :style="{ background: HOA_COLOR[s.hoa] + '33', color: HOA_COLOR[s.hoa], borderColor: HOA_COLOR[s.hoa] }">
                    {{ s.hoa[0] }}
                  </span>
                </li>
              </ul>

              <!-- Phụ tinh + sát tinh + q2 — nhỏ hơn, gộp nhau -->
              <ul v-if="cell.phu.length" class="stars phu">
                <li v-for="s in cell.phu" :key="s.name" class="star phu-tinh">
                  {{ s.name }}
                  <span v-if="s.hoa" class="hoa-badge"
                    :style="{ background: HOA_COLOR[s.hoa] + '33', color: HOA_COLOR[s.hoa] }">
                    {{ s.hoa[0] }}
                  </span>
                </li>
              </ul>
              <ul v-if="cell.sat.length" class="stars sat">
                <li v-for="s in cell.sat" :key="s.name" class="star sat-tinh"
                    :class="{ 'loc-ton': s.name === 'Lộc Tồn', 'thien-ma': s.name === 'Thiên Mã' }">
                  {{ s.name }}
                </li>
              </ul>
              <ul v-if="cell.q2?.length" class="stars q2">
                <li v-for="s in cell.q2" :key="s.name"
                    :class="['star','q2-tinh', s.group === 'thai_tue' ? 'thai-tue' : 'phu-q2']">
                  {{ s.name }}
                </li>
              </ul>

              <!-- Footer badges -->
              <div class="cell-foot">
                <span v-if="cell.palace?.name === 'Mệnh'" class="menh-mark">★ MỆNH</span>
                <span v-if="cell.branchIndex === data.than_index && cell.palace?.name !== 'Mệnh'" class="than-mark">身 THÂN</span>
                <span v-if="cell.branchIndex === data.dau_quan_index" class="dauquan-mark"
                      title="Đẩu Quân — sao tháng sinh">斗</span>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-tl'">
              <div class="center-info center-title">
                <div class="ct-logo">紫微</div>
                <div class="ct-sub">Tử Vi Đẩu Số · Bắc Phái</div>
                <div class="ct-cuc">{{ data.cuc_name }}</div>
                <div class="ct-row">
                  <span class="ci-label">Mệnh</span>
                  <b>{{ data.menh_branch }}</b>
                  <span class="ci-label" style="margin-left:8px">Thân</span>
                  <b>{{ data.than_branch }}</b>
                </div>
                <div class="ct-row" v-if="data.menh_chu">
                  <span class="ci-label">Mệnh chủ</span>
                  <b>{{ data.menh_chu }}</b>
                </div>
                <div class="ct-row" v-if="data.than_chu">
                  <span class="ci-label">Thân chủ</span>
                  <b>{{ data.than_chu }}</b>
                </div>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-tr'">
              <div class="center-info">
                <div class="ci-row">
                  <span class="ci-label">Năm</span>
                  <span>{{ data.year_stem }} {{ data.year_branch }}</span>
                </div>
                <div class="ci-row">
                  <span class="ci-label">Tháng âm</span>
                  <span>{{ data.lunar_month }}</span>
                </div>
                <div class="ci-row">
                  <span class="ci-label">Ngày âm</span>
                  <span>{{ data.lunar_day }}</span>
                </div>
                <div class="ci-row">
                  <span class="ci-label">Giờ</span>
                  <span>{{ data.hour_branch }} · {{ data.gender }}</span>
                </div>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-bl'">
              <div class="center-info center-hoa">
                <div class="ci-hoa-title">Tứ Hóa năm {{ data.year_stem }}</div>
                <div class="hoa-line" v-for="(star, hoa) in data.tu_hoa" :key="hoa">
                  <span class="hoa-tag" :style="{ background: HOA_COLOR[hoa] + '30', color: HOA_COLOR[hoa], borderColor: HOA_COLOR[hoa] + '60' }">
                    {{ hoa }}
                  </span>
                  <em>{{ star }}</em>
                </div>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-br'">
              <div class="center-info center-dv-mini">
                <div class="ci-hoa-title">Đại Vận</div>
                <div v-for="c in data.dai_van.slice(0, 6)" :key="c.cycle_index"
                  class="dv-mini-row"
                  :class="{ 'dv-current': luuTru && luuTru.dai_han_cycle?.cycle_index === c.cycle_index }">
                  <span class="dv-mini-age">{{ c.start_age }}</span>
                  <span class="dv-mini-branch">{{ c.branch }}</span>
                </div>
              </div>
            </template>
          </div>
        </template>
      </div>

      <!-- ── Đại Vận strip ────────────────────────────────────── -->
      <h4 class="section-h">Đại Vận — chu kỳ 10 năm</h4>
      <ol class="dv-list">
        <li v-for="c in data.dai_van.slice(0, 10)" :key="c.cycle_index" class="dv-cell"
          :class="{ 'is-current': luuTru && luuTru.dai_han_cycle.cycle_index === c.cycle_index }">
          <strong>V{{ c.cycle_index }}</strong>
          <span class="dv-branch">{{ c.branch }}</span>
          <small>{{ c.start_age }}–{{ c.end_age }}t</small>
        </li>
      </ol>

      <!-- ── Lưu Trú Sao (target year transit) ───────────────────── -->
      <template v-if="luuTru">
        <h4 class="section-h">Lưu Trú Sao — vận năm {{ luuTru.target_year }} ({{ luuTru.target_stem }} {{ luuTru.target_branch }})</h4>
        <div class="luu-tru-card">
          <div class="lt-row">
            <div class="lt-cell">
              <span class="lt-label">Tuổi tại năm</span>
              <strong>{{ luuTru.age_at_year }}</strong>
            </div>
            <div class="lt-cell">
              <span class="lt-label">Đại Vận hiện tại</span>
              <strong>V{{ luuTru.dai_han_cycle.cycle_index }} · {{ luuTru.dai_han_cycle.branch }}</strong>
              <small>vị trí {{ luuTru.dai_han_intra_cung + 1 }}/10</small>
            </div>
            <div class="lt-cell">
              <span class="lt-label">Tiểu Hạn</span>
              <strong>{{ luuTru.tieu_han_branch }}</strong>
            </div>
          </div>

          <h6 class="lt-h">Lưu Tứ Hóa — năm {{ luuTru.target_year }}</h6>
          <ul class="lt-hoa-list">
            <li v-for="(star, hoa) in luuTru.luu_tu_hoa" :key="hoa"
              class="lt-hoa-item" :style="{ borderColor: HOA_COLOR[hoa] }">
              <span class="lt-hoa-tag" :style="{ background: HOA_COLOR[hoa] + '33', color: HOA_COLOR[hoa] }">
                Lưu {{ hoa }}
              </span>
              <em>{{ star }}</em>
            </li>
          </ul>

          <h6 class="lt-h">Lưu sao theo Thiên Can năm {{ luuTru.target_stem }}</h6>
          <div class="lt-stars-grid">
            <div class="lt-star-cell"><span>Lưu Lộc Tồn</span><b>{{ luuTru.luu_loc_ton }}</b></div>
            <div class="lt-star-cell"><span>Lưu Kình Dương</span><b>{{ luuTru.luu_kinh_duong }}</b></div>
            <div class="lt-star-cell"><span>Lưu Đà La</span><b>{{ luuTru.luu_da_la }}</b></div>
            <div class="lt-star-cell"><span>Lưu Thiên Khôi</span><b>{{ luuTru.luu_thien_khoi }}</b></div>
            <div class="lt-star-cell"><span>Lưu Thiên Việt</span><b>{{ luuTru.luu_thien_viet }}</b></div>
          </div>
        </div>
      </template>

      <!-- ── Safety Check (Q1+Q3 dark warnings → gentle self-care) ─── -->
      <template v-if="safetyCheck && safetyCheck.patterns_triggered?.length">
        <section class="safety-block">
          <header class="sb-head">
            <h4>💚 Lưu ý chăm sóc bản thân</h4>
            <small>Iron Rule #6 — KHÔNG predict, chỉ là "dấu hiệu kích hoạt nhận thức"</small>
          </header>
          <div v-for="p in safetyCheck.patterns_triggered" :key="p.id" class="sb-pattern">
            <header class="sb-pattern-head">
              <strong>{{ p.title }}</strong>
              <small>{{ p.source }}</small>
            </header>
            <p class="sb-gentle">{{ p.gentle_message }}</p>
            <div v-if="p.which_dai_van?.length" class="sb-when">
              <small>Khi nào cần chú ý:</small>
              <ul>
                <li v-for="(d, di) in p.which_dai_van" :key="di">{{ d }}</li>
              </ul>
            </div>
            <div class="sb-tips">
              <small>Gợi ý chăm sóc:</small>
              <ul>
                <li v-for="(t, ti) in p.self_care_tips" :key="ti">{{ t }}</li>
              </ul>
            </div>
            <details class="sb-source">
              <summary>Câu sách gốc</summary>
              <em>« {{ p.key_phrase_hv }} »</em>
              <small>{{ p.key_phrase_zh }}</small>
            </details>
          </div>
          <p class="sb-paradigm">💡 {{ safetyCheck.note }}</p>
        </section>
      </template>

      <!-- ── Chart Strength (Q2 p0102 Miếu Vượng Hãm) ────────────── -->
      <template v-if="chartStrength">
        <section class="chart-strength-block">
          <header class="cs-head">
            <h4>⚖️ Sức mạnh tổng thể lá số (Miếu Vượng Hãm)</h4>
            <small class="cs-source">{{ chartStrength.source }}</small>
          </header>
          <div class="cs-score-row">
            <div class="cs-total" :class="{
              'cs-strong': chartStrength.total_score >= 15,
              'cs-balanced': chartStrength.total_score >= 0 && chartStrength.total_score < 15,
              'cs-weak': chartStrength.total_score < 0,
            }">
              <span class="cs-num">{{ chartStrength.total_score > 0 ? '+' : '' }}{{ chartStrength.total_score }}</span>
              <span class="cs-verdict">{{ chartStrength.verdict }}</span>
            </div>
          </div>
          <div class="cs-grid">
            <div v-for="s in chartStrength.stars" :key="s.star" class="cs-star-cell"
                 :style="{ borderLeftColor: s.color }">
              <span class="cs-star-name">{{ s.star }}</span>
              <span class="cs-star-meta">{{ s.branch }} · <b :style="{ color: s.color }">{{ s.level }}</b></span>
              <span class="cs-star-score" :style="{ color: s.color }">
                {{ s.score > 0 ? '+' : '' }}{{ s.score }}
              </span>
            </div>
          </div>
        </section>
      </template>

      <!-- ── Q4 Thiên Quán Archetype (36 archetypes typology — chỉ giờ sinh) ── -->
      <template v-if="thienQuanArchetype">
        <section class="tq-archetype-block">
          <header class="tq-head">
            <h4>🎭 Archetype Thiên Quán Phân Cung — Q4 p0268-p0271</h4>
            <small>Giờ {{ thienQuanArchetype.hour }} · khắc {{ thienQuanArchetype.khac }}</small>
          </header>
          <div class="tq-body">
            <div class="tq-cung-name">
              <span class="tq-label">Cung archetype:</span>
              <strong>{{ thienQuanArchetype.cung_name }}</strong>
            </div>
            <p v-if="thienQuanArchetype.summary_vi" class="tq-summary">
              📜 {{ thienQuanArchetype.summary_vi }}
            </p>
            <details class="tq-detail">
              <summary>Chi tiết archetype (theo cổ kinh)</summary>
              <ul>
                <li v-if="thienQuanArchetype.khac_phu_mau"><b>Khắc phụ mẫu:</b> {{ thienQuanArchetype.khac_phu_mau }}</li>
                <li v-if="thienQuanArchetype.luc_than"><b>Lục thân:</b> {{ thienQuanArchetype.luc_than }}</li>
                <li v-if="thienQuanArchetype.su_nghiep"><b>Sự nghiệp:</b> {{ thienQuanArchetype.su_nghiep }}</li>
                <li v-if="thienQuanArchetype.y_loc"><b>Y lộc:</b> {{ thienQuanArchetype.y_loc }}</li>
                <li v-if="thienQuanArchetype.to_nghiep"><b>Tổ nghiệp:</b> {{ thienQuanArchetype.to_nghiep }}</li>
                <li v-if="thienQuanArchetype.tu_tuc"><b>Tử tức:</b> {{ thienQuanArchetype.tu_tuc }}</li>
                <li v-if="thienQuanArchetype.tinh_cach"><b>Tính cách:</b> {{ thienQuanArchetype.tinh_cach }}</li>
                <li v-if="thienQuanArchetype.khuyen"><b>Khuyên:</b> {{ thienQuanArchetype.khuyen }}</li>
                <li><b>Nguồn:</b> {{ thienQuanArchetype.source_ref }}</li>
              </ul>
            </details>
            <p class="tq-iron-rule">⚠ {{ thienQuanArchetype.iron_rule_note }}</p>
          </div>
        </section>
      </template>

      <!-- ── Phê Mệnh (Q4 Khang Tiết Edition — phú thi + "mỗ" pattern) ── -->
      <section class="phe-menh-block">
        <header class="pm-head">
          <h4>📜 Phê mệnh phú thi (Q4 Khang Tiết Edition)</h4>
          <div class="pm-actions">
            <small v-if="pheMenh?.provider" class="pm-meta">via {{ pheMenh.provider }} · {{ (pheMenh.tokens?.prompt + pheMenh.tokens?.completion).toLocaleString() }} tokens</small>
            <button v-if="!pheMenh && !pheMenhLoading" class="pm-btn" @click="loadPheMenh(false)">
              ✨ Tạo phê mệnh
            </button>
            <button v-if="pheMenh && !pheMenh.error && !pheMenhLoading" class="pm-btn pm-regen" @click="loadPheMenh(true)">
              🔄 Viết lại
            </button>
          </div>
        </header>

        <p v-if="!pheMenh && !pheMenhLoading" class="pm-intro">
          Phê mệnh viết theo phong cách Q4 Tử Vi Đẩu Số Toàn Thư — phú thi 4-7 chữ + ẩn dụ + <b>"mỗ" pattern</b>
          (gợi mở, KHÔNG predict). Tổ sư Trần Đoàn + Khang Tiết đồng tác. ~26 giây + miễn phí qua MiniMax.
        </p>

        <p v-if="pheMenhLoading" class="pm-loading">
          ⏳ Đang viết phê mệnh... (~30 giây, em đang gọi Tổ sư)
        </p>

        <p v-if="pheMenh?.error" class="pm-error">⚠ {{ pheMenh.error }}</p>

        <div v-if="pheMenh?.phe_menh && !pheMenh.error" class="pm-content">
          <article v-if="pheMenh.phe_menh.khai_de" class="pm-section pm-khai-de">
            <h5>🌅 Khai đề</h5>
            <p>{{ pheMenh.phe_menh.khai_de }}</p>
          </article>
          <article v-if="pheMenh.phe_menh.menh_than" class="pm-section pm-menh-than">
            <h5>🪞 Mệnh & Thân (CƠ — Trần Đoàn)</h5>
            <p>{{ pheMenh.phe_menh.menh_than }}</p>
          </article>
          <article v-if="pheMenh.phe_menh.dai_van" class="pm-section pm-dai-van">
            <h5>🌊 Đại Vận biến hoá (BIẾN — Khang Tiết, "mỗ" pattern)</h5>
            <p>{{ pheMenh.phe_menh.dai_van }}</p>
          </article>
          <article v-if="pheMenh.phe_menh.canh_bao" class="pm-section pm-canh-bao">
            <h5>💚 Lưu ý chăm sóc (Q3 safety)</h5>
            <p>{{ pheMenh.phe_menh.canh_bao }}</p>
          </article>
          <article v-if="pheMenh.phe_menh.ket_tam_an" class="pm-section pm-tam-an">
            <h5>🌸 Kết — Tâm an</h5>
            <p>{{ pheMenh.phe_menh.ket_tam_an }}</p>
          </article>
          <p v-if="pheMenh.paradigm_note" class="pm-paradigm">💡 {{ pheMenh.paradigm_note }}</p>
        </div>
      </section>

      <!-- ── Luận giải SÂU (VIP1 DeepSeek Pro — 10 sections theo 10 bước) ── -->
      <section class="phe-menh-sau-block">
        <header class="pms-head">
          <h4>🌟 Luận giải SÂU — VIP DeepSeek Pro · 10 bước Trần Đoàn</h4>
          <div class="pms-status">
            <template v-if="vipFeatureStatus('tu_vi_phe_menh_sau').hasAccess">
              <span class="pms-badge pms-vip">✓ VIP1</span>
              <small v-if="vipFeatureStatus('tu_vi_phe_menh_sau').subscription?.remaining_uses !== null" class="pms-remaining">
                Còn {{ vipFeatureStatus('tu_vi_phe_menh_sau').subscription.remaining_uses }} lượt
              </small>
              <small v-if="vipFeatureStatus('tu_vi_phe_menh_sau').subscription?.expires_at" class="pms-expires">
                Hết hạn: {{ new Date(vipFeatureStatus('tu_vi_phe_menh_sau').subscription.expires_at * 1000).toLocaleDateString('vi-VN') }}
              </small>
            </template>
            <template v-else>
              <span class="pms-badge pms-locked">🔒 Cần VIP1</span>
            </template>
          </div>
        </header>

        <p class="pms-intro">
          Phê mệnh SÂU theo <b>10 bước methodology Trần Đoàn</b> (Q4 p0266) — depth gấp 3 lần phê mệnh free tier.
          Dùng <b>DeepSeek Pro</b> với context đầy đủ Q1+Q2+Q3+Q4 + cách cục + case lịch sử + Chiếu Đởm Kinh.
          ~60 giây · ~$0.05/lượt.
        </p>

        <template v-if="!vipFeatureStatus('tu_vi_phe_menh_sau').hasAccess">
          <div class="pms-locked-msg">
            <p>🔒 <b>Tính năng VIP1</b> — anh chưa có quyền dùng. Liên hệ admin để được cấp.</p>
            <p v-if="vipFeatureStatus('tu_vi_phe_menh_sau').reason === 'expired'" class="pms-locked-reason">
              ⏰ Subscription đã hết hạn.
            </p>
            <p v-else-if="vipFeatureStatus('tu_vi_phe_menh_sau').reason === 'no_uses_left'" class="pms-locked-reason">
              💧 Hết lượt dùng.
            </p>
            <p v-else-if="vipFeatureStatus('tu_vi_phe_menh_sau').reason === 'disabled'" class="pms-locked-reason">
              ⏸ Tạm dừng bởi admin.
            </p>
          </div>
        </template>

        <template v-else>
          <div class="pms-actions">
            <button v-if="!pheMenhSau && !pheMenhSauLoading" class="pms-btn" @click="loadPheMenhSau(false)">
              🌟 Tạo luận giải SÂU
            </button>
            <button v-if="pheMenhSau && !pheMenhSau.error && !pheMenhSauLoading" class="pms-btn pms-regen" @click="loadPheMenhSau(true)">
              🔄 Viết lại (-1 lượt)
            </button>
          </div>

          <p v-if="pheMenhSauLoading" class="pms-loading">
            ⏳ Đang viết phê mệnh SÂU... (~60s — DeepSeek đọc cả Q1+Q2+Q3+Q4 + lá số anh)
          </p>

          <p v-if="pheMenhSau?.error" class="pms-error">⚠ {{ pheMenhSau.error }}</p>

          <div v-if="pheMenhSau?.phe_menh_sau && !pheMenhSau.error" class="pms-content">
            <div class="pms-meta">
              <small>
                via {{ pheMenhSau.provider }}
                · {{ (pheMenhSau.tokens?.total || (pheMenhSau.tokens?.prompt + pheMenhSau.tokens?.completion) || 0).toLocaleString() }} tokens
                · ${{ (pheMenhSau.cost_usd || 0).toFixed(4) }}
                · {{ Math.round(pheMenhSau.avg_length_chars || 0).toLocaleString() }} chars/section avg
                · <span v-if="pheMenhSau.wiki_extracted?.added_quotes >= 0">
                    📚 +{{ pheMenhSau.wiki_extracted.added_quotes }} phú, +{{ pheMenhSau.wiki_extracted.added_cach_cuc }} cách → wiki
                  </span>
              </small>
            </div>
            <article v-for="(content, key) in pheMenhSau.phe_menh_sau" :key="key"
                     v-show="!key.startsWith('_')"
                     class="pms-section" :class="{ 'pms-collapsed': collapsedSections.has(key) }">
              <header class="pms-section-header" @click="togglePmsSection(key)">
                <h5>{{ {
                  dinh_thoi_khac: '1️⃣ Định thời khắc',
                  khoi_bat_tu: '2️⃣ Khởi Bát Tự (Tứ Trụ)',
                  lap_cach_dung_than: '3️⃣ Lập cách · Dụng thần',
                  bai_tinh_than: '4️⃣ Bài tinh thần (14 chính tinh)',
                  lap_toa_menh: '5️⃣ Lập tọa Mệnh',
                  dai_van_phan_tich: '6️⃣ Đại Vận phân tích',
                  dai_han_luu_nien: '7️⃣ Đại Hạn + Lưu Niên',
                  tu_hoa_dien_giai: '8️⃣ Tứ Hóa diễn giải sâu',
                  hi_ky_canh_bao: '9️⃣ Hỉ kỵ + Cảnh báo',
                  ket_tam_an: '🔟 Kết tâm an'
                }[key] || key }}</h5>
                <div class="pms-section-controls">
                  <small class="pms-section-len">{{ (content?.length || 0).toLocaleString() }} chữ</small>
                  <button class="pms-copy-btn" @click.stop="copyPmsSection(key, content)" :title="'Copy section'">📋</button>
                  <span class="pms-toggle">{{ collapsedSections.has(key) ? '▸' : '▾' }}</span>
                </div>
              </header>
              <div v-if="!collapsedSections.has(key)" class="pms-section-body" v-html="formatPmsContent(content)"></div>
            </article>
            <p class="pms-paradigm">💡 {{ pheMenhSau.paradigm_note }}</p>
          </div>
        </template>
      </section>

      <!-- ── Case Studies — Lá số anh có nét giống ai (Q3+Q4) ──────── -->
      <template v-if="caseStudies && caseStudies.matches?.length">
        <section class="case-studies-block">
          <h4 class="section-h">
            🏛️ Lá số anh có nét giống ai trong lịch sử
            <small class="case-paradigm-tag">Q3+Q4 — dẫn chứng phê mệnh</small>
          </h4>
          <p class="case-warning">
            ⚠ Đây là <b>NÉT GIỐNG về cấu trúc sao</b>, không phải tiên tri "anh sẽ giống X".
            Cùng cấu trúc có 2 ngả — TÂM + thời + lựa chọn của anh quyết định.
          </p>
          <div v-for="(m, mi) in caseStudies.matches" :key="m.pattern_id" class="case-pattern-card"
               :class="'cpc-' + m.polarity">
            <header class="cpc-head">
              <div class="cpc-title">
                <span class="cpc-badge" :class="'badge-' + m.polarity">
                  {{ m.polarity === 'cát' ? '✦ Cát'
                    : m.polarity === 'ambiguous_warning' ? '⚠ Paradigm tension'
                    : m.polarity }}
                </span>
                <strong>{{ m.pattern_name }}</strong>
              </div>
              <small class="cpc-score">match score {{ m.score }} · {{ m.pattern_name_zh }}</small>
            </header>
            <div class="cpc-reasons">
              <span v-for="(r, ri) in m.reasons" :key="ri" class="cpc-reason">{{ r }}</span>
            </div>
            <div v-if="m.key_phrase_hv" class="cpc-phrase">
              <em>« {{ m.key_phrase_hv }} »</em>
              <small v-if="m.key_phrase_zh">— {{ m.key_phrase_zh }}</small>
            </div>
            <div v-if="m.key_phrase_hv_tran" class="cpc-dual-phrase">
              <div class="cpc-voice cpc-voice-tran">
                <small>Trần Đoàn:</small> <em>« {{ m.key_phrase_hv_tran }} »</em>
              </div>
              <div class="cpc-voice cpc-voice-khang-tiet">
                <small>Khang Tiết bổ:</small> <em>« {{ m.key_phrase_hv_khang_tiet }} »</em>
              </div>
            </div>
            <p class="cpc-lesson">{{ m.lesson_short }}</p>
            <div class="cpc-figures">
              <article v-for="(f, fi) in m.figures.slice(0, 4)" :key="fi" class="figure-card">
                <header>
                  <h6>{{ f.name_vi }} <small class="fc-zh">({{ f.name_zh }})</small></h6>
                  <small class="fc-era">{{ f.era }}</small>
                </header>
                <p class="fc-title">{{ f.title }}</p>
                <p class="fc-lesson">{{ f.lesson }}</p>
              </article>
            </div>
            <p v-if="m.warning" class="cpc-warning">{{ m.warning }}</p>
            <details class="cpc-source">
              <summary>Nguồn dẫn</summary>
              <ul>
                <li v-for="(v, k) in m.source_ref" :key="k"><b>{{ k }}:</b> {{ v }}</li>
              </ul>
            </details>
          </div>
          <p v-if="caseStudies.paradigm_note" class="case-paradigm-note">
            💡 {{ caseStudies.paradigm_note }}
          </p>
        </section>
      </template>
      <template v-else-if="caseLoading">
        <p class="case-loading">Đang tìm nét giống lịch sử...</p>
      </template>
      <template v-else-if="caseStudies && !caseStudies.matches?.length">
        <p class="case-empty">
          🌿 Lá số anh không khớp pattern Q3+Q4 nào (Tử Phủ Dần hoặc Tử Phá Thìn Tuất).
          Đó là <em>điều tốt</em> — lá số anh có cá tính riêng, không bị bóng các figure lịch sử.
        </p>
      </template>

      <!-- ── Interpretation — 12 cung readings ───────────────────── -->
      <template v-if="interpretation">
        <h4 class="section-h">
          Luận giải 12 cung
          <small class="interp-summary"
            :data-tag="interpretation.chart_summary.total_polarity_score >= 5 ? 'fav' :
                       interpretation.chart_summary.total_polarity_score <= -5 ? 'cha' : 'mid'">
            · {{ interpretation.chart_summary.verdict }}
          </small>
        </h4>
        <div class="interp-counts">
          <span class="ic favorable">⬆ Thuận: <b>{{ interpretation.chart_summary.favorable_palaces }}</b></span>
          <span class="ic mixed">⇆ Hỗn hợp: <b>{{ interpretation.chart_summary.mixed_palaces }}</b></span>
          <span class="ic challenging">⬇ Khó: <b>{{ interpretation.chart_summary.challenging_palaces }}</b></span>
          <span class="ic empty">○ Trống: <b>{{ interpretation.chart_summary.empty_palaces }}</b></span>
        </div>

        <ul class="interp-list">
          <li v-for="r in interpretation.palace_readings" :key="r.palace_name"
            class="interp-row" :class="`tag-${r.polarity_tag}`"
            @click="expandedPalace = expandedPalace === r.palace_name ? null : r.palace_name">
            <header>
              <strong>{{ r.palace_name }}</strong>
              <small>@ {{ r.branch }}</small>
              <span class="interp-verdict">{{ r.polarity_tag === 'favorable' ? '✓ Thuận'
                : r.polarity_tag === 'challenging' ? '✗ Khó'
                : r.polarity_tag === 'mixed' ? '⇆ Hỗn hợp'
                : '○ Trống' }}</span>
              <small class="interp-stars">{{ r.chinh_tinh.join(', ') || '(không chính tinh)' }}</small>
            </header>
            <p class="interp-reading">{{ r.main_reading }}</p>
            <div v-if="expandedPalace === r.palace_name && r.star_details.length" class="interp-stardetails">
              <div v-for="sd in r.star_details" :key="sd.ten_vi" class="sd-card">
                <h6>{{ sd.ten_vi }} ({{ sd.ten_zh }}) · {{ sd.ngu_hanh }}</h6>
                <p class="sd-kw">{{ sd.keywords.join(' · ') }}</p>
                <p class="sd-pos">✦ {{ sd.tich_cuc }}</p>
                <p class="sd-neg">⚠ {{ sd.tieu_cuc }}</p>
              </div>
            </div>
            <!-- ⭐ Q1 Phú + Q3 sao×cung passages từ sách cổ -->
            <div v-if="expandedPalace === r.palace_name && cungReading?.palaces?.[r.palace_name]"
                 class="cung-book-passages" @click.stop>
              <div v-if="cungReading.palaces[r.palace_name].q1_passages?.length" class="cbp-section">
                <h6 class="cbp-head">📚 Q1 Phú Thái Vi ({{ cungReading.palaces[r.palace_name].q1_passages.length }} câu)</h6>
                <div v-for="(p, i) in cungReading.palaces[r.palace_name].q1_passages" :key="'q1-'+i"
                     class="cbp-card cbp-q1">
                  <div class="cbp-meta">trang {{ p.page }} · score {{ p.score }}</div>
                  <div class="cbp-hv">{{ p.hanviet }}</div>
                  <div class="cbp-lg">{{ p.luangiai }}</div>
                  <div v-if="p.reasons?.length" class="cbp-reasons">
                    🎯 {{ p.reasons.slice(0, 3).join(' · ') }}
                  </div>
                </div>
              </div>
              <div v-if="cungReading.palaces[r.palace_name].q3_passages?.length" class="cbp-section">
                <h6 class="cbp-head">📖 Q3 Diễn Giải sao×cung ({{ cungReading.palaces[r.palace_name].q3_passages.length }} dòng)</h6>
                <div v-for="(p, i) in cungReading.palaces[r.palace_name].q3_passages" :key="'q3-'+i"
                     class="cbp-card cbp-q3"
                     :class="{ 'cbp-combo': p.match_type === 'combo_universal' }">
                  <div class="cbp-meta">
                    trang {{ p.page }} · [{{ p.matched_stars?.join(', ') || '' }}]
                    <span v-if="p.match_type === 'combo_universal'" class="cbp-tag cbp-tag-combo">combo</span>
                    <span v-else class="cbp-tag cbp-tag-anchor">cung</span>
                  </div>
                  <div class="cbp-hv">{{ p.hanviet }}</div>
                  <div v-if="p.luangiai" class="cbp-lg">{{ p.luangiai }}</div>
                </div>
              </div>
              <div v-if="!cungReading.palaces[r.palace_name].q1_passages?.length
                        && !cungReading.palaces[r.palace_name].q3_passages?.length"
                   class="cbp-empty">
                _Chưa tìm thấy đoạn trong Q1/Q3 đề cập trực tiếp cung này._
              </div>
            </div>
          </li>
        </ul>
      </template>
    </template>

    <!-- Phú Thái Vi modal — kinh điển từ TVDSTT Q.1 -->
    <PhuThaiViModal :visible="showPhuThaiVi" @close="showPhuThaiVi = false" />

    <!-- Cách cục đọc sâu modal (teleported to body — escape .panel backdrop-filter containing block) -->
    <Teleport to="body">
      <div v-if="showCachCuc" class="cc-modal-backdrop" @click.self="showCachCuc = false">
        <div class="cc-modal">
          <button class="cc-modal-close" @click="showCachCuc = false">✕</button>
          <CachCucPanel />
        </div>
      </div>
    </Teleport>

    <!-- 12 Đại Vận modal -->
    <Teleport to="body">
      <div v-if="showDaiVan" class="cc-modal-backdrop" @click.self="showDaiVan = false">
        <div class="cc-modal">
          <button class="cc-modal-close" @click="showDaiVan = false">✕</button>
          <DaiVanPanel />
        </div>
      </div>
    </Teleport>

    <!-- Lưu Niên 2026-2030 modal -->
    <Teleport to="body">
      <div v-if="showLuuNien" class="cc-modal-backdrop" @click.self="showLuuNien = false">
        <div class="cc-modal">
          <button class="cc-modal-close" @click="showLuuNien = false">✕</button>
          <LuuNienPanel />
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.tvls-panel { display: flex; flex-direction: column; gap: 14px; }

.tv-birth-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 10px 14px;
  background: rgba(245, 230, 177, 0.05);
  border-left: 3px solid var(--accent-gold-soft, #f5e6b1);
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
}
.tv-bs-item {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}
.tv-bs-label {
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-weight: 600;
  font-size: 12px;
}
.tv-bs-val {
  color: var(--text-strong, #e6eef5);
}

.intro-note {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 3px solid var(--accent-gold, #e8c95a);
  padding-left: 12px;
  margin: 0;
  line-height: 1.6;
}
.intro-note b { color: var(--accent-gold-soft, #f5e6b1); }
.intro-note em { color: var(--accent-teal, #5be5d3); font-style: normal; }

.tvls-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
}
.tvls-form label { display: flex; flex-direction: column; gap: 4px; }
.tvls-form span {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.tvls-actions { grid-column: 1 / -1; display: flex; gap: 8px; flex-wrap: wrap; }

/* Phú Thái Vi button — kinh điển */
.phu-btn {
  background: linear-gradient(135deg, #6d2727, #4a1a1a);
  color: #fde68a;
  border: 1px solid #8b3a2a;
  padding: 0.5rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: "Charter", "Iowan Old Style", Georgia, serif;
  letter-spacing: 0.02em;
  transition: all 0.15s;
}
.phu-btn:hover {
  background: linear-gradient(135deg, #8b3a2a, #6d2727);
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 58, 42, 0.4);
}

/* Cách cục button */
.cach-cuc-btn {
  background: linear-gradient(135deg, #1e3a8a, #1e40af);
  color: #93c5fd;
  border: 1px solid #2563eb;
  padding: 0.5rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: inherit;
  transition: all 0.15s;
}
.cach-cuc-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  color: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

/* Đại Vận button */
.dai-van-btn {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  color: #c4b5fd;
  border: 1px solid #7c3aed;
  padding: 0.5rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: inherit;
  transition: all 0.15s;
}
.dai-van-btn:hover {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: #fff;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
}

/* Lưu Niên button */
.luu-nien-btn {
  background: linear-gradient(135deg, #be185d, #9f1239);
  color: #fbcfe8;
  border: 1px solid #db2777;
  padding: 0.5rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: inherit;
  transition: all 0.15s;
}
.luu-nien-btn:hover {
  background: linear-gradient(135deg, #db2777, #be185d);
  color: #fff;
  box-shadow: 0 4px 12px rgba(219, 39, 119, 0.4);
}

/* Modal styles — removed (moved to non-scoped block below to work with Teleport-to-body) */

/* ── 4×4 lá số grid ────────────────────────────────────────────────────── */
.laso-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, minmax(150px, auto));
  gap: 3px;
  background: rgba(232, 201, 90, 0.06);
  padding: 4px;
  border-radius: 6px;
  border: 1px solid rgba(232, 201, 90, 0.25);
  box-shadow: 0 0 0 3px rgba(232, 201, 90, 0.04), inset 0 0 40px rgba(0,0,0,0.3);
}

.laso-cell {
  background: rgba(12, 18, 28, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 3px;
  padding: 5px 6px 4px;
  font-size: 11px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  position: relative;
  overflow: hidden;
}
.laso-cell.center {
  background: rgba(20, 28, 42, 0.9);
  border-color: rgba(232, 201, 90, 0.15);
}
.laso-cell.is-menh {
  background: rgba(232, 201, 90, 0.09);
  border-color: rgba(232, 201, 90, 0.55);
  box-shadow: 0 0 8px rgba(232, 201, 90, 0.15) inset;
}
.laso-cell.is-than:not(.is-menh) {
  border-left: 2px solid #d65a78;
}

/* ── Palace cell header ── */
.cell-head {
  display: flex;
  align-items: center;
  gap: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  padding-bottom: 4px;
  margin-bottom: 3px;
}
.cell-head-left { display: flex; align-items: center; gap: 3px; flex-shrink: 0; }
.elem-chip {
  font-size: 8px;
  font-weight: 800;
  padding: 0 3px;
  border-radius: 2px;
  border: 1px solid;
  line-height: 14px;
  letter-spacing: 0;
}
.cell-branch {
  font-size: 9.5px;
  color: rgba(230, 238, 245, 0.45);
  font-weight: 700;
  letter-spacing: 0.3px;
}
.cell-palace {
  flex: 1;
  font-size: 11.5px;
  color: rgba(245, 230, 177, 0.85);
  font-weight: 700;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cell-palace.is-menh-label { color: #e8c95a; font-size: 12px; }
.cell-palace.is-than-label { color: #f5a5b5; }
.dv-age-badge {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 800;
  color: rgba(232, 201, 90, 0.6);
  background: rgba(232, 201, 90, 0.08);
  border-radius: 2px;
  padding: 0 4px;
  line-height: 16px;
  min-width: 20px;
  text-align: center;
}

/* ── Stars ── */
.stars { list-style: none; margin: 0; padding: 0; }
.star {
  display: flex;
  align-items: baseline;
  gap: 3px;
  line-height: 1.35;
  font-size: 11.5px;
}
.chinh-tinh { font-weight: 800; font-size: 12px; line-height: 1.4; }
.phu-tinh { color: #7dd3fc; font-size: 10.5px; }
.stars.sat { display: flex; flex-wrap: wrap; gap: 2px; margin-top: 2px; }
.sat-tinh {
  color: #fca5a5; font-size: 9.5px;
  padding: 1px 4px; border-radius: 2px;
  background: rgba(252, 165, 165, 0.10);
}
.sat-tinh.loc-ton {
  color: #86efac; font-weight: 700;
  background: rgba(134, 239, 172, 0.14);
  border: 1px solid rgba(134, 239, 172, 0.30);
}
.sat-tinh.thien-ma {
  color: #fde68a; font-weight: 600;
  background: rgba(253, 230, 138, 0.13);
  border: 1px solid rgba(253, 230, 138, 0.30);
}
.stars.q2 {
  margin-top: 3px; padding-top: 3px;
  border-top: 1px dashed rgba(168, 85, 247, 0.25);
  display: flex; flex-wrap: wrap; gap: 2px;
}
.q2-tinh {
  font-size: 9px; padding: 1px 4px; border-radius: 2px;
  font-family: ui-sans-serif, sans-serif;
}
.q2-tinh.thai-tue {
  background: rgba(168, 85, 247, 0.18); color: #c084fc;
}
.q2-tinh.phu-q2 {
  background: rgba(34, 211, 238, 0.15); color: #67e8f9;
}

.hoa-badge {
  display: inline-block;
  font-size: 8.5px;
  padding: 0 4px;
  border-radius: 2px;
  border: 1px solid;
  font-weight: 700;
}

/* ── Cell footer badges ── */
.cell-foot {
  margin-top: auto;
  display: flex;
  gap: 4px;
  padding-top: 2px;
}
.menh-mark, .than-mark, .dauquan-mark {
  font-size: 8.5px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 2px;
  line-height: 14px;
}
.menh-mark  { background: rgba(232, 201, 90, 0.2); color: #e8c95a; }
.than-mark  { background: rgba(214, 90, 120, 0.2); color: #f5a5b5; }
.dauquan-mark { background: rgba(56, 189, 248, 0.15); color: #7dd3fc; font-family: "Songti SC", serif; }

/* ── Center cells ── */
.center-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11px;
  height: 100%;
  padding: 2px;
}

/* TL: title / cục / mệnh thân */
.center-title {
  align-items: center;
  text-align: center;
  justify-content: center;
}
.ct-logo {
  font-size: 22px;
  font-weight: 900;
  color: #e8c95a;
  font-family: "Songti SC", "SimSun", serif;
  letter-spacing: 2px;
  line-height: 1;
}
.ct-sub {
  font-size: 8.5px;
  color: rgba(245, 230, 177, 0.4);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.ct-cuc {
  font-size: 11px;
  font-weight: 700;
  color: #f5e6b1;
  padding: 2px 8px;
  border: 1px solid rgba(232, 201, 90, 0.3);
  border-radius: 3px;
  background: rgba(232, 201, 90, 0.07);
  margin-bottom: 3px;
}
.ct-row {
  font-size: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
}
.ct-row b { color: #f5e6b1; font-size: 11px; }

/* TR: birth detail rows */
.ci-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
}
.ci-row span:last-child { color: #e6eef5; }

.ci-label {
  font-size: 8.5px;
  color: rgba(230, 238, 245, 0.38);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  flex-shrink: 0;
}

/* BL: Tứ Hóa */
.ci-hoa-title {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(230, 238, 245, 0.4);
  margin-bottom: 2px;
}
.hoa-line {
  display: flex;
  gap: 5px;
  font-size: 10.5px;
  align-items: center;
}
.hoa-line em {
  color: rgba(230, 238, 245, 0.85);
  font-style: normal;
}
.hoa-tag {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 2px;
  border: 1px solid;
  font-weight: 700;
  min-width: 32px;
  text-align: center;
}

/* BR: Đại Vận mini */
.center-dv-mini { justify-content: flex-start; }
.dv-mini-row {
  display: flex;
  gap: 6px;
  align-items: center;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
}
.dv-mini-row.dv-current {
  background: rgba(232, 201, 90, 0.15);
  border-left: 2px solid #e8c95a;
}
.dv-mini-age { color: rgba(232, 201, 90, 0.7); font-weight: 700; min-width: 20px; }
.dv-mini-branch { color: #e6eef5; font-weight: 600; }

/* ── Đại Vận strip ───────────────────────────────────────────────────── */
.section-h {
  margin: 14px 0 6px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
}
.dv-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 5px;
}
.dv-cell {
  background: rgba(232, 201, 90, 0.05);
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 4px;
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}
.dv-cell strong {
  font-size: 10px;
  color: var(--accent-gold, #e8c95a);
}
.dv-branch {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
}
.dv-cell small {
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

/* ── Lưu Trú Sao card ────────────────────────────────────────────────── */
.luu-tru-card {
  background: rgba(91, 229, 211, 0.05);
  border: 1px solid rgba(91, 229, 211, 0.22);
  border-radius: 8px;
  padding: 14px;
}
.lt-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}
.lt-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 5px;
}
.lt-label {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.lt-cell strong {
  font-size: 15px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.lt-cell small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.lt-h {
  margin: 12px 0 6px 0;
  font-size: 11px;
  color: var(--accent-teal, #5be5d3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}
.lt-hoa-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 6px;
}
.lt-hoa-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid;
  border-radius: 4px;
  padding: 5px 9px;
  display: flex;
  gap: 6px;
  align-items: center;
  font-size: 12px;
}
.lt-hoa-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 2px;
  font-weight: 700;
}
.lt-hoa-item em { color: var(--text-primary, #e6eef5); font-style: normal; }
.lt-stars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 6px;
}
.lt-star-cell {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  padding: 5px 9px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 11.5px;
}
.lt-star-cell span { color: var(--text-muted, rgba(230, 238, 245, 0.6)); }
.lt-star-cell b { color: var(--accent-gold-soft, #f5e6b1); }

/* ── Đại Vận current cycle highlight ─────────────────────────────────── */
.dv-cell.is-current {
  background: rgba(91, 229, 211, 0.12);
  border-color: rgba(91, 229, 211, 0.5);
  box-shadow: 0 0 0 1px rgba(91, 229, 211, 0.25);
}

/* ── Interpretation list ─────────────────────────────────────────────── */
.interp-summary {
  font-weight: 400;
  font-size: 12px;
  letter-spacing: 0;
  text-transform: none;
  margin-left: 8px;
}
.interp-summary[data-tag="fav"] { color: #88d39e; }
.interp-summary[data-tag="cha"] { color: #f5b08c; }
.interp-summary[data-tag="mid"] { color: var(--text-muted, rgba(230, 238, 245, 0.55)); }

.interp-counts {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.ic {
  font-size: 11px;
  padding: 3px 9px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.04);
}
.ic.favorable { color: #88d39e; background: rgba(90, 176, 122, 0.08); }
.ic.mixed { color: #c0a878; background: rgba(192, 168, 120, 0.08); }
.ic.challenging { color: #f5b08c; background: rgba(214, 90, 74, 0.08); }
.ic.empty { color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.ic b { font-weight: 700; }

.interp-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 5px; }
.interp-row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.15s;
}
.interp-row:hover { background: rgba(255, 255, 255, 0.06); }
.interp-row.tag-favorable { border-left: 3px solid #5ab07a; }
.interp-row.tag-mixed { border-left: 3px solid #c0a878; }
.interp-row.tag-challenging { border-left: 3px solid #d65a4a; }
.interp-row.tag-empty { border-left: 3px solid rgba(255, 255, 255, 0.15); }
.interp-row header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.interp-row header strong {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.interp-row header small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.interp-verdict {
  font-size: 10.5px;
  padding: 1px 7px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.04);
  font-weight: 600;
}
.tag-favorable .interp-verdict { color: #88d39e; background: rgba(90, 176, 122, 0.12); }
.tag-mixed .interp-verdict { color: #c0a878; background: rgba(192, 168, 120, 0.12); }
.tag-challenging .interp-verdict { color: #f5b08c; background: rgba(214, 90, 74, 0.12); }
.interp-stars {
  margin-left: auto;
  font-style: italic;
}
.interp-reading {
  margin: 4px 0 0 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.interp-stardetails {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sd-card {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px 10px;
}
.sd-card h6 {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.sd-kw {
  margin: 0 0 4px 0;
  font-size: 11px;
  color: var(--accent-teal, #5be5d3);
}
.sd-pos { margin: 2px 0; font-size: 11.5px; color: #88d39e; }
.sd-neg { margin: 2px 0 0 0; font-size: 11.5px; color: #f5b08c; }

@media (max-width: 920px) {
  .laso-grid { grid-template-rows: repeat(4, minmax(120px, auto)); }
  .laso-cell { font-size: 10px; }
  .star { font-size: 10px; }
  .lt-row { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .laso-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, minmax(85px, auto));
  }
  .star { font-size: 9px; }
  .cell-palace { font-size: 10px; }
  .tvls-form { grid-template-columns: 1fr; }
}

/* Q1 Phú + Q3 passages per palace */
.cung-book-passages {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed rgba(232, 201, 90, 0.25);
}
.cbp-section { margin-top: 8px; }
.cbp-head {
  margin: 6px 0 4px;
  font-size: 11px;
  color: var(--accent-gold-soft, #f5e6b1);
  letter-spacing: 0.02em;
}
.cbp-card {
  background: rgba(255, 255, 255, 0.025);
  border-left: 2px solid var(--accent-teal, #5be5d3);
  border-radius: 0 3px 3px 0;
  padding: 6px 9px;
  margin: 4px 0;
  font-size: 11.5px;
  line-height: 1.5;
}
.cbp-q3 { border-left-color: #a78bfa; }
.cbp-meta {
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  margin-bottom: 2px;
}
.cbp-hv {
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-style: italic;
  margin: 2px 0;
}
.cbp-lg {
  color: var(--text-primary, #e6eef5);
  margin: 3px 0;
}
.cbp-reasons {
  font-size: 10px;
  color: var(--accent-teal, #5be5d3);
  margin-top: 3px;
  opacity: 0.85;
}
.cbp-empty {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.45));
  font-style: italic;
  margin-top: 6px;
}
.cbp-combo { opacity: 0.85; border-left-color: #94a3b8; }
.cbp-tag {
  display: inline-block;
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: 6px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  vertical-align: middle;
}
.cbp-tag-anchor {
  background: rgba(167, 139, 250, 0.18);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.3);
}
.cbp-tag-combo {
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

/* ━━━━━━━━ VIP1 Luận giải sâu (DeepSeek Pro) ━━━━━━━━ */
.phe-menh-sau-block {
  margin: 24px 0;
  padding: 18px 20px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(20, 30, 45, 0.5));
  border: 2px solid rgba(245, 158, 11, 0.4);
  border-radius: 10px;
  position: relative;
}
.phe-menh-sau-block::before {
  content: "✨ VIP";
  position: absolute; top: -12px; right: 16px;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #1a1a1a; padding: 2px 10px;
  border-radius: 12px; font-size: 11px;
  font-weight: 700; letter-spacing: 0.04em;
}
.pms-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.pms-head h4 { margin: 0; color: #fbbf24; font-size: 15px; }
.pms-status { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.pms-badge {
  padding: 3px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 600;
}
.pms-vip { background: rgba(90, 176, 122, 0.2); color: #88d39e; border: 1px solid #5ab07a; }
.pms-locked { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #94a3b8; }
.pms-remaining, .pms-expires { font-size: 11px; color: rgba(230, 238, 245, 0.7); }
.pms-intro {
  font-size: 12.5px; color: rgba(230, 238, 245, 0.85);
  line-height: 1.6; margin: 8px 0;
}
.pms-intro b { color: #fbbf24; }
.pms-locked-msg {
  background: rgba(148, 163, 184, 0.08);
  border: 1px dashed rgba(148, 163, 184, 0.4);
  border-radius: 6px;
  padding: 14px 16px; margin: 10px 0;
  font-size: 13px; color: rgba(230, 238, 245, 0.8);
}
.pms-locked-msg b { color: #fbbf24; }
.pms-locked-reason { color: #f5b08c; margin: 6px 0 0; font-size: 12px; }
.pms-actions { display: flex; gap: 8px; margin: 10px 0; }
.pms-btn {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  border: none; color: white;
  padding: 8px 18px; border-radius: 6px;
  font-size: 13px; cursor: pointer; font-weight: 600;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  transition: transform 0.15s;
}
.pms-btn:hover { transform: translateY(-1px); }
.pms-regen { background: rgba(245, 158, 11, 0.2); border: 1px solid #f59e0b; color: #fbbf24; box-shadow: none; }
.pms-loading { font-size: 13px; color: #fbbf24; font-style: italic; padding: 12px; }
.pms-error { font-size: 12.5px; color: #f5b08c; padding: 10px; background: rgba(214, 90, 74, 0.08); border-radius: 4px; }
.pms-content { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
.pms-meta { font-size: 10.5px; color: rgba(230, 238, 245, 0.5); font-style: italic; }
.pms-section {
  padding: 12px 14px;
  background: rgba(0, 0, 0, 0.22);
  border-left: 3px solid #fbbf24;
  border-radius: 0 6px 6px 0;
  transition: background 0.18s;
}
.pms-section.pms-collapsed { padding: 8px 14px; }
.pms-section.pms-collapsed:hover { background: rgba(0, 0, 0, 0.32); }
.pms-section-header {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; gap: 12px;
}
.pms-section-header h5 { margin: 0; color: #fcd34d; font-size: 13.5px; font-weight: 600; flex: 1; }
.pms-section-controls { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.pms-section-len { color: rgba(230, 238, 245, 0.45); font-size: 10.5px; }
.pms-copy-btn {
  background: transparent; border: 1px solid rgba(252, 211, 77, 0.3);
  color: #fbbf24; padding: 1px 6px; border-radius: 3px;
  cursor: pointer; font-size: 11px; transition: background 0.15s;
}
.pms-copy-btn:hover { background: rgba(252, 211, 77, 0.15); }
.pms-toggle { color: #fbbf24; font-size: 14px; }
.pms-section-body {
  margin-top: 10px;
  font-size: 13.5px; line-height: 1.75;
  color: var(--text-secondary, rgba(230, 238, 245, 0.92));
  font-family: "Charter", "Iowan Old Style", "Times New Roman", Georgia, serif;
}
.pms-section-body p {
  margin: 0 0 10px;
}
.pms-section-body p.pms-subhead {
  margin-top: 12px; margin-bottom: 4px;
  color: #fcd34d; font-size: 13px; font-weight: 600;
}
.pms-section-body blockquote.pms-classical {
  margin: 8px 0 6px; padding: 10px 14px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.08), rgba(251, 191, 36, 0.02));
  border-left: 3px solid #fbbf24;
  font-family: "Palatino", "Garamond", serif;
  color: #fde68a; font-size: 13.5px; font-style: italic;
  line-height: 1.65; letter-spacing: 0.2px;
  border-radius: 0 4px 4px 0;
}
.pms-section-body blockquote.pms-translation {
  margin: 4px 0 12px; padding: 6px 14px;
  background: rgba(91, 229, 211, 0.05);
  border-left: 2px solid #5be5d3;
  color: rgba(230, 238, 245, 0.82);
  font-size: 12.5px; font-style: italic;
  line-height: 1.6;
  border-radius: 0 3px 3px 0;
}
.pms-section-body .pms-gloss {
  color: rgba(91, 229, 211, 0.95);
  font-size: 0.9em; font-style: italic;
  background: rgba(91, 229, 211, 0.06);
  padding: 0 4px; border-radius: 2px;
}
.pms-section-body strong { color: #fde68a; font-weight: 700; }
.pms-section-body em { color: rgba(252, 211, 77, 0.85); }
.pms-paradigm {
  margin: 10px 0 0; padding: 8px 12px;
  background: rgba(91, 229, 211, 0.06);
  border-left: 2px solid #5be5d3;
  font-size: 11.5px; color: rgba(230, 238, 245, 0.78);
  line-height: 1.55; font-style: italic;
  border-radius: 0 3px 3px 0;
}

/* ━━━━━━━━ Q4 Thiên Quán Archetype ━━━━━━━━ */
.tq-archetype-block {
  margin: 18px 0;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.06), rgba(20, 30, 45, 0.3));
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
}
.tq-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; flex-wrap: wrap; }
.tq-head h4 { margin: 0; color: #fcd34d; font-size: 14px; }
.tq-head small { font-size: 11px; color: rgba(230, 238, 245, 0.55); font-style: italic; }
.tq-cung-name { margin: 8px 0; font-size: 14px; }
.tq-label { color: rgba(230, 238, 245, 0.55); margin-right: 6px; }
.tq-cung-name strong { color: #fcd34d; font-size: 16px; }
.tq-summary {
  margin: 8px 0;
  padding: 10px 12px;
  background: rgba(251, 191, 36, 0.08);
  border-left: 3px solid #fbbf24;
  border-radius: 0 4px 4px 0;
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
  line-height: 1.6;
}
.tq-detail { margin: 8px 0; font-size: 12px; }
.tq-detail summary { cursor: pointer; color: #fcd34d; font-weight: 500; }
.tq-detail ul { margin: 6px 0 0 18px; padding: 0; }
.tq-detail li {
  color: var(--text-secondary, rgba(230, 238, 245, 0.82));
  margin: 3px 0;
  line-height: 1.55;
}
.tq-detail b { color: rgba(230, 238, 245, 0.55); font-weight: 500; }
.tq-iron-rule {
  margin: 10px 0 0;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.06);
  border-left: 2px solid #a78bfa;
  font-size: 11.5px;
  color: rgba(230, 238, 245, 0.78);
  line-height: 1.55;
  font-style: italic;
  border-radius: 0 3px 3px 0;
}

/* ━━━━━━━━ Phê Mệnh phú thi (Q4 Khang Tiết) ━━━━━━━━ */
.phe-menh-block {
  margin: 18px 0;
  padding: 16px 18px;
  background: linear-gradient(180deg, rgba(167, 139, 250, 0.06), rgba(20, 30, 45, 0.4));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
}
.pm-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.pm-head h4 { margin: 0; color: #c4b5fd; font-size: 14px; }
.pm-actions { display: flex; align-items: center; gap: 8px; }
.pm-meta { font-size: 10.5px; color: rgba(230, 238, 245, 0.5); font-style: italic; }
.pm-btn {
  background: linear-gradient(135deg, #6d28d9, #a78bfa);
  border: none;
  color: white;
  padding: 6px 14px;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: transform 0.15s;
}
.pm-btn:hover { transform: translateY(-1px); }
.pm-regen { background: rgba(167, 139, 250, 0.2); border: 1px solid #a78bfa; color: #c4b5fd; }

.pm-intro {
  font-size: 12.5px;
  color: rgba(230, 238, 245, 0.78);
  line-height: 1.55;
  margin: 8px 0 0;
}
.pm-intro b { color: #c4b5fd; }
.pm-loading { font-size: 13px; color: #a78bfa; font-style: italic; padding: 12px; }
.pm-error { font-size: 12.5px; color: #f5b08c; padding: 10px; background: rgba(214, 90, 74, 0.08); border-radius: 4px; }

.pm-content { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.pm-section {
  padding: 12px 14px;
  background: rgba(0, 0, 0, 0.18);
  border-left: 3px solid;
  border-radius: 0 5px 5px 0;
}
.pm-khai-de { border-left-color: #fbbf24; }
.pm-menh-than { border-left-color: #5be5d3; }
.pm-dai-van { border-left-color: #a78bfa; }
.pm-canh-bao { border-left-color: #5ab07a; }
.pm-tam-an { border-left-color: #f9a8d4; }

.pm-section h5 {
  margin: 0 0 6px;
  font-size: 12.5px;
  font-weight: 600;
}
.pm-khai-de h5 { color: #fcd34d; }
.pm-menh-than h5 { color: #5be5d3; }
.pm-dai-van h5 { color: #c4b5fd; }
.pm-canh-bao h5 { color: #88d39e; }
.pm-tam-an h5 { color: #f9a8d4; }

.pm-section p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary, rgba(230, 238, 245, 0.88));
  white-space: pre-wrap;
  font-family: "Times New Roman", "Palatino", serif;
  font-style: italic;
}
.pm-paradigm {
  margin: 10px 0 0;
  padding: 8px 12px;
  background: rgba(91, 229, 211, 0.05);
  border-left: 2px solid #5be5d3;
  font-size: 11.5px;
  color: rgba(230, 238, 245, 0.78);
  line-height: 1.55;
  font-style: italic;
  border-radius: 0 3px 3px 0;
}

/* ━━━━━━━━ Safety Block (Q1+Q3 dark warnings) ━━━━━━━━ */
.safety-block {
  margin: 18px 0;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(90, 176, 122, 0.05), rgba(20, 30, 45, 0.3));
  border: 1px solid rgba(90, 176, 122, 0.3);
  border-radius: 8px;
}
.sb-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.sb-head h4 { margin: 0; color: #88d39e; font-size: 14px; }
.sb-head small { font-size: 10.5px; color: rgba(230, 238, 245, 0.5); font-style: italic; }
.sb-pattern {
  margin: 10px 0;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-left: 3px solid #5ab07a;
  border-radius: 0 4px 4px 0;
}
.sb-pattern-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
.sb-pattern-head strong { color: var(--accent-gold-soft, #f5e6b1); font-size: 13px; }
.sb-pattern-head small { font-size: 10.5px; color: rgba(230, 238, 245, 0.5); }
.sb-gentle {
  margin: 6px 0;
  padding: 8px 10px;
  background: rgba(91, 229, 211, 0.05);
  border-left: 2px solid #5be5d3;
  font-size: 12.5px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.85));
  line-height: 1.55;
  border-radius: 0 3px 3px 0;
}
.sb-when, .sb-tips {
  margin: 6px 0;
  font-size: 12px;
}
.sb-when small, .sb-tips small {
  color: rgba(230, 238, 245, 0.55);
  font-size: 11px;
}
.sb-when ul, .sb-tips ul {
  margin: 4px 0 0 18px;
  padding: 0;
}
.sb-when li, .sb-tips li {
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  margin: 2px 0;
  line-height: 1.5;
}
.sb-source { margin-top: 6px; font-size: 11px; }
.sb-source summary { cursor: pointer; color: rgba(230, 238, 245, 0.5); }
.sb-source em { color: #f5e6b1; display: block; margin: 4px 0; }
.sb-source small { color: rgba(230, 238, 245, 0.5); }
.sb-paradigm {
  margin: 10px 0 0;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.06);
  border-left: 2px solid #a78bfa;
  font-size: 11.5px;
  color: rgba(230, 238, 245, 0.78);
  line-height: 1.55;
  font-style: italic;
  border-radius: 0 3px 3px 0;
}

/* ━━━━━━━━ Chart Strength (Q2 p0102 Miếu Vượng Hãm) ━━━━━━━━ */
.chart-strength-block {
  margin: 18px 0;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(91, 229, 211, 0.05), rgba(20, 30, 45, 0.3));
  border: 1px solid rgba(91, 229, 211, 0.25);
  border-radius: 8px;
}
.cs-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.cs-head h4 { margin: 0; font-size: 14px; color: var(--accent-gold-soft, #f5e6b1); }
.cs-source { font-size: 10.5px; color: rgba(230, 238, 245, 0.5); font-style: italic; }

.cs-score-row { margin-bottom: 12px; }
.cs-total {
  padding: 10px 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.cs-strong { background: rgba(90, 176, 122, 0.12); border-left: 4px solid #5ab07a; }
.cs-balanced { background: rgba(148, 163, 184, 0.12); border-left: 4px solid #94a3b8; }
.cs-weak { background: rgba(214, 90, 74, 0.12); border-left: 4px solid #d65a4a; }

.cs-num { font-size: 24px; font-weight: 700; }
.cs-strong .cs-num { color: #5ab07a; }
.cs-balanced .cs-num { color: #cbd5e1; }
.cs-weak .cs-num { color: #d65a4a; }
.cs-verdict { font-size: 13px; color: var(--text-secondary, rgba(230, 238, 245, 0.85)); line-height: 1.5; }

.cs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 6px;
}
.cs-star-cell {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  gap: 2px;
  align-items: center;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.18);
  border-left: 3px solid #94a3b8;
  border-radius: 0 4px 4px 0;
}
.cs-star-name {
  grid-column: 1; grid-row: 1;
  font-size: 12px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 600;
}
.cs-star-meta {
  grid-column: 1; grid-row: 2;
  font-size: 10.5px;
  color: rgba(230, 238, 245, 0.62);
}
.cs-star-score {
  grid-column: 2; grid-row: 1 / span 2;
  font-size: 18px;
  font-weight: 700;
  align-self: center;
}

/* ━━━━━━━━ Case Studies (Q3+Q4 historical figures) ━━━━━━━━ */
.case-studies-block {
  margin: 20px 0;
  padding: 16px 18px;
  background: linear-gradient(180deg, rgba(232, 201, 90, 0.05) 0%, rgba(20, 30, 45, 0.3) 100%);
  border: 1px solid rgba(232, 201, 90, 0.3);
  border-radius: 8px;
}
.case-paradigm-tag {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin-left: 8px;
}
.case-warning {
  background: rgba(214, 90, 74, 0.08);
  border-left: 3px solid #d65a4a;
  padding: 8px 12px;
  font-size: 12.5px;
  color: #f5b08c;
  margin: 8px 0 14px;
  line-height: 1.55;
  border-radius: 3px;
}
.case-warning b { color: #f5e6b1; }

.case-pattern-card {
  background: rgba(255, 255, 255, 0.025);
  border-radius: 6px;
  padding: 12px 14px;
  margin: 10px 0;
  border-left: 4px solid var(--accent-gold, #e8c95a);
}
.cpc-cát { border-left-color: #5ab07a; }
.cpc-ambiguous_warning { border-left-color: #f59e0b; }
.cpc-hung { border-left-color: #d65a4a; }

.cpc-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 6px;
}
.cpc-title { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.cpc-title strong { font-size: 14px; color: var(--accent-gold-soft, #f5e6b1); }
.cpc-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10.5px;
  letter-spacing: 0.03em;
}
.badge-cát {
  background: rgba(90, 176, 122, 0.18);
  border: 1px solid rgba(90, 176, 122, 0.4);
  color: #88d39e;
}
.badge-ambiguous_warning {
  background: rgba(245, 158, 11, 0.18);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fcd34d;
}
.badge-hung {
  background: rgba(214, 90, 74, 0.18);
  border: 1px solid rgba(214, 90, 74, 0.4);
  color: #f5b08c;
}
.cpc-score {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

.cpc-reasons { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0; }
.cpc-reason {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.25);
  color: #5be5d3;
  font-size: 10.5px;
  padding: 2px 8px;
  border-radius: 3px;
}

.cpc-phrase {
  margin: 8px 0;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-left: 2px solid var(--accent-gold-soft, #f5e6b1);
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.85));
  border-radius: 0 3px 3px 0;
}
.cpc-phrase em { color: #f5e6b1; }
.cpc-phrase small { display: block; font-size: 10.5px; color: rgba(230, 238, 245, 0.55); margin-top: 3px; }

.cpc-dual-phrase {
  margin: 10px 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.cpc-voice {
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
}
.cpc-voice small { display: block; font-size: 10px; opacity: 0.75; margin-bottom: 2px; }
.cpc-voice-tran { background: rgba(91, 229, 211, 0.08); border-left: 2px solid #5be5d3; color: #c9efeb; }
.cpc-voice-khang-tiet { background: rgba(167, 139, 250, 0.08); border-left: 2px solid #a78bfa; color: #ddd1ff; }
.cpc-voice em { font-style: italic; }
@media (max-width: 720px) { .cpc-dual-phrase { grid-template-columns: 1fr; } }

.cpc-lesson {
  margin: 8px 0;
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
  line-height: 1.6;
}

.cpc-figures {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
  margin-top: 10px;
}
.figure-card {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 5px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.figure-card header h6 {
  margin: 0;
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.figure-card .fc-zh { font-size: 11px; color: rgba(230, 238, 245, 0.5); font-weight: normal; }
.figure-card .fc-era { display: block; font-size: 10.5px; color: rgba(230, 238, 245, 0.55); margin-top: 2px; }
.figure-card .fc-title {
  margin: 4px 0;
  font-size: 11px;
  color: var(--accent-teal, #5be5d3);
}
.figure-card .fc-lesson {
  margin: 4px 0 0;
  font-size: 11.5px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  line-height: 1.5;
}

.cpc-warning {
  margin: 10px 0 4px;
  padding: 7px 10px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 2px solid #f59e0b;
  font-size: 11.5px;
  color: #fcd34d;
  line-height: 1.5;
  border-radius: 0 3px 3px 0;
}

.cpc-source { margin-top: 8px; font-size: 11px; }
.cpc-source summary { cursor: pointer; color: rgba(230, 238, 245, 0.55); }
.cpc-source ul { margin: 4px 0 0 16px; padding: 0; }
.cpc-source li { color: rgba(230, 238, 245, 0.65); margin: 2px 0; }

.case-paradigm-note {
  margin: 12px 0 0;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.05);
  border-left: 2px solid #a78bfa;
  font-size: 12px;
  color: rgba(230, 238, 245, 0.78);
  line-height: 1.6;
  font-style: italic;
}
.case-loading, .case-empty {
  font-size: 12.5px;
  color: rgba(230, 238, 245, 0.55);
  font-style: italic;
  margin: 12px 0;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}
</style>

<!-- Non-scoped styles for Teleported modal so they apply when modal renders inside <body> -->
<style>
.cc-modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex; justify-content: center; align-items: center;
  padding: 1rem;
}
.cc-modal {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  max-width: 960px;
  width: 100%;
  max-height: 92vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 30px 90px rgba(0,0,0,0.7);
}
.cc-modal-close {
  position: absolute; top: 0.6rem; right: 0.8rem;
  background: rgba(255,255,255,0.1); border: none; color: #cbd5e1;
  width: 32px; height: 32px; border-radius: 4px;
  cursor: pointer; font-size: 1.1rem;
  z-index: 1;
}
.cc-modal-close:hover { background: rgba(255,255,255,0.2); }
</style>
