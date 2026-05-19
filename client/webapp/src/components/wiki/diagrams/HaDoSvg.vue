<script setup>
/**
 * HaDoSvg — Hà Đồ (河圖) chính xác:
 *   55 chấm, 5 cặp sinh thành:
 *     - 1-6 Bắc (thuỷ)
 *     - 2-7 Nam (hoả)
 *     - 3-8 Đông (mộc)
 *     - 4-9 Tây (kim)
 *     - 5-10 Trung (thổ)
 *   Số trời (lẻ): trắng. Số đất (chẵn): đen.
 *
 * Sách Mai Hoa trang 17.
 */
import { computed } from "vue";

const props = defineProps({
  size: { type: Number, default: 360 },
  showLabel: { type: Boolean, default: true },
});

const cx = computed(() => props.size / 2);
const cy = computed(() => props.size / 2);

// Vị trí 5 phương + nội ngoại (sinh ở trong, thành ở ngoài)
// Bắc dưới (theo phong tục TQ: trên-Nam, dưới-Bắc)
// Nhưng phổ biến hiện đại Bắc-trên. Em dùng convention sách Mai Hoa: Nam-trên, Bắc-dưới.
const POSITIONS = computed(() => {
  const s = props.size;
  const r1 = s * 0.18;  // số sinh (gần tâm)
  const r2 = s * 0.36;  // số thành (xa tâm)
  return {
    // [x_offset, y_offset, num_inner, num_outer, hành]
    // y dương = xuống (theo SVG)
    nam:   [0,        -r2, 7, 2, "Hoả"],   // 2 sinh, 7 thành — Nam (TRÊN)
    bac:   [0,        +r2, 1, 6, "Thuỷ"],  // 1 sinh, 6 thành — Bắc (DƯỚI)
    dong:  [-r2,      0,   3, 8, "Mộc"],   // 3 sinh, 8 thành — Đông (TRÁI)
    tay:   [+r2,      0,   4, 9, "Kim"],   // 4 sinh, 9 thành — Tây (PHẢI)
    trung: [0,        0,   5, 10, "Thổ"],  // 5 sinh, 10 thành — Trung tâm
  };
});

// Render dots cho 1 số
function dotsFor(num) {
  const out = [];
  const isYang = num % 2 === 1;
  const color = isYang ? "#fef3c7" : "#1c1917";  // trắng (dương) / đen (âm)
  const stroke = isYang ? "#7c2d12" : "#1c1917";
  // Layout dots: vertical column
  for (let i = 0; i < num; i++) {
    out.push({ idx: i, color, stroke });
  }
  return out;
}

function renderDotsGroup(num, x, y, vertical = true) {
  // Render dots vertically/horizontally centered at (x, y)
  const dotR = props.size * 0.018;
  const dotGap = props.size * 0.05;
  const dots = dotsFor(num);
  const total = num;
  const halfSpan = ((total - 1) * dotGap) / 2;
  return dots.map((d, i) => {
    const off = (i * dotGap) - halfSpan;
    return {
      cx: vertical ? x : x + off,
      cy: vertical ? y + off : y,
      r: dotR,
      fill: d.color,
      stroke: d.stroke,
    };
  });
}
</script>

<template>
  <svg :width="size" :height="showLabel ? size + 50 : size"
       :viewBox="`0 0 ${size} ${showLabel ? size + 50 : size}`"
       xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect :width="size" :height="size" rx="10" fill="#fef3c7" opacity="0.4" />
    <circle :cx="cx" :cy="cy" :r="size * 0.45" fill="none" stroke="#a16207" stroke-width="0.8" opacity="0.4" />

    <!-- Compass marks (Nam-trên) -->
    <text :x="cx" :y="size * 0.06" text-anchor="middle" fill="#a16207" font-size="11" font-weight="600">南 Nam</text>
    <text :x="cx" :y="size * 0.99" text-anchor="middle" fill="#a16207" font-size="11" font-weight="600">北 Bắc</text>
    <text :x="size * 0.04" :y="cy + 4" text-anchor="start" fill="#a16207" font-size="11" font-weight="600">東 Đông</text>
    <text :x="size * 0.96" :y="cy + 4" text-anchor="end" fill="#a16207" font-size="11" font-weight="600">西 Tây</text>

    <!-- Render 5 positions: số sinh (trong) + số thành (ngoài) -->
    <template v-for="(pos, name) in POSITIONS" :key="name">
      <!-- Số sinh (gần tâm) -->
      <g>
        <circle v-for="dot in renderDotsGroup(pos[2],
                                              cx + pos[0] * 0.5,
                                              cy + pos[1] * 0.5,
                                              Math.abs(pos[0]) < 0.001)"
                :cx="dot.cx" :cy="dot.cy" :r="dot.r"
                :fill="dot.fill" :stroke="dot.stroke" stroke-width="0.8" />
      </g>
      <!-- Số thành (xa tâm) -->
      <g>
        <circle v-for="dot in renderDotsGroup(pos[3],
                                              cx + pos[0],
                                              cy + pos[1],
                                              Math.abs(pos[0]) < 0.001)"
                :cx="dot.cx" :cy="dot.cy" :r="dot.r"
                :fill="dot.fill" :stroke="dot.stroke" stroke-width="0.8" />
      </g>
      <!-- Hành label -->
      <text :x="cx + pos[0] * 1.18"
            :y="cy + pos[1] * 1.22 + 4"
            text-anchor="middle"
            fill="#7c2d12"
            font-size="9"
            font-style="italic"
            opacity="0.8">
        {{ pos[4] }} {{ pos[2] }}+{{ pos[3] }}
      </text>
    </template>

    <!-- Title -->
    <text v-if="showLabel" :x="cx" :y="size + 22" text-anchor="middle"
          fill="#7c2d12" font-size="14" font-weight="700">
      Hà Đồ 河圖
    </text>
    <text v-if="showLabel" :x="cx" :y="size + 40" text-anchor="middle"
          fill="#a16207" font-size="10" font-style="italic">
      Tổng 55 = 25 (số trời) + 30 (số đất) · 5 cặp sinh thành
    </text>
  </svg>
</template>

<style scoped>
svg { display: block; }
</style>
