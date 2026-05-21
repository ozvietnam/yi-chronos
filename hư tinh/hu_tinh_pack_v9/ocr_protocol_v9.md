# OCR Protocol v9 — Quy trình xử lý S5

## 1. Tệp mục tiêu

S5: 13866643.pdf — 曹展硕《紫微斗数》, bản scan ảnh 150 trang.

## 2. Nguyên tắc kỹ thuật

- OCR chọn lọc, không OCR toàn bộ nếu không cần.
- Ưu tiên trang mục lục và trang chứa sao hư tinh.
- Mỗi kết quả OCR phải được kiểm lại bằng ảnh gốc nếu chữ quan trọng.

## 3. Schema lưu kết quả OCR

| file | page | term | raw_ocr | corrected_text | vietnamese_translation | confidence | notes |
|---|---|---|---|---|---|---|---|

## 4. Quy tắc chất lượng

- confidence thấp: không dùng làm kết luận.
- chữ Hán nghi ngờ: đánh dấu [?].
- nếu OCR sai giữa 天空 và 天哭, phải đối chiếu ảnh.
- mọi đoạn đưa vào paper phải có bản dịch và ghi chú nguồn.

## 5. Gói V10 sau OCR

Dự kiến tạo:
- s5_ocr_excerpts_v10.csv
- s5_terms_by_page_v10.csv
- s1_s5_comparison_v10.md
- chapter5_extension_from_s5_v10.md
