<script setup>
/**
 * EditMetadataModal — sửa metadata của 1 sách hiện có.
 *
 * Props:
 *   book — current book object
 *
 * Emits:
 *   close()
 *   updated(book)
 */
import { ref } from "vue";

const props = defineProps({
  book: { type: Object, required: true },
});
const emit = defineEmits(["close", "updated"]);

const form = ref({
  title_vi: props.book.title_vi || "",
  hanzi_title: props.book.hanzi_title || "",
  author: props.book.author || "",
  year: props.book.year || null,
  language: props.book.language || "zh",
  school: props.book.school || "",
  notes: props.book.notes || "",
});

const saving = ref(false);
const error = ref("");

async function save() {
  saving.value = true;
  error.value = "";
  try {
    const payload = { ...form.value };
    const r = await fetch(`/api/yi-publishing/books/${props.book.book_id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await r.json();
    if (!r.ok) {
      error.value = d.detail || "Lưu thất bại";
      return;
    }
    emit("updated", d.book);
  } catch (e) {
    error.value = `Lỗi mạng: ${e.message}`;
  } finally {
    saving.value = false;
  }
}

function close() {
  if (saving.value) return;
  emit("close");
}
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true">
      <header class="modal-header">
        <h2>✏️ Sửa metadata: <span class="book-id">{{ book.book_id }}</span></h2>
        <button type="button" class="close-btn" @click="close">×</button>
      </header>

      <div class="modal-body">
        <div class="form-row">
          <label>
            Tựa Việt
            <input v-model="form.title_vi" type="text" />
          </label>
        </div>

        <div class="form-row">
          <label>
            Tựa gốc
            <input v-model="form.hanzi_title" type="text" />
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
            Ngôn ngữ
            <select v-model="form.language">
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
            <textarea v-model="form.notes" rows="3"></textarea>
          </label>
        </div>

        <p v-if="error" class="error-msg">⚠ {{ error }}</p>
      </div>

      <footer class="modal-footer">
        <button type="button" class="btn-secondary" @click="close" :disabled="saving">Huỷ</button>
        <button type="button" class="btn-primary" @click="save" :disabled="saving">
          {{ saving ? "Đang lưu..." : "💾 Lưu" }}
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
  max-width: 580px; width: 100%;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}
.modal-header {
  display: flex; align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(168, 124, 255, 0.18);
}
.modal-header h2 { margin: 0; flex: 1; font-size: 1.1rem; color: #f0e6ff; }
.book-id {
  font-family: monospace; font-size: 0.85rem;
  color: rgba(220, 200, 240, 0.7);
}
.close-btn {
  background: transparent; border: none;
  color: rgba(220, 200, 240, 0.5); font-size: 1.8rem;
  cursor: pointer; width: 30px; line-height: 1; padding: 0;
}
.modal-body { padding: 1.2rem 1.5rem; }
.form-row { margin-bottom: 0.85rem; }
.form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-row label {
  display: flex; flex-direction: column;
  font-size: 0.82rem; color: #d8c7ff;
  font-weight: 500; gap: 0.3rem;
}
.form-row input, .form-row select, .form-row textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 124, 255, 0.2);
  border-radius: 6px; color: white;
  padding: 0.5rem 0.7rem; font-size: 0.9rem;
  font-family: inherit;
}
.error-msg {
  color: #ff9aa0; background: rgba(255, 100, 100, 0.1);
  border-radius: 6px; padding: 0.6rem 0.9rem;
  margin-top: 1rem; font-size: 0.88rem;
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
