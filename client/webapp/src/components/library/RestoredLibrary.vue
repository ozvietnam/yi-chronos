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
import { ref, computed, onMounted, watch } from "vue";

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

onMounted(loadList);
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

    <div class="rlib-body">
      <!-- Sidebar: books grouped by category -->
      <aside class="rlib-sidebar">
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
      <main class="rlib-main">
        <div v-if="!selectedBookId" class="empty-state">
          ← Chọn 1 sách bên trái để bắt đầu đọc
        </div>
        <div v-if="loadingContent" class="loading-state">⏳ Đang tải sách...</div>
        <div v-if="errorContent" class="error">{{ errorContent }}</div>

        <div v-if="bookContent" class="reader">
          <div class="reader-head">
            <h3>{{ bookContent.title }}</h3>
            <div class="reader-controls" v-if="totalChunks > 1">
              <button @click="chunkIdx = Math.max(0, chunkIdx - 1)" :disabled="chunkIdx === 0">← Trang trước</button>
              <span>Phần {{ chunkIdx + 1 }} / {{ totalChunks }}</span>
              <button @click="chunkIdx = Math.min(totalChunks - 1, chunkIdx + 1)" :disabled="chunkIdx === totalChunks - 1">Trang sau →</button>
            </div>
          </div>
          <div class="reader-body" v-html="renderMd(currentChunk)"></div>
          <div class="reader-controls" v-if="totalChunks > 1">
            <button @click="chunkIdx = Math.max(0, chunkIdx - 1)" :disabled="chunkIdx === 0">← Trang trước</button>
            <span>Phần {{ chunkIdx + 1 }} / {{ totalChunks }}</span>
            <button @click="chunkIdx = Math.min(totalChunks - 1, chunkIdx + 1)" :disabled="chunkIdx === totalChunks - 1">Trang sau →</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.rlib {
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px; padding: 1rem; margin: 0.5rem 0;
}
.rlib-head h2 { margin: 0; color: #fcd34d; font-size: 1.1rem; }
.subtitle { color: #94a3b8; font-size: 0.85rem; margin: 0.3rem 0 0.7rem; font-style: italic; }

.rlib-search {
  display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem;
  background: rgba(252, 211, 77, 0.05); border: 1px solid rgba(252, 211, 77, 0.2);
  border-radius: 5px; padding: 0.4rem 0.7rem;
}
.rlib-search input {
  flex: 1; background: transparent; color: #e0e7ff; border: none; outline: none;
  font-size: 0.9rem; padding: 0.3rem;
}
.rlib-search .loading { color: #fcd34d; }

.rlib-search-results {
  background: rgba(0,0,0,0.3); border-radius: 5px; padding: 0.5rem;
  max-height: 250px; overflow-y: auto; margin-bottom: 0.6rem;
}
.search-hit { padding: 0.4rem 0.6rem; cursor: pointer; border-radius: 4px; }
.search-hit:hover { background: rgba(252, 211, 77, 0.08); }
.hit-book { color: #fcd34d; font-weight: 600; font-size: 0.85rem; }
.hit-book small { color: #94a3b8; font-weight: 400; }
.hit-snippet { color: #cbd5e1; font-size: 0.82rem; line-height: 1.5; margin-top: 0.2rem; }
.hit-snippet :deep(p) { margin: 0.2rem 0; }

.rlib-body { display: grid; grid-template-columns: 280px 1fr; gap: 1rem; min-height: 500px; }

.rlib-sidebar {
  background: rgba(0,0,0,0.25); border-radius: 5px; padding: 0.5rem;
  max-height: 70vh; overflow-y: auto;
}
.rlib-cat h4 { margin: 0.5rem 0.3rem 0.3rem; color: #c4b5fd; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em; }
.rlib-cat ul { list-style: none; padding: 0; margin: 0 0 0.5rem; }
.rlib-cat li {
  padding: 0.35rem 0.5rem; cursor: pointer; border-radius: 4px;
  margin-bottom: 0.15rem; transition: background 0.15s;
}
.rlib-cat li:hover { background: rgba(252, 211, 77, 0.08); }
.rlib-cat li.active { background: rgba(252, 211, 77, 0.18); }
.rlib-cat li .book-title { color: #fcd34d; font-size: 0.85rem; line-height: 1.3; }
.rlib-cat li small { color: #94a3b8; font-size: 0.7rem; display: block; margin-top: 0.1rem; }

.rlib-main {
  background: rgba(0,0,0,0.25); border-radius: 5px; padding: 0.8rem;
  max-height: 70vh; overflow-y: auto;
}
.empty-state {
  display: flex; align-items: center; justify-content: center;
  height: 200px; color: #64748b; font-style: italic;
}
.loading-state { color: #fcd34d; padding: 1rem; text-align: center; }
.error { color: #f87171; padding: 0.5rem; }

.reader-head { border-bottom: 1px solid rgba(252,211,77,0.2); padding-bottom: 0.4rem; margin-bottom: 0.7rem; }
.reader-head h3 { margin: 0; color: #fcd34d; font-size: 1rem; }
.reader-controls {
  display: flex; align-items: center; gap: 0.6rem; margin: 0.7rem 0;
  font-size: 0.85rem; color: #cbd5e1; justify-content: center;
}
.reader-controls button {
  background: rgba(252,211,77,0.15); border: 1px solid rgba(252,211,77,0.3);
  color: #fcd34d; padding: 0.3rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.82rem;
}
.reader-controls button:disabled { opacity: 0.4; cursor: not-allowed; }
.reader-body {
  color: #e2e8f0; line-height: 1.7; font-size: 0.92rem;
  font-family: 'Charter', 'Iowan Old Style', 'Palatino', Georgia, serif;
}
.reader-body :deep(h1) { color: #fcd34d; font-size: 1.4rem; margin: 1.2rem 0 0.6rem; }
.reader-body :deep(h2) { color: #fcd34d; font-size: 1.15rem; margin: 1rem 0 0.5rem; }
.reader-body :deep(h3) { color: #c4b5fd; font-size: 1.02rem; margin: 0.8rem 0 0.4rem; }
.reader-body :deep(b) { color: #fcd34d; }
.reader-body :deep(i) { color: #c4b5fd; }
.reader-body :deep(ul) { padding-left: 1.2rem; }
.reader-body :deep(li) { margin: 0.25rem 0; }
.reader-body :deep(.page-marker) {
  color: #64748b; font-style: italic; text-align: center; font-size: 0.78rem;
  margin: 0.8rem 0; padding: 0.2rem; border-top: 1px dashed rgba(100,116,139,0.3);
}
.reader-body :deep(.page-empty) { color: #64748b; font-style: italic; text-align: center; font-size: 0.78rem; margin: 0.4rem 0; }

@media (max-width: 800px) {
  .rlib-body { grid-template-columns: 1fr; }
  .rlib-sidebar { max-height: 250px; }
}
</style>
