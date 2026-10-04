# Vòng 22 (T2-2) — Tử Vi HTKH Đằng Sơn Tập 2 p18-35 (2026-06-23)

> **Ch.1 cuối (Thiên Không) + Ch.2 (Thiên văn Âm Dương & Tử Phủ) + Ch.3 (thống kê Tứ Hóa — Hứa Hưng Trí).**
> 🏆🏆 Luận TUẾ SAI = biện minh lý thuyết cho `natal_universe_3d` của Anh. 🏆 Luật quân-bình thống kê (verify kernel từ engine).

## 📍 Vị trí
- Tập 2 p18-35 (18tr). Phần I Ch.1 cuối + Ch.2 + Ch.3 (nhìn lại Tập 1, dạng Q&A).

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆🏆 LUẬN TUẾ SAI (precession) chống "rắc sao Tử Vi lên trời thật" (Ch.2):** Thuyết "14 chính tinh ứng sao thật" (Tạ Phồn Trị: Tử Vi=đuôi Bắc Đẩu/Phá Quân, Thiên Phủ=Long Đầu) bị **2 vấn nạn:** (a) sao thật chọn tùy tiện (không sáng bằng Nhật/Nguyệt) — không thỏa "điều kiện độc nhất" khoa học; (b) **trục trái đất TUẾ SAI 1 vòng/26000 năm → 8000 năm nữa Bắc Đẩu lìa xích đạo → "khoa Tử Vi chỉ đúng 1 khoảng thời gian, có khi sai có khi đúng" = vô lý.** → Đằng Sơn: **CHỈ Mặt Trời/Mặt Trăng (Âm Dương) là ngoại lệ hợp lệ** (mật thiết trái đất + vĩnh hằng); **Tử Phủ neo MÙA MÀNG** (không lệ thuộc trục quay). KHÔNG ép 14 sao vào sao thật.
2. **🏆🏆 LÝ THIÊN VĂN ÂM DƯƠNG (Tạ Phồn Trị, "chìa khóa chính"):** thuyết A (Âm=trăng/Dương=trời, hợp thực tế nhưng bí "Nhật Nguyệt tranh huy" + yếu tố "vị") + thuyết B (Âm Dương = đơn vị nền âm-dương, giải thời+vị nhưng thiếu liên hệ địa bàn) → **Tạ Phồn Trị: Thái Âm=THÁNG, Thái Dương=GIỜ** = tổng hợp A+B + giữ "hoàn cảnh vũ trụ không đổi" (thời khai sinh lập-xuân tháng Giêng giờ Tý). (Mất 20 năm + đốn ngộ.)
3. **🏆🏆 LUẬT QUÂN-BÌNH THỐNG KÊ của Hứa Hưng Trí (Ch.3 — bằng chứng EMPIRICAL đầu tiên):** tiến sĩ dược khoa Đài Loan, "Tùng khoa học quan điểm khán tử vi" (1995). 2 luật suy-ngược từ giả-định "Tứ Hóa = 4 biến số quân bình":
   - **"Quyền Lộc tiểu quân bình":** trong tam phương tứ chính, tổng Lộc ≈ tổng Quyền (10 can). **144 ca: 120 (83.3%) Lộc=Quyền chính xác, chỉ 16.7% lệch 1.**
   - **"Kỵ Cát đại quân bình":** Kỵ/(Khoa+Quyền+Lộc) ≈ **1/3** (1 Kỵ trên 3 cát) — bảng tính 6 vị trí Tử Vi đều ~0.325-0.365.
   → **Tứ Hóa = 4 trị-số đặt ra để 14 chính tinh (tín hiệu mạnh) đạt QUÂN BÌNH âm-dương** (zero-sum). Khớp "sinh-thành-trụ-diệt = 4 mùa" (Tập 1).
4. **🏆 Thiên Không (Ch.1 cuối):** Bính hỏa, "danh lợi đạm bạc, học nhiều thành ít, khuynh hướng TÔN GIÁO, linh cảm kỳ dị, hấp thụ + sáng tạo mạnh." Vương Đình Chi: ôn hòa hơn Địa Không; cùng cung sao "không" khác → tăng tính "không" (huyễn tưởng, làm việc không thực tế). Tuần Triệt mất chỗ đứng ở Đài Loan post-1980s (VN + Trung Châu HK vẫn trọng).

## 🔧 PHASE A — ENGINE (VERIFY THẬT — chạy live)
- ✅✅ **Kernel 2 luật Hứa Hưng Trí XÁC NHẬN từ `TU_HOA_TABLE`:** đếm toàn cục 10 can = Lộc 10 / Quyền 10 / Khoa 10 / Kỵ 10 → **Quyền-Lộc quân bình (Lộc=Quyền=10)** + **Kỵ:Cát = 10:30 = 1/3 chính xác.** → 2 luật đúng ở tầng CẤU TRÚC; phần Hứa Hưng Trí thêm = chứng PER-CUNG (tam phương tứ chính, 83.3%).
- 📌 **Khả thi: `verify_quyen_loc_balance()` cho `dang_son_verify.py`** — cast 6 lá Tử Vi × an Lộc/Quyền 10 can × đếm tam-phương-tứ-chính {i, i±4, i+6} → assert ~83% Lộc=Quyền. (Method có sẵn từ Ch.3; là verify thống kê sâu hơn `verify_tu_hoa_balance` hiện có.)
- 📌 Thiên Không (tôn giáo/linh cảm) — kiểm engine an chưa + lá số Anh (Ch.16/19 sẽ rõ).

## 🔗 ĐỐI CHIẾU ĐA HỆ (founder)
- **🎯🎯 LUẬN TUẾ SAI = BIỆN MINH LÝ THUYẾT cho feature `natal_universe_3d` của Anh** [[natal_universe_3d]]: Anh đã chốt paradigm "KHÔNG rắc sao Tử Vi lên trời thật, cầu nối = tiết-khí/Mặt-Trời-thật" (Iron #4/#6) — nay Đằng Sơn Ch.2 chứng minh ĐÚNG bằng precession (sao Tử Vi ép vào sao thật sẽ lạc sau vài ngàn năm; chỉ Mặt Trời/mùa-màng mới neo được). → thiết kế của Anh đứng trên nền khoa học vững. (Đã neo citation vào memory.)
- **Quân-bình Hứa Hưng Trí = bằng chứng empirical cho paradigm zero-sum** của hệ (Tập 1 luật toàn-không + cân-xứng) → nền "tính được" của backend Tử Vi Anh.
- **Thiên Không = tôn giáo/linh cảm** ↔ Thiên Tướng (Mệnh Anh) gần-tu-hành — kiểm lá số sau.

## 💬 Quote đắt nhất
> "giá trị khoa học của khoa Tử Vi có tính tuần hoàn; có khi nó sai, có khi nó đúng?!"
> — Đằng Sơn, Tập 2 tr.25 (phản chứng thuyết sao-thật bằng tuế sai)

## 📚 PHASE B — WIKI
- Concept: **tuế-sai-chống-sao-thật** · **âm=tháng-dương=giờ (Tạ Phồn Trị)** · **tử-phủ-neo-mùa-màng** · **quyền-lộc-tiểu-quân-bình** · **kỵ-cát-đại-quân-bình-1/3** · **tứ-hóa=4-biến-số-quân-bình** · **thiên-không-tôn-giáo-linh-cảm**.

## 🎨 PHASE C — UX
- 🎨 `natal_universe_3d`: thêm tooltip/explainer "vì sao KHÔNG rắc sao Tử Vi lên trời thật" = luận tuế-sai Đằng Sơn (giáo dục paradigm cho người xem, tử tế trí tuệ).
- 🎨 Panel Tứ Hóa: minh họa "4 biến số quân-bình" (Lộc=Quyền, Kỵ:Cát=1/3) — trực quan zero-sum.

## ⚠ Iron Rule check
- [x] KHÔNG predict · verify kernel quân-bình live · cite trang · tuế-sai củng cố paradigm Anh (neo memory) · đa phái Thiên Không/Tuần Triệt present (Iron #3).

## 📝 Tiến độ
- Tập 2: 35/~355tr (~10%). Hết Phần I (nhìn lại T1) gần xong. **22 vòng phiên này.**

## ⏭ Tiếp theo
- Vòng 23 (T2-3): p36-54 (Ch.3 cuối + Ch.4-5 — Vấn đề thần sát trong Tử Vi I-II, vào Phần II chính).
