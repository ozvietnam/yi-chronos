<script setup>
import { ref } from "vue";
import {
  analyzeBook,
  TIER_LABEL,
  TIER_DESCRIPTION,
  SCHOOL_LABEL
} from "../../composables/useLexicon.js";

const emit = defineEmits(["close", "complete"]);

const step = ref(1);        // 1=path, 2=analyzing, 3=review, 4=done
const filePath = ref("");
const ocrPages = ref(6);
const skipLlm = ref(false);
const error = ref("");
const proposal = ref(null);
const corpus = ref(null);

async function analyze() {
  if (!filePath.value.trim()) {
    error.value = "Cần đường dẫn PDF.";
    return;
  }
  error.value = "";
  step.value = 2;
  try {
    const r = await analyzeBook(filePath.value.trim(), {
      ocrPages: ocrPages.value,
      skipLlm: skipLlm.value,
      register: true
    });
    proposal.value = r.proposal;
    corpus.value = r.corpus || null;
    step.value = 3;
  } catch (e) {
    error.value = String(e.message || e);
    step.value = 1;
  }
}

function finish() {
  emit("complete", corpus.value);
}
</script>

<template>
  <div class="wizard-overlay" @click.self="emit('close')">
    <div class="wizard-modal">
      <header>
        <h3>🤖 Thủ thư — Phân loại sách mới</h3>
        <button class="close-btn" @click="emit('close')">✕</button>
      </header>

      <!-- Step 1: input path -->
      <div v-if="step === 1" class="step">
        <p class="hint">
          Nhập đường dẫn PDF (tuyệt đối, hoặc tên file nếu đã có trong <code>thư viện sách/</code>).
          Thủ thư sẽ OCR 5-6 trang đầu và đề xuất tier + trường phái.
        </p>
        <label>
          Đường dẫn PDF:
          <input v-model="filePath" type="text" placeholder="VD: Kinh Dich Tron Bo - Ngo Tat To.pdf" />
        </label>
        <label>
          Số trang OCR (đầu sách):
          <input v-model.number="ocrPages" type="number" min="2" max="20" />
        </label>
        <label class="cb">
          <input v-model="skipLlm" type="checkbox" />
          Bỏ qua LLM (chỉ đọc filename + manifest, nhanh nhưng không phân loại sâu)
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <div class="step-actions">
          <button class="btn-primary" @click="analyze">🔍 Phân tích</button>
          <button class="btn-ghost" @click="emit('close')">Huỷ</button>
        </div>
      </div>

      <!-- Step 2: analyzing -->
      <div v-else-if="step === 2" class="step centered">
        <div class="spinner"></div>
        <p>Đang OCR + gọi LLM phân loại…</p>
        <small>Quá trình này có thể mất 30s — 2 phút.</small>
      </div>

      <!-- Step 3: review proposal -->
      <div v-else-if="step === 3" class="step">
        <h4>📋 Đề xuất phân loại</h4>
        <div v-if="proposal?.errors?.length" class="error-block">
          <strong>⚠️ Lỗi:</strong>
          <ul><li v-for="e in proposal.errors" :key="e">{{ e }}</li></ul>
        </div>
        <div v-if="proposal" class="prop-grid">
          <div><strong>Tên:</strong> {{ proposal.title }}</div>
          <div><strong>Tác giả:</strong> {{ proposal.author || "—" }}</div>
          <div>
            <strong>Tier:</strong>
            <span class="tier-badge" :style="{ background: TIER_LABEL[proposal.tier].color }">
              {{ proposal.tier }}
            </span>
            — {{ TIER_DESCRIPTION[proposal.tier] }}
          </div>
          <div><em>{{ proposal.tier_reason }}</em></div>
          <div>
            <strong>Trường phái:</strong>
            <span v-for="s in proposal.schools" :key="s" class="chip">
              {{ SCHOOL_LABEL[s] || s }}
            </span>
          </div>
          <div><em>{{ proposal.school_reason }}</em></div>
          <div><strong>Tóm tắt:</strong> {{ proposal.summary }}</div>
          <div v-if="proposal.quality_signals?.length">
            <strong>Tín hiệu chất lượng:</strong>
            <ul>
              <li v-for="s in proposal.quality_signals" :key="s">{{ s }}</li>
            </ul>
          </div>
          <div><strong>Tổng số trang:</strong> {{ proposal.pages_total }}</div>
          <div><strong>Confidence:</strong> {{ (proposal.confidence * 100).toFixed(0) }}%</div>
          <div v-if="proposal.source_tier_from_manifest" class="manifest-tag">
            ℹ️ Tier đã có trong manifest (anh duyệt trước đây).
          </div>
        </div>

        <p v-if="corpus" class="success">
          ✓ Đã lưu vào thư viện với corpus_id = {{ corpus.corpus_id }}, status = <strong>queued</strong>.
        </p>

        <div class="step-actions">
          <button class="btn-primary" @click="finish">✓ Xong — về thư viện</button>
          <button class="btn-ghost" @click="step = 1">⟲ Phân tích lại sách khác</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wizard-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.wizard-modal {
  background: #1e293b;
  border-radius: 8px;
  width: 90%;
  max-width: 580px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 1.25rem;
  color: #cbd5e1;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
header h3 { margin: 0; color: #e2e8f0; }
.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.2rem;
  cursor: pointer;
}
.step { display: flex; flex-direction: column; gap: 0.5rem; }
.step.centered { align-items: center; text-align: center; padding: 2rem 1rem; }
.hint { color: #94a3b8; font-size: 0.85rem; margin: 0; }
.hint code { background: rgba(0,0,0,0.3); padding: 0.1rem 0.3rem; border-radius: 2px; }

label {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
  color: #94a3b8;
}
label.cb { flex-direction: row; align-items: center; gap: 0.5rem; }
input[type="text"], input[type="number"] {
  padding: 0.4rem 0.6rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
  font-size: 0.9rem;
}
.step-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
.btn-primary {
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  padding: 0.45rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-ghost {
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
  border: none;
  padding: 0.45rem 0.95rem;
  border-radius: 4px;
  cursor: pointer;
}
.error { color: #f87171; font-size: 0.85rem; }
.error-block {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #f87171;
  padding: 0.5rem;
  border-radius: 3px;
  color: #fca5a5;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}
.success {
  color: #86efac;
  background: rgba(34, 197, 94, 0.1);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #475569;
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.prop-grid {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  background: rgba(15, 23, 42, 0.4);
  padding: 0.75rem;
  border-radius: 5px;
  font-size: 0.85rem;
}
.prop-grid strong { color: #cbd5e1; }
.prop-grid em { color: #94a3b8; font-style: italic; font-size: 0.78rem; }
.tier-badge {
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.72rem;
  margin: 0 0.25rem;
}
.chip {
  padding: 0.1rem 0.4rem;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border-radius: 3px;
  font-size: 0.72rem;
  margin: 0 0.15rem;
}
.manifest-tag {
  color: #86efac;
  font-size: 0.78rem;
  padding: 0.3rem 0.5rem;
  background: rgba(34, 197, 94, 0.08);
  border-radius: 3px;
}
ul { margin: 0.2rem 0 0 1.2rem; color: #cbd5e1; }
</style>
