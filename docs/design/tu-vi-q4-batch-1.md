# Q4 Phase A — Batch 1 (p0199-p0208)

**Range**: 10 trang OCR · **Total text VI**: 319 ký tự · **Lines**: 12
**Read date**: 2026-05-20 (CEO gate G1)
**Method**: Full OCR dump + MinerU content_list inspect + visual PDF inspect

---

## 🚨 R8 (từ Q4-MASTER-PLAN) — CONFIRMED

**Em đã sai. Original ledger title "Lá Số Cổ Kim 60+ case studies" THỰC SỰ ĐÚNG.**

MinerU `tuvidauso-zh_content_list.json` ghi rõ **12 images/tables** trong band p199-p208 (page_idx 198-206), chủ yếu `type=table`. Em đã visual inspect 1 image (`7270a850...170a.jpg`) — đây là **lá số Tử Vi 12-cung** cho **2 nhân vật cổ điển**:

- **孔尼仲命** = Khổng Tử (Trọng Ni) — sinh 庚戌年十一月初一子时 (Canh Tuất, tháng 11 mùng 1, giờ Tý) — 阳男, 土五局
- **子路之命** = Tử Lộ (học trò Khổng Tử) — sinh 癸丑年九月初九寅时 (Quý Sửu, tháng 9 mùng 9, giờ Dần) — 阴男, 木二局

→ Đây là **case studies thật**, không phải "Khang Tiết commentary headers".

---

## 1. Pages covered + content density

| Page | Region files | Lines | Chars VI | Note |
|------|-------------|-------|----------|------|
| p0199 | r001, r002 | 2 | 62 | Header "Tân toa Hy Di Trần tiên sinh" + "quyển chi tứ" — KHỞI Q4 |
| p0200 | (none) | 0 | 0 | **DIAGRAM PAGE** — MinerU detect table image |
| p0201 | r001 | 1 | 31 | Header "Khang Tiết thuyết Dịch toàn thư" (KHÔNG có content body) |
| p0202 | (none) | 0 | 0 | **DIAGRAM PAGE** — MinerU detect table image |
| p0203 | r001, r003 | 3 | 77 | 3 header lines: "Khang Tiết toàn thư" + "Tử Vi Đẩu Số" + "Khang Tiết Kim thư cửu" |
| p0204 | (none) | 0 | 0 | **DIAGRAM PAGE** — MinerU detect table image |
| p0205 | (none) | 0 | 0 | **DIAGRAM PAGE** — MinerU detect table image |
| p0206 | r001 | 1 | 34 | Header "Khang Tiết thuyết Dịch kim thư cửu" |
| p0207 | r002 | 5 | 115 | 5 headers lặp (Tử Vi Đẩu Số + Tương tiết + Khang Tiết Kim thư x2 + Tử Vi Đẩu Số) |
| p0208 | (none) | 0 | 0 | **DIAGRAM PAGE** |

→ **5/10 pages = ZERO text** (diagram pages). 5 pages có text = chỉ headers, KHÔNG commentary body.

---

## 2. Section headers detected (verbatim)

Em quote NGUYÊN VĂN (không paraphrase):

- **p0199 r001-l001**: _"Tân toa Hy Di Trần tiên sinh"_
- **p0199 r002-l001**: _"Tử Vi Đẩu Số toàn thư quyển chi tứ"_
- **p0201 r001-l001**: _"Khang Tiết thuyết Dịch toàn thư"_
- **p0203 r001-l001**: _"Khang Tiết thuyết Dịch toàn thư"_
- **p0203 r003-l001**: _"Tử Vi Đẩu Số"_
- **p0203 r003-l002**: _"Khang Tiết thuyết Dịch kim thư cửu"_
- **p0206 r001-l001**: _"Khang Tiết thuyết Dịch kim thư cửu"_
- **p0207 r002-l001**: _"Tử Vi Đẩu Số"_
- **p0207 r002-l002**: _"Tương tiết thuyết xương kim thư"_
- **p0207 r002-l003**: _"Khang Tiết thuyết Dịch kim thư"_
- **p0207 r002-l004**: _"Tử Vi Đẩu Số"_
- **p0207 r002-l005**: _"Tương tiết thuyết Dịch kim thư"_

→ **9/12 lines = "Khang Tiết..." hoặc "Tử Vi Đẩu Số" hoặc "Tương tiết..." — đều là HEADERS LẶP**. Không có 1 dòng content body nào.

---

## 3. Key paradigm/structural insights

1. **Q4 mở đầu = "quyển chi tứ"** (quyển 4) của Hi Di Trần tiên sinh — p0199 r002-l001 ✓
2. **Pattern Q4 band p0199-p0208**: header trang chẵn? hay alternating diagram + header? Cần verify thêm batch sau
3. **MinerU đã detect 12 image/table objects** trong band này — visual inspect 1 image đã confirm = lá số chart 12-cung của 2 nhân vật lịch sử (Khổng Tử + Tử Lộ)
4. **"Khang Tiết thuyết Dịch kim thư"** lặp lại = title/template header trên CHART pages, KHÔNG phải distinct Khang Tiết commentary

---

## 4. Structured data candidates

| Candidate | Source | Confidence |
|-----------|--------|-----------|
| Lá số Khổng Tử + Tử Lộ (chart_image=7270a850...) | p0199-p0202 area | HIGH (1 chart visually verified) |
| ~6-10 more chart images trong batch này | p0203-p0208 | HIGH (MinerU detect) |

→ **Em chưa biết** tên 6-10 nhân vật còn lại trong batch này. Cần visual inspect các images còn lại (kế hoạch sau khi batch 2-10 đọc xong text).

---

## 5. Engine implications (suggestion only — chưa build)

- **NEW: Build `data/tu_vi/q4_case_charts.json`** với schema `{name_vi, name_zh, era, birth_zh_text, gender, ngu_cuc, chart_image_path, 12_cung_summary}` — populate sau khi visual inspect tất cả 60 lá số
- **NEW: Build vision-based extractor** cho 12-cung chart images (vision LLM hoặc OCR cell-by-cell)
- **REVERT: LEDGER Q4 title** từ "Khang Tiết Bổ Chú + Phê Mệnh" về "Lá Số Cổ Kim 60+ case studies + Phê Mệnh Templates"

---

## 6. Direct quote citations

Tất cả quote ở Section 2 đều cite verbatim từ filepath:
`data/yi_publishing/translations/tuvidauso-zh/p0{NNN}/r{NNN}.json` line `r{NNN}-l001`.

Image visually inspected: `data/yi_publishing_mineru/tuvidauso-zh/auto/images/7270a850a708b1fb3cea2ee55c0d7b62e34252b3c1fad91ec2c6b1d615cc170a.jpg`.

MinerU manifest: `data/yi_publishing_mineru/tuvidauso-zh/auto/tuvidauso-zh_content_list.json`.

---

## 7. Reconciliation note vs `tu-vi-tham-nhuan-quyen-4.md`

| Claim trong journal hiện tại | Status post-Batch 1 |
|------------------------------|--------------------|
| "Q4 102 trang Khang Tiết Edition" | ❌ **RETRACT** — band p0199-p0208 có ~5 trang text + 5 trang diagram, headers lặp KHÔNG phải Khang Tiết commentary |
| "Khang Tiết hiện diện 30+ lần Q4" | ❌ **RETRACT** — em đếm header LẶP làm refs. Trong batch 1 thì "Khang Tiết..." xuất hiện 6 lần nhưng tất cả là **header/title repeated**, không phải nội dung commentary |
| "Phần 1 Khang Tiết Kim thư p0199-p0256 = 30+ sections" | ❌ **RETRACT** — band này = chart figures (lá số mẫu) + header pages, không phải commentary sections |
| "Q4 không phải 60+ case studies" (em viết khi rename ledger) | ❌ **RETRACT** — visually confirmed Khổng Tử + Tử Lộ charts đã có ngay batch 1. Original ledger title đúng. |

---

## 8. CEO decision needed (Gate G1)

1. **CEO duyệt batch 1 report** → tiếp Batch 2 (p0209-p0218)?
2. **REVERT LEDGER Q4 title** ngay (rollback Task #17 SAI) hay đợi sau VERIFY phase?
3. **Freeze tasks #17, #18, #19** (case_studies feature based on wrong thesis) cho đến khi Q4 case database rebuild xong?
