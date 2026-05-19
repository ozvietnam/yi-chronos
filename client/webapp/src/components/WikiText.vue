<script setup>
/**
 * WikiText — render text and auto-highlight known Tử Vi terms.
 *
 * Click highlighted term → opens WikiPopup with definition.
 *
 * Algorithm:
 * - Get sortedByLength concepts (longest first)
 * - Scan text greedy: find first concept match, split into segments
 * - Avoid re-matching inside already-matched ranges
 */
import { computed } from "vue";
import { sortedByLength, showPopup, byCanonicalVi } from "../stores/wikiTermsStore.js";

const props = defineProps({
  text: { type: String, default: "" },
});

// Build segments: [{type: 'text', content: '...'} | {type: 'term', concept: {...}, content: 'matched text'}]
const segments = computed(() => {
  const txt = props.text || "";
  if (!txt || sortedByLength.value.length === 0) {
    return [{ type: "text", content: txt }];
  }

  // Build regex from all terms — longest first (matters for greedy)
  // Escape special chars
  const terms = sortedByLength.value
    .map((c) => ({ pattern: c.vi, concept: c }))
    .filter((t) => t.pattern && t.pattern.length >= 2);

  if (!terms.length) return [{ type: "text", content: txt }];

  // Use single combined regex for speed: (term1|term2|term3...)
  const escaped = terms.map((t) => t.pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  // Use a non-capturing alternation, word-boundary-aware for Vietnamese (use unicode boundary)
  // Vietnamese accents — we use lookbehind/lookahead with non-letter chars
  const re = new RegExp(
    "(?<![\\p{L}\\p{M}])(" + escaped.join("|") + ")(?![\\p{L}\\p{M}])",
    "gu",
  );

  const out = [];
  let lastIdx = 0;
  let m;
  const conceptByVi = new Map();
  for (const t of terms) conceptByVi.set(t.pattern, t.concept);

  while ((m = re.exec(txt)) !== null) {
    if (m.index > lastIdx) {
      out.push({ type: "text", content: txt.slice(lastIdx, m.index) });
    }
    out.push({
      type: "term",
      content: m[0],
      concept: conceptByVi.get(m[0]) || byCanonicalVi.value.get(m[0].toLowerCase()),
    });
    lastIdx = m.index + m[0].length;
  }
  if (lastIdx < txt.length) {
    out.push({ type: "text", content: txt.slice(lastIdx) });
  }
  return out;
});

function onTermClick(concept) {
  if (concept) showPopup(concept);
}
</script>

<template>
  <span class="wt-wrap">
    <template v-for="(seg, i) in segments" :key="i">
      <span
        v-if="seg.type === 'term' && seg.concept"
        class="wt-term"
        :title="seg.concept.note?.substring(0, 100) || seg.concept.vi"
        @click.stop="onTermClick(seg.concept)"
      >{{ seg.content }}</span>
      <template v-else>{{ seg.content }}</template>
    </template>
  </span>
</template>

<style scoped>
.wt-wrap { display: inline; }
.wt-term {
  border-bottom: 1px dotted #60a5fa;
  cursor: help;
  color: inherit;
  transition: all 0.12s;
  padding: 0 1px;
}
.wt-term:hover {
  background: rgba(96, 165, 250, 0.18);
  border-bottom-style: solid;
  border-bottom-color: #2563eb;
  color: #2563eb;
}
</style>
