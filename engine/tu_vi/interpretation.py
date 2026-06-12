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

from dataclasses import asdict, dataclass, field

from . import ngu_uan as ngu_uan_mod
from .chinh_tinh import ALL_CHINH_TINH
from .mieu_vuong_ham import level_at, level_score
from .ngu_hanh_nen import sao_tai_cung


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
    polarity_score: int                  # độ-khó-bài-học score (miếu hãm + tứ hóa)
    polarity_tag: str                    # 'favorable' / 'mixed' / 'challenging' / 'empty'
    main_reading: str                    # composed Vietnamese text
    star_details: list[dict]             # per-star {ten_vi, keywords, tich_cuc, tieu_cuc}
    mieu_ham: dict = field(default_factory=dict)   # {star: miếu/vượng/đắc/bình/lạc/hãm}
    ngu_uan: dict | None = None          # khối Ngũ Uẩn (Tử Vi Bôn Ba) — None nếu thiếu dataset
    ngu_hanh: list = field(default_factory=list)   # nền ngũ hành sao↔đất cung (sinh khắc)

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
            f"Cung {palace_name} Vô Chính Diệu — bối cảnh mở, như vở kịch chưa chốt "
            f"nhân vật chính: linh hoạt, dễ đổi theo môi trường, khó theo một khuôn cố định. "
            f"{frame.capitalize()} cần xét phụ tinh tại cung và toàn cục lá số để bổ nghĩa "
            "(lệ cổ đọc theo cung xung chiếu/tam hợp; trường phái hiện đại khuyên "
            "xét thêm cả các cung còn lại thay vì chỉ mượn sao)."
        )

    stars_label = " + ".join(chinh_names)
    hoa_label = ""
    if hoa_attachments:
        hoa_label = " · " + ", ".join(
            f"{a['star']} Hóa {a['hoa']}" for a in hoa_attachments
        )

    # Ngôn ngữ "độ khó bài học" — không gán nhãn cung tốt/xấu.
    prefix = ngu_uan_mod.do_kho_label(polarity_tag).capitalize()

    return (
        f"{prefix}. Sao chính: {stars_label}{hoa_label}. "
        f"Bối cảnh {palace_name} ({frame})."
    )


def interpret_palace(
    palace_name: str,
    branch: str,
    chinh_at_palace: list[str],
    tu_hoa: dict[str, str],
    reminder_seed: int = 0,
) -> PalaceReading:
    """Build reading for one palace.

    Args:
        palace_name: e.g. 'Mệnh', 'Tài Bạch', ...
        branch: Vietnamese branch name (e.g. 'Tý').
        chinh_at_palace: list of chính tinh names present in this palace.
        tu_hoa: {Lộc/Quyền/Khoa/Kỵ → star_name} for the year.
        reminder_seed: xoay vòng lời nhắc paradigm (thường = index cung).
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

    # Độ-khó-bài-học score: miếu/vượng/đắc/bình/lạc/hãm của sao TẠI CHI này
    # (paradigm: không có sao tốt/sao xấu — chỉ có độ khó của bài học;
    #  bảng Q2 "Thập nhị cung Miếu Vượng Lạc Hãm đồ").
    score = 0
    mieu_ham: dict[str, str] = {}
    for s in chinh_at_palace:
        level = level_at(s, branch)
        if level:
            mieu_ham[s] = level
            score += level_score(level)
    for h in hoa_attachments:
        score += HOA_POLARITY.get(h["hoa"], 0)

    _, polarity_tag = _polarity_from_score(score, len(chinh_at_palace))

    # Nền ngũ hành: sao đứng trên đất cung — sinh khắc + nhận định cơ chế.
    ngu_hanh_blocks = [
        b for b in (sao_tai_cung(s, branch) for s in chinh_at_palace) if b
    ]

    # Khối Ngũ Uẩn (Tử Vi Bôn Ba) — None nếu dataset chưa build.
    ngu_uan_block = ngu_uan_mod.compose_palace_ngu_uan(
        palace_name=palace_name,
        chinh_stars=chinh_at_palace,
        hoa_attachments=hoa_attachments,
        mieu_ham_levels=mieu_ham,
        polarity_tag=polarity_tag,
        reminder_seed=reminder_seed,
    )

    main_reading = ngu_uan_mod.compose_main_reading_v2(
        palace_name, chinh_at_palace, ngu_uan_block, polarity_tag,
    ) or _compose_main_reading(
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
        mieu_ham=mieu_ham,
        ngu_uan=ngu_uan_block,
        ngu_hanh=ngu_hanh_blocks,
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
    for i, p in enumerate(palaces):
        reading = interpret_palace(
            palace_name=p["name"],
            branch=p["branch"],
            chinh_at_palace=stars_by_branch[p["branch_index"]],
            tu_hoa=tu_hoa,
            reminder_seed=i,
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
        verdict = (
            "Nhiều bối cảnh thuận đà — bài học đời này phần lớn dễ vào nhịp. "
            "Lưu ý: số đẹp dễ tạo ảo tưởng an toàn; thuận mà chủ quan thì vẫn lỡ bài."
        )
    elif total_score <= -5:
        verdict = (
            "Nhiều bối cảnh có độ khó cao — không phải án phạt, mà là bộ bài tập nặng đô. "
            "Sao chỉ quyết định độ khó của bài học, không quyết định kết cục; "
            "người vượt được bài của mình thì trạng thái nào cũng thành công được."
        )
    else:
        verdict = (
            "Các bối cảnh có độ khó đan xen — nơi thuận để lấy đà, nơi khó để rèn. "
            "Đọc theo từng cung để biết bài học nào đang chờ ở bối cảnh nào."
        )

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
        "paradigm_note": (
            "Lá số là bản đồ sống theo thời gian thực, không phải bản án: nó mô tả "
            "cấu trúc phản ứng và xu hướng vận hành, còn kết quả đời người nằm ở "
            "lựa chọn lặp lại hàng ngày và mức độ tỉnh thức của chính mình."
        ),
        "note": (
            "Diễn giải v2: độ khó bài học tính theo bảng Miếu-Vượng-Lạc-Hãm (Q2) + Tứ Hóa; "
            "khối Ngũ Uẩn theo trường phái Tử Vi Bôn Ba (hiện đại VN). "
            "Phiên bản sau sẽ thêm tổng lực cụm phụ tinh + liên hệ tam hợp/xung chiếu "
            "(diễn đạt 'liên hệ giữa các bối cảnh' thay cho 'sao chiếu')."
        ),
    }
