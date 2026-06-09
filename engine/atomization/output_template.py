"""Output Template — KHUNG OUTPUT 3-Layer cho 1 lá số.

Paradigm anh CHỐT 2026-06-09:
  - Layer 1 "Chuyện về anh" — user love stories about themselves
  - Layer 2 "Vì sao lại thế" — they want to understand why
  - Layer 3 "Sách cổ đã nói" — citation authentic củng cố niềm tin

Backend ĐỘC LẬP. Mỗi sách = 1 mảnh ghép quy luật vũ trụ.

Structure: 12 cung × N variants × 3 layers per output field.
Derived from Trung Châu Q2 Chương 5 (Cung Viên Luận).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

CUNG_12 = [
    "Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch",
    "Sự Nghiệp", "Giao Hữu", "Thiên Di", "Tật Ách",
    "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ",
]

CHINH_TINH_14 = [
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng",
    "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
    "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân",
]


class Layer(str, Enum):
    """3 lớp output anh chốt."""
    CHUYEN_VE_ANH = "layer_1_chuyen_ve_anh"        # narrative cá nhân
    VI_SAO_LAI_THE = "layer_2_vi_sao_lai_the"      # nguyên lý vận hành
    SACH_CO_DA_NOI = "layer_3_sach_co_da_noi"      # citation authentic


# ═══════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OutputField:
    """1 field trong khung output cho 1 cung của 1 lá số."""
    field_id: str               # vd "menh.tu_vi.tong_quan"
    cung: str                   # vd "Mệnh"
    sao_chinh: str | None       # vd "Tử Vi" or None nếu Vô chính diệu
    variant: str                # vd "Tử Vi độc tọa Tý/Ngọ"
    aspect: str                 # vd "tong_quan" | "modifiers" | "timing" | "canh_bao"
    description_vi: str         # mô tả Việt thuần
    atomic_q_keywords: list[str]  # keywords để retrieve atoms
    section_priority: dict[str, str]  # {section_id: priority} — sách section nào ưu tiên


@dataclass
class ThreeLayerOutput:
    """Output cho 1 field — 3 layers."""
    field_id: str

    # Layer 1: Chuyện về anh (narrative)
    layer_1_narrative: str = ""
    layer_1_examples: list[str] = field(default_factory=list)

    # Layer 2: Vì sao lại thế (reasoning)
    layer_2_nguyen_ly: str = ""
    layer_2_co_che: str = ""        # cơ chế vận hành (âm dương / ngũ hành / sao tương tác)

    # Layer 3: Sách cổ đã nói (citations)
    layer_3_citations: list[dict] = field(default_factory=list)
    # mỗi citation: {book, page, author, source_quote, han_viet, viet_dich}

    # Meta
    sources_atoms: list[int] = field(default_factory=list)  # atom_ids used
    sources_books: list[str] = field(default_factory=list)
    confidence: float = 0.0
    iron_rule_warning: str | None = None


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE BUILDER
# ═══════════════════════════════════════════════════════════════════

# Aspects per cung — câu hỏi cốt lõi user thường hỏi về mỗi cung
ASPECTS_PER_CUNG = {
    "Mệnh": [
        ("tong_quan", "Tổng quan tính cách + bản chất mệnh tạo"),
        ("uu_diem", "Ưu điểm bẩm sinh, sở trường"),
        ("nhuoc_diem", "Nhược điểm, điểm cần lưu ý"),
        ("dinh_huong", "Định hướng nghề / lĩnh vực phù hợp"),
        ("modifiers", "Cát hung modifiers: bách quan, cô quân, cách cục"),
        ("timing_dai_van", "Đại vận nào then chốt"),
        ("canh_bao_iron_rule", "Cảnh báo paradigm — KHÔNG predict cứng"),
    ],
    "Phu Thê": [
        ("dac_diem_ban_doi", "Đặc điểm người bạn đời"),
        ("hon_nhan", "Tính chất hôn nhân, hợp/khắc"),
        ("thoi_gian_thich_hop", "Tuổi cưới / năm cưới thuận"),
        ("canh_bao", "Cảnh báo: ly hôn / xa cách / hợp tan"),
        ("loi_khuyen", "Lời khuyên cải thiện quan hệ"),
    ],
    "Tài Bạch": [
        ("nguon_tien", "Nguồn tiền chính (lương, kinh doanh, đầu tư...)"),
        ("muc_do", "Mức độ tài lộc (cự phú, trung lưu, tiểu khang)"),
        ("rui_ro", "Rủi ro tài chính (phá tán, chậm, bệnh)"),
        ("nien_han_phat", "Năm phát tài (theo Hóa Lộc / Lộc Tồn lưu)"),
        ("loi_khuyen", "Cách giữ + tăng tài"),
    ],
    "Tử Tức": [
        ("con_cai", "Số con + đặc điểm"),
        ("thoi_gian_sinh", "Thời điểm sinh con thuận"),
        ("quan_he", "Quan hệ với con cái"),
        ("loi_khuyen", "Nuôi dạy + hỗ trợ"),
    ],
    "Sự Nghiệp": [
        ("nghe_phu_hop", "Nghề / lĩnh vực phù hợp"),
        ("tinh_chat_cong_viec", "Tính chất công việc (công/tư, độc lập/tập thể)"),
        ("muc_do_thang_tien", "Mức độ thăng tiến"),
        ("nien_han_phat", "Năm phát triển sự nghiệp"),
        ("canh_bao", "Cảnh báo công việc"),
    ],
    "Tật Ách": [
        ("benh_tieu_chi", "Bệnh tật tiềm ẩn theo cung"),
        ("cac_co_quan", "Cơ quan dễ bệnh"),
        ("phong_tranh", "Cách phòng tránh"),
        ("nien_han_can_chu_y", "Năm cần chú ý sức khỏe"),
    ],
    "Phúc Đức": [
        ("phuc_khi", "Phúc khí tổng quát"),
        ("hau_van", "Hậu vận an nhàn hay vất vả"),
        ("hau_due", "Quan hệ với hậu duệ"),
    ],
    # Skeleton — anh có thể refine sau
}


def build_aspects_for_cung(cung: str) -> list[tuple[str, str]]:
    """Return list of (aspect_key, description) for a cung. Default if no specific."""
    if cung in ASPECTS_PER_CUNG:
        return ASPECTS_PER_CUNG[cung]
    # Default 5 aspects for cung chưa define
    return [
        ("tong_quan", f"Tổng quan cung {cung}"),
        ("anh_huong", f"Ảnh hưởng đến cuộc sống mệnh tạo"),
        ("modifiers", "Modifiers cát/hung"),
        ("timing", "Niên hạn cát/kỵ"),
        ("loi_khuyen", "Lời khuyên"),
    ]


# Atomic Q keywords TEMPLATE per (sao, cung, aspect)
def build_atomic_keywords(sao: str | None, cung: str, aspect: str) -> list[str]:
    """Generate keywords để retrieve atoms cho field này."""
    keywords = [cung]
    if sao:
        keywords.insert(0, sao)
        keywords.append(f"{sao} {cung}")
        keywords.append(f"{sao} tại cung {cung}")
        keywords.append(f"{sao} thủ cung {cung}")
    # Aspect-specific
    aspect_keywords = {
        "tong_quan": ["tổng quan", "tính chất", "đặc điểm"],
        "uu_diem": ["ưu điểm", "sở trường", "cát"],
        "nhuoc_diem": ["nhược điểm", "kỵ", "hung"],
        "modifiers": ["bách quan triều củng", "cô quân", "cách cục"],
        "timing_dai_van": ["đại vận", "niên hạn", "lưu niên"],
        "canh_bao_iron_rule": ["cảnh báo", "Iron Rule", "đọc đồng dạng"],
        "dac_diem_ban_doi": ["bạn đời", "phu thê", "đặc điểm vợ chồng"],
        "hon_nhan": ["hôn nhân", "tính chất", "hợp khắc"],
        "nguon_tien": ["tài bạch", "tiền", "Lộc Tồn", "Hóa Lộc"],
        "rui_ro": ["phá tán", "rủi ro", "sát kỵ", "tài bạch"],
        "con_cai": ["tử tức", "con cái", "sinh"],
        "nghe_phu_hop": ["sự nghiệp", "quan lộc", "công việc"],
        "benh_tieu_chi": ["tật ách", "bệnh", "sức khỏe"],
        "phuc_khi": ["phúc đức", "phúc khí", "hậu vận"],
    }
    keywords.extend(aspect_keywords.get(aspect, []))
    return keywords


def build_full_template() -> list[OutputField]:
    """Build all 12 cung × 14 sao × N aspects fields."""
    fields = []
    for cung in CUNG_12:
        aspects = build_aspects_for_cung(cung)
        for sao in CHINH_TINH_14:
            for aspect_key, aspect_desc in aspects:
                fields.append(OutputField(
                    field_id=f"{cung}.{sao}.{aspect_key}",
                    cung=cung,
                    sao_chinh=sao,
                    variant=f"{sao} tại {cung}",
                    aspect=aspect_key,
                    description_vi=f"{aspect_desc} cho mệnh tạo có {sao} tại {cung}",
                    atomic_q_keywords=build_atomic_keywords(sao, cung, aspect_key),
                    section_priority={
                        # Trung Châu Q2 Chương 5.N section = primary
                        # (mapping logic in book_profile.py)
                    },
                ))
        # Also: Vô chính diệu variant
        fields.append(OutputField(
            field_id=f"{cung}.vo_chinh_dieu.tong_quan",
            cung=cung,
            sao_chinh=None,
            variant=f"Vô chính diệu tại {cung}",
            aspect="tong_quan",
            description_vi=f"Khi cung {cung} không có chính tinh — mượn sao đối cung",
            atomic_q_keywords=["vô chính diệu", "mượn sao", cung],
            section_priority={},
        ))
    return fields


# ═══════════════════════════════════════════════════════════════════
# CLI test
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fields = build_full_template()
    print(f"📐 Total output fields: {len(fields)}")
    print(f"   12 cung × 14 sao × ~5-7 aspects + vô chính diệu variants")
    print(f"\n📋 Sample first 5 fields:")
    for f in fields[:5]:
        print(f"   {f.field_id}")
        print(f"      desc: {f.description_vi}")
        print(f"      keywords: {f.atomic_q_keywords[:5]}")
    print(f"\n📋 Mệnh × Tử Vi aspects:")
    menh_tu_vi = [f for f in fields if f.cung == "Mệnh" and f.sao_chinh == "Tử Vi"]
    for f in menh_tu_vi:
        print(f"   {f.aspect:<20} — {f.description_vi}")
