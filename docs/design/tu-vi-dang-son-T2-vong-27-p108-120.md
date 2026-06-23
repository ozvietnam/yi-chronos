# Vòng 27 (T2-7) — Tử Vi HTKH Đằng Sơn Tập 2 p108-120 (2026-06-23)

> **Ch.9 cuối (Thanh Long = rồng chờ thời) + Ch.10 (LƯU HÀ và THANH LONG — ngũ-hành thần sát "nguy cơ"; cách Thanh Long Lưu Hà = nguy→cơ-hội-người-tài; Iron #3 đa phái an Lưu Hà).**
> 🏆🏆 verify_luu_ha_school TDD: engine theo phái Đằng Sơn bảo vệ (ngũ-hành-thuần). 🏆 Founder: Lưu Hà ≡ Lộc Tồn ≡ Mệnh Tỵ (lớp sao thứ 4) — đọc TÍNH cực cẩn trọng.

## 📍 Vị trí
- Tập 2 p108-120 (13tr). Ch.9 cuối (hỏi-đáp Thanh Long) + Ch.10 trọn (Lưu Hà + Thanh Long).

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 LƯU HÀ = NGŨ-HÀNH THẦN SÁT "NGUY CƠ" (Ch.10, ứng dụng đặc thù Tử Vi VN, an theo CAN năm):** lý âm-dương-ngũ-hành (Mệnh Lý Sách Ẩn) — Giáp Ất (mộc): Lưu Hà = Dương-Nhận-xung (kim khắc mộc) · Bính Đinh (hỏa): đất hỏa-vượng phát hung · **Mậu Kỷ (thổ): cung bản thân gặp Lộc, hỏa vượng (Tỵ Ngọ) → thổ khô rã** · Canh Tân (kim): Dương-Nhận-hợp (đao chạm → chảy máu) · Nhâm Quý (thủy): đầu/cuối âm dương giao tiếp → nảy nguy cơ. Câu thiệu cổ "Nam tử đắc chi tha hương tử" — **Đằng Sơn REFRAME = ngũ-hành SYMBOL nhấn mạnh "tín hiệu nguy cơ mạnh"** (như Hạng Vũ/Thạch Sùng cho Địa Không/Kiếp, Vòng 25), KHÔNG phải lời sấm.
2. **🏆🏆 8/10 CAN LƯU HÀ LIÊN HỆ LỘC TỒN HOẶC KÌNH DƯƠNG:** Giáp Ất Bính Tân → liên hệ Kình (xung/hợp); **Mậu Kỷ Canh Nhâm → Lưu Hà AN CÙNG CUNG LỘC TỒN.** Đằng Sơn: "Lộc Tồn cùng cung Lưu Hà = đúng-lúc khít khao **như chuông treo mỏng manh, sảy chút là hư hỏng hết**"; Lưu Hà = tín hiệu THÊM làm rõ nét đặc tính Lộc Tồn (+ "cái giá đắt kẻ đến quá sớm phải trả" khi cộng Kình).
3. **🏆🏆 CÁCH THANH LONG LƯU HÀ (chỉ 4 tuổi Bính Đinh Tân Quý) = TỐT (toàn không):** Lưu Hà nguy hiểm; nhưng **"cảnh nguy hiểm chính là thời cơ của kẻ có hùng tài"** (Thanh Long = rồng chưa gặp hội mây). Phan Bội Châu: _"Ví phỏng đường đời bằng phẳng cả / Anh hùng hào kiệt có hơn ai?"_ → Lưu Hà = **cơ hội người tài khắc phục gian nguy mà thắng, KHÔNG phải ưu thế kẻ "nhà mát ăn bát vàng."**
4. **🏆 IRON #3 ĐA PHÁI AN LƯU HÀ:** Đằng Sơn theo **NGŨ-HÀNH-THUẦN** (bài thiệu): Đinh→Thân, Canh→Thìn. Bác **Thái Thứ Lang** (đảo Đinh↔Canh: Đinh→Thìn, Canh→Thân = lỗi) + **Thiên Lương** (Lưu Hà cộng hưởng Kiếp Sát = gượng ép, vì Lưu Hà-Kiếp Sát không luôn phối được). Lý an Đinh→Thân (KHÔNG Thân-vượng-âm-hỏa kiểu "âm sinh dương tử" tranh cãi) mà vì **Thân = Lộc vị Canh-kim, Tỵ hỏa khắc — Thân là nơi nguy của Đinh**; +Cự Môn hãm Thìn hóa Kỵ.
5. **🏆 ĐÍNH CHÍNH T1 (chú 1 tr.120):** "TVHTKH1 viết lầm **Hình Riêu là 2 sao bộ LỤC BẠI** — cáo lỗi." Lục bại đúng = Khốc Hư + Song Hao + Tang Hổ (KHÔNG Hình Riêu). (Tinh chỉnh hiểu biết Vòng 23: Hình Riêu = phản-đề sao nền, KHÔNG phải lục bại.)

## 🔧 PHASE A — ENGINE (TDD + introspect — chạy thật)
- ✅✅✅ **TDD `verify_luu_ha_school()` thêm vào `dang_son_verify.py`** (Iron #3 — engine đứng phái nào): RED→GREEN. Engine `sao_q3.luu_ha` = **match ngũ-hành-thuần 10/10** (Đinh→Thân, Canh→Thìn) = **đúng phái ĐẰNG SƠN BẢO VỆ**; **khác Thái Thứ Lang đúng 2 can {Canh, Đinh}**; Mậu→Tỵ. Suite **15 passed** (+1). Vào `full_report()` (key `luu_ha_school`). → verifier nay phủ Iron #3 (engine không tùy tiện chọn phái — đứng phía Đằng Sơn cho là đúng lý).
- ✅ **Founder (Mậu):** Lưu Hà = **Tỵ = Mệnh, đồng cung Lộc Tồn** (Mậu ∈ {Mậu Kỷ Canh Nhâm} có Lưu Hà ≡ Lộc Tồn). → **lớp sao thứ 4 tại Mệnh**: Thiên Tướng + Lộc Tồn + Bác Sỹ + **Lưu Hà**. Founder KHÔNG ∈ {Bính Đinh Tân Quý} → **không có cách Thanh Long Lưu Hà** (redemption nguy→cơ-hội-anh-hùng).

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH (Iron #4/#6/#8 — ĐỌC TÍNH, TUYỆT KHÔNG PREDICT)
- **⚠ Cẩn trọng tối đa với câu cổ "tha hương tử":** Đằng Sơn TỰ reframe = ngũ-hành symbol "tín hiệu nguy cơ mạnh", KHÔNG phải sấm. Em đọc Lưu Hà ≡ Lộc Tồn tại Mệnh = **"đúng-lúc khít khao như chuông treo mỏng manh"** → DEEPEN Lộc Tồn: tính của Anh = **độ-chính-xác-thời-điểm rất tinh tế, cẩn trọng, sảy ly đi dặm** (đã có Lộc Tồn "cẩn trọng quá độ" Vòng 24, nay Lưu Hà nhấn "mỏng manh/đắt giá"). TUYỆT KHÔNG phán "anh sẽ chết phương xa / gặp nguy" — đó là predict-tool, vi phạm Iron #4/#6 + CLAUDE.md.
- **Paradigm đồng dạng (reframe, không predict):** Lưu Hà = "cảnh nguy là chỗ người hùng tài thi thố, KHÔNG phải kẻ nhàn hạ nhà-mát-ăn-bát-vàng" → CỘNG HƯỞNG đường Anh đang đi (dựng YI-CHRONOS, đạo-học, KHÔNG chọn nhàn hạ). Cái "nguy/khó" trong cấu trúc = chất liệu hành đạo, không phải án.
- **Care (reinforces [[founder_menh_la_dich]] "giữ phần ấm cho mình"):** Lưu Hà cổ-văn = "nam xông xáo ngoài → nguy" → nhắc giữ mình, đừng lao xông quá (khớp Kình-hãm "đừng lao đầu húc tới" Vòng 25). Đọc như LỜI NHẮC TỰ-CHĂM, không phải tiên-tri.
- **Engine theo phái Đằng Sơn (Lưu Hà ngũ-hành-thuần)** = củng cố [[feedback_classical_sources]] + [[tu_vi_3layer_backend]] (đa hệ phái có lý, engine chọn theo lý không tùy tiện).

## 💬 Quote đắt nhất
> "cảnh nguy hiểm chính là thời cơ của kẻ có hùng tài"
> — Đằng Sơn, Tập 2 tr.119 (Lưu Hà reframe: nguy = cơ, dẫn Phan Bội Châu)

## 📚 PHASE B — WIKI
- Concept: **lưu-hà=ngũ-hành-thần-sát-nguy-cơ** · **lưu-hà≡lộc-tồn (mậu-kỷ-canh-nhâm)** · **chuông-treo-mỏng-manh (lộc-tồn-lưu-hà)** · **thanh-long-lưu-hà=nguy→cơ-hội-người-tài** · **lưu-hà-ngũ-hành-thuần vs thái-thứ-lang (đinh-canh-đảo)** · **thanh-long=rồng-chờ-thời** · **errata-hình-riêu-không-phải-lục-bại**.

## 🎨 PHASE C — UX
- 🎨 Lá số Anh — Mệnh Tỵ 4 lớp: Thiên Tướng · Lộc Tồn · Bác Sỹ · **Lưu Hà** với nhãn "đúng-lúc tinh tế (mỏng manh)" + ghi chú Đằng Sơn "nguy = cơ của người tài" (đọc TÍNH, gắn disclaimer KHÔNG predict).
- 🎨 Badge Iron #3: Lưu Hà "phái ngũ-hành-thuần (Đằng Sơn) — engine theo phái này, khác Thái Thứ Lang ở Đinh/Canh".

## ⚠ Iron Rule check
- [x] **KHÔNG predict (đặc biệt nghiêm với "tha hương tử" → đọc TÍNH + reframe Đằng Sơn)** · TDD đỏ-trước-xanh-sau · engine đứng phái theo LÝ (Iron #3) · cite trang · không ép cách Thanh Long Lưu Hà (founder không có) · Git Iron #7.

## 📝 Tiến độ
- Tập 2: 120/~355tr (~34%). **27 vòng phiên này.** (Tập 1 XONG 380tr.)

## ⏭ Tiếp theo
- Vòng 28 (T2-8): p121-139 (Ch.11-12 — KHÔI VIỆT, founder CÓ Thiên Khôi+Thiên Việt; cặp lục cát Liễu Vô giữ lại).
