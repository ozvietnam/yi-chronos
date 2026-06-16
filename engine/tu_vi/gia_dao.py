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
