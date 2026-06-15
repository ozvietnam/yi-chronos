---
name: am-duong-ngu-hanh-index
description: Master index nền Âm Dương Ngũ Hành (Lê Văn Sửu) — tầng CƠ CHẾ dưới mọi luận giải Tử Vi/Bát Tự. Load khi cần grounding sinh-khắc-chế-hóa, tọa độ nhiệt-ẩm, thể-dụng, đọc đồng dạng.
metadata:
  hermes:
    tags: [am_duong_ngu_hanh, ngu_hanh, Index, AlwaysAvailable]
    routing_mode: short
    routing_keys: [ngũ hành, âm dương, sinh khắc, chế hóa, tương sinh, tương khắc, nhiệt ẩm, hành thổ, thể dụng, nạp âm, tràng sinh, ngũ âm, ngũ sắc, đọc đồng dạng, không định mệnh]
  source:
    book_corpus_id: hoc-thuyet-am-duong-ngu-hanh
    book_title: "Học Thuyết Âm Dương Ngũ Hành"
    author: "Lê Văn Sửu"
    tier: 3
    journals: "docs/design/am-duong-ngu-hanh-vong-1..13-*.md"
    wiki_atoms: 109
  curated_at: 2026-06-13 (sau khi thâm nhuần trọn 13 vòng / 251 trang)
---

# Âm Dương Ngũ Hành — Master Index (nền cơ chế cho luận giải)

Đây là **tầng nền** dưới mọi luận sao↔cung, can↔chi, sinh↔khắc. KHÔNG phải để predict —
là để giải thích CƠ CHẾ năng lượng theo paradigm "đọc đồng dạng" (Iron Rule #4/#6/#8).

Cấu trúc 3-tier:
- **Tier 1 (file này)** — 5 paradigm cốt + bảng định tuyến. Luôn load khi cần grounding ngũ hành.
- **Tier 2** `sinh-khac-che-hoa.md` (đủ 4 quy luật + thể-dụng) · `nhiet-am-the-dung.md` (lượng hóa + hành Thổ + đồng dạng thị-thính giác).
- **Engine** (số liệu chính xác): `engine/tu_vi/ngu_hanh_nen.py` (quan_he, che_hoa, sao_tai_cung, vong_sinh_khac) + `engine/tu_vi/do_hinh_co.py` (10 đồ hình payload).

## 🎯 5 paradigm cốt (luôn nhớ khi luận)

1. **Ngũ hành = 5 KIỂU/GIAI ĐOẠN vận động** (Mộc sinh trưởng · Hỏa bùng nổ · Thổ chuyển hóa ·
   Kim thu lại · Thủy lưu chuyển) — KHÔNG phải 5 chất liệu. Tên gỗ-lửa-đất-kim-nước chỉ là cách đặt.
2. **Lượng hóa = tọa độ nhiệt-ẩm**: mỗi hành một điểm trên mặt phẳng (% nhiệt = dương × % ẩm = âm).
   Hành **Thổ = điểm CÂN BẰNG** (50-50, tổng luôn 100%) → giải bí ẩn vị trí Thổ. → `nhiet-am-the-dung.md`.
3. **Đủ 4 quy luật**: sinh · khắc · **CHẾ** (con kẻ bị khắc phản công cứu mẹ) · **HÓA** (thông quan,
   biến khắc thành sinh). Thiếu chế-hóa = hệ mất cân bằng. → `sinh-khac-che-hoa.md`.
4. **THỂ-DỤNG trong tinh mệnh** (Thần bí dịch tinh tượng): ngã/mệnh cung = THỂ, sao đến = DỤNG.
   "Dụng sinh thể thì tốt, thể sinh dụng thì không tốt (tổn thể)". LƯU Ý: bảng miếu-hãm cổ xét SỨC
   SAO, thể-dụng xét LỢI CHO NGƯỜI — hai góc nhìn có thể lệch, giữ cả hai (KHÔNG ép khớp).
5. **ĐỌC ĐỒNG DẠNG, KHÔNG ĐỊNH MỆNH**: ngũ hành là quy luật TỰ NHIÊN, không phải công cụ định mệnh/
   chính trị. Một hành hiện diện đồng dạng xuyên mùa/khí/can/chi/màu/hình/thanh — luận theo đồng dạng,
   KHÔNG phán cát-hung cứng (gốc trực tiếp của Iron Rule #4/#6/#8).

## 📋 Map intent → route

| Intent khi luận giải | Route đến |
|---|---|
| Sao khắc/sinh cung quá tay, "cứu" được không | `sinh-khac-che-hoa.md` (chế = con bị-khắc phản công; hóa = thông quan) |
| Sao↔cung tốt/xấu cho NGƯỜI (không chỉ sức sao) | Tier-1 §4 thể-dụng + engine `sao_tai_cung()` (ghi_chu_lech) |
| Hành mạnh/yếu, cân bằng nhiệt-ẩm | `nhiet-am-the-dung.md` (tọa độ + hành Thổ 3 thế) |
| Nạp âm / mệnh cục ngũ hành của tuổi | engine `bat_tu/compatibility.NAP_AM_MAP` + Tier-1 (thuật toán bát quái + biệt lệ thiên phù) |
| Vòng Tràng Sinh / sinh-vượng-mộ | engine `tu_vi/paradigm/trang_sinh.py` (nền: Dần-Thân-Tỵ-Hợi=Sinh, Tý-Ngọ-Mão-Dậu=Vượng, Thìn-Tuất-Sửu-Mùi=Mộ) |
| Màu/âm/vị/giác quan ↔ tạng phủ (dong_y, tật ách) | `nhiet-am-the-dung.md` §ngũ-âm-sắc-vị + engine `ngu_hanh_nen.NGU_HANH_THAN` |
| Giờ sinh ↔ tạng phủ vượng (nhịp thời sinh học) | engine `do_hinh_co.THAP_NHI_KINH` (Tý-Đảm... Sửu-Can = 2h sáng viêm gan) |
| User hỏi "số tôi thế nào" (predict) | ❌ KHÔNG predict — §5: chuyển sang "cấu trúc này VẬN HÀNH tốt nhất khi..." (mệnh là động từ, Iron Rule #8) |

## ⚠ Khi dùng cho user
- Ngũ hành = giải CƠ CHẾ, KHÔNG phán định mệnh. "Mệnh là động từ" (Iron Rule #8): nói "cấu trúc
  này vận hành thế nào", không nói "số anh là...".
- Luận điểm Lê Văn Sửu "ÂDNH là của văn hóa Việt Nam" = **attribution** (position tác giả, cần đối
  chiếu) — KHÔNG phát ngôn như sự thật lịch sử.
- Số liệu chính xác (tọa độ, cặp chế-hóa, bảng tra) → gọi engine, đừng nhớ áng chừng.
