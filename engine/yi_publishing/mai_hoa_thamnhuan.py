"""Mai Hoa Q1+Q2 thâm nhuần — parallel DeepSeek + MiniMax.

Source: data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md (672 pages)
        Tác giả: Thiệu Khang Tiết (邵雍, 1011-1077)

Page boundaries (từ TOC):
    Q1: p15-115  (~100 pages) — Chu Dịch quái số, Ngũ hành sinh khắc, Bát quái tượng lệ
    Q2: p116-327 (~211 pages) — Chiêm bốc huyền cơ (Gia trạch, Hôn nhân, Sinh sản, ...)
    Q3: đã thâm nhuần (từ cuốn minh hoạ 321 trang Vương Hy Quý)
    Q4: p328-458 (~130 pages)
    Q5: p459-672 (~213 pages)

Output:
    data/yi_publishing/mai_hoa_thamnhuan/per_page/p{N:04d}.json
    data/yi_publishing/mai_hoa_thamnhuan/master/{methods_index,concepts_index,page_summaries}.json
"""
from __future__ import annotations

import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
SOURCE_MD = ROOT / "data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md"
OUT_ROOT = ROOT / "data/yi_publishing/mai_hoa_thamnhuan"
PER_PAGE_DIR = OUT_ROOT / "per_page"
MASTER_DIR = OUT_ROOT / "master"

Q1_START, Q1_END = 15, 115
Q2_START, Q2_END = 116, 327


def parse_pages() -> dict[int, str]:
    """Parse content.md → dict[page_num → page_text]."""
    text = SOURCE_MD.read_text()
    pages: dict[int, str] = {}
    # Pages separated by <a id="page-N"></a> markers
    parts = re.split(r'<a id="page-(\d+)"></a>', text)
    # parts[0] = header before page-1; [1] = "1", [2] = page 1 content; [3] = "2", [4] = page 2 content
    for i in range(1, len(parts) - 1, 2):
        try:
            num = int(parts[i])
            content = parts[i + 1].strip()
            # Strip HTML comment "Trang N" and ```code fence```
            content = re.sub(r'<!-- Trang \d+ -->', '', content)
            content = content.strip()
            if content:
                pages[num] = content
        except (ValueError, IndexError):
            continue
    return pages


# ─── DeepSeek extraction prompt ──────────────────────────────────────────────

DEEPSEEK_SYSTEM = """Bạn là chuyên gia Mai Hoa Dịch Số (梅花易數) 30 năm kinh nghiệm, đang đọc sách của Thiệu Khang Tiết (Tống, 1011-1077).

Nhiệm vụ: từ TEXT trang sách, trích xuất CHẶT CHẼ:

1. **methods[]**: các PHƯƠNG PHÁP / QUYẾT / CÔNG THỨC được nêu, mỗi method:
   - ten: tên phương pháp (vd: "Niên Nguyệt Nhật Thời", "Quan vật chiêm", "Khắc ứng")
   - linh_vuc: "chiêm bốc" | "an quái" | "ngũ hành" | "bát quái" | "thể dụng" | "khác"
   - quy_tac: 1-2 câu mô tả cách áp dụng (Hán-Việt nguyên văn nếu có)
   - y_nghia: 1-2 câu tiếng Việt hiện đại giải thích

2. **concepts[]**: các thuật ngữ kỹ thuật:
   - term: tên (vd: "Thể", "Dụng", "Quái Hổ", "Sinh", "Khắc")
   - kind: "khai_niem" | "quai" | "hao" | "than_sat" | "ngu_hanh" | "khac"
   - definition: 1 câu ≤ 30 từ tiếng Việt

3. **nhan_xet**: 1 câu chủ đề trang (≤ 25 từ).

Nếu trang trống / chỉ là mục lục → trả mảng rỗng. KHÔNG bịa.

Output JSON: {"methods": [...], "concepts": [...], "nhan_xet": "..."}"""

MINIMAX_SYSTEM = """Bạn đang đọc một trang trong "Mai Hoa Dịch Số" của Thiệu Khang Tiết. Viết MỘT đoạn tóm tắt 60-100 từ tiếng Việt hiện đại, không dùng thuật ngữ Hán cổ khó hiểu (nếu có thì giải nghĩa trong ngoặc).

Output JSON: {"summary_vn": "...", "key_takeaway": "1 câu ý chính"}"""


def _parse_json_loose(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(l for l in text.split("\n") if not l.startswith("```"))
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return None


def _load_minimax_key() -> Optional[str]:
    import os
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key
    f = ROOT / "data" / "ai_keys.json"
    if f.exists():
        try:
            return json.loads(f.read_text()).get("minimax")
        except Exception:
            return None
    return None


def run_deepseek(page_num: int, content: str) -> dict:
    from engine.yi_publishing.translator import get_deepseek_client
    text = f"=== TRANG {page_num} ===\n\n{content[:8000]}"
    client = get_deepseek_client()
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": DEEPSEEK_SYSTEM},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"}, timeout=180, max_tokens=4000,
        )
        u = resp.usage
        cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
        raw = resp.choices[0].message.content
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = _parse_json_loose(raw) or {}
        return {**data, "_cost": round(cost, 6), "_duration": round(time.time() - t0, 2)}
    except Exception as e:
        logger.warning(f"deepseek p{page_num} failed: {e}")
        return {"methods": [], "concepts": [], "nhan_xet": "",
                "_error": str(e), "_cost": 0, "_duration": time.time() - t0}


def run_minimax(page_num: int, content: str) -> dict:
    api_key = _load_minimax_key()
    if not api_key:
        return {"summary_vn": "", "key_takeaway": "", "_error": "no minimax key", "_cost": 0, "_duration": 0}
    from engine.ai.providers.minimax import MiniMaxProvider
    text = f"=== TRANG {page_num} ===\n\n{content[:5000]}\n\nTrả JSON đúng format yêu cầu."
    t0 = time.time()
    try:
        provider = MiniMaxProvider(api_key=api_key)
        resp = provider.chat(
            messages=[
                {"role": "system", "content": MINIMAX_SYSTEM},
                {"role": "user", "content": text},
            ],
            max_tokens=800, temperature=0.3,
        )
        parsed = _parse_json_loose(resp.content)
        if not parsed:
            return {"summary_vn": "", "key_takeaway": "",
                    "_error": f"parse fail: {resp.content[:100]}",
                    "_cost": 0, "_duration": round(time.time() - t0, 2)}
        return {**parsed, "_cost": 0, "_duration": round(time.time() - t0, 2)}
    except Exception as e:
        return {"summary_vn": "", "key_takeaway": "", "_error": str(e), "_cost": 0, "_duration": time.time() - t0}


def process_page(page_num: int, content: str, force: bool = False) -> dict:
    out_file = PER_PAGE_DIR / f"p{page_num:04d}.json"
    if out_file.exists() and not force:
        return json.loads(out_file.read_text())

    if not content or len(content) < 30:
        result = {"page": page_num, "skipped": True, "reason": "too short"}
        PER_PAGE_DIR.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_ds = ex.submit(run_deepseek, page_num, content)
        f_mm = ex.submit(run_minimax, page_num, content)
        ds = f_ds.result()
        mm = f_mm.result()

    result = {
        "page": page_num,
        "methods": ds.get("methods", []),
        "concepts": ds.get("concepts", []),
        "nhan_xet": ds.get("nhan_xet", ""),
        "summary_vn": mm.get("summary_vn", ""),
        "key_takeaway": mm.get("key_takeaway", ""),
        "cost": {"deepseek": ds.get("_cost", 0), "minimax": mm.get("_cost", 0)},
        "duration_sec": round(time.time() - t0, 2),
        "errors": {k: v for k, v in {"deepseek": ds.get("_error"), "minimax": mm.get("_error")}.items() if v},
        "generated_at": int(time.time()),
    }
    PER_PAGE_DIR.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def process_range(start: int, end: int, workers: int = 4, force: bool = False) -> dict:
    pages = parse_pages()
    to_process = [(p, pages[p]) for p in range(start, end + 1) if p in pages]
    print(f"Processing {len(to_process)} pages [{start}..{end}], {workers} workers...")
    t0 = time.time()
    results: dict[int, dict] = {}
    total_cost = 0.0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process_page, p, content, force): p for p, content in to_process}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                r = fut.result()
                results[p] = r
                if "cost" in r:
                    total_cost += r["cost"]["deepseek"] + r["cost"]["minimax"]
                methods = len(r.get("methods", []))
                concepts = len(r.get("concepts", []))
                logger.info(f"p{p:04d} done: {methods} methods, {concepts} concepts")
            except Exception as e:
                logger.exception(f"p{p:04d} failed")
                results[p] = {"page": p, "error": str(e)}
    return {
        "pages": len(results),
        "total_cost_usd": round(total_cost, 4),
        "duration_sec": round(time.time() - t0, 1),
        "errors": [p for p, r in results.items() if r.get("error") or r.get("errors", {}).get("deepseek")],
    }


def merge_masters() -> dict:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    methods_idx: dict[str, dict] = {}
    concepts_idx: dict[str, dict] = {}
    page_sums: list[tuple[int, str, str]] = []
    for pf in sorted(PER_PAGE_DIR.glob("p*.json")):
        try:
            r = json.loads(pf.read_text())
        except Exception:
            continue
        if r.get("skipped"):
            continue
        page = r["page"]
        for m in r.get("methods", []):
            ten = (m.get("ten") or "").strip()
            if not ten:
                continue
            if ten not in methods_idx:
                methods_idx[ten] = {**m, "first_page": page, "occurrences": 0, "pages": []}
            methods_idx[ten]["occurrences"] += 1
            methods_idx[ten]["pages"].append(page)
        for c in r.get("concepts", []):
            term = (c.get("term") or "").strip()
            if not term:
                continue
            if term not in concepts_idx:
                concepts_idx[term] = {**c, "first_page": page, "occurrences": 0}
            concepts_idx[term]["occurrences"] += 1
        page_sums.append((page, r.get("nhan_xet", ""), r.get("summary_vn", "")))

    (MASTER_DIR / "methods_index.json").write_text(json.dumps(methods_idx, ensure_ascii=False, indent=2))
    (MASTER_DIR / "concepts_index.json").write_text(json.dumps(concepts_idx, ensure_ascii=False, indent=2))
    md = ["# Mai Hoa — Page Summaries\n"]
    for p, nx, sv in sorted(page_sums):
        md.append(f"### p{p:04d}")
        if nx: md.append(f"**Chủ đề**: {nx}")
        if sv: md.append(sv)
        md.append("")
    (MASTER_DIR / "page_summaries.md").write_text("\n".join(md))
    return {"methods": len(methods_idx), "concepts": len(concepts_idx), "pages": len(page_sums)}


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--quyen", choices=["q1", "q2", "both"], default="q1")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--merge-only", action="store_true")
    args = ap.parse_args()

    if args.merge_only:
        print(json.dumps(merge_masters(), ensure_ascii=False, indent=2))
    else:
        if args.quyen == "q1":
            s = process_range(Q1_START, Q1_END, args.workers, args.force)
        elif args.quyen == "q2":
            s = process_range(Q2_START, Q2_END, args.workers, args.force)
        else:
            s = process_range(Q1_START, Q2_END, args.workers, args.force)
        print(json.dumps(s, ensure_ascii=False, indent=2))
        m = merge_masters()
        print("Merge:", json.dumps(m, ensure_ascii=False, indent=2))
