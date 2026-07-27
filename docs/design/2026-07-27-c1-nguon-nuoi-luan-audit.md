# C1 — Audit nguồn nuôi luận Tử Vi (tuyển Phúc→Phụ→Điền→Mệnh)

> **2026-07-27** · Track C (nguồn nuôi luận) · chốt sau inventory v2.  
> **Phạm vi:** kho DB + cách engine/UI ăn nguồn — **không** UX funnel đại chúng.  
> **Neo method:** `doc_tien_trinh.py` · Iron #3/#6/#8/#9 · quote-or-silence.  
> **Snapshot DB:** `data/yi_wiki/wiki.sqlite3` · live `doc_mot_cung` founder `1988-06-05T23:30` nam.

---

## 0. Verdict một dòng

**14 chính × 4 cung đất đã có `sao_noi_dung` fv=1.** Lỗ nuôi luận thật là: (1) **phụ/sát per-cung trống trên lá thật** → deep_cung phải im; (2) **7712 commentaries gần như toàn fv=0** → Hermes/council ăn “luận sâu” chưa founder-verify; (3) **nhiều pipeline song song** không cùng một “đường ống thức ăn”.

---

## 1. Kho nguồn — số liệu

### 1.1 `sao_noi_dung`

| Lớp / filter | Count |
|---|---|
| Tổng | 2603 |
| fv=1 | **2030** |
| fv=0 / fv=-1 | 408 / 165 |
| fv=1 · def / cung / ket_hop | 476 / 910 / 644 |

**Chuỗi đất (cung fv=1):** Phúc Đức 65 · Phụ Mẫu 65 · Điền Trạch 55 · Mệnh 129.

| Cung | 14 chính | Phụ/sát có per-cung | Avg `dich_thuan_viet` (cung) |
|---|---|---|---|
| Phúc Đức | **0 thiếu** · 27 phụ | ~163 chars | Trung Châu Q2 nặng |
| Phụ Mẫu | **0 thiếu** · 21 phụ | ~159 | Trung Châu Q2 nặng |
| Điền Trạch | **0 thiếu** · 19 phụ | ~158 | Trung Châu + Vũ Tài |
| Mệnh | **0 thiếu** · 38 phụ | ~195 | Vũ Tài + Trung Châu + Tường Tể |

**ket_hop** nhắc tên cung: Phúc 11 · Phụ 2 · Điền 4 · Mệnh 124 — lớp 3 trên chuỗi đất gần như không được nuôi từ ket_hop gắn cung.

### 1.2 `atomic_questions` + `atom_commentaries`

| Store | Count / ghi chú |
|---|---|
| atoms | 67497 · fv=1 ~62733 |
| commentaries | **7712** |
| commentary fv | **fv=1 = 0** · fv=0 = 7675 · fv=-1 = 37 |
| Field đầy | viet_thuan ~7711 · nguyen_ly 883 · vi_du 365 · cross_school 172 |

**JOIN atom+commentary trên chuỗi (fv≥0):**

| Cung | Atoms có commentary | có nguyen_ly | có vi_du | avg viet_thuan |
|---|---|---|---|---|
| Phúc Đức | 210 | 26 | 7 | ~204 |
| Phụ Mẫu | 184 | 33 | 6 | ~99 |
| Điền Trạch | 172 | 8 | 1 | ~197 |
| Mệnh | 1444 | 238 | 81 | ~133 |

→ Có **khối luận LLM-generated lớn**, nhưng **chưa có dòng commentary nào founder_verified=1**. Retriever cố ý giữ `ac.founder_verified >= 0` (vì fv=1 = rỗng) — nghĩa là council đang nuôi bằng bản chưa duyệt.

### 1.3 Ngũ Uẩn JSON

`tuvibonba_ngu_uan.json`: **95 records**. **14 chính đủ** field lõi (ngu_uan / gốc thẩm / khe / đường ra / âm dương / theo dõi / ví dụ / căn cứ). Phụ tinh v3 còn lệch — không phải lỗ chuỗi đất chính.

---

## 2. Live chart — founder trên 4 cung đất

`doc_la_so_tien_trinh('1988-06-05T23:30:00','nam')`:

| Cung | n_co_nguon | n_thieu | lop3 combo | Gaps (thiếu per-cung trừ khi ghi) |
|---|---|---|---|---|
| Phúc Đức | 14 | 2 | 0 | Tả Phù · Thiếu Âm |
| Phụ Mẫu | 15 | 5 | 0 | Lực Sĩ · Tai Sát · Ân Quang · Thai Phụ · Phượng Các |
| Điền Trạch | 6 | **6** | 0 | Quan Phù · Tiểu Hao · Chỉ Bối · Thiên Quý · **Văn Tinh thiếu def** · Văn Tinh@Điền |
| Mệnh | 14 | 4 | 0 | Thiếu Dương · Bác Sĩ · Lưu Hà · Thiên Hỉ |

**Tổng gap_list = 17** trên một lá điển hình.

### 2.1 Bản chất gap (đào DB)

| Sao gap | def fv=1 | per-cung trên chuỗi đất | Ghi chú |
|---|---|---|---|
| Văn Tinh | **0** | 0 | Thiếu cả def — ưu tiên P0 |
| Thiếu Âm / Thiếu Dương / Bác Sĩ / Lưu Hà / Thiên Hỉ / Tai Sát / Chỉ Bối / Thai Phụ | có def | **0 cung** (hoặc 0 mọi cung) | Chỉ sống ở lop1 def |
| Tả Phù | có def | 0 trên chuỗi · có 6 cung khác | Thiếu Phúc Đức |
| Quan Phù / Tiểu Hao / … | có def | lệch cung (vd Quan Phù có Mệnh, không Điền) | Lấp theo lá hay theo 12×sao |

**Điền Trạch trên lá founder mỏng nhất** (n_co=6, n_thieu=6): nhiều sao phụ không có hàng `lop='cung'`.

**lop3 = 0** trên cả 4 cung: `cach_cuc_named` có cách ở meta lá, nhưng không gắn vào reading từng cung như combo kết khối nguồn — deep_cung gần như chỉ ăn lop1+lop2.

---

## 3. Ai ăn nguồn nào? (engine diet)

```
┌─────────────────────┐     ┌──────────────────────┐
│ sao_noi_dung fv=1   │────▶│ doc_tien_trinh       │──▶ deep_cung (−10xu)
│  def + cung         │     │ van_han (sao block)  │──▶ VanHanPanel
│                     │     │ vong_sao             │
└─────────────────────┘     └──────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│ chinh_tinh schema + │────▶│ interpretation.py    │──▶ /api/tu-vi/cast
│ ngu_uan JSON        │     │ (Quán chiếu UI)       │    include_interpretation
└─────────────────────┘     └──────────────────────┘
        ▲ KHÔNG đọc sao_noi_dung / commentaries

┌─────────────────────┐     ┌──────────────────────┐
│ atoms + commentaries│────▶│ retriever (FTS)      │──▶ expert_context / Hermes
│ fv_atom≥0 ·         │     │ require_commentary   │    (council)
│ fv_comm≥0           │     │ cross_school JOIN    │──▶ 3-layer / phê mệnh
└─────────────────────┘     │ (cm không lọc fv=1)  │
                            └──────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│ Q1 Phú / Q3 lines   │────▶│ analyzer.cung_reading│──▶ analyze panel
│ concept_dict thin   │────▶│ per_cung_star_reading│──▶ sync AppChat
└─────────────────────┘     └──────────────────────┘

Orphan / mỏng UI: bat_phap · thap_du · (ba_vong/nhân_cung đã vào warnings 3-layer một phần)
```

| Route / panel | Nguồn chính | Gate fv | Commentaries? |
|---|---|---|---|
| `deep_cung` / sync deep | `doc_mot_cung` → sao_noi_dung | **fv=1 only** | Không |
| `van_han` | sao_noi_dung (+ tang riêng) | fv=1 | Không |
| cast `interpretation` | schema + ngũ uẩn + ngũ hành | n/a (code) | Không |
| Hermes `expert_context` | atoms FTS + commentaries | atom≥0 · **comm≥0** | Có (chưa verify) |
| 3-layer / narrative | `luan_sao_cung` atoms | atom≥0 | JOIN không bắt fv=1 |
| `cung_reading` analyzer | Q1/Q3 passages | riêng | Không |
| `per_cung` sync | concept_dict snippets | mỏng | Không |
| Ngũ Uẩn API / focus | JSON + optional atom_map | map≥0 | Không phải commentary |

**Hệ quả:** đường **trả phí grounded** (deep_cung) đói phụ-tinh per-cung; đường **chat/council** no đói số lượng nhưng **đói độ tin** (commentaries unverified).

---

## 4. Gap nuôi luận — xếp hạng

### P0 — Chặn deep_cung / tiến trình đất trên lá thật

1. **Văn Tinh:** thiếu def (+ cung Điền khi cần).  
2. **Per-cung phụ/sát trên chuỗi đất** cho các sao hay gặp (tối thiểu bộ gap founder + bộ phụ phổ biến: Tả Hữu, Lục Sát nhỏ, Thái Tuế hệ, bác sĩ hệ).  
3. **Điền Trạch phụ:** ưu tiên vì n_thieu/n_co xấu nhất trên lá mẫu.

### P1 — Làm commentaries thành thức ăn hợp lệ

4. **Founder-verify commentaries** trên atoms gắn chuỗi đất (bắt đầu Phúc→Phụ→Điền→Mệnh, ưu tiên có `nguyen_ly` / `vi_du`). Mục tiêu: có **fv=1 > 0** rồi siết retriever `ac.founder_verified = 1` (hiện không siết được vì =0).  
5. Sau khi có fv=1: wire bản verified vào **deep_cung block** (lop phụ / “luận sâu đã duyệt”) và/hoặc 3-layer — không dump toàn bộ fv=0.

### P2 — Dày lớp 3 + đa phái có kiểm

6. **ket_hop / cách gắn cung** trên Phúc·Phụ·Điền (hiện Mệnh lệch quá nặng).  
7. Cân book bias: chuỗi đất đang **Trung Châu-heavy** — Iron #3: bổ sung Vũ Tài / Hàm Số / luận giải chính tinh cho cùng ô sao×cung khi thiếu đối chứng.  
8. Ngũ Uẩn: giữ 14 chính; lấp phụ chỉ khi UI Quán chiếu cần.

### P3 — Không nhầm với “thiếu 14 chính”

- Ô **14 chính × 4 cung đã đầy** ở tầng cung fv=1 — **không** ưu tiên điền lại chính tinh trên chuỗi đất.  
- Không mở gitignore / sync ồ ạt wiki để “có thêm dòng”; verify tay / pipeline đối kháng như `verify_sao_noi_dung`.

---

## 5. Thứ tự làm việc đề xuất (C1 → C2)

| Bước | Việc | Done khi |
|---|---|---|
| **C1** (báo cáo này) | Audit + diet map + fill order | ✅ file này |
| **C2a** | Seed/verify `sao_noi_dung` cho gap phụ trên 4 cung (P0) | `doc_mot_cung` founder: n_thieu Điền ≤ 2; Văn Tinh có def |
| **C2b** | Queue verify commentaries chuỗi đất (P1) — tool UI hoặc batch Anh duyệt | ≥ N commentaries fv=1 trên Phúc+Mệnh |
| **C2c** | Siết retriever `require` fv_comm=1 khi N đủ; optional inject vào deep_cung | test expert_context + deep_cung |
| **C2d** | ket_hop / đa sách cân bằng (P2) | lop3 không còn luôn 0 trên lá mẫu có cách |

**Không làm trong track C:** gom panel phái · cắt cửa sổ trường · predict copy.

---

## 6. Liên kết

- Inventory method: `docs/design/2026-07-27-tu-vi-thong-tin-user-inventory-gap.md` §6 Hạng C  
- Engine: `engine/tu_vi/doc_tien_trinh.py` · `deep_cung.py` · `van_han.py` · `interpretation.py` · `cross_school.py`  
- RAG: `engine/atomization/retriever.py` · `engine/ai/expert_context.py`  
- Verify pipeline sẵn: `scripts/verify_sao_noi_dung.py` (pattern cho commentaries cần tương tự)

---

## 7. Kết luận C1

1. Chuỗi đất **không trống chính tinh** — sản phẩm grounded đã có xương sách cho 14×4.  
2. **Đói thật = phụ tinh per-cung + Văn Tinh + Điền mỏng** trên lá user.  
3. **7712 commentaries là kho chết-nửa-sống:** Hermes đã nối GAP-1 nhưng chưa có fv=1 → không nâng được thành nguồn “được phép nói chắc”.  
4. Fill order đúng: **P0 sao_noi_dung phụ trên 4 cung → P1 verify commentary → P2 ket_hop/đa phái** — không parallel “viết thêm LLM commentary” trước khi Anh duyệt.
