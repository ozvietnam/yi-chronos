<script setup>
/**
 * BatQuaiVongSvg — Vòng Bát Quái (Tiên Thiên hoặc Hậu Thiên).
 *
 * Tiên Thiên (Phục Hy):
 *   Càn-Nam, Khôn-Bắc | Đoài-ĐN, Cấn-TB | Ly-Đông, Khảm-Tây | Chấn-ĐB, Tốn-TN
 *
 * Hậu Thiên (Văn Vương):
 *   Ly-Nam, Khảm-Bắc | Chấn-Đông, Đoài-Tây | Tốn-ĐN, Khôn-TN | Cấn-ĐB, Càn-TB
 *
 * Vẽ vòng tròn với 8 trigram tại 8 vị trí, taijitu (âm dương) ở giữa.
 */
import { computed } from "vue";
import TrigramSvg from "./TrigramSvg.vue";

const props = defineProps({
  type: { type: String, default: "tien-thien" },  // "tien-thien" | "hau-thien"
  size: { type: Number, default: 460 },
});

// 8 directions: angle from top (12 o'clock = 0deg, clockwise)
// SVG y dương = xuống, x dương = phải
// Mai Hoa convention: Nam-trên
const DIRECTIONS = {
  N:  { angle: 0,    label: "南 Nam" },
  NE: { angle: 45,   label: "東南 ĐN" },
  E:  { angle: 90,   label: "東 Đông" },   // wait, E sẽ là right side
  SE: { angle: 135,  label: "東北 ĐB" },
  S:  { angle: 180,  label: "北 Bắc" },
  SW: { angle: 225,  label: "西北 TB" },
  W:  { angle: 270,  label: "西 Tây" },
  NW: { angle: 315,  label: "西南 TN" },
};

// Tiên Thiên Bát Quái Đồ (Phục Hy)
const TIEN_THIEN = {
  N:  "Càn",   // Nam (TRÊN) — Càn
  NE: "Đoài",  // ĐN
  E:  "Ly",    // Đông
  SE: "Chấn",  // ĐB
  S:  "Khôn",  // Bắc (DƯỚI)
  SW: "Cấn",   // Wait... cần check
  W:  "Khảm",  // Tây
  NW: "Tốn",   // TN
};
// Cách bố trí Tiên Thiên đúng (Mai Hoa trang 33):
// Càn Nam · Khôn Bắc
// Cấn Tây Bắc · Đoài Đông Nam (núi đầm thông khí)
// Chấn Đông Bắc · Tốn Tây Nam (sấm gió xô xát)
// Khảm Tây · Ly Đông (nước lửa thân thiết)
// 8 keys: N, NE, E, SE, S, SW, W, NW
const TIEN_THIEN_CORRECT = {
  N:  "Càn",     // Nam
  NE: "Đoài",    // ĐN (Đông Nam — đầm)
  E:  "Ly",      // Đông (Ly mặt trời mọc)
  SE: "Chấn",    // ĐB (Đông Bắc — sấm)
  S:  "Khôn",    // Bắc
  SW: "Cấn",     // TB (Tây Bắc — núi)
  W:  "Khảm",    // Tây (Khảm mặt trăng)
  NW: "Tốn",     // TN (Tây Nam — gió)
};

// Hậu Thiên (Văn Vương) — Mai Hoa trang 34
// Chấn Đông, Tốn ĐN, Ly Nam, Khôn TN, Đoài Tây, Càn TB, Khảm Bắc, Cấn ĐB
const HAU_THIEN = {
  N:  "Ly",      // Nam — Ly
  NE: "Tốn",     // ĐN
  E:  "Chấn",    // Đông
  SE: "Cấn",     // ĐB
  S:  "Khảm",    // Bắc
  SW: "Càn",     // TB
  W:  "Đoài",    // Tây
  NW: "Khôn",    // TN
};

const config = computed(() => props.type === "hau-thien" ? HAU_THIEN : TIEN_THIEN_CORRECT);
const titleText = computed(() =>
  props.type === "hau-thien"
    ? "Hậu Thiên Bát Quái Đồ 後天八卦圖 (Văn Vương)"
    : "Tiên Thiên Bát Quái Đồ 先天八卦圖 (Phục Hy)"
);

const cx = computed(() => props.size / 2);
const cy = computed(() => props.size / 2);
const R = computed(() => props.size * 0.36);
const TRIGRAM_SIZE = computed(() => props.size * 0.13);

// Compute position for each direction
function dirPos(dirKey) {
  const angle = DIRECTIONS[dirKey].angle;
  // angle 0 = top (Nam), clockwise
  const rad = (angle - 90) * Math.PI / 180;
  return {
    x: cx.value + R.value * Math.cos(rad),
    y: cy.value + R.value * Math.sin(rad),
    label: DIRECTIONS[dirKey].label,
  };
}

const positions = computed(() => {
  return Object.entries(config.value).map(([dir, que]) => ({
    dir, que, ...dirPos(dir),
  }));
});
</script>

<template>
  <svg :width="size" :height="size + 40" :viewBox="`0 0 ${size} ${size + 40}`"
       xmlns="http://www.w3.org/2000/svg">
    <rect :width="size" :height="size" rx="10" fill="#fef3c7" opacity="0.35" />

    <!-- Outer circle -->
    <circle :cx="cx" :cy="cy" :r="size * 0.46" fill="none" stroke="#a16207" stroke-width="1.2" opacity="0.5" />
    <circle :cx="cx" :cy="cy" :r="size * 0.26" fill="none" stroke="#a16207" stroke-width="0.6" opacity="0.3" />

    <!-- Taijitu (âm dương) ở giữa -->
    <g :transform="`translate(${cx}, ${cy})`">
      <circle r="40" fill="#fef3c7" stroke="#7c2d12" stroke-width="1.5" />
      <path d="M 0 -40 A 40 40 0 0 1 0 40 A 20 20 0 0 1 0 0 A 20 20 0 0 0 0 -40 Z"
            fill="#1c1917" />
      <circle cx="0" cy="-20" r="5" fill="#fef3c7" />
      <circle cx="0" cy="20" r="5" fill="#1c1917" />
      <!-- Outer dots -->
      <circle cx="0" cy="-20" r="2" fill="#1c1917" opacity="0.8" />
      <circle cx="0" cy="20" r="2" fill="#fef3c7" opacity="0.8" />
    </g>

    <!-- 8 trigrams + labels -->
    <template v-for="(pos, i) in positions" :key="pos.dir">
      <!-- Direction label outer -->
      <text :x="pos.x" :y="pos.y - TRIGRAM_SIZE - 4"
            text-anchor="middle"
            fill="#a16207"
            font-size="9"
            opacity="0.7">{{ pos.label }}</text>

      <!-- Foreignobject để render TrigramSvg component -->
      <foreignObject :x="pos.x - TRIGRAM_SIZE / 2"
                     :y="pos.y - TRIGRAM_SIZE / 2"
                     :width="TRIGRAM_SIZE"
                     :height="TRIGRAM_SIZE">
        <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
          <TrigramSvg :que="pos.que" :size="TRIGRAM_SIZE * 0.85" :show-label="false" />
        </div>
      </foreignObject>

      <!-- Trigram name -->
      <text :x="pos.x" :y="pos.y + TRIGRAM_SIZE / 2 + 11"
            text-anchor="middle"
            fill="#7c2d12"
            font-size="11"
            font-weight="600">
        {{ pos.que }}
      </text>
    </template>

    <!-- Title -->
    <text :x="cx" :y="size + 28" text-anchor="middle"
          fill="#7c2d12" font-size="13" font-weight="700">
      {{ titleText }}
    </text>
  </svg>
</template>

<style scoped>
svg { display: block; }
</style>
