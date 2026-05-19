<script setup>
/**
 * UserPersonsPanel — CRUD UI for user_persons (DB-backed via /api/auth/my/persons).
 *
 * Hiển thị khi anh login. Mỗi user có namespace riêng (gia đình, đồng nghiệp, bạn bè).
 * Phân biệt với localStorage profiles (legacy, single-user) — đây là multi-user data
 * lưu vĩnh viễn trên server.
 */
import { ref, computed, onMounted } from "vue";
import {
  apiPersons,
  apiActivePersonKey,
  loadMyPersons,
  addMyPerson,
  updateMyPerson,
  deleteMyPerson,
  setActivePerson,
  isSyncing,
  syncError,
} from "../stores/userDataStore.js";
import { isAuthenticated, currentUser } from "../stores/authStore.js";

const RELATIONSHIPS = [
  { value: "self", label: "Bản thân", emoji: "👤" },
  { value: "spouse", label: "Vợ / Chồng", emoji: "💍" },
  { value: "child", label: "Con", emoji: "🧒" },
  { value: "parent", label: "Cha / Mẹ", emoji: "👴" },
  { value: "sibling", label: "Anh / Chị / Em", emoji: "👫" },
  { value: "colleague", label: "Đồng nghiệp", emoji: "💼" },
  { value: "friend", label: "Bạn", emoji: "🤝" },
  { value: "partner", label: "Người yêu", emoji: "💕" },
  { value: "other", label: "Khác", emoji: "👥" },
];

const newDraft = ref({
  person_key: "",
  name: "",
  relationship: "other",
  gender: "nam",
  birth_year: null,
  birth_datetime_local: "",
  timezone: "Asia/Ho_Chi_Minh",
  birth_place: "",
  notes: "",
});

const editingId = ref(null);
const editDraft = ref({});
const status = ref({ kind: "", message: "" });

function relationLabel(rel) {
  const r = RELATIONSHIPS.find((x) => x.value === rel);
  return r ? `${r.emoji} ${r.label}` : rel;
}

function generatePersonKey(name, relationship) {
  const base = (name || relationship || "person")
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, "_")
    .replace(/_+/g, "_")
    .substring(0, 20);
  // Append random suffix to avoid collisions
  return `${base}_${Math.random().toString(36).substring(2, 6)}`;
}

async function submitNew() {
  status.value = { kind: "", message: "" };
  if (!newDraft.value.name) {
    status.value = { kind: "error", message: "Cần điền tên" };
    return;
  }
  if (!newDraft.value.person_key) {
    newDraft.value.person_key = generatePersonKey(
      newDraft.value.name, newDraft.value.relationship,
    );
  }
  try {
    await addMyPerson({
      ...newDraft.value,
      birth_year: newDraft.value.birth_year || null,
      birth_datetime_local: newDraft.value.birth_datetime_local || null,
    });
    status.value = { kind: "success", message: `✓ Đã thêm ${newDraft.value.name}` };
    newDraft.value = {
      person_key: "", name: "", relationship: "other",
      gender: "nam", birth_year: null, birth_datetime_local: "",
      timezone: "Asia/Ho_Chi_Minh", birth_place: "", notes: "",
    };
  } catch (e) {
    status.value = { kind: "error", message: e.message };
  }
}

function startEdit(p) {
  editingId.value = p.id;
  editDraft.value = { ...p };
}

function cancelEdit() {
  editingId.value = null;
  editDraft.value = {};
}

async function saveEdit() {
  if (!editingId.value) return;
  try {
    const patch = {};
    for (const k of ["name", "relationship", "gender", "birth_year",
                     "birth_datetime_local", "timezone", "birth_place", "notes"]) {
      if (editDraft.value[k] !== undefined) patch[k] = editDraft.value[k];
    }
    await updateMyPerson(editingId.value, patch);
    status.value = { kind: "success", message: "✓ Đã cập nhật" };
    editingId.value = null;
    editDraft.value = {};
  } catch (e) {
    status.value = { kind: "error", message: e.message };
  }
}

async function confirmDelete(p) {
  if (!confirm(`Xoá hồ sơ "${p.name}"? Hành động không thể hoàn tác.`)) return;
  try {
    await deleteMyPerson(p.id);
    status.value = { kind: "success", message: `✓ Đã xoá ${p.name}` };
  } catch (e) {
    status.value = { kind: "error", message: e.message };
  }
}

async function setActive(personKey) {
  setActivePerson(personKey);
  status.value = { kind: "success", message: `✓ Đã chọn hồ sơ hoạt động: ${personKey}` };
}

onMounted(() => {
  if (isAuthenticated.value) {
    loadMyPersons();
  }
});
</script>

<template>
  <div class="upp-wrap">
    <header class="upp-head">
      <div>
        <h2>👨‍👩‍👧 Hồ sơ cá nhân (server)</h2>
        <p>
          <template v-if="isAuthenticated">
            Đang đăng nhập: <b>{{ currentUser?.display_name }}</b> ({{ currentUser?.email }})
            · Dữ liệu lưu vĩnh viễn trên server, đồng bộ giữa các thiết bị.
          </template>
          <template v-else>
            ⚠️ <b>Chưa đăng nhập</b> — bấm "🔑 Đăng nhập" góc phải trên cùng để dùng tính năng này.
          </template>
        </p>
      </div>
      <button v-if="isAuthenticated" class="upp-refresh"
              @click="loadMyPersons" :disabled="isSyncing"
              :title="isSyncing ? 'Đang đồng bộ...' : 'Tải lại từ server'">
        {{ isSyncing ? "⏳" : "🔄" }} Refresh
      </button>
    </header>

    <div v-if="status.message" :class="['upp-status', `upp-status-${status.kind}`]">
      {{ status.message }}
    </div>
    <div v-if="syncError" class="upp-status upp-status-error">
      Lỗi đồng bộ: {{ syncError }}
    </div>

    <div v-if="!isAuthenticated" class="upp-guest">
      <p>Khi anh đăng nhập, tab này sẽ hiện hồ sơ vợ / con / đồng nghiệp đã lưu.</p>
    </div>

    <template v-else>
      <!-- Persons list -->
      <section class="upp-persons">
        <h3>{{ apiPersons.length }} hồ sơ trong namespace</h3>
        <p v-if="!apiPersons.length" class="upp-empty">
          Chưa có hồ sơ nào — thêm bằng form bên dưới.
        </p>
        <div v-for="p in apiPersons" :key="p.id" class="upp-card"
             :class="{ active: apiActivePersonKey === p.person_key }">
          <template v-if="editingId !== p.id">
            <div class="upp-card-head">
              <div class="upp-name">
                <span class="upp-rel">{{ relationLabel(p.relationship) }}</span>
                <strong>{{ p.name }}</strong>
                <span v-if="apiActivePersonKey === p.person_key" class="upp-active-tag">★ Đang dùng</span>
              </div>
              <div class="upp-actions">
                <button @click="setActive(p.person_key)" :disabled="apiActivePersonKey === p.person_key"
                        :title="apiActivePersonKey === p.person_key ? 'Đang là hồ sơ hoạt động' : 'Chọn làm hồ sơ hoạt động cho panels'">
                  ★
                </button>
                <button @click="startEdit(p)" title="Sửa">✏️</button>
                <button @click="confirmDelete(p)" class="upp-danger" title="Xoá">🗑</button>
              </div>
            </div>
            <div class="upp-card-body">
              <span><b>Sinh thần:</b> {{ p.birth_datetime_local || `năm ${p.birth_year}` || "—" }}</span>
              <span><b>Giới tính:</b> {{ p.gender || "—" }}</span>
              <span v-if="p.birth_place"><b>Nơi sinh:</b> {{ p.birth_place }}</span>
              <span><b>Key:</b> <code>{{ p.person_key }}</code></span>
              <p v-if="p.notes" class="upp-notes">📝 {{ p.notes }}</p>
            </div>
          </template>
          <template v-else>
            <div class="upp-edit-grid">
              <label>Tên
                <input v-model="editDraft.name" type="text" />
              </label>
              <label>Quan hệ
                <select v-model="editDraft.relationship">
                  <option v-for="r in RELATIONSHIPS" :key="r.value" :value="r.value">
                    {{ r.emoji }} {{ r.label }}
                  </option>
                </select>
              </label>
              <label>Giới tính
                <select v-model="editDraft.gender">
                  <option value="nam">Nam</option>
                  <option value="nữ">Nữ</option>
                </select>
              </label>
              <label>Năm sinh
                <input v-model.number="editDraft.birth_year" type="number" min="1900" max="2100" />
              </label>
              <label class="upp-full">Sinh thần đầy đủ (giờ)
                <input v-model="editDraft.birth_datetime_local" type="datetime-local" />
              </label>
              <label>Múi giờ
                <input v-model="editDraft.timezone" type="text" />
              </label>
              <label>Nơi sinh
                <input v-model="editDraft.birth_place" type="text" />
              </label>
              <label class="upp-full">Ghi chú
                <textarea v-model="editDraft.notes" rows="2"></textarea>
              </label>
              <div class="upp-edit-actions upp-full">
                <button @click="cancelEdit" class="upp-secondary">Huỷ</button>
                <button @click="saveEdit" class="upp-primary">💾 Lưu</button>
              </div>
            </div>
          </template>
        </div>
      </section>

      <!-- New person form -->
      <section class="upp-new">
        <h3>+ Thêm hồ sơ mới</h3>
        <div class="upp-edit-grid">
          <label class="upp-full">Tên đầy đủ <span class="req">*</span>
            <input v-model="newDraft.name" type="text" placeholder="vd: Nguyễn Văn A" />
          </label>
          <label>Quan hệ với anh
            <select v-model="newDraft.relationship">
              <option v-for="r in RELATIONSHIPS" :key="r.value" :value="r.value">
                {{ r.emoji }} {{ r.label }}
              </option>
            </select>
          </label>
          <label>Giới tính
            <select v-model="newDraft.gender">
              <option value="nam">Nam</option>
              <option value="nữ">Nữ</option>
            </select>
          </label>
          <label>Năm sinh
            <input v-model.number="newDraft.birth_year" type="number" min="1900" max="2100" placeholder="1992" />
          </label>
          <label class="upp-full">Sinh thần đầy đủ (cho engine — datetime-local)
            <input v-model="newDraft.birth_datetime_local" type="datetime-local" />
          </label>
          <label>Nơi sinh
            <input v-model="newDraft.birth_place" type="text" placeholder="vd: TP.HCM" />
          </label>
          <label class="upp-full">Ghi chú
            <textarea v-model="newDraft.notes" rows="2" placeholder="Đặc điểm, lưu ý..."></textarea>
          </label>
          <button @click="submitNew" class="upp-primary upp-full">+ Thêm hồ sơ</button>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.upp-wrap { padding: 1rem 1.2rem; max-width: 920px; margin: 0 auto; }
.upp-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  border-bottom: 1px solid #334155; padding-bottom: 0.7rem; margin-bottom: 1rem;
}
.upp-head h2 { margin: 0 0 0.2rem 0; color: #fde68a; font-size: 1.3rem; }
.upp-head p { margin: 0; font-size: 0.82rem; color: #94a3b8; line-height: 1.5; max-width: 600px; }
.upp-head b { color: #cbd5e1; }
.upp-refresh {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.upp-refresh:hover:not(:disabled) { background: #475569; }
.upp-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

.upp-status {
  padding: 0.45rem 0.7rem; border-radius: 4px; margin-bottom: 0.8rem; font-size: 0.85rem;
}
.upp-status-success { background: #064e3b; border: 1px solid #10b981; color: #6ee7b7; }
.upp-status-error { background: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5; }

.upp-guest {
  padding: 1.5rem; background: #1e293b; border-radius: 6px; text-align: center; color: #94a3b8;
}

.upp-persons, .upp-new {
  margin-bottom: 1.5rem;
}
.upp-persons h3, .upp-new h3 {
  margin: 0 0 0.6rem 0; color: #cbd5e1; font-size: 1.05rem; font-weight: 600;
  border-left: 3px solid #fde68a; padding-left: 0.5rem;
}
.upp-empty { color: #64748b; font-style: italic; padding: 0.5rem 0; }

.upp-card {
  background: #1e293b; border: 1px solid #334155; border-radius: 6px;
  padding: 0.7rem 0.9rem; margin-bottom: 0.6rem; transition: all 0.15s;
}
.upp-card.active { border-color: #fde68a; box-shadow: 0 0 0 2px rgba(253, 230, 138, 0.15); }
.upp-card-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.4rem;
}
.upp-name { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.upp-rel { font-size: 0.78rem; color: #94a3b8; }
.upp-name strong { color: #f1f5f9; font-size: 1rem; }
.upp-active-tag {
  background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff;
  padding: 1px 7px; border-radius: 3px; font-size: 0.7rem; font-weight: 600;
}
.upp-actions { display: flex; gap: 0.3rem; }
.upp-actions button {
  background: transparent; border: 1px solid #475569; color: #cbd5e1;
  width: 28px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.upp-actions button:hover:not(:disabled) { background: #334155; }
.upp-actions button:disabled { opacity: 0.4; cursor: not-allowed; }
.upp-actions .upp-danger { color: #fca5a5; }
.upp-actions .upp-danger:hover { background: rgba(239,68,68,0.15); border-color: #ef4444; }

.upp-card-body {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.3rem 0.9rem; font-size: 0.82rem; color: #cbd5e1;
}
.upp-card-body b { color: #94a3b8; font-weight: 500; }
.upp-card-body code { background: #0f172a; padding: 1px 4px; border-radius: 2px; font-size: 0.75rem; }
.upp-notes {
  grid-column: 1 / -1;
  margin: 0.3rem 0 0 0; padding: 0.4rem 0.6rem;
  background: rgba(100,116,139,0.15); border-left: 2px solid #64748b;
  border-radius: 0 3px 3px 0; font-size: 0.78rem; color: #94a3b8;
}

.upp-edit-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem;
}
.upp-edit-grid label {
  display: flex; flex-direction: column; gap: 0.2rem;
  font-size: 0.78rem; color: #94a3b8;
}
.upp-edit-grid input, .upp-edit-grid select, .upp-edit-grid textarea {
  background: #0f172a; border: 1px solid #475569; color: #e2e8f0;
  padding: 0.4rem 0.55rem; border-radius: 4px; font-size: 0.88rem; font-family: inherit;
}
.upp-edit-grid input:focus, .upp-edit-grid select:focus, .upp-edit-grid textarea:focus {
  outline: none; border-color: #fde68a;
}
.upp-edit-grid textarea { resize: vertical; }
.upp-full { grid-column: 1 / -1; }
.req { color: #fca5a5; }
.upp-edit-actions {
  display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.4rem;
}
.upp-primary, .upp-secondary {
  padding: 0.5rem 1.1rem; border: none; border-radius: 4px; cursor: pointer;
  font-size: 0.88rem; font-weight: 600;
}
.upp-primary {
  background: linear-gradient(135deg, #10b981, #059669); color: #fff;
}
.upp-primary:hover { background: linear-gradient(135deg, #34d399, #10b981); }
.upp-secondary { background: #334155; color: #cbd5e1; }
.upp-secondary:hover { background: #475569; }
</style>
