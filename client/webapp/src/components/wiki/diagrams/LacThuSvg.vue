<script setup>
/**
 * LacThuSvg — Lạc Thư (洛書) chính xác:
 *   9 ô vuông, tổng 45.
 *   Vị trí 9 ô tượng con rùa:
 *     - 9 đầu (Nam) | 1 chân (Bắc)
 *     - 3 trái mu (Đông) | 7 phải mu (Tây)
 *     - 4 vai trái (ĐN) | 2 vai phải (TN)
 *     - 8 chân trái (ĐB) | 6 chân phải (TB)
 *     - 5 giữa (Thái Cực)
 *   Đây là "magic square" 3x3 — mọi hàng/cột/chéo = 15.
 *
 * Sách Mai Hoa trang 20.
 */
import { computed } from "vue";

const props = defineProps({
  size: { type: Number, default: 360 },
  showLabel: { type: Boolean, default: true },
});

const cx = computed(() => props.size / 2);
const cy = computed(() => props.size / 2);

// Magic square 3x3 (Lo Shu)
// Cách bố trí chuẩn (Nam-trên, Bắc-dưới):
//   4 | 9 | 2     <- Nam (trên)
//   3 | 5 | 7
//   8 | 1 | 6     <- Bắc (dưới)
// Mỗi hàng/cột/chéo cộng = 15

const SQUARES = computed(() => {
  const s = props.size;
  const cellSize = s * 0.18;
  const gap = s * 0.04;
  const startX = cx.value - (cellSize * 1.5 + gap);
  const startY = cy.value - (cellSize * 1.5 + gap);
  return [
    // [num, col, row, hint]
    [4, 0, 0, "ĐN vai trái"],
    [9, 1, 0, "Nam đầu"],
    [2, 2, 0, "TN vai phải"],
    [3, 0, 1, "Đông trái mu"],
    [5, 1, 1, "Trung — Thái Cực"],
    [7, 2, 1, "Tây phải mu"],
    [8, 0, 2, "ĐB chân trái"],
    [1, 1, 2, "Bắc chân"],
    [6, 2, 2, "TB chân phải"],
  ].map(([num, col, row, hint]) => ({
    num, hint,
    x: startX + col * (cellSize + gap) + cellSize / 2,
    y: startY + row * (cellSize + gap) + cellSize / 2,
    cellSize,
  }));
});

function dotsFor(num) {
  const isYang = num % 2 === 1;
  return {
    color: isYang ? "#fef3c7" : "#1c1917",
    stroke: isYang ? "#7c2d12" : "#1c1917",
    label: isYang ? `${num} (lẻ-dương)` : `${num} (chẵn-âm)`,
  };
}

function dotsLayout(num, x, y, cellSize) {
  // Bố trí num chấm vào ô hình vuông
  const r = cellSize * 0.06;
  const out = [];
  // Layout đặc biệt cho số nhỏ
  if (num === 1) {
    out.push({ cx: x, cy: y });
  } else if (num === 2) {
    out.push({ cx: x, cy: y - r * 2 });
    out.push({ cx: x, cy: y + r * 2 });
  } else if (num === 3) {
    out.push({ cx: x - r * 2.5, cy: y - r * 2.5 });
    out.push({ cx: x, cy: y });
    out.push({ cx: x + r * 2.5, cy: y + r * 2.5 });
  } else if (num === 4) {
    out.push({ cx: x - r * 2, cy: y - r * 2 });
    out.push({ cx: x + r * 2, cy: y - r * 2 });
    out.push({ cx: x - r * 2, cy: y + r * 2 });
    out.push({ cx: x + r * 2, cy: y + r * 2 });
  } else if (num === 5) {
    out.push({ cx: x - r * 2.5, cy: y - r * 2.5 });
    out.push({ cx: x + r * 2.5, cy: y - r * 2.5 });
    out.push({ cx: x, cy: y });
    out.push({ cx: x - r * 2.5, cy: y + r * 2.5 });
    out.push({ cx: x + r * 2.5, cy: y + r * 2.5 });
  } else if (num === 6) {
    for (let i = 0; i < 3; i++)
      for (let j = 0; j < 2; j++)
        out.push({ cx: x + (j - 0.5) * r * 4, cy: y + (i - 1) * r * 3 });
  } else if (num === 7) {
    for (let i = 0; i < 3; i++) {
      out.push({ cx: x - r * 2.5, cy: y + (i - 1) * r * 2.5 });
      out.push({ cx: x + r * 2.5, cy: y + (i - 1) * r * 2.5 });
    }
    out.push({ cx: x, cy: y });
  } else if (num === 8) {
    for (let i = 0; i < 4; i++)
      for (let j = 0; j < 2; j++)
        out.push({ cx: x + (j - 0.5) * r * 4, cy: y + (i - 1.5) * r * 2.5 });
  } else if (num === 9) {
    for (let i = 0; i < 3; i++)
      for (let j = 0; j < 3; j++)
        out.push({ cx: x + (j - 1) * r * 3, cy: y + (i - 1) * r * 3 });
  }
  return out;
}
</script>

<template>
  <svg :width="size" :height="showLabel ? size + 50 : size"
       :viewBox="`0 0 ${size} ${showLabel ? size + 50 : size}`"
       xmlns="http://www.w3.org/2000/svg">
    <rect :width="size" :height="size" rx="10" fill="#fef3c7" opacity="0.4" />

    <!-- Compass -->
    <text :x="cx" :y="size * 0.06" text-anchor="middle" fill="#a16207" font-size="11" font-weight="600">南 Nam</text>
    <text :x="cx" :y="size * 0.99" text-anchor="middle" fill="#a16207" font-size="11" font-weight="600">北 Bắc</text>
    <text :x="size * 0.04" :y="cy + 4" text-anchor="start" fill="#a16207" font-size="11" font-weight="600">東 Đông</text>
    <text :x="size * 0.96" :y="cy + 4" text-anchor="end" fill="#a16207" font-size="11" font-weight="600">西 Tây</text>

    <!-- 9 ô + chấm bên trong -->
    <template v-for="sq in SQUARES" :key="sq.num">
      <rect :x="sq.x - sq.cellSize/2"
            :y="sq.y - sq.cellSize/2"
            :width="sq.cellSize"
            :height="sq.cellSize"
            fill="rgba(255,255,255,0.4)"
            stroke="#a16207"
            stroke-width="1"
            rx="2" />
      <!-- Dots -->
      <circle v-for="(d, i) in dotsLayout(sq.num, sq.x, sq.y, sq.cellSize)"
              :key="i"
              :cx="d.cx" :cy="d.cy"
              :r="sq.cellSize * 0.06"
              :fill="dotsFor(sq.num).color"
              :stroke="dotsFor(sq.num).stroke"
              stroke-width="0.8" />
      <!-- Number label corner -->
      <text :x="sq.x - sq.cellSize/2 + 4"
            :y="sq.y - sq.cellSize/2 + 12"
            fill="#7c2d12"
            font-size="9"
            font-weight="600"
            opacity="0.7">{{ sq.num }}</text>
    </template>

    <text v-if="showLabel" :x="cx" :y="size + 22" text-anchor="middle"
          fill="#7c2d12" font-size="14" font-weight="700">
      Lạc Thư 洛書
    </text>
    <text v-if="showLabel" :x="cx" :y="size + 40" text-anchor="middle"
          fill="#a16207" font-size="10" font-style="italic">
      Tổng 45 · Magic Square 3×3 (mọi hàng/cột/chéo = 15) · 5 ở giữa = Thái Cực
    </text>
  </svg>
</template>

<style scoped>
svg { display: block; }
</style>
