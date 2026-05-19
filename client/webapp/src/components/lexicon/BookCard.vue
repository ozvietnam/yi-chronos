<script setup>
import { computed } from "vue";
import { TIER_LABEL, STATUS_LABEL, SCHOOL_LABEL, RESTORE_METHOD_LABEL } from "../../composables/useLexicon.js";

const props = defineProps({
  book: { type: Object, required: true },
  selected: { type: Boolean, default: false }
});
const emit = defineEmits(["select"]);

const tier = computed(() => (props.book.tier || "B").toUpperCase());
const tierMeta = computed(() => TIER_LABEL[tier.value] || TIER_LABEL.B);
const statusMeta = computed(
  () => STATUS_LABEL[props.book.status] || STATUS_LABEL.queued
);
const progressColor = computed(() => {
  const p = displayProgress.value;
  if (p >= 80) return "#86efac";
  if (p >= 30) return "#fbbf24";
  return "#94a3b8";
});
const schoolChips = computed(() =>
  (props.book.schools_tags || []).map(s => SCHOOL_LABEL[s] || s)
);
const restoreMethodMeta = computed(
  () => RESTORE_METHOD_LABEL[props.book.restore_method || "unknown"]
);
const displayDonePages = computed(() =>
  (props.book.restored_pages || 0) > 0
    ? props.book.restored_pages || 0
    : props.book.pages_ingested || 0
);
const displayProgress = computed(() => {
  const total = props.book.pages_total || 0;
  return total > 0 ? Math.min(100, (displayDonePages.value / total) * 100) : 0;
});
const progressLabel = computed(() =>
  (props.book.restored_pages || 0) > 0 ? "phục chế" : "đã đọc"
);
</script>

<template>
  <div class="book-card" :class="{ selected }" @click="emit('select', book)">
    <div class="bc-head">
      <span class="tier-badge" :style="{ background: tierMeta.color }">{{ tier }}</span>
      <span class="status-pill" :style="{ color: statusMeta.color }">●&nbsp;{{ statusMeta.label }}</span>
      <span class="method-pill" :style="{ color: restoreMethodMeta.color }"
            :title="restoreMethodMeta.desc">
        {{ restoreMethodMeta.icon }}
      </span>
    </div>
    <div class="bc-body">
      <div class="title" :title="book.name">{{ book.name }}</div>
      <div v-if="book.author" class="author">— {{ book.author }}</div>
      <div v-if="schoolChips.length" class="schools">
        <span v-for="s in schoolChips" :key="s" class="chip">{{ s }}</span>
      </div>
    </div>
    <div class="bc-progress">
      <div class="bar">
        <div class="fill" :style="{
          width: displayProgress + '%',
          background: progressColor
        }"></div>
      </div>
      <div class="pp">
        <span>{{ displayDonePages }} / {{ book.pages_total || 0 }} tr {{ progressLabel }}</span>
        <span>{{ displayProgress.toFixed(1) }}%</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  padding: 0.6rem 0.7rem;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-height: 110px;
}
.book-card:hover {
  background: rgba(167, 139, 250, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
  transform: translateY(-1px);
}
.book-card.selected {
  background: rgba(167, 139, 250, 0.15);
  border-color: #a78bfa;
}
.bc-head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  justify-content: space-between;
}
.tier-badge {
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.7rem;
}
.status-pill {
  font-size: 0.7rem;
}
.method-pill {
  margin-left: auto;
  font-size: 0.85rem;
  cursor: help;
}
.bc-body { flex: 1; }
.title {
  color: #f1f5f9;
  font-size: 0.85rem;
  line-height: 1.3;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.author {
  color: #94a3b8;
  font-size: 0.72rem;
  margin-top: 0.2rem;
  font-style: italic;
}
.schools {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  margin-top: 0.3rem;
}
.chip {
  padding: 0.05rem 0.35rem;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border-radius: 3px;
  font-size: 0.65rem;
}
.bc-progress { margin-top: 0.2rem; }
.bar {
  height: 4px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 2px;
  overflow: hidden;
}
.fill { height: 100%; transition: width 0.3s; }
.pp {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: #64748b;
  margin-top: 0.25rem;
}
</style>
