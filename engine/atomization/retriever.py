"""ChunkAtomRetriever — Port PIKE-RAG architecture sang SQLite + sqlite-vec.

2-store architecture:
- chunks_v2 + chunks_vec_v2 (chunk text + embedding)
- atomic_questions + atom_vec (atomic Q + embedding)

4 retrieval methods (PIKE-RAG paradigm):
- retrieve_atom_info_through_atom(queries) — atomic Q semantic search
- retrieve_atom_info_through_chunk(query) — chunk semantic, best-hit atom
- retrieve_contents_by_query(query) — combine both paths, dedup
- search_atom_fts(query) — FTS5 fallback nếu vec không có embedding

Embedding: dùng provider có sẵn. MVP: text-embedding-3-small ($0.02/1M).
Fallback: nếu không có OpenAI key → BM25-like FTS5 only.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


@dataclass
class AtomRetrievalInfo:
    """Match PIKE-RAG paradigm + yi-chronos specifics."""
    atom_id: int
    atom_query: str                  # query gốc của user
    atom_question: str               # atomic Q matched
    chunk_id: int
    chunk_text: str                  # ENTIRE chunk, KHÔNG nén
    source_book: str
    page_start: int
    page_end: int
    retrieval_score: float
    # Tử Vi specific
    subject_identifiers: dict[str, Any] = field(default_factory=dict)
    from_category: str | None = None
    source_quote: str | None = None
    confidence: float = 0.85
    founder_verified: int = 0
    archetype: dict[str, int] = field(default_factory=dict)
    format_style: str | None = None


def _open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    # Try load vec extension
    try:
        import sqlite_vec
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
    except (ImportError, sqlite3.OperationalError):
        pass
    conn.row_factory = sqlite3.Row
    return conn


class ChunkAtomRetriever:
    """yi-chronos equivalent of PIKE-RAG ChunkAtomRetriever.

    NOTE: MVP version dùng FTS5 + denormalized atom_q_str. Vec embedding sẽ
    add sau khi có embedding provider configured.
    """

    def __init__(
        self,
        db_path: Path = DB_PATH,
        embedder: Callable[[str], list[float]] | None = None,
        retrieve_k: int = 16,
        atom_retrieve_k: int = 8,
        threshold_chunk: float = 0.2,
        threshold_atom: float = 0.5,
    ):
        self.db_path = db_path
        self.embedder = embedder
        self.retrieve_k = retrieve_k
        self.atom_retrieve_k = atom_retrieve_k
        self.threshold_chunk = threshold_chunk
        self.threshold_atom = threshold_atom

    # ─────────────────────────────────────────────────────────────
    # FTS5 retrieval (MVP baseline, không cần embedding)
    # ─────────────────────────────────────────────────────────────
    def search_atom_fts(
        self,
        query: str,
        limit: int | None = None,
        school: str | None = None,
    ) -> list[AtomRetrievalInfo]:
        """FTS5 keyword search trên atomic_questions_fts.

        Dùng cho MVP khi chưa có embedding. Khi có embedding → swap với atom_vec.
        """
        k = limit or self.atom_retrieve_k
        # "Một fact nhiều tên gọi" (Anh chốt 2026-06-11): expand biệt danh qua wiki
        # → tìm SONG SONG mọi tên gọi (Đế tinh OR Tử Vi OR Đế tọa...) ra hết kết quả.
        try:
            from engine.tu_vi.star_aliases import expand_search_terms
            terms = expand_search_terms(query)
        except Exception:
            terms = [query]
        if len(terms) > 1:
            # Mỗi term là 1 phrase (giữ nguyên cụm "Đế tinh"), strip quote nội bộ
            phrases = []
            for t in terms[:12]:
                clean = t.replace('"', " ").strip()
                if clean:
                    phrases.append(f'"{clean}"')
            safe_query = " OR ".join(phrases) if phrases else self._sanitize_fts_query(query)
        else:
            # Sanitize query — FTS5 cần escape special chars
            safe_query = self._sanitize_fts_query(query)
        sql = """
            SELECT
                aq.atom_id, aq.question_text, aq.chunk_id,
                aq.subject_identifiers, aq.from_category, aq.source_quote,
                aq.confidence, aq.founder_verified,
                c.text AS chunk_text, c.book_corpus_id, c.page_start, c.page_end,
                cc.is_chu_the, cc.is_cong_thuc, cc.is_luan_giai,
                cc.is_to_hop, cc.is_kinh_nghiem, cc.format_style,
                bm25(atomic_questions_fts) AS score
            FROM atomic_questions_fts
            JOIN atomic_questions aq ON aq.atom_id = atomic_questions_fts.rowid
            JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
            LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
            WHERE atomic_questions_fts MATCH ?
              -- Iron #9 / M0-C: LOẠI atom Anh đã bác (founder_verified = -1) khỏi
              -- retrieval → council/sage KHÔNG dẫn tri thức đã bị bác. Giữ 0 (chưa
              -- duyệt) + 1 (duyệt dương) vì hiện 0 atom duyệt dương → require dương = rỗng.
              AND aq.founder_verified >= 0
        """
        params: list[Any] = [safe_query]
        if school:
            sql += " AND c.book_corpus_id LIKE ?"
            params.append(f"%{school}%")
        sql += " ORDER BY score LIMIT ?"
        params.append(k)

        conn = _open_db()
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            # FTS query syntax error — fallback empty
            print(f"  ⚠ FTS query error: {e}")
            return []
        finally:
            conn.close()

        results = []
        for r in rows:
            try:
                ids = json.loads(r["subject_identifiers"] or "{}")
            except json.JSONDecodeError:
                ids = {}
            archetype = {
                "is_chu_the": r["is_chu_the"] or 0,
                "is_cong_thuc": r["is_cong_thuc"] or 0,
                "is_luan_giai": r["is_luan_giai"] or 0,
                "is_to_hop": r["is_to_hop"] or 0,
                "is_kinh_nghiem": r["is_kinh_nghiem"] or 0,
            }
            results.append(AtomRetrievalInfo(
                atom_id=r["atom_id"],
                atom_query=query,
                atom_question=r["question_text"],
                chunk_id=r["chunk_id"],
                chunk_text=r["chunk_text"],
                source_book=r["book_corpus_id"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                retrieval_score=-float(r["score"]),  # bm25 negative, flip
                subject_identifiers=ids,
                from_category=r["from_category"],
                source_quote=r["source_quote"],
                confidence=r["confidence"] or 0.85,
                founder_verified=r["founder_verified"] or 0,
                archetype=archetype,
                format_style=r["format_style"],
            ))
        return results

    def search_chunk_fts(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[AtomRetrievalInfo]:
        """FTS5 trên chunks_v2_fts — fallback path."""
        k = limit or self.retrieve_k
        safe_query = self._sanitize_fts_query(query)
        sql = """
            SELECT
                c.chunk_id, c.text, c.book_corpus_id, c.page_start, c.page_end,
                c.atom_q_str,
                bm25(chunks_v2_fts) AS score
            FROM chunks_v2_fts
            JOIN chunks_v2 c ON c.chunk_id = chunks_v2_fts.rowid
            WHERE chunks_v2_fts MATCH ?
            ORDER BY score LIMIT ?
        """
        conn = _open_db()
        try:
            rows = conn.execute(sql, (safe_query, k)).fetchall()
        except sqlite3.OperationalError as e:
            print(f"  ⚠ Chunk FTS error: {e}")
            return []
        finally:
            conn.close()

        results = []
        for r in rows:
            # Build pseudo AtomRetrievalInfo (no specific atom matched, chunk-level)
            atom_str = r["atom_q_str"] or ""
            best_atom = atom_str.split("\n")[0] if atom_str else "(no atom)"
            results.append(AtomRetrievalInfo(
                atom_id=-1,  # no atom
                atom_query=query,
                atom_question=best_atom,
                chunk_id=r["chunk_id"],
                chunk_text=r["text"],
                source_book=r["book_corpus_id"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                retrieval_score=-float(r["score"]),
            ))
        return results

    @staticmethod
    def _sanitize_fts_query(q: str) -> str:
        """FTS5 syntax-safe: phrase query với each word."""
        # Strip dangerous chars, keep VI chars
        words = [w.strip() for w in q.split() if len(w.strip()) >= 2]
        # Quote each word to avoid FTS5 operator interpretation
        quoted = [f'"{w}"' for w in words if all(c.isalnum() or c in "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ" for c in w)]
        if not quoted:
            return '""'
        # OR-join → match any
        return " OR ".join(quoted)

    # ─────────────────────────────────────────────────────────────
    # Combined retrieval (3-level fallback PIKE-RAG)
    # ─────────────────────────────────────────────────────────────
    def retrieve_atoms(
        self,
        atomic_queries: list[str],
        original_query: str,
        chosen_chunk_ids: set[int] | None = None,
    ) -> list[AtomRetrievalInfo]:
        """3-level fallback PIKE-RAG:
        1. atomic_queries → atom_store (FTS or vec)
        2. original_query → atom_store
        3. original_query → chunk_store
        Filter dup chunks.
        """
        chosen = chosen_chunk_ids or set()

        # Level 1: atomic queries via atoms
        results = []
        for q in atomic_queries:
            results.extend(self.search_atom_fts(q))
        results = [r for r in results if r.chunk_id not in chosen]
        if results:
            return self._dedup_by_atom_id(results)

        # Level 2: original query via atoms
        results = self.search_atom_fts(original_query)
        results = [r for r in results if r.chunk_id not in chosen]
        if results:
            return self._dedup_by_atom_id(results)

        # Level 3: original query via chunks
        results = self.search_chunk_fts(original_query)
        results = [r for r in results if r.chunk_id not in chosen]
        return self._dedup_by_atom_id(results)

    @staticmethod
    def _dedup_by_atom_id(results: list[AtomRetrievalInfo]) -> list[AtomRetrievalInfo]:
        seen = set()
        out = []
        for r in results:
            key = r.atom_id if r.atom_id > 0 else r.chunk_id
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
        return out


if __name__ == "__main__":
    # Smoke test
    r = ChunkAtomRetriever()
    print("🔍 Test search_atom_fts với 'Vũ Khúc Phá Quân':")
    hits = r.search_atom_fts("Vũ Khúc Phá Quân", limit=5)
    for h in hits[:5]:
        print(f"  • {h.atom_question[:80]}")
        print(f"    chunk_id={h.chunk_id} · p{h.page_start} · score={h.retrieval_score:.2f}")
        print(f"    cat: {h.from_category}")
        print()
