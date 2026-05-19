# Luc Hao Data Development Guide (Targeted Reading Mode)

Muc tieu tai lieu nay:
- Phat trien data Luc Hao theo huong co cau truc, de tim nhanh bang `rule_id`.
- Khong doc toan bo thu vien; chi doc pham vi trang/chuong phuc vu rule can ma hoa.

## 1) Tep du lieu da tao

- `data/seeds/luc_hao_source_index.json`
  - Chi luc nguon sach uu tien cho Luc Hao.
  - Co `source_id`, `domains`, `target_chapters`, `status`.
- `data/seeds/luc_hao_rules_v1.json`
  - Seed rule Luc Hao theo schema co san:
    - `rule_id`
    - `input_contract`
    - `logic_summary`
    - `output_contract`
    - `confidence`
    - `source_refs`
    - `status`
- `data/seeds/luc_hao_reading_queue.json`
  - Hang doi cong viec theo ngay (D01..D07) de trich rule co muc tieu.
  - Moi ngay gan voi `source_id` + `target_chapters` + `target_rule_ids`.

## 2) Quy trinh lam viec (khong doc ca thu vien)

1. Chon 1 `source_id` trong source index.
2. Chi doc `target_chapters` cua source do.
3. Trich toi da 3-5 rule moi/1 buoi.
4. Them vao `luc_hao_rules_v1.json` voi `status = draft`.
5. Neu co test va du evidence, doi sang `active`.

## 2.1) Lam viec theo ngay (theo goi y)

- Dung `luc_hao_reading_queue.json` lam backlog theo ngay.
- Moi ngay chi lam 1 `day_id`:
  - `queued -> extracting -> validated`.
- Khong lam nhieu sach cung luc neu khong nam trong `target_chapters`.

## 3) Quy uoc dat Rule ID

Format:
- `luc_hao.<domain>.<topic>`

Vi du:
- `luc_hao.core.the_ung_mapping`
- `luc_hao.calendar.tuan_khong`
- `luc_hao.interpret.moving_line_impact`

## 4) Tieu chuan chat luong cho moi rule

Moi rule moi phai co:
- input ro rang (khong mo ho)
- output testable
- source reference cu the
- confidence muc ban dau (`low/medium/high`)

Neu khong du 4 dieu kien tren -> khong dua vao deterministic core.

## 5) Cach tra cuu nhanh trong code

Su dung module:
- `core/luc_hao_data.py`

Ham san co:
- `load_luc_hao_source_index()`
- `load_luc_hao_rules()`
- `load_luc_hao_reading_queue()`
- `list_luc_hao_rules(status=None)`
- `get_luc_hao_rule(rule_id)`
- `list_luc_hao_reading_days(status=None)`

## 6) Muc tieu gan han

- Lap day bo core Luc Hao toi thieu:
  - The/Ung
  - Luc Than
  - Tuan Khong
  - Nguyet Pha/Nhat Pha
  - Anh huong hao dong vao hao The

Sau khi hoan thanh, moi nang cap sang than sat nang cao.
