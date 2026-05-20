# Q4 Reconciliation — Claim Audit + NEW INSIGHTS từ Kinh Điển

**Source**: 6 batches Phase A (`tu-vi-q4-batch-1.md` → `tu-vi-q4-batch-6.md`)
**Audit date**: 2026-05-20
**Purpose**: (1) Reconcile journal Q4 cũ vs evidence; (2) Rút NEW INSIGHTS từ Q4 mà em đã bỏ sót

---

# Phần 1 — Claim Audit (Truthfulness check)

## 1.1 Journal Q4 hiện tại (`tu-vi-tham-nhuan-quyen-4.md`) — claim by claim

| # | Claim cũ | Verdict | Evidence |
|---|----------|---------|----------|
| C1 | "Q4 = Khang Tiết Edition (~30+ Khang Tiết refs)" | ❌ **RETRACT** | 6 batches confirm "Khang Tiết..." chỉ là **HEADER LẶP** trên chart pages + 1-2 commentary sections. Không phải "edition" |
| C2 | "Q4 = 60+ case studies" (LEDGER cũ) | ✅ **PARTIAL CONFIRM** | Q4 thực sự có ~30 chart figures (Khổng Tử, Tử Lộ, Triệu Cao, Lý Tư, Lưu Linh, Hàn Thông...) ở p0199-p0256. Em không extract per CEO decision |
| C3 | "Q4 chỉ 2 phê mệnh templates" | ❌ **CORRECTED** | Thực tế **7 phê mệnh templates** (p0257 + p0259 + p0260 + p0261 + p0262 + p0263 + p0264) |
| C4 | "Q4 có Định thời khắc lệ p0267" | ✅ **CONFIRMED** | Batch 3 verified verbatim |
| C5 | "Hựu Thiên Quán Phân Cung p0271 = 12 archetypes" | ❌ **CORRECTED** | Thực tế **36 archetypes** (12 giờ × 3 khắc thượng/trung/hạ) — bắt đầu p0268, không phải p0271 |
| C6 | "Định tử sinh quyết — sinh ly khắc tử rules" | ❌ **UNDER-ESTIMATED** | Thực tế là **predict death timing rules** (Thiên Khốc + Thiên Hư → chết trong 3-5 ngày). PSYCH SAFETY paradigm SAI nguy hiểm nếu surface raw |
| C7 | "Phần 3 = Định thời + Thiên Quán + Tử sinh + Tứ Hóa" | ❌ **WRONG MAPPING** | Thực tế Phần 3 (p0269-p0300) = **2 KINH PHÁI KHÁC** (Chiếu Đởm Kinh + Nhập Cốt Tiên Kinh) với 18 Phi Tinh + matrix riêng |
| C8 | "An Lộc Sơn + Triệu Cao mệnh thị dã" (case studies Q3) | ✅ **CONFIRMED + EXPANDED** | Verified Q3 p0180. Plus: Triệu Cao có CHART CỤ THỂ ở Q4 batch 2 (p0210) |
| C9 | "Cases lịch sử Q4: Trác Mậu, Lỗ Cung, Cung Khiêm, Cung Hoàng, Sơ Quảng, Sơ Thụ" | ⚠️ **VERIFY NEEDED** | 4 names confirmed in p0257-p0258 phê mệnh template references. Batches 1-2 thêm: Khổng Tử, Tử Lộ, Triệu Cao, Lý Tư, Lưu Linh, Hàn Thông (verified visual chart inspect) |
| C10 | "Q4 paradigm 'mỗ' pattern + KHÔNG predict" | ✅ **CONFIRMED + REINFORCED** | p0299 r018 verbatim: _"Thập bát tinh chuyển, tại nhân biến thông. **Bất khả chấp nhất**, y thân hội đoạn."_ → 2 kinh nói thẳng KHÔNG predict cứng |

### Verdict tổng: ~50% journal Q4 cũ chính xác, ~30% wrong, ~20% under-estimated

→ Journal cũ cần **rewrite hoàn toàn** sau Phase B.

---

## 1.2 Engine modules đã build — quick verdict (chi tiết ở `Q4-ENGINE-AUDIT.md`)

| Module | Source claim | Verdict |
|--------|-------------|---------|
| M1 — `case_studies.json` (8 figures) | Q3+Q4 | ⚠️ Cung Toại + Hoàng Bá có thật trong source? Verify needed |
| M2 — `dau_quan.py` | Q2+Q3 (not Q4) | ✅ OK |
| M3 — `psychological_safety.py` | Q1+Q3 (not Q4) | ✅ OK — nhưng Q4 có ⚠️ **Định tử sinh quyết** dữ hơn → cần add |
| M4 — `mieu_vuong_ham.py` | Q2 | ✅ OK |
| M5 — `chinh_tinh.py` v2 | Q2 | ✅ OK |
| M6 — `phe_menh()` LLM | Q4 "mỗ" + Khang Tiết Edition thesis | ⚠️ SYSTEM prompt claim "Khang Tiết Edition" → SAI thesis. Generator chỉ học từ 1 sample, thực có 7 samples |
| M7 — Sage cross-bind "Khang Tiết bridge" | Q4 paradigm | ⚠️ Bridge metaphor OK nhưng "Khang Tiết co-author" claim cần soften |
| M8 — UI `TuViLaSoPanel.vue` hooks | Surface deps M1+M6 | ⚠️ Downstream issues |

---

# Phần 2 — ⭐ NEW INSIGHTS TỪ KINH ĐIỂN (CEO hứng thú)

Đây là những điểm Q4 chứa mà em đã bỏ sót khi skim. Em sắp xếp theo **mức độ quan trọng paradigm**.

---

## ⭐⭐⭐⭐⭐ Insight #1 — METHODOLOGY 10 BƯỚC CHÍNH THỨC của Trần Đoàn

**Source**: Q4 p0266 r003 (verbatim)
> _"Nhất định thời khắc, nhị khởi bát tự, tam lập cách cục, tứ bài tinh thần, ngũ lập tọa mệnh, lục khởi đại vận, thất khởi đại hạn, bát thư hóa diệu, cửu thư hỉ kỵ, thập bài cát hung."_

10 bước paradigm rõ ràng + chi tiết từng bước p0266-p0267:

1. **Định thời khắc** — định giờ + khắc (thượng/trung/hạ)
2. **Khởi Bát Tự** — Tứ Trụ + sinh vượng/hình xung/tam hợp/sát/mộ khố/không vong
3. **Lập cách Dụng Thần** — Tài Quan Ấn Thực, Thương Quan, Tỷ Kiếp, Thiên Đức Nguyệt Đức, Quý Lộc Nhẫn Sát, Kim Thần Khôi Cương, Củng cách, Tỉnh Lan, Đảo Xung, Triêu Dương, Long Bối, Tùng cách
4. **An sao** — 14 chính tinh + phụ tinh (Q2 đã làm)
5. **Lập tọa Mệnh** — Tam phương tứ chính + 12 cung thân + trường sinh + mã tiền sát + tọa mộ tọa lộc
6. **Khởi Đại Vận** — Sinh phù tiết chế, hợp khắc hướng bội
7. **Khởi Đại Hạn / Lưu Niên** — Thái Tuế chinh phạm, hình hợp nhật chủ
8. **Thư Tứ Hóa** — Lộc, Quyền, Khoa, Kỵ
9. **Thư hỉ kỵ** — đảo hạn thần sát + cứu trợ
10. **Bài cát hung** — Đoán ứng tử mệnh, niên/nguyệt/nhật/thời/khắc

→ **Tại sao mới**: Em (và sage Tử Vi hiện tại) đang đọc lá số theo trình tự **ad-hoc** (xem chính tinh ở Mệnh, rồi cách cục, rồi Đại Vận). 10 bước này là **trình tự CHÍNH THỨC** của Trần Đoàn — phải tuân.

→ **Engine implication**: Sage Tử Vi SOUL.md phải **embed 10 bước này như checklist**. Hiện chưa có.

---

## ⭐⭐⭐⭐⭐ Insight #2 — Q4 chứa **2 KINH PHÁI KHÁC** (Chiếu Đởm Kinh + Nhập Cốt Tiên Kinh)

**Source**: Q4 p0271 r010 + p0297 r003 (verbatim)
- _"Chiếu Đởm Kinh Tứ Ngôn Thập Bát Phi Tinh Trực Chỉ Tự"_ (照胆经)
- _"Nhập Cốt Tiên Kinh Tứ Ngôn Tổng Đoạn Toát Yếu Pháp"_ (入骨先经)

### Phân biệt 2 kinh:

| Aspect | Tử Vi Đẩu Số chính thống (Q1-Q3) | Chiếu Đởm Kinh (Q4) | Nhập Cốt Tiên Kinh (Q4) |
|--------|----------------------------------|---------------------|--------------------------|
| Tên sách | Tử Vi Đẩu Số 紫微斗数 | 照胆经 | 入骨先经 |
| Sao chính | 14 chính tinh | **18 Phi Tinh** | 18 Phi Tinh + tổng đoán 4-chữ |
| Convention 10 can | Giáp Bính Mậu Canh Nhâm = **DƯƠNG** | ⚠️ **ĐẢO** (= ÂM) | Same as Chiếu Đởm |
| An sao Tử Vi | Theo Ngũ Cục + ngày | **Cung Tý** (default?) | Same |
| Phong cách | Phú thi luận giải | Phú thi 4-câu per sao | Tóm đoán 4-chữ |

→ **Tại sao mới**: 3 trường phái Tử Vi (gần 1000 năm) gồm: **Bắc Phái Trần Đoàn** (chính thống), **Nam Phái** (sửa của Bắc Phái), **Trung Châu Phái** (hiện đại). NHƯNG Q4 chứa **2 kinh khác** mà sách hiện đại Tử Vi VN không proliferated. Đây có thể là **kinh điển bị mất tích** mà Q4 giữ lại được.

→ **Engine implication**: KHÔNG tích hợp Chiếu Đởm Kinh / Nhập Cốt Tiên Kinh vào main engine (sẽ phá convention). Phải tách **panel riêng "Phái Chiếu Đởm + Nhập Cốt Tiên"** parallel với main Tử Vi.

---

## ⭐⭐⭐⭐ Insight #3 — **36 ARCHETYPES** (12 giờ × 3 khắc) — typology độc lập

**Source**: Q4 p0268-p0271 — bắt đầu _"Mệnh tinh thời khắc độ số tổng luận"_

Mỗi (giờ, khắc) = 1 archetype riêng với:
- **Cung tên** (Thiên Khố, Thiên Quán, Hồng Loan, Thiên Không, Thiên Thọ, Thiên Ấn, Thiên Lộc, Tử Vi Điện Giá, Thiên Hư, Thiên Phúc, Văn Xương phân cung, Thiên Quán Phân Cung, Hựu Thiên Quán)
- **Khắc cha/mẹ rule** (tiên khắc phụ / mẫu / vô khắc phá)
- **Lục thân profile** (huynh đệ vô tình / hữu tứ ngoại hòa khí...)
- **Sự nghiệp + tổ nghiệp profile**

### Sample (verbatim quotes from Q4)

| Archetype | Cung name | Source quote |
|-----------|-----------|--------------|
| **Tý thượng** | Thiên Khố | _"Tiên khắc mẫu, tự thành kế. Y lộc bất túc, huynh đệ vô tình."_ (p0268 r003) |
| **Tý trung** | Thiên Quán | _"Vô khắc phá. Tác sự khởi đảo, mạt niên xứng ý."_ (p0268 r005) |
| **Mùi thượng** | Tử Vi Điện Giá | _"Vô khắc phá. Huynh đệ hữu tứ, ngoại hòa khí. Đáo xứ xuân phong, tâm hành bình trực..."_ (p0270) |
| **Hợi thượng** | Thiên Quán Phân Cung | _"Tiên khắc mẫu. Tác sự lược vi năng. Lục thân thiểu kháo..."_ (p0271 r005) |

→ **Tại sao mới**: Đây là **typology độc lập** với 12 cung Tử Vi chính thống (cung = chức năng). 36 archetypes phân theo **giờ-khắc**, đại diện **archetype tính cách + lục thân pattern**. KHÔNG cần lá số đầy đủ — chỉ giờ sinh + khắc là đoán được.

→ **Engine implication**: 36 archetypes làm **fast personality preview** mà KHÔNG cần cast full chart. Phù hợp cho users không biết chính xác lá số nhưng biết giờ sinh.

---

## ⭐⭐⭐⭐ Insight #4 — **Định thời khắc lệ + Tiểu nhi thời khắc** (rectification)

**Source**: Q4 p0267 r017-r024 (verbatim)

### (a) Định thời khắc qua hoạt động hàng ngày
> _"Bán dạ tý khắc kê minh sửu, bình đán dần thời nhật xuất mão._
> _Thực thời thần hề chúc trung tị, ngọ nhật trung vị nhật trắc diểu._
> _Hoàng hôn tuất hề thụy chúc hợi, bộ thời thân hề nhật nhập dậu."_

12 hoạt động ↔ 12 giờ — engine có thể quiz user: "khi sinh, mọi người đang làm gì?" → suy ra giờ.

### (b) Tiểu nhi thời khắc qua đỉnh đầu trẻ
> _"Tý ngọ mão dậu hướng phụ sinh, nhân vật tiểu xảo đỉnh trung bình._
> _Dần thân tị hợi song đỉnh định, bán phiến hướng phụ thể trung đình._
> _Thìn tuất sửu mùi hoàn phiên đỉnh, bội sinh ư phụ hệ phì nhân."_

3 đỉnh đầu pattern ↔ 12 giờ — physical trait → rectify giờ sinh.

→ **Tại sao mới**: Birth hour quiz v2 em đã có dùng **behavior pattern** (Hợi/Tý/Sửu...). Q4 cung cấp **rule cụ thể** từ kinh điển — quiz v3 có thể quote nguyên văn cổ nhân.

→ **Engine implication**: Update birth_hour_quiz v2 với Q4 quotes. Add rectification by physical trait (đỉnh đầu) cho parents biết giờ sinh con.

---

## ⭐⭐⭐⭐ Insight #5 — **18 PHI TINH** schema parallel system

**Source**: Q4 p0271-p0299 — 18 sao với ngũ hành + âm dương + vị miếu vượng riêng

### Bảng 18 Phi Tinh (verbatim từ p0275 + per-sao detail)

**9 Dương tinh**:
| Sao | Ngũ hành | Vị miếu | Source |
|-----|---------|---------|--------|
| Tử (Vi?) | Mộc | Tý (default) | p0275 r002 + p0286 |
| Văn (Xương) | Mộc | Dần Ngọ Tuất | p0289 |
| Phúc | Thổ | Thân Mão | p0291 |
| Lộc | Mộc | Tỵ Thân | p0292 |
| Ấn | Thổ | Tý Mão Thìn | p0288 |
| Thọ | Thổ | Hợi Dậu Tuất | p0289 |
| Trượng | Mộc | Mùi Hợi Tý Thân | p0293 |
| Khố | Thổ | Mão Tỵ Hợi Ngọ | p0290 |
| Diêu | Thổ | Mão Thìn Tuất Hợi | p0296 |

**9 Âm tinh**:
| Sao | Ngũ hành | Vị miếu | Source |
|-----|---------|---------|--------|
| Quý | Thổ | Dần Thìn Hợi Mão Mùi | p0287 |
| Hồng | Kim | Thìn Sửu Dần | p0291 |
| Dị | Thổ | Sửu Dần Thìn Mùi | p0293 |
| Mao | Thủy | Tý Mão Dần Tuất | p0294 |
| Hư | Thủy | Ngọ Sửu Dậu Hợi | p0287 |
| Quán | Thổ | Mão Tỵ Ngọ Mùi Hợi | p0290 |
| Hình | Hỏa | Dần Ngọ Dậu Tuất | p0296 |
| Nhận | Kim | Thân Tỵ Ngọ Dần Dậu | p0295 |
| Khốc | Kim | Sửu Thân Mão Ngọ | p0298 r013 |

→ **Tại sao mới**: Một số sao **NAME OVERLAP** với chính tinh chính thống (Tử Vi, Văn Xương, Hồng Loan, Lộc Tồn). Nhưng RULE + NGỦ HÀNH có thể khác → cần distinct namespace trong engine.

→ **Engine implication**: `chieu_dom_kinh_18_phi_tinh.json` — separate from `chinh_tinh.json` chính thống.

---

## ⭐⭐⭐⭐ Insight #6 — **Định tử sinh quyết** (PSYCH SAFETY ALERT)

**Source**: Q4 p0274 r008-r009 (verbatim)

Q4 có **quy tắc predict death timing CỤ THỂ**:
> _"Nhược Thiên Khốc chính lâm thân mệnh, cánh dữ Thiên Hư đồng vị, hỉ tinh hựu thả vô lực, kỳ nhân **sinh hạ bất xuất tam ngũ nhật nhi tử**."_

| Pattern | Hậu quả (theo Q4) |
|---------|------------------|
| Thiên Khốc + Thiên Hư đồng vị Thân/Mệnh + cát yếu | Chết 3-5 ngày sau sinh |
| Thấy Thân không thấy Mệnh / ngược lại | Vài năm chết |
| Hình + Đao xung chiếu đồng chủ | Ác tử (chết thảm) |
| Có Thiên Thọ + ẩn đức | Kéo dài. Max 9 chu kỳ Dương = 81 tuổi |

→ **Tại sao DANGER**: Đây là quy tắc paradigm SAI nguy hiểm. Nếu engine surface raw → user có lá số "Thiên Khốc + Thiên Hư" thấy text "chết 3-5 ngày sau sinh" → tổn hại tâm lý.

→ **Engine implication (CEO direction)**:
- **Tích hợp** để CEO test (CEO duyệt G4 option (C) — surface kèm disclaimer mạnh)
- Wrap **"mỗ" pattern** + cảnh báo paradigm
- Iron Rule #6 mandate: KHÔNG phán "anh sẽ chết khi nào"
- Có thể **dùng làm validation negative** — nếu engine output match pattern, **đối chiếu với lá số người sống thật** để chứng minh paradigm SAI

---

## ⭐⭐⭐ Insight #7 — **MATRIX 18 PHI TINH × 12 CUNG** = 216 rules

**Source**: Q4 p0279-p0286 — mỗi cung có rules cho từng 18 sao

VD verbatim p0282 r008 (Cung Thê Thiếp × 18 sao):
> _"Tử (nhập viên chiêu quý mạo chi thê)._
> _Hư (chủ khắc hại, nghi trì miễn tổn)._
> _Quý (chủ chiêu mỹ khiết chi thê)._
> _Ấn (nhân thê trí phú)._
> _Thọ (nghi phu thê niên lão)._
> _Hồng (chiêu mỹ mạo chi thê)._
> _Khố (đắc thê thiếp bất nghi lão)._
> _Lộc (đắc thê quý, kỵ ác tinh xung)._
> _Văn (chiêu thông minh linh lợi chi thê)._
> _..."_

→ Mỗi cung × 18 sao = 18 rules. Tổng **12 × 18 = 216 rules**.

→ **Tại sao mới**: Đây là **dataset structured khổng lồ** mà em chưa extract. Có thể automate parse → 216 entries JSON cho engine quick lookup.

→ **Engine implication**: LLM batch extract `chieu_dom_kinh_12cung_x_18sao.json` (~4-6h pipeline).

---

## ⭐⭐⭐ Insight #8 — **CƯỜNG-NHƯỢC CUNG classification**

**Source**: Q4 p0276 r003 (verbatim)
> _"Phàm cát diệu gia lâm vi phúc mệnh cung, điền trạch thê thiếp quan lộc tứ cung hệ **cao cường**,_
> _nam nữ phúc đức vi **thứ cường**, tài bạch vi **cận cường** dã."_

| Tier | Cung |
|------|------|
| **Cao cường** (sao tốt vào → đại phúc) | Phúc Đức, Mệnh, Điền Trạch, Thê Thiếp, Quan Lộc |
| **Thứ cường** | Nam Nữ (Tử Tức), Phúc Đức |
| **Cận cường** | Tài Bạch |

p0276 r005 (verbatim):
> _"Tướng mạo nô bộc vi **ác nhược** + hãm chi địa, huynh đệ vi **bán hãm cung** (nhàn cực cung)._
> _Tật ách thiên di vi **thứ ác sát**. Cư miếu vi kỳ."_

| Tier | Cung |
|------|------|
| **Ác nhược** | Tướng Mạo (Phụ Mẫu), Nô Bộc |
| **Bán hãm / Nhàn cực** | Huynh Đệ |
| **Thứ ác sát** (nếu miếu thì kỳ diệu) | Tật Ách, Thiên Di |

→ **Tại sao mới**: Engine `chart_strength` hiện chỉ tính per-star (Miếu Vượng Hãm). Q4 dạy **weight per CUNG** — sao tốt ở Phúc/Mệnh nặng hơn sao tốt ở Nô Bộc.

→ **Engine implication**: Update `chart_strength` v2 với palace weights.

---

## ⭐⭐⭐ Insight #9 — **CỬU DƯƠNG + CỬU ÂM rules** (phân tai phúc)

**Source**: Q4 p0275 r002 + r004 (verbatim)
> _"Tử, Văn, Phúc, Lộc, Ấn, Thọ, Trượng, Khố, Diêu... Tại **Dương cung tắc phúc trọng nhi tai khinh**, tại Âm cung tắc phúc khinh nhi tai trọng."_
> _"Quý, Hồng, Dị, Mao, Hư, Quán, Hình, Nhận, Khốc... Tại **Âm cung tắc phúc trọng nhi tai khinh**, tại Dương cung tắc tai trọng nhi phúc khinh."_

→ Quy tắc rõ ràng: **dương sao + dương cung = phúc; âm sao + âm cung = phúc**. Sai mismatch (dương sao + âm cung hoặc ngược lại) = tai.

→ **Tại sao mới**: Em chưa có rule âm-dương cho 18 phi tinh. Quy tắc này HEURISTIC cho engine evaluate chart polarity score.

→ **Engine implication**: Add `cuu_duong_am_polarity.json` cho 18 phi tinh.

---

## ⭐⭐⭐ Insight #10 — **5-6 CÁCH CỤC MỚI** từ Chiếu Đởm Kinh

**Source**: Q4 p0275 r009 (verbatim — list cách cục)

| Cách cục | Pattern | Hậu quả |
|---------|---------|---------|
| **Thân nịch giang hồ cách** (身溺江湖) | Thân/Mệnh tại Hợi/Tý + sao bất nhập miếu | Chìm sông hồ — phiêu bạt |
| **Tử đầu la võng cách** (子头罗网) | Nam nữ tại Tuất/Hợi/Thìn/Tỵ | Đầu con cạm lưới |
| **Thân nhập bần dân cách** (身入贫民) | Thân quan tại Tỵ | Vào nhà nghèo |
| **Ma chúc vi mệnh cách** (磨烛为命) | Mệnh tọa nhận thượng (Kình Dương) | Nến mài làm mệnh — đa thành đa bại |
| **Mệnh tọa phú môn cách** (命坐富门) | Thiên Nhận + Thiên Hư cư Mão | Mệnh ngồi cửa giàu — hung mà không hung |
| **Xà nhập long cung** (蛇入龙宫) | Giờ Mão + Mệnh cung Mão | Rắn vào long cung — đều tốt |

→ **Tại sao mới**: Cách cục Q1 dict hiện có **545 cách**. Q4 Chiếu Đởm Kinh thêm 6 cách (chưa kể matrix 216 rules có thể derive thêm). Cách "Mệnh tọa phú môn" đặc biệt — paradigm **hung-mà-không-hung** giống Thạch Trung Ẩn Ngọc.

→ **Engine implication**: Update `cach_cuc_dict.py` với 6 cách Chiếu Đởm Kinh.

---

## ⭐⭐⭐ Insight #11 — **PHÚ THI 4-CÂU per Phi Tinh** (mỗi sao có 2-4 stanza)

**Source**: Q4 p0287-p0299 — "Lục viết" / "Lục nhật" pattern lặp

Mỗi sao có 2-4 bài thơ phú style 4-7 chữ tóm tắt. Vd Thiên Hư (p0287 r011):
> _"Thiên Hư Sửu Ngọ vị nghi lai, miếu vượng tương phùng bất sinh tai._
> _Từ ngôn cuống tâm bất tu thính, cánh năng mưu đạt phú đa tài."_

VD Thiên Quý (p0288 r003):
> _"Thiên quý tinh danh miếu vượng trung, thân tý thần cập hợi dần cung._
> _Thiếu niên lâm nhã phỉ thanh dự, kim bảng tiêu danh phúc khánh long."_

→ **Tại sao mới**: 18 sao × 2-4 stanza = **~50 phú thi** mà em chưa surface. Đây là **training data tốt cho phê mệnh generator** — LLM học variety phong cách thay vì 1 sample.

→ **Engine implication**: Build `chieu_dom_kinh_phu_thi.json` — 50 stanza per sao. Re-train phê mệnh generator V2 với variety.

---

## ⭐⭐⭐ Insight #12 — **VẬN HẠN ĐỊNH LUẬN** kết quyển (formula Tiểu Hạn riêng)

**Source**: Q4 p0300 r002 (verbatim — line cuối Q4)
> _"Tự Tiểu Hạn đối xung khởi chi nhất cung, an nhất diệu,_
> _Dương nam Âm nữ thuận hành, Âm nam Dương nữ nghịch hành."_

→ **Tại sao mới**: Tiểu Hạn formula chính thống = từ Thân/Mệnh cung. Chiếu Đởm Kinh = **từ ĐỐI XUNG Tiểu Hạn**. KHÁC HOÀN TOÀN.

→ **Engine implication**: Nếu integrate Chiếu Đởm Kinh, có engine `chieu_dom_tieu_han.py` riêng.

---

## ⭐⭐ Insight #13 — Paradigm "BẤT KHẢ CHẤP NHẤT" tái xác nhận

**Source**: Q4 p0299 r018 (verbatim — line gần cuối Q4)
> _"Thập bát tinh chuyển, tại nhân biến thông. **Bất khả chấp nhất**, y thân hội đoạn._
> _Vận hạn đồng thôi, lưu niên tịnh khán."_

(18 sao vận chuyển, tùy người biến thông. KHÔNG nên cứng nhắc một cách. Đại + Tiểu hạn + Lưu niên cùng xem.)

→ **Tại sao mới**: Plan agent dự đoán Iron Rule #6 ("đọc đồng dạng, không predict") — đây là CONFIRM trực tiếp từ kinh điển CHIẾU ĐỞM KINH (kinh phái khác Trần Đoàn) cũng nói cùng paradigm. → **2 kinh điển độc lập đều dạy bất khả chấp nhất**.

→ **Engine implication**: Tử Vi Sage + Chiếu Đởm Sage SOUL phải embed quote này như Iron Rule (nghĩa là PARADIGM-LEVEL).

---

## ⭐⭐ Insight #14 — Cross-link Q3 phú lệnh ↔ Q4 chart

**Source**: Q3 p0180 phú lệnh + Q4 batch 2 chart

Q3 p0180:
> _"Tử Phá Thìn Tuất, quân thần bất nghĩa. **An Lộc Sơn, Triệu Cao mệnh thị dã**."_

Q4 batch 2 (visual inspect chart image):
- **赵高之命** (Triệu Cao): 阴男, 癸卯年正月二十一日戌时生, 土五局 — visual confirmed

→ **Tại sao mới**: Q3 phú lệnh có thể được **chứng minh** bằng Q4 chart. Engine có thể link: user có pattern Tử Phá Thìn Tuất → reference Q4 chart Triệu Cao để verify (nếu chart Q4 match Tử Phá Thìn Tuất, paradigm OK; nếu không, paradigm cần question).

→ **Engine implication**: Layer cross-reference: Q3 phú lệnh → Q4 chart verify.

---

## ⭐⭐ Insight #15 — Q4 reference **"Tục Đạo Tạng"** (续道藏)

**Source**: Q4 p0266 r001 (verbatim)
> _"《Tục Đạo Tạng》 tam quyển bản"_
> _"《Tử Vi Đẩu Số》 quyển chi nhất"_

⚠️ Q4 đột nhiên claim "quyển chi nhất" — CONTRADICT với p0199 "quyển chi tứ". Có thể:
- (a) p0266 INSERT từ Tục Đạo Tạng (3 quyển) — không phải continuation Q4
- (b) Q4 vẫn là quyển 4 nhưng REFERENCE "quyển chi nhất" của bộ khác
- (c) OCR/page marker error

→ **Tại sao mới**: **Tục Đạo Tạng** là bộ kinh Đạo giáo. Tử Vi có root từ Đạo giáo → Q4 đột nhiên cite source Đạo giáo → có thể Tử Vi có **nguồn gốc Đạo giáo sâu hơn** em đã biết. Đáng research thêm.

→ **Engine implication**: Reference Tục Đạo Tạng trong sage SOUL khi nói về paradigm gốc Tử Vi.

---

# Phần 3 — Tóm tắt cho CEO

## 3.1 Em sai chỗ nào (~50% journal cũ)

1. Q4 KHÔNG phải "Khang Tiết Edition" — đó là over-correction
2. Phần 3 Q4 KHÔNG phải "Định thời + Thiên Quán + Tử sinh" — thực ra là 2 KINH PHÁI KHÁC
3. 12 archetypes → thực ra **36 archetypes**
4. 2 phê mệnh templates → thực ra **7 templates**
5. case_studies 8 figures có thể có ⚠️ Cung Toại + Hoàng Bá em bịa (verify needed)

## 3.2 Em phát hiện gì NEW (15 insights ranked)

⭐⭐⭐⭐⭐ — Game-changer paradigm:
- 10 bước methodology Trần Đoàn
- 2 KINH PHÁI KHÁC (Chiếu Đởm Kinh + Nhập Cốt Tiên Kinh)

⭐⭐⭐⭐ — Important new content:
- 36 archetypes typology
- Rectification rules (giờ qua activity + đỉnh đầu)
- 18 Phi Tinh schema parallel
- Định tử sinh quyết (psych safety alert)

⭐⭐⭐ — Useful new content:
- Matrix 216 rules (12 cung × 18 sao)
- Cường-nhược cung classification
- Cửu Dương + Cửu Âm rules
- 5-6 cách cục mới
- ~50 phú thi 4-câu
- Vận hạn định luận formula

⭐⭐ — Nice-to-have:
- Paradigm "bất khả chấp nhất" tái xác nhận
- Cross-link Q3 ↔ Q4 chart
- Tục Đạo Tạng reference

## 3.3 Action tiếp theo (Phase B continue)

- B.2 — `Q4-ENGINE-AUDIT.md` (audit chi tiết 8 modules)
- B.3 — Verify case_studies.json figures (Cung Toại + Hoàng Bá có thật?)
- → Sau Phase B → Phase C REFACTOR (sửa SOUL "Khang Tiết Edition" SAI, etc.) + Phase D BUILD (15 engine modules theo priority)

Em đợi CEO duyệt G7 sau khi đọc reconciliation này.
