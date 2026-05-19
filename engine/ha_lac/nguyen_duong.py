"""Nguyên đường (元堂) — the "starting hall" / moving line for a Hà Lạc hexagram.

Algorithm:
- Birth-hour branch is yang (Tý..Tỵ) or yin (Ngọ..Hợi).
- Walk the hexagram's lines bottom→top.
- Yang hour: count ONLY yang lines (1-bits in our convention). The k-th yang
  branch (Tý=1st, Sửu=2nd, ..., Tỵ=6th) determines which yang line is nguyên đường.
- Yin hour: count ONLY yin lines. Ngọ=1st yin branch, Mùi=2nd, etc.
- If the hour-rank exceeds the matching-parity line count → cycle modulo count.
- Edge: zero matching-parity lines → degenerate; flag for manual review.
"""

from __future__ import annotations

from .constants import YANG_BRANCHES, YIN_BRANCHES


def hour_branch_rank(hour_branch: str) -> tuple[int, bool]:
    """Return (rank 1..6, is_yang_hour) for a given hour branch."""
    if hour_branch in YANG_BRANCHES:
        return YANG_BRANCHES.index(hour_branch) + 1, True
    if hour_branch in YIN_BRANCHES:
        return YIN_BRANCHES.index(hour_branch) + 1, False
    raise ValueError(f"Unknown hour branch: {hour_branch!r}")


def nguyen_duong_line(binary_top_down: str, hour_branch: str) -> tuple[int, list[str]]:
    """Determine the moving line (1..6, bottom-up) for a hexagram + birth hour.

    Returns (line_position, notes) where line_position is 1-indexed bottom-up.
    If zero matching-parity lines, returns (1, [note]) as a defensive fallback.

    v2 (2026-05-12, critique #6): `notes` always includes a `rationale` line
    explaining WHY this line was chosen — for sage diễn giải.
    """
    notes: list[str] = []
    rank, is_yang_hour = hour_branch_rank(hour_branch)

    line_bits = [(6 - i, binary_top_down[i]) for i in range(6)]
    line_bits.sort()

    if is_yang_hour:
        matching = [pos for pos, bit in line_bits if bit == "1"]
    else:
        matching = [pos for pos, bit in line_bits if bit == "0"]

    if not matching:
        notes.append(
            f"rationale: Giờ {hour_branch} là giờ "
            f"{'DƯƠNG (rank ' + str(rank) + ' trong Tý-Sửu-Dần-Mão-Thìn-Tỵ)' if is_yang_hour else 'ÂM (rank ' + str(rank) + ' trong Ngọ-Mùi-Thân-Dậu-Tuất-Hợi)'} "
            f"nhưng quẻ {binary_top_down} không có hào cùng tính → suy biến, dùng hào 1 dự phòng."
        )
        return 1, notes

    idx = (rank - 1) % len(matching)
    selected = matching[idx]

    # Always emit a rationale (critique #6)
    parity_vi = "dương (cương)" if is_yang_hour else "âm (nhu)"
    bs = "Tý-Sửu-Dần-Mão-Thìn-Tỵ" if is_yang_hour else "Ngọ-Mùi-Thân-Dậu-Tuất-Hợi"
    notes.append(
        f"rationale: Giờ sinh {hour_branch} là giờ {parity_vi}, "
        f"hạng {rank} trong nhóm 6 giờ cùng tính ({bs}). "
        f"Quẻ {binary_top_down} có {len(matching)} hào {'dương' if is_yang_hour else 'âm'} "
        f"tại vị trí {matching} (đếm bottom-up). "
        f"Đối chiếu rank {rank} (mod {len(matching)} = {idx + 1}) → "
        f"nguyên đường = hào {selected}."
    )

    if rank > len(matching):
        notes.append(
            f"Lưu ý: hour rank {rank} vượt số hào cùng tính ({len(matching)}) — "
            f"quay vòng modulo, chọn hào thứ {idx + 1} trong danh sách."
        )
    return selected, notes
