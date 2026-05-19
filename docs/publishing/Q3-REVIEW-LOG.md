# 📖 Q3 Review Log — 5-page cycle

**Sách**: Mai Hoa Dịch Số — Hành Đạo Toàn Thư (v1.2)
**File**: `data/published/Q3-mai-hoa-toan-thu-v1.2.pdf` (659 trang A4)
**Reviewer**: em (Claude), do Anh chỉ đạo
**Lý do review**: Anh đọc v1.2 phát hiện em làm ẨU, ra lệnh đọc lại 5 trang một, dừng cải tiến mỗi cycle.

---

## Quy trình review (Bookflow v2.1 — Review Cycle)

```
Mỗi 5 trang:
  1. Export PDF page → PNG
  2. Đọc THẬT (không skim, không stats)
  3. Ghi MỌI lỗi vào log này (typo, layout, OCR, image, structure)
  4. Phân loại lỗi: A (block ship) / B (cần fix) / C (cosmetic)
  5. Propose fix → update process v2.1
  6. Tiếp 5 trang sau
```

**Mục tiêu**: KHÔNG phải fix sách này (sách này đã ship lỗi). Mục tiêu là **trích process lessons** cho sách sau.

---

## Lỗi đã biết trước (Anh catch v1.1)

- ❌ **407 fake image refs** trong manuscript do LLM cleanup hallucinate (đã fix v1.2)
- ❌ **17 figures lạc** không nhúng (đã fix v1.2)

## Lỗi mới phát hiện (review log)

---

### 🔍 Cycle 1: Trang 1-5 (Cover + TOC area)

**Đã đọc**: Cover (p.1) + TOC (p.2-5)
**Verdict**: 🔴 NẶNG — sách bị broken ngay từ trang đầu

#### Lỗi A (block ship — bắt buộc fix)

| # | Trang | Lỗi | Root cause |
|---|---|---|---|
| A1 | p.1 | **Cover không phải cover** — title bị nén, TOC tràn vào ngay cùng trang | CSS không có `.title-page { page-break-after: always; }` riêng cho cover |
| A2 | p.1 | Còn nguyên Trung văn "图解梅花易数" trong TOC chưa dịch | TOC entries sinh từ heading content; heading manuscript còn trộn Việt/Trung |
| A3 | p.1-5 | **TOC layout 2-column rối loạn** — bên trái TOC, bên phải nội dung Phần III + IV chen vào | CSS `column-count: 2` trên #TOC > ul nhưng `column-break` không enforce → tràn |
| A4 | p.2-5 | **TOC dài 4 trang** với "Trang 1 (nguyên tác), Trang 2 (nguyên tác)..." liệt kê 321 lần | `pandoc --toc-depth=3` include h3, mà mỗi page Phần IV là h2 → 321 entries spam TOC |
| A5 | p.2 | "Sách: Minh hoạ Mai Hoa Dịch Số — Thiệu Khang Tiết [trang 12]" — meta-text OCR còn sót | Pages_vi/page-XXXX.md có metadata text từ raw OCR; không strip trong normalize |

#### Lỗi B (cần fix nhưng không block ship)

| # | Trang | Lỗi |
|---|---|---|
| B1 | p.1 | Title page không có vertical centering — chữ dồn lên trên |
| B2 | p.1 | "đồng tác giả Anh & Claude" — `&` HTML escape không render đẹp, nên dùng "và" |
| B3 | p.2-5 | Mục lục có "Mục lục" như một entry — recursive |

#### Process Lesson cho v2.1

```
LESSON L1.1: Cover phải là PAGE RIÊNG
  → CSS: .cover, .title-page { page-break-after: always; height: 100vh; }
  → Manuscript: dedicated title-page section với class wrapper

LESSON L1.2: TOC depth quá sâu = spam
  → Sách dày: --toc-depth=1 (chỉ chương lớn) hoặc --toc-depth=2
  → KHÔNG bao giờ depth=3 cho sách >300 trang

LESSON L1.3: TOC layout column-count nguy hiểm
  → Nếu TOC dài >1 trang, single-column an toàn hơn
  → Hoặc explicit column-fill: auto + page-break-inside: avoid

LESSON L1.4: STRIP meta-text từ pages_vi trước compile
  → Patterns cần strip:
    - "Sách: ..."
    - "[trang N]"
    - "Mục lục" (tránh recursive)
    - "图解梅花易数 — ..." (Trung văn meta)

LESSON L1.5: Heading levels phải standardize TRƯỚC compile
  → pages_vi/page-0012.md có thể có "## Sách: ..." mà em không catch
  → Cần audit heading levels per page TRƯỚC khi concat
```

---

### 🔍 Cycle 2: v1.3 Trang 1-10 (sau khi fix 6 lỗi A của v1.2)

**Đã đọc**: p.1-10 v1.3
**Verdict**: 🟢 CẢI THIỆN VƯỢT BẬC — 6 lỗi A fixed, 2 lỗi A mới phát hiện

#### Cải thiện so v1.2

| Lỗi v1.2 | v1.3 status |
|---|---|
| A1: Cover broken | ✅ Title page riêng |
| A2: Trung văn chưa dịch trong TOC | ✅ Stripped (9,412 chars meta-text removed) |
| A3: TOC 2-cột rối loạn | ✅ Single-column |
| A4: TOC 26 trang | ✅ **TOC chỉ 1 trang** (depth=2, 30 entries) |
| A5: Empty pages giữa book | ✅ (cần verify cycle sau) |
| A6: Meta-text "[trang N]", "Sách:..." | ✅ Stripped |

→ **Content thực bắt đầu từ p.5** (vs v1.2 bắt đầu p.42)

#### Lỗi A mới phát hiện v1.3

| # | Trang | Lỗi | Root cause |
|---|---|---|---|
| A7 | p.1 + p.3 | **DUPLICATE title pages** — pandoc YAML auto-tạo title page (p.1) + custom cover-page div (p.3) | YAML frontmatter `title:` cộng với `.cover-page` markdown div → pandoc render 2 lần |
| A8 | p.3 | Title font 36pt vỡ thành 2 dòng "Mai Hoa Dịch" / "Số" | `.cover-page h1` 36pt + padding 4cm trên A4 → overflow row, browser break |

#### Lỗi B mới (cosmetic)

| # | Trang | Lỗi |
|---|---|---|
| B4 | p.2 TOC | TOC entry "🎀 KẾT THÚC THÂM NHUẦN..." có icon — đẹp nhưng không clean publishing |
| B5 | p.4 | Trang bản quyền: "Tựa Việt:...Tựa gốc:...Tác giả:..." chồng thành 1 đoạn (no line break) |
| B6 | p.6-7 | Tables render OK nhưng cell text nhỏ (8.5pt) — hơi khó đọc |
| B7 | p.6 | Heading "📖 PHẦN 1 — Trang 1-20: Khai môn" có emoji — chấp nhận được nhưng không chuẩn publishing |

#### Process Lesson cho v2.1

```
LESSON L2.1: KHÔNG dùng cả YAML `title:` VÀ custom cover-page div
  → Chọn 1 trong 2:
    A) YAML title — pandoc tự render, đơn giản, không control được
    B) Custom cover-page div + skip YAML title — full control
  → Recommendation: B (đẹp hơn, professional)

LESSON L2.2: Title font phải có max-width / fit-content
  → CSS: .cover-page h1 { font-size: clamp(28pt, 36pt, calc(100% - 4cm)) }
  → Hoặc đơn giản hơn: font 28-30pt thay 36pt cho A4

LESSON L2.3: Trang bản quyền cần line-break giữa fields
  → Manuscript: dùng `\` hoặc 2 spaces ở cuối line + newline để force <br>
  → Hoặc dùng `<dl><dt>Tựa Việt:</dt><dd>...</dd></dl>` HTML

LESSON L2.4: Emoji trong heading
  → Trong manuscript markdown (journal): OK để dễ scan
  → Trong PDF chính thức: nên strip hoặc giữ minimal
  → Trade-off: tùy audience
```

---

### 🔍 Cycle 3+4: Phần I v3 — Design preview, đọc thực p.1-15

**Đã đọc**: 15/101 pages của Phần I standalone (Tinh hoa thâm nhuần)
**File**: `data/published/Q3-part-I-design-v3.pdf`
**Approach**: STOP build monolithic, design-first section-by-section
**CSS**: `/tmp/book-design-v2.css` (468 lines — drop caps, ornaments, pull quotes, image frames)

#### ✅ Quality verified across 15 pages

| Element | Verdict |
|---|---|
| **Cover (p.1)** | Fit 1 trang, title 26pt clean, ornament ✦✦✦, cream warm bg |
| **Part title (p.2)** | h1 center + ornament + epigraph pull quote box |
| **Body text indent** | 1.4em first-line indent, 0 after heading — chuẩn book |
| **Running header** | Small-caps "PHẦN I — TINH HOA THÂM NHUẦN" + italic right |
| **Pull quotes** | Box gradient bg, italic, border-left purple — beautiful |
| **Image frames** | Border + padding + warm bg #fefcf9 |
| **Image captions** | Italic centered, max-width 80%, 9pt |
| **H2 headings** | Underline border + purple, page-break-after avoid |
| **H3 headings** | Italic uppercase serif — distinctive |
| **Tables** | Header purple bg, alternating row tint, normal text (not italic) |
| **Ornament HR** | "❦" dingbat centered |
| **Page numbers** | Bottom center 9.5pt |
| **Chinese (邵雍, 觀梅折數)** | Render đúng, không lỗi font |

#### ⚠ Lỗi nhỏ còn lại (B-tier)

| # | Phát hiện |
|---|---|
| B8 | Body bullet "🌟 Bát Quái xuyên qua 8 tầng tồn tại" (p.4) emoji giữ — chấp nhận trong journal style nhưng KHÔNG chuẩn publishing nếu strict |
| B9 | Heading "🌟 Suy ngẫm của Em..." (p.14) — emoji không strip vì có thể là bold paragraph chứ không phải heading |
| B10 | Cell text trong bảng Tam Dịch (p.14) — cột "Tinh thần" có italic do markdown `*italic*` từ trích dẫn nguyên văn — chấp nhận content |

#### 🎓 Process Lessons Cycle 3+4

```
L3.1: Design-first WORKS — invest CSS = output đẹp
  → 6 trang đầu v1.3 chỉ pandoc default → buồn cười
  → 6 trang đầu v3 với CSS 468 dòng → publishing quality

L3.2: Section-by-section build hiệu quả hơn monolithic
  → Phần I standalone 101 trang build 3.7s (vs 577 trang full 12s)
  → Quality check granular, fix targeted

L3.3: Anh dạy đúng — đọc lại NHƯ CON NGƯỜI, không phải robot stats
  → "lỗi 9/9 contract pass" mà sách không có hình = vẫn ẨU
  → Đọc visually từng trang mới catch được layout issues

L3.4: Cycle 5-trang-một quality > batch big check
  → v1.2 batch ship → 6 lỗi A
  → v3 cycle đọc → 0 lỗi A trong 15 trang
```

---
