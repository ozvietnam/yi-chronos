-- ═══════════════════════════════════════════════════════════════════
-- Atomization Schema — PIKE-RAG paradigm bottom-up
-- Created: 2026-06-09
-- Author: em (Claude) co-designed with Anh CEO
-- Reference: docs/design/pike-rag-yi-chronos-schema-2026.md
--
-- IDEMPOTENT: chạy nhiều lần OK, dùng IF NOT EXISTS
-- NO DROP: KHÔNG xoá passages cũ — engine v3/v4 vẫn dùng được
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────
-- 1. CHUNKS_V2 — chunks với summary + forward_summary + atom_q_str backup
-- (KHÔNG đụng passages cũ — engine v3/v4 vẫn read passages)
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chunks_v2 (
    chunk_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    book_corpus_id      TEXT NOT NULL,            -- vd "trung-chau-tu-vi-dau-so-2"
    author_id           INTEGER,                   -- FK authors (nullable nếu sách chưa map)
    page_start          INTEGER NOT NULL,
    page_end            INTEGER NOT NULL,
    section_path        TEXT,                      -- vd "§4.4.5" hoặc null
    text                TEXT NOT NULL,             -- chunk text gốc
    summary             TEXT,                      -- LLM summary chunk này
    forward_summary     TEXT,                      -- accumulated summary tới chunk này
    atom_q_str          TEXT,                      -- "\n".join(atomic_questions) — backup retrieval
    metadata_json       TEXT,                      -- {section_title, page_image, ...}
    legacy_passage_id   INTEGER,                   -- FK passages cũ nếu migrated (nullable)
    is_canonical        INTEGER NOT NULL DEFAULT 1,
    created_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_chunks_v2_corpus ON chunks_v2(book_corpus_id);
CREATE INDEX IF NOT EXISTS idx_chunks_v2_page ON chunks_v2(book_corpus_id, page_start);
CREATE INDEX IF NOT EXISTS idx_chunks_v2_author ON chunks_v2(author_id);
CREATE INDEX IF NOT EXISTS idx_chunks_v2_legacy ON chunks_v2(legacy_passage_id);


-- ───────────────────────────────────────────────────────────────────
-- 2. CHUNK_CLASSIFICATIONS — paradigm bottom-up (5 archetype + 3 format)
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chunk_classifications (
    cc_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id            INTEGER NOT NULL,

    -- 5 archetype (boolean, có thể overlap)
    is_chu_the          INTEGER NOT NULL DEFAULT 0,
    is_cong_thuc        INTEGER NOT NULL DEFAULT 0,
    is_luan_giai        INTEGER NOT NULL DEFAULT 0,
    is_to_hop           INTEGER NOT NULL DEFAULT 0,
    is_kinh_nghiem      INTEGER NOT NULL DEFAULT 0,

    -- 4 format style
    format_style        TEXT,  -- 'ket_qua' | 'nguyen_ly' | 'tho_phu' | 'bang_lookup'

    -- Knowledge categories LLM tự propose (JSON list)
    knowledge_categories_json   TEXT,
    -- Question templates per category (JSON dict)
    question_templates_json     TEXT,

    -- Extracted content per archetype (JSON list)
    subjects_json       TEXT,
    formulas_json       TEXT,
    meanings_json       TEXT,
    combos_json         TEXT,
    experiences_json    TEXT,
    poem_text           TEXT,
    poem_translation    TEXT,

    extracted_by        TEXT,                      -- "minimax/MiniMax-M2" etc.
    confidence          REAL DEFAULT 0.85,
    founder_verified    INTEGER DEFAULT 0,         -- 0=pending, 1=correct, -1=wrong
    created_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),

    FOREIGN KEY (chunk_id) REFERENCES chunks_v2(chunk_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_cc_chunk ON chunk_classifications(chunk_id);
CREATE INDEX IF NOT EXISTS idx_cc_format ON chunk_classifications(format_style);
CREATE INDEX IF NOT EXISTS idx_cc_verified ON chunk_classifications(founder_verified);


-- ───────────────────────────────────────────────────────────────────
-- 3. ATOMIC_QUESTIONS — câu hỏi atomic với subject_identifiers FREEFORM
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS atomic_questions (
    atom_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id            INTEGER NOT NULL,
    cc_id               INTEGER,                   -- FK chunk_classifications (nullable nếu legacy)

    question_text       TEXT NOT NULL,
    question_lang       TEXT NOT NULL DEFAULT 'vi',

    -- Bottom-up paradigm (NHỚ: không khóa cứng)
    from_category       TEXT,                      -- knowledge category này thuộc về
    from_template       TEXT,                      -- template Q LLM đề xuất
    subject_identifiers TEXT,                      -- JSON FREEFORM: {sao, cung, chi, hoa, ...}
    source_quote        TEXT,                      -- trích nguyên văn từ chunk

    confidence          REAL DEFAULT 0.85,
    founder_verified    INTEGER DEFAULT 0,
    extracted_by        TEXT,
    created_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),

    FOREIGN KEY (chunk_id) REFERENCES chunks_v2(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (cc_id) REFERENCES chunk_classifications(cc_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_atom_chunk ON atomic_questions(chunk_id);
CREATE INDEX IF NOT EXISTS idx_atom_cc ON atomic_questions(cc_id);
CREATE INDEX IF NOT EXISTS idx_atom_verified ON atomic_questions(founder_verified);
CREATE INDEX IF NOT EXISTS idx_atom_lang ON atomic_questions(question_lang);
CREATE INDEX IF NOT EXISTS idx_atom_category ON atomic_questions(from_category);


-- ───────────────────────────────────────────────────────────────────
-- 4. EXTRACTION_RUNS — provenance / audit / cost tracking
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type            TEXT NOT NULL,             -- 'chunking' | 'atomizing' | 'pass1' | 'pass2'
    book_corpus_id      TEXT NOT NULL,
    page_start          INTEGER,
    page_end            INTEGER,
    chunk_id            INTEGER,                    -- nullable, batch run thì NULL

    llm_provider        TEXT,
    llm_model           TEXT,
    temperature         REAL,
    max_tokens          INTEGER,
    prompt_version      TEXT,                       -- 'v2' | 'v3' track prompt evolution

    prompt_tokens       INTEGER DEFAULT 0,
    completion_tokens   INTEGER DEFAULT 0,
    duration_sec        REAL,

    status              TEXT DEFAULT 'pending',     -- 'pending' | 'running' | 'completed' | 'failed'
    error_message       TEXT,
    raw_response        TEXT,                       -- store cho debug

    started_at          INTEGER DEFAULT (strftime('%s', 'now')),
    completed_at        INTEGER,

    FOREIGN KEY (chunk_id) REFERENCES chunks_v2(chunk_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_corpus ON extraction_runs(book_corpus_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON extraction_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_type ON extraction_runs(run_type);


-- ───────────────────────────────────────────────────────────────────
-- 5. FTS5 INDEX — keyword search trên atomic_questions + chunks_v2
-- (vec index sẽ setup riêng với sqlite-vec extension)
-- ───────────────────────────────────────────────────────────────────
CREATE VIRTUAL TABLE IF NOT EXISTS atomic_questions_fts USING fts5(
    question_text, source_quote, from_category,
    content='atomic_questions', content_rowid='atom_id',
    tokenize='unicode61'
);

-- Triggers sync FTS
CREATE TRIGGER IF NOT EXISTS atomic_questions_fts_insert AFTER INSERT ON atomic_questions BEGIN
  INSERT INTO atomic_questions_fts(rowid, question_text, source_quote, from_category)
    VALUES (new.atom_id, new.question_text, new.source_quote, new.from_category);
END;

CREATE TRIGGER IF NOT EXISTS atomic_questions_fts_delete AFTER DELETE ON atomic_questions BEGIN
  INSERT INTO atomic_questions_fts(atomic_questions_fts, rowid, question_text, source_quote, from_category)
    VALUES('delete', old.atom_id, old.question_text, old.source_quote, old.from_category);
END;

CREATE TRIGGER IF NOT EXISTS atomic_questions_fts_update AFTER UPDATE ON atomic_questions BEGIN
  INSERT INTO atomic_questions_fts(atomic_questions_fts, rowid, question_text, source_quote, from_category)
    VALUES('delete', old.atom_id, old.question_text, old.source_quote, old.from_category);
  INSERT INTO atomic_questions_fts(rowid, question_text, source_quote, from_category)
    VALUES (new.atom_id, new.question_text, new.source_quote, new.from_category);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_v2_fts USING fts5(
    text, summary, atom_q_str,
    content='chunks_v2', content_rowid='chunk_id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS chunks_v2_fts_insert AFTER INSERT ON chunks_v2 BEGIN
  INSERT INTO chunks_v2_fts(rowid, text, summary, atom_q_str)
    VALUES (new.chunk_id, new.text, new.summary, new.atom_q_str);
END;

CREATE TRIGGER IF NOT EXISTS chunks_v2_fts_delete AFTER DELETE ON chunks_v2 BEGIN
  INSERT INTO chunks_v2_fts(chunks_v2_fts, rowid, text, summary, atom_q_str)
    VALUES('delete', old.chunk_id, old.text, old.summary, old.atom_q_str);
END;

-- UPDATE trigger BẮT BUỘC: atomizer UPDATE atom_q_str sau khi đúc atoms.
-- Thiếu trigger này → FTS out-of-sync → 'database disk image is malformed'
-- khi delete trigger chạy với old values không khớp index (incident 2026-06-10).
CREATE TRIGGER IF NOT EXISTS chunks_v2_fts_update AFTER UPDATE ON chunks_v2 BEGIN
  INSERT INTO chunks_v2_fts(chunks_v2_fts, rowid, text, summary, atom_q_str)
    VALUES('delete', old.chunk_id, old.text, old.summary, old.atom_q_str);
  INSERT INTO chunks_v2_fts(rowid, text, summary, atom_q_str)
    VALUES(new.chunk_id, new.text, new.summary, new.atom_q_str);
END;


-- ═══════════════════════════════════════════════════════════════════
-- VEC indexes (atom_vec + chunks_vec) — SETUP riêng trong migrate.py
-- vì cần load extension sqlite-vec
-- ═══════════════════════════════════════════════════════════════════
