# Vòng 8 — Thiệu Vĩ Hoa p141-160 (2026-06-03)

🌸 _Câu chú._

## 📍 Vị trí: p141-160 (Quẻ Thể Dụng + Hào động + Quẻ Hỗ Biến + 4 phương pháp đoán quẻ)
## 📊 Tiến độ: 160/798 (**20%**) 🎉 1/5 cuốn

## 🎯 5 Paradigm cốt

### 1. ⭐⭐⭐⭐ **5 vai trò của Hào Động trong Quẻ Mai Hoa** (p120)
1. Phân biệt **Quẻ Thể** vs **Quẻ Dụng** (Hào động ở quẻ Hạ → quẻ Hạ là DỤNG)
2. Phân biệt **Quẻ Biến** (Hào động → dương ↔ âm → quẻ mới)
3. Đoán cát/hung sự việc (xem hào từ tương ứng)
4. Phân biệt biến sinh/khắc/ngang nhau/xấu đi
5. Hướng người đi xa + phương biến hóa

### 2. ⭐⭐⭐⭐ **Quẻ THỂ vs Quẻ DỤNG — paradigm CỐT Mai Hoa**
- **Thể** = MÌNH | **Dụng** = người khác / sự việc
- **Thể khắc Dụng** = **CÁT** (mình thắng)
- **Dụng khắc Thể** = **HUNG** (bị hại)
- **Thể sinh Dụng** = hao tổn (cho đi)
- **Dụng sinh Thể** = tin mừng (nhận về)
- **Thể ngang Dụng** = thuận lợi 100 việc

→ **14 quẻ NGANG NHAU**: Càn, Khảm, Cấn, Chấn, Tốn, Ly, Khôn, Đoài (8 quẻ thuần) + Lý, Quải, Khiêm, Bốc, Hằng, Ích

### 3. ⭐⭐ **Quẻ Hỗ + Quẻ Biến = 3 giai đoạn sự việc**
- **Quẻ Chủ** = giai đoạn ĐẦU (gốc)
- **Quẻ Hỗ** = giai đoạn GIỮA (lấy 4 hào giữa của Quẻ Chủ chia thành thượng-hạ)
- **Quẻ Biến** = giai đoạn CUỐI (hào động biến → quẻ mới)

→ Cát Chủ + Hung Biến = TRƯỚC CÁT SAU HUNG
→ Hung Chủ + Cát Biến = TRƯỚC HUNG SAU CÁT
→ **Càn, Khôn KHÔNG có quẻ Hỗ**

### 4. ⭐⭐⭐ **4 phương pháp đoán Thời gian ứng nghiệm** (p123)
1. **Theo Tượng Quẻ**: Càn-Đoài→Canh-Tân-Tuất-Hợi-Dậu; Chấn-Tốn→Giáp-Ất-Dần-Mão-Thìn; Khôn-Cấn→Mậu-Kỷ-Thìn-Tuất-Sửu-Mùi; Khảm→Nhâm-Quý-Hợi-Tý; Ly→Bính-Đinh-Tỵ-Ngọ
2. **Theo Số Quẻ** (CHÍNH ỨNG): Càn(1)+Khảm(6)=7 → 7 năm/tháng/ngày/giờ
3. **Theo Quẻ Sinh Thể**: nhanh; Quẻ Hỗ sinh thể: từ từ; Quẻ Biến sinh: chậm hơn
4. **Theo Trạng thái Động/Tĩnh người đến đoán**:
   - Đi lại = chia 2 (nhanh)
   - Đứng = giữ nguyên
   - Ngồi = bình thường
   - Nằm = nhân 2 (chậm)

### 5. ⭐⭐⭐ **4 phương pháp đoán Quẻ** (p124-128)
1. **Hào Động** (1 hào động = sự việc đơn; nhiều hào = sự việc lặp)
2. **Tượng Quẻ** (case Tấn Văn Công + Bắc Kinh không lụt 1987)
3. **Nghĩa Lý** (Khổng Tử > Tử Cống đoán Lỗ đánh Việt = "lấy đỉnh gãy chân" — nhưng đi thuyền không dùng chân → CÁT)
4. **Lý Số** (Thiệu Khang Tiết ông già 5 ngày chết = Càn1+Tốn5+Mão4 chia 2 = 5)

## 💬 Quote nguyên văn
> _"Bát Quái to vô cùng, nhỏ cũng vô cùng. Xa thì bao gồm hết vạn vật, gần thì chỉ có bản thân nó, nên thời gian ứng nghiệm xa là năm-tháng, gần là ngày-giờ. Khi đoán cần căn cứ tình hình THỰC TẾ, không phân biệt rõ việc lớn nhỏ mà nói đại khái thì nhất định sẽ sai."_
> — Thiệu Vĩ Hoa p124

## 🔧 PHASE A — ENGINE

**Đã làm:**
- ✅ Tạo `engine/mai_hoa/the_dung_van_phuong.py` — quan hệ Thể/Dụng + 4 thời gian + Hào động

## 📚 PHASE B — WIKI

**Đã làm:**
- ✅ Verify Quẻ Hỗ + Biến đã có trong `engine/mai_hoa/cast.py` — đúng paradigm Khang Tiết
- ⚠ Đoán theo trạng thái động/tĩnh user CHƯA wire vào engine — cần upgrade

## 🎨 PHASE C — UX/UI

- 🎨 **Hỏi user trạng thái** khi cast: "Anh đang đi/đứng/ngồi/nằm?" → engine điều chỉnh thời gian ứng nghiệm
- 🎨 **3 chiều sự việc** SVG: Chủ → Hỗ → Biến (timeline đầu/giữa/cuối)
- 🎨 **Highlight 14 quẻ Ngang Nhau**: badge "Thể=Dụng → 100 việc thuận"

## ⚠ Iron Rule
- [x] Phương pháp đoán = paradigm tham chiếu
- [x] Cite Khổng Tử + Tử Cống case = lịch sử, không tạo fortune-telling

## ⏭ Vòng 9: p161-180 — Mai Hoa Dịch Số tiếp + Tượng vạn vật mở rộng
