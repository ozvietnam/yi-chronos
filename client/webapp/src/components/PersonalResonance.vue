<script setup>
import { reactive, ref, watch } from "vue";
import { Send, UserPlus } from "lucide-vue-next";
import { compareBasic, convertCalendar } from "../lib/api";
import { isAuthenticated } from "../stores/authStore.js";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import ActivePersonBar from "./ActivePersonBar.vue";

const props = defineProps({
  personal: {
    type: Object,
    default: null
  },
  profiles: {
    type: Array,
    default: () => []
  },
  activeProfileId: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["submit-profile", "profile-select", "profile-create"]);

// Form defaults — empty, không hardcode founder birth (privacy 2026-05-27).
const form = reactive({
  profile_label: "",
  birth_datetime_local: "",
  timezone: "Asia/Ho_Chi_Minh",
  location_ref: "",
  birth_precision: "exact",
  gender_optional: null
});

const calendarForm = reactive({
  datetime_local: "",
  timezone: "Asia/Ho_Chi_Minh",
  source_calendar: "solar",
  is_leap_month: false
});
const calendarResult = ref(null);
const compareResult = ref(null);
const localError = ref("");

function applyProfileFromProp(profile) {
  if (!profile) return;
  form.profile_label = profile.label ?? "";
  form.birth_datetime_local = profile.birth_datetime_local;
  form.timezone = profile.timezone;
  form.location_ref = profile.location_ref ?? "";
  form.birth_precision = profile.birth_precision ?? "exact";
  form.gender_optional = profile.gender_optional ?? null;
  calendarForm.datetime_local = profile.birth_datetime_local;
  calendarForm.timezone = profile.timezone;
}

watch(
  () => [props.profiles, props.activeProfileId],
  () => {
    const p = props.profiles?.find((x) => x.id === props.activeProfileId);
    if (p) applyProfileFromProp(p);
  },
  { immediate: true, deep: true }
);

function onProfileSelect(ev) {
  emit("profile-select", ev.target.value);
}

function createProfile() {
  emit("profile-create");
}

// Đã đăng nhập → ngày sinh lấy từ HỒ SƠ tài khoản (nhập 1 lần, Anh chốt 2026-07-18);
// khách chưa đăng nhập vẫn tự nhập ở form dưới (hồ sơ lưu máy).
useActivePersonBirth(
  {
    get value() { return form.birth_datetime_local; },
    set value(v) { form.birth_datetime_local = v; },
  },
  {
    genderRef: {
      get value() { return form.gender_optional; },
      set value(v) { form.gender_optional = v; },
    },
  },
);

function submit() {
  emit("submit-profile", { ...form });
}

async function runCalendarConvert() {
  localError.value = "";
  try {
    calendarResult.value = await convertCalendar({ ...calendarForm });
  } catch (_error) {
    localError.value = "Không chuyển đổi được âm/dương lịch.";
  }
}

async function runCompareBasic() {
  localError.value = "";
  try {
    compareResult.value = await compareBasic({
      birth_datetime_local: form.birth_datetime_local,
      timezone: form.timezone,
      location_ref: form.location_ref
    });
  } catch (_error) {
    localError.value = "Không tạo được báo cáo so sánh cơ bản.";
  }
}
</script>

<template>
  <section class="panel personal-panel">
    <div class="panel-title">
      <span>Cộng hưởng cá nhân</span>
      <small>giờ dân dụng</small>
    </div>

    <!-- Đã đăng nhập: dùng hồ sơ tài khoản (nhập ngày sinh 1 lần ở tab Hồ sơ). -->
    <ActivePersonBar v-if="isAuthenticated" />
    <template v-else>
      <div class="profile-toolbar profile-form">
        <label class="profile-picker">
          <span>Hồ sơ</span>
          <select :value="activeProfileId" @change="onProfileSelect">
            <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.label }}</option>
          </select>
        </label>
        <button class="outline-button profile-new" type="button" @click="createProfile">
          <UserPlus :size="16" />
          <span>Tạo hồ sơ mới</span>
        </button>
      </div>
      <p class="profile-hint">Đang làm việc dưới hồ sơ đã chọn — lưu trên máy (localStorage), không cần đăng nhập.</p>
    </template>

    <form class="profile-form" @submit.prevent="submit">
      <label v-if="!isAuthenticated">
        <span>Tên hiển thị</span>
        <input v-model="form.profile_label" type="text" placeholder="Ví dụ: Lại Minh Thắng" />
      </label>
      <!-- Ngày sinh: đã đăng nhập → tự lấy từ hồ sơ (thanh trên), không nhập lại. -->
      <label v-if="!isAuthenticated">
        <span>Ngày giờ sinh</span>
        <input v-model="form.birth_datetime_local" type="datetime-local" />
      </label>
      <label>
        <span>Múi giờ</span>
        <input v-model="form.timezone" type="text" />
      </label>
      <div class="form-row">
        <label>
          <span>Nơi sinh</span>
          <input v-model="form.location_ref" type="text" />
        </label>
        <label>
          <span>Độ chính xác</span>
          <select v-model="form.birth_precision">
            <option value="exact">Chính xác</option>
            <option value="approx">Ước lượng</option>
            <option value="unknown">Không rõ</option>
          </select>
        </label>
      </div>
      <button class="primary-button" type="submit">
        <Send :size="16" />
        <span>Tính điểm cộng hưởng</span>
      </button>
    </form>

    <div v-if="personal" class="resonance-result">
      <div class="sync-score">
        <span>Điểm</span>
        <strong>{{ Math.round(personal.sync_score * 100) }}</strong>
      </div>
      <div class="element-strip">
        <span v-for="(value, key) in personal.personal_vector.five_element_bias" :key="key">
          {{ key }} {{ Math.round(value * 100) }}
        </span>
      </div>
    </div>

    <p v-if="localError" class="status-message error">{{ localError }}</p>

    <div class="calendar-tool">
      <div class="panel-title">
        <span>Chuyển đổi lịch âm / dương</span>
        <small>hỗ trợ nhập liệu sinh</small>
      </div>
      <div class="profile-form">
        <label>
          <span>Ngày giờ</span>
          <input v-model="calendarForm.datetime_local" type="datetime-local" />
        </label>
        <div class="form-row">
          <label>
            <span>Nguồn</span>
            <select v-model="calendarForm.source_calendar">
              <option value="solar">Dương lịch</option>
              <option value="lunar">Âm lịch</option>
            </select>
          </label>
          <label>
            <span>Múi giờ</span>
            <input v-model="calendarForm.timezone" type="text" />
          </label>
        </div>
        <label v-if="calendarForm.source_calendar === 'lunar'" class="checkbox-row">
          <input v-model="calendarForm.is_leap_month" type="checkbox" />
          <span>Tháng nhuận</span>
        </label>
        <button class="primary-button" type="button" @click="runCalendarConvert">Chuyển đổi</button>
      </div>
      <p v-if="calendarResult" class="calendar-result">
        {{ calendarResult.source_calendar.toUpperCase() }} ->
        {{ calendarResult.target_calendar.toUpperCase() }}:
        <strong>{{ calendarResult.converted_datetime_local }}</strong>
      </p>
    </div>

    <div class="calendar-tool">
      <div class="panel-title">
        <span>So sánh cơ bản + báo cáo</span>
        <small>chưa tuyệt đối</small>
      </div>
      <button class="primary-button" type="button" @click="runCompareBasic">Chạy so sánh cơ bản</button>
      <div v-if="compareResult" class="compare-result">
        <p><strong>Confidence:</strong> {{ Math.round(compareResult.confidence * 100) }}%</p>
        <ul>
          <li v-for="row in compareResult.checks" :key="row.id">
            [{{ row.status }}] {{ row.label }} - {{ row.detail }}
          </li>
        </ul>
        <textarea :value="compareResult.report_markdown" rows="7" readonly />
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}
.profile-picker {
  flex: 1 1 12rem;
  min-width: 10rem;
}
.profile-new {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}
.profile-hint {
  font-size: 0.78rem;
  opacity: 0.75;
  margin: 0 0 0.85rem;
  line-height: 1.35;
}
.outline-button {
  border: 1px solid color-mix(in srgb, var(--border, #ccc) 80%, transparent);
  background: transparent;
  color: inherit;
  border-radius: 8px;
  padding: 0.45rem 0.65rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.outline-button:hover {
  border-color: var(--accent, #6366f1);
  background: color-mix(in srgb, var(--accent, #6366f1) 8%, transparent);
}
</style>
