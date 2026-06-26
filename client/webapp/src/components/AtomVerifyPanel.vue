<script setup>
/**
 * AtomVerifyPanel — Bàn duyệt Atoms (owner-only). Anh = chuyên gia duyệt đúng/sai
 * tri thức đã trích từ sách → bước confidence 0.85→0.98 (đúng) / 0.0 (sai). Nâng chất
 * MỌI môn. Wire vào workbench API có sẵn (api/atomization.py). 2026-06-26.
 */
import { ref, computed, onMounted } from "vue";
import { sessionToken } from "../stores/authStore.js";

const stats = ref(null);
const books = ref([]);
const book = ref("");          // book đang chọn
const sections = ref([]);
const section = ref(null);     // section đang chọn
const atoms = ref([]);
const onlyUnverified = ref(true);
const loading = ref("");
const err = ref("");

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}
async function api(path, opts = {}) {
  const r = await fetch(`/api/atomization${path}`, {
    headers: authHeaders(), credentials: "include", ...opts,
  });
  if (!r.ok) throw new Error(`Lỗi ${r.status}`);
  return r.json();
}

const pct = computed(() => {
  if (!stats.value || !stats.value.n_atomic_questions) return 0;
  const v = (stats.value.founder_verified_count || 0) + (stats.value.founder_rejected_count || 0);
  return Math.round((v / stats.value.n_atomic_questions) * 1000) / 10;
});
const shownAtoms = computed(() =>
  onlyUnverified.value ? atoms.value.filter((a) => a.founder_verified === 0) : atoms.value);

const BOOK_VI = {
  "trung-chau-tu-vi-dau-so-2": "Trung Châu Tử Vi — Quyển 2 (Vương Đình Chi)",
  "tu-vi-dau-so-toan-thu-vu-tai-luc": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lộc)",
  "tu-vi-ham-so": "Tử Vi Hàm Số",
  "tu-vi-nghiem-ly-toan-thu-thien-luong": "Tử Vi Nghiệm Lý (Thiên Lương)",
};
const bookVi = (b) => BOOK_VI[b] || b;
const STATUS_VI = { todo: "chưa làm", in_progress: "đang làm", done: "đã trích", verified: "đã duyệt" };

async function loadStats() {
  try { stats.value = await api("/stats"); } catch (e) { /* noop */ }
}
async function loadBooks() {
  loading.value = "books"; err.value = "";
  try { books.value = await api("/books"); }
  catch (e) { err.value = String(e.message || e); }
  finally { loading.value = ""; }
}
async function pickBook(b) {
  book.value = b; section.value = null; atoms.value = []; sections.value = [];
  loading.value = "sections"; err.value = "";
  try { sections.value = await api(`/books/${encodeURIComponent(b)}/sections`); }
  catch (e) { err.value = String(e.message || e); }
  finally { loading.value = ""; }
}
async function pickSection(s) {
  section.value = s; atoms.value = [];
  loading.value = "atoms"; err.value = "";
  try { atoms.value = await api(`/books/${encodeURIComponent(book.value)}/sections/${encodeURIComponent(s.id)}/atoms`); }
  catch (e) { err.value = String(e.message || e); }
  finally { loading.value = ""; }
}
async function verify(atom, verdict) {
  const prev = atom.founder_verified;
  atom.founder_verified = verdict;           // optimistic
  try {
    await api(`/verify/${atom.atom_id}?verdict=${verdict}`, { method: "POST" });
    // cập nhật tiến độ section + tổng (đếm lại tại chỗ)
    if (section.value) {
      section.value.n_verified = atoms.value.filter((a) => a.founder_verified === 1).length;
      section.value.n_rejected = atoms.value.filter((a) => a.founder_verified === -1).length;
    }
    loadStats();
  } catch (e) {
    atom.founder_verified = prev;            // rollback nếu lỗi
    err.value = String(e.message || e);
  }
}
const sid = (a) => {
  const s = a.subject_identifiers || {};
  return [s.sao, s.cung, s.chi, s.hoa].filter(Boolean).join(" · ");
};

onMounted(() => { loadStats(); loadBooks(); });
</script>

<template>
  <div class="atom-verify">
    <header class="av-head">
      <h2>📋 Bàn duyệt Atoms — hiệu chỉnh tri thức</h2>
      <p class="av-sub">Anh là <b>chuyên gia duyệt</b>: đọc tri thức máy trích từ sách → bấm
        <b>Đúng/Sai</b>. Đúng → độ tin cậy lên 0.98 (sage ưu tiên trích); Sai → loại khỏi luận giải.
        Nâng chất <b>mọi môn</b>.</p>
      <div v-if="stats" class="av-stats">
        <span class="av-stat"><b>{{ (stats.founder_verified_count || 0).toLocaleString() }}</b> đúng</span>
        <span class="av-stat av-rej"><b>{{ (stats.founder_rejected_count || 0).toLocaleString() }}</b> sai</span>
        <span class="av-stat av-mut">/ {{ (stats.n_atomic_questions || 0).toLocaleString() }} atoms</span>
        <div class="av-bar"><div class="av-bar-fill" :style="{ width: pct + '%' }"></div></div>
        <span class="av-stat av-mut">{{ pct }}% đã duyệt</span>
      </div>
    </header>

    <p v-if="err" class="av-err">⚠ {{ err }}</p>

    <!-- Chọn sách -->
    <div class="av-books">
      <button v-for="b in books" :key="b.book" type="button"
        class="av-book" :class="{ on: book === b.book }" @click="pickBook(b.book)">
        <span class="av-book-ten">{{ bookVi(b.book) }}</span>
        <span class="av-book-n">{{ b.n_atoms }} atoms · {{ b.n_sections }} mục</span>
      </button>
      <span v-if="loading === 'books'" class="av-mut">đang tải sách…</span>
    </div>

    <!-- Chọn mục (section) -->
    <div v-if="book" class="av-sections">
      <span v-if="loading === 'sections'" class="av-mut">đang tải mục…</span>
      <button v-for="s in sections" :key="s.id" type="button"
        class="av-sec" :class="{ on: section && section.id === s.id, ['st-' + s.status]: true }"
        @click="pickSection(s)">
        <span class="av-sec-ten">{{ s.title || s.id }}</span>
        <span class="av-sec-meta">{{ s.n_verified }}✓/{{ s.n_atoms }} · {{ STATUS_VI[s.status] || s.status }}</span>
      </button>
    </div>

    <!-- Duyệt atoms -->
    <div v-if="section" class="av-atoms">
      <div class="av-atoms-head">
        <h3>{{ section.title || section.id }} — {{ shownAtoms.length }} atom</h3>
        <label class="av-toggle"><input type="checkbox" v-model="onlyUnverified" /> chỉ hiện chưa duyệt</label>
      </div>
      <p v-if="loading === 'atoms'" class="av-mut">đang tải atoms…</p>
      <p v-else-if="!shownAtoms.length" class="av-mut">Không còn atom nào {{ onlyUnverified ? 'chưa duyệt' : '' }} trong mục này. 🎉</p>

      <article v-for="a in shownAtoms" :key="a.atom_id" class="av-atom"
        :class="{ ok: a.founder_verified === 1, no: a.founder_verified === -1 }">
        <div class="av-atom-q">{{ a.question_text }}</div>
        <p v-if="sid(a)" class="av-atom-sid">{{ sid(a) }}</p>
        <blockquote v-if="a.source_quote" class="av-atom-src">“{{ a.source_quote }}”
          <cite v-if="a.page_start">— tr.{{ a.page_start }}</cite></blockquote>
        <details v-if="a.viet_thuan || a.vi_du_doi_song" class="av-atom-com">
          <summary>diễn giải thuần Việt + ví dụ</summary>
          <p v-if="a.viet_thuan">{{ a.viet_thuan }}</p>
          <p v-if="a.vi_du_doi_song" class="av-atom-vd">Ví dụ: {{ a.vi_du_doi_song }}</p>
        </details>
        <p v-if="a.iron_rule_warning" class="av-atom-warn">⚠ {{ a.iron_rule_warning }}</p>
        <div class="av-atom-acts">
          <button class="av-ok" :class="{ active: a.founder_verified === 1 }" @click="verify(a, 1)">✓ Đúng</button>
          <button class="av-no" :class="{ active: a.founder_verified === -1 }" @click="verify(a, -1)">✕ Sai</button>
          <button v-if="a.founder_verified !== 0" class="av-reset" @click="verify(a, 0)">↺</button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.atom-verify { max-width: 960px; margin: 0 auto; color: var(--read-fg, inherit); }
.av-head h2 { margin-bottom: .2rem; }
.av-sub { color: var(--read-muted, #888); font-size: .9rem; line-height: 1.6; }
.av-stats { display: flex; gap: .7rem; align-items: center; flex-wrap: wrap; margin-top: .7rem; font-size: .9rem; }
.av-stat b { font-size: 1.05rem; }
.av-rej b { color: #c2410c; }
.av-mut { color: var(--read-muted, #999); }
.av-bar { flex: 1; min-width: 120px; height: 8px; border-radius: 4px; background: var(--read-border, #e5e5e5); overflow: hidden; }
.av-bar-fill { height: 100%; background: linear-gradient(90deg, #16a34a, #65a30d); }
.av-err { color: #c2410c; background: rgba(217,119,6,.08); padding: .5rem .7rem; border-radius: 6px; }
.av-books { display: flex; gap: .5rem; flex-wrap: wrap; margin: 1rem 0; }
.av-book { text-align: left; display: flex; flex-direction: column; gap: .15rem; cursor: pointer;
  border: 1px solid var(--read-border, #ccc); border-radius: 10px; padding: .55rem .8rem; background: transparent; color: inherit; }
.av-book.on { border-color: #7c3aed; background: rgba(124,58,237,.06); }
.av-book-ten { font-weight: 600; font-size: .92rem; }
.av-book-n { font-size: .78rem; color: var(--read-muted, #999); }
.av-sections { display: flex; gap: .4rem; flex-wrap: wrap; margin-bottom: 1rem; }
.av-sec { text-align: left; cursor: pointer; border: 1px solid var(--read-border, #ddd); border-radius: 8px;
  padding: .35rem .6rem; background: transparent; color: inherit; display: flex; flex-direction: column; gap: .1rem; }
.av-sec.on { border-color: #7c3aed; background: rgba(124,58,237,.06); }
.av-sec.st-verified { border-left: 3px solid #16a34a; }
.av-sec.st-done { border-left: 3px solid #ca8a04; }
.av-sec-ten { font-size: .85rem; font-weight: 500; }
.av-sec-meta { font-size: .72rem; color: var(--read-muted, #999); }
.av-atoms-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: .5rem; }
.av-atoms-head h3 { margin: 0; font-size: 1.05rem; }
.av-toggle { font-size: .85rem; color: var(--read-muted, #888); cursor: pointer; }
.av-atom { border: 1px solid var(--read-border, #ddd); border-radius: 10px; padding: .8rem 1rem; margin-bottom: .7rem;
  background: var(--read-bg, transparent); }
.av-atom.ok { border-left: 3px solid #16a34a; }
.av-atom.no { border-left: 3px solid #c2410c; opacity: .7; }
.av-atom-q { font-weight: 600; line-height: 1.6; }
.av-atom-sid { font-size: .78rem; color: var(--read-muted, #888); margin: .25rem 0; }
.av-atom-src { margin: .5rem 0; padding: .4rem .7rem; border-left: 2px solid var(--read-border, #ccc);
  font-size: .9rem; line-height: 1.65; color: var(--read-fg, inherit); background: rgba(0,0,0,.02); }
.av-atom-src cite { display: block; font-size: .76rem; color: var(--read-muted, #999); font-style: normal; margin-top: .2rem; }
.av-atom-com { margin: .4rem 0; font-size: .88rem; }
.av-atom-com summary { cursor: pointer; color: var(--read-muted, #888); }
.av-atom-com p { line-height: 1.65; margin: .35rem 0; }
.av-atom-vd { color: var(--read-muted, #777); font-style: italic; }
.av-atom-warn { font-size: .82rem; color: #c2410c; margin: .35rem 0; }
.av-atom-acts { display: flex; gap: .5rem; margin-top: .6rem; }
.av-ok, .av-no, .av-reset { padding: .4rem .9rem; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: .9rem;
  border: 1px solid var(--read-border, #ccc); background: transparent; color: inherit; }
.av-ok.active { background: #16a34a; color: #fff; border-color: transparent; }
.av-no.active { background: #c2410c; color: #fff; border-color: transparent; }
.av-ok:hover { border-color: #16a34a; }
.av-no:hover { border-color: #c2410c; }
</style>
