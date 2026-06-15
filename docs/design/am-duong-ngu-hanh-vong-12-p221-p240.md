# Vòng 12 — Học Thuyết Âm Dương Ngũ Hành (Lê Văn Sửu) p221-p240 (2026-06-13)

## 📍 Vị trí
- Phạm vi: p221 → p240 (20 trang) — HOÀN TẤT hệ yếu tố thị giác của chương NHÌN.
- Mạch: chiều hướng → dáng đầu/nét mặt → độ dài (↔ ngũ âm) → độ lớn → kết hợp = tổng hành.

## 🎯 Paradigm cốt em ngộ

1. ⭐⭐⭐ **CHIỀU HƯỚNG ↔ NGŨ HÀNH — HỢP NHẤT NGHE + NHÌN + THÂN THỂ** (Bảng 4-17 p226). 5 chiều
   hướng thị giác ĐỒNG THỜI với hướng sức toàn thân + tiếng nói (6 thanh) + dáng đầu cổ, cùng quy
   ngũ hành: ngửa lên cao (mặt trời)=Hỏa/vui (tiếng sắc, đầu hất cao); chéo lên (cây)=Mộc/hăng hái
   (tiếng ngã, đầu hất chéo); ngang (mặt đất)=Thổ/lo (tiếng đoản-trường bình, đầu ngang); chéo
   xuống (quặng)=Kim/buồn (tiếng hỏi, đầu dằn chéo); cúi xuống thấp (nước)=Thủy/sợ (tiếng nặng,
   đầu gập). → cử động thân, hướng nhìn, dấu thanh là MỘT hệ ngũ hành.

2. ⭐⭐ **ĐỘ DÀI ↔ NGŨ HÀNH ↔ NGŨ ÂM ↔ THANH** (Bảng 4-19 p232). Ngắn(1/5)=Hỏa=Chủy=Thượng;
   hơi ngắn=Mộc=Giốc=Khứ; trung bình=Thổ=Cung=Đoản/Trường; hơi dài=Kim=Thương=Hồi; dài(5/5)=
   Thủy=Vũ=Hạ. Áp cho cả không gian + thời gian + độ dài thanh. Nối ngũ âm (vòng 8) + 6 thanh (vòng 9).

3. ⭐ **DÁNG ĐẦU + NÉT MẶT ↔ NGŨ HÀNH** (Hình 4-38) + **ĐỘ LỚN ↔ NGŨ HÀNH** (Bảng 4-21). Mặt
   người = bản đồ ngũ hành tâm trạng (Hỏa mặt tươi cười → Thủy miệng cụp xuống). Độ lớn nhỏ(1/5)=
   Hỏa → lớn(5/5)=Thủy; tâm lý so kích thước người (quá nhỏ=hài hước, quá to=sợ); núi non bộ=vui,
   đền dưới núi cao=linh thiêng sợ sệt.

4. ⭐ **KẾT HỢP = TỔNG HÀNH**. Mọi yếu tố thị giác (hình/màu/nét/độ cao/chiều hướng/độ dài/độ lớn)
   cùng một quy luật; hiệu quả kết hợp = tổng số hành (chiếu cố chính-phụ). VD nét thẳng + màu
   trắng + chéo lên = thổ+kim+mộc → đủ diễn đạt mọi khía cạnh tâm lý.

## 💬 Quote NGUYÊN VĂN đắt nhất
> "Khi vui sướng thì người ta nhảy lên reo múa... ước muốn bay vọt lên... thì dáng đầu cổ cùng
> với sức hơi phải hất lên cao. Vì thế hướng lên cao chính là hành hoả chỉ sự vui."
> — Lê Văn Sửu p225 (chiều hướng = hướng sức = thanh = hành)

## 🔧 PHASE A — ENGINE
- [x] `do_hinh_co.py`: làm giàu `NGU_HANH_TAO_HINH` thêm `chieu_huong`/`huong_goc` (góc vẽ mũi tên,
      Bảng 4-17) + `do_dai` (Bảng 4-19) + `do_lon` (Bảng 4-21) + `dang_dau`/nét mặt (Hình 4-38) +
      note `he_thi_giac_day_du` (trọn hệ + kết hợp = tổng hành).

## 📚 PHASE B — WIKI
- [x] Ingest vòng 12: chunk p221-240 (13.4k chars) + 7 atoms. Corpus tổng **103 atoms**.
- [x] Cross-link: chiều hướng↔hướng sức↔6 thanh↔dáng đầu; độ dài↔ngũ âm (vòng 8)↔thanh (vòng 9).

## 🎨 PHASE C — UX/UI — HOÀN THIỆN ĐỒ HÌNH TẠO HÌNH (Anh duyệt đầu tư đồ hình)
- [x] Tab **"🎨 Ngũ hành Tạo hình"** thành TRỌN HỆ: thêm hàng MŨI TÊN CHIỀU HƯỚNG (Hỏa lên thẳng
      → Thủy xuống thẳng, fan 5 hướng); hover thêm chiều hướng + độ dài + độ lớn + dáng đầu; details
      "📐 Trọn hệ thị giác ↔ ngũ hành".
- [x] Verify Playwright render harness data thật: 5 hình + 5 nét + 5 dấu thanh + 5 mũi tên đúng
      hướng (chéo lên/lên thẳng/ngang/chéo xuống/xuống thẳng). Screenshot
      `data/research/screenshots/do-hinh-tao-hinh-tron-he-vong12-*.png` — đọc tay, render đẹp.

## ⚠ Iron Rule check
- [x] Chiều hướng/độ dài/độ lớn: dùng đúng Bảng 4-17/4-19/4-21; vẫn luận điểm tác giả (attribution).
- [x] Mũi tên huong_goc: khớp mô tả "hất lên cao / gập xuống" của tác giả.
- [x] Cite trang + bảng đầy đủ.

## 📝 Tiến độ
- Đã đọc: 240 / 251 trang (96%)
- Còn lại: 11 trang (p241-251) = vòng cuối 13

## ⏭ Tiếp theo
- Vòng 13 (CUỐI): p241-251 — tổng kết toàn sách, kết luận luận điểm nguồn gốc Việt, đóng dự án
  đọc sâu (13 vòng). Sau vòng cuối: báo cáo cụm tổng kết + cập nhật HANH-TRINH-NHAP-DAO.
