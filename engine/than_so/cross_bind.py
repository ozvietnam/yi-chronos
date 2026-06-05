"""Đối chiếu số Thần Số Học (1-9) ↔ Ngũ Hành / Thiên Can Đông phương.

IRON RULE #3 (đa phái độc lập): ĐỐI CHIẾU 3 cầu nối, KHÔNG ép về một hệ.
- Hà Đồ: tái dùng engine.yi_wiki.ha_do_lac_thu (repo native).
- Lạc Thư + hành tinh Cheiro: nạp từ data/than_so/master/cross_bind_dong_phuong.json.

KHÔNG predict — chỉ trình bày tương ứng để Anh tự quan-sát.
"""
from __future__ import annotations

from collections import Counter

from .constants import _load_json

try:
    from engine.yi_wiki.ha_do_lac_thu import get_ngu_hanh_for_so as _ha_do_ngu_hanh
except Exception:  # pragma: no cover - fallback nếu yi_wiki không import được
    _ha_do_ngu_hanh = None

_HA_DO_FALLBACK = {1: "Thủy", 6: "Thủy", 2: "Hỏa", 7: "Hỏa",
                   3: "Mộc", 8: "Mộc", 4: "Kim", 9: "Kim", 5: "Thổ"}


def _ha_do(n: int) -> str | None:
    if _ha_do_ngu_hanh is not None:
        return _ha_do_ngu_hanh(n)
    return _HA_DO_FALLBACK.get(n)


def _data() -> dict:
    return _load_json("cross_bind_dong_phuong.json")


def cross_bind_dong_phuong(number: int) -> dict:
    """Đối chiếu 1 số (1-9) sang Ngũ Hành/Thiên Can qua 3 cầu nối độc lập.

    Số chủ 11/22/33 được rút về gốc (2/4/6) để đối chiếu, có ghi chú.
    """
    data = _data()
    base = number
    master_note = None
    if number in (11, 22, 33):
        base = {11: 2, 22: 4, 33: 6}[number]
        master_note = f"Số chủ {number} → rút về {base} để đối chiếu Đông phương."
    if not (1 <= base <= 9):
        return {"number": number, "error": "Chỉ đối chiếu số 1-9 (hoặc master 11/22/33)."}

    key = str(base)
    ha_do_nh = _ha_do(base)
    lac_thu_nh = data["bridges"]["lac_thu"]["map"].get(key)
    cheiro = data["bridges"]["cheiro_planet"]["map"].get(key, {})
    cheiro_nh = cheiro.get("ngu_hanh")

    # Đồng thuận: hành nào được ≥2 cầu nối nhắc tới
    votes = [x for x in (ha_do_nh, lac_thu_nh, cheiro_nh) if x]
    counter = Counter(votes)
    consensus = [nh for nh, c in counter.items() if c >= 2]

    # Thiên Can ứng viên từ MỌI hành xuất hiện (đa phái)
    e2c = data["element_to_thien_can"]
    thien_can: dict[str, list[str]] = {nh: e2c[nh] for nh in counter if nh in e2c}

    return {
        "number": number,
        "base": base,
        "master_note": master_note,
        "paradigm_note": data["paradigm_note"],
        "bridges": {
            "ha_do": {"ngu_hanh": ha_do_nh},
            "lac_thu": {"ngu_hanh": lac_thu_nh},
            "cheiro_planet": {"planet": cheiro.get("planet"), "ngu_hanh": cheiro_nh},
        },
        "consensus_ngu_hanh": consensus,
        "divergence": len(set(votes)) > 1,
        "thien_can_candidates": thien_can,
    }


__all__ = ["cross_bind_dong_phuong"]
