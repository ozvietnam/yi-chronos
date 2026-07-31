# GAP ANALYSIS + ROADMAP — Backend Tử Vi "nhai gọn 1 lá số bất kỳ"

**Ngày**: 2026-06-10
**Trạng thái**: Phase Data đã dày (~2700 atoms / 4 hệ phái). Phase Engine + UI CHƯA wire.

---

## 🔄 CẬP NHẬT 2026-07-17 — Phase A/B/C/D thực ra ĐÃ XONG, doc này bị stale

Rà lại (yêu cầu "sang khối gap-analysis Tử Vi") phát hiện: **toàn bộ Phase A→D bên
dưới đã được build + wire trong commit `9410bf03` (auto-sync 2026-06-27)** — 17 ngày
sau ngày viết doc này — nhưng doc chưa từng được cập nhật để đóng dấu DONE. Kết quả:
đọc doc từ đầu sẽ tưởng còn ~1.6M token / 2.5 phiên việc, trong khi thực tế còn lại
rất nhỏ.

**Đối chiếu thực tế từng Mảng:**

| Mảng | Doc nói | Thực tế 2026-07-17 |
|---|---|---|
| 2 — Paradigm Engine (6 hàm) | ❌ chưa có | ✅ `engine/tu_vi/paradigm/` — **7 hàm** (thêm `to_hop_cung`/`giap_cung`/`muon_sao` ngoài 6 hàm gốc), đủ nguồn trích dẫn. **Chưa có test nào** cho tới hôm nay — viết 34 test, phát hiện + sửa 1 bug thật (xem dưới). |
| 3 — Mapping CUNG_SAO | 🔴 blocker, 14/168 tĩnh | ✅ `engine/tu_vi/cung_sao_mapping.py` — **live query auto-gen** (không phải bảng tĩnh), phủ **8 sách** (4 gốc + `tu-vi-dau-so-toan-thu-zh`, `tuvi-bon-ba-tiktok`, `tu-vi-huy-tuan-tiktok`, `nguyet-do-so-menh-tiktok`), cache module-level, lọc `anti_paradigm`/`quan_diem` khỏi luận tích cực. |
| 4 — Cross-School Orchestrator | 🟡 needed | ✅ `engine/tu_vi/cross_school.py` (346 dòng) — `luan_sao_cung`, `luan_to_hop_cung`, `detect_paradigm_warnings` (gọi cả 7 hàm paradigm). |
| 5 — Output Filler v2 | 🔴 blocker | ✅ `engine/atomization/output_filler_v2.py` (369 dòng) — `render_3_layer()` dùng paradigm + cross_school + mapping đúng như spec doc. |
| — API | (không nhắc) | ✅ `api/tu_vi_3layer.py` (955 dòng, **router riêng**, đã `include_router` trong `api/main.py`) — `/api/tu-vi/3-layer`, `/3-layer/from-birth`, `/3-layer/narrative`, `/3-layer/chu-de(-sau)`, `/3-layer/gia-vi`, `/3-layer/feedback`, `/hop-hon`, `/thien-luong`, `/cung-sau`, `/duyen`, `/gia-dao`, `/3-layer/founder-demo`, ... |
| 6 — UI TuViLaSoPanelV2 | 🟡 needed | ✅ `client/webapp/src/components/TuVi3LayerPanel.vue` — **đã mount** bên trong `TuViLaSoPanel.vue:1745`, gọi đủ endpoint trên. |
| 7 — Founder Verify Workflow | 🟡 needed | ✅ **ĐÃ CÓ, qua route khác không như doc mô tả**: `AtomVerifyPanel.vue` (260 dòng, xây 2026-06-26) + `api/atomization.py` (`POST /verify/{atom_id}`, `POST /verify-bulk`) — mount ở tab `atom-verify` trong `App.vue`, browse theo sách/mục, **duyệt hàng loạt**, đúng 4 sách Tử Vi cần (`BOOK_VI` khớp chính xác danh sách trong roadmap). **KHÔNG dùng** `api/atoms_verify.py` (`/api/atoms/verify` + `/api/atoms/pending`, xây riêng, đăng ký router trong `main.py`) — verify 2026-07-17: **0 caller ở đâu cả (không UI, không script, không test)** → nhiều khả năng là bản nháp trùng chức năng bị bỏ quên. Đề xuất: giữ nguyên (không xóa mù) — anh quyết xoá hay giữ làm API hẹp cho automation sau. |

**Bug thật tìm thấy khi viết test cho Mảng 2** (không có trong doc gốc, vì doc gốc
viết TRƯỚC khi code tồn tại): `engine/tu_vi/paradigm/nhan_cung.py` dùng canonical
`"ty"` (=Tý) cho vị trí Nhân Cung của Thiên Lương/Thiên Cơ/Phá Quân — nhưng theo
đúng quy ước canonical toàn hệ thống (`la_so_input_builder.CHI_VI_TO_CANON` v.v.)
thì `"ty"` = Tý và `"ti"` = Tỵ là **2 chi khác nhau**; comment nguồn trong chính
file đó ghi rõ "ở Tỵ". Bug này chạy thật (`cross_school.detect_paradigm_warnings`
→ `output_filler_v2.render_3_layer` → API `/api/tu-vi/3-layer` user-facing) — khiến
**bỏ sót cảnh báo** khi sao thật ở Tỵ, và **báo giả** khi sao ở Tý. Đã sửa (3 dòng)
+ 34 test cho toàn bộ package paradigm (`tests/test_tu_vi_paradigm_engine.py`).

**Còn lại CHƯA verify được từ container này** (thiếu `data/yi_wiki/wiki.sqlite3` —
DB không theo git/CI, chỉ sync qua VPS theo CLAUDE.md): chất lượng thật của output
3-layer trên lá số founder — cần chạy `POST /api/tu-vi/3-layer/founder-demo` (hoặc
`from-birth`) trên máy có DB thật để mắt thấy văn bản sinh ra có đúng "chuyện về
anh / vì sao / sách cổ nói" như acceptance test §Goal mô tả hay không. Đây là việc
duy nhất còn thật sự cần làm trong roadmap gốc — không phải build gì mới, mà là
**QC bằng mắt trên dữ liệu thật**.

**Kết luận**: Phase A→D coi như DONE về mặt kỹ thuật (code + wiring + giờ có test).
Effort thật còn lại ≈ 1 lượt QC thủ công trên máy có DB, không phải "~1.6M
tokens / 2.5 phiên" như ước tính gốc.

---

## 🎯 GOAL ĐỊNH NGHĨA RÕ

> Anh đưa BẤT KỲ 1 lá số (year/month/day/hour/gender) → Em sinh OUTPUT 3-Layer cho user:
> - **Lớp 1: Chuyện về anh** — narrative cá nhân hóa
> - **Lớp 2: Vì sao** — nguyên lý đằng sau (paradigm engine giải thích)
> - **Lớp 3: Sách cổ nói** — citation 4 hệ phái có agree/disagree

**Acceptance test**: User input lá số founder (1988-06-05 23:30 Nam) → Output đầy đủ:
- Bậc tuổi Mậu Thìn (paradigm Thiên Lương: bậc 4 — trở lực)
- Mệnh chủ Vũ Khúc Mệnh tại Tỵ (paradigm Trần Đoàn: NHÂN CUNG → giảm 80%)
- 3 vòng lớn (Lộc Tồn Mậu / Thái Tuế Thìn / Tràng Sinh Mậu)
- Cách cục (nếu có): "Cự Nhật / Phủ Tướng triều viên / ..."
- Cross-school: TCQ2 nói gì, Trần Đoàn nói gì, Thiên Lương nói gì, Hàm Số nói gì
- Founder verify: atom nào anh đã ✅, atom nào còn ⚠

---

## 📊 BẢNG GAP ANALYSIS 6 MẢNG

### MẢNG 1 — Atom Data (✅ ĐỦ DÀY, còn QC)

| Sách | Atoms | confidence | Founder verified |
|---|---:|---|---|
| TCQ2 Cung Mệnh | 200 | 0.85 | 0% |
| Toàn Thư Trần Đoàn | 1153 | 0.85 | 0% |
| Thiên Lương | ~700 | 0.85 | 0% |
| Hàm Số | ~650 | 0.85 | 0% |
| **TỔNG** | **~2700** | | |

**Còn THIẾU**:
- ❌ 12 cung khác của TCQ2 (mới có Cung Mệnh) — ~2000 atoms tiềm năng
- ❌ Founder verify CHƯA chạy — tất cả atoms confidence 0.85, không có atom 0.95+
- ⚠ Atom data CÓ NHƯNG CHƯA WIRE INTO ENGINE

**Effort còn lại**: ~3 phiên × 500k tokens = bổ sung 12 cung TCQ2 + verify workflow.

---

### MẢNG 2 — Paradigm Engine (❌ CHƯA CÓ, blocker CỨNG)

#### 2.1 — `nhan_cung_check(sao, cung) → bool` 🔴
**Nguồn**: Trần Đoàn Toàn Thư p63-64 (S4)
**Data**: 8 trường hợp Nhân Cung đã capture trong atoms tdts.S4
**Cần code**: ~50 dòng Python, lookup dict
**Effort**: 30 phút
**Token**: ~20k

```python
NHAN_CUNG = {
  "tu_vi": ["ty", "thin", "hoi"],
  "tham_lang": ["dan", "than"],
  "thien_tuong": ["thin", "tuat"],
  "that_sat": ["thin", "hoi"],
  "thien_luong": ["ty"],
  "thien_co": ["ty"],
  "pha_quan": ["ty", "than"],
  "vu_khuc": ["than"],
}
def is_nhan_cung(sao: str, cung: str) -> tuple[bool, str]:
    """Return (is_nhan_cung, citation)"""
    return cung in NHAN_CUNG.get(sao, []), "tdts.S4.Q25-Q33"
```

#### 2.2 — `bac_tuoi_can_chi(can, chi) → int (1-5)` 🔴
**Nguồn**: Thiên Lương Nghiệm Lý S1 (p7-10)
**Data**: 5 bậc tuổi đã trong atoms tlnl.S1
**Cần code**: ~80 dòng (sinh-khắc Ngũ Hành of Can + Chi)
**Effort**: 45 phút
**Token**: ~25k

```python
CAN_NGU_HANH = {"giap": "moc", "at": "moc", "binh": "hoa", ...}
CHI_NGU_HANH = {"ty": "thuy", "suu": "tho", "dan": "moc", ...}
NGU_HANH_SINH_KHAC = {("moc","hoa"): "sinh", ("kim","moc"): "khac", ...}

def bac_tuoi(can: str, chi: str) -> tuple[int, str]:
    """Bậc 1: Can sinh Chi (phúc lớn)... Bậc 5: Chi khắc Can (nghịch cảnh)"""
    can_h, chi_h = CAN_NGU_HANH[can], CHI_NGU_HANH[chi]
    if can_h == chi_h: return 2, "vững chắc"
    rel = NGU_HANH_SINH_KHAC.get((can_h, chi_h))
    if rel == "sinh": return 1, "phúc lớn"
    if rel == "khac": return 4, "trở lực"
    rel_rev = NGU_HANH_SINH_KHAC.get((chi_h, can_h))
    if rel_rev == "sinh": return 3, "may > thực lực"
    if rel_rev == "khac": return 5, "nghịch cảnh"
    return 2, "vững chắc"
```

#### 2.3 — `tam_hop_loc_ton(can) → list[chi]` 🔴
**Nguồn**: Thiên Lương S1 p9
**Data**: 10 can → 4 tam hợp đã trong tlnl.S1.Q62-Q65
**Effort**: 15 phút
**Token**: ~10k

```python
LOC_TON_TAM_HOP = {
  "giap": ["dan", "ngo", "tuat"],   # Lộc Tồn tại Dần
  "at":   ["mao", "hoi", "mui"],
  "binh": ["ti", "tuat", "thin"],   # placeholder — em check sách
  # ... 10 can
}
```

#### 2.4 — `bat_phap_classify(menh_atoms) → str (4 cách)` 🟡
**Nguồn**: Trần Đoàn S1 (p19-20)
**Data**: Bát Pháp 8 lối đã trong atoms tdts.S1
**Cần code**: ~100 dòng (detect Khoa/Quyền/Lộc/Quý vs Hỏa/Linh/Dương/Đà trong tam phương + xung chiếu)
**Effort**: 1h
**Token**: ~40k

#### 2.5 — `thap_du_eval(menh, ban_phuong, hop_phuong, lan_phuong, xung_chieu) → dict` 🟡
**Nguồn**: Trần Đoàn S1 (p19)
**Data**: Thập Dụ 10 điều đã trong atoms tdts.S1.Q43-Q52
**Effort**: 45 phút
**Token**: ~30k

#### 2.6 — `ba_vong_lon(can, chi, gender) → dict[loc_ton, thai_tue, trang_sinh]` 🟡
**Nguồn**: Thiên Lương S1 + S6
**Data**: 3 vòng paradigm trong tlnl.S1 + tlnl.S6
**Effort**: 1h
**Token**: ~50k

**TỔNG MẢNG 2**: 6 functions, ~4h effort, ~175k tokens

---

### MẢNG 3 — Mapping CUNG_SAO_TO_SECTION (🔴 BLOCKER CỨNG)

#### Hiện trạng
- TCQ2: 14/168 mappings (CHỈ Cung Mệnh)
- Toàn Thư: 0/168
- Thiên Lương: 0/168
- Hàm Số: 0/168

#### Cần
672 mappings (4 sách × 14 sao × 12 cung). NHƯNG NHIỀU SÁCH KHÔNG có atom đầy đủ cho mọi cung — em fall back: 1 mapping = `[]` nếu không có atom.

#### Approach: SUB-AGENT AUTO-GENERATE
Spawn 4 sub-agents (1 per sách), mỗi sub-agent:
1. Query DB: lấy atoms của sách đó, group theo (sao, palace) qua tags
2. Output: mapping `(sao, cung) → list[section_id, atom_ids]`

**Effort**: ~1.5h (1 sub-agent run + verify)
**Token**: ~200k (4 sub-agents parallel)

---

### MẢNG 4 — Cross-School Orchestrator (🟡 NEEDED)

#### Hiện trạng
- ❌ Chưa có `engine/tu_vi/cross_school.py`
- Atoms có tag `school:tran_doan`, `school:thien_luong`, etc. nhưng chưa được orchestrate

#### Cần build
```python
# engine/tu_vi/cross_school.py
class CrossSchoolOrchestrator:
    def luan_sao_cung(self, sao: str, cung: str) -> CrossSchoolView:
        """
        Return:
          {
            "agree": [<atoms 4 hệ phái cùng nói>],
            "disagree": [
              {"school": "tran_doan", "atoms": [...]},
              {"school": "thien_luong", "atoms": [...]},
              ...
            ],
            "unique_per_school": {school: [atoms only that school]}
          }
        """
        ...
    
    def detect_paradigm_warnings(self, la_so: LaSo) -> list[Warning]:
        """
        Run paradigm engine + return list các cảnh báo:
          - Nhân Cung warning (Trần Đoàn)
          - Bậc tuổi nghịch cảnh (Thiên Lương)
          - Tuần Triệt xấu vs có lợi (cross-school)
          - Tam Hóa Liên Châu (Thiên Lương)
          - etc.
        """
```

**Logic merge agree/disagree**:
- Atoms cùng `tags["star:X", "palace:Y"]` → group
- Nếu commentary `viet_thuan` similarity > 0.7 → AGREE
- Nếu CONFLICT keywords (vd "thuần xấu" vs "có lợi ích") → DISAGREE

**Effort**: 3-4h
**Token**: ~200k

---

### MẢNG 5 — Output Filler v2 (🔴 BLOCKER CỨNG)

#### Hiện trạng
`engine/atomization/output_filler.py` — v1, mới render 14 mappings TCQ2 Cung Mệnh, không có:
- ❌ Paradigm engine integration
- ❌ Cross-school orchestrator
- ❌ 4 sách integration

#### Cần build `output_filler_v2.py`

```python
class OutputFillerV2:
    def __init__(self):
        self.paradigm = ParadigmEngine()  # Mảng 2
        self.cross_school = CrossSchoolOrchestrator()  # Mảng 4
        self.mappings = load_mappings()  # Mảng 3
    
    def render(self, la_so: LaSo) -> ThreeLayerOutput:
        # Step 1: Detect paradigm warnings
        warnings = self.paradigm.detect_warnings(la_so)
        # → Nhân Cung warning (Vũ Khúc-Thân), Bậc tuổi 4 (Mậu Thìn), ...
        
        # Step 2: Iterate qua 12 cung
        per_cung_output = {}
        for cung in la_so.cungs:
            for sao in cung.chinh_tinh:
                atoms_per_school = self.mappings.lookup(sao, cung.name)
                cross_view = self.cross_school.luan_sao_cung(sao, cung.name)
                per_cung_output[cung.name][sao] = self.render_3_layer(
                    cross_view, warnings, la_so.user_context
                )
        
        # Step 3: Render 3-Layer
        return ThreeLayerOutput(
            lop_1_chuyen_ve_anh=self.render_narrative(per_cung_output, la_so),
            lop_2_vi_sao=self.render_nguyen_ly(per_cung_output, warnings),
            lop_3_sach_co=self.render_citations(per_cung_output, cross_view),
        )
    
    def render_3_layer(self, cross_view, warnings, user_context):
        """Render 1 (sao × cung) thành 3-layer dùng LLM."""
        prompt = f"""
        User: {user_context}
        Cross-school view: {cross_view}
        Warnings: {warnings}
        
        Output 3-layer:
        Lớp 1 (Chuyện về anh): narrative cá nhân hóa
        Lớp 2 (Vì sao): paradigm explanation
        Lớp 3 (Sách cổ nói): citation 4 hệ phái
        """
        return LLM.call(prompt)
```

**Effort**: 6-8h
**Token**: ~400k (LLM calls test + iterate)

---

### MẢNG 6 — UI TuViLaSoPanel v2 (🟡 NEEDED)

#### Hiện trạng
`client/webapp/src/components/TuViLaSoPanel.vue` — v1, render 10 sections phê mệnh cũ. Không có:
- ❌ Section "Cảnh báo paradigm" (Nhân Cung, Bậc tuổi, ...)
- ❌ Section "Cross-school view" (4 cột)
- ❌ Section "3 vòng lớn" (Lộc Tồn / Thái Tuế / Tràng Sinh map)
- ❌ Tooltip Hán-Việt cho thuật ngữ

#### Cần build v2

```vue
<TuViLaSoPanelV2>
  <!-- Section 1: Tổng quan lá số -->
  <SectionLaSoOverview :la-so="laSo" />
  
  <!-- Section 2: Bậc tuổi Can-Chi (Thiên Lương) -->
  <SectionBacTuoi :bac="paradigm.bac_tuoi" />
  
  <!-- Section 3: 3 Vòng lớn map (Lộc Tồn + Thái Tuế + Tràng Sinh) -->
  <Section3VongLon :vongs="paradigm.ba_vong" />
  
  <!-- Section 4: Cảnh báo paradigm (Nhân Cung, Bát Pháp, Thập Dụ) -->
  <SectionWarnings :warnings="paradigm.warnings" />
  
  <!-- Section 5: Cross-school view per cung -->
  <SectionCrossSchool :view="crossSchoolView" />
  
  <!-- Section 6: 3-Layer output cho user -->
  <Section3Layer :output="threeLayerOutput" />
  
  <!-- Section 7: Founder verify checklist -->
  <SectionFounderVerify v-if="isOwner" />
</TuViLaSoPanelV2>
```

**Effort**: 8-10h
**Token**: ~300k (Vue components + CSS + test)

---

### MẢNG 7 — Founder Verify Workflow (🟡 NEEDED, GIẢM ẨU)

#### Hiện trạng
- ❌ Tất cả 2700 atoms confidence 0.85, founder_verified=0
- ❌ Workflow verify chưa có UI

#### Cần build
- Admin UI: list atoms theo (sao, cung), tick ✅/⚠/❌ + comment
- API: `POST /api/atoms/verify` → update confidence + verified flag
- Anh review N atoms / phiên, confidence ✅ → 0.95

**Effort**: 4-5h
**Token**: ~200k

---

## 🗺 ROADMAP — Thứ tự CRITICAL PATH để "nhai gọn"

### Phase A — Foundation (Mảng 2 + 3) — *MUST DO FIRST*
| Step | Việc | Effort | Token | Dep |
|---|---|---|---:|---|
| A1 | Build paradigm engine 6 functions (Mảng 2) | 4h | 175k | - |
| A2 | Sub-agents auto-gen mappings 4 sách (Mảng 3) | 1.5h | 200k | - |
| A3 | Unit test paradigm engine vs founder lá số | 1h | 50k | A1 |

**Phase A total**: ~6.5h, ~425k tokens. Sau A: paradigm + mappings WORK.

### Phase B — Orchestration + Output (Mảng 4 + 5)
| Step | Việc | Effort | Token | Dep |
|---|---|---|---:|---|
| B1 | Build CrossSchoolOrchestrator (Mảng 4) | 3h | 200k | A1 |
| B2 | Build OutputFillerV2 (Mảng 5) | 6-8h | 400k | A1, A2, B1 |
| B3 | E2E test lá số founder → output 3-Layer text | 1h | 50k | B2 |

**Phase B total**: ~10-12h, ~650k tokens. Sau B: có thể test E2E text output.

### Phase C — UI (Mảng 6)
| Step | Việc | Effort | Token | Dep |
|---|---|---|---:|---|
| C1 | Build TuViLaSoPanelV2 components | 6h | 200k | B3 |
| C2 | Integrate API + render | 2h | 50k | C1 |
| C3 | Visual QA + tooltip Hán-Việt | 2h | 50k | C2 |

**Phase C total**: ~10h, ~300k tokens. Sau C: User vào kinhdich.online → thấy lá số đẹp + 3-Layer.

### Phase D — Verify + QC (Mảng 7)
| Step | Việc | Effort | Token | Dep |
|---|---|---|---:|---|
| D1 | Admin UI founder verify | 3h | 100k | C3 |
| D2 | Anh review N atoms/phiên → upgrade confidence | ongoing | 100k/phiên | D1 |
| D3 | Re-train output filler với atoms 0.95+ | 1h | 50k | D2 |

**Phase D total**: ~4h initial + ongoing, ~250k tokens.

---

## 📈 TOTAL EFFORT để "nhai gọn"

| Phase | Việc | Token | Phiên |
|---|---|---:|---|
| **Phase A** | Foundation paradigm + mappings | 425k | 0.5 phiên |
| **Phase B** | Cross-school + output filler | 650k | 1 phiên |
| **Phase C** | UI v2 | 300k | 0.5 phiên |
| **Phase D** | Founder verify | 250k+ | 0.5 phiên + ongoing |
| **TỔNG** | | **~1.6M tokens** | **~2.5 phiên** |

---

## ⚠ CRITICAL RISKS

1. **Atoms confidence 0.85 chưa verify** — output filler có thể propagate sai. Mitigation: Anh verify 50-100 atoms cốt lõi trước khi launch
2. **Mapping 168 sao×cung không đủ data** — nhiều sách không phủ hết 12 cung. Mitigation: graceful fallback "Hệ phái X không nói rõ về tổ hợp này"
3. **Cross-school disagree → user rối** — nếu 4 sách nói khác nhau. Mitigation: UI có toggle "1 trường phái" vs "4 trường phái"
4. **LLM cost output filler** — mỗi lá số ~10 LLM calls cho 14 sao × 12 cung. Mitigation: cache + batch + dùng MiniMax/Gemini free trước

---

## 🎯 ĐỀ XUẤT TIẾP

Sau khi 9 sub-agents Sách 2+3 xong + ingest DB → em propose:

**ƯU TIÊN 1**: Đi Phase A NGAY (paradigm engine + mappings) — 1 phiên là xong. Sau A, em có thể demo paradigm engine trên lá số founder ngay (text-only).

**ƯU TIÊN 2**: Phase B (cross-school + output filler) — 1 phiên nữa. Sau B, demo 3-Layer text cho founder.

**ƯU TIÊN 3**: Phase C (UI) — 0.5 phiên. Sau C, anh vào kinhdich.online thấy.

**ƯU TIÊN 4**: Phase D (verify) — ongoing, mỗi phiên anh review 20-50 atoms cốt.

→ **~2.5 phiên** để đạt "nhai gọn 1 lá số bất kỳ".
