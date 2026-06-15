---
name: am-duong-ngu-hanh-nhiet-am
description: Lượng hóa ngũ hành thành tọa độ nhiệt-ẩm + hành Thổ cân bằng + tương ứng thân thể (ngũ âm/sắc/vị/giác quan) + đọc đồng dạng thị-thính giác. Citation Lê Văn Sửu Bảng 3-3, p90-96, Chương 4.
metadata:
  hermes:
    tags: [ngu_hanh, nhiet_am, hanh_tho, ngu_am, dong_dang]
    routing_mode: deep
    routing_keys: [nhiệt ẩm, tọa độ, hành thổ, cân bằng, ngũ âm, ngũ sắc, ngũ vị, tạng phủ, tượng hình, 6 thanh, đọc đồng dạng]
  source:
    book_title: "Học Thuyết Âm Dương Ngũ Hành"
    author: "Lê Văn Sửu"
    pages: "p90-96 (lượng hóa), Chương 4 (đồng dạng thị-thính giác)"
---

# Lượng hóa nhiệt-ẩm + hành Thổ + tương ứng thân thể + đọc đồng dạng

Engine số liệu: `engine/tu_vi/ngu_hanh_nen.NGU_HANH_NHIET_AM`, `HANH_THO_3_THE`, `NGU_HANH_THAN`.

## Tọa độ nhiệt-ẩm (đóng góp gốc Lê Văn Sửu, Bảng 3-3 p90)
Mỗi hành = một ĐIỂM trên mặt phẳng (% nhiệt = dương × % ẩm = âm):
- **Thủy** (Bắc, Hàn): nhiệt 0 / ẩm 50 — lạnh nhất
- **Hỏa** (Nam, Thử): nhiệt 100 / ẩm 50 — nóng nhất
- **Mộc** (Đông, Phong): nhiệt 50 / ẩm 100 — ẩm nhất
- **Kim** (Tây, Táo): nhiệt 50 / ẩm 0 — khô nhất
- **Thổ** (Trung ương, Thấp): nhiệt 50 / ẩm 50 — **CÂN BẰNG**

## Hành Thổ = điểm cân bằng (giải bí ẩn nghìn năm, p95-96)
Thổ = trạng thái khí TRUNG BÌNH, tổng nhiệt+ẩm luôn = 100%, 3 thế:
- Trung ương 50/50 = quân bình (thuần thổ)
- Tây nam 75/25 = dương thắng (âm trong dương thổ)
- Đông bắc 25/75 = âm thắng (dương trong âm thổ)
→ Thổ ở giao mùa (hè-thu), điểm tĩnh giữa các chuyển động. Khi luận hành Thổ vượng: nói "ổn định,
nuôi giữ, chuyển hóa, điều hòa" — không phán cứng.

## Tương ứng THÂN THỂ (nền y học cổ, Chương 4, dẫn Châm cứu đại thành)
| Hành | Tạng | Giác quan | Sắc | Vị | Ngũ âm | Tiếng |
|---|---|---|---|---|---|---|
| Mộc | Can (gan) | mắt | xanh | chua | Giốc | hô |
| Hỏa | Tâm (tim) | tay | đỏ | đắng | Chủy | cười |
| Thổ | Tỳ | lưỡi | vàng | ngọt | Cung | ca |
| Kim | Phế (phổi) | mũi | trắng | cay | Thương | khóc |
| Thủy | Thận | tai | đen | mặn | Vũ | rên |
→ Dùng khi luận cung Tật Ách / dong_y / màu hợp mệnh.

## Đọc đồng dạng THỊ-THÍNH GIÁC (Chương 4 — chân luận điểm Việt, attribution)
Một hành hiện diện đồng dạng xuyên: **6 thanh tiếng Việt = đường nét = chiều hướng = hình thể = độ
cao = ngũ âm** (Hỏa→Mộc→Thổ→Kim→Thủy = vui→giận→lo→buồn→sợ):
- Thanh: Sắc=Hỏa, Ngã=Mộc, Không dấu/Huyền=Thổ, Hỏi=Kim, Nặng=Thủy
- Hình: tròn=Hỏa, chữ nhật=Mộc, vuông=Thổ, tam giác=Kim, uốn khúc=Thủy
- Dáng người: mừng vui=Hỏa, hiên ngang=Mộc, bình thản/lo=Thổ, suy tính buồn=Kim, múa khéo=Thủy
→ Đây là bằng chứng paradigm "đọc đồng dạng" — quan-vật-trace-tính, KHÔNG predict. (Engine `do_hinh_co`
giữ trọn hệ trong payload `ngu_hanh_tao_hinh` + `sau_thanh_tieng_viet`.)

⚠ Luận điểm "ÂDNH của văn hóa Việt Nam" = position Lê Văn Sửu (attribution), không khẳng định như sự thật.
