<script setup>
import { computed, ref } from "vue";
import { getTransitHits } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const NATAL_POINTS_VI = {
  sun: "Mặt Trời",
  moon: "Mặt Trăng",
  mercury: "Thủy Tinh",
  venus: "Kim Tinh",
  mars: "Hỏa Tinh",
  ascendant: "Mọc (Asc)",
  midheaven: "Đỉnh (MC)"
};

const NATAL_POINTS_ORDER = ["sun", "moon", "mercury", "venus", "mars", "ascendant", "midheaven"];

const BODY_VI = {
  jupiter: "Mộc Tinh",
  saturn: "Thổ Tinh",
  uranus: "Thiên Vương",
  neptune: "Hải Vương",
  pluto: "Diêm Vương"
};

const BODY_GLYPH = {
  jupiter: "♃", saturn: "♄", uranus: "♅", neptune: "♆", pluto: "♇"
};

const BODY_COLOR = {
  jupiter: "#d68a4a",
  saturn: "#a07a5a",
  uranus: "#4ab0c2",
  neptune: "#9a7ac8",
  pluto: "#c25a78"
};

const ASPECT_VI = {
  conjunction: "hợp",
  sextile: "lục hợp",
  square: "vuông",
  trine: "tam hợp",
  opposition: "đối"
};

const ASPECT_DESC = {
  conjunction: "Hai năng lượng dồn vào cùng một điểm sống.",
  sextile: "Cơ hội kết nối — cần chủ động thì mới mở ra.",
  square: "Căng thẳng cấu trúc — đòi hỏi điều chỉnh hướng đi.",
  trine: "Dòng năng lượng dễ chảy — nhưng cũng dễ trôi qua không nhận ra.",
  opposition: "Đối lập — buộc tìm điểm cân bằng giữa hai phía."
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth, { onReady: loadHits }); // nhập 1 lần → tự vẽ; đổi profile → vẽ lại
const inputLat = ref("");
const inputLon = ref("");
const inputSpan = ref(90);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const filterImportance = ref("major");
const filterTransit = ref("all");
const filterNatal = ref("all");
const selected = ref(null);

const SVG_WIDTH = 720;
const ROW_HEIGHT = 26;
const PAD_LEFT = 100;
const PAD_RIGHT = 16;
const PAD_TOP = 20;
const PAD_BOTTOM = 28;

const visibleNatalPoints = computed(() => {
  if (!data.value) return [];
  const present = new Set(data.value.hits.map((h) => h.natal_point));
  return NATAL_POINTS_ORDER.filter((p) => present.has(p));
});

const SVG_HEIGHT = computed(() =>
  PAD_TOP + visibleNatalPoints.value.length * ROW_HEIGHT + PAD_BOTTOM
);

const innerW = computed(() => SVG_WIDTH - PAD_LEFT - PAD_RIGHT);

const ageScale = computed(() => {
  const span = data.value?.span_years || 90;
  return (age) => PAD_LEFT + (age / span) * innerW.value;
});

const yearTicks = computed(() => {
  const span = data.value?.span_years || 90;
  const ticks = [];
  for (let a = 0; a <= span; a += 10) ticks.push({ age: a, x: ageScale.value(a) });
  return ticks;
});

const filtered = computed(() => {
  if (!data.value) return [];
  return data.value.hits.filter((h) => {
    if (filterImportance.value !== "all" && h.importance !== filterImportance.value) return false;
    if (filterTransit.value !== "all" && h.transit_body !== filterTransit.value) return false;
    if (filterNatal.value !== "all" && h.natal_point !== filterNatal.value) return false;
    return true;
  });
});

const dotsByRow = computed(() => {
  const map = new Map();
  for (const p of visibleNatalPoints.value) map.set(p, []);
  for (const h of filtered.value) {
    if (!map.has(h.natal_point)) continue;
    map.get(h.natal_point).push({
      ...h,
      x: ageScale.value(h.age_years),
      color: BODY_COLOR[h.transit_body],
      r: h.importance === "major" ? 6 : h.importance === "medium" ? 4 : 2.5
    });
  }
  return map;
});

const todayMarker = computed(() => {
  if (!data.value) return null;
  const birthMs = new Date(data.value.birth_utc).getTime();
  const ageNow = (Date.now() - birthMs) / (365.25 * 86400 * 1000);
  if (ageNow < 0 || ageNow > data.value.span_years) return null;
  return { age: ageNow, x: ageScale.value(ageNow) };
});

const groupedByDecade = computed(() => {
  const m = new Map();
  for (const h of filtered.value) {
    const d = Math.floor(h.age_years / 10) * 10;
    if (!m.has(d)) m.set(d, []);
    m.get(d).push(h);
  }
  return Array.from(m.entries()).sort((a, b) => a[0] - b[0]);
});

async function loadHits() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập ngày giờ sinh";
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
    data.value = await getTransitHits({ birthAt, lat, lon, spanYears: Number(inputSpan.value) });
    selected.value = null;
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

function fmtAge(age) {
  const y = Math.floor(age);
  const m = Math.round((age - y) * 12);
  if (m === 12) return `${y + 1} tuổi`;
  if (m === 0) return `${y} tuổi`;
  return `${y}t ${m}th`;
}

function rowY(natalPoint) {
  const idx = visibleNatalPoints.value.indexOf(natalPoint);
  return PAD_TOP + idx * ROW_HEIGHT + ROW_HEIGHT / 2;
}
</script>

<template>
  <section class="panel transit-panel">
    <div class="panel-title">
      <span>Lịch quá cảnh — hành tinh chậm chạm vào lá số sinh</span>
      <small>{{ data?.ephemeris_source || "JPL DE440s" }}</small>
    </div>

    <p class="t-note">
      Mỗi điểm = một thời khắc khi Mộc/Thổ/Thiên Vương/Hải Vương/Diêm Vương tạo
      góc lớn với một điểm trong lá số sinh của anh. Đây là "thời tiết cuộc đời".
    </p>

    <div class="t-form">
      <label>
        <span>Ngày giờ sinh</span>
        <input v-model="inputBirth" type="datetime-local" step="60" />
      </label>
      <div class="t-loc">
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
        <input v-model.number="inputSpan" type="number" min="20" max="100" step="10" />
      </label>
      <div class="t-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
        <button class="preset-btn" @click="setPreset('danang')">ĐN</button>
      </div>
      <button class="apply-btn" @click="loadHits" :disabled="loading">
        {{ loading ? "Đang tính..." : "Vẽ" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="t-filters">
        <div class="filter-group">
          <span class="lbl">Tầm:</span>
          <button :class="['f-btn', filterImportance === 'major' && 'on']" @click="filterImportance = 'major'">⭐ Lớn</button>
          <button :class="['f-btn', filterImportance === 'medium' && 'on']" @click="filterImportance = 'medium'">Trung bình</button>
          <button :class="['f-btn', filterImportance === 'all' && 'on']" @click="filterImportance = 'all'">Tất cả ({{ data.hits.length }})</button>
        </div>
        <div class="filter-group">
          <span class="lbl">Hành tinh:</span>
          <button :class="['f-btn', filterTransit === 'all' && 'on']" @click="filterTransit = 'all'">Tất cả</button>
          <button v-for="(label, body) in BODY_VI" :key="body"
            :class="['f-btn', filterTransit === body && 'on']" @click="filterTransit = body"
            :style="filterTransit === body ? { borderColor: BODY_COLOR[body], color: BODY_COLOR[body] } : {}">
            {{ BODY_GLYPH[body] }} {{ label }}
          </button>
        </div>
        <div class="filter-group">
          <span class="lbl">Điểm sinh:</span>
          <button :class="['f-btn', filterNatal === 'all' && 'on']" @click="filterNatal = 'all'">Tất cả</button>
          <button v-for="p in visibleNatalPoints" :key="p"
            :class="['f-btn', filterNatal === p && 'on']" @click="filterNatal = p">
            {{ NATAL_POINTS_VI[p] }}
          </button>
        </div>
      </div>

      <div class="t-svg-wrap">
        <svg :viewBox="`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`" class="t-svg" role="img"
          aria-label="Timeline transit cuộc đời">
          <g v-for="t in yearTicks" :key="`t-${t.age}`">
            <line :x1="t.x" :y1="PAD_TOP - 4" :x2="t.x" :y2="SVG_HEIGHT - PAD_BOTTOM + 4"
              stroke="rgba(255,255,255,0.06)" stroke-width="0.6" />
            <text :x="t.x" :y="SVG_HEIGHT - 8" text-anchor="middle" class="ax-tick">{{ t.age }}</text>
          </g>

          <g v-for="(p, idx) in visibleNatalPoints" :key="`row-${p}`">
            <line :x1="PAD_LEFT" :y1="rowY(p)" :x2="SVG_WIDTH - PAD_RIGHT" :y2="rowY(p)"
              stroke="rgba(255,255,255,0.06)" stroke-width="0.6" />
            <text :x="PAD_LEFT - 8" :y="rowY(p) + 3" text-anchor="end" class="row-label">
              {{ NATAL_POINTS_VI[p] }}
            </text>
          </g>

          <g v-if="todayMarker">
            <line :x1="todayMarker.x" :y1="PAD_TOP" :x2="todayMarker.x" :y2="SVG_HEIGHT - PAD_BOTTOM"
              stroke="rgba(232,201,90,0.5)" stroke-width="1" stroke-dasharray="3 3" />
            <text :x="todayMarker.x" :y="PAD_TOP - 6" text-anchor="middle" class="today-lbl">hôm nay</text>
          </g>

          <g v-for="p in visibleNatalPoints" :key="`dots-${p}`">
            <g v-for="(d, i) in dotsByRow.get(p)" :key="`d-${p}-${i}`" class="dot-g"
              :class="{ selected: selected && selected.date_utc === d.date_utc && selected.transit_body === d.transit_body }"
              @click="selected = d">
              <circle :cx="d.x" :cy="rowY(p)" :r="d.r" :fill="d.color" stroke="#fff" stroke-opacity="0.25" />
              <title>{{ BODY_VI[d.transit_body] }} {{ ASPECT_VI[d.aspect_type] }} {{ NATAL_POINTS_VI[p] }} · {{ fmtAge(d.age_years) }} · {{ fmtDate(d.date_utc) }}</title>
            </g>
          </g>
        </svg>
      </div>

      <div v-if="selected" class="t-detail">
        <div class="d-head">
          <strong :style="{ color: BODY_COLOR[selected.transit_body] }">
            {{ BODY_GLYPH[selected.transit_body] }} {{ BODY_VI[selected.transit_body] }}
            {{ ASPECT_VI[selected.aspect_type] }}
            {{ NATAL_POINTS_VI[selected.natal_point] }} sinh
          </strong>
          <span class="d-date">{{ fmtDate(selected.date_utc) }} · {{ fmtAge(selected.age_years) }}</span>
        </div>
        <p class="d-desc">{{ ASPECT_DESC[selected.aspect_type] }}</p>
        <p class="d-meta">
          {{ BODY_VI[selected.transit_body] }} đang ở
          <b>{{ selected.transit_sign }} {{ selected.transit_degree }}°</b>.
        </p>
      </div>

      <div class="t-list">
        <details v-for="[decade, items] in groupedByDecade" :key="decade" :open="filtered.length < 30 || decade < 50">
          <summary>Tuổi {{ decade }}–{{ decade + 9 }} <span class="ct">({{ items.length }})</span></summary>
          <ul>
            <li v-for="h in items" :key="`${h.transit_body}-${h.natal_point}-${h.aspect_type}-${h.date_utc}`"
              :class="{ major: h.importance === 'major' }" @click="selected = h">
              <span class="g" :style="{ color: BODY_COLOR[h.transit_body] }">{{ BODY_GLYPH[h.transit_body] }}</span>
              <span class="age">{{ fmtAge(h.age_years) }}</span>
              <span class="dt">{{ fmtDate(h.date_utc) }}</span>
              <span class="lb">
                {{ BODY_VI[h.transit_body] }} {{ ASPECT_VI[h.aspect_type] }} {{ NATAL_POINTS_VI[h.natal_point] }}
              </span>
            </li>
          </ul>
        </details>
      </div>
    </template>

    <p v-else class="empty-hint">Chưa có dữ liệu. Nhập ngày giờ sinh + tọa độ rồi bấm "Vẽ".</p>
  </section>
</template>

<style scoped>
.transit-panel { display: flex; flex-direction: column; gap: 12px; }

.t-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}

.t-form {
  display: grid;
  grid-template-columns: 1.6fr 1.4fr 0.5fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}

.t-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }

.t-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}

.t-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }

.t-presets { display: flex; gap: 2px; }
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

.t-filters {
  display: flex; flex-direction: column; gap: 6px;
  background: rgba(255,255,255,0.02); padding: 8px; border-radius: 6px;
}

.filter-group { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }

.lbl {
  font-size: 0.72rem; color: rgba(255,255,255,0.5); width: 70px;
  text-transform: uppercase; letter-spacing: 0.4px;
}

.f-btn {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.8); padding: 3px 8px; border-radius: 4px;
  font-size: 0.74rem; cursor: pointer;
}
.f-btn.on {
  background: rgba(232,201,90,0.12);
  border-color: rgba(232,201,90,0.45); color: #e8c95a;
}

.t-svg-wrap {
  background: rgba(255,255,255,0.02); border-radius: 8px; padding: 4px;
  overflow-x: auto;
}
.t-svg { width: 100%; height: auto; min-width: 600px; }

.ax-tick { fill: rgba(255,255,255,0.5); font-size: 9px; }
.row-label { fill: rgba(255,255,255,0.75); font-size: 10px; font-weight: 500; }
.today-lbl { fill: #e8c95a; font-size: 9px; }

.dot-g { cursor: pointer; }
.dot-g:hover circle { filter: brightness(1.4); }
.dot-g.selected circle { stroke: #e8c95a; stroke-width: 2; stroke-opacity: 1; }

.t-detail {
  background: rgba(232,201,90,0.06); border: 1px solid rgba(232,201,90,0.25);
  border-radius: 6px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 3px;
}

.d-head {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: 6px; font-size: 0.86rem;
}

.d-date { font-size: 0.74rem; color: rgba(255,255,255,0.6); }
.d-desc { font-size: 0.78rem; color: rgba(255,255,255,0.85); margin: 0; }
.d-meta { font-size: 0.74rem; color: rgba(255,255,255,0.6); margin: 0; }

.t-list { display: flex; flex-direction: column; gap: 3px; }

.t-list details {
  background: rgba(255,255,255,0.03); border-radius: 5px; overflow: hidden;
}

.t-list summary {
  padding: 5px 9px; font-size: 0.78rem; color: rgba(255,255,255,0.85);
  cursor: pointer; font-weight: 600;
}

.ct { font-weight: 400; color: rgba(255,255,255,0.5); }

.t-list ul {
  list-style: none; margin: 0; padding: 0 8px 6px 8px;
  display: flex; flex-direction: column; gap: 2px;
}

.t-list li {
  display: grid;
  grid-template-columns: 24px 80px 90px 1fr;
  gap: 6px; align-items: center;
  padding: 3px 6px; font-size: 0.74rem;
  color: rgba(255,255,255,0.78); border-radius: 4px; cursor: pointer;
}
.t-list li:hover { background: rgba(255,255,255,0.05); }
.t-list li.major { background: rgba(232,201,90,0.05); }

.g { font-size: 1rem; text-align: center; }
.age { color: rgba(255,255,255,0.85); font-weight: 600; }
.dt { color: rgba(255,255,255,0.5); font-family: ui-monospace, monospace; font-size: 0.7rem; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
