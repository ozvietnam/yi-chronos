"""Tests for engine.ha_lac — Bát Tự Hà Lạc.

Includes the canonical worked example from k366.com:
  Bát Tự: 甲子 丁卯 庚申 庚辰 → Tiên thiên = Thiên Phong Cấu (44).
"""

from __future__ import annotations

import pytest

from engine.ha_lac import cast_ha_lac
from engine.ha_lac.constants import BRANCH_NUMBER_PAIRS, STEM_NUMBERS
from engine.ha_lac.hau_thien import _flip_line, derive_hau_thien
from engine.ha_lac.nguyen_duong import hour_branch_rank, nguyen_duong_line
from engine.ha_lac.number_pools import compute_number_pools
from engine.ha_lac.quai_assembly import assemble_tien_thien


# ─── Constants — Hà Đồ numbers ─────────────────────────────────────────────────


def test_stem_numbers_canonical():
    """10 stems must map to the Chen Tuan / Học Năng canonical numbers."""
    assert STEM_NUMBERS["Giáp"] == 6
    assert STEM_NUMBERS["Ất"] == 2
    assert STEM_NUMBERS["Bính"] == 8
    assert STEM_NUMBERS["Đinh"] == 7
    assert STEM_NUMBERS["Mậu"] == 1
    assert STEM_NUMBERS["Kỷ"] == 9
    assert STEM_NUMBERS["Canh"] == 3
    assert STEM_NUMBERS["Tân"] == 4
    assert STEM_NUMBERS["Nhâm"] == 6
    assert STEM_NUMBERS["Quý"] == 2


def test_branch_pairs():
    assert BRANCH_NUMBER_PAIRS["Tý"] == (1, 6)
    assert BRANCH_NUMBER_PAIRS["Hợi"] == (1, 6)
    assert BRANCH_NUMBER_PAIRS["Dần"] == (3, 8)
    assert BRANCH_NUMBER_PAIRS["Ngọ"] == (2, 7)
    assert BRANCH_NUMBER_PAIRS["Thân"] == (4, 9)
    assert BRANCH_NUMBER_PAIRS["Thìn"] == (5, 10)


# ─── Number pools ──────────────────────────────────────────────────────────────


def test_compute_number_pools_canonical_example():
    """Worked example: Bát Tự 甲子 丁卯 庚申 庚辰 → Thiên 31, Địa 34.

    Stems: Giáp=6, Đinh=7, Canh=3, Canh=3  (one even=6, three odd=7,3,3)
    Branches:
      Tý=(1,6), Mão=(3,8), Thân=(4,9), Thìn=(5,10)
      odd: 1,3,9,5 → 4 numbers
      even: 6,8,4,10 → 4 numbers
    Total odd: [7,3,3,1,3,9,5] = 31 (sum)
    Total even: [6,6,8,4,10] = 34
    """
    pillars = {
        "year":  {"stem": "Giáp",  "branch": "Tý"},
        "month": {"stem": "Đinh", "branch": "Mão"},
        "day":   {"stem": "Canh", "branch": "Thân"},
        "hour":  {"stem": "Canh", "branch": "Thìn"},
    }
    pools = compute_number_pools(pillars)
    assert pools.tien_raw == 31
    assert pools.dia_raw == 34
    # Reduce: 31 - 25 = 6; 34 - 30 = 4
    assert pools.tien_reduced == 6
    assert pools.dia_reduced == 4


# ─── Tiên thiên quái assembly ──────────────────────────────────────────────────


def test_assemble_tien_thien_worked_example():
    """Bát Tự 甲子 ... → Thiên 6 (Càn) → upper; Địa 4 (Tốn) → lower → Cấu (44).

    Yang-year (Giáp) + nam → Thiên upper.
    """
    hex_ref = assemble_tien_thien(
        pools_tien_reduced=6,
        pools_dia_reduced=4,
        year_stem="Giáp",
        gender="nam",
    )
    assert hex_ref.upper_trigram == "Càn"
    assert hex_ref.lower_trigram == "Tốn"
    assert hex_ref.king_wen_index == 44   # Thiên Phong Cấu
    assert hex_ref.name_vi == "Cấu"


def test_assemble_tien_thien_yin_year_nam_swaps_upper_lower():
    """Âm năm + nam → Địa upper, Thiên lower."""
    hex_ref = assemble_tien_thien(
        pools_tien_reduced=6,
        pools_dia_reduced=4,
        year_stem="Ất",   # yin year
        gender="nam",
    )
    # Now Địa (4=Tốn) → upper, Thiên (6=Càn) → lower → Phong Thiên Tiểu Súc (#9)
    assert hex_ref.upper_trigram == "Tốn"
    assert hex_ref.lower_trigram == "Càn"


def test_assemble_tien_thien_yang_year_nu_swaps():
    """Dương năm + nữ → Địa upper, Thiên lower (same as âm năm + nam)."""
    hex_ref = assemble_tien_thien(
        pools_tien_reduced=6,
        pools_dia_reduced=4,
        year_stem="Giáp",
        gender="nữ",
    )
    assert hex_ref.upper_trigram == "Tốn"
    assert hex_ref.lower_trigram == "Càn"


def test_assemble_tien_thien_flags_jigong_5():
    """Reduced number = 5 triggers a low-confidence note."""
    hex_ref = assemble_tien_thien(
        pools_tien_reduced=5,
        pools_dia_reduced=4,
        year_stem="Giáp",
        gender="nam",
    )
    assert any("trung cung" in n.lower() or "5 jì-gōng" in n for n in hex_ref.notes)


# ─── Nguyên đường ──────────────────────────────────────────────────────────────


def test_hour_branch_rank():
    assert hour_branch_rank("Tý") == (1, True)
    assert hour_branch_rank("Tỵ") == (6, True)
    assert hour_branch_rank("Ngọ") == (1, False)
    assert hour_branch_rank("Hợi") == (6, False)


def test_nguyen_duong_for_qian_pure():
    """乾為天 (111111) is all yang. Yang hour → walks all 6 yang lines."""
    pos, _ = nguyen_duong_line("111111", "Tý")
    assert pos == 1
    pos, _ = nguyen_duong_line("111111", "Ngọ")
    # All yang, no yin → degenerate, fallback to line 1.
    assert pos == 1


def test_nguyen_duong_for_kun_pure():
    """坤為地 (000000) is all yin."""
    pos, _ = nguyen_duong_line("000000", "Ngọ")
    assert pos == 1
    pos, _ = nguyen_duong_line("000000", "Mùi")
    assert pos == 2


def test_nguyen_duong_for_cau_example():
    """Cấu (Thiên Phong, 111110) — 5 yang + 1 yin.

    Hour Thìn = 5th yang branch (Tý=1, Sửu=2, Dần=3, Mão=4, Thìn=5).
    Yang lines bottom-up: positions 2, 3, 4, 5, 6 (5 yang lines).
    Tý=line 2, Sửu=line 3, Dần=line 4, Mão=line 5, Thìn=line 6.
    """
    pos, _ = nguyen_duong_line("111110", "Thìn")
    assert pos == 6


# ─── Flip line ─────────────────────────────────────────────────────────────────


def test_flip_line_bottom_up():
    """Top-down binary; line 1 = bottom = index 5."""
    assert _flip_line("111111", 1) == "111110"
    assert _flip_line("111111", 6) == "011111"


# ─── Hậu thiên derivation ──────────────────────────────────────────────────────


def test_derive_hau_thien_for_cau_line_6():
    """Cấu (Thiên Phong, 111110, kw=44), nguyên đường line 6, hour Thìn.

    Steps:
      flip line 6 → 011110 (top yin)
      swap upper/lower: upper was 011, becomes lower; lower was 110, becomes upper
      so new = 110 + 011 = 110011 = Tốn upper + Đoài lower = Phong Trạch Trung Phu (61)
    """
    from engine.ha_lac.quai_assembly import HexagramRef

    tien = HexagramRef(
        king_wen_index=44,
        name_vi="Cấu",
        binary_top_down="111110",
        upper_trigram="Càn",
        lower_trigram="Tốn",
        tien_number_reduced=6,
        dia_number_reduced=4,
        upper_source="thien",
        notes=[],
    )
    hau, nd_hau, _ = derive_hau_thien(tien, 6, "Thìn")
    assert hau.king_wen_index == 61   # Phong Trạch Trung Phu
    assert hau.name_vi == "Trung Phu"


# ─── Top-level cast ────────────────────────────────────────────────────────────


def test_cast_ha_lac_complete_shape():
    r = cast_ha_lac(
        birth_datetime_local="1985-08-15T10:30:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert r["method_id"] == "bat_tu_ha_lac_v1"
    assert "tien_thien_quai" in r
    assert "hau_thien_quai" in r
    assert "decade_trajectory" in r
    assert "number_pools" in r
    assert len(r["decade_trajectory"]) == 12
    assert r["lifespan_span"]["total_years"] in range(72, 109)   # 12×6=72 to 12×9=108


def test_cast_ha_lac_rejects_invalid_gender():
    with pytest.raises(ValueError):
        cast_ha_lac(birth_datetime_local="1985-08-15T10:30:00", gender="other")


def test_cast_ha_lac_is_json_serializable():
    import json
    r = cast_ha_lac(birth_datetime_local="1985-08-15T10:30:00")
    s = json.dumps(r, ensure_ascii=False)
    decoded = json.loads(s)
    assert decoded["method_id"] == "bat_tu_ha_lac_v1"


def test_cast_ha_lac_trajectory_nguyen_duong_flagged():
    """The decade trajectory must mark nguyên đường stages."""
    r = cast_ha_lac(birth_datetime_local="1985-08-15T10:30:00")
    nd_stages = [s for s in r["decade_trajectory"] if s["is_nguyen_duong"]]
    # Exactly 2 nguyên đường lines: one in Tiên thiên, one in Hậu thiên.
    assert len(nd_stages) == 2


def test_api_ha_lac_endpoint():
    """Smoke: /api/ha-lac/cast returns valid structure."""
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/ha-lac/cast",
        json={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "gender": "nam",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "ha_lac_state" in payload
    state = payload["ha_lac_state"]
    assert state["method_id"] == "bat_tu_ha_lac_v1"
    assert "tien_thien_quai" in state
    assert "hau_thien_quai" in state
    assert "decade_trajectory" in state
    assert len(state["decade_trajectory"]) == 12
