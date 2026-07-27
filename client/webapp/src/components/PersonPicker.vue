<script setup>
/**
 * PersonPicker — chọn MỘT NGƯỜI từ hồ sơ đã lưu (Anh chốt 2026-07-18: panel đa người
 * lấy người thứ 2/3 từ profile, KHÔNG gõ tay ngày sinh nữa).
 *
 * v-model = birth_datetime_local đã chọn (chuỗi). @picked nhả cả person {name,gender,...}
 * để panel set thêm tên/giới. mode="date" → nhả YYYY-MM-DD; mặc định datetime YYYY-MM-DDTHH:mm.
 */
import { computed } from "vue";
import { persons, activePersonKey, personLabel } from "../stores/userDataStore.js";

const props = defineProps({
  modelValue: { type: String, default: "" },
  label: { type: String, default: "Chọn người" },
  mode: { type: String, default: "datetime" }, // "datetime" | "date"
  excludeSelf: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue", "picked"]);

const list = computed(() =>
  (persons.value || []).filter(
    (p) => !props.excludeSelf || (p.person_key || p.person_id) !== activePersonKey.value,
  ),
);

// Suy ngược person đang chọn từ birth hiện có (để giữ <select> đúng khi mở lại).
const selectedKey = computed(() => {
  const cur = (props.modelValue || "").slice(0, 10);
  if (!cur) return "";
  const p = (persons.value || []).find(
    (pp) => (pp.birth_datetime_local || "").slice(0, 10) === cur,
  );
  return p ? (p.person_key || p.person_id) : "";
});

function onPick(e) {
  const key = e.target.value;
  const p = (persons.value || []).find((pp) => (pp.person_key || pp.person_id) === key);
  if (!p) { emit("update:modelValue", ""); return; }
  const bd = p.birth_datetime_local || "";
  emit("update:modelValue", props.mode === "date" ? bd.slice(0, 10) : bd.slice(0, 16));
  emit("picked", p);
}
function goProfiles() { window.dispatchEvent(new CustomEvent("yi-nav-tab", { detail: "profiles" })); }
</script>

<template>
  <div class="pp">
    <select class="pp-sel" :value="selectedKey" @change="onPick" :aria-label="label">
      <option value="">— {{ label }} —</option>
      <option v-for="p in list" :key="p.person_key || p.person_id" :value="p.person_key || p.person_id">
        {{ personLabel(p) }}<template v-if="p.birth_datetime_local"> · {{ p.birth_datetime_local.slice(0, 10) }}</template>
      </option>
    </select>
    <button type="button" class="pp-add" @click="goProfiles" title="Thêm người ở tab Hồ sơ">＋ Hồ sơ</button>
  </div>
</template>

<style scoped>
.pp { display: inline-flex; align-items: center; gap: 6px; }
.pp-sel {
  padding: 4px 9px; border-radius: 7px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.25));
  background: var(--read-bg, transparent); color: var(--read-text, inherit);
  font-size: calc(13px * var(--reading-scale, 1)); max-width: 100%;
}
.pp-add {
  background: none; border: none; cursor: pointer; padding: 2px 4px;
  color: var(--read-accent, #7ec8e3); font-size: 0.85em; text-decoration: underline; white-space: nowrap;
}
</style>
