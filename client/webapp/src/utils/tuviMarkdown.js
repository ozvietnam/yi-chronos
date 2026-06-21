// Markdown renderer cục bộ cho panel Tử Vi 3-layer. Tách ra từ TuVi3LayerPanel.vue
// để test được (vitest). Giữ ĐÚNG output cũ (.narrative-text dùng white-space:pre-wrap
// nên chỉ transform nhẹ + giữ nguyên xuống dòng) — KHÁC lib/markdown.js (tách block <p>).

export function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

export function renderMarkdown(text) {
  // XSS fix (review 2026-06-21): escape TRƯỚC mọi transform → output LLM/wiki có
  // <script>/<img onerror=…> thành text trơ. Marker markdown (## ** -) không bị
  // escape nên vẫn transform. escapeHtml cũng null-safe (String(s||'')).
  return escapeHtml(text)
    .replace(/^## (.+)$/gm, '<h4>$1</h4>')
    .replace(/^\*\*(.+?)\*\*/gm, '<strong>$1</strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
}
