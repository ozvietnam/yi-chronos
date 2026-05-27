<script setup>
import { computed } from "vue";

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 16 }
});

const iconMap = {
  profiles: { glyph: "📋", tone: "gold" },
  universe: { glyph: "🌌", tone: "blue" },
  western: { glyph: "♈", tone: "violet" },
  maihoa: { glyph: "☯", tone: "teal" },
  "luc-hao": { glyph: "☷", tone: "slate" },
  "lien-hoa": { glyph: "☘", tone: "green" },
  "bat-tu": { glyph: "🪙", tone: "amber" },
  "tu-vi": { glyph: "🔮", tone: "magenta" },
  "ky-mon": { glyph: "⊞", tone: "bronze" },
  pytago: { glyph: "🔢", tone: "cyan" },
  family: { glyph: "👪", tone: "sage" },
  gps: { glyph: "🎯", tone: "red" },
  lexicon: { glyph: "📖", tone: "indigo" },
  chronos: { glyph: "☯", tone: "gold" },
  hexagram: { glyph: "☰", tone: "gold" }
};

const icon = computed(() => iconMap[props.name] || iconMap.hexagram);
const style = computed(() => ({
  "--school-icon-size": `${Number(props.size) || 16}px`
}));
</script>

<template>
  <span class="school-icon" :class="`tone-${icon.tone}`" :style="style" aria-hidden="true">
    {{ icon.glyph }}
  </span>
</template>

<style scoped>
.school-icon {
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  width: var(--school-icon-size);
  height: var(--school-icon-size);
  border: 0;
  border-radius: 0;
  font-size: var(--school-icon-size);
  line-height: 1;
  background: transparent;
  box-shadow: none;
}

.tone-gold { color: #e8c95a; }
.tone-blue { color: #7dd3fc; }
.tone-violet { color: #c4b5fd; }
.tone-teal { color: #5be5d3; }
.tone-slate { color: #cbd5e1; }
.tone-green { color: #86efac; }
.tone-amber { color: #fbbf24; }
.tone-magenta { color: #f0abfc; }
.tone-cyan { color: #67e8f9; }
.tone-sage { color: #bbf7d0; }
.tone-red { color: #fca5a5; }
.tone-indigo { color: #a5b4fc; }
.tone-bronze { color: #d4a574; }
</style>
