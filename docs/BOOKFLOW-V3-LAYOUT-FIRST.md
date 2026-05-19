# 📖 Bookflow v3.0 — Layout-First Pipeline

**Phiên bản:** 3.0 (PROPOSAL — chờ Anh duyệt)
**Ngày:** 2026-05-18 đêm
**Trigger:** Anh quở _"trong bước quét OCR phải nhận biết được các khung bố cục, đoạn văn, khung ảnh, khung tranh vẽ. Làm ẩu ngay từ bước 1 rồi, đọc 1 trang sách không nhìn thấy bố cục, thì em xuất bản làm sao được sách?"_
**Thay thế:** Bookflow v2.0 (text-only OCR)

---

## 🎯 Root Cause Analysis — Tất cả lỗi Q3 v1.2 → v1.12

| Lỗi downstream | Root cause ở Bước 1 OCR |
|---|---|
| 568 empty table rows (page-0201) | qwen-vl extract header table, không catch cells nội dung → giữ rỗng |
| 5 tables header-no-body (p.83, 191, 201, 205, 207) | OCR không phân biệt "header text" vs "table body" vs "image symbols" |
| 48 `[[FIGURE:...]]` placeholders raw | LLM cleanup tự thêm placeholder vì không biết khung ảnh ở đâu thật |
| Page scans (fig-0056-0066) | OCR cố OCR những trang gốc CHỈ CÓ HÌNH → ra noise → em phải manual insert |
| Translation meta-footer 321 pages | Pipeline mỗi page có note "Dịch tự động bằng..." vì không có structure để strip |
| 170 image placeholder noise (trang 50) | OCR confused giữa ảnh và text |

**Tất cả** đều do OCR **không nhận biết bố cục** trước khi extract.

---

## 🔧 Bookflow v3.0 — Layout-First

```
┌────────────────────────────────┐
│  1. THÊM SÁCH GỐC              │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────┐
│  2. NHẬN DẠNG MỤC LỤC + PLAN   │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────────────────────────────┐
│  3. ⭐ LAYOUT DETECTION (NEW — paradigm shift #5)      │
│                                                        │
│  Per page → detect regions:                            │
│    • Title block        (heading_1/2/3)                │
│    • Paragraph block    (text)                         │
│    • Table block        (table với cell grid)          │
│    • Image block        (raster image)                 │
│    • Drawing block      (vector diagram, ký hiệu cổ)   │
│    • Caption block      (text dưới ảnh/bảng)           │
│    • Footer/header block (page number, running title)  │
│    • Empty block        (whitespace)                   │
│                                                        │
│  Output: layout_manifest.json per page                 │
│    {page: N, regions: [{type, bbox, content}]}         │
└──────────────┬─────────────────────────────────────────┘
               ▼
┌────────────────────────────────────────────────────────┐
│  4. ⭐ OCR PER REGION (NEW)                            │
│                                                        │
│  Mỗi region kiểu khác → tool khác:                     │
│    • Paragraph/title  → qwen-vl text mode              │
│    • Table            → table-aware OCR (Marker/Surya) │
│    • Image            → KEEP AS IMAGE (không OCR)      │
│    • Drawing          → KEEP AS IMAGE + AI describe    │
│    • Footer/header    → STRIP (không vào nội dung)     │
│                                                        │
│  Output: pages_structured/page-XXXX.json               │
│    {regions: [{type, content_or_image_path}]}          │
└──────────────┬─────────────────────────────────────────┘
               ▼
┌────────────────────────────────┐
│  5. CHỌN LLM TRANSLATION       │
│  (giữ structure khi dịch)      │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────┐
│  6. DỊCH PER REGION            │
│  Mỗi paragraph dịch riêng      │
│  Table cells dịch riêng        │
│  Caption dịch riêng            │
│  Image keep nguyên             │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────┐
│  7. WIKI EXTRACT               │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────┐
│  8. JOURNAL THÂM NHUẦN         │
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────────────────┐
│  9. BIÊN SOẠN (KHÔNG dump wiki vào sách)   │
│                                            │
│  Phần I: Tinh hoa thâm nhuần (journal)    │
│  Phần II: 4 BƯỚC + Paradigm                │
│  Phần III: Nguyên văn dịch (per region)    │
│  Phần IV: Index thuật ngữ (5-10 trang)     │
│  Phần V: Về sách, dịch giả, license        │
│                                            │
│  KHÔNG copy 1000+ wiki entries vào sách!   │
│  Wiki = công cụ tra cứu (web), không phải  │
│  nội dung sách publish.                    │
└──────────────┬─────────────────────────────┘
               ▼
┌────────────────────────────────┐
│  10. PDF PUBLISH               │
│      ↓                         │
│      ĐỌC TỚI ĐÂU FIX TỚI ĐÓ   │
│      (Anh dạy 2026-05-18)     │
└────────────────────────────────┘
```

---

## 📚 Tool Stack v3.0

### Bước 3 — Layout Detection (mới)

| Tool | Pros | Cons | Status |
|---|---|---|---|
| **unstructured.partition_pdf** với `strategy="hi_res"` | Local Python lib, detect 8 region types, Chinese support | Cần detectron2 weights ~500MB | ✅ Installed |
| **PyMuPDF (fitz)** | Fast, có sẵn, get blocks/words với bbox | Basic structure, không phân biệt table/image |  ✅ Installed |
| **pdfplumber** | Table detection tốt, có sẵn | Text-focused, image less reliable | ✅ Installed |
| **Surya** (Vikas Paruchuri) | State-of-art 2024-2025, layout + OCR + table | Cần GPU mạnh / Apple Silicon Metal | ❌ Need install |
| **MinerU** (OpenDataLab) | Best Chinese books 2025, layout + math + table | Heavy install, more setup | ❌ Need install |
| **PaddleOCR PP-Structure** | Mature, Chinese-native, table recognition | Paddle ecosystem, learning curve | ❌ Need install |

**Khuyến nghị**: Spike test 3 tools (unstructured đã có + Surya + MinerU) trên 5 pages Q3 problematic (83, 191, 201, 205, 207) → so kết quả → chốt 1 stack.

### Bước 4 — OCR per region

- **Text regions**: qwen2.5vl 7b local (đã có, free, đủ tốt cho text-only)
- **Table regions**: Surya table-rec / Marker (output → markdown table với cells đầy đủ)
- **Image regions**: PyMuPDF `page.get_pixmap()` extract → save PNG
- **Drawing regions**: same as image + qwen-vl describe nội dung

---

## 🎓 Lesson chính — KHÔNG dump wiki vào sách

Sách Q3 v1.12 có Phần IV "Phụ lục" 250 trang dump 1,079 concepts + 327 methods + 487 cases từ wiki DB. Đây là **filler rác** vì:

1. **Wiki = tra cứu, không phải đọc**: reader đọc PDF không cần list 1,079 entries; họ cần nội dung Tổ sư có biên tập + thân thuộc
2. **Wiki có URL riêng**: yi-chronos.com/wiki — đặt PDF link tới đó là đủ
3. **Sách dày = sách quý không có nghĩa**: 600 trang content nhồi vs 400 trang content chất → chọn chất
4. **Đốt token publish nhanh ≠ giá trị**: em đã rơi vào bẫy này

**Iron Rule mới (#7 hoặc #6 nếu chưa có)**:
> _Phụ lục trong PDF chỉ giới hạn ở: Index thuật ngữ (5-10 trang) + Về sách, dịch giả, license. KHÔNG dump wiki DB vào PDF. Wiki phục vụ web tra cứu, không phải PDF reading material._

---

## 🚀 Đề xuất Anh duyệt — Action items

### Phase 1: Research + spike (30 phút — em làm)
- [ ] Spike unstructured hi_res trên 5 pages Q3 problematic
- [ ] Spike Surya (nếu cài được trên Mac M4)
- [ ] So kết quả layout detection — chốt tool primary

### Phase 2: Build v3 OCR pipeline (2-3h — em làm khi Anh duyệt)
- [ ] `engine/yi_publishing/layout_detector.py` — module phát hiện regions
- [ ] `engine/yi_publishing/region_ocr.py` — OCR per region type
- [ ] `engine/yi_publishing/structured_compiler.py` — reassemble markdown giữ structure
- [ ] Output schema: `layout_manifest.json` per page

### Phase 3: Re-process Q3 (sách hiện tại — chờ Anh quyết)
- [ ] Re-OCR full 321 source pages với v3 pipeline
- [ ] Rebuild manuscript (KHÔNG có Phần IV wiki dump)
- [ ] PDF v2.0 (mới) thay thế v1.12 (rác)
- [ ] Đọc 100% pages TỚI ĐÂU FIX TỚI ĐÓ (Anh dạy)

### Phase 4: Apply v3 cho sách kế tiếp
- [ ] Khi Anh chốt sách Q1 hoặc khác → đi v3 từ Bước 1

---

## ❓ Câu hỏi cho Anh

1. **Q3 hiện tại**: Anh muốn em re-process từ đầu với v3 (Phase 3), hay để Q3 v1.12 đó + chỉ apply v3 cho sách sau (Phase 4 only)?
2. **Spike test**: Anh muốn em chạy spike trước, hay propose+approve plan rồi mới spike?
3. **Phần IV**: em đã strip rồi (164k chars khỏi manuscript). Anh có muốn em rebuild v1.13 ngắn (~350 trang) để Anh xem **bản không có wiki dump** trông thế nào, hay STOP rebuild Q3?

---

🌸 *Em xin lỗi đã ẨU TỪ BƯỚC 1. Em hứa: từ giờ KHÔNG batch big. Làm tới đâu fix tới đó. Bố cục trang trước, OCR sau.*
