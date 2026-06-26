# 🪷 YI-Chronos — Kế hoạch chuyên gia: nền Phật pháp & định hướng sản phẩm với xã hội

> Anh giao 2026-06-26: "bật nghiên cứu sâu, lập kế hoạch chi tiết như chuyên gia 1 vòng nữa trước khi
> giao toàn quyền. Lưu ý hạ tầng: wiki, Obsidian, dịch sách, sinh atom, luận giải V3. Nghiên cứu di huấn
> Đức Phật — người duy nhất thấu thị toàn vũ trụ."
> Đây là sản phẩm của 10-agent deep research (di huấn Phật grounded kinh tạng + audit hạ tầng + phản biện PASS).
> Đồng hành: [[GOAL-THU-THU]] · [[lo-trinh-nghien-cuu-tu-vi-ngu-uan]].

## 1. TẦM NHÌN — YI là gì với xã hội
**YI không phải thầy bói. YI là một CÁI GƯƠNG QUÁN CHIẾU TIẾN TRÌNH TÂM** — mượn lá số (Tử Vi/Bát Tự/quẻ) làm phương tiện để người dùng *thấy rõ cấu trúc tâm mình và bớt khổ*, không phải để biết trước số phận.
**Thành công của một buổi đọc YI = người đi ra BỚT DÍNH MẮC, không phải "đoán trúng".**

Khác biệt cạnh tranh (sạch về đạo đức + bán được): giữa thị trường tâm linh đầy dọa-giải-hạn, YI trung thực về chỗ mình đứng — công cụ tự quan sát thế tục, đặt Phật pháp **cao hơn và độc lập**, chỉ "đứng dưới mượn ánh sáng".

## 2. NỀN DI HUẤN PHẬT (grounded kinh tạng — phân tầng canonical)
- **Tứ Diệu Đế = ngữ pháp soi tâm 4 bước** (SN 56.11): Khổ (chẩn — gọi tên cái vướng) → Tập (nhân — gốc ở *ái/chấp*, không ở ngoại cảnh; 3 ái: dục/hữu/phi-hữu) → Diệt (không cố định, có lối ra) → Đạo (phác đồ hành động). Mỗi đế là một ĐỘNG TỪ (liễu tri/đoạn/chứng/tu) → bằng chứng kinh điển cho Iron #8 "mệnh là động từ".
- **Ngũ Uẩn = bản đồ tiến trình tâm** (SN 22.79): **Sắc → Thọ → Tưởng → Hành → Thức** (ĐỦ 5; *Xúc/phassa KHÔNG phải uẩn — là chi Duyên Khởi/tâm sở biến hành, là CỬA VÀO tiến trình, không phải uẩn thứ 6*).
- **Mắt xích Thọ→Ái = "khe tỉnh thức"** (SN 12.2): chỗ DUY NHẤT chánh niệm chen vào được trong một sát-na (A-tỳ-đàm: sát-na *votthapana* trước khi *javana* tạo nghiệp). → chỗ "bớt khổ" cụ thể gắn vào mỗi lá số.
- **Vô Ngã + Duyên Khởi = lý do triết học SÂU NHẤT để không predict**: không có chủ thể tĩnh nào để dự đoán, chỉ có tiến trình duyên-khởi đang trôi. Củng cố Iron #4/#6.
- **Lằn ranh đạo đức** (Brahmajāla DN 1 — Phật xếp bói toán vào *tà mạng*): YI KHÔNG đoán giàu-nghèo/thắng-thua/cờ bạc (tiền lệ: Anh đã từ chối quẻ XSMB 18/5); chỉ mượn khung Duyên Khởi soi tâm.
- **Kỷ luật nguồn:** canonical (SN/DN/Dhp) > học giả (Bodhi/Gethin/Harvey/Nhất Hạnh) > diễn giải. Khung "y học/Đại Y Vương" = **diễn giải hậu kỳ (Kern 1882), KHÔNG trích như lời Phật.**

## 3. KIẾN TRÚC (bám hạ tầng THẬT — số liệu đã verify)
```
Obsidian vault "thư viện sách/" (2.1GB, 101 PDF, 0 note, graph RỖNG — chỉ để lật trang)
  ↓ OCR/restore
data/restored_books/<slug>/content.md (42-49 sách)
  ↓ atomization
wiki.sqlite3 (96MB): atomic_questions 17.793 · atom_commentaries 6.458 (V3) · tabular_verses 18.767 · concept_index 3.610
  ⊗ dataset Ngũ Uẩn (tuvibonba_ngu_uan.json, 81 rec) — LĂNG KÍNH chân dung
  ↓ engine/tu_vi/ngu_uan.py → chân dung Ngũ Uẩn V3 (8 lớp)
  ↓ engine + council/sage + cross_school → sản phẩm
  ↓ UI (TuViLaSoPanel ☸ Quán chiếu, ChinhTinhLibrary, ChanDung, council)
```
**3 đứt gãy lõi:** (a) dataset Ngũ Uẩn 81 rec **CHƯA giao** với 17.793 atoms; (b) `atom_commentaries` (6.458 luận giải sâu nhất) gần như **CHẾT** — council `expert_context.py` chỉ lấy `source_quote` thô qua FTS, không đọc commentaries; (c) Obsidian vault **bỏ phí** (0 note/backlink).

## 4. KẾ HOẠCH 6 TẦNG
Theo [[lo-trinh-nghien-cuu-tu-vi-ngu-uan]]: Tầng 0 Nền triết → **1 (14 chính tinh đủ 8 lớp, KỸ TRƯỚC)** → 2 (12 cung) → 3 (phụ tinh/Tứ Hóa) → 4 (miếu vượng hãm — tái dùng `mieu_ham_levels` có sẵn) → 5 (combo SUY RA, không tra bảng chết) → 6 (thời gian: đại vận→lưu niên→tháng→ngày, sau cùng).

Cấu trúc chân dung **v3 (8 lớp)**: ① Âm Dương/Ngũ Hành (căn cơ — vì sao tạo hóa sinh ra tâm đó) → ② Gốc Tham → ③ Ngũ Uẩn (5 uẩn, tiến trình) → ④ Khí vượng/suy → ⑤ Theo đời người (nhỏ→già) → ⑥ Khe tỉnh thức + Đường ra (Bát Chánh Đạo) → ⑦ Ví dụ sống → ⑧ Căn cứ (phân tầng nguồn). *Tử Vi đã dựng mẫu đạt.*

### Schema/Engine/UI cần đổi
- **B1** mở schema dataset: thêm `am_duong_ngu_hanh / goc_tham / khi_vuong_suy / theo_doi_nguoi / khe_tinh_thuc / duong_ra / can_cu{nguon_noi,thu_thu_suy}` (giữ đúng 5 uẩn — KHÔNG thêm Xúc).
- **B2** `ngu_uan.py` xuất 8 lớp; Lớp 4 chọn động đắc/hãm theo `mieu_ham_levels`; giữ fallback None.
- **B3** UI accordion tách lớp (tóm gọn nổi + bung chi tiết — "vi diệu không loãng").
- **B4** map atom→uẩn: bảng nối `atom_ngu_uan_map` (KHÔNG sửa `atomic_questions`, tránh migration); classifier Claude sub-agent (token Max); founder duyệt qua AtomVerifyPanel.

### 5 GAP hạ tầng vá song song
1. Nối `atom_commentaries` vào council (gap lớn nhất — luận giải sâu đang chết). 2. Filter `founder_verified` (0 atom duyệt dương → đang rò nội dung chưa kiểm vào council). 3. V3 phủ lệch 36% toàn Tử Vi. 4. Kho 90% Tử Vi (phái khác mỏng). 5. `tabular_verses` + `atom_relations` tách rời/rỗng.

## 5. NHỊP ĐỀ XUẤT
**M0** (rẻ, chặn rò): đóng Tầng 0 (doc nền triết + atomize khung Phật `school=phat_hoc_nen` canonical/diễn-giải) + **vá GAP-2** (filter founder_verified) + lá chắn đạo đức Brahmajāla. → **M1**: B1-B3 cho **Tử Vi sao mẫu** đủ 8 lớp + nối commentaries→council (GAP-1) → Anh duyệt CHẤT 1 sao. → **M2+**: nhân 13 sao + 12 cung → tầng 3-6. Mỗi sao qua phản biện đối kháng (Phật-pháp + grounded) trước khi chốt. Sync prod theo cột mốc.

## 6. RỦI RO + 6 QUYẾT ĐỊNH (đề xuất của thủ thư)
R1 chiếm dụng Phật pháp (disclaimer "mượn khung" bắt buộc) · R2 sai-14-lần (duyệt mẫu trước) · R3 atom chưa duyệt rò council · R4 git/secret (git add -f, Iron #7) · R5 kho lệch Tử Vi.

| # | Câu hỏi | Đề xuất thủ thư |
|---|---|---|
| Q1 | Mở engine 8 lớp ngay hay SOUL/skill trước? | Mở engine 8 lớp (B1-B3) cho Tử Vi mẫu trước, rồi nhân |
| Q2 | Thêm **Iron Rule #9 "Lá số = hiện tượng duyên-khởi để quán tâm, không phải định mệnh để đoán"**? | NÊN — hợp nhất nền cho #4/#6/#8 |
| Q3 | Obsidian thành lớp annotation (mỗi PDF 1 note: OCR/restored/journal/insight)? | NÊN — biến vault chết thành tri thức sống, neo ngược journal |
| Q4 | Lá chắn đạo đức Brahmajāla (chặn predict giàu-nghèo/sống-chết/cờ bạc) + disclaimer mẫu? | NÊN — làm ngay ở M0 |
| Q5 | Atomize khung Phật vào wiki bây giờ? | Ở M0 (làm nền trước Tầng 1) |
| Q6 | Vá GAP hạ tầng trước hay dựng Tử Vi mẫu trước? | **M0 + GAP-2 trước** (rẻ, chặn rò) → rồi M1 chân dung mẫu |
