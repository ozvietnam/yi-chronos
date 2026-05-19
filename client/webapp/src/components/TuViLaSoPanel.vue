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
      </div>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <!-- ── Lá số 4×4 grid ─────────────────────────────────────────── -->
    <template v-if="data">
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
              <header class="cell-head">
                <span class="cell-branch">{{ ['Tý','Sửu','Dần','Mão','Thìn','Tỵ','Ngọ','Mùi','Thân','Dậu','Tuất','Hợi'][cell.branchIndex] }}</span>
                <span class="cell-palace">{{ cell.palace?.name }}</span>
              </header>
              <ul class="stars chinh">
                <li v-for="s in cell.chinh" :key="s.name" class="star chinh-tinh">
                  {{ s.name }}
                  <span v-if="s.hoa" class="hoa-badge" :style="{ background: HOA_COLOR[s.hoa] + '33', color: HOA_COLOR[s.hoa], borderColor: HOA_COLOR[s.hoa] }">
                    {{ s.hoa[0] }}
                  </span>
                </li>
              </ul>
              <ul v-if="cell.phu.length" class="stars phu">
                <li v-for="s in cell.phu" :key="s.name" class="star phu-tinh">
                  {{ s.name }}
                  <span v-if="s.hoa" class="hoa-badge" :style="{ background: HOA_COLOR[s.hoa] + '33', color: HOA_COLOR[s.hoa] }">
                    {{ s.hoa[0] }}
                  </span>
                </li>
              </ul>
              <ul v-if="cell.sat.length" class="stars sat">
                <li v-for="s in cell.sat" :key="s.name" class="star sat-tinh">{{ s.name }}</li>
              </ul>
              <span v-if="cell.palace?.name === 'Mệnh'" class="menh-mark">★ MỆNH</span>
              <span v-if="cell.branchIndex === data.than_index" class="than-mark">身 THÂN</span>
              <span v-if="cell.branchIndex === data.dau_quan_index" class="dauquan-mark"
                    title="Đẩu Quân — sao tháng sinh. Source: TVDSTT Q.2 (Trần Đoàn)">
                斗 ĐẨU QUÂN
              </span>
            </template>
            <template v-else-if="cell.type === 'center-tl'">
              <div class="center-info center-name">
                <h3>{{ data.cuc_name }}</h3>
                <p>Cục số {{ data.cuc }}</p>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-tr'">
              <div class="center-info">
                <span class="ci-label">Mệnh / Thân</span>
                <p><b>{{ data.menh_branch }}</b> / <b>{{ data.than_branch }}</b></p>
                <template v-if="data.menh_chu">
                  <span class="ci-label">Mệnh chủ · Thân chủ</span>
                  <p class="ms-chu"
                     title="Mệnh chủ (theo địa chi Mệnh cung) + Thân chủ (theo địa chi năm sinh). Source: TVDSTT Q.2">
                    ⭐ <b>{{ data.menh_chu }}</b><br/>
                    ⭐ <b>{{ data.than_chu }}</b>
                  </p>
                </template>
                <template v-else>
                  <span class="ci-label">Giới tính</span>
                  <p>{{ data.gender }}</p>
                </template>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-bl'">
              <div class="center-info">
                <span class="ci-label">Năm sinh</span>
                <p>{{ data.year_stem }} {{ data.year_branch }}</p>
                <span class="ci-label">Giờ / Tháng âm</span>
                <p>{{ data.hour_branch }} · tháng {{ data.lunar_month }}</p>
              </div>
            </template>
            <template v-else-if="cell.type === 'center-br'">
              <div class="center-info center-hoa">
                <span class="ci-label">Tứ Hóa năm {{ data.year_stem }}</span>
                <p class="hoa-line" v-for="(star, hoa) in data.tu_hoa" :key="hoa">
                  <span class="hoa-tag" :style="{ background: HOA_COLOR[hoa] + '22', color: HOA_COLOR[hoa] }">
                    {{ hoa }}
                  </span>
                  <em>{{ star }}</em>
                </p>
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

    <!-- Cách cục đọc sâu modal -->
    <div v-if="showCachCuc" class="cc-modal-backdrop" @click.self="showCachCuc = false">
      <div class="cc-modal">
        <button class="cc-modal-close" @click="showCachCuc = false">✕</button>
        <CachCucPanel />
      </div>
    </div>
  </section>
</template>

<style scoped>
.tvls-panel { display: flex; flex-direction: column; gap: 14px; }

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

/* Cách cục modal wrapper */
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

/* ── 4×4 lá số grid ────────────────────────────────────────────────────── */
.laso-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, minmax(140px, auto));
  gap: 4px;
  background: rgba(232, 201, 90, 0.04);
  padding: 6px;
  border-radius: 8px;
  border: 1px solid rgba(232, 201, 90, 0.2);
}

.laso-cell {
  background: rgba(20, 30, 45, 0.55);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 6px 7px;
  font-size: 11.5px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  position: relative;
  min-height: 0;
}
.laso-cell.center {
  background: rgba(232, 201, 90, 0.06);
  border-color: rgba(232, 201, 90, 0.18);
}
.laso-cell.is-menh {
  background: rgba(232, 201, 90, 0.12);
  border-color: rgba(232, 201, 90, 0.5);
  box-shadow: 0 0 0 1px rgba(232, 201, 90, 0.3);
}
.laso-cell.is-than {
  border-left: 3px solid #d65a78;
}

.cell-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  padding-bottom: 3px;
  margin-bottom: 2px;
}
.cell-branch {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}
.cell-palace {
  font-size: 12px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
}

.stars { list-style: none; margin: 0; padding: 0; }
.star {
  display: flex;
  align-items: baseline;
  gap: 3px;
  line-height: 1.35;
  font-size: 11.5px;
}
.chinh-tinh { color: var(--accent-gold-soft, #f5e6b1); font-weight: 700; }
.phu-tinh { color: var(--accent-teal, #5be5d3); font-size: 11px; }
.sat-tinh { color: #d65a4a; font-size: 10.5px; }

.hoa-badge {
  display: inline-block;
  font-size: 8.5px;
  padding: 0 4px;
  border-radius: 2px;
  border: 1px solid;
  font-weight: 700;
}

.menh-mark, .than-mark {
  position: absolute;
  bottom: 3px;
  font-size: 9.5px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 2px;
}
.menh-mark {
  right: 4px;
  background: rgba(232, 201, 90, 0.2);
  color: var(--accent-gold, #e8c95a);
}
.than-mark {
  left: 4px;
  background: rgba(214, 90, 120, 0.2);
  color: #f5a5b5;
}
.dauquan-mark {
  top: 3px;
  right: 4px;
  background: rgba(56, 189, 248, 0.18);
  color: #7dd3fc;
  font-family: "Songti SC", serif;
}
.ms-chu {
  font-size: 11.5px;
  margin: 0;
  line-height: 1.35;
  color: var(--accent-gold, #fde68a);
}
.ms-chu b {
  color: #fff;
}

/* Center cells */
.center-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
}
.center-name h3 {
  margin: 0;
  font-size: 14px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.center-name p {
  margin: 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
}
.ci-label {
  font-size: 9px;
  color: var(--text-muted, rgba(230, 238, 245, 0.45));
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-top: 3px;
}
.center-info p {
  margin: 0;
  font-size: 12px;
  color: var(--text-primary, #e6eef5);
}
.center-info p b { color: var(--accent-gold-soft, #f5e6b1); }
.hoa-line {
  display: flex;
  gap: 5px;
  font-size: 10.5px;
  align-items: center;
  margin: 1px 0 !important;
}
.hoa-line em {
  color: var(--text-secondary, rgba(230, 238, 245, 0.85));
  font-style: normal;
}
.hoa-tag {
  font-size: 9.5px;
  padding: 1px 5px;
  border-radius: 2px;
  font-weight: 700;
  min-width: 28px;
  text-align: center;
}

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
