"""Trích 条文 SẠCH từ bản 图解 (MinerU OCR) → corpus `thiet-ban-than-so-tujie`.

Nguyên lý CỐT: số 条文 LIÊN TỤC (1001..13000). Câu (verse CJK) đáng tin; số hay bị
GỘP (rowspan: "7806780778087809") hoặc OCR bỏ. → Mỗi BẢNG: lấy verse theo thứ tự,
NEO bằng số OCR đọc được, gán số theo SEGMENT giữa 2 anchor:
  - hàng có số OCR thật  → `anchored`
  - nội suy giữa 2 anchor KHỚP khoảng cách (không drift) → `counted`
  - segment DRIFT (anchor lệch số hàng) → BỎ phần trong (chỉ giữ anchor) = không bịa.
Số 条文 cũng nằm ở text-block (vd 3142 ngoài bảng) → lấp `anchored`.

Bản 图解 ≠ bản DB cũ (邵乙) ~38% → giữ corpus RIÊNG, engine ưu tiên 图解, fallback DB.
MinerU pass này chỉ phủ ~57% (table-detect sót ~88 trang 下篇) → phần còn lại chờ
re-OCR vision (bookflow Stage 5). KHÔNG bịa phần thiếu.
"""
from __future__ import annotations

import json
import re
import sqlite3

CJK = re.compile(r"[一-鿿]")
DB = "data/yi_wiki/wiki.sqlite3"
CORPUS = "thiet-ban-than-so-tujie"
B = ("data/yi_publishing_mineru/757915970-图解铁板神数/ocr/"
     "757915970-图解铁板神数")


def _split_nums(digits: str) -> list[int]:
    """Tách cụm số gộp: width 5 nếu rơi 10001-13000, ngược lại width 4."""
    for w in (4, 5):
        if len(digits) % w == 0 and len(digits) >= w:
            parts = [int(digits[i:i + w]) for i in range(0, len(digits), w)]
            if all(1001 <= p <= 13000 for p in parts):
                return parts
    return [int(digits)] if 1001 <= int(digits or 0) <= 13000 else []


def _classify(c: str):
    cc = c.replace(" ", "").replace("\n", "")
    if re.fullmatch(r"\d{4,}", cc):
        return ("num", _split_nums(cc))
    if re.fullmatch(r"[（(][\d\s]+[)）]", cc):
        return ("age", cc)
    if CJK.search(c) and len(CJK.findall(c)) >= 2:
        return ("verse", c.strip())
    return (None, None)


def _table_rows(body: str):
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        nums, age, verse = [], "", ""
        for c in cells:
            k, v = _classify(c)
            if k == "num":
                nums += v
            elif k == "age" and not age:
                age = v
            elif k == "verse" and len(v) > len(verse):
                verse = v
        rows.append({"nums": nums, "age": age, "verse": verse})
    return rows


def _assign_block(rows):
    """→ list (num, age, verse, conf). Segment có kiểm drift, không bịa."""
    seq, anchors, pending = [], {}, []
    for r in rows:
        if not r["verse"]:
            if r["nums"]:
                pending += r["nums"]
            continue
        idx = len(seq)
        seq.append((r["age"], r["verse"]))
        if r["nums"]:
            anchors[idx] = r["nums"][0]
            pending = r["nums"][1:]
        elif pending:
            anchors[idx] = pending.pop(0)
    if not seq or not anchors:
        return []
    aidx = sorted(anchors)
    out = []

    def emit(i, num, conf):
        if 1001 <= num <= 13000:
            out.append((num, seq[i][0], seq[i][1], conf))

    a0 = aidx[0]
    for i in range(a0):                       # đầu bảng: ngoại suy lùi
        emit(i, anchors[a0] - (a0 - i), "counted")
    emit(a0, anchors[a0], "anchored")
    for k in range(len(aidx) - 1):
        i, j = aidx[k], aidx[k + 1]
        if anchors[j] - anchors[i] == j - i:  # không drift → nội suy
            for t in range(i + 1, j):
                emit(t, anchors[i] + (t - i), "counted")
            emit(j, anchors[j], "anchored")
        else:                                 # drift → bỏ phần trong
            emit(j, anchors[j], "anchored")
    aL = aidx[-1]
    for i in range(aL + 1, len(seq)):         # cuối bảng: ngoại suy tiến
        emit(i, anchors[aL] + (i - aL), "counted")
    return out


_RANK = {"anchored": 2, "counted": 1}


def extract() -> dict:
    d = json.load(open(B + "_content_list.json", encoding="utf-8"))
    verses, pages = {}, {}
    n_tbl = 0
    for b in d:
        if b.get("type") != "table":
            continue
        n_tbl += 1
        pg = b.get("page_idx")
        for num, age, verse, conf in _assign_block(_table_rows(b.get("table_body", ""))):
            old = verses.get(num)
            better = (old is None or _RANK[conf] > _RANK[old[2]]
                      or (_RANK[conf] == _RANK[old[2]] and len(verse) > len(old[1])))
            if better:
                verses[num] = (age, verse, conf)
                pages[num] = pg
    # text-block 条文 (ngoài bảng) — có số rõ → anchored, chỉ lấp chỗ trống
    md = open(B + ".md", encoding="utf-8").read()
    notable = re.sub(r"<table>.*?</table>", "", md, flags=re.S)
    for m in re.finditer(r"(?<!\d)(\d{4,5})\s*[（(]?([\d\s]{0,6})[)）]?\s*"
                         r"([一-鿿，。、；！？…]{4,})", notable):
        n = int(m.group(1))
        if 1001 <= n <= 13000 and (n not in verses or verses[n][2] == "counted"):
            v = re.sub(r"\s+", "", m.group(3))
            if len(CJK.findall(v)) >= 2:
                verses[n] = (m.group(2).strip(), v, "anchored")
    return {"verses": verses, "pages": pages, "n_tables": n_tbl}


def ingest_db():
    r = extract()
    v, pages = r["verses"], r["pages"]
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM tabular_verses WHERE book_corpus_id=?", (CORPUS,))
    VOL = ["子集", "丑集", "寅集", "卯集", "辰集", "巳集",
           "午集", "未集", "申集", "酉集", "戌集", "亥集"]
    rows = []
    for n in sorted(v):
        age, zh, conf = v[n]
        vol = VOL[min((n - 1001) // 1000, 11)] if n >= 1001 else None
        rows.append((CORPUS, vol, n, conf, age or None, zh, pages.get(n), "图解-mineru"))
    con.executemany(
        "INSERT INTO tabular_verses (book_corpus_id,volume,seq_no,seq_confidence,"
        "age_marks_raw,zh,page_pdf,note) VALUES (?,?,?,?,?,?,?,?)", rows)
    con.commit()
    n_anchored = sum(1 for n in v if v[n][2] == "anchored")
    con.close()
    return {"ingested": len(rows), "anchored": n_anchored,
            "counted": len(rows) - n_anchored}


if __name__ == "__main__":
    import sys
    if "--ingest" in sys.argv:
        print("INGEST:", ingest_db())
    else:
        r = extract()
        v = r["verses"]
        anc = sum(1 for n in v if v[n][2] == "anchored")
        print(f"tables {r['n_tables']} | 条文 {len(v)}/12000 ({len(v)*100//12000}%) "
              f"| anchored {anc} counted {len(v)-anc}")
        for lo in range(1000, 13000, 1000):
            print(f"  {lo+1:>5}-{lo+1000}: {sum(1 for n in v if lo<n<=lo+1000):>4}")
        for n in (3142, 4410, 7198, 7866, 12985):
            print(f"  {n}:", v.get(n, "TRỐNG"))
