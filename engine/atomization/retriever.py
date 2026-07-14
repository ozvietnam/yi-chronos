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
    # GAP-1: luận giải SÂU (atom_commentaries) — chỉ điền khi atom CÓ commentary
    # founder_verified != -1 (Anh chưa bác). None nếu atom không có / bị bác.
    commentary: dict[str, Any] | None = None


def _open_db(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
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
        require_commentary: bool = False,
    ) -> list[AtomRetrievalInfo]:
        """FTS5 keyword search trên atomic_questions_fts.

        Dùng cho MVP khi chưa có embedding. Khi có embedding → swap với atom_vec.
        require_commentary: chỉ trả atom CÓ luận giải sâu (atom_commentaries) —
        dùng cho pass-2 quota của expert_context (commentary chỉ phủ ~10% kho
        nên top-k thường không dính, phải fetch chủ đích).
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
                -- GAP-1: luận giải SÂU. LOẠI commentary Anh đã bác (-1) ngay trong JOIN
                -- → atom vẫn ra (source_quote thô), chỉ commentary bị bác mới NULL.
                ac.han_viet_explain, ac.viet_thuan, ac.nguyen_ly,
                ac.vi_du_doi_song, ac.cross_school_notes, ac.iron_rule_warning,
                bm25(atomic_questions_fts) AS score
            FROM atomic_questions_fts
            JOIN atomic_questions aq ON aq.atom_id = atomic_questions_fts.rowid
            JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
            LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
            LEFT JOIN atom_commentaries ac
                   ON ac.atom_id = aq.atom_id AND ac.founder_verified >= 0
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
        if require_commentary:
            # viet_thuan là field lõi (6.456/6.458 commentary có) → proxy "có luận sâu"
            sql += " AND ac.viet_thuan IS NOT NULL"
        sql += " ORDER BY score LIMIT ?"
        params.append(k)

        conn = _open_db(self.db_path)
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            # FTS query syntax error — fallback empty
            print(f"  ⚠ FTS query error: {e}")
            return []
        finally:
            conn.close()

        # bm25 âm → flip dương (score cao = liên quan hơn)
        return [self._map_row(r, query, -float(r["score"])) for r in rows]

    # Cột + join DÙNG CHUNG cho FTS / vector KNN / lan-cạnh → cùng shape _map_row.
    _ATOM_COLS = """
        aq.atom_id, aq.question_text, aq.chunk_id,
        aq.subject_identifiers, aq.from_category, aq.source_quote,
        aq.confidence, aq.founder_verified,
        c.text AS chunk_text, c.book_corpus_id, c.page_start, c.page_end,
        cc.is_chu_the, cc.is_cong_thuc, cc.is_luan_giai,
        cc.is_to_hop, cc.is_kinh_nghiem, cc.format_style,
        ac.han_viet_explain, ac.viet_thuan, ac.nguyen_ly,
        ac.vi_du_doi_song, ac.cross_school_notes, ac.iron_rule_warning
    """
    _ATOM_JOINS = """
        FROM atomic_questions aq
        JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
        LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
        LEFT JOIN atom_commentaries ac
               ON ac.atom_id = aq.atom_id AND ac.founder_verified >= 0
    """

    @staticmethod
    def _map_row(r, query: str, score: float) -> AtomRetrievalInfo:
        """Row (đủ _ATOM_COLS) → AtomRetrievalInfo. Dùng cho MỌI đường truy xuất."""
        try:
            ids = json.loads(r["subject_identifiers"] or "{}")
        except (json.JSONDecodeError, TypeError):
            ids = {}
        archetype = {
            "is_chu_the": r["is_chu_the"] or 0,
            "is_cong_thuc": r["is_cong_thuc"] or 0,
            "is_luan_giai": r["is_luan_giai"] or 0,
            "is_to_hop": r["is_to_hop"] or 0,
            "is_kinh_nghiem": r["is_kinh_nghiem"] or 0,
        }
        # GAP-1: gom luận giải sâu (chỉ field có nội dung thật).
        comm: dict[str, Any] = {}
        for fld in ("han_viet_explain", "viet_thuan", "nguyen_ly",
                    "vi_du_doi_song", "iron_rule_warning"):
            val = (r[fld] or "").strip() if r[fld] else ""
            if val:
                comm[fld] = val
        csn_raw = (r["cross_school_notes"] or "").strip() if r["cross_school_notes"] else ""
        if csn_raw:
            try:
                parsed = json.loads(csn_raw)
                comm["cross_school_notes"] = parsed if parsed else None
            except (json.JSONDecodeError, TypeError):
                comm["cross_school_notes"] = csn_raw
            if not comm.get("cross_school_notes"):
                comm.pop("cross_school_notes", None)
        return AtomRetrievalInfo(
            atom_id=r["atom_id"],
            atom_query=query,
            atom_question=r["question_text"],
            chunk_id=r["chunk_id"],
            chunk_text=r["chunk_text"],
            source_book=r["book_corpus_id"],
            page_start=r["page_start"],
            page_end=r["page_end"],
            retrieval_score=score,
            subject_identifiers=ids,
            from_category=r["from_category"],
            source_quote=r["source_quote"],
            confidence=r["confidence"] or 0.85,
            founder_verified=r["founder_verified"] or 0,
            archetype=archetype,
            format_style=r["format_style"],
            commentary=comm or None,
        )

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
        conn = _open_db(self.db_path)
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
    # P6 (issue #61): Vector KNN + Hybrid RRF + lan-cạnh (atom_relations)
    # Biến 66k vector + 107k cạnh nằm chết thành giá trị truy xuất cho Council.
    # ─────────────────────────────────────────────────────────────
    # Cạnh MẠNH có ngữ nghĩa — BỎ 'nói-về' (92.677 = 87% nhiễu chủ-đề-lỏng, issue #61).
    _STRONG_RELS = (
        "làm-rõ-sao", "thuộc-về", "làm-rõ", "giải-thích-bằng", "là-loại-của",
        "cho-ví-dụ", "là-mảnh-của", "đồng-nghĩa-phái-khác", "dẫn-chứng", "mở-rộng",
    )

    def _embed_query(self, query: str):
        """Embed query bge-m3 1024. None nếu embedder/LM Studio không sẵn (prod) → caller rớt FTS."""
        if self.embedder is not None:
            try:
                return self.embedder(query)
            except Exception:
                return None
        try:
            from engine.yi_wiki.embeddings import embed_one
            return embed_one(query)
        except Exception:
            return None

    def _fetch_by_ids(self, atom_ids, query, scores=None, school=None):
        """Lấy đầy đủ info cho list atom_id (GIỮ thứ tự input — KNN/relation đã rank)."""
        ids = [i for i in atom_ids if i and i > 0]
        if not ids:
            return []
        ph = ",".join("?" * len(ids))
        sql = f"SELECT {self._ATOM_COLS} {self._ATOM_JOINS} WHERE aq.atom_id IN ({ph}) AND aq.founder_verified >= 0"
        params: list[Any] = list(ids)
        if school:
            sql += " AND c.book_corpus_id LIKE ?"
            params.append(school)
        conn = _open_db(self.db_path)
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            print(f"  ⚠ fetch_by_ids error: {e}")
            return []
        finally:
            conn.close()
        by_id = {r["atom_id"]: r for r in rows}
        scores = scores or {}
        out = []
        for aid in ids:
            r = by_id.get(aid)
            if r is not None:
                out.append(self._map_row(r, query, scores.get(aid, 0.0)))
        return out

    def search_atom_vec(self, query, limit=None, school=None):
        """KNN ngữ nghĩa trên atom_vec (bge-m3 1024). [] nếu embed không sẵn (→ hybrid rớt FTS)."""
        vec = self._embed_query(query)
        if not vec:
            return []
        k = limit or self.atom_retrieve_k
        conn = _open_db(self.db_path)
        try:
            import sqlite_vec
            qv = sqlite_vec.serialize_float32(vec)
            rows = conn.execute(
                "SELECT atom_id, distance FROM atom_vec WHERE embedding MATCH ? AND k = ? ORDER BY distance",
                (qv, k * 4),  # lấy dư để lọc phái/founder sau
            ).fetchall()
        except Exception as e:
            print(f"  ⚠ vec KNN error: {str(e)[:80]}")
            return []
        finally:
            conn.close()
        scores = {r["atom_id"]: 1.0 / (1.0 + float(r["distance"])) for r in rows}  # gần→điểm cao
        infos = self._fetch_by_ids([r["atom_id"] for r in rows], query, scores, school=school)
        return infos[:k]

    def expand_via_relations(self, seed_atom_ids, query, limit=4, school=None):
        """Lan 1 bước theo cạnh MẠNH (2 chiều) từ seed atoms → atoms liên đới có ngữ nghĩa."""
        seeds = [i for i in seed_atom_ids if i and i > 0][:12]
        if not seeds:
            return []
        sph = ",".join("?" * len(seeds))
        rph = ",".join("?" * len(self._STRONG_RELS))
        sql = (
            f"SELECT to_atom_id AS nb FROM atom_relations "
            f"WHERE from_atom_id IN ({sph}) AND relation_type IN ({rph}) "
            f"UNION SELECT from_atom_id AS nb FROM atom_relations "
            f"WHERE to_atom_id IN ({sph}) AND relation_type IN ({rph})"
        )
        conn = _open_db(self.db_path)
        try:
            rows = conn.execute(
                sql, seeds + list(self._STRONG_RELS) + seeds + list(self._STRONG_RELS)
            ).fetchall()
        except sqlite3.OperationalError as e:
            print(f"  ⚠ expand error: {e}")
            return []
        finally:
            conn.close()
        seed_set = set(seeds)
        nb_ids = [r["nb"] for r in rows if r["nb"] and r["nb"] not in seed_set][: limit * 3]
        return self._fetch_by_ids(nb_ids, query, school=school)[:limit]

    def search_atom_hybrid(self, query, limit=None, school=None, expand=True):
        """FTS + vector KNN hợp nhất (RRF) + lan-cạnh. RỚT về FTS nếu vector không sẵn (prod)."""
        k = limit or self.atom_retrieve_k
        fts = self.search_atom_fts(query, limit=k * 2, school=school)
        vec = self.search_atom_vec(query, limit=k * 2, school=school)
        if not vec:
            return fts[:k]  # graceful degrade: không LM Studio → FTS thuần (prod)
        # Reciprocal Rank Fusion: score = Σ 1/(C+rank) qua 2 danh sách (C=60 chuẩn)
        C = 60
        rrf: dict[int, float] = {}
        info_by_id: dict[int, AtomRetrievalInfo] = {}
        for lst in (fts, vec):
            for rank, a in enumerate(lst):
                if a.atom_id <= 0:
                    continue
                rrf[a.atom_id] = rrf.get(a.atom_id, 0.0) + 1.0 / (C + rank)
                info_by_id.setdefault(a.atom_id, a)
        ranked = sorted(rrf, key=lambda i: rrf[i], reverse=True)
        fused = []
        for i in ranked:
            a = info_by_id[i]
            a.retrieval_score = rrf[i]
            fused.append(a)
        top = fused[:k]
        if expand and top:
            have = {a.atom_id for a in top}
            extra = [a for a in self.expand_via_relations(
                        [a.atom_id for a in top[:6]], query, limit=max(2, k // 4), school=school)
                     if a.atom_id not in have]
            top = top + extra
        return top

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
