# Vòng 18 — Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn FULL) p328-348 (2026-06-23)

> **Ch.25 cuối (lục cát/lục sát × chính tinh) + Ch.26 (Thiên Địa Giải / Thai Cáo / Tam Thai Bát Tọa).**
> 🔧 PHÁT HIỆN GAP ENGINE: `cast_la_so` có lục cát, THIẾU lục sát phản-đề (Hình Riêu Không Kiếp).

## 📍 Vị trí
- Tập 1 FULL p328-348 (20tr). Ch.25 cuối + Ch.26 (các phụ tinh tháng giờ ngày).

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 LỤC SÁT = PHẢN ĐỀ của LỤC CÁT (luật toàn-không sinh để cân):** mỗi cặp trợ-tinh có 1 cặp hoại-tinh phản-đề phương-vị: Tả Hữu ⊥ **Hình Riêu**, Xương Khúc ⊥ **Không Kiếp**. Đặc tính (phản đề): **Hình**(dương)=nam-thiếu-tài→bá đạo/đe dọa/sát (con dao); **Riêu**(âm)=nữ-thiếu-khả-ái→quyến rũ/dâm (thuốc mê, đào hoa); **Không**(Địa Không, dương)=khác-đời/lập-dị ("tác sự hư không"); **Kiếp**(Địa Kiếp, âm)=ngược-đời/phá-hoại ("tác sự sơ cuồng").
2. **🏆🏆 "XÁC SUẤT chứ KHÔNG tuyệt đối" (lặp — Iron #4/#6):** "Xương tốt nhất, Kiếp xấu nhất chỉ có nghĩa XÁC SUẤT — vẫn có số nhỏ trường hợp **Kiếp tốt hơn Xương**." Cõi ta = "**dương thịnh âm suy**" → dương tốt/âm xấu (lúc không rõ) = "định nghĩa CHỦ QUAN theo cái nhìn hạn hẹp của chúng ta" (Đằng Sơn thẳng thắn về nền chủ-quan).
3. **🏆 CHỦ-TỚ TƯƠNG TÁC (chính tinh × phụ tinh):** Tử Phủ (động, hiếu động) cần Tả Hữu (tay chân) → "**Tử Phủ vô Tả Hữu vi cô quân**". **Sát Phá Tham (đối kháng) THIÊN VỀ Không Kiếp (tàn phá) thay vì Xương Khúc (xây dựng)** — khác đa số sách. Cơ Lương (mưu sĩ) cần Xương Khúc (trí).
4. **🏆🏆 THIÊN TƯỚNG + HÌNH = PHÁ CÁCH (founder-relevant):** "Tướng đại biểu quyền uy VAY MƯỢN, nên có **Hình cùng cung hoặc xung chiếu ví như SỨ GIẢ BỊ QUÂN GIẶC CHÉM ĐẦU; là phá cách.**" → lá số Anh (Mệnh Thiên Tướng @ Tỵ) cần kiểm Thiên Hình có ở Mệnh/xung-chiếu không.
5. **🏆 Thời-thế reframe (lặp):** "Khoa tử vi thời phong kiến, im lặng tuân xã hội = thượng sách → Không/Kiếp bị gán 'làm việc không đâu'/'điên rồ'." Thời nay đổi → đọc lại theo gốc. Thai Cáo / Thiên Địa Giải / Tam Thai Bát Tọa = sao "dẫn đường" tinh-chỉnh lục cát (Khúc kém Xương; Tả vai chính nhờ Thiên Giải tam hợp).

## 🔧 PHASE A — ENGINE (VERIFY THẬT — phát hiện gap)
- ✅ Cast lá số Anh: `phu_tinh` = {Tả Phù, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt} = **đủ LỤC CÁT** (Tả Hữu Xương Khúc Khôi Việt).
- ⚠️ **GAP: `cast_la_so` THIẾU LỤC SÁT (Hình Riêu Không Kiếp)** — phản-đề bắt buộc của lục cát theo luật toàn-không (Ch.24-25). Hệ quả: **không kiểm được cách "Thiên Tướng + Hình phá cách" cho lá số Anh** (engine chưa an Hình). → **spawn task riêng** (đã tạo) bổ sung, KÈM an-formula từ Ch.24:
  - **Thiên Hình**: khởi cung Dậu = tháng giêng, đếm THUẬN theo tháng → idx=(9+(m−1))%12.
  - **Thiên Riêu**: khởi cung Sửu = tháng giêng, đếm THUẬN theo tháng → idx=(1+(m−1))%12.
  - **Địa Kiếp** (dương Tuyệt, thuận): khởi Hợi = giờ Tý, đếm THUẬN theo giờ → idx=(11+giờ_idx)%12.
  - **Địa Không** (âm Tuyệt, nghịch): khởi Hợi = giờ Tý, đếm NGHỊCH theo giờ → idx=(11−giờ_idx)%12.
  → bổ sung lục sát = HOÀN TẤT cân âm-dương lá số theo paradigm Đằng Sơn (lá số hiện chỉ có cực dương trợ-tinh, thiếu cực âm hoại-tinh).

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH
- **Thiên Tướng (Mệnh Anh) = quyền uy VAY MƯỢN** → đặc biệt CẦN Tả Hữu (engine xác nhận Anh CÓ Tả Hữu ở cung Thân/idx7 — tam hợp) + DỄ TỔN bởi Hình (cần kiểm sau khi engine an Hình). Cộng hưởng Vòng 11/15/17 (Thiên Tướng = sao phụ/mượn-chỗ/sứ-giả). Đồng dạng, KHÔNG predict.
- **Xác suất ≠ tuyệt đối + dương-thịnh-âm-suy chủ quan** = Đằng Sơn thành thật về nền chủ-quan → khớp Iron #4/#6 (không phán cứng) + "phán xét tốt-xấu là chủ quan" (Vòng 17).

## 💬 Quote đắt nhất
> "Tướng... có Hình cùng cung hoặc xung chiếu ví như sứ giả bị quân giặc chém đầu"
> — Đằng Sơn, tr.337 (Mệnh Thiên Tướng của Anh)

## 📚 PHASE B — WIKI
- Concept: **lục-sát-phản-đề-lục-cát** · **hình-riêu-không-kiếp-đặc-tính** · **thiên-tướng-hình-phá-cách** · **sát-phá-tham-thiên-không-kiếp** · **tốt-xấu-xác-suất-không-tuyệt-đối** · **dương-thịnh-âm-suy-chủ-quan** · **thai-cáo-tam-thai-bát-tọa-dẫn-đường**.

## 🎨 PHASE C — UX
- 🎨 Sau khi engine an lục sát: lá số Anh hiển thị ĐỦ cân âm-dương (lục cát + lục sát) + cảnh báo cách "Thiên Tướng + Hình" nếu có (đọc-động, không phán).

## ⚠ Iron Rule check
- [x] KHÔNG predict (lục sát = TÍNH phản-đề, phá-cách đọc đồng-dạng) · verify thật (cast live, phát hiện gap) · cite trang · gap → spawn task riêng KHÔNG gián đoạn mạch đọc (kỷ luật scope) · Git Iron #7 (1 file).

## 📝 Tiến độ
- 348/380 trang Tập 1 (~92%). Còn ~2 vòng Tập 1 + Tập 2. **18 vòng phiên này.**

## ⏭ Tiếp theo
- Vòng 19: p349-367 (Ch.26 cuối + Ch.27 — Lộc Tồn Kình Đà / sao theo can, gần hết Tập 1).
