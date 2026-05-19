<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  universe: {
    type: Object,
    default: null
  },
  rulesetMeta: {
    type: Object,
    default: null
  }
});

const palaces = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
const cycleMode = ref("year");
const showFixed = ref(true);
const showMoving = ref(true);
const activeRule = ref(null);

const cycleModes = [
  { id: "year", label: "Năm", key: "year", description: "Lưu tinh dịch theo địa chi năm." },
  { id: "month", label: "Tháng", key: "month", description: "Lưu tinh dịch theo địa chi tháng." },
  { id: "day", label: "Ngày", key: "day", description: "Lưu tinh dịch theo địa chi ngày." },
  { id: "hour", label: "Giờ", key: "hour", description: "Lưu tinh dịch theo địa chi giờ." }
];

const rulebook = {
  "bac.yi.hexagram.seed": {
    id: "bac.yi.hexagram.seed",
    ruleType: "fixed",
    title: "Thiên bàn cố định",
    input: "cycle_60_idx tại thời điểm lập snapshot",
    logic: "Mỗi sao cố định nhận offset riêng, neo vào 12 cung theo modulo 12.",
    output: "Vị trí cố định tương đối của nhóm sao chủ tinh.",
    confidence: "MVP - quy tắc mô phỏng để trực quan hóa.",
    testHint: "Snapshot cùng input phải trả về cùng palaceIndex."
  },
  "bac.time.ganzhi.cycle60": {
    id: "bac.time.ganzhi.cycle60",
    ruleType: "moving",
    title: "Lưu tinh theo chu kỳ",
    input: "Địa chi của mode đang chọn (năm/tháng/ngày/giờ)",
    logic: "Lấy địa chi làm cung gốc, các sao lưu nhận offset khác nhau quanh cung gốc.",
    output: "Bộ vị trí Lưu Thái Tuế/Lưu Lộc Tồn/Lưu Kình Dương/Lưu Đà La.",
    confidence: "MVP - quy tắc cấu trúc, chuẩn bị nối engine.",
    testHint: "Đổi mode phải làm thay đổi cung gốc nhất quán theo địa chi."
  }
};

function extractBranch(label) {
  const parts = (label || "").trim().split(/\s+/);
  return parts[parts.length - 1] || "Tý";
}

const yearBranch = computed(() => {
  return extractBranch(props.universe?.ganzhi?.year);
});

const yearBranchIndex = computed(() => {
  const index = palaces.indexOf(yearBranch.value);
  return index >= 0 ? index : 0;
});

const fixedStars = computed(() => {
  const seed = props.universe?.cycle_60_idx || 0;
  const stars = [
    { name: "Tử Vi", offset: 0, ruleId: "bac.yi.hexagram.seed" },
    { name: "Thiên Phủ", offset: 3, ruleId: "bac.yi.hexagram.seed" },
    { name: "Thái Dương", offset: 6, ruleId: "bac.yi.hexagram.seed" },
    { name: "Vũ Khúc", offset: 9, ruleId: "bac.yi.hexagram.seed" }
  ];
  return stars.map((star) => ({
    ...star,
    layer: "fixed",
    palaceIndex: (seed + star.offset) % 12
  }));
});

const modeBranch = computed(() => {
  const ganzhi = props.universe?.ganzhi || {};
  const mode = cycleModes.find((item) => item.id === cycleMode.value);
  const key = mode?.key || "year";
  return extractBranch(ganzhi[key]);
});

const modeBranchIndex = computed(() => {
  const index = palaces.indexOf(modeBranch.value);
  return index >= 0 ? index : yearBranchIndex.value;
});

const movingStarsByMode = computed(() => {
  const base = modeBranchIndex.value;
  return [
    { name: "Lưu Thái Tuế", palaceIndex: base, type: "main", ruleId: "bac.time.ganzhi.cycle60", layer: "moving" },
    { name: "Lưu Lộc Tồn", palaceIndex: (base + 4) % 12, type: "support", ruleId: "bac.time.ganzhi.cycle60", layer: "moving" },
    { name: "Lưu Kình Dương", palaceIndex: (base + 1) % 12, type: "alert", ruleId: "bac.time.ganzhi.cycle60", layer: "moving" },
    { name: "Lưu Đà La", palaceIndex: (base + 11) % 12, type: "alert", ruleId: "bac.time.ganzhi.cycle60", layer: "moving" }
  ];
});

const visibleStars = computed(() => {
  const stars = [];
  if (showFixed.value) stars.push(...fixedStars.value);
  if (showMoving.value) stars.push(...movingStarsByMode.value);
  return stars;
});

function starsAt(index) {
  return visibleStars.value.filter((star) => star.palaceIndex === index);
}

function selectRule(star) {
  activeRule.value = {
    star: star.name,
    palace: palaces[star.palaceIndex],
    ...rulebook[star.ruleId]
  };
}

function tooltipText(star) {
  const rule = rulebook[star.ruleId];
  if (!rule) return star.name;
  return `${star.name} (${star.layer})\nRule: ${rule.id}\nInput: ${rule.input}\nLogic: ${rule.logic}\nOutput: ${rule.output}`;
}
</script>

<template>
  <section class="ziwei-panel" aria-label="Tử vi: thiên bàn và vận hạn">
    <header class="ziwei-header">
      <div>
        <h3>Tử Vi biểu tượng (không phải thiên văn vật lý)</h3>
        <p>Tách riêng lớp "thiên bàn cố định" và "vận hạn lưu niên" theo đúng logic lý số.</p>
      </div>
      <span class="year-pill">Năm Can Chi: {{ universe?.ganzhi?.year || "--" }}</span>
    </header>
    <p v-if="rulesetMeta" class="ruleset-note">
      Ruleset runtime: <strong>{{ rulesetMeta.ziwei_ruleset_id }}</strong> · {{ rulesetMeta.ziwei_ruleset_label }}
    </p>

    <div class="control-row">
      <div class="switches">
        <label><input v-model="showFixed" type="checkbox"> Hiện lớp cố định</label>
        <label><input v-model="showMoving" type="checkbox"> Hiện lớp lưu tinh</label>
      </div>
      <div class="mode-picker">
        <span>Chu kỳ:</span>
        <button
          v-for="mode in cycleModes"
          :key="mode.id"
          type="button"
          class="mode-btn"
          :class="{ active: cycleMode === mode.id }"
          @click="cycleMode = mode.id"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>

    <div class="mode-note">
      <span>Mode hiện tại: {{ cycleModes.find((item) => item.id === cycleMode)?.description }}</span>
      <strong>Chi gốc: {{ modeBranch }}</strong>
    </div>

    <div class="legend-row">
      <span><i class="dot fixed"></i> Thiên bàn cố định (neo theo lá số đã lập)</span>
      <span><i class="dot moving"></i> Vận hạn theo mode chu kỳ (năm/tháng/ngày/giờ)</span>
    </div>

    <div class="palace-grid">
      <article v-for="(palace, index) in palaces" :key="palace" class="palace-cell">
        <div class="palace-head">
          <strong>{{ palace }}</strong>
          <small>Cung {{ index + 1 }}</small>
        </div>
        <div class="star-stack">
          <button
            v-for="star in starsAt(index)"
            :key="`${star.layer}-${star.name}`"
            type="button"
            class="star-chip"
            :class="{
              'fixed-chip': star.layer === 'fixed',
              'moving-main': star.type === 'main',
              'moving-support': star.type === 'support',
              'moving-alert': star.type === 'alert'
            }"
            :title="tooltipText(star)"
            @click="selectRule(star)"
          >
            {{ star.name }}
          </button>
        </div>
      </article>
    </div>

    <div class="rule-card" v-if="activeRule">
      <h4>{{ activeRule.star }} · {{ activeRule.palace }}</h4>
      <p><strong>Rule ID:</strong> <code>{{ activeRule.id }}</code></p>
      <p><strong>Input:</strong> {{ activeRule.input }}</p>
      <p><strong>Logic:</strong> {{ activeRule.logic }}</p>
      <p><strong>Output:</strong> {{ activeRule.output }}</p>
      <p><strong>Mức tin cậy:</strong> {{ activeRule.confidence }}</p>
      <p><strong>Test hint:</strong> {{ activeRule.testHint }}</p>
    </div>
  </section>
</template>

<style scoped>
.ziwei-panel {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid rgba(138, 183, 194, 0.25);
  background: linear-gradient(165deg, rgba(6, 20, 28, 0.9), rgba(5, 14, 20, 0.8));
}

.ziwei-header {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: flex-start;
}

.ziwei-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #e6fbff;
}

.ziwei-header p {
  margin: 0.35rem 0 0;
  font-size: 0.82rem;
  color: #9ec5cc;
  line-height: 1.35;
}

.year-pill {
  white-space: nowrap;
  padding: 0.32rem 0.56rem;
  border-radius: 999px;
  font-size: 0.75rem;
  color: #fef3c7;
  border: 1px solid rgba(245, 158, 11, 0.35);
  background: rgba(107, 61, 0, 0.25);
}

.legend-row {
  margin-top: 0.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem 1.2rem;
  font-size: 0.76rem;
  color: #bfdde1;
}

.ruleset-note {
  margin: 0.5rem 0 0;
  font-size: 0.74rem;
  color: #9cc1c9;
}

.ruleset-note strong {
  color: #fef3c7;
}

.control-row {
  margin-top: 0.75rem;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.switches {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.switches label {
  font-size: 0.78rem;
  color: #c9e6eb;
  display: inline-flex;
  align-items: center;
  gap: 0.34rem;
}

.mode-picker {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.mode-picker span {
  font-size: 0.76rem;
  color: #9ec5cc;
}

.mode-btn {
  border: 1px solid rgba(126, 161, 173, 0.35);
  background: rgba(8, 26, 36, 0.7);
  color: #cce9ed;
  border-radius: 999px;
  font-size: 0.72rem;
  padding: 0.16rem 0.5rem;
}

.mode-btn.active {
  color: #ecfeff;
  border-color: rgba(34, 211, 238, 0.6);
  background: rgba(8, 145, 178, 0.26);
}

.mode-note {
  margin-top: 0.52rem;
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  flex-wrap: wrap;
  font-size: 0.74rem;
  color: #9cc1c9;
}

.mode-note strong {
  color: #fef3c7;
}

.dot {
  width: 0.52rem;
  height: 0.52rem;
  display: inline-block;
  border-radius: 999px;
  margin-right: 0.35rem;
}

.dot.fixed {
  background: #60a5fa;
}

.dot.moving {
  background: #f59e0b;
}

.palace-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.55rem;
}

.palace-cell {
  min-height: 6.1rem;
  padding: 0.56rem;
  border-radius: 10px;
  border: 1px solid rgba(126, 161, 173, 0.2);
  background: rgba(10, 27, 36, 0.55);
}

.palace-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.palace-head strong {
  color: #d8f5f8;
}

.palace-head small {
  color: #8eb8c0;
  font-size: 0.68rem;
}

.star-stack {
  margin-top: 0.45rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.34rem;
}

.star-chip {
  border-radius: 999px;
  padding: 0.18rem 0.46rem;
  font-size: 0.67rem;
  line-height: 1.2;
  border: 1px solid transparent;
  cursor: pointer;
}

.fixed-chip {
  color: #dbeafe;
  background: rgba(37, 99, 235, 0.28);
  border: 1px solid rgba(96, 165, 250, 0.4);
}

.moving-main {
  color: #ffedd5;
  background: rgba(234, 88, 12, 0.24);
  border: 1px solid rgba(251, 146, 60, 0.45);
}

.moving-support {
  color: #fef9c3;
  background: rgba(161, 98, 7, 0.28);
  border: 1px solid rgba(250, 204, 21, 0.42);
}

.moving-alert {
  color: #fee2e2;
  background: rgba(153, 27, 27, 0.3);
  border: 1px solid rgba(248, 113, 113, 0.45);
}

.rule-card {
  margin-top: 0.82rem;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(2, 10, 17, 0.6);
  padding: 0.68rem 0.75rem;
}

.rule-card h4 {
  margin: 0 0 0.35rem;
  color: #e2f7ff;
  font-size: 0.9rem;
}

.rule-card p {
  margin: 0.22rem 0;
  font-size: 0.75rem;
  color: #b8d6de;
}

.rule-card code {
  color: #fef08a;
}

@media (max-width: 980px) {
  .palace-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
