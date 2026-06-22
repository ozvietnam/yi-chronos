"""Hồ sơ THÁI ĐỘ SỐ PHẬN — hiện thực Phần II sách 《Tử Vi Tính Được》 (phái tu_vi_dang_son).

Embedding 14 chính tinh vào không-gian-thái-độ 3 trục (Đằng Sơn → AI hình thức hoá):
  • dinh_bien : Định (+1, tin số cố định/khoá) ↔ Biến (−1, tin số đổi được)
  • thu_tac   : Tác (+1, kiến tạo số)         ↔ Thụ (−1, chấp nhận số)
  • noi_ngoai : Nội (+1, số từ tính bên trong) ↔ Ngoại (−1, số từ hoàn cảnh ngoài)
(Trục 4 Cá-nhân↔Siêu cho Tả/Hữu để ở AUX, không vào profile chính.)

⚠️ ĐỌC ĐỒNG DẠNG, KHÔNG PREDICT (Iron #4/#6/#8): hồ sơ mô tả *thế đứng VẬN HÀNH* cái
tính — KHÔNG dự báo sự kiện. Hàm thuần (tất định): cùng lá → cùng hồ sơ.
"""
from __future__ import annotations

from typing import Optional

# Vector 14 chính tinh (khớp bảng Phần II — từ bản chất sao cổ văn).
STARS: dict[str, dict[str, float]] = {
    "tu_vi":       {"dinh_bien": +1.0, "thu_tac": +0.5, "noi_ngoai": +0.5},
    "thien_co":    {"dinh_bien": -1.0, "thu_tac": +0.5, "noi_ngoai": +0.5},
    "thai_duong":  {"dinh_bien": +0.5, "thu_tac": +0.5, "noi_ngoai": -1.0},
    "vu_khuc":     {"dinh_bien": +1.0, "thu_tac": +0.5, "noi_ngoai": +0.5},
    "thien_dong":  {"dinh_bien": +0.5, "thu_tac": -1.0, "noi_ngoai": +0.5},
    "liem_trinh":  {"dinh_bien": -0.5, "thu_tac":  0.0, "noi_ngoai": +0.5},
    "thien_phu":   {"dinh_bien": +1.0, "thu_tac": -0.5, "noi_ngoai": +0.5},
    "thai_am":     {"dinh_bien": +0.5, "thu_tac": -0.5, "noi_ngoai": +1.0},
    "tham_lang":   {"dinh_bien": -0.5, "thu_tac": +1.0, "noi_ngoai": +0.5},
    "cu_mon":      {"dinh_bien": -0.5, "thu_tac": -0.5, "noi_ngoai": -0.5},
    "thien_tuong": {"dinh_bien": +0.5, "thu_tac":  0.0, "noi_ngoai": -0.5},
    "thien_luong": {"dinh_bien": +1.0, "thu_tac": -0.5, "noi_ngoai": +0.5},
    "that_sat":    {"dinh_bien": -0.5, "thu_tac": +1.0, "noi_ngoai": +0.5},
    "pha_quan":    {"dinh_bien": -1.0, "thu_tac": +1.0, "noi_ngoai": +0.5},
}

# Trục 4 (phụ tinh Đằng Sơn xếp): số xuyên quan hệ/kiếp.
AUX = {"ta_phu": "samsara (luân hồi)", "huu_bat": "transmigration (chuyển kiếp)"}

# Cung trọng số: Mệnh > Thân > cung trụ > còn lại. Sao ở Mệnh định hình thế-đứng mạnh nhất.
PALACE_WEIGHT = {
    "menh": 3.0, "than": 2.0,
    "quan_loc": 1.5, "tai_bach": 1.5, "phu_the": 1.5, "phuc_duc": 1.5,
}
_DEFAULT_W = 1.0
_AXES = ("dinh_bien", "thu_tac", "noi_ngoai")

# Nhãn đọc-đồng-dạng (mô tả THẾ ĐỨNG, tuyệt đối không giọng predict).
_POLE = {
    "dinh_bien": ("thiên RÈN/khoá số bằng ý chí (Định)", "thiên PHÁ/biến chuyển số (Biến)"),
    "thu_tac":   ("thiên KIẾN TẠO, chủ động đắp số (Tác)", "thiên AN HƯỞNG, thuận theo số (Thụ)"),
    "noi_ngoai": ("số nghiêng về TÍNH bên trong (Nội)", "số nghiêng về HOÀN CẢNH ngoài (Ngoại)"),
}

PARADIGM = ("Hồ sơ này là THẾ ĐỨNG vận hành cái tính (đọc đồng dạng), không phải lời "
            "đoán. Lá số cho nguyên liệu; vận hành ra sao là việc của người (mệnh là động từ).")


def ho_so_thai_do(
    chinh_tinh_per_palace: dict[str, list[str]],
    brightness: Optional[dict[str, float]] = None,
) -> dict:
    """Tính hồ sơ thái-độ-số-phận từ chính tinh per cung. Tất định.

    chinh_tinh_per_palace: {cung_key: [sao_canonical, ...]} — cung_key gồm 'menh',
        'than', 'quan_loc'... (khớp PALACE_WEIGHT) hoặc bất kỳ (mặc định trọng số 1).
    brightness: {sao: hệ số miếu-hãm 0..1} tuỳ chọn (mặc định 1).
    """
    brightness = brightness or {}
    acc = {ax: 0.0 for ax in _AXES}
    total_w = 0.0
    for palace, stars in (chinh_tinh_per_palace or {}).items():
        pw = PALACE_WEIGHT.get(palace, _DEFAULT_W)
        for s in stars or []:
            vec = STARS.get(s)
            if not vec:
                continue
            w = pw * float(brightness.get(s, 1.0))
            for ax in _AXES:
                acc[ax] += vec[ax] * w
            total_w += w

    profile = {ax: (round(acc[ax] / total_w, 4) if total_w else 0.0) for ax in _AXES}

    # Mô tả thế đứng trội (trục có |giá trị| lớn nhất) — đọc-đồng-dạng.
    if total_w:
        ax_max = max(_AXES, key=lambda a: abs(profile[a]))
        pole = _POLE[ax_max][0 if profile[ax_max] >= 0 else 1]
        dominant = f"Thế đứng trội: {pole}."
    else:
        dominant = "Chưa đủ chính tinh để dựng thế đứng."

    return {
        "profile": profile,           # vector 3 trục (tính được, tất định)
        "dominant": dominant,         # mô tả thế đứng (không predict)
        "axes": {ax: _POLE[ax] for ax in _AXES},
        "paradigm": PARADIGM,
    }
