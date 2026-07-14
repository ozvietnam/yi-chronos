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


def _fmt_commentary(comm: dict) -> str:
    """GAP-1: dựng khối luận giải SÂU từ atom_commentaries (đã lọc -1 ở SQL).
    Mỗi lớp 1 dòng có nhãn → council luận SÂU thay vì trích thô. '' nếu rỗng."""
    if not comm:
        return ""
    lines = []
    viet = (comm.get("viet_thuan") or "").strip()
    if viet:
        lines.append(f"    • Việt thuần: {viet[:360]}")
    ngly = (comm.get("nguyen_ly") or "").strip()
    if ngly:
        lines.append(f"    • Nguyên lý: {ngly[:360]}")
    hv = (comm.get("han_viet_explain") or "").strip()
    if hv:
        lines.append(f"    • Hán-Việt cốt: {hv[:240]}")
    vd = (comm.get("vi_du_doi_song") or "").strip()
    if vd:
        lines.append(f"    • Ví dụ đời sống: {vd[:240]}")
    csn = comm.get("cross_school_notes")
    if csn:
        if isinstance(csn, list):
            notes = []
            for it in csn[:2]:
                if isinstance(it, dict):
                    sch = (it.get("school") or "").strip()
                    note = (it.get("note") or "").strip()
                    notes.append(f"[{sch}] {note}" if sch else note)
                elif it:
                    notes.append(str(it).strip())
            csn_txt = " · ".join(n for n in notes if n)
        else:
            csn_txt = str(csn).strip()
        if csn_txt:
            lines.append(f"    • Đối chiếu phái: {csn_txt[:300]}")
    irw = (comm.get("iron_rule_warning") or "").strip()
    if irw:
        lines.append(f"    • ⚠ Paradigm (Iron #6 — không đoán cứng): {irw[:240]}")
    return "\n".join(lines)


def _fmt(atoms, limit: int) -> str:
    out, seen = [], set()
    for a in atoms:
        # dataclass AtomRetrievalInfo đặt tên field là atom_question (bug cũ đọc
        # question_text → q luôn rỗng, block mất dòng câu hỏi dẫn đầu)
        q = (getattr(a, "atom_question", "") or "").strip()
        src = (getattr(a, "source_quote", None) or getattr(a, "chunk_text", "") or "").strip()
        deep = _fmt_commentary(getattr(a, "commentary", None) or {})
        # Bỏ atom rỗng hoàn toàn (không trích, không luận giải)
        if not src and not deep:
            continue
        src = src[:280]
        # Dedup theo trích nguồn; nếu không có trích thì theo câu hỏi + luận giải
        dedup_key = src or (q + deep)[:280]
        if dedup_key in seen:        # bỏ trích trùng (FTS có thể trả atom lặp)
            continue
        seen.add(dedup_key)
        head = f"- {q}" if q else "-"
        block = [head]
        if src:
            block.append(f"  > {src}")
        if deep:
            block.append(deep)
        out.append("\n".join(block))
        if len(out) >= limit:
            break
    return "\n".join(out)


# Commentary chỉ phủ ~10% kho → tối thiểu 2/limit slot dành cho atom CÓ luận sâu
_MIN_COMMENTARY_SLOTS = 2
# Hard-cap block (chart đã chiếm ~6k trong prompt sage; block phình quá → loãng/timeout)
_MAX_BLOCK_CHARS = 6000


def build_expert_context(question: str, agent_id: str, *, limit: int = 4) -> str:
    """Block 'TRI THỨC SÂU TỪ SÁCH' cho 1 sage trả lời câu hỏi này. '' nếu không có gì.

    2-pass quota: pass 1 lấy top-k thường; nếu <2 atom trong top mang commentary
    (luận sâu) → pass 2 fetch chủ đích atom-có-commentary và dành 2 slot cuối cho
    chúng — không thì 6.458 luận sâu gần như không bao giờ lọt top-4 (~10% kho).
    """
    if not question or not question.strip():
        return ""
    try:
        r = _retriever()
        if r is None:
            return ""
        corpus = _CORPUS_BY_AGENT.get(agent_id)
        fetch = limit * 3   # lấy dư để sau dedup vẫn đủ
        # P6 (issue #61): hybrid FTS+vector KNN + lan-cạnh thay FTS thuần.
        # Tự rớt về FTS nếu LM Studio embed không sẵn (prod) → an toàn.
        atoms = r.search_atom_hybrid(question, limit=fetch, school=corpus) if corpus else []
        if not atoms:
            atoms = r.search_atom_hybrid(question, limit=fetch)   # fallback: không lọc phái

        # Pass 2 (quota): top-limit hiện tại có mấy atom mang luận sâu?
        n_comm_top = sum(1 for a in atoms[:limit] if getattr(a, "commentary", None))
        if n_comm_top < _MIN_COMMENTARY_SLOTS:
            try:
                extra = r.search_atom_fts(question, limit=_MIN_COMMENTARY_SLOTS * 2,
                                          school=corpus, require_commentary=True)
                if not extra and corpus:
                    extra = r.search_atom_fts(question, limit=_MIN_COMMENTARY_SLOTS * 2,
                                              require_commentary=True)
                seen_ids = {getattr(a, "atom_id", None) for a in atoms[:limit]}
                extra = [a for a in extra if getattr(a, "atom_id", None) not in seen_ids]
                if extra:
                    need = _MIN_COMMENTARY_SLOTS - n_comm_top
                    # giữ (limit - need) atom liên quan nhất + chèn atom luận sâu vào cuối
                    atoms = atoms[:max(limit - need, 0)] + extra[:need] + atoms[max(limit - need, 0):]
            except Exception:
                pass   # pass 2 best-effort — lỗi thì giữ nguyên pass 1

        body = _fmt(atoms, limit)
        if not body:
            return ""
        if len(body) > _MAX_BLOCK_CHARS:
            body = body[:_MAX_BLOCK_CHARS].rsplit("\n", 1)[0]
        return ("## TRI THỨC SÂU TỪ SÁCH (trích nguyên văn + LUẬN GIẢI SÂU đã thẩm — "
                "luận BÁM vào đây, DẪN tên cách/sao/nguyên lý cụ thể, vận dụng phần "
                "'Việt thuần / Nguyên lý / Đối chiếu phái', KHÔNG nói chung chung)\n" + body)
    except Exception as e:
        logger.info("expert_context skip (%s): %s", agent_id, str(e)[:80])
        return ""
