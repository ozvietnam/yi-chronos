# D04 - Tuan Khong va Xung thuc

- Date (local): 2026-05-08
- Queue ID: `reading_ingest_queue_v1`
- Day ID: `D04`
- Status: `completed`

## 1) Session objective

Chuan hoa xu ly ung ky khi Dung Than roi vao Tuan Khong:
- uu tien moc Ra Khong,
- giu candidate Xung thuc lam kich hoat phu.

## 2) Implementation updates

- File: `engine/luc_hao.py`
  - cap nhat `_days_until_branch()`:
    - truoc: cung chi -> `12`
    - sau: cung chi -> `0` (co the ung ngay hien tai)
  - khong doi contract `calculate_timing`, chi lam chinh xac offset.

## 3) Rules finalized

- `timing.void_release` -> active
- `timing.void_by_clash_activation` -> active

## 4) Tests added

- File: `tests/test_luc_hao_void_timing.py`
  - `test_void_release_can_be_today_when_branch_matches`
  - `test_void_clash_activation_is_secondary_candidate`

## 5) Practical impact

- UI ung ky co the hien thi `D+0` khi dung ngay Ra Khong.
- Candidate list van giu moc Xung thuc de nguoi dung co phuong an theo doi tiep.

## 6) Next handoff

- D05: xu ly Nguyet Pha/Nhat Pha va dieu kien go pha uu tien.
