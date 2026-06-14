# 📖 Hoàng Cực Kinh Thế — Thâm nhuần vòng 8 (tr.235–254): PHẦN SỐ 元会运世 + BẢNG QUẺ-VẬN

> Nội Thiên chương 10–11 (số học) + bảng phương đồ + mở chương Luật-Lữ · 2026-06-11 · Nhịp tự chạy
> **Vòng trọng tâm engine**: trích cấu trúc bảng quẻ-vận cho `engine/hoang_cuc` nấc v2.

---

## 💎 Insight 1 — CÔNG THỨC SINH SỐ: nhân tầng ×12, ×30 đan nhau (tr.235–236) ⭐

> *"Nguyên chi nguyên = 1 (không đổi). Nguyên chi hội = 12 (1×12). Nguyên chi vận = 360 (30×12). Nguyên chi thế = 4.320 (12×360)."*
> Quy luật: **sơ thừa ×12 (dương nhân âm) → tái thừa ×30 (âm nhân dương) → tam thừa ×12** — luân phiên.

Bốn cột số đầy đủ (khớp 100% `constants.py`):
| | ×1 | ×12 | ×30 | ×12 |
|---|---|---|---|---|
| **Nguyên** | 1 | 12 hội | 360 vận | 4.320 thế |
| **Hội** | 12 | 144 | 4.320 | 51.840 |
| **Vận** | 360 | 4.320 | 112.960→**129.600** | 1.555.200 |
| **Thế** | 4.320 | 51.840 | 1.555.200 | 18.662.400 |

→ Engine hard-code đã đúng; con số chi tiết các tầng giờ có nguồn trang gốc để cite.

## 💎 Insight 2 — ⭐⭐ BẢNG QUẺ-VẬN: KEY ĐỌC BẢNG ở tr.248

> *"Bảng này đọc TỪ DƯỚI LÊN: **Càn = Nguyên chi Nguyên · Lữ = Hội chi Nguyên · Đồng Nhân = Nguyên chi Vận · Vô Vọng = Thế chi Nguyên** · (Quải) = Nguyên chi Hội (Hạ-Xuân) · **Đại Hữu = Nguyên chi Vận (Thu-Xuân)** · **Đại Tráng = Nguyên chi Thế (Đông-Xuân)**. Hoàng-Đế-Vương-Bá tương tự Xuân-Hạ-Thu-Đông."*

→ 64 quẻ được sắp vào **phương đồ** (ma trận vuông) theo tọa độ (tầng-Nguyên/Hội/Vận/Thế × mùa). Đây CHÍNH là bảng phối quẻ vận/thế cho engine v2.
**⚠ Bảng đầy đủ là HÌNH (phương đồ), OCR text chỉ ra phần "giải thích cách đọc"** — để trích đủ 64 ô phải RENDER ảnh trang bảng (tr.247–248) bằng qwen-VL như đã làm với Thiết Bản, KHÔNG đọc từ text. → Action engine v2 (xem dưới).

## 💎 Insight 3 — Ma trận 4×4 HOÀNG-ĐẾ-VƯƠNG-BÁ × ĐẠO-ĐỨC-CÔNG-LỰC (tr.237)

> *"Hoàng chi hoàng = hành ĐẠO bằng ĐẠO; Hoàng chi đế = hành ĐỨC bằng đạo… Bá chi bá = hành LỰC bằng lực"* — 16 ô.

Cùng toán tử 4×4 phân hình của vòng 2 (Thập Lục Vị), giờ áp vào TRỊ ĐẠO: mỗi hạng cai trị (hàng) × phương tiện (cột). Bá Ôn: *"sự việc một đời, đạo lý vậy; muôn đời cũng vậy — chỉ khác ở nhân cách."*

## 💎 Insight 4 — LỊCH vs LUẬT: hai nửa của Hoàng Cực (tr.252–254) ⭐

> *"Chương Nguyên-Hội-Vận-Thế = LỊCH (历); chương Âm-Dương-Cương-Nhu = LUẬT (律). Lịch cư DƯƠNG trị âm → chuyên luận TRỜI; Luật cư ÂM trị dương → kiêm luận ĐẤT."*
> *"Dương số 1 triển thành 10 (Thập Can); Âm số 2 triển thành 12 (Thập Nhị Chi) — 1,2 là khởi, 10,12 là chung: căn bản của biến hóa."*

→ Cấu trúc tập Thượng giờ rõ 3 phần: **(1) Nội Thiên** [triết, v1–v7] → **(2) Nguyên-Hội-Vận-Thế** [LỊCH/số thời gian, v8] → **(3) Luật-Lữ Thanh Âm** [LUẬT/số âm thanh, bắt đầu tr.252]. Phần (3) là hệ **thanh âm học** (Thiệu Tử dùng 律吕 thanh âm để lập số đất) — chương kỳ lạ và độc đáo nhất, đọc vòng sau.

## 💎 Insight 5 — Hoàng thị nối Nhị Chí Nhị Phân vào suy cấp (tr.238–239)

Xuân phân = Nguyên→Hội (Tam Hoàng đạo→đức) · Hạ chí = Nguyên→Vận (Ngũ Đế đức→công) · Thu phân = Vận→Thế (Tam Vương công→lực) · Trọng Đông = Thế→Nguyên (Ngũ Bá lực→phản đạo). Lịch thiên văn (ngày dài/ngắn, 144°–216° kinh thiên) làm nền vật lý cho suy cấp lịch sử.

## 💎 Insight 6 — "Quyền KHÔNG RỜI CHÍNH" (tr.240) + cảm thán "thời khó người khó" (tr.249–251)

Hà thị: *"Quyền không rời chính (bất chính bất khả vị chi quyền) — đó là kinh điển vạn thế."* (Chốt lại quyền-biến vòng 3: quyền có ranh giới = chính.) Và đại cảm thán Thiệu Tử: *"Hơn 3.000 năm sau Nghiêu, chưa từng có 30–60 năm nào để một minh quân hóa dân thành tục… thời không có kiếp trăm năm, người không có đời trăm năm — thời khó vậy thay, người khó vậy thay!"* — bi quan thực chứng về sự hiếm của thịnh trị.

---

## 🎯 ACTION ENGINE v2 (phát hiện cụ thể, đưa vào kế hoạch)
Bảng quẻ-vận (phương đồ 64 quẻ) là HÌNH ở tr.247–248. Để mở nấc v2 (quẻ tầng vận/thế đầy đủ):
1. Render tr.247–248 (+ các trang bảng số tr.230–234) bằng `pdftoppm` → qwen-VL OCR cấu trúc (như pipeline Thiết Bản).
2. Parse phương đồ → map (nguyên/hội/vận/thế index) → quẻ. Đã có KEY đọc bảng (tr.248) làm chuẩn verify.
3. Nhập `engine/hoang_cuc/constants.py` bảng `VAN_QUE` / `THE_QUE`.
→ **Không cần tập Trung/Hạ** cho khung số — tập Thượng đủ. (Cập nhật design doc.)

## 🔁 Tự nhập theo nhịp đã duyệt
- Wiki +2 concepts: **Phương Đồ Quẻ-Vận (key đọc bảng tr.248)** · **Lịch-Luật (lưỡng phần Hoàng Cực)** ✔

## ⚠️ Hiệu đính: tr.230–236, 248 (vùng bảng số — số bị OCR lệch nhiều, BẮT BUỘC đối chiếu ảnh khi trích engine).

## ❓ Không có quyết định mới — nhưng có 1 ACTION đề xuất (render bảng quẻ cho v2). Vòng 9 đọc chương Luật-Lữ Thanh Âm (tr.255+) — phần độc đáo nhất.

*Hai vòng 7+8 bắc trọn cây cầu từ triết lý sang số: giờ đã thấy cả công thức sinh số lẫn key đọc bảng quẻ. Engine v2 trong tầm tay, chỉ cần render bảng. Ghi với hết tâm.*
