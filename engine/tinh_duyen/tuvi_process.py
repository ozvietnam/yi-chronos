"""doc_tuvi_12_buoc — QUY TRÌNH 12 BƯỚC đọc tình duyên bằng Tử Vi Đẩu Số.

Engine DETERMINISTIC, KHÔNG gọi LLM, KHÔNG sửa reading.py. Đây là tầng QUY TRÌNH
(process) đọc lá số theo đúng trình tự một thầy Trung Châu (王亭之 — Vương Đình Chi)
soi hôn nhân: bắt đầu từ cung Phu Thê, lan ra tam chiếu / xung chiếu, rồi quét các
cung liên đới (Tử Tức, Điền Trạch, Nô Bộc = người thứ ba, Tật Ách, Tài Bạch, Mệnh),
cuối cùng là tầng ĐỘNG (đại vận / lưu niên).

PARADIGM (Iron Rule #4/#6/#8): KHÔNG BÓI — đọc đồng dạng, mệnh là ĐỘNG TỪ.
Lá số cho biết TÍNH (cấu trúc bẩm phú); engine đọc cách VẬN HÀNH cái tính đó.
KHÔNG phán "sẽ ly hôn / số cô quả". Định thời = "năm khí được kích hoạt / năm cần
giữ gìn", không phải lời tiên tri.

GROUNDING (vượt free-AI vốn chỉ trích web): mỗi luận điểm bám nguồn cổ THẬT —
  - kho tri thức tinh_duyen/knowledge/tuvi_phuthe.json (mỗi mục có _nguon trỏ về
    tc7.txt = 《王亭之 中州派紫微斗數 深造講義》 + 女命骨髓賦 + design doc),
  - bảng Miếu-Vượng-Hãm (Phú Thái Vi Q2 p0102),
  - dict cách cục Phú Thái Vi (545 cách),
  - wiki passages_fts (data/yi_wiki/wiki.sqlite3) khi cần câu cổ văn bổ trợ.

TÁI DÙNG engine sẵn (KHÔNG viết lại):
  - engine.tu_vi.an_sao              : PALACE_NAMES, BRANCHES_TVI, _fix, hour helpers
  - engine.tu_vi.from_birth          : cast_la_so_from_birth
  - engine.tu_vi.mieu_vuong_ham      : level_at / level_label (trạng thái sao)
  - engine.tu_vi.cach_cuc_dict       : match_cach_in_chart (cách cục)
  - engine.tu_vi.chiem_phu_the_v4    : chiem_phu_the_v4 (26 quy luật Phu Thê)
  - engine.tu_vi.dai_van_luu_nien_phu_the : cung_phu_the_dai_van + luu_nien_phu_the_markers
  - engine.tinh_duyen.knowledge_loader    : kho tri thức 6 JSON grounded _nguon
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional

from engine.tu_vi.an_sao import BRANCHES_TVI, PALACE_NAMES
from engine.tu_vi.from_birth import cast_la_so_from_birth
from engine.tu_vi.mieu_vuong_ham import level_at, level_label
from engine.tu_vi import cach_cuc_dict
from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4
from engine.tu_vi.dai_van_luu_nien_phu_the import (
    cung_phu_the_dai_van,
    luu_nien_phu_the_markers,
)
from engine.tinh_duyen import knowledge_loader as kb

METHOD_ID = "tinh_duyen_tuvi_12_buoc_v1"

# ─── Mức độ ảnh hưởng (gán theo doc #1 — đặc tả nhiệm vụ) ─────────────────────
TRUC_TIEP = "trực tiếp"   # cung Phu Thê + trạng thái + Hóa Kỵ + sát tại Phu Thê
GIAN_TIEP = "gián tiếp"   # tam chiếu / Quan Lộc / Tử Tức / đại vận / Mệnh
TIEM_AN = "tiềm ẩn"       # Nô Bộc / Điền Trạch / Tài Bạch / Tật Ách / lưu niên

_B2I = {b: i for i, b in enumerate(BRANCHES_TVI)}

# Đào hoa chư diệu (tên trong la_so → key kho dao_hoa_tinh)
_DAO_HOA_STARS = {
    "Thiên Diêu": "thien_dieu", "Hàm Trì": "ham_tri", "Mộc Dục": "moc_duc",
    "Đại Hao đào hoa": "dai_hao", "Hồng Loan": "hong_loan", "Thiên Hỉ": "thien_hi",
    "Văn Xương": "xuong_khuc", "Văn Khúc": "xuong_khuc",
}
# Lục sát (tên trong la_so.sat_tinh → key kho sat_tinh_phu_the)
_SAT_STARS = {
    "Kình Dương": "kinh_duong", "Đà La": "da_la", "Hỏa Tinh": "hoa_tinh",
    "Linh Tinh": "linh_tinh", "Địa Không": "dia_khong", "Địa Kiếp": "dia_kiep",
}
_CHINH_TINH_14 = (
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
    "Thất Sát", "Phá Quân",
)

_DISCLAIMER = (
    "Đọc đồng dạng — KHÔNG bói, KHÔNG phán định mệnh. Lá số cho biết TÍNH "
    "(cấu trúc bẩm phú); 'mệnh' là việc XỬ LÝ tính đó (mệnh là động từ — Iron Rule #8). "
    "Mốc định thời chỉ là 'năm khí được kích hoạt / năm cần giữ gìn'."
)

_WIKI_DB = Path(__file__).resolve().parents[2] / "data/yi_wiki/wiki.sqlite3"


# ─── Helpers cấu trúc cung / sao ──────────────────────────────────────────────
def _palace_index(la_so: dict, palace_name: str) -> Optional[int]:
    """Branch index (0..11) của 1 cung theo tên."""
    for p in la_so.get("palaces", []):
        if p.get("name") == palace_name:
            return p.get("branch_index")
    return None


def _stars_at_index(la_so: dict, idx: Optional[int]) -> dict[str, list[str]]:
    """Gom mọi sao tọa tại branch idx, phân nhóm chính/phụ/sát/đào hoa/lẻ."""
    if idx is None:
        return {"chinh": [], "phu": [], "sat": [], "dao_hoa": [], "q2": []}
    idx %= 12
    chinh = [s for s, i in (la_so.get("chinh_tinh") or {}).items() if i % 12 == idx]
    phu = [s for s, i in (la_so.get("phu_tinh") or {}).items() if i % 12 == idx]
    sat = [s for s, i in (la_so.get("sat_tinh") or {}).items() if i % 12 == idx]
    q2 = [s for s, i in (la_so.get("sao_q2") or {}).items()
          if isinstance(i, int) and i % 12 == idx]
    dao = [s for s in (chinh + phu + sat + q2) if s in _DAO_HOA_STARS]
    return {"chinh": chinh, "phu": phu, "sat": sat, "dao_hoa": dao, "q2": q2}


def _trang_thai(stars: list[str], branch: str) -> list[dict]:
    """Trạng thái Miếu/Vượng/Đắc/Bình/Lạc/Hãm của các chính tinh tại branch."""
    out = []
    for s in stars:
        lv = level_at(s, branch)
        if lv:
            out.append({"sao": s, "muc": lv, "nhan": level_label(lv)})
    return out


def _hoa_at_index(la_so: dict, idx: Optional[int]) -> list[dict]:
    """Tứ Hóa (Lộc/Quyền/Khoa/Kỵ) rơi vào cung tại idx (sao hóa đang tọa cung)."""
    if idx is None:
        return []
    idx %= 12
    chinh = la_so.get("chinh_tinh") or {}
    phu = la_so.get("phu_tinh") or {}
    out = []
    for hoa, star in (la_so.get("tu_hoa") or {}).items():
        pos = chinh.get(star, phu.get(star))
        if pos is not None and pos % 12 == idx:
            out.append({"hoa": hoa, "sao": star})
    return out


def _triet_tuan_at(la_so: dict, idx: Optional[int]) -> list[str]:
    """Triệt / Tuần án ngữ tại cung idx."""
    if idx is None:
        return []
    idx %= 12
    flags = []
    if idx in {i % 12 for i in (la_so.get("triet") or [])}:
        flags.append("Triệt")
    if idx in {i % 12 for i in (la_so.get("tuan") or [])}:
        flags.append("Tuần")
    return flags


def _kb_chinh_tinh(star: str) -> dict:
    """Tra mục chính-tinh-tại-Phu-Thê trong kho (grounded _nguon)."""
    table = kb.get("tuvi_phuthe").get("chinh_tinh_phu_the", {})
    return table.get(kb.name_to_key(star), {})


def _wiki_passage(query: str) -> Optional[dict]:
    """Lấy 1 passage cổ văn khớp query qua passages_fts (bổ trợ grounding)."""
    if not _WIKI_DB.exists():
        return None
    try:
        con = sqlite3.connect(f"file:{_WIKI_DB}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT p.raw_text, p.page_start, p.author_id "
                "FROM passages_fts f JOIN passages p ON p.rowid = f.rowid "
                "WHERE passages_fts MATCH ? ORDER BY length(p.raw_text) LIMIT 1",
                (query,),
            ).fetchone()
        finally:
            con.close()
        if row:
            txt = (row[0] or "").strip().replace("\n", " ")
            return {"trich": txt[:200], "trang": row[1],
                    "_nguon": f"wiki.sqlite3 passages (p{row[1]}, FTS '{query}')"}
    except Exception:
        return None
    return None


def _buoc(ten, sao_chinh, du_lieu, luan, muc_do, nguon):
    return {
        "ten_buoc": ten,
        "sao_chinh": sao_chinh,
        "du_lieu": du_lieu,
        "luan": luan,
        "_nguon": nguon,
        "muc_do_anh_huong": muc_do,
    }


# ─── 12 BƯỚC ──────────────────────────────────────────────────────────────────
def doc_tuvi_12_buoc(
    la_so: dict,
    gender: str = "nữ",
    as_of_year: Optional[int] = None,
) -> dict:
    """Đọc TRỌN 12 bước quy trình tình duyên Tử Vi từ 1 lá số đã an sao.

    Args:
        la_so: dict trả về bởi cast_la_so / cast_la_so_from_birth.
        gender: 'nữ' (mặc định — engine soi nữ mệnh) hoặc 'nam'.
        as_of_year: năm dương lịch dùng cho khung lưu niên (mặc định 2024-2034).

    Returns:
        {method_id, gender, paradigm, disclaimer, buoc: [12 step dict]}.
        Mỗi step: {ten_buoc, sao_chinh, du_lieu, luan, _nguon, muc_do_anh_huong}.
    """
    gender = (gender or "nữ").strip().lower()
    gender = "nữ" if gender in ("nữ", "nu", "female", "f", "") else "nam"

    pt_idx = _palace_index(la_so, "Phu Thê")
    pt_branch = BRANCHES_TVI[pt_idx % 12] if pt_idx is not None else "?"
    pt_stars = _stars_at_index(la_so, pt_idx)

    buoc: list[dict] = []

    # ── BƯỚC 1 — Cung Phu Thê (gốc trực tiếp) ─────────────────────────────────
    ct = pt_stars["chinh"]
    tt = _trang_thai(ct, pt_branch)
    hoa = _hoa_at_index(la_so, pt_idx)
    sat = pt_stars["sat"]
    dao = pt_stars["dao_hoa"]
    triet_tuan = _triet_tuan_at(la_so, pt_idx)
    kb_entries = [_kb_chinh_tinh(s) for s in ct]
    if ct:
        tt_str = ", ".join(f"{x['sao']} {x['muc']}" for x in tt) or "không rõ mức"
        nét = " ".join(e.get("tinh_chat_phoi_ngau", "") for e in kb_entries if e).strip()
        luan1 = (
            f"Cung Phu Thê tại {pt_branch} có {', '.join(ct)} ({tt_str}). "
            f"{nét} "
            "Đây là TÍNH phối ngẫu bẩm phú — vận hành tốt khi hiểu đúng cấu trúc này, "
            "không phải bản án."
        )
    else:
        luan1 = (
            f"Cung Phu Thê tại {pt_branch} VÔ CHÍNH DIỆU — mượn chính tinh cung xung "
            "chiếu (Quan Lộc) để luận; duyên cần điểm tựa bên ngoài định hình."
        )
    extras = []
    if hoa:
        extras.append("Tứ Hóa: " + ", ".join(f"{h['sao']} {h['hoa']}" for h in hoa))
    if sat:
        extras.append("Sát tinh tọa: " + ", ".join(sat))
    if dao:
        extras.append("Đào hoa: " + ", ".join(dao))
    if triet_tuan:
        extras.append("Án ngữ: " + ", ".join(triet_tuan))
    if extras:
        luan1 += " (" + " · ".join(extras) + ")."
    buoc.append(_buoc(
        "1. Cung Phu Thê (夫妻宫) — chính tinh + trạng thái + Hóa + cát/sát + đào hoa + Tuần/Triệt",
        ct or ["(vô chính diệu)"],
        {"chi": pt_branch, "chinh_tinh": ct, "trang_thai": tt, "tu_hoa": hoa,
         "sat_tinh": sat, "dao_hoa": dao, "tuan_triet": triet_tuan,
         "phu_tinh": pt_stars["phu"]},
        luan1, TRUC_TIEP,
        ["tuvi_phuthe.json:chinh_tinh_phu_the (王亭之 深造講義/tc7.txt)",
         "mieu_vuong_ham.json (Phú Thái Vi Q2 p0102)"],
    ))

    # ── BƯỚC 2 — Tam chiếu Phu Thê ↔ Phúc Đức ↔ Thiên Di ──────────────────────
    # Tam phương của Phu Thê: +4 và -4 cung index (tam hợp chi). Phu Thê index 2,
    # các cung tam hợp = Phúc Đức (10) và Thiên Di (6) theo PALACE_NAMES order.
    pd_idx = _palace_index(la_so, "Phúc Đức")
    td_idx = _palace_index(la_so, "Thiên Di")
    pd_s = _stars_at_index(la_so, pd_idx)
    td_s = _stars_at_index(la_so, td_idx)
    luan2 = (
        f"Tam phương hội chiếu Phu Thê: Phúc Đức ({BRANCHES_TVI[pd_idx % 12]}: "
        f"{', '.join(pd_s['chinh']) or 'VCD'}) chủ phúc-khí & quan-niệm tình cảm; "
        f"Thiên Di ({BRANCHES_TVI[td_idx % 12]}: {', '.join(td_s['chinh']) or 'VCD'}) "
        "chủ duyên gặp gỡ bên ngoài. Theo Trung Châu, không luận cung Phu Thê đơn lẻ "
        "mà phải xét cả tam phương — phúc khí dày + di cát thì cấu trúc duyên được nâng đỡ."
    )
    buoc.append(_buoc(
        "2. Tam phương hội chiếu — Phu Thê ↔ Phúc Đức ↔ Thiên Di",
        pd_s["chinh"] + td_s["chinh"],
        {"phuc_duc": {"chi": BRANCHES_TVI[pd_idx % 12], "chinh_tinh": pd_s["chinh"],
                      "sat": pd_s["sat"], "dao_hoa": pd_s["dao_hoa"]},
         "thien_di": {"chi": BRANCHES_TVI[td_idx % 12], "chinh_tinh": td_s["chinh"],
                      "sat": td_s["sat"], "dao_hoa": td_s["dao_hoa"]}},
        luan2, GIAN_TIEP,
        ["Trung Châu phái — 三方四正 (王亭之)",
         "an_sao.PALACE_NAMES (tam hợp chi)"],
    ))

    # ── BƯỚC 3 — Xung chiếu Phu Thê ↔ Quan Lộc ───────────────────────────────
    ql_idx = _palace_index(la_so, "Quan Lộc")  # = Phu Thê + 6 (đối xung)
    ql_s = _stars_at_index(la_so, ql_idx)
    ql_hoa = _hoa_at_index(la_so, ql_idx)
    wiki3 = _wiki_passage("Quan Lộc Phu Thê")
    luan3 = (
        f"Cung xung chiếu (đối cung) của Phu Thê = Quan Lộc tại "
        f"{BRANCHES_TVI[ql_idx % 12]} ({', '.join(ql_s['chinh']) or 'VCD'}). "
        "Sao đối cung 'chiếu' về Phu Thê: sự nghiệp & cách hành sự của bản thân/phối ngẫu "
        "định hình chất lượng tương tác hôn nhân. Quan Lộc có Hóa Kỵ/sát thì xung động "
        "tới Phu Thê — quan hệ dễ căng khi công việc trục trặc, cần giữ gìn ranh giới."
    ) if not ql_hoa else (
        f"Quan Lộc tại {BRANCHES_TVI[ql_idx % 12]} có Tứ Hóa "
        f"({', '.join(h['sao']+' '+h['hoa'] for h in ql_hoa)}) xung chiếu thẳng vào Phu Thê — "
        "biến động sự nghiệp phản chiếu trực tiếp vào hôn nhân; đọc động từ: năm khí Quan Lộc "
        "động cũng là năm cần chăm sóc quan hệ."
    )
    buoc.append(_buoc(
        "3. Xung chiếu (đối cung) — Phu Thê ↔ Quan Lộc",
        ql_s["chinh"],
        {"quan_loc": {"chi": BRANCHES_TVI[ql_idx % 12], "chinh_tinh": ql_s["chinh"],
                      "tu_hoa": ql_hoa, "sat": ql_s["sat"]},
         "wiki": wiki3},
        luan3, GIAN_TIEP,
        ["Trung Châu phái — đối cung xung chiếu"]
        + ([wiki3["_nguon"]] if wiki3 else []),
    ))

    # ── BƯỚC 4 — STUB cho so lá số đôi (để trống) ─────────────────────────────
    buoc.append(_buoc(
        "4. So đôi lá số (hợp hôn song phái) — STUB",
        [],
        {"trang_thai": "chua_co_la_so_doi",
         "huong_dan": "Gọi engine.cross_paradigm.hon_nhan_song_phai khi có lá số đối phương; "
                      "bước này để trống có chủ đích trong quy trình 1-lá-số."},
        "Bước này dành cho khi có lá số người thứ hai — đối chiếu cung Phu Thê hai bên, "
        "phối Mệnh-Thân, lục hợp/lục xung địa chi. Với 1 lá số đơn, để trống.",
        GIAN_TIEP,
        ["(stub — engine hợp hôn song phái xử lý riêng)"],
    ))

    # ── BƯỚC 5 — Đại vận → Phu Thê ────────────────────────────────────────────
    dv_pt = cung_phu_the_dai_van(la_so)
    canh_bao_dv = [c for dv in dv_pt for c in dv.get("canh_bao", [])]
    luan5 = (
        "Đại vận kéo cung Phu Thê dịch chuyển: mỗi vận 10 năm, cung Phu Thê đại-vận "
        "mang chính tinh khác → giai đoạn nào duyên được kích hoạt, giai đoạn nào cần giữ gìn. "
        + (f"Cảnh báo vận: {'; '.join(canh_bao_dv)}. "
           if canh_bao_dv else "Không có Hóa Kỵ trùng điệp tại Phu Thê đại vận. ")
        + "Đọc động từ: vận là KHÍ được kích hoạt, không phải án."
    )
    buoc.append(_buoc(
        "5. Đại vận (大运) → cung Phu Thê từng 10 năm",
        [s for dv in dv_pt for s in dv.get("phu_the_chinh_tinh", [])][:6],
        {"dai_van_phu_the": dv_pt},
        luan5, GIAN_TIEP,
        ["dai_van_luu_nien_phu_the.cung_phu_the_dai_van",
         "Trung Châu Tử Vi Đẩu Số 2 (王亭之) §5.3"],
    ))

    # ── BƯỚC 6 — Tiểu hạn & Lưu niên ──────────────────────────────────────────
    yr = as_of_year or 2024
    markers = luu_nien_phu_the_markers(la_so, year_range=(yr, yr + 10))
    th_anchor = la_so.get("tieu_han_anchor")
    luan6 = (
        f"Lưu niên (流年) {yr}-{yr+10}: theo dõi năm Hồng Loan/Thiên Hỉ bay đến Mệnh hoặc "
        "Phu Thê = ứng kỳ hỉ-sự (gặp duyên / kết hôn / sinh nở) NẾU chính diệu cát ổn. "
        + (f"Năm đáng chú ý: "
           + "; ".join(f"{m['year']}({m['year_branch']})" for m in markers) + ". "
           if markers else "Không có mốc Hồng Loan/Thiên Hỉ rõ trong khung này. ")
        + "Tiểu hạn an theo chi năm sinh, chồng lên lưu niên để định tháng. "
        "Mốc = 'năm khí được kích hoạt', không phải tiên tri."
    )
    buoc.append(_buoc(
        "6. Tiểu hạn & Lưu niên (流年) — định thời duyên/hôn",
        ["Hồng Loan", "Thiên Hỉ"],
        {"tieu_han_anchor": th_anchor,
         "tieu_han_anchor_chi": BRANCHES_TVI[th_anchor % 12] if th_anchor is not None else None,
         "luu_nien_markers": markers},
        luan6, TIEM_AN,
        ["dai_van_luu_nien_phu_the.luu_nien_phu_the_markers",
         "Trung Châu phái §3.1 (Hồng Loan/Thiên Hỉ ứng kỳ)"],
    ))

    # ── BƯỚC 7 — Tử Tức (con cái) ─────────────────────────────────────────────
    tt_idx = _palace_index(la_so, "Tử Tức")
    tt_s = _stars_at_index(la_so, tt_idx)
    tt_dao = tt_s["dao_hoa"]
    luan7 = (
        f"Cung Tử Tức tại {BRANCHES_TVI[tt_idx % 12]} ({', '.join(tt_s['chinh']) or 'VCD'}) "
        "phản chiếu duyên con cái + tầng thân-mật sâu của vợ chồng (cổ văn coi Tử Tức là "
        "cung 'tình dục/thân mật'). "
        + ("Có đào hoa (" + ", ".join(tt_dao) + ") — sắc thái tình cảm đậm, cần vận hành lành mạnh. "
           if tt_dao else "")
        + "Tham Lang/đào hoa tụ ở đây: cổ văn nói tình cảm nồng — đọc lại theo Vương Đình Chi "
        "là sức sống tình cảm, không kết án."
    )
    buoc.append(_buoc(
        "7. Cung Tử Tức (子女宫) — con cái & tầng thân mật",
        tt_s["chinh"],
        {"chi": BRANCHES_TVI[tt_idx % 12], "chinh_tinh": tt_s["chinh"],
         "dao_hoa": tt_dao, "sat": tt_s["sat"]},
        luan7, GIAN_TIEP,
        ["tuvi_phuthe.json:dao_hoa_tinh (天姚 Tử Tham — 情欲甚深, tc7.txt)"],
    ))

    # ── BƯỚC 8 — Điền Trạch ───────────────────────────────────────────────────
    dt_idx = _palace_index(la_so, "Điền Trạch")
    dt_s = _stars_at_index(la_so, dt_idx)
    dt_hoa = _hoa_at_index(la_so, dt_idx)
    luan8 = (
        f"Cung Điền Trạch tại {BRANCHES_TVI[dt_idx % 12]} ({', '.join(dt_s['chinh']) or 'VCD'}) "
        "= 'kho/nhà' — tổ ấm, nơi an cư của hôn nhân; cũng là cung lưu giữ tài sản chung. "
        + ("Vũ Khúc Hóa Kỵ tại Điền Trạch (theo kho) là tín hiệu cấu trúc tài-sản/tổ-ấm cần "
           "lưu tâm. " if any(h['sao'] == 'Vũ Khúc' and h['hoa'] == 'Kỵ' for h in dt_hoa) else "")
        + "Điền Trạch vững → hôn nhân có nền 'an cư'; đọc đồng dạng: nhà yên thì người yên."
    )
    buoc.append(_buoc(
        "8. Cung Điền Trạch (田宅宫) — tổ ấm & tài sản chung",
        dt_s["chinh"],
        {"chi": BRANCHES_TVI[dt_idx % 12], "chinh_tinh": dt_s["chinh"],
         "tu_hoa": dt_hoa, "sat": dt_s["sat"]},
        luan8, TIEM_AN,
        ["tuvi_phuthe.json:tu_hoa_phu_the (武曲化忌 Điền Trạch, tc7.txt)"],
    ))

    # ── BƯỚC 9 — Nô Bộc (NGƯỜI THỨ BA) ───────────────────────────────────────
    nb_idx = _palace_index(la_so, "Nô Bộc")
    nb_s = _stars_at_index(la_so, nb_idx)
    nb_dao = nb_s["dao_hoa"]
    nb_hoa = _hoa_at_index(la_so, nb_idx)
    luan9 = (
        f"Cung Nô Bộc tại {BRANCHES_TVI[nb_idx % 12]} ({', '.join(nb_s['chinh']) or 'VCD'}) "
        "= giao hữu / người ngoài — trong tình duyên đọc là khả năng có NGƯỜI THỨ BA / can dự "
        "từ bên ngoài. "
        + ("Đào hoa tại Nô Bộc (" + ", ".join(nb_dao) + ") + sát/Kỵ = cổ văn cảnh báo "
           "duyên ngoài luồng — đọc lại: cần ranh giới quan hệ rõ ràng, KHÔNG phán 'sẽ ngoại tình'. "
           if (nb_dao and (nb_s["sat"] or nb_hoa)) else
           "Không có cụm đào-hoa-trùng-sát ở đây → tín hiệu người-thứ-ba mờ. ")
        + "Mệnh là động từ: cấu trúc này nói cần chủ động giữ gìn ranh giới giao tế."
    )
    buoc.append(_buoc(
        "9. Cung Nô Bộc (奴仆宫) — NGƯỜI THỨ BA / can dự ngoài",
        nb_s["chinh"],
        {"chi": BRANCHES_TVI[nb_idx % 12], "chinh_tinh": nb_s["chinh"],
         "dao_hoa": nb_dao, "sat": nb_s["sat"], "tu_hoa": nb_hoa},
        luan9, TIEM_AN,
        ["tuvi_phuthe.json:dao_hoa_tinh:_cum_dao_hoa_kiep (đào hoa + sát-kỵ, tc7.txt)"],
    ))

    # ── BƯỚC 10 — Tật Ách ─────────────────────────────────────────────────────
    ta_idx = _palace_index(la_so, "Tật Ách")
    ta_s = _stars_at_index(la_so, ta_idx)
    ta_sat = ta_s["sat"]
    luan10 = (
        f"Cung Tật Ách tại {BRANCHES_TVI[ta_idx % 12]} ({', '.join(ta_s['chinh']) or 'VCD'}) "
        "= thân-tâm-bệnh, đọc thêm tầng cảm xúc & sức khỏe ảnh hưởng tới quan hệ. "
        + ("Sát tinh tại Tật Ách (" + ", ".join(ta_sat) + ") — căng thẳng thân-tâm dễ dội "
           "vào hôn nhân; chăm sóc sức khỏe = chăm sóc quan hệ. " if ta_sat else "")
        + "女命骨髓賦: 三方四正嫌逢杀 — sát hội thì lưu tâm SÂU, nhưng là 'cần giữ gìn', "
        "không phải định mệnh."
    )
    buoc.append(_buoc(
        "10. Cung Tật Ách (疾厄宫) — thân-tâm & cảm xúc",
        ta_s["chinh"],
        {"chi": BRANCHES_TVI[ta_idx % 12], "chinh_tinh": ta_s["chinh"], "sat": ta_sat},
        luan10, TIEM_AN,
        ["tuvi_phuthe.json:sat_tinh_phu_the (女命骨髓賦 三方四正嫌逢杀, tc7.txt)"],
    ))

    # ── BƯỚC 11 — Tài Bạch ────────────────────────────────────────────────────
    tb_idx = _palace_index(la_so, "Tài Bạch")
    tb_s = _stars_at_index(la_so, tb_idx)
    tb_hoa = _hoa_at_index(la_so, tb_idx)
    luan11 = (
        f"Cung Tài Bạch tại {BRANCHES_TVI[tb_idx % 12]} ({', '.join(tb_s['chinh']) or 'VCD'}) "
        "= tiền tài — kinh tế là nền vật chất của hôn nhân, mâu thuẫn tiền bạc là một trục "
        "căng phổ biến. "
        + ("Vũ Khúc Hóa Kỵ tại Tài Bạch (kho ghi 武曲化忌) → cấu trúc tài chính cần lưu tâm, "
           "dễ thành điểm va chạm vợ chồng. " if any(h['sao'] == 'Vũ Khúc' and h['hoa'] == 'Kỵ'
                                                    for h in tb_hoa) else "")
        + "Đọc đồng dạng: tài ổn thì một trục căng của hôn nhân được tháo."
    )
    buoc.append(_buoc(
        "11. Cung Tài Bạch (财帛宫) — kinh tế nền của hôn nhân",
        tb_s["chinh"],
        {"chi": BRANCHES_TVI[tb_idx % 12], "chinh_tinh": tb_s["chinh"],
         "tu_hoa": tb_hoa, "sat": tb_s["sat"]},
        luan11, TIEM_AN,
        ["tuvi_phuthe.json:tu_hoa_phu_the (武曲化忌 Tài Bạch, tc7.txt)"],
    ))

    # ── BƯỚC 12 — Mệnh ────────────────────────────────────────────────────────
    m_idx = la_so.get("menh_index")
    m_s = _stars_at_index(la_so, m_idx)
    m_tt = _trang_thai(m_s["chinh"], BRANCHES_TVI[m_idx % 12]) if m_idx is not None else []
    # cách cục tổng (đối chiếu dict Phú Thái Vi) — grounding cấp lá số
    stars_in_palaces = {
        p.get("name"): _stars_at_index(la_so, p.get("branch_index"))["chinh"]
        for p in la_so.get("palaces", [])
    }
    cach = cach_cuc_dict.match_cach_in_chart(
        stars_at_menh=m_s["chinh"], stars_in_palaces=stars_in_palaces,
        min_overlap=2, max_results=5,
    )
    cach_names = [c.get("ten") for c in cach if c.get("ten")]
    luan12 = (
        f"Cung Mệnh tại {BRANCHES_TVI[m_idx % 12]} ({', '.join(m_s['chinh']) or 'VCD'}"
        + (f"; {', '.join(x['sao']+' '+x['muc'] for x in m_tt)}" if m_tt else "")
        + ") là CHỦ THỂ — chính bản thân người nữ. Tử Vi đọc hôn nhân không tách rời Mệnh: "
        "tính cách, độ cương-nhu, cách yêu của chủ thể quyết định cách VẬN HÀNH duyên. "
        + ("Cách cục tổng nổi: " + ", ".join(cach_names) + ". " if cach_names else "")
        + "王亭之 biện chính: nữ cương liệt (Vũ Khúc…) thời nay thành tự lập, thành đạt "
        "(女命反易奋发) — Mệnh là động từ, không phải số phận đóng đinh."
    )
    buoc.append(_buoc(
        "12. Cung Mệnh (命宫) — chủ thể & cách cục tổng",
        m_s["chinh"],
        {"chi": BRANCHES_TVI[m_idx % 12], "chinh_tinh": m_s["chinh"],
         "trang_thai": m_tt, "menh_chu": la_so.get("menh_chu"),
         "than_chu": la_so.get("than_chu"), "cach_cuc": cach_names},
        luan12, GIAN_TIEP,
        ["cach_cuc_dict.match_cach_in_chart (Phú Thái Vi 545 cách)",
         "tuvi_phuthe.json (王亭之 女命反易奋发, tc7.txt)"],
    ))

    return {
        "method_id": METHOD_ID,
        "gender": gender,
        "paradigm": "đọc đồng dạng — mệnh là động từ (Iron Rule #4/#6/#8)",
        "disclaimer": _DISCLAIMER,
        "cung_phu_the_chi": pt_branch,
        "as_of_year": as_of_year,
        "buoc": buoc,
    }


# ─── Tiện ích: đọc thẳng từ giờ sinh ──────────────────────────────────────────
def doc_tuvi_12_buoc_from_birth(
    *, birth_datetime_local: str, timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nữ", as_of_year: Optional[int] = None,
    birth_longitude: Optional[float] = None, birth_province: Optional[str] = None,
) -> dict:
    """Cast lá số từ giờ sinh dương lịch rồi chạy 12 bước (one-shot helper)."""
    la_so = cast_la_so_from_birth(
        birth_datetime_local=birth_datetime_local, timezone=timezone, gender=gender,
        birth_longitude=birth_longitude, birth_province=birth_province,
    )
    out = doc_tuvi_12_buoc(la_so, gender=gender, as_of_year=as_of_year)
    out["la_so"] = la_so
    return out
