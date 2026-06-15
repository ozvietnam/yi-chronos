<script setup>
import { ref } from "vue";
import { getLunarReturns } from "../lib/api";
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
const ELEMENT_COLOR = { fire: "#d65a4a", earth: "#9a7b4a", air: "#4ab0c2", water: "#3a6cb0" };
const SIGN_ELEMENT = {
  aries: "fire", leo: "fire", sagittarius: "fire",
  taurus: "earth", virgo: "earth", capricorn: "earth",
  gemini: "air", libra: "air", aquarius: "air",
  cancer: "water", scorpio: "water", pisces: "water"
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth, { onReady: load }); // nhập 1 lần → tự vẽ; đổi profile → vẽ lại
const inputLat = ref("");
const inputLon = ref("");
const inputCount = ref(12);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const expanded = ref(null);

async function load() {
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
    data.value = await getLunarReturns({ birthAt, count: Number(inputCount.value), lat, lon });
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
}

function fmtDateTime(iso) {
  return new Intl.DateTimeFormat("vi-VN", {
    weekday: "short", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", timeZone: "Asia/Ho_Chi_Minh"
  }).format(new Date(iso));
}
</script>

<template>
  <section class="panel lr-panel">
    <div class="panel-title">
      <span>Lunar Returns — Tháng cá nhân</span>
      <small>chu kỳ ~27 ngày</small>
    </div>

    <p class="lr-note">
      Mỗi 27 ngày, Mặt Trăng quay về vị trí lúc anh sinh. Mỗi return tạo
      một "tháng cá nhân" với chủ đề riêng. Dùng để lên kế hoạch ngắn hạn.
    </p>

    <div class="lr-form">
      <label><span>Ngày giờ sinh</span><input v-model="inputBirth" type="datetime-local" step="60" /></label>
      <div class="lr-loc">
        <label><span>Vĩ độ</span><input v-model="inputLat" type="number" step="0.0001" /></label>
        <label><span>Kinh độ</span><input v-model="inputLon" type="number" step="0.0001" /></label>
      </div>
      <label><span>Số tháng</span><input v-model.number="inputCount" type="number" min="1" max="36" /></label>
      <div class="lr-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
      </div>
      <button class="apply-btn" @click="load" :disabled="loading">{{ loading ? "..." : "Vẽ" }}</button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <ul v-if="data" class="lr-list">
      <li v-for="r in data.returns" :key="r.index"
        :class="{ expanded: expanded === r.index }"
        @click="expanded = expanded === r.index ? null : r.index">
        <div class="head">
          <span class="idx">#{{ r.index }}</span>
          <span class="dt">{{ fmtDateTime(r.date_utc) }}</span>
          <span class="el" :style="{ color: ELEMENT_COLOR[r.chart.dominant_element] }">
            {{ ELEMENT_VI[r.chart.dominant_element] }}
          </span>
        </div>
        <div class="body">
          <span><b>Mặt Trời</b> {{ SIGN_GLYPH[r.chart.sun_sign] }} {{ SIGN_VI[r.chart.sun_sign] }}</span>
          <span v-if="r.chart.ascendant">
            <b>Mọc</b> {{ SIGN_GLYPH[r.chart.ascendant.sign] }} {{ SIGN_VI[r.chart.ascendant.sign] }}
          </span>
        </div>

        <div v-if="expanded === r.index" class="detail">
          <ul class="b-list">
            <li v-for="b in r.chart.bodies" :key="b.name">
              <span class="bn">{{ b.name }}</span>
              <span class="bs">{{ SIGN_GLYPH[b.sign] }} {{ SIGN_VI[b.sign] }}</span>
              <span class="bd">{{ b.sign_degree.toFixed(1) }}°</span>
              <span v-if="b.is_retrograde" class="retro">℞</span>
            </li>
          </ul>
        </div>
      </li>
    </ul>

    <p v-else class="empty-hint">Nhập ngày giờ sinh để xem các tháng tới.</p>
  </section>
</template>

<style scoped>
.lr-panel { display: flex; flex-direction: column; gap: 12px; }
.lr-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.lr-form {
  display: grid; grid-template-columns: 1.6fr 1.2fr 0.6fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.lr-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }
.lr-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}
.lr-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.lr-presets { display: flex; gap: 2px; }
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

.lr-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}
.lr-list li {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 8px 10px; cursor: pointer;
}
.lr-list li:hover { background: rgba(255,255,255,0.07); }
.lr-list li.expanded { background: rgba(232,201,90,0.05); border-color: rgba(232,201,90,0.3); }

.head {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 0.82rem; gap: 8px;
}
.idx { color: #e8c95a; font-weight: 600; }
.dt { color: rgba(255,255,255,0.85); flex: 1; }
.el { font-weight: 600; font-size: 0.78rem; }

.body {
  display: flex; gap: 16px; margin-top: 4px;
  font-size: 0.78rem; color: rgba(255,255,255,0.78);
  flex-wrap: wrap;
}
.body b { color: rgba(255,255,255,0.5); font-weight: 400; }

.detail { margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); }

.b-list {
  list-style: none; margin: 0; padding: 0;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 2px;
}
.b-list li {
  display: grid; grid-template-columns: 70px 1fr 50px 20px;
  font-size: 0.74rem; padding: 1px 4px;
  background: transparent; border: none; cursor: default;
}
.bn { color: rgba(255,255,255,0.55); }
.bd { font-family: ui-monospace, monospace; font-size: 0.72rem; }
.retro { color: #e89a8c; font-weight: 700; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
