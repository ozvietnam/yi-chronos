<script setup>
/**
 * LibraryView — gallery view của tab "📖 Dịch sách".
 *
 * Hiển thị tất cả sách từ /api/yi-publishing/books với cover, metadata,
 * % progress. Polling /api/yi-publishing/jobs?active=true mỗi 5s để
 * update OCR progress real-time.
 *
 * Emits:
 *   open-book(book_id) — user wants to open this book in PublishingWorkspace
 */
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import BookCard from "./BookCard.vue";
import AddBookModal from "./AddBookModal.vue";
import OcrJobModal from "./OcrJobModal.vue";
import EditMetadataModal from "./EditMetadataModal.vue";
import JobBadge from "./JobBadge.vue";

const emit = defineEmits(["open-book"]);

const books = ref([]);
const activeJobs = ref([]);
const allJobs = ref([]);
const filterStage = ref("all");
const showAddModal = ref(false);
const showOcrModal = ref(false);
const showMetadataModal = ref(false);
const showJobsPanel = ref(false);
const selectedBookForModal = ref(null);
const loading = ref(false);
const error = ref("");
const coverInputRef = ref(null);
const coverUploadBookId = ref(null);

let pollHandle = null;
const POLL_INTERVAL_MS = 5000;

const filteredBooks = computed(() => {
  if (filterStage.value === "all") return books.value;
  if (filterStage.value === "active") return books.value.filter((b) => b.active_job_id);
  return books.value.filter((b) => String(b.stage) === filterStage.value);
});

const stageCounts = computed(() => {
  const counts = { all: books.value.length, active: 0 };
  for (let i = 1; i <= 6; i++) counts[String(i)] = 0;
  for (const b of books.value) {
    if (b.active_job_id) counts.active += 1;
    counts[String(b.stage)] = (counts[String(b.stage)] || 0) + 1;
  }
  return counts;
});

const hasActiveJobs = computed(() => activeJobs.value.length > 0);

async function loadBooks() {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch("/api/yi-publishing/books");
    const d = await r.json();
    if (d.status === "ok") {
      books.value = d.books || [];
    } else {
      error.value = d.message || "Tải sách thất bại";
    }
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    loading.value = false;
  }
}

async function loadJobs() {
  try {
    const [activeR, allR] = await Promise.all([
      fetch("/api/yi-publishing/jobs?active=true"),
      fetch("/api/yi-publishing/jobs?limit=10"),
    ]);
    const activeD = await activeR.json();
    const allD = await allR.json();
    if (activeD.status === "ok") activeJobs.value = activeD.jobs || [];
    if (allD.status === "ok") allJobs.value = allD.jobs || [];

    // Update books with active job progress
    if (activeJobs.value.length) {
      const jobsByBook = Object.fromEntries(
        activeJobs.value.map((j) => [j.book_id, j])
      );
      books.value = books.value.map((b) => {
        const j = jobsByBook[b.book_id];
        return j
          ? { ...b, active_job_id: j.job_id, active_job_progress: j.progress }
          : { ...b, active_job_id: null, active_job_progress: null };
      });
    } else {
      // No active jobs — clear flags
      const needClear = books.value.some((b) => b.active_job_id);
      if (needClear) {
        books.value = books.value.map((b) => ({
          ...b,
          active_job_id: null,
          active_job_progress: null,
        }));
        // Refetch to get fresh stage + progress (OCR just finished)
        loadBooks();
      }
    }
  } catch (e) {
    // Silent — polling failure shouldn't disrupt UI
  }
}

function getBook(bookId) {
  return books.value.find((b) => b.book_id === bookId);
}

function handleOpen(bookId) {
  emit("open-book", bookId);
}

function handleMenu(action, bookId) {
  const book = getBook(bookId);
  if (!book) return;
  if (action === "ocr") {
    selectedBookForModal.value = book;
    showOcrModal.value = true;
  } else if (action === "metadata") {
    selectedBookForModal.value = book;
    showMetadataModal.value = true;
  } else if (action === "cover") {
    coverUploadBookId.value = bookId;
    coverInputRef.value?.click();
  } else if (action === "delete") {
    confirmDelete(bookId);
  }
}

async function confirmDelete(bookId) {
  const book = getBook(bookId);
  if (!book) return;
  if (!confirm(`Xoá sách "${book.title_vi}"? (Có thể khôi phục từ books.json sau)`))
    return;
  try {
    const r = await fetch(`/api/yi-publishing/books/${bookId}`, { method: "DELETE" });
    const d = await r.json();
    if (d.status === "ok") {
      books.value = books.value.filter((b) => b.book_id !== bookId);
    } else {
      alert(`Xoá thất bại: ${d.detail || d.message}`);
    }
  } catch (e) {
    alert(`Lỗi mạng: ${e.message}`);
  }
}

async function handleCoverFileChosen(e) {
  const file = e.target.files?.[0];
  e.target.value = ""; // reset for re-pick
  if (!file || !coverUploadBookId.value) return;
  const fd = new FormData();
  fd.append("file", file);
  try {
    const r = await fetch(`/api/yi-publishing/books/${coverUploadBookId.value}/cover`, {
      method: "PUT",
      body: fd,
    });
    const d = await r.json();
    if (d.status === "ok") {
      // Force reload books to bust cover cache
      await loadBooks();
    } else {
      alert(`Đổi cover thất bại: ${d.detail || d.message}`);
    }
  } catch (e) {
    alert(`Lỗi mạng: ${e.message}`);
  } finally {
    coverUploadBookId.value = null;
  }
}

function onBookAdded(_book) {
  showAddModal.value = false;
  loadBooks();
}

function onOcrSubmitted() {
  showOcrModal.value = false;
  selectedBookForModal.value = null;
  loadJobs();
}

function onMetadataUpdated() {
  showMetadataModal.value = false;
  selectedBookForModal.value = null;
  loadBooks();
}

async function cancelJob(jobId) {
  if (!confirm("Huỷ job OCR này? Chunk hiện tại sẽ chạy xong rồi mới dừng.")) return;
  try {
    const r = await fetch(`/api/yi-publishing/jobs/${jobId}`, { method: "DELETE" });
    const d = await r.json();
    if (d.status === "ok") {
      await loadJobs();
    } else {
      alert(`Huỷ thất bại: ${d.detail || d.message}`);
    }
  } catch (e) {
    alert(`Lỗi mạng: ${e.message}`);
  }
}

// Global click handler to close menus — bubble-up close
function closeMenusOnOutside(_e) {
  // BookCard manages its own menu state internally; we just close panel here
  // Note: each BookCard re-creates menu on next open
}

onMounted(async () => {
  await loadBooks();
  await loadJobs();
  pollHandle = setInterval(loadJobs, POLL_INTERVAL_MS);
});

onBeforeUnmount(() => {
  if (pollHandle) clearInterval(pollHandle);
});
</script>

<template>
  <div class="library-view" @click="closeMenusOnOutside">
    <header class="lib-header">
      <div class="lib-title-area">
        <h1>📚 Thư viện dịch sách</h1>
        <span class="lib-subtitle">
          {{ stageCounts.all }} sách
          <template v-if="stageCounts.active > 0">
            · {{ stageCounts.active }} đang OCR
          </template>
        </span>
      </div>
      <div class="lib-actions">
        <button type="button" class="btn-primary" @click="showAddModal = true">
          ➕ Thêm sách
        </button>
      </div>
    </header>

    <!-- Job badge: active OCR jobs -->
    <JobBadge
      v-if="hasActiveJobs || allJobs.length > 0"
      :active-jobs="activeJobs"
      :recent-jobs="allJobs"
      :expanded="showJobsPanel"
      @toggle="showJobsPanel = !showJobsPanel"
      @cancel="cancelJob"
    />

    <!-- Stage filter -->
    <div class="filter-row">
      <button
        v-for="opt in [
          { key: 'all', label: 'Tất cả' },
          { key: 'active', label: '🔍 Đang OCR' },
          { key: '1', label: 'Stage 1' },
          { key: '4', label: 'Stage 4' },
          { key: '5', label: 'Stage 5' },
          { key: '6', label: 'Stage 6' },
        ]"
        :key="opt.key"
        type="button"
        :class="['filter-chip', { active: filterStage === opt.key }]"
        @click="filterStage = opt.key"
      >
        {{ opt.label }}
        <span class="filter-count">({{ stageCounts[opt.key] || 0 }})</span>
      </button>
    </div>

    <!-- Loading + empty + error -->
    <div v-if="loading" class="lib-loading">Đang tải sách...</div>
    <div v-else-if="error" class="lib-error">⚠ {{ error }}</div>
    <div v-else-if="!books.length" class="lib-empty">
      <p>Chưa có sách nào trong thư viện.</p>
      <button type="button" class="btn-primary" @click="showAddModal = true">
        ➕ Thêm sách đầu tiên
      </button>
    </div>
    <div v-else-if="!filteredBooks.length" class="lib-empty">
      <p>Không có sách nào ở filter "{{ filterStage }}".</p>
    </div>

    <!-- Gallery grid -->
    <div v-else class="book-grid">
      <BookCard
        v-for="book in filteredBooks"
        :key="book.book_id"
        :book="book"
        :active-job="
          book.active_job_id ? { progress: book.active_job_progress } : null
        "
        @open="handleOpen"
        @menu="handleMenu"
      />
    </div>

    <!-- Hidden cover file input -->
    <input
      ref="coverInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleCoverFileChosen"
    />

    <!-- Modals -->
    <AddBookModal
      v-if="showAddModal"
      @close="showAddModal = false"
      @added="onBookAdded"
    />
    <OcrJobModal
      v-if="showOcrModal && selectedBookForModal"
      :book="selectedBookForModal"
      @close="showOcrModal = false; selectedBookForModal = null"
      @submitted="onOcrSubmitted"
    />
    <EditMetadataModal
      v-if="showMetadataModal && selectedBookForModal"
      :book="selectedBookForModal"
      @close="showMetadataModal = false; selectedBookForModal = null"
      @updated="onMetadataUpdated"
    />
  </div>
</template>

<style scoped>
.library-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 1.5rem 2rem;
  min-height: calc(100vh - 200px);
}

.lib-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
}

.lib-title-area h1 {
  margin: 0;
  font-size: 1.6rem;
  color: #f0e6ff;
}

.lib-subtitle {
  color: rgba(220, 200, 240, 0.7);
  font-size: 0.92rem;
  margin-left: 0.5rem;
}

.btn-primary {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #a87cff, #7d52d8);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(168, 124, 255, 0.4);
}

/* Filter row */
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-chip {
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(168, 124, 255, 0.25);
  background: rgba(168, 124, 255, 0.08);
  color: #d8c7ff;
  font-size: 0.82rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.15s ease;
}

.filter-chip:hover {
  background: rgba(168, 124, 255, 0.18);
}

.filter-chip.active {
  background: rgba(168, 124, 255, 0.4);
  border-color: rgba(168, 124, 255, 0.7);
  color: white;
  font-weight: 600;
}

.filter-count {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  opacity: 0.75;
}

/* States */
.lib-loading,
.lib-error,
.lib-empty {
  padding: 2.5rem;
  text-align: center;
  color: rgba(220, 200, 240, 0.7);
  background: rgba(168, 124, 255, 0.05);
  border-radius: 12px;
  border: 1px dashed rgba(168, 124, 255, 0.2);
}

.lib-error {
  color: #ff9aa0;
  border-color: rgba(255, 100, 100, 0.3);
}

.lib-empty p {
  margin-bottom: 1rem;
}

/* Gallery grid */
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

@media (max-width: 700px) {
  .library-view {
    padding: 1rem;
  }
  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.8rem;
  }
}
</style>
