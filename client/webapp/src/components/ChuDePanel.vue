<script setup>
/**
 * 🎯 ĐỌC THEO CHỦ ĐỀ — dời tâm lá số theo câu hỏi đời sống.
 *
 * Khách hỏi theo chuyện đời ("đường công danh?", "sức khoẻ?") chứ không hỏi theo "cung".
 * Engine lấy CUNG của chủ đề làm TÂM rồi đọc CHÒM THẬT của nó (tam phương tứ chính tính
 * từ chính cung đó) — cổ pháp Trung Châu đọc chòm theo điểm tham chiếu.
 * 0-LLM, miễn phí, nội dung chỉ từ kho đã duyệt (thiếu nguồn → nói rõ, không bịa).
 *
 * UI theo ý Anh: TẬP TRUNG LUẬN GIẢI, dẫn sách gấp vào "📚 Chi tiết & dẫn sách".
 */
import { computed, onMounted, ref, watch } from "vue";
import { activePerson } from "../stores/userDataStore.js";

const props = defineProps({
  birthDatetimeLocal: { type: String, default: "" },
  gender: { type: String, default: "" },
});

const list = ref([]);
const chosen = ref("");
const blk = ref(null);
const loading = ref(false);
const err = ref("");

const birth = computed(() => props.birthDatetimeLocal || activePerson.value?.birth_datetime_local || "");
const gioiTinh = computed(() => props.gender || activePerson.value?.gender || "nam");

async function loadList() {
  try {
    const d = await fetch("/api/tu-vi/chu-de/danh-sach").then((r) => r.json());
    if (d.status === "ok") list.value = d.chu_de || [];
  } catch { /* im lặng */ }
}

async function pick(slug) {
  if (!birth.value) { err.value = "Chưa có ngày giờ sinh — thêm/chọn hồ sơ ở tab Hồ sơ."; return; }
  chosen.value = slug;
  loading.value = true; err.value = ""; blk.value = null;
  try {
    const d = await fetch("/api/tu-vi/chu-de/doi-tam", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({
        birth_datetime_local: birth.value, gender: gioiTinh.value,
        person_key: activePerson.value?.person_key || undefined, chu_de: slug,
      }),
    }).then((r) => r.json());
    if (d.status !== "ok") throw new Error(d.message || "Không đọc được");
    blk.value = d;
  } catch (e) {
    err.value = String(e.message || e);
  } finally { loading.value = false; }
}

// Đổi người → xoá kết quả cũ, đọc lại chủ đề đang chọn
watch(() => activePerson.value?.person_key, () => { if (chosen.value) pick(chosen.value); else blk.value = null; });
onMounted(loadList);

const tam = computed(() => blk.value?.tam || null);
const sao = computed(() => (tam.value?.sao || []).join(", ") || "Vô Chính Diệu");
</script>

<template>
  <section class="cd-panel">
    <header class="cd-head">
      <h4>🎯 Đọc theo chủ đề</h4>
      <p class="cd-sub">
        Chọn điều Anh đang bận tâm — hệ thống <b>lấy đúng cung của việc đó làm tâm</b> rồi đọc
        cả chòm quanh nó (cổ pháp Trung Châu), thay vì chỉ đọc từ cung Mệnh. Miễn phí.
      </p>
    </header>

    <div class="cd-chips">
      <button v-for="c in list" :key="c.slug" type="button"
              class="cd-chip" :class="{ on: chosen === c.slug }" @click="pick(c.slug)">
        <span class="cd-ic">{{ c.icon }}</span>{{ c.ten }}
      </button>
    </div>

    <p v-if="loading" class="cd-note">⏳ Đang đọc…</p>
    <p v-if="err" class="cd-err">⚠ {{ err }}</p>

    <div v-if="blk && tam" class="cd-result">
      <p class="cd-center">
        Đang đọc từ cung <b>{{ blk.cung_tam }}</b> ({{ tam.vi_tri }}) — sao: <b>{{ sao }}</b>
        <em v-if="tam.sao_muon_xung"> · cung không có chính tinh nên mượn sao cung đối diện (cổ pháp)</em>
      </p>

      <!-- LUẬN: nội dung sao ở cung tâm -->
      <div v-if="tam.sao_nguon?.length" class="cd-body">
        <p v-for="(s, i) in tam.sao_nguon" :key="i" class="cd-p">
          <b>{{ s.sao }}</b> — {{ s.dich }}
        </p>
      </div>
      <p v-else class="cd-note">Kho sách chưa có nội dung đã duyệt cho bộ sao này — để trống, không suy đoán.</p>

      <!-- CHÒM -->
      <div v-if="tam.hoi_chieu?.length" class="cd-chom">
        <h5>Chòm quanh cung {{ blk.cung_tam }} — cùng ảnh hưởng tới việc này</h5>
        <div v-for="(h, i) in tam.hoi_chieu" :key="i" class="cd-item">
          <span class="cd-rel">{{ h.quan_he }}</span>
          <b>{{ h.cung }}</b> ({{ h.vi_tri }}) · {{ (h.sao || []).join(", ") || "Vô Chính Diệu" }}
          <small v-for="(s, j) in (h.sao_nguon || []).slice(0, 1)" :key="j">{{ s.dich }}</small>
        </div>
      </div>

      <p v-if="blk.luu_y" class="cd-luuy">⚠ {{ blk.luu_y }}</p>

      <details class="cd-src">
        <summary>📚 Chi tiết &amp; dẫn sách</summary>
        <p class="cd-why"><b>Vì sao lấy cung {{ blk.cung_tam }}:</b> {{ blk.goc_nhin }}</p>
        <ul>
          <li v-for="(s, i) in tam.sao_nguon || []" :key="'s' + i">
            {{ s.sao }}: {{ s.dich }} <em>({{ s.nguon }})</em>
          </li>
          <li v-for="(r, i) in tam.cung_rules || []" :key="'r' + i">
            Nguyên tắc đọc cung {{ blk.cung_tam }}: {{ r.rule }} <em>({{ r.nguon }})</em>
          </li>
        </ul>
        <p v-if="blk.phu_tro?.length" class="cd-why">
          <b>Cung đối chiếu thêm:</b>
          {{ blk.phu_tro.map((p) => `${p.cung} (${p.vi_tri})`).join(" · ") }}
        </p>
        <p class="cd-para">{{ blk.paradigm_note }}</p>
      </details>
    </div>
  </section>
</template>

<style scoped>
.cd-panel { margin: 14px 0; padding: 12px 14px; border-radius: 12px;
  border: 1px solid var(--read-border, rgba(230,238,245,0.18));
  background: var(--read-surface, rgba(255,255,255,0.02)); }
.cd-head h4 { margin: 0 0 4px; font-size: calc(15px * var(--reading-scale, 1)); }
.cd-sub { margin: 0 0 10px; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-faint, rgba(230,238,245,0.62)); }
.cd-chips { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 10px; }
.cd-chip { display: inline-flex; align-items: center; gap: 5px; padding: 5px 11px; cursor: pointer;
  border-radius: 999px; border: 1px solid var(--read-border, rgba(230,238,245,0.22));
  background: transparent; color: var(--read-text-dim, rgba(230,238,245,0.85));
  font-size: calc(12.5px * var(--reading-scale, 1)); }
.cd-chip.on { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3);
  background: rgba(126,200,227,0.08); font-weight: 600; }
.cd-ic { font-size: 1.05em; }
.cd-center { margin: 6px 0 10px; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-dim, rgba(230,238,245,0.85)); }
.cd-center em { font-style: normal; opacity: 0.7; font-size: 0.92em; }
.cd-p { margin: 0 0 9px; line-height: 1.75; font-size: calc(13.5px * var(--reading-scale, 1)); }
.cd-chom { margin-top: 12px; }
.cd-chom h5 { margin: 0 0 6px; font-size: calc(13px * var(--reading-scale, 1));
  color: var(--read-text-faint, rgba(230,238,245,0.62)); font-weight: 600; }
.cd-item { padding: 6px 10px; margin-bottom: 5px; border-radius: 8px;
  border-left: 3px solid var(--read-border, rgba(230,238,245,0.25));
  background: var(--read-bg, rgba(255,255,255,0.015));
  font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; }
.cd-item small { display: block; margin-top: 2px; color: var(--read-text-faint, rgba(230,238,245,0.58)); }
.cd-rel { display: inline-block; margin-right: 6px; padding: 1px 7px; border-radius: 999px;
  background: rgba(126,200,227,0.12); color: var(--read-accent, #7ec8e3); font-size: 0.85em; }
.cd-note, .cd-err, .cd-luuy { font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; }
.cd-note { color: var(--read-text-faint, rgba(230,238,245,0.6)); }
.cd-err { color: #d65a4a; }
.cd-luuy { margin-top: 10px; padding: 7px 10px; border-radius: 8px;
  background: rgba(214,160,90,0.09); color: var(--read-text-dim, rgba(230,238,245,0.85)); }
.cd-src { margin-top: 12px; font-size: calc(12px * var(--reading-scale, 1)); }
.cd-src summary { cursor: pointer; color: var(--read-text-faint, rgba(230,238,245,0.6)); }
.cd-src ul { margin: 8px 0; padding-left: 18px; line-height: 1.65; }
.cd-src em { opacity: 0.65; }
.cd-why, .cd-para { line-height: 1.6; color: var(--read-text-faint, rgba(230,238,245,0.62)); }
.cd-para { margin-top: 8px; font-style: italic; }
</style>
