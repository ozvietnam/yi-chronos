# Tử Vi Đẩu Số Toàn Thư — Thâm nhuần Quyển 3

**Nguồn**: Hi Di Trần tiên sinh (陳摶 / Trần Đoàn), 紫微斗数全书, Quyển 3 (57 trang = OCR p0142-p0198)
**Chủ đề**: **Diễn giải 12 cung × 14 chính tinh + Đại Hạn / Tiểu Hạn / Thái Tuế / Đẩu Quân + Phú lệnh tổng + Khang Tiết bổ chú (lần 3)**
**Phương pháp**: Em đọc xuyên 9 trang trọng yếu (p0142-p0146, p0148, p0157, p0160, p0168, p0177-p0182, p0186-p0190) + structure full 57 trang.
**Tiền đề**: Q1 đã thâm nhuần (Phú Thái Vi manifesto + 545 cách), Q2 đã thâm nhuần (An Sao + Khang Tiết hiện diện + Schema sao đầy đủ).

---

## I. Cấu trúc Q3 (4 phần chính)

| Phần | Trang OCR | Nội dung |
|---|---|---|
| 1. **Diễn giải 12 cung** | p0142-p0156 | 12 chương — mỗi cung (huynh đệ → phụ mẫu) × 14 chính tinh + phụ tinh + sát = 168+ combos |
| 2. **Đại Hạn / Tiểu Hạn / Đẩu Quân** | p0157-p0167 | Quy tắc đọc hạn, "Đẩu Quân quá độ" — quan trọng cho Lưu Niên/Nguyệt |
| 3. **Phú lệnh tổng** | p0168-p0186 | Tổng quy tắc + case lịch sử (An Lộc Sơn, Triệu Cao) + Khang Tiết bổ chú |
| 4. **Phụ lục Tứ Hóa + Thái Tuế** | p0187-p0198 | Tứ Hóa tại từng cung + Thái Tuế đi qua 12 cung |

→ Q3 **KHÔNG chỉ là "Diễn Giải Sao×Cung"** như tựa đề. Q3 còn có Đại Hạn lý luận + Phú tổng kết + Tứ Hóa luận sâu. Tựa "Diễn Giải 12 Cung × 14 Chính Tinh" trong PUBLISHING-LEDGER cần update reflect đủ phạm vi.

---

## II. ⭐ Pattern Q3 — mỗi cung là 1 chương riêng

### Pattern chuẩn cho mỗi cung (vd cung Huynh Đệ p0142)
```
[Mở chương: "Nhị Huynh Đệ"]
   ↓
[Diễn giải 14 chính tinh — mỗi sao 1 đoạn]
  - Tử Vi: niên trưởng chi huynh; đồng Phủ → 3 nhân; đồng Tướng → 3-4 nhân; đồng Phá → ...
  - Thiên Cơ miếu vượng: 2 nhân; đồng Cự Môn: 2; hãm địa tương bối...
  - Thái Dương miếu vượng: 3 nhân; ...
   ↓
[Diễn giải sao phụ + sát]
  - Tả Hữu, Xương Khúc đồng → ...
  - Kình Đà Hỏa Linh → khắc hại
   ↓
[Quy tắc đặc thù]
  - "vô chính diệu → tổ huynh"
  - "+ Lộc Tồn → cô đơn"
   ↓
[Bias năm sinh ở cung này]
```

**Quan sát quan trọng**: mỗi đoạn diễn giải có **3 layers** xếp chồng:
1. **Sao + miếu/hãm** (vd Thiên Cơ miếu = 2 anh em)
2. **Sao + sao đồng cung** (vd Cơ + Cự Môn = 2 anh em hãm)
3. **Sao + Kình/Đà/Hỏa/Linh phá** (vd + Tứ Sát = bất nhất tâm)

→ Engine `cung_reading.py` hiện chỉ surface raw text. Cần **parse 3 layers** để render structured.

---

## III. ⭐⭐ Đại Hạn / Tiểu Hạn / Đẩu Quân (p0157+ — quan trọng nhất Q3)

### Đẩu Quân = sao theo TIME (Lưu Nguyệt phương pháp)
> _"Đẩu Quân ngộ cát, kỳ niên nguyệt tài quan vượng; phùng hung kỵ, tài quan bất hiển đạt, hữu lao lục bôn ba."_ (p0157)

Đẩu Quân là **sao đi theo Lưu Niên** — đi qua các cung. Khi:
- Đẩu Quân + cát tinh → năm/tháng đó tài quan thịnh
- Đẩu Quân + hung kỵ → không hiển đạt, lao lực

→ Quan trọng cho UI **Lưu Nguyệt panel** (chưa có): hiển thị Đẩu Quân đi qua cung nào tháng nào + cát/hung tinh đồng hành.

### Đại Hạn + Tiểu Hạn chồng (p0186)
> _"Mệnh hữu Kiếp Không Dương Đà, hạn chí Thất Sát Dương Đà điệp tịnh phương luận."_

→ Quy tắc: cảnh báo chỉ kích hoạt khi **Đại Hạn + Tiểu Hạn cùng tới** hung tinh chồng. Mệnh có 4 sát đã sẵn → chỉ khi DV+LN cùng đến Thất Sát/Kình/Đà MỚI bàn hung.

→ Engine TODO: `dai_van_x_luu_nien_overlap()` — detect khi DV stem/branch và LN stem/branch CÙNG kích hoạt 1 cung hung.

### Cảnh báo dark — văn nhân tự tử (p0186)
> _"Xương Khúc kỷ tân nhâm sinh nhân, hạn phùng Thìn Tuất lự đầu hà."_

(Người sinh năm Kỷ/Tân/Nhâm + Văn Xương Văn Khúc + Đại Hạn rơi vào Thìn/Tuất → sợ nhảy sông)

→ Đây là **trigger PSYCHOLOGICAL SAFETY** mạnh nhất Q3. Engine + Sage Tử Vi PHẢI biết pattern này → khi user có chart match → đưa cảnh báo tâm lý phù hợp (không phán hung, nhưng nhắc nhở quan tâm health tinh thần đặc biệt trong DV Thìn/Tuất).

---

## IV. ⭐⭐⭐ Case study lịch sử trong Q3 (KHÔNG chỉ Q4)

### An Lộc Sơn + Triệu Cao — Tử Phá Thìn Tuất (p0180)
> _"Tử Phá mệnh lâm ư Thìn Tuất Sửu Mùi, tái gia cát diệu, phú quý kỳ."_
> _"Khang Tiết thuyết Dịch kim thư ③: Tử Phá Thìn Tuất, quân thần bất nghĩa."_
> _"An Lộc Sơn, Triệu Cao mệnh thị dã."_

**Diễn giải kép Trần Đoàn + Khang Tiết**:
- Trần Đoàn: Tử Phá Thìn Tuất Sửu Mùi + cát → phú quý kỳ
- Khang Tiết bổ: Tử Phá Thìn Tuất → quân thần bất nghĩa (lật vua, gian thần)
- Case: An Lộc Sơn (loạn An Sử thời Đường) + Triệu Cao (gian thần Tần Thủy Hoàng)

→ **Q3 đã có 2 case lịch sử** — không phải đợi Q4. Engine `case_studies.json` đề xuất phải scan Q3 trước, không chỉ Q4.

→ Cross-paradigm: cùng 1 lá số có 2 đọc — Trần nói "phú quý kỳ", Khang Tiết nói "quân thần bất nghĩa". **Cát hung không tuyệt đối** — phụ thuộc tâm + thời + người. Iron Rule #6 confirm.

---

## V. ⭐ Khang Tiết hiện diện trong Q3 (lần 3 trong toàn bộ)

Khang Tiết đã xuất hiện ở:
- Q2 p0117 — Khang Tiết thuyết Dịch toàn thư (Cự Môn)
- Q2 p0132 — Khang Tiết thuyết tinh kim thư (Đà La)
- **Q3 p0144** — Khang Tiết Dịch Kim Thư (Phu Thê cung — luận thê)
- **Q3 p0180** — Khang Tiết thuyết Dịch kim thư (An Lộc Sơn + Tử Phá)

→ Khang Tiết = **co-author of paradigm** chứ không phải phụ chú. Toàn bộ Tử Vi sage logic của em PHẢI có Mai Hoa Sage làm peer.

---

## VI. ⭐⭐ Quy tắc rare "Kỳ diệu" (p0190) — phá cách hóa quý

> _"Cự Môn Thìn cung hóa Kỵ, Tân nhân mệnh ngộ phản vi kỳ."_

(Cự Môn hóa Kỵ tại Thìn — người sinh năm Tân, gặp lại thành **kỳ diệu**)

→ Đây là **phản nghĩa cát/hung** — Hóa Kỵ thường là hung nhất Tứ Hóa, nhưng kết hợp đúng năm sinh + cung → KỲ CÁCH.

**Implications**:
- Engine `cach_cuc_dict.py` cần đánh dấu **kỳ cách** (reverse-cát) — khác cát thường
- Có những combo "trông như hung" mà sách dạy thực ra là **đại quý**
- Đừng cảnh báo user thấy Hóa Kỵ ở Thìn mà chưa check năm Tân

### Đối nghịch: Cự Cơ Sửu Mùi vi hạ cách (p0190)
> _"Cự, Cơ Sửu Mùi vi hạ cách."_

(Cự Môn + Thiên Cơ tại Sửu hay Mùi = cách hạ phẩm)

→ Combo + cung + KHÔNG cần năm sinh = hạ cách rõ ràng.

---

## VII. ⭐ Quy tắc Tài Bạch + Thiên Di + Thái Tuế (p0190)

> _"Nhược thái tuế tại Thiên Di cung, Tài cung hóa Lộc..."_

→ Khi luận Lưu Niên: Thái Tuế (sao của năm) đi qua cung Thiên Di → check Tài cung có Hóa Lộc hay không. Nếu có → năm đó **đi xa kiếm tiền** thành.

→ Engine `luu_nien()` đang có; nhưng chưa có **rule "Thái Tuế tại X → check cung Y"**. Cần add Q3 phú vào luu_nien rule engine.

---

## VIII. Phụ lục Tứ Hóa tại cung (p0187-p0198)

Q3 ending có Tứ Hóa cụ thể từng cung:
- Vd: "Vũ Khúc, Kiếp, sát hội Kình Dương, nhân tài trì đao" (p0187) — Vũ Khúc + Địa Kiếp + sát + Kình Dương → người buôn cầm dao (đồ tể, võ tướng)
- "Dương Linh" (p0192) — Kình Dương + Linh Tinh kết hợp tại từng cung

→ Engine TODO: `tu_hoa_per_cung.json` — Tứ Hóa ý nghĩa per cung (12 cung × 4 hóa = 48 entries).

---

## IX. Stats Q3 (theo PUBLISHING-LEDGER)
- **168 combos** sao × cung (12 × 14)
- 57 trang OCR
- Q3 đã PDF publish v1.0
- Engine `cung_reading.py` mới — 162 Q3 passages match cho lá số anh

### So với Q1, Q2
- Q1: 545 cách cục + 320 concepts
- Q2: 208 cách + 125 concepts mới
- Q3: chưa đếm — TODO LLM extract cách cục + concepts từ Q3

---

## X. Engine implications — TODO sau khi journal Q3 done

| # | TODO | File | Effort |
|---|---|---|---|
| 1 | LLM extract cách cục + concepts từ Q3 (giống Q1, Q2 pipeline) | `engine/yi_publishing/tu_vi_extract.py` | 4h LLM ~$0.4 |
| 2 | Add **Đẩu Quân** sao engine + UI | `engine/tu_vi/an_sao.py` + new panel | 3h |
| 3 | Add **Đại Hạn × Lưu Niên overlap detection** | `engine/tu_vi/analyzer.py` | 2h |
| 4 | Add **kỳ cách** (reverse-cát) marker vào dict | `engine/tu_vi/cach_cuc_dict.py` | 1h |
| 5 | **Psychological safety rules** — Xương Khúc + năm Kỷ/Tân/Nhâm + Thìn/Tuất → cảnh báo health tinh thần | `engine/tu_vi/psychological_safety.py` (mới) | 2h |
| 6 | Q3 case studies (An Lộc Sơn, Triệu Cao) → `data/tu_vi/case_studies.json` | data file | 1h |
| 7 | Tứ Hóa per cung (48 entries) từ p0187-p0198 | `data/tu_vi/tu_hoa_per_cung.json` | 3h |
| 8 | UI **Lưu Nguyệt panel** với Đẩu Quân tracking | `client/webapp/src/components/LuuNguyetPanel.vue` | 4h |

---

## XI. Tâm Q3 (theo Iron Rule #6)

✅ **GIỮ**: Cát hung không tuyệt đối — Q3 case An Lộc Sơn (giàu nhưng phản nghịch) chứng minh.
✅ **GIỮ**: Phải đọc CƠ + BIẾN — Q3 dành riêng 10+ trang luận Đại Hạn / Tiểu Hạn / Đẩu Quân = paradigm "biến hóa" Khang Tiết.
✅ **GIỮ**: Kỳ cách — phá cách có thể là quý cách nếu đủ điều kiện năm sinh. Đừng phán cố.
✅ **GIỮ**: Psychological safety — Q3 có warning cụ thể (lự đầu hà). Sage Tử Vi PHẢI thấy + dùng đúng cách (chăm sóc thay vì hù).

❌ **TRÁNH**: Surface raw text Q3 mà không filter context. 162 passage cho user là quá tải.
❌ **TRÁNH**: Bỏ Đẩu Quân — sao này là chìa khóa Lưu Nguyệt.

---

**Kết**: Q3 không chỉ là "168 combos sao×cung". Q3 dạy phương pháp đọc Đại Hạn + Lưu Niên + Lưu Nguyệt qua Đẩu Quân; dạy kỳ cách (phản cát/hung); dạy psychological safety qua warning Văn Xương Khúc + năm + Thìn Tuất. Khang Tiết hiện diện lần 3 → bộ Tử Vi + Mai Hoa thực sự đồng tác.

**Tiếp theo**: thâm nhuần Q4 (Lá Số Cổ Kim, 102 trang, 60+ case studies) → kết hợp với case Q3 (An Lộc Sơn, Triệu Cao) → build full `case_studies.json` để feature "Giống ai trong lịch sử".
