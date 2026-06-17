"""Duyên — bộ tính năng tình duyên cho NGƯỜI ĐANG TÌM (Anh chốt 2026-06-16).

4 tính năng, đều đọc đồng dạng (KHÔNG predict số phận, mệnh là động từ):
- chan_dung_nua_kia(ls): lá số bạn hợp KIỂU bạn đời nào + con giáp hợp.
- duyen_ca_nhan(ls, tuoi, gender): đường tình duyên (sớm/muộn, đào hoa, vì sao chưa, cách).
- dao_hoa_van(ls, birth_year, nam_xem, n): cửa sổ NĂM có duyên (đại vận + lưu niên sao hỉ).
- tuoi_hop(chi): tam hợp/lục hợp/xung/hại theo con giáp.

Input: la_so_input từ render_from_birth.
"""
from __future__ import annotations

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
CON_GIAP = {"Tý": "Chuột", "Sửu": "Trâu", "Dần": "Hổ", "Mão": "Mèo", "Thìn": "Rồng",
            "Tỵ": "Rắn", "Ngọ": "Ngựa", "Mùi": "Dê", "Thân": "Khỉ", "Dậu": "Gà",
            "Tuất": "Chó", "Hợi": "Lợn"}
_CANON = {"ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn", "ti": "Tỵ",
          "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi"}
TAM_HOP = [["Thân", "Tý", "Thìn"], ["Dần", "Ngọ", "Tuất"], ["Tỵ", "Dậu", "Sửu"], ["Hợi", "Mão", "Mùi"]]
LUC_HOP = {"Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần", "Mão": "Tuất", "Tuất": "Mão",
           "Thìn": "Dậu", "Dậu": "Thìn", "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ"}
LUC_XUNG = {"Tý": "Ngọ", "Ngọ": "Tý", "Sửu": "Mùi", "Mùi": "Sửu", "Dần": "Thân", "Thân": "Dần",
            "Mão": "Dậu", "Dậu": "Mão", "Thìn": "Tuất", "Tuất": "Thìn", "Tỵ": "Hợi", "Hợi": "Tỵ"}
LUC_HAI = {"Tý": "Mùi", "Mùi": "Tý", "Sửu": "Ngọ", "Ngọ": "Sửu", "Dần": "Tỵ", "Tỵ": "Dần",
           "Mão": "Thìn", "Thìn": "Mão", "Thân": "Hợi", "Hợi": "Thân", "Dậu": "Tuất", "Tuất": "Dậu"}

# Chính tinh ở Phu Thê → kiểu bạn đời (chân dung)
NUA_KIA = {
    "tu_vi": "người có khí chất, tự trọng cao, ưa làm chủ, dáng vẻ sang trọng — cần bạn biết tôn trọng cái tôi của họ",
    "thien_co": "người thông minh, nhanh nhạy, hay suy nghĩ và giỏi tính toán — hợp người biết trò chuyện, chia sẻ ý tưởng",
    "thai_duong": "người hướng ngoại, nhiệt thành, có chí và quảng giao, hào phóng — bạn đời 'có ánh sáng', thích việc lớn",
    "vu_khuc": "người thực tế, giỏi tiền bạc, quyết đoán, hơi cứng và ít ngọt ngào — chân thành kiểu hành động hơn lời nói",
    "thien_dong": "người hiền hòa, tình cảm, trẻ trung, thích sự nhẹ nhàng vui vẻ — dễ gần, ít toan tính",
    "liem_trinh": "người cá tính mạnh, có sức hút, nhiều nguyên tắc riêng, yêu nồng nhiệt — đậm chất 'tình' nhưng cần thấu hiểu",
    "thien_phu": "người ổn định, biết lo toan, rộng rãi, là 'kho tàng' giữ nhà — bạn đời đáng tin, vững chãi",
    "thai_am": "người dịu dàng, tế nhị, lãng mạn, giỏi quán xuyến trong êm — tình cảm sâu mà kín đáo",
    "tham_lang": "người có sức hút lớn, giao tế rộng, đa tài đa tình, ham vui sống động — duyên dáng nhưng cần sự gắn bó rõ ràng",
    "cu_mon": "người giỏi ăn nói, lý lẽ rạch ròi, thẳng thắn (đôi khi hay nghi) — hợp người trung thực, nói rõ lòng",
    "thien_tuong": "người trung hậu, biết chăm lo, trọng lễ nghĩa và hình thức — bạn đời tận tụy, là chỗ dựa",
    "thien_luong": "người chững chạc, che chở, có nguyên tắc, lo xa (đôi khi hơi 'người lớn') — vững vàng, đáng nương",
    "that_sat": "người mạnh mẽ, độc lập, quyết liệt, ít ngọt nhưng chung thủy theo cách riêng — hợp người tôn trọng khoảng tự do",
    "pha_quan": "người dám nghĩ dám làm, phá cách, đời nhiều thay đổi — sống động nhưng cần bạn chịu được biến động",
}
_SAO_VI = {"tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương", "vu_khuc": "Vũ Khúc",
           "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh", "thien_phu": "Thiên Phủ",
           "thai_am": "Thái Âm", "tham_lang": "Tham Lang", "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng",
           "thien_luong": "Thiên Lương", "that_sat": "Thất Sát", "pha_quan": "Phá Quân"}
DAO_HOA_TINH = {"hong_loan", "thien_hy", "ham_tri", "thien_rieu", "dao_hoa", "dai_hao"}
CO_QUA = {"co_than", "qua_tu"}


def _norm(c):
    return _CANON.get(c, c)


def _phu_the(ls):
    fn = ls.get("fn_to_chi") or {}
    raw = fn.get("phu_the")
    chi = _norm(raw)
    sao = (ls.get("chinh_tinh_per_palace") or {}).get(raw) or []
    return raw, chi, sao


def _stars_at(ls, raw_chi):
    """Tất cả sao (phụ + vòng) tại 1 chi."""
    out = []
    for src in ("phu_tinh_per_palace", "vong_sao_per_palace"):
        out += (ls.get(src) or {}).get(raw_chi) or []
    return out


# ════════ 1. CHÂN DUNG NỬA KIA ════════
def chan_dung_nua_kia(ls: dict) -> dict:
    raw, chi, sao = _phu_the(ls)
    year_chi = _norm(ls.get("chi"))
    mo_ta = []
    if sao:
        for s in sao:
            if s in NUA_KIA:
                mo_ta.append(f"{_SAO_VI.get(s, s)}: {NUA_KIA[s]}")
    else:
        # vô chính diệu — mượn đối cung
        mo_ta.append("Cung Phu Thê vô chính diệu — hình bóng bạn đời chưa định hình rõ một nét, "
                     "thường đa diện; duyên cần thời gian để 'lộ mặt'. Nên nhìn vào người đối cung và trải nghiệm thực tế.")
    # con giáp hợp theo tuổi
    trio = next((t for t in TAM_HOP if year_chi in t), [])
    tam = [CON_GIAP[c] for c in trio if c != year_chi]
    luc = CON_GIAP.get(LUC_HOP.get(year_chi))
    return {
        "phu_the_chi": chi, "phu_the_chi_con_giap": CON_GIAP.get(chi),
        "chinh_tinh": [_SAO_VI.get(s, s) for s in sao],
        "mo_ta": mo_ta,
        "con_giap_hop": {"tam_hop": tam, "luc_hop": luc},
        "loi_khuyen": "Đây là KIỂU người dễ cộng hưởng với bạn — không phải khuôn cứng. "
                      "Tuổi hợp chỉ là gợi ý ưu tiên, cái chính vẫn là con người thật.",
    }


# ════════ 2. DUYÊN CỦA TÔI ════════
def duyen_ca_nhan(ls: dict, tuoi_mu: int | None = None, gender: str = "M") -> dict:
    raw, chi, sao = _phu_the(ls)
    pt_stars = _stars_at(ls, raw)
    menh_raw = ls.get("menh_palace")
    menh_stars = _stars_at(ls, menh_raw)
    diem_dao_hoa = 0
    tin_hieu = []

    # đào hoa
    dh = [s for s in (pt_stars + menh_stars) if s in DAO_HOA_TINH]
    if dh:
        diem_dao_hoa = len(set(dh))
        tin_hieu.append(("dao_hoa", f"Có {len(set(dh))} sao đào hoa quanh Mệnh/Phu Thê — "
                         "bạn vốn có duyên, dễ được người khác phái để ý; cái khó thường là 'chốt', không phải 'gặp'."))
    # cô thần quả tú → muộn/kén
    cq = [s for s in (pt_stars + menh_stars) if s in CO_QUA]
    if cq:
        tin_hieu.append(("muon", "Có Cô Thần/Quả Tú — thiên hướng độc lập, kén chọn, hoặc duyên đến muộn. "
                         "Không phải 'ế', mà là 'chờ đúng người' — khi mở lòng và bớt cầu toàn thì duyên tới."))
    # chính tinh Phu Thê mạnh (Tử/Sát/Phá/Tham) → bạn đời cá tính, duyên sóng gió/muộn
    if any(s in ("tu_vi", "that_sat", "pha_quan", "tham_lang", "vu_khuc") for s in sao):
        tin_hieu.append(("ban_doi_manh", "Cung Phu Thê có chính tinh cá tính mạnh — bạn đời thường là người "
                         "'có chất riêng'; nên lấy hơi muộn (sau khi cả hai đủ chín) thì bền hơn."))
    if not sao:
        tin_hieu.append(("vcd", "Phu Thê vô chính diệu — duyên cần thời gian định hình; đừng vội, "
                         "người phù hợp thường xuất hiện khi bạn đã rõ mình muốn gì."))
    # Hóa Kỵ Phu Thê
    if any(t.get("hoa") == "hoa_ky" and t.get("palace_fn") == "phu_the" for t in (ls.get("tu_hoa") or [])):
        tin_hieu.append(("vuong", "Có Hóa Kỵ ở Phu Thê — chuyện tình dễ vướng mắc, trăn trở; "
                         "cần học buông cái 'phải hoàn hảo' và giao tiếp thẳng."))
    # tổng kết sớm/muộn
    muon = bool(cq) or any(s in ("tu_vi", "that_sat", "pha_quan") for s in sao) or not sao
    return {
        "phu_the_chi": chi, "chinh_tinh": [_SAO_VI.get(s, s) for s in sao],
        "diem_dao_hoa": diem_dao_hoa,
        "xu_huong": "muộn / kén chọn" if muon else "thuận / dễ có duyên",
        "tin_hieu": [{"loai": l, "noi_dung": n} for l, n in tin_hieu],
        "cach_van_hanh": [
            "Mệnh là động từ: lá số nói thiên hướng, còn 'có duyên hay không' do bạn vận hành.",
            "Nếu thiên muộn/kén: bớt cầu toàn, mở rộng môi trường gặp gỡ, cho người ta cơ hội hiểu mình.",
            "Nếu đào hoa nhiều: tập 'chốt' — chọn một người và đi sâu, thay vì giữ nhiều mối hời hợt.",
        ],
    }


# ════════ 3. NĂM CÓ DUYÊN (đào hoa vận) ════════
def _menh_index(ls):
    return CHI.index(_norm(ls.get("menh_palace")))


def _hong_loan_idx(year_branch_vn):
    """Hồng Loan: khởi Mão nghịch theo chi năm (Tý→Mão, Sửu→Dần...)."""
    return (3 - CHI.index(year_branch_vn)) % 12


def dao_hoa_van(ls: dict, birth_year: int, nam_xem: int, n_nam: int = 12) -> dict:
    """Quét N năm tới: năm nào lưu Hồng Loan/Thiên Hỷ đáo Mệnh hoặc Phu Thê = cửa sổ duyên."""
    menh_i = _menh_index(ls)
    raw, pt_chi, _ = _phu_the(ls)
    pt_i = CHI.index(pt_chi) if pt_chi in CHI else None
    nam_cat = []
    for y in range(nam_xem, nam_xem + n_nam):
        yb = CHI[(y - 4) % 12]
        hl = _hong_loan_idx(yb)
        th = (hl + 6) % 12  # Thiên Hỷ xung Hồng Loan
        hits = []
        if hl == menh_i or th == menh_i:
            hits.append("Mệnh")
        if pt_i is not None and (hl == pt_i or th == pt_i):
            hits.append("Phu Thê")
        if hits:
            tuoi = y - birth_year + 1
            nam_cat.append({"nam": y, "tuoi_mu": tuoi, "cung": hits,
                            "sao": "Hồng Loan" if (hl == menh_i or hl == pt_i) else "Thiên Hỷ"})
    return {
        "tu_nam": nam_xem, "den_nam": nam_xem + n_nam - 1,
        "nam_co_duyen": nam_cat,
        "ghi_chu": "Năm sao hỉ (Hồng Loan/Thiên Hỷ) chiếu Mệnh hoặc Phu Thê = cửa sổ duyên dễ khởi. "
                   "Đây là XU HƯỚNG thuận, không phải lời hứa — vẫn cần bạn chủ động bước ra.",
    }


# ════════ 4. TUỔI HỢP – TUỔI CẦN Ý THỨC ════════
def tuoi_hop(chi_raw: str) -> dict:
    chi = _norm(chi_raw)
    if chi not in CHI:
        return {"error": "Chi không hợp lệ"}
    trio = next((t for t in TAM_HOP if chi in t), [])
    tam = [c for c in trio if c != chi]
    return {
        "con_giap": CON_GIAP.get(chi), "chi": chi,
        "tam_hop": [{"chi": c, "con_giap": CON_GIAP[c]} for c in tam],
        "luc_hop": {"chi": LUC_HOP.get(chi), "con_giap": CON_GIAP.get(LUC_HOP.get(chi))},
        "luc_xung": {"chi": LUC_XUNG.get(chi), "con_giap": CON_GIAP.get(LUC_XUNG.get(chi))},
        "luc_hai": {"chi": LUC_HAI.get(chi), "con_giap": CON_GIAP.get(LUC_HAI.get(chi))},
        "ghi_chu": "Tam hợp + lục hợp = dễ đồng điệu. Lục xung/lục hại = cần ý thức dung hòa hơn — "
                   "KHÔNG phải cấm kỵ; nhiều cặp xung/hại vẫn bền nhờ hiểu nhau (xem kỹ cả lá số, đừng chỉ nhìn con giáp).",
    }
