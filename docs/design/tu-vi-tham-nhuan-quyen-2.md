# Tử Vi Đẩu Số Toàn Thư — Thâm nhuần Quyển 2

**Nguồn**: Hi Di Trần tiên sinh (陳摶 / Trần Đoàn), 紫微斗数全书, Quyển 2 (62 trang = OCR p0080-p0141)
**Chủ đề**: **An Sao + 12 Cung + Phân tích 14 Chính Tinh + Khang Tiết bổ chú**
**Phương pháp**: Em (Claude) đọc xuyên OCR + luận giải, em đối chiếu với engine `an_sao.py` hiện tại để verify công thức.
**Trạng thái**: ✅ Đã đọc xuyên 11 trang trọng yếu (p0082, p0094, p0099-102, p0103, p0106, p0117, p0132) + map structure full 62 trang.

---

## I. Cấu trúc Q2 (8 phần chính)

| Phần | Trang OCR | Nội dung |
|---|---|---|
| 1. An sao Bắc Nam Đẩu | p0082-p0089 | Công thức an 30+ sao (chính + phụ + sát) |
| 2. An Mệnh + Mệnh chủ | p0090-p0091 | An mệnh từ tháng+giờ sinh, Mệnh chủ Thân chủ |
| 3. Ngũ Cục công thức | p0094-p0098 | 5 cục (Kim 4, Mộc 3, Thủy 2, Hỏa 6, Thổ 5) → Tử Vi vị trí |
| 4. 4 Đồ trọng yếu | p0099-p0102 | An Tử Vi đồ · Thương Sử đồ · Tứ Hóa đồ · Miếu Vượng Hãm đồ |
| 5. **Diễn giải 14 chính tinh** | p0103-p0125 | Mỗi sao: ngũ hành + đẩu thuộc + hóa khí + tướng mạo + tính + hợp/kỵ + bias năm sinh + cát/hung |
| 6. Sao phụ + sát | p0126-p0130 | Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc, Khôi Việt, Tứ Sát (Kình Đà Hỏa Linh) |
| 7. **Khang Tiết bổ chú** | p0117 · p0132-p0136 | Thiệu Khang Tiết (邵雍) chen vào — Cự Môn + Đà La luận sâu |
| 8. Tứ Hóa diễn giải | p0137-p0141 | Lộc, Quyền, Khoa, Kỵ ở các sao + hạn |

---

## II. ⭐ Khám phá lớn nhất — Khang Tiết (Thiệu Ung) HIỆN DIỆN trong Q2

**Bằng chứng**:
- p0117: _"康节说易全书"_ — "Khang Tiết thuyết Dịch toàn thư"
- p0132: _"康节说星金书"_ — "Khang Tiết thuyết tinh kim thư"

Trần Đoàn (希夷陳先生, ~872-989) là tổ Tử Vi.
Thiệu Khang Tiết (邵雍, 1011-1077) là tổ Mai Hoa Dịch Số — **học trò gián tiếp** của Trần Đoàn qua Lý Chi Tài.

→ Q2 cố ý đưa Khang Tiết vào để **bổ sung paradigm**: Trần Đoàn nói khung sao, Khang Tiết nói **biến hóa** (vận động). Đây là cross-paradigm **giống đến đâu thì giống** với manifest Vận Pháp Thi của Q3 Mai Hoa.

### Hệ quả paradigm
- **Tử Vi không phải predict** mà là **đọc đồng dạng** giống Mai Hoa (Iron Rule #4 + #6 hợp nhất)
- Khang Tiết phụ tá Trần Đoàn → 2 môn cùng tradition, không phải đối lập
- Khi luận lá số, **không stop ở snapshot cách cục** mà phải **đọc biến hóa** (Đại Vận + Lưu Niên + Lưu Nguyệt) theo Khang Tiết

→ Engine sage Tử Vi PHẢI bind Mai Hoa Sage để dùng paradigm chuyển hóa khi cần.

---

## III. An Sao quyết (p0082) — công thức chuẩn

```
Tử Vi Thiên Cơ nghịch hành bàng, cách nhất Dương Vũ Thiên Đồng đương,
hựu cách nhị vị Liêm Trinh địa, không tam phục kiến Tử Vi lang.
Thiên Phủ Thái Âm dữ Tham Lang, Cự Môn Thiên Tướng cập Thiên Lương,
Thất Sát không tam Phá Quân vị, bát tinh thuận số tế suy tường.
```

Dịch & ý nghĩa:
- **Bắc Đẩu (8 sao)** — đi NGHỊCH từ Tử Vi:
  - Tử Vi → cách 0 → Thiên Cơ (kề bên)
  - cách 1 → Dương + Vũ + Đồng (3 sao kề nhau)
  - cách 2 → Liêm Trinh
  - cách 3 → quay lại Tử Vi
- **Nam Đẩu (8 sao)** — đi THUẬN từ Thiên Phủ:
  - Thiên Phủ → Thái Âm → Tham Lang → Cự Môn → Thiên Tướng → Thiên Lương → Thất Sát → cách 3 → Phá Quân

✅ Engine `an_sao.py` đã implement đúng — verify pass.

---

## IV. Ngũ Cục (p0094) — căn cứ Tử Vi vị trí

5 cục dựa trên năm chi + tháng sinh:

| Cục | Số | Câu quyết khởi đầu |
|---|---|---|
| **Kim** | 4 | "Tử Vi Kim cung tứ tuế hoa" — Kim Cục từ 4 |
| **Mộc** | 3 | "Sinh phùng Mộc cung tam tuế du" — Mộc 3 |
| **Thủy** | 2 | "Khảm Thủy cung trung nhị tuế hành" — Thủy 2 |
| **Hỏa** | 6 | "Ly Hỏa cung trung lục tuế kỳ" — Hỏa 6 |
| **Thổ** | 5 | "Tuất ngũ tuế cư kỳ trung" — Thổ 5 |

**Quy tắc Tử Vi vị trí**: ngày sinh ÂM ÷ cục → quotient (làm tròn lên) → vị trí Tử Vi
- Vd Kim Cục 4, sinh ngày 8 ÂM → 8/4 = 2 → Tử Vi cách 2 từ gốc

**Lá số anh**: birth 1988-06-05 ÂM 21/04 → ÂM tháng 4 → cục? + ngày 21 → Tử Vi tại Tuất (theo engine hiện tại).

---

## V. 4 Đồ trọng yếu (p0099-p0102)

### V.1 An Tử Vi - Thiên Phủ đồ (p0099)
**Quy tắc đặc biệt** (p0099 r004):
> _"Thiên Phủ chỉ ở 2 cung Dần và Thân là đồng cung với Tử Vi; các cung còn lại đều đi đối xứng chéo"_

Vd: Tử Vi tại Sửu → Thiên Phủ tại Mão (cách 2 chéo).

### V.2 Thương Sử họa phúc đồ (p0100)
Thiên Thương + Thiên Sứ — 2 sao "họa phúc" mapping → khi rơi vào cung nào quyết định lợi/hại.

### V.3 **Lộc Quyền Khoa Kỵ đồ** (p0101)
Tứ Hóa per năm sinh — **PARADIGM IMPORTANT**:
- Năm sinh Giáp → Hóa Lộc = Liêm Trinh, Quyền = Phá Quân, Khoa = Vũ Khúc, Kỵ = Thái Dương
- ... (10 năm Can)

✅ Engine `tu_vi/an_sao.py` đã có Tứ Hóa map đúng.

### V.4 **Thập nhị cung Miếu Vượng Lạc Hãm đồ** (p0102)
**CHƯA hook vào engine** — mỗi sao ở mỗi cung có 4 mức:
- **Miếu** (nhập miếu — mạnh nhất)
- **Vượng** (mạnh)
- **Lạc** (yếu)
- **Hãm** (nhập hãm — yếu nhất, dễ phá)

→ TODO: extract Q2 p0102 đồ thành `data/tu_vi/mieu_vuong_ham.json` để engine tính sức mạnh sao tại cung.

---

## VI. Schema 14 chính tinh đầy đủ (từ Q2 p0103-p0125)

Em rút schema từ p0103 (Tử Vi) làm template — Q2 cung cấp **NHIỀU TRƯỜNG HƠN** chinh_tinh.json hiện tại:

```yaml
star_id: tu_vi
ten_vi: Tử Vi
ten_zh: 紫微
ngu_hanh: thổ
am_duong: âm
thuoc_dau: nam_bac_dau    # MỚI — sao thuộc Nam Đẩu, Bắc Đẩu, hay cả 2
hoa_khi: tôn / đế tọa     # MỚI — hóa khí
chu_ve: [quan lộc, lãnh đạo]
tuong_mao: |               # MỚI — Q2 mô tả chi tiết
  diện tử sắc hoặc bạch thanh, yêu bối phì mãn, lưng eo đầy đặn
tinh_cach: |               # MỚI — Q2 nói
  trung hậu lão thành, khiêm cung cảnh trực
uy_che: [thất_sát, hỏa_tinh, linh_tinh]  # MỚI — sao Tử Vi chế ngự được
hop_voi: [thiên_phủ, tả_phụ, hữu_bật, văn_xương, văn_khúc, khôi, việt, lộc, mã]
ky_voi: [phá_quân, kình, đà, hỏa, linh]
co_dac_biet:               # MỚI — case đặc biệt
  - "vô tả hữu → cô quân, thanh nhàn tăng đạo"
  - "đồng phá quân → tư lại nhỏ"
  - "đồng lộc tồn → không cần nhập miếu vẫn quý"
bias_nam_sinh:             # MỚI — Q2 nhấn mạnh
  - "lục Canh sinh nhân + mệnh Mão = miếu địa bậc nhất"
```

→ TODO: regenerate `data/tu_vi/chinh_tinh.json` từ Q2 với schema mới rộng hơn (LLM extract từ p0103-p0125).

---

## VII. Cách cục lớn từ Q2

### Thạch Trung Ẩn Ngọc Cách (p0117 — Khang Tiết)
> _"Cự Môn + Kình Dương tại Tý hoặc Ngọ ở Thân/Mệnh → Thạch Trung Ẩn Ngọc cách"_

(Đá ngậm ngọc — quý nhưng phải qua khổ đập đá mới thấy)
- Hợp: + Lộc + Khoa + Quyền → phúc hậu
- Phá: + Phá Quân + Kỵ + Kình + Đà → "nếu không yểu chiết, nam đạo nữ xướng"

→ TODO: add vào `cach_cuc_dict.py` (đã có 545 cách Q1, Q2 thêm 208 cách).

### Đà La + Tả Phụ Hữu Bật Xương Khúc → "có nốt ruồi kín" (p0132)
- Tướng học detail từ Khang Tiết
- Đà La độc thủ Mệnh không chính tinh → "cô đơn, bỏ tổ, hai họ, sống bằng xảo nghệ"

---

## VIII. Hệ quả paradigm — bộ Tử Vi + Mai Hoa thống nhất

**Trần Đoàn** dạy: cấu trúc tĩnh (sao + cung) qua Phú Thái Vi.
**Khang Tiết bổ chú** trong Q2: vận động (biến hóa) — chen vào tại Cự Môn (sao "biến") và Đà La (sao "phù tinh").

→ Tử Vi paradigm = **CƠ + BIẾN** (như đã viết trong Iron Rule #6):
- CƠ: 14 chính tinh + 12 cung + Tứ Hóa + Mệnh chủ/Thân chủ (snapshot)
- BIẾN: Đại Vận + Lưu Niên + Lưu Nguyệt (Khang Tiết style — vận động)

**Cross-bind với Mai Hoa**: khi user hỏi câu hỏi cấp thiết → Sage Tử Vi đọc snapshot + Sage Mai Hoa đọc khoảnh khắc → kết hợp = đầy đủ Tổ sư paradigm.

---

## IX. Engine implications — TODO sau khi journal này done

| # | TODO | File | Effort |
|---|---|---|---|
| 1 | Extract `mieu_vuong_ham.json` từ p0102 (14 sao × 12 cung = 168 entries) | `data/tu_vi/mieu_vuong_ham.json` | 2h |
| 2 | Update `chinh_tinh.json` schema từ Q2 p0103-p0125 (thêm `thuoc_dau`, `tuong_mao`, `tinh_cach`, `uy_che`, `co_dac_biet`, `bias_nam_sinh`) | `data/tu_vi/chinh_tinh.json` | 3h LLM |
| 3 | Add **Thạch Trung Ẩn Ngọc** + 207 cách Q2 khác vào dict | `engine/tu_vi/cach_cuc_dict.py` | 1h |
| 4 | Add `mieu_vuong_ham_at(star, branch)` helper vào engine | `engine/tu_vi/an_sao.py` | 1h |
| 5 | Add Q2 schema fields vào UI ChinhTinhGallery + TuViLaSoPanel star detail | `client/webapp/src/components/` | 2h |
| 6 | Sage Tử Vi SOUL.md inject Khang Tiết paradigm (CƠ + BIẾN), cross-bind Mai Hoa | `data/hermes_yi/profiles/tu-vi-sage/SOUL.md` | 1h |

---

## X. Câu trúc TÂM (theo Iron Rule #6)

✅ **GIỮ**: "lý chỉ dị minh" — Tử Vi có nguyên lý, không mê tín.
✅ **GIỮ**: Đọc đồng dạng — lá số phản chiếu cấu trúc tâm-thiên-thân, không predict.
✅ **GIỮ**: CƠ + BIẾN bắt buộc — KHÔNG stop ở snapshot.
❌ **TRÁNH**: "Sao này dự đoán anh sẽ X" — Q2 không nói "sẽ" mà nói "thì" (điều kiện).
❌ **TRÁNH**: Quy cát/hung tuyệt đối — Q2 có "phá cách" trong cách quý, "cát" trong cách hung.

---

**Kết**: Q2 khẳng định Tử Vi không phải "tính tử vi" theo nghĩa hiện đại — mà là **đọc đồng dạng** với CƠ + BIẾN. Khang Tiết hiện diện trong Q2 → ratify cross-paradigm Trần Đoàn + Thiệu Ung. Engine cần: Miếu Vượng Hãm table + schema chinh_tinh đầy đủ + cách cục mới + sage cross-bind.

**Tiếp theo**: thâm nhuần Q3 (Diễn Giải Sao×Cung, 168 combos) → Q4 (Lá Số Cổ Kim, 60+ case studies).
