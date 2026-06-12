"""Kiến thức nền Âm Dương Ngũ Hành cho Tử Vi — tầng cơ chế dưới mọi luận giải.

Anh chốt 2026-06-12: "chưa đưa âm dương ngũ hành vào làm kiến thức nền tảng...
tab Bát Tự liên hệ rất nhiều tới ngũ hành và quan hệ tương sinh tương khắc
rất rõ nét dễ hiểu" → tab Tử Vi cần cùng tầng nền đó.

Định nghĩa nền (theo trường phái hiện đại, khớp cổ thư):
- Âm dương = 2 TRẠNG THÁI VẬN ĐỘNG của một sự vật (không phải 2 thứ đối lập).
- Ngũ hành = 5 KIỂU VẬN ĐỘNG của năng lượng: Mộc=sinh trưởng, Hỏa=bùng nổ,
  Thổ=ổn định/chuyển hóa, Kim=thu lại, Thủy=lưu chuyển. Tên gỗ-lửa-đất-kim-nước
  chỉ là cách đặt cho dễ nhớ.
- Sinh không hẳn tốt, khắc không hẳn xấu — "luận bệnh tật sẽ biết:
  không có khắc là toi luôn."

Module này cung cấp:
- Hành của 12 địa chi (cung) + hành/âm dương/hóa khí của 14 chính tinh
  (đọc từ data/tu_vi/chinh_tinh.json — nguồn Q2 đã enrich).
- ``quan_he(a, b)``: quan hệ sinh-khắc giữa 2 hành, kèm nhãn dễ hiểu.
- ``sao_tai_cung(star, chi)``: phân tích sao đứng trên đất cung — tầng CƠ CHẾ
  góp phần giải thích miếu-hãm. LƯU Ý TRUNG THỰC: bảng miếu-hãm cổ (Q2) xét
  nhiều yếu tố hơn sinh-khắc hành đơn (tổ hợp, nhật nguyệt, cách cục...) —
  khi hai tầng lệch nhau, trả cả hai, KHÔNG bịa lý do để ép khớp.
"""
from __future__ import annotations

from functools import lru_cache

from .chinh_tinh import ALL_CHINH_TINH
from .mieu_vuong_ham import level_at

# ── Bảng nền ──────────────────────────────────────────────────────────────────

# Hành của 12 địa chi (đất của cung)
HANH_CHI: dict[str, str] = {
    "Dần": "mộc", "Mão": "mộc",
    "Tỵ": "hỏa", "Ngọ": "hỏa",
    "Thân": "kim", "Dậu": "kim",
    "Hợi": "thủy", "Tý": "thủy",
    "Thìn": "thổ", "Tuất": "thổ", "Sửu": "thổ", "Mùi": "thổ",
}

# Âm dương của 12 địa chi
AM_DUONG_CHI: dict[str, str] = {
    "Tý": "dương", "Dần": "dương", "Thìn": "dương",
    "Ngọ": "dương", "Thân": "dương", "Tuất": "dương",
    "Sửu": "âm", "Mão": "âm", "Tỵ": "âm",
    "Mùi": "âm", "Dậu": "âm", "Hợi": "âm",
}

# Vòng tương sinh / tương khắc
SINH: dict[str, str] = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
KHAC: dict[str, str] = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}

# 5 kiểu vận động của năng lượng (định nghĩa nền — không phải vật chất)
HANH_VAN_DONG: dict[str, str] = {
    "mộc": "sinh trưởng — vươn lên, mở rộng",
    "hỏa": "bùng nổ — phát sáng, lan tỏa",
    "thổ": "ổn định — nuôi giữ, chuyển hóa",
    "kim": "thu lại — kết tinh, định hình",
    "thủy": "lưu chuyển — thấm sâu, linh hoạt",
}

_STAR_BY_NAME = {s.ten_vi: s for s in ALL_CHINH_TINH}


def _hanh_chinh(ngu_hanh_raw: str) -> tuple[str, str | None]:
    """Tách hành chính + hành phụ ('mộc / thủy' → ('mộc', 'thủy'))."""
    parts = [p.strip().lower() for p in str(ngu_hanh_raw).split("/") if p.strip()]
    if not parts:
        return "", None
    return parts[0], (parts[1] if len(parts) > 1 else None)


def quan_he(hanh_a: str, hanh_b: str) -> dict:
    """Quan hệ giữa hành A (chủ thể) và hành B (đối tượng).

    Returns {code, label, arrow}:
      dong_hanh | a_sinh_b | b_sinh_a | a_khac_b | b_khac_a
    """
    a, b = hanh_a.lower().strip(), hanh_b.lower().strip()
    if not a or not b:
        return {"code": "unknown", "label": "không rõ", "arrow": "?"}
    if a == b:
        return {"code": "dong_hanh", "label": "đồng hành", "arrow": f"{a} = {b}"}
    if SINH.get(a) == b:
        return {"code": "a_sinh_b", "label": "tương sinh (A sinh B)", "arrow": f"{a} → sinh → {b}"}
    if SINH.get(b) == a:
        return {"code": "b_sinh_a", "label": "tương sinh (B sinh A)", "arrow": f"{b} → sinh → {a}"}
    if KHAC.get(a) == b:
        return {"code": "a_khac_b", "label": "tương khắc (A khắc B)", "arrow": f"{a} ⊣ khắc ⊣ {b}"}
    if KHAC.get(b) == a:
        return {"code": "b_khac_a", "label": "tương khắc (B khắc A)", "arrow": f"{b} ⊣ khắc ⊣ {a}"}
    return {"code": "unknown", "label": "không rõ", "arrow": "?"}


# Diễn giải sao-đứng-trên-đất-cung theo từng quan hệ (A = sao, B = đất cung).
# Giọng: cơ chế năng lượng + bài học — KHÔNG phán tốt/xấu.
_NHAN_DINH_SAO_CUNG: dict[str, str] = {
    "dong_hanh": (
        "Sao về đúng quê hành của mình — khí thuận, lực biểu hiện tự nhiên, "
        "không phải gồng. Bài học ở đây là dùng cái thuận cho khéo, đừng để thành quán tính."
    ),
    "b_sinh_a": (
        "Đất cung SINH cho sao — như cây trồng đúng thổ nhưỡng: lực sao được bồi đắp "
        "liên tục, vào đà nhanh. Cẩn thận một điều: được nuôi dễ thì cũng dễ ỷ vào đà."
    ),
    "a_sinh_b": (
        "Sao phải NHẢ lực ra nuôi bối cảnh — làm được việc cho nơi này nhưng hao khí. "
        "Bài học: tiết chế nhịp, biết nạp lại, đừng cho đi đến cạn."
    ),
    "b_khac_a": (
        "Đất cung KHẮC sao — lực bị nén lại, biểu hiện chậm và khó hơn. Nén không phải "
        "án phạt: nén đúng cách thành độ chắc, thành bản lĩnh; nén sai cách thành ức chế."
    ),
    "a_khac_b": (
        "Sao KHẮC đất cung — lực đủ mạnh để áp đặt lên bối cảnh, nhưng tốn sức kiểm soát, "
        "dễ căng. Bài học: thắng bối cảnh chưa phải là xong, giữ được lâu mới là xong."
    ),
}


def sao_tai_cung(star_vi: str, chi_vi: str) -> dict | None:
    """Phân tích nền ngũ hành: sao ``star_vi`` đứng trên đất cung ``chi_vi``.

    Returns dict cho UI:
      {sao, hanh_sao, hanh_phu, am_duong_sao, hoa_khi, cung_chi, hanh_cung,
       am_duong_cung, quan_he{code,label,arrow}, nhan_dinh, mieu_ham,
       ghi_chu_lech (nếu bảng miếu-hãm cổ lệch chiều với sinh-khắc hành đơn)}
    """
    star = _STAR_BY_NAME.get(star_vi)
    hanh_cung = HANH_CHI.get(chi_vi)
    if star is None or hanh_cung is None:
        return None
    hanh_sao, hanh_phu = _hanh_chinh(star.ngu_hanh)
    qh = quan_he(hanh_sao, hanh_cung)
    nhan_dinh = _NHAN_DINH_SAO_CUNG.get(qh["code"], "")

    level = level_at(star_vi, chi_vi)

    # Trung thực đa tầng: sinh-khắc hành đơn vs bảng miếu-hãm cổ truyền
    ghi_chu_lech = None
    thuan_codes = {"dong_hanh", "b_sinh_a"}
    nghich_codes = {"b_khac_a", "a_sinh_b"}
    if level in ("miếu", "vượng") and qh["code"] in nghich_codes:
        ghi_chu_lech = (
            f"Bảng cổ truyền (Q2) xếp {star_vi} {level.upper()} tại {chi_vi} dù hành đơn "
            f"không thuận — cổ nhân xét thêm tổ hợp sao, thế nhật nguyệt và cách cục, "
            "không chỉ một cặp hành. Hai tầng cùng được giữ để đối chiếu."
        )
    elif level in ("hãm", "lạc") and qh["code"] in thuan_codes:
        ghi_chu_lech = (
            f"Hành đơn thuận nhưng bảng cổ truyền (Q2) xếp {star_vi} {level.upper()} tại "
            f"{chi_vi} — cổ nhân xét thêm nhiều yếu tố ngoài một cặp hành. "
            "Hai tầng cùng được giữ để đối chiếu."
        )

    return {
        "sao": star_vi,
        "hanh_sao": hanh_sao,
        "hanh_phu": hanh_phu,
        "hanh_sao_van_dong": HANH_VAN_DONG.get(hanh_sao),
        "am_duong_sao": star.am_duong,
        "hoa_khi": star.hoa_khi,
        "cung_chi": chi_vi,
        "hanh_cung": hanh_cung,
        "hanh_cung_van_dong": HANH_VAN_DONG.get(hanh_cung),
        "am_duong_cung": AM_DUONG_CHI.get(chi_vi),
        "quan_he": qh,
        "nhan_dinh": nhan_dinh,
        "mieu_ham": level,
        "ghi_chu_lech": ghi_chu_lech,
    }


@lru_cache(maxsize=1)
def vong_sinh_khac() -> dict:
    """Bảng nền cho UI trang kiến thức: vòng sinh, vòng khắc, định nghĩa 5 hành.

    Khối ``nguon_goc`` bồi từ vòng đọc sâu "Học Thuyết Âm Dương Ngũ Hành"
    (Lê Văn Sửu) — vòng 1 p1-20, 2026-06-13.
    """
    return {
        "dinh_nghia": {
            "am_duong": "Âm dương là 2 trạng thái vận động của một sự vật — "
                        "hoạt động/nghỉ, mở/thu, nóng/lạnh — không phải 2 phe tốt xấu.",
            "ngu_hanh": "Ngũ hành là 5 kiểu vận động của năng lượng; tên gỗ-lửa-đất-"
                        "kim-nước chỉ là cách đặt cho dễ nhớ.",
            "sinh_khac": "Sinh không hẳn tốt, khắc không hẳn xấu — không có khắc thì "
                         "không có định hình, như luận bệnh: không có khắc là hỏng.",
        },
        "nguon_goc": {
            "tom_tat": (
                "Học thuyết sinh từ nhu cầu sinh tồn ở Phương Đông — vùng đất kẹp giữa "
                "các cực đối nghịch lớn nhất (biển lớn nhất phía đông, núi cao nhất phía tây, "
                "hàn đới bắc, xích đạo nam) với gió bốn mùa bốn tính chất. Người xưa ghi chép "
                "'khí ứng' (vật biến đổi tương ứng với thời gian, nơi chốn), so sánh các 'tượng' "
                "đối lập mà quy thành hai loại âm–dương; rồi vì hai mặt không đủ tả trọn quá trình "
                "sinh → trưởng → suy → diệt nên chia thành NĂM BƯỚC — đó là ngũ hành. "
                "Ngũ hành nguyên thủy là 5 giai đoạn của một quá trình, không phải 5 chất liệu."
            ),
            "bon_quy_luat": (
                "Năm bước tác động qua lại thành 4 quy luật: tương sinh, tương khắc, "
                "tương chế, tương hóa (hệ hiện hiển thị sinh–khắc; chế–hóa sẽ bổ sung "
                "khi đọc tới chương chuyên sâu)."
            ),
            "the_dung": (
                "Tiên thiên bát quái (Phục Hy) là cái THỂ của âm dương; Hậu thiên bát quái "
                "(Văn Vương, theo tứ thời bát tiết) là cái DỤNG — hai tầng chức năng, "
                "không phải hai phiên bản cạnh tranh."
            ),
            "truc_thoi_gian": (
                "Cái quyết định sự thay đổi giá trị tương tác của âm dương trong vạn vật "
                "là sự vận động của vũ trụ tính bằng ĐƠN VỊ THỜI GIAN — đối ứng hiện đại "
                "là 'nhịp thời sinh học' (chronobiology)."
            ),
            "nguon": "Lê Văn Sửu — Học Thuyết Âm Dương Ngũ Hành, p4-20 (vòng đọc sâu 1, 2026-06-13)",
        },
        "hanh": HANH_VAN_DONG,
        "vong_sinh": [["mộc", "hỏa"], ["hỏa", "thổ"], ["thổ", "kim"], ["kim", "thủy"], ["thủy", "mộc"]],
        "vong_khac": [["mộc", "thổ"], ["thổ", "thủy"], ["thủy", "hỏa"], ["hỏa", "kim"], ["kim", "mộc"]],
        "hanh_chi": HANH_CHI,
    }
