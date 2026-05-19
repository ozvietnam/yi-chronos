"""YI-Lexicon SQLite store — schema + CRUD.

Tables:
- concepts            atomic symbols (token-level)
- mappings            concept → cosmology dimension (bat_quai/ngu_hanh/...)
- contextual_meanings composite phrases ("lá rơi mùa hạ" → meaning)
- corpora             source books/texts ingested via LLM
- distill_queue       LLM-proposed items, anh review (YOLO auto-accept)
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_lexicon" / "lexicon.sqlite3"


# ─── Dimensions enumerated (extensible) ──────────────────────────────────────

DIM_TYPES: tuple[str, ...] = (
    "bat_quai",         # 8 trigrams (Càn, Khôn, Đoài, ...)
    "ngu_hanh",         # 5 elements (mộc, hỏa, thổ, kim, thủy)
    "am_duong",         # yin / yang
    "thien_can",        # 10 stems
    "dia_chi",          # 12 branches
    "tiet_khi",         # 24 solar terms
    "hexagram",         # 64 hexagrams (Quẻ)
    "thap_than",        # 10 god types (Bát Tự)
    "than_sat",         # auxiliary stars
    "cung_tu_vi",       # 12 palaces (Tử Vi)
    "huong",            # direction (Bắc / Nam / Đông / ...)
    "mua",              # season
    "tang_phu",         # organs/body parts
    "thoi",             # generic time/period
    "khac",             # other / freeform
)

CONCEPT_TYPES: tuple[str, ...] = (
    "object",           # vật cụ thể: lá, hoa, đá, sách, xe
    "phenomenon",       # hiện tượng: rơi, vỡ, bay, sáng, mưa
    "color",            # màu: đỏ, vàng, trắng, đen, xanh
    "number",           # số: 1, 2, 3, ...
    "action",           # hành động: đi, đến, hợp, tan
    "relation",         # quan hệ: bố, mẹ, vợ, sếp
    "time",             # thời gian: 9h, sáng, mùa hạ
    "place",            # không gian: nhà, văn phòng, ngã tư
    "concept",          # trừu tượng: phú quý, cô độc, khởi đầu
    "symbol",           # symbol cổ điển: long, hổ, quy
    "other",
)

SCHOOLS: tuple[str, ...] = (
    "mai_hoa",
    "lien_hoa",
    "luc_hao",
    "bat_tu",
    "tu_vi",
    "ha_lac",
    "chiem_tinh",
    "common",           # áp dụng tất cả
)


# ─── Dataclasses ─────────────────────────────────────────────────────────────


@dataclass
class Concept:
    concept_id: int | None
    canonical_vi: str
    canonical_zh: str | None = None
    canonical_en: str | None = None
    concept_type: str = "other"
    aliases: list[str] = field(default_factory=list)
    schools: list[str] = field(default_factory=lambda: ["common"])
    source: str = "manual"
    confidence: float = 0.5
    notes: str | None = None
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Mapping:
    """One concept → cosmology-dimension edge.

    v2 (2026-05-12): added source_tier + provenance + conflict tracking
    per anh's tuyên ngôn (multi-school independent with cross-validation).
    """
    mapping_id: int | None
    concept_id: int
    dim_type: str          # one of DIM_TYPES
    dim_value: str         # "mộc" / "Đoài" / "Tỵ" / "Đại Quá" / ...
    strength: float = 1.0
    reasoning_vi: str | None = None
    reasoning_zh: str | None = None
    school: str = "common"
    source: str = "manual"
    confidence: float = 0.5
    created_at: int = 0
    # v2 provenance + conflict
    source_tier: str = "B"                  # 'S' | 'A' | 'B' | 'C'
    source_book: str | None = None
    source_chapter: str | None = None
    source_page: int | None = None
    source_quote: str | None = None
    conflict_flag: int = 0
    conflict_group_id: int | None = None
    supersedes: int | None = None
    verified_by_anh: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConflictGroup:
    """A group of mappings that disagree about the same (concept, dim_type)."""
    conflict_group_id: int | None
    concept_id: int
    dim_type: str
    status: str = "open"           # 'open' | 'resolved' | 'kept_all' | 'dismissed'
    primary_mapping_id: int | None = None
    anh_note: str | None = None
    created_at: int = 0
    resolved_at: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContextualMeaning:
    cm_id: int | None
    primary_concept_id: int
    modifier_concept_ids: list[int]    # 0+ secondary concepts that modify
    contextual_phrase_vi: str
    meaning_vi: str
    meaning_zh: str | None = None
    school: str = "common"
    source: str = "manual"
    confidence: float = 0.5
    created_at: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Corpus:
    """A book/source ingested into lexicon.

    v3 (2026-05-12): library-mode fields for "Thủ thư" workflow.
    Tracks reading progress, tier classification provenance, multi-school tags.
    """
    corpus_id: int | None
    name: str
    author: str | None = None
    school: str | None = None                 # primary school (legacy single-tag)
    language: str = "vi"
    file_path: str | None = None
    ingested_at: int | None = None
    concepts_extracted: int = 0
    mappings_extracted: int = 0
    notes: str | None = None
    # v3 library fields
    status: str = "queued"                    # 'queued' | 'reading' | 'done' | 'skip' | 'error'
    tier: str = "B"                           # 'S' | 'A' | 'B' | 'C'
    tier_decided_by: str = "manifest"         # 'manifest' | 'librarian_llm' | 'anh'
    pages_total: int = 0
    pages_ingested: int = 0
    progress_percent: float = 0.0
    schools_tags: list[str] = field(default_factory=list)  # multi-school: ["mai_hoa","luc_hao"]
    cover_image: str | None = None            # path to thumbnail (page-001 png)
    last_ingest_at: int | None = None
    librarian_summary: str | None = None      # LLM-generated 1-2 sentence summary
    librarian_proposal_json: str | None = None  # raw LLM classify proposal JSON
    # v4 restoration fields (2026-05-12) — "phục chế sách scan thành bản đẹp"
    restored_status: str = "none"             # 'none'|'pending'|'partial'|'done'|'error'
    restored_pages: int = 0                   # số trang đã phục chế xong
    restored_path: str | None = None          # thư mục data/yi_restored/<book_id>/
    restored_manifest: str | None = None      # path tới manifest.json
    restored_at: int | None = None
    copyright_status: str = "internal_only"   # 'public_domain'|'internal_only'|'consent_pending'
    allow_download: int = 0                   # 0=cấm tải (default — theo policy anh)
    # v5 text-layer classification (2026-05-12)
    restore_method: str = "unknown"           # 'unknown'|'text_layer'|'pure_scan'|'hybrid'
    text_layer_chars_per_page: float = 0.0    # avg chars per page (metric for quality)
    text_layer_probed_at: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DistillItem:
    item_id: int | None
    kind: str                       # 'new_concept' | 'new_mapping' | 'new_contextual'
    payload: dict
    source: str
    confidence: float = 0.5
    status: str = "auto_accepted"   # 'auto_accepted' | 'manual_pending' | 'approved' | 'rejected'
    created_at: int = 0
    reviewed_at: int | None = None
    reviewer_note: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


# ─── DB ──────────────────────────────────────────────────────────────────────


def _conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def bootstrap_db() -> None:
    """Create tables if not exist. Safe to call multiple times.

    v2 (2026-05-12, anh tuyên ngôn): adds tier + provenance + conflict columns
    to mappings table. Each mapping now carries authority info so the system
    can detect conflicts between sources WITHOUT auto-overwriting.
    """
    with _conn() as c:
        # ─── Migration: add v2 columns to mappings ──────────────────────────
        existing_cols = {r[1] for r in c.execute("PRAGMA table_info(mappings)").fetchall()}
        v2_columns = [
            ("source_tier",       "TEXT DEFAULT 'B'"),      # S/A/B/C — see docs
            ("source_book",       "TEXT"),                   # human-readable book name
            ("source_chapter",    "TEXT"),                   # chapter / section
            ("source_page",       "INTEGER"),                # PDF page
            ("source_quote",      "TEXT"),                   # ~50-200 char snippet for traceback
            ("conflict_flag",     "INTEGER DEFAULT 0"),      # 0=no, 1=conflict pending
            ("conflict_group_id", "INTEGER"),                # links mappings that disagree
            ("supersedes",        "INTEGER"),                # mapping_id của bản cũ bị thay
            ("verified_by_anh",   "INTEGER DEFAULT 0"),      # 1 nếu anh đã review approve
        ]
        for col_name, col_def in v2_columns:
            if col_name not in existing_cols:
                try:
                    c.execute(f"ALTER TABLE mappings ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass  # already added by parallel run

        # ─── Migration: add v3 library columns to corpora ───────────────────
        try:
            existing_corp_cols = {r[1] for r in c.execute("PRAGMA table_info(corpora)").fetchall()}
        except Exception:
            existing_corp_cols = set()
        if existing_corp_cols:  # table exists, migrate
            v3_corpus_columns = [
                ("status",                  "TEXT DEFAULT 'queued'"),
                ("tier",                    "TEXT DEFAULT 'B'"),
                ("tier_decided_by",         "TEXT DEFAULT 'manifest'"),
                ("pages_total",             "INTEGER DEFAULT 0"),
                ("pages_ingested",          "INTEGER DEFAULT 0"),
                ("progress_percent",        "REAL DEFAULT 0.0"),
                ("schools_tags_json",       "TEXT DEFAULT '[]'"),
                ("cover_image",             "TEXT"),
                ("last_ingest_at",          "INTEGER"),
                ("librarian_summary",       "TEXT"),
                ("librarian_proposal_json", "TEXT"),
                # v4 restoration columns
                ("restored_status",         "TEXT DEFAULT 'none'"),
                ("restored_pages",          "INTEGER DEFAULT 0"),
                ("restored_path",           "TEXT"),
                ("restored_manifest",       "TEXT"),
                ("restored_at",             "INTEGER"),
                ("copyright_status",        "TEXT DEFAULT 'internal_only'"),
                ("allow_download",          "INTEGER DEFAULT 0"),
                # v5 text-layer classification
                ("restore_method",          "TEXT DEFAULT 'unknown'"),
                ("text_layer_chars_per_page", "REAL DEFAULT 0.0"),
                ("text_layer_probed_at",    "INTEGER"),
            ]
            for col_name, col_def in v3_corpus_columns:
                if col_name not in existing_corp_cols:
                    try:
                        c.execute(f"ALTER TABLE corpora ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass

        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS concepts (
                concept_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_vi    TEXT NOT NULL,
                canonical_zh    TEXT,
                canonical_en    TEXT,
                concept_type    TEXT NOT NULL DEFAULT 'other',
                aliases_json    TEXT NOT NULL DEFAULT '[]',
                schools_json    TEXT NOT NULL DEFAULT '["common"]',
                source          TEXT NOT NULL DEFAULT 'manual',
                confidence      REAL NOT NULL DEFAULT 0.5,
                notes           TEXT,
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER NOT NULL,
                UNIQUE(canonical_vi, concept_type)
            );
            CREATE INDEX IF NOT EXISTS idx_concept_vi   ON concepts(canonical_vi);
            CREATE INDEX IF NOT EXISTS idx_concept_zh   ON concepts(canonical_zh);
            CREATE INDEX IF NOT EXISTS idx_concept_type ON concepts(concept_type);

            CREATE TABLE IF NOT EXISTS mappings (
                mapping_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id      INTEGER NOT NULL,
                dim_type        TEXT NOT NULL,
                dim_value       TEXT NOT NULL,
                strength        REAL NOT NULL DEFAULT 1.0,
                reasoning_vi    TEXT,
                reasoning_zh    TEXT,
                school          TEXT NOT NULL DEFAULT 'common',
                source          TEXT NOT NULL DEFAULT 'manual',
                confidence      REAL NOT NULL DEFAULT 0.5,
                created_at      INTEGER NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(concept_id),
                UNIQUE(concept_id, dim_type, dim_value, school)
            );
            CREATE INDEX IF NOT EXISTS idx_map_concept ON mappings(concept_id);
            CREATE INDEX IF NOT EXISTS idx_map_dim     ON mappings(dim_type, dim_value);

            CREATE TABLE IF NOT EXISTS contextual_meanings (
                cm_id                INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_concept_id   INTEGER NOT NULL,
                modifier_ids_json    TEXT NOT NULL DEFAULT '[]',
                contextual_phrase_vi TEXT,
                meaning_vi           TEXT NOT NULL,
                meaning_zh           TEXT,
                school               TEXT NOT NULL DEFAULT 'common',
                source               TEXT NOT NULL DEFAULT 'manual',
                confidence           REAL NOT NULL DEFAULT 0.5,
                created_at           INTEGER NOT NULL,
                FOREIGN KEY (primary_concept_id) REFERENCES concepts(concept_id)
            );
            CREATE INDEX IF NOT EXISTS idx_cm_primary  ON contextual_meanings(primary_concept_id);
            CREATE INDEX IF NOT EXISTS idx_cm_phrase   ON contextual_meanings(contextual_phrase_vi);

            CREATE TABLE IF NOT EXISTS corpora (
                corpus_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name                TEXT NOT NULL,
                author              TEXT,
                school              TEXT,
                language            TEXT NOT NULL DEFAULT 'vi',
                file_path           TEXT,
                ingested_at         INTEGER,
                concepts_extracted  INTEGER NOT NULL DEFAULT 0,
                mappings_extracted  INTEGER NOT NULL DEFAULT 0,
                notes               TEXT,
                -- v3 library fields
                status              TEXT NOT NULL DEFAULT 'queued',
                tier                TEXT NOT NULL DEFAULT 'B',
                tier_decided_by     TEXT NOT NULL DEFAULT 'manifest',
                pages_total         INTEGER NOT NULL DEFAULT 0,
                pages_ingested      INTEGER NOT NULL DEFAULT 0,
                progress_percent    REAL NOT NULL DEFAULT 0.0,
                schools_tags_json   TEXT NOT NULL DEFAULT '[]',
                cover_image         TEXT,
                last_ingest_at      INTEGER,
                librarian_summary   TEXT,
                librarian_proposal_json TEXT,
                -- v4 restoration
                restored_status     TEXT NOT NULL DEFAULT 'none',
                restored_pages      INTEGER NOT NULL DEFAULT 0,
                restored_path       TEXT,
                restored_manifest   TEXT,
                restored_at         INTEGER,
                copyright_status    TEXT NOT NULL DEFAULT 'internal_only',
                allow_download      INTEGER NOT NULL DEFAULT 0,
                -- v5 text-layer classification
                restore_method      TEXT NOT NULL DEFAULT 'unknown',
                text_layer_chars_per_page REAL NOT NULL DEFAULT 0.0,
                text_layer_probed_at INTEGER,
                UNIQUE(name)
            );
            CREATE INDEX IF NOT EXISTS idx_corpus_tier            ON corpora(tier);
            CREATE INDEX IF NOT EXISTS idx_corpus_status          ON corpora(status);
            CREATE INDEX IF NOT EXISTS idx_corpus_restored_status ON corpora(restored_status);

            CREATE TABLE IF NOT EXISTS conflict_groups (
                conflict_group_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id         INTEGER NOT NULL,
                dim_type           TEXT NOT NULL,
                status             TEXT NOT NULL DEFAULT 'open',
                                   -- 'open' | 'resolved' | 'kept_all' | 'dismissed'
                primary_mapping_id INTEGER,
                anh_note           TEXT,
                created_at         INTEGER NOT NULL,
                resolved_at        INTEGER,
                FOREIGN KEY (concept_id) REFERENCES concepts(concept_id)
            );
            CREATE INDEX IF NOT EXISTS idx_conflict_concept ON conflict_groups(concept_id);
            CREATE INDEX IF NOT EXISTS idx_conflict_status  ON conflict_groups(status);

            CREATE TABLE IF NOT EXISTS distill_queue (
                item_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                kind           TEXT NOT NULL,
                payload_json   TEXT NOT NULL,
                source         TEXT NOT NULL,
                confidence     REAL NOT NULL DEFAULT 0.5,
                status         TEXT NOT NULL DEFAULT 'auto_accepted',
                created_at     INTEGER NOT NULL,
                reviewed_at    INTEGER,
                reviewer_note  TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_distill_status ON distill_queue(status);
            CREATE INDEX IF NOT EXISTS idx_distill_kind   ON distill_queue(kind);

            -- FTS for full-text concept search (Vi+Zh+En + aliases)
            CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
                canonical_vi, canonical_zh, canonical_en, aliases_json, notes,
                content='concepts', content_rowid='concept_id', tokenize='unicode61'
            );
            """
        )


# ─── CRUD: Concepts ──────────────────────────────────────────────────────────


def _row_to_concept(row: sqlite3.Row) -> Concept:
    return Concept(
        concept_id=row["concept_id"],
        canonical_vi=row["canonical_vi"],
        canonical_zh=row["canonical_zh"],
        canonical_en=row["canonical_en"],
        concept_type=row["concept_type"],
        aliases=json.loads(row["aliases_json"] or "[]"),
        schools=json.loads(row["schools_json"] or '["common"]'),
        source=row["source"],
        confidence=row["confidence"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def add_concept(
    canonical_vi: str,
    *,
    concept_type: str = "other",
    canonical_zh: str | None = None,
    canonical_en: str | None = None,
    aliases: list[str] | None = None,
    schools: list[str] | None = None,
    source: str = "manual",
    confidence: float = 0.5,
    notes: str | None = None,
) -> Concept:
    """Add a concept (or return existing if (canonical_vi, concept_type) exists)."""
    bootstrap_db()
    now = int(time.time())
    aliases_json = json.dumps(aliases or [], ensure_ascii=False)
    schools_json = json.dumps(schools or ["common"], ensure_ascii=False)

    with _conn() as c:
        existing = c.execute(
            "SELECT * FROM concepts WHERE canonical_vi = ? AND concept_type = ?",
            (canonical_vi, concept_type),
        ).fetchone()
        if existing:
            return _row_to_concept(existing)

        cur = c.execute(
            """INSERT INTO concepts (
                canonical_vi, canonical_zh, canonical_en, concept_type,
                aliases_json, schools_json, source, confidence, notes,
                created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                canonical_vi, canonical_zh, canonical_en, concept_type,
                aliases_json, schools_json, source, confidence, notes,
                now, now,
            ),
        )
        cid = cur.lastrowid
        c.execute(
            "INSERT INTO concepts_fts (rowid, canonical_vi, canonical_zh, canonical_en, aliases_json, notes) "
            "VALUES (?,?,?,?,?,?)",
            (cid, canonical_vi, canonical_zh or "", canonical_en or "", aliases_json, notes or ""),
        )
        row = c.execute("SELECT * FROM concepts WHERE concept_id = ?", (cid,)).fetchone()
        return _row_to_concept(row)


def get_concept(
    *, concept_id: int | None = None, canonical_vi: str | None = None, concept_type: str | None = None,
) -> Concept | None:
    bootstrap_db()
    if concept_id is None and canonical_vi is None:
        return None
    with _conn() as c:
        if concept_id is not None:
            row = c.execute("SELECT * FROM concepts WHERE concept_id = ?", (concept_id,)).fetchone()
        else:
            sql = "SELECT * FROM concepts WHERE canonical_vi = ?"
            args = [canonical_vi]
            if concept_type:
                sql += " AND concept_type = ?"
                args.append(concept_type)
            row = c.execute(sql, args).fetchone()
    return _row_to_concept(row) if row else None


def search_concepts(query: str, *, schools: list[str] | None = None, limit: int = 20) -> list[Concept]:
    """Full-text search across canonical_vi/zh/en + aliases + notes.

    If `schools` provided, post-filter for concepts tagged any of those schools.
    """
    bootstrap_db()
    if not query.strip():
        return []
    with _conn() as c:
        # FTS5 query
        try:
            rows = c.execute(
                "SELECT c.* FROM concepts c "
                "INNER JOIN concepts_fts f ON c.concept_id = f.rowid "
                "WHERE concepts_fts MATCH ? "
                "ORDER BY rank LIMIT ?",
                (query, limit * 3),  # over-fetch for filtering
            ).fetchall()
        except sqlite3.OperationalError:
            # FTS query syntax issue → fallback to LIKE
            like = f"%{query}%"
            rows = c.execute(
                "SELECT * FROM concepts WHERE canonical_vi LIKE ? "
                "OR canonical_zh LIKE ? OR canonical_en LIKE ? OR aliases_json LIKE ? "
                "LIMIT ?",
                (like, like, like, like, limit * 3),
            ).fetchall()
    out: list[Concept] = []
    for r in rows:
        c_obj = _row_to_concept(r)
        if schools:
            if not any(s in c_obj.schools for s in schools) and "common" not in c_obj.schools:
                continue
        out.append(c_obj)
        if len(out) >= limit:
            break
    return out


# ─── CRUD: Mappings ──────────────────────────────────────────────────────────


def _row_to_mapping(row: sqlite3.Row) -> Mapping:
    return Mapping(
        mapping_id=row["mapping_id"],
        concept_id=row["concept_id"],
        dim_type=row["dim_type"],
        dim_value=row["dim_value"],
        strength=row["strength"],
        reasoning_vi=row["reasoning_vi"],
        reasoning_zh=row["reasoning_zh"],
        school=row["school"],
        source=row["source"],
        confidence=row["confidence"],
        created_at=row["created_at"],
        source_tier=_row_get(row, "source_tier", "B"),
        source_book=_row_get(row, "source_book", None),
        source_chapter=_row_get(row, "source_chapter", None),
        source_page=_row_get(row, "source_page", None),
        source_quote=_row_get(row, "source_quote", None),
        conflict_flag=_row_get(row, "conflict_flag", 0) or 0,
        conflict_group_id=_row_get(row, "conflict_group_id", None),
        supersedes=_row_get(row, "supersedes", None),
        verified_by_anh=_row_get(row, "verified_by_anh", 0) or 0,
    )


def _row_get(row: sqlite3.Row, key: str, default):
    """Safely get column from row; return default if column doesn't exist."""
    try:
        return row[key]
    except (KeyError, IndexError):
        return default


# Tier ordering (lower number = higher authority)
_TIER_RANK = {"S": 0, "A": 1, "B": 2, "C": 3}


def _tier_compare(tier_a: str, tier_b: str) -> int:
    """Compare tiers. -1: a higher authority; +1: b higher; 0: same."""
    ra = _TIER_RANK.get(tier_a, 99)
    rb = _TIER_RANK.get(tier_b, 99)
    return -1 if ra < rb else (1 if ra > rb else 0)


# Dim types where multiple values for same concept ARE valid (not conflicts)
# - `khac` (freeform "other" category — multi-fact storage)
# - `huong` (one concept can map to multiple directions)
# - `thien_can`, `dia_chi` (concepts may relate to multiple stems/branches)
# - `mua`, `tiet_khi`, `tang_phu` (multi-season organs, etc.)
MULTI_VALUE_DIM_TYPES: set[str] = {
    # Canonical multi-value dims
    "khac", "huong", "thien_can", "dia_chi", "mua", "tiet_khi",
    "tang_phu", "thoi", "hexagram", "than_sat",
    # LLM-generated freeform dims (extend as needed; these are accepted as multi-fact)
    "other", "phân_loại", "phan_loai", "số", "so", "hệ_thống", "he_thong",
    "loại", "loai", "vai_trò", "vai_tro", "tính_chất", "tinh_chat",
    "nhóm", "nhom", "ý_nghĩa", "y_nghia", "ứng_dụng", "ung_dung",
}


def _normalize_dim_value(value: str) -> str:
    """Normalize dim_value: lowercase, strip whitespace, fold variants.

    Returns the canonical form used for conflict detection (case-insensitive).
    Stored dim_value remains the original cased version.
    """
    return value.strip().lower()


def add_mapping(
    concept_id: int,
    dim_type: str,
    dim_value: str,
    *,
    strength: float = 1.0,
    reasoning_vi: str | None = None,
    reasoning_zh: str | None = None,
    school: str = "common",
    source: str = "manual",
    confidence: float = 0.5,
    source_tier: str = "B",
    source_book: str | None = None,
    source_chapter: str | None = None,
    source_page: int | None = None,
    source_quote: str | None = None,
) -> Mapping:
    """Add a mapping with tier-aware conflict detection.

    Behavior (v2 per anh's tuyên ngôn):
    1. Exact duplicate (same concept_id+dim_type+dim_value+school) → return existing
    2. Different dim_value for same (concept_id, dim_type, school) → CONFLICT:
       - Create or join conflict_group
       - Insert new mapping with conflict_flag=1
       - If new tier > existing tier → existing also flagged, new becomes primary candidate
       - If tiers equal → both flagged, anh review
       - If new tier < existing → new flagged as alternative
    3. Different school → not a conflict (each school independent — tuyên ngôn nguyên tắc 2)
    """
    bootstrap_db()
    now = int(time.time())
    norm_value = _normalize_dim_value(dim_value)
    with _conn() as c:
        # SQLite LOWER() doesn't lowercase Vietnamese chars → query candidates by
        # (concept, dim_type, school) and filter case-insensitively in Python.
        candidates = c.execute(
            "SELECT * FROM mappings WHERE concept_id=? AND dim_type=? AND school=?",
            (concept_id, dim_type, school),
        ).fetchall()

        # 1. Exact duplicate (case-insensitive on dim_value)
        for row in candidates:
            if _normalize_dim_value(row["dim_value"]) == norm_value:
                return _row_to_mapping(row)

        # 2. Conflict detection — ONLY for canonical (single-value) dim_types.
        # MULTI_VALUE_DIM_TYPES allow multiple distinct values per concept (legitimate multi-fact).
        rivals: list[sqlite3.Row] = []
        if dim_type not in MULTI_VALUE_DIM_TYPES:
            rivals = [
                row for row in candidates
                if _normalize_dim_value(row["dim_value"]) != norm_value
            ]

        conflict_group_id: int | None = None
        conflict_flag = 0
        if rivals:
            # Find or create conflict group for this (concept, dim_type)
            group_row = c.execute(
                "SELECT conflict_group_id FROM conflict_groups "
                "WHERE concept_id=? AND dim_type=? AND status='open' LIMIT 1",
                (concept_id, dim_type),
            ).fetchone()
            if group_row:
                conflict_group_id = group_row["conflict_group_id"]
            else:
                cur = c.execute(
                    "INSERT INTO conflict_groups (concept_id, dim_type, status, created_at) "
                    "VALUES (?, ?, 'open', ?)",
                    (concept_id, dim_type, now),
                )
                conflict_group_id = cur.lastrowid
                # Mark existing rivals (case-insensitive different value) as conflict members
                for rival in rivals:
                    c.execute(
                        "UPDATE mappings SET conflict_flag=1, conflict_group_id=? WHERE mapping_id=?",
                        (conflict_group_id, rival["mapping_id"]),
                    )
            conflict_flag = 1

        # 3. Insert new mapping with provenance
        cur = c.execute(
            """INSERT INTO mappings (
                concept_id, dim_type, dim_value, strength,
                reasoning_vi, reasoning_zh, school, source, confidence, created_at,
                source_tier, source_book, source_chapter, source_page, source_quote,
                conflict_flag, conflict_group_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?)""",
            (
                concept_id, dim_type, dim_value, strength,
                reasoning_vi, reasoning_zh, school, source, confidence, now,
                source_tier, source_book, source_chapter, source_page, source_quote,
                conflict_flag, conflict_group_id,
            ),
        )
        row = c.execute("SELECT * FROM mappings WHERE mapping_id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_mapping(row)


def mappings_for(concept_id: int, *, school: str | None = None) -> list[Mapping]:
    bootstrap_db()
    with _conn() as c:
        if school:
            rows = c.execute(
                "SELECT * FROM mappings WHERE concept_id=? AND school IN (?, 'common') "
                "ORDER BY strength DESC, confidence DESC",
                (concept_id, school),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT * FROM mappings WHERE concept_id=? ORDER BY strength DESC, confidence DESC",
                (concept_id,),
            ).fetchall()
    return [_row_to_mapping(r) for r in rows]


# ─── CRUD: Conflict groups ──────────────────────────────────────────────────


def list_conflicts(*, status: str | None = "open", limit: int = 50) -> list[dict]:
    """List conflict groups. Each item includes group meta + all member mappings."""
    bootstrap_db()
    with _conn() as c:
        if status:
            rows = c.execute(
                "SELECT * FROM conflict_groups WHERE status=? "
                "ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT * FROM conflict_groups ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out: list[dict] = []
        for r in rows:
            group = {
                "conflict_group_id": r["conflict_group_id"],
                "concept_id": r["concept_id"],
                "dim_type": r["dim_type"],
                "status": r["status"],
                "primary_mapping_id": r["primary_mapping_id"],
                "anh_note": r["anh_note"],
                "created_at": r["created_at"],
                "resolved_at": r["resolved_at"],
            }
            # Concept name
            cn = c.execute("SELECT canonical_vi FROM concepts WHERE concept_id=?",
                           (r["concept_id"],)).fetchone()
            group["concept_vi"] = cn["canonical_vi"] if cn else "?"
            # Member mappings
            members = c.execute(
                "SELECT * FROM mappings WHERE conflict_group_id=? ORDER BY source_tier, created_at",
                (r["conflict_group_id"],),
            ).fetchall()
            group["mappings"] = [_row_to_mapping(m).to_dict() for m in members]
            out.append(group)
    return out


def resolve_conflict(
    conflict_group_id: int,
    *,
    primary_mapping_id: int | None = None,
    status: str = "resolved",
    anh_note: str = "",
) -> bool:
    """Anh resolves a conflict.

    Modes:
    - status='resolved' + primary_mapping_id → that mapping wins, others demoted (kept as alternatives)
    - status='kept_all' → all mappings stay primary (multi-school disagree but each valid in own context)
    - status='dismissed' → all mappings flagged conflict_flag=0 but not chosen as primary
    """
    bootstrap_db()
    now = int(time.time())
    with _conn() as c:
        c.execute(
            "UPDATE conflict_groups SET status=?, primary_mapping_id=?, anh_note=?, resolved_at=? "
            "WHERE conflict_group_id=?",
            (status, primary_mapping_id, anh_note, now, conflict_group_id),
        )
        if status == "resolved" and primary_mapping_id is not None:
            # Mark primary as verified, others lose conflict_flag but stay as alternatives
            c.execute(
                "UPDATE mappings SET verified_by_anh=1, conflict_flag=0 WHERE mapping_id=?",
                (primary_mapping_id,),
            )
            c.execute(
                "UPDATE mappings SET conflict_flag=0 WHERE conflict_group_id=? AND mapping_id!=?",
                (conflict_group_id, primary_mapping_id),
            )
        elif status in ("kept_all", "dismissed"):
            c.execute(
                "UPDATE mappings SET conflict_flag=0 WHERE conflict_group_id=?",
                (conflict_group_id,),
            )
        return True


def reverse_lookup_concepts(dim_type: str, dim_value: str, *, limit: int = 50) -> list[Concept]:
    """Find concepts that map to (dim_type, dim_value). E.g. 'what concepts → Mộc?'"""
    bootstrap_db()
    with _conn() as c:
        rows = c.execute(
            "SELECT c.* FROM concepts c "
            "INNER JOIN mappings m ON c.concept_id = m.concept_id "
            "WHERE m.dim_type = ? AND m.dim_value = ? "
            "ORDER BY m.strength DESC LIMIT ?",
            (dim_type, dim_value, limit),
        ).fetchall()
    return [_row_to_concept(r) for r in rows]


# ─── CRUD: Contextual ────────────────────────────────────────────────────────


def add_contextual_meaning(
    primary_concept_id: int,
    meaning_vi: str,
    *,
    modifier_concept_ids: list[int] | None = None,
    contextual_phrase_vi: str | None = None,
    meaning_zh: str | None = None,
    school: str = "common",
    source: str = "manual",
    confidence: float = 0.5,
) -> ContextualMeaning:
    bootstrap_db()
    now = int(time.time())
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO contextual_meanings (
                primary_concept_id, modifier_ids_json, contextual_phrase_vi,
                meaning_vi, meaning_zh, school, source, confidence, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                primary_concept_id,
                json.dumps(modifier_concept_ids or [], ensure_ascii=False),
                contextual_phrase_vi,
                meaning_vi, meaning_zh, school, source, confidence, now,
            ),
        )
        row = c.execute(
            "SELECT * FROM contextual_meanings WHERE cm_id = ?", (cur.lastrowid,)
        ).fetchone()
    return ContextualMeaning(
        cm_id=row["cm_id"],
        primary_concept_id=row["primary_concept_id"],
        modifier_concept_ids=json.loads(row["modifier_ids_json"] or "[]"),
        contextual_phrase_vi=row["contextual_phrase_vi"],
        meaning_vi=row["meaning_vi"],
        meaning_zh=row["meaning_zh"],
        school=row["school"],
        source=row["source"],
        confidence=row["confidence"],
        created_at=row["created_at"],
    )


# ─── CRUD: Corpora ───────────────────────────────────────────────────────────


def _row_to_corpus(r: sqlite3.Row) -> Corpus:
    """Build Corpus dataclass from row, tolerating missing v3 columns."""
    schools_tags = []
    raw = _row_get(r, "schools_tags_json", "[]")
    if raw:
        try:
            schools_tags = json.loads(raw)
        except Exception:
            schools_tags = []
    return Corpus(
        corpus_id=r["corpus_id"], name=r["name"], author=r["author"],
        school=r["school"], language=r["language"], file_path=r["file_path"],
        ingested_at=r["ingested_at"],
        concepts_extracted=r["concepts_extracted"],
        mappings_extracted=r["mappings_extracted"],
        notes=r["notes"],
        status=_row_get(r, "status", "queued") or "queued",
        tier=_row_get(r, "tier", "B") or "B",
        tier_decided_by=_row_get(r, "tier_decided_by", "manifest") or "manifest",
        pages_total=_row_get(r, "pages_total", 0) or 0,
        pages_ingested=_row_get(r, "pages_ingested", 0) or 0,
        progress_percent=_row_get(r, "progress_percent", 0.0) or 0.0,
        schools_tags=schools_tags,
        cover_image=_row_get(r, "cover_image", None),
        last_ingest_at=_row_get(r, "last_ingest_at", None),
        librarian_summary=_row_get(r, "librarian_summary", None),
        librarian_proposal_json=_row_get(r, "librarian_proposal_json", None),
        restored_status=_row_get(r, "restored_status", "none") or "none",
        restored_pages=_row_get(r, "restored_pages", 0) or 0,
        restored_path=_row_get(r, "restored_path", None),
        restored_manifest=_row_get(r, "restored_manifest", None),
        restored_at=_row_get(r, "restored_at", None),
        copyright_status=_row_get(r, "copyright_status", "internal_only") or "internal_only",
        allow_download=_row_get(r, "allow_download", 0) or 0,
        restore_method=_row_get(r, "restore_method", "unknown") or "unknown",
        text_layer_chars_per_page=_row_get(r, "text_layer_chars_per_page", 0.0) or 0.0,
        text_layer_probed_at=_row_get(r, "text_layer_probed_at", None),
    )


def add_corpus(
    name: str,
    *,
    author: str | None = None,
    school: str | None = None,
    language: str = "vi",
    file_path: str | None = None,
    notes: str | None = None,
    status: str = "queued",
    tier: str = "B",
    tier_decided_by: str = "manifest",
    pages_total: int = 0,
    schools_tags: list[str] | None = None,
    cover_image: str | None = None,
    librarian_summary: str | None = None,
    librarian_proposal_json: str | None = None,
) -> Corpus:
    """Add or fetch corpus by unique name. Provides v3 library fields."""
    bootstrap_db()
    with _conn() as c:
        existing = c.execute("SELECT * FROM corpora WHERE name = ?", (name,)).fetchone()
        if existing:
            return _row_to_corpus(existing)
        cur = c.execute(
            """INSERT INTO corpora (
                name, author, school, language, file_path, notes,
                status, tier, tier_decided_by, pages_total,
                schools_tags_json, cover_image,
                librarian_summary, librarian_proposal_json
            ) VALUES (?,?,?,?,?,?, ?,?,?,?, ?,?, ?,?)""",
            (
                name, author, school, language, file_path, notes,
                status, tier, tier_decided_by, pages_total,
                json.dumps(schools_tags or [], ensure_ascii=False),
                cover_image,
                librarian_summary, librarian_proposal_json,
            ),
        )
        row = c.execute("SELECT * FROM corpora WHERE corpus_id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_corpus(row)


def update_corpus(
    corpus_id: int,
    *,
    status: str | None = None,
    tier: str | None = None,
    tier_decided_by: str | None = None,
    pages_total: int | None = None,
    pages_ingested: int | None = None,
    schools_tags: list[str] | None = None,
    author: str | None = None,
    school: str | None = None,
    cover_image: str | None = None,
    librarian_summary: str | None = None,
    librarian_proposal_json: str | None = None,
    notes: str | None = None,
    bump_last_ingest: bool = False,
    # v4 restoration patches
    restored_status: str | None = None,
    restored_pages: int | None = None,
    restored_path: str | None = None,
    restored_manifest: str | None = None,
    copyright_status: str | None = None,
    allow_download: int | None = None,
    bump_restored_at: bool = False,
    # v5 text-layer fields
    restore_method: str | None = None,
    text_layer_chars_per_page: float | None = None,
    bump_text_layer_probed_at: bool = False,
) -> Corpus | None:
    """Patch corpus fields; only provided kwargs are updated."""
    bootstrap_db()
    sets: list[str] = []
    args: list = []
    if status is not None:
        sets.append("status=?"); args.append(status)
    if tier is not None:
        sets.append("tier=?"); args.append(tier)
    if tier_decided_by is not None:
        sets.append("tier_decided_by=?"); args.append(tier_decided_by)
    if pages_total is not None:
        sets.append("pages_total=?"); args.append(pages_total)
    if pages_ingested is not None:
        sets.append("pages_ingested=?"); args.append(pages_ingested)
    if schools_tags is not None:
        sets.append("schools_tags_json=?")
        args.append(json.dumps(schools_tags, ensure_ascii=False))
    if author is not None:
        sets.append("author=?"); args.append(author)
    if school is not None:
        sets.append("school=?"); args.append(school)
    if cover_image is not None:
        sets.append("cover_image=?"); args.append(cover_image)
    if librarian_summary is not None:
        sets.append("librarian_summary=?"); args.append(librarian_summary)
    if librarian_proposal_json is not None:
        sets.append("librarian_proposal_json=?"); args.append(librarian_proposal_json)
    if notes is not None:
        sets.append("notes=?"); args.append(notes)
    if bump_last_ingest:
        sets.append("last_ingest_at=?"); args.append(int(time.time()))
    if restored_status is not None:
        sets.append("restored_status=?"); args.append(restored_status)
    if restored_pages is not None:
        sets.append("restored_pages=?"); args.append(restored_pages)
    if restored_path is not None:
        sets.append("restored_path=?"); args.append(restored_path)
    if restored_manifest is not None:
        sets.append("restored_manifest=?"); args.append(restored_manifest)
    if copyright_status is not None:
        sets.append("copyright_status=?"); args.append(copyright_status)
    if allow_download is not None:
        sets.append("allow_download=?"); args.append(allow_download)
    if bump_restored_at:
        sets.append("restored_at=?"); args.append(int(time.time()))
    if restore_method is not None:
        sets.append("restore_method=?"); args.append(restore_method)
    if text_layer_chars_per_page is not None:
        sets.append("text_layer_chars_per_page=?"); args.append(text_layer_chars_per_page)
    if bump_text_layer_probed_at:
        sets.append("text_layer_probed_at=?"); args.append(int(time.time()))
    # Recompute progress_percent if pages_ingested or pages_total touched
    recompute_progress = (pages_total is not None) or (pages_ingested is not None)

    with _conn() as c:
        if sets:
            args.append(corpus_id)
            c.execute(f"UPDATE corpora SET {', '.join(sets)} WHERE corpus_id=?", args)
        if recompute_progress:
            r = c.execute("SELECT pages_total, pages_ingested FROM corpora WHERE corpus_id=?",
                          (corpus_id,)).fetchone()
            if r:
                pt = r["pages_total"] or 0
                pi = r["pages_ingested"] or 0
                pct = (pi / pt * 100.0) if pt > 0 else 0.0
                c.execute("UPDATE corpora SET progress_percent=? WHERE corpus_id=?",
                          (round(pct, 2), corpus_id))
        row = c.execute("SELECT * FROM corpora WHERE corpus_id=?", (corpus_id,)).fetchone()
    return _row_to_corpus(row) if row else None


def get_corpus(*, corpus_id: int | None = None, name: str | None = None) -> Corpus | None:
    bootstrap_db()
    if corpus_id is None and name is None:
        return None
    with _conn() as c:
        if corpus_id is not None:
            row = c.execute("SELECT * FROM corpora WHERE corpus_id=?", (corpus_id,)).fetchone()
        else:
            row = c.execute("SELECT * FROM corpora WHERE name=?", (name,)).fetchone()
    return _row_to_corpus(row) if row else None


def list_corpora(
    *,
    tier: str | None = None,
    status: str | None = None,
    school: str | None = None,
) -> list[Corpus]:
    """List corpora with optional filters. Sorted: tier S→C, then by name."""
    bootstrap_db()
    where_sql, args = _corpus_filter_where(tier=tier, status=status, school=school)
    sql = f"SELECT * FROM corpora {where_sql}"
    sql += (
        " ORDER BY CASE tier WHEN 'S' THEN 0 WHEN 'A' THEN 1 "
        "WHEN 'B' THEN 2 WHEN 'C' THEN 3 ELSE 9 END, name"
    )
    with _conn() as c:
        rows = c.execute(sql, args).fetchall()
    return [_row_to_corpus(r) for r in rows]


def _corpus_filter_where(
    *,
    tier: str | None = None,
    status: str | None = None,
    school: str | None = None,
) -> tuple[str, list]:
    """Build the same WHERE clause for list and stats endpoints."""
    clauses = ["1=1"]
    args: list = []
    if tier:
        clauses.append("tier=?"); args.append(tier)
    if status:
        clauses.append("status=?"); args.append(status)
    if school:
        clauses.append("(school=? OR schools_tags_json LIKE ?)")
        args.extend([school, f'%"{school}"%'])
    return "WHERE " + " AND ".join(clauses), args


def sync_restoration_metadata_from_manifest(corpus: Corpus) -> Corpus:
    """Refresh denormalized restoration fields from manifest.json if it exists."""
    if not corpus.corpus_id or not corpus.restored_manifest:
        return corpus
    manifest_path = Path(corpus.restored_manifest)
    if not manifest_path.exists():
        return corpus
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return corpus

    pages = data.get("pages") or []
    page_count = len({
        int(p.get("page"))
        for p in pages
        if isinstance(p, dict) and p.get("page") is not None and p.get("md_path")
    })
    restored_pages = page_count or int(data.get("pages_restored") or 0)
    pages_total = int(data.get("pages_total") or corpus.pages_total or 0)
    restored_status = (
        "done" if pages_total and restored_pages >= pages_total
        else "partial" if restored_pages > 0
        else corpus.restored_status
    )

    if (
        restored_pages == (corpus.restored_pages or 0)
        and restored_status == corpus.restored_status
        and (not pages_total or pages_total == (corpus.pages_total or 0))
    ):
        return corpus

    return update_corpus(
        corpus.corpus_id,
        pages_total=pages_total if pages_total else None,
        restored_pages=restored_pages,
        restored_status=restored_status,
    ) or corpus


def library_stats(
    *,
    tier: str | None = None,
    status: str | None = None,
    school: str | None = None,
) -> dict:
    """Aggregate stats for library dashboard: counts by tier/status/school."""
    bootstrap_db()
    where_sql, args = _corpus_filter_where(tier=tier, status=status, school=school)
    with _conn() as c:
        by_tier = {row[0]: row[1] for row in c.execute(
            f"SELECT tier, COUNT(*) FROM corpora {where_sql} GROUP BY tier",
            args,
        ).fetchall()}
        by_status = {row[0]: row[1] for row in c.execute(
            f"SELECT status, COUNT(*) FROM corpora {where_sql} GROUP BY status",
            args,
        ).fetchall()}
        total = c.execute(f"SELECT COUNT(*) FROM corpora {where_sql}", args).fetchone()[0]
        pages_total = c.execute(
            f"SELECT COALESCE(SUM(pages_total),0) FROM corpora {where_sql}",
            args,
        ).fetchone()[0]
        pages_ingested = c.execute(
            f"SELECT COALESCE(SUM(pages_ingested),0) FROM corpora {where_sql}",
            args,
        ).fetchone()[0]
    overall_progress = (pages_ingested / pages_total * 100.0) if pages_total > 0 else 0.0
    return {
        "total_books": total,
        "by_tier": by_tier,
        "by_status": by_status,
        "pages_total": pages_total,
        "pages_ingested": pages_ingested,
        "overall_progress_percent": round(overall_progress, 2),
    }


# ─── CRUD: Distill queue ─────────────────────────────────────────────────────


def add_distill_item(
    kind: str,
    payload: dict,
    *,
    source: str,
    confidence: float = 0.5,
    status: str = "auto_accepted",
) -> DistillItem:
    bootstrap_db()
    now = int(time.time())
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO distill_queue (kind, payload_json, source, confidence, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (kind, json.dumps(payload, ensure_ascii=False), source, confidence, status, now),
        )
        return DistillItem(
            item_id=cur.lastrowid, kind=kind, payload=payload,
            source=source, confidence=confidence, status=status, created_at=now,
        )


def get_distill_queue(*, status: str | None = None, limit: int = 100) -> list[DistillItem]:
    bootstrap_db()
    with _conn() as c:
        if status:
            rows = c.execute(
                "SELECT * FROM distill_queue WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT * FROM distill_queue ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [
        DistillItem(
            item_id=r["item_id"], kind=r["kind"],
            payload=json.loads(r["payload_json"] or "{}"),
            source=r["source"], confidence=r["confidence"], status=r["status"],
            created_at=r["created_at"], reviewed_at=r["reviewed_at"],
            reviewer_note=r["reviewer_note"],
        )
        for r in rows
    ]


def resolve_distill_item(item_id: int, *, status: str, reviewer_note: str = "") -> bool:
    """Mark a distill item as approved/rejected. Status must be 'approved' or 'rejected'."""
    if status not in ("approved", "rejected"):
        raise ValueError("status must be 'approved' or 'rejected'")
    bootstrap_db()
    with _conn() as c:
        cur = c.execute(
            "UPDATE distill_queue SET status=?, reviewed_at=?, reviewer_note=? WHERE item_id=?",
            (status, int(time.time()), reviewer_note, item_id),
        )
        return cur.rowcount > 0


# ─── Stats ───────────────────────────────────────────────────────────────────


def stats() -> dict:
    bootstrap_db()
    with _conn() as c:
        nc = c.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        nm = c.execute("SELECT COUNT(*) FROM mappings").fetchone()[0]
        ncm = c.execute("SELECT COUNT(*) FROM contextual_meanings").fetchone()[0]
        ncorp = c.execute("SELECT COUNT(*) FROM corpora").fetchone()[0]
        ndq = c.execute("SELECT status, COUNT(*) FROM distill_queue GROUP BY status").fetchall()
        by_type = c.execute(
            "SELECT concept_type, COUNT(*) FROM concepts GROUP BY concept_type ORDER BY 2 DESC"
        ).fetchall()
        by_dim = c.execute(
            "SELECT dim_type, COUNT(*) FROM mappings GROUP BY dim_type ORDER BY 2 DESC"
        ).fetchall()
    return {
        "concepts": nc,
        "mappings": nm,
        "contextual_meanings": ncm,
        "corpora": ncorp,
        "distill_queue": {row[0]: row[1] for row in ndq},
        "concepts_by_type": {row[0]: row[1] for row in by_type},
        "mappings_by_dim":  {row[0]: row[1] for row in by_dim},
    }
