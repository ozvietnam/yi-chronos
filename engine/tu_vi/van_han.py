"""Vận hạn GROUNDED — đọc Đại Vận / Lưu Niên (năm) / Lưu Nguyệt (tháng) / Tuần theo
phương pháp cổ THỂ-DỤNG + Tứ Hóa rọi cung, LUẬN chỉ từ NGUỒN đã duyệt (Anh giao
2026-07-14: "vận hạn theo tuần/tháng, làm kỹ, dùng sách/thư viện/công thức").

═══ PHƯƠNG PHÁP (grounded, Trung Châu — Vương Đình Chi, đã phục chế) ═══
  • Mỗi tầng thời gian có 12 cung RIÊNG dịch chuyển; đọc theo THỂ-DỤNG:
    "lấy Cung X của nguyên cục làm tính chất (THỂ), cung X của đại vận/lưu niên/lưu
     nguyệt làm phản ứng của tính chất (DỤNG)" — Trung Châu Tử Vi Đẩu Số.
  • Tứ Hóa của TẦNG (Lộc/Quyền/Khoa/Kỵ theo can của tầng) rọi vào cung chức nào →
    đó là "sân khấu" tầng đó MỜI QUAN-SÁT (Iron #4/#6/#8: đọc đồng dạng, KHÔNG predict).
  • Fine-grained: Đại Vận(10n) → Lưu Niên(năm) → Lưu Nguyệt(tháng, Đẩu Quân) → Tuần
    (thượng/trung/hạ = 3×10 ngày trong tháng) → Lưu Nhật(ngày).

Iron #9 quote-or-silence: nội dung SAO chỉ lấy từ sao_noi_dung founder_verified=1 (kho
đã duyệt đối kháng). Cung/sao KHÔNG có nguồn → để trống (chua_co_nguon), KHÔNG bịa.
Engine 0-LLM (xương tất định); LLM chỉ BIÊN TẬP block này ở tầng analyzer.
"""
from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional

from engine.tu_vi.an_sao import BRANCHES_TVI, TU_HOA_TABLE

_WIKI_DB = "data/yi_wiki/wiki.sqlite3"

# Nguyên tắc THỂ-DỤNG có nguồn (không bịa) — nền mọi tầng vận hạn.
THE_DUNG_PRINCIPLE = {
    "text": ("Cung nguyên cục là TÍNH CHẤT gốc (Thể); cung cùng tên của đại vận / lưu "
             "niên / lưu nguyệt là PHẢN ỨNG của tính chất đó trong tầng thời gian ấy "
             "(Dụng). Vận hạn = cách cái Thể bẩm sinh VẬN HÀNH qua thời gian, không "
             "phải bản án cát-hung định sẵn."),
    "nguon": "Trung Châu Tử Vi Đẩu Số (Vương Đình Chi)",
}

_HOA_NGHIA = {
    "Lộc": "được nuôi dưỡng, thuận lợi, có lộc",
    "Quyền": "được trao quyền, chủ động, có lực đẩy",
    "Khoa": "được soi sáng, danh tiếng, quý nhân",
    "Kỵ": "vướng mắc, cần cẩn trọng, chỗ hao tâm",
}

# Nguyên tắc ĐỌC CUNG khi nó là cung VẬN (Thể-Dụng per-cung) — TRÍCH có nguồn từ sách
# phục chế Trung Châu phái (#3 dày kho fine-grained, 2026-07-14). Cung CHƯA có trích rõ
# → KHÔNG bịa (quote-or-silence): engine để trống, tầng LLM không luận thêm.
_CUNG_VAN_NGHIA = {
    "Thiên Di": {
        "rule": "Cung Thiên Di của vận tốt → nên tìm cơ hội xuất ngoại / đổi chỗ ở / đổi "
                "việc để phát triển; kỳ này quan-sát việc đi lại, dời chuyển hoàn cảnh.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Tật Ách": {
        "rule": "Cung Tật Ách của lưu niên/đại vận gặp Thiên Hình + Lưu Dương xung → đề "
                "phòng phẫu thuật; ưa gặp Thiên Thọ → dù bệnh nặng cũng dễ gặp thầy giỏi, chữa khỏi.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Tài Bạch": {
        "rule": "Gặp sát-kỵ ở cung Tài Bạch của vận, CHỚ vội võ đoán tài vận xấu — phải xét "
                "kỹ tổ hợp; ứng nghiệm có khi là thu nhập tăng nhưng tiền lời đến chậm.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Điền Trạch": {
        "rule": "Hồng Loan / Thiên Hỉ đến cung Điền Trạch lưu niên → thêm nhân khẩu (sinh "
                "con, người đến ở); gặp thêm Tả Phụ, Hữu Bật → có khách đến tá túc.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Tử Tức": {
        "rule": "Lưu niên gặp Lưu Xương - Lưu Khúc hội chiếu + cung Tử Tức lưu niên cát lợi "
                "→ thuận việc sinh nở (mẹ tròn con vuông).",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Nô Bộc": {
        "rule": "Cung Giao Hữu (Nô Bộc) của vận cát → người dưới quyền đồng cam cộng khổ, "
                "chung mục tiêu; gặp sát-kỵ → tranh chấp, bất hòa trong công việc.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
    "Phụ Mẫu": {
        "rule": "Bạch Hổ ở cung Phụ Mẫu của lưu niên → chủ hung tang (tang chế); kỳ này "
                "quan-sát sức khỏe / quan hệ với bậc trên.",
        "nguon": "Trung Châu phái (Vương Đình Chi)"},
}


@lru_cache(maxsize=1)
def _db() -> "sqlite3.Connection | None":
    p = Path(_WIKI_DB)
    if not p.exists():
        return None
    try:
        return sqlite3.connect(f"file:{p}?mode=ro", uri=True, check_same_thread=False)
    except Exception:
        return None


def _grounded_sao(sao: str, cung: Optional[str] = None, limit: int = 2) -> list[dict]:
    """Nội dung sao ĐÃ DUYỆT (founder_verified=1). Ưu tiên lớp 'cung' nếu có tên cung,
    fallback 'def'. [] nếu không có nguồn (quote-or-silence)."""
    conn = _db()
    if conn is None:
        return []
    out: list[dict] = []
    try:
        if cung:
            rows = conn.execute(
                "SELECT dich_thuan_viet, nguon_book FROM sao_noi_dung "
                "WHERE sao_vi=? AND lop='cung' AND cung=? AND founder_verified=1 "
                "AND dich_thuan_viet!='' LIMIT ?", (sao, cung, limit)).fetchall()
            out += [{"sao": sao, "dich": r[0], "nguon": r[1], "lop": "cung"} for r in rows]
        if len(out) < limit:
            rows = conn.execute(
                "SELECT dich_thuan_viet, nguon_book FROM sao_noi_dung "
                "WHERE sao_vi=? AND lop='def' AND founder_verified=1 "
                "AND dich_thuan_viet!='' LIMIT ?", (sao, limit - len(out))).fetchall()
            out += [{"sao": sao, "dich": r[0], "nguon": r[1], "lop": "def"} for r in rows]
    except Exception:
        return []
    return out


def _cung_van_rules(cung: str, tang_key: str, limit: int = 3) -> list[dict]:
    """Nguyên tắc đọc cung <cung> khi là cung VẬN — từ bảng van_han_nguon (đã atomize +
    duyệt, founder_verified=1), khớp tầng (tang_key hoặc 'all'). Fallback seed hardcoded
    nếu bảng chưa có / rỗng. Trả [{rule, nguon, quote_goc, tang}] (quote-or-silence)."""
    conn = _db()
    rules: list[dict] = []
    if conn is not None:
        try:
            rows = conn.execute(
                "SELECT rule, nguon_book, quote_goc, tang FROM van_han_nguon "
                "WHERE cung=? AND founder_verified=1 AND (tang=? OR tang='all') "
                "ORDER BY (tang='all') ASC, id ASC LIMIT ?", (cung, tang_key, limit)).fetchall()
            rules = [{"rule": r[0], "nguon": r[1], "quote_goc": r[2] or "", "tang": r[3]} for r in rows]
        except Exception:
            rules = []
    if not rules and cung in _CUNG_VAN_NGHIA:      # seed hardcoded (khi bảng chưa atomize)
        h = _CUNG_VAN_NGHIA[cung]
        rules = [{"rule": h["rule"], "nguon": h["nguon"], "quote_goc": "", "tang": "all"}]
    return rules


_TANG_KEY = {"Đại Vận": "dai_van", "Lưu Niên": "luu_nien", "Lưu Nguyệt": "luu_nguyet",
             "Tuần": "luu_nguyet", "Lưu Nhật": "luu_nguyet"}


def _palace_at(la_so: dict, branch_index: int) -> "dict | None":
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == branch_index:
            return p
    return None


def _stars_at(la_so: dict, branch_index: int) -> list[str]:
    """Chính tinh (+ Vô Chính Diệu nếu rỗng) đóng tại 1 branch."""
    br = BRANCHES_TVI[branch_index]
    stars = [s for s, idx in la_so.get("chinh_tinh", {}).items() if idx == branch_index]
    return stars


def _hoa_lit(hoa_stem: str, la_so: dict) -> list[dict]:
    """Tứ Hóa của 1 tầng (theo can) rọi vào cung chức nào của nguyên cục.

    star (được hóa) → branch nó đậu ở natal → cung chức đó. Trả [{hoa, sao, cung, nghia}].
    """
    star_to_branch = {s: idx for s, idx in la_so.get("chinh_tinh", {}).items()}
    star_to_branch.update({s: idx for s, idx in la_so.get("phu_tinh", {}).items()})
    branch_to_palace = {p["branch_index"]: p["name"] for p in la_so.get("palaces", [])}
    out: list[dict] = []
    for hoa, star in TU_HOA_TABLE.get(hoa_stem, {}).items():
        bi = star_to_branch.get(star)
        palace = branch_to_palace.get(bi) if bi is not None else None
        out.append({
            "hoa": hoa, "sao": star,
            "cung": palace or "(phụ tinh — ngoài 14 chính tinh)",
            "nghia": _HOA_NGHIA[hoa],
        })
    return out


def _tam_phuong(la_so: dict, i: int) -> list[dict]:
    """Tam phương tứ chính HỘI CHIẾU vào cung i: đối cung (xung, +6) + 2 cung tam hợp
    (±4). Trả [{quan_he, cung, vi_tri, sao, sao_nguon}]. Cổ pháp: cung vận không đọc lẻ.
    Sao hội chiếu KÈM 1 trích nội dung có nguồn (để luận cả chòm, không chỉ tên sao)."""
    out = []
    for off, qh in ((6, "đối cung (xung chiếu)"), (4, "tam hợp"), (8, "tam hợp")):
        bi = (i + off) % 12
        p = _palace_at(la_so, bi)
        pname = p["name"] if p else "?"
        stars = _stars_at(la_so, bi)
        nguon = []
        for st in stars[:2]:
            g = _grounded_sao(st, cung=pname, limit=1)
            if g:
                nguon.append(g[0])
        out.append({
            "quan_he": qh, "cung": pname, "vi_tri": BRANCHES_TVI[bi],
            "sao": stars, "sao_nguon": nguon,
        })
    return out


def _dai_van_of_age(la_so: dict, age: int) -> "dict | None":
    for dv in la_so.get("dai_van", []):
        if dv["start_age"] <= age <= dv["end_age"]:
            return dv
    return None


def _bao_tram_dai_van(la_so: dict, birth_year: int, year: int) -> "dict | None":
    """Đại Vận (10 năm) BAO TRÙM năm này — để đọc năm/tháng TRONG bối cảnh đại vận
    (cổ pháp: 'lấy đại hạn làm chủ, lưu niên nói rõ thêm một bước'). age = tuổi âm."""
    dv = _dai_van_of_age(la_so, year - birth_year + 1)
    if dv is None:
        return None
    bi = dv["branch_index"]
    p = _palace_at(la_so, bi)
    pname = p["name"] if p else "?"
    stars = _stars_at(la_so, bi) or _stars_at(la_so, (bi + 6) % 12)
    return {
        "cycle_index": dv["cycle_index"], "khoang_tuoi": [dv["start_age"], dv["end_age"]],
        "cung": pname, "vi_tri": BRANCHES_TVI[bi], "sao": stars,
        "sao_nguon": [g for st in stars[:2] for g in _grounded_sao(st, cung=pname, limit=1)],
    }


def _the_dung_block(la_so: dict, active_branch_index: int, tang: str) -> dict:
    """Khối THỂ-DỤNG cho 1 tầng: cung nguyên cục tại vị trí vận Mệnh (Thể) + sao + nguồn
    + TAM PHƯƠNG TỨ CHÍNH hội chiếu (cổ pháp: không đọc cung lẻ).

    Vô Chính Diệu (cung không chính tinh) → MƯỢN SAO cung xung chiếu (đối diện +6), cổ pháp.
    """
    natal_palace = _palace_at(la_so, active_branch_index)
    palace_name = natal_palace["name"] if natal_palace else "?"
    stars = _stars_at(la_so, active_branch_index)
    borrowed = False
    if not stars:                                    # Vô Chính Diệu → mượn sao cung xung
        stars = _stars_at(la_so, (active_branch_index + 6) % 12)
        borrowed = bool(stars)
    sao_grounded: list[dict] = []
    for st in stars:
        sao_grounded.extend(_grounded_sao(st, cung=palace_name))
    dg = (f"{tang} an Mệnh tại {BRANCHES_TVI[active_branch_index]} — trùng cung "
          f"{palace_name} của nguyên cục. Tầng này VẬN HÀNH chất '{palace_name}' "
          f"(Thể) theo cách của {tang} (Dụng).")
    if borrowed:
        dg += " Cung Vô Chính Diệu — mượn sao cung xung chiếu (đối diện) để luận."
    return {
        "vi_tri": BRANCHES_TVI[active_branch_index],
        "cung_the": palace_name,          # cung nguyên cục = THỂ
        "sao": stars,                     # sao đóng tại vị trí vận Mệnh (hoặc mượn xung)
        "sao_muon_xung": borrowed,        # True = Vô Chính Diệu, sao mượn
        "sao_nguon": sao_grounded,        # nội dung sao đã duyệt (có thể rỗng)
        "chua_co_nguon": len(sao_grounded) == 0,
        "dien_giai_the_dung": dg,
        # TAM PHƯƠNG TỨ CHÍNH (cổ pháp "còn phải xem lục xung tam hợp chiếu"): đối cung
        # (xung) + 2 cung tam hợp HỘI CHIẾU vào cung vận — không đọc cung lẻ.
        "hoi_chieu": _tam_phuong(la_so, active_branch_index),
        # #3: nguyên tắc đọc cung này khi là cung VẬN — LIST có nguồn (rỗng nếu chưa trích).
        "cung_van_rules": _cung_van_rules(palace_name, _TANG_KEY.get(tang, "all")),
    }


# ── ĐẠI VẬN ───────────────────────────────────────────────────────────────────
def dai_van_block(la_so: dict, cycle_index: int) -> dict:
    """Khối grounded 1 Đại Vận (10 năm). cycle_index: 1..12."""
    dv = next((d for d in la_so.get("dai_van", []) if d["cycle_index"] == cycle_index), None)
    if dv is None:
        return {"available": False}
    bi = dv["branch_index"]
    natal_palace = _palace_at(la_so, bi)
    dv_can = natal_palace.get("can") if natal_palace else None   # can cung → Tứ Hóa đại vận
    block = _the_dung_block(la_so, bi, "Đại Vận")
    return {
        "available": True,
        "tang": "dai_van",
        "cycle_index": cycle_index,
        "khoang_tuoi": [dv["start_age"], dv["end_age"]],
        **block,
        "tu_hoa_van": _hoa_lit(dv_can, la_so) if dv_can else [],
        "tu_hoa_can": dv_can,
        "nguyen_tac": THE_DUNG_PRINCIPLE,
    }


# ── LƯU NIÊN (năm) ────────────────────────────────────────────────────────────
def _year_stem_branch(year: int) -> tuple[str, str]:
    """(can, chi) năm dương theo chu kỳ 60 (mốc 1984 = Giáp Tý)."""
    can = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")
    chi = BRANCHES_TVI
    return can[(year - 1984) % 10], chi[(year - 1984) % 12]


def luu_nien_block(la_so: dict, year: int) -> dict:
    """Khối grounded 1 Lưu Niên. Lưu niên Mệnh = cung tại chi năm (Thái Tuế)."""
    y_can, y_chi = _year_stem_branch(year)
    bi = BRANCHES_TVI.index(y_chi)
    block = _the_dung_block(la_so, bi, "Lưu Niên")
    return {
        "available": True,
        "tang": "luu_nien",
        "year": year,
        "year_can_chi": f"{y_can} {y_chi}",
        **block,
        "tu_hoa_van": _hoa_lit(y_can, la_so),   # Tứ Hóa lưu niên theo can năm
        "tu_hoa_can": y_can,
        "nguyen_tac": THE_DUNG_PRINCIPLE,
    }


# ── LƯU NGUYỆT (tháng) ────────────────────────────────────────────────────────
_NGU_HO_DON = {"Giáp": "Bính", "Kỷ": "Bính", "Ất": "Mậu", "Canh": "Mậu",
               "Bính": "Canh", "Tân": "Canh", "Đinh": "Nhâm", "Nhâm": "Nhâm",
               "Mậu": "Giáp", "Quý": "Giáp"}
_CAN = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")


def _month_can(year_can: str, month: int) -> str:
    """Can tháng âm (1..12) theo Ngũ Hổ Độn (Giêng=Dần, thuận +1 can)."""
    gieng = _NGU_HO_DON[year_can]
    return _CAN[(_CAN.index(gieng) + (month - 1)) % 10]


def _solar_month_to_lunar(solar_year: int, solar_month: int, anchor_day: int = 15) -> tuple:
    """Đổi (năm, tháng DƯƠNG) → âm lịch qua sxtwl (mốc ngày 15 dương của tháng đó).
    Trả (lunar_year, lunar_month, is_leap, năm_can, năm_chi). Năm can-chi theo NĂM ÂM
    (đổi ở Tết — đúng cổ pháp Tử Vi), nên tháng 1 dương thuộc năm âm trước là chính xác."""
    import sxtwl
    d = sxtwl.fromSolar(solar_year, solar_month, anchor_day)
    ly, lm = d.getLunarYear(), d.getLunarMonth()
    y_can, y_chi = _year_stem_branch(ly)
    return ly, lm, d.isLunarLeap(), y_can, y_chi


def luu_nguyet_block(la_so: dict, year: int, month: int) -> dict:
    """Khối grounded 1 Lưu Nguyệt. NHẬP DƯƠNG LỊCH (year, month) → tự đổi ÂM (sxtwl).
    Lưu nguyệt Mệnh khởi Đẩu Quân lưu niên (Q2 p88): cung tại chi năm ÂM → tháng Giêng,
    thuận 1 cung/tháng âm."""
    if not 1 <= month <= 12:
        raise ValueError("month 1..12")
    ly, lmonth, is_leap, y_can, y_chi = _solar_month_to_lunar(year, month)
    dau_quan_bi = BRANCHES_TVI.index(y_chi)                 # Đẩu Quân lưu niên tại chi năm ÂM
    lnm_bi = (dau_quan_bi + (lmonth - 1)) % 12              # lưu nguyệt Mệnh, thuận theo tháng ÂM
    m_can = _month_can(y_can, lmonth)
    block = _the_dung_block(la_so, lnm_bi, "Lưu Nguyệt")
    leap = _leap_month_of(ly)
    return {
        "available": True,
        "tang": "luu_nguyet",
        "year": year, "month": month,                       # DƯƠNG (user nhập)
        "am_lich": {"nam": ly, "nam_can_chi": f"{y_can} {y_chi}", "thang": lmonth, "nhuan": is_leap},
        "month_can": m_can,
        "thang_nhuan": leap,
        "thang_nhuan_note": (
            f"⚠️ Năm âm {y_can} {y_chi} có tháng nhuận (sau tháng {leap} âm) — tháng nhuận "
            f"nằm chung cung với tháng kề; quanh đó cổ pháp luận CẢ HAI trường hợp."
            if leap else ""),
        **block,
        "tu_hoa_van": _hoa_lit(m_can, la_so),   # Tứ Hóa tháng theo can tháng ÂM
        "tu_hoa_can": m_can,
        "nguyen_tac": THE_DUNG_PRINCIPLE,
    }


# ── TUẦN (thượng/trung/hạ — 3×10 ngày trong tháng) ────────────────────────────
_TUAN_LABEL = {1: "Thượng tuần (ngày 1-10)", 2: "Trung tuần (ngày 11-20)",
               3: "Hạ tuần (ngày 21-cuối)"}


def tuan_block(la_so: dict, year: int, month: int, tuan: int) -> dict:
    """Khối grounded 1 Tuần (旬 = 10 ngày). tuan: 1 thượng · 2 trung · 3 hạ.

    Cổ pháp (Trung Châu): trong lưu nguyệt, mỗi tuần dịch cung Mệnh thuận 1 bước từ lưu
    nguyệt Mệnh (thượng=lưu nguyệt Mệnh, trung +1, hạ +2) — đọc tiếp tục Thể-Dụng nhỏ hơn.
    ⚠️ Nội dung tuần MỎNG trong sách → chủ yếu DẪN XUẤT (cung động + Tứ Hóa + sao đã duyệt),
    nói rõ tầng này 'quan-sát vi mô', không phán ngày cụ thể.
    """
    if tuan not in (1, 2, 3):
        raise ValueError("tuan 1|2|3")
    lng = luu_nguyet_block(la_so, year, month)
    lnm_bi = BRANCHES_TVI.index(lng["vi_tri"])
    tuan_bi = (lnm_bi + (tuan - 1)) % 12
    block = _the_dung_block(la_so, tuan_bi, "Tuần")
    return {
        "available": True,
        "tang": "tuan",
        "year": year, "month": month, "tuan": tuan,     # DƯƠNG (user nhập)
        "am_lich": lng.get("am_lich"),
        "tuan_label": _TUAN_LABEL[tuan],
        **block,
        "tu_hoa_van": lng["tu_hoa_van"],        # tuần dùng Tứ Hóa của tháng chứa nó
        "tu_hoa_can": lng["month_can"],
        "luu_nguyet_me": lng["vi_tri"],
        "nguyen_tac": THE_DUNG_PRINCIPLE,
        "luu_y_vi_mo": ("Tầng tuần là quan-sát VI MÔ trong tháng — kho sách cổ về tuần "
                        "mỏng, nên đây là DẪN XUẤT (cung động + Tứ Hóa tháng + sao đã "
                        "duyệt), KHÔNG phán ngày/việc cụ thể."),
    }


# ── Overview (skeleton tất định — thay nguồn cached-analyzer ungrounded) ───────
def dai_van_overview(la_so: dict) -> dict:
    """12 Đại Vận skeleton tất định: cycle, tuổi, vị trí, cung Thể, sao. 0-LLM, 0 bịa."""
    cycles = []
    for dv in la_so.get("dai_van", []):
        bi = dv["branch_index"]
        pal = _palace_at(la_so, bi)
        stars = _stars_at(la_so, bi)
        borrowed = False
        if not stars:
            stars = _stars_at(la_so, (bi + 6) % 12)
            borrowed = bool(stars)
        cycles.append({
            "cycle_index": dv["cycle_index"],
            "start_age": dv["start_age"], "end_age": dv["end_age"],
            "branch": BRANCHES_TVI[bi],
            "cung_the": pal["name"] if pal else "?",
            "sao": stars, "sao_muon_xung": borrowed,
        })
    return {"cycles": cycles}


@lru_cache(maxsize=128)
def _leap_month_of(lunar_year: int) -> int:
    """Tháng nhuận (âm) của 1 NĂM ÂM, 0 nếu không nhuận. Quét ngày dương của năm âm đó
    (lọc getLunarYear==lunar_year), bắt isLunarLeap(). API sxtwl.fromLunar không validate
    cờ nhuận nên phải quét."""
    try:
        import datetime
        import sxtwl
        dt = datetime.date(lunar_year, 1, 15)     # giữa tháng 1 dương ~ vẫn lunar năm trước/này
        for _ in range(400):                       # phủ trọn 1 năm âm (~354-384 ngày)
            d = sxtwl.fromSolar(dt.year, dt.month, dt.day)
            if d.getLunarYear() == lunar_year and d.isLunarLeap():
                return d.getLunarMonth()
            dt += datetime.timedelta(days=1)
    except Exception:
        pass
    return 0


def luu_nguyet_overview(la_so: dict, year: int) -> dict:
    """12 tháng DƯƠNG (T1..T12 của năm dương) → mỗi tháng đổi ÂM (sxtwl) → vị trí + cung
    Thể. Nhất quán với luu_nguyet_block (nhập dương). Kèm cờ tháng nhuận nếu năm âm có."""
    months = []
    for m in range(1, 13):
        ly, lmonth, is_leap, y_can, y_chi = _solar_month_to_lunar(year, m)
        dau_quan_bi = BRANCHES_TVI.index(y_chi)
        bi = (dau_quan_bi + (lmonth - 1)) % 12
        p = _palace_at(la_so, bi)
        stars = _stars_at(la_so, bi)
        borrowed = False
        if not stars:
            stars = _stars_at(la_so, (bi + 6) % 12)
            borrowed = bool(stars)
        months.append({
            "month": m, "am_thang": lmonth, "am_nam_can_chi": f"{y_can} {y_chi}",
            "branch": BRANCHES_TVI[bi], "cung_the": p["name"] if p else "?",
            "sao": stars, "sao_muon_xung": borrowed,
        })
    # cờ nhuận theo năm âm giữa năm dương (tháng 6 dương)
    ly_mid = _solar_month_to_lunar(year, 6)[0]
    leap = _leap_month_of(ly_mid)
    return {
        "year": year, "months": months,
        "thang_nhuan": leap,
        "thang_nhuan_note": (
            f"Năm âm quanh {year} có THÁNG NHUẬN (sau tháng {leap} âm) — cổ pháp luận cả 2 "
            f"trường hợp quanh tháng nhuận." if leap else ""),
    }


def luu_nien_overview(la_so: dict, start_year: int, end_year: int) -> dict:
    """Skeleton Lưu Niên nhiều năm (tất định): mỗi năm can-chi, vị trí, cung Thể, sao."""
    if end_year < start_year or end_year - start_year > 30:
        raise ValueError("khoảng năm không hợp lệ (≤30 năm)")
    years = []
    for y in range(start_year, end_year + 1):
        y_can, y_chi = _year_stem_branch(y)
        bi = BRANCHES_TVI.index(y_chi)
        pal = _palace_at(la_so, bi)
        stars = _stars_at(la_so, bi)
        borrowed = False
        if not stars:
            stars = _stars_at(la_so, (bi + 6) % 12)
            borrowed = bool(stars)
        years.append({
            "year": y, "year_can_chi": f"{y_can} {y_chi}", "branch": y_chi,
            "cung_the": pal["name"] if pal else "?",
            "sao": stars, "sao_muon_xung": borrowed,
        })
    return {"years": years}


# ── LƯU NHẬT (ngày) — cổ pháp có nguồn ────────────────────────────────────────
# "định lưu nhật: Lấy cung lưu nguyệt khởi mùng một, thuận đi 12 cung, một ngày một
#  cung" (Trung Châu phái, sách phục chế). Tứ Hóa ngày = theo CAN NGÀY (lịch 60).
def _lunar_of(solar_year: int, solar_month: int, solar_day: int) -> tuple[int, int, str, int]:
    """(lunar_month, lunar_day, day_can, lunar_year) của 1 ngày dương — qua sxtwl."""
    import sxtwl
    from engine.yi_wiki.lich_conversion import TG_NAMES
    d = sxtwl.fromSolar(solar_year, solar_month, solar_day)
    return d.getLunarMonth(), d.getLunarDay(), TG_NAMES[d.getDayGZ().tg], d.getLunarYear()


def luu_nhat_block(la_so: dict, solar_year: int, solar_month: int, solar_day: int) -> dict:
    """Khối grounded 1 Lưu Nhật (ngày). Lưu nhật Mệnh = lưu nguyệt Mệnh + (ngày âm -1),
    thuận. Tứ Hóa ngày theo can ngày. ⚠️ Kho nội dung ngày cực mỏng → DẪN XUẤT."""
    lmonth, lday, day_can, lyear = _lunar_of(solar_year, solar_month, solar_day)
    # lưu nguyệt Mệnh của tháng âm chứa ngày này (Đẩu Quân lưu niên theo NĂM ÂM + thuận tháng)
    y_can, y_chi = _year_stem_branch(lyear)
    dau_quan_bi = BRANCHES_TVI.index(y_chi)
    lnm_bi = (dau_quan_bi + (lmonth - 1)) % 12
    lnhat_bi = (lnm_bi + (lday - 1)) % 12
    block = _the_dung_block(la_so, lnhat_bi, "Lưu Nhật")
    return {
        "available": True,
        "tang": "luu_nhat",
        "solar": f"{solar_year:04d}-{solar_month:02d}-{solar_day:02d}",
        "lunar_month": lmonth, "lunar_day": lday, "day_can": day_can,
        "lunar_year_can_chi": f"{y_can} {y_chi}",
        **block,
        "tu_hoa_van": _hoa_lit(day_can, la_so),
        "tu_hoa_can": day_can,
        "nguyen_tac": THE_DUNG_PRINCIPLE,
        "luu_y_vi_mo": ("Tầng ngày là quan-sát CỰC VI MÔ — kho sách cổ về lưu nhật rất "
                        "mỏng, đây là DẪN XUẤT (cung động theo cổ pháp 'lưu nguyệt khởi "
                        "mùng một, thuận 1 cung/ngày' + Tứ Hóa ngày + sao đã duyệt). "
                        "KHÔNG phán việc cụ thể trong ngày."),
    }


# ── Dựng block cho 1 tầng bất kỳ (dispatch) ───────────────────────────────────
def build_block(la_so: dict, tang: str, **kw) -> dict:
    """Dispatch: tang ∈ {dai_van, luu_nien, luu_nguyet, tuan, luu_nhat}."""
    if tang == "dai_van":
        return dai_van_block(la_so, int(kw["cycle_index"]))
    if tang == "luu_nien":
        return luu_nien_block(la_so, int(kw["year"]))
    if tang == "luu_nguyet":
        return luu_nguyet_block(la_so, int(kw["year"]), int(kw["month"]))
    if tang == "tuan":
        return tuan_block(la_so, int(kw["year"]), int(kw["month"]), int(kw["tuan"]))
    if tang == "luu_nhat":
        return luu_nhat_block(la_so, int(kw["year"]), int(kw["month"]), int(kw["day"]))
    raise ValueError(f"tang không hợp lệ: {tang}")


def block_to_source_text(blk: dict) -> str:
    """Ép khối grounded thành TEXT NGUỒN cho LLM biên tập (giống deep_cung).

    LLM CHỈ được dệt từ text này; không thêm nghĩa ngoài. Trả "" nếu không đủ nguồn.
    """
    if not blk.get("available"):
        return ""
    lines: list[str] = []
    tang_vi = {"dai_van": "Đại Vận", "luu_nien": "Lưu Niên (năm)",
               "luu_nguyet": "Lưu Nguyệt (tháng)", "tuan": "Tuần (10 ngày)", "luu_nhat": "Lưu Nhật (ngày)"}.get(blk["tang"], blk["tang"])
    lines.append(f"### TẦNG: {tang_vi} — an Mệnh tại cung {blk['vi_tri']}")
    bt = blk.get("bao_tram_dai_van")
    if bt:
        bt_sao = ", ".join(bt["sao"]) or "Vô Chính Diệu"
        lines.append(f"### BỐI CẢNH — Đại Vận bao trùm (LẤY LÀM CHỦ): vận V{bt['cycle_index']} "
                     f"tuổi {bt['khoang_tuoi'][0]}-{bt['khoang_tuoi'][1]}, cung {bt['cung']} ({bt_sao}). "
                     f"Đọc tầng này như MỘT BƯỚC cụ thể trong đại vận đó.")
        for s in bt.get("sao_nguon", []):
            lines.append(f"  · {s['sao']} (đại vận): {s['dich']} (nguồn: {s['nguon']})")
    lines.append(f"### THỂ-DỤNG: {blk['dien_giai_the_dung']}")
    lines.append(f"### Nguyên tắc (nguồn {blk['nguyen_tac']['nguon']}): {blk['nguyen_tac']['text']}")
    hc = blk.get("hoi_chieu") or []
    if hc:
        lines.append("### Tam phương tứ chính HỘI CHIẾU (cổ pháp — xét cả chòm, không đọc cung lẻ):")
        for h in hc:
            sao = ", ".join(h["sao"]) or "Vô Chính Diệu"
            lines.append(f"- {h['quan_he']}: cung {h['cung']} ({h['vi_tri']}) — {sao}")
            for s in h.get("sao_nguon", []):
                lines.append(f"  · {s['sao']}: {s['dich']} (nguồn: {s['nguon']})")
    cvr = blk.get("cung_van_rules") or []
    if cvr:
        lines.append(f"### Đọc cung {blk['cung_the']} khi là cung vận (nguyên tắc CÓ NGUỒN):")
        for r in cvr:
            lines.append(f"- {r['rule']} (nguồn: {r['nguon']})")
    if blk.get("sao_nguon"):
        lines.append("### Sao tại cung vận Mệnh — nội dung CÓ NGUỒN (chỉ dùng ý này):")
        for s in blk["sao_nguon"]:
            lines.append(f"- {s['sao']}: {s['dich']} (nguồn: {s['nguon']})")
    else:
        lines.append("### Sao tại cung vận Mệnh: CHƯA CÓ NGUỒN trong kho — KHÔNG luận, không bịa.")
    lit = [h for h in blk.get("tu_hoa_van", []) if not h["cung"].startswith("(")]
    if lit:
        lines.append("### Tứ Hóa của tầng rọi vào cung (sân khấu MỜI QUAN-SÁT, không phán cát/hung):")
        for h in lit:
            lines.append(f"- {h['hoa']} ({h['sao']}) → cung {h['cung']}: {h['nghia']}")
    if blk.get("luu_y_vi_mo"):
        lines.append(f"### Lưu ý: {blk['luu_y_vi_mo']}")
    return "\n".join(lines)


def van_han_luan(person: dict, tang: str, *, want_llm: bool = True, **kw) -> dict:
    """Luận 1 tầng vận hạn GROUNDED. Trả {block, source_text, luan?}.

    block = khối tất định (luôn có). luan = narrative LLM biên-tập-từ-nguồn (nếu want_llm
    + đủ nguồn + provider sẵn). Thiếu nguồn → luan="" + reason, KHÔNG bịa.
    """
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    birth = person["birth_datetime_local"]
    gender = person.get("gender") or "nam"
    la_so = cast_la_so_from_birth(birth_datetime_local=birth, gender=gender)
    blk = build_block(la_so, tang, **kw)
    if not blk.get("available"):
        return {"available": False}
    # LỒNG TẦNG: năm/tháng/tuần/ngày đọc TRONG đại vận bao trùm (cổ pháp lấy đại hạn làm chủ).
    if tang in ("luu_nien", "luu_nguyet", "tuan", "luu_nhat"):
        try:
            byear = int(str(birth)[:4])
            yr = int(str(blk.get("solar", ""))[:4]) if tang == "luu_nhat" else int(kw.get("year"))
            blk["bao_tram_dai_van"] = _bao_tram_dai_van(la_so, byear, yr)
        except Exception:
            blk["bao_tram_dai_van"] = None
    src = block_to_source_text(blk)
    out = {"available": True, "block": blk, "source_text": src, "luan": "", "grounded": not blk["chua_co_nguon"]}
    if not want_llm or blk["chua_co_nguon"]:
        return out
    try:
        out["luan"] = _luan_llm(person, tang, src)
    except Exception as e:  # LLM lỗi → vẫn trả block tất định, KHÔNG chặn
        out["luan_error"] = str(e)[:120]
    return out


def _luan_llm(person: dict, tang: str, source_text: str) -> str:
    """LLM biên tập vận hạn CHỈ từ source_text (edit-only, cấm sinh nghĩa ngoài)."""
    from engine.ai.agents import run_agent
    from engine.ai.council import _get_agent_provider
    provider, model = _get_agent_provider("tu_vi")
    try:
        from engine.ai.council import sage_model
        model = sage_model(provider, model)
    except Exception:
        from engine.ai.council import _SAGE_FAST_MODEL
        model = _SAGE_FAST_MODEL.get(provider.name, model)
    tang_vi = {"dai_van": "Đại Vận (10 năm)", "luu_nien": "Lưu Niên (năm)",
               "luu_nguyet": "Lưu Nguyệt (tháng)", "tuan": "Tuần (10 ngày)", "luu_nhat": "Lưu Nhật (ngày)"}.get(tang, tang)
    # Hướng dẫn CHUYÊN BIỆT theo tầng (chất luận tốt nhất cho năm/tháng).
    _GUIDE = {
        "luu_nien": (
            "Đây là VẬN NĂM. Đọc năm này như MỘT BƯỚC trong Đại Vận bao trùm (lấy đại vận "
            "làm CHỦ, năm nói rõ thêm một bước — theo bối cảnh cho sẵn). Cấu trúc: (1) chủ đề "
            "năm 1 câu; (2) cái Thể nào của nguyên cục được năm này kích hoạt + đọc cả tam "
            "phương tứ chính hội chiếu; (3) Tứ Hóa năm mời quan-sát lĩnh vực nào; (4) 1-2 câu "
            "gợi ý nên NUÔI DƯỠNG/QUAN-SÁT gì. Tổng hợp, có chiều sâu."),
        "luu_nguyet": (
            "Đây là VẬN THÁNG — CỤ THỂ hơn năm. Đặt tháng trong bối cảnh Đại Vận + năm (cho "
            "sẵn). Cấu trúc: (1) tháng này sân khấu chính là cung nào (Tứ Hóa tháng rọi đâu); "
            "(2) đọc cung đó + tam phương tứ chính hội chiếu; (3) gợi ý quan-sát THỰC TẾ trong "
            "tháng (dựa nguyên tắc đọc-cung có nguồn nếu có). Gọn, thiết thực, KHÔNG phán việc."),
        "dai_van": "Đây là ĐẠI VẬN 10 năm — đọc chất nền cả giai đoạn, khái quát.",
        "tuan": "Đây là TUẦN (10 ngày) — quan-sát VI MÔ, nói rõ là dẫn xuất, không phán ngày.",
        "luu_nhat": "Đây là NGÀY — CỰC VI MÔ, dẫn xuất, tuyệt đối không phán việc trong ngày.",
    }
    guide = _GUIDE.get(tang, "")
    q = (
        f"Bạn là người BIÊN TẬP luận vận hạn Tử Vi, KHÔNG phải người sáng tác nghĩa. Dưới đây "
        f"là dữ kiện CÓ NGUỒN về tầng {tang_vi} của người này:\n\n{source_text}\n\n"
        f"ĐỊNH HƯỚNG TẦNG NÀY: {guide}\n\n"
        f"NHIỆM VỤ: dệt các ý CÓ NGUỒN thành đoạn luận {tang_vi} mạch lạc, đời thường, theo "
        f"paradigm ĐỌC ĐỒNG DẠNG (mệnh là ĐỘNG TỪ — cách VẬN HÀNH cái tính qua thời gian, "
        f"KHÔNG án định số phận).\n"
        f"LUẬT BẮT BUỘC (vi phạm = hỏng):\n"
        f"1. CHỈ dùng ý trong nguồn cho sẵn — TUYỆT ĐỐI không thêm nghĩa từ kiến thức ngoài.\n"
        f"2. Đọc theo THỂ-DỤNG + LỒNG TẦNG: tầng nhỏ là bước cụ thể trong tầng lớn bao trùm.\n"
        f"3. Đọc CẢ CHÒM tam phương tứ chính, KHÔNG chỉ cung lẻ.\n"
        f"4. Tứ Hóa rọi cung = MỜI QUAN-SÁT lĩnh vực đó, KHÔNG phán cát/hung, KHÔNG tiên tri.\n"
        f"5. Sao 'CHƯA CÓ NGUỒN' → không luận.\n"
        f"~220–380 chữ, văn xuôi tiếng Việt, có thể nhắc tên sách nguồn cho tự nhiên."
    )
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    resp = run_agent(agent_id="tu_vi", provider=provider, model=model, question=q,
                     chart_data={"birth_datetime_local": person["birth_datetime_local"],
                                 "gender": person.get("gender") or "nam", "timezone": tz},
                     round_label="van_han", challenges=None, max_tokens=1200)
    import re
    return re.sub(r"^\s*#{1,4}\s*(READ|REACT|REVISE|ĐỌC)\s*\n+", "", resp.content or "",
                  flags=re.IGNORECASE)
