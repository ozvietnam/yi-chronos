<script setup>
import { computed } from "vue";
import {
  ClipboardList, Orbit, Sun, Flower2, AlignJustify, Flower, Columns3,
  Sparkles, LayoutGrid, Calculator, Users, Compass, BookA, Clock,
  FileText, ScanFace, Scale, Atom, Library, HeartHandshake, HeartPulse,
  Settings, FlaskConical, BookOpenText, BookMarked, UserCog, Shield, ClipboardCheck
} from "lucide-vue-next";

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 16 }
});

// name → { icon Lucide (SVG thật, không còn emoji), tone màu }
const iconMap = {
  profiles: { comp: ClipboardList, tone: "gold" },
  universe: { comp: Orbit, tone: "blue" },
  western: { comp: Sun, tone: "violet" },
  maihoa: { comp: Flower2, tone: "teal" },
  "luc-hao": { comp: AlignJustify, tone: "slate" },
  "lien-hoa": { comp: Flower, tone: "green" },
  "bat-tu": { comp: Columns3, tone: "amber" },
  "tu-vi": { comp: Sparkles, tone: "magenta" },
  "ky-mon": { comp: LayoutGrid, tone: "bronze" },
  pytago: { comp: Calculator, tone: "cyan" },
  family: { comp: Users, tone: "sage" },
  gps: { comp: Compass, tone: "red" },
  lexicon: { comp: BookA, tone: "indigo" },
  chronos: { comp: Clock, tone: "gold" },
  hexagram: { comp: AlignJustify, tone: "gold" },
  // Các tab/heading trước dùng emoji → nay SVG đồng bộ
  "my-publications": { comp: FileText, tone: "gold" },
  "chan-dung": { comp: ScanFace, tone: "magenta" },
  "hoi-hermes": { comp: Scale, tone: "gold" },
  "hoang-cuc": { comp: Atom, tone: "violet" },
  library: { comp: Library, tone: "indigo" },
  "gieo-duyen": { comp: HeartHandshake, tone: "magenta" },
  health: { comp: HeartPulse, tone: "green" },
  settings: { comp: Settings, tone: "slate" },
  research: { comp: FlaskConical, tone: "cyan" },
  wiki: { comp: BookOpenText, tone: "blue" },
  publishing: { comp: BookMarked, tone: "amber" },
  admin: { comp: UserCog, tone: "slate" },
  "admin-hermes": { comp: Shield, tone: "gold" },
  "atom-verify": { comp: ClipboardCheck, tone: "green" }
};

const entry = computed(() => iconMap[props.name] || iconMap.hexagram);
const px = computed(() => Number(props.size) || 16);
</script>

<template>
  <component
    :is="entry.comp"
    :size="px"
    :stroke-width="2"
    class="school-icon"
    :class="`tone-${entry.tone}`"
    aria-hidden="true"
  />
</template>

<style scoped>
.school-icon {
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: -0.18em;
}

/* màu tông (SVG dùng stroke=currentColor → ăn theo color) */
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
