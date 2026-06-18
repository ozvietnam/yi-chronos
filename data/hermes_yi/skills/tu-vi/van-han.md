---
name: tu-vi-van-han
description: Vận Hạn (Đại Vận / Tiểu Hạn) — "sao nhập hạn ca" + bác bỏ "năm xung" + Lưu Bá Ôn chốt vận quy về Mệnh-Thân. Toàn Thư tr.95–107.
metadata:
  hermes:
    tags: [tu_vi, van_han, dai_van, luu_nien, Reference, LongContext]
    routing_mode: long
    routing_keys: [van-han, dai-van, tieu-han, nam-nay-the-nao, nam-xung, nam-tuoi, sao-nhap-han]
  source:
    book_corpus_id: "tu-vi-dau-so-toan-thu-vu-tai-luc"
    author: "Trần Đoàn (Hi Di), dịch Vũ Tài Lục"
    pages_orig: "95-107"
    journal: "docs/design/tu-vi-toan-thu-tran-doan-tham-nhuan-vong-6-p101-120.md"
  curated_at: 2026-06-17
---

# Vận Hạn — Toàn Thư tr.95–107

## Khoá: "X nhập hạn ca"
Mỗi chính tinh + sát tinh có MỘT bài phú cho khi nó **cai quản Đại Vận / Tiểu Hạn**. Quy luật chung:
> **Đắc địa (miếu/vượng) → hạn tốt** (thăng quan, phát tài, hỉ sự).
> **Hãm địa + Tứ Sát (Hỏa Linh · Dương Đà · Không Kiếp) → hạn họa** (quan tai, khẩu thiệt, tang, phá tài, bệnh).
Cùng MỘT sao cho kết quả ngược nhau tùy miếu-hãm + sát → KHÔNG phán cứng theo tên sao.

Vài nét đặc trưng:
- **Cự Môn** đắc hạn → "mất chức để lên to hơn" (hung vi cát triệu); hãm + Tang Môn → kiện cáo, tang.
- **Tham Lang** miếu + Hỏa Tinh (người tuổi Thìn Tuất Sửu Mùi) → hoạnh phát phút chốc; hãm → nên tiết dục, chớ bài bạc.
- **Lộc Tồn** hạn → cũng là **hạn cưới/sinh con** (hôn nhân giá thú thiêm tự tục); kỵ Lộc-Mã giao trì gặp Không Kiếp + Thái Tuế xung → nguy.
- **Thiên Tướng/Thiên Lương** đắc → phúc thọ; gặp Kình Dương + Hỏa Linh → "nhất mệnh nhập hoàng tuyền" (hạn nặng).
- **Phá Quân** hạn → xét kỹ; hãm + sát → vợ con tổn thương, đàn bà khó đẻ/đại tang.
- **Tứ Hóa nhập hạn**: Lộc → tước vị cao; **Kỵ nhập miếu vẫn khá**, Kỵ + Thiên Không / hãm + Ác Sát → tài tán người lìa, thoái chức, tang.

## ⚠ Toàn Thư TỰ BÁC BỎ "năm xung năm tuổi" (tr.107)
Sách chép "Câu quyết về năm xung" (Tý Ngọ kỵ Dần Thân, tuổi Tị kỵ năm Tị…) RỒI phê thẳng:
> *"Đây chỉ là câu quyết của mấy người thuật sĩ giang hồ, KHÔNG có mấu cớ chắc chắn — vì nếu cứ tính miên man như vậy thì con người ta chẳng có năm nào tốt nữa."*
→ **Chốt sản phẩm**: KHÔNG bán "năm xung/năm tuổi" như định mệnh cứng. Đây là chính sách của chính Toàn Thư, trùng paradigm không-predict (Iron Rule #6).

## 🔑 Lưu Bá Ôn (Trích Thiên Tủy) — vận quy về CƠ (tr.108)
> *"Điều quan trọng vẫn là MỆNH và THÂN có vượng hay không."*
→ Vận Hạn (BIẾN) phải đặt TRÊN nền Mệnh-Thân gốc (CƠ). Cùng tinh thần "CƠ + BIẾN" của Phú Thái Vi. Luận hạn mà bỏ gốc Mệnh-Thân = sai phép.

## Liên hệ engine
`engine/bat_tu/dai_van.py` + `luu_nien.py` + `engine/hoang_cuc` (đào hoa vận / năm hợp cưới / năm đón con đã dùng sao hỉ theo năm). Khi luận "năm nay thế nào" → áp khoá nhập-hạn + nhắc "vận quy về Mệnh-Thân", KHÔNG dùng năm-xung cứng.
