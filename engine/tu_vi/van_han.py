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
        "can": p.get("can") if p else None,          # can cung đại vận → Tứ Hóa đại vận
        "sao_nguon": [g for st in stars[:2] for g in _grounded_sao(st, cung=pname, limit=1)],
    }


def _star_branch_map(la_so: dict) -> dict:
    """{tên sao (chính+phụ) → branch_index nó đậu}."""
    m = {s: i for s, i in la_so.get("chinh_tinh", {}).items()}
    m.update({s: i for s, i in la_so.get("phu_tinh", {}).items()})
    return m


def _tu_hoa_rules(loai_keys: tuple, limit: int = 2, keywords: tuple = ()) -> list[dict]:
    """Rule diễn giải Tứ Hóa ĐÃ DUYỆT từ bảng tu_hoa_nguon (atomize Tinh Hoa Tập Thành),
    khớp loại (song_loc / loc_ky_xung / trung_phung / tu_hoa). [] nếu bảng chưa có.

    keywords: tuple các chuỗi thay thế — lọc câu ĐÚNG hóa (vd tự-hóa-Lộc chỉ lấy câu về Lộc).
    Lọc phía Python (chuẩn dấu tiếng Việt, tránh LIKE bỏ dấu). Không câu nào khớp → fallback
    trả rule chung của loại (đừng để trống khi vẫn có nguồn hợp lệ).
    """
    conn = _db()
    if conn is None:
        return []
    try:
        ph = ",".join("?" * len(loai_keys))
        rows = conn.execute(
            f"SELECT rule, nguon_book FROM tu_hoa_nguon WHERE loai IN ({ph}) "
            f"AND founder_verified=1 ORDER BY id", loai_keys).fetchall()
        out = [{"rule": r[0], "nguon": r[1]} for r in rows]
        if keywords:
            kws = [k.lower() for k in keywords]
            filt = [r for r in out if any(k in r["rule"].lower() for k in kws)]
            out = filt or out                     # fallback nếu keyword không khớp gì
        return out[:limit]
    except Exception:
        return []


# ── Tầng luận SÂU cho phi tinh (journal tu-hoa-truy-nguyen #551 + #149) ────────
# nghĩa từng chiều TỰ HÓA — nguyên lý "tự phát, không tích, ĐẢO dấu" (Đạo pháp Tự nhiên)
_TU_HOA_NGHIA = {
    "Lộc": "Lộc TỰ PHÁT TÁN ngay tại cung — phúc/lộc đến mà giữ không được (cổ pháp: đại quý dễ rớt trung quý), khí hướng RA ngoài.",
    "Quyền": "Quyền TỰ NẮM ngay tại cung — chủ động mạnh nhưng dễ độc đoán, sức tự tiêu.",
    "Khoa": "Khoa/phong độ TỰ LỘ tại cung — cần có dẫn dắt, kích phát mới thành danh.",
    "Kỵ": "chỗ TỰ BẾ, nhưng cái nghẽn TỰ BUNG thành dẫn động — bó buộc được kích đúng thì bật ra cơ hội (chớ vội kêu hung).",
}
_HOA_KW = {                                        # chuỗi tìm câu ĐÚNG hóa (đủ dị bản Kị/Kỵ)
    "Lộc": ("tự hóa lộc", "hóa lộc"),
    "Quyền": ("tự hóa quyền", "hóa quyền"),
    "Khoa": ("tự hóa khoa", "hóa khoa"),
    "Kỵ": ("tự hóa kị", "tự hóa kỵ", "hóa kị", "hóa kỵ"),
}
_TU_HOA_NGUYEN_LY = ("tự hóa = 自 TỰ-PHÁT (khí ra NGAY tại chỗ, KHÔNG tích được) → thường ĐẢO dấu: "
                     "tốt mà tự hóa thì hao, xấu mà tự hóa thì động. Neo: 'Đạo pháp Tự nhiên' — cái tự-nó-thế.")
# Hóa Kỵ chồng tầng = ĐIỂM QUAY của cả cục (thần cơ) — đọc điểm chuyển, không chỉ hung
_KY_THAN_CO = ("Hóa Kỵ = ĐIỂM QUAY của cả cục (thần cơ) — khí THU về, trời đất trở mình; cổ pháp quẻ Phục "
               "'phản phục kỳ đạo… kiến thiên địa chi tâm' (lòng trời hiện ở CHỖ QUAY VỀ). Nên TĨNH quan-sát "
               "điểm chuyển, không nôn nóng phán hung.")


def phi_hoa(la_so: dict, layer_cans: list, *, with_rules: bool = True) -> dict:
    """Phi tinh TỨ HÓA CHỒNG TẦNG — trụ cột phái Tứ Hóa (Tinh Hoa Tập Thành).

    layer_cans = [(tên_tầng, can), ...] theo thứ tự nguyên cục → đại vận → lưu niên →
    lưu nguyệt. Trả:
      • tu_hoa: cung TỰ HÓA (can cung hóa chính sao ngồi trong cung đó).
      • trung_phung: sao bị ≥2 tầng cùng hóa (song Lộc cát / Lộc-Kỵ xung giằng co / …).
    Deterministic. Ý nghĩa dùng nhãn KHUNG chuẩn (song Lộc=cát mạnh, Lộc-Kỵ=mâu thuẫn);
    diễn giải sâu để atomize Tinh Hoa Tập Thành sau (grounded).

    with_rules=False → BỎ QUA truy vấn câu luận trích sách (nguon=[]) cho nhanh khi chỉ
    cần XƯƠNG cấu trúc (life_arc lặp trăm mốc — không cần dẫn sách mỗi mốc).
    """
    def _rules(*a, **k):
        return _tu_hoa_rules(*a, **k) if with_rules else []
    sb = _star_branch_map(la_so)
    bi_pal = {p["branch_index"]: p["name"] for p in la_so.get("palaces", [])}
    # sao → [(tầng, hóa)]
    hits: dict = {}
    for tang, can in layer_cans:
        for hoa, star in TU_HOA_TABLE.get(can, {}).items():
            if star in sb:
                hits.setdefault(star, []).append({"tang": tang, "hoa": hoa})
    trung_phung = []
    for star, hs in hits.items():
        if len(hs) < 2:
            continue
        hoas = [h["hoa"] for h in hs]
        if all(h == "Lộc" for h in hoas):
            loai, tot, lk = "Song Lộc trùng phùng", True, ("song_loc", "hoa_nghia")
            nghia = "hai tầng cùng rọi Lộc lên sao này — cát lực rất lớn, chỗ được nuôi dưỡng mạnh."
        elif "Lộc" in hoas and ("Kỵ" in hoas):
            loai, tot, lk = "Lộc–Kỵ xung", False, ("loc_ky_xung",)
            nghia = "một tầng cho Lộc, một tầng cho Kỵ trên cùng sao — giằng co, được-mất lẫn lộn, cần cẩn trọng."
        elif hoas.count("Kỵ") >= 2:
            loai, tot, lk = "Song Kỵ trùng phùng", False, ("loc_ky_xung", "trung_phung")
            nghia = "hai tầng cùng rọi Kỵ — chỗ hao tâm nặng, nên tĩnh không nên động."
        else:
            loai, tot = "Trùng phùng " + "+".join(dict.fromkeys(hoas)), None
            # kéo rule theo hóa nổi bật: có Lộc → song_loc; có Kỵ → loc_ky_xung; + nghĩa-hóa
            lk = (("song_loc", "hoa_nghia") if "Lộc" in hoas
                  else ("loc_ky_xung", "hoa_nghia") if "Kỵ" in hoas
                  else ("hoa_nghia", "trung_phung"))
            nghia = "sao này được nhiều tầng thời gian cùng kích hoạt — điểm cần quan-sát kỹ."
        trung_phung.append({
            "sao": star, "cung": bi_pal.get(sb[star], "?"),
            "tang_hoa": hs, "loai": loai, "cat": tot, "nghia": nghia,
            # NGUYÊN LÝ đọc (diễn giải có nhãn, tách khỏi nguon): Kỵ chồng tầng = điểm quay/thần cơ
            "nguyen_ly": _KY_THAN_CO if "Kỵ" in hoas else None,
            "nguon": _rules(lk),                 # câu luận trích sách (nếu đã atomize)
        })
    tu_hoa = []
    for p in la_so.get("palaces", []):
        can, bi = p.get("can"), p["branch_index"]
        for hoa, star in TU_HOA_TABLE.get(can, {}).items():
            if sb.get(star) == bi:                          # sao ngồi ngay cung có can hóa nó
                tu_hoa.append({
                    "cung": p["name"], "sao": star, "hoa": hoa,
                    "nghia": f"cung {p['name']} TỰ HÓA {hoa} ({star}) — {_TU_HOA_NGHIA.get(hoa, '')}",
                    "nguyen_ly": _TU_HOA_NGUYEN_LY,           # diễn giải có nhãn (Đạo pháp Tự nhiên)
                    "nguon": _rules(("tu_hoa",), keywords=_HOA_KW.get(hoa, ())),  # trích ĐÚNG hóa
                })
    return {"tu_hoa": tu_hoa, "trung_phung": trung_phung}


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
    # FOREGROUND nền bẩm sinh (Mệnh chủ · Thân chủ · Cục) — đọc TRƯỚC (soil-before-seed).
    nm = blk.get("nen_menh")
    if nm:
        cuc = nm.get("cuc") or {}
        cuc_s = (f"{cuc.get('cuc_name')} (hành nền {cuc.get('element')} — {cuc.get('nature')})"
                 if cuc.get("available") else "?")
        dong = " (Mệnh-Thân đồng cung)" if nm.get("menh_than_dong_cung") else ""
        lines.append(f"### NỀN BẨM SINH (KHÔNG đổi — foreground): Mệnh chủ {nm.get('menh_chu')} · "
                     f"Thân chủ {nm.get('than_chu')} · Cục {cuc_s} · Thân cư {nm.get('than_cung')}{dong}. "
                     f"Mọi tầng vận hạn VẬN HÀNH trên nền này (mệnh là ĐỘNG TỪ, không phải số định sẵn).")
    bt = blk.get("bao_tram_dai_van")
    if bt:
        bt_sao = ", ".join(bt["sao"]) or "Vô Chính Diệu"
        lines.append(f"### BỐI CẢNH — Đại Vận bao trùm (LẤY LÀM CHỦ): vận V{bt['cycle_index']} "
                     f"tuổi {bt['khoang_tuoi'][0]}-{bt['khoang_tuoi'][1]}, cung {bt['cung']} ({bt_sao}). "
                     f"Đọc tầng này như MỘT BƯỚC cụ thể trong đại vận đó.")
        for s in bt.get("sao_nguon", []):
            lines.append(f"  · {s['sao']} (đại vận): {s['dich']} (nguồn: {s['nguon']})")
    bln = blk.get("bao_tram_luu_nien")
    if bln:
        bln_sao = ", ".join(bln["sao"]) or "Vô Chính Diệu"
        lines.append(f"### BỐI CẢNH — Lưu Niên bao trùm (năm {bln['nam_can_chi']}): lưu niên Mệnh "
                     f"cung {bln['cung']} ({bln_sao}). Tháng/tuần/ngày là MỘT BƯỚC trong năm này "
                     f"(đại vận làm chủ → năm nói thêm một bước → rồi mới tới tầng nhỏ).")
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
    ph = blk.get("phi_hoa") or {}
    if ph.get("trung_phung"):
        lines.append("### TRỤ CỘT Tứ Hóa CHỒNG TẦNG (phi tinh — quan trọng nhất, đọc kỹ):")
        for t in ph["trung_phung"]:
            tang_list = " + ".join(f"{x['tang']} hóa {x['hoa']}" for x in t["tang_hoa"])
            lines.append(f"- {t['loai']}: sao {t['sao']} (cung {t['cung']}) — {tang_list}. {t['nghia']}")
            if t.get("nguyen_ly"):
                lines.append(f"    → NGUYÊN LÝ đọc: {t['nguyen_ly']}")
            for g in (t.get("nguon") or [])[:1]:
                lines.append(f"    (nguồn: {g['rule']} — {g['nguon']})")
    if ph.get("tu_hoa"):
        lines.append(f"### Tự hóa (cung tự hóa sao của chính nó) — NGUYÊN LÝ: {_TU_HOA_NGUYEN_LY}")
        for t in ph["tu_hoa"]:
            lines.append(f"- {t['nghia']}")
            for g in (t.get("nguon") or [])[:1]:
                lines.append(f"    (nguồn: {g['rule']} — {g['nguon']})")
    if blk.get("luu_y_vi_mo"):
        lines.append(f"### Lưu ý: {blk['luu_y_vi_mo']}")
    return "\n".join(lines)


# ── FOREGROUND: nền bẩm sinh (Mệnh chủ · Thân chủ · Cục) + Lưu Niên bao trùm ──
def _nen_menh(la_so: dict) -> dict:
    """Nền bẩm sinh KHÔNG đổi — foreground ĐẦU mỗi buổi đọc (soil-before-seed,
    khớp [[tu_vi_doc_la_so_tien_trinh_phan_lop]]). Mệnh chủ / Thân chủ / Cục là hằng
    số của cả đời; mọi tầng vận hạn VẬN HÀNH trên nền này (mệnh là động từ — Iron #8)."""
    from engine.tu_vi.than_cu import doc_cuc
    menh_p = _palace_at(la_so, la_so.get("menh_index", 0))
    than_p = _palace_at(la_so, la_so.get("than_index", 0))
    return {
        "menh_chu": la_so.get("menh_chu"),
        "than_chu": la_so.get("than_chu"),
        "cuc": doc_cuc(la_so),                       # {cuc_name, element, nature, source}
        "menh_cung_vi_tri": la_so.get("menh_branch"),
        "than_cung": than_p["name"] if than_p else None,
        "menh_than_dong_cung": la_so.get("menh_index") == la_so.get("than_index"),
        "menh_sao": _stars_at(la_so, la_so.get("menh_index", 0)),
        "note": ("Nền bẩm sinh (KHÔNG đổi cả đời) — Mệnh chủ + Thân chủ + Cục là hành nền "
                 "mà mọi vận hạn vận hành trên đó. Đọc vận = xem cái nền này VẬN HÀNH ra sao "
                 "qua thời gian, KHÔNG phải số phận định sẵn."),
    }


def _bao_tram_luu_nien(la_so: dict, year: int) -> dict:
    """Lưu Niên (năm) BAO TRÙM một tầng nhỏ hơn (tháng/tuần/ngày) — lồng tầng rõ hơn:
    năm là bối cảnh giữa Đại Vận và Tháng (cổ pháp: đại hạn làm chủ, lưu niên nói thêm
    một bước, rồi mới tới lưu nguyệt)."""
    y_can, y_chi = _year_stem_branch(year)
    bi = BRANCHES_TVI.index(y_chi)
    p = _palace_at(la_so, bi)
    pname = p["name"] if p else "?"
    stars = _stars_at(la_so, bi) or _stars_at(la_so, (bi + 6) % 12)
    return {
        "year": year, "nam_can_chi": f"{y_can} {y_chi}",
        "cung": pname, "vi_tri": y_chi, "sao": stars,
        "tu_hoa_van": [h for h in _hoa_lit(y_can, la_so) if not h["cung"].startswith("(")],
    }


def _wire_layers(la_so: dict, birth, blk: dict, tang: str, kw: dict, *, with_rules: bool = True) -> None:
    """LỒNG TẦNG đầy đủ (mutate blk): nền bẩm sinh → Đại Vận bao trùm → Lưu Niên bao
    trùm → phi tinh Tứ Hóa chồng tầng. Dùng chung cho van_han_luan + life_arc (tránh
    diverge). with_rules=False → phi_hoa bỏ truy vấn dẫn sách (nhanh cho arc)."""
    blk["nen_menh"] = _nen_menh(la_so)               # foreground bẩm sinh (mọi tầng)
    blk["nguyen_cuc_can"] = la_so.get("year_stem")   # can nguyên cục (arc cộng hưởng đại vận)
    if tang in ("luu_nien", "luu_nguyet", "tuan", "luu_nhat"):
        try:
            byear = int(str(birth)[:4])
            yr = int(str(blk.get("solar", ""))[:4]) if tang == "luu_nhat" else int(kw.get("year"))
            blk["bao_tram_dai_van"] = _bao_tram_dai_van(la_so, byear, yr)
        except Exception:
            blk["bao_tram_dai_van"] = None
    # Lưu Niên bao trùm — chỉ cho tầng NHỎ HƠN năm (tháng/tuần/ngày)
    if tang in ("luu_nguyet", "tuan", "luu_nhat"):
        try:
            ly = (blk.get("am_lich") or {}).get("nam") or int(kw.get("year"))
            blk["bao_tram_luu_nien"] = _bao_tram_luu_nien(la_so, int(ly))
        except Exception:
            blk["bao_tram_luu_nien"] = None
    # TRỤ CỘT phi-tinh Tứ Hóa chồng tầng (Tinh Hoa Tập Thành): gom can từng tầng.
    layer_cans = [("Nguyên cục", la_so.get("year_stem"))]
    if tang == "dai_van" and blk.get("tu_hoa_can"):     # đại vận đọc lẻ: thêm can chính nó
        layer_cans.append(("Đại vận", blk["tu_hoa_can"]))
    bt = blk.get("bao_tram_dai_van")
    if bt and bt.get("can"):
        layer_cans.append(("Đại vận", bt["can"]))
    if tang == "luu_nien":
        layer_cans.append(("Lưu niên", _year_stem_branch(int(kw["year"]))[0]))
    if tang in ("luu_nguyet", "tuan") and blk.get("am_lich"):
        layer_cans.append(("Lưu niên", blk["am_lich"]["nam_can_chi"].split()[0]))
        layer_cans.append(("Lưu nguyệt", blk.get("month_can") or _month_can(
            blk["am_lich"]["nam_can_chi"].split()[0], blk["am_lich"]["thang"])))
    if tang == "luu_nhat":
        layer_cans.append(("Lưu nhật (can ngày)", blk.get("day_can")))
    blk["phi_hoa"] = phi_hoa(la_so, [(t, c) for t, c in layer_cans if c], with_rules=with_rules)


# ── BỨC TRANH CUỘC ĐỜI THĂNG TRẦM — đường cong KHÍ (tất định, 0-LLM) ───────────
# ⚠️ GUARD Iron #9: đây là BẢN ĐỒ KHÍ động↔tĩnh, TUYỆT ĐỐI KHÔNG phải đồ thị bói
# giàu-nghèo / thắng-thua (=tà mạng Brahmajāla). "Thăng" = khí mở/động/tụ lực (nên
# HÀNH); "Trầm" = khí thu/tĩnh/quay (nên DƯỠNG-TU). Cả hai đều KHÔNG cát/hung định sẵn.
_CUNG_DONG = {"Thiên Di", "Quan Lộc", "Tài Bạch", "Phu Thê"}   # khí HƯỚNG RA — động
_CUNG_TINH = {"Tật Ách", "Phúc Đức", "Phụ Mẫu"}               # khí THU VÀO — tĩnh
_ARC_DISCLAIMER = (
    "Đường cong này là BẢN ĐỒ KHÍ (động ↔ tĩnh) để SOI TÂM — chỗ nào nên HÀNH, chỗ "
    "nào nên DƯỠNG — KHÔNG phải đồ thị đoán giàu-nghèo / thắng-thua / năm phát năm lụn. "
    "Trầm KHÔNG phải xui; trầm = mùa nghỉ. Mệnh là ĐỘNG TỪ: cách vận hành cái tính qua "
    "thời gian, không phải bản án. Lá số không thay tu học hay quyết định của chính mình."
)
_TRUC_NOTE = ("Trục dọc = khí ĐỘNG (mở/hành — thăng, phía trên) ↔ khí TĨNH (thu/dưỡng — "
              "trầm, phía dưới). KHÔNG phải trục tốt↔xấu / giàu↔nghèo.")


def _arc_point(blk: dict, tang: str, label: str) -> dict:
    """Rút CHỈ SỐ CẤU TRÚC tất định của 1 mốc từ block đã lồng tầng (0-LLM, 0 bịa).

    dong_tinh (hướng khí từ cung Mệnh vận) · dong_luc (cường độ: trùng phùng + Song
    Lộc/Kỵ) · diem_quay (Hóa Kỵ chồng tầng) · cong_huong (can trùng tầng trên) ·
    xa (tự hóa Lộc tại cung Mệnh vận). → khi ∈ [-1,1] cho đường cong + đường hành.
    """
    cung = blk.get("cung_the", "?")
    if cung in _CUNG_DONG:
        huong, dong_tinh = 1, "động"
    elif cung in _CUNG_TINH:
        huong, dong_tinh = -1, "tĩnh"
    else:
        huong, dong_tinh = 0, "trung"
    ph = blk.get("phi_hoa") or {}
    tp = ph.get("trung_phung") or []
    tuhoa = ph.get("tu_hoa") or []
    song_loc = sum(1 for t in tp if str(t.get("loai", "")).startswith("Song Lộc"))
    song_ky = sum(1 for t in tp if str(t.get("loai", "")).startswith("Song Kỵ"))
    # điểm quay = có Hóa Kỵ chồng tầng (bất kỳ trùng phùng nào chứa Kỵ)
    diem_quay = any("Kỵ" in [x["hoa"] for x in t.get("tang_hoa", [])] for t in tp)
    # xả = tự hóa Lộc NGAY tại cung Mệnh vận ("có mà giữ không được")
    xa = any(t.get("hoa") == "Lộc" and t.get("cung") == cung for t in tuhoa)
    # cộng hưởng = can tầng nhỏ trùng can tầng trên → Tứ Hóa khuếch đại (mốc đậm)
    cong_huong = False
    if tang == "luu_nguyet" and blk.get("am_lich"):
        cong_huong = (blk.get("month_can") == blk["am_lich"]["nam_can_chi"].split()[0])
    elif tang == "luu_nien":
        bt = blk.get("bao_tram_dai_van") or {}
        cong_huong = bool(bt.get("can") and bt["can"] == blk.get("year_can_chi", " ").split()[0])
    elif tang == "dai_van":
        cong_huong = bool(blk.get("tu_hoa_can") and blk["tu_hoa_can"] == blk.get("nguyen_cuc_can"))
    # ── KHÍ (động ↔ tĩnh), KHÔNG phải cát ↔ hung ──
    khi = 0.55 * huong
    khi += 0.18 * song_loc + (0.12 if xa else 0.0)     # Lộc/tự hóa Lộc → khí mở (thăng)
    khi -= 0.18 * song_ky                              # Kỵ chồng → khí thu (trầm)
    if diem_quay and not song_ky:
        khi -= 0.15                                    # điểm quay lẻ → nghiêng trầm/quay
    if cong_huong:
        khi *= 1.25                                    # cộng hưởng → biên độ ĐẬM hơn
    khi = max(-1.0, min(1.0, round(khi, 3)))
    # ── đường hành (DÙNG / TĨNH / CẨN) — nên làm gì cho hợp thời ──
    # Điểm quay + khí VẪN nghiêng động (khi>0.15) → DÙNG nhưng tỉnh táo ở khúc chuyển
    # (khớp ví dụ founder T7: Thiên Di động + tự hóa Lộc, dù có Kỵ chồng tầng vẫn DÙNG).
    # Điểm quay mà khí thu/trầm → CẨN. Không quay: theo hướng cung.
    if diem_quay and khi > 0.15:
        duong_hanh, hanh_y = "DÙNG", "khí mở nhưng có điểm quay — dùng cơ hội, tỉnh táo ở khúc chuyển (chớ tích)"
    elif diem_quay:
        duong_hanh, hanh_y = "CẨN", "khí quay — tĩnh quan-sát điểm chuyển, chớ khởi sự lớn"
    elif huong > 0 or (huong == 0 and (song_loc or xa)):
        duong_hanh, hanh_y = "DÙNG", "khí mở — nên ra ngoài, dùng cơ hội (đừng tích giữ)"
    elif huong < 0:
        duong_hanh, hanh_y = "TĨNH", "khí thu — mùa dưỡng thân, tĩnh tâm, không khởi sự lớn"
    else:
        duong_hanh, hanh_y = "TĨNH", "khí trung hòa — giữ nhịp, tùy duyên"
    # ── 1 dòng "đọc" (tất định, KHÔNG cát/hung) ──
    parts = [f"Mệnh vận ở {cung} ({dong_tinh})"]
    if cong_huong:
        parts.append("can trùng tầng trên (cộng hưởng — mốc đậm)")
    if song_loc:
        parts.append("Song Lộc (được nuôi mạnh)")
    if song_ky:
        parts.append("Song Kỵ (khí thu)")
    if diem_quay and not song_ky:
        parts.append("Hóa Kỵ chồng tầng (điểm quay)")
    if xa:
        parts.append("tự hóa Lộc (có mà khó giữ)")
    doc = " · ".join(parts) + f" → {duong_hanh}: {hanh_y}"
    pt = {
        "label": label,
        "cung_the": cung, "vi_tri": blk.get("vi_tri"),
        "dong_tinh": dong_tinh, "huong": huong,
        "khi": khi,
        "dong_luc": {"trung_phung": len(tp), "song_loc": song_loc, "song_ky": song_ky},
        "diem_quay": diem_quay, "cong_huong": cong_huong, "xa": xa,
        "duong_hanh": duong_hanh, "doc": doc,
    }
    if tang == "luu_nguyet" and blk.get("am_lich"):
        pt["year"] = blk.get("year"); pt["month"] = blk.get("month")
        pt["am_thang"] = blk["am_lich"]["thang"]
        pt["am_nam_can_chi"] = blk["am_lich"]["nam_can_chi"]
    elif tang == "luu_nien":
        pt["year"] = blk.get("year"); pt["nam_can_chi"] = blk.get("year_can_chi")
    elif tang == "dai_van":
        kt = blk.get("khoang_tuoi") or [None, None]
        pt["cycle_index"] = blk.get("cycle_index")
        pt["start_age"] = kt[0]; pt["end_age"] = kt[1]
    return pt


def life_arc(person: dict, tu_nam: int, den_nam: int, buoc: str = "thang") -> dict:
    """BỨC TRANH CUỘC ĐỜI THĂNG TRẦM — soi liên tục các tháng/năm → đường cong KHÍ.

    Lặp mốc (tháng dương hoặc năm) tu_nam..den_nam, mỗi mốc rút chỉ số cấu trúc TẤT
    ĐỊNH (0 LLM) qua _arc_point. Trả nền bẩm sinh (foreground) + list mốc + đường hành
    mỗi mốc. ⚠️ Iron #9: bản đồ KHÍ động↔tĩnh, KHÔNG bói giàu-nghèo/thắng-thua.

    buoc = "thang" (12 mốc/năm — mạch thở) | "nam" (1 mốc/năm) | "dai_van" (CẢ ĐỜI theo
    tuổi — mỗi Đại Vận 10 năm 1 mốc, trục tuổi; tu_nam/den_nam bỏ qua).
    """
    if buoc not in ("thang", "nam", "dai_van"):
        raise ValueError("buoc phải là 'thang' | 'nam' | 'dai_van'")
    if buoc != "dai_van":
        if den_nam < tu_nam:
            raise ValueError("den_nam < tu_nam")
        span = den_nam - tu_nam + 1
        if buoc == "thang" and span > 30:
            raise ValueError("buoc='thang': khoảng năm ≤ 30 (≤360 mốc)")
        if buoc == "nam" and span > 100:
            raise ValueError("buoc='nam': khoảng năm ≤ 100")

    from engine.tu_vi.from_birth import cast_la_so_from_birth
    birth = person["birth_datetime_local"]
    gender = person.get("gender") or "nam"
    la_so = cast_la_so_from_birth(birth_datetime_local=birth, gender=gender)

    diem: list[dict] = []
    if buoc == "dai_van":
        # CẢ ĐỜI theo tuổi — mỗi Đại Vận (10 năm) = 1 mốc, trục hoành = tuổi khởi vận.
        for dv in sorted(la_so.get("dai_van", []), key=lambda d: d["start_age"]):
            blk = dai_van_block(la_so, dv["cycle_index"])
            if not blk.get("available"):
                continue
            _wire_layers(la_so, birth, blk, "dai_van", {}, with_rules=False)
            diem.append(_arc_point(blk, "dai_van", f"{dv['start_age']}t"))
    elif buoc == "nam":
        for y in range(tu_nam, den_nam + 1):
            blk = luu_nien_block(la_so, y)
            _wire_layers(la_so, birth, blk, "luu_nien", {"year": y}, with_rules=False)
            diem.append(_arc_point(blk, "luu_nien", str(y)))
    else:
        for y in range(tu_nam, den_nam + 1):
            for m in range(1, 13):
                blk = luu_nguyet_block(la_so, y, m)
                _wire_layers(la_so, birth, blk, "luu_nguyet", {"year": y, "month": m}, with_rules=False)
                diem.append(_arc_point(blk, "luu_nguyet", f"T{m}/{y}"))
    return {
        "available": True,
        "buoc": buoc, "tu_nam": tu_nam, "den_nam": den_nam,
        "nen_menh": _nen_menh(la_so),
        "diem": diem,
        "truc_note": _TRUC_NOTE,
        "disclaimer": _ARC_DISCLAIMER,
    }


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
    # LỒNG TẦNG đầy đủ (nền bẩm sinh → Đại Vận → Lưu Niên bao trùm → phi tinh chồng tầng).
    _wire_layers(la_so, birth, blk, tang, kw)
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
