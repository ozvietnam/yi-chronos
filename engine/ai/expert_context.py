"""RAG grounding cho council — sage trả lời CHUYÊN GIA bám sách, không chung chung.

Gốc vấn đề (founder 2026-06-24): council "chung chung, chưa chuyên gia" vì run_agent chỉ
đưa persona + chart, KHÔNG truy xuất kho sâu (17k atoms trích sách thật trong wiki.sqlite3).
→ Mỗi sage, với câu hỏi, lấy top atoms (FTS5) bơm vào prompt → sage DẪN nguyên văn sách.

Tử Vi/Chiếu Đởm lọc đúng sách Tử Vi (corpus ~90% là Tử Vi); phái khác lấy atom liên quan
nhất (không lọc). Best-effort tuyệt đối: thiếu DB / lỗi / rỗng → "" (KHÔNG chặn council).
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger("yi.expert_context")

# Sage → pattern LIKE book_corpus_id. Chỉ map sage có kho sách rõ trong wiki.sqlite3;
# sage khác = None (không lọc, lấy atom liên quan nhất — corpus hiện ~90% Tử Vi).
_CORPUS_BY_AGENT = {
    "tu_vi": "%tu%vi%",
    "chieu_dom": "%tu%vi%",      # Bắc phái 18 Phi Tinh = nhánh Tử Vi
    "hoang_cuc": "%hoang-cuc%",
    "thiet_ban": "%thiet-ban%",
}

_WIKI_DB = "data/yi_wiki/wiki.sqlite3"


@lru_cache(maxsize=1)
def _retriever():
    """Singleton retriever (tránh mở DB mỗi lượt). None nếu thiếu DB / init lỗi (cache None)."""
    try:
        from pathlib import Path

        from engine.atomization.retriever import ChunkAtomRetriever
        p = Path(_WIKI_DB)
        if not p.exists():
            return None
        return ChunkAtomRetriever(p)
    except Exception as e:
        logger.info("expert_context: retriever init lỗi → tắt RAG: %s", str(e)[:80])
        return None


def _fmt(atoms, limit: int) -> str:
    out, seen = [], set()
    for a in atoms:
        q = (getattr(a, "question_text", "") or "").strip()
        src = (getattr(a, "source_quote", None) or getattr(a, "chunk_text", "") or "").strip()
        if not src:
            continue
        src = src[:280]
        if src in seen:        # bỏ trích trùng (FTS có thể trả atom lặp)
            continue
        seen.add(src)
        out.append(f"- {q}\n  > {src}" if q else f"- > {src}")
        if len(out) >= limit:
            break
    return "\n".join(out)


def build_expert_context(question: str, agent_id: str, *, limit: int = 4) -> str:
    """Block 'TRI THỨC SÂU TỪ SÁCH' cho 1 sage trả lời câu hỏi này. '' nếu không có gì."""
    if not question or not question.strip():
        return ""
    try:
        r = _retriever()
        if r is None:
            return ""
        corpus = _CORPUS_BY_AGENT.get(agent_id)
        fetch = limit * 3   # lấy dư để sau dedup vẫn đủ
        atoms = r.search_atom_fts(question, limit=fetch, school=corpus) if corpus else []
        if not atoms:
            atoms = r.search_atom_fts(question, limit=fetch)   # fallback: không lọc phái
        body = _fmt(atoms, limit)
        if not body:
            return ""
        return ("## TRI THỨC SÂU TỪ SÁCH (trích nguyên văn — luận BÁM vào đây, "
                "DẪN tên cách/sao/nguyên lý cụ thể, KHÔNG nói chung chung)\n" + body)
    except Exception as e:
        logger.info("expert_context skip (%s): %s", agent_id, str(e)[:80])
        return ""
