<script setup>
/**
 * ActivePersonBar — thanh "Đang xem [tên] · Đổi người" cho mọi panel phân tích.
 *
 * Anh chốt 2026-07-18: ngày sinh NHẬP 1 LẦN DUY NHẤT ở quản lý tài khoản (tab Hồ sơ);
 * panel phân tích KHÔNG còn ô gõ ngày sinh — chỉ hiện người đang xem + đổi profile.
 * Đọc từ MỘT NGUỒN: userDataStore.activePerson. Đổi người = setActivePerson (mọi panel theo).
 */
import { computed } from "vue";
import { persons, activePerson, activePersonKey, setActivePerson } from "../stores/userDataStore.js";

const hasPerson = computed(() => !!activePerson.value);
const list = computed(() => persons.value || []);

function fmtBirth(bd) {
  if (!bd) return "—";
  const [d, t] = String(bd).split("T");
  const [y, m, day] = (d || "").split("-");
  if (!y) return bd;
  return `${day}/${m}/${y}${t ? " " + t.slice(0, 5) : ""}`;
}
function onSwitch(e) { setActivePerson(e.target.value); }
function goProfiles() { window.dispatchEvent(new CustomEvent("yi-nav-tab", { detail: "profiles" })); }
</script>

<template>
  <div class="apb">
    <template v-if="hasPerson">
      <span class="apb-ic">👤</span>
      <span class="apb-name">{{ activePerson.name || activePerson.person_id || "Hồ sơ" }}</span>
      <span class="apb-meta">
        sinh {{ fmtBirth(activePerson.birth_datetime_local) }} <em>dương</em>
        <template v-if="activePerson.gender"> · {{ activePerson.gender }}</template>
      </span>
      <select
        v-if="list.length > 1"
        class="apb-switch"
        :value="activePersonKey"
        aria-label="Đổi người xem"
        @change="onSwitch"
      >
        <option v-for="p in list" :key="p.person_key || p.person_id" :value="p.person_key || p.person_id">
          {{ p.name || p.person_id }}
        </option>
      </select>
      <button type="button" class="apb-link" @click="goProfiles" title="Thêm / sửa hồ sơ ở tab Hồ sơ">
        {{ list.length > 1 ? "＋ Hồ sơ" : "Đổi người" }}
      </button>
    </template>
    <template v-else>
      <span class="apb-ic">👤</span>
      <span class="apb-name">Chưa có hồ sơ</span>
      <button type="button" class="apb-link" @click="goProfiles">＋ Nhập ngày sinh ở tab Hồ sơ</button>
    </template>
  </div>
</template>

<style scoped>
.apb {
  display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px;
  padding: 8px 12px; margin-bottom: 12px; border-radius: 10px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.18));
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.5;
}
.apb-ic { font-size: 1.05em; }
.apb-name { font-weight: 600; color: var(--read-text, rgba(230, 238, 245, 0.95)); }
.apb-meta { color: var(--read-text-faint, rgba(230, 238, 245, 0.6)); font-size: 0.9em; }
.apb-meta em { font-style: normal; opacity: 0.75; }
.apb-switch {
  margin-left: auto; padding: 3px 8px; border-radius: 7px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.25));
  background: var(--read-bg, transparent); color: var(--read-text, inherit);
  font-size: 0.9em;
}
.apb-link {
  background: none; border: none; cursor: pointer; padding: 2px 4px;
  color: var(--read-accent, #7ec8e3); font-size: 0.9em; text-decoration: underline;
}
.apb-switch + .apb-link { margin-left: 0; }
.apb-switch { }
</style>
