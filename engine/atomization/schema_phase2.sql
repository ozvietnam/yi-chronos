-- ═══════════════════════════════════════════════════════════════════
-- Phase 2 Schema — atom_commentaries + atom_relations
-- Created: 2026-06-09 (sau MVP Phase 1 ingest 894 chunks)
-- Anh chốt: A + C, B default
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────
-- atom_commentaries — chú giải chi tiết per atom (Việt thuần + ví dụ)
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS atom_commentaries (
    commentary_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    atom_id             INTEGER NOT NULL UNIQUE,

    -- 4 lớp chú giải (mỗi field độc lập, có thể NULL nếu LLM không gen được lớp đó)
    han_viet_explain    TEXT,       -- giải nghĩa từng từ Hán-Việt cốt
    viet_thuan          TEXT,       -- diễn giải Việt thuần dễ hiểu cho user thường
    nguyen_ly           TEXT,       -- giải nguyên lý vận hành (KHI nào áp, TẠI sao)
    vi_du_doi_song      TEXT,       -- ví dụ cụ thể tình huống đời sống

    -- Cross-school perspectives (nếu sách khác có quan điểm)
    cross_school_notes  TEXT,       -- JSON list: [{school, note, source_book, source_page}]

    -- Cảnh báo paradigm Iron Rule #6 (KHÔNG predict cứng)
    iron_rule_warning   TEXT,       -- text cảnh báo nếu atom dễ bị hiểu sai thành predict

    extracted_by        TEXT,
    confidence          REAL DEFAULT 0.85,
    founder_verified    INTEGER DEFAULT 0,
    created_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),

    FOREIGN KEY (atom_id) REFERENCES atomic_questions(atom_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_commentary_atom ON atom_commentaries(atom_id);
CREATE INDEX IF NOT EXISTS idx_commentary_verified ON atom_commentaries(founder_verified);

-- FTS cho commentaries
CREATE VIRTUAL TABLE IF NOT EXISTS atom_commentaries_fts USING fts5(
    han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song,
    content='atom_commentaries', content_rowid='commentary_id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS atom_commentaries_fts_insert AFTER INSERT ON atom_commentaries BEGIN
  INSERT INTO atom_commentaries_fts(rowid, han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song)
    VALUES (new.commentary_id, new.han_viet_explain, new.viet_thuan, new.nguyen_ly, new.vi_du_doi_song);
END;


-- ───────────────────────────────────────────────────────────────────
-- atom_relations — cross-atom graph link (atom A → atom B)
-- ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS atom_relations (
    rel_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    from_atom_id        INTEGER NOT NULL,
    to_atom_id          INTEGER NOT NULL,

    -- Loại quan hệ
    relation_type       TEXT NOT NULL,
    -- 'luan_giai_them'      : atom B là luận giải sâu thêm cho atom A
    -- 'cong_thuc_apdung'    : atom B là công thức áp dụng cho atom A
    -- 'kinh_nghiem_apdung'  : atom B là kinh nghiệm khi gặp atom A
    -- 'trai_nghia'          : atom B nói ngược với atom A (cảnh báo)
    -- 'cach_cuc_lien_quan'  : atom B nói về cách cục liên quan
    -- 'cross_school'        : atom B từ school khác về cùng chủ đề

    rationale           TEXT,       -- LLM explain tại sao có quan hệ này
    confidence          REAL DEFAULT 0.7,
    founder_verified    INTEGER DEFAULT 0,
    extracted_by        TEXT,
    created_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),

    UNIQUE(from_atom_id, to_atom_id, relation_type),
    FOREIGN KEY (from_atom_id) REFERENCES atomic_questions(atom_id) ON DELETE CASCADE,
    FOREIGN KEY (to_atom_id) REFERENCES atomic_questions(atom_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_rel_from ON atom_relations(from_atom_id);
CREATE INDEX IF NOT EXISTS idx_rel_to ON atom_relations(to_atom_id);
CREATE INDEX IF NOT EXISTS idx_rel_type ON atom_relations(relation_type);
