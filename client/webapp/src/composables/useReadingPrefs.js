/**
 * Reading comfort preferences — global text scale + reading theme.
 *
 * Persists to localStorage and applies to <html> as:
 *   --reading-scale   (number, e.g. 1.15)   → scales reading-surface + root font
 *   data-reading       ("sepia" | "dark" | "paper")
 *
 * Default: Sepia đêm (warm dark) + scale 1.0 — chosen by founder for long
 * classical-text reading (low eye strain).
 */
import { ref, watch } from "vue";

const STORE_KEY = "yi.reading.prefs.v1";

const THEMES = ["sepia", "dark", "paper"];
const LEADINGS = ["normal", "relaxed", "loose"];
const LEADING_HEIGHT = { normal: 1.78, relaxed: 1.92, loose: 2.08 };
const SCALE_MIN = 0.9;
const SCALE_MAX = 1.5;
const SCALE_STEP = 0.075;

function _load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) {
      const p = JSON.parse(raw);
      return {
        theme: THEMES.includes(p.theme) ? p.theme : "sepia",
        scale: typeof p.scale === "number" ? clampScale(p.scale) : 1,
        leading: LEADINGS.includes(p.leading) ? p.leading : "relaxed",
        focus: !!p.focus,
      };
    }
  } catch (_) {
    /* ignore */
  }
  return { theme: "sepia", scale: 1, leading: "relaxed", focus: false };
}

function clampScale(s) {
  return Math.min(SCALE_MAX, Math.max(SCALE_MIN, Math.round(s * 1000) / 1000));
}

// Module-level singletons so every caller shares one source of truth.
const _initial = _load();
const theme = ref(_initial.theme);
const scale = ref(_initial.scale);
const leading = ref(_initial.leading);
const focus = ref(_initial.focus);

function _apply() {
  const el = document.documentElement;
  el.setAttribute("data-reading", theme.value);
  el.setAttribute("data-reading-leading", leading.value);
  el.toggleAttribute("data-reading-focus", focus.value);
  el.style.setProperty("--reading-scale", String(scale.value));
  el.style.setProperty("--reading-line-height", String(LEADING_HEIGHT[leading.value] || 1.78));
}

let _started = false;
function startReadingPrefs() {
  if (_started) return;
  _started = true;
  _apply();
  watch([theme, scale, leading, focus], () => {
    _apply();
    try {
      localStorage.setItem(
        STORE_KEY,
        JSON.stringify({
          theme: theme.value,
          scale: scale.value,
          leading: leading.value,
          focus: focus.value,
        })
      );
    } catch (_) {
      /* ignore quota */
    }
  });
}

export function useReadingPrefs() {
  return {
    theme,
    scale,
    leading,
    focus,
    THEMES,
    LEADINGS,
    SCALE_MIN,
    SCALE_MAX,
    startReadingPrefs,
    setTheme(t) {
      if (THEMES.includes(t)) theme.value = t;
    },
    setLeading(l) {
      if (LEADINGS.includes(l)) leading.value = l;
    },
    toggleFocus() {
      focus.value = !focus.value;
    },
    incScale() {
      scale.value = clampScale(scale.value + SCALE_STEP);
    },
    decScale() {
      scale.value = clampScale(scale.value - SCALE_STEP);
    },
    resetScale() {
      scale.value = 1;
    },
    scalePct() {
      return Math.round(scale.value * 100);
    },
    leadingLabel() {
      return { normal: "Gọn", relaxed: "Thoải", loose: "Rộng" }[leading.value] || leading.value;
    },
  };
}
