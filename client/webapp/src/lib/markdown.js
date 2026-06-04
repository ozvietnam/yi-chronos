/**
 * Safe markdown → HTML renderer (escape-first). Single source of truth — replaces
 * the 11+ hand-rolled per-component renderers (audit rec #3, fixes XSS #22).
 *
 * Security model:
 *  - ALL source text is HTML-escaped BEFORE any transform, so injected
 *    <script>/<img onerror=…> become inert text.
 *  - Links are scheme-validated (http/https/mailto + relative/anchor only) — blocks
 *    javascript:/data:/vbscript: — and get rel="noopener noreferrer".
 *  - Output only ever contains the safe tags this module emits.
 */

const _SAFE_SCHEME = /^(?:https?:|mailto:)/i;

export function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Return a safe href, or null if the scheme is not allowed. `raw` is the
 *  already-escaped link target captured from `[text](raw)`. */
function safeHref(raw) {
  const href = String(raw).trim();
  if (!href) return null;
  if (_SAFE_SCHEME.test(href)) return href;
  // Relative paths / same-page anchors are safe (no scheme).
  if (/^[/#?]/.test(href)) return href;
  // A bare path like "foo/bar" (no scheme, no leading slash) — treat as relative.
  if (!/^[a-z][a-z0-9+.-]*:/i.test(href)) return href;
  // Anything with an explicit non-allowed scheme (javascript:, data:, …) is blocked.
  return null;
}

/** Inline transforms (bold/italic/code/link). Escapes first, validates links. */
export function renderInline(s) {
  let html = escapeHtml(s)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>")
    .replace(/\b_([^_\n]+)_\b/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
  // Links — drop the link (keep text) if the scheme is unsafe.
  html = html.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, text, href) => {
    const safe = safeHref(href);
    if (!safe) return text;
    return `<a href="${safe}" target="_blank" rel="noopener noreferrer">${text}</a>`;
  });
  return html;
}

/**
 * Full block-level markdown renderer: tables, headings (h1–h6), hr, blockquote,
 * unordered lists, paragraphs — all escape-first.
 */
export function renderMarkdown(md) {
  if (!md) return "";
  const lines = String(md).split("\n");
  const out = [];
  let inList = false;
  let inTable = false;
  const closeList = () => { if (inList) { out.push("</ul>"); inList = false; } };
  const closeTable = () => { if (inTable) { out.push("</table>"); inTable = false; } };

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const s = raw.trim();

    // Tables: | a | b |
    if (s.startsWith("|") && s.endsWith("|")) {
      closeList();
      if (!inTable) { out.push('<table class="md-table">'); inTable = true; }
      if (/^\|\s*[-:]+\s*\|/.test(s)) continue; // separator row
      const cells = s.slice(1, -1).split("|").map((c) => c.trim());
      const isHeader = i + 1 < lines.length && /^\|\s*[-:]+/.test(lines[i + 1].trim());
      const tag = isHeader ? "th" : "td";
      out.push("<tr>" + cells.map((c) => `<${tag}>${renderInline(c)}</${tag}>`).join("") + "</tr>");
      continue;
    }
    closeTable();

    if (!s) { closeList(); continue; }

    let m;
    if ((m = s.match(/^(#{1,6})\s+(.*)$/))) {
      closeList();
      const lvl = m[1].length;
      out.push(`<h${lvl}>${renderInline(m[2])}</h${lvl}>`);
      continue;
    }
    if (/^---+$/.test(s)) { closeList(); out.push("<hr>"); continue; }
    if (s.startsWith(">")) {
      closeList();
      out.push(`<blockquote>${renderInline(s.replace(/^>\s?/, ""))}</blockquote>`);
      continue;
    }
    if (/^[-*→]\s+/.test(s)) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${renderInline(s.replace(/^[-*→]\s+/, ""))}</li>`);
      continue;
    }
    // Plain paragraph line.
    closeList();
    out.push(`<p>${renderInline(s)}</p>`);
  }
  closeList();
  closeTable();
  return out.join("\n");
}
