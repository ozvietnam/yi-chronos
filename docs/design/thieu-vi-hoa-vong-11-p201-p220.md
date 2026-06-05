# Vòng 11 — Thiệu Vĩ Hoa p201-220 (2026-06-03)

🌸 _Câu chú._

## 📍 Vị trí: p201-220 (Tượng Hào 64 quẻ + Nạp Can Nạp Chi + Hào Thế/Ứng + Lục Thân động biến)
## 📊 Tiến độ: 220/798 (**27.6%**)

## 🎯 5 Paradigm cốt

### 1. ⭐⭐⭐⭐ **Đại cục HỖN THIÊN GIÁP TÝ — Nạp Chi 8 quẻ**
**Quẻ nội (3 hào dưới):**
| Quẻ | Hào 1 | Hào 2 | Hào 3 |
|---|---|---|---|
| Càn | Tý Thủy | Dần Mộc | Thìn Thổ |
| Khảm | Dần Mộc | Thìn Thổ | Ngọ Hỏa |
| Cấn | Thìn Thổ | Ngọ Hỏa | Thân Kim |
| Chấn | Tý Thủy | Dần Mộc | Thìn Thổ |
| Tốn | Sửu Thổ | Hợi Thủy | Dậu Kim |
| Ly | Mão Mộc | Sửu Thổ | Hợi Thủy |
| Khôn | Mùi Thổ | Tỵ Hỏa | Mão Mộc |
| Đoài | Tỵ Hỏa | Mão Mộc | Sửu Thổ |

**Quy luật**: Quẻ dương (Càn/Khảm/Cấn/Chấn) sắp xuôi từ dưới lên; Quẻ âm (Khôn/Tốn/Ly/Đoài) sắp ngược từ trên xuống.

### 2. ⭐⭐⭐ **Nạp CAN 8 quẻ**
| Quẻ | Nạp Can | Ghi chú |
|---|---|---|
| Càn | Giáp (nội) + Nhâm (ngoại) | 2 can vì là cha trời |
| Khôn | Ất (nội) + Quý (ngoại) | 2 can vì là mẹ đất |
| Cấn | Bính | 1 can |
| Đoài | Đinh | 1 can |
| Khảm | Mậu | 1 can |
| Ly | Kỷ | 1 can |
| Chấn | Canh | 1 can |
| Tốn | Tân | 1 can |

### 3. ⭐⭐⭐ **6 hào Càn Khôn ↔ 12 tháng** (lý do nạp chi)
- Hào 9-1 Càn = Tý = tháng 11
- Hào 9-2 Càn = Dần = tháng giêng
- ... cách ngôi
- Hào 6-1 Khôn = Mùi = tháng 6
- Hào 6-2 Khôn = Dậu = tháng 8
- ... cách ngôi, đi ngược

### 4. ⭐⭐⭐ **Hào THẾ và Hào ỨNG — cách xác định** (mỗi cung 8 quẻ)
- Quẻ thuần (Q1): Hào thế ở hào 6
- Q2: hào thế ở hào 1
- Q3: hào 2, Q4: hào 3, Q5: hào 4, Q6: hào 5
- Q7 (Du Hồn): hào thế LÙI về hào 4
- Q8 (Quy Hồn): hào thế TRỞ VỀ hào 3
- **Hào ứng** = hào cách hào thế 3 ngôi

### 5. ⭐⭐⭐⭐ **5 hào TRÌ THẾ — ý nghĩa cốt** (Mai Hoa nâng cao)
| Hào trì thế | Ý nghĩa |
|---|---|
| **Phụ Mẫu** | Thần gian khổ — bận rộn, bôn ba, hôn nhân khó, con hiếm. Nếu Quan Quỷ động sinh → đường VĂN KHOA THI CỬ |
| **Tử Tôn** | Thần phúc — không lo, tai họa thoảng qua. KHÔNG lợi cầu quan |
| **Quan Quỷ** | Thần hoạn nạn — sức khỏe khó yên, nhưng RẤT LỢI cầu danh + cầu quan |
| **Thê Tài** | Của cải phồn vinh. Nếu Tử Tôn động sinh → khỏe + nhiều của. KHÔNG lợi văn thư |
| **Huynh Đệ** | Thần KIẾP TÀI — mất của + khắc vợ. Nếu hóa Quan Quỷ → đại xấu |

## 💬 Quote nguyên văn
> _"Hào thế hưng vượng lại được Nguyệt, Nhật, Hào động, Dụng thần sinh hợp hoặc được một trong những cái đó sinh hợp thì như vải gấm còn thêu hoa."_
> — Thiệu Vĩ Hoa p167

## 🔧 PHASE A — ENGINE

**Đã làm:**
- ✅ Tạo `data/seeds/nap_giap_8_que.json` — đầy đủ Nạp Can + Nạp Chi 8 quẻ + Hào Thế/Ứng

## 📚 PHASE B — WIKI

- ✅ Verify Nạp Giáp với engine `mai_hoa/cast.py` — engine có cơ bản
- ⚠ Lục Thân 5 hào trì thế CHƯA wire chi tiết vào LLM phê mệnh

## 🎨 PHASE C — UX/UI

- 🎨 **Panel "Hào Thế trì thế"**: Hiển thị 1 trong 5 ý nghĩa (Phụ/Tử/Quan/Tài/Huynh) khi user cast
- 🎨 **64 quẻ Nạp Giáp table**: tab bảng tra cho user trí thức

## ⚠ Iron Rule
- [x] Cite nạp giáp theo Kinh Phòng Tây Hán
- [x] 5 hào trì thế = paradigm, KHÔNG predict tuyệt đối

## ⏭ Vòng 12: p221-240 — Lục Thân biến hóa + Lục Thần phát động + 6 thân
