# 🪙 Hệ phái 04 — BỐC PHỆ / BỐC DỊCH

> Chiêm bốc qua **đồng tiền** + **Nạp Giáp** + **Lục Thân** + **Lục Thần**.
> Khởi nguồn: phái Văn Vương → Kinh Phòng (đời Hán).
> 4 cuốn · ~8.5 MB.

## 📚 Danh sách

### boc-phe-chinh-tong (Bốc Phệ Chính Tông)
- **KINH ĐIỂN** Bốc Phệ — sách cốt phái Văn Vương
- Cổ điển TQ, bản dịch VN

### tang-san-boc-dich (Tăng San Bốc Dịch)
- **KINH ĐIỂN** Bốc Phệ — Vương Hồng Tự bình chú
- Bản tăng san (bổ sung) cổ điển

### khong-minh-than-toan-384-que (Khổng Minh Thần Toán)
- 384 quẻ tiên tri thần toán
- Truyền thuyết liên hệ Khổng Minh — quân sự / chiến lược

### don-toan-than-dieu (Đôn Toán Thần Diệu)
- Bridge giữa Bốc Phệ + Mai Hoa
- Phương pháp đôn toán nhanh

## 🎯 Khác biệt Bốc Phệ vs Mai Hoa

| | Bốc Phệ | Mai Hoa Dịch |
|---|---|---|
| Cách lập quẻ | 6 đồng xu × 6 lần | Số / thời / vật |
| Trọng tâm | Nạp Giáp + Lục Thân + Thế Ứng + Dụng Thần | Thể-Dụng + Hỗ Biến + Ngũ Hành |
| Phái khởi | Văn Vương → Kinh Phòng | Thiệu Khang Tiết (đời Tống) |
| Ứng dụng | Cụ thể: tài/quan/hôn/bệnh | Vật / sự kiện / quan sát |

## 🔗 Engine

Hiện chưa wire Bốc Phệ riêng vào engine. Future:
- `engine/boc_phe/cast.py` (cast quẻ từ random / input)
- Lục Thân: Phụ Mẫu, Huynh Đệ, Tử Tôn, Thê Tài, Quan Quỷ
- Lục Thần: Thanh Long, Chu Tước, Câu Trận, Đằng Xà, Bạch Hổ, Huyền Vũ

## ⚠ Note

Bốc Phệ rất phổ biến TQ + VN nhưng paradigm khắc nghiệt (predict cụ thể):
- Cát/Hung rõ ràng (khác Tử Vi paradigm "đọc đồng dạng")
- Engine nếu wire cần dùng Iron Rule #6 nhuyễn → KHÔNG output cát/hung tuyệt đối
