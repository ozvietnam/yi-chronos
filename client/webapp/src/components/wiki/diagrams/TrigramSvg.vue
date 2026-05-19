<script setup>
/**
 * TrigramSvg — Vẽ 1 quẻ 3 vạch chính xác.
 *
 * Props:
 *   que: tên quẻ ("Càn", "Khôn", ...) hoặc lines [bot, mid, top] với 1=yang, 0=yin
 *   size: kích thước SVG (mặc định 120)
 *   showLabel: hiện tên quẻ phía dưới
 *   color: màu vạch (mặc định sepia)
 */
import { computed } from "vue";

const props = defineProps({
  que: { type: [String, Array], default: "Càn" },
  size: { type: Number, default: 120 },
  showLabel: { type: Boolean, default: true },
  color: { type: String, default: "#7c2d12" },
  bgColor: { type: String, default: "#fef3c7" },
});

const TRIGRAM_BITS = {
  // (bottom, middle, top) — 1=yang(solid), 0=yin(broken)
  "Càn":  [1, 1, 1],
  "Đoài": [1, 1, 0],   // thượng khuyết
  "Ly":   [1, 0, 1],   // trung hư
  "Chấn": [1, 0, 0],   // ngưỡng vu
  "Tốn":  [0, 1, 1],   // hạ đoạn
  "Khảm": [0, 1, 0],   // trung mãn
  "Cấn":  [0, 0, 1],   // phúc uyển
  "Khôn": [0, 0, 0],
};

const QUE_META = {
  "Càn":  { zh: "乾", hexa: "☰", tn: "Trời", hanh: "Kim" },
  "Khôn": { zh: "坤", hexa: "☷", tn: "Đất", hanh: "Thổ" },
  "Chấn": { zh: "震", hexa: "☳", tn: "Sấm", hanh: "Mộc" },
  "Tốn":  { zh: "巽", hexa: "☴", tn: "Gió", hanh: "Mộc" },
  "Khảm": { zh: "坎", hexa: "☵", tn: "Nước", hanh: "Thuỷ" },
  "Ly":   { zh: "離", hexa: "☲", tn: "Lửa", hanh: "Hoả" },
  "Cấn":  { zh: "艮", hexa: "☶", tn: "Núi", hanh: "Thổ" },
  "Đoài": { zh: "兌", hexa: "☱", tn: "Đầm", hanh: "Kim" },
};

const lines = computed(() => {
  if (Array.isArray(props.que)) return props.que;
  return TRIGRAM_BITS[props.que] || [0, 0, 0];
});

const meta = computed(() => QUE_META[typeof props.que === "string" ? props.que : "Càn"] || {});

// Geometry: 3 hào, render từ top xuống (hào 3 trên cùng)
const LINE_W = computed(() => props.size * 0.7);
const LINE_H = computed(() => props.size * 0.08);
const GAP = computed(() => props.size * 0.06);
const cx = computed(() => props.size / 2);

function lineY(idx) {
  // idx: 0=bottom, 1=middle, 2=top
  // y: top=highest, bottom=lowest
  const topPad = props.size * 0.1;
  return topPad + (2 - idx) * (LINE_H.value + GAP.value);
}

function lineX1(idx) {
  return cx.value - LINE_W.value / 2;
}
function lineX2(idx) {
  return cx.value + LINE_W.value / 2;
}
// For yin (broken) line — gap in middle
const GAP_W = computed(() => LINE_W.value * 0.25);
</script>

<template>
  <svg :width="size" :height="showLabel ? size + 36 : size" :viewBox="`0 0 ${size} ${showLabel ? size + 36 : size}`"
       xmlns="http://www.w3.org/2000/svg">
    <!-- Background rounded -->
    <rect :width="size" :height="size" rx="6" :fill="bgColor" opacity="0.15" />

    <!-- Render 3 lines -->
    <template v-for="(yang, idx) in lines" :key="idx">
      <!-- Yang (solid) -->
      <rect v-if="yang === 1"
            :x="lineX1(idx)"
            :y="lineY(idx)"
            :width="LINE_W"
            :height="LINE_H"
            :fill="color"
            rx="1.5" />
      <!-- Yin (broken — 2 halves) -->
      <template v-else>
        <rect :x="lineX1(idx)"
              :y="lineY(idx)"
              :width="(LINE_W - GAP_W) / 2"
              :height="LINE_H"
              :fill="color"
              rx="1.5" />
        <rect :x="cx + GAP_W / 2"
              :y="lineY(idx)"
              :width="(LINE_W - GAP_W) / 2"
              :height="LINE_H"
              :fill="color"
              rx="1.5" />
      </template>
    </template>

    <!-- Label -->
    <g v-if="showLabel" :transform="`translate(${cx}, ${size + 20})`">
      <text text-anchor="middle" fill="#7c2d12" font-size="14" font-weight="600">
        {{ que }} <tspan fill="#a16207" font-size="11">{{ meta.zh }}</tspan>
      </text>
    </g>
  </svg>
</template>

<style scoped>
svg { display: block; }
</style>
