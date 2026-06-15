"""Món chính — luận theo CHỦ ĐỀ ĐỜI SỐNG (Anh chốt 2026-06-13 'vào main').

Khách Việt hỏi theo câu chuyện đời ('đường công danh?', 'tình duyên?'), không
hỏi theo 'cung'. Mỗi chủ đề gom TAM HỢP CUNG liên quan thành 1 bài luận riêng,
nói ngôn ngữ đời thường — chữ 'cung' là hậu trường.

Lazy: user bấm món nào, engine gom atoms các cung liên quan + bộ phụ tinh +
cách cục + Tứ Hóa của chúng → LLM luận 1 bài.
"""
from __future__ import annotations

# slug → {tên hiển thị, icon, cung chính, cung phụ (liên quan), mô tả khách}
CHU_DE = {
    "su_nghiep": {
        "ten": "Sự nghiệp & công danh", "icon": "💼",
        "cung_chinh": "quan_loc",
        "cung_lien_quan": ["quan_loc", "menh", "tai_bach", "thien_di"],
        "goc_nhin": "con đường công danh, năng lực làm việc, hợp nghề gì, thăng tiến hay nên tự lập, môi trường hợp",
    },
    "tinh_duyen": {
        "ten": "Tình duyên & hôn nhân", "icon": "💕",
        "cung_chinh": "phu_the",
        "cung_lien_quan": ["phu_the", "menh", "phuc_duc"],
        "goc_nhin": "chuyện tình cảm – hôn nhân, kiểu người bạn đời, duyên sớm hay muộn, cách giữ gìn hạnh phúc",
    },
    "tai_loc": {
        "ten": "Tài lộc & của cải", "icon": "💰",
        "cung_chinh": "tai_bach",
        "cung_lien_quan": ["tai_bach", "dien_trach", "phuc_duc", "quan_loc"],
        "goc_nhin": "khả năng kiếm tiền và giữ tiền, cách tài đến, nhà cửa đất đai, phúc về của cải",
    },
    "suc_khoe": {
        "ten": "Sức khỏe & thân tâm", "icon": "🍀",
        "cung_chinh": "tat_ach",
        "cung_lien_quan": ["tat_ach", "menh", "phuc_duc"],
        "goc_nhin": "tạng người, chỗ cần giữ gìn sức khỏe, thân – tâm, cách dưỡng sinh hợp",
    },
    "gia_dao": {
        "ten": "Gia đạo (cha mẹ – vợ chồng – con cái – anh em)", "icon": "👨‍👩‍👧",
        "cung_chinh": "phu_mau",
        "cung_lien_quan": ["phu_mau", "phu_the", "tu_tuc", "huynh_de", "no_boc"],
        "goc_nhin": "mối duyên với cha mẹ, vợ/chồng, con cái, anh em – bạn bè; nề nếp và phúc ấm gia đình",
    },
}

_CUNG_VI = {"menh": "Mệnh", "phu_the": "Phu Thê", "tai_bach": "Tài Bạch",
            "quan_loc": "Quan Lộc", "thien_di": "Thiên Di", "phuc_duc": "Phúc Đức",
            "tat_ach": "Tật Ách", "dien_trach": "Điền Trạch", "no_boc": "Nô Bộc",
            "huynh_de": "Huynh Đệ", "tu_tuc": "Tử Tức", "phu_mau": "Phụ Mẫu"}


def gom_chu_de(chu_de: str, la_so_input: dict, three_layer: dict) -> dict | None:
    """Gom toàn bộ dữ kiện các cung liên quan 1 chủ đề → context cho LLM.

    Returns: {slug, ten, icon, goc_nhin, cung_data: [{cung, cung_vi, sao, atoms}],
              bo_phu_tinh: [...], cach_cuc_lq: [...], tu_hoa_lq: [...]}
    """
    spec = CHU_DE.get(chu_de)
    if not spec:
        return None
    lop3 = three_layer.get("lop_3_sach_co", {})
    per = lop3.get("per_palace", {})
    bo_all = lop3.get("bo_phu_tinh_per_palace", {})
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    lq = spec["cung_lien_quan"]

    cung_data = []
    for cung in lq:
        pd = per.get(cung)
        if not pd:
            continue
        sao = list(pd.get("stars") or [])
        atoms = []
        for star, cv in (pd.get("cross_views") or {}).items():
            for school, ats in (cv.get("schools") or {}).items():
                for a in ats[:1]:
                    vt = a.get("viet_thuan") or a.get("source_quote")
                    if vt:
                        atoms.append({"sao": star, "school": school, "text": vt[:200]})
        cung_data.append({"cung": cung, "cung_vi": _CUNG_VI.get(cung, cung),
                          "la_chinh": cung == spec["cung_chinh"], "sao": sao, "atoms": atoms[:6]})

    # Bộ phụ tinh của các cung liên quan (qua chi)
    bo_lq = []
    for cung in lq:
        chi = fn_to_chi.get(cung)
        for b in (bo_all.get(chi) or []):
            if b.get("du_cap") or b.get("loai") in ("sat", "hung"):
                bo_lq.append({"cung_vi": _CUNG_VI.get(cung, cung), **b})

    # Tứ Hóa rơi vào cung liên quan
    tu_hoa_lq = [t for t in (la_so_input.get("tu_hoa") or []) if t.get("palace_fn") in lq]

    return {
        "slug": chu_de, "ten": spec["ten"], "icon": spec["icon"],
        "goc_nhin": spec["goc_nhin"],
        "cung_data": cung_data, "bo_phu_tinh": bo_lq[:6], "tu_hoa_lq": tu_hoa_lq,
    }
