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

## 📚 Vòng 4 — ICML 2025 paper p1-20 ĐÚC KẾT

### Insight 21: KAR³-RAG = Knowledge-Aware dual Rewriting and Reasoning (§3.2)
4 components rõ ràng:
1. **Knowledge Atomizer** $f_a$: chunk → atomic tags (offline preprocessing)
2. **Query Proposer** $f_p$: (q, context) → atomic query proposals (online)
3. **Atomic Retriever** $\mathcal{R}_{atom}$: atomic queries → atomic pairs
4. **Atomic Selector** $\mathcal{S}_{atom}$: select most useful atomic pair

### Insight 22: Dual Rewriting paradigm (Figure 3) — INNOVATION CỐT
- **Query side**: user question → atomic queries (LLM Query Proposer)
- **Chunk side**: chunk → atomic tags = atomic questions chunk answer được (LLM Atomizer)
- **Bridge**: atomic queries semantically match atomic tags qua embedding
→ Giải quyết schema gap "the mother of" vs "the son of" trong corpus

### Insight 23: Dynamic Path Generation (Figure 1) — paradigm shift
- Chain-shaped (Self-Ask): 1 sub-Q tại 1 step
- Tree-shaped (ProbTree): multiple sub-Q tại 1 step
- **Dynamic (KAR³)**: SELECT sub-Q from PROPOSAL SET based on RELEVANCE OF ATOMIC RETRIEVAL
→ Adaptive, không cứng chain/tree

### Insight 24: Composable functional notation (§3.4 Eq 1-7)
```
KB = {f_a(d_k), d_k}                                   # knowledge base
q̂_t = f_p(q, C_{t-1})                                  # propose atomic queries
P^q̂_t = R_atom(q̂_t, f_a(D))                            # retrieve atomic pairs
c_t = S_atom(R_atom(f_p(q, C_{t-1}), f_a(D)))          # select chunk
```
→ Clean math, dễ implement.

### Insight 25: N=5 sweet spot (§4.3 Figure 5, Table 8)
N=4 đạt ~92% recall (HotpotQA, 2Wiki). N=5 chỉ tăng marginal. N=6+ overfit.
→ Confirm Insight 19 codebase (max_num_question=5).

### Insight 26: Ablation — mỗi component đóng góp 15-17% (Table 3)
| Variant | F1 drop |
|---|---|
| Atomizer → plain text | -15.1% |
| Query Proposer → single Q | -16.6% |
| Atomic Retriever → chunks only | -15.3% |
| Atomic Selector → chunks direct | -16.2% |

→ **KHÔNG SKIP component nào**. Mỗi cái critical.

### Insight 27: Token economics (Table 10-12)
- KAR³: 8,820 tokens/QA (efficient)
- ProbTree: 25,875 tokens (3x đắt)
- Atomization preprocessing one-time: 320-340 tokens/chunk × ~5000-7000 calls/dataset

→ **Áp Tử Vi**: 42 sách × ~500 chunks × 350 tokens = ~7.3M tokens ingestion. Đốt được.

### Insight 28: Atomic Q > Plain text (Table 13)
| Atomic Tags | F1 (MuSiQue) | Acc |
|---|---|---|
| Plain text sentence | 45.88 | 54.20 |
| **Atomic questions** | **57.86** | **62.60** |

→ Question-as-Index lúc nào cũng tốt hơn plain. Paradigm confirmed.

### Insight 29: Method comparison (Table 5) — KAR³ KHÁC 3 chỗ
| | Decomposition | Retrieval | Context |
|---|---|---|---|
| Self-Ask | chain | sub-Q → chunk | QA pairs (nén) |
| ProbTree | tree | sub-Q → chunk | QA pairs |
| **KAR³** | **dynamic** | **sub-Q → atomic Q → chunk** | **selected chunks (entire)** |

### Insight 30: Limitation (§4.3)
- Cần LLM mạnh (GPT-4 > GPT-3.5)
- Future work: train query proposer riêng → match Decision 4 yi-chronos

---

## 📚 Vòng 5 — ICML p21-26 ĐÚC KẾT (KEY: 4 PROMPTS FULL)

### Insight 31: 4 Prompt Templates production (§A.7)

**(1) Atomic Question Tagging Prompt** (offline, atomize chunks):
```
# Task
Your task is to extract as many questions as possible that are relevant
and can be answered by the given content. Please try to be diverse and
avoid extracting duplicated or similar questions. Make sure your question
contain necessary entity names and avoid to use pronouns like it, he, she,
they, the company, the person etc.

# Output Format
Output your answers line by line, with each question on a new line,
without itemized symbols or numbers.

# Content
{content}

# Output
```

**Áp Tử Vi** — chỉnh template:
- "necessary entity names" → "tên sao + tên cung + chi rõ ràng (vd. 'Tử Vi tại Mệnh cung Tý')"
- "avoid pronouns" → "tránh đại từ 'nó, người này, mệnh tạo'"

**(2) Atomic Query Proposer Prompt** (runtime, decompose):
```
# Task
Your task is to analyse the providing context then raise atomic
sub-questions for the knowledge that can help you answer the question
better. Think in different ways and raise as many diverse questions
as possible.

# Output Format JSON:
{"thinking": <analysis>, "sub_questions": <list>}

# Context: {chosen_content}
# Question: {content}
```

**(3) Atomic Tag Selection Prompt** (runtime, select 1 best):
```
# Task
... Select a most relevant sub-question from the given question list,
avoid selecting sub-question that can already be answered with the given
context or with your own knowledge.

# Output Format JSON:
{"thinking": <thinking>, "question_idx": <integer 1 to {num_atom_questions}>}

# Context: {chosen_content}
# Sub-Questions: {atom_question_list_str}
# Question: {content}
```

**(4) Question Answering Prompt** (final synthesis):
```
# Task
Your task is to answer a question referring to a given context...

# Output format JSON:
{"answer": <string>, "rationale": <rationale behind your choice>}

# Context, if any: {context_if_any}
# Question: {content}{yes_or_no_limit}

Let's think step by step.
```

→ Notes:
- "Let's think step by step" (CoT prompt)
- `rationale` field = CITATION yêu cầu
- JSON format strict
- Zero-shot (không few-shot)

### Insight 32: Legal benchmark detail (§A.8) — DOMAIN GẦN TỬ VI

LawBench 6 tasks (Trung văn pháp luật, mỗi task 500 Q):
- 1-1 Statute Recitation (Generation/F1) → ~ "Trích nguyên văn sách Trung Châu"
- 1-2 Legal Knowledge Q&A (Single Choice/EM) → ~ "Sao này thuộc loại gì"
- 3-1 Statute Prediction Fact-based → ~ "Lá số có cách cục nào"
- 3-2 Statute Prediction Scenario-based (Generation/F1) → ~ "Tình huống X thì sao"
- 3-6 Case Analysis (Single Choice/EM) → ~ "Phân tích case"
- 3-8 Consultation (Generation/F1) → ~ "Tư vấn lá số user"

**KAR³ trên Open Australian Legal QA: 98.59% Acc** — domain formal terminology + structured rationale (giống Tử Vi 100%) — win cực mạnh.

---

## 📊 TỔNG KẾT 5 VÒNG RESEARCH — 32 insights

| Vòng | Source | Insights |
|---|---|---|
| 1 | arxiv p1-20 (paradigm + algorithm) | 1-7 |
| 2 | arxiv p21-38 (benchmarks + cases) | 8-14 |
| 3 | codebase 5 files (architecture) | 15-20 |
| 4 | ICML p1-20 (KAR³ deep) | 21-30 |
| 5 | ICML p21-26 (4 prompts + legal) | 31-32 |

**4 Decision anh đã chốt** (vẫn giữ nguyên, được confirm thêm qua vòng 3-5):
1. Paradigm tuple identity + N-layered meaning + KHÔNG suy đoán
2. Rebuild full PIKE-RAG chunking + atomic Q (Decision C)
3. Wrap engine v3/v4 hiện có (atomic answerers)
4. Train decomposer riêng Tử Vi (đốt token Max)

**5 GAP yi-chronos cần build**:
1. Atomic Q store + link `source_chunk_id`
2. LLM Recursive Splitter (chunking + forward-summary)
3. LLM Atomic Q Generator (4 prompt templates)
4. Algo 1 orchestrator wrap engine cũ
5. CommunicationProtocol classes (4 protocols per case)

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
