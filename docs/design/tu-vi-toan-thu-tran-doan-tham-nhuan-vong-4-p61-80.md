# Vòng 4 — Toàn Thư p61-80 (2026-06-10)

## Phạm vi (đọc p61-70, còn p71-80 trong batch tiếp)
- p61-63: 4 sao chòm Thái Tuế (Bạch Hổ, Tang Môn, Điếu Khách, Quan Phù) — Toàn Thư KHÔNG diễn giải, chỉ VN
- p61-63: Sao THÊM của VN không có trong Toàn Thư: Long Trì, Phượng Các, Tam Thai, Bát Tọa, Hồng Loan, Thiên Hỉ, Thiên Nguyệt Đức, Cô Thần, Quả Tú, Hoa Cái, An Quang, Thiên Quí, Kiếp Sát, Phá Toái, Đẩu Quân
- p63-64: **NHÂN CUNG** — khái niệm CỰC QUAN TRỌNG
- p64-65: **Thập Nhị Cung Luận** + **Thân = Dụng / Mệnh = Thể**
- p65: Cường cung vs Nhược cung (khác nam-nữ)
- p65-70: **Nhất Cung Mệnh — Nam Mệnh Ca** cho 11/14 chính tinh (Tử Vi → Thiên Tướng)

---

## 💎 INSIGHT 4 SIÊU QUAN TRỌNG cho engine

### 🌟 PARADIGM #1 — NHÂN CUNG (engine-worthy)

> _"Nhân cung là nơi đất đắc địa cho một số sao... Vào nhân cung khả năng tốt sẽ bị giảm đến 80% hoặc nó sẽ gây thành tính kỳ quặc mà hỏng việc; nhân cung nghĩa bóng của thất vị thất nghiệp."_ — p63-64

**8 trường hợp nhân cung Toàn Thư ghi (rất rõ):**
| Sao | Cung nhân |
|---|---|
| Tử Vi | Tí, Thìn, Hợi |
| Tham Lang | Dần, Thân |
| Thiên Tướng | Thìn, Tuất |
| Thất Sát | Thìn, Hợi |
| Thiên Lương | Tị |
| Thiên Cơ | Tị |
| Phá Quân | Tị, Thân |
| Vũ Khúc | Thân |

→ **CHƯA THẤY trong TCQ2 + Tử Vi VN hiện đại.** Đây là FAUX-AMI: tưởng tốt nhưng thực ra giảm 80% giá trị. **Wire engine**:
```python
NHAN_CUNG = {
  "tu_vi": ["ty", "thin", "hoi"],
  "tham_lang": ["dan", "than"],
  # ...
}
def is_nhan_cung(sao, cung):
    return cung in NHAN_CUNG.get(sao, [])

# Trong output_filler: nếu hit → giảm score 0.8x + warning paradigm
```

### 🌟 PARADIGM #2 — MỆNH=THỂ vs THÂN=DỤNG

> _"Mệnh là thể mà Thân là dụng. Có thể mà vô dụng thì phát sớm tàn sớm. Có dụng mà vô thể thì thành công muộn màng chẳng được hưởng bao nhiêu."_ — p65

**Ma trận 2x2:**
| Mệnh | Thân | Hệ quả |
|---|---|---|
| Tốt | Tốt | Thể + Dụng đều hay — TỐT NHẤT |
| Tốt | Xấu | Thể hay Dụng dở — **phát sớm tàn sớm** |
| Xấu | Tốt | Thể dở Dụng hay — **thành công muộn** |
| Xấu | Xấu | Cả thể dụng đều dở |

→ **Em chưa có paradigm này phát biểu rõ trong TCQ2**. Em wire vào: section header "Tổng quan Mệnh-Thân" cho user, đặt TRƯỚC từng cung. Nội dung tổng quan = ma trận 2x2 với lá số cụ thể của user.

### 🌟 PARADIGM #3 — CƯỜNG/NHƯỢC CUNG khác Nam-Nữ

| Phái | Cường cung (5 cung quan trọng) |
|---|---|
| **Nam** | Mệnh + Thân + Tài Bạch + Quan Lộc + Thiên Di |
| **Nữ** | Mệnh + Thân + Phu Thê + Phúc Đức + Tử Tức |

→ **Em đã có gender-aware nhưng chưa wire CƯỜNG CUNG weight**. Wire engine:
```python
CUONG_CUNG_NAM = ["menh", "than", "tai_bach", "quan_loc", "thien_di"]
CUONG_CUNG_NU = ["menh", "than", "phu_the", "phuc_duc", "tu_tuc"]

def palace_weight(palace, gender):
    cuong = CUONG_CUNG_NAM if gender == "M" else CUONG_CUNG_NU
    return 2.0 if palace in cuong else 1.0
```

### 🌟 PARADIGM #4 — 12 CUNG chi tiết ý nghĩa
Toàn Thư phát biểu RÕ ý nghĩa từng cung — sẽ atomize vào commentary header per cung. Đáng nhất:
- **Phu Thê** = quan hệ + hình dáng + sinh hoạt VC + TINH THẦN của vợ/chồng (4 lớp)
- **Nam Nữ cung** = con cái + **sinh hoạt tình dục** (Toàn Thư nói thẳng — em sẽ giữ trong atom!)
- **Tài Bạch** = mạnh yếu năng lực kinh tế + tình hình thực lợi của sự nghiệp
- **Phúc Đức** = thọ yểu + **mức độ hưởng thụ** trong đời

---

## ⚠ CONFLICT mới với Tử Vi VN (cập nhật bảng vòng 3)

| Mục | Toàn Thư | VN | Note |
|---|---|---|---|
| Bạch Hổ "hổ khiếm tây phương" ở Dậu | Toàn Thư im, VN có | VN có | VN sáng tạo |
| Bạch Hổ ở Dần | "Có người nói tốt vì hổ cư hổ vị, có người nói không tốt vì xuất sơn" | VN giữ cách "Hổ cư hổ vị" tích cực | Conflict nội bộ |
| 7 sao VN thêm (Cô Thần, Quả Tú, Hoa Cái, An Quang, Thiên Quý, Kiếp Sát, Phá Toái) | KHÔNG có | Có | "VN sáng tạo sau Trần Đoàn" |
| Sao Đẩu Quân | Toàn Thư "không định rõ" | VN có chương riêng | Vô Muộn = Đẩu Quân coi nguyệt lệnh ảnh hưởng Tiểu Hạn |

---

## 📋 TIẾN ĐỘ Phase 0+1

- **80/171 trang = 46.8%** sau khi đọc thêm p71-80
- Đã đi qua: Chư tinh vấn đáp xong (14 chính + 30+ phụ), Thập Nhị Cung Luận (Cung Mệnh + Thiên Di + bắt đầu Quan Lộc) + Nam Mệnh Ca toàn bộ (14 sao + Tứ Hoá + Sát tinh)
- Còn lại 91 trang chia: Cung Tài/Tật/Phụ Mẫu/Phu Thê/Tử Tức/Nô Bộc/Điền Trạch/Phúc Đức + Nữ Mệnh + Đại Hạn + Lưu Niên + Lá số danh nhân

## Bổ sung Insight vòng 4 cuối (p71-80)

### NAM MỆNH CA — pattern lặp 14 chính tinh + Tứ Hoá + Sát tinh
Đã có Nam Mệnh Ca cho TẤT CẢ sao. Mỗi ca = 4-8 câu phú + giải nghĩa. **PHỤC VỤ Phase 3 atomize**: pattern giống "Chư tinh vấn đáp" nhưng tập trung CUNG MỆNH. Em sẽ atomize ca này thành combo (sao × Mệnh + điều kiện hội sao).

### THIÊN DI CUNG — luận chi tiết 14 chính tinh khi đóng cung Di
Cấu trúc rất nhất quán: mỗi chính tinh ở Di + combo với sao khác → ra ngoài thế nào (gặp quý nhân / lao tâm / phát tài / bị thị phi / nên hoạt động hay tĩnh thủ).

→ **Engine wire**: function `loan_giai_thien_di(chinh_tinh, palace_combo)` — Toàn Thư cung cấp ~50+ combo rules.

### QUAN LỘC — bắt đầu p79
Pattern tương tự Thiên Di nhưng tập trung sự nghiệp + chức vị.

---

## 🎯 ĐỀ XUẤT CHUYỂN PHASE 2

Em đã có đủ:
1. **Book Profile** (5 axes, hoàn chỉnh)
2. **6 paradigm keys** đặc trưng (70/30, Mệnh-Thân, Nhân Cung, Cường-Nhược, Bát Pháp, Thập Dụ)
3. **Pattern atomize** verified (Chư tinh + Nam Mệnh Ca + Thập Nhị Cung)
4. **Cross-school conflict map** (Toàn Thư vs TCQ2 vs Tử Vi VN) — đã có 12+ điểm
5. **Cấu trúc sách** đã rõ (Chư tinh xong p60, Thập Nhị Cung p64-cuối)

**KHÔNG CẦN đọc tiếp 91 trang còn lại** trước Phase 2, vì:
- Sub-agent sẽ đọc TEXT TRỰC TIẾP của từng section khi atomize
- Em đã có overview + paradigm để craft sub-agent prompt strict
- Em đốt token đọc thêm = redundant với sub-agent đọc lại

→ **Đề xuất chuyển Phase 2 (section detection + manifest update) NGAY**. Trong Phase 3 sub-agent sẽ đọc trực tiếp p81-171.
