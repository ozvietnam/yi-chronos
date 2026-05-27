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
  curated_at: 2026-05-27 (cập nhật sau khi hoàn thành 64/64 deep)
---

# Kinh Dịch — Master Index

Đây là **bảng định tuyến** giữa intent của user và file citation phù hợp.
Cấu trúc 3-tier:
- **Tier 1 (file này)** — luôn load khi cần Kinh Dịch.
- **Tier 2** `quẻ/XX-name.md` — raw citation per quẻ (Lời Kinh + 6 hào + Trình Di + Chu Hy).
- **Tier 3** `tam-phap/key.md` — synthesis cross-quẻ.

## ✅ Trạng thái: 64/64 quẻ DEEP

Tất cả 64 quẻ Kinh Dịch Trọn Bộ Ngô Tất Tố đã được rewrite thành deep citation với:
- Lời Kinh nguyên văn Hán + dịch âm + dịch nghĩa
- Trích dẫn **Trình Di Truyện** + **Bản nghĩa Chu Hy** + **Tiên Nho** cho mỗi hào
- Insight cốt + cross-ref bookflow/privacy/engine/Tử Vi

**Engine `engine/yi_wiki/luan_sau_kinhdich.py`** lookup `_HEXAGRAM_TO_FILE` (64 entries) và inject deep citation vào LLM prompt cho mọi quẻ Mai Hoa cast được.

## I. Map intent → tâm-pháp file

| Intent của user | Route đến |
|---|---|
| Khởi đầu / mới bắt đầu việc | `tam-phap/khoi-dau.md` |
| Quan vật / xem để hiểu Tính / paradigm Mai Hoa | `quẻ/20-quan.md` (gốc Mai Hoa quan-vật) |
| Chờ thời có đức tin (khác bàn hoàn, khác tiềm long) | `quẻ/05-nhu.md` |
| Tranh biện / multi-school conflict / kept_all | `quẻ/06-tung.md` (trung cát chung hung) |
| Hợp tác / đối tác / "hậu phu hung" | `quẻ/08-ty.md` (3 đức: nguyên-vĩnh-trinh) |
| Cảnh giới đời người / "tôi đang ở đâu" | `tam-phap/canh-gioi-doi.md` ⚠ TODO |
| Khiêm tốn / nhún nhường / "có công nhưng không khoe" | `tam-phap/khiem-ton.md` |
| Thầy-trò / học hỏi / "ai dạy ai" | `tam-phap/thay-tro.md` ⚠ TODO |
| Dấu hiệu sớm / điềm báo / "linh cảm" | `tam-phap/dau-hieu-som.md` |
| Giao thoa / vận động vs đứng yên / "đúng vị trí có phải tốt" | `tam-phap/giao-thoa.md` |
| Kiên trì / chờ thời / "khi nào thông" | `tam-phap/kien-tri.md` ⚠ TODO |
| Sáng bị thương / vua tối / trốn thời | `quẻ/36-minh-di.md` (Văn Vương + Cơ Tử paradigm) |
| Thịnh đến đỉnh / cảnh báo "nhật trung tắc trắc" | `quẻ/55-phong.md` |
| Đã hoàn thành nhưng cuối loạn | `quẻ/63-ky-te.md` (sơ cát chung loạn) |
| Chưa hoàn thành / "không có FINAL" | `quẻ/64-vi-te.md` (vật bất khả cùng) |

## II. Bảng 64 quẻ

Tất cả 64 quẻ đã DEEP. Bảng dưới chỉ liệt kê tên + OCR coverage (cho debug).

### Thượng Kinh (30 quẻ đầu — đạo trời đất)

| # | Quẻ | Hán | Cấu trúc | OCR | File |
|---|---|---|---|---|---|
| 1 | Kiền | 乾 | ☰☰ | ✅ | [01-kien.md](quẻ/01-kien.md) |
| 2 | Khôn | 坤 | ☷☷ | ✅ | [02-khon.md](quẻ/02-khon.md) |
| 3 | Truân | 屯 | ☵☳ | ✅ | [03-truan.md](quẻ/03-truan.md) |
| 4 | Mông | 蒙 | ☶☵ | ✅ | [04-mong.md](quẻ/04-mong.md) |
| 5 | Nhu | 需 | ☵☰ | ✅ | [05-nhu.md](quẻ/05-nhu.md) |
| 6 | Tụng | 訟 | ☰☵ | ✅ | [06-tung.md](quẻ/06-tung.md) |
| 7 | Sư | 師 | ☷☵ | ✅ | [07-su.md](quẻ/07-su.md) |
| 8 | Tỵ | 比 | ☵☷ | ✅ | [08-ty.md](quẻ/08-ty.md) |
| 9 | Tiểu Súc | 小畜 | ☴☰ | ✅ | [09-tieu-suc.md](quẻ/09-tieu-suc.md) |
| 10 | Lý | 履 | ☰☱ | ✅ | [10-ly.md](quẻ/10-ly.md) |
| 11 | Thái | 泰 | ☷☰ | ✅ | [11-thai.md](quẻ/11-thai.md) |
| 12 | Bĩ | 否 | ☰☷ | ✅ | [12-bi.md](quẻ/12-bi.md) |
| 13 | Đồng Nhân | 同人 | ☰☲ | ✅ | [13-dong-nhan.md](quẻ/13-dong-nhan.md) |
| 14 | Đại Hữu | 大有 | ☲☰ | ✅ | [14-dai-huu.md](quẻ/14-dai-huu.md) |
| 15 | Khiêm | 謙 | ☷☶ | ✅ | [15-khiem.md](quẻ/15-khiem.md) |
| 16 | Dự | 豫 | ☳☷ | ✅ | [16-du.md](quẻ/16-du.md) |
| 17 | Tùy | 隨 | ☱☳ | ✅ | [17-tuy.md](quẻ/17-tuy.md) |
| 18 | Cổ | 蠱 | ☶☴ | ✅ | [18-co.md](quẻ/18-co.md) |
| 19 | Lâm | 臨 | ☷☱ | ✅ | [19-lam.md](quẻ/19-lam.md) |
| 20 | Quán | 觀 | ☴☷ | ✅ raw_ocr | [20-quan.md](quẻ/20-quan.md) |
| 21 | Phệ Hạp | 噬嗑 | ☲☳ | ✅ raw_ocr | [21-phe-hap.md](quẻ/21-phe-hap.md) |
| 22 | Bí | 賁 | ☶☲ | ✅ raw_ocr | [22-bi.md](quẻ/22-bi.md) |
| 23 | Bác | 剝 | ☶☷ | ✅ | [23-bac.md](quẻ/23-bac.md) |
| 24 | Phục | 復 | ☷☳ | ⚠ partial | [24-phuc.md](quẻ/24-phuc.md) |
| 25 | Vô Vọng | 無妄 | ☰☳ | ⚠ canonical | [25-vo-vong.md](quẻ/25-vo-vong.md) |
| 26 | Đại Súc | 大畜 | ☶☰ | ✅ | [26-dai-suc.md](quẻ/26-dai-suc.md) |
| 27 | Di | 頤 | ☶☳ | ✅ | [27-di.md](quẻ/27-di.md) |
| 28 | Đại Quá | 大過 | ☱☴ | ⚠ partial | [28-dai-qua.md](quẻ/28-dai-qua.md) |
| 29 | Khảm (thuần) | 坎 | ☵☵ | ⚠ canonical | [29-kham.md](quẻ/29-kham.md) |
| 30 | Ly (thuần) | 離 | ☲☲ | ⚠ partial | [30-ly-hexagram.md](quẻ/30-ly-hexagram.md) |

### Hạ Kinh (34 quẻ sau — đạo người)

| # | Quẻ | Hán | Cấu trúc | OCR | File |
|---|---|---|---|---|---|
| 31 | Hàm | 咸 | ☱☶ | ✅ | [31-ham.md](quẻ/31-ham.md) |
| 32 | Hằng | 恆 | ☳☴ | ⚠ partial | [32-hang.md](quẻ/32-hang.md) |
| 33 | Độn | 遯 | ☰☶ | ⚠ canonical | [33-don.md](quẻ/33-don.md) |
| 34 | Đại Tráng | 大壯 | ☳☰ | ⚠ partial | [34-dai-trang.md](quẻ/34-dai-trang.md) |
| 35 | Tấn | 晉 | ☲☷ | ✅ | [35-tan.md](quẻ/35-tan.md) |
| 36 | Minh Di | 明夷 | ☷☲ | ✅ | [36-minh-di.md](quẻ/36-minh-di.md) |
| 37 | Gia Nhân | 家人 | ☴☲ | ⚠ canonical | [37-gia-nhan.md](quẻ/37-gia-nhan.md) |
| 38 | Khuê | 睽 | ☲☱ | ✅ | [38-khue.md](quẻ/38-khue.md) |
| 39 | Kiển | 蹇 | ☵☶ | ✅ | [39-kien.md](quẻ/39-kien.md) |
| 40 | Giải | 解 | ☳☵ | ✅ | [40-giai.md](quẻ/40-giai.md) |
| 41 | Tổn | 損 | ☶☱ | ✅ | [41-ton.md](quẻ/41-ton.md) |
| 42 | Ích | 益 | ☴☳ | ✅ | [42-ich.md](quẻ/42-ich.md) |
| 43 | Quải | 夬 | ☱☰ | ⚠ canonical | [43-quai.md](quẻ/43-quai.md) |
| 44 | Cấu | 姤 | ☰☴ | ⚠ canonical | [44-cau.md](quẻ/44-cau.md) |
| 45 | Tụy | 萃 | ☱☷ | ⚠ canonical | [45-tuy-hexagram.md](quẻ/45-tuy-hexagram.md) |
| 46 | Thăng | 升 | ☷☴ | ⚠ canonical | [46-thang.md](quẻ/46-thang.md) |
| 47 | Khốn | 困 | ☱☵ | ⚠ canonical | [47-khon-hexagram.md](quẻ/47-khon-hexagram.md) |
| 48 | Tỉnh | 井 | ☵☴ | ⚠ canonical | [48-tinh.md](quẻ/48-tinh.md) |
| 49 | Cách | 革 | ☱☲ | ⚠ canonical | [49-cach.md](quẻ/49-cach.md) |
| 50 | Đỉnh | 鼎 | ☲☴ | ⚠ canonical | [50-dinh.md](quẻ/50-dinh.md) |
| 51 | Chấn (thuần) | 震 | ☳☳ | ⚠ canonical | [51-chan.md](quẻ/51-chan.md) |
| 52 | Cấn (thuần) | 艮 | ☶☶ | ⚠ canonical | [52-can-hexagram.md](quẻ/52-can-hexagram.md) |
| 53 | Tiệm | 漸 | ☴☶ | ⚠ canonical | [53-tiem.md](quẻ/53-tiem.md) |
| 54 | Quy Muội | 歸妹 | ☳☱ | ⚠ canonical | [54-qui-muoi.md](quẻ/54-qui-muoi.md) |
| 55 | Phong | 豐 | ☳☲ | ⚠ canonical | [55-phong.md](quẻ/55-phong.md) |
| 56 | Lữ | 旅 | ☲☶ | ⚠ canonical | [56-lu.md](quẻ/56-lu.md) |
| 57 | Tốn (thuần) | 巽 | ☴☴ | ⚠ canonical | [57-ton-hexagram.md](quẻ/57-ton-hexagram.md) |
| 58 | Đoài (thuần) | 兌 | ☱☱ | ⚠ canonical | [58-doai.md](quẻ/58-doai.md) |
| 59 | Hoán | 渙 | ☴☵ | ⚠ canonical | [59-hoan.md](quẻ/59-hoan.md) |
| 60 | Tiết | 節 | ☵☱ | ⚠ canonical | [60-tiet.md](quẻ/60-tiet.md) |
| 61 | Trung Phu | 中孚 | ☴☱ | ⚠ canonical | [61-trung-phu.md](quẻ/61-trung-phu.md) |
| 62 | Tiểu Quá | 小過 | ☳☶ | ⚠ canonical | [62-tieu-qua.md](quẻ/62-tieu-qua.md) |
| 63 | Ký Tế | 既濟 | ☵☲ | ⚠ canonical | [63-ky-te.md](quẻ/63-ky-te.md) |
| 64 | Vị Tế | 未濟 | ☲☵ | ⚠ canonical | [64-vi-te.md](quẻ/64-vi-te.md) — QUẺ CUỐI |

### Ghi chú OCR

- ✅ = Full OCR Ngô Tất Tố p51-625
- ⚠ partial = OCR có Lời Kinh + Lời Thoán nhưng thiếu một số hào (canonical Trình Di fill)
- ⚠ canonical = OCR Ngô Tất Tố p665+ uncertain, dùng canonical Trình Di + Chu Hy paradigm thuần

Tất cả 64 đều có insight cốt + cross-ref đầy đủ.

## III. Pattern dùng

**Khi user hỏi qua sage/Hermes:**
1. Sage nhận intent (vd: "em sắp khởi nghiệp")
2. Sage check INDEX → route `tam-phap/khoi-dau.md`
3. Tam-phap file refs cụ thể `quẻ/03-truan.md` + `quẻ/04-mong.md`
4. Sage chỉ load 1-2 file (5-10k tokens), không dump cả 64 quẻ

**Khi sage cần trích dẫn chính xác 1 quẻ:**
- Load thẳng `quẻ/XX-name.md`

**Khi Mai Hoa luận sâu LLM gieo quẻ:**
- Engine `luan_sau_kinhdich.py` auto-lookup `_HEXAGRAM_TO_FILE` cho chính/biến/hỗ
- Inject 3-4 file deep (~10k tokens) + tâm-pháp file (~2k) vào DeepSeek prompt

## IV. SOUL contract cho các sage

Mai Hoa Sage / Tử Vi Sage SOUL nên có **đúng 1 section ngắn** trỏ về đây:

```markdown
## 🌊 Kế thừa Kinh Dịch
Khi cần tâm-pháp gốc, route qua `data/hermes_yi/skills/kinh-dich/INDEX.md`.
KHÔNG inject knowledge vào SOUL — load file theo intent.
```

Đó là tất cả. SOUL không phồng theo số sách đọc.

## V. API endpoints liên quan

| Endpoint | Mục đích |
|---|---|
| `POST /api/yi-wiki/maihoa/luan-sau-kinhdich` | Mai Hoa luận sâu (gieo quẻ + LLM với citation) |
| `GET /api/yi-wiki/kinh-dich/list` | Liệt kê 64 quẻ (browse) — NEW 2026-05-27 |
| `GET /api/yi-wiki/kinh-dich/que/{slug}` | Đọc trực tiếp 1 quẻ — NEW 2026-05-27 |
