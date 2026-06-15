# Vòng 10 — Học Thuyết Âm Dương Ngũ Hành (Lê Văn Sửu) p181-p200 (2026-06-13)

## 📍 Vị trí
- Phạm vi: p181 → p200 (20 trang) — kết chương NGHE (ngôn ngữ) + mở **chương NHÌN: Âm Dương
  Ngũ Hành trong NGHỆ THUẬT TẠO HÌNH** Phương Đông (chân thứ hai luận điểm nguồn gốc Việt).
- Mạch: nhạc tính tiếng Việt → kết luận ngôn ngữ (3 mặt) → tạo hình ↔ tâm sinh lý → **ngũ hành ↔
  HÌNH THỂ / MÀU SẮC / DÁNG NGƯỜI** → cộng hưởng 2 màu/hình theo sinh-khắc.

## 🎯 Paradigm cốt em ngộ

1. ⭐⭐⭐ **NGŨ HÀNH ↔ HÌNH THỂ** (Bảng 4-13 p196-198) — kiến thức nền THỊ GIÁC: vạn vật lược về
   5 hình đại biểu — **Mộc = chữ nhật** (thân cây/cột/dầm: chống đỡ, ngay thẳng); **Hỏa = tròn**
   (cầu/bánh xe/đầu người/mặt trời: linh hoạt, ấm sáng, nguồn sống); **Thổ = vuông** (vững, sức ì,
   lo); **Kim = tam giác** (giáo mác/mũi tên: phá cái mềm hơn, buồn); **Thủy = uốn khúc** (nước
   chảy/múa/sóng/chớp: khéo léo / sợ). Lý do quy loại = cảm quan bản năng, không võ đoán.

2. ⭐⭐ **NGŨ HÀNH ↔ MÀU SẮC ↔ TÂM LÝ** (Bảng 4-11, trích Châm cứu đại thành): Mộc-Xanh-Can-
   tướng quân-mưu lự/giận; Hỏa-Đỏ-Tâm-quân chủ-vui; Thổ-Vàng-Tỳ-điều hòa-bình thản/lo; Kim-Trắng-
   Phế-tướng phó-buồn; Thủy-Đen-Thận-kỹ xảo/kinh hãi. **Hai màu cạnh nhau CỘNG HƯỞNG theo sinh-
   khắc**: xanh trên đỏ (mộc sinh hỏa) = hy vọng gặp kết quả; xanh trên vàng (mộc khắc thổ) = lo
   xâm nhập niềm tin... → tương sinh = hòa hợp, tương khắc = căng (bất kể màu gì).

3. ⭐ **NGŨ HÀNH ↔ DÁNG NGƯỜI** (Hình 4-19): Mộc=đứng hiên ngang/chống đỡ; Hỏa=mừng vui; Thổ=lo/
   bình thản; Kim=suy tính/buồn; Thủy=múa khéo léo/bắt bóng. Cộng hưởng nguyên lý TƯ THẾ THÂN THỂ
   (Mai Hoa BƯỚC 4) — thân thể biểu lộ hành đang vượng.

4. ⭐ **VN KHÁC TQ: HỎA ↔ KIM HOÁN VỊ** (attribution, p198). Bảng hình thể người Việt vs "Địa lý
   ngũ quyết" TQ: 3 hành Thủy/Mộc/Thổ trùng, riêng Hỏa↔Kim đảo. Tác giả cho bảng Việt khớp cảm
   quan bản năng hơn (tam giác sắc nhọn = phá = Kim hợp lý), bảng TQ chỉ quy ước. → ghi attribution.

5. ⭐ **GỐC VIỆT của tương ứng MÀU-HÀNH: Tuệ Tĩnh** (Hồng nghĩa giác tư y thư tr.66): "khí đen→thủy
   sinh, khí đỏ→hỏa sinh, khí xanh→mộc sinh, khí trắng→kim sinh, khí vàng→thổ sinh". Tiếng Việt 3
   mặt: tượng thanh + tượng hình + nhạc tính.

## 💬 Quote NGUYÊN VĂN đắt nhất
> "Mọi vật thể có khối hình tam giác hoặc góc nhọn như giáo, mác... đều gây cho con người một
> nhận biết về khả năng phá nát những gì mềm hơn nó, gây ra một cảm giác buồn trong lòng. Vì thế
> hình thị giác tam giác được quy loại vào hành kim."
> — Lê Văn Sửu p197

## 🔧 PHASE A — ENGINE
- [x] `do_hinh_co.py`: `NGU_HANH_TAO_HINH` (hình/hình_loại/màu/tính cách/dáng người/tâm lý/lý do
      mỗi hành) + payload `ngu_hanh_tao_hinh` (kèm note VN≠TQ Hỏa↔Kim + Tuệ Tĩnh khí hóa màu).

## 📚 PHASE B — WIKI
- [x] Ingest vòng 10: chunk p181-200 (28.4k chars) + 9 atoms. Corpus tổng **89 atoms**.
- [x] Atom VN≠TQ (Hỏa↔Kim) confidence 0.68 + nhãn attribution.
- [x] Cross-link: dáng người↔Mai Hoa BƯỚC 4; màu-hành↔Tuệ Tĩnh khí hóa; cộng hưởng↔sinh-khắc.

## 🎨 PHASE C — UX/UI — ĐỒ HÌNH NGŨ HÀNH TẠO HÌNH (Anh duyệt đầu tư đồ hình)
- [x] Tab thứ 10 **"🎨 Ngũ hành Tạo hình"**: render 5 HÌNH THỂ thật (chữ nhật/tròn/vuông/tam giác/
      uốn khúc) trong 5 màu hành; hover hiện dáng người + tâm lý + lý do; details "Việt khác TQ".
- [x] Verify Playwright render harness data thật: 5 hình thể đúng (2 rect mộc/thổ, 1 tròn hỏa,
      1 tam giác kim, 1 uốn khúc thủy) + màu hành. Screenshot
      `data/research/screenshots/do-hinh-ngu-hanh-tao-hinh-vong10-*.png` — đọc tay, render đẹp.

## ⚠ Iron Rule check
- [x] VN≠TQ Hỏa↔Kim: nhãn attribution rõ trong engine + atom confidence thấp.
- [x] Hình thể/màu/dáng: dùng đúng Bảng 4-11/4-13/Hình 4-19; tâm lý ghi "không hiểu máy móc".
- [x] Cite trang + cổ thư đầy đủ (Châm cứu đại thành, Tuệ Tĩnh, Địa lý ngũ quyết).

## 📝 Tiến độ
- Đã đọc: 200 / 251 trang (80%)
- Còn lại: 51 trang ≈ 2-3 vòng

## ⏭ Tiếp theo
- Vòng 11: p201-220 — tiếp tạo hình: cộng hưởng hình-màu, đường nét, chiều hướng, ứng dụng;
  có thể vào tổng kết / phụ lục.
