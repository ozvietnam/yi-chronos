"""#55 — Hợp nhất SONG PHÁI Bát Tự (THỂ 體) ↔ Tử Vi (DỤNG 用): hôn nhân/gia đình.

Bát Tự = THỂ (năng lượng ngũ hành/thập thần, tiên thiên, "bạn LÀ AI").
Tử Vi  = DỤNG (tinh diệu × 12 cung, hậu thiên, "bạn VẬN HÀNH/ TRẢI QUA điều gì").
Cao thủ THAM ĐOÁN (参断): đồng-tham (cùng hướng → tin cao) vs dị-tham (lệch → giữ CẢ
HAI, thận trọng — kept_all, Iron #3). Mệnh là ĐỘNG TỪ (Iron #8); đọc đồng dạng KHÔNG
predict (Iron #4/#6) — mọi prose qua `hermes_guard.paradigm_violations`.

⚠️ TRẠNG THÁI: đây là NỀN TẢNG (foundation, issue #55 mục 1-2). Phần ĐÃ làm + test:
ma trận 12 khía cạnh, thuật toán đồng/dị-tham, paradigm guard, orchestration (gọi 2
engine an toàn, không sập). Phần TĂNG DẦN (chưa xong): extract tín-hiệu PER-KHÍA-CẠNH
từ output thật của từng engine (hiện dùng hướng TỔNG của mỗi engine làm xấp xỉ) +
đối chiếu corpus wiki.sqlite3 cho từng luận điểm (hiện gắn `sources` thô / `unsourced`).
"""
from __future__ import annotations

import json
import unicodedata
from typing import Any, Optional

from engine.hermes_guard import paradigm_violations

# Engine con — import ở module level để test monkeypatch được (spec: "mock engine con").
from engine.bat_tu.hon_nhan import analyze_hon_nhan
from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4

CONCORD_DONG = "đồng_tham"   # 2 phái cùng hướng → tin cao
CONCORD_DI = "dị_tham"       # lệch hướng → giữ CẢ HAI, thận trọng (KHÔNG chọn phái)
CONCORD_MOT = "một_phía"     # chỉ 1 phái có tín hiệu

# Ma trận 12 khía cạnh (issue #55). lead = phái DẪN luận chính; phái kia cross-check.
ASPECTS: list[dict] = [
    {"id": 1,  "ten": "Tính cách/khí chất phối ngẫu",          "lead": "tu_vi"},
    {"id": 2,  "ten": "Chất lượng hôn nhân tổng thể",          "lead": "tu_vi"},
    {"id": 3,  "ten": "Ứng kỳ (khoảng kích hoạt quan hệ)",     "lead": "tu_vi"},
    {"id": 4,  "ten": "Năng lượng tương tác hợp/khắc",         "lead": "bat_tu"},
    {"id": 5,  "ten": "'Cao thấp'/lực của Thê tinh",           "lead": "bat_tu"},
    {"id": 6,  "ten": "Hợp đôi (hai người)",                   "lead": "bat_tu"},
    {"id": 7,  "ten": "Điểm căng quan hệ (xa cách/biến động)", "lead": "tu_vi"},
    {"id": 8,  "ten": "Con cái — cách nuôi dưỡng/truyền tính", "lead": "tu_vi"},
    {"id": 9,  "ten": "Cha mẹ / anh chị em",                   "lead": "bat_tu"},
    {"id": 10, "ten": "Tâm lý/EQ hôn nhân (khí số)",           "lead": "tu_vi"},
    {"id": 11, "ten": "Tài sản chung / kinh tế gia đình",      "lead": "bat_tu"},
    {"id": 12, "ten": "Định khắc giờ sinh (định bàn)",         "lead": "tu_vi"},
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().replace("đ", "d")


def _concord(lead_dir: Optional[str], cross_dir: Optional[str]) -> str:
    """Đồng-tham nếu cùng hướng; dị-tham nếu lệch; một-phía nếu thiếu 1 phía."""
    if lead_dir is None or cross_dir is None:
        return CONCORD_MOT
    return CONCORD_DONG if lead_dir == cross_dir else CONCORD_DI


def _reframe_check(text: str) -> tuple[bool, list[str]]:
    """(paradigm_ok, flags). ok=False nếu dính giọng tiên tri (Iron #4/#6/#8)."""
    flags = paradigm_violations(text or "")
    return (not flags), flags


# ── hướng TỔNG mỗi engine (xấp xỉ foundation; per-khía-cạnh tinh chỉnh sau) ──────
_BT_NEG = ("cang", "xung", "khac", "hung", "ky", "hao", "pha", "yeu", "tan", "kiep")
_BT_POS = ("thuan", "tot", "cat", "on", "vuong", "manh", "dep", "hop", "vien")


def _dir_bat_tu(out: Optional[dict]) -> Optional[str]:
    if not out:
        return None
    label = _norm(str((out.get("overall") or {}).get("label", "")))
    if any(k in label for k in _BT_NEG):
        return "cang"
    if any(k in label for k in _BT_POS):
        return "thuan"
    if out.get("warnings"):
        return "cang"
    return "thuan" if out.get("overall") else None


def _dir_tu_vi(out: Optional[dict]) -> Optional[str]:
    if not out:
        return None
    # Bất kỳ rule Q* nào "hit" (vd Hóa Kỵ/Sát/Tuần Triệt ở Phu Thê) → điểm căng.
    if any(isinstance(v, dict) and v.get("hit") for v in out.values()):
        return "cang"
    return "thuan" if out else None


def _reading_bat_tu(out: Optional[dict]) -> str:
    if not out:
        return ""
    ov = (out.get("overall") or {}).get("narrative")
    cp = (out.get("cung_phoi") or {}).get("trait_narrative")
    return str(ov or cp or "")


def _reading_tu_vi(out: Optional[dict]) -> str:
    if not out:
        return ""
    if out.get("phu_the_tong_quan"):
        return str(out["phu_the_tong_quan"])
    notes = [v.get("note") for v in out.values() if isinstance(v, dict) and v.get("note")]
    return " · ".join(str(n) for n in notes if n)


def _sources_of(out: Optional[dict], school: str) -> list[str]:
    if not out:
        return []
    if school == "bat_tu" and out.get("source_ref"):
        return [str(out["source_ref"])]
    src = out.get("sources") or out.get("source_ref")
    return [str(src)] if src else []


def _read_dir_src(out, school):
    if school == "bat_tu":
        return _reading_bat_tu(out), _dir_bat_tu(out), _sources_of(out, "bat_tu")
    return _reading_tu_vi(out), _dir_tu_vi(out), _sources_of(out, "tu_vi")


def luan_hon_nhan_song_phai(*, bat_tu_state: dict, la_so: dict) -> dict[str, Any]:
    """Hợp nhất Bát Tự ↔ Tử Vi → 12 khía cạnh hôn nhân + cờ đồng/dị-tham.

    An toàn: 1 engine lỗi → khía cạnh phái đó `unsourced`/`một_phía`, KHÔNG sập;
    lỗi ghi vào `engine_errors` (minh bạch). Mọi reading qua paradigm guard.
    """
    engine_errors: list[str] = []
    try:
        bt_out = analyze_hon_nhan(bat_tu_state)
    except Exception as e:  # noqa: BLE001 — engine con lỗi không được làm sập orchestrator
        bt_out, _ = None, engine_errors.append(f"bat_tu: {e}")
    try:
        tv_out = chiem_phu_the_v4(la_so)
    except Exception as e:  # noqa: BLE001
        tv_out, _ = None, engine_errors.append(f"tu_vi: {e}")

    out_by_school = {"bat_tu": bt_out, "tu_vi": tv_out}
    khia_canh: list[dict] = []
    all_paradigm_ok = True

    for asp in ASPECTS:
        lead_s = asp["lead"]
        cross_s = "tu_vi" if lead_s == "bat_tu" else "bat_tu"
        lead_reading, lead_dir, lead_src = _read_dir_src(out_by_school[lead_s], lead_s)
        cross_reading, cross_dir, cross_src = _read_dir_src(out_by_school[cross_s], cross_s)

        ok_l, fl_l = _reframe_check(lead_reading)
        ok_c, fl_c = _reframe_check(cross_reading)
        paradigm_ok = ok_l and ok_c
        all_paradigm_ok = all_paradigm_ok and paradigm_ok

        sources = lead_src + cross_src
        khia_canh.append({
            "id": asp["id"],
            "ten": asp["ten"],
            "lead_school": lead_s,
            "lead_reading": lead_reading or "(unsourced — chưa wiring tín hiệu per-khía-cạnh)",
            "cross_reading": cross_reading or "(unsourced)",
            "concord": _concord(lead_dir, cross_dir),
            "note": ("dị-tham: giữ CẢ HAI quan điểm, thận trọng"
                     if _concord(lead_dir, cross_dir) == CONCORD_DI else ""),
            "sources": sources,
            "unsourced": not sources,
            "paradigm_ok": paradigm_ok,
            "paradigm_flags": (fl_l + fl_c) or None,
        })

    return {
        "method_id": "hon_nhan_song_phai_v0",
        "paradigm": "Đọc đồng dạng, KHÔNG predict. Bát Tự=THỂ, Tử Vi=DỤNG; mệnh là động từ.",
        "khia_canh": khia_canh,
        "paradigm_ok": all_paradigm_ok,
        "engine_errors": engine_errors,
    }
