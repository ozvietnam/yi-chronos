"""Bộ phụ tinh + THẾ — luận phụ tinh theo cặp và theo vị trí với cung (2026-06-13).

Anh chốt: phụ tinh KHÔNG xem lẻ — phải xem theo BỘ (cặp sao đi với nhau) và
theo THẾ so với cung: đồng cung / giáp (kẹp 2 bên) / hội chiếu (tam hợp) /
xung chiếu (đối cung). Vd Mệnh có Lộc Tồn thì Kình-Đà LUÔN giáp 2 bên.

Tầng này chạy cho cả 12 cung, bồi vào luận giải + narrative.
"""
from __future__ import annotations

CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti",
            "ngo", "mui", "than", "dau", "tuat", "hoi"]

# Các BỘ phụ tinh chuẩn: slug → (sao A, sao B, tên hiển thị, loại)
BO_PHU_TINH = [
    ("ta_huu", "ta_phu", "huu_bat", "Tả Phụ – Hữu Bật", "cat"),
    ("xuong_khuc", "van_xuong", "van_khuc", "Văn Xương – Văn Khúc", "cat"),
    ("khoi_viet", "thien_khoi", "thien_viet", "Thiên Khôi – Thiên Việt", "cat"),
    ("kinh_da", "kinh_duong", "da_la", "Kình Dương – Đà La", "sat"),
    ("hoa_linh", "hoa_tinh", "linh_tinh", "Hỏa Tinh – Linh Tinh", "sat"),
    ("khong_kiep", "dia_khong", "dia_kiep", "Địa Không – Địa Kiếp", "sat"),
    ("loc_ma", "loc_ton", "thien_ma", "Lộc Tồn – Thiên Mã", "cat"),
    ("long_phuong", "long_tri", "phuong_cac", "Long Trì – Phượng Các", "cat"),
    ("khoc_hu", "thien_khoc", "thien_hu", "Thiên Khốc – Thiên Hư", "hung"),
    ("thai_cao", "thai_phu", "phong_cao", "Thai Phụ – Phong Cáo", "cat"),
    ("an_quy", "an_quang", "thien_quy", "Ân Quang – Thiên Quý", "cat"),
    ("thai_toa", "tam_thai", "bat_toa", "Tam Thai – Bát Tọa", "cat"),
    ("hong_hy", "hong_loan", "thien_hy", "Hồng Loan – Thiên Hỉ", "dao_hoa"),
    ("co_qua", "co_than", "qua_tu", "Cô Thần – Quả Tú", "hung"),
]

THE_VI = {
    "dong_cung": "đồng cung", "giap": "giáp (kẹp 2 bên)",
    "xung_chieu": "xung chiếu (đối cung)", "hoi_chieu": "hội chiếu (tam hợp)",
}
# Ưu tiên thế (mạnh → yếu): đồng cung > giáp > xung > hội
_THE_ORDER = {"dong_cung": 0, "giap": 1, "xung_chieu": 2, "hoi_chieu": 3}


def _chis_of(star: str, all_stars: dict[str, list[str]]) -> list[int]:
    return [i for i, chi in enumerate(CHI_RING) if star in (all_stars.get(chi) or [])]


def _the_of(star_idxs: list[int], target: int) -> str | None:
    """Thế của 1 sao (theo các chi nó đóng) so với cung target."""
    if not star_idxs:
        return None
    best = None
    for i in star_idxs:
        if i == target:
            return "dong_cung"  # mạnh nhất, trả ngay
        d = (i - target) % 12
        if d in (1, 11):
            cand = "giap"
        elif d == 6:
            cand = "xung_chieu"
        elif d in (4, 8):
            cand = "hoi_chieu"
        else:
            cand = None
        if cand and (best is None or _THE_ORDER[cand] < _THE_ORDER[best]):
            best = cand
    return best


def luan_bo_phu_tinh(target_chi: str, all_stars: dict[str, list[str]]) -> list[dict]:
    """Phát hiện các bộ phụ tinh có THẾ đáng kể với cung target_chi.

    all_stars: {chi: [sao canonical]} — gom mọi phụ tinh + vòng sao theo chi.
    Returns: list {slug, ten, loai, sao_co, the, the_vi, đủ_cặp} sắp theo độ mạnh.
    """
    if target_chi not in CHI_RING:
        return []
    target = CHI_RING.index(target_chi)
    out = []
    for slug, a, b, ten, loai in BO_PHU_TINH:
        ia, ib = _chis_of(a, all_stars), _chis_of(b, all_stars)
        ta, tb = _the_of(ia, target), _the_of(ib, target)
        # Lấy thế mạnh nhất trong 2 sao có liên hệ với cung
        cands = [t for t in (ta, tb) if t]
        if not cands:
            continue
        the = min(cands, key=lambda t: _THE_ORDER[t])
        sao_co = []
        if ta:
            sao_co.append(a)
        if tb:
            sao_co.append(b)
        out.append({
            "slug": slug, "ten": ten, "loai": loai,
            "the": the, "the_vi": THE_VI[the],
            "sao_co": sao_co, "du_cap": len(sao_co) == 2,
        })
    # Sắp: đủ cặp trước, rồi thế mạnh, rồi sát/hung (đáng lưu ý) trước
    out.sort(key=lambda x: (not x["du_cap"], _THE_ORDER[x["the"]],
                            0 if x["loai"] in ("sat", "hung") else 1))
    return out


def atoms_for_bo(sao_a: str, sao_b: str, limit_per_school: int = 1) -> dict:
    """Pull atoms nói về CẢ 2 sao của bộ (star tag chứa cả a lẫn b)."""
    import sqlite3
    from pathlib import Path
    from .cross_school import SCHOOL_MAP, _fetch_atom_details
    db = Path(__file__).resolve().parents[2] / "data" / "yi_wiki" / "wiki.sqlite3"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT a.atom_id, a.subject_identifiers, a.confidence, c.book_corpus_id
           FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id=a.chunk_id
           WHERE a.subject_identifiers LIKE ? AND a.subject_identifiers LIKE ?
             AND a.founder_verified >= 0 ORDER BY a.confidence DESC LIMIT 30""",
        (f"%{sao_a}%", f"%{sao_b}%"),
    ).fetchall()
    by_school: dict[str, list[int]] = {}
    for r in rows:
        sc = SCHOOL_MAP.get(r["book_corpus_id"])
        if sc and len(by_school.setdefault(sc, [])) < limit_per_school:
            by_school[sc].append(r["atom_id"])
    schools = {sc: _fetch_atom_details(conn, ids) for sc, ids in by_school.items()}
    conn.close()
    return {"schools": schools, "total_atoms": sum(len(v) for v in schools.values())}


def build_all_stars(la_so_input: dict) -> dict[str, list[str]]:
    """Gom chính tinh + phụ tinh + vòng sao theo chi (chỉ key 12 chi)."""
    all_stars: dict[str, list[str]] = {}
    for src in ("chinh_tinh_per_palace", "phu_tinh_per_palace", "vong_sao_per_palace"):
        for chi, stars in (la_so_input.get(src) or {}).items():
            if chi in CHI_RING:
                all_stars.setdefault(chi, []).extend(stars)
    return all_stars
