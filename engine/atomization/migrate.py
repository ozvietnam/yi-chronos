"""Migrate — Apply atomization schema vào yi_wiki SQLite DB.

Idempotent: chạy nhiều lần OK. KHÔNG drop passages cũ — engine v3/v4 còn dùng.

Run:
    python3 -m engine.atomization.migrate
    python3 -m engine.atomization.migrate --check   # chỉ verify, không apply
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# Embedding dim — text-embedding-3-small = 1536, BGE-M3 = 1024
DEFAULT_EMBED_DIM = 1536


def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        sys.exit(f"❌ DB not found: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    return conn


def _try_load_vec(conn: sqlite3.Connection) -> bool:
    """Try load sqlite-vec extension. Return True if loaded."""
    try:
        conn.enable_load_extension(True)
        # Try common paths for vec extension
        candidates = [
            "vec0",
            "sqlite-vec/vec0",
            "/usr/local/lib/vec0",
            str(PROJECT_ROOT / ".venv/lib/python3.14/site-packages/sqlite_vec/vec0"),
        ]
        # First: try python sqlite-vec package
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
            return True
        except ImportError:
            pass
        # Fallback: try direct extension path
        for cand in candidates:
            try:
                conn.load_extension(cand)
                return True
            except sqlite3.OperationalError:
                continue
    except Exception as e:
        print(f"   ⚠ Vec extension load failed: {e}")
    return False


def apply_schema(conn: sqlite3.Connection, dry_run: bool = False) -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    print(f"📜 Loading schema from: {SCHEMA_PATH}")
    print(f"   Total SQL bytes: {len(schema_sql)}")

    if dry_run:
        print("   [DRY-RUN] Skip executing")
        return

    conn.executescript(schema_sql)
    conn.commit()
    print("   ✅ Schema applied")


def setup_vec_indexes(conn: sqlite3.Connection, embed_dim: int = DEFAULT_EMBED_DIM) -> bool:
    """Setup vec0 virtual tables cho atom_vec + chunks_vec_v2."""
    if not _try_load_vec(conn):
        print("   ⚠ sqlite-vec NOT available — skip vec index setup (FTS5 vẫn work)")
        print("   → Install via: pip install sqlite-vec  hoặc brew install sqlite-vec")
        return False

    print(f"   📐 Vec dim: {embed_dim}")
    statements = [
        f"""CREATE VIRTUAL TABLE IF NOT EXISTS atom_vec USING vec0(
            atom_id INTEGER PRIMARY KEY,
            embedding FLOAT[{embed_dim}]
        )""",
        f"""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec_v2 USING vec0(
            chunk_id INTEGER PRIMARY KEY,
            embedding FLOAT[{embed_dim}]
        )""",
    ]
    for stmt in statements:
        try:
            conn.execute(stmt)
            tbl = stmt.split()[5]  # vd "atom_vec"
            print(f"   ✅ Created vec table: {tbl}")
        except sqlite3.OperationalError as e:
            print(f"   ⚠ Vec table create failed: {e}")
    conn.commit()
    return True


def verify_schema(conn: sqlite3.Connection) -> None:
    """Print summary of new tables + row counts."""
    cur = conn.cursor()
    expected_tables = [
        "chunks_v2",
        "chunk_classifications",
        "atomic_questions",
        "extraction_runs",
        "atomic_questions_fts",
        "chunks_v2_fts",
    ]
    print("\n📊 Schema verification:")
    for t in expected_tables:
        row = cur.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','virtual table') AND name=?",
            (t,)
        ).fetchone()
        if row:
            try:
                n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"   ✅ {t:<32} ({n} rows)")
            except sqlite3.OperationalError as e:
                print(f"   ✅ {t:<32} (virtual, can't count: {e})")
        else:
            print(f"   ❌ {t:<32} MISSING")

    # Check legacy passages still intact
    pass_n = cur.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
    print(f"\n   📚 passages (legacy): {pass_n} rows preserved")

    # Check vec tables
    for t in ["atom_vec", "chunks_vec_v2"]:
        row = cur.execute(
            "SELECT name FROM sqlite_master WHERE name=?", (t,)
        ).fetchone()
        marker = "✅" if row else "⚠ (no vec ext)"
        print(f"   {marker} {t}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply atomization schema")
    parser.add_argument("--check", action="store_true", help="Verify only, no changes")
    parser.add_argument("--embed-dim", type=int, default=DEFAULT_EMBED_DIM)
    args = parser.parse_args()

    print(f"🗄  DB: {DB_PATH}")
    print(f"📐 Embed dim: {args.embed_dim}")
    print()

    conn = _conn()
    try:
        if args.check:
            verify_schema(conn)
            return

        apply_schema(conn, dry_run=False)
        setup_vec_indexes(conn, embed_dim=args.embed_dim)
        verify_schema(conn)

        print("\n✅ Migration complete. Engine v3/v4 cũ vẫn dùng passages — không bị ảnh hưởng.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
