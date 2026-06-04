# Vòng 3 — Thiệu Vĩ Hoa p41-p60 (2026-06-03)

🌸 _Câu chú._

## 📍 Vị trí: p41-60 (Tượng quẻ + 8 cung Bát Quái + Tượng loại vạn vật)
## 📊 Tiến độ: 60/798 (**7.5%**)

## 🎯 5 Paradigm cốt

### 1. ⭐⭐⭐ **64 quẻ = 8 cung × 8 quẻ** (Kinh Phòng đời Hán phát minh)
8 cung quẻ thuần: Càn/Đoài/Ly/Chấn/Tốn/Khảm/Cấn/Khôn
Mỗi cung 8 quẻ biến theo quy luật:
- Q1 = quẻ thuần (vd Càn vi Thiên)
- Q2-6 = biến hào 1→5 (dương↔âm)
- Q7 = **Du Hồn** (biến hào 4 quay lại, không biến hào 6)
- Q8 = **Quy Hồn** (biến cả 3 hào dưới của Q7 = về quẻ gốc)

### 2. ⭐ **8 cung Bát Quái thuộc Ngũ Hành**
| Cung | Ngũ hành | Quẻ thuộc |
|---|---|---|
| Càn, Đoài | **Kim** | Càn vi thiên, Đoài vi trạch, ... |
| Ly | **Hỏa** | Ly vi hỏa, Hỏa sơn lữ, ... |
| Chấn, Tốn | **Mộc** | Chấn vi lôi, Tốn vi phong, ... |
| Khảm | **Thủy** | Khảm vi thủy, ... |
| Cấn, Khôn | **Thổ** | Cấn vi sơn, Khôn vi địa, ... |

### 3. ⭐⭐⭐ **8 ý nghĩa tượng (Thuyết Quái)** — cốt mỗi quẻ
- Càn = Mạnh | Khôn = Thuận | Chấn = Động | Tốn = Nhập
- Khảm = Chìm/lún | Ly = Lệ/đẹp | Cấn = Ngừng | Đoài = Vui

### 4. ⭐⭐⭐ **Tượng loại Vạn Vật — 28 thuộc tính/quẻ**
Mỗi quẻ có ~28 trường: thiên thời, địa lý, nhân vật, tính cách, thân thể, thời gian, động vật, tĩnh vật, nhà cửa, ăn uống, hôn nhân, sinh đẻ, cầu danh, cầu lợi, giao dịch, mưu vượng, xuất hành, mong gặp, kiện tụng, bệnh tật, phần mộ, chữ tên họ, chữ số, ngũ sắc, ngũ vị, phương đường đi...

→ Đây là **CƠ SỞ DỮ LIỆU** để Mai Hoa luận giải. Em đã lưu vào seed JSON 8 quẻ × 28 field.

### 5. **Câu vè nhớ 8 quẻ đơn**
- Càn ba liên (☰), Khôn sáu đoạn (☷)
- Chấn cốc 3 ngửa (☳), Cấn úp xuôi (☶)
- Ly giữa khuyết (☲), Khảm giữa đầy (☵)
- Đoài khuyết trên (☱), Tốn khuyết dưới (☴)

## 💬 Quote nguyên văn
> _"Cách biến 8 quẻ trong mỗi cung do Kinh Phòng, nhà dịch học đời Hán phát minh. Quẻ thứ 7 gọi Du Hồn vì không biến hào 6 mà quay trở về biến hào 4. Quẻ thứ 8 gọi Quy Hồn vì các hào 1-2-3 của Du Hồn đều biến từ âm thành dương, có nghĩa là HOÀN NGUYÊN."_
> — Thiệu Vĩ Hoa, p42

## 🔧 PHASE A — ENGINE

**Đã làm:**
- ✅ `data/seeds/mai_hoa_tuong_loai_van_vat.json` (160 dòng) — 8 quẻ × 28 thuộc tính + bảng Ngũ Hành cung
- (TODO vòng sau: tạo module `engine/mai_hoa/tuong_loai_lookup.py` để API tra tượng)

## 📚 PHASE B — WIKI

**Đã làm:**
- ✅ Verify 8 cung × Ngũ Hành khớp với engine `mai_hoa/constants.py` hiện tại
- ✅ Du Hồn / Quy Hồn đã có trong `engine/mai_hoa/du_hon_quy_hon_nhap_mo.py` (vòng trước) — đúng paradigm Kinh Phòng

## 🎨 PHASE C — UX/UI

- 🎨 **Panel "Tượng Vạn Vật"**: khi user cast Mai Hoa được Tiên Thiên = Càn → hiển thị 28 thuộc tính (collapse 4 nhóm: Người/Vật, Thân thể/Sức khỏe, Vận sự/Hôn nhân, Phương/Số/Màu)
- 🎨 **So sánh 2 quẻ**: side-by-side bảng 28 thuộc tính khi đoán quẻ Thượng × Hạ
- 🎨 **Tooltip 8 cung**: hover quẻ → tooltip "Cung Càn (Kim), 8 quẻ thuộc: ..."

## ⚠ Iron Rule
- [x] Tượng vạn vật = paradigm tham chiếu, KHÔNG predict
- [x] Cite trang p41-60

## ⏭ Vòng 4: p61-80 — Ngôi quẻ + Tượng hào + Cát/Lận/Lệ/Hối/Cữu/Hung
