# Nghiên cứu sâu: Tử Vi mang lại thông tin gì? · Phương pháp · Kỳ vọng · Gap sản phẩm

> **2026-07-27 v2** — thay bản inventory nông (catalog phẳng).  
> **Câu hỏi Anh:** Xem Tử Vi, user nhận được thông tin gì? Liệt kê kỳ vọng chi tiết → đối chiếu sản phẩm → gợi ý thiếu.  
> **Kỷ luật:** nghiên cứu · đa phái độc lập (#3) · CƠ+BIẾN (#6) · mệnh động từ (#8) · không predict (#9).  
> **Nguồn:** Toàn Thư Q1–Q4 journals · Đằng Sơn · Thiên Lương · Trung Châu · Bôn Ba Ngũ Uẩn · `engine/tu_vi/*` · wiki counts 2026-07-27.

---

## 0. Vì sao bản trước nông

Liệt kê “12 cung / Đại Vận / cách cục” chỉ là **mục lục cấu trúc**, chưa trả lời:

1. Thông tin đó thuộc **loại nhận thức** nào (mô tả cấu trúc? gợi mùa? so sánh phái?)  
2. Phải đọc theo **thứ tự / điều kiện** nào mới thành thông tin (không nhảy cóc)  
3. Cùng một lá, **mỗi phái rút thông tin khác** thế nào  
4. Trong repo, cái gì là **engine đã có nhưng chưa thành thông tin user**, cái gì **chưa có dữ liệu**

Bản này đi theo 4 tầng đó.

---

## 1. Tử Vi là máy thông tin kiểu gì?

Theo Phú Thái Vi + Đằng Sơn + paradigm YI:

| Tuyên bố | Hệ quả về “thông tin” |
|---|---|
| *Lý chỉ dị minh* — có nguyên lý, không mê tín | User nhận **cấu trúc có thể kiểm** (vị trí, miếu/hãm, hóa), không bùa |
| *Sát cơ + bất vong biến* | Mọi buổi đọc phải có **CƠ (snapshot)** và **BIẾN (vận)** — thiếu một = thông tin cụt |
| *Giả tướng* (Đằng Sơn) | Thông tin = **biểu kiến/cấu trúc đồng dạng**, không phải nhân quả “sao gây ra giàu” |
| *Mệnh = động từ* | Thông tin hợp lệ kết bằng **cách vận hành tính**, không “số anh là…” |
| *Mỗ niên / mỗ tinh* (Q4) | Tầng gợi mở: chỉ đường tra, **không spell-out tiên tri** |

**Định nghĩa làm việc:**  
> Một “thông tin Tử Vi” = một mệnh đề user kiểm được trên lá / trên thời gian / trên sách nguồn, giúp **quan-sát cấu trúc tâm–đời**, không phải dự báo sự kiện đóng.

---

## 2. Bảy loại thông tin (phân loại nhận thức)

Mọi hạng mục cụ thể ở §4–§6 đều thuộc một trong bảy loại:

| Loại | Ký hiệu | User nhận được | Ví dụ |
|---|---|---|---|
| **Cấu trúc tĩnh** | Σ | Ai đứng đâu, mạnh yếu thế nào | 14 chính tại cung, miếu/hãm, Tuần/Triệt |
| **Topology quan hệ** | Τ | Sao/cung liên kết ra sao | Tam phương tứ chính, giáp, xung, tam hợp |
| **Danh pháp / cách** | Κ | Tên pattern đã có trong truyền thống | Cự Nhật, Bát Pháp thành/phá, Thập Dụ |
| **Miền đời** | Δ | Cấu trúc chiếu vào lĩnh vực nào | Quan Lộc → nghề; Phu Thê → quan hệ |
| **Thời–biến** | Χ | Cùng cấu trúc đang “mùa” nào | ĐV, LN, Đẩu Quân tháng, life_arc khí |
| **Tiến trình tâm** | Ψ | Khát / uẩn / khe thoát | Ngũ Uẩn 8 lớp, thái độ số phận Đằng Sơn |
| **Đối chiếu nguồn** | Ω | Sách/phái nói gì · đồng · lệch | Cross-school atoms, case lịch sử |

Loại **bị cấm** (không thuộc thông tin YI): dự báo đóng (giàu/nghèo/chết/xổ số/bệnh danh/ngày cưới cố định).

---

## 3. Thứ tự đọc = thứ tự sinh thông tin (method stack)

Thông tin không độc lập. Thiếu tầng dưới → tầng trên thành bịa.

### 3.1 Tiến trình “đất trước hạt” (Anh chốt · `doc_tien_trinh.py`)

```
Phúc Đức (phúc ấm tổ) → Phụ Mẫu (gen/mầm) → Điền Trạch (vun/phá)
        → đặt Mệnh + Thân vào môi trường đó
```

**Thông tin kỳ vọng theo bước:** nền chạy ngầm → mầm trao → môi trường đầu đời → bản thể trong ngữ cảnh.  
**Không:** nhảy thẳng “Mệnh anh là X” rồi bỏ ba cung đất.

### 3.2 Bốn lớp trong một cung (chống ảo giác)

| Lớp | Thông tin | Điều kiện |
|---|---|---|
| 1 | Tính chất **từng sao** (def) | Có nguồn `sao_noi_dung` fv=1 |
| 2 | Sao **trên cung này** | Có nguồn per-cung fv=1 |
| 3 | **Combo đã kết khối** (rule-match) | Chỉ cách thật — không gom lỏng |
| 4 | **Tam phương tứ chính** | Topology chiếu |

Thiếu nguồn → **gap khai trống** (quote-or-silence), không LLM đắp.

### 3.3 Lồng tầng thời gian (Anh · bức tranh thăng trầm)

```
Mệnh chủ + Thân chủ + Cục (hằng)
  └─ Đại Vận (chủ đề ~10 năm)
       └─ Lưu Niên (can năm → Tứ Hóa)
            └─ Lưu Nguyệt / Đẩu Quân
                 └─ Tuần / Lưu Nhật
```

Mỗi tầng dưới chỉ thành thông tin khi đọc **trong** tầng trên (Thể–Dụng / bao trùm).

### 3.4 Q3 — ba lớp chồng trong diễn giải cung

1. Sao × miếu/hãm  
2. Sao × sao đồng cung  
3. Sao × sát phá  

→ Thông tin “Huynh Đệ có Thiên Cơ” **chưa đủ**; phải kèm độ sáng + đồng cung + sát.

---

## 4. Catalog kỳ vọng chi tiết (theo pha buổi đọc)

### Pha 0 — Input & độ tin cậy Σ

| ID | Thông tin kỳ vọng | Ghi chú phương pháp |
|---|---|---|
| P0.1 | Ngày giờ + true solar (nếu có kinh độ) | Sai giờ = sai Mệnh |
| P0.2 | Âm lịch resolve + giờ chi | |
| P0.3 | Giới tính → chiều ĐV / trọng cung | |
| P0.4 | **Độ chắc giờ** (biết / khoảng / quiz rectification) | Q4 Định thời khắc |
| P0.5 | Phái đang đứng (Bắc / CDK / Đằng Sơn…) | #3 — nói rõ khung |

### Pha 1 — CƠ: lập bàn Σ + Τ

| ID | Thông tin | Loại |
|---|---|---|
| C1.1 | Mệnh / Thân chi + quan hệ đồng·lệch·xung | Σ Τ |
| C1.2 | Ngũ Cục + tên + (nếu có) “chất cục” có nguồn | Σ |
| C1.3 | Mệnh chủ / Thân chủ | Σ |
| C1.4 | 12 cung chức năng × chi × can ngũ hổ | Σ |
| C1.5 | 14 chính + vô chính diệu | Σ |
| C1.6 | Lục cát / lục sát / Lộc–Mã | Σ |
| C1.7 | Tứ Hóa natal map lên sao–cung | Σ Τ |
| C1.8 | Trường Sinh · Thái Tuế belt · Bác Sĩ · Tướng · sao Q2/Q3/lẻ | Σ |
| C1.9 | Tuần / Triệt | Σ |
| C1.10 | Độ sáng từng chính tinh tại chi | Σ |
| C1.11 | Đẩu Quân neo sinh | Σ |
| C1.12 | **Tam phương tứ chính từ Mệnh** (Tài–Quan–Phúc + xung) | Τ |
| C1.13 | **Giáp cung / mượn sao đối** | Τ |
| C1.14 | **3 vòng xương sống** (Lộc Tồn / Thái Tuế / Tràng Sinh) — Thiên Lương | Σ Ψ |
| C1.15 | **Bậc tuổi Can–Chi** (1–5) — Thiên Lương | Ψ |
| C1.16 | Cảnh báo **Nhân Cung** (chính tinh thất vị) — Trần Đoàn | Κ |

### Pha 2 — Cách đọc cấu trúc quanh Mệnh Κ

| ID | Thông tin | Nguồn cổ |
|---|---|---|
| K2.1 | **Bát Pháp** thành/phá/cứu/khí (8 lối) | Toàn Thư p19–20 |
| K2.2 | **Thập Dụ** (10 điều bản/hợp/lân/xung) | Toàn Thư p19 |
| K2.3 | Cách cục có tên khớp lá (+ cấp + điều kiện) | Phú Thái Vi 545+ |
| K2.4 | Kỳ cách / phá cách có điều kiện | Q3 |
| K2.5 | Biến cách: Vong Thần, Câu Giảo, Phản Bối… (106 concept Q1) | Q1 concepts |
| K2.6 | Bộ phụ tinh đủ cặp + thế (đồng/giáp/hội/xung) | Trung Châu |
| K2.7 | Điểm nổi bật toàn lá (dị cách, hóa kỵ trọng cung, cung rực/nặng) | Heuristic có nguồn |

### Pha 3 — Đất → hạt (tiến trình) Δ + Ω

| ID | Thông tin |
|---|---|
| D3.1 | Phúc Đức: phúc ấm / sở thích tinh thần (4 lớp nguồn) |
| D3.2 | Phụ Mẫu: gen–bậc trên–học sớm |
| D3.3 | Điền Trạch: môi trường / tích sản / ổn–động |
| D3.4 | Mệnh (+ Thân): vận hành tính trong ngữ cảnh 3 cung trên |
| D3.5 | Gaps: sao nào thiếu def / thiếu per-cung (trung thực) |

### Pha 4 — Mười hai miền đời Δ (mỗi cung)

Với **mỗi** cung, kỳ vọng đủ bộ:

1. Vai trò miền (câu hỏi đời)  
2. Chính + phụ/sát + hóa tại chỗ  
3. Miếu/hãm chính tinh  
4. Lớp 1–4 nguồn (def / per-cung / combo / tam phương cung đó)  
5. (YI) Ngũ Uẩn / gốc tham / khe tỉnh thức nếu có dataset  
6. Bias giới / năm sinh đặc thù nếu sách có (Q3)

| Cung | Trọng tâm thông tin (không phải phán) |
|---|---|
| Mệnh | Cách vận hành tính; nhất quán Mệnh–Thân |
| Phụ Mẫu | Quan hệ bậc trên; nền |
| Phúc Đức | An lòng; phúc nội |
| Điền Trạch | Chỗ ở / tích sản / nhân khẩu nhà |
| Quan Lộc | Vai trò xã hội–nghề |
| Nô Bộc | Mạng lưới ngang/dưới |
| Thiên Di | Ra ngoài môi trường quen |
| Tật Ách | Cơ địa / stress (*không* bệnh danh) |
| Tài Bạch | Phong cách kiếm–giữ (*không* đoán giàu) |
| Tử Tức | Nuôi dạy / “con” mở rộng (*không* số/giới con) |
| Phu Thê | Archetype phối; chất quan hệ; mùa duyên |
| Huynh Đệ | Anh em / core team |

### Pha 5 — BIẾN Χ (mỗi tầng = Thể–Dụng + phi hóa)

| ID | Thông tin |
|---|---|
| X5.1 | ĐV hiện tại: cung Thể, tuổi, sao, intra-cung |
| X5.2 | Overview 12 ĐV đời |
| X5.3 | Tứ Hóa theo Can ĐV · phi hóa chồng natal |
| X5.4 | Tiểu Hạn năm + **quy tắc chồng hung chỉ khi ĐV∩TH** (Q3) |
| X5.5 | Lưu Niên: Thái Tuế cung, Lưu Tứ Hóa, Lộc/Kình/Đà/Khôi… |
| X5.6 | Bao trùm ĐV lên LN (foreground Mệnh chủ/Cục) |
| X5.7 | Lưu Nguyệt / Đẩu Quân 12 tháng + cát tinh đồng hành (Q3) |
| X5.8 | Tuần / Lưu Nhật |
| X5.9 | **Đường cong khí** liên tục (động↔tĩnh, điểm quay Hóa Kỵ, tự hóa xả) — *không* giàu–nghèo |
| X5.10 | Rule per-cung vận có nguồn (Trung Châu) + hồi chiếu tam phương |

### Pha 6 — Chủ đề đời sống Δ (không bắt user nghĩ “cung”)

| ID | Chủ đề | Cung gom |
|---|---|---|
| T6.1 | Sự nghiệp & công danh | Quan + Mệnh + Tài + Di |
| T6.2 | Tình duyên & hôn nhân | Phu Thê + Mệnh + Phúc |
| T6.3 | Tài lộc & của cải | Tài + Điền + Phúc + Quan |
| T6.4 | Sức khỏe & thân tâm | Tật + Mệnh + Phúc |
| T6.5 | Gia đạo tổng | Phụ + Phu + Tử + Huynh + Nô |

Mỗi chủ đề kỳ vọng: atoms đa phái · bộ phụ · cách · hóa · narrative paradigm · (tuỳ) vòng đời theo tuổi×giới.

### Pha 7 — Quan hệ / đa lá Ε

| ID | Thông tin |
|---|---|
| E7.1 | Phu Thê Bắc phái: quy luật + cross-ref + partner traits |
| E7.2 | Duyên / đào hoa vận (mùa, không ngày cưới) |
| E7.3 | Hợp đĩa: Tử Vi × Bát Tự × Hà Lạc (trục cương–nhu) |
| E7.4 | Gia quý an ở · năm sinh con (cấu trúc) · luận lá con · đặt tên |
| E7.5 | Case lịch sử “pattern giống” (học, không định mệnh) |

### Pha 8 — Gương tâm YI Ψ

| ID | Thông tin |
|---|---|
| Y8.1 | Ngũ Uẩn 5 bước tại sao/cung |
| Y8.2 | 8 lớp v3 (căn cơ → … → khe tỉnh thức → ví dụ → căn cứ) |
| Y8.3 | Hồ sơ **thái độ số phận** 3 trục Định–Biến / Tác–Thụ / Nội–Ngoại (Đằng Sơn) |
| Y8.4 | Việc xử lý tính / tự soi (không habit-app nuốt lá) |
| Y8.5 | Safety: pattern dark Q3 → self-care, không surface tử vong |
| Y8.6 | Disclaimer mượn khung soi tâm |

### Pha 9 — Đa thế giới phái Ω (cửa sổ riêng)

| ID | Thông tin |
|---|---|
| W9.1 | Bắc phái Toàn Thư (trên) |
| W9.2 | Chiếu Đởm Kinh: 18 Phi Tinh · matrix · cách CDK · luận VIP |
| W9.3 | Đằng Sơn: địa bàn khoa học · độ sáng · nhịp tháng · natal universe |
| W9.4 | Trung Châu nhấn Phu Thê / Di Cung Hoán Vị |
| W9.5 | Cross-school cùng sao×cung: agree / diverge / kept_all |

### Pha 10 — Thư viện (không cần ngày sinh) Ω

| ID | Thông tin |
|---|---|
| L10.1 | Hồ sơ 14 chính + phụ (Ngũ Uẩn, miếu 12 chi, quotes) |
| L10.2 | Ngũ Cục / Thân–Mệnh / ~89 vòng sao |
| L10.3 | Concept 320 · cách phổ biến · Q4 Thiên Quán / Chiếu Đởm corpus |

---

## 5. Đối chiếu sản phẩm (sâu — không chỉ “có/không”)

Chú giải: **●** user-facing đủ method · **◐** có nhưng lệch method / ẩn / VIP / mỏng nguồn · **◇** engine có, cửa sổ yếu hoặc orphan · **○** thiếu dữ liệu hoặc chưa làm · **✕** cố ý không làm (G)

### 5.1 Method stack

| Kỳ vọng method | Status | Bằng chứng / lỗ |
|---|---|---|
| Đất→hạt Phúc→Phụ→Điền→Mệnh | **◇** | `doc_tien_trinh.py` + deep_cung kéo 1 cung; **không** là mặc định sau cast trên lưới lá |
| 4 lớp quote-or-silence | **◇** | Có; phụ thuộc `sao_noi_dung` fv=1 (~2030/2603); gaps chưa luôn hiện cho user |
| Lồng ĐV⊃LN⊃tháng | **◐** | `van_han` + bao trùm; UI còn dễ đọc từng tầng rời |
| Q3 3 lớp miếu×đồng×sát | **◐** | Data/atoms có; render structured 3 lớp chưa chuẩn |
| life_arc đường cong khí | **●** | API + `VanHanPanel` tab Bức tranh; paradigm guard có test |

### 5.2 CƠ / topology / cách

| ID nhóm | Status | Chi tiết |
|---|---|---|
| C1.1–C1.11 lập bàn | **●** | `cast_la_so` + TuViLaSo cơ bản/nâng cao rất dày |
| C1.12–13 tam phương / giáp UI | **◐◇** | Có trong van_han / paradigm `to_hop_cung`; lưới lá chưa highlight mặc định |
| C1.14–16 ba vòng / bậc tuổi / nhân cung | **◐** | Wire qua `cross_school` → 3-layer warnings; **chưa** thẻ CƠ đầu buổi đọc mọi user |
| K2.1 Bát Pháp | **◇○** | Module `bat_phap.py` tồn tại — **gần như không gọi từ API/UI đọc lá** |
| K2.2 Thập Dụ | **◇○** | `thap_du.py` — orphan tương tự |
| K2.3 cách cục 545+/1193 | **◐** | Dict + panel; phụ cache analyze |
| K2.5 biến cách 106 | **○** | Concept Q1; chưa engine map đủ |
| K2.7 highlights | **◐** | Trong 3-layer; không phải lớp đầu mọi cast |

### 5.3 Miền & chủ đề

| | Status | |
|---|---|---|
| 12 cung trên lưới | **●** | |
| Interpretation / cung reading / deep_cung | **◐** | Đọc sâu / VIP / cache |
| Chủ đề 5 món (T6) | **◐** | API 3-layer; chưa = xương sống Bắc phái tab chính |
| Vòng đời tuổi×giới | **◐** | `vong_doi` trong 3-layer |
| Ngũ Cục “chất người” | **○** | `chua_co_nguon` |

### 5.4 BIẾN

| | Status | |
|---|---|---|
| ĐV / LN / tháng / tuần / nhật blocks | **●** | |
| Phi hóa + rules nguồn | **◐** | |
| Chồng hung ĐV∩Tiểu hạn (Q3) | **○◇** | Logic cổ đã ghi journal; chưa feature rõ |
| Đẩu Quân tháng + cát đồng hành | **◐** | Có endpoint/đồ; chưa đủ Q3 narrative |
| Foreground Mệnh chủ/Cục mỗi buổi vận | **◐** | Design đã chốt; implement một phần trong van_han |

### 5.5 Quan hệ & đa phái

| | Status | |
|---|---|---|
| Phu Thê Bắc flagship | **●** | |
| Gia đạo / duyên / hợp hôn | **◐●** | Nhiều API; hợp đĩa chưa cửa sổ ngang Phu Thê |
| CDK / Đằng Sơn tách cửa | **●** | Đúng kiến trúc Anh |
| Case match | **●** | |
| Thái độ số phận | **◐** | API 3-layer; ít nổi trên lá Bắc |

### 5.6 Gương tâm / dữ liệu

| | Status | Số liệu |
|---|---|---|
| Ngũ Uẩn dataset | **◐** | 95 records; 14 chính + một phần phụ; có field v3 |
| 8 lớp đủ sâu 14 sao | **◐** | Schema có; chất + phủ chưa đồng đều |
| sao_noi_dung fv=1 | **◐** | 2030 đã duyệt; def 476 · cung 910 — còn gap theo sao×cung |
| atom_commentaries | **○/◐** | 7712 tồn tại; council/phê mệnh **chưa nuôi đủ** (gap cũ kế hoạch Phật) |
| Safety + disclaimer | **◐** | Có module; audit LLM định kỳ còn thiếu |

### 5.7 So với gap analysis 2026-06-10

| Khi đó | Nay (2026-07) |
|---|---|
| Paradigm engine “chưa có” | **Đã code** nhan_cung, bậc tuổi, ba vòng, tam hợp lộc, to_hop — wire một phần vào 3-layer |
| Bát Pháp / Thập Dụ “cần build” | **Đã code** nhưng **orphan UI** |
| 3-layer goal | **Có** API + panel; chưa thay mặc định đọc lá |
| life_arc | **Đã ship** trong VanHan |
| Founder verify atoms | **Tiến bộ** trên `sao_noi_dung`; atomic_questions verify vẫn là trận lớn |

---

## 6. Gợi ý phát triển (theo lỗ method — không UX gom phái)

### Hạng A — Khép method đã chốt mà chưa lên mặt CƠ

1. **Mặc định sau cast Bắc phái:** thẻ CƠ = Mệnh–Thân–Cục–chủ + **3 vòng** + **bậc tuổi** + cảnh báo Nhân Cung (nếu có) — trước LLM.  
2. **Nút / mode “Đọc tiến trình đất→hạt”** gọi `doc_la_so_tien_trinh`, hiện gaps trung thực.  
3. **Highlight tam phương tứ chính** trên lưới (Τ).  
4. **Wire Bát Pháp + Thập Dụ** vào đọc Mệnh (Κ) — module đã có, thiếu sản phẩm hóa.

### Hạng B — BIẾN đủ cổ pháp Q3

5. Feature **ĐV ∩ Tiểu hạn chồng hung** (chỉ khi đồng kích).  
6. Đẩu Quân tháng: cát tinh đồng hành + đọc Q3 (không cát/hung tuyệt).  
7. Chuẩn hóa copy **mùa khí** trên life_arc (đã có xương).

### Hạng C — Nguồn nuôi luận

8. Lấp gap `sao_noi_dung` per-cung theo tiến trình 4 cung đất + Mệnh trước.  
9. Nối `atom_commentaries` + filter fv vào phê mệnh / 3-layer / Hermes.  
10. Phủ Ngũ Uẩn 8 lớp: ưu tiên 14 chính tinh mẫu duyệt từng sao (lộ trình thủ thư).

### Hạng D — Đủ catalog cổ còn mỏng

11. Map **biến cách** Q1 (106) có chọn lọc vào engine.  
12. Kỳ cách / phá cách có điều kiện trên cách cục panel.  
13. Ngũ Cục chất người — chỉ khi có nguồn; không placeholder giả.  
14. Hợp đĩa TV = cửa sổ riêng (khi Anh mở bàn quan hệ liên cửa).

### Hạng E — Không làm

- Gộp CDK + Bắc + Đằng Sơn thành một funnel.  
- Surface predict G.  
- Coi “thêm panel” = đủ thông tin (thiếu method stack vẫn nông).

---

## 7. Kết luận nghiên cứu (v2)

1. **Tử Vi có thể mang lại** không chỉ “lá số + vận hạn”, mà một **máy thông tin 7 loại** (Σ Τ Κ Δ Χ Ψ Ω), sinh theo **method stack** (đất→hạt · 4 lớp · lồng thời gian · đa phái).  
2. **Sản phẩm YI đã rất dày Σ và xương Χ**; đã có Ψ/Ω một phần (Ngũ Uẩn, 3-layer, cross-school, life_arc, Phu Thê).  
3. **Lỗ sâu nhất không phải thiếu sao**, mà:  
   - method đọc **chưa là mặc định user-facing** (tiến trình, Bát Pháp, Thập Dụ, ba vòng đầu buổi);  
   - **nguồn per-cung / commentaries** chưa đủ nuôi lớp 1–2–3;  
   - **Q3 chồng hạn / Đẩu Quân** chưa đủ sản phẩm;  
   - **orphan paradigm modules** (bat_phap, thap_du).  
4. Phát triển tiếp nên **khép method trong cửa Bắc phái** (và từng cửa phái khác tương tự), không nghiên cứu nông kiểu liệt kê cung.

---

### Phụ lục — Chỉ số kho (snapshot 2026-07-27)

| Kho | Số |
|---|---|
| `sao_noi_dung` | 2603 (fv=1: 2030; def: 476; cung: 910) |
| `atomic_questions` | 67497 |
| `atom_commentaries` | 7712 |
| `cach_cuc_index` entries | ~1193 |
| Ngũ Uẩn records | 95 (chính tinh + phụ + cung + nguyên lý…) |

---

*Hết v2. Nếu Anh muốn vòng 3: chọn **một** cung (vd Phúc Đức) hoặc **một** tầng BIẾN (Đẩu Quân tháng) — em đối chiếu sát từng câu Q3 × engine × UI.*
