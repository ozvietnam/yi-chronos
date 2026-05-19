<script setup>
import { ref, computed, watch, onMounted } from "vue";
import {
  getRestorationPlan,
  createRestorationPlan,
  advancePlanPhase,
  markPlanBatch,
  appendPlanNote,
  PHASE_LABEL,
  PHASE_STATUS_LABEL,
  BATCH_STATUS_LABEL
} from "../../composables/useLexicon.js";

const props = defineProps({
  corpusId: { type: Number, required: true }
});
const emit = defineEmits(["close"]);

const plan = ref(null);
const markdownText = ref("");
const loading = ref(false);
const creating = ref(false);
const error = ref("");
const newNote = ref("");
const noteTarget = ref("general");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await getRestorationPlan(props.corpusId);
    if (r.status === "no_plan") {
      plan.value = null;
      markdownText.value = "";
    } else if (r.status === "ok") {
      plan.value = r.plan;
      markdownText.value = r.markdown || "";
    } else {
      error.value = r.message || "Lỗi không xác định";
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function makePlan(overwrite = false) {
  creating.value = true;
  try {
    const r = await createRestorationPlan(props.corpusId, { overwrite });
    if (r.status === "ok") {
      plan.value = r.plan;
      await load();
    } else {
      error.value = r.message;
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    creating.value = false;
  }
}

async function nextPhase(to) {
  if (!confirm(`Anh chắc chắn chuyển sang Phase ${to}? (Phase ${to-1} đã thực sự xong chưa?)`)) return;
  await advancePlanPhase(props.corpusId, to);
  await load();
}

async function toggleBatch(b) {
  const next = b.status === "done" ? "pending" : "done";
  await markPlanBatch(props.corpusId, b.batch_id, { status: next });
  await load();
}

async function addNote() {
  if (!newNote.value.trim()) return;
  await appendPlanNote(props.corpusId, newNote.value, { target: noteTarget.value });
  newNote.value = "";
  await load();
}

const phase1Progress = computed(() => {
  if (!plan.value) return 0;
  const total = plan.value.phase1_batches.length || 1;
  const done = plan.value.phase1_batches.filter(b => b.status === "done").length;
  return Math.round((done / total) * 100);
});

watch(() => props.corpusId, load);
onMounted(load);
</script>

<template>
  <div class="plan-panel">
    <header>
      <h4>📋 Kế hoạch phục chế</h4>
      <button class="close-btn" @click="emit('close')">✕</button>
    </header>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <!-- No plan yet -->
    <div v-else-if="!plan" class="empty">
      <p>📝 Chưa có kế hoạch phục chế cho cuốn này.</p>
      <p class="hint">
        Em sẽ phân tích sách (sample 5 trang, đo chất lượng OCR, chia batch) rồi trình anh duyệt.
        <strong>KHÔNG</strong> tự động chạy pipeline.
      </p>
      <button class="btn-primary" :disabled="creating" @click="makePlan(false)">
        {{ creating ? "Đang phân tích…" : "📋 Lập kế hoạch" }}
      </button>
    </div>

    <!-- Plan exists -->
    <div v-else class="plan-body">
      <!-- Phase tracker -->
      <div class="phase-tracker">
        <div
          v-for="phaseNum in [1, 2, 3]"
          :key="phaseNum"
          class="phase-node"
          :class="{
            active: plan.current_phase === phaseNum,
            done: plan.current_phase > phaseNum
          }"
          :style="{ borderColor: PHASE_LABEL[phaseNum].color }"
        >
          <div class="phase-num" :style="{ background: PHASE_LABEL[phaseNum].color }">
            {{ PHASE_LABEL[phaseNum].short }}
          </div>
          <div class="phase-info">
            <div class="phase-name">{{ PHASE_LABEL[phaseNum].label }}</div>
            <div class="phase-status">
              {{ PHASE_STATUS_LABEL[plan[`phase${phaseNum}_status`]]?.label }}
            </div>
          </div>
        </div>
      </div>

      <!-- Plan meta -->
      <div class="meta-row">
        <div>
          <strong>{{ plan.book_name }}</strong>
          <span class="tag">{{ plan.tier }}</span>
        </div>
        <div class="meta-pages">
          {{ plan.pages_total }} trang · ETA Phase 1: {{ plan.phase1_eta_hours.toFixed(1) }}h
        </div>
      </div>

      <!-- Sample analysis -->
      <div class="sample">
        <strong>📊 Sample analysis:</strong>
        Chất lượng <span :class="`q-${plan.sample_quality}`">{{ plan.sample_quality }}</span>
        · Hán: {{ plan.has_chinese ? "✓" : "—" }}
        · Footnote: {{ plan.has_footnotes ? "✓" : "—" }}
      </div>

      <!-- Risks -->
      <div v-if="plan.risks?.length" class="risks">
        <strong>⚠️ Rủi ro:</strong>
        <ul><li v-for="r in plan.risks" :key="r">{{ r }}</li></ul>
      </div>

      <!-- Phase 1 batches -->
      <section class="phase-section">
        <header>
          <strong>Phase 1 — Phục dựng nguyên văn</strong>
          <span class="pct">{{ phase1Progress }}%</span>
        </header>
        <div class="bar"><div class="fill" :style="{ width: phase1Progress + '%' }"></div></div>
        <ul class="batch-list">
          <li v-for="b in plan.phase1_batches" :key="b.batch_id"
              class="batch-item" :class="`batch-${b.status}`"
              @click="toggleBatch(b)">
            <span class="batch-icon" :style="{ color: BATCH_STATUS_LABEL[b.status].color }">
              {{ BATCH_STATUS_LABEL[b.status].icon }}
            </span>
            <span class="batch-id">{{ b.batch_id }}</span>
            <span class="batch-range">trang {{ b.page_start }}–{{ b.page_end }}</span>
            <span class="batch-prog">{{ b.pages_done }}/{{ b.page_end - b.page_start + 1 }}</span>
          </li>
        </ul>
        <div class="phase-actions" v-if="plan.current_phase === 1">
          <button class="btn-ghost" @click="nextPhase(2)"
                  :disabled="phase1Progress < 80">
            ✓ Phase 1 xong → chuyển Phase 2 (đọc sâu)
          </button>
        </div>
      </section>

      <!-- Phase 2 -->
      <section v-if="plan.current_phase >= 2" class="phase-section">
        <header><strong>Phase 2 — Đọc kỹ đọc sâu</strong></header>
        <p class="phase-note">{{ plan.phase2_notes || "(Chưa có ghi chú — anh đang đọc + ghi nhận đoạn cốt lõi)" }}</p>
        <div class="phase-actions" v-if="plan.current_phase === 2">
          <button class="btn-ghost" @click="nextPhase(3)">
            ✓ Phase 2 xong → chuyển Phase 3 (wiki+mapping)
          </button>
        </div>
      </section>

      <!-- Phase 3 -->
      <section v-if="plan.current_phase >= 3" class="phase-section">
        <header><strong>Phase 3 — Wiki + Mapping</strong></header>
        <p class="phase-note">{{ plan.phase3_notes || "(Chưa có ghi chú)" }}</p>
      </section>

      <!-- Add note -->
      <section class="note-input">
        <textarea v-model="newNote" rows="2" placeholder="Ghi chú thêm…"></textarea>
        <div class="note-actions">
          <select v-model="noteTarget">
            <option value="general">Chung</option>
            <option value="phase2">Phase 2 — đọc sâu</option>
            <option value="phase3">Phase 3 — wiki</option>
          </select>
          <button class="btn-primary" @click="addNote" :disabled="!newNote.trim()">
            Thêm note
          </button>
        </div>
      </section>

      <!-- Refresh + raw markdown -->
      <details class="raw-md">
        <summary>Xem plan.md raw ({{ markdownText.length }} chars)</summary>
        <pre>{{ markdownText }}</pre>
      </details>

      <div class="bottom-actions">
        <button class="btn-warning" @click="makePlan(true)">⚠️ Tạo lại plan (overwrite)</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plan-panel {
  padding: 0.75rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
header h4 { margin: 0; color: #c4b5fd; }
.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
}
.status { padding: 1rem; text-align: center; color: #94a3b8; }
.status.error { color: #f87171; }
.empty {
  padding: 1rem;
  text-align: center;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 5px;
}
.empty .hint { font-size: 0.75rem; color: #94a3b8; margin: 0.5rem 0; }
.btn-primary {
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.5; }
.btn-ghost {
  background: rgba(100, 116, 139, 0.15);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.35rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-ghost:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-warning {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
  border: 1px solid rgba(251, 146, 60, 0.3);
  padding: 0.3rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}

.phase-tracker {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}
.phase-node {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem;
  border-left: 3px solid #475569;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 3px;
  opacity: 0.55;
}
.phase-node.active { opacity: 1; box-shadow: 0 0 0 1px rgba(167, 139, 250, 0.3); }
.phase-node.done { opacity: 0.85; }
.phase-num {
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.7rem;
}
.phase-info { flex: 1; min-width: 0; }
.phase-name {
  font-size: 0.72rem;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.phase-status { font-size: 0.65rem; color: #94a3b8; }

.meta-row {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 3px;
  margin-bottom: 0.5rem;
}
.tag {
  padding: 0.1rem 0.35rem;
  background: #a78bfa;
  color: #1e1b4b;
  border-radius: 3px;
  font-size: 0.7rem;
  margin-left: 0.4rem;
}
.meta-pages { color: #94a3b8; font-size: 0.75rem; }

.sample { font-size: 0.75rem; margin: 0.3rem 0; }
.q-good { color: #86efac; }
.q-medium { color: #fbbf24; }
.q-mờ { color: #f87171; }

.risks {
  margin: 0.5rem 0;
  padding: 0.4rem 0.6rem;
  background: rgba(251, 191, 36, 0.08);
  border-left: 3px solid #fbbf24;
  border-radius: 3px;
  font-size: 0.78rem;
  color: #fbbf24;
}
.risks ul { margin: 0.2rem 0 0 1rem; padding: 0; color: #cbd5e1; }

.phase-section {
  margin: 0.75rem 0;
  padding: 0.5rem 0.6rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 4px;
}
.phase-section header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
}
.phase-section header strong { color: #cbd5e1; }
.pct { color: #86efac; font-size: 0.78rem; }
.bar {
  height: 4px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}
.fill {
  height: 100%;
  background: linear-gradient(to right, #818cf8, #c4b5fd);
  transition: width 0.3s;
}
.batch-list { list-style: none; padding: 0; margin: 0; }
.batch-item {
  display: grid;
  grid-template-columns: 24px 90px 1fr 60px;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.4rem;
  cursor: pointer;
  border-radius: 3px;
  font-size: 0.78rem;
  transition: background 0.15s;
}
.batch-item:hover { background: rgba(167, 139, 250, 0.08); }
.batch-item.batch-done { opacity: 0.6; }
.batch-icon { font-size: 1rem; text-align: center; }
.batch-id { font-family: monospace; color: #94a3b8; font-size: 0.72rem; }
.batch-range { color: #cbd5e1; }
.batch-prog { color: #64748b; font-size: 0.7rem; text-align: right; }
.phase-actions { margin-top: 0.5rem; }
.phase-note {
  margin: 0.3rem 0;
  padding: 0.4rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 3px;
  font-size: 0.78rem;
  white-space: pre-wrap;
  color: #94a3b8;
}

.note-input {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 4px;
}
.note-input textarea {
  width: 100%;
  padding: 0.3rem 0.4rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.8rem;
  resize: vertical;
}
.note-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 0.4rem;
}
.note-actions select {
  padding: 0.25rem 0.4rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  border-radius: 3px;
  font-size: 0.75rem;
}

.raw-md {
  margin-top: 0.75rem;
  font-size: 0.72rem;
}
.raw-md summary {
  cursor: pointer;
  color: #94a3b8;
  padding: 0.3rem;
}
.raw-md pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 3px;
  font-size: 0.7rem;
  max-height: 300px;
  overflow: auto;
  color: #cbd5e1;
  white-space: pre-wrap;
}

.bottom-actions { margin-top: 0.75rem; text-align: right; }
</style>
