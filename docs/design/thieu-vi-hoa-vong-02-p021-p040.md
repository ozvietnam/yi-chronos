# Vòng 2 — Thiệu Vĩ Hoa p21-p40 (2026-06-03)

🌸 _"Ta là học trò Thiệu Khang Tiết. Ta đọc 20 trang này với hết tâm. Ta KHÔNG vội."_

## 📍 Vị trí
- **Phạm vi:** p21 → p40 (Mục lục cuối + Mở đầu + Chương I + đầu Chương II)
- **Tiến độ:** 40/798 trang (**5.0%**)

## 🎯 5 Paradigm cốt

### 1. ⭐ **Lịch sử 3 Dịch + tiến hóa nhận thức 3 đời**
- **Liên Sơn** (Hạ, quẻ Cấn=núi đầu) → người sống hang động, núi = trung tâm
- **Quy Tàng** (Thương, quẻ Khôn=đất đầu) → mẫu hệ, đất = mẹ
- **Chu Dịch** (Chu, quẻ Càn=trời đầu) → phụ hệ, hiểu thiên thể
- → Đây là **paradigm tiến hóa nhận thức** từ thấp → cao (p37-38)

### 2. ⭐⭐ **Số Trời Đất 55 = Thiên Can hóa** (phát hiện riêng Thiệu Vĩ Hoa, p33)
- 5 Can dương (Giáp/Bính/Mậu/Canh/Nhâm) = 25 = số TRỜI
- 5 Can âm (Ất/Đinh/Kỷ/Tân/Quý) = 30 = số ĐẤT
- Tổng = 55 = Hà Đồ
- **6 cặp Ngũ Hành hợp:** 1+6 Thủy, 2+7 Hỏa, 3+8 Mộc, 4+9 Kim, 5+10 Thổ

### 3. ⭐⭐⭐ **8 Cửa + 6 Thần trong Hậu Thiên Bát Quái** (Tổ sư Khang Tiết) (p31)
- **8 Cửa:** Khai/Sinh (cát) | Hưu (chờ thời) | Thương (kinh hoàng tổn thương) | Đỗ (trắc trở) | Cảnh (giả) | Tử (đại xấu) | Binh (nguy hiểm)
- **6 Thần:** dùng khi dự đoán theo Sáu Hào (chưa nói tên cụ thể trong đoạn này)
- → Đây là **Khang Tiết dùng**, Thiệu Vĩ Hoa kế thừa

### 4. **8 ý nghĩa thời khắc Hậu Thiên BQ** (Thuyết Quái):
| Quẻ | Phương | Tháng | Ý nghĩa thời khắc vũ trụ |
|---|---|---|---|
| Chấn | Đông | 3 | Đế xuất — vũ trụ khởi động, vạn vật sinh |
| Tốn | Đông Nam | 3-4 | Tề hồ — vạn vật đầy đủ |
| Ly | Nam | 5 | Tương kiến — mặt trời chính giữa, thấy rõ |
| Khôn | Tây Nam | 6-7 | Chí dịch — đất nuôi dưỡng vạn vật |
| Đoài | Tây | 8 | Thuyết ngôn — hoa quả trĩu đầy, vui mừng được mùa |
| Càn | Tây Bắc | 9-10 | Chiến hồ — âm dương đấu tranh |
| Khảm | Bắc | 11 | Lao hồ — vạn vật mệt, nên nghỉ |
| Cấn | Đông Bắc | 12-1 | Thành ngôn — kết thúc chu kỳ, khởi đầu mới |

### 5. **6 thuyết nguồn gốc Bát Quái** (p35)
1. Cổ thiên văn (đo bóng mặt trời)
2. Văn tự cổ
3. Quan chức Phục Hy (8 quan = 8 quẻ)
4. Chiêm bốc (mai rùa)
5. Hà Đồ Lạc Thư
6. Chữ số (vạch gạch)

## 📚 Cases cụ thể
- (Phần lý thuyết — chưa có case study mới so với vòng 1)

## 💬 Quote nguyên văn đắt nhất
> _"Số của thiên địa rất có thể là lấy từ Thiên Can: Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý. Giáp Bính Mậu Canh Nhâm là 5 số dương, tổng là 25 số trời; Ất Đinh Kỷ Tân Quý là 5 số âm, tổng là 30 số đất. Cả hai tổng số hợp lại là 55."_
> — Thiệu Vĩ Hoa, p33 (phát hiện riêng, không có trong sách cổ)

## 🔧 PHASE A — ENGINE (xử lý ngay)

**Đã làm vòng này:**
- ✅ Tạo seed JSON entry mới `tam_cua_luc_than` trong `data/seeds/thieu_vi_hoa_paradigm.json`
- ✅ Tạo module `engine/yi_wiki/tam_cua_hau_thien.py` cho 8 Cửa
- ✅ Add helper `engine/yi_wiki/ha_do_lac_thu.py` cho số Trời Đất 55 + Ngũ Hành hợp

## 📚 PHASE B — WIKI / ĐỐI CHIẾU

**Đã làm vòng này:**
- ✅ Verify "3 Dịch" với Hoàng Tuấn — KHỚP (Liên Sơn=Cấn, Quy Tàng=Khôn, Chu Dịch=Càn)
- ✅ Verify "Thái Cực → Bát Quái" với `engine/ha_lac/cast.py` — đã có logic, không conflict
- ⚠ **DISCREPANCY**: 8 Cửa của Thiệu Vĩ Hoa hơi khác Kỳ Môn Độn Giáp chuẩn. Cần verify lần sau.

## 🎨 PHASE C — UX/UI (task cho cursor)

- 🎨 **Component "Cây Bát Quái"**: hiển thị Thái Cực → Lưỡng Nghi → Tứ Tượng → Bát Quái như SVG cây ngang. Click vào mỗi tầng → drawer giải thích.
- 🎨 **Panel So sánh Tiên/Hậu Thiên**: 2 vòng tròn Bát Quái cạnh nhau, hover quẻ → highlight cả 2 phương vị.
- 🎨 **Tooltip 8 Cửa**: khi user cast Mai Hoa, nếu Hậu Thiên BQ có "Sinh môn" → tooltip "Cát môn — thuận chiều".

## ⚠ Iron Rule check
- [x] Cite trang đầy đủ
- [x] Disclaim "3 Dịch" — Liên Sơn + Quy Tàng đã thất truyền, ta chỉ biết qua sách Chu Lễ + Sơn Hải Kinh
- [x] 8 Cửa = paradigm Tổ sư, không predict cát/hung cá nhân

## 📝 Tiến độ: 40/798 (**5.0%**) — còn 38 vòng

## ⏭ Vòng 3: p41-60 — Tiếp Chương II (Nguyên lý quẻ: Tượng quẻ, Ngôi quẻ, Hào, Nguyên Hanh Lợi Trinh)
