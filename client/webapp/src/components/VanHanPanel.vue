<script setup>
/**
 * 🗓️ Vận hạn GROUNDED — Đại Vận / Lưu Niên (năm) / Lưu Nguyệt (tháng) / Tuần (10 ngày).
 *
 * Anh giao 2026-07-14: "vận hạn theo tuần/tháng, làm kỹ, dùng sách/thư viện/công thức".
 * Đọc theo cổ pháp THỂ-DỤNG + Tứ Hóa rọi cung (paradigm đồng dạng, KHÔNG predict).
 * Nội dung sao CHỈ từ kho đã DUYỆT (founder_verified=1); thiếu nguồn → nói rõ, không bịa.
 * Endpoint: POST /api/tu-vi/van-han (block tất định + luận LLM biên-tập-từ-nguồn).
 */
import { computed, ref, watch } from "vue";
import { tuviPersonBirth, tuviPersonGender, tuviPersonName } from "../stores/tuviPersonStore.js";

const open = ref(false);
const tang = ref("luu_nguyet");   // default tháng — đúng trọng tâm Anh cần
const year = ref(2026);
const month = ref(1);
const tuan = ref(1);
const cycle = ref(1);

const block = ref(null);
const luan = ref("");
const loading = ref(false);
const luanLoading = ref(false);
const error = ref("");

const TANG_TABS = [
  { key: "dai_van", label: "Đại Vận", sub: "10 năm" },
  { key: "luu_nien", label: "Lưu Niên", sub: "năm" },
  { key: "luu_nguyet", label: "Lưu Nguyệt", sub: "tháng" },
  { key: "tuan", label: "Tuần", sub: "10 ngày" },
];
const TUAN_LABEL = { 1: "Thượng tuần", 2: "Trung tuần", 3: "Hạ tuần" };
const HOA_COLOR = { "Lộc": "loc", "Quyền": "quyen", "Khoa": "khoa", "Kỵ": "ky" };

const litHoa = computed(() =>
  (block.value?.tu_hoa_van || []).filter((h) => !h.cung.startsWith("(")),
);

function body() {
  const b = {
    birth_datetime_local: tuviPersonBirth.value,
    gender: tuviPersonGender.value || "nam",
    tang: tang.value,
    want_llm: false,
  };
  if (tang.value === "dai_van") b.cycle_index = cycle.value;
  if (["luu_nien", "luu_nguyet", "tuan"].includes(tang.value)) b.year = year.value;
  if (["luu_nguyet", "tuan"].includes(tang.value)) b.month = month.value;
  if (tang.value === "tuan") b.tuan = tuan.value;
  return b;
}

async function loadBlock() {
  if (!tuviPersonBirth.value) { error.value = "Chưa có ngày giờ sinh — chọn người xem ở tab Hồ sơ."; return; }
  loading.value = true; error.value = ""; luan.value = "";
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" },
      credentials: "include", body: JSON.stringify(body()),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || d.status || "lỗi");
    block.value = d.block;
  } catch (e) {
    error.value = "Không tải được vận hạn: " + (e?.message || e);
    block.value = null;
  } finally { loading.value = false; }
}

async function genLuan() {
  luanLoading.value = true; luan.value = "";
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" },
      credentials: "include", body: JSON.stringify({ ...body(), want_llm: true }),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || "lỗi");
    luan.value = d.luan || "(kho sách chưa đủ nguồn để luận tầng này — không suy đoán bừa)";
  } catch (e) {
    luan.value = "Không sinh được luận: " + (e?.message || e);
  } finally { luanLoading.value = false; }
}

watch([tang, year, month, tuan, cycle], () => { if (open.value) loadBlock(); });

async function toggle() {
  open.value = !open.value;
  if (open.value && !block.value) await loadBlock();
}
</script>

<template>
  <section class="vh-block">
    <button type="button" class="vh-toggle" @click="toggle">
      <span>🗓️ Vận hạn — Đại Vận · Lưu Niên · Lưu Nguyệt · Tuần (đọc Thể-Dụng, có nguồn)</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="vh-body">
      <!-- Chọn tầng -->
      <nav class="vh-tangs">
        <button v-for="t in TANG_TABS" :key="t.key" type="button"
          class="vh-tang" :class="{ active: tang === t.key }" @click="tang = t.key">
          {{ t.label }}<small>{{ t.sub }}</small>
        </button>
      </nav>

      <!-- Bộ chọn thời điểm theo tầng -->
      <div class="vh-picker">
        <template v-if="tang === 'dai_van'">
          <label>Vận số <input type="number" v-model.number="cycle" min="1" max="12" /></label>
        </template>
        <template v-else>
          <label>Năm <input type="number" v-model.number="year" min="1930" max="2100" /></label>
          <label v-if="['luu_nguyet','tuan'].includes(tang)">Tháng
            <input type="number" v-model.number="month" min="1" max="12" /></label>
          <label v-if="tang === 'tuan'">Tuần
            <select v-model.number="tuan">
              <option :value="1">Thượng tuần (1-10)</option>
              <option :value="2">Trung tuần (11-20)</option>
              <option :value="3">Hạ tuần (21-cuối)</option>
            </select>
          </label>
        </template>
      </div>

      <p v-if="loading" class="vh-note">Đang tra vận hạn…</p>
      <p v-else-if="error" class="vh-error">{{ error }}</p>

      <div v-else-if="block" class="vh-result">
        <!-- Thể-Dụng -->
        <div class="vh-thedung">
          <span class="vh-vitri">an Mệnh tại <b>{{ block.vi_tri }}</b></span>
          <p>{{ block.dien_giai_the_dung }}</p>
        </div>

        <!-- Tứ Hóa rọi cung -->
        <div v-if="litHoa.length" class="vh-hoa-group">
          <h6 class="vh-sub">Tứ Hóa của tầng rọi vào cung — sân khấu MỜI QUAN-SÁT (không phán cát/hung)</h6>
          <div class="vh-hoa-grid">
            <div v-for="h in litHoa" :key="h.hoa" class="vh-hoa" :data-hoa="HOA_COLOR[h.hoa]">
              <span class="vh-hoa-name">{{ h.hoa }}</span>
              <span class="vh-hoa-star">{{ h.sao }}</span>
              <span class="vh-hoa-cung">→ {{ h.cung }}</span>
              <small>{{ h.nghia }}</small>
            </div>
          </div>
        </div>

        <!-- Sao tại cung vận Mệnh (có nguồn) -->
        <div class="vh-sao">
          <h6 class="vh-sub">
            Sao tại cung vận Mệnh: {{ (block.sao || []).join(', ') || 'Vô Chính Diệu' }}
            <span v-if="block.sao_muon_xung" class="vh-muon">(mượn sao cung xung)</span>
          </h6>
          <template v-if="block.sao_nguon && block.sao_nguon.length">
            <div v-for="(s, i) in block.sao_nguon" :key="i" class="vh-sao-item">
              <p><b>{{ s.sao }}:</b> {{ s.dich }}</p>
              <span class="vh-src">📖 {{ s.nguon }}</span>
            </div>
          </template>
          <p v-else class="vh-chuanguon">Kho sách chưa có nội dung đã duyệt cho cung này — để trống, không suy đoán.</p>
        </div>

        <p v-if="block.luu_y_vi_mo" class="vh-vimo">⚠ {{ block.luu_y_vi_mo }}</p>

        <!-- Nguyên tắc + luận grounded -->
        <details class="vh-principle">
          <summary>Nguyên tắc Thể-Dụng (nguồn: {{ block.nguyen_tac.nguon }})</summary>
          <p>{{ block.nguyen_tac.text }}</p>
        </details>

        <div class="vh-luan-zone">
          <button v-if="!luan && !block.chua_co_nguon" type="button" class="vh-luan-btn"
            :disabled="luanLoading" @click="genLuan">
            {{ luanLoading ? "Đang dệt luận từ nguồn…" : "✍️ Luận tầng này (biên tập từ nguồn)" }}
          </button>
          <p v-else-if="block.chua_co_nguon" class="vh-chuanguon">Chưa đủ nguồn để luận — không gieo rác.</p>
          <div v-if="luan" class="vh-luan">{{ luan }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.vh-block { margin-top: 14px; }
.vh-toggle {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 10px; text-align: left; padding: 11px 14px; cursor: pointer;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.15)); border-radius: 10px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(14px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-toggle small { color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); font-weight: 400; }
.vh-body { padding: 12px 4px 4px; }
.vh-note, .vh-error { color: var(--read-text-muted, rgba(230, 238, 245, 0.7)); font-size: calc(13px * var(--reading-scale, 1)); }
.vh-error { color: #f5a08c; }
.vh-tangs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.vh-tang {
  display: inline-flex; flex-direction: column; align-items: center; cursor: pointer;
  padding: 6px 14px; border-radius: 9px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2));
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
  color: var(--read-text-dim, rgba(230, 238, 245, 0.82));
  font-size: calc(13px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-tang small { font-weight: 400; font-size: calc(10px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-tang.active { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126, 200, 227, 0.12)); }
.vh-picker { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; }
.vh-picker label { font-size: calc(12.5px * var(--reading-scale, 1)); color: var(--read-text-dim, rgba(230, 238, 245, 0.8)); display: inline-flex; align-items: center; gap: 6px; }
.vh-picker input, .vh-picker select {
  padding: 4px 8px; border-radius: 6px; width: 84px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2));
  background: var(--read-surface, rgba(255, 255, 255, 0.04)); color: var(--read-text, rgba(230, 238, 245, 0.92));
}
.vh-picker select { width: auto; }
.vh-result { border: 1px solid var(--read-border, rgba(230, 238, 245, 0.14)); border-radius: 10px; padding: 12px 14px; background: var(--read-surface, rgba(255, 255, 255, 0.02)); }
.vh-thedung { margin-bottom: 12px; }
.vh-vitri { font-size: calc(13px * var(--reading-scale, 1)); color: var(--read-accent, #7ec8e3); }
.vh-thedung p { margin: 4px 0 0; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text, rgba(230, 238, 245, 0.88)); }
.vh-sub { margin: 0 0 6px; font-size: calc(12px * var(--reading-scale, 1)); font-weight: 600; color: var(--read-han, #e8c95a); opacity: 0.9; }
.vh-hoa-group { margin-bottom: 12px; }
.vh-hoa-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; }
.vh-hoa { border: 1px solid var(--read-border, rgba(230, 238, 245, 0.16)); border-left-width: 3px; border-radius: 8px; padding: 7px 10px; font-size: calc(12px * var(--reading-scale, 1)); }
.vh-hoa[data-hoa="loc"] { border-left-color: #5ab07a; }
.vh-hoa[data-hoa="quyen"] { border-left-color: #d6a05a; }
.vh-hoa[data-hoa="khoa"] { border-left-color: #7ec8e3; }
.vh-hoa[data-hoa="ky"] { border-left-color: #d65a4a; }
.vh-hoa-name { font-weight: 700; color: var(--read-text, rgba(230, 238, 245, 0.92)); }
.vh-hoa-star { margin-left: 5px; color: var(--read-text-dim, rgba(230, 238, 245, 0.8)); }
.vh-hoa-cung { display: block; color: var(--read-accent, #7ec8e3); margin-top: 2px; }
.vh-hoa small { display: block; color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); margin-top: 2px; }
.vh-sao { margin-bottom: 10px; }
.vh-muon { font-weight: 400; font-size: calc(10.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-sao-item { padding: 6px 0; border-top: 1px solid var(--read-border, rgba(230, 238, 245, 0.1)); }
.vh-sao-item:first-of-type { border-top: none; }
.vh-sao-item p { margin: 0; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230, 238, 245, 0.82)); }
.vh-src { font-size: calc(10.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-chuanguon { font-size: calc(12px * var(--reading-scale, 1)); font-style: italic; color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); margin: 6px 0 0; }
.vh-vimo { font-size: calc(11.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.6)); margin: 8px 0; }
.vh-principle > summary { cursor: pointer; font-size: calc(11.5px * var(--reading-scale, 1)); color: var(--read-accent, #7ec8e3); margin: 8px 0; }
.vh-principle p { margin: 4px 0 0; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230, 238, 245, 0.75)); padding-left: 9px; border-left: 2px solid var(--read-rule, rgba(232, 201, 90, 0.35)); }
.vh-luan-zone { margin-top: 10px; }
.vh-luan-btn {
  padding: 7px 14px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126, 200, 227, 0.12));
  color: var(--read-accent, #7ec8e3); font-size: calc(12.5px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-luan-btn:disabled { opacity: 0.6; cursor: default; }
.vh-luan { margin-top: 10px; padding: 10px 12px; border-radius: 8px; background: var(--read-surface, rgba(255, 255, 255, 0.03)); font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.75; color: var(--read-text, rgba(230, 238, 245, 0.88)); white-space: pre-wrap; }
</style>
