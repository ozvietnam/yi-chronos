<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import SchoolIcon from "./SchoolIcon.vue";
import { ChevronDown } from "lucide-vue-next";

const props = defineProps({
  group: { type: Object, required: true }, // { label, tabs: [{id, icon, label}] }
  active: { type: String, default: "" }
});
const emit = defineEmits(["select"]);

const open = ref(false);
const root = ref(null);

// tab đang active có nằm trong nhóm này không → hiện tên tab đó trên nút (user thấy mình ở đâu)
const activeTab = computed(() => props.group.tabs.find((t) => t.id === props.active) || null);

function toggle() { open.value = !open.value; }
function select(id) { emit("select", id); open.value = false; }
function onDocClick(e) { if (root.value && !root.value.contains(e.target)) open.value = false; }
function onEsc(e) { if (e.key === "Escape") open.value = false; }

onMounted(() => { document.addEventListener("click", onDocClick); document.addEventListener("keydown", onEsc); });
onBeforeUnmount(() => { document.removeEventListener("click", onDocClick); document.removeEventListener("keydown", onEsc); });
</script>

<template>
  <div class="nav-dd" ref="root">
    <button
      type="button"
      class="nav-dd-trigger"
      :class="{ active: !!activeTab, open }"
      @click.stop="toggle"
      :aria-expanded="open"
      :title="group.label"
    >
      <SchoolIcon v-if="activeTab" :name="activeTab.icon" :size="15" />
      <span class="nav-dd-text">{{ activeTab ? activeTab.label : group.label }}</span>
      <ChevronDown :size="14" class="nav-dd-caret" :class="{ flip: open }" />
    </button>

    <div v-show="open" class="nav-dd-menu" role="menu">
      <div class="nav-dd-grouplabel">{{ group.label }}</div>
      <button
        v-for="t in group.tabs"
        :key="t.id"
        type="button"
        class="nav-dd-item"
        :class="{ active: t.id === active }"
        @click.stop="select(t.id)"
        role="menuitem"
      >
        <SchoolIcon :name="t.icon" :size="15" />
        <span>{{ t.label }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.nav-dd { position: relative; display: inline-flex; }

.nav-dd-trigger {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 6px 10px 6px 11px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.nav-dd-trigger:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-primary); }
.nav-dd-trigger.active {
  background: rgba(232, 201, 90, 0.16);
  color: var(--accent-gold);
  border-color: var(--border-accent);
}
.nav-dd-trigger.open { background: rgba(255, 255, 255, 0.07); color: var(--text-primary); }
.nav-dd-caret { opacity: 0.6; transition: transform 0.18s; flex: 0 0 auto; }
.nav-dd-caret.flip { transform: rotate(180deg); }

.nav-dd-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 60;
  min-width: 184px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px;
  border-radius: 10px;
  border: 1px solid var(--border-soft);
  background: var(--bg-card-solid, #141e28);
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.42);
  backdrop-filter: blur(12px);
}
.nav-dd-grouplabel {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  font-weight: 700;
  color: var(--text-muted);
  padding: 4px 8px 5px;
  user-select: none;
}
.nav-dd-item {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  text-align: left;
  border: 1px solid transparent;
  border-radius: 7px;
  padding: 7px 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.nav-dd-item:hover { background: rgba(255, 255, 255, 0.06); color: var(--text-primary); }
.nav-dd-item.active {
  background: rgba(232, 201, 90, 0.16);
  color: var(--accent-gold);
  border-color: var(--border-accent);
}
</style>
