"""Vòng đời — quyết định món khai vị MỞ BÀI chạm vào điều gì, theo TUỔI THẬT.

Anh chốt 2026-06-13: bài khai vị phải bắt nhịp đồng cảm — nói đúng cái user
đang bận tâm ở khúc đời họ. 20t hỏi việc-tình, 30t hỏi con-đất-phụ mẫu,
40t hỏi phu thê-cha mẹ-sức khỏe, 50t hỏi sức khỏe-con yên bề-phúc đức...
Bé sơ sinh (bố mẹ xem) → khai vị riêng. Nam/nữ khác câu từ.

Tuổi tính theo TUỔI MỤ = năm xem − năm sinh + 1 (đồng bộ cách Tử Vi tính vận).
"""
from __future__ import annotations

# (max_tuoi, slug, tên giai đoạn, chủ đề mở bài, ai xem)
_GIAI_DOAN = [
    (3,  "so_sinh",  "Bé sơ sinh",
     "thiên hướng bẩm sinh, khí chất trời cho, cách nuôi dạy thuận tính, nền sức khỏe",
     "cha_me_xem"),
    (15, "nhi_dong", "Nhi đồng – thiếu niên",
     "năng khiếu nổi trội, đường học hành, tính nết, mối quan hệ cha mẹ – con",
     "cha_me_xem"),
    (22, "thanh_nien", "Thanh niên",
     "định hướng nghề nghiệp/học vấn, những rung động tình cảm đầu đời, hành trình tìm chính mình",
     "tu_xem"),
    (32, "lap_than", "Lập thân",
     "sự nghiệp và chọn đường đi, chuyện tình yêu – hôn nhân, nền tài chính khởi đầu, bản lĩnh vào đời",
     "tu_xem"),
    (39, "tam_thap", "Tam thập nhi lập",
     "con cái, nhà cửa đất đai, đồng nghiệp – quý nhân, sự nghiệp đang lên đỉnh, cha mẹ",
     "tu_xem"),
    (49, "tu_thap", "Tứ thập",
     "hôn nhân vợ chồng (bền hay lung lay), sức khỏe bắt đầu cần giữ, cha mẹ tuổi già",
     "tu_xem"),
    (59, "ngu_thap", "Ngũ thập tri thiên mệnh",
     "sức khỏe, con cái yên bề gia thất, chuyển giao – nghỉ ngơi, phúc đức để lại, lòng dần tìm an",
     "tu_xem"),
    (200, "luc_thap", "Lục thập trở lên",
     "sức khỏe và tuổi thọ, phúc đức, con cháu, sự an nhàn trong tâm, nhìn lại cả đời",
     "tu_xem"),
]


def giai_doan_song(tuoi_mu: int, gender: str = "M") -> dict:
    """Trả giai đoạn sống + chủ đề mở bài nên chạm vào.

    Returns: {slug, ten, chu_de, ai_xem ('cha_me_xem'|'tu_xem'), gender_vi, xung_ho}
    """
    for max_t, slug, ten, chu_de, ai_xem in _GIAI_DOAN:
        if tuoi_mu <= max_t:
            g = "nữ" if gender in ("F", "nu", "nữ") else "nam"
            return {
                "tuoi_mu": tuoi_mu, "slug": slug, "ten": ten,
                "chu_de": chu_de, "ai_xem": ai_xem,
                "gender_vi": g,
                "xung_ho": ("bé" if ai_xem == "cha_me_xem"
                            else "anh" if g == "nam" else "chị"),
            }
    return {}


def buoc_ngoat_dai_van(dai_van: dict | None) -> str | None:
    """Nếu vừa BƯỚC VÀO đại vận mới (1-2 năm đầu) → câu nhắc khảo sát bước ngoặt.

    dai_van: dict dai_van_hien_tai có start_age + age_mu.
    """
    if not dai_van:
        return None
    start = dai_van.get("start_age")
    age = dai_van.get("age_mu")
    if start is None or age is None:
        return None
    nam_vao = age - start
    if 0 <= nam_vao <= 2:
        return (f"Anh/chị vừa bước vào một đại vận mới (khoảng {nam_vao} năm trước) — "
                "đây thường là một bước ngoặt: đổi việc, đổi nơi ở, đổi tâm thế, hoặc một "
                "biến chuyển lớn trong lòng. Hãy nhẹ nhàng gợi để người xem tự đối chiếu "
                "xem giai đoạn vừa rồi có đúng vậy không (tăng độ tin, không phán chắc).")
    return None
