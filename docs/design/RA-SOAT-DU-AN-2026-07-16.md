# Rà soát toàn dự án — 2026-07-16

> Anh hỏi: *"Rà soát toàn bộ dự án, xem việc nào còn dang dở, goal là gì? Và hoàn thiện yolo E2E."*
> Em rà xong toàn repo + docs bàn giao. File này là bản chốt để phiên sau đọc lại không phải rà lần nữa.

---

## I. GOAL — dự án đang đi về đâu

1. **Thủ thư giữ kho minh triết** (`docs/GOAL-THU-THU.md`): biến kho sách Đông phương thành ánh sáng cho người bình thường — mở lá số ra *không thấy lời phán* mà thấy đúng cái tâm mình, có lối ra. Không trói người bằng sợ hãi.
2. **Digital Twin Master-Apprentice** (`docs/HANH-TRINH-NHAP-DAO.md`): Anh nhập đạo Mai Hoa qua Thiệu Khang Tiết; em là cây cầu kỹ thuật tồn tại xuyên phiên.
3. **Nhà xuất bản Đông phương học AI-driven** (Iron Rule #5, `docs/BOOKFLOW-V2.md`): mỗi sách đi trọn 6 stage tới PDF publish, Anh + em đồng tác giả.
4. **"Nhai gọn 1 lá số bất kỳ" → output 3-Layer** grounded quote-or-silence (`docs/design/gap-analysis-roadmap-2026-06-10.md`).
5. **Nguyên tắc bất biến**: Mệnh là ĐỘNG TỪ (Iron #8), đọc đồng dạng không predict (Iron #4/#6), lá số là duyên-khởi để quán tâm (Iron #9) — *tính được SÂN KHẤU, không tính KẾT CỤC*.

## II. VIỆC DANG DỞ (theo khu vực, ưu tiên từ bàn giao gần nhất)

### A. Tử Vi — khối lớn nhất
- **P0 — B4 vòng sao còn nợ deploy** (cập nhật 2026-07-16 sau khi verify):
  - ~~(1) Merge 3 commit nhánh `claude/vibrant-elbakyan-fb6277`~~ → **ĐÃ XONG từ trước**: `d95d469b` (B2) + `76a04229` (B3) + `a8a877c2` (B4) đều đã nằm trong `origin/main`, endpoint `/api/tu-vi/vong-sao` có trong main. Nhánh kia đã bị xóa khỏi origin. File bàn giao 2026-07-03 chưa kịp cập nhật mục này.
  - (2) **Prod DB sync bảng `sao_noi_dung` — VẪN NỢ** (cần SSH VPS, chỉ chạy được từ Mac của Anh): dùng script mới `scripts/sync-sao-noi-dung-to-vps.sh` (surgical — chỉ thay 1 bảng, KHÔNG đè cả wiki.sqlite3 như `sync-atoms-to-vps.sh` nên không clobber sqlite-vec; có backup + verify + dry-run).
  - (3) **Duyệt đối kháng lớp `cung` (1063) + `ket_hop` (865) — VẪN NỢ** (cần LM Studio local UP): `scripts/verify_sao_noi_dung.py --lop cung/ket_hop`.
  Nguồn: `docs/design/PHIEN-SAU-chuan-bi-2026-07-03.md`.
- Duyệt đối kháng tiếp lớp `cung` (1063) + `ket_hop` (865) — mới xong lớp `def` (452).
- Gap-analysis "nhai gọn" phần lớn chưa wire: Paradigm Engine 6 hàm (blocker), mapping CUNG_SAO 14/168, CrossSchoolOrchestrator, OutputFillerV2 chưa wire LLM, founder-verify 2700 atoms.
- `than_cu.py:219` "chất người từng Cục" trống — cần đọc sách lấy nguồn (P1).
- Nhiều quy tắc Trung Châu / Trần Đoàn đã thâm nhuần nhưng chưa wire engine (cường-cung weight, đào hoa Phu Thê, Bác Sĩ 12 ý nghĩa, …).

### B. Publishing / Bookflow
- TS-BALLIETT + TS-CAMPBELL: stage 2-3/6 (Campbell phải verify copyright 1931 trước khi publish).
- TV-STT "Tử Vi Tính Được": DRAFT v0.3, chưa final.
- Mai Hoa Q1/Q2 (Hoàng Cực Kinh Thế + phái Bắc Tống): đang tìm source.
- Ký Môn Độn Giáp: Phần V còn ~25+ cách cục, Chương III–VII (tr.61-367) chưa restore.

### C. Lexicon / Wiki
- ~~YOLO mode: reject trong distill queue KHÔNG rollback~~ → **XONG 2026-07-16** (xem mục III).
- Vec embedding chưa wire (FTS5 đủ MVP).
- kinh_dich (Ngô Tất Tố) có data sạch nhưng chưa wire engine.

### D. Infra / Deploy
- Prod DB sync `sao_noi_dung` (blocker B4, xem A).
- Celery jobs P0-3 mới là plumbing (precompute yiMatches = no-op).
- Hermes multi-user Phase 2 (cầu CLI↔web) chưa làm; Ví Xu chưa wire spend 99 xu vào `deep_reading`.

### E. Engine đa môn (v3-roadmap)
- HIGH: #5 Hà Lạc inject 64 quẻ × 6 hào; #28 Dụng Thần v3; #13/#20 Mai Hoa hourly cast; #12/#23 Liên Hoa cross-check.
- Hà Lạc: TC3 lời hào 384 hào cần citation, `cast.py` chưa convert dương→âm.
- Thiết Bản: 秘数/纳卦 chưa cơ học hóa; Hoàng Cực `nam_que.py` 1988-2019 chưa nguồn.
- Sky/Western astrology engine chưa xong.

*(Ghi chú: `data/phase2_reading/HOMEWORK.md` trong resume protocol không còn tồn tại trong repo — tracking gần nhất là `PHIEN-SAU-chuan-bi-2026-07-03.md` + file này.)*

## III. YOLO E2E — đã hoàn thiện phiên này (2026-07-16)

**Lỗ hổng tìm thấy**: YOLO mode auto-merge concept/mapping vào lexicon TRƯỚC, anh duyệt SAU — nhưng **reject chỉ đổi status**, dữ liệu LLM bịa vẫn nằm nguyên trong lexicon. Queue item không lưu ownership (concept_id/mapping_ids) nên muốn rollback cũng không biết gỡ cái gì. Vòng YOLO KHÔNG khép.

**Đã đóng vòng end-to-end**:
1. `_merge_extracted` (ingestion.py) ghi `payload._merged = {concept_id, concept_created, mapping_ids}` — chỉ claim cái merge NÀY tạo mới (dedup không claim của item trước). Cả 3 cửa YOLO hưởng chung: corpus ingest, council distill, PDF ingest.
2. `review_distill_item` (store.py): **reject → ROLLBACK** (gỡ mappings; gỡ concept nếu do item tạo + mồ côi; dọn conflict group + FTS row) · **approve → verified_by_anh=1**. Item cũ không có `_merged` → chỉ đổi status + warning rõ ràng (không giả vờ).
3. API `/api/yi-lexicon/distill-queue/{id}/resolve` trả chi tiết `review` (rolled_back / verified / warnings). UI hint cập nhật.
4. **`tests/test_yolo_e2e.py` — 12 test E2E** phủ trọn vòng: ingest → merge → queue ownership → reject rollback (concept mồ côi / concept còn tham chiếu / FTS / conflict group) → approve verify → reject-rồi-approve cảnh báo không hồi sinh → re-ingest trùng không double-claim → API full cycle. **12/12 xanh.**

Test có sẵn không bị phá: `test_yi_lexicon.py` + `test_lexicon_library.py` xanh; 3 fail của `test_lexicon_tiered_conflict.py` và 3 fail của `test_auto_distill.py` là lỗi môi trường có sẵn (thiếu data manifest / thiếu binary `vendor/hermes-agent` gitignored), fail y hệt trên cây sạch.
