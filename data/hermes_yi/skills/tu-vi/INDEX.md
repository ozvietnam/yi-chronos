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
- **vòng 5: tr.81–100 ✅** — Thập Nhị Cung Luận (12 cung) → `cung/`
- **vòng 6: tr.101–120 ✅** — Vận Hạn → `van-han.md`; Nữ Mệnh → `nu-menh.md`
- **vòng 7 (swarm e2e): tr.121–171 ✅** — Ngũ Hành → `ngu-hanh.md`; Hình dáng-Tính tình → `hinh-dang-tinh-tinh.md`; Cách cục + Mệnh 12 cung → `cach-cuc-menh-12-cung.md`; Thập Đẳng Luận + Mệnh VCD + phú đánh số → `cach-cuc-phu-danh-so.md`

## 🏁 QUYỂN HOÀN THÀNH (171/171 trang) — 2026-06-17
Đọc trọn Tử Vi Đẩu Số Toàn Thư. Skill Hermes: INDEX + 10 file `cung/` + van-han + nu-menh + ngu-hanh + hinh-dang-tinh-tinh + cach-cuc-menh-12-cung + cach-cuc-phu-danh-so.

## Map cung → file (tách chi tiết per-cung, routing mịn)
| Cung user hỏi | Route |
|---|---|
| Sự nghiệp / Quan Lộc | `cung/quan-loc.md` |
| Tiền bạc / Tài Bạch | `cung/tai-bach.md` |
| Vợ chồng / Phu Thê (Gieo Duyên) | `cung/phu-the.md` ★ |
| Phúc Đức / phúc phận | `cung/phuc-duc.md` (⚠ cổ-Việt: mộ phần) |
| Cha mẹ / Phụ Mẫu | `cung/phu-mau.md` (Nhật=cha, Nguyệt=mẹ) |
| Bạn bè / đối tác / Nô Bộc | `cung/no-boc.md` (⚠ cổ-Việt: lứa đôi) |
| Nhà đất / Điền Trạch | `cung/dien-trach.md` (Hỏa/Linh+Vũ/Tham ngoại lệ tốt) |
| Sức khỏe / Tật Ách | `cung/tat-ach.md` (→ Chiếu Đởm Kinh riêng) |
| Anh em / Huynh Đệ | `cung/huynh-de.md` |
| Con cái / Tử Tức (Gia Đạo) | `cung/tu-tuc.md` ★ |
| Vận hạn / "năm nay thế nào" / năm xung | `van-han.md` (⚠ KHÔNG bán năm-xung cứng) |
| Lá số nữ / phụ nữ | `nu-menh.md` (giữ nguyên nghĩa cổ + ghi chú thời đại) |
| Ngũ hành sao / sinh-khắc-chế-hóa / nạp âm | `ngu-hanh.md` (⚠ Vũ Tài Lục phê phái Việt — xem dưới) |
| Hình dáng / tướng mạo / tính tình | `hinh-dang-tinh-tinh.md` |
| Cách cục / Mệnh đóng cung địa chi | `cach-cuc-menh-12-cung.md` |
| Cách cục có tên / phú / Thập Đẳng Luận / Mệnh VCD | `cach-cuc-phu-danh-so.md` |

## Khoá đọc nhanh (áp mọi cung)
**Tứ Sát = Dương Đà · Linh Hỏa · Không Kiếp** đảo cát→hung ở mọi cung. Ngoại lệ: Hỏa/Linh + Vũ Khúc/Tham Lang ở Điền Trạch = cực tốt.

## Iron Rule khi luận (đa phái — #3)
3 điểm Toàn Thư (cổ) ≠ tiền nhân Việt → NÊU CẢ HAI, không hoà tan:
- Phúc Đức ↔ mộ phần ông cha (VN có, Trần Đoàn không)
- Nô Bộc ↔ cuộc sống lứa đôi (VN có, Toàn Thư không)
- Thê cung: Tả Hữu = lắm vợ (VN) vs Xương Khúc (Toàn Thư)

Engine liên quan: `engine/tu_vi/hop_hon.py` (Phu Thê/Quan Lộc/Tử Tức) · `engine/tu_vi/gia_dao.py` · `engine/tu_vi/duyen.py` — đã grounded vào citation §3/§10.
