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

## 📚 Vòng 2 — p21-38 ĐÚC KẾT

### Insight 8: L3 Predictive RAG (§5.4)
3 submodule: Knowledge Structuring + Knowledge Induction + Forecasting.
→ **Rename cho Tử Vi**: `Forecasting` → `Tendency Reading` (Iron Rule #6).

### Insight 9: L4 Multi-Agent Planning (§5.5)
Multi-agent parallel với unique reasoning strategies.
→ Match đa trường phái yi-chronos.

### Insight 10: Benchmark KẾT QUẢ (§6.2-6.3)

| Dataset | PIKE-RAG (Ours) | Best Baseline | Gain |
|---|---|---|---|
| HotpotQA | EM 61.20 / F1 76.26 / Acc 87.60 | GraphRAG 89.00 Acc (EM=0) | EM lead +6.4 |
| 2WikiMultiHopQA | EM 66.80 / Acc 82.00 | Self-Ask H-R 80.00 | Top mọi metric |
| MuSiQue (hardest) | EM 46.40 / Acc 59.60 | Self-Ask R 49.80 | +9.8 Acc |
| LawBench 1-1 | 78.58 F1 | GraphRAG 23.27 | **+55pt** |
| Open Australian Legal QA | 98.59 Acc | GraphRAG 88.27 | +10pt |

→ Legal benchmark relevant nhất với Tử Vi (domain-specific). Win mạnh = paradigm hợp.

### Insight 11: Train Decomposer cải thiện 5-14pt (§6.4)

| Atomic Proposer | Pre-FT | Post-FT |
|---|---|---|
| Llama-3.1-8B | 47.83 | 62.14 (+14.31) |
| Qwen2.5-14B | 56.52 | 63.95 (+7.43) |
| phi-4-14B | 60.33 | 65.76 (+5.43) |

→ Xác nhận Decision 4 anh chốt — train decomposer riêng Tử Vi đáng đốt token.

### Insight 12: 3 lý do PIKE-RAG win (Real Cases §6.5)

1. **Multi atomic queries** thay vì single follow-up (Self-Ask fail mode)
2. **Diverse phrasings** bridge schema gap (corpus formal vs query colloquial)
3. **Retain entire chunk** không nén intermediate answer (giữ context)

→ Áp Tử Vi:
- User "anh giàu không" → multi atomic ("Vũ Khúc Hoá Lộc?" + "Tham Lang Hoá Lộc tài?" + "Lưu niên Lộc Tồn nhập?")
- Corpus "Phú quý song toàn" vs query "giàu có" → atomic Q multiple Hán-Việt + Việt thuần
- Giữ nguyên paragraph Trung Châu Q2 §X, không nén "Liêm-Thất hùng tú"

### Insight 13: SFT data transformation (Algorithm 3, prompt template)

```
prompt_x:
"...Output:
<decompose>True/False</decompose>
<sub-question>...</sub-question>"

LoRA r=16, alpha=64, lr=1.5e-5. Single A100-80G GPU.
```

### Insight 14: Hyperparameters production

- Atomizing: temperature **0.7** (diversity)
- QA generation: temperature **0** (determinism)
- Hierarchical KB: top-8 atomic Q (threshold 0.5) + extra 4 chunks per atomic Q

---

## 📚 Vòng 3 — Codebase Deep-Dive ĐÚC KẾT (5 files / 814 lines)

### Insight 15: Architecture 2-Store (chunk_atom_retriever.py)

**ChunkAtomRetriever** = 2 Chroma vector stores SONG SONG:
- `_chunk_store`: lưu chunk text + metadata `atom_questions_str` (newline-separated backup)
- `_atom_store`: lưu mỗi atomic question riêng, metadata `source_chunk_id` link về chunk

**AtomRetrievalInfo dataclass** (output):
```python
{
  atom_query: str,             # query của user
  atom: str,                    # atomic Q matched
  source_chunk_title: str,
  source_chunk: str,            # ENTIRE chunk text, không nén
  source_chunk_id: str,
  retrieval_score: float,
  atom_embedding: List[float]
}
```

→ Match Insight 12c: retain entire chunk, không nén intermediate answer.

### Insight 16: 4 Retrieval methods

1. `retrieve_atom_info_through_atom(queries)` — query → atom_store → source_chunk
2. `retrieve_atom_info_through_chunk(query)` — query → chunk_store → best-hit atom in metadata
3. `retrieve_contents_by_query(query)` — COMBINE cả 2 paths
4. `retrieve_contents(qa)` — wrapper

→ Hybrid retrieval thông minh, không phụ thuộc 1 path.

### Insight 17: Algorithm 1 impl (qa_decompose.py)

**4 protocols inject**:
- `decompose_proposal_protocol` — LLM propose atomic Q
- `selection_protocol` — LLM select Q tốt nhất
- `backup_selection_protocol` — fallback nếu select fail
- `original_question_answering_protocol` — final synthesize

**Loop logic** (method `answer`):
```python
chosen_atom_infos = []
while len(chosen_atom_infos) < max_num_question (5):
    # Step 1: Proposal
    decompose, thinking, proposals = propose(question, chosen)
    if not decompose: break

    # Step 2: Retrieval (3-level fallback)
    candidates = retrieve_atom_info_candidates(proposals, query, chosen)
    #   a) atom_queries → atom_store
    #   b) original query → atom_store
    #   c) original query → chunk_store
    if not candidates: break

    # Step 3: Selection
    selected, _, chosen_info = select_atom_question(question, candidates, chosen)
    if selected: chosen.append(chosen_info)
    else: break

# Final
output = answer_original_question(question, chosen)
```

**Filter dup**: drop candidates có `source_chunk_id` trùng với chunks đã chọn.

### Insight 18: CommunicationProtocol pattern (protocol.py)

```python
@dataclass
class CommunicationProtocol:
    template: MessageTemplate       # prompt template
    parser: BaseContentParser       # output parser
    template_partial(**kwargs)      # partially fill placeholders
    process_input(content, **kwargs) -> List[Dict[str, str]]   # format messages
    parse_output(content, **kwargs) -> Any                      # decode response
```

→ Mỗi LLM step (propose/select/answer) có 1 protocol riêng. Tách rõ prompt + parser.

### Insight 19: Hyperparameters default (qa_decompose.py)

- `max_num_question = 5` (max sub-questions trong loop)
- `question_similarity_threshold = 0.9` (chưa dùng)

### Insight 20: Ingestion = LangChain-style (chunking.py + tagging.py)

```
Books → DocumentLoader → LLMPoweredRecursiveSplitter
     → chunks (with summary) → pickle dump
     → LLMPoweredTagger → atom_questions per chunk
     → 2 Chroma stores
```

Workflow class wraps YAML config → init LLM client (with sqlite cache) → init splitter/tagger with 3-4 protocols → run.

---

## 🏗 ARCHITECTURE TỔNG (sau khi đọc cả paper + code)

```
┌─────────────────────────────────────────────────────────────┐
│  INGESTION (offline, run 1 lần cho mỗi sách)                 │
│                                                              │
│  Books → DocumentLoader → LLMPoweredRecursiveSplitter        │
│       → chunks {text, summary, atom_questions_str}           │
│       → LLMPoweredTagger → tags                              │
│       → chunk_store (Chroma) + atom_store (Chroma)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  REASONING (online, mỗi user query)                          │
│                                                              │
│  User query                                                  │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ QaDecompositionWorkflow (Algorithm 1)               │    │
│  │                                                      │    │
│  │  while len(chosen) < 5:                              │    │
│  │    1. Proposal protocol → atomic Qs                  │    │
│  │    2. ChunkAtomRetriever 3-level                     │    │
│  │       a) atomic Q → atom_store                       │    │
│  │       b) original Q → atom_store (fallback)          │    │
│  │       c) original Q → chunk_store (fallback)         │    │
│  │    3. Selection protocol → pick 1 useful             │    │
│  │       drop dup source_chunk_id                       │    │
│  │                                                      │    │
│  │  Answer protocol → final synthesis                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺 GAP ANALYSIS yi-chronos vs PIKE-RAG

| PIKE-RAG component | yi-chronos đã có | Cần build mới |
|---|---|---|
| Chroma `_chunk_store` | SQLite `passages` + sqlite-vec | ✅ có |
| Chroma `_atom_store` | ❌ | **Build bảng `atomic_questions`** |
| `source_chunk_id` link | ❌ | FK trong atomic_questions |
| LLMPoweredRecursiveSplitter (chunking + forward-summary) | MarkItDown chia trang | **Build LLM chunker mới** |
| LLMPoweredTagger (atomic Q gen) | ❌ | **Build atomic Q generator** |
| QaDecompositionWorkflow (Algorithm 1) | engine v3/v4 47 rules thủ công | **Build orchestrator wrap engine cũ** |
| CommunicationProtocol pattern | api/main.py prompts ad-hoc | **Refactor thành protocol classes** |
| LLM client + cache | ai_keys.json + 8 providers | ✅ có |
| Cosine similarity | sqlite-vec | ✅ có |

**5 gap chính**: atomic Q store + chunker + tagger + Algo 1 wrapper + protocol classes.

---

## 📝 DECISIONS UPDATED sau vòng 3

(Chưa đổi gì so với vòng 1+2, chỉ confirm thêm chi tiết)

- **Decision 1 paradigm**: confirm Question-as-Index khớp `_atom_store` model
- **Decision 2 chunking**: confirm cần LLMPoweredRecursiveSplitter equivalent
- **Decision 3 wrap v3/v4**: rõ cách wrap — QaDecompositionWorkflow là class wrapper, gọi `_retriever` (engine v3/v4) làm 1 trong các path retrieval
- **Decision 4 train decomposer**: rõ data structure cần collect — `(question, [sub-Q + answer per step], final_answer, score)`

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
