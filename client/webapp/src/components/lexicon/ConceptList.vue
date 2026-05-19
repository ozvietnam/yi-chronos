<script setup>
import { ref, computed, watch } from "vue";
import { searchConcepts, SCHOOL_LABEL } from "../../composables/useLexicon.js";

const emit = defineEmits(["select"]);

const query = ref("");
const schoolFilter = ref("");      // empty = all
const results = ref([]);
const loading = ref(false);
const error = ref("");

const debounceTimer = ref(null);

watch(query, (val) => {
  if (debounceTimer.value) clearTimeout(debounceTimer.value);
  if (!val.trim()) {
    results.value = [];
    return;
  }
  debounceTimer.value = setTimeout(() => doSearch(), 250);
});

watch(schoolFilter, () => {
  if (query.value.trim()) doSearch();
});

async function doSearch() {
  loading.value = true;
  error.value = "";
  try {
    const schools = schoolFilter.value ? [schoolFilter.value] : null;
    const data = await searchConcepts(query.value, { schools, limit: 50 });
    results.value = data.results || [];
  } catch (e) {
    error.value = String(e.message || e);
    results.value = [];
  } finally {
    loading.value = false;
  }
}

const schoolOptions = computed(() => Object.entries(SCHOOL_LABEL));

function selectConcept(concept) {
  emit("select", concept);
}
</script>

<template>
  <div class="concept-list">
    <div class="search-bar">
      <input
        v-model="query"
        type="search"
        placeholder="Tìm concept... (vd: lá, Càn, ngũ hành)"
        class="search-input"
        autocomplete="off"
      />
      <select v-model="schoolFilter" class="school-select">
        <option value="">Mọi trường phái</option>
        <option v-for="[key, label] in schoolOptions" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
    </div>

    <div v-if="loading" class="status">Đang tìm…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else-if="!query.trim()" class="status hint">
      Gõ ít nhất 1 ký tự để tìm. Ví dụ: <em>lá, Càn, số 5, Hà Đồ, âm dương</em>
    </div>
    <div v-else-if="results.length === 0" class="status">Không tìm thấy.</div>

    <ul v-else class="results">
      <li v-for="c in results" :key="c.concept_id" @click="selectConcept(c)">
        <div class="concept-row">
          <span class="vi">{{ c.canonical_vi }}</span>
          <span v-if="c.canonical_zh" class="zh">{{ c.canonical_zh }}</span>
          <span v-if="c.canonical_en" class="en">/ {{ c.canonical_en }}</span>
        </div>
        <div class="meta">
          <span class="type">{{ c.concept_type }}</span>
          <span v-for="s in c.schools" :key="s" class="school-tag">{{ SCHOOL_LABEL[s] || s }}</span>
          <span class="source">{{ c.source }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.concept-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: 100%;
}
.search-bar {
  display: flex;
  gap: 0.5rem;
}
.search-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  font-size: 0.95rem;
}
.school-select {
  padding: 0.4rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(15, 23, 42, 0.6);
  color: #cbd5e1;
}
.status {
  padding: 0.75rem;
  color: #94a3b8;
  font-size: 0.9rem;
}
.status.error { color: #f87171; }
.status.hint em { color: #a78bfa; font-style: normal; }

.results {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}
.results li {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: background 0.15s;
}
.results li:hover {
  background: rgba(167, 139, 250, 0.08);
}
.concept-row {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  margin-bottom: 0.25rem;
}
.concept-row .vi {
  font-weight: 600;
  color: #f1f5f9;
}
.concept-row .zh {
  color: #fbbf24;
  font-size: 1rem;
}
.concept-row .en {
  color: #94a3b8;
  font-size: 0.85rem;
  font-style: italic;
}
.meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: #64748b;
}
.meta .type {
  padding: 0.1rem 0.4rem;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border-radius: 3px;
}
.meta .school-tag {
  padding: 0.1rem 0.4rem;
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
  border-radius: 3px;
}
.meta .source {
  color: #475569;
  font-family: monospace;
  font-size: 0.7rem;
}
</style>
