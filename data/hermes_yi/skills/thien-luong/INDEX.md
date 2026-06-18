---
name: thien-luong-index
description: Master index Tử Vi Nghiệm Lý Toàn Thư (Cụ Thiên Lương — phái VN cải cách 1972). Map intent → file citation. Hermes load trước khi luận theo phái Thiên Lương.
metadata:
  hermes:
    tags: [tu_vi, thien_luong, Index, AlwaysAvailable]
    routing_mode: short
  source:
    book_corpus_id: "tu-vi-nghiem-ly-toan-thu-thien-luong"
    book_title: "Tử Vi Nghiệm Lý Toàn Thư"
    author: "Lê Quang Khải (Cụ Thiên Lương, 1910–1985)"
    school: "thien_luong"
    journal_prefix: "docs/design/tu-vi-nghiem-ly-thien-luong-tham-nhuan-*"
  curated_at: 2026-06-17
---

# Tử Vi Nghiệm Lý Toàn Thư (Thiên Lương) — Master Index

Phái VN cải cách 1972 — **Tử Vi = ĐẠO ĐỨC HỌC + TÂM LÝ HỌC, không huyền bí, đừng dùng kiếm tiền.**
Khớp Iron Rule #6/#8 mạnh nhất cả hệ. Để CẠNH Trần Đoàn/Trung Châu (kept_all, đa phái — KHÔNG hoà tan, KHÔNG phán phái nào sai).

## 🧭 PARADIGM CỐT (khác hẳn Trần Đoàn/Trung Châu)
- **Đọc TUỔI trước SAO**: "sao chỉ là lớp áo phủ pho tượng". Khung dựng số = **3 VÒNG (Tam Tài)**:
  - **Lộc Tồn** (Thiên/Can) — phúc-tài, "hoàng lương một kiếp"
  - **Thái Tuế** (Địa/Chi) — **tư cách / chánh danh — CHỦ ĐẠO, đọc trước chính tinh**
  - **Tràng Sinh** (Nhân/Cục/nạp âm) — cách xử thế đường dài
- **BA ĐIỂM QUAN HỆ NHẤT**: Mệnh · Thái Tuế · Lộc Tồn. Trục trặc 1/3 → rẽ đường "Quan Phúc Tứ Đức (từ thiện)" = biến cách xấu thành LỜI KHUYÊN ĐẠO ĐỨC.
- **Đức năng thắng số**: Mệnh = dự thảo · Thân = sửa chữa · "Chữ Tâm bằng ba chữ Tài" → mệnh là ĐỘNG TỪ.
- **5 bậc tuổi Can-Chi** (Can sinh Chi=phúc lớn … Chi khắc Can=nghịch cảnh) — đọc đầu tiên.

## Map intent → file (vòng 7 swarm e2e, p12-186)
| Intent | Route |
|---|---|
| Lộc / Quốc Ấn Đường Phù / Thiên La Địa Võng / Lục Sát / "đức năng thắng số" | `sao-loc-sat.md` |
| Cấu trúc lá số · 3 điểm quan hệ · Tuần Triệt · nhị/tam hợp xung chiếu | `cau-truc-la-so.md` |
| Vòng Tràng Sinh · Ngũ Hành → Ngũ Thường (đức tính) · vận hội · Tam Tài | `trang-sinh-ngu-hanh-duc-tinh.md` |
| **Vòng Thái Tuế chủ đạo** · Can-Chi · Cục · âm-dương thuận nghịch | `thai-tue-can-chi-cuc.md` ★ |
| Tứ Hóa (10 Can) · Tam Hóa Liên Châu · nghiệm lý · Tử Vi Thời Lý Học (chu kỳ) | `tu-hoa-nghiem-ly-chu-ky.md` |

## 🏁 QUYỂN HOÀN THÀNH (186/186 trang) — 2026-06-17
Vòng 1 (p2-11, tông chỉ + 5 paradigm key) + vòng 7 swarm e2e (p12-186, 5 cụm).

## ⚠ Lưu ý kỹ thuật cho engine (kept_all, KHÔNG ghi đè mặc định)
Phái Thiên Lương an **Tràng Sinh Thổ Ngũ Cục khởi ở NGỌ** (Hỏa sinh Thổ) — có thể khác `engine/tu_vi/an_sao.py` (Thổ cục khởi Thân theo Thủy). Nếu wire phái này → thêm option `school=thien_luong`, giữ kept_all. Các method cải cách đáng wire: 5 bậc tuổi · vòng Thái Tuế chủ đạo · Nhị Hợp(chỉ sinh)/Xung Chiếu(chỉ khắc) nhập-xuất · Ngũ Hành→Ngũ Thường.
