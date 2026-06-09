# 📖 PIKE-RAG Thâm Nhuần — Journey Log

> Microsoft Research Asia · arxiv 2501.11551 · ICML 2025
> Start: 2026-06-09 · Skill: `doc-sau-20-trang` · Iron Rule project #1

---

## 🎯 Lý do thâm nhuần

Anh CEO chỉ ra bài toán CỐT 2026-06-09:
> "Các vì sao là cố định về định nghĩa, tên gọi hay tính chất chung, nhưng mỗi khi ở 1 vị trí trong lá số, tương tác với các sao khác lại ra ý nghĩa khác, nó có vô vàn kiến thức nhỏ li ti như vậy cần xử lý để chuẩn bị cho việc luận giải hàng triệu tổ hợp của user."

Vấn đề: em đã wire 47 rules thủ công sau 32 vòng đọc Trung Châu Q2 (1 cuốn). 41 cuốn còn lại = vài năm + không scale.

→ Anh ra lệnh: research thế giới đã giải bài toán này thế nào.

Kết quả research (báo cáo riêng): **Microsoft PIKE-RAG = EXACT match paradigm** anh cần.

---

## 🔑 4 Decisions anh chốt 2026-06-09 sau vòng 1 (p1-20)

### Decision 1 — PARADIGM CỐT (anh tự diễn)

> "1 sao × cung × combo liên sao × combo liên cung >> ra ý nghĩa 1, từng sách khác nhau mà bổ sung thêm ý nghĩa 2-3-4. Chúng ta cần bám sát vào các luận giải của sách trước. Câu hỏi kèm theo nên mặc định: tính chất gốc của sao? của cung? nguyên lý hoạt động hoặc vận hành để tìm ra bản chất lõi, không suy đoán."

**Schema reflect anh đặt:**

```
KEY (tuple identity, fixed):
  - sao_chinh: vd "Tử Vi"
  - cung: vd "Mệnh"
  - combo_sao: vd "+Phá Quân đồng cung"
  - combo_cung: vd "+Tham Lang Thiên Di tam hợp"

VALUES (N-layered, accumulated, KHÔNG ghi đè):
  Layer 1: book A page X — meaning 1
  Layer 2: book B page Y — meaning 2 (supplements)
  Layer N: book Z page W — meaning N

ATOMIC QUESTIONS (default template, attached):
  - Tính chất GỐC của sao X?
  - Tính chất GỐC của cung Y?
  - Nguyên lý VẬN HÀNH của combo Z?
  - Bản chất LÕI của (X + Y + Z)?

CONSTRAINT: ⛔ KHÔNG suy đoán. Bám sách 100%.
```

→ Match perfect với Question-as-Index paradigm của PIKE-RAG (p16 §5.3.1).

### Decision 2 — Atomic Q + Chunking: (C) Rebuild full PIKE-RAG

Anh chọn quality cao nhất. Effort 2-3 tuần.

- Re-chunk 42 sách với iterative text splitting + forward-summary recursive
- Mỗi chunk: `{text, summary, atomic_questions[], source: {book, page, section}}`
- Atomic Q template chuẩn theo Decision 1
- Index qua sqlite-vec

### Decision 3 — Algorithm 1: Wrap quanh engine v3/v4 hiện có

KHÔNG đập đi build lại. Algorithm 1 (Knowledge-Aware Decomposition) làm orchestrator gọi engine v3/v4 (47 rules Trung Châu đã wire) làm atomic answerers.

Pattern:
```
user_query
  → decompose thành atomic Q
  → cho mỗi atomic Q:
      → check engine v3/v4 trả lời được không
      → nếu không → retrieve từ atomic_questions KB
  → synthesize với citations + confidence
```

### Decision 4 — Algorithm 2: TRAIN decomposer riêng Tử Vi

Anh duyệt đốt token Max. Plan:
- Claude/DeepSeek làm seed teacher
- Data từ kinhdich.online user-confirmed cases
- UCB sampling + SFT + DPO
- Phase muộn — document path tuần này, training thật khi pipeline ổn định

---

## 📚 Vòng 1 — p1-20 ĐÚC KẾT

### Insight 1: Phân loại task 4 level (L1-L4)

| Level | Question type | Tử Vi mapping |
|---|---|---|
| L1 | Factual | Lookup sao/cung |
| L2 | Linkable-Reasoning (bridging/quant/compare/summarize) | Cách cục + tam phương |
| L3 | Predictive | Đại vận biến hóa (paradigm đồng dạng — KHÔNG predict cứng per Iron Rule #6) |
| L4 | Creative | Tổng đoán cuộc đời |

→ Tử Vi nặng L2 + L4.

### Insight 2: Knowledge base 3 lớp Graph (G_i / G_c / G_dk)

- **G_i Information Resource**: 42 sách (✅ yi-chronos có)
- **G_c Corpus**: sections + chunks (✅ SQLite passages có)
- **G_dk Distilled**: KG + atomic + tabular + induced (❌ **GAP** — sẽ build qua Decision 2)

### Insight 3: Question-as-Index (CHÌA KHOÁ §5.3.1)

Quote nguyên: _"Instead of utilizing declarative sentences or subject-relationship-object tuples, we propose using questions as knowledge indexes to further bridge the gap between stored knowledge and query."_

→ Match Decision 1 anh đặt.

### Insight 4: Enhanced Chunking (§5.2.1, Figure 5)

Iterative text splitting với forward-summary recursive. Mỗi chunk có summary kèm theo. Tránh disrupt semantic coherence.

### Insight 5: Auto-tagging Domain Gap (§5.2.2, Figure 7)

Query colloquial vs corpus formal. 3-step solution:
1. Corpus Tag Collection (LLM extract tags từ corpus)
2. Tag Pair Collection (LLM map query tags → corpus tags)
3. Information Retrieval qua mapped tags

→ Tag classes Tử Vi sẽ build: 命格 / 财官 / 婚姻 / 子女 / 大运 / 流年 / 健康 / 性格 / 父母 / 兄弟 (10 tier 1).

### Insight 6: Algorithm 1 — Knowledge-Aware Decomposition (§5.3.2)

```
1. C₀ = ∅
2. for t in 1..N:
3.   {q̂ᵢᵗ} = LLM(q, C_{t-1})                  # propose atomic queries
4.   for each q̂ᵢᵗ: retrieve top-K from KB     # cosine sim ≥ δ
5.   qᵗ = LLM_select_most_useful(...)
6.   if qᵗ is None: break
7.   else: cᵗ = fetch_chunk(qᵗ); Cᵗ ∪= {cᵗ}
8. â = LLM(q, Cᵗ)
```

→ Decision 3: wrap quanh engine v3/v4. Engine v3/v4 = "atomic answerers", Algorithm 1 = orchestrator.

### Insight 7: Decomposer Training (§5.3.3, Algorithm 2)

SFT + DPO + UCB context sampling. → Decision 4 chọn làm.

---

## 📚 Vòng 2 — p21-38 (PENDING)

Sẽ đọc tiếp:
- L3 Predictive RAG (§5.4)
- L4 Creative RAG + multi-agent planning (§5.5)
- Experiments + benchmarks (§6)
- Discussion + limitations (§7)
- Conclusion

---

## 📚 Vòng 3 — Codebase deep-dive (PENDING)

- `pikerag/knowledge_retrievers/chunk_atom_retriever.py` (CỐT)
- `pikerag/workflows/qa_decompose.py` (Algorithm 1)
- `pikerag/workflows/tagging.py` (Auto-tagging)
- `pikerag/workflows/chunking.py` (Enhanced chunking)
- `pikerag/prompts/protocol.py` (Prompt templates)
- `examples/biology` (domain-specific reference, gần với Tử Vi terminology)

---

## 📝 Phương châm

> "Đây là bài toán backend, nền tảng, cần nghiên cứu sâu. Làm sai là rất mệt."
> — Anh CEO, 2026-06-09

- Pure research mode, KHÔNG jump code
- Bám paper + codebase Microsoft, không tự bịa
- Decisions ghi nhận lại, không trôi
