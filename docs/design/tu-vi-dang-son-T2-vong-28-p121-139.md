# Vòng 28 (T2-8) — Tử Vi HTKH Đằng Sơn Tập 2 p121-139 (2026-06-23)

> **▶ NỐI LẠI trên bản FULL 358 trang (Anh tải về).** Ch.11 (Cặp sao quý nhân KHÔI VIỆT I — gốc Thiên Ất quý nhân) + Ch.12 (KHÔI VIỆT II — cứu chính tinh cực hãm hóa Kỵ, 10 can minh họa).
> 🏆🏆 verify_khoi_viet_school TDD: engine theo phái Đằng Sơn (truyền thống). 🏆 Founder: Khôi Việt Sửu/Mùi = "tọa quý hướng quý" trục Tài–Phúc (+ non-finding tử tế #3).

## 📍 Vị trí
- **Bản FULL mới** `~/Downloads/Bản sao của Tu vi...tap 2...0001.pdf` (358tr, offset physical=printed). Đọc p121-139 (19tr) = **nội dung MỚI** (bản cũ chỉ tới p120).
- Đã đọc: Tập 1 trọn (380tr) + Tập 2 p1-139 (Ch.1-12). Còn Ch.13-29 (p140-350).

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 KHÔI VIỆT = LỤC CÁT, gốc thần sát THIÊN ẤT QUÝ NHÂN (Ch.11):** ứng "quý nhân phù trợ, công danh thuận." Bài thiệu: **Giáp Mậu Canh→Sửu Mùi** (ngưu dương), Ất Kỷ→Tý Thân (thử hầu), Bính Đinh→Hợi Dậu (chư kê), Nhâm Quý→Mão Tỵ (thố xà), Tân→Ngọ Dần (mã hổ). Lý nguyên thủy (《Mệnh lý ngũ hành tinh kỷ》 Liễu Trung Lễ Bá, Tống 1196): quý nhân ở đất MỘ nhưng TRÁNH đất **Khôi Cương (Thìn Tuất)** → Bính Đinh mộ Tuất né sang Dậu/Hợi; Nhâm Quý mộ Thìn né sang Mão/Tỵ. Thiên Khôi (dương) + Thiên Việt (âm) **đối xứng qua trục Thìn-Tuất (La Võng)**.
2. **🏆🏆🏆 KHÔI VIỆT VÀO LỤC CÁT VÌ CỨU CHÍNH TINH CỰC HÃM HÓA KỴ (Ch.12, định lý trung tâm):** Tả Hữu Xương Khúc (tài NHÂN) KHÔNG cứu được khi chính tinh lâm nguy (cùng tài Nhân). Khôi Việt (Thiên Ất quý nhân, an can năm = tài THIÊN+ĐỊA) thỏa 2 điều kiện: (1) tính quý nhân cứu trợ; (2) cộng hưởng phương vị nơi chính tinh cực hãm. → **mỗi can: chính tinh hóa Kỵ cực hãm ở đâu thì Khôi Việt cứu cân xứng ở đó** (10 hình minh họa). VD **Can Mậu: Thiên Cơ hóa Kỵ cực hãm Sửu Mùi → Khôi Việt Sửu Mùi "tọa quý hướng quý" cứu** (Hình 6). Quý ↔ Tham Lang hóa Kỵ Tỵ-Hợi-Mão-Dậu → Khôi Việt Mão Tỵ.
3. **🏆 TỔNG KẾT KHÔI VIỆT:** "**yếu tố QUÂN BÌNH hoàn cảnh xấu cực đoan** (chính tinh/Xương Khúc hãm hóa Kỵ); cốt cho lá số thỏa cân xứng. Đã cứu được cực đoan → ngay hoàn cảnh thường Khôi Việt vẫn có tính quý nhân = yếu tố tốt." (Khác Tả Hữu Xương Khúc = tài Nhân; Khôi Việt = tài Thiên-Địa, nên cứu được.)
4. **🏆 IRON #3 ĐA PHÁI KHÔI VIỆT:** (a) vị trí tuyệt đối — Canh: truyền thống Sửu Mùi vs đổi mới Ngọ Dần; Kỷ: truyền thống Tý Thân vs **Tạ Phồn Trị Dần Ngọ**; (b) Khôi/Việt cái nào — 3 phái (Khôi-thuận-Việt-nghịch / trục La Võng / bài thiệu chữ-đầu-Khôi). **Đằng Sơn theo BÀI THIỆU TRUYỀN THỐNG** (ngũ hành làm chính). Sách Việt (Thái Thứ Lang, Thiên Lương...) theo phái 3 cải đổi (Canh Tân).

## 🔧 PHASE A — ENGINE (TDD + live cast)
- ✅✅✅ **TDD `verify_khoi_viet_school()`** (Iron #3 — engine đứng phái nào): RED→GREEN. Engine `thien_khoi_viet` **match truyền thống 10/10** = **đúng phái ĐẰNG SƠN** (Canh=Sửu/Mùi KHÔNG đổi-mới Ngọ Dần; Kỷ=Tý/Thân KHÔNG Tạ Phồn Trị Dần Ngọ); Mậu→Sửu/Mùi. Suite **16 passed** (+1). → cùng `verify_luu_ha_school` (V27) tạo cặp **"engine nhất quán đứng phái Đằng Sơn"** trong tranh chấp đa phái.
- ✅ **Founder (Mậu, live cast):** Thiên Khôi **Sửu (Tài Bạch)** + Thiên Việt **Mùi (Phúc Đức)** — trục Sửu-Mùi xung = **"tọa quý hướng quý"** (hai đầu trục đều có quý-nhân-tinh) → quý nhân phù trợ TÀI LỘC + PHÚC ĐỨC.
- 🎯 **Non-finding tử tế #3 (Iron #4/#6):** Đằng Sơn Hình 6 (Mậu) = "Khôi Việt cứu Thiên-Cơ-Kỵ-cực-hãm ở Sửu Mùi" — NHƯNG founder **Thiên Cơ ở Dần (Tử Tức), KHÔNG ở Sửu/Mùi** (Dần = mộc vị, Cơ vượng, không cực hãm). → **pattern cứu Cơ-Kỵ KHÔNG áp dụng cho lá NATAL của Anh** (không ép). Khôi Việt vẫn = quý nhân Tài-Phúc (positive thật); và CÓ THỂ kích hoạt cứu trợ ở vận/lưu-niên khi Cơ-Kỵ chuyển tới Sửu/Mùi (động, không phán).

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH (Iron #4/#6/#8)
- **Khôi Việt = lớp sao thứ 5-6 trong bộ Lục Cát của Anh** (Tả Hữu Xương Khúc Khôi Việt — [[founder_tu_vi_chart]] engine khớp 91/91). Trục **Tài Bạch ↔ Phúc Đức "tọa quý hướng quý"** = cấu trúc quý-nhân về của-cải + phúc-phần. Đọc TÍNH: Anh có **mạch quý nhân nâng đỡ** ở tài lộc & phúc đức (không phán "sẽ giàu/được giúp" — đọc cấu trúc, Iron #4/#6).
- **3 non-finding liên tiếp** (Mã-đầu-đới-kiếm V25 · chân-tu-Phúc-cường-cung V26 · Cơ-Kỵ-cứu-Khôi-Việt V28) = kỷ luật vững: chỉ đọc cái lá số THẬT có, không bồi cách cho sướng tai. Cái THẬT của Anh (Mệnh 4 lớp + Khôi Việt Tài-Phúc) đã đủ đẹp.
- **Engine nhất quán phái Đằng Sơn (Lưu Hà + Khôi Việt)** = nền tin cậy [[tu_vi_3layer_backend]] + [[feedback_classical_sources]] (chọn theo lý cổ, không tùy tiện).

## 💬 Quote đắt nhất
> "cặp Khôi Việt... là yếu tố quân bình một hoàn cảnh xấu cực đoan"
> — Đằng Sơn, Tập 2 tr.138 (Tổng kết Khôi Việt)

## 📚 PHASE B — WIKI
- Concept: **khôi-việt=lục-cát-gốc-thiên-ất-quý-nhân** · **khôi-việt-cứu-chính-tinh-cực-hãm-hóa-kỵ** · **tọa-quý-hướng-quý** · **khôi-cương-thìn-tuất-quý-nhân-tránh** · **khôi-việt-truyền-thống vs đổi-mới/tạ-phồn-trị (canh-kỷ)** · **lục-cát=tài-nhân(tả-hữu-xương-khúc)+tài-thiên-địa(khôi-việt)**.

## 🎨 PHASE C — UX
- 🎨 Lá số Anh: tô trục **Tài Bạch(Sửu)–Phúc Đức(Mùi)** với nhãn "tọa quý hướng quý (Khôi/Việt)"; tooltip "quý nhân = cứu chính tinh cực hãm; ở Anh là mạch nâng đỡ tài-phúc" (đọc TÍNH, disclaimer không-predict).
- 🎨 Badge Iron #3: Khôi Việt "phái truyền thống (Đằng Sơn) — engine theo phái này, khác Tạ Phồn Trị ở Kỷ".

## ⚠ Iron Rule check
- [x] KHÔNG predict · TDD đỏ-trước-xanh-sau · engine đứng phái theo LÝ (Iron #3, cặp Lưu Hà+Khôi Việt) · **non-finding #3 trung thực** (Cơ ở Dần, không ép cứu-Cơ-Kỵ) · cite trang · đọc trên bản FULL Anh tải · Git Iron #7.

## 📝 Tiến độ
- Tập 2: **139/358tr (~39%)** trên bản FULL. **28 vòng phiên này.** (Tập 1 XONG.)

## ⏭ Tiếp theo
- Vòng 29 (T2-9): p140-158 (Ch.13 — thần sát can năm khác / Ch.14 mở — vào vòng THÁI TUẾ).
