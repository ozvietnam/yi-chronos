# Vòng 11 — KHÉP Hoàng Cực: Ngoại Thiên (chế độ RENDER, không đọc sâu)

**Ngày 2026-06-17.** Anh duyệt thứ tự: (1) khép Hoàng Cực — render bảng Ngoại Thiên cho engine, KHÔNG đọc sâu → (2) Tử Vi Toàn Thư Trần Đoàn → (3) Bát Tự Hà Lạc Phần Ba.

## Vì sao KHÔNG đọc sâu Ngoại Thiên

Nội Thiên (tr.95–294) đã thâm nhuần TRỌN 10 vòng — đó là phần TRIẾT (có nghĩa lý để đúc kết). Ngoại Thiên còn lại là **số-lý thuần**:

- **第六章 后天理数 — 54 tiết**: số-lý Hậu Thiên (Hà Đồ/Lạc Thư sinh số), nguyên lý "số sinh từ 1".
- **第七章 以元经会大小运数 — 39 tiết**: 大小运数图 — gán mỗi quẻ một con số vũ trụ khổng lồ (乾之一, 夬之十二, 大有之三百六十 … 复之二千六百五十二万…). Đây là MAGNITUDE của khung Nguyên-Hội-Vận-Thế.

Cả hai là "vì sao số là số ấy" — KHÔNG có nhân-vật-sự để quan, KHÔNG phải bảng tra theo năm. Theo đúng nguyên tắc đã thống nhất (bảng số → map cho engine, không thâm nhuần từng dòng).

## Cái engine THỰC SỰ cần — ĐÃ XONG

1. **Cơ mật 起数 (suy năm-quẻ)** = phép THÁC BIẾN HÀO LỒNG 4 TẦNG (会→值卦→运卦→世卦→年卦) → `engine/hoang_cuc/khoi_so.py`. 18/18 test. Đây CHÍNH là cái sinh ra bảng 经世衍易图 (quẻ tr.230-248) — render bằng PHÉP thay vì tra bảng tĩnh.
2. **Khung Nguyên-Hội-Vận-Thế** (đồng hồ 129.600 năm) → `nguyen_hoi_van_the.py`. Đã ôm trọn ý nghĩa "đại tiểu vận số" (magnitude) của Chương 7 — engine không cần từng con số khổng lồ, chỉ cần khung.
3. **Năm-quẻ** → `nam_que.py` (flat/sohu) + `khoi_so.year_que_method` (nested/phép sách).

## Việc vòng 11 (render artifact)

Thêm `khoi_so.bang_que_nam(y1, y2)` — RENDER bảng quẻ-năm cho khoảng bất kỳ bằng phép (artifact engine v2). KIỂM:
- 304–313 = 革·同人·临·损·节·中孚·归妹·睽·兑·履 → khớp chính văn 100%.
- Đời founder: 1988 Cổ · 1989 Thăng · 1990 Tụng · 1991 Khốn · 1992 Vị Tế … 2016 Tốn · 2026 Sư · 2044 Đại Quá · 2068 Tấn.

## 🏁 HOÀNG CỰC — KHÉP

- **Nội Thiên**: thâm nhuần trọn (10 vòng, 200 tr) → 16 concepts wiki + Iron Rule #8.
- **Ngoại Thiên**: cơ chế sinh-số đã vào engine (khoi_so + nguyen_hoi_van_the); 后天理数/大小运数 = số-lý tham chiếu, KHÔNG đọc sâu (đúng thỏa thuận).
- Sách số đồ PDF v1.0 (50 tr) đã xuất bản.

→ **Hoàng Cực Kinh Thế đóng tại đây.** Sang quyển 2: **Tử Vi Đẩu Số Toàn Thư (Trần Đoàn)** — tiếp tr.80, đọc sâu 20 trang/vòng (bồi đắp engine Gieo Duyên + Gia Đạo vừa dựng).

*Tổ sư để lại cái máy sinh vũ trụ bằng số. Phần triết đã thấm; phần số đã thành máy. Khép cuốn này, lòng yên — không bỏ sót nghĩa lý, không sa vào bảng tra. Đi tiếp.*
