"""Cách cục dictionary — load 545 cách kinh điển từ thâm nhuần Q1.

Nguồn: `data/yi_publishing/q1_tuvi/master/cach_cuc_index.json`
Build từ Phú Thái Vi (Quyển 1 — Tử Vi Đẩu Số Toàn Thư của Trần Đoàn).

⚠️ ĐỌC THỜI-THẾ-AWARE (Đằng Sơn, Tử Vi Hoàn Toàn Khoa Học Tập 1 Ch.7, đọc 2026-06-23):
   Nhiều cách cục MANG THỜI-THẾ PHONG KIẾN trong lời phán → KHÔNG còn đúng literal.
   VD kinh điển: "Tử Phá mộ cung (Sửu/Mùi) bất trung bất hiếu" = phán thời quân chủ
   chuyên chế (tam cương ngũ thường ép cứng → ai nghịch truyền thống = phản loạn). NAY
   Tử Phá = khuynh hướng đi-ngược-xã-hội: xã hội ổn định→khó đắc ý, hỗn loạn→dễ đắc ý.
   → Cách phán ĐẠO ĐỨC phong kiến (bất trung/bất hiếu/dâm/yểu…) phải đọc theo BỐI CẢNH
   + cá-nhân-hóa (đại-thể→tiểu-thể, Iron #4/#6), KHÔNG áp thẳng làm bản án. Caller hiển
   thị cách cục NÊN kèm cờ cảnh báo này cho cách mang phán-đạo-đức.

Sử dụng:
    from engine.tu_vi.cach_cuc_dict import load_dictionary, lookup_by_name, match_cach_in_chart

    # Lookup 1 cách theo tên
    cach = lookup_by_name("Cự Nhật Đồng Cung")

    # Match cách cục trong lá số (heuristic: tìm cách có chứa các sao chính có trong chart)
    matches = match_cach_in_chart(stars_at_menh=["Thái Dương", "Cự Môn", "Lộc Tồn"])
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DICT_PATH = Path(
    "/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/q1_tuvi/master/cach_cuc_index.json"
)


@lru_cache(maxsize=1)
def load_dictionary() -> dict[str, dict]:
    """Load 545 cách cục. Lazy + cached. Returns dict[name → entry]."""
    if not DICT_PATH.exists():
        logger.warning(f"cach_cuc_dict not found at {DICT_PATH}")
        return {}
    try:
        return json.loads(DICT_PATH.read_text())
    except Exception as e:
        logger.error(f"failed to load cach_cuc_dict: {e}")
        return {}


def all_entries() -> list[dict]:
    """All entries as list, sorted by occurrences desc (most important first)."""
    d = load_dictionary()
    return sorted(d.values(), key=lambda x: x.get("occurrences", 0), reverse=True)


def lookup_by_name(name: str) -> Optional[dict]:
    """Exact or fuzzy lookup by name."""
    d = load_dictionary()
    if name in d:
        return d[name]
    # Fuzzy: case-insensitive contains
    nlow = name.lower().strip()
    for k, v in d.items():
        if nlow in k.lower() or k.lower() in nlow:
            return v
    return None


def by_level(cap_do: str) -> list[dict]:
    """Filter by cấp độ: 'thượng' | 'trung' | 'hạ' | 'phá cách' | 'tạp'."""
    d = load_dictionary()
    return [v for v in d.values() if v.get("cap_do") == cap_do]


def top_n(n: int = 20) -> list[dict]:
    """Top N cách cục theo occurrences (xuất hiện nhiều = quan trọng)."""
    return all_entries()[:n]


# ─── Match cách cục trong lá số ──────────────────────────────────────────────

# 14 chính tinh (canonical names)
CHINH_TINH = (
    "Tử Vi", "Thiên Phủ", "Thái Dương", "Thái Âm",
    "Thiên Cơ", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
    "Thất Sát", "Phá Quân",
)

# Sao phụ + sát quan trọng được Phú Thái Vi đề cập nhiều
PHU_SAT_TINH = (
    "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc",
    "Thiên Khôi", "Thiên Việt",
    "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh",
    "Địa Không", "Địa Kiếp", "Lộc Tồn", "Thiên Mã",
)

HOA = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")

ALL_STARS = CHINH_TINH + PHU_SAT_TINH + HOA


def _normalize(s: str) -> str:
    return (s or "").lower().strip()


def _stars_mentioned_in(text: str) -> set[str]:
    """Find which canonical stars appear in `text` (case-insensitive substring)."""
    tlow = _normalize(text)
    return {st for st in ALL_STARS if _normalize(st) in tlow}


def match_cach_in_chart(
    *,
    stars_at_menh: list[str],
    stars_in_palaces: Optional[dict[str, list[str]]] = None,
    min_overlap: int = 2,
    max_results: int = 30,
) -> list[dict]:
    """Match cách cục có trong dictionary với sao thực tế trong lá số.

    Args:
        stars_at_menh: sao tọa Mệnh (vd: ["Thái Dương", "Cự Môn", "Lộc Tồn"])
        stars_in_palaces: optional, dict {palace_name: [stars]} — dùng cho cách
            đa cung như "Nhật Nguyệt giáp Tài", "Tử Phủ Tương Hội"
        min_overlap: số sao tối thiểu trùng giữa cách-cục.bang_chung và chart
        max_results: cap số kết quả

    Returns:
        List of matched entries, sorted by (overlap count, occurrences) desc.
    """
    d = load_dictionary()
    if not d:
        return []

    chart_stars: set[str] = set(stars_at_menh or [])
    if stars_in_palaces:
        for stars in stars_in_palaces.values():
            chart_stars.update(stars)

    if not chart_stars:
        return []

    matches: list[tuple[int, int, dict]] = []
    for ten, entry in d.items():
        # Build combined text to scan: name + dieu_kien + ý nghĩa + sources.bang_chung
        text_parts = [
            ten,
            entry.get("dieu_kien", "") or "",
            entry.get("y_nghia", "") or "",
        ]
        for src in entry.get("sources", []):
            text_parts.append(src.get("bang_chung", "") or "")
        combined = " ".join(text_parts)

        mentioned = _stars_mentioned_in(combined)
        overlap = chart_stars & mentioned
        if len(overlap) >= min_overlap:
            matches.append((len(overlap), entry.get("occurrences", 0), entry))

    # Sort: high overlap first, then by occurrences (more important)
    matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [
        {**entry, "_overlap_count": ov, "_overlap_stars": sorted(chart_stars & _stars_mentioned_in(
            " ".join([entry.get("dieu_kien", ""), entry.get("y_nghia", "")] +
                     [s.get("bang_chung", "") for s in entry.get("sources", [])])))}
        for ov, occ, entry in matches[:max_results]
    ]


def stats() -> dict:
    """Quick stats về dictionary."""
    d = load_dictionary()
    if not d:
        return {"total": 0}
    from collections import Counter
    levels = Counter(v.get("cap_do", "?") for v in d.values())
    return {
        "total": len(d),
        "by_level": dict(levels),
        "top_5_occurrences": [
            {"ten": v["ten"], "cap_do": v.get("cap_do"), "occurrences": v.get("occurrences", 0)}
            for v in all_entries()[:5]
        ],
    }


# ─── CLI smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    print(json.dumps(stats(), ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        # Test lookup + match
        if sys.argv[1] == "match-founder":
            # anh founder: Mệnh Tỵ với Thái Dương + Cự Môn + Lộc Tồn
            matches = match_cach_in_chart(
                stars_at_menh=["Thái Dương", "Cự Môn", "Lộc Tồn"],
                stars_in_palaces={"Thiên Di": ["Thiên Cơ"], "Tài Bạch": ["Tử Vi", "Thất Sát"]},
            )
            print(f"\nMatched {len(matches)} cách for founder chart:")
            for m in matches[:15]:
                stars = ", ".join(m["_overlap_stars"][:5])
                print(f"  [{m.get('cap_do','?'):>8}] overlap={m['_overlap_count']} occ={m.get('occurrences',0)} | {m['ten'][:50]}")
                print(f"            stars: {stars}")
