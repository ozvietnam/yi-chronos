"""extract_perpage — Đọc SÂU từng trang. Mỗi trang Vi → 1 API call DeepSeek riêng.

KHÁC chunk-level (extract_to_wiki.py):
- chunk-level: 47 calls cho 321 trang (group 5-12 trang/chunk) → summarize chương
- per-page: 321 calls cho 321 trang (1 trang/call) → đào sâu chi tiết

Output staging JSON khác structure để dedupe khi commit:
{
  "corpus_id": "thieu-khang-tiet-tq",
  "extracted_at": int,
  "pages": [
    {
      "page": int,
      "page_path": str,
      "char_count": int,
      "result": {
        "summary_3line": str,   # 1-3 dòng tóm tắt page này
        "concepts": [{canonical_vi, canonical_zh, aliases[], short_note}],
        "methods": [{name_vi, name_zh, domain, procedure_steps[]}],
        "micro_cases": [{historical_event, inputs, predicted, actual, quote}],
        "quotes": [str]   # 0-3 trích nguyên văn đáng nhớ
      }
    }
  ],
  "stats": {pages_done, pages_failed, total_*}
}
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
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


PERPAGE_PROMPT = """Bạn là chuyên gia Mai Hoa Dịch Số đọc SÂU từng trang sách. Khác với extraction chapter-level (đã làm), lần này em đọc kỹ TỪNG TRANG để extract MỌI chi tiết — kể cả micro-cases, footnotes, sidebar, hình chú thích.

INPUT: 1 trang sách "Đồ Giải Mai Hoa Dịch Số" (bản dịch Việt).

NHIỆM VỤ: Phân tích trang → trả về JSON với 5 nhóm thông tin:

1. **summary_3line** (string ≤ 200 ký tự): tóm tắt 1-3 dòng nội dung trang này
   - Nói trang này dạy gì, có ví dụ gì, kết luận gì
   - Nếu trang chỉ là bảng/hình → mô tả bảng/hình

2. **concepts** (0-12 entries): MỌI thuật ngữ chuyên ngành mới hoặc được giải thích trên trang
   - `canonical_vi`: tên Hán-Việt chuẩn (vd: "Tiên Thiên Bát Quái")
   - `canonical_zh`: tên gốc Hán nếu sách có in
   - `aliases`: tên khác (≤ 3)
   - `short_note`: định nghĩa 1-2 câu (≤ 150 ký tự) **theo cách trang này giải thích**
   - ⚠️ Concept generic (vd: "Càn", "Khôn") chỉ extract nếu trang có giải nghĩa MỚI / SÂU. Không lặp lại định nghĩa cơ bản.

3. **methods** (0-3 entries): chỉ nếu trang có dạy QUY TRÌNH bước 1-2-3
   - `name_vi`, `name_zh`, `domain` (bốc/đọc/ứng_kỳ/biến_hoá/khác)
   - `procedure_steps`: list 2-7 bước, mỗi bước 1 câu súc tích

4. **micro_cases** (0-5 entries): MỌI ví dụ chiêm cụ thể trong trang, kể cả ví dụ ngắn 2-3 câu
   - `historical_event`: ngắn gọn (≤ 100 ký tự), ví dụ "Quẻ Sơn Hỏa Bí xem hôn nhân"
   - `inputs`: input cụ thể (giờ, ngày, trigger, observation) — nếu trang có
   - `predicted`: dự đoán Mai Hoa đưa ra
   - `actual`: kết quả thật (nếu có ghi)
   - `quote`: trích ≤ 200 ký tự nguyên văn trang (key sentence)

5. **quotes** (0-3 entries): 0-3 câu cốt lõi nhất từ trang, mỗi câu ≤ 200 ký tự
   - Chỉ chọn câu THẬT SỰ tinh tuý — không quote câu thường

⚠️ QUY TẮC NGHIÊM:
- CHỈ extract những gì THẬT SỰ có trong trang. KHÔNG bịa, KHÔNG suy diễn từ kiến thức ngoài trang.
- Nếu trang trống / chỉ có ISBN / chỉ có table of contents → trả tất cả arrays rỗng + summary_3line ngắn.
- JSON OUTPUT phải parse được (no markdown wrapper, no ```json fence).
- Tên người, địa danh giữ Hán-Việt (Thiệu Khang Tiết, không 邵康节 hoặc Shao Yong).

TRANG SÁCH (page {page_num}):
{page_text}

TRẢ VỀ JSON THUẦN:"""


@dataclass
class PerPageStats:
    pages_done: int = 0
    pages_failed: int = 0
    pages_empty: int = 0
    total_concepts: int = 0
    total_methods: int = 0
    total_cases: int = 0
    total_quotes: int = 0
    total_seconds: float = 0.0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    failures: list[str] = field(default_factory=list)


def _call_deepseek(prompt: str, *, timeout: int = 90) -> tuple[str, dict]:
    key = _load_deepseek_key()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY không có")
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 3000,
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"], d.get("usage", {})


def extract_one_page(page_num: int, page_text: str) -> tuple[dict | None, dict, str]:
    """Extract 1 trang. Returns (result_dict | None, usage, error_str)."""
    prompt = PERPAGE_PROMPT.format(page_num=page_num, page_text=page_text)
    try:
        raw, usage = _call_deepseek(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            if len(lines) >= 2:
                raw = "\n".join(lines[1:-1]).strip()
        result = json.loads(raw)
        return result, usage, ""
    except json.JSONDecodeError as e:
        return None, {}, f"JSON parse fail: {e}"
    except Exception as e:
        return None, {}, f"{type(e).__name__}: {e}"


def extract_corpus_perpage(
    corpus_path: str | Path,
    *,
    output_path: str | Path,
    skip_existing: bool = True,
    max_pages: int | None = None,
    start_page: int = 1,
    verbose: bool = True,
) -> dict:
    root = Path(corpus_path)
    pages_vi_dir = root / "pages_vi"
    if not pages_vi_dir.exists():
        return {"error": f"pages_vi/ không tồn tại trong {root}"}

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume support
    state = {
        "corpus_id": root.name,
        "extracted_at": int(time.time()),
        "pages": [],
        "stats": {},
    }
    if skip_existing and output_path.exists():
        try:
            state = json.loads(output_path.read_text())
            if verbose:
                print(f"⏯️  Resume: đã có {len(state['pages'])} trang trong staging")
        except Exception:
            pass

    done_pages = {p["page"] for p in state["pages"]}
    src_pages = sorted(pages_vi_dir.glob("page-*.md"))
    if start_page > 1:
        src_pages = [p for p in src_pages if int(p.stem.split("-")[1]) >= start_page]
    if max_pages:
        src_pages = src_pages[:max_pages]

    stats = PerPageStats(pages_done=len(done_pages))
    t0 = time.time()

    if verbose:
        print(f"🪷 Per-page extraction {len(src_pages)} pages từ {root.name}")
        print(f"   output={output_path}")
        print()

    for i, page_file in enumerate(src_pages, 1):
        pn = int(page_file.stem.split("-")[1])
        if pn in done_pages:
            if verbose and i % 50 == 0:
                print(f"⏭️  [{i}/{len(src_pages)}] page {pn} — done, skip")
            continue

        text = page_file.read_text()
        if not text.strip() or len(text.strip()) < 50:
            stats.pages_empty += 1
            state["pages"].append({
                "page": pn,
                "page_path": page_file.name,
                "char_count": len(text),
                "result": {"summary_3line": "(trang trống)", "concepts": [], "methods": [], "micro_cases": [], "quotes": []},
            })
            continue

        if verbose:
            print(f"📖 [{i}/{len(src_pages)}] page {pn:>3} ({len(text):>4}c)", end=" ", flush=True)

        result, usage, err = extract_one_page(pn, text)
        if err:
            stats.pages_failed += 1
            stats.failures.append(f"p{pn}: {err}")
            state["pages"].append({
                "page": pn,
                "page_path": page_file.name,
                "char_count": len(text),
                "error": err,
            })
            if verbose:
                print(f"❌ {err[:60]}")
        else:
            stats.pages_done += 1
            stats.total_concepts += len(result.get("concepts", []) or [])
            stats.total_methods += len(result.get("methods", []) or [])
            stats.total_cases += len(result.get("micro_cases", []) or [])
            stats.total_quotes += len(result.get("quotes", []) or [])
            stats.total_tokens_in += usage.get("prompt_tokens", 0)
            stats.total_tokens_out += usage.get("completion_tokens", 0)
            state["pages"].append({
                "page": pn,
                "page_path": page_file.name,
                "char_count": len(text),
                "result": result,
            })
            if verbose:
                summary = (result.get("summary_3line") or "")[:60]
                cnt = (
                    f"c={len(result.get('concepts',[]) or [])} "
                    f"m={len(result.get('methods',[]) or [])} "
                    f"x={len(result.get('micro_cases',[]) or [])}"
                )
                print(f"✅ [{cnt}] {summary}")

        # Persist after each page (interruption-safe)
        state["stats"] = {
            "pages_done": stats.pages_done,
            "pages_failed": stats.pages_failed,
            "pages_empty": stats.pages_empty,
            "total_concepts": stats.total_concepts,
            "total_methods": stats.total_methods,
            "total_cases": stats.total_cases,
            "total_quotes": stats.total_quotes,
            "total_tokens_in": stats.total_tokens_in,
            "total_tokens_out": stats.total_tokens_out,
            "time_seconds": time.time() - t0,
        }
        output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))

    if verbose:
        cost_in = stats.total_tokens_in * 0.27 / 1_000_000
        cost_out = stats.total_tokens_out * 1.10 / 1_000_000
        print(f"\n{'='*60}")
        print(f"📊 PER-PAGE EXTRACTION FINAL")
        print(f"{'='*60}")
        print(f"  ✅ Pages done:    {stats.pages_done}")
        print(f"  ❌ Pages failed:  {stats.pages_failed}")
        print(f"  ⊝  Pages empty:   {stats.pages_empty}")
        print(f"  💎 Concepts:      {stats.total_concepts}")
        print(f"  🛠️  Methods:       {stats.total_methods}")
        print(f"  📚 Micro-cases:   {stats.total_cases}")
        print(f"  💬 Quotes:        {stats.total_quotes}")
        print(f"  ⏱️  Time:          {(time.time()-t0)/60:.1f} phút")
        print(f"  💰 Cost:          ${cost_in + cost_out:.4f} (in={stats.total_tokens_in:,} / out={stats.total_tokens_out:,})")
    return state


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="data/yi_restored/thieu-khang-tiet-tq")
    ap.add_argument("--output", default="data/_logs/extract-tq-perpage.json")
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--start-page", type=int, default=1)
    args = ap.parse_args()
    extract_corpus_perpage(
        args.corpus,
        output_path=args.output,
        max_pages=args.max_pages,
        start_page=args.start_page,
    )
