"""H4 — gieo duyên engine (G1–G4): nạp âm + cung mệnh bát trạch, tuổi hợp,
tuổi kết hôn, chấm điểm hàng loạt theo compatKey.

Paradigm guard (Iron Rule #6/#8): KHÔNG tiên tri "sẽ hạnh phúc/ly hôn"; chỉ đọc
cấu trúc tương hợp (đồng dạng). Con số/sao = chỉ dấu cấu trúc, không phải số phận.
"""
from __future__ import annotations

import pytest


# ─── G1 helpers: can-chi, nạp âm, cung phi bát trạch ─────────────────────────

def test_year_to_can_chi_anchor():
    from engine.bat_tu.gieo_duyen import year_to_can_chi
    assert year_to_can_chi(1984)[:2] == ("Giáp", "Tý")
    assert year_to_can_chi(1990)[:2] == ("Canh", "Ngọ")
    assert year_to_can_chi(1986)[:2] == ("Bính", "Dần")


def test_nap_am_for_year():
    from engine.bat_tu.gieo_duyen import nap_am_for_year
    na = nap_am_for_year(1986)  # Bính Dần → Lư Trung Hỏa
    assert na["name"] == "Lư Trung Hỏa"
    assert na["element"] == "hỏa"


@pytest.mark.parametrize("year,gender,quai,group", [
    (1984, "nam", "Đoài", "tay"),
    (1984, "nữ", "Cấn", "tay"),
    (1990, "nam", "Khảm", "dong"),
    (2000, "nam", "Đoài", "tay"),
    (2000, "nữ", "Cấn", "tay"),
])
def test_cung_phi_bat_trach(year, gender, quai, group):
    from engine.bat_tu.gieo_duyen import cung_phi
    c = cung_phi(year, gender)
    assert c["quai"] == quai
    assert c["menh_group"] == group


def test_profile_derived_g1():
    from engine.bat_tu.gieo_duyen import profile_derived
    p = profile_derived(1986, "nam")
    assert p["nap_am"]["name"] == "Lư Trung Hỏa"
    assert p["cung_menh"]["quai"]
    assert "paradigm_guard" in p


# ─── G2: tuổi hợp ────────────────────────────────────────────────────────────

def test_compatible_years_shape_and_order():
    from engine.bat_tu.gieo_duyen import compatible_years
    out = compatible_years(1990, top=6)
    assert 1 <= len(out) <= 6
    for it in out:
        assert {"year", "can_chi", "grade", "reason", "score"} <= set(it)
    scores = [it["score"] for it in out]
    assert scores == sorted(scores, reverse=True)


def test_compatible_years_luc_hop_ranks_high():
    # User 1990 = Ngọ; Ngọ–Mùi lục hợp → năm chi Mùi nên xếp hạng cao.
    from engine.bat_tu.gieo_duyen import compatible_years
    out = compatible_years(1990, span=10, top=8)
    mui_years = [it for it in out if it["can_chi"].split()[1] == "Mùi"]
    assert mui_years, "expected a Mùi candidate in range"
    assert mui_years[0]["score"] > 0


# ─── G3: tuổi kết hôn ────────────────────────────────────────────────────────

def test_marriage_years_deterministic():
    from engine.bat_tu.gieo_duyen import marriage_years
    out = marriage_years("1990-08-20T09:30:00", "nam", from_year=2026, count=3, scan=6)
    assert 1 <= len(out) <= 3
    for it in out:
        assert it["year"] >= 2026
        assert {"year", "can_chi", "grade", "reason"} <= set(it)
    # Hàm thuần → chạy lại cho kết quả y hệt.
    out2 = marriage_years("1990-08-20T09:30:00", "nam", from_year=2026, count=3, scan=6)
    assert [x["year"] for x in out] == [x["year"] for x in out2]


# ─── G4: compat-batch theo compatKey ─────────────────────────────────────────

def test_compat_key_and_batch():
    from engine.bat_tu.gieo_duyen import compat_key, compat_batch
    anchor = compat_key(1990, day_master="Giáp")
    cands = [
        {"id": "a", **compat_key(1991, day_master="Kỷ")},   # Mùi + hợp can Giáp-Kỷ
        {"id": "b", **compat_key(1996, day_master="Canh")},  # Tý xung Ngọ
    ]
    res = compat_batch(anchor, cands)
    assert len(res) == 2
    for r in res:
        assert 0 <= r["percent"] <= 100
        assert 1 <= r["stars"] <= 5
        assert "highlight" in r
    # Sorted desc by score; the hợp-can + lục-hợp candidate ('a') should win.
    assert res[0]["id"] == "a"
    scores = [r["score"] for r in res]
    assert scores == sorted(scores, reverse=True)


# ─── API endpoints (G1–G4) ───────────────────────────────────────────────────

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)


def test_api_profile_derived(client):
    r = client.post("/api/bat-tu/profile-derived", json={"birth_year": 1986, "gender": "nam"})
    assert r.status_code == 200, r.text
    j = r.json()
    assert "profile_derived" in j["profile_derived"] or "nap_am" in j["profile_derived"]
    assert j["profile_derived"]["nap_am"]["name"] == "Lư Trung Hỏa"
    assert j["algo_version"].endswith("profile_derived-1")


def test_api_compatible_years(client):
    r = client.post("/api/bat-tu/compatible-years", json={"birth_year": 1990, "top": 5})
    assert r.status_code == 200, r.text
    j = r.json()
    assert len(j["compatible_years"]) <= 5
    assert "paradigm_guard" in j
    assert j["algo_version"].endswith("compatible_years-1")


def test_api_marriage_years(client):
    r = client.post("/api/bat-tu/marriage-years", json={
        "birth_datetime_local": "1990-08-20T09:30:00", "gender": "nam",
        "from_year": 2026, "count": 3})
    assert r.status_code == 200, r.text
    j = r.json()
    assert all(it["year"] >= 2026 for it in j["marriage_years"])
    assert j["algo_version"].endswith("marriage_years-1")


def test_api_compat_batch(client):
    from engine.bat_tu.gieo_duyen import compat_key
    body = {
        "anchor": compat_key(1990, day_master="Giáp"),
        "candidates": [
            {"id": "a", **compat_key(1991, day_master="Kỷ")},
            {"id": "b", **compat_key(1996, day_master="Canh")},
        ],
    }
    r = client.post("/api/bat-tu/compat-batch", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["count"] == 2
    assert j["scores"][0]["id"] == "a"
    assert j["algo_version"].endswith("couple_match-1")
