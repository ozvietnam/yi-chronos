"""YI-Wiki SQLite store — schema + CRUD.

Tables:
- authors       lineage hierarchy (Master + 5 tiers)
- works         books/treatises mapped to corpus_books
- passages      intact text excerpts (NOT fragments)
- methods       procedural how-to (Mai Hoa pp bốc, etc.)
- case_studies  historical applications by Master
- predictions   real divinations anh gieo qua wiki (tâm-aware)
- concept_index reverse lookup concept → passages
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Iterator, Optional

from engine.yi_wiki.models import (
    Author,
    CaseStudy,
    ConceptIndex,
    Method,
    Passage,
    Prediction,
    Work,
)

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_wiki" / "wiki.sqlite3"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_vi TEXT NOT NULL,
    name_zh TEXT,
    tier_in_lineage INTEGER NOT NULL,
    era TEXT,
    birth_year INTEGER,
    death_year INTEGER,
    worldview_school TEXT,
    foundational_axioms TEXT,
    hermeneutic_style TEXT,
    works TEXT,
    bio_summary TEXT,
    teachers TEXT,
    disciples TEXT,
    created_at INTEGER NOT NULL,
    UNIQUE(name_vi, name_zh, tier_in_lineage)
);

CREATE TABLE IF NOT EXISTS works (
    work_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title_vi TEXT NOT NULL,
    title_zh TEXT,
    year_composed INTEGER,
    role TEXT,
    corpus_id TEXT,
    is_canonical INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
CREATE INDEX IF NOT EXISTS idx_works_author ON works(author_id);
CREATE INDEX IF NOT EXISTS idx_works_corpus ON works(corpus_id);

CREATE TABLE IF NOT EXISTS passages (
    passage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    corpus_id TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    raw_text TEXT NOT NULL,
    topic TEXT,
    summary_50w TEXT,
    concepts_mentioned TEXT,
    related_passages TEXT,
    is_canonical INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
CREATE INDEX IF NOT EXISTS idx_passages_author ON passages(author_id);
CREATE INDEX IF NOT EXISTS idx_passages_corpus ON passages(corpus_id);

CREATE TABLE IF NOT EXISTS methods (
    method_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    name_vi TEXT NOT NULL,
    name_zh TEXT,
    domain TEXT,
    inputs_required TEXT,
    procedure_steps TEXT,
    output_format TEXT,
    source_passages TEXT,
    derived_from TEXT,
    case_studies TEXT,
    confidence_baseline REAL DEFAULT 0,
    notes TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    UNIQUE(name_zh, author_id)
);
CREATE INDEX IF NOT EXISTS idx_methods_author ON methods(author_id);

CREATE TABLE IF NOT EXISTS case_studies (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_id INTEGER NOT NULL,
    historical_event TEXT,
    inputs_recorded TEXT,
    output_predicted TEXT,
    output_actual TEXT,
    accuracy_score REAL DEFAULT 0,
    source_book TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (method_id) REFERENCES methods(method_id)
);

CREATE TABLE IF NOT EXISTS predictions (
    pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    user_intent TEXT,
    user_context TEXT,
    interaction_log TEXT,
    tam_note TEXT,
    method_chain TEXT,
    consultants_invoked TEXT,
    predicted_outcome TEXT,
    predicted_timing TEXT,
    review_reminder_at INTEGER,
    actual_outcome TEXT,
    learning_notes TEXT,
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_predictions_ts ON predictions(timestamp);

CREATE TABLE IF NOT EXISTS concept_index (
    concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_vi TEXT NOT NULL,
    canonical_zh TEXT,
    aliases TEXT,
    mentioned_in_passages TEXT,
    short_note TEXT,
    first_seen_corpus TEXT,
    first_seen_page INTEGER,
    category TEXT,
    corpora TEXT,
    school TEXT,
    created_at INTEGER NOT NULL,
    UNIQUE(canonical_zh, canonical_vi)
);
CREATE INDEX IF NOT EXISTS idx_concept_vi ON concept_index(canonical_vi);
CREATE INDEX IF NOT EXISTS idx_concept_zh ON concept_index(canonical_zh);

CREATE TABLE IF NOT EXISTS _meta (key TEXT PRIMARY KEY, value TEXT);

-- FTS5 full-text search (#18 Phase 1): un-deads the `passages` corpus + upgrades
-- concept search from LIKE → ranked bm25. External-content tables mirror the base
-- tables; kept in sync by triggers below + backfilled in _migrate for existing DBs.
CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(
    raw_text, topic, summary_50w, concepts_mentioned,
    content='passages', content_rowid='passage_id', tokenize='unicode61'
);
CREATE TRIGGER IF NOT EXISTS passages_ai AFTER INSERT ON passages BEGIN
  INSERT INTO passages_fts(rowid, raw_text, topic, summary_50w, concepts_mentioned)
    VALUES (new.passage_id, new.raw_text, new.topic, new.summary_50w, new.concepts_mentioned);
END;
CREATE TRIGGER IF NOT EXISTS passages_ad AFTER DELETE ON passages BEGIN
  INSERT INTO passages_fts(passages_fts, rowid, raw_text, topic, summary_50w, concepts_mentioned)
    VALUES ('delete', old.passage_id, old.raw_text, old.topic, old.summary_50w, old.concepts_mentioned);
END;
CREATE TRIGGER IF NOT EXISTS passages_au AFTER UPDATE ON passages BEGIN
  INSERT INTO passages_fts(passages_fts, rowid, raw_text, topic, summary_50w, concepts_mentioned)
    VALUES ('delete', old.passage_id, old.raw_text, old.topic, old.summary_50w, old.concepts_mentioned);
  INSERT INTO passages_fts(rowid, raw_text, topic, summary_50w, concepts_mentioned)
    VALUES (new.passage_id, new.raw_text, new.topic, new.summary_50w, new.concepts_mentioned);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS concept_fts USING fts5(
    canonical_vi, canonical_zh, aliases, short_note,
    content='concept_index', content_rowid='concept_id', tokenize='unicode61'
);
CREATE TRIGGER IF NOT EXISTS concept_ai AFTER INSERT ON concept_index BEGIN
  INSERT INTO concept_fts(rowid, canonical_vi, canonical_zh, aliases, short_note)
    VALUES (new.concept_id, new.canonical_vi, new.canonical_zh, new.aliases, new.short_note);
END;
CREATE TRIGGER IF NOT EXISTS concept_ad AFTER DELETE ON concept_index BEGIN
  INSERT INTO concept_fts(concept_fts, rowid, canonical_vi, canonical_zh, aliases, short_note)
    VALUES ('delete', old.concept_id, old.canonical_vi, old.canonical_zh, old.aliases, old.short_note);
END;
CREATE TRIGGER IF NOT EXISTS concept_au AFTER UPDATE ON concept_index BEGIN
  INSERT INTO concept_fts(concept_fts, rowid, canonical_vi, canonical_zh, aliases, short_note)
    VALUES ('delete', old.concept_id, old.canonical_vi, old.canonical_zh, old.aliases, old.short_note);
  INSERT INTO concept_fts(rowid, canonical_vi, canonical_zh, aliases, short_note)
    VALUES (new.concept_id, new.canonical_vi, new.canonical_zh, new.aliases, new.short_note);
END;
"""


def _now() -> int:
    return int(time.time())


def _enc(obj):
    """Encode list/dict → JSON string for SQLite."""
    if obj is None:
        return None
    if isinstance(obj, (list, dict)):
        return json.dumps(obj, ensure_ascii=False)
    return obj


def _dec(s, default=None):
    if not s:
        return default
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default


class WikiStore:
    def __init__(self, db_path: Path | str = _DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(_SCHEMA)
            self._migrate(conn)
            conn.commit()

    def _migrate(self, conn) -> None:
        """Idempotent migrations — keep store.py the single source of truth for
        schema and bring older DBs up to date (issue #19: category/corpora/school
        were used by extractors + queries but missing from the canonical schema)."""
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(concept_index)").fetchall()}
        except sqlite3.Error:
            return
        for col, col_def in (("category", "TEXT"), ("corpora", "TEXT"), ("school", "TEXT")):
            if col not in cols:
                try:
                    conn.execute(f"ALTER TABLE concept_index ADD COLUMN {col} {col_def}")
                except sqlite3.Error:
                    pass  # already added by a parallel run

        # FTS5 backfill (#18) — index rows that existed BEFORE the FTS tables were
        # added (triggers only catch new writes). External-content FTS5 must be
        # backfilled with the 'rebuild' command, and `count(*) FROM fts` reflects the
        # CONTENT table (never 0 when it has rows) — so guard with a one-time _meta flag.
        try:
            done = conn.execute(
                "SELECT value FROM _meta WHERE key='fts_backfilled_v1'"
            ).fetchone()
            if not done:
                for fts in ("passages_fts", "concept_fts"):
                    try:
                        conn.execute(f"INSERT INTO {fts}({fts}) VALUES('rebuild')")
                    except sqlite3.Error:
                        pass
                conn.execute(
                    "INSERT OR REPLACE INTO _meta(key, value) VALUES('fts_backfilled_v1', '1')"
                )
        except sqlite3.Error:
            pass

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Load sqlite-vec if present (#18 vector search). Optional: hosts without it
        # (e.g. prod) just use FTS5 — the vector path is only taken when both the
        # extension AND an embedder are available.
        try:
            import sqlite_vec

            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
        except Exception:
            pass
        finally:
            try:
                conn.enable_load_extension(False)
            except Exception:
                pass
        try:
            yield conn
        finally:
            conn.close()

    # ─── Authors ───────────────────────────────────────────────────────────
    def upsert_author(self, a: Author) -> int:
        a.created_at = a.created_at or _now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO authors
                (name_vi, name_zh, tier_in_lineage, era, birth_year, death_year,
                 worldview_school, foundational_axioms, hermeneutic_style, works,
                 bio_summary, teachers, disciples, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(name_vi, name_zh, tier_in_lineage) DO UPDATE SET
                    name_vi=excluded.name_vi,
                    era=excluded.era,
                    birth_year=excluded.birth_year,
                    death_year=excluded.death_year,
                    worldview_school=excluded.worldview_school,
                    foundational_axioms=excluded.foundational_axioms,
                    hermeneutic_style=excluded.hermeneutic_style,
                    bio_summary=excluded.bio_summary
                RETURNING author_id""",
                (
                    a.name_vi, a.name_zh, a.tier_in_lineage, a.era,
                    a.birth_year, a.death_year, a.worldview_school,
                    _enc(a.foundational_axioms), a.hermeneutic_style,
                    _enc(a.works), a.bio_summary,
                    _enc(a.teachers), _enc(a.disciples), a.created_at,
                ),
            )
            aid = cur.fetchone()[0]
            conn.commit()
            return aid

    def get_author(self, author_id: int) -> Optional[Author]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM authors WHERE author_id=?", (author_id,)
            ).fetchone()
        if not row:
            return None
        return Author(
            author_id=row["author_id"],
            name_vi=row["name_vi"],
            name_zh=row["name_zh"] or "",
            tier_in_lineage=row["tier_in_lineage"],
            era=row["era"] or "",
            birth_year=row["birth_year"],
            death_year=row["death_year"],
            worldview_school=row["worldview_school"] or "",
            foundational_axioms=_dec(row["foundational_axioms"], []),
            hermeneutic_style=row["hermeneutic_style"] or "",
            works=_dec(row["works"], []),
            bio_summary=row["bio_summary"] or "",
            teachers=_dec(row["teachers"], []),
            disciples=_dec(row["disciples"], []),
            created_at=row["created_at"],
        )

    def list_authors(self) -> list[Author]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM authors ORDER BY tier_in_lineage, birth_year"
            ).fetchall()
        return [self.get_author(r["author_id"]) for r in rows]

    # ─── Works ─────────────────────────────────────────────────────────────
    def upsert_work(self, w: Work) -> int:
        w.created_at = w.created_at or _now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO works
                (author_id, title_vi, title_zh, year_composed, role, corpus_id,
                 is_canonical, notes, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                RETURNING work_id""",
                (w.author_id, w.title_vi, w.title_zh, w.year_composed, w.role,
                 w.corpus_id, int(w.is_canonical), w.notes, w.created_at),
            )
            wid = cur.fetchone()[0]
            conn.commit()
            return wid

    def list_works(self, author_id: Optional[int] = None) -> list[dict]:
        sql = "SELECT * FROM works"
        params: tuple = ()
        if author_id:
            sql += " WHERE author_id=?"
            params = (author_id,)
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    # ─── Methods ───────────────────────────────────────────────────────────
    def upsert_method(self, m: Method) -> int:
        m.created_at = m.created_at or _now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO methods
                (author_id, name_vi, name_zh, domain, inputs_required,
                 procedure_steps, output_format, source_passages, derived_from,
                 case_studies, confidence_baseline, notes, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(name_zh, author_id) DO UPDATE SET
                    name_vi=excluded.name_vi,
                    domain=excluded.domain,
                    inputs_required=excluded.inputs_required,
                    procedure_steps=excluded.procedure_steps,
                    notes=excluded.notes
                RETURNING method_id""",
                (m.author_id, m.name_vi, m.name_zh, m.domain,
                 _enc(m.inputs_required), _enc(m.procedure_steps),
                 m.output_format, _enc(m.source_passages),
                 _enc(m.derived_from), _enc(m.case_studies),
                 m.confidence_baseline, m.notes, m.created_at),
            )
            mid = cur.fetchone()[0]
            conn.commit()
            return mid

    def list_methods(self, author_id: Optional[int] = None) -> list[dict]:
        sql = "SELECT * FROM methods"
        params: tuple = ()
        if author_id:
            sql += " WHERE author_id=?"
            params = (author_id,)
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    # ─── Passages ──────────────────────────────────────────────────────────
    def insert_passage(self, p: Passage) -> int:
        p.created_at = p.created_at or _now()
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO passages
                (author_id, corpus_id, page_start, page_end, raw_text, topic,
                 summary_50w, concepts_mentioned, related_passages, is_canonical,
                 created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                RETURNING passage_id""",
                (p.author_id, p.corpus_id, p.page_start, p.page_end, p.raw_text,
                 p.topic, p.summary_50w, _enc(p.concepts_mentioned),
                 _enc(p.related_passages), int(p.is_canonical), p.created_at),
            )
            pid = cur.fetchone()[0]
            conn.commit()
            return pid

    def list_passages(self, author_id: Optional[int] = None,
                      corpus_id: Optional[str] = None) -> list[dict]:
        sql = "SELECT * FROM passages WHERE 1=1"
        params: list = []
        if author_id:
            sql += " AND author_id=?"
            params.append(author_id)
        if corpus_id:
            sql += " AND corpus_id=?"
            params.append(corpus_id)
        sql += " ORDER BY corpus_id, page_start"
        with self._conn() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]

    # ─── Full-text search (FTS5 — #18 Phase 1) ──────────────────────────────
    @staticmethod
    def _fts_query(text: str) -> str:
        """Turn free text into a safe FTS5 OR-query (quote each token, drop FTS
        operators) so user input never triggers a syntax error."""
        toks = re.findall(r"\w+", text or "", flags=re.UNICODE)
        return " OR ".join(f'"{t}"' for t in toks if len(t) > 1)

    def search_passages(self, query: str, limit: int = 8,
                        corpus_id: Optional[str] = None) -> list[dict]:
        """Rank passages by FTS5 bm25 (un-deads the restored-book corpus). Returns
        the matched passage rows (best first). Empty query → []."""
        match = self._fts_query(query)
        if not match:
            return []
        sql = (
            "SELECT p.* FROM passages p "
            "JOIN passages_fts f ON p.passage_id = f.rowid "
            "WHERE passages_fts MATCH ?"
        )
        params: list = [match]
        if corpus_id:
            sql += " AND p.corpus_id = ?"
            params.append(corpus_id)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            try:
                rows = conn.execute(sql, tuple(params)).fetchall()
            except sqlite3.OperationalError:
                like = f"%{query}%"
                rows = conn.execute(
                    "SELECT * FROM passages WHERE raw_text LIKE ? OR topic LIKE ? "
                    "LIMIT ?", (like, like, limit),
                ).fetchall()
        return [dict(r) for r in rows]

    def search_concepts(self, query: str, limit: int = 20) -> list[dict]:
        """Rank concepts by FTS5 bm25 (replaces LIKE substring search)."""
        match = self._fts_query(query)
        if not match:
            return []
        with self._conn() as conn:
            try:
                rows = conn.execute(
                    "SELECT c.* FROM concept_index c "
                    "JOIN concept_fts f ON c.concept_id = f.rowid "
                    "WHERE concept_fts MATCH ? ORDER BY rank LIMIT ?",
                    (match, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                like = f"%{query}%"
                rows = conn.execute(
                    "SELECT * FROM concept_index WHERE canonical_vi LIKE ? "
                    "OR aliases LIKE ? OR short_note LIKE ? LIMIT ?",
                    (like, like, like, limit),
                ).fetchall()
        return [dict(r) for r in rows]

    # ─── Vector search (sqlite-vec + LM Studio embeddings — #18 Phase 2) ─────
    @staticmethod
    def _vec_available(conn) -> bool:
        try:
            conn.execute("SELECT vec_version()").fetchone()
            return True
        except sqlite3.Error:
            return False

    def ensure_vec_table(self, conn) -> bool:
        """Create the passages_vec vec0 table if sqlite-vec is loaded. Returns
        True if the vector table is usable."""
        if not self._vec_available(conn):
            return False
        from .embeddings import EMBED_DIM
        try:
            conn.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS passages_vec "
                f"USING vec0(passage_id INTEGER PRIMARY KEY, embedding FLOAT[{EMBED_DIM}])"
            )
            return True
        except sqlite3.Error:
            return False

    def backfill_embeddings(self, batch: int = 64, limit: int | None = None) -> dict:
        """Embed passages that lack a vector (via the configured embedder) and store
        them in passages_vec. One-time/local op (needs an embedder, e.g. LM Studio).
        Idempotent: only embeds passages not already in passages_vec."""
        from .embeddings import embed_texts, is_available
        if not is_available():
            return {"status": "no_embedder", "embedded": 0}
        with self._conn() as conn:
            if not self.ensure_vec_table(conn):
                return {"status": "no_sqlite_vec", "embedded": 0}
            sql = (
                "SELECT p.passage_id, p.raw_text FROM passages p "
                "LEFT JOIN passages_vec v ON v.passage_id = p.passage_id "
                "WHERE v.passage_id IS NULL AND p.raw_text != '' ORDER BY p.passage_id"
            )
            if limit:
                sql += f" LIMIT {int(limit)}"
            todo = conn.execute(sql).fetchall()
            done = 0
            for i in range(0, len(todo), batch):
                chunk = todo[i:i + batch]
                vecs = embed_texts([r["raw_text"][:2000] for r in chunk])
                if not vecs:
                    break
                for row, vec in zip(chunk, vecs):
                    conn.execute(
                        "INSERT OR REPLACE INTO passages_vec(passage_id, embedding) VALUES (?, ?)",
                        (row["passage_id"], json.dumps(vec)),
                    )
                conn.commit()
                done += len(chunk)
        return {"status": "ok", "embedded": done, "remaining": len(todo) - done}

    def search_passages_hybrid(self, query: str, limit: int = 8,
                               corpus_id: Optional[str] = None, k_rrf: int = 60) -> list[dict]:
        """Hybrid retrieval: FTS5 (bm25) + vector KNN fused with Reciprocal Rank
        Fusion. Falls back to FTS5-only when no embedder / no sqlite-vec / no
        vectors (e.g. on the prod VPS)."""
        fts_hits = self.search_passages(query, limit=limit * 2, corpus_id=corpus_id)
        # Vector leg — only if embedder + sqlite-vec + vectors are all present.
        vec_ids: list[int] = []
        try:
            from .embeddings import embed_one
            qvec = embed_one(query)
            if qvec is not None:
                with self._conn() as conn:
                    if self._vec_available(conn):
                        rows = conn.execute(
                            "SELECT passage_id FROM passages_vec "
                            "WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
                            (json.dumps(qvec), limit * 2),
                        ).fetchall()
                        vec_ids = [r["passage_id"] for r in rows]
        except sqlite3.Error:
            vec_ids = []
        except Exception:
            vec_ids = []
        if not vec_ids:
            return fts_hits[:limit]
        # RRF fuse: score = Σ 1/(k + rank) across both rankings.
        scores: dict[int, float] = {}
        fts_ids = [h["passage_id"] for h in fts_hits]
        for rank, pid in enumerate(fts_ids):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k_rrf + rank + 1)
        for rank, pid in enumerate(vec_ids):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k_rrf + rank + 1)
        top_ids = sorted(scores, key=lambda p: scores[p], reverse=True)[:limit]
        by_id = {h["passage_id"]: h for h in fts_hits}
        missing = [pid for pid in top_ids if pid not in by_id]
        if missing:
            with self._conn() as conn:
                qs = ",".join("?" * len(missing))
                for r in conn.execute(
                    f"SELECT * FROM passages WHERE passage_id IN ({qs})", tuple(missing)
                ).fetchall():
                    by_id[r["passage_id"]] = dict(r)
        return [by_id[pid] for pid in top_ids if pid in by_id]

    # ─── Concept index ─────────────────────────────────────────────────────
    def upsert_concept(self, c: ConceptIndex) -> int:
        c.created_at = c.created_at or _now()
        with self._conn() as conn:
            # Dedup by canonical_vi (a concept is identified by its Vietnamese name),
            # NOT by the (canonical_zh, canonical_vi) pair — otherwise the auto-extractor
            # stub ("", "Cự Môn") and a later manual ("巨門", "Cự Môn") become 2 rows (#19).
            existing = conn.execute(
                "SELECT concept_id, canonical_zh FROM concept_index WHERE canonical_vi=?",
                (c.canonical_vi,),
            ).fetchone()
            if existing:
                cid = existing["concept_id"]
                new_zh = c.canonical_zh or existing["canonical_zh"] or ""
                try:
                    conn.execute(
                        """UPDATE concept_index
                           SET canonical_zh=?, aliases=?,
                               short_note=COALESCE(?, short_note)
                           WHERE concept_id=?""",
                        (new_zh, _enc(c.aliases), c.short_note, cid),
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    # A row with the enriched (zh, vi) pair already exists — keep the
                    # existing match rather than creating/duplicating.
                    pass
                return cid
            cur = conn.execute(
                """INSERT INTO concept_index
                (canonical_vi, canonical_zh, aliases, mentioned_in_passages,
                 short_note, first_seen_corpus, first_seen_page, created_at)
                VALUES (?,?,?,?,?,?,?,?)
                RETURNING concept_id""",
                (c.canonical_vi, c.canonical_zh, _enc(c.aliases),
                 _enc(c.mentioned_in_passages), c.short_note,
                 c.first_seen_corpus, c.first_seen_page, c.created_at),
            )
            cid = cur.fetchone()[0]
            conn.commit()
            return cid

    def list_concepts(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM concept_index ORDER BY canonical_vi"
            ).fetchall()
        return [dict(r) for r in rows]

    def append_concept_passage(self, concept_id: int, passage_id: int):
        """Append passage_id to concept's mentioned_in_passages list."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT mentioned_in_passages FROM concept_index WHERE concept_id=?",
                (concept_id,),
            ).fetchone()
            if not row:
                return
            current = _dec(row["mentioned_in_passages"], [])
            if passage_id not in current:
                current.append(passage_id)
                conn.execute(
                    "UPDATE concept_index SET mentioned_in_passages=? WHERE concept_id=?",
                    (_enc(current), concept_id),
                )
                conn.commit()

    # ─── Stats ─────────────────────────────────────────────────────────────
    def stats(self) -> dict:
        with self._conn() as conn:
            return {
                "authors": conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0],
                "works": conn.execute("SELECT COUNT(*) FROM works").fetchone()[0],
                "passages": conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0],
                "methods": conn.execute("SELECT COUNT(*) FROM methods").fetchone()[0],
                "case_studies": conn.execute("SELECT COUNT(*) FROM case_studies").fetchone()[0],
                "predictions": conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0],
                "concepts": conn.execute("SELECT COUNT(*) FROM concept_index").fetchone()[0],
            }


_store: Optional[WikiStore] = None


def get_store() -> WikiStore:
    global _store
    if _store is None:
        _store = WikiStore()
    return _store
