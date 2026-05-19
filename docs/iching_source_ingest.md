## I Ching Source Ingest (Ngô Tất Tố)

- Active reference book:
  - `thư viện sách/Kinh Dịch Trọn Bộ - Ngô Tất Tố - khoahoctamlinh.vn.pdf`
- Current status:
  - Core 64-hexagram catalog is normalized and linked to source provenance.
  - Full paragraph-level `quẻ từ` / `hào từ` extraction is pending because the local source file is stored in a mixed HTML/PDF wrapper format.

### Next ingest step

1. Convert the source into a clean text/PDF stream.
2. Segment each hexagram section (`QUẺ ...`) into:
   - `judgement_text` (quẻ từ / thoán từ)
   - `line_texts[1..6]` (hào từ)
3. Save as:
   - `data/seeds/hexagram_texts_ngotatto.json`
4. Add regression tests for:
   - non-empty judgement for all 64 hexagrams
   - 6 line texts per hexagram
   - source span/provenance per excerpt
