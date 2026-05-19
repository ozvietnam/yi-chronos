<script setup>
import { computed } from "vue";

const props = defineProps({
  universe: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const headlineMetrics = computed(() => [
  {
    label: "Kp",
    value: props.universe?.space_weather?.kp_index ?? "--",
    note: "địa từ"
  },
  {
    label: "Trăng",
    value: props.universe ? `${Math.round(props.universe.moon_phase.illumination * 100)}%` : "--",
    note: "chiếu sáng"
  },
  {
    label: "Tiết khí",
    value: props.universe?.solar_term?.name_vi || "--",
    note: props.universe?.solar_term?.solar_longitude != null
      ? `${props.universe.solar_term.solar_longitude}°`
      : "kinh độ mặt trời"
  },
  {
    label: "Giờ Can Chi",
    value: props.universe?.ganzhi?.hour || "--",
    note: "mốc hiện tại"
  }
]);

const scores = computed(() => [
  ["heaven", "Thiên"],
  ["earth", "Địa"],
  ["instability", "Độ nhiễu"]
]);

const timeRows = computed(() => [
  ["Năm", props.universe?.ganzhi?.year],
  ["Tháng", props.universe?.ganzhi?.month],
  ["Ngày", props.universe?.ganzhi?.day],
  ["Âm lịch", props.universe?.almanac?.lunar_date],
  ["Thứ / Trực", props.universe ? `${props.universe.almanac?.weekday_vi || "--"} · ${props.universe.almanac?.truc_of_day || "--"}` : null]
]);

const fortuneRows = computed(() => [
  ["Năm", props.universe?.almanac?.annual_fortune],
  ["Tháng", props.universe?.almanac?.monthly_fortune],
  ["Ngày", props.universe?.almanac?.daily_fortune],
  ["Giờ", props.universe?.almanac?.hourly_fortune]
]);
</script>

<template>
  <section class="panel weather-panel">
    <div class="panel-title">
      <span>Bảng điều khiển vũ trụ</span>
      <small>{{ universe?.algorithm_version || "mvp-0.1.0" }}</small>
    </div>
    <div v-if="loading && !universe" class="skeleton-block"></div>
    <template v-else>
      <div class="cosmic-hero">
        <span>Quẻ thời gian</span>
        <strong>{{ universe?.yi_state?.hexagram_name || "--" }}</strong>
        <small>
          {{ universe?.yi_state?.hexagram_binary || "--" }}
          <template v-if="universe?.yi_state?.transformed_hexagram_name">
            → {{ universe.yi_state.transformed_hexagram_name }}
          </template>
        </small>
      </div>

      <div class="cosmic-metrics">
        <div
          v-for="item in headlineMetrics"
          :key="item.label"
          class="cosmic-metric"
        >
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.note }}</small>
        </div>
      </div>

      <div class="energy-stack">
        <div
          v-for="item in scores"
          :key="item[0]"
          class="energy-row"
        >
          <span>{{ item[1] }}</span>
          <div class="bar"><i :style="{ width: ((universe?.scores?.[item[0]] || 0) * 100) + '%' }"></i></div>
          <b>{{ universe?.scores?.[item[0]] ?? "--" }}</b>
        </div>
      </div>

      <div class="cosmic-section">
        <h4>Can Chi / Lịch</h4>
        <dl>
          <template v-for="row in timeRows" :key="row[0]">
            <dt>{{ row[0] }}</dt>
            <dd>{{ row[1] || "--" }}</dd>
          </template>
        </dl>
      </div>

      <details class="cosmic-section compact-details">
        <summary>Vận hạn vạn niên</summary>
        <dl>
          <template v-for="row in fortuneRows" :key="row[0]">
            <dt>{{ row[0] }}</dt>
            <dd>{{ row[1] || "--" }}</dd>
          </template>
        </dl>
      </details>

      <p class="reflection">
        {{ universe?.reflection_prompt || "Đang chờ tín hiệu hiện tại." }}
      </p>
    </template>
  </section>
</template>

<style scoped>
.weather-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.cosmic-hero {
  border: 1px solid rgba(232, 201, 90, 0.26);
  border-radius: 10px;
  padding: 14px;
  background: linear-gradient(135deg, rgba(232, 201, 90, 0.1), rgba(91, 229, 211, 0.04));
}

.cosmic-hero span,
.cosmic-metric span,
.cosmic-section h4,
.cosmic-section dt {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.cosmic-hero strong {
  display: block;
  margin-top: 6px;
  color: var(--accent-gold-soft);
  font-size: 28px;
  line-height: 1;
}

.cosmic-hero small,
.cosmic-metric small {
  display: block;
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 12px;
}

.cosmic-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.cosmic-metric {
  min-height: 82px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: rgba(255,255,255,0.035);
}

.cosmic-metric strong {
  display: block;
  margin-top: 8px;
  color: var(--accent-teal-dim);
  font-size: 20px;
  line-height: 1.1;
}

.energy-stack {
  display: grid;
  gap: 10px;
}

.energy-row {
  display: grid;
  grid-template-columns: 76px 1fr 56px;
  align-items: center;
  gap: 10px;
}

.energy-row span {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.energy-row b {
  color: var(--accent-gold-soft);
  font-size: 13px;
  text-align: right;
}

.cosmic-section {
  border-top: 1px solid var(--border-soft);
  padding-top: 12px;
}

.cosmic-section h4 {
  margin: 0 0 10px;
}

.cosmic-section dl {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 8px 12px;
  margin: 0;
}

.cosmic-section dd {
  margin: 0;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 650;
  overflow-wrap: anywhere;
}

.compact-details summary {
  cursor: pointer;
  color: var(--accent-gold-soft);
  font-size: 13px;
  font-weight: 750;
}

.compact-details dl {
  margin-top: 10px;
}
</style>
