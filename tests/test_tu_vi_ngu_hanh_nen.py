"""Nền Âm Dương Ngũ Hành cho Tử Vi — sinh khắc sao↔đất cung (2026-06-12)."""
from engine.tu_vi.ngu_hanh_nen import (
    HANH_CHI, SINH, KHAC, quan_he, sao_tai_cung, vong_sinh_khac,
)


def test_hanh_chi_du_12():
    assert len(HANH_CHI) == 12
    assert HANH_CHI["Tỵ"] == "hỏa"
    assert HANH_CHI["Tý"] == "thủy"
    assert sum(1 for h in HANH_CHI.values() if h == "thổ") == 4  # Thìn Tuất Sửu Mùi


def test_vong_sinh_khac_khep_kin():
    # Vòng sinh + vòng khắc mỗi hành xuất hiện đúng 1 lần ở mỗi vai
    assert set(SINH) == set(SINH.values()) == set(KHAC) == set(KHAC.values())
    assert SINH["thủy"] == "mộc" and KHAC["thủy"] == "hỏa"


def test_quan_he_cac_truong_hop():
    assert quan_he("mộc", "mộc")["code"] == "dong_hanh"
    assert quan_he("mộc", "hỏa")["code"] == "a_sinh_b"
    assert quan_he("hỏa", "mộc")["code"] == "b_sinh_a"
    assert quan_he("thủy", "hỏa")["code"] == "a_khac_b"
    assert quan_he("hỏa", "thủy")["code"] == "b_khac_a"


def test_sao_tai_cung_thien_dong_ty():
    """Thiên Đồng (thủy) tại Tỵ (hỏa) — sao khắc đất, bảng Q2 vẫn miếu."""
    r = sao_tai_cung("Thiên Đồng", "Tỵ")
    assert r is not None
    assert r["hanh_sao"] == "thủy" and r["hanh_cung"] == "hỏa"
    assert r["quan_he"]["code"] == "a_khac_b"
    assert r["mieu_ham"] == "miếu"
    assert r["nhan_dinh"]  # luôn có nhận định cơ chế
    assert r["hoa_khi"] == "phúc"


def test_sao_tai_cung_ghi_chu_lech_trung_thuc():
    """Khi bảng cổ xếp miếu/vượng mà hành đơn nghịch (đất khắc sao / sao hao)
    → phải có ghi chú đối chiếu trung thực, không ép khớp."""
    hits = 0
    for chi in HANH_CHI:
        for sao in ("Tử Vi", "Thiên Cơ", "Thái Âm", "Vũ Khúc", "Thiên Đồng"):
            r = sao_tai_cung(sao, chi)
            if not r:
                continue
            nghich = r["quan_he"]["code"] in ("b_khac_a", "a_sinh_b")
            if r["mieu_ham"] in ("miếu", "vượng") and nghich:
                assert r["ghi_chu_lech"], f"{sao}@{chi} thiếu ghi chú lệch"
                hits += 1
    assert hits >= 1, "bảng cổ chắc chắn có chỗ lệch hành đơn — phải bắt được ít nhất 1"


def test_sao_tai_cung_hoa_giai_khi_khac():
    """Cung có KHẮC → hoa_giai chỉ chế (khắc lại kẻ đi khắc) + hóa (thông quan).
    Cung sinh/đồng hành → hoa_giai = None (chỉ khắc mới cần hóa giải)."""
    # Thiên Tướng (thủy) khắc Tỵ (hỏa): a_khac_b, attacker=thủy victim=hỏa
    r = sao_tai_cung("Thiên Tướng", "Tỵ")
    assert r["quan_he"]["code"] == "a_khac_b"
    hg = r["hoa_giai"]
    assert hg is not None
    # chế = con của victim(hỏa)=thổ; thổ khắc lại attacker(thủy)
    assert hg["che"] == SINH["hỏa"] == "thổ" and KHAC["thổ"] == "thủy"
    # hóa = con của attacker(thủy)=mộc; mộc sinh xuống victim(hỏa)
    assert hg["hoa"] == SINH["thủy"] == "mộc" and SINH["mộc"] == "hỏa"
    assert hg["mo_ta"]
    # Đồng hành / tương sinh → không có hoa_giai
    dong = sao_tai_cung("Thiên Phủ", "Sửu")  # thổ/thổ đồng hành
    assert dong["quan_he"]["code"] == "dong_hanh" and dong["hoa_giai"] is None


def test_sao_khong_ton_tai():
    assert sao_tai_cung("Sao Bịa", "Tý") is None
    assert sao_tai_cung("Tử Vi", "Chi Bịa") is None


def test_vong_sinh_khac_payload_ui():
    v = vong_sinh_khac()
    assert len(v["vong_sinh"]) == 5 and len(v["vong_khac"]) == 5
    assert "am_duong" in v["dinh_nghia"] and "sinh_khac" in v["dinh_nghia"]
