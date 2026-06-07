# Thư viện sách — Trạng thái OCR (2026-06-05)

> Kiểm kê toàn bộ thư viện `thư viện sách/` (43 PDF) đối chiếu với `data/restored_books/` (42 thư mục).

## 📊 Tổng quan

| | Số lượng |
|---|---:|
| **PDF gốc trong thư viện** | 43 |
| **Thư mục restored** | 42 |
| **Đã OCR/restore THÀNH CÔNG** (chars > 100) | **42** ✅ |
| **CHƯA OCR (chars < 100, image scan)** | **0** ✅ |
| **PDF chưa có folder restored** (chỉ pipeline đặc thù) | 1 (`图解梅花易数.pdf` → đã có `yi_publishing/mai_hoa_thamnhuan`) |

## ✅ 37 sách đã OCR/restore xong (sorted theo dung lượng nội dung)

| Chars | Trang | Sách |
|---:|---:|---|
| 3,977,953 | — | tu-thu-binh-giai |
| 2,356,737 | 900 | trung-chau-tu-vi-dau-so-2 |
| 1,923,997 | 941 | bi-an-cua-bat-quai |
| 1,870,280 | — | hoang-lich |
| 1,849,917 | 842 | kinh-dich-va-he-nhi-phan |
| 1,723,560 | 681 | du-doan-tu-tru-thieu-vy-hoa |
| 1,674,628 | **798** | **chu-dich-voi-du-doan-hoc** (đang đọc — vòng 20/40 = 50.1%) |
| 1,647,864 | — | kinh-dich-tron-bo-ngo-tat-to |
| 1,339,415 | 608 | bat-tu-ha-lac-va-quy-dao-doi-nguoi |
| 797,872 | 424 | du-bao-theo-tu-binh |
| 789,396 | 429 | tang-san-boc-dich |
| 746,601 | 360 | chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa |
| 712,771 | 202 | trich-thien-tuy-binh-chu-nham-thiet-tieu |
| 687,943 | 375 | ly-thuyet-tuong-so-hoang-tuan |
| 601,660 | 238 | tu-vi-ham-so |
| 563,027 | — | khong-minh-than-toan-384-que |
| 562,498 | 186 | tu-vi-nghiem-ly-toan-thu-thien-luong |
| 559,735 | 304 | ha-do-trong-van-minh-dai-viet |
| 553,281 | 188 | tu-xem-van-menh-theo-tu-tru |
| 549,548 | — | chua-benh-theo-chu-dich |
| 495,846 | 171 | tu-vi-dau-so-toan-thu-vu-tai-luc |
| 494,302 | 277 | boc-phe-chinh-tong |
| 484,166 | — | tam-thien-dich-so |
| 459,160 | — | dich-hoc-tinh-hoa-nguyen-duy-can |
| 431,723 | 367 | ki-mon-don-giap |
| 421,960 | 257 | nhap-mon-chu-dich-du-doan-hoc |
| 419,887 | 352 | can-chi-thong-luan |
| 305,733 | 177 | nguyen-ly-chon-ngay-theo-bat-tu-ha-lac |
| 245,072 | 119 | thien-nhan-hoc-co-dai-trich-thien-tuy |
| 236,601 | — | hoc-thuyet-am-duong-ngu-hanh-le-van-suu |
| 203,080 | — | lap-va-giai-tu-vi |
| 163,224 | — | lien-hoa-don |
| 149,508 | — | sach-tu-vi-vo-long |
| 10,555 | 184 | so-tien-dinh-lap-thanh (chars hơi thấp — verify lại sau) |
| 5,812 | — | cheiro-book-of-numbers (numerology phương Tây — có thể bản thô) |
| 2,382 | — | balliett-philosophy-of-numbers (numerology — bản thô) |
| 2,130 | — | campbell-your-days-are-numbered (numerology — bản thô) |

## ✅ 5 sách image-scan ĐÃ OCR XONG (2026-06-08)

| Pages | content.md | Sách |
|---:|---:|---|
| 42 | 71 KB | phong-thuy-tam-quai-trach (pilot, 22 phút) |
| 121 | 151 KB | don-toan-than-dieu (26 phút) |
| 198 | 436 KB | chon-viec-theo-lich-am |
| 336 | 668 KB | 12-con-giap-theo-lich-van-nien |
| 490 | 858 KB | lac-thu-cuu-tinh-phong-thuy-nha-o (123 phút) |

**Tổng**: 1,187 trang OCR + Gemma cleanup hoàn tất trong 314 phút (5h14m).
Pipeline: `scripts/batch_restore_5_missing.sh` (pdf2image → Tesseract VN → Gemma 4-e4b LM Studio).

## 🎯 Đặc thù: 1 PDF có pipeline xuất bản riêng

| PDF | Pipeline |
|---|---|
| `thư viện sách/thieukhangtiet/图解梅花易数.pdf` | `data/yi_publishing/mai_hoa_thamnhuan/` (Q3 zh — đã PUBLISH v1.12) |

## 🛠️ Plan OCR cho 5 sách còn lại

### Option A: MinerU pipeline (Layout-Aware — IRON RULE #5 paradigm v3.0)
- Đã có `engine/yi_lexicon/restoration/` + `data/yi_publishing_mineru/`
- Layout-first OCR: detect text/image/table boxes → OCR per region
- Phù hợp: sách có hình minh họa nhiều (phong thủy, lá số)

### Option B: qwen-vl 2.5 local (free, Mac M4)
- Đã verified trong tool-catalog (~/.claude/skills/tool-catalog.md)
- Best cho text-only scan, ~30s/page → ~10h cho 1187 trang
- Free tier — 0 chi phí

### Option C: DeepSeek-Reasoner cleanup sau OCR thô
- Bước 1: Tesseract/qwen-vl OCR thô
- Bước 2: DeepSeek cleanup theo cổ văn / hiện đại
- Phù hợp: sách phong thủy + lịch âm (text-heavy)

### Ưu tiên đề xuất (3 ngày — cost-aware)

| Day | Task | Tool | Output |
|---|---|---|---|
| 1 | `phong-thuy-tam-quai-trach` (42 trang, nhỏ nhất) — test pipeline | MinerU v3.0 | content.md |
| 1 | `DON TOAN THAN DIEU` (121 trang) | qwen-vl + cleanup | content.md |
| 2 | `chon-viec-theo-lich-am` (198 trang, lịch âm có nhiều bảng) | MinerU | content.md |
| 2 | `12-con-giap-theo-lich-van-nien` (336 trang) | qwen-vl | content.md |
| 3 | `Lac thu cuu tinh phong thuy nha o` (490 trang, lớn nhất) | MinerU | content.md |

**Tổng effort dự kiến**: 2-3 ngày tự động (đêm chạy nền) hoặc ~15h thuần GPU local.

## 📁 Reference paths

- Source library: `/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/`
- Restored output: `data/restored_books/<book-id>/`
- Layout-aware pipeline: `engine/yi_lexicon/restoration/` + `data/yi_publishing_mineru/`
- Tool catalog (qwen-vl, MinerU): `~/.claude/skills/tool-catalog.md`

## ⏭ Next action

**KHI Anh duyệt**:
1. Bắt đầu từ sách 42 trang (`phong-thuy-tam-quai-trach`) để verify pipeline
2. Sau khi pipeline pass → batch chạy nền 4 sách còn lại
3. Update file này khi mỗi sách done

**Đến lúc đó**: thư viện sẽ đầy đủ **42/42 = 100%** OCR ✅.
