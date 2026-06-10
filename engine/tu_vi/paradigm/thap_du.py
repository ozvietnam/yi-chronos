"""Thập Dụ — Trần Đoàn Toàn Thư p19.

10 điều cốt khi xem 4 cung quanh Mệnh (Bản phương + Hợp phương + Lân phương + Xung chiếu).

| # | Tình trạng | Tên cổ |
|---|---|---|
| 1 | Bản phương cát | nội tự cường — mạnh từ trong |
| 2 | Bản phương hung | tòng căn tự phạt — hư từ gốc |
| 3 | Xung chiếu cát | nghênh xuân tiếp phúc — đón xuân |
| 4 | Xung chiếu hung | đương đầu ác bổng — chịu búa |
| 5 | Tam hợp cát | tả hữu phùng nguyên — đông chân tay |
| 6 | Tam hợp hung | tả hữu thụ địch — địch 2 bên |
| 7 | Lân phương cát | lưỡng lân tương phù — hàng xóm phù |
| 8 | Lân phương hung | lưỡng nan tương vũ — hàng xóm hại |
| 9 | Cả 4 cát | thiên tường vàn tập — mây ngũ sắc |
| 10 | Cả 4 hung | tứ diện sở ca — vây 4 phía |

Nguồn: tdts.S1.Q43-Q52
"""
from __future__ import annotations

THAP_DU_NAMES: dict[int, str] = {
    1:  "Nội tự cường (mạnh từ trong)",
    2:  "Tòng căn tự phạt (hư từ gốc)",
    3:  "Nghênh xuân tiếp phúc (đón xuân tiếp phúc)",
    4:  "Đương đầu ác bổng (giơ đầu chịu búa)",
    5:  "Tả hữu phùng nguyên (đông chân tay giúp)",
    6:  "Tả hữu thụ địch (địch 2 bên đánh tới)",
    7:  "Lưỡng lân tương phù (2 hàng xóm phù trợ)",
    8:  "Lưỡng nan tương vũ (2 hàng xóm mưu hại)",
    9:  "Thiên tường vàn tập (mây ngũ sắc chầu)",
    10: "Tứ diện sở ca (vây 4 phía không thoát)",
}

CITATION = "Trần Đoàn Toàn Thư p19 (atoms tdts.S1.Q43-Q52)"


def thap_du_eval(
    ban_phuong_cat: bool, ban_phuong_hung: bool,
    xung_chieu_cat: bool, xung_chieu_hung: bool,
    tam_hop_cat: bool, tam_hop_hung: bool,
    lan_phuong_cat: bool, lan_phuong_hung: bool,
) -> dict:
    """Đánh giá 10 điều cốt Thập Dụ.

    Mỗi cặp (cát, hung) cho 1 trong 4 trường hợp: cát thuần, hung thuần,
    cả 2 (mixed), không gì. Function này flag điều nào "đắc" — không khái quát.

    Returns:
        dict {dieu_dac: list[int], dac_4: bool, hung_4: bool}
    """
    dac = []
    if ban_phuong_cat and not ban_phuong_hung: dac.append(1)
    if ban_phuong_hung and not ban_phuong_cat: dac.append(2)
    if xung_chieu_cat and not xung_chieu_hung: dac.append(3)
    if xung_chieu_hung and not xung_chieu_cat: dac.append(4)
    if tam_hop_cat and not tam_hop_hung: dac.append(5)
    if tam_hop_hung and not tam_hop_cat: dac.append(6)
    if lan_phuong_cat and not lan_phuong_hung: dac.append(7)
    if lan_phuong_hung and not lan_phuong_cat: dac.append(8)

    # Điều 9 + 10
    dac_4 = ban_phuong_cat and xung_chieu_cat and tam_hop_cat and lan_phuong_cat
    hung_4 = ban_phuong_hung and xung_chieu_hung and tam_hop_hung and lan_phuong_hung
    if dac_4: dac.append(9)
    if hung_4: dac.append(10)

    return {
        "dieu_dac": dac,
        "names": [THAP_DU_NAMES[i] for i in dac],
        "dac_4": dac_4,
        "hung_4": hung_4,
        "citation": CITATION,
    }
