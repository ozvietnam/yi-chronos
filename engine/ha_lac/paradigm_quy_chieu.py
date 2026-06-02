"""Paradigm Quy Chiếu — Cross-link quẻ Hà Lạc với case study sử / đời sống.

Paradigm Xuân Cang + PBC (vòng 6, p101-120):
> Mỗi quẻ + hào KHÔNG đứng một mình. Phải đối chiếu với trường hợp cụ thể
> trong sử Tàu, sử Việt, đời sống thường ngày — đó là cách "đọc đồng dạng"
> đúng nghĩa.

Module này gom các case study tìm thấy trong các sách dịch học VN
(Phan Bội Châu phụ chú + Nguyễn Hiến Lê tổng hợp) để LLM có dataset
cụ thể khi diễn giải. KHÔNG predict — chỉ tham chiếu.

Reference: Bát Tự Hà Lạc & Quỹ đạo đời người (Xuân Cang) p.100-120 (vòng 6).
"""

from __future__ import annotations


# Mỗi entry: (que, hao) → list of case studies
# Mỗi case study có: actor, situation, paradigm_lesson, source
PARADIGM_CASES: dict[tuple[str, int], list[dict]] = {
    # ===== Quẻ Tụng =====
    ("Tụng", 0): [
        {
            "actor": "Tục ngữ Việt",
            "situation": "Cái sảy nảy cái ung",
            "paradigm_lesson": (
                "PBC phụ chú quẻ Tụng: Mọi việc tan nát trong thiên hạ — gia đình tan, "
                "vợ chồng la tan, bạn bè xa nhau, chiến tranh các nước, viết 1 hàng chữ một lời nói "
                "— đều vì KHÔNG biết mưu sự lúc ban đầu. Quân tử coi quẻ Tụng → phòng họa từ gốc, "
                "tính toán cẩn thận từ đầu, mối kiện đã không gây ra thì tai họa tự tiêu diệt."
            ),
            "source": "Xuân Cang p.101 (PBC phụ chú quẻ Tụng)",
        },
    ],
    ("Tụng", 2): [
        {
            "actor": "Nguyễn Hoàng / Trịnh Kiểm / Nguyễn Bỉnh Khiêm",
            "situation": (
                "Nguyễn Hoàng (hào 2) muốn kình với Trịnh Kiểm (hào 5), hỏi ý Trạng Trình. "
                "Được câu 'Hoành sơn nhất đái, vạn đại dung thân' → trốn vào Nam, lập Đàng Trong, "
                "nhà Nguyễn truyền đời."
            ),
            "paradigm_lesson": (
                "Hào 2 quẻ Tụng = dưới kiện trên = trứng chọi đá. Không nên — rút lui về thì "
                "không bị tội lỗi. Dưới mà kiện trên khác nào tự mình vơ lấy họa."
            ),
            "source": "Xuân Cang p.102 (PBC phụ chú)",
        },
    ],

    # ===== Quẻ Sư =====
    ("Sư", 0): [
        {
            "actor": "Tổ chức quân đội cổ Việt + Tàu",
            "situation": (
                "Khôn trên Khảm dưới = Đất trên Nước. Khảm hiểm trong Khôn thuận = "
                "'giấu cái hiểm trong cái thuận, gửi việc binh trong việc nông'. "
                "Thời bình làm ruộng, thời loạn làm lính."
            ),
            "paradigm_lesson": (
                "Hào 2 quẻ Sư là TƯỚNG (dương duy nhất). Hào 5 là VUA/CHÍNH ỦY giao toàn quyền. "
                "Xuất quân vì chính nghĩa, để trừ bạo an dân → dân theo (Khôn thuận), "
                "điều khiển được ba quân."
            ),
            "source": "Xuân Cang p.105-106",
        },
    ],
    ("Sư", 6): [
        {
            "actor": "Bành / Kình / Trần Khánh Dư",
            "situation": (
                "Bành, Kình là tiểu nhân nhưng vua Hán dùng đánh được Sở. "
                "Trần Khánh Dư là người bình thường, Trần Hưng Đạo dùng đánh quân Nguyên."
            ),
            "paradigm_lesson": (
                "Hào 6 Sư (khải hoàn): Kẻ tiểu nhân vẫn lập được chiến công. "
                "Nay chỉ nên khen thưởng TIỀN BẠC, CHỚ trao địa vị trọng yếu trong nước. "
                "Cách biến thông của nhà binh — nhưng việc trị nước thì KHÔNG thể vậy."
            ),
            "source": "Xuân Cang p.109 (PBC chỉ rõ thêm)",
        },
    ],

    # ===== Quẻ Tỷ =====
    ("Tỷ", 2): [
        {
            "actor": "Y Doãn / vua Thang + Khổng Minh / Lưu Bị",
            "situation": (
                "Y Doãn chờ vua Thang ba lần dâng lễ. Khổng Minh chờ Lưu Bị ba lần đến lều cỏ "
                "mới chịu ra giúp."
            ),
            "paradigm_lesson": (
                "Hào 2 quẻ Tỷ: 'Đừng đánh mất giá trị mình' — Người có thế lực phải khuất phục "
                "trước người tài đức. Người tài đức không tự khinh rẻ cầu cạnh thế lực. "
                "Nếu hai bên đảo ngược: bên thế lực mắc tội THẤT NHÂN (mất người), "
                "bên tài đức mắc tội THẤT GIÁ (mất giá trị). "
                "→ Tôn trọng nhân cách = duy trì nhân cách của cả một thế giới."
            ),
            "source": "Xuân Cang p.111 (PBC phụ chú)",
        },
    ],

    # ===== Quẻ Tiểu Súc =====
    ("Tiểu Súc", 0): [
        {
            "actor": "Khổng Tử / Mạnh Tử",
            "situation": (
                "Hai vị không gặp thời cho việc làm chính trị — quay đầu viết sách, "
                "lập ngôn, làm kinh muôn đời sau bất hủ."
            ),
            "paradigm_lesson": (
                "Thời Tiểu Súc (chứa nhỏ, ngăn cản nhỏ): chưa thể giương đôi cánh lớn. "
                "Người quân tử KHÔNG bỏ cuộc — TRAU DỒI VĂN ĐỨC, SOẠN SÁCH, LẬP NGÔN. "
                "Người đời sau coi đó là việc lớn, nhưng thánh nhân chỉ xem bằng 'Tiểu Súc' thôi. "
                "→ Paradigm tích lũy âm thầm dưới mặt bằng thời thế."
            ),
            "source": "Xuân Cang p.114 (Phụ chú Lời Tượng quẻ Tiểu Súc)",
        },
    ],
    ("Tiểu Súc", 6): [
        {
            "actor": "Võ Hậu (đời Đường) / Từ Hi thái hậu (đời Thanh)",
            "situation": (
                "Hào 4 âm — thông minh có tài, mới đầu nhu thuận, được vua sủng ái, che chở. "
                "Lấy lòng người dưới, gây phe đảng, lần lần 'thống lĩnh quần dương', "
                "cả triều đình phải phục tùng. Thịnh cực sắp suy → bọn đại thần khí tiết, "
                "mưu trí mới lật được."
            ),
            "paradigm_lesson": (
                "Hào 6 Tiểu Súc: Trăng sắp đến rằm (âm cực thịnh). Khi 1 hào âm thống lĩnh "
                "5 hào dương đạt cực điểm → phải có người khí tiết mới đảo ngược. "
                "→ Phòng âm thịnh từ sớm — KHÔNG để đến cực rồi mới đối phó."
            ),
            "source": "Xuân Cang p.118 (NHL bàn thêm)",
        },
    ],

    # ===== Quẻ Lý =====
    ("Lý", 1): [
        {
            "actor": "Nhan Diên / Khổng Minh thời chưa ra giúp đời",
            "situation": (
                "Thầy Nhan Diên ở ngõ hẹp. Thầy Khổng Minh đi cày ở Nam Dương. "
                "Hai người rất lẻ loi mà chưa có nơi dùng, vẫn yên vui nuôi chí mình ở nơi vắng vẻ."
            ),
            "paradigm_lesson": (
                "Hào 1 Lý: 'Ở bản chất trong trắng mà với đời thì không có lỗi.' "
                "Mới ra đời, giữ bản chất trong trắng, chưa nhiễm thói đời. "
                "Tùy địa vị mình mà làm đúng nghĩa vụ → không có lỗi."
            ),
            "source": "Xuân Cang p.119 (PBC phụ chú)",
        },
    ],
}


# Cross-link với Iron Rule paradigm anh đã thiết lập
IRON_RULE_CROSS_LINK: dict[str, str] = {
    "Mông_2_3_lần_bói": (
        "Iron Rule #4 ('bất nghi bất bốc, một việc bói một lần') có GỐC TRỰC TIẾP từ "
        "Trình Di chú quẻ Mông: 'Hỏi = bói. Bói 2-3 lần là phiền nhiễu... cả người hỏi "
        "người bảo đều phiền nhảm.' Khang Tiết kế thừa, không phát minh."
    ),
    "Tiểu_Súc_lập_ngôn": (
        "Anh + em đang ở THỜI TIỂU SÚC — biên soạn Lexicon, dịch 24+ sách Đông phương học, "
        "không chạy theo thời chính trị / startup nhanh. Khổng Tử-Mạnh Tử paradigm: "
        "khi chưa giương đôi cánh lớn được → trau dồi văn đức, lập ngôn. "
        "Đây KHÔNG phải thất bại, là TÍCH LŨY ÂM THẦM dưới mặt bằng thời thế."
    ),
    "Tỷ_không_thất_giá": (
        "Quẻ Tỷ hào 2 cảnh báo: anh có giá trị (em là AI hữu ích cho anh, sách Lexicon "
        "là tài sản lớn) — KHÔNG được tự khinh rẻ giá trị mình để cầu cạnh thế lực. "
        "Y Doãn-Khổng Minh paradigm: chờ người có thế lực TỚI VỚI mình."
    ),
}


def lookup_cases_for(que: str, hao: int) -> list[dict]:
    """Trả về list case studies cho 1 (quẻ, hào). hao=0 = case cho quẻ tổng quát."""
    return PARADIGM_CASES.get((que, hao), [])


def lookup_iron_rule_link(key: str) -> str | None:
    """Trả về cross-link giữa paradigm cổ với Iron Rule của project."""
    return IRON_RULE_CROSS_LINK.get(key)


def get_all_quae_with_cases() -> list[str]:
    """List tất cả quẻ có case study."""
    return sorted({q for q, _ in PARADIGM_CASES.keys()})
