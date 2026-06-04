<script setup>
/**
 * Floating reading-comfort control: text size A− / A+ and reading theme.
 * Global — affects every reading surface. Persisted via useReadingPrefs.
 */
import { ref } from "vue";
import { useReadingPrefs } from "../composables/useReadingPrefs.js";

const { theme, setTheme, incScale, decScale, resetScale, scalePct } =
  useReadingPrefs();

const open = ref(false);

const THEME_OPTS = [
  { id: "sepia", label: "Sepia đêm", swatch: "#1d1813", dot: "#d9b977" },
  { id: "dark", label: "Than dịu", swatch: "#16181c", dot: "#5be5d3" },
  { id: "paper", label: "Giấy mềm", swatch: "#f3ead4", dot: "#8a5a22" },
];
</script>

<template>
  <div class="rc-root">
    <button
      class="rc-fab"
      :title="'Cỡ chữ & nền đọc'"
      @click="open = !open"
      aria-label="Cỡ chữ và nền đọc"
    >
      <span class="rc-fab-a">A</span>
    </button>

    <div v-if="open" class="rc-panel">
      <div class="rc-row">
        <span class="rc-cap">Cỡ chữ</span>
        <div class="rc-size">
          <button class="rc-btn" @click="decScale()" title="Nhỏ hơn">A−</button>
          <button class="rc-val" @click="resetScale()" title="Về 100%">{{ scalePct() }}%</button>
          <button class="rc-btn rc-btn-lg" @click="incScale()" title="Lớn hơn">A+</button>
        </div>
      </div>
      <div class="rc-row rc-themes">
        <span class="rc-cap">Nền đọc</span>
        <div class="rc-theme-list">
          <button
            v-for="t in THEME_OPTS"
            :key="t.id"
            class="rc-theme"
            :class="{ active: theme === t.id }"
            :style="{ background: t.swatch }"
            @click="setTheme(t.id)"
            :title="t.label"
          >
            <span class="rc-theme-dot" :style="{ background: t.dot }"></span>
            <span class="rc-theme-lbl">{{ t.label }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rc-root {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 1200;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}
.rc-fab {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--border-accent, rgba(232, 201, 90, 0.35));
  background: var(--bg-card-strong, rgba(28, 42, 56, 0.95));
  color: var(--accent-gold, #e8c95a);
  cursor: pointer;
  box-shadow: 0 6px 22px rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s, border-color 0.15s;
}
.rc-fab:hover { transform: translateY(-1px); border-color: var(--accent-gold, #e8c95a); }
.rc-fab-a { font-size: 19px; font-weight: 700; line-height: 1; }
.rc-fab-a::after { content: "+"; font-size: 11px; vertical-align: super; opacity: 0.8; }

.rc-panel {
  position: absolute;
  right: 0;
  bottom: 54px;
  width: 232px;
  background: var(--bg-card-strong, rgba(28, 42, 56, 0.98));
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.14));
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rc-row { display: flex; flex-direction: column; gap: 7px; }
.rc-cap {
  font-size: 11px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.rc-size { display: flex; align-items: center; gap: 6px; }
.rc-btn {
  flex: 1;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.14));
  background: var(--bg-input, rgba(0, 0, 0, 0.35));
  color: var(--text-primary, #e6eef5);
  cursor: pointer;
  font-size: 14px;
}
.rc-btn-lg { font-size: 17px; }
.rc-btn:hover { border-color: var(--accent-gold, #e8c95a); }
.rc-val {
  min-width: 54px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: transparent;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  cursor: pointer;
  font-size: 12.5px;
}
.rc-theme-list { display: flex; flex-direction: column; gap: 6px; }
.rc-theme {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.1));
  cursor: pointer;
  transition: border-color 0.15s;
}
.rc-theme:hover { border-color: var(--border-accent, rgba(232, 201, 90, 0.35)); }
.rc-theme.active { border-color: var(--accent-gold, #e8c95a); border-width: 1.5px; }
.rc-theme-dot { width: 12px; height: 12px; border-radius: 50%; flex: none; box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15); }
.rc-theme-lbl { font-size: 13px; color: #fff; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6); }
</style>
