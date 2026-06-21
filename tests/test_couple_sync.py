"""#56 — Luận SO ĐÔI đích danh (2 lá số): Bát Tự hợp hôn + Tử Vi Phu Thê chéo.

Test phần LÕI orchestrator so-đôi (mock engine con). Cùng primitive đồng/dị-tham +
paradigm guard với #55 (qua _common). Giá đã chốt 30 xu (issue #56).
"""
from __future__ import annotations

import engine.cross_paradigm.couple_sync as C


def _fake_compat(label="hợp", narrative="Hai bên bổ khuyết ngũ hành, tương hỗ."):
    return {"overall": {"label": label, "score": 75, "narrative": narrative},
            "source_ref": "tu-binh-compat"}


def _fake_phu_the(tense=False):
    d = {"phu_the_tong_quan": "Phu Thê Thiên Tướng, ôn hoà."}
    if tense:
        d["Q14"] = {"hit": True, "note": "Hóa Kỵ — điểm căng tài-tình"}
    return d


def _ppl():
    return ({"bat_tu_state": {"tu_tru": {}}, "la_so": {}},
            {"bat_tu_state": {"tu_tru": {}}, "la_so": {}})


def test_luan_so_doi_co_concord_paradigm_va_gia(monkeypatch):
    monkeypatch.setattr(C, "analyze_compatibility", lambda a, b, **k: _fake_compat("hợp"))
    monkeypatch.setattr(C, "chiem_phu_the_v4", lambda ls: _fake_phu_the(False))
    a, b = _ppl()
    out = C.luan_so_doi(person_a=a, person_b=b)
    assert out["concord"] in ("đồng_tham", "dị_tham", "một_phía")
    assert out["paradigm_ok"] is True
    assert out["bat_tu_hop_hon"]["reading"] and out["tu_vi_phu_the_cheo"]["reading"]
    assert out["gia_xu"] == 30  # giá đã chốt issue #56


def test_di_tham_giu_ca_hai(monkeypatch):
    """Bát Tự 'hợp' nhưng Tử Vi Phu Thê 'căng' → dị_tham, giữ CẢ HAI (kept_all)."""
    monkeypatch.setattr(C, "analyze_compatibility", lambda a, b, **k: _fake_compat("hợp"))
    monkeypatch.setattr(C, "chiem_phu_the_v4", lambda ls: _fake_phu_the(tense=True))
    a, b = _ppl()
    out = C.luan_so_doi(person_a=a, person_b=b)
    assert out["concord"] == "dị_tham"
    assert out["bat_tu_hop_hon"]["reading"] and out["tu_vi_phu_the_cheo"]["reading"]


def test_paradigm_predict_bi_flag(monkeypatch):
    monkeypatch.setattr(C, "analyze_compatibility",
                        lambda a, b, **k: _fake_compat("hợp", "Hai người chắc chắn sẽ giàu và sẽ thành công"))
    monkeypatch.setattr(C, "chiem_phu_the_v4", lambda ls: _fake_phu_the(False))
    a, b = _ppl()
    out = C.luan_so_doi(person_a=a, person_b=b)
    assert out["paradigm_ok"] is False and out["paradigm_flags"]


def test_engine_loi_khong_sap(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("engine lỗi")
    monkeypatch.setattr(C, "analyze_compatibility", boom)
    monkeypatch.setattr(C, "chiem_phu_the_v4", lambda ls: _fake_phu_the(False))
    a, b = _ppl()
    out = C.luan_so_doi(person_a=a, person_b=b)
    assert out["engine_errors"], "engine lỗi phải được ghi nhận"
    assert out["tu_vi_phu_the_cheo"]["reading"], "phái còn lại vẫn có kết quả (không sập)"
