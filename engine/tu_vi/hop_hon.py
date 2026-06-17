"""Hợp Hôn Tam Hệ — chấm độ tương ứng 2 lá số qua Tử Vi + Bát Tự + Kinh Dịch.

Đóng gói phương pháp đã đào + qua phản biện đa chiều (2026-06-16):
- KHÔNG predict hợp/tan (Iron Rule #6/#8). Đọc CẤU TRÚC, nói 2 mặt: khóa duyên + chỗ cọ xát.
- Trục CƯƠNG–NHU là quy luật sống sót qua phản biện → trọng số cao nhất.
- Mỗi điểm có giải thích để user hiểu, kèm hướng dẫn + lời nhắc paradigm.

Input thuần (không I/O): la_so_input Tử Vi + pillars Bát Tự + quẻ Hà Lạc của 2 người.
"""
from __future__ import annotations

# ── Bảng nền ──
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
_CHI_CANON = {"ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn",
              "ti": "Tỵ", "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu",
              "tuat": "Tuất", "hoi": "Hợi"}

LUC_HOP = {frozenset(x) for x in [("Tý", "Sửu"), ("Dần", "Hợi"), ("Mão", "Tuất"),
           ("Thìn", "Dậu"), ("Tỵ", "Thân"), ("Ngọ", "Mùi")]}
TAM_HOP = [{"Thân", "Tý", "Thìn"}, {"Dần", "Ngọ", "Tuất"}, {"Tỵ", "Dậu", "Sửu"}, {"Hợi", "Mão", "Mùi"}]
LUC_XUNG = {frozenset(x) for x in [("Tý", "Ngọ"), ("Sửu", "Mùi"), ("Dần", "Thân"),
            ("Mão", "Dậu"), ("Thìn", "Tuất"), ("Tỵ", "Hợi")]}
LUC_HAI = {frozenset(x) for x in [("Tý", "Mùi"), ("Sửu", "Ngọ"), ("Dần", "Tỵ"),
           ("Mão", "Thìn"), ("Thân", "Hợi"), ("Dậu", "Tuất")]}
NGU_HOP_CAN = {frozenset(x) for x in [("Giáp", "Kỷ"), ("Ất", "Canh"), ("Bính", "Tân"),
               ("Đinh", "Nhâm"), ("Mậu", "Quý")]}

CAN_NH = {"Giáp": "Mộc", "Ất": "Mộc", "Bính": "Hỏa", "Đinh": "Hỏa", "Mậu": "Thổ",
          "Kỷ": "Thổ", "Canh": "Kim", "Tân": "Kim", "Nhâm": "Thủy", "Quý": "Thủy"}
CHI_NH = {"Dần": "Mộc", "Mão": "Mộc", "Tỵ": "Hỏa", "Ngọ": "Hỏa", "Thân": "Kim", "Dậu": "Kim",
          "Hợi": "Thủy", "Tý": "Thủy", "Thìn": "Thổ", "Tuất": "Thổ", "Sửu": "Thổ", "Mùi": "Thổ"}
CUC_NH = {"thuy_nhi_cuc": "Thủy", "moc_tam_cuc": "Mộc", "kim_tu_cuc": "Kim",
          "tho_ngu_cuc": "Thổ", "hoa_luc_cuc": "Hỏa"}
CAN_DUONG = {"Giáp", "Bính", "Mậu", "Canh", "Nhâm"}

_SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
_KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}

# Chính tinh thiên cương / thiên nhu (cho trục cương–nhu)
SAO_CUONG = {"thai_duong", "vu_khuc", "that_sat", "pha_quan", "tham_lang", "liem_trinh", "cu_mon", "tu_vi"}
SAO_NHU = {"thai_am", "thien_dong", "thien_luong", "thien_tuong", "thien_co", "thien_phu"}
_SAO_VI = {"tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương", "vu_khuc": "Vũ Khúc",
           "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh", "thien_phu": "Thiên Phủ",
           "thai_am": "Thái Âm", "tham_lang": "Tham Lang", "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng",
           "thien_luong": "Thiên Lương", "that_sat": "Thất Sát", "pha_quan": "Phá Quân"}


def _norm_chi(c):
    return _CHI_CANON.get(c, c)


def _rel_chi(a, b):
    """Quan hệ địa chi: (loại, nhãn)."""
    s = frozenset((a, b))
    if a == b:
        return "đồng", "cùng chi"
    if s in LUC_HOP:
        return "hop", "lục hợp"
    if any({a, b} <= t for t in TAM_HOP):
        return "tam_hop", "tam hợp"
    if s in LUC_XUNG:
        return "xung", "lục xung"
    if s in LUC_HAI:
        return "hai", "lục hại"
    return "trung", "trung tính"


# ════════════════ TỬ VI ════════════════
def _phu_the_info(ls):
    """chi cung Phu Thê + chính tinh + có Hóa Lộc đóng Phu Thê không."""
    fn = ls.get("fn_to_chi") or {}
    chi = _norm_chi(fn.get("phu_the"))
    ct = ls.get("chinh_tinh_per_palace") or {}
    raw_chi = fn.get("phu_the")
    sao = [_SAO_VI.get(s, s) for s in (ct.get(raw_chi) or [])]
    hoa_loc = any(t.get("hoa") == "hoa_loc" and t.get("palace_fn") == "phu_the"
                  for t in (ls.get("tu_hoa") or []))
    return chi, sao, hoa_loc


def _tu_vi_compat(ls1, ls2):
    pt1_chi, pt1_sao, loc1 = _phu_the_info(ls1)
    pt2_chi, pt2_sao, loc2 = _phu_the_info(ls2)
    diem = 50
    nx = []
    # Hai cung Phu Thê quan hệ
    if pt1_chi and pt2_chi:
        loai, nhan = _rel_chi(pt1_chi, pt2_chi)
        if loai in ("hop", "tam_hop"):
            diem += 18
            nx.append(("+", f"Hai cung Phu Thê {nhan} (Mệnh thê khế hợp) — định hướng hôn nhân hòa điệu."))
        elif loai == "xung":
            diem -= 12
            nx.append(("-", "Hai cung Phu Thê lục xung — quan niệm về bạn đời dễ lệch pha, cần dung hòa."))
        elif loai == "hai":
            diem -= 6
            nx.append(("-", "Hai cung Phu Thê lục hại — dễ có hiềm khích ngấm ngầm về chuyện vợ chồng."))
    # Lộc song nhập Phu Thê
    if loc1 and loc2:
        diem += 14
        nx.append(("+", "Cả hai đều có Hóa Lộc đóng cung Phu Thê — phúc duyên hai chiều (hiếm), được lợi từ hôn nhân."))
    elif loc1 or loc2:
        diem += 6
        nx.append(("+", "Một người có Hóa Lộc ở cung Phu Thê — mang phúc duyên cho mối quan hệ."))
    # Ngũ hành Cục sinh khắc
    c1 = CUC_NH.get(ls1.get("cuc")); c2 = CUC_NH.get(ls2.get("cuc"))
    if c1 and c2:
        if _SINH.get(c1) == c2:
            diem += 8; nx.append(("+", f"Cục {c1} (người 1) sinh Cục {c2} (người 2) — người 1 nâng đỡ người 2."))
        elif _SINH.get(c2) == c1:
            diem += 8; nx.append(("+", f"Cục {c2} (người 2) sinh Cục {c1} (người 1) — người 2 nâng đỡ người 1."))
        elif _KHAC.get(c1) == c2 or _KHAC.get(c2) == c1:
            diem -= 6; nx.append(("-", f"Cục hai người tương khắc ({c1} ↔ {c2}) — có lực ghì, cần biết nhường."))
        elif c1 == c2:
            diem += 4; nx.append(("~", f"Cùng Cục {c1} — đồng điệu, nhưng dễ cùng điểm yếu."))
    return {
        "phu_the_nguoi1": {"chi": pt1_chi, "sao": pt1_sao, "hoa_loc": loc1},
        "phu_the_nguoi2": {"chi": pt2_chi, "sao": pt2_sao, "hoa_loc": loc2},
        "diem": max(0, min(100, diem)), "nhan_xet": nx,
    }


# ════════════════ BÁT TỰ ════════════════
def _pillars_list(pillars):
    """[(can, chi)] từ pillars dict của extract_tu_tru."""
    out = []
    for k in ("year", "month", "day", "hour"):
        p = (pillars.get("pillars") or {}).get(k) or {}
        if p.get("stem") and p.get("branch"):
            out.append((p["stem"], p["branch"]))
    return out


def _element_counts(plist):
    cnt = {"Mộc": 0, "Hỏa": 0, "Thổ": 0, "Kim": 0, "Thủy": 0}
    for can, chi in plist:
        cnt[CAN_NH[can]] += 1
        cnt[CHI_NH[chi]] += 1
    return cnt


def _than_vuong(plist):
    """Thân vượng/nhược đơn giản: đắc lệnh (nguyệt) + đồng đảng (ấn+tỷ) vs khắc-tiết-hao."""
    day_can = plist[2][0]
    day_el = CAN_NH[day_can]
    month_el = CHI_NH[plist[1][1]]
    cnt = _element_counts(plist)
    sinh_day = next(k for k, v in _SINH.items() if v == day_el)  # hành sinh ra nhật chủ (Ấn)
    support = cnt[day_el] + cnt[sinh_day]
    against = sum(v for k, v in cnt.items() if k not in (day_el, sinh_day))
    dac_lenh = month_el == day_el or month_el == sinh_day
    score = support + (1.5 if dac_lenh else 0)
    vuong = score >= against - 0.5 and (dac_lenh or support >= against)
    return ("vượng" if vuong else "nhược"), day_el, dac_lenh


def _dung_than(plist):
    """Dụng thần đơn giản: vượng → cần khắc/tiết/hao; nhược → cần sinh/trợ."""
    tag, day_el, _ = _than_vuong(plist)
    khac_day = next(k for k, v in _KHAC.items() if v == day_el)  # hành khắc nhật chủ (Quan Sát)
    tiet = _SINH[day_el]            # nhật chủ sinh ra (Thực Thương)
    hao = _KHAC[day_el]            # nhật chủ khắc (Tài)
    sinh_day = next(k for k, v in _SINH.items() if v == day_el)  # Ấn
    if tag == "vượng":
        return [khac_day, tiet, hao], tag, day_el
    return [sinh_day, day_el], tag, day_el


def _bat_tu_compat(p1, p2):
    pl1, pl2 = _pillars_list(p1), _pillars_list(p2)
    diem = 50
    nx = []
    if len(pl1) < 4 or len(pl2) < 4:
        return {"diem": 50, "nhan_xet": [("~", "Thiếu giờ sinh — Bát Tự chỉ tính được phần.")], "thien_hop_dia_hop": []}
    # Thiên hợp địa hợp giữa các trụ
    POS = ["Năm", "Tháng", "Ngày", "Giờ"]
    thdh = []
    for i, (ca, ba) in enumerate(pl1):
        for j, (cb, bb) in enumerate(pl2):
            if frozenset((ca, cb)) in NGU_HOP_CAN and frozenset((ba, bb)) in LUC_HOP:
                trong = "Ngày" in (POS[i], POS[j])  # chạm trụ Ngày = cung phối ngẫu
                thdh.append({"nguoi1": POS[i], "nguoi2": POS[j], "trong_tam": trong,
                             "tru1": f"{ca}{ba}", "tru2": f"{cb}{bb}"})
    if thdh:
        cham_ngay = any(t["trong_tam"] for t in thdh)
        diem += 16 if cham_ngay else 9
        msg = "Có cặp trụ THIÊN HỢP ĐỊA HỢP (can+chi cùng hợp) — điểm khóa duyên"
        msg += " chạm đúng trụ Ngày (cung vợ chồng) — rất đáng quý." if cham_ngay else " — duyên có chốt."
        nx.append(("+", msg))
    # Nhật chủ quan hệ
    d1, d2 = CAN_NH[pl1[2][0]], CAN_NH[pl2[2][0]]
    if frozenset((pl1[2][0], pl2[2][0])) in NGU_HOP_CAN:
        diem += 12; nx.append(("+", f"Nhật chủ hai người HỢP nhau ({pl1[2][0]}–{pl2[2][0]}) — tương hợp tận gốc."))
    elif _SINH.get(d1) == d2:
        diem += 8; nx.append(("+", f"Nhật chủ người 1 ({d1}) sinh người 2 ({d2}) — người 1 dưỡng người 2."))
    elif _SINH.get(d2) == d1:
        diem += 8; nx.append(("+", f"Nhật chủ người 2 ({d2}) sinh người 1 ({d1}) — người 2 dưỡng người 1."))
    elif _KHAC.get(d1) == d2 or _KHAC.get(d2) == d1:
        diem -= 4; nx.append(("-", f"Nhật chủ tương khắc ({d1} ↔ {d2}) — có lực chế, cần một người chịu mềm."))
    # Địa chi hợp/xung/hại tổng
    hop = xung = hai = 0
    for _, b1 in pl1:
        for _, b2 in pl2:
            s = frozenset((b1, b2))
            if s in LUC_HOP: hop += 1
            elif s in LUC_XUNG: xung += 1
            elif s in LUC_HAI: hai += 1
    diem += hop * 3 - xung * 4 - hai * 3
    if hai or xung:
        nx.append(("-", f"Nền địa chi có {xung} xung + {hai} hại (so với {hop} hợp) — "
                        f"{'thiên về cọ xát, cần nề nếp để hóa giải.' if (xung+hai) > hop else 'cọ xát vừa phải.'}"))
    elif hop:
        nx.append(("+", f"Nền địa chi có {hop} lục hợp, ít xung-hại — hòa thuận."))
    # Dụng thần chung
    dt1, t1, _ = _dung_than(pl1); dt2, t2, _ = _dung_than(pl2)
    chung = set(dt1) & set(dt2)
    if chung:
        diem += 8
        nx.append(("+", f"Cùng cần hành {', '.join(chung)} (dụng thần chung) — hợp nhau ở nhu cầu sâu; "
                        f"vun cùng một hướng thì cả hai cùng lợi."))
    return {
        "diem": max(0, min(100, diem)), "nhan_xet": nx, "thien_hop_dia_hop": thdh,
        "nhat_chu_1": pl1[2][0], "nhat_chu_2": pl2[2][0],
        "than_1": t1, "than_2": t2, "dung_than_1": dt1, "dung_than_2": dt2,
        "luc_hop": hop, "luc_xung": xung, "luc_hai": hai,
    }


# ════════════════ KINH DỊCH / HÀ LẠC ════════════════
def _que_cuong(que):
    """Đếm hào dương trong binary_top_down (6 ký tự '1'=dương)."""
    b = (que or {}).get("binary_top_down") or ""
    return b.count("1")


def _ha_lac_compat(q1, q2):
    diem = 50
    nx = []
    n1, n2 = (q1 or {}).get("name_vi"), (q2 or {}).get("name_vi")
    if not n1 or not n2:
        return {"diem": 50, "nhan_xet": [], "que_1": n1, "que_2": n2}
    # ngũ hành quẻ qua thượng quái? dùng đơn giản: số hào dương → cương/nhu (đưa vào trục riêng)
    nx.append(("~", f"Quẻ cốt: người 1 = {n1}, người 2 = {n2}."))
    return {"diem": diem, "nhan_xet": nx, "que_1": n1, "que_2": n2,
            "cuong_1": _que_cuong(q1), "cuong_2": _que_cuong(q2)}


# ════════════════ TRỤC CƯƠNG – NHU (quy luật sống sót) ════════════════
def _cuong_index(ls, pillars, que):
    """Chỉ số cương 0..3 từ 3 hệ. >2 = cương, <1 = nhu."""
    s = 0.0
    parts = []
    # Tử Vi: chính tinh Mệnh
    ct = ls.get("chinh_tinh_per_palace") or {}
    menh = ls.get("menh_palace")
    msao = ct.get(menh) or []
    nc = sum(1 for x in msao if x in SAO_CUONG)
    nn = sum(1 for x in msao if x in SAO_NHU)
    if nc > nn: s += 1; parts.append("Tử Vi: chính tinh Mệnh thiên cương")
    elif nn > nc: parts.append("Tử Vi: chính tinh Mệnh thiên nhu")
    else: s += 0.5
    # Bát Tự: thân vượng = cương
    pl = _pillars_list(pillars)
    if len(pl) >= 4:
        tag, _, _ = _than_vuong(pl)
        if tag == "vượng": s += 1; parts.append("Bát Tự: thân vượng (cương)")
        else: parts.append("Bát Tự: thân nhược (nhu)")
    else:
        s += 0.5
    # Hà Lạc: hào dương quẻ cốt
    c = _que_cuong(que)
    if c >= 4: s += 1; parts.append(f"Hà Lạc: quẻ {c}/6 hào dương (cương)")
    elif c <= 2: parts.append(f"Hà Lạc: quẻ {c}/6 hào dương (nhu)")
    else: s += 0.5; parts.append("Hà Lạc: quẻ cân (3/6)")
    return s, parts


def _truc_cuong_nhu(ls1, p1, q1, ls2, p2, q2):
    s1, parts1 = _cuong_index(ls1, p1, q1)
    s2, parts2 = _cuong_index(ls2, p2, q2)
    # Thang 0–3 (mỗi hệ góp 0/0.5/1). ≥2 hệ nghiêng = theo hướng đó.
    xh = lambda s: "cương" if s >= 2 else ("nhu" if s <= 1 else "cân")
    x1, x2 = xh(s1), xh(s2)
    diem = 50
    if {x1, x2} == {"cương", "nhu"}:
        diem = 88
        gt = ("Một người CƯƠNG, một người NHU — đúng 'cương nhu giai ứng' (quẻ Hằng). "
              "Đây là trục bền nhất: người mạnh có chỗ tựa mềm, người mềm có chỗ neo cứng.")
    elif x1 == "cương" and x2 == "cương":
        diem = 42
        gt = ("Cả hai đều thiên CƯƠNG — hai cái mạnh dễ va nhau. Bền khi biết phân vai: "
              "ai chủ việc gì thì người kia nhường việc đó.")
    elif x1 == "nhu" and x2 == "nhu":
        diem = 46
        gt = ("Cả hai đều thiên NHU — êm nhưng dễ cùng thụ động, thiếu người quyết. "
              "Bền khi luân phiên đứng mũi chịu sào.")
    else:
        diem = 64
        gt = ("Một người rõ tính, một người trung hòa — co giãn được, miễn giữ tôn trọng.")
    return {"xu_huong_1": x1, "xu_huong_2": x2, "chi_so_1": round(s1, 1), "chi_so_2": round(s2, 1),
            "ung_nhau": {x1, x2} == {"cương", "nhu"}, "diem": diem, "giai_thich": gt,
            "chi_tiet_1": parts1, "chi_tiet_2": parts2}


# ════════════════ GIA QUY gợi ý ════════════════
def _gia_quy(truc, bat_tu):
    gq = []
    if truc["ung_nhau"]:
        manh = "người 1" if truc["xu_huong_1"] == "cương" else "người 2"
        mem = "người 2" if manh == "người 1" else "người 1"
        gq.append(f"Việc lớn: {manh} (cương) ĐỀ XUẤT, {mem} (nhu) CÂN NHẮC & GIỮ NHỊP — cương ra ý, nhu định hướng.")
        gq.append(f"Đừng đảo vai: bắt {mem} quyết vội hay {manh} im lặng chịu đựng đều nghịch cấu trúc, dễ sinh hờn ngầm.")
    else:
        gq.append("Phân vai rõ: mỗi mảng việc cử MỘT người chủ trì, người kia hậu thuẫn — tránh hai cái cùng cương va nhau hoặc cùng nhu bỏ trống.")
    if bat_tu.get("luc_hai", 0) or bat_tu.get("luc_xung", 0):
        gq.append("Tranh luận có luật: nói thẳng ngay, giải quyết trong ngày, KHÔNG để giận qua đêm (hóa giải lục hại = hờn ngấm).")
    chung = set(bat_tu.get("dung_than_1") or []) & set(bat_tu.get("dung_than_2") or [])
    if chung:
        gq.append(f"Cùng cần hành {', '.join(chung)}: dồn sức vào một hướng chung (sự nghiệp/nhà cửa chung) — cả hai cùng được nuôi.")
    gq.append("Lời có thực chất: hứa thì giữ, nói thì thật (đạo Gia Nhân) — đây là nền của mọi nếp nhà.")
    gq.append("Việc lặp có phép thường: lịch sinh hoạt, tài chính, giỗ tết cố định — trật tự là chỗ dựa cho cả hai.")
    return gq


# ════════════════ NGHỀ NGHIỆP ĐÔI BÊN ════════════════
_QL_NGHE = {
    "tu_vi": "lãnh đạo, quản lý cấp cao, ngành lớn/nhà nước, vị trí 'cầm trịch'",
    "thien_co": "tư vấn, lên kế hoạch, kỹ thuật, nghiên cứu, môi giới, IT",
    "thai_duong": "ngành công khai — giáo dục, truyền thông, chính trị, đối ngoại, quảng bá",
    "vu_khuc": "tài chính, ngân hàng, kế toán, kỹ thuật/cơ khí, kinh doanh thực tế",
    "thien_dong": "dịch vụ, ẩm thực, giải trí, phúc lợi, công việc nhẹ nhàng sáng tạo",
    "liem_trinh": "pháp luật, công nghệ, kỷ luật (quân/cảnh), hoặc nghệ thuật cá tính",
    "thien_phu": "quản lý tài sản, kho vận, hành chính, tài chính ổn định",
    "thai_am": "bất động sản, tài chính, chăm sóc, nghệ thuật, nghiên cứu thầm lặng",
    "tham_lang": "kinh doanh giao tế, marketing, giải trí, ngành 'hot', đa nghề",
    "cu_mon": "nghề dùng lời — luật sư, giảng dạy, bán hàng, truyền thông, ẩm thực",
    "thien_tuong": "trợ lý, hành chính, dịch vụ, tư vấn, thời trang, ngành chăm lo",
    "thien_luong": "y dược, giáo dục, từ thiện, giám sát, tư vấn, tâm linh",
    "that_sat": "kinh doanh quyết liệt, kỹ thuật, khởi nghiệp, ngành nặng/độc lập",
    "pha_quan": "nghề biến động/tiên phong, kỹ thuật, vận tải, sáng tạo phá cách, tự do",
}
_LAM_CHU = {"tu_vi", "vu_khuc", "that_sat", "pha_quan", "tham_lang", "thai_duong"}


def _nghe_1(ls):
    fn = ls.get("fn_to_chi") or {}
    raw = fn.get("quan_loc")
    sao = (ls.get("chinh_tinh_per_palace") or {}).get(raw) or []
    nghe = [_QL_NGHE[s] for s in sao if s in _QL_NGHE]
    lam_chu = any(s in _LAM_CHU for s in sao)
    if not sao:
        return {"sao": [], "nghe": ["Quan Lộc vô chính diệu — nghề đa dạng, dễ đổi nghề; nên theo sở trường thực tế"],
                "thien_huong": "linh hoạt"}
    return {"sao": [_SAO_VI.get(s, s) for s in sao], "nghe": nghe,
            "thien_huong": "thiên làm chủ / tự lập" if lam_chu else "thiên hợp tác / phụ tá"}


def _nghe_doi_ben(ls1, ls2):
    n1, n2 = _nghe_1(ls1), _nghe_1(ls2)
    c1 = "chu" if "làm chủ" in n1["thien_huong"] else "tro"
    c2 = "chu" if "làm chủ" in n2["thien_huong"] else "tro"
    if c1 == "chu" and c2 == "chu":
        gt = "Cả hai đều thiên làm chủ — nếu cùng làm ăn phải PHÂN VAI rõ (ai quyết mảng nào), kẻo 'hai vua một nước'."
    elif c1 != c2:
        gt = "Một người thiên dẫn dắt, một người thiên phụ trợ — bổ nhau tốt, dễ thành một ê-kíp ăn ý."
    else:
        gt = "Cả hai thiên hợp tác/phụ tá — êm, nhưng cần một người dám đứng mũi khi việc lớn."
    return {"nguoi1": n1, "nguoi2": n2, "doi_ben": gt}


# ════════════════ CON CÁI CÓ KHỚP KHÔNG (Tử Tức 2 lá) ════════════════
def _tu_tuc_khop(ls1, ls2):
    fn1 = (ls1.get("fn_to_chi") or {}); fn2 = (ls2.get("fn_to_chi") or {})
    raw1, raw2 = fn1.get("tu_tuc"), fn2.get("tu_tuc")
    chi1, chi2 = _norm_chi(raw1), _norm_chi(raw2)
    sao1 = set((ls1.get("chinh_tinh_per_palace") or {}).get(raw1) or [])
    sao2 = set((ls2.get("chinh_tinh_per_palace") or {}).get(raw2) or [])
    chung = sao1 & sao2
    loai, nhan = _rel_chi(chi1, chi2) if (chi1 and chi2) else ("trung", "")
    diem = 50
    khop = False
    if loai == "đồng":
        diem = 90; khop = True
        gt = "Hai cung Con Cái ĐỒNG CHI (trùng khít) — quan niệm nuôi dạy con rất đồng điệu. Điểm cộng lớn."
    elif loai in ("hop", "tam_hop"):
        diem = 78; khop = True
        gt = f"Hai cung Con Cái {nhan} — hòa hợp trong chuyện con cái, dễ cùng hướng."
    elif loai == "xung":
        diem = 38
        gt = "Hai cung Con Cái lục xung — quan điểm nuôi dạy con dễ lệch, cần thống nhất sớm."
    elif loai == "hai":
        diem = 44
        gt = "Hai cung Con Cái lục hại — có chỗ vênh ngấm về con cái, nên nói rõ kỳ vọng."
    else:
        gt = "Hai cung Con Cái trung tính — không đặc biệt hợp hay nghịch."
    if chung:
        diem = min(100, diem + 8)
        gt += f" Lại cùng có sao {', '.join(_SAO_VI.get(s, s) for s in chung)} ở cung Con Cái — thêm điểm đồng điệu."
    return {"chi_nguoi1": chi1, "chi_nguoi2": chi2,
            "sao_nguoi1": [_SAO_VI.get(s, s) for s in sao1], "sao_nguoi2": [_SAO_VI.get(s, s) for s in sao2],
            "sao_chung": [_SAO_VI.get(s, s) for s in chung], "quan_he": nhan,
            "khop": khop, "diem": diem, "ghi_chu": gt}


# ════════════════ NĂM HỢP CƯỚI (đào hoa vận cặp) ════════════════
def nam_hop_cuoi(ls1, by1, ls2, by2, nam_xem, n_nam=10) -> dict:
    """Năm nào sao hỉ chiếu Mệnh/Phu Thê của MỘT hoặc CẢ HAI → cửa sổ cưới.

    Cả hai cùng sáng = năm đậm nhất.
    """
    from engine.tu_vi.duyen import dao_hoa_van
    d1 = {x["nam"]: x for x in dao_hoa_van(ls1, by1, nam_xem, n_nam)["nam_co_duyen"]}
    d2 = {x["nam"]: x for x in dao_hoa_van(ls2, by2, nam_xem, n_nam)["nam_co_duyen"]}
    nam = []
    for y in range(nam_xem, nam_xem + n_nam):
        a, b = d1.get(y), d2.get(y)
        if not a and not b:
            continue
        ca_hai = bool(a and b)
        nam.append({
            "nam": y, "ca_hai": ca_hai,
            "nguoi1": (a["cung"] if a else []), "nguoi2": (b["cung"] if b else []),
            "do_dam": "đậm (cả hai cùng sáng)" if ca_hai else "vừa (một người sáng)",
        })
    nam.sort(key=lambda x: (not x["ca_hai"], x["nam"]))
    return {"tu_nam": nam_xem, "den_nam": nam_xem + n_nam - 1, "nam": nam,
            "ghi_chu": "Năm cả hai cùng có sao hỉ chiếu Mệnh/Phu Thê = cửa sổ cưới đậm nhất. "
                       "Là XU HƯỚNG thuận, không phải ngày giờ định — vẫn do hai người quyết."}


# ════════════════ TỔNG HỢP ════════════════
def phan_tich_hop_hon(ls1, pillars1, que1, ls2, pillars2, que2,
                      ten1="Người 1", ten2="Người 2") -> dict:
    tv = _tu_vi_compat(ls1, ls2)
    bt = _bat_tu_compat(pillars1, pillars2)
    hl = _ha_lac_compat(que1, que2)
    truc = _truc_cuong_nhu(ls1, pillars1, que1, ls2, pillars2, que2)
    nghe = _nghe_doi_ben(ls1, ls2)
    tu_tuc = _tu_tuc_khop(ls1, ls2)

    # Điểm tổng: trục cương–nhu trọng số cao nhất; con cái khớp = điểm cộng nhẹ
    diem_tong = round(truc["diem"] * 0.38 + tv["diem"] * 0.24 + bt["diem"] * 0.24
                      + hl["diem"] * 0.08 + tu_tuc["diem"] * 0.06)
    diem_tong = max(0, min(100, diem_tong))
    if diem_tong >= 78: muc = "Tương ứng cao — duyên có nhiều chốt khóa"
    elif diem_tong >= 62: muc = "Tương ứng khá — hợp nhiều, vài chỗ cần chăm"
    elif diem_tong >= 48: muc = "Tương ứng vừa — vừa hợp vừa va, cần nề nếp"
    else: muc = "Cần dụng công nhiều — khác biệt lớn, vun đắp bằng ý thức"

    khoa = []
    cho_giu = []
    for blk in (tv, bt, hl):
        for loai, msg in blk.get("nhan_xet", []):
            if loai == "+":
                khoa.append(msg)
            elif loai == "-":
                cho_giu.append(msg)
    if truc["ung_nhau"]:
        khoa.insert(0, "TRỤC CƯƠNG–NHU ứng nhau (điểm bền nhất): " + truc["giai_thich"])
    else:
        cho_giu.insert(0, truc["giai_thich"])
    if tu_tuc["khop"]:
        khoa.append("Con cái: " + tu_tuc["ghi_chu"])

    return {
        "ten1": ten1, "ten2": ten2,
        "diem_tong": diem_tong, "muc": muc,
        "truc_cuong_nhu": truc,
        "tu_vi": tv, "bat_tu": bt, "ha_lac": hl,
        "nghe_nghiep": nghe, "con_cai": tu_tuc,
        "khoa_duyen": khoa, "cho_phai_giu": cho_giu,
        "gia_quy": _gia_quy(truc, bt),
        "huong_dan": [
            "Điểm số là độ TƯƠNG ỨNG của cấu trúc, KHÔNG phải xác suất hạnh phúc. Duyên là việc hai người vận hành mỗi ngày.",
            "Đọc cả hai cột: 'Khóa duyên' (chỗ trời cho sẵn) và 'Chỗ phải giữ' (bài tập chung). Cặp bền là cặp biết chăm cột thứ hai.",
            "Trục Cương–Nhu quan trọng nhất: duyên bền không vì hai người GIỐNG nhau, mà vì ỨNG nhau — một âm một dương.",
            "Bộ Gia Quy là gợi ý rút từ chính hai lá số — hãy bàn cùng nhau rồi điều chỉnh cho hợp nhà mình.",
        ],
        "paradigm": "Đọc đồng dạng, không bói. Mệnh là động từ: lá số mở cửa, người bước qua.",
    }
