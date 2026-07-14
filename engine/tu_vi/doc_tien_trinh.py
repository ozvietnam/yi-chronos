"""Đọc lá số theo TRÌNH TỰ đất-trước-hạt + KỶ LUẬT 4 lớp (Anh chốt 2026-06-28).

Paradigm (memory tu_vi_doc_la_so_tien_trinh_phan_lop):
  TIẾN TRÌNH: Phúc Đức (phúc ấm tổ tiên) → Phụ Mẫu (gen, mầm khỏe/yếu)
              → Điền Trạch (vun hay phá) → đặt Mệnh+Thân vào môi trường đó.
  4 LỚP (không nhảy cóc, chống ảo giác):
    1. tính chất TỪNG sao (def)
    2. sao an TRÊN cung (per-cung)
    3. COMBO — CHỈ khi đã kết thành khối THẬT (rule-match, không gom lỏng)
    4. tam phương tứ chính
  Quy tắc: quote-or-silence — chỉ nói cái CÓ NGUỒN trong sao_noi_dung;
           ô thiếu → KHAI TRỐNG (gaps), KHÔNG bịa. Iron #8 (mệnh động từ), #9 (không predict).

Engine TẤT ĐỊNH: 0 LLM. LLM (nếu có) chỉ được biên tập câu chữ ở tầng trên, không sinh nghĩa.
"""
from __future__ import annotations
import os, sqlite3
from typing import Optional

from engine.tu_vi import from_birth, an_sao, la_so_input_builder, cach_cuc_named

_DB_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "yi_wiki", "wiki.sqlite3")
BRANCHES = an_sao.BRANCHES_TVI

# Thứ tự đọc (đất trước, hạt sau). Thân đọc kèm Mệnh (thường đồng/giao).
TIEN_TRINH = ["Phúc Đức", "Phụ Mẫu", "Điền Trạch", "Mệnh"]

CUNG_VAI_TRO = {
    "Phúc Đức": "phúc ấm tổ tiên — nền chạy ngầm, dày hay mỏng",
    "Phụ Mẫu": "gen trao truyền trực tiếp — mầm của ta khỏe hay yếu, ngả tốt hay xấu",
    "Điền Trạch": "vun bồi âm đức hay 'mang tiền nhà đi phá' — đầu đời tới 16-20 và trưởng thành",
    "Mệnh": "đặt Mệnh+Thân vào môi trường ba cung trên mới cảm rõ",
}


def _stars_per_cung(la_so: dict) -> dict:
    """cung_name -> {chi, branch_index, sao:[...]} thuần toán từ cast_la_so."""
    pal = {p["branch_index"]: p["name"] for p in la_so["palaces"]}
    out = {name: {"branch_index": bi, "chi": BRANCHES[bi], "sao": []}
           for bi, name in pal.items()}
    name_by_idx = pal
    GROUPS = ["chinh_tinh", "phu_tinh", "sat_tinh", "thai_tue_belt",
              "bac_si_belt", "tuong_tinh_belt", "sao_le", "sao_q2", "sao_q3"]
    for f in GROUPS:
        v = la_so.get(f)
        if isinstance(v, dict):
            for s, i in v.items():
                if isinstance(i, int) and i in name_by_idx:
                    out[name_by_idx[i]]["sao"].append(s)
    return out


def _pull(cur, sao: str, lop: str, cung: Optional[str] = None) -> list[dict]:
    # CHỈ nội dung ĐÃ DUYỆT ĐỐI KHÁNG (founder_verified=1): quote có trong sách + dịch
    # không bịa (pipeline verify_sao_noi_dung.py). Chặn 84 dòng fabricated (fv=-1) +
    # dòng treo (fv=0) khỏi route trả phí — quote-or-silence, thiếu → gaps/hoàn xu.
    if lop == "def":
        rows = cur.execute(
            "SELECT dich_thuan_viet, quote_goc, nguon_book, nguon_loc "
            "FROM sao_noi_dung WHERE sao_vi=? AND lop='def' AND founder_verified=1 "
            "AND dich_thuan_viet IS NOT NULL AND dich_thuan_viet!='' LIMIT 2", (sao,)).fetchall()
    else:
        rows = cur.execute(
            "SELECT dich_thuan_viet, quote_goc, nguon_book, nguon_loc "
            "FROM sao_noi_dung WHERE sao_vi=? AND lop='cung' AND cung=? AND founder_verified=1 "
            "AND dich_thuan_viet IS NOT NULL AND dich_thuan_viet!='' LIMIT 2", (sao, cung)).fetchall()
    return [{"dich": r[0], "quote_goc": r[1], "nguon_book": r[2], "nguon_loc": r[3]} for r in rows]


def _cach_per_cung(la_so: dict, cachs: list[dict]) -> dict:
    """Map cách cục ĐÃ KẾT KHỐI -> cung chứa nó (qua sao trong match_rule). Chỉ combo thật."""
    spc = _stars_per_cung(la_so)
    star_to_cung = {}
    for cung, d in spc.items():
        for s in d["sao"]:
            star_to_cung[s] = cung
    out = {}
    for c in cachs:
        cungs = set()
        for rule in (c.get("match_rule") or []):
            for key in ("stars", "any_of"):
                for s in (rule.get(key) or []):
                    if s in star_to_cung:
                        cungs.add(star_to_cung[s])
            if rule.get("star") in star_to_cung:
                cungs.add(star_to_cung[rule["star"]])
        for cu in cungs:
            out.setdefault(cu, []).append({"ten": c["ten"], "loai": c.get("loai"),
                                           "dieu_kien": c.get("dieu_kien"), "atoms": c.get("atoms_count")})
    return out


def _tam_phuong(branch_index: int, spc_by_idx: dict) -> dict:
    """Tam hợp (i, i+4, i+8) + xung (i+6), kèm sao mỗi cung hội chiếu."""
    tam = [(i % 12) for i in (branch_index, branch_index + 4, branch_index + 8)]
    xung = (branch_index + 6) % 12
    def info(i):
        d = spc_by_idx.get(i, {})
        return {"chi": BRANCHES[i], "cung": d.get("name"), "sao": d.get("sao", [])}
    return {"tam_hop": [info(i) for i in tam], "xung": info(xung)}


def doc_cung(cur, cung_name: str, node: dict, cach_in_cung: list, tam_phuong: dict) -> dict:
    """Đọc 1 cung theo 4 lớp, quote-or-silence."""
    lop1, lop2, gaps = [], [], []
    for s in node["sao"]:
        d = _pull(cur, s, "def")
        if d:
            lop1.append({"sao": s, "nguon": d})
        else:
            gaps.append(f"{s}: thiếu def")
        c = _pull(cur, s, "cung", cung_name)
        if c:
            lop2.append({"sao": s, "nguon": c})
        else:
            gaps.append(f"{s} @ {cung_name}: thiếu per-cung")
    return {
        "cung": cung_name, "chi": node["chi"], "vai_tro": CUNG_VAI_TRO.get(cung_name, ""),
        "lop1_tinh_chat_sao": lop1,
        "lop2_sao_tren_cung": lop2,
        "lop3_combo_ket_khoi": cach_in_cung,   # CHỈ cách đã rule-match; rỗng = không có khối → KHÔNG bịa
        "lop4_tam_phuong_tu_chinh": tam_phuong,
        "gaps": gaps,
        "n_co_nguon": len(lop1) + len(lop2), "n_thieu": len(gaps),
    }


def doc_la_so_tien_trinh(birth_datetime_local: str, gender: str,
                         birth_year: Optional[int] = None,
                         db_path: Optional[str] = None,
                         province: Optional[str] = None) -> dict:
    """Đọc TRỌN lá số theo trình tự đất-trước-hạt. Tất định, có nguồn, khai trống chỗ thiếu.

    Trả: {meta, tien_trinh:[phuc_duc, phu_mau, dien_trach, menh], moi_truong_summary, gap_list}
    """
    by = birth_year or int(birth_datetime_local[:4])
    la = from_birth.cast_la_so_from_birth(birth_datetime_local=birth_datetime_local, gender=gender,
                                          province=province) if province else \
         from_birth.cast_la_so_from_birth(birth_datetime_local=birth_datetime_local, gender=gender)
    inp = la_so_input_builder.build_la_so_input(la, gender, birth_year=by)
    cachs = cach_cuc_named.match_named_cach_cucs(inp) or []

    spc = _stars_per_cung(la)
    spc_by_idx = {}
    for p in la["palaces"]:
        bi = p["branch_index"]
        spc_by_idx[bi] = {"name": p["name"], "sao": spc[p["name"]]["sao"]}
    cach_map = _cach_per_cung(la, cachs)

    # Mệnh-Thân đồng cung: so branch index cung Mệnh vs cung Thân (Thân là NHÃN trên 1 cung, không phải palace riêng)
    try:
        _hi = an_sao.hour_index_from_branch(la["hour_branch"])
        than_bi = an_sao.cung_than_index(la["lunar_month"], _hi)
        menh_than_dong = (spc["Mệnh"]["branch_index"] == than_bi)
    except Exception:
        menh_than_dong = None

    conn = sqlite3.connect(db_path or _DB_DEFAULT)
    cur = conn.cursor()
    try:
        readings = []
        for cung in TIEN_TRINH:
            node = spc[cung]
            tp = _tam_phuong(node["branch_index"], spc_by_idx)
            readings.append(doc_cung(cur, cung, node, cach_map.get(cung, []), tp))
    finally:
        conn.close()

    # môi trường = 3 cung đất; Mệnh đặt vào sau
    moi_truong = [r for r in readings if r["cung"] != "Mệnh"]
    gap_list = [g for r in readings for g in r["gaps"]]
    menh_node = spc["Mệnh"]
    return {
        "meta": {
            "sinh": birth_datetime_local, "gender": gender,
            "can_chi_nam": f"{la.get('year_stem')} {la.get('year_branch')}",
            "cuc": la.get("cuc_name"),
            "menh_chi": menh_node["chi"],
            "menh_than_dong_cung": menh_than_dong,
            "cach_cuc_that": [{"ten": c["ten"], "loai": c.get("loai"), "dieu_kien": c.get("dieu_kien")} for c in cachs],
            "disclaimer": ("Tử Vi MƯỢN khung soi tâm — không đoán hung-cát, không thay tu học/y tế. "
                           "Mệnh là động từ: đọc cách VẬN HÀNH, không phán số phận."),
        },
        "tien_trinh": readings,
        "moi_truong_cung": [r["cung"] for r in moi_truong],
        "gap_list": gap_list,
        "n_gap": len(gap_list),
    }


def doc_mot_cung(birth_datetime_local: str, gender: str, cung_name: str,
                 birth_year: Optional[int] = None, db_path: Optional[str] = None,
                 province: Optional[str] = None) -> dict:
    """Đọc grounded MỘT cung bất kỳ (cho route trả phí deep_cung).

    Tái dùng doc_cung (4 lớp, quote-or-silence): chỉ trả nghĩa CÓ NGUỒN trong
    sao_noi_dung; sao thiếu nguồn → vào `gaps`, KHÔNG bịa. Engine tất định 0 LLM —
    LLM tầng trên chỉ được biên tập câu chữ từ block này, cấm sinh nghĩa ngoài nguồn.

    cung_name: tên cung tiếng Việt (Mệnh, Phúc Đức, Tài Bạch, ...).
    Trả: dict như doc_cung + {ok, meta} | {ok:False, error} nếu cung_name sai.
    """
    by = birth_year or int(birth_datetime_local[:4])
    la = from_birth.cast_la_so_from_birth(birth_datetime_local=birth_datetime_local,
                                          gender=gender, province=province) if province else \
         from_birth.cast_la_so_from_birth(birth_datetime_local=birth_datetime_local, gender=gender)
    spc = _stars_per_cung(la)
    if cung_name not in spc:
        return {"ok": False, "error": f"cung không hợp lệ: {cung_name}",
                "cung_hop_le": sorted(spc.keys())}
    inp = la_so_input_builder.build_la_so_input(la, gender, birth_year=by)
    cachs = cach_cuc_named.match_named_cach_cucs(inp) or []
    spc_by_idx = {p["branch_index"]: {"name": p["name"], "sao": spc[p["name"]]["sao"]}
                  for p in la["palaces"]}
    cach_map = _cach_per_cung(la, cachs)
    node = spc[cung_name]
    tp = _tam_phuong(node["branch_index"], spc_by_idx)
    conn = sqlite3.connect(db_path or _DB_DEFAULT)
    try:
        reading = doc_cung(conn.cursor(), cung_name, node, cach_map.get(cung_name, []), tp)
    finally:
        conn.close()
    reading["ok"] = True
    reading["meta"] = {
        "sinh": birth_datetime_local, "gender": gender,
        "cuc": la.get("cuc_name"),
        "disclaimer": ("Tử Vi MƯỢN khung soi tâm — không đoán hung-cát, không thay tu học/y tế. "
                       "Mệnh là động từ: đọc cách VẬN HÀNH, không phán số phận."),
    }
    return reading
