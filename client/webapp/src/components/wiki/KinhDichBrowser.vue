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
function renderMarkdown(md) {
  if (!md) return "";
  const lines = md.split("\n");
  const html = [];
  let inTable = false;
  let inList = false;
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    // Tables: detect | a | b |
    if (line.startsWith("|") && line.endsWith("|")) {
      if (!inTable) { html.push('<table class="md-table">'); inTable = true; }
      // Skip separator row |---|
      if (line.match(/^\|\s*[-:]+\s*\|/)) continue;
      const cells = line.slice(1, -1).split("|").map(c => c.trim());
      const tag = (i + 1 < lines.length && lines[i + 1].match(/^\|\s*[-:]+\s*\|/)) ? "th" : "td";
      html.push("<tr>" + cells.map(c => `<${tag}>${inlineMd(c)}</${tag}>`).join("") + "</tr>");
      continue;
    } else if (inTable) {
      html.push("</table>");
      inTable = false;
    }
    // Headers
    let m;
    if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
      const lvl = m[1].length;
      html.push(`<h${lvl}>${inlineMd(m[2])}</h${lvl}>`);
      continue;
    }
    // Horizontal rule
    if (line.match(/^---+$/)) { html.push("<hr>"); continue; }
    // Blockquote
    if (line.startsWith(">")) {
      html.push(`<blockquote>${inlineMd(line.slice(1).trim())}</blockquote>`);
      continue;
    }
    // List
    if (line.match(/^[-*]\s+/)) {
      if (!inList) { html.push("<ul>"); inList = true; }
      html.push(`<li>${inlineMd(line.replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    } else if (inList && line.trim() === "") {
      html.push("</ul>");
      inList = false;
    } else if (inList) {
      html.push("</ul>");
      inList = false;
    }
    // Paragraph
    if (line.trim()) {
      html.push(`<p>${inlineMd(line)}</p>`);
    } else {
      html.push("");
    }
  }
  if (inTable) html.push("</table>");
  if (inList) html.push("</ul>");
  return html.join("\n");
}

function inlineMd(s) {
  // **bold**, _italic_, `code`, [text](url)
  return s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/\b_([^_]+)_\b/g, "<i>$1</i>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
}

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
.kdb { padding: 1rem; max-width: 1400px; margin: 0 auto; }
.kdb-header { margin-bottom: 1.2rem; }
.kdb-header h2 { margin: 0 0 .3rem; color: #7c2d12; }
.subtitle { color: #6b4f3c; font-style: italic; margin: 0 0 .8rem; font-size: .9rem; }
.kdb-search {
  width: 100%; max-width: 600px; padding: .55rem .8rem; border: 1px solid #d4a574;
  border-radius: 6px; font-size: 0.95rem; background: #fef9e7;
}
.kdb-status, .kdb-error { padding: 1rem; text-align: center; color: #6b4f3c; }
.kdb-error { color: #b91c1c; }
.kdb-grid-hint, .kdb-list-hint { color: #6b4f3c; font-size: .85rem; margin: .5rem 0; }

/* 8×8 grid */
.kdb-grid { border-collapse: collapse; width: 100%; table-layout: fixed; }
.kdb-grid th, .kdb-grid td {
  border: 1px solid #e7c490; padding: 0; text-align: center;
}
.kdb-grid th { background: #fef3c7; padding: .4rem .2rem; font-size: .85rem; vertical-align: middle; }
.kdb-grid th.corner { font-size: .75rem; color: #6b4f3c; }
.tr-head { display: flex; flex-direction: column; gap: .15rem; align-items: center; }
.tr-uni { font-size: 1.3rem; }
.tr-name { font-size: .75rem; color: #6b4f3c; }
.kdb-cell {
  cursor: pointer; padding: 0; transition: background .15s; background: #fff;
}
.kdb-cell:hover { background: #fef9e7; }
.kdb-cell.active { background: #fcd34d; }
.cell-inner { padding: .3rem .15rem; display: flex; flex-direction: column; gap: .1rem; align-items: center; }
.cell-num { font-size: .7rem; color: #6b4f3c; font-weight: bold; }
.cell-name { font-size: .72rem; color: #7c2d12; line-height: 1.1; }

/* List view (search) */
.kdb-list-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: .8rem;
}
.kdb-list-card {
  background: #fff; border: 1px solid #e7c490; border-radius: 6px; padding: .6rem .8rem;
  cursor: pointer; transition: all .15s;
}
.kdb-list-card:hover { background: #fef9e7; border-color: #d4a574; }
.kdb-list-card.active { background: #fcd34d; border-color: #92400e; }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.card-num { font-weight: bold; color: #92400e; }
.card-uni { font-size: 1.3rem; }
.card-name { font-size: 1.05rem; font-weight: 600; color: #7c2d12; margin: .25rem 0; }
.card-zh { font-size: .9rem; color: #6b4f3c; font-weight: normal; }
.card-trigram { font-size: .78rem; color: #6b4f3c; }
.card-desc { font-size: .78rem; color: #4b3621; margin-top: .3rem; line-height: 1.35; }

/* Drawer */
.kdb-drawer {
  position: fixed; top: 0; right: 0; bottom: 0; width: 50%; max-width: 720px; min-width: 360px;
  background: #fef9e7; border-left: 2px solid #d4a574; z-index: 100; overflow: hidden;
  display: flex; flex-direction: column; box-shadow: -4px 0 20px rgba(0,0,0,0.15);
}
.drawer-head {
  padding: .6rem .9rem; background: #92400e; color: white;
  display: flex; align-items: center; gap: .8rem;
}
.drawer-close {
  background: rgba(255,255,255,0.2); border: none; color: white; padding: .35rem .7rem;
  border-radius: 4px; cursor: pointer; font-size: .85rem;
}
.drawer-close:hover { background: rgba(255,255,255,0.35); }
.drawer-title { font-weight: 600; }
.drawer-struct { font-size: 1.3rem; margin-left: .4rem; }
.drawer-status, .drawer-error { padding: 1rem; text-align: center; color: #6b4f3c; }
.drawer-body {
  flex: 1; overflow-y: auto; padding: 1rem 1.4rem 2rem;
}
.drawer-meta {
  display: flex; gap: 1.2rem; padding-bottom: 1rem; border-bottom: 1px solid #e7c490; margin-bottom: 1rem;
}
.meta-info { flex: 1; font-size: .88rem; color: #4b3621; }
.meta-info p { margin: .2rem 0; }
.rk { background: #fef3c7; padding: 1px 5px; border-radius: 3px; margin-right: 4px; font-size: .75rem; }
.depth-warn { background: #fef3c7; padding: .35rem .55rem; border-left: 3px solid #d97706; font-size: .8rem; }

/* Markdown content styles */
.drawer-markdown :deep(h1) { font-size: 1.35rem; color: #7c2d12; margin: 1rem 0 .5rem; }
.drawer-markdown :deep(h2) { font-size: 1.15rem; color: #92400e; margin: 1rem 0 .5rem; border-bottom: 1px solid #e7c490; padding-bottom: .2rem; }
.drawer-markdown :deep(h3) { font-size: 1.02rem; color: #92400e; margin: .8rem 0 .4rem; }
.drawer-markdown :deep(p) { line-height: 1.65; color: #4b3621; margin: .4rem 0; }
.drawer-markdown :deep(blockquote) {
  background: #fef3c7; border-left: 3px solid #d4a574; padding: .55rem .8rem;
  margin: .55rem 0; font-style: italic; color: #6b4f3c; line-height: 1.55;
}
.drawer-markdown :deep(ul) { padding-left: 1.3rem; line-height: 1.6; }
.drawer-markdown :deep(li) { margin: .15rem 0; }
.drawer-markdown :deep(code) { background: #f3e8c0; padding: 1px 5px; border-radius: 3px; font-family: monospace; font-size: .85rem; }
.drawer-markdown :deep(b) { color: #7c2d12; }
.drawer-markdown :deep(hr) { border: 0; border-top: 1px dashed #d4a574; margin: 1rem 0; }
.drawer-markdown :deep(.md-table) {
  border-collapse: collapse; margin: .8rem 0; font-size: .85rem; width: 100%;
}
.drawer-markdown :deep(.md-table th), .drawer-markdown :deep(.md-table td) {
  border: 1px solid #e7c490; padding: .35rem .55rem; vertical-align: top;
}
.drawer-markdown :deep(.md-table th) { background: #fef3c7; }
.drawer-markdown :deep(a) { color: #92400e; }

/* Mobile */
@media (max-width: 768px) {
  .kdb-drawer { width: 100%; max-width: none; }
  .kdb-grid { font-size: .7rem; }
  .cell-inner { padding: .15rem .05rem; }
  .cell-name { font-size: .55rem; }
}
</style>
