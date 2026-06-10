"""Tabular Ingest v2 — parse điều văn Thiết Bản từ MinerU *model.json* (lớp RAW).

Vì sao model.json: bước model→middle của MinerU có bug GỘP nội dung các trang
dạng 'index' (điều văn) vào 1 page entry (76 trang dồn, xác minh 2026-06-10 qua
3 lần OCR: swarm-merge / 1-process JBIG2 / 1-process JPEG đều dính ở middle.json,
còn model.json per-page LUÔN SẠCH).

Cấu trúc hình học 1 trang điều văn (ảnh ~1654×2436, đo trên model.json):
    x/W < 0.16   → cột ANCHOR (số tuyệt đối, nhô lề trái, dòng 十 cuối block)
    x/W < 0.215  → cột SỐ ĐIỀU trong block (一..九, 十)
    x/W < 0.295  → cột TUỔI ỨNG (1-2 số nhỏ, optional)
    x/W ≥ 0.295  → cột VĂN ĐOÁN
Hàng ghép theo y-center (line-height ~65px, tolerance 18px). Dòng wrap = hàng
chỉ có văn → nối điều trước. Block tách bằng dòng 十/anchor + sequence-reset.

Số tuyệt đối: anchor mỗi block (一〇一〇十=1010; OCR rụng 〇 cuối → ×10 fix),
lọc nhiễu LIS toàn sách, nội suy block giữa 2 mốc tin cậy (kiểm khoảng cách).

VI: map từ translations cũ theo norm-ZH (key đã bỏ số đầu dòng), strip tiền tố
số-từ ("Hai:") khi khớp đúng seq_in_block.

Usage:
    python3 -m engine.atomization.tabular_ingest_model \
        --model-json <path model.json> \
        --old-middle <path middle.json cũ> --old-trans <translations dir> \
        --corpus thiet-ban-than-so [--commit]
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

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema_tabular.sql"

CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
            "八": 8, "九": 9, "〇": 0, "○": 0, "O": 0, "0": 0}
OCR_FIX = str.maketrans({"-": "一", "—": "一", "=": "二", "+": "十",
                         "0": "〇", "O": "〇", "○": "〇", "o": "〇", "t": "十",
                         "1": "一", "l": "一", "|": "一", "I": "一"})
UNIT_MAP = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
# OCR vỡ nét: 二 → "11"/"ll", 三 → "111" (đếm gạch). Map TRƯỚC translate.
STROKE_FIX = {"11": "二", "ll": "二", "||": "二", "II": "二", "111": "三", "lll": "三"}
RE_WS = re.compile(r"\s+")
RE_VOLUME = re.compile(r"^([子丑寅卯辰巳午未申酉戌亥乾坎艮震巽离坤兑])\s*集$")
RE_PAGE_NO = re.compile(r"^[·.\-—\s]*\d{1,4}[·.\-—\s]*$")

VI_NUM_PREFIX = {1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm",
                 6: "sáu", 7: "bảy", 8: "tám", 9: "chín", 10: "mười"}


def norm(s: str) -> str:
    return RE_WS.sub("", (s or "").strip())


def norm_numeral(s: str) -> str:
    t = norm(s)
    t = STROKE_FIX.get(t, t)
    return t.translate(OCR_FIX)


def parse_unit(s: str) -> int | None:
    return UNIT_MAP.get(norm_numeral(s))


def parse_anchor(s: str) -> int | None:
    """一〇二〇十 → 1020. OCR rụng 〇 cuối (一〇二十 → 102) → ×10 khi cần."""
    t = norm_numeral(s)
    if len(t) < 3 or not t.endswith("十"):
        return None
    digits = t[:-1]
    if any(ch not in CN_DIGIT for ch in digits):
        return None
    val = 0
    for ch in digits:
        val = val * 10 + CN_DIGIT[ch]
    if val == 0:
        return None
    if val % 10 != 0:
        val *= 10  # rụng 〇 cuối
    return val if val % 10 == 0 else None


def strip_leading_cn_num(s: str) -> str:
    return re.sub(r"^[一二三四五六七八九十〇○\s]+", "", s or "")


def _cjk_len(s: str) -> int:
    return sum(1 for ch in s if "一" <= ch <= "鿿")


# ── Build zh→vi từ middle cũ + translations cũ ─────────────────────────────

def build_zh2vi(old_middle_path: Path, old_trans_root: Path) -> dict[str, str]:
    middle = json.loads(old_middle_path.read_text())
    zh2vi: dict[str, str] = {}
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
        tdir = old_trans_root / f"p{page_num:04d}"
        if not tdir.exists():
            continue
        cache: dict[str, dict] = {}
        for ridx, block in enumerate(blocks, start=1):
            rid = f"r{ridx:03d}"
            if rid not in cache:
                tp = tdir / f"{rid}.json"
                try:
                    cache[rid] = json.loads(tp.read_text()).get("lines", {}) if tp.exists() else {}
                except Exception:
                    cache[rid] = {}
            for lidx, line in enumerate(block.get("lines", []), start=1):
                zh = "".join(s.get("content", "") for s in line.get("spans", [])).strip()
                if not zh:
                    continue
                vi = ((cache[rid].get(f"{rid}-l{lidx:03d}") or {}).get("text_vi") or "").strip()
                if not vi:
                    continue
                key = norm(strip_leading_cn_num(zh))
                if len(key) >= 4 and key not in zh2vi:
                    zh2vi[key] = vi
    return zh2vi


def map_vi(zh2vi: dict[str, str], zh: str, unit: int | None) -> str | None:
    vi = zh2vi.get(norm(zh))
    if not vi:
        return None
    # strip tiền tố số-từ đúng unit: "Hai: ..." / "Mười một," ...
    if unit:
        word = VI_NUM_PREFIX.get(unit, "")
        m = re.match(rf"^\s*{word}\b[^:,]{{0,12}}[:,]\s*", vi, flags=re.IGNORECASE)
        if m:
            vi = vi[m.end():].strip() or vi
    return vi


# ── Parse model.json ────────────────────────────────────────────────────────

def parse_model(model_path: Path, zh2vi: dict[str, str]):
    model = json.loads(model_path.read_text())
    stats = {"pages_with_verses": 0, "anchors_read": 0, "wrap_joined": 0,
             "unparsed_rows": 0, "vi_mapped": 0}
    volume = None
    blocks: list[dict] = []
    cur = {"verses": [], "anchor": None, "last_unit": 0}
    current_verse: dict | None = None

    def close_block():
        nonlocal cur
        if cur["verses"]:
            blocks.append(cur)
        cur = {"verses": [], "anchor": None, "last_unit": 0}

    for entry in model:
        page_no = (entry.get("page_info") or {}).get("page_no", 0)
        page_pdf = page_no + 2  # MinerU -s 1 bỏ trang bìa (0-based slice)
        W = (entry.get("page_info") or {}).get("width", 1654)
        items = [d for d in entry.get("layout_dets", []) if d.get("label") == "ocr_text"
                 and (d.get("text") or "").strip()]
        if not items:
            continue

        # page printed number (đáy trang) — bỏ khỏi luồng điều văn
        rows_src = []
        for d in items:
            x1, y1, x2, y2 = d["bbox"]
            t = d["text"].strip()
            if RE_PAGE_NO.match(t) and y1 > 2100:
                continue
            m = RE_VOLUME.match(norm(t))
            if m:
                volume = norm(t)
                continue
            rows_src.append((x1, (y1 + y2) / 2, t))

        # ghép hàng theo y-center — tolerance động theo cỡ chữ trang
        heights = sorted(d["bbox"][3] - d["bbox"][1] for d in items)
        med_h = heights[len(heights) // 2] if heights else 50
        y_tol = max(14, min(28, int(med_h * 0.45)))
        rows_src.sort(key=lambda r: r[1])
        rows: list[list[tuple]] = []
        for x1, yc, t in rows_src:
            if rows and abs(yc - rows[-1][0][1]) <= y_tol:
                rows[-1].append((x1, yc, t))
            else:
                rows.append([(x1, yc, t)])

        page_had = False
        for row in rows:
            row.sort(key=lambda r: r[0])
            head_t = row[0][2]

            # CONTENT-BASED (lề chẵn/lẻ sách scan lệch nhau → không tin x tuyệt đối)
            unit = parse_unit(head_t)
            anchor = parse_anchor(head_t)
            rest = row[1:]
            # anchor đôi khi OCR tách "四一一" + "十" → thử ghép 2 item đầu
            if anchor is None and unit is None and len(row) >= 2:
                joined = parse_anchor(head_t + row[1][2])
                if joined is not None:
                    anchor = joined
                    rest = row[2:]

            def is_age(t: str) -> bool:
                u = norm_numeral(t)
                return bool(u) and len(u) <= 5 and all(ch in CN_DIGIT or ch in "十百" for ch in u)

            # tuổi = prefix liên tiếp ngay sau head; gặp văn là dừng
            ages = []
            k = 0
            while k < len(rest) and is_age(rest[k][2]):
                ages.append(rest[k][2])
                k += 1
            body_parts = [t for _, _, t in rest[k:]]
            if unit is None and anchor is None:
                ages = []
                body_parts = [t for _, _, t in row]

            body = "".join(body_parts).strip()

            if anchor is not None or unit == 10:
                if body:
                    current_verse = {
                        "volume": volume, "seq_in_block": 10,
                        "age_marks_raw": " ".join(ages) or None,
                        "zh": body, "vi": map_vi(zh2vi, body, 10), "page_pdf": page_pdf,
                        "line_ref": f"model:p{page_no}", "note": None,
                    }
                    cur["verses"].append(current_verse)
                if anchor:
                    cur["anchor"] = anchor
                    stats["anchors_read"] += 1
                close_block()
                current_verse = None
                page_had = True
            elif unit is not None:
                # body có thể rỗng (văn tách hàng do y lệch) → mở điều chờ wrap nối
                if unit <= cur["last_unit"]:
                    close_block()
                cur["last_unit"] = unit
                vi = map_vi(zh2vi, body, unit) if body else None
                current_verse = {
                    "volume": volume, "seq_in_block": unit,
                    "age_marks_raw": " ".join(ages) or None,
                    "zh": body, "vi": vi, "page_pdf": page_pdf,
                    "line_ref": f"model:p{page_no}", "note": None if body else "|body-from-wrap",
                }
                cur["verses"].append(current_verse)
                page_had = True
            elif body and current_verse is not None and unit is None and anchor is None and not ages and not current_verse["zh"]:
                # văn của điều vừa mở (số ở hàng trước, văn tách hàng)
                current_verse["zh"] = body
                current_verse["vi"] = map_vi(zh2vi, body, current_verse["seq_in_block"])
                stats["wrap_joined"] += 1
            elif unit is None and anchor is None and body and 0 < cur["last_unit"] < 9 and _cjk_len(body) >= 4:
                # SỐ ĐIỀU MẤT (OCR rớt cột số) nhưng đang trong mạch block →
                # suy số ngầm = last_unit + 1. Head có thể là cụm TUỔI (age-like).
                head_is_age = norm_numeral(head_t) and all(
                    ch in CN_DIGIT or ch in "十百" for ch in norm_numeral(head_t)) and len(norm_numeral(head_t)) <= 5
                implied = cur["last_unit"] + 1
                cur["last_unit"] = implied
                impl_ages = ([head_t] + ages) if head_is_age else ages
                impl_body = body if head_is_age else (head_t + body if head_t not in impl_ages else body)
                # nếu head không phải age cũng không phải số → nó là phần văn
                if not head_is_age:
                    impl_body = "".join(t for _, _, t in row)
                    impl_ages = []
                current_verse = {
                    "volume": volume, "seq_in_block": implied,
                    "age_marks_raw": " ".join(impl_ages) or None,
                    "zh": impl_body, "vi": map_vi(zh2vi, impl_body, implied), "page_pdf": page_pdf,
                    "line_ref": f"model:p{page_no}", "note": "|unit-implied",
                }
                cur["verses"].append(current_verse)
                page_had = True
            elif body and current_verse is not None and unit is None and anchor is None and not ages:
                current_verse["zh"] += body
                extra_vi = map_vi(zh2vi, body, None)
                if extra_vi:
                    current_verse["vi"] = ((current_verse.get("vi") or "") + " " + extra_vi).strip()
                current_verse["note"] = (current_verse.get("note") or "") + "|wrap"
                stats["wrap_joined"] += 1
            else:
                stats["unparsed_rows"] += 1

        if page_had:
            stats["pages_with_verses"] += 1

    close_block()

    # ── LIS lọc anchor + nội suy (như tabular_ingest pass 2) ──────────────
    n = len(blocks)
    marks = [(i, blocks[i]["anchor"] // 10) for i in range(n) if blocks[i]["anchor"]]
    tails: list[int] = []
    tails_idx: list[int] = []
    parent = [-1] * len(marks)
    for mi, (bi, bno) in enumerate(marks):
        pos = bisect.bisect_left(tails, bno)
        if pos == len(tails):
            tails.append(bno); tails_idx.append(mi)
        else:
            tails[pos] = bno; tails_idx[pos] = mi
        parent[mi] = tails_idx[pos - 1] if pos > 0 else -1
    lis_set = set()
    if tails_idx:
        c = tails_idx[-1]
        while c != -1:
            lis_set.add(c)
            c = parent[c]
    trusted = [(bi, bno) for mi, (bi, bno) in enumerate(marks) if mi in lis_set]
    stats["anchors_trusted"] = len(trusted)
    stats["anchors_rejected"] = len(marks) - len(trusted)

    bno_of = [None] * n
    conf_of = ["uncertain"] * n
    for bi, bno in trusted:
        bno_of[bi] = bno
        conf_of[bi] = "anchored"
    for k in range(len(trusted) + 1):
        lo = trusted[k - 1] if k > 0 else None
        hi = trusted[k] if k < len(trusted) else None
        start = (lo[0] + 1) if lo else 0
        end = (hi[0] - 1) if hi else n - 1
        if start > end:
            continue
        clean = lo is not None and hi is not None and (hi[0] - lo[0]) == (hi[1] - lo[1])
        for i in range(start, end + 1):
            if lo:
                bno_of[i] = lo[1] + (i - lo[0])
            elif hi:
                bno_of[i] = hi[1] - (hi[0] - i)
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
            if v.get("vi"):
                stats["vi_mapped"] += 1
            verses.append(v)
    stats["blocks_total"] = n
    # bỏ verse rỗng văn (dòng anchor đứng riêng / số mồ côi không vớt được wrap)
    n_empty = sum(1 for v in verses if not v["zh"].strip())
    stats["empty_dropped"] = n_empty
    verses = [v for v in verses if v["zh"].strip()]
    return verses, stats


def commit(corpus: str, verses: list[dict]) -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.execute("DELETE FROM tabular_verses WHERE book_corpus_id = ?", (corpus,))
    conn.executemany(
        """INSERT INTO tabular_verses
           (book_corpus_id, volume, seq_no, seq_in_block, seq_confidence,
            age_marks_raw, zh, vi, page_pdf, line_ref, note)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        [(corpus, v.get("volume"), v.get("seq_no"), v.get("seq_in_block"),
          v.get("seq_confidence", "uncertain"), v.get("age_marks_raw"),
          v.get("zh", ""), v.get("vi"), v.get("page_pdf"),
          v.get("line_ref"), v.get("note")) for v in verses],
    )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM tabular_verses WHERE book_corpus_id=?",
                     (corpus,)).fetchone()[0]
    conn.close()
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-json", required=True)
    ap.add_argument("--old-middle", required=True)
    ap.add_argument("--old-trans", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    zh2vi = build_zh2vi(Path(args.old_middle), Path(args.old_trans))
    print(f"zh2vi keys: {len(zh2vi)}")
    verses, stats = parse_model(Path(args.model_json), zh2vi)

    seqs = [v["seq_no"] for v in verses if v.get("seq_no")]
    from collections import Counter
    dup = [k for k, c in Counter(seqs).items() if c > 1]
    print(f"verses parsed : {len(verses)}")
    print(f"seq range     : {min(seqs) if seqs else '-'} .. {max(seqs) if seqs else '-'}")
    for conf in ("anchored", "interpolated", "uncertain"):
        print(f"{conf:14s}: {sum(1 for v in verses if v['seq_confidence'] == conf)}")
    print(f"with VI       : {sum(1 for v in verses if v.get('vi'))}")
    print(f"with age marks: {sum(1 for v in verses if v.get('age_marks_raw'))}")
    print(f"duplicate seq : {len(dup)}{' vd ' + str(dup[:8]) if dup else ''}")
    print(f"stats         : {stats}")
    print("--- samples ---")
    for v in verses[:3] + verses[len(verses) // 2:len(verses) // 2 + 2] + verses[-2:]:
        print(f"  #{v.get('seq_no')} [{v['seq_confidence']}] vol={v.get('volume')} p{v['page_pdf']}"
              f" ages={v.get('age_marks_raw')!r}\n    ZH: {v['zh'][:55]}\n    VI: {(v.get('vi') or '')[:75]}")

    if args.commit:
        print(f"\n✅ committed {commit(args.corpus, verses)} verses")
    else:
        print("\n(dry-run — thêm --commit để ghi DB)")


if __name__ == "__main__":
    main()
