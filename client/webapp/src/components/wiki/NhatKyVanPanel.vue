<script setup>
/**
 * NhatKyVanPanel — Phase 2A GOAL.
 * Ghi nhật ký việc thực + auto-snapshot 7 vòng quẻ.
 *
 * ⚠️ Iron Rule #4: KHÔNG predict cát/hung. Đây là SỔ GHI.
 * Sau N tháng/năm → pattern mining (Phase 3).
 */
import { ref, computed, onMounted } from "vue";

const entries = ref([]);
const stats = ref({});
const loading = ref(false);
const error = ref("");

// Form create
const form = ref({
  happened_at_iso: new Date().toISOString().slice(0, 16),  // YYYY-MM-DDTHH:MM
  title: "",
  body: "",
  tags: "",
  importance: 3,
  sentiment: "chua_ro",
});

// Selected entry (drawer)
const selectedEntry = ref(null);

// Sentiment options
const SENTIMENT_OPTIONS = [
  { value: "chua_ro", label: "Chưa rõ", color: "#94a3b8" },
  { value: "thuan",   label: "Thuận",  color: "#10b981" },
  { value: "binh",    label: "Bình",   color: "#fbbf24" },
  { value: "nghich",  label: "Nghịch", color: "#f87171" },
];
const IMPORTANCE_OPTIONS = [
  { value: 1, label: "1 — nhỏ" },
  { value: 2, label: "2" },
  { value: 3, label: "3 — vừa" },
  { value: 4, label: "4" },
  { value: 5, label: "5 — định mệnh" },
];

async function loadEntries() {
  loading.value = true;
  try {
    const r = await fetch("/api/yi-wiki/nhat-ky/list", { credentials: "include" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    entries.value = d.entries || [];
    stats.value = d.stats || {};
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function createEntry() {
  if (!form.value.title.trim()) {
    error.value = "Title bắt buộc";
    return;
  }
  error.value = "";
  loading.value = true;
  try {
    const body = {
      happened_at_iso: form.value.happened_at_iso.replace("T", " "),
      title: form.value.title,
      body: form.value.body,
      tags: form.value.tags.split(",").map(s => s.trim()).filter(Boolean),
      importance: parseInt(form.value.importance),
      sentiment: form.value.sentiment,
    };
    const r = await fetch("/api/yi-wiki/nhat-ky/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    // Reset form
    form.value.title = "";
    form.value.body = "";
    form.value.tags = "";
    form.value.happened_at_iso = new Date().toISOString().slice(0, 16);
    await loadEntries();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function updateOutcome(entry, outcome, sentiment) {
  try {
    const r = await fetch(`/api/yi-wiki/nhat-ky/update-outcome/${entry.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ outcome, sentiment }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    await loadEntries();
    if (selectedEntry.value?.id === entry.id) {
      const d = await r.json();
      selectedEntry.value = d.entry;
    }
  } catch (e) {
    error.value = String(e.message || e);
  }
}

async function deleteEntry(entry) {
  if (!confirm(`Xóa entry "${entry.title}"?`)) return;
  try {
    const r = await fetch(`/api/yi-wiki/nhat-ky/delete/${entry.id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    if (selectedEntry.value?.id === entry.id) selectedEntry.value = null;
    await loadEntries();
  } catch (e) {
    error.value = String(e.message || e);
  }
}

function sentimentColor(s) {
  return SENTIMENT_OPTIONS.find(o => o.value === s)?.color || "#94a3b8";
}
function sentimentLabel(s) {
  return SENTIMENT_OPTIONS.find(o => o.value === s)?.label || s;
}

function formatDate(iso) {
  return iso.replace("T", " ").slice(0, 16);
}

function getSnapshotSummary(entry) {
  const snap = entry.luu_van_snapshot || {};
  const items = [];
  for (let i = 1; i <= 7; i++) {
    const key = Object.keys(snap).find(k => k.startsWith(`vong_${i}_`));
    if (key && snap[key]?.chinh) {
      const c = snap[key].chinh;
      items.push({
        label: snap[key].paradigm_meta?.ten || `Vòng ${i}`,
        name: c.name_vi || c.name,
        zh: c.name_zh,
        number: c.number,
        hao: snap[key].moving_line,
      });
    }
  }
  return items;
}

const outcomeForm = ref({});
function openOutcome(entry) {
  outcomeForm.value = { ...entry, _outcome: entry.outcome || "", _sentiment: entry.sentiment || "chua_ro" };
  selectedEntry.value = entry;
  llmReadback.value = "";
  llmReadbackError.value = "";
}
function saveOutcome() {
  if (!selectedEntry.value) return;
  updateOutcome(selectedEntry.value, outcomeForm.value._outcome, outcomeForm.value._sentiment);
}

// V5 — LLM đọc lại
const llmReadback = ref("");
const llmReadbackLoading = ref(false);
const llmReadbackError = ref("");

async function callLLMReadback() {
  if (!selectedEntry.value) return;
  llmReadbackLoading.value = true;
  llmReadbackError.value = "";
  llmReadback.value = "";
  try {
    const r = await fetch("/api/yi-wiki/nhat-ky/llm-doc-lai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ entry_id: selectedEntry.value.id }),
    });
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    const d = await r.json();
    llmReadback.value = d.narrative || "(LLM trả về empty)";
  } catch (e) {
    llmReadbackError.value = String(e.message || e);
  } finally {
    llmReadbackLoading.value = false;
  }
}

function renderMd(s) {
  if (!s) return "";
  return s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/_([^_]+)_/g, "<i>$1</i>")
    .replace(/\n/g, "<br>");
}

onMounted(loadEntries);
</script>

<template>
  <div class="nky">
    <header class="nky-head">
      <h3>📓 Nhật ký vận — gắn việc thực × 7 quẻ tại thời điểm</h3>
      <p class="subtitle">
        Tổ sư Khang Tiết: ghi việc → snapshot 7 vòng quẻ → sau N tháng pattern mới hiện. <b>KHÔNG predict cát/hung.</b>
      </p>
    </header>

    <!-- Stats -->
    <div v-if="stats.total" class="nky-stats">
      <span><b>{{ stats.total }}</b> entry</span>
      <span v-for="(n, s) in stats.by_sentiment" :key="s">
        <span :style="{color: sentimentColor(s)}">●</span> {{ sentimentLabel(s) }}: {{ n }}
      </span>
    </div>

    <!-- Form Create -->
    <details class="nky-form" open>
      <summary>✍️ Ghi việc mới</summary>
      <div class="form-grid">
        <label>
          <span>Title <span class="req">*</span></span>
          <input v-model="form.title" placeholder="Ký deal X / Họp gia đình / Quyết định Y..." />
        </label>
        <label>
          <span>Thời điểm xảy ra</span>
          <input type="datetime-local" v-model="form.happened_at_iso" />
        </label>
        <label class="full">
          <span>Nội dung (tùy chọn)</span>
          <textarea v-model="form.body" rows="2" placeholder="Bối cảnh, người liên quan..."></textarea>
        </label>
        <label>
          <span>Tags (phẩy)</span>
          <input v-model="form.tags" placeholder="deal, kho, thuan" />
        </label>
        <label>
          <span>Importance</span>
          <select v-model="form.importance">
            <option v-for="o in IMPORTANCE_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>
        <label>
          <span>Sentiment (ban đầu)</span>
          <select v-model="form.sentiment">
            <option v-for="o in SENTIMENT_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>
      </div>
      <button class="btn-save" @click="createEntry" :disabled="loading">
        {{ loading ? '⏳ Đang lưu...' : '💾 Lưu + snapshot 7 quẻ' }}
      </button>
    </details>

    <div v-if="error" class="nky-error">{{ error }}</div>

    <!-- Timeline list -->
    <div v-if="entries.length" class="nky-timeline">
      <h4>📜 {{ entries.length }} entry gần nhất</h4>
      <div v-for="e in entries" :key="e.id" class="entry-card"
           :class="{ active: selectedEntry?.id === e.id }"
           @click="openOutcome(e)">
        <div class="e-header">
          <span class="e-time">{{ formatDate(e.happened_at_iso) }}</span>
          <span class="e-imp" :title="`Importance: ${e.importance}/5`">
            {{ '★'.repeat(e.importance) }}<span class="dim">{{ '☆'.repeat(5 - e.importance) }}</span>
          </span>
          <span class="e-sent" :style="{color: sentimentColor(e.sentiment)}">● {{ sentimentLabel(e.sentiment) }}</span>
        </div>
        <div class="e-title">{{ e.title }}</div>
        <div v-if="e.tags?.length" class="e-tags">
          <code v-for="t in e.tags" :key="t">{{ t }}</code>
        </div>
        <div class="e-snapshot">
          <span v-for="(s, i) in getSnapshotSummary(e)" :key="i" class="snap-pill"
                :title="`${s.label} — hào động ${s.hao}`">
            <small>#{{ s.number }}</small> {{ s.name }}<sup v-if="s.zh && s.zh !== '?'" class="zh">{{ s.zh }}</sup>
          </span>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="nky-empty">
      Chưa có entry nào. Ghi việc đầu tiên bên trên để bắt đầu nhật ký vận.
    </div>

    <!-- Drawer chi tiết -->
    <aside v-if="selectedEntry" class="nky-drawer">
      <div class="drawer-head">
        <button class="drawer-close" @click="selectedEntry = null">✕</button>
        <span class="drawer-title">{{ selectedEntry.title }}</span>
      </div>
      <div class="drawer-body">
        <p class="drawer-time">📅 {{ formatDate(selectedEntry.happened_at_iso) }}</p>
        <p v-if="selectedEntry.body" class="drawer-body-text">{{ selectedEntry.body }}</p>

        <h5>7 vòng quẻ tại thời điểm</h5>
        <div class="drawer-snap-grid">
          <div v-for="(s, i) in getSnapshotSummary(selectedEntry)" :key="i" class="dsg-cell">
            <div class="dsg-label">{{ s.label }}</div>
            <div class="dsg-name">#{{ s.number }} {{ s.name }}<sup v-if="s.zh && s.zh !== '?'">{{ s.zh }}</sup></div>
            <div class="dsg-hao">Hào động: <b>{{ s.hao }}</b></div>
          </div>
        </div>

        <h5>Update outcome (sau khi việc xong)</h5>
        <label>
          <span>Outcome thực tế</span>
          <textarea v-model="outcomeForm._outcome" rows="3" placeholder="Việc đã xong, kết quả thế nào..."></textarea>
        </label>
        <label>
          <span>Sentiment cuối</span>
          <select v-model="outcomeForm._sentiment">
            <option v-for="o in SENTIMENT_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>
        <div class="drawer-actions">
          <button class="btn-save" @click="saveOutcome">💾 Lưu outcome</button>
          <button class="btn-llm" @click="callLLMReadback" :disabled="llmReadbackLoading">
            {{ llmReadbackLoading ? '⏳ Đang đọc...' : '🤖 LLM đọc lại' }}
          </button>
          <button class="btn-del" @click="deleteEntry(selectedEntry)">🗑 Xóa</button>
        </div>

        <!-- V5 — LLM readback result -->
        <div v-if="llmReadbackError" class="nky-error">{{ llmReadbackError }}</div>
        <div v-if="llmReadback" class="llm-readback">
          <h5>📜 LLM phản chiếu việc × paradigm</h5>
          <article v-html="renderMd(llmReadback)"></article>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.nky {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px;
  margin: 0.5rem 0;
  position: relative;
}
.nky-head h3 { margin: 0; color: #34d399; font-size: 1rem; }
.subtitle { color: #94a3b8; font-style: italic; font-size: 0.82rem; margin: 0.3rem 0 0.8rem; }

.nky-stats {
  display: flex; gap: 1rem; flex-wrap: wrap; padding: 0.5rem 0.8rem;
  background: rgba(52, 211, 153, 0.05); border-radius: 5px;
  font-size: 0.82rem; color: #cbd5e1; margin-bottom: 0.8rem;
}

.nky-form {
  background: rgba(52, 211, 153, 0.05);
  border: 1px solid rgba(52, 211, 153, 0.2);
  border-radius: 6px;
  padding: 0.5rem 0.8rem 0.8rem;
  margin-bottom: 1rem;
}
.nky-form summary { cursor: pointer; color: #34d399; font-weight: 600; padding: 0.3rem 0; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem; }
.form-grid label.full { grid-column: span 2; }
.form-grid label { display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.8rem; color: #cbd5e1; }
.form-grid input, .form-grid textarea, .form-grid select {
  background: #1e1b4b; color: #e0e7ff; border: 1px solid rgba(196, 181, 253, 0.3);
  padding: 0.3rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
}
.form-grid .req { color: #f87171; }
.btn-save, .btn-del {
  padding: 0.4rem 0.9rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem;
  margin-top: 0.5rem; border: none;
}
.btn-save { background: rgba(52, 211, 153, 0.25); border: 1px solid rgba(52, 211, 153, 0.5); color: #34d399; }
.btn-save:hover { background: rgba(52, 211, 153, 0.35); }
.btn-del { background: rgba(248, 113, 113, 0.18); border: 1px solid rgba(248, 113, 113, 0.4); color: #f87171; margin-left: 0.5rem; }
.btn-del:hover { background: rgba(248, 113, 113, 0.3); }

.nky-error { color: #f87171; padding: 0.4rem 0.8rem; background: rgba(248, 113, 113, 0.08); border-left: 2px solid #f87171; border-radius: 4px; margin-bottom: 0.5rem; }
.nky-empty { padding: 2rem; text-align: center; color: #6b7280; font-style: italic; }

.nky-timeline h4 { color: #fcd34d; margin: 0 0 0.5rem; font-size: 0.95rem; }
.entry-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(196, 181, 253, 0.15);
  border-left: 3px solid #34d399;
  border-radius: 5px; padding: 0.55rem 0.75rem; margin-bottom: 0.45rem;
  cursor: pointer; transition: all .15s;
}
.entry-card:hover { background: rgba(52, 211, 153, 0.05); }
.entry-card.active { background: rgba(52, 211, 153, 0.1); border-left-color: #fcd34d; }
.e-header { display: flex; gap: 0.6rem; align-items: center; font-size: 0.75rem; margin-bottom: 0.2rem; flex-wrap: wrap; }
.e-time { color: #94a3b8; font-family: monospace; }
.e-imp { color: #fbbf24; letter-spacing: 1px; }
.e-imp .dim { color: rgba(251, 191, 36, 0.3); }
.e-sent { font-size: 0.75rem; }
.e-title { color: #fcd34d; font-weight: 600; margin-bottom: 0.2rem; font-size: 0.93rem; }
.e-tags { display: flex; gap: 0.3rem; flex-wrap: wrap; margin-bottom: 0.3rem; }
.e-tags code { background: rgba(196, 181, 253, 0.12); color: #c4b5fd; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; }
.e-snapshot { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.snap-pill {
  background: rgba(252, 211, 77, 0.08); color: #fde68a;
  padding: 1px 5px; border-radius: 3px; font-size: 0.7rem;
  border: 1px solid rgba(252, 211, 77, 0.2);
}
.snap-pill small { color: #fcd34d; margin-right: 2px; }
.snap-pill sup.zh { color: #c4b5fd; font-size: 0.7em; }

/* Drawer */
.nky-drawer {
  position: fixed; top: 60px; right: 0; bottom: 0; width: 480px; max-width: 90vw;
  background: #0f172a; border-left: 2px solid #34d399; z-index: 100;
  display: flex; flex-direction: column; box-shadow: -4px 0 20px rgba(0,0,0,0.4);
}
.drawer-head {
  padding: 0.6rem 0.9rem; background: #064e3b; color: white;
  display: flex; gap: 0.7rem; align-items: center;
}
.drawer-close {
  background: rgba(255,255,255,0.18); border: none; color: white;
  padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer;
}
.drawer-close:hover { background: rgba(255,255,255,0.3); }
.drawer-title { font-weight: 600; }
.drawer-body { flex: 1; overflow-y: auto; padding: 1rem; }
.drawer-time { color: #94a3b8; font-family: monospace; margin: 0 0 0.5rem; }
.drawer-body-text { color: #cbd5e1; background: rgba(15, 23, 42, 0.5); padding: 0.5rem 0.7rem; border-radius: 4px; line-height: 1.5; }
.drawer-body h5 { color: #fcd34d; margin: 1rem 0 0.4rem; font-size: 0.9rem; }
.drawer-snap-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; }
.dsg-cell { background: rgba(252, 211, 77, 0.05); border: 1px solid rgba(252, 211, 77, 0.2); border-radius: 4px; padding: 0.4rem 0.55rem; font-size: 0.78rem; }
.dsg-label { color: #94a3b8; font-size: 0.7rem; }
.dsg-name { color: #fcd34d; font-weight: 600; margin: 0.15rem 0; }
.dsg-hao { color: #cbd5e1; font-size: 0.75rem; }
.drawer-body label { display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.82rem; color: #cbd5e1; margin: 0.5rem 0; }
.drawer-body textarea, .drawer-body select {
  background: #1e1b4b; color: #e0e7ff; border: 1px solid rgba(196, 181, 253, 0.3);
  padding: 0.3rem 0.5rem; border-radius: 4px;
}
.drawer-actions { display: flex; gap: 0.5rem; margin-top: 0.8rem; flex-wrap: wrap; }
.btn-llm {
  background: rgba(167, 139, 250, 0.2); border: 1px solid rgba(167, 139, 250, 0.5);
  color: #c4b5fd; padding: 0.4rem 0.85rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem;
}
.btn-llm:hover { background: rgba(167, 139, 250, 0.3); }
.btn-llm:disabled { opacity: 0.6; cursor: wait; }
.llm-readback {
  margin-top: 1rem; padding: 0.7rem 0.9rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.06), rgba(252,211,77,0.04));
  border: 1px solid rgba(167,139,250,0.3); border-radius: 6px;
}
.llm-readback h5 { color: #c4b5fd; margin: 0 0 0.5rem; font-size: 0.92rem; }
.llm-readback article { color: #e2e8f0; line-height: 1.65; font-size: 0.88rem; }
.llm-readback :deep(b) { color: #fcd34d; }
.llm-readback :deep(i) { color: #fde68a; }

@media (max-width: 700px) {
  .form-grid { grid-template-columns: 1fr; }
  .form-grid label.full { grid-column: span 1; }
  .nky-drawer { width: 100%; }
  .drawer-snap-grid { grid-template-columns: 1fr; }
}
</style>
