<script setup>
import { ref, onMounted, computed } from "vue";
import {
  listSchools,
  addSchool,
  getLibrary,
  SCHOOL_LABEL,
  TIER_LABEL
} from "../../composables/useLexicon.js";

const schools = ref([]);
const booksBySchool = ref({});
const loading = ref(false);
const error = ref("");
const selectedSchool = ref(null);
const addingNew = ref(false);
const newKey = ref("");
const newLabel = ref("");
const newColor = ref("#94a3b8");

const tiersOrdered = ["S", "A", "B", "C"];

async function load() {
  loading.value = true;
  try {
    const [sRes, lRes] = await Promise.all([
      listSchools(),
      getLibrary({})
    ]);
    schools.value = sRes.schools || [];
    // Group books by school tag
    const bySchool = {};
    for (const b of (lRes.books || [])) {
      for (const tag of (b.schools_tags || [])) {
        if (!bySchool[tag]) bySchool[tag] = [];
        bySchool[tag].push(b);
      }
    }
    booksBySchool.value = bySchool;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function submitNewSchool() {
  if (!newKey.value || !newLabel.value) return;
  try {
    await addSchool({ key: newKey.value, viLabel: newLabel.value, color: newColor.value });
    addingNew.value = false;
    newKey.value = ""; newLabel.value = ""; newColor.value = "#94a3b8";
    await load();
  } catch (e) {
    error.value = String(e.message || e);
  }
}

const selectedBooks = computed(() => {
  if (!selectedSchool.value) return [];
  return booksBySchool.value[selectedSchool.value.key] || [];
});

const schoolStats = computed(() => {
  return schools.value.map(s => ({
    ...s,
    book_count: (booksBySchool.value[s.key] || []).length
  }));
});

onMounted(load);
</script>

<template>
  <div class="schools-view">
    <header>
      <h3>🏛️ Trường phái ({{ schools.length }})</h3>
      <button class="btn-primary" @click="addingNew = true">➕ Thêm trường phái</button>
    </header>
    <p class="hint">
      Mỗi trường phái có ngôn ngữ riêng. Sách có thể thuộc nhiều trường phái cùng lúc
      (theo tuyên ngôn: đa trường phái, độc lập, đối chiếu chéo).
    </p>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="sv-body">
      <div class="schools-list">
        <button
          v-for="s in schoolStats"
          :key="s.key"
          class="school-card"
          :class="{ active: selectedSchool?.key === s.key }"
          :style="{ borderLeftColor: s.color }"
          @click="selectedSchool = s"
        >
          <div class="sc-name">{{ s.vi }}</div>
          <div class="sc-meta">
            <span class="sc-key">{{ s.key }}</span>
            <span class="sc-count">{{ s.book_count }} sách</span>
          </div>
        </button>
      </div>

      <div class="school-detail" v-if="selectedSchool">
        <h4>
          <span class="dot" :style="{ background: selectedSchool.color }"></span>
          {{ selectedSchool.vi }}
        </h4>
        <p class="meta-line">
          <code>{{ selectedSchool.key }}</code>
          · {{ selectedBooks.length }} sách trong thư viện
        </p>

        <div v-if="selectedBooks.length === 0" class="empty">
          Chưa có sách nào được gắn trường phái này.
        </div>
        <ul v-else class="book-list">
          <li v-for="b in selectedBooks" :key="b.corpus_id">
            <span class="tier-pill" :style="{ background: TIER_LABEL[b.tier]?.color || '#888' }">
              {{ b.tier }}
            </span>
            {{ b.name }}
            <span v-if="b.author" class="author">— {{ b.author }}</span>
            <span class="prog">{{ (b.progress_percent || 0).toFixed(0) }}%</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Add school modal -->
    <div v-if="addingNew" class="modal-overlay" @click.self="addingNew = false">
      <div class="modal">
        <h4>➕ Thêm trường phái mới</h4>
        <label>
          Key (slug, snake_case):
          <input v-model="newKey" placeholder="VD: phong_thuy_lac_viet" />
        </label>
        <label>
          Tên hiển thị tiếng Việt:
          <input v-model="newLabel" placeholder="VD: Phong thuỷ Lạc Việt" />
        </label>
        <label>
          Màu (hex):
          <input v-model="newColor" type="color" />
        </label>
        <div class="modal-actions">
          <button class="btn-primary" @click="submitNewSchool">Lưu</button>
          <button class="btn-ghost" @click="addingNew = false">Huỷ</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schools-view {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
header h3 { margin: 0; color: #e2e8f0; }
.btn-primary {
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-ghost {
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
}
.hint { color: #94a3b8; font-size: 0.85rem; margin: 0 0 1rem; }
.status { padding: 2rem; text-align: center; color: #94a3b8; }
.status.error { color: #f87171; }

.sv-body {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 2fr;
  gap: 1rem;
  overflow: hidden;
}
.schools-list {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding-right: 0.5rem;
}
.school-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-left: 4px solid;
  border-radius: 4px;
  padding: 0.5rem 0.7rem;
  cursor: pointer;
  text-align: left;
  color: #cbd5e1;
  transition: all 0.15s;
}
.school-card:hover { background: rgba(167, 139, 250, 0.1); }
.school-card.active {
  background: rgba(167, 139, 250, 0.15);
  border-color: #a78bfa;
}
.sc-name { font-weight: 500; color: #f1f5f9; }
.sc-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #94a3b8;
  margin-top: 0.2rem;
}
.sc-key { font-family: monospace; }

.school-detail {
  overflow-y: auto;
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 4px;
}
.school-detail h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.3rem;
  color: #f1f5f9;
}
.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.meta-line {
  color: #94a3b8;
  font-size: 0.8rem;
  margin: 0 0 1rem;
}
.meta-line code {
  background: rgba(0,0,0,0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
  font-size: 0.75rem;
}
.empty {
  text-align: center;
  padding: 1rem;
  color: #64748b;
  font-style: italic;
}
.book-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.book-list li {
  padding: 0.45rem 0.6rem;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 4px;
  color: #cbd5e1;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.tier-pill {
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.7rem;
}
.author { color: #94a3b8; font-style: italic; font-size: 0.78rem; }
.prog {
  margin-left: auto;
  color: #86efac;
  font-size: 0.75rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: #1e293b;
  padding: 1.25rem;
  border-radius: 8px;
  width: 90%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.modal h4 { margin: 0 0 0.5rem; color: #e2e8f0; }
.modal label {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
  color: #94a3b8;
}
.modal input[type="text"], .modal input:not([type="color"]) {
  padding: 0.4rem 0.6rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
}
.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

@media (max-width: 800px) {
  .sv-body { grid-template-columns: 1fr; }
}
</style>
