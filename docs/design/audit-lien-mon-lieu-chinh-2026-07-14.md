# Audit liêm chính liên môn — 2026-07-14

> Nối tiếp việc duyệt đối kháng Tử Vi (sao_noi_dung). Anh giao "audit các môn khác":
> kiểm xem Bát Tự / Mai Hoa / Hoàng Cực / Lục Hào… có dính cùng lỗi **content máy-sinh
> gắn founder_verified=1 hàng loạt → lọt bịa vào council** như Tử Vi lúc đầu không.

## Phương pháp
1. Phân bố `atomic_questions.founder_verified` theo `extracted_by` (pipeline tạo).
2. Gán atom → môn qua `chunks_v2.book_corpus_id`.
3. Provenance: `source_quote` có nằm trong chunk gốc không (mẫu 60/môn).
4. LLM đối kháng (qwen3-30b local): atom có bịa claim ngoài `source_quote` không (mẫu 20/môn).

## Phát hiện

### 1. Các kho content có `founder_verified`
| Bảng | Phân bố fv | Ghi chú |
|---|---|---|
| `atomic_questions` | -1: 2883 · 0: 1896 · **1: 62718** | Kho RAG chính (council/sage). 62.7K máy-duyệt. |
| `sao_noi_dung` | -1: 165 · 0: 602 · 1: 1836 | Tử Vi — ĐÃ duyệt đối kháng (phiên trước). |
| `atom_commentaries` | -1: 37 · **0: 7675** | Phần lớn TREO (không bulk-approve) — an toàn. |
| `atom_ngu_uan_map` | -1: 63 · 1: 542 | Ngũ Uẩn 14 sao Tử Vi. |
| `atom_relations` | 0: 107K | Cạnh mạng, không phải content. |

**→ KHÔNG có bảng per-concept kiểu `sao_noi_dung` nào khác cho môn khác.** Kho content
duy nhất dùng chung là `atomic_questions`.

### 2. `atomic_questions` máy-duyệt theo môn (fv=1)
Tử Vi 33.190 · **Bát Tự 11.724 · Hoàng Cực 7.484 · Mai Hoa 4.658** · ÂDNH 254 · Kinh Dịch 74.

### 3. Provenance `source_quote` trong chunk gốc (mẫu)
| Môn | Grounded |
|---|---|
| Hoàng Cực | 100% |
| Tử Vi | 98% |
| Bát Tự | 95% |
| Mai Hoa | 62% ⚠️ |

Mai Hoa 62% = **CẢNH BÁO GIẢ**: các source_quote đó là *paraphrase có cấu trúc* của đúng
nội dung chunk (vd `"CẦU TÀI (tr.158): Dụng khắc Thể → vô tài"` khớp chunk "gán nghĩa
Thể-Dụng theo việc hỏi"), KHÔNG bịa — chỉ khác cách trích (structured thay vì verbatim).

### 4. LLM đối kháng — atom có bám nguồn? (mẫu 20/môn)
| Môn | ok+drift | fabricated |
|---|---|---|
| Bát Tự | 20/20 | 0 |
| Mai Hoa | 20/20 | 0 |
| Hoàng Cực | 18/20 | 2 (không tái lập ở lần chạy 2 → judge noise, không hệ thống) |

## KẾT LUẬN

**Các môn khác KHÔNG dính lỗi "bịa lọt council" như Tử Vi.** Lý do bản chất: lỗi
`sao_noi_dung` nằm ở **lớp DỊCH độc lập** (`dich_thuan_viet` tô vẽ vượt `quote_goc`) — một
tầng biên tập LLM sinh nghĩa. Còn `atomic_questions` các môn là atom **TRÍCH TỪ chunk sách
thật** (`source_quote` từ chunk, grounded 95-100%) — không có tầng dịch bịa. Book-atomization
đáng tin theo thiết kế.

→ **Không cần chạy lại pipeline duyệt đối kháng cho Bát Tự/Mai Hoa/Hoàng Cực.** Việc đó chỉ
đúng cho kho có lớp-dịch/biên-tập (đã làm cho sao_noi_dung).

## GAP THẬT của môn khác (khác với Tử Vi)
Không phải *bịa*, mà là:
1. **Kho MỎNG** (memory `council_rag_grounding`): corpus ~90% Tử Vi → Mai Hoa/Bát Tự kho
   sage mỏng, cần atomize thêm sách (không phải duyệt lại).
2. **"Hút mà chưa nối"** (như Tử Vi Thân cư): có thể tri-thức-verified của Bát Tự/Mai Hoa
   chưa được engine/panel deterministic surface — CẦN audit engine+UI từng môn (phiên sau,
   surface lớn hơn, nên tách riêng).

## Việc đã làm phiên này (liêm chính, đã LIVE)
- Tử Vi sao_noi_dung: duyệt đối kháng 3 lớp (452+785+599 duyệt / 165 loại / 602 treo).
- Đóng 3 tầng tiêu thụ: Thư viện (vong_sao) · route trả phí (deep_cung) · **RAG council
  (164 atom bịa → fv=-1, retriever loại)**.
- Audit liên môn (báo cáo này): xác nhận môn khác grounded, không cần duyệt lại.
