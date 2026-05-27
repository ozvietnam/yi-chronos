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
| 2 | 31-40 | ✅ Done | 4 tầng Âm Dương Bàn + "Theo 3 tránh 5" + corrected 5 cat_hung Cửu tinh | _(this commit)_ |
| 3 | 41-50 | ⏳ Pending | — | — |
| 4 | 51-60 | ⏳ Pending | — | — |
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
