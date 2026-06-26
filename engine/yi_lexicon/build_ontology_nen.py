#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh data/yi_lexicon/ontology_nen.json — xương sống ontology nền Đông phương học.
CANONICAL deterministic. Cross-check với concept_index trong wiki.sqlite3.
"""
import json, os, sqlite3, sys, time

ROOT = "/Users/ozvietnamdesktop/Desktop/yi"
OUT = os.path.join(ROOT, "data/yi_lexicon/ontology_nen.json")
WIKI = os.path.join(ROOT, "data/yi_wiki/wiki.sqlite3")

# ── NGŨ HÀNH ──────────────────────────────────────────────
NGU_HANH = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]
NGU_HANH_ZH = {"Mộc": "木", "Hỏa": "火", "Thổ": "土", "Kim": "金", "Thủy": "水"}
# sinh: Mộc→Hỏa→Thổ→Kim→Thủy→Mộc
SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
# khắc: Mộc→Thổ→Thủy→Hỏa→Kim→Mộc
KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}

# ── ÂM DƯƠNG ──────────────────────────────────────────────
AM_DUONG = {"Dương": "陽", "Âm": "陰"}

# ── THIÊN CAN (10) {âm dương, ngũ hành} ───────────────────
THIEN_CAN = [
    ("Giáp", "甲", "Dương", "Mộc"),
    ("Ất",   "乙", "Âm",    "Mộc"),
    ("Bính", "丙", "Dương", "Hỏa"),
    ("Đinh", "丁", "Âm",    "Hỏa"),
    ("Mậu",  "戊", "Dương", "Thổ"),
    ("Kỷ",   "己", "Âm",    "Thổ"),
    ("Canh", "庚", "Dương", "Kim"),
    ("Tân",  "辛", "Âm",    "Kim"),
    ("Nhâm", "壬", "Dương", "Thủy"),
    ("Quý",  "癸", "Âm",    "Thủy"),
]

# ── ĐỊA CHI (12) {âm dương, ngũ hành, tàng can} ───────────
# Tàng can theo canon Tử Bình (bản khí + trung khí + dư khí).
DIA_CHI = [
    ("Tý",   "子", "Dương", "Thủy", ["Quý"]),
    ("Sửu",  "丑", "Âm",    "Thổ",  ["Kỷ", "Quý", "Tân"]),
    ("Dần",  "寅", "Dương", "Mộc",  ["Giáp", "Bính", "Mậu"]),
    ("Mão",  "卯", "Âm",    "Mộc",  ["Ất"]),
    ("Thìn", "辰", "Dương", "Thổ",  ["Mậu", "Ất", "Quý"]),
    ("Tỵ",   "巳", "Âm",    "Hỏa",  ["Bính", "Mậu", "Canh"]),
    ("Ngọ",  "午", "Dương", "Hỏa",  ["Đinh", "Kỷ"]),
    ("Mùi",  "未", "Âm",    "Thổ",  ["Kỷ", "Đinh", "Ất"]),
    ("Thân", "申", "Dương", "Kim",  ["Canh", "Nhâm", "Mậu"]),
    ("Dậu",  "酉", "Âm",    "Kim",  ["Tân"]),
    ("Tuất", "戌", "Dương", "Thổ",  ["Mậu", "Tân", "Đinh"]),
    ("Hợi",  "亥", "Âm",    "Thủy", ["Nhâm", "Giáp"]),
]

# ── BÁT QUÁI (8) {ngũ hành, âm dương, nạp giáp, zh} ───────
# Âm/Dương theo Tiên Thiên: Càn/Chấn/Khảm/Cấn = Dương; Khôn/Tốn/Ly/Đoài = Âm.
# (Theo lý: 3 quái có vạch dương lẻ = dương quái; vạch âm lẻ = âm quái.)
# Nạp giáp: Càn→Giáp/Nhâm, Khôn→Ất/Quý, Chấn→Canh, Tốn→Tân,
#           Khảm→Mậu, Ly→Kỷ, Cấn→Bính, Đoài→Đinh.
BAT_QUAI = [
    ("Càn",  "乾", "Kim",  "Dương", ["Giáp", "Nhâm"]),
    ("Đoài", "兌", "Kim",  "Âm",    ["Đinh"]),
    ("Ly",   "離", "Hỏa",  "Âm",    ["Kỷ"]),
    ("Chấn", "震", "Mộc",  "Dương", ["Canh"]),
    ("Tốn",  "巽", "Mộc",  "Âm",    ["Tân"]),
    ("Khảm", "坎", "Thủy", "Dương", ["Mậu"]),
    ("Cấn",  "艮", "Thổ",  "Dương", ["Bính"]),
    ("Khôn", "坤", "Thổ",  "Âm",    ["Ất", "Quý"]),
]

# Tam hào (Tiên Thiên Bát Quái nhị tiến vị) — dưới→trên, 1=dương vạch liền, 0=âm vạch đứt
QUAI_LINES = {
    "Càn":  [1, 1, 1],
    "Đoài": [1, 1, 0],
    "Ly":   [1, 0, 1],
    "Chấn": [1, 0, 0],
    "Tốn":  [0, 1, 1],
    "Khảm": [0, 1, 0],
    "Cấn":  [0, 0, 1],
    "Khôn": [0, 0, 0],
}

# ── 64 QUẺ = thượng × hạ ──────────────────────────────────
# Tên VN chuẩn 64 quẻ theo (thượng, hạ). zh kèm theo.
# key = "ThượngQuái/HạQuái"
QUE_64 = {
    # Thượng Càn
    "Càn/Càn": ("Thuần Càn", "乾為天"),
    "Càn/Khôn": ("Thiên Địa Bĩ", "天地否"),
    "Càn/Chấn": ("Thiên Lôi Vô Vọng", "天雷無妄"),
    "Càn/Tốn": ("Thiên Phong Cấu", "天風姤"),
    "Càn/Khảm": ("Thiên Thủy Tụng", "天水訟"),
    "Càn/Ly": ("Thiên Hỏa Đồng Nhân", "天火同人"),
    "Càn/Cấn": ("Thiên Sơn Độn", "天山遯"),
    "Càn/Đoài": ("Thiên Trạch Lý", "天澤履"),
    # Thượng Khôn
    "Khôn/Càn": ("Địa Thiên Thái", "地天泰"),
    "Khôn/Khôn": ("Thuần Khôn", "坤為地"),
    "Khôn/Chấn": ("Địa Lôi Phục", "地雷復"),
    "Khôn/Tốn": ("Địa Phong Thăng", "地風升"),
    "Khôn/Khảm": ("Địa Thủy Sư", "地水師"),
    "Khôn/Ly": ("Địa Hỏa Minh Di", "地火明夷"),
    "Khôn/Cấn": ("Địa Sơn Khiêm", "地山謙"),
    "Khôn/Đoài": ("Địa Trạch Lâm", "地澤臨"),
    # Thượng Chấn
    "Chấn/Càn": ("Lôi Thiên Đại Tráng", "雷天大壯"),
    "Chấn/Khôn": ("Lôi Địa Dự", "雷地豫"),
    "Chấn/Chấn": ("Thuần Chấn", "震為雷"),
    "Chấn/Tốn": ("Lôi Phong Hằng", "雷風恆"),
    "Chấn/Khảm": ("Lôi Thủy Giải", "雷水解"),
    "Chấn/Ly": ("Lôi Hỏa Phong", "雷火豐"),
    "Chấn/Cấn": ("Lôi Sơn Tiểu Quá", "雷山小過"),
    "Chấn/Đoài": ("Lôi Trạch Quy Muội", "雷澤歸妹"),
    # Thượng Tốn
    "Tốn/Càn": ("Phong Thiên Tiểu Súc", "風天小畜"),
    "Tốn/Khôn": ("Phong Địa Quán", "風地觀"),
    "Tốn/Chấn": ("Phong Lôi Ích", "風雷益"),
    "Tốn/Tốn": ("Thuần Tốn", "巽為風"),
    "Tốn/Khảm": ("Phong Thủy Hoán", "風水渙"),
    "Tốn/Ly": ("Phong Hỏa Gia Nhân", "風火家人"),
    "Tốn/Cấn": ("Phong Sơn Tiệm", "風山漸"),
    "Tốn/Đoài": ("Phong Trạch Trung Phu", "風澤中孚"),
    # Thượng Khảm
    "Khảm/Càn": ("Thủy Thiên Nhu", "水天需"),
    "Khảm/Khôn": ("Thủy Địa Tỷ", "水地比"),
    "Khảm/Chấn": ("Thủy Lôi Truân", "水雷屯"),
    "Khảm/Tốn": ("Thủy Phong Tỉnh", "水風井"),
    "Khảm/Khảm": ("Thuần Khảm", "坎為水"),
    "Khảm/Ly": ("Thủy Hỏa Ký Tế", "水火既濟"),
    "Khảm/Cấn": ("Thủy Sơn Kiển", "水山蹇"),
    "Khảm/Đoài": ("Thủy Trạch Tiết", "水澤節"),
    # Thượng Ly
    "Ly/Càn": ("Hỏa Thiên Đại Hữu", "火天大有"),
    "Ly/Khôn": ("Hỏa Địa Tấn", "火地晉"),
    "Ly/Chấn": ("Hỏa Lôi Phệ Hạp", "火雷噬嗑"),
    "Ly/Tốn": ("Hỏa Phong Đỉnh", "火風鼎"),
    "Ly/Khảm": ("Hỏa Thủy Vị Tế", "火水未濟"),
    "Ly/Ly": ("Thuần Ly", "離為火"),
    "Ly/Cấn": ("Hỏa Sơn Lữ", "火山旅"),
    "Ly/Đoài": ("Hỏa Trạch Khuê", "火澤睽"),
    # Thượng Cấn
    "Cấn/Càn": ("Sơn Thiên Đại Súc", "山天大畜"),
    "Cấn/Khôn": ("Sơn Địa Bác", "山地剝"),
    "Cấn/Chấn": ("Sơn Lôi Di", "山雷頤"),
    "Cấn/Tốn": ("Sơn Phong Cổ", "山風蠱"),
    "Cấn/Khảm": ("Sơn Thủy Mông", "山水蒙"),
    "Cấn/Ly": ("Sơn Hỏa Bí", "山火賁"),
    "Cấn/Cấn": ("Thuần Cấn", "艮為山"),
    "Cấn/Đoài": ("Sơn Trạch Tổn", "山澤損"),
    # Thượng Đoài
    "Đoài/Càn": ("Trạch Thiên Quải", "澤天夬"),
    "Đoài/Khôn": ("Trạch Địa Tụy", "澤地萃"),
    "Đoài/Chấn": ("Trạch Lôi Tùy", "澤雷隨"),
    "Đoài/Tốn": ("Trạch Phong Đại Quá", "澤風大過"),
    "Đoài/Khảm": ("Trạch Thủy Khốn", "澤水困"),
    "Đoài/Ly": ("Trạch Hỏa Cách", "澤火革"),
    "Đoài/Cấn": ("Trạch Sơn Hàm", "澤山咸"),
    "Đoài/Đoài": ("Thuần Đoài", "兌為澤"),
}


def build():
    flags = []

    # Ngũ hành block
    ngu_hanh = {}
    for h in NGU_HANH:
        ngu_hanh[h] = {
            "zh": NGU_HANH_ZH[h],
            "sinh": SINH[h],      # h sinh ra ai
            "khac": KHAC[h],      # h khắc ai
            "duoc_sinh_boi": next(k for k, v in SINH.items() if v == h),
            "bi_khac_boi": next(k for k, v in KHAC.items() if v == h),
        }

    am_duong = {k: {"zh": v} for k, v in AM_DUONG.items()}

    thien_can = {}
    for i, (vi, zh, ad, nh) in enumerate(THIEN_CAN, 1):
        thien_can[vi] = {"so": i, "zh": zh, "am_duong": ad, "ngu_hanh": nh}

    dia_chi = {}
    for i, (vi, zh, ad, nh, tang) in enumerate(DIA_CHI, 1):
        dia_chi[vi] = {"so": i, "zh": zh, "am_duong": ad,
                       "ngu_hanh": nh, "tang_can": tang}

    bat_quai = {}
    for i, (vi, zh, nh, ad, nap) in enumerate(BAT_QUAI, 1):
        bat_quai[vi] = {"so": i, "zh": zh, "ngu_hanh": nh, "am_duong": ad,
                        "nap_giap": nap, "hao": QUAI_LINES[vi]}

    # 64 quẻ sinh từ 8×8
    que_64 = {}
    so = 0
    for tq, *_ in BAT_QUAI:
        for hq, *_ in BAT_QUAI:
            so += 1
            key = f"{tq}/{hq}"
            ten_vi, ten_zh = QUE_64[key]
            que_64[ten_vi] = {
                "so_sinh": so,
                "thuong_quai": tq,
                "ha_quai": hq,
                "zh": ten_zh,
                "ngu_hanh_thuong": bat_quai[tq]["ngu_hanh"],
                "ngu_hanh_ha": bat_quai[hq]["ngu_hanh"],
            }

    # ALIAS (vi/zh → canonical key) gom can/chi/quái/quẻ
    alias = {"thien_can": {}, "dia_chi": {}, "bat_quai": {}, "que_64": {}}
    for vi, d in thien_can.items():
        alias["thien_can"][vi] = vi
        alias["thien_can"][d["zh"]] = vi
    for vi, d in dia_chi.items():
        alias["dia_chi"][vi] = vi
        alias["dia_chi"][d["zh"]] = vi
    for vi, d in bat_quai.items():
        alias["bat_quai"][vi] = vi
        alias["bat_quai"][d["zh"]] = vi
    for vi, d in que_64.items():
        alias["que_64"][vi] = vi
        if d["zh"]:
            alias["que_64"][d["zh"]] = vi

    ontology = {
        "_meta": {
            "ten": "Ontology Nền — Xương sống toạ-độ Đông phương học",
            "mo_ta": "Bảng canonical deterministic: ngũ hành, âm dương, thiên can, "
                     "địa chi, bát quái, 64 quẻ + alias. Nối Bát Tự ↔ Kinh Dịch qua nạp giáp.",
            "phien_ban": "1.0",
            "tao_luc": int(time.time()),
            "nguon": "Canon kinh điển (CLAUDE.md spec) — cross-check concept_index/wiki.sqlite3",
        },
        "ngu_hanh": ngu_hanh,
        "am_duong": am_duong,
        "thien_can": thien_can,
        "dia_chi": dia_chi,
        "bat_quai": bat_quai,
        "que_64": que_64,
        "alias": alias,
    }

    # ── CROSS-CHECK với concept_index ──
    if os.path.exists(WIKI):
        db = sqlite3.connect(WIKI)
        cur = db.cursor()

        def db_note(name):
            r = cur.execute(
                "select canonical_zh, short_note from concept_index where canonical_vi=? limit 1",
                (name,)).fetchone()
            return r

        # Thiên can: hành (suy từ note keyword) + zh
        hanh_kw = {"mộc": "Mộc", "hỏa": "Hỏa", "thổ": "Thổ", "kim": "Kim", "thủy": "Thủy"}
        for vi, d in thien_can.items():
            r = db_note(vi)
            if not r:
                flags.append(f"[thien_can] '{vi}' không có trong concept_index (DB thiếu, canon giữ).")
                continue
            zh_db, note = r
            if zh_db and zh_db != d["zh"]:
                flags.append(f"[thien_can] '{vi}' zh lệch: canon={d['zh']} vs DB={zh_db}.")
            note_l = (note or "").lower()
            db_hanh = [v for k, v in hanh_kw.items() if k in note_l]
            if db_hanh and d["ngu_hanh"] not in db_hanh:
                flags.append(f"[thien_can] '{vi}' ngũ hành lệch: canon={d['ngu_hanh']} vs DB-note gợi {db_hanh}.")

        # Địa chi: hành + tàng can từ note
        for vi, d in dia_chi.items():
            r = db_note(vi)
            if not r:
                flags.append(f"[dia_chi] '{vi}' không có trong concept_index.")
                continue
            zh_db, note = r
            if zh_db and zh_db != d["zh"]:
                flags.append(f"[dia_chi] '{vi}' zh lệch: canon={d['zh']} vs DB={zh_db}.")
            note_l = (note or "").lower()
            db_hanh = [v for k, v in hanh_kw.items() if k in note_l]
            if db_hanh and d["ngu_hanh"] not in db_hanh:
                flags.append(f"[dia_chi] '{vi}' ngũ hành lệch: canon={d['ngu_hanh']} vs DB gợi {db_hanh}.")
            # tàng can — chỉ check khi DB có ghi "Tàng can:"
            if note and "Tàng can:" in note:
                seg = note.split("Tàng can:", 1)[1]
                seg = seg.split(".")[0]
                db_tang = [t.strip() for t in seg.replace("，", ",").replace(";", ",").split(",") if t.strip()]
                # so khớp tập
                cn = set(d["tang_can"]); dbn = set(db_tang)
                if cn != dbn:
                    flags.append(f"[dia_chi] '{vi}' tàng can lệch: canon={d['tang_can']} vs DB={db_tang}.")

        # Bát quái: zh (DB hay dùng giản thể) + hành
        for vi, d in bat_quai.items():
            r = db_note(vi)
            if not r:
                flags.append(f"[bat_quai] '{vi}' không có trong concept_index.")
                continue
            zh_db, note = r
            if zh_db and zh_db != d["zh"]:
                flags.append(f"[bat_quai] '{vi}' zh lệch: canon(phồn thể)={d['zh']} vs DB={zh_db} (DB dùng giản thể?).")

        db.close()
    else:
        flags.append("wiki.sqlite3 không tồn tại — bỏ qua cross-check.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ontology, f, ensure_ascii=False, indent=2)

    return ontology, flags


def self_test(ont):
    errs = []
    if len(ont["thien_can"]) != 10:
        errs.append(f"thien_can != 10 ({len(ont['thien_can'])})")
    if len(ont["dia_chi"]) != 12:
        errs.append(f"dia_chi != 12 ({len(ont['dia_chi'])})")
    if len(ont["bat_quai"]) != 8:
        errs.append(f"bat_quai != 8 ({len(ont['bat_quai'])})")
    if len(ont["que_64"]) != 64:
        errs.append(f"que_64 != 64 ({len(ont['que_64'])})")
    # sinh khép vòng
    h = "Mộc"; seen = []
    for _ in range(5):
        seen.append(h); h = ont["ngu_hanh"][h]["sinh"]
    if h != "Mộc" or len(set(seen)) != 5:
        errs.append(f"sinh không khép vòng: {seen}->{h}")
    # khắc khép vòng
    h = "Mộc"; seen = []
    for _ in range(5):
        seen.append(h); h = ont["ngu_hanh"][h]["khac"]
    if h != "Mộc" or len(set(seen)) != 5:
        errs.append(f"khắc không khép vòng: {seen}->{h}")
    # nạp giáp phủ 8 quái + phủ đủ 10 can
    nap_cans = set()
    for vi, d in ont["bat_quai"].items():
        if not d["nap_giap"]:
            errs.append(f"nạp giáp trống: {vi}")
        nap_cans.update(d["nap_giap"])
    if nap_cans != set(ont["thien_can"].keys()):
        errs.append(f"nạp giáp KHÔNG phủ đủ 10 can: thiếu {set(ont['thien_can'])-nap_cans}")
    # 64 quẻ: mỗi quẻ thượng+hạ hợp lệ + so_sinh 1..64 duy nhất
    sos = sorted(d["so_sinh"] for d in ont["que_64"].values())
    if sos != list(range(1, 65)):
        errs.append("so_sinh quẻ không 1..64 duy nhất")
    quai_set = set(ont["bat_quai"].keys())
    for ten, d in ont["que_64"].items():
        if d["thuong_quai"] not in quai_set or d["ha_quai"] not in quai_set:
            errs.append(f"quẻ {ten} có quái không hợp lệ")
    return errs


if __name__ == "__main__":
    ont, flags = build()
    errs = self_test(ont)
    print("=== SELF-TEST ===")
    print(f"thien_can={len(ont['thien_can'])} dia_chi={len(ont['dia_chi'])} "
          f"bat_quai={len(ont['bat_quai'])} que_64={len(ont['que_64'])}")
    print("sinh vòng:", " → ".join(["Mộc", ont['ngu_hanh']['Mộc']['sinh'],
          ont['ngu_hanh']['Hỏa']['sinh'], ont['ngu_hanh']['Thổ']['sinh'],
          ont['ngu_hanh']['Kim']['sinh'], ont['ngu_hanh']['Thủy']['sinh']]))
    print("khắc vòng:", " → ".join(["Mộc", ont['ngu_hanh']['Mộc']['khac'],
          ont['ngu_hanh']['Thổ']['khac'], ont['ngu_hanh']['Thủy']['khac'],
          ont['ngu_hanh']['Hỏa']['khac'], ont['ngu_hanh']['Kim']['khac']]))
    nap = set()
    for d in ont["bat_quai"].values(): nap.update(d["nap_giap"])
    print(f"nạp giáp phủ {len(nap)}/10 can")
    print("PASS" if not errs else "FAIL: " + "; ".join(errs))
    print("=== CROSS-CHECK FLAGS ===")
    if flags:
        for f in flags: print(" -", f)
    else:
        print(" (không lệch)")
    sys.exit(0 if not errs else 1)
