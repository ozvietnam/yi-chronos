<script setup>
import { computed, ref } from "vue";
import {
  EVENT_OUTCOMES,
  ORG_TYPES,
  PERSON_ROLES,
  activePersonId as guestActivePersonId,
  addEvent,
  addFamily,
  addOrganization,
  addPerson,
  events,
  families,
  getOrganizationById,
  getPersonById,
  organizations,
  persons as guestPersons,
  removeEvent,
  removeFamily,
  removeOrganization,
  removePerson,
  setActivePerson as setGuestActivePerson,
  updateEvent,
  updateFamily,
  updateOrganization,
  updatePerson,
} from "../stores/profileStore.js";
// Unified person store: returns DB persons when logged in, localStorage when guest.
// The top "Active person" picker must use this so anh sees his family members
// from the DB after login (not the legacy localStorage entries).
import {
  persons as unifiedPersons,
  activePerson,
  activePersonKey,
  setActivePerson,
} from "../stores/userDataStore.js";
import BirthShareButton from "./BirthShareButton.vue";
import UserPersonsPanel from "./UserPersonsPanel.vue";
import RedeemCodeWidget from "./RedeemCodeWidget.vue";
import { isAuthenticated } from "../stores/authStore.js";

// Unified id for picker option values: DB rows expose `person_key`, localStorage
// rows expose `id`. Normalise so the <select> works in both modes.
function personPickerKey(p) {
  return p?.person_key ?? p?.id ?? null;
}
function personPickerLabel(p) {
  if (!p) return "";
  const rel = p.relationship || p.role || "";
  const year = p.birth_year || (p.birth_datetime_local || "").slice(0, 4) || "?";
  return `${p.name} (${roleLabel(rel)}, ${year})`;
}

const activeSection = ref("persons");

const newPersonDraft = ref({
  name: "",
  role: "self",
  birth_year: "",
  birth_datetime_local: "",
  birth_location: "",
  notes: "",
});
const newFamilyDraft = ref({
  name: "Gia đình",
  member_ids: [],
  wedding_datetime_local: "",
});
const newOrgDraft = ref({
  name: "",
  type: "company",
  founded_datetime_local: "",
  member_links: [],
});
const newEventDraft = ref({
  title: "",
  datetime_local: "",
  confirmed_fact: true,
  outcome: "favorable",
  related_person_ids: [],
  related_org_ids: [],
  notes: "",
});

function roleLabel(role) {
  return PERSON_ROLES.find((r) => r.value === role)?.label || role;
}
function orgTypeLabel(type) {
  return ORG_TYPES.find((t) => t.value === type)?.label || type;
}
function outcomeLabel(outcome) {
  return EVENT_OUTCOMES.find((o) => o.value === outcome)?.label || outcome;
}

function submitPerson() {
  if (!newPersonDraft.value.name) return;
  addPerson(newPersonDraft.value);
  newPersonDraft.value = {
    name: "", role: "other", birth_year: "",
    birth_datetime_local: "", birth_location: "", notes: "",
  };
}

function submitFamily() {
  if (!newFamilyDraft.value.name || newFamilyDraft.value.member_ids.length === 0) return;
  addFamily(newFamilyDraft.value);
  newFamilyDraft.value = { name: "Gia đình", member_ids: [], wedding_datetime_local: "" };
}

function submitOrg() {
  if (!newOrgDraft.value.name) return;
  addOrganization(newOrgDraft.value);
  newOrgDraft.value = {
    name: "", type: "company", founded_datetime_local: "", member_links: [],
  };
}

function submitEvent() {
  if (!newEventDraft.value.title) return;
  addEvent(newEventDraft.value);
  newEventDraft.value = {
    title: "", datetime_local: "", confirmed_fact: true,
    outcome: "favorable", related_person_ids: [], related_org_ids: [], notes: "",
  };
}

function toggleMemberInDraft(personId, listKey, draftRef) {
  const list = draftRef.value[listKey];
  if (list.includes(personId)) {
    draftRef.value[listKey] = list.filter((id) => id !== personId);
  } else {
    draftRef.value[listKey] = [...list, personId];
  }
}

function memberPreviewNames(idList) {
  return idList
    .map((id) => getPersonById(id)?.name || "?")
    .join(", ");
}

const stats = computed(() => ({
  // Top "active person" picker now sources from the unified store, so the
  // count reflects what's actually selectable for that picker.
  persons: unifiedPersons.value.length,
  families: families.value.length,
  organizations: organizations.value.length,
  events: events.value.length,
}));
</script>

<template>
  <section class="panel profiles-panel">
    <div class="panel-title">
      <span>Hồ sơ — Person · Family · Organization · Event</span>
      <small>4 loại thực thể được dùng xuyên suốt các trường phái</small>
    </div>

    <RedeemCodeWidget v-if="isAuthenticated" />

    <!-- DB-backed user_persons (hiển thị khi đã đăng nhập) -->
    <UserPersonsPanel v-if="isAuthenticated" />
    <div v-else class="login-hint">
      <p>
        💡 <b>Đăng nhập</b> (góc trên phải) để dùng <b>Hồ sơ cá nhân server</b> —
        lưu vợ / con / đồng nghiệp / bạn vĩnh viễn trên DB, dùng cho mọi trường phái.
      </p>
      <p>
        Phần dưới là Hồ sơ <b>localStorage</b> (chỉ máy này, không sync) — vẫn dùng được cho khách.
      </p>
    </div>

    <div class="active-bar">
      <label class="ab-block">
        <span class="ab-label">Bản thân (active person)</span>
        <select :value="activePersonKey" @change="(e) => setActivePerson(e.target.value || null)">
          <option :value="null">— chưa chọn —</option>
          <option v-for="p in unifiedPersons" :key="personPickerKey(p)" :value="personPickerKey(p)">
            {{ personPickerLabel(p) }}
          </option>
        </select>
        <BirthShareButton
          v-if="activePerson?.birth_datetime_local"
          :birth-datetime-local="activePerson.birth_datetime_local"
          :person-name="activePerson.name"
          class="ab-share"
        />
      </label>
      <div class="ab-stats">
        <span><b>{{ stats.persons }}</b> Người</span>
        <span><b>{{ stats.families }}</b> Gia đình</span>
        <span><b>{{ stats.organizations }}</b> Tổ chức</span>
        <span><b>{{ stats.events }}</b> Sự kiện</span>
      </div>
    </div>

    <!--
      Legacy localStorage sub-tabs (Người · Gia đình · Tổ chức · Sự kiện).
      For logged-in users, person management lives in UserPersonsPanel above
      (DB-backed). Keeping these sub-tabs visible after login caused confusion:
      the dropdown at top showed DB persons, but this section showed unrelated
      localStorage rows like "Trần Hoàng Minh". Hide them post-login —
      Families/Orgs/Events stay localStorage-only for now (separate feature).
    -->
    <div v-if="!isAuthenticated" class="sub-tabs">
      <button :class="{ on: activeSection === 'persons' }" @click="activeSection = 'persons'">
        Người ({{ guestPersons.length }})
      </button>
      <button :class="{ on: activeSection === 'families' }" @click="activeSection = 'families'">
        Gia đình ({{ stats.families }})
      </button>
      <button :class="{ on: activeSection === 'organizations' }" @click="activeSection = 'organizations'">
        Tổ chức ({{ stats.organizations }})
      </button>
      <button :class="{ on: activeSection === 'events' }" @click="activeSection = 'events'">
        Sự kiện ({{ stats.events }})
      </button>
    </div>

    <template v-if="!isAuthenticated">

    <!-- ====================== PERSONS ====================== -->
    <div v-if="activeSection === 'persons'" class="section">
      <h5>Thêm người mới</h5>
      <div class="form-grid">
        <label><span>Họ tên</span>
          <input v-model="newPersonDraft.name" type="text" placeholder="vd: Nguyễn Văn A" />
        </label>
        <label><span>Vai trò</span>
          <select v-model="newPersonDraft.role">
            <option v-for="r in PERSON_ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </label>
        <label><span>Năm sinh</span>
          <input v-model.number="newPersonDraft.birth_year" type="number" placeholder="1988" min="1900" max="2100" />
        </label>
        <label><span>Ngày giờ sinh chi tiết</span>
          <input v-model="newPersonDraft.birth_datetime_local" type="datetime-local" step="60" />
        </label>
        <label><span>Nơi sinh (tuỳ chọn)</span>
          <input v-model="newPersonDraft.birth_location" type="text" placeholder="vd: Hà Nội" />
        </label>
        <button class="add-btn primary-add" @click="submitPerson">+ Thêm người</button>
      </div>
      <p class="form-hint">
        Vai trò "Bản thân" chỉ nên có 1. Ngày giờ chi tiết giúp tính chính xác hơn — nếu không có, dùng năm sinh.
      </p>

      <h5>Danh sách đã có ({{ guestPersons.length }} người)</h5>
      <div v-if="guestPersons.length" class="entity-list-wrap">
        <div class="list-header">
          <span>Họ tên</span>
          <span>Vai trò</span>
          <span>Năm</span>
          <span>Ngày giờ sinh</span>
          <span></span>
          <span></span>
        </div>
        <ul class="entity-list">
          <li v-for="p in guestPersons" :key="p.id" :class="{ active: p.id === guestActivePersonId }">
            <input type="text" :value="p.name" @input="(e) => updatePerson(p.id, { name: e.target.value })" />
            <select :value="p.role" @change="(e) => updatePerson(p.id, { role: e.target.value })">
              <option v-for="r in PERSON_ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
            <input type="number" :value="p.birth_year" @input="(e) => updatePerson(p.id, { birth_year: Number(e.target.value) })" />
            <input type="datetime-local" step="60" :value="p.birth_datetime_local"
              @input="(e) => updatePerson(p.id, { birth_datetime_local: e.target.value })" />
            <button class="select-btn" :class="{ on: p.id === guestActivePersonId }" @click="setGuestActivePerson(p.id)"
              :title="p.id === guestActivePersonId ? 'Đang là active person' : 'Đặt làm active person'">
              {{ p.id === guestActivePersonId ? '★ ACTIVE' : 'Chọn' }}
            </button>
            <button class="del-btn" @click="removePerson(p.id)" title="Xoá">×</button>
          </li>
        </ul>
      </div>
      <p v-else class="empty">Chưa có người nào. Bắt đầu bằng cách thêm "Bản thân" ở form trên.</p>
    </div>

    <!-- ====================== FAMILIES ====================== -->
    <div v-if="activeSection === 'families'" class="section">
      <h5>Tạo gia đình</h5>
      <div class="form-block">
        <input v-model="newFamilyDraft.name" type="text" placeholder="Tên gia đình (vd: Gia đình Anh)" />
        <label>
          <span>Ngày cưới (tuỳ chọn — cho Quẻ Gia Đạo)</span>
          <input v-model="newFamilyDraft.wedding_datetime_local" type="datetime-local" step="60" />
        </label>
        <div class="member-select">
          <span>Chọn thành viên (từ Persons):</span>
          <div class="checkbox-grid">
            <label v-for="p in guestPersons" :key="p.id" class="cb">
              <input type="checkbox"
                :checked="newFamilyDraft.member_ids.includes(p.id)"
                @change="toggleMemberInDraft(p.id, 'member_ids', newFamilyDraft)" />
              <span>{{ p.name }} ({{ roleLabel(p.role) }})</span>
            </label>
          </div>
          <small v-if="newFamilyDraft.member_ids.length === 0">Phải chọn ≥1 thành viên</small>
        </div>
        <button class="add-btn" @click="submitFamily">+ Tạo gia đình</button>
      </div>

      <h5>Danh sách ({{ stats.families }})</h5>
      <ul v-if="families.length" class="entity-list block">
        <li v-for="f in families" :key="f.id">
          <div class="entity-head">
            <strong>{{ f.name }}</strong>
            <button class="del-btn" @click="removeFamily(f.id)">×</button>
          </div>
          <div class="entity-body">
            <span><b>{{ f.member_ids.length }} thành viên:</b> {{ memberPreviewNames(f.member_ids) }}</span>
            <span v-if="f.wedding_datetime_local"><b>Cưới:</b> {{ f.wedding_datetime_local }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="empty">Chưa có gia đình. Cần ≥1 người trong tab Người trước.</p>
    </div>

    <!-- ====================== ORGANIZATIONS ====================== -->
    <div v-if="activeSection === 'organizations'" class="section">
      <h5>Tạo tổ chức</h5>
      <div class="form-block">
        <input v-model="newOrgDraft.name" type="text" placeholder="Tên tổ chức (vd: Công ty XYZ)" />
        <select v-model="newOrgDraft.type">
          <option v-for="t in ORG_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
        <label>
          <span>Ngày thành lập (tuỳ chọn)</span>
          <input v-model="newOrgDraft.founded_datetime_local" type="datetime-local" step="60" />
        </label>
        <button class="add-btn" @click="submitOrg">+ Tạo tổ chức</button>
      </div>

      <h5>Danh sách ({{ stats.organizations }})</h5>
      <ul v-if="organizations.length" class="entity-list block">
        <li v-for="o in organizations" :key="o.id">
          <div class="entity-head">
            <strong>{{ o.name }}</strong>
            <span class="badge">{{ orgTypeLabel(o.type) }}</span>
            <button class="del-btn" @click="removeOrganization(o.id)">×</button>
          </div>
          <div class="entity-body">
            <span v-if="o.founded_datetime_local"><b>Thành lập:</b> {{ o.founded_datetime_local }}</span>
            <span><b>Thành viên:</b> {{ o.member_links.length }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="empty">Chưa có tổ chức.</p>
    </div>

    <!-- ====================== EVENTS ====================== -->
    <div v-if="activeSection === 'events'" class="section">
      <h5>Ghi nhận sự kiện đã xảy ra (fact)</h5>
      <p class="pf-note">
        Sự kiện đã xảy ra dùng để <b>đối chiếu</b> output của các trường phái.
        Vd: "Năm 2022 tôi chuyển công ty" — sau này khi engine cho rằng năm 2022 anh
        nên có biến động lớn → match. Càng nhiều fact, càng có dữ liệu validation.
      </p>
      <div class="form-block">
        <input v-model="newEventDraft.title" type="text" placeholder="Tiêu đề sự kiện (vd: Chuyển công ty)" />
        <label>
          <span>Thời điểm xảy ra</span>
          <input v-model="newEventDraft.datetime_local" type="datetime-local" step="60" />
        </label>
        <label>
          <span>Kết quả</span>
          <select v-model="newEventDraft.outcome">
            <option v-for="o in EVENT_OUTCOMES" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>
        <label class="cb-inline">
          <input type="checkbox" v-model="newEventDraft.confirmed_fact" />
          <span>Là fact đã xác nhận (mặc định)</span>
        </label>
        <div class="member-select" v-if="guestPersons.length">
          <span>Người liên quan:</span>
          <div class="checkbox-grid">
            <label v-for="p in guestPersons" :key="p.id" class="cb">
              <input type="checkbox"
                :checked="newEventDraft.related_person_ids.includes(p.id)"
                @change="toggleMemberInDraft(p.id, 'related_person_ids', newEventDraft)" />
              <span>{{ p.name }}</span>
            </label>
          </div>
        </div>
        <div class="member-select" v-if="organizations.length">
          <span>Tổ chức liên quan:</span>
          <div class="checkbox-grid">
            <label v-for="o in organizations" :key="o.id" class="cb">
              <input type="checkbox"
                :checked="newEventDraft.related_org_ids.includes(o.id)"
                @change="toggleMemberInDraft(o.id, 'related_org_ids', newEventDraft)" />
              <span>{{ o.name }}</span>
            </label>
          </div>
        </div>
        <textarea v-model="newEventDraft.notes" placeholder="Mô tả ngắn (tuỳ chọn)" rows="2"></textarea>
        <button class="add-btn" @click="submitEvent">+ Ghi nhận sự kiện</button>
      </div>

      <h5>Danh sách ({{ stats.events }})</h5>
      <ul v-if="events.length" class="entity-list block">
        <li v-for="e in events" :key="e.id" :class="['event-card', `outcome-${e.outcome}`]">
          <div class="entity-head">
            <strong>{{ e.title }}</strong>
            <span class="badge">{{ outcomeLabel(e.outcome) }}</span>
            <span v-if="e.confirmed_fact" class="fact-tag">FACT</span>
            <button class="del-btn" @click="removeEvent(e.id)">×</button>
          </div>
          <div class="entity-body">
            <span><b>Thời điểm:</b> {{ e.datetime_local || '—' }}</span>
            <span v-if="e.related_person_ids.length">
              <b>Người:</b> {{ memberPreviewNames(e.related_person_ids) }}
            </span>
            <span v-if="e.notes"><b>Ghi chú:</b> {{ e.notes }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="empty">Chưa có sự kiện nào.</p>
    </div>
    </template>
  </section>
</template>

<style scoped>
.profiles-panel { display: flex; flex-direction: column; gap: 16px; }

.pf-note {
  font-size: 13px; color: var(--text-secondary, rgba(230,238,245,0.72));
  border-left: 3px solid var(--accent-gold, #e8c95a); padding-left: 12px;
  margin: 0; line-height: 1.6;
}

.active-bar {
  display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: center;
  background: rgba(232,201,90,0.08);
  border: 1px solid var(--border-accent, rgba(232,201,90,0.3));
  padding: 12px 14px; border-radius: 8px;
}
.ab-block { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.ab-label {
  font-size: 11px; color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}
.active-bar select {
  background: var(--bg-input, rgba(0,0,0,0.35));
  border: 1px solid var(--border-medium, rgba(255,255,255,0.14));
  color: var(--text-primary, #e6eef5); border-radius: 6px; padding: 7px 10px;
  font-size: 13px; min-height: 36px; margin-top: 0;
}
.ab-stats {
  display: flex; gap: 14px; flex-wrap: wrap;
  font-size: 12px; color: var(--text-muted, rgba(230,238,245,0.5));
}
.ab-stats b { color: var(--accent-gold-soft, #f5e6b1); font-weight: 700; }

.sub-tabs {
  display: flex; gap: 6px; flex-wrap: wrap;
  border-bottom: 1px solid var(--border-soft, rgba(255,255,255,0.08));
  padding-bottom: 8px;
}
.sub-tabs button {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-medium, rgba(255,255,255,0.14));
  color: var(--text-secondary, rgba(230,238,245,0.72));
  padding: 7px 14px; border-radius: 6px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.sub-tabs button:hover { background: rgba(255,255,255,0.08); color: var(--text-primary, #e6eef5); }
.sub-tabs button.on {
  background: rgba(232,201,90,0.18);
  border-color: var(--border-accent, rgba(232,201,90,0.35));
  color: var(--accent-gold, #e8c95a);
}

.section { display: flex; flex-direction: column; gap: 14px; }

h5 {
  margin: 4px 0 0 0; font-size: 12px;
  color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 700;
}

.form-grid {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr 0.6fr 1.3fr 1fr auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255,255,255,0.08));
}
.form-grid label {
  display: flex; flex-direction: column; gap: 4px;
}
.form-grid label span {
  font-size: 11px;
  color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}
.form-grid input,
.form-grid select {
  margin: 0;
}

.form-hint {
  font-size: 12px; color: var(--text-muted, rgba(230,238,245,0.5));
  font-style: italic; margin: 0;
}

.list-header {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr 0.6fr 1.3fr 90px 30px;
  gap: 8px; padding: 0 8px;
  font-size: 11px; color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}

.form-block {
  display: flex; flex-direction: column; gap: 8px;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px;
}
.form-block label {
  display: flex; flex-direction: column; gap: 3px;
  font-size: 0.78rem; color: rgba(255,255,255,0.7);
}
.form-block input, .form-block select, .form-block textarea, .form-row input, .form-row select {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 8px; font-size: 0.85rem;
  font-family: inherit;
}

.cb-inline { flex-direction: row !important; align-items: center; gap: 6px; }

.member-select { display: flex; flex-direction: column; gap: 4px; font-size: 0.78rem; color: rgba(255,255,255,0.75); }
.member-select > span { color: rgba(255,255,255,0.55); }
.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 4px; }
.cb { display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 0.78rem; }

.add-btn {
  background: rgba(232,201,90,0.2);
  border: 1px solid var(--border-accent, rgba(232,201,90,0.5));
  color: var(--accent-gold, #e8c95a);
  padding: 8px 14px; border-radius: 6px;
  font-size: 13px; font-weight: 600; cursor: pointer; align-self: flex-start;
  white-space: nowrap;
  transition: background 0.15s;
}
.add-btn:hover { background: rgba(232,201,90,0.32); }
.primary-add { padding: 8px 16px; min-height: 38px; }

.entity-list-wrap { display: flex; flex-direction: column; gap: 4px; }
.entity-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }

.entity-list li {
  background: rgba(255,255,255,0.04);
  border: 1px solid transparent;
  border-radius: 6px; padding: 8px 10px;
  display: grid;
  grid-template-columns: 1.4fr 0.9fr 0.6fr 1.3fr 90px 30px;
  gap: 8px; align-items: center;
  font-size: 13px;
}
.entity-list li input,
.entity-list li select {
  margin: 0; min-height: 32px;
}
.entity-list li.active {
  border-color: var(--border-accent, rgba(232,201,90,0.4));
  background: rgba(232,201,90,0.07);
}
.entity-list.block li { display: flex; flex-direction: column; gap: 4px; }

.entity-head {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 0.86rem;
}
.entity-head strong { color: #f5e6b1; }
.entity-body {
  display: flex; gap: 12px; flex-wrap: wrap; font-size: 0.78rem;
  color: rgba(255,255,255,0.7);
}
.entity-body b { color: rgba(255,255,255,0.5); font-weight: 500; }

.inline { background: transparent !important; border: 1px solid transparent !important; }
.inline:focus { border-color: rgba(255,255,255,0.2) !important; }
.year-input { max-width: 80px; }

.select-btn {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.85); padding: 3px 8px; border-radius: 4px;
  font-size: 0.74rem; cursor: pointer;
}
.select-btn.on { background: rgba(232,201,90,0.2); border-color: rgba(232,201,90,0.5); color: #e8c95a; font-weight: 600; }

.del-btn {
  background: rgba(214,90,74,0.18); border: 1px solid rgba(214,90,74,0.4);
  color: #ff9080; padding: 2px 8px; border-radius: 4px;
  font-size: 0.9rem; cursor: pointer; line-height: 1;
}

.badge {
  background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 3px;
  font-size: 0.7rem; color: rgba(255,255,255,0.7);
}
.fact-tag {
  background: rgba(90,176,122,0.2); color: #9adcb0;
  padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; font-weight: 700;
  letter-spacing: 0.5px;
}

.event-card.outcome-favorable { border-left: 3px solid #5ab07a; padding-left: 8px; }
.event-card.outcome-neutral { border-left: 3px solid #9adfe5; padding-left: 8px; }
.event-card.outcome-challenging { border-left: 3px solid #d65a4a; padding-left: 8px; }
.event-card.outcome-unknown { border-left: 3px solid #888; padding-left: 8px; }

.empty { font-size: 0.85rem; color: rgba(255,255,255,0.5); text-align: center; padding: 16px 0; margin: 0; }

.login-hint {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  border: 1px dashed #475569; border-radius: 6px;
  padding: 0.9rem 1.1rem; margin: 0.8rem 0;
  color: #cbd5e1; font-size: 0.85rem; line-height: 1.6;
}
.login-hint p { margin: 0 0 0.35rem 0; }
.login-hint p:last-child { margin-bottom: 0; color: #94a3b8; font-size: 0.78rem; }
.login-hint b { color: #fde68a; }
</style>
