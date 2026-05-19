<script setup>
/**
 * Small share button — copies a kabala-compatible ?birth=... URL of the
 * given person to the clipboard, and lets the user pin the active person
 * into the URL (so refresh keeps state).
 *
 * Props:
 *   - birthDatetimeLocal (string, required) — ISO local datetime
 *   - gender (string, optional) — 'nam' | 'nữ'
 *   - personName (string, optional) — for the title attribute
 */

import { ref } from "vue";
import { buildShareLink, syncBirthInUrl } from "../composables/useBirthShare.js";

const props = defineProps({
  birthDatetimeLocal: { type: String, required: true },
  gender: { type: String, default: null },
  personName: { type: String, default: "" },
});

const copied = ref(false);
const pinned = ref(false);

async function copy() {
  const url = buildShareLink({
    birthDatetimeLocal: props.birthDatetimeLocal,
    gender: props.gender,
  });
  if (!url) return;
  try {
    await navigator.clipboard.writeText(url);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // Fallback: just navigate so user can copy from address bar.
    window.history.replaceState({}, "", url);
  }
}

function pinToUrl() {
  syncBirthInUrl({
    birthDatetimeLocal: props.birthDatetimeLocal,
    gender: props.gender,
  });
  pinned.value = true;
  setTimeout(() => (pinned.value = false), 2000);
}
</script>

<template>
  <span class="share-group">
    <button
      class="share-btn"
      type="button"
      :title="personName ? `Sao chép link chia sẻ chart của ${personName}` : 'Sao chép link chia sẻ'"
      @click="copy"
    >
      {{ copied ? "✓ Đã sao chép" : "🔗 Sao chép link" }}
    </button>
    <button
      class="share-btn secondary"
      type="button"
      title="Ghim sinh thần vào URL (refresh giữ nguyên)"
      @click="pinToUrl"
    >
      {{ pinned ? "✓ Đã ghim" : "📌 Ghim URL" }}
    </button>
  </span>
</template>

<style scoped>
.share-group { display: inline-flex; gap: 6px; flex-wrap: wrap; }
.share-btn {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.3);
  color: var(--accent-teal, #5be5d3);
  padding: 5px 11px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.share-btn:hover {
  background: rgba(91, 229, 211, 0.16);
}
.share-btn.secondary {
  background: rgba(232, 201, 90, 0.06);
  border-color: rgba(232, 201, 90, 0.3);
  color: var(--accent-gold, #e8c95a);
}
.share-btn.secondary:hover {
  background: rgba(232, 201, 90, 0.14);
}
</style>
