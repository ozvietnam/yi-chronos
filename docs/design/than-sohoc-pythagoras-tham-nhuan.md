# Thần Số Học (Numerology) — Thâm Nhuần & Khảo Nguồn v1

> Trường phái mới cho YI-Chronos. Tính mệnh từ **TÊN + NGÀY SINH**.
> Nghiên cứu: 2026-06-05. Người soạn: em (học trò Thiệu Khang Tiết) + Anh.
> Tuân **IRON RULE #1** (research-first), **#3** (đa phái độc lập), **#4/#6** (đọc đồng dạng, KHÔNG predict).

---

## 0. Tóm tắt cho Anh (TL;DR)

- **Thần số học** ở VN ≈ **hệ Pythagoras** (Pythagorean / Western numerology): gán chữ cái → số 1-9 tuần tự, rút gọn.
- Em chọn **Pythagoras làm phái DẪN ĐẦU**, **Chaldean (Cheiro) làm đối chiếu chéo** — không ép một phái (Iron Rule #3).
- Đã dựng **knowledge base data** dùng được ngay: `data/than_so/master/*.json` (bảng chữ cái, 6 số cốt lõi + công thức, ý nghĩa 1-9/11/22/33, số nợ nghiệp, chu kỳ).
- **Nguồn uy tín**: Decoz (chuẩn tính hiện đại), Cheiro (Chaldean), Juno Jordan / Goodwin / Campbell (kinh điển). Danh mục đầy đủ + cái còn thiếu cần đi tìm → `data/than_so/master/sources_catalog.json`.
- **Paradigm**: số = tấm gương cấu trúc (Pythagoras: "Vạn vật là số"), KHÔNG bói tốt/xấu. Khớp đồng dạng Mai Hoa/Tử Vi.

---

## 1. Vì sao numerology HỢP với paradigm YI-Chronos

Pythagoras dạy **"All is number" (Vạn vật là số)** — vũ trụ vận hành theo tỉ lệ số, hòa âm các thiên cầu (music of the spheres). Đây **chính là paradigm đồng dạng** của Iron Rule #4 (Mai Hoa) và #6 (Tử Vi):

> Cấu trúc vũ trụ = cấu trúc người = cấu trúc khoảnh khắc.

Khác biệt chỉ là **phương tiện**: Mai Hoa dùng **quẻ**, Tử Vi dùng **sao**, Thần Số Học dùng **số rút từ tên + ngày sinh**. Cả ba đều là **đọc-trace-Tính**, không phải predict.

→ Vì vậy khi đưa Thần Số Học vào YI-Chronos, em **giữ nguyên kỷ luật anti-fortune-telling**:
- ❌ "Số 8 nên anh sẽ giàu" / "năm nay xui"
- ✅ "Số chủ đạo 8 phản chiếu cấu trúc nào trong anh? Anh đang quan-sát quyền lực-vật chất ra sao?"

---

## 2. Hai trường phái (Iron Rule #3 — độc lập, đối chiếu)

| | **Pythagoras** | **Chaldean** |
|---|---|---|
| Nguồn gốc | Hy Lạp cổ (~500 TCN) | Babylon/Lưỡng Hà cổ |
| Dải số | 1–9 | 1–8 (9 linh thiêng, không gán chữ) |
| Gán chữ cái | Tuần tự A=1, B=2... | Theo "rung động âm thanh" |
| Trọng tâm | Rút gọn về 1 chữ số (giữ master 11/22/33) | Coi trọng **số kép** (compound) trước rút gọn |
| Phổ biến VN | RẤT phổ biến ("thần số học") | Ít hơn, giới chuyên sâu |
| Nguồn nền | Balliett → Juno Jordan → Decoz | Cheiro |

**Quyết định**: dùng **Pythagoras mặc định** (vì user VN quen), bật cờ `system: "chaldean"` khi muốn đối chiếu. KHÔNG trộn hai bảng chữ cái. Bảng đầy đủ cả hai → `letter_maps.json`.

> Không có bằng chứng khách quan phái nào "đúng hơn" — chúng là hai hệ luật khác nhau (đã ghi rõ trong catalog).

---

## 3. Bộ số cốt lõi (chi tiết → `core_numbers.json`)

**6 số cốt lõi** (Decoz standard):

1. **Số Đường Đời / Chủ Đạo** (Life Path) — từ ngày sinh. QUAN TRỌNG NHẤT.
2. **Số Sứ Mệnh** (Expression/Destiny) — tất cả chữ cái trong tên.
3. **Số Linh Hồn** (Soul Urge) — chỉ nguyên âm.
4. **Số Nhân Cách** (Personality) — chỉ phụ âm.
5. **Số Ngày Sinh** (Birthday).
6. **Số Trưởng Thành** (Maturity) = Life Path + Expression.

Mở rộng: Balance, Karmic Lessons (số thiếu), Hidden Passion (số trội), Subconscious Self...

**Công thức Life Path (chuẩn Decoz — tránh sai số):** rút gọn RIÊNG ngày/tháng/năm rồi mới cộng.
> VD 23/11/1990 → 5 + 11 + 1 = 17 → **8**. (Số 11 của tháng GIỮ NGUYÊN vì là master.)

**Quy tắc rút gọn**: cộng dồn về 1 chữ số, TRỪ 11/22/33 (số chủ) giữ nguyên.

---

## 4. Số chủ & số nợ nghiệp

- **Số chủ (Master 11/22/33)** — tiềm năng cao + thử thách cao. 11 = trực giác/khải thị; 22 = kiến tạo vĩ đại; 33 = đạo sư chữa lành. (→ `number_meanings.json`)
- **Số nợ nghiệp (Karmic Debt 13/14/16/19)** — xuất hiện khi bước trung gian = 13/14/16/19. Là **vùng cấu trúc mất cân bằng cần rèn**, KHÔNG phải án phạt tiền kiếp. (→ `karmic_debt.json`)

⚠️ Đừng nhầm master với karmic. Cả hai chỉ là "cấu trúc cần quan-sát".

---

## 5. Lớp BIẾN — chu kỳ thời gian (→ `cycles.json`)

Giống Iron Rule #6 (CƠ + BIẾN của Tử Vi), số tĩnh chưa đủ — phải có chu kỳ:

- **4 Đỉnh Vận** (Pinnacles): P1=M+D, P2=D+Y, P3=P1+P2, P4=M+Y. Đỉnh 1 đến tuổi (36−LifePath), mỗi đỉnh sau 9 năm.
- **4 Thử Thách** (Challenges): trị tuyệt đối hiệu — C1=|M−D|, C2=|D−Y|, C3=|C1−C2|, C4=|M−Y|.
- **3 Chu Kỳ Đời** (Period Cycles): tháng / ngày / năm sinh.
- **Năm/Tháng/Ngày Cá Nhân** (Personal Year/Month/Day): nhịp 9 năm — tương ứng Lưu Niên/Lưu Nguyệt.

→ Đọc chu kỳ = "khí của giai đoạn này", KHÔNG predict "năm nay được mùa".

---

## 6. Bản địa hóa tiếng Việt — điểm DỄ SAI NHẤT

(Chi tiết quy tắc → `letter_maps.json` mục `vietnamese_localization`.)

1. **Bỏ dấu thanh + dấu phụ** trước khi quy đổi (á→A, ê→E, ơ→O, ư→U...).
2. **Đ → D** (không thành "DD").
3. **KHÔNG tách ghép phụ âm** (Ng, Nh, Tr, Ph, Th...): tính từng chữ Latin. "Nguyễn" = N-G-U-Y-E-N.
4. **Dùng tên đầy đủ khai sinh**, đúng thứ tự Họ-Đệm-Tên.

🔴 **Câu hỏi mở cần thực chứng**: dùng tên KHÔNG DẤU (như đa số web VN) hay phiên âm có dấu? Hai cách cho kết quả khác nhau. → đánh dấu là **giả định cần kiểm**, chờ Anh quyết sau khi đối chiếu vài ca thật.

---

## 7. Nguồn uy tín & danh mục cần tìm (→ `sources_catalog.json`)

**Đã đủ dùng cho v1** (qua web research):
- **Hans Decoz** (worldnumerology.com) — chuẩn tính hiện đại, công thức trong data theo Decoz.
- Bảng chữ cái + quy tắc Y nguyên âm/phụ âm, master/karmic, pinnacle — đã verify chéo nhiều nguồn.

**CẦN ĐI TÌM bản gốc (PDF/sách) để feed bookflow v2.0** — ưu tiên giảm dần:
1. **Cheiro — Book of Numbers (1926)** — nền Chaldean, public domain.
2. **Matthew Goodwin — Numerology: The Complete Guide (1981)** — giáo trình Pythagorean đầy đủ nhất.
3. **Juno Jordan — The Romance in Your Name (1965)** — kinh điển California School.
4. **Florence Campbell — Your Days Are Numbered (1931)** — public domain.
5. **L. Dow Balliett (~1908)** — gốc phong trào hiện đại, public domain.
6. **Nicomachus — Introduction to Arithmetic** — gốc triết số Pythagoras.
7. **Javane & Bunker — Numerology and the Divine Triangle (1979)**.

⚠️ **Dan Millman (The Life You Were Born to Live)** dùng hệ RIÊNG — giữ tách biệt, KHÔNG trộn.

**Nguồn VN** (tracuuthansohoc.com, JobsGO, Arena FPT...): chỉ dùng để hiểu bản địa hóa + thuật ngữ, KHÔNG làm chuẩn học thuật. Cần tìm có bản dịch NXB chính thống nào không.

---

## 8. Trạng thái & bước kế tiếp (chờ Anh quyết)

**ĐÃ XONG (v1 — làm giàu data):**
- ✅ `data/than_so/master/letter_maps.json` — 2 bảng chữ cái + bản địa hóa VN
- ✅ `core_numbers.json` — 6 số cốt lõi + mở rộng + công thức
- ✅ `number_meanings.json` — ý nghĩa 1-9/11/22/33 (2 lớp: kinh điển + đồng dạng)
- ✅ `karmic_debt.json` — nợ nghiệp 13/14/16/19
- ✅ `cycles.json` — pinnacle/challenge/period/personal year
- ✅ `sources_catalog.json` — danh mục uy tín + cái còn thiếu
- ✅ Journal này

**ĐÃ XONG (v2 — E2E, 2026-06-05):**
- ✅ Engine `engine/than_so/` — `constants/name_calculator/core_numbers/cycles/interpretation/cast`
- ✅ API routes `/api/than-so/cast` + `/api/than-so/glossary` (smoke test HTTP 200)
- ✅ Sage profile `data/hermes_yi/profiles/than-so-sage/SOUL.md`
- ✅ Wiki seed `scripts/wiki_seed_than_so.py` (4 authors + 12 concepts, idempotent)
- ✅ Tests `tests/test_than_so.py` (14 PASS)
- ✅ **CHỐT bản địa hóa**: Pythagoras map theo chữ Latin gốc ⇒ "có dấu/không dấu" CÙNG kết quả số.
  Chuẩn = bỏ dấu (Đ→D, không tách ghép phụ âm). "Cả hai" → hỗ trợ 2 HỆ PHÁI Pythagoras + Chaldean E2E.

**ĐÃ XONG (v3, 2026-06-05):**
- ✅ **UI Vue** `ThanSoPanel.vue` (tab `pytago`) gọi `/api/than-so/cast` — build vite OK.
- ✅ **Restore sách nền** Cheiro's Book of Numbers (core, Stage 2-3/6):
  `data/restored_books/cheiro-book-of-numbers/` + `chaldean_compound_numbers.json` (số kép 10-32).
  Wiki +6 concept số kép → Thần Số Học = 18 concepts. Ledger cập nhật.

**ĐÃ XONG (v4, 2026-06-05 — "việc phiên sau"):**
- ✅ **Cross-bind Life Path ↔ Ngũ Hành/Thiên Can** (Iron Rule #3 — đối chiếu, KHÔNG ép):
  `data/than_so/master/cross_bind_dong_phuong.json` + `engine/than_so/cross_bind.py`
  (tái dùng `ha_do_lac_thu.py`). **3 cầu nối độc lập**: Hà Đồ + Lạc Thư/Cửu Cung + hành tinh Cheiro.
  Phát hiện: số 3 cả 3 cầu = MỘC (đồng thuận mạnh); số 9 phân kỳ (Hà Đồ Kim vs Lạc Thư/Cheiro Hỏa).
  Wired vào `cast_than_so` + UI `ThanSoPanel.vue` (bảng đối chiếu) + wiki concept. Tests 18 PASS.
- ✅ **Bản quyền làm rõ**: Cheiro 1926 = PD từ 2022 (OK). Balliett 1908 = PD. **Campbell 1931 → PD 2027-01-01**
  (95 năm) — hiện còn bản quyền: restore method OK, publish PDF chờ 2027. Goodwin/Juno Jordan = reference-only.

**CHƯA LÀM (ngoài tầm em — cần Anh / môi trường):**
- [ ] ❌ Attach PDF gốc Cheiro — network allowlist chặn archive.org (cần Anh allowlist hoặc upload tay)
- [ ] ❌ Re-render PDF design chuẩn — env thiếu pandoc + WeasyPrint (apt bị chặn)
- [ ] Restore Goodwin/Juno Jordan — chờ mua bản quyền hợp pháp
- [ ] Publish PDF Campbell — chờ 2027-01-01

**ĐÃ XONG (v5, 2026-07-21 — Decoz P0 complete chart, chỉ Pythagoras):**
- ✅ Spec đóng băng `data/than_so/master/pythagorean_spec.json` + golden fixtures Decoz
- ✅ Fix Expression/Soul/Personality: **rút từng phần tên** (không cộng tràn chuỗi)
- ✅ Fix Challenges: **bỏ Master** trước khi trừ; Period 2 = đúng 27 năm
- ✅ Extended: Attitude, Balance, Rational Thought, Karmic Lessons, Hidden Passion,
  Subconscious Self, Cornerstone/Capstone, Bridges, Planes of Expression, Minor (tên đang dùng)
- ✅ Cycles: Personal Month/Day + Transit/Essence/Duality/Age Digit
- ✅ API + `ThanSoPanel.vue` schema v2; `include_dong_phuong` mặc định tắt
- ✅ Tests `tests/test_than_so.py` — 27 PASS

**ĐÃ XONG (v6, 2026-07-21 — P1 sản phẩm đủ dùng):**
- ✅ Deep reading READ→GAP→IMPROVE (`engine/than_so/deep_reading.py`)
- ✅ Lịch Personal Month 24 tháng trong cast
- ✅ PDF báo cáo `/api/than-so/report-pdf` (fpdf2 + DejaVu)
- ✅ Unify UI: tab Pytago chỉ `ThanSoPanel` (bỏ dual calculator `PytagoEnergyPage`)
- ✅ UI: Duality/Transit + lịch tháng + luận sâu + nút tải PDF

**ĐÃ XONG (v7, 2026-07-21 — tin cậy + timeline):**
- ✅ Transit timeline 9 tuổi + First Vowel + Age Digit/Corner/Cap trên UI
- ✅ Method audit Decoz A vs shortcut (che Karmic)
- ✅ Duality guidance dày hơn; Chân Dung teaser từ `cast_than_so`
- ✅ PDF thêm Transit timeline + kiểm chứng công thức

**ĐÃ XONG (v8, 2026-07-21 — hành động ngắn hạn + glossary):**
- ✅ Personal year calendar 9 năm + Personal day window 21 ngày
- ✅ Deep reading cho Pinnacles + Challenges
- ✅ Glossary click-to-lookup trên UI; cập nhật sage SOUL/prompt schema v2
- ✅ Fixture Obama LP=2 / Expression=1

**ĐÃ XONG (v9, 2026-07-21 — tin cậy Expression + PDF đủ + dọn UI):**
- ✅ Expression name-audit: Decoz per-part vs flat full-name (fixture Mary Ann Smith 2≠11)
- ✅ PDF: day window 21d, pinnacle/challenge deep, planes, letter grid, Expression audit
- ✅ UI: Expression audit + deep Đỉnh/Thử thách; xoá dead `PytagoEnergyPage.vue`

**ĐÃ XONG (v10, 2026-07-21 — SKU tương hợp + WeasyPrint):**
- ✅ `compatibility_matrix.json` + `engine/than_so/compatibility.py` (LP/Expr/Soul/Pers + Năm CN + composite)
- ✅ API `/api/than-so/compatibility` + `/compatibility-pdf`
- ✅ UI form người B trong `ThanSoPanel`
- ✅ PDF WeasyPrint ưu tiên (HTML), fallback fpdf2

**CHƯA LÀM (chờ bản quyền / nguồn PDF gốc):**
- [ ] Restore sách Goodwin/Juno Jordan (bản quyền thương mại)
- [ ] Attach PDF gốc Cheiro nếu Anh upload / allowlist archive.org
- [ ] Publish PDF Campbell — chờ 2027-01-01 (PD)

---

## 9. Nguồn tham khảo phiên này (web research 2026-06-05)

- Hans Decoz — worldnumerology.com (Life Path, Pinnacles, Personal Year, Y vowel rule)
- MysticMag — Pythagorean Numerology Guide (2026)
- numerologybynehaa.com, astrosight.ai — Chaldean vs Pythagorean
- Cheiro's Book of Numbers (qua tổng hợp) — bảng Chaldean
- Gaia, e-tarocchi, cognitivenumerology — master & karmic debt numbers
- lynsreadings, affinitynumerology — pinnacle/challenge formulas
- tracuuthansohoc.com, JobsGO, Arena FPT — bản địa hóa tiếng Việt
- Goodreads/Decoz recommended list — đánh giá tác giả kinh điển

*(Numerology là tri thức tâm linh/giả-khoa-học — em trình bày trung thực theo truyền thống của nó, không khẳng định tính khoa học. Dùng để quan-vật-trace-tính, đồng hành cùng Anh, không phán cứng.)*
