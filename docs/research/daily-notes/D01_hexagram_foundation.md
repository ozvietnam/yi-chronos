# D01 - Hexagram Foundation (Rule-first)

- Date (local): 2026-05-08
- Queue ID: `reading_ingest_queue_v1`
- Day ID: `D01`
- Status: `completed`

## 1) Session objective

Khoa 3 rule nen tang de bao dam:
- identity 64 que la deterministic,
- line indexing khong lech quy uoc,
- transform line hoat dong dung theo hao dong 1..6.

## 2) Evidence source used in this run

Do chua co file sach `Kinh Dich Tron Bo - Ngo Tat To` trong workspace, D01 nay su dung:

- `core/hexagram.py` (co `SOURCE_REF` tro den Ngo Tat To edition).
- `tests/test_hexagram.py` lam bang chung regression.

Ghi chu:
- Khi file sach goc duoc nap vao thu vien, se bo sung doi chieu provenance theo chuong/trang.

## 3) Extracted rules (D01 deliverables)

### Rule 01 - `yi.core.hexagram_identity`

- Input:
  - `KING_WEN_TABLE`
  - `TRIGRAM_BITS`
- Logic:
  - Sinh 64 que theo thu tu King Wen, moi que gom:
    - `king_wen_index`
    - `binary` (6 bit)
    - `upper_trigram`, `lower_trigram`
  - Rang buoc uniqueness:
    - 64 `binary` duy nhat
    - 64 `id` duy nhat
    - 64 `king_wen_index` duy nhat
- Output:
  - `HEXAGRAMS`, `_BY_BINARY`, `_BY_NAME`
- Constraint:
  - Binary phai dung 6 ky tu `0/1`.
- Test:
  - `test_canonical_qian_and_kun_binary_mapping`
  - `test_all_hexagrams_are_unique_and_transitions_are_valid`
  - `test_king_wen_index_and_binary_are_complete`
- Confidence: `high`

### Rule 02 - `yi.core.line_indexing`

- Input:
  - `binary`
  - `line` (1..6)
- Logic:
  - Quy uoc Dịch:
    - `line 1` = hao duoi cung
    - `line 6` = hao tren cung
  - Cong thuc index tren chuoi top-down:
    - `index = 6 - line`
- Output:
  - Vi tri can dao bit dung quy uoc line.
- Constraint:
  - `line` ngoai [1,6] -> invalid.
- Test:
  - `test_line_flip_uses_line_one_as_bottom_line`
- Confidence: `high`

### Rule 03 - `yi.core.transform_line`

- Input:
  - `binary`
  - `moving_lines` (iterable)
- Logic:
  - `flip_line(binary, line)` dao 1 hao theo Rule 02.
  - `apply_moving_lines`:
    - dedupe
    - sort tang dan
    - flip lan luot
  - `generate_transitions`:
    - tao 6 bien the ung voi 6 hao dong don.
- Output:
  - `transformed_binary`
  - `transitions{line -> binary}`
- Constraint:
  - Binary dau vao phai hop le.
- Test:
  - `test_compose_hexagram_and_moving_lines`
  - `test_all_hexagrams_are_unique_and_transitions_are_valid`
- Confidence: `high`

## 4) Action coding done

- [x] Chot 3 rule nen tang co the code/test duoc.
- [x] Ghi note D01 theo template rule-first.
- [x] Dong bo status D01 trong `reading_ingest_queue_v1.json` -> `completed`.

## 5) Pending for provenance hardening

- [ ] Bo sung file sach goc `Ngo Tat To` vao thu vien.
- [ ] Gan reference theo chuong/trang vao tung rule D01.

## 6) Next handoff

Day tiep theo: `D02` - Dung Than theo domain cau hoi va matrix uu tien.
