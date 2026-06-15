"""Vòng đời v2 — món khai vị chạm ĐÚNG bận tâm theo TUỔI × GIỚI × NĂM XEM.

Anh chốt 2026-06-13: chia nhỏ tới nam/nữ, khai thác thêm tín hiệu từ năm sinh
→ năm xem. Bám research tâm lý người Việt (2 mốc khủng hoảng tên riêng: 22 lạc
lối, 30 'ai cũng thành công trừ tôi') + Tử Vi truyền thống (cung nhấn theo giai
đoạn) + dân gian (năm tuổi, xung/hợp Thái Tuế, tam tai, Kim Lâu).

Nguyên tắc: luôn cặp 1 tín hiệu TÍCH CỰC để đồng cảm, KHÔNG hù dọa.
Tuổi = tuổi mụ = năm xem − năm sinh + 1.
"""
from __future__ import annotations

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
_TAM_HOP = [(0, 4, 8), (2, 6, 10), (5, 9, 1), (11, 3, 7)]  # Thân-Tý-Thìn / Dần-Ngọ-Tuất / Tỵ-Dậu-Sửu / Hợi-Mão-Mùi
# Tam tai: tam hợp tuổi → 3 chi năm gặp tam tai
_TAM_TAI = {(0, 4, 8): (2, 3, 4), (2, 6, 10): (8, 9, 10),
            (5, 9, 1): (11, 0, 1), (11, 3, 7): (5, 6, 7)}

# (max_tuoi, slug, tên) — giai đoạn theo tuổi mụ
_BANDS = [
    (3, "so_sinh", "Bé sơ sinh"),
    (15, "nhi_dong", "Nhi đồng – thiếu niên"),
    (22, "thanh_nien", "Thanh niên"),
    (32, "lap_than", "Lập thân"),
    (39, "tam_thap", "Tam thập"),
    (49, "tu_thap", "Tứ thập"),
    (59, "ngu_thap", "Ngũ thập tri thiên mệnh"),
    (200, "luc_thap", "Lục thập trở lên"),
]

# Chủ đề mở bài × GIỚI. Sơ sinh + nhi đồng dùng chung (cha mẹ xem).
_CHU_DE = {
    "so_sinh": {"chung": "thiên hướng bẩm sinh, khí chất trời cho, cách nuôi dạy thuận tính, nền sức khỏe"},
    "nhi_dong": {"chung": "năng khiếu nổi trội, đường học hành, tính nết, quan hệ cha mẹ – con"},
    "thanh_nien": {
        "nam": "chọn nghề/định hướng ra đời (sợ chọn sai đường), đi tìm chính mình — mình mạnh ở đâu, những rung động đầu đời",
        "nu": "học xong theo nghề hay theo người, người ấy có thật lòng không, cảm giác chênh vênh khi thấy bạn bè 'có vẻ' hơn mình",
    },
    "lap_than": {
        "nam": "định hình sự nghiệp (thăng tiến hay nhảy việc/khởi nghiệp), áp lực tiền bạc – nhà cửa – cảm giác 'ai cũng thành công trừ mình', chuyện lập gia đình",
        "nu": "hôn nhân (lấy chồng, tuổi hợp), con cái sớm muộn, cân bằng sự nghiệp – gia đình và giá trị bản thân",
    },
    "tam_thap": {
        "nam": "sự nghiệp vào đỉnh hay chững lại – có đột phá được không, trụ cột tài chính gia đình, con cái và quan hệ vợ chồng sau cưới",
        "nu": "con cái (sức khỏe, học hành, dạy dỗ) là ưu tiên hàng đầu, hôn nhân trung hạn, quay lại sự nghiệp sau sinh",
    },
    "tu_thap": {
        "nam": "khủng hoảng trung niên (sự nghiệp trần hay 'làm mãi vẫn vậy', thức tỉnh ý nghĩa), tài chính dài hạn – nhà cửa, sức khỏe bắt đầu đi xuống",
        "nu": "con cái lớn (hướng nghiệp, đừng gấp gáp giục giã), thay đổi thân-tâm tuổi tiền mãn kinh, tình cảm vợ chồng nguội dần",
    },
    "ngu_thap": {
        "nam": "cuối chặng sự nghiệp – bàn giao, hưu trí, di sản để lại, sức khỏe & lo cho con lập nghiệp",
        "nu": "con cái dựng gia đình – chăm cháu, sức khỏe tuổi xế chiều, gắn kết vợ chồng về già, an yên tinh thần",
    },
    "luc_thap": {
        "nam": "sức khỏe & tuổi thọ (bận tâm số 1), con cháu hiếu thảo – gia đình hòa thuận, phúc đức để lại, tâm an",
        "nu": "sức khỏe sống thọ ít bệnh, con cháu sum vầy hiếu thảo, an yên tâm linh – phúc ấm hậu vận",
    },
}


def _chi_nam(year: int) -> int:
    return (year - 4) % 12


def giai_doan_song(tuoi_mu: int, gender: str = "M") -> dict:
    g = "nu" if gender in ("F", "nu", "nữ") else "nam"
    for max_t, slug, ten in _BANDS:
        if tuoi_mu <= max_t:
            cd = _CHU_DE[slug]
            chu_de = cd.get("chung") or cd.get(g)
            ai_xem = "cha_me_xem" if slug in ("so_sinh", "nhi_dong") else "tu_xem"
            xung_ho = "bé" if ai_xem == "cha_me_xem" else ("anh" if g == "nam" else "chị")
            return {
                "tuoi_mu": tuoi_mu, "slug": slug, "ten": ten,
                "gioi": g, "chu_de": chu_de, "ai_xem": ai_xem, "xung_ho": xung_ho,
            }
    return {}


def buoc_ngoat_dai_van(dai_van: dict | None) -> str | None:
    """Nếu vừa BƯỚC VÀO đại vận mới (1-2 năm đầu) → câu mời khảo sát bước ngoặt."""
    if not dai_van:
        return None
    start = dai_van.get("start_age")
    age = dai_van.get("age_mu")
    if start is None or age is None:
        return None
    nam_vao = age - start
    if 0 <= nam_vao <= 2:
        return (f"Vừa bước vào một đại vận mới (khoảng {nam_vao} năm trước) — thường là bước ngoặt: "
                "đổi việc, đổi nơi ở, đổi tâm thế, hoặc biến chuyển lớn trong lòng. Gợi nhẹ để người xem "
                "tự đối chiếu giai đoạn vừa rồi có đúng vậy không (tăng độ tin, không phán chắc).")
    return None


def tin_hieu_nam_xem(year_branch_sinh: str, nam_xem: int, tuoi_mu: int, gender: str = "M") -> list[dict]:
    """Tín hiệu dân gian từ năm sinh → năm xem. Mỗi tín hiệu: {loai, sac_thai, nhac}.

    sac_thai: 'tich_cuc' | 'trung_tinh' | 'luu_y' — để cân giọng, không toàn cảnh báo.
    """
    try:
        cs = CHI.index(year_branch_sinh)
    except ValueError:
        return []
    cx = _chi_nam(nam_xem)
    out = []
    trio = next((t for t in _TAM_HOP if cs in t), None)

    if cx == cs:
        out.append({"loai": "nam_tuoi", "sac_thai": "luu_y",
                    "nhac": f"Năm {nam_xem} là NĂM TUỔI (bản mệnh niên) của {('chị' if gender in ('F','nu','nữ') else 'anh')} "
                            "— dân gian xem là năm cần giữ mình, nhưng cũng là năm 'về đúng nhà' của bản mệnh."})
    elif (cx - cs) % 12 == 6:
        out.append({"loai": "xung_thai_tue", "sac_thai": "luu_y",
                    "nhac": f"Năm {nam_xem} XUNG Thái Tuế với tuổi — thường có nhiều biến động, thay đổi quanh mình "
                            "(công việc, đi lại, môi trường). Nhắc nhẹ để chủ động, KHÔNG dọa."})
    elif trio and cx in trio:
        out.append({"loai": "hop_thai_tue", "sac_thai": "tich_cuc",
                    "nhac": f"Năm {nam_xem} HỢP/tam hợp Thái Tuế với tuổi — năm thuận, dễ có quý nhân, "
                            "việc trôi chảy hơn. Dùng để mở giọng tích cực."})

    if trio and cx in _TAM_TAI.get(trio, ()):
        out.append({"loai": "tam_tai", "sac_thai": "luu_y",
                    "nhac": "Đang trong giai đoạn Tam Tai (3 năm) — nhắc kiểu 'cần vững tay chèo, việc lớn nên tính kỹ', "
                            "TUYỆT ĐỐI không hù dọa tai họa."})

    if gender in ("F", "nu", "nữ") and (tuoi_mu % 9) in (1, 3, 6, 8):
        out.append({"loai": "kim_lau", "sac_thai": "luu_y",
                    "nhac": f"Tuổi {tuoi_mu} là tuổi Kim Lâu (nữ) — CHỈ nhắc khi nói tới việc lớn (cưới hỏi, làm nhà), "
                            "theo lệ xưa nên cân nhắc thời điểm; nói nhẹ như tham khảo."})
    return out
