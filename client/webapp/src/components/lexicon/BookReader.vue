<script setup>
import { ref, computed, watch, onMounted } from "vue";
import {
  getRestoredOverview,
  getRestoredPage,
  restoredFigureUrl,
  getRestoredFigures,
  updateRestoredFigure,
  getRestoredHashtags,
  getRestoredPersons,
  searchRestoredBook,
  getTranslationStatus,
  COPYRIGHT_LABEL,
  TIER_LABEL,
  FIGURE_TYPE_LABEL,
  REDRAW_STATUS_LABEL
} from "../../composables/useLexicon.js";

const props = defineProps({
  corpusId: { type: Number, required: true }
});
const emit = defineEmits(["close", "concept-click"]);

const overview = ref(null);
const currentPage = ref(1);
const pageContent = ref({
  html: "", markdown: "", wikilinks: [], needs_review: false,
  summary_short: "", hashtags: [], persons: [], que_mentions: []
});
const loading = ref(false);
const error = ref("");
const showFigures = ref(false);
const figures = ref([]);
const figuresLoading = ref(false);
const showSearch = ref(false);
const searchQ = ref("");
const searchTag = ref("");
const searchHits = ref([]);
const searchLoading = ref(false);
const popularHashtags = ref([]);
const popularPersons = ref([]);
const showToc = ref(false);
const contentRef = ref(null);

// === Translation toggle (Việt / Trung) ===
const lang = ref("zh");  // "zh" = bản gốc, "vi" = bản dịch
const translationStatus = ref({ has_translation: false, translated_pages: 0, total_pages: 0 });
const langServed = ref("zh");  // server tells us which lang was actually served

async function loadTranslationStatus() {
  try {
    const r = await getTranslationStatus(props.corpusId);
    if (r.status === "ok") {
      translationStatus.value = r;
    }
  } catch (e) { /* ignore */ }
}

function toggleLang() {
  lang.value = lang.value === "zh" ? "vi" : "zh";
  loadPage(currentPage.value);
}

async function loadIndexes() {
  try {
    const [ht, ps] = await Promise.all([
      getRestoredHashtags(props.corpusId),
      getRestoredPersons(props.corpusId)
    ]);
    popularHashtags.value = (ht.hashtags || []).slice(0, 30);
    popularPersons.value = (ps.persons || []).slice(0, 20);
  } catch (e) { /* ignore */ }
}

async function runSearch() {
  searchLoading.value = true;
  try {
    const params = {};
    if (searchTag.value) params.hashtag = searchTag.value;
    if (searchQ.value) params.q = searchQ.value;
    const r = await searchRestoredBook(props.corpusId, params);
    searchHits.value = r.hits || [];
  } catch (e) { /* ignore */ }
  finally { searchLoading.value = false; }
}

function jumpAndClose(pn) {
  currentPage.value = pn;
  showSearch.value = false;
}

async function loadFigures() {
  figuresLoading.value = true;
  try {
    const r = await getRestoredFigures(props.corpusId);
    figures.value = r.figures || [];
  } catch (e) { /* ignore */ }
  finally { figuresLoading.value = false; }
}

async function markFigureStatus(fig, newStatus) {
  await updateRestoredFigure(props.corpusId, fig.figure_id, { redraw_status: newStatus });
  await loadFigures();
}

const tocSections = computed(() => overview.value?.manifest?.sections || []);
const restoredPages = computed(() => overview.value?.manifest?.pages_restored || 0);
const totalPages = computed(() => overview.value?.manifest?.pages_total || 0);

async function loadOverview() {
  loading.value = true;
  try {
    const r = await getRestoredOverview(props.corpusId);
    if (r.restored === false) {
      error.value = "Sách chưa được phục chế. Hãy chạy restoration trước.";
      return;
    }
    overview.value = r;
    // Find first restored page to start
    const firstSection = r.manifest?.sections?.[0];
    const startPage = firstSection?.start_page || currentPage.value;
    if (startPage !== currentPage.value) {
      currentPage.value = startPage;
    } else {
      await loadPage(startPage);
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

/** ⭐ Post-process HTML — thay placeholders bằng <img> thật từ /figures/ */
function injectFigureImages(html, pn) {
  if (!html) return html;
  const corpusId = props.corpusId;
  const pageStr = String(pn).padStart(4, "0");

  // Pattern 1: [[FIGURE:slug|caption]] hoặc [[FIGURE: slug|caption]]
  //   → thử fig-{page:04d}-1.png trước; nếu không có thì thử slug.png
  html = html.replace(/\[\[FIGURE:\s*([^|\]]+?)\s*\|\s*([^\]]+?)\s*\]\]/g, (_m, slug, caption) => {
    slug = slug.trim();
    const candidates = [
      `/figures/${corpusId}/figures/fig-${pageStr}-1.png`,
      `/figures/${corpusId}/figures/${slug}.png`,
      `/figures/${corpusId}/figures/${slug}.jpg`,
    ];
    // Ưu tiên fig-{page}-1.png — em không check existence từ client, dùng fallback onerror
    const primary = candidates[0];
    const fallback = candidates[1];
    return `
      <figure class="page-figure">
        <img src="${primary}"
             onerror="this.onerror=null;this.src='${fallback}';this.classList.add('img-fallback')"
             alt="${caption.replace(/"/g, '&quot;')}"
             loading="lazy" />
        <figcaption>${caption}</figcaption>
      </figure>`;
  });

  // Pattern 2: ![alt](imageN.png) trong markdown TQ
  //   → thử fig-{page}-N.png
  html = html.replace(/!\[([^\]]*)\]\(image(\d+)\.png\)/g, (_m, alt, idx) => {
    const src = `/figures/${corpusId}/figures/fig-${pageStr}-${idx}.png`;
    return `<figure class="page-figure"><img src="${src}" alt="${alt}" loading="lazy" onerror="this.style.display='none'" /></figure>`;
  });

  // Pattern 3: ![alt](图N.png) — biến thể TQ
  html = html.replace(/!\[([^\]]*)\]\(图(\d+)\.png\)/g, (_m, alt, idx) => {
    const src = `/figures/${corpusId}/figures/fig-${pageStr}-${idx}.png`;
    return `<figure class="page-figure"><img src="${src}" alt="${alt}" loading="lazy" onerror="this.style.display='none'" /></figure>`;
  });

  // Pattern 4: <aside class="figure-placeholder" data-figure-type="X" data-figure-desc="Y">...</aside>
  //   ⭐ Server đã rewrite [[FIGURE:...]] thành aside này TRƯỚC khi gửi về client.
  //   → Resolve về <figure><img> với 3 cấp fallback: fig-{page}-1.png → slug.png → fig-{page}-detected-1.png
  html = html.replace(
    /<aside class="figure-placeholder"[^>]*>[\s\S]*?<\/aside>/g,
    (match) => {
      const slugMatch = match.match(/data-figure-type="([^"]+)"/);
      const descMatch = match.match(/data-figure-desc="([^"]+)"/);
      if (!slugMatch) return match; // keep original if no slug
      const slug = slugMatch[1].trim();
      const caption = (descMatch ? descMatch[1] : slug).replace(/"/g, "&quot;");
      const primary = `/figures/${corpusId}/figures/fig-${pageStr}-1.png`;
      const fallback1 = `/figures/${corpusId}/figures/${slug}.png`;
      const fallback2 = `/figures/${corpusId}/figures/${slug}.jpg`;
      // chain onerror: primary → fallback1 → fallback2 → hide
      const onerrorChain = `
        if(!this.dataset.fb){this.dataset.fb='1';this.src='${fallback1}';return;}
        if(this.dataset.fb==='1'){this.dataset.fb='2';this.src='${fallback2}';return;}
        this.onerror=null;this.style.display='none';
        const cap=this.parentElement.querySelector('figcaption');
        if(cap){cap.classList.add('fig-missing');cap.innerHTML='⚠️ Hình chưa có: '+cap.textContent;}
      `.replace(/\s+/g, " ").trim();
      return `
        <figure class="page-figure" data-figure-slug="${slug}">
          <img src="${primary}"
               onerror="${onerrorChain}"
               alt="${caption}"
               loading="lazy" />
          <figcaption>${caption}</figcaption>
        </figure>`;
    }
  );

  return html;
}

async function loadPage(pn) {
  try {
    const r = await getRestoredPage(props.corpusId, pn, { fmt: "html", lang: lang.value });
    langServed.value = r.lang_served || "zh";
    if (r.status !== "ok") {
      error.value = r.message || `Trang ${pn} chưa phục chế`;
      pageContent.value = { html: "", markdown: "", wikilinks: [], needs_review: false };
      return;
    }
    error.value = "";
    pageContent.value = {
      html: injectFigureImages(r.html || "", pn),
      wikilinks: r.wikilinks || [],
      needs_review: r.needs_review,
      confidence: r.confidence,
      summary_short: r.summary_short || "",
      hashtags: r.hashtags || [],
      persons: r.persons || [],
      que_mentions: r.que_mentions || []
    };
  } catch (e) {
    error.value = String(e.message || e);
  }
}

watch(currentPage, (pn) => { if (overview.value) loadPage(pn); });

function gotoPage(pn) {
  if (pn < 1) return;
  if (totalPages.value && pn > totalPages.value) return;
  currentPage.value = pn;
  if (contentRef.value) contentRef.value.scrollTop = 0;
}

function gotoSection(sec) {
  currentPage.value = sec.start_page;
  showToc.value = false;
}

function onClickPage(ev) {
  const target = ev.target;
  if (target && target.classList?.contains("wikilink")) {
    ev.preventDefault();
    const concept = target.getAttribute("data-concept");
    if (concept) emit("concept-click", concept);
  }
}

onMounted(async () => {
  await loadOverview();
  loadTranslationStatus();
});
</script>

<template>
  <div class="book-reader" @click="onClickPage">
    <header class="reader-header">
      <div class="head-left">
        <button class="close-btn" @click="emit('close')">← Về thư viện</button>
        <h3 v-if="overview" class="bk-title">
          <span class="tier-badge" :style="{ background: TIER_LABEL[overview.book.tier]?.color }">
            {{ overview.book.tier }}
          </span>
          {{ overview.manifest?.book_name }}
          <span class="copyright-pill" v-if="overview.book.copyright_status">
            {{ COPYRIGHT_LABEL[overview.book.copyright_status]?.icon }}
            {{ COPYRIGHT_LABEL[overview.book.copyright_status]?.label }}
          </span>
        </h3>
      </div>
      <div class="head-right" v-if="overview">
        <!-- Language toggle -->
        <button v-if="translationStatus.has_translation"
                class="figbtn langbtn"
                :class="{ 'lang-vi': lang === 'vi', 'lang-zh': lang === 'zh' }"
                @click="toggleLang"
                :title="`${translationStatus.translated_pages}/${translationStatus.total_pages} trang đã dịch`">
          {{ lang === "vi" ? "🇻🇳 Việt" : "🇨🇳 Trung" }}
          <span v-if="langServed !== lang" class="lang-fallback-mark">⚠</span>
        </button>
        <button class="figbtn searchbtn" @click="showSearch = !showSearch; if (showSearch) loadIndexes()">
          🔍 Tìm
        </button>
        <button class="figbtn tocbtn" @click="showToc = !showToc">
          📑 Mục lục
        </button>
        <button class="figbtn" @click="showFigures = !showFigures; if (showFigures) loadFigures()">
          🎨 Hình ({{ figures.length || '?' }})
        </button>
        Trang {{ currentPage }} / {{ totalPages || "?" }}
        <span class="restored-info">({{ restoredPages }} đã phục chế)</span>
        <span v-if="translationStatus.has_translation" class="trans-info">
          🇻🇳 {{ translationStatus.translated_pages }}/{{ translationStatus.total_pages }}
        </span>
      </div>
    </header>

    <div v-if="loading" class="status">Đang tải…</div>
    <div v-else-if="error && !overview" class="status error">{{ error }}</div>

    <div v-else-if="overview" class="reader-body">
      <!-- TOC sidebar / mobile drawer -->
      <aside class="toc" :class="{ open: showToc }">
        <h4>📑 Mục lục ({{ tocSections.length }})</h4>
        <ul>
          <li v-for="sec in tocSections" :key="sec.section_id"
              :class="{ active: currentPage >= sec.start_page && (!sec.end_page || currentPage <= sec.end_page),
                        level1: sec.level === 1, level2: sec.level === 2, level3: sec.level >= 3 }"
              @click="gotoSection(sec)">
            <span class="toc-title">{{ sec.title }}</span>
            <span class="toc-page">tr.{{ sec.start_page }}</span>
          </li>
        </ul>
        <div v-if="tocSections.length === 0" class="empty">
          Chưa có mục lục — sẽ tự cập nhật sau khi LLM phát hiện chương đầu tiên.
        </div>
      </aside>
      <button
        v-if="showToc"
        type="button"
        class="toc-backdrop"
        aria-label="Đóng mục lục"
        @click="showToc = false"
      />

      <!-- Page content -->
      <main ref="contentRef" class="page-pane reading-pane">
        <div class="copyright-banner">
          ⚠️ <strong>Bản phục chế nội bộ</strong> — phục vụ nghiên cứu, không thay thế sách in.
          <span v-if="overview.book.author">
            Vui lòng mua sách gốc của <em>{{ overview.book.author }}</em> để ủng hộ tác giả.
          </span>
        </div>
        <div v-if="error" class="status error inline">{{ error }}</div>
        <div v-if="pageContent.needs_review" class="review-flag">
          ⚠️ Trang này LLM đánh dấu cần review (confidence {{ (pageContent.confidence * 100).toFixed(0) }}%).
        </div>

        <!-- Page summary + hashtags (v2 metadata) -->
        <div v-if="pageContent.summary_short" class="page-summary">
          <span class="ps-label">📝 TLDR:</span>
          <span class="ps-text">{{ pageContent.summary_short }}</span>
        </div>
        <div v-if="pageContent.hashtags?.length || pageContent.persons?.length || pageContent.que_mentions?.length"
             class="page-tags">
          <span v-for="tag in pageContent.hashtags" :key="'h-'+tag"
                class="ht-chip" @click="searchTag = tag; showSearch = true; loadIndexes(); runSearch()">
            {{ tag }}
          </span>
          <span v-for="p in pageContent.persons" :key="'p-'+p" class="person-chip">👤 {{ p }}</span>
          <span v-for="q in pageContent.que_mentions" :key="'q-'+q" class="que-chip">☱ {{ q }}</span>
        </div>

        <article class="page-content reading-surface reading-prose" v-html="pageContent.html"></article>
        <div v-if="pageContent.wikilinks?.length" class="page-wls">
          <strong>Khái niệm trên trang này:</strong>
          <span v-for="w in pageContent.wikilinks" :key="w" class="wl-chip"
                @click="emit('concept-click', w)">{{ w }}</span>
        </div>
      </main>
    </div>

    <!-- Search panel (hashtags + persons + free text) -->
    <aside v-if="showSearch" class="search-panel">
      <header>
        <h4>🔍 Tìm trong sách</h4>
        <button class="close-btn" @click="showSearch = false">✕</button>
      </header>
      <div class="search-controls">
        <input v-model="searchQ" type="text" placeholder="Tìm trong tóm tắt, người, quẻ..." @keyup.enter="runSearch"/>
        <input v-model="searchTag" type="text" placeholder="Hashtag (vd: #ngũ-hành)" @keyup.enter="runSearch"/>
        <button class="btn-search" :disabled="searchLoading" @click="runSearch">
          {{ searchLoading ? "..." : "Tìm" }}
        </button>
      </div>

      <details class="popular" open>
        <summary>🏷️ Hashtag phổ biến ({{ popularHashtags.length }})</summary>
        <div class="tag-cloud">
          <span v-for="h in popularHashtags" :key="h.tag" class="ht-chip clickable"
                @click="searchTag = h.tag; runSearch()" :title="h.count + ' trang'">
            {{ h.tag }} <em>{{ h.count }}</em>
          </span>
        </div>
      </details>

      <details class="popular">
        <summary>👤 Người được nhắc ({{ popularPersons.length }})</summary>
        <div class="tag-cloud">
          <span v-for="p in popularPersons" :key="p.name" class="person-chip clickable"
                @click="searchQ = p.name; runSearch()" :title="p.count + ' trang'">
            {{ p.name }} <em>{{ p.count }}</em>
          </span>
        </div>
      </details>

      <div v-if="searchHits.length" class="search-results">
        <strong>Kết quả ({{ searchHits.length }}):</strong>
        <ul>
          <li v-for="hit in searchHits" :key="hit.page" class="search-hit"
              @click="jumpAndClose(hit.page)">
            <div class="sh-page">Trang {{ hit.page }}</div>
            <div v-if="hit.summary_short" class="sh-summary">{{ hit.summary_short }}</div>
            <div class="sh-tags">
              <span v-for="t in hit.hashtags.slice(0, 6)" :key="t" class="mini-tag">{{ t }}</span>
            </div>
          </li>
        </ul>
      </div>
      <div v-else-if="searchTag || searchQ" class="empty">Không tìm thấy.</div>
    </aside>

    <!-- Figures panel (toggleable) -->
    <aside v-if="showFigures" class="figures-panel">
      <header>
        <h4>🎨 Hình trong sách ({{ figures.length }})</h4>
        <button class="close-btn" @click="showFigures = false">✕</button>
      </header>
      <p class="hint">
        Phục chế ghi nhận hình. Anh review danh sách → quyết định vẽ lại (SVG hoặc AI redraw).
      </p>
      <div v-if="figuresLoading">Đang tải...</div>
      <div v-else-if="figures.length === 0" class="empty">
        Chưa có hình nào được note. Trang này có thể chưa có scan hoặc OCR chưa detect.
      </div>
      <ul v-else class="fig-list">
        <li v-for="fig in figures" :key="fig.figure_id"
            class="fig-item" :class="`fig-${fig.redraw_status}`">
          <div class="fi-head">
            <span class="fi-type">{{ FIGURE_TYPE_LABEL[fig.figure_type] || fig.figure_type }}</span>
            <span class="fi-page" @click="currentPage = fig.page">tr.{{ fig.page }}</span>
            <span class="fi-status"
                  :style="{ color: REDRAW_STATUS_LABEL[fig.redraw_status]?.color }">
              {{ REDRAW_STATUS_LABEL[fig.redraw_status]?.label }}
            </span>
          </div>
          <!-- ⭐ Thumbnail ảnh phục chế -->
          <div class="fi-thumb">
            <img
              :src="`/figures/${props.corpusId}/figures/fig-${String(fig.page).padStart(4,'0')}-${fig.figure_index || 1}.png`"
              :alt="fig.description || fig.caption || `Hình trang ${fig.page}`"
              loading="lazy"
              @error="(e) => { e.target.style.display='none'; e.target.nextElementSibling.style.display='block' }" />
            <span class="fi-noimg" style="display:none">(file chưa có)</span>
          </div>
          <div class="fi-desc">{{ fig.description || fig.caption || "(không có mô tả)" }}</div>
          <div v-if="fig.redraw_status === 'needs_redraw'" class="fi-actions">
            <button class="btn-sm" @click="markFigureStatus(fig, 'in_progress')">📝 Bắt đầu vẽ</button>
            <button class="btn-sm" @click="markFigureStatus(fig, 'done')">✓ Đã có ảnh</button>
            <button class="btn-sm-ghost" @click="markFigureStatus(fig, 'skip')">Bỏ qua</button>
          </div>
          <div v-else-if="fig.redraw_status === 'in_progress'" class="fi-actions">
            <button class="btn-sm" @click="markFigureStatus(fig, 'done')">✓ Done</button>
            <button class="btn-sm-ghost" @click="markFigureStatus(fig, 'needs_redraw')">↶ Reset</button>
          </div>
          <div v-else-if="fig.redraw_status === 'done' || fig.redraw_status === 'skip'" class="fi-actions">
            <button class="btn-sm-ghost" @click="markFigureStatus(fig, 'needs_redraw')">↶ Mở lại</button>
          </div>
        </li>
      </ul>
    </aside>

    <!-- Pagination -->
    <footer v-if="overview" class="pager">
      <button @click="gotoPage(currentPage - 1)" :disabled="currentPage <= 1">← Trang trước</button>
      <input type="number" v-model.number="currentPage" :min="1" :max="totalPages || undefined"
             class="page-input"/>
      <button @click="gotoPage(currentPage + 1)" :disabled="totalPages && currentPage >= totalPages">
        Trang sau →
      </button>
    </footer>
  </div>
</template>

<style scoped>
.book-reader {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--read-bg);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}
.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  background: var(--read-bg-soft);
  border-bottom: 1px solid var(--read-border);
  gap: 1rem;
  flex-wrap: wrap;
}
.head-left { display: flex; align-items: center; gap: 0.75rem; }
.close-btn {
  background: var(--read-cite-bg);
  color: var(--read-link);
  border: 1px solid var(--read-border);
  padding: 0.3rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: calc(13.5px * var(--reading-scale));
}
.bk-title {
  margin: 0;
  color: var(--read-heading);
  font-size: calc(17px * var(--reading-scale));
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.tier-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  color: #0f172a;
  font-weight: 700;
  font-size: 0.75rem;
}
.copyright-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.45rem;
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border-radius: 3px;
}
.head-right { color: var(--read-text-dim); font-size: calc(13.5px * var(--reading-scale)); }
.restored-info { color: var(--read-text-faint); }

.status { padding: 2rem; text-align: center; color: var(--read-text-dim); }
.status.error { color: #f87171; }
.status.inline { padding: 0.5rem; text-align: left; }

.reader-body {
  flex: 1;
  display: grid;
  grid-template-columns: 240px 1fr;
  overflow: hidden;
}
.toc {
  background: var(--read-bg-soft);
  border-right: 1px solid var(--read-border);
  padding: 0.75rem;
  overflow-y: auto;
}
.toc h4 { color: var(--read-heading); margin: 0 0 0.5rem; font-size: calc(13.5px * var(--reading-scale)); }
.toc ul { list-style: none; padding: 0; margin: 0; }
.toc li {
  padding: 0.3rem 0.5rem;
  cursor: pointer;
  border-radius: 3px;
  color: var(--read-text-dim);
  font-size: calc(13px * var(--reading-scale));
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
}
.toc li:hover { background: var(--read-cite-bg); color: var(--read-link); }
.toc li.active { background: var(--read-cite-bg); color: var(--read-heading); }
.toc li.level2 { padding-left: 1.2rem; font-size: calc(12.5px * var(--reading-scale)); }
.toc li.level3 { padding-left: 2rem; font-size: calc(12px * var(--reading-scale)); }
.toc-page { color: var(--read-text-faint); font-size: calc(11.5px * var(--reading-scale)); }
.toc .empty {
  font-size: calc(12.5px * var(--reading-scale));
  color: var(--read-text-faint);
  font-style: italic;
  padding: 0.5rem;
}

.page-pane {
  overflow-y: auto;
  padding: 1rem 1.5rem;
  color: var(--read-text);
}
.copyright-banner {
  background: rgba(251, 191, 36, 0.08);
  border-left: 3px solid #fbbf24;
  padding: 0.5rem 0.75rem;
  border-radius: 3px;
  color: #fbbf24;
  font-size: 0.78rem;
  margin-bottom: 1rem;
}
.review-flag {
  padding: 0.4rem 0.6rem;
  background: rgba(239, 68, 68, 0.08);
  color: #fca5a5;
  border-left: 3px solid #f87171;
  border-radius: 3px;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
}
.page-content {
  font-family: "Be Vietnam Pro", Georgia, "Times New Roman", serif;
  font-size: calc(16px * var(--reading-scale));
  line-height: var(--reading-line-height, 1.78);
  color: var(--read-text);
}
.page-content :deep(p) {
  font-size: calc(16px * var(--reading-scale));
  line-height: var(--reading-line-height, 1.78);
  margin: 0.65em 0;
}
.page-content :deep(h1) {
  color: var(--read-heading);
  font-size: calc(24px * var(--reading-scale));
  margin: 1rem 0 0.5rem;
}
.page-content :deep(h2) {
  color: var(--read-heading);
  font-size: calc(20px * var(--reading-scale));
  margin-top: 1rem;
}
.page-content :deep(h3) {
  color: var(--read-han);
  font-size: calc(17.5px * var(--reading-scale));
}
.page-content :deep(blockquote) {
  border-left: 3px solid var(--read-cite-accent);
  padding: 0.3rem 0.75rem;
  margin: 0.5rem 0;
  background: var(--read-cite-bg);
  color: var(--read-text-dim);
  font-style: italic;
}
.page-content :deep(.wikilink) {
  color: var(--read-link);
  text-decoration: none;
  border-bottom: 1px dotted var(--read-link);
  cursor: pointer;
}
.page-content :deep(.wikilink:hover) {
  background: var(--read-cite-bg);
}
.page-content :deep(figure) {
  margin: 0.75rem 0;
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.5rem;
  border-radius: 4px;
}
.page-content :deep(figure img) {
  max-width: 100%;
  border-radius: 3px;
}
.page-content :deep(figcaption) {
  font-size: calc(13px * var(--reading-scale));
  color: var(--read-text-dim);
  margin-top: 0.3rem;
}
/* Figure placeholder card — chỗ ảnh cần vẽ lại */
.page-content :deep(.figure-placeholder) {
  display: block;
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  background: rgba(251, 191, 36, 0.08);
  border: 2px dashed rgba(251, 191, 36, 0.5);
  border-radius: 6px;
  color: #fbbf24;
}
.page-content :deep(.figure-placeholder .fp-head) {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
}
.page-content :deep(.figure-placeholder .fp-desc) {
  font-size: calc(13.5px * var(--reading-scale));
  color: var(--read-text-dim);
  font-style: italic;
  line-height: 1.6;
}

.page-wls {
  margin-top: 1rem;
  padding: 0.6rem;
  background: var(--read-bg-soft);
  border-radius: 4px;
  font-size: calc(13px * var(--reading-scale));
}
.page-wls strong { color: var(--read-text-dim); margin-right: 0.5rem; }
.wl-chip {
  display: inline-block;
  margin: 0.15rem;
  padding: 0.15rem 0.5rem;
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  border-radius: 3px;
  cursor: pointer;
}
.wl-chip:hover { background: rgba(34, 197, 94, 0.3); }

.figbtn {
  padding: 0.3rem 0.7rem;
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.78rem;
  margin-right: 0.5rem;
}
.figbtn:hover { background: rgba(251, 191, 36, 0.2); }
.langbtn {
  font-weight: 600;
  font-size: 0.85rem;
  position: relative;
}
.langbtn.lang-vi {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.18) 0%, rgba(250, 204, 21, 0.18) 100%);
  border-color: rgba(220, 38, 38, 0.5);
  color: #fef3c7;
}
.langbtn.lang-zh {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.lang-fallback-mark {
  position: absolute;
  top: -4px; right: -4px;
  background: #f59e0b; color: #1c1917;
  border-radius: 50%; width: 14px; height: 14px;
  font-size: 0.6rem; line-height: 14px;
  text-align: center;
}
.trans-info {
  color: #fbbf24;
  font-size: 0.72rem;
  margin-left: 0.4rem;
  padding: 2px 6px;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 4px;
}
.searchbtn {
  background: rgba(96, 165, 250, 0.1);
  color: #93c5fd;
  border-color: rgba(96, 165, 250, 0.3);
}
.searchbtn:hover { background: rgba(96, 165, 250, 0.2); }

.page-summary {
  margin-bottom: 0.75rem;
  padding: 0.6rem 0.8rem;
  background: rgba(96, 165, 250, 0.08);
  border-left: 3px solid #60a5fa;
  border-radius: 3px;
  font-size: calc(14px * var(--reading-scale));
  line-height: 1.6;
}
.ps-label { color: #60a5fa; font-weight: 600; margin-right: 0.4rem; }
.ps-text { color: var(--read-text-dim); font-style: italic; }

.page-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 1rem;
  font-size: 0.75rem;
}
.ht-chip {
  padding: 0.15rem 0.5rem;
  background: rgba(167, 139, 250, 0.15);
  color: #c4b5fd;
  border-radius: 3px;
  cursor: pointer;
}
.ht-chip:hover { background: rgba(167, 139, 250, 0.3); }
.ht-chip em { color: #94a3b8; font-style: normal; font-size: 0.7rem; }
.person-chip {
  padding: 0.15rem 0.5rem;
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
  border-radius: 3px;
}
.person-chip.clickable { cursor: pointer; }
.que-chip {
  padding: 0.15rem 0.5rem;
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
  border-radius: 3px;
}

.search-panel {
  position: absolute;
  top: 60px;
  right: 12px;
  width: 380px;
  max-height: 80vh;
  background: rgba(15, 23, 42, 0.97);
  border: 1px solid rgba(96, 165, 250, 0.3);
  border-radius: 6px;
  padding: 0.75rem;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}
.search-panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.search-panel h4 { margin: 0; color: #93c5fd; font-size: 0.9rem; }
.search-panel .close-btn {
  background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 1rem;
}
.search-controls {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.6rem;
}
.search-controls input {
  padding: 0.35rem 0.5rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.82rem;
}
.btn-search {
  padding: 0.35rem;
  background: #60a5fa;
  color: #0f172a;
  font-weight: 600;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.82rem;
}
.popular {
  margin-bottom: 0.6rem;
  font-size: 0.78rem;
}
.popular summary {
  cursor: pointer;
  color: #cbd5e1;
  padding: 0.25rem 0;
}
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding-top: 0.3rem;
}
.search-results { margin-top: 0.5rem; font-size: 0.8rem; }
.search-results ul {
  list-style: none; padding: 0; margin: 0.4rem 0 0;
  display: flex; flex-direction: column; gap: 0.4rem;
}
.search-hit {
  padding: 0.4rem 0.5rem;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 3px;
  cursor: pointer;
}
.search-hit:hover { background: rgba(167, 139, 250, 0.1); }
.sh-page { color: #93c5fd; font-weight: 600; font-size: 0.78rem; }
.sh-summary { color: #cbd5e1; margin: 0.2rem 0; line-height: 1.4; font-style: italic; font-size: 0.78rem; }
.sh-tags { display: flex; flex-wrap: wrap; gap: 0.15rem; }
.mini-tag {
  padding: 0.05rem 0.3rem;
  background: rgba(167, 139, 250, 0.15);
  color: #c4b5fd;
  border-radius: 2px;
  font-size: 0.68rem;
}
.search-panel .empty {
  color: #64748b;
  text-align: center;
  padding: 1rem;
  font-style: italic;
}

.figures-panel {
  position: absolute;
  top: 60px;
  right: 12px;
  width: 340px;
  max-height: 70vh;
  background: rgba(15, 23, 42, 0.97);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 6px;
  padding: 0.75rem;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}
.figures-panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}
.figures-panel h4 { margin: 0; color: #fbbf24; font-size: 0.9rem; }
.figures-panel .close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 1rem;
}
.figures-panel .hint {
  color: #94a3b8;
  font-size: 0.72rem;
  margin: 0 0 0.5rem;
}
.figures-panel .empty {
  color: #64748b;
  font-style: italic;
  padding: 1rem;
  text-align: center;
}
.fig-list { list-style: none; padding: 0; margin: 0; }
.fig-item {
  padding: 0.5rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 4px;
  margin-bottom: 0.4rem;
  border-left: 3px solid #fbbf24;
}
.fig-item.fig-done { border-left-color: #86efac; opacity: 0.7; }
.fig-item.fig-skip { border-left-color: #64748b; opacity: 0.55; }
.fig-item.fig-in_progress { border-left-color: #60a5fa; }
.fi-head {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  font-size: 0.75rem;
  margin-bottom: 0.3rem;
}
.fi-type { color: #f1f5f9; font-weight: 600; flex: 1; }
.fi-page {
  color: #93c5fd;
  cursor: pointer;
  text-decoration: underline;
}
.fi-status { font-size: 0.7rem; }
.fi-thumb {
  margin: 0.35rem 0;
  background: rgba(0,0,0,0.3);
  border-radius: 3px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  max-height: 200px;
}
.fi-thumb img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  cursor: zoom-in;
}
.fi-noimg {
  padding: 1rem;
  color: #94a3b8;
  font-size: 0.78rem;
  font-style: italic;
  text-align: center;
}

/* ⭐ Page figure injected inline */
:deep(.page-figure) {
  margin: 1rem auto;
  text-align: center;
  background: var(--read-surface);
  border-radius: 6px;
  padding: 0.75rem;
  border: 1px solid var(--read-border);
  max-width: 90%;
}
:deep(.page-figure img) {
  max-width: 100%;
  max-height: 480px;
  object-fit: contain;
  border-radius: 4px;
  display: block;
  margin: 0 auto 0.5rem;
}
:deep(.page-figure figcaption) {
  font-size: calc(13.5px * var(--reading-scale));
  color: var(--read-text-dim);
  font-style: italic;
  line-height: 1.6;
  margin-top: 0.4rem;
}
:deep(.page-figure figcaption.fig-missing) {
  color: #b91c1c;
  font-style: italic;
  background: #fef2f2;
  border: 1px dashed #fca5a5;
  border-radius: 6px;
  padding: 6px 10px;
}
:deep(.page-figure img.img-fallback) {
  opacity: 0.85;
  border: 1px dashed #a16207;
}

.fi-desc {
  font-size: 0.75rem;
  color: #cbd5e1;
  font-style: italic;
  margin-bottom: 0.4rem;
  line-height: 1.4;
}
.fi-actions { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.btn-sm, .btn-sm-ghost {
  padding: 0.2rem 0.5rem;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.72rem;
}
.btn-sm { background: rgba(167, 139, 250, 0.2); color: #c4b5fd; }
.btn-sm-ghost { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }

.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem;
  background: var(--read-bg-soft);
  border-top: 1px solid var(--read-border);
}
.pager button {
  padding: 0.35rem 0.8rem;
  background: var(--read-cite-bg);
  color: var(--read-link);
  border: 1px solid var(--read-border);
  border-radius: 4px;
  cursor: pointer;
}
.pager button:disabled { opacity: 0.4; cursor: not-allowed; }
.page-input {
  width: 70px;
  text-align: center;
  padding: 0.35rem;
  background: var(--read-surface);
  border: 1px solid var(--read-border);
  color: var(--read-text);
  border-radius: 4px;
}

@media (max-width: 700px) {
  .reader-body { grid-template-columns: 1fr; position: relative; }
  .toc {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: min(86vw, 320px);
    z-index: 120;
    box-shadow: 8px 0 28px rgba(0, 0, 0, 0.45);
  }
  .toc.open { display: block; }
  .toc-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 110;
    border: 0;
    background: rgba(0, 0, 0, 0.55);
    cursor: pointer;
  }
  .page-pane {
    padding-inline: 0.35rem;
  }
  .page-content :deep(p) {
    font-size: calc(17px * var(--reading-scale));
  }
  .pager {
    position: sticky;
    bottom: 0;
    background: linear-gradient(180deg, transparent, var(--read-bg) 30%);
    padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0px));
  }
  .pager button {
    min-height: 44px;
    min-width: 44px;
  }
  .head-right {
    width: 100%;
    flex-wrap: wrap;
    gap: 0.35rem;
  }
  .figbtn {
    min-height: 40px;
  }
}
</style>
