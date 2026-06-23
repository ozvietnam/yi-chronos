---
name: tu-vi-dang-son-khoa-hoc-hoa
description: Phái KHOA-HỌC-HÓA Tử Vi của Đằng Sơn (《Tử Vi Hoàn Toàn Khoa Học》 T1+T2, kế thừa Tạ Phồn Trị). Suy mọi sao/cách từ ÂM DƯƠNG; ngũ hành = phép tính gần đúng; thần sát = tài Thiên-Địa. Đọc đồng dạng, mệnh-là-động-từ — KHÔNG predict. Kết tinh 40 vòng đọc sâu.
metadata:
  hermes:
    tags: [tu_vi, dang_son, khoa_hoc_hoa, than_sat, tuan_triet, Reference, LongContext]
    routing_mode: long
    routing_keys: [dang-son, khoa-hoc-hoa, vi-sao-co-sao-nay, suy-tu-am-duong, than-sat, loc-ton, kinh-da, khoi-viet, hoa-linh, vong-thai-tue, dao-ma-cai-sat, co-than-qua-tu, tuan-triet, vong-truong-sinh, tuyet-xu-phung-sinh, ma-quan-la-ban-dao, menh-tai-tuyet, tu-mo-tu-duong]
  source:
    book_corpus_id: "tuvi-dang-son"
    book_title: "Tử Vi Hoàn Toàn Khoa Học (Tập 1 + Tập 2)"
    author: "Đằng Sơn (Cao Hùng, Đài Loan; kế thừa Tạ Phồn Trị)"
    journal_prefix: "docs/design/tu-vi-dang-son-FULL-vong-* + tu-vi-dang-son-T2-vong-*"
    wiki_corpus: "tuvi-dang-son (270 concepts, school=tu_vi_dang_son)"
    verify_module: "engine/tu_vi/dang_son_verify.py (9 định lý, 21 test)"
  curated_at: 2026-06-23
---

# Tử Vi phái KHOA-HỌC-HÓA — Đằng Sơn

Đằng Sơn dựng Tử Vi như **chuỗi ĐỊNH LÝ suy từ âm dương**, không phải bảng tra thuộc lòng.
Tổ Tử Vi vẫn là Trần Đoàn; đây là **lăng kính khoa-học-hóa** (kế thừa Tạ Phồn Trị) — present
song song, KHÔNG thay Toàn Thư (Iron Rule #3 đa phái).

## Paradigm gốc (3 trụ)
1. **Tử Vi suy diễn được từ ÂM DƯƠNG** (first principles) — mọi sao/cách có cái LÝ, hỏi "vì sao có sao này".
2. **Ngũ hành = phép tính GẦN ĐÚNG của âm dương** (ngũ giác ≈ vòng tròn) → đắc-hãm bằng ngũ hành vốn bất-khả-khít; đừng luận sinh-khắc cứng.
3. **Thần sát = tài Thiên-Địa** (an theo CAN/CHI năm) — KHÔNG thể bỏ (khác phái "giản lược" Đài Loan chỉ giữ 14 chính + Tứ Hóa). Tài Nhân = tháng/ngày/giờ; tài Thiên-Địa = năm.

## Định lý cốt (đã kiểm bằng máy — `dang_son_verify.py`)
- **Lộc Tồn** = kết hợp Tứ Hóa (đúng-lúc/đúng-chỗ/thu-tàng, hành Thổ trung ương) → KHÔNG bao giờ ở tứ mộ. Phản đề: **Kình** (Lộc+1, "quá sớm") · **Đà** (Lộc−1, "quá trễ") · **Quan Phúc** (sai-chỗ) · **Song Hao** (phóng-túng, thẳng góc).
- **Khôi Việt** (Thiên Ất quý nhân) = quân-bình "toàn không": cứu chính tinh cực-hãm-hóa-Kỵ tại cung tương ứng. Engine theo phái TRUYỀN THỐNG (Giáp Mậu Canh→Sửu Mùi).
- **Hỏa Linh** = thủy-hỏa giao thoa (Tạ Phồn Trị). ⚠ Iron #3: engine theo bài thiệu truyền thống (Tỵ Dậu Sửu → Hỏa Mão), KHÁC Đằng Sơn/Tạ Phồn Trị (đảo → Hỏa Tuất). Present cho user chọn phái.
- **Vòng Thái Tuế** = 12 sao từ chu kỳ biểu kiến 5 hành tinh (Kim8/Thủy20/Hỏa32/Mộc12/Thổ30 năm). Thái Tuế ≠ Mộc tinh (chiều ngược + tuế sai).
- **Đào-Mã-Cái-Sát** = vòng Trường Sinh chi-năm ("đồng sinh cộng tử"): Đào=Mộc Dục · Mã=Bệnh · Cái=Mộ · Sát=Tuyệt.
- **Cô Thần / Quả Tú** = cô độc — ⚠ Đằng Sơn BÁC cách giải ngũ-hành Tử Bình ("không cha/vợ"); với bậc chân tu **Cô Quả = ĐẠO HẠNH** (tr.198).
- **Tuần Triệt** = 2 loại ảnh-hưởng-trấn-CUNG (không tam phương): **Tuần = căn-ngăn** (giảm 50% mọi sao, cả đời) · **Triệt = cắt-đứt** (giảm 80-90%, 30 năm đầu). Thái Tuế ∉ Tuần. **Mão Dậu nhị không = trục TU HÀNH**.
- **Vòng Trường Sinh** (cục) = nạp-hành: **Thổ đi CÙNG Thủy** (TS Thân); chiều dương-nam-âm-nữ thuận. (engine: `an_vong_truong_sinh`)
- **Mệnh chủ / Thân chủ** (Trần Đoàn): theo chi Mệnh / chi năm. (Tỵ→Vũ Khúc; năm Tý→Linh Tinh, đã sửa bug.)

## Cách ĐỌC (paradigm — bắt buộc khi luận theo Đằng Sơn)
- **Đọc đồng dạng, KHÔNG predict** (Iron #4/#6): mọi tầng là TÍNH / cấu-trúc / cơ-hội (disposition), không sấm kết cục. _"người tu thành tựu hay không còn lệ thuộc nhiều yếu tố khác."_
- **Mệnh là động từ** (Iron #8): "cấu trúc này vận hành tốt nhất khi...", không "số anh là...".
- **Ma quân là bạn đạo** (tr.241): sát tinh (Không Kiếp / Kình Đà Hỏa Linh) với bậc tu = nhiên-liệu thăng-tiến; nghịch-cảnh chuyển thành đạo.
- **Tuyệt-xứ-phùng-sinh** (tr.267): "cùng tắc biến, tướng chết tìm sinh lộ" — Mệnh tại Tuyệt KHÔNG = diệt vong mà = điểm bật-sinh (nếu được cứu gỡ).

## Đại tổng hợp một lá số
Khi user xin "tổng hợp / chân dung lá số" theo lăng kính này → engine `dai_tong_hop` trả structured
(THỂ Mệnh-chủ / DỤNG chính-tinh-Mệnh / hậu-thiên Thân-chủ + cụm cửa-tu + tứ-mộ tu-dưỡng + Tuần/Triệt
+ cân-bằng sáng/xấu-nhẹ) + SVG poster. LUÔN kèm disclaimer đọc-TÍNH-không-predict.
