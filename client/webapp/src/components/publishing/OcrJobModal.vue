<script setup>
/**
 * OcrJobModal — config + submit MinerU OCR job cho 1 sách.
 *
 * Props:
 *   book — { book_id, title_vi, page_count }
 *
 * Emits:
 *   close()
 *   submitted(job)
 */
import { ref, computed } from "vue";

const props = defineProps({
  book: { type: Object, required: true },
});
const emit = defineEmits(["close", "submitted"]);

const form = ref({
  start_page: 1,
  end_page: props.book.page_count || 1,
  backend: "pipeline",
  language: "ch",
});

const submitting = ref(false);
const error = ref("");

const pagesCount = computed(() => {
  return Math.max(0, form.value.end_page - form.value.start_page + 1);
});

const estimateMinutes = computed(() => {
  // Rough estimate: 1.5 phút/trang với MinerU pipeline trên M4
  return Math.round(pagesCount.value * 1.5);
});

const estimateText = computed(() => {
  const m = estimateMinutes.value;
  if (m < 60) return `~${m} phút`;
  const h = Math.floor(m / 60);
  const min = m % 60;
  return min > 0 ? `~${h}h ${min}p` : `~${h}h`;
});

async function submit() {
  submitting.value = true;
  error.value = "";
  try {
    const r = await fetch(
      `/api/yi-publishing/books/${props.book.book_id}/jobs/ocr`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form.value),
      }
    );
    const d = await r.json();
    if (!r.ok) {
      error.value = d.detail || "Submit thất bại";
      return;
    }
    emit("submitted", d.job);
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
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true">
      <header class="modal-header">
        <h2>🔍 Đặt scan OCR</h2>
        <button type="button" class="close-btn" @click="close">×</button>
      </header>

      <div class="modal-body">
        <p class="book-name">
          <strong>{{ book.title_vi }}</strong>
          <span v-if="book.page_count" class="page-count">· {{ book.page_count }} trang</span>
        </p>

        <div class="form-row form-row-2">
          <label>
            Trang bắt đầu
            <input v-model.number="form.start_page" type="number" min="1" />
          </label>
          <label>
            Trang kết thúc
            <input v-model.number="form.end_page" type="number" min="1" :max="book.page_count || 9999" />
          </label>
        </div>

        <div class="form-row form-row-2">
          <label>
            Backend
            <select v-model="form.backend">
              <option value="pipeline">pipeline (mặc định, nhanh)</option>
              <option value="vlm">vlm (qwen-vl, sâu hơn)</option>
            </select>
          </label>
          <label>
            Ngôn ngữ
            <select v-model="form.language">
              <option value="ch">中文 (Trung)</option>
              <option value="en">English</option>
            </select>
          </label>
        </div>

        <div class="estimate-box">
          📊 <strong>{{ pagesCount }}</strong> trang · ước tính <strong>{{ estimateText }}</strong>
          (chạy nền, anh có thể đóng tab)
        </div>

        <p class="hint">
          💡 MinerU "bắt khối ảnh": detect bố cục paragraphs / images / tables / captions
          theo paradigm shift #5 (layout-first OCR). Chỉ 1 job OCR chạy tại 1 lần.
        </p>

        <p v-if="error" class="error-msg">⚠ {{ error }}</p>
      </div>

      <footer class="modal-footer">
        <button type="button" class="btn-secondary" @click="close" :disabled="submitting">
          Huỷ
        </button>
        <button type="button" class="btn-primary" @click="submit" :disabled="submitting || pagesCount < 1">
          {{ submitting ? "Đang submit..." : "🚀 Bắt đầu OCR" }}
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
  max-width: 540px; width: 100%;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex; align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(168, 124, 255, 0.18);
}

.modal-header h2 { margin: 0; flex: 1; font-size: 1.1rem; color: #f0e6ff; }

.close-btn {
  background: transparent; border: none;
  color: rgba(220, 200, 240, 0.5); font-size: 1.8rem;
  cursor: pointer; width: 30px; line-height: 1; padding: 0;
}

.close-btn:hover { color: white; }

.modal-body { padding: 1.2rem 1.5rem; }

.book-name {
  font-size: 0.95rem;
  margin: 0 0 1rem;
  color: #e0d3ff;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(168, 124, 255, 0.15);
}

.page-count {
  color: rgba(220, 200, 240, 0.6);
  font-weight: normal;
  margin-left: 0.4rem;
}

.form-row { margin-bottom: 0.85rem; }
.form-row-2 {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;
}

.form-row label {
  display: flex; flex-direction: column;
  font-size: 0.82rem; color: #d8c7ff;
  font-weight: 500; gap: 0.3rem;
}

.form-row input, .form-row select {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 124, 255, 0.2);
  border-radius: 6px;
  color: white;
  padding: 0.5rem 0.7rem;
  font-size: 0.9rem;
}

.estimate-box {
  background: rgba(168, 124, 255, 0.12);
  border: 1px solid rgba(168, 124, 255, 0.3);
  border-radius: 8px;
  padding: 0.7rem 1rem;
  margin: 1rem 0 0.6rem;
  color: #e0d3ff;
  font-size: 0.88rem;
}

.hint {
  font-size: 0.78rem;
  color: rgba(220, 200, 240, 0.6);
  margin: 0;
  line-height: 1.45;
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
