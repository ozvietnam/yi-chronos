"""Thần sát Lục Hào — seed than_sat_7_sao.json đã-nối (audit 2026-07-16).

Trước fix: seed (Thiệu Vĩ Hoa p99-103) tồn tại nhưng engine Lục Hào 0-ref —
quý nhân / dịch mã / đào hoa / kình dương / lộc / hoa cái / thiên la địa võng
không bao giờ surface trong quẻ.
"""

from __future__ import annotations


def _lines(branches: list[str]) -> list[dict]:
    return [
        {"line_position": i + 1, "branch": b} for i, b in enumerate(branches)
    ]


def test_quy_nhan_giap_day_hits_suu_mui():
    from engine.luc_hao.than_sat import compute_than_sat

    out = compute_than_sat("Giáp", "Tý", _lines(["Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Mùi"]))
    assert out["source"] and "Thiệu Vĩ Hoa" in out["source"]
    qn = next(s for s in out["sao"] if s["key"] == "quy_nhan_thien_at")
    assert qn["lines_hit"] == [1, 6]           # Sửu (hào 1) + Mùi (hào 6)
    assert set(qn["target_branches"]) == {"Sửu", "Mùi"}
    assert qn["y_nghia"]


def test_dich_ma_dao_hoa_by_tam_hop_of_day_branch():
    from engine.luc_hao.than_sat import compute_than_sat

    # Ngày Tý thuộc cục Thân-Tý-Thìn → Dịch Mã = Dần, Đào Hoa = Dậu
    out = compute_than_sat("Bính", "Tý", _lines(["Dần", "Dậu", "Ngọ", "Tuất", "Hợi", "Tý"]))
    ma = next(s for s in out["sao"] if s["key"] == "sao_ma_dich_ma")
    assert ma["target_branches"] == ["Dần"] and ma["lines_hit"] == [1]
    dh = next(s for s in out["sao"] if s["key"] == "dao_hoa_ham_tri")
    assert dh["target_branches"] == ["Dậu"] and dh["lines_hit"] == [2]


def test_only_hit_sao_are_listed():
    from engine.luc_hao.than_sat import compute_than_sat

    # 6 hào không trúng chi đích nào của ngày Giáp Tý ngoài Lộc (Dần)
    out = compute_than_sat("Giáp", "Tý", _lines(["Dần", "Ngọ", "Ngọ", "Ngọ", "Ngọ", "Ngọ"]))
    keys = {s["key"] for s in out["sao"]}
    assert "loc_thap_can" in keys              # Lộc Giáp = Dần → hào 1
    assert "quy_nhan_thien_at" not in keys     # không có Sửu/Mùi trong 6 hào


def test_cast_luc_hao_carries_than_sat():
    from engine.luc_hao.cast import cast_luc_hao
    from engine.luc_hao.casting import InteractionSignal

    r = cast_luc_hao(
        datetime_local="2026-07-16T10:30:00",
        timezone="Asia/Ho_Chi_Minh",
        question_text="Thử thần sát",
        interaction=InteractionSignal(
            hold_duration_ms=1200, move_event_count=7,
            path_length_px=345.6, release_timestamp_ms=1720000000000,
        ),
    )
    ts = r["than_sat"]
    assert ts, "seed có trong repo → phải nạp được"
    assert ts["iron_rule"]                     # "KHÔNG predict tuyệt đối"
    for sao in ts["sao"]:
        assert sao["lines_hit"], "chỉ liệt kê sao có hào trúng"
        assert sao["ten"] and sao["y_nghia"]
