<template>
  <div class="gieo-duyen">
    <header class="gd-hero">
      <div class="gd-hero-icon">💞</div>
      <h2>Gieo Duyên</h2>
      <p class="gd-sub">Đạo phu thê soi qua ba hệ Đông phương — Tử Vi · Bát Tự · Kinh Dịch</p>
      <p class="gd-tag">Đúc kết sau khi đọc nhiều sách và tự phản biện · không bói toán, mệnh là động từ</p>
      <div class="gd-actions">
        <a class="gd-pdf-btn" href="/GIEO-DUYEN.pdf" target="_blank" rel="noopener">📄 Đọc / tải bản PDF</a>
      </div>
    </header>

    <!-- Công cụ tương tác: Xem tuổi đôi lứa -->
    <section class="gd-tool">
      <h3>🔮 Xem tuổi đôi lứa — ba hệ</h3>
      <p class="gd-tool-sub">Nhập lá số của bạn và một lá số khác. Hệ thống soi Tử Vi · Bát Tự · Kinh Dịch, chấm độ <em>tương ứng</em> và gợi ý <strong>gia quy</strong>.</p>
      <div class="gd-form">
        <div class="gd-person">
          <h4>Người 1 (bạn)</h4>
          <input v-model="n1" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b1" type="datetime-local" class="gd-in" />
          <select v-model="g1" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
        <div class="gd-heart">💞</div>
        <div class="gd-person">
          <h4>Người 2</h4>
          <input v-model="n2" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b2" type="datetime-local" class="gd-in" />
          <select v-model="g2" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
      </div>
      <button class="gd-run" :disabled="!b1 || !b2 || loading" @click="run">
        {{ loading ? '⏳ Đang soi ba hệ...' : '✨ Xem tương ứng' }}
      </button>
      <p v-if="err" class="gd-err">{{ err }}</p>

      <!-- Kết quả -->
      <div v-if="res" class="gd-result">
        <div class="gd-score">
          <div class="gd-score-num">{{ res.diem_tong }}<span>/100</span></div>
          <div class="gd-score-muc">{{ res.muc }}</div>
        </div>

        <div class="gd-truc" :class="res.truc_cuong_nhu.ung_nhau ? 'ung' : 'chua'">
          <strong>Trục Cương–Nhu:</strong>
          {{ res.ten1 }} <b>{{ res.truc_cuong_nhu.xu_huong_1 }}</b> ·
          {{ res.ten2 }} <b>{{ res.truc_cuong_nhu.xu_huong_2 }}</b>
          {{ res.truc_cuong_nhu.ung_nhau ? '→ ỨNG NHAU ✓' : '' }}
          <div class="gd-truc-gt">{{ res.truc_cuong_nhu.giai_thich }}</div>
        </div>

        <div class="gd-he">
          <span>Tử Vi <b>{{ res.tu_vi.diem }}</b></span>
          <span>Bát Tự <b>{{ res.bat_tu.diem }}</b></span>
          <span>Kinh Dịch <b>{{ res.ha_lac.diem }}</b></span>
        </div>

        <div class="gd-cols">
          <div class="gd-col khoa">
            <h5>🔑 Khóa duyên</h5>
            <ul><li v-for="(k,i) in res.khoa_duyen" :key="i">{{ k }}</li></ul>
          </div>
          <div class="gd-col giu">
            <h5>🛠 Chỗ phải giữ</h5>
            <ul><li v-for="(c,i) in res.cho_phai_giu" :key="i">{{ c }}</li></ul>
          </div>
        </div>

        <div class="gd-giaquy">
          <h5>📜 Gia quy gợi ý cho hai bạn</h5>
          <ol><li v-for="(g,i) in res.gia_quy" :key="i">{{ g }}</li></ol>
        </div>

        <details class="gd-guide">
          <summary>📖 Hướng dẫn đọc kết quả (đọc trước khi tin)</summary>
          <ul><li v-for="(h,i) in res.huong_dan" :key="i">{{ h }}</li></ul>
          <p class="gd-para">⚖️ {{ res.paradigm }}</p>
        </details>
      </div>
    </section>

    <article class="gd-body reading-surface" v-html="rendered"></article>

    <footer class="gd-foot">
      <p>Cuốn sách này là đúc kết của một ca điển hình. Công cụ phía trên áp cùng phương pháp cho lá số bất kỳ — đọc đồng dạng, không bói toán.</p>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import manuscript from "../content/gieo-duyen.md?raw";
import { activeBirthDatetime, activePerson } from "../stores/userDataStore.js";

// ── Công cụ Xem tuổi đôi lứa ──
const n1 = ref(""); const b1 = ref(""); const g1 = ref("nam");
const n2 = ref(""); const b2 = ref(""); const g2 = ref("nữ");
const loading = ref(false); const res = ref(null); const err = ref("");

onMounted(() => {
  // prefill lá số người dùng nếu đã đăng nhập / có active person
  const bd = activeBirthDatetime?.value;
  if (bd) b1.value = String(bd).slice(0, 16);
  const p = activePerson?.value;
  if (p?.name) n1.value = p.name;
  if (p?.gender) g1.value = p.gender === "nữ" || p.gender === "nu" || p.gender === "F" ? "nữ" : "nam";
});

async function run() {
  if (!b1.value || !b2.value) return;
  loading.value = true; err.value = ""; res.value = null;
  try {
    const r = await fetch("/api/tu-vi/hop-hon", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth1: b1.value, gender1: g1.value, ten1: n1.value || "Người 1",
        birth2: b2.value, gender2: g2.value, ten2: n2.value || "Người 2",
      }),
    });
    const d = await r.json();
    if (d.error) { err.value = d.error; } else { res.value = d; }
  } catch (e) { err.value = "Lỗi kết nối, thử lại."; } finally { loading.value = false; }
}

// Markdown nhẹ → HTML (đủ cho sách: heading, đậm, nghiêng, trích dẫn, bảng, hr, list)
function renderMarkdown(md) {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const lines = md.split("\n");
  const out = [];
  let i = 0;
  const inline = (t) =>
    esc(t)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
  while (i < lines.length) {
    let ln = lines[i];
    if (/^\s*$/.test(ln)) { i++; continue; }
    // bảng
    if (ln.includes("|") && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      const header = ln.split("|").map((c) => c.trim()).filter(Boolean);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].includes("|")) {
        rows.push(lines[i].split("|").map((c) => c.trim()).filter((_, k, a) => !(k === 0 && a[0] === "") ));
        i++;
      }
      let t = "<table><thead><tr>" + header.map((h) => `<th>${inline(h)}</th>`).join("") + "</tr></thead><tbody>";
      for (const r of rows) {
        const cells = r.filter((c) => c !== "");
        t += "<tr>" + cells.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>";
      }
      t += "</tbody></table>";
      out.push(t);
      continue;
    }
    if (/^####\s/.test(ln)) { out.push(`<h5>${inline(ln.replace(/^####\s/, ""))}</h5>`); i++; continue; }
    if (/^###\s/.test(ln)) { out.push(`<h4>${inline(ln.replace(/^###\s/, ""))}</h4>`); i++; continue; }
    if (/^##\s/.test(ln)) { out.push(`<h3>${inline(ln.replace(/^##\s/, ""))}</h3>`); i++; continue; }
    if (/^#\s/.test(ln)) { out.push(`<h2 class="gd-h1">${inline(ln.replace(/^#\s/, ""))}</h2>`); i++; continue; }
    if (/^>\s?/.test(ln)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(inline(lines[i].replace(/^>\s?/, ""))); i++; }
      out.push(`<blockquote>${buf.join("<br>")}</blockquote>`);
      continue;
    }
    if (/^(-{3,}|\*{3,})\s*$/.test(ln)) { out.push("<hr>"); i++; continue; }
    if (/^\s*[-*]\s+/.test(ln) || /^\s*\d+\.\s+/.test(ln)) {
      const ordered = /^\s*\d+\.\s+/.test(ln);
      const buf = [];
      while (i < lines.length && (/^\s*[-*]\s+/.test(lines[i]) || /^\s*\d+\.\s+/.test(lines[i]))) {
        buf.push(`<li>${inline(lines[i].replace(/^\s*(?:[-*]|\d+\.)\s+/, ""))}</li>`);
        i++;
      }
      out.push((ordered ? "<ol>" : "<ul>") + buf.join("") + (ordered ? "</ol>" : "</ul>"));
      continue;
    }
    // đoạn văn
    const buf = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^[#>|]/.test(lines[i]) && !/^(-{3,})/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i])) {
      buf.push(inline(lines[i]));
      i++;
    }
    out.push(`<p>${buf.join(" ")}</p>`);
  }
  return out.join("\n");
}

const rendered = computed(() => renderMarkdown(manuscript));
</script>

<style scoped>
.gieo-duyen { max-width: 760px; margin: 0 auto; padding: 16px; }
.gd-hero { text-align: center; padding: 28px 16px 22px; background: linear-gradient(160deg,#fff6f0,#fdeef5); border: 1px solid #e8cdd6; border-radius: 16px; margin-bottom: 22px; }
.gd-hero-icon { font-size: 2.4em; }
.gd-hero h2 { margin: 6px 0 4px; font-size: 1.9em; color: #9c3a5a; letter-spacing: 1px; }
.gd-sub { margin: 4px 0; color: #6a4555; font-size: 0.98em; }
.gd-tag { margin: 8px 0 0; color: #9a7886; font-size: 0.84em; font-style: italic; }
.gd-actions { margin-top: 16px; }
.gd-pdf-btn { display: inline-block; padding: 10px 22px; border-radius: 24px; background: #9c3a5a; color: #fff; text-decoration: none; font-size: 0.92em; transition: all .15s; }
.gd-pdf-btn:hover { background: #7d2c47; transform: translateY(-1px); }

/* Công cụ Xem tuổi đôi lứa */
.gd-tool { margin: 0 0 30px; padding: 22px; background: var(--read-surface,#fff); border: 1px solid #e8cdd6; border-radius: 16px; }
.gd-tool h3 { margin: 0 0 4px; color: #9c3a5a; font-size: 1.3em; text-align: center; }
.gd-tool-sub { margin: 0 0 16px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }
.gd-form { display: flex; align-items: stretch; gap: 12px; flex-wrap: wrap; }
.gd-person { flex: 1; min-width: 210px; display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #fdf6f8; border-radius: 10px; }
.gd-person h4 { margin: 0 0 2px; color: #7d2c47; font-size: 0.95em; }
.gd-in { padding: 8px 10px; border: 1px solid #dcc6cd; border-radius: 8px; font: inherit; font-size: 0.9em; background: #fff; color: #333; }
.gd-heart { display: flex; align-items: center; font-size: 1.6em; }
.gd-run { display: block; width: 100%; margin-top: 14px; padding: 12px; border: none; border-radius: 24px; background: #9c3a5a; color: #fff; font: inherit; font-size: 1em; cursor: pointer; transition: all .15s; }
.gd-run:hover:not(:disabled) { background: #7d2c47; }
.gd-run:disabled { opacity: .5; cursor: not-allowed; }
.gd-err { color: #c0392b; text-align: center; margin-top: 10px; font-size: 0.9em; }

.gd-result { margin-top: 22px; }
.gd-score { text-align: center; margin-bottom: 16px; }
.gd-score-num { font-size: 3em; font-weight: 700; color: #9c3a5a; line-height: 1; }
.gd-score-num span { font-size: 0.35em; color: #b88; font-weight: 400; }
.gd-score-muc { color: #7d4357; font-size: 1.02em; margin-top: 4px; }
.gd-truc { padding: 12px 16px; border-radius: 10px; margin-bottom: 14px; font-size: 0.94em; }
.gd-truc.ung { background: #eef9f0; border: 1px solid #b6dfc0; }
.gd-truc.chua { background: #fbf6ee; border: 1px solid #e6d6b8; }
.gd-truc b { color: #9c3a5a; text-transform: capitalize; }
.gd-truc-gt { margin-top: 6px; color: var(--read-text,#444); font-size: 0.92em; line-height: 1.55; }
.gd-he { display: flex; justify-content: center; gap: 18px; margin-bottom: 16px; font-size: 0.9em; color: #7d4357; }
.gd-he b { color: #9c3a5a; font-size: 1.1em; }
.gd-cols { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.gd-col { flex: 1; min-width: 230px; padding: 12px 14px; border-radius: 10px; }
.gd-col.khoa { background: #eef9f0; border: 1px solid #c4e6cd; }
.gd-col.giu { background: #fdf3ec; border: 1px solid #ecd3bf; }
.gd-col h5 { margin: 0 0 8px; font-size: 0.95em; }
.gd-col.khoa h5 { color: #2e7d32; } .gd-col.giu h5 { color: #b06a28; }
.gd-col ul { margin: 0; padding-left: 18px; } .gd-col li { margin: 6px 0; font-size: 0.88em; line-height: 1.5; color: var(--read-text,#3a3a38); }
.gd-giaquy { padding: 14px 16px; background: #f5f0fa; border: 1px solid #d8cce8; border-radius: 10px; margin-bottom: 14px; }
.gd-giaquy h5 { margin: 0 0 8px; color: #6a4a9c; }
.gd-giaquy ol { margin: 0; padding-left: 20px; } .gd-giaquy li { margin: 6px 0; font-size: 0.9em; line-height: 1.55; }
.gd-guide summary { cursor: pointer; color: #8a6d1a; font-size: 0.9em; padding: 6px 0; }
.gd-guide ul { padding-left: 18px; } .gd-guide li { margin: 6px 0; font-size: 0.86em; color: var(--read-text-faint,#777); line-height: 1.5; }
.gd-para { font-style: italic; color: #9c3a5a; font-size: 0.88em; margin-top: 8px; }

.gd-body { line-height: 1.85; color: var(--read-text, #2b2b2b); font-size: var(--reading-scale, 1em); }
.gd-body :deep(.gd-h1) { display: none; } /* tiêu đề sách đã ở hero */
.gd-body :deep(h3) { margin: 28px 0 10px; padding-top: 14px; border-top: 1px solid #eddfe4; color: #9c3a5a; font-size: 1.25em; }
.gd-body :deep(h4) { margin: 20px 0 8px; color: #7d4357; font-size: 1.08em; }
.gd-body :deep(h5) { margin: 16px 0 6px; color: #8a6d1a; font-size: 0.98em; }
.gd-body :deep(p) { margin: 12px 0; }
.gd-body :deep(blockquote) { margin: 16px 0; padding: 12px 18px; background: #fbf3f6; border-left: 3px solid #c98aa0; border-radius: 6px; color: #5d4450; font-style: italic; }
.gd-body :deep(table) { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.9em; }
.gd-body :deep(th), .gd-body :deep(td) { border: 1px solid #e6d5db; padding: 7px 10px; text-align: left; vertical-align: top; }
.gd-body :deep(th) { background: #f7e9ee; color: #7d2c47; }
.gd-body :deep(ul), .gd-body :deep(ol) { margin: 12px 0; padding-left: 22px; }
.gd-body :deep(li) { margin: 5px 0; }
.gd-body :deep(hr) { border: none; border-top: 1px dashed #d8c2c9; margin: 26px 0; }
.gd-body :deep(code) { background: #f3e8ec; padding: 1px 5px; border-radius: 4px; font-size: 0.88em; }
.gd-body :deep(strong) { color: #7d2c47; }

.gd-foot { margin-top: 28px; padding: 16px; background: #f7f3f0; border-radius: 12px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }
</style>
