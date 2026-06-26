"""Test reader cung Tử Tức (phương pháp nam-đẩu/bắc-đẩu) — kênh #3 làm giàu engine."""
from engine.tu_vi.tu_tuc_reader import read_tu_tuc, CAVEAT


def _lsi(chinh_tu_tuc, *, chi="dan", phu=None, vong=None, tuan=None, triet=None):
    return {
        "chinh_tinh_per_palace": {"tu_tuc": chinh_tu_tuc, chi: chinh_tu_tuc},
        "phu_tinh_per_palace": {chi: phu or []},
        "vong_sao_per_palace": {chi: vong or []},
        "fn_to_chi": {"tu_tuc": chi},
        "tuan_chi": tuan or [], "triet_chi": triet or [],
    }


def test_caveat_luon_co():
    """Iron Rule: mọi output PHẢI kèm caveat 30/30/40 (không định mệnh)."""
    r = read_tu_tuc(_lsi(["thien_co", "thai_am"]))
    assert r["caveat"] == CAVEAT and "30%" in r["caveat"]
    assert "không phải định mệnh" in r["caveat"].lower()


def test_can_bang_nam_bac():
    """1 nam-đẩu + 1 bắc-đẩu → cân bằng (case founder: Thiên Cơ + Thái Âm)."""
    r = read_tu_tuc(_lsi(["thien_co", "thai_am"], chi="dan"))
    assert "cân bằng" in r["gioi_tinh_con"]["xu_huong"]


def test_thien_trai():
    """Toàn nam-đẩu + Khôi Việt + cung dương → hơi thiên con trai."""
    r = read_tu_tuc(_lsi(["thien_phu", "thien_luong"], chi="thin", phu=["thien_khoi"]))
    assert "trai" in r["gioi_tinh_con"]["xu_huong"]
    assert r["gioi_tinh_con"]["diem_nam"] > r["gioi_tinh_con"]["diem_bac"]


def test_thien_gai():
    """Toàn bắc-đẩu + đào-hồng + cung âm → hơi thiên con gái."""
    r = read_tu_tuc(_lsi(["thai_am", "tham_lang"], chi="mao", phu=["hong_loan"]))
    assert "gái" in r["gioi_tinh_con"]["xu_huong"]
    assert r["gioi_tinh_con"]["diem_bac"] > r["gioi_tinh_con"]["diem_nam"]


def test_phuc_con_thien_dong():
    """Thiên Đồng (phúc tinh) ở Tử Tức → cờ phúc con."""
    r = read_tu_tuc(_lsi(["thien_dong"]))
    assert r["phuc_con"]["co"] is True and "phúc tinh" in r["phuc_con"]["mo_ta"]
    r2 = read_tu_tuc(_lsi(["vu_khuc"]))
    assert r2["phuc_con"]["co"] is False


def test_so_con_giam_co_qua():
    """Cô Thần/Quả Tú/Lộc Tồn → khuynh hướng ít con."""
    r = read_tu_tuc(_lsi(["thien_phu"], phu=["co_than", "qua_tu"]))
    assert "ít" in r["so_con"]["xu_huong"]


def test_so_con_muon_tuan_triet():
    """Tuần/Triệt án cung Tử Tức → con muộn (không vô sinh)."""
    r = read_tu_tuc(_lsi(["thien_phu"], chi="dan", tuan=["dan"]))
    assert any("muộn" in y for y in r["so_con"]["yeu_to"])


def test_vo_chinh_dieu():
    """Vô chính diệu → vẫn đọc được xu hướng nhẹ theo cung."""
    r = read_tu_tuc(_lsi([], chi="ty"))
    assert r["chinh_tinh"] == ["Vô chính diệu"]
    assert r["gioi_tinh_con"]["xu_huong"]


def test_founder_real_chart():
    """Lá số founder thật (1988-06-05 23:30) → Tử Tức Dần, Thiên Cơ + Thái Âm → cân bằng."""
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.la_so_input_builder import build_la_so_input
    ls = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00",
                               timezone="Asia/Ho_Chi_Minh", gender="nam")
    lsi = build_la_so_input(ls, "nam", birth_year=1988, now_year=2026)
    r = read_tu_tuc(lsi)
    assert r["cung_chi"] == "dan"
    assert set(r["chinh_tinh"]) == {"Thiên Cơ", "Thái Âm"}
    assert "cân bằng" in r["gioi_tinh_con"]["xu_huong"]
    assert r["caveat"]
