# Vòng 10 — Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn FULL) p174-192 (2026-06-23)

> **Ch.13 (Tả Hữu Xương Khúc) + Ch.14 (Tứ Hóa 1: Lộc Quyền Khoa Kỵ).** ENGINE-CRITICAL:
> verify `TU_HOA_TABLE` khớp bài thiệu Đằng Sơn → nền nhịp-tháng của Anh ĐÚNG.

## 📍 Vị trí
- Tập 1 FULL p174-192 (18tr). Ch.13 (phụ tinh Tả/Hữu/Xương/Khúc) + Ch.14 (Tứ Hóa 1).

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 TỨ HÓA = SINH-THÀNH-TRỤ-DIỆT = XUÂN-HẠ-THU-ĐÔNG:** **Hóa Lộc**=Xuân/Sinh (hồi sinh, nảy lộc, vui tươi) · **Hóa Quyền**=Hạ/Thành (cường tráng, hăng hái) · **Hóa Khoa**=Thu/Trụ (bình lặng, điều chỉnh, thư thái) · **Hóa Kỵ**=Đông/Diệt (xác xơ, âu sầu, tàn phá). → **grounding TRỰC TIẾP feature nhịp-tháng của Anh** (Lộc=cửa-mở/sinh ↔ Kỵ=nút-thắt/diệt).
2. **🏆🏆 BÀI THIỆU TỨ HÓA (= `TU_HOA_TABLE`):** "Giáp Liêm Phá Vũ Dương / Ất Cơ Lương Tử Nguyệt / Bính Đồng Cơ Xương Liêm / Đinh Nguyệt Đồng Cơ Cự / Mậu Tham Nguyệt Hữu Cơ / Kỷ Vũ Tham Lương Khúc / Canh Nhật Vũ Âm Đồng / Tân Cự Nhật Khúc Xương / Nhâm Lương Vi Phụ Vũ / Quý Phá Cự Âm Tham" (thứ tự Lộc-Quyền-Khoa-Kỵ). ⚠ Nhật=Thái Dương, Nguyệt=Thái Âm (theo bài thiệu chuẩn — chú thích sách in ngược, là lỗi in/OCR; engine khớp chuẩn).
3. **🏆 NGŨ HÀNH TỨ HÓA:** Hóa Lộc=Mộc(đới thổ) · Hóa Quyền=Hỏa đới thổ · Hóa Khoa=Thủy đới thổ (KHÔNG kim — kim sát khí không hợp nhu hòa) · Hóa Kỵ=Thủy thuần (như bão tố/đại dương nhận chìm).
4. **🏆 DẪN XUẤT TẢ HỮU XƯƠNG KHÚC:** công thức Mệnh **M = 3+T−G (mod 12)**. Tả Phụ=sao THÁNG (Thìn=đế vượng tháng, thuận); Văn Xương=sao GIỜ (Tuất=đế vượng giờ, nghịch); Hữu Bật=đối xứng Tả qua trục Sửu-Mùi; Văn Khúc=đối xứng Xương. Tả/Hữu=cặp dương (giờ), Xương/Khúc=cặp âm (tháng).
5. **Tứ Hóa ĐA PHÁI bất đồng:** Canh Khoa/Kỵ tranh luận nhất (Âm Đồng đa số / Phủ Đồng / Tướng Kỵ-Phan Tử Ngư). Vương Đình Chi (HK): Mậu Dương Khoa, Nhâm Phủ Khoa. Tạ Phồn Trị: Quý Đồng Khoa. → cần truy nguyên khoa học.

## 🔧 PHASE A — ENGINE (VERIFY THẬT — vừa đọc vừa làm)
- ✅✅ **`TU_HOA_TABLE` (an_sao.py) KHỚP 10/10 CAN với bài thiệu Đằng Sơn:**
  Giáp(Liêm-Phá-Vũ-Dương)✓ · Ất(Cơ-Lương-Tử-Âm)✓ · Bính(Đồng-Cơ-Xương-Liêm)✓ · Đinh(Âm-Đồng-Cơ-Cự)✓ · Mậu(Tham-Âm-Hữu-Cơ)✓ · Kỷ(Vũ-Tham-Lương-Khúc)✓ · **Canh(Dương-Vũ-Âm-Đồng)✓** (dùng đúng convention "Âm Đồng" Đằng Sơn endorse) · Tân(Cự-Dương-Khúc-Xương)✓ · Nhâm(Lương-Vi-Phụ-Vũ)✓ · Quý(Phá-Cự-Âm-Tham)✓.
  → **Feature nhịp-tháng (`luu_nguyet`) + lá số Tứ Hóa của Anh đứng trên bảng ĐÚNG NGUYÊN VĂN nguồn.**
- 📌 Grounding nhịp-tháng: Lộc/Kỵ = Sinh/Diệt (Xuân/Đông) → có thể bổ chú giải nghĩa "cửa mở/nút thắt" cho UX.

## 📚 PHASE B — WIKI
- Concept: **tứ-hóa=sinh-thành-trụ-diệt=4-mùa** · **bài-thiệu-tứ-hóa** · **ngũ-hành-tứ-hóa-đới-thổ** · **dẫn-xuất-tả-hữu-xương-khúc** · **công-thức-mệnh-M=3+T−G** · **tứ-hóa-đa-phái-Canh**.

## 🎨 PHASE C — UX
- 🎨 Nhịp-tháng: nhãn Tứ Hóa theo MÙA (Lộc=🌱xuân-sinh, Quyền=☀️hạ-thành, Khoa=🍂thu-trụ, Kỵ=❄️đông-diệt) — trực quan hóa "cửa mở / nút thắt" cho Anh.

## ⚠ Iron Rule check
- [x] KHÔNG predict (Tứ Hóa = TÍNH của mùa, không phán kết cục) · verify thật bảng engine · cite trang.

## 📝 Tiến độ
- 192/380 trang Tập 1 (~51% — QUÁ NỬA). Còn ~10 vòng Tập 1 + Tập 2. **10 vòng phiên này.**

## ⏭ Tiếp theo
- Vòng 11: p193-212 (Ch.14 cuối + Ch.15 — truy nguyên Tứ Hóa khoa học / Lộc Tồn).
