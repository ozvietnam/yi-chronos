<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { getYiNarrative } from "../lib/api";

const props = defineProps({
  now: { type: Date, default: null },
  selectedTimeZone: { type: String, default: "Asia/Ho_Chi_Minh" }
});

const ROLE_COLOR = {
  chanh: "#e8c95a",  // Gold — surface
  ho:    "#7a5ab0",  // Violet — hidden
  bien:  "#5ab07a",  // Green — direction
  giao:  "#c25a78",  // Crimson — opposing
  phuc:  "#4ab0c2",  // Cyan — reverse view
  bao:   "#9a7b4a"   // Earth — frame
};

const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const customDateTime = ref("");
const useCustom = ref(false);

function isoForBackend(dt) {
  // Format as "YYYY-MM-DDTHH:MM:SS" in local TZ (no offset suffix).
  const pad = (n) => String(n).padStart(2, "0");
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
}

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
    data.value = await getYiNarrative({
      datetimeLocal,
      timezone: props.selectedTimeZone
    });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

watch(() => props.selectedTimeZone, () => { if (!useCustom.value) load(); });
watch(() => useCustom.value, () => load());
</script>

<template>
  <section class="panel narrative-panel">
    <div class="panel-title">
      <span>Kịch bản 6 quẻ — Timeline narrative</span>
      <small>{{ data?.method_id || "mai_hoa_nntt_v1" }}</small>
    </div>

    <p class="n-note">
      Mai Hoa Niên-Nguyệt-Nhật-Thời sinh quẻ Chánh, từ đó suy ra 5 quẻ phái sinh
      (Hỗ, Biến, Giao, Phục, Bao). Mỗi quẻ giữ một vai trò khác nhau trong câu chuyện
      của khoảnh khắc này.
    </p>

    <div class="n-form">
      <label class="checkbox">
        <input type="checkbox" v-model="useCustom" />
        <span>Nhập thời điểm khác (mặc định: hiện tại)</span>
      </label>
      <input v-if="useCustom" v-model="customDateTime" type="datetime-local" step="60" />
      <button class="apply-btn" @click="load" :disabled="loading">
        {{ loading ? "Đang tính..." : "Vẽ lại" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="n-meta">
        <span><b>Thời điểm:</b> {{ data.local_datetime?.replace("T", " ").slice(0, 16) || "—" }}</span>
        <span><b>Can-Chi:</b> {{ data.ganzhi.year }} · {{ data.ganzhi.day }} · {{ data.ganzhi.hour }}</span>
        <span><b>Âm lịch:</b> {{ data.lunar_date }}</span>
      </div>

      <div class="derivation-line">
        Niên({{ data.derivation.year_branch_idx }}) +
        Nguyệt({{ data.derivation.lunar_month }}) +
        Nhật({{ data.derivation.lunar_day }}) +
        Thời({{ data.derivation.hour_branch_idx }})
        →
        thượng <b>{{ data.derivation.upper_trigram }}</b> ({{ data.derivation.upper_num }}),
        hạ <b>{{ data.derivation.lower_trigram }}</b> ({{ data.derivation.lower_num }}),
        hào động <b>{{ data.derivation.moving_line }}</b>
      </div>

      <ol class="segments">
        <li v-for="(s, idx) in data.segments" :key="s.role_key"
          :style="{ borderLeftColor: ROLE_COLOR[s.role_key] }">
          <div class="seg-head">
            <span class="seg-step">{{ idx + 1 }}</span>
            <span class="seg-role" :style="{ color: ROLE_COLOR[s.role_key] }">{{ s.role_label }}</span>
            <span class="seg-name">
              {{ s.hexagram_name }}
              <small>(quẻ {{ s.hexagram_king_wen }} · {{ s.hexagram_binary }})</small>
            </span>
          </div>
          <div class="seg-desc">{{ s.role_description }}</div>
          <div class="seg-state">{{ s.state_phrase }}</div>
        </li>
      </ol>

      <div class="composed-block">
        <h5>Câu chuyện kết nối</h5>
        <p>{{ data.composed_text }}</p>
      </div>

      <p class="footer-ref">Nguồn: {{ data.source_ref }}</p>
    </template>
  </section>
</template>

<style scoped>
.narrative-panel { display: flex; flex-direction: column; gap: 12px; }
.n-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.n-form {
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
  font-size: 0.8rem;
}
.checkbox { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.8); }
.n-form input[type="datetime-local"] {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 8px; font-size: 0.82rem;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 6px 14px; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
}
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.n-meta {
  display: flex; flex-wrap: wrap; gap: 12px;
  font-size: 0.78rem; color: rgba(255,255,255,0.85);
  background: rgba(255,255,255,0.03); padding: 8px 10px; border-radius: 6px;
}
.n-meta b { color: rgba(255,255,255,0.55); font-weight: 500; }

.derivation-line {
  font-size: 0.78rem; color: rgba(255,255,255,0.7);
  background: rgba(232,201,90,0.05); border: 1px dashed rgba(232,201,90,0.25);
  border-radius: 6px; padding: 8px 10px; line-height: 1.5;
}
.derivation-line b { color: #f5e6b1; }

.segments {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 6px;
  counter-reset: seg;
}
.segments li {
  background: rgba(255,255,255,0.03);
  border-left: 3px solid;
  border-radius: 0 6px 6px 0;
  padding: 8px 12px;
}
.seg-head {
  display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
}
.seg-step {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.7); font-size: 0.74rem; font-weight: 700;
}
.seg-role {
  font-weight: 600; font-size: 0.82rem;
  text-transform: uppercase; letter-spacing: 0.4px;
}
.seg-name {
  color: rgba(255,255,255,0.95); font-size: 0.92rem; font-weight: 600;
}
.seg-name small { color: rgba(255,255,255,0.45); font-weight: 400; margin-left: 4px; }

.seg-desc {
  font-size: 0.76rem; color: rgba(255,255,255,0.6);
  margin-top: 3px; line-height: 1.4;
}
.seg-state {
  font-size: 0.84rem; color: #f5e6b1; margin-top: 4px;
  font-style: italic;
}

.composed-block {
  background: rgba(232,201,90,0.06); border: 1px solid rgba(232,201,90,0.25);
  border-radius: 8px; padding: 10px 12px;
}
.composed-block h5 {
  margin: 0 0 6px 0; font-size: 0.78rem;
  color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px;
}
.composed-block p {
  margin: 0; font-size: 0.86rem; color: rgba(255,255,255,0.92);
  line-height: 1.6;
}

.footer-ref {
  font-size: 0.7rem; color: rgba(255,255,255,0.4);
  margin: 0; text-align: right;
}
</style>
