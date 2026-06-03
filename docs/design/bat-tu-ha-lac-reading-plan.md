# 📖 Bát Tự Hà Lạc & Quỹ Đạo Đời Người — Kế hoạch đọc tiếp

**Tác giả**: Xuân Cang
**Tổng số trang**: 608
**Đã đọc**: ~200 trang + jump tới Tiết
**Còn lại**: ~400 trang (chủ yếu quẻ giữa + Phần Ba + Phụ lục)

---

## 🔖 BOOKMARK hiện tại (2026-06-03)

### ✅ Cụm A Sau Khảm — DONE 2026-06-03
- 5 quẻ: Di, Đại Quá, Ly, Hàm, Hằng (p213-260)
- Journal: `docs/design/ha-lac-cum-a-tham-nhuan.md`
- Paradigm cốt: NUÔI → ẨN SÚC → GIẤU SÁNG → HƯ TÂM → GIỮ TRUNG

### ✅ Cụm B Mệnh-Thân — DONE 2026-06-03
- 8 quẻ: Độn, Đại Tráng, Tấn, Minh Di, Gia Nhân, Khuê, Kiển, Giải
- Journal: `docs/design/ha-lac-cum-b-tham-nhuan.md`
- ⭐ Minh Di Hào 2: "đau đùi BÊN TRÁI nhưng sẽ mau khỏi"

### ✅ Cụm C Tổn-Ích-Quải-Cấu — DONE 2026-06-03 🆕
- 8 quẻ: Tổn, Ích, Quải, Cấu, Tụy, Thăng, Khốn, Tỉnh
- Journal: `docs/design/ha-lac-cum-c-tham-nhuan.md`
- Paradigm cốt: QUYẾT ĐỊNH (mất-được, dứt khoát)
- ⭐ Cặp Tổn-Ích: "Tổn dưới → trên cũng tổn; Tổn trên → cả hai cùng ích"
- ⭐ Case Phùng Hoan đốt khế = "mua nghĩa" cho Mạnh Thường Quân
- ⭐ Khốn + Văn Vương + Khổng Tử: "Khốn mà Hanh"

### Trang dừng đọc cuối cùng (cập nhật 2026-06-03 chiều):
- **p340** — Cụm A + B + C DONE
- Đã đọc: 49/64 quẻ (77%)
- Tiếp Cụm D Cách-Đỉnh-Chấn-Cấn (p340-380) — 9 quẻ CHUYỂN HÓA

### Trang dừng đọc trước đó:
- **p180** — vòng 1-9 (đọc tuần tự): Phần I + 22 quẻ đầu (Càn → Bí)
- **p200** — vòng 10-11: Bác/Phục/Vô Vọng/Đại Súc/Di/Khảm
- **p389-394** — JUMP tới quẻ 60 **Tiết** (Tiền Thiên founder) — đọc kỹ vì cần cho lá số anh

### Engine + Wiki coverage:
- **THOI_QUE_TABLE**: 28/64 quẻ (44%) — `engine/ha_lac/thoi_que.py`
- **PARADIGM_CASES**: 22+ case studies — `engine/ha_lac/paradigm_quy_chieu.py`
- **IRON_RULE_CROSS_LINK**: 19 keys — cross-link sách cổ với Iron Rule project
- **Seed 384 hào**: 12/384 hào (Càn + Khôn full) — `data/seeds/hexagram_lines_ha_lac.json`

---

## 📋 Quẻ ĐÃ thâm nhuần (28/64)

| # | Tên | Vòng | Paradigm key |
|---|---|---|---|
| 1 | Càn | v4-5 | tự_cường (Tứ Đức) |
| 2 | Khôn | v5 | nhu_thuận (Nam Khoái case) |
| 3 | Truân | v5 | gian_truân_có_cơ (Quang Trung-NHĐ) |
| 4 | Mông | v5 | mông_muội_cần_dạy (**gốc Iron Rule #4**) |
| 5 | Nhu | v5 | chờ_đợi (PBC paradigm Trung) |
| 6 | Tụng | v6 | tranh_tụng (Nguyễn Hoàng-Trạng Trình) |
| 7 | Sư | v6 | quân_đội_đám_đông |
| 8 | Tỷ | v6 | tỷ_quy_phục (Y Doãn + Khổng Minh) |
| 9 | Tiểu Súc | v6 | tiểu_súc_lập_ngôn (**THỜI HIỆN TẠI anh+em**) |
| 10 | Lý | v7 | lễ_dẫm_lên |
| 11 | **Thái** | v7 | đảo_vị_giao_thoa (**3 nguồn cổ confirm**) |
| 12 | **Bĩ** | v7 | đúng_vị_cách_tuyệt |
| 13 | Đồng Nhân | v7 | đại_đồng (Tiểu đồng hẹp hòi) |
| 14 | Đại Hữu | v7 | sở_hữu_lớn (Y Doãn + Cavour) |
| 15 | **Khiêm** | v8 | lao_khiêm (Hạ Vũ + Washington, **cross-link Mỗ Tử Vi**) |
| 16 | Dự | v8 | hòa_vui_tri_cơ |
| 17 | **Tùy** | v8 | tùy_thời (**Hưng Đạo Vương + Iron Rule #7**) |
| 18 | **Cổ** | v8 | đổ_nát_mà_sửa (**Mission Lexicon**) |
| 19 | Lâm | v9 | hàm_lâm (Đông Hán 4 quân tử) |
| 20 | Quan | v9 | biểu_thị_xem_xét |
| 21 | Phệ Hạp | v9 | trừ_gián (PBC paradigm TÀI+VỊ) |
| 22 | Bí | v9 | văn_chất_cân_bằng (Khổng Tử) |
| 23 | Bác | v10 | tiêu_mòn_chờ_thời (Lão Tử) |
| 24 | Phục | v10 | trở_lại (đức NHÂN, hạt cây = nhân) |
| 25 | Vô Vọng | v10 | không_kỳ_vọng (Hồ Văn Phong "biết THỜI") |
| 26 | Đại Súc | v10 | tích_trữ_lời_xưa (ĐỐC THỰC + UY QUANG) |
| 27 | 🌟 **Khảm** | v11 | **TẬP KHẢM 2 lần hiểm** (Hậu Thiên founder) |
| 28 | 🌟 **Tiết** | jump | **tiết_chế** (Tiền Thiên founder, hào 1 NĐ) |

---

## 📋 Quẻ CHƯA đọc (36/64)

### Cụm A: Sau Khảm (p213-260) — 5 quẻ
- 27 — Sơn Lôi Di (p~205)
- 28 — Trạch Phong Đại Quá (p~210)
- 30 — Thuần Ly (p~225)
- 31 — Trạch Sơn Hàm (p~230)
- 32 — Lôi Phong Hằng (p~235)

### Cụm B: Mệnh-Thân paradigm (p240-300) — 8 quẻ
- 33 — Thiên Sơn Độn
- 34 — Lôi Thiên Đại Tráng (p240)
- 35 — Hỏa Địa Tấn
- 36 — Địa Hỏa Minh Di
- 37 — Phong Hỏa Gia Nhân
- 38 — Hỏa Trạch Khuê (p263)
- 39 — Thủy Sơn Kiển
- 40 — Lôi Thủy Giải

### Cụm C: Tổn-Ích-Quải-Cấu (p300-340) — 8 quẻ
- 41 — Sơn Trạch Tổn
- 42 — Phong Lôi Ích
- 43 — Trạch Thiên Quải
- 44 — Thiên Phong Cấu
- 45 — Trạch Địa Tụy
- 46 — Địa Phong Thăng (p312)
- 47 — Trạch Thủy Khốn (p317)
- 48 — Thủy Phong Tỉnh

### Cụm D: Cách-Đỉnh-Chấn-Cấn (p340-380) — 9 quẻ
- 49 — Trạch Hỏa Cách
- 50 — Hỏa Phong Đỉnh
- 51 — Thuần Chấn
- 52 — Thuần Cấn (p345)
- 53 — Phong Sơn Tiệm
- 54 — Lôi Trạch Quy Muội
- 55 — Lôi Hỏa Phong
- 56 — Hỏa Sơn Lữ
- 57 — Thuần Tốn

### Cụm E: Cuối + Trung Phu (p378-410) — 6 quẻ
- 58 — Thuần Đoài (p378)
- 59 — Phong Thủy Hoán (p383)
- 61 — Phong Trạch Trung Phu (p394) — **đã đọc nửa khi jump Tiết**
- 62 — Lôi Sơn Tiểu Quá (p400)
- 63 — Thủy Hỏa Ký Tế
- 64 — Hỏa Thủy Vị Tế

---

## 📑 PHẦN BA & PHỤ LỤC (p420-608) — chưa đọc

- **p420-583**: PHẦN BA — Chân dung nhà văn soi chiếu (~160 trang)
  - Case studies cụ thể áp dụng paradigm cho từng nhà văn
  - Hữu ích để hiểu cách Xuân Cang "đọc đồng dạng" lá số người thật
- **p584-608**: PHỤ LỤC
  - Tiết khí + lịch âm dương
  - Bảng tiết lệnh 12 tháng

---

## 🎯 Kế hoạch đọc tiếp (priority order)

### 🥇 Priority 1 — Cụm A (Di/Đại Quá/Ly/Hàm/Hằng) — 1 vòng
**Lý do**: Liền sau Khảm, paradigm âm-dương đang chuyển. Quan trọng:
- Ly = lửa văn minh (đôi với Khảm)
- Hàm-Hằng = cảm + bền (paradigm hôn nhân + bạn bè)
- Đại Quá = "thái quá" — paradigm cảnh báo

**Effort**: 1 vòng × 20p (~p213-235)

### 🥈 Priority 2 — Cụm E cuối sách (Đoài/Hoán/Trung Phu/Tiểu Quá/Ký Tế/Vị Tế) — 1 vòng
**Lý do**: Hoán + Trung Phu + Tiểu Quá nằm SÁT Tiết và quan trọng:
- Trung Phu = Chí Thành (PBC: paradigm trung tín → chính → trung phu)
- Tiểu Quá = thái quá nhỏ (đôi với Đại Quá)
- Ký Tế / Vị Tế = đã thành / chưa thành (hai quẻ kết Kinh Dịch)

**Effort**: 1 vòng × 25p (~p394-410)

### 🥉 Priority 3 — Cụm B (8 quẻ Mệnh-Thân) — 2 vòng
**Lý do**: Cụm này có Đại Tráng, Minh Di, Khuê — paradigm rất hữu ích cho diễn giải Hà Lạc thực tế.

**Effort**: 2 vòng × 20p (~p240-300)

### 🏅 Priority 4 — Cụm C + D (17 quẻ giữa) — 4 vòng
**Lý do**: Hoàn chỉnh 64 quẻ paradigm. Có Cách + Đỉnh quan trọng.

**Effort**: 4 vòng × 20p (~p300-380)

### 🎓 Priority 5 — Phần Ba (Chân dung nhà văn) — 4 vòng
**Lý do**: HỌC CÁCH ÁP DỤNG paradigm. Đây là CASE STUDY thật — Xuân Cang "đọc lá số" của các nhà văn.

**Effort**: 4 vòng × 40p (~p420-583)

### 📚 Priority 6 — Phụ Lục (Tiết khí) — 1 vòng nhanh
**Effort**: 1 vòng × 25p

---

## 📊 Tổng effort còn lại

| Priority | Vòng | Trang | Output engine |
|---|---|---|---|
| 1 (Cụm A) | 1 | 20 | +5 quẻ THỜI_QUE_TABLE |
| 2 (Cụm E cuối) | 1 | 17 | +6 quẻ |
| 3 (Cụm B) | 2 | 60 | +8 quẻ |
| 4 (Cụm C+D) | 4 | 80 | +17 quẻ |
| 5 (Phần Ba) | 4 | 160 | +Case studies thật |
| 6 (Phụ Lục) | 1 | 25 | Tiết khí table |
| **TỔNG** | **13 vòng** | **~362 trang** | **64/64 quẻ + 1 PHẦN BA paradigm** |

---

## 🔁 Resume protocol

Khi anh nói tiếp:
- `v12` → đọc Cụm A (Priority 1)
- `tiếp cuối sách` → jump Priority 2 (Cụm E)
- `Phần Ba` → jump Priority 5 (chân dung)
- `tiếp tự nhiên` → follow priority order

### File em đọc tiếp:
`data/restored_books/bat-tu-ha-lac-va-quy-dao-doi-nguoi/pages/p0201.md` (Cụm A start — Di)

### Engine em update tiếp:
- `engine/ha_lac/thoi_que.py` — THOI_QUE_TABLE
- `engine/ha_lac/paradigm_quy_chieu.py` — PARADIGM_CASES + IRON_RULE_CROSS_LINK
- `data/seeds/hexagram_lines_ha_lac.json` — backfill 372 hào còn lại

### Journal em update:
- File này (`bat-tu-ha-lac-reading-plan.md`) — cập nhật vòng đã đọc
- `CLAUDE.md` — thêm Iron Rule mới nếu phát hiện

---

## 🌟 2 quẻ founder ĐÃ XONG (an tâm dừng)

Anh có thể dừng đây mà KHÔNG lo lá số thiếu data:
- **TIẾT** (TT) — paradigm đầy đủ (Đại Tượng + 4 đức + Hào 1 founder rule + case Tiết-sau-Hoán)
- **TẬP KHẢM** (HT) — paradigm đầy đủ (Hai nghĩa Tập + Tâm chí thành + Thiên Cơ Đật Sĩ phù suy)

Các phần đọc tiếp = enrich engine cho NGƯỜI KHÁC (khi user khác cast Hà Lạc).

---

**Lần đánh dấu cuối**: 2026-06-02 — sau commit `3bc66c8`
**Người dừng đọc**: Em (Claude) theo lệnh anh "nghỉ tay"
**Lý do dừng**: Anh muốn nghỉ xem live trước

---

## 📈 UPDATE 2026-06-02 sau session đọc tiếp + luận giải sâu

Anh chỉ thêm: "Engine ra cách cục, chưa luận giải sâu được. Có gì hay bổ sung wiki sau luận giải cho tường minh."

### Đã làm thêm
- ✅ V12 Cụm A đọc (Di/Đại Quá/Ly/Hàm/Hằng) — +5 quẻ
- ✅ V13 Cụm E cuối Kinh Dịch (Đoài/Hoán/Trung Phu/Tiểu Quá/Ký Tế/Vị Tế) — +6 quẻ
- ✅ V14 đầu Cụm B (Đại Tráng/Tấn/Minh Di) — +3 quẻ
- ✅ Module `engine/ha_lac/luan_giai_sau.py` — 3-lớp render narrative tường minh
- ✅ API endpoint `POST /api/ha-lac/luan-giai-sau`
- ✅ UI button + render markdown 3 lớp trong panel Bát Tự
- ✅ Wiki: Xuân Cang author + work + **90 concepts** Hà Lạc Xuân Cang
- ✅ Founder luận giải sâu: 6000+ chars narrative (Tiết+Tập Khảm)

### Updated coverage
- **THOI_QUE_TABLE: 42/64 quẻ (66%)** — vượt 2/3
- **PARADIGM_CASES: 23 cases**
- **IRON_RULE_CROSS_LINK: 25 keys**
- **Wiki: 90 concepts** Hà Lạc Xuân Cang
- **Trang đọc: ~285/608 (47%)**

### Pháp đắt nhất phát hiện đợt 12-14
🌟 **PBC paradigm Vị Tế (quẻ 64 — kết Kinh Dịch)**:
"Hanh ở Ký Tế (đã thành) có HẠN.
 Hanh ở Vị Tế (chưa thành) VÔ CÙNG.
 Xuân chưa đến hoa nở. Đêm chưa đến trăng tròn.
 Hy vọng tiền đồ còn nhiều.
 Ai dám bảo Vị Tế mà bất tế đâu?"
→ Kinh Dịch quy kết bằng HY VỌNG, không bằng thành tựu.

🌟 **PBC paradigm 4 quẻ tuần hoàn** (Thái-Bĩ + Ký Tế-Vị Tế):
"Đạo trời như bánh xe lăn, việc người như bàn tay lật.
 Tất cả là do CHÚNG TA — chớ vì Thái-Ký Tế mà kiêu,
 chớ vì Bĩ-Vị Tế mà buồn."

🌟 **Văn Vương + Cơ Tử case (quẻ Minh Di)**: Khi ánh sáng bị tổn —
GIẤU SÁNG, nhu thuận ngoài, giữ đức sáng trong. Văn Vương viết Kinh Dịch
trong ngục Dữu Lý. Cơ Tử giả điên giữ dòng dõi nhà Ân.

---

### Còn lại tiếp tục (priority order, chưa đọc)
- **P3.2 Cụm B còn** (Khuê, Kiển, Giải) — 1 vòng × p263-310
- **P4 Cụm C+D** (15 quẻ giữa) — 3 vòng × p310-380
- **P5 PHẦN BA — Chân dung nhà văn** (case study thật) — 4 vòng × p420-583
- **P6 PHỤ LỤC Tiết khí** — 1 vòng × p584-608

**Tổng còn lại**: ~9 vòng × ~325 trang

---

## 🆕 PHÁT HIỆN 8 SÁCH MỚI RESTORE (2026-06-02, rà công việc dở)

Anh đã âm thầm restore 8 sách KMĐG + Kinh Dịch + Hà Lạc + Can Chi. Em rà ngay:

| # | Sách | Trang | Tác giả | Đề tài |
|---|---|---|---|---|
| 1 | **kinh-dich-va-he-nhi-phan** | 842 | **Hoàng Tuấn** (Đại tá GS) | Kinh Dịch ↔ Hệ Nhị Phân (khoa học hiện đại) |
| 2 | **ly-thuyet-tuong-so-hoang-tuan** | 375 | **Hoàng Tuấn** | LÝ THUYẾT TƯỢNG SỐ + Phép tính số Hà Lạc |
| 3 | **chu-dich-voi-du-doan-hoc** | 798 | **Thiệu Vĩ Hoa** | Chu Dịch với Dự Đoán Học (kinh điển TQ) |
| 4 | can-chi-thong-luan | 352 | TQ biên dịch | Can Chi + Ngũ Hành Dự Trắc |
| 5 | bi-an-cua-bat-quai | 499 | Vương Ngọc Đức et al. | Bí ẩn Bát Quái (duy vật biện chứng) |
| 6 | ki-mon-don-giap | 367 | TQ | KMĐG (khác Đàm Liên) |
| 7 | nhap-mon-chu-dich-du-doan-hoc | 257 | Thiệu Vĩ Hoa? | Nhập môn Dự đoán |
| 8 | so-tien-dinh-lap-thanh | 184 | Thiên Phúc Nguyên Phúc | Số tử vi nhỏ |

**Tổng**: ~3674 trang sách mới → MỞ rộng GĐ học của em đáng kể.

### Ưu tiên đọc 8 sách mới (priority order)

**🥇 Priority 1A**: `ly-thuyet-tuong-so-hoang-tuan` (375p) — **Hà Lạc cùng đề tài Xuân Cang** nhưng từ góc KHOA HỌC + Y HỌC HIỆN ĐẠI. Cross-check engine của em.

**🥈 Priority 1B**: `chu-dich-voi-du-doan-hoc` (798p) — **Thiệu Vĩ Hoa kinh điển TQ** về Chu Dịch dự đoán. Bổ sung paradigm cho Mai Hoa + Bát Tự + Tử Vi (vì Thiệu Vĩ Hoa là cháu đời 29 Thiệu Khang Tiết).

**🥉 Priority 1C**: `kinh-dich-va-he-nhi-phan` (842p) — **Hoàng Tuấn paradigm Kinh Dịch ↔ Hệ Nhị Phân** — góc khoa học mới mẻ, có thể cross-link với engine binary của em.

**Sau đó**: can-chi-thong-luan + bi-an-cua-bat-quai (paradigm cổ điển bổ sung).

### 🎓 Vòng 1 Hoàng Tuấn (p1-25) — em đã đọc:

3 phát hiện ĐẮT đã wire vào engine `hoang_tuan_paradigm.py`:

1. **Paradigm "PHÂN LOẠI NHÂN HỌC CỔ"** — Hà Lạc + Tử Vi là MÔN PHÂN LOẠI cổ, 525,948 lá số = tiêu chí phân loại theo Hệ Tọa Độ Không-Thời Gian. Answer user khi hỏi "hàng triệu người cùng lá số?".

2. **KHỔNG MINH 7 cách phối hợp đánh giá người** (cực quý cho engine luận giải tính cách):
   - 1. Điều phải lẽ trái → CHÍ HƯỚNG
   - 2. Lý luận dồn thế bí → phản ứng ĐÚNG-SAI
   - 3. Mưu trí thử → KIẾN THỨC
   - 4. Đưa khó khăn → ĐỨC DŨNG
   - 5. Lợi lộc → LIÊM CHÍNH
   - 6. Hẹn công việc → CHỮ TÍN
   - 7. Rượu say → TÂM TÍNH
   - → "TÂM TƯỚNG hơn NGOẠI TƯỚNG"

3. **Cụm từ biểu tượng + tục ngữ VN** — dataset cho LLM render luận giải hấp dẫn:
   - "Bàn thuyên tại liễu" (én sầu cành liễu = tuyệt vọng)
   - "Vân đầu vọng nguyệt" (chờ trăng = hão huyền)
   - "Y cẩm kỵ ngưu" (áo gấm cưỡi trâu = giả dối)
   - "Ngọc thụ lâm phong" (cây ngọc gặp gió = quý nhân gặp nạn)
   - + tục ngữ Việt: "đời cha ăn mặn đời con khát nước", "lắm sãi không ai đóng cửa chùa"...

4. **Phương pháp 14 BƯỚC Hoàng Tuấn** — chi tiết hơn Xuân Cang. Có **bước 9 quẻ THỂ + DỤNG** (em đã wire) + **bước 10 NIÊN MỆNH** so quẻ Tiên Thiên (chưa wire) — TODO sau.

**Bookmark Hoàng Tuấn**: p25/375 — còn ~350 trang (18 vòng × 20p).
