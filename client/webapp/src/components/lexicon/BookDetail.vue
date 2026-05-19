<script setup>
import { ref, watch, computed } from "vue";
import RestorationPlan from "./RestorationPlan.vue";
import {
  TIER_LABEL,
  TIER_DESCRIPTION,
  STATUS_LABEL,
  SCHOOL_LABEL,
  RESTORED_STATUS_LABEL,
  COPYRIGHT_LABEL,
  restoreBook
} from "../../composables/useLexicon.js";

const props = defineProps({
  book: { type: Object, required: true }
});
const emit = defineEmits(["save", "close", "open-reader"]);

const restoring = ref(false);
const restoreMsg = ref("");
const restorePages = ref(5);   // pilot batch size
const restoreSkipLlm = ref(false);
const showPlan = ref(false);

async function triggerRestore() {
  restoring.value = true;
  restoreMsg.value = "Đang phục chế… (có thể mất vài phút)";
  try {
    const r = await restoreBook(props.book.corpus_id, {
      maxPages: restorePages.value,
      skipLlm: restoreSkipLlm.value
    });
    const rs = r.result || {};
    restoreMsg.value = `✓ ${rs.pages_processed} trang phục chế / ${rs.figures_extracted} hình / ${rs.wikilinks_total} wikilinks · ${rs.duration_seconds}s`;
    // Notify parent to refresh book row
    emit("save", props.book.corpus_id, { /* trigger refresh */ });
  } catch (e) {
    restoreMsg.value = "✗ " + String(e.message || e);
  } finally {
    restoring.value = false;
  }
}

const editing = ref(false);
const form = ref({
  tier: props.book.tier || "B",
  status: props.book.status || "queued",
  author: props.book.author || "",
  notes: props.book.notes || "",
  schools_tags: [...(props.book.schools_tags || [])]
});

watch(() => props.book, (b) => {
  editing.value = false;
  form.value = {
    tier: b.tier || "B",
    status: b.status || "queued",
    author: b.author || "",
    notes: b.notes || "",
    schools_tags: [...(b.schools_tags || [])]
  };
});

const tier = computed(() => (props.book.tier || "B").toUpperCase());
const tierMeta = computed(() => TIER_LABEL[tier.value] || TIER_LABEL.B);
const schoolNames = computed(
  () => (props.book.schools_tags || []).map(s => SCHOOL_LABEL[s] || s).join(", ")
);
const displayDonePages = computed(() =>
  (props.book.restored_pages || 0) > 0
    ? props.book.restored_pages || 0
    : props.book.pages_ingested || 0
);
const displayProgress = computed(() => {
  const total = props.book.pages_total || 0;
  return total > 0 ? Math.min(100, (displayDonePages.value / total) * 100) : 0;
});
const progressLabel = computed(() =>
  (props.book.restored_pages || 0) > 0 ? "Đã phục chế" : "Đã đọc"
);

function toggleSchool(key) {
  const i = form.value.schools_tags.indexOf(key);
  if (i === -1) form.value.schools_tags.push(key);
  else form.value.schools_tags.splice(i, 1);
}

function save() {
  emit("save", props.book.corpus_id, { ...form.value });
  editing.value = false;
}
</script>

<template>
  <div class="book-detail">
    <header>
      <div>
        <span class="tier-badge" :style="{ background: tierMeta.color }">{{ tier }}</span>
        <span class="tier-note">{{ TIER_DESCRIPTION[tier] }}</span>
      </div>
      <button class="close-btn" @click="emit('close')">✕</button>
    </header>

    <h3 class="bd-title">{{ book.name }}</h3>
    <div v-if="book.author" class="bd-author">— {{ book.author }}</div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat">
        <div class="sv">{{ book.pages_total || 0 }}</div>
        <div class="sl">Tổng trang</div>
      </div>
      <div class="stat">
        <div class="sv">{{ displayDonePages }}</div>
        <div class="sl">{{ progressLabel }}</div>
      </div>
      <div class="stat">
        <div class="sv">{{ displayProgress.toFixed(1) }}%</div>
        <div class="sl">Tiến độ</div>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="big-bar">
      <div class="fill" :style="{ width: displayProgress + '%' }"></div>
    </div>

    <!-- Meta -->
    <div class="meta">
      <div><strong>Status:</strong>
        <span :style="{ color: (STATUS_LABEL[book.status] || STATUS_LABEL.queued).color }">
          ●&nbsp;{{ (STATUS_LABEL[book.status] || STATUS_LABEL.queued).label }}
        </span>
      </div>
      <div><strong>Trường phái:</strong> {{ schoolNames || "—" }}</div>
      <div><strong>Tier decided by:</strong> {{ book.tier_decided_by || "—" }}</div>
      <div v-if="book.file_path"><strong>File:</strong>
        <code class="filepath">{{ book.file_path }}</code>
      </div>
      <div><strong>Concepts/Mappings extracted:</strong>
        {{ book.concepts_extracted }} / {{ book.mappings_extracted }}
      </div>
    </div>

    <!-- Librarian summary -->
    <div v-if="book.librarian_summary" class="summary">
      <div class="sum-label">🤖 Thủ thư tóm tắt:</div>
      <p>{{ book.librarian_summary }}</p>
    </div>

    <div v-if="book.notes" class="notes">
      <strong>Ghi chú:</strong> {{ book.notes }}
    </div>

    <!-- Restoration plan (em chốt: plan trước, run sau) -->
    <div class="plan-toggle">
      <button class="btn-plan" @click="showPlan = !showPlan">
        📋 {{ showPlan ? "Ẩn kế hoạch" : "Xem/Lập kế hoạch phục chế" }}
      </button>
    </div>
    <div v-if="showPlan" class="plan-container">
      <RestorationPlan
        :corpus-id="book.corpus_id"
        @close="showPlan = false"
      />
    </div>

    <!-- Restoration panel (phục chế) -->
    <div class="restore-panel">
      <div class="rp-head">
        <strong>🔧 Phục chế (Restoration)</strong>
        <span class="rs-pill"
              :style="{ color: RESTORED_STATUS_LABEL[book.restored_status || 'none']?.color }">
          ●&nbsp;{{ RESTORED_STATUS_LABEL[book.restored_status || 'none']?.label }}
          <span v-if="book.restored_pages">
            · {{ book.restored_pages }} trang
          </span>
        </span>
      </div>
      <div class="rp-copyright">
        Bản quyền:
        <span :style="{ color: COPYRIGHT_LABEL[book.copyright_status || 'internal_only']?.color }">
          {{ COPYRIGHT_LABEL[book.copyright_status || 'internal_only']?.icon }}
          {{ COPYRIGHT_LABEL[book.copyright_status || 'internal_only']?.label }}
        </span>
        <span v-if="!book.allow_download" class="dl-locked">— 🚫 Tắt download</span>
      </div>

      <div class="rp-controls">
        <label>Số trang phục chế (test):
          <input v-model.number="restorePages" type="number" min="1" max="50"/>
        </label>
        <label class="cb">
          <input v-model="restoreSkipLlm" type="checkbox"/>
          Bỏ qua LLM (nhanh, chỉ OCR thô)
        </label>
        <button class="btn-primary" :disabled="restoring" @click="triggerRestore">
          {{ restoring ? "Đang phục chế…" : "🔧 Chạy phục chế" }}
        </button>
        <button v-if="(book.restored_pages || 0) > 0"
                class="btn-read"
                @click="emit('open-reader', book)">
          📖 Đọc bản phục chế
        </button>
      </div>
      <p v-if="restoreMsg" class="rp-msg" :class="{ ok: restoreMsg.startsWith('✓') }">
        {{ restoreMsg }}
      </p>
    </div>

    <!-- Edit mode -->
    <div v-if="!editing" class="actions">
      <button class="btn-edit" @click="editing = true">✏️ Sửa</button>
    </div>
    <div v-else class="edit-form">
      <label>
        Tier:
        <select v-model="form.tier">
          <option v-for="t in ['S','A','B','C']" :key="t" :value="t">{{ t }}</option>
        </select>
      </label>
      <label>
        Status:
        <select v-model="form.status">
          <option v-for="(v,k) in STATUS_LABEL" :key="k" :value="k">{{ v.label }}</option>
        </select>
      </label>
      <label>
        Tác giả:
        <input v-model="form.author" type="text" />
      </label>
      <div class="schools-edit">
        <span class="se-label">Trường phái:</span>
        <button
          v-for="(lbl, key) in SCHOOL_LABEL"
          :key="key"
          type="button"
          class="school-toggle"
          :class="{ active: form.schools_tags.includes(key) }"
          @click="toggleSchool(key)"
        >{{ lbl }}</button>
      </div>
      <label>
        Ghi chú:
        <textarea v-model="form.notes" rows="3"></textarea>
      </label>
      <div class="edit-actions">
        <button class="btn-primary" @click="save">💾 Lưu</button>
        <button class="btn-ghost" @click="editing = false">Huỷ</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-detail {
  padding: 1rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.tier-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.75rem;
}
.tier-note { font-size: 0.72rem; color: #94a3b8; margin-left: 0.4rem; }
.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
}
.bd-title { color: #f1f5f9; margin: 0.3rem 0 0.1rem; font-size: 1rem; }
.bd-author { color: #94a3b8; font-style: italic; font-size: 0.8rem; margin-bottom: 0.5rem; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.4rem;
  margin: 0.5rem 0;
}
.stat {
  background: rgba(99, 102, 241, 0.1);
  padding: 0.4rem;
  border-radius: 4px;
  text-align: center;
}
.sv { font-size: 1.1rem; font-weight: 700; color: #c4b5fd; }
.sl { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; }

.big-bar {
  height: 6px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 3px;
  overflow: hidden;
  margin: 0.5rem 0 0.75rem;
}
.big-bar .fill {
  height: 100%;
  background: linear-gradient(to right, #818cf8, #c4b5fd);
  transition: width 0.3s;
}

.meta {
  font-size: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}
.meta strong { color: #94a3b8; font-weight: 500; }
.filepath {
  font-family: monospace;
  font-size: 0.7rem;
  color: #64748b;
  background: rgba(0,0,0,0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
  word-break: break-all;
}

.summary {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(167, 139, 250, 0.08);
  border-left: 3px solid #a78bfa;
  border-radius: 3px;
}
.sum-label {
  font-size: 0.7rem;
  color: #a78bfa;
  margin-bottom: 0.2rem;
}
.summary p { margin: 0; color: #cbd5e1; line-height: 1.4; }

.notes {
  margin-top: 0.5rem;
  padding: 0.4rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 3px;
  font-size: 0.8rem;
}

.plan-toggle {
  margin-top: 0.5rem;
}
.btn-plan {
  width: 100%;
  padding: 0.4rem;
  background: rgba(96, 165, 250, 0.1);
  color: #93c5fd;
  border: 1px solid rgba(96, 165, 250, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.82rem;
}
.btn-plan:hover {
  background: rgba(96, 165, 250, 0.2);
}
.plan-container {
  margin-top: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 5px;
  max-height: 600px;
  overflow-y: auto;
}

.restore-panel {
  margin-top: 0.75rem;
  padding: 0.6rem 0.7rem;
  background: rgba(167, 139, 250, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.15);
  border-radius: 5px;
  font-size: 0.8rem;
}
.rp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}
.rp-head strong { color: #c4b5fd; }
.rs-pill { font-size: 0.72rem; }
.rp-copyright { font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.5rem; }
.dl-locked { color: #fca5a5; margin-left: 0.4rem; }
.rp-controls {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.rp-controls label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: #94a3b8;
}
.rp-controls label.cb { flex-direction: row; }
.rp-controls input[type="number"] {
  width: 60px;
  padding: 0.2rem 0.4rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 3px;
}
.rp-controls .btn-primary {
  margin-top: 0.2rem;
  padding: 0.4rem 0.7rem;
}
.btn-read {
  margin-top: 0.2rem;
  padding: 0.4rem 0.7rem;
  background: #86efac;
  color: #064e3b;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-read:hover { background: #bbf7d0; }
.rp-msg {
  margin: 0.4rem 0 0;
  padding: 0.3rem 0.5rem;
  background: rgba(239, 68, 68, 0.08);
  color: #fca5a5;
  border-radius: 3px;
  font-size: 0.75rem;
}
.rp-msg.ok {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
}

.actions { margin-top: 0.75rem; }
.btn-edit, .btn-primary, .btn-ghost {
  padding: 0.35rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-edit {
  background: rgba(167, 139, 250, 0.15);
  color: #c4b5fd;
}
.btn-edit:hover { background: rgba(167, 139, 250, 0.3); }
.btn-primary { background: #a78bfa; color: #1e1b4b; font-weight: 600; }
.btn-ghost { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }

.edit-form {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 4px;
}
.edit-form label {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.75rem;
  color: #94a3b8;
}
.edit-form select, .edit-form input, .edit-form textarea {
  padding: 0.3rem 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.85rem;
}
.schools-edit {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}
.se-label { font-size: 0.75rem; color: #94a3b8; margin-right: 0.3rem; }
.school-toggle {
  padding: 0.2rem 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid transparent;
  color: #cbd5e1;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.72rem;
}
.school-toggle.active {
  background: rgba(167, 139, 250, 0.25);
  border-color: #a78bfa;
  color: #f1f5f9;
}
.edit-actions { display: flex; gap: 0.4rem; }
</style>
