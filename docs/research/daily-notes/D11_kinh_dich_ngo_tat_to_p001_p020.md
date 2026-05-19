# D11 - Kinh Dich Tron Bo (Ngo Tat To), p.001-020

## Provenance
- Source: `thư viện sách/Kinh Dich Tron Bo - Ngo Tat To.pdf`
- Range reviewed: pages 1-20 (ebook pagination)
- Focus: foundation terms and rules that can be encoded for Page 2 engine (Mai Hoa + Luc Hao)

## 1) Kien thuc cot loi
- Kinh Dich duoc trinh bay theo lop: he vach (Phuc Hy) -> Loi Que/Thoan (Van Vuong) -> Loi Hao (Chu Cong) -> Thap Duc/Truyen (Khong Tu).
- Quẻ co 2 cap: `quẻ don (8 quái)` va `quẻ kep (64 quẻ)`.
- Hào co tinh chat `am/duong`, vi tri `1..6`, va quan he vi tri (`chinh`, `trung`, `ung`).
- Tac gia nhan manh can tach `Tuong` (hinh tuong) va `Chiêm` (loi doan), khong tron hai lop.
- Ban dich co tinh chu giai cao, can dung theo nguyen tac provenance (khong tuyet doi hoa 1 cach chu giai).

## 2) Quy tac co the ma hoa

### Rule ID: ngo_tat_to_r01_hexagram_structure
- Input: upper/lower trigram
- Logic: tao quẻ kep tu 2 quẻ don, luon bao toan 6 hào theo thu tu tu duoi len.
- Output: `hexagram.lines[6]`, `upper_trigram`, `lower_trigram`
- Gioi han: chi la ket cau, khong tu sinh loi doan.

### Rule ID: ngo_tat_to_r02_line_position_semantics
- Input: line index 1..6, line polarity (am/duong)
- Logic:
  - `vi tri`: 1-6
  - `chinh`: duong o vi tri le, am o vi tri chan
  - `trung`: vi tri 2 va 5
  - `ung`: cap (1,4), (2,5), (3,6) va phai khac am/duong moi tinh la co ung
- Output: metadata cho moi hao: `is_correct`, `is_center`, `is_corresponding`
- Gioi han: van can ket hop boi canh quẻ de luan tot/xau.

### Rule ID: ngo_tat_to_r03_tuong_chiem_split
- Input: text segment cho tung hào/quẻ
- Logic: tach cau mo ta hinh tuong (Tuong) va cau mang tinh huong dan/cat-hung (Chiêm)
- Output: `imagery_text`, `judgement_text`, `judgement_polarity`
- Gioi han: can mot bo parser text theo mau ngon ngu co dien.

### Rule ID: ngo_tat_to_r04_judgement_scale
- Input: judgement token (cat, hanh, loi, vo hoi, hung, le, lan, huu cuu...)
- Logic: map token vao thang chat luong 3 muc
  - positive: `nguyen cat`, `cat hanh`, `cat`, `hanh`, `loi`
  - neutral/mixed: `vo hoi`, `vo cuu`, `huu hoi`, `huu cuu`
  - negative: `hung`, `le`, `lan`, `vo du loi`
- Output: `decision_quality` (favorable / mixed / regret-risk)
- Gioi han: can uu tien bo canh toan cau khi xuat hien nhieu token trai chieu.

### Rule ID: ngo_tat_to_r05_interpretation_uncertainty_flag
- Input: so luong cach hieu co the cua cung 1 doan
- Logic: neu parser tim thay >1 cach tach nghia hop le thi gan co `ambiguity_flag=true`
- Output: `source_bias_note`, `confidence_adjustment`
- Gioi han: day la co che giam do tu tin, khong phai co che ket luan.

## 3) Quy tac chi nen de o layer dien giai
- Cac doan dan giai lich su truyen thuya Phuc Hy long ma/ha do chi nen de background.
- Cac nhan dinh phe binh hoc phai (Trinh Di vs Chu Hy) dung cho provenance, khong dua thang vao deterministic scoring.

## 4) Lien ket toi code
- `core/hexagram.py`: bo sung metadata vi tri hao (`chinh/trung/ung`) neu chua co day du.
- `engine/luc_hao.py`: doi chieu bo `decision_quality` voi thang token cat-hung tu text.
- `core/hexagram_texts.py`: bo sung schema tach `tuong_text` vs `chiem_text`.
- `docs/research/mai-hoa/mai-hoa-ruler-notes-v1.md`: them provenance cum rule moi theo nguon Ngo Tat To (P1-20).

## 5) Bai test can them
- Test mapping `ung` dung cho 3 cap (1-4, 2-5, 3-6), fail neu dong tinh am/duong.
- Test `decision_quality` khi gap token trai chieu (vd: "cat nhung huu hoi") phai ra `mixed`.
- Test parser tach Tuong/Chiêm tren 1 vai doan mau.

## 6) De xuat buoi tiep theo
- Doc tiep p.021-040, uu tien cac doan vao "Dich thuyet cuong linh" de rut rule co the code cho:
  - dynamic/static transitions
  - relation giua hao dong va xu huong hanh dong
  - nguyen tac nhin quẻ theo "thoi" (context timing)
