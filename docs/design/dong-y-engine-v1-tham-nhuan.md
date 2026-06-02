# Đông Y Engine v1 — Thâm Nhuần "Chữa bệnh theo Chu Dịch"

**Ngày:** 2026-06-03
**Tuyên ngôn:** Anh chỉ "đọc Hoàng Đế Nội Kinh + xây engine như các trường phái em đã làm rất tốt"
**Tình trạng corpus:** KHÔNG có Hoàng Đế Nội Kinh trong thư viện. Em dùng sách thay thế **"Chữa bệnh theo Chu Dịch"** (Lý Ngọc Sơn + Lý Kiện Dân) — sách Đông y bằng tiếng Việt đã restore (11461 dòng), paradigm Dịch + Y học cổ.

---

## I. Paradigm CỐT phát hiện trong sách

> _"Bát quái tượng số liệu pháp trong quan hệ lấy **BÁT QUÁI VI THỂ, NGŨ HÀNH VI DỤNG** — chính là thể hiện nguyên lý vĩnh hằng của vũ trụ."_
> — Lý Ngọc Sơn + Lý Kiện Dân, chương I

### 8 quẻ Bát Quái ↔ Tạng phủ (verified từ sách dòng 314-565)

| Quẻ | Hiệu | Số TT | Hành | Tạng | Cơ thể | Gia tộc |
|---|---|---|---|---|---|---|
| Càn | ☰ | 1 | kim | Đại trường | Đầu | Cha |
| Đoài | ☱ | 2 | kim | Phế | Miệng | Thiếu nữ |
| Ly | ☲ | 3 | hỏa | Tâm + Tâm bào | Mắt | Trung nữ |
| **Chấn** | ☳ | **4** | **mộc** | **Can (Gan)** | **Chân + gân** | Trưởng nam |
| Tốn | ☴ | 5 | mộc | Đởm (Mật) | Đùi | Trưởng nữ |
| Khảm | ☵ | 6 | thủy | Thận | Tai | Trung nam |
| Cấn | ☶ | 7 | thổ | Vị | Tay | Thiếu nam |
| Khôn | ☷ | 8 | thổ | Tỳ | Bụng | Mẹ |

🎯 **Founder match đúng:** Đứt gân đầu gối = **Chấn (số 4, mộc, Can, chân + gân)** — biểu hiện CỐT.

---

## II. Liệu pháp Tượng Số (paradigm độc đáo từ sách)

Đọc nhẩm dãy số tượng quẻ → cộng hưởng với tạng phủ. 7 công thức verified:

| Tượng số | Ý nghĩa | Trích sách (dòng) |
|---|---|---|
| **640** hoặc 40 | Bổ máu Can, dưỡng gân cốt | 2426 |
| 650.3820 | Bổ thận dương + kiện tỳ | 2546 |
| 260.50 | Bổ thận nạp khí (hô hấp ngắn) | 2569 |
| 430.20 | Thông Can khí an thần (stress) | 2404 |
| 20.650 | Phấn chấn thận dương (đau lưng + lạnh) | 2521 |
| 3820 | Kiện tỳ ích khí | 2547 |
| 003 | Trị Can hỏa làm mắt đỏ | 2450 |

🎯 **Founder cụ thể:** Tượng số **640** = 6 (Khảm/Thận) + 4 (Chấn/Can) + 0 (âm) → bổ Can-Thận đồng nguồn, dưỡng gân cốt. ĐÚNG TỪ SÁCH cho đứt gân + chân yếu.

---

## III. 4 Module engine đã build (~1000 dòng)

| Module | Function | Cho founder |
|---|---|---|
| `tang_phu_chan_doan` | Bát Quái ↔ Tạng phủ chẩn đoán từ chấn thương | Chấn → Can/gân (primary) + Càn → Đại trường (đầu gối) |
| `kinh_lac_overview` | 12 kinh chính + giờ vượng | Can: 1h-3h Sửu, cặp Đởm 23h-1h Tý |
| `am_duong_can_bang` | Đánh giá âm dương + nhiệt hàn từ lá số | 2/6 (thiên dương), GÂN-XƯƠNG = nguyên âm hư |
| `lieu_phap_tuong_so` | Sinh dãy số chữa bệnh paradigm cổ | **640** = bổ Can-Thận cho gân |

---

## IV. Cross paradigm

| TTT chương 17-19 (Bát Tự) | Chữa bệnh theo Chu Dịch | Hoàng Đế Nội Kinh |
|---|---|---|
| Mộc Day Master nhược | Quẻ Chấn yếu → Can hư | Mộc → Can chủ gân |
| Nguyên Lưu tắc Kim | Chu trình ngũ hành đứt | Khí huyết không thông |
| Ấn Thủy yếu | Khảm yếu → Thận hư | Thủy → Thận chủ cốt |

→ **3 paradigm hội tụ 1 chẩn đoán cho founder**: Can-Thận đồng nguồn hư → cần TƯ ÂM (bổ Mộc + Thủy).

---

## V. Iron Rule trong engine Đông y

🪷 4 module đều giữ Iron Rule #4+6:
- KHÔNG predict "anh sẽ bị bệnh X năm Y"
- KHÔNG thay thế y học hiện đại (cần đi khám bác sĩ)
- Liệu pháp tượng số = công cụ THIỀN ĐỊNH, không phải thuốc
- Đức năng thắng số — hành động vẫn của Anh

---

## VI. Roadmap mở rộng (Anh chỉ thì làm)

1. **Đọc Hoàng Đế Nội Kinh** khi Anh có PDF (em build engine v2 đầy đủ hơn — Vận khí, Tạng tượng, Kinh mạch chi tiết)
2. **OCR lại Lê Văn Sửu** (Âm Dương Ngũ Hành) — hiện CID encoding hỏng
3. Mở rộng `lieu_phap_tuong_so` — đọc tiếp chương II sách (có thêm case study)
4. Cross paradigm Mai Hoa: dùng quẻ cast được hôm nay → đoán giờ cần chú ý tạng nào
