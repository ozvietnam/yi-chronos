<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import {
  runResearch,
  getResearchJob,
  listResearchJobs,
  getResearchReport,
  applyResearchCatalog,
  RESEARCH_STATUS_LABEL,
  RESEARCH_PROVIDERS,
  RESEARCH_RETRIEVERS
} from "../composables/useYiResearch.js";
import { renderMarkdown } from "../lib/markdown.js";

const query = ref("");
const provider = ref("ollama");
const model = ref("qwen3:32b");
const retriever = ref("duckduckgo");
const catalogSync = ref(true);
const catalogApply = ref(false);

const running = ref(false);
const currentJob = ref(null);
const currentReport = ref(null);
const jobs = ref([]);
const error = ref("");
const message = ref("");

let pollInterval = null;

const providers = RESEARCH_PROVIDERS;
const retrievers = RESEARCH_RETRIEVERS;

function onProviderChange() {
  const p = providers.find(x => x.value === provider.value);
  if (p) model.value = p.defaultModel;
}

async function loadJobs() {
  try {
    const r = await listResearchJobs({ limit: 20 });
    jobs.value = r.jobs || [];
  } catch (e) { /* ignore */ }
}

async function startResearch() {
  if (!query.value.trim()) return;
  error.value = "";
  message.value = "";
  running.value = true;
  try {
    const r = await runResearch({
      query: query.value,
      provider: provider.value,
      model: model.value,
      retriever: retriever.value,
      catalogSync: catalogSync.value,
      catalogApply: catalogApply.value
    });
    if (r.status === "ok") {
      message.value = `🔄 Job ${r.job_id} đã bắt đầu — Ollama qwen3:32b sẽ mất 2-5 phút`;
      currentJob.value = { job_id: r.job_id, status: "running", query: query.value };
      currentReport.value = null;
      startPolling(r.job_id);
      await loadJobs();
    } else {
      error.value = r.error || "Lỗi khi start research";
      running.value = false;
    }
  } catch (e) {
    error.value = String(e.message || e);
    running.value = false;
  }
}

function startPolling(jobId) {
  stopPolling();
  pollInterval = setInterval(async () => {
    try {
      const r = await getResearchJob(jobId);
      if (r.status === "ok") {
        currentJob.value = r.job;
        if (r.job.status === "done") {
          stopPolling();
          running.value = false;
          // Load full report
          const rep = await getResearchReport(jobId);
          if (rep.status === "ok") {
            currentReport.value = rep;
          }
          await loadJobs();
        } else if (r.job.status === "error") {
          stopPolling();
          running.value = false;
          error.value = r.job.error || "Job failed";
          await loadJobs();
        }
      }
    } catch (e) { /* keep polling */ }
  }, 5000);
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

async function loadJobReport(jobId) {
  try {
    const rep = await getResearchReport(jobId);
    if (rep.status === "ok") {
      currentReport.value = rep;
      currentJob.value = jobs.value.find(j => j.job_id === jobId) || null;
    } else {
      error.value = rep.message || "Báo cáo chưa sẵn sàng";
    }
  } catch (e) {
    error.value = String(e.message || e);
  }
}

async function applyCatalogNow() {
  if (!currentJob.value) return;
  try {
    const r = await applyResearchCatalog(currentJob.value.job_id);
    if (r.status === "ok") {
      message.value = `✓ Đã apply ${r.new?.length || 0} tools vào catalog`;
    }
  } catch (e) {
    error.value = String(e.message || e);
  }
}

// renderMarkdown now imported from ../lib/markdown.js — escape-first + safe links
// (was unsafe: rendered web-sourced report HTML + javascript: links via v-html → XSS #22).

const renderedReport = computed(() => renderMarkdown(currentReport.value?.markdown || ""));

const elapsedSeconds = computed(() => {
  if (!currentJob.value?.started_at) return 0;
  const end = currentJob.value.finished_at || Math.floor(Date.now() / 1000);
  return end - currentJob.value.started_at;
});

onMounted(loadJobs);
onUnmounted(stopPolling);
</script>

<template>
  <div class="research-panel">
    <header class="page-head">
      <h2>🔬 Research Agent</h2>
      <p class="hint">
        Autonomous AI research — em delegate task tìm existing solutions cho agent
        (GPT Researcher + Ollama free local). 2-5 phút mỗi research, output markdown
        report với 10-20 citations + auto-detect tool mới.
      </p>
    </header>

    <p v-if="message" class="msg ok">{{ message }}</p>
    <p v-if="error" class="msg error">{{ error }}</p>

    <!-- Query form -->
    <section class="query-section">
      <textarea
        v-model="query"
        rows="2"
        placeholder="Ví dụ: best Vietnamese OCR tools 2026, vector databases comparison, audio transcription Vietnamese..."
        :disabled="running"
      ></textarea>
      <div class="form-row">
        <label>
          <span>Provider:</span>
          <select v-model="provider" @change="onProviderChange" :disabled="running">
            <option v-for="p in providers" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </label>
        <label>
          <span>Model:</span>
          <input v-model="model" type="text" :disabled="running" />
        </label>
        <label>
          <span>Search engine:</span>
          <select v-model="retriever" :disabled="running">
            <option v-for="r in retrievers" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </label>
      </div>
      <div class="form-row">
        <label class="cb">
          <input v-model="catalogSync" type="checkbox" :disabled="running"/>
          Auto-extract tool mới vào catalog
        </label>
        <label class="cb" v-if="catalogSync">
          <input v-model="catalogApply" type="checkbox" :disabled="running"/>
          Apply ngay (không dry-run)
        </label>
      </div>
      <div class="form-row">
        <button class="btn-primary" :disabled="!query.trim() || running" @click="startResearch">
          {{ running ? "🔄 Đang research..." : "🔬 Bắt đầu research" }}
        </button>
      </div>
    </section>

    <!-- Current job status -->
    <section v-if="currentJob" class="job-status">
      <header>
        <strong>Job hiện tại</strong>
        <span class="status-badge" :style="{ color: RESEARCH_STATUS_LABEL[currentJob.status]?.color }">
          {{ RESEARCH_STATUS_LABEL[currentJob.status]?.label }}
        </span>
      </header>
      <div class="job-meta">
        <div><strong>Query:</strong> {{ currentJob.query }}</div>
        <div v-if="currentJob.provider"><strong>Provider:</strong> {{ currentJob.provider }}:{{ currentJob.model }}</div>
        <div><strong>Elapsed:</strong> {{ elapsedSeconds }}s</div>
        <div v-if="currentJob.sources_count > 0">
          <strong>Sources:</strong> {{ currentJob.sources_count }}
        </div>
        <div v-if="currentJob.new_tools?.length">
          <strong>🆕 Tools mới:</strong> {{ currentJob.new_tools.join(", ") }}
        </div>
      </div>
      <details v-if="currentJob.progress_log?.length" class="progress-log">
        <summary>Progress log ({{ currentJob.progress_log.length }} events)</summary>
        <pre>{{ currentJob.progress_log.join("\n") }}</pre>
      </details>
    </section>

    <!-- Report viewer -->
    <section v-if="currentReport" class="report-section">
      <header>
        <strong>📋 Report</strong>
        <div class="report-meta">
          {{ currentReport.duration_seconds }}s · {{ currentReport.sources_count }} sources
          <span v-if="currentReport.cost_usd > 0">· ${{ currentReport.cost_usd.toFixed(4) }}</span>
        </div>
      </header>
      <div v-if="currentReport.new_tools?.length" class="new-tools-callout">
        <strong>🆕 {{ currentReport.new_tools.length }} tools mới phát hiện:</strong>
        <span v-for="t in currentReport.new_tools" :key="t" class="tool-chip">{{ t }}</span>
        <button class="btn-small" @click="applyCatalogNow">
          📥 Apply vào catalog
        </button>
      </div>
      <article class="report-content" v-html="renderedReport"></article>
    </section>

    <!-- Recent jobs -->
    <section class="recent-jobs">
      <header><strong>📚 Research lịch sử ({{ jobs.length }})</strong></header>
      <div v-if="jobs.length === 0" class="empty">
        Chưa có research nào. Nhập query trên + bấm 🔬.
      </div>
      <ul v-else class="job-list">
        <li v-for="j in jobs" :key="j.job_id" class="job-item"
            :class="{ active: currentJob?.job_id === j.job_id }">
          <div class="ji-head">
            <span class="status-badge"
                  :style="{ color: RESEARCH_STATUS_LABEL[j.status]?.color }">
              {{ RESEARCH_STATUS_LABEL[j.status]?.label }}
            </span>
            <span class="ji-query">{{ j.query }}</span>
          </div>
          <div class="ji-meta">
            <code>{{ j.job_id }}</code>
            · {{ j.provider }}:{{ j.model }}
            · {{ j.sources_count || 0 }} sources
            <span v-if="j.new_tools?.length">· 🆕 {{ j.new_tools.length }}</span>
            <button v-if="j.status === 'done'" class="btn-tiny" @click="loadJobReport(j.job_id)">
              📋 View
            </button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.research-panel {
  padding: 1rem;
  color: #e2e8f0;
  max-width: 1100px;
  margin: 0 auto;
}
.page-head h2 { color: #c4b5fd; margin: 0 0 0.3rem; }
.hint { color: #94a3b8; font-size: 0.85rem; margin: 0 0 1rem; }

.msg {
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  margin-bottom: 0.8rem;
  font-size: 0.9rem;
}
.msg.ok { background: rgba(34, 197, 94, 0.15); color: #86efac; }
.msg.error { background: rgba(239, 68, 68, 0.1); color: #fca5a5; }

.query-section {
  background: rgba(15, 23, 42, 0.55);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.query-section textarea {
  width: 100%;
  padding: 0.6rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
  font-size: 0.9rem;
  resize: vertical;
  margin-bottom: 0.6rem;
}
.form-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}
.form-row label {
  display: flex;
  flex-direction: column;
  font-size: 0.78rem;
  color: #94a3b8;
  gap: 0.2rem;
  flex: 1;
  min-width: 180px;
}
.form-row label.cb {
  flex-direction: row;
  align-items: center;
  gap: 0.4rem;
}
.form-row select, .form-row input {
  padding: 0.35rem 0.5rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
  font-size: 0.85rem;
}
.btn-primary {
  padding: 0.5rem 1.2rem;
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.92rem;
}
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-small {
  padding: 0.3rem 0.7rem;
  background: rgba(167, 139, 250, 0.2);
  color: #c4b5fd;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.78rem;
  margin-left: 0.5rem;
}
.btn-tiny {
  padding: 0.15rem 0.5rem;
  background: rgba(96, 165, 250, 0.15);
  color: #93c5fd;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.72rem;
  margin-left: auto;
}

.job-status {
  background: rgba(96, 165, 250, 0.08);
  border-left: 3px solid #60a5fa;
  border-radius: 4px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}
.job-status header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.status-badge { font-size: 0.85rem; }
.job-meta { font-size: 0.85rem; }
.job-meta > div { margin-bottom: 0.2rem; }
.job-meta strong { color: #94a3b8; }
.progress-log {
  margin-top: 0.5rem;
  font-size: 0.78rem;
}
.progress-log summary { cursor: pointer; color: #94a3b8; }
.progress-log pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 3px;
  max-height: 200px;
  overflow: auto;
  font-size: 0.72rem;
  color: #cbd5e1;
}

.report-section {
  background: rgba(15, 23, 42, 0.55);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.report-section header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.report-section header strong { color: #cbd5e1; }
.report-meta { color: #94a3b8; font-size: 0.78rem; }

.new-tools-callout {
  background: rgba(251, 191, 36, 0.08);
  border-left: 3px solid #fbbf24;
  padding: 0.5rem 0.7rem;
  border-radius: 3px;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
}
.new-tools-callout strong { color: #fbbf24; }
.tool-chip {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border-radius: 3px;
  margin: 0 0.15rem;
  font-size: 0.78rem;
}

.report-content {
  background: rgba(15, 23, 42, 0.7);
  padding: 1rem 1.25rem;
  border-radius: 4px;
  font-size: 0.9rem;
  line-height: 1.6;
  max-height: 600px;
  overflow-y: auto;
}
.report-content :deep(h1), .report-content :deep(h2), .report-content :deep(h3) {
  color: #c4b5fd;
  margin: 1rem 0 0.4rem;
}
.report-content :deep(code) {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
  font-size: 0.82rem;
}
.report-content :deep(a) {
  color: #93c5fd;
  text-decoration: underline;
}
.report-content :deep(li) {
  margin-left: 1.2rem;
}

.recent-jobs header { margin-bottom: 0.5rem; color: #cbd5e1; }
.recent-jobs .empty { color: #64748b; padding: 1rem; text-align: center; }
.job-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.job-item {
  background: rgba(15, 23, 42, 0.4);
  border-radius: 4px;
  padding: 0.5rem 0.7rem;
}
.job-item.active {
  background: rgba(167, 139, 250, 0.12);
  border-left: 3px solid #a78bfa;
}
.ji-head {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.2rem;
}
.ji-query { color: #f1f5f9; font-size: 0.88rem; flex: 1; }
.ji-meta {
  font-size: 0.72rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.ji-meta code { background: rgba(0, 0, 0, 0.3); padding: 0.05rem 0.3rem; border-radius: 2px; }
</style>
