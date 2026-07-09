<script setup>
/**
 * DeepReadingPanel — "Luận Sâu Trọn Đời" (99 xu) cho người đang xem.
 * Phê mệnh DeepSeek async (mirror Hội Đồng nhưng KHÔNG câu hỏi/sage): bấm → chạy ngầm
 * 30-90s → poll → hiện bản văn xuôi đầy đủ. Login-gated; trừ 99 xu (hoàn nếu lỗi).
 */
import { ref, computed, onMounted, onUnmounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";
import { sessionToken } from "../stores/authStore.js";

const result = ref(null);
const loading = ref(false);
const err = ref("");
const elapsed = ref(0);
const LS_KEY = "yi_deep_reading_job";   // nhớ job đang chạy → quay lại tự hiện
let pollTimer = null, tickTimer = null;

function stopTimers() {
  if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
  if (tickTimer) { clearInterval(tickTimer); tickTimer = null; }
}

const personName = computed(() => activePerson.value?.name || "người đang xem");
const personKey = computed(() => activePerson.value?.person_key || "self");
const hasBirth = computed(() => !!activePerson.value?.birth_datetime_local);

const LABELS = {
  khai_de: "Khai đề", dan_nhap: "Dẫn nhập", tong_quan: "Tổng quan", menh_cuc: "Mệnh cục",
  tinh_cach: "Tính cách", ban_menh: "Bản mệnh", su_nghiep: "Sự nghiệp", quan_loc: "Quan lộc",
  tai_loc: "Tài lộc", tai_bach: "Tài bạch", tinh_duyen: "Tình duyên", phu_the: "Phu thê",
  gia_dao: "Gia đạo", tu_tuc: "Tử tức", suc_khoe: "Sức khỏe", tat_ach: "Tật ách",
  phuc_duc: "Phúc đức", dai_van: "Đại vận", luu_nien: "Lưu niên", loi_khuyen: "Lời khuyên",
  ket: "Lời kết", ket_luan: "Lời kết",
};
function humanize(k) {
  return LABELS[k] || String(k).replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}
function asText(v) {
  if (v == null) return "";
  if (typeof v === "string") return v;
  if (Array.isArray(v)) return v.map(asText).filter(Boolean).join("\n");
  if (typeof v === "object") return Object.values(v).map(asText).filter(Boolean).join("\n");
  return String(v);
}
const sections = computed(() => {
  const phe = result.value?.phe_menh;
  if (!phe) return [];
  if (typeof phe === "string") return phe.trim() ? [{ label: "Phê mệnh", text: phe.trim() }] : [];
  if (typeof phe !== "object") return [];
  return Object.entries(phe)
    .map(([k, v]) => ({ label: humanize(k), text: asText(v).trim() }))
    .filter((s) => s.text);
});

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

async function runDeep() {
  if (!hasBirth.value) { err.value = "Người đang xem chưa có giờ sinh — chọn người có giờ sinh để luận."; return; }
  loading.value = true; err.value = ""; result.value = null; elapsed.value = 0;
  stopTimers();
  tickTimer = setInterval(() => { elapsed.value += 1; }, 1000);
  try {
    const r = await fetch("/api/hermes/deep-reading/enqueue", {
      method: "POST", headers: authHeaders(), credentials: "include",
      body: JSON.stringify({ person_key: personKey.value }),
    });
    const d = await r.json();
    if (!r.ok) { err.value = d.detail || `Lỗi ${r.status}`; loading.value = false; stopTimers(); return; }
    if (d.status !== "processing") {     // precheck fail (not_synced/missing_birth/denied) → hiện luôn
      result.value = d; loading.value = false; stopTimers(); return;
    }
    try { localStorage.setItem(LS_KEY, JSON.stringify({ job_id: d.job_id })); } catch { /* noop */ }
    pollJob(d.job_id);
  } catch (e) { err.value = String(e.message || e); loading.value = false; stopTimers(); }
}

async function pollJob(jobId) {
  try {
    const r = await fetch(`/api/hermes/deep-reading/job/${jobId}`, { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (d.state === "SUCCESS") {
      result.value = d.result || {}; loading.value = false; stopTimers();
      try { localStorage.removeItem(LS_KEY); } catch { /* noop */ }
      return;
    }
    if (d.state === "FAILURE") {
      err.value = "Luận Sâu gặp trục trặc khi luận. Anh thử lại sau nhé (nếu đã trừ xu sẽ được hoàn).";
      loading.value = false; stopTimers();
      try { localStorage.removeItem(LS_KEY); } catch { /* noop */ }
      return;
    }
    pollTimer = setTimeout(() => pollJob(jobId), 5000);     // PENDING/STARTED → chờ tiếp
  } catch {
    pollTimer = setTimeout(() => pollJob(jobId), 8000);     // lỗi mạng tạm → thử lại
  }
}

function resumePending() {     // quay lại trang khi job còn chạy → tiếp tục poll, tự hiện
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(LS_KEY) || "null"); } catch { saved = null; }
  if (saved && saved.job_id) {
    loading.value = true; elapsed.value = 0;
    stopTimers();
    tickTimer = setInterval(() => { elapsed.value += 1; }, 1000);
    pollJob(saved.job_id);
  }
}

onMounted(resumePending);
onUnmounted(stopTimers);
</script>

<template>
  <div class="deep-reading">
    <header class="dr-head">
      <h2>💎 Luận Sâu Trọn Đời — Tử Vi Đẩu Số</h2>
      <p class="dr-sub">Luận sâu trọn lá số của <b>{{ personName }}</b> — phê mệnh theo phong cách Khang Tiết
        (gợi mở, đọc đồng dạng, <b>không tiên tri</b>). Bản văn xuôi đầy đủ, chạy ngầm 30-90 giây.</p>
    </header>

    <div class="dr-actions">
      <button class="dr-run" :disabled="loading || !hasBirth" @click="runDeep">
        {{ loading ? `💎 Đang luận sâu… (${elapsed}s)` : "💎 Luận Sâu Trọn Đời (99 xu)" }}
      </button>
      <span v-if="!hasBirth" class="dr-note">Chọn người có giờ sinh để luận.</span>
    </div>
    <p v-if="loading" class="dr-progress">🔮 Đang luận sâu trọn lá số + bám sách cổ — cần <b>30-90 giây</b>,
      chạy ngầm. Anh cứ để đó (hoặc qua tab khác rồi quay lại) — kết quả sẽ <b>tự hiện</b>.</p>
    <p v-if="err" class="dr-err">⚠ {{ err }}</p>

    <div v-if="result" class="dr-result">
      <p v-if="result.status === 'denied' || result.code === 403" class="dr-err">
        Chưa đủ điều kiện / hết lượt cho Luận Sâu (99 xu).<span v-if="result.reason"> ({{ result.reason }})</span>
      </p>
      <p v-else-if="result.code === 404 || result.status === 'not_synced'" class="dr-err">
        Hồ sơ chưa sẵn sàng để luận.
      </p>
      <p v-else-if="result.code === 422 || result.status === 'missing_birth'" class="dr-err">
        Người đang xem thiếu giờ sinh.
      </p>
      <p v-else-if="result.status && result.status !== 'done'" class="dr-err">
        {{ result.reason || result.status }}
      </p>
      <template v-else>
        <section v-for="(s, i) in sections" :key="i" class="dr-sec reading-surface">
          <h3>{{ s.label }}</h3>
          <div class="dr-sec-body reading-prose">{{ s.text }}</div>
        </section>
        <p v-if="!sections.length" class="dr-note">Đã luận xong (lá #{{ result.casting_id }}) nhưng nội dung trống — thử lại sau.</p>
        <p v-if="result.paradigm_note" class="dr-paradigm">{{ result.paradigm_note }}</p>
        <p v-if="result.remaining_uses != null" class="dr-note">Còn {{ result.remaining_uses }} lượt luận sâu.</p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.deep-reading { max-width: 920px; margin: 0 auto; color: var(--read-fg, inherit); }
.dr-head h2 { margin-bottom: .2rem; }
.dr-sub { color: var(--read-muted, #888); font-size: .9rem; line-height: 1.6; }
.dr-actions { display: flex; gap: .8rem; align-items: center; margin: 1rem 0 .4rem; flex-wrap: wrap; }
.dr-run { padding: .65rem 1.3rem; border: none; border-radius: 8px; font-weight: 700; font-size: 1.02rem;
  cursor: pointer; background: linear-gradient(135deg, #b45309, #f59e0b); color: #fff;
  box-shadow: 0 2px 10px rgba(180,83,9,.3); }
.dr-run:disabled { opacity: .6; cursor: wait; }
.dr-note { font-size: .82rem; color: var(--read-muted, #888); }
.dr-progress { color: var(--read-muted, #666); background: rgba(245,158,11,.07); border: 1px dashed rgba(180,83,9,.3);
  padding: .55rem .8rem; border-radius: 8px; font-size: .9rem; line-height: 1.6; margin: .5rem 0; }
.dr-err { color: #c2410c; background: rgba(217,119,6,.08); padding: .5rem .7rem; border-radius: 6px; }
.dr-result { margin-top: 1.1rem; }
.dr-sec { border: 1px solid var(--read-border, #ddd); border-left: 3px solid #b45309;
  border-radius: 0 8px 8px 0; padding: .7rem 1rem; margin-bottom: .7rem; background: var(--read-bg, transparent); }
.dr-sec h3 { margin: 0 0 .45rem; font-size: 1.05rem; }
.dr-sec-body { white-space: pre-wrap; line-height: var(--reading-line-height, 1.78); font-size: calc(1rem * var(--reading-scale)); }
.dr-paradigm { margin-top: .8rem; font-size: calc(0.82rem * var(--reading-scale)); font-style: italic; color: var(--read-muted, #999);
  line-height: var(--reading-line-height, 1.78); border-top: 1px solid var(--read-border, #eee); padding-top: .6rem; }

@media (max-width: 560px) {
  .deep-reading { padding-inline: 2px; }
  .dr-run { width: 100%; min-height: 48px; }
  .dr-sec { padding: 0.85rem 0.9rem; }
  .dr-sec h3 { font-size: calc(1.02rem * var(--reading-scale)); }
  .dr-sec-body { font-size: calc(17px * var(--reading-scale)); }
}
</style>
