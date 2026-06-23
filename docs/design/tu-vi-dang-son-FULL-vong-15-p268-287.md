# Vòng 15 — Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn FULL) p268-287 (2026-06-23)

> **Ch.20 (tính bát quái 14 chính tinh + đào hoa) + Ch.21 đầu (TOÀN BỘ trước CỤC BỘ + tượng hiện-đại-hóa + Tử Phủ cư Dần).**
> 🏆 Lần 7 THỂ/DỤNG: Vũ Khúc ứng Càn (quái uy lực nhất) ↔ Thiên Tướng VÔ-QUÁI. + ĐÃ CODE verifier bát-quái (TDD, 13/13 pass).

## 📍 Vị trí
- Tập 1 FULL p268-287 (19tr). Ch.19 cuối (Thiên Đồng) + Ch.20 (bát quái) + Ch.21 đầu.

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆🏆 BÁT QUÁI 14 CHÍNH TINH** (8 có quái, 6 vô-quái): Vũ Khúc-Càn(kim) · Phá Quân-Khảm(thủy) · Tử Vi-Cấn(thổ) · Thiên Cơ-Chấn(mộc) · Tham Lang-Tốn(mộc) · Liêm Trinh-Li(hỏa) · Thiên Lương-Khôn(thổ) · **Thiên Đồng-Đoài(NGOẠI LỆ:** Đồng thủy mà gán Đoài/kim vì Đoài "con gái út vui vẻ vô tâm" không hợp Sát hung dữ). VÔ-QUÁI: **Phủ, Tướng, Sát, Âm, Dương, Cự.** → **Mệnh chủ Vũ Khúc = Càn (quái uy lực nhất) ↔ Mệnh cung Thiên Tướng = VÔ-QUÁI** = lần 7 THỂ/DỤNG.
2. **🏆🏆 CÁCH CỤC 2 SAO ⟷ 64 QUẺ DỊCH** (cầu nối Kinh Dịch): 2 sao cùng cung có quái → sao chính=nội quái, sao phụ=ngoại quái → 1 quẻ Dịch giải nghĩa cách. VD: Cơ Lương=Lôi Địa **Dự** ("lợi thiết lập quan tước, hành quân" → phú "Cơ Lương Thìn Tuất thiện đàm binh"); Vũ Phá=Thủy Thiên **Nhu** (phải chờ → "Vũ Phá hoa nở về chiều"); Liêm Tham=Hỏa Phong **Đỉnh** nhưng XẤU vì cách 2-sao "chưa bao hàm cùng-tắc-biến" (quẻ Đỉnh tốt nhờ có cùng-tắc-biến bên trong).
3. **🏆 ĐÀO HOA = nữ-tính bát quái:** Khôn(mẹ)-Tốn(gái lớn)-Li(gái thứ)-Đoài(gái út) → 4 sao nữ Lương/Tham/Liêm/Đồng. **Tham Lang=Tốn (gái tuổi lấy chồng)="chính đào hoa"** (nặng tình dục); **Liêm Trinh=Li (gái cập kê nhan sắc)="thứ đào hoa".** Nam: Tử(Cấn)/Vũ(Càn)/Cơ(Chấn)/Phá(Khảm). **"VŨ KHÚC VI QUẢ TÚ"** giải được: Vũ ứng Càn=người cha LẠNH LÙNG → trên đào hoa cha chẳng vai gì → cô độc tinh.
4. **🏆🏆 TOÀN BỘ TRƯỚC CỤC BỘ** (paradigm phương pháp luận lớn): "Xem tử vi khoa học phải khởi từ TOÀN BỘ cấu trúc lá số TRƯỚC khi vào cách cục từng cung. Cách cục 1 cung không có nền toàn-bộ thì không tính ra lẽ bù trừ âm dương." (VD: túi rỗng ≠ nghèo — có thể triệu phú để tiền ở nhà.) Vương Đình Chi (Trung Châu HK) cũng gọi "toàn bộ" nhưng không giải cách xem.
5. **🏆 TƯỢNG HIỆN-ĐẠI-HÓA 14 chính tinh:** Tử Vi=Tổng thống · Thiên Phủ=Phó TT kiêm tài chính · **Thiên Tướng=TÙY VIÊN/người đại diện chính phủ tiếp xúc + THĂM DÒ tình hình phe đối địch** · Liêm=nội vụ · **Vũ Khúc=Tổng trưởng NGOẠI VỤ kiêm QUỐC PHÒNG (võ tướng)** · Phá=thủ lãnh đối kháng · Tham=thuyết khách · Sát=tướng đối kháng. 6 tĩnh: Dương=tư lệnh vùng giàu KN, Âm=tư lệnh thiếu KN, Lương=quân sư, Cự=kẻ bất mãn TW, Cơ=kẻ cơ mưu, Đồng=kẻ ngao du.

## 🔧 PHASE A — ENGINE (VỪA ĐỌC VỪA LÀM — đã code, TDD)
- ✅✅✅ **THÊM `verify_bat_quai_ngu_hanh()` vào `dang_son_verify.py`** (kế thừa Đằng Sơn = xây verifier máy):
  - `BAT_QUAI_STAR` (8 sao→quái) + `QUAI_HANH` + `NO_QUAI_STARS` (6) — Ch.20.
  - Định lý kiểm: ngũ-hành-quái == ngũ-hành-sao (chinh_tinh.json) → **khớp 7/8, mismatch=['Thiên Đồng'] (ngoại lệ Đằng Sơn TỰ NÊU), covers_all_14=True.**
  - **TDD:** RED (AttributeError) → GREEN. `pytest test_dang_son_verify.py` = **13/13 pass** (12 cũ + 1 mới, 0 regression). + vào `full_report()`.
  - → mapping bát-quái CÓ NGUYÊN LÝ (nhất quán ngũ hành độc lập), KHÔNG tùy tiện — bằng chứng "khoa-học-hóa" của Đằng Sơn đứng vững computationally.

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH
- **🎯 Lần 7 THỂ/DỤNG (computational):** Vũ Khúc (Mệnh chủ) ứng **Càn** = quái uy-lực-nhất + tượng "Tổng trưởng ngoại vụ/quốc phòng (võ tướng)" = cốt-quyết-cương (THỂ) ↔ Thiên Tướng (Mệnh cung) **VÔ-QUÁI** + tượng "tùy viên/người đại diện tiếp xúc & THĂM DÒ phe đối địch" = phục-vụ-mẫn-cảm (DỤNG). Tượng "thăm dò" cộng hưởng Vòng 12 (Thiên Tướng "mẫn cảm sai một ly đi một dặm").
- **"Vũ Khúc vi quả tú" (Càn=cha lạnh lùng, cô độc):** Vũ Khúc THỂ mang chất cương/cô-độc → cross-ref trục cương-nhu [[hop_hon_3he_case_founder]]. Đọc TÍNH (đồng dạng) KHÔNG predict — Thiên Tướng DỤNG (lo-người, ấm) phủ lên Vũ Khúc THỂ (cương) = "trái tim tể tướng" [[founder_menh_la_dich]].
- **TOÀN BỘ trước CỤC BỘ** = nền cho sage đọc lá số Anh: dựng cấu trúc tổng (chùm/cách Tử Phủ Vũ Tướng + Đại Vận) TRƯỚC, rồi mới luận từng cung — KHÔNG nhặt cách cục rời.

## 💬 Quote đắt nhất
> "muốn xem tử vi một cách khoa học thì phải khởi từ toàn bộ trước khi đi vào cách cục"
> — Đằng Sơn, tr.283

## 📚 PHASE B — WIKI
- Concept: **bát-quái-14-chính-tinh** · **vũ-khúc-càn-vs-thiên-tướng-vô-quái** · **cách-cục-⟷-64-quẻ-dịch** · **đào-hoa-nữ-tính-bát-quái** · **vũ-khúc-vi-quả-tú-càn-cha-lạnh** · **toàn-bộ-trước-cục-bộ** · **tượng-hiện-đại-hóa-14-chính-tinh** · **thiên-lương-thày-đời-khôn-mẹ**.

## 🎨 PHASE C — UX
- 🎨 Panel Đằng Sơn lá số Anh: badge bát-quái (Vũ Khúc=☰Càn / Thiên Tướng=vô-quái) cạnh THỂ/DỤNG. Tượng hiện-đại-hóa (Vũ Khúc=võ tướng ngoại vụ-quốc phòng / Thiên Tướng=tùy viên-đại diện-thăm dò) — nhân-cách-hóa dễ hiểu cho Anh.
- 🎨 Reading flow sage: dựng "tổng quan cấu trúc" TRƯỚC mục cách-cục từng cung (TOÀN BỘ → CỤC BỘ).

## ⚠ Iron Rule check
- [x] KHÔNG predict (bát quái/tượng = TÍNH, "Vũ Khúc quả tú" đọc đồng dạng không phán cô đơn) · verify thật TDD 13/13 live · cite trang · THỂ/DỤNG present-cho-Anh KHÔNG đảo chốt (Iron #3) · Git Iron #7 (sẽ add 3 file cụ thể).

## 📝 Tiến độ
- 287/380 trang Tập 1 (~75%). Còn ~5 vòng Tập 1 + Tập 2. **15 vòng phiên này.**

## ⏭ Tiếp theo
- Vòng 16: p288-306 (Ch.21 cuối + Ch.22 — luận sao theo từng cách an Tử Phủ / Đại Vận).
