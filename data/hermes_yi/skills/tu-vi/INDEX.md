---
name: tu-vi-index
description: Master index Tử Vi Đẩu Số Toàn Thư (Trần Đoàn / Vũ Tài Lục). Map cung/intent → file citation cổ văn. Hermes load trước khi luận Tử Vi theo Toàn Thư.
metadata:
  hermes:
    tags: [tu_vi, Index, AlwaysAvailable]
    routing_mode: short
  source:
    book_corpus_id: "tu-vi-dau-so-toan-thu-vu-tai-luc"
    book_title: "Tử Vi Đẩu Số Toàn Thư"
    author: "Trần Đoàn (Hi Di), đời Tống"
    translator: "Vũ Tài Lục"
    journal_prefix: "docs/design/tu-vi-toan-thu-tran-doan-tham-nhuan-vong-*"
  curated_at: 2026-06-17
---

# Tử Vi Đẩu Số Toàn Thư — Master Index

Bảng định tuyến intent → citation cổ văn (gốc Trần Đoàn, bản dịch Vũ Tài Lục).
Tổ Tử Vi = **Trần Đoàn (Hi Di)** — KHÔNG phải Thiệu Khang Tiết (xem gia phả ở [[hoang_cuc_anchor_year_que]]).

## Trạng thái đọc sâu (vòng / trang)
- vòng 1–4: tr.1–80 (Book Profile, 14 chính tinh chư tinh, Nam Mệnh Ca, paradigm: 70/30, Mệnh-Thân Thể-Dụng, Nhân Cung, Cường-Nhược, Bát Pháp, Thập Dụ)
- **vòng 5: tr.81–100 ✅** — Thập Nhị Cung Luận (12 cung × chính tinh) + mở Vận Hạn → `thap-nhi-cung-toan-thu.md`
- *Tiếp theo (vòng 6): tr.100–120 — Vận Hạn (sao nhập Đại Vận / Tiểu Hạn).*

## Map cung → file (luận theo cung cụ thể)
| Cung user hỏi | Route |
|---|---|
| Sự nghiệp / Quan Lộc | `thap-nhi-cung-toan-thu.md` §1 |
| Tiền bạc / Tài Bạch | §2 |
| Vợ chồng / Phu Thê (Gieo Duyên) | §3 ★ |
| Phúc Đức / phúc phận | §4 (⚠ xung đột cổ-Việt: mộ phần) |
| Cha mẹ / Phụ Mẫu | §5 (Nhật=cha, Nguyệt=mẹ) |
| Bạn bè / đối tác / Nô Bộc | §6 (⚠ xung đột: lứa đôi) |
| Nhà đất / Điền Trạch | §7 (Hỏa/Linh+Vũ/Tham = ngoại lệ tốt) |
| Sức khỏe / Tật Ách | §8 (→ module Chiếu Đởm Kinh riêng) |
| Anh em / Huynh Đệ | §9 |
| Con cái / Tử Tức (Gia Đạo) | §10 ★ |

## Khoá đọc nhanh (áp mọi cung)
**Tứ Sát = Dương Đà · Linh Hỏa · Không Kiếp** đảo cát→hung ở mọi cung. Ngoại lệ: Hỏa/Linh + Vũ Khúc/Tham Lang ở Điền Trạch = cực tốt.

## Iron Rule khi luận (đa phái — #3)
3 điểm Toàn Thư (cổ) ≠ tiền nhân Việt → NÊU CẢ HAI, không hoà tan:
- Phúc Đức ↔ mộ phần ông cha (VN có, Trần Đoàn không)
- Nô Bộc ↔ cuộc sống lứa đôi (VN có, Toàn Thư không)
- Thê cung: Tả Hữu = lắm vợ (VN) vs Xương Khúc (Toàn Thư)

Engine liên quan: `engine/tu_vi/hop_hon.py` (Phu Thê/Quan Lộc/Tử Tức) · `engine/tu_vi/gia_dao.py` · `engine/tu_vi/duyen.py` — đã grounded vào citation §3/§10.
