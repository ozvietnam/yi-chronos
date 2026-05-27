<script setup>
/**
 * DailyHexagramPanel — 1 quẻ/ngày (morning brief).
 *
 * Paradigm: cùng ngày = cùng quẻ. User "ngấm" 1 quẻ mỗi sáng.
 * KHÔNG predict tốt/xấu — chỉ "quan vật khoảnh khắc của ngày".
 */
import { ref, computed, onMounted, watch } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";

const dateInput = ref(new Date().toISOString().slice(0, 10));
const data = ref(null);
const loading = ref(false);
const error = ref("");

async function loadDaily(date) {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch(`/api/yi-wiki/kinh-dich/daily?date=${encodeURIComponent(date)}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    data.value = await r.json();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

function isToday() {
  return dateInput.value === new Date().toISOString().slice(0, 10);
}

function shiftDate(delta) {
  const d = new Date(dateInput.value);
  d.setDate(d.getDate() + delta);
  dateInput.value = d.toISOString().slice(0, 10);
}

function goToday() {
  dateInput.value = new Date().toISOString().slice(0, 10);
}

// Minimal markdown render for excerpt
function renderMd(md) {
  if (!md) return "";
  return md
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .split("\n").map(ln => {
      const s = ln.trim();
      if (s.startsWith("&gt; _") && s.endsWith("_")) {
        return `<blockquote class="italic">${s.slice(6, -1)}</blockquote>`;
      }
      if (s.startsWith("&gt; ")) {
        return `<blockquote class="han">${s.slice(5)}</blockquote>`;
      }
      return `<p>${s
        .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
        .replace(/_([^_]+)_/g, "<i>$1</i>")
      }</p>`;
    }).join("");
}

watch(dateInput, (v) => loadDaily(v));
onMounted(() => loadDaily(dateInput.value));
</script>

<template>
  <div class="dhp">
    <header class="dhp-head">
      <h3>☀️ Quẻ hôm nay</h3>
      <div class="dhp-nav">
        <button @click="shiftDate(-1)" title="Hôm qua">←</button>
        <input type="date" v-model="dateInput" />
        <button @click="shiftDate(1)" title="Ngày mai">→</button>
        <button v-if="!isToday()" @click="goToday" class="btn-today">Hôm nay</button>
      </div>
    </header>

    <div v-if="loading" class="dhp-status">Đang đọc quẻ ngày {{ dateInput }}...</div>
    <div v-if="error" class="dhp-error">Lỗi: {{ error }}</div>

    <div v-if="data && !loading" class="dhp-card">
      <div class="dhp-svg">
        <HexagramSvg :upper="data.upper" :lower="data.lower" :size="120" />
      </div>
      <div class="dhp-info">
        <div class="dhp-title">
          <span class="num">#{{ data.number }}</span>
          <span class="name">{{ data.name_vi }}</span>
          <span class="zh">{{ data.name_zh }}</span>
          <span class="unicode">{{ data.structure_unicode }}</span>
        </div>
        <div class="dhp-struct">{{ data.upper }} trên / {{ data.lower }} dưới</div>
        <div class="dhp-desc">{{ data.description }}</div>
        <article class="dhp-excerpt" v-html="renderMd(data.daily_excerpt)"></article>
        <div class="dhp-rkeys" v-if="data.routing_keys?.length">
          <span class="rkey-label">Tâm pháp:</span>
          <code v-for="k in data.routing_keys.slice(0, 5)" :key="k">{{ k }}</code>
        </div>
      </div>
    </div>

    <p class="dhp-foot">
      ⚠️ Paradigm: <i>cùng ngày = cùng quẻ</i>. Đây không phải predict cát/hung — chỉ là "quan vật" khoảnh khắc của ngày.
    </p>
  </div>
</template>

<style scoped>
.dhp {
  background: linear-gradient(135deg, rgba(252, 211, 77, 0.05), rgba(167, 139, 250, 0.05));
  border: 1px solid rgba(252, 211, 77, 0.25);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  margin: 0.5rem 0;
}
.dhp-head {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 0.5rem;
}
.dhp-head h3 { margin: 0; color: #fcd34d; font-size: 1rem; }
.dhp-nav {
  display: flex; gap: 0.3rem; align-items: center; font-size: 0.85rem;
}
.dhp-nav button {
  background: rgba(252, 211, 77, 0.18); border: 1px solid rgba(252, 211, 77, 0.4);
  color: #fcd34d; padding: 0.2rem 0.55rem; border-radius: 4px; cursor: pointer;
  font-size: 0.85rem;
}
.dhp-nav button:hover { background: rgba(252, 211, 77, 0.3); }
.btn-today { background: rgba(252, 211, 77, 0.3) !important; }
.dhp-nav input[type="date"] {
  background: #1e1b4b; color: #e0e7ff; border: 1px solid rgba(196, 181, 253, 0.3);
  border-radius: 4px; padding: 0.15rem 0.35rem; font-size: 0.85rem;
}
.dhp-status, .dhp-error {
  padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.9rem;
}
.dhp-error { color: #f87171; }
.dhp-card {
  display: flex; gap: 1rem; margin-top: 0.6rem;
  background: rgba(15, 23, 42, 0.4); padding: 0.8rem; border-radius: 6px;
}
.dhp-svg { flex-shrink: 0; }
.dhp-info { flex: 1; min-width: 0; }
.dhp-title {
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
  font-weight: 600;
}
.dhp-title .num { color: #fcd34d; font-size: 0.9rem; }
.dhp-title .name { color: #fbbf24; font-size: 1.2rem; }
.dhp-title .zh { color: #e0e7ff; font-size: 1rem; }
.dhp-title .unicode { font-size: 1.4rem; color: #c4b5fd; }
.dhp-struct {
  font-size: 0.78rem; color: #94a3b8; margin: 0.2rem 0;
}
.dhp-desc {
  font-size: 0.85rem; color: #cbd5e1; margin: 0.4rem 0; line-height: 1.5;
}
.dhp-excerpt { margin-top: 0.5rem; }
.dhp-excerpt :deep(p) {
  color: #e2e8f0; line-height: 1.55; margin: 0.3rem 0; font-size: 0.88rem;
}
.dhp-excerpt :deep(blockquote) {
  background: rgba(252, 211, 77, 0.06);
  border-left: 2px solid rgba(252, 211, 77, 0.5);
  padding: 0.35rem 0.6rem; margin: 0.4rem 0; font-size: 0.88rem;
  color: #fef3c7;
}
.dhp-excerpt :deep(blockquote.italic) {
  font-style: italic; color: #fde68a;
}
.dhp-excerpt :deep(b) { color: #fcd34d; }
.dhp-rkeys { margin-top: 0.6rem; font-size: 0.78rem; }
.rkey-label { color: #94a3b8; margin-right: 0.4rem; }
.dhp-rkeys code {
  background: rgba(167, 139, 250, 0.18); color: #c4b5fd;
  padding: 0.05rem 0.4rem; border-radius: 3px; margin-right: 0.3rem;
  font-size: 0.72rem;
}
.dhp-foot {
  margin-top: 0.6rem; font-size: 0.75rem; color: #6b7280; font-style: italic;
}

/* Mobile */
@media (max-width: 600px) {
  .dhp-card { flex-direction: column; align-items: center; }
}
</style>
