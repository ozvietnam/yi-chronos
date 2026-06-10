"""Tổ hợp cung — Tam Phương Tứ Chính + Giáp Cung + Mượn Sao An Cung.

Trung Châu (Vương Đình Chỉ Q2) dạy rõ:
- "Chỉ biết phương pháp Tam Phương Tứ Chính kiểu đơn giản... sẽ trở thành
  luận đoán máy móc" — xem 1 cung PHẢI gom cả tam hợp + xung chiếu.
- "Luận Thiên Tướng phải xem cung giáp TRƯỚC cả Tam Phương Tứ Chính" —
  Thiên Tướng dễ bị hoàn cảnh 2 bên chi phối (Hình Kỵ giáp / Tài Ấm giáp).
- Cung vô chính diệu phải MƯỢN SAO đối cung rồi mới luận (tá tinh an cung).

Built 2026-06-11 (việc A+B+C combo cung × cung × cung).
"""
from __future__ import annotations

# Vòng 12 địa chi theo thứ tự
CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti",
            "ngo", "mui", "than", "dau", "tuat", "hoi"]
_CHI_IDX = {c: i for i, c in enumerate(CHI_RING)}

# Tam hợp 4 cục (Thân-Tý-Thìn / Dần-Ngọ-Tuất / Tỵ-Dậu-Sửu / Hợi-Mão-Mùi)
TAM_HOP_GROUPS = [
    ["than", "ty", "thin"],
    ["dan", "ngo", "tuat"],
    ["ti", "dau", "suu"],
    ["hoi", "mao", "mui"],
]
_CHI_TO_TAM_HOP: dict[str, list[str]] = {}
for _g in TAM_HOP_GROUPS:
    for _c in _g:
        _CHI_TO_TAM_HOP[_c] = _g

CITATION_TAM_PHUONG = (
    "Trung Châu Q2: chỉ xét Tam Phương Tứ Chính kiểu đơn giản "
    "= luận đoán máy móc — phải gom tam hợp + xung chiếu khi luận 1 cung"
)
CITATION_GIAP_THIEN_TUONG = (
    "Trung Châu Q2: luận Thiên Tướng phải xem cung giáp TRƯỚC "
    "Tam Phương Tứ Chính — Thiên Tướng dễ bị hoàn cảnh 2 bên chi phối"
)
CITATION_MUON_SAO = (
    "Trung Châu Q2: cung vô chính diệu phải mượn sao đối cung "
    "(tá tinh an cung) rồi mới luận"
)


def tam_phuong_tu_chinh(chi: str) -> dict:
    """Tính tam phương tứ chính của 1 cung (chi canonical).

    Returns: {cung, tam_hop: [2 chi], xung_chieu: chi, tu_chinh: [4 chi]}
    """
    if chi not in _CHI_IDX:
        raise ValueError(f"Chi không hợp lệ: {chi}")
    tam_hop = [c for c in _CHI_TO_TAM_HOP[chi] if c != chi]
    xung = CHI_RING[(_CHI_IDX[chi] + 6) % 12]
    return {
        "cung": chi,
        "tam_hop": tam_hop,
        "xung_chieu": xung,
        "tu_chinh": [chi] + tam_hop + [xung],
    }


def giap_cung(chi: str) -> list[str]:
    """2 cung kề kẹp 2 bên (giáp). Returns [cung trước, cung sau]."""
    if chi not in _CHI_IDX:
        raise ValueError(f"Chi không hợp lệ: {chi}")
    i = _CHI_IDX[chi]
    return [CHI_RING[(i - 1) % 12], CHI_RING[(i + 1) % 12]]


def muon_sao(chi: str, chinh_tinh_per_palace: dict[str, list[str]]) -> dict:
    """Mượn sao an cung cho cung vô chính diệu (tá tinh từ đối cung).

    Returns: {vo_chinh_dieu: bool, stars: [...], borrowed_from: chi|None, citation}
    """
    own = list(chinh_tinh_per_palace.get(chi) or [])
    if own:
        return {"vo_chinh_dieu": False, "stars": own, "borrowed_from": None}
    xung = CHI_RING[(_CHI_IDX[chi] + 6) % 12]
    borrowed = list(chinh_tinh_per_palace.get(xung) or [])
    return {
        "vo_chinh_dieu": True,
        "stars": borrowed,
        "borrowed_from": xung if borrowed else None,
        "citation": CITATION_MUON_SAO,
    }


def to_hop_cung(chi: str, chinh_tinh_per_palace: dict[str, list[str]]) -> dict:
    """Tổng hợp tổ hợp cung đầy đủ cho 1 cung: tứ chính + mượn sao + giáp.

    Args:
        chi: cung cần luận (chi canonical)
        chinh_tinh_per_palace: map chi → list chính tinh canonical
                               (chỉ dùng key là 12 chi, key chức năng bị bỏ qua)

    Returns: {
        cung, tu_chinh: {...}, muon_sao: {...},
        hoi_chieu_stars: list (toàn bộ sao trong tứ chính, gồm sao mượn),
        giap: {cungs: [2], stars_per_cung: {...}, thien_tuong_note: str|None},
        citation
    }
    """
    tpc = tam_phuong_tu_chinh(chi)
    ms = muon_sao(chi, chinh_tinh_per_palace)

    # Gom sao hội chiếu từ cả 4 cung tứ chính (cung vô chính diệu thì mượn)
    hoi_chieu: list[str] = []
    stars_per_cung: dict[str, dict] = {}
    for c in tpc["tu_chinh"]:
        m = muon_sao(c, chinh_tinh_per_palace)
        stars_per_cung[c] = m
        for s in m["stars"]:
            if s not in hoi_chieu:
                hoi_chieu.append(s)

    giap = giap_cung(chi)
    giap_stars = {c: list(chinh_tinh_per_palace.get(c) or []) for c in giap}

    # Thiên Tướng đặc biệt: giáp quan trọng hơn tam phương (Trung Châu)
    own_stars = chinh_tinh_per_palace.get(chi) or []
    thien_tuong_note = CITATION_GIAP_THIEN_TUONG if "thien_tuong" in own_stars else None

    return {
        "cung": chi,
        "tu_chinh": tpc,
        "tu_chinh_stars": stars_per_cung,
        "muon_sao": ms,
        "hoi_chieu_stars": hoi_chieu,
        "giap": {
            "cungs": giap,
            "stars_per_cung": giap_stars,
            "thien_tuong_note": thien_tuong_note,
        },
        "citation": CITATION_TAM_PHUONG,
    }
