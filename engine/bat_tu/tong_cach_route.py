"""Tòng Cách Routing — 4 path khi Day Master CỰC ĐOAN không thể phù-ức bình thường.

Anh duyệt 2026-06-02 (sau thâm nhuần TTT chương 17): Engine `phu_uc_route` chỉ
giải quyết Phù-Ức bậc 1. TTT dạy bậc 2 = TÒNG CÁCH khi DM quá yếu KHÔNG phù được.

Paradigm CỐT (Nhậm Thiết Tiều, TTT chương 17, dòng 2505):
> "Vượng cực không thể tốn, suy cực không thể sinh — tức vượng cực, suy cực vậy."

4 PATH TÒNG:
1. TÒNG TÀI — DM vô căn + Tài cực vượng (lộ Can) → tòng theo Tài
2. TÒNG SÁT — DM cô yếu + Quan Sát cực vượng → tòng theo Sát
3. TÒNG VƯỢNG — DM + Tỷ Kiếp vượng + không có Tài Quan chế → tòng theo khí vượng
4. TÒNG CƯỜNG — Ấn + Kiếp đều vượng (Mẹ + Anh em mạnh) → tòng theo cường thần

Detect logic (verified từ 5 case TTT chương 17):
- DM score thông căn = 0 (hư phù) + 1 hành dominant cực vượng → Tòng
- Có Ấn + Kiếp đều vượng → Tòng Cường
- Có Tỷ Kiếp vượng, KHÔNG có Tài Quan → Tòng Vượng
- Áp lực Tài >= 3.5 + DM hư phù → Tòng Tài
- Áp lực Quan Sát >= 3.5 + DM cô yếu → Tòng Sát

⚠️ Iron Rule #4+6: Tòng KHÔNG dự đoán "thuận theo dòng đời" tĩnh —
chỉ là cấu trúc khí cực đoan, hành động vẫn của anh.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── 4 PATHS TÒNG ────────────────────────────────────────────────────────────

PATH_TONG_TAI = {
    "path_id": "TÒNG_TÀI",
    "ten_viet": "Tòng Tài (theo Tiền Của)",
    "condition": "Day Master vô căn + Tài cực vượng + lộ Can",
    "dung_than": ["Thực Thần", "Thương Quan", "Chính Tài", "Thiên Tài"],
    "ky_than": ["Tỷ Kiên", "Kiếp Tài", "Chính Ấn", "Thiên Ấn"],
    "ly_do_sach": (
        "Day Master quá yếu, không có gốc trong Địa Chi. Tài cực vượng đến mức "
        "Tỷ Kiếp đến cũng không đoạt nổi, Ấn đến cũng bị Tài khắc tan. "
        "Đành tòng theo Tài — thuận theo dòng tài lực. Dụng Thực Thương sinh Tài + "
        "Tài bản thân làm dụng. Kỵ Tỷ Kiếp đoạt Tài (vô vọng) + Ấn (bị Tài khắc)."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (case 116)",
            "dong": 2474,
            "noi_dung": (
                "Nhật chủ quá nhược, trong mệnh cục thực tài quan đã vượng. "
                "Thành cách tòng thủy. Dụng thân mộc, gặp mộc vận (tài vận) thì tốt, "
                "gặp thủy vận (thực thương vận) trung bình, hỏa vận cũng kém; "
                "gặp thổ kim vận là đại họa."
            ),
        },
        {
            "sach": "Trích Thiên Tủy bình chú (case 119)",
            "dong": 2489,
            "noi_dung": (
                "Nhật chủ quá nhược, mộc hỏa vượng, trên can lại thấu mộc hỏa. "
                "Thành cách tòng tài. Vận thực thương tài thì tốt, "
                "quan sát vận trung bình."
            ),
        },
    ],
    "hanh_dong": [
        "Thuận theo dòng tiền — không gồng giữ độc lập tài chính",
        "Tham gia kinh doanh / nhận đầu tư / hợp tác tài chính",
        "Tránh đu đồng đạo cùng tranh ăn (Tỷ Kiếp đoạt Tài)",
        "Tránh ôm thủ học vấn lý thuyết (Ấn bị Tài khắc)",
    ],
}

PATH_TONG_SAT = {
    "path_id": "TÒNG_SÁT",
    "ten_viet": "Tòng Sát (theo Quyền Lực)",
    "condition": "Day Master cô yếu vô căn + Quan Sát cực vượng",
    "dung_than": ["Chính Tài", "Thiên Tài", "Chính Quan", "Thất Sát"],
    "ky_than": ["Chính Ấn", "Thiên Ấn", "Tỷ Kiên", "Kiếp Tài"],
    "ly_do_sach": (
        "Day Master quá yếu không cứu được, Quan Sát mạnh đến mức Ấn tới cũng không "
        "hóa nổi (vì Ấn còn bị Tài khắc trước). Đành tòng theo Sát — thuận theo quyền lực. "
        "Dụng Tài sinh Sát + Sát làm dụng. Kỵ Ấn (vì Ấn hóa Sát = phản đồ với cường thần) "
        "+ Tỷ Kiếp (chống Sát = đối đầu vô lực)."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (case 108)",
            "dong": 2406,
            "noi_dung": (
                "Chỉ có thủy vượng, trên lại lộ sát, nhật chủ cô yếu vô căn. "
                "Thành cách tòng sát."
            ),
        },
        {
            "sach": "Trích Thiên Tủy bình chú (case 103)",
            "dong": 2343,
            "noi_dung": (
                "Trụ này Nhật chủ quá nhược, sát vượng nên tòng sát. "
                "Gặp vận Thổ, Kim tức vận Tài, Quan là cát vận."
            ),
        },
    ],
    "hanh_dong": [
        "Thuận theo quyền lực — gia nhập tổ chức lớn, làm việc dưới trướng",
        "Tài sinh Sát = dùng tiền để xây quan hệ với người quyền lực",
        "Tránh ôm độc lập đối đầu (Tỷ Kiếp chống Sát = thất bại)",
        "Tránh ôm học vấn lý thuyết cứu mình (Ấn vô vọng trước Tài-Sát)",
    ],
}

PATH_TONG_VUONG = {
    "path_id": "TÒNG_VƯỢNG",
    "ten_viet": "Tòng Vượng (theo Đồng Đạo)",
    "condition": "Day Master + Tỷ Kiếp vượng + không có Tài Quan chế",
    "dung_than": ["Tỷ Kiên", "Kiếp Tài", "Thực Thần", "Thương Quan"],
    "ky_than": ["Chính Tài", "Thiên Tài", "Chính Quan", "Thất Sát"],
    "ly_do_sach": (
        "Day Master vượng + Tỷ Kiếp trùng điệp, KHÔNG có Tài Quan để chế tiết. "
        "Khí thuần một hành, không thể đối nghịch — đành tòng theo khí vượng. "
        "Dụng Tỷ Kiếp + Thực Thương phát tiết. Kỵ Tài Quan (đối đầu vô lực với cường thần)."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (case 117)",
            "dong": 2479,
            "noi_dung": (
                "Trụ này thành cách tòng vượng, do trong mệnh cục kiếp vượng, "
                "ấn suy lại có thực thương. Gặp mộc vận (thực thương vận) là tốt nhất, "
                "kế đến là kiếp vận. Ấn vận trung bình."
            ),
        },
    ],
    "hanh_dong": [
        "Phát triển trong cộng đồng đồng đạo cùng tần số",
        "Phát tiết qua sáng tạo / dạy học / xuất bản (Thực Thương)",
        "Tránh cạnh tranh quyền lực với người ngoài (Quan Sát)",
        "Tránh ép kiếm tiền (Tài bị Kiếp đoạt vô lợi)",
    ],
}

PATH_TONG_CUONG = {
    "path_id": "TÒNG_CƯỜNG",
    "ten_viet": "Tòng Cường (theo Mẹ + Anh Em)",
    "condition": "Ấn + Kiếp đều vượng (Mẹ + Anh Em đều mạnh)",
    "dung_than": ["Chính Ấn", "Thiên Ấn", "Tỷ Kiên", "Kiếp Tài"],
    "ky_than": ["Thực Thần", "Thương Quan", "Chính Tài", "Thiên Tài", "Chính Quan", "Thất Sát"],
    "ly_do_sach": (
        "Mệnh có Ấn + Kiếp đều cực vượng — như được mẹ + anh em cùng nâng đỡ. "
        "Tòng theo cường thần này. Dụng Ấn + Tỷ Kiếp. Kỵ Thực Thương (vì Kiêu Thần Ấn "
        "gặp Thực Thần sẽ đoạt = phản đồ) + Tài Quan (đối đầu cường thần)."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (case 106)",
            "dong": 2380,
            "noi_dung": (
                "Trụ này Ấn Kiếp đều vượng, thành cách tòng cường. "
                "Nên dụng thần là Ấn Kiếp. Tuyệt đối không nên gặp vận Thực Tài Quan, "
                "thất bại như vôi."
            ),
        },
        {
            "sach": "Trích Thiên Tủy bình chú (case 114)",
            "dong": 2441,
            "noi_dung": (
                "Trụ này thành cách Tòng Cường (do Ấn vượng, Kiếp vượng). "
                "Dụng thần Kiếp Ấn (thổ kim)."
            ),
        },
    ],
    "hanh_dong": [
        "Phát triển dựa vào học vấn + đồng đạo (cả Ấn + Tỷ)",
        "Tu học sâu, kết nối thầy + bạn đạo cùng đường",
        "Tránh phát tiết quá đà (Thực Thương) — sẽ bị Kiêu đoạt",
        "Tránh kinh doanh lớn / quyền lực ngoài (Tài Quan đối đầu cường thần)",
    ],
}


ALL_TONG_PATHS = [PATH_TONG_TAI, PATH_TONG_SAT, PATH_TONG_VUONG, PATH_TONG_CUONG]


@dataclass
class TongResult:
    """Kết quả routing Tòng Cách. Nếu không phải Tòng → is_tong=False."""

    is_tong: bool
    day_master_stem: str
    day_master_element: str
    path_id: str = ""              # "" nếu không phải Tòng
    ten_viet: str = ""
    condition: str = ""
    dung_than: list[str] = field(default_factory=list)
    dung_than_elements: list[str] = field(default_factory=list)
    ky_than: list[str] = field(default_factory=list)
    ky_than_elements: list[str] = field(default_factory=list)
    ly_do_sach: str = ""
    trich_dan: list[dict] = field(default_factory=list)
    hanh_dong: list[str] = field(default_factory=list)
    sach_nguon: list[str] = field(default_factory=list)
    not_tong_reason: str = ""      # Lý do không phải Tòng (khi is_tong=False)

    def to_dict(self) -> dict:
        return asdict(self)


def _detect_tong(thong_can_score: float, pressure: dict) -> tuple[bool, str, str]:
    """Detect xem lá số có vào Tòng Cách không.

    Returns: (is_tong, path_id, reason)
    """
    tai = pressure.get("tài", 0)
    quan = pressure.get("quan_sát", 0)
    thuc = pressure.get("thực_thương", 0)
    an = pressure.get("ấn", 0)
    ty = pressure.get("tỷ", 0)

    # Điều kiện CHUNG cho 3 Tòng đầu: Day Master phải hư phù hoặc cô yếu
    # Tòng Cường khác — DM mạnh + Ấn Kiếp đều vượng (không cần DM yếu)
    dm_too_weak = thong_can_score < 1.5

    # Path 4: Tòng Cường — Ấn + Kiếp đều vượng (DM thường VƯỢNG, không cần yếu)
    # Paradigm TTT case 106, 114: DM vượng + Ấn + Kiếp đều cực vượng + không Tài Quan/Thực Thương
    # Check trước vì có thể match với DM mạnh (priority cao hơn Tòng Vượng)
    # Threshold: tổng Ấn+Kiếp >= 4.5 (mỗi cái ~2.4 thường gặp) + đối phương yếu
    pho_tro_total = an + ty
    chong_pho_total = tai + quan + thuc
    if (pho_tro_total >= 4.5 and an >= 2.0 and ty >= 2.0
            and chong_pho_total <= 2.0):
        return True, "TÒNG_CƯỜNG", (
            f"Ấn ({an:.1f}) + Kiếp ({ty:.1f}) = {pho_tro_total:.1f}, "
            f"Tài+Quan+Thực Thương = {chong_pho_total:.1f}. "
            f"Cường thần đẩy DM lên cực vượng."
        )

    # Path 1: Tòng Tài — DM hư phù + Tài cực vượng
    if dm_too_weak and tai >= 3.5 and tai > quan:
        # Verify Ấn không đủ cứu
        if an < 1.5:
            return True, "TÒNG_TÀI", f"DM hư phù (score={thong_can_score}) + Tài áp lực {tai:.1f} ≥ 3.5"

    # Path 2: Tòng Sát — DM hư phù + Quan Sát cực vượng
    if dm_too_weak and quan >= 3.5 and quan > tai:
        # Verify Ấn không đủ hóa Quan
        if an < 2.0:
            return True, "TÒNG_SÁT", f"DM cô yếu (score={thong_can_score}) + Quan Sát áp lực {quan:.1f} ≥ 3.5"

    # Path 3: Tòng Vượng — Kiếp vượng + không có Tài Quan (Ấn ít)
    # Khác Tòng Cường: ở đây chỉ Kiếp vượng, Ấn không vượng
    if ty >= 3.5 and tai < 1.0 and quan < 1.0 and an < 2.5:
        return True, "TÒNG_VƯỢNG", f"Tỷ Kiếp áp lực {ty:.1f} ≥ 3.5, không có Tài Quan chế, Ấn không vượng"

    # Không phải Tòng
    reasons = []
    if not dm_too_weak:
        reasons.append(f"DM có gốc (score={thong_can_score})")
    if tai < 3.5 and quan < 3.5 and ty < 3.5 and an < 2.5:
        reasons.append("không có hành nào cực vượng")
    if an >= 1.5 and tai >= 3.5:
        reasons.append("Ấn còn đủ cứu thân (không đến mức Tòng Tài)")
    return False, "", "; ".join(reasons) or "Không khớp condition Tòng"


def _resolve_element(thap_than: str, day_master_element: str) -> str:
    """Resolve Thập Thần → element."""
    from .phu_uc_route import ELEMENT_RELATION
    rel = ELEMENT_RELATION.get(day_master_element, {})
    if "Tỷ" in thap_than or "Kiếp" in thap_than:
        return rel.get("tỷ", "")
    elif "Ấn" in thap_than or "Kiêu" in thap_than:
        return rel.get("ấn", "")
    elif "Tài" in thap_than:
        return rel.get("tài", "")
    elif "Quan" in thap_than or "Sát" in thap_than:
        return rel.get("quan_sát", "")
    elif "Thực" in thap_than or "Thương" in thap_than:
        return rel.get("thực_thương", "")
    return ""


def route_tong_cach(tu_tru: dict) -> TongResult:
    """Routing chính Tòng Cách. Return is_tong=False nếu không phải Tòng.

    Args: tu_tru với pillars
    Returns: TongResult
    """
    from .phu_uc_route import STEM_ELEMENT, _count_pressure
    from .thong_can import summarize_day_master_thong_can

    pillars = tu_tru["pillars"]
    day_master_stem = pillars["day"]["stem"]
    day_master_element = STEM_ELEMENT.get(day_master_stem, "?")

    # Thông căn
    tc_summary = summarize_day_master_thong_can(pillars)
    thong_can_score = tc_summary.get("score", 0)

    # Pressure
    pressure = _count_pressure(pillars, day_master_element)

    # Detect Tòng?
    is_tong, path_id, reason = _detect_tong(thong_can_score, pressure)

    if not is_tong:
        return TongResult(
            is_tong=False,
            day_master_stem=day_master_stem,
            day_master_element=day_master_element,
            not_tong_reason=reason,
        )

    # Resolve path
    path_map = {
        "TÒNG_TÀI": PATH_TONG_TAI,
        "TÒNG_SÁT": PATH_TONG_SAT,
        "TÒNG_VƯỢNG": PATH_TONG_VUONG,
        "TÒNG_CƯỜNG": PATH_TONG_CUONG,
    }
    path = path_map[path_id]

    dung_elements = [
        e for e in (_resolve_element(dt, day_master_element) for dt in path["dung_than"])
        if e
    ]
    ky_elements = [
        e for e in (_resolve_element(kt, day_master_element) for kt in path["ky_than"])
        if e
    ]

    return TongResult(
        is_tong=True,
        day_master_stem=day_master_stem,
        day_master_element=day_master_element,
        path_id=path["path_id"],
        ten_viet=path["ten_viet"],
        condition=path["condition"],
        dung_than=path["dung_than"],
        dung_than_elements=list(dict.fromkeys(dung_elements)),  # unique preserve order
        ky_than=path["ky_than"],
        ky_than_elements=list(dict.fromkeys(ky_elements)),
        ly_do_sach=path["ly_do_sach"],
        trich_dan=path["trich_dan"],
        hanh_dong=path["hanh_dong"],
        sach_nguon=["Trích Thiên Tủy bình chú (Nhậm Thiết Tiều) chương 17 — Suy Vượng"],
        not_tong_reason="",
    )


def render_tong_markdown(result: TongResult) -> str:
    """Render TongResult → markdown."""
    if not result.is_tong:
        return (
            f"## 🚫 KHÔNG PHẢI TÒNG CÁCH\n\n"
            f"Day Master {result.day_master_stem} ({result.day_master_element}) "
            f"không khớp điều kiện Tòng Cách.\n\n"
            f"**Lý do:** {result.not_tong_reason}\n\n"
            f"→ Engine route theo **Phù-Ức bình thường** (bậc 1) — "
            f"xem `phu_uc_route` cho hỉ-kỵ thần."
        )

    lines = [
        f"## 🌀 Tòng Cách — {result.ten_viet}\n",
        f"**Path:** `{result.path_id}`  ",
        f"**Day Master:** {result.day_master_stem} ({result.day_master_element.title()})  ",
        f"**Điều kiện:** {result.condition}\n",
        f"### ✅ Dụng Thần (tòng theo)",
        f"- **{' / '.join(result.dung_than)}**",
        f"- Hành: {' + '.join(result.dung_than_elements)}\n",
        f"### ❌ Kỵ Thần (đối nghịch cường thần)",
        f"- **{' / '.join(result.ky_than)}**",
        f"- Hành: {' + '.join(result.ky_than_elements)}\n",
        f"### 📚 Lý do theo Trích Thiên Tủy\n",
        f"{result.ly_do_sach}\n",
        f"### 📖 Trích nguyên văn (case study TTT)",
    ]
    for td in result.trich_dan:
        dong_str = f" (dòng {td['dong']})" if td.get("dong") else ""
        lines.append(f"\n> _{td['noi_dung']}_  ")
        lines.append(f"> — **{td['sach']}**{dong_str}")

    lines.append("\n### 🎯 Hành động cụ thể (paradigm đồng-dạng, KHÔNG predict)")
    for hd in result.hanh_dong:
        lines.append(f"- {hd}")

    lines.append("\n### 🪷 Iron Rule #4+6")
    lines.append(
        "Tòng = cấu trúc khí cực đoan. KHÔNG nghĩa 'số mệnh phải thuận'. "
        "Anh vẫn có quyền chọn — chỉ là chọn theo dòng sẽ ít kháng cự hơn."
    )
    lines.append(
        "\n_TTT chương 17 dòng 2505: 'Vượng cực không thể tốn, "
        "suy cực không thể sinh' — đảo logic._"
    )
    return "\n".join(lines)
