# Engine Gaps — Sau Thâm Nhuần Q2

**Ngày**: 2026-05-19
**Nguồn**: Thâm nhuần Q2 Tử Vi Đẩu Số Toàn Thư (62 trang, p0080-p0141)
**Phát hiện**: 208 cách cục mới + 125 concepts mới → **một số sao engine `an_sao.py` chưa có**

---

## I. Engine current state (audit)

### ✅ Đã có trong `engine/tu_vi/an_sao.py`

| Function | Tương ứng Q2 |
|---|---|
| `cung_menh_index()` + `cung_than_index()` | An Mệnh-Thân |
| `cuc_so()` | An Cục |
| `tu_vi_position()` + `place_14_chinh_tinh()` | An 14 chính tinh |
| `ta_phu()`, `huu_bat()` | Tả Hữu |
| `van_xuong()`, `van_khuc()` | Xương Khúc |
| `thien_khoi_viet()` | Khôi Việt |
| `kinh_duong()`, `da_la()` | Dương Đà |
| `hoa_linh_tinh()` | Hỏa Linh |
| `dia_khong_kiep()` | Không Kiếp |
| `loc_ton()` | Lộc Tồn |
| `tu_hoa_assignments()` | Tứ Hóa |
| `menh_chu()`, `than_chu()` | Mệnh chủ + Thân chủ |
| `dau_quan()` | Đẩu Quân |
| `dai_van_trajectory()` | Đại Vận |
| `tieu_han_for_age()` | Tiểu Hạn |

→ Engine đã có **~30 functions** an sao chính.

---

## II. ❌ Gaps: Sao chưa có trong engine

### 1. Bộ 12 sao Thái Tuế (chu trình theo địa chi năm sinh)

| # | Sao | Ý nghĩa (Q2) | Function cần thêm |
|---|---|---|---|
| 1 | **Thái Tuế** | Sao chủ năm hiện hành, có ảnh hưởng nhiều mặt | `thai_tue(year_branch)` |
| 2 | **Thiếu Dương** | Chủ vui vẻ, hỉ sự (thuận theo Thái Tuế +1) | `thieu_duong()` |
| 3 | **Tang Môn** | Chủ tang chế, mất mát (+2) | `tang_mon()` |
| 4 | **Thiếu Âm** | Chủ phụ nữ trợ giúp (+3) | `thieu_am()` |
| 5 | **Quan Phù** | Chủ kiện tụng (+4) | `quan_phu()` |
| 6 | **Tử Phù** | Chủ tử biệt (+5) | `tu_phu()` |
| 7 | **Tuế Phá** | Chủ phá tài, xung đột (+6, đối với Thái Tuế) | `tue_pha()` |
| 8 | **Long Đức** | Chủ phúc đức (+7) | `long_duc()` |
| 9 | **Bạch Hổ** | Chủ tai nạn, máu (+8) | `bach_ho()` |
| 10 | **Phúc Đức** | Chủ phúc lộc (+9) | `phuc_duc_sao()` |
| 11 | **Điếu Khách** | Chủ khách đến nhà, sự việc bất ngờ (+10) | `dieu_khach()` |
| 12 | **Bệnh Phù** | Chủ bệnh tật (+11) | `benh_phu()` |

**Quy tắc Q2**: từ Thái Tuế đếm thuận 12 cung → 12 sao theo thứ tự trên.

### 2. Bộ Tam Thai + Bát Tọa

| Sao | An theo | Q2 reference |
|---|---|---|
| **Tam Thai** | An từ vị trí Tả Phụ theo ngày sinh | p86 |
| **Bát Tọa** | An từ vị trí Hữu Bật theo ngày sinh | p86 |

### 3. Cặp sao Thiên Khốc + Thiên Hư

| Sao | Quy tắc Q2 | Ý nghĩa |
|---|---|---|
| **Thiên Khốc** | Khởi Ngọ, NGHỊCH đếm theo năm | Bi thương |
| **Thiên Hư** | Khởi Ngọ, THUẬN đếm theo năm | Hư hao |

### 4. Cặp sao Long Trì + Phượng Các

| Sao | Quy tắc Q2 | Ý nghĩa |
|---|---|---|
| **Long Trì** | Khởi Tý THUẬN đến năm sinh | Long trọng |
| **Phượng Các** | Khởi Tuất NGHỊCH đến năm sinh | Trang trí phong nhã |

### 5. Sao đại tiểu hao + biến

- **Đại Hao**, **Tiểu Hao** (theo Lộc Tồn) — chủ hao tổn
- **Cô Thần**, **Quả Tú** (theo địa chi năm)
- **Hồng Loan**, **Thiên Hỉ** (đào hoa + hỉ sự)
- **Phi Liêm**, **Hỉ Thần**, **Phục Binh** (Thái Tuế bộ)

---

## III. Khẩu quyết Q2 cần code vào engine

### Quyết an Mệnh chủ (p90)

| Mệnh cung địa chi | Mệnh chủ |
|---|---|
| Tý | Tham Lang |
| Sửu, Hợi | Cự Môn |
| Dần, Tuất | Lộc Tồn |
| Mão, Dậu | Văn Khúc |
| Thìn, Thân | Liêm Trinh |
| Tỵ, Mùi | Vũ Khúc |
| Ngọ | Phá Quân |

✅ **Đã có**: `menh_chu()` trong an_sao.py.

### Quyết an Thân chủ (p90)

| Năm sinh địa chi | Thân chủ |
|---|---|
| Tý, Ngọ | Hỏa Tinh |
| Sửu, Mùi | Thiên Tướng |
| Dần, Thân | Thiên Lương |
| Mão, Dậu | Thiên Đồng |
| Thìn, Tuất | Văn Xương |
| Tỵ, Hợi | Thiên Cơ |

✅ **Đã có**: `than_chu()` trong an_sao.py.

### Quyết "Trúc La tam hạn" (p90) — chưa có engine

Đây là 3 đại hạn nguy hiểm tổ sư cảnh báo:
1. **Kim Tỏa Quan** — sao xấu chiếu Mệnh ở năm Lưu Niên cụ thể
2. **Thiết Xà Quan** — Đà La + Phá Quân + Hóa Kỵ
3. **Trúc La hạn** — Kình Đà + Hỏa Linh tam hợp

→ Cần code logic detect 3 hạn này khi user xem Lưu Niên.

---

## IV. Engine update plan (refined sau Q2)

| Priority | Việc | Effort | Source |
|---|---|---|---|
| 🥇 | Thêm 12 sao Thái Tuế (function `thai_tue_belt()`) | 1h | Q2 p85, p100 |
| 🥇 | Cô Thần + Quả Tú + Hồng Loan + Thiên Hỉ (4 sao biểu cảm) | 30p | Q2 p85-86 |
| 🥈 | Tam Thai + Bát Tọa (theo ngày sinh) | 30p | Q2 p86 |
| 🥈 | Thiên Khốc + Thiên Hư | 20p | Q2 p86 |
| 🥈 | Long Trì + Phượng Các | 20p | Q2 p86 |
| 🥉 | Detect "Trúc La tam hạn" trong Lưu Niên | 1-2h | Q2 p90 |
| 🥉 | Verify engine match với 60+ case studies Q4 (regression test) | 2h | Q4 lá số cổ kim |

**Total**: ~5-6h để engine có đủ bộ sao Q2.

---

## V. Lá số Anh — bonus phát hiện từ Q2

Với engine update sao Thái Tuế bộ, lá số Anh sẽ có thêm các thông tin:

- **Thái Tuế năm 2026** (Bính Ngọ): tại Ngọ → cùng cung **Huynh Đệ** (có Thiên Tướng + Kình Dương)
- **Bạch Hổ 2026**: 8 cung sau Thái Tuế → tại **Sửu** (Quan Lộc — Thiên Khôi)
- **Tang Môn 2026**: 2 cung sau → tại **Thân** (Tử Tức — Tử Vi + Thất Sát)

→ Khi build xong, panel Lưu Niên có thể hiển thị 12 sao Thái Tuế đi qua từng cung mỗi năm — rich hơn nhiều.

---

## VI. Stats sau Q2

| Metric | Before Q2 | After Q2 | Δ |
|---|---|---|---|
| Cách cục unique | 985 | **1,193** | +208 |
| Concepts | 576 | **686** | +110 |
| Trang processed | 196 | **258** | +62 |
| Cuốn PDF Tử Vi | 3 (Q1+Q3+Q4) + Bộ | **4 (Q1+Q2+Q3+Q4) + Bộ v2** | +Q2 |

**Cost**: ~$0.13 (62 × $0.002 DeepSeek) + $0 MiniMax.

---

_Source: thâm nhuần Q2 background pipeline 2026-05-19 đêm._
_Files: `data/yi_publishing/q1_tuvi/master/{cach_cuc_index,concepts_index}.json`_
_PDF: `data/published/tu-vi-q2-an-sao.pdf` (116 trang) + `data/published/tu-vi-bo-toan-thu.pdf` (395 trang, 4-quyển)_
