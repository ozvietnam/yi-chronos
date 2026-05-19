<script setup>
/**
 * TuViPersonSwitcher — widget chọn person + chạy phân tích đầy đủ + xuất PDF.
 *
 * Hiển thị: dropdown (mặc định = currentPerson auth), nút "⚡ Phân tích đầy đủ",
 * nút "📄 Xuất PDF". Tất cả Tử Vi panels đọc theo `tuviPerson` từ store.
 */
import { ref, onMounted, computed, watch } from "vue";
import {
  tuviPerson, tuviPersonKey, tuviPersonName, setTuviPerson,
  availablePersons, fetchAvailablePersons,
  runFullPipelineBackground, pollJobStatus, pdfReportUrl,
} from "../stores/tuviPersonStore.js";
import { isAuthenticated, currentPerson } from "../stores/authStore.js";

const job = ref(null);
const pollTimer = ref(null);
const pdfBusy = ref(false);
const pdfError = ref("");

const personOptions = computed(() => {
  const list = availablePersons.value || [];
  if (!list.length && currentPerson.value) return [currentPerson.value];
  return list;
});

function onSelect(e) {
  const pid = e.target.value;
  const p = personOptions.value.find((x) => (x.person_id || x.person_key) === pid);
  if (p) setTuviPerson(p);
}

async function runFull() {
  pdfError.value = "";
  job.value = null;
  try {
    const r = await runFullPipelineBackground(tuviPersonKey.value);
    if (r.status === "queued") {
      job.value = { job_id: r.job_id, status: "queued", progress: 0, total_steps: 4 };
      pollTimer.value = setInterval(async () => {
        const j = await pollJobStatus(r.job_id);
        if (j.status === "ok") {
          job.value = j;
          if (j.status === "done" || j.status === "error") {
            clearInterval(pollTimer.value);
            pollTimer.value = null;
            // Trigger panels reload via custom event
            window.dispatchEvent(new CustomEvent("tuvi-analysis-updated", { detail: { person_key: tuviPersonKey.value } }));
          }
        }
      }, 1500);
    } else {
      pdfError.value = r.detail || r.message || "Lỗi queue";
    }
  } catch (e) {
    pdfError.value = e.message;
  }
}

async function exportPdf() {
  pdfBusy.value = true; pdfError.value = "";
  try {
    const url = pdfReportUrl(tuviPersonKey.value);
    // Use anchor click to trigger browser download
    const a = document.createElement("a");
    a.href = url;
    a.download = `bao-cao-la-so-${tuviPersonKey.value}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (e) {
    pdfError.value = e.message;
  } finally {
    setTimeout(() => { pdfBusy.value = false; }, 1500);
  }
}

const progressPct = computed(() => {
  const j = job.value;
  if (!j || !j.total_steps) return 0;
  return Math.round((j.progress / j.total_steps) * 100);
});

onMounted(() => {
  fetchAvailablePersons();
});

watch(isAuthenticated, () => fetchAvailablePersons());
</script>

<template>
  <div class="tps-wrap">
    <div class="tps-row">
      <label class="tps-label">📊 Phân tích lá số của:</label>
      <select class="tps-select" :value="tuviPersonKey" @change="onSelect">
        <option v-for="p in personOptions" :key="p.person_id || p.person_key" :value="p.person_id || p.person_key">
          {{ p.name || p.full_name || p.person_id }}
          <template v-if="p.birth_datetime_local">— {{ p.birth_datetime_local.slice(0, 10) }}</template>
        </option>
      </select>
      <button class="tps-btn tps-run" @click="runFull"
              :disabled="job && (job.status === 'queued' || job.status === 'running')">
        ⚡ Phân tích đầy đủ
      </button>
      <button class="tps-btn tps-pdf" @click="exportPdf" :disabled="pdfBusy">
        {{ pdfBusy ? "⏳" : "📄" }} Xuất PDF
      </button>
    </div>

    <div v-if="job" class="tps-job">
      <div class="tps-bar">
        <div class="tps-fill" :style="{ width: progressPct + '%' }"></div>
      </div>
      <div class="tps-status">
        <span v-if="job.status === 'queued' || job.status === 'running'">
          ⏳ {{ job.current_step || 'queued' }} — {{ job.progress || 0 }}/{{ job.total_steps || 4 }} ({{ progressPct }}%)
        </span>
        <span v-else-if="job.status === 'done'" class="tps-done">
          ✅ Xong! Cost ${{ (job.cost_usd || 0).toFixed(4) }} · {{ tuviPersonName }} sẵn sàng.
        </span>
        <span v-else-if="job.status === 'error'" class="tps-err">
          ❌ {{ job.error }}
        </span>
      </div>
    </div>

    <div v-if="pdfError" class="tps-err">{{ pdfError }}</div>
  </div>
</template>

<style scoped>
.tps-wrap {
  background: linear-gradient(135deg, rgba(217,119,6,0.08), rgba(217,119,6,0.02));
  border: 1px solid rgba(217,119,6,0.25); border-radius: 6px;
  padding: 0.6rem 0.9rem; margin: 0.5rem 0 1rem;
}
.tps-row {
  display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;
}
.tps-label { color: #fde68a; font-weight: 600; font-size: 0.88rem; }
.tps-select {
  background: #1e293b; border: 1px solid #475569; color: #f1f5f9;
  padding: 0.35rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
  flex: 1; min-width: 200px;
}
.tps-btn {
  border: none; padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer;
  font-size: 0.82rem; font-weight: 600; color: white;
}
.tps-run { background: linear-gradient(135deg, #d97706, #f59e0b); }
.tps-run:hover:not(:disabled) { background: linear-gradient(135deg, #b45309, #d97706); }
.tps-run:disabled { background: #4b5563; cursor: not-allowed; }
.tps-pdf { background: linear-gradient(135deg, #0e7490, #06b6d4); }
.tps-pdf:hover:not(:disabled) { background: linear-gradient(135deg, #155e75, #0891b2); }
.tps-pdf:disabled { background: #4b5563; cursor: not-allowed; }

.tps-job {
  margin-top: 0.5rem;
}
.tps-bar {
  height: 6px; background: rgba(0,0,0,0.3); border-radius: 3px; overflow: hidden;
}
.tps-fill {
  height: 100%; background: linear-gradient(90deg, #f59e0b, #fbbf24);
  transition: width 0.3s;
}
.tps-status { margin-top: 0.3rem; font-size: 0.82rem; color: #cbd5e1; }
.tps-done { color: #86efac; }
.tps-err { color: #fca5a5; margin-top: 0.3rem; font-size: 0.82rem; }
</style>
