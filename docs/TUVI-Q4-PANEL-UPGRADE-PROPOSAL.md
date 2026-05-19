# TuViLaSoPanel Upgrade Proposal — Lấy nền móng Thiệu Khang Tiết

**Date**: 2026-05-19
**Source**: Đọc sâu 20 trang đầu Tử Vi Đẩu Số Toàn Thư (紫微斗数全书) — Trần Đoàn (Hi Di tiên sinh)
**Engine snapshot**: `bac_phai_v1` ruleset · `engine/tu_vi/{an_sao, chinh_tinh, interpretation, luu_tru}.py`
**Panel snapshot**: `client/webapp/src/components/TuViLaSoPanel.vue` (800 lines)

---

## 1. Tinh thần nền móng

Sách của thầy Thiệu (qua Trần Đoàn → Phan Hy Doãn) **KHÔNG phải engine bói** — là **MÔN ĐỌC ĐỒNG DẠNG** giữa người với vũ trụ. Bốn quyển sách:

| Quyển | Nội dung chính | Hiện trạng trong engine |
|---|---|---|
| 1 | **Phú Thái Vi**, Phú Hình Tính, Luận Tinh Viên, Đẩu Số Cốt Tủy, các định nghĩa cách cục | ❌ Chỉ có 14 chính tinh tham chiếu, thiếu *Phú* gốc |
| 2 | An mệnh + 12 cung + các sao chính/phụ/sát/lưu | ✅ Engine an sao đầy đủ (Bắc Phái) |
| 3 | Diễn giải 12 cung × 14 chính tinh (huynh đệ → phụ mẫu) | ⚠️ Có `interpretation.py` nhưng đơn giản |
| 4 | 60+ lá số cổ kim (Khổng Tử, Lý Bạch, Bạch Khởi, Mã Viện...) | ❌ Chưa có database lá số mẫu |

→ **Panel hiện tại = engine an sao chính xác, NHƯNG thiếu chiều sâu Hán học của Tổ sư**.

---

## 2. 8 đề xuất nâng cấp (xếp theo priority)

### 🥇 #1 — Thêm "Mệnh chủ + Thân chủ" (đã có công thức trong sách)

**Trích Q4 mục lục p11:** *An Mệnh chủ · An Thân chủ*

- **Mệnh chủ**: sao chủ theo địa chi Mệnh cung
  - Tý → Tham Lang, Sửu/Hợi → Cự Môn, Dần/Tuất → Lộc Tồn, Mão/Dậu → Văn Khúc, Thìn/Thân → Liêm Trinh, Tỵ/Mùi → Vũ Khúc, Ngọ → Phá Quân
- **Thân chủ**: sao chủ theo địa chi năm sinh
  - Tý/Ngọ → Hỏa Tinh, Sửu/Mùi → Thiên Tướng, Dần/Thân → Thiên Lương, Mão/Dậu → Thiên Đồng, Thìn/Tuất → Văn Xương, Tỵ/Hợi → Thiên Cơ

**Engine cần thêm**: `an_sao.menh_chu(branch_idx) → star_name`, `than_chu(year_branch) → star_name`
**Panel hiển thị**: 2 cell phụ trong center 2×2 → "Mệnh chủ: ⭐ Tham Lang · Thân chủ: ⭐ Thiên Lương"

### 🥈 #2 — Đẩu Quân (斗君) — sao tháng sinh

**Trích Q4 mục lục p11:** *An Đẩu Quân quyết*

- Đẩu Quân = chỉ tháng sinh của đương sự, an theo Địa chi tháng + Địa chi giờ sinh
- Quan trọng để xem **tháng đi hạn** trong Đại Vận/Tiểu Hạn

**Engine cần thêm**: `an_sao.dau_quan(month, hour_idx) → branch_idx`
**Panel hiển thị**: marker nhỏ "斗 ĐẨU QUÂN" trên cung tương ứng (giống ★ MỆNH và 身 THÂN)

### 🥉 #3 — Phú Thái Vi block (quote tổ sư khi mở panel)

**Trích Q4 p16:**
> *"Đẩu số chí huyền chí vi, lý chỉ dị minh, tuy thiết vấn ư bách thiên chi trung, do hữu ngôn nhi vị tận"*
> — Phú Thái Vi, mở quyển 1 Tử Vi Đẩu Số Toàn Thư

**Panel UX**: trước khi an lá số, hiển thị 1 quote card với **lời tổ sư** + ngữ cảnh. Sau khi an xong, link nhỏ "📜 Phú Thái Vi" mở modal hiển thị toàn bộ phú.

**Implementation**: chỉ là JSON data file `data/tuvi/phu_thai_vi.json` + 1 Vue component `<PhuThaiViModal>`

### #4 — Hình Tính Phú tooltips trên chính tinh

**Trích Q4 mục lục p9:** *Phú Hình Tính (2)*

Mỗi chính tinh có miêu tả hình thể + tính cách trong Hình Tính Phú. Vd:
- **Tử Vi**: hình thể đoan chính, tính kiên định nhưng có chút cô độc
- **Thiên Phủ**: dung mạo hòa nhã, tính rộng rãi, có chất "chủ"
- **Vũ Khúc**: cương nghị, quả đoán, hợp võ nghiệp/tài chính

**Implementation**: hover trên tên sao trong cell → tooltip 2-3 dòng từ Hình Tính Phú. JSON map `chinh_tinh → hinh_tinh_description`.

### #5 — Cách cục detector (Phú Quý Bần Tiện)

**Trích Q4 mục lục p9-10:**
- *Định phú cách / quý cách / bần cách / tiện cách / tạp cách*
- *Định phú quý bần tiện 10 đẳng luận*
- *Luận chư tinh đắc địa hợp cách phú quý / luận chư tinh hãm địa bần tiện*

Hiện engine có `interpretation.py` nhưng KHÔNG có pattern detection (cách cục).

**Đề xuất**: tạo `engine/tu_vi/cach_cuc.py` — phát hiện ~15 cách kinh điển:
- **Cát cách**: Quân Thần Khánh Hội · Tử Phủ Đồng Cung · Tam Hợp Bích Mệnh · Khôi Việt Phù Trì · Lộc Mã Giao Trì · Tả Hữu Đồng Cung...
- **Hung cách**: Dương Đà Điệp Tịnh · Thất Sát Trùng Phùng · Mã Đầu Đới Kiếm · Đại Hao Đồng Cung...

**Panel hiển thị**: section "Cách cục phát hiện" hiện danh sách cách cục với badge cát/hung + trích Phú giải thích.

### #6 — Mệnh Kim Tỏa Thiết Xà Quan + Đồng Hạn (cho trẻ em)

**Trích Q4 mục lục p11:** *An Mệnh Kim Tỏa Thiết Xà Quan · An Đồng hạn*

Đây là phần kinh điển cho **luận mệnh trẻ em**:
- "Khóa vàng - rắn sắt" = quan ải đặc biệt mà tuổi nhỏ phải vượt
- **Đồng Hạn** = vận của thời thơ ấu (trước khi vào Đại Hạn đầu)

**Engine**: thêm `cach_cuc.kim_toa_thiet_xa(la_so)`, `luu_tru.dong_han(age)`
**Panel**: hiển thị khi nhập sinh thần < 18 tuổi → cảnh báo "Mệnh đang qua Khóa Vàng Rắn Sắt — cẩn thận giai đoạn ..."

### #7 — Database 60+ lá số cổ kim (Quyển 4)

**Trích Q4 mục lục p13-15:**
> Khổng Tử (Khổng Trọng Ni) · Lý Thái Bạch · Ngô Bỉnh Trực · Bạch Khởi · Mã Viện · Triệu Phổ · Hoàng Vũ An · Bạch Cư Dị · Tư Mã Bật · Vũ An Vương · Nghiêm Giới Khê · …

→ **60+ lá số mẫu của nhân vật lịch sử** (vua, tướng, văn nhân, hòa thượng, đạo nhân, người nghèo).

**Đề xuất**: tạo `data/tuvi/mau_la_so/{nhanvat}.json` mỗi nhân vật 1 file. Khi đương sự cast xong:
- Engine so sánh lá số với 60 mẫu (similarity by: chính tinh ở Mệnh + Thân + Tài Bạch + Quan Lộc)
- Top 3 matches: "Lá số của Anh GIỐNG VỚI: 1. Bạch Cư Dị (thi nhân), 2. Tư Mã Bật (võ quan), 3. ..."

**Panel hiển thị**: section "Lá số tương đồng cổ kim" — hover → modal chi tiết lá số của nhân vật + chú giải Phú.

### #8 — Phân phái Bắc/Nam toggle

**Trích Q4 p7:**
> *"Tử Vi thực chia làm hai phái Nam và Bắc... Nam phái Tử Vi chú trọng vào Đẩu số thực dụng. Cách suy đoán của Nam phái Tử Vi là: trước tiên định Tử Vi, tức lấy Nạp âm của Mệnh cung để định cung tọa của Tử Vi..."*

Hiện engine `bac_phai_v1` cố định. Đề xuất **toggle Bắc/Nam phái**:
- Bắc Phái (default): theo Trần Đoàn — Tử Vi đặt dựa trên Cục số
- Nam Phái: theo Trương Diệu Văn — Tử Vi đặt dựa trên Nạp Âm Mệnh cung

**Engine**: thêm `school: 'bac' | 'nam'` parameter. Khác nhau ở `an_tu_vi_position()`.
**Panel UI**: nút radio "🏔️ Bắc Phái (Tổ sư Trần Đoàn) | 🌊 Nam Phái (Trương Diệu Văn)" — mặc định Bắc.

---

## 3. Roadmap đề xuất

### Phase 1 — Ngắn (1-2 phiên)
- ✅ Wiki: 20 concepts Tử Vi từ Q4 đã add
- 🔲 **#1 Mệnh chủ + Thân chủ** (đơn giản: 14 dòng lookup table + 1 cell trong center)
- 🔲 **#2 Đẩu Quân** (công thức rõ ràng trong Q4 p11)
- 🔲 **#3 Phú Thái Vi quote** (data-only, 1 modal component)

### Phase 2 — Trung bình (3-5 phiên)
- 🔲 **#4 Hình Tính Phú tooltips** (14 entries, cần đọc Phú Hình Tính ở Q4 p16+ — chưa dịch hết)
- 🔲 **#5 Cách cục detector** (~15 cách, cần luật rõ — đọc Q4 p9-10 + p16-30)
- 🔲 **#8 Bắc/Nam phái toggle** (engine refactor nhỏ)

### Phase 3 — Dài (cần đọc thêm Q4 đến hết quyển 4)
- 🔲 **#6 Đồng Hạn + Kim Tỏa Thiết Xà** (cần đọc luận trẻ em)
- 🔲 **#7 60+ lá số cổ kim** (cần dịch + extract Quyển 4)

---

## 4. Hồ sơ pháp lý

Mọi đề xuất CITED về **Tử Vi Đẩu Số Toàn Thư** (sách của thầy Thiệu, qua Trần Đoàn). KHÔNG bịa thêm cách cục, KHÔNG mix với phái khác trừ khi đặc biệt declared.

Mỗi feature mới sẽ có **citation footnote** dạng: *"Theo TVDSTT Q.1 - Phú Thái Vi, dòng ..."* để truy ngược về nguồn gốc.

---

## 5. Sẵn sàng triển khai

Anh chọn:
- **A**: Em làm Phase 1 ngay (Mệnh/Thân Chủ + Đẩu Quân + Phú Thái Vi quote) — 1-2 giờ
- **B**: Đọc tiếp Q4 p21-50 trước (Phú Hình Tính + đầu cách cục) → mới có data đầy đủ cho Phase 2
- **C**: Anh xem PDF v0.3 + wiki + proposal này trước, em đợi quyết định
