"""Gia Đạo — bộ tính năng cho người ĐÃ CƯỚI (Anh chốt goal 2026-06-16).

Khác Gieo Duyên (tìm duyên mới): Gia Đạo = cưới rồi → ăn ở hợp đạo, sinh con, đặt tên.
- gia_quy_an_o(ls1, ls2): nếp nhà hợp cấu trúc cặp (đạo Gia Nhân + Hằng).
- nam_sinh_con(ls_me, by, nam_xem, n): năm thuận đón con (sao hỉ chiếu Tử Tức/Mệnh).
- dat_ten_con(pillars_con): Bát Tự con → dụng thần → gợi ý hành bổ + chữ/tên mẫu.

Paradigm: đọc đồng dạng, không predict. Mệnh là động từ.
"""
from __future__ import annotations

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
_CANON = {"ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn", "ti": "Tỵ",
          "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi"}


def _norm(c):
    return _CANON.get(c, c)


# ════════ 1. GIA QUY ĂN Ở HỢP ĐẠO ════════
def gia_quy_an_o(ls1, ls2, ten1="Vợ/Chồng 1", ten2="Vợ/Chồng 2") -> dict:
    """Nếp nhà rút từ trục cương–nhu của cặp + đạo Gia Nhân (mỗi người đúng vị) + Hằng (bền)."""
    from engine.tu_vi.hop_hon import _truc_cuong_nhu, _bat_tu_compat, _gia_quy
    # cần pillars + quẻ? _truc_cuong_nhu cần pillars+que; ở đây chỉ có ls.
    # Dùng phiên bản nhẹ: cương–nhu từ chính tinh Mệnh (đủ cho gia quy).
    from engine.tu_vi.hop_hon import SAO_CUONG, SAO_NHU

    def _cuong(ls):
        ct = ls.get("chinh_tinh_per_palace") or {}
        msao = ct.get(ls.get("menh_palace")) or []
        nc = sum(1 for x in msao if x in SAO_CUONG)
        nn = sum(1 for x in msao if x in SAO_NHU)
        return "cương" if nc > nn else ("nhu" if nn > nc else "cân")

    x1, x2 = _cuong(ls1), _cuong(ls2)
    gq = []
    # đạo Gia Nhân: mỗi người đúng vị
    gq.append("Mỗi người đúng vị (đạo Gia Nhân): phân rõ ai lo 'trong' (nề nếp, con cái, tay hòm), "
              "ai lo 'ngoài' (đối ngoại, sự nghiệp) — không giẫm chân là yên nửa nhà.")
    if {x1, x2} == {"cương", "nhu"}:
        manh = ten1 if x1 == "cương" else ten2
        mem = ten2 if manh == ten1 else ten1
        gq.append(f"Việc lớn: {manh} (cương) đề xuất, {mem} (nhu) cân nhắc & giữ nhịp — cương ra ý, nhu định hướng (cương nhu giai ứng).")
    elif x1 == x2 == "cương":
        gq.append("Cả hai cùng cương: chia 'lãnh địa' rõ ràng, việc của ai người đó quyết — tránh 'hai vua một nước'.")
    elif x1 == x2 == "nhu":
        gq.append("Cả hai cùng nhu: luân phiên đứng mũi chịu sào, đừng cùng chờ người kia quyết.")
    gq.append("Lời có thực chất (Gia Nhân: 'ngôn hữu vật'): hứa thì giữ, nói thì thật — nền của mọi nếp nhà.")
    gq.append("Tranh luận có luật: nói thẳng ngay, giải quyết trong ngày, không để giận qua đêm.")
    gq.append("Việc lặp có phép thường (quẻ Hằng): lịch sinh hoạt, tài chính, giỗ tết, dạy con — định thành nếp cố định.")
    return {
        "cuong_nhu": {"nguoi1": x1, "nguoi2": x2},
        "gia_quy": gq,
        "tinh_than": "Đạo Gia Nhân: 'trong nhà chính thì thiên hạ chính'. Quẻ Hằng: cảm rồi thì giữ cho bền. "
                     "Gia quy không để áp đặt, mà để mỗi người đúng vị thì cả nhà yên.",
    }


# ════════ 2. NĂM THUẬN ĐÓN CON ════════
def _hong_loan_idx(yb):
    return (3 - CHI.index(yb)) % 12


def nam_sinh_con(ls_me, birth_year, nam_xem, n_nam=10) -> dict:
    """Năm sao hỉ (Thiên Hỷ/Hồng Loan) chiếu cung Tử Tức hoặc Mệnh → thuận đón con.

    Tính theo lá người được xem (thường là mẹ). Là XU HƯỚNG, không phải lịch định.
    """
    fn = ls_me.get("fn_to_chi") or {}
    menh_i = CHI.index(_norm(ls_me.get("menh_palace")))
    tt_raw = fn.get("tu_tuc")
    tt_i = CHI.index(_norm(tt_raw)) if _norm(tt_raw) in CHI else None
    nam = []
    for y in range(nam_xem, nam_xem + n_nam):
        yb = CHI[(y - 4) % 12]
        hl = _hong_loan_idx(yb)
        th = (hl + 6) % 12
        hits = []
        if tt_i is not None and (hl == tt_i or th == tt_i):
            hits.append("Tử Tức")
        if hl == menh_i or th == menh_i:
            hits.append("Mệnh")
        if hits:
            nam.append({"nam": y, "tuoi_mu": y - birth_year + 1, "cung": hits,
                        "sao": "Thiên Hỷ" if (th == tt_i or th == menh_i) else "Hồng Loan"})
    return {"tu_nam": nam_xem, "den_nam": nam_xem + n_nam - 1, "nam": nam,
            "ghi_chu": "Năm sao hỉ chiếu cung Con Cái / Mệnh = khí 'hỉ sự' thuận cho việc sinh nở. "
                       "Là XU HƯỚNG đồng dạng, KHÔNG phải chọn ngày — sức khỏe & y khoa vẫn là chính."}


# ════════ 3. ĐẶT TÊN CON BỔ NGŨ HÀNH ════════
HANH_TEN = {
    "Mộc": {"y_nghia": "cây cối, sinh trưởng, nhân ái, sáng tạo",
            "bo_thu": "木 (mộc), 艹 (thảo)",
            "goi_y": ["Lâm", "Tùng", "Bách", "Thanh", "Quân", "Nhã", "Linh", "Vỹ", "Kha", "Chi"]},
    "Hỏa": {"y_nghia": "ánh sáng, ấm áp, nhiệt thành, lễ nghĩa",
            "bo_thu": "火 (hỏa), 日 (nhật)",
            "goi_y": ["Minh", "Quang", "Huy", "Hồng", "Đăng", "Diễm", "Nhật", "Dương", "Ánh", "Hạ"]},
    "Thổ": {"y_nghia": "đất đai, vững vàng, thành tín, bao dung",
            "bo_thu": "土 (thổ), 山 (sơn)",
            "goi_y": ["Sơn", "Thành", "Cương", "An", "Khuê", "Duy", "Điền", "Khang", "Phong", "Vân"]},
    "Kim": {"y_nghia": "kim loại, sắc bén, quý giá, quyết đoán, nghĩa khí",
            "bo_thu": "金 (kim)",
            "goi_y": ["Kim", "Ngân", "Tích", "Chung", "Tú", "Bảo", "Thuần", "Cẩm", "Thiết", "Tân"]},
    "Thủy": {"y_nghia": "nước, linh hoạt, trí tuệ, mềm mại, lưu thông",
             "bo_thu": "水 / 氵 (thủy)",
             "goi_y": ["Hà", "Giang", "Hải", "Tuyền", "Vũ", "Băng", "Khê", "Hàm", "Thủy", "Mạnh"]},
}


def dat_ten_con(pillars_con: dict) -> dict:
    """Bát Tự con → dụng thần (hành cần bổ) → gợi ý chữ/tên mang hành đó."""
    from engine.tu_vi.hop_hon import _pillars_list, _dung_than, _element_counts, CAN_NH

    pl = _pillars_list(pillars_con)
    if len(pl) < 4:
        return {"error": "Cần đủ ngày + giờ sinh của bé để tính dụng thần."}
    dung, tag, day_el = _dung_than(pl)
    cnt = _element_counts(pl)
    thieu = sorted(cnt, key=lambda k: cnt[k])  # hành ít nhất trước
    # Hành nên bổ = dụng thần (ưu tiên), giao với hành thiếu nếu có
    nen_bo = dung[:2]
    goi_y = []
    for h in nen_bo:
        if h in HANH_TEN:
            goi_y.append({"hanh": h, **HANH_TEN[h]})
    return {
        "nhat_chu": pl[2][0], "nhat_chu_hanh": day_el, "than": tag,
        "ngu_hanh_co": cnt, "hanh_thieu_nhat": thieu[0],
        "hanh_nen_bo": nen_bo,
        "goi_y_ten": goi_y,
        "ghi_chu": "Đặt tên theo phép cổ là BỔ DỤNG THẦN (hành lá số bé cần), không chỉ bổ hành thiếu. "
                   "Đây là GỢI Ý hành + chữ mẫu — tên hay còn cần hợp họ, âm vần, ý nghĩa và mong muốn của cha mẹ.",
    }


# ════════ 4. LUẬN LÁ SỐ CON CÁI (founder chốt 2026-06-18) ════════
# Đọc cái NỀN bé được trao (THỂ), KHÔNG phán định đời bé (DỤNG). Thận trọng vì là trẻ em.
# "Mô hình hình thành con người": con = trường năng lượng lúc sinh ⊗ gen bố mẹ ⊗ môi trường.

# 14 chính tinh → lăng kính TRẺ: khí chất bẩm + hướng nuôi dưỡng (không phán số).
SAO_TRE = {
    "tu_vi": ("Tử Vi", "có chủ kiến, thích được tôn trọng, khí 'đầu đàn'",
              "cho bé vai trò nhỏ để dẫn dắt; dạy khiêm nhường, đừng đè ép cái tự tôn."),
    "thien_co": ("Thiên Cơ", "nhanh trí, hiếu động, đầu óc hay xoay",
                 "cho câu đố, lắp ráp, kể chuyện; dạy kiên định kẻo 'cả thèm chóng chán'."),
    "thai_duong": ("Thái Dương", "sáng, nhiệt, hướng ngoại, hào phóng",
                   "khuyến khích hoạt động nhóm, thể thao; dạy bé giữ sức, biết nghỉ."),
    "vu_khuc": ("Vũ Khúc", "cương nghị, thực tế, thích rõ ràng, sớm biết tính toán",
                "dạy mềm mỏng & nói ra cảm xúc; khen cả nỗ lực, không chỉ kết quả."),
    "thien_dong": ("Thiên Đồng", "hồn nhiên, vui, dễ thương, ưa an nhàn",
                   "khích lệ tự cố gắng, giao việc nhỏ vừa sức, tránh nuông để bé ỷ lại."),
    "liem_trinh": ("Liêm Trinh", "cá tính mạnh, nguyên tắc riêng, cảm xúc nồng",
                   "kênh năng lượng vào kỷ luật tích cực (võ, nhạc, đội nhóm); lắng nghe bé."),
    "thien_phu": ("Thiên Phủ", "điềm, biết giữ, độ lượng, hơi thận trọng",
                  "khuyến khích thử cái mới, bớt rụt rè; cho bé cảm giác an toàn để bước ra."),
    "thai_am": ("Thái Âm", "dịu, tình cảm, mơ mộng, yêu cái đẹp",
                "nuôi mạch nghệ thuật (vẽ, nhạc, văn); dạy mạnh dạn, bớt giữ trong lòng."),
    "tham_lang": ("Tham Lang", "đa tài, ham vui, hiếu kỳ, khéo giao tế",
                  "hướng đam mê vào việc có ích; dạy chuyên nhất một thứ tới nơi."),
    "cu_mon": ("Cự Môn", "tò mò, hay hỏi 'tại sao', miệng lưỡi, đôi khi hoài nghi",
               "trả lời bé thật lòng; dạy lời nói thiện, dùng cái miệng để kết bạn."),
    "thien_tuong": ("Thiên Tướng", "trung hậu, biết điều, thích giúp người, trọng lễ",
                    "trân trọng tấm lòng bé; nhưng dạy bé tự lo cho mình nữa, đừng quên mình."),
    "thien_luong": ("Thiên Lương", "già dặn trước tuổi, có lòng che chở, ưa lý lẽ",
                    "cho bé được làm trẻ con, bớt ôm việc người lớn; nuôi lòng nhân sẵn có."),
    "that_sat": ("Thất Sát", "mạnh mẽ, độc lập, quyết đoán, ưa thử thách",
                 "cho không gian + ranh giới rõ ràng; dạy nhẫn, biến gan lì thành bản lĩnh."),
    "pha_quan": ("Phá Quân", "phá cách, tiên phong, không thích lối mòn",
                 "cho đất sáng tạo + hướng dẫn nhất quán; biến 'phá' thành 'đổi mới có ích'."),
}

CUNG_TRE = {
    "menh": "Bản tính & khí chất bé",
    "phu_mau": "Duyên với cha mẹ & người trên (thầy cô, quý nhân) — cũng là nẻo học hỏi",
    "phuc_duc": "Phúc ấm & tâm an — cái bé hưởng từ gốc nhà",
    "tat_ach": "Thân thể — chỗ nên để ý chăm (cái NỀN, không phải bệnh án)",
    "huynh_de": "Anh chị em & bạn bè — cách bé nương tựa, kết bạn",
    "quan_loc": "Nẻo học & việc về sau — mầm thiên hướng",
}

_SINH_NH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
_KHAC_NH = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}
VAN_TINH = {"van_xuong": "Văn Xương", "van_khuc": "Văn Khúc", "hoa_khoa": "Hóa Khoa"}


def _doc_cung_tre(ls, fn):
    """Đọc 1 cung theo lăng kính trẻ: chính tinh → khí chất + hướng nuôi."""
    ct = ls.get("chinh_tinh_per_palace") or {}
    fn2chi = ls.get("fn_to_chi") or {}
    chi = fn2chi.get(fn)
    sao = ct.get(fn) or (ct.get(chi) if chi else None) or []
    sao = [s for s in sao if s in SAO_TRE]
    if not sao:
        return {"cung": CUNG_TRE[fn], "chi": chi, "chinh_tinh": [],
                "vo_chinh_dieu": True,
                "khi_chat": "Vô chính diệu — bé chưa lộ nét đậm ở mặt này; "
                            "nét sẽ rõ dần theo môi trường & người bé gần.",
                "nuoi": "Cho bé hình mẫu rõ ràng để soi (cha mẹ, thầy, sách) — "
                        "môi trường định hình mạnh ở cung vô chính diệu."}
    return {
        "cung": CUNG_TRE[fn], "chi": chi, "vo_chinh_dieu": False,
        "chinh_tinh": [SAO_TRE[s][0] for s in sao],
        "khi_chat": "; ".join(SAO_TRE[s][1] for s in sao),
        "nuoi": " ".join(SAO_TRE[s][2] for s in sao),
    }


def _doc_van_tinh(ls):
    """Văn tinh (Xương/Khúc/Hóa Khoa) chiếu Mệnh/Quan/Phụ Mẫu → duyên chữ nghĩa."""
    pt = ls.get("phu_tinh_per_palace") or {}
    fn2chi = ls.get("fn_to_chi") or {}
    found = []
    for fn in ("menh", "quan_loc", "phu_mau"):
        chi = fn2chi.get(fn)
        stars = set((pt.get(fn) or []) + ((pt.get(chi) or []) if chi else []))
        hit = [VAN_TINH[s] for s in stars if s in VAN_TINH]
        if hit:
            found.append({"cung": CUNG_TRE.get(fn, fn), "van_tinh": hit})
    if not found:
        return None
    return {"co_van_tinh": True, "chi_tiet": found,
            "luan": "Có văn tinh chiếu việc học → bé có DUYÊN chữ nghĩa / thi cử. "
                    "Là thiên hướng cần VUN (đọc sách cùng bé, khen sự tìm tòi), không phải bảo đảm."}


def _doi_chieu_bo_me(child_dung, child_day_el, parents):
    """Trường năng lượng bố mẹ ⊗ cái con CẦN (dụng thần). Hướng nuôi, KHÔNG phán bố mẹ tốt/xấu cho con."""
    need = child_dung[0] if child_dung else child_day_el
    out = []
    for p in parents:
        el = p.get("hanh")
        vai = p.get("vai", "Cha/Mẹ")
        if not el:
            continue
        if el == need:
            rel, loi = "đồng khí", (f"{vai} cùng hành **{el}** với cái con cần → đồng khí, củng cố "
                                    f"cái bé vốn cần. Gần {vai.lower()}, bé được tiếp thêm đúng nguồn.")
        elif _SINH_NH.get(el) == need:
            rel, loi = "sinh con", (f"{vai} hành **{el}** SINH ra hành con cần (**{need}**) → "
                                    f"{vai.lower()} là NGUỒN nuôi cái bé thiếu. Đây là chỗ dựa lớn cho bé.")
        elif _KHAC_NH.get(el) == need:
            rel, loi = "khắc nhẹ", (f"{vai} hành **{el}** khắc hành con cần (**{need}**) — KHÔNG phải xấu; "
                                    f"chỉ là mặt đó {vai.lower()} nên DỊU & kiên nhẫn, đừng ép cái con vốn yếu.")
        elif _SINH_NH.get(need) == el:
            rel, loi = "con sinh bố mẹ", (f"Hành con cần (**{need}**) lại SINH cho {vai.lower()} (**{el}**) → "
                                         f"bé hay 'lo ngược' cho {vai.lower()}; nhớ để bé được là trẻ con.")
        else:
            rel, loi = "trung tính", (f"{vai} hành **{el}** — tương quan êm với cái con cần (**{need}**); "
                                      f"giữ nếp đồng hành là đủ.")
        out.append({"vai": vai, "hanh": el, "quan_he": rel, "loi": loi})
    return {"con_can": need, "doi_chieu": out,
            "ghi_chu": "Đây là cách đọc TRƯỜNG NĂNG LƯỢNG (con = năng lượng sinh ⊗ gen bố mẹ ⊗ môi trường), "
                       "để biết hướng NUÔI — không phải chấm điểm bố mẹ hợp/khắc con."}


def luan_la_so_con(child_ls, child_pillars, parents=None) -> dict:
    """Luận lá số con: lăng kính trẻ (6 cung) + Bát Tự dụng thần + đối chiếu trường khí bố mẹ.

    child_ls: la_so_input của bé (từ render_from_birth).
    child_pillars: tứ trụ bé (từ extract_tu_tru) — để tính dụng thần.
    parents: [{"vai": "Bố"/"Mẹ", "hanh": "Mộc"}, ...] (hành nhật chủ bố mẹ), tuỳ chọn.
    """
    from engine.tu_vi.hop_hon import _pillars_list, _dung_than, _element_counts

    cung = [_doc_cung_tre(child_ls, fn)
            for fn in ("menh", "phu_mau", "phuc_duc", "tat_ach", "huynh_de", "quan_loc")]
    out = {
        "cung": cung,
        "van_tinh": _doc_van_tinh(child_ls),
        "paradigm": "Đọc cái NỀN bé được trao (khí chất, thân, phúc) để biết hướng DÌU DẮT — "
                    "KHÔNG phán định đời bé. Mệnh là dịch: bé sẽ lớn lên & tự viết phần DỤNG. "
                    "Thận trọng gấp đôi vì là trẻ em.",
    }
    pl = _pillars_list(child_pillars or {})
    if len(pl) >= 4:
        dung, tag, day_el = _dung_than(pl)
        cnt = _element_counts(pl)
        thieu = sorted(cnt, key=lambda k: cnt[k])
        out["bat_tu"] = {
            "nhat_chu": pl[2][0], "nhat_chu_hanh": day_el, "than": tag,
            "ngu_hanh_co": cnt, "hanh_thieu_nhat": thieu[0],
            "hanh_con_can": dung[:2],
            "huong_nuoi": f"Bé nhật chủ {pl[2][0]} ({day_el}), thân {tag}. "
                          f"Hướng vun bồi: thiên về hành {', '.join(dung[:2])} "
                          f"(môi trường, hoạt động, màu sắc, sự dìu dắt mang hành đó).",
        }
        if parents:
            out["truong_bo_me"] = _doi_chieu_bo_me(dung, day_el, parents)
    else:
        out["bat_tu"] = {"note": "Cần đủ ngày + giờ sinh của bé để tính dụng thần & hướng nuôi."}
    return out
