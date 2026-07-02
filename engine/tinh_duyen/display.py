"""Lớp TRÌNH BÀY dùng chung web + AppChat cho read_tinh_duyen.

`build_display(reading_output, gender)` map output thô của
`engine.tinh_duyen.reading.read_tinh_duyen` → một cấu trúc {meta, sections}
SẠCH, CÓ THỨ TỰ, ĐÃ ẨN internal — render được trực tiếp ở cả 2 nơi:

- Web YI-Chronos (Vue): mỗi section.kind → 1 widget (dùng --read-* tokens).
- AppChat (prvchat): sections là JSON THUẦN (kind→widget), KHÔNG HTML.

ĐÂY LÀ PRESENTATION — KHÔNG đổi mệnh-lý, KHÔNG bịa: chỉ map cái có thật trong
reading_output. Giữ paradigm (Iron Rule #4/#6/#8): disclaimer ở meta + phác hoạ
mang nghĩa biểu tượng.

Quy tắc chính:
- Cấp độ thử thách (cap_do) là KILLER → LÊN ĐẦU sections.
- ẨN khỏi sections: base_12_khia_canh, scrub_caution_count, method_id nội bộ,
  các _nguon rải rác (GOM vào section 'nguon').
- Section RỖNG (không có data/items) → BỎ khỏi list.
- Title + meta.phoi_ngau gender-aware: NỮ → 'chồng', NAM → 'vợ'.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from . import knowledge_loader as kb

# Token giới NỮ: mặc định engine cho nữ mệnh.
_FEMALE_TOKENS = ("nữ", "nu", "female", "f", "")

# Dải Hán (CJK Unified Ideographs cơ bản). Strip để text KẾT QUẢ thuần Việt.
_HAN_RE = re.compile(r"[一-鿿]+")
# Ngoặc rỗng còn lại sau khi xoá Hán: () （） [] 【】 「」 + bên trong chỉ
# khoảng trắng / dấu phân cách.
_EMPTY_PAREN_RE = re.compile(r"[\(\（\[【「]\s*[,，;；·、\-—\s]*\s*[\)\）\]】」]")
# Dấu câu mồ côi đầu cụm sau khi xoá Hán (vd ' — ' đứng đầu / lặp).
_STRAY_LEAD_RE = re.compile(r"(^|[\(\（\[【「])\s*[,，;；·、]+\s*")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+([,，.。;；:：!！?？\)\）\]】」])")
# Chú dẫn INTERNAL của engine lọt vào prose: 'xem lo_trinh_ren.cu_mon_sang_kheo_loi'
# (key chấm-nối nội bộ, KHÔNG có nghĩa với user). Strip riêng cho KẾT QUẢ (tom_tat),
# giữ nguyên trong data/can_cu. Bắt cả khi đứng sau ' — ' hoặc trong '(..., xem X)'.
_INTERNAL_REF_RE = re.compile(
    r"\s*(?:[—\-,，;；]\s*)?xem\s+[a-z_][a-z0-9_]*(?:\.[a-z0-9_]+)+\s*"
)


def _is_female(gender: str) -> bool:
    return (gender or "").strip().lower() in _FEMALE_TOKENS


def _strip_han(text: Any) -> Any:
    """Xoá MỌI ký tự Hán [一-鿿] khỏi text + dọn ngoặc rỗng + space thừa.

    Dùng cho MỌI text trong `tom_tat` để user chỉ thấy KẾT QUẢ tiếng Việt thuần
    (CÔNG THỨC chữ Hán đẩy xuống `can_cu`). KHÔNG đổi nội dung non-str (None,
    số, bool... trả nguyên); list/dict → strip đệ quy từng phần tử."""
    if text is None or isinstance(text, bool):
        return text
    if isinstance(text, (int, float)):
        return text
    if isinstance(text, list):
        return [_strip_han(x) for x in text]
    if isinstance(text, tuple):
        return tuple(_strip_han(x) for x in text)
    if isinstance(text, dict):
        return {k: _strip_han(v) for k, v in text.items()}
    if not isinstance(text, str):
        return text
    s = _HAN_RE.sub("", text)
    # Dọn ngoặc rỗng (lặp tới khi ổn định — ngoặc lồng).
    prev = None
    while prev != s:
        prev = s
        s = _EMPTY_PAREN_RE.sub("", s)
    s = _STRAY_LEAD_RE.sub(r"\1", s)
    s = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", s)
    s = _MULTI_SPACE_RE.sub(" ", s)
    # Gọn dấu nối mồ côi liền nhau & space quanh dấu —.
    s = re.sub(r"\s*—\s*—\s*", " — ", s)
    s = re.sub(r"(^|[(\（])\s*—\s*", r"\1", s)
    s = re.sub(r"\s*—\s*$", "", s.strip())
    return s.strip()


def _strip_internal_ref(text: Any) -> Any:
    """Xoá chú dẫn INTERNAL 'xem <key.dotted>' khỏi prose KẾT QUẢ (tom_tat).

    Đây là con trỏ nội bộ engine (vd 'xem lo_trinh_ren.cu_mon_sang_kheo_loi') —
    vô nghĩa với user, lọt từ knowledge JSON. CHỈ dùng cho tom_tat; data/can_cu
    giữ NGUYÊN để trace. KHÔNG bịa nội dung, chỉ bỏ con trỏ. Đệ quy list/dict;
    dọn lại ngoặc rỗng + dấu mồ côi giống _strip_han."""
    if text is None or isinstance(text, bool):
        return text
    if isinstance(text, (int, float)):
        return text
    if isinstance(text, list):
        return [_strip_internal_ref(x) for x in text]
    if isinstance(text, tuple):
        return tuple(_strip_internal_ref(x) for x in text)
    if isinstance(text, dict):
        return {k: _strip_internal_ref(v) for k, v in text.items()}
    if not isinstance(text, str):
        return text
    s = _INTERNAL_REF_RE.sub("", text)
    if s == text:
        return text
    # Dọn ngoặc rỗng / dấu mồ côi còn lại (vd '(khéo lời, )' → '(khéo lời)').
    prev = None
    while prev != s:
        prev = s
        s = _EMPTY_PAREN_RE.sub("", s)
        s = re.sub(r"([\(\（\[【「][^\)\）\]】」]*?)[\s,，;；·、]+([\)\）\]】」])",
                   r"\1\2", s)
    s = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", s)
    s = _MULTI_SPACE_RE.sub(" ", s)
    s = re.sub(r"\s*—\s*$", "", s.strip())
    s = re.sub(r"\s*\.\s*\.", ".", s)
    return s.strip()


# --------------------------------------------------------------------------- #
# Tầng NGHĨA THUẦN (_plain_vi) — biến text kỹ thuật thành nghĩa đời thường.
# Glossary: engine/tinh_duyen/knowledge/plain_glossary.json (thay_the + is_jargon).
# Mục tiêu: tom_tat còn lại là NGHĨA đời thường (KHÔNG tên sao / thập thần / lý-thuật
# / Hán). Jargon đẩy xuống can_cu (giữ nguyên ở data/can_cu).
# --------------------------------------------------------------------------- #
# Cache regex đã compile cho scrub_phrases_regex (BUG4) — key = id(glossary).
_SCRUB_CACHE: dict[int, list] = {}


def _load_glossary() -> dict:
    """Trả plain_glossary (cached qua knowledge_loader). Lỗi → fallback rỗng."""
    try:
        return kb.get("plain_glossary") or {}
    except Exception:
        return {}


def _glossary_jargon(glossary: dict) -> list[str]:
    """Gom MỌI token jargon (tên sao + thập thần + lý-thuật + can-chi) từ
    is_jargon, sắp DÀI trước (tránh thay/khớp lồng vd 'Thiên Tài' trước 'Tài')."""
    ij = (glossary or {}).get("is_jargon") or {}
    toks: list[str] = []
    for grp in ("ten_sao", "thap_than", "ly_thuat", "can_chi"):
        for t in ij.get(grp) or []:
            if isinstance(t, str) and t.strip():
                toks.append(t)
    # Dedup giữ thứ tự rồi sắp dài→ngắn.
    seen: set[str] = set()
    uniq = [t for t in toks if not (t in seen or seen.add(t))]
    uniq.sort(key=len, reverse=True)
    return uniq


# Dấu kết câu/phân cách để cắt mệnh đề (sau khi xoá jargon, mệnh đề rỗng → bỏ).
_CLAUSE_SPLIT_RE = re.compile(r"([;；,，—]|\s-\s)")
# Mệnh đề CHỈ còn rác (dấu / khoảng trắng / dăm liên-từ rỗng nghĩa) → bỏ.
_JUNK_CLAUSE_RE = re.compile(
    r"^[\s,，;；·、\-—()（）\[\]【】「」]*"
    r"(?:và|hoặc|thì|là|chủ|chứ|nên|mà|ở|tại|khi|của|cho|với|→|=)?"
    r"[\s,，;；·、\-—()（）\[\]【】「」]*$"
)


# Toán-tử ráp (label/định-vị) bị MỒ CÔI sau khi strip jargon. BUG3.
# Định-vị treo: 'tại <chi/sao đã strip>' → còn 'tại' lơ lửng + (toán tử / ngoặc
# rỗng / dấu câu / verb tiếp). Object định-vị LUÔN là jargon (chi/tên-sao) nên đã
# bị strip; 'tại' còn trơ = rác. Bắt: locative + (toán tử '='/':') HOẶC + ngoặc
# (sắp rỗng) HOẶC + dấu câu → bỏ cả locative.
_ORPHAN_LOCATIVE_OP_RE = re.compile(
    r"\b(?:tại|ở|nơi|vào|đóng|toạ|tọa|cư)\s*"
    r"(?:[=:：]+|[\(\（][\s,，;；·、\-—]*[\)\）]|(?=[,，.。;；—]))",
)
# Locative + (đã mất noun-object) đứng trước VỊ-NGỮ thường (chữ thường tiếng Việt):
# 'tại phản chiếu', 'tại giao hữu' → object (chi/sao Viết-HOA) đã strip nên 'tại'
# trơ. Tên ĐỊA-DANH thật sau 'tại' luôn VIẾT HOA ('tại Hà Nội') nên KHÔNG khớp
# (an toàn). Chỉ bỏ chữ định-vị, GIỮ vị-ngữ.
_ORPHAN_LOCATIVE_VERB_RE = re.compile(
    r"\b(?:tại|toạ|tọa|đóng|cư)\s+(?=[a-zà-ỹ])(?!sao\b|vì\b|đây\b|đó\b|chỗ\b|gia\b)",
)
# '=' mồ côi (không phải trong biểu thức số): bỏ, để space nối 2 vế.
_ORPHAN_EQUALS_RE = re.compile(r"\s*=+\s*")
# Cluster dấu câu trộn ':' '.' ',' ';' '…' liền nhau (>=2 dấu) → còn 1 dấu mạnh nhất.
_PUNCT_CLUSTER_RE = re.compile(r"[\s]*[:：.,，;；…]{2,}[\s]*")
# ':' / '：' mồ côi: đứng đầu cụm, hoặc ngay sau '(' / dấu phẩy, hoặc cuối cụm.
_ORPHAN_COLON_RE = re.compile(
    r"(^|[\(\（\[【「,，;；—\-])\s*[:：]+\s*"
)
_TRAILING_COLON_RE = re.compile(r"\s*[:：]+\s*$")


def _strip_orphan_operators(s: str) -> str:
    """Bỏ TOÁN-TỬ ráp mồ côi (':', '=', cluster ',:.:') còn lại sau khi strip
    jargon. Vế dữ-liệu (label/tên-cung/tên-sao) đã bị xoá nên dấu nối thành rác.

    KHÔNG đụng ':' HỢP LỆ (có chữ 2 bên, vd 'kết luận: ...') — chỉ bỏ khi 1 vế trống
    (đầu/cuối cụm, sau '(' / dấu phẩy). Cluster (>=2 dấu trộn) → 1 dấu mạnh nhất."""
    if not isinstance(s, str) or not s:
        return s
    # 1) Định-vị treo + toán tử ('tại =', 'ở :', 'tại ()') → bỏ cả cụm.
    s = _ORPHAN_LOCATIVE_OP_RE.sub(" ", s)
    # 1b) Định-vị treo trước vị-ngữ thường ('tại phản chiếu') → bỏ chữ định-vị.
    s = _ORPHAN_LOCATIVE_VERB_RE.sub("", s)
    # 1c) '/' mồ côi do strip 1 vế ('Tham Lang/đào hoa' → '/đào hoa'): bỏ slash treo.
    s = re.sub(r"(^|[\s(（])/+\s*", r"\1", s)   # '/' đầu cụm / sau space
    s = re.sub(r"\s*/+(?=[\s)）]|$)", "", s)     # '/' cuối cụm / trước space
    # 2) Cluster dấu trộn ',:.:' / ': :' / '…:' → 1 dấu (ưu tiên kết câu '.' > ';' > ',').
    def _pick_punct(m: "re.Match") -> str:
        chunk = m.group(0)
        for p in (".", "。"):
            if p in chunk:
                return p + " "
        for p in (";", "；"):
            if p in chunk:
                return p + " "
        if "," in chunk or "，" in chunk:
            return ", "
        return " "
    s = _PUNCT_CLUSTER_RE.sub(_pick_punct, s)
    # 3) ':' mồ côi (1 vế trống) → bỏ.
    s = _ORPHAN_COLON_RE.sub(r"\1 ", s)
    s = _TRAILING_COLON_RE.sub("", s)
    # 4) '=' mồ côi còn sót → bỏ (nối 2 vế bằng space).
    s = _ORPHAN_EQUALS_RE.sub(" ", s)
    return s


def _compile_scrub_patterns(glossary: dict) -> list[tuple["re.Pattern", str]]:
    """BUG4 — compile các regex 'scrub_phrases_regex' từ glossary (cụm jargon CÓ
    BIẾN THỂ: 'Nam/Bắc Đẩu đệ X tinh', '(âm/dương <hành>)', 'X chi tinh', 'hóa khí
    vi Y'). Cache theo id(glossary) để khỏi recompile mỗi chuỗi. Pattern lỗi → bỏ
    qua (an toàn, không vỡ tom_tat)."""
    cache_key = id(glossary)
    cached = _SCRUB_CACHE.get(cache_key)
    if cached is not None:
        return cached
    out: list[tuple["re.Pattern", str]] = []
    block = (glossary or {}).get("scrub_phrases_regex") or {}
    for item in block.get("patterns") or []:
        pat = item.get("pattern")
        if not isinstance(pat, str) or not pat:
            continue
        try:
            out.append((re.compile(pat), item.get("thay") or ""))
        except re.error:
            continue
    _SCRUB_CACHE[cache_key] = out
    return out


def _plain_one(s: str, glossary: dict, jargon: list[str]) -> str:
    """Thuần 1 chuỗi: strip Hán + bỏ con trỏ internal + scrub cụm-jargon-biến-thể
    (Nam/Bắc Đẩu đệ X tinh, hành âm-dương, 'X chi tinh', 'hóa khí vi Y') + áp
    thay_the (jargon→nghĩa đời thường hoặc bỏ) + xoá jargon còn sót + dọn mệnh đề
    rỗng + dấu mồ côi."""
    if not isinstance(s, str) or not s.strip():
        return s
    out = _strip_internal_ref(_strip_han(s))
    if not isinstance(out, str):
        return out
    # 0) BUG4 — scrub cụm jargon CÓ BIẾN THỂ trước thay_the (xoá hẳn khỏi KẾT QUẢ).
    for pat, rep in _compile_scrub_patterns(glossary):
        out = pat.sub(rep, out)
    thay_the = (glossary or {}).get("thay_the") or {}
    # 1) Thay theo thay_the (key DÀI trước để tránh thay lồng).
    for k in sorted(thay_the.keys(), key=len, reverse=True):
        if k and k in out:
            out = out.replace(k, thay_the[k])
    # 2) Xoá jargon còn sót (tên sao / thập thần / lý-thuật / can-chi) — chưa được
    #    thay_the và không có nghĩa đời thường → bỏ token (để lại nghĩa quanh nó).
    #    2a-PRE) Nếu jargon đi LIỀN 1 chú-giải đời thường trong ngoặc — 'Tham Lang
    #    (khí ham sống mãnh liệt)' — thì THĂNG chú-giải lên (bỏ ngoặc, giữ nghĩa)
    #    thay vì xoá tên sao để lại '(khí ham sống...)' mồ côi. Chỉ promote khi nội
    #    dung ngoặc KHÔNG còn jargon (nếu còn thì để bước xoá thường xử lý).
    for tok in jargon:
        if not tok or tok not in out:
            continue
        # 'Tok (gloss)' / 'Tok(gloss)' → 'gloss'. gloss = chuỗi không lồng ngoặc.
        pat = re.compile(
            re.escape(tok) + r"\s*[\(\（]([^\(\)\（\）]*?)[\)\）]"
        )

        def _promote(m: "re.Match") -> str:
            inner = (m.group(1) or "").strip()
            return inner if inner else ""

        out = pat.sub(_promote, out)
    # 2b-PRE) Xoá jargon còn sót (token trần, không kèm chú-giải) → bỏ token.
    for tok in jargon:
        if tok and tok in out:
            out = out.replace(tok, "")
    # 2b) Dọn rác do xoá token: dấu '/' mồ côi (vd 'Tỵ/Hợi hãm'→' / ' ), và giới
    #     từ định-vị treo lơ lửng đầu mệnh đề ('ở / là'→'là', 'tại là'→'là').
    out = re.sub(r"\s*/\s*(?=[/\s]|$)", " ", out)          # slash mồ côi liên tiếp
    out = re.sub(r"\s+/\s+", " ", out)                       # ' / ' còn lại
    out = re.sub(r"\b(ở|tại|nơi|vào)\s+(?=(?:là|và|thì|,|;|—|\.|$))",
                 "", out)                                    # giới từ định-vị treo
    out = re.sub(r"\(\s*([+,，;；·、]\s*)", "(", out)        # '(+ đào hoa' → '(đào hoa'
    # 3) Cắt mệnh đề; mệnh đề nào CHỈ còn rác (jargon đã xoá → trống) → loại.
    parts = _CLAUSE_SPLIT_RE.split(out)
    kept: list[str] = []
    for p in parts:
        if p is None:
            continue
        # Giữ lại dấu phân cách chỉ khi 2 bên đều có nội dung (xử ở bước ghép).
        if _CLAUSE_SPLIT_RE.fullmatch(p or ""):
            kept.append(p)
            continue
        if _JUNK_CLAUSE_RE.match(p):
            kept.append("")  # đánh dấu mệnh đề rỗng
        else:
            kept.append(p)
    # Ghép lại: bỏ mệnh đề rỗng + dấu phân cách mồ côi quanh nó.
    rebuilt = ""
    for i, p in enumerate(kept):
        if _CLAUSE_SPLIT_RE.fullmatch(p or ""):
            # Chỉ giữ dấu nếu sẽ có nội dung phía sau.
            tail = "".join(x for x in kept[i + 1:]
                           if not _CLAUSE_SPLIT_RE.fullmatch(x or ""))
            if rebuilt.strip() and tail.strip():
                rebuilt += p if p.strip() else ", "
        else:
            rebuilt += p
    out = rebuilt
    # 3b) BUG3 — dọn DẤU MỒ CÔI để lại sau khi strip jargon (tên sao/cung/chi/Hán):
    #     'Cung Nô Bộc tại Thân (…) =' → strip 'Thân'+'(…)' để lại 'tại =';
    #     'Tham Lang: …' → ': …'; cluster ',:.:' / ': :'. Các dấu ':' '=' này là
    #     TOÁN-TỬ ráp (label/định-vị) đã mất vế jargon → bỏ, KHÔNG để rác lên UI.
    out = _strip_orphan_operators(out)
    # 4) Dọn ngoặc rỗng, space thừa, dấu mồ côi (tái dùng regex _strip_han).
    prev = None
    while prev != out:
        prev = out
        out = _EMPTY_PAREN_RE.sub("", out)
    out = _STRAY_LEAD_RE.sub(r"\1", out)
    out = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", out)
    out = _MULTI_SPACE_RE.sub(" ", out)
    out = re.sub(r"[,，;；]\s*([,，;；.。])", r"\1", out)   # dấu đôi mồ côi
    out = re.sub(r"\(\s*\)", "", out)
    out = re.sub(r"\s+([,，.。;；:：!！?？])", r"\1", out)
    out = re.sub(r"^[\s,，;；·、\-—]+", "", out)
    out = re.sub(r"\s*[—\-]\s*$", "", out.strip())
    # Quét dấu mồ côi 1 lần nữa sau khi gộp space (cluster có thể lộ ra).
    out = _strip_orphan_operators(out)
    return out.strip()


def _plain_vi(text: Any, glossary: Optional[dict] = None) -> Any:
    """Biến text → NGHĨA THUẦN đời thường (đệ quy list/dict/tuple).

    - strip Hán + bỏ con trỏ internal 'xem X.Y'
    - áp glossary.thay_the (đại vận→giai đoạn, lưu niên→năm, 'năm Hồng Loan tới'→
      'năm có khí vui/duyên', cung Phu Thê→chuyện bạn đời...)
    - xoá jargon còn sót (tên sao / thập thần / hãm-miếu / can-chi)
    - dọn mệnh đề chỉ còn jargon + dấu mồ côi

    KHÔNG bịa nghĩa mới — chỉ DIỄN ĐẠT LẠI cái đã có. Non-str (None/số/bool) →
    trả nguyên."""
    if glossary is None:
        glossary = _load_glossary()
    jargon = _glossary_jargon(glossary)
    if text is None or isinstance(text, bool):
        return text
    if isinstance(text, (int, float)):
        return text
    if isinstance(text, list):
        return [_plain_vi(x, glossary) for x in text]
    if isinstance(text, tuple):
        return tuple(_plain_vi(x, glossary) for x in text)
    if isinstance(text, dict):
        return {k: _plain_vi(v, glossary) for k, v in text.items()}
    if not isinstance(text, str):
        return text
    return _plain_one(text, glossary, jargon)


# Marker dẫn vào KẾT LUẬN đời thường trong reconcile prose (cơ chế ở trước marker
# là kỹ thuật; sau marker là câu nói-thẳng cho user). Lấy ĐOẠN SAU marker cuối.
_TAKEAWAY_MARKER_RE = re.compile(
    r"(?:nói thẳng được|kết luận chắc|kết luận|hội tụ[^:：.]*|nói thẳng)\s*[:：]\s*",
    re.IGNORECASE,
)


def _takeaway_clause(text: Any) -> Any:
    """Trả ĐOẠN KẾT LUẬN đời thường của reconcile prose (sau marker 'nói thẳng /
    kết luận chắc / HỘI TỤ:'). Không có marker → trả nguyên (đoạn vốn đã plain)."""
    if not isinstance(text, str) or not text.strip():
        return text
    last = None
    for m in _TAKEAWAY_MARKER_RE.finditer(text):
        last = m
    if last is None:
        return text
    tail = text[last.end():].strip()
    return tail or text


def _nonempty(obj: Any) -> bool:
    """True nếu obj có nội dung đáng hiển thị (str non-rỗng / list non-rỗng /
    dict non-rỗng / số). None / '' / [] / {} → False."""
    if obj is None:
        return False
    if isinstance(obj, str):
        return obj.strip() != ""
    if isinstance(obj, (list, tuple, dict)):
        return len(obj) > 0
    return True


def _refs_from(*blocks: Any) -> list[str]:
    """Gom mọi _nguon (str / list) từ các block lại thành list refs duy nhất,
    giữ thứ tự. Dùng cho refs cấp-section (vd cung_phu_the, cap_do)."""
    out: list[str] = []

    def _add(src: Any) -> None:
        if isinstance(src, str) and src.strip():
            if src not in out:
                out.append(src)
        elif isinstance(src, (list, tuple)):
            for x in src:
                _add(x)

    for b in blocks:
        _add(b)
    return out


# --------------------------------------------------------------------------- #
# Section builders — mỗi hàm trả 1 section dict hoặc None (None = bỏ).
# --------------------------------------------------------------------------- #
def _sec_cap_do(cd: dict) -> Optional[dict]:
    """KILLER section: chẩn đoán CẤP ĐỘ thử thách (1-5). LÊN ĐẦU."""
    if not _nonempty(cd):
        return None
    cap = cd.get("cap_do")
    if cap is None:
        return None
    nguyen_tac = cd.get("nguyen_tac_vang") or {}
    tin_hieu = cd.get("tin_hieu_kich_hoat") or []
    lo_trinh = cd.get("lo_trinh") or []
    data = {
        "cap_do": cap,
        "max": 5,
        "ten_cap": cd.get("ten_cap"),
        "do_thay_doi_duoc": cd.get("do_thay_doi_duoc"),
        "phan_loai": cd.get("phan_loai"),
        "muc_do_thu_thach": cd.get("muc_do_thu_thach"),
        "tin_hieu": tin_hieu,
        "lo_trinh": lo_trinh,
        "nguyen_tac": nguyen_tac.get("tuyen_bo"),
    }
    # tom_tat: mức + lộ trình + nguyên tắc — THUẦN NGHĨA đời thường (không tên sao /
    # thập thần / lý-thuật / Hán). lo_trinh đã thuần sẵn trong cham_cap_do.json,
    # vẫn chạy _plain_vi cho chắc. nguyen_tac đẩy qua _plain_vi (đại vận→giai đoạn...).
    tom_tat = {
        "cap_do": cap,
        "max": 5,
        "ten_cap": _plain_vi(cd.get("ten_cap")),
        "do_thay_doi_duoc": cd.get("do_thay_doi_duoc"),
        "phan_loai": _plain_vi(cd.get("phan_loai")),
        "muc_do_thu_thach": cd.get("muc_do_thu_thach"),
        "lo_trinh": _plain_vi(lo_trinh),
        "nguyen_tac": _plain_vi(nguyen_tac.get("tuyen_bo")),
    }
    # can_cu: tín hiệu kích hoạt (tên sao / thập thần — Thương Quan, hóa Kỵ...).
    # Giữ NGUYÊN cho người tò mò trace cơ chế. AUTO-HIDE.
    can_cu = {"tin_hieu": tin_hieu}
    return {
        "id": "cap_do", "icon": "gauge", "title": "Mức độ thử thách",
        "kind": "cap_do", "data": data,
        "tom_tat": tom_tat, "can_cu": can_cu, "mac_dinh_an": False,
        "refs": _refs_from(cd.get("_nguon"), nguyen_tac.get("_nguon")),
    }


def _sec_hoi_dap(cau_hoi: list[dict]) -> Optional[dict]:
    """Câu hỏi của tuổi (Q&A) + cờ gieo quẻ Mai Hoa cho câu quyết định."""
    if not _nonempty(cau_hoi):
        return None
    items = []
    for q in cau_hoi:
        if not _nonempty(q.get("cau_hoi")):
            continue
        # BUG4 — 'dap' là câu trả lời USER-FACING: phải SẠCH Hán + jargon như mọi
        # surface đọc. Router chỉ _scrub (giữ branch 'Tỵ' để ground), nhưng body rút
        # từ tinh_chat_phoi_ngau còn lẫn '(刚烈之星)/(孤克)' → _plain_vi strip Hán +
        # tên-sao + dọn orphan. 'hoi' (câu user) cũng _plain_vi cho đồng nhất.
        items.append({
            "hoi": _plain_vi(q.get("cau_hoi")),
            "dap": _plain_vi(q.get("tra_loi")),
            "he": q.get("he_tra_loi"),
            "cta_gieo_que": bool(q.get("can_gieo_que")),
        })
    if not items:
        return None
    return {
        "id": "hoi_dap", "icon": "messages", "title": "Câu hỏi của tuổi",
        "kind": "qa", "items": items,
        # Q&A tiếng Việt — thuần nghĩa (đại vận→giai đoạn, năm Hồng Loan→năm có
        # khí vui/duyên...). Không can_cu.
        "tom_tat": _plain_vi(items), "can_cu": None, "mac_dinh_an": False,
    }


def _sec_cung_phu_the(cpt: dict, phoi_ngau: str) -> Optional[dict]:
    """Cung Phu Thê Tử Vi — prose_list (chính tinh / đào hoa / sát / tứ hoá)."""
    if not _nonempty(cpt):
        return None
    items = []
    tom_tat = []
    can_cu = []
    refs = []
    groups = (
        ("chinh_tinh_luan", "tinh_chat_phoi_ngau"),
        ("dao_hoa_luan", "y_nghia_duyen"),
        ("sat_tinh_luan", "y_nghia"),
        ("tu_hoa_luan", "y_nghia"),
    )
    for key, body_field in groups:
        for entry in cpt.get(key) or []:
            ten = entry.get("sao") or entry.get("hoa")
            noi_dung = entry.get(body_field) or entry.get("y_nghia")
            if not _nonempty(noi_dung):
                continue
            items.append({"ten": ten, "noi_dung": noi_dung})
            # tom_tat: THUẦN nghĩa về bạn đời — DÙNG nghia_thuan (câu đời thường,
            # KHÔNG tên sao / thập thần / jargon: 'Bạn đời chu đáo, biết điều...').
            # KHÔNG dùng noi_dung kỹ thuật nữa. Fallback _plain_vi(noi_dung) khi
            # entry chưa có nghia_thuan (đẩy hết jargon ra). KHÔNG ghi 'ten' (tên sao).
            nghia_thuan = entry.get("nghia_thuan")
            noi_dung_plain = (nghia_thuan if _nonempty(nghia_thuan)
                              else _plain_vi(noi_dung))
            if not _nonempty(noi_dung_plain):
                # Không có nghĩa thuần đọc được → bỏ khỏi tom_tat (chỉ để can_cu).
                pass
            else:
                tom_tat.append({"noi_dung": noi_dung_plain})
            # can_cu: 'TênSao (Hán)' + mô tả kỹ thuật GỐC + cát-hung + điều cần chú
            # ý (giữ NGUYÊN, có Hán). Dành người tò mò trace cơ chế. AUTO-HIDE.
            ten_han = entry.get("ten_han")
            ten_full = f"{ten} ({ten_han})" if _nonempty(ten_han) else ten
            can_cu.append({
                "ten": ten_full,
                "noi_dung": noi_dung,
                "cat_hung": entry.get("cat_hung"),
                "dieu_can_chu_y": entry.get("dieu_can_chu_y"),
            })
            refs.append(entry.get("_nguon"))
    if not items:
        return None
    return {
        "id": "cung_phu_the", "icon": "users",
        "title": f"Cung Phu Thê ({phoi_ngau})",
        "kind": "prose_list", "items": items,
        "tom_tat": tom_tat, "can_cu": can_cu, "mac_dinh_an": False,
        "refs": _refs_from(*refs),
    }


def _sec_song_phai(rec: list[dict]) -> Optional[dict]:
    """Tử Vi ⇄ Bát Tự — pairs (hội tụ / dị biệt theo chủ đề)."""
    if not _nonempty(rec):
        return None
    items = []
    tom_tat = []
    can_cu = []
    for cd in rec:
        chu_de = cd.get("chu_de")
        tu_vi = cd.get("tuvi_doc_bang")
        bat_tu = cd.get("batu_doc_bang")
        if not (_nonempty(tu_vi) or _nonempty(bat_tu)):
            continue
        hoi_tu = cd.get("khi_HOI_TU")
        di_biet = cd.get("khi_DI_BIET")
        trang_thai = "hội tụ" if _nonempty(hoi_tu) else (
            "dị biệt" if _nonempty(di_biet) else "hội tụ")
        items.append({
            "chu_de": chu_de, "tu_vi": tu_vi, "bat_tu": bat_tu,
            "trang_thai": trang_thai,
        })
        # tom_tat: chủ đề + 'hai phái hội tụ/dị biệt' + KẾT LUẬN thuần. Reconcile
        # prose dày cơ chế (Đế tinh / Sát-Kỵ / Quan...) — cơ chế giữ ở can_cu; tom_tat
        # CHỈ lấy câu KẾT LUẬN đời thường (đoạn sau marker 'nói thẳng được / kết luận
        # chắc / HỘI TỤ:'), rồi _plain_vi đẩy nốt jargon còn sót.
        y_nghia = hoi_tu if _nonempty(hoi_tu) else di_biet
        prefix = "hai phái hội tụ" if trang_thai == "hội tụ" else "hai phái dị biệt"
        takeaway = _takeaway_clause(y_nghia)
        y_nghia_plain = _plain_vi(takeaway)
        ket_luan = (f"{prefix} — {y_nghia_plain}"
                    if _nonempty(y_nghia_plain) else prefix)
        tom_tat.append({
            "chu_de": _plain_vi(chu_de),
            # trang_thai = 'hội tụ'/'dị biệt' (tiếng Việt thuần, KHÔNG jargon) —
            # giữ cho UI badge; ket_luan đã gồm prefix nên vẫn tự đủ.
            "trang_thai": trang_thai,
            "ket_luan": ket_luan,
        })
        # can_cu: cơ chế đọc-bảng từng phái (giữ NGUYÊN Hán/jargon). AUTO-HIDE.
        can_cu.append({
            "chu_de": chu_de,
            "tu_vi": tu_vi,
            "bat_tu": bat_tu,
        })
    if not items:
        return None
    return {
        "id": "song_phai", "icon": "arrows-shuffle",
        "title": "Tử Vi ⇄ Bát Tự", "kind": "pairs", "items": items,
        "tom_tat": tom_tat, "can_cu": can_cu, "mac_dinh_an": False,
    }


def _sec_dinh_thoi(dt: dict) -> Optional[dict]:
    """Định thời — timeline (năm kích hoạt / năm cần giữ gìn)."""
    if not _nonempty(dt):
        return None
    items = []
    # Lưu niên GẦN đứng ĐẦU timeline — user thấy năm cụ thể trước mắt (2026, 2028...)
    # thay vì chỉ cửa đại vận xa. note của marker đã kèm điều kiện "cần chính diệu cát".
    for ln in dt.get("luu_nien_gan") or []:
        items.append({
            "loai": "lưu niên gần",
            "mo_ta": ln.get("note") or (f"Năm {ln.get('year')}: "
                                        + ", ".join(ln.get("triggers") or [])),
            "year": ln.get("year"),
            "branch": ln.get("year_branch"),
            "da_qua": False,
        })
    for kh in dt.get("nam_kich_hoat") or []:
        items.append({
            "loai": "kích hoạt",
            "mo_ta": kh.get("dien_dat") or "đại vận có khí hỉ sự / duyên được kích hoạt",
            "start_age": kh.get("start_age"), "end_age": kh.get("end_age"),
            "branch": kh.get("branch"),
            "da_qua": bool(kh.get("da_qua")),
        })
    for gg in dt.get("nam_can_giu_gin") or []:
        items.append({
            "loai": "giữ gìn",
            "mo_ta": gg.get("dien_dat") or "năm cần giữ gìn / chăm sóc quan hệ",
            "start_age": gg.get("start_age"), "end_age": gg.get("end_age"),
            "branch": gg.get("branch"),
            "da_qua": bool(gg.get("da_qua")),
        })
    if not items:
        return None
    return {
        "id": "dinh_thoi", "icon": "clock", "title": "Định thời",
        "kind": "timeline", "items": items,
        # Năm + mô tả Việt — thuần nghĩa (đại vận→giai đoạn...). Không can_cu.
        "tom_tat": _plain_vi(items), "can_cu": None, "mac_dinh_an": False,
    }


# Map cat_hung engine → tone hiển thị.
_TONE_MAP = {
    "the_manh": "the_manh",
    "diem_can_chu_y": "can_chu_y",
    "trung_tinh": "trung_tinh",
}


def _fmt_nguon(n) -> Optional[str]:
    """Nguồn (dict/str/list) → chuỗi đọc được cho 'Căn cứ'. Bỏ path file nội bộ
    (file=...); dict {sach,trang} → 'Sách (tr.X)'. Tránh render JSON thô ra UI."""
    if not n:
        return None
    if isinstance(n, str):
        return n.strip() or None
    if isinstance(n, list):
        parts = [_fmt_nguon(x) for x in n]
        return "; ".join(p for p in parts if p) or None
    if isinstance(n, dict):
        sach = (n.get("sach") or n.get("nguon") or n.get("ten") or "").strip()
        trang = n.get("trang")
        if isinstance(trang, (list, tuple)):
            trang = ", ".join(str(t) for t in trang if t not in (None, ""))
        elif trang is not None:
            trang = str(trang)
        if sach and trang:
            return f"{sach} (tr.{trang})"
        return sach or (f"tr.{trang}" if trang else None)
    return str(n)


def _sec_cach_cuc(cc: list[dict]) -> Optional[dict]:
    """Cách cục — list (đã reframe đọc-đồng-dạng qua field bien_chinh)."""
    if not _nonempty(cc):
        return None
    items = []
    tom_tat = []
    can_cu = []
    for c in cc:
        noi_dung = c.get("bien_chinh") or c.get("van_hanh")
        if not _nonempty(noi_dung):
            continue
        tone = _TONE_MAP.get(c.get("cat_hung"), "trung_tinh")
        items.append({
            "ten": c.get("ten_cach"),
            "noi_dung": noi_dung,
            "tone": tone,
        })
        # tom_tat: THUẦN nghĩa từ bien_chinh — bỏ tên cách-Hán + tên sao + chi
        # (Tỵ/Hợi hãm) qua _plain_vi. KHÔNG ghi 'ten' (tên cách kỹ thuật).
        noi_dung_plain = _plain_vi(noi_dung)
        if _nonempty(noi_dung_plain):
            tom_tat.append({"noi_dung": noi_dung_plain, "tone": tone})
        # can_cu: tên cách + Hán-tự (sao khớp) + trích sách. Dành người tò mò.
        han_tu = _refs_from(c.get("sao_khop"))
        can_cu.append({
            "ten_cach": c.get("ten_cach"),
            "han_tu": han_tu,
            "_nguon": _fmt_nguon(c.get("_nguon")),
        })
    if not items:
        return None
    return {
        "id": "cach_cuc", "icon": "recycle", "title": "Cách cục",
        "kind": "list", "items": items,
        "tom_tat": tom_tat, "can_cu": can_cu, "mac_dinh_an": False,
    }


def _sec_luan_chi_tiet(qt: dict) -> Optional[dict]:
    """Luận chi tiết 12+10 bước — collapsible (kim tự tháp + xếp hạng + bước)."""
    if not _nonempty(qt):
        return None
    tuvi = qt.get("tu_vi_12_buoc") or {}
    batu = qt.get("bat_tu_10_buoc") or {}
    xh = qt.get("xep_hang_yeu_to") or {}

    def _buoc(block: dict) -> list[dict]:
        out = []
        for b in block.get("buoc") or []:
            luan = b.get("luan")
            if not _nonempty(luan):
                continue
            out.append({"ten_buoc": b.get("ten_buoc"), "luan": luan})
        return out

    buoc_tu_vi = _buoc(tuvi)
    buoc_bat_tu = _buoc(batu)
    if not (buoc_tu_vi or buoc_bat_tu):
        return None

    def _rank(items: Any) -> list[dict]:
        out = []
        for it in items or []:
            out.append({"ten_buoc": it.get("ten_buoc"),
                        "luan_tom": it.get("luan_tom")})
        return out

    data = {
        "kim_tu_thap": qt.get("tong_hop_kim_tu_thap"),
        "xep_hang": {
            "truc_tiep": _rank(xh.get("truc_tiep")),
            "gian_tiep": _rank(xh.get("gian_tiep")),
            "tiem_an": _rank(xh.get("tiem_an")),
        },
        "buoc_tu_vi": buoc_tu_vi,
        "buoc_bat_tu": buoc_bat_tu,
    }
    return {
        "id": "luan_chi_tiet", "icon": "stack-2",
        "title": "Luận chi tiết 12+10 bước", "kind": "collapsible", "data": data,
        # THUẦN công thức (12+10 bước, Hán/jargon dày) → cả section là can_cu,
        # gập mặc định. Không có tom_tat (không phải kết-quả cho user thường).
        "tom_tat": None, "can_cu": data, "mac_dinh_an": True,
    }


def _sec_loi_thay(action_base: str) -> dict:
    """Lời thầy — narration (sage narrate qua endpoint, fetch riêng)."""
    return {
        "id": "loi_thay", "icon": "quote", "title": "Lời thầy",
        "kind": "narration", "content": None,
        "fetch_action": f"{action_base}/narrate",
        "tom_tat": None, "can_cu": None, "mac_dinh_an": False,
    }


def _sec_phac_hoa(phoi_ngau: str, disclaimer: Optional[str], action_base: str) -> dict:
    """Phác hoạ chân dung BIỂU TƯỢNG người phối ngẫu — cta (paradigm)."""
    return {
        "id": "phac_hoa", "icon": "palette",
        "title": f"Phác họa người {phoi_ngau}", "kind": "cta",
        "action": f"{action_base}/phac-hoa",
        "note": disclaimer,
        "tom_tat": None, "can_cu": None, "mac_dinh_an": False,
    }


def _sec_gieo_que(action_base: str) -> dict:
    """Gieo quẻ Mai Hoa cho câu quyết định — cta_gieo_que."""
    return {
        "id": "gieo_que", "icon": "yin-yang", "title": "Gieo quẻ quyết định",
        "kind": "cta_gieo_que",
        "action": f"{action_base}/gieo-que",
        "tom_tat": None, "can_cu": None, "mac_dinh_an": False,
    }


def _sec_nguon(sources: list[str]) -> Optional[dict]:
    """Nguồn — refs (gom _nguon rải rác về 1 chỗ)."""
    if not _nonempty(sources):
        return None
    return {
        "id": "nguon", "icon": "book", "title": "Nguồn",
        "kind": "refs", "items": list(sources),
        # Trích sách (tên file/Hán/§) = THUẦN căn cứ → gập mặc định.
        "tom_tat": None, "can_cu": list(sources), "mac_dinh_an": True,
    }


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def build_display(reading_output: dict, gender: str = "nữ",
                  action_base: str = "/api/cross-paradigm/tinh-duyen") -> dict:
    """Map read_tinh_duyen output → {meta, sections} trình bày dùng chung.

    action_base: prefix cho CTA action (phac-hoa/gieo-que/narrate). Web giữ default
    `/api/cross-paradigm/tinh-duyen` (session auth); AppChat truyền `/api/sync/tinh-duyen`
    (service key + firebase_uid) để client gọi đúng namespace.

    Args:
        reading_output: dict trả từ read_tinh_duyen (hoặc service.run_tinh_duyen,
            có merge thêm charged_xu/cached — vẫn chứa đủ key engine).
        gender: 'nữ' (mặc định) / 'nam'. Nếu rỗng/không rõ, suy từ
            reading_output['input']['gender'].

    Returns:
        {meta: {...}, sections: [...]} — sections SẠCH, CÓ THỨ TỰ, ẨN internal,
        section rỗng đã bị bỏ. KHÔNG còn base_12_khia_canh / scrub_caution_count.
    """
    ro = reading_output or {}
    inp = ro.get("input") or {}

    # Giới (BUG2 defense): NGUỒN CHÂN LÝ là input.gender (engine đã chuẩn hoá +
    # đã _apply_gender_tree theo nó). Tham số `gender` chỉ là fallback khi input
    # thiếu — TRÁNH ca caller quên truyền gender (mặc định 'nữ') khiến lá NAM hiện
    # 'chồng'/'người chồng' dù body đã đảo sang 'vợ'. input.gender luôn 'nam'/'nữ'.
    g = inp.get("gender") if _nonempty(inp.get("gender")) else gender
    nu = _is_female(g)
    phoi_ngau = "chồng" if nu else "vợ"
    gender_token = "nữ" if nu else "nam"

    stage = ro.get("stage") or {}
    disclaimer = ro.get("_disclaimer")

    meta = {
        "title": f"Tình duyên — người {phoi_ngau}",
        "gender": gender_token,
        "phoi_ngau": phoi_ngau,
        "tuoi": inp.get("tuoi") if inp.get("tuoi") is not None else stage.get("tuoi"),
        "stage_id": stage.get("stage_id"),
        "moi_truong": stage.get("moi_truong"),
        "disclaimer": disclaimer,
        "method_id": ro.get("method_id"),
        "paradigm_ok": bool(ro.get("paradigm_ok", True)),
        # Báo client: mỗi section có tom_tat (KẾT QUẢ, hiện) + can_cu (CÔNG THỨC,
        # auto-hide) → render kết-quả-trước, căn-cứ-ẩn-bấm-mới-hiện.
        "co_can_cu": True,
    }

    # THỨ TỰ hiển thị (cap_do KILLER lên đầu; nguon cuối). None / rỗng đã bị bỏ.
    candidates = [
        _sec_cap_do(ro.get("chan_doan_cap_do") or {}),
        _sec_hoi_dap(ro.get("cau_hoi_tuoi") or []),
        _sec_cung_phu_the(ro.get("cung_phu_the_tuvi") or {}, phoi_ngau),
        _sec_song_phai(ro.get("song_phai_reconcile") or []),
        _sec_dinh_thoi(ro.get("dinh_thoi") or {}),
        _sec_cach_cuc(ro.get("cach_cuc") or []),
        _sec_luan_chi_tiet(ro.get("quy_trinh_day_du") or {}),
        _sec_loi_thay(action_base),
        _sec_phac_hoa(phoi_ngau, disclaimer, action_base),
        _sec_gieo_que(action_base),
        _sec_nguon(ro.get("sources") or []),
    ]
    sections = [s for s in candidates if s is not None]

    return {"meta": meta, "sections": sections}


__all__ = ["build_display", "_strip_han", "_strip_internal_ref", "_plain_vi"]
