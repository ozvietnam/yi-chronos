<script setup>
import { ref, onMounted, computed } from "vue";
import {
  getLibrary,
  getLibraryStats,
  syncLibrary,
  scanLibraryTextLayers,
  analyzeBook,
  updateBook,
  TIER_LABEL,
  TIER_DESCRIPTION,
  STATUS_LABEL,
  SCHOOL_LABEL,
  RESTORE_METHOD_LABEL
} from "../../composables/useLexicon.js";
import BookCard from "./BookCard.vue";
import BookDetail from "./BookDetail.vue";
import LibrarianWizard from "./LibrarianWizard.vue";
import BookReader from "./BookReader.vue";

const books = ref([]);
const stats = ref(null);
const loading = ref(false);
const error = ref("");
const filterTier = ref("");        // ''|'S'|'A'|'B'|'C'
const filterStatus = ref("");
const filterSchool = ref("");
const selectedBook = ref(null);
const showWizard = ref(false);
const syncing = ref(false);
const syncMsg = ref("");
const readerBook = ref(null);  // open BookReader for this book
const filterMethod = ref("");   // ''|'text_layer'|'hybrid'|'pure_scan'|'unknown'
const probing = ref(false);
const probeMsg = ref("");

const tiersOrdered = ["S", "A", "B", "C"];

const grouped = computed(() => {
  const g = { S: [], A: [], B: [], C: [] };
  for (const b of books.value) {
    const t = (b.tier || "B").toUpperCase();
    (g[t] || g["B"]).push(b);
  }
  return g;
});
const hasBooks = computed(() => books.value.length > 0);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await getLibrary({
      tier: filterTier.value || null,
      status: filterStatus.value || null,
      school: filterSchool.value || null
    });
    books.value = data.books || [];
    stats.value = data.stats;
    if (selectedBook.value && !books.value.some(b => b.corpus_id === selectedBook.value.corpus_id)) {
      selectedBook.value = null;
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function doProbeTextLayers(onlyUnprobed = true) {
  probing.value = true;
  probeMsg.value = "Đang probe text layer toàn bộ thư viện…";
  try {
    const r = await scanLibraryTextLayers({ onlyUnprobed });
    const by = r.by_method || {};
    probeMsg.value = `✓ Đã probe ${r.scanned} sách · text_layer=${by.text_layer || 0} · hybrid=${by.hybrid || 0} · pure_scan=${by.pure_scan || 0}`;
    await load();
  } catch (e) {
    probeMsg.value = "✗ " + String(e.message || e);
  } finally {
    probing.value = false;
    setTimeout(() => { probeMsg.value = ""; }, 8000);
  }
}

async function doSync() {
  syncing.value = true;
  syncMsg.value = "Đang quét thư viện sách/…";
  try {
    const r = await syncLibrary({ skipLlm: true });
    syncMsg.value = `✓ Quét ${r.scanned} sách — ${r.registered} mới, ${r.updated} cập nhật`;
    await load();
  } catch (e) {
    syncMsg.value = "✗ " + String(e.message || e);
  } finally {
    syncing.value = false;
    setTimeout(() => { syncMsg.value = ""; }, 5000);
  }
}

function onSelect(book) {
  selectedBook.value = book;
}

async function onSaveBook(corpusId, patch) {
  // If patch is empty, treat as a refresh trigger (after restoration)
  if (!patch || Object.keys(patch).length === 0) {
    await load();
    return;
  }
  try {
    const r = await updateBook(corpusId, patch);
    if (r.book) {
      const idx = books.value.findIndex(b => b.corpus_id === corpusId);
      if (idx !== -1) books.value[idx] = r.book;
      selectedBook.value = r.book;
    }
  } catch (e) {
    error.value = String(e.message || e);
  }
}

function onOpenReader(book) {
  readerBook.value = book;
}

async function onWizardComplete(corpus) {
  showWizard.value = false;
  await load();
  if (corpus) {
    selectedBook.value = books.value.find(b => b.corpus_id === corpus.corpus_id) || corpus;
  }
}

onMounted(load);
</script>

<template>
  <div class="library-view">
    <header class="lib-header">
      <div class="lib-title">
        <h3>📚 Thư viện ({{ stats?.total_books || 0 }} sách)</h3>
        <div class="lib-overall" v-if="stats">
          {{ stats.pages_ingested }} / {{ stats.pages_total }} trang đã đọc
          ({{ stats.overall_progress_percent }}%)
        </div>
      </div>
      <div class="lib-actions">
        <button class="btn-ghost" :disabled="probing" @click="doProbeTextLayers(true)"
                title="Probe text layer cho các sách chưa probe — nhanh">
          {{ probing ? "Đang probe…" : "🔍 Probe text-layer" }}
        </button>
        <button class="btn-ghost" :disabled="syncing" @click="doSync">
          {{ syncing ? "Đang quét…" : "🔄 Sync thư viện" }}
        </button>
        <button class="btn-primary" @click="showWizard = true">
          ➕ Thêm sách mới
        </button>
      </div>
    </header>

    <p v-if="syncMsg" class="sync-msg">{{ syncMsg }}</p>
    <p v-if="probeMsg" class="sync-msg">{{ probeMsg }}</p>

    <!-- Filters -->
    <div class="filters">
      <label>
        Tier:
        <select v-model="filterTier" @change="load">
          <option value="">Tất cả</option>
          <option v-for="t in tiersOrdered" :key="t" :value="t">
            {{ t }} — {{ TIER_DESCRIPTION[t] }}
          </option>
        </select>
      </label>
      <label>
        Status:
        <select v-model="filterStatus" @change="load">
          <option value="">Tất cả</option>
          <option v-for="(v,k) in STATUS_LABEL" :key="k" :value="k">{{ v.label }}</option>
        </select>
      </label>
      <label>
        Trường phái:
        <select v-model="filterSchool" @change="load">
          <option value="">Tất cả</option>
          <option v-for="(label,k) in SCHOOL_LABEL" :key="k" :value="k">{{ label }}</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="lib-body">
      <!-- Books grouped by tier -->
      <div class="shelves">
        <div v-if="!hasBooks" class="empty-state">
          Không có sách nào khớp bộ lọc hiện tại.
        </div>
        <section v-for="t in tiersOrdered" :key="t" class="shelf" v-show="grouped[t].length > 0">
          <h4 class="shelf-title">
            <span class="tier-badge" :style="{ background: TIER_LABEL[t].color }">{{ t }}</span>
            {{ TIER_DESCRIPTION[t] }}
            <span class="shelf-count">{{ grouped[t].length }} sách</span>
          </h4>
          <div class="shelf-grid">
            <BookCard
              v-for="book in grouped[t]"
              :key="book.corpus_id"
              :book="book"
              :selected="selectedBook?.corpus_id === book.corpus_id"
              @select="onSelect"
            />
          </div>
        </section>
      </div>

      <!-- Detail panel -->
      <aside v-if="selectedBook" class="detail-pane">
        <BookDetail
          :book="selectedBook"
          @save="onSaveBook"
          @close="selectedBook = null"
          @open-reader="onOpenReader"
        />
      </aside>
    </div>

    <!-- BookReader modal (full-screen) -->
    <div v-if="readerBook" class="reader-overlay">
      <BookReader
        :corpus-id="readerBook.corpus_id"
        @close="readerBook = null; load()"
        @concept-click="(c) => console.log('concept clicked:', c)"
      />
    </div>

    <!-- Librarian wizard modal -->
    <LibrarianWizard
      v-if="showWizard"
      @close="showWizard = false"
      @complete="onWizardComplete"
    />
  </div>
</template>

<style scoped>
.library-view {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.lib-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  gap: 1rem;
  flex-wrap: wrap;
}
.lib-title h3 { margin: 0; color: #e2e8f0; }
.lib-overall {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-top: 0.2rem;
}
.lib-actions { display: flex; gap: 0.5rem; }
.btn-primary {
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary:hover { background: #c4b5fd; }
.btn-ghost {
  background: rgba(167, 139, 250, 0.1);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.3);
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-ghost:disabled { opacity: 0.5; }
.sync-msg {
  margin: 0 0 0.5rem;
  padding: 0.4rem 0.7rem;
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
  border-radius: 4px;
  font-size: 0.85rem;
}
.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: #94a3b8;
}
.filters select {
  margin-left: 0.3rem;
  padding: 0.25rem 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  border-radius: 3px;
}
.status { padding: 2rem; text-align: center; color: #94a3b8; }
.status.error { color: #f87171; }
.empty-state {
  padding: 1.25rem;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  color: #94a3b8;
  text-align: center;
  background: rgba(15, 23, 42, 0.35);
}

.lib-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr minmax(0, 380px);
  gap: 1rem;
  overflow: hidden;
}
.shelves {
  overflow-y: auto;
  padding-right: 0.5rem;
}
.shelf {
  margin-bottom: 1.25rem;
}
.shelf-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem;
  color: #cbd5e1;
  font-size: 0.9rem;
  font-weight: 500;
}
.tier-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.75rem;
}
.shelf-count {
  margin-left: auto;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 400;
}
.shelf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.6rem;
}
.detail-pane {
  background: rgba(15, 23, 42, 0.55);
  border-radius: 6px;
  overflow-y: auto;
}

.reader-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  z-index: 1500;
  padding: 1rem;
  display: flex;
}
.reader-overlay > * { width: 100%; height: 100%; }

@media (max-width: 900px) {
  .lib-body { grid-template-columns: 1fr; }
  .detail-pane { max-height: 50vh; }
}
</style>
