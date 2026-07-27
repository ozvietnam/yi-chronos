# Nghiên cứu: Tử Vi mang lại thông tin gì cho user? · Inventory kỳ vọng × Đối chiếu sản phẩm YI

> **Ngày:** 2026-07-27 · **Hướng:** nghiên cứu (không UX đại chúng)  
> **Câu hỏi Anh:** Xem Tử Vi, user có thể nhận những thông tin gì? Liệt kê kỳ vọng → đối chiếu sản phẩm → gợi ý phần còn thiếu.  
> **Paradigm:** đọc đồng dạng · CƠ+BIẾN · mệnh = động từ · Iron #3/#4/#6/#8/#9 — **không** liệt kê như menu bói.

**Chứng cứ sản phẩm:** `engine/tu_vi/*` · `api/tu_vi_routes.py` · `TuViLaSoPanel` · thư viện · vận hạn · Gia đạo · CDK · Đằng Sơn · 3-layer · PDF cache.

---

## 1. Trả lời ngắn

Tử Vi có thể mang lại **sáu họ thông tin**:

1. **Cấu trúc lá số** — ai đứng ở đâu trên 12 sân khấu  
2. **Miền đời (12 cung)** — từng khía cạnh quan sát (không bản án)  
3. **Biến theo thời gian** — Đại Vận → Tiểu Hạn → Lưu niên/nguyệt/tuần/nhật  
4. **Cách cục & biến hóa** — tổ hợp sao, Tứ Hóa, miếu/hãm  
5. **Quan hệ / đa lá** — Phu Thê, gia đạo, hợp đĩa, case lịch sử  
6. **Gương tâm (paradigm YI)** — Ngũ Uẩn, khe tỉnh thức, việc xử lý tính  

YI **từ chối** họ thứ bảy cổ điển: đoán giàu–nghèo / chết / xổ số / bệnh danh / ngày cưới cố định.

---

## 2. Danh mục kỳ vọng chi tiết (thông tin user-facing hợp lệ)

### A. Cấu trúc lá số (CƠ — snapshot)

| # | Thông tin kỳ vọng | 1 dòng |
|---|---|---|
| A01 | Ngày giờ + lịch âm đã resolve | Neo lập bàn |
| A02 | Giới tính → chiều Đại Vận / trọng cung | Nam–nữ mệnh khác nhấn |
| A03 | Mệnh cung + chi | Sân khấu bản thể |
| A04 | Thân cung + chi | Hậu vận / thân làm |
| A05 | Quan hệ Mệnh–Thân (đồng/lệch/xung) | Tâm nói vs thân làm |
| A06 | Ngũ Cục + tên cục | Hàm an Tử Vi + Trường Sinh |
| A07 | Mệnh chủ / Thân chủ | Ai cầm trịch |
| A08 | 12 cung × Địa Chi (+ thiên can ngũ hổ) | Bản đồ địa bàn |
| A09 | 14 chính tinh vị trí | Xương sống |
| A10 | Vô chính diệu tại cung | Đọc đối/xung/phụ |
| A11 | Lục cát / lục sát / Lộc–Mã | Trợ & áp lực |
| A12 | Tứ Hóa natal (Lộc Quyền Khoa Kỵ) | DNA biến hóa |
| A13 | Vòng Trường Sinh | Tuổi đời hành cục |
| A14 | Vòng Thái Tuế (12) | Lớp khí năm trên natal |
| A15 | Tuần Không / Triệt | Vùng suy / trống |
| A16 | Sao Q2 / sao lẻ / Bác Sĩ / Tướng Tinh | Lớp phụ đầy đủ |
| A17 | Đẩu Quân neo sinh | Neo lưu nguyệt |
| A18 | Độ sáng miếu–vượng–đắc–hãm từng chính tinh | Độ khó bài học |
| A19 | Tam phương tứ chính từ Mệnh | Khung đọc chính |
| A20 | Metadata sao (hành, âm dương, chủ về) | Nền sinh–khắc |

### B. Miền đời theo 12 cung (+ Thân)

Mỗi cung kỳ vọng: **chính tinh · phụ/sát · thế · miếu/hãm · câu hỏi miền · (YI) chân dung tâm**.

| Cung | Thông tin kỳ vọng (loại) |
|---|---|
| **Mệnh** | Cách vận hành tính; khí chất; Mệnh–Thân khớp/lệch |
| **Phụ Mẫu** | Quan hệ bậc trên; nền gia; học sớm / ấn |
| **Phúc Đức** | An lòng; sở thích tinh thần; “phúc” nội |
| **Điền Trạch** | Không gian sống; tích sản nhà; ổn định vs đổi chỗ |
| **Quan Lộc** | Vai trò xã hội / nghề; kiểu lãnh đạo–chuyên môn |
| **Nô Bộc** | Bạn–đồng nghiệp–cấp dưới; mạng lưới tin cậy |
| **Thiên Di** | Ra ngoài môi trường quen; danh bên ngoài |
| **Tật Ách** | Cơ địa / stress pattern (*không* chẩn bệnh) |
| **Tài Bạch** | Phong cách kiếm–giữ–tiêu (*không* đoán giàu nghèo) |
| **Tử Tức** | Nuôi dạy / “con” mở rộng = dự án–học trò (*không* đoán số/giới con) |
| **Phu Thê** | Archetype phối ngẫu; chất lượng quan hệ; mùa duyên |
| **Huynh Đệ** | Anh chị em / core team; tranh–hòa |
| **Thân** | Thân rơi cung nào → trọng tâm hậu vận |

### C. Biến theo thời gian (BIẾN)

| # | Thông tin kỳ vọng |
|---|---|
| C01 | Đại Vận hiện tại: cung Thể, tuổi, sao, Tứ Hóa DV |
| C02 | Chuỗi 12 Đại Vận đời người (overview) |
| C03 | Intra-cung trong hạn 10 năm |
| C04 | Tiểu Hạn năm nay (+ chồng DV) |
| C05 | Lưu Niên: Thái Tuế cung, Lưu Tứ Hóa, Lộc/Kình/Đà/Khôi/Việt… |
| C06 | Overview vài năm lưu niên tới |
| C07 | Lưu Nguyệt / Đẩu Quân 12 tháng |
| C08 | Tuần (thượng/trung/hạ) trong tháng |
| C09 | Lưu Nhật (fine-grain) |
| C10 | Life-arc / nhịp khí năm (quan sát, không cát hung tuyệt) |
| C11 | Thể–Dụng: cung gốc × cung vận |
| C12 | Hồi chiếu tam phương khi đọc vận |

### D. Cách cục & pattern đặc biệt

| # | Thông tin kỳ vọng |
|---|---|
| D01 | Danh sách cách cục khớp lá (tên + cấp + nguồn) |
| D02 | Giải thích cách — cấu trúc cần quan-sát |
| D03 | Kỳ cách / phá cách (điều kiện) |
| D04 | Tứ Hóa × cung (ý nghĩa hóa tại miền) |
| D05 | Đồng cung / giáp / hội / xung giữa sao |
| D06 | Cặp kinh điển (Tử–Phủ, Sát–Phá–Tham…) |
| D07 | Chart strength tổng hợp miếu/hãm |
| D08 | Case lịch sử “giống pattern” |

### E. Quan hệ / đa lá / gia đạo

| # | Thông tin kỳ vọng |
|---|---|
| E01 | Đọc sâu cung Phu Thê + quy luật phái |
| E02 | Partner traits từ cấu trúc |
| E03 | Hợp đĩa / synastry 2 lá (*không* đoán hợp–tan tuyệt) |
| E04 | Gia đạo: Phúc Đức, Nô Bộc, quan hệ nhà |
| E05 | Luận con / cung sau / đặt tên (khung cấu trúc) |
| E06 | Đa phái đối chiếu cùng một lá (Bắc / CDK / Đằng Sơn) |

### F. Paradigm YI (thông tin “gương tâm”)

| # | Thông tin kỳ vọng |
|---|---|
| F01 | Ngũ Uẩn tại cung/sao (5 bước tiến trình tâm) |
| F02 | 8 lớp chân dung (căn cơ → gốc tham → … → khe tỉnh thức) |
| F03 | Câu tự soi / việc nhỏ tuần này (mệnh = động từ) |
| F04 | Disclaimer + safety (không dọa chết/bệnh) |
| F05 | Atom / trích dẫn nguồn đã duyệt |
| F06 | Phê mệnh có cấu trúc (khai đề → miền → vận) nhưng tone đồng dạng |

### G. Cổ pháp — YI **không** cung cấp (whitelist từ chối)

Đoán giàu–nghèo cụ thể · thắng cược/xổ số · ngày chết · số/giới con · ngày cưới/ly hôn cố định · chức danh cụ thể · bệnh danh · bản án cát/hung tuyệt · hù giải hạn.

---

## 3. Đối chiếu sản phẩm YI hôm nay

Chú giải: **●** đủ user-facing · **◐** có engine/UI nhưng mỏng / ẩn / VIP / cache · **○** thiếu hoặc chưa khép paradigm

### A. Cấu trúc

| Kỳ vọng | Status | Ghi chú ngắn |
|---|---|---|
| A01–A18 natal layers | **●** | `cast_la_so` + TuViLaSo cơ bản/nâng cao rất dày |
| A19 tam phương tứ chính UI rõ | **◐** | Có trong vận hạn `hoi_chieu`; lá số chính chưa “highlight khung” mặc định |
| A20 metadata trên lá | **◐** | Thư viện ★; trên cell lá chủ yếu tên sao + hóa + độ sáng |

### B. 12 cung miền đời

| Kỳ vọng | Status | Ghi chú |
|---|---|---|
| Lưới 12 cung + sao | **●** | |
| Interpretation / cung reading | **◐** | Có API + UI trong “Đọc sâu”; không phải lớp mặc định sau cast |
| Ngũ Uẩn theo cung | **◐** | Có khi bung cung; coverage & 8 lớp chưa đều 14 sao |
| Plain “miền này mời quan-sát gì” (1 câu/cung) | **○** | Còn thiên jargon / LLM dài hơn là thẻ miền chuẩn |
| Thư viện sao / cục / thân–mệnh / vòng | **●** | Không cần ngày sinh |
| Ngũ Cục “chất người” | **○** | UI `chua_co_nguon` |

### C. Thời gian

| Kỳ vọng | Status | Ghi chú |
|---|---|---|
| Đại Vận 12 + grounded van_han | **●** | |
| Lưu niên / nguyệt / tuần / nhật skeleton | **●** | `van_han.py` |
| Overview + life_arc | **●** | |
| LLM vận chỉ edit-from-source | **◐** | Có; phụ thuộc rate limit / chất nguồn |
| Đọc Thể–Dụng user hiểu ngay | **◐** | Có field; UX/giải thích paradigm còn mỏng |
| Chuỗi “mùa quan sát” plain (không cát hung) | **○** | Arc số có; câu plain chuẩn hóa chưa |

### D. Cách cục

| Kỳ vọng | Status | Ghi chú |
|---|---|---|
| Dict 545+ match | **●** | |
| Panel + PDF từ cache | **◐** | Phụ thuộc analyze/run-all |
| Kỳ cách / phá cách có điều kiện rõ | **◐** | Corpus Q3/Q4; chưa sản phẩm hóa thành lớp đọc |
| Case studies match | **●** | API + UI |

### E. Quan hệ

| Kỳ vọng | Status | Ghi chú |
|---|---|---|
| Phu Thê Bắc phái flagship | **●** | Panel riêng rất sâu |
| Gia đạo / luận con / đặt tên | **●** | `GiaDaoPanel` |
| Hợp đĩa 2 người (synastry TV) | **◐** | Có module hướng; chưa = cửa sổ ngang Phu Thê |
| CDK / Đằng Sơn = thế giới riêng | **●** | Đúng kiến trúc đa phái Anh chốt |

### F. Gương tâm YI

| Kỳ vọng | Status | Ghi chú |
|---|---|---|
| Quán chiếu Ngũ Uẩn trên lá | **◐** | Có; chưa xương sống mặc định mọi buổi đọc |
| 8 lớp đủ 14 chính tinh | **○/◐** | Lộ trình thủ thư; mẫu chưa phủ |
| Việc nhỏ / checkbox streak | **○** | Chưa khép product |
| Safety check | **●** | |
| Phê mệnh free / VIP / 3-layer / Deep Reading | **●/◐** | Nhiều kênh LLM; **lệch** so với grounded-first |
| Atom commentaries nuôi luận | **○** | Gap đã ghi: commentaries gần chết với council |
| PDF báo cáo | **◐** | Phụ thuộc cache |

### G. Từ chối

| Kỳ vọng | Status |
|---|---|
| Filter psychological + paradigm copy | **◐** | Có nền; cần audit output LLM định kỳ |

---

## 4. Khoảng trống có ý nghĩa (gợi ý phát triển — nghiên cứu → làm)

Ưu tiên theo **độ thiếu × đúng cửa sổ Tử Vi** (không gộp phái).

### P1 — Khép “đọc một cung / một mùa” trong đúng thế giới Bắc phái
1. **Thẻ miền 12 cung (deterministic):** mỗi cung = câu hỏi miền + sao cầm micro + 1 câu plain “quan-sát gì” + link Ngũ Uẩn — trước LLM.  
2. **Mặc định sau cast:** hiện Mệnh + Thân–Mệnh + 1 Đại Vận hiện tại (plain) — lớp nâng cao giữ nguyên (không cắt thế giới).  
3. **Chuẩn hóa BIẾN plain:** template “mùa ĐV / năm này mời quan-sát cung X vì …” từ `vi_tri` + `sao_nguon`, 0-LLM trước.

### P2 — Xương sống paradigm (đúng GOAL thủ thư)
4. **Phủ 8 lớp / Ngũ Uẩn cho 14 chính tinh** theo lộ trình đã có — mẫu duyệt từng sao.  
5. **Nối `atom_commentaries` + `founder_verified`** vào phê mệnh / 3-layer / Hermes tu-vi — giảm luận “trôi”.  
6. **Ngũ Cục “chất người”** — chỉ khi có nguồn; bỏ placeholder im lặng hoặc ghi “chưa có nguồn”.

### P3 — Lớp còn mỏng trong taxonomy
7. **Tam phương tứ chính highlight** trên lưới lá (A19).  
8. **Kỳ cách / phá cách** thành lớp đọc có điều kiện (không chỉ tên cách).  
9. **Hợp đĩa Tử Vi** ngang tầm Phu Thê panel (E03) — khi Anh mở bàn quan hệ liên cửa sổ.  
10. **Việc nhỏ tuần này** gắn khe tỉnh thức Mệnh/ĐV — optional, không biến thành habit-app nuốt lá số.  
11. **Audit LLM** định kỳ theo whitelist G (refuse list).  
12. **PDF** one-click từ cast (ít phụ thuộc run-all) hoặc UX báo rõ “cần phân tích trước”.

### Không ưu tiên (nghiên cứu này)
- Gộp CDK + Bắc + Đằng Sơn thành một funnel.  
- Thêm môn ngoài Tử Vi vào default.  
- Surface predict cổ (G).

---

## 5. Kết luận nghiên cứu

- **Kỳ vọng cổ + YI-safe ≈ 150–200 loại thông tin**; sản phẩm đã **rất dày ở CƠ (lá số) và xương BIẾN (van_han)**, cộng thư viện và vài cửa sâu (Phu Thê, CDK, Đằng Sơn).  
- **Thiếu chủ yếu không phải “thêm sao”**, mà: (1) lớp **plain miền/mùa deterministic**, (2) **phủ chân dung Ngũ Uẩn**, (3) **nuôi luận bằng nguồn đã duyệt**, (4) vài pattern cao cấp (kỳ cách, tam phương UI, hợp đĩa).  
- Kiến trúc **mỗi cửa sổ một thế giới** đang đúng với inventory; phần còn thiếu nằm **bên trong cửa Tử Vi**, không phải UX gom đại chúng.

---

*Hết vòng nghiên cứu câu hỏi. Bước tiếp nếu Anh muốn: chọn 1 mục P1–P2 để đào sâu thiết kế (không code) hoặc audit live 1 lá mẫu theo checklist A–F.*
