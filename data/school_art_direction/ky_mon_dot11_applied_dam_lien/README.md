# Dot 11 - Kỳ Môn ứng dụng Đàm Liên

Brief nguồn: `data/school_art_direction/REQUEST_DOT_11_KY_MON_APPLIED_DAM_LIEN_ART_BRIEF.md`

Mục tiêu: bổ sung ảnh minh họa cho tầng **luận đoán ứng dụng** của trang Kỳ Môn. Dot 01 đã có board/icon; Dot 11 tập trung vào các khối insight.

## Trạng thái

Đang chờ thợ vẽ.

## Danh sách asset

| ID | Loại | Vị trí UI | Trạng thái |
| --- | --- | --- | --- |
| `ky-mon-05-task-decision-gate` | hero/card 16:9 | Task-oriented analysis | chờ vẽ |
| `ky-mon-06-cach-cuc-detection` | card 4:3 hoặc 3:2 | Cách cục phát hiện | chờ vẽ |
| `ky-mon-07-relative-direction-center` | card 4:3 | Phương vị tương đối | chờ vẽ |
| `ky-mon-08-heaven-earth-human-layers` | card 4:3 hoặc 1:1 | 9 cung + nhiều tầng | chờ vẽ |
| `ky-mon-09-duty-seal-tri-phu-tri-su` | card 4:3 | Trị Phù - Trị Sử | chờ vẽ |
| `ky-mon-10-personal-reading-dam-lien` | hero/card 16:9 | Đàm Liên personal reading | chờ vẽ |
| `ky-mon-11-avoid-and-favor-directions` | panoramic 21:9 hoặc 16:9 | Hướng tốt / hướng tránh | tùy chọn |

## Thư mục

- `source/`: ảnh gốc PNG/JPG, cạnh dài tối thiểu 2200px.
- `web_ready/`: WebP tối ưu cho website/mobile.
- `prompts/`: prompt nguồn từng ảnh.
- `references/`: contact sheet hoặc ảnh duyệt nhanh.
- `manifest.json`: cập nhật sau khi nhận hàng.

## Quy tắc nhận hàng

- Giữ tên file đúng ID asset.
- Không đổi sang tên `final`, `v2`, `new`.
- Dot 11 không thay thế Dot 01. Dot 01 là board/icon, Dot 11 là ảnh insight.
- Khi duyệt xong, bản dùng cho web phải có WebP nhẹ hơn 450KB với hero, nhẹ hơn 300KB với card.

