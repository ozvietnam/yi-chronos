# PLAN đọc sâu — "Học Thuyết Âm Dương Ngũ Hành" (Lê Văn Sửu, 251 trang)

> Anh chốt 2026-06-13: *"em vừa đọc vừa hiệu chỉnh wiki đưa lên web và làm backend 1 vòng nhé,
> soát lại skill đọc sâu và làm những việc cần thiết 1 vòng trước khi đọc."*
> Kỷ luật: skill `~/.claude/skills/doc-sau-20-trang.md` — 20 trang/vòng, journal 10 mục,
> Phase A Engine + Phase B Wiki xử lý NGAY trong vòng, Phase C UX/UI ghi task.

## Việc cần thiết đã làm TRƯỚC khi đọc (2026-06-13)

1. ✅ Soát lại skill đọc sâu (đọc full, nhắc anti-pattern 2026-06-03)
2. 🚨 **Phát hiện bản OCR cũ THIẾU 100 trang đầu** (chỉ có p101-251) — nếu đọc ngay sẽ
   thâm nhuần nửa cuốn mà tưởng cả cuốn. PDF gốc có text layer nhưng là rác CID
   → chạy lại OCR Tesseract p1-100 (300 DPI), backup bản cũ `content_p101_251.bak.md`,
   merge thành content.md đủ 251 trang.
3. ✅ Script ingest vòng đọc: `scripts/ingest_reading_round.py` — mỗi vòng 1 chunk
   (text 20 trang) + atoms đúc kết → wiki.sqlite3, corpus `hoc-thuyet-am-duong-ngu-hanh`,
   idempotent theo (corpus, from_page, to_page).
4. ✅ Đích web/backend mỗi vòng: atoms vào wiki (tra cứu được) + tri thức nền bồi vào
   `engine/tu_vi/ngu_hanh_nen.py` (`vong_sinh_khac()` / nhận định sinh khắc) +
   trang 📖 kiến thức nền trong ChinhTinhLibraryPanel.

## Lịch vòng (251 trang ≈ 13 vòng)

| Vòng | Trang | Ghi chú |
|---|---|---|
| 1 | p1-20 | (sau khi OCR p1-100 xong) — dự kiến: nguồn gốc học thuyết |
| 2 | p21-40 | |
| 3 | p41-60 | |
| 4 | p61-80 | |
| 5 | p81-100 | |
| 6-13 | p101-251 | bản OCR cũ đã có (đã thấy: ngũ vận lục khí, đồng dạng y học) |

Mỗi vòng: đọc full → journal `am-duong-ngu-hanh-vong-N-pXXX-pYYY.md` (10 mục) →
ingest wiki → backend/web nếu có paradigm cốt → commit → câu hỏi cho Anh.
Nhịp: dừng hỏi Anh sau MỖI vòng (Anh đang muốn review từng vòng).

## Trạng thái

- [ ] OCR p1-100 (đang chạy nền)
- [ ] Merge content.md 251 trang + update manifest
- [ ] Vòng 1 (p1-20)
