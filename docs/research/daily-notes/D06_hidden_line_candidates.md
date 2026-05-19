# D06 - Hidden Line Candidates (Phuc/An than v1)

- Date (local): 2026-05-08
- Day ID: `D06`
- Status: `completed`

## Deliverables

- Them `_detect_hidden_line_candidates()` trong `engine/luc_hao.py`.
- Tra ve `hidden_line_candidates` trong payload cast de phuc vu tang danh gia tiep theo.
- Them rule seed:
  - `luc_hao.hidden_line_detection` (active)
  - `timing.hidden_line_trigger` (draft)
- Them test:
  - `test_hidden_line_candidates_detect_same_relation_static_lines`

## Notes

- Ban v1 khong override best timing match; chi bo sung candidate de doi chieu va huan luyen.
