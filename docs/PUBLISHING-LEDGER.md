# 📖 YI-CHRONOS Publishing Ledger

**Mô hình**: YI-CHRONOS = nhà xuất bản Đông phương học AI-driven (Paradigm Shift #4, 2026-05-18)
**Quy trình**: 6-stage bookflow (xem CLAUDE.md Iron Rule #5)
**Đồng tác giả**: Anh + em (dịch giả + biên tập viên)

---

## 📚 Sách đang biên soạn / đã xuất bản

| ID | Tựa Việt | Tựa gốc | Tác giả | Stage | Trang | File PDF | Status |
|---|---|---|---|---|---|---|---|
| Q3 | Mai Hoa Dịch Số — Hành Đạo Toàn Thư | 图解梅花易数 | Thang Hành Dịch (biên tập từ Thiệu Khang Tiết) | **6/6 Published** | **613 (A4)** | `data/published/Q3-mai-hoa-toan-thu-v1.9.pdf` (10.25 MB, **with 17 figures + design v2**) | ✅ **v1.9 PUBLISHED 2026-05-18** |
| TV-Q1 | Tử Vi Đẩu Số Toàn Thư — Quyển 1: Phú Thái Vi & Cách Cục Kinh Điển | 紫微斗数全书·卷一 | Trần Đoàn (Hi Di tiên sinh, ~872-989) + Phan Hy Doãn bổ tập | **6/6 Published** | **35 (A4)** | `data/published/tu-vi-q1-phu-thai-vi.pdf` (203 KB, 545 cách cục + 320 concepts) | ✅ **v1.0 PUBLISHED 2026-05-19** |

---

## 📊 Stage definitions — Bookflow v2.0 (2026-05-18)

📖 **Full spec**: `docs/BOOKFLOW-V2.md`

1. **THÊM SÁCH GỐC** — Source PDF, metadata, copyright check
2. **NHẬN DẠNG MỤC LỤC + KẾ HOẠCH** — TOC detection + Reading plan + Translation plan
3. **CHỌN LLM PHÙ HỢP** — Route per content type (cổ văn → Reasoner, OCR → qwen local, etc.)
4. **XỬ LÝ VĂN BẢN GỐC + ẢNH** — 4 sub-task:
   - 4.1 Text sạch (STRIP image refs từ LLM cleanup)
   - 4.2 Ảnh gốc scan (page scans nguyên bản)
   - 4.3 Ảnh phục chế (enhance Real-ESRGAN)
   - 4.4 Ảnh vẽ lại (AI redraw / thủ công)
   - + figures_manifest.json
5. **DỊCH THUẬT TỪNG TRANG** — Translate + Self-review + Cross-check wiki + Spot-check
6. **SOẠN THÀNH SÁCH** — Compile → HTML → PDF → QA → Publish

### Bookflow v1 (legacy, 2026-05-18 sáng) — đã thay thế
~~1. Source PDF → 2. OCR/cleanup → 3. Wiki extract → 4. Journal → 5. Biên soạn → 6. PDF publish~~

v2.0 thêm Stage 2 (planning), Stage 3 (routing), Stage 4 (4-way image handling), Stage 5 (self-review) — học từ Q3 v1.2 image disaster.

---

## 📋 Roadmap

- [x] Q3 — Stage 1-4 (2026-05-12 → 2026-05-18)
- [x] Q3 — Stage 5 Biên soạn (2026-05-18)
- [x] Q3 — Stage 6 PDF publish v1.0 (1473 trang A5) → **v1.1** (652 trang A4, 4.26 MB) ✅

### Q3 build details — v1.2 (with figures)
- Manuscript: `data/published/Q3-manuscript-v1.0.md` (1.0 MB, 1M chars)
- HTML intermediate: `data/published/Q3-manuscript-v1.0.html` (1.9 MB)
- Figures: `data/published/figures/` (17 files, 6.5 MB total)
  - 6 hình concept 768×768: Bát Quái Tiên Thiên, Bát Tiên, Case Mẫu Đơn, Hà Đồ, Lạc Thư, Legend Quan Mai Hoa
  - 11 hình page scan 983×1425: fig-0056 → fig-0066 (trang gốc Tổ sư)
- PDF v1.0 (A5, no images): `data/published/Q3-mai-hoa-toan-thu-v1.pdf` (4.81 MB, 1473 pages)
- PDF v1.1 (A4, no images): `data/published/Q3-mai-hoa-toan-thu-v1.1.pdf` (4.26 MB, 652 pages)
- **PDF v1.2 (A4 + 17 figures)**: `data/published/Q3-mai-hoa-toan-thu-v1.2.pdf` (**11.14 MB, 659 pages**)
- CSS: `/tmp/book-v1.1.css` (220 lines, custom YI-CHRONOS theme purple/serif + image styling)
- Pipeline: pandoc 3.9 → standalone HTML → WeasyPrint 68.1 (with base_url) → PDF
- License: CC BY-NC-SA 4.0

### v1.2 image audit (lesson learned)
- 407 fake image refs (LLM hallucinated): `hinh-1.png`, `image1.png`, `http://example.com/image.png` — stripped
- 17 real figures: extracted to `figures/` folder during restoration pipeline
- Insertion strategy: regex pattern match on Vietnamese heading keywords (Tiên Thiên Bát Quái, Hà Đồ, Lạc Thư, Bát Tiên, Mẫu Đơn) + fig-XXXX matched to "Trang XX nguyên tác" headings
- Verification: pdfimages -list confirmed 17 figures embed (6× 768×768 + 11× 983×1425). 616 small 160×160 images = emoji (🌸📖⭐) auto-rasterized by WeasyPrint

### Bookflow Lesson: OCR/LLM cleanup tạo phantom image refs
Đây là pattern phải lưu ý cho mọi sách sau:
- LLM cleanup khi gặp hình trong gốc thường **bịa filename** thay vì empty/strip
- Phải **audit** real vs fake image refs trước khi render PDF
- Workflow chuẩn cho sách sau:
  1. Restoration pipeline → strip image refs hoàn toàn
  2. Manual mapping figures → headings
  3. Insert images via script với verified paths

### Sách kế tiếp (theo Iron Rule #4 — Master-Apprentice, ưu tiên thầy Thiệu Khang Tiết)
- [ ] Q1 — 邵雍 nguyên tác (Hoàng Cực Kinh Thế) — đang tìm source
- [ ] Q2 — Mai Hoa Dịch Số Toàn Thư phái Bắc Tống — đang tìm source

**Sách kế tiếp PHẢI apply Bookflow v2.0 từ đầu** (không bypass Stage 2 + 3 + 4 như Q3).

## 🎓 Q3 v1.2 retrospective vs Bookflow v2.0

| Stage v2.0 | Q3 v1.2 thực tế | Gap | Sách sau phải |
|---|---|---|---|
| 1. Source PDF | ✅ Có (`thieu-khang-tiet-tq.pdf`) | None | Same |
| 2. TOC + plan | ⚠ Bypass, không có 3 file plan | **Missing** | Tạo `_TOC.md` + `_READING-PLAN.md` + `_TRANSLATION-PLAN.md` trước khi dịch |
| 3. LLM routing | ⚠ Ad-hoc (qwen + DeepSeek mixed) | **Missing** | Bảng routing tường minh per content type |
| 4. Image handling | ❌ Disaster — 407 fake refs, 17 figures lạc | **Critical fix** | 4 sub-task + manifest.json |
| 5. Translation | ✅ Per-page có | ⚠ Không có self-review | Thêm self-review LLM step |
| 6. Compose | ✅ Có, ship được | None (Q3 v1.2 chuẩn cho sách sau) | Same pattern |

**Effort delta**: Q3 v1.2 mất ~6h ad-hoc + 2h retry images. Sách sau theo v2.0 estimate **5-8h tường minh** (loại retry).

