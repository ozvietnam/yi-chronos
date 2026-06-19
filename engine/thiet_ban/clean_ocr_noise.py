"""Lau OCR-noise 条文 bản CHUNG bằng bản PD digital sạch (repo/古籍).

DB `thiet-ban-than-so` (OCR 邵乙) có lỗi OCR chữ-giống-hình (可↔元, 月↔用, 任↔往...).
Bản PD digital (cùng lineage) sạch hơn. Script này CHỈ sửa lỗi OCR RÕ RÀNG (an toàn):
  • chỉ động verse GỐC (note NULL) — KHÔNG đụng phần vừa lấp (đã PD).
  • chỉ thay khi: cùng verse (2 ký tự ĐẦU khớp) VÀ Levenshtein ≤ 2 (khác 1-2 chữ).
  • khác nhiều (độ dài lệch / wording khác) → GIỮ NGUYÊN DB (không phải OCR-noise).
Lưu note truy nguồn + nguyên văn cũ (reversible).
"""
from __future__ import annotations

import csv
import io
import re
import sqlite3

DB = "data/yi_wiki/wiki.sqlite3"
CORPUS = "thiet-ban-than-so"
REPO_CSV = "/tmp/tbss/数据库/铁板神数-条文断词.csv"
_STRIP = lambda s: re.sub(r"[，。、；！？…\s]", "", s or "")  # noqa: E731


def _lev(a: str, b: str, cap: int = 3) -> int:
    """Levenshtein có CHẶN (early-exit khi > cap)."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        best = i
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            best = min(best, cur[-1])
        if best > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def _load_repo() -> dict:
    raw = open(REPO_CSV, "rb").read().decode("gb18030", "replace")
    return {int(r[1]): r[3].strip() for r in csv.reader(io.StringIO(raw))
            if len(r) >= 4 and r[1].strip().isdigit() and r[3].strip()}


def clean(dry_run: bool = True) -> dict:
    con = sqlite3.connect(DB)
    repo = _load_repo()
    rows = con.execute(
        f"SELECT seq_no, zh FROM tabular_verses WHERE book_corpus_id='{CORPUS}' "
        "AND zh IS NOT NULL AND zh!='' AND note IS NULL").fetchall()
    fixes, samples, kept_big = [], [], 0
    for seq, zh in rows:
        if seq not in repo:
            continue
        a, b = _STRIP(zh), _STRIP(repo[seq])
        if a == b or len(a) < 3:
            continue
        if a[:2] == b[:2] and _lev(a, b) <= 2:
            fixes.append((repo[seq], f"OCR-fix PD 2026-06-20 (cũ: {zh})", seq))
            if len(samples) < 16:
                samples.append((seq, zh, repo[seq]))
        else:
            kept_big += 1
    if not dry_run and fixes:
        con.executemany(
            f"UPDATE tabular_verses SET zh=?, note=? WHERE book_corpus_id='{CORPUS}' "
            "AND seq_no=? AND note IS NULL", fixes)
        con.commit()
    con.close()
    return {"se_fix" if dry_run else "fixed": len(fixes),
            "giu_nguyen_khac_nhieu": kept_big, "samples": samples}


if __name__ == "__main__":
    import sys
    r = clean(dry_run="--apply" not in sys.argv)
    print({k: v for k, v in r.items() if k != "samples"})
    print("--- mẫu (seq: DB cũ → repo sạch) ---")
    for seq, old, new in r["samples"]:
        print(f"  {seq}: {old}  →  {new}")
