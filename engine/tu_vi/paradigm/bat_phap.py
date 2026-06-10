"""Bát Pháp — Trần Đoàn Toàn Thư p19-20.

8 lối định cách cục khi xem số:

A. **Thành phá tứ pháp**:
  1. Khoa+Quyền+Lộc+Quý đến → THÀNH (giao long đắc vận, rồng gặp mây)
  2. Hỏa+Linh+Dương+Đà đến → PHÁ (miêu nhi bất tú, mầm không xanh)
  3. Cả Tứ Cát + Tứ Hung → THÀNH có PHÁ (bạch khuê hữu điểm)
  4. Đều không → CHƯA THÀNH CHƯA PHÁ (hỗn kim phác ngọc, chờ thời)

B. **Cứu khí tứ pháp** (mệnh+xung+tam hợp đồng đặc tính):
  5. Lộc+Quý+Quyền+Khoa → CỨU (cửu hạn phùng cam vũ, hạn lâu gặp mưa)
  6. Hỏa+Linh+Dương+Đà → KHÍ (hử mộc nan điêu, gỗ mục)
  7. Cả 2 → VỪA CỨU VỪA KHÍ (thực kê lặc, ăn gân gà)
  8. Đều không → CHỜ THỜI (thủ tàu bảo khuyết)

Nguồn: tdts.S1.Q53-Q54
"""
from __future__ import annotations

BAT_PHAP_CACH = {
    "thanh":            "Giao long đắc vận (rồng gặp mây) — phát đạt như ý",
    "pha":              "Miêu nhi bất tú (mầm không xanh) — phá cách, không thành",
    "thanh_co_pha":     "Bạch khuê hữu điểm (ngọc trắng có vết) — thành có khuyết",
    "chua_thanh":       "Hỗn kim phác ngọc (vàng lẫn tạp) — chờ thời, chưa rõ",
    "cuu":              "Cửu hạn phùng cam vũ (hạn lâu gặp mưa) — cứu cách",
    "khi":              "Hử mộc nan điêu (gỗ mục) — khí cách, bỏ đi",
    "vua_cuu_vua_khi":  "Thực kê lặc (ăn gân gà) — vừa cứu vừa khí",
    "cho_thoi":         "Thủ tàu bảo khuyết — chờ thời để đợi cơ",
}

TU_CAT = {"khoa", "quyen", "loc", "quy"}   # Hoá Khoa, Hoá Quyền, Hoá Lộc, Khôi Việt (Quý)
TU_HUNG = {"hoa", "linh", "duong", "da"}    # Hỏa Tinh, Linh Tinh, Kình Dương, Đà La

CITATION = "Trần Đoàn Toàn Thư p19-20 (atoms tdts.S1.Q53-Q54)"


def bat_phap_classify(
    sao_in_ban_phuong: set[str],
    sao_in_tam_hop: set[str],
    sao_in_xung_chieu: set[str],
) -> dict:
    """Phân loại cách cục theo Bát Pháp.

    Args:
        sao_in_ban_phuong: set các sao trong cung Mệnh (đã canonical lowercase)
        sao_in_tam_hop: set sao trong tam hợp Mệnh
        sao_in_xung_chieu: set sao xung chiếu Mệnh

    Returns:
        dict {
          "thanh_pha": cách A
          "cuu_khi": cách B
          "citation": str
        }
    """
    # Hợp tất cả sao trong vùng ảnh hưởng
    all_sao = sao_in_ban_phuong | sao_in_tam_hop | sao_in_xung_chieu

    has_cat = bool(all_sao & TU_CAT)
    has_hung = bool(all_sao & TU_HUNG)

    # A — Thành phá (xét bản phương + xung chiếu + tam hợp tổng quát)
    if has_cat and not has_hung:
        thanh_pha = "thanh"
    elif has_hung and not has_cat:
        thanh_pha = "pha"
    elif has_cat and has_hung:
        thanh_pha = "thanh_co_pha"
    else:
        thanh_pha = "chua_thanh"

    # B — Cứu khí (xét Mệnh + xung + tam hợp ĐỒNG đặc tính)
    # Logic: cùng 1 trong 3 vùng có TẤT CẢ Tứ Cát hoặc Tứ Hung
    cat_in_3 = TU_CAT & sao_in_ban_phuong and TU_CAT & sao_in_tam_hop and TU_CAT & sao_in_xung_chieu
    hung_in_3 = TU_HUNG & sao_in_ban_phuong and TU_HUNG & sao_in_tam_hop and TU_HUNG & sao_in_xung_chieu

    if cat_in_3 and not hung_in_3:
        cuu_khi = "cuu"
    elif hung_in_3 and not cat_in_3:
        cuu_khi = "khi"
    elif cat_in_3 and hung_in_3:
        cuu_khi = "vua_cuu_vua_khi"
    else:
        cuu_khi = "cho_thoi"

    return {
        "thanh_pha": thanh_pha,
        "thanh_pha_name": BAT_PHAP_CACH[thanh_pha],
        "cuu_khi": cuu_khi,
        "cuu_khi_name": BAT_PHAP_CACH[cuu_khi],
        "citation": CITATION,
    }
