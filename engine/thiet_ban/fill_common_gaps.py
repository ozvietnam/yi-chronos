"""Lấp lỗ 条文 bản CHUNG (邵/铁卜子 lineage) → 100% coverage 1001-13000.

DB `thiet-ban-than-so` (OCR 邵乙) có 10907 điều, thiếu ~1102. Bản CHUNG này có nhiều
nguồn 12000 điều DIGITAL công khai (古籍 PD: 古易资源网 Excel, 知乎 12000条, repo
xaminxan) — CÙNG lineage với DB (đã đối chiếu: khác chỉ do OCR lỗi 可/元 月/用...).

Script này CHỈ THÊM các seq còn THIẾU (không đụng 10907 verse cũ → không vỡ test/đọc).
Verse nguồn = 古籍 公有领域; đánh dấu note để truy nguồn. KHÔNG lấp 图解 edition (bản
khác, scan thiếu — cần scan vật lý đầy đủ, không có digital).
"""
from __future__ import annotations

import csv
import io
import sqlite3

DB = "data/yi_wiki/wiki.sqlite3"
CORPUS = "thiet-ban-than-so"
REPO_CSV = "/tmp/tbss/数据库/铁板神数-条文断词.csv"
VOL = ["子集", "丑集", "寅集", "卯集", "辰集", "巳集",
       "午集", "未集", "申集", "酉集", "戌集", "亥集"]
NOTE = "古籍 PD common-edition (lấp lỗ 2026-06-20)"


def _load_repo() -> dict:
    raw = open(REPO_CSV, "rb").read().decode("gb18030", "replace")
    out = {}
    for r in csv.reader(io.StringIO(raw)):
        if len(r) >= 4 and r[1].strip().isdigit() and r[3].strip():
            out[int(r[1])] = (r[2].strip(), r[3].strip())   # (年龄, 断词)
    return out


def fill(dry_run: bool = False) -> dict:
    con = sqlite3.connect(DB)
    have = {r[0] for r in con.execute(
        f"SELECT seq_no FROM tabular_verses WHERE book_corpus_id='{CORPUS}' "
        "AND zh IS NOT NULL AND zh!=''")}
    repo = _load_repo()
    gaps = [n for n in range(1001, 13001) if n not in have and n in repo]
    rows = []
    for n in gaps:
        age, zh = repo[n]
        vol = VOL[min((n - 1001) // 1000, 11)]
        rows.append((CORPUS, vol, n, "counted", age or None, zh, NOTE))
    if not dry_run and rows:
        con.executemany(
            "INSERT INTO tabular_verses (book_corpus_id,volume,seq_no,seq_confidence,"
            "age_marks_raw,zh,note) VALUES (?,?,?,?,?,?,?)", rows)
        con.commit()
    total = con.execute(
        f"SELECT count(*) FROM tabular_verses WHERE book_corpus_id='{CORPUS}' "
        "AND zh IS NOT NULL AND zh!=''").fetchone()[0]
    con.close()
    return {"filled": len(rows), "total_after": total,
            "coverage_pct": total * 100 // 12000}


if __name__ == "__main__":
    import sys
    print(fill(dry_run="--dry" in sys.argv))
