"""cham_cap — CHẤM CẤP ĐỘ thử thách hôn nhân (NỮ MỆNH, 5 cấp, ngôn ngữ xây dựng).

Tầng GỘP (synthesis) — KHÔNG tính lại lý. Đọc các FACTOR mà `quy_trinh_day_du`
(12 bước Tử Vi + 10 bước Bát Tự) ĐÃ tính, đối chiếu bảng tín hiệu trong
`knowledge/cham_cap_do.json`, suy ra:

    {cap_do (1-5), ten_cap, do_thay_doi_duoc, phan_loai,
     tin_hieu_kich_hoat: [yếu tố THẬT trên lá này khớp cấp],
     lo_trinh: [hành động cụ thể theo cấp],
     nguyen_tac_vang, muc_do_thu_thach, ranh_gioi, _nguon}

PARADIGM (Iron Rule #4/#6/#8): KHÔNG BÓI — mệnh là ĐỘNG TỪ. Cấp độ đo ĐỘ KHÓ của
NGUYÊN LIỆU trời ban (TÍNH), KHÔNG đo kết cục. NGÔN NGỮ XÂY DỰNG (constructive):
được GỌI TÊN cái khó như KHÁI NIỆM phân tích ('cấu trúc Thương Quan', 'áp lực lên
cung phối ngẫu', 'mức độ thử thách 3/5') + chấm cấp + chỉ lối — KHÔNG lời-phán-vào-
người ('em sẽ khắc chồng / số cô quả / chắc chắn ly hôn').

GROUNDING: #2 framework (cham_cap_do.json) + 王亭之 深造講義 + Thiệu Vĩ Hoa (chế hóa)
+ Trích Thiên Tủy. Mọi tín hiệu kích hoạt CHỈ từ factor thật (KHÔNG bịa).

Quy tắc chọn cấp (theo cham_cap_do.json._meta.cach_dung_engine):
  - Quét tín hiệu từng cấp; KHỚP CẤP CAO NHẤT mà tín hiệu thoả.
  - Mơ hồ giữa 2 cấp → chọn cấp THẤP hơn (an toàn, không thổi phồng) + cờ 'ranh_gioi'.
  - Mọi kết quả đính kèm nguyen_tac_vang (TIỀM NĂNG, không phải án).
"""
from __future__ import annotations

from typing import Any, Optional

from . import gender_lens as GL
from . import knowledge_loader as kb

METHOD_ID = "cham_cap_do_nu_menh_v1"

# ── CONCEPT-MAP theo giới (NAM mirror) ──────────────────────────────────────
# cham_cap_do.json + signal text viết theo NỮ (伤官 khắc 官). Với NAM, khái niệm đối
# xứng là 比劫 đoạt 财: 'Thương Quan' → 'Tỷ Kiếp', 'Quan (sao phối ngẫu)' → 'Tài
# (sao phối ngẫu)'. Áp SAU GL.apply_gender (lo chồng→vợ / khắc phu→khắc thê) để
# nam đọc đúng cơ học mà KHÔNG bao giờ phán 'tái hôn/khắc chồng'.
# Thứ tự: cụm DÀI trước (để 'Thương Quan vượng' không bị 'Quan' nuốt).
_CONCEPT_MAP_NAM = [
    ("Thương Quan", "Tỷ Kiếp"),
    ("伤官见官", "比劫夺财"),
    ("食伤", "食伤"),                 # giữ (cùng tên 2 giới)
    ("Quan Sát", "Tài tinh"),
    ("Quan (sao phối ngẫu)", "Tài (sao phối ngẫu)"),
    ("thân-Quan", "thân-Tài"),
    ("lấn Quan", "đoạt Tài"),
    ("Quan nhược", "Tài nhược"),
    ("Quan còn nguồn", "Tài còn nguồn"),
    ("khí 'chồng'", "khí 'vợ'"),
    ("cái tôi/sáng tạo", "bản ngã/đua tranh"),
]


def _concept_gender(text: Optional[str], gender: Optional[str]) -> str:
    """Đổi text theo giới: GL.apply_gender (chồng→vợ…) RỒI concept-map (Thương Quan→
    Tỷ Kiếp…). Nữ (flagship) trả nguyên văn."""
    if text is None:
        return ""
    if not GL.is_male(gender):
        return text
    out = GL.apply_gender(text, "nam")
    for src, dst in _CONCEPT_MAP_NAM:
        out = out.replace(src, dst)
    return out


def _concept_gender_list(items, gender: Optional[str]) -> list:
    return [_concept_gender(x, gender) if isinstance(x, str) else x for x in (items or [])]


# Mức trạng thái cung (Tử Vi) coi là HÃM/yếu (tín hiệu khó) vs ĐẮC/tốt (tín hiệu lành).
_MUC_HAM = {"hãm", "lạc", "bình"}
_MUC_DAC = {"miếu", "vượng", "đắc"}

# Chính tinh tình-cảm (khi HÃM → khí lạnh nhạt = L2).
_SAO_TINH_CAM = ("Thiên Đồng", "Thái Âm")
# Chính tinh cương / biến (khi HÃM → va chạm = L3).
_SAO_CUONG_BIEN = ("Cự Môn", "Liêm Trinh", "Phá Quân")
# Chính tinh chủ tốt cho phối ngẫu (đắc = nền lành L1).
_SAO_PHU_THE_LANH = ("Thiên Đồng", "Thái Âm", "Thiên Lương", "Thiên Tướng")
# Cụm sát rất nặng (L5).
_SAO_TU_SAT = ("Thất Sát", "Vũ Khúc")

# Sao cô / sầu tại cung phối ngẫu.
_CO_THAN_QUA_TU = ("Cô Thần", "Quả Tú")
_KHOC_HU = ("Thiên Khốc", "Thiên Hư")

# Sát tinh (lục sát + Hình) — đếm độ nặng tại cung Phu Thê.
_SAT_TINH = (
    "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh",
    "Địa Không", "Địa Kiếp", "Thiên Hình",
)


# --------------------------------------------------------------------------- #
# Trích FACTOR từ quy_trinh_day_du + la_so (KHÔNG tính lại lý)
# --------------------------------------------------------------------------- #
def _bt_buoc(qt: dict, idx: int) -> dict:
    """Lấy bước Bát Tự thứ idx (0-based) từ quy_trinh_day_du."""
    buoc = (qt.get("bat_tu_10_buoc") or {}).get("buoc") or []
    return buoc[idx] if 0 <= idx < len(buoc) else {}


def _tv_buoc(qt: dict, idx: int) -> dict:
    """Lấy bước Tử Vi thứ idx (0-based) từ quy_trinh_day_du."""
    buoc = (qt.get("tu_vi_12_buoc") or {}).get("buoc") or []
    return buoc[idx] if 0 <= idx < len(buoc) else {}


def _phu_the_index(la_so: dict) -> Optional[int]:
    """Branch-index cung Phu Thê (palaces[2])."""
    palaces = la_so.get("palaces") or []
    if len(palaces) > 2:
        return palaces[2].get("branch_index")
    return None


def _stars_q2_at(la_so: dict, branch_index: Optional[int]) -> set[str]:
    """Các sao trong nhóm sao_q2 (Cô Thần/Quả Tú/Khốc/Hư…) toạ branch_index."""
    if branch_index is None:
        return set()
    g = la_so.get("sao_q2") or {}
    return {s for s, i in g.items() if i == branch_index}


def _extract_factors(qt: dict, la_so: dict, bat_tu_state: dict) -> dict:
    """Gom MỌI factor cham_cap cần — CHỈ đọc từ dữ liệu engine đã tính.

    Trả dict thuần để bước quét tín hiệu dễ kiểm + dễ test.
    """
    # ── Tử Vi: cung Phu Thê (bước 1) ──────────────────────────────────────────
    tv1 = _tv_buoc(qt, 0).get("du_lieu", {}) or {}
    pt_chinh = list(tv1.get("chinh_tinh") or [])
    pt_trang_thai = tv1.get("trang_thai") or []  # [{sao, muc, nhan}]
    pt_sat = list(tv1.get("sat_tinh") or [])
    pt_tu_hoa = tv1.get("tu_hoa") or []           # [{hoa, sao}]
    pt_chi = tv1.get("chi")

    # mức cao nhất của các chính tinh Phu Thê (đắc hay hãm).
    muc_set = {(t.get("muc") or "").strip().lower() for t in pt_trang_thai}
    co_dac = bool(muc_set & _MUC_DAC)
    co_ham = bool(muc_set & _MUC_HAM)

    # Hóa Kỵ nhập Phu Thê?
    co_hoa_ky_phu_the = any((h.get("hoa") == "Kỵ") for h in pt_tu_hoa)

    # Cô Thần / Quả Tú / Khốc / Hư tại cung Phu Thê (đọc trực tiếp từ la_so).
    pt_idx = _phu_the_index(la_so)
    q2_phu_the = _stars_q2_at(la_so, pt_idx)
    co_than_qua_tu = sorted(q2_phu_the & set(_CO_THAN_QUA_TU))
    khoc_hu = sorted(q2_phu_the & set(_KHOC_HU))

    # Sát tinh nặng tại Phu Thê (đếm).
    sat_o_phu_the = [s for s in pt_sat if s in _SAT_TINH]
    so_sat = len(sat_o_phu_the)

    # Cụm sát rất nặng (Thất Sát/Vũ Khúc + Hóa Kỵ + nhiều sát) → tín hiệu L5.
    tu_sat_o_phu_the = [s for s in pt_chinh if s in _SAO_TU_SAT]

    # Chính tinh tình-cảm HÃM (L2) / cương-biến HÃM (L3) / phu-thê-lành ĐẮC (L1).
    def _sao_o_muc(saos: tuple[str, ...], ham: bool) -> list[str]:
        out = []
        for t in pt_trang_thai:
            sao = t.get("sao")
            muc = (t.get("muc") or "").strip().lower()
            if sao in saos and ((muc in _MUC_HAM) if ham else (muc in _MUC_DAC)):
                out.append(sao)
        return out

    sao_tinh_cam_ham = _sao_o_muc(_SAO_TINH_CAM, ham=True)
    sao_cuong_bien_ham = _sao_o_muc(_SAO_CUONG_BIEN, ham=True)
    sao_phu_the_lanh_dac = _sao_o_muc(_SAO_PHU_THE_LANH, ham=False)

    # ── Bát Tự: Quan Sát (bước 2), Thương Quan (bước 3), Chế hóa (bước 4) ──────
    bt2 = _bt_buoc(qt, 1).get("du_lieu", {}) or {}
    bt3 = _bt_buoc(qt, 2).get("du_lieu", {}) or {}
    bt4 = _bt_buoc(qt, 3).get("du_lieu", {}) or {}

    nhat_chu_tag = bt2.get("nhat_chu_strength_tag")       # 'weak'|'strong'|...
    trang_thai_quan_sat = bt2.get("trang_thai_quan_sat")  # nhãn vi
    tong_quan_sat = float(bt2.get("tong_quan_sat") or 0.0)

    thuong_quan = float(bt3.get("thuong_quan") or 0.0)
    tq_manh_hon_qs = bool(bt3.get("manh_hon_quan_sat"))
    co_che_hoa = bool(bt4.get("co_duong_che_hoa"))

    # ── NGƯỠNG SỐ HỌC = QUY ƯỚC ENGINE (KHÔNG phải con số có thẩm quyền cổ văn) ──
    # Issue V2 #2: _nguon chỉ ground KHÁI NIỆM (伤官见官, chế hóa, thân-Quan cân lệch);
    # còn các MỐC SỐ dưới đây (≥2.0 vượng, ≥3.0 cực vượng, <1.0 nhược, ≤0 cực nhược)
    # là heuristic NỘI BỘ engine — đơn vị = "điểm Thập Thần" (visible 1.0 + hidden 0.5,
    # quy ước nu_menh.py/_cnt). Cổ văn nói ĐỊNH TÍNH ("Thương Quan vượng", "Quan nhược"),
    # engine lượng-hoá để chấm cấp nhất quán; KHÔNG được ngộ nhận con số có thẩm quyền cổ.
    _TQ_VUONG = 2.0       # quy ước: Thương Quan ≥2 điểm = "vượng"
    _TQ_CUC_VUONG = 3.0   # quy ước: ≥3 điểm = "cực vượng" (đương lệnh/thành cách)
    _QUAN_NHUOC = 1.0     # quy ước: tổng Quan Sát <1 điểm = "nhược"

    # Thương Quan VƯỢNG (≥ngưỡng VÀ mạnh hơn Quan Sát) — định nghĩa theo bước 3.
    tq_vuong = thuong_quan >= _TQ_VUONG and tq_manh_hon_qs
    # Quan (sao chồng) NHƯỢC: tổng Quan Sát thấp.
    quan_nhuoc = tong_quan_sat < _QUAN_NHUOC
    quan_cuc_nhuoc = tong_quan_sat <= 0.0
    # Thương Quan CỰC VƯỢNG (≥ngưỡng cao VÀ mạnh hơn Quan Sát).
    tq_cuc_vuong = thuong_quan >= _TQ_CUC_VUONG and tq_manh_hon_qs

    # Thân VƯỢNG (nhat_chu_tag) — Issue V2 #3: factor có sẵn nhưng detector L4 chưa
    # dùng. "Thân vượng lấn Quan quá nhược" (mô tả L4 JSON) cần tag này để khớp đúng
    # cấu trúc cân-lệch âm-dương, thay vì để JSON mô tả rộng hơn code thực thi.
    than_vuong = nhat_chu_tag in ("strong", "very_strong")

    return {
        # Tử Vi cung Phu Thê
        "pt_chi": pt_chi,
        "pt_chinh_tinh": pt_chinh,
        "pt_co_dac": co_dac,
        "pt_co_ham": co_ham,
        "pt_so_sat": so_sat,
        "pt_sat_tinh": sat_o_phu_the,
        "pt_hoa_ky": co_hoa_ky_phu_the,
        "co_than_qua_tu": co_than_qua_tu,
        "khoc_hu": khoc_hu,
        "tu_sat_o_phu_the": tu_sat_o_phu_the,
        "sao_tinh_cam_ham": sao_tinh_cam_ham,
        "sao_cuong_bien_ham": sao_cuong_bien_ham,
        "sao_phu_the_lanh_dac": sao_phu_the_lanh_dac,
        # Bát Tự
        "nhat_chu_tag": nhat_chu_tag,
        "than_vuong": than_vuong,
        "trang_thai_quan_sat": trang_thai_quan_sat,
        "tong_quan_sat": tong_quan_sat,
        "thuong_quan": thuong_quan,
        "tq_vuong": tq_vuong,
        "tq_cuc_vuong": tq_cuc_vuong,
        "co_che_hoa": co_che_hoa,
        "quan_nhuoc": quan_nhuoc,
        "quan_cuc_nhuoc": quan_cuc_nhuoc,
        # Ghi rõ ngưỡng = quy ước engine (truy vết + chống ngộ nhận thẩm quyền cổ).
        "_nguong_quy_uoc_engine": {
            "thuong_quan_vuong": _TQ_VUONG,
            "thuong_quan_cuc_vuong": _TQ_CUC_VUONG,
            "quan_nhuoc_duoi": _QUAN_NHUOC,
            "_ghi_chu": (
                "Mốc số là QUY ƯỚC ENGINE (đơn vị: điểm Thập Thần, visible 1.0 + "
                "hidden 0.5), KHÔNG phải con số có thẩm quyền cổ văn. Cổ văn chỉ nói "
                "định tính (vượng/nhược); engine lượng-hoá để chấm cấp nhất quán."
            ),
        },
    }


# --------------------------------------------------------------------------- #
# Quét tín hiệu THẬT khớp từng cấp — trả (so_tin_hieu, [tín hiệu mô tả])
# --------------------------------------------------------------------------- #
# Mỗi cấp trả (core_signals, support_signals):
#   - core = tín hiệu CẤU TRÚC quyết định cấp (đủ 1 core là khớp cấp).
#   - support = tín hiệu phụ trợ (chỉ tô đậm, KHÔNG tự đẩy lên cấp cao — tránh
#     thổi phồng, vd 1 Cô Thần đơn lẻ không được đẩy thẳng lên L4).
def _signals_L5(f: dict) -> tuple[list[str], list[str]]:
    core, sup = [], []
    # CORE — Bát Tự: Thương Quan CỰC VƯỢNG không chế + Quan cực nhược (không lối thông).
    if f["tq_cuc_vuong"] and not f["co_che_hoa"] and f["quan_cuc_nhuoc"]:
        core.append(
            f"Thương Quan cực vượng ({f['thuong_quan']:.1f}) KHÔNG chế hóa + "
            "Quan (sao phối ngẫu) cực nhược — không lối thông quan"
        )
    # CORE — Tử Vi: cung Phu Thê tụ sát rất nặng + Hóa Kỵ + KHÔNG cát hoá chế giải.
    if f["tu_sat_o_phu_the"] and f["pt_hoa_ky"] and f["pt_so_sat"] >= 2 and not f["pt_co_dac"]:
        core.append(
            f"cung Phu Thê tụ {'+'.join(f['tu_sat_o_phu_the'])} + Hóa Kỵ + "
            f"{f['pt_so_sat']} sát tinh, KHÔNG cát hoá chế giải (cụm sát cực nặng)"
        )
    return core, sup


def _signals_L4(f: dict) -> tuple[list[str], list[str]]:
    core, sup = [], []
    # CORE — Bát Tự: Thương Quan vượng KHÔNG chế + Quan nhược (cái tôi áp đảo khí phối ngẫu).
    if f["tq_vuong"] and not f["co_che_hoa"] and f["quan_nhuoc"]:
        core.append(
            f"Thương Quan vượng ({f['thuong_quan']:.1f}) KHÔNG chế hóa + Quan "
            "(sao phối ngẫu) nhược → cấu trúc 'cái tôi/sáng tạo' áp đảo khí phối ngẫu"
        )
    # CORE — Bát Tự: THÂN VƯỢNG lấn Quan quá nhược (cân-lệch âm-dương rõ).
    # Issue V2 #3: dùng nhat_chu_tag (than_vuong) đúng như mô tả JSON L4
    # ("thân vượng lấn Quan quá nhược → cân-lệch âm-dương rõ"). Yêu cầu Thương Quan
    # vượng-không-chế đi kèm để KHÔNG fire chỉ vì thân khoẻ (thân vượng + Quan đủ
    # mạnh = cân xứng, KHÔNG phải L4 — xem _buoc_2 'thân vững + Quan vượng = cân xứng').
    if f["than_vuong"] and f["quan_nhuoc"] and f["tq_vuong"] and not f["co_che_hoa"]:
        core.append(
            "Thân (Nhật Chủ) VƯỢNG lấn Quan (sao phối ngẫu) quá nhược + Thương Quan "
            "vượng không chế → cân-lệch âm-dương rõ (khí bản thân áp đảo khí phối ngẫu)"
        )
    # CORE — Tử Vi: cung Phu Thê có sát + Khốc/Hư (khí sầu/trống) — áp lực mạnh có cấu trúc.
    if f["pt_so_sat"] >= 1 and f["khoc_hu"]:
        core.append(
            f"cung Phu Thê có sát tinh ({', '.join(f['pt_sat_tinh'])}) + "
            f"{', '.join(f['khoc_hu'])} (khí sầu/trống)"
        )
    # SUPPORT — Cô Thần và/hoặc Quả Tú (đóng cung phối ngẫu): chỉ tô đậm, không đẩy cấp.
    if f["co_than_qua_tu"]:
        sup.append(
            f"{', '.join(f['co_than_qua_tu'])} đóng cung phối ngẫu "
            "(khuynh hướng độc lập/khép mạnh)"
        )
    # SUPPORT — Hóa Kỵ chạm Phu Thê đi kèm cụm sát.
    if f["pt_hoa_ky"] and f["pt_so_sat"] >= 1:
        sup.append("Hóa Kỵ chạm cung Phu Thê đi kèm cụm sát")
    return core, sup


def _signals_L3(f: dict) -> tuple[list[str], list[str]]:
    core, sup = [], []
    # CORE — Tử Vi: chính tinh cương/biến HÃM (khẩu thiệt/cương/biến).
    if f["sao_cuong_bien_ham"]:
        extra = (f" + {', '.join(f['co_than_qua_tu'])}" if f["co_than_qua_tu"] else "")
        core.append(
            f"cung Phu Thê có {', '.join(f['sao_cuong_bien_ham'])} HÃM "
            f"(khẩu thiệt/cương/biến động){extra}"
        )
    # CORE — Bát Tự: Thương Quan vượng NHƯNG CÓ chế hóa sẵn (khó thật, có thuốc).
    if f["tq_vuong"] and f["co_che_hoa"]:
        core.append(
            f"Thương Quan vượng ({f['thuong_quan']:.1f}) NHƯNG CÓ chế hóa sẵn "
            "(Tài thông quan / Ấn chế) → khó là thật nhưng có thuốc"
        )
    # CORE — Cô Thần + Quả Tú CẢ HAI đóng cung phối ngẫu (cô lập có cấu trúc, không thuốc TV).
    if len(f["co_than_qua_tu"]) >= 2:
        core.append(
            f"{', '.join(f['co_than_qua_tu'])} CẢ HAI đóng/giáp cung phối ngẫu "
            "(khuynh hướng độc lập rõ)"
        )
    # SUPPORT — sát mức vừa kèm Hóa Kỵ nhẹ.
    if f["pt_so_sat"] == 1 and f["pt_hoa_ky"]:
        sup.append("sát tinh mức vừa tại cung Phu Thê kèm Hóa Kỵ nhẹ")
    return core, sup


def _signals_L2(f: dict) -> tuple[list[str], list[str]]:
    core, sup = [], []
    # CORE — Tử Vi: chính tinh tình-cảm HÃM (lạnh nhạt).
    if f["sao_tinh_cam_ham"]:
        core.append(
            f"cung Phu Thê có {', '.join(f['sao_tinh_cam_ham'])} HÃM "
            "→ khí lạnh nhạt, ngại biểu lộ"
        )
    # CORE — Cô Thần HOẶC Quả Tú đơn lẻ (khuynh hướng khép, chưa thành cô lập).
    if len(f["co_than_qua_tu"]) == 1:
        core.append(f"{f['co_than_qua_tu'][0]} đơn lẻ (khuynh hướng khép nhẹ)")
    # SUPPORT — Thương Quan không quá vượng (không khắc mạnh) — nền của L2.
    if 0 < f["thuong_quan"] < 2.0 and not f["tq_vuong"]:
        sup.append(
            f"Thương Quan không quá vượng ({f['thuong_quan']:.1f}) → "
            "không tạo áp lực mạnh lên sao phối ngẫu"
        )
    return core, sup


def _signals_L1(f: dict) -> tuple[list[str], list[str]]:
    core, sup = [], []
    # CORE — Tử Vi: cung Phu Thê đắc/miếu (chính tinh lành) + ít sát.
    if f["pt_co_dac"] and f["pt_so_sat"] <= 1:
        sao = (", ".join(f["sao_phu_the_lanh_dac"])
               if f["sao_phu_the_lanh_dac"] else ", ".join(f["pt_chinh_tinh"]))
        core.append(f"cung Phu Thê đắc/miếu ({sao}) + chỉ {f['pt_so_sat']} sát nhẹ")
    # SUPPORT — KHÔNG Hóa Kỵ tại Phu Thê.
    if not f["pt_hoa_ky"]:
        sup.append("KHÔNG có Hóa Kỵ đóng cung Phu Thê")
    # SUPPORT — Bát Tự: Thương Quan hài hoà (vô Thương hoặc có chế hóa, không vượng).
    if f["thuong_quan"] == 0 or (f["thuong_quan"] > 0 and f["co_che_hoa"] and not f["tq_vuong"]):
        sup.append("Bát Tự: khí Thương Quan hài hoà (vô Thương hoặc có chế hóa, không vượng)")
    # SUPPORT — không (hoặc rất mờ) Cô Thần/Quả Tú.
    if not f["co_than_qua_tu"]:
        sup.append("không có Cô Thần / Quả Tú ở cung phối ngẫu")
    return core, sup


# --------------------------------------------------------------------------- #
# ĐỐI CHIẾU CHÉO Tử Vi ⇔ Bát Tự (Issue V2 #1) — chống thổi phồng khi 2 phái lệch
# --------------------------------------------------------------------------- #
# Paradigm (Iron Rule #3 kept_all + tuvi_batu_reconcile.json): nơi 2 phái HỘI TỤ →
# kết luận chắc; nơi DỊ BIỆT → điểm chung làm CHẮC, điểm riêng làm ĐIỀU KIỆN/sắc thái.
# Trước đây cham_cap quét cấp-cao-nhất bất kể phái nào fire core → lá có CẢ
# (Thương Quan vượng-không-chế = core L4 Bát Tự) LẪN (cát tinh đắc Phu Thê = lành rõ
# Tử Vi) bị chốt thẳng L4 = thổi phồng. Lớp này: nếu cấp cao (≥4) do MỘT phái đẩy lên
# mà phái KIA báo LÀNH RÕ → HẠ 1 cấp + cờ doi_chieu_cheo (an toàn, không thổi phồng).
def _core_tu_phai_bat_tu(f: dict) -> bool:
    """Core cấp cao có đến từ cấu trúc BÁT TỰ (Thương Quan / thân-Quan)?"""
    return (
        (f["tq_vuong"] and not f["co_che_hoa"] and f["quan_nhuoc"]) or
        (f["tq_cuc_vuong"] and not f["co_che_hoa"] and f["quan_cuc_nhuoc"]) or
        (f["than_vuong"] and f["quan_nhuoc"] and f["tq_vuong"] and not f["co_che_hoa"])
    )


def _core_tu_phai_tu_vi(f: dict) -> bool:
    """Core cấp cao có đến từ cấu trúc TỬ VI (sát + Khốc/Hư / cụm sát + Hóa Kỵ)?"""
    return (
        (f["pt_so_sat"] >= 1 and bool(f["khoc_hu"])) or
        (bool(f["tu_sat_o_phu_the"]) and f["pt_hoa_ky"] and f["pt_so_sat"] >= 2 and not f["pt_co_dac"])
    )


def _tu_vi_lanh_ro(f: dict) -> bool:
    """Tử Vi báo cung Phu Thê LÀNH RÕ: chính tinh đắc/miếu + ít sát + KHÔNG Hóa Kỵ +
    KHÔNG Cô Thần/Quả Tú (đúng L1 core TV kèm support sạch)."""
    return (
        f["pt_co_dac"] and f["pt_so_sat"] <= 1 and not f["pt_hoa_ky"]
        and not f["co_than_qua_tu"] and not f["khoc_hu"]
    )


def _bat_tu_lanh_ro(f: dict) -> bool:
    """Bát Tự báo khí phối ngẫu LÀNH RÕ: Thương Quan hài hoà (vô Thương, hoặc có chế +
    không vượng) VÀ Quan không cực nhược (sao chồng còn nguồn khí)."""
    tq_hai_hoa = (
        f["thuong_quan"] == 0
        or (f["thuong_quan"] > 0 and f["co_che_hoa"] and not f["tq_vuong"])
    )
    return tq_hai_hoa and not f["quan_cuc_nhuoc"]


def _reconcile_cheo(chosen: int, f: dict) -> tuple[int, Optional[dict]]:
    """Đối chiếu chéo 2 phái trước khi chốt cấp CAO (≥4).

    Trả (cap_sau_dieu_chinh, ghi_chu | None). Chỉ HẠ TỐI ĐA 1 cấp (không tụt sâu),
    và chỉ khi cấp cao do MỘT phái đẩy lên còn phái KIA lành rõ (mâu thuẫn thật).
    """
    if chosen < 4:
        return chosen, None

    bt_day = _core_tu_phai_bat_tu(f)
    tv_day = _core_tu_phai_tu_vi(f)

    # Cấp cao do BÁT TỰ đẩy (Tử Vi KHÔNG góp core) nhưng Tử Vi lành rõ → dị biệt.
    if bt_day and not tv_day and _tu_vi_lanh_ro(f):
        return chosen - 1, {
            "phai_day_cap_cao": "bat_tu",
            "phai_bao_lanh": "tu_vi",
            "ly_do": (
                "Bát Tự cho cấu trúc Thương Quan/thân-Quan nặng (đẩy cấp cao) NHƯNG "
                "Tử Vi cho cung Phu Thê đắc/miếu, ít sát, không Hóa Kỵ/Cô Thần (lành "
                "rõ) → hai phái DỊ BIỆT. Theo kept_all (Iron Rule #3): điểm chung làm "
                "chắc, điểm riêng làm điều kiện → HẠ 1 cấp (an toàn, không thổi phồng)."
            ),
        }
    # Cấp cao do TỬ VI đẩy (Bát Tự KHÔNG góp core) nhưng Bát Tự lành rõ → dị biệt.
    if tv_day and not bt_day and _bat_tu_lanh_ro(f):
        return chosen - 1, {
            "phai_day_cap_cao": "tu_vi",
            "phai_bao_lanh": "bat_tu",
            "ly_do": (
                "Tử Vi cho cung Phu Thê tụ sát/Khốc-Hư (đẩy cấp cao) NHƯNG Bát Tự cho "
                "khí Thương Quan hài hoà + Quan còn nguồn (lành rõ) → hai phái DỊ BIỆT. "
                "Theo kept_all (Iron Rule #3): HẠ 1 cấp (an toàn, không thổi phồng)."
            ),
        }
    return chosen, None


# --------------------------------------------------------------------------- #
# Public API — chấm cấp 5 bậc theo CORE signal (support chỉ tô đậm, không đẩy cấp)
# --------------------------------------------------------------------------- #
def cham_cap_do(
    quy_trinh_day_du: dict,
    la_so: dict,
    bat_tu_state: dict,
    gender: str = "nữ",
) -> dict:
    """Chấm CẤP ĐỘ thử thách hôn nhân (nữ mệnh) từ factor đã tính.

    Args:
        quy_trinh_day_du: output build_quy_trinh_day_du (12 bước TV + 10 bước BT).
        la_so: lá số đã an sao (để đọc Cô Thần/Quả Tú tại cung Phu Thê).
        bat_tu_state: bát tự đã lập (giữ chữ ký API; factor chính đọc qua quy_trinh).
        gender: 'nữ' (engine cho nữ mệnh).

    Returns:
        dict {cap_do, ten_cap, muc_do_thu_thach, do_thay_doi_duoc, phan_loai,
              tin_hieu_kich_hoat, lo_trinh, ranh_gioi, nguyen_tac_vang, _nguon,
              _factors}.
    """
    data = kb.get("cham_cap_do")
    cac_cap = data["cac_cap"]
    nguyen_tac_vang = data["nguyen_tac_vang"]

    f = _extract_factors(quy_trinh_day_du, la_so, bat_tu_state)

    # Quét tín hiệu mỗi cấp → (core, support).
    detectors = {
        5: _signals_L5, 4: _signals_L4, 3: _signals_L3,
        2: _signals_L2, 1: _signals_L1,
    }
    core: dict[int, list[str]] = {}
    support: dict[int, list[str]] = {}
    for n, det in detectors.items():
        c, s = det(f)
        core[n], support[n] = c, s

    # KHỚP CẤP CAO NHẤT có ≥1 tín hiệu CORE (5 → 1). Support KHÔNG đẩy cấp
    # (tránh thổi phồng: 1 Cô Thần đơn lẻ không nâng lên L4/L5).
    chosen = None
    for n in (5, 4, 3, 2, 1):
        if core[n]:
            chosen = n
            break
    if chosen is None:
        # Không cấp nào có core → mặc định L1 (an toàn, không thổi phồng độ khó).
        chosen = 1

    # ĐỐI CHIẾU CHÉO Tử Vi ⇔ Bát Tự (Issue V2 #1): nếu cấp CAO (≥4) do MỘT phái đẩy
    # lên mà phái KIA báo LÀNH RÕ → hai phái dị biệt → HẠ 1 cấp (kept_all, không thổi
    # phồng). Chạy sau khi đã có chosen; tối đa hạ 1 cấp.
    cap_truoc_doi_chieu = chosen
    chosen, doi_chieu_cheo = _reconcile_cheo(chosen, f)
    if doi_chieu_cheo:
        doi_chieu_cheo["cap_truoc_doi_chieu"] = cap_truoc_doi_chieu
        doi_chieu_cheo["cap_sau_doi_chieu"] = chosen
        doi_chieu_cheo["_nguon"] = (
            "tuvi_batu_reconcile.json (HỘI TỤ→chắc, DỊ BIỆT→điểm chung làm chắc + "
            "điểm riêng làm điều kiện); Iron Rule #3 (kept_all đa phái)"
        )

    # Cờ RANH GIỚI: cấp cao hơn liền kề có tín hiệu (core HOẶC support) nhưng chưa
    # đủ core để khớp → giáp ranh, sage diễn đạt mềm. Theo _meta: chọn cấp THẤP hơn.
    ranh_gioi = False
    if chosen < 5 and (core[chosen + 1] or support[chosen + 1]):
        ranh_gioi = True
    # L3 vốn là RANH GIỚI quan trọng nhất của thang (đánh dấu luôn).
    if chosen == 3:
        ranh_gioi = True

    # tin_hieu_kich_hoat = core (bằng chứng chính) + support của CẤP ĐÃ CHỌN.
    tin_hieu = list(core[chosen]) + list(support[chosen])
    # Nếu đã HẠ cấp do đối chiếu chéo: cấp mới có thể không có core riêng → giữ bằng
    # chứng cấu trúc của cấp gốc (gắn nhãn 'đã hạ cấp') để không mất tín hiệu THẬT.
    if doi_chieu_cheo and not core[chosen]:
        tin_hieu = [
            f"(đã hạ từ cấp {cap_truoc_doi_chieu} do đối chiếu chéo 2 phái) " + t
            for t in core[cap_truoc_doi_chieu]
        ] + list(support[chosen])

    key = f"L{chosen}"
    cap_entry = cac_cap[key]

    # Áp lăng kính giới lên MỌI field người-đọc-thấy (NAM: chồng→vợ + Thương Quan→
    # Tỷ Kiếp…). Nữ (flagship) giữ nguyên văn.
    return {
        "method_id": METHOD_ID,
        "gender": gender,
        "cap_do": cap_entry["cap"],
        "ten_cap": _concept_gender(cap_entry["ten_cap"], gender),
        "muc_do_thu_thach": cap_entry["muc_do_thu_thach"],
        "do_thay_doi_duoc": cap_entry["do_thay_doi_duoc"],
        "phan_loai": cap_entry["phan_loai"],
        "mo_ta": _concept_gender(cap_entry["mo_ta"], gender),
        # Tín hiệu THẬT trên lá này (đã khớp cấp đã chọn) — bằng chứng, không bịa.
        "tin_hieu_kich_hoat": _concept_gender_list(tin_hieu, gender),
        "lo_trinh": _concept_gender_list(list(cap_entry.get("lo_trinh") or []), gender),
        "ranh_gioi": ranh_gioi,
        # Đối chiếu chéo 2 phái (None nếu không có dị biệt hạ cấp) — minh bạch quá trình.
        "doi_chieu_cheo": doi_chieu_cheo,
        "nguyen_tac_vang": nguyen_tac_vang,
        # Phép rèn cốt lõi (cho cấp L1-L3) — đính kèm để sage chỉ lối cụ thể.
        "lo_trinh_ren": data.get("lo_trinh_ren"),
        "_nguon": cap_entry.get("_nguon"),
        # Snapshot factor (để truy vết + test) — KHÔNG surface raw verdict.
        "_factors": f,
        # Toàn cảnh thang 5 cấp (UI hiển thị thanh tiến trình).
        "_thang_5_cap": data["_meta"].get("thang_5_cap_tong_quan"),
    }


__all__ = ["cham_cap_do", "METHOD_ID"]
