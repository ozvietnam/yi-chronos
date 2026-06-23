"""Kiểm chứng bằng máy các ĐỊNH LÝ DẪN XUẤT của Đằng Sơn — kế thừa, tiếp tục công trình.

Đằng Sơn (《Tử Vi Hoàn Toàn Khoa Học》 Q1, kế thừa Tạ Phồn Trị) dựng tử vi như một
chuỗi định lý BẰNG TAY. Module này lấy engine kiểm các định lý ấy trên dữ liệu
canonical (data/tu_vi/chinh_tinh.json + mieu_vuong_ham.json). Tinh thần khoa học:
luật phải TÁI TẠO được dữ liệu — chỗ nào khép kín, chỗ nào hở, báo cáo trung thực.

Định lý kiểm:
- Tam hợp = vòng ngũ-hành-SINH (tr.200)
- Độ sáng = giai đoạn Trường Sinh của hành sao tại cung (tr.243)
- Bảo toàn âm-dương tổng = 0 (tr.172) — báo cáo giới hạn dữ liệu, không ép
"""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

_DATA = Path(__file__).resolve().parents[2] / "data" / "tu_vi"

# Vòng tương SINH + KHẮC ngũ hành (Đằng Sơn Chương 8 tr.80)
NGU_HANH_SINH = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
NGU_HANH_KHAC = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}

# Ngũ hành 12 chi (Đằng Sơn tr.82 "Lý ngũ hành của thập nhị địa chi")
CHI_HANH = {"Tý": "thủy", "Sửu": "thổ", "Dần": "mộc", "Mão": "mộc", "Thìn": "thổ",
            "Tỵ": "hỏa", "Ngọ": "hỏa", "Mùi": "thổ", "Thân": "kim", "Dậu": "kim",
            "Tuất": "thổ", "Hợi": "thủy"}

# id sao → tên hiển thị (bảng độ sáng dùng tên hiển thị)
_STAR_DISPLAY = {
    "tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương",
    "vu_khuc": "Vũ Khúc", "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh",
    "thien_phu": "Thiên Phủ", "thai_am": "Thái Âm", "tham_lang": "Tham Lang",
    "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng", "thien_luong": "Thiên Lương",
    "that_sat": "Thất Sát", "pha_quan": "Phá Quân",
}

# 12 chi theo thứ tự địa bàn
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# 12 giai đoạn Trường Sinh (thuận)
TRUONG_SINH_STAGES = [
    "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy",
    "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng",
]
# Cung khởi Trường Sinh theo hành — Đằng Sơn gom Hỏa-Thổ cùng vòng (tr.243)
_TS_START = {"hỏa": "Dần", "thổ": "Dần", "kim": "Tỵ", "thủy": "Thân", "mộc": "Hợi"}
# Sức từng giai đoạn (Đế Vượng đỉnh → Tuyệt đáy) — đường đời sinh-vượng-tử-tuyệt
_STAGE_STRENGTH = {
    "Trường Sinh": 3, "Mộc Dục": 0, "Quan Đới": 2, "Lâm Quan": 4, "Đế Vượng": 5,
    "Suy": -1, "Bệnh": -2, "Tử": -3, "Mộ": -2, "Tuyệt": -4, "Thai": -1, "Dưỡng": 1,
}


def _primary_hanh(s: str) -> str:
    """Sao đa hành ('mộc / thủy') → hành chủ (đầu)."""
    return s.split("/")[0].strip()


def _load_stars():
    d = json.loads((_DATA / "chinh_tinh.json").read_text(encoding="utf-8"))
    out = {}
    for s in d["stars"]:
        sid = s.get("id") or s.get("ten") or s.get("name")
        out[sid] = {
            "hanh": _primary_hanh(s.get("ngu_hanh", "")),
            "am_duong": s.get("am_duong"),
            "display": _STAR_DISPLAY.get(sid, sid),
        }
    return out


STARS = _load_stars()


def is_sinh_chain(hanh_list) -> bool:
    """Danh sách hành có theo thứ tự tương sinh liên tiếp không?"""
    return all(NGU_HANH_SINH.get(hanh_list[i]) == hanh_list[i + 1]
               for i in range(len(hanh_list) - 1))


def _find_sinh_order(star_ids):
    for perm in permutations(star_ids):
        hanh = [STARS[s]["hanh"] for s in perm]
        if is_sinh_chain(hanh):
            return list(perm), hanh
    return None, None


# Hai bộ tam hợp Đằng Sơn nêu đích danh (tr.200)
_TAM_HOP = {
    "Tử-Vũ-Liêm": ["tu_vi", "vu_khuc", "liem_trinh"],
    "Sát-Phá-Tham": ["that_sat", "pha_quan", "tham_lang"],
}


def verify_tam_hop():
    out = {}
    for name, ids in _TAM_HOP.items():
        order, hanh = _find_sinh_order(ids)
        out[name] = {
            "stars": ids,
            "hanh": [STARS[s]["hanh"] for s in ids],
            "is_sinh_chain": order is not None,
            "sinh_order": order,
            "sinh_order_hanh": hanh,
        }
    return out


def truong_sinh_stage(hanh: str, cung: str) -> str:
    off = (CHI.index(cung) - CHI.index(_TS_START[hanh])) % 12
    return TRUONG_SINH_STAGES[off]


def _corr(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs) ** 0.5
    vy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


def verify_brightness():
    """Độ sáng canonical có tương quan với sức Trường Sinh của hành sao tại cung không?"""
    m = json.loads((_DATA / "mieu_vuong_ham.json").read_text(encoding="utf-8"))
    scores = {k: v["score"] for k, v in m["levels"].items()}
    table = m["table"]
    xs, ys, mism = [], [], []
    for info in STARS.values():
        disp = info["display"]
        if disp not in table:
            continue
        for cung, level in table[disp].items():
            if level not in scores:
                continue
            stage = truong_sinh_stage(info["hanh"], cung)
            xs.append(_STAGE_STRENGTH[stage])
            ys.append(scores[level])
    return {"n_pairs": len(xs), "correlation": round(_corr(xs, ys), 4)}


def ngu_hanh_relation(star_hanh: str, chi_hanh: str) -> str:
    """Quan hệ ngũ hành của CUNG (chi) đối với SAO — theo Chương 8 Đằng Sơn."""
    if star_hanh == chi_hanh:
        return "đồng hành"
    if NGU_HANH_SINH.get(chi_hanh) == star_hanh:
        return "cung sinh sao"            # cung dưỡng sao → mạnh
    if NGU_HANH_SINH.get(star_hanh) == chi_hanh:
        return "sao sinh cung"            # sao bị tiết khí → yếu
    if NGU_HANH_KHAC.get(chi_hanh) == star_hanh:
        return "cung khắc sao"            # sao bị chế → yếu nhất
    if NGU_HANH_KHAC.get(star_hanh) == chi_hanh:
        return "sao khắc cung"            # sao chế cung → trung tính
    return "?"


_REL_STRENGTH = {"đồng hành": 2, "cung sinh sao": 2, "sao khắc cung": 0,
                 "sao sinh cung": -1, "cung khắc sao": -2}


def verify_brightness_relation():
    """Mô hình ngũ-hành-quan-hệ (Ch.8): độ sáng theo sinh-khắc sao↔chi.
    Vòng 2 cho thấy mô hình này (r≈0.20) > Trường Sinh (r≈0.18), và độ sáng trung
    bình mỗi nhóm xếp ĐÚNG hướng — nhưng vẫn yếu: bảng miếu-hãm giữ nội dung
    truyền-thống bất-khả-suy ngoài luật ngũ hành thuần.

    📖 BẢN FULL xác nhận (Đằng Sơn Tập 1 tr.18, đọc 2026-06-23): "ngũ hành là một
    phép tính GẦN ĐÚNG của bài toán âm dương" (ngũ giác ≈ vòng tròn). → r≈0.20 yếu
    KHÔNG phải engine sai, mà vì CHÍNH ngũ-hành là xấp xỉ ⇒ độ sáng vốn bất-khả-khít.
    Lời sách ↔ kết quả máy khép vòng.
    """
    from collections import defaultdict
    m = json.loads((_DATA / "mieu_vuong_ham.json").read_text(encoding="utf-8"))
    scores = {k: v["score"] for k, v in m["levels"].items()}
    table = m["table"]
    buck, xs, ys = defaultdict(list), [], []
    for info in STARS.values():
        disp = info["display"]
        if disp not in table:
            continue
        for cung, level in table[disp].items():
            if level not in scores:
                continue
            rel = ngu_hanh_relation(info["hanh"], CHI_HANH[cung])
            buck[rel].append(scores[level])
            xs.append(_REL_STRENGTH[rel])
            ys.append(scores[level])
    means = {r: round(sum(v) / len(v), 3) for r, v in buck.items()}
    return {"n_pairs": len(xs), "correlation": round(_corr(xs, ys), 4), "group_means": means}


def verify_conservation():
    """Bảo toàn tổng âm-dương=0 (tr.172) — báo cáo trung thực với dữ liệu sẵn có."""
    duong = [s for s, i in STARS.items() if i["am_duong"] == "dương"]
    am = [s for s, i in STARS.items() if i["am_duong"] == "âm"]
    return {
        "n_duong": len(duong), "n_am": len(am),
        "balanced_raw": len(duong) == len(am),
        "note": ("Âm-dương TRUYỀN THỐNG %d dương / %d âm — chưa cân. Đằng Sơn (tr.120) "
                 "dùng âm-dương theo CỘNG HƯỞNG (trái nghịch=âm, tương đồng=dương), khác "
                 "bảng truyền thống → phải trích bộ giá trị ấy mới kiểm định luật =0."
                 % (len(duong), len(am))),
    }


# Hai chùm sao (lấy từ engine an_sao.place_14_chinh_tinh — nguồn thật, không tự nhận)
TU_VI_CHUM = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh"]
PHU_CHUM = ["Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng",
            "Thiên Lương", "Thất Sát", "Phá Quân"]
CAN_DUONG = ["Giáp", "Bính", "Mậu", "Canh", "Nhâm"]
CAN_AM = ["Ất", "Đinh", "Kỷ", "Tân", "Quý"]


def verify_hoa_ky_structure():
    """Định lý Hóa Kỵ (tr.170-172): Tứ Hóa Kỵ KHÔNG tùy tiện — suy từ cấu trúc chùm.

    - 5 can DƯƠNG: Hóa Kỵ = đúng chùm Tử Vi BỎ Tử Vi ("bỏ Tử Vi ra ngoài thì được
      5 sao hóa y hệt tài liệu hiện hành", tr.170).
    - 5 can ÂM: chính tinh chùm Phủ không đủ → hệ kéo PHỤ TINH Văn Xương/Văn Khúc vào.
      Dấu vết định luật bảo toàn ③: "Âm Kỵ là lý do hiện hữu của Xương Khúc" (tr.172).
    """
    from engine.tu_vi.an_sao import TU_HOA_TABLE
    duong_ky = {TU_HOA_TABLE[c]["Kỵ"] for c in CAN_DUONG}
    am_ky = [TU_HOA_TABLE[c]["Kỵ"] for c in CAN_AM]
    return {
        "duong_ky": sorted(duong_ky),
        "duong_match_tu_vi_chum_minus_tuvi": duong_ky == (set(TU_VI_CHUM) - {"Tử Vi"}),
        "am_ky": am_ky,
        "am_phu_chum_stars": [s for s in am_ky if s in PHU_CHUM],
        "am_auxiliary_stars": [s for s in am_ky
                               if s not in TU_VI_CHUM and s not in PHU_CHUM],
    }


# Phụ tinh Tứ Hóa + âm-dương cặp kinh điển (Xương dương/Khúc âm, Tả dương/Hữu âm)
_AUX_AD = {"Văn Xương": "dương", "Văn Khúc": "âm", "Tả Phù": "dương", "Hữu Bật": "âm"}


def verify_tu_hoa_balance():
    """Định luật bảo toàn ③ (tr.172) — test trực tiếp âm-dương toàn bảng Tứ Hóa.

    V4: tổng KHÔNG cân theo âm-dương TRUYỀN THỐNG (15 dương / 25 âm) → ③ không phải
    số học âm-dương ngây thơ (Đằng Sơn dùng resonance, tr.120). NHƯNG phụ tinh
    Xương/Khúc/Tả/Hữu tự cân 3/3 → ③ đúng ở dạng CẤU TRÚC: phụ tinh là bộ cân-bằng
    zero-sum (khớp Vòng 3 — phụ tinh hiện đúng nơi hệ cần đóng).
    """
    from engine.tu_vi.an_sao import TU_HOA_TABLE
    ad = {STARS[s]["display"]: STARS[s]["am_duong"] for s in STARS}
    ad.update(_AUX_AD)
    per_hoa, tot_d, tot_a, aux_d, aux_a = {}, 0, 0, 0, 0
    for hoa in ("Lộc", "Quyền", "Khoa", "Kỵ"):
        stars = [TU_HOA_TABLE[c][hoa] for c in TU_HOA_TABLE]
        d = sum(1 for s in stars if ad.get(s) == "dương")
        a = sum(1 for s in stars if ad.get(s) == "âm")
        per_hoa[hoa] = {"duong": d, "am": a}
        tot_d, tot_a = tot_d + d, tot_a + a
        for s in stars:
            if s in _AUX_AD:
                aux_d += _AUX_AD[s] == "dương"
                aux_a += _AUX_AD[s] == "âm"
    return {
        "per_hoa": per_hoa,
        "total_duong": tot_d, "total_am": tot_a,
        "naive_balanced": tot_d == tot_a,
        "aux_duong": aux_d, "aux_am": aux_a,
        "aux_balanced": aux_d == aux_a,
    }


# Đường đi chủ Lộc/Quyền (Ch.14 tr.163-165, kế thừa Tạ Phồn Trị): 11 sao.
# Lộc(can) = walk[start]; Quyền(can) = walk[start+1] — Quyền luôn KỀ Lộc.
LOC_QUYEN_WALK = ["Liêm Trinh", "Phá Quân", "Cự Môn", "Thái Dương", "Vũ Khúc",
                  "Tham Lang", "Thái Âm", "Thiên Đồng", "Thiên Cơ", "Thiên Lương", "Tử Vi"]
_CAN_START = {"Giáp": 0, "Quý": 1, "Tân": 2, "Canh": 3, "Kỷ": 4,
              "Mậu": 5, "Đinh": 6, "Bính": 7, "Ất": 8, "Nhâm": 9}


def verify_loc_quyen_walk():
    """Định lý Lộc/Quyền (Ch.14): toàn bộ 20 ô Hóa Lộc + Hóa Quyền của 10 can đọc ra
    từ MỘT đường đi 11 sao — Lộc(can)=walk[start(can)], Quyền(can)=walk[start+1].
    Quyền luôn KỀ Lộc (bước +1). Phần Tứ Hóa tưởng học-thuộc nhất → dẫn xuất từ 1 cấu trúc.
    """
    from engine.tu_vi.an_sao import TU_HOA_TABLE
    loc_ok = quyen_ok = 0
    for can, start in _CAN_START.items():
        if LOC_QUYEN_WALK[start] == TU_HOA_TABLE[can]["Lộc"]:
            loc_ok += 1
        if LOC_QUYEN_WALK[start + 1] == TU_HOA_TABLE[can]["Quyền"]:
            quyen_ok += 1
    return {"n_can": len(_CAN_START), "loc_match": loc_ok, "quyen_match": quyen_ok,
            "perfect": loc_ok == quyen_ok == len(_CAN_START)}


def verify_star_hoa_participation():
    """Định lý Ch.17 (tr.191-196): TÍNH của sao đọc từ việc nó THAM GIA Tứ Hóa ra sao.
    - Phủ/Tướng/Sát: hoàn toàn KHÔNG hóa (bị động, xung-chiếu vĩnh viễn).
    - Cơ/Nguyệt(Thái Âm)/Vũ: hóa ĐỦ 4/4 (chủ động, đa năng).
    - Tử Vi/Thiên Lương: không hóa Kỵ.
    """
    from engine.tu_vi.an_sao import TU_HOA_TABLE
    appear = {}
    for hoas in TU_HOA_TABLE.values():
        for hoa, star in hoas.items():
            appear.setdefault(star, set()).add(hoa)
    g = lambda s: appear.get(s, set())
    never_hoa = [s for s in ("Thiên Phủ", "Thiên Tướng", "Thất Sát") if not g(s)]
    full_hoa = [s for s in ("Thiên Cơ", "Thái Âm", "Vũ Khúc") if len(g(s)) == 4]
    never_ky = [s for s in ("Tử Vi", "Thiên Lương") if "Kỵ" not in g(s)]
    return {
        "never_hoa": never_hoa, "full_hoa": full_hoa, "never_ky": never_ky,
        "phu_tuong_sat_never_hoa": len(never_hoa) == 3,
        "co_nguyet_vu_full_hoa": len(full_hoa) == 3,
    }


# Ch.20 (tr.270-276): TÍNH BÁT QUÁI của 14 chính tinh. 8 sao mang 1 quái; ngũ hành quái
# khớp ngũ hành sao (đã dẫn xuất độc lập) — bằng chứng mapping CÓ NGUYÊN LÝ. Ngoại lệ DUY
# NHẤT: Thiên Đồng (Đoài/kim mà Đồng thủy — gán Đoài vì Đoài "con gái út vui vẻ" không hợp
# Sát hung dữ, tr.271-272). 6 sao VÔ-QUÁI: Phủ Tướng Sát Âm Dương Cự (14 = 8 + 6).
QUAI_HANH = {"Càn": "kim", "Khảm": "thủy", "Cấn": "thổ", "Chấn": "mộc",
             "Tốn": "mộc", "Li": "hỏa", "Khôn": "thổ", "Đoài": "kim"}
BAT_QUAI_STAR = {"Vũ Khúc": "Càn", "Phá Quân": "Khảm", "Tử Vi": "Cấn", "Thiên Cơ": "Chấn",
                 "Tham Lang": "Tốn", "Liêm Trinh": "Li", "Thiên Lương": "Khôn",
                 "Thiên Đồng": "Đoài"}
NO_QUAI_STARS = ["Thiên Phủ", "Thiên Tướng", "Thất Sát", "Thái Âm", "Thái Dương", "Cự Môn"]


def verify_bat_quai_ngu_hanh():
    """Định lý Ch.20 (tr.270-276): mapping 8 chính tinh → 8 quái NHẤT QUÁN với ngũ hành sao
    (dẫn xuất độc lập ở chinh_tinh.json). Khớp 7/8; Thiên Đồng là ngoại lệ Đằng Sơn TỰ NÊU.
    14 chính tinh = 8 (có quái) + 6 (vô quái), không trùng, phủ trọn.
    """
    disp2hanh = {v["display"]: v["hanh"] for v in STARS.values()}
    matches, mismatches = [], []
    for star, quai in BAT_QUAI_STAR.items():
        if QUAI_HANH[quai] == disp2hanh.get(star):
            matches.append(star)
        else:
            mismatches.append(star)
    covers_all = sorted(list(BAT_QUAI_STAR) + NO_QUAI_STARS) == sorted(disp2hanh)
    return {
        "n_quai_stars": len(BAT_QUAI_STAR),
        "n_match": len(matches),
        "matches": matches,
        "mismatches": mismatches,
        "covers_all_14": covers_all,
    }


def verify_loc_ton_kinh_da():
    """Định lý Lộc Tồn (Tập 2 Ch.6) + Kình Đà (Tập 2 Ch.7) — kế thừa, kiểm bằng máy.

    Ch.6: Lộc Tồn an theo CAN năm = MÙA (Giáp Ất→Dần Mão xuân, Bính Đinh Mậu Kỷ→Tỵ Ngọ
    hạ, Canh Tân→Thân Dậu thu, Nhâm Quý→Hợi Tý đông). Vì gom đủ 4 mùa = "kết hợp khít khao
    Lộc-Quyền-Khoa-Kỵ" = hành Thổ trung ương → Lộc Tồn KHÔNG BAO GIỜ ở tứ mộ Thìn Tuất Sửu Mùi.
    Ch.7: "tiền Kình hậu Đà" — Kình Dương = Lộc+1 (đến quá sớm, ứng dương), Đà La = Lộc−1
    (đến quá trễ, ứng âm). Kiểm trên engine an_sao canonical (loc_ton/kinh_duong/da_la), trọn 10 can.
    """
    from engine.tu_vi import an_sao as _a

    B = _a.BRANCHES_TVI
    TU_MO = {"Thìn", "Tuất", "Sửu", "Mùi"}
    SEASON = {"Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Đinh": "Ngọ", "Mậu": "Tỵ",
              "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu", "Nhâm": "Hợi", "Quý": "Tý"}
    flank, avoid_mo, season = [], [], []
    for s in _a.STEMS_TVI:
        lt, kd, dl = _a.loc_ton(s), _a.kinh_duong(s), _a.da_la(s)
        if kd == (lt + 1) % 12 and dl == (lt - 1) % 12:
            flank.append(s)
        if B[lt] not in TU_MO:
            avoid_mo.append(s)
        if B[lt] == SEASON[s]:
            season.append(s)
    n = len(_a.STEMS_TVI)
    return {
        "n_stems": n,
        "tien_kinh_hau_da": len(flank),
        "loc_ton_avoids_tu_mo": len(avoid_mo),
        "loc_ton_matches_season": len(season),
        "all_pass": len(flank) == len(avoid_mo) == len(season) == n,
    }


def verify_luu_ha_school():
    """Định lý Lưu Hà (Tập 2 Ch.10) — Iron #3 đa phái, kiểm engine đứng phái nào.

    Lưu Hà an theo CAN năm. Đằng Sơn BẢO VỆ phái NGŨ-HÀNH-THUẦN (bài thiệu / Mệnh Lý Sách Ẩn):
    Đinh→Thân, Canh→Thìn. Thái Thứ Lang (Tử Vi Đẩu Số Tân Biên) ĐẢO CHỖ Đinh↔Canh
    (Đinh→Thìn, Canh→Thân) — Đằng Sơn cho là lỗi. Kiểm `sao_q3.luu_ha` (engine canonical) theo phái nào.
    Founder Mậu → Lưu Hà ở Tỵ = đồng cung Lộc Tồn = Mệnh (Mậu/Kỷ/Canh/Nhâm có Lưu Hà ≡ Lộc Tồn).
    """
    from engine.tu_vi import sao_q3, an_sao as _a

    B = _a.BRANCHES_TVI
    NGU_HANH_THUAN = {"Giáp": "Dậu", "Ất": "Tuất", "Bính": "Mùi", "Đinh": "Thân", "Mậu": "Tỵ",
                      "Kỷ": "Ngọ", "Canh": "Thìn", "Tân": "Mão", "Nhâm": "Hợi", "Quý": "Tý"}
    THAI_THU_LANG = {**NGU_HANH_THUAN, "Đinh": "Thìn", "Canh": "Thân"}  # đảo Đinh↔Canh
    engine_tbl = {s: B[sao_q3.luu_ha(s)] for s in _a.STEMS_TVI}
    match_nh = [s for s in _a.STEMS_TVI if engine_tbl[s] == NGU_HANH_THUAN[s]]
    differ_ttl = [s for s in _a.STEMS_TVI if engine_tbl[s] != THAI_THU_LANG[s]]
    n = len(_a.STEMS_TVI)
    return {
        "n_stems": n,
        "match_ngu_hanh_thuan": len(match_nh),
        "follows_dang_son_school": len(match_nh) == n,
        "differs_from_thai_thu_lang_at": sorted(differ_ttl),
        "mau_luu_ha": engine_tbl["Mậu"],
    }


def verify_khoi_viet_school():
    """Định lý Khôi Việt (Tập 2 Ch.11-12) — Iron #3 đa phái, kiểm engine đứng phái nào.

    Khôi Việt = Lục Cát (cùng Tả Hữu Xương Khúc), gốc thần sát THIÊN ẤT QUÝ NHÂN (an theo can năm,
    cứu chính tinh cực hãm hóa Kỵ). Đằng Sơn theo BÀI THIỆU TRUYỀN THỐNG: Giáp Mậu Canh→Sửu Mùi,
    Ất Kỷ→Tý Thân, Bính Đinh→Hợi Dậu, Nhâm Quý→Mão Tỵ, Tân→Ngọ Dần. Tranh chấp: phái "đổi mới"
    cho Canh=Ngọ Dần (giống Tân); Tạ Phồn Trị cho Kỷ=Dần Ngọ. Kiểm `an_sao.thien_khoi_viet` theo phái nào.
    Founder Mậu → Khôi Việt Sửu/Mùi = trục Tài Bạch ↔ Phúc Đức ("tọa quý hướng quý").
    """
    from engine.tu_vi import an_sao as _a

    B = _a.BRANCHES_TVI
    TRADITIONAL = {"Giáp": {"Sửu", "Mùi"}, "Mậu": {"Sửu", "Mùi"}, "Canh": {"Sửu", "Mùi"},
                   "Ất": {"Tý", "Thân"}, "Kỷ": {"Tý", "Thân"},
                   "Bính": {"Hợi", "Dậu"}, "Đinh": {"Hợi", "Dậu"},
                   "Nhâm": {"Mão", "Tỵ"}, "Quý": {"Mão", "Tỵ"}, "Tân": {"Ngọ", "Dần"}}
    engine_tbl = {s: {B[i] for i in _a.thien_khoi_viet(s)} for s in _a.STEMS_TVI}
    match = [s for s in _a.STEMS_TVI if engine_tbl[s] == TRADITIONAL[s]]
    n = len(_a.STEMS_TVI)
    return {
        "n_stems": n,
        "match_traditional": len(match),
        "follows_dang_son_school": len(match) == n,
        "canh_traditional_suu_mui": engine_tbl["Canh"] == {"Sửu", "Mùi"},
        "ky_traditional_than_ty": engine_tbl["Kỷ"] == {"Tý", "Thân"},
        "mau_khoi_viet": sorted(engine_tbl["Mậu"]),
    }


def verify_dao_ma_cai_sat():
    """Định lý Đào-Mã-Cái-Sát (Tập 2 Ch.17) — an theo CHI năm, suy từ vòng Trường Sinh ngũ hành.

    Đằng Sơn (chú thích 3-4): Tử Vi dùng thuyết "ĐỒNG SINH CỘNG TỬ" (mộc TS Hợi, hỏa+thổ TS Dần,
    kim TS Tỵ, thủy TS Thân; THUẬN cho cả âm-dương — KHÔNG dùng "âm sinh dương tử"). Trung Châu phái HK
    chỉ giữ 4 trong 12 vị trí: Đào Hoa(Hàm Trì)=Mộc Dục(+1), Thiên Mã=Bệnh(+6), Hoa Cái=Mộ(+8),
    Kiếp Sát=Tuyệt(+9). Cặp Đào-Sát ("đoan/xấu") vĩnh viễn TAM HỢP. Kiểm engine (ham_tri / sao_q3.thien_ma
    / vòng Tướng Tinh) có tái tạo đúng phái này cho trọn 12 chi năm.
    Founder năm Thìn (Thân Tý Thìn, thủy) → Kiếp Sát ở Tỵ = đồng cung Mệnh.
    """
    from engine.tu_vi import an_sao as _a, sao_q3

    branches = list(_a.BRANCHES_TVI)             # tuple int→name
    NB = {name: i for i, name in enumerate(branches)}   # name→index
    # Trường Sinh head theo tam hợp chi năm (đồng sinh cộng tử, thuận)
    TS_HEAD = {
        "Dần": NB["Dần"], "Ngọ": NB["Dần"], "Tuất": NB["Dần"],      # hỏa+thổ → TS Dần
        "Thân": NB["Thân"], "Tý": NB["Thân"], "Thìn": NB["Thân"],   # thủy   → TS Thân
        "Tỵ": NB["Tỵ"], "Dậu": NB["Tỵ"], "Sửu": NB["Tỵ"],           # kim    → TS Tỵ
        "Hợi": NB["Hợi"], "Mão": NB["Hợi"], "Mùi": NB["Hợi"],       # mộc    → TS Hợi
    }
    dao_ok = ma_ok = cai_ok = sat_ok = dao_sat_th = 0
    for yb in branches:
        ts = TS_HEAD[yb]
        exp_dao = (ts + 1) % 12   # Mộc Dục
        exp_ma = (ts + 6) % 12    # Bệnh
        exp_cai = (ts + 8) % 12   # Mộ
        exp_sat = (ts + 9) % 12   # Tuyệt
        tt = sao_q3.tuong_tinh_belt(yb)
        if _a.ham_tri(yb) == exp_dao:
            dao_ok += 1
        if sao_q3.thien_ma(yb) == exp_ma:
            ma_ok += 1
        if tt["Hoa Cái"] == exp_cai:
            cai_ok += 1
        if tt["Kiếp Sát"] == exp_sat:
            sat_ok += 1
        if (_a.ham_tri(yb) - tt["Kiếp Sát"]) % 12 in (4, 8):   # Đào-Sát tam hợp
            dao_sat_th += 1
    n = len(branches)
    return {
        "n_branches": n,
        "dao_hoa_is_moc_duc": dao_ok,
        "thien_ma_is_benh": ma_ok,
        "hoa_cai_is_mo": cai_ok,
        "kiep_sat_is_tuyet": sat_ok,
        "follows_dong_sinh_cong_tu": dao_ok == ma_ok == cai_ok == sat_ok == n,
        "dao_sat_tam_hop": dao_sat_th,
        "founder_kiep_sat_branch": branches[sao_q3.tuong_tinh_belt("Thìn")["Kiếp Sát"]],
    }


def verify_tu_mo_tu_duong():
    """Định lý tu-dưỡng TỨ MỘ (Tập 2 Ch.19 p222-223) — chữ ký tính toán của "tuổi tứ mộ dễ tu tâm
    dưỡng tính hơn các tuổi khác".

    TUỔI TỨ MỘ (Thìn Tuất Sửu Mùi): Thiên Không + Thiếu Dương + Kiếp Sát + Cô Thần CÙNG đáp 1 cung
    GÓC (Dần Thân Tỵ Hợi) → 4 sao duyên-nghiệp (bản-năng / thánh-tính / băng-tâm-sát / cô-độc) chế-hóa
    lẫn nhau; sao lạc-lõng (Hồng năm dương, Hỉ năm âm) cùng cung Long Đức (tứ đức tiếp tay Thiếu Dương).
    Đối chiếu tuổi tứ Đào Hoa (Tý Ngọ Mão Dậu): Thiên Không ĐỘC THỦ ở tứ mộ (không góc, vắng Hồng Loan)
    = gieo họa. Founder năm Thìn → góc tu-dưỡng = Tỵ = đồng cung Mệnh.
    """
    from engine.tu_vi import an_sao as _a, sao_q3

    BR = _a.BRANCHES_TVI
    NB = {n: i for i, n in enumerate(BR)}
    CORNERS = {NB[x] for x in ("Dần", "Thân", "Tỵ", "Hợi")}
    TU_MO = {NB[x] for x in ("Thìn", "Tuất", "Sửu", "Mùi")}

    colo = lac = 0
    for yb in ("Thìn", "Tuất", "Sửu", "Mùi"):
        tt = _a.thai_tue_belt(yb)
        tts = sao_q3.tuong_tinh_belt(yb)
        core = {_a.thien_khong(yb), tt["Thiếu Dương"], tts["Kiếp Sát"], _a.co_than(yb)}
        if len(core) == 1 and next(iter(core)) in CORNERS:
            colo += 1
        duong = NB[yb] % 2 == 0
        lac_star = _a.hong_loan(yb) if duong else _a.thien_hi(yb)
        if lac_star == tt["Long Đức"]:
            lac += 1

    doc_thu = 0
    for yb in ("Tý", "Ngọ", "Mão", "Dậu"):
        tk = _a.thien_khong(yb)
        if tk in TU_MO and tk not in CORNERS:
            doc_thu += 1

    tt = _a.thai_tue_belt("Thìn")
    tts = sao_q3.tuong_tinh_belt("Thìn")
    fcore = {_a.thien_khong("Thìn"), tt["Thiếu Dương"], tts["Kiếp Sát"], _a.co_than("Thìn")}
    founder_corner = BR[next(iter(fcore))] if len(fcore) == 1 else None
    return {
        "tu_mo_years_corner_colocated": colo,
        "tu_mo_lac_long_eq_long_duc": lac,
        "dao_hoa_thien_khong_doc_thu": doc_thu,
        "follows_dang_son_tu_duong": colo == 4 and lac == 4 and doc_thu == 4,
        "founder_corner": founder_corner,
    }


def verify_hoa_linh_school():
    """Định lý Hỏa Linh (Tập 2 Ch.20-21) — Iron #3 đa phái. CHỖ ĐẦU TIÊN engine KHÔNG theo phái
    Đằng Sơn (ghi nhận TRUNG THỰC, KHÔNG ép sửa — multi-school respect, present cho founder duyệt).

    Bài thiệu TRUYỀN THỐNG (Hỏa, Linh) tại cung khởi: Dần Ngọ Tuất→(Sửu,Mão) · Thân Tý Thìn→(Dần,Tuất)
    · Tỵ Dậu Sửu→(Mão,Tuất) · Hợi Mão Mùi→(Dậu,Tuất). Đằng Sơn suy lại từ thủy-hỏa giao thoa
    (trùng Tạ Phồn Trị): ĐẢO riêng Tỵ Dậu Sửu → (Tuất, Mão). Engine `hoa_linh_tinh` theo TRUYỀN THỐNG.
    Về GIỜ: engine cộng h cho CẢ Hỏa+Linh (thuận-thuận = phái Hán/thiên-văn — Đằng Sơn cho là chuẩn
    thiên-văn nhất, dù bản thân tạm dùng VN thuận-nghịch). Founder năm Thìn → Hỏa Dần, Linh Tuất:
    KHỚP cả 2 phái (tranh chấp chỉ ở Tỵ Dậu Sửu).
    """
    from engine.tu_vi import an_sao as _a

    BR = _a.BRANCHES_TVI
    TRAD = {
        "Dần": ("Sửu", "Mão"), "Ngọ": ("Sửu", "Mão"), "Tuất": ("Sửu", "Mão"),
        "Thân": ("Dần", "Tuất"), "Tý": ("Dần", "Tuất"), "Thìn": ("Dần", "Tuất"),
        "Tỵ": ("Mão", "Tuất"), "Dậu": ("Mão", "Tuất"), "Sửu": ("Mão", "Tuất"),
        "Hợi": ("Dậu", "Tuất"), "Mão": ("Dậu", "Tuất"), "Mùi": ("Dậu", "Tuất"),
    }
    DANGSON = {**TRAD, "Tỵ": ("Tuất", "Mão"), "Dậu": ("Tuất", "Mão"), "Sửu": ("Tuất", "Mão")}
    eng = {yb: tuple(BR[i] for i in _a.hoa_linh_tinh(yb, 1)) for yb in BR}   # giờ Tý → h=0
    match_trad = [yb for yb in BR if eng[yb] == TRAD[yb]]
    match_ds = [yb for yb in BR if eng[yb] == DANGSON[yb]]
    tds = ("Tỵ", "Dậu", "Sửu")
    e1, e2 = _a.hoa_linh_tinh("Tý", 1), _a.hoa_linh_tinh("Tý", 2)            # h: 0 vs 1
    both_thuan = ((e2[0] - e1[0]) % 12 == 1) and ((e2[1] - e1[1]) % 12 == 1)
    return {
        "match_traditional": len(match_trad),
        "match_dang_son_correction": len(match_ds),
        "engine_follows_traditional": len(match_trad) == 12,
        "diverges_from_dang_son_at": sorted(yb for yb in tds if eng[yb] != DANGSON[yb]),
        "ty_dau_suu_engine": list(eng["Tỵ"]),
        "ty_dau_suu_dang_son": list(DANGSON["Tỵ"]),
        "gio_both_thuan_han_school": both_thuan,
        "founder_thin_hoa_linh": list(eng["Thìn"]),
    }


def verify_menh_than_chu():
    """Định lý Mệnh chủ / Thân chủ (Tập 2 Ch.23 p278-279) — bí kíp Trần Đoàn, Iron #3.

    Mệnh chủ an theo CHI MỆNH cung; Thân chủ an theo CHI NĂM. Bảng Đằng Sơn (≡ TVDSTT Q.2):
    Mệnh chủ — Tý:Tham Lang · Sửu/Hợi:Cự Môn · Dần/Tuất:Lộc Tồn · Mão/Dậu:Văn Khúc · Tỵ/Mùi:VŨ KHÚC
    · Thìn/Thân:Liêm Trinh · Ngọ:Phá Quân. → founder Mệnh Tỵ = VŨ KHÚC (KHÔNG Liêm Trinh — bảng VN sai).
    Thân chủ — Tý:LINH Tinh · Ngọ:Hỏa Tinh · Sửu/Mùi:Thiên Tướng · Dần/Thân:Thiên Lương · Mão/Dậu:Thiên
    Đồng · Tỵ/Hợi:Thiên Cơ · Thìn/Tuất:Văn Xương. ENGINE LỆCH ở Tý (engine=Hỏa Tinh, Đằng Sơn=Linh Tinh)
    — Linh Tinh vắng mặt toàn bảng Thân chủ engine = nghi BUG sao chép (KHÔNG đụng founder năm Thìn=Văn Xương).
    """
    from engine.tu_vi import an_sao as _a

    BR = _a.BRANCHES_TVI
    MENH_CHU_DS = {
        "Tý": "Tham Lang", "Sửu": "Cự Môn", "Hợi": "Cự Môn", "Dần": "Lộc Tồn", "Tuất": "Lộc Tồn",
        "Mão": "Văn Khúc", "Dậu": "Văn Khúc", "Tỵ": "Vũ Khúc", "Mùi": "Vũ Khúc",
        "Thìn": "Liêm Trinh", "Thân": "Liêm Trinh", "Ngọ": "Phá Quân",
    }
    THAN_CHU_DS = {
        "Tý": "Linh Tinh", "Ngọ": "Hỏa Tinh", "Sửu": "Thiên Tướng", "Mùi": "Thiên Tướng",
        "Dần": "Thiên Lương", "Thân": "Thiên Lương", "Mão": "Thiên Đồng", "Dậu": "Thiên Đồng",
        "Tỵ": "Thiên Cơ", "Hợi": "Thiên Cơ", "Thìn": "Văn Xương", "Tuất": "Văn Xương",
    }
    menh_eng = {b: _a.menh_chu(BR.index(b)) for b in BR}
    than_eng = {b: _a.than_chu(b) for b in BR}
    menh_match = [b for b in BR if menh_eng[b] == MENH_CHU_DS[b]]
    than_match = [b for b in BR if than_eng[b] == THAN_CHU_DS[b]]
    than_div = sorted(b for b in BR if than_eng[b] != THAN_CHU_DS[b])
    linh_missing = "Linh Tinh" not in set(than_eng.values())
    return {
        "menh_chu_match": len(menh_match),
        "menh_chu_follows_dang_son": len(menh_match) == 12,
        "founder_menh_chu": menh_eng["Tỵ"],
        "founder_than_chu": than_eng["Thìn"],
        "than_chu_match": len(than_match),
        "than_chu_diverges_at": than_div,
        "ty_than_chu_engine": than_eng["Tý"],
        "ty_than_chu_dang_son": THAN_CHU_DS["Tý"],
        "linh_tinh_missing_in_engine_table": linh_missing,
    }


def verify_tuan_triet():
    """Định lý Tuần Triệt (Tập 2 Ch.24-25) — không vong.

    Tuần ("Tuần trung không vong") = 2 chi ngoài chu kỳ thiên can của lục-giáp-tuần chứa năm sinh
    (Thiên-Địa trái cựa → "không vong"; tài Thiên-Địa, "phản Thái Tuế"). Triệt ("Triệt lộ không vong")
    = không vong của THÁNG, an theo can năm (Bảng 2 Đằng Sơn): Giáp Kỷ→Thân Dậu · Ất Canh→Ngọ Mùi ·
    Bính Tân→Thìn Tỵ · Đinh Nhâm→Dần Mão · Mậu Quý→Tý Sửu. ĐỊNH LÝ (tr.294): THÁI TUẾ KHÔNG BAO GIỜ
    bị Tuần xâm phạm (chi năm ∉ Tuần, vì chi năm nằm TRONG tuần còn không-vong là 2 chi DƯ).
    Founder Mậu Thìn → Triệt Tý-Sửu (Tật Ách-Tài Bạch), Tuần Tuất-Hợi (Nô Bộc-Thiên Di) → Mệnh Tỵ THÔNG
    (ngoài cả hai); Thiên Di Hợi (Phá Quân + Không Kiếp) NẰM TRONG Tuần → xung-phá bị không-vong-hóa.
    """
    from engine.tu_vi import an_sao as _a, sao_q3

    BR = _a.BRANCHES_TVI
    STEMS = _a.STEMS_TVI
    TRIET_DS = {
        "Giáp": {"Thân", "Dậu"}, "Kỷ": {"Thân", "Dậu"}, "Ất": {"Ngọ", "Mùi"}, "Canh": {"Ngọ", "Mùi"},
        "Bính": {"Thìn", "Tỵ"}, "Tân": {"Thìn", "Tỵ"}, "Đinh": {"Dần", "Mão"}, "Nhâm": {"Dần", "Mão"},
        "Mậu": {"Tý", "Sửu"}, "Quý": {"Tý", "Sửu"},
    }
    triet_match = [s for s in STEMS if {BR[i] for i in sao_q3.triet(s)} == TRIET_DS[s]]
    never = True
    for k in range(60):                                   # 60 lục giáp năm
        stem, branch_idx = STEMS[k % 10], k % 12
        if branch_idx in sao_q3.tuan(stem, BR[branch_idx]):
            never = False
            break
    ftriet = {BR[i] for i in sao_q3.triet("Mậu")}
    ftuan = {BR[i] for i in sao_q3.tuan("Mậu", "Thìn")}
    return {
        "triet_match": len(triet_match),
        "triet_follows_dang_son": len(triet_match) == 10,
        "thai_tue_never_in_tuan": never,
        "founder_triet": sorted(ftriet),
        "founder_tuan": sorted(ftuan),
        "menh_clear_of_both": "Tỵ" not in (ftriet | ftuan),
        "thien_di_in_tuan": "Hợi" in ftuan,
    }


def full_report():
    return {
        "tam_hop": verify_tam_hop(),
        "brightness": verify_brightness(),
        "brightness_relation": verify_brightness_relation(),
        "hoa_ky_structure": verify_hoa_ky_structure(),
        "loc_quyen_walk": verify_loc_quyen_walk(),
        "star_hoa_participation": verify_star_hoa_participation(),
        "bat_quai_ngu_hanh": verify_bat_quai_ngu_hanh(),
        "loc_ton_kinh_da": verify_loc_ton_kinh_da(),
        "luu_ha_school": verify_luu_ha_school(),
        "khoi_viet_school": verify_khoi_viet_school(),
        "dao_ma_cai_sat": verify_dao_ma_cai_sat(),
        "tu_mo_tu_duong": verify_tu_mo_tu_duong(),
        "hoa_linh_school": verify_hoa_linh_school(),
        "menh_than_chu": verify_menh_than_chu(),
        "tuan_triet": verify_tuan_triet(),
        "tu_hoa_balance": verify_tu_hoa_balance(),
        "conservation": verify_conservation(),
    }
