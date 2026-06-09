# 📚 THƯ VIỆN YI-CHRONOS — CATALOG TOÀN BỘ

> 42 sách Đông phương học đã restored (OCR + cleanup) — phân loại theo 8 hệ phái.
> Cập nhật: 2026-06-09

## 🗂️ Tổ chức thư mục

```
data/restored_books/
├── LIBRARY-INDEX.md          ← file này (mục lục master)
├── by-school/                ← phân loại theo hệ phái (SYMLINKS — không trùng dung lượng)
│   ├── 01-tu-vi-dau-so/      (6 cuốn · 18.5 MB)
│   ├── 02-bat-tu-tu-binh/    (9 cuốn · 27.8 MB)
│   ├── 03-kinh-dich-chu-dich/(8 cuốn · 27.2 MB)
│   ├── 04-boc-phe-boc-dich/  (4 cuốn · 8.5 MB)
│   ├── 05-phong-thuy/        (3 cuốn · 8.2 MB)
│   ├── 06-trach-cat-lich/    (5 cuốn · 8.9 MB)
│   ├── 07-ly-so-khac/        (4 cuốn · 7.7 MB)
│   └── 08-numerology-tay-phuong/ (3 cuốn · 28 KB)
└── <book-slug>/              ← folder gốc mỗi sách (content.md + pages/ + manifest.json)
    ├── content.md            ← bản sạch markdown đã OCR
    ├── manifest.json         ← metadata
    └── pages/                ← ảnh scan từng trang (nếu có)
```

> **Lưu ý**: subfolders `by-school/*` chỉ chứa SYMLINKS trỏ về folder gốc.
> Engine code (path hardcoded) vẫn dùng `data/restored_books/<book-slug>/content.md` — không ảnh hưởng.

---

## 🌌 1. TỬ VI ĐẨU SỐ — 6 cuốn

📂 `by-school/01-tu-vi-dau-so/` → xem [README riêng](by-school/01-tu-vi-dau-so/README.md)

| Sách | Tác giả / Trường phái | Status | Note |
|---|---|---|---|
| 🥇 **trung-chau-tu-vi-dau-so-2** | Vương Đình Chỉ (Bắc phái) | ✅ thâm nhuần 100% (32 vòng) | Sách cốt engine v3/v4 |
| tu-vi-dau-so-toan-thu-vu-tai-luc | Vũ Tài Lục | restored | Toàn Thư VN |
| tu-vi-nghiem-ly-toan-thu-thien-luong | Thiên Lương | restored | Nghiệm lý VN |
| tu-vi-ham-so | Hàm Số (VN) | restored | — |
| sach-tu-vi-vo-long | Võ Long (VN) | restored | — |
| lap-va-giai-tu-vi | (VN) | restored | tutorial — lập + giải |

## 📿 2. BÁT TỰ / TỬ BÌNH — 9 cuốn

📂 `by-school/02-bat-tu-tu-binh/` → xem [README riêng](by-school/02-bat-tu-tu-binh/README.md)

| Sách | Tác giả | Status | Note |
|---|---|---|---|
| 🥇 **du-doan-tu-tru-thieu-vy-hoa** | Thiệu Vĩ Hoa | ✅ thâm nhuần partial | Iron Rule master 2026-05-27 |
| **trich-thien-tuy-binh-chu-nham-thiet-tieu** | Nhâm Thiết Tiều bình chú | restored | Trích Thiên Tủy chính tông |
| thien-nhan-hoc-co-dai-trich-thien-tuy | Trích Thiên Tủy gốc | restored | — |
| tu-thu-binh-giai | (cổ điển) | restored | Bình giải |
| bat-tu-ha-lac-va-quy-dao-doi-nguoi | Hà Lạc | restored | bridge Hà Lạc–Bát Tự |
| nguyen-ly-chon-ngay-theo-bat-tu-ha-lac | Hà Lạc | restored | trạch cát |
| can-chi-thong-luan | (cổ điển) | restored | căn cứ can chi |
| du-bao-theo-tu-binh | hiện đại | restored | dự báo Tử Bình |
| tu-xem-van-menh-theo-tu-tru | hiện đại | restored | tự học |

## ☯ 3. KINH DỊCH / CHU DỊCH — 8 cuốn

📂 `by-school/03-kinh-dich-chu-dich/` → xem [README riêng](by-school/03-kinh-dich-chu-dich/README.md)

| Sách | Tác giả | Status | Note |
|---|---|---|---|
| 🥇 **kinh-dich-tron-bo-ngo-tat-to** | Ngô Tất Tố (VN) | ✅ thâm nhuần p51-200 (19 quẻ) | Iron Rule #5 chính |
| chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa | Thiệu Vĩ Hoa | restored | cách dự đoán có ví dụ |
| chu-dich-voi-du-doan-hoc | hiện đại | restored | — |
| nhap-mon-chu-dich-du-doan-hoc | hiện đại | restored | tutorial |
| dich-hoc-tinh-hoa-nguyen-duy-can | Nguyễn Duy Cần | restored | triết học Dịch VN |
| kinh-dich-va-he-nhi-phan | hiện đại | restored | cross-disciplinary |
| chua-benh-theo-chu-dich | (chuyên đề) | restored | y học |
| bi-an-cua-bat-quai | (chuyên đề) | restored | Bát Quái |

## 🪙 4. BỐC PHỆ / BỐC DỊCH — 4 cuốn

📂 `by-school/04-boc-phe-boc-dich/` → xem [README riêng](by-school/04-boc-phe-boc-dich/README.md)

| Sách | Tác giả | Status |
|---|---|---|
| boc-phe-chinh-tong | (cổ điển TQ) | restored — kinh điển Bốc Phệ |
| tang-san-boc-dich | (cổ điển TQ) | restored — Tăng San kinh điển |
| khong-minh-than-toan-384-que | Khổng Minh (truyền thuyết) | restored — 384 quẻ tiên tri |
| don-toan-than-dieu | (Mai Hoa nhánh) | restored — Đôn toán thần diệu |

## 🏛 5. PHONG THỦY — 3 cuốn

📂 `by-school/05-phong-thuy/` → xem [README riêng](by-school/05-phong-thuy/README.md)

| Sách | Note |
|---|---|
| lac-thu-cuu-tinh-phong-thuy-nha-o | Lạc Thư Cửu Tinh nhà ở |
| phong-thuy-tam-quai-trach | Tam Quái Trạch |
| ha-do-trong-van-minh-dai-viet | Hà Đồ + văn minh Đại Việt |

## 📅 6. TRẠCH CÁT / LỊCH — 5 cuốn

📂 `by-school/06-trach-cat-lich/` → xem [README riêng](by-school/06-trach-cat-lich/README.md)

| Sách | Note |
|---|---|
| hoang-lich | Hoàng Lịch (chính tông) |
| chon-viec-theo-lich-am | Chọn việc theo lịch âm |
| 12-con-giap-theo-lich-van-nien | 12 con giáp lịch vạn niên |
| so-tien-dinh-lap-thanh | Số tiền định lập thành |
| tam-thien-dich-so | Tam thiên dịch số |

## 🌟 7. LÝ SỐ KHÁC — 4 cuốn

📂 `by-school/07-ly-so-khac/` → xem [README riêng](by-school/07-ly-so-khac/README.md)

| Sách | Hệ |
|---|---|
| hoc-thuyet-am-duong-ngu-hanh-le-van-suu | Âm Dương Ngũ Hành — Lê Văn Sửu |
| ki-mon-don-giap | Kỳ Môn Độn Giáp |
| ly-thuyet-tuong-so-hoang-tuan | Tướng số — Hoàng Tuấn |
| lien-hoa-don | Liên Hoa Đôn (hệ ít phổ biến) |

## 🌐 8. NUMEROLOGY TÂY PHƯƠNG — 3 cuốn

📂 `by-school/08-numerology-tay-phuong/` → xem [README riêng](by-school/08-numerology-tay-phuong/README.md)

| Sách | Tác giả | Note |
|---|---|---|
| balliett-philosophy-of-numbers | Mrs. L. Dow Balliett | nền tảng numerology phương Tây |
| campbell-your-days-are-numbered | Florence Campbell | thực hành numerology |
| cheiro-book-of-numbers | Cheiro (William J. Warner) | Cheiro cổ điển |

---

## 🔍 TRA CỨU NHANH

### Tìm theo từ khóa chính

| Từ khóa | Sách liên quan |
|---|---|
| **Tử Vi Bắc phái** | trung-chau-tu-vi-dau-so-2 |
| **Tử Vi Bát Tự bridge** | bat-tu-ha-lac-va-quy-dao-doi-nguoi |
| **Trích Thiên Tủy** | thien-nhan-hoc-co-dai-trich-thien-tuy + trich-thien-tuy-binh-chu-nham-thiet-tieu |
| **Thiệu Vĩ Hoa** | du-doan-tu-tru-thieu-vy-hoa + chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa |
| **Hà Lạc** | bat-tu-ha-lac + nguyen-ly-chon-ngay-theo-bat-tu-ha-lac |
| **Ngô Tất Tố** | kinh-dich-tron-bo-ngo-tat-to |
| **Khổng Minh** | khong-minh-than-toan-384-que |
| **Ngũ Hành / Âm Dương** | hoc-thuyet-am-duong-ngu-hanh-le-van-suu |
| **Kỳ Môn Độn Giáp** | ki-mon-don-giap |
| **Trạch cát (chọn ngày)** | hoang-lich + chon-viec-theo-lich-am + nguyen-ly-chon-ngay-theo-bat-tu-ha-lac |

### Tìm theo lĩnh vực ứng dụng

- **Luận mệnh cá nhân** → 01 Tử Vi + 02 Bát Tự
- **Chiêm sự / dự báo sự kiện** → 03 Kinh Dịch + 04 Bốc Phệ
- **Chọn ngày tốt** → 06 Trạch Cát + nguyen-ly-chon-ngay-theo-bat-tu-ha-lac
- **Phong thủy nhà / mộ** → 05 Phong Thủy
- **Sức khỏe (bệnh theo Dịch)** → chua-benh-theo-chu-dich
- **Tướng pháp** → ly-thuyet-tuong-so-hoang-tuan
- **Quân sự / chiến lược cổ** → ki-mon-don-giap + khong-minh-than-toan-384-que

---

## 📊 Sách CỐT đã thâm nhuần / wire vào engine

| Sách | Số trang đọc | Engine module |
|---|---|---|
| **trung-chau-tu-vi-dau-so-2** | 900/900 (100%) — 32 vòng | `chiem_phu_the_v3.py` (34 rules) + `chiem_phu_the_v4.py` (13 rules) + `phu_the_partner_traits.py` (60+ paradigm) + `trung_chau_paradigm.py` (3 Iron Rules + 20+ paradigm) |
| **kinh-dich-tron-bo-ngo-tat-to** | p51-200 (19 quẻ Kiền/Khôn/Truân/Mông/Nhu/Tụng/Sư/Tỷ/Tiểu Súc/Lý/Thái/Bĩ/Đồng Nhân/Đại Hữu/Khiêm/Dự/Tùy/Cổ/Lâm) | wiki citations Mai Hoa |
| **du-doan-tu-tru-thieu-vy-hoa** | partial — Iron Rule master | `engine/bat_tu/*` |

> **Roadmap**: tiếp tục thâm nhuần Q3 Trung Châu (Đại Vận), Q1 Phú Thái Vi (Trần Đoàn), Quyển 3 Mai Hoa.

---

## 📁 File trợ giúp

- `markitdown_batch_summary.json` — log batch OCR/cleanup
- `ocr_8_missing_summary.json` — log OCR sót

> Mỗi sách cốt có journal riêng trong `docs/design/trung-chau-q2-vong-*.md`,
> `docs/design/mai-hoa-tham-nhuan-*.md`, `docs/design/kinh-dich-*.md`...
