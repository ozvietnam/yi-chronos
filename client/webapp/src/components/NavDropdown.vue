<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import SchoolIcon from "./SchoolIcon.vue";
import { ChevronDown } from "lucide-vue-next";

const props = defineProps({
  group: { type: Object, required: true }, // { label, tabs: [{id, icon, label}] }
  active: { type: String, default: "" }
});
const emit = defineEmits(["select"]);

const open = ref(false);
const root = ref(null);     // .nav-dd (chứa nút trigger, ở nguyên vị trí)
const menuRef = ref(null);  // menu đã teleport ra <body>
const menuStyle = ref({});

// tab đang active có nằm trong nhóm này không → hiện tên tab đó trên nút
const activeTab = computed(() => props.group.tabs.find((t) => t.id === props.active) || null);

// Đặt menu (position:fixed) ngay dưới nút — tính từ rect nút vì menu đã ở body.
function position() {
  const trg = root.value && root.value.querySelector(".nav-dd-trigger");
  if (!trg) return;
  const r = trg.getBoundingClientRect();
  // né tràn phải mép màn
  const left = Math.min(Math.round(r.left), window.innerWidth - 200);
  menuStyle.value = { top: `${Math.round(r.bottom + 6)}px`, left: `${Math.max(8, left)}px` };
}

async function toggle() {
  if (open.value) { open.value = false; return; }
  open.value = true;
  await nextTick();
  position();
}
function select(id) { emit("select", id); open.value = false; }
function close() { open.value = false; }

// click ngoài CẢ nút LẪN menu (menu ở body nên phải check riêng) → đóng
function onDocClick(e) {
  if (!open.value) return;
  if (root.value && root.value.contains(e.target)) return;
  if (menuRef.value && menuRef.value.contains(e.target)) return;
  open.value = false;
}
function onEsc(e) { if (e.key === "Escape") open.value = false; }

onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onEsc);
  window.addEventListener("scroll", close, true);
  window.addEventListener("resize", close);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onEsc);
  window.removeEventListener("scroll", close, true);
  window.removeEventListener("resize", close);
});
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

    <!-- Teleport ra body: thoát stacking context của .main-tabs (backdrop-filter),
         menu luôn nổi trên content (z-index 900), dưới modal (950+). -->
    <Teleport to="body">
      <div v-show="open" ref="menuRef" class="nav-dd-menu" :style="menuStyle" role="menu">
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
    </Teleport>
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

/* menu đã teleport ra body → position: fixed, toạ độ set inline theo nút */
.nav-dd-menu {
  position: fixed;
  z-index: 900;
  min-width: 188px;
  max-height: min(70vh, 520px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px;
  border-radius: 10px;
  border: 1px solid var(--border-soft);
  background: var(--bg-card-solid, #141e28);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
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
