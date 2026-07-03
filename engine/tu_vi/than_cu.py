"""Thân cư — cung an Thân đóng ở đâu → trọng tâm & hậu vận đời người.

Thân luôn đóng ở 1 trong 6 cung (Mệnh/Phúc Đức/Quan Lộc/Thiên Di/Tài Bạch/Phu Thê).
"Thân đóng ở đâu thì trọng tâm cuộc đời, đặc biệt hậu vận, dồn về đó." Mỗi vị trí một
nghĩa khác — trước đây lá số CHỈ hiện chữ 'Thân' + sao Thân-chủ, KHÔNG nói Thân cư đâu.

GROUNDED (Iron #9 quote-or-silence): CHỈ trả atom ĐÃ DUYỆT (founder_verified=1) trong
wiki.sqlite3, kèm NGUỒN. Vị trí nào không có nguồn → để trống (chua_co_nguon), KHÔNG bịa.
Deterministic: than_index → cung → kéo atom 'Thân cư X'.
"""
from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

_WIKI_DB = "data/yi_wiki/wiki.sqlite3"

# Tên rút gọn khớp question_text của atom (vd cung "Phúc Đức" → atom ghi "Thân cư Phúc").
_PALACE_KEY = {
    "Mệnh": "Thân cư Mệnh",
    "Phúc Đức": "Thân cư Phúc",
    "Quan Lộc": "Thân cư Quan",
    "Thiên Di": "Thân cư Thiên Di",
    "Tài Bạch": "Thân cư Tài",
    "Phu Thê": "Thân cư Phu",
}
# corpus → nhãn nguồn thân thiện (attribution minh bạch cho người xem).
_CORPUS_LABEL = {
    "tuvi-bon-ba-tiktok": "Tử Vi Bôn Ba",
    "nguyet-do-so-menh-tiktok": "Nguyệt Đồ Số Mệnh",
    "tu-vi-huy-tuan-tiktok": "Huy Tuấn Tử Vi",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Nghiệm Lý Toàn Thư (Thiên Lương)",
    "tu-vi-dau-so-toan-thu-zh": "Tử Vi Đẩu Số Toàn Thư (cổ văn)",
}


@lru_cache(maxsize=1)
def _db() -> "sqlite3.Connection | None":
    p = Path(_WIKI_DB)
    if not p.exists():
        return None
    try:
        return sqlite3.connect(f"file:{p}?mode=ro", uri=True, check_same_thread=False)
    except Exception:
        return None


def _retrieve(palace: str, limit: int) -> list[dict]:
    """Kéo atom 'nghĩa' của Thân cư <palace> — đã duyệt, có nguồn. [] nếu không có."""
    conn = _db()
    key = _PALACE_KEY.get(palace)
    if conn is None or not key:
        return []
    like = f"%{key}%"
    try:
        # CHỈ khớp question_text (định danh CHỦ ĐỀ atom) — tránh atom nhắc-lướt vị trí
        # khác trong source_quote (vd atom liệt kê cả 6 vị trí → nhiễu chéo).
        rows = conn.execute(
            """SELECT a.source_quote, c.book_corpus_id
               FROM atomic_questions a LEFT JOIN chunks_v2 c ON a.chunk_id = c.chunk_id
               WHERE a.founder_verified = 1
                 AND a.question_text LIKE ?
                 AND (a.question_text LIKE '%nói gì%' OR a.question_text LIKE '%hậu vận%'
                      OR a.question_text LIKE '%kiểu người%' OR a.question_text LIKE '%trọng tâm%'
                      OR a.question_text LIKE '%luận%')
                 AND length(a.source_quote) > 60
               ORDER BY a.confidence DESC, length(a.source_quote) DESC
               LIMIT 12""",
            (like,),
        ).fetchall()
    except Exception:
        return []
    # Ưu tiên bản SẠCH: câu hoàn chỉnh (viết hoa đầu) > mảnh giữa-câu (thường) > bản ASR thô.
    rows = sorted(rows, key=lambda r: (_is_raw(r[0] or ""), (r[0] or "").strip()[:1].islower()))
    out: list[dict] = []
    wordsets: list[set] = []
    for quote, corpus in rows:
        q = (quote or "").strip()
        if not q or _is_meta(q):     # bỏ atom dạy-sage-tránh-nói (Mẫu SAI…) — không hiện cho user
            continue
        w = _words(q)
        # bỏ nghĩa TRÙNG nội dung (cùng ý, khác cách chép) — overlap-coefficient > 0.6.
        if any(len(w & ws) / max(1, min(len(w), len(ws))) > 0.6 for ws in wordsets):
            continue
        wordsets.append(w)
        out.append({"text": q, "source": _CORPUS_LABEL.get(corpus, corpus or "wiki")})
        if len(out) >= limit:
            break
    return out


def _is_raw(text: str) -> bool:
    """Bản chép giọng nói thô (ASR) — bắt đầu 'số N …' hoặc nhiều tiếng đệm ' à '."""
    t = (text or "").strip().lower()
    return t[:4].startswith("số ") or t.count(" à ") >= 3


def _is_meta(text: str) -> bool:
    """Atom META dạy sage TRÁNH nói (mẫu sai / cách nói sai) — KHÔNG phải nghĩa user-facing."""
    t = (text or "").strip().lower()
    return (t.startswith("mẫu sai") or t.startswith("sai:") or t.startswith("cách nói sai")
            or "mẫu sai" in t[:40] or "tránh khẳng định" in t or "không nên nói" in t)


def _words(text: str) -> set:
    import re
    return set(re.sub(r"[^\w\s]", " ", (text or "").lower()).split())


def _menh_than_axis() -> "dict | None":
    """Trục Mệnh→Thân (tiên/hậu thiên) — kéo atom NGUYÊN TẮC đã duyệt. None nếu không có."""
    conn = _db()
    if conn is None:
        return None
    try:
        row = conn.execute(
            """SELECT a.source_quote, c.book_corpus_id
               FROM atomic_questions a LEFT JOIN chunks_v2 c ON a.chunk_id = c.chunk_id
               WHERE a.founder_verified = 1 AND a.source_quote LIKE '%điều khiển nửa đời trước%'
               ORDER BY length(a.source_quote) LIMIT 1""",
        ).fetchone()
    except Exception:
        return None
    if not row or not row[0]:
        return None
    txt = row[0].strip()
    # cắt phần caveat "Tuy nhiên..." (giữ nguyên tắc gọn), nhưng KHÔNG bịa thêm.
    cut = txt.find("Tuy nhiên")
    if cut > 40:
        txt = txt[:cut].strip().rstrip(". ") + "."
    return {"text": txt, "source": _CORPUS_LABEL.get(row[1], row[1] or "wiki")}


def doc_than_cu(la_so: dict, *, limit: int = 3) -> dict:
    """Đọc Thân cư từ lá số. Trả khối grounded {than_cung, than_branch, y_nghia[], …}."""
    than_idx = la_so.get("than_index")
    palaces = la_so.get("palaces") or []
    palace = next((p for p in palaces if p.get("branch_index") == than_idx), None)
    if palace is None:
        return {"available": False}
    name = palace["name"]
    y_nghia = _retrieve(name, limit)
    return {
        "available": True,
        "than_cung": name,
        "than_branch": palace.get("branch"),
        "menh_than_dong_cung": la_so.get("menh_index") == than_idx,
        "y_nghia": y_nghia,                    # [{text, source}] — có nguồn
        "chua_co_nguon": len(y_nghia) == 0,    # True → UI hiện "chưa có nguồn", KHÔNG bịa
        "menh_than_axis": _menh_than_axis(),   # #3: trục Mệnh nửa-đầu → Thân nửa-sau (có nguồn)
    }


# ── Cục = ngũ hành NỀN của Mệnh (neo vào ngu_hanh_nen, "khớp cổ thư") ──────────
_CUC_ELEMENT = {2: ("thủy", "Thủy"), 3: ("mộc", "Mộc"), 4: ("kim", "Kim"),
                5: ("thổ", "Thổ"), 6: ("hỏa", "Hỏa")}


def doc_cuc(la_so: dict) -> dict:
    """Đọc ý nghĩa Cục = ngũ hành NỀN của Mệnh (tính chất element grounded, không bịa).
    Cục quyết định cơ học (đại vận/Trường Sinh/vị trí Tử Vi) + là hành nền của mệnh."""
    ekey_vi = _CUC_ELEMENT.get(la_so.get("cuc"))
    if not ekey_vi:
        return {"available": False}
    ekey, evi = ekey_vi
    try:
        from engine.tu_vi.ngu_hanh_nen import HANH_VAN_DONG
        nature = HANH_VAN_DONG.get(ekey, "")
    except Exception:
        nature = ""
    return {
        "available": True,
        "cuc_name": la_so.get("cuc_name"),
        "element": evi,                 # "Thổ"
        "nature": nature,               # "ổn định — nuôi giữ, chuyển hóa" (grounded)
        "source": "Ngũ hành nền (Lê Văn Sửu — khớp cổ thư)",
    }
