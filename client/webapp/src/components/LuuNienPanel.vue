<script setup>
/**
 * LuuNienPanel — Lưu Niên (năm) + Lưu Nguyệt (tháng) GROUNDED (2026-07-14: chuyển từ
 * luận-DeepSeek-ungrounded sang /api/tu-vi/van-han — Thể-Dụng + Tứ Hóa + sao CÓ NGUỒN).
 * Banner Đẩu Quân (Q2 p0088) giữ nguyên — tất định. Khung năm/tháng = van-han overview.
 */
import { ref, onMounted, computed, watch } from "vue";
import { tuviPersonKey, tuviPersonBirth, tuviPersonGender, tuviPersonName } from "../stores/tuviPersonStore.js";

const viewMode = ref("year");      // 'year' | 'month'
const activeYear = ref(2026);
const activeMonth = ref(1);
const years = ref([]);             // luu_nien_overview
const dauQuanData = ref(null);
const block = ref(null);           // grounded block cho năm/tháng đang chọn
const luan = ref("");
const loading = ref(false);
const luanBusy = ref(false);
const error = ref("");

const HOA_COLOR = { "Lộc": "loc", "Quyền": "quyen", "Khoa": "khoa", "Kỵ": "ky" };
const litHoa = computed(() => (block.value?.tu_hoa_van || []).filter((h) => !h.cung.startsWith("(")));

function reqBase() {
  return { birth_datetime_local: tuviPersonBirth.value, gender: tuviPersonGender.value || "nam" };
}
async function vanHan(payload) {
  const r = await fetch("/api/tu-vi/van-han", {
    method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
    body: JSON.stringify({ ...reqBase(), ...payload }),
  });
  return r.json();
}

async function loadDauQuan() {
  try {
    const resp = await fetch("/api/tu-vi/dau-quan", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({ person_key: tuviPersonKey.value, luu_nguyet_year: activeYear.value }),
    }).then((r) => r.json());
    if (resp.status === "ok") dauQuanData.value = resp;
  } catch (e) { /* silent */ }
}

async function loadYears() {
  if (!tuviPersonBirth.value) { error.value = "Chưa có ngày giờ sinh — chọn người ở tab Hồ sơ."; return; }
  error.value = "";
  const d = await vanHan({ tang: "luu_nien_overview", year: 2026, year_end: 2030 });
  if (d.status === "ok") years.value = d.years || [];
}

async function loadBlock() {
  if (!tuviPersonBirth.value) return;
  loading.value = true; luan.value = ""; block.value = null;
  try {
    const payload = viewMode.value === "year"
      ? { tang: "luu_nien", year: activeYear.value, want_llm: false }
      : { tang: "luu_nguyet", year: activeYear.value, month: activeMonth.value, want_llm: false };
    const d = await vanHan(payload);
    if (d.status !== "ok") throw new Error(d.reason || d.status);
    block.value = d.block;
  } catch (e) { error.value = "Không tải được: " + (e?.message || e); }
  finally { loading.value = false; }
}

async function genLuan() {
  luanBusy.value = true; luan.value = "";
  try {
    const payload = viewMode.value === "year"
      ? { tang: "luu_nien", year: activeYear.value, want_llm: true }
      : { tang: "luu_nguyet", year: activeYear.value, month: activeMonth.value, want_llm: true };
    const d = await vanHan(payload);
    luan.value = d.luan || "(kho sách chưa đủ nguồn để luận — không suy đoán)";
  } catch (e) { luan.value = "Lỗi: " + e.message; }
  finally { luanBusy.value = false; }
}

async function init() { await Promise.all([loadYears(), loadDauQuan()]); await loadBlock(); }
watch(tuviPersonBirth, init);
watch([viewMode, activeYear, activeMonth], loadBlock);
watch(activeYear, loadDauQuan);
onMounted(init);
</script>

<template>
  <div class="ln-wrap">
    <header class="ln-head">
      <div>
        <h2>📅 Lưu Niên · Lưu Nguyệt — {{ tuviPersonName }}</h2>
        <p>Đọc theo <b>Thể-Dụng</b>: cung nguyên cục VẬN HÀNH thế nào trong năm/tháng ấy. Nội dung <b>có nguồn</b>, không bịa.</p>
      </div>
      <button class="ln-refresh" @click="init" :disabled="loading">{{ loading ? "⏳" : "🔄" }}</button>
    </header>

    <p v-if="error" class="ln-error">{{ error }}</p>

    <!-- Đẩu Quân banner (tất định) -->
    <div v-if="dauQuanData" class="dq-banner">
      <div class="dq-head">
        <span class="dq-title">⭐ Đẩu Quân (斗君) năm {{ dauQuanData.year }} ({{ dauQuanData.year_branch }})</span>
        <span class="dq-source">Q2 p0088</span>
      </div>
      <p>Đẩu Quân năm tại <b>{{ dauQuanData.dau_quan_year.dau_quan_branch }}</b>
        (cung <b>{{ dauQuanData.dau_quan_year.palace }}</b>) — mốc khởi lưu nguyệt.</p>
      <details v-if="dauQuanData.dau_quan_year.trace" class="dq-trace">
        <summary>Cách tính</summary>
        <ol><li v-for="(t, i) in dauQuanData.dau_quan_year.trace" :key="i">{{ t }}</li></ol>
      </details>
    </div>

    <!-- Chọn năm / tháng -->
    <div class="ln-toggle">
      <button :class="{ active: viewMode === 'year' }" @click="viewMode = 'year'">Vận Năm</button>
      <button :class="{ active: viewMode === 'month' }" @click="viewMode = 'month'">Vận Tháng</button>
    </div>
    <div class="ln-picker">
      <div class="ln-years">
        <button v-for="y in years" :key="y.year" class="ln-yr" :class="{ active: activeYear === y.year }"
          @click="activeYear = y.year" :title="`${y.year_can_chi} · cung ${y.cung_the}`">
          {{ y.year }}<small>{{ y.branch }}</small>
        </button>
      </div>
      <div v-if="viewMode === 'month'" class="ln-months">
        <button v-for="m in 12" :key="m" class="ln-mo" :class="{ active: activeMonth === m }" @click="activeMonth = m">T{{ m }}</button>
      </div>
    </div>

    <!-- Block grounded -->
    <div v-if="loading" class="ln-loading">Đang tra nguồn…</div>
    <div v-else-if="block" class="ln-result">
      <p class="ln-thedung"><b>an Mệnh tại {{ block.vi_tri }}</b> — {{ block.dien_giai_the_dung }}</p>
      <p v-if="block.cung_van_nghia" class="ln-cungrule">📐 <b>Đọc cung {{ block.cung_the }} theo vận:</b> {{ block.cung_van_nghia.rule }} <span class="ln-src">📖 {{ block.cung_van_nghia.nguon }}</span></p>
      <div v-if="litHoa.length" class="ln-hoa-grid">
        <div v-for="h in litHoa" :key="h.hoa" class="ln-hoa" :data-hoa="HOA_COLOR[h.hoa]">
          <b>{{ h.hoa }}</b> {{ h.sao }} → {{ h.cung }}<small>{{ h.nghia }}</small>
        </div>
      </div>
      <div class="ln-sao">
        <template v-if="block.sao_nguon?.length">
          <div v-for="(s, i) in block.sao_nguon" :key="i" class="ln-sao-item">
            <p><b>{{ s.sao }}:</b> {{ s.dich }}</p><span class="ln-src">📖 {{ s.nguon }}</span>
          </div>
        </template>
        <p v-else class="ln-chuanguon">Kho sách chưa có nội dung đã duyệt cho cung này — để trống, không suy đoán.</p>
      </div>
      <div class="ln-luan-zone">
        <button v-if="!luan && !block.chua_co_nguon" class="ln-luan-btn" :disabled="luanBusy" @click="genLuan">
          {{ luanBusy ? "Đang dệt luận…" : "✍️ Luận từ nguồn" }}
        </button>
        <div v-if="luan" class="ln-luan">{{ luan }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ln-wrap { padding: 1rem 1.5rem; max-width: 980px; margin: 0 auto; color: var(--read-text, #e2e8f0); }
.ln-head { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--read-border, #334155); padding-bottom: 0.7rem; margin-bottom: 1rem; }
.ln-head h2 { margin: 0 0 0.2rem; color: var(--read-han, #fde68a); font-size: 1.3rem; }
.ln-head p { margin: 0; font-size: 0.85rem; color: var(--read-text-muted, #94a3b8); line-height: 1.5; }
.ln-refresh { background: var(--read-surface, #334155); border: 1px solid var(--read-border, #475569); color: var(--read-text-dim, #cbd5e1); padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer; }
.ln-error { color: #fca5a5; padding: 0.6rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.ln-loading { text-align: center; padding: 1.2rem; color: var(--read-text-muted, #94a3b8); }
.dq-banner { background: rgba(253,230,138,0.06); border: 1px solid rgba(253,230,138,0.25); border-radius: 8px; padding: 0.7rem 0.9rem; margin-bottom: 1rem; }
.dq-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.3rem; }
.dq-title { color: var(--read-han, #fde68a); font-weight: 600; font-size: 0.92rem; }
.dq-source { font-size: 0.7rem; color: var(--read-text-faint, #64748b); }
.dq-banner p { margin: 0; font-size: 0.85rem; line-height: 1.55; color: var(--read-text-dim, #cbd5e1); }
.dq-trace summary { cursor: pointer; font-size: 0.78rem; color: var(--read-accent, #7ec8e3); margin-top: 0.4rem; }
.dq-trace ol { margin: 0.3rem 0 0; font-size: 0.8rem; color: var(--read-text-muted, #94a3b8); }
.ln-toggle { display: flex; gap: 6px; margin-bottom: 0.8rem; }
.ln-toggle button { padding: 5px 16px; border-radius: 8px; border: 1px solid var(--read-border, #475569); background: var(--read-surface, #1e293b); color: var(--read-text-dim, #cbd5e1); cursor: pointer; font-weight: 600; font-size: 0.85rem; }
.ln-toggle button.active { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); }
.ln-picker { margin-bottom: 1rem; }
.ln-years, .ln-months { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
.ln-yr { display: inline-flex; flex-direction: column; align-items: center; padding: 4px 12px; border-radius: 8px; border: 1px solid var(--read-border, #475569); background: var(--read-surface, #1e293b); color: var(--read-text-dim, #cbd5e1); cursor: pointer; font-size: 0.85rem; }
.ln-yr small { font-size: 0.65rem; color: var(--read-text-faint, #64748b); }
.ln-yr.active, .ln-mo.active { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); }
.ln-mo { padding: 4px 10px; border-radius: 6px; border: 1px solid var(--read-border, #475569); background: var(--read-surface, #1e293b); color: var(--read-text-dim, #cbd5e1); cursor: pointer; font-size: 0.8rem; }
.ln-result { border: 1px solid var(--read-border, #334155); border-radius: 10px; padding: 0.9rem 1rem; background: var(--read-surface, rgba(0,0,0,0.12)); }
.ln-thedung { margin: 0 0 0.5rem; font-size: 0.9rem; line-height: 1.6; color: var(--read-text-dim, #cbd5e1); }
.ln-cungrule { margin: 0 0 0.7rem; padding: 6px 9px; border-left: 3px solid var(--read-rule, rgba(232,201,90,0.5)); border-radius: 6px; font-size: 0.82rem; line-height: 1.55; color: var(--read-text-dim, #cbd5e1); background: rgba(0,0,0,0.12); }
.ln-hoa-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 6px; margin-bottom: 0.7rem; }
.ln-hoa { border: 1px solid var(--read-border, rgba(230,238,245,0.16)); border-left-width: 3px; border-radius: 6px; padding: 5px 9px; font-size: 0.78rem; color: var(--read-text-dim, #cbd5e1); }
.ln-hoa small { display: block; color: var(--read-text-faint, #64748b); margin-top: 2px; }
.ln-hoa[data-hoa="loc"] { border-left-color: #5ab07a; }
.ln-hoa[data-hoa="quyen"] { border-left-color: #d6a05a; }
.ln-hoa[data-hoa="khoa"] { border-left-color: #7ec8e3; }
.ln-hoa[data-hoa="ky"] { border-left-color: #d65a4a; }
.ln-sao-item { padding: 5px 0; border-top: 1px solid var(--read-border, rgba(230,238,245,0.08)); }
.ln-sao-item:first-of-type { border-top: none; }
.ln-sao-item p { margin: 0; font-size: 0.85rem; line-height: 1.55; color: var(--read-text-dim, #cbd5e1); }
.ln-src { font-size: 0.7rem; color: var(--read-text-faint, #64748b); }
.ln-chuanguon { font-size: 0.82rem; font-style: italic; color: var(--read-text-faint, #64748b); }
.ln-luan-zone { margin-top: 0.7rem; }
.ln-luan-btn { padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); color: var(--read-accent, #7ec8e3); font-size: 0.82rem; font-weight: 600; }
.ln-luan-btn:disabled { opacity: 0.6; }
.ln-luan { margin-top: 0.6rem; padding: 0.7rem 0.9rem; border-radius: 6px; background: rgba(0,0,0,0.18); font-size: 0.88rem; line-height: 1.7; color: var(--read-text, #cbd5e1); white-space: pre-wrap; }
</style>
