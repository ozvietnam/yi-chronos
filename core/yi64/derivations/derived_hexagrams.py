"""Derived hexagram computations.

Given a primary hexagram binary code (top-down: binary[0]=line6, binary[5]=line1),
compute the 5 standard derived charts read in Mai Hoa Dịch Số and related schools.

References:
- 互卦 (Hỗ / Nuclear): formed from lines 5,4,3 (upper) and 4,3,2 (lower).
  Source: Thiệu Khang Tiết, Mai Hoa Dịch Số Toàn Tập, "Hỗ quái pháp".
- 變卦 (Biến / Transformed): flip moving lines.
  Source: Chu Hi, Chu Dịch Bản Nghĩa.
- 錯卦 (Giao / Thác / Opposing): flip every line yin↔yang.
  Source: Lại Tri Đức, Lai Trị Đức Tử Quán Vật Ngoại Thiên.
- 綜卦 (Phục / Tổng / Reversed): reverse line order vertically (line 1 ↔ line 6, etc.).
  Source: Trình Di, Y Xuyên Dịch Truyện.
- 包卦 (Bao / Envelope): chart of the outermost frame — line 6 triplicated as upper,
  line 1 triplicated as lower. Project convention; documented for reproducibility.
"""

from __future__ import annotations

from core.hexagram import flip_line, get_hexagram_by_binary

from ..model import HexagramIdentity
from ..transforms import binary_to_hexagram_identity


def compute_nuclear(primary_binary: str) -> str:
    """Hỗ quái — nuclear hexagram from middle 4 lines."""
    # Top-down indices: 0..5 == lines 6..1.
    # Upper of nuclear = lines 5,4,3 (indices 1,2,3).
    # Lower of nuclear = lines 4,3,2 (indices 2,3,4).
    return (
        primary_binary[1] + primary_binary[2] + primary_binary[3]
        + primary_binary[2] + primary_binary[3] + primary_binary[4]
    )


def compute_transformed(primary_binary: str, moving_lines: tuple[int, ...]) -> str:
    """Biến quái — flip every moving line."""
    out = primary_binary
    for line in sorted(set(moving_lines)):
        out = flip_line(out, line)
    return out


def compute_opposing(primary_binary: str) -> str:
    """Giao/Thác quái (錯卦) — flip every line yin↔yang."""
    return "".join("1" if c == "0" else "0" for c in primary_binary)


def compute_reversed(primary_binary: str) -> str:
    """Phục/Tổng quái (綜卦) — reverse line order vertically.

    Original line 1 (bottom) becomes new line 6 (top), etc.
    In top-down representation this is just the string reversed.
    """
    return primary_binary[::-1]


def compute_envelope(primary_binary: str) -> str:
    """Bao quái (包卦) — line 6 triplicated as upper, line 1 triplicated as lower.

    Captures the "outermost frame" view: only the topmost and bottommost
    lines of the original determine the envelope.
    """
    top = primary_binary[0]
    bottom = primary_binary[5]
    return top * 3 + bottom * 3


def compute_all_derived(
    primary_binary: str,
    moving_lines: tuple[int, ...] = (),
) -> dict[str, HexagramIdentity]:
    """Compute the full set of 5 derived hexagrams plus the primary identity.

    Returns a dict with keys: chanh, ho, bien, giao, phuc, bao.
    """
    primary = binary_to_hexagram_identity(primary_binary)
    nuclear = binary_to_hexagram_identity(compute_nuclear(primary_binary))
    transformed = (
        binary_to_hexagram_identity(compute_transformed(primary_binary, moving_lines))
        if moving_lines
        else primary
    )
    opposing = binary_to_hexagram_identity(compute_opposing(primary_binary))
    reversed_h = binary_to_hexagram_identity(compute_reversed(primary_binary))
    envelope = binary_to_hexagram_identity(compute_envelope(primary_binary))
    return {
        "chanh": primary,
        "ho": nuclear,
        "bien": transformed,
        "giao": opposing,
        "phuc": reversed_h,
        "bao": envelope,
    }


def derived_summary_dict(
    primary_binary: str,
    moving_lines: tuple[int, ...] = (),
) -> dict:
    """Return a JSON-serializable summary of all 5 derived charts."""
    derived = compute_all_derived(primary_binary, moving_lines)
    return {
        key: {
            "king_wen_index": h.king_wen_index,
            "binary": h.binary_code,
            "name_vi": h.name_vi,
            "upper_trigram": h.upper_trigram,
            "lower_trigram": h.lower_trigram,
        }
        for key, h in derived.items()
    }
