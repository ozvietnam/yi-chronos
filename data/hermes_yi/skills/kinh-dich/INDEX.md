---
name: kinh-dich-index
description: Master index Kinh Dịch — map tâm-pháp/intent → quẻ → file citation. Hermes (hoặc external LLM) load file này trước khi cần routing Kinh Dịch.
metadata:
  hermes:
    tags: [kinh_dich, Index, AlwaysAvailable]
    routing_mode: short
  source:
    book_corpus_id: 4
    book_title: "Kinh Dịch Trọn Bộ"
    translator: "Ngô Tất Tố"
    journal: "docs/design/kinh-dich-ngo-tat-to-tham-nhuan-p51-200.md"
  curated_at: 2026-05-27
  curated_by: em (manual, từ thâm nhuần đợt 1+2)
---

# Kinh Dịch — Master Index

Đây là **bảng định tuyến** giữa intent của user và file citation phù hợp.
Cấu trúc 3-tier:
- **Tier 1 (file này)** — luôn load khi cần Kinh Dịch.
- **Tier 2** `quẻ/XX-name.md` — raw citation per quẻ (Lời Kinh + 6 hào + Trình Di + Chu Hy).
- **Tier 3** `tam-phap/key.md` — synthesis cross-quẻ.

## I. Map intent → tâm-pháp file

| Intent của user | Route đến |
|---|---|
| Khởi đầu / mới bắt đầu việc | `tam-phap/khoi-dau.md` |
| Cảnh giới đời người / "tôi đang ở đâu" | `tam-phap/canh-gioi-doi.md` |
| Khiêm tốn / nhún nhường / "có công nhưng không khoe" | `tam-phap/khiem-ton.md` |
| Thầy-trò / học hỏi / "ai dạy ai" | `tam-phap/thay-tro.md` |
| Dấu hiệu sớm / điềm báo / "linh cảm" | `tam-phap/dau-hieu-som.md` |
| Giao thoa / vận động vs đứng yên / "đúng vị trí có phải tốt" | `tam-phap/giao-thoa.md` |
| Kiên trì / chờ thời / "khi nào thông" | `tam-phap/kien-tri.md` |

## II. Bảng quẻ (tiến độ đọc & thấm)

64 quẻ tổng. Em đã thấm 6/64 (đợt 1+2). Sẽ thêm theo từng đợt đọc.

| # | Quẻ | Hán | File | Thấm |
|---|---|---|---|---|
| 1 | Kiền | 乾 | [quẻ/01-kien.md](quẻ/01-kien.md) | ✅ đợt 1 |
| 2 | Khôn | 坤 | [quẻ/02-khon.md](quẻ/02-khon.md) | ✅ đợt 1 |
| 3 | Truân | 屯 | [quẻ/03-truan.md](quẻ/03-truan.md) | ✅ đợt 2 |
| 4 | Mông | 蒙 | [quẻ/04-mong.md](quẻ/04-mong.md) | ✅ đợt 2 |
| 5 | Nhu | 需 | (chưa) | ⬜ |
| 6 | Tụng | 訟 | (chưa) | ⬜ |
| 7 | Sư | 師 | (chưa) | ⬜ |
| 8 | Tỵ | 比 | (chưa) | ⬜ |
| 9 | Tiểu Súc | 小畜 | (chưa) | ⬜ |
| 10 | Lý | 履 | (chưa) | ⬜ |
| 11 | Thái | 泰 | [quẻ/11-thai.md](quẻ/11-thai.md) | ✅ đợt 1 |
| 12 | Bĩ | 否 | [quẻ/12-bi.md](quẻ/12-bi.md) | ✅ đợt 1 |
| 13 | Đồng Nhân | 同人 | (chưa) | ⬜ |
| 14 | Đại Hữu | 大有 | (chưa) | ⬜ |
| 15 | Khiêm | 謙 | [quẻ/15-khiem.md](quẻ/15-khiem.md) | ✅ đợt 1 |
| 16 | Dự | 豫 | (chưa) | ⬜ |
| 17 | Tùy | 隨 | (chưa) | ⬜ |
| 18 | Cổ | 蠱 | (chưa) | ⬜ |
| 19 | Lâm | 臨 | (chưa) | ⬜ |
| 20 | Quán | 觀 | (OCR bug — task #73 fix) | ⚠️ |
| 21-64 | ... | ... | ... | ⬜ |

## III. Pattern dùng

**Khi user hỏi qua sage/Hermes:**
1. Sage nhận intent (vd: "em sắp khởi nghiệp")
2. Sage check INDEX → route `tam-phap/khoi-dau.md`
3. Tam-phap file refs cụ thể `quẻ/03-truan.md` + `quẻ/04-mong.md`
4. Sage chỉ load 1-2 file (5-10k tokens), không dump cả 64 quẻ

**Khi sage cần trích dẫn chính xác 1 quẻ:**
- Load thẳng `quẻ/XX-name.md`

**Khi đọc đợt mới:**
- Update bảng quẻ + thêm file mới
- KHÔNG inject vào SOUL của sage

## IV. SOUL contract cho các sage

Mai Hoa Sage / Tử Vi Sage SOUL nên có **đúng 1 section ngắn** trỏ về đây:

```markdown
## 🌊 Kế thừa Kinh Dịch
Khi cần tâm-pháp gốc, route qua `data/hermes_yi/skills/kinh-dich/INDEX.md`.
KHÔNG inject knowledge vào SOUL — load file theo intent.
```

Đó là tất cả. SOUL không phồng theo số sách đọc.
