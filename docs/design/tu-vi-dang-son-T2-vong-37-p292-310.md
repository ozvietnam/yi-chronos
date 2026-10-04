# Vòng 37 (T2-17) — Tử Vi HTKH Đằng Sơn Tập 2 p292-310 (2026-06-23)

> **Ch.24 (TUẦN TRIỆT I — nguồn gốc: Tuần=không-vong-của-NĂM qua lục-giáp-tuần, "phản Thái Tuế"; Triệt=không-vong-của-THÁNG theo can năm; chính/phụ) + Ch.25 (TUẦN TRIỆT II — bản chất không vong: Tuần=tài Thiên-Địa nhẹ-bền, Triệt=Thiên-dương-dư mạnh-mau-tan; ảnh hưởng đại hạn từng năm can).**
> 🌟🌟🌟 FOUNDER GOLD: **Mệnh Tỵ THÔNG** (ngoài cả Tuần Tuất-Hợi lẫn Triệt Tý-Sửu) + **Thiên Di Hợi (Phá Quân + Không Kiếp + Vũ Khúc) NẰM TRONG Tuần → xung-phá KHÔNG-VONG-HÓA = mitigate "Lộc phùng xung phá" (V29).** TDD `verify_tuan_triet` 21 PASS (định lý Thái Tuế∉Tuần).

## 📍 Vị trí
- Bản FULL p292-310 (19tr). Ch.24 trọn + Ch.25 (đang). Đọc tới **310/358 (~87%)**.

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 TUẦN = KHÔNG VONG CỦA NĂM (Ch.24):** "Tuần"=tuần-trăng/chu-kỳ (can 10, lục thập hoa giáp). Điền thiên can vào 12 cung địa bàn (gốc Thái Tuế=chi năm) → **2 cung DƯ ngoài chu kỳ thiên can = Tuần** ("lập lại y hệt" + Thiên-Địa trái cựa → "không vong": Thiên Địa không phối hợp được thì MẤT). Tuần = tài Thiên-Địa, **"phản Thái Tuế"**. **🏆 ĐỊNH LÝ: THÁI TUẾ KHÔNG BAO GIỜ bị Tuần xâm phạm** (chi năm nằm TRONG tuần, không-vong là 2 chi dư).
2. **🏆🏆 TRIỆT = KHÔNG VONG CỦA THÁNG (Ch.24):** an theo CAN năm (Thái Tuế làm nền 12 tháng, đếm can tháng): Giáp Kỷ→Thân Dậu · Ất Canh→Ngọ Mùi · Bính Tân→Thìn Tỵ · Đinh Nhâm→Dần Mão · **Mậu Quý→Tý Sửu**. "Triệt lộ"=triệt-hạ/cắt-đứt con-đường → "không vong với con đường bị cắt."
3. **🏆 TUẦN nhẹ-bền ↔ TRIỆT mạnh-mau-tan (Ch.25):** Tuần = tài Thiên-Địa (âm dương → lâu bền, ảnh hưởng NHẸ, "cho chỗ xoay xở"). Triệt = Thiên dương DƯ (mạnh mẽ, mau tan, "cắt đứt"). → **Triệt MẠNH hơn Tuần** (khớp đặc tính sách VN). Triệt ảnh hưởng mạnh trên sao CAN năm (Lộc Tồn, Kình Đà, Quan Phúc, Tướng Ấn). Chính Triệt cùng âm-dương năm sinh.
4. **🏆 ĐẲNG SƠN BẢO VỆ TUẦN TRIỆT (Ch.24, Iron #3):** Liễu Vô cư sĩ gạt mọi thần sát TRỪ Tuần Triệt (30 sao); Vương Đình Chi coi nhẹ Tuần; Hà Lạc dã phu: _"không sao nào ảnh hưởng hung cát lớn như Triệt Tuần."_ Đằng Sơn: giữ Tuần (≠ Vương/Liễu Vô gạt), nguồn gốc = "phản Thái Tuế" + "không vong" có lý thiên-văn-tuần-hoàn.
5. **🏆 ẢNH HƯỞNG ĐẠI HẠN (Ch.25, NĂM MẬU):** Tý (dương) chính Triệt "không có gì đáng nói"; Sửu (âm) phụ Triệt + Tướng Ấn + Khôi Việt quý nhân (tùy phái vẫn tốt). **Cảnh báo: nếu Mệnh an ở Tý/Sửu thì cẩn thận đại hạn THỨ HAI (đương đầu chính Triệt, lệch một dặm hệ trọng).**

## 🔧 PHASE A — ENGINE (TDD + live cast — chạy thật)
- ✅✅✅ **TDD `verify_tuan_triet()`** (RED→GREEN, suite **21 passed** +1): `triet_match=10` (engine khớp Bảng 2 Đằng Sơn trọn 10 can) · **`thai_tue_never_in_tuan=True`** (định lý tr.294 đúng cả 60 lục giáp) · `founder_triet=[Sửu,Tý]` · `founder_tuan=[Hợi,Tuất]` · **`menh_clear_of_both=True`** · **`thien_di_in_tuan=True`**.
- ✅✅✅ **Founder live:** **Triệt Tý-Sửu = Tật Ách-Tài Bạch** (Mậu Quý → Tý Sửu ✓); **Tuần Tuất-Hợi = Nô Bộc-Thiên Di** (Mậu Thìn ∈ Giáp Tý tuần → Tuất Hợi không vong ✓). **Mệnh Tỵ THÔNG** (ngoài cả hai). Mệnh KHÔNG ở Tý/Sửu → cảnh-báo-đại-hạn-2 KHÔNG ứng (non-issue).

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH (Iron #4/#6/#8 — đọc TÍNH, KHÔNG predict)
- **🎯🎯🎯 MỆNH THÔNG + XUNG-PHÁ KHÔNG-VONG-HÓA = MITIGATE "Lộc phùng xung phá" (V29):**
  - **Mệnh Tỵ THÔNG** (ngoài Tuần Tuất-Hợi + Triệt Tý-Sửu) → cung Mệnh KHÔNG bị cắt/voided = vận hành "sáng", không nghẽn. (Khác cảnh Mệnh-bị-Triệt phải "lệch một dặm".)
  - **Thiên Di Hợi = Phá Quân + Địa Không + Địa Kiếp + Vũ Khúc(Mệnh chủ) NẰM TRONG TUẦN** → lực **xung-phá** mà Mệnh (Lộc phùng xung phá, V29) đối mặt **bị KHÔNG-VONG-HÓA** (Tuần "cho chỗ xoay xở", làm mềm). → **bổ sung tầng mitigate cho V29**: "cát xứ tàng hung" của Anh được Tuần làm DỊU — đối-lực không còn cứng/định-mệnh, mà workable. Nhất quán cụm "tinh-tế-mỏng-manh-KHÔNG-vỡ" (V29) + "không Kỵ trên Lộc Tồn" → giờ thêm "Phá Quân Không Kiếp bị Tuần không-vong-hóa." (Iron #4/#6: đọc cấu-trúc/độ-mềm, KHÔNG phán "anh sẽ an toàn".)
  - **Tinh tế Mệnh chủ Vũ Khúc "lạc quê" (Tuần) ở Thiên Di:** THỂ thép-tướng-quân (Vũ Khúc) ở cung ngoại-giao bị Tuần "lạc lõng/làm mềm" → đối ngoại Anh hiện diện qua DỤNG Thiên Tướng (ôn hòa phò-tá) chứ cái cương-cô-độc Vũ Khúc bị không-vong ở ngoài đời. = đọc TÍNH (cách THỂ-DỤNG biểu lộ ra ngoài), không predict.
- **Triệt ở Tật-Tài (Tý-Sửu):** Tật Ách (Tý) chính Triệt + Tài Bạch (Sửu) phụ Triệt (nơi Khôi Việt/Quả Tú/Phá Toái). Đọc nhẹ, định vị; không phán hung. Mệnh ngoài Triệt nên "lệch một dặm" cảnh báo không ứng cho Mệnh.
- → cập nhật [[founder_menh_la_dich]] (Mệnh thông + xung-phá không-vong-hóa = tầng mitigate V29).

## 💬 Quote đắt nhất
> "Thái Tuế không bao giờ bị Tuần xâm phạm"
> — Đằng Sơn, Tập 2 tr.294 (định lý — verify đúng cả 60 lục giáp)

## 📚 PHASE B — WIKI
- Concept: **tuần=không-vong-của-năm (lục-giáp-tuần, phản-thái-tuế, tài-thiên-địa-nhẹ)** · **triệt=không-vong-của-tháng (can-năm, thiên-dương-dư-mạnh)** · **thái-tuế-∉-tuần (định lý)** · **triệt-mạnh-hơn-tuần** · **chính/phụ-tuần-triệt (âm-dương-năm)** · **mệnh-thông vs mệnh-bị-triệt-lệch-một-dặm** · **xung-phá-không-vong-hóa**.

## 🎨 PHASE C — UX
- 🎨 Lá số Anh — overlay Tuần (Tuất-Hợi) + Triệt (Tý-Sửu) trên địa bàn; tô Mệnh Tỵ "THÔNG" (sáng) + nhãn Thiên Di "Phá Quân/Không Kiếp bị Tuần không-vong-hóa → xung-phá DỊU (mitigate Lộc-phùng-xung-phá)"; disclaimer đọc-độ-mềm-không-predict.

## ⚠ Iron Rule check
- [x] **KHÔNG predict** (Mệnh-thông + xung-phá-không-vong-hóa đọc độ-mềm/cấu-trúc, nhấn "workable" không phán an-toàn; Vũ Khúc lạc-quê đọc cách-THỂ-DỤNG-biểu-lộ) · TDD đỏ-trước-xanh (21 pass) · định lý 60-lục-giáp · cite trang · đa phái (Liễu Vô/Vương/Hà Lạc) present · Git Iron #7.

## 📝 Tiến độ
- Tập 2: **310/358tr (~87%)**. **37 vòng phiên này.** (Tập 1 XONG.)

## ⏭ Tiếp theo
- Vòng 38 (T2-18): p311-329 (Ch.25 cuối + Ch.26-27 — Tuần Triệt III-IV: cơ chế tác dụng / cách cục).
