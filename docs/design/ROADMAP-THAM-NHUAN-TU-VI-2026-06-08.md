# Roadmap thâm nhuần Tử Vi — Luận giải sâu

> Tạo 2026-06-08 sau khi engine an_sao đã KHỚP HOÀN TOÀN với anlasotuvi.com
> (12 chính tinh + Tứ Hóa + Lục Cát + Lục Sát + Tuế Tiền + Bác Sĩ vòng +
> Tướng Tinh vòng + Triệt-Tuần + sao lẻ).
>
> **Vấn đề tiếp theo**: engine đã có đủ DATA, nhưng LUẬN GIẢI SÂU vẫn còn
> bề mặt. Cần thâm nhuần sách kinh điển để engine output đạt độ sâu của
> chuyên gia 30 năm chiêm tinh.

## 📚 Thư viện Tử Vi đã OCR (6 sách, ~2 triệu ký tự)

| # | Sách | Tác giả | Trang | Chars | Phái | Status |
|---|---|---|---:|---:|---|---|
| 1 | **Trung Châu Tử Vi Đẩu Số 2** | Vương Đình Chỉ | 900 | 2.36M | TQ Bắc phái | Đã đọc §5.3 (Phu Thê) — còn 95% |
| 2 | **Tử Vi Đẩu Số Toàn Thư** | Trần Đoàn (cổ TQ) — Vũ Tài Lục dịch | 171 | 496K | TQ kinh điển → VN | Q2 đã thâm nhuần (an sao) |
| 3 | **Tử Vi Hàm Số** | Hàm Số phái | 238 | 602K | TQ Hàm Số | CHƯA đọc |
| 4 | **Tử Vi Nghiệm Lý** | Thiên Lương | 186 | 562K | VN nghiệm thực | CHƯA đọc |
| 5 | **Tử Vi Võ Long** | Võ Long | ~120 | 150K | VN | CHƯA đọc |
| 6 | **Lập và Giải Tử Vi** | (VN cơ bản) | ~80 | 203K | VN nhập môn | CHƯA đọc |

---

## 🎯 Mục tiêu cuối cùng

Engine + UI luận giải cung Phu Thê (và 11 cung khác) đạt **chiều sâu chuyên
gia 30 năm** — kết hợp:

1. **Sách gốc TQ** (chuẩn paradigm, không trại tự diễn giải VN)
2. **Sách VN nghiệm thực** (case study người Việt, văn hoá hôn nhân VN)
3. **Đa phái cross-reference** (Bắc phái Trung Châu + Hàm Số + Nghiệm Lý
   + Phú Thái Vi)
4. **Engine match** từng paradigm với sao thật trong lá số (đã có Q14-Q18
   cho Phúc Đức)

---

## 📅 Roadmap 4 giai đoạn (~6 tuần)

### Giai đoạn 1: Foundation — Đọc sâu sách kinh điển TQ (2 tuần)

**Mục tiêu**: nắm chắc paradigm gốc trước khi đối chiếu phái khác.

#### Tuần 1: Trung Châu Q2 (Vương Đình Chỉ) — phần CƠ
- **Tài liệu**: `data/restored_books/trung-chau-tu-vi-dau-so-2/content.md`
- **Tập trung**: §1 An Sao chi tiết · §2 14 Chính Tinh đặc tính ·
  §3 Tứ Hóa biến động · §4 Lục Cát Lục Sát hội chiếu
- **Cách đọc**: Iron Rule `doc-sau-20-trang` — 20 trang/lần, đúc kết +
  5-7 vòng hỏi anh, tiếp.
- **Output**: `docs/design/trung-chau-q2-tham-nhuan-co.md`
- **Wire vào engine**: extract paradigm 14 chính tinh + tổ hợp đôi mở rộng
  ngoài seed Phu Thê hiện có.

#### Tuần 2: Trung Châu Q2 — phần 12 CUNG
- **Tập trung**: §5 Luận 12 cung (Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch,
  Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê (đã đọc),
  Huynh Đệ)
- **Output**: `docs/design/trung-chau-q2-tham-nhuan-12-cung.md`
- **Wire vào engine**: build `chiem_<cung_name>_bac_phai.py` cho 11 cung
  còn lại theo pattern Phu Thê.

### Giai đoạn 2: TVDSTT (Phú Thái Vi) — gốc TQ (1 tuần)

**Mục tiêu**: nắm Phú Thái Vi — 545 cách cục kinh điển — để build engine
match cách cục mạnh hơn.

- **Tài liệu**: `data/restored_books/tu-vi-dau-so-toan-thu-vu-tai-luc/content.md`
- **Đã có**: 545 cách cục dict `data/yi_publishing/q1_tuvi/master/cach_cuc_index.json`
- **Cần làm**: validate dict + extract paradigm phù mệnh cho từng cách
- **Output**: `docs/design/tvdstt-tham-nhuan-cach-cuc.md`
- **Wire**: nâng cấp `engine/tu_vi/cach_cuc_dict.py` với citation page +
  Vietnamese paraphrase mỗi cách.

### Giai đoạn 3: Đa phái VN nghiệm thực (2 tuần)

**Mục tiêu**: cross-reference với phái VN để bổ sung văn hoá hôn nhân
+ nghiệm lý người Việt (paradigm cổ TQ → diễn giải VN hiện đại).

#### Tuần 4: Tử Vi Nghiệm Lý (Thiên Lương)
- **Tác giả**: Thiên Lương (1907-1998) — học giả Tử Vi VN nghiệm lý sâu sắc
- **Tài liệu**: `data/restored_books/tu-vi-nghiem-ly-toan-thu-thien-luong/content.md`
- **Tập trung**: case study thực tế, paradigm "mỗ" pattern (đã có engine),
  điểm khác biệt giữa Bắc phái TQ và phái VN
- **Output**: `docs/design/thien-luong-nghiem-ly-tham-nhuan.md`
- **Wire**: bổ sung `engine/tu_vi/case_studies.json` với case Việt.

#### Tuần 5: Tử Vi Hàm Số (TQ)
- **Tài liệu**: `data/restored_books/tu-vi-ham-so/content.md`
- **Tập trung**: Hàm Số phái — paradigm gắn với số học, dự báo định lượng
- **Output**: `docs/design/tu-vi-ham-so-tham-nhuan.md`
- **Wire**: nếu có công thức định lượng → wire vào engine.

### Giai đoạn 4: Sách bổ trợ + tổng hợp (1 tuần)

#### Tử Vi Võ Long + Lập và Giải Tử Vi
- **Mục tiêu**: skim để bắt insight quan trọng, KHÔNG đọc sâu (nhập môn)
- **Output**: `docs/design/vo-long-lap-giai-quick-notes.md`

#### Tổng hợp cross-bind 5 phái
- **Output**: `docs/design/TU-VI-DA-PHAI-SO-SANH.md`
- **Wire**: Iron Rule #3 multi-school respect — mỗi phái 1 sage profile,
  cross-bind paradigm, KHÔNG ép 1 phái duy nhất.

---

## 🔧 Discipline mỗi tuần

### Mỗi sách / mỗi 20 trang:
1. Em invoke skill `doc-sau-20-trang` BẮT BUỘC (Global Iron Rule)
2. Em đọc → tóm tắt → flag những đoạn **paradigm chưa có trong engine**
3. Anh hỏi em 5-7 vòng — anh đặt nghi vấn, em phải giải đúng
4. Anh duyệt → em mở rộng engine (thêm Qxx vào `chiem_<cung>_v3` hoặc
   `chiem_phu_the_v4`)
5. Test với lá số anh + 2 lá số sample → verify paradigm match thật
6. Commit + deploy
7. Update file này với progress

### Tools chạy nền (Iron Rule #2 Token Appetite — DƯ DẢ):
- Em dùng **agent sub-agent** chạy nền extract concepts từng sách (token Max đã trả, free)
- KHÔNG dùng cursor-agent (CEO incident 2026-06-05)
- Multi-agent cho việc đọc song song (vd: Trung Châu Q2 §1 + §2 cùng lúc)

---

## 📊 Output cuối cùng (sau 6 tuần)

| Output | Vị trí | Mục đích |
|---|---|---|
| 6 journal thâm nhuần | `docs/design/*-tham-nhuan*.md` | Lưu insight + Anh trace ngược |
| Engine `chiem_*_bac_phai.py` × 12 cung | `engine/tu_vi/` | Render thật cho 11 cung còn lại |
| `cach_cuc_dict.py` mở rộng | `engine/tu_vi/` | 545 cách cục + page citation |
| `case_studies.json` mở rộng | `data/yi_lexicon/` | +20 case Việt từ Thiên Lương |
| 5 sage profile (1/phái) | `data/hermes_yi/profiles/` | Đa phái respect |
| UI panel 11 cung mới | `client/webapp/src/components/` | Như CungPhuTheBacPhaiPanel |

---

## 🚦 Tuần này: bắt đầu Giai đoạn 1 — Trung Châu Q2 phần CƠ

Anh duyệt → em invoke `doc-sau-20-trang` đọc 20 trang đầu **§1 An Sao
chi tiết** Trung Châu Q2 → đúc kết → hỏi anh 5-7 vòng → tiếp.

Hoặc anh muốn em đọc cuốn khác trước? (em nghĩ Trung Châu Q2 là gốc cốt
vì engine em đã dùng paradigm của Vương Đình Chỉ.)
