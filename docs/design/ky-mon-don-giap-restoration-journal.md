# Restoration Journal — Kỳ Môn Độn Giáp (Đàm Liên)

**Sách**: Kỳ Môn Độn Giáp — Đàm Liên, NXB Thời Đại
**PDF gốc**: `/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/Kỳ Môn Độn Giáp .pdf`
**Tổng**: 367 trang scanned (không có text layer)
**Method**: pdftoppm 200dpi + tesseract -l vie + đọc + extract + improve engine
**Pattern**: Mỗi batch 10 pages = 1 commit. Workflow: OCR → đọc → insight → engine improvement → commit.

---

## Tiến độ tổng

| Batch | Pages | Trạng thái | Insight chính | Commit |
|---|---|---|---|---|
| Sample | 1-20 | ✅ Done | Đàm Liên paradigm + 2 hệ KMDG + 5 cổ thư | `4aed3de` |
| 1 | 21-30 | ✅ Done | Tam Kỳ Lục Nghi mapping + Cửu tinh 2 hệ tên + nguyệt gia rule + Dương/Âm độn chiều | `31c2c04` |
| 2 | 31-40 | ✅ Done | 4 tầng Âm Dương Bàn + "Theo 3 tránh 5" + corrected 5 cat_hung Cửu tinh | `cb78a4d` |
| 3 | 41-50 | ✅ Done | **25+ Cách Cục KMDG canon + auto-detection engine** (Hình Cách / Phi Điểu Trật Huyệt / Giao Thái / 7 cách cục đơn giản) | `ed522db` |
| 4 | 51-60 | ✅ Done | Chương II bố cục — 4320/1080/72/18 cục + tiết vs trung khí + Phù Đầu rule + Trí Nhuận (giải thích chabu/zhirun) | _(this commit)_ |
| ... | ... | Backlog | Toàn bộ 307 trang còn lại | future sessions |

---

## Batch 0 — Sample pages 1-20 (đã commit `4aed3de`)

**Cover**: Đàm Liên, "Kỳ Môn Độn Giáp", NXB Thời Đại, series "Tìm hiểu văn hóa phương Đông".

**Lời nói đầu**: KMDG = 1 trong tam đại cổ bốc (Kỳ Môn / Thái Ất / Lục Nhâm). Đàm Liên BÁC BỎ paradigm mê tín.

**Chương I — Khái niệm cơ bản (pages 9-20+)**:
- KMDG = "kết hợp dung hoà giữa đa tư duy, cái lập thể và sự vận động, giữa thời gian, không gian và những con số"
- Phương vị TƯƠNG ĐỐI (tùy trung tâm)
- 9 cung không gian: Đông/Tây/Nam/Bắc/Trung + 4 hướng phụ
- 2 hệ: Chuyển bàn (4 cổ thư) vs Phi bàn (Pháp khiếu — sách Đàm Liên)
- 5 cổ thư canon: Diễn nghĩa, Tống tông, Ngũ long quy, Bí cực toàn thư, Pháp khiếu

**Engine improvements**:
- `engine/ky_mon/wiki.py`: thêm 3 sections (co_thu_canon, he_kmdg, source_book) + to_su.lineage_note
- UI: subtitle dùng quote Đàm Liên, intro thêm 2 card

---

## Workflow per batch (template)

Mỗi batch em sẽ:

1. **OCR** (~2-3 phút):
   ```bash
   cd /tmp/kmdg_sample
   pdftoppm -f START -l END -r 200 "/Users/.../Kỳ Môn Độn Giáp .pdf" p -png
   for i in $(seq START END); do
     tesseract "p-$(printf '%03d' $i).png" \
       data/yi_restored/ky-mon-don-giap-dam-lien/raw_ocr/page-$i -l vie
   done
   ```

2. **Đọc + extract** (~10 phút):
   - Đọc raw_ocr files
   - Note errors OCR (Tesseract Việt thường lỗi với chữ KMDG đặc thù)
   - Extract: terminology mới, structure mới, insight đắt, hình ảnh quan trọng

3. **Engine improvements** (~10-15 phút):
   - Update `engine/ky_mon/constants.py` nếu có terminology mới
   - Update `engine/ky_mon/wiki.py` nếu có concept mới hoặc clarification cũ
   - Update `engine/ky_mon/cast.py` nếu có rule logic mới
   - Update UI nếu có info quan trọng cho user

4. **Tests + commit** (~5 phút):
   - Run pytest
   - git add specific
   - Commit message: `feat(ky-mon): batch X pages P-P' — <insight tóm>`

5. **Journal update** (~3 phút):
   - Update tiến độ table
   - Add section "Batch X" với insights + improvements

**Estimated 30-45 phút per batch**. Phiên này realistic 3-5 batches.

---

## Batch 1 — Pages 21-30: Tam Kỳ Lục Nghi + Cửu tinh hai hệ tên

### OCR + đọc

10 pages OCR clean. Tesseract Việt chất lượng tốt — vài lỗi nhỏ: "Quý" → "Canh" trong bảng Dương độn 2, "Tuất" → "Mão" trong list Tứ Quý (em note + correct theo cổ điển).

### Insights chính

1. **9 thiên can KMDG = Tam Kỳ + Lục Nghi (ẨN Giáp)**:
   - **Tam Kỳ** = 3 thiên thể sáng:
     - Đinh 丁 = **Tinh kỳ** (sao)
     - Bính 丙 = **Nguyệt kỳ** (mặt trăng)
     - Ất 乙 = **Nhật kỳ** (mặt trời)
   - **Lục Nghi** = 6 nghi ẩn 6 Giáp tuần:
     - Mậu 戊 = Giáp Tý tuần
     - Kỷ 己 = Giáp Tuất tuần
     - Canh 庚 = Giáp Thân tuần
     - Tân 辛 = Giáp Ngọ tuần
     - Nhâm 壬 = Giáp Thìn tuần
     - Quý 癸 = Giáp Dần tuần
   - **Giáp 甲 ẨN** không xuất hiện trong bàn → gốc tên "**Độn Giáp**" (giấu Giáp)

2. **Cửu tinh có 2 hệ tên gọi song song**:
   - Hệ KMDG: Thiên Bồng / Nhậm / Xung / Phụ / Cầm / Tâm / Trụ / Anh / Nhuế
   - Hệ Huyền Không Phi Tinh: Nhất bạch / Nhị hắc / Tam bích / Tứ lục / Ngũ hoàng / Lục bạch / Thất xích / Bát bạch / Cửu tử
   - Mapping 1↔1 theo số cung Lạc Thư

3. **Phương pháp xác định Nguyên cho Kỳ Môn Nguyệt Gia** (60 tháng = 1 nguyên, 5 năm):
   - Niên can Giáp/Kỷ + niên chi **Tứ Mạnh** (Dần Thân Tỵ Hợi) → Thượng Nguyên (cung Khảm số 1)
   - Niên chi **Tứ Trọng** (Tý Ngọ Mão Dậu) → Trung Nguyên (cung Đoài số 7)
   - Niên chi **Tứ Quý** (Thìn Tuất Sửu Mùi) → Hạ Nguyên (cung Tốn số 4, đều âm độn)

4. **Quy luật Dương độn vs Âm độn xếp 9 can**:
   - **Dương độn 陽遁** (Đông Chí → Hạ Chí, 6 tháng): xếp **THUẬN chiều** (cung số 1→9)
   - **Âm độn 陰遁** (Hạ Chí → Đông Chí, 6 tháng): xếp **NGƯỢC chiều** (cung số 9→1)
   - Mỗi độn có 9 cục (1-9) khác nhau, phụ thuộc tiết khí + nguyên

### Engine improvements

1. `engine/ky_mon/constants.py`: thêm 6 hằng số mới:
   - `TAM_KY_FULL_NAME` (Nhật/Nguyệt/Tinh kỳ + thiên thể + ngũ hành)
   - `LUC_NGHI_GIAP_MAPPING` (6 mappings Lục Nghi ↔ Giáp ẩn)
   - `CUU_TINH_NUMBER_NAME` (mapping số → Nhất bạch/... + cross-ref KMDG tinh name)
   - `TU_MANH`, `TU_TRONG`, `TU_QUY` (12 chi phân 3 nhóm)
   - `NGUYET_GIA_NGUYEN_RULE` (rule xác định Nguyên cho nguyệt gia)
   - `DUONG_AM_DON_RULE` (chiều xếp + tiết khí range)

2. `engine/ky_mon/wiki.py`: thêm 3 sections trong WIKI:
   - `tam_ky_luc_nghi` — overview + tam_ky + luc_nghi + insight về Giáp ẨN
   - `cuu_tinh_two_naming` — mapping 9 sao 2 hệ tên
   - `phuong_phap_an_cuc` — 4 hệ thời gian (niên/nguyệt/nhật/thời gia) + nguyên rule + Dương/Âm độn

3. UI `KyMonPanel.vue` intro: thêm 2 components mới
   - Card "🔑 Tam Kỳ + Lục Nghi" — 2 cột (3 Kỳ / 6 Nghi) + insight
   - `<details>` "⭐ Cửu tinh — 2 hệ tên gọi" collapsible expand-on-demand

4. Tests: thêm 5 tests
   - `test_tam_ky_full_name_3_thien_the`
   - `test_luc_nghi_giap_mapping`
   - `test_cuu_tinh_two_naming_mapping`
   - `test_nguyet_gia_nguyen_rule`
   - `test_duong_am_don_chieu`

### Verification

- 18/18 tests PASS (13 cũ + 5 mới)
- Webapp build clean (1749 modules, 3.03s)
- 10 pages OCR saved `data/yi_restored/ky-mon-don-giap-dam-lien/raw_ocr/page-{21..30}.txt`

---

## Batch 2 — Pages 31-40: Cấu trúc 4 tầng Âm Dương Bàn + phân cấp cát/hung Cửu tinh

### Insights chính

1. **Âm Dương Bàn HOÀN CHỈNH = 4 tầng đồng tâm**:
   - Tầng 1 (đáy, lớn nhất, CỐ ĐỊNH): **Địa Bàn** 地盤 — 8 cung Bát Quái cố định
   - Tầng 2: **Môn Bàn** — 8 môn (Chuyển bàn xoay, Phi bàn biến theo giờ)
   - Tầng 3: **Thiên Bàn** 天盤 — Lục Nghi Tam Kỳ + 9 sao (xoay theo Trực Phù)
   - Tầng 4 (đỉnh, nhỏ nhất): **Thần Bàn** 神盤 — 8 thần (Phi bàn chỉ 1 đường tròn)

2. **Trung cung trick**: Trung cung số 5 GỬI vào cung Khôn số 2 (vì 3 tầng dưới che lấp Trung cung — không nhìn thấy trực tiếp).

3. **Bát thần thứ tự (canonical)**: Trực Phù → Đằng Xà (rắn bay) → Thái Âm → Lục Hợp → Câu Trần → Chu Tước (= Huyền Vũ) → Cửu Địa → Cửu Thiên. Dương độn xếp xuôi, Âm độn xếp ngược.

4. **Quy tắc "Theo 3 tránh 5"** (proverb cốt):
   - **3 cát môn**: Khai, Hưu, Sinh
   - **5 hung môn**: Thương, Đỗ, Cảnh, Tử, Kinh
   - Rule: chọn cát → hành động, tránh hung → đợi thời

5. **Phân cấp Cửu tinh CHÍNH XÁC** (em đã set SAI ở wiki ban đầu, batch 2 sửa):
   - **3 Đại cát**: Phụ 輔, Cầm 禽, Tâm 心
   - **2 Tiểu cát**: Xung 沖, Nhậm 任
   - **2 Đại hung**: Bồng 蓬, Nhuế 芮
   - **2 Tiểu hung**: Trụ 柱, Anh 英
   - → Sửa: Cầm + Tâm từ "cát" → **"đại cát"**, Xung từ "trung bình" → **"cát"**, Trụ + Anh từ "trung bình" → **"hung"**

6. **Sinh khắc Môn ↔ Cung**:
   - Mỗi môn có ngũ hành. Đặt vào cung → check sinh/khắc/đồng
   - VD: Khai môn (Kim) cung Chấn/Tốn (Mộc) → Mộc khắc Kim → "kim khắc" suy giảm cát
   - VD: Thương môn (Mộc) cung Khôn/Cấn (Thổ) → Mộc khắc Thổ → tăng hung
   - Principle: cat_hung tổng = (cat_hung gốc) × (sinh/khắc cung) × (mùa hợp)

7. **Mùa hợp/khắc cho Cửu tinh**:
   - Thiên Bồng (Thủy): hợp xuân/hè, khắc thu/đông
   - Thiên Nhuế (Thổ): hợp đông/thu, khắc xuân/hè
   - → Đàm Liên gắn từng tinh với mùa hợp — thêm 1 chiều luận

### Engine improvements

1. `engine/ky_mon/constants.py`:
   - `TINH_CAT_HUNG` corrected (5 sao thay đổi giá trị)

2. `engine/ky_mon/wiki.py`:
   - Section "am_duong_ban_4_tang" (4 tầng + Trung cung trick)
   - Section "theo_3_tranh_5" (3 cát + 5 hung + nuance từng môn)
   - Section "cuu_tinh_phan_cap" (đại/tiểu cát/hung documented)
   - Section "sinh_khac_mon_cung" (rule luận sinh khắc)
   - Section "mua_hop_khac_tinh" (Thiên Bồng/Nhuế mùa hợp/khắc)
   - `WIKI['tinh']` updated cat_hung cho 5 sao (sync với TINH_CAT_HUNG)

3. Tests: thêm 4 tests
   - `test_cuu_tinh_cat_hung_corrected`
   - `test_am_duong_ban_4_tang`
   - `test_theo_3_tranh_5_rule`

### Verification

- 21/21 tests PASS (17 cũ + 4 mới)
- 10 pages OCR saved `data/yi_restored/ky-mon-don-giap-dam-lien/raw_ocr/page-{31..40}.txt`

### ⚠️ Behavior change cho user

Bàn KMDG render trong UI sẽ có **cat_hung khác** cho 5 sao trên (Cầm Tâm = đại cát mới, Xung = cát mới, Trụ Anh = hung mới). Đây là SỬA SAI theo canon Đàm Liên, không phải bug.

---

## Batch 3 — Pages 41-50: **Cách Cục KMDG** (BIG payoff!)

### Insights chính

Pages 41-50 = Chương I phần V "**CÁCH CỤC CÁT HUNG**" — phần BIGGEST của KMDG luận. Đàm Liên list **50+ cách cục** canon. Em đọc được ~30 cách cục cụ thể trong batch này.

**Cát cách quan trọng** (13 cách):
- **Thanh Long Hồi Thủ** 青龍回首 — Trăm sự bình an
- **Phi Điểu Trật Huyệt** 飛鳥跌穴 — Trăm sự thuận lợi
- **Thiên Độn / Quỷ Độn / Phong Độn / Vân Độn / Long Độn / Hổ Độn** — 6 độn chiến thuật quân sự
- **Tam Trá** (Trùng Trá / Hưu Trá / Đại Giả) — cầu tài, gặp quý nhân
- **Địa Giả** — ẩn mình, lánh nạn
- **Giao Thái** — đại lợi (Thiên Ất + Địa Đinh)

**Hung cách quan trọng** (12 cách):
- **Thanh Long Đào Tẩu** — bại trận, bỏ trốn (Ất/Tân)
- **Bạch Hổ Xương Cuồng** — đại hung (Tân/Ất)
- **Đằng Xà Yêu Dược** — kiện tụng
- **Chu Tước Đầu Giang** — lộ thông tin
- **Thái Bạch Nhập Huỳnh** — phục binh cố thủ
- **Phục Can Cách** — tham chiến bị bắt
- **Tam Kỳ Nhập Mộ** — mưu sự không thành
- **Lục Nghi Kích Hình** — ĐẠI KỴ xuất hành
- **Hình Cách** — khởi binh cực hung
- **Phục Ngâm / Phản Ngâm** — bàn không động / đối xung
- **Môn Cung Chế Bức** — môn↔cung khắc

### Engine improvements (BIG!)

1. `engine/ky_mon/constants.py`:
   - `CACH_CUC_CANON` dict — 25+ entries với info (zh/loai/tom/dieu_kien/usage/check)

2. `engine/ky_mon/cast.py`:
   - `detect_cach_cuc(thien_ban, dia_ban, mon)` function — loop 9 cung + match conditions
   - Implemented **7 cách cục auto-detection** đơn giản:
     - Phi Điểu Trật Huyệt (Thiên Bính + Địa Lục Nghi)
     - Thanh Long Đào Tẩu (Thiên Ất + Địa Tân)
     - Bạch Hổ Xương Cuồng (Thiên Tân + Địa Ất)
     - Đằng Xà Yêu Dược (Thiên Quý + Địa Đinh)
     - Chu Tước Đầu Giang (Thiên Đinh + Địa Quý)
     - Hình Cách (Thiên Canh + Địa Kỷ)
     - Giao Thái (Thiên Ất + Địa Đinh hoặc Thiên Đinh + Địa Bính)
   - `cast()` return giờ có thêm field `cach_cuc_detected: List[dict]`

3. UI `KyMonPanel.vue`:
   - Section "🎯 Cách cục phát hiện" hiển thị TRƯỚC trục bàn Trị Phù
   - Color-code theo cát/hung (xanh đại cát / xanh nhạt cát / đỏ nhạt hung / đỏ đậm đại hung)
   - Mỗi cách cục show: tên VN+ZH, badge cát/hung, tóm, chi tiết cung phát hiện, usage

4. Tests: thêm 3 tests
   - `test_cach_cuc_detect_founder_hinh_cach` — verify founder data detect Hình Cách
   - `test_cach_cuc_canon_25_entries`
   - `test_detect_cach_cuc_returns_list`

### Founder data discovery

Bàn KMDG founder (1988-06-05 23:30) **detected Hình Cách (đại hung)** ở cung Khảm:
- Thiên Canh 庚 + Địa Kỷ 己 → "khởi binh cực hung"
- Paradigm note: KHÔNG predict — đây là cấu trúc khoảnh khắc sinh, **không phải tuyên án đời founder**. Đối ứng tâm cảnh.

### Verification

- 24/24 tests PASS (21 cũ + 3 mới)
- Webapp build clean (3.00s)
- 10 pages OCR saved `data/yi_restored/ky-mon-don-giap-dam-lien/raw_ocr/page-{41..50}.txt`

### ⚠️ Behavior change

UI bàn KMDG giờ hiển thị **section "Cách cục phát hiện"** mới phía trên trục Trị Phù. Sau cast, user thấy ngay 0-N cách cục matching với loại cát/hung + usage cụ thể.

### 📊 Engine status

| Layer | Before batch 3 | After batch 3 |
|---|---|---|
| Thiên Bàn render | ✓ | ✓ |
| Cát/hung labels | ✓ (corrected) | ✓ |
| Paradigm reasoning | tooltip cung | **+ cách cục detection** |
| Luận bàn cổ điển | ❌ | ✅ 7 cách cục auto |
| Canon coverage | 0% | ~50% (25/50+ entries) |

---

## Batch 4 — Pages 51-60: Chương II "Bố cục" + Trí Nhuận

### Insights chính

Pages 51-60 = **Chương II "BỐ CỤC CỦA KMDG"**. Heavy theory, không có cách cục mới — focus vào MATH + lịch sử giảm số bố cục:

1. **4 cấp số bố cục**:
   - **4320 cục** theoretical (360 ngày × 12 giờ)
   - **1080 cục** practical (4320 ÷ 4 trùng lặp)
   - **72 bố cục** canon (24 tiết khí × 3 nguyên)
   - **18 cục Địa Bàn** cố định (9 Dương + 9 Âm)
   - Trích Yên Ba Chước Du Ca: "Chế ra thời gian 1800 giờ, Thái Công chia 72, đến Hán Trương Tử Phòng tiết giảm còn 18 cục"

2. **Tiết ≠ Trung Khí**:
   - 12 **Tiết** = nửa tháng đầu (Lập Xuân, Kinh Chập, ...)
   - 12 **Trung Khí** = nửa tháng sau (Vũ Thủy, Xuân Phân, ...)
   - "24 tiết khí" thực ra là phiếm xưng cho 12+12

3. **Phù Đầu rule** (Đông phương cổ điển):
   - Thượng Nguyên: Phù Đầu Giáp/Kỷ + **Tứ Trọng** (Tý Ngọ Mão Dậu)
   - Trung Nguyên: + **Tứ Mạnh** (Dần Thân Tỵ Hợi)
   - Hạ Nguyên: + **Tứ Quý** (Thìn Tuất Sửu Mùi)
   - VD Đông Chí cung 1 Khảm → Dương Độn 1 cục. Hạ Chí cung 9 Ly → Âm Độn 9 cục.

4. **Trí Nhuận** 置閏 (explain methods em đã hỗ trợ):
   - **Chabu 拆補** (default): Mỗi 5 ngày 1 nguyên, không insert. Khi Phù Đầu cách tiết khí < 9 ngày.
   - **Zhirun 置閏**: Khi Phù Đầu cách tiết khí > 9 ngày → insert 15 ngày lặp Thượng/Trung/Hạ Nguyên. "Siêu Thần" → "Tiếp Khí".
   - → Mapping với `method='chabu'` vs `method='zhirun'` trong kinqimen library!

### Engine improvements

1. `engine/ky_mon/wiki.py`: thêm 4 sections mới
   - `bo_cuc_numbers` — 4 cấp số 4320/1080/72/18
   - `tiet_vs_trung_khi` — phân biệt 12 Tiết / 12 Trung Khí
   - `phu_dau_rule` — 3 nguyên với chi pattern
   - `tri_nhuan_chabu` — giải thích chabu vs zhirun (mapping kinqimen library values)

2. Tests: thêm 4 tests
   - `test_bo_cuc_numbers_4320_1080_72_18`
   - `test_tiet_vs_trung_khi_12_12`
   - `test_phu_dau_rule_3_nguyen`
   - `test_tri_nhuan_explain_chabu_zhirun`

### Insight đắt nhất batch 4

**Mapping rõ ràng giữa Chabu/Zhirun trong dropdown UI ↔ Trí Nhuận paradigm**. Trước em note "Chabu (giờ, phổ thông) / Zhirun (giờ, lịch nhuận)" mơ hồ. Giờ em hiểu:
- Chabu = method KMDG cổ điển, không có Trí Nhuận
- Zhirun = method KMDG hiệu chỉnh khi gặp Siêu Thần (Phù Đầu cách tiết khí > 9 ngày)

→ User chọn dropdown method giờ có ngữ cảnh rõ.

### Verification

- 28/28 tests PASS (24 cũ + 4 mới)
- 10 pages OCR saved `data/yi_restored/ky-mon-don-giap-dam-lien/raw_ocr/page-{51..60}.txt`

---

## 📊 Tổng tiến độ phiên này

- **60/367 pages restored** (16% sách Đàm Liên)
- **5 commits** (`4aed3de` → `cb78a4d` → `ed522db` → batch 4 → ...)
- **28 tests passing** (gốc 10 → +18 từ 4 batches)
- **Engine từ "render bàn" → "luận bàn cách cục cổ điển" + paradigm sâu**
- **Backlog**: Phần V còn ~25+ cách cục chưa extract (auto-detect cần expand), Chương III–VII còn nguyên (pages 61-367)

---
