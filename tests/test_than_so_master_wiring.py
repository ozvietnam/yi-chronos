"""Thần Số — nối master data đã hút (audit 2026-07-16).

Trước fix: `chaldean_compound_numbers.json` (số kép Cheiro 1926) và phần
ý-nghĩa/timing của `cycles.json` (curate 2026-06-05) 0-ref trong engine —
cross_reference Chaldean chỉ trả số trần, pinnacles/challenges chỉ có số.
"""

from __future__ import annotations


def test_compound_info_lookup():
    from engine.than_so.chaldean_compound import compound_info

    rec10 = compound_info(10)
    assert rec10 is not None
    assert "Bánh Xe" in rec10["symbol"]
    assert rec10["meaning_vi"]
    assert rec10["source"]
    # Số đơn → hành tinh Cheiro
    rec1 = compound_info(1)
    assert rec1 is not None and "Mặt Trời" in rec1["planet"]
    # Ngoài bảng → None (không bịa)
    assert compound_info(9999) is None


def test_cast_cross_reference_carries_compound_numbers():
    from engine.than_so.cast import cast_than_so

    r = cast_than_so(name="Nguyen Van A", birth_date="1988-06-05")
    xr = r.get("cross_reference")
    assert xr is not None, "mặc định phải có đối chiếu Chaldean"
    # Số trần giữ nguyên (backward compat)
    assert isinstance(xr["expression"], int)
    # Tầng số kép mới — mọi entry phải có nghĩa + nguồn
    comp = xr["compound_numbers"]
    assert comp, "tên có chữ → tổng Chaldean ≥ 10 → phải tra được số kép"
    for k, v in comp.items():
        assert v["compound"] >= 1
        assert v.get("meaning_vi") or v.get("planet")
        assert v["source"]


def test_pinnacles_carry_meta_from_master():
    from engine.than_so.cycles import pinnacles_and_challenges

    out = pinnacles_and_challenges(day=5, month=6, year=1988)
    meta = out["meta"]
    assert meta, "cycles.json có trong repo → meta phải nạp được"
    assert "Đỉnh Vận" in meta["pinnacles"]["name_vi"]
    assert meta["challenges"]["note"]          # note số 0 = thử thách lựa chọn
    assert "KHÔNG predict" in meta["paradigm_note"]
    # Số vẫn tính đúng như cũ
    assert len(out["pinnacles"]) == 4 and len(out["challenges"]) == 4
