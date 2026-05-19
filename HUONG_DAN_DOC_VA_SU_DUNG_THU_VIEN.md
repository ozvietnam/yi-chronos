# Huong dan doc va su dung thu vien sach

Tai lieu nay giup ban doc thu vien sach trong du an theo cach co he thong, de bien tri thuc thanh nang luc code duoc (khong doc xong roi de do).

## 1) Muc tieu cua viec doc

Du an hien tai la `YI-CHRONOS MVP` voi loi:

- Tinh trang thai thoi gian (Can-Chi, tiet khi, pha trang) trong `core/chronos.py`.
- Bieu dien trang thai Dich hoc (64 que, hao dong, que bien) trong `core/hexagram.py`.
- Lop ca nhan hoa + prompt kiem chung trong `engine/personal.py`.
- Lop diem so va dong bo trong `engine/scoring.py` va `engine/resonance.py`.
- Vong phan hoi nguoi dung trong `/api/feedback` va bang `feedback_event`.

Vi vay, viec doc sach phai phuc vu 3 cau hoi:

1. Quy tac nao co the ma hoa thanh ham tinh toan?
2. Quy tac nao co the kiem chung bang du lieu feedback?
3. Quy tac nao chi nen de o layer dien giai (khong dua vao loi tinh)?

## 2) Thu tu doc khuyen nghi

### Chang A - Nen tang Dich hoc (doc truoc)

Muc tieu: hieu ngon ngu he thong (que/hao/tuong), khong voi "doan".

- `Dich hoc tinh hoa Nguyen Duy Can.pdf`
- `Kinh Dich Tron Bo - Ngo Tat To - khoahoctamlinh.vn.pdf`
- `Bi an cua bat quai.pdf`

Output bat buoc sau chang A:

- 1 file ghi chu "tu dien thuat ngu" (que, hao, am/duong, dong/tinh, bien).
- 1 bang mapping tam thoi: "khai niem -> co the ma hoa hay khong".

### Chang B - Lich phap va Can-Chi (song hanh voi chronos)

Muc tieu: cung co truc thoi gian hoc, vi day la dau vao cua toan bo he thong.

- `Hoang lich.pdf`
- `Nguyen ly chon ngay theo lich Can Chi.pdf`
- `12 con giap theo lich van nien.pdf`
- `chon viec theo lich am.pdf`

Output bat buoc sau chang B:

- Checklist "Cong thuc can co" cho `chronos.py`:
  - chu ky 60
  - tiet khi
  - quy tac gio Chi
  - cach dat moc thoi gian theo timezone
- Danh sach diem "chua chac chan" can doi chieu them voi nguon chinh thong.

### Chang C - Tu tru/Tu binh cho lop ca nhan hoa

Muc tieu: nang cap `personal.py` theo huong co cau truc, khong than bi hoa.

- `Du Bao Theo Tu Binh.pdf`
- `Tu-xem-van-menh-theo-tu-tru.pdf`
- `Trich Thien tuy binh chu (Full)- Nham Thiet Tieu.pdf`
- `Thien nhan hoc co dai trich thien tuy.pdf`

Output bat buoc sau chang C:

- De xuat bo feature ca nhan moi (co trong so ro rang).
- Danh sach prompt moc kiem chung bo sung (suc khoe/cong viec/quan he).

### Chang D - Ky thuat du doan va vi du co giai (doc sau cung)

Muc tieu: rut ra "rule testable", khong copy nguyen van luan giai.

- `Nhap-Mon-Chu-Dich-Du-Doan-Hoc.pdf`
- `Chu Dich Du Doan Cac Vi Du Co Giai - Thieu Vi Hoa.pdf`
- `Chu dich voi du doan hoc.pdf`
- `Tang San Boc Dich.pdf`
- `DON TOAN THAN DIEU.pdf`
- `KhongMinhThanToan 384Que.pdf`

Output bat buoc sau chang D:

- Moi quy tac phai co dang:
  - Input:
  - Rule:
  - Output:
  - Muc do tu tin:
  - Cach test bang feedback:

## 3) Cach doc moi cuon (khung thuc thi 90 phut)

Moi buoi doc dung khung nay:

1. 20 phut quet muc luc + chuong lien quan truc tiep toi du an.
2. 40 phut doc ky 1-2 chuong trong tam.
3. 20 phut trich 3-5 quy tac co the ma hoa.
4. 10 phut ghi "action coding" cho ngay hom sau.

Khong dat muc tieu "doc het sach". Dat muc tieu "lay duoc rule de code".

## 4) Mau ghi chu de bien tri thuc thanh code

Tao file ghi chu theo mau sau:

```text
Ten sach:
Chuong:

1) Kien thuc cot loi:
- ...

2) Quy tac co the ma hoa:
- Rule ID:
  Input:
  Logic:
  Output:
  Gioi han:

3) Quy tac chi nen de o layer dien giai:
- ...

4) Lien ket toi code:
- core/chronos.py: ...
- core/hexagram.py: ...
- engine/personal.py: ...
- engine/scoring.py: ...

5) Bai test can them:
- ...
```

## 5) Cach su dung thu vien de nang cap du an (workflow thuc te)

Moi tuan dung vong lap:

1. Doc va trich 5-10 quy tac.
2. Chon 1-2 quy tac de dua vao code.
3. Them test trong `tests/`.
4. Chay test va doi chieu output.
5. Theo doi phan hoi that tu `feedback_event`.

Neu quy tac lam ket qua xau hon (feedback giam), dua quy tac ve layer dien giai.

## 6) Quy tac chat luong khi "ap dung sach"

- Khong dua quy tac mo ho vao deterministic core.
- Moi quy tac moi phai co test.
- Uu tien quy tac co the lap lai, khong phu thuoc "cam giac nguoi giai".
- Tach ro "rule tinh toan" va "van ban dien giai".
- Giu provenance: ghi ro sach nao, chuong nao.

## 7) Danh sach doc nhanh theo muc tieu

Neu ban can nang cap nhanh:

- Can nang cap `chronos.py`:
  - `Hoang lich.pdf`
  - `Nguyen ly chon ngay theo lich Can Chi.pdf`
- Can nang cap `hexagram.py`:
  - `Kinh Dich Tron Bo - Ngo Tat To - khoahoctamlinh.vn.pdf`
  - `Bi an cua bat quai.pdf`
- Can nang cap `personal.py`:
  - `Du Bao Theo Tu Binh.pdf`
  - `Trich Thien tuy binh chu (Full)- Nham Thiet Tieu.pdf`
- Can nang cap prompt/feedback:
  - `Chu Dich Du Doan Cac Vi Du Co Giai - Thieu Vi Hoa.pdf`
  - `Nhap-Mon-Chu-Dich-Du-Doan-Hoc.pdf`

## 8) Ke hoach 14 ngay de vao guong

- Ngay 1-3: Chang A (nen tang Dich hoc).
- Ngay 4-6: Chang B (lich phap, Can-Chi).
- Ngay 7-10: Chang C (tu tru, ca nhan hoa).
- Ngay 11-14: Chang D (rule du doan + testability).

Moi ngay ket thuc bang 1 commit nho (neu co thay doi code/test), hoac 1 file note ro rang (neu chua code).

## 9) Dinh nghia thanh cong

Huong dan nay co gia tri khi:

- Ban doc xong biet chinh xac "quy tac nao dua vao loi".
- So test tang len theo tung chang doc.
- Feedback that tu nguoi dung giup loc quy tac tot/xau.
- Thu vien sach tro thanh "nguon rule co kiem chung", khong phai "kho quote".

