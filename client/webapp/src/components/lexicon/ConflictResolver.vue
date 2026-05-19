<script setup>
import { ref, onMounted } from "vue";
import { listConflicts, resolveConflict, TIER_LABEL, DIM_TYPE_LABEL, SCHOOL_LABEL } from "../../composables/useLexicon.js";

const conflicts = ref([]);
const loading = ref(false);
const error = ref("");

const filterStatus = ref("open");
const selectedPrimary = ref({});   // {conflict_group_id: mapping_id}
const anhNotes = ref({});          // {conflict_group_id: text}
const processing = ref({});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await listConflicts(filterStatus.value, 100);
    conflicts.value = data.conflicts || [];
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function resolve(cg, status) {
  const cid = cg.conflict_group_id;
  processing.value[cid] = true;
  try {
    await resolveConflict(cid, {
      primaryMappingId: status === "resolved" ? (selectedPrimary.value[cid] || null) : null,
      status,
      anhNote: anhNotes.value[cid] || ""
    });
    await load();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    processing.value[cid] = false;
  }
}

function tierColor(tier) {
  return TIER_LABEL[tier]?.color || "#94a3b8";
}

onMounted(load);
</script>

<template>
  <div class="conflict-resolver">
    <header>
      <h3>Duyệt mâu thuẫn ({{ conflicts.length }})</h3>
      <div class="controls">
        <select v-model="filterStatus" @change="load">
          <option value="open">Đang chờ duyệt</option>
          <option value="resolved">Đã duyệt</option>
          <option value="kept_all">Multi-school giữ tất cả</option>
          <option value="dismissed">Đã bỏ qua</option>
        </select>
        <button @click="load" :disabled="loading">↻ Refresh</button>
      </div>
    </header>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else-if="conflicts.length === 0" class="status empty">
      <p v-if="filterStatus === 'open'">🎉 Không có conflict nào chờ duyệt.</p>
      <p v-else>Không có item nào ở trạng thái "{{ filterStatus }}".</p>
    </div>

    <ul v-else class="conflict-list">
      <li v-for="cg in conflicts" :key="cg.conflict_group_id" class="conflict-card">
        <div class="conflict-header">
          <span class="concept-name">{{ cg.concept_vi }}</span>
          <span class="arrow">→</span>
          <span class="dim-type">{{ DIM_TYPE_LABEL[cg.dim_type] || cg.dim_type }}</span>
          <span class="status-pill" :class="`status-${cg.status}`">{{ cg.status }}</span>
        </div>

        <div class="mappings">
          <label v-for="m in cg.mappings" :key="m.mapping_id" class="mapping-option">
            <input
              v-if="cg.status === 'open'"
              type="radio"
              :name="`cg-${cg.conflict_group_id}`"
              :value="m.mapping_id"
              v-model="selectedPrimary[cg.conflict_group_id]"
            />
            <div class="mapping-content">
              <div class="mapping-head">
                <span class="tier-badge" :style="{ background: tierColor(m.source_tier) }">
                  {{ m.source_tier }}
                </span>
                <span class="dim-value">{{ m.dim_value }}</span>
                <span class="school" v-if="m.school !== 'common'">{{ SCHOOL_LABEL[m.school] || m.school }}</span>
                <span v-if="m.verified_by_anh" class="verified">✓</span>
              </div>
              <p v-if="m.reasoning_vi" class="reasoning">{{ m.reasoning_vi }}</p>
              <p v-if="m.source_quote" class="source-quote">
                "{{ m.source_quote }}"
              </p>
              <div class="provenance">
                <span v-if="m.source_book">📖 {{ m.source_book }}</span>
                <span v-if="m.source_page">tr.{{ m.source_page }}</span>
                <span v-else class="auto">{{ m.source }}</span>
              </div>
            </div>
          </label>
        </div>

        <div v-if="cg.status === 'open'" class="actions">
          <input
            v-model="anhNotes[cg.conflict_group_id]"
            type="text"
            placeholder="Ghi chú của anh (optional)..."
            class="note-input"
          />
          <button
            class="btn-primary"
            :disabled="!selectedPrimary[cg.conflict_group_id] || processing[cg.conflict_group_id]"
            @click="resolve(cg, 'resolved')"
          >
            Chọn primary
          </button>
          <button class="btn-secondary" :disabled="processing[cg.conflict_group_id]" @click="resolve(cg, 'kept_all')">
            Giữ tất cả (multi-school)
          </button>
          <button class="btn-ghost" :disabled="processing[cg.conflict_group_id]" @click="resolve(cg, 'dismissed')">
            Bỏ qua
          </button>
        </div>
        <div v-else class="resolved-note">
          <span v-if="cg.anh_note"><strong>Ghi chú:</strong> {{ cg.anh_note }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.conflict-resolver {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
header h3 {
  margin: 0;
  color: #e2e8f0;
}
.controls {
  display: flex;
  gap: 0.5rem;
}
.controls select, .controls button {
  padding: 0.35rem 0.7rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
}
.status {
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
}
.status.error { color: #f87171; }
.status.empty p { color: #34d399; font-size: 1.1rem; }

.conflict-list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.conflict-card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 6px;
  padding: 0.75rem;
}

.conflict-header {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}
.concept-name { color: #f1f5f9; font-weight: 600; }
.arrow { color: #64748b; }
.dim-type { color: #a78bfa; }
.status-pill {
  margin-left: auto;
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.7rem;
  text-transform: uppercase;
}
.status-pill.status-open { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-pill.status-resolved { background: rgba(34, 197, 94, 0.2); color: #86efac; }
.status-pill.status-kept_all { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.status-pill.status-dismissed { background: rgba(100, 116, 139, 0.2); color: #94a3b8; }

.mappings {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.mapping-option {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 4px;
  cursor: pointer;
}
.mapping-option:hover { background: rgba(167, 139, 250, 0.08); }
.mapping-option input[type="radio"] { margin-top: 0.3rem; cursor: pointer; }
.mapping-content { flex: 1; }
.mapping-head { display: flex; gap: 0.5rem; align-items: center; }
.tier-badge {
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 20px;
  text-align: center;
}
.dim-value { color: #f1f5f9; font-weight: 600; }
.school { color: #86efac; font-size: 0.75rem; }
.verified { color: #34d399; }
.reasoning {
  margin: 0.4rem 0 0.2rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}
.source-quote {
  margin: 0.4rem 0;
  padding: 0.4rem;
  background: rgba(0, 0, 0, 0.25);
  color: #cbd5e1;
  font-style: italic;
  font-size: 0.85rem;
  border-radius: 3px;
}
.provenance {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.provenance .auto { font-family: monospace; }

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}
.note-input {
  flex: 1;
  min-width: 200px;
  padding: 0.4rem 0.6rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #e2e8f0;
  border-radius: 4px;
}
.actions button {
  padding: 0.4rem 0.85rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.actions button:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-primary { background: #a78bfa; color: #1e1b4b; font-weight: 600; }
.btn-primary:hover:not(:disabled) { background: #c4b5fd; }
.btn-secondary { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.btn-secondary:hover:not(:disabled) { background: rgba(59, 130, 246, 0.35); }
.btn-ghost { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }
.btn-ghost:hover:not(:disabled) { background: rgba(100, 116, 139, 0.3); }

.resolved-note {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(34, 197, 94, 0.05);
  border-radius: 4px;
  font-size: 0.85rem;
  color: #86efac;
}
</style>
