# D03 - Timing Matrix (Dong/Tinh + Hop/Xung)

- Date (local): 2026-05-08
- Queue ID: `reading_ingest_queue_v1`
- Day ID: `D03`
- Status: `completed`

## 1) Session objective

Chuan hoa tang 2 cua ung ky:
- Hao Dung Than dong -> ngay Hop.
- Hao Dung Than tinh -> ngay Xung.

## 2) Implementation done

- Cap nhat `engine/luc_hao.py::calculate_timing`:
  - them `trigger_type` cho tung candidate.
  - them `primary_rule_id` trong ket qua de frontend/backend audit de dang.
  - matrix trigger hien tai:
    - `moving_to_harmony`
    - `static_to_clash`
    - `void_release`
    - `void_clash_activation`
    - `break_recovery_by_harmony`
    - `mai_hoa_formula`

## 3) Rules promoted in seed

- `timing.moving_to_harmony` -> `active`
- `timing.static_to_clash` -> `active`

Cap nhat tai:
- `data/seeds/luc_hao_rules_v1.json`

## 4) Tests added

- File: `tests/test_luc_hao_timing.py`
- Cases:
  - moving -> harmony
  - static -> clash
  - void release priority
  - always include mai hoa formula candidate

## 5) Next handoff

- D04: Tang Tuan Khong / Xung thuc chi tiet hon, bo sung edge-case cho cycle ngay chi.
