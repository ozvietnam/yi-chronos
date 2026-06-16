<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { activePerson } from "../stores/userDataStore.js";

// ── Thời cuộc Nguyên-Hội-Vận-Thế ─────────────────────────────────────────
const nowYear = new Date().getFullYear();
const year = ref(nowYear);
const birthYear = ref(null); // tự lấy từ người đang xem (lá số); vẫn cho sửa tay
const viTri = ref(null);
const namQue = ref(null);    // hệ flat 值年 (bảng) — chỉ 304-313 + 2020-2103
const namQuePhep = ref(null);// hệ 经世 (phép sách, mọi năm) — kiểm 10/10 chính văn
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
    namQuePhep.value = d.nam_que_phep || null;
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

function syncBirthFromPerson() {
  if (personBirthYear.value) birthYear.value = personBirthYear.value;
}

onMounted(async () => {
  try {
    const r = await fetch("/api/thiet-ban/stats");
    if (r.ok) tbStats.value = await r.json();
  } catch { /* stats là trang trí — lỗi không chặn panel */ }
  syncBirthFromPerson();
  locate();
});

// Đổi người đang xem → tự cập nhật tuổi + định vị lại
watch(activePerson, () => { syncBirthFromPerson(); locate(); });
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

      <div v-if="viTri" class="hc-result">
        <div class="hc-pos">
          <div class="hc-pos-line"><strong>{{ viTri.year }} ({{ viTri.can_chi }})</strong></div>
          <div class="hc-pos-line">{{ viTri.nguyen.label }} · {{ viTri.nguyen.start }} → {{ viTri.nguyen.end }}</div>
          <div class="hc-pos-line">☀ {{ viTri.hoi.label }} <em v-if="viTri.hoi.note">— {{ viTri.hoi.note }}</em></div>
          <div class="hc-pos-line">⟳ {{ viTri.van.label }} ({{ viTri.van.start }} → {{ viTri.van.end }})</div>
          <div class="hc-pos-line">◈ {{ viTri.the.label }} ({{ viTri.the.start }} → {{ viTri.the.end }}) — năm thứ {{ viTri.the.nam_trong_the }}/30</div>
          <div class="hc-pos-line hc-namque" v-if="namQuePhep">🎴 Năm-quẻ {{ year }}<span v-if="birthYear"> · Anh {{ year - birthYear }} tuổi</span>:
            <strong>{{ namQuePhep.han }} {{ namQuePhep.viet }}</strong>
            <em>(phép 经世 · thế-quẻ {{ namQuePhep.the_que }} · kiểm 10/10 chính văn 304-313)</em></div>
          <div class="hc-namque-flat" v-if="namQue">· bảng phổ thông (值年 vòng 60): {{ namQue.han }} {{ namQue.viet }}<span v-if="namQue.suspect"> · nghi lỗi</span></div>
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

    <!-- B. Tra Thiết Bản -->
    <div class="hc-card">
      <h3>🔢 Tra điều văn Thiết Bản Thần Số</h3>
      <p class="hc-hint" v-if="tbStats">
        Bảng tra {{ tbStats.total?.toLocaleString() }} điều (số {{ tbStats.seq_range?.[0] }}–{{ tbStats.seq_range?.[1] }}),
        {{ tbStats.with_vi?.toLocaleString() }} điều có bản dịch. Phép TÍNH số từ bát tự: chờ đọc sâu phần lệ (tầng B).
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
.hc-namque { color: var(--accent, #7c5cff); }
.hc-namque em { opacity: .7; font-size: .82rem; }
.hc-namque-flat { font-size: .8rem; opacity: .6; margin: 2px 0 0 18px; }
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
