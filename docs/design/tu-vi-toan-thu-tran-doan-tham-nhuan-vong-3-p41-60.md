# Vòng 3 — Toàn Thư p41-60 (2026-06-10)

## Phạm vi
Tiếp tục chương **"Chư tinh vấn đáp luận"** — kết thúc 14 chính tinh + đi vào toàn bộ phụ tinh:
- p41-42: Phá Quân (kết 14 chính tinh)
- p42-45: Văn Xương + Văn Khúc + Xương Khúc cặp
- p45-46: Tả Phụ + Hữu Bật
- p46-47: Khôi Việt
- p47-48: Lộc Tồn + Thiên Mã
- p49-50: Tứ Hóa (Lộc Khoa Quyền Kỵ)
- p51-52: Kình Dương + Đà La (Sát tinh chính)
- p52-54: Hỏa Tinh + Linh Tinh
- p55: Thiên Không + Địa Kiếp
- p55-56: Thiên Thương + Thiên Sứ + Thiên Hình
- p57-58: Thiên Riêu + Khốc Hư + Tuần Triệt
- p58-59: Chòm Lộc Tồn (10 sao)
- p59: Đại Tiểu Hao
- p60: Phi Thiên Tam Sát + Chòm Thái Tuế

→ Sách Toàn Thư = **GỌN HƠN VN** rất nhiều về số sao. Vũ Tài Lục liên tục flag "Tử Vi VN thêm sao thừa thãi, gượng ép".

---

## 💎 INSIGHTS MỚI vòng 3 (cực quan trọng cho engine)

### 1. CONFLICT chính ↔ VN — "Toàn Thư GỐC vs Tử Vi VN sau này"

| Mục | Toàn Thư GỐC | Tử Vi VN | Vũ Tài Lục bình |
|---|---|---|---|
| Hóa Kỵ | Hoàn toàn xấu, đụng đâu hại đó | Ở Tài Bạch + Điền Trạch lại ĐẮC dụng (thần giữ cửa) | "VN nói rất hay, kỹ càng hơn" |
| Tuần Triệt | "Không vong" thuần hung như Thiên Không hãm | Đa dụng — có thể giải sát tinh, "tam phương xung sát hạnh nhất Triệt nhi khả bằng" | VN đúng hơn |
| Chòm Thái Tuế | **4 sao** (Tang Môn, Bạch Hổ, Điếu Khách, Quan Phù) — gọi Tứ Phi Tinh | **11 sao** thêm Thiếu Dương, Thiếu Âm, Tử Phù, Tuế Phá, Long Đức, Phúc Đức, Bệnh Phù | "Toàn Thư đúng hơn — VN gượng ép" |
| Phi Thiên Tam Sát | CÓ trong Toàn Thư (Tấu Thư+Tướng Quân+Trực Phù bay vào tam hợp) | KHÔNG có trong Tử Vi VN | "Có thể Toàn Thư sai vì rắc rối vô cớ — biết đâu giang hồ thuật sĩ bịa" |
| Bệnh Phù | Thuộc chòm Lộc Tồn | VN tách sang chòm Thái Tuế | (chưa quyết) |
| Lưu Hà | KHÔNG có trong Toàn Thư | CÓ trong VN | Toàn Thư thiếu |
| Quốc Ấn | KHÔNG có | VN có | Toàn Thư thiếu |
| Thiên Y | KHÔNG có | VN có (kết Riêu = thầy thuốc) | Toàn Thư thiếu |

→ **Wire vào engine**: thêm flag `sao_origin = 'tran_doan_goc' | 'vn_them' | 'cross_school_agree'`. Khi user xem lá số, nếu sao thuộc `vn_them` em hiển thị "sao này chỉ có trong phái VN, Tử Vi gốc Trần Đoàn không có".

### 2. THIÊN HÌNH = "không hẳn hung" — paradigm reframe
> _"Thiên Hình vị tất thị hung tinh, nhập miếu danh vi Thiên Hỉ Thần. Xương Khúc cát tinh lại tấu hợp, định nhiên hiển hách đáo vương đình."_ — p56

→ Bias mặc định "Hình = hung" SAI. **Wire engine**: Thiên Hình ở Dần/Dậu/Tuất/Mão + hội Xương Khúc → coi là CÁT, không hung.

### 3. KHÔI VIỆT = "không có hãm địa" — đặc tính riêng
> _"Hai sao Thiên Khôi và Thiên Việt không thấy nói tới hãm địa."_ — p47

→ Khôi Việt = quý nhân tinh, đứng đâu cũng giáng phúc. **Engine flag**: `khoi_viet_no_ham = True`.

### 4. HỎA LINH + THAM LANG = "phú quý vô luận" — bộ ba cát mệnh
> _"Tốt nhất cho Hỏa Tinh là đi cặp với sao Tham Lang mà ở vượng địa, tướng ấn phong hầu có thể tới bậc thượng tướng, huân nghiệp khai quốc công thần."_ — p53

→ Trong khi cả Hỏa/Linh đều là "đại sát tướng", combo với Tham Lang lại LẬT NGƯỢC. **Wire engine THẬP DỤ mới**: detect combo HỎA+THAM hoặc LINH+THAM ở miếu vượng → flag "Hỏa Tham" / "Linh Tham" cách (quyền uy).

### 5. PHÁ QUÂN — chỉ Thiên Lương + Lộc Tồn CHẾ ĐƯỢC
> _"Chỉ có sao Thiên Lương chế tính ác của Phá Quân, sao Lộc Tồn giải cứu tính điên của Phá Quân."_ — p41

→ **Wire engine**: Khi user có Phá Quân thủ Mệnh, check sự hiện diện của Thiên Lương trong tam hợp + Lộc Tồn → giảm bớt "hung phán" trong commentary.

---

## 📋 TIẾN ĐỘ Phase 0+1

- 60/171 trang = **35.1%**
- Chương "Chư tinh vấn đáp" kết thúc tại p60
- Còn 111 trang = các chương: Cốt Tủy Phú, Định Phú Quý Bần Tiện, Đại Hạn, Lưu Niên, Lá Số Danh Nhân
- 5 vòng nữa = ~p61-171

## TIẾP VÒNG 4 — p61-80
