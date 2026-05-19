# Tử Vi Đẩu Số Toàn Thư — Thâm nhuần Quyển 1

**Nguồn**: Hi Di Trần tiên sinh (陳摶 / Trần Đoàn), 紫微斗数全书, Quyển 1 (64 trang = OCR p0016-p0079)
**Phương pháp**: DeepSeek-chat (trích cách cục + concepts structured) + MiniMax-M2 (tóm tắt VN dễ hiểu) chạy song song, em (Claude) đọc rà → synthesize.
**Cost**: ~$0.31 toàn Q1 (DeepSeek) + $0 (MiniMax via plan).
**Trạng thái**: 🚧 đang viết — chờ batch 2 (p26-79) chạy xong rồi điền các phần II-VI.

---

## I. Cấu trúc Quyển 1 (qua mục lục)

Theo mục lục PDF (p0009-0011) + OCR markers, sách Toàn Thư chia 4 quyển:

| Quyển | Source page | OCR page | Chủ đề |
|---|---|---|---|
| 1 | 1-64 | p0016 → p0079 | **Phú Thái Vi · các bài phú khai môn · định nghĩa cách cục** |
| 2 | 65-126 | p0080 → p0141 | An mệnh, an sao, 12 cung, các sao chính/phụ/sát |
| 3 | 127-183 | p0142 → p0198 | Diễn giải 12 cung × 14 chính tinh (168 combos) |
| 4 | 184-? | p0199 → p0300 | Case studies 60+ lá số cổ kim |

Quyển 1 = **nền móng lý thuyết** — đọc xong mới hiểu các quyển sau dùng những "ngôn ngữ" gì.

---

## II. Phú Thái Vi — bài khai môn

Bắt đầu từ p0016 r004-l001: **"Thái Vi phú"**.

> _"Đẩu số chí huyền chí vi, lý chỉ dị minh."_
> — (Đẩu Số vốn rất huyền vi sâu xa, nhưng lý vẫn có thể làm sáng tỏ)

Đây là **manifesto** giống Vận Pháp Thi của Q3 Mai Hoa:
- Đẩu số = **tinh chế** (huyền vi) nhưng có **nguyên lý** (lý chỉ dị minh)
- KHÔNG mê tín, có thể luận giải bằng khái niệm rõ ràng
- Mỗi sao có chỗ thuộc (phân dã); thọ yểu hiền ngu, phú quý bần tiện đều có quy luật

### Bố cục Phú Thái Vi (theo trích xuất DeepSeek)
- **Khai môn**: tổng quát phương pháp xét sao (vào miếu, thất độ, kiêm sát chế hóa)
- **Lệ thí dụ**: liệt kê hàng chục cách cục → mỗi cách 1 câu sấm
- **Tổng kết**: nhấn mạnh tinh thần "biến hóa" — sao tốt gặp xấu thành xấu, sao xấu gặp tốt thành tốt

---

## III. Top 30 cách cục kinh điển

_(Em sẽ điền sau khi batch p26-79 xong + merge masters)_

Sẽ liệt kê dạng:

```
| Cách | Cấp | Điều kiện | Ý nghĩa | Page nguồn |
```

Mỗi cách dùng `data/yi_publishing/q1_tuvi/master/cach_cuc_index.json` làm ground truth.

---

## IV. Concepts / Thuật ngữ chuyên biệt Q1

_(Điền sau merge — dự kiến ~200-300 concepts)_

Sẽ phân loại:
- **Sao**: 14 chính tinh + Tả Phụ Hữu Bật + Văn Xương Văn Khúc + ...
- **Hóa**: Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ
- **Biến cách**: Tam Hóa Liên Châu, Đắc Viên, Thất Độ, Tuần Không, ...
- **Cung**: 12 cung + Đắc địa / Hãm địa / Miếu vượng

---

## V. Insight (em rút sau khi đọc toàn quyển)

_(Sẽ viết sau khi đã read xong + cross-reference với Phú Thái Vi đã có 3-layer + 8 đề xuất engine từ 20 trang đầu)_

Câu hỏi em phải trả lời:
1. **Cách "đọc đồng dạng" trong Tử Vi tương đồng / khác Mai Hoa thế nào?**
2. **Mệnh chủ + Thân chủ + Đẩu Quân (3 sao 12 cung mới mà engine đã thêm) thực sự dùng ra sao trong Phú Thái Vi?**
3. **8 cách cục cho lá số founder DeepSeek trả runtime có khớp với cách kinh điển Phú Thái Vi mô tả không?** (Verify accuracy)
4. **Có chỗ nào Quyển 1 nói rõ "khi nào nên / không nên xem Tử Vi"** (giống quy tắc Tâm của Mai Hoa: không nghi không bói)?

---

## VI. Đề xuất engine update (kết quả thâm nhuần)

_(Sẽ refine 8 đề xuất ban đầu trong `docs/TUVI-Q4-PANEL-UPGRADE-PROPOSAL.md` thành plan cụ thể)_

Các candidate:
1. **`cach_cuc_dictionary.json`**: build từ master/cach_cuc_index.json → engine lookup runtime thay vì DeepSeek-on-the-fly
2. **Phú Thái Vi nguyên văn + layer 3** (đã có) — verify lại sau khi đối chiếu
3. **Quy tắc "Tâm" cho Tử Vi** (nếu sách có) → Iron Rule #6 (nếu cần)
4. **Lookup table "concept → định nghĩa"** dùng cho WikiText highlight
5. **Cảnh báo: KHÔNG predict, ĐỌC đồng dạng** — paradigm tương tự Mai Hoa

---

## VII. Quy trình orchestration (DeepSeek + MiniMax parallel)

Em đã thiết kế `engine/yi_publishing/q1_thamnhuan.py`:

```
            ┌──────────────────────────┐
            │  read_page_content(p)    │  ← từ tuvidauso-zh/p{N:04d}/r*.json
            └──────────────┬───────────┘
                           │ {hv, lg, lines_count}
                           ▼
            ┌──────────────────────────┐
            │  ThreadPoolExecutor      │
            │  max_workers=2 (per page)│
            └──────┬───────────────┬───┘
                   │               │
        ┌──────────▼────┐   ┌──────▼─────────────┐
        │ DeepSeek-chat │   │ MiniMax-M2          │
        │ structured    │   │ paragraph summary   │
        │ ~$0.005/page  │   │ ~$0 (plan)          │
        │ ~10-15s       │   │ ~20-25s             │
        └──────┬────────┘   └──────┬──────────────┘
               │                   │
               └─────────┬─────────┘
                         ▼
            ┌──────────────────────────┐
            │  per_page/p{N:04d}.json  │  ← cached, idempotent
            └──────────────┬───────────┘
                           │
                           ▼ (after all pages)
            ┌──────────────────────────┐
            │  merge_masters()         │
            │  → cach_cuc_index.json   │  (dedup by ten)
            │  → concepts_index.json   │  (dedup by term)
            │  → page_summaries.md     │
            └──────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  Em (Claude) đọc rà →    │
            │  viết tay journal này    │
            │  (Insight, Iron Rule)    │
            └──────────────────────────┘
```

**Bounded concurrency**:
- Mỗi page = 2 calls song song (1 DeepSeek + 1 MiniMax)
- 4 page xử lý song song = **8 calls đồng thời** max
- DeepSeek free tier rate limit ~60 RPM → 8 concurrent OK
- MiniMax coding plan → unlimited-ish

**Safety**:
- Cache `per_page/p*.json` → re-run idempotent
- JSON parse loose (tolerate truncated)
- Silent fail per page (1 trang lỗi không kill batch)

---

## VIII. Update log

| Ngày | Sự kiện |
|---|---|
| 2026-05-19 21:53 | Pilot p0016 — DeepSeek json parse fail (tăng max_tokens 3000→8000 + loose parse fallback) |
| 2026-05-19 21:54 | Pilot p0016 retry — PASS. 1 cách cục, 7 concepts, $0.0048 |
| 2026-05-19 21:55 | Batch p16-25 — 10 pages PASS, 125 cách cục, 109 concepts, $0.0418, 58s |
| 2026-05-19 21:56 | Batch p26-79 — 54 pages running in background |
| TBD | Merge masters + write sections III-VI |

---

_Đây là journal sống — sẽ tiếp tục cập nhật trong session này và các session sau._
