<script setup>
import { computed } from "vue";

const props = defineProps({
  laSo: { type: Object, required: true },
  // Optional: highlight 1 cung (vd Phu Thê)
  highlightPalace: { type: String, default: "" },
});

// Layout 4x4 chuẩn — index branch theo grid
// Row 0: Tỵ(5)  Ngọ(6)  Mùi(7)  Thân(8)
// Row 1: Thìn(4) — center — Dậu(9)
// Row 2: Mão(3) — center — Tuất(10)
// Row 3: Dần(2) Sửu(1)  Tý(0)  Hợi(11)
const GRID_LAYOUT = [
  // row, col, branch_index
  { row: 0, col: 0, branch: "Tỵ", idx: 5 },
  { row: 0, col: 1, branch: "Ngọ", idx: 6 },
  { row: 0, col: 2, branch: "Mùi", idx: 7 },
  { row: 0, col: 3, branch: "Thân", idx: 8 },
  { row: 1, col: 0, branch: "Thìn", idx: 4 },
  { row: 1, col: 3, branch: "Dậu", idx: 9 },
  { row: 2, col: 0, branch: "Mão", idx: 3 },
  { row: 2, col: 3, branch: "Tuất", idx: 10 },
  { row: 3, col: 0, branch: "Dần", idx: 2 },
  { row: 3, col: 1, branch: "Sửu", idx: 1 },
  { row: 3, col: 2, branch: "Tý", idx: 0 },
  { row: 3, col: 3, branch: "Hợi", idx: 11 },
];

const BRANCHES = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"];

// Map branch_index → cung name
const palaceByBranch = computed(() => {
  const m = {};
  for (const p of (props.laSo.palaces || [])) {
    m[p.branch_index] = p.name;
  }
  return m;
});

function starsAt(branch_idx) {
  const ls = props.laSo;
  const out = { chinh: [], phu: [], sat: [], q2: [], bac_si: [], tuong_tinh: [], thai_tue: [], sao_le: [] };

  const ct = ls.chinh_tinh || {};
  for (const [s, i] of Object.entries(ct)) if (i === branch_idx) out.chinh.push(s);
  const pt = ls.phu_tinh || {};
  for (const [s, i] of Object.entries(pt)) if (i === branch_idx) out.phu.push(s);
  const st = ls.sat_tinh || {};
  for (const [s, i] of Object.entries(st)) if (i === branch_idx) out.sat.push(s);
  const q2 = ls.sao_q2 || {};
  for (const [s, i] of Object.entries(q2)) if (i === branch_idx) out.q2.push(s);
  const bs = ls.bac_si_belt || {};
  for (const [s, i] of Object.entries(bs)) if (i === branch_idx) out.bac_si.push(s);
  const tt = ls.tuong_tinh_belt || {};
  for (const [s, i] of Object.entries(tt)) if (i === branch_idx) out.tuong_tinh.push(s);
  const tue = ls.thai_tue_belt || {};
  for (const [s, i] of Object.entries(tue)) if (i === branch_idx) out.thai_tue.push(s);
  const sl = ls.sao_le || {};
  for (const [s, i] of Object.entries(sl)) if (i === branch_idx) out.sao_le.push(s);
  return out;
}

// Hóa năm sinh tại sao trong cung
function hoaInPalace(branch_idx) {
  const hoa = props.laSo.tu_hoa || {};
  const stars = starsAt(branch_idx);
  const allStars = new Set([...stars.chinh, ...stars.phu, ...stars.q2]);
  const out = [];
  for (const [hoaKey, star] of Object.entries(hoa)) {
    if (allStars.has(star)) {
      out.push({ star, hoa: hoaKey });
    }
  }
  return out;
}

function isTrietBranch(branch_idx) {
  return (props.laSo.triet || []).includes(branch_idx);
}
function isTuanBranch(branch_idx) {
  return (props.laSo.tuan || []).includes(branch_idx);
}

const meta = computed(() => ({
  cuc: props.laSo.cuc_name || "",
  menh_chu: props.laSo.menh_chu || "",
  than_chu: props.laSo.than_chu || "",
  year_stem: props.laSo.year_stem || "",
  year_branch: props.laSo.year_branch || "",
  hour_branch: props.laSo.hour_branch || "",
  lunar_month: props.laSo.lunar_month || "",
  lunar_day: props.laSo.lunar_day || "",
  triet: (props.laSo.triet || []).map((i) => BRANCHES[i]).join("-"),
  tuan: (props.laSo.tuan || []).map((i) => BRANCHES[i]).join("-"),
}));
</script>

<template>
  <div class="la-so-chart">
    <div class="chart-grid">
      <!-- 12 cung -->
      <div
        v-for="cell in GRID_LAYOUT"
        :key="cell.branch"
        class="cung-cell"
        :class="{
          'col-0': cell.col === 0,
          'col-1': cell.col === 1,
          'col-2': cell.col === 2,
          'col-3': cell.col === 3,
          'row-0': cell.row === 0,
          'row-1': cell.row === 1,
          'row-2': cell.row === 2,
          'row-3': cell.row === 3,
          'is-triet': isTrietBranch(cell.idx),
          'is-tuan': isTuanBranch(cell.idx),
          'is-highlight': palaceByBranch[cell.idx] === highlightPalace,
        }"
      >
        <div class="cung-header">
          <span class="branch">{{ cell.branch }}</span>
          <span class="palace-name">{{ palaceByBranch[cell.idx] || "?" }}</span>
        </div>
        <div class="cung-stars">
          <!-- Chính tinh -->
          <div v-if="starsAt(cell.idx).chinh.length" class="row chinh">
            <span v-for="s in starsAt(cell.idx).chinh" :key="s" class="star primary">
              {{ s }}
            </span>
          </div>
          <!-- Hóa -->
          <div v-if="hoaInPalace(cell.idx).length" class="row hoa">
            <span v-for="h in hoaInPalace(cell.idx)" :key="h.star+h.hoa" class="star hoa-chip">
              {{ h.star }} Hóa {{ h.hoa }}
            </span>
          </div>
          <!-- Phụ -->
          <div v-if="starsAt(cell.idx).phu.length" class="row phu">
            <span v-for="s in starsAt(cell.idx).phu" :key="s" class="star phu-s">{{ s }}</span>
          </div>
          <!-- Sát -->
          <div v-if="starsAt(cell.idx).sat.length" class="row sat">
            <span v-for="s in starsAt(cell.idx).sat" :key="s" class="star sat-s">{{ s }}</span>
          </div>
          <!-- Q2 -->
          <div v-if="starsAt(cell.idx).q2.length" class="row q2">
            <span v-for="s in starsAt(cell.idx).q2" :key="s" class="star q2-s">{{ s }}</span>
          </div>
          <!-- Tuế Tiền + Bác Sĩ + Tướng Tinh -->
          <div v-if="starsAt(cell.idx).thai_tue.length" class="row tt">
            <span v-for="s in starsAt(cell.idx).thai_tue" :key="s" class="star tt-s">{{ s }}</span>
          </div>
          <div v-if="starsAt(cell.idx).bac_si.length" class="row bs">
            <span v-for="s in starsAt(cell.idx).bac_si" :key="s" class="star bs-s">{{ s }}</span>
          </div>
          <div v-if="starsAt(cell.idx).tuong_tinh.length" class="row tg">
            <span v-for="s in starsAt(cell.idx).tuong_tinh" :key="s" class="star tg-s">{{ s }}</span>
          </div>
          <!-- Sao lẻ -->
          <div v-if="starsAt(cell.idx).sao_le.length" class="row sl">
            <span v-for="s in starsAt(cell.idx).sao_le" :key="s" class="star sl-s">{{ s }}</span>
          </div>
        </div>
        <!-- Triệt / Tuần marker -->
        <div v-if="isTrietBranch(cell.idx)" class="triet-marker">⛔ TRIỆT</div>
        <div v-if="isTuanBranch(cell.idx)" class="tuan-marker">○ TUẦN</div>
      </div>

      <!-- Center meta -->
      <div class="meta-center">
        <h3>Lá số đầy đủ</h3>
        <div class="meta-row"><strong>Sinh:</strong> {{ meta.lunar_month }}/{{ meta.lunar_day }} giờ {{ meta.hour_branch }}</div>
        <div class="meta-row"><strong>Năm:</strong> {{ meta.year_stem }} {{ meta.year_branch }}</div>
        <div class="meta-row"><strong>Cục:</strong> {{ meta.cuc }}</div>
        <div class="meta-row"><strong>Mệnh chủ:</strong> {{ meta.menh_chu }}</div>
        <div class="meta-row"><strong>Thân chủ:</strong> {{ meta.than_chu }}</div>
        <div class="meta-row triet-row"><strong>Triệt:</strong> {{ meta.triet }}</div>
        <div class="meta-row tuan-row"><strong>Tuần:</strong> {{ meta.tuan }}</div>
      </div>
    </div>

    <div class="legend">
      <span class="legend-item"><span class="dot primary"></span> Chính tinh</span>
      <span class="legend-item"><span class="dot hoa-chip"></span> Hóa Tứ</span>
      <span class="legend-item"><span class="dot phu-s"></span> Phụ tinh</span>
      <span class="legend-item"><span class="dot sat-s"></span> Sát tinh</span>
      <span class="legend-item"><span class="dot q2-s"></span> Đào hoa/Khốc Hư</span>
      <span class="legend-item"><span class="dot tt-s"></span> Tuế Tiền</span>
      <span class="legend-item"><span class="dot bs-s"></span> Bác Sĩ vòng</span>
      <span class="legend-item"><span class="dot tg-s"></span> Tướng Tinh vòng</span>
      <span class="legend-item"><span class="dot sl-s"></span> Sao lẻ</span>
    </div>
  </div>
</template>

<style scoped>
.la-so-chart {
  font-family: var(--font-family, sans-serif);
  color: var(--read-text, #e9dcc6);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, minmax(140px, auto));
  gap: 3px;
  background: var(--read-border, rgba(201, 161, 74, 0.22));
  border: 1px solid var(--read-rule, #c9a14a);
  border-radius: 6px;
  padding: 3px;
  position: relative;
}

/* Center: spans 2x2 trong giữa */
.meta-center {
  grid-column: 2 / 4;
  grid-row: 2 / 4;
  background: linear-gradient(135deg, rgba(217, 185, 119, 0.08) 0%, rgba(201, 161, 74, 0.05) 100%);
  border: 1px solid var(--read-rule, #c9a14a);
  border-radius: 4px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.88em;
}
.meta-center h3 {
  margin: 0 0 8px;
  color: var(--read-han, #d9b977);
  font-size: 1em;
  text-align: center;
}
.meta-row strong { color: var(--read-han, #d9b977); margin-right: 6px; }
.meta-row.triet-row { color: #ff8a8a; }
.meta-row.tuan-row { color: #ffb88a; }

.cung-cell {
  background: var(--read-bg, #1d1813);
  border-radius: 3px;
  padding: 6px;
  font-size: 0.78em;
  position: relative;
  overflow: hidden;
}
.cung-cell.is-triet::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent 48%, rgba(255, 138, 138, 0.18) 48%, rgba(255, 138, 138, 0.18) 52%, transparent 52%);
  pointer-events: none;
}
.cung-cell.is-tuan::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(-45deg, transparent 48%, rgba(255, 184, 138, 0.14) 48%, rgba(255, 184, 138, 0.14) 52%, transparent 52%);
  pointer-events: none;
}
.cung-cell.is-highlight {
  background: rgba(126, 234, 218, 0.10);
  border: 1.5px solid #7eeada;
  box-shadow: 0 0 12px rgba(126, 234, 218, 0.18);
}

.cung-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
  padding-bottom: 3px;
  border-bottom: 1px dashed var(--read-border, rgba(201, 161, 74, 0.22));
}
.cung-header .branch {
  font-weight: 700;
  color: var(--read-han, #d9b977);
}
.cung-header .palace-name {
  font-size: 0.95em;
  font-weight: 600;
  color: var(--read-heading, #f3e6c8);
  letter-spacing: 0.5px;
}

.cung-stars {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}
.star {
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 0.93em;
  line-height: 1.35;
}
.star.primary {
  color: #f3e6c8;
  font-weight: 700;
  font-size: 1.02em;
}
.hoa-chip {
  color: #ffd966;
  background: rgba(255, 217, 102, 0.10);
  font-weight: 600;
}
.phu-s {
  color: #7eeada;
}
.sat-s {
  color: #ff8a8a;
}
.q2-s {
  color: #c9a14a;
  opacity: 0.92;
}
.tt-s {
  color: #b39ddb;
  font-size: 0.86em;
  opacity: 0.85;
}
.bs-s {
  color: #90caf9;
  font-size: 0.86em;
  opacity: 0.85;
}
.tg-s {
  color: #ce93d8;
  font-size: 0.86em;
  opacity: 0.82;
}
.sl-s {
  color: var(--read-text-dim, rgba(233, 220, 198, 0.65));
  font-size: 0.82em;
  font-style: italic;
}

.triet-marker, .tuan-marker {
  position: absolute;
  bottom: 4px;
  right: 4px;
  font-size: 0.74em;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 2px;
}
.triet-marker {
  background: rgba(255, 138, 138, 0.20);
  color: #ff8a8a;
}
.tuan-marker {
  background: rgba(255, 184, 138, 0.16);
  color: #ffb88a;
  bottom: 22px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
  padding: 8px 12px;
  background: var(--read-surface, #221b14);
  border: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  border-radius: 4px;
  font-size: 0.85em;
}
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-item .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
.dot.primary { background: #f3e6c8; }
.dot.hoa-chip { background: #ffd966; }
.dot.phu-s { background: #7eeada; }
.dot.sat-s { background: #ff8a8a; }
.dot.q2-s { background: #c9a14a; }
.dot.tt-s { background: #b39ddb; }
.dot.bs-s { background: #90caf9; }
.dot.tg-s { background: #ce93d8; }
.dot.sl-s { background: rgba(233, 220, 198, 0.65); }
</style>
