"""Adapter raw engine output → ``display.sections[]`` cho AppChat (2026-06-25).

App PRVchat render DATA-DRIVEN theo ``kind`` (cùng khuôn ``build_display`` của
tinh-duyen). Các món FREE Gieo Duyên (duyen / hop-hon / so-sanh) + sub-flow
(gieo-que / phac-hoa) đi qua đây để trả ``{meta, sections:[...]}`` ĐỒNG NHẤT —
KHÔNG luận lại, chỉ TRÌNH BÀY lại output engine đã có.

Kind dùng (khớp 11 kind app hỗ trợ):
- ``prose_list`` ``items:[{ten, noi_dung}]``
- ``list``       ``items:[{ten, noi_dung, tone}]``  (tone: the_manh|can_chu_y|trung_tinh)
- ``timeline``   ``items:[{loai, mo_ta, start_age, end_age}]``
- ``refs``       ``items:[str]``
"""
from __future__ import annotations

from typing import Any, Optional


def _sec(id_: str, icon: str, title: str, kind: str, **body: Any) -> dict:
    """Dựng 1 section chuẩn (id/icon/title/kind + body), kèm tom_tat mặc định = body
    cho renderer app (đã plain tiếng Việt → không cần tách can_cu)."""
    s: dict = {"id": id_, "icon": icon, "title": title, "kind": kind}
    s.update(body)
    s.setdefault("tom_tat", body.get("items") or body.get("data"))
    s.setdefault("can_cu", None)
    s.setdefault("mac_dinh_an", False)
    return s


def _txt(x: Any) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return x.get("noi_dung") or x.get("dien_dat") or x.get("text") or str(x)
    return str(x)


def _cg(x: Any) -> Optional[str]:
    return x.get("con_giap") if isinstance(x, dict) else (x if isinstance(x, str) else None)


# ─────────────────────────── Đang tìm (4 món FREE) ───────────────────────────
def build_duyen_display(raw: dict) -> dict:
    sections: list[dict] = []

    nk = raw.get("chan_dung_nua_kia") or {}
    chinh = nk.get("chinh_tinh") or []
    mo_ta = nk.get("mo_ta") or []
    if mo_ta or chinh:
        if chinh and len(chinh) == len(mo_ta):
            items = [{"ten": c, "noi_dung": m} for c, m in zip(chinh, mo_ta)]
        else:
            items = [{"ten": f"Nét {i + 1}", "noi_dung": m} for i, m in enumerate(mo_ta)]
        if nk.get("loi_khuyen"):
            items.append({"ten": "Lời khuyên", "noi_dung": nk["loi_khuyen"]})
        sub = nk.get("phu_the_chi_con_giap") or nk.get("phu_the_chi") or ""
        sections.append(_sec("nua_kia", "heart",
                             f"Chân dung nửa kia (Phu Thê: {sub})" if sub else "Chân dung nửa kia",
                             "prose_list", items=items))

    th = raw.get("tuoi_hop") or {}
    if th:
        items = []
        tam = ", ".join(t.get("con_giap") for t in (th.get("tam_hop") or []) if t.get("con_giap"))
        if tam:
            items.append({"ten": "Tam hợp", "noi_dung": tam, "tone": "the_manh"})
        if _cg(th.get("luc_hop")):
            items.append({"ten": "Lục hợp", "noi_dung": _cg(th["luc_hop"]), "tone": "the_manh"})
        if _cg(th.get("luc_xung")):
            items.append({"ten": "Lục xung (ý thức dung hòa)", "noi_dung": _cg(th["luc_xung"]), "tone": "can_chu_y"})
        if _cg(th.get("luc_hai")):
            items.append({"ten": "Lục hại", "noi_dung": _cg(th["luc_hai"]), "tone": "can_chu_y"})
        if items:
            cg = th.get("con_giap") or ""
            sections.append(_sec("tuoi_hop", "calendar",
                                 f"Tuổi hợp duyên (bạn: {cg})" if cg else "Tuổi hợp duyên",
                                 "list", items=items))

    dc = raw.get("duyen_ca_nhan") or {}
    items = []
    if dc.get("xu_huong"):
        items.append({"ten": "Xu hướng", "noi_dung": dc["xu_huong"]})
    for t in dc.get("tin_hieu") or []:
        ten = (t.get("loai") or "Tín hiệu").replace("_", " ").capitalize() if isinstance(t, dict) else "Tín hiệu"
        items.append({"ten": ten, "noi_dung": _txt(t)})
    for c in dc.get("cach_van_hanh") or []:
        items.append({"ten": "Cách vận hành", "noi_dung": _txt(c)})
    if items:
        sections.append(_sec("duong_duyen", "route", "Đường tình duyên", "prose_list", items=items))

    ncd = raw.get("nam_co_duyen") or {}
    yrs = ncd.get("nam_co_duyen") or []
    if yrs:
        items = []
        for y in yrs:
            cung = y.get("cung")
            cung_s = ", ".join(cung) if isinstance(cung, list) else (cung or "")
            mo = (y.get("sao") or "Sao hỉ") + (f" chiếu {cung_s}" if cung_s else "")
            items.append({"loai": "có duyên", "mo_ta": f"{y.get('nam', '')} — {mo}".strip(" —"),
                          "start_age": y.get("tuoi_mu"), "end_age": y.get("tuoi_mu")})
        sections.append(_sec("nam_co_duyen", "clock", "Năm có duyên (cửa sổ)", "timeline", items=items))

    return {"meta": {"mon": "duyen", "tuoi_mu": raw.get("tuoi_mu"), "gioi": raw.get("gioi"),
                     "paradigm": raw.get("paradigm")}, "sections": sections}


# ─────────────────────────── Đôi lứa ba hệ (FREE) ───────────────────────────
def build_hop_hon_display(raw: dict) -> dict:
    sections: list[dict] = []

    items = [{"ten": f"Điểm tương ứng: {raw.get('diem_tong', '?')}/100", "noi_dung": raw.get("muc") or ""}]
    tcn = raw.get("truc_cuong_nhu") or {}
    if tcn.get("giai_thich"):
        items.append({"ten": "Trục cương–nhu", "noi_dung": tcn["giai_thich"]})
    he = []
    for key, label in (("tu_vi", "Tử Vi"), ("bat_tu", "Bát Tự"), ("ha_lac", "Kinh Dịch")):
        d = (raw.get(key) or {}).get("diem")
        if d is not None:
            he.append(f"{label} {d}")
    if he:
        items.append({"ten": "Ba hệ chấm", "noi_dung": " · ".join(he)})
    sections.append(_sec("tong_quan", "heart-handshake", "Hợp đôi — tổng quan", "prose_list", items=items))

    if raw.get("khoa_duyen"):
        sections.append(_sec("khoa_duyen", "key", "Khóa duyên (điểm cộng hưởng)", "list",
                             items=[{"ten": "•", "noi_dung": _txt(k), "tone": "the_manh"} for k in raw["khoa_duyen"]]))
    if raw.get("cho_phai_giu"):
        sections.append(_sec("cho_phai_giu", "alert-triangle", "Chỗ phải giữ", "list",
                             items=[{"ten": "•", "noi_dung": _txt(k), "tone": "can_chu_y"} for k in raw["cho_phai_giu"]]))
    if raw.get("gia_quy"):
        sections.append(_sec("gia_quy", "home", "Gia quy (nếp nhà)", "list",
                             items=[{"ten": "•", "noi_dung": _txt(k), "tone": "trung_tinh"} for k in raw["gia_quy"]]))

    nhc = raw.get("nam_hop_cuoi") or {}
    yrs = nhc.get("nam") if isinstance(nhc, dict) else None
    if yrs:
        items = []
        for y in yrs:
            if isinstance(y, dict):
                items.append({"loai": "thuận cưới", "mo_ta": f"{y.get('nam', '')} — {y.get('dien_dat') or y.get('ghi_chu') or 'năm thuận'}".strip(" —")})
            else:
                items.append({"loai": "thuận cưới", "mo_ta": str(y)})
        if items:
            sections.append(_sec("nam_hop_cuoi", "calendar-heart", "Năm hợp cưới", "timeline", items=items))

    return {"meta": {"mon": "hop_hon", "diem_tong": raw.get("diem_tong"),
                     "paradigm": raw.get("paradigm")}, "sections": sections}


# ─────────────────────────── So nhiều người (FREE) ───────────────────────────
def build_so_sanh_display(raw: dict) -> dict:
    xh = raw.get("xep_hang") or []
    items = []
    for i, p in enumerate(xh):
        noi = (p.get("muc") or "")
        if p.get("diem_noi_bat"):
            noi = f"{noi} — {p['diem_noi_bat']}".strip(" —")
        items.append({
            "ten": f"#{i + 1} {p.get('ten', '')} · {p.get('diem_tong', '?')}đ"
                   + (" · ứng nhau" if p.get("ung_nhau") else ""),
            "noi_dung": noi,
            "tone": "the_manh" if i == 0 else "trung_tinh",
        })
    sections = [_sec("xep_hang", "trophy", "Xếp hạng tương ứng", "list", items=items)] if items else []
    if raw.get("ghi_chu"):
        sections.append(_sec("ghi_chu", "info-circle", "Lưu ý", "prose_list",
                             items=[{"ten": "Ghi chú", "noi_dung": raw["ghi_chu"]}]))
    return {"meta": {"mon": "so_sanh", "so_nguoi": len(xh)}, "sections": sections}


# ─────────────────────────── Gieo quẻ quyết định (0 xu) ───────────────────────
def build_gieo_que_display(raw: dict) -> dict:
    sections: list[dict] = []

    def _que_ten(q: Any) -> str:
        return q.get("ten_que") if isinstance(q, dict) else (q or "")

    items = []
    if raw.get("que_chinh"):
        items.append({"ten": "Quẻ chính", "noi_dung": _que_ten(raw["que_chinh"])})
    if raw.get("que_bien"):
        items.append({"ten": "Quẻ biến", "noi_dung": _que_ten(raw["que_bien"])})
    if raw.get("hao_dong") is not None:
        items.append({"ten": "Hào động", "noi_dung": str(raw["hao_dong"])})
    td = raw.get("the_dung") or {}
    if td.get("quan_he"):
        items.append({"ten": "Thể–Dụng", "noi_dung": td["quan_he"]})
    if items:
        sections.append(_sec("que", "yin-yang", "Quẻ gieo", "prose_list", items=items))

    if td.get("doc_dong_dang"):
        sections.append(_sec("doc_dong_dang", "eye", "Đọc đồng dạng", "prose_list",
                             items=[{"ten": "Soi tâm", "noi_dung": _txt(td["doc_dong_dang"])}]))

    bb = raw.get("bon_buoc")
    if bb:
        if isinstance(bb, dict):
            items = [{"ten": k.replace("_", " ").capitalize(), "noi_dung": _txt(v)} for k, v in bb.items() if v]
        else:
            items = [{"ten": f"Bước {i + 1}", "noi_dung": _txt(b)} for i, b in enumerate(bb)]
        if items:
            sections.append(_sec("bon_buoc", "list-numbers", "4 bước đoán quẻ", "prose_list", items=items))

    if raw.get("tam_phap"):
        sections.append(_sec("tam_phap", "heart", "Tâm pháp", "list",
                             items=[{"ten": "•", "noi_dung": _txt(t), "tone": "trung_tinh"} for t in raw["tam_phap"]]))

    return {"meta": {"mon": "gieo_que", "cau_hoi": raw.get("cau_hoi")}, "sections": sections}


# ─────────────────────────── Phác hoạ phối ngẫu (50 xu) ──────────────────────
_HOSO_LABELS = {
    "gioi_tinh_phoi_ngau": "Giới", "khuon_mat": "Khuôn mặt", "dang_nguoi": "Dáng người",
    "chieu_cao": "Chiều cao", "da": "Nước da", "mat": "Mắt", "mui": "Mũi", "mieng": "Miệng",
    "toc": "Tóc", "nghe": "Nghề", "phong_cach": "Phong cách", "bieu_cam": "Biểu cảm",
    "moi_truong": "Bối cảnh",
}


def build_phac_hoa_display(raw: dict) -> dict:
    """Phần TƯỚNG MẠO (text) thành sections; ẢNH giữ ở top-level ``image_b64`` của
    response (app render riêng — không có kind 'image' trong khuôn)."""
    ho_so = raw.get("ho_so") or {}
    items = [{"ten": lbl, "noi_dung": str(ho_so[key])}
             for key, lbl in _HOSO_LABELS.items() if ho_so.get(key)]
    sections = [_sec("tuong_mao", "user-circle", "Tướng mạo biểu tượng", "prose_list", items=items)] if items else []
    note = raw.get("disclaimer") or raw.get("image_note")
    if note:
        sections.append(_sec("luu_y", "alert-circle", "Lưu ý", "prose_list",
                             items=[{"ten": "Paradigm", "noi_dung": note}]))
    return {"meta": {"mon": "phac_hoa", "has_image": bool(raw.get("image_b64"))}, "sections": sections}
