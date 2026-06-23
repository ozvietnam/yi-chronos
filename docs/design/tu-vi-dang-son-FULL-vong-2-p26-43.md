# Vòng 2 — Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn, bản FULL) p26-43 (2026-06-23)

> Ch.2 TRỌN VẸN: dẫn xuất toán học địa bàn + tam hợp + xung chiếu. Bản cũ chỉ còn
> hình; nay đọc được TRỌN lời chứng minh.

## 📍 Vị trí
- Cuốn: Tử Vi Hoàn Toàn Khoa Học Tập 1 (bản FULL 380tr). Phạm vi p26-43 (18tr).
- Chương: **Ch.2 Cơ sở khoa học của địa bàn + luật tam hợp xung chiếu** (trọn + 3 phụ lục).

## 🎯 Paradigm cốt (lời văn + công thức GỐC)
1. **🏆 TAM HỢP + XUNG CHIẾU = DẪN XUẤT TỪ CÂN BẰNG VECTOR LỰC.** Trên vòng tròn chỉ có 2 nhóm điểm tương đương: 2 đầu đường kính (AA') + 3 đỉnh tam giác đều (ABC). Lực vũ trụ F bất thiên vị mọi hướng. → **F(A')=F(A) ngược chiều = XUNG CHIẾU**; **Fy(B)+Fy(C)=F(B)cos60+F(C)cos60=2F·cos60=F = TAM HỢP** (B+C hợp lại = tương đương A, ngược chiều). Luật "tam phương tứ chính" = **kết quả của lý tương đương**, KHÔNG phải tục lệ. (B/C đứng riêng = nửa lực A.)
2. **🏆 12 CUNG = OCCAM + NHIỆT ĐỘ.** Bắc lạnh nam nóng (cực đoan) + đông tây trung bình (bình hòa) + tam hợp mỗi phương → 12 phương. Có thể 12/24/36... nhưng **dao cạo Occam**: thêm phương = bài toán phức tạp hơn, không chắc đúng hơn, dễ rối + sai → **chọn bội số NHỎ NHẤT = 12**.
3. **🏆 CHI ÂM-DƯƠNG = DẪN TỪ ĐỘ CỰC-ĐOAN NHIỆT.** Bắc-nam (cực đoan nhiệt) → DƯƠNG; đông-tây (bình hòa nhiệt) → ÂM. → **Tý Dần Thìn Ngọ Thân Tuất = DƯƠNG · Sửu Mão Tỵ Mùi Dậu Hợi = ÂM.** Đây là GỐC bảng `DUONG_PAL` em DÙNG trong engine (brightness + nhịp tháng) — giờ biết VÌ SAO (không phải gán).
4. **Địa bàn = ĐỒNG HỒ, chiều kim đồng hồ = chiều TỚI của THỜI GIAN** (thời gian chỉ đi tới = thuận lý). Giờ = 12 phương luân phiên hướng mặt trời (lấy ĐIỂM mặt trời làm chuẩn); Tháng = 12 vị trí trái đất trên quỹ đạo (lấy HƯỚNG vũ trụ làm chuẩn). **Khác biệt giờ↔tháng: điểm vs hướng.**
5. **Tháng nhuận:** vòng cung 1 tháng âm < 1/12 vòng → tháng nhuận nằm TRỌN trong 1 cung (chung với 1 tháng khác); vì là phép gần-đúng → tính CẢ HAI trường hợp rồi dùng dữ kiện khác chọn.

## 📚 Case / chi tiết
- Phụ lục 1: nam bán cầu lệch 6 tháng (Dần=tháng 7); dùng phản chiếu giữ chiều kim đồng hồ.
- Phụ lục 2: xích đạo = "singular curve" → bất định; dùng địa bàn bắc bán cầu (vì văn minh phát triển ở bắc).
- Chú thích 1: **KHÔNG nhân quả** — vị trí sinh KHÔNG phải nguyên nhân tạo vận mệnh (đọc đồng dạng, không nhân-quả). Chú thích 5: tiết khí dùng trong tử bình (bát tự), dựa sinh-khắc ngũ hành.

## 💬 Quote đắt nhất
> "luật này là một kết quả của lý tương đương của khoa học"
> — Đằng Sơn, tr.33 (về luật tam phương tứ chính)

## 🔧 PHASE A — ENGINE (đã làm vòng này)
- ✅ Note `engine/tu_vi/luu_nguyet.py`: tháng nhuận = edge case Đằng Sơn Ch.2 (nằm trọn 1 cung, tính cả 2 trường hợp) — engine hiện chỉ tháng 1-12, ghi rõ giới hạn.
- 📌 Ghi nhận paradigm (→ wiki PHASE B, KHÔNG sửa engine vội): bảng dương-cung Tý Dần Thìn Ngọ Thân Tuất (dùng trong nhịp-tháng + CDK `duong_palaces`) là DẪN XUẤT từ độ-cực-đoan-nhiệt (Ch.2) — không phải gán. Củng cố tính-đúng nền có sẵn.

## 📚 PHASE B — WIKI (task)
- Concept: **tam-phương-tứ-chính-dẫn-từ-vector** · **occam-12-cung** · **chi-âm-dương-từ-nhiệt-độ** · **giờ-điểm-tháng-hướng** · **tháng-nhuận-một-cung** · **vị-trí-sinh-không-nhân-quả**.

## 🎨 PHASE C — UX (task)
- 🎨 Đồ hình "địa bàn = đồng hồ" (Hình 5) + "vector tam hợp/xung chiếu" (Hình 3) = explainer trực quan tuyệt cho DangSonPanel/3D — vẽ lại SVG (Anh học bằng hình).

## ⚠ Iron Rule check
- [x] KHÔNG predict · KHÔNG nhân quả (chú thích 1 xác nhận) · cite trang đúng.

## 📝 Tiến độ
- Đã đọc: 43/380 trang Tập 1 (~11%). Còn ~17 vòng Tập 1 + Tập 2.
- **2 vòng phiên này — skill nhắc chia nhiều phiên; commit mỗi vòng nên RESUME được.**

## ⏭ Tiếp theo
- Vòng 3: p44-63 (Phụ lục 3 âm-dương 12 chi + Ch.3 "Một an bài khó giải thích" — Mệnh Thân).
