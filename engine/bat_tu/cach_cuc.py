"""Cách Cục (格局) classifier — pattern recognition for Bát Tự charts.

Classical 子平 categorizes charts into named "patterns" (格), which determine
how Day Master is interpreted + refine Dụng Thần choice. Common categories:

1. 普通格 (Normal patterns) — based on month branch's hidden stem in Thập Thần:
   - Chính Quan cách (正官格)
   - Thất Sát cách (七殺格 / 偏官)
   - Chính Tài cách (正財格)
   - Thiên Tài cách (偏財格)
   - Thực Thần cách (食神格)
   - Thương Quan cách (傷官格)
   - Chính Ấn cách (正印格)
   - Thiên Ấn cách (偏印格)
   - (Tỉ Kiên + Kiếp Tài usually NOT classified as cách — they form 比劫 patterns)

2. 從格 (Follow patterns) — extreme imbalance:
   - Tòng Tài cách (從財) — Day Master extremely weak, all Tài; follow money
   - Tòng Sát cách (從殺)
   - Tòng Nhi cách (從兒)  — follow output
   - Tòng Cường cách (從強) — follow strength when DM extreme strong

3. 化氣格 (Transform patterns) — DM merges with another via 5-合:
   - Hóa Mộc / Hóa Hỏa / Hóa Thổ / Hóa Kim / Hóa Thủy

This v1 implements **Normal cách cục classifier** (most common). Tòng + Hóa
patterns require more nuanced detection — flagged as deferred.

Reference: 子平真詮 chương 12-22.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import BRANCH_HIDDEN_STEMS
from .thap_than import thap_than_of


# Map Thập Thần → cách cục name (where applicable).
THAP_THAN_TO_CACH: dict[str, str] = {
    "Chính Quan": "Chính Quan cách (正官格)",
    "Thất Sát":   "Thất Sát cách (七殺格)",
    "Chính Tài":  "Chính Tài cách (正財格)",
    "Thiên Tài":  "Thiên Tài cách (偏財格)",
    "Thực Thần":  "Thực Thần cách (食神格)",
    "Thương Quan":"Thương Quan cách (傷官格)",
    "Chính Ấn":   "Chính Ấn cách (正印格)",
    "Thiên Ấn":   "Thiên Ấn cách (偏印格)",
    # Tỉ/Kiếp typically NOT a "cách" — but we tag them for completeness.
    "Tỷ Kiên":    "Kiến Lộc cách (建祿格) — đặc biệt",
    "Kiếp Tài":   "Dương Nhận cách (羊刃格) — đặc biệt",
}


# Cách cục characteristics + Vietnamese reading.
CACH_DETAILS: dict[str, dict[str, str]] = {
    "Chính Quan cách (正官格)": {
        "polarity": "lành (quý)",
        "essence": "Quan tinh chính thống — danh tiếng, chức tước, kỷ luật.",
        "favorable": "Hợp công chức / chức vụ / nghề chính danh. Cần Ấn bảo hộ.",
        "kỵ": "Sợ Thương Quan đả phá. Sợ Thất Sát hỗn tạp.",
    },
    "Thất Sát cách (七殺格)": {
        "polarity": "mạnh (hung-thành-quý)",
        "essence": "Quan sát — quyền lực dữ dội, áp lực + tướng tinh.",
        "favorable": "Hợp quân đội / công an / kinh doanh mạo hiểm. Cần Thực Thần chế Sát hoặc Ấn hóa Sát.",
        "kỵ": "Sát quá mạnh + không có chế hóa → tai họa, kiện tụng.",
    },
    "Chính Tài cách (正財格)": {
        "polarity": "lành (phú)",
        "essence": "Tài chính ổn định — lương cứng, vợ chính (Nam).",
        "favorable": "Day Master vượng + Tài vượng → đại phú. Cần Thực Thương sinh Tài.",
        "kỵ": "Kiếp Tài cướp đoạt. Day Master nhược không gánh nổi Tài.",
    },
    "Thiên Tài cách (偏財格)": {
        "polarity": "lành (phú, đào hoa)",
        "essence": "Tài lộc bất ngờ — kinh doanh, đầu cơ, có sức hút.",
        "favorable": "Phù hợp khởi nghiệp, kinh doanh đa lĩnh vực, môi giới.",
        "kỵ": "Quá nhiều Tỉ Kiếp cướp Tài. Day Master nhược.",
    },
    "Thực Thần cách (食神格)": {
        "polarity": "lành (phúc, hưởng thụ)",
        "essence": "Sao sáng tạo + tận hưởng — tài năng + ăn lộc.",
        "favorable": "Hợp nghệ thuật, sáng tạo, ẩm thực, giáo dục.",
        "kỵ": "Kiêu Thần (Thiên Ấn) đoạt Thực Thần → mất nguồn lộc.",
    },
    "Thương Quan cách (傷官格)": {
        "polarity": "phá cách — vừa lành vừa dữ",
        "essence": "Tài năng vượt khuôn khổ — phá cách, nổi loạn.",
        "favorable": "Hợp nghệ sĩ, sáng tạo độc đáo, khởi nghiệp đột phá. Cần Chính Ấn để 'Thương Quan phối Ấn'.",
        "kỵ": "Khi Day Master nhược + Quan tinh hiện → 'Thương Quan kiến Quan' đại hung.",
    },
    "Chính Ấn cách (正印格)": {
        "polarity": "lành (quý + an dưỡng)",
        "essence": "Sao mẹ + học vấn + bảo hộ — trí tuệ, danh tiếng học thuật.",
        "favorable": "Hợp giáo dục, học thuật, nghiên cứu, từ thiện.",
        "kỵ": "Tài tinh đoạt Ấn (Chính Tài phá Chính Ấn). Quá nhiều Ấn → ỷ lại.",
    },
    "Thiên Ấn cách (偏印格)": {
        "polarity": "trung tính — đa năng nhưng khắc nghiệt",
        "essence": "Kiêu Thần — trí tuệ phi truyền thống, quý nhân ngầm.",
        "favorable": "Hợp lĩnh vực thiền / tôn giáo / nghiên cứu lập dị / công nghệ.",
        "kỵ": "Thiên Ấn đoạt Thực Thần → mất phúc lộc.",
    },
    "Kiến Lộc cách (建祿格) — đặc biệt": {
        "polarity": "phải xét Tài-Quan",
        "essence": "Day Master đắc lệnh tại Trụ Tháng — Lộc Thần ngụ.",
        "favorable": "Cần Tài hoặc Quan để hóa khí, không thì cô đơn vô dụng.",
        "kỵ": "Thiếu Tài + Thiếu Quan → người tự lập nhưng nghèo + cô.",
    },
    "Dương Nhận cách (羊刃格) — đặc biệt": {
        "polarity": "dữ — uy mãnh nhưng hiểm",
        "essence": "Kiếp Tài cực vượng — Dương Nhận sao quyền + tai nạn.",
        "favorable": "Hợp tướng quân / kinh doanh mạo hiểm / phẫu thuật.",
        "kỵ": "Sợ Thất Sát phối Nhận (羊刃逢沖) → tai nạn lớn.",
    },
}


@dataclass(frozen=True)
class CachCucResult:
    """Cách cục classification + diễn giải."""

    cach_name: str                  # canonical name (alias: cach_cuc_label)
    based_on: str                   # which hidden stem of month branch
    based_on_thap_than: str         # Thập Thần of that stem vs Day Master
    polarity: str
    essence: str
    favorable: str
    ky: str
    confidence: str                 # 'high' / 'medium' / 'low'
    note: str

    @property
    def cach_cuc_label(self) -> str:
        """Alias for cach_name — consumers may use either field."""
        return self.cach_name

    def to_dict(self) -> dict:
        # Inject alias so downstream code reading `cach_cuc_label` works
        d = asdict(self)
        d["cach_cuc_label"] = self.cach_name
        return d


def classify_cach_cuc(pillars: dict, day_master_stem: str) -> dict:
    """Classify a Bát Tự chart's cách cục based on month-branch's primary hidden stem.

    Classical 子平 rule: take Trụ Tháng's địa chi, find its 本氣 (primary hidden stem),
    then derive that stem's Thập Thần relative to Day Master. The resulting Thập Thần
    name → cách cục name.

    Edge cases:
    - If month-branch's primary stem == Day Master → Kiến Lộc (special).
    - Tỉ Kiên usually NOT a cách; Kiếp Tài → Dương Nhận cách (special).

    Returns CachCucResult dict.
    """
    month_branch = pillars["month"]["branch"]
    hidden_stems = BRANCH_HIDDEN_STEMS.get(month_branch, ())
    if not hidden_stems:
        return CachCucResult(
            cach_name="Không xác định",
            based_on="(không có tàng can)",
            based_on_thap_than="",
            polarity="",
            essence="Không tra được tàng can của Trụ Tháng.",
            favorable="",
            ky="",
            confidence="low",
            note=f"Branch {month_branch} không có entry trong BRANCH_HIDDEN_STEMS.",
        ).to_dict()

    # Primary hidden stem = first in the tuple (本氣).
    primary_stem = hidden_stems[0]

    if primary_stem == day_master_stem:
        # Special: Kiến Lộc cách
        cach = "Kiến Lộc cách (建祿格) — đặc biệt"
        thap_than_name = "Tỷ Kiên"
    else:
        thap_than_name = thap_than_of(day_master_stem, primary_stem)
        cach = THAP_THAN_TO_CACH.get(thap_than_name, "Không xác định")

    details = CACH_DETAILS.get(cach, {
        "polarity": "", "essence": "", "favorable": "", "kỵ": "",
    })

    return CachCucResult(
        cach_name=cach,
        based_on=f"{primary_stem} (bản khí Trụ Tháng {month_branch})",
        based_on_thap_than=thap_than_name,
        polarity=details["polarity"],
        essence=details["essence"],
        favorable=details["favorable"],
        ky=details["kỵ"],
        confidence="high" if cach != "Không xác định" else "low",
        note=(
            "Phân loại theo bản khí tàng can Trụ Tháng — quy tắc Tử Bình chuẩn. "
            "Tòng cách + Hóa Khí cách (extreme patterns) chưa kiểm tra — sẽ thêm v2."
        ),
    ).to_dict()
