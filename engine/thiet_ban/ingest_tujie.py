"""Trích 13000 条文 SẠCH từ bản 图解 (MinerU OCR) → corpus thiet-ban-than-so-tujie.

Nguyên lý CỐT: số 条文 LIÊN TỤC (1001..13000). Câu (verse CJK) là phần đáng tin của OCR;
số hay bị GỘP (rowspan: "7806780778087809") hoặc lệch. → Mỗi BẢNG: lấy verse theo thứ tự,
NEO bằng số OCR sạch đầu tiên, gán số liên tiếp, VALIDATE bằng các số neo khác trong bảng.
Số 条文 ở cả table-block lẫn text-block (vd 3142 nằm text). Cảnh báo bảng anchor mâu thuẫn.

KHÔNG bịa: bảng nào anchor mâu thuẫn / không có verse → bỏ + log. Verse giữ NGUYÊN OCR
(cleanup tiếng Hán để pass LLM local sau — bookflow Stage 4.1).
"""
from __future__ import annotations

import json
import re

CJK = re.compile(r"[一-鿿]")
B = ("data/yi_publishing_mineru/757915970-图解铁板神数/ocr/"
     "757915970-图解铁板神数")


def _split_nums(digits: str, width: int) -> list[int]:
    """Tách cụm số gộp theo độ rộng (4 cho <10000, 5 cho 10001-13000)."""
    if len(digits) % width != 0:
        return []
    out = [int(digits[i:i + width]) for i in range(0, len(digits), width)]
    return out


def _classify_cell(c: str):
    """→ ('num', [ints]) | ('age', str) | ('verse', str) | (None, None)."""
    cc = c.replace(" ", "").replace("\n", "")
    if re.fullmatch(r"\d{4,}", cc):
        width = 5 if (len(cc) % 5 == 0 and 10001 <= int(cc[:5]) <= 13000) else 4
        nums = _split_nums(cc, width)
        if not nums and len(cc) in (4, 5):
            nums = [int(cc)]
        return ("num", nums)
    if re.fullmatch(r"[（(][\d\s]+[)）]", cc):
        return ("age", cc)
    if CJK.search(c) and len(CJK.findall(c)) >= 2:
        return ("verse", c.strip())
    return (None, None)


def _table_rows(body: str):
    """Mỗi <tr> → {nums:[...], age, verse}. nums có thể nhiều (ô gộp rowspan)."""
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        nums, age, verse = [], "", ""
        for c in cells:
            kind, val = _classify_cell(c)
            if kind == "num":
                nums += val
            elif kind == "age" and not age:
                age = val
            elif kind == "verse" and len(val) > len(verse):
                verse = val
        rows.append({"nums": nums, "age": age, "verse": verse})
    return rows


def _assign_block(rows: list[dict]) -> tuple[dict, list[str]]:
    """Gán số liên tiếp cho verse-rows trong 1 bảng, NEO bằng số OCR.

    rows theo thứ tự đọc. Ô số gộp (rowspan: nhiều num) = neo hàng hiện tại + hàng kế.
    Thuật toán: neo offset từ số sạch ĐẦU; đi dọc; mỗi anchor KHỚP-gần (≤30) thì
    cập nhật offset (hút theo OCR, chịu drift do verse bị bỏ); anchor lệch THÔ (OCR
    sai) thì BỎ anchor đó, KHÔNG vứt cả bảng. Trả {num: (age, verse)} + cảnh báo.
    """
    seq = []                 # [{age, verse}]
    anchors = {}             # idx_in_seq -> num
    pending = []             # số dư từ ô gộp → hàng verse kế
    for r in rows:
        if not r["verse"]:
            if r["nums"]:
                pending += r["nums"]
            continue
        idx = len(seq)
        seq.append({"age": r["age"], "verse": r["verse"]})
        if r["nums"]:
            anchors[idx] = r["nums"][0]
            pending = r["nums"][1:]
        elif pending:
            anchors[idx] = pending.pop(0)
    if not seq or not anchors:
        return {}, ["no-anchor-or-verse"]

    out, warns, skip = {}, [], 0
    last = None                                  # số gán gần nhất (kiểm đơn điệu)
    for idx, item in enumerate(seq):
        if idx not in anchors:                   # KHÔNG nội suy → bỏ (để text-block lấp)
            skip += 1
            continue
        n = anchors[idx]
        if last is not None and not (-2 <= n - last <= 30):
            skip += 1                            # số lệch thô đơn điệu = OCR sai → bỏ
            continue
        last = n
        if 1001 <= n <= 13000:
            if n not in out or len(item["verse"]) > len(out[n][1]):
                out[n] = (item["age"], item["verse"])
    if skip:
        warns.append(f"bỏ {skip} hàng không-số/lệch")
    return out, warns


def extract() -> dict:
    d = json.load(open(B + "_content_list.json", encoding="utf-8"))
    verses, all_warns = {}, []
    n_tbl = 0
    for b in d:
        if b.get("type") != "table":
            continue
        n_tbl += 1
        got, warns = _assign_block(_table_rows(b.get("table_body", "")))
        for n, av in got.items():
            # giữ verse dài hơn nếu trùng (OCR tốt hơn)
            if n not in verses or len(av[1]) > len(verses[n][1]):
                verses[n] = av
        if warns:
            all_warns.append((b.get("page_idx"), warns))
    # text-block 条文 (vd 3142（43）水尽山穷...)
    md = open(B + ".md", encoding="utf-8").read()
    for m in re.finditer(r"(?<!\d)(\d{4,5})\s*[（(]?([\d\s]{0,6})[)）]?\s*"
                         r"([一-鿿，。、；！？…\s]{4,})", md):
        n = int(m.group(1))
        if 1001 <= n <= 13000 and n not in verses:
            v = re.sub(r"\s+", "", m.group(3))
            if len(CJK.findall(v)) >= 2:
                verses[n] = (m.group(2).strip(), v)
    return {"verses": verses, "n_tables": n_tbl, "warns": all_warns}


if __name__ == "__main__":
    r = extract()
    v = r["verses"]
    print(f"tables: {r['n_tables']} | 条文 trích: {len(v)} / 12000 "
          f"({len(v) * 100 // 12000}%)")
    for lo in range(1000, 13000, 1000):
        c = sum(1 for n in v if lo < n <= lo + 1000)
        print(f"  {lo + 1:>5}-{lo + 1000}: {c:>4}")
    print("cảnh báo bảng:", len(r["warns"]))
    print("--- cặp kiểm 图解 ---")
    for n in (3142, 4410, 7866, 12985, 1063):
        print(f"  {n}:", v.get(n, "TRỐNG"))
