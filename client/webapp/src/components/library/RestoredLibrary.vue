<script setup>
/**
 * RestoredLibrary — Thư viện sách Việt đã phục chế (OCR + cleanup).
 *
 * Show sidebar danh sách sách (group by category) + main panel render markdown.
 * Search full-text trên toàn bộ corpus.
 *
 * Backend:
 *  GET /api/library/restored-books/list
 *  GET /api/library/restored-books/{book_id}/content
 *  GET /api/library/restored-books/search?q=...
 */
import { ref, computed, onMounted, watch, nextTick } from "vue";

const books = ref([]);
const categories = ref({});
const stats = ref({ total_books: 0, total_pages: 0, total_chars: 0 });
const loadingList = ref(false);
const errorList = ref("");

const selectedBookId = ref(null);
const bookContent = ref(null);
const loadingContent = ref(false);
const errorContent = ref("");
const search = ref("");
const searchHits = ref([]);
const searchLoading = ref(false);

// Pagination view (split content thành chunks 20K chars để render nhanh)
const CHUNK_SIZE = 20000;
const chunkIdx = ref(0);
const showBookList = ref(true);
const mainRef = ref(null);
const totalChunks = computed(() => {
  if (!bookContent.value?.content_md) return 1;
  return Math.ceil(bookContent.value.content_md.length / CHUNK_SIZE);
});
const currentChunk = computed(() => {
  if (!bookContent.value?.content_md) return "";
  const start = chunkIdx.value * CHUNK_SIZE;
  return bookContent.value.content_md.slice(start, start + CHUNK_SIZE);
});

async function loadList() {
  loadingList.value = true;
  errorList.value = "";
  try {
    const r = await fetch("/api/library/restored-books/list");
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    books.value = d.books || [];
    categories.value = d.categories || {};
    stats.value = {
      total_books: d.total_books,
      total_pages: d.total_pages,
      total_chars: d.total_chars,
    };
  } catch (e) {
    errorList.value = String(e.message || e);
  } finally {
    loadingList.value = false;
  }
}

async function openBook(bid) {
  selectedBookId.value = bid;
  bookContent.value = null;
  errorContent.value = "";
  loadingContent.value = true;
  chunkIdx.value = 0;
  if (typeof window !== "undefined" && window.innerWidth <= 800) {
    showBookList.value = false;
  }
  try {
    const r = await fetch(`/api/library/restored-books/${bid}/content`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    if (d.status !== "ok") throw new Error(d.reason || "Unknown error");
    bookContent.value = d;
  } catch (e) {
    errorContent.value = String(e.message || e);
  } finally {
    loadingContent.value = false;
  }
}

async function doSearch() {
  const q = search.value.trim();
  if (q.length < 2) {
    searchHits.value = [];
    return;
  }
  searchLoading.value = true;
  try {
    const r = await fetch(`/api/library/restored-books/search?q=${encodeURIComponent(q)}&max_results=30`);
    const d = await r.json();
    searchHits.value = d.hits || [];
  } catch (e) {
    console.error(e);
  } finally {
    searchLoading.value = false;
  }
}

function fmtChars(n) {
  if (n > 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n > 1000) return (n / 1000).toFixed(0) + "K";
  return String(n);
}

// Light markdown render — không pull dependency
function renderMd(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Headers (## ###)
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
  // Bold / italic
  html = html.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  html = html.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, "<i>$1</i>");
  // Bullet lists
  html = html.replace(/^\* (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*?<\/li>(\n<li>.*?<\/li>)+)/gs, "<ul>$1</ul>");
  // Page comments
  html = html.replace(/&lt;!-- page (\d+) --&gt;/g, '<div class="page-marker">— Trang $1 —</div>');
  html = html.replace(/&lt;!-- trang trống --&gt;/g, '<div class="page-empty">(trang trống)</div>');
  // Paragraphs (2+ newlines)
  html = html.replace(/\n{2,}/g, "</p><p>");
  html = `<p>${html}</p>`;
  // Remove empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, "");
  return html;
}

function scrollReaderTop() {
  nextTick(() => {
    if (mainRef.value) mainRef.value.scrollTop = 0;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

function prevChunk() {
  chunkIdx.value = Math.max(0, chunkIdx.value - 1);
  scrollReaderTop();
}
function nextChunk() {
  chunkIdx.value = Math.min(totalChunks.value - 1, chunkIdx.value + 1);
  scrollReaderTop();
}

onMounted(loadList);
watch(chunkIdx, scrollReaderTop);
watch(search, () => {
  // Debounced search
  clearTimeout(window.__libSearchTo);
  window.__libSearchTo = setTimeout(doSearch, 400);
});
</script>

<template>
  <div class="rlib">
    <header class="rlib-head">
      <h2>📚 Thư viện phục chế — Sách Việt môn Đông phương</h2>
      <p class="subtitle" v-if="stats.total_books">
        {{ stats.total_books }} sách · {{ stats.total_pages.toLocaleString() }} trang ·
        {{ fmtChars(stats.total_chars) }} chữ
      </p>
    </header>

    <div class="rlib-search">
      <input v-model="search" type="search"
             placeholder="Tìm trong toàn bộ thư viện (vd: Thiên Can, Tả Phụ, Dụng Thần, ...)" />
      <span v-if="searchLoading" class="loading">⏳</span>
      <span v-else-if="searchHits.length">{{ searchHits.length }} hits</span>
    </div>

    <div v-if="searchHits.length" class="rlib-search-results">
      <div v-for="(h, i) in searchHits" :key="i" class="search-hit"
           @click="openBook(h.book_id)">
        <div class="hit-book">{{ h.title }} <small>· {{ h.category }}</small></div>
        <div class="hit-snippet" v-html="renderMd(h.snippet)"></div>
      </div>
    </div>

    <div class="rlib-body" :class="{ 'is-reading': selectedBookId && !showBookList }">
      <!-- Sidebar: books grouped by category -->
      <aside v-show="showBookList || !selectedBookId" class="rlib-sidebar">
        <div v-if="loadingList" class="loading-state">Đang tải...</div>
        <div v-if="errorList" class="error">{{ errorList }}</div>
        <div v-for="(books_in_cat, cat) in categories" :key="cat" class="rlib-cat">
          <h4>{{ cat }}</h4>
          <ul>
            <li v-for="b in books_in_cat" :key="b.book_id"
                :class="{ active: selectedBookId === b.book_id }"
                @click="openBook(b.book_id)">
              <div class="book-title">{{ b.title }}</div>
              <small>{{ b.total_pages }}p · {{ fmtChars(b.chars) }}c · {{ b.extractor }}</small>
            </li>
          </ul>
        </div>
      </aside>

      <!-- Main: reader -->
      <main ref="mainRef" class="rlib-main reading-pane">
        <div v-if="!selectedBookId" class="empty-state">
          ← Chọn 1 sách bên trái để bắt đầu đọc
        </div>
        <div v-if="loadingContent" class="loading-state">⏳ Đang tải sách...</div>
        <div v-if="errorContent" class="error">{{ errorContent }}</div>

        <div v-if="bookContent" class="reader">
          <div class="reader-head">
            <button
              v-if="!showBookList"
              type="button"
              class="reader-back"
              @click="showBookList = true"
            >
              ← Sách
            </button>
            <h3>{{ bookContent.title }}</h3>
            <div class="reader-controls" v-if="totalChunks > 1">
              <button @click="prevChunk" :disabled="chunkIdx === 0">← Trước</button>
              <span>Phần {{ chunkIdx + 1 }} / {{ totalChunks }}</span>
              <button @click="nextChunk" :disabled="chunkIdx === totalChunks - 1">Sau →</button>
            </div>
          </div>
          <div class="reader-body reading-surface reading-prose" v-html="renderMd(currentChunk)"></div>
          <div class="reader-controls reader-controls-bottom" v-if="totalChunks > 1">
            <button @click="prevChunk" :disabled="chunkIdx === 0">← Trước</button>
            <span>Phần {{ chunkIdx + 1 }} / {{ totalChunks }}</span>
            <button @click="nextChunk" :disabled="chunkIdx === totalChunks - 1">Sau →</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.rlib {
  background: var(--read-bg, rgba(15, 23, 42, 0.4));
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem 0;
  color: var(--read-text, #e2e8f0);
}
.rlib-head h2 { margin: 0; color: var(--read-heading, #fcd34d); font-size: calc(1.05rem * var(--reading-scale)); }
.subtitle { color: var(--read-text-dim, #94a3b8); font-size: calc(0.85rem * var(--reading-scale)); margin: 0.3rem 0 0.7rem; font-style: italic; }

.rlib-search {
  display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem;
  background: var(--read-cite-bg, rgba(252, 211, 77, 0.05));
  border: 1px solid var(--read-border, rgba(252, 211, 77, 0.2));
  border-radius: 8px; padding: 0.45rem 0.75rem;
}
.rlib-search input {
  flex: 1; background: transparent; color: var(--read-text, #e0e7ff); border: none; outline: none;
  font-size: calc(0.92rem * var(--reading-scale)); padding: 0.35rem; min-height: 40px;
}
.rlib-search .loading { color: var(--read-rule, #fcd34d); }

.rlib-search-results {
  background: var(--read-bg-soft, rgba(0,0,0,0.3)); border-radius: 8px; padding: 0.5rem;
  max-height: 250px; overflow-y: auto; margin-bottom: 0.6rem;
  -webkit-overflow-scrolling: touch;
}
.search-hit { padding: 0.5rem 0.65rem; cursor: pointer; border-radius: 6px; min-height: 44px; }
.search-hit:hover { background: var(--read-cite-bg, rgba(252, 211, 77, 0.08)); }
.hit-book { color: var(--read-heading, #fcd34d); font-weight: 600; font-size: calc(0.85rem * var(--reading-scale)); }
.hit-book small { color: var(--read-text-dim, #94a3b8); font-weight: 400; }
.hit-snippet { color: var(--read-text-dim, #cbd5e1); font-size: calc(0.84rem * var(--reading-scale)); line-height: var(--reading-line-height, 1.78); margin-top: 0.2rem; }
.hit-snippet :deep(p) { margin: 0.2rem 0; }

.rlib-body { display: grid; grid-template-columns: 280px 1fr; gap: 1rem; min-height: 500px; }
.rlib-body.is-reading { grid-template-columns: 1fr; }

.rlib-sidebar {
  background: var(--read-bg-soft, rgba(0,0,0,0.25)); border-radius: 8px; padding: 0.5rem;
  max-height: 70vh; overflow-y: auto; border: 1px solid var(--read-border, transparent);
  -webkit-overflow-scrolling: touch;
}
.rlib-cat h4 { margin: 0.5rem 0.3rem 0.3rem; color: var(--read-han, #c4b5fd); font-size: calc(0.8rem * var(--reading-scale)); font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em; }
.rlib-cat ul { list-style: none; padding: 0; margin: 0 0 0.5rem; }
.rlib-cat li {
  padding: 0.45rem 0.55rem; cursor: pointer; border-radius: 6px;
  margin-bottom: 0.15rem; transition: background 0.15s; min-height: 44px;
}
.rlib-cat li:hover { background: var(--read-cite-bg, rgba(252, 211, 77, 0.08)); }
.rlib-cat li.active { background: var(--read-cite-bg, rgba(252, 211, 77, 0.18)); border-left: 3px solid var(--read-rule, #fcd34d); }
.rlib-cat li .book-title { color: var(--read-heading, #fcd34d); font-size: calc(0.86rem * var(--reading-scale)); line-height: 1.35; }
.rlib-cat li small { color: var(--read-text-faint, #94a3b8); font-size: calc(0.72rem * var(--reading-scale)); display: block; margin-top: 0.1rem; }

.rlib-main {
  background: var(--read-surface, rgba(0,0,0,0.25));
  border-radius: 8px;
  padding: 0.85rem 1rem;
  max-height: 70vh;
  border: 1px solid var(--read-border, transparent);
}
.empty-state {
  display: flex; align-items: center; justify-content: center;
  height: 200px; color: var(--read-text-faint, #64748b); font-style: italic;
}
.loading-state { color: var(--read-rule, #fcd34d); padding: 1rem; text-align: center; }
.error { color: #f87171; padding: 0.5rem; }

.reader-head {
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--read-border, rgba(252,211,77,0.2));
  padding-bottom: 0.55rem; margin-bottom: 0.75rem;
  position: sticky; top: 0; z-index: 2;
  background: var(--read-surface, rgba(0,0,0,0.25));
  padding-top: 0.15rem;
}
.reader-back {
  background: var(--read-cite-bg, rgba(252,211,77,0.12));
  border: 1px solid var(--read-border, rgba(252,211,77,0.3));
  color: var(--read-link, #fcd34d);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: calc(0.82rem * var(--reading-scale));
  min-height: 40px;
}
.reader-head h3 { margin: 0; color: var(--read-heading, #fcd34d); font-size: calc(1rem * var(--reading-scale)); flex: 1; min-width: 0; }
.reader-controls {
  display: flex; align-items: center; gap: 0.6rem; margin: 0.55rem 0;
  font-size: calc(0.85rem * var(--reading-scale)); color: var(--read-text-dim, #cbd5e1); justify-content: center;
  flex-wrap: wrap;
}
.reader-controls-bottom {
  position: sticky;
  bottom: 0;
  padding: 0.5rem 0 0.15rem;
  background: linear-gradient(180deg, transparent, var(--read-bg, #1d1813) 28%);
}
.reader-controls button {
  background: var(--read-cite-bg, rgba(252,211,77,0.15));
  border: 1px solid var(--read-border, rgba(252,211,77,0.3));
  color: var(--read-link, #fcd34d);
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: calc(0.84rem * var(--reading-scale));
  min-height: 44px;
}
.reader-controls button:disabled { opacity: 0.4; cursor: not-allowed; }
.reader-body {
  font-family: "Be Vietnam Pro", Charter, "Iowan Old Style", Palatino, Georgia, serif;
}
.reader-body :deep(h1) { color: var(--read-heading, #fcd34d); font-size: calc(1.35rem * var(--reading-scale)); margin: 1.1rem 0 0.55rem; }
.reader-body :deep(h2) { color: var(--read-heading, #fcd34d); font-size: calc(1.12rem * var(--reading-scale)); margin: 0.95rem 0 0.45rem; }
.reader-body :deep(h3) { color: var(--read-han, #c4b5fd); font-size: calc(1.02rem * var(--reading-scale)); margin: 0.75rem 0 0.35rem; }
.reader-body :deep(b) { color: var(--read-heading, #fcd34d); }
.reader-body :deep(i) { color: var(--read-han, #c4b5fd); }
.reader-body :deep(ul) { padding-left: 1.25rem; }
.reader-body :deep(li) { margin: 0.3rem 0; }
.reader-body :deep(.page-marker) {
  color: var(--read-text-faint, #64748b); font-style: italic; text-align: center;
  font-size: calc(0.78rem * var(--reading-scale));
  margin: 1rem 0; padding: 0.25rem; border-top: 1px dashed var(--read-border, rgba(100,116,139,0.3));
}
.reader-body :deep(.page-empty) { color: var(--read-text-faint, #64748b); font-style: italic; text-align: center; font-size: calc(0.78rem * var(--reading-scale)); margin: 0.4rem 0; }

@media (max-width: 800px) {
  .rlib-body { grid-template-columns: 1fr; min-height: auto; }
  .rlib-sidebar { max-height: min(42vh, 320px); }
  .rlib-main {
    max-height: none;
    min-height: min(72vh, calc(100vh - 220px));
    padding: 0.75rem 0.85rem;
  }
  .rlib-body.is-reading .rlib-main {
    min-height: min(78vh, calc(100vh - 160px));
  }
}
</style>
