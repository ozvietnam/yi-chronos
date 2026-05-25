<script setup>
/**
 * BookCard — single book card in LibraryView gallery.
 *
 * Props:
 *   book          — Object: { book_id, title_vi, hanzi_title, author, page_count,
 *                              cover_url, stage, stage_label, progress }
 *   activeJob     — Object | null: { progress: { current, total, stage } }
 *
 * Emits:
 *   open(book_id)            — user wants to open this book in Workspace
 *   menu(action, book_id)    — menu action: cover | ocr | metadata | delete
 */
import { computed, ref } from "vue";

const props = defineProps({
  book: { type: Object, required: true },
  activeJob: { type: Object, default: null },
});
const emit = defineEmits(["open", "menu"]);

const menuOpen = ref(false);

const ocrPct = computed(() => {
  if (props.activeJob?.progress) {
    const { current, total } = props.activeJob.progress;
    return total > 0 ? Math.round((current / total) * 100) : 0;
  }
  return props.book.progress?.ocr_pct || 0;
});

const ocrText = computed(() => {
  if (props.activeJob?.progress) {
    const { current, total } = props.activeJob.progress;
    return `OCR đang chạy: ${current}/${total}`;
  }
  const done = props.book.progress?.ocr_pages_done || 0;
  const total = props.book.progress?.ocr_pages_total || props.book.page_count || 0;
  return total > 0 ? `OCR: ${done}/${total} trang` : "OCR: chưa scan";
});

const transPct = computed(() => props.book.progress?.translation_pct || 0);

const transText = computed(() => {
  const done = props.book.progress?.translation_lines_done || 0;
  const total = props.book.progress?.translation_lines_total || 0;
  return total > 0 ? `Dịch: ${done}/${total} dòng` : "Dịch: chưa bắt đầu";
});

const stageBadgeClass = computed(() => {
  const stage = props.book.stage || 1;
  return `stage-badge stage-${stage}`;
});

const coverUrl = computed(() => props.book.cover_url || "");
const hasActiveJob = computed(() => !!props.activeJob);

function handleOpen() {
  emit("open", props.book.book_id);
}

function handleMenu(action, e) {
  e?.stopPropagation();
  emit("menu", action, props.book.book_id);
  menuOpen.value = false;
}

function toggleMenu(e) {
  e?.stopPropagation();
  menuOpen.value = !menuOpen.value;
}
</script>

<template>
  <div class="book-card" :class="{ 'has-job': hasActiveJob }" @click="handleOpen">
    <!-- Cover image -->
    <div class="cover-wrap">
      <img
        v-if="coverUrl"
        :src="coverUrl"
        :alt="book.title_vi"
        class="cover-img"
        loading="lazy"
      />
      <div v-else class="cover-placeholder">
        <span class="placeholder-icon">📖</span>
        <span class="placeholder-text">{{ book.title_vi }}</span>
      </div>
      <div v-if="hasActiveJob" class="cover-overlay">
        <span class="overlay-spinner">🔍</span>
        <span class="overlay-label">Đang OCR…</span>
      </div>
    </div>

    <!-- Metadata -->
    <div class="card-body">
      <h3 class="card-title-vi">{{ book.title_vi }}</h3>
      <div v-if="book.hanzi_title" class="card-title-zh">{{ book.hanzi_title }}</div>
      <div class="card-meta">
        <span v-if="book.author">{{ book.author }}</span>
        <span v-if="book.page_count > 0"> · {{ book.page_count }} trang</span>
      </div>

      <!-- Stage badge -->
      <div :class="stageBadgeClass">
        🏷️ Stage {{ book.stage }}: {{ book.stage_label }}
      </div>

      <!-- Progress bars -->
      <div class="progress-section">
        <div class="progress-row">
          <span class="progress-icon">🔍</span>
          <div class="progress-bar-wrap">
            <div class="progress-bar" :style="{ width: ocrPct + '%' }"></div>
          </div>
          <span class="progress-pct">{{ ocrPct }}%</span>
        </div>
        <div class="progress-label">{{ ocrText }}</div>

        <div class="progress-row">
          <span class="progress-icon">✍️</span>
          <div class="progress-bar-wrap">
            <div class="progress-bar progress-trans" :style="{ width: transPct + '%' }"></div>
          </div>
          <span class="progress-pct">{{ transPct }}%</span>
        </div>
        <div class="progress-label">{{ transText }}</div>
      </div>

      <!-- Actions -->
      <div class="card-actions">
        <button
          type="button"
          class="btn-open"
          @click.stop="handleOpen"
          :title="book.progress?.ocr_pct > 0 ? 'Mở để dịch' : 'Cần OCR trước'"
        >
          📖 Mở để dịch
        </button>
        <div class="menu-wrap">
          <button
            type="button"
            class="btn-menu"
            @click="toggleMenu"
            :aria-expanded="menuOpen"
            aria-haspopup="true"
            title="Thêm hành động"
          >
            ⋯
          </button>
          <div v-if="menuOpen" class="menu-dropdown" @click.stop>
            <button type="button" @click="handleMenu('ocr', $event)">
              🔍 Đặt scan OCR
            </button>
            <button type="button" @click="handleMenu('cover', $event)">
              🖼️ Đổi cover
            </button>
            <button type="button" @click="handleMenu('metadata', $event)">
              ✏️ Sửa metadata
            </button>
            <hr />
            <button type="button" class="menu-danger" @click="handleMenu('delete', $event)">
              🗑️ Xoá sách
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-card {
  display: flex;
  flex-direction: column;
  background: var(--card-bg, #1a1226);
  border: 1px solid var(--card-border, rgba(168, 124, 255, 0.18));
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  position: relative;
}

.book-card:hover {
  transform: translateY(-3px);
  border-color: rgba(168, 124, 255, 0.5);
  box-shadow: 0 8px 24px rgba(74, 38, 142, 0.35);
}

.book-card.has-job {
  border-color: rgba(255, 200, 100, 0.5);
  animation: pulse 2.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(255, 200, 100, 0.15); }
  50% { box-shadow: 0 4px 24px rgba(255, 200, 100, 0.35); }
}

/* Cover */
.cover-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  background: #15101e;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  text-align: center;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 0.5rem;
}

.placeholder-text {
  font-size: 0.85rem;
  font-weight: 600;
}

.cover-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.6rem 0.8rem;
  background: linear-gradient(transparent, rgba(255, 180, 60, 0.95));
  color: #2a1a05;
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.overlay-spinner {
  animation: spin 1.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Body */
.card-body {
  display: flex;
  flex-direction: column;
  padding: 0.85rem 1rem 1rem;
  flex: 1;
  gap: 0.5rem;
}

.card-title-vi {
  margin: 0;
  font-size: 0.98rem;
  line-height: 1.3;
  color: #f5f0ff;
  font-weight: 600;
}

.card-title-zh {
  font-size: 0.85rem;
  color: rgba(200, 180, 240, 0.85);
  font-family: "Source Han Serif SC", "Songti SC", serif;
}

.card-meta {
  font-size: 0.78rem;
  color: rgba(220, 200, 240, 0.65);
  margin-bottom: 0.2rem;
}

.stage-badge {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.72rem;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  background: rgba(168, 124, 255, 0.18);
  color: #d8c7ff;
  font-weight: 500;
}

.stage-badge.stage-1 { background: rgba(120, 120, 120, 0.25); color: #c0c0c0; }
.stage-badge.stage-2 { background: rgba(80, 140, 220, 0.22); color: #a3c8ff; }
.stage-badge.stage-3 { background: rgba(100, 180, 200, 0.22); color: #a8e0e8; }
.stage-badge.stage-4 { background: rgba(255, 180, 60, 0.22); color: #ffd88a; }
.stage-badge.stage-5 { background: rgba(168, 124, 255, 0.25); color: #e0c8ff; }
.stage-badge.stage-6 { background: rgba(80, 200, 130, 0.25); color: #9cf0bf; }

/* Progress */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin-top: 0.3rem;
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
}

.progress-icon {
  width: 1rem;
  text-align: center;
}

.progress-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ffb74d, #ff9800);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.progress-bar.progress-trans {
  background: linear-gradient(90deg, #a87cff, #7d52d8);
}

.progress-pct {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  min-width: 2.5em;
  text-align: right;
  color: #e0d3ff;
}

.progress-label {
  font-size: 0.7rem;
  color: rgba(200, 180, 240, 0.55);
  padding-left: 1.4rem;
  margin-bottom: 0.2rem;
}

/* Actions */
.card-actions {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.5rem;
}

.btn-open {
  flex: 1;
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(168, 124, 255, 0.5);
  background: rgba(168, 124, 255, 0.18);
  color: #e8d8ff;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-open:hover {
  background: rgba(168, 124, 255, 0.35);
}

.menu-wrap {
  position: relative;
}

.btn-menu {
  width: 2.2rem;
  padding: 0.5rem 0;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e8d8ff;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
}

.btn-menu:hover {
  background: rgba(255, 255, 255, 0.14);
}

.menu-dropdown {
  position: absolute;
  right: 0;
  bottom: calc(100% + 6px);
  min-width: 180px;
  background: #2a1f3a;
  border: 1px solid rgba(168, 124, 255, 0.35);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  z-index: 10;
  padding: 0.3rem 0;
  display: flex;
  flex-direction: column;
}

.menu-dropdown button {
  background: transparent;
  border: none;
  color: #e8d8ff;
  text-align: left;
  padding: 0.5rem 0.9rem;
  font-size: 0.83rem;
  cursor: pointer;
}

.menu-dropdown button:hover {
  background: rgba(168, 124, 255, 0.2);
}

.menu-dropdown hr {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin: 0.25rem 0;
}

.menu-dropdown .menu-danger {
  color: #ff9aa0;
}

.menu-dropdown .menu-danger:hover {
  background: rgba(255, 100, 100, 0.18);
}
</style>
