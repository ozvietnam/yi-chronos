"""Tử Vi interpretation engine — combine star placements with chính tinh
semantics to produce per-palace readings.

Output for each of 12 palaces:
- List of stars present (chính + phụ + sát)
- Star tags (Hóa Lộc/Quyền/Khoa/Kỵ if any)
- Combined verdict (favorable / mixed / challenging / empty)
- Vietnamese reading: domain-specific tích cực + tiêu cực drawn from the
  star schema, with palace-specific framing.

Caveat: classical Tử Vi interpretation requires examining cung Mệnh against
opposite palace (Thiên Di), trio (tam hợp), and many other relations. This
v1 engine produces a baseline per-palace reading. Multi-palace synthesis
will come in v2.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .chinh_tinh import ALL_CHINH_TINH


# ─── Star semantics lookup ────────────────────────────────────────────────────

# Vietnamese name → ChinhTinh dataclass
_STAR_BY_NAME: dict[str, object] = {s.ten_vi: s for s in ALL_CHINH_TINH}


# Palace-specific framing — how each palace "asks" the star to behave.
PALACE_DOMAIN: dict[str, dict[str, str]] = {
    "Mệnh": {
        "question": "Cá tính cốt lõi + đường hướng đời người",
        "frame": "tính cách / bản chất / xu hướng hành động",
    },
    "Phụ Mẫu": {
        "question": "Quan hệ với cha mẹ + người có quyền lực phía trên",
        "frame": "cha mẹ / cấp trên / quý nhân phía trên",
    },
    "Phúc Đức": {
        "question": "Phước lành tích lũy + đời sống tinh thần",
        "frame": "phúc đức / hưởng thụ tinh thần / hậu vận",
    },
    "Điền Trạch": {
        "question": "Tài sản bất động + nhà cửa / quê quán",
        "frame": "nhà cửa / đất đai / tài sản dài hạn",
    },
    "Quan Lộc": {
        "question": "Sự nghiệp + chức vị + công danh",
        "frame": "sự nghiệp / chức vị / quyền lực",
    },
    "Nô Bộc": {
        "question": "Bạn bè + cấp dưới + người giúp việc",
        "frame": "bạn bè / cấp dưới / đồng đội",
    },
    "Thiên Di": {
        "question": "Khả năng đi xa + môi trường ngoài / thay đổi không gian",
        "frame": "di chuyển / xã giao / môi trường rộng",
    },
    "Tật Ách": {
        "question": "Sức khỏe + bệnh tật + tai ách",
        "frame": "sức khỏe / điểm yếu cơ thể / tai họa tiềm tàng",
    },
    "Tài Bạch": {
        "question": "Tiền bạc lưu thông + thu nhập + tài chính ngắn hạn",
        "frame": "tiền bạc / dòng tiền / cách kiếm tiền",
    },
    "Tử Tức": {
        "question": "Con cái + sáng tạo + sản phẩm sinh ra",
        "frame": "con cái / sáng tạo / sản phẩm",
    },
    "Phu Thê": {
        "question": "Hôn nhân + quan hệ tình cảm chính",
        "frame": "vợ / chồng / mối tình lớn",
    },
    "Huynh Đệ": {
        "question": "Anh chị em + bạn đồng môn + đối thủ ngang vai",
        "frame": "anh chị em / đồng nghiệp ngang vai",
    },
}


# Star strength tag based on hóa attachment.
HOA_TAG_LABEL: dict[str, str] = {
    "Lộc":   "Hóa Lộc — thu hoạch tốt, tài lộc thông",
    "Quyền": "Hóa Quyền — uy quyền, sức bật mạnh",
    "Khoa":  "Hóa Khoa — danh tiếng, quý nhân, học vấn",
    "Kỵ":    "Hóa Kỵ — trở ngại, ách tắc, tránh dấn sâu",
}

HOA_POLARITY: dict[str, int] = {
    "Lộc": +2, "Quyền": +1, "Khoa": +1, "Kỵ": -2,
}


@dataclass(frozen=True)
class PalaceReading:
    """Reading for one of 12 palaces."""

    palace_name: str
    branch: str
    domain_question: str
    domain_frame: str
    chinh_tinh: list[str]                # star names present
    chinh_tinh_count: int
    hoa_attachments: list[dict]          # [{star, hoa, label}]
    polarity_score: int                  # rough sentiment
    polarity_tag: str                    # 'favorable' / 'mixed' / 'challenging' / 'empty'
    main_reading: str                    # composed Vietnamese text
    star_details: list[dict]             # per-star {ten_vi, keywords, tich_cuc, tieu_cuc}

    def to_dict(self) -> dict:
        return asdict(self)


def _polarity_from_score(score: int, chinh_count: int) -> tuple[int, str]:
    """Map polarity score + star count to tag."""
    if chinh_count == 0:
        return 0, "empty"
    if score >= 2:
        return score, "favorable"
    if score <= -2:
        return score, "challenging"
    return score, "mixed"


def _compose_main_reading(
    palace_name: str,
    frame: str,
    chinh_names: list[str],
    hoa_attachments: list[dict],
    polarity_tag: str,
) -> str:
    """Compose Vietnamese reading sentence from inputs."""
    if not chinh_names:
        return (
            f"Cung {palace_name} không có chính tinh — đọc theo cung đối diện "
            f"(tam hợp). {frame.capitalize()} chịu ảnh hưởng gián tiếp; "
            "cần xét phụ tinh + sát tinh tại cung này để bổ nghĩa."
        )

    stars_label = " + ".join(chinh_names)
    hoa_label = ""
    if hoa_attachments:
        hoa_label = " · " + ", ".join(
            f"{a['star']} Hóa {a['hoa']}" for a in hoa_attachments
        )

    if polarity_tag == "favorable":
        prefix = "Lực cung mạnh, tín hiệu thuận"
    elif polarity_tag == "challenging":
        prefix = "Cung có áp lực, cần cẩn trọng"
    elif polarity_tag == "mixed":
        prefix = "Cung pha trộn — vừa có tiềm năng vừa có rủi ro"
    else:
        prefix = "Cung trầm"

    return (
        f"{prefix}. Sao chính: {stars_label}{hoa_label}. "
        f"Ý nghĩa cung {palace_name} ({frame}): xem chi tiết bên dưới."
    )


def interpret_palace(
    palace_name: str,
    branch: str,
    chinh_at_palace: list[str],
    tu_hoa: dict[str, str],
) -> PalaceReading:
    """Build reading for one palace.

    Args:
        palace_name: e.g. 'Mệnh', 'Tài Bạch', ...
        branch: Vietnamese branch name (e.g. 'Tý').
        chinh_at_palace: list of chính tinh names present in this palace.
        tu_hoa: {Lộc/Quyền/Khoa/Kỵ → star_name} for the year.
    """
    domain = PALACE_DOMAIN.get(palace_name, {"question": "", "frame": palace_name})

    # Hóa attachments where the hóa'd star sits in THIS palace.
    star_to_hoa = {star: hoa for hoa, star in tu_hoa.items()}
    hoa_attachments = []
    for s in chinh_at_palace:
        if s in star_to_hoa:
            hoa_attachments.append({
                "star": s,
                "hoa": star_to_hoa[s],
                "label": HOA_TAG_LABEL[star_to_hoa[s]],
            })

    # Polarity score.
    score = 0
    for s in chinh_at_palace:
        star = _STAR_BY_NAME.get(s)
        # Star inherent polarity heuristic: gold stars (Tử Vi, Thiên Phủ, Thiên Đồng,
        # Thái Dương đắc địa, Thái Âm đắc địa) trend positive; Thất Sát, Phá Quân,
        # Tham Lang, Cự Môn, Liêm Trinh trend mixed-to-negative.
        positive_set = {"Tử Vi", "Thiên Phủ", "Thiên Đồng", "Thiên Lương", "Thiên Tướng", "Thiên Cơ"}
        negative_set = {"Thất Sát", "Phá Quân", "Cự Môn"}
        if s in positive_set:
            score += 1
        elif s in negative_set:
            score -= 1
    for h in hoa_attachments:
        score += HOA_POLARITY.get(h["hoa"], 0)

    _, polarity_tag = _polarity_from_score(score, len(chinh_at_palace))
    main_reading = _compose_main_reading(
        palace_name, domain["frame"], chinh_at_palace, hoa_attachments, polarity_tag,
    )

    # Per-star details from the schema.
    star_details = []
    for s in chinh_at_palace:
        star = _STAR_BY_NAME.get(s)
        if star:
            star_details.append({
                "ten_vi": star.ten_vi,
                "ten_zh": star.ten_zh,
                "keywords": list(star.keywords),
                "tich_cuc": star.tich_cuc,
                "tieu_cuc": star.tieu_cuc,
                "ngu_hanh": star.ngu_hanh,
            })

    return PalaceReading(
        palace_name=palace_name,
        branch=branch,
        domain_question=domain["question"],
        domain_frame=domain["frame"],
        chinh_tinh=list(chinh_at_palace),
        chinh_tinh_count=len(chinh_at_palace),
        hoa_attachments=hoa_attachments,
        polarity_score=score,
        polarity_tag=polarity_tag,
        main_reading=main_reading,
        star_details=star_details,
    )


def interpret_la_so(la_so: dict) -> dict:
    """Build full interpretation for a complete lá số (output of cast_la_so).

    Returns:
        {
            'palace_readings': list of 12 PalaceReading dicts (Mệnh first),
            'chart_summary': overall short verdict,
            'menh_focus': dict with Mệnh details + framing,
        }
    """
    palaces = la_so["palaces"]
    chinh_tinh = la_so["chinh_tinh"]   # name → branch_index
    tu_hoa = la_so["tu_hoa"]

    # Group stars by branch_index for fast lookup.
    stars_by_branch: dict[int, list[str]] = {i: [] for i in range(12)}
    for name, idx in chinh_tinh.items():
        stars_by_branch[idx].append(name)

    readings = []
    for p in palaces:
        reading = interpret_palace(
            palace_name=p["name"],
            branch=p["branch"],
            chinh_at_palace=stars_by_branch[p["branch_index"]],
            tu_hoa=tu_hoa,
        )
        readings.append(reading.to_dict())

    # Mệnh focus
    menh_focus = readings[0]

    # Overall summary: weighted polarity across all 12 palaces.
    total_score = sum(r["polarity_score"] for r in readings)
    favorable_count = sum(1 for r in readings if r["polarity_tag"] == "favorable")
    challenging_count = sum(1 for r in readings if r["polarity_tag"] == "challenging")
    mixed_count = sum(1 for r in readings if r["polarity_tag"] == "mixed")
    empty_count = sum(1 for r in readings if r["polarity_tag"] == "empty")

    if total_score >= 5:
        verdict = "Lá số nghiêng thuận — nhiều cung có tín hiệu tốt."
    elif total_score <= -5:
        verdict = "Lá số nhiều áp lực — cần phòng vệ ở cung Tật Ách + Quan Lộc."
    else:
        verdict = "Lá số cân bằng — tốt xấu hỗn hợp, cần đọc theo từng cung."

    return {
        "palace_readings": readings,
        "menh_focus": menh_focus,
        "chart_summary": {
            "total_polarity_score": total_score,
            "favorable_palaces": favorable_count,
            "mixed_palaces": mixed_count,
            "challenging_palaces": challenging_count,
            "empty_palaces": empty_count,
            "verdict": verdict,
        },
        "note": (
            "Diễn giải v1 dựa trên ngữ nghĩa từng sao và Tứ Hóa. Phiên bản nâng cao "
            "sẽ thêm Tam Hợp (trio palace synthesis), Lục Hội (opposite-palace mirror), "
            "và cách cục patterns (Tử Vi đắc địa, Tử Phủ đồng cung, ...)."
        ),
    }
