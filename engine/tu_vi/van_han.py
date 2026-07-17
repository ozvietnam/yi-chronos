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


def _the_dung_block(la_so: dict, active_branch_index: int, tang: str) -> dict:
    """Khối THỂ-DỤNG cho 1 tầng: cung nguyên cục tại vị trí vận Mệnh (Thể) + sao + nguồn.

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


def luu_nguyet_block(la_so: dict, year: int, month: int) -> dict:
    """Khối grounded 1 Lưu Nguyệt. Lưu nguyệt Mệnh khởi từ Đẩu Quân lưu niên (Q2 p88):
    Đẩu Quân lưu niên = cung tại chi năm → tháng Giêng; thuận 1 cung/tháng."""
    if not 1 <= month <= 12:
        raise ValueError("month 1..12")
    y_can, y_chi = _year_stem_branch(year)
    dau_quan_bi = BRANCHES_TVI.index(y_chi)                 # Đẩu Quân lưu niên tại chi năm
    lnm_bi = (dau_quan_bi + (month - 1)) % 12               # lưu nguyệt Mệnh, thuận
    m_can = _month_can(y_can, month)
    block = _the_dung_block(la_so, lnm_bi, "Lưu Nguyệt")
    return {
        "available": True,
        "tang": "luu_nguyet",
        "year": year, "month": month,
        "month_can": m_can,
        **block,
        "tu_hoa_van": _hoa_lit(m_can, la_so),   # Tứ Hóa tháng theo can tháng
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
        "year": year, "month": month, "tuan": tuan,
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
def _lunar_of(solar_year: int, solar_month: int, solar_day: int) -> tuple[int, int, str]:
    """(lunar_month, lunar_day, day_can) của 1 ngày dương — qua sxtwl."""
    import sxtwl
    from engine.yi_wiki.lich_conversion import TG_NAMES
    d = sxtwl.fromSolar(solar_year, solar_month, solar_day)
    return d.getLunarMonth(), d.getLunarDay(), TG_NAMES[d.getDayGZ().tg]


def luu_nhat_block(la_so: dict, solar_year: int, solar_month: int, solar_day: int) -> dict:
    """Khối grounded 1 Lưu Nhật (ngày). Lưu nhật Mệnh = lưu nguyệt Mệnh + (ngày âm -1),
    thuận. Tứ Hóa ngày theo can ngày. ⚠️ Kho nội dung ngày cực mỏng → DẪN XUẤT."""
    lmonth, lday, day_can = _lunar_of(solar_year, solar_month, solar_day)
    # lưu nguyệt Mệnh của tháng âm chứa ngày này (Đẩu Quân lưu niên + thuận tháng)
    y_can, y_chi = _year_stem_branch(solar_year)
    dau_quan_bi = BRANCHES_TVI.index(y_chi)
    lnm_bi = (dau_quan_bi + (lmonth - 1)) % 12
    lnhat_bi = (lnm_bi + (lday - 1)) % 12
    block = _the_dung_block(la_so, lnhat_bi, "Lưu Nhật")
    return {
        "available": True,
        "tang": "luu_nhat",
        "solar": f"{solar_year:04d}-{solar_month:02d}-{solar_day:02d}",
        "lunar_month": lmonth, "lunar_day": lday, "day_can": day_can,
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
    lines.append(f"### THỂ-DỤNG: {blk['dien_giai_the_dung']}")
    lines.append(f"### Nguyên tắc (nguồn {blk['nguyen_tac']['nguon']}): {blk['nguyen_tac']['text']}")
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
    q = (
        f"Bạn là người BIÊN TẬP luận vận hạn Tử Vi, KHÔNG phải người sáng tác nghĩa. Dưới đây "
        f"là dữ kiện CÓ NGUỒN về tầng {tang_vi} của người này:\n\n{source_text}\n\n"
        f"NHIỆM VỤ: dệt các ý CÓ NGUỒN thành đoạn luận {tang_vi} mạch lạc, đời thường, theo "
        f"paradigm ĐỌC ĐỒNG DẠNG (mệnh là ĐỘNG TỪ — cách VẬN HÀNH cái tính qua thời gian, "
        f"KHÔNG án định số phận).\n"
        f"LUẬT BẮT BUỘC (vi phạm = hỏng):\n"
        f"1. CHỈ dùng ý trong nguồn cho sẵn — TUYỆT ĐỐI không thêm nghĩa từ kiến thức ngoài.\n"
        f"2. Đọc theo THỂ-DỤNG: cái tính gốc (Thể) VẬN HÀNH thế nào trong tầng này (Dụng).\n"
        f"3. Tứ Hóa rọi cung = MỜI QUAN-SÁT lĩnh vực đó, KHÔNG phán cát/hung, KHÔNG tiên tri việc cụ thể.\n"
        f"4. Sao 'CHƯA CÓ NGUỒN' → không luận. Tầng tuần → nói rõ là quan-sát vi mô.\n"
        f"~200–350 chữ, văn xuôi tiếng Việt, có thể nhắc tên sách nguồn cho tự nhiên."
    )
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    resp = run_agent(agent_id="tu_vi", provider=provider, model=model, question=q,
                     chart_data={"birth_datetime_local": person["birth_datetime_local"],
                                 "gender": person.get("gender") or "nam", "timezone": tz},
                     round_label="van_han", challenges=None, max_tokens=1200)
    import re
    return re.sub(r"^\s*#{1,4}\s*(READ|REACT|REVISE|ĐỌC)\s*\n+", "", resp.content or "",
                  flags=re.IGNORECASE)
