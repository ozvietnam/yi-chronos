# Thư Viện Tinh Hoa — Ưu Tiên Tiêu Hoá (Track C)

> Tổng hợp 2026-06-26. Hai luồng: **Lane A** (máy auto-digest sách đã có) · **Lane B** (Anh đọc sâu sách tổ sư, theo Global Iron Rule "đọc sâu 20 trang").
> Bám hạ tầng thật: `books.json` · `source_tiers.yaml` · `data/restored_books/` · `wiki.sqlite3` (bảng `passages` + `atomic_questions`). Tôn trọng Iron Rule #3 (đa phái độc lập, không ép 1 phái).

**Ký hiệu trạng thái:** ✅ ĐÃ TIÊU HOÁ (có atoms/bảng tra) · 📄 PASSAGES-ONLY (text trong wiki, chưa rút Q&A) · 📕 PDF THÔ (restored, 0 atom) · 🗑️ FILLER (stub stage-1, không tier).

---

## PHẦN 1 — DANH SÁCH ƯU TIÊN TIÊU HOÁ (sách ĐÃ CÓ — Lane A máy auto-digest)

Tiêu chí xếp: (a) tier — (b) độ CỐT-LÕI với hệ (phái gốc Thiệu Khang Tiết / Trần Đoàn; nền âm-dương-ngũ-hành / Kinh Dịch) — (c) đang dang dở mà cốt-lõi.

| # | Sách | Tier | Phái / nền | Trạng thái | Lý do TINH HOA |
|---|---|---|---|---|---|
| 1 | **Mai Hoa Dịch Số q1q2** (`mai-hoa-dich-so-q1q2`, 482 passages) | A | Mai Hoa — **GỐC Thiệu Khang Tiết** | 📄 | Phái GỐC của hệ (Iron #4) mà mới passages-only. Wiki có 1.941 concept Mai Hoa nhưng **0 atom** từ chính sách tổ sư → lỗ hổng nghiêm trọng nhất. |
| 2 | **Mai Hoa Dịch Số — bản Thiệu Khang Tiết** (`mai-hoa-dich-so-thieu-khang-tiet`, 47) | A | Mai Hoa — GỐC | 📄 | Cùng cụm #1, bản tổ sư trực tiếp. Atomize chung 1 lượt với #1 (Lane B đọc-sâu vì là tổ sư). |
| 3 | **Kinh Dịch Trọn Bộ — Ngô Tất Tố** (`kinh-dich-tron-bo`, 64 passages) | **S** | Common — nền 64 quẻ/384 hào | 📄 | Tier S DUY NHẤT dang dở. Authority mọi mapping bát quái–hexagram. 64 passages cho ~600 trang = chưa thấm. Nền mọi phái. |
| 4 | **Hoàng Cực Kinh Thế — Hạ sách (trọn bộ Thượng–Hạ)** | A | **GỐC Thiệu Khang Tiết** | 🗑️→📕 0 trang | Thượng đã atomize 7.154 atoms; **Hạ chưa OCR**. Đóng trọn bộ tổ sư (Iron #8). Cần OCR trước. |
| 5 | **Tăng San Bốc Dịch** (`tang-san-boc-dich`, 429 trang) | A | Lục Hào — kinh điển gốc | 📕 | Authority tuyệt đối Lục Hào. Cả phái Lục Hào hiện **0 atom**. Restored dày, mở cả phái với chi phí thấp. |

**Tiếp theo (6–15):** Thiên Nhân Học Cổ Đại–Trích Thiên Tủy (A, Bát Tự, 119tr 📕) · Trích Thiên Tủy bình chú Nhậm Thiết Tiều (A, 202tr 📕) · Bốc Phệ Chính Tông (A, Lục Hào, 277tr 📕) · Tam Thiên Dịch Số (A, Mai Hoa/Liên Hoa, cần re-OCR) · Học Thuyết ÂDNH Lê Văn Sửu (A, nền triết, ✅109 atoms — **đào sâu thêm**) · Bát Tự Hà Lạc (A, Hà Lạc, 605 passages 📄) · Dịch Học Tinh Hoa Nguyễn Duy Cần (B, cần re-OCR) · Dự Đoán Theo Tứ Trụ Thiệu Vỹ Hoa (B, Bát Tự, 673 passages 📄) · Chu Dịch Dự Đoán Ví Dụ Có Giải Thiệu Vỹ Hoa (B, Lục Hào, 356 passages 📄) · Trung Châu Phái Tử Vi–Thâm Tạo Giảng Nghĩa (B, 595tr 🗑️ — ngoại lệ duy nhất vớt khỏi batch TUVIFULL).

### Nhóm FILLER nên HOÃN (đừng tiêu hoá vội)
- **Batch TUVIFULL** (~44 cuốn stage-1, không tier) — phái Tử Vi đã có 5 corpora (~9.700 atoms) phủ tốt. Hoãn toàn bộ TRỪ Trung Châu Thâm Tạo. (Trùng Toàn Thư nhiều bản · Tử vi kim chỉ nam I–IV · Tử vi đại toàn · KHHB 1.184tr · Tam Hợp Phái · Đạo Tạng (đã có) · Tứ Hóa hiện đại.)
- **Tier C** (`source_tiers.yaml`): 12 con giáp lịch vạn niên · Số tiền định · Chọn việc theo lịch âm · Chữa bệnh theo Chu Dịch · Tử Vi Hàm Số (đã đủ). Chỉ cross-ref.
- **Bản trùng/sample** đã đánh skip + **Numerology Tây** (balliett/cheiro/campbell) — ngoài hệ Đông phương, hoãn vô thời hạn.

---

## PHẦN 2 — DANH SÁCH MỞ RỘNG (sách NÊN TẢI/MUA — có nguồn + lý do)

GAP lớn nhất theo phái: **Bát Tự kinh điển gốc** (chỉ có tier B VN, thiếu Tứ thư mệnh lý chữ Hán) · **Phật học Nikāya = TRỐNG hoàn toàn** (nền triết cho mệnh-là-động-từ) · vài lỗ hổng dị-bản Mai Hoa / Kinh Dịch học thuật.

### A. Bát Tự (Tử Bình) — Tứ thư mệnh lý gốc — GAP LỚN NHẤT
| Sách (Hán) | Tác giả | Tier | Lý do | Nguồn (FREE) |
|---|---|---|---|---|
| **子平真诠** Tử Bình Chân Thuyên | Thẩm Hiếu Chiêm | S | Định nghĩa hệ dụng-thần/cách-cục chặt nhất. Anh chỉ đích danh. | GitHub `mymmsc/books` /国学/ (đã test tải OK) |
| **穷通宝鉴** Cùng Thông Bảo Giám | Dư Xuân Đài / Từ Lạc Ngô | S | Kinh điển ĐIỀU HẬU (nhiệt-ẩm theo mùa) — đúng trục engine `ngu_hanh_nen`. Anh chỉ đích danh. | GitHub raw; scan NLC (Wikimedia) |
| **滴天髓阐微** Trích Thiên Tủy Xiển Vi | Từ Lạc Ngô bổ chú | S | Bản đầy đủ + bình chú sâu nhất (bản đang có là Nhậm Thiết Tiều). | GitHub raw |
| 三命通会 Tam Mệnh Thông Hội | Vạn Dân Anh | S | Bách khoa Tử Bình (Tứ Khố). Nguồn thần sát + nạp âm. | GitHub raw / archive.org |
| 渊海子平 Uyên Hải Tử Bình | Từ Đại Thăng | S | Sách KHAI TỔ môn Tử Bình. | GitHub raw |
| 神峰通考 Thần Phong Thông Khảo | Trương Nam | A | Góc phản biện (Iron #3 đa phái). | GitHub raw |

### B. Phật học Nikāya — nền triết Iron #9 (kho hiện = 0)
| Sách | Bản | Tier | Nguồn (verified) |
|---|---|---|---|
| **Kinh Trung Bộ** (Majjhima Nikāya) | HT Thích Minh Châu | S | archive.org/details/KinhTrungBo_201407 (200 OK) |
| **Kinh Tương Ưng Bộ** (Saṃyutta Nikāya) | HT Thích Minh Châu | S | archive.org/details/tuongungbokinh (200 OK, mirror ổn nhất) |
| Thắng Pháp Tập Yếu Luận (Abhidhamma) | HT Thích Minh Châu | A | phapthihoi.org (200 OK, PDF 2.3MB) |

### C. Mai Hoa thiện bản + Kinh Dịch học thuật (nâng bản đang có)
| Sách | Bản | Tier | Nguồn |
|---|---|---|---|
| 梅花易数 hiệu chú | Lý Phong (李峰), Hải Nam XB | A | douban 20432517 · ctext.org (cross-ref dị bản với bản Diêm Tu Triện đang có) |
| **周易古经今注** Chu Dịch Cổ Kinh Kim Chú | Cao Hanh (高亨) | S | douban 5285306 · pc1999.com (nâng Kinh Dịch lên tier học thuật) |
| 周易大传今注 Chu Dịch Đại Truyện Kim Chú | Cao Hanh | S | douban 5285307 (chú Thập Dực, đủ bộ kinh+truyện) |
| 周易本义 Chu Dịch Bản Nghĩa | Chu Hi | A | ctext.org (đối trọng Tống Nho — Iron #3) |
| 中州派初级讲义 Trung Châu sơ cấp | Vương Đình Chi | A | pdfcoffee / nayona.cn (đủ bộ với 深造 đã có) |
| 紫微斗数全书 善本 Hán | Trần Hi Di mộc bản | S | shuge.org (bản gốc canonical đối chiếu các bản VN) |

**Lưu ý kỹ thuật tải (đã verify curl):** archive.org + phapthihoi + GitHub raw = 200 OK, ưu tiên. thuvienhoasen 403 (chặn bot, cần browser UA). ctext timeout 1 lần (vốn ổn, retry).

---

## PHẦN 3 — GHI CHÚ 2-TỐC-ĐỘ (Lane A / Lane B)

**Lane A — Máy auto-digest (token Max, dư dả):** atomize sách restored/passages-only thành Q&A + bảng tra. Workhorse cho sách diễn giải/ứng dụng (Lục Hào, Bát Tự VN, Trung Châu, ÂDNH). Output vào `wiki.sqlite3` → council/sage RAG. KHÔNG atomize điều-văn/bảng-tra kiểu Q&A (sai phép dùng sách).

**Lane B — Anh đọc sâu sách TỔ SƯ (Global Iron Rule "đọc sâu 20 trang"):** Mai Hoa (Thiệu Khang Tiết), Hoàng Cực, Kinh Dịch tier-S, Phật học Nikāya. Quy trình: 20 trang → DỪNG đúc kết → 5-7 vòng hỏi Anh → tiếp. Đây là sách NỀN sinh ra Iron Rule (#4/#6/#8/#9), không phải bảng tra → máy KHÔNG được "tóm tắt 800 trang trong 5 phút". Em support, Anh đọc tay.

**Phân luồng đề xuất:**
- Lane B trước (cụm phái-gốc #1–4 Phần 1 + Nikāya Phần 2B) — lỗ hổng nhức nhất: phái GỐC mới passages-only trong khi phái Tử Vi đã giàu ~9.700 atoms.
- Lane A song song: Lục Hào (Phần 1 #5 + Bốc Phệ + Chu Dịch ví dụ) mở phái trắng với chi phí thấp (PDF đã restored); đào sâu ÂDNH Lê Văn Sửu (đào sâu > thêm mới ở nền triết xương sống).
- **3 cuốn cốt-lõi restored 0 trang → cần re-OCR TRƯỚC** (chặn kỹ thuật): Tam Thiên Dịch Số · Dịch Học Tinh Hoa · Hoàng Cực Hạ.

### File tham chiếu (tuyệt đối)
- `/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/books.json`
- `/Users/ozvietnamdesktop/Desktop/yi/data/yi_lexicon/source_tiers.yaml`
- `/Users/ozvietnamdesktop/Desktop/yi/data/restored_books/`
- `/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3` (bảng `passages` + `atomic_questions`)
- Nguồn Bát Tự: GitHub `mymmsc/books` /国学/ + mirror `duanYou/books-1`
