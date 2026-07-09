<script setup>
/**
 * KinhDichBrowser — Tra cứu 64 quẻ Kinh Dịch tự do.
 *
 * UI:
 *   - 8×8 grid (8 quẻ đơn upper × 8 quẻ đơn lower) → 64 cell
 *   - Click cell → drawer mở từ phải hiện full Lời Kinh + 6 hào + Trình Di + Chu Hy
 *   - Search box filter theo tên / Hán / routing_keys
 *   - Markdown render với highlight quotes (Trình Di) trong blockquote
 *
 * API:
 *   GET /api/yi-wiki/kinh-dich/list  → 64 hexagrams metadata
 *   GET /api/yi-wiki/kinh-dich/que/{slug} → full body markdown
 */
import { ref, computed, onMounted } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";
import { renderMarkdown } from "../../lib/markdown.js";

const TRIGRAMS = ["Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"];
const TRIGRAM_UNICODE = {
  "Càn": "☰", "Đoài": "☱", "Ly": "☲", "Chấn": "☳",
  "Tốn": "☴", "Khảm": "☵", "Cấn": "☶", "Khôn": "☷",
};

const hexagrams = ref([]);     // 64 list từ API
const loading = ref(false);
const error = ref("");
const search = ref("");

// Detail drawer
const selectedSlug = ref(null);
const selectedHex = ref(null);   // {body_markdown, ...}
const detailLoading = ref(false);
const detailError = ref("");

// Build 8×8 grid: rows = upper trigram, cols = lower trigram
const gridLookup = computed(() => {
  const map = {};
  for (const h of hexagrams.value) {
    map[`${h.upper}|${h.lower}`] = h;
  }
  return map;
});

function getCell(upper, lower) {
  return gridLookup.value[`${upper}|${lower}`];
}

// Filter for list view (search)
const filteredHexagrams = computed(() => {
  if (!search.value.trim()) return hexagrams.value;
  const q = search.value.trim().toLowerCase();
  return hexagrams.value.filter(h => {
    if (h.name_vi.toLowerCase().includes(q)) return true;
    if (h.name_zh.includes(q)) return true;
    if (h.number.toString() === q) return true;
    if (h.description?.toLowerCase().includes(q)) return true;
    if (h.upper.toLowerCase().includes(q) || h.lower.toLowerCase().includes(q)) return true;
    return false;
  });
});

async function loadList() {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch("/api/yi-wiki/kinh-dich/list");
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    hexagrams.value = d.hexagrams || [];
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function selectHexagram(slug, number) {
  selectedSlug.value = slug;
  selectedHex.value = null;
  detailLoading.value = true;
  detailError.value = "";
  try {
    // Use number as slug since slugs are not unique (4-Mông và 39-Kiển cùng slug "kien")
    const r = await fetch(`/api/yi-wiki/kinh-dich/que/${number}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    selectedHex.value = await r.json();
  } catch (e) {
    detailError.value = String(e.message || e);
  } finally {
    detailLoading.value = false;
  }
}

function closeDetail() {
  selectedSlug.value = null;
  selectedHex.value = null;
}

// Lightweight markdown → HTML (no deps; supports headers, blockquote, bold, italic, lists, hr, tables)
// renderMarkdown now imported from ../../lib/markdown.js — escape-first + scheme-safe
// links (was: local inlineMd escaped HTML but allowed javascript: links → XSS #22).

onMounted(loadList);
</script>

<template>
  <div class="kdb">
    <header class="kdb-header">
      <h2>📜 64 Quẻ Kinh Dịch — Tra cứu</h2>
      <p class="subtitle">
        Trích dẫn Trình Di Truyện + Bản nghĩa Chu Hy + Tiên Nho. Bấm vào 1 quẻ để xem Lời Kinh + 6 hào.
      </p>
      <input v-model="search" type="text" placeholder="Tìm theo tên (Khôn, Tỉnh), Hán (坤), số (1, 64), từ khóa (hữu phu, đại nhân)..."
             class="kdb-search" />
    </header>

    <div v-if="loading" class="kdb-status">Đang tải 64 quẻ...</div>
    <div v-if="error" class="kdb-error">Lỗi: {{ error }}</div>

    <!-- Grid view: 8×8 traditional layout (default, when no search) -->
    <div v-if="!loading && !search.trim() && hexagrams.length" class="kdb-grid-wrap">
      <p class="kdb-grid-hint">Hàng = quẻ <b>TRÊN</b> (Ngoại). Cột = quẻ <b>DƯỚI</b> (Nội).</p>
      <table class="kdb-grid">
        <thead>
          <tr>
            <th class="corner">Ngoại\Nội</th>
            <th v-for="lower in TRIGRAMS" :key="lower">
              <div class="tr-head">
                <span class="tr-uni">{{ TRIGRAM_UNICODE[lower] }}</span>
                <span class="tr-name">{{ lower }}</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="upper in TRIGRAMS" :key="upper">
            <th class="tr-head">
              <span class="tr-uni">{{ TRIGRAM_UNICODE[upper] }}</span>
              <span class="tr-name">{{ upper }}</span>
            </th>
            <td v-for="lower in TRIGRAMS" :key="lower"
                class="kdb-cell"
                :class="{ active: getCell(upper, lower)?.slug === selectedSlug }"
                @click="getCell(upper, lower) && selectHexagram(getCell(upper, lower).slug, getCell(upper, lower).number)">
              <div v-if="getCell(upper, lower)" class="cell-inner">
                <div class="cell-num">{{ getCell(upper, lower).number }}</div>
                <HexagramSvg :upper="upper" :lower="lower" :size="60" :show-label="false" />
                <div class="cell-name">{{ getCell(upper, lower).name_vi }}</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- List view (when searching) -->
    <div v-if="!loading && search.trim() && hexagrams.length" class="kdb-list">
      <p class="kdb-list-hint">{{ filteredHexagrams.length }} / 64 quẻ khớp "{{ search }}"</p>
      <div class="kdb-list-grid">
        <div v-for="h in filteredHexagrams" :key="h.number"
             class="kdb-list-card"
             :class="{ active: h.slug === selectedSlug }"
             @click="selectHexagram(h.slug, h.number)">
          <div class="card-head">
            <span class="card-num">{{ h.number }}</span>
            <span class="card-uni">{{ h.structure_unicode }}</span>
          </div>
          <div class="card-name">{{ h.name_vi }} <span class="card-zh">{{ h.name_zh }}</span></div>
          <div class="card-trigram">{{ h.upper }} / {{ h.lower }}</div>
          <div class="card-desc">{{ h.description }}</div>
        </div>
      </div>
    </div>

    <!-- Detail drawer -->
    <div v-if="selectedSlug" class="kdb-drawer">
      <div class="drawer-head">
        <button class="drawer-close" @click="closeDetail">✕ Đóng</button>
        <span v-if="selectedHex" class="drawer-title">
          Quẻ {{ selectedHex.number }} — {{ selectedHex.name_vi }} {{ selectedHex.name_zh }}
          <span class="drawer-struct">{{ selectedHex.structure_unicode }}</span>
        </span>
      </div>
      <div v-if="detailLoading" class="drawer-status">Đang đọc quẻ...</div>
      <div v-if="detailError" class="drawer-error">Lỗi: {{ detailError }}</div>
      <div v-if="selectedHex" class="drawer-body">
        <div class="drawer-meta">
          <HexagramSvg :upper="selectedHex.upper" :lower="selectedHex.lower" :size="120" />
          <div class="meta-info">
            <p><b>Cấu trúc:</b> {{ selectedHex.upper }} trên + {{ selectedHex.lower }} dưới</p>
            <p v-if="selectedHex.routing_keys?.length"><b>Routing keys:</b>
              <code v-for="k in selectedHex.routing_keys" :key="k" class="rk">{{ k }}</code>
            </p>
            <p v-if="!selectedHex.has_deep" class="depth-warn">⚠️ Quẻ này dùng canonical Trình Di paradigm (OCR Ngô Tất Tố không đủ rõ)</p>
          </div>
        </div>
        <article class="drawer-markdown" v-html="renderMarkdown(selectedHex.body_markdown)"></article>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Follows the global reading theme (Sepia đêm / Than dịu / Giấy mềm) + text scale
   via the --read-* tokens and --reading-scale set on <html> by useReadingPrefs. */
.kdb {
  padding: 1rem; max-width: 1400px; margin: 0 auto;
  background: var(--read-bg); color: var(--read-text); border-radius: 12px;
  font-size: calc(15px * var(--reading-scale));
}
.kdb-header { margin-bottom: 1.2rem; }
.kdb-header h2 { margin: 0 0 .3rem; color: var(--read-heading); font-size: calc(22px * var(--reading-scale)); }
.subtitle { color: var(--read-text-dim); font-style: italic; margin: 0 0 .8rem; font-size: calc(14px * var(--reading-scale)); }
.kdb-search {
  width: 100%; max-width: 600px; padding: .55rem .8rem; border: 1px solid var(--read-border);
  border-radius: 6px; font-size: calc(15px * var(--reading-scale));
  background: var(--read-surface); color: var(--read-text);
}
.kdb-status, .kdb-error { padding: 1rem; text-align: center; color: var(--read-text-dim); }
.kdb-error { color: var(--accent-red, #b91c1c); }
.kdb-grid-hint, .kdb-list-hint { color: var(--read-text-dim); font-size: calc(13.5px * var(--reading-scale)); margin: .5rem 0; }

/* 8×8 grid */
.kdb-grid { border-collapse: collapse; width: 100%; table-layout: fixed; }
.kdb-grid th, .kdb-grid td {
  border: 1px solid var(--read-border); padding: 0; text-align: center;
}
.kdb-grid th { background: var(--read-bg-soft); padding: .4rem .2rem; font-size: calc(13.5px * var(--reading-scale)); vertical-align: middle; color: var(--read-text); }
.kdb-grid th.corner { font-size: calc(12px * var(--reading-scale)); color: var(--read-text-dim); }
.tr-head { display: flex; flex-direction: column; gap: .15rem; align-items: center; }
.tr-uni { font-size: calc(20px * var(--reading-scale)); color: var(--read-han); }
.tr-name { font-size: calc(12px * var(--reading-scale)); color: var(--read-text-dim); }
.kdb-cell {
  cursor: pointer; padding: 0; transition: background .15s; background: var(--read-surface);
}
.kdb-cell:hover { background: var(--read-bg-soft); }
.kdb-cell.active { background: var(--read-rule); }
.cell-inner { padding: .3rem .15rem; display: flex; flex-direction: column; gap: .1rem; align-items: center; }
.cell-num { font-size: calc(11.5px * var(--reading-scale)); color: var(--read-text-dim); font-weight: bold; }
.cell-name { font-size: calc(12px * var(--reading-scale)); color: var(--read-heading); line-height: 1.15; }

/* List view (search) */
.kdb-list-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: .8rem;
}
.kdb-list-card {
  background: var(--read-surface); border: 1px solid var(--read-border); border-radius: 6px; padding: .6rem .8rem;
  cursor: pointer; transition: all .15s;
}
.kdb-list-card:hover { background: var(--read-bg-soft); border-color: var(--read-rule); }
.kdb-list-card.active { background: var(--read-bg-soft); border-color: var(--read-rule); box-shadow: inset 3px 0 0 var(--read-rule); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.card-num { font-weight: bold; color: var(--read-han); }
.card-uni { font-size: calc(20px * var(--reading-scale)); color: var(--read-han); }
.card-name { font-size: calc(16px * var(--reading-scale)); font-weight: 600; color: var(--read-heading); margin: .25rem 0; }
.card-zh { font-size: calc(14px * var(--reading-scale)); color: var(--read-text-dim); font-weight: normal; }
.card-trigram { font-size: calc(12.5px * var(--reading-scale)); color: var(--read-text-dim); }
.card-desc { font-size: calc(13px * var(--reading-scale)); color: var(--read-text); margin-top: .3rem; line-height: 1.45; }

/* Drawer — the main reading pane */
.kdb-drawer {
  position: fixed; top: 0; right: 0; bottom: 0; width: 50%; max-width: 760px; min-width: 360px;
  background: var(--read-bg); border-left: 2px solid var(--read-border); z-index: 100; overflow: hidden;
  display: flex; flex-direction: column; box-shadow: -4px 0 28px rgba(0,0,0,0.4);
}
.drawer-head {
  padding: .6rem .9rem; background: var(--read-bg-soft); color: var(--read-heading);
  border-bottom: 1px solid var(--read-border);
  display: flex; align-items: center; gap: .8rem;
}
.drawer-close {
  background: var(--read-cite-bg); border: 1px solid var(--read-border); color: var(--read-text); padding: .35rem .7rem;
  border-radius: 4px; cursor: pointer; font-size: calc(13.5px * var(--reading-scale));
}
.drawer-close:hover { border-color: var(--read-rule); }
.drawer-title { font-weight: 600; }
.drawer-struct { font-size: calc(20px * var(--reading-scale)); margin-left: .4rem; color: var(--read-han); }
.drawer-status, .drawer-error { padding: 1rem; text-align: center; color: var(--read-text-dim); }
.drawer-body {
  flex: 1; overflow-y: auto; padding: 1.1rem 1.5rem 2rem;
}
.drawer-meta {
  display: flex; gap: 1.2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--read-border); margin-bottom: 1rem;
}
.meta-info { flex: 1; font-size: calc(14px * var(--reading-scale)); color: var(--read-text-dim); }
.meta-info p { margin: .2rem 0; }
.meta-info b { color: var(--read-text); }
.rk { background: var(--read-cite-bg); color: var(--read-text); padding: 1px 5px; border-radius: 3px; margin-right: 4px; font-size: calc(12px * var(--reading-scale)); }
.depth-warn { background: var(--read-cite-bg); color: var(--read-text-dim); padding: .35rem .55rem; border-left: 3px solid var(--read-cite-accent); font-size: calc(13px * var(--reading-scale)); border-radius: 0 6px 6px 0; }

/* Markdown content — the actual hexagram reading text (16px base, generous leading) */
.drawer-markdown { font-size: calc(16px * var(--reading-scale)); line-height: var(--reading-line-height, 1.78); color: var(--read-text); }
.drawer-markdown :deep(h1) { font-size: calc(24px * var(--reading-scale)); color: var(--read-heading); margin: 1.2rem 0 .5rem; line-height: 1.3; }
.drawer-markdown :deep(h2) { font-size: calc(20px * var(--reading-scale)); color: var(--read-heading); margin: 1.2rem 0 .5rem; border-bottom: 1px solid var(--read-border); padding-bottom: .2rem; line-height: 1.3; }
.drawer-markdown :deep(h3) { font-size: calc(17.5px * var(--reading-scale)); color: var(--read-han); margin: 1rem 0 .4rem; }
.drawer-markdown :deep(p) { font-size: calc(16px * var(--reading-scale)); line-height: var(--reading-line-height, 1.78); color: var(--read-text); margin: .5rem 0; }
.drawer-markdown :deep(blockquote) {
  background: var(--read-cite-bg); border-left: 3px solid var(--read-cite-accent); padding: .6rem .9rem;
  margin: .7rem 0; font-style: italic; color: var(--read-text-dim); line-height: 1.7; border-radius: 0 6px 6px 0;
}
.drawer-markdown :deep(ul) { padding-left: 1.4rem; line-height: 1.7; }
.drawer-markdown :deep(li) { margin: .2rem 0; }
.drawer-markdown :deep(code) { background: var(--read-bg-soft); color: var(--read-han); padding: 1px 5px; border-radius: 3px; font-family: monospace; font-size: calc(14px * var(--reading-scale)); }
.drawer-markdown :deep(b) { color: var(--read-heading); }
.drawer-markdown :deep(hr) { border: 0; border-top: 1px dashed var(--read-border); margin: 1.1rem 0; }
.drawer-markdown :deep(.md-table) {
  border-collapse: collapse; margin: .9rem 0; font-size: calc(14px * var(--reading-scale)); width: 100%;
}
.drawer-markdown :deep(.md-table th), .drawer-markdown :deep(.md-table td) {
  border: 1px solid var(--read-border); padding: .4rem .6rem; vertical-align: top; color: var(--read-text);
}
.drawer-markdown :deep(.md-table th) { background: var(--read-bg-soft); color: var(--read-heading); }
.drawer-markdown :deep(a) { color: var(--read-link); }

/* Mobile */
@media (max-width: 768px) {
  .kdb { padding: 0.75rem; border-radius: 10px; }
  .kdb-drawer {
    width: 100%;
    max-width: none;
    min-width: 0;
    z-index: 200;
    border-left: 0;
  }
  .drawer-head {
    padding: calc(0.55rem + env(safe-area-inset-top, 0px)) 0.85rem 0.55rem;
    position: sticky;
    top: 0;
    z-index: 2;
  }
  .drawer-body {
    padding: 1rem 1rem calc(1.5rem + env(safe-area-inset-bottom, 0px));
  }
  .drawer-meta {
    flex-direction: column;
    gap: 0.75rem;
  }
  .drawer-markdown {
    font-size: calc(17px * var(--reading-scale));
  }
  .drawer-markdown :deep(p) {
    font-size: calc(17px * var(--reading-scale));
    line-height: var(--reading-line-height, 1.92);
    margin: 0.7rem 0;
  }
  .drawer-close {
    min-height: 44px;
    min-width: 44px;
  }
  .kdb-grid { font-size: .7rem; }
  .cell-inner { padding: .15rem .05rem; }
  .cell-name { font-size: calc(10px * var(--reading-scale)); }
}
</style>
