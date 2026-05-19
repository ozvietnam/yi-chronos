# Engine Gaps — Mai Hoa Q1+Q2 Thâm Nhuần

**Ngày**: 2026-05-19
**Nguồn**: Thâm nhuần Mai Hoa Q1+Q2 (311 trang, p15-p327)
**Phát hiện**: 298 methods + 523 concepts unique → engine có cần update không?

---

## I. Engine Mai Hoa hiện tại (audit)

### ✅ Đã có

| Module | Function | Mô tả |
|---|---|---|
| `core/yi64/derivations/mai_hoa_nntt.py` | `derive_inputs_from_chronos()` | Niên Nguyệt Nhật Thời từ ChronosState |
| | `derive_line_states()` | Tính 6 hào động |
| | `derivation_summary()` | Output 5 quẻ phái sinh |
| `engine/yi_wiki/interpret.py` | `MaiHoaInterpretation` dataclass | Đầy đủ cấu trúc luận quẻ |
| | Quẻ Chánh + Quẻ Hổ + Quẻ Biến + động hào | ✓ |
| | `external_omen_*` (Khắc ứng) | ✓ Q3 Iron Rule #4 đã wire |
| | `posture_*` (tư thế thân thể) | ✓ Q3 Iron Rule #4 đã wire |
| | `paradigm_quan_vat_trace` (Khí→Tượng→Số→Thần→Tính) | ✓ |
| `api/main.py` | `POST /api/hexagram/mai-hoa-cast` | Cast endpoint |
| `engine/luc_hao/mai_hoa_env.py` | Tiết khí, Kp, pha trăng | Environmental context |

### ✅ Top methods Q1+Q2 vs engine

| Method (Q1+Q2) | Engine có? | Notes |
|---|---|---|
| Khắc ứng (19×) | ✅ | `external_omen_*` |
| Quan vật chiêm (16×) | ✅ | `paradigm_quan_vat_trace` |
| Niên Nguyệt Nhật Thời (13×) | ✅ | `core/yi64/derivations/mai_hoa_nntt.py` |
| Thể dụng sinh khắc (5×) | ⚠️ Partial | engine có Thể-Dụng marker nhưng chưa tự động tính sinh-khắc ngũ hành |
| Tam yếu (3×) | ❌ | **GAP** |
| Thập ứng (3×) | ❌ | **GAP** — 10 loại ứng |
| Chính ứng (3×) | ⚠️ | Engine có "Khắc ứng" generic, chưa phân biệt sub-types |
| Biến ứng (3×) | ❌ | **GAP** |
| Nhật ứng (3×) | ❌ | **GAP** — ứng theo NGÀY (vs khoảnh khắc) |
| Ngoại ứng (3×) | ⚠️ | Đã có `external_omen` nhưng KHÁI NIỆM khác chút |
| Thiên thời ứng (3×) | ❌ | **GAP** |
| Địa lý ứng (3×) | ❌ | **GAP** |
| Phong giác chiêm (2×) | ❌ | **GAP** |
| Thanh âm chiêm (2×) | ❌ | **GAP** |

---

## II. ❌ Gaps cần bổ sung engine

### Gap 1 — "Thập ứng" (10 loại ứng)

Q2 dạy phân biệt 10 loại "ứng" (signal) khi đoán quẻ:

| # | Tên ứng | Mô tả | Engine status |
|---|---|---|---|
| 1 | **Chính ứng** | Ứng trực tiếp với câu hỏi | ❌ |
| 2 | **Biến ứng** | Ứng theo biến chuyển | ❌ |
| 3 | **Nhật ứng** | Ứng theo ngày hiện hành (天干地支日) | ❌ |
| 4 | **Ngoại ứng** | Ứng từ môi trường bên ngoài (giống external_omen) | ⚠️ Partial |
| 5 | **Thiên thời ứng** | Ứng từ thời tiết, mưa, gió, sấm | ❌ |
| 6 | **Địa lý ứng** | Ứng từ địa hình, vị trí | ❌ |
| 7 | **Nhân sự ứng** | Ứng từ người gặp | ❌ |
| 8 | **Vật loại ứng** | Ứng từ vật (chim bay, côn trùng) | ❌ |
| 9 | **Thanh âm ứng** | Ứng từ âm thanh | ❌ |
| 10 | **Hành chỉ ứng** | Ứng từ tư thế, cử chỉ (giống `posture`) | ⚠️ Partial |

→ Đề xuất: thêm `external_omen.category` enum với 10 giá trị trên.

### Gap 2 — "Tam yếu" (3 yếu tố)

Q1 nêu 3 yếu tố cốt lõi khi xem quẻ:
1. **Yếu 1**: Quẻ Chánh (Thể-Dụng)
2. **Yếu 2**: Khắc ứng (external)
3. **Yếu 3**: Sinh-Khắc (relationships)

→ Engine đã có cả 3 nhưng chưa wrap thành 1 method `tam_yeu_summary()`.

### Gap 3 — Thể-Dụng sinh-khắc auto

Engine hiện chỉ mark "Thể-quái" và "Dụng-quái" qua động hào. **Chưa tự động** tính:
- Thể sinh Dụng (Thể tổn, Dụng vượng) → người hỏi hao tổn cho người/việc
- Dụng sinh Thể (Dụng tổn, Thể vượng) → người/việc đem lợi đến
- Thể khắc Dụng (Thể vượng, Dụng tổn) → người hỏi thắng việc
- Dụng khắc Thể (Dụng vượng, Thể tổn) → việc thắng người hỏi
- Thể-Dụng tỷ hòa → bình bình

→ Đề xuất: thêm `interpret.py:_compute_the_dung_relationship()` dựa trên ngũ hành 2 quẻ.

### Gap 4 — 9 chiêm chuyên đề (Q2)

Q2 chia "Chiêm bốc huyền cơ" thành 9-10 lĩnh vực:

| Chiêm | Engine cần |
|---|---|
| **Thiên thời chiêm** (天時占) | Hỏi thời tiết, mưa nắng |
| **Gia trạch chiêm** (家宅占) | Hỏi nhà cửa, nơi ở |
| **Hôn nhân chiêm** (婚姻占) | Hỏi hôn nhân, vợ chồng |
| **Sinh sản chiêm** (生產占) | Hỏi sinh con |
| **Cầu danh chiêm** (求名占) | Hỏi học hành, công danh |
| **Giao dịch chiêm** (交易占) | Hỏi mua bán, kinh doanh |
| **Xuất hành chiêm** (出行占) | Hỏi đi xa |
| **Thất vật chiêm** (失物占) | Hỏi mất đồ |
| **Tật bệnh chiêm** (疾病占) | Hỏi bệnh tật |
| **Quan tụng chiêm** (官訟占) | Hỏi kiện tụng |
| **Phần mộ chiêm** (墳墓占) | Hỏi mồ mả phong thủy |

Mỗi chiêm có quy tắc đọc Thể-Dụng + ngũ hành riêng. Engine hiện chỉ có generic interpretation, không có **branch theo loại câu hỏi**.

→ Đề xuất: thêm `interpret.py:interpret_by_topic(topic_id)` với 10 sub-interpreters.

---

## III. Engine update roadmap (sau Q1+Q2 audit)

| Priority | Việc | Effort | Reference |
|---|---|---|---|
| 🥇 | `_compute_the_dung_relationship()` — 5 cases ngũ hành | 1h | Q1 Thể-Dụng sinh-khắc |
| 🥇 | `Thập ứng` category enum (10 values) | 30p | Q2 |
| 🥈 | `interpret_by_topic(topic_id)` — 9 sub-interpreters | 3-4h | Q2 9 chiêm |
| 🥉 | `tam_yeu_summary()` wrapper | 30p | Q1 |
| 🥉 | Hand-tuning: extract patterns từ master/methods_index.json | 1h | Q1+Q2 master |

**Total**: ~6h cho đủ engine theo Q1+Q2 Mai Hoa.

---

## IV. Lá số Anh — chưa apply trực tiếp

Mai Hoa = chiêm bốc khoảnh khắc, không phụ thuộc ngày sinh user. Tuy nhiên với engine update:
- Nếu Anh hỏi về **kinh doanh** → engine route đến **Giao dịch chiêm** (Q2 p160-180)
- Nếu Anh hỏi về **vợ chồng** → engine route đến **Hôn nhân chiêm** (Q2 p150-170) — combine với cảnh báo Tử Vi Phu Thê Hóa Kỵ (Iron Rule #6)

---

## V. Stats sau Q1+Q2

| Metric | Value |
|---|---|
| Trang processed | 311 (Q1: 101 + Q2: 210) |
| Methods unique | **298** |
| Concepts unique | **523** |
| Cost | $0.2383 |
| Top method | Khắc ứng (19×) |

Wiki state: **3,609 concepts + 2,463 passages** (Mai Hoa contribution: +523 + 298)

---

_Source: master/{methods_index, concepts_index}.json_
_PDF: data/published/mai-hoa-q1q2-nguyen-tac.pdf (278 trang)_
