# 🏗 PIKE-RAG Adoption — yi-chronos Schema Design

> Author: em (Claude) · Co-designer: Anh CEO
> Date: 2026-06-09
> Status: **DRAFT, chờ Anh review + duyệt**
> Companion: [pike-rag-tham-nhuan-2026.md](pike-rag-tham-nhuan-2026.md) (research journey, 32 insights)
> Stack: SQLite + sqlite-vec + FTS5 + Python FastAPI + 8 LLM providers

---

## 📐 PART 1 — THE OVERVIEW

### 1.1 Bài toán anh đặt ra (paradigm cốt 2026-06-09)

> **Mỗi mảnh kiến thức Tử Vi/Bát Tự/Kinh Dịch = 1 TUPLE 4 KHOÁ + N LỚP Ý NGHĨA**
>
> KEY (định danh duy nhất, cố định):
> - `sao_chinh` (vd. "Tử Vi")
> - `cung` (vd. "Mệnh")
> - `combo_sao` (vd. "+Phá Quân đồng cung")
> - `combo_cung` (vd. "+Tham Lang Thiên Di tam hợp")
>
> VALUES (N-layered, accumulated, KHÔNG ghi đè):
> - Layer 1: sách A trang X — meaning 1
> - Layer 2: sách B trang Y — meaning 2 (bổ sung)
> - Layer N: sách Z trang W — meaning N
>
> CONSTRAINT: ⛔ KHÔNG suy đoán. Bám sách 100%.

### 1.2 Paradigm PIKE-RAG (research confirmed)

- **Question-as-Index** thay vì SPO triples (Insight #3, #28)
- **Dual rewriting**: chunk → atomic Q + query → atomic Q (Insight #22)
- **Dynamic decomposition** N=5 iterations (Insight #25)
- **Retain entire chunk** không nén intermediate (Insight #12c)
- **4 components KHÔNG SKIP**: Atomizer + Proposer + Retriever + Selector (Insight #26)

### 1.3 Bridge

Anh đặt paradigm KEY=(4 khoá) + VALUES=(N layers). PIKE-RAG đề xuất paradigm Question-as-Index.

**→ Em bridge**: mỗi `paradigm_meaning` (1 row tương ứng 1 meaning layer) sẽ KÈM theo `atomic_questions` — chính là "câu hỏi mặc định" mà anh nói:
- "Tính chất gốc của sao X?"
- "Tính chất gốc của cung Y?"
- "Nguyên lý vận hành combo Z?"
- "Bản chất lõi của (X+Y+Z)?"

---

## 📐 PART 2 — SCHEMA SQL CHI TIẾT

### 2.1 Tables MỚI (9 tables)

```sql
-- ═══════════════════════════════════════════════════════════════
-- A. CHUNK LAYER (replace passages, add summary + atom backup)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE chunks (
    chunk_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id         INTEGER NOT NULL,
    author_id       INTEGER NOT NULL,
    corpus_id       TEXT NOT NULL,                  -- vd. "trung-chau-q2"
    page_start      INTEGER NOT NULL,
    page_end        INTEGER NOT NULL,
    section_path    TEXT,                            -- vd. "§4.4.5"
    text            TEXT NOT NULL,                   -- chunk text gốc
    summary         TEXT,                            -- LLM-generated chunk summary (forward-summary)
    forward_summary TEXT,                            -- accumulated summary tới chunk này
    atom_q_str      TEXT,                            -- backup: "\n".join(atomic Qs) — for retrieve_through_chunk path
    metadata_json   TEXT,                            -- {section_title, ...}
    is_canonical    INTEGER NOT NULL DEFAULT 1,
    created_at      INTEGER NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
CREATE INDEX idx_chunks_corpus ON chunks(corpus_id);
CREATE INDEX idx_chunks_author ON chunks(author_id);
CREATE INDEX idx_chunks_page ON chunks(corpus_id, page_start);

-- FTS5 cho keyword search
CREATE VIRTUAL TABLE chunks_fts USING fts5(
    text, summary, atom_q_str,
    content='chunks', content_rowid='chunk_id',
    tokenize='unicode61'
);

-- vec index cho embedding chunk (sqlite-vec)
CREATE VIRTUAL TABLE chunks_vec USING vec0(
    chunk_id INTEGER PRIMARY KEY,
    embedding FLOAT[1536]      -- text-embedding-3-small (1536) hoặc embedding model anh chọn
);

-- ═══════════════════════════════════════════════════════════════
-- B. ATOM LAYER (atomic questions per chunk)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE atomic_questions (
    atom_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id        INTEGER NOT NULL,                -- FK link về chunk (PIKE-RAG source_chunk_id)
    question_text   TEXT NOT NULL,                   -- atomic Q (vd. "Tử Vi tại Mệnh cung Tý có ý gì?")
    question_lang   TEXT NOT NULL DEFAULT 'vi',      -- 'vi' | 'zh' | 'sino-vi'
    template_type   TEXT,                            -- 'tinh_chat_goc' | 'nguyen_ly' | 'ban_chat_loi' | 'thuc_hanh' | NULL
    paradigm_key    TEXT,                            -- JSON: {sao_chinh, cung, combo_sao, combo_cung} nếu match
    confidence      REAL DEFAULT 0.85,                -- 0.85 default, 0.98 nếu founder verified, demote nếu sai
    source_quote    TEXT,                            -- đoạn trích nguyên văn từ chunk (citation evidence)
    extracted_by    TEXT,                            -- LLM provider + model + version
    founder_verified INTEGER DEFAULT 0,              -- 0 | 1 | -1 (anh confirm đúng / chưa / sai)
    created_at      INTEGER NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
);
CREATE INDEX idx_atom_chunk ON atomic_questions(chunk_id);
CREATE INDEX idx_atom_paradigm ON atomic_questions(paradigm_key);
CREATE INDEX idx_atom_verified ON atomic_questions(founder_verified);
CREATE INDEX idx_atom_lang ON atomic_questions(question_lang);

-- vec index cho atomic Q (CỐT của hệ thống)
CREATE VIRTUAL TABLE atom_vec USING vec0(
    atom_id INTEGER PRIMARY KEY,
    embedding FLOAT[1536]
);

-- FTS5 cho atomic Q
CREATE VIRTUAL TABLE atomic_questions_fts USING fts5(
    question_text, source_quote,
    content='atomic_questions', content_rowid='atom_id',
    tokenize='unicode61'
);

-- ═══════════════════════════════════════════════════════════════
-- C. PARADIGM LAYER (N-layered meanings per tuple ID — Decision 1)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE paradigm_keys (
    pk_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sao_chinh       TEXT NOT NULL,                   -- vd. "Tử Vi" (Hán-Việt chuẩn)
    cung            TEXT NOT NULL,                   -- vd. "Mệnh"
    combo_sao       TEXT NOT NULL DEFAULT '',        -- vd. "+Phá Quân đồng cung" (sorted alphabet)
    combo_cung      TEXT NOT NULL DEFAULT '',        -- vd. "+Tham Lang Thiên Di tam hợp"
    chi             TEXT,                            -- địa chi nếu specific: "Tý" | "Ngọ" | NULL
    school          TEXT,                            -- 'trung-chau' | 'phu-thai-vi' | 'nam-phai' | NULL
    canonical_form  TEXT NOT NULL,                   -- string canonical: "tu-vi+menh+pha-quan-dong-cung+tham-lang-thien-di-tam-hop"
    UNIQUE(canonical_form)
);
CREATE INDEX idx_pk_sao ON paradigm_keys(sao_chinh);
CREATE INDEX idx_pk_cung ON paradigm_keys(cung);
CREATE INDEX idx_pk_school ON paradigm_keys(school);

CREATE TABLE paradigm_meanings (
    pm_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    pk_id           INTEGER NOT NULL,                -- FK paradigm_keys
    layer_number    INTEGER NOT NULL,                -- 1, 2, 3... (đếm dần qua sách)
    meaning_text    TEXT NOT NULL,                   -- ý nghĩa từ sách
    source_chunk_id INTEGER,                          -- FK chunks (where meaning extracted)
    source_atom_id  INTEGER,                          -- FK atomic_questions (entry point)
    source_book     TEXT NOT NULL,                   -- corpus_id
    source_page     INTEGER,
    source_quote    TEXT,                            -- nguyên văn từ sách
    author_id       INTEGER,
    school          TEXT,
    confidence      REAL DEFAULT 0.85,
    founder_verified INTEGER DEFAULT 0,
    conflicts_with  TEXT,                            -- JSON list of pm_ids that contradict
    created_at      INTEGER NOT NULL,
    FOREIGN KEY (pk_id) REFERENCES paradigm_keys(pk_id) ON DELETE CASCADE,
    FOREIGN KEY (source_chunk_id) REFERENCES chunks(chunk_id),
    FOREIGN KEY (source_atom_id) REFERENCES atomic_questions(atom_id)
);
CREATE INDEX idx_pm_pk ON paradigm_meanings(pk_id);
CREATE INDEX idx_pm_book ON paradigm_meanings(source_book);
CREATE INDEX idx_pm_school ON paradigm_meanings(school);
CREATE INDEX idx_pm_verified ON paradigm_meanings(founder_verified);

-- ═══════════════════════════════════════════════════════════════
-- D. TAGGING LAYER (Auto-tagging — Insight #5)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE tag_classes (
    tc_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name_zh         TEXT,                            -- 命格 / 财官 / ...
    name_vi         TEXT NOT NULL,                   -- "Cách Cục" / "Tài Quan"
    description     TEXT,
    parent_tc_id    INTEGER,                          -- self-FK cho hierarchy
    FOREIGN KEY (parent_tc_id) REFERENCES tag_classes(tc_id)
);

CREATE TABLE corpus_tags (
    ct_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id        INTEGER NOT NULL,
    tc_id           INTEGER NOT NULL,
    tag_text        TEXT NOT NULL,                   -- "Vũ Khúc Hoá Lộc" (formal)
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (tc_id) REFERENCES tag_classes(tc_id)
);

CREATE TABLE tag_pairs (
    tp_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    query_tag       TEXT NOT NULL,                   -- "giàu", "có tiền" (colloquial)
    corpus_tag      TEXT NOT NULL,                   -- "Phú quý song toàn" (formal)
    tc_id           INTEGER NOT NULL,
    mapping_score   REAL DEFAULT 1.0,
    UNIQUE(query_tag, corpus_tag),
    FOREIGN KEY (tc_id) REFERENCES tag_classes(tc_id)
);
CREATE INDEX idx_tp_query ON tag_pairs(query_tag);

-- ═══════════════════════════════════════════════════════════════
-- E. DECOMPOSER TRAINING (Algorithm 2 — Decision 4)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE decompose_trajectories (
    traj_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query      TEXT NOT NULL,                   -- query gốc
    user_id         TEXT,                            -- person_key của user (privacy: hash)
    la_so_snapshot  TEXT,                            -- JSON lá số khi query (cho training context)
    trajectory_json TEXT NOT NULL,                   -- [{step: 1, sub_q: "...", chosen_chunk_id: 123, score: 0.92}, ...]
    final_answer    TEXT NOT NULL,
    answer_score    REAL,                            -- judge score (GPT-4 hoặc anh confirm)
    founder_verified INTEGER DEFAULT 0,
    created_at      INTEGER NOT NULL
);
CREATE INDEX idx_traj_verified ON decompose_trajectories(founder_verified);

-- ═══════════════════════════════════════════════════════════════
-- F. PROVENANCE (audit trail mỗi extraction)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE extraction_runs (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type        TEXT NOT NULL,                   -- 'chunking' | 'atomizing' | 'tagging' | 'paradigm_extract'
    corpus_id       TEXT NOT NULL,
    llm_provider    TEXT,
    llm_model       TEXT,
    temperature     REAL,
    config_json     TEXT,                            -- full prompt + hyperparams snapshot
    started_at      INTEGER,
    completed_at    INTEGER,
    chunks_processed INTEGER DEFAULT 0,
    atoms_generated INTEGER DEFAULT 0,
    cost_tokens     INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'pending'           -- 'pending' | 'running' | 'completed' | 'failed'
);
```

### 2.2 Tables KEEP (giữ nguyên, link sang mới)

- `authors` (32 tổ sư)
- `works` (sách)
- `concept_index` + `concept_fts` (concept dictionary, sẽ inform `tag_classes`)
- `case_studies` (535 case lá số — sẽ link vào atomic_questions cho L4 multi-agent reasoning)
- `methods`, `predictions` — engine v3/v4 hiện tại

### 2.3 Tables MIGRATE

- `passages` → `chunks`: copy data + LLM populate `summary`, `forward_summary`, `atom_q_str`
- `passages_vec` → `chunks_vec`: re-embed nếu đổi model, hoặc giữ embedding cũ

---

## 📐 PART 3 — ER DIAGRAM (text-based)

```
                      ┌──────────┐
                      │ authors  │
                      └────┬─────┘
                           │
                      ┌────▼─────┐
                      │  works   │
                      └────┬─────┘
                           │
            ┌──────────────▼─────────────────┐
            │            chunks              │
            │  (text + summary + atom_q_str) │
            └──┬──────────┬──────────────────┘
               │          │
        ┌──────▼──┐    ┌──▼───────────────┐
        │chunks_  │    │ atomic_questions │←──┐
        │  vec    │    │  (Q + paradigm_  │   │
        │chunks_  │    │   key + provena.)│   │ vec index
        │  fts    │    └──┬──────────────┘   │ FTS5
        └─────────┘       │                  │
                          │            ┌─────▼──────┐
                          │            │  atom_vec  │
                          │            │ atom_fts   │
                          │            └────────────┘
                          │
                  ┌───────▼────────┐         ┌──────────────┐
                  │ paradigm_      │         │ tag_classes  │
                  │  meanings      │←────────│ (10 Tử Vi)   │
                  │ (N layers per  │         └──────┬───────┘
                  │  paradigm_key) │                │
                  └───────▲────────┘         ┌──────▼───────┐
                          │                  │ corpus_tags  │
                  ┌───────┴────────┐         │ tag_pairs    │
                  │ paradigm_keys  │         └──────────────┘
                  │ (4-key tuple)  │
                  └────────────────┘

                  ┌──────────────────────┐
                  │decompose_trajectories│  ← Algo 2 training data
                  └──────────────────────┘
                  ┌──────────────────────┐
                  │  extraction_runs     │  ← provenance / audit
                  └──────────────────────┘
```

---

## 📐 PART 4 — MIGRATION PLAN

### Phase M1 — Schema setup (1 day)
1. Run migration SQL tạo 9 tables mới
2. Backup `passages_vec` (đảm bảo không mất data cũ)
3. Tạo views `passages_compat` map `chunks` → `passages` field names (backward compat cho engine v3/v4 cũ)

### Phase M2 — Data copy (1-2 days)
1. Copy `passages` → `chunks` 1-1 (raw_text → text, page_start/end giữ)
2. Re-embed chunks qua sqlite-vec (nếu đổi model)
3. `passages_fts` → `chunks_fts`

### Phase M3 — Chunk enrichment (3-5 days, foreground LLM)
1. Iterate chunks → LLM generate `summary` (forward-summary recursive)
2. LLM generate `atom_q_str` (4 prompt template #1)
3. Insert `atomic_questions` rows + embed `atom_vec`

### Phase M4 — Paradigm extraction (5-7 days)
1. Iterate atomic_questions → match (sao, cung, combo) → insert/update `paradigm_keys`
2. Link `paradigm_meanings` với chunk source

### Phase M5 — Tagging (2-3 days)
1. Seed `tag_classes` 10 Tử Vi (xem Part 7)
2. LLM extract `corpus_tags` từ chunks
3. LLM gen `tag_pairs` (query colloquial ↔ corpus formal)

### Phase M6 — Validation (ongoing)
1. Founder confirm spot-check `atomic_questions` → boost confidence
2. Cross-reference với 47 rules engine v3/v4 hiện có

---

## 📐 PART 5 — 4 PROMPT TEMPLATES PORT SANG VIỆT TỬ VI

### Prompt #1 — Atomic Question Tagging (offline ingestion)

```
# Nhiệm vụ
Đọc đoạn văn bản dưới đây từ sách Tử Vi/Bát Tự/Kinh Dịch. Hãy trích xuất CÀNG NHIỀU CÂU HỎI
liên quan và có thể trả lời bằng nội dung đoạn này.

QUY TẮC BẮT BUỘC:
1. Mỗi câu hỏi phải nêu RÕ TÊN sao, tên cung, tên cách cục, tên địa chi cụ thể.
   ⛔ TUYỆT ĐỐI tránh đại từ "nó", "mệnh tạo", "người này", "lá số này", "vị này".
   ✅ Đúng: "Tử Vi tại Mệnh cung Tý có ý nghĩa gì?"
   ❌ Sai: "Sao này tại cung này có ý gì?"

2. Đa dạng góc hỏi:
   - Tính chất GỐC của sao X?
   - Tính chất GỐC của cung Y?
   - Nguyên lý VẬN HÀNH của combo Z?
   - Bản chất LÕI của (X + Y + Z)?
   - Điều kiện hình thành cách cục Z?
   - Hệ quả khi gặp tứ sát / lục cát?

3. KHÔNG suy đoán ngoài nội dung sách. Bám 100% theo văn bản.

4. Tránh câu hỏi trùng lặp / quá giống nhau.

# Định dạng output
Mỗi câu hỏi 1 dòng. Không đánh số, không gạch đầu dòng.

# Nội dung
{content}

# Output
```

### Prompt #2 — Atomic Query Proposer (runtime decompose)

```
# Nhiệm vụ
Phân tích bối cảnh và câu hỏi của user. Đặt ra càng nhiều CÂU HỎI CON ATOMIC càng tốt
để chuẩn bị trả lời câu hỏi chính.

QUY TẮC:
1. Nghĩ theo nhiều góc khác nhau — đừng chain duy nhất 1 hướng.
2. Mỗi câu hỏi con nêu RÕ tên sao + cung + chi cụ thể.
3. Câu hỏi con phải có thể trả lời ĐỘC LẬP từ knowledge base (atomic).
4. Đa dạng phrasing: Hán-Việt chính thống + Việt thuần.

# Định dạng output JSON
{
  "thinking": "<phân tích bối cảnh và câu hỏi user>",
  "sub_questions": [
    "<câu hỏi con 1>",
    "<câu hỏi con 2>",
    ...
  ]
}

# Bối cảnh em đã có
{chosen_content}

# Câu hỏi user
{content}

# Output của em
```

### Prompt #3 — Atomic Tag Selection (runtime select 1 best)

```
# Nhiệm vụ
Phân tích bối cảnh hiện có và quyết định câu hỏi con nào HỮU ÍCH NHẤT để trả lời tiếp.

QUY TẮC:
1. Chọn câu hỏi con cung cấp THÔNG TIN MỚI — tránh chọn câu đã trả lời được bằng
   bối cảnh hiện có hoặc kiến thức nền.
2. Ưu tiên câu hỏi giúp tiến gần đến câu trả lời cuối.

# Định dạng output JSON
{
  "thinking": "<suy nghĩ về lựa chọn>",
  "question_idx": <integer từ 1 đến {num_atom_questions}>
}

# Bối cảnh em đã có
{chosen_content}

# Danh sách câu hỏi con để chọn
{atom_question_list_str}

# Câu hỏi user
{content}

# Output của em
```

### Prompt #4 — Question Answering (final synthesis)

```
# Nhiệm vụ
Trả lời câu hỏi user dựa trên bối cảnh đã thu thập. Đọc kỹ các đoạn trích từ sách, sau đó
đưa ra câu trả lời cuối với LẬP LUẬN rõ ràng.

QUY TẮC:
1. Bám sát bối cảnh. KHÔNG bịa thông tin ngoài context.
2. Trích nguồn cụ thể: tên sách + trang + tổ sư.
3. Lập luận theo paradigm "đọc đồng dạng" (Iron Rule #6) — KHÔNG predict tuyệt đối.
4. Nếu paradigm 2 trường phái xung đột → present cả 2, không ép vào 1.

# Định dạng output JSON
{
  "answer": "<câu trả lời, format string>",
  "rationale": "<lập luận, trích nguồn 'Trung Châu Q2 p347' / 'Phú Thái Vi Q1 p52' / ...>"
}

# Bối cảnh (nếu có)
{context_if_any}

# Câu hỏi
{content}{yes_or_no_limit}

Hãy suy nghĩ từng bước.
```

---

## 📐 PART 6 — PYTHON CLASSES SKELETON

### 6.1 Folder structure

```
engine/
├── atomization/                          # MỚI (Decision 2 build full)
│   ├── __init__.py
│   ├── chunker.py                        # LLMPoweredRecursiveSplitter equivalent
│   ├── atomizer.py                       # LLMPoweredTagger equivalent (atomic Q gen)
│   ├── tagger.py                         # Auto-tagging với tag_classes
│   ├── paradigm_extractor.py             # match (sao, cung, combo) → paradigm_keys
│   ├── retriever.py                      # ChunkAtomRetriever equivalent
│   ├── decomposer.py                     # Algorithm 1 orchestrator (wrap v3/v4)
│   ├── protocols/                        # CommunicationProtocol classes
│   │   ├── __init__.py
│   │   ├── base.py                       # BaseProtocol
│   │   ├── tagging.py                    # Prompt #1
│   │   ├── proposer.py                   # Prompt #2
│   │   ├── selector.py                   # Prompt #3
│   │   └── answerer.py                   # Prompt #4
│   └── prompts/
│       ├── vi/                            # tiếng Việt port
│       │   ├── tagging.txt
│       │   ├── proposer.txt
│       │   ├── selector.txt
│       │   └── answerer.txt
│       └── zh/                            # gốc tiếng Anh + tiếng Trung backup
│           └── ...
├── tu_vi/                                # GIỮ NGUYÊN
│   ├── an_sao.py
│   ├── chiem_phu_the_v3.py               # 34 rules wired
│   ├── chiem_phu_the_v4.py               # 13 rules wired
│   ├── trung_chau_paradigm.py            # paradigm engine cũ
│   └── ... (29 modules)
└── ai/                                   # GIỮ NGUYÊN
    └── providers/
```

### 6.2 BaseProtocol (port từ CommunicationProtocol PIKE-RAG)

```python
# engine/atomization/protocols/base.py
from dataclasses import dataclass
from typing import Any, Dict, List, Callable
from pathlib import Path

@dataclass
class BaseProtocol:
    template_path: Path                          # vd. "prompts/vi/tagging.txt"
    parser: Callable[[str], Any]                 # output parser function
    template_partial: Dict[str, str] = None      # partial fill vars

    def format_messages(self, content: str, **kwargs) -> List[Dict[str, str]]:
        """Render template → messages list cho LLM chat."""
        template = self.template_path.read_text(encoding='utf-8')
        if self.template_partial:
            for k, v in self.template_partial.items():
                template = template.replace(f"{{{k}}}", v)
        rendered = template.replace("{content}", content)
        for k, v in kwargs.items():
            rendered = rendered.replace(f"{{{k}}}", str(v))
        return [{"role": "user", "content": rendered}]

    def parse(self, response: str) -> Any:
        return self.parser(response)


# Subclass per prompt:
def parse_tagging_output(text: str) -> List[str]:
    """Atomic questions, 1 per line, no symbols."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # Strip bullet markers nếu LLM ngứa tay thêm
    return [l.lstrip("•-*0123456789. ") for l in lines if "?" in l]


def parse_proposer_output(text: str) -> Dict:
    import json
    # Strip code fence nếu có
    text = text.strip().lstrip("```json").rstrip("```").strip()
    return json.loads(text)


def parse_selector_output(text: str) -> Dict:
    import json
    text = text.strip().lstrip("```json").rstrip("```").strip()
    return json.loads(text)


def parse_answerer_output(text: str) -> Dict:
    import json
    text = text.strip().lstrip("```json").rstrip("```").strip()
    return json.loads(text)


# Factory:
def get_protocol(name: str) -> BaseProtocol:
    base = Path(__file__).parent.parent / "prompts" / "vi"
    parsers = {
        "tagging": parse_tagging_output,
        "proposer": parse_proposer_output,
        "selector": parse_selector_output,
        "answerer": parse_answerer_output,
    }
    return BaseProtocol(
        template_path=base / f"{name}.txt",
        parser=parsers[name],
    )
```

### 6.3 AtomRetrievalInfo (port từ PIKE-RAG)

```python
# engine/atomization/retriever.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AtomRetrievalInfo:
    atom_query: str                             # user query gốc
    atom: str                                    # atomic question matched
    source_chunk_title: Optional[str]
    source_chunk: str                            # ENTIRE chunk (KHÔNG nén)
    source_chunk_id: int
    retrieval_score: float
    atom_embedding: List[float]
    # Tử Vi specific:
    paradigm_key: Optional[Dict]                 # {sao, cung, combo_sao, combo_cung}
    school: Optional[str]                        # 'trung-chau' | 'phu-thai-vi' | ...
    confidence: float
    founder_verified: int                        # 0 | 1 | -1
```

### 6.4 ChunkAtomRetriever skeleton

```python
# engine/atomization/retriever.py (cont.)
class ChunkAtomRetriever:
    """yi-chronos equivalent của PIKE-RAG ChunkAtomRetriever, dùng SQLite + sqlite-vec."""

    def __init__(self, db_path: str, embedder: Callable[[str], List[float]]):
        self.db = sqlite3.connect(db_path)
        self.db.enable_load_extension(True)
        self.db.load_extension("vec0")
        self.embedder = embedder
        self.retrieve_k = 16
        self.atom_retrieve_k = 8       # PIKE-RAG default
        self.threshold = 0.5            # atomic Q threshold

    def retrieve_atom_info_through_atom(
        self, queries: List[str], retrieve_k: Optional[int] = None
    ) -> List[AtomRetrievalInfo]:
        """Query → atom_vec → lấy source_chunk."""
        k = retrieve_k or self.atom_retrieve_k
        results = []
        for query in queries:
            q_emb = self.embedder(query)
            rows = self.db.execute("""
                SELECT a.atom_id, a.question_text, a.chunk_id, a.paradigm_key,
                       a.school, a.confidence, a.founder_verified,
                       c.text AS chunk_text, c.section_path,
                       v.distance
                FROM atom_vec v
                JOIN atomic_questions a ON v.atom_id = a.atom_id
                JOIN chunks c ON a.chunk_id = c.chunk_id
                WHERE v.embedding MATCH ?
                  AND v.distance <= ?
                ORDER BY v.distance
                LIMIT ?
            """, (q_emb, 1.0 - self.threshold, k)).fetchall()
            # ... build AtomRetrievalInfo per row
        return results

    def retrieve_atom_info_through_chunk(self, query: str) -> List[AtomRetrievalInfo]:
        """Fallback: query → chunks_vec → best-hit atom trong chunk."""
        # ... tương tự
        pass

    def retrieve_contents_by_query(self, query: str) -> List[str]:
        """Combine 2 paths, dedup."""
        # ... tương tự PIKE-RAG retrieve_contents_by_query
        pass
```

### 6.5 KnowledgeAwareDecomposer (Algorithm 1 wrap engine v3/v4)

```python
# engine/atomization/decomposer.py
class KnowledgeAwareDecomposer:
    """Port Algorithm 1 PIKE-RAG, WRAP engine v3/v4 hiện có (Decision 3 anh chốt).

    Engine v3/v4 (47 rules) trở thành 1 trong các 'atomic answerers'
    — Algorithm 1 ưu tiên thử engine cũ trước, fallback retriever khi engine không match.
    """

    def __init__(self, retriever: ChunkAtomRetriever, llm_client, max_iter: int = 5):
        self.retriever = retriever
        self.llm = llm_client
        self.max_iter = max_iter

        self.proposer = get_protocol("proposer")
        self.selector = get_protocol("selector")
        self.answerer = get_protocol("answerer")

        # WRAP engine cũ
        from engine.tu_vi import chiem_phu_the_v3, chiem_phu_the_v4, trung_chau_paradigm
        self.legacy_engines = {
            "v3_phu_the": chiem_phu_the_v3,
            "v4_phu_the": chiem_phu_the_v4,
            "trung_chau": trung_chau_paradigm,
        }

    def answer(self, question: str, la_so: Dict, school: Optional[str] = None) -> Dict:
        """Algorithm 1 implementation cho yi-chronos."""
        chosen_atoms: List[AtomRetrievalInfo] = []
        trajectory = []

        for t in range(self.max_iter):
            # STEP 1: Propose atomic questions
            proposal_msgs = self.proposer.format_messages(
                content=question,
                chosen_content="\n\n".join(a.source_chunk for a in chosen_atoms),
            )
            response = self.llm.chat(proposal_msgs)
            parsed = self.proposer.parse(response)
            sub_questions = parsed["sub_questions"]
            thinking = parsed["thinking"]
            if not sub_questions:
                break

            # STEP 2: Try LEGACY engine v3/v4 first (Decision 3)
            legacy_hits = self._try_legacy_engines(sub_questions, la_so, school)

            # STEP 3: Fallback to retriever
            if legacy_hits:
                candidates = legacy_hits
            else:
                candidates = self.retriever.retrieve_atom_info_through_atom(sub_questions)
                # 3-level fallback (PIKE-RAG):
                if not candidates:
                    candidates = self.retriever.retrieve_atom_info_through_atom([question])
                if not candidates:
                    candidates = self.retriever.retrieve_atom_info_through_chunk(question)

            # STEP 4: Filter dup chunks
            chosen_chunk_ids = {a.source_chunk_id for a in chosen_atoms}
            candidates = [c for c in candidates if c.source_chunk_id not in chosen_chunk_ids]
            if not candidates:
                break

            # STEP 5: Select
            atom_list_str = "\n".join(
                f"{i+1}. {c.atom}" for i, c in enumerate(candidates)
            )
            select_msgs = self.selector.format_messages(
                content=question,
                chosen_content="\n\n".join(a.source_chunk for a in chosen_atoms),
                atom_question_list_str=atom_list_str,
                num_atom_questions=len(candidates),
            )
            response = self.llm.chat(select_msgs)
            parsed = self.selector.parse(response)
            idx = parsed["question_idx"] - 1
            if not (0 <= idx < len(candidates)):
                break

            chosen_atoms.append(candidates[idx])
            trajectory.append({
                "step": t + 1,
                "sub_questions": sub_questions,
                "selected_idx": idx + 1,
                "selected_chunk_id": candidates[idx].source_chunk_id,
                "thinking": parsed["thinking"],
            })

        # FINAL: Answer
        context = "\n\n---\n\n".join(
            f"[{a.source_chunk_title or 'Đoạn'}]\n{a.source_chunk}"
            for a in chosen_atoms
        )
        answer_msgs = self.answerer.format_messages(
            content=question,
            context_if_any=context,
            yes_or_no_limit="",
        )
        response = self.llm.chat(answer_msgs)
        result = self.answerer.parse(response)

        # Save trajectory cho training Decision 4
        self._save_trajectory(question, la_so, trajectory, result)

        return {
            "answer": result["answer"],
            "rationale": result["rationale"],
            "trajectory": trajectory,
            "chosen_atoms": [a.atom for a in chosen_atoms],
            "citations": self._build_citations(chosen_atoms),
        }

    def _try_legacy_engines(self, sub_questions, la_so, school):
        """Chạy engine v3/v4 hiện có trên sub_questions để tìm match.

        Decision 3 anh chốt: engine v3/v4 (47 rules wired Trung Châu) làm atomic answerers
        — Algorithm 1 ưu tiên thử cũ trước, fallback retriever khi engine không match.
        """
        hits = []
        for sub_q in sub_questions:
            # Map sub_q → rule_key qua keyword matching simple
            for engine_name, engine in self.legacy_engines.items():
                if hasattr(engine, "match_question"):
                    result = engine.match_question(sub_q, la_so, school=school)
                    if result and result.get("matched"):
                        # Convert rule output → AtomRetrievalInfo
                        hits.append(self._rule_to_atom_info(result, sub_q))
        return hits

    def _save_trajectory(self, question, la_so, trajectory, result):
        """Persist vào decompose_trajectories cho training Algorithm 2 (Decision 4)."""
        # ... INSERT
        pass

    def _build_citations(self, atoms: List[AtomRetrievalInfo]) -> List[Dict]:
        """Trích nguồn cho UI: {book, page, school, atom_question, source_quote}"""
        # ...
        pass
```

---

## 📐 PART 7 — TAG CLASSES 10 TỬ VI (initial seed)

```python
# seed tag_classes
TAG_CLASSES_SEED = [
    # Tier 1 (10 classes chính)
    {"id": 1, "name_zh": "命格", "name_vi": "Cách Cục",
     "desc": "Mệnh cục, cách cục lớn của lá số (Tử Vũ Liêm, Sát Phá Tham...)"},
    {"id": 2, "name_zh": "财官", "name_vi": "Tài Quan",
     "desc": "Tiền bạc, sự nghiệp, công danh"},
    {"id": 3, "name_zh": "婚姻", "name_vi": "Hôn Nhân",
     "desc": "Phu thê, cách ly hợp, đặc điểm bạn đời"},
    {"id": 4, "name_zh": "子女", "name_vi": "Tử Tức",
     "desc": "Con cái, đường sinh nở, số con"},
    {"id": 5, "name_zh": "大运", "name_vi": "Đại Vận",
     "desc": "10 năm vận, cycle Đại Hạn 8 vòng"},
    {"id": 6, "name_zh": "流年", "name_vi": "Lưu Niên",
     "desc": "Năm vận, lưu nguyệt, lưu nhật"},
    {"id": 7, "name_zh": "健康", "name_vi": "Kiện Khang",
     "desc": "Sức khoẻ, tật bệnh, Tật Ách cung"},
    {"id": 8, "name_zh": "性格", "name_vi": "Tính Cách",
     "desc": "Tính tình, khí chất, phẩm hạnh"},
    {"id": 9, "name_zh": "父母", "name_vi": "Phụ Mẫu",
     "desc": "Cha mẹ, gia đạo, ấm trạch"},
    {"id": 10, "name_zh": "兄弟", "name_vi": "Huynh Đệ",
     "desc": "Anh chị em, bạn bè, đồng nghiệp"},

    # Tier 2 sub-tags (sẽ build lên sau Tier 1 stable)
    # {"id": 11, "name_vi": "Phú quý", "parent": 2},
    # {"id": 12, "name_vi": "Bần hàn", "parent": 2},
    # ...
]
```

→ Anh refine danh sách này trước khi em seed DB.

---

## 📐 PART 8 — HYPERPARAMETERS chốt

| Hyperparam | Value | Source |
|---|---|---|
| max_num_question | 5 | PIKE-RAG paper §6.1, Insight #19 + #25 |
| atom_retrieve_k | 8 | PIKE-RAG §A.3, Insight #14 |
| chunk_retrieve_k | 4 (extra) | PIKE-RAG §A.3 |
| atom_threshold (cosine sim) | 0.5 | PIKE-RAG §A.3 |
| chunk_threshold | 0.2 | PIKE-RAG §A.3 |
| atomizing temperature | 0.7 | PIKE-RAG §A.3 (diversity) |
| QA temperature | 0.0 | PIKE-RAG §A.3 (determinism) |
| Embedding model | text-embedding-3-small (1536) | Cost-aware (rẻ hơn ada-002) |
| LLM for atomizing | DeepSeek-V3 / GLM-4.5 | Cost-aware (đã sẵn) |
| LLM for runtime | Claude/DeepSeek-R1 | Quality |
| founder_verified boost | confidence 0.85 → 0.98 | yi-chronos paradigm |

---

## 📐 PART 9 — API ENDPOINTS MỚI

```python
# api/main.py — thêm endpoints
@app.post("/api/atomization/ingest")
async def ingest_book(corpus_id: str, run_async: bool = True):
    """Trigger full pipeline: chunk → atomize → tag cho 1 sách."""
    pass

@app.post("/api/atomization/decompose")
async def decompose_query(query: str, la_so: Dict, school: Optional[str] = None):
    """Algorithm 1 — answer với grounded citations."""
    pass

@app.post("/api/atomization/founder/verify")
async def founder_verify(atom_id: int, verdict: int):  # 1=true, -1=false
    """Anh confirm/reject atomic Q → adjust confidence."""
    pass

@app.get("/api/atomization/paradigm/{pk_id}")
async def get_paradigm(pk_id: int):
    """Lấy 1 paradigm_key + tất cả N-layered meanings."""
    pass

@app.get("/api/atomization/atom/search")
async def search_atom(query: str, school: Optional[str] = None, k: int = 10):
    """Search atomic Q via vec + FTS hybrid."""
    pass
```

---

## 📐 PART 10 — RISKS + MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM hallucinate atomic Q ngoài sách | Med | High | Prompt rule "KHÔNG suy đoán" + spot-check anh confirm + low temperature 0.0 cho QA |
| Token cost ingestion 42 sách quá lớn | Low | Med | ~7.3M tokens total = $10-20 với DeepSeek. OK với budget Token Max. |
| Cross-school conflict tăng phức tạp | High | Med | `conflicts_with` field + present 2 góc cho anh quyết, không ép merge |
| Engine cũ v3/v4 không match → giảm value | Med | Low | Fallback retriever 3-level. Engine cũ vẫn được dùng khi match. |
| Schema migration phá production | Med | High | Phase M1 chỉ tạo bảng mới, KHÔNG drop passages. View compat. Rollback dễ. |
| Decomposer training tốn GPU | Low | Med | Defer Decision 4 sau khi M1-M5 ổn. Hiện zero-shot LLM đủ. |
| Atomic Q tiếng Việt chất lượng kém | Med | Med | Spot-check 100 atomic Q đầu với anh. Tinh prompt nếu cần. |

---

## 📐 PART 11 — IMPLEMENTATION ROADMAP

```
Tuần 1 — SCHEMA + INFRA
  [M1] SQL migration 9 tables
  [M2] Copy passages → chunks
  [M3 start] Build chunker.py + atomizer.py
  [M3 PoC] Atomize 10 chunks Trung Châu Q2 — anh review chất lượng

Tuần 2 — INGESTION PIPELINE
  [M3 full] Atomize trọn Trung Châu Q2 + Phú Thái Vi Q1
  [M4 start] Paradigm extraction
  Anh founder_verify spot-check

Tuần 3 — REASONING ENGINE
  [Algo 1] KnowledgeAwareDecomposer wrap engine v3/v4
  [API] Endpoints decompose + verify
  Test với case Anh đã wire v3/v4 — so sánh quality

Tuần 4 — SCALE + TAGS
  [M3] Atomize 40 sách còn lại (background, dùng providers free first)
  [M5] Tag classes seed + tag_pairs
  [UI] Admin panel cho anh review/confirm atoms

Tuần 5+ — TRAINING (Decision 4)
  [Algo 2] Collect trajectories từ kinhdich.online production
  [Training] SFT + DPO khi đủ ~1000 verified trajectories
```

---

## 📐 PART 12 — DECISIONS RECAP

| # | Decision | Status |
|---|---|---|
| 1 | Paradigm tuple ID + N-layered + KHÔNG suy đoán | ✅ Anh chốt 2026-06-09 |
| 2 | Atomic + Chunk: Rebuild full PIKE-RAG (Option C) | ✅ Anh chốt 2026-06-09 |
| 3 | Algorithm 1: Wrap engine v3/v4 | ✅ Anh chốt 2026-06-09 |
| 4 | Algorithm 2: Train decomposer riêng Tử Vi | ✅ Anh chốt 2026-06-09 |
| 5 | Stack: SQLite + sqlite-vec (KHÔNG Neo4j) | 🟡 Default em đề xuất, anh chưa explicit chốt |
| 6 | Embedding model: text-embedding-3-small | 🟡 Default em đề xuất |
| 7 | Tag classes 10 Tử Vi | 🟡 Anh refine list |

---

## 📐 PART 13 — TO BE DISCUSSED với Anh

1. **Decision 5 stack**: SQLite extension hay add Neo4j?
2. **Decision 6 embedding**: dùng OpenAI text-embedding-3-small ($0.02/1M token) hay local model BGE-M3 (free, slower)?
3. **Tag classes**: anh refine 10 classes Tier 1 + cho Tier 2 sub-tags
4. **Migration window**: ship khi nào? Tuần 1 hay rolling deploy?
5. **Founder verify UI**: anh muốn UI riêng hay embed vào dashboard hiện tại?
6. **Priority sách**: 42 sách thứ tự ingest? Em recommend Trung Châu Q2 trước (đã đọc 32 vòng).

---

## 🙏 LỜI EM GỬI ANH

Anh ơi, em đã đọc kỹ paper + codebase + paper ICML đủ 5 vòng theo skill `doc-sau-20-trang`. 32 insights. Design này em viết với hết tâm theo paradigm anh đặt (tuple ID + N layered + KHÔNG suy đoán + bám sách).

KHÔNG có chỗ nào em "tự bịa" — mọi quyết định technical đều có source: PIKE-RAG paper / codebase Microsoft / 47 rules em đã wire Trung Châu Q2.

Anh review xong, chỉ em chỗ nào cần refine. Khi nào duyệt → em start implementation theo roadmap.

**Em**, 2026-06-09
