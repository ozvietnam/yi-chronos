# Smart Book Onboarding Pipeline v1.0

**Ngày**: 2026-05-25
**Trigger**: Anh quở _"dịch sách không ẩu được em ạ. làm chuẩn bước 1 đi mới nhân bản được. bộ dịch ngày càng thông minh cho nhiều loại sách, chứ không phải tắt bật thủ công như thế."_
**Sai lầm em đã phạm**: Ship swarm OCR (Phase 2 nhanh x5) mà skip Stage 1-3 của Bookflow v2.0 — em đã quên rằng anh đã đầu tư công sức viết `BOOKFLOW-V3-LAYOUT-FIRST.md` (2026-05-18) + `_BOOK-TEMPLATE/` chuẩn rồi.
**Liên quan**:
- IRON RULE #5 — Bookflow v2.0 (`docs/BOOKFLOW-V2.md`)
- Paradigm Shift #5 — LAYOUT-FIRST (`docs/BOOKFLOW-V3-LAYOUT-FIRST.md`)
- Existing: `engine/yi_lexicon/restoration/plan.py` (RestorationPlan dataclass)
- Existing: `data/raw_pdfs/_BOOK-TEMPLATE/` (5 markdown templates)

---

## 1. Vấn đề + nhìn lại sai lầm

### 1.1 Em đã sai gì
1. **Skip Stage 2-3 Bookflow**: em chạy thẳng Stage 4 (OCR) với hard-coded config `-b pipeline -l ch -m auto`. Không profile sách.
2. **Hard-code, không thông minh**: Thiết Bản Thần Số là Hán cổ 3 cột dày đặc → MinerU false detect 26% items thành LaTeX equations. Em không có quy trình tự nhận biết.
3. **Build redundant**: Em viết `engine/yi_publishing/jobs.py` song song với `engine/yi_lexicon/restoration/plan.py` đã có sẵn full features (phase progression, batch tracking, OCR backend config).
4. **Manual toggle thủ công**: Em định propose toggle UI "📐 Bắt công thức" — exactly cách anh KHÔNG muốn. Mỗi sách mới anh phải nhớ tắt/bật → không scale.
5. **Quên 2 sách trước**: Mai Hoa Q3 + Tử Vi Đẩu Số đã được processed thành công — em không học từ chúng.

### 1.2 Tại sao em phạm
- Em focus vào "speedup" (swarm) mà bỏ "smart" (profiling)
- Em không đọc `BOOKFLOW-V3-LAYOUT-FIRST.md` trước khi build
- Em không hỏi "2 sách trước được processed thế nào?" trước khi config sách mới
- Em ship → bug → quở → spike → propose toggle. Vòng loop sai từ đầu.

### 1.3 Triết lý anh muốn (em internalize lần này)

> **Bộ dịch ngày càng thông minh** cho nhiều loại sách. Mỗi sách mới = học thêm → pipeline tự config dựa trên profile, không cần anh nhớ flag.

---

## 2. Lessons từ 2 sách trước (BẮT BUỘC nhúng vào pipeline mới)

| Lesson | Source | Bake vào pipeline |
|---|---|---|
| MarkItDown 1300x faster cho PDF text-layer | 2026-05-12 | Stage 1 detect text_layer → auto route MarkItDown vs OCR |
| qwen-vl 2x quality cho woodblock | 2026-05-12 | Profile detect "woodblock_print" → recommend vlm-auto backend |
| 8-way parallel dispatcher | 2026-05-12 | Đã có `parallel_dispatcher.py`, em chỉ copy pattern (KHÔNG re-build) |
| `[[FIGURE:...]]` LLM bịa filename | 2026-05-18 Q3 v1.2 | Stage 4.1 STRIP all image refs, re-insert manually từ figures_manifest |
| 568 empty rows cho table không có body | 2026-05-18 | Layout-first detect table → cell-level OCR, không là 1 block paragraph |
| Hán cổ 3 cột detect false equations | 2026-05-25 (mới) | Profile detect "classical_chinese" + density="dense" → auto `-f False` |

---

## 3. Smart Onboarding Pipeline — 6 sub-stages của Stage 1-3 Bookflow

```
USER UPLOAD PDF
      │
      ▼
┌─────────────────────────────────────────────────┐
│ S1.1 INTAKE                                      │
│   • Verify PDF integrity (fitz.open)             │
│   • Extract basic metadata (pages, has_textlayer,│
│     title, author from PDF meta)                 │
│   • Move temp → data/raw_pdfs/<book_id>.pdf      │
│   • Register vào RestorationPlan + books.json    │
│ Out: book_id, raw_pdf_path, page_count           │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│ S1.2 PAGE SPLIT + THUMBNAILS                     │
│   • Render every page → thumbnails 150x200       │
│     (gallery preview, no OCR yet)                │
│   • Detect page types: cover/blank/text/image/   │
│     toc/index by simple heuristics (whitespace   │
│     ratio, edge detection)                       │
│ Out: pages_thumbnails/p0001..pNNNN.jpg           │
│      + page_types.json                           │
│ Time: ~30s for 600 pages                         │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│ S1.3 BOOK PROFILER (⭐ heart of intelligence)    │
│   Sample 5 random pages giữa book:               │
│   • Column count       (1/2/3+) via x-histogram  │
│   • Script type        (modern/classical/Hán Nôm)│
│   • Density            (sparse/normal/dense)     │
│   • Font style         (typed/woodblock/scan)    │
│   • Image ratio        (image pixels / total)    │
│   • Has tables?        (line detection)          │
│                                                  │
│   Spike test 2-3 configs (5 pages each):         │
│   • Config A: pipeline auto                      │
│   • Config B: pipeline auto -f False             │
│   • Config C: hybrid-auto-engine (if GPU)        │
│   → Compare equation_ratio, region count,        │
│     reading order. Pick best.                    │
│                                                  │
│ Out: book_profile.json                           │
│      + recommended_ocr_config                    │
│ Time: ~3-5 phút                                  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│ S2.1 TOC DETECTION (3 strategies)                │
│   Strategy 1 (best): fitz.get_toc() bookmarks   │
│   Strategy 2: visual detect "目录"/"Mục lục"      │
│     pages → OCR → parse "chương N: page X"       │
│   Strategy 3: keyword scan pages 5-30 cho        │
│     "第X章", "卷N", "PHẦN N", chapter markers    │
│                                                  │
│ Out: _TOC.md (chapters + page ranges)            │
│      + chapter_ranges.json                       │
│ Time: ~1-3 phút                                  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│ S2.2 PLAN GENERATION                             │
│   Based on profile + TOC, generate:              │
│   • Reading plan: S/A/B/C tier per chapter       │
│   • OCR config: validated recommendation         │
│   • Chunking strategy:                           │
│       - Per chapter (if TOC clean)               │
│       - Equal split N workers (no TOC)           │
│       - Hybrid (TOC + force-split large chapters)│
│   • Translation routing: LLM per content type    │
│     (cổ văn→DeepSeek-Reasoner, modern→Chat,      │
│      tables→Claude...)                           │
│                                                  │
│ Out: _READING-PLAN.md + _TRANSLATION-PLAN.md     │
│      + _OCR-CONFIG.json                          │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│ S2.3 ANH DUYỆT (gate)                            │
│   UI presents:                                   │
│   • Profile summary card                         │
│   • TOC preview (editable)                       │
│   • OCR config + estimated ETA                   │
│   • Translation plan                             │
│                                                  │
│   Anh có 3 options:                              │
│   1. ✅ Duyệt as-is → tiến Stage 4               │
│   2. ✏️ Edit (override config, edit TOC, change  │
│      chunks) → save approved version             │
│   3. ❌ Reject → revisit Stage 1.3 profiler      │
│                                                  │
│ Out: _APPROVED.json (snapshot config khi duyệt)  │
│      + advance phase trong RestorationPlan       │
└──────────────────┬──────────────────────────────┘
                   ▼
       ─────────── Stage 4: OCR ─────────────
       (chạy với config đã duyệt, không hỏi)
```

---

## 4. Book Profiler — chi tiết kỹ thuật

### 4.1 Column detection
- Render 1 sample page → grayscale → binarize
- Compute x-axis histogram of black pixels
- Find vertical gutters (low-density bands)
- N gutters → N+1 columns
- Threshold: gutter width > 20px + density < 10% → real gutter

### 4.2 Script type
- OCR 1 sample page → 50-100 chars
- Char distribution analysis:
  - >80% chars trong CJK Unified Ideographs (U+4E00–U+9FFF) → Chinese
  - Check radicals/variants:
    - Many traditional variants (繁體 specific chars) → traditional
    - Many simplified-only chars → simplified
    - Mix + Nôm chars (U+E000 PUA area or specific Nôm radicals) → Hán Nôm
  - Char repetition pattern: cổ văn lặp ít, modern lặp nhiều common particles (的, 了)

### 4.3 Density + font style
- Whitespace ratio = white pixels / total
- < 30% → dense (woodblock cổ)
- 30-60% → normal (typed modern)
- > 60% → sparse (illustrated)
- Edge detection: woodblock có brush stroke variance cao + ragged edges; typed font có uniform edges

### 4.4 Spike test
- Pick 5 pages từ giữa book (skip cover + TOC)
- Run MinerU mỗi page với 2 configs:
  - A: `pipeline -l ch -m auto`
  - B: `pipeline -l ch -m auto -f False`
- Metrics:
  - `equation_ratio = equation_inline / total_inline_items`
  - `region_count_consistency = stddev(regions_per_page)`
  - `text_extracted = sum(len(content) for text items)`
- Pick config với `equation_ratio < 5%` AND highest `text_extracted`

### 4.5 Decision matrix output

```json
{
  "profile": {
    "columns": 3,
    "script": "classical_chinese",
    "density": "dense",
    "font_style": "woodblock_print",
    "has_tables": false,
    "image_ratio": 0.05
  },
  "ocr_config": {
    "backend": "pipeline",
    "method": "auto",
    "lang": "ch",
    "formula_enable": false,
    "table_enable": false,
    "workers": 3,
    "rationale": "Classical Chinese dense woodblock 3-col → disable formula+table parsing to avoid false positives (spike: 26% → 0% equation_ratio)"
  },
  "similar_books": ["q3-mai-hoa", "..."],
  "expected_ocr_quality": "high",
  "expected_eta_hours": 5.8
}
```

---

## 5. "Bộ dịch thông minh" — Learning loop

Mỗi book processed thành công → save profile + actual results vào `data/yi_publishing/book_profiles.jsonl`. Lần sau gặp sách mới:

1. Profile sách mới
2. Find similar profiles trong history (k-NN trên feature vector: columns, script, density, font_style)
3. If found similar book → recommend SAME config + show anh "Giống Mai Hoa Q3, em đề xuất config X (đã work cho sách đó)"
4. Anh confirm → no spike needed → speed up onboarding

Future improvement: train classifier (script_type, density → optimal_config) khi đã có ≥20 books.

---

## 6. Integration với existing system

### 6.1 Reuse, KHÔNG re-build
| Existing module | Em sẽ dùng | Em sẽ KHÔNG dùng |
|---|---|---|
| `engine/yi_lexicon/restoration/plan.py` RestorationPlan | ✅ Phase tracking, batches | — |
| `_BOOK-TEMPLATE/` markdown files | ✅ _TOC, _READING-PLAN, _TRANSLATION-PLAN, _LLM-ROUTING | — |
| `engine/yi_publishing/books_store.py` (em mới viết) | ✅ Library Gallery metadata | — |
| `engine/yi_publishing/jobs.py` (em mới viết) | ✅ Job queue + swarm | Remove standalone OCR submit; phải go through plan-approved gate |
| `engine/yi_lexicon/restoration/parallel_dispatcher.py` | Pattern (8-way) | Code duplicate trong jobs.py |

### 6.2 Module mới em sẽ build
| Module | Purpose | LOC |
|---|---|---|
| `engine/yi_publishing/book_profiler.py` | Profile + spike + config recommendation | ~400 |
| `engine/yi_publishing/toc_detector.py` | 3-strategy TOC detection | ~250 |
| `engine/yi_publishing/plan_generator.py` | Generate reading + translation plan từ profile + TOC | ~200 |
| `engine/yi_publishing/page_splitter.py` | Thumbnail rendering + page type detection | ~150 |
| API endpoints: `/books/{id}/profile`, `/toc`, `/plan`, `/plan/approve` | ~250 in api/main.py |
| UI components: `BookProfilerView.vue`, `TocEditor.vue`, `PlanReview.vue` | ~600 |

### 6.3 Workflow integration

Library Gallery card → menu mới:
- **📋 Bước 1: Profile + Plan** (replaces direct "Đặt scan OCR")
  - Click → BookProfilerView opens
  - Auto-run profiler + TOC detection + spike (~3-5 phút)
  - Show summary → Anh duyệt
  - Sau khi duyệt → button "🔍 Bắt đầu OCR (config đã duyệt)" enabled

OCR job submit thay đổi: chỉ work khi `_APPROVED.json` exists. Không có plan → reject với message "Run Stage 1.3 profiler first".

---

## 7. Quality gates (anti-ẩu)

| Gate | Khi nào | Pass criteria | Fail action |
|---|---|---|---|
| G1: PDF integrity | After S1.1 | fitz.open OK + page_count > 0 | Reject upload |
| G2: Spike OCR quality | After S1.3 | equation_ratio < 5%, region_count > 0 | Try alternative config OR alert anh |
| G3: TOC sanity | After S2.1 | ≥1 chapter detected OR anh manual confirm | Manual TOC entry |
| G4: Anh approves | After S2.3 | `_APPROVED.json` exists | Block Stage 4 |
| G5: First-chunk smoke | After OCR chunk 0 done | equation_ratio < 5% on real run | STOP swarm, alert |
| G6: Translation FIT | After 10% translated | avg_fit > 70% | Pause, anh review |

---

## 8. Implementation phases (em sẽ làm)

### Phase 1: Foundation (TDD-first)
- `book_profiler.py` + tests — column detection, script detection, spike runner
- `toc_detector.py` + tests — 3 strategies
- `plan_generator.py` + tests
- `page_splitter.py` + tests

### Phase 2: Integration
- API endpoints: `POST /profile`, `GET /plan`, `POST /plan/approve`
- Hook vào existing `RestorationPlan` flow
- Modify `jobs.py` to require `_APPROVED.json` before OCR submit

### Phase 3: UI
- `BookProfilerView.vue` — auto-run profile + show summary
- `TocEditor.vue` — edit chapters + page ranges
- `PlanReview.vue` — show OCR config + ETA + chunking + Anh duyệt
- Replace "Đặt scan OCR" CTA → "📋 Lập kế hoạch dịch" workflow

### Phase 4: Migration
- Re-profile + re-plan cho 4 sách hiện có (q3-*, tuvi, shao-yong)
- Re-OCR Thiết Bản Thần Số với config đúng từ profiler

### Phase 5: Learning loop (later)
- `book_profiles.jsonl` accumulation
- k-NN recommendation cho sách mới

---

## 9. Acceptance criteria

- [ ] Anh upload sách mới → KHÔNG có nút "Đặt scan OCR" ngay; thay vào "📋 Lập kế hoạch dịch"
- [ ] Click "Lập kế hoạch" → auto run profile + TOC + plan trong ~5 phút
- [ ] Output là 1 card preview với: profile summary, TOC, recommended config + ETA, translation plan
- [ ] Anh edit được TOC + config trước khi duyệt
- [ ] Duyệt → unlock "Bắt đầu OCR (config đã duyệt)" button
- [ ] OCR job dùng config từ approved plan, KHÔNG có hard-code
- [ ] First chunk done → smoke check equation_ratio < 5% → tiếp tục; fail → STOP + alert
- [ ] Sau khi xong → save profile + outcome vào `book_profiles.jsonl`
- [ ] Sách mới tương tự sau này → recommend config từ history

---

## 10. Decision points cho anh

Trước khi em code, anh duyệt:

| # | Question | Em đề xuất |
|---|---|---|
| 1 | Foundation modules có nên reuse `RestorationPlan` (legacy) hay extend `books_store` (mới)? | **Reuse RestorationPlan** — có sẵn phase/batch system, chỉ thêm `book_profile` field |
| 2 | Spike test có nên chạy tự động hay đợi anh trigger? | **Auto** sau upload — báo "Đang profile..." ~3-5 phút |
| 3 | Configs em sẽ spike compare? | **2 configs**: A (default), B (-f False). Add C (hybrid-auto) sau khi confirm Stage 1 work |
| 4 | TOC detection priority? | Strategy 1 (bookmarks) > 2 (visual TOC pages) > 3 (keyword scan). Anh override bất cứ lúc nào |
| 5 | UI: 1 màn lớn hay multi-step wizard? | **Single page** với expandable sections (profile / TOC / OCR config / Plan), Anh xem all at once |
| 6 | Quyển Thiết Bản hiện tại: re-OCR thẳng với -f False hay đợi pipeline mới? | **Đợi pipeline** — em không patch nữa, dùng smart pipeline ngay từ đầu cho quyển này như test case đầu tiên |

---

**Cam kết của em**:
- Em **KHÔNG ship code** trước khi anh duyệt design này
- Em **KHÔNG hard-code config** nào nữa cho sách Hán cổ
- Em sẽ **học từ 2 sách trước** trước khi thiết kế module
- Em sẽ **theo Bookflow v3** đã có sẵn, không reinvent

Anh duyệt + chọn options cho 6 decision points → em viết detailed implementation plan rồi triển khai phase-by-phase với TDD.
