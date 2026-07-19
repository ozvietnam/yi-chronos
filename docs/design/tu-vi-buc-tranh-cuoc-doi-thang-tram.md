# Cải tiến: "Bức tranh cuộc đời thăng trầm" — soi liên tục các tháng/năm

> Anh phát hiện 2026-07-18 (sau khi đọc tháng 7): *"em luận giải có soi cả mệnh chủ, đại vận, niên vận,
> rồi mới tới nguyệt vận, logic này rất hợp lý. Nếu soi liên tục các tháng, có lẽ sẽ vẽ được bức tranh
> cuộc đời anh thăng trầm ra sao."* → GHI để cải tiến engine.

## 1. Phát hiện cốt lõi (2 tầng)

**(a) LỒNG TẦNG đầy đủ = đọc đúng.** Thứ tự soil-before-seed (khớp [[tu_vi_doc_la_so_tien_trinh_phan_lop]]):
```
Mệnh chủ + Thân chủ + Cục (bẩm sinh, KHÔNG đổi)
  └─ Đại Vận (10 năm — chủ đề giai đoạn)
       └─ Lưu Niên (năm — can năm rọi Tứ Hóa)
            └─ Lưu Nguyệt (tháng — MỘT BƯỚC trong năm)
                 └─ Lưu Nhật (ngày — vi mô)
```
Mỗi tầng dưới đọc TRONG tầng trên (engine đã có `_bao_tram_dai_van`; cần thêm n/lồng Lưu Niên rõ hơn +
Mệnh chủ/Thân chủ/Cục lên đầu mỗi buổi đọc).

**(b) SOI LIÊN TỤC = ĐƯỜNG CONG.** Chạy Lưu Nguyệt (hoặc Lưu Niên) tuần tự qua thời gian →
mỗi mốc có một "cường độ + hướng khí" → nối lại thành **đường cong thăng trầm**.

## 2. ⚠️ LẰN RANH PARADIGM (Iron #9 — KHÔNG được vi phạm)

Đường cong này **KHÔNG phải đồ thị bói giàu-nghèo / năm nào phát năm nào lụn**. Đó là **tà mạng** (Brahmajāla).
Nó là **bản đồ KHÍ**: chỗ nào khí **DỒN** (nhiều tầng chồng), chỗ nào **QUAY** (Hóa Kỵ điểm quay), chỗ nào **XẢ**
(tự hóa), Mệnh vận đang ở cung **ĐỘNG** (Thiên Di/Quan/Tài) hay cung **TĨNH** (Tật Ách/Phúc Đức).
- "Thăng" = khí mở/động/tụ lực (nên HÀNH). "Trầm" = khí thu/tĩnh/quay (nên DƯỠNG-TU).
- **Cả hai đều KHÔNG phải cát/hung định sẵn** — chỉ là *nên làm gì cho hợp thời*. Trầm ≠ xui; trầm = mùa nghỉ.
- Mỗi mốc PHẢI kèm **đường hành** (DÙNG/TĨNH/CẨN) + disclaimer soi-tâm.

## 3. Kế hoạch engine (đề xuất — chưa build)

`engine/tu_vi/van_han.py::life_arc(person, tu_nam, den_nam, buoc="thang"|"nam")`:
- Lặp mốc → mỗi mốc gọi `van_han_luan(want_llm=False)`, rút **chỉ số cấu trúc TẤT ĐỊNH** (0 LLM):
  | Chỉ số | Từ đâu | Ý |
  |---|---|---|
  | `dong_tinh` | cung Mệnh vận (Thiên Di/Quan/Tài/Phu=ĐỘNG · Tật Ách/Phúc Đức/Phụ Mẫu=TĨNH) | thăng/trầm hướng |
  | `dong_luc` | #trùng phùng + có Song Lộc(+)/Song Kỵ(−) | cường độ |
  | `diem_quay` | có Hóa Kỵ chồng tầng | chỗ trời trở mình |
  | `cong_huong` | can tháng == can năm → Tứ Hóa khuếch đại | mốc đậm |
  | `xa` | tự hóa Lộc tại cung Mệnh vận | "có mà giữ không được" |
- Trả list mốc + 1 dòng "đọc" mỗi mốc → UI vẽ **strip đường cong** (thăng=trên, trầm=dưới), click 1 mốc → full luận.
- **Guard:** nhãn trục = "khí ĐỘNG ↔ khí TĨNH", TUYỆT ĐỐI không nhãn "tốt ↔ xấu / giàu ↔ nghèo".

## 4. Bằng chứng đường cong hoạt động (founder, thử tay 2 tháng)

| Mốc | Mệnh vận ở | Khí | Đọc 1 dòng |
|---|---|---|---|
| **T7/2026** (âm 6) | **Thiên Di** (ĐỘNG) + Thiên Di tự hóa Lộc | **THĂNG/động** | ra ngoài, dùng chuyên môn, DÙNG cơ hội đừng tích |
| **T8/2026** (âm 7) | **Tật Ách** (TĨNH) + Thái Dương hãm + **Song Kỵ Liêm Trinh @ Phúc Đức** (can tháng=can năm Bính, cộng hưởng) | **TRẦM/thu** | tháng DƯỠNG thân + TĨNH tâm, không khởi sự lớn |

→ Hai tháng liền kề đã cho một nhịp **động→tĩnh** rõ. Nối 120 tháng của 1 đại vận = thấy mạch thở của giai đoạn.

## 5. Việc cần làm
- [ ] Foreground Mệnh chủ/Thân chủ/Cục + Lưu Niên lên đầu mỗi buổi đọc (hiện mới lồng Đại Vận).
- [ ] `life_arc()` tất định + strip UI (guard paradigm ở #2).
- [ ] Neo mỗi mốc vào [[tu_vi_doc_van_han_goal]] + Iron #9.

*Liên hệ: [[tu-hoa-truy-nguyen-rule-551-than-co]] (điểm quay) · [[tu-hoa-truy-nguyen-rule-149-tu-hoa]] (tự hóa xả) · [[mo-hinh-hinh-thanh-con-nguoi]].*
