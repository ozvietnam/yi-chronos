<script setup>
import { computed, ref, watch } from "vue";
import { castBatTu, castHaLac, batTuLuanGiai, batTuLuuNien, batTuHonNhan, batTuSuNghiep, batTuTaiVan, haLacLuanGiai } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import { saveCasting, activePerson } from "../stores/userDataStore.js";
import { isAuthenticated } from "../stores/authStore.js";
import HexagramImage from "./HexagramImage.vue";
import HexagramDetailModal from "./HexagramDetailModal.vue";
import AuspiciousDayPanel from "./wiki/AuspiciousDayPanel.vue";
import BirthHourQuizV2 from "./BirthHourQuizV2.vue";
import { useHexagramModal } from "../composables/useHexagramModal";
import { openConceptPopup } from "../composables/useBatTuConceptPopup.js";

// ── State ─────────────────────────────────────────────────────────────────────

const inputBirth = ref("");
const inputGender = ref("nam");
const inputTimezone = ref("Asia/Ho_Chi_Minh");
const showHourQuiz = ref(false);

const batTuData = ref(null);
const haLacData = ref(null);
const luanGiaiData = ref(null);
const luanGiaiLoading = ref(false);
const luanGiaiError = ref("");
const luuNienData = ref(null);
const luuNienLoading = ref(false);
const luuNienError = ref("");
const honNhanData = ref(null);
const honNhanLoading = ref(false);
const honNhanError = ref("");
const suNghiepData = ref(null);
const suNghiepLoading = ref(false);
const suNghiepError = ref("");
const taiVanData = ref(null);
const taiVanLoading = ref(false);
const taiVanError = ref("");
const haLacLuanData = ref(null);
const haLacLuanLoading = ref(false);
const haLacLuanError = ref("");
const loading = ref(false);
const errorMsg = ref("");

useActivePersonBirth(inputBirth);

const { openSlug, openHexagram, closeHexagram } = useHexagramModal();

// ── Visual maps ──────────────────────────────────────────────────────────────

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

const ELEMENT_GLYPH = {
  kim: "金", "mộc": "木", "thủy": "水", "hỏa": "火", "thổ": "土",
};

const THAP_THAN_COLOR = {
  "Tỷ Kiên":   "#c4c4c4",
  "Kiếp Tài":  "#9a9a9a",
  "Thực Thần": "#5ab07a",
  "Thương Quan": "#5be5d3",
  "Thiên Tài":  "#e8c95a",
  "Chính Tài":  "#d4af37",
  "Thất Sát":   "#d65a4a",
  "Chính Quan": "#5b8ee5",
  "Thiên Ấn":   "#c25a78",
  "Chính Ấn":   "#e0a8b8",
  "Bản thân":   "#f5e6b1",
};

// ── Actions ──────────────────────────────────────────────────────────────────

async function castAll() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập datetime sinh thần.";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  batTuData.value = null;
  haLacData.value = null;
  try {
    const [bt, hl] = await Promise.all([
      castBatTu({
        birthDatetimeLocal: inputBirth.value,
        timezone: inputTimezone.value,
        gender: inputGender.value,
      }),
      castHaLac({
        birthDatetimeLocal: inputBirth.value,
        timezone: inputTimezone.value,
        gender: inputGender.value,
      }),
    ]);
    batTuData.value = bt.bat_tu_state;
    haLacData.value = hl.ha_lac_state;

    // Auto-save to user_castings (silent — only if logged in)
    if (isAuthenticated.value && bt.bat_tu_state) {
      const dm = bt.bat_tu_state.tu_tru?.day_master;
      const cc = bt.bat_tu_state.cach_cuc?.cach_name;
      const verdict = `${dm?.stem || ""} ${dm?.element || ""}${cc ? " · " + cc : ""}`.trim();
      saveCasting({
        method: "bat_tu",
        subject_person_key: activePerson.value?.person_key || null,
        question: null,
        input_json: {
          birth_datetime_local: inputBirth.value,
          timezone: inputTimezone.value,
          gender: inputGender.value,
        },
        result_json: { bat_tu: bt, ha_lac: hl },
        verdict: verdict || null,
      });
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function reset() {
  batTuData.value = null;
  haLacData.value = null;
  luanGiaiData.value = null;
  luanGiaiError.value = "";
  luuNienData.value = null;
  luuNienError.value = "";
  honNhanData.value = null;
  honNhanError.value = "";
  suNghiepData.value = null;
  suNghiepError.value = "";
  taiVanData.value = null;
  taiVanError.value = "";
  haLacLuanData.value = null;
  haLacLuanError.value = "";
  errorMsg.value = "";
}

async function loadLuanGiai() {
  if (!inputBirth.value) return;
  luanGiaiLoading.value = true;
  luanGiaiError.value = "";
  try {
    const r = await batTuLuanGiai({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    luanGiaiData.value = r.luan_giai;
  } catch (err) {
    luanGiaiError.value = err?.message || String(err);
  } finally {
    luanGiaiLoading.value = false;
  }
}

async function loadLuuNien() {
  if (!inputBirth.value) return;
  luuNienLoading.value = true;
  luuNienError.value = "";
  try {
    const r = await batTuLuuNien({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    luuNienData.value = r.luu_nien;
  } catch (err) {
    luuNienError.value = err?.message || String(err);
  } finally {
    luuNienLoading.value = false;
  }
}

async function loadHonNhan() {
  if (!inputBirth.value) return;
  honNhanLoading.value = true;
  honNhanError.value = "";
  try {
    const r = await batTuHonNhan({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    honNhanData.value = r.hon_nhan;
  } catch (err) {
    honNhanError.value = err?.message || String(err);
  } finally {
    honNhanLoading.value = false;
  }
}

async function loadSuNghiep() {
  if (!inputBirth.value) return;
  suNghiepLoading.value = true;
  suNghiepError.value = "";
  try {
    const r = await batTuSuNghiep({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    suNghiepData.value = r.su_nghiep;
  } catch (err) {
    suNghiepError.value = err?.message || String(err);
  } finally {
    suNghiepLoading.value = false;
  }
}

async function loadTaiVan() {
  if (!inputBirth.value) return;
  taiVanLoading.value = true;
  taiVanError.value = "";
  try {
    const r = await batTuTaiVan({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    taiVanData.value = r.tai_van;
  } catch (err) {
    taiVanError.value = err?.message || String(err);
  } finally {
    taiVanLoading.value = false;
  }
}

async function loadHaLacLuan() {
  if (!inputBirth.value) return;
  haLacLuanLoading.value = true;
  haLacLuanError.value = "";
  try {
    const r = await haLacLuanGiai({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
    });
    haLacLuanData.value = r.luan_giai;
  } catch (err) {
    haLacLuanError.value = err?.message || String(err);
  } finally {
    haLacLuanLoading.value = false;
  }
}

// ── Derived ──────────────────────────────────────────────────────────────────

const dayMasterStem = computed(() => batTuData.value?.tu_tru?.day_master?.stem);
const dayMasterElement = computed(() => batTuData.value?.tu_tru?.day_master?.element);

const elementBarMax = computed(() => {
  if (!batTuData.value) return 1;
  const counts = batTuData.value.ngu_hanh.counts;
  return Math.max(...Object.values(counts), 1);
});

const orderedPillars = computed(() => {
  if (!batTuData.value) return [];
  const ps = batTuData.value.tu_tru.pillars;
  return ["year", "month", "day", "hour"].map((pos) => ps[pos]);
});

const orderedDecades = computed(() => haLacData.value?.decade_trajectory || []);

function cachCucPolarityClass(polarity) {
  if (!polarity) return "neutral";
  if (polarity.includes("lành") || polarity.includes("phú") || polarity.includes("quý")) return "favorable";
  if (polarity.includes("dữ") || polarity.includes("hung") || polarity.includes("phá")) return "challenging";
  return "mixed";
}

// ── Wiki popup helper — click any Thập Thần / Cách Cục / phase tag to look up
//    the canonical concept entry seeded from Thiệu Vĩ Hoa.
function openConcept(name) {
  if (!name) return;
  // Normalize: trim chinese-tail like "Chính Quan cách (正官格)" → "Chính Quan cách"
  const cleaned = String(name).replace(/\s*\([^)]+\)\s*$/, "").trim();
  openConceptPopup(cleaned);
}

// Minimal Markdown renderer for **bold** in luận giải narrative strings.
// Engine outputs short snippets only — we don't need a full MD parser.
function renderMd(s) {
  if (!s) return "";
  // Escape HTML first
  let html = String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  // **bold** → <b>
  html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  return html;
}

function formatSolarDateTime(iso) {
  if (!iso) return "";
  // "2026-05-19T22:00" → "19/05/2026 22:00"
  const [d, t] = iso.split("T");
  if (!d) return iso;
  const [y, m, day] = d.split("-");
  const time = (t || "").slice(0, 5);
  return time ? `${day}/${m}/${y} ${time}` : `${day}/${m}/${y}`;
}
</script>

<template>
  <section class="panel bt-panel">
    <div class="panel-title">
      <span>Bát Tự &amp; Hà Lạc Lý Số</span>
      <small>{{ batTuData?.method_id || "bat_tu_tu_tru_v1" }} + bat_tu_ha_lac_v1</small>
    </div>

    <p class="bt-note">
      <b>Bát Tự</b> = Tứ Trụ (Năm/Tháng/Ngày/Giờ) — phân tích Thiên Can + Địa Chi, Lục Thần,
      Ngũ Hành cân bằng. <b>Hà Lạc</b> = cross-module suy ra <b>2 quẻ Tiên thiên + Hậu thiên</b>
      của người + <b>chuỗi 12 hào ~ 84-90 năm</b> theo sách Học Năng 1974.
      <br />
      ⭐ Đây là tính năng moat — Kabala.vn có nhắc nhưng không ship.
    </p>

    <!-- Paradigm guard — Iron Rule #4 + #6: đọc đồng dạng, KHÔNG predict-tool -->
    <p class="bt-paradigm-note">
      🪷 <b>Lưu ý paradigm</b> (Thiệu Vĩ Hoa, Q1 ch.1):
      Tứ Trụ KHÔNG dự đoán anh sẽ giàu/nghèo. Tứ Trụ phản chiếu <b>cấu trúc khí bẩm sinh</b>
      tại điểm sinh + <b>lưu biến</b> theo Đại Vận. Mục đích là <em>tri mệnh</em> (biết
      mình ở đâu trong tổng thể) → cân bằng (<em>"Bổ"</em> — chìa khóa vàng Chương 2)
      → thuận tự nhiên. <small>Click các tag bên dưới để xem giải nghĩa từ wiki.</small>
    </p>

    <div class="bt-hour-uncertain">
      <button class="bt-find-hour" type="button" @click="showHourQuiz = true">
        🔍 Không nhớ giờ sinh? Tìm lại qua trắc nghiệm bát tự
      </button>
    </div>

    <div class="bt-form">
      <label>
        <span>Sinh thần (datetime-local)</span>
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
      <div class="bt-actions">
        <button class="apply-btn" @click="castAll" :disabled="loading">
          {{ loading ? "Đang luận..." : "Luận Bát Tự + Hà Lạc" }}
        </button>
        <button v-if="batTuData" class="secondary-btn" @click="reset" type="button">
          ✕ Luận lại
        </button>
      </div>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <!-- ── Bát Tự results ──────────────────────────────────────────── -->
    <template v-if="batTuData">
      <!-- Sinh thần dương + âm + tiết khí -->
      <div class="birth-summary" v-if="batTuData.tu_tru?.lunar">
        <div class="bs-row">
          <span class="bs-label">☀ Dương lịch</span>
          <span class="bs-val">{{ formatSolarDateTime(batTuData.birth_datetime_local) }}</span>
          <span class="bs-weekday">· {{ batTuData.tu_tru.lunar.weekday_vi }}</span>
        </div>
        <div class="bs-row">
          <span class="bs-label">🌙 Âm lịch</span>
          <span class="bs-val">
            ngày {{ batTuData.tu_tru.lunar.day }} tháng {{ batTuData.tu_tru.lunar.month }}{{
              batTuData.tu_tru.lunar.is_leap_month ? ' (nhuận)' : ''
            }} năm {{ batTuData.tu_tru.lunar.year }}
          </span>
          <span class="bs-ganzhi">· {{ batTuData.tu_tru.ganzhi_raw.year }} niên</span>
        </div>
        <div class="bs-row" v-if="batTuData.tu_tru.solar_term">
          <span class="bs-label">🌾 Tiết khí</span>
          <span class="bs-val">{{ batTuData.tu_tru.solar_term.name_vi }}</span>
        </div>
      </div>

      <h4 class="section-h">Tứ Trụ — 4 trụ</h4>
      <div class="pillar-grid">
        <article v-for="p in orderedPillars" :key="p.position"
          class="pillar-card" :class="{ 'is-day-master': p.position === 'day' }">
          <header class="pillar-head">
            <h5>{{ p.position_vi }}</h5>
            <small>{{ p.domain_vi }}</small>
          </header>
          <div class="pillar-stem-branch">
            <div class="pillar-stem"
              :style="{ background: ELEMENT_COLOR[p.stem_element] + '22', color: ELEMENT_COLOR[p.stem_element] }">
              <span class="char">{{ p.stem }}</span>
              <small>{{ ELEMENT_GLYPH[p.stem_element] }} {{ p.stem_element }} ({{ p.stem_polarity }})</small>
            </div>
            <div class="pillar-branch"
              :style="{ background: ELEMENT_COLOR[p.branch_element] + '15', color: ELEMENT_COLOR[p.branch_element] }">
              <span class="char">{{ p.branch }}</span>
              <small>{{ ELEMENT_GLYPH[p.branch_element] }} {{ p.branch_element }}</small>
            </div>
          </div>
          <div class="pillar-thapthan">
            <span class="tt-tag wiki-link"
              :style="{ borderColor: THAP_THAN_COLOR[p.stem_thap_than] || '#aaa', color: THAP_THAN_COLOR[p.stem_thap_than] || '#aaa' }"
              @click="openConcept(p.stem_thap_than)"
              :title="`Xem giải nghĩa Thập Thần: ${p.stem_thap_than}`">
              {{ p.stem_thap_than }}
            </span>
          </div>
          <ul class="pillar-hidden" v-if="p.hidden_stems_with_thap_than?.length">
            <li v-for="h in p.hidden_stems_with_thap_than" :key="h.stem">
              <em>{{ h.stem }}</em> → <span class="wiki-link" @click="openConcept(h.thap_than)">{{ h.thap_than }}</span>
            </li>
          </ul>
        </article>
      </div>

      <h4 class="section-h">Nhật chủ (Day Master) — {{ dayMasterStem }} ({{ dayMasterElement }})</h4>
      <div class="dm-card">
        <div class="dm-strength" :data-tag="batTuData.ngu_hanh.day_master_assessment.strength_tag">
          <span class="dm-label">Cường độ</span>
          <strong>{{ batTuData.ngu_hanh.day_master_assessment.strength_label }}</strong>
          <small>Support {{ batTuData.ngu_hanh.day_master_assessment.support_score }} · Drain {{ batTuData.ngu_hanh.day_master_assessment.drain_score }}</small>
        </div>
        <div class="dm-breakdown">
          <div v-for="(score, key) in batTuData.ngu_hanh.day_master_assessment.breakdown" :key="key" class="dm-bar">
            <span class="dm-bar-label">{{ key.replace(/_/g, ' ') }}</span>
            <div class="dm-bar-track">
              <div class="dm-bar-fill" :style="{ width: (score / elementBarMax * 100) + '%' }"></div>
            </div>
            <span class="dm-bar-value">{{ score }}</span>
          </div>
        </div>
      </div>

      <h4 class="section-h">Ngũ hành phân bố</h4>
      <div class="elements-grid">
        <div v-for="(count, el) in batTuData.ngu_hanh.counts" :key="el" class="element-cell"
          :style="{ borderLeft: '3px solid ' + ELEMENT_COLOR[el] }">
          <span class="element-name" :style="{ color: ELEMENT_COLOR[el] }">{{ ELEMENT_GLYPH[el] }} {{ el }}</span>
          <strong>{{ count }}</strong>
          <div class="element-bar">
            <div :style="{ width: (count / elementBarMax * 100) + '%', background: ELEMENT_COLOR[el] }"></div>
          </div>
        </div>
      </div>

      <!-- ── Cách Cục ────────────────────────────────────────────── -->
      <template v-if="batTuData.cach_cuc">
        <h4 class="section-h">
          <span class="wiki-link" @click="openConcept('Cách Cục')">Cách Cục</span>
          — pattern cổ điển của lá số
        </h4>
        <article class="cach-cuc-card" :data-polarity="cachCucPolarityClass(batTuData.cach_cuc.polarity)">
          <header>
            <h3 class="wiki-link" @click="openConcept(batTuData.cach_cuc.cach_name)"
              :title="`Xem giải nghĩa Cách: ${batTuData.cach_cuc.cach_name}`">
              {{ batTuData.cach_cuc.cach_name }}
            </h3>
            <span class="cc-polarity">{{ batTuData.cach_cuc.polarity }}</span>
          </header>
          <p class="cc-based-on">
            <span class="cc-label">Xác định dựa trên:</span>
            <b>{{ batTuData.cach_cuc.based_on }}</b>
            <span v-if="batTuData.cach_cuc.based_on_thap_than">
              → Thập Thần: <em class="wiki-link" @click="openConcept(batTuData.cach_cuc.based_on_thap_than)">{{ batTuData.cach_cuc.based_on_thap_than }}</em>
            </span>
          </p>
          <p class="cc-essence">{{ batTuData.cach_cuc.essence }}</p>
          <div class="cc-prosand-cons">
            <div class="cc-fav">
              <h6>✦ Thuận / Hợp</h6>
              <p>{{ batTuData.cach_cuc.favorable }}</p>
            </div>
            <div class="cc-ky">
              <h6>⚠ Kỵ / Tránh</h6>
              <p>{{ batTuData.cach_cuc.ky }}</p>
            </div>
          </div>
          <p class="cc-note"><em>{{ batTuData.cach_cuc.note }}</em></p>
        </article>
      </template>

      <!-- ── Dụng Thần / Hỷ Thần / Kỵ Thần ──────────────────────── -->
      <h4 class="section-h">
        <span class="wiki-link" @click="openConcept('Dụng Thần')">Dụng Thần</span>
        — hành cốt yếu cho nhật chủ
      </h4>
      <div class="dung-than-card">
        <div class="dt-trio">
          <div class="dt-cell dt-dung wiki-link"
            :style="{ background: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] + '15', borderColor: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] }"
            @click="openConcept('Dụng Thần')"
            title="Xem giải nghĩa Dụng Thần">
            <span class="dt-label">★ Dụng Thần</span>
            <strong :style="{ color: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] }">
              {{ ELEMENT_GLYPH[batTuData.dung_than.dung_than_element] }} {{ batTuData.dung_than.dung_than_element }}
            </strong>
            <small>{{ batTuData.dung_than.dung_than_role_vi }}</small>
          </div>
          <div class="dt-cell dt-hy wiki-link"
            :style="{ background: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] + '10', borderColor: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] + '88' }"
            @click="openConcept('Hỷ Thần')"
            title="Xem giải nghĩa Hỷ Thần">
            <span class="dt-label">Hỷ Thần</span>
            <strong :style="{ color: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] }">
              {{ ELEMENT_GLYPH[batTuData.dung_than.hy_than_element] }} {{ batTuData.dung_than.hy_than_element }}
            </strong>
            <small>hỗ trợ Dụng Thần</small>
          </div>
          <div class="dt-cell dt-ky wiki-link"
            :style="{ background: '#d65a4a0a', borderColor: '#d65a4a88' }"
            @click="openConcept('Kỵ Thần')"
            title="Xem giải nghĩa Kỵ Thần">
            <span class="dt-label">⚠ Kỵ Thần</span>
            <strong style="color: #d65a4a">
              {{ ELEMENT_GLYPH[batTuData.dung_than.ky_than_element] }} {{ batTuData.dung_than.ky_than_element }}
            </strong>
            <small>kẻ địch của Dụng Thần</small>
          </div>
        </div>
        <p class="dt-reason">{{ batTuData.dung_than.dung_than_reason }}</p>
        <p class="dt-note"><em>{{ batTuData.dung_than.note }}</em></p>
      </div>

      <!-- ── Vòng Trường Sinh ────────────────────────────────────── -->
      <h4 class="section-h">
        <span class="wiki-link" @click="openConcept('Vòng Trường Sinh')">Vòng Trường Sinh</span>
        — sức sống Day Master tại mỗi trụ
      </h4>
      <div class="truongsinh-grid">
        <article v-for="(p, pos) in batTuData.truong_sinh.pillars" :key="pos"
          class="ts-cell wiki-link" :data-score="p.strength_score >= 2 ? 'high' : p.strength_score <= -2 ? 'low' : 'mid'"
          @click="openConcept(p.phase)"
          :title="`Xem giải nghĩa giai đoạn: ${p.phase}`">
          <header>
            <h6>{{ p.pillar_position_vi }}</h6>
            <small>{{ p.branch }}</small>
          </header>
          <strong>{{ p.phase }}</strong>
          <span class="ts-score" :data-positive="p.strength_score > 0">
            {{ p.strength_score >= 0 ? '+' : '' }}{{ p.strength_score }}
          </span>
        </article>
      </div>
      <p class="ts-total">
        Tổng điểm sức sống: <b>{{ batTuData.truong_sinh.total_strength_score }}</b>
        — Trường Sinh khởi tại {{ batTuData.truong_sinh.truong_sinh_start_branch }}.
      </p>

      <!-- ── Thần Sát ─────────────────────────────────────────────── -->
      <h4 class="section-h">
        <span class="wiki-link" @click="openConcept('Thần Sát')">Thần Sát</span>
        — sao phụ trong lá số
      </h4>
      <div v-if="!batTuData.than_sat.length" class="ts-empty">
        Lá số này không có sao Thần Sát nào trong 15 sao cốt lõi đang sàng.
      </div>
      <ul v-else class="than-sat-list">
        <li v-for="(s, i) in batTuData.than_sat" :key="i" class="ts-star" :data-polarity="s.polarity">
          <div class="ts-star-head">
            <strong class="wiki-link" @click="openConcept(s.name)"
              :title="`Xem giải nghĩa sao: ${s.name}`">{{ s.name }}</strong>
            <span class="ts-tag">{{ s.short_tag }}</span>
            <span class="ts-polarity">{{ s.polarity }}</span>
            <small class="ts-where">tại trụ {{ s.found_at_pillar }} ({{ s.branch_or_stem }})</small>
          </div>
          <p class="ts-desc">{{ s.description }}</p>
        </li>
      </ul>

      <!-- ── Đại Vận ──────────────────────────────────────────────── -->
      <h4 class="section-h">
        <span class="wiki-link" @click="openConcept('Đại Vận')">Đại Vận</span>
        — chu kỳ 10 năm
      </h4>
      <p class="dv-meta">
        Hướng: <b>{{ batTuData.dai_van.direction_label }}</b> ·
        Tuổi bắt đầu vận: <b>{{ batTuData.dai_van.starting_age }}</b>
        <small>({{ batTuData.dai_van.starting_age_estimation }})</small>
        <span v-if="batTuData.dai_van.distance_days_to_reference_tiet_khi !== null && batTuData.dai_van.distance_days_to_reference_tiet_khi !== undefined" class="dv-distance">
          · {{ batTuData.dai_van.distance_days_to_reference_tiet_khi }} ngày từ tiết khí gần nhất
          <small v-if="batTuData.dai_van.reference_tiet_khi_date">
            ({{ batTuData.dai_van.reference_tiet_khi_date.slice(0, 10) }})
          </small>
        </span>
      </p>
      <ol class="dai-van-list">
        <li v-for="c in batTuData.dai_van.cycles" :key="c.cycle_index" class="dv-cycle">
          <div class="dv-age">
            <strong>{{ c.start_age }}-{{ c.end_age }}</strong>
            <small>tuổi</small>
          </div>
          <div class="dv-stembr">
            <span class="dv-stem">{{ c.stem }}</span>
            <span class="dv-branch">{{ c.branch }}</span>
          </div>
          <span class="dv-index">V{{ c.cycle_index }}</span>
        </li>
      </ol>
      <p class="dv-note" v-if="batTuData.dai_van.starting_age_note">
        <em>{{ batTuData.dai_van.starting_age_note }}</em>
      </p>
    </template>

    <!-- ── Hà Lạc results ──────────────────────────────────────────── -->
    <template v-if="haLacData">
      <h4 class="section-h ha-lac-h">
        ⭐ Hà Lạc Lý Số — 2 quẻ cốt mệnh
      </h4>
      <p class="ha-lac-intro">
        Thiên số <b>{{ haLacData.number_pools.tien_raw }}</b> → {{ haLacData.number_pools.tien_reduced }} ·
        Địa số <b>{{ haLacData.number_pools.dia_raw }}</b> → {{ haLacData.number_pools.dia_reduced }}
        · Năm {{ haLacData.year_stem_polarity }} ({{ haLacData.gender }})
      </p>

      <div class="halac-quai-pair">
        <article class="halac-quai" data-which="tien">
          <header>
            <h5>Tiên thiên quái (先天卦)</h5>
            <small>Mệnh cốt — gốc đời người</small>
          </header>
          <div class="halac-quai-body" @click="openHexagram(haLacData.tien_thien_quai.king_wen_index)" title="Mở chi tiết quẻ">
            <HexagramImage :king-wen="haLacData.tien_thien_quai.king_wen_index" :size="80" />
            <div>
              <strong>{{ haLacData.tien_thien_quai.name_vi }}</strong>
              <small>quẻ {{ haLacData.tien_thien_quai.king_wen_index }}</small>
              <p>Thượng: {{ haLacData.tien_thien_quai.upper_trigram }} / Hạ: {{ haLacData.tien_thien_quai.lower_trigram }}</p>
              <p class="nd-tag">🌟 Nguyên đường: <b>hào {{ haLacData.tien_thien_quai.nguyen_duong_line }}</b></p>
            </div>
          </div>
        </article>

        <div class="halac-arrow">→</div>

        <article class="halac-quai" data-which="hau">
          <header>
            <h5>Hậu thiên quái (後天卦)</h5>
            <small>Vận dụng — cách thức vận hành</small>
          </header>
          <div class="halac-quai-body" @click="openHexagram(haLacData.hau_thien_quai.king_wen_index)" title="Mở chi tiết quẻ">
            <HexagramImage :king-wen="haLacData.hau_thien_quai.king_wen_index" :size="80" />
            <div>
              <strong>{{ haLacData.hau_thien_quai.name_vi }}</strong>
              <small>quẻ {{ haLacData.hau_thien_quai.king_wen_index }}</small>
              <p>Thượng: {{ haLacData.hau_thien_quai.upper_trigram }} / Hạ: {{ haLacData.hau_thien_quai.lower_trigram }}</p>
              <p class="nd-tag">🌟 Nguyên đường: <b>hào {{ haLacData.hau_thien_quai.nguyen_duong_line }}</b></p>
            </div>
          </div>
        </article>
      </div>

      <h4 class="section-h">Lộ trình 12 hào — {{ haLacData.lifespan_span.total_years }} năm cuộc đời</h4>
      <ol class="trajectory">
        <li v-for="stage in orderedDecades" :key="stage.stage_index"
          class="traj-stage"
          :class="{ 'is-nd': stage.is_nguyen_duong, [`is-${stage.hexagram}`]: true, [`pol-${stage.polarity}`]: true }">
          <div class="traj-age">
            <strong>{{ stage.age_start }}-{{ stage.age_end }}</strong>
            <small>tuổi</small>
          </div>
          <div class="traj-info">
            <span class="traj-label">{{ stage.label }}</span>
            <span class="traj-meta">{{ stage.hexagram === 'tien' ? 'Tiên thiên' : 'Hậu thiên' }} · hào {{ stage.line_position }} · {{ stage.polarity }}</span>
          </div>
        </li>
      </ol>

      <p v-if="haLacData.notes?.length" class="halac-notes-block">
        <b>Ghi chú thuật toán:</b>
        <span v-for="(n, i) in haLacData.notes" :key="i">{{ n }}</span>
      </p>

      <p class="halac-interpretation">
        <b>Hướng diễn giải:</b> {{ haLacData.interpretation_hint }}
      </p>

      <p class="footer-ref">Nguồn: {{ haLacData.source_ref }}</p>
    </template>

    <!-- ── Luận Giải Tổng Hợp ──────────────────────────────────────────────
         Synthesizer engine — Thiệu Vĩ Hoa Q1 Chương 1-3 paradigm-tone narrative.
    -->
    <div v-if="batTuData" class="luan-giai-trigger">
      <button v-if="!luanGiaiData" class="apply-btn lg-trigger-btn"
        @click="loadLuanGiai" :disabled="luanGiaiLoading">
        {{ luanGiaiLoading ? "Đang luận giải tổng hợp..." : "📜 Luận Giải Tổng Hợp (Thiệu Vĩ Hoa)" }}
      </button>
      <p v-if="luanGiaiError" class="status-message error">{{ luanGiaiError }}</p>
    </div>

    <template v-if="luanGiaiData">
      <h4 class="section-h lg-h">📜 Luận Giải Tổng Hợp — paradigm Thiệu Vĩ Hoa</h4>
      <p class="lg-paradigm">{{ luanGiaiData.paradigm_guard }}</p>

      <!-- Overview -->
      <div class="lg-block lg-overview" v-html="renderMd(luanGiaiData.overview)"></div>

      <!-- Cường độ Nhật Chủ -->
      <div class="lg-block">
        <h5 class="lg-section-title">⚖ Cường độ Nhật Chủ</h5>
        <div class="lg-strength-row" :data-tag="luanGiaiData.cuong_do_nhat_chu.tag">
          <span class="lg-tag">{{ luanGiaiData.cuong_do_nhat_chu.label }}</span>
          <small>Support {{ luanGiaiData.cuong_do_nhat_chu.support_score }} ·
            Drain {{ luanGiaiData.cuong_do_nhat_chu.drain_score }} ·
            Δ {{ luanGiaiData.cuong_do_nhat_chu.diff.toFixed(1) }}</small>
        </div>
        <p v-html="renderMd(luanGiaiData.cuong_do_nhat_chu.narrative)"></p>
      </div>

      <!-- Ngũ Hành Balance -->
      <div class="lg-block">
        <h5 class="lg-section-title">🌳🔥🌍⚒️💧 Ngũ Hành Balance</h5>
        <p v-html="renderMd(luanGiaiData.ngu_hanh_balance.narrative)"></p>
        <p v-if="luanGiaiData.ngu_hanh_balance.can_bo?.length" class="lg-can-bo">
          🎯 <b>Cần BỔ</b>: {{ luanGiaiData.ngu_hanh_balance.can_bo.join(", ") }}
        </p>
      </div>

      <!-- Cách Cục -->
      <div v-if="luanGiaiData.cach_cuc_luan.present" class="lg-block lg-cach-cuc">
        <h5 class="lg-section-title">🎴 Cách Cục</h5>
        <p v-html="renderMd(luanGiaiData.cach_cuc_luan.narrative)"></p>
      </div>

      <!-- Extreme Pattern (Tòng / Hóa Khí / Five Special) — EDGE CASE -->
      <div v-if="luanGiaiData.extreme_pattern_luan" class="lg-block lg-extreme"
        :data-type="luanGiaiData.extreme_pattern_luan.type">
        <h5 class="lg-section-title">
          {{ luanGiaiData.extreme_pattern_luan.type_label }} — paradigm ĐẢO NGƯỢC
        </h5>
        <p v-html="renderMd(luanGiaiData.extreme_pattern_luan.narrative)"></p>
        <div class="lg-extreme-trio">
          <span class="lg-ext-cell lg-ext-dung">★ Dụng: <b>{{ luanGiaiData.extreme_pattern_luan.dung_than_element.toUpperCase() }}</b></span>
          <span class="lg-ext-cell lg-ext-hy">Hỷ: <b>{{ luanGiaiData.extreme_pattern_luan.hy_than_element.toUpperCase() }}</b></span>
          <span class="lg-ext-cell lg-ext-ky">⚠ Kỵ: <b>{{ luanGiaiData.extreme_pattern_luan.ky_than_element.toUpperCase() }}</b></span>
        </div>
        <small class="lg-ext-conf">Confidence: {{ luanGiaiData.extreme_pattern_luan.confidence }} · {{ luanGiaiData.extreme_pattern_luan.notes }}</small>
      </div>

      <!-- Dụng Thần -->
      <div class="lg-block lg-dung-than">
        <h5 class="lg-section-title">★ Dụng Thần — thuốc cứu mệnh</h5>
        <p v-html="renderMd(luanGiaiData.dung_than_luan.narrative)"></p>
      </div>

      <!-- Thập Thần dominant -->
      <div v-if="luanGiaiData.thap_than_pattern.profiles?.length" class="lg-block">
        <h5 class="lg-section-title">🌟 Thập Thần nổi bật — tâm tính + công năng</h5>
        <article v-for="p in luanGiaiData.thap_than_pattern.profiles" :key="p.name" class="lg-tt-profile">
          <header>
            <strong class="wiki-link" @click="openConcept(p.name)">{{ p.name }}</strong>
            <span class="lg-tt-weight">trọng số {{ p.weight.toFixed(0) }}</span>
          </header>
          <p><b>Tích cực</b>: {{ p.tich_cuc }}</p>
          <p><b>Tiêu cực</b>: {{ p.tieu_cuc }}</p>
          <p class="lg-tt-cong-nang" v-html="renderMd(p.cong_nang)"></p>
        </article>
      </div>

      <!-- Favorable combinations -->
      <div v-if="luanGiaiData.favorable_combinations?.length" class="lg-block lg-favorable">
        <h5 class="lg-section-title">✦ Cấu hình thuận lợi (cổ điển)</h5>
        <article v-for="fc in luanGiaiData.favorable_combinations" :key="fc.name" class="lg-fc">
          <strong>✦ {{ fc.name }}</strong>
          <p>{{ fc.narrative }}</p>
        </article>
      </div>

      <!-- Warnings -->
      <div v-if="luanGiaiData.warnings?.length" class="lg-block lg-warnings">
        <h5 class="lg-section-title">⚠ Cảnh báo (cấu hình cần đề phòng)</h5>
        <article v-for="w in luanGiaiData.warnings" :key="w.name" class="lg-warn">
          <strong>⚠ {{ w.name }}</strong>
          <p>{{ w.narrative }}</p>
        </article>
      </div>

      <!-- Thông quan -->
      <div v-if="luanGiaiData.thong_quan" class="lg-block lg-thong-quan">
        <h5 class="lg-section-title">🌉 Thông Quan</h5>
        <p v-html="renderMd(luanGiaiData.thong_quan.narrative)"></p>
      </div>

      <!-- Trường Sinh -->
      <div class="lg-block">
        <h5 class="lg-section-title">⏳ Vòng Trường Sinh — sức sống tổng thể</h5>
        <p v-html="renderMd(luanGiaiData.truong_sinh_luan.narrative)"></p>
      </div>

      <!-- Thần Sát Highlights -->
      <div v-if="luanGiaiData.than_sat_highlights.present" class="lg-block">
        <h5 class="lg-section-title">✨ Thần Sát nổi bật</h5>
        <p v-html="renderMd(luanGiaiData.than_sat_highlights.narrative)"></p>
        <ul class="lg-stars">
          <li v-for="s in luanGiaiData.than_sat_highlights.highlights" :key="s.name"
            :data-polarity="s.polarity">
            <strong class="wiki-link" @click="openConcept(s.name)">{{ s.name }}</strong>
            <span class="lg-star-polarity">({{ s.polarity }})</span>
            <small>tại trụ {{ s.pillar }}</small>
          </li>
        </ul>
      </div>

      <!-- Đại Vận hiện tại -->
      <div class="lg-block lg-dv-current">
        <h5 class="lg-section-title">🌀 Đại Vận hiện tại</h5>
        <p v-html="renderMd(luanGiaiData.dai_van_current.narrative)"></p>
      </div>

      <!-- Bổ hướng (actionable) -->
      <div class="lg-block lg-bo-huong">
        <h5 class="lg-section-title">🎯 Bổ Hướng — chìa khóa vàng (actionable)</h5>
        <p v-html="renderMd(luanGiaiData.bo_huong.narrative)"></p>
        <div class="lg-bo-grid">
          <article v-for="(rec, key) in luanGiaiData.bo_huong.recommend" :key="key" class="lg-bo-cell"
            :data-role="key">
            <header>
              <strong>{{ key === 'dung' ? '★ Dụng Thần' : 'Hỷ Thần' }}: {{ rec.element.toUpperCase() }}</strong>
            </header>
            <div class="lg-bo-cat">
              <small>💼 Nghề</small>
              <span>{{ rec.nghe_nghiep.slice(0, 5).join(" · ") }}{{ rec.nghe_nghiep.length > 5 ? '...' : '' }}</span>
            </div>
            <div class="lg-bo-cat">
              <small>🎨 Màu</small>
              <span>{{ rec.mau_sac.join(" · ") }}</span>
            </div>
            <div class="lg-bo-cat">
              <small>🧭 Phương</small>
              <span>{{ rec.phuong_vi.join(" · ") }}</span>
            </div>
            <div class="lg-bo-cat">
              <small>🍲 Ẩm thực</small>
              <span>{{ rec.am_thuc.join(" · ") }}</span>
            </div>
          </article>
        </div>
        <div v-if="luanGiaiData.bo_huong.tranh" class="lg-bo-tranh">
          <strong>⚠ Tránh (Kỵ Thần: {{ luanGiaiData.bo_huong.tranh.element.toUpperCase() }})</strong>
          — không phải tránh hoàn toàn, mà giảm liều lượng.
          Phương: {{ luanGiaiData.bo_huong.tranh.phuong_vi.join(", ") }}.
          Màu: {{ luanGiaiData.bo_huong.tranh.mau_sac.join(", ") }}.
        </div>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(luanGiaiData.closing)"></div>
    </template>

    <!-- ── Lưu Niên — Năm hiện tại ──────────────────────────────────────────
         Engine luu_nien — phân tích năm + 12 tháng + Đại Vận hiện tại.
    -->
    <div v-if="batTuData" class="luu-nien-trigger">
      <button v-if="!luuNienData" class="apply-btn ln-trigger-btn"
        @click="loadLuuNien" :disabled="luuNienLoading">
        {{ luuNienLoading ? "Đang phân tích Lưu Niên..." : "🌀 Lưu Niên — Năm hiện tại" }}
      </button>
      <p v-if="luuNienError" class="status-message error">{{ luuNienError }}</p>
    </div>

    <template v-if="luuNienData">
      <h4 class="section-h ln-h">
        🌀 Lưu Niên {{ luuNienData.target_year }} — Năm
        <b class="ln-ganzhi">{{ luuNienData.luu_nien.stem }} {{ luuNienData.luu_nien.branch }}</b>
        đi qua lá số
      </h4>
      <p class="lg-paradigm">{{ luuNienData.paradigm_guard }}</p>

      <!-- Overall verdict header -->
      <div class="lg-block ln-overall" :data-verdict="luuNienData.overall_verdict.verdict">
        <h5 class="lg-section-title">📊 Đánh giá tổng năm</h5>
        <div class="ln-verdict-row">
          <span class="ln-verdict-tag">{{ luuNienData.overall_verdict.verdict.toUpperCase() }}</span>
          <small>Thập Thần năm:
            <span class="wiki-link" @click="openConcept(luuNienData.luu_nien.thap_than_vs_dm)">
              {{ luuNienData.luu_nien.thap_than_vs_dm }}
            </span>
            · Hành {{ luuNienData.luu_nien.stem_element.toUpperCase() }}/{{ luuNienData.luu_nien.branch_element.toUpperCase() }}
          </small>
        </div>
        <p v-html="renderMd(luuNienData.overall_verdict.narrative)"></p>
      </div>

      <!-- Tương tác Lưu Niên vs 4 trụ gốc -->
      <div class="lg-block">
        <h5 class="lg-section-title">⚖ Tương tác với 4 Trụ gốc</h5>
        <div class="ln-pillars-grid">
          <article v-for="(info, pos) in luuNienData.vs_chart.vs_pillars" :key="pos" class="ln-pillar-cell">
            <header>
              <strong>{{ info.pillar_position_vi }}</strong>
              <small>{{ info.natal_stem }} {{ info.natal_branch }}</small>
            </header>
            <div class="ln-inter-row" :data-polarity="info.stem_interaction.polarity">
              <small>Can</small>
              <span>{{ info.stem_interaction.type }}</span>
            </div>
            <div v-for="(ci, i) in info.chi_interactions" :key="i" class="ln-inter-row" :data-polarity="ci.polarity">
              <small>Chi</small>
              <span>{{ ci.type }}</span>
            </div>
            <div v-if="!info.chi_interactions.length" class="ln-inter-row" data-polarity="trung">
              <small>Chi</small>
              <span style="opacity:0.5">không tương tác</span>
            </div>
          </article>
        </div>
        <div v-if="luuNienData.vs_chart.tam_hop_detected.length" class="ln-tam-hop">
          <h6>🌀 Tam Hợp / Bán Hợp với Lưu Niên</h6>
          <p v-for="(th, i) in luuNienData.vs_chart.tam_hop_detected" :key="i">{{ th.narrative }}</p>
        </div>
      </div>

      <!-- Vs Đại Vận hiện tại -->
      <div v-if="luuNienData.vs_dai_van.current_dai_van" class="lg-block ln-vs-dv">
        <h5 class="lg-section-title">🌊 Lưu Niên vs Đại Vận hiện tại</h5>
        <p v-html="renderMd(luuNienData.vs_dai_van.narrative)"></p>
      </div>

      <!-- 12 tháng Lưu Nguyệt -->
      <div v-if="luuNienData.luu_nguyet?.length" class="lg-block ln-luu-nguyet">
        <h5 class="lg-section-title">🗓 12 Tháng — Lưu Nguyệt theo Tiết khí</h5>
        <p class="ln-month-legend">
          <small>
            ✦ <b>thuận</b> · ⚖ <b>hỗn tạp</b> · ⚠ <b>thử thách</b> · · <b>trung tính</b>
          </small>
        </p>
        <div class="ln-month-grid">
          <article v-for="m in luuNienData.luu_nguyet" :key="m.month_index" class="ln-month-cell"
            :data-verdict="m.verdict">
            <header>
              <strong>Tháng {{ m.month_index }}</strong>
              <small>{{ m.tiet_khi }}</small>
            </header>
            <div class="ln-month-gz">{{ m.stem }} {{ m.branch }}</div>
            <div class="ln-month-tt wiki-link" @click="openConcept(m.thap_than)">{{ m.thap_than }}</div>
            <div class="ln-month-marker">{{ m.short_marker }} {{ m.verdict }}</div>
          </article>
        </div>
      </div>

      <!-- Bổ Hướng năm -->
      <div class="lg-block lg-bo-huong ln-bo">
        <h5 class="lg-section-title">🎯 Bổ Hướng cho năm {{ luuNienData.target_year }}</h5>
        <p v-html="renderMd(luuNienData.bo_huong_nam.narrative)"></p>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(luuNienData.closing)"></div>
    </template>

    <!-- ── Hôn Nhân ─────────────────────────────────────────────────────────
         Engine hon_nhan — Cung Phối + Tài/Quan stars + thời điểm.
    -->
    <div v-if="batTuData" class="hn-trigger-section">
      <button v-if="!honNhanData" class="apply-btn hn-trigger-btn"
        @click="loadHonNhan" :disabled="honNhanLoading">
        {{ honNhanLoading ? "Đang phân tích Hôn nhân..." : "💞 Hôn Nhân — Cung Phối + Tài/Quan" }}
      </button>
      <p v-if="honNhanError" class="status-message error">{{ honNhanError }}</p>
    </div>

    <template v-if="honNhanData">
      <h4 class="section-h hn-h">💞 Hôn Nhân — đọc cấu trúc Cung Phối</h4>
      <p class="lg-paradigm">{{ honNhanData.paradigm_guard }}</p>

      <!-- Overall verdict -->
      <div class="lg-block hn-overall" :data-label="honNhanData.overall.label">
        <h5 class="lg-section-title">📊 Đánh giá cấu trúc</h5>
        <div class="hn-verdict-row">
          <span class="hn-verdict-tag">{{ honNhanData.overall.label.toUpperCase() }}</span>
          <small>điểm cấu hình: {{ honNhanData.overall.score }}</small>
        </div>
        <p>{{ honNhanData.overall.narrative }}</p>
      </div>

      <!-- Cung Phối -->
      <div class="lg-block">
        <h5 class="lg-section-title">🏠 Cung Phối — Trụ Ngày
          <span class="wiki-link" @click="openConcept(honNhanData.cung_phoi.branch)">
            chi {{ honNhanData.cung_phoi.branch }}
          </span>
          ({{ honNhanData.cung_phoi.branch_element }})
        </h5>
        <p>{{ honNhanData.cung_phoi.trait_narrative }}</p>
        <div v-if="honNhanData.cung_phoi.tang_can?.length" class="hn-tang-can">
          <small><b>Tàng can</b>:</small>
          <span v-for="t in honNhanData.cung_phoi.tang_can" :key="t.stem" class="hn-tang-item">
            <em>{{ t.stem }}</em> →
            <span class="wiki-link" @click="openConcept(t.thap_than)">{{ t.thap_than }}</span>
          </span>
        </div>
        <div v-if="honNhanData.cung_phoi.interactions_with_other_pillars?.length" class="hn-interactions">
          <small><b>Tương tác với 3 trụ khác</b>:</small>
          <ul>
            <li v-for="(inter, i) in honNhanData.cung_phoi.interactions_with_other_pillars" :key="i"
              :data-polarity="inter.polarity">{{ inter.narrative }}</li>
          </ul>
        </div>
        <p v-if="honNhanData.cung_phoi.dao_hoa_chi" class="hn-dao-hoa">
          🌸 <b>Đào hoa</b> của lá số: chi {{ honNhanData.cung_phoi.dao_hoa_chi }}
          ({{ honNhanData.cung_phoi.has_dao_hoa_in_chart ? "✓ XUẤT HIỆN trong Tứ Trụ" : "không xuất hiện trong Tứ Trụ" }})
        </p>
      </div>

      <!-- Partner Star -->
      <div class="lg-block">
        <h5 class="lg-section-title">⭐ Star vợ/chồng
          ({{ honNhanData.gender === "nam" ? "Tài tinh" : "Quan tinh" }})
        </h5>
        <p>
          Tổng số đếm: <b>{{ honNhanData.partner_star.total_count }}</b>.
          Main star: <span class="wiki-link" @click="openConcept(honNhanData.partner_star.main_star)">{{ honNhanData.partner_star.main_star }}</span>,
          phụ: <span class="wiki-link" @click="openConcept(honNhanData.partner_star.secondary_star)">{{ honNhanData.partner_star.secondary_star }}</span>.
        </p>
        <div v-if="honNhanData.partner_star.visible_positions?.length" class="hn-star-list">
          <small><b>Hiện rõ</b>:</small>
          <ul><li v-for="(pos, i) in honNhanData.partner_star.visible_positions" :key="i">{{ pos }}</li></ul>
        </div>
        <div v-if="honNhanData.partner_star.hidden_positions?.length" class="hn-star-list">
          <small><b>Ẩn (tàng can)</b>:</small>
          <ul><li v-for="(pos, i) in honNhanData.partner_star.hidden_positions" :key="i">{{ pos }}</li></ul>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="honNhanData.warnings?.length" class="lg-block lg-warnings">
        <h5 class="lg-section-title">⚠ Cảnh báo cấu hình</h5>
        <article v-for="w in honNhanData.warnings" :key="w.name" class="lg-warn">
          <strong>⚠ {{ w.name }}</strong>
          <p>{{ w.narrative }}</p>
        </article>
      </div>

      <!-- Special stars -->
      <div v-if="Object.keys(honNhanData.special_stars).length" class="lg-block">
        <h5 class="lg-section-title">✨ Sao đặc biệt</h5>
        <ul class="hn-stars">
          <li v-for="(info, name) in honNhanData.special_stars" :key="name" :data-polarity="info.polarity">
            <strong class="wiki-link" @click="openConcept(name)">{{ name }}</strong>
            <span>({{ info.polarity }}) tại {{ info.pillar }}</span>
          </li>
        </ul>
      </div>

      <!-- Timing suggestions -->
      <div class="lg-block hn-timing">
        <h5 class="lg-section-title">⏳ Thời điểm khả thi (theo Đại Vận)</h5>
        <p>{{ honNhanData.timing_suggestions.narrative }}</p>
        <div v-if="honNhanData.timing_suggestions.favorable_cycles?.length" class="hn-fav-cycles">
          <article v-for="c in honNhanData.timing_suggestions.favorable_cycles" :key="c.cycle_index" class="hn-cycle-cell">
            <header>
              <strong>V{{ c.cycle_index }} {{ c.stem }} {{ c.branch }}</strong>
              <small>{{ c.start_age }}-{{ c.end_age }}t · điểm {{ c.score }}</small>
            </header>
            <ul>
              <li v-for="(r, i) in c.reasons" :key="i">{{ r }}</li>
            </ul>
          </article>
        </div>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(honNhanData.closing)"></div>
    </template>

    <!-- ── Sự Nghiệp ──────────────────────────────────────────────────────
         Engine su_nghiep — Cách Cục + Dụng Thần + Thập Thần patterns.
    -->
    <div v-if="batTuData" class="sn-trigger-section">
      <button v-if="!suNghiepData" class="apply-btn sn-trigger-btn"
        @click="loadSuNghiep" :disabled="suNghiepLoading">
        {{ suNghiepLoading ? "Đang phân tích Sự nghiệp..." : "💼 Sự Nghiệp — Cách Cục + Dụng Thần" }}
      </button>
      <p v-if="suNghiepError" class="status-message error">{{ suNghiepError }}</p>
    </div>

    <template v-if="suNghiepData">
      <h4 class="section-h sn-h">💼 Sự Nghiệp — đọc hành thuận + cách cục</h4>
      <p class="lg-paradigm">{{ suNghiepData.paradigm_guard }}</p>

      <!-- Cách Cục summary -->
      <div class="lg-block sn-cach">
        <h5 class="lg-section-title">🎴 Cách Cục
          <span class="wiki-link" @click="openConcept(suNghiepData.cach_cuc_summary.name)">
            {{ suNghiepData.cach_cuc_summary.name }}
          </span>
        </h5>
        <p><b>Career style</b>: {{ suNghiepData.cach_cuc_summary.career_style }}</p>
        <p>{{ suNghiepData.cach_cuc_summary.narrative }}</p>
      </div>

      <!-- Career patterns -->
      <div v-if="suNghiepData.career_patterns?.length" class="lg-block">
        <h5 class="lg-section-title">🌀 Patterns phát hiện</h5>
        <article v-for="p in suNghiepData.career_patterns" :key="p.name" class="sn-pattern">
          <strong>✦ {{ p.name }}</strong>
          <p>{{ p.narrative }}</p>
          <p class="sn-hint">💡 <em>Hint</em>: {{ p.career_hint }}</p>
        </article>
      </div>

      <!-- Dominant Thập Thần styles -->
      <div v-if="suNghiepData.dominant_thap_than_styles?.length" class="lg-block">
        <h5 class="lg-section-title">🌟 Thập Thần nổi bật — career style</h5>
        <ul class="sn-styles">
          <li v-for="d in suNghiepData.dominant_thap_than_styles" :key="d.name">
            <strong class="wiki-link" @click="openConcept(d.name)">{{ d.name }}</strong>:
            {{ d.style }}
          </li>
        </ul>
      </div>

      <!-- Recommendations -->
      <div class="lg-block sn-rec">
        <h5 class="lg-section-title">🎯 Recommend ngành nghề</h5>
        <div class="sn-rec-grid">
          <article class="sn-rec-cell" data-role="dung">
            <header>
              <strong>★ Dụng Thần: {{ suNghiepData.recommendations.by_dung_than.element.toUpperCase() }}</strong>
            </header>
            <div v-for="ind in suNghiepData.recommendations.by_dung_than.industries" :key="ind.category" class="sn-ind">
              <strong>{{ ind.category }}</strong>
              <small>{{ ind.examples }}</small>
            </div>
          </article>
          <article class="sn-rec-cell" data-role="hy">
            <header>
              <strong>Hỷ Thần: {{ suNghiepData.recommendations.by_hy_than.element.toUpperCase() }}</strong>
            </header>
            <div v-for="ind in suNghiepData.recommendations.by_hy_than.industries" :key="ind.category" class="sn-ind">
              <strong>{{ ind.category }}</strong>
              <small>{{ ind.examples }}</small>
            </div>
          </article>
        </div>
        <div class="sn-cach-list">
          <h6>Theo Cách Cục:</h6>
          <ul>
            <li v-for="ind in suNghiepData.recommendations.by_cach_cuc" :key="ind">{{ ind }}</li>
          </ul>
        </div>
      </div>

      <!-- Avoid -->
      <div class="lg-block sn-avoid">
        <h5 class="lg-section-title">⚠ Giảm liều lượng (Kỵ Thần)</h5>
        <p>{{ suNghiepData.avoid.narrative }}</p>
        <ul class="sn-avoid-list">
          <li v-for="ind in suNghiepData.avoid.from_ky_than" :key="ind.category">{{ ind.category }}</li>
        </ul>
      </div>

      <!-- Timing by Đại Vận -->
      <div v-if="suNghiepData.timing_by_dai_van?.length" class="lg-block sn-timing">
        <h5 class="lg-section-title">⏳ Thời điểm phát triển (Đại Vận)</h5>
        <div class="sn-dv-grid">
          <article v-for="c in suNghiepData.timing_by_dai_van" :key="c.cycle_index"
            class="sn-dv-cell" :data-verdict="c.verdict">
            <header>
              <strong>V{{ c.cycle_index }}</strong>
              <small>{{ c.start_age }}-{{ c.end_age }}t</small>
            </header>
            <div class="sn-dv-gz">{{ c.stem }} {{ c.branch }}</div>
            <div class="sn-dv-mark">{{ c.mark }} {{ c.verdict }}</div>
          </article>
        </div>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(suNghiepData.closing)"></div>
    </template>

    <!-- ── Tài Vận ──────────────────────────────────────────────────────────
         Engine tai_van — Tài tinh + DM balance + 6 patterns + Đại Vận tài.
    -->
    <div v-if="batTuData" class="tv-trigger-section">
      <button v-if="!taiVanData" class="apply-btn tv-trigger-btn"
        @click="loadTaiVan" :disabled="taiVanLoading">
        {{ taiVanLoading ? "Đang phân tích Tài Vận..." : "💰 Tài Vận — Tài tinh + Đại Vận tài" }}
      </button>
      <p v-if="taiVanError" class="status-message error">{{ taiVanError }}</p>
    </div>

    <template v-if="taiVanData">
      <h4 class="section-h tv-h">💰 Tài Vận — đọc cấu hình khí tài</h4>
      <p class="lg-paradigm">{{ taiVanData.paradigm_guard }}</p>

      <!-- DM-Tài Balance (header verdict) -->
      <div class="lg-block tv-balance" :data-polarity="taiVanData.dm_tai_balance.polarity">
        <h5 class="lg-section-title">⚖ Day Master vs Tài tinh</h5>
        <div class="tv-balance-row">
          <span class="tv-balance-tag">{{ taiVanData.dm_tai_balance.status.toUpperCase() }}</span>
          <small>polarity: {{ taiVanData.dm_tai_balance.polarity }}</small>
        </div>
        <p>{{ taiVanData.dm_tai_balance.narrative }}</p>
        <p class="tv-recommend">💡 <b>Recommend</b>: {{ taiVanData.dm_tai_balance.recommend }}</p>
      </div>

      <!-- Tài Map (positions) -->
      <div class="lg-block">
        <h5 class="lg-section-title">📍 Tài Tinh Map (vị trí trong lá số)</h5>
        <div class="tv-map-row">
          <span class="tv-map-stat"><b>Chính Tài</b>: {{ taiVanData.tai_map.total_chinh_tai }}</span>
          <span class="tv-map-stat"><b>Thiên Tài</b>: {{ taiVanData.tai_map.total_thien_tai }}</span>
          <span class="tv-map-stat">Tổng: <b>{{ taiVanData.tai_map.total_count }}</b></span>
        </div>
        <ul v-if="taiVanData.tai_map.chinh_tai_positions.length || taiVanData.tai_map.thien_tai_positions.length" class="tv-positions">
          <li v-for="(p, i) in taiVanData.tai_map.chinh_tai_positions" :key="'c'+i" data-type="chinh">
            <strong class="wiki-link" @click="openConcept('Chính Tài')">Chính Tài</strong>
            tại <em>{{ p.position_vi }}</em> ({{ p.type === 'visible_stem' ? 'thiên can' : 'tàng can ' + p.branch }}: {{ p.stem }})
          </li>
          <li v-for="(p, i) in taiVanData.tai_map.thien_tai_positions" :key="'t'+i" data-type="thien">
            <strong class="wiki-link" @click="openConcept('Thiên Tài')">Thiên Tài</strong>
            tại <em>{{ p.position_vi }}</em> ({{ p.type === 'visible_stem' ? 'thiên can' : 'tàng can ' + p.branch }}: {{ p.stem }})
          </li>
        </ul>
      </div>

      <!-- Sources -->
      <div class="lg-block">
        <h5 class="lg-section-title">🎯 Nguồn Tài (Chính / Thiên)</h5>
        <article v-for="s in taiVanData.sources" :key="s.type" class="tv-source">
          <header>
            <strong>{{ s.type }}</strong>
            <small>x{{ s.count }}</small>
          </header>
          <p><b>Bản chất</b>: {{ s.essence }}</p>
          <p><b>Hợp</b>: {{ s.favorable }}</p>
          <p class="tv-source-ky"><b>Kỵ</b>: {{ s.kỵ || s["kỵ"] }}</p>
          <p><b>Nghề</b>: {{ s.career }}</p>
        </article>
      </div>

      <!-- Patterns -->
      <div v-if="taiVanData.patterns?.length" class="lg-block">
        <h5 class="lg-section-title">🌀 Patterns phát hiện</h5>
        <article v-for="p in taiVanData.patterns" :key="p.name" class="tv-pattern"
          :data-polarity="p.polarity.includes('lành') || p.polarity.includes('quý') ? 'positive' : (p.polarity.includes('cảnh') ? 'warning' : 'neutral')">
          <header>
            <strong>{{ p.name }}</strong>
            <span class="tv-pattern-polarity">{{ p.polarity }}</span>
          </header>
          <p>{{ p.narrative }}</p>
          <p class="tv-actionable">💡 <em>Actionable</em>: {{ p.actionable }}</p>
        </article>
      </div>

      <!-- Đại Vận Tài Timing -->
      <div v-if="taiVanData.dai_van_tai_timing?.length" class="lg-block tv-timing">
        <h5 class="lg-section-title">⏳ Thời điểm Tài kích hoạt (Đại Vận)</h5>
        <p class="tv-legend">
          <small>✦ <b>kích hoạt</b> · · <b>bình</b> · ○ <b>yên</b></small>
        </p>
        <div class="tv-dv-grid">
          <article v-for="c in taiVanData.dai_van_tai_timing" :key="c.cycle_index"
            class="tv-dv-cell" :data-verdict="c.verdict">
            <header>
              <strong>V{{ c.cycle_index }}</strong>
              <small>{{ c.start_age }}-{{ c.end_age }}t</small>
            </header>
            <div class="tv-dv-gz">{{ c.stem }} {{ c.branch }}</div>
            <div class="tv-dv-verdict">{{ c.mark }} {{ c.verdict }}</div>
            <ul v-if="c.reasons.length" class="tv-dv-reasons">
              <li v-for="(r, i) in c.reasons" :key="i">{{ r }}</li>
            </ul>
          </article>
        </div>
      </div>

      <!-- Strategy -->
      <div class="lg-block tv-strategy">
        <h5 class="lg-section-title">🎯 Chiến lược (Strategy)</h5>
        <ul>
          <li v-for="(s, i) in taiVanData.strategy" :key="i" :data-polarity="s.startsWith('✦') ? 'positive' : (s.startsWith('⚠') ? 'warning' : 'neutral')">
            {{ s }}
          </li>
        </ul>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(taiVanData.closing)"></div>
    </template>

    <!-- ── Bát Tự Hà Lạc Luận Giải ─────────────────────────────────────────
         Engine ha_lac/luan_giai — Tiên + Hậu thiên + 12 hào trajectory.
    -->
    <div v-if="batTuData" class="hl-trigger-section">
      <button v-if="!haLacLuanData" class="apply-btn hl-trigger-btn"
        @click="loadHaLacLuan" :disabled="haLacLuanLoading">
        {{ haLacLuanLoading ? "Đang luận giải Hà Lạc..." : "🪷 Hà Lạc Luận Giải — Học Năng 1974" }}
      </button>
      <p v-if="haLacLuanError" class="status-message error">{{ haLacLuanError }}</p>
    </div>

    <template v-if="haLacLuanData">
      <h4 class="section-h hl-h">🪷 Bát Tự Hà Lạc — đọc 2 quẻ + quỹ đạo 12 hào</h4>
      <p class="lg-paradigm">{{ haLacLuanData.paradigm_guard }}</p>

      <!-- Overview -->
      <div class="lg-block lg-overview" v-html="renderMd(haLacLuanData.overview)"></div>

      <!-- Tiên thiên + Hậu thiên — 2 cột -->
      <div class="hl-quai-grid">
        <article class="hl-quai-cell hl-tien">
          <header>
            <h5>🌒 {{ haLacLuanData.tien_thien_luan.role }}</h5>
            <strong>{{ haLacLuanData.tien_thien_luan.name_vi }}</strong>
            <small>quẻ {{ haLacLuanData.tien_thien_luan.king_wen }}</small>
          </header>
          <div class="hl-quai-trigrams">
            <span class="wiki-link" @click="openConcept(haLacLuanData.tien_thien_luan.upper_trigram)">
              {{ haLacLuanData.tien_thien_luan.upper_trigram }}
            </span>
            <small>({{ haLacLuanData.tien_thien_luan.upper_element }})</small>
            <span class="hl-trigram-sep">/</span>
            <span class="wiki-link" @click="openConcept(haLacLuanData.tien_thien_luan.lower_trigram)">
              {{ haLacLuanData.tien_thien_luan.lower_trigram }}
            </span>
            <small>({{ haLacLuanData.tien_thien_luan.lower_element }})</small>
          </div>
          <div class="hl-nd">
            🌟 <b>Nguyên Đường</b>: hào {{ haLacLuanData.tien_thien_luan.nguyen_duong_line }}
            <small>{{ haLacLuanData.tien_thien_luan.nguyen_duong_phase }}</small>
          </div>
        </article>
        <article class="hl-quai-cell hl-hau">
          <header>
            <h5>☀ {{ haLacLuanData.hau_thien_luan.role }}</h5>
            <strong>{{ haLacLuanData.hau_thien_luan.name_vi }}</strong>
            <small>quẻ {{ haLacLuanData.hau_thien_luan.king_wen }}</small>
          </header>
          <div class="hl-quai-trigrams">
            <span class="wiki-link" @click="openConcept(haLacLuanData.hau_thien_luan.upper_trigram)">
              {{ haLacLuanData.hau_thien_luan.upper_trigram }}
            </span>
            <small>({{ haLacLuanData.hau_thien_luan.upper_element }})</small>
            <span class="hl-trigram-sep">/</span>
            <span class="wiki-link" @click="openConcept(haLacLuanData.hau_thien_luan.lower_trigram)">
              {{ haLacLuanData.hau_thien_luan.lower_trigram }}
            </span>
            <small>({{ haLacLuanData.hau_thien_luan.lower_element }})</small>
          </div>
          <div class="hl-nd">
            🌟 <b>Nguyên Đường</b>: hào {{ haLacLuanData.hau_thien_luan.nguyen_duong_line }}
            <small>{{ haLacLuanData.hau_thien_luan.nguyen_duong_phase }}</small>
          </div>
        </article>
      </div>

      <!-- Comparison -->
      <div class="lg-block hl-compare" :data-pattern="haLacLuanData.comparison.pattern">
        <h5 class="lg-section-title">⚖ So sánh Tiên ↔ Hậu</h5>
        <div class="hl-pattern-tag">{{ haLacLuanData.comparison.pattern.toUpperCase() }}</div>
        <p>{{ haLacLuanData.comparison.narrative }}</p>
      </div>

      <!-- Quỹ đạo 12 hào -->
      <div class="lg-block hl-trajectory">
        <h5 class="lg-section-title">🌀 Quỹ Đạo 12 Hào ({{ haLacLuanData.lifespan.total_years }} năm)</h5>
        <p>{{ haLacLuanData.trajectory_luan.summary_narrative }}</p>
        <p class="hl-current-line" v-if="haLacLuanData.trajectory_luan.current"
          v-html="renderMd(haLacLuanData.trajectory_luan.current_narrative)"></p>
        <ol class="hl-stages">
          <li v-for="s in haLacLuanData.trajectory_luan.stages" :key="s.stage_index"
            :data-hexagram="s.hexagram"
            :data-polarity="s.polarity"
            :class="{ 'is-nd': s.is_nguyen_duong, 'is-current': s.is_current }">
            <span class="hl-stage-marker">{{ s.is_current ? '★' : (s.is_nguyen_duong ? '●' : '·') }}</span>
            <span class="hl-stage-meta">
              S{{ s.stage_index }} · {{ s.hexagram === 'tien' ? 'Tiên' : 'Hậu' }} hào {{ s.line_position }}
              · {{ s.polarity }} {{ s.years_span }}n
              · tuổi {{ s.age_start }}-{{ s.age_end }}
            </span>
            <span class="hl-stage-label">{{ s.phase_label }}</span>
          </li>
        </ol>
      </div>

      <!-- Bổ hướng giai đoạn -->
      <div class="lg-block lg-bo-huong hl-bo">
        <h5 class="lg-section-title">🎯 Bổ Hướng cho giai đoạn hiện tại</h5>
        <p v-html="renderMd(haLacLuanData.bo_huong_stage)"></p>
      </div>

      <!-- Closing -->
      <div class="lg-block lg-closing" v-html="renderMd(haLacLuanData.closing)"></div>
    </template>

    <!-- Citation + paradigm footer -->
    <div v-if="batTuData" class="bt-citation">
      <p>
        📚 <b>Nguồn khái niệm</b>: Thiệu Vĩ Hoa &amp; Trần Viên —
        <em>Dự đoán theo Tứ trụ</em> (NXB Văn hóa Thông tin, dịch giả Nguyễn Văn Mậu, tái bản lần 4).
        Engine <code>engine/bat_tu/*</code>. Wiki: 66 concepts đã seed
        (Thập Thần · Cách Cục · Dụng Thần · 12 Trường Sinh · Thần Sát · Đại Vận).
      </p>
      <p class="bt-paradigm-footer">
        🪷 <b>Paradigm</b>: <em>"Mệnh cố kết, vận lưu biến. Biết mệnh để cân bằng — Bổ —
        không phải để biết kết quả."</em> (Thiệu Vĩ Hoa Q1 ch.1-2)
      </p>
    </div>

    <!-- 📅 Chọn ngày tốt — Bát Tự + Mai Hoa + Hoàng Đạo -->
    <div class="bt-auspicious-section">
      <hr class="bt-divider" />
      <AuspiciousDayPanel />
    </div>

    <!-- 🔍 Birth Hour Quiz v2 modal -->
    <div v-if="showHourQuiz" class="bt-modal-backdrop" @click.self="showHourQuiz = false">
      <div class="bt-modal">
        <button class="bt-modal-close" @click="showHourQuiz = false">✕</button>
        <BirthHourQuizV2 />
      </div>
    </div>

    <HexagramDetailModal
      v-if="openSlug"
      :slug="openSlug"
      @close="closeHexagram"
    />
  </section>
</template>

<style scoped>
.bt-panel { display: flex; flex-direction: column; gap: 14px; }

.bt-note {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 3px solid var(--accent-gold, #e8c95a);
  padding-left: 12px;
  margin: 0;
  line-height: 1.6;
}
.bt-note b { color: var(--accent-gold-soft, #f5e6b1); }

.bt-paradigm-note {
  font-size: 12.5px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  background: rgba(94, 234, 212, 0.06);
  border-left: 3px solid rgba(94, 234, 212, 0.55);
  padding: 10px 14px;
  margin: 0;
  line-height: 1.65;
  border-radius: 0 4px 4px 0;
}
.bt-paradigm-note b { color: #5be5d3; }
.bt-paradigm-note em { color: #93c5fd; font-style: italic; }
.bt-paradigm-note small { display: inline-block; margin-top: 4px; opacity: 0.7; font-size: 11px; }

/* Clickable wiki concept links */
.wiki-link {
  cursor: pointer;
  transition: filter 0.15s, text-shadow 0.15s;
}
.wiki-link:hover {
  filter: brightness(1.25);
  text-shadow: 0 0 8px currentColor;
}
.wiki-link:active {
  filter: brightness(0.9);
}

/* Citation block */
.bt-citation {
  margin-top: 18px;
  padding: 10px 14px;
  background: rgba(245, 230, 177, 0.04);
  border-left: 3px solid rgba(245, 230, 177, 0.3);
  border-radius: 0 4px 4px 0;
  font-size: 11.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  line-height: 1.55;
}
.bt-citation p { margin: 0 0 6px 0; }
.bt-citation p:last-child { margin-bottom: 0; }
.bt-citation b { color: var(--accent-gold-soft, #f5e6b1); }
.bt-citation em { color: #cbd5e1; }
.bt-citation code {
  font-family: ui-monospace, monospace;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.25);
  padding: 1px 4px;
  border-radius: 3px;
}
.bt-paradigm-footer { color: #93c5fd !important; font-style: italic; }
.bt-paradigm-footer b { color: #5be5d3 !important; font-style: normal; }

/* ── Luận Giải Tổng Hợp section ──────────────────────────────────────────── */
.luan-giai-trigger {
  margin: 20px 0 4px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.lg-trigger-btn {
  background: linear-gradient(135deg, rgba(245, 230, 177, 0.18), rgba(94, 234, 212, 0.14));
  border-color: rgba(245, 230, 177, 0.4);
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 600;
  letter-spacing: 0.2px;
}
.lg-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(245, 230, 177, 0.7);
}

.lg-h {
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 14px;
  border-top: 1px dashed rgba(245, 230, 177, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}
.lg-paradigm {
  font-size: 12px;
  color: #5be5d3;
  font-style: italic;
  border-left: 2px solid rgba(94, 234, 212, 0.55);
  padding-left: 10px;
  margin: 0 0 14px 0;
  line-height: 1.55;
}

.lg-block {
  margin: 14px 0;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid rgba(245, 230, 177, 0.28);
  line-height: 1.65;
  font-size: 13.5px;
}
.lg-block p { margin: 6px 0; }
.lg-block p:first-child { margin-top: 0; }
.lg-block p:last-child { margin-bottom: 0; }
.lg-block b { color: var(--accent-gold-soft, #f5e6b1); }

.lg-overview {
  background: rgba(245, 230, 177, 0.06);
  border-left-color: rgba(245, 230, 177, 0.55);
}

.lg-section-title {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
  letter-spacing: 0.3px;
}

.lg-strength-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 6px;
}
.lg-tag {
  font-size: 13px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
}
.lg-strength-row[data-tag="strong"] .lg-tag { background: rgba(255, 175, 94, 0.15); color: #ffaf5e; }
.lg-strength-row[data-tag="weak"] .lg-tag { background: rgba(91, 229, 211, 0.15); color: #5be5d3; }
.lg-strength-row[data-tag="balanced"] .lg-tag { background: rgba(90, 176, 122, 0.15); color: #5ab07a; }
.lg-strength-row small { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-size: 11px; }

.lg-can-bo {
  background: rgba(91, 229, 211, 0.08);
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12.5px;
}

.lg-cach-cuc { border-left-color: rgba(91, 142, 229, 0.45); }
.lg-dung-than { border-left-color: rgba(232, 201, 90, 0.55); }

/* Extreme Pattern (Tòng / Hóa Khí / Five Special) — edge case */
.lg-extreme {
  border-left: 3px solid #fbbf24 !important;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(167, 139, 250, 0.06));
  position: relative;
}
.lg-extreme[data-type="special"] { border-left-color: #fbbf24 !important; }
.lg-extreme[data-type="hoa"] { border-left-color: #c4b5fd !important; background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(91, 229, 211, 0.06)); }
.lg-extreme[data-type="tong"] { border-left-color: #f8b4d9 !important; background: linear-gradient(135deg, rgba(245, 130, 175, 0.1), rgba(232, 201, 90, 0.06)); }

.lg-extreme-trio {
  display: flex;
  gap: 8px;
  margin: 8px 0;
  flex-wrap: wrap;
}
.lg-ext-cell {
  background: rgba(255, 255, 255, 0.06);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}
.lg-ext-dung { color: #fbbf24; }
.lg-ext-hy { color: #5be5d3; }
.lg-ext-ky { color: #d65a4a; }
.lg-ext-conf {
  display: block;
  margin-top: 6px;
  font-size: 10.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-family: ui-monospace, monospace;
  font-style: italic;
}

.lg-tt-profile {
  margin: 10px 0;
  padding: 9px 11px;
  background: rgba(255, 255, 255, 0.025);
  border-radius: 5px;
  border-left: 2px solid rgba(147, 197, 253, 0.45);
}
.lg-tt-profile header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 4px;
}
.lg-tt-profile strong {
  color: #93c5fd;
  font-size: 14px;
}
.lg-tt-weight {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  background: rgba(147, 197, 253, 0.12);
  padding: 1px 6px;
  border-radius: 3px;
}
.lg-tt-profile p { margin: 4px 0; font-size: 12.5px; }
.lg-tt-cong-nang {
  font-size: 12px !important;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  background: rgba(0, 0, 0, 0.15);
  padding: 6px 8px;
  border-radius: 3px;
  margin-top: 5px !important;
}

.lg-favorable { border-left-color: rgba(90, 176, 122, 0.5); }
.lg-fc {
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(90, 176, 122, 0.08);
  border-radius: 4px;
}
.lg-fc strong { display: block; color: #5ab07a; font-size: 13px; margin-bottom: 3px; }
.lg-fc p { margin: 0; font-size: 12.5px; }

.lg-warnings { border-left-color: rgba(214, 90, 74, 0.5); }
.lg-warn {
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(214, 90, 74, 0.08);
  border-radius: 4px;
}
.lg-warn strong { display: block; color: #d65a4a; font-size: 13px; margin-bottom: 3px; }
.lg-warn p { margin: 0; font-size: 12.5px; }

.lg-thong-quan { border-left-color: rgba(167, 139, 250, 0.5); }

.lg-stars {
  list-style: none;
  margin: 8px 0 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.lg-stars li {
  background: rgba(255, 255, 255, 0.04);
  padding: 4px 9px;
  border-radius: 3px;
  font-size: 11.5px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.lg-stars li[data-polarity="lành"] { color: #5ab07a; }
.lg-stars li[data-polarity="dữ"] { color: #d65a4a; }
.lg-stars li[data-polarity="trung tính"] { color: #94a3b8; }
.lg-stars small { color: var(--text-muted, rgba(230, 238, 245, 0.5)); font-size: 10px; }

.lg-dv-current { border-left-color: rgba(232, 201, 90, 0.65); }

.lg-bo-huong { border-left-color: rgba(94, 234, 212, 0.6); }
.lg-bo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.lg-bo-cell {
  background: rgba(94, 234, 212, 0.06);
  padding: 9px 11px;
  border-radius: 5px;
  border-left: 2px solid rgba(94, 234, 212, 0.4);
}
.lg-bo-cell[data-role="dung"] {
  border-left-color: var(--accent-gold-soft, #f5e6b1);
  background: rgba(245, 230, 177, 0.06);
}
.lg-bo-cell header { margin-bottom: 6px; }
.lg-bo-cell header strong { color: var(--accent-gold-soft, #f5e6b1); font-size: 12.5px; }
.lg-bo-cell[data-role="hy"] header strong { color: #5be5d3; }
.lg-bo-cat {
  display: flex;
  gap: 7px;
  margin: 4px 0;
  font-size: 11.5px;
  line-height: 1.45;
}
.lg-bo-cat small {
  min-width: 60px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 11px;
  white-space: nowrap;
}
.lg-bo-cat span {
  color: var(--text-strong, #e6eef5);
  flex: 1;
}
.lg-bo-tranh {
  margin-top: 10px;
  padding: 7px 10px;
  background: rgba(214, 90, 74, 0.06);
  border-radius: 4px;
  font-size: 11.5px;
  border-left: 2px solid rgba(214, 90, 74, 0.4);
}
.lg-bo-tranh strong { color: #d65a4a; }

.lg-closing {
  background: linear-gradient(180deg, rgba(245, 230, 177, 0.08), rgba(91, 229, 211, 0.06));
  border-left-color: rgba(245, 230, 177, 0.6);
  font-style: italic;
  font-size: 13px;
  line-height: 1.7;
}

/* ── Lưu Niên section ────────────────────────────────────────────────────── */
.luu-nien-trigger {
  margin: 20px 0 4px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ln-trigger-btn {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.18), rgba(94, 234, 212, 0.14));
  border-color: rgba(167, 139, 250, 0.4);
  color: #c4b5fd;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.ln-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(167, 139, 250, 0.7);
}

.ln-h {
  color: #c4b5fd;
  font-size: 14px;
  border-top: 1px dashed rgba(167, 139, 250, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}
.ln-ganzhi {
  color: #c4b5fd;
  background: rgba(167, 139, 250, 0.12);
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 700;
}

.ln-overall {
  border-left-color: rgba(167, 139, 250, 0.55);
}
.ln-overall[data-verdict="thuận"] { border-left-color: rgba(90, 176, 122, 0.7); background: rgba(90, 176, 122, 0.06); }
.ln-overall[data-verdict="thuận nhẹ"] { border-left-color: rgba(90, 176, 122, 0.5); background: rgba(90, 176, 122, 0.04); }
.ln-overall[data-verdict="thử thách"] { border-left-color: rgba(214, 90, 74, 0.7); background: rgba(214, 90, 74, 0.06); }
.ln-overall[data-verdict="hỗn tạp"] { border-left-color: rgba(232, 201, 90, 0.7); background: rgba(232, 201, 90, 0.06); }

.ln-verdict-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.ln-verdict-tag {
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  letter-spacing: 0.5px;
}
.ln-overall[data-verdict="thuận"] .ln-verdict-tag { background: rgba(90, 176, 122, 0.18); color: #5ab07a; }
.ln-overall[data-verdict="thuận nhẹ"] .ln-verdict-tag { background: rgba(90, 176, 122, 0.12); color: #5ab07a; }
.ln-overall[data-verdict="thử thách"] .ln-verdict-tag { background: rgba(214, 90, 74, 0.18); color: #d65a4a; }
.ln-overall[data-verdict="hỗn tạp"] .ln-verdict-tag { background: rgba(232, 201, 90, 0.18); color: #e8c95a; }
.ln-overall[data-verdict="trung tính"] .ln-verdict-tag { background: rgba(148, 163, 184, 0.18); color: #94a3b8; }
.ln-verdict-row small { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-size: 11.5px; }

.ln-pillars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.ln-pillar-cell {
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 10px;
  border-radius: 4px;
  border-left: 2px solid rgba(167, 139, 250, 0.35);
}
.ln-pillar-cell header {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 5px;
}
.ln-pillar-cell header strong { font-size: 12px; color: #c4b5fd; }
.ln-pillar-cell header small { font-size: 10.5px; color: var(--accent-gold-soft, #f5e6b1); font-family: ui-monospace, monospace; }
.ln-inter-row {
  display: flex;
  gap: 5px;
  font-size: 11px;
  margin: 2px 0;
  align-items: baseline;
}
.ln-inter-row small {
  min-width: 24px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-size: 10px;
}
.ln-inter-row[data-polarity="lành"] span { color: #5ab07a; }
.ln-inter-row[data-polarity="hung"] span { color: #d65a4a; }
.ln-inter-row[data-polarity="trung"] span { color: #cbd5e1; }

.ln-tam-hop {
  margin-top: 10px;
  padding: 8px 10px;
  background: rgba(232, 201, 90, 0.06);
  border-radius: 4px;
  border-left: 2px solid rgba(232, 201, 90, 0.45);
}
.ln-tam-hop h6 { margin: 0 0 4px 0; font-size: 12px; color: var(--accent-gold-soft, #f5e6b1); }
.ln-tam-hop p { margin: 3px 0; font-size: 12px; }

.ln-vs-dv { border-left-color: rgba(94, 234, 212, 0.5); }

.ln-luu-nguyet { border-left-color: rgba(167, 139, 250, 0.5); }
.ln-month-legend {
  font-size: 11px !important;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  margin: 0 0 8px 0 !important;
}
.ln-month-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(115px, 1fr));
  gap: 6px;
}
.ln-month-cell {
  background: rgba(255, 255, 255, 0.025);
  padding: 7px 9px;
  border-radius: 4px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
  font-size: 11.5px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.ln-month-cell[data-verdict="thuận"] {
  border-left-color: rgba(90, 176, 122, 0.65);
  background: rgba(90, 176, 122, 0.06);
}
.ln-month-cell[data-verdict="thử thách"] {
  border-left-color: rgba(214, 90, 74, 0.65);
  background: rgba(214, 90, 74, 0.05);
}
.ln-month-cell[data-verdict="hỗn tạp"] {
  border-left-color: rgba(232, 201, 90, 0.55);
  background: rgba(232, 201, 90, 0.04);
}
.ln-month-cell header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 5px;
}
.ln-month-cell header strong { font-size: 11px; color: #c4b5fd; }
.ln-month-cell header small { font-size: 9.5px; color: var(--text-muted, rgba(230, 238, 245, 0.5)); font-style: italic; }
.ln-month-gz {
  font-weight: 700;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 12px;
  font-family: ui-monospace, monospace;
}
.ln-month-tt {
  font-size: 11px;
  color: #93c5fd;
}
.ln-month-marker {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-style: italic;
}

.ln-bo { border-left-color: rgba(167, 139, 250, 0.6); }

/* ── Hôn Nhân section ──────────────────────────────────────────────────── */
.hn-trigger-section, .sn-trigger-section {
  margin: 20px 0 4px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.hn-trigger-btn {
  background: linear-gradient(135deg, rgba(245, 130, 175, 0.18), rgba(232, 201, 90, 0.14));
  border-color: rgba(245, 130, 175, 0.4);
  color: #f8b4d9;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.hn-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(245, 130, 175, 0.7);
}

.hn-h {
  color: #f8b4d9;
  font-size: 14px;
  border-top: 1px dashed rgba(245, 130, 175, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}

.hn-overall {
  border-left-color: rgba(245, 130, 175, 0.55);
}
.hn-overall[data-label="thuận"] { border-left-color: rgba(90, 176, 122, 0.7); background: rgba(90, 176, 122, 0.06); }
.hn-overall[data-label="trung bình"] { border-left-color: rgba(232, 201, 90, 0.6); background: rgba(232, 201, 90, 0.04); }
.hn-overall[data-label="thử thách"] { border-left-color: rgba(214, 90, 74, 0.7); background: rgba(214, 90, 74, 0.06); }

.hn-verdict-row {
  display: flex; align-items: baseline; gap: 10px; margin-bottom: 5px;
}
.hn-verdict-tag {
  font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 4px;
  background: rgba(245, 130, 175, 0.18); color: #f8b4d9;
}
.hn-overall[data-label="thuận"] .hn-verdict-tag { background: rgba(90, 176, 122, 0.2); color: #5ab07a; }
.hn-overall[data-label="thử thách"] .hn-verdict-tag { background: rgba(214, 90, 74, 0.2); color: #d65a4a; }

.hn-tang-can {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.18);
  border-radius: 3px;
  display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
}
.hn-tang-can small { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-size: 11px; }
.hn-tang-item {
  font-size: 12px;
  background: rgba(245, 230, 177, 0.08);
  padding: 2px 8px;
  border-radius: 3px;
}
.hn-tang-item em { color: var(--accent-gold-soft, #f5e6b1); font-style: normal; font-weight: 600; }

.hn-interactions ul, .hn-star-list ul {
  list-style: disc;
  margin: 4px 0 0 18px;
  padding: 0;
  font-size: 12px;
}
.hn-interactions li[data-polarity="lành"] { color: #5ab07a; }
.hn-interactions li[data-polarity="hung"] { color: #d65a4a; }

.hn-dao-hoa {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(245, 130, 175, 0.08);
  border-radius: 4px;
  font-size: 12.5px;
}

.hn-stars { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 6px; }
.hn-stars li {
  background: rgba(255, 255, 255, 0.04);
  padding: 4px 9px;
  border-radius: 3px;
  font-size: 11.5px;
  display: flex; gap: 5px; align-items: center;
}
.hn-stars li[data-polarity="lành"] strong { color: #5ab07a; }
.hn-stars li[data-polarity="dữ"] strong { color: #d65a4a; }
.hn-stars li[data-polarity="trung tính"] strong { color: #94a3b8; }
.hn-stars li span { color: var(--text-muted, rgba(230, 238, 245, 0.6)); font-size: 11px; }

.hn-timing { border-left-color: rgba(245, 130, 175, 0.5); }
.hn-fav-cycles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.hn-cycle-cell {
  background: rgba(245, 130, 175, 0.06);
  padding: 8px 10px;
  border-radius: 4px;
  border-left: 2px solid rgba(245, 130, 175, 0.45);
}
.hn-cycle-cell header { display: flex; align-items: baseline; gap: 6px; margin-bottom: 4px; flex-wrap: wrap; }
.hn-cycle-cell header strong { font-size: 12px; color: #f8b4d9; }
.hn-cycle-cell header small { font-size: 10.5px; color: var(--text-muted, rgba(230, 238, 245, 0.55)); }
.hn-cycle-cell ul { margin: 0 0 0 16px; padding: 0; font-size: 11px; }
.hn-cycle-cell li { color: var(--text-secondary, rgba(230, 238, 245, 0.72)); margin: 1px 0; }

/* ── Sự Nghiệp section ──────────────────────────────────────────────────── */
.sn-trigger-btn {
  background: linear-gradient(135deg, rgba(94, 142, 229, 0.18), rgba(91, 229, 211, 0.14));
  border-color: rgba(94, 142, 229, 0.4);
  color: #93c5fd;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.sn-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(94, 142, 229, 0.7);
}

.sn-h {
  color: #93c5fd;
  font-size: 14px;
  border-top: 1px dashed rgba(94, 142, 229, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}

.sn-cach { border-left-color: rgba(94, 142, 229, 0.55); }

.sn-pattern {
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(94, 142, 229, 0.05);
  border-radius: 4px;
  border-left: 2px solid rgba(94, 142, 229, 0.4);
}
.sn-pattern strong { display: block; color: #93c5fd; font-size: 13px; margin-bottom: 3px; }
.sn-pattern p { margin: 3px 0; font-size: 12.5px; }
.sn-hint {
  background: rgba(0, 0, 0, 0.15);
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11.5px !important;
  margin-top: 5px !important;
}
.sn-hint em { color: var(--accent-gold-soft, #f5e6b1); }

.sn-styles { list-style: none; padding: 0; margin: 0; }
.sn-styles li {
  margin: 5px 0;
  padding: 5px 9px;
  background: rgba(91, 142, 229, 0.06);
  border-radius: 3px;
  font-size: 12.5px;
}
.sn-styles strong { color: #93c5fd; }

.sn-rec { border-left-color: rgba(91, 229, 211, 0.55); }
.sn-rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
  margin-top: 8px;
}
.sn-rec-cell {
  background: rgba(91, 229, 211, 0.05);
  padding: 9px 11px;
  border-radius: 5px;
  border-left: 2px solid rgba(91, 229, 211, 0.4);
}
.sn-rec-cell[data-role="dung"] {
  border-left-color: var(--accent-gold-soft, #f5e6b1);
  background: rgba(245, 230, 177, 0.05);
}
.sn-rec-cell header strong { font-size: 12.5px; color: var(--accent-gold-soft, #f5e6b1); }
.sn-rec-cell[data-role="hy"] header strong { color: #5be5d3; }
.sn-ind {
  margin: 4px 0;
  padding: 4px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
}
.sn-ind:last-child { border-bottom: 0; }
.sn-ind strong { display: block; font-size: 11.5px; color: var(--text-strong, #e6eef5); }
.sn-ind small { font-size: 11px; color: var(--text-muted, rgba(230, 238, 245, 0.55)); }

.sn-cach-list {
  margin-top: 10px;
  padding: 8px 10px;
  background: rgba(94, 142, 229, 0.06);
  border-radius: 4px;
}
.sn-cach-list h6 { margin: 0 0 4px 0; font-size: 11px; color: #93c5fd; text-transform: uppercase; letter-spacing: 0.5px; }
.sn-cach-list ul { margin: 0 0 0 18px; padding: 0; font-size: 12px; }

.sn-avoid { border-left-color: rgba(214, 90, 74, 0.5); }
.sn-avoid-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex; flex-wrap: wrap; gap: 6px;
}
.sn-avoid-list li {
  background: rgba(214, 90, 74, 0.08);
  padding: 4px 9px;
  border-radius: 3px;
  font-size: 11.5px;
  color: #d65a4a;
}

.sn-timing { border-left-color: rgba(94, 142, 229, 0.5); }
.sn-dv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(105px, 1fr));
  gap: 6px;
  margin-top: 6px;
}
.sn-dv-cell {
  background: rgba(255, 255, 255, 0.025);
  padding: 6px 8px;
  border-radius: 4px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
  font-size: 11px;
  display: flex; flex-direction: column; gap: 3px;
}
.sn-dv-cell[data-verdict="thuận lợi"] {
  border-left-color: rgba(90, 176, 122, 0.65);
  background: rgba(90, 176, 122, 0.06);
}
.sn-dv-cell[data-verdict="thử thách"] {
  border-left-color: rgba(214, 90, 74, 0.65);
  background: rgba(214, 90, 74, 0.05);
}
.sn-dv-cell[data-verdict="tích lũy"] {
  border-left-color: rgba(91, 229, 211, 0.5);
  background: rgba(91, 229, 211, 0.04);
}
.sn-dv-cell[data-verdict="hỗn tạp"] {
  border-left-color: rgba(232, 201, 90, 0.55);
  background: rgba(232, 201, 90, 0.04);
}
.sn-dv-cell header { display: flex; justify-content: space-between; align-items: baseline; }
.sn-dv-cell header strong { font-size: 11px; color: #93c5fd; }
.sn-dv-cell header small { font-size: 9.5px; color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.sn-dv-gz { font-weight: 700; color: var(--accent-gold-soft, #f5e6b1); font-family: ui-monospace, monospace; font-size: 11.5px; }
.sn-dv-mark { font-size: 10px; color: var(--text-muted, rgba(230, 238, 245, 0.6)); font-style: italic; }

/* ── Bát Tự Hà Lạc section ──────────────────────────────────────────────── */
.hl-trigger-section {
  margin: 20px 0 4px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.hl-trigger-btn {
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.18), rgba(167, 139, 250, 0.16));
  border-color: rgba(244, 114, 182, 0.4);
  color: #f9a8d4;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.hl-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(244, 114, 182, 0.7);
}

.hl-h {
  color: #f9a8d4;
  font-size: 14px;
  border-top: 1px dashed rgba(244, 114, 182, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}

.hl-quai-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 14px 0;
}
.hl-quai-cell {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px 14px;
  border-radius: 6px;
  border-left: 3px solid rgba(244, 114, 182, 0.4);
}
.hl-quai-cell.hl-tien { border-left-color: rgba(167, 139, 250, 0.55); background: rgba(167, 139, 250, 0.05); }
.hl-quai-cell.hl-hau { border-left-color: rgba(245, 230, 177, 0.55); background: rgba(245, 230, 177, 0.05); }
.hl-quai-cell header {
  margin-bottom: 8px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  padding-bottom: 6px;
}
.hl-quai-cell header h5 {
  margin: 0 0 3px 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.hl-quai-cell header strong {
  display: block;
  font-size: 17px;
  font-weight: 700;
  color: var(--accent-gold-soft, #f5e6b1);
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
}
.hl-quai-cell.hl-tien header strong { color: #c4b5fd; }
.hl-quai-cell header small {
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-size: 11px;
  font-family: ui-monospace, monospace;
}
.hl-quai-trigrams {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  margin-bottom: 6px;
}
.hl-quai-trigrams .wiki-link {
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 600;
}
.hl-trigram-sep { color: var(--text-muted, rgba(230, 238, 245, 0.4)); font-size: 14px; }
.hl-quai-trigrams small { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-size: 10.5px; }
.hl-nd {
  margin-top: 4px;
  padding: 5px 8px;
  background: rgba(245, 230, 177, 0.08);
  border-radius: 3px;
  font-size: 11.5px;
}
.hl-nd b { color: var(--accent-gold-soft, #f5e6b1); }
.hl-nd small {
  display: block;
  margin-top: 2px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  font-size: 11px;
  font-style: italic;
}

.hl-compare { border-left-color: rgba(167, 139, 250, 0.55); }
.hl-compare[data-pattern="tỷ hòa"], .hl-compare[data-pattern="Tiên sinh Hậu"] {
  border-left-color: rgba(90, 176, 122, 0.65) !important;
  background: rgba(90, 176, 122, 0.06);
}
.hl-compare[data-pattern*="khắc"] {
  border-left-color: rgba(214, 90, 74, 0.6) !important;
  background: rgba(214, 90, 74, 0.05);
}
.hl-compare[data-pattern="trùng lặp"] {
  border-left-color: rgba(232, 201, 90, 0.6) !important;
  background: rgba(232, 201, 90, 0.05);
}
.hl-pattern-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.hl-trajectory { border-left-color: rgba(244, 114, 182, 0.5); }
.hl-current-line {
  background: rgba(245, 230, 177, 0.12);
  padding: 8px 10px;
  border-radius: 4px;
  border-left: 2px solid rgba(245, 230, 177, 0.6);
  margin: 8px 0 !important;
}
.hl-current-line b { color: var(--accent-gold-soft, #f5e6b1); }

.hl-stages {
  list-style: none;
  margin: 8px 0 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.hl-stages li {
  display: grid;
  grid-template-columns: 20px 220px 1fr;
  align-items: baseline;
  gap: 8px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.025);
  border-radius: 3px;
  font-size: 11.5px;
  border-left: 2px solid transparent;
}
.hl-stages li[data-hexagram="tien"] { border-left-color: rgba(167, 139, 250, 0.35); }
.hl-stages li[data-hexagram="hau"] { border-left-color: rgba(245, 230, 177, 0.35); }
.hl-stages li.is-nd {
  background: rgba(245, 230, 177, 0.06);
  border-left-color: rgba(245, 230, 177, 0.7) !important;
}
.hl-stages li.is-current {
  background: rgba(244, 114, 182, 0.12);
  border-left-color: rgba(244, 114, 182, 0.8) !important;
  border: 1px solid rgba(244, 114, 182, 0.4);
}
.hl-stage-marker {
  text-align: center;
  font-size: 13px;
}
.hl-stages li.is-nd .hl-stage-marker { color: var(--accent-gold-soft, #f5e6b1); }
.hl-stages li.is-current .hl-stage-marker { color: #f9a8d4; }
.hl-stage-meta {
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  font-family: ui-monospace, monospace;
  font-size: 10.5px;
}
.hl-stage-label {
  color: var(--text-strong, #e6eef5);
  font-size: 11px;
}

.hl-bo { border-left-color: rgba(244, 114, 182, 0.6); }

/* ── Tài Vận section ──────────────────────────────────────────────────── */
.tv-trigger-section {
  margin: 20px 0 4px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.tv-trigger-btn {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.18), rgba(232, 201, 90, 0.16));
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.tv-trigger-btn:hover:not(:disabled) {
  filter: brightness(1.18);
  border-color: rgba(245, 158, 11, 0.7);
}

.tv-h {
  color: #fbbf24;
  font-size: 14px;
  border-top: 1px dashed rgba(245, 158, 11, 0.3);
  padding-top: 18px;
  margin-top: 22px;
}

.tv-balance { border-left-color: rgba(245, 158, 11, 0.55); }
.tv-balance[data-polarity="lành"] { border-left-color: rgba(90, 176, 122, 0.7); background: rgba(90, 176, 122, 0.06); }
.tv-balance[data-polarity="cảnh báo cao"] { border-left-color: rgba(214, 90, 74, 0.7); background: rgba(214, 90, 74, 0.06); }
.tv-balance[data-polarity="trung tính"] { border-left-color: rgba(148, 163, 184, 0.55); }

.tv-balance-row {
  display: flex; gap: 10px; align-items: baseline; margin-bottom: 5px;
}
.tv-balance-tag {
  font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 4px;
  background: rgba(255, 255, 255, 0.08); letter-spacing: 0.4px;
}
.tv-balance[data-polarity="lành"] .tv-balance-tag { background: rgba(90, 176, 122, 0.18); color: #5ab07a; }
.tv-balance[data-polarity="cảnh báo cao"] .tv-balance-tag { background: rgba(214, 90, 74, 0.18); color: #d65a4a; }
.tv-balance-row small { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-size: 11px; }
.tv-recommend {
  margin-top: 6px;
  padding: 6px 9px;
  background: rgba(91, 229, 211, 0.06);
  border-radius: 4px;
  font-size: 12.5px;
}
.tv-recommend b { color: #5be5d3; }

.tv-map-row {
  display: flex; gap: 12px; margin-bottom: 8px; flex-wrap: wrap;
}
.tv-map-stat {
  background: rgba(245, 158, 11, 0.08);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}
.tv-map-stat b { color: #fbbf24; }
.tv-positions {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}
.tv-positions li {
  font-size: 12px;
  padding: 4px 9px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.025);
}
.tv-positions li[data-type="chinh"] strong { color: #5ab07a; }
.tv-positions li[data-type="thien"] strong { color: #fbbf24; }
.tv-positions em { color: var(--accent-gold-soft, #f5e6b1); font-style: normal; }

.tv-source {
  margin: 8px 0;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.05);
  border-radius: 5px;
  border-left: 2px solid rgba(245, 158, 11, 0.4);
}
.tv-source header {
  display: flex; align-items: baseline; gap: 8px; margin-bottom: 5px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08); padding-bottom: 4px;
}
.tv-source strong { color: #fbbf24; font-size: 13px; }
.tv-source small {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  padding: 1px 7px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 700;
}
.tv-source p { margin: 3px 0; font-size: 12.5px; }
.tv-source b { color: var(--accent-gold-soft, #f5e6b1); }
.tv-source-ky b { color: #d65a4a; }

.tv-pattern {
  margin: 8px 0;
  padding: 9px 11px;
  border-radius: 4px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
}
.tv-pattern[data-polarity="positive"] {
  background: rgba(90, 176, 122, 0.07);
  border-left-color: rgba(90, 176, 122, 0.55);
}
.tv-pattern[data-polarity="warning"] {
  background: rgba(214, 90, 74, 0.07);
  border-left-color: rgba(214, 90, 74, 0.55);
}
.tv-pattern[data-polarity="neutral"] {
  background: rgba(148, 163, 184, 0.06);
  border-left-color: rgba(148, 163, 184, 0.4);
}
.tv-pattern header {
  display: flex; align-items: baseline; gap: 10px; margin-bottom: 4px; flex-wrap: wrap;
}
.tv-pattern strong { font-size: 13px; }
.tv-pattern[data-polarity="positive"] strong { color: #5ab07a; }
.tv-pattern[data-polarity="warning"] strong { color: #d65a4a; }
.tv-pattern[data-polarity="neutral"] strong { color: #94a3b8; }
.tv-pattern-polarity {
  font-size: 10.5px;
  background: rgba(255, 255, 255, 0.06);
  padding: 1px 7px;
  border-radius: 3px;
  font-style: italic;
}
.tv-pattern p { margin: 3px 0; font-size: 12.5px; }
.tv-actionable {
  background: rgba(0, 0, 0, 0.15);
  padding: 5px 8px;
  border-radius: 3px;
  font-size: 11.5px !important;
  margin-top: 5px !important;
}
.tv-actionable em { color: var(--accent-gold-soft, #f5e6b1); }

.tv-timing { border-left-color: rgba(245, 158, 11, 0.55); }
.tv-legend { font-size: 11px !important; color: var(--text-muted, rgba(230, 238, 245, 0.55)); margin: 0 0 8px 0 !important; }

.tv-dv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.tv-dv-cell {
  background: rgba(255, 255, 255, 0.025);
  padding: 8px 10px;
  border-radius: 4px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
  font-size: 11px;
  display: flex; flex-direction: column; gap: 3px;
}
.tv-dv-cell[data-verdict="tài lộc kích hoạt"] {
  border-left-color: rgba(245, 158, 11, 0.65);
  background: rgba(245, 158, 11, 0.08);
}
.tv-dv-cell[data-verdict="tài lộc bình"] {
  border-left-color: rgba(148, 163, 184, 0.5);
  background: rgba(148, 163, 184, 0.04);
}
.tv-dv-cell[data-verdict="tài lộc yên"] {
  border-left-color: rgba(99, 102, 120, 0.4);
  background: rgba(99, 102, 120, 0.04);
}
.tv-dv-cell header { display: flex; justify-content: space-between; align-items: baseline; }
.tv-dv-cell header strong { font-size: 11px; color: #fbbf24; }
.tv-dv-cell header small { font-size: 9.5px; color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.tv-dv-gz { font-weight: 700; color: var(--accent-gold-soft, #f5e6b1); font-family: ui-monospace, monospace; font-size: 11.5px; }
.tv-dv-verdict { font-size: 10.5px; color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-style: italic; }
.tv-dv-reasons {
  margin: 4px 0 0 14px;
  padding: 0;
  font-size: 10px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
}

.tv-strategy { border-left-color: rgba(245, 158, 11, 0.55); }
.tv-strategy ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.tv-strategy li {
  padding: 5px 10px;
  border-radius: 3px;
  font-size: 12.5px;
  background: rgba(255, 255, 255, 0.03);
}
.tv-strategy li[data-polarity="positive"] {
  background: rgba(90, 176, 122, 0.08);
  border-left: 2px solid rgba(90, 176, 122, 0.55);
}
.tv-strategy li[data-polarity="warning"] {
  background: rgba(214, 90, 74, 0.08);
  border-left: 2px solid rgba(214, 90, 74, 0.55);
}

.bt-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
}
.bt-form label { display: flex; flex-direction: column; gap: 4px; }
.bt-form label span {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.bt-actions {
  grid-column: 1 / -1;
  display: flex; gap: 8px; align-items: center;
}

.birth-summary {
  margin: 12px 0 4px 0;
  padding: 10px 14px;
  background: rgba(245, 230, 177, 0.05);
  border-left: 3px solid var(--accent-gold-soft, #f5e6b1);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bs-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  font-size: 13px;
  line-height: 1.5;
}
.bs-label {
  min-width: 90px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.bs-val {
  color: var(--text-strong, #e6eef5);
  font-weight: 500;
}
.bs-weekday, .bs-ganzhi {
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 12px;
}
.bs-ganzhi {
  color: var(--accent-gold-soft, #f5e6b1);
  font-style: italic;
}

.section-h {
  margin: 14px 0 6px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
}
.ha-lac-h { color: var(--accent-gold-soft, #f5e6b1); font-size: 14px; }

/* ── Pillars grid ──────────────────────────────────────────────────────── */
.pillar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}
.pillar-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 7px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pillar-card.is-day-master {
  border-color: rgba(232, 201, 90, 0.45);
  background: rgba(232, 201, 90, 0.06);
  box-shadow: 0 0 0 1px rgba(232, 201, 90, 0.2);
}
.pillar-head h5 {
  margin: 0; font-size: 14px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.pillar-head small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.pillar-stem-branch { display: flex; gap: 6px; }
.pillar-stem, .pillar-branch {
  flex: 1;
  padding: 6px 8px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  align-items: center;
}
.pillar-stem .char, .pillar-branch .char {
  font-size: 17px;
  font-weight: 700;
}
.pillar-stem small, .pillar-branch small {
  font-size: 10px;
  opacity: 0.85;
}
.pillar-thapthan { text-align: center; }
.tt-tag {
  display: inline-block;
  border: 1px solid;
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.04);
}
.pillar-hidden {
  list-style: none;
  margin: 0;
  padding: 6px 8px;
  background: rgba(0, 0, 0, 0.18);
  border-radius: 3px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.pillar-hidden li {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  line-height: 1.4;
}
.pillar-hidden em { color: var(--accent-gold-soft, #f5e6b1); font-style: normal; }

/* ── Day Master card ───────────────────────────────────────────────────── */
.dm-card {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 12px;
  background: rgba(232, 201, 90, 0.05);
  border: 1px solid rgba(232, 201, 90, 0.22);
  border-radius: 7px;
  padding: 12px;
}
.dm-strength { display: flex; flex-direction: column; gap: 4px; }
.dm-label {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.dm-strength strong {
  font-size: 16px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.dm-strength[data-tag="strong"] strong { color: #ffaf5e; }
.dm-strength[data-tag="weak"] strong { color: #5be5d3; }
.dm-strength[data-tag="balanced"] strong { color: #5ab07a; }
.dm-strength small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.dm-breakdown { display: flex; flex-direction: column; gap: 4px; }
.dm-bar {
  display: grid;
  grid-template-columns: 130px 1fr 40px;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}
.dm-bar-label { color: var(--text-muted, rgba(230, 238, 245, 0.6)); }
.dm-bar-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}
.dm-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #5ab07a 0%, #e8c95a 100%);
  border-radius: 3px;
}
.dm-bar-value { text-align: right; font-family: ui-monospace, monospace; color: var(--text-primary, #e6eef5); }

/* ── Elements grid ─────────────────────────────────────────────────────── */
.elements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.element-cell {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 8px 10px;
}
.element-name {
  font-size: 12px;
  font-weight: 700;
}
.element-cell strong {
  display: block;
  font-size: 18px;
  color: var(--text-primary, #e6eef5);
  margin: 2px 0 6px;
}
.element-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}
.element-bar > div { height: 100%; border-radius: 2px; }

/* ── Hà Lạc section ────────────────────────────────────────────────────── */
.ha-lac-intro {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-family: ui-monospace, monospace;
  background: rgba(91, 229, 211, 0.04);
  border: 1px solid rgba(91, 229, 211, 0.2);
  padding: 8px 12px;
  border-radius: 5px;
  margin: 0;
}
.ha-lac-intro b { color: var(--accent-teal, #5be5d3); }

.halac-quai-pair {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
}
.halac-quai {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 7px;
  padding: 12px;
}
.halac-quai[data-which="tien"] { border-left: 3px solid var(--accent-gold, #e8c95a); }
.halac-quai[data-which="hau"]  { border-left: 3px solid var(--accent-teal, #5be5d3); }
.halac-quai header h5 {
  margin: 0 0 2px 0;
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
}
.halac-quai header small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.halac-quai-body {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  cursor: pointer;
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.15s;
}
.halac-quai-body:hover { background: rgba(91, 229, 211, 0.06); }
.halac-quai-body > div { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.halac-quai-body strong {
  font-size: 18px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.halac-quai-body small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.halac-quai-body p {
  margin: 2px 0;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.nd-tag { color: var(--accent-teal, #5be5d3) !important; }
.nd-tag b { color: var(--accent-gold, #e8c95a); }
.halac-arrow {
  font-size: 28px;
  color: var(--accent-gold, #e8c95a);
  text-align: center;
}

/* ── Decade trajectory ─────────────────────────────────────────────────── */
.trajectory {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 6px;
}
.traj-stage {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 8px 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}
.traj-stage.is-nd {
  background: rgba(232, 201, 90, 0.09);
  border-color: rgba(232, 201, 90, 0.4);
}
.traj-stage.is-hau { border-left: 3px solid var(--accent-teal, #5be5d3); }
.traj-stage.is-tien { border-left: 3px solid var(--accent-gold, #e8c95a); }
.traj-age {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
}
.traj-age strong {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.traj-age small {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.traj-info { display: flex; flex-direction: column; gap: 1px; }
.traj-label {
  font-size: 12px;
  color: var(--text-primary, #e6eef5);
}
.traj-meta {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

.halac-notes-block {
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  background: rgba(214, 90, 74, 0.06);
  border-left: 2px solid #d65a4a;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
}
.halac-notes-block b { color: #f5b08c; }

.halac-interpretation {
  font-size: 13px;
  font-style: italic;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 2px solid var(--accent-teal, #5be5d3);
  padding-left: 12px;
  margin: 0;
}

.footer-ref {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.4));
  text-align: right;
  font-style: italic;
  margin: 0;
}

/* ── Cách Cục ──────────────────────────────────────────────────────────── */
.cach-cuc-card {
  background: rgba(232, 201, 90, 0.04);
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  padding: 14px 16px;
}
.cach-cuc-card[data-polarity="favorable"] { border-left: 3px solid #5ab07a; }
.cach-cuc-card[data-polarity="mixed"]     { border-left: 3px solid #c0a878; }
.cach-cuc-card[data-polarity="challenging"] { border-left: 3px solid #d65a4a; }
.cach-cuc-card[data-polarity="neutral"]   { border-left: 3px solid #9a9a9a; }

.cach-cuc-card header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px dashed rgba(232, 201, 90, 0.2);
  padding-bottom: 8px;
  margin-bottom: 10px;
}
.cach-cuc-card header h3 {
  margin: 0;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 16px;
}
.cc-polarity {
  font-size: 11px;
  padding: 3px 9px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-weight: 600;
}
.cc-based-on {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.65));
}
.cc-based-on b { color: var(--accent-gold-soft, #f5e6b1); }
.cc-based-on em { color: var(--accent-teal, #5be5d3); font-style: normal; }
.cc-label {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.45));
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-right: 4px;
}
.cc-essence {
  margin: 0 0 10px 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary, #e6eef5);
  font-weight: 500;
}
.cc-prosand-cons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.cc-fav, .cc-ky { padding: 10px 12px; border-radius: 5px; }
.cc-fav {
  background: rgba(90, 176, 122, 0.06);
  border-left: 3px solid #5ab07a;
}
.cc-ky {
  background: rgba(214, 90, 74, 0.06);
  border-left: 3px solid #d65a4a;
}
.cc-fav h6, .cc-ky h6 {
  margin: 0 0 4px 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.cc-fav h6 { color: #88d39e; }
.cc-ky h6  { color: #f5b08c; }
.cc-fav p, .cc-ky p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230, 238, 245, 0.82));
}
.cc-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 0;
}

/* ── Dụng Thần ─────────────────────────────────────────────────────────── */
.dung-than-card {
  background: rgba(232, 201, 90, 0.04);
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  padding: 14px;
}
.dt-trio {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
.dt-cell {
  border: 1px solid;
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.dt-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  font-weight: 700;
}
.dt-cell strong {
  font-size: 18px;
  font-weight: 700;
}
.dt-cell small {
  font-size: 11px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
}
.dt-reason {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-primary, #e6eef5);
  margin: 0 0 8px 0;
}
.dt-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 0;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
  padding-top: 8px;
}
.dt-note em { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-style: italic; }
.dv-distance { color: var(--accent-teal, #5be5d3); font-size: 12px; }
.dv-distance small { color: var(--text-muted, rgba(230, 238, 245, 0.4)); }

/* ── Trường Sinh ───────────────────────────────────────────────────────── */
.truongsinh-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}
.ts-cell {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ts-cell[data-score="high"] { border-left: 3px solid #5ab07a; }
.ts-cell[data-score="mid"]  { border-left: 3px solid #9a9a9a; }
.ts-cell[data-score="low"]  { border-left: 3px solid #d65a4a; }
.ts-cell header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ts-cell h6 {
  margin: 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ts-cell header small {
  font-size: 14px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
  font-weight: 600;
}
.ts-cell strong {
  font-size: 15px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.ts-score {
  font-size: 12px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #d65a4a;
}
.ts-score[data-positive="true"] { color: #5ab07a; }
.ts-total {
  margin: 6px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
}
.ts-total b { color: var(--accent-gold-soft, #f5e6b1); }

/* ── Thần Sát ──────────────────────────────────────────────────────────── */
.ts-empty {
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-style: italic;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}
.than-sat-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 8px;
}
.ts-star {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 10px 12px;
}
.ts-star[data-polarity="lành"] { border-left: 3px solid #5ab07a; }
.ts-star[data-polarity="dữ"] { border-left: 3px solid #d65a4a; }
.ts-star[data-polarity="trung tính"] { border-left: 3px solid #c0a878; }
.ts-star-head { display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.ts-star-head strong {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.ts-tag {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.25);
  color: var(--accent-teal, #5be5d3);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
}
.ts-polarity {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
}
.ts-where {
  font-size: 10.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  margin-left: auto;
}
.ts-desc {
  margin: 4px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-secondary, rgba(230, 238, 245, 0.75));
}

/* ── Đại Vận ────────────────────────────────────────────────────────────── */
.dv-meta {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  margin: 0;
}
.dv-meta b { color: var(--accent-gold-soft, #f5e6b1); }
.dv-meta small { color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.dai-van-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 6px;
}
.dv-cycle {
  background: rgba(232, 201, 90, 0.05);
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 5px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}
.dv-age { display: flex; flex-direction: column; align-items: center; min-width: 46px; }
.dv-age strong {
  font-size: 12px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.dv-age small {
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.dv-stembr {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}
.dv-stem {
  font-size: 14px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
}
.dv-branch {
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
}
.dv-index {
  position: absolute;
  top: 4px;
  right: 6px;
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.4));
  font-weight: 700;
}
.dv-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 4px 0 0 0;
}

@media (max-width: 720px) {
  .halac-quai-pair { grid-template-columns: 1fr; }
  .halac-arrow { transform: rotate(90deg); }
  .bt-form { grid-template-columns: 1fr; }
  .dm-card { grid-template-columns: 1fr; }
  .dt-trio { grid-template-columns: 1fr; }
  .cc-prosand-cons { grid-template-columns: 1fr; }
}

/* Auspicious day section — separator between Hà Lạc trajectory and date picker */
.bt-auspicious-section {
  margin-top: 2.5rem;
}
.bt-divider {
  border: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color, #ddd), transparent);
  margin: 1.5rem 0 1rem;
}

/* Find-hour quiz button + modal */
.bt-hour-uncertain {
  margin: 0.8rem 0;
}
.bt-find-hour {
  padding: 0.5rem 1rem;
  background: #f0f8ff;
  border: 1px solid #4a90e2;
  color: #2a5db0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 500;
}
.bt-find-hour:hover {
  background: #e6f3ff;
}
.bt-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.bt-modal {
  background: #fff;
  padding: 1.5rem 1.5rem 1rem;
  max-width: 820px;
  width: 100%;
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 10px;
  position: relative;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
}
.bt-modal-close {
  position: absolute;
  top: 0.5rem;
  right: 0.8rem;
  background: transparent;
  border: 0;
  font-size: 1.4em;
  cursor: pointer;
  color: #888;
}
.bt-modal-close:hover { color: #333; }
</style>
