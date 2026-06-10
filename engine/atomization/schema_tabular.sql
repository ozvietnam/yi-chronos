-- ═══════════════════════════════════════════════════════════════════
-- Tabular Verses — kiến thức dạng BẢNG TRA (PIKE-RAG G_dk: tabular)
-- Created: 2026-06-10 — cho sách công cụ tra số (Thiết Bản Thần Số,
-- Khổng Minh Thần Toán, ...). KHÔNG atomize Q&A loại nội dung này:
-- phép dùng sách = tra theo KHÓA SỐ, không phải hỏi-đáp ngữ nghĩa.
--
-- IDEMPOTENT. Đủ bộ trigger insert/delete/UPDATE (incident 2026-06-10:
-- thiếu update trigger → FTS malformed).
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS tabular_verses (
    verse_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    book_corpus_id  TEXT NOT NULL,             -- vd 'thiet-ban-than-so'
    volume          TEXT,                       -- tập: 子集, 丑集, ... (nếu detect được)
    seq_no          INTEGER,                    -- số điều TUYỆT ĐỐI (1..~12000)
    seq_in_block    INTEGER,                    -- 1-10 vị trí trong block
    seq_confidence  TEXT NOT NULL DEFAULT 'counted',
                    -- 'anchored'  = block có anchor số đầy đủ đọc được
                    -- 'counted'   = suy từ đếm tích lũy (anchor unreadable)
                    -- 'uncertain' = counter vs anchor mismatch, cần người soát
    age_marks_raw   TEXT,                       -- cột số nhỏ (tuổi ứng) NGUYÊN VĂN OCR
    zh              TEXT NOT NULL,              -- lời đoán nguyên văn
    vi              TEXT,                       -- bản dịch (per-line translations)
    page_pdf        INTEGER,                    -- trang PDF nguồn
    line_ref        TEXT,                       -- vd 'p0107:r001-l003' truy ngược layout
    note            TEXT,                       -- ghi chú parser (wrap-joined, mismatch...)
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_verses_book_seq ON tabular_verses(book_corpus_id, seq_no);
CREATE INDEX IF NOT EXISTS idx_verses_book_page ON tabular_verses(book_corpus_id, page_pdf);

CREATE VIRTUAL TABLE IF NOT EXISTS tabular_verses_fts USING fts5(
    zh, vi,
    content='tabular_verses', content_rowid='verse_id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS tabular_verses_fts_insert AFTER INSERT ON tabular_verses BEGIN
  INSERT INTO tabular_verses_fts(rowid, zh, vi) VALUES (new.verse_id, new.zh, new.vi);
END;

CREATE TRIGGER IF NOT EXISTS tabular_verses_fts_delete AFTER DELETE ON tabular_verses BEGIN
  INSERT INTO tabular_verses_fts(tabular_verses_fts, rowid, zh, vi)
    VALUES('delete', old.verse_id, old.zh, old.vi);
END;

CREATE TRIGGER IF NOT EXISTS tabular_verses_fts_update AFTER UPDATE ON tabular_verses BEGIN
  INSERT INTO tabular_verses_fts(tabular_verses_fts, rowid, zh, vi)
    VALUES('delete', old.verse_id, old.zh, old.vi);
  INSERT INTO tabular_verses_fts(rowid, zh, vi) VALUES (new.verse_id, new.zh, new.vi);
END;
