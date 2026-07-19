"""Test BỨC TRANH CUỘC ĐỜI THĂNG TRẦM — life_arc() tất định (0-LLM) + foreground.

Neo [[tu_vi_doc_van_han_goal]] + Iron #9: đường cong = BẢN ĐỒ KHÍ động↔tĩnh, KHÔNG
đồ thị bói giàu-nghèo/thắng-thua. Test XƯƠNG tất định (không cần LLM, không cần DB
đầy đủ — grounded sao rỗng vẫn OK vì chỉ số cấu trúc không phụ thuộc nội dung sao).
"""
import pytest

from engine.tu_vi import van_han as vh

FOUNDER = {"birth_datetime_local": "1988-06-05T23:30:00", "gender": "nam"}


def test_life_arc_thang_shape():
    arc = vh.life_arc(FOUNDER, 2026, 2026, buoc="thang")
    assert arc["available"] and arc["buoc"] == "thang"
    assert len(arc["diem"]) == 12
    p = arc["diem"][0]
    # đủ chỉ số cấu trúc
    for k in ("khi", "dong_tinh", "huong", "dong_luc", "diem_quay",
              "cong_huong", "xa", "duong_hanh", "doc"):
        assert k in p
    assert -1.0 <= p["khi"] <= 1.0
    assert p["dong_tinh"] in ("động", "tĩnh", "trung")
    assert p["duong_hanh"] in ("DÙNG", "TĨNH", "CẨN")


def test_life_arc_nam_shape():
    arc = vh.life_arc(FOUNDER, 2020, 2029, buoc="nam")
    assert len(arc["diem"]) == 10
    assert all(-1.0 <= p["khi"] <= 1.0 for p in arc["diem"])
    assert arc["diem"][0]["label"] == "2020"


def test_life_arc_dai_van_ca_doi():
    """Đường CẢ ĐỜI theo tuổi (Đại vận) — mỗi vận 1 mốc, trục tuổi (giống app tham khảo,
    nhưng KHÍ động↔tĩnh chứ KHÔNG chấm điểm cát-hung)."""
    arc = vh.life_arc(FOUNDER, 2026, 2030, buoc="dai_van")
    assert arc["buoc"] == "dai_van"
    assert len(arc["diem"]) == 12                    # 12 đại vận cả đời
    p = arc["diem"][0]
    assert p["start_age"] is not None and p["end_age"] == p["start_age"] + 9
    assert p["label"].endswith("t")                  # nhãn tuổi "5t"
    assert all(-1.0 <= d["khi"] <= 1.0 for d in arc["diem"])
    # trục tuổi tăng dần
    ages = [d["start_age"] for d in arc["diem"]]
    assert ages == sorted(ages)


def test_foreground_nen_menh():
    """Foreground bẩm sinh: Mệnh chủ + Thân chủ + Cục lên đầu (soil-before-seed)."""
    arc = vh.life_arc(FOUNDER, 2026, 2026, buoc="thang")
    nm = arc["nen_menh"]
    assert nm["menh_chu"] == "Vũ Khúc"       # founder validated (memory project_menh_chu_validated)
    assert nm["than_chu"]
    assert nm["cuc"]["cuc_name"] == "Thổ Ngũ Cục"


def test_founder_arc_matches_design_curve():
    """Bằng chứng đường cong (design §4): T7/2026 THĂNG/động, T8/2026 TRẦM/thu."""
    arc = vh.life_arc(FOUNDER, 2026, 2026, buoc="thang")
    t7 = next(p for p in arc["diem"] if p.get("month") == 7)
    t8 = next(p for p in arc["diem"] if p.get("month") == 8)
    # T7 Mệnh vận Thiên Di (ĐỘNG) + tự hóa Lộc → khí THĂNG (dương), đường hành DÙNG
    assert t7["cung_the"] == "Thiên Di"
    assert t7["huong"] == 1 and t7["khi"] > 0
    assert t7["xa"] is True                  # Thiên Di tự hóa Lộc
    assert t7["duong_hanh"] == "DÙNG"
    # T8 Mệnh vận Tật Ách (TĨNH) + Song Kỵ → khí TRẦM (âm)
    assert t8["cung_the"] == "Tật Ách"
    assert t8["huong"] == -1 and t8["khi"] < 0
    assert t8["duong_hanh"] in ("TĨNH", "CẨN")
    # đường cong đi xuống rõ giữa 2 tháng liền kề
    assert t7["khi"] - t8["khi"] > 0.8


def test_guard_no_cat_hung_labels():
    """Iron #9: KHÔNG có nhãn tốt↔xấu/giàu↔nghèo/thắng↔thua trong output."""
    arc = vh.life_arc(FOUNDER, 2026, 2026, buoc="thang")
    # Chỉ soi phần LUẬN mỗi mốc (đường hành + đọc) — disclaimer được phép nhắc
    # "giàu-nghèo" ở dạng PHỦ ĐỊNH ("KHÔNG đoán giàu-nghèo").
    blob = " ".join(p["doc"] + " " + p["duong_hanh"] for p in arc["diem"]).lower()
    for banned in ("giàu", "nghèo", "thắng", "thua", "tốt xấu", "cát hung", "xui"):
        assert banned not in blob
    # disclaimer soi-tâm bắt buộc
    assert "SOI TÂM" in arc["disclaimer"] or "soi tâm" in arc["disclaimer"].lower()


def test_range_guards():
    with pytest.raises(ValueError):
        vh.life_arc(FOUNDER, 2026, 2060, buoc="thang")   # >30 năm mốc tháng
    with pytest.raises(ValueError):
        vh.life_arc(FOUNDER, 2030, 2020, buoc="nam")     # đảo ngược
    with pytest.raises(ValueError):
        vh.life_arc(FOUNDER, 2026, 2026, buoc="xxx")     # buoc sai


def test_van_han_luan_foreground_wired():
    """van_han_luan block cũng có nen_menh + bao_tram_luu_nien (foreground lồng tầng)."""
    out = vh.van_han_luan(FOUNDER, "luu_nguyet", want_llm=False, year=2026, month=8)
    blk = out["block"]
    assert blk["nen_menh"]["menh_chu"] == "Vũ Khúc"
    assert blk["bao_tram_luu_nien"]["nam_can_chi"]      # năm bao trùm
    assert blk["bao_tram_dai_van"]                      # đại vận bao trùm (đã có)
    # source_text foreground nền bẩm sinh
    assert "NỀN BẨM SINH" in out["source_text"]
