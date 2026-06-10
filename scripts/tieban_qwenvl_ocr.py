#!/usr/bin/env python3
"""Re-OCR điều văn Thiết Bản bằng qwen2.5-VL 7B (Ollama local) — chạy đêm.

Spike 2026-06-10: qwen-VL đọc số điều + văn + anchor block CHUẨN (kể cả
anchor 一〇一〇十 mà MinerU OCR vỡ), nhưng cột tuổi hallucinate → chỉ lấy
{so, van, tap}; tuổi ứng merge sau từ bảng v1 (model.json MinerU).

Resumable: mỗi trang lưu data/tieban_qwenvl/pNNNN.json — chạy lại tự skip.

Usage:
    python3 scripts/tieban_qwenvl_ocr.py [--start 106] [--end 587] [--model qwen2.5vl:7b]
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF = PROJECT_ROOT / "data/raw_pdfs/shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk.pdf"
OUT_DIR = PROJECT_ROOT / "data/tieban_qwenvl"
OLLAMA = "http://localhost:11434/api/chat"

PROMPT = """Đây là 1 trang sách Thiết Bản Thần Số in điều văn dạng bảng 3 cột. Mỗi dòng gồm:
- Cột 1 (trái): số thứ tự điều trong block (一 đến 九; dòng cuối block ghi số đầy đủ kết thúc bằng 十, ví dụ 一〇一〇十 nghĩa là điều 1010)
- Cột 2 (giữa, CÓ THỂ TRỐNG): số tuổi ứng nhỏ (1-2 số xếp dọc)
- Cột 3: câu đoán chữ Hán

Hãy trích xuất TẤT CẢ các dòng theo đúng thứ tự, xuất JSON array, mỗi dòng 1 object:
{"so": "<cột 1 nguyên văn>", "tuoi": "<cột 2 hoặc null>", "van": "<cột 3>"}
CHỈ xuất JSON, không giải thích. Nếu trang có tiêu đề tập (như 子集) thì thêm object {"tap": "..."} ở đầu."""


def render_page(page: int, tmp: Path) -> Path:
    png = tmp / f"pg-{page}"
    subprocess.run(
        ["pdftoppm", "-png", "-f", str(page), "-l", str(page), "-r", "110",
         str(PDF), str(png)],
        check=True, capture_output=True,
    )
    hits = sorted(tmp.glob(f"pg-{page}-*.png")) or sorted(tmp.glob(f"pg-{page}*.png"))
    if not hits:
        raise RuntimeError(f"render failed p{page}")
    return hits[0]


def ocr_page(png: Path, model: str, timeout: int = 600) -> str:
    img = base64.b64encode(png.read_bytes()).decode()
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT, "images": [img]}],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 4000},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    return resp["message"]["content"]


def extract_json(raw: str):
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=106)
    ap.add_argument("--end", type=int, default=587)
    ap.add_argument("--model", default="qwen2.5vl:7b")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/tieban_qwenvl_render")
    tmp.mkdir(exist_ok=True)

    pages = list(range(args.start, args.end + 1))
    done = skip = fail = 0
    t_start = time.time()
    for i, page in enumerate(pages, 1):
        out_path = OUT_DIR / f"p{page:04d}.json"
        if out_path.exists():
            skip += 1
            continue
        t0 = time.time()
        try:
            png = render_page(page, tmp)
            raw = ocr_page(png, args.model)
            data = extract_json(raw)
            png.unlink(missing_ok=True)
        except Exception as e:
            fail += 1
            print(f"[{i}/{len(pages)}] p{page} FAIL: {str(e)[:120]}", flush=True)
            time.sleep(3)
            continue
        if data is None:
            fail += 1
            (OUT_DIR / f"p{page:04d}.rawfail.txt").write_text(raw)
            print(f"[{i}/{len(pages)}] p{page} JSON-FAIL (raw saved)", flush=True)
            continue
        out_path.write_text(json.dumps(
            {"page_pdf": page, "items": data, "model": args.model,
             "ocr_at": int(time.time())}, ensure_ascii=False))
        done += 1
        if done % 10 == 0 or i == len(pages):
            el = (time.time() - t_start) / 60
            rate = done / el if el > 0 else 0
            eta = (len(pages) - skip - done) / rate if rate > 0 else 0
            print(f"[{i}/{len(pages)}] p{page} ok ({time.time()-t0:.0f}s) | "
                  f"done={done} skip={skip} fail={fail} | {el:.0f}m elapsed, ~{eta:.0f}m left",
                  flush=True)

    print(f"FINISHED: done={done} skip={skip} fail={fail}", flush=True)
    sys.exit(1 if fail > 20 else 0)


if __name__ == "__main__":
    main()
