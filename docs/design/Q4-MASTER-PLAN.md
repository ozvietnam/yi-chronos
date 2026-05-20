# Q4 MASTER PLAN — Evidence-Based Rebuild

**Tác giả**: Plan agent (rà soát độc lập, không skim)
**Ngày**: 2026-05-20
**Mục đích**: CEO yêu cầu kế hoạch dựa trên evidence sau khi em (Claude) admit đã skim Q4 + claim sai scope.

---

## 0. Executive Summary

CEO đã đúng khi nghi ngờ Q4 work. Plan agent verify bằng `python3` đếm character thực tế trên 102 trang OCR:

**Reality check khắc nghiệt** (objective evidence, không phải skim):
- Toàn Q4 = **72,766 ký tự** `text_vi` (rất nhỏ — chỉ ~1.5× một journal hiện tại)
- **p0199-p0256 (58 trang) = 1,473 ký tự total** = TRUNG BÌNH 25 ký tự/trang. Đây gần như toàn diagram/chart pages, mỗi trang chỉ có **một dòng header** ("Khang Tiết thuyết Dịch toàn thư" / "Tử Vi Đẩu số" v.v.) lặp đi lặp lại
- **p0257-p0265 (9 trang) = 14,013 ký tự** — phê mệnh templates (đã đọc sâu)
- **p0266-p0275 (10 trang) = 17,627 ký tự** — định thời khắc + thiên quán (đã skim)
- **p0276-p0300 (25 trang) = 39,653 ký tự** — tứ hóa phú thi + tướng mạo + tổng kết (CHƯA đọc)

**Hệ quả nặng**: claim "Q4 là Khang Tiết Edition với 30+ Khang Tiết refs" trong journal hiện tại có rủi ro **đếm header lặp lại làm refs commentary**. Engine đã build dựa trên claim đó → cần verify từng cái có grounded vào text thực không.

**Critical Risk R8**: 58 sparse pages p0199-p0256 có thể chứa **chart figures (60 lá số mẫu)** mà OCR không bắt được. Nếu R8 đúng → **ledger cũ "Lá Số Cổ Kim 60+ case studies" thực sự đúng**, journal "Khang Tiết Edition" là OVER-CORRECTION SAI.

---

## 1. Q4 Actual Content Map — Evidence Before Claims

### 1.1 Mật độ thực tế (đo bằng `text_vi` char count)

| Band | Pages | Total chars | Avg chars/page | Density |
|------|-------|-------------|----------------|---------|
| p0199-p0256 | 58 | 1,473 | 25 | **Sparse — headers/diagrams** |
| p0257-p0265 | 9 | 14,013 | 1,557 | Dense — phê mệnh |
| p0266-p0275 | 10 | 17,627 | 1,763 | Dense — định thời + thiên quán |
| p0276-p0300 | 25 | 39,653 | 1,586 | Dense — tứ hóa + tổng kết |
| **TOTAL Q4** | **102** | **72,766** | **713** | — |

### 1.2 10-batch plan (revised by density)

| Batch | Pages | Est. chars | Effort | Focus |
|------:|-------|-----------:|-------|-------|
| B1 | p0199-p0208 | ~200 | 15 min | Verify: sparse = chỉ headers? Note diagram presence (R8 check) |
| B2 | p0209-p0218 | ~400 | 15 min | Same — verify "Khang Tiết" recurring là header hay nội dung |
| B3 | p0219-p0228 | ~250 | 15 min | Same |
| B4 | p0229-p0238 | ~150 | 15 min | Same |
| B5 | p0239-p0248 | ~200 | 15 min | Same |
| B6 | p0249-p0258 | ~3,400 | 45 min | TRANSITION — Phê mệnh sample 1 bắt đầu p0257 |
| B7 | p0259-p0268 | ~12,500 | 60 min | Phê mệnh sample 2 + Khang Tiết duyệt + định thời khắc lệ |
| B8 | p0269-p0278 | ~16,500 | 60 min | Thiên Quán Phân Cung 12 archetypes + định tử sinh |
| B9 | p0279-p0288 | ~16,000 | 60 min | Tướng mạo + thân cung + cung Phụ Mẫu rules |
| B10 | p0289-p0300 | ~23,500 | 75 min | Tứ Hóa phú thi + tổng kết |

**Tổng READ effort**: ~6 giờ thuần đọc + note-taking (vs 15min em đã làm khi skim).

**Output mỗi batch**: `docs/design/tu-vi-q4-batch-{N}.md`, 200-400 chữ, gồm:
1. Pages covered
2. Section headers detected (verbatim, không paraphrase)
3. Key paradigm/structural insights
4. Structured data extractable (JSON candidates)
5. Engine implications (suggestion only — chưa build)
6. **Direct quote citations (with page+r-id) cho mỗi claim**
7. **Reconciliation note** vs `tu-vi-tham-nhuan-quyen-4.md` hiện tại

---

## 2. Existing Engine/UI Audit — Đúng/Sai/Cần refactor

### 2.1 Module audit table

| # | Module | Claimed source | Evidence reality | Verdict (preliminary) |
|---|--------|---------------|------------------|----------------------|
| M1 | `case_matcher.py` + `case_studies.json` | Q4 p0257-p0258 + Q3 p0180 | Tử Phủ Dần OK ✓. **Cung Toại + Hoàng Bá trong JSON KHÔNG có trong journal — em tự bịa?** | NEEDS VERIFY figures |
| M2 | `dau_quan.py` | Q2 p0088 + Q3 p0157 | Source Q2/Q3, không phải Q4 | OK |
| M3 | `psychological_safety.py` | Q1 + Q3 patterns | Source Q1/Q3, không phải Q4 | OK |
| M4 | `mieu_vuong_ham.py` | Q2 p0102 | Source Q2 | OK |
| M5 | `chinh_tinh.py` v2 | Q2 enrichment | Source Q2 | OK |
| M6 | `phe_menh()` LLM | Q4 phú thi + "mỗ" pattern | Sample đã đọc p0257-p0258 ✓. SOUL prompt claim "Q4 Khang Tiết Edition" — **depends on R8** | NEEDS VERIFY |
| M7 | Sage cross-bind "Khang Tiết bridge" | Khang Tiết co-author Q4 | **Depends on R8** | NEEDS VERIFY |
| M8 | UI TuViLaSoPanel hooks | Surface deps M1+M6 | Same verdicts downstream | NEEDS VERIFY |

### 2.2 Journal claim audit (11 key claims)

| # | Claim | Status |
|---|-------|--------|
| C1 | "Q4 = Khang Tiết Edition" | LIKELY FALSE (58/102 sparse) |
| C2 | "Khang Tiết 30+ refs Q4" | LIKELY FALSE (đếm header lặp) |
| C3 | "Phần 1: Khang Tiết Kim thư 30+ sections" | LIKELY FALSE |
| C4 | "Sample 1 Tử Phủ Dần p0257" | ✅ confirmed |
| C5 | "Sample 2 Khang Tiết duyệt p0258" | NEEDS VERIFY |
| C6 | "Định thời khắc lệ p0267" | ✅ confirmed |
| C7 | "Thiên Quán Phân Cung p0271" | ✅ confirmed |
| C8 | "8 cases lịch sử Q3+Q4" | NEEDS VERIFY each name |
| C9 | "Tứ Hóa Q4 phụ lục p0287-p0294" | NEEDS VERIFY |
| C10 | "Định tử sinh quyết p0274" | NEEDS VERIFY |
| C11 | "Khang Tiết LẦN CUỐI p0294" | NEEDS VERIFY |

→ **3 confirmed, 6 needs verify, 3 likely false**. **~27% rủi ro fabrication trên 11 key claims** — đúng như CEO nghi ngờ.

---

## 3. Gap Analysis — Candidates (sau READ + VERIFY)

| Candidate | Source band | Risk if skip |
|-----------|------------|-------------|
| **Thiên Quán Phân Cung typology engine** | p0271-p0273 | HIGH — feature differentiator |
| **Định thời khắc rectification** | p0266-p0270 | MEDIUM (overlap birth_hour_quiz v2) |
| **Tứ Hóa phú thi reading** | p0287-p0294 | MEDIUM (enrichment) |
| **Định tử sinh quyết** | p0274 | HIGH RISK if careless — psych safety |
| **Tướng mạo cung rules** | p0286-p0288 | LOW (nice-to-have) |

---

## 4. Phased Build Plan — Ordered

```
PHASE A — READ (mandatory first, ~6h, 10 batches)
   ↓ G1-G10 (CEO duyệt sau mỗi batch)
PHASE B — VERIFY (~3h)
   ↓ G11
PHASE C — REFACTOR (only if B finds issues, 4-8h)
   ↓ Gates per task
PHASE D — BUILD new features (ordered, ~23h sequential)
   ↓ Gates per task
```

### Phase D tasks (post-VERIFY)

| Task | Depends on | Effort | Acceptance |
|------|-----------|--------|-----------|
| D1. `thien_quan_typology.json` | B8 + verify | 3h | 12 entries with verbatim citations |
| D2. `thien_quan_engine.py` | D1 | 2h | Unit test pass |
| D3. `ThienQuanTypology.vue` | D2 | 3h | Renders for founder chart |
| D4. `dinh_thoi_khac_rules.json` | B7 | 2h | Loaded + smoke test |
| D5. Birth hour quiz v3 alignment | D4 | 2h | Existing quiz still works |
| D6. `tu_hoa_phu_thi.json` | B10 | 4h | ~50+ entries verbatim |
| D7. Tứ Hóa phú thi UI overlay | D6 | 3h | Each hóa expandable |
| D8. Tướng mạo flag | B9 | 2h | Banner if Phụ Mẫu has Dị Hình Đao |
| D9. (Conditional) Khang Tiết sections index | B1-B5 verify | 2h | Skip if R8 confirms diagram-only |
| D10. Update LEDGER Q4 title | All B | 30min | Reflect actual content |

---

## 5. CEO Checkpoint Gates

| Gate | After | What CEO sees | What CEO approves |
|------|-------|---------------|-------------------|
| G1-G10 | Each batch | `tu-vi-q4-batch-{N}.md` (200-400 chữ) | Quote citations đầy đủ → tiếp B(N+1) |
| G11 | After B (VERIFY) | `Q4-RECONCILIATION.md` + audit M1-M8 | Refactor scope cho Phase C |
| G12+ | Each REFACTOR/BUILD task | Diff + smoke test + UI screenshot | Approve before next |

**Rule**: KHÔNG auto-approve. CEO duyệt explicit.

---

## 6. Risk Register

| Risk | Prob | Impact | Mitigation |
|------|------|--------|-----------|
| R1: Khang Tiết Edition thesis collapses (refs = headers) | HIGH (>60%) | HIGH | Softer wording sau VERIFY |
| R2: case_studies.json fabricated figures (Cung Toại + Hoàng Bá) | MEDIUM | MEDIUM | Remove unverified; add source quotes |
| R3: Em skim batch instead of read | MEDIUM | HIGH | Mỗi report PHẢI cite verbatim + page+r-id |
| R4: OCR lỗi (sparse pages có diagram text) | MEDIUM | LOW-MEDIUM | Note diagram per batch |
| R5: Time overrun | MEDIUM | LOW | OK overrun — quality > speed |
| R6: Refactor break existing UI | LOW-MEDIUM | MEDIUM | Atomic + rollback per task |
| R7: New extracts drift from "mỗ" paradigm | MEDIUM | HIGH | Anti-predict guards per engine |
| **R8: p0199-p0256 chứa 60+ chart figures** (OCR missed) | LOW-MEDIUM | HIGH — original ledger title đúng, journal sai | **B1-B5 inspect PDF visually**, không chỉ OCR text |

---

## 7. Working Discipline (em đề xuất CEO ratify)

1. **No claim without verbatim quote** — every Q4 statement kèm `[page r-id: "..."]` citation
2. **Diagram blindness disclosure** — mỗi batch ghi rõ "PDF pages X-Y có diagram em chưa visual-inspect"
3. **Reconciliation honesty** — Q4-RECONCILIATION.md: ✅ confirmed / ✏️ corrected / ❌ retracted per claim
4. **No engine work mid-READ** — Phase A và B tách khỏi C/D
5. **Atomic commits** — mỗi batch/task = 1 commit
6. **Snapshot before refactor** — `git tag pre-q4-refactor` trước Phase C

---

## 8. Deliverables Checklist

**Phase A**:
- [ ] `docs/design/tu-vi-q4-batch-1.md` through `batch-10.md` (10 files)

**Phase B**:
- [ ] `docs/design/Q4-RECONCILIATION.md`
- [ ] `docs/design/Q4-ENGINE-AUDIT.md`

**Phase C** (conditional): Refactor commits per finding

**Phase D**: D1-D10 commits as approved

---

## Critical Files

- `docs/design/tu-vi-tham-nhuan-quyen-4.md` (existing journal — needs reconciliation)
- `data/tu_vi/case_studies.json` (audit + likely figure removal)
- `engine/tu_vi/analyzer.py` (`phe_menh` SYSTEM prompt — adjust claim wording post-VERIFY)
- `data/yi_publishing/translations/tuvidauso-zh/p0257/` → `p0300/` (44 dense pages = actual reading target)
- `data/published/tu-vi-q4-la-so-co-kim.pdf` (visual inspect for R8)
