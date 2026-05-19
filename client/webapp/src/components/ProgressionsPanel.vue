<script setup>
import { computed, ref } from "vue";
import { getProgressedChart, getProgressedMoonTimeline } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const SIGN_VI = {
  aries: "Bạch Dương", taurus: "Kim Ngưu", gemini: "Song Tử",
  cancer: "Cự Giải", leo: "Sư Tử", virgo: "Xử Nữ",
  libra: "Thiên Bình", scorpio: "Bọ Cạp", sagittarius: "Nhân Mã",
  capricorn: "Ma Kết", aquarius: "Bảo Bình", pisces: "Song Ngư"
};
const SIGN_GLYPH = {
  aries: "♈", taurus: "♉", gemini: "♊", cancer: "♋", leo: "♌", virgo: "♍",
  libra: "♎", scorpio: "♏", sagittarius: "♐", capricorn: "♑", aquarius: "♒", pisces: "♓"
};
const SIGN_ELEMENT = {
  aries: "fire", leo: "fire", sagittarius: "fire",
  taurus: "earth", virgo: "earth", capricorn: "earth",
  gemini: "air", libra: "air", aquarius: "air",
  cancer: "water", scorpio: "water", pisces: "water"
};
const ELEMENT_COLOR = { fire: "#d65a4a", earth: "#9a7b4a", air: "#4ab0c2", water: "#3a6cb0" };

const inputBirth = ref("");
useActivePersonBirth(inputBirth);
const inputLat = ref("");
const inputLon = ref("");
const inputSpan = ref(90);
const ageQuery = ref(30);
const phasesData = ref(null);
const chartData = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const SVG_WIDTH = 700;
const SVG_HEIGHT = 70;
const PAD = 16;

const ageScale = computed(() => {
  const span = phasesData.value?.span_years || 90;
  return (a) => PAD + (a / span) * (SVG_WIDTH - 2 * PAD);
});

const phaseRibbons = computed(() => {
  if (!phasesData.value) return [];
  const span = phasesData.value.span_years;
  return phasesData.value.phases.map((p) => {
    const start = ageScale.value(p.age_start);
    const end = ageScale.value(p.age_end ?? span);
    return {
      ...p,
      x: start,
      width: Math.max(end - start, 1),
      color: ELEMENT_COLOR[SIGN_ELEMENT[p.sign]]
    };
  });
});

const yearTicks = computed(() => {
  const span = phasesData.value?.span_years || 90;
  const ticks = [];
  for (let a = 0; a <= span; a += 10) ticks.push({ age: a, x: ageScale.value(a) });
  return ticks;
});

const todayAge = computed(() => {
  if (!phasesData.value) return null;
  const birthMs = new Date(phasesData.value.birth_utc).getTime();
  const a = (Date.now() - birthMs) / (365.25 * 86400 * 1000);
  if (a < 0 || a > phasesData.value.span_years) return null;
  return a;
});

async function loadAll() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần ngày giờ sinh";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const local = new Date(inputBirth.value);
    if (Number.isNaN(local.getTime())) throw new Error("Định dạng thời điểm không hợp lệ");
    const birthAt = local.toISOString();
    const lat = inputLat.value !== "" ? Number(inputLat.value) : null;
    const lon = inputLon.value !== "" ? Number(inputLon.value) : null;
    phasesData.value = await getProgressedMoonTimeline({ birthAt, spanYears: Number(inputSpan.value) });
    chartData.value = await getProgressedChart({ birthAt, atAge: Number(ageQuery.value), lat, lon });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

async function refreshChartAtAge() {
  if (!inputBirth.value) return;
  loading.value = true;
  try {
    const local = new Date(inputBirth.value);
    const birthAt = local.toISOString();
    const lat = inputLat.value !== "" ? Number(inputLat.value) : null;
    const lon = inputLon.value !== "" ? Number(inputLon.value) : null;
    chartData.value = await getProgressedChart({ birthAt, atAge: Number(ageQuery.value), lat, lon });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function setPreset(name) {
  if (name === "hanoi") { inputLat.value = "21.0285"; inputLon.value = "105.8542"; }
  else if (name === "saigon") { inputLat.value = "10.7626"; inputLon.value = "106.6602"; }
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("vi-VN", { year: "numeric", month: "2-digit" }).format(new Date(iso));
}
</script>

<template>
  <section class="panel pr-panel">
    <div class="panel-title">
      <span>Tiến triển — Progressed Moon Timeline + lá số tiến triển theo tuổi</span>
      <small>1 ngày = 1 năm</small>
    </div>

    <p class="pr-note">
      Mỗi ngày sau sinh tượng trưng cho một năm sống. Tracking <b>Mặt Trăng tiến triển</b>
      cho biết "chương cảm xúc" anh đang sống — đổi cung mỗi ~2.5 năm.
    </p>

    <div class="pr-form">
      <label><span>Ngày giờ sinh</span><input v-model="inputBirth" type="datetime-local" step="60" /></label>
      <div class="pr-loc">
        <label><span>Vĩ độ</span><input v-model="inputLat" type="number" step="0.0001" /></label>
        <label><span>Kinh độ</span><input v-model="inputLon" type="number" step="0.0001" /></label>
      </div>
      <label><span>Năm</span><input v-model.number="inputSpan" type="number" min="20" max="100" step="10" /></label>
      <div class="pr-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
      </div>
      <button class="apply-btn" @click="loadAll" :disabled="loading">{{ loading ? "..." : "Vẽ" }}</button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="phasesData">
      <h4 class="sec-title">Mặt Trăng tiến triển — chương cảm xúc</h4>
      <div class="ribbon-wrap">
        <svg :viewBox="`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`" class="ribbon">
          <g v-for="r in phaseRibbons" :key="`r-${r.age_start}`">
            <rect :x="r.x" :y="20" :width="r.width" :height="32" :fill="r.color" fill-opacity="0.4"
              :stroke="r.color" stroke-opacity="0.7" stroke-width="0.6" />
            <text v-if="r.width > 25" :x="r.x + r.width / 2" :y="40" text-anchor="middle" class="r-glyph">
              {{ SIGN_GLYPH[r.sign] }}
            </text>
            <title>{{ SIGN_VI[r.sign] }} · từ {{ fmtDate(r.date_start_utc) }} đến {{ fmtDate(r.date_end_utc) }}</title>
          </g>
          <g v-for="t in yearTicks" :key="`t-${t.age}`">
            <line :x1="t.x" :y1="52" :x2="t.x" :y2="56" stroke="rgba(255,255,255,0.3)" />
            <text :x="t.x" :y="65" text-anchor="middle" class="ax-tick">{{ t.age }}</text>
          </g>
          <g v-if="todayAge !== null">
            <line :x1="ageScale(todayAge)" :y1="14" :x2="ageScale(todayAge)" :y2="56"
              stroke="#e8c95a" stroke-width="1.5" stroke-dasharray="2 2" />
            <text :x="ageScale(todayAge)" :y="12" text-anchor="middle" class="today-tick">hôm nay</text>
          </g>
        </svg>
      </div>

      <ul class="phase-list">
        <li v-for="p in phasesData.phases" :key="`p-${p.age_start}`">
          <span class="age">{{ p.age_start.toFixed(1) }}–{{ p.age_end !== null ? p.age_end.toFixed(1) : "..." }}t</span>
          <span class="sign" :style="{ color: ELEMENT_COLOR[SIGN_ELEMENT[p.sign]] }">
            {{ SIGN_GLYPH[p.sign] }} {{ SIGN_VI[p.sign] }}
          </span>
          <span class="dt">{{ fmtDate(p.date_start_utc) }} → {{ fmtDate(p.date_end_utc) }}</span>
        </li>
      </ul>
    </template>

    <template v-if="phasesData">
      <h4 class="sec-title">Lá số tiến triển tại tuổi cụ thể</h4>
      <div class="age-slider">
        <input v-model.number="ageQuery" type="range" min="0" :max="phasesData?.span_years || 90" step="1"
          @change="refreshChartAtAge" />
        <span class="age-val">tuổi <b>{{ ageQuery }}</b></span>
      </div>

      <div v-if="chartData" class="chart-summary">
        <div class="cs-cell">
          <span>Mặt Trời tiến triển</span>
          <strong>{{ SIGN_GLYPH[chartData.chart.sun_sign] }} {{ SIGN_VI[chartData.chart.sun_sign] }}</strong>
        </div>
        <div class="cs-cell">
          <span>Mặt Trăng tiến triển</span>
          <strong>{{ SIGN_GLYPH[chartData.chart.moon_sign] }} {{ SIGN_VI[chartData.chart.moon_sign] }}</strong>
        </div>
        <div v-if="chartData.chart.ascendant" class="cs-cell">
          <span>Mọc tiến triển</span>
          <strong>
            {{ SIGN_GLYPH[chartData.chart.ascendant.sign] }}
            {{ SIGN_VI[chartData.chart.ascendant.sign] }}
            {{ chartData.chart.ascendant.sign_degree.toFixed(1) }}°
          </strong>
        </div>
        <div class="cs-cell">
          <span>Nguyên tố trội</span>
          <strong :style="{ color: ELEMENT_COLOR[chartData.chart.dominant_element] }">
            {{ chartData.chart.dominant_element }}
          </strong>
        </div>
      </div>

      <ul v-if="chartData" class="bodies-list">
        <li v-for="b in chartData.chart.bodies" :key="b.name">
          <span class="bn">{{ b.name }}</span>
          <span class="bs">{{ SIGN_GLYPH[b.sign] }} {{ SIGN_VI[b.sign] }}</span>
          <span class="bd">{{ b.sign_degree.toFixed(1) }}°</span>
          <span v-if="b.is_retrograde" class="retro">℞</span>
        </li>
      </ul>
    </template>

    <p v-else class="empty-hint">Nhập ngày giờ sinh để xem.</p>
  </section>
</template>

<style scoped>
.pr-panel { display: flex; flex-direction: column; gap: 12px; }
.pr-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.pr-form {
  display: grid; grid-template-columns: 1.6fr 1.2fr 0.5fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.pr-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }
.pr-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}
.pr-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.pr-presets { display: flex; gap: 2px; }
.preset-btn {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.85); padding: 5px 7px; border-radius: 4px;
  font-size: 0.72rem; cursor: pointer;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 7px 14px; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
}

.sec-title {
  margin: 6px 0 0 0; font-size: 0.85rem;
  color: rgba(255,255,255,0.85); text-transform: uppercase;
  letter-spacing: 0.4px; font-weight: 600;
}

.ribbon-wrap {
  background: rgba(255,255,255,0.02); border-radius: 6px; padding: 4px;
  overflow-x: auto;
}
.ribbon { width: 100%; height: auto; min-width: 600px; }
.r-glyph { fill: #fff; font-size: 14px; }
.ax-tick { fill: rgba(255,255,255,0.5); font-size: 9px; }
.today-tick { fill: #e8c95a; font-size: 9px; }

.phase-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 2px;
  max-height: 220px; overflow-y: auto;
  background: rgba(255,255,255,0.02); border-radius: 6px; padding: 6px;
}
.phase-list li {
  display: grid; grid-template-columns: 90px 150px 1fr;
  gap: 8px; font-size: 0.78rem; color: rgba(255,255,255,0.8);
  padding: 3px 6px; border-radius: 3px;
}
.phase-list .age { color: #e8c95a; font-weight: 600; }
.phase-list .sign { font-weight: 500; }
.phase-list .dt { color: rgba(255,255,255,0.5); font-size: 0.72rem; }

.age-slider {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;
}
.age-slider input[type="range"] { flex: 1; }
.age-val { font-size: 0.85rem; color: #e8c95a; }

.chart-summary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  background: rgba(232,201,90,0.05); padding: 10px; border-radius: 8px;
}
.cs-cell { display: flex; flex-direction: column; gap: 2px; }
.cs-cell span { font-size: 0.7rem; color: rgba(255,255,255,0.55); text-transform: uppercase; }
.cs-cell strong { font-size: 0.92rem; color: #f5e6b1; }

.bodies-list {
  list-style: none; margin: 0; padding: 0;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 4px;
  background: rgba(255,255,255,0.02); border-radius: 6px; padding: 8px;
}
.bodies-list li {
  display: grid; grid-template-columns: 70px 1fr 50px 20px;
  font-size: 0.74rem; color: rgba(255,255,255,0.8); padding: 1px 4px;
}
.bn { color: rgba(255,255,255,0.55); }
.bd { font-family: ui-monospace, monospace; font-size: 0.72rem; }
.retro { color: #e89a8c; font-weight: 700; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
