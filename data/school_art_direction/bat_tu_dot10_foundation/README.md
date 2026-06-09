# Dot 10 - Bát Tự Foundation

Brief nguồn: `data/school_art_direction/REQUEST_DOT_10_BAT_TU_FOUNDATION_ART_BRIEF.md`

Mục tiêu: bộ ảnh riêng cho trang **Bát Tự & Hà Lạc Lý Số**, tách khỏi Kỳ Môn Dot 01 và Tử Vi oracle cards.

## Trạng thái

Đã nhận hàng Dot 10: 7/7 asset có source PNG và WebP web-ready.

## Danh sách asset

| ID | Loại | Vị trí UI | Trạng thái |
| --- | --- | --- | --- |
| `bat-tu-01-four-pillars-command-table` | hero 16:9 | đầu trang / sau khi luận | web_ready |
| `bat-tu-02-day-master-forge` | card 4:3 hoặc 1:1 | Nhật Chủ | web_ready |
| `bat-tu-03-five-elements-balance` | diagram 1:1 hoặc 4:3 | Ngũ Hành cân bằng | web_ready |
| `bat-tu-04-ten-gods-court` | card 4:3 | Thập Thần / Cách Cục | web_ready |
| `bat-tu-05-useful-god-remedy` | card 4:3 hoặc 3:2 | Dụng Thần / Bổ khí | web_ready |
| `bat-tu-06-da-van-river` | panoramic 21:9 hoặc 16:9 | Đại Vận timeline | web_ready |
| `bat-tu-07-ha-lac-two-hexagrams` | banner 16:9 | Hà Lạc Lý Số | web_ready |

## Thư mục

- `source/`: ảnh gốc PNG/JPG, cạnh dài tối thiểu 2200px.
- `web_ready/`: WebP tối ưu cho website/mobile.
- `prompts/`: prompt nguồn từng ảnh.
- `references/`: contact sheet hoặc ảnh duyệt nhanh.
- `manifest.json`: cập nhật sau khi nhận hàng.

## Quy tắc nhận hàng

- Giữ tên file đúng ID asset.
- Không đổi sang tên `final`, `v2`, `new`.
- Nếu thợ giao nhiều version, đặt hậu tố rõ: `bat-tu-01-four-pillars-command-table-alt-a.png`.
- Khi duyệt xong, bản dùng cho web phải có WebP nhẹ hơn 450KB với hero, nhẹ hơn 300KB với card.

## QA

- Contact sheet: `references/bat_tu_dot10_foundation_contact_sheet.jpg`
- `manifest.json` đã cập nhật đường dẫn source/web/prompt, kích thước và dung lượng.
- Tất cả WebP đang dưới ngưỡng dung lượng brief yêu cầu.
- QA mỹ thuật: pass. Bộ ảnh giữ đúng bản sắc Bát Tự, không lẫn Tử Vi oracle card hay Kỳ Môn Dot 01.
- `bat-tu-01` dùng tốt làm hero vì có vùng tối và bố cục bốn trụ rõ.
- `bat-tu-02`, `bat-tu-03`, `bat-tu-04`, `bat-tu-05` dùng tốt cho các section Nhật Chủ, Ngũ Hành, Thập Thần, Dụng Thần.
- `bat-tu-06` phù hợp làm nền Đại Vận timeline vì panoramic nhẹ, dễ crop mobile.
- `bat-tu-07` dùng riêng cho Hà Lạc; không dùng nó cho Bát Tự chính vì có ngôn ngữ quẻ/bát quái mạnh hơn các ảnh còn lại.
- Quy tắc UI: không phơi cả lô thành gallery. Ảnh nào chỉ hiện tại đúng section tương ứng sau khi user luận Bát Tự/Hà Lạc.
