<script setup>
import { computed, ref } from "vue";
import { getSolarArcHits } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const BODY_VI = {
  sun: "Mặt Trời", moon: "Mặt Trăng", mercury: "Thủy", venus: "Kim", mars: "Hỏa",
  jupiter: "Mộc", saturn: "Thổ", uranus: "Thiên Vương", neptune: "Hải Vương", pluto: "Diêm Vương",
  ascendant: "Mọc", midheaven: "Đỉnh"
};
const BODY_GLYPH = {
  sun: "☉", moon: "☽", mercury: "☿", venus: "♀", mars: "♂",
  jupiter: "♃", saturn: "♄", uranus: "♅", neptune: "♆", pluto: "♇",
  ascendant: "Asc", midheaven: "MC"
};
const ASPECT_VI = {
  conjunction: "hợp", sextile: "lục hợp", square: "vuông", trine: "tam hợp", opposition: "đối"
};
const ASPECT_DESC = {
  conjunction: "Năng lượng directed dồn vào điểm sinh — thường là 'một điều mới đến'.",
  sextile: "Cơ hội mở ra — phải chủ động.",
  square: "Căng thẳng cấu trúc — đòi hỏi điều chỉnh.",
  trine: "Dòng chảy thuận — dễ xảy ra mà ít cảm thấy.",
  opposition: "Đối lập — buộc cân bằng hai phía của đời mình."
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth, { onReady: load }); // nhập 1 lần → tự vẽ; đổi profile → vẽ lại
const inputLat = ref("");
const inputLon = ref("");
const inputSpan = ref(90);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const filterImportance = ref("major");
const selected = ref(null);

const filtered = computed(() => {
  if (!data.value) return [];
  if (filterImportance.value === "all") return data.value.hits;
  return data.value.hits.filter((h) => h.importance === filterImportance.value);
});

const todayAge = computed(() => {
  if (!data.value) return null;
  const birthMs = new Date(data.value.birth_utc).getTime();
  return (Date.now() - birthMs) / (365.25 * 86400 * 1000);
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
    data.value = await getSolarArcHits({ birthAt, lat, lon, spanYears: Number(inputSpan.value) });
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
</script>

<template>
  <section class="panel sa-panel">
    <div class="panel-title">
      <span>Solar Arc Directions — Mốc biểu tượng theo ~1°/năm</span>
      <small>kỹ thuật cổ điển</small>
    </div>

    <p class="sa-note">
      Mỗi điểm trong lá số sinh tiến đều đặn ~1°/năm theo Mặt Trời tiến triển.
      Khi điểm tiến chạm vào điểm sinh khác, đó là <b>mốc biểu tượng</b> — thường
      đi kèm sự kiện cụ thể.
    </p>

    <div class="sa-form">
      <label><span>Ngày giờ sinh</span><input v-model="inputBirth" type="datetime-local" step="60" /></label>
      <div class="sa-loc">
        <label><span>Vĩ độ</span><input v-model="inputLat" type="number" step="0.0001" /></label>
        <label><span>Kinh độ</span><input v-model="inputLon" type="number" step="0.0001" /></label>
      </div>
      <label><span>Năm</span><input v-model.number="inputSpan" type="number" min="20" max="100" step="10" /></label>
      <div class="sa-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
      </div>
      <button class="apply-btn" @click="load" :disabled="loading">{{ loading ? "..." : "Vẽ" }}</button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="sa-filters">
        <button :class="['f-btn', filterImportance === 'major' && 'on']" @click="filterImportance = 'major'">⭐ Lớn</button>
        <button :class="['f-btn', filterImportance === 'medium' && 'on']" @click="filterImportance = 'medium'">Trung bình</button>
        <button :class="['f-btn', filterImportance === 'all' && 'on']" @click="filterImportance = 'all'">Tất cả ({{ data.hits.length }})</button>
      </div>

      <div v-if="selected" class="sa-detail">
        <div class="d-head">
          <strong>
            Arc {{ BODY_VI[selected.directed_body] }} {{ ASPECT_VI[selected.aspect_type] }}
            natal {{ BODY_VI[selected.natal_target] }}
          </strong>
          <span class="d-date">{{ fmtDate(selected.date_utc) }} · {{ fmtAge(selected.age_years) }}</span>
        </div>
        <p class="d-desc">{{ ASPECT_DESC[selected.aspect_type] }}</p>
        <p class="d-meta">Arc value: <b>{{ selected.arc_value_deg.toFixed(2) }}°</b></p>
      </div>

      <div class="decade-list">
        <details v-for="[decade, items] in groupedByDecade" :key="decade"
          :open="todayAge !== null && Math.abs(decade - Math.floor(todayAge / 10) * 10) < 20">
          <summary>Tuổi {{ decade }}–{{ decade + 9 }} <span class="ct">({{ items.length }})</span></summary>
          <ul>
            <li v-for="h in items" :key="`${h.directed_body}-${h.natal_target}-${h.aspect_type}`"
              :class="{ major: h.importance === 'major' }" @click="selected = h">
              <span class="age">{{ fmtAge(h.age_years) }}</span>
              <span class="dt">{{ fmtDate(h.date_utc) }}</span>
              <span class="lb">
                <b>{{ BODY_GLYPH[h.directed_body] }}</b> {{ BODY_VI[h.directed_body] }}
                {{ ASPECT_VI[h.aspect_type] }}
                <b>{{ BODY_GLYPH[h.natal_target] }}</b> {{ BODY_VI[h.natal_target] }}
              </span>
            </li>
          </ul>
        </details>
      </div>
    </template>

    <p v-else class="empty-hint">Nhập ngày giờ sinh + tọa độ để vẽ.</p>
  </section>
</template>

<style scoped>
.sa-panel { display: flex; flex-direction: column; gap: 12px; }
.sa-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.sa-form {
  display: grid; grid-template-columns: 1.6fr 1.2fr 0.5fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.sa-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }
.sa-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}
.sa-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.sa-presets { display: flex; gap: 2px; }
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

.sa-filters { display: flex; gap: 4px; flex-wrap: wrap; }
.f-btn {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.8); padding: 4px 10px; border-radius: 5px;
  font-size: 0.78rem; cursor: pointer;
}
.f-btn.on {
  background: rgba(232,201,90,0.15); border-color: rgba(232,201,90,0.5); color: #e8c95a;
}

.sa-detail {
  background: rgba(232,201,90,0.06); border: 1px solid rgba(232,201,90,0.25);
  border-radius: 6px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 3px;
}
.d-head {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: 6px; font-size: 0.86rem;
}
.d-date { font-size: 0.74rem; color: rgba(255,255,255,0.6); }
.d-desc { font-size: 0.78rem; color: rgba(255,255,255,0.85); margin: 0; line-height: 1.4; }
.d-meta { font-size: 0.74rem; color: rgba(255,255,255,0.6); margin: 0; }

.decade-list { display: flex; flex-direction: column; gap: 3px; }
.decade-list details {
  background: rgba(255,255,255,0.03); border-radius: 5px; overflow: hidden;
}
.decade-list summary {
  padding: 5px 9px; font-size: 0.78rem; color: rgba(255,255,255,0.85);
  cursor: pointer; font-weight: 600;
}
.ct { font-weight: 400; color: rgba(255,255,255,0.5); }

.decade-list ul {
  list-style: none; margin: 0; padding: 0 8px 6px 8px;
  display: flex; flex-direction: column; gap: 2px;
}
.decade-list li {
  display: grid; grid-template-columns: 80px 90px 1fr;
  gap: 8px; align-items: center;
  padding: 3px 6px; font-size: 0.74rem;
  color: rgba(255,255,255,0.78); border-radius: 4px; cursor: pointer;
}
.decade-list li:hover { background: rgba(255,255,255,0.05); }
.decade-list li.major { background: rgba(232,201,90,0.05); }
.age { color: rgba(255,255,255,0.85); font-weight: 600; }
.dt { color: rgba(255,255,255,0.5); font-family: ui-monospace, monospace; font-size: 0.7rem; }
.lb b { color: #e8c95a; font-weight: 600; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
