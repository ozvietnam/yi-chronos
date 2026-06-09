# 📿 Hệ phái 02 — BÁT TỰ / TỬ BÌNH

> Khoa học luận mệnh qua **Tứ Trụ** (4 trụ Năm-Tháng-Ngày-Giờ × Can+Chi = 8 chữ).
> Khởi nguồn: **Từ Tử Bình** đời Tống (mệnh lý cải tiến từ Lý Hư Trung đời Đường).
> 9 cuốn · ~27.8 MB.

## 📚 Danh sách

### 🥇 du-doan-tu-tru-thieu-vy-hoa (Thiệu Vĩ Hoa)
- **Master Thiệu Vĩ Hoa** — Bát Tự đương đại TQ
- **Status**: ✅ partial thâm nhuần — Iron Rule master chọn 2026-05-27
- **Wire vào**: `engine/bat_tu/*` (cách cục + dụng thần + dự đoán)
- **Wiki**: +70 concepts school=tu_binh_ba_tu
- **Journal**: `docs/design/bat-tu-thieu-vi-hoa-tham-nhuan.md`

### trich-thien-tuy-binh-chu-nham-thiet-tieu (Trích Thiên Tủy — Nhâm Thiết Tiều bình chú)
- **Trích Thiên Tủy** = kinh điển bát tự cốt cổ điển
- Bản bình chú của Nhâm Thiết Tiều (cuối Thanh) — chuẩn nhất

### thien-nhan-hoc-co-dai-trich-thien-tuy
- Trích Thiên Tủy bản gốc (chưa bình chú)
- Đối chiếu cùng cuốn trên

### tu-thu-binh-giai
- Tử Thư Bình Giải — sách cổ điển

### bat-tu-ha-lac-va-quy-dao-doi-nguoi
- Bridge Bát Tự ↔ Hà Lạc Dịch (cross-disciplinary)
- VN modern

### nguyen-ly-chon-ngay-theo-bat-tu-ha-lac
- Ứng dụng: trạch cát qua Bát Tự + Hà Lạc

### can-chi-thong-luan
- Cơ sở: lý thuyết Can Chi sâu

### du-bao-theo-tu-binh
- Hiện đại — dự báo + cách cục

### tu-xem-van-menh-theo-tu-tru
- Tự học hiện đại

## 🔑 Nhật chủ + 10 sao Thập Thần

Bát Tự xoay quanh:
- **Nhật chủ** (thiên can ngày sinh) — định danh mệnh tạo
- **10 sao Thập Thần** (Tỷ-Kiếp / Thực-Thương / Tài (Chính+Thiên) / Quan-Sát / Ấn (Chính+Thiên))
- **Vòng Trường Sinh 12** — pha sống chết của nhật chủ trong mỗi chi
- **Đại Vận / Lưu Niên / Lưu Nguyệt** — đo dòng thời gian

## 👨‍👩‍👧‍👦 Tra cứu nhân thân theo Thập Thần

| Sao | Nam mệnh | Nữ mệnh |
|---|---|---|
| Tỷ-Kiếp | huynh đệ | huynh đệ |
| Thực-Thương | con / cấp dưới | **CON CÁI** (Thực=trai, Thương=gái) |
| Chính Tài | **VỢ** chính / tài | tài |
| Thiên Tài | cha / vợ nhỏ | cha |
| Chính Quan | quyền / cấp trên | **CHỒNG** |
| Thất Sát | **CON TRAI** / kẻ địch | quyền/đối thủ |
| Chính Ấn | mẹ ruột | mẹ ruột |
| Thiên Ấn | mẹ kế / quý nhân | mẹ kế |

## 🔗 Wiki + Engine

- Engine: `engine/bat_tu/cast.py` (cast tứ trụ qua `sxtwl`), `thap_than.py`, `cach_dung_than_ttt.py`, `compatibility.py`...
- Wiki: corpus `bat-tu-zh-q1` trong `data/yi_wiki/wiki.sqlite3`
- Sage soul: `data/hermes_yi/profiles/bat-tu-sage/SOUL.md`

## ⚠ Iron Rule (đã established)

**Hierarchy nguồn**:
1. Cổ văn Trung Quốc (Trích Thiên Tủy, Tử Thư Bình Giải, Uyên Hải Tử Bình)
2. Bình chú hiện đại (Thiệu Vĩ Hoa, Nhâm Thiết Tiều)
3. Biên dịch VN
4. Diễn giải hiện đại

Conflict → ưu tiên cổ văn + flag founder review.
