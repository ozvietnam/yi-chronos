"""Generate 64 SVG hexagram images for /que-images/01.svg ... 64.svg.

Convention:
- File name: zero-padded 2-digit King-Wen number ({king_wen:02d}.svg).
- Image: 6 horizontal bars stacked top-down representing the hexagram.
  Top of image = top hào (line 6) = first char of binary string.
- Yang (bit '1') = single solid bar.
- Yin (bit '0') = bar with a gap in the middle (two segments).

Output: client/webapp/public/que-images/*.svg
"""

from __future__ import annotations

from pathlib import Path

from core.hexagram import HEXAGRAMS


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "client/webapp/public/que-images"

# Visual constants (viewBox-relative units).
VIEW_W = 80
VIEW_H = 80
BAR_HEIGHT = 9
BAR_GAP = 3          # vertical gap between hào
YIN_SPLIT = 14       # horizontal gap in the middle of a yin bar
PAD_X = 8            # left/right padding
PAD_Y = 4            # top/bottom padding

COLOR_BAR = "#e8c95a"        # gold (matches frontend accent)
COLOR_BG = "transparent"


def hexagram_svg(king_wen: int, binary_top_down: str, name_vi: str) -> str:
    """Render one hexagram as SVG markup."""
    bar_w = VIEW_W - 2 * PAD_X
    half_w = (bar_w - YIN_SPLIT) / 2

    bars: list[str] = []
    # binary_top_down[0] is the TOP hào. We draw top-down: y increases downward.
    for i, bit in enumerate(binary_top_down):
        y = PAD_Y + i * (BAR_HEIGHT + BAR_GAP)
        if bit == "1":
            bars.append(
                f'<rect x="{PAD_X}" y="{y}" width="{bar_w}" height="{BAR_HEIGHT}" '
                f'fill="{COLOR_BAR}" rx="1.2" />'
            )
        else:
            # Yin: two segments with center gap.
            bars.append(
                f'<rect x="{PAD_X}" y="{y}" width="{half_w}" height="{BAR_HEIGHT}" '
                f'fill="{COLOR_BAR}" rx="1.2" />'
            )
            bars.append(
                f'<rect x="{PAD_X + half_w + YIN_SPLIT}" y="{y}" width="{half_w}" '
                f'height="{BAR_HEIGHT}" fill="{COLOR_BAR}" rx="1.2" />'
            )

    bars_svg = "\n  ".join(bars)
    title = f"Quẻ {king_wen} — {name_vi}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'role="img" aria-label="{title}">\n'
        f"  <title>{title}</title>\n"
        f"  {bars_svg}\n"
        f"</svg>\n"
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # HEXAGRAMS is ordered by hex.id (Fuxi), but each item has king_wen_index.
    by_kw = {h.king_wen_index: h for h in HEXAGRAMS}
    assert set(by_kw.keys()) == set(range(1, 65)), "Expected 64 hexagrams 1..64"

    for kw in range(1, 65):
        h = by_kw[kw]
        svg = hexagram_svg(kw, h.binary, h.name_vi)
        out = OUTPUT_DIR / f"{kw:02d}.svg"
        out.write_text(svg, encoding="utf-8")

    print(f"Wrote 64 SVG files to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
