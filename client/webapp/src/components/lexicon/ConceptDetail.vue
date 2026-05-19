<script setup>
import { ref, watch, computed } from "vue";
import { getConcept, TIER_LABEL, DIM_TYPE_LABEL, SCHOOL_LABEL } from "../../composables/useLexicon.js";

const props = defineProps({
  concept: { type: Object, default: null }
});

const detail = ref(null);
const loading = ref(false);
const error = ref("");

watch(() => props.concept, async (c) => {
  if (!c) { detail.value = null; return; }
  loading.value = true;
  error.value = "";
  try {
    detail.value = await getConcept(c.concept_id);
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}, { immediate: true });

const mappingsByDim = computed(() => {
  if (!detail.value || !detail.value.mappings) return {};
  const groups = {};
  for (const m of detail.value.mappings) {
    const key = m.dim_type;
    if (!groups[key]) groups[key] = [];
    groups[key].push(m);
  }
  return groups;
});

function tierColor(tier) {
  return TIER_LABEL[tier]?.color || "#94a3b8";
}
</script>

<template>
  <div class="concept-detail">
    <div v-if="!concept" class="empty">
      <p>Chọn 1 concept ở danh sách bên trái để xem chi tiết.</p>
    </div>

    <div v-else-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else-if="detail" class="content">
      <header>
        <h2>
          {{ detail.concept.canonical_vi }}
          <span v-if="detail.concept.canonical_zh" class="zh">{{ detail.concept.canonical_zh }}</span>
        </h2>
        <p v-if="detail.concept.canonical_en" class="en">{{ detail.concept.canonical_en }}</p>
        <div class="header-meta">
          <span class="type-pill">{{ detail.concept.concept_type }}</span>
          <span v-for="s in detail.concept.schools" :key="s" class="school-pill">
            {{ SCHOOL_LABEL[s] || s }}
          </span>
        </div>
        <p v-if="detail.concept.notes" class="notes">{{ detail.concept.notes }}</p>
        <p v-if="detail.concept.aliases && detail.concept.aliases.length" class="aliases">
          <strong>Alias:</strong> {{ detail.concept.aliases.join(", ") }}
        </p>
      </header>

      <section>
        <h3>Mappings ({{ detail.mappings.length }})</h3>
        <div v-if="detail.mappings.length === 0" class="empty">Chưa có mapping nào.</div>
        <div v-else class="mappings-grid">
          <div v-for="(group, dimType) in mappingsByDim" :key="dimType" class="dim-group">
            <h4>{{ DIM_TYPE_LABEL[dimType] || dimType }}</h4>
            <ul>
              <li v-for="m in group" :key="m.mapping_id">
                <div class="mapping-row">
                  <span class="tier-badge" :style="{ background: tierColor(m.source_tier) }">{{ m.source_tier }}</span>
                  <span class="dim-value">{{ m.dim_value }}</span>
                  <span class="school" v-if="m.school !== 'common'">{{ SCHOOL_LABEL[m.school] || m.school }}</span>
                  <span v-if="m.verified_by_anh" class="verified" title="anh đã verify">✓</span>
                  <span v-if="m.conflict_flag" class="conflict" title="đang trong conflict group">⚠ conflict</span>
                </div>
                <p v-if="m.reasoning_vi" class="reasoning">{{ m.reasoning_vi }}</p>
                <p v-if="m.reasoning_zh" class="reasoning-zh">{{ m.reasoning_zh }}</p>
                <div v-if="m.source_quote" class="source-quote">
                  <span class="quote-mark">"</span>{{ m.source_quote }}<span class="quote-mark">"</span>
                </div>
                <div class="provenance">
                  <span v-if="m.source_book">📖 {{ m.source_book }}</span>
                  <span v-if="m.source_chapter">— {{ m.source_chapter }}</span>
                  <span v-if="m.source_page">tr.{{ m.source_page }}</span>
                  <span v-if="!m.source_book" class="auto">{{ m.source }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.concept-detail {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}
.empty, .status {
  padding: 2rem;
  color: #94a3b8;
  text-align: center;
}
.status.error { color: #f87171; }

header h2 {
  margin: 0 0 0.5rem;
  color: #f1f5f9;
  font-size: 1.5rem;
  display: flex;
  gap: 0.75rem;
  align-items: baseline;
}
header h2 .zh {
  color: #fbbf24;
  font-size: 1.2rem;
}
header .en {
  color: #94a3b8;
  font-style: italic;
  margin: 0 0 0.5rem;
}
.header-meta {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin: 0.5rem 0;
}
.type-pill {
  padding: 0.15rem 0.5rem;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border-radius: 3px;
  font-size: 0.75rem;
}
.school-pill {
  padding: 0.15rem 0.5rem;
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
  border-radius: 3px;
  font-size: 0.75rem;
}
.notes {
  margin: 0.5rem 0;
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  border-left: 3px solid #a78bfa;
  color: #cbd5e1;
  font-size: 0.9rem;
  border-radius: 0 4px 4px 0;
}
.aliases {
  font-size: 0.85rem;
  color: #94a3b8;
}
.aliases strong { color: #cbd5e1; }

section { margin-top: 1.5rem; }
section h3 {
  color: #e2e8f0;
  font-size: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.25rem;
  margin-bottom: 0.75rem;
}

.mappings-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dim-group {
  background: rgba(15, 23, 42, 0.4);
  border-radius: 6px;
  padding: 0.75rem;
}
.dim-group h4 {
  margin: 0 0 0.5rem;
  color: #a78bfa;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.dim-group ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.dim-group li {
  background: rgba(30, 41, 59, 0.5);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
}
.mapping-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.tier-badge {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 20px;
  text-align: center;
}
.dim-value {
  color: #f1f5f9;
  font-weight: 600;
}
.school { color: #86efac; font-size: 0.75rem; }
.verified { color: #34d399; }
.conflict { color: #fbbf24; font-size: 0.75rem; }
.reasoning {
  margin: 0.4rem 0 0.2rem;
  color: #cbd5e1;
  font-size: 0.85rem;
  line-height: 1.4;
}
.reasoning-zh {
  margin: 0 0 0.4rem;
  color: #fcd34d;
  font-size: 0.85rem;
  font-style: italic;
}
.source-quote {
  margin: 0.4rem 0;
  padding: 0.4rem 0.6rem;
  background: rgba(0, 0, 0, 0.25);
  color: #cbd5e1;
  font-style: italic;
  font-size: 0.85rem;
  border-radius: 3px;
}
.quote-mark { color: #a78bfa; }
.provenance {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.3rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.provenance .auto {
  font-family: monospace;
  color: #475569;
}
</style>
