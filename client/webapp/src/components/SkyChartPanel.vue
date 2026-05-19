<script setup>
import { computed, onMounted, ref } from "vue";
import { getSkyNow } from "../lib/api";

const SIGN_VI = {
  aries: "Bạch Dương",
  taurus: "Kim Ngưu",
  gemini: "Song Tử",
  cancer: "Cự Giải",
  leo: "Sư Tử",
  virgo: "Xử Nữ",
  libra: "Thiên Bình",
  scorpio: "Bọ Cạp",
  sagittarius: "Nhân Mã",
  capricorn: "Ma Kết",
  aquarius: "Bảo Bình",
  pisces: "Song Ngư"
};

const SIGN_GLYPH = {
  aries: "♈",
  taurus: "♉",
  gemini: "♊",
  cancer: "♋",
  leo: "♌",
  virgo: "♍",
  libra: "♎",
  scorpio: "♏",
  sagittarius: "♐",
  capricorn: "♑",
  aquarius: "♒",
  pisces: "♓"
};

const SIGN_ELEMENT = {
  aries: "fire", leo: "fire", sagittarius: "fire",
  taurus: "earth", virgo: "earth", capricorn: "earth",
  gemini: "air", libra: "air", aquarius: "air",
  cancer: "water", scorpio: "water", pisces: "water"
};

const ELEMENT_VI = { fire: "Hỏa", earth: "Thổ", air: "Phong", water: "Thủy" };
const ELEMENT_COLOR = {
  fire: "#d65a4a",
  earth: "#9a7b4a",
  air: "#4ab0c2",
  water: "#3a6cb0"
};

const BODY_VI = {
  sun: "Mặt Trời",
  moon: "Mặt Trăng",
  mercury: "Thủy Tinh",
  venus: "Kim Tinh",
  mars: "Hỏa Tinh",
  jupiter: "Mộc Tinh",
  saturn: "Thổ Tinh",
  uranus: "Thiên Vương",
  neptune: "Hải Vương",
  pluto: "Diêm Vương"
};

const BODY_GLYPH = {
  sun: "☉",
  moon: "☽",
  mercury: "☿",
  venus: "♀",
  mars: "♂",
  jupiter: "♃",
  saturn: "♄",
  uranus: "♅",
  neptune: "♆",
  pluto: "♇"
};

const ASPECT_VI = {
  conjunction: "Hợp",
  opposition: "Đối",
  trine: "Tam hợp",
  square: "Vuông",
  sextile: "Lục hợp"
};

const ASPECT_DESC = {
  conjunction: "hai thiên thể giao điểm — năng lượng dồn về cùng vị trí",
  opposition: "hai thiên thể đối diện — căng thẳng đối lập, cần cân bằng",
  trine: "góc 120° — dòng năng lượng hài hòa, dễ chảy",
  square: "góc 90° — căng thẳng cấu trúc, đòi hỏi điều chỉnh",
  sextile: "góc 60° — cơ hội kết nối, cần chủ động"
};

const ASPECT_COLOR = {
  conjunction: "#e8c95a",
  opposition: "#d65a4a",
  trine: "#5ab07a",
  square: "#d65a4a",
  sextile: "#5ab07a"
};

const DIGNITY_VI = {
  rulership: "cai quản",
  exaltation: "vượng",
  detriment: "suy",
  fall: "hãm"
};

const sky = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const inputAt = ref("");
const inputLat = ref("");
const inputLon = ref("");
const presetMode = ref("now");

const SIZE = 360;
const CENTER = SIZE / 2;
const OUTER_R = 170;
const SIGN_R = 150;
const PLANET_R = 120;
const ASPECT_R = 90;

function lonToXY(lonDeg, radius) {
  const angle = (180 - lonDeg) * (Math.PI / 180);
  return {
    x: CENTER + radius * Math.cos(angle),
    y: CENTER - radius * Math.sin(angle)
  };
}

function signSegmentPath(signIndex) {
  const startLon = signIndex * 30;
  const endLon = startLon + 30;
  const inner = SIGN_R - 22;
  const outer = OUTER_R;
  const a = lonToXY(startLon, outer);
  const b = lonToXY(endLon, outer);
  const c = lonToXY(endLon, inner);
  const d = lonToXY(startLon, inner);
  return `M ${a.x} ${a.y} A ${outer} ${outer} 0 0 0 ${b.x} ${b.y} L ${c.x} ${c.y} A ${inner} ${inner} 0 0 1 ${d.x} ${d.y} Z`;
}

const signSegments = computed(() => {
  const signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"];
  return signs.map((sign, idx) => {
    const midLon = idx * 30 + 15;
    const labelPos = lonToXY(midLon, SIGN_R - 11);
    return {
      sign,
      path: signSegmentPath(idx),
      color: ELEMENT_COLOR[SIGN_ELEMENT[sign]],
      labelX: labelPos.x,
      labelY: labelPos.y,
      glyph: SIGN_GLYPH[sign]
    };
  });
});

function spreadPlanetPositions(bodies) {
  // Avoid label collision: if two bodies within 6°, fan them out radially.
  const sorted = [...bodies].sort((a, b) => a.ecliptic_longitude - b.ecliptic_longitude);
  const slots = sorted.map((b) => ({ body: b, radius: PLANET_R }));
  for (let i = 1; i < slots.length; i += 1) {
    const prev = slots[i - 1];
    const cur = slots[i];
    const diff = Math.abs(cur.body.ecliptic_longitude - prev.body.ecliptic_longitude);
    if (diff < 7) {
      cur.radius = prev.radius - 18;
      if (cur.radius < 70) cur.radius = PLANET_R;
    }
  }
  return slots;
}

const planetMarkers = computed(() => {
  if (!sky.value) return [];
  const slots = spreadPlanetPositions(sky.value.bodies);
  return slots.map(({ body, radius }) => {
    const pos = lonToXY(body.ecliptic_longitude, radius);
    return {
      body,
      x: pos.x,
      y: pos.y,
      glyph: BODY_GLYPH[body.name] || "•"
    };
  });
});

const aspectLines = computed(() => {
  if (!sky.value) return [];
  const byName = Object.fromEntries(sky.value.bodies.map((b) => [b.name, b]));
  return sky.value.aspects.map((a) => {
    const ba = byName[a.body_a];
    const bb = byName[a.body_b];
    if (!ba || !bb) return null;
    const pa = lonToXY(ba.ecliptic_longitude, ASPECT_R);
    const pb = lonToXY(bb.ecliptic_longitude, ASPECT_R);
    return {
      x1: pa.x,
      y1: pa.y,
      x2: pb.x,
      y2: pb.y,
      color: ASPECT_COLOR[a.aspect_type],
      type: a.aspect_type,
      bodyA: a.body_a,
      bodyB: a.body_b,
      orb: a.orb_deg
    };
  }).filter(Boolean);
});

const ascendantMarker = computed(() => {
  if (!sky.value?.ascendant) return null;
  const pos = lonToXY(sky.value.ascendant.ecliptic_longitude, OUTER_R + 8);
  return {
    x: pos.x,
    y: pos.y,
    sign: sky.value.ascendant.sign,
    degree: sky.value.ascendant.sign_degree
  };
});

async function loadSky({ at = null, lat = null, lon = null } = {}) {
  loading.value = true;
  errorMsg.value = "";
  try {
    sky.value = await getSkyNow({ at, lat, lon });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function applyCustom() {
  let atIso = null;
  if (inputAt.value) {
    const local = new Date(inputAt.value);
    if (!Number.isNaN(local.getTime())) {
      atIso = local.toISOString();
    }
  }
  const lat = inputLat.value !== "" ? Number(inputLat.value) : null;
  const lon = inputLon.value !== "" ? Number(inputLon.value) : null;
  presetMode.value = "custom";
  loadSky({ at: atIso, lat, lon });
}

function backToNow() {
  inputAt.value = "";
  inputLat.value = "";
  inputLon.value = "";
  presetMode.value = "now";
  loadSky();
}

function setPreset(name) {
  if (name === "hanoi") {
    inputLat.value = "21.0285";
    inputLon.value = "105.8542";
  } else if (name === "saigon") {
    inputLat.value = "10.7626";
    inputLon.value = "106.6602";
  } else if (name === "danang") {
    inputLat.value = "16.0544";
    inputLon.value = "108.2022";
  }
}

function fmtDeg(value) {
  return Number(value).toFixed(2);
}

function bodyLabel(name) {
  return BODY_VI[name] || name;
}

function signLabel(sign) {
  return SIGN_VI[sign] || sign;
}

onMounted(() => {
  loadSky();
});
</script>

<template>
  <section class="panel sky-panel">
    <div class="panel-title">
      <span>Bầu trời chiêm tinh phương Tây</span>
      <small>{{ sky?.ephemeris_source || "JPL DE421" }}</small>
    </div>

    <div class="sky-toolbar">
      <p>
        <b>Mô hình trạng thái bầu trời</b>
        <span>Ephemeris JPL · tropical zodiac · không diễn giải định mệnh</span>
      </p>
      <div class="sky-mode">
        <button :class="['mode-btn', presetMode === 'now' && 'active']" @click="backToNow">
          Hiện tại
        </button>
        <button :class="['mode-btn', presetMode === 'custom' && 'active']" @click="presetMode = 'custom'">
          Tùy chỉnh
        </button>
      </div>
    </div>

    <div v-if="presetMode === 'custom'" class="sky-custom-form">
      <label>
        <span>Thời điểm (giờ địa phương trình duyệt)</span>
        <input v-model="inputAt" type="datetime-local" step="60" />
      </label>
      <div class="sky-row">
        <label>
          <span>Vĩ độ</span>
          <input v-model="inputLat" type="number" step="0.0001" placeholder="vd 21.0285" />
        </label>
        <label>
          <span>Kinh độ</span>
          <input v-model="inputLon" type="number" step="0.0001" placeholder="vd 105.8542" />
        </label>
      </div>
      <div class="sky-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">Hà Nội</button>
        <button class="preset-btn" @click="setPreset('saigon')">Sài Gòn</button>
        <button class="preset-btn" @click="setPreset('danang')">Đà Nẵng</button>
        <button class="apply-btn" @click="applyCustom">Tính bầu trời</button>
      </div>
      <p class="sky-hint">
        Để xem lá số khi sinh: nhập đúng ngày giờ sinh + tọa độ nơi sinh.
      </p>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>
    <div v-if="loading && !sky" class="skeleton-block"></div>

    <template v-if="sky">
      <div class="sky-pro-grid">
        <div class="sky-chart-stage">
          <div class="chart-stage-head">
            <div>
              <span>Chart wheel</span>
              <strong>{{ signLabel(sky.sun_sign) }} Sun · {{ signLabel(sky.moon_sign) }} Moon</strong>
            </div>
            <small>{{ sky.timestamp_utc }}</small>
          </div>

          <div class="sky-wheel-wrap">
            <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="sky-wheel" role="img" aria-label="Bánh xe Hoàng đạo">
              <circle :cx="CENTER" :cy="CENTER" :r="OUTER_R" class="wheel-bg" />
              <circle :cx="CENTER" :cy="CENTER" :r="ASPECT_R" class="aspect-ring" />
              <path
                v-for="seg in signSegments"
                :key="seg.sign"
                :d="seg.path"
                :fill="seg.color"
                fill-opacity="0.16"
                stroke="rgba(255,255,255,0.18)"
                stroke-width="0.6"
              />
              <text
                v-for="seg in signSegments"
                :key="`l-${seg.sign}`"
                :x="seg.labelX"
                :y="seg.labelY"
                text-anchor="middle"
                dominant-baseline="middle"
                class="sign-label"
                :fill="seg.color"
              >
                {{ seg.glyph }}
              </text>

              <line
                v-for="(line, idx) in aspectLines"
                :key="`a-${idx}`"
                :x1="line.x1"
                :y1="line.y1"
                :x2="line.x2"
                :y2="line.y2"
                :stroke="line.color"
                stroke-width="1"
                stroke-opacity="0.52"
              >
                <title>{{ ASPECT_VI[line.type] }} · {{ bodyLabel(line.bodyA) }} – {{ bodyLabel(line.bodyB) }} · sai số {{ fmtDeg(line.orb) }}°</title>
              </line>

              <g v-for="m in planetMarkers" :key="m.body.name">
                <circle :cx="m.x" :cy="m.y" r="13" class="planet-bg" />
                <text
                  :x="m.x"
                  :y="m.y + 1"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="planet-glyph"
                >{{ m.glyph }}</text>
                <text
                  :x="m.x"
                  :y="m.y + 22"
                  text-anchor="middle"
                  class="planet-deg"
                >{{ Math.floor(m.body.sign_degree) }}°{{ m.body.is_retrograde ? " ℞" : "" }}</text>
                <title>{{ bodyLabel(m.body.name) }} · {{ signLabel(m.body.sign) }} {{ fmtDeg(m.body.sign_degree) }}°{{ m.body.is_retrograde ? " (nghịch hành)" : "" }}{{ m.body.dignity ? ` · ${DIGNITY_VI[m.body.dignity]}` : "" }}</title>
              </g>

              <g v-if="ascendantMarker">
                <line :x1="CENTER" :y1="CENTER" :x2="ascendantMarker.x" :y2="ascendantMarker.y"
                  stroke="#e8c95a" stroke-width="1.5" stroke-dasharray="4 3" />
                <text :x="ascendantMarker.x" :y="ascendantMarker.y - 4" class="asc-label" text-anchor="middle">Asc</text>
              </g>
            </svg>
          </div>

          <div class="chart-legend">
            <span><i class="fire"></i>Hỏa</span>
            <span><i class="earth"></i>Thổ</span>
            <span><i class="air"></i>Phong</span>
            <span><i class="water"></i>Thủy</span>
          </div>
        </div>

        <aside class="sky-inspector">
          <div class="sky-summary">
            <div class="summary-cell">
              <span>Mặt Trời</span>
              <strong>{{ signLabel(sky.sun_sign) }} {{ SIGN_GLYPH[sky.sun_sign] }}</strong>
            </div>
            <div class="summary-cell">
              <span>Mặt Trăng</span>
              <strong>{{ signLabel(sky.moon_sign) }} {{ SIGN_GLYPH[sky.moon_sign] }}</strong>
            </div>
            <div class="summary-cell">
              <span>Nguyên tố trội</span>
              <strong>{{ ELEMENT_VI[sky.dominant_element] }}</strong>
            </div>
            <div v-if="sky.ascendant" class="summary-cell">
              <span>Asc</span>
              <strong>{{ signLabel(sky.ascendant.sign) }} {{ fmtDeg(sky.ascendant.sign_degree) }}°</strong>
            </div>
          </div>

          <div class="planet-list">
            <div class="planet-row" v-for="b in sky.bodies" :key="b.name">
              <span class="body-glyph">{{ BODY_GLYPH[b.name] }}</span>
              <strong>{{ bodyLabel(b.name) }}</strong>
              <em>{{ SIGN_GLYPH[b.sign] }} {{ signLabel(b.sign) }}</em>
              <b>{{ fmtDeg(b.sign_degree) }}°</b>
              <small v-if="b.is_retrograde || b.dignity">
                {{ b.is_retrograde ? "℞" : "" }}
                {{ b.dignity ? DIGNITY_VI[b.dignity] : "" }}
              </small>
            </div>
          </div>
        </aside>
      </div>

      <section class="aspect-board">
        <header>
          <h4>Góc lớn</h4>
          <span>{{ sky.aspects.length }} aspect</span>
        </header>
        <p v-if="sky.aspects.length === 0" class="empty">Không có góc lớn nào trong sai số cho phép.</p>
        <ul v-else class="aspect-list">
          <li v-for="(a, idx) in sky.aspects" :key="idx" :style="{ borderTopColor: ASPECT_COLOR[a.aspect_type] }">
            <div class="aspect-head">
              <strong>{{ bodyLabel(a.body_a) }}</strong>
              <span class="aspect-type">{{ ASPECT_VI[a.aspect_type] }}</span>
              <strong>{{ bodyLabel(a.body_b) }}</strong>
            </div>
            <div class="aspect-meta">
              sai số {{ fmtDeg(a.orb_deg) }}° ·
              <span v-if="a.applying">đang siết</span>
              <span v-else>đang giãn</span>
            </div>
            <div class="aspect-desc">{{ ASPECT_DESC[a.aspect_type] }}</div>
          </li>
        </ul>
      </section>

      <p class="sky-footer">
        Thời điểm UTC: <code>{{ sky.timestamp_utc }}</code>
      </p>
    </template>
  </section>
</template>

<style scoped>
.sky-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sky-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
}

.sky-toolbar p {
  margin: 0;
  display: grid;
  gap: 3px;
  color: rgba(255, 255, 255, 0.82);
  font-size: 0.85rem;
}

.sky-toolbar p span {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.74rem;
}

.sky-mode {
  display: flex;
  gap: 6px;
  flex: 0 0 auto;
}

.mode-btn,
.preset-btn,
.apply-btn {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: background 0.15s, border 0.15s;
}

.mode-btn.active {
  background: rgba(232, 201, 90, 0.15);
  border-color: rgba(232, 201, 90, 0.5);
  color: #e8c95a;
}

.mode-btn:hover,
.preset-btn:hover,
.apply-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.apply-btn {
  background: rgba(232, 201, 90, 0.18);
  border-color: rgba(232, 201, 90, 0.5);
  color: #e8c95a;
  align-self: flex-start;
  padding: 7px 14px;
  font-weight: 600;
}

.sky-custom-form {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(240px, 1fr) auto;
  align-items: end;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.sky-custom-form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.7);
}

.sky-custom-form input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 5px;
  padding: 6px 8px;
  font-size: 0.85rem;
}

.sky-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.sky-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sky-hint {
  grid-column: 1 / -1;
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
  line-height: 1.4;
}

.sky-pro-grid {
  display: grid;
  grid-template-columns: minmax(420px, 0.95fr) minmax(360px, 1fr);
  gap: 16px;
  align-items: stretch;
}

.sky-chart-stage,
.sky-inspector,
.aspect-board {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(4, 13, 18, 0.36);
}

.sky-chart-stage {
  padding: 14px;
  background:
    radial-gradient(circle at 50% 48%, rgba(91, 229, 211, 0.08), transparent 46%),
    rgba(4, 13, 18, 0.4);
}

.chart-stage-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-stage-head div {
  display: grid;
  gap: 4px;
}

.chart-stage-head span,
.aspect-board header span {
  color: rgba(255, 255, 255, 0.46);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.55px;
  text-transform: uppercase;
}

.chart-stage-head strong {
  color: #f5e6b1;
  font-size: 1rem;
}

.chart-stage-head small {
  color: rgba(255, 255, 255, 0.42);
  font-size: 0.72rem;
  text-align: right;
}

.sky-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.summary-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 58px;
  border-radius: 8px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.035);
}

.summary-cell span {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-cell strong {
  font-size: 1rem;
  color: #f5e6b1;
}

.sky-wheel-wrap {
  display: flex;
  justify-content: center;
}

.sky-wheel {
  width: 100%;
  max-width: 440px;
  height: auto;
}

.wheel-bg {
  fill: rgba(255, 255, 255, 0.02);
  stroke: rgba(255, 255, 255, 0.08);
}

.aspect-ring {
  fill: rgba(0, 0, 0, 0.12);
  stroke: rgba(255, 255, 255, 0.06);
}

.sign-label {
  font-size: 16px;
  font-weight: 600;
}

.planet-bg {
  fill: rgba(0, 0, 0, 0.7);
  stroke: rgba(232, 201, 90, 0.5);
  stroke-width: 0.8;
}

.planet-glyph {
  fill: #f5e6b1;
  font-size: 14px;
  font-weight: 700;
}

.planet-deg {
  fill: rgba(255, 255, 255, 0.55);
  font-size: 8.5px;
}

.asc-label {
  fill: #e8c95a;
  font-size: 9px;
  font-weight: 600;
}

.body-glyph {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  color: #e8c95a;
  background: rgba(232, 201, 90, 0.08);
}

.planet-list {
  display: grid;
  padding: 8px;
}

.planet-row {
  display: grid;
  grid-template-columns: 28px minmax(92px, 1fr) minmax(112px, 1.1fr) 58px minmax(44px, auto);
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 6px 8px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.82);
}

.planet-row:nth-child(odd) {
  background: rgba(255, 255, 255, 0.025);
}

.planet-row strong,
.planet-row b {
  font-size: 0.82rem;
}

.planet-row em {
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.8rem;
  font-style: normal;
}

.planet-row b {
  color: #99f6e4;
  text-align: right;
}

.planet-row small {
  color: #f5e6b1;
  font-size: 0.72rem;
  text-align: right;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 10px;
  color: rgba(255,255,255,0.64);
  font-size: 0.75rem;
}

.chart-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.chart-legend i {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.chart-legend .fire { background: #d65a4a; }
.chart-legend .earth { background: #9a7b4a; }
.chart-legend .air { background: #4ab0c2; }
.chart-legend .water { background: #3a6cb0; }

.aspect-board {
  padding: 14px;
}

.aspect-board header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.aspect-board h4 {
  margin: 0;
  color: rgba(255,255,255,0.88);
  font-size: 0.88rem;
}

.aspect-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  max-height: 360px;
  overflow: auto;
  padding-right: 4px;
}

.aspect-list li {
  background: rgba(255, 255, 255, 0.03);
  border-top: 3px solid;
  padding: 10px;
  border-radius: 8px;
}

.aspect-head {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.9);
}

.aspect-type {
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 7px;
  border-radius: 3px;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.aspect-meta {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
  margin-top: 2px;
}

.aspect-desc {
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.65);
  margin-top: 3px;
  line-height: 1.4;
}

@media (max-width: 980px) {
  .sky-pro-grid,
  .sky-custom-form {
    grid-template-columns: 1fr;
  }

  .sky-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .sky-mode {
    width: 100%;
  }

  .mode-btn {
    flex: 1;
  }
}

@media (max-width: 560px) {
  .sky-panel {
    padding: 14px;
  }

  .chart-stage-head {
    flex-direction: column;
  }

  .chart-stage-head small {
    text-align: left;
  }

  .sky-summary {
    grid-template-columns: 1fr;
  }

  .planet-row {
    grid-template-columns: 28px minmax(0, 1fr) auto;
    gap: 8px;
  }

  .body-glyph {
    grid-row: 1 / span 2;
  }

  .planet-row strong {
    grid-column: 2;
  }

  .planet-row b {
    grid-column: 3;
    grid-row: 1;
    white-space: nowrap;
  }

  .planet-row em {
    grid-column: 2;
    grid-row: 2;
    text-align: left;
  }

  .planet-row small {
    grid-column: 3;
    grid-row: 2;
    white-space: nowrap;
  }
}

.sky-footer {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
  text-align: right;
}

.sky-footer code {
  background: rgba(255, 255, 255, 0.06);
  padding: 1px 5px;
  border-radius: 3px;
}

.empty {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.skeleton-block {
  height: 360px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  background-size: 200% 100%;
  border-radius: 8px;
  animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
