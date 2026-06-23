# Vòng 6 — Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn FULL) p99-117 (2026-06-23)

> **Ch.8 (ngũ hành chế-hóa + thập-nhị-chi/thập-can + nạp âm + CỤC SỐ) + Ch.9 (3 VÒNG
> SAO + vì sao tử vi bỏ tiết khí)** — TIM KỸ THUẬT grounding engine `an_sao.py`.

## 📍 Vị trí
- Tập 1 FULL p99-117 (18tr). Ch.8 (Ngũ hành Cục số I) trọn + Ch.9 (Cục số II) đầu.

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 4 BƯỚC ĐỊNH CỤC (nền `an_sao` cục/Tràng Sinh):** B1 định can 12 cung (ngũ hổ độn: niên-can ×2+1 → can cung Dần) · B2 nạp âm can-chi cung Mệnh · B3 **cục = hành nạp âm cung Mệnh** · B4 cục số (Thủy 2, Mộc 3, Kim 4, Thổ 5, Hỏa 6). **"Cục = ngũ hành nạp âm của THÁNG (cung mệnh)."**
2. **🏆🏆 3 VÒNG SAO = TAM TÀI (Ch.9):** **Lộc Tồn**←niên CAN = THIÊN · **Thái Tuế**←niên CHI = ĐỊA · **Tràng Sinh**←MỆNH NẠP ÂM (cục) = NHÂN. Cung Mệnh (nguyệt-chi + thời-chi) = nền "nhân". → Phối ngày sinh + cục số = **14 chính tinh**; phối niên can = **Tứ Hóa (Lộc Quyền Khoa Kỵ)**. Đây là TOÀN BỘ logic an sao.
3. **🏆 14 CHÍNH TINH = 2 CHÙM** (chú thích 4): **chùm Tử Vi 6** (Tử Vi, Liêm Trinh, Thiên Đồng, Vũ Khúc, Thái Dương, Thiên Cơ) + **chùm Thiên Phủ 8** (Thiên Phủ, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân). → **XÁC NHẬN hằng số `TU_VI_CHUM`/`PHU_CHUM` em dùng trong `dang_son_verify` (verify Hóa Kỵ) — khớp NGUYÊN VĂN nguồn.**
4. **🏆 VÌ SAO TỬ VI BỎ TIẾT KHÍ (khác Bát Tự):** lý tuần hoàn mặt trăng → tử vi coi **00:00 ngày mùng 1 = đầu tháng**, KHÔNG dùng tiết khí ("bất y ngũ tinh yếu quá tiết"). Ngày bỏ can-chi (chỉ 1-29/30 = tiểu đơn vị tháng); giờ bỏ thời-can (chỉ thời-chi). → grounding: engine Tử Vi dùng tháng âm, KHÁC engine Bát Tự (cần sxtwl tiết-khí).
5. **🏆 NGŨ HÀNH CHẾ-HÓA (chú thích 1) — vượng/nhược đảo tốt-xấu:** "kim **vượng** được hỏa luyện thành khí" (bị khắc lúc vượng = TÔI LUYỆN, tốt); ngược lại "kim quá yếu được thổ sinh nhiều quá thì kim bị CHÔN VÙI" (được sinh quá = ngộp, xấu). → khắc/sinh KHÔNG nhị phân, tùy lực.
6. **Thập-nhị-chi ngũ hành:** Thổ = trung dung, chiếm 4 mộ Thìn Tuất Sửu Mùi; Hợi Tý=Thủy, Tỵ Ngọ=Hỏa, Dần Mão=Mộc, Thân Dậu=Kim. Hợi Tỵ Tý Ngọ **nghịch** lý âm-dương (→ cách Lộc Mã giao trì).

## 🔗 ĐỐI CHIẾU ĐA HỆ
- **🎯 CỤC SỐ = "THỂ-DỤNG" (Iron #8 của Anh!):** Đài/HK giải thủy-nhị/hỏa-lục cục bằng thể-dụng — **nạp âm = THỂ, cục số = DỤNG**; thể-dụng khác → cục (dụng) của thủy lấy lý-số của hỏa. → Đằng Sơn DÙNG chính khung Thể-Dụng Thiệu Tử mà Anh chốt Iron #8. (Đằng Sơn chưa chốt đúng-sai, hứa giải sau — em theo dõi vòng tới.)
- **TU_VI_CHUM/PHU_CHUM xác nhận** → cú verify Hóa Kỵ (chùm Tử Vi 5/5) của em đứng trên hằng số ĐÚNG nguồn.
- **Ngũ hành chế-hóa (vượng/nhược)** = tinh chỉnh `ngu_hanh_relation` + `ngu_hanh_nen`: thêm tầng "tùy vượng-nhược" (bị khắc lúc vượng = luyện; được sinh quá = ngộp).

## 💬 Quote đắt nhất
> "kim vượng được hỏa luyện thành khí"
> — Đằng Sơn, tr.110 (chế-hóa: bị khắc lúc mạnh = tôi luyện)

## 🔧 PHASE A — ENGINE
- ✅ XÁC NHẬN (đọc-verify, không sửa): `TU_VI_CHUM`=6 sao + `PHU_CHUM`=8 sao trong `dang_son_verify.py` KHỚP chú thích 4 Ch.8 Đằng Sơn → nền verify Hóa Kỵ vững. Logic 4-bước-cục + 3-vòng-sao khớp `an_sao.py` (cục→Tràng Sinh, niên can→Tứ Hóa).
- 📌 Ghi nhận (PHASE B/C, chưa sửa): ngũ hành chế-hóa vượng/nhược → nâng cấp tương lai cho `ngu_hanh_relation`.

## 📚 PHASE B — WIKI
- Concept: **4-bước-định-cục** · **cục=nạp-âm-tháng** · **3-vòng-sao-tam-tài** (Lộc Tồn-thiên/Thái Tuế-địa/Tràng Sinh-nhân) · **14-chính-tinh-2-chùm** · **tử-vi-bỏ-tiết-khí** · **ngũ-hành-chế-hóa-vượng-nhược** · **cục-số-thể-dụng** · **chi-ngũ-hành-Hợi-Tỵ-nghịch**.

## 🎨 PHASE C — UX
- 🎨 Đồ hình "3 vòng sao = Tam Tài" (Lộc Tồn/Thái Tuế/Tràng Sinh ↔ thiên/địa/nhân) + sơ đồ 4-bước-an-sao — explainer engine cho user hiểu lá số dựng thế nào.

## ⚠ Iron Rule check
- [x] KHÔNG predict · cục-số thể-dụng nối Iron #8 (mệnh là động từ/dụng) · cite trang.

## 📝 Tiến độ
- 117/380 trang Tập 1 (~31%). Còn ~13 vòng Tập 1 + Tập 2. **6 vòng phiên này.**

## ⏭ Tiếp theo
- Vòng 7: p118-137 (Ch.9 cuối + Ch.10 — cộng hưởng cục số / an 14 chính tinh chi tiết).
