<script setup>
import { computed, ref } from "vue";
import { getLifeTimeline } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const BODY_VI = {
  saturn: "Thổ Tinh",
  jupiter: "Mộc Tinh",
  uranus: "Thiên Vương",
  neptune: "Hải Vương",
  pluto: "Diêm Vương"
};

const BODY_GLYPH = {
  saturn: "♄",
  jupiter: "♃",
  uranus: "♅",
  neptune: "♆",
  pluto: "♇"
};

const BODY_COLOR = {
  saturn: "#a07a5a",
  jupiter: "#d68a4a",
  uranus: "#4ab0c2",
  neptune: "#9a7ac8",
  pluto: "#c25a78"
};

const ASPECT_VI = {
  return: "hồi quy",
  square: "vuông góc",
  opposition: "đối nghịch"
};

const ASPECT_DESC = {
  return: "Hành tinh quay về chính vị trí lúc anh sinh ra. Thường cảm nhận như một chu kỳ khép — mở.",
  square: "Hành tinh tạo góc 90° với vị trí sinh — căng thẳng cấu trúc, đòi hỏi điều chỉnh hướng đi.",
  opposition: "Hành tinh đối diện vị trí sinh — căng thẳng đối lập, thường lộ ra điểm cân bằng cần xử lý."
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth, { onReady: loadTimeline }); // nhập 1 lần → tự vẽ; đổi profile → vẽ lại
const inputSpan = ref(90);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const selectedMilestone = ref(null);
const filterImportance = ref("all");

const SVG_WIDTH = 700;
const SVG_HEIGHT = 220;
const PAD_LEFT = 36;
const PAD_RIGHT = 24;
const PAD_TOP = 32;
const PAD_BOTTOM = 56;

const innerW = SVG_WIDTH - PAD_LEFT - PAD_RIGHT;
const innerH = SVG_HEIGHT - PAD_TOP - PAD_BOTTOM;
const trackY = PAD_TOP + innerH / 2;

const ageScale = computed(() => {
  const span = data.value?.span_years || inputSpan.value || 90;
  return (age) => PAD_LEFT + (age / span) * innerW;
});

const yearTicks = computed(() => {
  const span = data.value?.span_years || inputSpan.value || 90;
  const ticks = [];
  for (let a = 0; a <= span; a += 10) {
    ticks.push({ age: a, x: ageScale.value(a) });
  }
  return ticks;
});

const filteredMilestones = computed(() => {
  if (!data.value) return [];
  if (filterImportance.value === "all") return data.value.milestones;
  return data.value.milestones.filter((m) => m.importance === filterImportance.value);
});

const milestoneMarkers = computed(() =>
  filteredMilestones.value.map((m) => ({
    ...m,
    x: ageScale.value(m.age_years),
    y: trackY,
    color: BODY_COLOR[m.transit_body] || "#888",
    radius: m.importance === "major" ? 8 : m.importance === "medium" ? 5.5 : 3.5
  }))
);

const todayMarker = computed(() => {
  if (!data.value) return null;
  const birthMs = new Date(data.value.birth_utc).getTime();
  const todayMs = Date.now();
  const ageNow = (todayMs - birthMs) / (365.25 * 86400 * 1000);
  if (ageNow < 0 || ageNow > data.value.span_years) return null;
  return { age: ageNow, x: ageScale.value(ageNow) };
});

const groupedByDecade = computed(() => {
  const map = new Map();
  for (const m of filteredMilestones.value) {
    const decade = Math.floor(m.age_years / 10) * 10;
    if (!map.has(decade)) map.set(decade, []);
    map.get(decade).push(m);
  }
  return Array.from(map.entries()).sort((a, b) => a[0] - b[0]);
});

async function loadTimeline() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập ngày giờ sinh";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const local = new Date(inputBirth.value);
    if (Number.isNaN(local.getTime())) {
      throw new Error("Định dạng thời điểm sinh không hợp lệ");
    }
    const isoUtc = local.toISOString();
    data.value = await getLifeTimeline({ birthAt: isoUtc, spanYears: Number(inputSpan.value) });
    selectedMilestone.value = null;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function selectMilestone(m) {
  selectedMilestone.value = m;
}

function fmtDate(iso) {
  const d = new Date(iso);
  return new Intl.DateTimeFormat("vi-VN", { year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
}

function fmtAge(age) {
  const years = Math.floor(age);
  const months = Math.round((age - years) * 12);
  if (months === 12) return `${years + 1} tuổi`;
  if (months === 0) return `${years} tuổi`;
  return `${years} tuổi ${months} tháng`;
}
</script>

<template>
  <section class="panel timeline-panel">
    <div class="panel-title">
      <span>Bản đồ mốc lớn cuộc đời</span>
      <small>{{ data?.ephemeris_source || "JPL DE440s" }}</small>
    </div>

    <p class="timeline-note">
      Nhập ngày giờ sinh → xem các mốc thiên văn lớn (Thổ/Mộc/Thiên Vương/Hải Vương/Diêm Vương hồi quy, vuông, đối)
      trên cả đời. Đối chiếu mốc với ký ức để kiểm chứng.
    </p>

    <div class="timeline-form">
      <label>
        <span>Ngày giờ sinh (giờ địa phương trình duyệt)</span>
        <input v-model="inputBirth" type="datetime-local" step="60" />
      </label>
      <label>
        <span>Trải dài (năm)</span>
        <input v-model.number="inputSpan" type="number" min="20" max="100" step="10" />
      </label>
      <button class="apply-btn" @click="loadTimeline" :disabled="loading">
        {{ loading ? "Đang tính..." : "Vẽ timeline" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="timeline-controls">
        <span class="ctrl-label">Hiển thị:</span>
        <button :class="['filter-btn', filterImportance === 'all' && 'active']" @click="filterImportance = 'all'">
          Tất cả ({{ data.milestones.length }})
        </button>
        <button :class="['filter-btn', filterImportance === 'major' && 'active']" @click="filterImportance = 'major'">
          ⭐ Lớn nhất
        </button>
        <button :class="['filter-btn', filterImportance === 'medium' && 'active']" @click="filterImportance = 'medium'">
          Trung bình
        </button>
      </div>

      <div class="legend">
        <span v-for="(label, body) in BODY_VI" :key="body" class="legend-item">
          <span class="dot" :style="{ background: BODY_COLOR[body] }"></span>
          <span>{{ BODY_GLYPH[body] }} {{ label }}</span>
        </span>
      </div>

      <div class="timeline-svg-wrap">
        <svg :viewBox="`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`" class="timeline-svg" role="img"
          aria-label="Timeline mốc cuộc đời">
          <line :x1="PAD_LEFT" :y1="trackY" :x2="SVG_WIDTH - PAD_RIGHT" :y2="trackY" class="axis-line" />

          <g v-for="t in yearTicks" :key="`tick-${t.age}`">
            <line :x1="t.x" :y1="trackY - 4" :x2="t.x" :y2="trackY + 4" class="tick" />
            <text :x="t.x" :y="trackY + 18" text-anchor="middle" class="tick-label">{{ t.age }}</text>
          </g>

          <g v-if="todayMarker">
            <line :x1="todayMarker.x" :y1="PAD_TOP" :x2="todayMarker.x" :y2="SVG_HEIGHT - PAD_BOTTOM"
              class="today-line" />
            <text :x="todayMarker.x" :y="PAD_TOP - 8" text-anchor="middle" class="today-label">
              hôm nay · {{ Math.floor(todayMarker.age) }}t
            </text>
          </g>

          <g v-for="(m, idx) in milestoneMarkers" :key="`m-${idx}`" class="marker"
            :class="{ selected: selectedMilestone === m }" @click="selectMilestone(m)">
            <line :x1="m.x" :y1="trackY - m.radius" :x2="m.x" :y2="trackY - m.radius - 14"
              :stroke="m.color" stroke-width="0.7" stroke-opacity="0.6" />

            <template v-if="m.aspect_type === 'return'">
              <circle :cx="m.x" :cy="trackY" :r="m.radius" :fill="m.color" stroke="#fff" stroke-opacity="0.4" />
            </template>
            <template v-else-if="m.aspect_type === 'opposition'">
              <circle :cx="m.x" :cy="trackY" :r="m.radius" fill="none" :stroke="m.color" stroke-width="2" />
            </template>
            <template v-else>
              <rect :x="m.x - m.radius" :y="trackY - m.radius" :width="m.radius * 2" :height="m.radius * 2"
                :fill="m.color" stroke="#fff" stroke-opacity="0.3" />
            </template>

            <text :x="m.x" :y="trackY - m.radius - 18" text-anchor="middle" class="marker-glyph"
              :fill="m.color">{{ BODY_GLYPH[m.transit_body] }}</text>

            <title>{{ BODY_VI[m.transit_body] }} {{ ASPECT_VI[m.aspect_type] }} · {{ fmtAge(m.age_years) }} · {{ fmtDate(m.date_utc) }}</title>
          </g>
        </svg>
      </div>

      <div v-if="selectedMilestone" class="selected-detail">
        <div class="detail-head">
          <strong :style="{ color: BODY_COLOR[selectedMilestone.transit_body] }">
            {{ BODY_GLYPH[selectedMilestone.transit_body] }} {{ BODY_VI[selectedMilestone.transit_body] }}
            {{ ASPECT_VI[selectedMilestone.aspect_type] }}
          </strong>
          <span class="detail-date">{{ fmtDate(selectedMilestone.date_utc) }} · {{ fmtAge(selectedMilestone.age_years) }}</span>
        </div>
        <p class="detail-desc">{{ ASPECT_DESC[selectedMilestone.aspect_type] }}</p>
        <p class="detail-meta">
          {{ BODY_VI[selectedMilestone.transit_body] }} đang ở
          <b>{{ selectedMilestone.transit_sign }} {{ selectedMilestone.transit_degree }}°</b>
          khi sự kiện xảy ra.
        </p>
      </div>

      <div class="decade-list">
        <details v-for="[decade, items] in groupedByDecade" :key="decade" :open="decade < 50">
          <summary>
            Tuổi {{ decade }}–{{ decade + 9 }} <span class="count">({{ items.length }})</span>
          </summary>
          <ul>
            <li v-for="m in items" :key="`${m.transit_body}-${m.aspect_type}-${m.date_utc}`"
              :class="{ major: m.importance === 'major' }"
              @click="selectMilestone({ ...m, x: ageScale(m.age_years), y: trackY, color: BODY_COLOR[m.transit_body] })">
              <span class="li-glyph" :style="{ color: BODY_COLOR[m.transit_body] }">
                {{ BODY_GLYPH[m.transit_body] }}
              </span>
              <span class="li-age">{{ fmtAge(m.age_years) }}</span>
              <span class="li-date">{{ fmtDate(m.date_utc) }}</span>
              <span class="li-label">{{ m.label_vi }}</span>
            </li>
          </ul>
        </details>
      </div>
    </template>

    <p v-else class="empty-hint">
      Chưa có timeline. Nhập ngày giờ sinh và bấm "Vẽ timeline".
    </p>
  </section>
</template>

<style scoped>
.timeline-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.timeline-note {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.7);
  border-left: 2px solid rgba(232, 201, 90, 0.5);
  padding-left: 10px;
  line-height: 1.5;
  margin: 0;
}

.timeline-form {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 8px;
  align-items: end;
  background: rgba(255, 255, 255, 0.03);
  padding: 10px;
  border-radius: 8px;
}

.timeline-form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.7);
}

.timeline-form input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 5px;
  padding: 6px 8px;
  font-size: 0.85rem;
}

.apply-btn {
  background: rgba(232, 201, 90, 0.18);
  border: 1px solid rgba(232, 201, 90, 0.5);
  color: #e8c95a;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.apply-btn:hover:not(:disabled) {
  background: rgba(232, 201, 90, 0.28);
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.timeline-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ctrl-label {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
}

.filter-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.8);
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 0.78rem;
  cursor: pointer;
}

.filter-btn.active {
  background: rgba(232, 201, 90, 0.15);
  border-color: rgba(232, 201, 90, 0.5);
  color: #e8c95a;
}

.legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.timeline-svg-wrap {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  padding: 6px;
  overflow-x: auto;
}

.timeline-svg {
  width: 100%;
  height: auto;
  min-width: 600px;
}

.axis-line {
  stroke: rgba(255, 255, 255, 0.25);
  stroke-width: 1;
}

.tick {
  stroke: rgba(255, 255, 255, 0.35);
  stroke-width: 1;
}

.tick-label {
  fill: rgba(255, 255, 255, 0.5);
  font-size: 10px;
}

.today-line {
  stroke: rgba(232, 201, 90, 0.5);
  stroke-width: 1;
  stroke-dasharray: 3 3;
}

.today-label {
  fill: #e8c95a;
  font-size: 10px;
  font-weight: 600;
}

.marker {
  cursor: pointer;
}

.marker:hover circle,
.marker:hover rect {
  filter: brightness(1.3);
}

.marker.selected circle,
.marker.selected rect {
  filter: drop-shadow(0 0 4px currentColor);
}

.marker-glyph {
  font-size: 11px;
  pointer-events: none;
}

.selected-detail {
  background: rgba(232, 201, 90, 0.06);
  border: 1px solid rgba(232, 201, 90, 0.25);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 0.92rem;
}

.detail-date {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.6);
}

.detail-desc {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  line-height: 1.5;
}

.detail-meta {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.decade-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.decade-list details {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 5px;
  overflow: hidden;
}

.decade-list summary {
  padding: 6px 10px;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  font-weight: 600;
}

.decade-list summary .count {
  font-weight: 400;
  color: rgba(255, 255, 255, 0.5);
}

.decade-list ul {
  list-style: none;
  margin: 0;
  padding: 0 10px 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.decade-list li {
  display: grid;
  grid-template-columns: 24px 110px 100px 1fr;
  gap: 6px;
  align-items: center;
  padding: 4px 6px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.78);
  border-radius: 4px;
  cursor: pointer;
}

.decade-list li:hover {
  background: rgba(255, 255, 255, 0.05);
}

.decade-list li.major {
  background: rgba(232, 201, 90, 0.06);
}

.li-glyph {
  font-size: 1rem;
  text-align: center;
}

.li-age {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
}

.li-date {
  color: rgba(255, 255, 255, 0.5);
  font-family: ui-monospace, monospace;
  font-size: 0.72rem;
}

.li-label {
  color: rgba(255, 255, 255, 0.7);
}

.empty-hint {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
  padding: 30px 0;
  margin: 0;
}
</style>
