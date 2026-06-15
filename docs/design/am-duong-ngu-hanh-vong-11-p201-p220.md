# Vòng 11 — Học Thuyết Âm Dương Ngũ Hành (Lê Văn Sửu) p201-p220 (2026-06-13)

## 📍 Vị trí
- Phạm vi: p201 → p220 (20 trang) — tiếp chương NHÌN: yếu tố tạo hình theo ngũ hành.
- Mạch: cộng hưởng hình×hình → màu×hình (25 combo) → **đường nét ↔ ngũ hành** → **5 dấu thanh
  Việt = đường nét** → **độ cao ↔ ngũ hành** → cộng hưởng đa yếu tố = tổng hành.

## 🎯 Paradigm cốt em ngộ

1. ⭐⭐⭐ **5 DẤU THANH CHỮ VIỆT = 5 ĐƯỜNG NÉT NGŨ HÀNH** (Bảng 4-15 p213) — HỢP NHẤT đẹp nhất
   của cả cuốn: nối thẳng chương NGHE (6 thanh, vòng 9) với chương NHÌN (đường nét). Sắc=cong
   tròn=Hỏa; Ngã=uốn ngửa=Mộc; Không dấu+Huyền=thẳng ngang=Thổ; Hỏi=cong câu=Kim; Nặng=gấp khúc=
   Thủy (dấu nặng dùng cho tiện thay nét uốn khúc). → **6 thanh tiếng Việt và nét vẽ là MỘT hệ
   ngũ hành** — bằng chứng mạnh nhất cho luận điểm khí chất sinh học Việt (attribution kế thừa).

2. ⭐⭐ **ĐƯỜNG NÉT ↔ NGŨ HÀNH** (Bảng 4-14). 5 nét đại biểu: Mộc=uốn ngửa (giun oằn, chống trả);
   Hỏa=cong tròn (trăng non, khóe cười); Thổ=thẳng ngang (đều đều, lo); Kim=cong câu (rắn cuộn,
   buồn rầu); Thủy=gấp khúc (sông uốn, tia chớp, sợ). Lý do = cảm quan bản năng.

3. ⭐⭐ **ĐỘ CAO ↔ NGŨ HÀNH** (Bảng 4-16). Theo vị trí thật vật đại biểu so tầm mắt: cao nhất=
   mặt trời=Hỏa; trên trung bình=cây=Mộc; trung bình=mặt đất=Thổ; dưới trung bình=quặng kim=Kim;
   thấp nhất=nước (mạch ngầm)=Thủy. → thêm một trục thị giác (cao-thấp) vào hệ ngũ hành.

4. ⭐ **CỘNG HƯỞNG MÀU × HÌNH (25 combo)** theo sinh-khắc: tương đồng = ổn định theo bản chất
   hành; tương sinh = êm dịu; tương khắc = chói chang gay gắt. Màu không tách rời hình.

5. ⭐ **CỘNG HƯỞNG ĐA YẾU TỐ = TỔNG HÀNH**. Mọi yếu tố (màu/hình/nét/độ cao) cùng quy luật;
   kết hợp → hiệu quả = tổng số hành (chiếu cố chính-phụ). VD nét cong câu + hình uốn khúc +
   màu vàng + độ cao trung bình = kim+thủy+thổ+thổ. Đủ diễn đạt mọi khía cạnh tâm lý.

## 💬 Quote NGUYÊN VĂN đắt nhất
> "Trong đó có 4 dấu giống với bốn loại đường nét có cùng hành và tâm lý, chỉ có thanh hạ không
> dùng nét cong uốn khúc, đã dùng dấu nặng cho tiện mà thôi."
> — Lê Văn Sửu p213 (dấu thanh chữ Việt = đường nét ngũ hành)

## 🔧 PHASE A — ENGINE
- [x] `do_hinh_co.py`: làm giàu `NGU_HANH_TAO_HINH` thêm `duong_net` + `net_pts` (toạ độ vẽ nét) +
      `do_cao`/`do_cao_vat` (Bảng 4-16) + `dau_thanh` (Bảng 4-15 hợp nhất). Cập nhật y_nghia payload.

## 📚 PHASE B — WIKI
- [x] Ingest vòng 11: chunk p201-220 (16.3k chars) + 7 atoms. Corpus tổng **96 atoms**.
- [x] Cross-link: dấu thanh ↔ đường nét ↔ 6 thanh (vòng 9); đa yếu tố cộng hưởng = tổng hành.

## 🎨 PHASE C — UX/UI — NÂNG CẤP ĐỒ HÌNH TẠO HÌNH (Anh duyệt đầu tư đồ hình)
- [x] Tab **"🎨 Ngũ hành Tạo hình"**: thêm hàng ĐƯỜNG NÉT (render 5 nét thật từ net_pts) + dấu
      thanh dưới mỗi hành; hover thêm đường nét + dấu thanh + độ cao; details "🖋 Dấu thanh Việt =
      đường nét ngũ hành" + "📏 Độ cao ↔ hành".
- [x] Verify Playwright render harness data thật: 5 hình thể + 5 đường nét glyph (uốn ngửa/cong
      tròn/thẳng/cong câu/gấp khúc) + dấu thanh + bảng độ cao. Screenshot
      `data/research/screenshots/do-hinh-tao-hinh-net-dau-vong11-*.png` — đọc tay, render đẹp.

## ⚠ Iron Rule check
- [x] Dấu thanh = đường nét: dùng đúng Bảng 4-15; vẫn trong luận điểm tác giả (attribution kế thừa).
- [x] Đường nét/độ cao: minh họa net_pts theo mô tả "văn" cổ; ghi nguồn bảng.
- [x] Cite trang + bảng đầy đủ.

## 📝 Tiến độ
- Đã đọc: 220 / 251 trang (88%)
- Còn lại: 31 trang ≈ 2 vòng (p221-240, p241-251)

## ⏭ Tiếp theo
- Vòng 12: p221-240 — tiếp chiều hướng/độ lớn tạo hình + có thể tổng kết toàn sách / kết luận
  luận điểm nguồn gốc Việt.
