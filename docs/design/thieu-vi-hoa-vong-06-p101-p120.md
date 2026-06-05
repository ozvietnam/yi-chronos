# Vòng 6 — Thiệu Vĩ Hoa p101-120 (2026-06-03)

🌸 _Câu chú._

## 📍 Vị trí: p101-120 (Thiên tai vận mệnh + 12 Tiết Lệnh + Tứ Trụ + Thần Sát)
## 📊 Tiến độ: 120/798 (**15.0%**)

## 🎯 5 Paradigm cốt

### 1. ⭐⭐⭐ **Quy luật năm có số 9 = chiến tranh/máu chảy** (p92)
> _"Trung Quốc phàm những năm có chữ số cuối là 6, 7, 8, 9 thường không thuận. Đặc biệt năm có số 9 là động quân đội, có chiến tranh."_
- 1929 = quân phiệt cát cứ tàn sát
- 1939 = kháng Nhật phát triển toàn diện
- 1949 = chiến tranh giải phóng
- 1959 = chiến tranh Trung Ấn
- 1969 = biên giới Trung-Xô
- 1979 = chiến tranh Việt-Trung
→ **Năm 2029 dự đoán bất ổn** (paradigm Thiệu)

### 2. ⭐⭐ **Case study 1988 — Mộc khắc Thổ** (p91)
1988 = "Đại Lâm Mộc" + Mậu Thìn (Thổ) → **Mộc khắc Thổ** → 3 tai họa:
- Dịch viêm gan Thượng Hải (Mộc=gan)
- Nạn lụt (Mộc khắc Thổ)
- Mất mùa (Thổ là mẹ nuôi vạn vật)
→ Thiệu dùng paradigm này dự đoán 1989 còn nặng hơn

### 3. ⭐⭐⭐ **CÁCH LẤY THÁNG THEO NĂM** (cốt cho engine bat_tu)
| Năm Can | Tháng Giêng bắt đầu |
|---|---|
| Giáp / Kỷ | Bính Dần |
| Ất / Canh | Mậu Dần |
| Bính / Tân | Canh Dần |
| Đinh / Nhâm | Nhâm Dần |
| Mậu / Quý | Giáp Dần |

### 4. ⭐⭐⭐ **CÁCH LẤY GIỜ THEO NGÀY**
| Ngày Can | Giờ Tý bắt đầu |
|---|---|
| Giáp / Kỷ | Giáp Tý |
| Ất / Canh | Bính Tý |
| Bính / Tân | Mậu Tý |
| Đinh / Nhâm | Canh Tý |
| Mậu / Quý | Nhâm Tý |

### 5. ⭐⭐⭐⭐ **7 THẦN SÁT** (paradigm Tứ Trụ + Mai Hoa nâng cao)
| Thần Sát | Tra | Ý nghĩa |
|---|---|---|
| **Quý Nhân** (Thiên Ất) | Giáp/Mậu→Sửu/Mùi, Ất/Kỷ→Tý/Thân, Bính/Đinh→Hợi/Dậu, Nhâm/Quý→Mão/Tỵ, Canh/Tân→Dần/Ngọ | Cứu trợ, gặp nạn có người giúp |
| **Sao Mã** (Dịch Mã) | Thân-Tý-Thìn→Dần; Dần-Ngọ-Tuất→Thân; Tỵ-Dậu-Sửu→Hợi; Hợi-Mão-Mùi→Tỵ | Chạy động, lao khổ; nhiều = bôn ba |
| **Đào Hoa** (Hàm Trì) | Dần-Ngọ-Tuất→Mão; Tỵ-Dậu-Sửu→Ngọ; Thân-Tý-Thìn→Dậu; Hợi-Mão-Mùi→Tý | Đẹp, thông minh, phong lưu; Hoa ngoài tường = thị phi |
| **Kình Dương** (Dương Nhẫn) | Giáp→Mão, Bính/Mậu→Ngọ, Canh→Dậu, Nhâm→Tý (lấy can ngày) | Kiếp sát, hữu hỉ hữu kỵ |
| **Lộc** | Giáp→Dần, Ất→Mão, Bính/Mậu→Tỵ, ... | Phúc lộc |
| **Hoa Cái** | Dần-Ngọ-Tuất→Tuất; Tỵ-Dậu-Sửu→Sửu; ... | Thông minh hiếu học, cô độc, ham đạo |
| **Thiên La / Địa Võng** | Tuất-Hợi=Thiên La, Thìn-Tỵ=Địa Võng | Phạm hình pháp |

## 💬 Quote nguyên văn
> _"Hoa trong tường không dễ bị hái, Hoa ngoài tường dễ bị người đi qua hái. Hoa trong tường ít bị thị phi mang tiếng; Hoa ngoài tường dễ bị thị phi."_
> — Thiệu Vĩ Hoa p101 (về Đào Hoa)

## 🔧 PHASE A — ENGINE

**Đã làm:**
- ✅ Tạo `data/seeds/than_sat_7_sao.json` — 7 Thần Sát với bảng tra
- ✅ Update seed thêm "luat_nam_9" (quy luật năm có số 9)

## 📚 PHASE B — WIKI

**Đã làm:**
- ✅ Verify engine `bat_tu/dia_chi.py` đã có Đào Hoa + Quý Nhân chưa? — Engine bat_tu CHƯA có toàn bộ 7 Thần Sát này
- ⚠ Cần upgrade engine bat_tu để thêm Sao Mã, Kình Dương, Hoa Cái, Thiên La Địa Võng

## 🎨 PHASE C — UX/UI

- 🎨 **Badge Thần Sát**: panel Bát Tự hiển thị "Anh có Quý Nhân ★", "Đào Hoa ngoài tường", "Sao Mã hợp/xung" (icon + tooltip)
- 🎨 **Quy luật năm 9**: timeline 1929 → 2029 với highlight các năm chiến tranh + dự đoán 2029

## ⚠ Iron Rule
- [x] Quy luật năm 9 = paradigm Thiệu, **disclaim**: pattern lịch sử TQ, áp VN cần verify
- [x] Thần Sát = bảng tra, KHÔNG predict tuyệt đối

## ⏭ Vòng 7: p121-140 — Quẻ thể quẻ dụng + phương pháp tính Bát Quái
