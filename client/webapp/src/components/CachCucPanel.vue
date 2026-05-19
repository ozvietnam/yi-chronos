<script setup>
/**
 * CachCucPanel — hiển thị các cách cục phát hiện trong lá số anh
 * + synastry với vợ.
 *
 * Source: /api/yi-publishing/anh-deep-analysis (DeepSeek generated)
 */
import { ref, onMounted, watch } from "vue";
import WikiText from "./WikiText.vue";
import { tuviPersonKey, tuviPersonName, fetchCachedAnalysis, runAnalysis } from "../stores/tuviPersonStore.js";

const data = ref(null);
const loading = ref(false);
const running = ref(false);
const error = ref("");
const expanded = ref({});
const activeTab = ref("cach_cuc"); // 'cach_cuc' | 'synastry'

async function load() {
  loading.value = true;
  error.value = "";
  data.value = null;
  try {
    const pk = tuviPersonKey.value;
    // Try deep_analysis first (founder format with synastry), fall back to cach_cuc
    let d = await fetchCachedAnalysis(pk, "deep_analysis");
    if (d.status !== "ok") d = await fetchCachedAnalysis(pk, "cach_cuc");
    if (d.status === "ok") {
      data.value = d;
    } else if (d.status === "not_cached") {
      error.value = `Chưa có Cách Cục cho ${tuviPersonName.value}. Nhấn "Phân tích ngay" (~5s, ~$0.002).`;
    } else {
      error.value = d.message || "Lỗi tải data";
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function runNow() {
  if (running.value) return;
  running.value = true; error.value = "";
  try {
    const d = await runAnalysis(tuviPersonKey.value, "cach_cuc");
    if (d.status === "ok") { data.value = d; }
    else { error.value = d.message || "Lỗi"; }
  } catch (e) { error.value = e.message; }
  finally { running.value = false; }
}

watch(tuviPersonKey, () => load());

function levelColor(level) {
  return {
    thượng: "#10b981",
    trung: "#fbbf24",
    hạ: "#fca5a5",
    "phá cách": "#ef4444",
  }[level] || "#94a3b8";
}

function levelIcon(level) {
  return {
    thượng: "⭐",
    trung: "🔆",
    hạ: "⚠️",
    "phá cách": "🚨",
  }[level] || "•";
}

onMounted(load);
</script>

<template>
  <div class="ccp-wrap">
    <header class="ccp-head">
      <div>
        <h2>🪐 Cách cục — {{ tuviPersonName }}</h2>
        <p>Phân tích cách cục phát hiện trong lá số + đối chiếu vợ chồng.<br/>
           <small>Nguồn: Tử Vi Đẩu Số Toàn Thư · DeepSeek đọc sâu cá nhân hóa</small></p>
      </div>
      <button class="ccp-refresh" @click="load" :disabled="loading">
        {{ loading ? "⏳" : "🔄" }}
      </button>
    </header>

    <div class="ccp-tabs">
      <button :class="{ active: activeTab === 'cach_cuc' }" @click="activeTab = 'cach_cuc'">
        🌌 Cách cục lá số ({{ data?.cach_cucs?.length || 0 }})
      </button>
      <button :class="{ active: activeTab === 'synastry' }" @click="activeTab = 'synastry'">
        💍 Đối chiếu vợ chồng
      </button>
    </div>

    <div v-if="loading" class="ccp-loading">Đang tải...</div>
    <div v-if="error" class="ccp-error">
      <p>{{ error }}</p>
      <button v-if="!data && !running" class="ccp-run-btn" @click="runNow">⚡ Phân tích ngay</button>
      <p v-if="running" class="ccp-running">⏳ DeepSeek đang tìm cách cục (~5s)...</p>
    </div>

    <!-- TAB 1: Cách cục -->
    <div v-if="activeTab === 'cach_cuc' && data?.cach_cucs" class="ccp-cach-cucs">
      <div v-for="(cc, idx) in data.cach_cucs" :key="idx" class="ccp-card">
        <div class="ccp-card-head" @click="expanded[idx] = !expanded[idx]">
          <div class="ccp-title">
            <span class="ccp-num">#{{ idx + 1 }}</span>
            <h3>{{ cc.ten }}</h3>
            <span class="ccp-level" :style="{ background: levelColor(cc.cap_do), color: '#fff' }">
              {{ levelIcon(cc.cap_do) }} {{ cc.cap_do || 'không rõ' }}
            </span>
          </div>
          <span class="ccp-toggle">{{ expanded[idx] ? '▾' : '▸' }}</span>
        </div>
        <div class="ccp-card-body">
          <p class="ccp-evidence">
            <b>📍 Bằng chứng:</b> <WikiText :text="cc.bang_chung" />
          </p>
          <p class="ccp-meaning" v-if="expanded[idx]">
            <b>📖 Ý nghĩa:</b> <WikiText :text="cc.y_nghia" />
          </p>
        </div>
      </div>
    </div>

    <!-- TAB 2: Synastry -->
    <div v-if="activeTab === 'synastry' && data?.synastry" class="ccp-synastry">
      <section class="ccp-syn-block">
        <h4>🌐 Hợp Mệnh Cục</h4>
        <p><WikiText :text="data.synastry.hop_menh_cuc" /></p>
      </section>

      <section class="ccp-syn-block">
        <h4>⚖️ Mệnh chủ tương tác</h4>
        <p><WikiText :text="data.synastry.menh_chu_tuong_tac" /></p>
      </section>

      <section class="ccp-syn-block">
        <h4>🏠 Cung Phu Thê anh ↔ Mệnh vợ</h4>
        <p><WikiText :text="data.synastry.phu_the_vs_menh_vo" /></p>
      </section>

      <section v-if="data.synastry.phu_the_vo_vs_menh_anh" class="ccp-syn-block">
        <h4>🏡 Cung Phu Thê vợ ↔ Mệnh anh</h4>
        <p><WikiText :text="data.synastry.phu_the_vo_vs_menh_anh" /></p>
      </section>

      <section v-if="data.synastry.than_chong_chap" class="ccp-syn-block ccp-special">
        <h4>👫 Thân ↔ Thân (chồng chập)</h4>
        <p><WikiText :text="data.synastry.than_chong_chap" /></p>
      </section>

      <section class="ccp-syn-block">
        <h4>🔄 Hóa Lộc/Kỵ chéo</h4>
        <p><WikiText :text="data.synastry.hoa_loc_ky_cheo" /></p>
      </section>

      <section v-if="data.synastry.tam_hop_luc_xung" class="ccp-syn-block">
        <h4>🔗 Tam hợp / Lục xung các cung</h4>
        <p><WikiText :text="data.synastry.tam_hop_luc_xung" /></p>
      </section>

      <section class="ccp-syn-block ccp-bright">
        <h4>✨ Điểm sáng</h4>
        <ul>
          <li v-for="(item, i) in data.synastry.diem_sang" :key="i"><WikiText :text="item" /></li>
        </ul>
      </section>

      <section class="ccp-syn-block ccp-warning">
        <h4>⚠️ Điểm cần chú ý</h4>
        <ul>
          <li v-for="(item, i) in data.synastry.diem_can_chu_y" :key="i"><WikiText :text="item" /></li>
        </ul>
      </section>

      <section class="ccp-syn-block ccp-apply">
        <h4>💡 Ứng dụng đời sống</h4>
        <p><WikiText :text="data.synastry.ung_dung_doi_song" /></p>
      </section>
    </div>

    <footer v-if="data" class="ccp-foot">
      <small>
        Generated: {{ new Date(data.generated_at * 1000).toLocaleString('vi') }} ·
        Cost: ${{ data.cost_usd?.toFixed(4) }} ·
        Anh sinh: {{ data.anh_birth }} · Vợ sinh: {{ data.wife_birth }}
      </small>
    </footer>
  </div>
</template>

<style scoped>
.ccp-wrap {
  padding: 1rem 1.5rem; max-width: 920px; margin: 0 auto;
  color: #e2e8f0; font-family: "Charter", "Iowan Old Style", Georgia, serif;
}
.ccp-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  border-bottom: 1px solid #334155; padding-bottom: 0.7rem; margin-bottom: 1rem;
}
.ccp-head h2 { margin: 0 0 0.2rem 0; color: #fde68a; font-size: 1.35rem; }
.ccp-head p { margin: 0; font-size: 0.85rem; color: #94a3b8; line-height: 1.5; }
.ccp-head small { color: #64748b; font-size: 0.72rem; }
.ccp-refresh {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem;
}
.ccp-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

.ccp-tabs { display: flex; gap: 0.4rem; margin-bottom: 1rem; }
.ccp-tabs button {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 0.5rem 0.95rem; border-radius: 4px 4px 0 0; cursor: pointer;
  font-size: 0.85rem; font-family: inherit;
  transition: all 0.15s;
}
.ccp-tabs button:hover { background: #283248; }
.ccp-tabs button.active {
  background: linear-gradient(135deg, #6d2727, #4a1a1a); color: #fde68a;
  border-color: #6d2727;
}

.ccp-loading { text-align: center; padding: 2rem; color: #94a3b8; }
.ccp-error { color: #fca5a5; padding: 0.6rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.ccp-run-btn {
  margin-top: 0.4rem; background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white; border: none; padding: 0.45rem 0.9rem; border-radius: 4px;
  font-size: 0.85rem; cursor: pointer; font-weight: 600;
}
.ccp-run-btn:hover { background: linear-gradient(135deg, #b45309, #d97706); }
.ccp-running { color: #fde68a; font-size: 0.85rem; margin-top: 0.4rem; }

/* Cards */
.ccp-card {
  background: #1e293b; border: 1px solid #334155; border-radius: 6px;
  margin-bottom: 0.7rem; overflow: hidden; transition: all 0.15s;
}
.ccp-card:hover { border-color: #475569; }
.ccp-card-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.7rem 0.9rem; cursor: pointer;
  background: linear-gradient(180deg, rgba(253,230,138,0.04), transparent);
}
.ccp-title { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.ccp-num {
  background: #4a1a1a; color: #fde68a;
  width: 24px; height: 24px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.78rem; font-weight: 700;
}
.ccp-title h3 {
  margin: 0; color: #fde68a; font-size: 1.05rem; font-weight: 600;
}
.ccp-level {
  font-size: 0.72rem; padding: 2px 8px; border-radius: 3px;
  font-weight: 600; font-family: ui-sans-serif, sans-serif;
}
.ccp-toggle { color: #94a3b8; font-size: 0.85rem; }
.ccp-card-body { padding: 0.7rem 0.9rem; border-top: 1px solid #1e293b; }
.ccp-evidence, .ccp-meaning {
  margin: 0; font-size: 0.88rem; line-height: 1.65; color: #cbd5e1;
}
.ccp-evidence { color: #94a3b8; font-style: italic; }
.ccp-evidence b { color: #cbd5e1; font-style: normal; }
.ccp-meaning { margin-top: 0.5rem; }
.ccp-meaning b { color: #fde68a; }

/* Synastry */
.ccp-synastry { display: flex; flex-direction: column; gap: 0.7rem; }
.ccp-syn-block {
  background: #1e293b; border: 1px solid #334155; border-radius: 6px;
  padding: 0.75rem 0.95rem;
}
.ccp-syn-block h4 {
  margin: 0 0 0.45rem 0; color: #fde68a; font-size: 0.95rem;
  border-left: 3px solid #fde68a; padding-left: 0.5rem;
}
.ccp-syn-block p {
  margin: 0; font-size: 0.92rem; line-height: 1.7; color: #cbd5e1;
}
.ccp-syn-block ul {
  margin: 0; padding-left: 1.2rem;
}
.ccp-syn-block ul li {
  margin: 0.25rem 0; font-size: 0.9rem; line-height: 1.55; color: #cbd5e1;
}
.ccp-bright { border-left: 4px solid #10b981; }
.ccp-bright h4 { color: #34d399; border-left-color: #34d399; }
.ccp-warning { border-left: 4px solid #f59e0b; }
.ccp-warning h4 { color: #fbbf24; border-left-color: #fbbf24; }
.ccp-apply { border-left: 4px solid #60a5fa; background: rgba(59,130,246,0.05); }
.ccp-apply h4 { color: #60a5fa; border-left-color: #60a5fa; }
.ccp-special {
  border-left: 4px solid #c084fc;
  background: rgba(192,132,252,0.07);
}
.ccp-special h4 { color: #c084fc; border-left-color: #c084fc; }

.ccp-foot {
  margin-top: 1.2rem; padding-top: 0.7rem;
  border-top: 1px dashed #475569;
  text-align: center;
}
.ccp-foot small { color: #64748b; font-size: 0.72rem; }
</style>
