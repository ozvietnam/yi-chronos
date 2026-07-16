"""Tượng loại vạn vật Mai Hoa — seed đã-nối vào interpret (audit 2026-07-16).

Trước fix: seed `data/seeds/mai_hoa_tuong_loai_van_vat.json` (Thiệu Vĩ Hoa
p45-60, 8 quẻ × 28 thuộc tính) tồn tại nhưng 0-ref — engine chỉ dùng
QUAI_VAN_VAT rút gọn 1 dòng ("hút mà chưa nối").

Sau fix: mỗi lượt interpret mang `tuong_loai_van_vat` = bảng đầy đủ cho các
quẻ xuất hiện trong Chính/Hỗ/Biến, kèm source đích danh.
"""

from __future__ import annotations

BAT_QUAI = {"Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"}


def test_get_tuong_loai_van_vat_lookup():
    from engine.yi_wiki.interpret import get_tuong_loai_van_vat

    can = get_tuong_loai_van_vat("Càn")
    assert can is not None
    # Đủ các mục chính của bảng tượng loại (không phải bản rút gọn 1 dòng)
    for key in ("thien_thoi", "dia_ly", "nhan_vat", "tinh_cach"):
        assert can.get(key), f"thiếu mục {key}"
    assert get_tuong_loai_van_vat("KhôngPhảiQuẻ") is None


def test_analyze_carries_tuong_loai_for_cast_que():
    from engine.yi_wiki.cast import cast_by_time
    from engine.yi_wiki.interpret import analyze

    cast = cast_by_time("Ngọ", 5, 15, "Mùi")
    r = analyze(cast, month=5)

    tl = r.tuong_loai_van_vat
    assert tl, "kết quả phải mang bảng tượng loại (seed có trong repo)"
    assert "Thiệu Vĩ Hoa" in (tl.get("source") or "")

    que_in_cast = {
        cast.chinh_quai.upper_que, cast.chinh_quai.lower_que,
        cast.ho_quai.upper_que, cast.ho_quai.lower_que,
        cast.bien_quai.upper_que, cast.bien_quai.lower_que,
    }
    assert set(tl["que"].keys()) == que_in_cast
    assert set(tl["que"].keys()) <= BAT_QUAI
    for que, rec in tl["que"].items():
        assert rec.get("nhan_vat"), f"quẻ {que} thiếu mục nhân vật"


def test_api_interpret_returns_tuong_loai():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-wiki/interpret", json={
        "year_chi": "Ngọ", "month": 5, "day": 15, "hour_chi": "Mùi",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    tl = body["tuong_loai_van_vat"]
    assert tl["que"]
    assert set(tl["que"].keys()) <= BAT_QUAI
