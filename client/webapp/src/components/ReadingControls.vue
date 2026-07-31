<script setup>
/**
 * Floating reading-comfort control: text size A− / A+, reading theme,
 * line spacing, and optional focus mode (hide chrome while reading).
 */
import { ref } from "vue";
import { useReadingPrefs } from "../composables/useReadingPrefs.js";

const {
  theme, setTheme, incScale, decScale, resetScale, scalePct,
  leading, setLeading, LEADINGS, leadingLabel,
  focus, toggleFocus,
} = useReadingPrefs();

const open = ref(false);

const THEME_OPTS = [
  { id: "sepia", label: "Sepia đêm", swatch: "#1d1813", dot: "#d9b977" },
  { id: "dark", label: "Than dịu", swatch: "#16181c", dot: "#5be5d3" },
  { id: "paper", label: "Giấy mềm", swatch: "#f3ead4", dot: "#8a5a22" },
];

const LEADING_OPTS = [
  { id: "normal", label: "Gọn", hint: "1.78" },
  { id: "relaxed", label: "Thoải", hint: "1.92" },
  { id: "loose", label: "Rộng", hint: "2.08" },
];
</script>

<template>
  <div class="rc-root">
    <button
      class="rc-fab"
      :class="{ active: open || focus }"
      :title="'Cỡ chữ & nền đọc'"
      @click="open = !open"
      aria-label="Cỡ chữ và nền đọc"
      aria-expanded="open"
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

      <div class="rc-row">
        <span class="rc-cap">Khoảng dòng · {{ leadingLabel() }}</span>
        <div class="rc-leading">
          <button
            v-for="l in LEADING_OPTS"
            :key="l.id"
            class="rc-lead-btn"
            :class="{ active: leading === l.id }"
            @click="setLeading(l.id)"
            :title="`Line-height ${l.hint}`"
          >
            {{ l.label }}
          </button>
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

      <div class="rc-row rc-focus">
        <button
          type="button"
          class="rc-focus-btn"
          :class="{ on: focus }"
          @click="toggleFocus()"
        >
          <span class="rc-focus-icon">{{ focus ? "◉" : "○" }}</span>
          <span>
            <b>Đọc tập trung</b>
            <small>Ẩn tác vụ nhanh & đồng hồ phụ</small>
          </span>
        </button>
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
  transition: transform 0.12s, border-color 0.15s, background 0.15s;
}
.rc-fab:hover { transform: translateY(-1px); border-color: var(--accent-gold, #e8c95a); }
.rc-fab.active {
  border-color: var(--accent-teal, #5be5d3);
  box-shadow: 0 0 0 2px rgba(91, 229, 211, 0.25);
}
.rc-fab-a { font-size: 19px; font-weight: 700; line-height: 1; }
.rc-fab-a::after { content: "+"; font-size: 11px; vertical-align: super; opacity: 0.8; }

.rc-panel {
  position: absolute;
  right: 0;
  bottom: 54px;
  width: 260px;
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
.rc-leading { display: flex; gap: 5px; }
.rc-lead-btn {
  flex: 1;
  min-height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.14));
  background: var(--bg-input, rgba(0, 0, 0, 0.35));
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}
.rc-lead-btn.active {
  border-color: var(--accent-gold, #e8c95a);
  color: var(--accent-gold, #e8c95a);
  background: rgba(232, 201, 90, 0.12);
}
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

.rc-focus-btn {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 10px 11px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.1));
  background: rgba(0, 0, 0, 0.2);
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  cursor: pointer;
  text-align: left;
}
.rc-focus-btn.on {
  border-color: var(--accent-teal, #5be5d3);
  background: rgba(91, 229, 211, 0.1);
  color: var(--text-primary, #e6eef5);
}
.rc-focus-icon { font-size: 16px; line-height: 1.2; color: var(--accent-teal, #5be5d3); }
.rc-focus-btn b { display: block; font-size: 13px; margin-bottom: 2px; }
.rc-focus-btn small { display: block; font-size: 11px; opacity: 0.75; line-height: 1.35; }

@media (max-width: 560px) {
  .rc-root {
    left: calc(14px + env(safe-area-inset-left, 0px));
    right: auto;
    bottom: calc(14px + env(safe-area-inset-bottom, 0px));
  }
  .rc-fab {
    width: 48px;
    height: 48px;
  }
  .rc-panel {
    left: 0;
    right: auto;
    width: min(280px, calc(100vw - 28px));
    bottom: 56px;
    max-height: min(70vh, calc(100vh - 90px));
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
