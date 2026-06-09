# 🌌 Hệ phái 01 — TỬ VI ĐẨU SỐ

> Khoa học luận đoán nhân mệnh qua 14 chính tinh + 12 cung địa chi + Tứ Hóa.
> Khởi nguồn: **Trần Đoàn (Hi Di tiên sinh)** — đời Tống.
> 6 cuốn · ~18.5 MB.

## 📚 Danh sách

### 🥇 trung-chau-tu-vi-dau-so-2 (Vương Đình Chỉ — Bắc phái Trung Châu)
- **900 trang** — sách cốt engine YI-Chronos
- **Status**: ✅ thâm nhuần 100% (32 vòng đọc, 2026-06-08)
- **Wire vào**: `engine/tu_vi/chiem_phu_the_v3.py` (34 rules), `chiem_phu_the_v4.py` (13 rules cross-bind), `phu_the_partner_traits.py` (60+ paradigm), `trung_chau_paradigm.py` (LLM context)
- **3 Iron Rule cốt**: DI CUNG HOÁN VỊ + XU CÁT TỊ HUNG + HƯ TÂM LÃNH HỘI
- **Journal**: `docs/design/trung-chau-q2-vong-*.md` (32 file)

### tu-vi-dau-so-toan-thu-vu-tai-luc (Vũ Tài Lục)
- Phiên bản Toàn Thư VN cổ điển
- Bridge giữa Trần Đoàn nguyên bản và phái VN

### tu-vi-nghiem-ly-toan-thu-thien-luong (Thiên Lương)
- "Nghiệm lý" — case study + minh chứng thực tế
- VN modern (~thế kỷ 20)

### tu-vi-ham-so
- "Hàm số" — luận theo công thức + thuộc tính sao
- VN

### sach-tu-vi-vo-long (Võ Long)
- VN — thực hành / dễ tiếp cận

### lap-va-giai-tu-vi
- Tutorial — lập + giải lá số bước cơ bản
- Phù hợp người mới

## 🎯 Phân biệt phái

| Phái | Đặc điểm | Tài liệu chính |
|---|---|---|
| **Bắc phái Trung Châu** | DI CUNG HOÁN VỊ, 3-tier reading, paradigm "đọc đồng dạng" | trung-chau-q2 |
| **Tam Hợp phái VN** | Tam phương tứ chính + cách cục cổ điển | tu-vi-dau-so-toan-thu-vu-tai-luc |
| **Phái Thiên Lương** | Nghiệm lý case study VN | tu-vi-nghiem-ly-toan-thu-thien-luong |

## 🔗 Wiki + journals

- Wiki: `data/yi_wiki/wiki.sqlite3` (corpus tuvidauso-zh-q1, 320 concepts + 545 cách cục)
- Sage soul: `data/hermes_yi/profiles/tu-vi-sage/SOUL.md`
- Journals: `docs/design/trung-chau-q2-vong-*.md` (32 vòng), `docs/design/tu-vi-tham-nhuan-quyen-1.md`

## ⚠ Iron Rule #6 (project-wide)

**Tử Vi = ĐỌC ĐỒNG DẠNG, không phải predict tool.**
> _"Đẩu số chí huyền chí vi, lý chỉ dị minh."_ — Trần Đoàn
> _"Cẩu hoặc bất sát kỳ cơ, cánh vong kỳ biến, tắc số chi tạo hóa viễn hĩ."_

Không output kiểu "Anh sẽ giàu/nghèo" — phải dùng "khoảnh khắc này phản chiếu cấu trúc gì".
