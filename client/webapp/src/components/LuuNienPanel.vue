<script setup>
/**
 * LuuNienPanel — vận năm chi tiết 2026-2030 cho anh.
 *
 * Source: /api/yi-publishing/luu-nien/founder
 * Mỗi năm kết hợp: Đại Vận (10 năm) + Tiểu Hạn (vận năm).
 */
import { ref, onMounted, computed, watch } from "vue";
import WikiText from "./WikiText.vue";
import { tuviPersonKey, tuviPersonName, fetchCachedAnalysis, runAnalysis } from "../stores/tuviPersonStore.js";

const data = ref(null);
const monthlyData = ref(null);
const dauQuanData = ref(null);  // ⭐ Đẩu Quân (Q2 p0088 + Q3 p0157)
const loading = ref(false);
const running = ref(false);
const error = ref("");
const activeYear = ref(2026);
const viewMode = ref("year"); // 'year' | 'monthly'
const activeMonth = ref(1);

async function loadDauQuan() {
  try {
    const pk = tuviPersonKey.value;
    const resp = await fetch("/api/tu-vi/dau-quan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ person_key: pk, luu_nguyet_year: activeYear.value }),
    }).then((r) => r.json());
    if (resp.status === "ok") dauQuanData.value = resp;
  } catch (e) { /* silent */ }
}

async function load() {
  loading.value = true; error.value = "";
  data.value = null; monthlyData.value = null; dauQuanData.value = null;
  try {
    const pk = tuviPersonKey.value;
    loadDauQuan();  // background
    // luu_nien is stored as luu_nien_{start}_{end}.json by analyzer; default 2026-2030
    const ynRes = await fetchCachedAnalysis(pk, "luu_nien_2026_2030");
    const lnRes = await fetchCachedAnalysis(pk, "luu_nien"); // legacy
    const yn = ynRes.status === "ok" ? ynRes : lnRes;
    if (yn.status === "ok") { data.value = yn; }

    const lngRes = await fetchCachedAnalysis(pk, "luu_nguyet_2026");
    const lngLegacy = await fetchCachedAnalysis(pk, "luu_nguyet");
    const lng = lngRes.status === "ok" ? lngRes : lngLegacy;
    if (lng.status === "ok") { monthlyData.value = lng; }

    if (!data.value && !monthlyData.value) {
      error.value = `Chưa có Lưu Niên / Lưu Nguyệt cho ${tuviPersonName.value}. Nhấn "Phân tích ngay".`;
    }
  } catch (e) { error.value = e.message; }
  finally { loading.value = false; }
}

async function runNow() {
  if (running.value) return;
  running.value = true; error.value = "";
  try {
    const pk = tuviPersonKey.value;
    const [yn, lng] = await Promise.all([
      runAnalysis(pk, "luu_nien", { luu_nien_start: 2026, luu_nien_end: 2030 }),
      runAnalysis(pk, "luu_nguyet", { luu_nguyet_year: 2026 }),
    ]);
    if (yn.status === "ok") data.value = yn;
    if (lng.status === "ok") monthlyData.value = lng;
  } catch (e) { error.value = e.message; }
  finally { running.value = false; }
}

watch(tuviPersonKey, () => load());
watch(activeYear, () => loadDauQuan());

const dauQuanByMonth = computed(() => {
  const out = {};
  for (const m of dauQuanData.value?.dau_quan_months || []) {
    out[m.luu_nguyet_month] = m;
  }
  return out;
});

const months = computed(() => monthlyData.value?.months || []);
const currentMonth = computed(() =>
  months.value.find((m) => m.thang_am === activeMonth.value) || months.value[0],
);

// Verdict-color helpers removed — Iron Rule #6 (#21): vận-hạn is read as đồng dạng
// (quan_sat), not labelled cát/hung. The engine no longer emits cat_hung*.

const years = computed(() => data.value?.years || []);
const currentYearData = computed(() =>
  years.value.find((y) => y.year === activeYear.value) || years.value[0],
);

onMounted(load);
</script>

<template>
  <div class="ln-wrap">
    <header class="ln-head">
      <div>
        <h2>📅 Lưu Niên — {{ tuviPersonName }} (2026-2030)</h2>
        <p>
          5 năm gần nhất, kết hợp Đại Vận (chu kỳ 10 năm) + Tiểu Hạn (vận từng năm).
        </p>
      </div>
      <button class="ln-refresh" @click="load" :disabled="loading">{{ loading ? "⏳" : "🔄" }}</button>
    </header>

    <div v-if="loading" class="ln-loading">Đang tải...</div>
    <div v-if="error" class="ln-error">
      <p>{{ error }}</p>
      <button v-if="!data && !running" class="ln-run-btn" @click="runNow">⚡ Phân tích ngay</button>
      <p v-if="running" class="ln-running">⏳ Đang chạy lưu niên + lưu nguyệt (~20s)...</p>
    </div>

    <!-- ⭐ Đẩu Quân banner (Q2 p0088 + Q3 p0157) -->
    <div v-if="dauQuanData" class="dau-quan-banner">
      <div class="dq-head">
        <span class="dq-title">⭐ Đẩu Quân (斗君) năm {{ dauQuanData.year }} ({{ dauQuanData.year_branch }})</span>
        <span class="dq-source">Q2 p0088 · Q3 p0157</span>
      </div>
      <div class="dq-body">
        <p>
          Đẩu Quân năm tại <b>{{ dauQuanData.dau_quan_year.dau_quan_branch }}</b>
          (cung <b>{{ dauQuanData.dau_quan_year.palace }}</b>) — toàn bộ năm 2026
          chịu ảnh hưởng cát/hung của cung này.
        </p>
        <details class="dq-trace">
          <summary>Cách tính (Q2 p0088)</summary>
          <ol>
            <li v-for="(t, i) in dauQuanData.dau_quan_year.trace" :key="i">{{ t }}</li>
          </ol>
        </details>
        <p class="dq-paradigm">💡 {{ dauQuanData.paradigm_note }}</p>
      </div>
    </div>

    <!-- View mode toggle -->
    <div v-if="years.length || months.length" class="ln-view-toggle">
      <button :class="{ active: viewMode === 'year' }" @click="viewMode = 'year'">
        📅 Lưu Niên 5 năm
      </button>
      <button :class="{ active: viewMode === 'monthly' }" @click="viewMode = 'monthly'"
              :disabled="!months.length">
        📆 Lưu Nguyệt 12 tháng âm 2026
      </button>
    </div>

    <!-- Year tabs -->
    <div v-if="viewMode === 'year' && years.length" class="ln-year-tabs">
      <button v-for="y in years" :key="y.year"
              :class="{ active: y.year === activeYear }"
              @click="activeYear = y.year">
        <strong>{{ y.year }}</strong>
        <small>tuổi {{ y.age_lunar }}</small>
      </button>
    </div>

    <!-- Monthly tabs -->
    <div v-if="viewMode === 'monthly' && months.length" class="ln-month-tabs">
      <button v-for="m in months" :key="m.thang_am"
              :class="{ active: m.thang_am === activeMonth,
                        'is-menh': m.palace === 'Mệnh',
                        'is-phu-the': m.palace === 'Phu Thê' }"
              @click="activeMonth = m.thang_am">
        <strong>T{{ m.thang_am }}</strong>
        <small>{{ m.branch }}</small>
        <em>{{ m.palace }}</em>
        <span v-if="dauQuanByMonth[m.thang_am]" class="dq-month-badge"
              :title="`Đẩu Quân tại ${dauQuanByMonth[m.thang_am].dau_quan_branch} (${dauQuanByMonth[m.thang_am].palace})`">
          ⭐{{ dauQuanByMonth[m.thang_am].palace.slice(0, 4) }}
        </span>
      </button>
    </div>

    <!-- Đẩu Quân monthly detail (when monthly view + month active) -->
    <div v-if="viewMode === 'monthly' && dauQuanByMonth[activeMonth]" class="dq-month-detail">
      <h4>⭐ Đẩu Quân tháng {{ activeMonth }}</h4>
      <div class="dq-md-row">
        <span class="dq-md-label">Vị trí:</span>
        <b>{{ dauQuanByMonth[activeMonth].dau_quan_branch }}</b>
        (cung <b>{{ dauQuanByMonth[activeMonth].palace }}</b>)
      </div>
      <div class="dq-md-interp">
        <div class="dq-md-cat">
          <small>Nếu cát:</small> {{ dauQuanByMonth[activeMonth].interp_cat }}
        </div>
        <div class="dq-md-hung">
          <small>Nếu hung:</small> {{ dauQuanByMonth[activeMonth].interp_hung }}
        </div>
      </div>
      <p class="dq-md-source">Nguồn: {{ dauQuanByMonth[activeMonth].source_ref }}</p>
    </div>

    <!-- Active year detail -->
    <div v-if="viewMode === 'year' && currentYearData" class="ln-detail">
      <!-- Cung context -->
      <div class="ln-cung-grid">
        <div class="ln-cung-card">
          <h4>🌗 Đại Vận V{{ currentYearData.dai_van_cycle }}</h4>
          <div class="ln-cung-branch">{{ currentYearData.dai_van_branch }}</div>
          <div class="ln-cung-palace">{{ currentYearData.dai_van_palace }}</div>
          <div class="ln-stars">
            <span v-for="s in currentYearData.dai_van_stars" :key="s" class="ln-star ln-star-dv">{{ s }}</span>
            <span v-if="!currentYearData.dai_van_stars?.length" class="ln-empty">(vô chính tinh)</span>
          </div>
        </div>
        <div class="ln-cung-card ln-cung-th">
          <h4>📅 Tiểu Hạn {{ currentYearData.year }}</h4>
          <div class="ln-cung-branch">{{ currentYearData.tieu_han_branch }}</div>
          <div class="ln-cung-palace">{{ currentYearData.tieu_han_palace }}</div>
          <div class="ln-stars">
            <span v-for="s in currentYearData.tieu_han_stars" :key="s" class="ln-star ln-star-th">{{ s }}</span>
            <span v-if="!currentYearData.tieu_han_stars?.length" class="ln-empty">(vô chính tinh)</span>
          </div>
        </div>
      </div>

      <!-- Analysis -->
      <template v-if="currentYearData.analysis">
        <div class="ln-block ln-chu-de">
          <h3>{{ currentYearData.analysis.chu_de }}</h3>
          <span v-if="currentYearData.analysis.quan_sat" class="ln-quan-sat">
            👁 {{ currentYearData.analysis.quan_sat }}
          </span>
        </div>

        <div class="ln-block">
          <h4>📖 Tổng quan</h4>
          <p><WikiText :text="currentYearData.analysis.tong_quan" /></p>
        </div>

        <div class="ln-grid-2">
          <div class="ln-block ln-bright">
            <h4>🎯 Lĩnh vực quan tâm</h4>
            <ul>
              <li v-for="(item, i) in currentYearData.analysis.linh_vuc_quan_tam" :key="i">
                <WikiText :text="item" />
              </li>
            </ul>
          </div>

          <div class="ln-block ln-warning">
            <h4>⏰ Thời điểm cần chú ý</h4>
            <ul>
              <li v-for="(item, i) in currentYearData.analysis.thoi_diem_can_chu_y" :key="i">
                <WikiText :text="item" />
              </li>
            </ul>
          </div>
        </div>

        <div class="ln-block ln-apply">
          <h4>💡 Lời khuyên</h4>
          <p><WikiText :text="currentYearData.analysis.loi_khuyen" /></p>
        </div>
      </template>
    </div>

    <!-- Monthly detail -->
    <div v-if="viewMode === 'monthly' && currentMonth" class="ln-detail">
      <div class="ln-cung-card ln-cung-month">
        <h4>📆 Tháng {{ currentMonth.thang_am }} âm (DL {{ currentMonth.solar_range }})</h4>
        <div class="ln-cung-branch">{{ currentMonth.branch }}</div>
        <div class="ln-cung-palace">{{ currentMonth.palace }}</div>
        <div class="ln-stars">
          <span v-for="s in currentMonth.stars" :key="s" class="ln-star ln-star-th">{{ s }}</span>
          <span v-if="!currentMonth.stars?.length" class="ln-empty">(vô chính tinh)</span>
        </div>
        <small v-if="currentMonth.palace === 'Mệnh'" class="ln-flag">⭐ Lưu nguyệt VỀ MỆNH</small>
        <small v-else-if="currentMonth.palace === 'Phu Thê'" class="ln-flag ln-flag-warn">⚠️ Vào Phu Thê — đề phòng</small>
      </div>

      <template v-if="currentMonth.analysis">
        <div class="ln-block ln-chu-de">
          <h3>{{ currentMonth.analysis.chu_de }}</h3>
          <span v-if="currentMonth.analysis.quan_sat" class="ln-quan-sat">
            👁 {{ currentMonth.analysis.quan_sat }}
          </span>
        </div>

        <div class="ln-block">
          <h4>🔍 Tính chất</h4>
          <p><WikiText :text="currentMonth.analysis.tinh_chat" /></p>
        </div>

        <div class="ln-grid-2">
          <div class="ln-block ln-bright">
            <h4>✅ Nên làm</h4>
            <ul>
              <li v-for="(x, i) in currentMonth.analysis.viec_lam" :key="i">
                <WikiText :text="x" />
              </li>
            </ul>
          </div>
          <div class="ln-block ln-warning">
            <h4>🚫 Nên tránh</h4>
            <ul>
              <li v-for="(x, i) in currentMonth.analysis.viec_tranh" :key="i">
                <WikiText :text="x" />
              </li>
            </ul>
          </div>
        </div>
      </template>
    </div>

    <footer v-if="data" class="ln-foot">
      <small>
        Generated {{ new Date(data.generated_at * 1000).toLocaleString('vi') }} ·
        Cost ${{ data.cost_usd?.toFixed(4) }}
      </small>
    </footer>
  </div>
</template>

<style scoped>
.ln-wrap {
  padding: 1rem 1.5rem; max-width: 980px; margin: 0 auto;
  color: #e2e8f0; font-family: "Charter", "Iowan Old Style", Georgia, serif;
}
.ln-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  border-bottom: 1px solid #334155; padding-bottom: 0.7rem; margin-bottom: 1rem;
}
.ln-head h2 { margin: 0 0 0.2rem 0; color: #fde68a; font-size: 1.3rem; }
.ln-head p { margin: 0; font-size: 0.85rem; color: #94a3b8; line-height: 1.5; }
.ln-head small { color: #64748b; font-size: 0.72rem; }
.ln-refresh {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer;
}

.ln-loading { text-align: center; padding: 2rem; color: #94a3b8; }
.ln-error { color: #fca5a5; padding: 0.6rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.ln-run-btn {
  margin-top: 0.4rem; background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white; border: none; padding: 0.45rem 0.9rem; border-radius: 4px;
  font-size: 0.85rem; cursor: pointer; font-weight: 600;
}
.ln-run-btn:hover { background: linear-gradient(135deg, #b45309, #d97706); }
.ln-running { color: #fde68a; font-size: 0.85rem; margin-top: 0.4rem; }

.ln-year-tabs {
  display: flex; gap: 0.4rem; margin-bottom: 1.2rem;
  flex-wrap: wrap;
}
.ln-year-tabs button {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 0.5rem 0.95rem; border-radius: 6px; cursor: pointer;
  font-family: inherit; display: flex; flex-direction: column; align-items: center;
  min-width: 80px; line-height: 1.2; transition: all 0.15s;
}
.ln-year-tabs button:hover { background: #283248; }
.ln-year-tabs button.active {
  background: linear-gradient(135deg, #6d28d9, #4c1d95); color: #fff;
  border-color: #7c3aed;
}
.ln-year-tabs button strong { font-size: 1.05rem; }
.ln-year-tabs button small { font-size: 0.7rem; opacity: 0.75; }

/* View mode toggle */
.ln-view-toggle { display: flex; gap: 0.4rem; margin-bottom: 0.9rem; }
.ln-view-toggle button {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;
  font-family: inherit; font-size: 0.88rem;
  transition: all 0.15s;
}
.ln-view-toggle button:hover:not(:disabled) { background: #283248; }
.ln-view-toggle button:disabled { opacity: 0.4; cursor: not-allowed; }
.ln-view-toggle button.active {
  background: linear-gradient(135deg, #be185d, #9f1239); color: #fff;
  border-color: #db2777;
}

/* Month tabs */
.ln-month-tabs {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.3rem; margin-bottom: 1.2rem;
}
.ln-month-tabs button {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 0.5rem 0.4rem; border-radius: 5px; cursor: pointer;
  font-family: inherit; line-height: 1.2;
  display: flex; flex-direction: column; align-items: center; gap: 1px;
  transition: all 0.15s;
}
.ln-month-tabs button:hover { background: #283248; }
.ln-month-tabs button.active {
  background: linear-gradient(135deg, #be185d, #9f1239); color: #fff;
  border-color: #db2777;
}
.ln-month-tabs button strong { font-size: 0.9rem; }
.ln-month-tabs button small { font-size: 0.72rem; color: #fde68a; opacity: 0.85; }
.ln-month-tabs button.active small { color: #fff; }
.ln-month-tabs button em {
  font-size: 0.65rem; font-style: normal; color: #64748b;
  text-align: center; opacity: 0.85;
}
.ln-month-tabs button.active em { color: #fbcfe8; }
.ln-month-tabs button.is-menh {
  border-color: #fde68a; box-shadow: 0 0 0 1px rgba(253,230,138,0.3);
}
.ln-month-tabs button.is-menh small { color: #fde68a; }
.ln-month-tabs button.is-phu-the {
  border-color: #f59e0b; box-shadow: 0 0 0 1px rgba(245,158,11,0.3);
}

/* Cung card cho month */
.ln-cung-month {
  border-left-color: #db2777;
  position: relative;
}
.ln-cung-month h4 { color: #f9a8d4; font-size: 0.85rem; }
.ln-flag {
  display: inline-block;
  background: #fde68a; color: #4a1a1a;
  padding: 2px 8px; border-radius: 3px;
  font-size: 0.7rem; font-weight: 700;
  margin-top: 0.4rem;
}
.ln-flag-warn { background: #f59e0b; color: #fff; }

@media (max-width: 700px) {
  .ln-month-tabs { grid-template-columns: repeat(4, 1fr); }
}

.ln-detail { display: flex; flex-direction: column; gap: 0.7rem; }

.ln-cung-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem;
}
.ln-cung-card {
  background: #1e293b; border: 1px solid #475569;
  border-radius: 6px; padding: 0.7rem 0.9rem;
  border-left: 4px solid #7c3aed;
}
.ln-cung-card.ln-cung-th { border-left-color: #f59e0b; }
.ln-cung-card h4 { margin: 0 0 0.4rem 0; font-size: 0.85rem; color: #94a3b8; }
.ln-cung-branch {
  font-size: 1.4rem; font-weight: 700; color: #fde68a;
  font-family: "Songti SC", serif;
}
.ln-cung-palace { font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.4rem; }
.ln-stars { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.ln-star {
  padding: 1px 6px; border-radius: 3px; font-size: 0.72rem;
  font-family: ui-sans-serif, sans-serif;
}
.ln-star-dv { background: rgba(124,58,237,0.18); color: #c4b5fd; }
.ln-star-th { background: rgba(245,158,11,0.18); color: #fbbf24; }
.ln-empty { color: #64748b; font-style: italic; font-size: 0.72rem; }

.ln-block {
  background: #1e293b; border: 1px solid #334155;
  border-radius: 6px; padding: 0.7rem 0.95rem;
}
.ln-block h3 { margin: 0; color: #fde68a; font-size: 1.05rem; }
.ln-block h4 {
  margin: 0 0 0.4rem 0; color: #94a3b8; font-size: 0.85rem;
  letter-spacing: 0.04em; text-transform: uppercase;
}
.ln-block p, .ln-block ul { margin: 0; font-size: 0.93rem; line-height: 1.65; color: #cbd5e1; }
.ln-block ul { padding-left: 1.1rem; }
.ln-block ul li { margin: 0.2rem 0; }

.ln-chu-de {
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  border-color: #7c3aed;
}
.ln-chu-de h3 { color: #fff; flex: 1; }
/* Neutral "đọc đồng dạng" observation (replaces the old cát/hung verdict badge) */
.ln-quan-sat {
  padding: 4px 11px; border-radius: 6px;
  background: rgba(167, 139, 250, 0.14);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #cbb6f5; font-size: 0.82rem; font-style: italic;
  font-family: ui-sans-serif, sans-serif; line-height: 1.5;
}

.ln-grid-2 {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem;
}
.ln-bright { border-left: 4px solid #10b981; }
.ln-bright h4 { color: #34d399; }
.ln-warning { border-left: 4px solid #f59e0b; }
.ln-warning h4 { color: #fbbf24; }
.ln-apply {
  border-left: 4px solid #60a5fa;
  background: rgba(59,130,246,0.06);
}
.ln-apply h4 { color: #60a5fa; }

.ln-foot {
  margin-top: 1rem; padding-top: 0.5rem;
  border-top: 1px dashed #475569; text-align: center;
}
.ln-foot small { color: #64748b; font-size: 0.72rem; }

@media (max-width: 700px) {
  .ln-cung-grid, .ln-grid-2 { grid-template-columns: 1fr; }
}

/* ━━━━ Đẩu Quân (Q2 p0088 + Q3 p0157) ━━━━ */
.dau-quan-banner {
  margin: 14px 0;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(232, 201, 90, 0.12), rgba(232, 201, 90, 0.04));
  border: 1px solid rgba(232, 201, 90, 0.35);
  border-radius: 8px;
}
.dq-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
.dq-title {
  font-weight: 600;
  color: #f5e6b1;
  font-size: 14px;
}
.dq-source {
  font-size: 10.5px;
  color: rgba(230, 238, 245, 0.5);
  font-style: italic;
}
.dq-body p { margin: 6px 0; font-size: 13px; color: #e6eef5; line-height: 1.55; }
.dq-body b { color: #f5e6b1; }
.dq-trace summary { cursor: pointer; font-size: 12px; color: #94a3b8; }
.dq-trace ol { margin: 6px 0 0 22px; padding: 0; }
.dq-trace li { font-size: 12px; color: rgba(230, 238, 245, 0.78); margin: 3px 0; }
.dq-paradigm {
  margin-top: 10px !important;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.08);
  border-left: 2px solid #a78bfa;
  border-radius: 0 3px 3px 0;
  font-size: 12px !important;
  color: rgba(230, 238, 245, 0.85);
  font-style: italic;
}

/* Đẩu Quân badge trên month tab */
.dq-month-badge {
  display: block;
  margin-top: 3px;
  background: rgba(232, 201, 90, 0.18);
  color: #f5e6b1;
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 2px;
  white-space: nowrap;
}

/* Đẩu Quân monthly detail */
.dq-month-detail {
  margin: 12px 0;
  padding: 12px 14px;
  background: rgba(232, 201, 90, 0.06);
  border-left: 3px solid #e8c95a;
  border-radius: 0 5px 5px 0;
}
.dq-month-detail h4 {
  margin: 0 0 6px;
  font-size: 13px;
  color: #f5e6b1;
}
.dq-md-row { font-size: 13px; color: #e6eef5; margin-bottom: 8px; }
.dq-md-label { color: rgba(230, 238, 245, 0.55); margin-right: 6px; }
.dq-md-row b { color: #f5e6b1; }
.dq-md-interp {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 6px 0;
}
@media (max-width: 720px) { .dq-md-interp { grid-template-columns: 1fr; } }
.dq-md-cat, .dq-md-hung {
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.55;
}
.dq-md-cat {
  background: rgba(90, 176, 122, 0.08);
  border-left: 2px solid #5ab07a;
  color: #c0e8c8;
}
.dq-md-hung {
  background: rgba(214, 90, 74, 0.08);
  border-left: 2px solid #d65a4a;
  color: #f5b8a0;
}
.dq-md-cat small, .dq-md-hung small {
  display: block;
  font-size: 10px;
  opacity: 0.7;
  margin-bottom: 2px;
}
.dq-md-source {
  margin: 6px 0 0;
  font-size: 10.5px;
  color: rgba(230, 238, 245, 0.45);
  font-style: italic;
}
</style>
