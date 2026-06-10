#!/usr/bin/env python3
"""Remap per-line translations sang middle.json MỚI bằng khớp nội dung ZH.

Bối cảnh: middle.json cũ của Thiết Bản hỏng (merge swarm dồn/lặp trang) →
OCR lại nguyên cuốn → line_id đổi toàn bộ. Bản dịch 24.804 dòng gắn line_id cũ.
Giải pháp: build dict normalize(zh) → vi từ (old middle + old translations),
apply vào new middle theo từng line, ghi translations mới.

Usage:
    python3 scripts/remap_translations_by_zh.py \
        --old-middle <path old middle.json> \
        --old-trans  <path old translations dir> \
        --new-middle <path new middle.json> \
        --out-trans  <path translations dir để ghi> \
        [--apply]   # mặc định dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import time
from pathlib import Path

RE_WS = re.compile(r"\s+")


def norm_zh(s: str) -> str:
    return RE_WS.sub("", (s or "").strip())


def iter_lines(middle: dict):
    """Yield (page_num, line_id, zh_text) theo đúng logic page_layout."""
    for pidx, page in enumerate(middle.get("pdf_info", [])):
        page_num = pidx + 1
        blocks = page.get("para_blocks", page.get("preproc_blocks", []))
        preproc = page.get("preproc_blocks") or []
        for b in blocks:
            if not b.get("lines") and b.get("lines_deleted"):
                for pb in preproc:
                    if pb.get("bbox") == b.get("bbox") or pb.get("index") == b.get("index"):
                        if pb.get("lines"):
                            b["lines"] = pb["lines"]
                            break
        for ridx, block in enumerate(blocks, start=1):
            if block.get("type") not in ("text", "title", "list", "table", "index",
                                          "table_caption", "figure_caption"):
                continue
            for lidx, line in enumerate(block.get("lines", []), start=1):
                spans = line.get("spans", [])
                text = "".join(s.get("content", "") for s in spans).strip()
                if not text:
                    continue
                yield page_num, f"r{ridx:03d}", f"r{ridx:03d}-l{lidx:03d}", text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-middle", required=True)
    ap.add_argument("--old-trans", required=True)
    ap.add_argument("--new-middle", required=True)
    ap.add_argument("--out-trans", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    old_middle = json.loads(Path(args.old_middle).read_text())
    new_middle = json.loads(Path(args.new_middle).read_text())
    old_trans_root = Path(args.old_trans)

    # 1. Build zh → vi từ old
    zh2vi: dict[str, str] = {}
    n_old_vi = 0
    for page_num, rid, line_id, zh in iter_lines(old_middle):
        tp = old_trans_root / f"p{page_num:04d}" / f"{rid}.json"
        if not tp.exists():
            continue
        try:
            entries = json.loads(tp.read_text()).get("lines", {})
        except Exception:
            continue
        vi = ((entries.get(line_id) or {}).get("text_vi") or "").strip()
        if not vi:
            continue
        n_old_vi += 1
        key = norm_zh(zh)
        if key and key not in zh2vi:  # giữ bản dịch đầu tiên (trang lặp → vi như nhau)
            zh2vi[key] = vi

    print(f"old translated lines: {n_old_vi} | unique zh keys: {len(zh2vi)}")

    # 2. Apply vào new middle
    out_root = Path(args.out_trans)
    pages: dict[str, dict] = {}  # "p0001/r001" -> {line_id: vi}
    hit = miss = 0
    miss_samples = []
    for page_num, rid, line_id, zh in iter_lines(new_middle):
        vi = zh2vi.get(norm_zh(zh))
        if vi:
            hit += 1
            pages.setdefault(f"p{page_num:04d}/{rid}", {})[line_id] = vi
        else:
            miss += 1
            if len(miss_samples) < 8:
                miss_samples.append((page_num, line_id, zh[:40]))

    print(f"new lines: hit={hit} miss={miss} ({100.0*hit/max(1,hit+miss):.1f}% mapped)")
    print("miss samples:", *[f"\n  p{p} {l}: {z}" for p, l, z in miss_samples])

    if not args.apply:
        print("\n(dry-run — thêm --apply để ghi)")
        return

    # 3. Ghi translations mới (xoá dir cũ — caller đã backup)
    if out_root.exists():
        shutil.rmtree(out_root)
    now = int(time.time())
    for key, lines in pages.items():
        pdir, rid = key.split("/")
        d = out_root / pdir
        d.mkdir(parents=True, exist_ok=True)
        payload = {"lines": {
            lid: {"text_vi": vi, "status": "auto", "translator": "remap-zh",
                  "version": 1, "updated_at": now}
            for lid, vi in lines.items()
        }}
        (d / f"{rid}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"✅ wrote {len(pages)} region files → {out_root}")


if __name__ == "__main__":
    main()
