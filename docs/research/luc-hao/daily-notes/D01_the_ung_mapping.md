# D01 - The/Ung Mapping Foundation

- Date (local): 2026-05-08
- Queue status: extracting
- Source ID: `book_nhap_mon_chu_dich_du_doan_hoc`
- Target chapters:
  - chuong lap que va an hao
  - chuong the hao - ung hao
- Target rule IDs:
  - `luc_hao.core.the_ung_mapping`

## 1) Session objective

Trich quy tac xac dinh hao The/Ung theo cung que, de chot duoc:
- input contract ro rang,
- bang mapping co the code duoc,
- dieu kien gioi han va variant.

## 2) Evidence extraction log

## Evidence 01
- Source fragment:
  - (dien sau khi doc dung doan muc tieu)
- Candidate rule:
  - Input:
  - Logic:
  - Output:
  - Constraint:
- Confidence:

## Evidence 02
- Source fragment:
  - (dien sau khi doc dung doan muc tieu)
- Candidate rule:
  - Input:
  - Logic:
  - Output:
  - Constraint:
- Confidence:

## 3) Rule draft update checklist

- [ ] Cap nhat `luc_hao.core.the_ung_mapping` trong `data/seeds/luc_hao_rules_v1.json`
- [ ] Bo sung `source_refs` cu the hon
- [ ] Chot confidence (`medium` -> `high` neu du bang chung)
- [ ] Them test case cho mapping The/Ung

## 4) End-of-day decision

- [ ] Giu `status = draft`
- [ ] Nang len `status = active` (chi khi du test + evidence)

## 5) Next handoff

Neu xong D01:
- chuyen `D01` -> `validated`
- chuyen `D02` -> `extracting`
