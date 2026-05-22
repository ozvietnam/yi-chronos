# Chiếu Đởm Kinh 18 Phi Tinh Oracle Cards

Thư mục này quản lý riêng bộ ảnh **Chiếu Đởm Kinh / 18 Phi Tinh**.

Không trộn bộ này với `TUVI_ORACLE_CARD_WIKI.md` của hệ **Tử Vi Bắc Phái / 14 Chính Tinh**. Hai hệ có nguồn, quy tắc an sao và ngôn ngữ mỹ thuật khác nhau.

## Vai trò thư mục

- `CHIEU_DOM_KINH_18_PHI_TINH_ART_DIRECTION.md`: chuẩn mỹ thuật, giải thích cho thợ vẽ để không lẫn với 14 chính tinh.
- `18_PHI_TINH_CARD_MANIFEST.md`: danh sách 18 thẻ cần vẽ, thứ tự, tên file, trạng thái.
- `prompts/`: prompt đặt vẽ từng thẻ.
- `source_assets/`: ảnh tham chiếu, crop sách, sketch, bản nháp nguồn.
- `generated_cards/`: ảnh gốc chất lượng cao sau khi vẽ/generate.
- `web_ready/`: ảnh đã tối ưu cho website/mobile.
- `references/`: ghi chú nguồn, đối chiếu, OCR, hoặc tài liệu phụ cho bộ này.

## Quy ước đặt tên file

Ảnh gốc:

```text
cdk_phi_XX_slug__hanzi__polarity_element.png
```

Ví dụ:

```text
cdk_phi_14_hu__xu__am_thuy.png
cdk_phi_18_khoc__ku__am_kim.png
```

Prompt:

```text
prompts/cdk_phi_XX_slug.prompt.md
```

Ảnh web-ready:

```text
web_ready/cdk_phi_XX_slug.webp
```

## Luồng làm việc

1. Chọn thẻ từ `18_PHI_TINH_CARD_MANIFEST.md`.
2. Viết prompt vào `prompts/`.
3. Đưa ảnh gốc vào `generated_cards/`.
4. Tối ưu ảnh cho web/mobile vào `web_ready/`.
5. Cập nhật trạng thái trong manifest.
6. Khi đủ bộ hoặc đủ nhóm ưu tiên, mới gắn vào UI.

## Nguyên tắc nguồn

- Dữ liệu gốc lấy từ `data/tu_vi/chieu_dom_kinh_18_phi_tinh.json`.
- Tổng đoán/hỷ cung lấy từ `data/tu_vi/nhap_cot_tien_kinh_tong_doan.json`.
- Gói `hư tinh/hu_tinh_pack_v9` chỉ là manifest kiểm soát nguồn; S5 đang pending OCR, không ghi là trích dẫn chắc chắn.

