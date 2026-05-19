"""Person profile system — layered, extensible, cross-reference-ready.

Each Person is an INDEPENDENT data entity with **pluggable layers** that can grow
over time without schema migration. Layers in v1:

- `identity`     — aliases, nickname, dob_civil, gender, nationality, contact
- `cosmology`    — birth data + cached Bát Tự / Tử Vi / Hà Lạc charts
- `career`       — role, title, company, industry, history, skills
- `physiognomy`  — face/body indicators (height, build, face_shape, ...) — placeholder for future engine.nhan_tuong
- `health`       — conditions, allergies, energy, vitals — placeholder for future engine.health
- `lifestyle`    — habits, diet, sleep, hobbies
- `context`      — freeform notes from chat / observations

Cross-references via `engine.yi_hermes.relationships` (separate module).

Storage: `data/yi_hermes/persons.sqlite3`. Layers stored as JSON in `layers_json`.
Core cosmology fields denormalized to indexed columns for fast filter.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "persons.sqlite3"

# Standard layer names — v1 ships these as known keys. Anh có thể thêm layer mới qua API
# (engine không enforce — chỉ là convention).
STANDARD_LAYERS: tuple[str, ...] = (
    "identity",
    "cosmology",
    "career",
    "physiognomy",
    "health",
    "lifestyle",
    "context",
)

# Confidence tag for any layer / field — "exact" if verified, lower if inferred
CONFIDENCE_LEVELS: tuple[str, ...] = ("verified", "high", "medium", "low", "unknown")


@dataclass
class PersonNote:
    """Timestamped note attached to a Person."""

    note_id: int | None
    person_id: str
    body: str
    source: str          # 'telegram' | 'web' | 'manual' | 'chat_extract'
    created_at: int
    confidence: str = "medium"
    layer_hint: str | None = None  # e.g. "career" — used by auto-extractor to route

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Person:
    """A person known to YI-CHRONOS — independent data entity with layers.

    Core indexed fields are denormalized from `layers` for fast querying.
    The full layered data is in `layers` dict (stored as JSON).
    """

    person_id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    nickname: str | None = None
    gender: str | None = None        # 'nam' | 'nữ' | None

    # Cosmology core (denormalized for indexing)
    birth_datetime_local: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"
    day_pillar_convention: str = "late_zi"  # 'early_zi' | 'late_zi' | 'midnight'
    birth_confidence: str = "unknown"        # 'exact' | 'approx_hour' | 'date_only' | 'unknown'
    day_master: str | None = None            # Cached for fast filter — e.g. "Ất mộc âm"
    cach_cuc: str | None = None              # Cached

    # Pluggable layered data (JSON-stored)
    layers: dict[str, dict] = field(default_factory=dict)

    # Metadata
    source: str = "manual"            # 'telegram' | 'web' | 'manual' | 'chat_extract'
    relationship_to_founder: str | None = None   # convenience field — full graph in relationships table
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def get_layer(self, name: str) -> dict:
        """Return the named layer (empty dict if not set)."""
        return self.layers.get(name, {})

    def update_layer(self, name: str, patch: dict, confidence: str = "medium") -> None:
        """Merge `patch` into the named layer + tag confidence.

        Each layer is a dict. We merge top-level keys; nested structures replaced.
        A `_meta` key tracks last update time + confidence per layer.
        """
        if name not in self.layers:
            self.layers[name] = {}
        self.layers[name].update(patch)
        self.layers[name].setdefault("_meta", {})
        self.layers[name]["_meta"].update({
            "last_updated": int(time.time()),
            "confidence": confidence,
        })


# ─── DB ──────────────────────────────────────────────────────────────────────


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS persons (
                person_id           TEXT PRIMARY KEY,
                name                TEXT NOT NULL,
                aliases_json        TEXT NOT NULL DEFAULT '[]',
                nickname            TEXT,
                gender              TEXT,
                birth_datetime_local TEXT,
                timezone            TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
                day_pillar_convention TEXT NOT NULL DEFAULT 'late_zi',
                birth_confidence    TEXT NOT NULL DEFAULT 'unknown',
                day_master          TEXT,
                cach_cuc            TEXT,
                layers_json         TEXT NOT NULL DEFAULT '{}',
                source              TEXT NOT NULL DEFAULT 'manual',
                relationship_to_founder TEXT,
                created_at          INTEGER NOT NULL,
                updated_at          INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);
            CREATE INDEX IF NOT EXISTS idx_persons_dm   ON persons(day_master);
            CREATE INDEX IF NOT EXISTS idx_persons_rel  ON persons(relationship_to_founder);

            CREATE TABLE IF NOT EXISTS person_notes (
                note_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id   TEXT NOT NULL,
                body        TEXT NOT NULL,
                source      TEXT NOT NULL DEFAULT 'manual',
                confidence  TEXT NOT NULL DEFAULT 'medium',
                layer_hint  TEXT,
                created_at  INTEGER NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons(person_id)
            );
            CREATE INDEX IF NOT EXISTS idx_notes_person ON person_notes(person_id);
            CREATE INDEX IF NOT EXISTS idx_notes_layer  ON person_notes(layer_hint);
            """
        )


def _row_to_person(row: sqlite3.Row) -> Person:
    return Person(
        person_id=row["person_id"],
        name=row["name"],
        aliases=json.loads(row["aliases_json"] or "[]"),
        nickname=row["nickname"],
        gender=row["gender"],
        birth_datetime_local=row["birth_datetime_local"],
        timezone=row["timezone"],
        day_pillar_convention=row["day_pillar_convention"],
        birth_confidence=row["birth_confidence"],
        day_master=row["day_master"],
        cach_cuc=row["cach_cuc"],
        layers=json.loads(row["layers_json"] or "{}"),
        source=row["source"],
        relationship_to_founder=row["relationship_to_founder"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ─── Public API ──────────────────────────────────────────────────────────────


def _slugify(name: str) -> str:
    """Build a stable person_id from a name."""
    base = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower().strip())
    base = re.sub(r"_+", "_", base).strip("_")
    return base[:40] or f"person_{uuid.uuid4().hex[:8]}"


def create_person(
    *,
    name: str,
    person_id: str | None = None,
    aliases: list[str] | None = None,
    nickname: str | None = None,
    gender: str | None = None,
    birth_datetime_local: str | None = None,
    timezone: str = "Asia/Ho_Chi_Minh",
    day_pillar_convention: str = "late_zi",
    birth_confidence: str = "unknown",
    layers: dict | None = None,
    source: str = "manual",
    relationship_to_founder: str | None = None,
) -> Person:
    """Create a new Person. Auto-generates person_id if not given."""
    _ensure_db()
    pid = person_id or _slugify(name)
    # Dedupe with random suffix if collision
    with sqlite3.connect(_DB_PATH) as c:
        existing = c.execute("SELECT 1 FROM persons WHERE person_id = ?", (pid,)).fetchone()
        if existing:
            pid = f"{pid}_{uuid.uuid4().hex[:6]}"

    now = int(time.time())
    p = Person(
        person_id=pid,
        name=name,
        aliases=aliases or [],
        nickname=nickname,
        gender=gender,
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        day_pillar_convention=day_pillar_convention,
        birth_confidence=birth_confidence,
        layers=layers or {},
        source=source,
        relationship_to_founder=relationship_to_founder,
        created_at=now,
        updated_at=now,
    )
    _save(p)
    return p


def _save(p: Person) -> None:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as c:
        c.execute(
            """INSERT OR REPLACE INTO persons (
                person_id, name, aliases_json, nickname, gender,
                birth_datetime_local, timezone, day_pillar_convention,
                birth_confidence, day_master, cach_cuc, layers_json,
                source, relationship_to_founder, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                p.person_id, p.name, json.dumps(p.aliases, ensure_ascii=False),
                p.nickname, p.gender,
                p.birth_datetime_local, p.timezone, p.day_pillar_convention,
                p.birth_confidence, p.day_master, p.cach_cuc,
                json.dumps(p.layers, ensure_ascii=False),
                p.source, p.relationship_to_founder,
                p.created_at, p.updated_at,
            ),
        )


def get_person(person_id: str) -> Person | None:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT * FROM persons WHERE person_id = ?", (person_id,)
        ).fetchone()
    return _row_to_person(row) if row else None


def find_by_name(name: str) -> Person | None:
    """Lookup by exact name or alias (case-insensitive)."""
    _ensure_db()
    name_l = name.strip().lower()
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM persons").fetchall()
    for r in rows:
        if r["name"].strip().lower() == name_l:
            return _row_to_person(r)
        aliases = json.loads(r["aliases_json"] or "[]")
        if any(a.strip().lower() == name_l for a in aliases):
            return _row_to_person(r)
    return None


def update_person(person_id: str, patch: dict) -> Person | None:
    """Update top-level fields. To update a layer, use `update_layer()`."""
    p = get_person(person_id)
    if not p:
        return None
    for key, val in patch.items():
        if hasattr(p, key) and key not in {"person_id", "created_at"}:
            setattr(p, key, val)
    p.updated_at = int(time.time())
    _save(p)
    return p


def update_layer(person_id: str, layer_name: str, patch: dict, confidence: str = "medium") -> Person | None:
    """Merge `patch` into the named layer of person."""
    p = get_person(person_id)
    if not p:
        return None
    p.update_layer(layer_name, patch, confidence=confidence)
    p.updated_at = int(time.time())
    _save(p)
    return p


def update_cached_cosmology(person_id: str, *, day_master: str | None = None, cach_cuc: str | None = None, charts: dict | None = None) -> Person | None:
    """Set denormalized cosmology fields + optionally store full charts in cosmology layer."""
    p = get_person(person_id)
    if not p:
        return None
    if day_master is not None:
        p.day_master = day_master
    if cach_cuc is not None:
        p.cach_cuc = cach_cuc
    if charts:
        cos = p.get_layer("cosmology")
        cos.setdefault("charts", {}).update(charts)
        cos.setdefault("_meta", {})["last_cast_at"] = int(time.time())
        p.layers["cosmology"] = cos
    p.updated_at = int(time.time())
    _save(p)
    return p


def list_persons(
    *,
    relationship_to_founder: str | None = None,
    day_master: str | None = None,
    limit: int = 100,
) -> list[Person]:
    _ensure_db()
    sql = "SELECT * FROM persons WHERE 1=1"
    args: list = []
    if relationship_to_founder:
        sql += " AND relationship_to_founder = ?"
        args.append(relationship_to_founder)
    if day_master:
        sql += " AND day_master = ?"
        args.append(day_master)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    args.append(limit)
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, args).fetchall()
    return [_row_to_person(r) for r in rows]


def delete_person(person_id: str) -> bool:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as c:
        cur = c.execute("DELETE FROM persons WHERE person_id = ?", (person_id,))
        c.execute("DELETE FROM person_notes WHERE person_id = ?", (person_id,))
        return cur.rowcount > 0


# ─── Notes ───────────────────────────────────────────────────────────────────


def add_note(
    person_id: str,
    body: str,
    *,
    source: str = "manual",
    confidence: str = "medium",
    layer_hint: str | None = None,
) -> int:
    _ensure_db()
    now = int(time.time())
    with sqlite3.connect(_DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO person_notes (person_id, body, source, confidence, layer_hint, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (person_id, body, source, confidence, layer_hint, now),
        )
        return cur.lastrowid


def list_notes(person_id: str, *, layer_hint: str | None = None, limit: int = 50) -> list[PersonNote]:
    _ensure_db()
    sql = "SELECT * FROM person_notes WHERE person_id = ?"
    args: list = [person_id]
    if layer_hint:
        sql += " AND layer_hint = ?"
        args.append(layer_hint)
    sql += " ORDER BY created_at DESC LIMIT ?"
    args.append(limit)
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, args).fetchall()
    return [
        PersonNote(
            note_id=r["note_id"], person_id=r["person_id"], body=r["body"],
            source=r["source"], created_at=r["created_at"],
            confidence=r["confidence"], layer_hint=r["layer_hint"],
        )
        for r in rows
    ]


# ─── Chart casting (lazy + cached) ───────────────────────────────────────────


def cast_bat_tu_for(person_id: str) -> dict | None:
    """Cast Bát Tự for a person — uses engine.bat_tu, caches in cosmology layer.

    Returns the chart dict, or None if person lacks birth data.
    """
    p = get_person(person_id)
    if not p or not p.birth_datetime_local:
        return None

    cosmology = p.get_layer("cosmology")
    charts = cosmology.get("charts", {})

    # Check cache freshness
    cached = charts.get("bat_tu")
    if cached and cached.get("birth_datetime_local") == p.birth_datetime_local:
        return cached

    # Cast fresh
    from engine.bat_tu.cast import cast_bat_tu
    chart = cast_bat_tu(
        birth_datetime_local=p.birth_datetime_local,
        timezone=p.timezone,
        gender=p.gender or "nam",
    )
    # Cache + denormalize core fields
    update_cached_cosmology(
        person_id,
        day_master=f"{chart['tu_tru']['day_master']['stem']} {chart['tu_tru']['day_master']['element']}",
        cach_cuc=chart.get("cach_cuc", {}).get("cach_name"),
        charts={"bat_tu": chart},
    )
    return chart


# ─── Founder bootstrap ──────────────────────────────────────────────────────


FOUNDER_ID = "_founder"


_FOUNDER_SEED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seeds" / "founder.json"
_FOUNDER_SEED_FALLBACK = {
    "person_id": FOUNDER_ID,
    "name": "Founder",
    "aliases": ["founder"],
    "identity": {
        "email": "founder@yi-chronos.local",
        "soul_keys": [FOUNDER_ID],
        "telegram_username": None,
    },
    "career": {
        "role": "Founder",
        "company": "YI-Chronos",
        "industry": "AI + Cosmology tools",
        "side_project": "YI-CHRONOS",
    },
}


def _load_founder_seed() -> dict:
    """Load founder identity from `data/seeds/founder.json` (gitignored).

    Falls back to placeholder values if the file is missing — handy on
    fresh clones. Personal info (email, telegram, company) lives in the
    seed file, never in committed source. See
    `examples/seeds/founder.example.json` for the schema.
    """
    if _FOUNDER_SEED_PATH.exists():
        return json.loads(_FOUNDER_SEED_PATH.read_text())
    return _FOUNDER_SEED_FALLBACK


def ensure_founder() -> Person:
    """Bootstrap the founder profile.

    Idempotent — safe to call on every startup. Reads personal identity
    from `data/seeds/founder.json` (gitignored) so source stays free of PII.
    """
    existing = get_person(FOUNDER_ID)
    if existing:
        return existing

    seed = _load_founder_seed()
    from engine.ai.founder_chart import FOUNDER_BIRTH, cast_founder_bat_tu

    chart = cast_founder_bat_tu()
    p = create_person(
        person_id=seed.get("person_id", FOUNDER_ID),
        name=seed.get("name", "Founder"),
        aliases=seed.get("aliases", ["founder"]),
        gender=FOUNDER_BIRTH["gender"],
        birth_datetime_local=FOUNDER_BIRTH["birth_datetime_local"],
        timezone=FOUNDER_BIRTH["timezone"],
        day_pillar_convention="early_zi",
        birth_confidence="approx_hour",
        source="founder_profile",
        relationship_to_founder="self",
    )
    p.update_layer("cosmology", {
        "charts": {"bat_tu": chart},
        "verified_via": "body-indicator V2B 2026-05-12",
    }, confidence="verified")
    p.update_layer("identity", seed.get("identity", {}), confidence="verified")
    p.update_layer("career", seed.get("career", {}), confidence="verified")
    p.day_master = f"{chart['tu_tru']['day_master']['stem']} {chart['tu_tru']['day_master']['element']}"
    p.cach_cuc = chart.get("cach_cuc", {}).get("cach_name")
    p.updated_at = int(time.time())
    _save(p)
    return p
