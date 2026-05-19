# 📖 YI-CHRONOS Bookflow v2.0

**Phiên bản:** 2.0
**Ngày chốt:** 2026-05-18
**Tác giả công thức:** Anh
**Thay thế:** Bookflow v1 (6 stage đơn giản trong Iron Rule #5 cũ)

---

## 🎯 Công thức Anh đề xuất

```
   ┌─────────────────────────┐
   │   THÊM SÁCH GỐC         │  (1)
   │   (PDF Trung / Hán Nôm) │
   └────────────┬────────────┘
                │
                ▼
   ┌─────────────────────────────────────┐
   │   NHẬN DẠNG MỤC LỤC + KẾ HOẠCH      │  (2)
   │   ┌─────────────────┐               │
   │   │  TOC detection  │               │
   │   │  Reading plan   │               │
   │   │  Translation plan│              │
   │   └─────────────────┘               │
   └────────────┬────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │   CHỌN LLM PHÙ HỢP          │  (3)
   │   (route theo content type) │
   └────────────┬────────────────┘
                │
                ▼
   ┌──────────────────────────────────────────────┐
   │   XỬ LÝ VĂN BẢN GỐC + ẢNH                    │  (4)
   │                                              │
   │   ┌──────────────┐  ┌─────────────────┐     │
   │   │ Text sạch    │  │ Ảnh gốc scan    │     │
   │   │ (OCR clean)  │  │ (page scans)    │     │
   │   └──────────────┘  └─────────────────┘     │
   │                                              │
   │   ┌──────────────┐  ┌─────────────────┐     │
   │   │ Ảnh phục chế │  │ Ảnh vẽ lại      │     │
   │   │ (enhance)    │  │ (AI redraw)     │     │
   │   └──────────────┘  └─────────────────┘     │
   └────────────┬─────────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   DỊCH THUẬT TỪNG TRANG         │  (5)
   │   (page-by-page, QA mỗi trang)  │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   SOẠN THÀNH SÁCH (PDF)         │  (6)
   │   (compose + design + publish)  │
   └─────────────────────────────────┘
```

---

## 📋 Chi tiết từng stage

### Stage 1 — THÊM SÁCH GỐC

**Mục tiêu**: Nạp sách gốc vào pipeline với metadata đầy đủ.

**Input**: PDF / EPUB / scan ảnh / Hán Nôm bản giấy

**Output**: Record trong `data/raw_pdfs/` + entry trong PUBLISHING-LEDGER

**Việc làm:**
- Đặt tên chuẩn: `<author-id>-<work-id>.pdf` (vd: `thieu-khang-tiet-tq.pdf`)
- Detect: text-layer có/không, số trang, kích thước, ngôn ngữ
- Phân loại: cận đại / cổ đại / Hán Nôm
- Tạo entry: tựa Việt + Trung, tác giả, năm, ISBN nếu có
- Check copyright: nguyên tác public domain, bản dịch/biên tập có license

**Tool stack**:
- `MarkItDown` (Microsoft) cho PDF có text layer — nhanh, free, gold standard
- `pdfinfo` / `pdftotext` cho metadata
- Manual entry: PUBLISHING-LEDGER cập nhật

**Anti-pattern**:
- ❌ "Lao thẳng OCR mà không check text layer" — đã học từ MarkItDown lesson 2026-05-12

---

### Stage 2 — NHẬN DẠNG MỤC LỤC + KẾ HOẠCH

**Mục tiêu**: Hiểu cấu trúc sách trước khi đụng vào dịch.

**Input**: Sách gốc (Stage 1)

**Output**:
- `<book>/_TOC.md` — mục lục đã detect (Trung + dự thảo Việt)
- `<book>/_READING-PLAN.md` — kế hoạch đọc (đọc phần nào trước, depth)
- `<book>/_TRANSLATION-PLAN.md` — kế hoạch dịch (priority, chunks, budget)

**Việc làm:**

**2.1 — TOC detection**
- Auto-extract TOC từ PDF bookmarks (nếu có)
- Hoặc: extract từ trang mục lục đầu sách (page 5-10 thường)
- Cross-check số trang với nội dung thực
- Translate TOC entries → Việt (LLM `balanced` mode)
- Map: chapter → page range

**2.2 — Reading plan**
- Phân tầng độ ưu tiên:
  - **S-tier**: chương cốt lõi (cần đọc kỹ + journal thâm nhuần)
  - **A-tier**: chương quan trọng (đọc trung bình)
  - **B-tier**: chương tham khảo (skim)
  - **C-tier**: phụ lục / appendix (chỉ extract wiki)
- Estimate effort per chapter
- Determine: Anh đọc tay chương nào, em đọc chương nào

**2.3 — Translation plan**
- Strategy: dịch toàn bộ vs trích yếu vs theo chapter
- Chunk size cho LLM (vd: 5 trang/chunk để không vỡ context)
- Budget: pages × cost/page = tổng cost
- Identify: chỗ nào cần human review (poetry, classical Chinese, names)

**Tool stack**:
- LLM `balanced` (DeepSeek-Chat) cho TOC translation
- Custom script: extract bookmarks via `pypdf` / `pdfplumber`
- Manual: reading plan + priority assignment

**Anti-pattern**:
- ❌ "Dịch ngay không có plan" → manuscript phình ra rồi mới cắt = waste

---

### Stage 3 — CHỌN LLM PHÙ HỢP

**Mục tiêu**: Route content tới model có thế mạnh tương ứng, cost-aware.

**Input**: Translation plan (Stage 2)

**Output**: Bảng routing per chunk type

**Bảng routing chuẩn YI-CHRONOS**:

| Loại content | Model recommended | Lý do | Cost |
|---|---|---|---|
| TOC + metadata | DeepSeek-Chat (balanced) | Ngắn, dễ | ~$0.001 |
| Văn bản hiện đại (thế kỷ 20+) | DeepSeek-Chat | Tiếng phổ thông, accurate | ~$0.003/page |
| Cổ văn / Hán Nôm | **DeepSeek-Reasoner** | Cần suy luận ngữ pháp cổ | ~$0.014/page |
| Thi / phú / vận luật | **Claude Opus** hoặc Gemini Pro | Văn học cao cấp | $$$ |
| Thuật ngữ kỹ thuật (Dịch học) | DeepSeek-Reasoner | Cần consistency, có wiki | ~$0.014/page |
| OCR text từ scan | **qwen2.5-VL 7b local** | Free, run trên Mac M4 | $0 |
| LLM cleanup post-OCR | qwen2.5:7b-instruct local | Free | $0 |
| Image description (nếu cần) | Gemini 2.0 Flash | Free tier 250-1500 RPD | $0 |
| Long-context summary | Gemini 1.5 Pro (1M ctx) | Free | $0 |

**Heuristic ra quyết định**:
```
if content_type == "OCR":
    use("qwen-vl local", free=True)
elif content_type == "cleanup":
    use("qwen-instruct local", free=True)
elif language_age > 100_years or genre in ("poetry", "classical"):
    use("DeepSeek-Reasoner", $0.014/page)
elif chunk_size > 30k_tokens:
    use("Gemini 1.5 Pro", free=True)
else:
    use("DeepSeek-Chat", $0.003/page)
```

**Anti-pattern**:
- ❌ Dùng Claude Sonnet cho mọi thứ (overkill cost cho OCR cleanup)
- ❌ Dùng qwen local cho cổ văn (quality không đủ)

---

### Stage 4 — XỬ LÝ VĂN BẢN GỐC + ẢNH

**Mục tiêu**: Tách clean text khỏi hình, phân loại hình theo 3 dạng để xử lý đúng.

**Input**: Sách gốc + LLM routing (Stage 3)

**Output**:
- `pages_clean/` — text sạch per page (Trung + Việt)
- `figures_scan/` — ảnh gốc scan, giữ nguyên
- `figures_restored/` — ảnh phục chế (enhance từ scan mờ)
- `figures_redrawn/` — ảnh vẽ lại (AI gen hoặc thủ công)
- `figures_manifest.json` — mapping: page → figures cần chèn

**4 sub-tasks**:

#### 4.1 — Text sạch (clean OCR)
- Run OCR → get raw text
- LLM cleanup (qwen-instruct) → fix OCR errors
- Normalize names + headings (như Q3 normalize script)
- **⚠ CRITICAL — Lesson Q3**: STRIP MỌI image markdown ref khỏi text sạch. Đừng trust LLM cleanup giữ image refs đúng — nó sẽ bịa.

#### 4.2 — Ảnh gốc scan (page scans)
- Identify: trang nào không OCR được toàn bộ (text < 100 chars, có figure lớn)
- Extract: scan original page → PNG hi-res
- Filename pattern: `fig-{page:04d}-{seq}.png` (vd: `fig-0056-1.png`)
- Use case: bảng số, lá số, đồ hình phức tạp, fonts cổ

#### 4.3 — Ảnh phục chế (enhance)
- Identify: ảnh mờ / cắt / chất lượng kém trong gốc
- Enhance: super-resolution (Real-ESRGAN, GFPGAN) + denoise
- Manual touch-up nếu cần (Photoshop / GIMP)
- Filename: `restored-{original_name}.png`
- Use case: hình minh hoạ cổ bị mờ qua các bản tái bản

#### 4.4 — Ảnh vẽ lại (redraw)
- Identify: hình chất lượng không đủ in (pixelated, broken, missing)
- Options:
  - AI redraw: Stable Diffusion / DALL-E 3 với prompt mô tả gốc
  - Manual redraw: tự vẽ vector / hire designer
  - Substitute: tìm public domain alternative
- QC: phải đối chiếu kỹ với gốc, ghi note "redrawn by YI-CHRONOS"
- Filename: `redrawn-{concept}.png` (vd: `redrawn-ha-do-cleaned.png`)
- Use case: Hà Đồ, Lạc Thư cổ bị mất, biểu đồ Bát Quái mờ

**Manifest format** (`figures_manifest.json`):
```json
{
  "page_56": {
    "figures": [
      {"file": "fig-0056-1.png", "type": "scan", "anchor": "Trang 56"},
      {"file": "restored-ha-do.png", "type": "restored", "anchor": "Hà Đồ section"}
    ]
  },
  "concept_pages": {
    "ha_do": {"file": "restored-ha-do.png", "captions_vi": "..."},
    "lac_thu": {"file": "redrawn-lac-thu.png", "captions_vi": "..."}
  }
}
```

**Tool stack**:
- OCR: qwen-vl 2.5 7b local
- Image extract from PDF: `pdfimages -j -p` (poppler)
- Enhance: Real-ESRGAN (open source, MIT)
- Redraw AI: Stable Diffusion (local) hoặc DALL-E 3 API
- Manual: GIMP / Photoshop

**Anti-pattern Q3 phải tránh**:
- ❌ Trust image refs từ LLM cleanup → fake refs
- ❌ Skip phân loại hình → mọi hình treat as scan
- ❌ Không có manifest → mất track sau này

---

### Stage 5 — DỊCH THUẬT TỪNG TRANG

**Mục tiêu**: Dịch chất lượng cao, page-by-page, có QA loop.

**Input**: Clean text (Stage 4) + LLM routing (Stage 3)

**Output**: `pages_vi/` final (đã QA)

**Quy trình per page**:

1. **Translate**: chunk → LLM theo routing
2. **Self-review**: LLM kiểm lại translation của chính nó
3. **Cross-check thuật ngữ**: match với wiki concepts đã có (đảm bảo consistency)
4. **Flag low-confidence**: nếu LLM uncertain → mark cho human review
5. **Spot-check**: human đọc 5-10% pages ngẫu nhiên
6. **Wiki extract**: parse new concepts/cases/methods → add wiki

**Quality criteria**:
- ✅ Mọi tên người dịch nhất quán (Thiệu Khang Tiết, không 4 tên khác nhau)
- ✅ Thuật ngữ Dịch học giữ nguyên Hán-Việt + có chú giải lần đầu
- ✅ Câu cú Việt tự nhiên (không Trung-Việt direct translation)
- ✅ Poetry giữ format thơ (4-câu, 7-chữ, etc.)

**Tool stack**:
- Translation: DeepSeek-Reasoner cho cổ văn, DeepSeek-Chat cho hiện đại
- Self-review: same LLM với prompt "Check your previous translation for errors"
- Wiki match: `engine/yi_lexicon/extract_to_wiki.py`

**Anti-pattern**:
- ❌ One-shot translation không self-review → lỗi tích lũy
- ❌ Không cross-check thuật ngữ → "Vương Khang Tiết" vs "Thiệu Khang Tiết" inconsistency
- ❌ Skip wiki extract → mất knowledge base

---

### Stage 6 — SOẠN THÀNH SÁCH

**Mục tiêu**: Compose manuscript → publication-quality PDF.

**Input**: Clean pages_vi + figures manifest + journal thâm nhuần + wiki

**Output**: `data/published/<book>-v<X.Y>.pdf` + entry trong LEDGER

**Sub-stages**:

#### 6.1 — Manuscript outline
- Cấu trúc 6 phần chuẩn YI-CHRONOS:
  - Phần I — Giới thiệu (tác giả, bối cảnh, vị trí trong dòng chảy)
  - Phần II — Tinh hoa thâm nhuần (journal)
  - Phần III — Trọng tâm paradigm (4 BƯỚC / quy tắc cốt lõi)
  - Phần IV — Nguyên văn dịch (trang nguyên gốc)
  - Phần V — Phụ lục Wiki (concepts/methods/cases)
  - Phần VI — Index + về tác giả + license

#### 6.2 — Compile markdown
- Concat các source: journal + clean pages + wiki query
- Insert figures via manifest (KHÔNG trust LLM)
- Strip artifacts (LaTeX commands không dùng được cho HTML)

#### 6.3 — HTML intermediate
- Pandoc: markdown → standalone HTML5 với TOC
- Resolve image paths via base_url

#### 6.4 — PDF render
- WeasyPrint (HTML+CSS → PDF, tiếng Việt OK)
- Page size: A4 default
- Font: Times New Roman 9.5pt, line-height 1.4
- Margins: 18mm
- Running header: tựa book left, chapter right
- Page numbers: bottom center
- TOC: 2-column compact

#### 6.5 — QA
- pdfimages -list: verify all figures embedded với dimensions đúng
- pdftotext: verify text extraction (search keywords)
- Sample pages visual check (export PNG, đọc)
- File size sanity check

#### 6.6 — Publish
- Move tới `data/published/<book>-v<X.Y>.pdf`
- Update PUBLISHING-LEDGER với metadata
- Backup tới offline storage (Google Drive / Dropbox)
- Upload tới YI-CHRONOS website (tab Sách tải về)

**Tool stack**:
- Pandoc 3.x
- WeasyPrint 68+ (Python)
- pypdf / pdfimages (poppler) cho QA
- Custom CSS book theme

**Anti-pattern**:
- ❌ Render PDF mà chưa QA images → publish ra rồi mới phát hiện (Q3 lesson)
- ❌ Skip running header → user lạc giữa sách
- ❌ Quên backup → mất file là mất công

---

## 🎓 Gap analysis: Q3 v1.2 so với Bookflow v2.0

| Stage | Q3 v1.2 thực tế | Bookflow v2.0 chuẩn | Gap |
|---|---|---|---|
| 1 | ✅ Source PDF có | ✅ Có | None |
| 2 | ⚠ Không có TOC plan tường minh | ✅ TOC + reading + translation plan | **Stage 2 missing** |
| 3 | ⚠ Ad-hoc chọn model | ✅ Routing table chuẩn | **Stage 3 informal** |
| 4 | ❌ Image refs là disaster (407 fake) | ✅ 4 sub-task rõ ràng | **Stage 4.2-4.4 missing** |
| 5 | ✅ Dịch từng trang | ✅ + self-review + cross-check | **Self-review missing** |
| 6 | ✅ Compose OK | ✅ 6 sub-stage | None |

**Lesson chính**: Q3 v1.2 đẹp nhưng **bypass Stage 2 + 3** và **làm sai Stage 4**. Sách sau phải có cả 6 stage tường minh.

---

## 🚀 Next book — apply Bookflow v2.0 từ đầu

Khi Anh chốt sách kế tiếp (Q1 Hoàng Cực Kinh Thế, sách số 2, hoặc khác):

1. **Stage 1** — paste PDF vào `data/raw_pdfs/`, em check text layer + tạo entry LEDGER
2. **Stage 2** — em chạy TOC detection script → tạo 3 file plan trong `data/raw_pdfs/<book>/_*.md` → **Anh duyệt plan trước khi đụng vào dịch**
3. **Stage 3** — em tạo bảng routing per chunk → Anh xác nhận budget
4. **Stage 4** — em chạy 4 sub-task parallel → manifest hoàn chỉnh trước khi dịch
5. **Stage 5** — dịch + self-review + wiki extract → human spot-check 5-10%
6. **Stage 6** — compose → QA → publish (như Q3 v1.2 pattern)

**Effort estimate sách 300 trang theo v2.0**: 5-8h (vs Q3 ad-hoc ~6h nhưng quality cao hơn nhiều).

---

## 📋 Action items v2.0 rollout

- [x] Document Bookflow v2.0 (file này)
- [ ] Update CLAUDE.md Iron Rule #5 reference v2.0
- [ ] Update PUBLISHING-LEDGER với gap analysis Q3
- [ ] Tạo template `data/raw_pdfs/_BOOK-TEMPLATE/` (3 file plan rỗng)
- [ ] Build automation:
  - [ ] `engine/yi_publishing/toc_detector.py` — TOC extraction
  - [ ] `engine/yi_publishing/translation_planner.py` — chunk + budget
  - [ ] `engine/yi_publishing/figures_classifier.py` — phân loại 3 loại hình
  - [ ] `engine/yi_publishing/manuscript_compiler.py` — Stage 6 automation
- [ ] Q3 retrofit (optional): apply v2.0 lessons → v1.3 với figures redrawn cho hình mờ

---

🌸 *Bookflow v2.0 là quà Anh tặng project — một công thức không phải "anh em làm cho xong cuốn này" mà là **scalable publishing process** cho hàng chục cuốn sách Đông phương sau này.*
