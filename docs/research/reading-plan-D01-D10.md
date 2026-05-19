# Ke hoach doc sach de nang chat luong ket qua (D01-D10)

Muc tieu:
- Tang do dung va do on dinh cua Dung Than + Ung Ky.
- Giam rule mo ho trong core; rule khong test duoc dua ve layer dien giai.

## 1) Nguyen tac thuc thi

- Moi ngay trich 3-5 rule co the code.
- Moi rule theo mau:
  - `Input`
  - `Logic`
  - `Output`
  - `Dieu kien loai tru`
  - `Test case`
  - `Provenance (sach/chuong)`
- Ket ngay phai co 1 trong 2:
  - cap nhat file rule seed, hoac
  - note ky thuat + pending test ro rang.

## 2) Danh sach uu tien sach

### Bat buoc truoc (P0)

1. `Kinh Dich Tron Bo - Ngo Tat To`
2. `Chu Dich Du Doan Hoc`
3. `Chu Dich Du Doan Cac Vi Du Co Giai`
4. `Tang San Boc Dich`

### Bo tro nang cap (P1)

5. `Nhap Mon Chu Dich Du Doan Hoc`
6. `Don Toan Than Dieu`
7. `Khong Minh Than Toan 384 Que`
8. `Hoang Lich`
9. `Nguyen Ly Chon Ngay Theo Lich Can Chi`

### Co san trong workspace (P2)

10. `Tam Thien Dich So`

## 3) Lich D01-D10 (ban thao tac)

- D01: Khoa nen 64 que va mapping hao.
- D02: Dung Than co ban theo domain cau hoi.
- D03: Ung ky dong/tinh theo hop/xung.
- D04: Tuan Khong va xung thuc.
- D05: Nguyet Pha/Nhat Pha va dieu kien go pha.
- D06: Phuc Than/An Than va trigger ung ky.
- D07: Chuan hoa matrix phieu loc ung ky 3 tang.
- D08: Chinh lich phap Can-Chi de giam sai so ngay gio.
- D09: Doi chieu casebook voi feedback thuc te.
- D10: Chot rulepack v2, test report, rollout checklist.

Chi tiet machine-readable nam o:
- `data/seeds/reading_ingest_queue_v1.json`

## 4) Tieu chi "rule du dieu kien vao core"

Rule duoc vao core neu dat tat ca:

1. Co input xac dinh, khong can cam giac nguoi giai.
2. Co test co the lap lai.
3. Co provenance ro rang.
4. Co tac dong duong khi doi chieu feedback.

Neu khong dat, rule chi o layer dien giai.
