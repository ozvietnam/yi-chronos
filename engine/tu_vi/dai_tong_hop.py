"""Đại tổng hợp lá số — synthesis layer trên cast_la_so (kết tinh 40 vòng đọc Đằng Sơn 2026-06-23).

Lấy một lá số (output an_sao.cast_la_so) → tính các TÍN HIỆU CẤU TRÚC:
  • THỂ–DỤNG–HẬU THIÊN (Mệnh chủ / Mệnh cung chính tinh / Thân chủ)
  • giai đoạn Trường Sinh của Mệnh (cục-vòng)
  • cụm CỬA TU tại Mệnh (Thiên Tướng + Thiên Không + Thiếu Dương + Cô Thần)
  • config TỨ MỘ tu-dưỡng (chữ ký Đằng Sơn T2 Ch.19)
  • Tuần/Triệt clearance của Mệnh
  • CÂN BẰNG: sáng & xấu-nhẹ (trung thực, không tô hồng)

Iron #4/#6/#8: đọc TÍNH / cấu-trúc / cơ-hội — TUYỆT KHÔNG predict. Mọi tầng là disposition, không phán kết cục.
"""
from __future__ import annotations

from . import an_sao as _a

BR = _a.BRANCHES_TVI
_NB = {n: i for i, n in enumerate(BR)}
_CORNERS = {_NB[x] for x in ("Dần", "Thân", "Tỵ", "Hợi")}

# Cụm sao "cửa tu" (đọc đồng dạng) — Đằng Sơn T2 V20/V30/V32
_CUA_TU_STARS = {
    "Thiên Tướng": "cận tu/giác ngộ (kém tranh quyền thế tục → bù lại gần đạo)",
    "Thiên Không": "tôn giáo, linh cảm — 4 góc + Hồng Loan = 'tư cách người tu hành'",
    "Thiếu Dương": "thánh tính — 'ngộ ra mọi danh lợi đều hư'",
    "Cô Thần": "cô độc = ĐẠO HẠNH cho bậc chân tu (Tổ tr.198)",
}


def _menh_branch_idx(la_so: dict) -> int:
    return next(p["branch_index"] for p in la_so["palaces"] if p["name"] == "Mệnh")


def _palace_of(la_so: dict, idx: int) -> str:
    return next((p["name"] for p in la_so["palaces"] if p["branch_index"] == idx), "?")


def _stage_at(la_so: dict, idx: int) -> str:
    """Giai đoạn vòng Trường Sinh (cục) tại 1 cung."""
    ts = la_so.get("trang_sinh", {})
    for stage, b in ts.items():
        if b == idx:
            return stage
    return "?"


def _all_stars_at(la_so: dict, idx: int) -> list[str]:
    """Mọi sao engine đặt tại 1 cung (gộp các nhóm + sao chi-năm tính riêng)."""
    found = []
    for grp in ("chinh_tinh", "phu_tinh", "sat_tinh", "sao_le", "sao_q2", "sao_q3"):
        for nm, v in la_so.get(grp, {}).items():
            if isinstance(v, int) and v == idx:
                found.append(nm)
    for belt in ("thai_tue_belt", "tuong_tinh_belt", "bac_si_belt"):
        for nm, v in la_so.get(belt, {}).items():
            if isinstance(v, int) and v == idx and nm not in found:
                found.append(nm)
    return found


def the_dung_hau_thien(la_so: dict) -> dict:
    """3 lớp: THỂ (Mệnh chủ, tiên thiên) · DỤNG (chính tinh Mệnh cung) · HẬU THIÊN (Thân chủ)."""
    menh_idx = _menh_branch_idx(la_so)
    menh_chinh = [s for s in la_so.get("chinh_tinh", {}) if la_so["chinh_tinh"][s] == menh_idx]
    return {
        "the": {"sao": la_so.get("menh_chu", ""), "vai": "tiên thiên — cốt/căn"},
        "dung": {"sao": menh_chinh, "vai": "diện mạo — cách đã học để gánh"},
        "hau_thien": {"sao": la_so.get("than_chu", ""), "vai": "hướng phát triển hậu thiên"},
    }


def cua_tu_cluster(la_so: dict) -> dict:
    """Cụm sao 'cửa tu' hội tụ tại Mệnh (đọc đồng dạng — Đằng Sơn T2 V20/V30/V32)."""
    menh_idx = _menh_branch_idx(la_so)
    at_menh = set(_all_stars_at(la_so, menh_idx))
    present = {s: note for s, note in _CUA_TU_STARS.items() if s in at_menh}
    return {
        "menh_branch": BR[menh_idx],
        "stars_present": sorted(present),
        "notes": present,
        "count": len(present),
    }


def tu_mo_tu_duong(la_so: dict) -> dict:
    """Chữ ký config TỨ MỘ tu-dưỡng (Đằng Sơn T2 Ch.19): năm tứ-mộ → Thiên Không+Thiếu Dương+
    Kiếp Sát+Cô Thần CÙNG 1 cung GÓC (Dần Thân Tỵ Hợi)."""
    yb = la_so["year_branch"]
    is_tu_mo = yb in ("Thìn", "Tuất", "Sửu", "Mùi")
    belt = la_so.get("thai_tue_belt", {})
    tt = la_so.get("tuong_tinh_belt", {})
    core = {
        la_so.get("sao_le", {}).get("Thiên Không"),
        belt.get("Thiếu Dương"),
        tt.get("Kiếp Sát"),
        la_so.get("sao_q2", {}).get("Cô Thần"),
    }
    core.discard(None)
    colocated = len(core) == 1 and next(iter(core)) in _CORNERS if core else False
    corner = BR[next(iter(core))] if colocated else None
    return {
        "is_tu_mo_year": is_tu_mo,
        "cua_khong_colocated_corner": colocated,
        "corner": corner,
        "reading": (
            "tuổi tứ mộ + 4 sao duyên-nghiệp chế-hóa tại 1 góc = cơ-hội tu tâm dưỡng tính "
            "hơn các tuổi khác (Đằng Sơn tr.223)" if (is_tu_mo and colocated) else None
        ),
    }


def tuan_triet_status(la_so: dict) -> dict:
    """Mệnh có THÔNG (ngoài Tuần+Triệt) không + Tuần/Triệt rơi cung nào."""
    menh_idx = _menh_branch_idx(la_so)
    triet = set(la_so.get("triet", []))
    tuan = set(la_so.get("tuan", []))
    return {
        "menh_thong": menh_idx not in (triet | tuan),
        "triet_palaces": [_palace_of(la_so, i) for i in sorted(triet)],
        "tuan_palaces": [_palace_of(la_so, i) for i in sorted(tuan)],
        "reading": (
            "Mệnh THÔNG — chính tinh đắc giữ nguyên, không bị căn-ngăn/cắt-đứt"
            if menh_idx not in (triet | tuan) else "Mệnh bị Tuần/Triệt — cần xét giảm"
        ),
    }


def can_bang(la_so: dict) -> dict:
    """Cân bằng TRUNG THỰC: tín hiệu sáng & xấu-nhẹ (không tô hồng)."""
    menh_idx = _menh_branch_idx(la_so)
    at_menh = set(_all_stars_at(la_so, menh_idx))
    triet = set(la_so.get("triet", []))
    sang, xau = [], []
    if "Lộc Tồn" in at_menh:
        sang.append("Lộc Tồn tọa Mệnh — phúc-lộc đúng-lúc thu-tàng")
    if "Thiên Hỉ" in at_menh:
        sang.append("Thiên Hỉ tọa Mệnh — sinh khí dương, hỉ-lạc trong lò luyện")
    khoi, viet = la_so.get("sao_le", {}).get("Thiên Khôi"), la_so.get("sao_le", {}).get("Thiên Việt")
    # Khôi/Việt có thể nằm ở sao_q3/phu — fallback an theo can
    try:
        k, v = _a.thien_khoi_viet(la_so["year_stem"])
        khoi, viet = k, v
    except Exception:
        pass
    if khoi is not None and viet is not None:
        sang.append(f"Khôi Việt ({BR[khoi]}/{BR[viet]}) — mạch quý nhân (tọa quý hướng quý)")
        if khoi in triet:
            xau.append(f"Thiên Khôi ({_palace_of(la_so, khoi)}) bị Triệt — quý-nhân-tài-lộc nhịp 'đứt-nối' nửa đời đầu")
    # Lộc Tồn nội tại Lộc-Kỵ / Lộc phùng xung phá (đọc qua chính tinh Mệnh + xung)
    if "Lộc Tồn" in at_menh:
        xau.append("Lộc Tồn nội tại Lộc-Kỵ — cẩn-trọng quá độ, may mắn bị chiết giảm (cần ý thức)")
    return {"sang": sang, "xau_nhe": xau}


_DISCLAIMER = (
    "ĐỌC ĐỒNG DẠNG — KHÔNG PREDICT (Iron #4/#6/#8). Mọi tầng là TÍNH / cấu-trúc / cơ-hội "
    "(disposition), KHÔNG phải sấm kết cục. Tổ chốt: 'người tu thành tựu hay không còn lệ thuộc "
    "nhiều yếu tố khác.' Lá số cho nguyên-liệu + cánh-cửa; bước vào là việc của đương sự."
)


def dai_tong_hop(la_so: dict) -> dict:
    """Đại tổng hợp một lá số — kết tinh 40 vòng đọc Đằng Sơn. Trả structured dict (UI/PDF)."""
    menh_idx = _menh_branch_idx(la_so)
    return {
        "co": {
            "menh_branch": BR[menh_idx],
            "cuc": la_so.get("cuc"),
            "cuc_name": la_so.get("cuc_name"),
            "menh_truong_sinh_stage": _stage_at(la_so, menh_idx),
            "menh_stars": _all_stars_at(la_so, menh_idx),
        },
        "the_dung_hau_thien": the_dung_hau_thien(la_so),
        "cua_tu": cua_tu_cluster(la_so),
        "tu_mo_tu_duong": tu_mo_tu_duong(la_so),
        "tuan_triet": tuan_triet_status(la_so),
        "can_bang": can_bang(la_so),
        "disclaimer": _DISCLAIMER,
    }
