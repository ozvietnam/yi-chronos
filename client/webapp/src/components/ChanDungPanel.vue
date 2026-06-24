<script setup>
/**
 * ChanDungPanel — Trang "Chân Dung khách hàng" (Anh chốt 2026-06-24).
 * Tổng hợp DETERMINISTIC "khách LÀ AI" từ 3 lá số (Bát Tự cốt cách + Tử Vi mệnh + Chiếu Đởm nội
 * tâm) + lịch sử đã hỏi + bệ phóng tới sản phẩm tốt nhất. Đọc đồng dạng — KHÔNG predict.
 */
import { ref, computed, watch, onMounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";
import { sessionToken } from "../stores/authStore.js";

const emit = defineEmits(["open-product"]);

const cd = ref(null);
const history = ref([]);
const loading = ref(false);
const err = ref("");

const personKey = computed(() => activePerson.value?.person_key || activePerson.value?.id || "self");
const personName = computed(() => activePerson.value?.name || cd.value?.name || "Quý khách");
const hasBirth = computed(() => !!activePerson.value?.birth_datetime_local);

const HANH_COLOR = { "Mộc": "#16a34a", "Hoả": "#dc2626", "Thổ": "#ca8a04", "Kim": "#a3a3a3", "Thuỷ": "#2563eb" };
const METHOD_LABEL = {
  hermes_council: "⚖️ Hội Đồng", hermes_quick: "💭 Hỏi nhanh", mai_hoa: "🌸 Mai Hoa",
  bat_tu: "🎋 Bát Tự", tu_vi: "🌌 Tử Vi", luc_hao: "☯ Lục Hào", ha_lac: "🔢 Hà Lạc",
  lien_hoa: "🪷 Liên Hoa", cross_paradigm_couple_sync: "💞 So đôi", cross_paradigm_hon_nhan: "💞 Hôn nhân",
};
function methodLabel(m) { return METHOD_LABEL[m] || m; }
function fmtDate(ts) { try { return new Date(ts * 1000).toLocaleDateString("vi-VN"); } catch { return ""; } }

const PALACE_VI = {
  menh: "Mệnh", huynh_de: "Huynh Đệ", phu_the: "Phu Thê", tu_tuc: "Tử Tức", tai_bach: "Tài Bạch",
  tat_ach: "Tật Ách", thien_di: "Thiên Di", no_boc: "Nô Bộc", quan_loc: "Quan Lộc",
  dien_trach: "Điền Trạch", phuc_duc: "Phúc Đức", phu_mau: "Phụ Mẫu",
};
function fnLabel(fn) { return PALACE_VI[fn] || fn || ""; }
function loaiLabel(l) { return l === "hung" ? "cần lưu tâm" : (l === "cat" || l === "cát") ? "lợi thế" : (l || ""); }

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

async function load() {
  if (!hasBirth.value) { cd.value = null; return; }
  loading.value = true; err.value = "";
  try {
    const r = await fetch(`/api/chan-dung?person_key=${encodeURIComponent(personKey.value)}`,
      { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (!r.ok || d.ok === false) { err.value = d.reason || d.detail || `Lỗi ${r.status}`; cd.value = null; }
    else cd.value = d;
  } catch (e) { err.value = String(e.message || e); }
  finally { loading.value = false; }
  loadHistory();
}

async function loadHistory() {
  try {
    const r = await fetch("/api/auth/my/castings?limit=8", { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (r.ok) history.value = (d.castings || []).filter(c => !c.subject_person_key || c.subject_person_key === personKey.value);
  } catch { history.value = []; }
}

watch(activePerson, load);
onMounted(load);
</script>

<template>
  <div class="chan-dung">
    <header class="cd-head">
      <h2>🪞 Chân Dung — {{ personName }}</h2>
      <p class="cd-sub">Phản chiếu bạn LÀ AI qua ba lá số, đọc đồng dạng — <b>không phán trước cát/hung</b>.
        Mệnh là cách <b>vận hành</b> cái tính trời cho, không phải án định sẵn.</p>
    </header>

    <p v-if="!hasBirth" class="cd-empty">Chọn người có <b>giờ sinh</b> ở tab Hồ sơ để xem chân dung.</p>
    <p v-else-if="loading" class="cd-loading">Đang dựng chân dung…</p>
    <p v-else-if="err" class="cd-err">⚠ {{ err }}</p>

    <template v-else-if="cd && cd.ok">
      <!-- Cốt cách (Bát Tự) -->
      <section class="cd-card cd-cot">
        <h3>🎋 Cốt cách <small>— Bát Tự</small></h3>
        <div class="cd-nhatchu">
          <span class="cd-nc-label">{{ cd.cot_cach.nhat_chu }}</span>
          <span v-if="cd.cot_cach.hinh_anh" class="cd-nc-img">{{ cd.cot_cach.hinh_anh }}</span>
        </div>
        <p v-if="cd.cot_cach.tinh_cach" class="cd-tinhcach">{{ cd.cot_cach.tinh_cach }}</p>
        <div v-if="cd.cot_cach.ngu_hanh" class="cd-nguhanh">
          <span v-for="(n, h) in cd.cot_cach.ngu_hanh" :key="h" class="cd-hanh"
            :style="{ '--c': HANH_COLOR[h] || '#888' }">{{ h }} <b>{{ n }}</b></span>
        </div>
        <p v-if="cd.cot_cach.thieu_hanh && cd.cot_cach.thieu_hanh.length" class="cd-note">
          Thiếu: <b>{{ cd.cot_cach.thieu_hanh.join(", ") }}</b>
          <span v-if="cd.cot_cach.thua_hanh && cd.cot_cach.thua_hanh.length"> · Thừa: <b>{{ cd.cot_cach.thua_hanh.join(", ") }}</b></span>
        </p>
        <p v-if="cd.cot_cach.favorable && cd.cot_cach.favorable.colors" class="cd-fav">
          🎨 Hợp: màu {{ cd.cot_cach.favorable.colors }} · hướng {{ cd.cot_cach.favorable.direction }} · số {{ (cd.cot_cach.favorable.numbers || []).join(", ") }}
        </p>
      </section>

      <!-- Mệnh (Tử Vi) -->
      <section class="cd-card cd-menh">
        <h3>🌌 Mệnh <small>— Tử Vi Đẩu Số</small></h3>
        <div class="cd-menh-top">
          <span class="cd-pill">Mệnh tại <b>{{ cd.menh.menh_cung }}</b></span>
          <span class="cd-pill">{{ cd.menh.cuc }}</span>
          <span class="cd-pill">Mệnh chủ <b>{{ cd.menh.menh_chu }}</b></span>
          <span class="cd-pill">Thân chủ <b>{{ cd.menh.than_chu }}</b></span>
        </div>
        <div v-for="s in cd.menh.chinh_tinh_tai_menh" :key="s.sao" class="cd-sao">
          <b>{{ s.sao }}</b><span v-if="s.nghia"> — {{ s.nghia }}</span>
        </div>
        <div v-if="cd.menh.tu_hoa" class="cd-tuhoa">
          <span v-for="(star, hoa) in cd.menh.tu_hoa" :key="hoa" class="cd-hoa">Hóa {{ hoa }}: <b>{{ star }}</b></span>
        </div>
        <p v-if="cd.menh.dai_van_hien_tai" class="cd-daivan">
          ⏳ Đang ở <b>Đại Vận {{ cd.menh.dai_van_hien_tai.start_age }}–{{ cd.menh.dai_van_hien_tai.end_age }} tuổi</b>
          — vận cung {{ fnLabel(cd.menh.dai_van_hien_tai.fn) }}
        </p>
        <div v-if="cd.menh.cach_cuc && cd.menh.cach_cuc.length" class="cd-caccuc">
          <p class="cd-cc-label">Cách cục nổi bật:</p>
          <details v-for="c in cd.menh.cach_cuc" :key="c.ten" class="cd-cc">
            <summary><b>{{ c.ten }}</b> <span class="cd-cc-loai" :class="c.loai">{{ loaiLabel(c.loai) }}</span></summary>
            <p v-if="c.dieu_kien" class="cd-cc-dk">{{ c.dieu_kien }}</p>
            <p v-if="c.y_nghia" class="cd-cc-nghia">{{ c.y_nghia }}
              <span class="cd-cc-note">— nguyên văn sách cổ, đọc đồng dạng (không phải lời phán định)</span></p>
          </details>
        </div>
      </section>

      <!-- Nội tâm (Chiếu Đởm) -->
      <section v-if="cd.noi_tam && cd.noi_tam.phi_tinh_tai_menh" class="cd-card cd-noitam">
        <h3>🪞 Nội tâm <small>— Chiếu Đởm Kinh (Bắc phái)</small></h3>
        <p class="cd-noitam-body">Phi tinh tọa mệnh nội tâm: <b>{{ cd.noi_tam.phi_tinh_tai_menh.join(", ") || "—" }}</b>
          (cung {{ cd.noi_tam.menh_cung }}). Lăng kính nội tâm sâu, song hành với Tử Vi chính thống.</p>
      </section>

      <!-- Đường đời (Bát Tự gợi mở) -->
      <section v-if="cd.huong_dan && ((cd.huong_dan.su_nghiep && cd.huong_dan.su_nghiep.length) || (cd.huong_dan.loi_khuyen && cd.huong_dan.loi_khuyen.length))"
        class="cd-card cd-huongdan">
        <h3>🧭 Đường đời <small>— gợi mở từ Bát Tự</small></h3>
        <p v-if="cd.huong_dan.su_nghiep && cd.huong_dan.su_nghiep.length" class="cd-hd-row">
          <b>Hướng nghề hợp</b><span v-if="cd.huong_dan.dung_hanh"> (dụng hành {{ cd.huong_dan.dung_hanh }})</span>:
          {{ cd.huong_dan.su_nghiep.join(" · ") }}
        </p>
        <div v-if="cd.huong_dan.suc_khoe && cd.huong_dan.suc_khoe.length" class="cd-hd-row">
          <b>Sức khỏe lưu tâm:</b>
          <p v-for="s in cd.huong_dan.suc_khoe" :key="s.hanh" class="cd-hd-sk"><b>{{ s.hanh }}</b> — {{ s.note }}</p>
        </div>
        <div v-if="cd.huong_dan.loi_khuyen && cd.huong_dan.loi_khuyen.length" class="cd-hd-row">
          <b>Lời khuyên:</b>
          <ul class="cd-hd-lk"><li v-for="(l, i) in cd.huong_dan.loi_khuyen" :key="i">{{ l }}</li></ul>
        </div>
      </section>

      <!-- Hành trình -->
      <section v-if="history.length" class="cd-card cd-history">
        <h3>📜 Hành trình đã hỏi <small>({{ history.length }})</small></h3>
        <div v-for="h in history" :key="h.id" class="cd-hrow">
          <span class="cd-hmethod">{{ methodLabel(h.method) }}</span>
          <span class="cd-hq">{{ (h.question || "").slice(0, 70) || "—" }}</span>
          <span class="cd-hdate">{{ fmtDate(h.created_at) }}</span>
        </div>
      </section>

      <!-- Sản phẩm tốt nhất -->
      <section class="cd-products">
        <h3>✨ Muốn hiểu sâu hơn?</h3>
        <div class="cd-prod-grid">
          <button v-for="p in cd.products" :key="p.key" class="cd-prod" @click="emit('open-product', p.key)">
            <span class="cd-prod-icon">{{ p.icon }}</span>
            <span class="cd-prod-ten">{{ p.ten }}</span>
            <span class="cd-prod-mota">{{ p.mo_ta }}</span>
            <span class="cd-prod-cta">{{ p.cta }} · {{ p.xu }} xu →</span>
          </button>
        </div>
      </section>

      <p class="cd-paradigm">{{ cd.paradigm_note }}</p>
    </template>
  </div>
</template>

<style scoped>
.chan-dung { max-width: 920px; margin: 0 auto; color: var(--read-fg, inherit); }
.cd-head h2 { margin-bottom: .2rem; }
.cd-sub { color: var(--read-muted, #888); font-size: .9rem; line-height: 1.6; }
.cd-empty, .cd-loading, .cd-err { padding: .7rem; border-radius: 8px; }
.cd-err { color: #c2410c; background: rgba(217,119,6,.08); }
.cd-empty, .cd-loading { color: var(--read-muted, #888); }
.cd-card { border: 1px solid var(--read-border, #ddd); border-radius: 10px; padding: .9rem 1.1rem;
  margin: .9rem 0; background: var(--read-bg, transparent); }
.cd-card h3 { margin: 0 0 .6rem; font-size: 1.1rem; }
.cd-card h3 small { color: var(--read-muted, #888); font-weight: 400; font-size: .82rem; }
.cd-cot { border-left: 3px solid #16a34a; }
.cd-menh { border-left: 3px solid #7c3aed; }
.cd-noitam { border-left: 3px solid #0891b2; }
.cd-nhatchu { display: flex; align-items: baseline; gap: .6rem; }
.cd-nc-label { font-size: 1.4rem; font-weight: 800; }
.cd-nc-img { color: var(--read-muted, #888); }
.cd-tinhcach { line-height: 1.7; margin: .5rem 0; }
.cd-nguhanh { display: flex; gap: .4rem; flex-wrap: wrap; margin: .5rem 0; }
.cd-hanh { padding: .2rem .6rem; border-radius: 6px; font-size: .85rem;
  border: 1px solid var(--c); color: var(--c); }
.cd-note, .cd-fav { font-size: .88rem; color: var(--read-muted, #777); margin: .3rem 0; }
.cd-menh-top { display: flex; gap: .4rem; flex-wrap: wrap; margin-bottom: .6rem; }
.cd-pill { padding: .25rem .65rem; border-radius: 20px; font-size: .85rem;
  background: rgba(124,58,237,.1); border: 1px solid rgba(124,58,237,.25); }
.cd-sao { line-height: 1.7; margin: .35rem 0; padding-left: .5rem; border-left: 2px solid var(--read-border, #ddd); }
.cd-tuhoa { display: flex; gap: .5rem; flex-wrap: wrap; margin-top: .6rem; }
.cd-hoa { font-size: .82rem; color: var(--read-muted, #777); }
.cd-daivan { margin-top: .6rem; font-size: .9rem; padding: .4rem .6rem; border-radius: 6px;
  background: rgba(124,58,237,.08); }
.cd-caccuc { margin-top: .7rem; }
.cd-cc-label { font-size: .85rem; color: var(--read-muted, #888); margin: 0 0 .3rem; }
.cd-cc { border: 1px solid var(--read-border, #e3e3e3); border-radius: 8px; margin-bottom: .4rem; padding: .15rem .6rem; }
.cd-cc summary { cursor: pointer; padding: .4rem 0; font-size: .92rem; }
.cd-cc-loai { font-size: .72rem; padding: 1px 7px; border-radius: 10px; margin-left: .3rem; }
.cd-cc-loai.hung { background: rgba(217,119,6,.12); color: #c2410c; }
.cd-cc-loai.cat, .cd-cc-loai.cát { background: rgba(22,163,74,.12); color: #15803d; }
.cd-cc-dk { font-size: .82rem; color: var(--read-muted, #888); margin: .2rem 0; }
.cd-cc-nghia { font-size: .88rem; line-height: 1.6; margin: .2rem 0 .5rem; }
.cd-cc-note { font-size: .75rem; color: var(--read-muted, #999); font-style: italic; }
.cd-huongdan { border-left: 3px solid #ca8a04; }
.cd-hd-row { margin: .5rem 0; line-height: 1.6; font-size: .92rem; }
.cd-hd-sk { margin: .25rem 0; font-size: .88rem; color: var(--read-muted, #777); }
.cd-hd-lk { margin: .3rem 0 0; padding-left: 1.2rem; }
.cd-hd-lk li { line-height: 1.6; font-size: .9rem; margin: .15rem 0; }
.cd-noitam-body { line-height: 1.7; }
.cd-hrow { display: flex; gap: .7rem; align-items: baseline; padding: .35rem 0;
  border-bottom: 1px solid var(--read-border, #eee); font-size: .9rem; }
.cd-hmethod { white-space: nowrap; }
.cd-hq { flex: 1; color: var(--read-muted, #777); }
.cd-hdate { white-space: nowrap; color: var(--read-muted, #999); font-size: .82rem; }
.cd-products { margin: 1.2rem 0; }
.cd-products h3 { margin: 0 0 .7rem; }
.cd-prod-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: .7rem; }
.cd-prod { text-align: left; display: flex; flex-direction: column; gap: .3rem; cursor: pointer;
  border: 1px solid var(--read-border, #ddd); border-radius: 10px; padding: .8rem; background: transparent;
  color: inherit; transition: transform .12s, box-shadow .12s; }
.cd-prod:hover { transform: translateY(-2px); box-shadow: 0 4px 14px rgba(124,58,237,.18); border-color: #7c3aed; }
.cd-prod-icon { font-size: 1.5rem; }
.cd-prod-ten { font-weight: 700; }
.cd-prod-mota { font-size: .84rem; color: var(--read-muted, #777); line-height: 1.5; }
.cd-prod-cta { margin-top: .3rem; font-size: .85rem; font-weight: 600; color: #7c3aed; }
.cd-paradigm { font-size: .82rem; color: var(--read-muted, #888); font-style: italic;
  border-top: 1px dashed var(--read-border, #ccc); padding-top: .7rem; margin-top: 1rem; line-height: 1.6; }
</style>
