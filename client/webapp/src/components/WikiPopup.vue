<script setup>
/**
 * WikiPopup — global popup component that shows the currently-selected
 * Tử Vi concept (set via wikiTermsStore.showPopup()).
 *
 * Mount once in App.vue.
 */
import { computed } from "vue";
import { popupConcept, hidePopup } from "../stores/wikiTermsStore.js";

const visible = computed(() => !!popupConcept.value);
const c = computed(() => popupConcept.value);

const aliasList = computed(() => {
  const a = c.value?.aliases;
  if (!a) return [];
  try {
    const parsed = typeof a === "string" ? JSON.parse(a) : a;
    return Array.isArray(parsed) ? parsed : (typeof a === "string" ? a.split(",").map((s) => s.trim()) : []);
  } catch {
    return typeof a === "string" ? a.split(",").map((s) => s.trim()).filter(Boolean) : [];
  }
});
</script>

<template>
  <div v-if="visible" class="wp-backdrop" @click.self="hidePopup">
    <div class="wp-modal" @click.stop>
      <button class="wp-close" @click="hidePopup">✕</button>
      <header class="wp-head">
        <div class="wp-zh" v-if="c.zh">{{ c.zh }}</div>
        <h3 class="wp-vi">{{ c.vi }}</h3>
        <small class="wp-id">Wiki #{{ c.id }}</small>
      </header>
      <p v-if="c.note" class="wp-note">{{ c.note }}</p>
      <p v-else class="wp-empty">(chưa có giải nghĩa)</p>
      <div v-if="aliasList.length" class="wp-aliases">
        <span class="wp-alias-label">Tên khác:</span>
        <span v-for="a in aliasList" :key="a" class="wp-alias">{{ a }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wp-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.65); z-index: 3000;
  display: flex; justify-content: center; align-items: center;
  padding: 1rem;
  backdrop-filter: blur(3px);
}
.wp-modal {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #475569;
  border-radius: 8px;
  max-width: 480px;
  width: 100%;
  padding: 1.1rem 1.3rem;
  color: #e2e8f0;
  font-family: "Charter", "Iowan Old Style", Georgia, serif;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.wp-close {
  position: absolute; top: 0.4rem; right: 0.55rem;
  background: rgba(255,255,255,0.1); border: none; color: #cbd5e1;
  width: 28px; height: 28px; border-radius: 4px;
  cursor: pointer; font-size: 0.9rem;
}
.wp-close:hover { background: rgba(255,255,255,0.2); }

.wp-head { padding-bottom: 0.6rem; border-bottom: 1px solid #334155; margin-bottom: 0.7rem; }
.wp-zh {
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
  font-size: 1.4rem; color: #fde68a; letter-spacing: 0.1em; line-height: 1.2;
}
.wp-vi { margin: 0.25rem 0 0; color: #f1f5f9; font-size: 1.15rem; font-weight: 600; }
.wp-id { color: #64748b; font-size: 0.72rem; font-family: ui-monospace, monospace; }

.wp-note {
  margin: 0; line-height: 1.65; font-size: 0.92rem; color: #cbd5e1;
}
.wp-empty { color: #64748b; font-style: italic; font-size: 0.85rem; }

.wp-aliases {
  margin-top: 0.7rem; padding-top: 0.55rem; border-top: 1px dashed #334155;
  font-size: 0.78rem;
}
.wp-alias-label { color: #94a3b8; margin-right: 0.4rem; }
.wp-alias {
  display: inline-block;
  background: rgba(96,165,250,0.15); color: #93c5fd;
  padding: 1px 7px; border-radius: 3px; margin: 1px 3px 1px 0;
  font-family: ui-sans-serif, sans-serif;
}
</style>
