<script setup>
import { computed, ref } from "vue";
import { postFamilyResonance } from "../lib/api";
import {
  familyMembers as sharedFamilyMembers,
  weddingDatetime as sharedWedding,
  setFamily,
  clearFamily,
} from "../stores/familyStore.js";

const ROLE_OPTIONS = [
  { value: "self", label: "Bản thân" },
  { value: "spouse", label: "Vợ / Chồng" },
  { value: "child", label: "Con" },
  { value: "parent", label: "Cha mẹ" },
  { value: "sibling", label: "Anh chị em" },
  { value: "boss", label: "Cấp trên" },
];

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

const INTERACTION_COLOR = {
  "đồng chi": "#9adfe5",
  "lục hợp": "#5ab07a",
  "tam hợp": "#5ab07a",
  "xung": "#d65a4a",
  "trung tính": "#888",
};

const CLASH_LABEL = {
  "khắc": "khắc",
  "đồng": "đồng hành",
  "sinh": "sinh",
  "neutral": "trung tính",
};

// Use shared store so other panels (PersonalQuai, GPS) pick up the same family.
const members = sharedFamilyMembers;
const weddingDatetime = sharedWedding;
// Initialize with defaults if store is empty.
if (members.value.length === 0) {
  // Default = founder profile (anh — 1988-06-05). See data/yi_hermes/founder_profile.md
  members.value = [
    { role: "self", name: "Anh", birth_year: 1988, birth_datetime_local: "1988-06-05T23:30:00" },
    { role: "spouse", name: "", birth_year: 1992, birth_datetime_local: "" },
  ];
}
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");

function addMember(role = "child") {
  members.value.push({ role, name: "", birth_year: 2020, birth_datetime_local: "" });
}

function removeMember(idx) {
  members.value.splice(idx, 1);
}

async function load() {
  errorMsg.value = "";
  loading.value = true;
  try {
    const cleanMembers = members.value
      .filter((m) => m.birth_year && m.name)
      .map((m) => ({
        role: m.role,
        name: m.name,
        birth_year: Number(m.birth_year),
        birth_datetime_local: m.birth_datetime_local
          ? (m.birth_datetime_local.length === 16
              ? m.birth_datetime_local + ":00"
              : m.birth_datetime_local)
          : null,
      }));
    if (cleanMembers.length === 0) {
      errorMsg.value = "Cần ít nhất 1 thành viên có tên + năm sinh";
      return;
    }
    const wedding = weddingDatetime.value
      ? (weddingDatetime.value.length === 16 ? weddingDatetime.value + ":00" : weddingDatetime.value)
      : null;
    const result = await postFamilyResonance({
      members: cleanMembers,
      weddingDatetimeLocal: wedding,
    });
    if (result.status === "ok") {
      data.value = result;
    } else {
      errorMsg.value = result.message || "Không tính được";
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

const roleLabel = (role) =>
  ROLE_OPTIONS.find((o) => o.value === role)?.label || role;

const overlayItems = computed(() => data.value?.thai_tue_overlay || []);
const bridges = computed(() => data.value?.bridges || []);
const unifiedSig = computed(() => data.value?.unified_household?.member_signatures || []);
</script>

<template>
  <section class="panel fs-panel">
    <div class="panel-title">
      <span>Hệ thống Gia đạo — đa chủ thể</span>
      <small>4 phương pháp hợp nhất</small>
    </div>

    <p class="fs-note">
      Một người không phải hòn đảo. Khi anh có vợ + con, năng lượng cộng hưởng.
      Hệ thống tính: <b>(1)</b> Quẻ Gia Đạo từ ngày cưới · <b>(2)</b> Thái Tuế Nhập Quái —
      chi sinh từng người ánh vào lá số · <b>(3)</b> Số học Mai Hoa hợp nhất ·
      <b>(4)</b> Element bridging — phát hiện ai làm cầu nối thông quan.
    </p>

    <div class="fs-form">
      <h5>Thành viên gia đình</h5>
      <div v-for="(m, idx) in members" :key="idx" class="member-row">
        <select v-model="m.role">
          <option v-for="opt in ROLE_OPTIONS" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <input v-model="m.name" type="text" placeholder="Tên" />
        <input v-model.number="m.birth_year" type="number" min="1900" max="2100" placeholder="Năm" />
        <input v-model="m.birth_datetime_local" type="datetime-local" step="60"
          title="Ngày giờ sinh chính xác (tuỳ chọn — nếu trống chỉ dùng năm)" />
        <button class="del-btn" @click="removeMember(idx)" v-if="members.length > 1">×</button>
      </div>
      <div class="add-row">
        <button class="add-btn" @click="addMember('child')">+ Thêm con</button>
        <button class="add-btn" @click="addMember('parent')">+ Thêm cha mẹ</button>
        <button class="add-btn" @click="addMember('sibling')">+ Thêm anh chị em</button>
      </div>

      <h5>Ngày cưới (tuỳ chọn — cho Quẻ Gia Đạo)</h5>
      <input v-model="weddingDatetime" type="datetime-local" step="60" />

      <button class="apply-btn" @click="load" :disabled="loading">
        {{ loading ? "Đang tính..." : "Tính cộng hưởng gia đình" }}
      </button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <!-- Method 1: Marriage / Self natal -->
      <div class="fs-row">
        <div v-if="data.self_natal" class="natal-card">
          <h6>Quẻ bản mệnh chủ hộ</h6>
          <strong>{{ data.self_natal.primary_name }}</strong>
          <small>quẻ {{ data.self_natal.primary_king_wen }} · {{ data.self_natal.primary_binary }}</small>
          <span class="meta">{{ data.self_natal.upper_trigram }} / {{ data.self_natal.lower_trigram }}</span>
        </div>
        <div v-if="data.marriage_hexagram" class="natal-card marriage">
          <h6>Quẻ Gia Đạo (ngày cưới)</h6>
          <strong>{{ data.marriage_hexagram.primary_name }}</strong>
          <small>quẻ {{ data.marriage_hexagram.primary_king_wen }} · {{ data.marriage_hexagram.primary_binary }}</small>
          <span class="meta">{{ data.marriage_hexagram.upper_trigram }} / {{ data.marriage_hexagram.lower_trigram }}</span>
        </div>
      </div>

      <!-- Method 2: Thái Tuế overlay -->
      <h5 v-if="overlayItems.length">Thái Tuế Nhập Quái — chi sinh các thành viên</h5>
      <ul class="overlay-list">
        <li v-for="(item, i) in overlayItems" :key="i"
          :style="{ borderLeftColor: INTERACTION_COLOR[item.interaction] }">
          <div class="ov-head">
            <strong>{{ item.member_role_vi }} · {{ item.member_name }}</strong>
            <span class="ov-branch">chi {{ item.member_year_branch }}</span>
            <span class="ov-luc-than" v-if="item.luc_than_target !== '—'">
              vai trò: {{ item.luc_than_target }}
            </span>
            <span class="ov-int" :style="{ color: INTERACTION_COLOR[item.interaction] }">
              {{ item.interaction }} ({{ item.score >= 0 ? '+' : '' }}{{ item.score }})
            </span>
          </div>
          <div class="ov-expl">{{ item.explanation }}</div>
        </li>
      </ul>

      <!-- Method 3: Unified household -->
      <h5>Số học Mai Hoa hợp nhất</h5>
      <div class="unified-block">
        <div class="formula">
          <div>
            Số lý của từng thành viên =
            <code>year_branch_idx + lunar_month + lunar_day</code>
          </div>
          <ul class="sig-list">
            <li v-for="s in unifiedSig" :key="s.name">
              {{ roleLabel(s.role) }} <b>{{ s.name }}</b>:
              chi <b>{{ s.year_branch }}</b> ({{ s.year_branch_idx }})
              · âm lịch {{ s.lunar_day }}/{{ s.lunar_month }}
              → <b>{{ s.signature_sum }}</b>
            </li>
          </ul>
          <div class="formula-line">
            <span>
              Thượng = (chồng + vợ + ngoại trừ con) mod 8 =
              <b>{{ data.unified_household.sum_excluding_children }} mod 8 = {{ data.unified_household.upper_num }}</b>
              ({{ data.unified_household.upper_trigram }})
            </span>
          </div>
          <div class="formula-line">
            <span>
              Hạ = (cả nhà gồm con) mod 8 =
              <b>{{ data.unified_household.sum_full }} mod 8 = {{ data.unified_household.lower_num }}</b>
              ({{ data.unified_household.lower_trigram }})
            </span>
          </div>
          <div class="formula-line">
            <span>Hào động = ({{ data.unified_household.sum_full }}) mod 6 = <b>{{ data.unified_household.moving_line }}</b></span>
          </div>
        </div>
        <div class="unified-result">
          <h6>Quẻ hợp nhất gia đạo</h6>
          <strong>{{ data.unified_household.primary_name }}</strong>
          <small>quẻ {{ data.unified_household.primary_king_wen }} · {{ data.unified_household.primary_binary }}</small>
          <div class="derived-row">
            <span v-for="key in ['chanh', 'ho', 'bien', 'giao', 'phuc', 'bao']" :key="key" class="d-cell">
              <span class="dk">{{ key }}</span>
              <span class="dn">{{ data.unified_household.derived_hexagrams[key].name_vi }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Method 4: Bridges -->
      <h5>Cầu nối ngũ hành (Element bridging)</h5>
      <ul class="bridges-list">
        <li v-for="(b, i) in bridges" :key="i" :class="['bridge', `clash-${b.clash_type}`]">
          <span class="b-pair">
            <span :style="{ color: ELEMENT_COLOR[b.element_a] }">{{ b.pair_a }} ({{ b.element_a }})</span>
            <span class="b-vs">↔</span>
            <span :style="{ color: ELEMENT_COLOR[b.element_b] }">{{ b.pair_b }} ({{ b.element_b }})</span>
          </span>
          <span class="b-clash">{{ CLASH_LABEL[b.clash_type] }}</span>
          <span v-if="b.bridge_member" class="b-bridge">
            ✓ <b>{{ b.bridge_member }}</b> ({{ b.bridge_element }}) thông quan: {{ b.bridge_path }}
          </span>
          <span v-else-if="b.clash_type === 'khắc'" class="b-no-bridge">
            ✗ chưa có thành viên thông quan
          </span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.fs-panel { display: flex; flex-direction: column; gap: 12px; }

.fs-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}

h5 {
  margin: 6px 0 0 0; font-size: 0.85rem;
  color: rgba(255,255,255,0.85); text-transform: uppercase;
  letter-spacing: 0.4px; font-weight: 600;
}
h6 {
  margin: 0 0 4px 0; font-size: 0.74rem;
  color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.4px;
}

.fs-form {
  display: flex; flex-direction: column; gap: 8px;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}

.member-row {
  display: grid;
  grid-template-columns: 100px 1fr 80px 1fr 30px;
  gap: 6px; align-items: center;
}

.member-row select,
.member-row input,
.fs-form > input[type="datetime-local"] {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}

.del-btn {
  background: rgba(214,90,74,0.18); border: 1px solid rgba(214,90,74,0.4);
  color: #ff9080; padding: 3px 8px; border-radius: 4px;
  font-size: 0.9rem; cursor: pointer; line-height: 1;
}

.add-row { display: flex; gap: 6px; flex-wrap: wrap; }
.add-btn {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.85); padding: 5px 12px; border-radius: 5px;
  font-size: 0.78rem; cursor: pointer;
}

.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 8px 16px; border-radius: 6px;
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.fs-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}

.natal-card {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 2px;
}
.natal-card.marriage { border-color: rgba(232,201,90,0.4); background: rgba(232,201,90,0.06); }
.natal-card strong { font-size: 1.1rem; color: #f5e6b1; }
.natal-card small { color: rgba(255,255,255,0.55); font-size: 0.72rem; }
.natal-card .meta { font-size: 0.78rem; color: rgba(255,255,255,0.7); margin-top: 4px; }

.overlay-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}
.overlay-list li {
  background: rgba(255,255,255,0.04); border-left: 3px solid;
  border-radius: 0 6px 6px 0; padding: 6px 10px;
}
.ov-head {
  display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap;
  font-size: 0.82rem;
}
.ov-head strong { color: #f5e6b1; }
.ov-branch { color: rgba(255,255,255,0.6); font-family: ui-monospace, monospace; font-size: 0.74rem; }
.ov-luc-than { font-size: 0.74rem; color: rgba(255,255,255,0.5); }
.ov-int { font-weight: 700; margin-left: auto; }
.ov-expl { font-size: 0.78rem; color: rgba(255,255,255,0.78); margin-top: 3px; }

.unified-block {
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
  display: grid; grid-template-columns: 1.4fr 1fr; gap: 12px;
}
.formula {
  font-size: 0.8rem; color: rgba(255,255,255,0.85); line-height: 1.5;
  display: flex; flex-direction: column; gap: 6px;
}
.formula code {
  background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 3px;
  font-size: 0.74rem;
}
.sig-list {
  list-style: disc inside; margin: 0; padding: 4px 0;
  font-size: 0.74rem; color: rgba(255,255,255,0.78);
}
.sig-list b { color: #f5e6b1; }
.formula-line {
  font-size: 0.78rem; color: rgba(255,255,255,0.85);
  padding: 3px 6px; background: rgba(232,201,90,0.05); border-radius: 4px;
}
.formula-line b { color: #e8c95a; }

.unified-result {
  background: rgba(232,201,90,0.06); border: 1px solid rgba(232,201,90,0.25);
  border-radius: 6px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 4px;
}
.unified-result strong { font-size: 1.1rem; color: #f5e6b1; }
.unified-result small { color: rgba(255,255,255,0.55); font-size: 0.72rem; }

.derived-row { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
.d-cell {
  display: flex; gap: 4px; align-items: baseline;
  background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 3px;
  font-size: 0.7rem;
}
.d-cell .dk { color: rgba(255,255,255,0.5); text-transform: uppercase; }
.d-cell .dn { color: rgba(255,255,255,0.85); }

.bridges-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 3px;
}
.bridge {
  background: rgba(255,255,255,0.04); padding: 6px 10px; border-radius: 5px;
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  font-size: 0.82rem;
}
.bridge.clash-khắc { background: rgba(214,90,74,0.06); border: 1px solid rgba(214,90,74,0.2); }
.bridge.clash-sinh { background: rgba(90,176,122,0.05); border: 1px solid rgba(90,176,122,0.2); }
.bridge.clash-đồng { background: rgba(74,176,194,0.05); border: 1px solid rgba(74,176,194,0.2); }

.b-pair { display: flex; gap: 4px; align-items: center; }
.b-vs { color: rgba(255,255,255,0.4); }
.b-clash {
  text-transform: uppercase; letter-spacing: 0.4px;
  font-size: 0.7rem; padding: 1px 6px; border-radius: 3px;
  background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.7);
}
.b-bridge { color: #5ab07a; font-size: 0.78rem; }
.b-bridge b { color: #9adcb0; }
.b-no-bridge { color: rgba(214,90,74,0.85); font-size: 0.78rem; font-style: italic; }
</style>
