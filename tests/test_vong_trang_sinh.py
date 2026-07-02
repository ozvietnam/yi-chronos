"""Vòng Trường Sinh (12 sao) trên địa bàn Tử Vi — an_sao.vong_trang_sinh.

Khoá công thức an sao (xương tất định, Iron #6/#9): khởi theo Cục + chiều thuận/nghịch.
Điểm KHÁC Bát Tự: Thổ khởi THÂN (水土同宫), KHÔNG phải Dần (火土同宫 của Bát Tự).
Verify 2 data point thật: lá số founder + giáo cụ 'GIẢI MÃ ĐỊA BÀN'.
"""
from engine.tu_vi.an_sao import vong_trang_sinh, _TRUONG_SINH_12
from engine.tu_vi.from_birth import cast_la_so_from_birth

B = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def _by_branch(ts: dict) -> dict:
    return {B[idx]: name for name, idx in ts.items()}


def test_bijection_12_sao_12_cung():
    ts = vong_trang_sinh(5, "Mậu", "nam")
    assert len(ts) == 12
    assert set(ts.keys()) == set(_TRUONG_SINH_12)
    assert len(set(ts.values())) == 12          # 12 cung phân biệt


def test_khoi_theo_cuc_thuan():
    """Dương nam → thuận. Trường Sinh khởi đúng cung theo Cục."""
    # Thủy nhị → Thân, Mộc tam → Hợi, Kim tứ → Tỵ, Thổ ngũ → Thân, Hỏa lục → Dần
    for cuc, start in [(2, "Thân"), (3, "Hợi"), (4, "Tỵ"), (5, "Thân"), (6, "Dần")]:
        ts = vong_trang_sinh(cuc, "Giáp", "nam")   # Giáp dương + nam → thuận
        assert _by_branch(ts)[start] == "Trường Sinh", f"Cục {cuc} phải khởi {start}"


def test_tho_khoi_than_khac_bat_tu():
    """Tử Vi: Thổ ngũ cục Trường Sinh tại THÂN (水土同宫) — KHÁC Bát Tự (Dần)."""
    ts = vong_trang_sinh(5, "Giáp", "nam")
    assert _by_branch(ts)["Thân"] == "Trường Sinh"
    assert _by_branch(ts)["Dần"] != "Trường Sinh"


def test_chieu_thuan_nghich_theo_am_duong_nam_nu():
    # Thủy nhị (khởi Thân). Dương nam → thuận: Thân,Dậu,Tuất… ; Âm nam → nghịch: Thân,Mùi,Ngọ…
    thuan = _by_branch(vong_trang_sinh(2, "Giáp", "nam"))   # dương nam
    nghich = _by_branch(vong_trang_sinh(2, "Ất", "nam"))    # âm nam
    assert thuan["Dậu"] == "Mộc Dục"     # thuận: Thân→Dậu
    assert nghich["Mùi"] == "Mộc Dục"    # nghịch: Thân→Mùi


def test_founder_menh_ty_tuyet():
    """Founder: Thổ ngũ cục, Mậu (dương) nam → thuận → Mệnh Tỵ = Tuyệt."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    assert "trang_sinh" in r
    rev = {idx: name for name, idx in r["trang_sinh"].items()}
    menh = next(p for p in r["palaces"] if p["name"] == "Mệnh")
    assert rev[menh["branch_index"]] == "Tuyệt"


def test_giao_cu_thuy_nhi_nghich_menh_ty_lam_quan():
    """Ảnh 'GIẢI MÃ ĐỊA BÀN': Thủy nhị cục (gốc đại vận=2), đi nghịch → Mệnh Tỵ = Lâm Quan."""
    ts = vong_trang_sinh(2, "Ất", "nam")   # âm nam → nghịch
    assert _by_branch(ts)["Tỵ"] == "Lâm Quan"


# ── Năm tiểu vận + nguyệt vận (2 lớp cuối GIẢI MÃ ĐỊA BÀN) ────────────────────
def test_tieu_van_bijection_va_founder():
    """Năm tiểu vận: song ánh năm-chi ↔ cung. Founder (Thìn, nam) → Mệnh Tỵ = năm Hợi."""
    from engine.tu_vi.an_sao import tieu_van_per_cung
    tv = tieu_van_per_cung("Thìn", "nam")
    assert len(tv) == 12 and len(set(tv.values())) == 12       # 12 cung ↔ 12 chi
    assert tv[5] == "Hợi"                                       # cung Tỵ (idx5) → năm Hợi (khớp ảnh)


def test_nguyet_van_bijection_va_dau_quan_2026():
    """Nguyệt vận: song ánh tháng ↔ cung. 2026 (Ngọ) founder tháng4 giờ Tý → cung Hợi = T.9."""
    from engine.tu_vi.an_sao import nguyet_van_per_cung
    nv = nguyet_van_per_cung("Ngọ", 4, "Tý")
    assert len(nv) == 12 and len(set(nv.values())) == 12       # 12 tháng phân biệt
    assert nv[11] == 9                                          # cung Hợi (idx11) → T.9 (khớp ảnh)


def test_cast_output_co_tieu_van():
    """Cast base LUÔN kèm tieu_van (tĩnh, không cần chọn năm)."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    assert "tieu_van" in r and len(r["tieu_van"]) == 12
