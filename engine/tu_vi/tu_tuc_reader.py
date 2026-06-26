"""Reader cung TỬ TỨC (con cái) — phương pháp nam-đẩu/bắc-đẩu cổ điển.

Anh duyệt 2026-06-26 (làm giàu engine kênh #3 Nguyệt Đồ, hướng AN TOÀN cổ điển):
GAP engine — chưa có reader cung Tử Tức chuyên sâu. Phương pháp dùng phân loại sao
NAM-ĐẨU / BẮC-ĐẨU (cổ điển Tử Vi) để đọc XU HƯỚNG con cái, chắt lọc cách trình bày
từ kênh Nguyệt Đồ Số Mệnh.

⚠️ Iron Rule: KHÔNG predict định mệnh. Tác giả kênh tự nhấn — và engine BẮT BUỘC kèm:
"lá số con chỉ ~30%, người hôn phối ~30%, nhân duyên của chính đứa trẻ ~40%". Mọi output
là XU HƯỚNG đọc-đồng-dạng, không phải bản án.

Input: la_so_input (từ la_so_input_builder.build_la_so_input) — cần chinh_tinh_per_palace,
phu_tinh_per_palace, vong_sao_per_palace, fn_to_chi, tuan_chi, triet_chi.
"""
from __future__ import annotations

# Phân loại CỔ ĐIỂN (Bắc Đẩu / Nam Đẩu tinh hệ)
NAM_DAU = {"thien_phu", "thien_tuong", "thien_luong", "that_sat",
           "thien_dong", "thai_duong", "thien_co"}          # → thiên con trai
BAC_DAU = {"thai_am", "tham_lang", "cu_mon", "liem_trinh",
           "vu_khuc", "pha_quan"}                            # → thiên con gái
# Tử Vi = trung thiên đế tinh → trung tính (không tính nghiêng)

CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti",
            "ngo", "mui", "than", "dau", "tuat", "hoi"]
# chi DƯƠNG = index chẵn (Tý Dần Thìn Ngọ Thân Tuất) → hơi thiên trai; ÂM → hơi thiên gái

KHOI_VIET = {"thien_khoi", "thien_viet"}                     # → hỗ trợ con trai
DAO_HONG = {"hong_loan", "dao_hoa", "dai_hao"}               # đào-hồng → hỗ trợ con gái

# Vòng Tràng Sinh thịnh → tăng số con; suy/tử → giảm
TS_THINH = {"ts_trang_sinh", "ts_lam_quan", "ts_de_vuong", "ts_quan_doi"}
TS_SUY = {"ts_suy", "ts_benh", "ts_tu", "ts_mo", "ts_tuyet"}
GIAM_CON = {"co_than", "qua_tu", "loc_ton", "dia_khong", "dia_kiep", "kiep_sat"}

VI_NAME = {
    "tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương",
    "vu_khuc": "Vũ Khúc", "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh",
    "thien_phu": "Thiên Phủ", "thai_am": "Thái Âm", "tham_lang": "Tham Lang",
    "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng", "thien_luong": "Thiên Lương",
    "that_sat": "Thất Sát", "pha_quan": "Phá Quân",
}

CAVEAT = ("Lá số con chỉ phản ánh ~30% — khoảng 30% nữa từ người hôn phối và ~40% từ "
          "nhân duyên của chính đứa trẻ. Đây là XU HƯỚNG để hiểu và chuẩn bị, KHÔNG phải định mệnh.")
NGUON = "Phương pháp nam-đẩu/bắc-đẩu (cổ điển Tử Vi) · cách trình bày chắt lọc từ kênh Nguyệt Đồ Số Mệnh"


def _stars_at(la_so_input: dict, cung: str, chi: str | None) -> set[str]:
    """Gộp sao tại cung Tử Tức theo CẢ key cung-tên lẫn key chi (engine lưu cả hai)."""
    out: set[str] = set()
    for src in ("chinh_tinh_per_palace", "phu_tinh_per_palace", "vong_sao_per_palace"):
        d = la_so_input.get(src) or {}
        for key in (cung, chi):
            if key and d.get(key):
                out.update(d[key])
    return out


def read_tu_tuc(la_so_input: dict) -> dict:
    """Đọc xu hướng cung Tử Tức. Trả {cung_chi, chinh_tinh, gioi_tinh_con, so_con, phuc_con, caveat, nguon}."""
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    chi = fn_to_chi.get("tu_tuc") if isinstance(fn_to_chi, dict) else None
    stars = _stars_at(la_so_input, "tu_tuc", chi)
    chinh = [s for s in ((la_so_input.get("chinh_tinh_per_palace") or {}).get("tu_tuc")
                         or (la_so_input.get("chinh_tinh_per_palace") or {}).get(chi) or [])]

    # ── 1. Giới tính con (xu hướng) ──
    diem_nam = sum(1 for s in chinh if s in NAM_DAU) + (1 if stars & KHOI_VIET else 0)
    diem_bac = sum(1 for s in chinh if s in BAC_DAU) + (1 if stars & DAO_HONG else 0)
    duong = chi in CHI_RING and CHI_RING.index(chi) % 2 == 0
    diem_nam += 0.5 if duong else 0
    diem_bac += 0.5 if (chi in CHI_RING and not duong) else 0
    if not chinh:  # vô chính diệu → mượn xu hướng cung dương/âm + sao phụ
        ly_do_vcd = "Cung Tử Tức vô chính diệu — xu hướng nhẹ theo cung "
    else:
        ly_do_vcd = ""
    if abs(diem_nam - diem_bac) < 0.6:
        xu_huong_gt = "cân bằng (khả năng có đủ cả trai lẫn gái)"
    elif diem_nam > diem_bac:
        xu_huong_gt = "hơi thiên con trai"
    else:
        xu_huong_gt = "hơi thiên con gái"
    nam_names = [VI_NAME.get(s, s) for s in chinh if s in NAM_DAU]
    bac_names = [VI_NAME.get(s, s) for s in chinh if s in BAC_DAU]
    ly_do_gt = ly_do_vcd + (
        f"{'+'.join(nam_names) or '—'} (nam-đẩu→trai) vs {'+'.join(bac_names) or '—'} (bắc-đẩu→gái)"
        f"; cung {chi or '?'} {'dương' if duong else 'âm'}"
        + ("; có Khôi/Việt (→trai)" if stars & KHOI_VIET else "")
        + ("; có đào-hồng (→gái)" if stars & DAO_HONG else ""))

    # ── 2. Số con (xu hướng) ──
    yeu_to = []
    score = 0
    if stars & TS_THINH:
        score += 1; yeu_to.append("vòng Tràng Sinh thịnh (Trường Sinh/Lâm Quan/Đế Vượng) → nhỉnh hơn")
    if stars & TS_SUY:
        score -= 0.5; yeu_to.append("vòng Tràng Sinh suy/bệnh → không nhiều")
    giam = stars & GIAM_CON
    if giam:
        score -= 1; yeu_to.append(f"có {', '.join(sorted(giam))} → khuynh hướng ít/khó")
    muon = chi in (la_so_input.get("tuan_chi") or []) or chi in (la_so_input.get("triet_chi") or [])
    if muon:
        yeu_to.append("Tuần/Triệt án cung → con đến muộn (không phải vô sinh)")
    xu_huong_sc = ("nhỉnh hơn trung bình" if score >= 1 else
                   "thiên ít / cần vun đắp" if score <= -1 else "trung bình (quanh 2)")

    # ── 3. Phúc con ──
    phuc = "thien_dong" in chinh
    phuc_mo_ta = ("Thiên Đồng (phúc tinh) tọa Tử Tức → giai đoạn sinh con thường kèm vận khí "
                  "hanh thông lên (theo giai đoạn, không kéo dài mãi)." if phuc else None)

    return {
        "cung_chi": chi,
        "chinh_tinh": [VI_NAME.get(s, s) for s in chinh] or ["Vô chính diệu"],
        "gioi_tinh_con": {"xu_huong": xu_huong_gt, "ly_do": ly_do_gt,
                          "diem_nam": round(diem_nam, 1), "diem_bac": round(diem_bac, 1)},
        "so_con": {"xu_huong": xu_huong_sc, "yeu_to": yeu_to or ["không có dấu hiệu đặc biệt → quanh mức trung bình"]},
        "phuc_con": {"co": phuc, "mo_ta": phuc_mo_ta},
        "caveat": CAVEAT,
        "nguon": NGUON,
    }
