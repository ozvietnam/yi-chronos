"""Tabular Ingest — parse điều văn sách tra số (Thiết Bản Thần Số) → tabular_verses.

Cấu trúc trang điều văn (xác minh trên scan p107/p159, 2026-06-10):
- Điều văn nhóm BLOCK 10 điều, cột trái = số trong block (一..九, dòng 10 = anchor).
- Dòng anchor ghi SỐ TUYỆT ĐỐI đầy đủ kết thúc bằng 十 (vd 一〇一〇十 = điều 1010,
  二三二〇十 = 2320). OCR hay vỡ anchor thành '-0=○+' → normalize trước khi đọc.
- Cột số nhỏ giữa = tuổi ứng nghiệm (optional, 1-2 số) → giữ NGUYÊN VĂN (age_marks_raw).
- Lời đoán có thể wrap sang dòng không số → nối vào điều trước.
- Số tuyệt đối suy bằng ĐẾM TÍCH LŨY, anchor dùng để RECALIBRATE + đánh dấu confidence.

Usage:
    python3 -m engine.atomization.tabular_ingest --book-id <yi_publishing book_id> \
        --corpus thiet-ban-than-so [--pages 105-470] [--dry-run] [--commit]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
MINERU_ROOT = PROJECT_ROOT / "data" / "yi_publishing_mineru"
TRANS_ROOT = PROJECT_ROOT / "data" / "yi_publishing" / "translations"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema_tabular.sql"

# ── Số Trung Hoa + OCR noise normalize ──────────────────────────────────────
CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
            "八": 8, "九": 9, "〇": 0, "○": 0, "O": 0, "0": 0}
# OCR hay vỡ: 一→'-', 二→'=', 十→'+', 〇→'0'/'○'/'O'
OCR_FIX = str.maketrans({"-": "一", "=": "二", "+": "十", "0": "〇", "O": "〇", "○": "〇"})

UNIT_MAP = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

RE_AGE_MARK = re.compile(r"^[一二三四五六七八九十百〇○O0\s]+$")


def normalize_numeral(s: str) -> str:
    return s.strip().translate(OCR_FIX)


def parse_unit(s: str) -> int | None:
    """Số đơn trong block: 一..九 → 1..9, 十 → 10."""
    s = normalize_numeral(s)
    return UNIT_MAP.get(s)


def parse_anchor(s: str) -> int | None:
    """Anchor số tuyệt đối: chuỗi digit kết thúc 十, vd 一〇二〇十 → 1020.

    Đọc theo POSITIONAL digits (mỗi ký tự 1 chữ số), bỏ 十 cuối.
    Trả None nếu không đủ tin cậy (≥3 digit + kết thúc 十).
    """
    s = normalize_numeral(s).replace(" ", "")
    if len(s) < 4 or not s.endswith("十"):
        return None
    digits = s[:-1]
    if any(ch not in CN_DIGIT for ch in digits):
        return None
    if len(digits) < 3:  # số tuyệt đối thật luôn ≥ 3 chữ số (block ≥ 100... thận trọng)
        return None
    val = 0
    for ch in digits:
        val = val * 10 + CN_DIGIT[ch]
    return val if val % 10 == 0 else None  # anchor luôn là bội của 10


RE_VOLUME = re.compile(r"^([子丑寅卯辰巳午未申酉戌亥乾坎艮震巽离坤兑])\s*集$")


def load_translations(book_id: str, page_num: int) -> dict[str, str]:
    """{line_id: text_vi} cho 1 trang."""
    out: dict[str, str] = {}
    tdir = TRANS_ROOT / book_id / f"p{page_num:04d}"
    if not tdir.exists():
        return out
    for rf in sorted(tdir.glob("r*.json")):
        try:
            data = json.loads(rf.read_text())
        except Exception:
            continue
        for line_id, entry in (data.get("lines") or {}).items():
            vi = (entry.get("text_vi") or "").strip()
            if vi:
                out[line_id] = vi
    return out


def iter_page_blocks(page: dict):
    """Yield (region_idx, block) với patch lines_deleted như api page_layout."""
    blocks = page.get("para_blocks", page.get("preproc_blocks", []))
    preproc = page.get("preproc_blocks") or []
    for b in blocks:
        if not b.get("lines") and b.get("lines_deleted"):
            for pb in preproc:
                if pb.get("bbox") == b.get("bbox") or pb.get("index") == b.get("index"):
                    if pb.get("lines"):
                        b["lines"] = pb["lines"]
                        break
    for ridx, b in enumerate(blocks, start=1):
        yield ridx, b


def parse_book(book_id: str, corpus: str, page_range: tuple[int, int] | None):
    """Parse điều văn → list verse dicts + stats.

    Chiến lược số: BLOCK-ANCHOR + INTERPOLATION (không đếm tích lũy toàn sách).
    - Pass 1: gom blocks-of-10; mỗi block giữ anchor đọc được (nếu có).
    - Pass 2: block có anchor → seq = anchor - 10 + seq_in_block ('anchored').
      Block không anchor → nội suy block-index từ 2 block có anchor gần nhất
      (số block liên tục: anchor/10 tăng 1 mỗi block) → 'interpolated';
      hai phía cho đáp án khác nhau hoặc không có mốc → 'uncertain'.
    """
    mid_path = next((MINERU_ROOT / book_id).rglob("*_middle.json"))
    middle = json.loads(mid_path.read_text())
    pdf_info = middle["pdf_info"]

    stats = {"anchors_read": 0, "wrap_joined": 0,
             "unparsed_lines": 0, "pages_with_verses": 0}
    volume = None
    current: dict | None = None
    blocks: list[dict] = []          # {verses: [...], anchor: int|None}
    cur_block: dict = {"verses": [], "anchor": None, "last_unit": 0}

    def close_block():
        nonlocal cur_block
        if cur_block["verses"]:
            blocks.append(cur_block)
        cur_block = {"verses": [], "anchor": None, "last_unit": 0}

    rng = range(len(pdf_info)) if not page_range else range(page_range[0] - 1, min(page_range[1], len(pdf_info)))
    for pidx in rng:
        page_num = pidx + 1
        page = pdf_info[pidx]
        vi_map = load_translations(book_id, page_num)
        page_had = False

        for ridx, block in iter_page_blocks(page):
            btype = block.get("type")
            if btype == "title":
                t = "".join(s.get("content", "") for ln in block.get("lines", [])
                            for s in ln.get("spans", [])).strip()
                if RE_VOLUME.match(t.replace(" ", "")):
                    volume = t.replace(" ", "")
                continue
            if btype != "index":
                continue

            for lidx, line in enumerate(block.get("lines", []), start=1):
                spans = [s.get("content", "").strip() for s in line.get("spans", [])
                         if (s.get("content") or "").strip()]
                if not spans:
                    continue
                line_id = f"r{ridx:03d}-l{lidx:03d}"
                vi = vi_map.get(line_id)

                head = spans[0]
                unit = parse_unit(head)
                anchor = parse_anchor(head)

                if anchor is not None or unit == 10:
                    # dòng 十 — kết block (anchor có thể unreadable)
                    body = spans[-1] if len(spans) >= 2 else ""
                    ages = spans[1:-1]
                    current = {
                        "volume": volume, "seq_in_block": 10,
                        "age_marks_raw": " ".join(ages) or None,
                        "zh": body, "vi": vi, "page_pdf": page_num,
                        "line_ref": f"p{page_num:04d}:{line_id}", "note": None,
                    }
                    cur_block["verses"].append(current)
                    if anchor is not None:
                        cur_block["anchor"] = anchor
                        stats["anchors_read"] += 1
                    close_block()
                    current = None
                    page_had = True
                elif unit is not None and len(spans) >= 2:
                    # SEQUENCE-RESET: unit quay đầu (vd đang 五 gặp 一) nghĩa là
                    # dòng 十/anchor của block trước bị OCR vỡ và mất —
                    # block mới đã bắt đầu, tách tại đây.
                    if unit <= cur_block["last_unit"]:
                        close_block()
                    cur_block["last_unit"] = unit
                    body = spans[-1]
                    ages = spans[1:-1]
                    current = {
                        "volume": volume, "seq_in_block": unit,
                        "age_marks_raw": " ".join(ages) or None,
                        "zh": body, "vi": vi, "page_pdf": page_num,
                        "line_ref": f"p{page_num:04d}:{line_id}", "note": None,
                    }
                    cur_block["verses"].append(current)
                    page_had = True
                elif current is not None and len(spans) == 1:
                    # wrap line — CHỈ nhận dòng thuần văn (1 span, không cột số).
                    # Dòng nhiều spans mà head vỡ = nghi điều mới hỏng số → unparsed,
                    # không nối bậy vào điều trước.
                    current["zh"] += spans[-1]
                    if vi:
                        current["vi"] = ((current.get("vi") or "") + " " + vi).strip()
                    current["note"] = (current.get("note") or "") + "|wrap"
                    stats["wrap_joined"] += 1
                else:
                    stats["unparsed_lines"] += 1

        if page_had:
            stats["pages_with_verses"] += 1

    close_block()

    # ── Pass 2: gán số — LIS-filter anchors + interpolation kiểm khoảng cách ──
    # Tính chất sách: block number (anchor/10) TĂNG DẦN qua các block.
    # OCR có thể đọc SAI SỐ anchor (一三〇〇 → 一二〇〇) → lọc nhiễu bằng
    # Longest Increasing Subsequence trên (block_idx, block_no); anchor ngoài
    # LIS bị coi là misread. Block giữa 2 anchor tin cậy: nếu số-block-đếm-được
    # khớp khoảng-cách-số → 'interpolated', lệch → 'uncertain' (vẫn gán ước lượng).
    n = len(blocks)
    marks = [(i, blocks[i]["anchor"] // 10) for i in range(n) if blocks[i]["anchor"]]

    # LIS (strictly increasing theo block_no, giữ thứ tự block_idx)
    import bisect
    tails: list[int] = []          # tails[k] = block_no nhỏ nhất kết thúc LIS dài k+1
    tails_idx: list[int] = []      # index trong marks
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
        cur = tails_idx[-1]
        while cur != -1:
            lis_set.add(cur)
            cur = parent[cur]
    trusted = [(bi, bno) for mi, (bi, bno) in enumerate(marks) if mi in lis_set]
    stats["anchors_trusted"] = len(trusted)
    stats["anchors_rejected"] = len(marks) - len(trusted)

    # Gán block_no: trusted anchors là mốc; đoạn giữa nội suy.
    bno_of = [None] * n
    conf_of = ["uncertain"] * n
    for bi, bno in trusted:
        bno_of[bi] = bno
        conf_of[bi] = "anchored"
    # đoạn giữa các mốc (và 2 đầu mút)
    mark_pos = [bi for bi, _ in trusted]
    for k in range(len(trusted) + 1):
        lo = trusted[k - 1] if k > 0 else None          # (bi, bno) trái
        hi = trusted[k] if k < len(trusted) else None   # (bi, bno) phải
        start = (lo[0] + 1) if lo else 0
        end = (hi[0] - 1) if hi else n - 1
        if start > end:
            continue
        gap_blocks = (hi[0] - lo[0]) if (lo and hi) else None
        gap_nums = (hi[1] - lo[1]) if (lo and hi) else None
        clean = lo is not None and hi is not None and gap_blocks == gap_nums
        for i in range(start, end + 1):
            if lo:
                bno_of[i] = lo[1] + (i - lo[0])
            elif hi:
                bno_of[i] = hi[1] - (hi[0] - i)
            conf_of[i] = "interpolated" if clean else "uncertain"

    verses: list[dict] = []
    for i, b in enumerate(blocks):
        bno = bno_of[i]
        seen_units: set[int] = set()
        for v in b["verses"]:
            u = v["seq_in_block"]
            v["seq_no"] = (bno - 1) * 10 + u if bno else None
            v["seq_confidence"] = conf_of[i]
            if u in seen_units:  # 2 dòng cùng unit trong 1 block — OCR nhiễu
                v["seq_confidence"] = "uncertain"
                v["note"] = (v.get("note") or "") + "|dup-unit"
            seen_units.add(u)
            verses.append(v)

    stats["blocks_total"] = n
    stats["blocks_interpolated"] = sum(1 for c in conf_of if c == "interpolated")
    stats["blocks_uncertain"] = sum(1 for c in conf_of if c == "uncertain")
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
          v.get("seq_confidence", "counted"), v.get("age_marks_raw"),
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
    ap.add_argument("--book-id", required=True, help="yi_publishing book_id (mineru/translations)")
    ap.add_argument("--corpus", required=True, help="corpus id ghi vào tabular_verses")
    ap.add_argument("--pages", help="vd 105-470 (PDF pages)")
    ap.add_argument("--commit", action="store_true", help="ghi DB (mặc định dry-run)")
    args = ap.parse_args()

    page_range = None
    if args.pages:
        a, b = args.pages.split("-")
        page_range = (int(a), int(b))

    verses, stats = parse_book(args.book_id, args.corpus, page_range)
    seqs = [v["seq_no"] for v in verses if v.get("seq_no")]
    print(f"verses parsed : {len(verses)}")
    print(f"seq range     : {min(seqs) if seqs else '-'} .. {max(seqs) if seqs else '-'}")
    print(f"anchored      : {sum(1 for v in verses if v['seq_confidence']=='anchored')}")
    print(f"counted       : {sum(1 for v in verses if v['seq_confidence']=='counted')}")
    print(f"uncertain     : {sum(1 for v in verses if v['seq_confidence']=='uncertain')}")
    print(f"with VI       : {sum(1 for v in verses if v.get('vi'))}")
    print(f"with age marks: {sum(1 for v in verses if v.get('age_marks_raw'))}")
    print(f"stats         : {stats}")
    # duplicates check
    from collections import Counter
    dup = [k for k, c in Counter(seqs).items() if c > 1]
    print(f"duplicate seq : {len(dup)}{' vd ' + str(dup[:8]) if dup else ''}")
    print("--- samples ---")
    for v in verses[:3] + verses[len(verses)//2:len(verses)//2+2] + verses[-3:]:
        print(f"  #{v.get('seq_no')} [{v['seq_confidence']}] vol={v.get('volume')} p{v['page_pdf']}"
              f" ages={v.get('age_marks_raw')!r}\n    ZH: {v['zh'][:60]}\n    VI: {(v.get('vi') or '')[:70]}")

    if args.commit:
        n = commit(args.corpus, verses)
        print(f"\n✅ committed {n} verses → tabular_verses ({args.corpus})")
    else:
        print("\n(dry-run — thêm --commit để ghi DB)")


if __name__ == "__main__":
    main()
