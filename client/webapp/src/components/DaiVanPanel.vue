<script setup>
/**
 * DaiVanPanel — hiển thị 12 Đại Vận lá số anh với annotations từ DeepSeek.
 *
 * Source: /api/yi-publishing/dai-van/founder
 * Mỗi đại vận = 10 năm, có cung tọa + sao + cơ hội / thách thức / lời khuyên.
 */
import { ref, onMounted, computed, watch } from "vue";
import WikiText from "./WikiText.vue";
import { tuviPersonKey, tuviPersonName, fetchCachedAnalysis, runAnalysis } from "../stores/tuviPersonStore.js";

const data = ref(null);
const loading = ref(false);
const running = ref(false);
const error = ref("");
const expanded = ref({});

async function load() {
  loading.value = true; error.value = "";
  data.value = null;
  try {
    const d = await fetchCachedAnalysis(tuviPersonKey.value, "dai_van");
    if (d.status === "ok") {
      data.value = d;
      const cur = d.annotations?.find(a => a.is_current);
      if (cur) expanded.value[cur.cycle_index] = true;
    } else if (d.status === "not_cached") {
      error.value = `Chưa có phân tích Đại Vận cho ${tuviPersonName.value}. Nhấn "Phân tích ngay" để chạy (~15s, ~$0.008).`;
    } else { error.value = d.message || "Lỗi tải dữ liệu"; }
  } catch (e) { error.value = e.message; }
  finally { loading.value = false; }
}

async function runNow() {
  if (running.value) return;
  running.value = true; error.value = "";
  try {
    const d = await runAnalysis(tuviPersonKey.value, "dai_van");
    if (d.status === "ok") {
      data.value = d;
      const cur = d.annotations?.find(a => a.is_current);
      if (cur) expanded.value[cur.cycle_index] = true;
    } else { error.value = d.message || "Lỗi chạy phân tích"; }
  } catch (e) { error.value = e.message; }
  finally { running.value = false; }
}

watch(tuviPersonKey, () => load());

const annotations = computed(() => data.value?.annotations || []);

function palaceIcon(palace) {
  return {
    "Mệnh": "🎯", "Phụ Mẫu": "👴", "Phúc Đức": "✨", "Điền Trạch": "🏛",
    "Quan Lộc": "💼", "Nô Bộc": "🤝", "Thiên Di": "🚀", "Tật Ách": "🩺",
    "Tài Bạch": "💰", "Tử Tức": "🧒", "Phu Thê": "💍", "Huynh Đệ": "👫",
  }[palace] || "•";
}

onMounted(load);
</script>

<template>
  <div class="dv-wrap">
    <header class="dv-head">
      <div>
        <h2>🌗 12 Đại Vận — {{ tuviPersonName }}</h2>
        <p>
          Mỗi đại vận = 10 năm. Mệnh tọa sao tại cung khác → tính chất khác.
          <br/><small v-if="data">Sinh: {{ data.birth || data.anh_birth }} · Hiện {{ data.current_age }} tuổi ({{ data.current_year }})</small>
        </p>
      </div>
      <button class="dv-refresh" @click="load" :disabled="loading">{{ loading ? "⏳" : "🔄" }}</button>
    </header>

    <div v-if="loading" class="dv-loading">Đang tải...</div>
    <div v-if="error" class="dv-error">
      <p>{{ error }}</p>
      <button v-if="!data && !running" class="dv-run-btn" @click="runNow">⚡ Phân tích ngay</button>
      <p v-if="running" class="dv-running">⏳ Đang chạy 12 đại vận qua DeepSeek (~15s)...</p>
    </div>

    <div v-if="annotations.length" class="dv-timeline">
      <div v-for="a in annotations" :key="a.cycle_index"
           class="dv-card"
           :class="{ 'is-current': a.is_current, 'is-expanded': expanded[a.cycle_index] }">
        <div class="dv-head-row" @click="expanded[a.cycle_index] = !expanded[a.cycle_index]">
          <div class="dv-left">
            <span class="dv-num">V{{ a.cycle_index }}</span>
            <div class="dv-age-range">
              <strong>tuổi {{ a.start_age }}-{{ a.end_age }}</strong>
              <small>{{ a.start_year }}–{{ a.end_year }}</small>
            </div>
          </div>
          <div class="dv-mid">
            <span class="dv-branch">{{ a.branch }}</span>
            <span class="dv-palace">{{ palaceIcon(a.palace) }} {{ a.palace }}</span>
          </div>
          <div class="dv-right">
            <div class="dv-stars">
              <span v-for="s in a.stars" :key="s" class="dv-star">{{ s }}</span>
              <span v-if="!a.stars?.length" class="dv-empty-star">(vô chính tinh)</span>
            </div>
            <span v-if="a.is_current" class="dv-current-tag">⭐ ĐANG TRẢI QUA</span>
          </div>
          <span class="dv-toggle">{{ expanded[a.cycle_index] ? '▾' : '▸' }}</span>
        </div>

        <div v-if="expanded[a.cycle_index]" class="dv-body">
          <p class="dv-tong-quan">
            <b>📖 Tổng quan:</b> <WikiText :text="a.tong_quan" />
          </p>
          <div class="dv-grid">
            <div class="dv-block dv-co-hoi">
              <h5>✨ Cơ hội</h5>
              <ul><li v-for="(c, i) in a.co_hoi" :key="i"><WikiText :text="c" /></li></ul>
            </div>
            <div class="dv-block dv-thach-thuc">
              <h5>⚠️ Thách thức</h5>
              <ul><li v-for="(c, i) in a.thach_thuc" :key="i"><WikiText :text="c" /></li></ul>
            </div>
          </div>
          <p class="dv-loi-khuyen">
            <b>💡 Lời khuyên:</b> <WikiText :text="a.loi_khuyen" />
          </p>
        </div>
      </div>
    </div>

    <footer v-if="data" class="dv-foot">
      <small>
        Generated {{ new Date(data.generated_at * 1000).toLocaleString('vi') }} ·
        Cost ${{ data.cost_usd?.toFixed(4) }}
      </small>
    </footer>
  </div>
</template>

<style scoped>
.dv-wrap {
  padding: 1rem 1.5rem; max-width: 980px; margin: 0 auto;
  color: #e2e8f0; font-family: "Charter", "Iowan Old Style", Georgia, serif;
}
.dv-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  border-bottom: 1px solid #334155; padding-bottom: 0.7rem; margin-bottom: 1rem;
}
.dv-head h2 { margin: 0 0 0.2rem 0; color: #fde68a; font-size: 1.3rem; }
.dv-head p { margin: 0; font-size: 0.85rem; color: #94a3b8; line-height: 1.5; }
.dv-head small { color: #64748b; font-size: 0.72rem; }
.dv-refresh {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}

.dv-loading { text-align: center; padding: 2rem; color: #94a3b8; }
.dv-error { color: #fca5a5; padding: 0.6rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.dv-run-btn {
  margin-top: 0.4rem; background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white; border: none; padding: 0.45rem 0.9rem; border-radius: 4px;
  font-size: 0.85rem; cursor: pointer; font-weight: 600;
}
.dv-run-btn:hover { background: linear-gradient(135deg, #b45309, #d97706); }
.dv-running { color: #fde68a; font-size: 0.85rem; margin-top: 0.4rem; }

.dv-timeline { display: flex; flex-direction: column; gap: 0.5rem; }

.dv-card {
  background: #1e293b; border: 1px solid #334155; border-radius: 6px;
  overflow: hidden; transition: all 0.15s;
}
.dv-card:hover { border-color: #475569; }
.dv-card.is-current {
  border-color: #fde68a;
  background: linear-gradient(135deg, rgba(253,230,138,0.08), rgba(253,230,138,0.02));
}
.dv-card.is-expanded { border-color: #60a5fa; }

.dv-head-row {
  display: grid;
  grid-template-columns: auto 1fr 2fr auto;
  gap: 0.8rem; align-items: center;
  padding: 0.6rem 0.9rem;
  cursor: pointer;
}

.dv-left { display: flex; align-items: center; gap: 0.5rem; }
.dv-num {
  background: #4a1a1a; color: #fde68a;
  width: 32px; height: 32px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700;
}
.dv-card.is-current .dv-num {
  background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff;
}
.dv-age-range { display: flex; flex-direction: column; line-height: 1.2; }
.dv-age-range strong { color: #f1f5f9; font-size: 0.9rem; }
.dv-age-range small { color: #64748b; font-size: 0.72rem; }

.dv-mid { display: flex; align-items: center; gap: 0.4rem; }
.dv-branch {
  background: #0f172a; border: 1px solid #475569;
  padding: 2px 8px; border-radius: 3px;
  color: #fde68a; font-weight: 600; font-size: 0.85rem;
}
.dv-palace { font-size: 0.8rem; color: #94a3b8; }

.dv-right {
  display: flex; flex-direction: column; gap: 0.25rem; align-items: flex-end;
}
.dv-stars { display: flex; flex-wrap: wrap; gap: 0.25rem; justify-content: flex-end; }
.dv-star {
  background: rgba(34,197,94,0.15); color: #86efac;
  padding: 1px 6px; border-radius: 3px; font-size: 0.72rem;
  font-family: ui-sans-serif, sans-serif;
}
.dv-empty-star { color: #64748b; font-size: 0.75rem; font-style: italic; }
.dv-current-tag {
  background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff;
  padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; font-weight: 600;
}

.dv-toggle { color: #94a3b8; font-size: 0.85rem; padding: 0 0.3rem; }

.dv-body {
  padding: 0.8rem 0.9rem 1rem; border-top: 1px solid #1e293b;
  background: rgba(0,0,0,0.15);
}
.dv-tong-quan {
  margin: 0 0 0.7rem 0; font-size: 0.9rem; line-height: 1.6; color: #cbd5e1;
}
.dv-tong-quan b { color: #fde68a; }

.dv-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; margin-bottom: 0.7rem;
}
.dv-block {
  border-radius: 4px; padding: 0.55rem 0.7rem;
}
.dv-block h5 {
  margin: 0 0 0.4rem 0; font-size: 0.85rem;
}
.dv-block ul {
  margin: 0; padding-left: 1.1rem;
}
.dv-block ul li {
  margin: 0.2rem 0; font-size: 0.83rem; line-height: 1.5; color: #cbd5e1;
}
.dv-co-hoi {
  background: rgba(16, 185, 129, 0.08);
  border-left: 3px solid #10b981;
}
.dv-co-hoi h5 { color: #34d399; }
.dv-thach-thuc {
  background: rgba(239, 68, 68, 0.08);
  border-left: 3px solid #f59e0b;
}
.dv-thach-thuc h5 { color: #fbbf24; }

.dv-loi-khuyen {
  margin: 0; padding: 0.55rem 0.7rem;
  background: rgba(59,130,246,0.08); border-left: 3px solid #60a5fa;
  border-radius: 4px;
  font-size: 0.88rem; line-height: 1.6; color: #cbd5e1;
}
.dv-loi-khuyen b { color: #60a5fa; }

.dv-foot {
  margin-top: 1rem; padding-top: 0.6rem;
  border-top: 1px dashed #475569; text-align: center;
}
.dv-foot small { color: #64748b; font-size: 0.72rem; }

@media (max-width: 700px) {
  .dv-head-row { grid-template-columns: auto 1fr; }
  .dv-mid, .dv-right { grid-column: 1 / -1; justify-content: flex-start; align-items: flex-start; }
  .dv-grid { grid-template-columns: 1fr; }
}
</style>
