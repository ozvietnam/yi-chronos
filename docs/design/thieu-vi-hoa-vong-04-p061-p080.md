# Vòng 4 — Thiệu Vĩ Hoa p61-p80 (2026-06-03)

🌸 _Câu chú._

## 📍 Vị trí: p61-80 (Nguyên-Hanh-Lợi-Trinh + 6 mức Cát-Hung + Chương III Khoa học)
## 📊 Tiến độ: 80/798 (**10.0%**) — đã hết Phần I Chương I-III

## 🎯 5 Paradigm cốt

### 1. ⭐⭐⭐ **6 mức Cát Hung** (Cao Hạnh - Kinh dịch cổ kinh kim chú)
| Cấp | Tên | Nghĩa | Phân cấp |
|---|---|---|---|
| 1 | **Cát** | Phúc tường, thiện | Sơ/Trung/Chung cát; Đại/Nguyên cát |
| 2 | **Lận** | Khó khăn, gian nan | Tiểu/Chung/Trinh lận |
| 3 | **Lệ** | Nguy hiểm | Hữu/Trinh lệ |
| 4 | **Hối** | Thế khó khăn quẫn bức | Hữu/Vô hối; Hối hữu hối; Hối vong |
| 5 | **Cữu** | Tai hoạn nhẹ (nặng hơn Hối, nhẹ hơn Hung) | Vi/Phi/Hà/Vô cữu |
| 6 | **Hung** | Tai họa lớn, ác | Chung/Hữu/Trinh hung |

→ **Engine YI-Chronos cần phân biệt 6 mức này khi LLM phê mệnh**, không gộp chung "cát/hung".

### 2. ⭐⭐ **Nguyên-Hanh-Lợi-Trinh** (4 đức cốt)
- **Nguyên** = đại nguyên (lớn)
- **Hanh** = hành thông
- **Lợi** = có lợi (cụ thể có "Không có cái gì không lợi" = phổ quát)
- **Trinh** = chính bền (Trinh Cát/Hung/Lịch/Khả/Lợi)

### 3. ⭐⭐⭐ **Bát Quái với 14 lĩnh vực khoa học** (Chương III)
1. Sử học (giáp cốt văn ghi chiêm bốc)
2. **Toán học** — Phục Hy = thủy tổ; Leibniz phát minh máy tính từ Bát Quái
3. **Y học** — Hoàng Đế Nội Kinh + Y dịch tương thông
4. **Nhân thể** — 8 quẻ × 8 bộ phận (Càn=đầu, Khôn=bụng, ...)
5. **Sinh học/Di truyền** — DNA 4 base × 3 codons = 64 (khớp 64 quẻ)
6. Giáo dục tư tưởng phẩm chất
7. Luật pháp (Khốn/Cách/Vô Vọng/Tụng)
8. Khí tượng (16 quẻ chuyên về thời tiết, Thiệu đoán đúng 68.16%)
9. **Thiên văn** — Lưu Tử Hoa 1940 dự đoán ngôi sao thứ 10 Thái Dương Hệ làm chấn động giới khoa học
10. **Quân sự** — Bát trận đồ Gia Cát Lượng + Đỗ Hiến + Tôn Tẫn
11. Khí công — Thủy Hỏa Ký Tế = Tâm Thận Tương Giao
12. Hôn nhân (quẻ Hàm, Tiểu Súc, Cấn, Truân, Khuê, Bí)
13. Phật giáo / Đạo giáo
14. **Triết học** — Một chia hai = Thái Cực sinh Lưỡng Nghi; Mâu thuẫn = Âm Dương; thuyết tương đối Einstein liên quan Bát Quái
15. Văn học (thủ pháp tỉ dụ, thơ ca, dân ca)
16. **Trị quốc** — Văn Vương diễn dịch, Khương Tử Nha quân sư, Tần Thủy Hoàng không đốt sách dịch, Trương Lương + Từ Mậu Công + Gia Cát Lượng + Lưu Bá Ôn

### 4. ⭐⭐ **3 đợt sóng khoa học tự nhiên** (Lý Thụ Thanh)
- Đợt 1: Tượng số "Chu Dịch" + quan niệm chỉnh thể
- Đợt 2: Galilei → Newton → Einstein (máy đo + số liệu)
- Đợt 3: 1960- (khoa học hệ thống, cơ cấu hao tán, lý thuyết hỗn độn, hình học Fractal, số học nhất nguyên hàm)
→ 14 thành tựu lớn 1980+ có 9 do nhà khoa học TQ, đều bắt nguồn tượng số

### 5. **Thân thể = máy cảm ứng thông tin**
- Da: đau, ngứa, nóng, lạnh
- Mắt: xa gần, to nhỏ, màu sắc
- Mũi: thơm thối
- Miệng: vị
- Tai: âm thanh
→ Các công cụ hiện đại (kính viễn vọng, điện thoại) đều bắt nguồn từ cảm ứng cơ thể
→ Bát Quái = công cụ cảm ứng SIÊU VIỆT khả năng cơ thể

## 💬 Quote nguyên văn đắt nhất
> _"Người ta có thói quen: bất kỳ làm việc gì, đầu tiên phải nắm tin tức. Dự đoán thông tin là CƠ SỞ của vấn đề, là bước đầu tiên của mọi công việc, cũng là sự bảo đảm cho công việc thắng lợi."_
> — Thiệu Vĩ Hoa, p76

## 🔧 PHASE A — ENGINE

**Đã làm:**
- ✅ Tạo `engine/yi_wiki/cat_hung_6_muc.py` — 6 mức + sub-categories
- (TODO vòng sau: seed JSON 14 lĩnh vực khoa học × Bát Quái)

## 📚 PHASE B — WIKI

**Đã làm:**
- ✅ Verify 8 quẻ × bộ phận cơ thể khớp với engine `dong_y/`
- ⚠ Engine LLM phê mệnh hiện CHỈ phân biệt cát/hung — cần upgrade thành 6 mức

## 🎨 PHASE C — UX/UI

- 🎨 **Color-code 6 mức cát hung**: Cát=xanh lá, Lận=xanh dương, Lệ=cam, Hối=vàng, Cữu=hồng, Hung=đỏ
- 🎨 **Panel "14 lĩnh vực Bát Quái"** — interactive list, user click → drawer giải thích cách Bát Quái ứng dụng

## ⚠ Iron Rule
- [x] 6 mức cát/hung = phân loại, KHÔNG predict tuyệt đối
- [x] 14 lĩnh vực = paradigm tham chiếu, cite p63-75

## ⏭ Vòng 5: p81-100 — Học thuyết Âm Dương + Ngũ Hành + Thiên Can + Địa Chi
