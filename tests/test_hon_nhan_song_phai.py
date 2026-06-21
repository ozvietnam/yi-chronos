"""#55 — Hợp nhất SONG PHÁI Bát Tự (THỂ) ↔ Tử Vi (DỤNG) cho hôn nhân/gia đình.

Test phần LÕI orchestrator liên-phái (mock engine con, theo spec): 12 khía cạnh +
thuật toán đồng/dị-tham + paradigm guard (đọc đồng dạng, KHÔNG predict — Iron #4/#6/#8).
"""
from __future__ import annotations

import engine.cross_paradigm.hon_nhan_song_phai as M


def test_co_du_12_khia_canh():
    assert len(M.ASPECTS) == 12
    ids = [a["id"] for a in M.ASPECTS]
    assert ids == list(range(1, 13)), "phải đủ id 1..12 theo ma trận issue #55"
    # mỗi khía cạnh có phái dẫn hợp lệ
    for a in M.ASPECTS:
        assert a["lead"] in ("bat_tu", "tu_vi"), a


def test_concord_dong_di_mot_phia():
    # cùng hướng → đồng tham (tin cao)
    assert M._concord("thuan", "thuan") == "đồng_tham"
    assert M._concord("cang", "cang") == "đồng_tham"
    # lệch hướng → dị tham (giữ cả hai)
    assert M._concord("thuan", "cang") == "dị_tham"
    # 1 phái không có tín hiệu → một phía
    assert M._concord("thuan", None) == "một_phía"
    assert M._concord(None, "cang") == "một_phía"


def test_reframe_flag_giong_predict():
    """Câu giọng tiên tri (vợ sẽ giàu / sẽ ly hôn / năm X cưới) → paradigm_ok=False."""
    ok, flags = M._reframe_check("Vợ anh sẽ giàu và hai người sẽ ly hôn năm 2026")
    assert ok is False and flags, "phải bắt giọng predict"
    ok2, flags2 = M._reframe_check(
        "Cấu trúc Phu Thê của anh vận hành mạnh nhất khi anh chủ động quan sát quan hệ tài-tình"
    )
    assert ok2 is True and not flags2, "câu đọc-đồng-dạng/động-từ phải sạch"


def _fake_bat_tu(label="thuận"):
    return {
        "overall": {"label": label, "score": 70, "narrative": "Cung phối ổn định."},
        "cung_phoi": {"trait_narrative": "Phối ngẫu khí chất Thổ, trầm ổn."},
        "warnings": [],
        "source_ref": "tu-binh-q1",
    }


def _fake_tu_vi(tense=False):
    base = {"phu_the_tong_quan": "Phu Thê có Thiên Tướng, ôn hoà."}
    if tense:
        base["Q14_vu_khuc_ki_sn_phu"] = {"hit": True, "note": "Vũ Khúc Hóa Kỵ — điểm căng tài-tình"}
    return base


def test_luan_song_phai_tra_12_khia_canh_co_concord(monkeypatch):
    monkeypatch.setattr(M, "analyze_hon_nhan", lambda st: _fake_bat_tu("thuận"))
    monkeypatch.setattr(M, "chiem_phu_the_v4", lambda ls: _fake_tu_vi(tense=False))
    out = M.luan_hon_nhan_song_phai(bat_tu_state={"tu_tru": {}}, la_so={})
    kc = out["khia_canh"]
    assert len(kc) == 12
    for a in kc:
        assert set(a) >= {"id", "ten", "lead_school", "lead_reading", "cross_reading",
                          "concord", "sources", "paradigm_ok"}
        assert a["concord"] in ("đồng_tham", "dị_tham", "một_phía")
        assert a["paradigm_ok"] is True, "không câu predict nào lọt"


def test_di_tham_giu_ca_hai_khong_chon_phai(monkeypatch):
    """Bát Tự 'thuận' nhưng Tử Vi báo 'căng' → dị_tham PHẢI giữ cả hai reading (kept_all)."""
    monkeypatch.setattr(M, "analyze_hon_nhan", lambda st: _fake_bat_tu("thuận"))
    monkeypatch.setattr(M, "chiem_phu_the_v4", lambda ls: _fake_tu_vi(tense=True))
    out = M.luan_hon_nhan_song_phai(bat_tu_state={"tu_tru": {}}, la_so={})
    di = [a for a in out["khia_canh"] if a["concord"] == "dị_tham"]
    assert di, "phải có ít nhất 1 khía cạnh dị_tham khi 2 phái lệch hướng"
    for a in di:
        assert a["lead_reading"] and a["cross_reading"], "dị_tham giữ CẢ HAI, không bỏ phái nào"


def test_engine_loi_khong_lam_sap_tra_unsourced(monkeypatch):
    """1 engine ném lỗi → orchestrator KHÔNG sập, khía cạnh phái đó → unsourced/một_phía."""
    def boom(_):
        raise RuntimeError("engine lỗi")
    monkeypatch.setattr(M, "analyze_hon_nhan", boom)
    monkeypatch.setattr(M, "chiem_phu_the_v4", lambda ls: _fake_tu_vi(tense=False))
    out = M.luan_hon_nhan_song_phai(bat_tu_state={"tu_tru": {}}, la_so={})
    assert len(out["khia_canh"]) == 12  # vẫn đủ 12, không sập
    assert out.get("engine_errors"), "phải ghi nhận engine lỗi (minh bạch)"
