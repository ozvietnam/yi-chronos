<script setup>
/**
 * DaiVanPanel — 12 Đại Vận GROUNDED (2026-07-14: chuyển từ luận-DeepSeek-ungrounded
 * sang endpoint /api/tu-vi/van-han: Thể-Dụng + Tứ Hóa rọi cung + sao CÓ NGUỒN + luận
 * biên-tập-từ-nguồn). Khung 12 vận = skeleton tất định (dai_van_overview), 0 bịa.
 */
import { ref, onMounted, watch } from "vue";
import { tuviPersonBirth, tuviPersonGender, tuviPersonName } from "../stores/tuviPersonStore.js";

const cycles = ref([]);
const loading = ref(false);
const error = ref("");
const expanded = ref({});      // cycle_index → grounded block
const luan = ref({});          // cycle_index → luận text
const busy = ref({});          // cycle_index → đang tải

const HOA_COLOR = { "Lộc": "loc", "Quyền": "quyen", "Khoa": "khoa", "Kỵ": "ky" };

function palaceIcon(p) {
  return { "Mệnh": "🎯", "Phụ Mẫu": "👴", "Phúc Đức": "✨", "Điền Trạch": "🏛",
    "Quan Lộc": "💼", "Nô Bộc": "🤝", "Thiên Di": "🚀", "Tật Ách": "🩺",
    "Tài Bạch": "💰", "Tử Tức": "🧒", "Phu Thê": "💍", "Huynh Đệ": "👫" }[p] || "•";
}

async function loadOverview() {
  if (!tuviPersonBirth.value) { error.value = "Chưa có ngày giờ sinh — chọn người ở tab Hồ sơ."; return; }
  loading.value = true; error.value = ""; cycles.value = []; expanded.value = {}; luan.value = {};
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({ birth_datetime_local: tuviPersonBirth.value,
        gender: tuviPersonGender.value || "nam", tang: "dai_van_overview" }),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || d.status);
    cycles.value = d.cycles || [];
  } catch (e) { error.value = "Không tải được Đại Vận: " + (e?.message || e); }
  finally { loading.value = false; }
}

async function toggleCycle(ci) {
  if (expanded.value[ci]) { expanded.value = { ...expanded.value, [ci]: null }; return; }
  busy.value = { ...busy.value, [ci]: true };
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({ birth_datetime_local: tuviPersonBirth.value,
        gender: tuviPersonGender.value || "nam", tang: "dai_van", cycle_index: ci, want_llm: false }),
    });
    const d = await resp.json();
    expanded.value = { ...expanded.value, [ci]: d.status === "ok" ? d.block : { error: d.reason } };
  } catch (e) { expanded.value = { ...expanded.value, [ci]: { error: e.message } }; }
  finally { busy.value = { ...busy.value, [ci]: false }; }
}

async function genLuan(ci) {
  busy.value = { ...busy.value, ["l" + ci]: true };
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({ birth_datetime_local: tuviPersonBirth.value,
        gender: tuviPersonGender.value || "nam", tang: "dai_van", cycle_index: ci, want_llm: true }),
    });
    const d = await resp.json();
    luan.value = { ...luan.value, [ci]: d.luan || "(kho sách chưa đủ nguồn để luận — không suy đoán)" };
  } catch (e) { luan.value = { ...luan.value, [ci]: "Lỗi: " + e.message }; }
  finally { busy.value = { ...busy.value, ["l" + ci]: false }; }
}

function litHoa(blk) { return (blk?.tu_hoa_van || []).filter((h) => !h.cung.startsWith("(")); }

watch(tuviPersonBirth, loadOverview);
onMounted(loadOverview);
</script>

<template>
  <div class="dv-wrap">
    <header class="dv-head">
      <div>
        <h2>🌗 12 Đại Vận — {{ tuviPersonName }}</h2>
        <p>Mỗi đại vận = 10 năm. Đọc theo <b>Thể-Dụng</b>: cung nguyên cục (Thể) VẬN HÀNH thế nào trong 10 năm ấy (Dụng). Nội dung sao <b>có nguồn</b>, không bịa.</p>
      </div>
      <button class="dv-refresh" @click="loadOverview" :disabled="loading">{{ loading ? "⏳" : "🔄" }}</button>
    </header>

    <div v-if="loading" class="dv-loading">Đang tải…</div>
    <div v-if="error" class="dv-error"><p>{{ error }}</p></div>

    <div v-if="cycles.length" class="dv-timeline">
      <div v-for="c in cycles" :key="c.cycle_index" class="dv-card" :class="{ 'is-expanded': expanded[c.cycle_index] }">
        <div class="dv-head-row" @click="toggleCycle(c.cycle_index)">
          <div class="dv-left">
            <span class="dv-num">V{{ c.cycle_index }}</span>
            <div class="dv-age-range"><strong>tuổi {{ c.start_age }}-{{ c.end_age }}</strong></div>
          </div>
          <div class="dv-mid">
            <span class="dv-branch">{{ c.branch }}</span>
            <span class="dv-palace">{{ palaceIcon(c.cung_the) }} {{ c.cung_the }}</span>
          </div>
          <div class="dv-right">
            <div class="dv-stars">
              <span v-for="s in c.sao" :key="s" class="dv-star">{{ s }}</span>
              <span v-if="!c.sao?.length" class="dv-empty-star">(vô chính tinh)</span>
              <span v-if="c.sao_muon_xung" class="dv-empty-star">mượn xung</span>
            </div>
          </div>
          <span class="dv-toggle">{{ expanded[c.cycle_index] ? '▾' : '▸' }}</span>
        </div>

        <div v-if="busy[c.cycle_index]" class="dv-body"><p class="dv-loading">Đang tra nguồn…</p></div>
        <div v-else-if="expanded[c.cycle_index]" class="dv-body">
          <p v-if="expanded[c.cycle_index].error" class="dv-error">{{ expanded[c.cycle_index].error }}</p>
          <template v-else>
            <p class="dv-thedung">{{ expanded[c.cycle_index].dien_giai_the_dung }}</p>
            <p v-if="expanded[c.cycle_index].cung_van_nghia" class="dv-cungrule">📐 <b>Đọc theo vận:</b> {{ expanded[c.cycle_index].cung_van_nghia.rule }} <span class="dv-src">📖 {{ expanded[c.cycle_index].cung_van_nghia.nguon }}</span></p>
            <div v-if="litHoa(expanded[c.cycle_index]).length" class="dv-hoa-grid">
              <div v-for="h in litHoa(expanded[c.cycle_index])" :key="h.hoa" class="dv-hoa" :data-hoa="HOA_COLOR[h.hoa]">
                <b>{{ h.hoa }}</b> {{ h.sao }} → {{ h.cung }}<small>{{ h.nghia }}</small>
              </div>
            </div>
            <div class="dv-sao">
              <template v-if="expanded[c.cycle_index].sao_nguon?.length">
                <div v-for="(s, i) in expanded[c.cycle_index].sao_nguon" :key="i" class="dv-sao-item">
                  <p><b>{{ s.sao }}:</b> {{ s.dich }}</p><span class="dv-src">📖 {{ s.nguon }}</span>
                </div>
              </template>
              <p v-else class="dv-chuanguon">Kho sách chưa có nội dung đã duyệt cho cung này — để trống, không suy đoán.</p>
            </div>
            <div class="dv-luan-zone">
              <button v-if="!luan[c.cycle_index] && !expanded[c.cycle_index].chua_co_nguon"
                class="dv-luan-btn" :disabled="busy['l'+c.cycle_index]" @click="genLuan(c.cycle_index)">
                {{ busy['l'+c.cycle_index] ? "Đang dệt luận…" : "✍️ Luận đại vận này (từ nguồn)" }}
              </button>
              <div v-if="luan[c.cycle_index]" class="dv-luan">{{ luan[c.cycle_index] }}</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dv-wrap { padding: 1rem 1.5rem; max-width: 980px; margin: 0 auto; color: var(--read-text, #e2e8f0); }
.dv-head { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--read-border, #334155); padding-bottom: 0.7rem; margin-bottom: 1rem; }
.dv-head h2 { margin: 0 0 0.2rem 0; color: var(--read-han, #fde68a); font-size: 1.3rem; }
.dv-head p { margin: 0; font-size: 0.85rem; color: var(--read-text-muted, #94a3b8); line-height: 1.5; }
.dv-refresh { background: var(--read-surface, #334155); border: 1px solid var(--read-border, #475569); color: var(--read-text-dim, #cbd5e1); padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer; }
.dv-loading { text-align: center; padding: 1rem; color: var(--read-text-muted, #94a3b8); }
.dv-error { color: #fca5a5; padding: 0.6rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.dv-timeline { display: flex; flex-direction: column; gap: 0.5rem; }
.dv-card { background: var(--read-surface, #1e293b); border: 1px solid var(--read-border, #334155); border-radius: 6px; overflow: hidden; }
.dv-card.is-expanded { border-color: var(--read-accent, #60a5fa); }
.dv-head-row { display: grid; grid-template-columns: auto 1fr 2fr auto; gap: 0.8rem; align-items: center; padding: 0.6rem 0.9rem; cursor: pointer; }
.dv-left { display: flex; align-items: center; gap: 0.5rem; }
.dv-num { background: #4a1a1a; color: #fde68a; width: 32px; height: 32px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; }
.dv-age-range strong { color: var(--read-text, #f1f5f9); font-size: 0.9rem; }
.dv-mid { display: flex; align-items: center; gap: 0.4rem; }
.dv-branch { background: var(--read-bg, #0f172a); border: 1px solid var(--read-border, #475569); padding: 2px 8px; border-radius: 3px; color: var(--read-han, #fde68a); font-weight: 600; font-size: 0.85rem; }
.dv-palace { font-size: 0.8rem; color: var(--read-text-muted, #94a3b8); }
.dv-right { display: flex; justify-content: flex-end; }
.dv-stars { display: flex; flex-wrap: wrap; gap: 0.25rem; justify-content: flex-end; }
.dv-star { background: rgba(34,197,94,0.15); color: #86efac; padding: 1px 6px; border-radius: 3px; font-size: 0.72rem; }
.dv-empty-star { color: var(--read-text-faint, #64748b); font-size: 0.72rem; font-style: italic; }
.dv-toggle { color: var(--read-text-muted, #94a3b8); font-size: 0.85rem; }
.dv-body { padding: 0.8rem 0.9rem 1rem; border-top: 1px solid var(--read-border, #1e293b); background: rgba(0,0,0,0.12); }
.dv-thedung { margin: 0 0 0.5rem; font-size: 0.9rem; line-height: 1.6; color: var(--read-text-dim, #cbd5e1); }
.dv-cungrule { margin: 0 0 0.7rem; padding: 6px 9px; border-left: 3px solid var(--read-rule, rgba(232,201,90,0.5)); border-radius: 6px; font-size: 0.82rem; line-height: 1.55; color: var(--read-text-dim, #cbd5e1); background: rgba(0,0,0,0.12); }
.dv-hoa-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 6px; margin-bottom: 0.7rem; }
.dv-hoa { border: 1px solid var(--read-border, rgba(230,238,245,0.16)); border-left-width: 3px; border-radius: 6px; padding: 5px 9px; font-size: 0.78rem; color: var(--read-text-dim, #cbd5e1); }
.dv-hoa small { display: block; color: var(--read-text-faint, #64748b); margin-top: 2px; }
.dv-hoa[data-hoa="loc"] { border-left-color: #5ab07a; }
.dv-hoa[data-hoa="quyen"] { border-left-color: #d6a05a; }
.dv-hoa[data-hoa="khoa"] { border-left-color: #7ec8e3; }
.dv-hoa[data-hoa="ky"] { border-left-color: #d65a4a; }
.dv-sao-item { padding: 5px 0; border-top: 1px solid var(--read-border, rgba(230,238,245,0.08)); }
.dv-sao-item:first-of-type { border-top: none; }
.dv-sao-item p { margin: 0; font-size: 0.85rem; line-height: 1.55; color: var(--read-text-dim, #cbd5e1); }
.dv-src { font-size: 0.7rem; color: var(--read-text-faint, #64748b); }
.dv-chuanguon { font-size: 0.82rem; font-style: italic; color: var(--read-text-faint, #64748b); }
.dv-luan-zone { margin-top: 0.7rem; }
.dv-luan-btn { padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); color: var(--read-accent, #7ec8e3); font-size: 0.82rem; font-weight: 600; }
.dv-luan-btn:disabled { opacity: 0.6; }
.dv-luan { margin-top: 0.6rem; padding: 0.7rem 0.9rem; border-radius: 6px; background: rgba(0,0,0,0.18); font-size: 0.88rem; line-height: 1.7; color: var(--read-text, #cbd5e1); white-space: pre-wrap; }
@media (max-width: 700px) { .dv-head-row { grid-template-columns: auto 1fr; } .dv-mid, .dv-right { grid-column: 1 / -1; justify-content: flex-start; } }
</style>
