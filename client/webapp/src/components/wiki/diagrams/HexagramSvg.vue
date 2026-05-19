<script setup>
/**
 * HexagramSvg — Vẽ 1 quẻ 6 vạch (Chu Dịch).
 *
 * Props:
 *   upper, lower: tên 2 quẻ 3 vạch (Càn/Khôn/...) — quẻ trên + quẻ dưới
 *   movingLine: vị trí hào động (1-6 từ dưới), -1 = không có
 *   size, showLabel, color
 */
import { computed } from "vue";

const props = defineProps({
  upper: { type: String, default: "Càn" },
  lower: { type: String, default: "Càn" },
  movingLine: { type: Number, default: -1 },
  size: { type: Number, default: 140 },
  showLabel: { type: Boolean, default: true },
  color: { type: String, default: "#7c2d12" },
  movingColor: { type: String, default: "#dc2626" },  // hào động đỏ
  bgColor: { type: String, default: "#fef3c7" },
});

const TRIGRAM_BITS = {
  "Càn": [1,1,1], "Đoài": [1,1,0], "Ly": [1,0,1], "Chấn": [1,0,0],
  "Tốn": [0,1,1], "Khảm": [0,1,0], "Cấn": [0,0,1], "Khôn": [0,0,0],
};

// All 6 lines from bottom to top: lower(bot,mid,top) + upper(bot,mid,top)
const lines = computed(() => {
  const lo = TRIGRAM_BITS[props.lower] || [0,0,0];
  const up = TRIGRAM_BITS[props.upper] || [0,0,0];
  return [lo[0], lo[1], lo[2], up[0], up[1], up[2]];
});

const LINE_W = computed(() => props.size * 0.72);
const LINE_H = computed(() => props.size * 0.05);
const GAP = computed(() => props.size * 0.035);
const cx = computed(() => props.size / 2);
const GAP_W = computed(() => LINE_W.value * 0.25);

const TOTAL_H = computed(() => 6 * LINE_H.value + 5 * GAP.value);
const TOP_PAD = computed(() => (props.size - TOTAL_H.value) / 2);

function lineY(idx) {
  // idx 0 = bottom, 5 = top. y=0 is top.
  return TOP_PAD.value + (5 - idx) * (LINE_H.value + GAP.value);
}
function isMoving(idx) {
  // movingLine: 1-6 from bottom
  return props.movingLine === idx + 1;
}
function colorFor(idx) {
  return isMoving(idx) ? props.movingColor : props.color;
}
</script>

<template>
  <svg :width="size" :height="showLabel ? size + 30 : size" :viewBox="`0 0 ${size} ${showLabel ? size + 30 : size}`"
       xmlns="http://www.w3.org/2000/svg">
    <rect :width="size" :height="size" rx="6" :fill="bgColor" opacity="0.12" />

    <!-- Divider giữa Thượng và Hạ -->
    <line :x1="cx - LINE_W/2"
          :y1="TOP_PAD + 3 * LINE_H + 2.5 * GAP"
          :x2="cx + LINE_W/2"
          :y2="TOP_PAD + 3 * LINE_H + 2.5 * GAP"
          stroke="#a16207"
          stroke-width="0.5"
          stroke-dasharray="2,3"
          opacity="0.5" />

    <template v-for="(yang, idx) in lines" :key="idx">
      <rect v-if="yang === 1"
            :x="cx - LINE_W/2"
            :y="lineY(idx)"
            :width="LINE_W"
            :height="LINE_H"
            :fill="colorFor(idx)"
            rx="1.5" />
      <template v-else>
        <rect :x="cx - LINE_W/2"
              :y="lineY(idx)"
              :width="(LINE_W - GAP_W) / 2"
              :height="LINE_H"
              :fill="colorFor(idx)"
              rx="1.5" />
        <rect :x="cx + GAP_W / 2"
              :y="lineY(idx)"
              :width="(LINE_W - GAP_W) / 2"
              :height="LINE_H"
              :fill="colorFor(idx)"
              rx="1.5" />
      </template>

      <!-- Moving line marker -->
      <circle v-if="isMoving(idx)"
              :cx="cx + LINE_W/2 + 12"
              :cy="lineY(idx) + LINE_H/2"
              r="3.5"
              :fill="movingColor" />
    </template>

    <text v-if="showLabel" :x="cx" :y="size + 20" text-anchor="middle"
          fill="#7c2d12" font-size="12" font-weight="600">
      {{ upper }} / {{ lower }}
    </text>
  </svg>
</template>

<style scoped>
svg { display: block; }
</style>
