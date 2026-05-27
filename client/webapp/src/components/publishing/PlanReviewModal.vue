<script setup>
/**
 * PlanReviewModal — show onboarding plan + button "Bắt đầu OCR with config".
 *
 * Props:
 *   book — { book_id, title_vi, page_count }
 *
 * Emits:
 *   close()
 *   ocr-submitted(job)
 *
 * Flow:
 *   1. On mount, GET /books/{id}/plan
 *   2. Show profile, OCR config (anh-editable workers + formula_enable),
 *      TOC, reading plan + translation plan markdown
 *   3. Anh duyệt + click "Bắt đầu OCR" → POST /jobs/ocr with config
 */
import { ref, computed, onMounted } from "vue";

const props = defineProps({
  book: { type: Object, required: true },
});
const emit = defineEmits(["close", "ocr-submitted"]);

const loading = ref(true);
const error = ref("");
const plan = ref(null);

// Anh-editable OCR config (initialized from approved values)
const ocrForm = ref({
  workers: 3,
  formula_enable: true,
  start_page: 1,
  end_page: 1,
});

const submitting = ref(false);

async function loadPlan() {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch(`/api/yi-publishing/books/${props.book.book_id}/plan`);
    if (!r.ok) {
      const d = await r.json();
      error.value = d.detail || "Plan chưa có";
      return;
    }
    const d = await r.json();
    plan.value = d;

    // Pre-fill OCR form from approved config
    if (d.ocr_config) {
      ocrForm.value.workers = d.ocr_config.workers || 3;
      ocrForm.value.formula_enable = d.ocr_config.formula_enable !== false;
    }
    ocrForm.value.start_page = 1;
    ocrForm.value.end_page = d.plan_summary?.ocr_config?.workers
      ? props.book.page_count || 1
      : (props.book.page_count || 1);
    // Try to read page_count from profile or summary
    const pageCount = props.book.page_count || d.profile?.page_count || 1;
    ocrForm.value.end_page = pageCount;
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    loading.value = false;
  }
}

const profileSummary = computed(() => {
  if (!plan.value?.profile) return null;
  const p = plan.value.profile;
  return {
    columns: p.columns,
    density: p.density,
    script: p.script,
    pageCount: props.book.page_count || "?",
  };
});

const planSummary = computed(() => plan.value?.plan_summary || null);

const ocrEtaText = computed(() => {
  const pages = Math.max(0, ocrForm.value.end_page - ocrForm.value.start_page + 1);
  const w = Math.max(1, ocrForm.value.workers);
  const speedup = w === 1 ? 1.0 : w * 0.85;
  let perPageMin = 1.5;
  if (!ocrForm.value.formula_enable) perPageMin *= 0.9;
  const minutes = Math.round((pages * perPageMin) / speedup);
  if (minutes < 60) return `~${minutes} phút`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `~${h}h${m}p` : `~${h}h`;
});

async function submitOcr() {
  submitting.value = true;
  error.value = "";
  try {
    const r = await fetch(
      `/api/yi-publishing/books/${props.book.book_id}/jobs/ocr`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_page: ocrForm.value.start_page,
          end_page: ocrForm.value.end_page,
          backend: "pipeline",
          language: plan.value?.ocr_config?.language || "ch",
          workers: ocrForm.value.workers,
          formula_enable: ocrForm.value.formula_enable,
        }),
      }
    );
    const d = await r.json();
    if (!r.ok) {
      error.value = d.detail || "Submit thất bại";
      return;
    }
    emit("ocr-submitted", d.job);
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    submitting.value = false;
  }
}

function close() {
  if (submitting.value) return;
  emit("close");
}

onMounted(loadPlan);
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true">
      <header class="modal-header">
        <h2>📋 Kế hoạch dịch: <span class="book-title">{{ book.title_vi }}</span></h2>
        <button type="button" class="close-btn" @click="close">×</button>
      </header>

      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="spinner">⏳</div>
          <p>Đang tải kế hoạch...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p>⚠ {{ error }}</p>
          <p class="hint">
            Có thể sách chưa được "Lập kế hoạch" — về Library, mở menu ⋯ chọn
            "📋 Lập kế hoạch dịch" để bắt đầu pipeline (3-5 phút).
          </p>
        </div>

        <template v-else-if="plan">
          <!-- Profile section -->
          <section class="plan-section">
            <h3>🔍 Profile sách (auto-detected)</h3>
            <div class="profile-grid">
              <div class="profile-item">
                <span class="label">Số cột</span>
                <span class="value">{{ profileSummary.columns }}</span>
              </div>
              <div class="profile-item">
                <span class="label">Mật độ chữ</span>
                <span class="value">{{ profileSummary.density }}</span>
              </div>
              <div class="profile-item">
                <span class="label">Văn tự</span>
                <span class="value">{{ profileSummary.script }}</span>
              </div>
              <div class="profile-item">
                <span class="label">Tổng số trang</span>
                <span class="value">{{ profileSummary.pageCount }}</span>
              </div>
            </div>
            <div v-if="plan.ocr_config?.rationale" class="rationale">
              💡 {{ plan.ocr_config.rationale }}
            </div>
          </section>

          <!-- TOC section -->
          <section v-if="plan.toc_markdown" class="plan-section">
            <h3>📖 Mục lục</h3>
            <pre class="md-preview">{{ plan.toc_markdown }}</pre>
          </section>

          <!-- OCR config (anh-editable) -->
          <section class="plan-section">
            <h3>⚙️ Cấu hình OCR (Anh điều chỉnh trước khi chạy)</h3>

            <div class="form-row form-row-2">
              <label>
                Trang bắt đầu
                <input v-model.number="ocrForm.start_page" type="number" min="1" />
              </label>
              <label>
                Trang kết thúc
                <input v-model.number="ocrForm.end_page" type="number" min="1"
                       :max="profileSummary.pageCount" />
              </label>
            </div>

            <div class="form-row">
              <label>
                🐝 Workers song song (1-4)
                <div class="workers-pills">
                  <button v-for="n in 4" :key="n"
                    type="button"
                    :class="['worker-pill', { active: ocrForm.workers === n }]"
                    @click="ocrForm.workers = n">
                    {{ n }}{{ n === 1 ? '' : 'x' }}
                  </button>
                </div>
              </label>
            </div>

            <div class="form-row formula-toggle">
              <label class="check-row">
                <input v-model="ocrForm.formula_enable" type="checkbox" />
                <span>
                  📐 Bật nhận diện công thức toán
                  <span class="hint-inline">
                    (Hán cổ multi-col → nên TẮT để tránh nhận nhầm chữ thành LaTeX)
                  </span>
                </span>
              </label>
            </div>

            <div class="eta-box">
              ⏱ Ước tính: <strong>{{ ocrEtaText }}</strong>
              · Chạy nền, anh có thể đóng tab
            </div>
          </section>

          <!-- Translation plan preview -->
          <section v-if="plan.translation_plan_markdown" class="plan-section">
            <h3>✍️ Kế hoạch dịch ({{ planSummary?.chunks_count || "?" }} chunks)</h3>
            <pre class="md-preview md-collapsed">{{ plan.translation_plan_markdown }}</pre>
          </section>

          <p v-if="error" class="error-msg">⚠ {{ error }}</p>
        </template>
      </div>

      <footer class="modal-footer">
        <button type="button" class="btn-secondary" @click="close" :disabled="submitting">
          Đóng
        </button>
        <button v-if="plan"
                type="button"
                class="btn-primary"
                @click="submitOcr"
                :disabled="submitting">
          {{ submitting ? "Đang submit..." : "🚀 Bắt đầu OCR (với config này)" }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(15, 8, 25, 0.75);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 1rem; backdrop-filter: blur(4px);
}

.modal {
  background: #1f1530;
  border: 1px solid rgba(168, 124, 255, 0.3);
  border-radius: 12px;
  max-width: 720px; width: 100%;
  max-height: 90vh;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex; align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(168, 124, 255, 0.18);
}

.modal-header h2 {
  margin: 0; flex: 1;
  font-size: 1.05rem; color: #f0e6ff;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.book-title {
  color: #d8c7ff; font-weight: normal;
}

.close-btn {
  background: transparent; border: none;
  color: rgba(220, 200, 240, 0.5); font-size: 1.8rem;
  cursor: pointer; width: 30px; line-height: 1; padding: 0;
}

.close-btn:hover { color: white; }

.modal-body {
  padding: 1.2rem 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.loading-state, .error-state {
  text-align: center;
  padding: 2.5rem 1rem;
  color: rgba(220, 200, 240, 0.85);
}

.spinner { font-size: 2.5rem; animation: spin 1.4s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.error-state .hint {
  font-size: 0.82rem;
  color: rgba(220, 200, 240, 0.55);
  margin-top: 1rem;
}

.plan-section {
  margin-bottom: 1.4rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed rgba(168, 124, 255, 0.18);
}

.plan-section h3 {
  margin: 0 0 0.6rem;
  font-size: 0.95rem;
  color: #ffd88a;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem 1rem;
}

.profile-item {
  display: flex; justify-content: space-between;
  padding: 0.4rem 0.8rem;
  background: rgba(168, 124, 255, 0.06);
  border-radius: 6px;
  font-size: 0.88rem;
}

.profile-item .label { color: rgba(220, 200, 240, 0.7); }
.profile-item .value { color: #e8d8ff; font-weight: 600; }

.rationale {
  margin-top: 0.7rem;
  padding: 0.6rem 0.9rem;
  background: rgba(255, 180, 60, 0.1);
  border-left: 3px solid rgba(255, 180, 60, 0.45);
  border-radius: 4px;
  font-size: 0.82rem;
  color: #ffd88a;
  line-height: 1.45;
}

.md-preview {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(168, 124, 255, 0.15);
  border-radius: 6px;
  padding: 0.8rem;
  font-size: 0.78rem;
  font-family: "JetBrains Mono", "Source Code Pro", monospace;
  color: rgba(220, 200, 240, 0.85);
  max-height: 240px;
  overflow-y: auto;
  white-space: pre-wrap;
  margin: 0;
}

.md-collapsed { max-height: 180px; }

.form-row { margin-bottom: 0.85rem; }
.form-row-2 {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;
}

.form-row label {
  display: flex; flex-direction: column;
  font-size: 0.82rem; color: #d8c7ff;
  font-weight: 500; gap: 0.3rem;
}

.form-row input[type="number"] {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 124, 255, 0.2);
  border-radius: 6px;
  color: white;
  padding: 0.5rem 0.7rem;
  font-size: 0.9rem;
}

.check-row {
  flex-direction: row !important;
  align-items: center;
  gap: 0.5rem !important;
  cursor: pointer;
}

.check-row input[type="checkbox"] {
  width: 16px; height: 16px;
  accent-color: #a87cff;
}

.hint-inline {
  display: block;
  font-size: 0.76rem;
  color: rgba(220, 200, 240, 0.55);
  margin-top: 0.2rem;
  font-weight: normal;
}

.workers-pills {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.2rem;
}

.worker-pill {
  flex: 1;
  padding: 0.45rem 0;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(168, 124, 255, 0.2);
  color: #d8c7ff;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.worker-pill.active {
  background: linear-gradient(135deg, #ffb74d, #ff9800);
  color: #2a1a05;
  border-color: transparent;
}

.eta-box {
  margin-top: 0.6rem;
  padding: 0.6rem 0.9rem;
  background: rgba(168, 124, 255, 0.12);
  border-radius: 6px;
  color: #e0d3ff;
  font-size: 0.88rem;
}

.error-msg {
  color: #ff9aa0;
  background: rgba(255, 100, 100, 0.1);
  border-radius: 6px;
  padding: 0.6rem 0.9rem;
  margin-top: 1rem;
  font-size: 0.88rem;
}

.modal-footer {
  display: flex; gap: 0.6rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(168, 124, 255, 0.18);
  background: rgba(0, 0, 0, 0.18);
  justify-content: flex-end;
}

.btn-primary {
  padding: 0.55rem 1.2rem;
  background: linear-gradient(135deg, #a87cff, #7d52d8);
  color: white; border: none;
  border-radius: 8px; font-weight: 600; font-size: 0.88rem;
  cursor: pointer;
}

.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  padding: 0.55rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  color: #d8c7ff;
  border: 1px solid rgba(168, 124, 255, 0.25);
  border-radius: 8px; font-size: 0.86rem;
  cursor: pointer;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
}
</style>
