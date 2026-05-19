# D02 - Dung Than Domain Mapping

- Date (local): 2026-05-08
- Queue ID: `reading_ingest_queue_v1`
- Day ID: `D02`
- Status: `completed`

## 1) Session objective

Chot rule xac dinh doi tuong cau hoi de map dung nhom Dung Than ngay tu dau vao.

## 2) Rules delivered

### Rule 01 - `luc_hao.domain_relation_mapping`

- Input:
  - `question_text`
- Logic:
  - Nhan dien domain bang tu khoa:
    - tien tai -> `The Tai`
    - cong viec/su nghiep/phap ly -> `Quan Quy`
    - suc khoe -> `Quan Quy`
    - gia dinh/hon nhan/cha me -> `Phu Mau`
    - con cai/an nhan -> `Tu Ton`
- Output:
  - `target_relation`
- Constraint:
  - Khong co keyword -> de trong, xu ly fallback o rule selector.

### Rule 02 - `luc_hao.dung_than_selector.v2`

- Input:
  - `question_text`
  - `lines[].luc_than`
  - `lines[].moving`
- Logic:
  - Neu tim thay line co `luc_than == target_relation` -> chon line do.
  - Neu khong tim thay -> chon hao dong dau tien.
  - Neu khong co hao dong -> chon hao 3 (baseline v1).
- Output:
  - `dung_than_line`

## 3) Code changes

- `engine/luc_hao.py`
  - them `QUESTION_DOMAIN_RELATION_MAP`
  - them `_detect_target_relation()`
  - cap nhat `_select_dung_than_line()` theo v2 selector.
- `data/seeds/luc_hao_rules_v1.json`
  - bo sung 2 rule moi cho D02.
- `tests/test_luc_hao_selector.py`
  - test domain mapping + fallback logic.

## 4) Validation

- Chay test selector va api smoke:
  - `tests/test_luc_hao_selector.py`
  - `tests/test_api.py` (khuyen nghi chay lai de bao dam khong vo contract)

## 5) Next handoff

- D03: ung ky tang 2 voi matrix Dong/Tinh + Hop/Xung.
