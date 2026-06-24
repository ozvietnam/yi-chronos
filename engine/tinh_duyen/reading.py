"""read_tinh_duyen — engine DETERMINISTIC xem tình duyên NỮ MỆNH.

Đây là engine MỞ RỘNG (không lặp lại) engine con
`engine.cross_paradigm.hon_nhan_song_phai.luan_hon_nhan_song_phai`:
- engine con cho FOUNDATION v0 (12 khía cạnh, lead_reading có thể '(unsourced)')
- engine NÀY tự LÀM GIÀU từ kho tri thức 6 JSON (đó là giá trị chính):
  personality theo Mệnh chính tinh, cung Phu Thê Tử Vi grounded _nguon,
  Bát Tự hôn nhân (官杀 + 日支 + đào hoa), reconcile 8 chủ đề, cách cục,
  định thời mức đại-vận, life-stage theo tuổi.

PARADIGM (Iron Rule #4/#6/#8): KHÔNG BÓI — đọc đồng dạng, mệnh là động từ.
KHÔNG gọi LLM (sage narrate sau). KHÔNG phán 'sẽ ly hôn / số cô quả';
định thời diễn đạt 'năm cần giữ gìn'. Mọi luận điểm bám _nguon từ kho tri thức.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from engine.bat_tu.cast import cast_bat_tu
from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
from engine.tu_vi.from_birth import cast_la_so_from_birth

from . import knowledge_loader as kb

METHOD_ID = "tinh_duyen_nu_menh_v1"

_DISCLAIMER = (
    "Engine đọc đồng dạng — KHÔNG bói, KHÔNG phán định mệnh. "
    "Lá số/bát tự cho biết TÍNH (nguyên liệu trời ban); 'mệnh' là việc XỬ LÝ tính đó "
    "(mệnh là động từ — Iron Rule #8). Các mốc 'định thời' chỉ là 'năm khí được kích hoạt' "
    "hoặc 'năm cần giữ gìn', KHÔNG phải lời tiên tri."
)

# 12 địa chi theo thứ tự index 0..11 (Tý ở 0).
_BRANCHES = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
]

# 官杀 = sao chồng ở nữ mệnh.
_QUAN_SAT = ("Chính Quan", "Thất Sát")

# Đào hoa cát (kích hoạt hỉ sự) dùng cho định thời.
_DAO_HOA_KICH_HOAT = ("Hồng Loan", "Thiên Hỉ")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _parse_birth(birth_datetime_local: str) -> datetime:
    """Parse 'YYYY-MM-DDTHH:MM' (cho phép thiếu phút / có giây)."""
    s = birth_datetime_local.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Fallback: chỉ lấy phần ngày.
    return datetime.strptime(s[:10], "%Y-%m-%d")


def _calc_age(birth: datetime, as_of_year: Optional[int]) -> int:
    """Tuổi (mụ-độc-lập, theo năm dương) tại as_of_year (mặc định năm hiện tại)."""
    year = as_of_year if as_of_year else datetime.now().year
    age = year - birth.year
    # Nếu chưa tới sinh nhật trong năm tham chiếu thì trừ 1 (xấp xỉ tuổi thật).
    if as_of_year is None:
        today = datetime.now()
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
    return max(age, 0)


def _stars_at(index_map: dict, branch_index: int) -> list[str]:
    """Các sao (key) có branch_index == branch_index."""
    return [s for s, i in index_map.items() if i == branch_index]


def _opposite(branch_index: int) -> int:
    return (branch_index + 6) % 12


def _count_quan_sat(thap_than_distribution: dict) -> dict:
    """Đếm 官杀 (Chính Quan + Thất Sát) từ visible + hidden."""
    visible = thap_than_distribution.get("visible", {}) or {}
    hidden = thap_than_distribution.get("hidden", {}) or {}
    out = {}
    total = 0
    for name in _QUAN_SAT:
        v = int(visible.get(name, 0))
        h = int(hidden.get(name, 0))
        out[name] = {"visible": v, "hidden": h, "total": v + h}
        total += v + h
    out["tong_quan_sat"] = total
    return out


# --------------------------------------------------------------------------- #
# (d) STAGE
# --------------------------------------------------------------------------- #
def _pick_stage(age: int) -> dict:
    stages = kb.get("life_stages")["stages"]
    chosen = None
    for st in stages:
        if st["tuoi_min"] <= age <= st["tuoi_max"]:
            chosen = st
            break
    if chosen is None:
        # Ngoài biên: clamp vào chặng đầu/cuối.
        chosen = stages[0] if age < stages[0]["tuoi_min"] else stages[-1]
    return {
        "tuoi": age,
        "stage_id": chosen["id"],
        "tuoi_min": chosen["tuoi_min"],
        "tuoi_max": chosen["tuoi_max"],
        "moi_truong": chosen.get("moi_truong"),
        "tam_ly_cot_loi": chosen.get("tam_ly_cot_loi"),
        "cau_hoi_chinh": chosen.get("cau_hoi_chinh"),
        "nhu_cau": chosen.get("nhu_cau"),
        "giong_van": chosen.get("giong_van"),
        "do_sau": chosen.get("do_sau"),
        "goi": chosen.get("goi"),
        "gia_xu_goi_y": chosen.get("gia_xu_goi_y"),
        "_nguon": chosen.get("_nguon"),
    }


# --------------------------------------------------------------------------- #
# (e) PERSONALITY
# --------------------------------------------------------------------------- #
def _personality(menh_chinh_tinh: list[str], nhat_chu: str, thap_than: dict) -> dict:
    pdict = kb.get("personality")
    profiles = []
    for star in menh_chinh_tinh:
        key = kb.name_to_key(star)
        entry = pdict.get(key)
        if not entry:
            continue
        profiles.append({
            "sao": star,
            "ten_han": entry.get("ten_han"),
            "khi_chat": entry.get("khi_chat"),
            "cach_yeu": entry.get("cach_yeu"),
            "khau_vi_giao_tiep": entry.get("khau_vi_giao_tiep"),
            "doi_chieu_batu_thap_than": entry.get("doi_chieu_batu_thap_than"),
            "_nguon": entry.get("_nguon"),
        })
    return {
        "menh_chinh_tinh": menh_chinh_tinh,
        "vo_chinh_dieu": len(menh_chinh_tinh) == 0,
        "profiles": profiles,
        "doi_chieu_batu": {
            "nhat_chu": nhat_chu,
            "thap_than_distribution": thap_than,
        },
    }


# --------------------------------------------------------------------------- #
# (f) CUNG PHU THÊ TỬ VI
# --------------------------------------------------------------------------- #
def _cung_phu_the_tuvi(la_so: dict, phu_the_idx: int) -> dict:
    tp = kb.get("tuvi_phuthe")
    chinh_map = tp["chinh_tinh_phu_the"]
    dao_map = tp["dao_hoa_tinh"]
    sat_map = tp["sat_tinh_phu_the"]
    hoa_map = tp["tu_hoa_phu_the"]

    chinh_tinh = _stars_at(la_so["chinh_tinh"], phu_the_idx)
    muon_doi_cung = False
    if not chinh_tinh:
        # Vô chính diệu cung Phu Thê -> mượn sao đối cung (index ±6).
        chinh_tinh = _stars_at(la_so["chinh_tinh"], _opposite(phu_the_idx))
        muon_doi_cung = True

    dao_hoa = _stars_at(la_so["sao_q2"], phu_the_idx)
    sat = _stars_at(la_so["sat_tinh"], phu_the_idx)
    # Tứ Hóa nhập Phu: hoá nào mà sao mang hoá đó toạ cung Phu Thê.
    tu_hoa_nhap_phu = [
        {"hoa": h, "sao": star}
        for h, star in la_so["tu_hoa"].items()
        if la_so["chinh_tinh"].get(star) == phu_the_idx
    ]

    # Ghép tri thức grounded _nguon.
    chinh_tinh_luan = []
    for star in chinh_tinh:
        entry = chinh_map.get(kb.name_to_key(star))
        if entry:
            chinh_tinh_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "tinh_chat_phoi_ngau": entry.get("tinh_chat_phoi_ngau"),
                "cat_hung": entry.get("cat_hung"),
                "dieu_can_chu_y": entry.get("dieu_can_chu_y"),
                "_nguon": entry.get("_nguon"),
            })

    dao_hoa_luan = []
    for star in dao_hoa:
        entry = dao_map.get(kb.name_to_key(star))
        if entry:
            dao_hoa_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "y_nghia_duyen": entry.get("y_nghia_duyen"),
                "_nguon": entry.get("_nguon"),
            })

    sat_luan = []
    for star in sat:
        entry = sat_map.get(kb.name_to_key(star))
        if entry:
            sat_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "y_nghia": entry.get("y_nghia"),
                "_nguon": entry.get("_nguon"),
            })

    # Tứ Hóa nhập Phu -> tra theo hoa_loc/hoa_quyen/hoa_khoa/hoa_ky.
    _hoa_key = {"Lộc": "hoa_loc", "Quyền": "hoa_quyen", "Khoa": "hoa_khoa", "Kỵ": "hoa_ky"}
    tu_hoa_luan = []
    for item in tu_hoa_nhap_phu:
        entry = hoa_map.get(_hoa_key.get(item["hoa"], ""))
        if entry:
            tu_hoa_luan.append({
                "hoa": item["hoa"],
                "sao": item["sao"],
                "ten_han": entry.get("ten_han"),
                "y_nghia": entry.get("y_nghia"),
                "_nguon": entry.get("_nguon"),
            })

    return {
        "phu_the_branch_index": phu_the_idx,
        "phu_the_branch": _BRANCHES[phu_the_idx],
        "muon_sao_doi_cung": muon_doi_cung,
        "chinh_tinh": chinh_tinh,
        "dao_hoa": dao_hoa,
        "sat_tinh": sat,
        "tu_hoa_nhap_phu": tu_hoa_nhap_phu,
        "chinh_tinh_luan": chinh_tinh_luan,
        "dao_hoa_luan": dao_hoa_luan,
        "sat_tinh_luan": sat_luan,
        "tu_hoa_luan": tu_hoa_luan,
    }


# --------------------------------------------------------------------------- #
# (g) BÁT TỰ HÔN NHÂN
# --------------------------------------------------------------------------- #
def _trang_thai_quan_sat(quan_sat_count: dict) -> str:
    total = quan_sat_count.get("tong_quan_sat", 0)
    if total == 0:
        return "vo_hinh"   # 官杀 không hiện rõ
    if total >= 3:
        return "vuong"
    return "binh_hoa"


def _batu_hon_nhan(bat_tu_state: dict, quan_sat_count: dict) -> dict:
    bk = kb.get("batu_hon_nhan")
    day = bat_tu_state["tu_tru"]["pillars"]["day"]
    nhat_chi = day["branch"]
    nhat_chu = bat_tu_state["tu_tru"]["day_master"]["stem"]

    # Trạng thái 官杀.
    trang_thai = _trang_thai_quan_sat(quan_sat_count)
    tt_dict = bk["phu_tinh"].get("trang_thai_quan_sat", {})
    trang_thai_luan = tt_dict.get(trang_thai) or tt_dict.get("binh_hoa")

    # 日支 phối ngẫu cung.
    dia_chi_map = bk["phoi_ngau_cung"].get("y_nghia_dia_chi", {})
    phoi_ngau_luan = dia_chi_map.get(nhat_chi)

    # Đào hoa tứ chi (Tý/Mão/Ngọ/Dậu).
    dao_hoa_chi = nhat_chi in ("Tý", "Mão", "Ngọ", "Dậu")

    return {
        "nhat_chu": nhat_chu,
        "nhat_chi": nhat_chi,
        "phu_tinh_la": list(_QUAN_SAT),
        "quan_sat_count": quan_sat_count,
        "trang_thai_quan_sat": trang_thai,
        "trang_thai_luan": trang_thai_luan,
        "phoi_ngau_cung_luan": phoi_ngau_luan,
        "nhat_chi_la_dao_hoa": dao_hoa_chi,
        "to_hop_then_chot": bk.get("to_hop_then_chot"),
        "_nguon": bk["phu_tinh"].get("_nguon_goc"),
    }


# --------------------------------------------------------------------------- #
# (h) RECONCILE
# --------------------------------------------------------------------------- #
def _reconcile(base: dict) -> list[dict]:
    rec = kb.get("reconcile")["chu_de"]
    khia_canh = base.get("khia_canh", []) or []
    # concord lấy theo thứ tự khía cạnh base (best-effort), gắn vào 8 chủ đề.
    out = []
    for i, cd in enumerate(rec):
        concord = None
        base_ref = None
        if i < len(khia_canh):
            concord = khia_canh[i].get("concord")
            base_ref = {"id": khia_canh[i].get("id"), "ten": khia_canh[i].get("ten")}
        out.append({
            "chu_de": cd.get("chu_de"),
            "tuvi_doc_bang": cd.get("tuvi_doc_bang"),
            "batu_doc_bang": cd.get("batu_doc_bang"),
            "khi_HOI_TU": cd.get("khi_HOI_TU"),
            "khi_DI_BIET": cd.get("khi_DI_BIET"),
            "phai_uu_tien": cd.get("phai_uu_tien"),
            "concord_tu_base": concord,
            "base_khia_canh_ref": base_ref,
            "_nguon": cd.get("_nguon"),
        })
    return out


# --------------------------------------------------------------------------- #
# (i) CÁCH CỤC
# --------------------------------------------------------------------------- #
def _cung_index_by_name(la_so: dict, cung_name: str) -> Optional[int]:
    """Tra branch_index của 1 cung theo tên ('Mệnh', 'Phu Thê', ...)."""
    if cung_name == "Mệnh":
        return la_so["menh_index"]
    for p in la_so["palaces"]:
        if p.get("name") == cung_name:
            return p.get("branch_index")
    return None


def _all_stars_at(la_so: dict, branch_index: int) -> set[str]:
    found = set()
    for grp in ("chinh_tinh", "sao_q2", "sat_tinh"):
        found.update(_stars_at(la_so.get(grp, {}), branch_index))
    return found


def _cach_cuc(la_so: dict) -> list[dict]:
    cc = kb.get("cach_cuc")["cach_cuc"]
    hits = []
    for c in cc:
        dk = c.get("dieu_kien_phat_hien", {}) or {}
        sao_req = dk.get("sao") or []
        if not sao_req:
            continue
        cung = dk.get("cung", "Mệnh")
        idx = _cung_index_by_name(la_so, cung)
        if idx is None:
            continue
        present = _all_stars_at(la_so, idx)
        # Khớp: tất cả sao điều kiện cùng có mặt tại cung đó.
        if all(s in present for s in sao_req):
            hits.append({
                "ten_cach": c.get("ten_cach"),
                "han_tu": c.get("han_tu"),
                "cung": cung,
                "sao_khop": sao_req,
                "y_nghia_duyen": c.get("y_nghia_duyen"),
                "cat_hung": c.get("cat_hung"),
                "_nguon": c.get("_nguon"),
            })
    return hits


# --------------------------------------------------------------------------- #
# (j) ĐỊNH THỜI
# --------------------------------------------------------------------------- #
def _dai_van_hien_tai(la_so: dict, age: int) -> Optional[dict]:
    for dv in la_so.get("dai_van", []):
        if dv.get("start_age", 0) <= age <= dv.get("end_age", 0):
            return dv
    return None


def _dinh_thoi(la_so: dict, age: int, phu_the_idx: int) -> dict:
    tp_dinh = kb.get("tuvi_phuthe").get("dinh_thoi", {})
    dv_hien_tai = _dai_van_hien_tai(la_so, age)

    # Năm KÍCH HOẠT (mức đại-vận): đại vận có cung đi qua nơi có Hồng Loan / Thiên Hỉ
    # hoặc Hồng Loan/Thiên Hỉ ở Mệnh / Phu Thê.
    kich_hoat_sao = {
        s: i for s, i in la_so["sao_q2"].items() if s in _DAO_HOA_KICH_HOAT
    }
    nam_kich_hoat = []
    for dv in la_so.get("dai_van", []):
        bi = dv.get("branch_index")
        touched = [s for s, i in kich_hoat_sao.items() if i == bi]
        if touched:
            nam_kich_hoat.append({
                "cycle_index": dv.get("cycle_index"),
                "branch": dv.get("branch"),
                "start_age": dv.get("start_age"),
                "end_age": dv.get("end_age"),
                "sao_kich_hoat": touched,
                "dien_dat": "đại vận có khí hỉ sự / duyên được kích hoạt",
            })

    # Năm CẦN GIỮ GÌN (mức đại-vận): đại vận đi qua cung Phu Thê mà nơi đó có
    # Hóa Kỵ nhập hoặc Kình Dương toạ -> năm cần chăm sóc (KHÔNG phán ly hôn).
    ky_star = la_so["tu_hoa"].get("Kỵ")
    ky_idx = la_so["chinh_tinh"].get(ky_star) if ky_star else None
    kinh_idx = la_so["sat_tinh"].get("Kình Dương")
    nam_giu_gin = []
    for dv in la_so.get("dai_van", []):
        bi = dv.get("branch_index")
        reasons = []
        if bi == phu_the_idx and ky_idx == phu_the_idx:
            reasons.append(f"Hóa Kỵ ({ky_star}) tại cung Phu Thê")
        if bi == phu_the_idx and kinh_idx == phu_the_idx:
            reasons.append("Kình Dương tại cung Phu Thê")
        # Đại vận đi tới chính cung Phu Thê cũng là chặng tiêu điểm quan hệ.
        if bi == phu_the_idx and not reasons:
            reasons.append("đại vận đi qua cung Phu Thê — chặng tiêu điểm quan hệ")
        if reasons:
            nam_giu_gin.append({
                "cycle_index": dv.get("cycle_index"),
                "branch": dv.get("branch"),
                "start_age": dv.get("start_age"),
                "end_age": dv.get("end_age"),
                "ly_do": reasons,
                "dien_dat": "năm cần GIỮ GÌN / chăm sóc quan hệ (không phải tiên tri ly tán)",
            })

    return {
        "muc_do": "dai_van",
        "dai_van_hien_tai": dv_hien_tai,
        "nam_kich_hoat": nam_kich_hoat,
        "nam_can_giu_gin": nam_giu_gin,
        "phuong_phap": tp_dinh.get("phuong_phap"),
        "bien_chinh_hien_dai": tp_dinh.get("bien_chinh_hien_dai"),
        "_nguon": tp_dinh.get("_ghi_chu"),
    }


# --------------------------------------------------------------------------- #
# Sources gom lại
# --------------------------------------------------------------------------- #
def _collect_sources() -> list[str]:
    out = []
    for key in ("tuvi_phuthe", "batu_hon_nhan", "reconcile", "personality",
                "cach_cuc", "life_stages"):
        meta = kb.get(key).get("_meta", {})
        src = meta.get("nguon") or meta.get("_nguon") or meta.get("sach") or meta.get("title")
        if isinstance(src, (list, tuple)):
            src = "; ".join(str(x) for x in src)
        if src:
            out.append(f"{key}: {src}")
        else:
            out.append(key)
    return out


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def read_tinh_duyen(
    birth_datetime_local: str,
    gender: str = "nữ",
    timezone: str = "Asia/Ho_Chi_Minh",
    as_of_year: Optional[int] = None,
) -> dict:
    """Đọc tình duyên nữ mệnh — trả DỮ LIỆU CẤU TRÚC (sage narrate sau).

    Args:
        birth_datetime_local: 'YYYY-MM-DDTHH:MM' giờ địa phương.
        gender: mặc định 'nữ' (engine cho nữ mệnh).
        timezone: IANA tz.
        as_of_year: năm tham chiếu để tính tuổi/chặng (None = năm hiện tại).

    Returns:
        dict với các khoá: method_id, input, stage, personality,
        cung_phu_the_tuvi, batu_hon_nhan, song_phai_reconcile, cach_cuc,
        dinh_thoi, base_12_khia_canh, paradigm_ok, sources, _disclaimer.
    """
    # (a) Lập lá số + bát tự.
    la_so = cast_la_so_from_birth(
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        gender=gender,
    )
    bat_tu_state = cast_bat_tu(
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        gender=gender,
    )

    # (b) FOUNDATION từ engine con.
    base = luan_hon_nhan_song_phai(bat_tu_state=bat_tu_state, la_so=la_so)

    # (c) Trích xuất chỉ số then chốt.
    phu_the_idx = la_so["palaces"][2]["branch_index"]
    menh_chinh_tinh = _stars_at(la_so["chinh_tinh"], la_so["menh_index"])
    nhat_chu = bat_tu_state["tu_tru"]["day_master"]["stem"]
    quan_sat_count = _count_quan_sat(bat_tu_state.get("thap_than_distribution", {}))

    # (d) STAGE theo tuổi.
    birth = _parse_birth(birth_datetime_local)
    age = _calc_age(birth, as_of_year)
    stage = _pick_stage(age)

    # (e) PERSONALITY.
    personality = _personality(
        menh_chinh_tinh, nhat_chu,
        bat_tu_state.get("thap_than_distribution", {}),
    )

    # (f) CUNG PHU THÊ TỬ VI.
    cung_phu_the = _cung_phu_the_tuvi(la_so, phu_the_idx)

    # (g) BÁT TỰ HÔN NHÂN.
    batu = _batu_hon_nhan(bat_tu_state, quan_sat_count)

    # (h) RECONCILE 8 chủ đề.
    reconcile = _reconcile(base)

    # (i) CÁCH CỤC.
    cach_cuc = _cach_cuc(la_so)

    # (j) ĐỊNH THỜI.
    dinh_thoi = _dinh_thoi(la_so, age, phu_the_idx)

    return {
        "method_id": METHOD_ID,
        "input": {
            "birth_datetime_local": birth_datetime_local,
            "gender": gender,
            "timezone": timezone,
            "as_of_year": as_of_year,
            "tuoi": age,
            "menh_branch": la_so.get("menh_branch"),
            "phu_the_branch": _BRANCHES[phu_the_idx],
        },
        "stage": stage,
        "personality": personality,
        "cung_phu_the_tuvi": cung_phu_the,
        "batu_hon_nhan": batu,
        "song_phai_reconcile": reconcile,
        "cach_cuc": cach_cuc,
        "dinh_thoi": dinh_thoi,
        "base_12_khia_canh": base.get("khia_canh", []),
        "paradigm_ok": bool(base.get("paradigm_ok", True)),
        "sources": _collect_sources(),
        "_disclaimer": _DISCLAIMER,
    }


__all__ = ["read_tinh_duyen", "METHOD_ID"]
