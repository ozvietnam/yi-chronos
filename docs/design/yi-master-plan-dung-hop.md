# 🪷 YI — MASTER PLAN hợp nhất (Nội dung ⊗ Mạng lưới ⊗ Thư viện)

> Anh chốt 2026-06-26: "thủ thư dung hợp hết ý kiến, all-in-one chỗ em. TỪNG BƯỚC đều nhớ XÂY NỀN."
> Hợp nhất: kế hoạch nền-Phật của em ([[yi-ke-hoach-nen-phat-dinh-huong]] + [[lo-trinh-nghien-cuu-tu-vi-ngu-uan]] + [[GOAL-THU-THU]])
> ⊗ báo cáo "mạng lưới tri thức" (worktree optimistic-feynman: LightRAG, ontology, 2-tốc-độ).

## ⛏️ KỶ LUẬT TRÙM: XÂY NỀN TỪNG BƯỚC
Mỗi việc, trước khi làm, truy về NỀN của nó — không nhảy ngọn:
- Nền triết = Âm Dương → Ngũ Hành → Ngũ Uẩn → Bát Chánh Đạo (Tầng 0, `tang-0-nen-triet-phat.md`) + Iron #9.
- Nền nội dung = chân dung MẪU đã duyệt (Tử Vi v3) trước khi nhân bản.
- Nền não = ontology + embeddings trước khi trích edges + đa-bước.
- Nền thư viện = lọc tinh hoa (chọn sách nền) trước khi tiêu hoá hàng loạt.
- Nền nguồn = grounded + `founder_verified` + phân tầng canonical/diễn-giải, không bịa.

## 3 TRACK XEN KẼ (một nhạc trưởng = thủ thư)

### TRACK A — NỘI DUNG / SOUL (chiều sâu, đọc đồng dạng)
Chân dung Ngũ Uẩn v3 8 lớp, giọng Phật. Lộ trình 6 tầng (`lo-trinh-nghien-cuu-tu-vi-ngu-uan.md`).
- ✅ M0 nền Phật · ✅ M1 Tử Vi mẫu 8 lớp + commentaries→council + disclaimer.
- ⏭️ **A2 nhân 13 chính tinh + 12 cung** (theo mẫu Tử Vi, mỗi sao qua phản biện Phật-pháp + grounded) → phụ tinh/Tứ Hóa → miếu vượng → combo → thời gian.

### TRACK B — MẠNG LƯỚI / NÃO (kết nối, đa-bước) — *hấp thụ từ báo cáo*
Biến kho rời thành "não": synapse + myelin + truy xuất đa-bước. **KEEP** pipeline nhà mình + SQLite; **BORROW** LightRAG (trích entity+quan hệ, truy xuất 2 tầng, cập nhật tăng dần); **DON'T** dùng open-notebook làm engine / bỏ SQLite.
- **B0 (nền) ONTOLOGY** — định nghĩa TRƯỚC: node {khái niệm, sao, cung, quẻ, hào, tác giả, phái, quy-tắc/cách-cục, công-thức} · edge {sinh, khắc, chế, hoá, thuộc-phái, an-tại-cung, biến-thành, dẫn(cites), mâu-thuẫn(contradicts/variant-of)}. Mâu thuẫn đa phái = cạnh tường minh (Iron #3), KHÔNG gộp lén.
- **B1 embeddings** `atom_vec` (17.793) → council tìm theo NGHĨA. *(chờ embedder LM Studio :1234; hoặc dùng cloud embedder.)*
- **B2 trích `atom_relations` edges** (Lane A, trên atoms CÓ SẴN, dẫn nguồn, `founder_verified=0` chờ duyệt).
- **B3 multi-step retriever** nối Council (FTS + vector + edges, lan 2-3 bước). *(M1 đã làm gap commentaries→council.)*

### TRACK C — THƯ VIỆN TINH HOA (lọc + mở rộng) — *chạy SONG SONG nhiều agent, an toàn*
Việc nghiên cứu (đọc catalog + search) → báo cáo/danh sách, KHÔNG sửa code chung → parallel-safe trong tay thủ thư.
- **C1 lọc tinh hoa**: xếp hạng 66 sách catalog + 45 restored theo tier S/A/B/C + độ cốt-lõi-với-hệ → chọn sách NỀN ưu tiên tiêu hoá (vd Mai Hoa q1q2 — phái gốc, mới passages-only).
- **C2 mở rộng sách tương tự**: research/tìm sách canonical cùng phái còn thiếu (Tử Vi 中州派 full · Bát Tự 子平真诠/滴天髓 · Mai Hoa · Phật Nikāya bản Việt) + khả năng tải.
- **C3 (2 tốc độ)**: Lane A máy auto-digest sách thường (`founder_verified=0`) · Lane B Anh+em đọc sâu sách tổ sư (`doc-sau-20-trang`, `founder_verified=1` đè máy).

## NHỊP (xây nền → ngọn, báo Anh mỗi mốc)
1. **Nền song song (giờ)**: C1+C2 (lọc/mở rộng — parallel research) · A2 nhân chân dung (mẫu đã có) · B0 ontology (design).
2. **Khi embedder bật**: B1 embeddings → B2 edges → B3 đa-bước.
3. **Sync prod wiki** (khung Phật + commentaries enrich + Bát Tự passages) để council enrichment lên live — surgical, có backup ([[live_deploy_infra]]).
4. Lane A auto-digest 45 sách thô (sau khi C1 chọn nền + B2 pipeline chạy).

## CỬA: prod-sync wiki + embedder
- Council enrichment + khung Phật chỉ LÊN LIVE sau khi sync wiki.sqlite3 lên prod (data/ không theo CI).
- B1 cần embedder (LM Studio :1234 hoặc cloud nomic).
