# 🧠 Nâng cấp TRÍ TUỆ tình duyên — bài học từ 3 tài liệu (Anh giao 2026-06-24)

> Anh: cái đã xây "mới là MÓNG". GOAL = **sản phẩm PRO xứng đáng thu phí**. 3 file là **AI MIỄN PHÍ trả lời** → bản trả phí (Claude) + **thủ thư giữ kho sách thật** phải VƯỢT nó: ground vào sách cổ thật, không xào tóm tắt web. Đốt tiền thật, multi-agent, **không hỏi — tự chọn đường khôn nhất**.

## 3 tài liệu (đọc theo đúng số Anh đánh)
- **#1 QUY TRÌNH** (xương sống): 12 bước Tử Vi + 10 bước Bát Tự + xếp hạng yếu tố.
- **#2 ĐỘ SÂU khắc phu**: thang 5 cấp + rèn-được/phải-chọn-khôn + lộ trình.
- **#3 NHU CẦU user**: bộ câu hỏi theo tuổi + ma trận năng lực 3 hệ.

## #1 — QUY TRÌNH CHUẨN
**Tử Vi 12 bước**: (1) cung Phu Thê [chính tinh + trạng-thái miếu/vượng/hãm + Hóa + cát + sát + đào hoa + Tuần Triệt] (2) tam chiếu Phu Thê↔Phúc Đức↔Thiên Di (3) xung chiếu Phu Thê↔Quan Lộc (4) so lá số đôi (5) đại vận→Phu Thê (6) tiểu hạn & lưu niên (7) Tử Tức (con=cầu nối) (8) Điền Trạch (vật chất) (9) Nô Bộc (**người thứ ba**) (10) Tật Ách (sức khỏe) (11) Tài Bạch (12) Mệnh (bản chất bản thân).
**Bát Tự 10 bước**: (1) Nhật chủ + Phu Thê tinh (官=chồng, 杀=tình nhân) (2) Quan Sát vượng/nhược (3) **Thương Quan = gốc khắc phu** (4) **chế hóa Thương Quan** (Ấn khắc Thương / Thực-Tài thông quan) (5) đại vận→Quan Sát (6) lưu niên (7) tứ trụ xung-hình-hợp (8) **ngũ hành thiếu** (thiếu Kim=thiếu chồng…) (9) thần sát (đào hoa/hồng loan/cô thần) (10) cung vị & tàng can (xa/gần, sớm/muộn).
**Xếp hạng**: TRỰC TIẾP 60-70% (chính tinh+trạng thái Phu Thê, 官杀, Thương Quan khắc Quan, Hóa Kỵ+sát Phu Thê) · GIÁN TIẾP 20-25% (tam chiếu, xung Quan Lộc, Tử Tức, đại vận, chế hóa, Mệnh, ngũ hành thiếu) · TIỀM ẨN 10-15% (Nô Bộc, Điền Trạch, Tài Bạch, Tật Ách, thần sát, tàng can, tiểu hạn).

## #2 — THANG 5 CẤP "khắc phu" (mệnh là động từ, có cấp độ + lối ra)
L5 tử-vong (0% đổi, chỉ không-cưới) · L4 bệnh/suy (10-15%, chọn cưới muộn/cách tuổi/sống xa) · **L3 bất hòa-ly hôn (40-50% — RANH GIỚI: rèn bắt đầu có tác dụng rõ)** · L2 lạnh nhạt (50-60%) · L1 tiềm ẩn (70-80%). Lộ trình rèn: Thương Quan→Thực Thần (bớt cãi/kiêu→khích lệ/khiêm), Cô Thần Quả Tú→mở lòng, Cự Môn→khéo lời. **Nguyên tắc vàng: khắc phu = TIỀM NĂNG, kích hoạt hay không tùy HÀNH VI — không phải án.**

## #3 — Ma trận năng lực 3 hệ (route câu hỏi đúng hệ)
- **Tử Vi** giỏi: năm cưới (85-90%), tính cách chồng, hòa hợp, số con, dấu hiệu ly hôn.
- **Bát Tự** giỏi: tính cách bản thân, thời điểm cưới chính xác, tuổi chênh, cự ly chồng, tướng chồng, **ngoại tình**, **khắc phu/vượng phu**, **ngũ hành thiếu**.
- **Kinh Dịch/Mai Hoa** giỏi: quyết định "có nên cưới/chia tay" (nhị nguyên), chọn ngày cưới, thời cơ sinh con. ← hệ ta CÓ `engine/mai_hoa` mà CHƯA nối.
- Câu hỏi theo tuổi: 16-20 (khó lấy chồng?/khắc chồng?/crush hợp?) · 21-25 (năm cưới?/định mệnh?/có nên chia tay chờ?) · 26-30 (sao chưa lấy được?/năm vàng?/sinh con?/ngoại tình?) · 31-35 (hôn nhân ổn?/ngoại tình?/hay cãi vì sao?) · 36-40 (bền đến già?/góa?/khắc con?). Nhóm **26-30 nhu cầu cao+khẩn nhất**.

## 🪞 Gap của "móng" hiện tại
`reading.py` chỉ đọc **bước 1/12 Tử Vi + ~2/10 Bát Tự** (cung Phu Thê + đếm 官杀). Bỏ trắng: tam chiếu, Quan Lộc, Tử Tức, **Nô Bộc/người-thứ-ba**, Điền Trạch, Tật Ách, Tài Bạch, Mệnh; **Thương Quan + chế hóa** (gốc khắc phu); ngũ hành thiếu; tàng can. Reframe **cụt** (scrub) thay vì **chấm cấp + chỉ đường**. Chưa route câu hỏi/tuổi. Chưa nối Mai Hoa.

## 🏗️ 3 TRỤ NÂNG CẤP
1. **Đọc TRỌN quy trình** (#1) — NỐI các engine sẵn (`per_cung_reading`, `deep_cung`, `mieu_vuong_ham`, `dai_van_luu_nien_phu_the`; BT `thap_than`/`hoa_giai`/`dung_than`/`ngu_hanh`/`nu_menh`/`vuong_suy_dao_nghich`) vào 12+10 bước → tổng hợp kim-tự-tháp (trực tiếp→gián tiếp→tiềm ẩn). **Làm trước — xương sống.**
2. **Chấm cấp + chỉ đường** (#2) — thay scrub bằng thang 5 cấp + rèn-được/chọn-khôn + lộ trình. Sửa hàng rào paradigm: gọi đúng cái khó + chấm cấp + lối thoát (không vứt phân tích).
3. **Route câu hỏi theo tuổi + 3 engine** (#3) — trả lời câu hỏi cụ thể của tuổi; mỗi câu giao hệ mạnh nhất; **nối Mai Hoa** làm tầng quyết định.

**Nguyên tắc thủ thư**: mọi luận điểm ground vào sách thật trong kho (王亭之 深造讲义, 女命骨髓赋, 形性赋, Toàn Thư, Thiệu Vĩ Hoa, Trích Thiên Tủy, wiki) — VƯỢT bản free-AI (vốn chỉ trích web lichngaytot/tuviglobal).

---

## ✅ ĐÃ DỰNG XONG cả 3 trụ (2026-06-25, 217 test, qua phản biện đối kháng từng trụ)
- **Trụ 1** `engine/tinh_duyen/{tuvi_process,batu_process,quy_trinh}.py` → `read_tinh_duyen.quy_trinh_day_du` (12+10 bước, kim-tự-tháp). Nối engine sẵn, không xây lại.
- **Trụ 2** `cham_cap.py` + `knowledge/cham_cap_do.json` → `chan_doan_cap_do` (5 cấp + lộ trình). **Sửa hàng rào** `_scrub`/`hermes_guard` context-aware (cho khái niệm phân tích, chặn lời-phán-vào-người) — vá over-scrub xóa Thương Quan. + đối-chiếu-chéo 2 phái.
- **Trụ 3** `cau_hoi_router.py` + `knowledge/cau_hoi_tuoi.json` → `cau_hoi_tuoi` (31 câu/5 nhóm tuổi); `gieo_que_quyet_dinh.py` (Mai Hoa cho câu quyết định, tái dùng `core.hexagram`+`the_dung_van_phuong`, Iron #4). API `/gieo-que`.
- **UX** GieoDuyenPanel.vue: 3 khối PRO + nút gieo quẻ + dark-mode tokens. read_tinh_duyen = 18 key, API không vỡ.
- Lỗi adversarial bắt được: engine **bịa** "Tham Lang ở Tử Tức" (guard) · **over-scrub** xóa Thương Quan (context-aware) · bịa luận lá-số-không-có. → đã fix hết.
- Deploy: push→CI (Dockerfile npm build webapp)→VPS kinhdich.online.
