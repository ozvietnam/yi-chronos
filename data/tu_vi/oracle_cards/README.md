# Tử Vi Oracle Cards Workshop

Thư mục này là nơi tập trung dữ liệu, prompt, ảnh gốc và ảnh web-ready cho các bộ thẻ Tử Vi trong dự án Yi.

## Cấu trúc hiện tại

- `TUVI_ORACLE_CARD_WIKI.md`: wiki chính cho bộ **Tử Vi Bắc Phái / 14 Chính Tinh / phụ tinh / tổ hợp / tọa cung**.
- `chieu_dom_kinh_18_phi_tinh/`: bộ riêng cho **Chiếu Đởm Kinh / 18 Phi Tinh**.
- `docx_rework/`: workflow render thẻ vào tài liệu/PDF.
- `make_star_guardian_cards.py`: script tạo card guardian dạng cũ.
- `add_guardian_cards_to_docx.py`: script gắn card vào tài liệu.

## Quy tắc phân luồng

1. **Tử Vi Bắc Phái** để trong `TUVI_ORACLE_CARD_WIKI.md`.
   - Gồm 14 chính tinh, phụ tinh, sát tinh, Tứ Hóa, tọa cung, đại vận, lưu niên.
   - Mỹ thuật thiên về nhân vật/archetype.

2. **Chiếu Đởm Kinh / 18 Phi Tinh** để riêng trong `chieu_dom_kinh_18_phi_tinh/`.
   - Không gộp vào wiki 14 chính tinh.
   - Mỹ thuật thiên về pháp tượng/ký hiệu sống/phi tinh.
   - Nguồn vận hành: `data/tu_vi/chieu_dom_kinh_18_phi_tinh.json` và `data/tu_vi/nhap_cot_tien_kinh_tong_doan.json`.

3. **Ảnh gốc chất lượng cao** đặt trong nhánh `generated_cards/` của đúng bộ.

4. **Ảnh tối ưu website/mobile** đặt trong `web_ready/` của đúng bộ.

5. **Prompt đặt vẽ** đặt trong `prompts/`.

6. **Không dùng tên chung chung** như `v2`, `new`, `final`.
   - Dùng ID hệ thống: `cdk_phi_14_hu`, `tuvi_thuan_thien_luong`, `tuvi_toa_cung_thien_luong_thien_di_hoi`.

## Ghi chú

Những file trong `docx_rework/rendered*` là output render tài liệu, không phải nguồn quản lý thẻ. Khi cần đưa lên website, copy/convert sang nhánh `web_ready/` tương ứng.

