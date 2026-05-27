"""Seed Bát Tự / Tứ Trụ concepts into wiki.sqlite3.

Source: Thiệu Vĩ Hoa & Trần Viên — "Dự đoán theo Tứ trụ" (NXB Văn hóa Thông tin,
tái bản lần 4, dịch giả Nguyễn Văn Mậu).

Paradigm: Tử Bình = đọc đồng dạng (Iron Rule #4 + #6). KHÔNG predict-tool.
Concepts viết với tone "đọc cấu trúc khí" + "tri mệnh" + "bổ-cân-bằng",
NOT "dự đoán sẽ giàu/nghèo".

Run: cd /Users/ozvietnamdesktop/Desktop/yi && .venv/bin/python3 scripts/wiki_seed_bat_tu.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "yi_wiki" / "wiki.sqlite3"
CORPUS_ID = "bat-tu-thieu-vi-hoa"
SCHOOL = "tu_binh_ba_tu"

# ─── Concepts (rich content, paradigm-aligned) ───────────────────────────────

# Each entry: (canonical_vi, canonical_zh, aliases, short_note, category, first_page)
CONCEPTS: list[tuple[str, str, list[str], str, str, int | None]] = [
    # ── Foundational paradigm ────────────────────────────────────────────────
    ("Tứ Trụ", "四柱", ["Bát Tự", "8 chữ", "Four Pillars"],
     "Bốn cột Năm/Tháng/Ngày/Giờ sinh, mỗi cột gồm 1 Thiên Can + 1 Địa Chi → tổng 8 chữ (八字). "
     "Mỗi trụ biểu thị một mặt cuộc đời: Năm=tổ tiên/0-15t, Tháng=cha mẹ/16-30t, Ngày=bản thân/vợ chồng/31-45t, "
     "Giờ=con cái/hậu vận 46+. Tứ Trụ là 'snapshot khí bẩm sinh' tại điểm sinh — KHÔNG predict thành/bại, "
     "mà phản chiếu cấu trúc khí của một con người trong vũ trụ.",
     "paradigm", 16),

    ("Bát Tự", "八字", ["Tứ Trụ", "8 chữ"],
     "= Tứ Trụ. 8 chữ gồm 4 cặp Can-Chi của Năm/Tháng/Ngày/Giờ sinh. Là phương tiện 'đọc đồng dạng' "
     "giữa người và vũ trụ — không phải lệnh phán quyết.",
     "paradigm", 16),

    ("Mệnh", "命", ["mệnh"],
     "Trạng thái khí vũ trụ CỐ KẾT lại tại điểm sinh. Snapshot. Cùng paradigm 'CƠ' của Tử Vi (Iron Rule #6). "
     "Không thể đổi — vì là dấu vân tay khí.",
     "paradigm", 11),

    ("Vận", "運", ["vận", "đại vận"],
     "Những cảnh ngộ gặp phải trong trạng thái vũ trụ KHÔNG NGỪNG LƯU BIẾN. Cùng paradigm 'BIẾN' của Tử Vi. "
     "Vận có thể 'thuận' (hợp Dụng Thần) hoặc 'nghịch' (hợp Kỵ Thần). Đại Vận chu kỳ 10 năm + Lưu Niên hàng năm.",
     "paradigm", 11),

    ("Mệnh Vận", "命運", ["fate", "destiny"],
     "Mệnh (cố kết) + Vận (lưu biến). Không phải lực siêu nhiên từ ngoài đến, mà là một LOẠI THỂ NGHIỆM "
     "(體驗) — kinh nghiệm sống sâu sắc, biểu thị qua âm dương + ngũ hành.",
     "paradigm", 10),

    ("Tri mệnh", "知命", ["biết mệnh"],
     "Mục đích cuối của Tử Bình. KHÔNG phải biết sẽ giàu/nghèo. Mà biết mình ở vị trí nào trong tổng thể "
     "vũ trụ → không lo, làm chủ. Trích Luận Ngữ: 'Tri mệnh thì không lo'.",
     "paradigm", 11),

    ("Thể nghiệm", "體驗", ["trải nghiệm"],
     "Cảm thụ + biểu đạt thế giới qua tâm linh người Đông phương cổ. Khác cảm giác chân thực — đây là cảm giác "
     "qua mô phỏng, tượng trưng, ẩn dụ. Mệnh-vận là một loại thể nghiệm sâu sắc, không phải số học cứng.",
     "paradigm", 10),

    ("Bổ", "補", ["bổ khí", "bổ cân bằng"],
     "CHÌA KHÓA VÀNG của Nhập môn Tứ trụ (theo Thiệu Vĩ Hoa, Chương 2). 'Bổ' = bổ sung khí ngũ hành "
     "thiếu trong Tứ trụ để cân bằng. Là gốc của lý thuyết Dụng Thần. Bổ qua: nghề nghiệp, môi trường, "
     "ẩm thực, màu sắc, phương vị, hôn nhân, tên gọi, vật dụng phong thủy. "
     "Không thay đổi mệnh (cố kết) nhưng giảm bất cân bằng → hướng cát tránh hung.",
     "paradigm", 24),

    # ── Âm Dương Ngũ Hành (Chương 2) ─────────────────────────────────────────
    ("Âm Dương", "陰陽", ["yin yang", "âm-dương"],
     "Hai khí đối lập + thống nhất, là gốc của vạn vật. Trong Tứ Trụ: Can-Chi đều có phân âm-dương "
     "(Giáp/Bính/Mậu/Canh/Nhâm dương; Ất/Đinh/Kỷ/Tân/Quý âm). Phân biệt âm-dương quyết định Thập Thần.",
     "ngu_hanh", 20),

    ("Ngũ Hành", "五行", ["5 hành", "kim-mộc-thủy-hỏa-thổ"],
     "Năm mô hình khí: Kim (Thu/Tây/Canh-Tân), Mộc (Xuân/Đông/Giáp-Ất), Thủy (Đông/Bắc/Nhâm-Quý), "
     "Hỏa (Hạ/Nam/Bính-Đinh), Thổ (Trung/Mậu-Kỷ). Không phải 5 nguyên tố hóa học — đây là 5 mô hình khí "
     "quan sát qua 5 hành tinh + mùa + phương vị.",
     "ngu_hanh", 20),

    ("Tương sinh", "相生", ["ngũ hành tương sinh", "sinh"],
     "Quy luật ngũ hành: Mộc→Hỏa→Thổ→Kim→Thủy→Mộc (vòng tuần hoàn). "
     "Sinh = nuôi dưỡng, tiếp khí. Mộc sinh Hỏa vì mộc tính ôn → hỏa ẩn phục trong mộc. "
     "Hỏa sinh Thổ vì cháy mộc thành tro = thổ. Thổ sinh Kim vì kim ẩn trong núi đá. "
     "Kim sinh Thủy vì khí thiếu âm chảy ngầm thành thủy. Thủy sinh Mộc vì thủy nhuận → cây mọc.",
     "ngu_hanh", 21),

    ("Tương khắc", "相剋", ["ngũ hành tương khắc", "khắc"],
     "Quy luật ngũ hành: Mộc khắc Thổ, Thổ khắc Thủy, Thủy khắc Hỏa, Hỏa khắc Kim, Kim khắc Mộc "
     "(quan hệ cách ngôi). Khắc = chế ngự, không tiêu diệt. Không có khắc thì không có cân bằng. "
     "Thiên Vĩ Hoa Q. 2: tương sinh + tương khắc đều có mặt thái quá + bất cập.",
     "ngu_hanh", 22),

    ("Thái quá", "太過", ["quá độ", "quá vượng"],
     "Khái niệm tinh tế hơn 'A sinh/khắc B'. Sinh quá nhiều = phản tác dụng: "
     "'Kim có thể sinh Thủy, nhưng Thủy nhiều thì Kim chìm'. 'Mộc sinh Hỏa, nhưng Hỏa nhiều thì Mộc bị đốt'. "
     "Engine `dung_than.py` đã model qua Điều Hậu.",
     "ngu_hanh", 22),

    ("Bất cập", "不及", ["nhược", "không đủ"],
     "Khí nhược → không đủ phát tác. Khi DM (Day Master) bất cập → cần Ấn + Tỷ/Kiếp BỔ. "
     "Khi khí khác bất cập → mất mặt tính tương ứng (mộc bất cập → tính chất phác/bác ái mất; "
     "kim bất cập → thiếu quyết đoán/cương trực).",
     "ngu_hanh", 22),

    ("Chế hóa", "制化", ["sinh khắc chế hóa"],
     "Chế = khắc khi vượng. Hóa = sinh chuyển thành khí khác (qua trung gian). "
     "Vd: Kim khắc Mộc trực tiếp (chế), nhưng nếu có Thủy thì Kim → Thủy → Mộc (hóa, chuyển khí thay vì khắc).",
     "ngu_hanh", 22),

    # ── 10 Thiên Can chi tiết ────────────────────────────────────────────────
    ("Giáp", "甲", ["mộc dương"],
     "Thiên can 1, mộc dương — đại thụ (cây lớn), thẳng, vươn cao. Tính nhân hậu, thẳng thắn, không khuất phục.",
     "thien_can", None),

    ("Ất", "乙", ["mộc âm"],
     "Thiên can 2, mộc âm — cây cỏ mềm, hoa lá. Tính uyển chuyển, dẻo dai, biết tùy hoàn cảnh.",
     "thien_can", None),

    ("Bính", "丙", ["hỏa dương"],
     "Thiên can 3, hỏa dương — mặt trời, hỏa lớn. Tính nóng nhanh, sáng tỏ, hào hùng, công khai.",
     "thien_can", None),

    ("Đinh", "丁", ["hỏa âm"],
     "Thiên can 4, hỏa âm — đèn dầu, lửa nến. Tính dịu nhưng dai, ấm áp, ẩn náu.",
     "thien_can", None),

    ("Mậu", "戊", ["thổ dương"],
     "Thiên can 5, thổ dương — núi lớn, đất khô cao. Tính trung hậu, vững vàng, độ lượng.",
     "thien_can", None),

    ("Kỷ", "己", ["thổ âm"],
     "Thiên can 6, thổ âm — đất ruộng ẩm, đất mềm. Tính tỉ mỉ, kiên trì, nuôi dưỡng.",
     "thien_can", None),

    ("Canh", "庚", ["kim dương"],
     "Thiên can 7, kim dương — kim loại thô, vũ khí. Tính cương trực, quyết đoán, dũng mãnh.",
     "thien_can", None),

    ("Tân", "辛", ["kim âm"],
     "Thiên can 8, kim âm — kim trang sức, ngọc tinh xảo. Tính tinh tế, nhạy cảm, kén chọn.",
     "thien_can", None),

    ("Nhâm", "壬", ["thủy dương"],
     "Thiên can 9, thủy dương — biển lớn, sông lớn. Tính rộng lượng, lưu động, trí tuệ rộng.",
     "thien_can", None),

    ("Quý", "癸", ["thủy âm"],
     "Thiên can 10, thủy âm — mưa, sương. Tính âm thầm, mềm mại, sâu sắc.",
     "thien_can", None),

    # ── 12 Địa Chi chi tiết ──────────────────────────────────────────────────
    ("Tý", "子", ["thủy dương"],
     "Địa chi 1, thủy dương — chuột. Giờ 23:00-01:00. Tàng can: Quý. "
     "Mùa đông giữa (tháng 11 ÂL). Phương Bắc.",
     "dia_chi", None),

    ("Sửu", "丑", ["thổ âm"],
     "Địa chi 2, thổ âm — trâu. Giờ 01:00-03:00. Tàng can: Kỷ, Quý, Tân. "
     "Tháng 12 ÂL. Phương Đông Bắc.",
     "dia_chi", None),

    ("Dần", "寅", ["mộc dương"],
     "Địa chi 3, mộc dương — hổ. Giờ 03:00-05:00. Tàng can: Giáp, Bính, Mậu. "
     "Tháng Giêng ÂL. Phương Đông Bắc. Khởi đầu Lập Xuân.",
     "dia_chi", None),

    ("Mão", "卯", ["mộc âm"],
     "Địa chi 4, mộc âm — mèo (VN) / thỏ (TQ). Giờ 05:00-07:00. Tàng can: Ất. "
     "Tháng 2 ÂL. Phương Đông.",
     "dia_chi", None),

    ("Thìn", "辰", ["thổ dương"],
     "Địa chi 5, thổ dương — rồng. Giờ 07:00-09:00. Tàng can: Mậu, Ất, Quý. "
     "Tháng 3 ÂL. Phương Đông Nam.",
     "dia_chi", None),

    ("Tỵ", "巳", ["hỏa âm"],
     "Địa chi 6, hỏa âm — rắn. Giờ 09:00-11:00. Tàng can: Bính, Mậu, Canh. "
     "Tháng 4 ÂL. Phương Đông Nam.",
     "dia_chi", None),

    ("Ngọ", "午", ["hỏa dương"],
     "Địa chi 7, hỏa dương — ngựa. Giờ 11:00-13:00. Tàng can: Đinh, Kỷ. "
     "Tháng 5 ÂL. Phương Nam.",
     "dia_chi", None),

    ("Mùi", "未", ["thổ âm"],
     "Địa chi 8, thổ âm — dê. Giờ 13:00-15:00. Tàng can: Kỷ, Đinh, Ất. "
     "Tháng 6 ÂL. Phương Tây Nam.",
     "dia_chi", None),

    ("Thân", "申", ["kim dương"],
     "Địa chi 9, kim dương — khỉ. Giờ 15:00-17:00. Tàng can: Canh, Nhâm, Mậu. "
     "Tháng 7 ÂL. Phương Tây Nam.",
     "dia_chi", None),

    ("Dậu", "酉", ["kim âm"],
     "Địa chi 10, kim âm — gà. Giờ 17:00-19:00. Tàng can: Tân. "
     "Tháng 8 ÂL. Phương Tây.",
     "dia_chi", None),

    ("Tuất", "戌", ["thổ dương"],
     "Địa chi 11, thổ dương — chó. Giờ 19:00-21:00. Tàng can: Mậu, Tân, Đinh. "
     "Tháng 9 ÂL. Phương Tây Bắc.",
     "dia_chi", None),

    ("Hợi", "亥", ["thủy âm"],
     "Địa chi 12, thủy âm — heo. Giờ 21:00-23:00. Tàng can: Nhâm, Giáp. "
     "Tháng 10 ÂL. Phương Tây Bắc.",
     "dia_chi", None),

    # ── Tàng Can (hidden stems) ──────────────────────────────────────────────
    ("Tàng Can", "藏干", ["tàng can địa chi", "hidden stems"],
     "Mỗi Địa Chi 'tàng' (chứa ẩn) 1-3 Thiên Can. Chi thuần (Tý, Mão, Ngọ, Dậu) tàng 1 can. "
     "Chi tạp tàng 2-3 can. Tàng can quyết định Cách Cục (qua Trụ Tháng) và Thập Thần ngầm.",
     "concept", None),

    ("Bản Khí", "本氣", ["primary hidden stem"],
     "Can chính (đầu tiên) trong tàng can của một Địa Chi. Vd: Bản khí của Dần là Giáp, "
     "Bản khí của Sửu là Kỷ. Bản khí Trụ Tháng quyết định Cách Cục chính của lá số.",
     "concept", None),

    # ── 10 Thập Thần ─────────────────────────────────────────────────────────
    ("Thập Thần", "十神", ["10 thần", "mười thần"],
     "10 mối quan hệ giữa Day Master (Nhật chủ) và mỗi Thiên Can khác trong lá số, dựa trên "
     "(sinh-khắc + cùng/khác âm dương). Là ngôn ngữ trung tâm của Tử Bình. "
     "10 thần: Tỷ Kiên, Kiếp Tài, Thực Thần, Thương Quan, Thiên Tài, Chính Tài, "
     "Thất Sát, Chính Quan, Thiên Ấn, Chính Ấn.",
     "thap_than", None),

    ("Tỷ Kiên", "比肩", ["Tỷ", "比"],
     "Cùng hành + cùng âm dương với Day Master. Biểu thị: anh em ngang vai, đồng nghiệp, cạnh tranh "
     "trực diện. Tích: hỗ trợ, độc lập, ý chí. Tiêu: cứng đầu, tranh chấp, hao của.",
     "thap_than", None),

    ("Kiếp Tài", "劫財", ["Kiếp", "劫"],
     "Cùng hành + khác âm dương với Day Master. Biểu thị: người cướp của, đối thủ ngầm. "
     "Tích: dũng mãnh, hành động nhanh. Tiêu: hao tổn tài lộc, dễ bị lừa, cướp đoạt vô hình. "
     "Khi Kiếp Tài ở Trụ Tháng → Dương Nhận cách (đặc biệt).",
     "thap_than", None),

    ("Thực Thần", "食神", ["Thực", "食"],
     "Day Master sinh ra, cùng âm dương. Biểu thị: tài năng sáng tạo, hưởng thụ, nuôi dưỡng. "
     "Tích: nghệ thuật, ẩm thực, giáo dục, sinh con, phúc lộc. Tiêu: lười nhác, ham hưởng thụ. "
     "Kỵ Thiên Ấn (Kiêu Thần đoạt Thực) → mất nguồn lộc.",
     "thap_than", None),

    ("Thương Quan", "傷官", ["Thương", "傷"],
     "Day Master sinh ra, khác âm dương. Biểu thị: tài năng vượt khuôn khổ, phá cách, nổi loạn. "
     "Tích: nghệ sĩ độc đáo, khởi nghiệp đột phá, ngôn ngữ tài. Tiêu: ngạo mạn, vô lễ, khắc Chồng (nữ). "
     "Cần Chính Ấn để 'Thương Quan phối Ấn' → tài năng có khuôn.",
     "thap_than", None),

    ("Thiên Tài", "偏財", ["T.Tài", "偏財"],
     "Day Master khắc, cùng âm dương. Biểu thị: tài lộc bất ngờ, đào hoa, đầu cơ. "
     "Tích: kinh doanh đa lĩnh vực, môi giới, có sức hút. Tiêu: phá tài bất ngờ, đào hoa loạn.",
     "thap_than", None),

    ("Chính Tài", "正財", ["C.Tài", "正財"],
     "Day Master khắc, khác âm dương. Biểu thị: tài chính ổn định, lương cứng, vợ chính (Nam). "
     "Tích: cần kiệm, tích lũy, gia đình ổn. Tiêu: cứng nhắc, sợ rủi ro. "
     "Khi Day Master vượng + Chính Tài vượng → đại phú.",
     "thap_than", None),

    ("Thất Sát", "七殺", ["Sát", "偏官", "Thiên Quan"],
     "Khắc Day Master, cùng âm dương. Biểu thị: quyền lực dữ dội, áp lực, tướng quân, đối thủ mạnh. "
     "Tích: quân đội, công an, kinh doanh mạo hiểm, leadership. Tiêu: tai họa, kiện tụng, kẻ thù. "
     "Cần Thực Thần CHẾ Sát hoặc Ấn HÓA Sát → quý hiển.",
     "thap_than", None),

    ("Chính Quan", "正官", ["Quan", "正官"],
     "Khắc Day Master, khác âm dương. Biểu thị: chức tước chính thống, kỷ luật, chồng (Nữ). "
     "Tích: công chức, chức vụ chính danh, danh tiếng tốt. Tiêu: gò bó, áp lực kỷ luật. "
     "Sợ Thương Quan đả phá, sợ Thất Sát hỗn tạp.",
     "thap_than", None),

    ("Thiên Ấn", "偏印", ["T.Ấn", "Kiêu Thần", "偏印"],
     "Sinh Day Master, cùng âm dương. Biểu thị: quý nhân ngầm, mẹ kế, trí tuệ phi truyền thống. "
     "Tích: thiền, tôn giáo, nghiên cứu lập dị, công nghệ. Tiêu: Kiêu Thần đoạt Thực Thần → mất phúc.",
     "thap_than", None),

    ("Chính Ấn", "正印", ["C.Ấn", "正印"],
     "Sinh Day Master, khác âm dương. Biểu thị: mẹ ruột, học vấn chính quy, ấn tín bảo hộ. "
     "Tích: trí tuệ, danh tiếng học thuật, nhân từ, từ thiện. Tiêu: ỷ lại, lười suy nghĩ độc lập. "
     "Kỵ Chính Tài đoạt Ấn.",
     "thap_than", None),

    # ── Cách Cục ──────────────────────────────────────────────────────────────
    ("Cách Cục", "格局", ["pattern"],
     "Pattern cổ điển phân loại lá số Tử Bình, dựa trên Bản Khí của Trụ Tháng + quan hệ Thập Thần "
     "với Day Master. 8 cách thường + 2 cách đặc biệt. Cách Cục → quyết định cách chọn Dụng Thần "
     "+ hướng diễn giải toàn lá số. Reference: 子平真詮 Chương 12-22.",
     "cach_cuc", None),

    ("Chính Quan cách", "正官格", ["官格"],
     "Khi Bản Khí Trụ Tháng = Chính Quan của Day Master. Polarity: lành (quý). "
     "Hợp công chức / chức vụ chính danh. Cần Ấn bảo hộ. "
     "Kỵ Thương Quan đả phá + Thất Sát hỗn tạp.",
     "cach_cuc", None),

    ("Thất Sát cách", "七殺格", ["殺格", "偏官格"],
     "Khi Bản Khí Trụ Tháng = Thất Sát. Polarity: mạnh (hung-thành-quý). "
     "Hợp quân đội / công an / kinh doanh mạo hiểm. Cần Thực Thần chế Sát hoặc Ấn hóa Sát. "
     "Sát quá mạnh + không chế hóa → tai họa, kiện tụng.",
     "cach_cuc", None),

    ("Chính Tài cách", "正財格", ["財格"],
     "Khi Bản Khí Trụ Tháng = Chính Tài. Polarity: lành (phú). "
     "Day Master vượng + Tài vượng → đại phú. Cần Thực Thương sinh Tài. "
     "Kỵ Kiếp Tài cướp đoạt + Day Master nhược không gánh nổi Tài.",
     "cach_cuc", None),

    ("Thiên Tài cách", "偏財格", ["偏財"],
     "Khi Bản Khí Trụ Tháng = Thiên Tài. Polarity: lành (phú, đào hoa). "
     "Phù hợp khởi nghiệp, kinh doanh đa lĩnh vực, môi giới. Tài lộc bất ngờ + có sức hút. "
     "Kỵ Tỉ Kiếp cướp Tài.",
     "cach_cuc", None),

    ("Thực Thần cách", "食神格", ["食格"],
     "Khi Bản Khí Trụ Tháng = Thực Thần. Polarity: lành (phúc, hưởng thụ). "
     "Sao sáng tạo + tận hưởng — tài năng + ăn lộc. Hợp nghệ thuật, sáng tạo, ẩm thực, giáo dục. "
     "Kỵ Kiêu Thần (Thiên Ấn) đoạt Thực Thần.",
     "cach_cuc", None),

    ("Thương Quan cách", "傷官格", ["傷格"],
     "Khi Bản Khí Trụ Tháng = Thương Quan. Polarity: phá cách — vừa lành vừa dữ. "
     "Tài năng vượt khuôn khổ — phá cách, nổi loạn. Hợp nghệ sĩ, sáng tạo độc đáo, khởi nghiệp đột phá. "
     "Cần Chính Ấn để 'Thương Quan phối Ấn'. Kỵ 'Thương Quan kiến Quan' đại hung khi Day Master nhược.",
     "cach_cuc", None),

    ("Chính Ấn cách", "正印格", ["印格"],
     "Khi Bản Khí Trụ Tháng = Chính Ấn. Polarity: lành (quý + an dưỡng). "
     "Sao mẹ + học vấn + bảo hộ. Hợp giáo dục, học thuật, nghiên cứu, từ thiện. "
     "Kỵ Tài tinh đoạt Ấn (Chính Tài phá Chính Ấn). Quá nhiều Ấn → ỷ lại.",
     "cach_cuc", None),

    ("Thiên Ấn cách", "偏印格", ["梟印格"],
     "Khi Bản Khí Trụ Tháng = Thiên Ấn (Kiêu Thần). Polarity: trung tính — đa năng nhưng khắc nghiệt. "
     "Trí tuệ phi truyền thống, quý nhân ngầm. Hợp thiền / tôn giáo / nghiên cứu lập dị / công nghệ. "
     "Kỵ Thiên Ấn đoạt Thực Thần.",
     "cach_cuc", None),

    ("Kiến Lộc cách", "建祿格", ["祿格"],
     "Cách ĐẶC BIỆT khi Bản Khí Trụ Tháng = chính Day Master (Lộc Thần ngụ tại Trụ Tháng). "
     "Day Master đắc lệnh. Cần Tài hoặc Quan để hóa khí — không thì cô đơn vô dụng. "
     "Thiếu Tài + thiếu Quan → người tự lập nhưng nghèo + cô.",
     "cach_cuc", None),

    ("Dương Nhận cách", "羊刃格", ["刃格"],
     "Cách ĐẶC BIỆT khi Bản Khí Trụ Tháng = Kiếp Tài của Day Master. Cực vượng. "
     "Sao quyền + tai nạn. Hợp tướng quân / kinh doanh mạo hiểm / phẫu thuật. "
     "Sợ Thất Sát phối Nhận (羊刃逢沖) → tai nạn lớn.",
     "cach_cuc", None),

    # ── Dụng Thần ─────────────────────────────────────────────────────────────
    ("Dụng Thần", "用神", ["thần dùng", "useful god"],
     "Hành cốt yếu CỨU mệnh — 'thuốc' cho lá số. "
     "Quy tắc: Day Master VƯỢNG → cần khí làm hao/tiết (Thực/Thương, Tài, Quan/Sát). "
     "Day Master NHƯỢC → cần khí hỗ trợ (Ấn, Tỷ/Kiếp). "
     "Đại Vận đi vào Dụng Thần → vận tốt. Đi vào Kỵ Thần → vận xấu. "
     "Engine `dung_than.py` đã model + bổ sung Điều Hậu (climate balance).",
     "dung_than", None),

    ("Hỷ Thần", "喜神", ["hỉ thần"],
     "Hành phụ trợ Dụng Thần. Sinh ra Dụng Thần. Vd: Dụng Thần là Hỏa thì Hỷ Thần là Mộc (sinh Hỏa).",
     "dung_than", None),

    ("Kỵ Thần", "忌神", ["kỵ"],
     "Hành đối nghịch Dụng Thần. Khắc Dụng Thần → cản trở mệnh. Đại Vận đi vào Kỵ Thần → cần đề phòng.",
     "dung_than", None),

    ("Điều Hậu", "調候", ["climate balance"],
     "Cân bằng theo NHIỆT-LẠNH-KHÔ-ƯỚT của tháng sinh. Từ Cùng Thông Bảo Giám (窮通寶鑑). "
     "Mùa Hè (Tỵ-Ngọ-Mùi) khô nóng → cần Thủy. Mùa Đông (Hợi-Tý-Sửu) lạnh ẩm → cần Hỏa. "
     "Engine `dung_than.py` áp dụng v2: khi Dụng Thần cường-độ-thuần không đồng ý Dụng Thần khí hậu → "
     "ưu tiên cường độ làm chính + khí hậu làm Hỷ Thần.",
     "dung_than", None),

    # ── Vòng Trường Sinh ──────────────────────────────────────────────────────
    ("Vòng Trường Sinh", "長生十二宮", ["12 vòng"],
     "12 giai đoạn vòng đời của Day Master tại mỗi Địa Chi: Trường Sinh, Mộc Dục, Quan Đới, "
     "Lâm Quan, Đế Vương, Suy, Bệnh, Tử, Mộ, Tuyệt, Thai, Dưỡng. "
     "Tổng điểm sức sống Day Master = sum điểm 4 trụ. Engine `truong_sinh.py` đã implement.",
     "truong_sinh", None),

    ("Trường Sinh", "長生", ["1"],
     "Phase 1/12. Day Master mới sinh ra — non yếu nhưng đầy tiềm năng. Như đứa trẻ. Điểm +2.",
     "truong_sinh", None),

    ("Mộc Dục", "沐浴", ["2"],
     "Phase 2/12. Day Master được tắm rửa — yếu, dễ lộ liễu, đào hoa. Điểm -1.",
     "truong_sinh", None),

    ("Quan Đới", "冠帶", ["3"],
     "Phase 3/12. Day Master đội mũ thắt đai — bắt đầu trưởng thành. Điểm +1.",
     "truong_sinh", None),

    ("Lâm Quan", "臨官", ["4", "禄"],
     "Phase 4/12. Day Master nhận chức (Lộc Thần). Mạnh khỏe, đắc dụng. Điểm +2.",
     "truong_sinh", None),

    ("Đế Vương", "帝旺", ["5", "đế vượng"],
     "Phase 5/12. Day Master cực thịnh — đỉnh điểm. Điểm +3. Đỉnh trước khi suy.",
     "truong_sinh", None),

    ("Suy", "衰", ["6"],
     "Phase 6/12. Day Master bắt đầu suy giảm sau đỉnh. Điểm 0.",
     "truong_sinh", None),

    ("Bệnh", "病", ["7"],
     "Phase 7/12. Day Master đau ốm — yếu thêm. Điểm -1.",
     "truong_sinh", None),

    ("Tử", "死", ["8"],
     "Phase 8/12. Day Master tử — cực nhược nhưng chưa tắt hẳn. Điểm -2.",
     "truong_sinh", None),

    ("Mộ", "墓", ["9", "khố"],
     "Phase 9/12. Day Master nhập mộ (kho chứa). Khí ẩn. Điểm -1.",
     "truong_sinh", None),

    ("Tuyệt", "絕", ["10"],
     "Phase 10/12. Day Master cực tuyệt — không còn khí. Điểm -3.",
     "truong_sinh", None),

    ("Thai", "胎", ["11"],
     "Phase 11/12. Day Master tái sinh — khí mới bắt đầu nhú. Điểm -1.",
     "truong_sinh", None),

    ("Dưỡng", "養", ["12"],
     "Phase 12/12. Day Master nuôi dưỡng trong thai — chuẩn bị sinh ra. Điểm 0.",
     "truong_sinh", None),

    # ── Đại Vận ───────────────────────────────────────────────────────────────
    ("Đại Vận", "大運", ["đại vận", "10-year cycle"],
     "Chu kỳ 10 năm. Khởi vận tính theo khoảng cách từ giờ sinh tới Tiết Khí gần nhất "
     "(Lập Xuân / Lập Hạ / ...). Vận đi THUẬN (nam Dương / nữ Âm) hoặc NGHỊCH (nam Âm / nữ Dương). "
     "Đại Vận đi vào Dụng Thần → 10 năm thuận. Vào Kỵ Thần → 10 năm thử thách. "
     "Engine `dai_van.py` đã implement.",
     "dai_van", None),

    ("Lưu Niên", "流年", ["lưu niên", "yearly"],
     "Năm hiện tại — đi qua lá số. Lưu Niên tương tác với Đại Vận + Tứ Trụ gốc → "
     "tạo cấu hình khí trong năm đó.",
     "dai_van", None),

    ("Tiết Khí", "節氣", ["24 tiết khí"],
     "24 mốc thời tiết trong năm Mặt Trời. Tử Bình KHÔNG dùng đầu tháng âm lịch — dùng TIẾT KHÍ. "
     "Lập Xuân (4-5/2) là đầu Trụ Tháng Dần. Tháng đổi tại Tiết, không tại mùng 1 ÂL.",
     "concept", None),

    # ── Thần Sát ──────────────────────────────────────────────────────────────
    ("Thần Sát", "神煞", ["sao phụ"],
     "Sao phụ trong lá số (không phải sao chính của Bát Tự). Vd: Thái Cực Quý Nhân, Thiên Ất Quý Nhân, "
     "Đào Hoa, Dịch Mã, Văn Xương, Hồng Diễm, Cô Thần, Quả Tú, Kiếp Sát, Vong Thần, Lộc Thần, Dương Nhận. "
     "Mỗi sao có polarity (tốt/xấu/trung tính). Engine `than_sat.py` sàng 15 sao cốt lõi.",
     "than_sat", None),

    ("Thiên Ất Quý Nhân", "天乙貴人", ["quý nhân"],
     "Sao quý nhân hộ mệnh, đứng đầu các Thần Sát. Khi gặp tai họa → có người giúp đỡ ngầm. "
     "Polarity: cực tốt.",
     "than_sat", None),

    ("Đào Hoa", "桃花", ["đào hoa"],
     "Sao tình duyên + nhan sắc. Tích: hấp dẫn người khác giới, có sức hút xã giao. "
     "Tiêu: dễ vướng tình cảm phức tạp, đào hoa loạn.",
     "than_sat", None),

    ("Dịch Mã", "驛馬", ["mã"],
     "Sao di chuyển + xa nhà + đi nước ngoài. Người có Dịch Mã → đời di chuyển nhiều, "
     "thường thay đổi nơi ở/công việc.",
     "than_sat", None),

    ("Văn Xương", "文昌", ["văn"],
     "Sao học vấn + thi cử. Người có Văn Xương → có duyên với học hành, sách vở, văn chương.",
     "than_sat", None),

    ("Hồng Diễm", "紅艷", [],
     "Sao đào hoa nặng — mạnh hơn Đào Hoa thông thường. Cảnh giác quan hệ tình cảm dễ vướng.",
     "than_sat", None),

    ("Cô Thần", "孤辰", [],
     "Sao cô độc với nam giới. Người có Cô Thần → khó kết hôn / hôn nhân xa cách.",
     "than_sat", None),

    ("Quả Tú", "寡宿", [],
     "Sao cô độc với nữ giới. Người có Quả Tú → khó có chồng / sống một mình.",
     "than_sat", None),

    ("Kiếp Sát", "劫煞", [],
     "Sao tai họa bất ngờ — cướp, lừa, tai nạn. Cần đề phòng.",
     "than_sat", None),

    ("Vong Thần", "亡神", [],
     "Sao mất mát — của cải, người thân, danh tiếng. Polarity: xấu.",
     "than_sat", None),

    ("Lộc Thần", "祿神", ["lộc"],
     "Sao tài lộc chính thống — vị trí Lâm Quan (4) trong vòng Trường Sinh. "
     "Cùng paradigm Kiến Lộc cách.",
     "than_sat", None),

    # ── Day Master (Nhật Chủ) ─────────────────────────────────────────────────
    ("Nhật Chủ", "日主", ["Day Master", "Nhật Can", "Bản Thân"],
     "Thiên Can của Trụ Ngày — đại biểu cho BẢN THÂN người được xem. Tất cả các phân tích Thập Thần, "
     "Dụng Thần, Cách Cục đều quy chiếu về Nhật Chủ. "
     "Trong engine: `day_master.stem` + `day_master.element`.",
     "concept", None),

    ("Cường độ Nhật Chủ", "日主強弱", ["vượng nhược"],
     "Mức độ MẠNH/YẾU của Day Master trong lá số. 3 hạng: Vượng (cường), Nhược (yếu), Trung hòa. "
     "Tính bằng: Support (Tỷ/Kiếp + Ấn cùng hành) trừ Drain (Thực/Thương + Tài + Quan/Sát). "
     "Quyết định hướng chọn Dụng Thần. Engine: `day_master_assessment.strength_tag`.",
     "concept", None),

    # ── Lục Thân ──────────────────────────────────────────────────────────────
    ("Lục Thân", "六親", ["6 thân", "family relations"],
     "Cách map Thập Thần → quan hệ gia đình: "
     "Tỷ/Kiếp = anh em. Thực/Thương = con cái/cấp dưới. "
     "Chính Tài = vợ chính (Nam) + tài chính ổn. Thiên Tài = cha + tài lộc bất ngờ. "
     "Chính Quan = chồng (Nữ) + cấp trên. Thất Sát = quyền/kẻ địch. "
     "Chính Ấn = mẹ ruột + học vấn. Thiên Ấn = mẹ kế + quý nhân ngầm.",
     "concept", None),
]


# ─── Insert logic ─────────────────────────────────────────────────────────────

def main() -> int:
    now = int(time.time())
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 1) Add Trần Viên (co-author)
    cur.execute("""
        INSERT OR IGNORE INTO authors (name_vi, name_zh, tier_in_lineage, era, worldview_school, bio_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Trần Viên", "陳園", 5, "hiện-đại", "tu_binh_ba_tu",
          "Đồng tác giả + biên tập 'Dự đoán theo Tứ trụ' với Thiệu Vĩ Hoa.", now))
    tran_vien_id = cur.lastrowid or cur.execute(
        "SELECT author_id FROM authors WHERE name_vi='Trần Viên'"
    ).fetchone()[0]

    # 2) Update Thiệu Vĩ Hoa with richer info
    cur.execute("""
        UPDATE authors
        SET worldview_school='tu_binh_ba_tu',
            foundational_axioms=?,
            hermeneutic_style=?,
            works=?,
            bio_summary=?
        WHERE author_id=10
    """, (
        json.dumps([
            "Mệnh-Vận là một loại THỂ NGHIỆM, không phải số học cứng.",
            "Tử Bình KHÔNG mê tín — cùng paradigm âm dương ngũ hành như Trung y.",
            "BỔ cân bằng = chìa khóa vàng (chữ 'Bổ' xuyên suốt Chương 2 sách Tứ Trụ).",
            "Mệnh cố kết + Vận lưu biến. Vận đi đúng Dụng Thần → cải mệnh được.",
        ], ensure_ascii=False),
        "Tổng kết kinh nghiệm thực hành + so sánh với Trung y + biện chính 'mê tín'/'khoa học'. "
        "Văn phong dạy học (target độc giả Việt hiện đại). Cross-ref Tử Bình cổ điển + Chu Dịch.",
        json.dumps([
            "Dự đoán theo Tứ trụ (1994/1999 — bản Việt 1999)",
            "Chu Dịch Dự Đoán Các Ví Dụ Có Giải",
            "Chu dịch và dự đoán học",
        ], ensure_ascii=False),
        "Sinh 1936, mất 2020. Đại sư Trung Quốc đương đại về Chu Dịch + Tử Bình. "
        "Tác giả 30+ sách lý số. Tài liệu Tử Bình phổ biến nhất tại Việt Nam. "
        "Co-author 'Dự đoán theo Tứ trụ' với Trần Viên (dịch giả Việt: Nguyễn Văn Mậu).",
    ))

    # 3) Add work entry
    cur.execute("""
        INSERT OR IGNORE INTO works (author_id, title_vi, title_zh, year_composed, role, corpus_id, is_canonical, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (10, "Dự đoán theo Tứ trụ", "四柱預測學", 1994, "co-author", CORPUS_ID, 1,
          "Tài liệu nhập môn Tử Bình phổ biến nhất tại VN. 681 trang. "
          "Dịch giả: Nguyễn Văn Mậu. NXB Văn hóa Thông tin tái bản lần 4.", now))

    # 4) Insert concepts
    inserted = 0
    updated = 0
    for canonical_vi, canonical_zh, aliases, short_note, category, first_page in CONCEPTS:
        # Check existing
        existing = cur.execute(
            "SELECT concept_id, corpora FROM concept_index WHERE canonical_vi=? AND canonical_zh=?",
            (canonical_vi, canonical_zh)
        ).fetchone()
        if existing:
            # Append corpus + update short_note if shorter than ours
            cid, old_corpora_json = existing
            try:
                old_corpora = json.loads(old_corpora_json) if old_corpora_json else []
            except json.JSONDecodeError:
                old_corpora = []
            if CORPUS_ID not in old_corpora:
                old_corpora.append(CORPUS_ID)
            # Update with merged corpora + our short_note if better
            cur.execute("""
                UPDATE concept_index
                SET corpora = ?,
                    short_note = CASE WHEN length(short_note) < length(?) THEN ? ELSE short_note END,
                    category = COALESCE(category, ?),
                    school = COALESCE(school, ?)
                WHERE concept_id=?
            """, (json.dumps(old_corpora, ensure_ascii=False), short_note, short_note,
                  category, SCHOOL, cid))
            updated += 1
        else:
            cur.execute("""
                INSERT INTO concept_index (canonical_vi, canonical_zh, aliases, short_note,
                                            first_seen_corpus, first_seen_page, category, corpora, school, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (canonical_vi, canonical_zh,
                  json.dumps(aliases, ensure_ascii=False),
                  short_note, CORPUS_ID, first_page, category,
                  json.dumps([CORPUS_ID], ensure_ascii=False),
                  SCHOOL, now))
            inserted += 1

    conn.commit()
    print(f"Inserted {inserted} new concepts, updated {updated} existing concepts.")
    print(f"Author Trần Viên: id={tran_vien_id}")
    print(f"Updated Thiệu Vĩ Hoa (id=10) with paradigm axioms.")
    print(f"Added work entry: 'Dự đoán theo Tứ trụ' (corpus={CORPUS_ID}).")

    # Final stats
    total = cur.execute("SELECT COUNT(*) FROM concept_index").fetchone()[0]
    bat_tu_concepts = cur.execute(
        "SELECT COUNT(*) FROM concept_index WHERE school=?", (SCHOOL,)
    ).fetchone()[0]
    print(f"\nWiki total concepts: {total}")
    print(f"Bát Tự / Tử Bình school concepts: {bat_tu_concepts}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
