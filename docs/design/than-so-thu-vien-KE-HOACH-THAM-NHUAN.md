# Kế hoạch thâm nhuần thư viện Thần Số Học

> Mục tiêu: đọc **hết** tài liệu thần số **đang có trong thư viện dự án**, rút nguyên lý phục vụ luận giải user (đồng dạng, không predict).
> Người thực hiện: em · Anh duyệt từng vòng trước khi nhảy vòng.
> Paradigm: Iron Rule #1 research · #2 không nhảy phase · #3 đa phái · #4/#6/#8/#9 không predict.
> Mẫu vận hành: giống `hoang-cuc-tham-nhuan-vong-N` / Mai Hoa Q3 — **một vòng = một journal + insight + inject có kiểm**.

---

## 0. Inventory — cái gì ĐANG có để đọc

### 0.1 Sách trường phái `08-numerology-tay-phuong`

| ID | Tài liệu | Hình thức đọc được | Độ sâu chữ | Ghi chú |
|---|---|---|---|---|
| **CHEIRO** | *Book of Numbers* (1926, PD) | OCR full `source/cheiro-book-of-numbers-ocr.txt` (~11k dòng, ~316k chars) + `content.md` + PDF publish core v0.2 | **ĐẦY ĐỦ** để thâm nhuần từng chương | Trục chính của kế hoạch |
| **BALLIETT** | *Philosophy of Numbers* (~1908, PD) | Chỉ `content.md` method stub (~44 dòng) | **MỎNG** | Chưa có OCR/scan trong repo → vòng Balliett = dual-track (xem §3) |
| **CAMPBELL** | *Your Days Are Numbered* (1931) | Chỉ `content.md` method stub (~43 dòng) | **MỎNG** | Còn bản quyền tới 2027 — chỉ method/facts; không restore nguyên văn |

### 0.2 Knowledge base máy (đọc như “phụ lục nguyên lý”, không phải sách)

`data/than_so/master/`:
- `pythagorean_spec.json`, `letter_maps.json`, `core_numbers.json`
- `number_meanings.json`, `karmic_debt.json`, `cycles.json`
- `chaldean_compound_numbers.json`, `compatibility_matrix.json`
- `interpretation_principles.json` (đã có từ v12 — sẽ **revise** sau mỗi vòng Cheiro)
- `library_provenance.json`, `sources_catalog.json`, `cross_bind_dong_phuong.json`

### 0.3 Đã thâm nhuần một phần (v12)

Journal: `docs/design/than-so-thu-vien-tham-nhuan.md`  
Phạm vi: Cheiro Ch.I–II, XII–XV, XVII, XXIV + stub Balliett/Campbell.  
→ **Chưa** đọc hết Cheiro; **chưa** đủ Balliett/Campbell full text.

### 0.4 Ngoài thư viện — KHÔNG nằm trong kế hoạch đọc “hết thư viện”

- Juno Jordan / Matthew Goodwin: **không có file** trong repo (bản quyền) → không bịa; ghi “chờ mua/upload”.
- Decoz web: tham chiếu công thức (đã đóng trong `pythagorean_spec.json`), không phải sách thư viện.

---

## 1. Nguyên tắc đọc (áp dụng mọi vòng)

1. **Đọc chữ trước, inject sau** — mỗi vòng có journal riêng; chỉ sau khi Anh duyệt insight mới đụng `deep_reading` / `number_meanings` / sage.
2. **Tone Cheiro → tone YI** — giữ nguyên lý cấu trúc; khi xuất user: bỏ may/xui/fatal; giữ “quan-sát / GAP / IMPROVE”.
3. **Đa phái rõ ràng (#3)** — Cheiro ≠ Decoz; mỗi insight ghi “khung nào”; conflict → present Anh (kept_all hợp lệ).
4. **Cấm dụng cụ tà mạng (#9)** — Ch.XXX *Horse-racing and Numbers*: đọc để **biết biên giới**, ghi “từ chối predict/cá cược”, **không** inject thành feature chọn số đề/đua ngựa.
5. **Ch.XXVIII Number and disease**: đọc nguyên lý liên hệ hành tinh–thể; **không** luận bệnh/chẩn đoán cho user; disclaimer y tế bắt buộc nếu có nhắc.
6. **Một vòng một phạm vi đóng** — không “đọc lướt cả cuốn một lần rồi claim xong”.

---

## 2. Lộ trình vòng — CHEIRO (trục chính)

Nguồn: `data/restored_books/cheiro-book-of-numbers/source/cheiro-book-of-numbers-ocr.txt`  
Artifact mỗi vòng: `docs/design/than-so-cheiro-tham-nhuan-vong-N.md`  
Skill citation (sau duyệt): `data/hermes_yi/skills/than-so/thu-vien/cheiro-vong-N.md` (force-add)

| Vòng | Chương OCR | Chủ đề | Deliverable bắt buộc | Inject engine? |
|---|---|---|---|---|
| **C0** (đã có v12) | I–II, XII–XV, XVII, XXIV | Rung động, đơn/kép, Birth Key, hòa Name↔Birth, tập trung | `than-so-thu-vien-tham-nhuan.md` | ✅ đã |
| **C1** | III–VII (số 1–5) | Tính cách Birth number 1…5; nhà Hoàng đạo; màu/đá (lọc tone) | Journal + bảng archetype_vi refine 1–5 | Sau duyệt → `number_meanings` + deep_reading roles |
| **C2** | VIII–XI (số 6–9) | Birth 6…9; nhấn 8/9; series | Journal + refine 6–9; note 4↔8 foreshadow | Sau duyệt |
| **C3** | XII–XIII (ôn + dày) | Compound symbolism + 10–52 **đối chiếu lại** OCR vs JSON | Diff audit `chaldean_compound_numbers.json`; bổ sung `dong_dang` từng số | Có thể sửa JSON nếu lệch OCR |
| **C4** | XIV–XVI | Hòa Name↔Birth; ví dụ tên (Napoleon, Lloyd George…) | Casebook nguyên lý (không copy dài); rule “tên đang dùng” | deep_reading + UI copy |
| **C5** | XVII–XXI | Recurrence, 13, periodicity, case lịch sử | Nguyên lý “số lặp = gương”; #9 filter case vua/chết | Chỉ nguyên lý pattern, không predict |
| **C6** | XXII–XXVII | Ngày / màu / tập trung / 1–4 / 4&8 / nhạc–màu | Map màu–số **như dữ liệu tham chiếu** (Balliett bridge); rule 4&8 | art-direction stub + four_eight guidance |
| **C7** | XXVIII–XXIX, XXXI–XXXIII | Bệnh (biên giới), nơi ở, Presidents examples, Bible numbers, Conclusion | Biên giới đạo đức; case Washington… như **bài tập đọc compound**; kết luận Cheiro “practical occultism” → YI procedural | Disclaimer; không medical feature |
| **C8** | XXX | Horse-racing | **Biên giới cứng**: từ chối SKU cá cược; ghi memory | Không inject |

**Thứ tự bắt buộc:** C1 → C2 → C3 → … (không nhảy). C0 giữ làm nền.

**Tiêu chí “xong một vòng Cheiro”:**
- [ ] Journal ≥ 5 insights có trích dòng OCR (line ref)
- [ ] Mỗi insight có: nguyên lý Cheiro → reframing YI → hệ quả luận giải user
- [ ] Liệt kê conflict với Decoz (nếu có)
- [ ] Đề xuất inject cụ thể (file + field) — **chưa code** cho đến khi Anh OK
- [ ] Cập nhật checklist §6

---

## 3. Lộ trình vòng — BALLIETT & CAMPBELL (dual-track)

### 3.1 Thực trạng

Trong repo **không đủ chữ** để thâm nhuần kiểu Cheiro.  
Nếu chỉ đọc stub hiện có → xong trong một vòng ngắn, **không được pretend “đã đọc sách”**.

### 3.2 Track A — Có ngay (không cần Anh)

| Vòng | Việc | Output |
|---|---|---|
| **B0** | Đọc lại stub Balliett + cross-ref chỗ Cheiro/Decoz đã dùng provenance Balliett | `than-so-balliett-tham-nhuan-vong-0.md` — chốt câu hỏi mở cần full text |
| **P0** | Đọc lại stub Campbell + audit engine Inclusion/Lessons/Passion đã khớp chưa | `than-so-campbell-tham-nhuan-vong-0.md` + test gaps |

### 3.3 Track B — Cần Anh (mở khóa full thâm nhuần)

| Điều kiện | Việc tiếp |
|---|---|
| Anh upload / allowlist PDF Balliett (PD) | OCR → `source/` → vòng **B1+** từng phần (Tone & Colors, Vibration, Success through numbers…) |
| Anh xác nhận được dùng Campbell method-only sâu hơn **hoặc** chờ PD 2027 | Vòng **P1+** Inclusion Table chi tiết, planning-by-number (không publish nguyên văn trước 2027) |

Không có Track B → kế hoạch “đọc hết thư viện” **vẫn hoàn thành** trên (Cheiro full + B0/P0), với ghi chú trung thực “Balliett/Campbell full text chưa có”.

---

## 4. Lộ trình vòng — MASTER DATA (đọc máy như kinh phụ)

Song song hoặc xen kẽ sau C2:

| Vòng | File | Mục tiêu |
|---|---|---|
| **M1** | `number_meanings.json` + `karmic_debt.json` | Đối chiếu từng số với Cheiro C1–C2; đánh dấu chỗ mỏng/bịa tone |
| **M2** | `cycles.json` + Decoz pinnacle/challenge | Tách rõ “Decoz BIẾN” vs “Cheiro ngày/kỳ” — tránh trộn |
| **M3** | `compatibility_matrix.json` | Đối chiếu Cheiro series 1–4 / 2–7 / 4&8; chỉnh pair note nếu lệch nguyên lý |
| **M4** | `interpretation_principles.json` | Merge insight mọi vòng C* → bản principles v2 |

---

## 5. Thứ tự đề xuất tổng (không nhảy)

```
C1 → C2 → M1
 → C3 → C4
 → C5 → C6
 → M2 → M3
 → C7 → C8 (biên giới)
 → B0 → P0
 → M4 (đóng principles v2)
 → [Track B nếu Anh mở khóa PDF]
```

Sau mỗi cụm (C1–C2, C3–C4, …): **một PR nhỏ** inject đã duyệt — tránh nhồi một commit khổng lồ.

---

## 6. Checklist tiến độ (cập nhật khi làm)

### Cheiro
- [x] C0 nền (v12)
- [x] C1 số 1–5
- [x] C2 số 6–9
- [x] C3 compound audit → `than-so-cheiro-tham-nhuan-vong-C3.md` (2026-07-22; alias 33–52 khớp OCR; chưa inject JSON)
- [x] C4 Name↔Birth + ví dụ tên → `than-so-cheiro-tham-nhuan-vong-C4.md` (cấm rename-for-luck)
- [x] C5 recurrence / periodicity → `than-so-cheiro-tham-nhuan-vong-C5.md` (ethical filter case chết)
- [ ] C6 màu–nhạc–4&8
- [ ] C7 biên giới + case + conclusion
- [ ] C8 horse-racing = từ chối SKU

### Balliett / Campbell
- [ ] B0 stub + câu hỏi mở
- [ ] P0 stub + audit Inclusion
- [ ] B1+ / P1+ (chờ nguồn)

### Master
- [ ] M1 meanings/debt
- [ ] M2 cycles vs Cheiro
- [ ] M3 compatibility
- [ ] M4 principles v2

---

## 7. Definition of Done — “đã đọc hết thư viện”

1. Mọi chương Cheiro OCR I–XXXIII đã có journal vòng tương ứng (C8 chỉ biên giới).
2. B0 + P0 xong; Track B ghi rõ còn thiếu file.
3. `interpretation_principles.json` v2 phản ánh đủ vòng đã duyệt.
4. Sage skill `than-so/` có citation per vòng (không nhét hết vào SOUL).
5. Engine luận giải: synthesis Name↔Birth + Birth layers + Inclusion + số 1–9 có chiều sâu Cheiro đã lọc tone.
6. Không có feature cá cược / chẩn bệnh từ số.

---

## 8. Rủi ro & cách xử lý

| Rủi ro | Xử lý |
|---|---|
| OCR Cheiro bẩn / lệch dòng | Mỗi vòng ghi line range; quote ngắn; nếu nghi → đối PDF publish/local scan |
| Sa vào fortune-tone Cheiro | Template insight bắt buộc có mục “Reframe YI” |
| Làm ẩu như v11 | Anh không duyệt vòng → không inject |
| Balliett/Campbell thiếu chữ | Không claim “đã đọc sách”; chỉ B0/P0 |

---

## 9. Bước kế tiếp ngay (khi Anh bảo “bắt đầu”)

1. Mở vòng **C1** — đọc OCR Ch.III–VII (số 1–5).
2. Viết `docs/design/than-so-cheiro-tham-nhuan-vong-1.md`.
3. Trình Anh duyệt insight → mới đề xuất patch `number_meanings` / deep_reading.

*(Em không tự nhảy C1 trong file kế hoạch này — Anh chốt “bắt đầu C1” thì làm.)*
