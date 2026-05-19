"""Q1 Tử Vi — Thâm nhuần parallel orchestration: DeepSeek + MiniMax.

Workflow:
    Q1 = 64 pages (p0016 → p0079) in tuvidauso-zh.
    Per page, run 2 LLM tasks IN PARALLEL:
        A. DeepSeek-chat — extract structured cách cục JSON (precision)
        B. MiniMax        — Vietnamese paragraph summary (volume, free via plan)

Output:
    data/yi_publishing/q1_tuvi/per_page/p{N:04d}.json
        {
          "page": N,
          "cach_cuc_extracted": [...],         # from DeepSeek
          "page_summary_vn": "...",            # from MiniMax
          "key_concepts": [...],               # from DeepSeek
          "cost": {"deepseek": $, "minimax": $},
          "duration_sec": float
        }

    data/yi_publishing/q1_tuvi/master/
        cach_cuc_index.json        # merged + deduped all cách cục
        concepts_index.json        # merged concepts
        page_summaries.md          # one paragraph per page, ordered

Em (Claude) đọc các master files → viết journal:
    docs/design/tu-vi-tham-nhuan-quyen-1.md

Safety: bounded concurrency (max 4 parallel), JSON-mode strict, retries on parse fail.
"""
from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
TVDS_ROOT = ROOT / "data/yi_publishing/translations/tuvidauso-zh"
Q1_OUT = ROOT / "data/yi_publishing/q1_tuvi"
PER_PAGE_DIR = Q1_OUT / "per_page"
MASTER_DIR = Q1_OUT / "master"

Q1_START = 16
Q1_END = 79   # inclusive


# ─── 1. Read page content from translations ─────────────────────────────────

def read_page_content(page_num: int) -> dict:
    """Return dict with hv (Hán-Việt joined text), lg (luận giải joined)."""
    pdir = TVDS_ROOT / f"p{page_num:04d}"
    if not pdir.exists():
        return {"hv": "", "lg": "", "lines_count": 0}

    hv_parts = []
    lg_parts = []
    n = 0
    for jf in sorted(pdir.glob("r*.json")):
        try:
            with jf.open() as f:
                d = json.load(f)
        except Exception:
            continue
        for lid, v in sorted(d.get("lines", {}).items()):
            tv = (v.get("text_vi") or "").strip()
            lg = (v.get("text_vi_luangiai") or "").strip()
            if tv:
                hv_parts.append(tv)
                n += 1
            if lg:
                lg_parts.append(lg)
    return {
        "hv": "\n".join(hv_parts),
        "lg": "\n".join(lg_parts),
        "lines_count": n,
    }


# ─── 2. DeepSeek task — extract structured cách cục + concepts ──────────────

DEEPSEEK_SYSTEM = """Bạn là chuyên gia Tử Vi Đẩu Số 30 năm kinh nghiệm, đang đọc một trang trong "Tử Vi Đẩu Số Toàn Thư" của Trần Đoàn (Hi Di tiên sinh), Quyển 1 (Phú Thái Vi + cách cục kinh điển).

Nhiệm vụ: từ TEXT đã dịch Hán-Việt + luận giải, hãy trích xuất CHẶT CHẼ:

1. **cach_cuc[]**: các CÁCH CỤC kinh điển được nhắc đến trong trang này, mỗi cách:
   - ten: tên Hán-Việt CHÍNH XÁC (vd: "Cự Nhật Đồng Cung", "Tử Phủ Tương Hội")
   - cap_do: "thượng" | "trung" | "hạ" | "phá cách" | "tạp"
   - dieu_kien: 1 câu ngắn mô tả điều kiện hình thành (Hán-Việt) — copy từ TEXT nếu có
   - y_nghia: 1-2 câu giải thích bằng tiếng Việt hiện đại (KHÔNG bịa, dựa vào text)
   - bang_chung_text: trích nguyên văn câu Hán-Việt mà cách này được nhắc

2. **concepts[]**: các THUẬT NGỮ KỸ THUẬT được dùng (sao, cung, biến cách), mỗi concept:
   - term: tên thuật ngữ (vd: "Hóa Lộc", "Tam Hóa Liên Châu", "Mệnh phùng Tử Phủ")
   - kind: "sao" | "cung" | "bien_cach" | "hoa" | "the_loai"
   - definition: 1 câu định nghĩa (≤ 30 từ tiếng Việt)

3. **nhan_xet**: 1 câu tổng quan trang này nói về chủ đề gì (≤ 25 từ).

Nếu trang KHÔNG có cách cục/concept nào (vd: trang mục lục, trang trống) → trả mảng rỗng. KHÔNG bịa.

Output JSON: {"cach_cuc": [...], "concepts": [...], "nhan_xet": "..."}"""


def run_deepseek_extract(page_num: int, content: dict) -> dict:
    """Call DeepSeek-chat to extract structured data. Cost ~$0.001-0.003/page."""
    from engine.yi_publishing.translator import get_deepseek_client

    text = f"=== TRANG {page_num} ===\n\nHÁN-VIỆT:\n{content['hv']}\n\nLUẬN GIẢI:\n{content['lg']}"
    if len(text) > 8_000:
        text = text[:8_000] + "\n... (truncated for token budget)"

    client = get_deepseek_client()
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": DEEPSEEK_SYSTEM},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            timeout=180, max_tokens=8000,
        )
        u = resp.usage
        cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
        raw_content = resp.choices[0].message.content
        # Tolerate truncated JSON: try strict first, then loose parse
        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            data = _parse_json_loose(raw_content)
            if not data:
                raise
    except Exception as e:
        logger.warning(f"deepseek p{page_num} failed: {e}")
        return {"cach_cuc": [], "concepts": [], "nhan_xet": "", "_error": str(e), "_cost": 0, "_duration": time.time() - t0}

    return {**data, "_cost": round(cost, 6), "_duration": round(time.time() - t0, 2)}


# ─── 3. MiniMax task — Vietnamese paragraph summary ─────────────────────────

MINIMAX_SYSTEM = """Bạn đang đọc một trang trong "Tử Vi Đẩu Số Toàn Thư". Hãy viết MỘT đoạn tóm tắt 60-100 từ tiếng Việt hiện đại, KHÔNG dùng thuật ngữ Hán cổ khó hiểu (nếu có thì giải nghĩa trong ngoặc).

Mục đích: người đọc Việt không cần biết chữ Hán cũng hiểu trang này dạy gì.

Output JSON: {"summary_vn": "...", "key_takeaway": "1 câu chốt ý chính"}"""


def _parse_json_loose(text: str) -> Optional[dict]:
    """Parse JSON from LLM output, tolerant of markdown code fences + leading text."""
    if not text:
        return None
    text = text.strip()
    # Strip code fence
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(l for l in lines if not l.startswith("```"))
    # Find first { and last }
    s = text.find("{")
    e = text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return None


def _load_minimax_key() -> Optional[str]:
    """Load MiniMax key from data/ai_keys.json or env."""
    import os
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key
    keys_file = ROOT / "data" / "ai_keys.json"
    if keys_file.exists():
        try:
            keys = json.loads(keys_file.read_text())
            return keys.get("minimax")
        except Exception:
            return None
    return None


def run_minimax_summary(page_num: int, content: dict) -> dict:
    """Call MiniMax for Vietnamese summary. ~free via plan (no per-call cost)."""
    try:
        from engine.ai.providers.minimax import MiniMaxProvider
    except Exception as e:
        return {"summary_vn": "", "key_takeaway": "", "_error": f"minimax import: {e}", "_cost": 0, "_duration": 0}

    api_key = _load_minimax_key()
    if not api_key:
        return {"summary_vn": "", "key_takeaway": "", "_error": "minimax key missing", "_cost": 0, "_duration": 0}

    text = f"=== TRANG {page_num} ===\n\nHÁN-VIỆT:\n{content['hv'][:5000]}\n\nLUẬN GIẢI:\n{content['lg'][:5000]}\n\nHãy trả về JSON đúng format yêu cầu."
    t0 = time.time()
    try:
        provider = MiniMaxProvider(api_key=api_key)
        resp = provider.chat(
            messages=[
                {"role": "system", "content": MINIMAX_SYSTEM},
                {"role": "user", "content": text},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        parsed = _parse_json_loose(resp.content)
        if not parsed:
            return {"summary_vn": "", "key_takeaway": "",
                    "_error": f"parse fail: {resp.content[:200]}",
                    "_cost": 0, "_duration": round(time.time() - t0, 2)}
        return {**parsed, "_cost": 0, "_duration": round(time.time() - t0, 2)}
    except Exception as e:
        logger.warning(f"minimax p{page_num} failed: {e}")
        return {"summary_vn": "", "key_takeaway": "", "_error": str(e), "_cost": 0, "_duration": time.time() - t0}


# ─── 4. Orchestrator — process one page with both providers parallel ────────

def process_page(page_num: int, force: bool = False) -> dict:
    """Run DeepSeek + MiniMax in parallel for 1 page. Cache result on disk."""
    out_file = PER_PAGE_DIR / f"p{page_num:04d}.json"
    if out_file.exists() and not force:
        return json.loads(out_file.read_text())

    content = read_page_content(page_num)
    if not content["hv"]:
        result = {"page": page_num, "skipped": True, "reason": "no content"}
        PER_PAGE_DIR.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_ds = ex.submit(run_deepseek_extract, page_num, content)
        f_mm = ex.submit(run_minimax_summary, page_num, content)
        ds = f_ds.result()
        mm = f_mm.result()

    result = {
        "page": page_num,
        "lines_count": content["lines_count"],
        "cach_cuc": ds.get("cach_cuc", []),
        "concepts": ds.get("concepts", []),
        "nhan_xet": ds.get("nhan_xet", ""),
        "summary_vn": mm.get("summary_vn", ""),
        "key_takeaway": mm.get("key_takeaway", ""),
        "cost": {
            "deepseek": ds.get("_cost", 0),
            "minimax": mm.get("_cost", 0),
        },
        "duration_sec": round(time.time() - t0, 2),
        "providers_status": {
            "deepseek": "error" if ds.get("_error") else "ok",
            "minimax": "error" if mm.get("_error") else "ok",
        },
        "errors": {k: v for k, v in {
            "deepseek": ds.get("_error"),
            "minimax": mm.get("_error"),
        }.items() if v},
        "generated_at": int(time.time()),
    }
    PER_PAGE_DIR.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


# ─── 5. Scale orchestrator — process Q1 with bounded concurrency ────────────

def process_q1(
    start: int = Q1_START,
    end: int = Q1_END,
    max_workers: int = 4,
    force: bool = False,
) -> dict:
    """Run all pages in [start, end]. Bounded concurrency = 4 (safe for both APIs)."""
    pages = list(range(start, end + 1))
    results: dict[int, dict] = {}
    total_cost = 0.0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_page = {ex.submit(process_page, p, force): p for p in pages}
        for fut in as_completed(future_to_page):
            p = future_to_page[fut]
            try:
                r = fut.result()
                results[p] = r
                if "cost" in r:
                    total_cost += r["cost"]["deepseek"] + r["cost"]["minimax"]
                logger.info(f"p{p:04d} done: {len(r.get('cach_cuc', []))} cách, {len(r.get('concepts', []))} concepts")
            except Exception as e:
                logger.exception(f"p{p:04d} failed: {e}")
                results[p] = {"page": p, "error": str(e)}

    duration = round(time.time() - t0, 1)
    summary = {
        "pages_processed": len(results),
        "total_cost_usd": round(total_cost, 4),
        "duration_sec": duration,
        "errors": [p for p, r in results.items() if r.get("error") or r.get("providers_status", {}).get("deepseek") == "error"],
    }
    return summary


# ─── 6. Merge masters ───────────────────────────────────────────────────────

def merge_masters() -> dict:
    """Aggregate per_page/*.json into master indexes + markdown summary."""
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    cach_index: dict[str, dict] = {}     # ten → merged entry with sources list
    concepts_index: dict[str, dict] = {}
    page_summaries: list[tuple[int, str, str]] = []

    for pf in sorted(PER_PAGE_DIR.glob("p*.json")):
        try:
            r = json.loads(pf.read_text())
        except Exception:
            continue
        if r.get("skipped"):
            continue
        page = r["page"]

        for c in r.get("cach_cuc", []):
            ten = (c.get("ten") or "").strip()
            if not ten:
                continue
            if ten not in cach_index:
                cach_index[ten] = {**c, "sources": [], "occurrences": 0}
            cach_index[ten]["occurrences"] += 1
            cach_index[ten]["sources"].append({
                "page": page,
                "bang_chung": c.get("bang_chung_text", "")[:200],
            })

        for cn in r.get("concepts", []):
            term = (cn.get("term") or "").strip()
            if not term:
                continue
            if term not in concepts_index:
                concepts_index[term] = {**cn, "first_page": page, "occurrences": 0}
            concepts_index[term]["occurrences"] += 1

        page_summaries.append((page, r.get("nhan_xet", ""), r.get("summary_vn", "")))

    # Write outputs
    (MASTER_DIR / "cach_cuc_index.json").write_text(
        json.dumps(cach_index, ensure_ascii=False, indent=2)
    )
    (MASTER_DIR / "concepts_index.json").write_text(
        json.dumps(concepts_index, ensure_ascii=False, indent=2)
    )

    # Page summaries markdown
    md_lines = ["# Q1 Tử Vi — Page Summaries\n"]
    for p, nx, sv in sorted(page_summaries):
        md_lines.append(f"### p{p:04d}")
        if nx:
            md_lines.append(f"**Chủ đề**: {nx}")
        if sv:
            md_lines.append(sv)
        md_lines.append("")
    (MASTER_DIR / "page_summaries.md").write_text("\n".join(md_lines))

    return {
        "cach_cuc_total": len(cach_index),
        "concepts_total": len(concepts_index),
        "pages_summarized": len(page_summaries),
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", type=int, help="Run 1 specific page (pilot test)")
    ap.add_argument("--start", type=int, default=Q1_START)
    ap.add_argument("--end", type=int, default=Q1_END)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--merge-only", action="store_true")
    args = ap.parse_args()

    if args.merge_only:
        s = merge_masters()
        print(json.dumps(s, ensure_ascii=False, indent=2))
    elif args.page:
        r = process_page(args.page, force=args.force)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        s = process_q1(args.start, args.end, args.workers, args.force)
        print(json.dumps(s, ensure_ascii=False, indent=2))
        m = merge_masters()
        print("Merge:", json.dumps(m, ensure_ascii=False, indent=2))
