"""Liệu Pháp Tượng Số — sinh dãy số chữa bệnh (paradigm độc đáo từ sách).

Source: "Chữa bệnh theo Chu Dịch" (Lý Ngọc Sơn + Lý Kiện Dân), CHƯƠNG I + II.
Paradigm: đọc nhẩm dãy số tượng quẻ → cộng hưởng vibration với tạng phủ.

⚠️ Paradigm này KHÁC LẠ — nhưng có gốc từ sách thật (đã verified):
- Số tiên thiên Bát Quái: Càn=1, Đoài=2, Ly=3, Chấn=4, Tốn=5, Khảm=6, Cấn=7, Khôn=8
- Mỗi tạng phủ tương ứng 1 quẻ → 1 số
- Số 0 thêm vào (đuôi) = âm khí (tăng hoặc giảm tùy ngữ cảnh)
- Dãy số được đọc nhẩm theo trật tự sinh-khắc

VÍ DỤ trong sách (verified):
- "640" hoặc "40" = Bổ máu Can, dưỡng gân cốt (cho gân cốt yếu)
- "640" = Tư âm tiềm dương (Can-Thận đồng nguồn: 6=Khảm/Thận, 4=Chấn/Can)
- "20.650" = Phấn chấn thận dương (cho lạnh, đau lưng)
- "650.3820" = Bổ thận dương + kiện tỳ hóa thấp
- "260.50" = Bổ thận nạp khí
- "430.20" = Thông can khí an thần
- "003" = Trị Can hỏa làm mắt đỏ
- "3820" = Hỏa sinh Thổ, Thổ sinh Kim — kiện tỳ ích khí

⚠️ Iron Rule: Đây là CÔNG CỤ THIỀN ĐỊNH (đọc nhẩm để tập trung tâm),
KHÔNG phải thuốc thay thế y học hiện đại. Cần đi khám bác sĩ song song.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# Số tiên thiên của 8 quẻ
QUE_SO: dict[str, int] = {
    "Càn": 1, "Đoài": 2, "Ly": 3, "Chấn": 4,
    "Tốn": 5, "Khảm": 6, "Cấn": 7, "Khôn": 8,
}

# Mỗi quẻ chủ tạng nào
QUE_TANG: dict[str, str] = {
    "Càn": "Đại trường (đầu)",
    "Đoài": "Phế",
    "Ly": "Tâm",
    "Chấn": "Can (gân)",
    "Tốn": "Đởm (đùi)",
    "Khảm": "Thận (xương)",
    "Cấn": "Vị",
    "Khôn": "Tỳ (bụng)",
}


# 5 PHƯƠNG PHÁP LẬP SỐ (yếu lĩnh dòng 3309-3312):
# "Bát quái vi thể, ngũ hành vi dụng; Tỷ loại thủ tướng, dĩ tượng định số;
#  biện chứng thi trị, bình hoành âm dương."
PHUONG_PHAP_LAP_SO: list[dict] = [
    {
        "phuong_phap": "1. Theo tượng bát quái (bộ phận cơ thể)",
        "vi_du": "Bệnh ở chân → 4 (Chấn) + 0 trước/sau",
        "case": "Học sinh Lý Viện trẹo gót → 0004000 → 20 phút khỏi",
        "trich_dong": "3181-3198",
    },
    {
        "phuong_phap": "2. Theo lý luận tàng tượng (tạng chủ)",
        "vi_du": "Bệnh về da → 2 (Đoài/Phế) chủ 'bì mao' + 000 → 0002",
        "case": "Nữ giáo sư người Mông mẩn ngứa → 0002 → mấy phút hết ngứa",
        "trich_dong": "3200-3213",
    },
    {
        "phuong_phap": "3. Theo 'quân cự tả sứ' (như đơn thuốc Đông y)",
        "vi_du": "Can dương tăng (đau đầu, mất ngủ) → 640.30.80",
        "case": "6=quân (Khảm, mát thận âm) + 4=cự (Chấn, bổ Can âm) + 30=tả (Ly, an thần) + 80=sứ (Khôn, kiện tỳ)",
        "trich_dong": "3215-3246",
    },
    {
        "phuong_phap": "4. Theo kinh lạc tuần hành",
        "vi_du": "Bệnh mũi → 07 (Cấn → Vị kinh → mũi)",
        "case": "Bệnh nhân Lăng viêm mũi → 07 → 1 ngày khỏi",
        "trich_dong": "3248-3255",
    },
    {
        "phuong_phap": "5. Theo quy luật ngũ hành sinh khắc",
        "vi_du": "650.30.820 = ôn thông thận dương + kiện tỳ ích khí",
        "case": "6 (Thủy) → 5 (Mộc) → 3 (Hỏa) → 8 (Thổ) → 2 (Kim) → vòng tròn sinh khắc",
        "trich_dong": "3259-3287",
    },
]

# QUY TẮC SỐ 0 (dòng 3144-3158, 3279-3287):
QUY_TAC_SO_0: dict = {
    "y_nghia": "Số 0 = khí hỗn nguyên thái cực, làm tăng năng lượng sóng tin tức để thông kinh khí âm dương.",
    "quy_tac": [
        "0 chẵn (00, 0000) = thiên ÂM (lạnh, làm dịu)",
        "0 lẻ (0, 000) = thiên ÔN DƯƠNG (ấm, kích hoạt)",
        "0 đặt TRƯỚC tượng số = hơi thiên về ÂM (phòng tổn âm)",
        "0 đặt SAU tượng số = hơi thiên về DƯƠNG (đẩy khí ra)",
    ],
    "vi_du": [
        "0002 (000 trước 2): trị mẩn ngứa - thiên âm để giữ âm khi sơ phong",
        "20.0000 (0000 sau): sơ giải dương",
        "003 = trị Can hỏa làm mắt đỏ (00 thủy khắc hỏa)",
    ],
    "nang_cao_Q7": [
        "0 đặt SAU = làm mạnh tín hiệu + thông kinh lạc + điều hòa (DEFAULT)",
        "Bệnh CẤP TÍNH + bệnh NGOAN CỐ → thêm 0 cả TRƯỚC + SAU = cường hóa",
        "Người THIÊN ÂM HƯ / DƯƠNG THỊNH → 0 KHÔNG đặt trước, chỉ đặt SAU",
        "0 chẵn (00, 0000) = âm tính (hoãn, làm dịu)",
        "0 lẻ (0, 000) = dương tính (ấm, kích hoạt)",
    ],
}

# 6 LƯU Ý KHI NIỆM (dòng 3316-3377) + Q&A insights (dòng 10468+):
LUU_Y_KHI_NIEM: list[str] = [
    "Niệm KHÔNG cảm thấy gì → vẫn tiếp tục (tác dụng vẫn có). Cảm ứng dễ chịu (mát đầu, nhẹ thân) = đúng số. Khó chịu ở đầu/dạ dày/tim = lập số sai → đổi số.",
    "Không câu nệ thời gian / địa điểm / tư thế: đi/ngồi/nằm đều niệm được. Tốt nhất: trước khi ngủ + sau thức giấc + lúc thả lỏng nhập tĩnh.",
    "Đã khỏi vẫn tiếp tục niệm để củng cố + tăng cường sức khỏe.",
    "Trong khi niệm, năng lượng tin tức xung kích vào ô bệnh → chứng trạng có thể tạm thời nặng lên. Chỉ cần đầu/dạ dày/tim không khó chịu là OK, cứ niệm tiếp.",
    "Có thể phối hợp châm cứu / ấn huyệt. KHÔNG phối hợp với các loại khí công khác (có thể ảnh hưởng tin tức tượng số). (Q9)",
    "Tuỳ bệnh tình điều chỉnh số: nếu thấy dễ chịu thì giữ, khó chịu thì đổi. Phép 'chìa nào mở khóa nấy' — biện chứng từng người. (Q12)",
    "TỐC ĐỘ niệm: trung bình — nhanh quá → bị nóng, chậm quá → bị lạnh. Giữa các nguyên (dấu chấm) dừng 1 chút. Niệm không thành tiếng, hoặc phối ý niệm. (Q6)",
    "Cảm ứng xuất hiện sau mấy phút → mười mấy phút = loại RÕ. Sau nửa giờ trở lên = loại NGẦM (chữa chậm hơn nhưng vẫn ổn định). (Q8)",
    "Liệu pháp này điều chỉnh CHỈNH THỂ → thường chữa luôn cả bệnh kèm theo (vd case 69: chữa viêm mũi + khỏi hoa mắt + bỏ kính). (Q10)",
    "Niệm tinh lực tăng, không thấy mệt — vì cộng chấn trường bát quái cơ thể với trường bát quái vũ trụ. (Q11)",
]

# CHỐNG CHỈ ĐỊNH (dòng 3373-3377):
CHONG_CHI_DINH: str = (
    "⛔ CẤM dùng cho: người tinh thần không bình thường (rối loạn tâm thần) + người trí nhớ kém."
)


# Công thức tượng số chuẩn (verified từ sách)
CONG_THUC_TUONG_SO: list[dict] = [
    {
        "tuong_so": "640",
        "y_nghia": "Bổ máu Can, dưỡng gân cốt",
        "phan_tich": "6=Khảm/Thận, 4=Chấn/Can, 0=âm khí. Can-Thận đồng nguồn → tư âm dưỡng huyết Can.",
        "chi_dinh": [
            "Gân yếu, chuột rút",
            "Đứt gân, đầu gối yếu",
            "Móng giòn dễ gãy",
            "Chân tay run rẩy",
            "Đau lưng + gối yếu (kèm thận hư)",
        ],
        "trich_sach": "Dòng 2426: 'Những chứng bệnh do Can không đủ máu, nói chung lấy tượng là 640 hoặc 40'",
    },
    {
        "tuong_so": "720.650.380",
        "y_nghia": "ĐAU KHỚP GỐI mạn tính — ôn bổ dương Tỳ-Thận, hàn thấp tự mất",
        "phan_tich": (
            "3 nguyên: 720 (tác động khớp gối) + 650 (chấn thận dương) + 380 (ôn tỳ táo thấp). "
            "7=Cấn(núi/khớp), 2=Đoài sơ giải cục bộ, 6=Khảm thận, 5=Tốn mộc, 3=Ly hỏa, 8=Khôn thổ."
        ),
        "chi_dinh": [
            "Đau khớp gối mạn tính",
            "Đau khớp lan tỏa, hàn thấp",
            "Thoái hóa khớp tuổi trung niên",
            "Đau khớp sau chấn thương (như đứt gân đã mổ)",
        ],
        "trich_sach": (
            "Case 71 (dòng 6325): Bà Trương 53t đau 2 khớp gối từ 1992, đã chữa nhiều không khỏi. "
            "Niệm 720.650.380 + nhĩ áp 3 tháng → khỏi + tóc bạc đen lại + sinh khí tăng."
        ),
    },
    {
        "tuong_so": "0004000",
        "y_nghia": "Trẹo gót / khớp bàn chân — tản ứ hoạt huyết, tiêu sưng",
        "phan_tich": (
            "4=Chấn (chân) ở giữa, 000 trước + 000 sau để tăng lợi tiểu + tiêu sưng + "
            "tản ứ hoạt huyết. Số 0 chẵn = thiên âm."
        ),
        "chi_dinh": [
            "Trẹo khớp gót / khớp cổ chân",
            "Sưng tấy chân sau chấn thương",
            "Đau bộ phận chân do tổn thương",
            "Bong gân chân cấp tính",
        ],
        "trich_sach": (
            "Case học sinh Lý Viện (dòng 3192): trẹo gót sưng tấy không đi nổi. "
            "Niệm 0004000 → 20 phút thấy lạnh→nóng→dễ chịu, 4 ngày hết sưng."
        ),
    },
    {
        "tuong_so": "640.30.80",
        "y_nghia": "Đau đầu, mất ngủ, buồn bực — Can dương hơi tăng",
        "phan_tich": (
            "4 nguyên 'quân cự tả sứ': 640 (tư âm tiềm dương) + 30 (Ly an thần) + 80 (Khôn kiện tỳ). "
            "6=quân, 4=cự, 3=tả, 8=sứ."
        ),
        "chi_dinh": [
            "Đau đầu kéo dài (do Can dương lên)",
            "Mất ngủ buồn bực",
            "Cao huyết áp nhẹ",
            "Hay cáu gắt vô cớ",
        ],
        "trich_sach": "Dòng 3241",
    },
    {
        "tuong_so": "260.50.30.80",
        "y_nghia": "Đau nửa đầu mạn tính do thủy bất hàm mộc",
        "phan_tich": (
            "260=Đoài sinh Khảm tăng dịch thận, 50=Tốn Can âm, 30=Ly an thần, 80=Khôn kiện tỳ. "
            "Bài cuối cùng sau khi điều chỉnh từ 650 → 60.50 → 60.50.30 → 60.50.30.820 → 260.50.30.80."
        ),
        "chi_dinh": [
            "Đau nửa đầu kéo dài nhiều năm",
            "Đau khi suy nghĩ căng, buồn bực mất ngủ",
            "Chân tay nóng về tối, mắt khô",
            "Lưỡi khô, người gầy (bệnh lao tâm)",
        ],
        "trich_sach": "Case 40 (dòng 5217): Bà Trương 54t đau nửa đầu 10 năm.",
    },
    {
        "tuong_so": "2000.60",
        "y_nghia": "Bệnh ngoài da mạn tính — sơ tán tà da, tư âm trừ phiền",
        "phan_tich": (
            "2=Đoài/Phế chủ bì mao. 2000 đứng trước = sơ giải biểu tà mạnh + thanh nhiệt. 60=tư âm trừ phiền."
        ),
        "chi_dinh": [
            "Nấm da mạn tính, lan toàn thân",
            "Mẩn ngứa kéo dài không hết",
            "Da khô nóng, nước vàng",
            "Eczema, viêm da tiết bã",
        ],
        "trich_sach": "Case 41 (dòng 5279): Bà Trương 58t nấm da 20 năm, 2 tháng khỏi.",
    },
    {
        "tuong_so": "820",
        "y_nghia": "Đau vai / viêm quanh vai — hoạt huyết tản hàn",
        "phan_tich": (
            "8=Khôn/Tỳ chủ cơ bắp + chủ vai phải. 2=Đoài tả tà hàn ngưng. 820 đi thẳng khu bệnh."
        ),
        "chi_dinh": [
            "Viêm quanh vai (frozen shoulder)",
            "Đau khớp vai, giơ tay khó",
            "Đau cơ bắp lan tỏa",
            "Co cứng vai gáy",
        ],
        "trich_sach": "Case 42 (dòng 5298): Bà Mai viêm quanh vai 6 tháng, niệm 1 tháng khỏi.",
    },
    {
        "tuong_so": "40.60.3800",
        "y_nghia": "Viêm túi mật + đau dạ dày + đau nửa đầu phối hợp",
        "phan_tich": (
            "40=Chấn sơ Can lợi đảm, 60=Khảm sơ tiết Can-Đảm, 3800=Ly-Khôn ôn kiện tỳ vị. "
            "Bài cho 'mộc uất thừa thổ'."
        ),
        "chi_dinh": [
            "Viêm túi mật mạn tính",
            "Đau dạ dày + tiêu hóa kém",
            "Đau nửa đầu kèm tiêu hóa kém (Đảm kinh)",
        ],
        "trich_sach": "Case 43 (dòng 5328): Cô Quách viêm túi mật 5 năm, 1 tháng khỏi.",
    },
    {
        "tuong_so": "720.40",
        "y_nghia": "Bệnh tim mạn — ôn tỳ hòa vị, ôn thông tâm dương",
        "phan_tich": (
            "7=Cấn dừng tim đập thất thường + chấn dương Tỳ-Vị. 2=Đoài an thần. 4=Chấn sơ đạo khí giáng trọc."
        ),
        "chi_dinh": [
            "Hồi hộp đánh trống ngực kéo dài",
            "Tim đập thất thường, run toàn thân",
            "Đầu căng + cao huyết áp tâm dương suy",
            "Mệt mỏi tinh thần do tim",
        ],
        "trich_sach": "Case 44 (dòng 5369): Bà Trương 61t bệnh tim 30 năm, niệm nửa năm khỏe. ⚠️ Tránh giờ Ngọ + Dần mùa xuân.",
    },
    {
        "tuong_so": "260",
        "y_nghia": "Cao huyết áp + xơ vữa — bổ thận ích khí tư âm tiềm dương",
        "phan_tich": "2=Đoài kim sinh 6=Khảm thủy → bổ thận. Can-Thận đồng nguồn nên đồng thời ích Can.",
        "chi_dinh": [
            "Cao huyết áp do âm hư dương cang",
            "Xơ vữa động mạch",
            "Hay cáu gắt mệt mỏi tuổi trung niên",
            "Huyết áp thấp / cao do hư khí (cùng cơ lý)",
        ],
        "trich_sach": "Case 61 (dòng 6003): Bà Vương 66t cao HA + xơ vữa + di chứng não, 3 tháng chuyển biến rõ.",
    },
    {
        "tuong_so": "6000.20",
        "y_nghia": "Đau lưng cấp / mạn — ôn thận thông lạc",
        "phan_tich": "6=Khảm thận chủ lưng. 6000 ôn thông kinh lạc. 20=Đoài tuyên đạo khí cơ.",
        "chi_dinh": [
            "Đau lưng kéo dài, hô hấp khó",
            "Đau lưng do hàn tà",
            "Trẹo lưng cấp (sau nhảy/sai tư thế)",
            "Đau thận vùng lưng dưới",
        ],
        "trich_sach": "Case 63-64 (dòng 6072-6099): Cô Liên 22t trẹo lưng, 6000 10 phút khỏi.",
    },
    {
        "tuong_so": "7000.20",
        "y_nghia": "Thần kinh tọa đùi — ôn kinh tản hàn",
        "phan_tich": (
            "7=Cấn (lồi, khớp, chân trái). 7000 đi thẳng vào ô bệnh, ôn thông khí huyết. "
            "20=Đoài sơ tản uất trệ cục bộ."
        ),
        "chi_dinh": [
            "Đau thần kinh tọa lan từ lưng xuống đùi",
            "Đau cơ bắp đùi do hàn ẩm",
            "Đau xương khớp lan tỏa",
            "Cứng khớp háng / đùi sau lao động",
        ],
        "trich_sach": "Case 65 (dòng 6136): Chị Trương đau thần kinh tọa 2 năm, 30 phút khỏi.",
    },
    {
        "tuong_so": "003",
        "y_nghia": "Mắt đỏ cấp tính (Can hỏa lên) — thủy khắc hỏa",
        "phan_tich": (
            "3=Ly hỏa chủ mục, là con của Chấn mộc. 00=số chẵn thiên âm. "
            "003 = thủy khắc hỏa + tử hỏa tả mẫu (truy đuổi đến cùng)."
        ),
        "chi_dinh": [
            "Mắt đỏ sưng đột ngột",
            "Viêm kết mạc cấp",
            "Đau nhức mắt do Can hỏa",
        ],
        "trich_sach": "Case 60 (dòng 5971): Cô Vương 23t niệm 2 ngày khỏi. ⚠️ Nếu vị nguyên hư hàn không dùng lâu.",
    },
    {
        "tuong_so": "650.30.820",
        "y_nghia": "⭐ KHÍ NGŨ TẠNG — bài tổng quát cho người già + nhiều bệnh kèm",
        "phan_tich": (
            "Bài CỐT chương II: cân bằng khí của 5 tạng. 650=bổ Can-Thận phấn chấn khí, "
            "30=ích Tâm dưỡng Mục, 820=kiện Tỳ ích Khí. Đạt 'thăng giáng, xuất nhập, "
            "nhanh chậm, cân bằng'."
        ),
        "chi_dinh": [
            "Người già bệnh lâu năm + nhiều bệnh kèm (cao HA, xơ vữa, bệnh tim, viêm Can, viêm dạ dày, đau đầu, viêm khớp)",
            "Âm hư dương cang kinh mạch yếu",
            "Tổn tiên thiên + mất dinh dưỡng hậu thiên",
            "Bệnh phức tạp khó định cách chữa cụ thể (dùng làm BÀI NỀN)",
        ],
        "trich_sach": "Case 2 (dòng 3877): Bà Chương 62t bệnh từ 1982, nhiều biến chứng. Gần 1 năm → trừ dần bệnh ngoan cố, tăng 10kg, da mềm bóng.",
    },
    {
        "tuong_so": "00100.0700",
        "y_nghia": "Đau khớp hàn tê — ôn thông đốc mạch + cục bộ",
        "phan_tich": (
            "1=Càn (bản chất dương, đốc mạch). 7=Cấn (đầu gối). "
            "Hai số 0 trước+sau (chẵn=thiên âm) để HOÃN dương, tránh viêm. "
            "00100=ôn đốc mạch, 0700=ôn thông cục bộ. ⚠️ Người gầy dễ đa hỏa, "
            "khi bệnh đã khỏi PHẢI thôi ngay (không niệm dài lâu)."
        ),
        "chi_dinh": [
            "Đau khớp gối hàn tê mạn tính",
            "Sợ rét thích nóng, đầu gối co như gắn chì",
            "Đau khi trời mưa âm u hoặc lao động mệt",
            "Mạch trầm + lưỡi viêm đỏ + chân tay nóng",
        ],
        "trich_sach": "Case 3 (dòng 3923): Cô Trương 29t đau 2 khớp gối 3 năm, 4 phút thấy toát hơi lạnh, 1 tuần khỏi.",
    },
    {
        "tuong_so": "00100.800",
        "y_nghia": "Trĩ — ôn mạch đốc + kiện tỳ tả tư âm",
        "phan_tich": (
            "00100 ôn dương đốc mạch (1=Càn còn chủ Đại trường). "
            "800 (8=Khôn/Tỳ + 00 thiên âm) = kiện tỳ + nhuận tràng + tả tư âm + trừ phiền."
        ),
        "chi_dinh": [
            "Trĩ do khí huyết vận hành không thông",
            "Đại tiện táo + chảy máu nhẹ",
            "Phát khi lao động mệt hoặc bị lạnh",
            "Kinh mạch tắc nghẽn đọng máu vùng hậu môn",
        ],
        "trich_sach": "Case 4 (dòng 3959): Cô Trương 21t trĩ 2 năm, niệm dù không có cảm giác vẫn khỏi, 2 năm không tái phát.",
    },
    {
        "tuong_so": "38000.40",
        "y_nghia": "Tiêu hóa kém + Can uất — kiện tỳ ích khí, thư Can giải uất",
        "phan_tich": (
            "38000=Ly-Khôn (hỏa sinh thổ) kiện tỳ + 4 số 0 cường hóa. "
            "40=Chấn sơ Can. Trị 'mộc uất khí trì có trở ngại sinh hóa'."
        ),
        "chi_dinh": [
            "Tiêu hóa kém do căng thẳng",
            "Đầy bụng + ợ hơi sau stress",
            "Tỳ vị bị Can mộc khắc (cáu xong đau dạ dày)",
            "Buồn bực không tả + ăn không ngon",
        ],
        "trich_sach": "Dòng 4691: niệm trong ngày, chiều đã thấy chuyển biến.",
    },
    {
        "tuong_so": "650.070",
        "y_nghia": "Tê chân / máu không lưu thông xuống chân",
        "phan_tich": (
            "650=Tốn-Khảm chấn thận dương sơ thông. 070=Cấn (chân) + số 0 thiên âm."
            " ⚠️ Nếu sửa thành 6500.070 sẽ nóng → quay lại 650.070."
        ),
        "chi_dinh": [
            "Tê chân, cảm giác máu chảy chậm",
            "Đầu ngón chân xì hơi lạnh",
            "Sau lao động chân nặng",
            "Tuần hoàn ngoại vi kém",
        ],
        "trich_sach": "Dòng 6801: niệm thấy như máu trong chân chảy, đầu ngón chân xì hơi lạnh, sau đó nhẹ nhàng.",
    },
    {
        "tuong_so": "80.20",
        "y_nghia": "⭐ Đau CỔ-VAI-GÁY do hàn — tản hàn giải cơ",
        "phan_tich": (
            "8=Khôn/Tỳ chủ cơ bắp (vai gáy thuộc cơ + Khôn), thiên ôn để tản hàn giải cơ. "
            "2=Đoài chủ khí cơ, giúp túc giáng trọc tà. "
            "Cổ vai gáy là nơi 3 kinh dương chạy qua (Bàng quang Khảm + Đởm Tốn + Đại trường Càn) — "
            "khi hàn tà xâm nhập làm 3 kinh tắc → đau cứng."
        ),
        "chi_dinh": [
            "Đau cổ vai gáy do gió lùa / thời tiết lạnh",
            "Cứng cổ vai gáy sáng dậy không quay được",
            "Đau vai trái / phải do hàn",
            "Đau vai gáy + lan xuống bả vai",
            "Đau cổ sau khi ngủ điều hòa lạnh",
        ],
        "trich_sach": "Case 86 (dòng 6896): Cô Kim 22t đau vai trái + 2 khớp gối do thời tiết rét, niệm 80.20 → 1 ngày vai khỏi hẳn.",
    },
    {
        "tuong_so": "8000.70",
        "y_nghia": "Đau vai + chân (Can-Thận kém người trung niên+) — phấn chấn tỳ dương",
        "phan_tich": (
            "8000=Khôn (Tỳ) + 3 số 0 trợ lực tản hàn. 70=Cấn (chân/đùi) ôn thông. "
            "Bài cho người trung niên Can-Thận kém → gân mạch mất bồi dưỡng → đau vai + co gân chân."
        ),
        "chi_dinh": [
            "Đau vai + bắp chân co gân cùng lúc",
            "Viêm khớp vai mạn + đau đùi",
            "Người trung niên trở lên Can-Thận hư, gân mạch yếu",
            "Đau xương khớp lan tỏa nhiều vùng",
        ],
        "trich_sach": "Case 87 (dòng 6940): Bà Diêm 68t bệnh mạch vành + vai phải bị thương + đùi trái co gân, niệm 8000.70 → vài chục phút vai+chân tiêu tán.",
    },
    {
        "tuong_so": "0002",
        "y_nghia": "Mẩn ngứa cấp da — sơ phong lợi thấp",
        "phan_tich": (
            "2=Đoài/Phế chủ bì mao. 000 trước = thiên âm để đề phòng tổn âm khi sơ phong. "
            "Cường hóa khả năng sơ giải tà khí trên mặt da."
        ),
        "chi_dinh": [
            "Mẩn ngứa cấp tính toàn thân",
            "Da đột ngột bị ngứa không rõ nguyên nhân",
            "Dị ứng cấp + mất ngủ vì ngứa",
            "Uống thuốc không khỏi (case mạn → dùng 2000.60)",
        ],
        "trich_sach": "Case nữ giáo sư Mông (dòng 3208): 0002 → mấy phút hết ngứa, mười mấy phút khỏi hoàn toàn.",
    },
    {
        "tuong_so": "20.650.380",
        "y_nghia": "Phong thấp toàn thân + bệnh ngoan cố — vực chính trừ tà",
        "phan_tich": (
            "Bài CƠ SỞ có thể gia giảm. 20=Đoài tuyên khí, 650=Khảm-Tốn ôn thận, 380=Ly-Khôn kiện tỳ ôn dương."
        ),
        "chi_dinh": [
            "Phong thấp toàn thân nhiều năm",
            "Kinh nguyệt không đều / viêm cổ tử cung kèm dạ dày",
            "Bệnh ngoan cố tổn chính khí",
            "Thể trạng giảm dần không lý do",
        ],
        "trich_sach": "Case 66 (dòng 6161): Bà Lý 51t phong thấp 10 năm, mấy tháng giảm rõ.",
    },
    {
        "tuong_so": "650.3820",
        "y_nghia": "Bổ thận dương + kiện tỳ hóa thấp",
        "phan_tich": "650=Tốn-Khảm (gió-nước, dương mộc sinh thận thủy), 3820=Ly-Khôn-Đoài (hỏa-thổ-kim sinh khí).",
        "chi_dinh": [
            "Thận dương hư: lạnh tay chân, mệt mỏi, di tiểu nhiều lần",
            "Liệt dương, sinh khí kém",
            "Đau lưng + tứ chi lạnh",
            "Phù toàn thân",
        ],
        "trich_sach": "Dòng 2546: '650.3820 có thể kiện tỳ ích khí'",
    },
    {
        "tuong_so": "260.50",
        "y_nghia": "Bổ thận nạp khí (hô hấp ngắn)",
        "phan_tich": "260=Đoài-Khảm-âm (phế kim sinh thận thủy), 50=Tốn-âm (dương mộc tả).",
        "chi_dinh": [
            "Hô hấp ngắn, hen suyễn",
            "Khí hít vào không đủ",
            "Thận không nạp khí",
        ],
        "trich_sach": "Dòng 2569: '260.50 là đoài kim sinh thận thủy, thêm 00 để tả thận khí'",
    },
    {
        "tuong_so": "430.20",
        "y_nghia": "Thông Can khí an thần",
        "phan_tich": "430=Chấn-Ly-âm (mộc sinh hỏa, an tâm thần), 20=Đoài-âm (kim tả Can).",
        "chi_dinh": [
            "Can khí uất, buồn bực không tả",
            "Stress, dễ giận",
            "Kinh nguyệt không đều (nữ)",
            "Mất ngủ do Can uất",
        ],
        "trich_sach": "Dòng 2404: 'Lập tượng số là 430.20 để thông Can khí an thần'",
    },
    {
        "tuong_so": "20.650",
        "y_nghia": "Phấn chấn thận dương (đau lưng + lạnh)",
        "phan_tich": "20=Đoài-âm (kim sinh thủy), 650=Khảm-Tốn-âm (thận-mộc tương sinh).",
        "chi_dinh": [
            "Thận dương hư",
            "Đau lưng kéo dài",
            "Tay chân lạnh",
            "Tinh thần mệt mỏi",
        ],
        "trich_sach": "Dòng 2521: 'Lập tượng số là 20.650'",
    },
    {
        "tuong_so": "3820",
        "y_nghia": "Kiện tỳ ích khí (Hỏa→Thổ→Kim)",
        "phan_tich": "3=Ly/hỏa, 8=Khôn/thổ, 2=Đoài/kim, 0=âm. Chuỗi sinh: hỏa→thổ→kim.",
        "chi_dinh": [
            "Tỳ hư, ăn không ngon",
            "Đầy bụng, phân lỏng",
            "Mệt mỏi không lý do",
            "Cơ nhão",
        ],
        "trich_sach": "Dòng 2547: '3820 là hỏa sinh thổ, thổ sinh kim'",
    },
    {
        "tuong_so": "003",
        "y_nghia": "Trị Can hỏa làm mắt đỏ",
        "phan_tich": "00=âm (thủy), 3=Ly/hỏa. Thủy khắc hỏa.",
        "chi_dinh": [
            "Mắt đỏ sưng",
            "Can hỏa vượng",
            "Đỏ mặt giận dữ",
        ],
        "trich_sach": "Dòng 2450: 'Can hỏa làm mắt đỏ lên hay sưng đỏ là 003'",
    },
]


@dataclass
class TuongSoResult:
    """Kết quả tra tượng số phù hợp."""

    chan_thuong_input: str
    matched_formulas: list[dict]   # Các công thức khớp
    primary_formula: dict          # Công thức ưu tiên nhất
    huong_dan_doc: str             # Hướng dẫn đọc nhẩm
    iron_rule_warning: str         # Cảnh báo Iron Rule

    def to_dict(self) -> dict:
        return asdict(self)


def _score_formula(formula: dict, ct: str) -> int:
    """Đếm số keyword khớp giữa formula chi_dinh và input."""
    score = 0
    # Cộng điểm cho mỗi chi_dinh có keyword match
    for chi in formula["chi_dinh"]:
        chi_lower = chi.lower()
        # Match từng từ có ý nghĩa
        for word in chi_lower.replace(",", " ").replace("(", " ").replace(")", " ").split():
            if len(word) >= 3 and word in ct:
                score += 1
                break  # mỗi chi_dinh tính 1 lần
    # Cộng thêm điểm nếu y_nghia có overlap
    yn = formula["y_nghia"].lower()
    for word in yn.split():
        if len(word) >= 4 and word in ct:
            score += 1
    return score


def tim_tuong_so(chan_thuong: str) -> TuongSoResult:
    """Tìm công thức tượng số phù hợp với triệu chứng (score-based)."""
    ct = chan_thuong.lower()

    # Score tất cả công thức
    scored = []
    for formula in CONG_THUC_TUONG_SO:
        s = _score_formula(formula, ct)
        if s > 0:
            scored.append((s, formula))

    # Sort by score desc
    scored.sort(key=lambda x: -x[0])
    matched = [f for _, f in scored]

    if not matched:
        # Fallback: nếu có gân/đầu gối → 640
        if any(k in ct for k in ["gân", "đầu gối", "móng", "khớp"]):
            matched.append(CONG_THUC_TUONG_SO[0])  # 640

    # Re-priority bonus: KHỚP + mạn → 720.650.380 (override score)
    chronic_keywords = ["mạn", "kéo dài", "thoái hóa", "nhiều năm", "lâu năm", "đã mổ", "sau mổ"]
    if "khớp" in ct and any(k in ct for k in chronic_keywords):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "720.650.380":
                matched.insert(0, matched.pop(i))
                break

    # Trẹo / bong gân cấp → 0004000 (chỉ khi có CHÂN/GÓT/BÀN)
    acute_keywords = ["trẹo", "bong gân"]
    foot_keywords = ["chân", "gót", "bàn chân", "cổ chân"]
    if any(k in ct for k in acute_keywords) and any(k in ct for k in foot_keywords):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "0004000":
                matched.insert(0, matched.pop(i))
                break

    # Mật / túi mật → 40.60.3800
    if any(k in ct for k in ["túi mật", "mật", "sỏi mật"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "40.60.3800":
                matched.insert(0, matched.pop(i))
                break

    # Mắt đỏ / mắt sưng → 003
    if "mắt" in ct and any(k in ct for k in ["đỏ", "sưng", "viêm kết mạc"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "003":
                matched.insert(0, matched.pop(i))
                break

    # Đau cổ-vai-gáy (do hàn / gió lùa / ngủ máy lạnh) → 80.20
    if any(k in ct for k in ["cổ vai gáy", "vai gáy", "cứng cổ", "đau cổ", "đau vai gáy", "cổ vai"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "80.20":
                matched.insert(0, matched.pop(i))
                break

    # Đau nửa đầu BÊN TRÁI (Can huyết hư) → 260.50.30.80
    if any(k in ct for k in ["nửa đầu bên trái", "nửa đầu trái", "nửa đầu", "migraine trái"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "260.50.30.80":
                matched.insert(0, matched.pop(i))
                break

    # Đau vai + chân/đùi cùng lúc (Can-Thận kém) → 8000.70
    if "vai" in ct and any(k in ct for k in ["chân", "đùi", "bắp chân", "co gân"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "8000.70":
                matched.insert(0, matched.pop(i))
                break

    # Trĩ → 00100.800
    if any(k in ct for k in ["trĩ", "hậu môn"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "00100.800":
                matched.insert(0, matched.pop(i))
                break

    # Đau khớp gối hàn tê (sợ rét, đau khi trời mưa) → 00100.0700
    if any(k in ct for k in ["hàn tê", "sợ rét", "trời mưa", "âm u"]) and "khớp" in ct:
        for i, f in enumerate(matched):
            if f["tuong_so"] == "00100.0700":
                matched.insert(0, matched.pop(i))
                break

    # Tê chân / máu chảy chậm → 650.070
    if any(k in ct for k in ["tê chân", "máu chảy chậm", "máu lưu thông kém", "tê tay chân"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "650.070":
                matched.insert(0, matched.pop(i))
                break

    # Mẩn ngứa cấp → 0002 (nếu không kéo dài)
    if "ngứa" in ct and not any(k in ct for k in ["kéo dài", "mạn", "nhiều năm", "lâu"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "0002":
                matched.insert(0, matched.pop(i))
                break

    # Người già nhiều bệnh kèm → 650.30.820
    if any(k in ct for k in ["người già", "nhiều bệnh", "đa bệnh", "phức tạp"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "650.30.820":
                matched.insert(0, matched.pop(i))
                break

    # Đau nửa đầu mạn tính → 260.50.30.80
    if any(k in ct for k in ["nửa đầu", "đau đầu kéo dài", "đau đầu nhiều năm"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "260.50.30.80":
                matched.insert(0, matched.pop(i))
                break

    # Đau đầu + Can dương / mất ngủ → 640.30.80
    if "đau đầu" in ct and any(k in ct for k in ["can dương", "mất ngủ", "buồn bực", "cáu", "huyết áp"]):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "640.30.80":
                matched.insert(0, matched.pop(i))
                break

    primary = matched[0] if matched else CONG_THUC_TUONG_SO[0]

    huong_dan = (
        "**Cách đọc nhẩm:**\n"
        f"1. Tâm tịnh, ngồi thẳng, mắt khép nhẹ hoặc nhìn xuôi\n"
        f"2. Đọc nhẩm dãy số **{primary['tuong_so']}** trong đầu (không cần nói ra)\n"
        f"3. Mỗi lần đọc cho hơi thở 1 nhịp. Đếm 36-108 lần/buổi\n"
        f"4. 2-3 buổi/ngày, vào giờ tạng tương ứng vượng nhất\n"
        f"5. Không cần ép — đọc với tâm thoải mái, không phải 'để khỏi bệnh' mà 'để tĩnh tâm'"
    )

    return TuongSoResult(
        chan_thuong_input=chan_thuong,
        matched_formulas=matched,
        primary_formula=primary,
        huong_dan_doc=huong_dan,
        iron_rule_warning=(
            "⚠️ **Paradigm CỔ — KHÔNG thay thế y học hiện đại.** "
            "Liệu pháp tượng số là CÔNG CỤ THIỀN ĐỊNH — đọc nhẩm để tập trung tâm + "
            "cộng hưởng paradigm Bát Quái. Vẫn cần đi khám bác sĩ, theo phác đồ. "
            "Em không khuyến nghị bỏ thuốc Tây hoặc Đông y chính thống."
        ),
    )


def render_tuong_so_markdown(result: TuongSoResult) -> str:
    if not result.matched_formulas:
        return "_(Chưa tìm thấy công thức phù hợp)_"

    lines = [
        f"## 🔢 Liệu pháp Tượng Số (paradigm cổ độc đáo)\n",
        f"_Triệu chứng:_ **{result.chan_thuong_input}**\n",
        f"### 🎯 Tượng số ưu tiên: **{result.primary_formula['tuong_so']}**\n",
        f"**Ý nghĩa:** {result.primary_formula['y_nghia']}\n",
        f"**Phân tích quẻ:** {result.primary_formula['phan_tich']}\n",
        f"**Chỉ định:**",
    ]
    for c in result.primary_formula['chi_dinh']:
        lines.append(f"- {c}")
    lines.append(f"\n**Trích sách:** _{result.primary_formula['trich_sach']}_\n")
    lines.append(result.huong_dan_doc)

    if len(result.matched_formulas) > 1:
        lines.append("\n### Công thức khác liên quan")
        for f in result.matched_formulas[1:]:
            lines.append(f"- **{f['tuong_so']}**: {f['y_nghia']}")

    # 5 phương pháp lập số
    lines.append("\n### 📐 5 Phương pháp lập số (yếu lĩnh chương I)")
    for pp in PHUONG_PHAP_LAP_SO:
        lines.append(f"\n**{pp['phuong_phap']}**")
        lines.append(f"- Ví dụ: {pp['vi_du']}")
        lines.append(f"- Case: _{pp['case']}_")

    # Quy tắc số 0
    lines.append("\n### 🔢 Quy tắc số 0")
    lines.append(f"_{QUY_TAC_SO_0['y_nghia']}_\n")
    for rule in QUY_TAC_SO_0['quy_tac']:
        lines.append(f"- {rule}")

    # 6 lưu ý
    lines.append("\n### 📋 6 Lưu ý khi niệm (cốt từ sách)")
    for i, ly in enumerate(LUU_Y_KHI_NIEM, 1):
        lines.append(f"{i}. {ly}")

    lines.append(f"\n{CHONG_CHI_DINH}\n")
    lines.append(f"\n---\n\n{result.iron_rule_warning}")
    return "\n".join(lines)


def get_paradigm_overview() -> dict:
    """Trả về paradigm tổng quan để frontend display."""
    return {
        "yeu_linh": (
            "Bát quái vi thể, ngũ hành vi dụng; "
            "Tỷ loại thủ tướng, dĩ tượng định số; "
            "Biện chứng thi trị, bình hoành âm dương."
        ),
        "yeu_linh_giai": (
            "Bát quái là thể (gốc), ngũ hành là dụng (cách dùng). "
            "Lấy tượng theo phân loại, dùng tượng để định số. "
            "Biện chứng để chữa trị, cân bằng âm dương."
        ),
        "phuong_phap_lap_so": PHUONG_PHAP_LAP_SO,
        "quy_tac_so_0": QUY_TAC_SO_0,
        "luu_y_khi_niem": LUU_Y_KHI_NIEM,
        "chong_chi_dinh": CHONG_CHI_DINH,
        "source": "Chữa bệnh theo Chu Dịch — Lý Ngọc Sơn + Lý Kiện Dân, chương I (dòng 3100-3380)",
    }
