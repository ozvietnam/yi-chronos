"""Mai Hoa Cross-Cast Correlation — Cải tiến #4.

Đối chiếu chéo các quẻ gieo cùng kỳ (cùng ngày, cùng sự kiện) để phát hiện:
1. Trường năng lượng cùng kỳ (Chính quẻ trùng nhau ở nhiều cast)
2. Vai trò Thể khác nhau giữa các intent
3. Tổng hợp pattern xuyên nhiều cast

Cơ sở thực nghiệm: Pr#3 (tổng ngày 17/5) và Pr#5 (riêng anh 86) cùng cast
được Chính Chấn/Tốn (Hằng) — bằng chứng đầu tay cho trường năng lượng ngày.

Em là HỌC TRÒ — output là STRUCTURED ANALYSIS, không phải lời tiên đoán.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from typing import Optional

from engine.yi_wiki.cast import CastResult
from engine.yi_wiki.interpret import (
    InterpretationResult, analyze, QUAI_NGU_HANH, NGU_HANH_SINH, NGU_HANH_KHAC,
)


@dataclass
class CastEntry:
    """1 lần gieo trong session correlate."""
    label: str                          # nhãn anh đặt: "Pr#3 tổng ngày" / "Anh 86"
    cast: CastResult
    intent: str = "general"
    month: Optional[int] = None
    interpretation: Optional[InterpretationResult] = None


@dataclass
class CrossCastReport:
    """Kết quả phân tích đối chiếu nhiều cast."""
    entries: list[CastEntry]
    n_casts: int

    # Trường năng lượng kỳ
    chinh_trung: dict[str, list[str]] = field(default_factory=dict)  # quẻ_name → [labels]
    chinh_trung_summary: str = ""

    # Vai trò Thể giữa các cast
    the_roles: list[dict] = field(default_factory=list)  # [{label, the_que, the_h, intent}, ...]
    the_roles_summary: str = ""

    # Pattern xuyên cast — tổng hợp
    common_warnings: list[str] = field(default_factory=list)
    cross_pattern: str = ""


def correlate_casts(
    entries: list[CastEntry],
    auto_analyze: bool = True,
) -> CrossCastReport:
    """Đối chiếu chéo nhiều cast cùng kỳ.

    Args:
        entries: danh sách cast với label + intent + (optional) month
        auto_analyze: tự động chạy analyze() nếu interpretation chưa có
    """
    if not entries:
        return CrossCastReport(entries=[], n_casts=0)

    # Tự động phân tích nếu chưa có
    if auto_analyze:
        for e in entries:
            if e.interpretation is None:
                e.interpretation = analyze(e.cast, month=e.month, intent=e.intent)

    # ── (1) Tìm Chính quẻ trùng nhau ──
    chinh_groups: dict[str, list[str]] = {}
    for e in entries:
        name = e.cast.chinh_quai.name
        chinh_groups.setdefault(name, []).append(e.label)

    chinh_trung = {n: labels for n, labels in chinh_groups.items() if len(labels) >= 2}

    if chinh_trung:
        parts = []
        for name, labels in chinh_trung.items():
            parts.append(
                f"★ Chính quẻ {name} xuất hiện ở {len(labels)} cast "
                f"({', '.join(labels)}) → bằng chứng TRƯỜNG NĂNG LƯỢNG CÙNG KỲ"
            )
        chinh_trung_summary = "\n".join(parts)
    else:
        chinh_trung_summary = (
            "Không có Chính quẻ trùng — mỗi cast có trường năng lượng riêng "
            "(tuỳ intent + thời điểm)."
        )

    # ── (2) Vai trò Thể giữa các cast ──
    the_roles = []
    for e in entries:
        if e.interpretation is None:
            continue
        td = e.interpretation.the_dung
        the_roles.append({
            "label": e.label,
            "intent": e.intent,
            "the_que": td.the_que,
            "the_hanh": td.the_hanh,
            "dung_que": td.dung_que,
            "dung_hanh": td.dung_hanh,
            "relationship": td.relationship,
            "auspice": td.auspice,
        })

    # Đếm tần suất Thể qua các cast
    the_freq = Counter(r["the_que"] for r in the_roles)
    if len(the_freq) == 1:
        only = list(the_freq.keys())[0]
        the_roles_summary = (
            f"Thể NHẤT QUÁN ở {only} qua {len(the_roles)} cast — "
            f"vai trò anh ổn định trong kỳ này"
        )
    else:
        items = ", ".join(f"{q}×{n}" for q, n in the_freq.items())
        the_roles_summary = (
            f"Thể THAY ĐỔI tuỳ intent ({items}) — "
            f"vai trò anh khác nhau với mỗi đối tác/sự việc"
        )

    # ── (3) Pattern xuyên cast ──
    # Đếm cát/hung
    auspices = Counter(r["auspice"] for r in the_roles)
    n_cat = auspices.get("cát", 0)
    n_hung = auspices.get("hung", 0)
    n_binh = auspices.get("bình", 0)

    cross_lines = [
        f"Tổng quát: {n_cat} cát · {n_hung} hung · {n_binh} bình "
        f"trong {len(the_roles)} cast"
    ]

    # Đếm Trùng Phùng cross-cast
    trung_phung_count = sum(
        1 for e in entries
        if e.interpretation
        and (e.interpretation.trung_phung_chinh or e.interpretation.trung_phung_bien)
    )
    if trung_phung_count > 0:
        cross_lines.append(
            f"⚡ {trung_phung_count}/{len(entries)} cast có TRÙNG PHÙNG — "
            f"lực khuếch đại mạnh trong kỳ này"
        )

    # Common warnings (xuất hiện ở ≥50% cast)
    all_warnings = []
    for e in entries:
        if e.interpretation:
            all_warnings.extend(e.interpretation.warnings)
    warn_counter = Counter(all_warnings)
    threshold = max(2, len(entries) // 2)
    common_warnings = [w for w, n in warn_counter.items() if n >= threshold]

    if common_warnings:
        cross_lines.append(
            f"⚠️ Cảnh báo CHUNG ({len(common_warnings)} pattern lặp ≥{threshold} cast):"
        )
        for w in common_warnings:
            cross_lines.append(f"  • {w}")

    cross_pattern = "\n".join(cross_lines)

    return CrossCastReport(
        entries=entries,
        n_casts=len(entries),
        chinh_trung=chinh_trung,
        chinh_trung_summary=chinh_trung_summary,
        the_roles=the_roles,
        the_roles_summary=the_roles_summary,
        common_warnings=common_warnings,
        cross_pattern=cross_pattern,
    )


def demo():
    """Demo cross-cast với Pr#3 + Pr#5 ngày 17/5 (cùng Chính Hằng)."""
    from engine.yi_wiki.cast import cast_by_time

    # Pr#3: tổng ngày 17/5 — gieo 16/5 00:52 (giờ Tý)
    cast_3 = cast_by_time("Ngọ", 5, 16, "Tý")

    # Pr#5: anh 86 — gieo 16/5 16:29 (giờ Thân)
    cast_5 = cast_by_time("Ngọ", 5, 16, "Thân")

    entries = [
        CastEntry(label="Pr#3 (tổng ngày 17/5)", cast=cast_3, intent="yet_kien", month=5),
        CastEntry(label="Pr#5 (anh 86 dự án 1 tháng)", cast=cast_5, intent="cau_tai", month=5),
    ]

    report = correlate_casts(entries)

    print("═" * 70)
    print(f"🔗 CROSS-CAST CORRELATION REPORT — {report.n_casts} cast")
    print("═" * 70)
    print()
    print("📊 (1) TRƯỜNG NĂNG LƯỢNG KỲ:")
    print(report.chinh_trung_summary)
    print()
    print("👤 (2) VAI TRÒ THỂ:")
    print(report.the_roles_summary)
    for r in report.the_roles:
        print(f"  • {r['label']}: Thể {r['the_que']}({r['the_hanh']}) | "
              f"Dụng {r['dung_que']}({r['dung_hanh']}) | "
              f"{r['relationship']} = {r['auspice']}")
    print()
    print("🎯 (3) PATTERN XUYÊN CAST:")
    print(report.cross_pattern)


if __name__ == "__main__":
    demo()
