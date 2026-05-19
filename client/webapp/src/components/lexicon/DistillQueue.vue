<script setup>
import { ref, onMounted } from "vue";
import { getDistillQueue, resolveDistillItem } from "../../composables/useLexicon.js";

const items = ref([]);
const loading = ref(false);
const error = ref("");
const filterStatus = ref("auto_accepted");
const processing = ref({});
const reviewNotes = ref({});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await getDistillQueue(filterStatus.value || null, 50);
    items.value = data.items || [];
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function resolve(item, status) {
  processing.value[item.item_id] = true;
  try {
    await resolveDistillItem(item.item_id, {
      status,
      reviewerNote: reviewNotes.value[item.item_id] || ""
    });
    await load();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    processing.value[item.item_id] = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="distill-queue">
    <header>
      <h3>Distill queue ({{ items.length }})</h3>
      <div class="controls">
        <select v-model="filterStatus" @change="load">
          <option value="auto_accepted">Auto-accepted</option>
          <option value="manual_pending">Chờ duyệt</option>
          <option value="approved">Đã duyệt</option>
          <option value="rejected">Bị từ chối</option>
        </select>
        <button @click="load" :disabled="loading">↻</button>
      </div>
    </header>

    <p class="hint">
      LLM tự đề xuất concept/mapping mới trong YOLO mode → đã auto-merge vào lexicon.
      Anh review để mark rõ <em>approved</em> hoặc <em>rejected</em> (nếu sai).
    </p>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else-if="items.length === 0" class="status">Trống.</div>

    <ul v-else class="items">
      <li v-for="item in items" :key="item.item_id" class="item-card">
        <div class="item-head">
          <span class="kind-pill">{{ item.kind }}</span>
          <span class="status-pill" :class="`status-${item.status}`">{{ item.status }}</span>
          <span class="conf">conf {{ item.confidence.toFixed(2) }}</span>
        </div>
        <div class="item-body">
          <pre>{{ JSON.stringify(item.payload, null, 2).slice(0, 600) }}</pre>
        </div>
        <div class="item-meta">
          <span>📂 {{ item.source }}</span>
          <span v-if="item.reviewer_note" class="reviewer-note">📝 {{ item.reviewer_note }}</span>
        </div>
        <div v-if="filterStatus === 'auto_accepted' || filterStatus === 'manual_pending'" class="actions">
          <input v-model="reviewNotes[item.item_id]" type="text" placeholder="Lý do (optional)" />
          <button class="btn-primary" :disabled="processing[item.item_id]" @click="resolve(item, 'approved')">✓ Approve</button>
          <button class="btn-ghost" :disabled="processing[item.item_id]" @click="resolve(item, 'rejected')">✗ Reject</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.distill-queue {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
header h3 { margin: 0; color: #e2e8f0; }
.controls { display: flex; gap: 0.5rem; }
.controls select, .controls button {
  padding: 0.3rem 0.6rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
}
.hint { color: #94a3b8; font-size: 0.85rem; margin: 0 0 1rem; }
.hint em { color: #a78bfa; font-style: normal; }
.status { padding: 2rem; text-align: center; color: #94a3b8; }
.status.error { color: #f87171; }

.items {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.item-card {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
  padding: 0.75rem;
}
.item-head {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.kind-pill {
  padding: 0.1rem 0.5rem;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border-radius: 3px;
  font-size: 0.75rem;
}
.status-pill {
  padding: 0.1rem 0.5rem;
  border-radius: 3px;
  font-size: 0.7rem;
}
.status-pill.status-auto_accepted { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-pill.status-approved { background: rgba(34, 197, 94, 0.2); color: #86efac; }
.status-pill.status-rejected { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
.conf { color: #94a3b8; font-size: 0.75rem; margin-left: auto; }

.item-body pre {
  margin: 0.5rem 0;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 3px;
  font-size: 0.75rem;
  color: #cbd5e1;
  overflow: auto;
  max-height: 200px;
}
.item-meta {
  font-size: 0.7rem;
  color: #64748b;
  display: flex;
  gap: 0.5rem;
}
.reviewer-note { color: #34d399; }

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.actions input {
  flex: 1;
  padding: 0.3rem 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #e2e8f0;
  border-radius: 4px;
}
.actions button {
  padding: 0.3rem 0.7rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}
.actions button:disabled { opacity: 0.4; }
.btn-primary { background: #86efac; color: #064e3b; font-weight: 600; }
.btn-ghost { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }
</style>
