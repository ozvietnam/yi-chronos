<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { getYiDiepSequence } from "../lib/api";

const props = defineProps({
  now: { type: Date, default: null },
  selectedTimeZone: { type: String, default: "Asia/Ho_Chi_Minh" }
});

const SIGN_ELEMENT = {
  "Càn": "kim", "Đoài": "kim", "Ly": "hỏa", "Chấn": "mộc",
  "Tốn": "mộc", "Khảm": "thủy", "Cấn": "thổ", "Khôn": "thổ"
};
const ELEMENT_COLOR = {
  kim: "#c0a878", hỏa: "#d65a4a", mộc: "#5ab07a", thủy: "#3a6cb0", thổ: "#9a7b4a"
};

const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const diepCount = ref(5);
const useCustom = ref(false);
const customDateTime = ref("");
const expanded = ref(null);

function isoForBackend(dt) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
}

const currentMinute = computed(() => {
  if (!props.now) return null;
  return props.now.getMinutes();
});

const currentDiepIdx = computed(() => {
  if (!data.value || currentMinute.value === null) return null;
  if (useCustom.value) return null;
  return data.value.entries.findIndex(
    (e) => currentMinute.value >= e.minute_start && currentMinute.value <= e.minute_end
  );
});

async function load() {
  loading.value = true;
  errorMsg.value = "";
  try {
    let datetimeLocal = null;
    if (useCustom.value && customDateTime.value) {
      datetimeLocal = customDateTime.value.length === 16
        ? customDateTime.value + ":00"
        : customDateTime.value;
    } else if (props.now) {
      datetimeLocal = isoForBackend(props.now);
    }
    data.value = await getYiDiepSequence({
      datetimeLocal,
      timezone: props.selectedTimeZone,
      diepCount: Number(diepCount.value)
    });
    expanded.value = null;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

watch(() => props.selectedTimeZone, () => { if (!useCustom.value) load(); });
watch(() => useCustom.value, () => load());
watch(() => diepCount.value, () => load());
</script>

<template>
  <section class="panel diep-panel">
    <div class="panel-title">
      <span>Lá / cánh hoa — Diệp granularity</span>
      <small>{{ data?.diep_count || 5 }} diệp · {{ data?.diep_minutes || 12 }} phút mỗi diệp</small>
    </div>

    <p class="d-note">
      Trong một giờ, năng lượng quẻ không tĩnh. Mai Hoa chia giờ thành các "diệp"
      (cánh hoa) — mỗi diệp có quẻ riêng, sinh ra từ Mai Hoa Niên-Nguyệt-Nhật-Thời
      lồng thêm chỉ số diệp.
    </p>

    <div class="d-form">
      <label class="checkbox">
        <input type="checkbox" v-model="useCustom" />
        <span>Thời điểm tùy chọn</span>
      </label>
      <input v-if="useCustom" v-model="customDateTime" type="datetime-local" step="60" />
      <label class="diep-select">
        <span>Số diệp</span>
        <select v-model.number="diepCount">
          <option v-for="n in [2, 3, 4, 5, 6, 10, 12]" :key="n" :value="n">{{ n }}</option>
        </select>
      </label>
      <button class="apply-btn" @click="load" :disabled="loading">
        {{ loading ? "..." : "Vẽ lại" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="d-meta">
        <span><b>Trụ năm:</b> {{ data.base_state.year_pillar }}</span>
        <span><b>Âm lịch:</b> {{ data.base_state.lunar_date }}</span>
        <span><b>Trụ giờ:</b> {{ data.base_state.hour_pillar }}</span>
      </div>

      <ul class="diep-list">
        <li v-for="(e, idx) in data.entries" :key="e.diep_index"
          :class="{ now: currentDiepIdx === idx, expanded: expanded === idx }"
          @click="expanded = expanded === idx ? null : idx">
          <div class="diep-head">
            <span class="d-idx">Diệp {{ e.diep_index + 1 }}</span>
            <span class="d-time">phút {{ String(e.minute_start).padStart(2, '0') }}–{{ String(e.minute_end).padStart(2, '0') }}</span>
            <span class="d-trigrams">
              <b :style="{ color: ELEMENT_COLOR[SIGN_ELEMENT[e.upper_trigram]] }">{{ e.upper_trigram }}</b>
              <span class="sep">/</span>
              <b :style="{ color: ELEMENT_COLOR[SIGN_ELEMENT[e.lower_trigram]] }">{{ e.lower_trigram }}</b>
            </span>
            <span class="d-quai">{{ e.primary_name }} <small>({{ e.primary_king_wen }})</small></span>
            <span class="d-line">hào {{ e.moving_line }}</span>
          </div>

          <div v-if="expanded === idx" class="d-detail">
            <h6>5 quẻ phái sinh</h6>
            <div class="derived-grid">
              <div v-for="key in ['chanh', 'ho', 'bien', 'giao', 'phuc', 'bao']" :key="key"
                class="derived-cell">
                <span class="dk">{{ key }}</span>
                <span class="dn">
                  {{ e.derived_hexagrams[key].name_vi }}
                  <small>({{ e.derived_hexagrams[key].king_wen_index }})</small>
                </span>
                <span class="db">{{ e.derived_hexagrams[key].binary }}</span>
              </div>
            </div>
            <div class="diep-formula">
              Numbers: thượng = {{ e.upper_num }}, hạ = {{ e.lower_num }}, hào động = {{ e.moving_line }}
            </div>
          </div>
        </li>
      </ul>

      <p v-if="currentDiepIdx !== null" class="now-hint">
        Đang ở <b>Diệp {{ currentDiepIdx + 1 }}</b>
        ({{ data.entries[currentDiepIdx].primary_name }}) — phút {{ currentMinute }}.
      </p>
    </template>
  </section>
</template>

<style scoped>
.diep-panel { display: flex; flex-direction: column; gap: 12px; }
.d-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.d-form {
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
  font-size: 0.8rem;
}
.checkbox { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.8); }
.d-form input[type="datetime-local"] {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 8px; font-size: 0.82rem;
}
.diep-select {
  display: flex; align-items: center; gap: 4px; color: rgba(255,255,255,0.8);
}
.diep-select select {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 4px 6px; font-size: 0.82rem;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 6px 14px; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
}

.d-meta {
  display: flex; flex-wrap: wrap; gap: 12px;
  font-size: 0.78rem; color: rgba(255,255,255,0.85);
  background: rgba(255,255,255,0.03); padding: 8px 10px; border-radius: 6px;
}
.d-meta b { color: rgba(255,255,255,0.55); font-weight: 500; }

.diep-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}
.diep-list li {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 8px 10px; cursor: pointer;
  transition: background 0.15s, border 0.15s;
}
.diep-list li:hover { background: rgba(255,255,255,0.07); }
.diep-list li.now { border-color: rgba(232,201,90,0.6); background: rgba(232,201,90,0.06); }
.diep-list li.expanded { background: rgba(232,201,90,0.05); }

.diep-head {
  display: grid;
  grid-template-columns: 70px 100px 80px 1fr 60px;
  gap: 8px; align-items: center;
  font-size: 0.82rem; color: rgba(255,255,255,0.85);
}
.d-idx { color: #e8c95a; font-weight: 700; }
.d-time { color: rgba(255,255,255,0.55); font-family: ui-monospace, monospace; font-size: 0.74rem; }
.d-trigrams { font-weight: 600; }
.d-trigrams .sep { color: rgba(255,255,255,0.4); margin: 0 2px; }
.d-quai { font-weight: 600; }
.d-quai small { color: rgba(255,255,255,0.45); margin-left: 3px; font-weight: 400; }
.d-line { color: rgba(255,255,255,0.6); font-size: 0.74rem; }

.d-detail {
  margin-top: 8px; padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.d-detail h6 {
  margin: 0 0 6px 0; font-size: 0.74rem;
  color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.5px;
}
.derived-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 4px;
  margin-bottom: 6px;
}
.derived-cell {
  display: grid; grid-template-columns: 50px 1fr 70px;
  font-size: 0.74rem; color: rgba(255,255,255,0.85);
  background: rgba(255,255,255,0.03); padding: 3px 6px; border-radius: 3px;
}
.dk { color: rgba(255,255,255,0.5); text-transform: uppercase; font-size: 0.7rem; }
.dn small { color: rgba(255,255,255,0.45); margin-left: 3px; }
.db { font-family: ui-monospace, monospace; font-size: 0.72rem; color: rgba(255,255,255,0.55); }

.diep-formula {
  font-size: 0.72rem; color: rgba(255,255,255,0.5);
  font-style: italic;
}

.now-hint {
  font-size: 0.78rem; color: #e8c95a; margin: 0;
  text-align: center;
}
</style>
