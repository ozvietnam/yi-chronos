# Vòng 34 (T2-14) — Tử Vi HTKH Đằng Sơn Tập 2 p235-253 (2026-06-23)

> **Ch.20 cuối (Hỏa Linh — Đằng Sơn SUY LẠI phép an từ thủy-hỏa giao thoa, độc lập trùng Tạ Phồn Trị; "ma quân là bạn đạo") + Ch.21 trọn (Hỏa Linh có dùng giờ? + lý thiên văn giờ + THIÊN TRÙ = khắc tinh Hỏa Linh / Thực Thần chế Sát).**
> 🟡🟡 IRON #3 TRUNG THỰC: **CHỖ ĐẦU TIÊN engine KHÔNG theo phái Đằng Sơn** — Hỏa Linh Tỵ Dậu Sửu engine theo TRUYỀN THỐNG (Hỏa Mão), khác Đằng Sơn/Tạ Phồn Trị (Hỏa Tuất). Ghi nhận, present founder, KHÔNG ép sửa. (TDD `verify_hoa_linh_school` 19 PASS.) Founder năm Thìn KHỚP cả 2 phái.
> 🌟 FOUNDER: "ma quân là bạn đạo" (sát tinh = nhiên liệu tu-dưỡng) nối tiếp lò-tu-dưỡng V33.

## 📍 Vị trí
- Bản FULL p235-253 (19tr). Ch.20 cuối + Ch.21 trọn (Hỏa Linh + Thiên Trù). Đọc tới **253/358 (~71%)**.

## 🎯 Paradigm cốt (lời văn GỐC)
1. **🏆🏆 HỎA LINH — ĐẰNG SƠN SUY LẠI từ THỦY-HỎA GIAO THOA (Ch.20):** Hỏa=X (hiển hiện/dương), Linh=Y (ẩn tàng/âm), cùng hành hỏa nhưng Hỏa dương Linh âm. Suy vị trí từ 4 nhóm tam hợp (luồng hỏa tiến sát thủy + giao thoa). Kết quả TRÙNG bài thiệu truyền thống **TRỪ Tỵ Dậu Sửu** (Đằng Sơn: Hỏa Tuất/Linh Mão — ĐẢO truyền thống Hỏa Mão/Linh Tuất) → trùng phép sửa của **Tạ Phồn Trị**. _"buộc lòng kết luận khác... Tỵ Dậu Sửu nhân Tuất Mão vị (ngược cũ)."_
2. **🏆🏆 "MA QUÂN LÀ BẠN ĐẠO" (Ch.20, hỏi đáp lục sát):** Lục sát=Kình Đà Hỏa Linh Không Kiếp; tứ sát=Kình Đà Hỏa Linh. _"cái xấu Không Kiếp tự nó giảm thiểu nếu nỗ lực tu tâm dưỡng tánh; trường hợp đặc biệt cái khó hại Không Kiếp chuyển ngược thành 'MA QUÂN LÀ BẠN ĐẠO' giúp ta tu hành thành đạt."_ Kình Đà Hỏa Linh cũng có thể thành tác nhân giúp thăng tiến tu luyện.
3. **🏆 YẾU TỐ GIỜ + LÝ THIÊN VĂN (Ch.21):** chỉ dùng chi năm thì Hỏa chỉ 4 cung, Linh 2 cung → không cân cho "lục sát" → PHẢI thêm giờ. Địa bàn ứng vị trí so mặt trời; Hỏa Linh khởi cung (tam hợp năm) rồi **chuyển THUẬN theo giờ → Hỏa Linh bất biến so mặt trời** (phái Hán/thiên-văn). Sách VN (thuận-nghịch: Hỏa thuận Linh nghịch) = "dựa lý khác thiên văn." Đằng Sơn (người Việt) tạm dùng VN, nhưng nhận phái Hán chuẩn thiên-văn hơn.
4. **🏆🏆 THIÊN TRÙ = KHẮC TINH HỎA LINH / THỰC THẦN CHẾ SÁT (Ch.21):** Thiên Trù ("bếp trời", an theo CAN, ăn uống/tài lộc) = "dầu sôi lửa bỏng" KIỀM CHẾ thành lạc thú (thú ăn uống) → khắc tinh cặp Hỏa Linh. Lý tương đồng bát tự: Hỏa Linh ⇄ "Sát"; Thiên Trù ⇄ "Thực Thần". **Thực Thần CHẾ Sát** (tốt) — nhưng nếu Hỏa Linh vô dụng (Tham Hỏa/Tham Linh cách tốt) thì Thiên Trù = "Thực Thần PHÁ Sát" (phá cách). An: chiếm đủ sinh-vượng-mộ của hỏa + sinh-vượng kim-thủy.

## 🔧 PHASE A — ENGINE (TDD Iron #3 + live — chạy thật)
- 🟡🟡 **TDD `verify_hoa_linh_school()`** (RED→GREEN, suite **19 passed** +1) — **GHI NHẬN TRUNG THỰC chỗ engine LỆCH Đằng Sơn:** `match_traditional=12` · `engine_follows_traditional=True` · `match_dang_son_correction=9` · `diverges_from_dang_son_at=["Dậu","Sửu","Tỵ"]` · `ty_dau_suu_engine=["Mão","Tuất"]` (truyền thống) vs `ty_dau_suu_dang_son=["Tuất","Mão"]` · `gio_both_thuan_han_school=True` (giờ: engine cộng h cho cả 2 = phái Hán/thiên-văn, KHỚP nguyên tắc Đằng Sơn). → **phá vỡ "engine luôn theo Đằng Sơn"**: engine theo TRUYỀN THỐNG ở năm-anchor Tỵ Dậu Sửu (đa số sách), Hán ở giờ. KHÔNG ép sửa (Iron #3 — present founder duyệt; kept_all hợp lệ).
- ✅ **Founder năm Thìn KHỚP cả 2 phái:** `founder_thin_hoa_linh=["Dần","Tuất"]` (Thân Tý Thìn → Hỏa Dần, Linh Tuất — tranh chấp chỉ ở Tỵ Dậu Sửu, KHÔNG đụng lá Anh). Hỏa Tinh **Dần (Tử Tức)** = nhập cụm Thiên Mã + Mã Khốc Khách; Linh Tinh **Tuất (Nô Bộc)**.
- ✅ **Thiên Trù founder = Ngọ (Phụ Mẫu)** (Mậu→Ngọ, đã thấy live cast V32) — khắc tinh Hỏa Linh hiện diện.

## 🔗 ĐỐI CHIẾU ĐA HỆ — LÁ SỐ ANH (Iron #4/#6/#8 — đọc TÍNH, KHÔNG predict)
- **🎯 "MA QUÂN LÀ BẠN ĐẠO" = chốt lý cho lò-tu-dưỡng (V33):** Đằng Sơn nói THẲNG sát tinh (Không Kiếp / Kình Đà Hỏa Linh) với bậc tu = **nhiên liệu thăng tiến tu luyện**, "ma quân chuyển thành bạn đạo." → đúng cơ chế "chế hóa" của config tứ-mộ (V33): Kiếp Sát (băng-tâm-sát) Mệnh + Hỏa Linh (Dần-Tuất, trục Tử Tức-Nô Bộc) của Anh KHÔNG phải doom mà là **nghịch-cảnh-làm-bạn-đạo**. Iron #4/#6: đọc TÍNH/cơ-chế, KHÔNG phán "anh sẽ vượt nghịch cảnh thành đạo" — chỉ là cấu trúc cho phép chuyển hóa (việc Anh làm = mệnh-động-từ).
- **Tứ sát của Anh định vị đúng:** Hỏa Dần + Linh Tuất (trục Tử Tức-Nô Bộc Dần-Ngọ-Tuất, cùng Mã Khốc Khách) + Kình Ngọ (Phụ Mẫu, giáp Mệnh) + Đà Thìn (Huynh Đệ, giáp Mệnh). → tứ sát KHÔNG tọa Mệnh (Mệnh Tỵ chỉ giáp Kình-Đà, không chứa Hỏa-Linh) — nhất quán "Mệnh tinh-tế giáp-sát chứ không-bị-sát-đè" (V24/V29). Không overclaim.
- **Thiên Trù Ngọ (Phụ Mẫu)** = khắc tinh Hỏa Linh + "bếp trời/ăn uống/tài lộc" ở cung cha mẹ — đọc cấu trúc, không phán.
- **🟡 CONFLICT ĐA PHÁI present founder (Iron #3):** engine Hỏa Linh Tỵ Dậu Sửu theo truyền thống (Hỏa Mão), Đằng Sơn/Tạ Phồn Trị đảo (Hỏa Tuất). KHÔNG đụng lá Anh (năm Thìn), nhưng đụng user tuổi Tỵ/Dậu/Sửu. **Cần Anh quyết:** giữ truyền thống (đa số sách) hay theo Đằng Sơn (suy-lý thủy-hỏa)? → ghi backlog, không tự sửa.

## 💬 Quote đắt nhất
> "ma quân là bạn đạo, giúp ta tu hành thành đạt"
> — Đằng Sơn, Tập 2 tr.241 (sát tinh = nhiên liệu tu-dưỡng — chốt lý lò-tu-dưỡng của Anh)

## 📚 PHASE B — WIKI
- Concept: **hỏa-linh=thủy-hỏa-giao-thoa (hỏa-dương/linh-âm)** · **hỏa-linh-tỵ-dậu-sửu: truyền-thống(hỏa-mão) vs đằng-sơn/tạ-phồn-trị(hỏa-tuất)** · **hỏa-linh-thuận-giờ=bất-biến-so-mặt-trời (phái-hán) vs vn-thuận-nghịch** · **ma-quân-là-bạn-đạo (sát-tinh=nhiên-liệu-tu-dưỡng)** · **thiên-trù=khắc-tinh-hỏa-linh (thực-thần-chế-sát)** · **lục-sát vs tứ-sát**.

## 🎨 PHASE C — UX
- 🎨 Badge Iron #3 (Settings/lá số): "Hỏa Linh Tỵ Dậu Sửu — engine theo TRUYỀN THỐNG (Hỏa Mão); Đằng Sơn/Tạ Phồn Trị đảo (Hỏa Tuất). [Anh duyệt phái]". Toggle tương lai cho founder chọn phái.
- 🎨 Lá số Anh: panel "tứ sát định vị" (Hỏa Dần / Linh Tuất / Kình Ngọ / Đà Thìn — giáp/cận Mệnh, KHÔNG tọa) + nhãn "ma quân là bạn đạo: nghịch-cảnh = nhiên-liệu tu-dưỡng (Đằng Sơn tr.241)".

## ⚠ Iron Rule check
- [x] **Iron #3 TRUNG THỰC** (ghi nhận engine LỆCH Đằng Sơn ở Hỏa Linh, KHÔNG ép sửa, present founder duyệt — phá "engine luôn theo Đằng Sơn") · **KHÔNG predict** ("ma quân bạn đạo" đọc cơ-chế/TÍNH) · TDD đỏ-trước-xanh-sau (19 pass) · cite trang · đa phái (Tạ Phồn Trị/Hán/VN) present · Git Iron #7.

## 📝 Tiến độ
- Tập 2: **253/358tr (~71%)**. **34 vòng phiên này.** (Tập 1 XONG.)

## ⏭ Tiếp theo
- Vòng 35 (T2-15): p254-272 (Ch.22 — vòng Trường Sinh / cách cục Hỏa Linh + Thiên Trù chi tiết).
