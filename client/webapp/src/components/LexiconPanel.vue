<script setup>
import { ref, onMounted } from "vue";
import ConceptList from "./lexicon/ConceptList.vue";
import ConceptDetail from "./lexicon/ConceptDetail.vue";
import ConflictResolver from "./lexicon/ConflictResolver.vue";
import DistillQueue from "./lexicon/DistillQueue.vue";
import LibraryView from "./lexicon/LibraryView.vue";
import SchoolsView from "./lexicon/SchoolsView.vue";
import {
  getLexiconStats,
  getCurrentReadingWeek,
  TIER_LABEL
} from "../composables/useLexicon.js";

const activeView = ref("library");  // 'library' | 'browse' | 'schools' | 'conflicts' | 'distill' | 'reading'
const selectedConcept = ref(null);
const stats = ref(null);
const currentWeek = ref(null);
const loadingStats = ref(false);
const error = ref("");

async function loadDashboard() {
  loadingStats.value = true;
  error.value = "";
  try {
    const [s, w] = await Promise.all([
      getLexiconStats(),
      getCurrentReadingWeek().catch(() => ({ current_week: null }))
    ]);
    stats.value = s.stats;
    currentWeek.value = w.current_week;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loadingStats.value = false;
  }
}

onMounted(loadDashboard);

function onConceptSelect(c) {
  selectedConcept.value = c;
}
</script>

<template>
  <div class="lexicon-panel">
    <!-- Stats banner -->
    <div class="dashboard">
      <div v-if="loadingStats" class="loading">Đang tải…</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <template v-else-if="stats">
        <div class="stat-card">
          <div class="stat-value">{{ stats.concepts }}</div>
          <div class="stat-label">Concepts</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.mappings }}</div>
          <div class="stat-label">Mappings</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.contextual_meanings }}</div>
          <div class="stat-label">Contextual</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.corpora }}</div>
          <div class="stat-label">Sách đã ingest</div>
        </div>
        <div v-if="currentWeek" class="reading-card">
          <div class="rc-label">Reading plan — Tuần {{ currentWeek.week }}</div>
          <div class="rc-title">{{ currentWeek.label }}</div>
          <div class="rc-meta">
            <span v-for="s in currentWeek.schools" :key="s" class="school-chip">{{ s }}</span>
            <span class="book-count">{{ (currentWeek.books || []).length }} sách</span>
          </div>
        </div>
      </template>
    </div>

    <!-- Sub-nav tabs -->
    <nav class="sub-tabs">
      <button :class="{ active: activeView === 'library' }" @click="activeView = 'library'">
        📚 Thư viện
      </button>
      <button :class="{ active: activeView === 'browse' }" @click="activeView = 'browse'">
        🔍 Browse concepts
      </button>
      <button :class="{ active: activeView === 'schools' }" @click="activeView = 'schools'">
        🏛️ Trường phái
      </button>
      <button :class="{ active: activeView === 'conflicts' }" @click="activeView = 'conflicts'">
        ⚠️ Duyệt mâu thuẫn
      </button>
      <button :class="{ active: activeView === 'distill' }" @click="activeView = 'distill'">
        🧪 Distill queue
      </button>
      <button :class="{ active: activeView === 'reading' }" @click="activeView = 'reading'">
        📅 Reading plan
      </button>
    </nav>

    <!-- Library view (default landing) -->
    <div v-if="activeView === 'library'" class="full-view">
      <LibraryView />
    </div>

    <!-- Schools view -->
    <div v-else-if="activeView === 'schools'" class="full-view">
      <SchoolsView />
    </div>

    <!-- Browse view (split: list + detail) -->
    <div v-else-if="activeView === 'browse'" class="browse-view">
      <div class="list-pane">
        <ConceptList @select="onConceptSelect" />
      </div>
      <div class="detail-pane">
        <ConceptDetail :concept="selectedConcept" />
      </div>
    </div>

    <!-- Conflicts view -->
    <div v-else-if="activeView === 'conflicts'" class="full-view">
      <ConflictResolver />
    </div>

    <!-- Distill queue view -->
    <div v-else-if="activeView === 'distill'" class="full-view">
      <DistillQueue />
    </div>

    <!-- Reading plan view -->
    <div v-else-if="activeView === 'reading'" class="full-view reading-view">
      <h3>Kế hoạch đọc sách (6 tuần)</h3>
      <p class="hint">Đọc TUẦN TỰ theo trường phái. Sau mỗi tuần STOP, review conflicts trước khi tiếp.</p>
      <div v-if="!currentWeek" class="loading">Đang tải…</div>
      <div v-else class="reading-detail">
        <h4>{{ currentWeek.label }} ({{ currentWeek.status }})</h4>
        <p><strong>Trường phái:</strong> {{ (currentWeek.schools || []).join(", ") }}</p>
        <p><strong>Sách trong tuần:</strong></p>
        <ul>
          <li v-for="b in (currentWeek.books || [])" :key="b">{{ b }}</li>
        </ul>
        <p v-if="currentWeek.philosophy" class="philosophy">{{ currentWeek.philosophy }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lexicon-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 600px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
}

.dashboard {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-wrap: wrap;
}
.stat-card {
  flex: 0 0 auto;
  min-width: 110px;
  padding: 0.75rem 1rem;
  background: rgba(99, 102, 241, 0.12);
  border-radius: 6px;
  text-align: center;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #c4b5fd;
}
.stat-label {
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.2rem;
}

.reading-card {
  flex: 1;
  min-width: 240px;
  padding: 0.75rem 1rem;
  background: rgba(34, 197, 94, 0.08);
  border-radius: 6px;
  border-left: 3px solid #86efac;
}
.rc-label {
  font-size: 0.7rem;
  color: #86efac;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.rc-title {
  font-size: 0.95rem;
  color: #f1f5f9;
  margin: 0.2rem 0;
  font-weight: 600;
}
.rc-meta {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
}
.school-chip {
  padding: 0.1rem 0.4rem;
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  border-radius: 3px;
}
.book-count { color: #94a3b8; }

.sub-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.sub-tabs button {
  padding: 0.4rem 0.85rem;
  background: transparent;
  border: 1px solid transparent;
  color: #94a3b8;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s;
}
.sub-tabs button:hover {
  background: rgba(167, 139, 250, 0.08);
  color: #c4b5fd;
}
.sub-tabs button.active {
  background: rgba(167, 139, 250, 0.15);
  border-color: rgba(167, 139, 250, 0.3);
  color: #c4b5fd;
}

.browse-view {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(300px, 1fr) 2fr;
  gap: 0;
  min-height: 500px;
  overflow: hidden;
}
.list-pane {
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.detail-pane {
  overflow: hidden;
}

.full-view {
  flex: 1;
  overflow: hidden;
}

.reading-view {
  padding: 1rem;
  overflow-y: auto;
}
.reading-view h3 { color: #e2e8f0; margin-top: 0; }
.reading-view .hint { color: #94a3b8; font-size: 0.85rem; }
.reading-detail {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
}
.reading-detail h4 { color: #c4b5fd; }
.reading-detail ul { color: #cbd5e1; line-height: 1.6; }
.philosophy {
  margin-top: 1rem;
  padding: 0.5rem;
  background: rgba(167, 139, 250, 0.08);
  border-left: 3px solid #a78bfa;
  color: #c4b5fd;
  font-style: italic;
}

.loading, .error {
  padding: 1rem;
  color: #94a3b8;
}
.error { color: #f87171; }

@media (max-width: 800px) {
  .browse-view {
    grid-template-columns: 1fr;
  }
  .detail-pane {
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }
}
</style>
