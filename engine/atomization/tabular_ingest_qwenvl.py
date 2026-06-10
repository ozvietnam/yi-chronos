"""Tabular Ingest v3 — bảng tra Thiết Bản từ qwen2.5-VL JSON (nguồn chính xác nhất).

Nguồn: data/tieban_qwenvl/pNNNN.json — mỗi trang list items {so, tuoi, van} | {tap}.
Spike 2026-06-10: qwen-VL đọc SỐ + VĂN + ANCHOR chuẩn; cột tuổi hallucinate → BỎ,
tuổi ứng merge từ bảng v1 (MinerU model.json) theo seq_no.
VI: map zh→vi từ translations cũ (norm exact) + fallback v1 verse cùng seq_no.

Usage:
    python3 -m engine.atomization.tabular_ingest_qwenvl --corpus thiet-ban-than-so [--commit]
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.atomization.tabular_ingest_model import (  # noqa: E402
    CN_DIGIT, norm, parse_anchor, parse_unit, strip_leading_cn_num, build_zh2vi,
)

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema_tabular.sql"
QWENVL_DIR = PROJECT_ROOT / "data" / "tieban_qwenvl"

BOOK_ID = "shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk"
RE_VOLUME = re.compile(r"^([子丑寅卯辰巳午未申酉戌亥乾坎艮震巽离坤兑])\s*集$")


def load_v1(corpus: str) -> dict[int, dict]:
    """seq_no → {age_marks_raw, vi, zh} từ bảng v1 hiện có (trước khi đè)."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT seq_no, age_marks_raw, vi, zh FROM tabular_verses
           WHERE book_corpus_id=? AND seq_no IS NOT NULL""", (corpus,)).fetchall()
    conn.close()
    out: dict[int, dict] = {}
    for seq, age, vi, zh in rows:
        if seq not in out:
            out[seq] = {"age": age, "vi": vi, "zh": zh}
    return out


def parse_qwenvl(zh2vi: dict[str, str], v1: dict[int, dict]):
    files = sorted(QWENVL_DIR.glob("p*.json"))
    stats = {"pages": len(files), "items": 0, "anchors_read": 0,
             "vi_from_zh2vi": 0, "vi_from_v1": 0, "age_from_v1": 0}
    volume = None
    blocks: list[dict] = []
    cur = {"verses": [], "anchor": None, "last_unit": 0}

    def close_block():
        nonlocal cur
        if cur["verses"]:
            blocks.append(cur)
        cur = {"verses": [], "anchor": None, "last_unit": 0}

    for f in files:
        d = json.loads(f.read_text())
        page_pdf = d["page_pdf"]
        for it in d.get("items", []):
            if not isinstance(it, dict):
                continue
            if "tap" in it:
                t = norm(str(it["tap"]))
                if RE_VOLUME.match(t):
                    volume = t
                continue
            so = str(it.get("so") or "").strip()
            van = str(it.get("van") or "").strip()
            unit = parse_unit(so)
            anchor = parse_anchor(so)
            # PROMPT-ECHO GUARD: prompt có ví dụ "一〇一〇十" — model chép lại khi
            # không đọc rõ số mốc. Anchor 1010 chỉ hợp lệ ở vùng trang đầu điều văn.
            if anchor == 1010 and page_pdf > 110:
                anchor = None
                if unit is None:
                    unit = 10  # vẫn là dòng kết block
            if not van:
                # dòng anchor đứng riêng (không lời đoán) — vẫn phải chốt block!
                if anchor is not None:
                    cur["anchor"] = anchor
                    stats["anchors_read"] += 1
                    close_block()
                elif unit == 10:
                    close_block()
                continue
            stats["items"] += 1
            if anchor is not None or unit == 10 or (so and norm(so).endswith(("十", "+"))
                                                    and len(norm(so)) >= 3):
                a = anchor if anchor is not None else parse_anchor(so)
                cur["verses"].append({
                    "volume": volume, "seq_in_block": 10, "zh": van,
                    "page_pdf": page_pdf, "line_ref": f"qwenvl:p{page_pdf}", "note": None,
                })
                if a:
                    cur["anchor"] = a
                    stats["anchors_read"] += 1
                close_block()
            elif unit is not None:
                if unit <= cur["last_unit"]:
                    close_block()
                cur["last_unit"] = unit
                cur["verses"].append({
                    "volume": volume, "seq_in_block": unit, "zh": van,
                    "page_pdf": page_pdf, "line_ref": f"qwenvl:p{page_pdf}", "note": None,
                })
            else:
                # item không số (hiếm với qwen) — nối vào verse trước nếu có
                if cur["verses"]:
                    cur["verses"][-1]["zh"] += van
                    cur["verses"][-1]["note"] = (cur["verses"][-1].get("note") or "") + "|join"
    close_block()

    # LIS + interpolation trên anchors (tái dùng cách v2)
    n = len(blocks)
    marks = [(i, blocks[i]["anchor"] // 10) for i in range(n) if blocks[i]["anchor"]]
    tails: list[int] = []; tails_idx: list[int] = []
    parent = [-1] * len(marks)
    for mi, (bi, bno) in enumerate(marks):
        pos = bisect.bisect_left(tails, bno)
        if pos == len(tails):
            tails.append(bno); tails_idx.append(mi)
        else:
            tails[pos] = bno; tails_idx[pos] = mi
        parent[mi] = tails_idx[pos - 1] if pos > 0 else -1
    lis = set()
    if tails_idx:
        c = tails_idx[-1]
        while c != -1:
            lis.add(c); c = parent[c]
    trusted = [(bi, bno) for mi, (bi, bno) in enumerate(marks) if mi in lis]
    stats["anchors_trusted"] = len(trusted)
    stats["anchors_rejected"] = len(marks) - len(trusted)

    bno_of = [None] * n
    conf_of = ["uncertain"] * n
    for bi, bno in trusted:
        bno_of[bi] = bno; conf_of[bi] = "anchored"
    for k in range(len(trusted) + 1):
        lo = trusted[k - 1] if k > 0 else None
        hi = trusted[k] if k < len(trusted) else None
        start = (lo[0] + 1) if lo else 0
        end = (hi[0] - 1) if hi else n - 1
        if start > end:
            continue
        clean = lo is not None and hi is not None and (hi[0] - lo[0]) == (hi[1] - lo[1])
        for i in range(start, end + 1):
            bno_of[i] = (lo[1] + (i - lo[0])) if lo else (hi[1] - (hi[0] - i))
            conf_of[i] = "interpolated" if clean else "uncertain"

    verses: list[dict] = []
    for i, b in enumerate(blocks):
        bno = bno_of[i]
        seen: set[int] = set()
        for v in b["verses"]:
            u = v["seq_in_block"]
            v["seq_no"] = (bno - 1) * 10 + u if bno else None
            v["seq_confidence"] = conf_of[i]
            if u in seen:
                v["seq_confidence"] = "uncertain"
                v["note"] = (v.get("note") or "") + "|dup-unit"
            seen.add(u)
            # VI: zh2vi exact → v1 cùng seq
            vi = zh2vi.get(norm(strip_leading_cn_num(v["zh"]))) or zh2vi.get(norm(v["zh"]))
            if vi:
                stats["vi_from_zh2vi"] += 1
            elif v["seq_no"] and v["seq_no"] in v1 and (v1[v["seq_no"]]["vi"] or "").strip():
                vi = v1[v["seq_no"]]["vi"]
                stats["vi_from_v1"] += 1
                v["note"] = (v.get("note") or "") + "|vi-from-v1"
            v["vi"] = vi
            # tuổi từ v1
            if v["seq_no"] and v["seq_no"] in v1 and v1[v["seq_no"]]["age"]:
                v["age_marks_raw"] = v1[v["seq_no"]]["age"]
                stats["age_from_v1"] += 1
            else:
                v["age_marks_raw"] = None
            verses.append(v)
    stats["blocks_total"] = n
    return verses, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="thiet-ban-than-so")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    # backup v1 trước khi đè
    v1 = load_v1(args.corpus)
    bak = PROJECT_ROOT / "data" / f"tabular_verses_v1_{args.corpus}.json"
    if not bak.exists():
        bak.write_text(json.dumps(v1, ensure_ascii=False))
        print(f"v1 backed up → {bak} ({len(v1)} seq)")

    book_dir = PROJECT_ROOT / "data" / "yi_publishing_mineru" / BOOK_ID
    zh2vi = build_zh2vi(next(book_dir.rglob("*_middle.json")),
                        PROJECT_ROOT / "data" / "yi_publishing" / "translations" / BOOK_ID)
    print(f"zh2vi keys: {len(zh2vi)} | v1 seq: {len(v1)}")

    verses, stats = parse_qwenvl(zh2vi, v1)
    seqs = [v["seq_no"] for v in verses if v.get("seq_no")]
    from collections import Counter
    dup = [k for k, c in Counter(seqs).items() if c > 1]
    print(f"verses: {len(verses)} | seq range: {min(seqs)}..{max(seqs)}")
    for conf in ("anchored", "interpolated", "uncertain"):
        print(f"  {conf:13s}: {sum(1 for v in verses if v['seq_confidence'] == conf)}")
    print(f"  with VI      : {sum(1 for v in verses if v.get('vi'))}")
    print(f"  with age     : {sum(1 for v in verses if v.get('age_marks_raw'))}")
    print(f"  duplicate seq: {len(dup)}{' vd ' + str(dup[:6]) if dup else ''}")
    print(f"stats: {stats}")
    print("--- samples ---")
    for v in verses[:2] + verses[len(verses)//2:len(verses)//2+2] + verses[-2:]:
        print(f"  #{v.get('seq_no')} [{v['seq_confidence']}] {v.get('volume')} p{v['page_pdf']}"
              f"\n    ZH: {v['zh'][:55]}\n    VI: {(v.get('vi') or '')[:70]}")

    if args.commit:
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(SCHEMA_PATH.read_text())
        conn.execute("DELETE FROM tabular_verses WHERE book_corpus_id=?", (args.corpus,))
        conn.executemany(
            """INSERT INTO tabular_verses
               (book_corpus_id, volume, seq_no, seq_in_block, seq_confidence,
                age_marks_raw, zh, vi, page_pdf, line_ref, note)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            [(args.corpus, v.get("volume"), v.get("seq_no"), v.get("seq_in_block"),
              v.get("seq_confidence", "uncertain"), v.get("age_marks_raw"),
              v.get("zh", ""), v.get("vi"), v.get("page_pdf"),
              v.get("line_ref"), v.get("note")) for v in verses])
        conn.commit()
        nn = conn.execute("SELECT COUNT(*) FROM tabular_verses WHERE book_corpus_id=?",
                          (args.corpus,)).fetchone()[0]
        conn.close()
        print(f"\n✅ committed {nn} verses (v3 qwen-VL)")
    else:
        print("\n(dry-run — thêm --commit để ghi)")


if __name__ == "__main__":
    main()
