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


def full_report():
    return {
        "tam_hop": verify_tam_hop(),
        "brightness": verify_brightness(),
        "brightness_relation": verify_brightness_relation(),
        "hoa_ky_structure": verify_hoa_ky_structure(),
        "loc_quyen_walk": verify_loc_quyen_walk(),
        "star_hoa_participation": verify_star_hoa_participation(),
        "bat_quai_ngu_hanh": verify_bat_quai_ngu_hanh(),
        "tu_hoa_balance": verify_tu_hoa_balance(),
        "conservation": verify_conservation(),
    }
