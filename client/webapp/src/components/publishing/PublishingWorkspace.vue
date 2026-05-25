<script setup>
/**
 * PublishingWorkspace — UI dịch sách layout-aware, line-level.
 *
 * 3-pane:
 *   LEFT  — Page image + bbox overlay (regions outer, lines inner)
 *   MID   — Region list with collapsible lines
 *   RIGHT — Per-line translation editor (side-by-side Trung-Việt per dòng)
 *
 * Backend: /api/yi-publishing/* — reads MinerU middle.json (lines preserved)
 */
import { ref, computed, watch, onMounted } from "vue";

const props = defineProps({
  bookId: { type: String, default: null },  // if set, load this book directly
});
const emit = defineEmits(["back"]);

const books = ref([]);
const selectedBook = ref(props.bookId || null);
const currentBookMeta = ref(null);  // full metadata from /books endpoint

function goBackToLibrary() {
  emit("back");
}
const pages = ref([]);
const selectedPage = ref(1);
const layout = ref(null);
const selectedRegionIdx = ref(0);
const selectedLineIdx = ref(0);  // -1 = no line selected (region-level)
const loading = ref(false);
const saving = ref(false);
const error = ref("");

const lineDrafts = ref({});  // local edits before save: { line_id: text_vi }
const lineStatuses = ref({});  // local status edits: { line_id: status }

// Redraw state
const redrawing = ref(false);
const redrawnVersions = ref([]);
const redrawContext = ref("");
const redrawStyle = ref("traditional Chinese ink painting, clean line art, balanced composition");

// Auto-translate state
const autoTranslating = ref(false);
const autoTranslateResult = ref(null);

// Term-catch state (highlight Chinese → add to wiki)
const termCatchVisible = ref(false);
const termCatchSelected = ref("");
const termCatchLookup = ref(null);  // null | {matches: []}
const termCatchForm = ref({ canonical_vi: "", short_note: "", aliases: "" });
const termCatchSaving = ref(false);
const termCatchResult = ref(null);

// View mode: 'editor' | 'compare' | 'auto'
const viewMode = ref("editor");

// AUTO batch state
const autoBatchRunning = ref(false);
const autoBatchStart = ref(1);
const autoBatchEnd = ref(10);
const autoBatchOverwrite = ref(false);
const autoBatchAllowPaid = ref(true);  // default ON — better quality
const autoBatchResult = ref(null);
const autoBatchProgress = ref({ current: 0, total: 0 });
const translatorStatus = ref(null);  // {free_chain, paid_chain, paid_fallback_available}

async function loadTranslatorStatus() {
  try {
    const r = await fetch("/api/yi-publishing/translator/status");
    translatorStatus.value = await r.json();
  } catch (e) {
    translatorStatus.value = null;
  }
}

async function runAutoBatch() {
  if (!selectedBook.value || autoBatchRunning.value) return;
  autoBatchRunning.value = true;
  autoBatchResult.value = null;
  autoBatchProgress.value = {
    current: 0,
    total: autoBatchEnd.value - autoBatchStart.value + 1,
  };
  try {
    const r = await fetch(
      `/api/yi-publishing/books/${selectedBook.value}/auto-batch`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_page: autoBatchStart.value,
          end_page: autoBatchEnd.value,
          overwrite: autoBatchOverwrite.value,
          allow_paid_fallback: autoBatchAllowPaid.value,
          delay_seconds: 2.0,
          retry_on_429: 2,
        }),
      }
    );
    const d = await r.json();
    autoBatchResult.value = d;
  } catch (e) {
    autoBatchResult.value = { status: "error", message: e.message };
  } finally {
    autoBatchRunning.value = false;
  }
}

function verdictLabel(v) {
  return (
    { fit: "✓ Khớp", review: "⚠ Cần soát", mismatch: "✗ Lệch", skip: "— Skip" }[v] ||
    v ||
    "?"
  );
}

function verdictClass(v) {
  return `pw-verdict-${v || "unknown"}`;
}

// Compare helpers: join translated lines or fallback to source
function joinRegionVi(region) {
  if (!region?.lines) return "";
  return region.lines
    .map((l) => l.translation?.text_vi || "")
    .filter((t) => t.trim())
    .join(" ");
}

function joinRegionZh(region) {
  if (!region?.lines) return "";
  return region.lines.map((l) => l.source_text || "").join(" ");
}

const compareTotalLines = computed(() => {
  if (!layout.value?.regions) return 0;
  return layout.value.regions.reduce((n, r) => n + (r.lines?.length || 0), 0);
});

const compareTranslatedCount = computed(() => {
  if (!layout.value?.regions) return 0;
  return layout.value.regions.reduce(
    (n, r) => n + (r.lines?.filter((l) => l.translation?.text_vi).length || 0),
    0
  );
});

const compareCoveragePct = computed(() => {
  const t = compareTotalLines.value;
  if (!t) return 0;
  return Math.round((compareTranslatedCount.value / t) * 100);
});

const REGION_COLORS = {
  title: "#dc2626",
  text: "#2563eb",
  paragraph: "#2563eb",
  list: "#0891b2",
  image: "#16a34a",
  table: "#7c3aed",
  page_header: "#94a3b8",
  page_footer: "#94a3b8",
  page_number: "#94a3b8",
};

const REGION_LABELS = {
  title: "Tiêu đề",
  text: "Đoạn văn",
  paragraph: "Đoạn văn",
  list: "Danh sách",
  image: "Hình",
  table: "Bảng",
  page_header: "Đầu trang",
  page_footer: "Cuối trang",
  page_number: "Số trang",
};

// Computed
const selectedRegion = computed(() => {
  if (!layout.value?.regions) return null;
  return layout.value.regions[selectedRegionIdx.value] || null;
});

const pageImageUrl = computed(() => {
  if (!selectedBook.value) return "";
  return `/api/yi-publishing/pages/${selectedBook.value}/${selectedPage.value}/image`;
});

const imagePath = computed(() => {
  const r = selectedRegion.value;
  if (r?.type !== "image") return null;
  const p = r.image_path;
  if (!p) return null;
  const filename = p.split("/").pop();
  return `/api/yi-publishing/images/${selectedBook.value}/${filename}`;
});

// Loading
async function loadBooks() {
  loading.value = true;
  try {
    const d = await (await fetch("/api/yi-publishing/books")).json();
    if (d.status === "ok") {
      books.value = d.books;
      if (books.value.length && !selectedBook.value) {
        selectedBook.value = books.value[0].book_id;
      }
      // Cache current book metadata for header display
      currentBookMeta.value = books.value.find(b => b.book_id === selectedBook.value) || null;
    }
  } catch (e) {
    error.value = "Load books: " + e.message;
  } finally {
    loading.value = false;
  }
}

// Keep currentBookMeta in sync with selectedBook
watch(selectedBook, (id) => {
  currentBookMeta.value = books.value.find(b => b.book_id === id) || null;
});

async function loadPages() {
  if (!selectedBook.value) return;
  try {
    const d = await (await fetch(`/api/yi-publishing/books/${selectedBook.value}/pages`)).json();
    if (d.status === "ok") {
      pages.value = d.pages;
      if (!pages.value.find(p => p.page_num === selectedPage.value)) {
        selectedPage.value = pages.value[0]?.page_num || 1;
      }
    }
  } catch (e) {
    error.value = "Load pages: " + e.message;
  }
}

async function loadLayout() {
  if (!selectedBook.value) return;
  loading.value = true;
  selectedRegionIdx.value = 0;
  selectedLineIdx.value = 0;
  lineDrafts.value = {};
  lineStatuses.value = {};
  try {
    const d = await (await fetch(`/api/yi-publishing/pages/${selectedBook.value}/${selectedPage.value}`)).json();
    if (d.status === "ok") {
      layout.value = d;
    } else {
      error.value = d.message || "Load fail";
    }
  } catch (e) {
    error.value = "Load layout: " + e.message;
  } finally {
    loading.value = false;
  }
}

function selectRegion(idx) {
  selectedRegionIdx.value = idx;
  selectedLineIdx.value = 0;
}

function selectLine(rIdx, lIdx) {
  selectedRegionIdx.value = rIdx;
  selectedLineIdx.value = lIdx;
}

function getLineDraft(line) {
  if (line.line_id in lineDrafts.value) return lineDrafts.value[line.line_id];
  return line.translation?.text_vi || "";
}

function getLineStatus(line) {
  if (line.line_id in lineStatuses.value) return lineStatuses.value[line.line_id];
  return line.translation?.status || "draft";
}

function setLineDraft(lineId, text) {
  lineDrafts.value = { ...lineDrafts.value, [lineId]: text };
}

function setLineStatus(lineId, status) {
  lineStatuses.value = { ...lineStatuses.value, [lineId]: status };
}

function isLineDirty(line) {
  return (line.line_id in lineDrafts.value) || (line.line_id in lineStatuses.value);
}

async function saveLine(region, line) {
  if (saving.value) return;
  saving.value = true;
  try {
    const r = await fetch(
      `/api/yi-publishing/regions/${selectedBook.value}/${selectedPage.value}/${region.region_id}/lines/${line.line_id}/translation`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text_vi: getLineDraft(line),
          status: getLineStatus(line),
          translator: "human",
        }),
      }
    );
    const d = await r.json();
    if (d.status === "ok") {
      // Clear drafts for this line, reload
      delete lineDrafts.value[line.line_id];
      delete lineStatuses.value[line.line_id];
      lineDrafts.value = { ...lineDrafts.value };
      lineStatuses.value = { ...lineStatuses.value };
      await loadLayout();
    } else {
      error.value = "Save: " + (d.message || "fail");
    }
  } catch (e) {
    error.value = "Save: " + e.message;
  } finally {
    saving.value = false;
  }
}

// Bbox → SVG percentage scale
function bboxStyle(bbox) {
  if (!layout.value || !bbox) return "";
  const w = layout.value.page_width || 920;
  const h = layout.value.page_height || 1300;
  const x = (bbox[0] / w) * 100;
  const y = (bbox[1] / h) * 100;
  const bw = ((bbox[2] - bbox[0]) / w) * 100;
  const bh = ((bbox[3] - bbox[1]) / h) * 100;
  return `left: ${x}%; top: ${y}%; width: ${bw}%; height: ${bh}%;`;
}

// Term-catch functions
async function openTermCatch(selectedText) {
  if (!selectedText || !selectedText.trim()) return;
  termCatchSelected.value = selectedText.trim();
  termCatchVisible.value = true;
  termCatchForm.value = { canonical_vi: "", short_note: "", aliases: "" };
  termCatchResult.value = null;

  // Lookup existing
  try {
    const r = await fetch(
      `/api/yi-publishing/wiki/lookup?zh=${encodeURIComponent(termCatchSelected.value)}`
    );
    termCatchLookup.value = await r.json();
  } catch (e) {
    termCatchLookup.value = { matches: [] };
  }
}

function closeTermCatch() {
  termCatchVisible.value = false;
  termCatchSelected.value = "";
  termCatchLookup.value = null;
  termCatchResult.value = null;
}

async function saveTermCatch() {
  if (!termCatchForm.value.canonical_vi.trim()) {
    error.value = "Cần điền tên tiếng Việt cho thuật ngữ";
    return;
  }
  termCatchSaving.value = true;
  try {
    const r = await fetch("/api/yi-publishing/wiki/concepts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        canonical_zh: termCatchSelected.value,
        canonical_vi: termCatchForm.value.canonical_vi.trim(),
        short_note: termCatchForm.value.short_note.trim(),
        aliases: termCatchForm.value.aliases.trim(),
        book_id: selectedBook.value,
        page_num: selectedPage.value,
      }),
    });
    const d = await r.json();
    termCatchResult.value = d;
    if (d.status === "ok") {
      setTimeout(closeTermCatch, 1500);
    }
  } catch (e) {
    error.value = "Save term: " + e.message;
  } finally {
    termCatchSaving.value = false;
  }
}

// Listen for text selection in source-text panes
function handleTextSelection(event) {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  if (text && text.length >= 1 && text.length <= 30) {
    // Only catch if selection is inside a source text element
    let node = selection.anchorNode;
    while (node && node.nodeType !== 1) node = node.parentNode;
    if (node && (node.closest('.pw-source-text') || node.closest('.pw-line-text'))) {
      openTermCatch(text);
    }
  }
}

// Auto-translate functions
async function autoTranslatePage(overwrite = false) {
  if (autoTranslating.value || !selectedBook.value) return;
  autoTranslating.value = true;
  autoTranslateResult.value = null;
  try {
    const r = await fetch(
      `/api/yi-publishing/pages/${selectedBook.value}/${selectedPage.value}/auto-translate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ overwrite }),
      }
    );
    const d = await r.json();
    autoTranslateResult.value = d;
    if (d.status === "ok") {
      await loadLayout();  // reload with new translations
    } else {
      error.value = "Auto-translate: " + (d.message || "fail");
    }
  } catch (e) {
    error.value = "Auto-translate: " + e.message;
  } finally {
    autoTranslating.value = false;
  }
}

// Redraw functions
async function loadRedrawnVersions() {
  if (!selectedRegion.value || selectedRegion.value.type !== "image") {
    redrawnVersions.value = [];
    return;
  }
  try {
    const d = await (await fetch(
      `/api/yi-publishing/regions/${selectedBook.value}/${selectedPage.value}/${selectedRegion.value.region_id}/redrawn`
    )).json();
    redrawnVersions.value = d.versions || [];
  } catch (e) {
    redrawnVersions.value = [];
  }
}

function buildRedrawContext() {
  // Get neighboring text regions for context
  if (!layout.value?.regions) return "";
  const myIdx = selectedRegionIdx.value;
  const before = layout.value.regions.slice(Math.max(0, myIdx - 2), myIdx);
  const after = layout.value.regions.slice(myIdx + 1, myIdx + 3);
  const texts = [];
  for (const r of [...before, ...after]) {
    if (r.lines) {
      for (const line of r.lines) {
        if (line.source_text) texts.push(line.source_text);
      }
    }
  }
  return texts.join(" ").substring(0, 400);
}

async function redrawImage() {
  if (!selectedRegion.value || redrawing.value) return;
  redrawing.value = true;
  try {
    const ctx = redrawContext.value || buildRedrawContext();
    const r = await fetch(
      `/api/yi-publishing/regions/${selectedBook.value}/${selectedPage.value}/${selectedRegion.value.region_id}/redraw`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          context_text: ctx,
          style: redrawStyle.value,
          width: 768,
          height: 1024,
        }),
      }
    );
    const d = await r.json();
    if (d.status === "ok") {
      await loadRedrawnVersions();
    } else {
      error.value = "Redraw: " + (d.message || "fail");
    }
  } catch (e) {
    error.value = "Redraw: " + e.message;
  } finally {
    redrawing.value = false;
  }
}

function redrawnImageUrl(filename) {
  return `/api/yi-publishing/redrawn/${selectedBook.value}/${filename}`;
}

watch(selectedBook, () => { loadPages(); loadLayout(); });
watch(selectedPage, () => { loadLayout(); });
watch(selectedRegionIdx, () => {
  if (selectedRegion.value?.type === "image") {
    redrawContext.value = buildRedrawContext();
    loadRedrawnVersions();
  }
});
onMounted(() => {
  loadBooks();
  loadTranslatorStatus();
});
</script>

<template>
  <div class="publishing-workspace">
    <header class="pw-header">
      <div class="pw-title-row">
        <button type="button" class="pw-back-btn" @click="goBackToLibrary" title="Về thư viện">
          ← Thư viện
        </button>
        <h2 class="pw-title">
          📖 <strong>{{ currentBookMeta?.title_vi || selectedBook || "Dịch sách" }}</strong>
          <span v-if="currentBookMeta?.hanzi_title" class="pw-zh">{{ currentBookMeta.hanzi_title }}</span>
          <span v-if="currentBookMeta?.stage_label" class="pw-stage-badge">
            🏷️ Stage {{ currentBookMeta.stage }}: {{ currentBookMeta.stage_label }}
          </span>
        </h2>
      </div>
      <div class="pw-toolbar">
        <select v-if="!props.bookId" v-model="selectedBook" class="pw-select">
          <option v-for="b in books" :key="b.book_id" :value="b.book_id">
            {{ b.title_vi || b.book_id }} ({{ b.page_count }} trang)
          </option>
        </select>
        <span class="pw-page-nav">
          <button @click="selectedPage = Math.max(1, selectedPage - 1)"
                  :disabled="selectedPage <= 1">←</button>
          <input type="number" v-model.number="selectedPage" min="1"
                 :max="pages.length" class="pw-page-input"/>
          <span>/ {{ pages.length }}</span>
          <button @click="selectedPage = Math.min(pages.length, selectedPage + 1)"
                  :disabled="selectedPage >= pages.length">→</button>
        </span>
        <span v-if="layout" class="pw-stats">
          {{ layout.regions?.length || 0 }} regions
          · {{ layout.regions?.reduce((n, r) => n + (r.lines?.length || 0), 0) || 0 }} lines
        </span>
        <button @click="autoTranslatePage(false)" :disabled="autoTranslating"
                class="pw-auto-trans-btn"
                title="Tự dịch các dòng chưa có bản Việt (free, DeepSeek)">
          {{ autoTranslating ? "🤖 Đang dịch..." : "🤖 Tự dịch trang" }}
        </button>
        <span v-if="autoTranslateResult?.status === 'ok'" class="pw-stats" style="color: #34d399;">
          ✓ {{ autoTranslateResult.total_lines_translated }} dòng
          · {{ autoTranslateResult.elapsed_seconds?.toFixed(1) }}s
        </span>
        <span v-if="loading" class="pw-loading">Loading...</span>
        <span v-if="error" class="pw-error">{{ error }}</span>
        <div class="pw-view-toggle">
          <button :class="{ active: viewMode === 'editor' }" @click="viewMode = 'editor'"
                  title="3-pane line editor">✍️ Editor</button>
          <button :class="{ active: viewMode === 'compare' }" @click="viewMode = 'compare'"
                  title="Side-by-side book preview">📑 Đối chiếu</button>
          <button :class="{ active: viewMode === 'auto' }" @click="viewMode = 'auto'"
                  title="Auto-batch translate with quality warnings">🤖 Auto</button>
        </div>
      </div>
    </header>

    <div class="pw-main" v-if="viewMode === 'editor'">
      <!-- LEFT: Page image with bbox overlay (regions + lines) -->
      <div class="pw-pane pw-pane-image">
        <div class="pw-image-container" v-if="selectedBook">
          <img :src="pageImageUrl" :key="`${selectedBook}-${selectedPage}`"
               class="pw-page-image" alt="Page image"/>

          <!-- Region bboxes -->
          <div v-if="layout?.regions" class="pw-overlay-container">
            <div v-for="(r, idx) in layout.regions" :key="`r-${idx}`"
                 class="pw-region-box"
                 :class="{ 'selected': idx === selectedRegionIdx }"
                 :style="bboxStyle(r.bbox) + `--c: ${REGION_COLORS[r.type] || '#666'};`"
                 @click="selectRegion(idx)"
                 :title="`${REGION_LABELS[r.type]} (${r.lines?.length || 0} lines)`">
              <span class="pw-region-label" :style="`background: ${REGION_COLORS[r.type] || '#666'};`">
                #{{ idx + 1 }} {{ REGION_LABELS[r.type] || r.type }}
              </span>
            </div>
            <!-- Line bboxes inside selected region -->
            <template v-if="selectedRegion?.lines">
              <div v-for="(line, lIdx) in selectedRegion.lines" :key="line.line_id"
                   class="pw-line-box"
                   :class="{ 'selected': lIdx === selectedLineIdx, 'translated': line.translation }"
                   :style="bboxStyle(line.bbox)"
                   @click.stop="selectLine(selectedRegionIdx, lIdx)"
                   :title="`Line ${lIdx + 1}`">
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- MID: Region list with line counts -->
      <div class="pw-pane pw-pane-list">
        <h3>Regions / Lines</h3>
        <div class="pw-region-list">
          <div v-for="(r, idx) in layout?.regions || []" :key="idx"
               class="pw-region-card"
               :class="{ 'active': idx === selectedRegionIdx }">
            <button class="pw-region-head" @click="selectRegion(idx)">
              <span class="pw-region-num">#{{ idx + 1 }}</span>
              <span class="pw-region-type"
                    :style="{ background: REGION_COLORS[r.type] || '#666' }">
                {{ REGION_LABELS[r.type] || r.type }}
              </span>
              <span v-if="r.lines?.length" class="pw-line-count">
                {{ r.lines.length }} dòng
              </span>
            </button>
            <!-- Lines within region (only when selected) -->
            <div v-if="idx === selectedRegionIdx && r.lines?.length"
                 class="pw-line-list">
              <button v-for="(line, lIdx) in r.lines" :key="line.line_id"
                      class="pw-line-item"
                      :class="{ 'active': lIdx === selectedLineIdx,
                                'translated': line.translation,
                                'dirty': isLineDirty(line) }"
                      @click="selectLine(idx, lIdx)">
                <span class="pw-line-num">{{ lIdx + 1 }}</span>
                <span class="pw-line-text">{{ line.source_text.substring(0, 35) }}</span>
                <span v-if="line.translation" class="pw-line-status">✓</span>
                <span v-if="isLineDirty(line)" class="pw-line-status pw-dirty">●</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Per-line editor -->
      <div class="pw-pane pw-pane-editor">
        <h3 v-if="selectedRegion">
          Bản dịch — {{ selectedRegion.region_id }}
          <span class="pw-region-id">
            ({{ REGION_LABELS[selectedRegion.type] }}, {{ selectedRegion.lines?.length || 0 }} dòng)
          </span>
        </h3>

        <div v-if="!selectedRegion" class="pw-empty">
          Chọn region từ ảnh hoặc danh sách bên cạnh.
        </div>

        <!-- Image region — show extracted image + AI redraw -->
        <div v-else-if="selectedRegion.type === 'image' && imagePath" class="pw-image-preview">
          <label>Hình gốc tách ra:</label>
          <img :src="imagePath" alt="Region image" class="pw-region-img"/>

          <!-- AI Redraw section -->
          <div class="pw-redraw-section">
            <label>🎨 Vẽ lại bằng AI (FLUX.1 schnell):</label>
            <textarea v-model="redrawContext" rows="3"
                      placeholder="Ngữ cảnh để AI vẽ (lấy tự động từ paragraphs xung quanh)..."
                      class="pw-redraw-context"></textarea>
            <input v-model="redrawStyle" type="text"
                   placeholder="Style: traditional Chinese ink painting, ..."
                   class="pw-redraw-style"/>
            <button @click="redrawImage" :disabled="redrawing" class="pw-redraw-btn">
              {{ redrawing ? "🎨 Đang vẽ (~2 phút)..." : "🎨 Vẽ lại" }}
            </button>

            <!-- Redrawn versions -->
            <div v-if="redrawnVersions.length" class="pw-redrawn-grid">
              <h4>Phiên bản đã vẽ ({{ redrawnVersions.length }}):</h4>
              <div class="pw-redrawn-list">
                <div v-for="v in redrawnVersions" :key="v.filename" class="pw-redrawn-card">
                  <img :src="redrawnImageUrl(v.filename)" :alt="v.filename" class="pw-redrawn-img"/>
                  <div class="pw-redrawn-meta">
                    <strong>v{{ v.seq }}</strong>
                    <span v-if="v.elapsed_seconds">· {{ Math.round(v.elapsed_seconds) }}s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Text region — per-line editor -->
        <div v-else-if="selectedRegion.lines?.length" class="pw-lines-editor">
          <div v-for="(line, lIdx) in selectedRegion.lines" :key="line.line_id"
               class="pw-line-edit-card"
               :class="{ 'active': lIdx === selectedLineIdx }"
               @click="selectedLineIdx = lIdx">

            <div class="pw-line-edit-head">
              <span class="pw-line-edit-num">Dòng {{ lIdx + 1 }}</span>
              <span class="pw-line-edit-id">{{ line.line_id }}</span>
              <span v-if="line.translation" class="pw-line-edit-meta">
                v{{ line.translation.version }} · {{ line.translation.status }}
              </span>
            </div>

            <pre class="pw-source-text" @mouseup="handleTextSelection"
                 title="Tô chọn chữ Hán để thêm vào Wiki">{{ line.source_text }}</pre>

            <textarea
              :value="getLineDraft(line)"
              @input="setLineDraft(line.line_id, $event.target.value)"
              rows="2"
              placeholder="Dịch dòng này..."
              class="pw-line-textarea"
            ></textarea>

            <div class="pw-line-toolbar">
              <select :value="getLineStatus(line)"
                      @change="setLineStatus(line.line_id, $event.target.value)"
                      class="pw-trans-status">
                <option value="pending">⏳ Chờ</option>
                <option value="auto">🤖 Tự</option>
                <option value="draft">✏️ Nháp</option>
                <option value="reviewed">👁 Review</option>
                <option value="approved">✅ Duyệt</option>
              </select>
              <button @click="saveLine(selectedRegion, line)"
                      :disabled="saving || !isLineDirty(line)"
                      class="pw-save-btn">
                {{ saving ? "..." : "💾 Lưu dòng" }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="pw-empty">
          Region này không có lines (vd: page_header, page_number).
        </div>
      </div>
    </div>

    <!-- COMPARE MODE: book-style side-by-side -->
    <div class="pw-compare" v-else-if="viewMode === 'compare'">
      <!-- LEFT: full page scan -->
      <div class="pw-compare-source">
        <div class="pw-compare-pane-head">原文 — Bản gốc (trang {{ selectedPage }})</div>
        <div class="pw-compare-scan">
          <img v-if="selectedBook" :src="pageImageUrl"
               :key="`cmp-${selectedBook}-${selectedPage}`"
               class="pw-compare-img" alt="Source page"/>
        </div>
      </div>

      <!-- RIGHT: rendered Vietnamese book layout -->
      <div class="pw-compare-target">
        <div class="pw-compare-pane-head">
          Bản Việt
          <span class="pw-compare-stats" v-if="layout">
            · {{ compareTranslatedCount }} / {{ compareTotalLines }} dòng đã dịch
            · {{ compareCoveragePct }}%
          </span>
        </div>
        <div class="pw-compare-book" @mouseup="handleTextSelection">
          <template v-if="layout?.regions">
            <template v-for="(r, idx) in layout.regions" :key="`cmp-r-${idx}`">

              <!-- Headings -->
              <h1 v-if="r.type === 'title' && (idx < 2)" class="pw-cmp-h1">
                {{ joinRegionVi(r) || joinRegionZh(r) }}
              </h1>
              <h2 v-else-if="r.type === 'title'" class="pw-cmp-h2">
                {{ joinRegionVi(r) || joinRegionZh(r) }}
              </h2>

              <!-- Paragraph (line-by-line for traceability) -->
              <div v-else-if="r.type === 'text' || r.type === 'paragraph'"
                   class="pw-cmp-para">
                <div v-for="(line, li) in r.lines || []" :key="line.line_id"
                     class="pw-cmp-line"
                     :class="{ 'pw-cmp-untranslated': !line.translation }">
                  <div class="pw-cmp-line-vi" v-if="line.translation?.text_vi">
                    {{ line.translation.text_vi }}
                  </div>
                  <div class="pw-cmp-line-vi pw-cmp-line-empty" v-else>
                    [chưa dịch] <span class="pw-cmp-line-zh-inline">{{ line.source_text }}</span>
                  </div>
                </div>
              </div>

              <!-- Lists -->
              <ul v-else-if="r.type === 'list'" class="pw-cmp-list">
                <li v-for="(line, li) in r.lines || []" :key="line.line_id"
                    :class="{ 'pw-cmp-untranslated': !line.translation }">
                  {{ line.translation?.text_vi || `[chưa dịch] ${line.source_text}` }}
                </li>
              </ul>

              <!-- Image regions -->
              <figure v-else-if="r.type === 'image'" class="pw-cmp-figure">
                <img v-if="r.image_path"
                     :src="`/api/yi-publishing/images/${selectedBook}/${r.image_path.split('/').pop()}`"
                     class="pw-cmp-figure-img" :alt="r.region_id"/>
                <figcaption v-if="(r.lines || []).length">
                  {{ joinRegionVi(r) || joinRegionZh(r) }}
                </figcaption>
              </figure>

              <!-- Table placeholder -->
              <div v-else-if="r.type === 'table'" class="pw-cmp-table">
                📊 Bảng [{{ r.region_id }}]
                <div class="pw-cmp-table-content">
                  <div v-for="(line, li) in r.lines || []" :key="line.line_id">
                    {{ line.translation?.text_vi || line.source_text }}
                  </div>
                </div>
              </div>

              <!-- Footer/header/page number — small muted -->
              <div v-else-if="['page_header', 'page_footer', 'page_number'].includes(r.type)"
                   class="pw-cmp-meta">
                {{ joinRegionVi(r) || joinRegionZh(r) }}
              </div>

              <!-- Fallback -->
              <div v-else class="pw-cmp-fallback">
                <em>[{{ r.type }}]</em>
                {{ joinRegionVi(r) || joinRegionZh(r) }}
              </div>
            </template>
          </template>
          <div v-else class="pw-empty">Chưa có layout cho trang này.</div>
        </div>
      </div>
    </div>

    <!-- AUTO MODE: batch translate with quality warnings -->
    <div class="pw-auto" v-else-if="viewMode === 'auto'">
      <div class="pw-auto-controls">
        <h3>🤖 Auto-batch dịch sách</h3>
        <div class="pw-auto-form">
          <label>Từ trang <input type="number" v-model.number="autoBatchStart" min="1" /></label>
          <label>Đến trang <input type="number" v-model.number="autoBatchEnd" min="1" /></label>
          <label class="pw-auto-check">
            <input type="checkbox" v-model="autoBatchOverwrite" />
            Ghi đè bản dịch cũ
          </label>
          <label class="pw-auto-check pw-auto-paid"
                 :class="{ 'pw-disabled': !translatorStatus?.paid_fallback_available }"
                 :title="translatorStatus?.paid_fallback_available
                         ? 'Khi free chain fail → escalate sang DeepSeek paid ($0.27/M in, $1.10/M out)'
                         : 'Cần add DeepSeek API key vào data/ai_keys.json hoặc tab ⚙️ Cài đặt'">
            <input type="checkbox" v-model="autoBatchAllowPaid"
                   :disabled="!translatorStatus?.paid_fallback_available" />
            💰 Cho phép fallback DeepSeek paid
            <span v-if="!translatorStatus?.paid_fallback_available" class="pw-no-key">(chưa có key)</span>
          </label>
          <button @click="runAutoBatch" :disabled="autoBatchRunning || !selectedBook"
                  class="pw-auto-run-btn">
            {{ autoBatchRunning ? "⏳ Đang chạy..." : "▶ Chạy auto-batch" }}
          </button>
        </div>
        <p class="pw-auto-help">
          ⚙️ Quy tắc <b>FIT</b> (đầu ra khớp nguyên bản): đủ số dòng, không rỗng, không trùng nguồn,
          không còn ký tự Hán, độ dài hợp lý (0.5x ≤ ratio ≤ 6x), không có lời từ chối của AI.
        </p>
        <p v-if="translatorStatus" class="pw-auto-providers">
          🔗 <b>Free chain</b>: {{ translatorStatus.free_chain?.join(" → ") }}
          <span v-if="translatorStatus.paid_fallback_available">
            <br/>💰 <b>Paid fallback</b>: deepseek-chat (DeepSeek native) ·
            <span class="pw-key-ok">✓ Key đã cấu hình</span>
          </span>
          <span v-else>
            <br/>⚠️ <span class="pw-key-missing">DeepSeek key chưa cấu hình</span> — thêm vào
            <code>data/ai_keys.json["deepseek"]</code> hoặc qua tab ⚙️ Cài đặt
          </span>
        </p>
      </div>

      <!-- Summary card -->
      <div v-if="autoBatchResult?.summary" class="pw-auto-summary">
        <div class="pw-auto-summary-row">
          <div class="pw-auto-stat">
            <div class="pw-auto-stat-label">Trang xử lý</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.pages_processed }}</div>
          </div>
          <div class="pw-auto-stat">
            <div class="pw-auto-stat-label">Dòng dịch</div>
            <div class="pw-auto-stat-value">
              {{ autoBatchResult.summary.total_lines_translated }}/{{ autoBatchResult.summary.total_lines_attempted }}
            </div>
          </div>
          <div class="pw-auto-stat" :class="{ 'pw-stat-good': autoBatchResult.summary.avg_fit_score >= 90 }">
            <div class="pw-auto-stat-label">Điểm FIT</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.avg_fit_score }}%</div>
          </div>
          <div class="pw-auto-stat" :class="{ 'pw-stat-bad': autoBatchResult.summary.total_errors > 0 }">
            <div class="pw-auto-stat-label">Lỗi</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.total_errors }}</div>
          </div>
          <div class="pw-auto-stat" :class="{ 'pw-stat-warn': autoBatchResult.summary.total_warnings > 0 }">
            <div class="pw-auto-stat-label">Cảnh báo</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.total_warnings }}</div>
          </div>
          <div class="pw-auto-stat">
            <div class="pw-auto-stat-label">Thời gian</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.batch_elapsed_seconds }}s</div>
          </div>
          <div class="pw-auto-stat" :class="{ 'pw-stat-warn': autoBatchResult.summary.paid_pages_count > 0 }">
            <div class="pw-auto-stat-label">Paid pages</div>
            <div class="pw-auto-stat-value">{{ autoBatchResult.summary.paid_pages_count || 0 }}</div>
          </div>
          <div class="pw-auto-stat" :class="{ 'pw-stat-warn': (autoBatchResult.summary.total_cost_usd || 0) > 0 }">
            <div class="pw-auto-stat-label">Chi phí</div>
            <div class="pw-auto-stat-value">${{ (autoBatchResult.summary.total_cost_usd || 0).toFixed(4) }}</div>
          </div>
        </div>
      </div>

      <!-- Per-page table -->
      <div v-if="autoBatchResult?.pages" class="pw-auto-table-wrap">
        <table class="pw-auto-table">
          <thead>
            <tr>
              <th>Trang</th>
              <th>Verdict</th>
              <th>Dòng</th>
              <th>FIT</th>
              <th>Lỗi</th>
              <th>Warn</th>
              <th>Thời gian</th>
              <th>Provider</th>
              <th>Model</th>
              <th>Cost</th>
              <th>Vấn đề</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in autoBatchResult.pages" :key="p.page_num"
                :class="verdictClass(p.verdict)">
              <td>
                <button class="pw-auto-page-link"
                        @click="viewMode = 'compare'; selectedPage = p.page_num">
                  p{{ p.page_num }}
                </button>
              </td>
              <td>
                <span v-if="p.status === 'error'" class="pw-verdict-error">✗ Lỗi</span>
                <span v-else :class="verdictClass(p.verdict)">{{ verdictLabel(p.verdict) }}</span>
              </td>
              <td>{{ p.lines_translated || 0 }} / {{ p.lines_attempted || 0 }}</td>
              <td>{{ p.fit_score !== null ? p.fit_score + "%" : "—" }}</td>
              <td>{{ p.error_count || 0 }}</td>
              <td>{{ p.warn_count || 0 }}</td>
              <td>{{ p.elapsed_seconds }}s</td>
              <td class="pw-auto-provider">
                <span v-if="p.provider === 'deepseek-native'" class="pw-prov-paid">💰 paid</span>
                <span v-else-if="p.provider === 'openrouter'" class="pw-prov-free">free</span>
                <span v-else>—</span>
              </td>
              <td class="pw-auto-model">{{ p.model_used?.split("/").pop() || "—" }}</td>
              <td class="pw-auto-cost">
                {{ p.cost_usd > 0 ? `$${p.cost_usd.toFixed(5)}` : "—" }}
              </td>
              <td class="pw-auto-issues">
                <div v-if="p.message" class="pw-auto-msg-err">{{ p.message.substring(0, 80) }}…</div>
                <div v-for="(iss, ii) in p.issues || []" :key="ii" class="pw-auto-issue">
                  <span v-for="(w, wi) in iss.warnings" :key="wi"
                        :class="`pw-warn-${w.level}`">
                    [{{ w.code }}]
                  </span>
                  <span class="pw-auto-issue-prev">{{ iss.source_preview }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="autoBatchRunning" class="pw-auto-spinner">
        Đang xử lý batch... có thể mất {{ Math.round((autoBatchEnd - autoBatchStart + 1) * 8) }}s
      </div>
    </div>

    <!-- Term-catch modal -->
    <div v-if="termCatchVisible" class="pw-modal-backdrop" @click.self="closeTermCatch">
      <div class="pw-modal pw-term-modal">
        <h3>📚 Thêm thuật ngữ vào Wiki</h3>

        <div class="pw-term-selected">
          <label>Chữ Hán bạn chọn:</label>
          <div class="pw-term-zh">{{ termCatchSelected }}</div>
        </div>

        <!-- Existing matches -->
        <div v-if="termCatchLookup?.matches?.length" class="pw-term-existing">
          <label>⚠ Đã có {{ termCatchLookup.matches.length }} concept tương tự trong Wiki:</label>
          <div v-for="m in termCatchLookup.matches.slice(0, 5)" :key="m.concept_id"
               class="pw-term-existing-card">
            <div class="pw-term-existing-head">
              <strong>{{ m.canonical_vi }}</strong>
              <span v-if="m.canonical_zh">{{ m.canonical_zh }}</span>
              <span class="pw-term-id">#{{ m.concept_id }}</span>
            </div>
            <div v-if="m.short_note" class="pw-term-note">{{ m.short_note }}</div>
          </div>
        </div>

        <div v-else-if="termCatchLookup" class="pw-term-new">
          <em>✨ Chưa có trong Wiki — thêm mới:</em>
        </div>

        <!-- Add form -->
        <div class="pw-term-form">
          <label>Tên tiếng Việt (Hán-Việt):</label>
          <input v-model="termCatchForm.canonical_vi" type="text"
                 placeholder="vd: Mai Hoa, Thiệu Khang Tiết, Hà Đồ..."/>

          <label>Định nghĩa ngắn:</label>
          <textarea v-model="termCatchForm.short_note" rows="2"
                    placeholder="Giải thích 1-2 câu về thuật ngữ..."></textarea>

          <label>Aliases (cách dịch khác, cách viết tắt):</label>
          <input v-model="termCatchForm.aliases" type="text"
                 placeholder="vd: Mai Hoa Dịch Số, Mai Hoa Số"/>
        </div>

        <!-- Result message -->
        <div v-if="termCatchResult" class="pw-term-result"
             :class="termCatchResult.action === 'created' ? 'success' : 'info'">
          <template v-if="termCatchResult.action === 'created'">
            ✅ Đã thêm "{{ termCatchResult.canonical_vi }}" (#{{ termCatchResult.concept_id }}) vào Wiki
          </template>
          <template v-else-if="termCatchResult.action === 'exists'">
            ℹ Concept đã tồn tại: #{{ termCatchResult.concept_id }} — {{ termCatchResult.canonical_vi }}
          </template>
          <template v-else-if="termCatchResult.status === 'error'">
            ❌ {{ termCatchResult.message }}
          </template>
        </div>

        <div class="pw-modal-actions">
          <button @click="closeTermCatch" class="pw-modal-cancel">Đóng</button>
          <button @click="saveTermCatch"
                  :disabled="termCatchSaving || !termCatchForm.canonical_vi.trim()"
                  class="pw-modal-save">
            {{ termCatchSaving ? "Đang lưu..." : "💾 Lưu vào Wiki" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.publishing-workspace {
  display: flex;
  flex-direction: column;
  height: 85vh;
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.pw-header {
  background: #1e293b;
  padding: 0.8rem 1.2rem;
  border-bottom: 1px solid #334155;
}

.pw-header h2 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #f9a8d4;
}

.pw-title-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.pw-back-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.15s ease;
}

.pw-back-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: #64748b;
}

.pw-title {
  margin: 0;
  font-size: 1.05rem;
  color: #f9a8d4;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.pw-title strong {
  font-weight: 600;
  color: #f0e6ff;
}

.pw-zh {
  font-family: "Source Han Serif SC", "Songti SC", serif;
  font-weight: normal;
  font-size: 0.92rem;
  color: rgba(200, 180, 240, 0.75);
}

.pw-stage-badge {
  font-size: 0.74rem;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  background: rgba(168, 124, 255, 0.2);
  color: #d8c7ff;
  font-weight: 500;
}

.pw-toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
  font-size: 0.85rem;
  flex-wrap: wrap;
}

.pw-select, .pw-page-input, .pw-trans-status {
  background: #0f172a;
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 0.35rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.pw-page-input { width: 60px; text-align: center; }

.pw-page-nav button {
  background: #334155;
  color: #e2e8f0;
  border: none;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
}
.pw-page-nav button:disabled { opacity: 0.4; cursor: not-allowed; }

.pw-stats { color: #94a3b8; }
.pw-loading { color: #fbbf24; }
.pw-error { color: #ef4444; }

.pw-main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 280px 1.3fr;
  gap: 1px;
  background: #334155;
  overflow: hidden;
}

.pw-pane {
  background: #0f172a;
  overflow: auto;
  padding: 1rem;
}

.pw-pane h3 {
  margin: 0 0 0.6rem;
  font-size: 0.95rem;
  color: #c084fc;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* LEFT: Image with overlays */
.pw-pane-image {
  padding: 0.5rem;
  background: #1a2030;
}

.pw-image-container {
  position: relative;
  width: 100%;
}

.pw-page-image {
  width: 100%;
  height: auto;
  display: block;
}

.pw-overlay-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Region boxes — outer */
.pw-region-box {
  position: absolute;
  border: 2px solid var(--c, #666);
  background: var(--c, #666);
  background-color: rgba(102, 102, 102, 0.10);
  pointer-events: all;
  cursor: pointer;
  transition: all 0.15s;
  box-sizing: border-box;
}

.pw-region-box:hover {
  background-color: rgba(102, 102, 102, 0.20);
}

.pw-region-box.selected {
  border-width: 3px;
  background-color: rgba(102, 102, 102, 0.18);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.pw-region-label {
  position: absolute;
  top: -1px;
  left: -1px;
  background: var(--c);
  color: white;
  font-size: 0.65rem;
  padding: 0.05rem 0.4rem;
  font-weight: 700;
  white-space: nowrap;
}

/* Line boxes — inner (only when region selected) */
.pw-line-box {
  position: absolute;
  border: 1px dashed #fbbf24;
  background: rgba(251, 191, 36, 0.10);
  pointer-events: all;
  cursor: pointer;
  transition: all 0.15s;
  box-sizing: border-box;
}

.pw-line-box:hover {
  background: rgba(251, 191, 36, 0.25);
}

.pw-line-box.selected {
  border: 2px solid #fbbf24;
  background: rgba(251, 191, 36, 0.30);
  z-index: 10;
}

.pw-line-box.translated {
  border-color: #34d399;
  border-style: solid;
}

/* MID: Region list */
.pw-region-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.pw-region-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-left: 3px solid transparent;
  border-radius: 4px;
  overflow: hidden;
}

.pw-region-card.active {
  border-left-color: #c084fc;
  background: #2a1b4a;
}

.pw-region-head {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.65rem;
  background: transparent;
  border: none;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
  font-size: 0.85rem;
}

.pw-region-head:hover {
  background: #334155;
}

.pw-region-num {
  font-size: 0.7rem;
  color: #94a3b8;
  font-family: monospace;
}

.pw-region-type {
  font-size: 0.65rem;
  font-weight: 700;
  color: white;
  padding: 0.1rem 0.45rem;
  border-radius: 3px;
  text-transform: uppercase;
}

.pw-line-count {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-left: auto;
}

.pw-line-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid #334155;
  padding: 0.2rem 0;
}

.pw-line-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.65rem 0.3rem 1.2rem;
  background: transparent;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  text-align: left;
  font-size: 0.78rem;
}

.pw-line-item:hover {
  background: #334155;
}

.pw-line-item.active {
  background: #4c1d95;
  color: white;
}

.pw-line-num {
  font-family: monospace;
  font-size: 0.7rem;
  color: #64748b;
  min-width: 1.5rem;
}

.pw-line-text {
  flex: 1;
  font-family: 'PingFang SC', serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pw-line-status {
  color: #34d399;
  font-weight: 700;
}

.pw-line-status.pw-dirty {
  color: #fbbf24;
}

/* RIGHT: Editor */
.pw-region-id {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: none;
  letter-spacing: 0;
  margin-left: 0.5rem;
}

.pw-empty {
  color: #64748b;
  font-style: italic;
  padding: 2rem 1rem;
  text-align: center;
}

.pw-image-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pw-image-preview label {
  font-size: 0.78rem;
  color: #94a3b8;
  text-transform: uppercase;
}

.pw-region-img {
  max-width: 100%;
  max-height: 320px;
  border: 1px solid #334155;
  border-radius: 4px;
}

.pw-image-note em {
  font-size: 0.8rem;
  color: #94a3b8;
}

.pw-lines-editor {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.pw-line-edit-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-left: 3px solid #475569;
  border-radius: 4px;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s;
}

.pw-line-edit-card.active {
  border-left-color: #fbbf24;
}

.pw-line-edit-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
  font-size: 0.75rem;
}

.pw-line-edit-num {
  background: #4c1d95;
  color: white;
  padding: 0.1rem 0.45rem;
  border-radius: 3px;
  font-weight: 700;
}

.pw-line-edit-id {
  color: #64748b;
  font-family: monospace;
}

.pw-line-edit-meta {
  color: #94a3b8;
  margin-left: auto;
  font-style: italic;
}

.pw-source-text {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.45rem 0.65rem;
  border-radius: 3px;
  font-size: 0.9rem;
  color: #fde68a;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'PingFang SC', serif;
  line-height: 1.55;
  margin: 0 0 0.4rem;
}

.pw-line-textarea {
  width: 100%;
  background: #0f172a;
  border: 1px solid #475569;
  color: #f1f5f9;
  padding: 0.45rem 0.65rem;
  border-radius: 3px;
  font-size: 0.9rem;
  line-height: 1.55;
  font-family: 'Times New Roman', serif;
  resize: vertical;
  box-sizing: border-box;
}

.pw-line-toolbar {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.4rem;
}

.pw-trans-status {
  font-size: 0.78rem;
  padding: 0.25rem 0.4rem;
}

.pw-save-btn {
  background: linear-gradient(135deg, #6b21a8, #9333ea);
  color: white;
  border: none;
  padding: 0.35rem 0.85rem;
  border-radius: 3px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.pw-save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pw-auto-trans-btn {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.pw-auto-trans-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: linear-gradient(135deg, #475569, #64748b);
}

/* Redraw section */
.pw-redraw-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px dashed #475569;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pw-redraw-context {
  width: 100%;
  background: #0f172a;
  border: 1px solid #475569;
  color: #fde68a;
  padding: 0.4rem 0.6rem;
  border-radius: 3px;
  font-size: 0.85rem;
  font-family: 'PingFang SC', serif;
  box-sizing: border-box;
  resize: vertical;
}

.pw-redraw-style {
  width: 100%;
  background: #0f172a;
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 0.4rem 0.6rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-style: italic;
  box-sizing: border-box;
}

.pw-redraw-btn {
  background: linear-gradient(135deg, #ea580c, #dc2626);
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  align-self: flex-start;
}

.pw-redraw-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: linear-gradient(135deg, #6b21a8, #9333ea);
}

.pw-redrawn-grid {
  margin-top: 1rem;
}

.pw-redrawn-grid h4 {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
  color: #fbbf24;
}

.pw-redrawn-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.6rem;
}

.pw-redrawn-card {
  background: #1e293b;
  border: 1px solid #475569;
  border-radius: 4px;
  overflow: hidden;
}

.pw-redrawn-img {
  width: 100%;
  height: auto;
  display: block;
}

.pw-redrawn-meta {
  padding: 0.3rem 0.45rem;
  font-size: 0.7rem;
  color: #94a3b8;
}

/* ============================================================
   Term-catch modal (B — bắt thuật ngữ vào wiki)
   ============================================================ */
.pw-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.pw-modal {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1.25rem;
  max-width: 560px;
  width: 92%;
  max-height: 88vh;
  overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
}

.pw-term-modal h3 {
  margin: 0 0 0.9rem 0;
  font-size: 1.05rem;
  color: #e2e8f0;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.pw-term-selected {
  margin-bottom: 0.85rem;
}

.pw-term-selected label {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.3rem;
}

.pw-term-zh {
  background: #1e293b;
  border: 1px solid #475569;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
  font-size: 1.4rem;
  color: #fde68a;
  text-align: center;
  letter-spacing: 0.1em;
}

.pw-term-existing {
  margin-bottom: 0.85rem;
  background: #082f49;
  border: 1px solid #0c4a6e;
  border-radius: 4px;
  padding: 0.55rem 0.65rem;
}

.pw-term-existing > label,
.pw-term-existing > p {
  display: block;
  font-size: 0.72rem;
  color: #7dd3fc;
  margin: 0 0 0.4rem 0;
}

.pw-term-existing-card {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 3px;
  padding: 0.4rem 0.55rem;
  margin-bottom: 0.35rem;
}

.pw-term-existing-card:last-child {
  margin-bottom: 0;
}

.pw-term-existing-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #e2e8f0;
}

.pw-term-id {
  font-size: 0.65rem;
  color: #64748b;
  font-family: ui-monospace, monospace;
}

.pw-term-note {
  font-size: 0.72rem;
  color: #94a3b8;
  margin-top: 0.2rem;
  line-height: 1.4;
}

.pw-term-new {
  background: #064e3b;
  border: 1px solid #047857;
  border-radius: 4px;
  padding: 0.5rem 0.65rem;
  margin-bottom: 0.85rem;
  font-size: 0.8rem;
  color: #6ee7b7;
}

.pw-term-form {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-bottom: 0.85rem;
}

.pw-term-form label {
  font-size: 0.72rem;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.pw-term-form input,
.pw-term-form textarea {
  background: #1e293b;
  border: 1px solid #475569;
  border-radius: 4px;
  padding: 0.4rem 0.55rem;
  color: #e2e8f0;
  font-size: 0.85rem;
  font-family: inherit;
}

.pw-term-form input:focus,
.pw-term-form textarea:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.pw-term-form textarea {
  resize: vertical;
  min-height: 60px;
}

.pw-term-result {
  padding: 0.55rem 0.7rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-bottom: 0.85rem;
}

.pw-term-result.success {
  background: #064e3b;
  border: 1px solid #10b981;
  color: #6ee7b7;
}

.pw-term-result.info {
  background: #1e3a8a;
  border: 1px solid #3b82f6;
  color: #93c5fd;
}

.pw-term-result.error {
  background: #7f1d1d;
  border: 1px solid #ef4444;
  color: #fca5a5;
}

.pw-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #334155;
}

.pw-modal-cancel,
.pw-modal-save {
  padding: 0.45rem 0.95rem;
  border-radius: 4px;
  border: none;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
}

.pw-modal-cancel {
  background: #334155;
  color: #e2e8f0;
}

.pw-modal-cancel:hover {
  background: #475569;
}

.pw-modal-save {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  font-weight: 600;
}

.pw-modal-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.pw-modal-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================
   View-mode toggle (Editor / Compare)
   ============================================================ */
.pw-view-toggle {
  display: inline-flex;
  margin-left: auto;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  overflow: hidden;
}

.pw-view-toggle button {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}

.pw-view-toggle button:hover {
  background: #334155;
  color: #e2e8f0;
}

.pw-view-toggle button.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  font-weight: 600;
}

/* ============================================================
   Compare panel (Feature C — side-by-side book preview)
   ============================================================ */
.pw-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.pw-compare-source,
.pw-compare-target {
  display: flex;
  flex-direction: column;
  background: #0f172a;
  overflow: hidden;
}

.pw-compare-source {
  border-right: 1px solid #334155;
}

.pw-compare-pane-head {
  background: #1e293b;
  padding: 0.5rem 0.9rem;
  font-size: 0.85rem;
  color: #cbd5e1;
  border-bottom: 1px solid #334155;
  flex-shrink: 0;
  font-weight: 600;
}

.pw-compare-stats {
  font-weight: 400;
  font-size: 0.75rem;
  color: #64748b;
  margin-left: 0.5rem;
}

.pw-compare-scan {
  flex: 1;
  overflow: auto;
  padding: 1rem;
  display: flex;
  justify-content: center;
  background: #020617;
}

.pw-compare-img {
  max-width: 100%;
  height: auto;
  background: #fff;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

/* Book-style Vietnamese page render */
.pw-compare-book {
  flex: 1;
  overflow: auto;
  padding: 2.2rem 2.4rem;
  background: #fafaf7;
  color: #1a1410;
  font-family: "Charter", "Iowan Old Style", "Georgia", "Noto Serif",
    "Source Han Serif", serif;
  font-size: 1rem;
  line-height: 1.75;
  letter-spacing: 0.005em;
}

.pw-cmp-h1 {
  font-size: 1.7rem;
  font-weight: 700;
  margin: 0.4em 0 0.7em 0;
  text-align: center;
  color: #4a1a1a;
  border-bottom: 2px solid #b8a890;
  padding-bottom: 0.3em;
  letter-spacing: 0.04em;
}

.pw-cmp-h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 1.2em 0 0.5em 0;
  color: #6d2727;
  letter-spacing: 0.03em;
}

.pw-cmp-para {
  margin: 0.6em 0 0.9em 0;
  text-align: justify;
  text-indent: 1.5em;
}

.pw-cmp-line {
  display: inline;
}

/* Lines render inline within paragraph for natural prose flow */
.pw-cmp-line + .pw-cmp-line {
  margin-left: 0.2em;
}

.pw-cmp-line-vi {
  display: inline;
}

.pw-cmp-line-empty {
  color: #b15454;
  font-style: italic;
  background: #fff3cd;
  padding: 0 0.2em;
  border-radius: 2px;
}

.pw-cmp-line-zh-inline {
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
  font-size: 0.95em;
  color: #555;
  margin-left: 0.3em;
}

.pw-cmp-list {
  margin: 0.7em 0 0.9em 1.5em;
  padding: 0;
}

.pw-cmp-list li {
  margin: 0.25em 0;
}

.pw-cmp-untranslated {
  background: rgba(255, 215, 0, 0.15);
}

.pw-cmp-figure {
  margin: 1.4em auto;
  text-align: center;
  max-width: 80%;
}

.pw-cmp-figure-img {
  max-width: 100%;
  height: auto;
  border: 1px solid #ccc;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.pw-cmp-figure figcaption {
  font-size: 0.85em;
  color: #5a4a3a;
  margin-top: 0.5em;
  font-style: italic;
}

.pw-cmp-table {
  background: #f0e9dc;
  border: 1px solid #c8b896;
  border-radius: 4px;
  padding: 0.7em 0.9em;
  margin: 1em 0;
  font-size: 0.92em;
}

.pw-cmp-table-content {
  margin-top: 0.4em;
  color: #2a2a2a;
}

.pw-cmp-meta {
  font-size: 0.75em;
  color: #999;
  text-align: center;
  margin: 0.4em 0;
  font-variant: small-caps;
}

.pw-cmp-fallback {
  background: #fff0d6;
  padding: 0.3em 0.6em;
  margin: 0.5em 0;
  border-left: 3px solid #d97706;
  font-size: 0.9em;
}

.pw-cmp-fallback em {
  color: #92400e;
  font-weight: 600;
  margin-right: 0.4em;
}

/* ============================================================
   AUTO mode panel
   ============================================================ */
.pw-auto {
  flex: 1;
  overflow: auto;
  padding: 1.2rem 1.5rem;
  background: #0f172a;
  color: #e2e8f0;
}

.pw-auto-controls {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
}

.pw-auto-controls h3 {
  margin: 0 0 0.7rem 0;
  font-size: 1.05rem;
  color: #cbd5e1;
}

.pw-auto-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  align-items: center;
}

.pw-auto-form label {
  font-size: 0.85rem;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.pw-auto-form input[type="number"] {
  width: 70px;
  background: #0f172a;
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 0.3rem 0.4rem;
  border-radius: 4px;
}

.pw-auto-check {
  user-select: none;
}

.pw-auto-run-btn {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  margin-left: auto;
}

.pw-auto-run-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pw-auto-help {
  margin: 0.7rem 0 0;
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.6;
}

.pw-auto-help b {
  color: #fde68a;
}

/* Summary cards */
.pw-auto-summary {
  margin-bottom: 1rem;
}

.pw-auto-summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.6rem;
}

.pw-auto-stat {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 5px;
  padding: 0.5rem 0.7rem;
  text-align: center;
}

.pw-auto-stat-label {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pw-auto-stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  margin-top: 0.2rem;
  color: #e2e8f0;
}

.pw-stat-good {
  border-color: #10b981;
}

.pw-stat-good .pw-auto-stat-value {
  color: #34d399;
}

.pw-stat-bad {
  border-color: #ef4444;
}

.pw-stat-bad .pw-auto-stat-value {
  color: #fca5a5;
}

.pw-stat-warn {
  border-color: #f59e0b;
}

.pw-stat-warn .pw-auto-stat-value {
  color: #fbbf24;
}

/* Per-page table */
.pw-auto-table-wrap {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  overflow: auto;
  max-height: calc(100vh - 280px);
}

.pw-auto-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.pw-auto-table th {
  background: #0f172a;
  color: #94a3b8;
  text-align: left;
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid #334155;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.pw-auto-table td {
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid #1e293b;
  vertical-align: top;
}

.pw-auto-table tr.pw-verdict-fit {
  background: rgba(16, 185, 129, 0.05);
}

.pw-auto-table tr.pw-verdict-review {
  background: rgba(245, 158, 11, 0.05);
}

.pw-auto-table tr.pw-verdict-mismatch {
  background: rgba(239, 68, 68, 0.08);
}

.pw-auto-table tr.pw-verdict-skip {
  background: rgba(100, 116, 139, 0.05);
  opacity: 0.6;
}

.pw-verdict-fit {
  color: #34d399;
  font-weight: 600;
}

.pw-verdict-review {
  color: #fbbf24;
  font-weight: 600;
}

.pw-verdict-mismatch,
.pw-verdict-error {
  color: #fca5a5;
  font-weight: 600;
}

.pw-verdict-skip {
  color: #64748b;
}

.pw-auto-page-link {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  font-family: ui-monospace, monospace;
  text-decoration: underline;
}

.pw-auto-model {
  font-size: 0.7rem;
  color: #64748b;
  font-family: ui-monospace, monospace;
}

.pw-auto-issues {
  max-width: 320px;
}

.pw-auto-msg-err {
  font-size: 0.72rem;
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 2px;
  margin-bottom: 0.2rem;
}

.pw-auto-issue {
  font-size: 0.72rem;
  color: #cbd5e1;
  margin-bottom: 0.2rem;
}

.pw-warn-error {
  color: #fca5a5;
  font-family: ui-monospace, monospace;
  font-size: 0.7rem;
}

.pw-warn-warn {
  color: #fbbf24;
  font-family: ui-monospace, monospace;
  font-size: 0.7rem;
}

.pw-warn-info {
  color: #93c5fd;
  font-family: ui-monospace, monospace;
  font-size: 0.7rem;
}

.pw-auto-issue-prev {
  margin-left: 0.4rem;
  font-family: "Songti SC", serif;
  color: #94a3b8;
}

.pw-auto-spinner {
  margin-top: 1rem;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  padding: 1.5rem;
}

/* Paid-fallback UI */
.pw-auto-paid {
  border: 1px dashed #f59e0b;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
}

.pw-auto-paid.pw-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #475569;
}

.pw-no-key {
  font-size: 0.7rem;
  color: #fca5a5;
  margin-left: 0.3rem;
}

.pw-auto-providers {
  margin: 0.6rem 0 0;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.6;
  font-family: ui-monospace, monospace;
}

.pw-auto-providers b {
  color: #cbd5e1;
  font-family: inherit;
}

.pw-auto-providers code {
  background: #0f172a;
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 0.95em;
}

.pw-key-ok {
  color: #34d399;
}

.pw-key-missing {
  color: #fca5a5;
}

.pw-auto-provider {
  font-size: 0.72rem;
}

.pw-prov-paid {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 600;
  font-size: 0.7rem;
}

.pw-prov-free {
  color: #64748b;
}

.pw-auto-cost {
  font-family: ui-monospace, monospace;
  font-size: 0.72rem;
  color: #fde68a;
  text-align: right;
}
</style>
