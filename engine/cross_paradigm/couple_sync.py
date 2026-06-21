"""#56 — Luận SO ĐÔI đích danh (2 lá số cụ thể): Bát Tự hợp hôn + Tử Vi Phu Thê chéo.

Khác #55 (12 khía cạnh của MỘT lá): đây so HAI người (mình + người yêu/vợ chồng).
THỂ (Bát Tự hợp hôn: bổ khuyết ngũ hành + thập thần tương hợp) × DỤNG (Tử Vi Phu Thê
chéo: sao cung Phu Thê A soi B và ngược lại) → đồng/dị-tham (kept_all, Iron #3).
Paradigm: KHÔNG "hợp/khắc → nên/không nên cưới"; đọc đồng dạng + động từ (Iron #4/#6/#8).

⚠️ FOUNDATION (issue #56 mục 1-2): hợp nhất + đồng/dị-tham + paradigm guard + an toàn
engine, ĐÃ test (mock engine con). TĂNG DẦN: Tử Vi Phu Thê chéo ĐÚNG NGHĨA (cung Phu
Thê A ↔ lá B — hiện dùng Phu Thê mỗi người làm xấp xỉ); đối chiếu corpus; API + trừ
30 xu + đồng thuận PDPL người thứ 2.
"""
from __future__ import annotations

from typing import Any, Optional

from engine.cross_paradigm._common import (
    CONCORD_DI, concord as _concord, norm as _norm, reframe_check as _reframe_check,
)

# Engine con — module-level để test monkeypatch được.
from engine.bat_tu.compatibility import analyze_compatibility
from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4

GIA_XU = 30  # giá đã chốt (issue #56) — luận 2 lá số

_NEG = ("khac", "xung", "cang", "ky", "hao", "pha", "kiep", "hung", "tuyet")
_POS = ("hop", "thuan", "tot", "cat", "on", "vuong", "bo khuyet", "tuong ho", "vien")


def _dir_compat(out: Optional[dict]) -> Optional[str]:
    """Hướng Bát Tự hợp hôn: hợp/bổ khuyết → thuan; khắc/xung → cang."""
    if not out:
        return None
    label = _norm(str((out.get("overall") or {}).get("label", "")))
    if any(k in label for k in _NEG):
        return "cang"
    if any(k in label for k in _POS):
        return "thuan"
    return "thuan" if out.get("overall") else None


def _dir_phu_the(a_out: Optional[dict], b_out: Optional[dict]) -> Optional[str]:
    """Hướng Tử Vi Phu Thê chéo: bất kỳ rule Q* 'hit' (Hóa Kỵ/Sát…) ở lá nào → căng."""
    outs = [o for o in (a_out, b_out) if o]
    if not outs:
        return None
    for o in outs:
        if any(isinstance(v, dict) and v.get("hit") for v in o.values()):
            return "cang"
    return "thuan"


def _phu_the_reading(a_out: Optional[dict], b_out: Optional[dict]) -> str:
    parts = []
    for tag, o in (("A", a_out), ("B", b_out)):
        if o and o.get("phu_the_tong_quan"):
            parts.append(f"[{tag}] {o['phu_the_tong_quan']}")
    return " · ".join(parts)


def luan_so_doi(*, person_a: dict, person_b: dict) -> dict[str, Any]:
    """So đôi đích danh 2 lá số → Bát Tự hợp hôn + Tử Vi Phu Thê chéo + đồng/dị-tham.

    person_{a,b} = {"bat_tu_state": <cast_bat_tu out>, "la_so": <tu vi la_so>}.
    An toàn: engine con lỗi → phái đó unsourced, KHÔNG sập, ghi engine_errors.
    """
    errs: list[str] = []
    try:
        bt = analyze_compatibility(person_a.get("bat_tu_state"), person_b.get("bat_tu_state"))
    except Exception as e:  # noqa: BLE001
        bt, _ = None, errs.append(f"bat_tu: {e}")
    try:
        tv_a = chiem_phu_the_v4(person_a.get("la_so"))
        tv_b = chiem_phu_the_v4(person_b.get("la_so"))
    except Exception as e:  # noqa: BLE001
        tv_a, tv_b, _ = None, None, errs.append(f"tu_vi: {e}")

    bt_reading = str((bt.get("overall") or {}).get("narrative", "")) if bt else ""
    bt_dir = _dir_compat(bt)
    bt_src = [str(bt["source_ref"])] if (bt and bt.get("source_ref")) else []

    tv_reading = _phu_the_reading(tv_a, tv_b)
    tv_dir = _dir_phu_the(tv_a, tv_b)

    con = _concord(bt_dir, tv_dir)
    ok_bt, fl_bt = _reframe_check(bt_reading)
    ok_tv, fl_tv = _reframe_check(tv_reading)

    return {
        "method_id": "couple_sync_v0",
        "paradigm": ("Đọc đồng dạng, KHÔNG 'nên/không nên cưới'. Bát Tự=THỂ (hợp hôn), "
                     "Tử Vi=DỤNG (Phu Thê chéo); năng lượng hai người VẬN HÀNH thế nào."),
        "bat_tu_hop_hon": {
            "reading": bt_reading or "(unsourced)", "direction": bt_dir, "sources": bt_src,
        },
        "tu_vi_phu_the_cheo": {
            "reading": tv_reading or "(unsourced)", "direction": tv_dir, "sources": [],
        },
        "concord": con,
        "note": "dị-tham: giữ CẢ HAI quan điểm, thận trọng" if con == CONCORD_DI else "",
        "paradigm_ok": ok_bt and ok_tv,
        "paradigm_flags": (fl_bt + fl_tv) or None,
        "engine_errors": errs,
        "gia_xu": GIA_XU,
    }
