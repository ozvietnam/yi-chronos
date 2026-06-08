"""Đặc điểm BẠN ĐỜI (vợ/chồng) qua sao chính diệu cung Phu Thê.

Kết tinh từ 32 vòng thâm nhuần Trung Châu Tử Vi Đẩu Số Q2 — Vương Đình Chỉ.
Section §5.3 (Cung Phu Thê) + §4.x (60 tinh hệ tại Phu Thê).

Output: build_partner_traits(la_so, gender) → list[dict]
  Mỗi item: {
    "tinh_he": "Tử-Tham",
    "category": "tính_cách" | "ngoại_hình" | "sự_nghiệp" | "quan_hệ",
    "trait": str,
    "warning": Optional[str],
    "source": "Trung Châu Q2 §5.3.1 p569",
  }

Paradigm gender-aware: nam mệnh xem vợ; nữ mệnh xem chồng.
"""
from __future__ import annotations
from typing import Any

from .chiem_phu_the import _find_palace, _stars_at_branch_idx


# ════════════════════════════════════════════════════════════════
# REGISTRY — đặc điểm bạn đời qua sao chính diệu Phu Thê
# Format: key = (sao1, sao2 or None, branch_idx or None or "X")
# value = list of trait dicts
# ════════════════════════════════════════════════════════════════

# Branch index: 0=Tý, 1=Sửu, 2=Dần, 3=Mão, 4=Thìn, 5=Tỵ,
#               6=Ngọ, 7=Mùi, 8=Thân, 9=Dậu, 10=Tuất, 11=Hợi

# ─── TỬ VI tại Phu Thê ────────────────────────────────────────
TU_VI_TRAITS = {
    # Tử Vi độc tọa Tý/Ngọ
    "Tử Vi_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời có khí chất 'Đế tinh' — địa vị cao, tự tin, tính ĐỘC ĐOÁN",
            "source": "Trung Châu Q2 §5.3.1 p568",
        },
        {
            "category": "quan_hệ",
            "trait": "CÓ KHUYNH HƯỚNG CHI PHỐI mệnh tạo — về tinh thần hoặc tiền bạc",
            "warning": "Nếu kết cấu 'tại dã cô quân' hoặc 'vô đạo' → bạn đời tính BẠO NGƯỢC",
            "source": "Trung Châu Q2 §5.3.1 p568",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Nam mệnh: VỢ NÊN CÓ SỰ NGHIỆP RIÊNG. Nếu ở nhà nhiều → 'không chế chồng' (tài lãnh đạo phát huy vào quan hệ gia đình)",
            "gender": "nam",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tuổi_tác",
            "trait": "Nữ mệnh 'tại dã cô quân/vô đạo' → cần KẾT HÔN MUỘN sau 30 tuổi, kết hôn sớm dễ trắc trở",
            "gender": "nữ",
            "source": "Trung Châu Q2 p572",
        },
    ],
    # Tử-Phá Sửu/Mùi
    "Tử Vi+Phá Quân_1_7": [
        {
            "category": "quan_hệ",
            "trait": "Trước hôn nhân CÓ SÓNG GIÓ, TRẮC TRỞ; nếu vốn không ổn định → dễ LY DỊ",
            "warning": "Gặp 'sao lẻ' phụ-tá → thường có NGƯỜI THỨ BA xen vào",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Vợ chồng cùng sáng lập sự nghiệp tay trắng làm nên (nếu 'bách quan triều củng')",
            "source": "Trung Châu Q2 p571",
        },
    ],
    # Tử-Phủ Dần/Thân
    "Tử Vi+Thiên Phủ_2_8": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời ổn định, có chí tiến thủ",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "tuổi_tác",
            "trait": "Có Thiên Thọ đồng độ — nam nên lấy vợ NHỎ TUỔI, nữ nên lấy chồng LỚN TUỔI",
            "source": "Trung Châu Q2 p569",
        },
        {
            "category": "quan_hệ",
            "trait": "Lộc Tồn đồng → bạn đời ÍCH KỶ, có khuynh hướng chi phối",
            "warning": "Không có cát phụ tá → dễ sinh ngoại tình tại lưu niên Liêm/Tướng/Đồng/Cơ Phu Thê",
            "source": "Trung Châu Q2 p569-570",
        },
    ],
    # Tử-Tham Mão/Dậu
    "Tử Vi+Tham Lang_3_9": [
        {
            "category": "tính_cách",
            "trait": "Tinh hệ THUẦN DỤC VỌNG. Phân biệt 2 loại: VẬT CHẤT (chí tiến thủ) vs DỤC TÌNH (dễ ngoại tình)",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Có cát tinh → vợ chồng cùng sáng nghiệp, NHƯNG VỢ/CHỒNG LÀ NHÂN VẬT CHÍNH (chủ sở hữu / đứng tên pháp lý)",
            "source": "Trung Châu Q2 p569",
        },
        {
            "category": "tinh_thần",
            "trait": "Bạn đời có khuynh hướng THẦN BÍ TÔN GIÁO (Tham Lang sinh hoạt tinh thần)",
            "source": "Trung Châu Q2 p531",
        },
        {
            "category": "quan_hệ",
            "warning": "Liêm Trinh Hóa Kỵ hội → bạn đời THÔNG MINH NHƯNG DỄ THẤT CHÍ, ưa cảm giác kích thích",
            "trait": "Liêm Trinh Hóa Lộc hội → bạn đời KHÔNG LO LẮNG CHO GIA ĐÌNH (chỉ lo công việc)",
            "source": "Trung Châu Q2 p569",
        },
    ],
    # Tử-Tướng Thìn/Tuất
    "Tử Vi+Thiên Tướng_4_10": [
        {
            "category": "tuổi_tác",
            "trait": "Nam nên lấy vợ NHỎ TUỔI hơn (có thể đến 12 tuổi); nữ nên lấy chồng LỚN TUỔI 8-12 tuổi",
            "warning": "Nếu 'vô tình' → vợ chồng cần CHÊNH LỆCH TUỔI TÁC nhiều mới khỏi sinh ly",
            "source": "Trung Châu Q2 §5.3.1 p570",
        },
        {
            "category": "lịch_sử",
            "trait": "Nên lấy NGƯỜI ĐÃ TỪNG KẾT HÔN (tái hôn / li dị / góa) — gặp 'sao lẻ' phụ-tá càng đúng",
            "source": "Trung Châu Q2 p570",
        },
        {
            "category": "sức_khỏe",
            "warning": "'Vô tình' + sát tinh xung khởi → đề phòng BẠN ĐỜI ĐỘT NHIÊN BỆNH",
            "source": "Trung Châu Q2 p570",
        },
    ],
    # Tử-Thất Tỵ/Hợi
    "Tử Vi+Thất Sát_5_11": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời LỘNG QUYỀN, mạnh mẽ",
            "source": "Trung Châu Q2 §5.3.1 p571",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Phụ-tá cát → bạn đời có SỰ NGHIỆP LỚN — nhưng vợ chồng GẶP NHAU ÍT, XA NHAU NHIỀU (hoặc ở chung nhưng quan hệ xa cách)",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tài_chính",
            "trait": "Hỏa-Linh Tham hội → bạn đời ĐỘT NHIÊN PHÁT ĐẠT",
            "warning": "Đào hoa hội → bạn đời ĐỘT NHIÊN THAY LÒNG ĐỔI DẠ",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tuổi_tác",
            "trait": "Nên KẾT HÔN MUỘN",
            "source": "Trung Châu Q2 p571",
        },
    ],
}

# ─── THIÊN CƠ tại Phu Thê ─────────────────────────────────────
THIEN_CO_TRAITS = {
    "Thiên Cơ_X_single": [
        {
            "category": "quan_hệ",
            "trait": "Về cơ bản BẤT LỢI — vợ chồng bằng mặt mà không bằng lòng",
            "warning": "Cơ Hóa Kỵ / Cự Hóa Kỵ → tính cách KHÔNG HỢP, dễ thay lòng đổi dạ",
            "source": "Trung Châu Q2 §5.3.2 p572",
        },
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng nên CHÊNH LỆCH TUỔI TÁC, kết hôn muộn",
            "source": "Trung Châu Q2 p572",
        },
    ],
    "Thiên Cơ+Thái Âm_2_8": [
        {
            "category": "ngoại_hình",
            "trait": "Nam mệnh: VỢ XINH ĐẸP, giỏi nội trợ",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.2 p573",
        },
        {
            "category": "tính_cách",
            "trait": "Nữ mệnh: cần ĐỀ PHÒNG dễ bị người khác giới để ý",
            "gender": "nữ",
            "source": "Trung Châu Q2 p573",
        },
        {
            "category": "tâm_lý",
            "warning": "Đồng Hóa Kỵ + Không-Kiếp/Hư/Hao → bạn đời TÂM CHÍ BẠC NHƯỢC, quá mẫn cảm → dễ sóng gió hôn nhân",
            "source": "Trung Châu Q2 p573",
        },
    ],
    "Thiên Cơ+Cự Môn_3_9": [
        {
            "category": "quan_hệ",
            "trait": "Cần sao Lộc mới sống đến bạc đầu. Sau kết hôn liền có sóng gió, trải qua mới sống ấm",
            "warning": "Cơ Hóa Kỵ → DỄ YÊU NGƯỜI ĐÃ CÓ GIA ĐÌNH",
            "source": "Trung Châu Q2 §5.3.2 p573",
        },
        {
            "category": "lịch_sử",
            "warning": "Cự Hóa Kỵ → có NỖI KHỔ ĐAU THẦM KÍN về tình cảm. Gặp sát → 2 LẦN KẾT HÔN",
            "source": "Trung Châu Q2 p574",
        },
    ],
    "Thiên Cơ+Thiên Lương_4_10": [
        {
            "category": "tuổi_tác",
            "trait": "KẾT HÔN MUỘN, hoặc trước hôn nhân có sóng gió trong tình yêu",
            "source": "Trung Châu Q2 §5.3.2 p574",
        },
        {
            "category": "lịch_sử",
            "trait": "Trước hôn nhân CÓ MỘT LẦN LÌA BIỆT, gặp lại nhau mới sống đến bạc đầu",
            "source": "Trung Châu Q2 p574",
        },
    ],
}

# ─── THÁI DƯƠNG tại Phu Thê ──────────────────────────────────
THAI_DUONG_TRAITS = {
    "Thái Dương_0_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời có tính SOI BÓI BỚI MÓC (đặc biệt khi gặp Hỏa-Linh)",
            "source": "Trung Châu Q2 §5.3.3 p575",
        },
        {
            "category": "quan_hệ",
            "warning": "Thái Dương Hóa Kỵ Tý + Địa Không/Kiếp → NỮ mệnh SỚM LÀM QUẢ PHỤ; nam SAU 30 tuổi dễ thay lòng",
            "gender_specific": True,
            "source": "Trung Châu Q2 p575-576",
        },
    ],
    "Thái Dương_6_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời GIỎI GIANG, CÓ TRÁCH NHIỆM",
            "source": "Trung Châu Q2 §5.3.3 p576",
        },
        {
            "category": "lịch_sử",
            "trait": "Sát tinh đồng → ngày đêm BÔN BA, BẬN RỘN BÊN NGOÀI, ít hưởng vui gia đình",
            "source": "Trung Châu Q2 p576",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Nam mệnh thời cổ → nhờ GIA ĐÌNH VỢ mà được quý; thời hiện đại → vợ có sự nghiệp tốt",
            "gender": "nam",
            "source": "Trung Châu Q2 p576",
        },
    ],
    "Thái Dương+Thái Âm_1_7": [
        {
            "category": "quan_hệ",
            "trait": "Nam mệnh cát + sinh đêm → VỢ HIẾP ĐÁP CHỒNG (đặc biệt cung Sửu)",
            "warning": "Sát-kỵ-hình → VÌ VỢ PHÁ GIA (cung Sửu, sinh đêm nặng nhất)",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.3 p576",
        },
        {
            "category": "tài_chính",
            "trait": "Âm Hóa Lộc → ĐƯỢC NHÀ VỢ TRỢ LỰC, vợ giỏi nội trợ",
            "gender": "nam",
            "source": "Trung Châu Q2 p577",
        },
        {
            "category": "tính_cách",
            "warning": "Nữ + Thái Dương Hóa Kỵ → CHỒNG NHIỀU NẠN TAI BỆNH TẬT, có sát → hình khắc / sinh ly",
            "gender": "nữ",
            "source": "Trung Châu Q2 p577",
        },
    ],
    "Thái Dương+Cự Môn_2_8": [
        {
            "category": "nguồn_gốc",
            "trait": "Hóa Lộc/Quyền → KẾT HÔN VỚI NGƯỜI NGOẠI QUỐC (hoặc người ở phương xa)",
            "source": "Trung Châu Q2 p577",
        },
        {
            "category": "lịch_sử",
            "trait": "Cát hóa + Phúc Đức không cát → nữ rời quê hương lấy chồng theo chồng; nam Ở RỂ",
            "source": "Trung Châu Q2 p577",
        },
    ],
    "Thái Dương+Thiên Lương_3_9": [
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng tuổi tác CHÊNH LỆCH; có Thiên Thọ chênh càng nhiều. Vợ có thể LỚN HƠN CHỒNG",
            "source": "Trung Châu Q2 §5.3.3 p577",
        },
        {
            "category": "lịch_sử",
            "trait": "Sóng gió trắc trở trước hôn nhân, hoặc BẠN CŨ GẶP LẠI NHAU rồi lấy nhau",
            "source": "Trung Châu Q2 p578",
        },
    ],
}

# ─── VŨ KHÚC tại Phu Thê ─────────────────────────────────────
VU_KHUC_TRAITS = {
    "Vũ Khúc+Thiên Phủ_0_6": [
        {
            "category": "sự_nghiệp",
            "trait": "Vũ Hóa Lộc + nam → VỢ CÓ NĂNG LỰC LÀM VIỆC GIỎI HƠN CHỒNG",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.4 p580",
        },
        {
            "category": "quan_hệ",
            "warning": "Thất Sát đối + Lộc Tồn đồng → tình hình 'VỢ ĐOẠT QUYỀN CHỒNG' càng nghiêm trọng. Nam có Hỏa-Linh Mệnh → Ở RỂ",
            "gender": "nam",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "tính_cách",
            "warning": "Vũ Hóa Kỵ + nữ → HÔN NHÂN GIỮA CHỪNG ĐỨT ĐOẠN (chồng mắc bệnh hoặc thay lòng)",
            "gender": "nữ",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "lịch_sử",
            "warning": "Sao lẻ phụ-tá → MẠNG TÁI HÔN. Đào hoa hội → sau kết hôn vẫn bị người đã có gia đình theo đuổi (nữ nặng hơn)",
            "source": "Trung Châu Q2 p580",
        },
    ],
    "Vũ Khúc+Tham Lang_1_7": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời KEO KIỆT, BỦN XỈN, xem nặng tiền bạc, kiểm soát tiền bạc của mệnh tạo",
            "warning": "Lộc Tồn/Hóa Lộc hội → KHÔNG đúng — chồng giàu sung túc / vợ tự kinh doanh",
            "source": "Trung Châu Q2 §5.3.4 p580",
        },
        {
            "category": "quan_hệ",
            "warning": "Hỏa-Linh đồng → tình cảm vợ chồng TRƯỚC NỒNG ẤM SAU NGUỘI LẠNH. Đào hoa tụ → trước+sau hôn nhân đều rắc rối tình cảm",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "lịch_sử",
            "warning": "Hóa Kỵ → vì bạn đời mà PHÁ TÀI. Khoa văn/đào hoa → THAY LÒNG ĐỔI DẠ. Không-Kiếp → KHÔNG có LẠC THÚ KHUÊ PHÒNG / TÁI HÔN",
            "source": "Trung Châu Q2 p580",
        },
    ],
}


# ════════════════════════════════════════════════════════════════
# BUILDER
# ════════════════════════════════════════════════════════════════

ALL_REGISTRIES = [
    TU_VI_TRAITS,
    THIEN_CO_TRAITS,
    THAI_DUONG_TRAITS,
    VU_KHUC_TRAITS,
]


def _stars_at_named_palace(la_so: dict, palace_name: str) -> dict[str, list[str]]:
    pal = _find_palace(la_so, palace_name)
    if not pal:
        return {"chinh_tinh": []}
    return _stars_at_branch_idx(la_so, pal["branch_index"])


def _palace_branch_idx(la_so: dict, palace_name: str) -> int | None:
    pal = _find_palace(la_so, palace_name)
    return pal["branch_index"] if pal else None


def _gender_norm(gender: str) -> str:
    g = (gender or "nam").lower().strip()
    return "nữ" if g in ("nu", "nữ") else "nam"


def _match_traits_key(key: str, chinh_tinh: list[str], branch_idx: int | None) -> bool:
    """Match key format:
    - "Sao1_idx_single" — sao đơn tại branch idx (X = any)
    - "Sao1+Sao2_idx1_idx2" — sao đôi tại idx1 OR idx2
    - "Sao1+Sao2_idx_idx" — same idx
    """
    parts = key.split("_")
    if "single" in parts:
        # "Sao_idx_single"
        star = parts[0]
        idx_str = parts[1] if len(parts) >= 3 else "X"
        if not any(star in s for s in chinh_tinh):
            return False
        if idx_str == "X":
            return True
        try:
            return branch_idx == int(idx_str)
        except ValueError:
            return False
    # Sao đôi
    star_part = parts[0]  # "Sao1+Sao2"
    if "+" not in star_part:
        return False
    s1, s2 = star_part.split("+", 1)
    if not (any(s1 in c for c in chinh_tinh) and any(s2 in c for c in chinh_tinh)):
        return False
    # Match branch
    idx_strs = parts[1:]
    if not idx_strs:
        return True
    try:
        valid_idxs = {int(x) for x in idx_strs}
    except ValueError:
        return True
    return branch_idx in valid_idxs


def build_partner_traits(la_so: dict, gender: str = "nam") -> dict[str, Any]:
    """Build paradigm "Đặc điểm Bạn Đời" từ sao chính diệu cung Phu Thê.

    Returns:
        {
            "role": "vợ" or "chồng",
            "phu_the_branch": "Mão",
            "phu_the_chinh_tinh": ["Tử Vi", "Tham Lang"],
            "phu_the_phu_tinh": [...],
            "tinh_he": "Tử-Tham",
            "traits": [
                {"category": "tính_cách", "trait": "...", "source": "...", "warning": "..."},
                ...
            ],
            "matched_keys": ["Tử Vi+Tham Lang_3_9", ...],
        }
    """
    gender_n = _gender_norm(gender)
    role = "vợ" if gender_n == "nam" else "chồng"

    pt_stars = _stars_at_named_palace(la_so, "Phu Thê")
    chinh_tinh = pt_stars.get("chinh_tinh", [])
    phu_tinh = pt_stars.get("phu_tinh", [])
    branch_idx = _palace_branch_idx(la_so, "Phu Thê")

    # Tinh hệ label
    tinh_he = "+".join(chinh_tinh) if chinh_tinh else "Vô chính diệu"

    traits = []
    matched_keys = []
    for registry in ALL_REGISTRIES:
        for key, trait_list in registry.items():
            if _match_traits_key(key, chinh_tinh, branch_idx):
                matched_keys.append(key)
                for trait in trait_list:
                    # Filter by gender if specified
                    trait_gender = trait.get("gender")
                    if trait_gender and trait_gender != gender_n:
                        continue
                    # Append a flat copy
                    item = {
                        "category": trait.get("category", "khác"),
                        "trait": trait.get("trait", ""),
                        "source": trait.get("source", "Trung Châu Q2"),
                    }
                    if trait.get("warning"):
                        item["warning"] = trait["warning"]
                    traits.append(item)

    # Branches Vietnamese
    BRANCH_NAMES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
                    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    branch_name = BRANCH_NAMES[branch_idx] if branch_idx is not None and 0 <= branch_idx < 12 else "?"

    return {
        "role": role,
        "gender_input": gender_n,
        "phu_the_branch": branch_name,
        "phu_the_branch_idx": branch_idx,
        "phu_the_chinh_tinh": chinh_tinh,
        "phu_the_phu_tinh": phu_tinh,
        "tinh_he": tinh_he,
        "traits": traits,
        "matched_keys": matched_keys,
        "summary": (
            f"{len(traits)} đặc điểm {role} (cấu hình {tinh_he} tại cung {branch_name})"
            if traits
            else f"Chưa có paradigm khớp cho cấu hình {tinh_he} tại {branch_name}"
        ),
        "note": (
            f"Đặc điểm bạn đời ({role} của mệnh tạo) trích từ Trung Châu Tử Vi Đẩu Số Q2 "
            f"(Vương Đình Chỉ) — §5.3 Cung Phu Thê. Paradigm 'đọc đồng dạng' không predict cứng."
        ),
    }
