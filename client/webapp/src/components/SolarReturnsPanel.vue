<script setup>
import { computed, ref } from "vue";
import { getSolarReturns } from "../lib/api";
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

const ELEMENT_VI = { fire: "Hỏa", earth: "Thổ", air: "Phong", water: "Thủy" };
const ELEMENT_COLOR = {
  fire: "#d65a4a", earth: "#9a7b4a", air: "#4ab0c2", water: "#3a6cb0"
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth);
const inputLat = ref("");
const inputLon = ref("");
const inputSpan = ref(60);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const expanded = ref(null);

const todayAge = computed(() => {
  if (!data.value) return null;
  const birthMs = new Date(data.value.birth_utc).getTime();
  return Math.floor((Date.now() - birthMs) / (365.25 * 86400 * 1000));
});

async function loadReturns() {
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
    data.value = await getSolarReturns({ birthAt, lat, lon, spanYears: Number(inputSpan.value) });
    expanded.value = null;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function setPreset(name) {
  if (name === "hanoi") { inputLat.value = "21.0285"; inputLon.value = "105.8542"; }
  else if (name === "saigon") { inputLat.value = "10.7626"; inputLon.value = "106.6602"; }
  else if (name === "danang") { inputLat.value = "16.0544"; inputLon.value = "108.2022"; }
}

function fmtDate(iso) {
  return new Intl.DateTimeFormat("vi-VN", { year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(iso));
}

function fmtTime(iso) {
  return new Intl.DateTimeFormat("vi-VN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Ho_Chi_Minh" }).format(new Date(iso));
}

function topAspects(chart, n = 3) {
  if (!chart?.aspects) return [];
  return [...chart.aspects].sort((a, b) => a.orb_deg - b.orb_deg).slice(0, n);
}

function bodyByName(chart, name) {
  return chart?.bodies?.find((b) => b.name === name) || null;
}

function toggleExpand(age) {
  expanded.value = expanded.value === age ? null : age;
}
</script>

<template>
  <section class="panel sr-panel">
    <div class="panel-title">
      <span>Solar Returns — Lá số sinh nhật mỗi năm</span>
      <small>{{ data?.ephemeris_source || "JPL DE440s" }}</small>
    </div>

    <p class="sr-note">
      Mỗi năm, Mặt Trời quay về đúng vị trí lúc anh sinh ra. Khoảnh khắc đó tạo
      ra lá số "năm cá nhân" — đọc cùng lá số sinh để hiểu chủ đề năm đó.
    </p>

    <div class="sr-form">
      <label>
        <span>Ngày giờ sinh</span>
        <input v-model="inputBirth" type="datetime-local" step="60" />
      </label>
      <div class="sr-loc">
        <label>
          <span>Vĩ độ</span>
          <input v-model="inputLat" type="number" step="0.0001" placeholder="21.0285" />
        </label>
        <label>
          <span>Kinh độ</span>
          <input v-model="inputLon" type="number" step="0.0001" placeholder="105.8542" />
        </label>
      </div>
      <label>
        <span>Năm</span>
        <input v-model.number="inputSpan" type="number" min="10" max="100" step="10" />
      </label>
      <div class="sr-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
        <button class="preset-btn" @click="setPreset('danang')">ĐN</button>
      </div>
      <button class="apply-btn" @click="loadReturns" :disabled="loading">
        {{ loading ? "Đang tính..." : "Vẽ" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="sr-grid">
        <div v-for="r in data.returns" :key="r.age"
          :class="['sr-card', expanded === r.age && 'expanded', todayAge === r.age && 'today']"
          @click="toggleExpand(r.age)">
          <div class="sr-card-head">
            <span class="age">{{ r.age }}t</span>
            <span class="date">{{ fmtDate(r.date_utc) }}</span>
          </div>
          <div class="sr-card-body">
            <div class="line">
              <span class="lbl">Trăng</span>
              <span class="val">{{ SIGN_GLYPH[r.chart.moon_sign] }} {{ SIGN_VI[r.chart.moon_sign] }}</span>
            </div>
            <div v-if="r.chart.ascendant" class="line">
              <span class="lbl">Mọc</span>
              <span class="val">{{ SIGN_GLYPH[r.chart.ascendant.sign] }} {{ SIGN_VI[r.chart.ascendant.sign] }}</span>
            </div>
            <div class="line element">
              <span class="lbl">Trội</span>
              <span class="val" :style="{ color: ELEMENT_COLOR[r.chart.dominant_element] }">
                {{ ELEMENT_VI[r.chart.dominant_element] }}
              </span>
            </div>
          </div>

          <div v-if="expanded === r.age" class="sr-detail">
            <p class="moment">Khoảnh khắc UTC: <code>{{ r.date_utc }}</code></p>
            <p class="moment">Giờ VN: <b>{{ fmtTime(r.date_utc) }}</b></p>

            <h5>Vị trí thiên thể</h5>
            <ul class="bodies">
              <li v-for="b in r.chart.bodies" :key="b.name">
                <span class="bn">{{ b.name }}</span>
                <span class="bs">{{ SIGN_GLYPH[b.sign] }} {{ SIGN_VI[b.sign] }}</span>
                <span class="bd">{{ b.sign_degree.toFixed(1) }}°</span>
                <span v-if="b.is_retrograde" class="retro">℞</span>
              </li>
            </ul>

            <template v-if="topAspects(r.chart).length">
              <h5>Góc sát nhất</h5>
              <ul class="aspects">
                <li v-for="(a, i) in topAspects(r.chart)" :key="i">
                  <b>{{ a.body_a }}</b> {{ a.aspect_type }} <b>{{ a.body_b }}</b>
                  <small>(sai số {{ a.orb_deg.toFixed(2) }}°)</small>
                </li>
              </ul>
            </template>
          </div>
        </div>
      </div>

      <p v-if="todayAge !== null" class="today-hint">
        Tuổi hiện tại: <b>{{ todayAge }}</b> · click vào ô tuổi đó để xem chủ đề năm đang sống.
      </p>
    </template>

    <p v-else class="empty-hint">Nhập ngày giờ sinh + tọa độ để xem từng năm.</p>
  </section>
</template>

<style scoped>
.sr-panel { display: flex; flex-direction: column; gap: 12px; }

.sr-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}

.sr-form {
  display: grid;
  grid-template-columns: 1.6fr 1.4fr 0.5fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}

.sr-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }

.sr-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}

.sr-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }

.sr-presets { display: flex; gap: 2px; }
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
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.sr-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 6px;
}

.sr-card {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 8px 10px; cursor: pointer;
  transition: background 0.15s, border 0.15s;
  display: flex; flex-direction: column; gap: 4px;
}

.sr-card:hover { background: rgba(255,255,255,0.07); }
.sr-card.today { border-color: rgba(232,201,90,0.6); background: rgba(232,201,90,0.05); }
.sr-card.expanded { grid-column: 1 / -1; background: rgba(232,201,90,0.06); }

.sr-card-head {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 0.78rem;
}
.age { font-weight: 700; color: #e8c95a; font-size: 0.92rem; }
.date { color: rgba(255,255,255,0.55); font-size: 0.72rem; font-family: ui-monospace, monospace; }

.sr-card-body { display: flex; flex-direction: column; gap: 2px; }

.line { display: flex; gap: 6px; align-items: baseline; font-size: 0.74rem; }
.lbl { color: rgba(255,255,255,0.45); width: 38px; }
.val { color: rgba(255,255,255,0.9); }
.line.element .val { font-weight: 600; }

.sr-detail {
  margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);
  display: flex; flex-direction: column; gap: 6px;
}
.sr-detail h5 {
  margin: 4px 0 2px 0; font-size: 0.74rem;
  color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px;
}
.moment { font-size: 0.74rem; color: rgba(255,255,255,0.7); margin: 0; }
.moment code {
  background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 3px;
}

.sr-detail ul { list-style: none; margin: 0; padding: 0; }
.sr-detail .bodies { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 2px; }

.sr-detail .bodies li {
  display: grid; grid-template-columns: 70px 1fr 50px 20px;
  font-size: 0.72rem; color: rgba(255,255,255,0.8); padding: 1px 4px;
}
.bn { color: rgba(255,255,255,0.5); }
.bd { font-family: ui-monospace, monospace; font-size: 0.7rem; }
.retro { color: #e89a8c; font-weight: 700; }

.sr-detail .aspects li {
  font-size: 0.74rem; color: rgba(255,255,255,0.85); padding: 2px 4px;
}
.sr-detail .aspects small { color: rgba(255,255,255,0.5); margin-left: 4px; }

.today-hint {
  font-size: 0.78rem; color: rgba(255,255,255,0.6);
  text-align: center; margin: 0;
}

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
