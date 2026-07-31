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
                for a in ats[:2]:  # 2 atom/phái/sao (trước: 1) → dày dẫn chứng
                    vt = a.get("viet_thuan") or a.get("source_quote")
                    if vt:
                        atoms.append({"sao": star, "school": school,
                                      "atom_id": a.get("atom_id"), "text": vt[:360]})
        cung_data.append({"cung": cung, "cung_vi": _CUNG_VI.get(cung, cung),
                          "la_chinh": cung == spec["cung_chinh"], "sao": sao, "atoms": atoms[:10]})

    # Bộ phụ tinh của các cung liên quan (qua chi)
    bo_lq = []
    for cung in lq:
        chi = fn_to_chi.get(cung)
        for b in (bo_all.get(chi) or []):
            if b.get("du_cap") or b.get("loai") in ("sat", "hung"):
                bo_lq.append({"cung_vi": _CUNG_VI.get(cung, cung), **b})

    # Tứ Hóa rơi vào cung liên quan
    tu_hoa_lq = [t for t in (la_so_input.get("tu_hoa") or []) if t.get("palace_fn") in lq]

    out = {
        "slug": chu_de, "ten": spec["ten"], "icon": spec["icon"],
        "goc_nhin": spec["goc_nhin"],
        "cung_data": cung_data, "bo_phu_tinh": bo_lq[:6], "tu_hoa_lq": tu_hoa_lq,
    }
    # Chủ đề có cung Tử Tức (Gia đạo) → kèm bài đọc CON CÁI deterministic (nam-đẩu/bắc-đẩu cổ điển)
    # để ground LLM, tránh LLM tự đoán giới tính/số con. Kèm caveat 30/30/40 (không định mệnh).
    if "tu_tuc" in lq:
        try:
            from engine.tu_vi.tu_tuc_reader import read_tu_tuc
            out["tu_tuc_reading"] = read_tu_tuc(la_so_input)
        except Exception:
            pass
    # Chủ đề có cung Phu Thê (Tình duyên) → kèm tín hiệu duyên deterministic (đào hoa-cấu-trúc /
    # risk độc thân cộng dồn / duyên xa) — ground LLM, framing đọc-đồng-dạng không phán nhân phẩm.
    if "phu_the" in lq:
        try:
            from engine.tu_vi.phu_the_signals import read_phu_the_signals
            out["phu_the_signals"] = read_phu_the_signals(la_so_input)
        except Exception:
            pass
    return out


# ── MÓN SÂU: 2 trụ + xuất xứ (Anh chốt 2026-06-15 'đào sâu - ăn tiếp') ──

def _star_sets_for_chi(chi: str, la_so_input: dict):
    """Sao đồng cung + hội chiếu của 1 chi → lọc atom combo (giống render_3_layer)."""
    from engine.tu_vi.paradigm.to_hop_cung import CHI_RING, to_hop_cung
    ct_chi = {k: v for k, v in (la_so_input.get("chinh_tinh_per_palace") or {}).items() if k in CHI_RING}
    for k, v in (la_so_input.get("phu_tinh_per_palace") or {}).items():
        if k in CHI_RING:
            ct_chi[k] = list(ct_chi.get(k, [])) + list(v)
    same = set(ct_chi.get(chi) or [])
    try:
        tc = set(to_hop_cung(chi, ct_chi)["hoi_chieu_stars"])
    except Exception:
        tc = same
    return same, tc


def gom_chu_de_sau(chu_de: str, la_so_input: dict, three_layer: dict,
                   cap_tru: int = 8) -> dict | None:
    """Món SÂU: chỉ 2 trụ (Trung Châu + Trần Đoàn), nới cap cao, KÈM xuất xứ
    (sách/tác giả/thời đại/trang) + tách đồng-thuận / dị-biệt cho từng sao chính.
    """
    from engine.tu_vi.cross_school import luan_sao_cung
    from engine.tu_vi.provenance import provenance, nhan_xuat_xu, TRU_CHINH
    from engine.tu_vi.viet_names import vi_star

    spec = CHU_DE.get(chu_de)
    if not spec:
        return None
    lop3 = three_layer.get("lop_3_sach_co", {})
    per = lop3.get("per_palace", {})
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    gender = la_so_input.get("gender")

    sao_blocks = []
    for cung in spec["cung_lien_quan"]:
        pd = per.get(cung)
        if not pd:
            continue
        chi = fn_to_chi.get(cung)
        same, tc = _star_sets_for_chi(chi, la_so_input) if chi else (None, None)
        for star in (pd.get("stars") or []):
            cv = luan_sao_cung(star, cung, limit_per_school=cap_tru, chi=chi,
                               gender=gender, same_stars=same, tu_chinh_stars=tc)
            schs = cv.get("schools") or {}
            # chỉ giữ 2 trụ, kèm xuất xứ
            tru_views = []
            for code in TRU_CHINH:
                atoms = schs.get(code) or []
                for a in atoms:
                    xx = nhan_xuat_xu(a.get("book_corpus_id"), a.get("page_start"))
                    vt = a.get("viet_thuan") or a.get("source_quote")
                    if vt:
                        tru_views.append({
                            "phai_code": code, "xuat_xu": xx, "atom_id": a.get("atom_id"),
                            "text": vt[:480], "page": a.get("page_start"),
                        })
            if not tru_views:
                continue
            n_phai = len({v["phai_code"] for v in tru_views})
            sao_blocks.append({
                "sao": star, "sao_vi": vi_star(star),
                "cung": cung, "cung_vi": _CUNG_VI.get(cung, cung),
                "la_chinh": cung == spec["cung_chinh"],
                "mieu_ham": cv.get("mieu_ham"),
                "views": tru_views, "hoi_tu": n_phai >= 2,
            })

    # cách cục + tổ hợp tam phương của cung chính (chiều sâu thêm)
    cung_chinh = spec["cung_chinh"]
    chi_chinh = fn_to_chi.get(cung_chinh)
    to_hop = (lop3.get("to_hop_per_palace") or {}).get(chi_chinh) if chi_chinh else None

    return {
        "slug": chu_de, "ten": spec["ten"], "icon": spec["icon"],
        "goc_nhin": spec["goc_nhin"],
        "sao_blocks": sao_blocks,
        "to_hop_chinh": to_hop,
    }


def gom_gia_vi(chu_de: str, la_so_input: dict, three_layer: dict,
               max_cau: int = 6) -> list[dict]:
    """Phái mỏng (gia vị) → atoms để LẬT THÀNH CÂU HỎI gợi ý.

    Returns: [{atom_id, sao, sao_vi, cung_vi, phai, phai_code, goi_y_text}]
    Mỗi atom là 1 nhận định 1 phái → engine narrative biến thành câu hỏi Đúng/Chưa/Không.
    """
    from engine.tu_vi.cross_school import luan_sao_cung
    from engine.tu_vi.provenance import GIA_VI, CORPUS_PROVENANCE
    from engine.tu_vi.viet_names import vi_star

    spec = CHU_DE.get(chu_de)
    if not spec:
        return []
    per = (three_layer.get("lop_3_sach_co", {})).get("per_palace", {})
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    gender = la_so_input.get("gender")
    # corpus_id của mỗi phái gia vị (để nhãn)
    code_to_corpus = {v["phai_code"]: (k, v) for k, v in CORPUS_PROVENANCE.items()}

    out, seen = [], set()
    for cung in spec["cung_lien_quan"]:
        pd = per.get(cung)
        if not pd:
            continue
        chi = fn_to_chi.get(cung)
        same, tc = _star_sets_for_chi(chi, la_so_input) if chi else (None, None)
        for star in (pd.get("stars") or []):
            cv = luan_sao_cung(star, cung, limit_per_school=3, chi=chi,
                               gender=gender, same_stars=same, tu_chinh_stars=tc)
            schs = cv.get("schools") or {}
            for code in GIA_VI:
                for a in (schs.get(code) or [])[:1]:  # 1 atom/phái/sao — đủ làm câu hỏi
                    aid = a.get("atom_id")
                    if aid in seen:
                        continue
                    vt = a.get("viet_thuan") or a.get("source_quote")
                    if not vt:
                        continue
                    seen.add(aid)
                    _, pmeta = code_to_corpus.get(code, (None, {}))
                    out.append({
                        "atom_id": aid, "sao": star, "sao_vi": vi_star(star),
                        "cung_vi": _CUNG_VI.get(cung, cung),
                        "phai": pmeta.get("phai", code), "phai_code": code,
                        "goi_y_text": vt[:220],
                    })
                    if len(out) >= max_cau:
                        return out
    return out


# ─── DỜI TÂM theo chủ đề (2026-07-31) ────────────────────────────────────────
# Anh khảo sát kỹ pháp "lập thái cực" (dời tâm lá số theo câu hỏi). Rà 11 sách Tử Vi:
# KHÔNG sách nào gọi tên "lập thái cực" — NHƯNG Trung Châu phái đọc chòm theo điểm tham
# chiếu khác Mệnh (nguyên văn "tam phương tứ chính CỦA THIÊN TƯỚNG"). Ta làm ĐÚNG RUỘT đó,
# gọi bằng tên có nguồn, KHÔNG chép từ nguồn AI trên mạng.
#
# Vì sao cần: `CHU_DE.cung_lien_quan` ở trên chọn cung phụ THỦ CÔNG nên sai hình học —
# vd sự nghiệp lấy [Quan Lộc, Mệnh, Tài Bạch, Thiên Di], nhưng Thiên Di là đối cung của
# MỆNH, không thuộc chòm Quan Lộc; đối cung đúng của Quan Lộc là PHU THÊ.
# Hàm dưới tính chòm THẬT của cung tâm + kéo nội dung sao/rule ĐÃ DUYỆT (quote-or-silence).

PARADIGM_DOI_TAM = (
    "Đọc theo chủ đề = LẤY CUNG CỦA CHỦ ĐỀ LÀM TÂM rồi đọc cả chòm của chính nó "
    "(tam phương tứ chính) — cổ pháp Trung Châu đọc chòm theo điểm tham chiếu, không chỉ "
    "đọc từ cung Mệnh. ĐỌC ĐỒNG DẠNG để quan-sát, KHÔNG tiên tri; mệnh là ĐỘNG TỪ."
)


def _doc_cung_grounded(la_so: dict, cung_vi: str, *, chom: bool) -> dict:
    """Đọc 1 cung: sao + nội dung ĐÃ DUYỆT; `chom=True` thì kèm tam phương tứ chính của nó."""
    from engine.tu_vi import van_han as vh

    bi = next((p.get("branch_index") for p in la_so.get("palaces", [])
               if p.get("name") == cung_vi), None)
    if bi is None:
        return {"cung": cung_vi, "co_du_lieu": False}
    stars = vh._stars_at(la_so, bi)
    borrowed = False
    if not stars:                       # Vô Chính Diệu → mượn sao cung xung (cổ pháp)
        stars = vh._stars_at(la_so, (bi + 6) % 12)
        borrowed = bool(stars)
    nguon: list[dict] = []
    for st in stars:
        nguon.extend(vh._grounded_sao(st, cung=cung_vi, limit=1))
    out = {"cung": cung_vi, "co_du_lieu": True, "vi_tri": vh.BRANCHES_TVI[bi],
           "sao": stars, "sao_muon_xung": borrowed, "sao_nguon": nguon,
           "chua_co_nguon": not nguon}
    if chom:
        out["hoi_chieu"] = vh._tam_phuong(la_so, bi)
        out["cung_rules"] = vh._cung_van_rules(cung_vi, "all")
    return out


def doc_doi_tam(la_so: dict, chu_de: str) -> dict:
    """Đọc chủ đề bằng cách DỜI TÂM: cung chủ đề làm tâm + CHÒM THẬT của nó.

    0-LLM, tất định. Nội dung sao/rule chỉ lấy bản founder_verified=1; thiếu → để trống.
    """
    spec = CHU_DE.get(chu_de)
    if not spec:
        return {"available": False, "reason": "chu_de_khong_ho_tro",
                "ho_tro": sorted(CHU_DE.keys())}
    cung_tam = _CUNG_VI.get(spec["cung_chinh"], spec["cung_chinh"])
    tam = _doc_cung_grounded(la_so, cung_tam, chom=True)
    # cung phụ = các cung liên quan KHÁC cung tâm và KHÔNG nằm sẵn trong chòm (tránh lặp)
    trong_chom = {h["cung"] for h in (tam.get("hoi_chieu") or [])} | {cung_tam}
    phu = []
    for c in spec.get("cung_lien_quan", []):
        ten = _CUNG_VI.get(c, c)
        if ten in trong_chom:
            continue
        d = _doc_cung_grounded(la_so, ten, chom=False)
        if d.get("co_du_lieu"):
            phu.append(d)
    return {
        "available": True, "chu_de": chu_de, "ten": spec["ten"], "icon": spec.get("icon"),
        "goc_nhin": spec.get("goc_nhin"),
        "cung_tam": cung_tam, "tam": tam, "phu_tro": phu,
        "paradigm_note": PARADIGM_DOI_TAM,
        "luu_y": ("Sức khoẻ: gợi mở QUAN-SÁT để chăm sóc bản thân, KHÔNG phải chẩn đoán "
                  "y tế — có triệu chứng thì đi khám." if chu_de == "suc_khoe" else None),
    }


def doi_tam_source_text(blk: dict) -> str:
    """Ép khối dời-tâm thành TEXT NGUỒN cho LLM biên-tập-từ-nguồn (pattern van_han)."""
    if not blk.get("available"):
        return ""
    L = [f"### ĐỌC THEO CHỦ ĐỀ: {blk['ten']} — {blk.get('goc_nhin') or ''}",
         f"### LẤY CUNG {blk['cung_tam']} LÀM TÂM (dời tâm theo chủ đề)",
         f"### Nguyên tắc: {blk['paradigm_note']}"]
    t = blk.get("tam") or {}
    if t.get("co_du_lieu"):
        sao = ", ".join(t.get("sao") or []) or "Vô Chính Diệu"
        L.append(f"### CUNG TÂM {t['cung']} ({t['vi_tri']}) — sao: {sao}"
                 + (" [Vô Chính Diệu — mượn sao cung xung]" if t.get("sao_muon_xung") else ""))
        for s in t.get("sao_nguon") or []:
            L.append(f"  · {s['sao']}: {s['dich']} (nguồn: {s['nguon']})")
        if not t.get("sao_nguon"):
            L.append("  · CHƯA CÓ NGUỒN trong kho — KHÔNG luận, không bịa.")
        for r in t.get("cung_rules") or []:
            L.append(f"  · nguyên tắc đọc cung {t['cung']}: {r['rule']} (nguồn: {r['nguon']})")
        if t.get("hoi_chieu"):
            L.append("### CHÒM CỦA CUNG TÂM (tam phương tứ chính — cổ pháp đọc cả chòm):")
            for h in t["hoi_chieu"]:
                sh = ", ".join(h.get("sao") or []) or "Vô Chính Diệu"
                L.append(f"- {h['quan_he']}: {h['cung']} ({h['vi_tri']}) — {sh}")
                for s in h.get("sao_nguon") or []:
                    L.append(f"    · {s['sao']}: {s['dich']} (nguồn: {s['nguon']})")
    if blk.get("phu_tro"):
        L.append("### CUNG PHỤ TRỢ (đối chiếu thêm, KHÔNG lấn át cung tâm):")
        for p in blk["phu_tro"]:
            sp = ", ".join(p.get("sao") or []) or "Vô Chính Diệu"
            L.append(f"- {p['cung']} ({p['vi_tri']}): {sp}")
            for s in (p.get("sao_nguon") or [])[:1]:
                L.append(f"    · {s['sao']}: {s['dich']} (nguồn: {s['nguon']})")
    if blk.get("luu_y"):
        L.append(f"### LƯU Ý: {blk['luu_y']}")
    return "\n".join(L)
