"""Luận sâu Mai Hoa — gọi LLM với citation Kinh Dịch nguyên văn (RAG).

Khác `interpret.py` (thuần tính toán Thể-Dụng + Quái Khí + Tam Yếu):
- Endpoint này build prompt cho LLM với context = citation Kinh Dịch tương ứng
- LLM sinh phê quẻ sâu theo paradigm "đồng dạng + Tam Tài + quan-vật-trace-tính"
- KHÔNG predict cát hung tĩnh (Iron Rule #4 Mai Hoa)

Routing strategy:
1. Cast result → 2 bát quái (upper + lower) → load citation gốc nếu có
   (Càn → 01-kien.md, Khôn → 02-khon.md...)
2. Intent (gia trạch/cầu danh/...) → load tâm-phap file phù hợp
3. Hào động (1-6) → có thể có insight riêng (vd: hào 1 ⇒ Tiềm long/Lý sương)
4. Compose prompt với citations capped (max ~12k chars) để không vọng context

Source citation files: data/hermes_yi/skills/kinh-dich/{quẻ,tam-phap}/*.md
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_skills_root() -> Path:
    """Resolve kinh-dich skills folder. Prefer mounted data/, fallback embedded_data/.

    Local dev: data/hermes_yi/skills/kinh-dich/ (git-tracked, mounted)
    Production VPS: volume mount /opt/yi-chronos/data shadows data/ in image,
    nhưng /opt/yi-chronos/data có thể không có skills/. Fallback embedded_data/
    (đã COPY vào Docker image — version-controlled knowledge).
    """
    primary = _PROJECT_ROOT / "data" / "hermes_yi" / "skills" / "kinh-dich"
    if (primary / "INDEX.md").exists():
        return primary
    embedded = _PROJECT_ROOT / "embedded_data" / "hermes_yi" / "skills" / "kinh-dich"
    if (embedded / "INDEX.md").exists():
        return embedded
    # Last resort: still return primary so caller sees consistent path in
    # error messages (load returns empty body).
    return primary


_SKILLS_ROOT = _resolve_skills_root()

# 8 bát quái → quẻ thuần (cùng tên trên-dưới) → file citation
# Hiện chỉ có Càn + Khôn. Sau khi đọc tiếp sẽ có thêm.
_BAT_QUAI_TO_FILE: dict[str, str] = {
    "Càn": "quẻ/01-kien.md",
    "Khôn": "quẻ/02-khon.md",
    # Đoài, Ly, Chấn, Tốn, Khảm, Cấn → chưa có quẻ thuần citation
}

# 64 hexagram (upper, lower) → file citation (chỉ những quẻ đã thấm)
_HEXAGRAM_TO_FILE: dict[tuple[str, str], str] = {
    ("Càn", "Càn"): "quẻ/01-kien.md",        # 1 Kiền
    ("Khôn", "Khôn"): "quẻ/02-khon.md",      # 2 Khôn
    ("Khảm", "Chấn"): "quẻ/03-truan.md",     # 3 Truân
    ("Cấn", "Khảm"): "quẻ/04-mong.md",       # 4 Mông
    ("Khảm", "Càn"): "quẻ/05-nhu.md",        # 5 Nhu
    ("Càn", "Khảm"): "quẻ/06-tung.md",       # 6 Tụng
    ("Khôn", "Khảm"): "quẻ/07-su.md",        # 7 Sư
    ("Khảm", "Khôn"): "quẻ/08-ty.md",        # 8 Tỵ
    ("Tốn", "Càn"): "quẻ/09-tieu-suc.md",    # 9 Tiểu Súc
    ("Càn", "Đoài"): "quẻ/10-ly.md",         # 10 Lý
    ("Khôn", "Càn"): "quẻ/11-thai.md",       # 11 Thái (đảo!)
    ("Càn", "Khôn"): "quẻ/12-bi.md",         # 12 Bĩ
    ("Càn", "Ly"): "quẻ/13-dong-nhan.md",    # 13 Đồng Nhân
    ("Ly", "Càn"): "quẻ/14-dai-huu.md",      # 14 Đại Hữu
    ("Khôn", "Cấn"): "quẻ/15-khiem.md",      # 15 Khiêm
    ("Chấn", "Khôn"): "quẻ/16-du.md",        # 16 Dự
    ("Đoài", "Chấn"): "quẻ/17-tuy.md",       # 17 Tùy
    ("Cấn", "Tốn"): "quẻ/18-co.md",          # 18 Cổ
    ("Khôn", "Đoài"): "quẻ/19-lam.md",       # 19 Lâm
    ("Tốn", "Khôn"): "quẻ/20-quan.md",       # 20 Quán
}

# Intent → tâm-phap file
_INTENT_TO_TAM_PHAP: dict[str, str] = {
    "khoi_dau": "tam-phap/khoi-dau.md",
    "cau_danh": "tam-phap/khoi-dau.md",       # cầu danh = khởi đầu
    "khiem_ton": "tam-phap/khiem-ton.md",
    "hop_tac": "tam-phap/khiem-ton.md",
    "thay_doi": "tam-phap/giao-thoa.md",
    "gia_trach": "tam-phap/giao-thoa.md",     # nhà cửa cần giao thoa
    "tat_benh": "tam-phap/dau-hieu-som.md",
    "general": "tam-phap/giao-thoa.md",       # default = giao thoa
}


def _strip_yaml_frontmatter(text: str) -> str:
    """Skip YAML frontmatter (--- ... ---) ở đầu file để chỉ giữ body."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    return text[end + 4:].lstrip()


def _load_citation_file(relpath: str) -> str:
    """Load 1 citation file từ skills/kinh-dich/. Return body (skip frontmatter).
    Trả về empty string nếu file không tồn tại — caller chịu trách nhiệm degrade."""
    f = _SKILLS_ROOT / relpath
    if not f.exists():
        return ""
    try:
        text = f.read_text(encoding="utf-8")
        return _strip_yaml_frontmatter(text)
    except Exception:
        return ""


def select_citations(
    *,
    chinh_upper: str,
    chinh_lower: str,
    bien_upper: str,
    bien_lower: str,
    ho_upper: str,
    ho_lower: str,
    intent: Optional[str] = None,
    max_chars: int = 12000,
) -> dict:
    """Chọn citation files cho 1 lần luận sâu.

    Logic ưu tiên:
    1. Hexagram exact match cho chính/biến/hỗ (nếu có file)
    2. Bát quái match (quẻ thuần) cho upper/lower nếu hexagram chưa có
    3. Tâm-pháp file theo intent
    4. Index.md luôn load (master router context)

    Returns:
        {
            "citations": [{"path": ..., "body": ..., "reason": ...}, ...],
            "total_chars": int,
            "dropped": ["path due to limit"],
        }
    """
    seen_paths: set[str] = set()
    citations: list[dict] = []
    total = 0

    def _try_add(path: str, reason: str) -> None:
        nonlocal total
        if not path or path in seen_paths:
            return
        body = _load_citation_file(path)
        if not body:
            return
        if total + len(body) > max_chars:
            return
        seen_paths.add(path)
        citations.append({"path": path, "body": body, "reason": reason})
        total += len(body)

    # 1. Index master (~500 chars, always)
    _try_add("INDEX.md", "master router")

    # 2. Hexagram exact match
    for label, upper, lower in [
        ("chính", chinh_upper, chinh_lower),
        ("biến", bien_upper, bien_lower),
        ("hỗ", ho_upper, ho_lower),
    ]:
        path = _HEXAGRAM_TO_FILE.get((upper, lower))
        if path:
            _try_add(path, f"quẻ {label} {upper}/{lower}")

    # 3. Bát quái thuần (fallback) cho 2 trigrams của chính quẻ
    # Vd: Quẻ Đại Hữu (Ly/Càn) chưa có file → load Càn (01-kien) làm gốc Dương
    for trig in (chinh_upper, chinh_lower, bien_upper, bien_lower):
        path = _BAT_QUAI_TO_FILE.get(trig)
        if path:
            _try_add(path, f"bát quái {trig}")

    # 4. Tâm-pháp theo intent
    if intent:
        path = _INTENT_TO_TAM_PHAP.get(intent)
        if path:
            _try_add(path, f"tâm-pháp intent={intent}")
    # Fallback intent
    _try_add("tam-phap/giao-thoa.md", "tâm-pháp default (Thái-Bĩ paradigm)")

    return {
        "citations": citations,
        "total_chars": total,
        "files_used": [c["path"] for c in citations],
    }


def build_luan_sau_prompt(
    *,
    cast: dict,
    analyze: dict,
    citations_pack: dict,
    user_question: Optional[str] = None,
) -> str:
    """Build prompt cho LLM luận sâu Mai Hoa.

    Paradigm: Iron Rule #4 (Mai Hoa = ĐỌC ĐỒNG DẠNG, KHÔNG predict).
    """
    citation_text = "\n\n".join(
        f"### [{c['reason']}] — {c['path']}\n{c['body']}"
        for c in citations_pack["citations"]
    )

    cast_block = f"""**Kết quả gieo quẻ Mai Hoa**:
- Quẻ chính: {cast['chinh_quai']['name']} (Quẻ {cast['chinh_quai'].get('name_vi', '?')})
- Quẻ biến: {cast['bien_quai']['name']} (Quẻ {cast['bien_quai'].get('name_vi', '?')})
- Quẻ hỗ: {cast['ho_quai']['name']} (Quẻ {cast['ho_quai'].get('name_vi', '?')})
- Hào động: {cast['moving_line']} (1=hào đầu, 6=hào trên)
- Cảnh báo hỗ: {cast.get('ho_warning', 'không')}
"""

    analyze_block = f"""**Phân tích kỹ thuật** (đã computed):
- Thể-Dụng: {analyze['the_dung']['the_que']} (Thể) / {analyze['the_dung']['dung_que']} (Dụng)
- Quan hệ: {analyze['the_dung']['relationship']} → auspice: {analyze['the_dung']['auspice']}
- Mùa: {analyze['quai_khi']['season']}, Vượng: {analyze['quai_khi']['vuong']}, Suy: {analyze['quai_khi']['suy']}
- Trạng thái Thể: {analyze['quai_khi']['the_status']}
- Overall: {analyze['overall']}
- Intent: {analyze['intent']['label']} ({analyze['intent']['key']})
"""

    return f"""Bạn là **bậc trí giả Mai Hoa Dịch Số** (梅花易數), kế thừa Thiệu Khang Tiết.

## ⚠️ Paradigm BẮT BUỘC (Iron Rule #4 — KHÔNG vượt qua)

Mai Hoa = **MÔN HỌC ĐỒNG DẠNG**:
- Cấu trúc vũ trụ = cấu trúc người = cấu trúc khoảnh khắc
- Người và vũ trụ NGANG NHAU (Tam Tài)
- **Quan-vật-trace-tính** (xem vật để hiểu Tính ẩn) — KHÔNG predict cát/hung tĩnh

❌ TUYỆT ĐỐI TRÁNH (paradigm sai):
- "Quẻ này dự đoán cát/hung"
- "Anh sẽ thành công/thất bại"
- "Tương lai sẽ X"

✅ PHẢI dùng (paradigm tổ sư):
- "Khoảnh khắc anh hỏi phản chiếu cái gì lớn hơn trong vũ trụ?"
- "Tâm anh đang ở vị trí nào trong tổng thể?"
- "Vũ trụ đang nói qua khoảnh khắc này: ..."

## 📚 Citation Kinh Dịch nguyên văn (RAG context)

{citation_text}

---

## 🎯 Yêu cầu luận sâu

{cast_block}

{analyze_block}

{f'**Câu hỏi của user**: {user_question}' if user_question else ''}

Hãy viết **phê quẻ sâu** (~600-1200 chữ) theo cấu trúc:

1. **Quan vật khoảnh khắc** (~150 chữ) — khoảnh khắc gieo quẻ + tổ hợp 3 quẻ (chính/biến/hỗ) phản chiếu cái gì? Trích dẫn cụ thể từ Kinh Dịch nguyên văn ở trên.

2. **Thể-Dụng + Quái Khí** (~200 chữ) — diễn giải quan hệ Thể-Dụng theo paradigm đồng dạng, KHÔNG predict. Dẫn chứng từ citation.

3. **Hào động + biến chuyển** (~200 chữ) — hào động chỉ ra cảnh giới gì? Dẫn cụ thể "hào X quẻ Y" + insight từ Trình Di/Chu Hy nếu có trong citation.

4. **Tâm-pháp cho người hỏi** (~150 chữ) — KHÔNG kê hành động cụ thể. Chỉ ra **cảnh giới + phận tương ứng** + 1 câu thầy tổ.

5. **Cảnh báo** (~50 chữ) — nếu có ho_warning từ engine.

LƯU Ý CRITICAL:
- Trích dẫn rõ "Kinh Dịch · quẻ X · hào Y · Trình Di Truyện" nếu lấy từ citation
- KHÔNG bịa quẻ / hào không có trong citation
- KHÔNG dùng tone fortune-telling
- Viết tiếng Việt, **xưng "Anh"** với người hỏi, em là "em" / "bậc trí giả"
"""


def call_llm_luan_sau(prompt: str) -> dict:
    """Gọi LLM (chain DeepSeek → MiniMax → Ollama → Mock fallback).

    Returns:
        {"narrative": str, "provider": str, "model": str, "tokens_used": int}
    """
    from engine.ai.registry import get_registry

    registry = get_registry()
    last_error: Optional[Exception] = None
    # Provider chain: deepseek (paid quality) → minimax (fast cloud) → ollama (free local) → mock
    for provider_id in ("deepseek", "minimax", "ollama"):
        try:
            provider = registry.get(provider_id)
        except KeyError:
            continue
        # `is_configured` là @property, không phải method
        if not provider.is_configured:
            continue
        try:
            # DeepSeek V4 Pro mặc định reasoning ON → content có thể empty
            # khi model "think but doesn't write". Pass reasoning_effort=none
            # cho writing task — vẫn dùng v4-pro nhưng skip chain-of-thought.
            kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.65,
                "max_tokens": 2000,
            }
            if provider_id == "deepseek":
                kwargs["reasoning_effort"] = "none"
            response = provider.chat(**kwargs)
            # response là LLMResponse dataclass (content, provider, model,
            # prompt_tokens, completion_tokens, total_tokens, raw)
            return {
                "narrative": (response.content or "").strip(),
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.total_tokens,
            }
        except Exception as exc:
            last_error = exc
            registry.mark_unhealthy(provider_id, str(exc))
            continue
    raise RuntimeError(
        f"Tất cả provider thất bại. Last error: {last_error or 'no provider configured'}"
    )
