"""Số hoá bảng SIGNATURE 坤集 (纳卦) của Thiết Bản từ MinerU model.json.

Khác `tabular_ingest_model.py` (trang 条文 lời+số). Đây là bảng định-vị can-chi:
mỗi 集/正卦 chứa các khối 纳X卦, mỗi khối là dãy DÒNG signature (4-5 can-chi + chú
ngũ hành fuse vào). model.json per-page SẠCH (middle.json bị gộp — bug đã biết).

Phép: load model.json → mỗi trang gom text dets có toạ độ → cụm 3 CỘT theo x →
sắp theo y → phân loại HEADER (tên 卦/集/爻/宫/度/用事/行度) vs DATA (dòng signature).
GIỮ NGUYÊN OCR (không tự sửa) — faithful; cờ nghi ngờ để soát sau.

Usage: python3 -m engine.thiet_ban.koan_table_extract [--from 16] [--to 146] [--out PATH]
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_GLOB = str(PROJECT_ROOT / "data/yi_publishing_mineru/"
                 "shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk/auto/*model.json")
OUT_DEFAULT = PROJECT_ROOT / "data/restored_books/thiet-ban-than-so/koan_tables.json"

CAN = set("甲乙丙丁戊己庚辛壬癸")
CHI = set("子丑寅卯辰巳午未申酉戌亥")
NGU_HANH = set("金木水火土")
# Header = tên mục cấu trúc (kết thúc/chứa các từ này)
RE_HEADER = re.compile(r"(集$|卦$|爻$|宫$|度$|用事|行度|流度|奇用|正卦|品卦|声音)")
# OCR confusions phổ biến (CHỈ ghi chú, KHÔNG tự sửa để giữ faithful)
KNOWN_OCR = {"成": "戊?", "已": "己?", "支": "巳?", "灭": "(chú?)", "卖": "(chú?)", "灵": "(chú?)"}


def _xy(det):
    poly = det.get("poly")
    if poly and len(poly) >= 2:
        return poly[0], poly[1]
    bb = det.get("bbox")
    if bb:
        return bb[0], bb[1]
    return None


def _classify(text: str) -> str:
    t = text.strip()
    if not t:
        return "empty"
    if RE_HEADER.search(t):
        return "header"
    # data row: chủ yếu can-chi (+ ngũ hành chú), độ dài 3-7
    core = [c for c in t if c in CAN or c in CHI]
    if len(core) >= 3:
        return "data"
    if t.isdigit() or (len(t) <= 3 and any(c in NGU_HANH for c in t)):
        return "marker"
    return "other"


def _flags(text: str) -> list[str]:
    return sorted({f"{c}→{KNOWN_OCR[c]}" for c in text if c in KNOWN_OCR})


def extract(model_json: str, p_from: int, p_to: int) -> dict:
    d = json.load(open(model_json))
    pages_out = []
    for pi in range(p_from, min(p_to + 1, len(d))):
        pg = d[pi]
        dets = pg.get("layout_dets", [])
        items = []
        for det in dets:
            t = (det.get("text") or "").strip()
            xy = _xy(det)
            if t and xy:
                items.append((xy[0], xy[1], t))
        if not items:
            continue
        xs = sorted(i[0] for i in items)
        n = len(xs)
        t1, t2 = xs[n // 3], xs[2 * n // 3]
        cols = {0: [], 1: [], 2: []}
        for x, y, t in items:
            c = 0 if x <= t1 else (1 if x <= t2 else 2)
            cols[c].append((y, t))
        col_out = []
        for c in (0, 1, 2):
            lines = []
            for _, t in sorted(cols[c]):
                kind = _classify(t)
                row = {"t": t, "k": kind}
                fl = _flags(t)
                if fl:
                    row["flag"] = fl
                lines.append(row)
            col_out.append(lines)
        pages_out.append({"page_idx": pi, "columns": col_out})
    return {"source": Path(model_json).name, "page_from": p_from, "page_to": p_to,
            "pages": pages_out}


def stats(data: dict) -> dict:
    nh = nd = nf = 0
    for p in data["pages"]:
        for col in p["columns"]:
            for r in col:
                if r["k"] == "header":
                    nh += 1
                elif r["k"] == "data":
                    nd += 1
                if r.get("flag"):
                    nf += 1
    return {"pages": len(data["pages"]), "headers": nh, "data_rows": nd, "flagged": nf}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="p_from", type=int, default=16)
    ap.add_argument("--to", dest="p_to", type=int, default=146)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    a = ap.parse_args()
    mj = glob.glob(MODEL_GLOB)[0]
    data = extract(mj, a.p_from, a.p_to)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(a.out, "w"), ensure_ascii=False, indent=1)
    s = stats(data)
    print(f"Extracted {s['pages']} pages · {s['headers']} headers · "
          f"{s['data_rows']} data rows · {s['flagged']} flagged → {a.out}")
