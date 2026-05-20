# Q4 Engine Audit — 8 modules đã ship

**Audit date**: 2026-05-20 (Phase B.2)
**Method**: So sánh mỗi module vs evidence từ 6 batches Phase A + `Q4-RECONCILIATION.md`
**Verdict scale**: ✅ OK / ⚠️ NEEDS REFACTOR (specific changes) / ❌ REWRITE (paradigm sai)

---

## M1 — `case_studies.json` + `case_matcher.py`

**Claim**: 2 patterns (Tử Phủ Dần + Tử Phá Thìn Tuất) + 8 historical figures

**Source claim**: Q3 p0180 + Q4 p0257-p0258

### Audit findings

| Field | Verdict | Evidence |
|-------|---------|----------|
| Pattern Tử Phủ Dần | ✅ | p0257 r003 verbatim: _"Tử Vi thủ mệnh tọa Dần phương, Thiên Phủ đồng cung tối diệu"_ |
| Pattern Tử Phá Thìn Tuất | ✅ | Q3 p0180 r002 verbatim + Khang Tiết bổ chú |
| Figure Trác Mậu | ✅ | p0257 VI confirmed |
| Figure Lỗ Cung | ✅ | p0257 VI confirmed |
| Figure Cung Toại | ✅ | p0258 VI verbatim (em NGHI bịa nhưng có thật) |
| Figure Hoàng Bá | ✅ | p0258 VI verbatim |
| Figure Sơ Quảng + Sơ Thụ | ✅ | p0258 VI verbatim "nhị sơ tòng giải tổ" |
| Figure An Lộc Sơn + Triệu Cao | ✅ | Q3 p0180 ZH 安禄山、赵高命是也 |

### Gaps phát hiện

1. **Chỉ 2 patterns trong khi Q4 có ~30 chart figures** (Khổng Tử, Tử Lộ, Lý Tư, Lưu Linh, Hàn Thông... + ~25 khác chưa visual inspect). User có thể "match" Khổng Tử (Mệnh Thân = Mùi/Thân) hoặc Tử Lộ (Mộc nhị cục, Dần giờ) → feature value cao hơn nhiều.
2. **Source ref weak** — figures hiện tại không link tới page+line ID cụ thể trong source (chỉ ghi "Q4 p0257"). Cần ghi `[p0258 r003-l021]` per claim để verify được.

### Verdict
**⚠️ NEEDS EXPANSION + source-ref tightening**

- Action 1: Add Khổng Tử + Tử Lộ patterns (em đã visual inspect chart Q4 batch 1 — birth + ngũ cục đầy đủ)
- Action 2: Add `source_quote_hv` + `source_quote_zh` + `source_ref` (page+r-id) field per figure
- Action 3: Optional — extract 25 chart images remaining trong batch 1-2 band (defer)

---

## M2 — `engine/tu_vi/dau_quan.py`

**Claim**: Đẩu Quân compute formula + interpret 12 cung

**Source claim**: Q2 p0088 + Q3 p0157 (NOT Q4)

### Audit findings

| Aspect | Verdict |
|--------|---------|
| Formula Đẩu Quân | ✅ Verified Q2 p0088 r002-l001 |
| 12-cung interpretation | ✅ |
| Source ref Q4 in code/docs? | ⚠️ Em đã hint Q4 trong commits/journals — should remove |

### Verdict
**✅ OK** (engine logic), nhưng cần **doc cleanup**: SOUL.md / journal references shouldn't link Đẩu Quân to Q4 — đó là Q2+Q3.

---

## M3 — `engine/tu_vi/psychological_safety.py`

**Claim**: 3 patterns (Xương Khúc + năm + Thìn Tuất / Cự Môn × Tý + sát / Phá Quân + Nhật Nguyệt)

**Source claim**: Q1 p0027-p0028 + Q3 p0186 (NOT Q4)

### Audit findings

3 patterns hiện tại đúng nguồn. NHƯNG Q4 có MỘT pattern NẶNG HƠN chưa add:

⚠️ **MISSING — Q4 Định tử sinh quyết** (p0274 r009):
> _"Nhược Thiên Khốc chính lâm thân mệnh, cánh dữ Thiên Hư đồng vị, hỉ tinh hựu thả vô lực, kỳ nhân sinh hạ bất xuất tam ngũ nhật nhi tử."_

CEO direction (G4): **Tích hợp Định tử sinh quyết để test**, wrap "mỗ" pattern.

### Verdict
**⚠️ NEEDS EXPANSION** với 1 pattern Q4

- Action: Add pattern 4 "Định tử sinh quyết" (Thiên Khốc + Thiên Hư + sát ác) với wording cực kỳ careful:
  - ❌ KHÔNG nói "sẽ chết X ngày"
  - ✅ Wording: "Cổ kinh Q4 ghi nhận pattern này — không phải predict, mà gợi mở chăm sóc thân thể đặc biệt"
  - Add disclaimer mạnh + cite verbatim p0274 r009

---

## M4 — `engine/tu_vi/mieu_vuong_ham.py`

**Claim**: Per-star strength score (Miếu/Vượng/Đắc/Lạc/Hãm)

**Source claim**: Q2 p0102 (NOT Q4)

### Audit findings

| Aspect | Verdict |
|--------|---------|
| Logic per-star strength | ✅ |
| Q2 source ref | ✅ |

⚠️ **MISSING — palace-level weight from Q4**:

Q4 p0276 r003-r005 chia 12 cung thành 7 tiers:
- Cao cường (5 cung): Phúc Đức, Mệnh, Điền Trạch, Thê Thiếp, Quan Lộc
- Thứ cường: Tử Tức
- Cận cường: Tài Bạch
- Ác nhược: Tướng Mạo, Nô Bộc
- Bán hãm: Huynh Đệ
- Thứ ác sát (kỳ nếu miếu): Tật Ách, Thiên Di

→ Engine `chart_strength()` hiện chỉ sum per-star score. Q4 dạy nên **weight by palace** (sao tốt ở Phúc/Mệnh nặng hơn sao tốt ở Nô Bộc).

### Verdict
**⚠️ NEEDS EXPANSION** với palace weight

- Action: Add `palace_weights.json` (7 tiers) + update `chart_strength()` multiply per-star score by palace tier weight
- Source: Q4 p0276 r003-r005

---

## M5 — `engine/tu_vi/chinh_tinh.py` v2

**Claim**: 14 chính tinh với schema mở rộng (thuộc đẩu, hóa khí, tướng mạo, tính cách, uy chế, hợp/kỵ, đặc biệt, bias năm sinh)

**Source claim**: Q2 p0103-p0125

### Audit findings

✅ Q2 source ref đúng. 14 chính tinh enrich đúng.

⚠️ **NEW from Q4 — 18 Phi Tinh (kinh khác)**:

Chiếu Đởm Kinh có **18 Phi Tinh** (Tử, Văn, Phúc, Lộc, Ấn, Thọ, Trượng, Khố, Diêu, Quý, Hồng, Dị, Mao, Hư, Quán, Hình, Nhận, Khốc) với ngũ hành riêng. Một số NAME OVERLAP với chính tinh chính thống (Tử Vi, Văn Xương, Hồng Loan, Lộc Tồn) nhưng RULE khác.

→ KHÔNG nên merge vào `chinh_tinh.json`. Cần FILE RIÊNG `chieu_dom_kinh_phi_tinh.json`.

### Verdict
**✅ OK current**, nhưng **cần thêm parallel file** `chieu_dom_kinh_phi_tinh.json` (Phase D)

---

## M6 — `TuViAnalyzer.phe_menh()` LLM generator

**Claim**: Sinh phê mệnh phú thi style + "mỗ" pattern, đa-provider fallback

**Source claim**: Q4 Khang Tiết Edition + 1 sample template p0257

### Audit findings

⚠️ **CLAIM SAI ở SYSTEM prompt** — em viết:
> _"Bạn là bậc trí giả Tử Vi Đẩu Số — đồng tác Trần Đoàn + Khang Tiết."_

→ Sau Phase A em biết "Khang Tiết Edition" là OVER-CORRECTION. Khang Tiết chỉ là header repeated. Sage prompt cần soften.

⚠️ **Training data weak** — chỉ học 1 sample p0257. Q4 có **≥7 phê mệnh templates** (p0257 + p0259 + p0260 + p0261 + p0262 + p0263 + p0264) + ~50 phú thi 4-câu từ 18 Phi Tinh detail. Variety lớn hơn nhiều.

### Verdict
**⚠️ NEEDS REFACTOR**

- Action 1: Update SYSTEM prompt — softer Khang Tiết claim. Quote:
  - OLD: "đồng tác Trần Đoàn + Khang Tiết"
  - NEW: "Trần Đoàn (Tổ chính) + Khang Tiết bổ chú 1-2 chỗ ở Q4 (Thạch Trung Ẩn Ngọc cách + Tử Phá Thìn Tuất)"
- Action 2: Expand training data với 7 phê mệnh templates + 50 phú thi → re-test quality
- Action 3: Embed 10 BƯỚC METHODOLOGY (Insight #1) làm cấu trúc output → 10 sections thay vì 5 ad-hoc

---

## M7 — Sage Tử Vi + Sage Mai Hoa cross-bind ("Khang Tiết bridge")

**Claim**: Khang Tiết = tổ Mai Hoa + co-author Tử Vi Q4 → bridge 2 sage

**Source claim**: Q4 Khang Tiết Edition (em claim 35 lần)

### Audit findings

⚠️ **Bridge metaphor OK** nhưng "co-author 35 lần Khang Tiết" claim SAI. Sau Phase A:
- Khang Tiết thật sự appearance: **3-5 substantive sections** trong Q2-Q3-Q4 (Cự Môn + Đà La + An Lộc Sơn Tử Phá + Thạch Trung Ẩn Ngọc + 1 phê mệnh p0258)
- ~30 occurrences còn lại là **header repeated** trên chart pages → không phải commentary

### Verdict
**⚠️ NEEDS SOFTEN — keep bridge but accurate count**

- Action: SOUL.md `tu-vi-sage` + `mai-hoa-sage`:
  - OLD: "Khang Tiết co-author Q4 (~35 lần)"
  - NEW: "Khang Tiết bổ chú Q2 + Q3 + Q4 ở 4-5 chỗ trọng yếu (Cự Môn, Đà La, An Lộc Sơn Tử Phá, Thạch Trung Ẩn Ngọc, phê mệnh p0258). Bridge paradigm vẫn hiệu lực."

---

## M8 — UI `TuViLaSoPanel.vue` hooks (case studies + phê mệnh + chart strength + safety + cung readings)

**Claim**: 5 UI blocks hooked vào main panel

**Source claim**: Surface deps M1+M3+M4+M6

### Audit findings

| UI block | Source | Verdict |
|----------|--------|---------|
| Case studies match | M1 | ⚠️ Will expand sau M1 refactor |
| Phê mệnh button | M6 | ⚠️ Will improve sau M6 refactor |
| Chart strength block | M4 | ⚠️ Will add palace weights sau M4 refactor |
| Safety check block | M3 | ⚠️ Will add Định tử sinh quyết sau M3 expansion |
| Cung readings expand | (Q1 phú + Q3 sao×cung) | ✅ OK (không phụ thuộc Q4) |

### Verdict
**⚠️ NEEDS UPDATE downstream after M1/M3/M4/M6 refactor**

- All UI blocks sẽ tự update khi engine refactor done. Không cần thay UI structure.

---

## Tổng kết Audit — 8 modules

| Module | Verdict | Action |
|--------|---------|--------|
| M1 case_studies | ⚠️ Expansion + source-ref tighten | 2h |
| M2 dau_quan | ✅ OK (doc cleanup only) | 15min |
| M3 psychological_safety | ⚠️ Add Định tử sinh quyết | 2h (careful) |
| M4 mieu_vuong_ham | ⚠️ Add palace weights | 1h |
| M5 chinh_tinh v2 | ✅ OK (parallel Phi Tinh file Phase D) | 0h now |
| M6 phe_menh LLM | ⚠️ Refactor SYSTEM prompt + 7 samples training | 3h |
| M7 Sage SOUL | ⚠️ Soften Khang Tiết claims | 30min |
| M8 UI | ⚠️ Auto-update after engine refactor | 0h now |

→ **Total Phase C REFACTOR effort: ~9h** + downstream UI tests.

---

## Critical findings

1. ✅ **case_studies.json KHÔNG có figure bịa** (B.3 verify) — Cung Toại + Hoàng Bá thực sự ở p0258. Em đã lo lắng vô căn cứ.
2. ⚠️ "Khang Tiết Edition" thesis trong M6/M7 cần soften (nhưng bridge paradigm vẫn OK)
3. ⚠️ Q4 có **15 NEW insights** chưa surface vào engine — bulk work cho Phase D BUILD
4. ⚠️ Định tử sinh quyết (M3 expansion) cần **psychological safety wrap CAO** — không hù dọa

---

## Phase B COMPLETE

- ✅ B.1 — `Q4-RECONCILIATION.md` (15 NEW insights + claim audit)
- ✅ B.2 — `Q4-ENGINE-AUDIT.md` (this file)
- ✅ B.3 — case_studies.json figure verification (no fakes)

→ Sẵn sàng cho **Phase C REFACTOR** (sửa 6 modules nhỏ ~9h) hoặc **Phase D BUILD** (15 new insights → engines).

CEO duyệt G7 sau khi đọc.
