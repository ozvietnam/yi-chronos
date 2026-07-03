# CHUẨN BỊ PHIÊN SAU — 2026-07-03 (đóng gói cuối phiên dài)

> Phiên 2026-07-03 rất dài (~25 deploy). Khởi từ ảnh giáo cụ **"GIẢI MÃ ĐỊA BÀN"** Anh gửi →
> mở rộng thành cả một đợt hoàn thiện Tử Vi + tái kiến trúc giao diện. File này ghi **việc ĐÃ
> xong (live)** + **việc CHƯA làm (yêu cầu phiên sau)** + **quyết định còn treo**.

---

## ✅ ĐÃ XONG & LIVE (kinhdich.online) trong phiên này

**A. Ví xu + đồng bộ AppChat**
1. **UI Ví Xu cho user** (`WalletModal.vue` + chip 🪙 UserBadge) — số dư, điểm danh (ẩn khi hết cửa sổ welcome qua `xu_wallet.daily_bonus_peek`), nhập mã, lịch sử.
2. **`POST /api/sync/wallet/deduct`** — trừ xu cho PRVchat lì xì (hong bao). Idempotent theo `ref` (thêm cờ `spend(idempotent=)`). Spec ở `~/Desktop/appchat/docs/superpowers/plans/2026-07-02-yi-hongbao-api-guide.md`. 24 test.

**B. Địa bàn Tử Vi — ĐỦ 9/9 thành phần** (giáo cụ GIẢI MÃ ĐỊA BÀN)
3. Độ sáng chính tinh (M/V/Đ/B/L/H) · can cung (Ngũ Hổ Độn) · vòng Trường Sinh (⚠️ 水土同宫: Thổ khởi THÂN, khác Bát Tự) · năm tiểu vận · nguyệt vận. Tất cả xương tất định, verify khớp lá số founder + 2 nhãn ảnh. `engine/tu_vi/an_sao.py`.

**C. Luận giải grounded (Anh phát hiện "bỏ sót dữ kiện lớn" — hút mà chưa nối)**
4. **Thân cư** (đóng cung nào → trọng tâm/hậu vận) — `engine/tu_vi/than_cu.py`, 92 atom verified nối vào lá số, quote-or-silence (lọc "Mẫu SAI", gộp trùng, khớp question_text).
5. **Cục** = ngũ hành nền (neo `ngu_hanh_nen`) + **Mệnh→Thân** trục nửa-đời (atom Nghiệm Lý Toàn Thư). Khối "🪞 Nền mệnh" trên lá số.

**D. Tái kiến trúc giao diện Tử Vi ("lá số = kết quả · thư viện = kiến thức")**
6. **Redesign 2-tier**: địa bàn 2 chế độ **Cơ bản/Nâng cao** (`chartMode`) + cổng **"🔎 Đọc sâu"** (`showDeepRead`) gom 5 khối nặng (phê mệnh/12-cung/case/3-tầng).
7. **Tách lá số ↔ thư viện**: gỡ tường trích sách Q1/Q3 per-cung · lightbox ảnh sao thêm nút "→ Thư viện" · dời ChinhTinhGallery sang tab Thư viện · gỡ star_details/context-art/nút Phú khỏi lá số · **hợp nhất 1 kho sao** (bỏ drawer nhúng, `moThuVienSao` emit `open-library-star` → App chuyển tab + openToStar).
8. **Thư viện chia 2 sub-tab song song**: 🔯 Tử Vi ⟷ 📚 Sách phục chế (`libSubTab`, App.vue).

Chi tiết: memory `tu_vi_dia_ban_hien_thi_day_du`, `tu_vi_than_cu_surfacing`, `appchat_yi_xu_bridge`, `tu_vi_thu_vien_mo_rong`.

---

## ⬜ CHƯA LÀM → YÊU CẦU PHIÊN SAU (ưu tiên P0→P2)

### ✅ P0 ĐÃ XONG (phiên nối 2026-07-03, sau bàn giao) — B2 + B3 + B4
- **B2 Ngũ Cục** (commit d95d469b): `than_cu.list_cuc` → `/api/tu-vi/cuc-list` → `NguCucLibraryPanel.vue`. 5 cục hành nền + vai trò cơ học; "chất người" để trống (chưa nguồn).
- **B3 Thân-Mệnh** (76a04229): `than_cu.list_than_menh` → `/api/tu-vi/than-menh` → `ThanMenhLibraryPanel.vue`. Đồng cung (nguyên tắc Vũ Tài Lục + 8 luận Nghiệm Lý) · khác cung (6 Thân cư). ⚠️ thực tế **22 atom** (không phải 28).
- **B4 vòng sao** (a8a877c2): **Anh chốt "em DUYỆT ĐỐI KHÁNG trước".** Pipeline `scripts/verify_sao_noi_dung.py` (provenance quote-trong-sách + LLM qwen3-30b local bắt bịa-dịch) duyệt lớp def: **452 duyệt · 33 loại · 190 treo · 103/104 sao**. `vong_sao.list_vong_sao` → `/api/tu-vi/vong-sao` → `VongSaoLibraryPanel.vue` (89 phụ/vòng sao, chỉ fv=1, kèm nguồn + quote gốc mở đối chiếu).

**⬜ CÒN NỢ (phiên sau):** (1) **Deploy** — 3 commit ở nhánh `claude/vibrant-elbakyan-fb6277`, CHƯA merge main/push. (2) **Prod DB sync** — founder_verified ghi wiki.sqlite3 LOCAL; prod chưa có → B4 prod RỖNG tới khi surgical-sync bảng `sao_noi_dung` (SSH `root@187.127.98.35`, backup + tránh clobber sqlite-vec, memory `live_deploy_infra`). Backup local `/tmp/wiki_backup_before_b4.sqlite3`. (3) **Duyệt tiếp lớp `cung` (1063) + `ket_hop` (865)** (mới xong def): `verify_sao_noi_dung.py --lop cung/ket_hop --cache <json>` (LM Studio phải UP).

---

### (tham chiếu gốc) P0 — Mở rộng Thư viện Tử Vi
Anh giao "trong thư viện > tử vi > bổ sung **Mệnh / Cục / vòng sao đầy đủ**". Đã xong 2 sub-tab (B1). Còn:

- **[B2] Cục (5 cục)** — thêm section/tier "Cục" vào `ChinhTinhLibraryPanel.vue` (tab Tử Vi). Data grounded SẴN: `engine/tu_vi/than_cu.doc_cuc` (5 item = ngũ hành nền `HANH_VAN_DONG`, nguồn Lê Văn Sửu "khớp cổ thư"). Nên thêm endpoint nhỏ `/api/tu-vi/cuc-list` (5 item + nature + source) rồi panel fetch.
- **[B3] Thân-Mệnh** — ⚠️ **"Mệnh" ở đây = quan hệ THÂN-MỆNH, KHÔNG phải tên 12 cung** (Anh chỉnh rõ). Gồm:
  - *Đồng cung* = **28 atom verified** ("Thân Mệnh đồng cung: tốt càng tốt, xấu càng xấu" + theo tuổi/vị trí; nguồn Nghiệm Lý Toàn Thư Thiên Lương / Trung Châu / Hàm Số). Build retrieval `doc_than_menh_dong_cung()` (query `atomic_questions` LIKE 'Thân Mệnh đồng cung', founder_verified=1) — mẫu theo `than_cu._retrieve`.
  - *Khác cung* = **92 atom Thân cư ĐÃ wire** (tái dùng `than_cu`).
  - Anh chốt: **dùng đồ ĐÃ duyệt, KHÔNG atomize sâu thêm** (còn ~100 passage đồng-cung Trung Châu/Hàm Số/Vũ Tài Lục để sau).
- **[B4] Vòng sao đầy đủ** — `sao_noi_dung` (104 sao, lớp `def` 675 dòng, có `nguon_book`) phủ Bác Sĩ/Kình Dương/Đà La/Hỏa-Linh Tinh/Địa Không-Kiếp/Thái Tuế/Thiên Mã/Lộc Tồn… **NHƯNG `founder_verified=0`** (chưa Anh duyệt). ⚠️ **QUYẾT ĐỊNH TREO** (hỏi Anh khi làm): hiện luôn + nhãn nguồn + cờ "chờ duyệt" **HAY** chỉ hiện cái đã duyệt (Anh duyệt qua bàn Duyệt Atoms trước).

### P1 — Nội dung sâu hơn (cần đọc sách, đúng bookflow)
- **Ý nghĩa "chất người" từng Cục** (Thủy nhị/Thổ ngũ… là kiểu người thế nào) — hiện MỚI có tầng ngũ-hành-nền; muốn sâu cần đọc/atomize nguồn cổ (Phú Thái Vi Q1/Q2 có sẵn trong wiki). = 1 phiên đọc sách.
- **Rà "hút mà chưa nối" ở môn khác**: Bát Tự / Mai Hoa / Lục Hào… có thể cũng đang lẫn kiến-thức-chung với kết-quả-lá-số như Tử Vi lúc đầu → soi + tách tương tự.

### P2 — Tinh chỉnh giao diện (nếu Anh muốn)
- **Đọc sâu tách hẳn route/wiki** thay vì collapse cùng trang (Anh từng cân nhắc, để sau).
- Thẻ tóm tắt Nền mệnh → dòng-dẫn "đọc sâu →" link thẳng wiki (thay vì hiện cả đoạn).
- **12 Cung (tên cung: Mệnh/Phu Thê/Tài Bạch…)** — ý nghĩa từng cung chức: hiện CHƯA có nguồn cấu trúc chuẩn (chỉ mô tả rời trong `analyzer.py`). Nếu Anh muốn thêm vào thư viện → cần atomize nguồn cung trước. (Khác với B3 Thân-Mệnh.)

---

## ⚠️ LƯU Ý PHIÊN SAU
- **Kỷ luật quote-or-silence**: mọi nghĩa hiện ra phải có nguồn đích danh; không có nguồn → để trống/nhãn "chưa có nguồn", KHÔNG bịa. (Đó là lý do B4 vòng-sao đang treo — content chưa duyệt.)
- **Bẫy test render**: fetch-override trong eval phải LƯU `orig=window.fetch` TRƯỚC khi override (đừng `__of=fetch` SAU → đệ quy vô hạn, oracle-cards không load).
- **Preview local cuối phiên chập chờn** (Vite 5174 → 000) — nếu tái diễn, restart sạch uvicorn+Vite hoặc verify qua engine-data + build + prod.
- **File chính đụng tới**: `client/webapp/src/components/TuViLaSoPanel.vue` (3700 dòng), `ChinhTinhLibraryPanel.vue`, `client/webapp/src/App.vue` (tab library ~930), `engine/tu_vi/than_cu.py`, `engine/tu_vi/an_sao.py`, `api/main.py` (endpoint /api/tu-vi/*).

---
*Ghi bởi Claude cuối phiên 2026-07-03. Phiên sau mở đầu: đọc file này + memory `tu_vi_thu_vien_mo_rong` → làm tiếp B2 ngay.*
