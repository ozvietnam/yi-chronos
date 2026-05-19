"""LLM cleanup + concept detection.

For each page of raw OCR text, send to LLM with:
1. Glossary (canonical concepts from YI-Hermes + Lexicon) → for term normalization
2. Strict instruction: do NOT bịa, only restore obvious OCR errors
3. Output: cleaned markdown + section_hint + wikilinks_detected

Output format (strict JSON):
{
  "cleaned_markdown": "...",                       # final text, with [[Càn]]-style wikilinks
  "section_hint": {"level": 1, "title": "Chương 1"} | null,
  "wikilinks": ["Càn", "Khôn", ...],              # concepts detected
  "confidence": 0.0-1.0,
  "warnings": ["text mờ trang dưới", ...]
}
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


_CLEANUP_SYSTEM_PROMPT = """Bạn là chuyên gia phục chế văn bản dịch học cổ. Bạn nhận RAW OCR output từ scan tiếng Việt (có thể xen kẽ Hán) — có lỗi nhận dạng điển hình (thiếu dấu, ghép chữ, mất khoảng trắng, đảo dòng).

## Mục tiêu

Phục chế bản text gần đúng bản gốc nhất, để anh đọc nội bộ — không phân phối, không thay thế sách in.

## Quy tắc TUYỆT ĐỐI

1. **CHỈ sửa lỗi OCR rõ ràng** (có context xác định). Nếu nghi ngờ → giữ nguyên + đánh dấu `[?]`.
2. **KHÔNG bịa câu, KHÔNG diễn giải lại, KHÔNG tóm tắt**. Bạn phục chế chứ không viết lại.
3. **Giữ Hán cổ nguyên xi** nếu có (sách dịch học thường có chú giải Hán).
4. **Markdown format**:
   - Tiêu đề chương/tiết dùng `#`, `##`, `###`
   - Câu thơ/sấm dùng `>`
   - Bảng đơn giản dùng `| col | col |`
5. **CỰC KỲ QUAN TRỌNG — Hình vẽ**: Nếu raw OCR có placeholder dạng
   `[[FIGURE:<loại>|<mô_tả>]]`, BẮT BUỘC giữ NGUYÊN XI placeholder đó tại đúng vị trí.
   KHÔNG được xoá, KHÔNG sửa, KHÔNG thay bằng `![](...)` hay text khác.
   Đây là marker để sau anh review và vẽ lại hình thật.
6. **Lọc watermark**: Nếu thấy URL `thuviansach.vn`, `dichhoc.com`, hoặc các watermark
   trang web → XOÁ. Không giữ lại trong văn bản.
7. **WikiLinks**: bọc khái niệm dịch học chính bằng `[[Tên]]` — VD: `[[Càn]]`, `[[Ngũ Hành]]`, `[[Khôn]]`. CHỈ những khái niệm có trong glossary dưới đây — KHÔNG tự thêm.

## Extract metadata (cho indexing + search, KHÔNG phải wikilink)

8. **summary_short**: tóm tắt nội dung trang trong 1-2 câu (≤ 50 từ), giúp anh skim 938 trang nhanh. Phải khách quan — KHÔNG bịa, chỉ nói trang này nói gì.

9. **hashtags**: tag ngắn dùng để search/filter. Định dạng `#slug-không-dấu`, max 10 tags/trang.
   - Loại tag: concept (#âm-dương, #ngũ-hành, #bát-quái), object (#hà-đồ, #lạc-thư), quẻ (#quẻ-càn, #quẻ-khôn-vi-địa), person (#chu-hy, #trình-di, #phục-hy), giáo (#hệ-từ, #thuyết-quái)
   - DỄ DÀNG: nếu nội dung mơ hồ, thà ÍT tag (3-4) còn hơn TAGS sai.

10. **persons**: danh sách người được nhắc trong trang (tiên hiền, học giả, nhân vật lịch sử). VD: `["Chu Hy", "Trình Di", "Phục Hy"]`. Để rỗng nếu không có.

11. **que_mentions**: tên quẻ Hexagram được nhắc cụ thể (KHÔNG phải tên trigram đơn). VD: `["Đại Quá", "Tỉnh", "Càn"]`. Để rỗng nếu không có.

## Glossary (chỉ dùng cho [[wikilink]])

{glossary}

## Output JSON

```json
{{
  "cleaned_markdown": "## Tiết 2 — Ngũ Hành\\n\\n[[Ngũ Hành]] gồm [[Kim]], [[Mộc]], [[Thuỷ]], [[Hoả]], [[Thổ]]...\\n",
  "section_hint": {{"level": 2, "title": "Tiết 2 — Ngũ Hành"}},
  "wikilinks": ["Ngũ Hành", "Kim", "Mộc", "Thuỷ", "Hoả", "Thổ"],
  "summary_short": "Giới thiệu 5 hành Kim Mộc Thuỷ Hoả Thổ theo quan điểm Trình-Chu.",
  "hashtags": ["#ngũ-hành", "#kim", "#mộc", "#thuỷ", "#hoả", "#thổ", "#trình-chu"],
  "persons": ["Trình Di", "Chu Hy"],
  "que_mentions": [],
  "confidence": 0.85,
  "warnings": []
}}
```

`section_hint` = null nếu trang này KHÔNG bắt đầu chương/tiết mới (là phần tiếp).
Trả về CHỈ JSON, không markdown wrapper."""


@dataclass
class DetectedFigure:
    """A figure marker `[[FIGURE:type|desc]]` parsed from cleaned markdown."""
    figure_type: str         # 'ha_do' | 'lac_thu' | 'bat_quai_tien_thien' | ...
    description: str         # detailed description for redraw
    placeholder: str         # exact original `[[FIGURE:...]]` string


@dataclass
class CleanupResult:
    cleaned_markdown: str = ""
    section_hint: dict | None = None
    wikilinks: list[str] = field(default_factory=list)
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_llm_response: str = ""
    detected_figures: list[DetectedFigure] = field(default_factory=list)
    # Extended metadata (v2, 2026-05-12 — anh đề xuất)
    summary_short: str = ""                       # 1-2 câu TLDR
    hashtags: list[str] = field(default_factory=list)        # ["#âm-dương", ...]
    persons: list[str] = field(default_factory=list)         # ["Chu Hy", ...]
    que_mentions: list[str] = field(default_factory=list)    # ["Đại Quá", ...]


# Regex to detect [[FIGURE:type|description]] in OCR output / cleaned markdown
_FIGURE_RE = re.compile(r"\[\[FIGURE:([a-z_]+)\|([^\]]+)\]\]")


def _normalize_hashtag(raw: str) -> str:
    """Normalize hashtag: ensure leading #, lowercase, replace whitespace with -.

    Giữ tiếng Việt có dấu (UI hiển thị đẹp). Slug-style nhưng UTF-8.
    """
    s = raw.strip()
    if not s.startswith("#"):
        s = "#" + s
    # Lowercase + replace whitespace runs with single hyphen
    body = s[1:].lower()
    body = re.sub(r"\s+", "-", body)
    body = re.sub(r"[^\w\-àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", "", body, flags=re.UNICODE)
    return "#" + body if body else ""


def parse_figures(text: str) -> list[DetectedFigure]:
    """Extract all [[FIGURE:type|desc]] markers from text."""
    figures: list[DetectedFigure] = []
    for m in _FIGURE_RE.finditer(text):
        figures.append(DetectedFigure(
            figure_type=m.group(1).strip(),
            description=m.group(2).strip(),
            placeholder=m.group(0),
        ))
    return figures


def _build_glossary_snippet(glossary_terms: list[str], max_terms: int = 60) -> str:
    """Format glossary as comma-separated list (truncated for token budget)."""
    if not glossary_terms:
        return "(empty — chỉ nhận diện những concept hiển nhiên trong dịch học cơ bản)"
    terms = list(dict.fromkeys(glossary_terms))[:max_terms]
    return ", ".join(terms)


def cleanup_page(
    raw_ocr_text: str,
    *,
    glossary_terms: list[str],
    llm_provider,
    model: str = "deepseek-v4-flash",
    book_hint: str = "",
    page_number: int | None = None,
) -> CleanupResult:
    """Send raw OCR to LLM. Returns CleanupResult."""
    result = CleanupResult()
    if not raw_ocr_text.strip():
        result.warnings.append("empty OCR text")
        return result

    glossary = _build_glossary_snippet(glossary_terms)
    sys_msg = _CLEANUP_SYSTEM_PROMPT.format(glossary=glossary)
    page_tag = f"[trang {page_number}]" if page_number else ""
    user_msg = (
        f"## Sách: {book_hint or '(unknown)'} {page_tag}\n\n"
        f"## RAW OCR\n\n{raw_ocr_text[:6000]}"
    )

    try:
        resp = llm_provider.chat(
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            model=model,
            max_tokens=4000,
            temperature=0.2,
        )
        content = resp.content if hasattr(resp, "content") else str(resp)
        result.raw_llm_response = content
    except Exception as e:
        result.errors.append(f"LLM call failed: {e}")
        return result

    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        result.errors.append("no JSON in LLM response")
        result.cleaned_markdown = raw_ocr_text  # fallback: keep raw
        return result
    raw_json = m.group(0)
    # Strip all C0 control chars except tab(\x09) and newline(\x0a) — includes CR(\x0d)
    raw_json = re.sub(r"[\x00-\x08\x0b-\x1f]", "", raw_json)
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        # Try json-repair if available (handles missing commas, trailing commas, etc.)
        try:
            import json_repair  # type: ignore
            data = json_repair.loads(raw_json)
        except ImportError:
            # json_repair not installed — last resort: strip literal newlines inside strings
            raw_json2 = re.sub(r'(?<=")([^"\\]*(?:\\.[^"\\]*)*)(?=")',
                               lambda m2: m2.group(0).replace('\n', '\\n').replace('\t', '\\t'),
                               raw_json, flags=re.DOTALL)
            try:
                data = json.loads(raw_json2)
            except json.JSONDecodeError:
                result.errors.append(f"JSON parse error: {e}")
                result.cleaned_markdown = raw_ocr_text
                return result
        except Exception:
            result.errors.append(f"JSON parse error: {e}")
            result.cleaned_markdown = raw_ocr_text
            return result

    result.cleaned_markdown = data.get("cleaned_markdown", "") or raw_ocr_text
    sh = data.get("section_hint")
    if isinstance(sh, dict) and sh.get("title"):
        result.section_hint = {
            "level": int(sh.get("level", 1)),
            "title": sh.get("title"),
        }
    wls = data.get("wikilinks") or []
    result.wikilinks = [w for w in wls if isinstance(w, str) and w.strip()]
    try:
        result.confidence = float(data.get("confidence", 0.5))
    except Exception:
        result.confidence = 0.5
    result.warnings = [w for w in (data.get("warnings") or []) if isinstance(w, str)]
    # ─── Extended metadata (v2) ─────────────────────────────────────────
    result.summary_short = str(data.get("summary_short", "") or "")[:300]
    hashtags = data.get("hashtags") or []
    result.hashtags = [
        _normalize_hashtag(h) for h in hashtags
        if isinstance(h, str) and h.strip()
    ] if isinstance(hashtags, list) else []
    persons = data.get("persons") or []
    result.persons = [
        p.strip() for p in persons if isinstance(p, str) and p.strip()
    ] if isinstance(persons, list) else []
    que_mentions = data.get("que_mentions") or []
    result.que_mentions = [
        q.strip() for q in que_mentions if isinstance(q, str) and q.strip()
    ] if isinstance(que_mentions, list) else []
    # Extract figures from BOTH raw OCR (in case LLM lost them) and cleaned output
    figs_from_raw = parse_figures(raw_ocr_text)
    figs_from_clean = parse_figures(result.cleaned_markdown)
    # Dedupe by placeholder
    seen: set[str] = set()
    all_figs: list[DetectedFigure] = []
    for f in figs_from_clean + figs_from_raw:
        if f.placeholder not in seen:
            all_figs.append(f); seen.add(f.placeholder)
    result.detected_figures = all_figs
    # If LLM stripped placeholders but raw had them, re-insert at end as fallback
    if figs_from_raw and not figs_from_clean:
        for f in figs_from_raw:
            result.cleaned_markdown += f"\n\n{f.placeholder}"
        result.warnings.append("LLM strip [[FIGURE]] — re-inserted from raw OCR")
    return result


def fetch_glossary_terms_for_book(book_schools: list[str] | None = None) -> list[str]:
    """Pull canonical concept names from Lexicon + Hermes glossary, filtered by school."""
    terms: list[str] = []
    # 1. From lexicon concepts (canonical_vi)
    try:
        from engine.yi_lexicon.store import _conn, bootstrap_db
        bootstrap_db()
        with _conn() as c:
            rows = c.execute(
                "SELECT canonical_vi FROM concepts ORDER BY canonical_vi LIMIT 300"
            ).fetchall()
        terms.extend([r[0] for r in rows if r[0]])
    except Exception:
        pass
    # 2. From Hermes glossary if present
    try:
        from engine.yi_hermes.glossary_store import list_glossary_terms
        gloss = list_glossary_terms(schools=book_schools)
        terms.extend([g.canonical_vi for g in gloss if getattr(g, "canonical_vi", None)])
    except Exception:
        pass
    # Dedupe + drop empties
    seen = set()
    out: list[str] = []
    for t in terms:
        t2 = (t or "").strip()
        if t2 and t2 not in seen:
            seen.add(t2)
            out.append(t2)
    return out
