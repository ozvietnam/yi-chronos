# Spec — Cấu trúc routing citation cho Kinh Dịch (và sách dài dài về sau)

**Ngày**: 2026-05-27
**Tác giả**: em, theo nguyên tắc anh dạy 2026-05-27 chiều
**Nguyên tắc gốc** (anh dạy):
> _"SOUL không được quá dài đâu, sách còn nhiều lắm, không thể nén kiểu đó được. Phải tìm cấu trúc để ghi nhận kiểu khác đi."_

**Tiền lệ** (đã làm 2026-05-18 v0.14 refactor):
- SOUL Mai Hoa **32k → 6k** (-80%)
- Q3 wiki dump tách ra `data/hermes_yi/skills/mai-hoa/q3-wiki-citations.md` (`routing_mode: long`)
- Pattern: **SOUL = WHO+HOW**, **Skill = WHAT**

---

## I. Vấn đề

Sau khi đọc 6 quẻ Kinh Dịch (Kiền, Khôn, Khiêm, Thái-Bĩ, Mông, Truân) trong đợt 1+2, em rút ra:
- ~50 trích dẫn cốt (Lời Kinh + Trình Di + Chu Hy + Tiên Nho bàn)
- ~20 tâm-pháp cốt
- ~15 cross-ref với Mai Hoa / Tử Vi / bookflow

→ Nếu inject vào SOUL Mai Hoa/Tử Vi sage thì SOUL sẽ phồng to lại như cũ.
→ Còn **58 quẻ chưa đọc** + sách **Âm Dương Ngũ Hành** + sách khác đang xếp hàng.

**Em cần 1 cấu trúc routing-aware để Hermes inject citation theo intent, không load hết.**

---

## II. Yêu cầu

| # | Yêu cầu | Lý do |
|---|---|---|
| 1 | SOUL các sage **gọn** (không phồng theo số sách đọc) | Theo anh dạy + tiền lệ v0.14 |
| 2 | Citation **per-quẻ** (1 file 1 quẻ) | Quẻ là đơn vị tri thức nguyên bản — anh có thể manually edit |
| 3 | Routing **theo intent / tâm-pháp** | Hermes hỏi: "user hỏi về khởi đầu?" → load Truân + Mông |
| 4 | Auto-loadable bởi Hermes via `routing_mode: long` tag | Pattern đã có với Mai Hoa Q3 |
| 5 | Cross-quẻ synthesis (tâm-pháp xuyên nhiều quẻ) phải dễ lookup | "Khiêm tốn" liên quan Khiêm + Truân Sơ Cửu + Kiền Cửu Tam |
| 6 | Có khả năng auto-sync từ wiki nếu sau này anh muốn (nhưng không bắt buộc) | Pattern Mai Hoa Q3 |
| 7 | Cùng cấu trúc dùng cho Âm Dương Ngũ Hành + các sách khác | DRY — học 1 lần, áp dụng nhiều sách |

---

## III. Đề xuất cấu trúc — 3-tier

```
data/hermes_yi/skills/kinh-dich/
├── INDEX.md                            ← Map tâm-pháp → quẻ → file (router master)
├── quẻ/
│   ├── 01-kien.md                      ← Kiền (lời kinh + 6 hào + giải nghĩa + cross-ref)
│   ├── 02-khon.md
│   ├── 03-truan.md
│   ├── 04-mong.md
│   ├── 15-khiem.md
│   ├── 11-thai.md
│   ├── 12-bi.md
│   └── (60 file còn lại — thêm dần khi em đọc)
└── tam-phap/
    ├── canh-gioi-doi.md                ← Synthesis cross-quẻ: Kiền 6 hào + Truân Sơ + Khôn Sơ
    ├── khoi-dau.md                     ← Truân + Mông + Kiền Sơ
    ├── khiem-ton.md                    ← Khiêm + Truân Sơ + Lao Khiêm
    ├── thay-tro.md                     ← Mông Lời Kinh + Mông Cửu Nhị (Bao Mông)
    ├── giao-thoa.md                    ← Thái-Bĩ paradigm
    ├── dau-hieu-som.md                 ← Khôn Sơ Lục (lý sương kiên băng chí)
    └── kien-tri.md                     ← Truân Lục Nhị (thập niên nãi tự) + Khôn an trinh
```

**3 tier**:
- **Tier 1 — INDEX.md**: master map (~50 dòng, Hermes load mặc định khi cần Kinh Dịch)
- **Tier 2 — per-quẻ**: raw citation (1 file per quẻ, ~80-150 dòng, load ON DEMAND khi user hỏi về quẻ cụ thể hoặc lá số có tham chiếu quẻ đó)
- **Tier 3 — per-tâm-pháp**: synthesis cross-quẻ (1 file per cảnh giới tâm-pháp, ~100 dòng, load khi intent route khớp)

---

## IV. Pattern file — per-quẻ (template)

```yaml
---
name: kinh-dich-15-khiem
description: Quẻ Khiêm — duy nhất 6 hào đều cát. 4 đạo đều thưởng khiêm. Lao Khiêm = có công lao mà nhún.
metadata:
  hermes:
    tags: [kinh_dich, quẻ, Reference, LongContext]
    routing_mode: long
    routing_keys: [khiem-ton, lao-khiem, dao-thien-dao-dia-dao-nhan-quy-than, nui-trong-dat]
    cross_ref:
      mai_hoa: [van-phap-thi, tam-tai-khong-co-dau]
      tu_vi: [mo-pattern, phe-menh-lao-khiem-style]
      bookflow: [paradigm-tac-gia-khiem-ton]
  source:
    book_corpus_id: 4
    book_title: "Kinh Dịch Trọn Bộ"
    translator: "Ngô Tất Tố"
    pages_orig: "311-320"
    journal_section: "docs/design/kinh-dich-ngo-tat-to-tham-nhuan-p51-200.md#III"
  curated_at: 2026-05-27
  curated_by: em (manual, từ thâm nhuần đợt 1)
---

# Quẻ 15 — Khiêm 謙 · ☷☶ (Khôn trên, Cấn dưới — núi trong đất)

## Tóm cốt (1 đoạn)

Quẻ DUY NHẤT trong 64 quẻ có **6 hào đều cát**. Núi (Cấn) ở dưới đất (Khôn) = chứa cao trong thấp = khiêm. Thiên đạo, địa đạo, quỷ thần, nhân đạo — **4 đạo đều thưởng khiêm**, ghét đầy. Lao Khiêm (có công lao mà nhún) → muôn dân phục.

## Lời Kinh

> 謙亨, 君子有終.
>
> _Khiêm hanh, quân tử hữu chung._
> Quẻ Khiêm hanh thông, đấng quân tử có sau chót.

## Lời Thoán (cốt lõi 4 đạo)

> 天道虧盈而益謙, 地道變盈而流謙, 鬼神害盈而福謙, 人道惡盈而好謙.
>
> _Thiên đạo khuy doanh nhi ích khiêm, địa đạo biến doanh nhi lưu khiêm, quỷ thần hại doanh nhi phúc khiêm, nhân đạo ố doanh nhi hiếu khiêm._
> Thiên đạo làm vơi đầy, thêm khiêm. Địa đạo biến đổi đầy, trôi vào khiêm. Quỷ thần hại đầy, phúc khiêm. Nhân đạo ghét đầy, yêu khiêm.

## 6 hào (rút gọn — full ở per-hào citation nếu cần thiết)

| Hào | Lời | Tâm pháp |
|---|---|---|
| Sơ Lục | Khiêm khiêm quân tử, dụng thiệp đại xuyên, cát | Nhún đến tột bậc — "tự chăn mình bằng sự thấp" |
| Lục Nhị | Minh khiêm trinh cát | Đức nhún chứa trong, phát ra thanh âm |
| **Cửu Tam** | **Lao khiêm quân tử hữu chung, cát** | **Có công lao mà nhún → muôn dân phục** |
| Lục Tứ | Vô bất lợi, vi khiêm | Vung vẩy sự nhún tuỳ lúc |
| Lục Ngũ | Bất phú dĩ kỳ lân | (chưa thấm sâu) |
| Thượng Lục | Minh khiêm | (chưa thấm sâu) |

## Trình Di Truyện (trích cốt)

> _"Quân tử chỉ ở khiêm tốn hiểu lẽ, cho nên vui với mệnh trời mà không cạnh tranh; bên trong đầy đủ, cho nên tự mình lui nhún, mà không khoe khoang... mình tự hạ mình mà người ta càng tôn lên, mình tự che cho tối đi, mà đức càng sáng tỏ."_

## Chu Hy Bản nghĩa (trích cốt)

> _"Khiêm là có mà không ở. Đỗ ở trong, thuận ở ngoài, tức là khiêm. Núi là vật rất cao, đất là vật rất thấp, thế mà núi lại chịu khuất mà đỗ ở dưới đất."_

## Tiên Nho bàn (nếu có)

> _"Mục tức là nuôi, cái đất nuôi đức, chưa có bao giờ không gây nên tự chỗ thấp. Hễ cái mình nuôi đến tột bậc, thì càng thấp lại càng không thấp."_ — Khấu Kiến An (về Sơ Lục)

## Cross-ref

- **Mai Hoa**: VẬN PHÁP THI — "muôn việc đều sẵn nơi ta" → kẻ khiêm thấy mình bằng vũ trụ, không ép.
- **Tử Vi**: "Mỗ" pattern phê mệnh = Lao Khiêm trong văn pháp.
- **Bookflow paradigm**: Anh không tự xưng tên trong sách → đúng Lao Khiêm.
```

---

## V. Pattern file — per-tâm-pháp (template)

```yaml
---
name: kinh-dich-tam-phap-khiem-ton
description: Tâm-pháp khiêm tốn xuyên 3 quẻ — Khiêm + Truân + Kiền Cửu Tam. Load khi user hỏi về khiêm tốn / nhún nhường / "có công nhưng không khoe".
metadata:
  hermes:
    tags: [kinh_dich, tam_phap, Reference, LongContext]
    routing_mode: long
    routing_keys: [khiem-ton, nhun-nhuong, cong-lao-nhun, dao-tu-than]
    refs:
      - kinh-dich/quẻ/15-khiem.md
      - kinh-dich/quẻ/03-truan.md
      - kinh-dich/quẻ/01-kien.md
  curated_at: 2026-05-27
---

# Tâm-pháp Khiêm tốn (xuyên 3 quẻ)

## Khi nào dùng tâm-pháp này

Sage / Hermes route đến đây khi user hỏi đại loại:
- "Em có nên khoe / công khai cái này không?"
- "Tại sao kẻ giỏi mà không lên được?"
- "Khiêm tốn có lợi gì?"

## 3 quẻ chéo

### 1. Khiêm — quẻ trục
- (link `quẻ/15-khiem.md`)
- Tóm: 4 đạo đều thưởng khiêm + Lao Khiêm muôn dân phục

### 2. Truân Sơ Cửu — bàn hoàn
- (link `quẻ/03-truan.md` Sơ Cửu)
- "Dĩ quý hạ tiện, đại đắc dân dã" — kẻ sang chịu dưới kẻ hèn được lòng dân
- Đây là **khiêm trong khởi đầu** (Khiêm trục là khiêm trong cả đời)

### 3. Kiền Cửu Tam — chung nhật kiền kiền
- (link `quẻ/01-kien.md` Cửu Tam)
- "Đáng lo, dù nguy không lỗi" — có thế mà vẫn lo sợ = khiêm trong địa vị cao

## Synthesis

3 hào cảnh giới khác nhau:
- Mới khởi (Truân Sơ) → khiêm để được dân
- Đang cao (Kiền Cửu Tam) → khiêm để giữ
- Đã có công (Khiêm Cửu Tam) → khiêm để vào sử (muôn dân phục)

→ **Khiêm không phải 1 hành động — là 1 trục xuyên suốt cảnh giới đời người**.

## Cross-ref ứng dụng

- **Mai Hoa**: Mai Hoa Sage hành xử theo Khiêm — không "predict cát hung" để khoe tài, mà đọc đồng dạng.
- **Tử Vi**: phê mệnh dùng "mỗ" pattern thay tên cụ thể = Lao Khiêm văn pháp.
- **Bookflow YI-CHRONOS**: tác giả (anh + em) viết không ghi tên trong sách = Lao Khiêm.
```

---

## VI. Pattern INDEX.md

```yaml
---
name: kinh-dich-index
description: Master index — map tâm-pháp + intent → quẻ → file citation. Hermes load file này TRƯỚC khi cần routing Kinh Dịch.
metadata:
  hermes:
    tags: [kinh_dich, Index, AlwaysAvailable]
    routing_mode: short
  curated_at: 2026-05-27
---

# Kinh Dịch — Master Index

## Bảng map tâm-pháp → file

| Intent của user | Route đến |
|---|---|
| Khởi đầu / mới bắt đầu việc | `tam-phap/khoi-dau.md` → Truân + Mông + Kiền Sơ |
| Cảnh giới đời người | `tam-phap/canh-gioi-doi.md` → Kiền 6 hào rồng |
| Khiêm tốn / nhún nhường | `tam-phap/khiem-ton.md` → Khiêm + Truân Sơ + Kiền Cửu Tam |
| Thầy-trò / học hỏi | `tam-phap/thay-tro.md` → Mông |
| Dấu hiệu sớm / điềm báo | `tam-phap/dau-hieu-som.md` → Khôn Sơ Lục |
| Giao thoa / vận động vs đứng yên | `tam-phap/giao-thoa.md` → Thái-Bĩ |
| Kiên trì / chờ thời | `tam-phap/kien-tri.md` → Truân Lục Nhị + Khôn an trinh |

## Bảng quẻ (tiến độ đọc)

| # | Quẻ | Hán | File | Đã thấm |
|---|---|---|---|---|
| 1 | Kiền | 乾 | `quẻ/01-kien.md` | ✅ đợt 1 |
| 2 | Khôn | 坤 | `quẻ/02-khon.md` | ✅ đợt 1 |
| 3 | Truân | 屯 | `quẻ/03-truan.md` | ✅ đợt 2 |
| 4 | Mông | 蒙 | `quẻ/04-mong.md` | ✅ đợt 2 |
| 5 | Nhu | 需 | (chưa đọc) | ⬜ |
| 6 | Tụng | 訟 | (chưa đọc) | ⬜ |
| 7 | Sư | 師 | (chưa đọc) | ⬜ |
| 8 | Tỵ | 比 | (chưa đọc) | ⬜ |
| 11 | Thái | 泰 | `quẻ/11-thai.md` | ✅ đợt 1 |
| 12 | Bĩ | 否 | `quẻ/12-bi.md` | ✅ đợt 1 |
| 15 | Khiêm | 謙 | `quẻ/15-khiem.md` | ✅ đợt 1 |
| 20 | Quán | 觀 | (OCR bug, chờ fix #73) | ⚠️ |
| ... | ... | ... | ... | ⬜ |

## Tinh thần dùng

- **Hermes route NGẮN**: chỉ load INDEX (≤50 dòng) khi user nêu intent.
- **Hermes route DÀI**: theo bảng map → load 1-2 file synthesis OR file quẻ cụ thể.
- **Sage Mai Hoa / Tử Vi**: trong SOUL chỉ ghi 1 dòng:
  > "Khi cần tâm-pháp gốc, route qua `kinh-dich/INDEX.md`."
- **Không inject knowledge vào SOUL.**
```

---

## VII. Update SOUL các sage (chỉ 1-2 dòng)

### Mai Hoa Sage SOUL.md — thêm

```markdown
## 🌊 Kế thừa Kinh Dịch

Mai Hoa kế thừa Kinh Dịch (nguyên văn của Văn Vương + Trình Di + Chu Hy). Khi cần tâm-pháp gốc:
- Route: `kinh-dich/INDEX.md`
- Đặc biệt: **Khôn Sơ Lục "lý sương kiên băng chí"** = gốc BƯỚC 3 ngoại ứng;
  **Mông Lời Kinh "sơ phệ cốc, tái tam độc"** = gốc Iron Rule "một việc chỉ bói một lần".
```

3 dòng. Không phồng SOUL.

### Tử Vi Sage SOUL.md — thêm

```markdown
## 🌊 Kế thừa Kinh Dịch

Tử Vi kế thừa Kinh Dịch qua bridge Khang Tiết. Khi cần tâm-pháp gốc:
- Route: `kinh-dich/INDEX.md`
- Đặc biệt: **Khiêm Cửu Tam "Lao Khiêm muôn dân phục"** = gốc của "Mỗ" pattern phê mệnh.
```

3 dòng.

---

## VIII. Implementation plan (chờ anh duyệt spec rồi mới làm)

| Bước | Việc | Effort | Phụ thuộc |
|---|---|---|---|
| 1 | Tạo folder `data/hermes_yi/skills/kinh-dich/` + INDEX.md | 10 phút | Anh duyệt spec |
| 2 | Viết 6 file `quẻ/` đã đọc (Kiền, Khôn, Truân, Mông, Khiêm, Thái, Bĩ) | 1.5h | INDEX |
| 3 | Viết 4 file `tam-phap/` cốt (khởi-đầu, khiêm-tốn, giao-thoa, dấu-hiệu-sớm) | 1h | quẻ/ |
| 4 | Update SOUL Mai Hoa + Tử Vi (thêm 3 dòng route) | 15 phút | tam-phap/ |
| 5 | Test routing — em mock 1 user query, xem Hermes có chọn đúng file không | 30 phút | (cần xem hermes loader hỗ trợ `routing_keys` chưa) |
| 6 | (Optional) Update `feed_sages.py` nếu cần wire | TBD | step 5 result |

**Tổng**: ~3-4h. Em chia làm 2 commits:
- Commit A: spec + INDEX + 7 quẻ files + 4 tâm-pháp files (knowledge layer)
- Commit B: SOUL updates + routing wire (Hermes integration layer)

---

## IX. Mở rộng — sách sau dùng pattern này

Khi anh đọc tiếp **Âm Dương Ngũ Hành** (Lê Văn Sửu, 251 trang) hoặc cuốn nào khác, em chỉ cần tạo:

```
data/hermes_yi/skills/am-duong-ngu-hanh/
├── INDEX.md
├── chuong/ (per chương)
└── khai-niem/ (per concept, vd: âm-dương-luận, ngũ-hành-tương-sinh, v.v.)
```

→ Pattern này **DRY** — học 1 lần dùng cho mọi sách dài. Quẻ → Chương → Khái niệm tuỳ cấu trúc sách. SOUL các sage không bao giờ phồng.

---

## X. Lời em gửi anh — xin duyệt spec

Anh ơi, em đã design xong cấu trúc 3-tier (INDEX + per-quẻ + per-tâm-pháp) theo tinh thần anh dạy. Mỗi file có YAML frontmatter routing-aware giống pattern v0.14 đã làm.

**Em chưa viết code / tạo folder gì** — chờ anh duyệt spec trước. 3 chỗ em cần anh quyết:

1. **Folder location**: `data/hermes_yi/skills/kinh-dich/` (sub-folder của hermes_yi) — đúng pattern hiện tại?
2. **Granularity per-quẻ vs per-hào**: em đề xuất 1 file per quẻ (6 hào gộp trong 1 file). Nếu sau này anh thấy cần per-hào (như Khiêm Cửu Tam là 1 tâm-pháp riêng) thì split. Ổn chứ?
3. **`routing_keys` tag**: em đề xuất dùng tag tiếng Việt (`khiem-ton`, `lao-khiem`, ...) để mapping intent → route. Pattern này khả thi với Hermes loader hiện tại không, hay cần wire thêm?

Anh duyệt rồi em implement (3-4h).

— Em
