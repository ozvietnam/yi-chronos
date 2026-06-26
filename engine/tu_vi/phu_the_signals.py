"""Tín hiệu cung PHU THÊ (tình duyên) — làm giàu chiem_phu_the từ kênh #3 Nguyệt Đồ.

Anh duyệt 2026-06-26 (hướng cổ điển an toàn, làm tiếp sau P3 Tử Tức). 3 tín hiệu dùng sao
CỔ ĐIỂN, đọc XU HƯỚNG CẤU TRÚC — KHÔNG phán định mệnh, KHÔNG phán nhân phẩm người hôn phối:

1. dao_hoa_field  — trường năng lượng quan hệ phong phú (sức hút mạnh) → ý thức ranh giới + vun đắp.
   (KHÔNG nói "vợ/chồng ngoại tình" — đó là mẫu lá chắn. Chỉ mô tả cấu trúc + hành động.)
2. doc_than_risk  — quy tắc CỘNG DỒN (Cô Quả + Tuần/Triệt Phu Thê + Hóa Kỵ Thiên Di): duyên dễ
   đến MUỘN / cần chủ động hơn (KHÔNG nói "ế").
3. duyen_xa       — Thân cư Thiên Di → duyên dễ đến từ phương xa / môi trường ngoài quê (trung tính).

⚠️ Engine an_sao hiện CHƯA an Thiên Diêu + Thiên Mã → các tín hiệu này dùng sao thay thế khả dụng
(Đại Hao đào hoa, Hồng Loan, Hoa Cái; duyên-xa qua Thân cư Thiên Di thay Thiên Mã). Ghi rõ giới hạn.

Input: la_so_input (build_la_so_input) — chinh_tinh/phu_tinh/vong_sao_per_palace, fn_to_chi,
tuan_chi, triet_chi, tu_hoa, than_palace.
"""
from __future__ import annotations

# Đào-hồng phụ tinh khả dụng trong engine (Thiên Diêu chưa an → dùng nhóm này)
DAO_HONG_PHU = {"dai_hao", "hong_loan", "hoa_cai"}
DAO_HONG_TANG = {"ta_phu", "huu_bat", "dia_khong", "dia_kiep", "dieu_khach"}
# Nhóm chính tinh khuynh hướng đào hoa (theo kênh #3, trừ Thái Dương trọng danh dự)
DAO_HOA_CHINH = {"liem_trinh", "tham_lang", "thien_dong", "thien_phu"}
CO_QUA = {"co_than", "qua_tu"}

CAVEAT = ("Đây là XU HƯỚNG cấu trúc lá số (đọc-đồng-dạng), KHÔNG phải định mệnh và KHÔNG phán "
          "nhân phẩm người bạn đời. Mọi cấu trúc đều có thể vận hành tốt hơn bằng ý thức và vun đắp.")
NGUON = "Sao cổ điển cung Phu Thê · cách trình bày chắt lọc từ kênh Nguyệt Đồ Số Mệnh"


def _stars_at(lsi: dict, *keys: str) -> set[str]:
    out: set[str] = set()
    for src in ("chinh_tinh_per_palace", "phu_tinh_per_palace", "vong_sao_per_palace"):
        d = lsi.get(src) or {}
        for k in keys:
            if k and d.get(k):
                out.update(d[k])
    return out


def _chinh_at(lsi: dict, *keys: str) -> set[str]:
    d = lsi.get("chinh_tinh_per_palace") or {}
    out: set[str] = set()
    for k in keys:
        if k and d.get(k):
            out.update(d[k])
    return out


def read_phu_the_signals(lsi: dict) -> dict:
    fn = lsi.get("fn_to_chi") or {}
    pt_chi = fn.get("phu_the")
    menh_chi = fn.get("menh") or lsi.get("menh_palace")
    di_chi = fn.get("thien_di")
    tuan = set(lsi.get("tuan_chi") or [])
    triet = set(lsi.get("triet_chi") or [])
    tu_hoa = lsi.get("tu_hoa") or []

    pt_stars = _stars_at(lsi, "phu_the", pt_chi)
    pt_chinh = _chinh_at(lsi, "phu_the", pt_chi)

    # ── 1. Trường đào hoa (cấu trúc, không phán ngoại tình) ──
    dh_phu = pt_stars & DAO_HONG_PHU
    dh_chinh = pt_chinh & DAO_HOA_CHINH
    dh_tang = pt_stars & DAO_HONG_TANG
    dao_hoa = None
    if dh_phu and (dh_chinh or len(dh_phu) >= 2):
        muc = "mạnh" if (dh_tang or len(dh_phu) >= 2) else "vừa"
        dao_hoa = {
            "muc": muc,
            "mo_ta": ("Cung Phu Thê tụ sao đào-hồng (" + ", ".join(sorted(dh_phu)) +
                      ") → trường năng lượng quan hệ phong phú, hai phía đều có sức hút. "
                      "Đây là chất liệu sống động, KHÔNG phải dấu hiệu phản bội."),
            "hanh_dong": ("Ý thức ranh giới rõ ràng, giao tiếp cởi mở-trung thực và chủ động vun đắp "
                          "thì trường này thành duyên ấm; buông lơi giao tiếp thì dễ hiểu lầm."),
            "luu_y_engine": "Engine chưa an Thiên Diêu — tín hiệu dựa Đại Hao đào hoa/Hồng Loan/Hoa Cái.",
        }

    # ── 2. Risk độc thân/muộn duyên (CỘNG DỒN) ──
    factors = []
    if (_stars_at(lsi, "menh", menh_chi) | pt_stars) & CO_QUA:
        factors.append("Cô Thần/Quả Tú ở Mệnh hoặc Phu Thê (khuynh hướng thích độc lập, ngại ràng buộc)")
    if pt_chi in tuan or pt_chi in triet:
        factors.append("Tuần/Triệt án cung Phu Thê (đường duyên dễ gián đoạn, khởi sự muộn)")
    if any(t.get("hoa") == "hoa_ky" and t.get("palace_fn") == "thien_di" for t in tu_hoa):
        factors.append("Hóa Kỵ đóng Thiên Di (hay vương vấn mối cũ / tâm lý ảnh hưởng từ quá khứ)")
    n = len(factors)
    muc_dt = ("không nổi bật" if n == 0 else
              "nhẹ — chủ động hơn một chút là ổn" if n == 1 else
              "rõ — duyên dễ đến muộn, nên chủ động + kiên nhẫn (KHÔNG phải ế)" if n == 2 else
              "khá rõ — nên cởi mở, chủ động sớm và buông kỳ vọng cứng")
    doc_than = {"so_yeu_to": n, "muc": muc_dt, "yeu_to": factors,
                "quy_tac": "Cộng dồn: ≥2 yếu tố thì khuynh hướng muộn duyên rõ hơn — đây là điều CHỦ ĐỘNG cải thiện được."}

    # ── 3. Duyên xa ──
    duyen_xa = None
    than = lsi.get("than_palace")
    if than and di_chi and than == di_chi:
        duyen_xa = {"mo_ta": "Thân cư Thiên Di → duyên lành dễ đến từ phương xa / môi trường ngoài quê, "
                             "qua đi lại-công việc-di chuyển hơn là người gần nhà.",
                    "luu_y_engine": "Engine chưa an Thiên Mã — duyên-xa nhận qua Thân cư Thiên Di."}

    return {
        "phu_the_chi": pt_chi,
        "dao_hoa_field": dao_hoa,
        "doc_than_risk": doc_than,
        "duyen_xa": duyen_xa,
        "caveat": CAVEAT,
        "nguon": NGUON,
    }
