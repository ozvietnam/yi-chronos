# Vòng 1 — Tử Vi Nghiệm Lý Toàn Thư (Cụ Thiên Lương) p2-11

**Sách**: `tu-vi-nghiem-ly-toan-thu-thien-luong` (372 trang)
**Tác giả**: **Lê Quang Khải (cụ Thiên Lương)** — 1910-1985, Hưng Yên → Thủ Dầu Một → Sài Gòn
**Hệ phái**: **VN cải cách 1972-1974** (`thien_luong_dao_duc_hoc`)

---

## 🎯 PHẦN I — TÔNG-CHỈ (cực mạnh Iron Rule #6)

> **"Tử Vi là một ĐẠO LÝ của thánh nhân xưa, một môn GIÁO DỤC ĐẠO ĐỨC của kẻ sĩ, tự biết mình, biết người để chung hòa dễ dàng và thích hợp với đời sống cá nhân và cộng đồng xã hội."** — p2

> **"Cụ đã đưa khoa này thành một KHOA TÂM LÝ HỌC."** — p2

> **"Khoa Tử Vi không phải là một khoa huyền bí mà là một khoa có bố cục tinh vi, linh hoạt, KHÔNG tà thuật, mê hoặc."** — p2

> Cụ căn dặn con cháu: **"đừng bao giờ dùng Tử Vi để kiếm tiền hoặc làm 'cần câu cơm'."** — p4-5

→ **Đây là SÁCH match Iron Rule #6 100% — mạnh hơn cả Trần Đoàn**. Vũ Tài Lục nói "Tử Vi không huyền bí"; Thiên Lương đi XA HƠN: "Tử Vi = ĐẠO ĐỨC HỌC + TÂM LÝ HỌC".

---

## 🌟 PHẦN II — 5 PARADIGM KEYS đặc trưng (KHÔNG có ở Trần Đoàn / TCQ2)

### Paradigm #1: 5 BẬC TUỔI CAN-CHI (p7-10)

Theo luật Ngũ Hành Can-Chi sinh khắc, tuổi mỗi cá nhân chia 5 bậc:

| Bậc | Quan hệ | Ý nghĩa | Ví dụ |
|---|---|---|---|
| **1** | Can sinh Chi | **PHÚC ĐỨC QUÁ LỚN — căn bản hơn người** | Giáp Ngọ (Mộc→Hỏa) |
| **2** | Can = Chi | Năng lực khá đầy đủ vững chắc | Giáp Dần (Mộc=Mộc) |
| **3** | Chi sinh Can | Đời gặp may NHIỀU HƠN THỰC LỰC | Giáp Tý (Thủy→Mộc) |
| **4** | Can khắc Chi | Đời gặp nhiều trở lực | Giáp Thìn (Mộc→Thổ) |
| **5** | Chi khắc Can | **NGHỊCH CẢNH ĐẦY RẪY CHUA CAY** | Giáp Thân (Kim→Mộc) |

> _"Can là gốc là Phúc đức, Chi là ngọn là Thân thế."_ — p11

→ **Engine wire**: function `bac_tuoi(can, chi)` returns 1-5. Wire vào commentary header trước khi luận lá số (Trần Đoàn / Trung Châu KHÔNG có cấu trúc này).

### Paradigm #2: 3 VÒNG LỚN — Lộc Tồn / Thái Tuế / Tràng Sinh (p7)

> _"sự hên xui đã ấn định như thế đó, còn tùy định mệnh phác họa hạnh phúc (**vòng Lộc Tồn**) tùy vị trí an Mệnh Thân (**vòng Thái Tuế** bổ khuyết tứ thế), nhất là Thân (chính đương số với **vòng Tràng Sinh**)..."_

- **Vòng Lộc Tồn** = HẠNH PHÚC (tài lộc, hưởng thụ)
- **Vòng Thái Tuế** = BỔ KHUYẾT TỨ THẾ (vị trí xã hội, chính nghĩa)
- **Vòng Tràng Sinh** = CHÍNH ĐƯƠNG SỐ (Thân, năng lực thực tế)

→ **3 vòng giải lá số** = paradigm gọn nhất em từng thấy. Wire làm view chính trong UI.

### Paradigm #3: TAM HỢP TUỔI HƯỞNG LỘC TỒN (p9)

> _"Tuổi Giáp Ngọ còn tiềm tàng căn bản phồn thịnh là tam hợp Lộc Tồn của tuổi Giáp (Lộc Tồn ở Dần) — Thiên Lộc dành riêng cho người Dần, Ngọ, Tuất."_

→ **Engine wire**: cho mỗi can → tam hợp tuổi nào hưởng Lộc Tồn của can đó:
```python
LOC_TON_TAM_HOP = {
  "Giáp": ["Dần", "Ngọ", "Tuất"],   # Lộc Tồn ở Dần
  "Canh": ["Thân", "Tý", "Thìn"],   # Lộc Tồn ở Thân
  # ... 10 can
}
```

### Paradigm #4: THẾ THÁI CỰC vũ trụ (p11)

> _"Bản địa bàn tử vi thấy cả một thế thái cực vững vàng cân phân... từ Mão đến Thân thuộc **Thái Dương**, từ Dậu đến Dần thuộc **Thái Âm** như hai đĩa cân ngang bằng sánh đôi."_

- 6 cung Mão-Thìn-Tỵ-Ngọ-Mùi-Thân = THÁI DƯƠNG (sáng lạng)
- 6 cung Dậu-Tuất-Hợi-Tý-Sửu-Dần = THÁI ÂM (tối)

→ Khái niệm "đĩa cân âm-dương" — em chưa thấy ở sách khác.

### Paradigm #5: CASE STUDY Trương Lương vs Hàn Tín (p10-11)

Cụ Thiên Lương dùng 2 nhân vật lịch sử CÙNG TUỔI GIÁP, cùng đắc Tử Phủ Sát Phá Tham + tam hợp Thái Tuế, NHƯNG cuộc đời khác hẳn vì:

| Mục | Trương Lương | Hàn Tín |
|---|---|---|
| Năm sinh | **Giáp Ngọ** (Can sinh Chi → phúc lớn) | **Giáp Tuất** (Can khắc Chi → trở lực) |
| Mệnh ở | Quan Phù — tính toán kỹ càng | Bạch Hổ — bất chấp, tham vọng |
| Phúc Đức | Tham Lang ngộ Tuần — hòa hợp, từ bỏ tham vọng | Thất Sát triều đầu ngộ Tuần+Triệt — bị thương |
| Kết cục | Nhàn du sơn thủy | Bị giết |

→ **Đây là MẪU LUẬN CHUẨN của Cụ Thiên Lương**: SO SÁNH 2 lá số cùng cấu trúc nhưng khác Can-Chi-vị trí.

---

## 📐 PHẦN III — BOOK PROFILE draft

```yaml
book_corpus_id: tu-vi-nghiem-ly-toan-thu-thien-luong
title: Tử Vi Nghiệm Lý Toàn Thư
author: Cụ Thiên Lương (Lê Quang Khải, 1910-1985)
school: thien_luong_dao_duc_hoc
total_pages: 372

book_profile:
  core_def: |
    Tử Vi = ĐẠO LÝ + GIÁO DỤC ĐẠO ĐỨC + TÂM LÝ HỌC.
    Tự biết mình, biết người để chung hòa với đời sống.
    KHÔNG huyền bí, KHÔNG tà thuật, KHÔNG dùng để kiếm tiền.
    Cốt yếu: 5 bậc tuổi Can-Chi + 3 vòng (Lộc Tồn / Thái Tuế / Tràng Sinh).
  paradigm_keys:
    - "Tử Vi = đạo đức học + tâm lý học" (p2, mạnh hơn Trần Đoàn về Iron Rule #6)
    - "5 BẬC TUỔI CAN-CHI" (p7-10) — chưa có ở sách khác
    - "3 VÒNG LỚN: Lộc Tồn/Thái Tuế/Tràng Sinh" (p7)
    - "TAM HỢP TUỔI hưởng Lộc Tồn" (p9)
    - "THẾ THÁI CỰC: Mão-Thân Dương, Dậu-Dần Âm" (p11)
    - "Can = Phúc đức, Chi = Thân thế" (p11)
    - "Mẫu luận so sánh 2 lá số cùng cấu trúc" (Trương Lương vs Hàn Tín)
  
  conflict_with_tcq2_and_toan_thu: |
    - Thiên Lương ĐI XA HƠN trong Iron Rule #6 — KHÔNG dùng Tử Vi kiếm tiền
    - Thiên Lương có 5 bậc tuổi Can-Chi (chưa có ở 2 sách khác)
    - Thiên Lương có 3 vòng lớn paradigm (Trần Đoàn/TCQ2 không phân ra)
    - Thiên Lương dùng pattern so sánh 2 lá số (Trần Đoàn dùng phú đoán độc lập)
    
  unique_concepts:
    - "Nhân quả luân hồi" (preface mention p2)
    - "Tài thọ" (2 chữ đặc trưng)
    - "Đào hồng" — cách cục
    - "Tam hóa liên châu"
    - "Oan trái nghiệp quả hình điếu không kiếp"
    - "Vòng Tràng Sinh" (cốt lõi)
```

---

## 🎯 ĐỊNH HƯỚNG vòng 2-?

Em dự đoán cấu trúc sách Thiên Lương sẽ KHÁC Trần Đoàn:
- p2-50: Paradigm nền (đã đọc p2-11)
- p51-150: Sao + Cung luận theo paradigm Thiên Lương
- p151-300: Cách cục đặc thù + Đại Hạn + Lưu Niên
- p301-372: Nhân quả + Tài thọ + Lá số case study

Em đọc tiếp vòng 2 (p12-30) để verify cấu trúc + paradigm sau đó chuyển Phase 2 (manifest).
