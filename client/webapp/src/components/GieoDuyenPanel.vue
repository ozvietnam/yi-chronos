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

    <article class="gd-body reading-surface" v-html="rendered"></article>

    <footer class="gd-foot">
      <p>Sắp tới trên trang này: nhập ngày sinh hai vợ chồng → phân tích xem tuổi 3 hệ + gợi ý <strong>gia quy</strong> riêng cho cặp của bạn.</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from "vue";
import manuscript from "../content/gieo-duyen.md?raw";

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
