<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { activePerson } from "../stores/userDataStore.js";

// ── Thời cuộc Nguyên-Hội-Vận-Thế ─────────────────────────────────────────
const nowYear = new Date().getFullYear();
const year = ref(nowYear);
const birthYear = ref(null); // tự lấy từ người đang xem (lá số); vẫn cho sửa tay
const viTri = ref(null);
const namQue = ref(null);    // năm-quẻ theo PHÉP 经世 (hệ duy nhất, mọi năm)
const atoms = ref([]);

// Người đang active = cùng lá số Tử Vi/Bát Tự → tự điền tuổi, không bắt gõ
const personName = computed(() => activePerson.value?.name || "");
const personBirthYear = computed(() => {
  const p = activePerson.value;
  if (!p) return null;
  if (p.birth_year) return Number(p.birth_year);
  const m = (p.birth_datetime_local || "").match(/^(\d{4})/);
  return m ? Number(m[1]) : null;
});
const age = computed(() => (birthYear.value ? nowYear - Number(birthYear.value) : null));

// Đồ năm — lá số lưu niên (3 lớp) cho người đang active, theo `year`
const doNamUrl = computed(() => {
  const bd = activePerson.value?.birth_datetime_local;
  if (!bd) return null;
  const g = activePerson.value?.gender || "nam";
  return `/api/hoang-cuc/do-nam.svg?birth=${encodeURIComponent(bd)}&gender=${encodeURIComponent(g)}&year=${year.value}`;
});
const loadingViTri = ref(false);
const errViTri = ref("");
const lifeMarks = ref([]);

async function locate() {
  loadingViTri.value = true;
  errViTri.value = "";
  lifeMarks.value = [];
  try {
    const r = await fetch(`/api/hoang-cuc/the-cuc?year=${year.value}&atoms=true`);
    const d = await r.json();
    if (!r.ok || d.status !== "ok") throw new Error(d.detail || "Lỗi định vị");
    viTri.value = d.vi_tri;
    namQue.value = d.nam_que || null;
    atoms.value = d.atoms_lien_quan || [];
    // overlay đời: các thế từ năm sinh → năm sinh + 90
    if (birthYear.value) {
      const tl = await fetch(`/api/hoang-cuc/timeline?start=${birthYear.value}&end=${Number(birthYear.value) + 90}`);
      const td = await tl.json();
      if (tl.ok && td.status === "ok") lifeMarks.value = td.marks || [];
    }
  } catch (e) {
    errViTri.value = String(e.message || e);
    viTri.value = null;
  } finally {
    loadingViTri.value = false;
  }
}

// ── Tra Thiết Bản Thần Số ────────────────────────────────────────────────
const tbStats = ref(null);
const tbSeq = ref(null);
const tbVerse = ref(null);
const tbQuery = ref("");
const tbResults = ref([]);
const tbMode = ref("");
const tbErr = ref("");
const loadingTb = ref(false);

async function traSo() {
  if (!tbSeq.value) return;
  loadingTb.value = true;
  tbErr.value = "";
  tbResults.value = [];
  try {
    const r = await fetch(`/api/thiet-ban/verse/${tbSeq.value}`);
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Không tìm thấy");
    tbVerse.value = d.verse;
  } catch (e) {
    tbErr.value = String(e.message || e);
    tbVerse.value = null;
  } finally {
    loadingTb.value = false;
  }
}

async function timKiem() {
  if (!tbQuery.value.trim()) return;
  loadingTb.value = true;
  tbErr.value = "";
  tbVerse.value = null;
  try {
    const r = await fetch(`/api/thiet-ban/search?q=${encodeURIComponent(tbQuery.value)}`);
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Lỗi tìm kiếm");
    tbResults.value = d.results || [];
    tbMode.value = d.mode;
  } catch (e) {
    tbErr.value = String(e.message || e);
  } finally {
    loadingTb.value = false;
  }
}

// ── Lập số Thiết Bản từ NGÀY SINH (本命 + 流年) ───────────────────────────
const tbBirth = ref("");
const tbGender = ref("nam");
const tbMaxAge = ref(60);
const tbLap = ref(null);
const tbLapLoading = ref(false);
const tbLapErr = ref("");

function syncTbBirthFromPerson() {
  const bd = activePerson.value?.birth_datetime_local;
  if (bd && !tbBirth.value) tbBirth.value = String(bd).slice(0, 16);
  if (activePerson.value?.gender) tbGender.value = activePerson.value.gender;
}

async function lapSo() {
  if (!tbBirth.value) { tbLapErr.value = "Cần ngày + giờ sinh."; return; }
  tbLapLoading.value = true; tbLapErr.value = ""; tbLap.value = null;
  try {
    const r = await fetch("/api/thiet-ban/lap-so", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth_datetime_local: tbBirth.value, gender: tbGender.value, max_age: tbMaxAge.value }),
    });
    const d = await r.json();
    if (!r.ok || d.status !== "ok") throw new Error(d.detail || "Lỗi lập số");
    tbLap.value = d;
  } catch (e) {
    tbLapErr.value = String(e.message || e);
  } finally {
    tbLapLoading.value = false;
  }
}

// ── Đa phép Thiết Bản (卦中取数 / 元会运世) + 考刻 lục thân ──────────────────
const tbMulti = ref(null);          // { quai_trung, nguyen_hoi }
const tbMultiLoading = ref(false);
const tbChaChi = ref("");           // địa chi năm sinh CHA (考刻)
const tbMeChi = ref("");            // địa chi năm sinh MẸ
const tbKaoKhac = ref(null);
const CHI12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];

async function daPhep() {
  if (!tbBirth.value) { tbLapErr.value = "Cần ngày + giờ sinh."; return; }
  tbMultiLoading.value = true; tbLapErr.value = ""; tbMulti.value = null;
  try {
    const hdr = { "Content-Type": "application/json" };
    const opt = { method: "POST", headers: hdr, body: JSON.stringify({ birth_datetime_local: tbBirth.value }) };
    const optG = { method: "POST", headers: hdr, body: JSON.stringify({ birth_datetime_local: tbBirth.value, gender: tbGender.value }) };
    const [qt, nh, gt, ts, tht] = await Promise.all([
      fetch("/api/thiet-ban/quai-trung", opt).then((r) => r.json()),
      fetch("/api/thiet-ban/nguyen-hoi-van-the", opt).then((r) => r.json()),
      fetch("/api/thiet-ban/bat-quai-gia-tac", opt).then((r) => r.json()),
      fetch("/api/thiet-ban/truoc-sau-que", opt).then((r) => r.json()),
      fetch("/api/thiet-ban/tien-hau-thien", optG).then((r) => r.json()),
    ]);
    tbMulti.value = { quai_trung: qt, nguyen_hoi: nh, gia_tac: gt, truoc_sau: ts, tien_hau: tht };
  } catch (e) { tbLapErr.value = String(e.message || e); }
  finally { tbMultiLoading.value = false; }
}

async function kaoKhac() {
  if (!tbBirth.value) { tbLapErr.value = "Cần ngày + giờ sinh."; return; }
  tbMultiLoading.value = true; tbLapErr.value = ""; tbKaoKhac.value = null;
  try {
    const r = await fetch("/api/thiet-ban/kao-khac", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_datetime_local: tbBirth.value,
        cha_chi: tbChaChi.value || null, me_chi: tbMeChi.value || null,
      }),
    });
    const d = await r.json();
    if (!r.ok || d.status !== "ok") throw new Error(d.detail || "Lỗi 考刻");
    tbKaoKhac.value = d;
  } catch (e) { tbLapErr.value = String(e.message || e); }
  finally { tbMultiLoading.value = false; }
}

// ── 大运 / 流年 取数 ──────────────────────────────────────────────────────
const tbVanNien = ref(null);
const tbDich = ref({});            // {so: {dich, binh}} — bản dịch + lời bình sage Thiết Bản
const tbDichLoading = ref(false);
const tbDichErr = ref("");
const tbLuuNienAge = ref(30);
async function vanNien() {
  if (!tbBirth.value) { tbLapErr.value = "Cần ngày + giờ sinh."; return; }
  tbMultiLoading.value = true; tbLapErr.value = ""; tbVanNien.value = null;
  try {
    const hdr = { "Content-Type": "application/json" };
    const [dv, ln] = await Promise.all([
      fetch("/api/thiet-ban/dai-van-so", { method: "POST", headers: hdr,
        body: JSON.stringify({ birth_datetime_local: tbBirth.value, gender: tbGender.value }) }).then((r) => r.json()),
      fetch("/api/thiet-ban/luu-nien-so", { method: "POST", headers: hdr,
        body: JSON.stringify({ birth_datetime_local: tbBirth.value, from_age: tbLuuNienAge.value, to_age: tbLuuNienAge.value + 9 }) }).then((r) => r.json()),
    ]);
    tbVanNien.value = { dai_van: dv, luu_nien: ln };
  } catch (e) { tbLapErr.value = String(e.message || e); }
  finally { tbMultiLoading.value = false; }
}

// Gom mọi điều văn {so, zh} từ kết quả (đệ quy, dedup theo so) → sage dịch + lời bình.
function _collectVerses(obj, acc, seen) {
  if (Array.isArray(obj)) { for (const x of obj) _collectVerses(x, acc, seen); return acc; }
  if (obj && typeof obj === "object") {
    const zh = obj.dieu_van;
    if (obj.so != null && typeof zh === "string" && zh && zh !== "—" && !seen.has(obj.so)) {
      seen.add(obj.so); acc.push({ so: obj.so, zh });
    }
    for (const v of Object.values(obj)) _collectVerses(v, acc, seen);
  }
  return acc;
}
async function dichDieuVan() {
  const items = _collectVerses(tbVanNien.value, [], new Set());
  if (!items.length) { tbDichErr.value = "Chưa có điều văn để dịch (bấm Vận niên trước)."; return; }
  tbDichLoading.value = true; tbDichErr.value = "";
  try {
    const r = await fetch("/api/thiet-ban/luan-dieu-van", {
      method: "POST", headers: { "Content-Type": "application/json" },
      credentials: "include", body: JSON.stringify({ items }),
    });
    const d = await r.json();
    if (!r.ok) { tbDichErr.value = d.detail || `Lỗi ${r.status}`; return; }
    tbDich.value = { ...tbDich.value, ...(d.luan || {}) };
    if (d.error) tbDichErr.value = d.error;          // provider lỗi → báo rõ, không im lặng
  } catch (e) { tbDichErr.value = String(e.message || e); }
  finally { tbDichLoading.value = false; }
}

function syncBirthFromPerson() {
  if (personBirthYear.value) birthYear.value = personBirthYear.value;
}

onMounted(async () => {
  try {
    const r = await fetch("/api/thiet-ban/stats");
    if (r.ok) tbStats.value = await r.json();
  } catch { /* stats là trang trí — lỗi không chặn panel */ }
  syncBirthFromPerson();
  syncTbBirthFromPerson();
  locate();
});

// Đổi người đang xem → tự cập nhật tuổi + định vị lại
watch(activePerson, () => { syncBirthFromPerson(); syncTbBirthFromPerson(); locate(); });
</script>

<template>
  <div class="hoang-cuc-panel">
    <!-- A. Thời cuộc -->
    <div class="hc-card">
      <h3>🌌 Thời cuộc — Nguyên · Hội · Vận · Thế</h3>
      <p class="hc-hint">
        Đặt một năm vào chu kỳ 129.600 năm của Thiệu Khang Tiết. Mốc quy chiếu (đoạn 以运经世
        bộ trọn): Giáp Tý 304 CN = hội Ngọ 7 · vận 188 · thế 2245 · năm-quẻ 革 Cách.
      </p>
      <div class="hc-form">
        <label>Năm <input type="number" v-model.number="year" min="-64815" max="64784" /></label>
        <label>Năm sinh (tự lấy từ lá số — sửa được)
          <input type="number" v-model.number="birthYear" placeholder="vd 1988" /></label>
        <button @click="locate" :disabled="loadingViTri">{{ loadingViTri ? "Đang định vị…" : "Định vị" }}</button>
      </div>
      <p v-if="errViTri" class="hc-err">{{ errViTri }}</p>

      <div v-if="age !== null" class="hc-me">
        👤 <strong>{{ personName || "Anh" }}</strong> · sinh {{ birthYear }} · <strong>{{ age }} tuổi</strong> (năm {{ nowYear }})
        <span class="hc-me-note">— lá số nói <b>LÀ AI</b>; Hoàng Cực nói đang ở <b>MÙA NÀO</b></span>
      </div>

      <div v-if="doNamUrl" class="hc-donam">
        <div class="hc-donam-title">🗺️ Đồ năm {{ year }} — lá số lưu niên (3 lớp: năm-quẻ · Đại Vận · tứ hóa năm)</div>
        <img :src="doNamUrl" :alt="`Đồ năm ${year}`" loading="lazy" />
      </div>

      <div v-if="viTri" class="hc-result">
        <div class="hc-pos">
          <div class="hc-pos-line"><strong>{{ viTri.year }} ({{ viTri.can_chi }})</strong></div>
          <div class="hc-pos-line">{{ viTri.nguyen.label }} · {{ viTri.nguyen.start }} → {{ viTri.nguyen.end }}</div>
          <div class="hc-pos-line">☀ {{ viTri.hoi.label }} <em v-if="viTri.hoi.note">— {{ viTri.hoi.note }}</em></div>
          <div class="hc-pos-line">⟳ {{ viTri.van.label }} ({{ viTri.van.start }} → {{ viTri.van.end }})</div>
          <div class="hc-pos-line">◈ {{ viTri.the.label }} ({{ viTri.the.start }} → {{ viTri.the.end }}) — năm thứ {{ viTri.the.nam_trong_the }}/30</div>
          <div class="hc-pos-line hc-namque" v-if="namQue">🎴 Năm-quẻ {{ year }}<span v-if="birthYear"> · Anh {{ year - birthYear }} tuổi</span>:
            <strong>{{ namQue.han }} {{ namQue.viet }}</strong>
            <em>(phép 经世 · thế-quẻ {{ namQue.the_que }} · kiểm 10/10 chính văn 304-313)</em></div>
          <div class="hc-pos-line hc-pending" v-else>Năm-quẻ: chưa có trong nguồn (ngoài 304–313 &amp; 2020–2103) — không suy diễn</div>
        </div>

        <div v-if="lifeMarks.length" class="hc-life">
          <h4>Đời mình trong dòng thế (từ {{ birthYear }})</h4>
          <div class="hc-life-track">
            <div v-for="m in lifeMarks" :key="m.the_so" class="hc-life-the"
                 :class="{ current: m.the_so === viTri.the.so_toan_nguyen }">
              <span class="hc-life-label">Thế {{ m.the_so }}</span>
              <span class="hc-life-years">{{ m.the_start }} → {{ m.the_end }}</span>
            </div>
          </div>
        </div>

        <div v-if="birthYear" class="hc-strip">
          <h4>🎴 Năm-quẻ đời mình (tô màu từng năm)</h4>
          <img class="hc-strip-img" :src="`/api/hoang-cuc/nam-que-strip.svg?birth=${birthYear}&now=${nowYear}`"
               alt="Dải năm-quẻ đời mình" loading="lazy" />
        </div>

        <div v-if="atoms.length" class="hc-atoms">
          <h4>📖 Sách nói (atoms trích từ 皇极经世书今说)</h4>
          <div v-for="a in atoms" :key="a.atom_id" class="hc-atom">
            <div class="hc-atom-q">{{ a.question }}</div>
            <blockquote v-if="a.quote">{{ a.quote }} <cite>— tr.{{ a.page }}</cite></blockquote>
          </div>
        </div>

        <p class="hc-paradigm">☯ Đọc đồng dạng: vị trí phản chiếu CẤU TRÚC thời đoạn — không phải lời đoán cát hung.</p>
      </div>
    </div>

    <!-- B0. Lập số Thiết Bản từ ngày sinh -->
    <div class="hc-card">
      <h3>🎴 Lập số Thiết Bản từ ngày sinh</h3>
      <p class="hc-tb-goal">
        <b>Bản mệnh + lưu niên từng tuổi</b> — tính TẤT ĐỊNH theo <b>giờ SINH</b> (không giờ hỏi).
        <span class="hc-tb-dao">Đọc cái ĐÃ ĐỊNH (THỂ) để hiểu cái nền — mệnh là dịch, người là cái biến.</span>
      </p>
      <div class="hc-form">
        <label>Ngày giờ sinh <input type="datetime-local" v-model="tbBirth" /></label>
        <label>Giới <select v-model="tbGender" class="hc-sel"><option value="nam">Nam</option><option value="nữ">Nữ</option></select></label>
        <label>Xem tới tuổi <input type="number" v-model.number="tbMaxAge" min="1" max="108" /></label>
        <button @click="lapSo" :disabled="tbLapLoading">{{ tbLapLoading ? "Đang lập…" : "Lập số" }}</button>
      </div>
      <p v-if="tbLapErr" class="hc-err">{{ tbLapErr }}</p>

      <div v-if="tbLap" class="hc-lapso">
        <div class="hc-bm-head">
          Bát tự: <b>{{ tbLap.ban_menh.bat_tu_sinh }}</b> · {{ tbLap.ban_menh.am_lich }} ·
          先天 <b>{{ tbLap.ban_menh.tien_thien_menh_so }}</b> · 五音 {{ tbLap.ban_menh.ngu_am }} ·
          本命数 <b>{{ tbLap.ban_menh.ban_menh_so }}</b> · 辟卦 <b>{{ tbLap.ban_menh.thap_nhi_tich_quai || "—" }}</b> · {{ tbLap.ban_menh.khao_khac }}
        </div>

        <div v-if="tbLap.ban_menh.ban_menh_dieu_van" class="hc-dv-block">
          <h4>📜 Bản mệnh (cái đã định)</h4>
          <template v-for="(m,i) in tbLap.ban_menh.ban_menh_dieu_van.muc" :key="i">
            <div v-if="m.dieu_van" class="hc-dv-row">
              <span class="hc-dv-muc">{{ m.muc }}</span>
              <span class="hc-dv-zh">{{ m.dieu_van }}</span>
              <span class="hc-conf">#{{ m.so }}</span>
            </div>
          </template>
        </div>
        <p v-else class="hc-pending">Bản mệnh điều văn: 秘数 cho 辟卦 này chưa khôi phục đủ — không bịa số.</p>

        <div v-if="tbLap.luu_nien && tbLap.luu_nien.luu_nien" class="hc-dv-block">
          <h4>🗓️ Lưu niên từng tuổi <span class="hc-pending">(tất định theo giờ sinh)</span></h4>
          <template v-for="x in tbLap.luu_nien.luu_nien" :key="x.tuoi">
            <div v-if="x.dieu_van" class="hc-dv-row">
              <span class="hc-dv-muc">{{ x.tuoi }} tuổi</span>
              <span class="hc-dv-zh">{{ x.dieu_van }}</span>
              <span class="hc-conf">#{{ x.so }}</span>
            </div>
          </template>
        </div>
        <p class="hc-tb-dao">{{ tbLap.ban_menh.paradigm }}</p>
      </div>
    </div>

    <!-- B0b. Đa phép Thiết Bản (卦中取数 / 元会运世) -->
    <div class="hc-card" v-if="tbBirth || tbMulti">
      <h3>🧮 Đa phép Thiết Bản (cùng giờ sinh)</h3>
      <p class="hc-hint">Mỗi phép soi một góc cái ĐÃ ĐỊNH — 卦中取数 (年月·日时) + 元会运世 (khung Thiệu Ung).</p>
      <button @click="daPhep" :disabled="tbMultiLoading">{{ tbMultiLoading ? "Đang tính…" : "Chạy đa phép" }}</button>
      <div v-if="tbMulti" class="hc-lapso">
        <div v-if="tbMulti.quai_trung && tbMulti.quai_trung.dieu_van" class="hc-dv-block">
          <h4>📜 卦中取数法 <span class="hc-pending">(4 điều, cặp kiểm 4/4)</span></h4>
          <div v-for="(m,i) in tbMulti.quai_trung.dieu_van" :key="'qt'+i" class="hc-dv-row">
            <span class="hc-dv-muc">{{ m.que }} · {{ m.nhan }}</span>
            <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
            <span class="hc-conf">#{{ m.so }}</span>
          </div>
        </div>
        <div v-if="tbMulti.gia_tac && tbMulti.gia_tac.quai" class="hc-dv-block">
          <h4>➕ 八卦加则法 <span class="hc-pending">(4 quẻ năm/tháng/ngày/giờ)</span></h4>
          <div v-for="(m,i) in tbMulti.gia_tac.quai" :key="'gt'+i" class="hc-dv-row">
            <span class="hc-dv-muc">{{ m.tru }} · {{ m.que }}</span>
            <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
            <span class="hc-conf">#{{ m.so }}</span>
          </div>
        </div>
        <div v-if="tbMulti.nguyen_hoi" class="hc-dv-block">
          <h4>🌌 元会运世法 <span class="hc-pending">元{{ tbMulti.nguyen_hoi.nguyen_so }} 会{{ tbMulti.nguyen_hoi.hoi_so }} 运{{ tbMulti.nguyen_hoi.van_so }} 世{{ tbMulti.nguyen_hoi.the_so }}</span></h4>
          <div v-for="(m,i) in [...tbMulti.nguyen_hoi.dieu_van_nguyen_hoi, ...tbMulti.nguyen_hoi.dieu_van_van_the]" :key="'nh'+i" class="hc-dv-row">
            <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
            <span class="hc-conf">#{{ m.so }}</span>
          </div>
        </div>
        <div v-if="tbMulti.truoc_sau && tbMulti.truoc_sau.dieu_van_truoc" class="hc-dv-block">
          <h4>🀄 前后卦取数法 <span class="hc-pending">前 {{ tbMulti.truoc_sau.truoc_que }} · 后 {{ tbMulti.truoc_sau.sau_que }}</span></h4>
          <div v-for="(m,i) in [...tbMulti.truoc_sau.dieu_van_truoc, ...tbMulti.truoc_sau.dieu_van_sau]" :key="'ts'+i" class="hc-dv-row">
            <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
            <span class="hc-conf">#{{ m.so }}</span>
          </div>
        </div>
        <div v-if="tbMulti.tien_hau && tbMulti.tien_hau.dieu_van_tien_thien" class="hc-dv-block">
          <h4>☯ 先后天卦八卦加则 <span class="hc-pending">先天 {{ tbMulti.tien_hau.tien_thien_que }} · 后天 {{ tbMulti.tien_hau.hau_thien_que }}</span></h4>
          <div v-for="(m,i) in [...tbMulti.tien_hau.dieu_van_tien_thien, ...tbMulti.tien_hau.dieu_van_hau_thien]" :key="'tht'+i" class="hc-dv-row">
            <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
            <span class="hc-conf">#{{ m.so }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- B0c. 考刻 lục thân -->
    <div class="hc-card" v-if="tbBirth || tbKaoKhac">
      <h3>🔍 考刻 — neo khắc bằng lục thân</h3>
      <p class="hc-tb-dao">乾坤流度数法: 年柱 → 父母爻 → sinh tiêu cha/mẹ. Đỉnh cao chính xác Thiết Bản — cấp sinh tiêu cha/mẹ để xác nhận khắc sinh (考刻).</p>
      <div class="hc-form">
        <label>Cha tuổi <select v-model="tbChaChi" class="hc-sel"><option value="">—</option><option v-for="c in CHI12" :key="c" :value="c">{{ c }}</option></select></label>
        <label>Mẹ tuổi <select v-model="tbMeChi" class="hc-sel"><option value="">—</option><option v-for="c in CHI12" :key="c" :value="c">{{ c }}</option></select></label>
        <button @click="kaoKhac" :disabled="tbMultiLoading">考刻</button>
      </div>
      <div v-if="tbKaoKhac" class="hc-lapso">
        <div class="hc-bm-head">年柱 <b>{{ tbKaoKhac.nam_tru }}</b> → quẻ <b>{{ tbKaoKhac.que }}</b> · 父母爻 <b>{{ tbKaoKhac.phu_mau_chi }}</b> → dự đoán cha/mẹ tuổi <b>{{ tbKaoKhac.sinh_tieu_du_doan }}</b></div>
        <div class="hc-dv-row"><span class="hc-dv-muc">CHA (乾宫)</span><span class="hc-dv-zh">{{ tbKaoKhac.cha && tbKaoKhac.cha.dieu_van_chuan }}</span><span class="hc-conf">#{{ tbKaoKhac.cha && tbKaoKhac.cha.mat_so }}</span></div>
        <div class="hc-dv-row"><span class="hc-dv-muc">MẸ (坤宫)</span><span class="hc-dv-zh">{{ tbKaoKhac.me && tbKaoKhac.me.dieu_van_chuan }}</span><span class="hc-conf">#{{ tbKaoKhac.me && tbKaoKhac.me.mat_so }}</span></div>
        <div v-if="tbKaoKhac.phu_mau_hoa_que" class="hc-dv-row">
          <span class="hc-dv-muc">父母生肖化卦</span>
          <span class="hc-dv-zh">{{ tbKaoKhac.phu_mau_hoa_que.dieu_van || "—" }}</span>
          <span class="hc-conf">#{{ tbKaoKhac.phu_mau_hoa_que.so }}</span>
        </div>
        <p :class="tbKaoKhac.ket_qua==='khớp' ? 'hc-tb-dao' : 'hc-pending'">{{ tbKaoKhac.ket_qua==='khớp' ? ('✓ ' + (tbKaoKhac.khop||[]).join('; ')) : (tbKaoKhac.ghi_chu || tbKaoKhac.ket_qua) }}</p>
      </div>
    </div>

    <!-- B0d. 大运 / 流年 取数 -->
    <div class="hc-card" v-if="tbBirth || tbVanNien">
      <h3>📅 大运 / 流年 取数</h3>
      <p class="hc-hint">Khung VẬN (đại vận 10 năm) + NIÊN (lưu niên từng năm) — đọc cái ĐÃ ĐỊNH theo thời, không phán.</p>
      <div class="hc-form">
        <label>Lưu niên từ tuổi <input type="number" v-model.number="tbLuuNienAge" min="1" max="110" /></label>
        <button @click="vanNien" :disabled="tbMultiLoading">{{ tbMultiLoading ? "Đang tính…" : "Tính vận/niên" }}</button>
      </div>
      <div v-if="tbVanNien" class="hc-lapso">
        <div class="hc-dich-bar">
          <button class="hc-dich-btn" :disabled="tbDichLoading" @click="dichDieuVan">
            {{ tbDichLoading ? "Sage đang dịch…" : "🔩 Dịch + lời bình (sage Thiết Bản)" }}
          </button>
          <span class="hc-pending">Dịch điều văn cổ văn → tiếng Việt + lời bình (đọc đồng dạng, không tiên tri). Dịch 1 lần lưu lại.</span>
          <span v-if="tbDichErr" class="hc-dich-err">⚠ {{ tbDichErr }}</span>
        </div>
        <div v-if="tbVanNien.dai_van && tbVanNien.dai_van.dai_van" class="hc-dv-block">
          <h4>🔟 大运 (8 đại vận) <span class="hc-pending">基本数 {{ tbVanNien.dai_van.basic_so }}</span></h4>
          <template v-for="(v,i) in tbVanNien.dai_van.dai_van" :key="'dv'+i">
            <div v-for="(m,j) in v.dieu_van" :key="'dv'+i+'_'+j" class="hc-dv-row">
              <span class="hc-dv-muc">{{ v.van }} · {{ v.tuoi }}t</span>
              <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
              <span class="hc-conf">#{{ m.so }}</span>
              <div v-if="tbDich[m.so]" class="hc-dv-luan">
                <div class="hc-dv-vi">{{ tbDich[m.so].dich }}</div>
                <div v-if="tbDich[m.so].binh" class="hc-dv-binh">{{ tbDich[m.so].binh }}</div>
              </div>
            </div>
          </template>
        </div>
        <div v-if="tbVanNien.luu_nien && tbVanNien.luu_nien.luu_nien" class="hc-dv-block">
          <h4>📆 流年 (10 năm)</h4>
          <template v-for="(x,i) in tbVanNien.luu_nien.luu_nien" :key="'ln'+i">
            <div v-for="(m,j) in x.dieu_van" :key="'ln'+i+'_'+j" class="hc-dv-row">
              <span class="hc-dv-muc">{{ x.tuoi }}t · {{ x.nam }} {{ x.can_chi }}</span>
              <span class="hc-dv-zh">{{ m.dieu_van || "—" }}</span>
              <span class="hc-conf">#{{ m.so }}</span>
              <div v-if="tbDich[m.so]" class="hc-dv-luan">
                <div class="hc-dv-vi">{{ tbDich[m.so].dich }}</div>
                <div v-if="tbDich[m.so].binh" class="hc-dv-binh">{{ tbDich[m.so].binh }}</div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- B. Tra Thiết Bản -->
    <div class="hc-card">
      <h3>🔢 Tra điều văn Thiết Bản Thần Số</h3>
      <p class="hc-tb-goal">
        <b>Mục đích:</b> soi những điều <b>đã định</b> của một đời theo <b>từng tuổi</b> — để HIỂU cái nền mình được trao, không phải để sợ.
        <span class="hc-tb-dao">Đọc đúng đạo: đây là <b>bàn tay được chia</b> (cái nền), không phải bản án — mệnh là dịch, người là cái biến.</span>
      </p>
      <p class="hc-hint" v-if="tbStats">
        Bảng tra {{ tbStats.total?.toLocaleString() }} điều (số {{ tbStats.seq_range?.[0] }}–{{ tbStats.seq_range?.[1] }}),
        {{ tbStats.with_vi?.toLocaleString() }} điều có bản dịch. Phép TÍNH số từ ngày sinh: đã bật (ô "🎴 Lập số" phía trên).
      </p>
      <div class="hc-form">
        <label>Số điều <input type="number" v-model.number="tbSeq" placeholder="vd 1002" min="991" max="12990"
               @keyup.enter="traSo" /></label>
        <button @click="traSo" :disabled="loadingTb">Tra số</button>
        <label class="hc-grow">Hoặc tìm theo nội dung (Việt / Hán)
          <input type="text" v-model="tbQuery" placeholder="vd: huynh đệ / 兄弟" @keyup.enter="timKiem" /></label>
        <button @click="timKiem" :disabled="loadingTb">Tìm</button>
      </div>
      <p v-if="tbErr" class="hc-err">{{ tbErr }}</p>

      <div v-if="tbVerse" class="hc-verse">
        <div class="hc-verse-no">Điều {{ tbVerse.seq_no }} <span v-if="tbVerse.volume">· {{ tbVerse.volume }}</span>
          <span class="hc-conf" :data-conf="tbVerse.confidence">{{ tbVerse.confidence }}</span></div>
        <div class="hc-verse-zh">{{ tbVerse.zh }}</div>
        <div class="hc-verse-vi" v-if="tbVerse.vi">{{ tbVerse.vi }}</div>
        <div class="hc-verse-vi hc-pending" v-else>(chưa có bản dịch — sẽ bổ sung)</div>
        <div class="hc-verse-meta" v-if="tbVerse.age_marks">Tuổi ứng (cột nhỏ nguyên bản): {{ tbVerse.age_marks }}</div>
      </div>

      <div v-if="tbResults.length" class="hc-search-results">
        <div class="hc-hint">{{ tbResults.length }} kết quả ({{ tbMode }})</div>
        <div v-for="r in tbResults" :key="r.seq_no" class="hc-verse hc-verse-row"
             @click="tbSeq = r.seq_no; traSo()">
          <span class="hc-verse-no">#{{ r.seq_no }}</span>
          <span class="hc-verse-zh">{{ r.zh }}</span>
          <span class="hc-verse-vi" v-if="r.vi">{{ r.vi }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hoang-cuc-panel { display: flex; flex-direction: column; gap: 16px; }
.hc-card { background: var(--card-bg, rgba(255,255,255,.04)); border: 1px solid var(--border-color, rgba(255,255,255,.1)); border-radius: 12px; padding: 16px; }
.hc-card h3 { margin: 0 0 6px; }
.hc-hint { font-size: .85rem; opacity: .75; margin: 4px 0 10px; }
.hc-form { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; }
.hc-form label { display: flex; flex-direction: column; font-size: .8rem; gap: 4px; }
.hc-form input { padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border-color, rgba(255,255,255,.15)); background: transparent; color: inherit; min-width: 110px; }
.hc-grow { flex: 1; min-width: 200px; }
.hc-grow input { width: 100%; }
.hc-form button { padding: 8px 16px; border-radius: 8px; border: none; background: var(--accent, #7c5cff); color: #fff; cursor: pointer; }
.hc-form button:disabled { opacity: .5; }
.hc-err { color: #ff7676; font-size: .85rem; }
.hc-pos { margin-top: 12px; display: flex; flex-direction: column; gap: 4px; }
.hc-pos-line { font-size: .95rem; }
.hc-pending { opacity: .6; font-style: italic; font-size: .82rem; }
.hc-life { margin-top: 14px; }
.hc-life-track { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.hc-life-the { border: 1px solid var(--border-color, rgba(255,255,255,.15)); border-radius: 8px; padding: 6px 10px; font-size: .78rem; display: flex; flex-direction: column; }
.hc-life-the.current { border-color: var(--accent, #7c5cff); background: rgba(124,92,255,.12); }
.hc-life-years { opacity: .7; }
.hc-atoms { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.hc-atom-q { font-weight: 600; font-size: .9rem; }
.hc-atom blockquote { margin: 4px 0 0; padding-left: 10px; border-left: 3px solid var(--accent, #7c5cff); font-size: .85rem; opacity: .85; }
.hc-me { margin-top: 12px; padding: 8px 12px; border-radius: 10px; background: rgba(124,92,255,.10); border: 1px solid var(--accent, #7c5cff); font-size: .92rem; }
.hc-me-note { display: block; font-size: .78rem; opacity: .72; margin-top: 2px; font-style: italic; }
.hc-sel { padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border-color, rgba(255,255,255,.15)); background: transparent; color: inherit; }
.hc-sel option { color: #222; }
.hc-lapso { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.hc-bm-head { font-size: .9rem; padding: 8px 12px; border-radius: 10px; background: rgba(124,92,255,.10); border: 1px solid var(--accent, #7c5cff); line-height: 1.7; }
.hc-dv-block h4 { margin: 4px 0 6px; font-size: .92rem; }
.hc-dv-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; padding: 5px 0; border-bottom: 1px dashed var(--border-color, rgba(255,255,255,.1)); font-size: .9rem; }
/* Dịch + lời bình sage Thiết Bản (xuống dòng riêng dưới điều văn zh) */
.hc-dich-bar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 4px 0 12px; }
.hc-dich-btn { padding: 7px 14px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;
  background: linear-gradient(135deg, #b45309, #d97706); color: #fff; box-shadow: 0 2px 8px rgba(180,83,9,.3); }
.hc-dich-btn:disabled { opacity: .6; cursor: wait; }
.hc-dich-err { color: #f87171; font-size: .85rem; }
.hc-dv-luan { flex-basis: 100%; margin: 4px 0 2px 0; padding: 6px 10px; border-left: 2px solid #d97706;
  background: rgba(217,119,6,.08); border-radius: 0 6px 6px 0; }
.hc-dv-vi { font-size: .92rem; line-height: 1.55; }
.hc-dv-binh { font-size: .85rem; opacity: .82; margin-top: 4px; font-style: italic; line-height: 1.5; }
.hc-dv-muc { flex: 0 0 92px; opacity: .7; font-size: .8rem; }
.hc-dv-zh { flex: 1; }
.hc-tb-goal { font-size: .85rem; opacity: .85; margin: 4px 0 10px; line-height: 1.55; }
.hc-tb-dao { display: block; font-size: .8rem; opacity: .7; font-style: italic; margin-top: 4px; }
.hc-namque { color: var(--accent, #7c5cff); }
.hc-namque em { opacity: .7; font-size: .82rem; }
.hc-namque-flat { font-size: .8rem; opacity: .6; margin: 2px 0 0 18px; }
.hc-donam { margin-top: 14px; }
.hc-donam-title { font-size: .9rem; font-weight: 600; color: var(--accent, #7c5cff); margin-bottom: 6px; }
.hc-donam img { width: 100%; max-width: 980px; border: 1px solid #e0d5b8; border-radius: 10px; background: #fbf7ef; }
.hc-tb-goal { font-size: .88rem; line-height: 1.5; margin: 4px 0 8px; padding: 8px 10px; border-radius: 8px; background: rgba(124,92,255,.06); border-left: 3px solid var(--accent, #7c5cff); }
.hc-tb-dao { display: block; font-size: .8rem; opacity: .75; font-style: italic; margin-top: 3px; }
.hc-strip { margin-top: 14px; }
.hc-strip-img { width: 100%; max-width: 100%; border: 1px solid var(--border-color, rgba(255,255,255,.1)); border-radius: 10px; background: #fbf7ef; padding: 4px; box-sizing: border-box; }
.hc-paradigm { margin-top: 14px; font-size: .82rem; opacity: .7; font-style: italic; }
.hc-verse { margin-top: 12px; padding: 10px 12px; border: 1px solid var(--border-color, rgba(255,255,255,.12)); border-radius: 10px; }
.hc-verse-no { font-weight: 700; }
.hc-conf { font-size: .7rem; opacity: .65; margin-left: 8px; border: 1px solid currentColor; border-radius: 6px; padding: 1px 6px; }
.hc-verse-zh { font-size: 1.05rem; margin-top: 4px; }
.hc-verse-vi { margin-top: 4px; font-size: .92rem; opacity: .9; }
.hc-verse-meta { margin-top: 4px; font-size: .78rem; opacity: .6; }
.hc-verse-row { cursor: pointer; display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
.hc-verse-row:hover { border-color: var(--accent, #7c5cff); }
.hc-search-results { margin-top: 10px; }
</style>
