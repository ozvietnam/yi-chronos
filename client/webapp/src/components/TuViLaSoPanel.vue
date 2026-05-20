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
  expandedPalace.value = null;
  errorMsg.value = "";
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
.sat-tinh { color: #fca5a5; font-size: 10px; }
.sat-tinh.loc-ton { color: #86efac; font-weight: 700; }
.sat-tinh.thien-ma { color: #fde68a; font-weight: 600; }
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
