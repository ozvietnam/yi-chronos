<script setup>
import { ref, onMounted, computed } from "vue";
import DoGiaiPanel from "./DoGiaiPanel.vue";
import AuspiciousDayPanel from "./AuspiciousDayPanel.vue";
import {
  getStats, getLineage, getAuthor, getConcepts, getMethods, getPassages,
  TIER_COLOR,
} from "../../composables/useWiki.js";

const stats = ref(null);
const tiers = ref([]);
const selectedAuthor = ref(null);
const concepts = ref([]);
const loadingAuthor = ref(false);
const activeSubTab = ref("lineage");  // 'lineage' | 'concepts' | 'methods' | 'passages'
const allMethods = ref([]);
const allPassages = ref([]);
const conceptFilter = ref("");

async function refresh() {
  [stats.value, tiers.value, concepts.value, allMethods.value, allPassages.value] =
    await Promise.all([getStats(), getLineage(), getConcepts(), getMethods(), getPassages()]);
}

async function onSelectAuthor(authorId) {
  loadingAuthor.value = true;
  try {
    selectedAuthor.value = await getAuthor(authorId);
  } finally {
    loadingAuthor.value = false;
  }
}

const masterAuthor = computed(() => {
  for (const t of tiers.value) {
    if (t.tier === 0 && t.authors.length) return t.authors[0];
  }
  return null;
});

const filteredConcepts = computed(() => {
  const q = conceptFilter.value.trim().toLowerCase();
  if (!q) return concepts.value;
  return concepts.value.filter(c =>
    c.canonical_vi.toLowerCase().includes(q) ||
    (c.canonical_zh || "").includes(q) ||
    (c.short_note || "").toLowerCase().includes(q)
  );
});

onMounted(async () => {
  await refresh();
  if (masterAuthor.value) await onSelectAuthor(masterAuthor.value.author_id);
});
</script>

<template>
  <div class="master-view">
    <!-- Header -->
    <header class="wv-header">
      <h2>🌌 Tổ sư - Đệ tử: Wiki Thiệu Khang Tiết</h2>
      <div v-if="stats" class="wv-stats">
        <span><b>{{ stats.authors }}</b> tác giả</span>
        <span><b>{{ stats.works }}</b> tác phẩm</span>
        <span><b>{{ stats.methods }}</b> phương pháp</span>
        <span><b>{{ stats.concepts }}</b> khái niệm</span>
        <span><b>{{ stats.passages }}</b> đoạn văn</span>
        <span><b>{{ stats.predictions }}</b> dự đoán</span>
      </div>
    </header>

    <!-- Sub tabs -->
    <nav class="wv-tabs">
      <button :class="{ active: activeSubTab === 'lineage' }" @click="activeSubTab = 'lineage'">
        🌳 Lineage
      </button>
      <button :class="{ active: activeSubTab === 'concepts' }" @click="activeSubTab = 'concepts'">
        📖 Khái niệm ({{ concepts.length }})
      </button>
      <button :class="{ active: activeSubTab === 'methods' }" @click="activeSubTab = 'methods'">
        ⚙️ Phương pháp ({{ allMethods.length }})
      </button>
      <button :class="{ active: activeSubTab === 'passages' }" @click="activeSubTab = 'passages'">
        📜 Đoạn văn ({{ allPassages.length }})
      </button>
      <button :class="{ active: activeSubTab === 'dogiai' }" @click="activeSubTab = 'dogiai'">
        🪷 Đồ Giải (sách số 2)
      </button>
      <button :class="{ active: activeSubTab === 'auspicious' }" @click="activeSubTab = 'auspicious'">
        📅 Chọn Ngày Tốt
      </button>
    </nav>

    <!-- ── LINEAGE ──────────────────────────────────────────────────── -->
    <div v-if="activeSubTab === 'lineage'" class="wv-body">
      <!-- Tree -->
      <aside class="lineage-tree">
        <section v-for="t in tiers" :key="t.tier" class="tier">
          <h3 :style="{ borderLeftColor: TIER_COLOR[t.tier] }">
            Tier {{ t.tier }} · {{ t.name }}
          </h3>
          <ul>
            <li v-for="a in t.authors" :key="a.author_id"
                :class="{ selected: selectedAuthor?.author?.author_id === a.author_id }"
                @click="onSelectAuthor(a.author_id)">
              <span class="dot" :style="{ background: TIER_COLOR[t.tier] }"></span>
              <span class="name">{{ a.name_vi }}</span>
              <span v-if="a.name_zh" class="zh">{{ a.name_zh }}</span>
              <span v-if="a.birth_year" class="years">
                {{ a.birth_year }}–{{ a.death_year || '?' }}
              </span>
            </li>
          </ul>
        </section>
      </aside>

      <!-- Author detail -->
      <main class="author-detail">
        <div v-if="loadingAuthor" class="placeholder">Đang tải…</div>
        <div v-else-if="!selectedAuthor" class="placeholder">Chọn tác giả bên trái</div>
        <template v-else>
          <h2>
            {{ selectedAuthor.author.name_vi }}
            <span v-if="selectedAuthor.author.name_zh" class="zh">
              {{ selectedAuthor.author.name_zh }}
            </span>
          </h2>
          <p class="meta">
            <span class="tier-pill" :style="{ background: TIER_COLOR[selectedAuthor.author.tier] }">
              {{ selectedAuthor.author.tier_name }}
            </span>
            <span v-if="selectedAuthor.author.era">{{ selectedAuthor.author.era }}</span>
            <span v-if="selectedAuthor.author.birth_year">
              ({{ selectedAuthor.author.birth_year }}–{{ selectedAuthor.author.death_year || '?' }})
            </span>
          </p>
          <p v-if="selectedAuthor.author.bio_summary" class="bio">
            {{ selectedAuthor.author.bio_summary }}
          </p>

          <section v-if="selectedAuthor.author.foundational_axioms?.length">
            <h3>Nguyên lý gốc</h3>
            <ul class="axiom-list">
              <li v-for="(ax, i) in selectedAuthor.author.foundational_axioms" :key="i">
                {{ ax }}
              </li>
            </ul>
          </section>

          <section v-if="selectedAuthor.works.length">
            <h3>Tác phẩm ({{ selectedAuthor.works.length }})</h3>
            <ul class="work-list">
              <li v-for="w in selectedAuthor.works" :key="w.work_id">
                <b>{{ w.title_vi }}</b>
                <span v-if="w.title_zh" class="zh">{{ w.title_zh }}</span>
                <span class="role">[{{ w.role }}]</span>
                <span v-if="w.corpus_id" class="corpus">✅ trong thư viện</span>
                <span v-else class="missing">⏳ chưa có</span>
                <div v-if="w.notes" class="note">{{ w.notes }}</div>
              </li>
            </ul>
          </section>

          <section v-if="selectedAuthor.methods.length">
            <h3>Phương pháp ({{ selectedAuthor.methods.length }})</h3>
            <ul class="method-list">
              <li v-for="m in selectedAuthor.methods" :key="m.method_id">
                <b>{{ m.name_vi }}</b>
                <span v-if="m.name_zh" class="zh">{{ m.name_zh }}</span>
                <span class="domain">[{{ m.domain }}]</span>
                <div v-if="m.notes" class="note">{{ m.notes }}</div>
              </li>
            </ul>
          </section>

          <section v-if="selectedAuthor.passages.length">
            <h3>Đoạn văn ({{ selectedAuthor.passages.length }})</h3>
            <ul class="passage-list">
              <li v-for="p in selectedAuthor.passages" :key="p.passage_id">
                <div class="anchor">
                  📜 {{ p.corpus_id }} · trang {{ p.page_start }}<span v-if="p.page_end !== p.page_start">–{{ p.page_end }}</span>
                </div>
                <div class="topic"><b>{{ p.topic }}</b></div>
                <pre>{{ p.raw_text }}</pre>
                <div v-if="p.summary_50w" class="summary">💡 {{ p.summary_50w }}</div>
              </li>
            </ul>
          </section>
        </template>
      </main>
    </div>

    <!-- ── CONCEPTS ─────────────────────────────────────────────────── -->
    <div v-else-if="activeSubTab === 'concepts'" class="wv-concepts">
      <input v-model="conceptFilter" placeholder="🔍 Lọc khái niệm…" class="filter-input" />
      <div class="concept-grid">
        <div v-for="c in filteredConcepts" :key="c.concept_id" class="concept-card">
          <div class="concept-head">
            <b>{{ c.canonical_vi }}</b>
            <span v-if="c.canonical_zh" class="zh">{{ c.canonical_zh }}</span>
          </div>
          <div v-if="c.short_note" class="note">{{ c.short_note }}</div>
          <div class="source">
            📜 trang {{ c.first_seen_page }}
          </div>
        </div>
      </div>
    </div>

    <!-- ── METHODS ──────────────────────────────────────────────────── -->
    <div v-else-if="activeSubTab === 'methods'" class="wv-methods">
      <div v-for="m in allMethods" :key="m.method_id" class="method-card">
        <div class="method-head">
          <b>{{ m.name_vi }}</b>
          <span v-if="m.name_zh" class="zh">{{ m.name_zh }}</span>
          <span class="domain-pill">[{{ m.domain }}]</span>
        </div>
        <div v-if="m.notes" class="note">{{ m.notes }}</div>
      </div>
    </div>

    <!-- ── PASSAGES ─────────────────────────────────────────────────── -->
    <div v-else-if="activeSubTab === 'passages'" class="wv-passages">
      <div v-for="p in allPassages" :key="p.passage_id" class="passage-card">
        <div class="anchor">
          📜 {{ p.corpus_id }} · trang {{ p.page_start }}<span v-if="p.page_end !== p.page_start">–{{ p.page_end }}</span>
        </div>
        <div class="topic"><b>{{ p.topic }}</b></div>
        <pre>{{ p.raw_text }}</pre>
        <div v-if="p.summary_50w" class="summary">💡 {{ p.summary_50w }}</div>
      </div>
    </div>

    <!-- ⭐ Đồ Giải — sách số 2 của Thầy -->
    <div v-else-if="activeSubTab === 'dogiai'" class="wv-dogiai">
      <DoGiaiPanel />
    </div>

    <!-- 📅 Chọn ngày tốt — Bát Tự + Mai Hoa -->
    <div v-else-if="activeSubTab === 'auspicious'" class="wv-auspicious">
      <AuspiciousDayPanel />
    </div>
  </div>
</template>

<style scoped>
.master-view {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #e2e8f0;
}

.wv-header h2 { margin: 0 0 0.4rem; }
.wv-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #94a3b8;
  flex-wrap: wrap;
}
.wv-stats b { color: #fbbf24; }

.wv-tabs {
  display: flex;
  gap: 0.25rem;
  margin: 0.75rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.wv-tabs button {
  background: transparent;
  color: #94a3b8;
  border: none;
  padding: 0.5rem 0.85rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.wv-tabs button.active {
  color: #fbbf24;
  border-bottom-color: #fbbf24;
}

.wv-body {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1rem;
  flex: 1;
  overflow: hidden;
}

.lineage-tree {
  overflow-y: auto;
  padding-right: 0.5rem;
}
.tier { margin-bottom: 1rem; }
.tier h3 {
  font-size: 0.78rem;
  margin: 0 0 0.4rem;
  padding-left: 0.5rem;
  border-left: 3px solid #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #cbd5e1;
}
.tier ul { list-style: none; padding: 0; margin: 0; }
.tier li {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.tier li:hover { background: rgba(167, 139, 250, 0.1); }
.tier li.selected { background: rgba(251, 191, 36, 0.15); }
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.name { font-weight: 500; }
.zh { color: #94a3b8; font-size: 0.85em; margin-left: 0.3rem; }
.years { color: #64748b; font-size: 0.75rem; margin-left: auto; }

.author-detail {
  overflow-y: auto;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
  padding: 1rem;
}
.author-detail h2 { margin: 0 0 0.3rem; color: #e2e8f0; }
.author-detail .meta {
  display: flex;
  gap: 0.6rem;
  margin: 0 0 0.6rem;
  color: #94a3b8;
  font-size: 0.85rem;
  align-items: center;
}
.tier-pill {
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 600;
  font-size: 0.75rem;
}
.bio {
  color: #cbd5e1;
  font-size: 0.9rem;
  margin: 0 0 1rem;
  line-height: 1.5;
}
.author-detail h3 {
  font-size: 0.85rem;
  color: #fbbf24;
  margin: 0.75rem 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.axiom-list, .work-list, .method-list, .passage-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.axiom-list li {
  padding: 0.4rem 0.75rem;
  background: rgba(251, 191, 36, 0.08);
  border-left: 2px solid #fbbf24;
  margin-bottom: 0.3rem;
  border-radius: 3px;
  color: #fef3c7;
  font-size: 0.88rem;
}
.work-list li, .method-list li {
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.03);
  border-radius: 4px;
  margin-bottom: 0.35rem;
  font-size: 0.88rem;
}
.role, .domain {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-left: 0.3rem;
}
.corpus { color: #34d399; font-size: 0.75rem; margin-left: 0.5rem; }
.missing { color: #f87171; font-size: 0.75rem; margin-left: 0.5rem; }
.note {
  color: #94a3b8;
  font-size: 0.8rem;
  margin-top: 0.2rem;
  font-style: italic;
}
.passage-list li {
  padding: 0.6rem 0.75rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.anchor { font-size: 0.75rem; color: #64748b; margin-bottom: 0.2rem; }
.topic { color: #cbd5e1; margin-bottom: 0.4rem; }
pre {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.85rem;
  color: #e2e8f0;
  background: transparent;
  margin: 0;
}
.summary {
  margin-top: 0.4rem;
  color: #c4b5fd;
  font-size: 0.82rem;
  font-style: italic;
}

/* Concepts grid */
.wv-concepts { flex: 1; overflow-y: auto; }
.filter-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(255,255,255,0.15);
  color: #e2e8f0;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}
.concept-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.5rem;
}
.concept-card {
  background: rgba(15,23,42,0.55);
  border-radius: 4px;
  padding: 0.6rem 0.75rem;
  border-left: 2px solid #a78bfa;
}
.concept-head b { color: #e2e8f0; }
.source { font-size: 0.7rem; color: #64748b; margin-top: 0.3rem; }

/* Methods grid */
.wv-methods, .wv-passages { flex: 1; overflow-y: auto; }
.method-card, .passage-card {
  background: rgba(15,23,42,0.55);
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.method-head { margin-bottom: 0.3rem; }
.domain-pill {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  background: rgba(167,139,250,0.2);
  color: #c4b5fd;
  border-radius: 3px;
  font-size: 0.7rem;
  margin-left: 0.4rem;
}

.placeholder {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}
</style>
