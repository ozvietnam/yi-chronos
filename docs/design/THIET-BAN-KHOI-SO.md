# THIẾT BẢN — Phương Pháp 起数 (tính số từ ngày sinh)

> Keystone của Thiết Bản. Đọc từ bản 《邵康节说易·铁板神数》(Trung Châu Cổ Tịch),
> front matter Càn Tập (restored p0006–0013). Lập 2026-06-16.
> **Nguyên tắc: chỉ ship cái KIỂM được. Phần bí truyền/OCR mờ → ghi rõ, KHÔNG bịa số.**

---

## 0. Sách tự nói về phép (p0008, Càn Tập)

> *"Tiền hiền chư phu tử **mật truyền lý số**: từ **bát tự bản thân + cha mẹ**, phối **ngũ âm bát quái**; mỗi giờ phải suy **tám khắc**, mỗi khắc lại suy **mười lăm phân**. Suy đến đúng giờ, tự nhiên toàn số đều hợp, hoạ phước cát hung mảy may không sai."*

→ Phép gồm 2 nửa: **(A) 起数 — phối quái lấy số** từ bát tự; **(B) 考刻 — neo đúng khắc/phân** bằng bát tự cha mẹ + sự kiện đời thật. Chính 考刻 cho Thiết Bản "độ chính xác đóng đinh" — và cũng chính nó khiến phép **không thuần cơ học** (cần dữ kiện ngoài + dò lặp).

## 1. Phần KIỂM ĐƯỢC (nền số = Hà Đồ – Lạc Thư, đúng Chương 9)

**Địa chi → số ngũ hành (Hà Đồ)** — p0009, khớp Hà Đồ:
| Chi | Số | Hành |
|---|---|---|
| Hợi Tý | 1 · 6 | Thủy |
| Dần Mão | 3 · 8 | Mộc |
| Tỵ Ngọ | 2 · 7 | Hỏa |
| Thân Dậu | 4 · 9 | Kim |
| Thìn Tuất Sửu Mùi | 5 · 10 | Thổ (trung) |

**Địa chi → quái (số Lạc Thư / Hậu Thiên)** — p0008: 1 Khảm · 2 Khôn · 3 Chấn · 4 Tốn · 5 trung · 6 Càn · 7 Đoài · 8 Cấn · 9 Ly *(OCR bản này chép "7 Cấn 8 Đoài" — đảo so chuẩn; dùng CHUẨN Hậu Thiên, ghi rõ sai lệch OCR)*.

**Tứ hóa theo can năm** — p0011, **KIỂM CHÉO khớp bảng Đồ Năm** (`engine/tu_vi/do_nam_svg`): Giáp = Liêm-Phá-Vũ-Dương ✓ · Bính = Đồng-Cơ-Xương-Liêm ✓ → bảng tứ hóa của ta đúng.

## 2. Phần CHƯA KIỂM ĐƯỢC (không ship số)

- **Thiên can → quái** (p0008): OCR mâu thuẫn (Canh hiện 2 nơi: Khôn & Cấn). Không hardcode khi chưa chắc.
- **八卦加则 (Bát quái gia tắc)** — khẩu quyết ráp số (p0008): *"Hào từ ba mươi khởi, Càn sáu là đầu… **gặp mười ắt không dùng** (逢十不用)…"* = mnemonic cô đọng, KHÔNG đủ rõ để cơ học hóa ra số điều văn 1000–12989.
- **考刻** (B): cần **bát tự CHA MẸ + sự kiện đời thật** + dò 8 khắc × 15 phân → bản chất **lặp + có người tham gia**, không phải hàm thuần.
- **Thiếu cặp kiểm**: không có "bát tự X → số điều Y" đã biết (như 304-313 cho Hoàng Cực) để xác nhận engine. **Không validate được = không ship số.**

## 3. Phát hiện kèm: sách Thiết Bản CHỨA Tử Vi

Front matter (p0010–0012) là **bộ an-sao Tử Vi đầy đủ** (Văn Xương/Khúc, Tả/Hữu, Khôi/Việt, **Tứ Hóa**, Đại/Tiểu Hạn, 12 cung). Tức trong chính sách 《邵康节说易》, **Tử Vi đã nằm cạnh Thiết Bản** — củng cố: lồng Tử Vi vào hệ 邵 là **đúng truyền thống của chính bộ sách**, miễn ghi rõ gốc (Tử Vi = Trần Đoàn; xem Đồ Năm footer).

## 4. Trạng thái keystone & đường tới (PATH ③)

- ✅ **Recovered**: phép 起数 (cấu trúc) + nền số Hà Đồ-Lạc Thư + tứ hóa (kiểm chéo).
- ⏳ **Chờ để ship engine tính-số**: ① OCR LẠI sạch các Lệ Càn Tập (天干配卦, 八卦加则, 安身命) — bản hiện mờ/đảo; ② tìm **cặp kiểm** (1–2 lá số có sẵn dãy số điều văn) để validate; ③ rồi mới code `khoi_so` + bật trên web.
- ⛔ **Không làm**: ship engine "bát tự → số điều" khi chưa validate — đó là **bói giả-chính-xác**, phản đạo (Iron Rule #4/#6/#8). Thiết Bản mạnh ở 考刻 (người + sự kiện), không phải auto.

---

*Keystone "triển khai" tới mức TRUNG THỰC cho phép: phép đã hiểu + tài liệu hóa + phần kiểm-được đã chốt; engine tính-số chờ OCR sạch + cặp kiểm. Không bịa số đóng đinh lên đời người.*
