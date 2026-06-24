"""batu_process — đọc TRỌN 10 BƯỚC quy trình tình duyên Bát Tự (Tử Bình, NỮ MỆNH).

Đây là engine ĐIỀU PHỐI (orchestrator) — KHÔNG phát minh lý mới, mà TÁI DÙNG các
engine con đã có trong `engine/bat_tu/` và kho tri thức JSON trong
`engine/tinh_duyen/knowledge/`, ráp lại thành 10 BƯỚC luận tình duyên có thứ tự
sư phụ truyền dạy (Tử Bình → Thiệu Vĩ Hoa → Trích Thiên Tủy Nữ Mệnh):

    1.  Nhật chủ + Phu Thê tinh   (官 = chồng chính / 杀 = tình nhân-người mạnh)
    2.  Quan Sát vượng / nhược     (so với Nhật chủ)
    3.  THƯƠNG QUAN (gốc khắc phu) — lộ / tàng, ở trụ nào
    4.  CHẾ HÓA Thương Quan        (Ấn khắc Thương / Thực-Tài thông quan / Quan hợp)
    5.  Đại Vận → Quan Sát         (vận đi qua kích / khắc sao chồng)
    6.  Lưu Niên                   (năm khí được kích hoạt / cần giữ gìn)
    7.  Tứ trụ xung-hình-hợp       (trọng tâm NHẬT CHI = cung phối ngẫu)
    8.  NGŨ HÀNH THIẾU             (thiếu Kim = thiếu chồng, thiếu Hỏa = thiếu con…)
    9.  Thần sát                   (đào hoa / hồng loan / cô thần quả tú)
    10. Cung vị & tàng can         (官杀 ở CAN = xa, ở CHI = gần; trụ nào = sớm/muộn)

Mỗi bước trả 1 dict:
    {ten_buoc, du_lieu, luan (đã ground + _nguon[]), muc_do_anh_huong}

muc_do_anh_huong (mức độ ảnh hưởng tới tình duyên) — 3 loại:
    "truc_tiep"  — 官杀 / Thương Quan khắc Quan  (bước 1,2,3,4 cốt lõi)
    "gian_tiep"  — chế hóa / đại vận / ngũ hành thiếu (bước 4,5,8)
    "tiem_an"    — thần sát / tàng can / lưu niên  (bước 6,9,10 màu sắc)

PARADIGM (Iron Rule #4 / #6 / #8): KHÔNG BÓI. Đọc đồng dạng — lá số cho biết
TÍNH (nguyên liệu trời ban); 'mệnh' là việc XỬ LÝ tính đó (mệnh là ĐỘNG TỪ).
KHÔNG phán 'sẽ ly hôn / số khắc chồng'. Mọi luận điểm GROUND vào nguồn cổ thật
(_nguon[]) — KHÔNG bịa. Đây là điểm vượt AI-free (vốn chỉ trích web).
"""

from __future__ import annotations

from typing import Any, Optional

from engine.bat_tu.cast import cast_bat_tu
from engine.bat_tu.hoa_giai import luan_hoa_giai
from engine.bat_tu.hon_nhan import analyze_hon_nhan
from engine.bat_tu.luc_than import analyze_luc_than
from engine.bat_tu.luu_nien import (
    LUC_HAI,
    LUC_HOP,
    LUC_XUNG,
    TAM_HINH_GROUPS,
    TU_HINH,
    TUONG_HINH,
    _branch_interaction,
    analyze_luu_nien,
)
from engine.bat_tu.ngu_hanh import count_elements
from engine.bat_tu.nu_menh import analyze_nu_menh
from engine.bat_tu.thap_than import thap_than_of
from engine.bat_tu.vuong_suy_dao_nghich import detect_vuong_suy_paradox

from . import knowledge_loader as kb

METHOD_ID = "batu_tinh_duyen_10_buoc_v1"

# Sao CHỒNG ở nữ mệnh.
_QUAN = "Chính Quan"   # 正官 — chồng chính danh
_SAT = "Thất Sát"      # 七殺 — người đàn ông mạnh / tình nhân / chồng cá tính
_QUAN_SAT = (_QUAN, _SAT)
_THUONG_QUAN = "Thương Quan"   # 伤官 — gốc khắc Quan (khắc phu)
_THUC_THAN = "Thực Thần"       # 食神 — thông quan (tiết khí, hóa Thương)

_NHAT_CHI_DISCLAIMER = (
    "Engine đọc đồng dạng (Iron Rule #4/#6/#8) — KHÔNG bói, KHÔNG phán 'sẽ ly hôn / "
    "số khắc chồng'. Lá số cho biết TÍNH (nguyên liệu trời ban); 'mệnh' là việc XỬ LÝ "
    "tính đó (mệnh là ĐỘNG TỪ). Các tín hiệu 'khắc phu / cô' chỉ là CẤU TRÚC KHÍ cần "
    "ý thức + chăm sóc, KHÔNG phải bản án. Định thời chỉ là 'năm cần giữ gìn'."
)

# Element tiếng Việt -> ý nghĩa lục thân khi THIẾU (nữ mệnh) — Tử Bình kinh điển:
# hành sinh ra Quan Sát (chồng) thiếu thì khí chồng yếu nguồn; Thực Thương (con)
# thiếu thì khí con yếu nguồn. Map này phụ thuộc Nhật chủ nên tính động bên dưới.
_ELEMENT_VI = {"kim": "Kim", "mộc": "Mộc", "thủy": "Thủy", "hỏa": "Hỏa", "thổ": "Thổ"}

# Sinh / khắc vòng ngũ hành (tiếng Việt thường) để suy Quan Sát-element & con-element.
_GENERATES = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
_CONTROLS = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}


# --------------------------------------------------------------------------- #
# Helpers chung
# --------------------------------------------------------------------------- #
def _is_nu(gender: str) -> bool:
    return (gender or "").strip().lower() in ("nữ", "nu", "female", "f", "")


def _cnt(distrib: dict, name: str) -> float:
    """Đếm 1 Thập Thần: visible 1.0 + hidden 0.5 (cùng quy ước nu_menh.py)."""
    visible = distrib.get("visible", {}) or {}
    hidden = distrib.get("hidden", {}) or {}
    return float(visible.get(name, 0) or 0) + 0.5 * float(hidden.get(name, 0) or 0)


def _scan_thap_than(pillars: dict, day_master: str, targets: tuple[str, ...]) -> list[dict]:
    """Quét VỊ TRÍ của các Thập Thần `targets` trên cả CAN (lộ) và TÀNG (chi).

    Trả list {thap_than, tru, vi_tri (can/tàng), stem, can_chi_label}.
    Đây là dữ liệu gốc cho BƯỚC 1/3/10 (lộ-tàng + trụ nào).
    """
    out = []
    pos_vi = {"year": "Năm", "month": "Tháng", "day": "Ngày", "hour": "Giờ"}
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        # Thiên can lộ (trừ chính Nhật can = bản thân).
        if pos != "day":
            tt = thap_than_of(day_master, p["stem"])
            if tt in targets:
                out.append({
                    "thap_than": tt,
                    "tru": pos,
                    "tru_vi": pos_vi[pos],
                    "vi_tri": "can",        # LỘ trên thiên can
                    "lo_tang": "lộ",
                    "stem": p["stem"],
                })
        # Tàng can trong địa chi (kể cả nhật chi).
        for hs in p.get("hidden_stems", []):
            tt = thap_than_of(day_master, hs)
            if tt in targets:
                out.append({
                    "thap_than": tt,
                    "tru": pos,
                    "tru_vi": pos_vi[pos],
                    "vi_tri": "chi",        # TÀNG trong địa chi
                    "lo_tang": "tàng",
                    "stem": hs,
                    "branch": p["branch"],
                })
    return out


def _kb_nguon(*keys: str) -> list[str]:
    """Gom _nguon từ các khối knowledge cho field _nguon[] của 1 bước."""
    out = []
    bk = kb.get("batu_hon_nhan")
    if "phu_tinh" in keys:
        n = bk.get("phu_tinh", {}).get("_nguon_goc")
        if n:
            out.append(f"batu_hon_nhan.phu_tinh: {n}")
    if "phoi_ngau" in keys:
        # phối ngẫu cung dùng nhật chi.
        out.append("batu_hon_nhan.phoi_ngau_cung.y_nghia_dia_chi (nhật chi = cung phối ngẫu)")
    if "to_hop" in keys:
        n = bk.get("to_hop_then_chot", {}).get("_nguon_goc")
        if n:
            out.append(f"batu_hon_nhan.to_hop_then_chot: {n}")
    if "dao_hoa" in keys:
        n = bk.get("dao_hoa", {}).get("_nguon_goc")
        if n:
            out.append(f"batu_hon_nhan.dao_hoa: {n}")
    return out


# --------------------------------------------------------------------------- #
# BƯỚC 1 — Nhật chủ + Phu Thê tinh
# --------------------------------------------------------------------------- #
def _buoc_1_nhat_chu_phu_the(state: dict, distrib: dict) -> dict:
    pillars = state["tu_tru"]["pillars"]
    dm = state["tu_tru"]["day_master"]
    day_master = dm["stem"]

    quan_loc_tang = _scan_thap_than(pillars, day_master, _QUAN_SAT)
    chinh_quan_n = _cnt(distrib, _QUAN)
    that_sat_n = _cnt(distrib, _SAT)
    tong = chinh_quan_n + that_sat_n

    bk = kb.get("batu_hon_nhan")["phu_tinh"]
    cq = bk.get("chinh_quan", {})
    ts = bk.get("that_sat", {})

    if tong == 0:
        luan = (
            f"Nhật chủ {day_master} ({dm['element']}). Cả Chính Quan ({_QUAN}) lẫn "
            f"Thất Sát ({_SAT}) đều KHÔNG hiện trong Tứ Trụ → 'Phu tinh vô khí'. "
            "Đọc đồng dạng: cấu trúc chưa khắc rõ hình ảnh người chồng — KHÔNG nghĩa là "
            "'không lấy chồng', mà là duyên phối ngẫu cần được CHỌN + vun chủ động, "
            "tín hiệu phối ngẫu rõ hơn ở Đại Vận / Lưu Niên có Quan Sát."
        )
    else:
        hon_tap = chinh_quan_n > 0 and that_sat_n > 0
        luan = (
            f"Nhật chủ {day_master} ({dm['element']}). Sao chồng ở nữ mệnh = 官杀: "
            f"Chính Quan {chinh_quan_n:.1f} (chồng chính danh — {cq.get('tam_tinh_chong','')[:40]}…), "
            f"Thất Sát {that_sat_n:.1f} (đàn ông MẠNH/cá tính — {ts.get('tam_tinh_chong','')[:40]}…). "
        )
        if hon_tap:
            luan += (
                "Chính Quan + Thất Sát CÙNG hiện = 官杀混杂 (Quan Sát hỗn tạp) — khí chồng "
                "đa dạng/phức tạp; vận hành tốt nhất khi 'khứ Sát lưu Quan' (định hướng vào "
                "mối quan hệ chính danh, để khí Thất Sát thành động lực thay vì rối)."
            )
        else:
            chu = _QUAN if chinh_quan_n >= that_sat_n else _SAT
            luan += f"Sao chồng CHỦ ĐẠO = {chu} (đọc tính khí người bạn đời theo sao này)."

    return {
        "ten_buoc": "1. Nhật chủ + Phu Thê tinh (官=chồng / 杀=người mạnh)",
        "du_lieu": {
            "nhat_chu": day_master,
            "nhat_chu_element": dm["element"],
            "chinh_quan": round(chinh_quan_n, 1),
            "that_sat": round(that_sat_n, 1),
            "tong_quan_sat": round(tong, 1),
            "phu_tinh_lo_tang": quan_loc_tang,
            "quan_sat_hon_tap": chinh_quan_n > 0 and that_sat_n > 0,
        },
        "luan": luan,
        "_nguon": _kb_nguon("phu_tinh"),
        "muc_do_anh_huong": "truc_tiep",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 2 — Quan Sát vượng / nhược (so Nhật chủ)
# --------------------------------------------------------------------------- #
def _buoc_2_quan_sat_vuong_nhuoc(state: dict, distrib: dict) -> dict:
    dm = state["tu_tru"]["day_master"]
    assessment = state.get("ngu_hanh", {}).get("day_master_assessment", {})
    strength_tag = assessment.get("strength_tag", "")
    strength_label = assessment.get("strength_label", "")
    # 官杀 pressure = element khắc Nhật chủ (đã có sẵn trong breakdown).
    pressure = assessment.get("breakdown", {}).get("quan_sat_pressure", 0.0)
    tong_qs = _cnt(distrib, _QUAN) + _cnt(distrib, _SAT)

    bk = kb.get("batu_hon_nhan")["phu_tinh"]["trang_thai_quan_sat"]
    # phân loại trạng thái 官杀 đối SÁNH Nhật chủ.
    if tong_qs == 0:
        key, trang_thai = "vo_quan", "vô Quan"
    elif _cnt(distrib, _QUAN) > 0 and _cnt(distrib, _SAT) > 0:
        key, trang_thai = "quan_sat_hon_tap", "Quan Sát hỗn tạp"
    elif tong_qs >= 3:
        key, trang_thai = "vuong", "vượng"
    else:
        key, trang_thai = "nhuoc", "nhược"
    entry = bk.get(key) or bk.get("nhuoc") or {}

    day_weak = strength_tag in ("weak", "very_weak")
    # Cân xứng thân-Quan: cốt lõi luận hôn nhân nữ mệnh.
    if day_weak and trang_thai == "vượng":
        can_doi = (
            "Thân NHƯỢC + Quan VƯỢNG = sức ép từ phía chồng / quan hệ lớn → cần BỔ thân "
            "(Ấn = học vấn, Tỉ Kiếp = đồng minh) để khí được cân, quan hệ mới nâng đỡ nhau."
        )
    elif not day_weak and trang_thai == "vượng":
        can_doi = "Thân vững + Quan vượng = cấu trúc CÂN XỨNG — vợ chồng có thể nâng đỡ nhau."
    elif trang_thai == "nhược":
        can_doi = "Quan nhược = hình ảnh người chồng mờ nhạt hơn — duyên cần chủ động vun, chọn kỹ."
    else:
        can_doi = "Đối sánh thân–Quan để biết quan hệ cân hay lệch (xem BƯỚC 8 ngũ hành thiếu)."

    # Tái dùng vượng-suy điên đảo (Trích Thiên Tủy Ch.17) nếu lá số cực đoan.
    counts = state.get("ngu_hanh", {}).get("counts", {})
    paradox = detect_vuong_suy_paradox(dm["element"], counts)

    return {
        "ten_buoc": "2. Quan Sát vượng / nhược (so Nhật chủ)",
        "du_lieu": {
            "nhat_chu_strength_tag": strength_tag,
            "nhat_chu_strength_label": strength_label,
            "quan_sat_pressure_score": pressure,
            "tong_quan_sat": round(tong_qs, 1),
            "trang_thai_quan_sat": trang_thai,
            "vuong_suy_dien_dao": paradox,   # None nếu không cực đoan
        },
        "luan": (
            f"{entry.get('y_nghia','')} {can_doi} "
            + (f"⚡ Lá số CỰC ĐOAN: {paradox['paradigm_text']} → dụng thần đảo logic "
               f"(Trích Thiên Tủy Ch.17)." if paradox else "")
        ),
        "_nguon": (
            [f"batu_hon_nhan.trang_thai_quan_sat.{key}: {entry.get('_nguon','')}"]
            + ([paradox["source"]] if paradox else [])
        ),
        "muc_do_anh_huong": "truc_tiep",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 3 — Thương Quan (gốc khắc phu): lộ / tàng, ở trụ nào
# --------------------------------------------------------------------------- #
def _buoc_3_thuong_quan(state: dict, distrib: dict) -> dict:
    pillars = state["tu_tru"]["pillars"]
    day_master = state["tu_tru"]["day_master"]["stem"]
    tq_loc_tang = _scan_thap_than(pillars, day_master, (_THUONG_QUAN,))
    tq_n = _cnt(distrib, _THUONG_QUAN)
    tong_qs = _cnt(distrib, _QUAN) + _cnt(distrib, _SAT)

    lo = [x for x in tq_loc_tang if x["lo_tang"] == "lộ"]
    tang = [x for x in tq_loc_tang if x["lo_tang"] == "tàng"]

    if tq_n == 0:
        luan = (
            "Không thấy Thương Quan trong Tứ Trụ → KHÔNG có gốc trực tiếp khắc Quan (khắc phu) "
            "từ bẩm sinh. Khí khắc phu nếu có sẽ đến từ Đại Vận / Lưu Niên dẫn Thương Quan (BƯỚC 5,6)."
        )
        muc = "gian_tiep"
    else:
        vi_tri = []
        if lo:
            vi_tri.append("LỘ trên thiên can (" + ", ".join(f"Trụ {x['tru_vi']}" for x in lo) + ") — khắc phu rõ, biểu hiện ra ngoài")
        if tang:
            vi_tri.append("TÀNG trong địa chi (" + ", ".join(f"Trụ {x['tru_vi']}" for x in tang) + ") — khắc phu ngầm, ẩn dưới")
        manh = tq_n >= 2 and tq_n > tong_qs
        luan = (
            f"Thương Quan = {tq_n:.1f} ({'; '.join(vi_tri)}). 伤官 là gốc TRỰC TIẾP khắc 官 "
            f"(伤官见官 = Thương Quan thấy Quan): với nữ mệnh là khí khắc chồng. "
            + ("Thương Quan MẠNH hơn Quan Sát → tín hiệu khắc phu nổi trội, cần CHẾ HÓA (xem BƯỚC 4). "
               if manh else "Mức vừa phải — chế hóa được thì khí Thương Quan thành tài hoa/biểu đạt. ")
            + "Đọc đồng dạng: Thương Quan = óc phản biện, cá tính độc lập — vận hành tốt khi "
            "có Ấn dẫn (học vấn) hoặc Tài tiết (sự nghiệp) thay vì xung trực diện người bạn đời."
        )
        muc = "truc_tiep"

    return {
        "ten_buoc": "3. Thương Quan (gốc khắc phu) — lộ/tàng, ở trụ nào",
        "du_lieu": {
            "thuong_quan": round(tq_n, 1),
            "lo": lo,
            "tang": tang,
            "manh_hon_quan_sat": tq_n > tong_qs and tq_n > 0,
        },
        "luan": luan,
        "_nguon": _kb_nguon("to_hop") or ["Tử Bình: 伤官见官 — Thương Quan khắc Chính Quan (nữ = khắc phu); chế hóa qua Ấn/Tài (Trích Thiên Tủy Ch.6 Nữ Mệnh)"],
        "muc_do_anh_huong": muc,
    }


# --------------------------------------------------------------------------- #
# BƯỚC 4 — Chế hóa Thương Quan
# --------------------------------------------------------------------------- #
def _buoc_4_che_hoa(state: dict, distrib: dict) -> dict:
    tq_n = _cnt(distrib, _THUONG_QUAN)
    an_n = _cnt(distrib, "Chính Ấn") + _cnt(distrib, "Thiên Ấn") + _cnt(distrib, "Kiêu Thần")
    tai_n = _cnt(distrib, "Chính Tài") + _cnt(distrib, "Thiên Tài")
    thuc_n = _cnt(distrib, _THUC_THAN)
    tong_qs = _cnt(distrib, _QUAN) + _cnt(distrib, _SAT)

    duong_che = []
    # 1) Ấn khắc Thương (伤官配印) — đường chế hóa CAO QUÝ nhất.
    if an_n >= 1:
        duong_che.append({
            "phep": "Ấn khắc Thương (伤官配印)",
            "kha_dung": True,
            "luan": (
                f"Có Ấn = {an_n:.1f} → Ấn (học vấn, dưỡng dục, từ thiện) KHẮC Thương Quan, "
                "biến khí khắc phu thành trí tuệ hữu dụng. Đây là phép chế hóa CAO QUÝ nhất "
                "cho nữ mệnh Thương Quan."
            ),
        })
    # 2) Thực/Tài thông quan (伤官生财) — Thương Quan sinh Tài, khí thoát qua sự nghiệp.
    if tai_n >= 1:
        duong_che.append({
            "phep": "Thương Quan sinh Tài (伤官生财)",
            "kha_dung": True,
            "luan": (
                f"Có Tài = {tai_n:.1f} → Thương Quan chuyển khí xuống Tài (sự nghiệp/kinh doanh) "
                "thay vì xung Quan. Tài lại sinh Quan = vòng thông quan, gián tiếp nuôi khí chồng."
            ),
        })
    if thuc_n >= 1:
        duong_che.append({
            "phep": "Thực Thần tiết tú (食神泄秀)",
            "kha_dung": True,
            "luan": (
                f"Có Thực Thần = {thuc_n:.1f} → khí ngày tiết ra hiền hòa (Thực) thay vì gắt (Thương), "
                "làm dịu cấu trúc khắc phu."
            ),
        })
    # 3) Quan hợp / Quan vượng tự lập (官星有力) — khí chồng đủ mạnh tự đứng.
    if tong_qs >= 2 and tq_n <= tong_qs:
        duong_che.append({
            "phep": "Quan Sát hữu lực tự lập",
            "kha_dung": True,
            "luan": (
                f"Quan Sát = {tong_qs:.1f} ≥ Thương Quan = {tq_n:.1f} → khí chồng đủ sức đứng vững, "
                "Thương Quan không áp đảo được — quan hệ ổn nếu giữ giao tiếp ôn hòa."
            ),
        })

    co_che_hoa = bool(duong_che)
    if tq_n == 0:
        ket = "Không có Thương Quan nên không cần chế hóa khắc phu (BƯỚC 3 trống)."
        muc = "gian_tiep"
    elif co_che_hoa:
        ket = (
            f"Thương Quan = {tq_n:.1f} CÓ {len(duong_che)} đường chế hóa khả dụng → khí khắc phu "
            "được hóa thành tài hoa/sự nghiệp. Vận hành tốt khi Anh/Chị Ý THỨC dùng đúng kênh "
            "(học vấn / sự nghiệp) thay vì xung trực diện."
        )
        muc = "gian_tiep"
    else:
        ket = (
            f"Thương Quan = {tq_n:.1f} nhưng THIẾU Ấn / Thực / Tài để chế hóa → khí khắc phu "
            "trực diện hơn. Hóa giải qua HÀNH ĐỘNG (Iron Rule #8): bổ Ấn (học/thiện) + chọn "
            "đối tác khí trường bù đắp + đầu tư giao tiếp. KHÔNG phải bản án."
        )
        muc = "truc_tiep"

    # Tái dùng engine hoa_giai.py để gợi ý bù-hành + dưỡng sinh theo Dụng Thần.
    hoa_giai = luan_hoa_giai(state)

    return {
        "ten_buoc": "4. Chế hóa Thương Quan (Ấn khắc Thương / Thực-Tài thông quan / Quan tự lập)",
        "du_lieu": {
            "thuong_quan": round(tq_n, 1),
            "an": round(an_n, 1),
            "tai": round(tai_n, 1),
            "thuc_than": round(thuc_n, 1),
            "duong_che_hoa": duong_che,
            "co_duong_che_hoa": co_che_hoa,
            "hoa_giai_hanh_dong": {
                "bu_hanh": hoa_giai.get("bu_hanh"),
                "duong_sinh": hoa_giai.get("duong_sinh"),
            },
        },
        "luan": ket,
        "_nguon": [
            "Tử Bình: 伤官配印 / 伤官生财 — chế hóa Thương Quan (Trích Thiên Tủy Ch.6 Nữ Mệnh; Thiệu Vĩ Hoa Tập 2)",
            "engine.bat_tu.hoa_giai (Thiệu Vĩ Hoa Tập 2 Ch.24 — hóa giải qua hành động)",
        ],
        "muc_do_anh_huong": muc,
    }


# --------------------------------------------------------------------------- #
# BƯỚC 5 — Đại Vận → Quan Sát
# --------------------------------------------------------------------------- #
def _buoc_5_dai_van(state: dict) -> dict:
    day_master = state["tu_tru"]["day_master"]["stem"]
    cycles = state.get("dai_van", {}).get("cycles", [])
    qua_quan = []
    for c in cycles:
        if c.get("start_age", 0) > 75:   # tầm hữu dụng đời người
            continue
        stem_tt = thap_than_of(day_master, c["stem"])
        is_quan_sat = stem_tt in _QUAN_SAT
        is_thuong = stem_tt == _THUONG_QUAN
        if is_quan_sat or is_thuong:
            qua_quan.append({
                "cycle_index": c.get("cycle_index"),
                "stem": c["stem"],
                "branch": c["branch"],
                "start_age": c.get("start_age"),
                "end_age": c.get("end_age"),
                "thap_than_stem": stem_tt,
                "y_nghia": (
                    "đại vận dẫn KHÍ CHỒNG (官杀) — vận thường khởi/kích duyên phối ngẫu"
                    if is_quan_sat else
                    "đại vận dẫn Thương Quan — khí khắc phu được kích, năm cần GIỮ GÌN giao tiếp"
                ),
            })

    if qua_quan:
        moc = ", ".join(
            f"vận {x['stem']}{x['branch']} ({x['start_age']}-{x['end_age']}t: {x['thap_than_stem']})"
            for x in qua_quan
        )
        luan = (
            f"Các đại vận có thiên can là Quan Sát / Thương Quan: {moc}. "
            "Vận dẫn 官杀 = khí chồng được kích (duyên dễ khởi); vận dẫn Thương Quan = khí khắc phu "
            "được kích (năm cần giữ gìn). Đọc đồng dạng: đây là CỬA SỔ khí, không phải lời tiên tri."
        )
    else:
        luan = (
            "Trong tầm hữu dụng (≤75t) không có đại vận nào thiên can là Quan Sát/Thương Quan rõ. "
            "Khí phối ngẫu chủ yếu đọc qua tương tác ĐỊA CHI đại vận với nhật chi (BƯỚC 7) + Lưu Niên."
        )

    return {
        "ten_buoc": "5. Đại Vận → Quan Sát (vận kích/khắc sao chồng)",
        "du_lieu": {"dai_van_lien_quan": qua_quan},
        "luan": luan,
        "_nguon": ["engine.bat_tu.dai_van (Tử Bình: đại vận 10 năm dẫn khí Thập Thần qua thiên can)"],
        "muc_do_anh_huong": "gian_tiep",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 6 — Lưu Niên
# --------------------------------------------------------------------------- #
def _buoc_6_luu_nien(state: dict, age: Optional[int], as_of_year: Optional[int]) -> dict:
    ln = analyze_luu_nien(
        state,
        current_age=age,
        target_year=as_of_year,
        include_luu_nguyet=False,
    )
    luu_nien = ln.get("luu_nien", {})
    ln_tt = luu_nien.get("thap_than_vs_dm")
    nhat_chi = state["tu_tru"]["pillars"]["day"]["branch"]

    # Tương tác Lưu Niên vs NHẬT CHI (cung phối ngẫu) — trọng tâm tình duyên.
    vs_nhat_chi = _branch_interaction(luu_nien.get("branch", ""), nhat_chi) if luu_nien.get("branch") else []

    kich_phu = ln_tt in _QUAN_SAT
    kich_thuong = ln_tt == _THUONG_QUAN
    if kich_phu:
        y = "năm khí CHỒNG (官杀) được kích — duyên/quan hệ phối ngẫu dễ động (theo hướng cát nếu khí thuận)."
    elif kich_thuong:
        y = "năm Thương Quan kích — khí khắc phu được khơi, năm cần GIỮ GÌN giao tiếp vợ chồng."
    else:
        y = "năm không trực tiếp kích sao chồng — đọc thêm tương tác địa chi với nhật chi."

    return {
        "ten_buoc": "6. Lưu Niên (năm khí kích hoạt / cần giữ gìn)",
        "du_lieu": {
            "nam": luu_nien.get("year") or as_of_year,
            "luu_nien_can_chi": f"{luu_nien.get('stem','')} {luu_nien.get('branch','')}".strip(),
            "thap_than_vs_nhat_chu": ln_tt,
            "tuong_tac_voi_nhat_chi": vs_nhat_chi,
            "danh_gia_tong": ln.get("overall", {}),
        },
        "luan": (
            f"Lưu Niên {luu_nien.get('stem','')} {luu_nien.get('branch','')} — Thập Thần so Nhật chủ = "
            f"{ln_tt}: {y}"
            + (f" Địa chi Lưu Niên vs NHẬT CHI ({nhat_chi}): "
               + "; ".join(i["narrative"] for i in vs_nhat_chi) if vs_nhat_chi else "")
        ),
        "_nguon": ["engine.bat_tu.luu_nien (Tử Bình: Lưu Niên dẫn khí năm; tương tác địa chi với cung phối ngẫu)"],
        "muc_do_anh_huong": "tiem_an",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 7 — Tứ trụ xung-hình-hợp (trọng tâm NHẬT CHI = cung phối ngẫu)
# --------------------------------------------------------------------------- #
def _buoc_7_xung_hinh_hop(state: dict) -> dict:
    pillars = state["tu_tru"]["pillars"]
    nhat_chi = pillars["day"]["branch"]
    pos_vi = {"year": "Năm", "month": "Tháng", "hour": "Giờ"}

    # Tương tác NHẬT CHI (cung phối ngẫu) với 3 chi còn lại — TRỌNG TÂM tình duyên.
    nhat_chi_inter = []
    for pos in ("year", "month", "hour"):
        other = pillars[pos]["branch"]
        inter = _branch_interaction(nhat_chi, other)
        for it in inter:
            nhat_chi_inter.append({**it, "voi_tru": pos_vi[pos], "chi_kia": other})

    # Toàn cục: liệt kê mọi xung/hình/hợp giữa 4 chi (để thấy cấu trúc tổng).
    branches = [(pos, pillars[pos]["branch"]) for pos in ("year", "month", "day", "hour")]
    toan_cuc = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            (p1, b1), (p2, b2) = branches[i], branches[j]
            for it in _branch_interaction(b1, b2):
                if it["type"] in ("đồng chi",):
                    continue
                toan_cuc.append({**it, "giua": f"{p1}-{p2}", "chi": f"{b1}-{b2}"})

    # Đào hoa nhật chi (Tý/Ngọ/Mão/Dậu) — sức hút phối ngẫu.
    dao_hoa_nhat_chi = nhat_chi in ("Tý", "Ngọ", "Mão", "Dậu")

    nhat_chi_co_xung = any(i["type"] in ("lục xung",) for i in nhat_chi_inter)
    nhat_chi_co_hop = any(i["type"] == "lục hợp" for i in nhat_chi_inter)

    if nhat_chi_co_xung:
        luan_nc = (
            f"NHẬT CHI {nhat_chi} (cung phối ngẫu) bị LỤC XUNG → cung vợ chồng có khí động/biến — "
            "đọc đồng dạng là quan hệ cần linh hoạt, dễ thay đổi nơi-ở/hoàn cảnh, KHÔNG phán ly tán."
        )
    elif nhat_chi_co_hop:
        luan_nc = (
            f"NHẬT CHI {nhat_chi} (cung phối ngẫu) có LỤC HỢP → khí cung vợ chồng hợp, duyên gắn kết."
        )
    else:
        luan_nc = f"NHẬT CHI {nhat_chi} (cung phối ngẫu) không xung/hợp mạnh với trụ khác — cung tương đối ổn."

    if dao_hoa_nhat_chi:
        luan_nc += f" Nhật chi {nhat_chi} là một trong tứ chính (子午卯酉) = đào hoa toạ mệnh, sức hút phối ngẫu nổi."

    return {
        "ten_buoc": "7. Tứ trụ xung-hình-hợp (trọng tâm NHẬT CHI = cung phối ngẫu)",
        "du_lieu": {
            "nhat_chi": nhat_chi,
            "nhat_chi_tuong_tac": nhat_chi_inter,
            "nhat_chi_dao_hoa": dao_hoa_nhat_chi,
            "toan_cuc_tuong_tac": toan_cuc,
        },
        "luan": luan_nc,
        "_nguon": _kb_nguon("phoi_ngau") + ["engine.bat_tu.luu_nien tables (Tử Bình: lục hợp/lục xung/lục hại/tam hình giữa địa chi; nhật chi = cung phối ngẫu)"],
        "muc_do_anh_huong": "truc_tiep" if nhat_chi_co_xung or nhat_chi_co_hop else "gian_tiep",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 8 — Ngũ hành thiếu
# --------------------------------------------------------------------------- #
def _buoc_8_ngu_hanh_thieu(state: dict) -> dict:
    dm_el = state["tu_tru"]["day_master"]["element"]
    counts = state.get("ngu_hanh", {}).get("counts", {}) or count_elements(state["tu_tru"]["pillars"])

    # Hành chồng (官杀) = hành KHẮC Nhật chủ; hành con (Thực Thương) = hành Nhật chủ SINH.
    hanh_chong = _CONTROLS.get(dm_el, "")        # khắc DM
    # _CONTROLS[x] = hành mà x khắc → cần đảo để tìm hành khắc DM.
    hanh_chong = next((k for k, v in _CONTROLS.items() if v == dm_el), "")
    hanh_con = _GENERATES.get(dm_el, "")          # DM sinh ra

    total = sum(counts.values()) or 1.0
    thieu = [el for el, v in counts.items() if v < 1.0]      # gần như vắng mặt
    nguy = {el: round(v, 1) for el, v in counts.items() if v < 1.0}

    notes = []
    chong_thieu = counts.get(hanh_chong, 0) < 1.0
    con_thieu = counts.get(hanh_con, 0) < 1.0
    if hanh_chong and chong_thieu:
        notes.append(
            f"THIẾU {_ELEMENT_VI.get(hanh_chong, hanh_chong)} (hành khắc Nhật chủ = hành CHỒNG/官杀, "
            f"chỉ {counts.get(hanh_chong,0):.1f}) → 'thiếu hành chồng': hình ảnh người bạn đời mờ "
            "nguồn khí, duyên cần chủ động vun + bù hành này qua môi trường (màu/hướng/nghề)."
        )
    if hanh_con and con_thieu:
        notes.append(
            f"THIẾU {_ELEMENT_VI.get(hanh_con, hanh_con)} (hành Nhật chủ sinh ra = hành CON/Thực Thương, "
            f"chỉ {counts.get(hanh_con,0):.1f}) → 'thiếu hành con': khí con cái yếu nguồn, "
            "bù hành này + xem Đại Vận có dẫn Thực Thương không."
        )
    if not notes:
        notes.append(
            "Ngũ hành tương đối đủ ở 2 hành then chốt (hành chồng + hành con) — "
            "không có tín hiệu 'thiếu chồng / thiếu con' theo cấu trúc bẩm sinh."
        )

    return {
        "ten_buoc": "8. Ngũ hành thiếu (thiếu Kim=thiếu chồng, thiếu Hỏa=thiếu con…)",
        "du_lieu": {
            "nhat_chu_element": dm_el,
            "counts": {k: round(v, 1) for k, v in counts.items()},
            "hanh_chong": hanh_chong,
            "hanh_con": hanh_con,
            "hanh_thieu": thieu,
            "hanh_thieu_chi_tiet": nguy,
            "thieu_hanh_chong": chong_thieu,
            "thieu_hanh_con": con_thieu,
        },
        "luan": " ".join(notes),
        "_nguon": [
            "Tử Bình: hành KHẮC Nhật chủ = Quan Sát (chồng ở nữ mệnh); hành Nhật chủ SINH = Thực Thương (con). "
            "Thiếu hành = thiếu nguồn khí lục thân tương ứng (Trích Thiên Tủy Ch.6 Nữ Mệnh).",
            "engine.bat_tu.ngu_hanh.count_elements",
        ],
        "muc_do_anh_huong": "gian_tiep",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 9 — Thần sát (đào hoa / hồng loan / cô thần quả tú)
# --------------------------------------------------------------------------- #
_THAN_SAT_DUYEN = {
    "Đào Hoa": ("duyên", "sức hút giới khác, duyên rộng — vận hành tốt khi đi cùng chính khí; hợp nghề giao tiếp/nghệ thuật."),
    "Hồng Loan": ("duyên", "sao hôn nhân/hỉ sự — duyên lành, năm gặp dễ khởi chuyện vui đôi lứa."),
    "Thiên Hỷ": ("duyên", "sao hỉ sự — vui mừng, sinh nở, lễ tốt."),
    "Hồng Diễm": ("duyên", "sức hấp dẫn nồng — duyên tình đậm."),
    "Cô Thần": ("co", "sao cô đơn (nam) — khí lẻ loi; đọc đồng dạng là cần chủ động kết nối, KHÔNG phải án cô độc."),
    "Quả Tú": ("co", "sao cô đơn (nữ) — khí đơn lẻ; vận hành tốt khi mở lòng + vun quan hệ chủ động, KHÔNG phải số góa."),
    "Âm Dương Xô Lệch": ("canh_bao", "ngày Âm Dương Xô Lệch (Thiệu Vĩ Hoa tr.144) — khí trường vợ chồng nghịch, cần đầu tư cao vào giao tiếp + chọn đối tác bù đắp; KHÔNG predict ly hôn."),
    "Khôi Cương": ("canh_bao", "trụ ngày Khôi Cương — cá tính sắc bén, độc lập; duyên hợp người tôn trọng sự độc lập đó."),
}


def _buoc_9_than_sat(state: dict) -> dict:
    than_sat = state.get("than_sat", []) or []
    duyen, co, canh_bao, khac = [], [], [], []
    for s in than_sat:
        name = s.get("name", "")
        loai, mota = _THAN_SAT_DUYEN.get(name, (None, None))
        item = {
            "name": name,
            "tru": s.get("found_at_pillar"),
            "branch_or_stem": s.get("branch_or_stem"),
            "polarity": s.get("polarity"),
            "y_nghia_duyen": mota,
        }
        if loai == "duyen":
            duyen.append(item)
        elif loai == "co":
            co.append(item)
        elif loai == "canh_bao":
            canh_bao.append(item)
        # các thần sát khác không liên quan duyên → bỏ qua khỏi 3 nhóm trên.

    parts = []
    if duyen:
        parts.append("Sao DUYÊN: " + ", ".join(f"{x['name']} (Trụ {x['tru']})" for x in duyen) + " → sức hút phối ngẫu, năm gặp dễ khởi chuyện vui.")
    if co:
        parts.append("Sao CÔ (đơn lẻ): " + ", ".join(f"{x['name']} (Trụ {x['tru']})" for x in co) + " → khí lẻ loi; đọc đồng dạng = cần CHỦ ĐỘNG kết nối, KHÔNG phải bản án cô độc/góa.")
    if canh_bao:
        parts.append("Tín hiệu CẦN Ý THỨC: " + ", ".join(x["name"] for x in canh_bao) + " → đầu tư giao tiếp + chọn đối tác khí trường bù đắp.")
    if not parts:
        parts.append("Không có thần sát duyên/cô nổi bật liên quan tình duyên.")

    return {
        "ten_buoc": "9. Thần sát (đào hoa / hồng loan / cô thần quả tú)",
        "du_lieu": {
            "sao_duyen": duyen,
            "sao_co": co,
            "sao_canh_bao": canh_bao,
        },
        "luan": " ".join(parts),
        "_nguon": _kb_nguon("dao_hoa") + ["engine.bat_tu.than_sat (三命通會 + 滴天髓 + 子平真詮; Thiệu Vĩ Hoa tr.144 Âm Dương Xô Lệch)"],
        "muc_do_anh_huong": "tiem_an",
    }


# --------------------------------------------------------------------------- #
# BƯỚC 10 — Cung vị & tàng can (xa/gần, sớm/muộn)
# --------------------------------------------------------------------------- #
_TRU_SOM_MUON = {
    "year": ("rất sớm / duyên thiếu thời", "Trụ Năm (0-15t)"),
    "month": ("sớm — tuổi thanh xuân", "Trụ Tháng (16-30t)"),
    "day": ("đúng tuổi lập gia đình — gần nhất với bản thân", "Trụ Ngày (31-45t, cung phối ngẫu)"),
    "hour": ("muộn / hậu vận", "Trụ Giờ (46t+)"),
}


def _buoc_10_cung_vi_tang_can(state: dict, distrib: dict) -> dict:
    pillars = state["tu_tru"]["pillars"]
    day_master = state["tu_tru"]["day_master"]["stem"]
    nhat_chi = pillars["day"]["branch"]

    quan_loc_tang = _scan_thap_than(pillars, day_master, _QUAN_SAT)

    # 官杀 ở CAN = xa (lộ, dễ thấy nhưng quan hệ "bên ngoài"); ở CHI = gần (tàng,
    # khí thân mật). 官杀 ở NHẬT CHI = gần nhất (chồng "trong nhà").
    o_can = [x for x in quan_loc_tang if x["vi_tri"] == "can"]
    o_chi = [x for x in quan_loc_tang if x["vi_tri"] == "chi"]
    o_nhat_chi = [x for x in o_chi if x["tru"] == "day"]

    # Phân tích phối ngẫu cung (nhật chi) qua knowledge JSON grounded.
    phoi_ngau = kb.get("batu_hon_nhan")["phoi_ngau_cung"].get("y_nghia_dia_chi", {}).get(nhat_chi)

    # Sớm/muộn theo trụ có Quan Sát đầu tiên.
    som_muon = None
    if quan_loc_tang:
        first = sorted(quan_loc_tang, key=lambda x: ["year", "month", "day", "hour"].index(x["tru"]))[0]
        som_muon = {"tru": first["tru"], "mo_ta": _TRU_SOM_MUON[first["tru"]][0], "khung": _TRU_SOM_MUON[first["tru"]][1]}

    parts = []
    if o_nhat_chi:
        parts.append(
            "官杀 TÀNG ngay NHẬT CHI (cung phối ngẫu) = chồng 'trong nhà', khí phối ngẫu GẦN + rõ — "
            "tín hiệu duyên phối ngẫu mật thiết."
        )
    elif o_chi:
        parts.append("官杀 TÀNG trong địa chi (không ở nhật chi) = khí chồng GẦN nhưng ẩn, cần thời điểm khơi mở.")
    if o_can:
        parts.append("官杀 LỘ trên thiên can = khí chồng 'ở xa/bên ngoài', dễ thấy nhưng quan hệ thiên về hình thức/xã giao hơn.")
    if not quan_loc_tang:
        parts.append("Không có 官杀 trên cả can lẫn chi — xem khí phối ngẫu qua Đại Vận/Lưu Niên (BƯỚC 5,6).")
    if som_muon:
        parts.append(f"Quan Sát xuất hiện sớm nhất ở {som_muon['khung']} → duyên ứng {som_muon['mo_ta']}.")

    return {
        "ten_buoc": "10. Cung vị & tàng can (官杀 ở can=xa/chi=gần; trụ nào=sớm/muộn)",
        "du_lieu": {
            "nhat_chi": nhat_chi,
            "quan_sat_o_can": o_can,
            "quan_sat_o_chi": o_chi,
            "quan_sat_o_nhat_chi": o_nhat_chi,
            "phoi_ngau_cung_luan": phoi_ngau,
            "som_muon": som_muon,
        },
        "luan": " ".join(parts),
        "_nguon": _kb_nguon("phu_tinh", "phoi_ngau"),
        "muc_do_anh_huong": "tiem_an",
    }


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def doc_batu_10_buoc(
    bat_tu_state: dict,
    gender: str = "nữ",
    as_of_year: Optional[int] = None,
) -> dict:
    """Đọc TRỌN 10 BƯỚC quy trình tình duyên Bát Tự (nữ mệnh).

    Args:
        bat_tu_state: output của `engine.bat_tu.cast.cast_bat_tu(...)`.
        gender: mặc định 'nữ' (engine cho nữ mệnh — sao chồng = 官杀).
        as_of_year: năm dương tham chiếu cho Lưu Niên + tuổi (None = năm hiện tại).

    Returns:
        dict {method_id, gender, input, buoc[10], cross_grounding, _disclaimer}.
        Mỗi phần tử buoc = {ten_buoc, du_lieu, luan, muc_do_anh_huong, _nguon[]}.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state phải chứa khoá 'tu_tru' (output của cast_bat_tu).")

    distrib = bat_tu_state.get("thap_than_distribution", {}) or {}

    # Tuổi (xấp xỉ) để dò Đại Vận hiện tại cho Lưu Niên.
    age = None
    try:
        from datetime import datetime
        birth_year = int(bat_tu_state["tu_tru"]["pillars"]["year"].get("solar_year")
                         or bat_tu_state.get("birth_datetime_local", "0")[:4])
        ref_year = as_of_year or datetime.now().year
        if birth_year:
            age = max(ref_year - birth_year, 0)
    except Exception:
        age = None

    buoc = [
        _buoc_1_nhat_chu_phu_the(bat_tu_state, distrib),
        _buoc_2_quan_sat_vuong_nhuoc(bat_tu_state, distrib),
        _buoc_3_thuong_quan(bat_tu_state, distrib),
        _buoc_4_che_hoa(bat_tu_state, distrib),
        _buoc_5_dai_van(bat_tu_state),
        _buoc_6_luu_nien(bat_tu_state, age, as_of_year),
        _buoc_7_xung_hinh_hop(bat_tu_state),
        _buoc_8_ngu_hanh_thieu(bat_tu_state),
        _buoc_9_than_sat(bat_tu_state),
        _buoc_10_cung_vi_tang_can(bat_tu_state, distrib),
    ]

    # Cross-grounding: tái dùng nu_menh.py + hon_nhan.py + luc_than.py để đối chiếu chéo.
    cross = {}
    try:
        cross["nu_menh"] = analyze_nu_menh(bat_tu_state, gender="nu" if _is_nu(gender) else "nam")
    except Exception as e:  # pragma: no cover
        cross["nu_menh"] = {"error": str(e)}
    try:
        cross["hon_nhan"] = analyze_hon_nhan(bat_tu_state)
    except Exception as e:  # pragma: no cover
        cross["hon_nhan"] = {"error": str(e)}
    try:
        lt = analyze_luc_than(bat_tu_state)
        # chỉ giữ quan hệ chồng/con cho gọn.
        cross["luc_than_phu_tu"] = [
            r for r in lt.get("relations", [])
            if any(k in (r.get("name", "")) for k in ("Chồng", "Con", "phu", "Phu"))
        ]
    except Exception as e:  # pragma: no cover
        cross["luc_than_phu_tu"] = {"error": str(e)}

    return {
        "method_id": METHOD_ID,
        "gender": gender,
        "input": {
            "as_of_year": as_of_year,
            "tuoi_xap_xi": age,
            "nhat_chu": bat_tu_state["tu_tru"]["day_master"]["stem"],
            "nhat_chi": bat_tu_state["tu_tru"]["pillars"]["day"]["branch"],
            "ganzhi": bat_tu_state["tu_tru"].get("ganzhi_raw"),
        },
        "buoc": buoc,
        "cross_grounding": cross,
        "_disclaimer": _NHAT_CHI_DISCLAIMER,
    }


__all__ = ["doc_batu_10_buoc", "METHOD_ID"]
