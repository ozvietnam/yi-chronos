"""extract_to_wiki — LLM-driven extraction từ pages_vi/ → wiki schema (passages/methods/concepts/cases).

INPUT:  Chapter chunk (text Việt từ pages_vi/, kèm context page numbers + topic).
OUTPUT: Structured dict cho 4 wiki tables:
        - passage:        {topic, summary_50w, raw_text_quote, concepts_mentioned}
        - methods[]:      {name_vi, name_zh, domain, procedure_steps[]}
        - concepts[]:     {canonical_vi, canonical_zh, aliases[], short_note}
        - case_studies[]: {historical_event, inputs_recorded, output_predicted, output_actual, source_quote}

Sử dụng DeepSeek-chat (đã chứng minh quality ⭐⭐⭐⭐⭐ với Mai Hoa thuật ngữ).

USAGE:
    from engine.yi_translation.extract_to_wiki import extract_chapter
    result = extract_chapter(
        chapter_title="Bát Quái trong vạn vật",
        pages={4: "...", 5: "...", ...},
        corpus_id="thieu-khang-tiet-tq",
    )
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path


def _load_deepseek_key() -> str | None:
    if os.environ.get("DEEPSEEK_API_KEY"):
        return os.environ["DEEPSEEK_API_KEY"]
    env_file = Path("/Users/ozvietnamdesktop/Desktop/yi/.env.local")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    os.environ["DEEPSEEK_API_KEY"] = v
                    return v
    return None


EXTRACTION_PROMPT = """Bạn là chuyên gia Mai Hoa Dịch Số phụ trách extract knowledge từ sách giải nghĩa vào wiki có schema chặt chẽ.

INPUT: 1 chương sách "Đồ Giải Mai Hoa Dịch Số" (bản dịch Việt từ tiếng Trung hiện đại).

NHIỆM VỤ: Phân tích chương → trả về JSON với 4 nhóm thông tin:

1. **passage** (1 record duy nhất tóm tắt chương):
   - `topic`: tiêu đề ngắn gọn (8-12 từ Việt) miêu tả chủ đề chương
   - `summary_50w`: tóm tắt 40-60 từ Việt — nói rõ chương dạy gì, cách dùng, ý nghĩa
   - `raw_text_quote`: 1-2 câu cốt lõi nhất từ chương (≤ 200 ký tự) — quote nguyên văn
   - `concepts_mentioned`: list Việt các thuật ngữ chính được nhắc (≤ 10 items)

2. **methods** (0-3 records — chỉ nếu chương có dạy KỸ THUẬT có quy trình bước 1-2-3):
   - `name_vi`: tên kỹ thuật bằng tiếng Việt (e.g., "Phép khởi quẻ theo số")
   - `name_zh`: tên gốc tiếng Hán (e.g., "数起卦法")
   - `domain`: 1 trong ["bốc", "đọc", "ứng_kỳ", "biến_hoá", "khác"]
   - `procedure_steps`: list 3-7 bước cụ thể, mỗi bước 1 câu

3. **concepts** (1-15 records — thuật ngữ kỹ thuật quan trọng):
   - `canonical_vi`: tên chuẩn tiếng Việt (Hán-Việt nếu là thuật ngữ, e.g., "Tiên Thiên Bát Quái")
   - `canonical_zh`: tên gốc Hán (e.g., "先天八卦")
   - `aliases`: list các tên gọi khác (≤ 3)
   - `short_note`: 1-2 câu định nghĩa (≤ 150 ký tự)

4. **case_studies** (0-3 records — chỉ nếu chương có VÍ DỤ chiêm cụ thể):
   - `historical_event`: bối cảnh ví dụ (e.g., "Mai Hoa Dịch Số đoán hoa rụng ngày Quý Mão")
   - `inputs_recorded`: input của ví dụ (thời gian, sự kiện trigger)
   - `output_predicted`: dự đoán của Mai Hoa
   - `output_actual`: kết quả thật (nếu sách có ghi)
   - `source_quote`: trích nguyên văn ví dụ (≤ 200 ký tự)

⚠️ QUY TẮC:
- CHỈ extract những gì THẬT SỰ có trong text. Đừng bịa hoặc suy diễn.
- Thuật ngữ Hán-Việt trong concepts viết hoa chuẩn (Bát Quái, Ngũ Hành, Thiên Can).
- Nếu chương không có method/case_study → trả `methods: []`, `case_studies: []`.
- JSON OUTPUT phải parse được (no markdown wrapper, no ```json fence).

CHƯƠNG SÁCH:
{chapter_text}

TRẢ VỀ JSON:
"""


@dataclass
class ExtractionResult:
    passage: dict | None = None
    methods: list[dict] = field(default_factory=list)
    concepts: list[dict] = field(default_factory=list)
    case_studies: list[dict] = field(default_factory=list)
    raw_response: str = ""
    error: str = ""

    def stats(self) -> str:
        return (
            f"passage={1 if self.passage else 0} "
            f"methods={len(self.methods)} "
            f"concepts={len(self.concepts)} "
            f"cases={len(self.case_studies)}"
        )


def _call_deepseek(prompt: str, *, timeout: int = 120) -> str:
    key = _load_deepseek_key()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY không có")
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # low for structured output
        "max_tokens": 4000,
        "response_format": {"type": "json_object"},  # force JSON
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"]


def _parse_extraction(text: str) -> ExtractionResult:
    """Parse LLM JSON response, defensively."""
    result = ExtractionResult(raw_response=text)
    # Strip code fence nếu có
    text = text.strip()
    if text.startswith("```"):
        # remove ```json ... ```
        lines = text.split("\n")
        if len(lines) >= 2:
            text = "\n".join(lines[1:-1]).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        result.error = f"JSON parse fail: {e}"
        return result
    result.passage = data.get("passage")
    result.methods = data.get("methods", []) or []
    result.concepts = data.get("concepts", []) or []
    result.case_studies = data.get("case_studies", []) or []
    return result


def extract_chapter(
    chapter_text: str,
    *,
    max_chars: int = 12000,
    verbose: bool = False,
) -> ExtractionResult:
    """Extract structured wiki entries from 1 chapter.

    Nếu chapter quá dài (> max_chars) → cắt và chỉ extract từ đầu chương
    (tóm tắt thường ở đầu). Long-tail merge có thể làm sau.
    """
    if len(chapter_text) > max_chars:
        chapter_text = chapter_text[:max_chars] + "\n\n[... chương còn dài hơn, đã cắt để fit context ...]"

    prompt = EXTRACTION_PROMPT.format(chapter_text=chapter_text)
    t0 = time.time()
    try:
        raw = _call_deepseek(prompt)
        result = _parse_extraction(raw)
        dt = time.time() - t0
        if verbose:
            print(f"  ⏱️  {dt:.1f}s   {result.stats()}")
            if result.error:
                print(f"  ⚠️  {result.error}")
        return result
    except Exception as e:
        dt = time.time() - t0
        result = ExtractionResult(error=f"{type(e).__name__}: {e}")
        if verbose:
            print(f"  ❌ {dt:.1f}s: {result.error}")
        return result


def load_chapter_text(
    corpus_path: str | Path,
    pages: list[int],
    *,
    lang: str = "vi",
) -> str:
    """Load + concat multiple pages from pages_vi/ (or pages/) thành chapter text."""
    root = Path(corpus_path)
    src_dir = root / ("pages_vi" if lang == "vi" else "pages")
    chunks: list[str] = []
    for pn in pages:
        f = src_dir / f"page-{pn:04d}.md"
        if f.exists():
            chunks.append(f"=== Trang {pn} ===\n{f.read_text()}")
    return "\n\n".join(chunks)


def extract_corpus_full(
    corpus_path: str | Path,
    *,
    output_path: str | Path,
    target_chapter_pages: int = 5,
    skip_existing: bool = True,
    verbose: bool = True,
) -> dict:
    """Extract toàn corpus → staging JSON.

    Output schema:
        {
          "corpus_id": str,
          "extracted_at": int,
          "chapters": [
            {
              "title": str, "start_page": int, "end_page": int,
              "result": {
                "passage": {...}, "methods": [...], "concepts": [...], "case_studies": [...]
              }
            }
          ],
          "stats": {chapters_done, chapters_failed, total_passages, total_methods, total_concepts, total_cases, time_seconds}
        }
    """
    root = Path(corpus_path)
    manifest_path = root / "manifest.json"
    chapters = group_sections_into_chapters(manifest_path, min_pages=target_chapter_pages)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume support: load existing staging if any
    state = {
        "corpus_id": root.name,
        "extracted_at": int(time.time()),
        "chapters": [],
        "stats": {},
    }
    if skip_existing and output_path.exists():
        try:
            state = json.loads(output_path.read_text())
            if verbose:
                print(f"⏯️  Resume: đã có {len(state['chapters'])} chapters extracted")
        except Exception:
            pass

    done_titles = {c["title"] for c in state["chapters"]}
    t0 = time.time()
    stats = {
        "chapters_done": len(state["chapters"]),
        "chapters_failed": 0,
        "total_passages": 0,
        "total_methods": 0,
        "total_concepts": 0,
        "total_cases": 0,
    }

    if verbose:
        print(f"🪷 Extract {len(chapters)} chapters từ {root.name}")
        print(f"   target_chapter_pages={target_chapter_pages}")
        print(f"   output={output_path}")
        print()

    for i, ch in enumerate(chapters, 1):
        if ch["title"] in done_titles:
            if verbose:
                print(f"⏭️  [{i}/{len(chapters)}] {ch['title'][:50]} — đã có, skip")
            continue
        text = load_chapter_text(root, ch["pages"], lang="vi")
        if not text.strip():
            if verbose:
                print(f"⏭️  [{i}/{len(chapters)}] {ch['title'][:50]} — empty pages")
            continue
        if verbose:
            print(f"📖 [{i}/{len(chapters)}] pp.{ch['start_page']}-{ch['end_page']} ({len(text):>5}c): {ch['title'][:50]}")
        result = extract_chapter(text, verbose=verbose)
        if result.error:
            stats["chapters_failed"] += 1
            state["chapters"].append({
                **ch,
                "error": result.error,
                "raw_response": result.raw_response[:500],
            })
        else:
            stats["chapters_done"] += 1
            if result.passage:
                stats["total_passages"] += 1
            stats["total_methods"] += len(result.methods)
            stats["total_concepts"] += len(result.concepts)
            stats["total_cases"] += len(result.case_studies)
            state["chapters"].append({
                **ch,
                "result": {
                    "passage": result.passage,
                    "methods": result.methods,
                    "concepts": result.concepts,
                    "case_studies": result.case_studies,
                },
            })
        # Persist after each chapter (interruption-safe)
        state["stats"] = {**stats, "time_seconds": time.time() - t0}
        output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))

    if verbose:
        print()
        print(_format_extraction_stats(state["stats"]))
    return state


def _format_extraction_stats(s: dict) -> str:
    return f"""
{'='*60}
📊 KẾT QUẢ EXTRACT
{'='*60}
  ✅ Chapters done:    {s.get('chapters_done', 0)}
  ❌ Chapters failed:  {s.get('chapters_failed', 0)}
  📝 Total passages:   {s.get('total_passages', 0)}
  🛠️  Total methods:   {s.get('total_methods', 0)}
  💎 Total concepts:   {s.get('total_concepts', 0)}
  📚 Total cases:      {s.get('total_cases', 0)}
  ⏱️  Time:            {s.get('time_seconds', 0)/60:.1f} phút
"""


def group_sections_into_chapters(manifest_path: str | Path, *, min_pages: int = 1) -> list[dict]:
    """Group manifest sections thành "chapters" hợp lý cho extraction.

    Manifest của quyển 3 có 173 L1 sections nhưng nhiều sections chỉ 1 trang.
    Em group consecutive L1 sections vào 1 chapter nếu < 4 trang để giảm số API call.
    """
    m = json.loads(Path(manifest_path).read_text())
    sections = m.get("sections", [])
    # Only L1 sections (major chapter markers)
    l1 = [s for s in sections if s.get("level") == 1]
    chapters: list[dict] = []
    i = 0
    while i < len(l1):
        s = l1[i]
        start = s.get("start_page") or 1
        end = s.get("end_page") or start
        title = s.get("title", f"Chương từ trang {start}")
        # Greedy merge: nếu chapter này quá ngắn, gộp với sections kế tiếp
        while end - start + 1 < min_pages and i + 1 < len(l1):
            i += 1
            s_next = l1[i]
            end = s_next.get("end_page") or s_next.get("start_page") or end
        chapters.append({
            "title": title,
            "start_page": start,
            "end_page": end,
            "pages": list(range(start, end + 1)),
        })
        i += 1
    return chapters
