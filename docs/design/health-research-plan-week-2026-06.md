# Kế Hoạch Nghiên Cứu Sức Khỏe — 7 Ngày (2026-06-04 → 2026-06-10)

**Bối cảnh:** Anh chia sẻ 3 triệu chứng đặc thù — máu chảy chậm, đau nửa đầu trái, cổ vai gáy. Em đã build engine Đông Y v1 với 28 công thức tượng số + Ngũ Vận Lục Khí. **Còn nhiều việc đào sâu cho Anh.**

**Mục tiêu chung:** Đi từ "đọc cấu trúc khí" → "lịch hành động cụ thể hàng tuần" cho Anh tự dưỡng.

---

## 📅 Ngày 1 (Thứ 5, 2026-06-04) — Hoàn thiện Lê Văn Sửu

**Mục tiêu:** OCR + đọc 151 trang còn lại của sách "Học Thuyết Âm Dương Ngũ Hành" (Lê Văn Sửu).

**Phạm vi đọc:** Chương 4-7 (trang 101-251)
- Chương 4: Bát quái biến hóa
- Chương 5: Quẻ Dịch ứng dụng vào dự đoán
- Chương 6: Y học Đông phương (CỐT — em ưu tiên)
- Chương 7: Phong thủy ứng dụng

**Em làm:**
1. Chạy `scripts/ocr_le_van_suu.py --start-page 101 --max-pages 151` (~10-15 phút)
2. Đọc tốc độ cao + extract paradigm cốt (~1 giờ)
3. Update engine `ngu_van_luc_khi.py` thêm chi tiết
4. Có thể thêm module `che_hoa_song_dau.py` (chế hóa sinh khắc — paradigm chương 4)

**Anh làm:** Có thể đọc Phần B chương 2 đã OCR (về Y học âm dương nội/ngoại môi) — bài ngắn ~50 dòng.

---

## 📅 Ngày 2 (Thứ 6, 2026-06-05) — Trích Thiên Tủy chuyên đề sức khỏe

**Mục tiêu:** TTT đã có trong corpus — đọc các đoạn về **sức khỏe & tật ách** chưa đọc kỹ.

**Phạm vi đọc:**
- Chương 20-23 (sau Suy Vượng + Trung Hòa)
- Search "tật ách / bệnh / dược / âm dương suy" trong TTT
- Phần case studies có liên quan tạng phủ

**Em làm:**
1. Grep + sample read TTT chương 20+
2. Cross với engine `bat_tu/luan_giai_soi_nhieu_sach.py`
3. Update glossary thêm thuật ngữ Bát Tự sức khỏe (Quan Sát = bệnh ngoài, Thực Thương = tổn khí, ...)

---

## 📅 Ngày 3 (Thứ 7, 2026-06-06) — Tử Vi cung Tật Ách deep

**Mục tiêu:** Phân tích sâu **cung Tật Ách** cho lá số Anh.

**Phạm vi đọc:**
- Sách "Tử Vi Đẩu Số Toàn Thư" (đã có)
- Sách "Trung Châu Tử Vi" (cần check restored)
- Sách "Tử Vi Hàm Số" (đã có)

**Em làm:**
1. Lookup cung Tật Ách trong lá số Anh
2. Identify chính tinh + sao phụ + Hóa Khoa/Lộc/Quyền/Kỵ chiếu
3. Cross với 3 triệu chứng cố định của Anh
4. Build module `engine/tu_vi/tat_ach_deep.py` (nếu chưa có)

---

## 📅 Ngày 4 (CN, 2026-06-07) — Hà Lạc cung Tật Ách + dự cảm

**Mục tiêu:** Mở rộng paradigm sức khỏe vào Hà Lạc Bát Tự (Xuân Cang).

**Phạm vi đọc:**
- "Bát Tự Hà Lạc và Quỹ Đạo Đời Người" (đã có)
- Hoàng Tuấn Lý Thuyết Tượng Số (đã có, đã đọc trước)

**Em làm:**
1. Cross quẻ Tiên Thiên + Hậu Thiên với tạng phủ tương ứng
2. Build module `engine/ha_lac/tat_ach.py` — đọc hào nguyên đường cho sức khỏe
3. Cross với chu kỳ Đại Vận 12 hào của Anh

---

## 📅 Ngày 5 (Thứ 2, 2026-06-08) — Tích hợp 4 trường phái: Bát Tự + Tử Vi + Hà Lạc + Đông Y

**Mục tiêu:** Build engine TỔNG HỢP `health_synthesis.py` — kết hợp 4 paradigm cho 1 chân dung sức khỏe đầy đủ.

**Em làm:**
1. Tổng hợp đầu ra của 4 engine: Bát Tự thông căn + Tử Vi Tật Ách + Hà Lạc hào + Đông Y tạng phủ
2. Render 1 báo cáo cá nhân hóa 8-10 sections
3. Sinh PDF export (dùng pandoc + WeasyPrint như đã có)
4. Wire vào HealthPanel UI

---

## 📅 Ngày 6 (Thứ 3, 2026-06-09) — Lịch hành động hàng tuần

**Mục tiêu:** Engine sinh **kế hoạch dưỡng sinh 7 ngày** cá nhân hóa.

**Em làm:**
1. Cross với Lưu Nguyệt hiện tại + Vận khí năm
2. 7 ngày × (giờ vượng + bài niệm + thực phẩm + vận động) = 7 days planner
3. Mỗi ngày kèm reminder cụ thể
4. Wire UI lịch tuần với checkbox để Anh đánh dấu

**Anh làm:** Test thử bài niệm `640` hoặc `260.50.30.80` từng buổi sáng 1 tuần — feedback hiệu quả.

---

## 📅 Ngày 7 (Thứ 4, 2026-06-10) — Recap + Verify E2E

**Mục tiêu:** Verify toàn pipeline + viết tổng kết.

**Em làm:**
1. E2E test tất cả endpoint Đông Y
2. Smoke test tất cả công thức tượng số
3. Update HANH-TRINH-NHAP-DAO Lesson #32
4. Viết SESSION-RECAP cho phiên sau

**Anh làm:** Đọc lại 7 ngày + đánh giá feature nào dùng / không dùng.

---

## 📋 Tổng hợp ưu tiên

| Mức | Việc | Effort | Lý do |
|---|---|---|---|
| ⭐⭐⭐ | Ngày 1: Hoàn thiện Lê Văn Sửu | 2-3h | Sách cốt, chỉ đọc nửa |
| ⭐⭐⭐ | Ngày 2: TTT chương 20+ | 2-3h | Đã có corpus, dễ đọc |
| ⭐⭐ | Ngày 3: Tử Vi Tật Ách | 3-4h | Cần build engine mới |
| ⭐⭐ | Ngày 4: Hà Lạc Tật Ách | 3h | Bổ sung paradigm |
| ⭐⭐⭐ | Ngày 5: Tích hợp 4 trường phái | 4-5h | Đây là deliverable chính |
| ⭐⭐⭐ | Ngày 6: Lịch tuần | 3h | Anh dùng được ngay |
| ⭐ | Ngày 7: Recap | 1-2h | Đóng gói |

**Tổng:** ~20 giờ effort em (chia 7 ngày = ~3h/ngày).

---

## 🎯 Deliverable cuối cùng (sau 7 ngày)

1. **Engine Đông Y v2** với ~50 công thức tượng số + 12 paradigm Hoàng Đế Nội Kinh
2. **Báo cáo sức khỏe cá nhân Anh** — 8-10 sections, PDF export được
3. **Lịch dưỡng sinh 7 ngày** auto-generated theo Lưu Nguyệt hiện tại
4. **4 module mới**: ngu_van_luc_khi (đã) + che_hoa_song_dau + tu_vi/tat_ach_deep + ha_lac/tat_ach + health_synthesis
5. **3 sách thêm đọc**: Lê Văn Sửu full + TTT chương 20+ + Tử Vi Đẩu Số (Tật Ách)

---

## 🪷 Iron Rule discipline

- **KHÔNG predict** ngày bệnh cụ thể trong 7 ngày
- **KHÔNG thay y học hiện đại** — Anh vẫn theo bác sĩ
- **Đức năng thắng số** — engine hỗ trợ, hành động vẫn của Anh
- **Đọc kỹ** — không lướt qua, mỗi sách extract 5-10 paradigm cốt

---

## ❓ Anh chỉ tiếp

3 lựa chọn:
1. **Duyệt plan như trên** → em theo 7 ngày
2. **Đổi thứ tự / scope** → Anh chỉnh
3. **Rút ngắn** → chọn 3-5 ngày quan trọng nhất

Em mặc định bắt đầu Ngày 1 (Lê Văn Sửu phần còn lại) khi Anh duyệt. Nếu Anh không chỉnh — em coi như duyệt và làm.
