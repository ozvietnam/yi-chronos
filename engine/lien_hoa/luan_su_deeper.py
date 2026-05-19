"""Liên Hoa luận sự — deeper interpretation layers.

Extends the existing 6-domain reading with:

1. **Per-KTS narrative**: each Không Thời Sự gets a phase-specific reading
   describing what happens at that stage of the đợt độn.
2. **Extra domains**: con cái, học vấn, kiện tụng (lawsuit), công việc detailed.
3. **Hexagram archetype overlay**: bring in the chánh quái text from
   `data/seeds/hexagram_interpretation_v2.json` for richer readings.
4. **Tổng kết luận** (overall synthesis): combine all domain readings into
   a 3-paragraph life summary.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import LUC_THAN_NAMES
from .luan_su import (
    DomainReading,
    chanh_dang_of,
    chu_su_distribution,
    menh_cung_lt_of,
)


# ─── Per-KTS narrative ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class KTSNarrative:
    """Narrative for one Không Thời Sự."""

    index: int
    label: str
    chanh_quai_vi: str
    chu_su: str
    chu_su_full: str
    role_in_sequence: str           # "Tiên đề" / "Đợt 1 - Vào" / "Đợt 1 - Trung" / ...
    phase_meaning: str
    transition_to_next: str         # what changes going to next KTS

    def to_dict(self) -> dict:
        return asdict(self)


# Role labels for each KTS index given the dot_count.
def _kts_role_label(index: int, dot_count: int) -> str:
    """Return a Vietnamese phase label for KTS #index in a `dot_count`-đợt chain."""
    if index == 1:
        return "Tiên đề (gốc khởi đầu)"
    # 4 KTS per đợt: KTS 2,3,4,5 = đợt 1; 6,7,8,9 = đợt 2; 10,11,12,13 = đợt 3
    offset = (index - 2) % 4
    cycle = (index - 2) // 4 + 1
    phase_in_cycle = ["Vào", "Trung", "Cuối", "Thoát"][offset]
    if cycle > dot_count:
        return f"Phụ thêm — KTS {index}"
    return f"Đợt {cycle} — {phase_in_cycle}"


def _phase_meaning(role: str, chu_su: str, chu_su_full: str) -> str:
    """Compose Vietnamese phase meaning from role + chủ sự."""
    if "Tiên đề" in role:
        return (
            f"Gốc rễ ban đầu — chủ sự {chu_su_full}. "
            f"Đây là 'điểm sinh' của toàn bộ chuỗi sự kiện."
        )
    if "Vào" in role:
        return f"Bước vào giai đoạn mới — {chu_su_full} dẫn dắt khởi sự."
    if "Trung" in role:
        return f"Đỉnh giai đoạn — {chu_su_full} đang mạnh, sự kiện chính xảy ra."
    if "Cuối" in role:
        return f"Cuối giai đoạn — {chu_su_full} đã suy, cần chuẩn bị chuyển hóa."
    if "Thoát" in role:
        return f"Thoát giai đoạn — chuyển trạng thái, {chu_su_full} đóng vai cầu nối."
    return f"Chủ sự {chu_su_full}."


def per_kts_narrative(spread: dict) -> list[dict]:
    """Build narrative for each KTS in the spread."""
    dot_count = spread["dot_count"]
    out = []
    kts_list = spread["khong_thoi"]
    for i, kt in enumerate(kts_list):
        role = _kts_role_label(kt["index"], dot_count)
        chu_su = kt["chu_su"]
        chu_su_full = LUC_THAN_NAMES.get(chu_su, chu_su)
        phase_meaning = _phase_meaning(role, chu_su, chu_su_full)

        # Transition: compare with next KTS if exists.
        transition = ""
        if i + 1 < len(kts_list):
            next_kt = kts_list[i + 1]
            next_chu_su = LUC_THAN_NAMES.get(next_kt["chu_su"], next_kt["chu_su"])
            if next_chu_su != chu_su_full:
                transition = f"Chuyển sang {next_chu_su}."
            else:
                transition = "Giữ nguyên chủ sự."
        else:
            transition = "Kết thúc chuỗi."

        out.append(KTSNarrative(
            index=kt["index"],
            label=kt["label"],
            chanh_quai_vi=kt["chanh"]["name_vi"],
            chu_su=chu_su,
            chu_su_full=chu_su_full,
            role_in_sequence=role,
            phase_meaning=phase_meaning,
            transition_to_next=transition,
        ).to_dict())
    return out


# ─── Extra domains: con cái / học vấn / kiện tụng / công việc ─────────────────


def interpret_children(spread: dict) -> DomainReading:
    """Con cái — chủ yếu xem Tử Tôn (C)."""
    counts = chu_su_distribution(spread["khong_thoi"])
    c = counts["C"]
    q = counts["Q"]
    t = counts["T"]
    evidence = [
        f"Tử Tôn (C, con cái): {c}",
        f"Quan Quỷ (Q, áp lực): {q}",
        f"Thê Tài (T, mẹ chăm con): {t}",
    ]

    if c == 0:
        return DomainReading(
            domain="children", domain_vi="Con cái",
            verdict="Hiếm con / muộn con",
            explanation="Vắng bóng Tử Tôn — khả năng có con muộn hoặc hiếm hoi.",
            evidence=evidence,
        )
    if c >= 3:
        return DomainReading(
            domain="children", domain_vi="Con cái",
            verdict="Đông con / con cái đa dạng",
            explanation=f"{c} Tử Tôn — có thể đông con hoặc nhiều mối quan hệ thầy-trò.",
            evidence=evidence,
        )
    if c >= 1 and q >= 2:
        return DomainReading(
            domain="children", domain_vi="Con cái",
            verdict="Có con nhưng lo lắng nhiều",
            explanation=f"{c} Tử Tôn + {q} Quan Quỷ → con cái có khó khăn, áp lực.",
            evidence=evidence,
        )
    return DomainReading(
        domain="children", domain_vi="Con cái",
        verdict="Bình thường",
        explanation=f"{c} Tử Tôn trong chuỗi — số con bình thường.",
        evidence=evidence,
    )


def interpret_study(spread: dict) -> DomainReading:
    """Học vấn — Phụ Mẫu (P) là sách / kiến thức; Tử Tôn (C) là khả năng học."""
    counts = chu_su_distribution(spread["khong_thoi"])
    p = counts["P"]
    c = counts["C"]
    evidence = [
        f"Phụ Mẫu (P, sách / thầy): {p}",
        f"Tử Tôn (C, khả năng tiếp thu): {c}",
    ]
    if p >= 2 and c >= 1:
        return DomainReading(
            domain="study", domain_vi="Học vấn",
            verdict="Học vấn tốt",
            explanation=f"{p} Phụ Mẫu + {c} Tử Tôn → có thầy có sách, có khả năng tiếp thu.",
            evidence=evidence,
        )
    if p == 0:
        return DomainReading(
            domain="study", domain_vi="Học vấn",
            verdict="Học vấn hạn chế",
            explanation="Không có Phụ Mẫu trong chuỗi — thiếu sách / thầy / nền tảng học vấn.",
            evidence=evidence,
        )
    return DomainReading(
        domain="study", domain_vi="Học vấn",
        verdict="Trung bình",
        explanation=f"{p} Phụ Mẫu → học vấn ở mức bình thường.",
        evidence=evidence,
    )


def interpret_lawsuit(spread: dict) -> DomainReading:
    """Kiện tụng — Quan Quỷ (Q) là sao kiện; Phụ Mẫu (P) là quan tòa / luật sư."""
    counts = chu_su_distribution(spread["khong_thoi"])
    q = counts["Q"]
    p = counts["P"]
    evidence = [
        f"Quan Quỷ (Q, kiện cáo / án): {q}",
        f"Phụ Mẫu (P, luật sư / quan): {p}",
    ]
    if q >= 2 and p == 0:
        return DomainReading(
            domain="lawsuit", domain_vi="Kiện tụng",
            verdict="Rủi ro kiện tụng, không có quan bảo hộ",
            explanation=f"{q} Quan Quỷ + thiếu Phụ Mẫu → dễ vướng kiện, không có người hậu thuẫn pháp lý.",
            evidence=evidence,
        )
    if q >= 1 and p >= 1:
        return DomainReading(
            domain="lawsuit", domain_vi="Kiện tụng",
            verdict="Có thể có kiện, nhưng có quý nhân hỗ trợ",
            explanation=f"{q} Quan + {p} Phụ → vướng nhưng có người giúp xử lý.",
            evidence=evidence,
        )
    if q == 0:
        return DomainReading(
            domain="lawsuit", domain_vi="Kiện tụng",
            verdict="Không vướng kiện",
            explanation="Không có Quan Quỷ → không có tín hiệu kiện tụng trong giai đoạn này.",
            evidence=evidence,
        )
    return DomainReading(
        domain="lawsuit", domain_vi="Kiện tụng",
        verdict="Bình thường",
        explanation="Phân bố cân bằng — không có dấu hiệu bất thường.",
        evidence=evidence,
    )


def interpret_career(spread: dict) -> DomainReading:
    """Sự nghiệp — Quan Quỷ (Q) là chức vị; Thê Tài (T) là thu nhập."""
    counts = chu_su_distribution(spread["khong_thoi"])
    q = counts["Q"]
    t = counts["T"]
    p = counts["P"]
    evidence = [
        f"Quan Quỷ (Q, chức vị): {q}",
        f"Thê Tài (T, lương / thu nhập): {t}",
        f"Phụ Mẫu (P, quý nhân cấp trên): {p}",
    ]
    if q >= 2 and t >= 2:
        return DomainReading(
            domain="career", domain_vi="Sự nghiệp",
            verdict="Sự nghiệp + tài chính cùng tốt",
            explanation=f"{q} Quan + {t} Tài → vừa có chức vừa có lộc.",
            evidence=evidence,
        )
    if q >= 2 and t == 0:
        return DomainReading(
            domain="career", domain_vi="Sự nghiệp",
            verdict="Có chức nhưng thu nhập kém",
            explanation=f"{q} Quan + thiếu Tài → chức vị danh dự nhưng lương bổng hẹp.",
            evidence=evidence,
        )
    if q == 0 and t >= 2:
        return DomainReading(
            domain="career", domain_vi="Sự nghiệp",
            verdict="Tự kinh doanh, không vào chức",
            explanation=f"{t} Tài + thiếu Quan → không hợp công chức, hợp tự kinh doanh.",
            evidence=evidence,
        )
    return DomainReading(
        domain="career", domain_vi="Sự nghiệp",
        verdict="Bình thường",
        explanation=f"Q={q}, T={t} → sự nghiệp ở mức trung bình.",
        evidence=evidence,
    )


# ─── Tổng kết luận synthesis ──────────────────────────────────────────────────


def composed_synthesis(spread: dict, domain_readings: list[dict]) -> str:
    """Compose a 3-paragraph synthesis of the entire reading."""
    gender_phrase = "TA Nam" if spread.get("gender") == "nam" else "TA Nữ"
    tien_de = spread["khong_thoi"][0]
    dot = spread["dot_count"]

    # Paragraph 1: tổng quan
    p1 = (
        f"Tổng quan: {gender_phrase}, quẻ Tiên đề {tien_de['chanh']['name_vi']} "
        f"({dot} đợt độn, {spread['khong_thoi_count']} không thời sự). "
    )

    # Paragraph 2: tổng hợp domains
    favorable = [r for r in domain_readings
                 if any(kw in r["verdict"].lower() for kw in ("thuận", "tốt", "thành", "lành", "vượng", "mạnh"))]
    challenging = [r for r in domain_readings
                   if any(kw in r["verdict"].lower() for kw in ("hao", "nguy", "kém", "thất", "bất thành", "khốn", "hiểm"))]

    p2 = "Điểm mạnh: "
    if favorable:
        p2 += "; ".join(f"{r['domain_vi']} ({r['verdict']})" for r in favorable[:3]) + ". "
    else:
        p2 += "không có lĩnh vực thuận rõ rệt. "
    p2 += "Điểm yếu: "
    if challenging:
        p2 += "; ".join(f"{r['domain_vi']} ({r['verdict']})" for r in challenging[:3]) + "."
    else:
        p2 += "không có rủi ro lớn."

    # Paragraph 3: khuyến nghị
    if dot == 1:
        p3 = (
            "Khuyến nghị: vận đời ổn định, ít thay đổi lớn — "
            "tập trung vào lĩnh vực mạnh, giữ vững nền tảng."
        )
    elif dot == 2:
        p3 = (
            "Khuyến nghị: có biến giữa đời — chuẩn bị cho chuyển hóa "
            "tại đợt thứ 2, linh hoạt thay đổi chiến lược."
        )
    else:
        p3 = (
            "Khuyến nghị: nhiều thăng trầm — không cố thủ một con đường, "
            "đón nhận biến cố như là cơ hội tái lập."
        )

    return p1 + "\n\n" + p2 + "\n\n" + p3


# ─── Top-level deeper interpretation ──────────────────────────────────────────


@dataclass(frozen=True)
class LuanSuDeeper:
    """Deeper layer of luận sự — extends LuanSu."""

    extra_domain_readings: list[dict]    # 4 new domains
    per_kts_narratives: list[dict]       # one per KTS
    composed_synthesis_full: str         # 3-paragraph synthesis

    def to_dict(self) -> dict:
        return asdict(self)


def luan_su_deeper(spread: dict) -> dict:
    """Build deeper interpretation layers.

    Args:
        spread: full Liên Hoa spread (from cast_lien_hoa)

    Returns dict with `extra_domain_readings`, `per_kts_narratives`, `composed_synthesis_full`.
    """
    extra_readings = [
        interpret_children(spread).to_dict(),
        interpret_study(spread).to_dict(),
        interpret_lawsuit(spread).to_dict(),
        interpret_career(spread).to_dict(),
    ]
    kts_narrative = per_kts_narrative(spread)

    # Combine with existing v1 domain readings (if present) for synthesis.
    all_domains = list(extra_readings)
    if "luan_su" in spread and "domain_readings" in spread["luan_su"]:
        all_domains.extend(spread["luan_su"]["domain_readings"])

    synthesis = composed_synthesis(spread, all_domains)

    return LuanSuDeeper(
        extra_domain_readings=extra_readings,
        per_kts_narratives=kts_narrative,
        composed_synthesis_full=synthesis,
    ).to_dict()
