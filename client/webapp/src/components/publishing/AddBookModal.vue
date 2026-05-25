<script setup>
/**
 * AddBookModal — 3-step wizard cho upload PDF mới.
 *
 * Step 1 — Upload PDF (drag-drop hoặc click file picker)
 * Step 2 — Metadata form (auto-fill từ PDF metadata)
 * Step 3 — Confirm với preview cover
 *
 * Emits:
 *   close()
 *   added(book) — when successfully finalized
 */
import { ref, computed } from "vue";

const emit = defineEmits(["close", "added"]);

const step = ref(1);
const uploading = ref(false);
const finalizing = ref(false);
const error = ref("");
const dragActive = ref(false);

const tempId = ref(null);
const coverUrl = ref("");
const suggested = ref(null);

// Step 2 form
const form = ref({
  book_id: "",
  title_vi: "",
  hanzi_title: "",
  author: "",
  year: null,
  language: "zh",
  school: "",
  notes: "",
});

const canGoStep3 = computed(() => {
  return form.value.book_id && form.value.title_vi && form.value.language;
});

const fileInputRef = ref(null);

function pickFile() {
  fileInputRef.value?.click();
}

async function handleFile(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    error.value = "Chỉ chấp nhận file PDF";
    return;
  }
  if (file.size > 200 * 1024 * 1024) {
    error.value = "File > 200 MB";
    return;
  }
  uploading.value = true;
  error.value = "";
  try {
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch("/api/yi-publishing/books/upload", {
      method: "POST",
      body: fd,
    });
    const d = await r.json();
    if (!r.ok) {
      error.value = d.detail || "Upload thất bại";
      return;
    }
    tempId.value = d.temp_id;
    coverUrl.value = d.cover_url;
    suggested.value = d.suggested_metadata;
    // Pre-fill form
    form.value = {
      book_id: d.suggested_metadata.book_id || "",
      title_vi: d.suggested_metadata.title_vi || "",
      hanzi_title: d.suggested_metadata.hanzi_title || "",
      author: d.suggested_metadata.author || "",
      year: d.suggested_metadata.year || null,
      language: d.suggested_metadata.language || "zh",
      school: "",
      notes: "",
    };
    step.value = 2;
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    uploading.value = false;
  }
}

function onFileChange(e) {
  const file = e.target.files?.[0];
  e.target.value = "";
  handleFile(file);
}

function onDrop(e) {
  e.preventDefault();
  dragActive.value = false;
  const file = e.dataTransfer.files?.[0];
  handleFile(file);
}

function onDragOver(e) {
  e.preventDefault();
  dragActive.value = true;
}

function onDragLeave() {
  dragActive.value = false;
}

async function finalize() {
  finalizing.value = true;
  error.value = "";
  try {
    const payload = { temp_id: tempId.value, ...form.value };
    const r = await fetch("/api/yi-publishing/books/finalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await r.json();
    if (!r.ok) {
      error.value = d.detail || "Finalize thất bại";
      return;
    }
    emit("added", d.book);
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    finalizing.value = false;
  }
}

function close() {
  if (uploading.value || finalizing.value) return;
  emit("close");
}

function back() {
  if (step.value > 1) step.value -= 1;
}
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true">
      <header class="modal-header">
        <h2>➕ Thêm sách dịch mới</h2>
        <div class="step-indicator">
          <span :class="{ active: step >= 1, done: step > 1 }">1</span>
          <span class="step-line" :class="{ done: step > 1 }"></span>
          <span :class="{ active: step >= 2, done: step > 2 }">2</span>
          <span class="step-line" :class="{ done: step > 2 }"></span>
          <span :class="{ active: step >= 3 }">3</span>
        </div>
        <button type="button" class="close-btn" @click="close">×</button>
      </header>

      <div class="modal-body">
        <!-- ─── Step 1: Upload ─── -->
        <div v-if="step === 1">
          <h3>Bước 1: Tải lên file PDF</h3>
          <p class="step-help">Drag-and-drop hoặc click để chọn file (.pdf, max 200 MB)</p>

          <div
            class="dropzone"
            :class="{ active: dragActive, uploading: uploading }"
            @click="pickFile"
            @drop="onDrop"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept="application/pdf,.pdf"
              style="display: none"
              @change="onFileChange"
            />
            <div v-if="uploading">
              <div class="spinner">⏳</div>
              <p>Đang tải lên + extract metadata...</p>
            </div>
            <div v-else>
              <div class="dropzone-icon">📄</div>
              <p>Kéo file PDF vào đây, hoặc <strong>click để chọn</strong></p>
              <p class="hint">Hỗ trợ PDF Trung văn / Hán Nôm / Việt</p>
            </div>
          </div>
        </div>

        <!-- ─── Step 2: Metadata ─── -->
        <div v-if="step === 2">
          <h3>Bước 2: Metadata sách</h3>
          <p class="step-help">Sửa lại nếu cần. Đã auto-fill từ PDF metadata.</p>

          <div class="form-row preview-row">
            <div class="cover-preview">
              <img v-if="coverUrl" :src="coverUrl" alt="Cover preview" />
            </div>
            <div class="meta-summary">
              <p><strong>Trang:</strong> {{ suggested?.page_count || "?" }}</p>
              <p v-if="suggested?.author"><strong>Tác giả PDF:</strong> {{ suggested.author }}</p>
              <p v-if="suggested?.year"><strong>Năm PDF:</strong> {{ suggested.year }}</p>
            </div>
          </div>

          <div class="form-row">
            <label>
              ID sách (slug, dùng làm folder name) *
              <input
                v-model="form.book_id"
                type="text"
                placeholder="vd: tu-vi-q1"
                pattern="[a-z0-9-]+"
                required
              />
            </label>
          </div>

          <div class="form-row">
            <label>
              Tựa Việt *
              <input v-model="form.title_vi" type="text" required />
            </label>
          </div>

          <div class="form-row">
            <label>
              Tựa gốc (Trung/Hán Nôm)
              <input v-model="form.hanzi_title" type="text" placeholder="vd: 紫微斗数全书·卷一" />
            </label>
          </div>

          <div class="form-row form-row-2">
            <label>
              Tác giả
              <input v-model="form.author" type="text" />
            </label>
            <label>
              Năm
              <input v-model.number="form.year" type="number" min="0" max="3000" />
            </label>
          </div>

          <div class="form-row form-row-2">
            <label>
              Ngôn ngữ *
              <select v-model="form.language" required>
                <option value="zh">中文 (Trung)</option>
                <option value="han-nom">Hán Nôm</option>
                <option value="vi">Tiếng Việt</option>
              </select>
            </label>
            <label>
              Trường phái
              <select v-model="form.school">
                <option value="">— Không xác định —</option>
                <option value="mai-hoa">Mai Hoa Dịch Số</option>
                <option value="tu-vi">Tử Vi Đẩu Số</option>
                <option value="luc-hao">Lục Hào</option>
                <option value="lien-hoa">Liên Hoa</option>
                <option value="other">Khác</option>
              </select>
            </label>
          </div>

          <div class="form-row">
            <label>
              Ghi chú
              <textarea v-model="form.notes" rows="2" placeholder="Source, edition, lý do thêm..."></textarea>
            </label>
          </div>
        </div>

        <!-- ─── Step 3: Confirm ─── -->
        <div v-if="step === 3">
          <h3>Bước 3: Xác nhận</h3>
          <p class="step-help">Kiểm tra lần cuối trước khi thêm vào thư viện.</p>

          <div class="confirm-grid">
            <div class="cover-preview-large">
              <img v-if="coverUrl" :src="coverUrl" alt="Cover preview" />
            </div>
            <dl class="confirm-meta">
              <dt>ID sách</dt><dd><code>{{ form.book_id }}</code></dd>
              <dt>Tựa Việt</dt><dd>{{ form.title_vi }}</dd>
              <dt>Tựa gốc</dt><dd>{{ form.hanzi_title || "—" }}</dd>
              <dt>Tác giả</dt><dd>{{ form.author || "—" }}</dd>
              <dt>Năm</dt><dd>{{ form.year || "—" }}</dd>
              <dt>Ngôn ngữ</dt><dd>{{ form.language }}</dd>
              <dt>Trường phái</dt><dd>{{ form.school || "—" }}</dd>
              <dt>Trang</dt><dd>{{ suggested?.page_count }}</dd>
            </dl>
          </div>
        </div>

        <p v-if="error" class="error-msg">⚠ {{ error }}</p>
      </div>

      <footer class="modal-footer">
        <button v-if="step > 1" type="button" class="btn-secondary" @click="back" :disabled="finalizing">
          ← Quay lại
        </button>
        <div class="footer-spacer"></div>
        <button type="button" class="btn-secondary" @click="close" :disabled="uploading || finalizing">
          Huỷ
        </button>
        <button
          v-if="step === 2"
          type="button"
          class="btn-primary"
          :disabled="!canGoStep3"
          @click="step = 3"
        >
          Tiếp tục →
        </button>
        <button
          v-if="step === 3"
          type="button"
          class="btn-primary"
          :disabled="finalizing"
          @click="finalize"
        >
          {{ finalizing ? "Đang lưu..." : "✓ Thêm vào thư viện" }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 8, 25, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.modal {
  background: #1f1530;
  border: 1px solid rgba(168, 124, 255, 0.3);
  border-radius: 12px;
  max-width: 720px;
  width: 100%;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(168, 124, 255, 0.18);
  gap: 1rem;
}

.modal-header h2 {
  margin: 0;
  flex: 1;
  font-size: 1.15rem;
  color: #f0e6ff;
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.step-indicator span:not(.step-line) {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(220, 200, 240, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(168, 124, 255, 0.25);
}

.step-indicator .active {
  background: linear-gradient(135deg, #a87cff, #7d52d8);
  color: white;
  border-color: transparent;
}

.step-indicator .done {
  background: rgba(80, 200, 130, 0.3);
  color: #9cf0bf;
  border-color: rgba(80, 200, 130, 0.5);
}

.step-line {
  width: 24px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1px;
}

.step-line.done {
  background: rgba(80, 200, 130, 0.6);
}

.close-btn {
  background: transparent;
  border: none;
  color: rgba(220, 200, 240, 0.5);
  font-size: 1.8rem;
  cursor: pointer;
  width: 30px;
  line-height: 1;
  padding: 0;
}

.close-btn:hover {
  color: white;
}

.modal-body {
  padding: 1.2rem 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-body h3 {
  margin: 0 0 0.4rem;
  color: #e0d3ff;
  font-size: 1rem;
}

.step-help {
  color: rgba(220, 200, 240, 0.7);
  font-size: 0.85rem;
  margin: 0 0 1rem;
}

/* Dropzone */
.dropzone {
  border: 2px dashed rgba(168, 124, 255, 0.4);
  border-radius: 12px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  background: rgba(168, 124, 255, 0.04);
  transition: all 0.15s ease;
}

.dropzone:hover, .dropzone.active {
  border-color: rgba(168, 124, 255, 0.8);
  background: rgba(168, 124, 255, 0.12);
}

.dropzone.uploading {
  cursor: progress;
  opacity: 0.7;
}

.dropzone-icon {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}

.dropzone .hint {
  font-size: 0.78rem;
  color: rgba(220, 200, 240, 0.5);
  margin-top: 0.4rem;
}

.spinner {
  font-size: 2.5rem;
  animation: spin 1.4s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Form */
.form-row {
  margin-bottom: 0.85rem;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-row label {
  display: flex;
  flex-direction: column;
  font-size: 0.82rem;
  color: #d8c7ff;
  font-weight: 500;
  gap: 0.3rem;
}

.form-row input, .form-row select, .form-row textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 124, 255, 0.2);
  border-radius: 6px;
  color: white;
  padding: 0.5rem 0.7rem;
  font-size: 0.9rem;
  font-family: inherit;
}

.form-row input:focus, .form-row select:focus, .form-row textarea:focus {
  outline: none;
  border-color: rgba(168, 124, 255, 0.7);
}

.preview-row {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 1rem;
  background: rgba(168, 124, 255, 0.06);
  padding: 0.7rem;
  border-radius: 8px;
}

.cover-preview img {
  width: 90px;
  aspect-ratio: 3/4;
  object-fit: cover;
  border-radius: 4px;
}

.meta-summary p {
  margin: 0.1rem 0;
  font-size: 0.83rem;
  color: rgba(220, 200, 240, 0.85);
}

/* Confirm */
.confirm-grid {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 1.5rem;
}

.cover-preview-large img {
  width: 180px;
  aspect-ratio: 3/4;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid rgba(168, 124, 255, 0.3);
}

.confirm-meta {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.3rem 1rem;
  font-size: 0.88rem;
}

.confirm-meta dt {
  color: rgba(220, 200, 240, 0.6);
  font-weight: 500;
}

.confirm-meta dd {
  margin: 0;
  color: #f0e6ff;
}

.confirm-meta code {
  background: rgba(168, 124, 255, 0.18);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85rem;
}

.error-msg {
  color: #ff9aa0;
  background: rgba(255, 100, 100, 0.1);
  border-radius: 6px;
  padding: 0.6rem 0.9rem;
  margin-top: 1rem;
  font-size: 0.88rem;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(168, 124, 255, 0.18);
  background: rgba(0, 0, 0, 0.18);
}

.footer-spacer { flex: 1; }

.btn-primary {
  padding: 0.55rem 1.2rem;
  background: linear-gradient(135deg, #a87cff, #7d52d8);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(168, 124, 255, 0.4);
}

.btn-secondary {
  padding: 0.55rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  color: #d8c7ff;
  border: 1px solid rgba(168, 124, 255, 0.25);
  border-radius: 8px;
  font-size: 0.86rem;
  cursor: pointer;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
