"""Thần sát cho quẻ Lục Hào — tra theo can/chi NGÀY gieo, đánh dấu hào trúng sao.

Nguồn: seed `data/seeds/than_sat_7_sao.json` (Thiệu Vĩ Hoa p99-103) — nối
2026-07-16 (audit "hút mà chưa nối": seed tồn tại, engine Lục Hào 0-ref).

Quy ước:
- Quý Nhân / Kình Dương / Lộc: tra theo CAN ngày.
- Dịch Mã / Đào Hoa / Hoa Cái: tra theo tam-hợp-cục của CHI ngày.
- Thiên La / Địa Võng: chi cố định.
- `luat_nam_9` trong seed là quy luật NĂM (không thuộc hào) — không dùng ở đây.

Quote-or-silence: seed thiếu/hỏng → trả {} ; chỉ liệt kê sao có hào TRÚNG.
Iron rule của seed: "Bảng tra paradigm, KHÔNG predict tuyệt đối".
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SEED_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data" / "seeds" / "than_sat_7_sao.json"
)


@lru_cache(maxsize=1)
def _seed() -> dict:
    try:
        return json.loads(_SEED_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _tam_hop_lookup(table: dict[str, str], day_branch: str) -> str | None:
    """Bảng keyed 'Dần-Ngọ-Tuất' → chi. Tìm nhóm chứa chi ngày."""
    for group, target in table.items():
        if day_branch in group.split("-"):
            return target
    return None


def compute_than_sat(day_stem: str, day_branch: str, lines: list[dict]) -> dict:
    """Tra 7 thần sát cho lượt gieo; trả các sao có hào trúng.

    Args:
        day_stem/day_branch: can chi ngày gieo.
        lines: 6 hào từ cast (mỗi hào có `line_position` + `branch`).

    Returns: {"source": ..., "sao": [{key, ten, y_nghia, target_branches,
              lines_hit, luu_y?}]} — {} nếu seed thiếu.
    """
    d = _seed()
    if not d:
        return {}

    # (key, list chi đích của ngày này, ghi chú thêm nếu có)
    targets: list[tuple[str, list[str], str | None]] = []

    qn = d.get("quy_nhan_thien_at", {})
    branches = qn.get("bang_tra", {}).get(day_stem)
    if branches:
        targets.append(("quy_nhan_thien_at", list(branches), qn.get("luu_y")))

    ma = d.get("sao_ma_dich_ma", {})
    hit = _tam_hop_lookup(ma.get("bang_tra_theo_chi_nam_hoac_ngay", {}), day_branch)
    if hit:
        targets.append(("sao_ma_dich_ma", [hit], None))

    dh = d.get("dao_hoa_ham_tri", {})
    hit = _tam_hop_lookup(dh.get("bang_tra", {}), day_branch)
    if hit:
        targets.append(("dao_hoa_ham_tri", [hit], None))

    kd = d.get("kinh_duong_duong_nhan", {})
    hit = kd.get("bang_tra_theo_can_ngay", {}).get(day_stem)
    if hit:
        targets.append(("kinh_duong_duong_nhan", [hit], None))

    loc = d.get("loc_thap_can", {})
    hit = loc.get("bang_tra_theo_can_ngay", {}).get(day_stem)
    if hit:
        targets.append(("loc_thap_can", [hit], None))

    hc = d.get("hoa_cai", {})
    hit = _tam_hop_lookup(hc.get("bang_tra", {}), day_branch)
    if hit:
        targets.append(("hoa_cai", [hit], None))

    tldv = d.get("thien_la_dia_vong", {})
    for sub_key in ("thien_la", "dia_vong"):
        chis = tldv.get(sub_key)
        if chis:
            targets.append((f"thien_la_dia_vong.{sub_key}", list(chis), None))

    out = []
    for key, target_branches, luu_y in targets:
        hits = [
            ln["line_position"] for ln in lines
            if ln.get("branch") in target_branches
        ]
        if not hits:
            continue
        base_key = key.split(".")[0]
        meta = d.get(base_key, {})
        entry = {
            "key": key,
            "ten": meta.get("ten"),
            "y_nghia": meta.get("y_nghia"),
            "target_branches": target_branches,
            "lines_hit": hits,
        }
        if luu_y:
            entry["luu_y"] = luu_y
        out.append(entry)

    return {
        "source": d.get("_meta", {}).get("title"),
        "iron_rule": d.get("_meta", {}).get("iron_rule"),
        "sao": out,
    }
