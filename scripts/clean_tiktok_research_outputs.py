#!/usr/bin/env python3
"""
Build reader-friendly research transcript files from extracted TikTok text.

This does deterministic cleanup only: it removes repeated technical metadata from
the combined file format, normalizes common TikTok caption casing errors, and
keeps one compact source line per video.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"


COMMON_WORD_FIXES = {
    "AI": "ai",
    "BA": "ba",
    "Cao": "cao",
    "Cho": "cho",
    "Ra": "ra",
    "SAO": "sao",
    "Sai": "sai",
    "Tay": "tay",
    "Theo": "theo",
    "Xu": "xu",
    "Xin": "xin",
}

PHRASE_FIXES = [
    (r"\btử VI\b", "tử vi"),
    (r"\bTử VI\b", "Tử vi"),
    (r"\btừ VI\b", "tử vi"),
    (r"\bTừ VI\b", "Tử vi"),
    (r"\btử bi\b", "tử vi"),
    (r"\bTử bi\b", "Tử vi"),
    (r"\btừ bi đẩu số\b", "tử vi đẩu số"),
    (r"\bTừ bi đẩu số\b", "Tử vi đẩu số"),
    (r"\btử vì\b", "tử vi"),
    (r"\bTử vì\b", "Tử vi"),
    (r"\btừ vi\b", "tử vi"),
    (r"\bTừ vi\b", "Tử vi"),
    (r"\bđầu số\b", "đẩu số"),
    (r"\bĐầu số\b", "Đẩu số"),
    (r"\blá số tử VI\b", "lá số tử vi"),
    (r"\blà số tử vi\b", "lá số tử vi"),
    (r"\blà số\b", "lá số"),
    (r"\blá số này\b", "lá số này"),
    (r"\blận giải\b", "luận giải"),
    (r"\blợn giải\b", "luận giải"),
    (r"\blận lá số\b", "luận lá số"),
    (r"\b7 bại\b", "thất bại"),
    (r"\b7 nghiệp\b", "thất nghiệp"),
    (r"\bnội 7\b", "nội thất"),
    (r"\b2 BA\b", "hai ba"),
    (r"\bthứ BA\b", "thứ ba"),
    (r"\bThứ BA\b", "Thứ ba"),
    (r"\btứ chủ 8 tự\b", "tứ trụ bát tự"),
    (r"\btứ châu 8 tự\b", "tứ trụ bát tự"),
    (r"\bcùng bài\b", "cúng bái"),
    (r"\btương Lai\b", "tương lai"),
    (r"\bTương Lai\b", "Tương lai"),
    (r"\bTai họa\b", "tai họa"),
    (r"\bcái Kim\b", "cái kim"),
    (r"\bVA chạm\b", "va chạm"),
    (r"\bchồng em chào anh nhá\b", "chồng em"),
    (r"\buống rượu thứ\b", "phương diện thứ"),
    (r"\bphương vị thứ\b", "phương diện thứ"),
    (r"\bbệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bmệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bsắp phá tham\b", "Sát Phá Tham"),
    (r"\bphàm quân\b", "Phá Quân"),
    (r"\btham Lam\b", "Tham Lang"),
    (r"\bTham Lam\b", "Tham Lang"),
    (r"\bcựu môn\b", "Cự Môn"),
    (r"\bngười đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ người đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyện đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyệt đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bphá tan\b", "Phá Tham"),
    (r"\bphá tha\b", "Phá Tham"),
    (r"\bthiên hạ\b", "thiên hạ"),
    (r"\bkhông AI\b", "không ai"),
    (r"\bAI cũng\b", "ai cũng"),
    (r"\bAI là\b", "ai là"),
    (r"\bAI nhìn\b", "anh nhìn"),
    (r"\bchống tương lai\b", "chồng tương lai"),
    (r"\bchống sau\b", "chồng sau"),
    (r"\bđời chống\b", "đời chồng"),
    (r"\blấy chống\b", "lấy chồng"),
    (r"\blay chống\b", "lấy chồng"),
    (r"\bvợ chống\b", "vợ chồng"),
    (r"\bnảy\b", "này"),
    (r"\bbao lầu\b", "bao lâu"),
    (r"\bnến tảng\b", "nền tảng"),
    (r"\bhồn nhẫn\b", "hôn nhân"),
    (r"\bLuận sưỡng\b", "Luận sướng"),
    (r"\bkhö qUa\b", "khổ qua"),
    (r"\bPhu The\b", "Phu Thê"),
    (r"\bnghé\b", "nghề"),
    (r"\bnghể\b", "nghề"),
    (r"\bngäy\b", "ngày"),
    (r"\bkhong\b", "không"),
    (r"\bthong qua\b", "thông qua"),
    (r"\bthang sinh\b", "tháng sinh"),
    (r"\bvan han\b", "vận hạn"),
    (r"\bKham pha\b", "Khám phá"),
    (r"\bphan\b", "phận"),
    (r"\bphat đạt\b", "phát đạt"),
    (r"\bPhat\b", "Phật"),
    (r"\bPhật P\b", "Phật"),
    (r"\bAmlich\b", "Âm lịch"),
    (r"\bTac hai\b", "Tác hại"),
    (r"\bbổ me\b", "bố mẹ"),
    (r"\bgidu\b", "giàu"),
    (r"\bgiảu\b", "giàu"),
    (r"\btải lộc\b", "tài lộc"),
    (r"\bthì lam\b", "thì làm"),
    (r"\bgi\b", "gì"),
    (r"\bvỉ trí\b", "vị trí"),
    (r"\bVong Trưởng Sinh\b", "Vòng Trường Sinh"),
    (r"\bdo gid sinh\b", "đổi giờ sinh"),
    (r"\bthi cảng\b", "thì càng"),
    (r"\bdau rắc\b", "đâu rắc"),
    (r"\bSóng gid\b", "Sống nhờ"),
    (r"\bphủ đởi trai\b", "phụ đời trai"),
    (r"\bhồn nhần\b", "hôn nhân"),
    (r"\bhồn nhẫn\b", "hôn nhân"),
    (r"\bnhẫn duyên\b", "nhân duyên"),
    (r"\bNhẫn quả\b", "Nhân quả"),
    (r"\bdung cách\b", "đúng cách"),
    (r"\bhanh thông\b", "hanh thông"),
    (r"\bKhi Thiên Cơ\b", "Khi Thiên Cơ"),
    (r"\bthực sự nghi\b", "thực sự nghĩ"),
    (r"\bNgồi sao\b", "Ngôi sao"),
    (r"\blam an xa\b", "làm ăn xa"),
    (r"\bmay man\b", "may mắn"),
    (r"\bgap chong\b", "gặp chồng"),
    (r"\bVảo nam nao\b", "vào năm nào"),
    (r"\bthanh công\b", "thành công"),
    (r"\bNang khiéu bam sinh\b", "Năng khiếu bẩm sinh"),
    (r"\bcon cải\b", "con cái"),
    (r"\bĐồ tuổi\b", "Độ tuổi"),
    (r"\bChon chong\b", "Chọn chồng"),
    (r"\bnảo\b", "nào"),
    (r"\bco tam thức\b", "có tâm thức"),
    (r"\bSắt tỉnh\b", "Sát tinh"),
    (r"\bhang nhất\b", "hạng nhất"),
    (r"\bHôn phổi\b", "Hôn phối"),
    (r"\bTrồng sẽ\b", "Chồng sẽ"),
    (r"\bnhin của\b", "nhìn của"),
    (r"\bquan Giàu\b", "Quan giàu"),
    (r"\bPhu Thề\b", "Phu Thê"),
    (r"\blành dữ\b", "lành dữ"),
    (r"\bDung mạo\b", "Dung mạo"),
    (r"\bxinh xan\b", "xinh xắn"),
    (r"\bthưởng có\b", "thường có"),
    (r"\bquan trong\b", "quan trọng"),
    (r"\btỉnh duyén\b", "tình duyên"),
    (r"\bnam sau\b", "năm sau"),
    (r"\bTải Bạch\b", "Tài Bạch"),
    (r"\blay Mệnh\b", "lấy Mệnh"),
    (r"\bthi hon nhãn viên man\b", "thì hôn nhân viên mãn"),
    (r"\btiền đổ\b", "tiền đồ"),
    (r"\btiển đồ\b", "tiền đồ"),
    (r"\bbản thần\b", "bản thân"),
    (r"\bThién Di\b", "Thiên Di"),
    (r"\bLý do\b", "Lý do"),
    (r"\bxdu\b", "xấu"),
    (r"\bnhan sắc\b", "nhan sắc"),
    (r"\blay được\b", "lấy được"),
    (r"\bmat sẽ\b", "mặt sẽ"),
    (r"\bmất sẽ\b", "mặt sẽ"),
    (r"\bCoi số mệnh sau này mặt sẽ ra sao: an\b", "Coi số mệnh sau này mặt sẽ ra sao"),
    (r"\bCap đồi\b", "Cặp đôi"),
    (r"\bđồi oan gia\b", "đôi oan gia"),
    (r"\bj\.\b", "gì"),
    (r"\bhôn k nhãn\b", "hôn nhân"),
    (r"\bthần ông Huỳnh Để\b", "thần Ông Huỳnh Đế"),
    (r"\bconTrdihay / con\b", "con trai hay con"),
    (r"\bTử Tức\b", "Tử Tức"),
    (r"\bTu Tức\b", "Tử Tức"),
    (r"\bBại tỉnh\b", "Bại tinh"),
    (r"\bquý tử ey F\b", "quý tử"),
    (r"\bcốtcách\b", "cốt cách"),
    (r"\btình số\b", "tính số"),
    (r"\btinh số\b", "tính số"),
    (r"\bHén\b", "Hèn"),
    (r"\blận dan\b", "luận đoán"),
    (r"\bHầu vẫn\b", "Hậu vận"),
    (r"\bphan\b", "phận"),
    (r"\bNhãn duyên\b", "Nhân duyên"),
    (r"\bChính tỉnh\b", "Chính tinh"),
    (r"\btải chính\b", "tài chính"),
    (r"\bdé bi ban đởi phản bồi\b", "dễ bị bạn đời phản bội"),
    (r"\bdé lấy\b", "dễ lấy"),
    (r"\bgioi kiem tien\b", "giỏi kiếm tiền"),
    (r"\bGidu lam\b", "giàu lắm"),
    (r"\bChöng\b", "Chồng"),
    (r"\bnhan sắc\b", "nhan sắc"),
    (r"\bNhìn phat\b", "Nhìn phát"),
    (r"\blay chồng\b", "lấy chồng"),
    (r"\bsông không tho\b", "sống không thọ"),
    (r"\blấychồng\b", "lấy chồng"),
    (r"\bcangdechialy\b", "càng dễ chia ly"),
    (r"\bPhu Thé\b", "Phu Thê"),
    (r"\bPhu thé\b", "Phu Thê"),
    (r"\bPhuc\b", "Phúc"),
    (r"\bHon nhẫn\b", "Hôn nhân"),
    (r"\bhồn nhân\b", "hôn nhân"),
    (r"\bhồn nhan\b", "hôn nhân"),
    (r"\bsao doi\b", "sao đôi"),
    (r"\bnay thi lam\b", "này thì làm"),
    (r"\bcon lả\b", "con là"),
    (r"\blả\b", "là"),
    (r"\btải:\s*\.\s*lộc\b", "tài lộc"),
    (r"\bThang nao nam nay\b", "Tháng nào năm nay"),
    (r"\bhầu van va con cai\b", "hậu vận và con cái"),
    (r"\bcon cai\b", "con cái"),
    (r"\bthảnh công\b", "thành công"),
    (r"\bNang khiéu bam h sinh\b", "Năng khiếu bẩm sinh"),
    (r"\bNang khiéu bam sinh\b", "Năng khiếu bẩm sinh"),
    (r"\bhơn kem\b", "hơn kém"),
    (r"\bgiàu lam\b", "giàu lắm"),
    (r"\bMenh\b", "Mệnh"),
    (r"\bnền tránh xa\b", "nên tránh xa"),
    (r"\bđảo hoa\b", "đào hoa"),
    (r"\bchống qua\b", "chồng qua"),
    (r"\bThiền Di\b", "Thiên Di"),
    (r"\bit con\b", "ít con"),
    (r"\btrồng ra sao\b", "trông ra sao"),
    (r"\bvôchính\b", "vô chính"),
    (r"\bco ý nghĩa\b", "có ý nghĩa"),
    (r"\bco ÿ nghĩa\b", "có ý nghĩa"),
    (r"\bso nhất sao gì\b", "sợ nhất sao gì"),
    (r"\bchống it\b", "chồng ít"),
    (r"\bit hay\b", "ít hay"),
    (r"\bBan sẽ\b", "Bạn sẽ"),
    (r"\bcảng\b", "càng"),
    (r"\bSf\b", ""),
    (r"\bchac chan\b", "chắc chắn"),
    (r"\bsinh đổi kha\b", "sinh đời khá"),
    (r"\bHe lo\b", "Hé lộ"),
    (r"\bVị sao\b", "Vì sao"),
    (r"\bsống gid\b", "sống giờ"),
    (r"\bú bế\b", "u bế"),
    (r"\bTỬ Vi\b", "Tử vi"),
    (r"\bbe Biết\b", "biết"),
    (r"\bcua con\b", "của con"),
    (r"\bnhãn 3 chị em\b", "nhắn 3 chị em"),
    (r"\bñ công danh\b", "công danh"),
    (r"\bXem chống\b", "Xem chồng"),
    (r"\be ave\b", ""),
    (r"\bchống\b", "chồng"),
    (r"\bChống\b", "Chồng"),
    (r"\btỉnh yéu\b", "tình yêu"),
    (r"\btỉnh yều\b", "tình yêu"),
    (r"\btinh duyén\b", "tình duyên"),
    (r"\bnhần duyên\b", "nhân duyên"),
    (r"\bgia thé\b", "gia thế"),
    (r"\bGia thé\b", "Gia thế"),
    (r"\bnhư thé\b", "như thế"),
    (r"\bcô của\b", "có của"),
    (r"\bđầu Đắc loi ở dé\b", "đâu đắc lợi ở đó"),
    (r"\bở đầu Đắc lợi ở\b", "ở đâu đắc lợi ở đó"),
    (r"\bở đầu may mắn ở đó\b", "ở đâu may mắn ở đó"),
    (r"\bở đầu Bổng lộc ở đó\b", "ở đâu bổng lộc ở đó"),
    (r"\bở đầu hôn nhân ở đẩy\b", "ở đâu hôn nhân ở đấy"),
    (r"\bở đầu\b", "ở đâu"),
    (r"\bdé được\b", "dễ được"),
    (r"\bdé lấy\b", "dễ lấy"),
    (r"\bdé gặp\b", "dễ gặp"),
    (r"\bdềgäp\b", "dễ gặp"),
    (r"\bNữ Ménh\b", "Nữ mệnh"),
    (r"\bMénh\b", "Mệnh"),
    (r"\bNi mệnh\b", "Nữ mệnh"),
    (r"\bNền lam\b", "nên làm"),
    (r"\blam ăn\b", "làm ăn"),
    (r"\bthưởng có\b", "thường có"),
    (r"\btrén\b", "trên"),
    (r"\bđất dai\b", "đất đai"),
    (r"\bphụ tỉnh\b", "phụ tinh"),
    (r"\bchính tỉnh\b", "chính tinh"),
    (r"\bĐặc tinh\b", "Đặc tính"),
    (r"\bChính tỉnh\b", "Chính tinh"),
    (r"\bTỬ Vỉ\b", "Tử vi"),
    (r"\bTỪ Vỉ\b", "Tử vi"),
    (r"\bTử Vỉ\b", "Tử vi"),
    (r"\bThất Sat\b", "Thất Sát"),
    (r"\bThất Sắt\b", "Thất Sát"),
    (r"\bThiền Tướng\b", "Thiên Tướng"),
    (r"\bTuyệt đổi\b", "Tuyệt đối"),
    (r"\bhôn nhần\b", "hôn nhân"),
    (r"\btình trang\b", "tình trạng"),
    (r"\bnước mắt chan cơm\b", "nước mắt chan cơm"),
    (r"\bVảo tuổi bao nhiều\b", "vào tuổi bao nhiêu"),
    (r"\bcó thé\b", "có thể"),
    (r"\bmai mổi\b", "mai mối"),
    (r"\bsau nay\b", "sau này"),
    (r"\bthông mỉnh\b", "thông minh"),
    (r"\bThỉ cử đồ đạt\b", "thi cử đỗ đạt"),
    (r"\bđồ đạt\b", "đỗ đạt"),
    (r"\bkhông hỏa thuận\b", "không hòa thuận"),
    (r"\btruyền tỉnh\b", "truyền tinh"),
    (r"\bchuyện be hy sự\b", "chuyện hỷ sự"),
    (r"\bSự thật đắng sợ\b", "Sự thật đáng sợ"),
    (r"\bNghiệp bảo\b", "Nghiệp báo"),
    (r"\bQuy tỉnh\b", "Quý tinh"),
    (r"\bBổng lộc\b", "Bổng lộc"),
    (r"\bTải Bạch\b", "Tài Bạch"),
    (r"\bNghéo\b", "Nghèo"),
    (r"\bDự đoàn\b", "Dự đoán"),
    (r"\bXÕ hơn\b", "vợ hơn"),
    (r"\bLiệu chồng cô chung thủy\b", "Liệu chồng có chung thủy"),
    (r"\bHình ảnh Ñ bản thân khi về gia\b", "Hình ảnh bản thân khi về già"),
    (r"\blảm qu\b", "làm quý"),
    (r"\bLy do\b", "Lý do"),
    (r"\bnạp âm\b", "nạp âm"),
    (r"\bTương Lai\b", "tương lai"),
    (r"\bTương lai\b", "tương lai"),
    (r"\btải:\s*\.\s*lộc\b", "tài lộc"),
    (r"\bở cung dé\b", "ở cung đó"),
    (r"\bliều có\b", "liệu có"),
    (r"\btình k yều\b", "tình yêu"),
    (r"\bhayĐẹp\b", "hay đẹp"),
    (r"\blây 1 vải bải phú\b", "lấy 1 vài bài phú"),
    (r"\bchắc ch\b", "chắc chắn"),
    (r"\bphụ tinh cung Mệnh\b", "phụ tinh cung Mệnh"),
    (r"\bcủa h mình\b", "của mình"),
    (r"\bchính h tỉnh\b", "chính tinh"),
    (r"\bvợ s chồng\b", "vợ chồng"),
    (r"\bChồng bạn sau này là người thể nào\b", "Chồng bạn sau này là người thế nào"),
    (r"\bhôn nhân Ñ dễ gặp\b", "hôn nhân dễ gặp"),
    (r"\bÐ Bạn\b", "Bạn"),
    (r"\bCách quý: Những sao lảm qu\b", "Cách quý: Những sao làm quý"),
    (r"\bĐặc điểm của lá số 2 đời chồng\b", "Đặc điểm của lá số 2 đời chồng"),
    (r"\bLuận đoán tương lai sự nghiệp\b", "Luận đoán tương lai sự nghiệp"),
    (r"\bz k tính sổ\b", "tính số"),
    (r"\btính sổ\b", "tính số"),
    (r"\bSổ phận\b", "Số phận"),
    (r"\bchỉ tiết\b", "chi tiết"),
    (r"\bgặp j\s+\.", "gặp gì"),
    (r"\bgặp j\.", "gặp gì"),
    (r"\bTử vi Biết\b", "Tử vi biết"),
]

BOILERPLATE_PATTERNS = [
    r"\bHãy subscribe cho kênh La(?:\s+La)?\s+School\b",
    r"\bsubscribe cho kênh La(?:\s+La)?\s+School\b",
    r"\bHãy subscribe cho kênh lalaschool\b",
    r"\bHãy subscribe cho kênh Ghiền Mì Gõ\b",
    r"\bHãy subscribe cho kênh\b",
    r"\blalaschool\b",
    r"\bHãy đăng ký kênh để ủng hộ kênh mình nhé\b",
    r"\bHãy đăng ký kênh\b",
    r"\bđể ủng hộ kênh của mình nhé\b",
    r"\bĐể không bỏ lỡ những video hấp dẫn\b",
    r"\bCảm ơn (?:người nghe|các bạn) đã theo dõi(?: và hẹn gặp lại)?\b",
    r"\bHẹn gặp lại\b",
    r"\bngười nghe trong những video tiếp theo\b",
    r"\bmình nhé\b",
]

DOMAIN_TERMS = [
    "tử vi",
    "đẩu số",
    "lá số",
    "cung ",
    "sao ",
    "mệnh",
    "phu thê",
    "tử tức",
    "tài bạch",
    "quan lộc",
    "thiên ",
    "thái ",
    "vũ khúc",
    "cự môn",
    "tham lang",
    "phá quân",
    "liêm trinh",
    "thất sát",
    "hóa ",
    "tuần",
    "triệt",
]

OCR_TEXT_OVERRIDES = {
    "7410699526715051282": "\n".join(
        [
            "Bảng nạp âm 1970-1982:",
            "1970 Canh Tuất - Tự Quan Chi Cẩu - Chó nhà chùa",
            "1971 Tân Hợi - Khuyên Dưỡng Chi Trư - Lợn nuôi nhốt",
            "1972 Nhâm Tý - Sơn Thượng Chi Thử - Chuột trên núi",
            "1973 Quý Sửu - Lan Ngoại Chi Ngưu - Trâu ngoài chuồng",
            "1974 Giáp Dần - Lập Định Chi Hổ - Hổ tự lập",
            "1975 Ất Mão - Đắc Đạo Chi Thố - Thỏ đắc đạo",
            "1976 Bính Thìn - Thiên Thượng Chi Long - Rồng trên trời",
            "1977 Đinh Tỵ - Đầm Nội Chi Xà - Rắn trong đầm",
            "1978 Mậu Ngọ - Cứu Nội Chi Mã - Ngựa trong chuồng",
            "1979 Kỷ Mùi - Thảo Dã Chi Dương - Dê đồng cỏ",
            "1980 Canh Thân - Thực Quả Chi Hầu - Khỉ ăn quả",
            "1981 Tân Dậu - Long Tàng Chi Kê - Gà trong lồng",
            "1982 Nhâm Tuất - Cố Gia Chi Khuyển - Chó về nhà",
        ]
    ),
    "7436684737382468872": "Hình Phạt nhà trời",
    "7480028809857600786": "Sao này ở đâu may mắn tại đó",
    "7548736991823744264": "Mẫu phụ nữ đức hạnh khéo chiều chồng, chăm con",
    "7572497265516875028": "12 Cung khi vô chính diệu có ý nghĩa ra sao?",
    "7576878902983953685": "Thiên Phạt của bạn",
    "7585041433321622804": "Nữ mệnh càng lấy chồng sớm càng dễ chia ly",
}

OCR_LEADING_JUNK = re.compile(
    r"^(?:"
    r"[a-z]{1,3}\s+[a-z]{1,3}\s*:\s*|"
    r"(?:nã|z\s+k|đ\s+CS\s+k|đ\s+7\s+k|ễ\s+6|k:|eae\s*:|NU|XÃ|N|SỈ|HP,|b|wh\s+ale\s*:|te\s+aft|ư|B|z|x|i\s+vn|ib\s+k|Ve|Vay|Ý|vee|hes|he\s+ụ|et\s+2\s+2\s+x|re\s+3|be\s+3|bu|VaR|k|ip|Vie|te|os|j|ì\s+3|g|NN|R|of|Va|xe|wit)\s+|"
    r"vee\?\s+ras\s+\d+\s+"
    r")",
    re.IGNORECASE,
)

OCR_TRAILING_JUNK = re.compile(
    r"(?:"
    r"\s*:?\s*an|"
    r"\s+geet\s+ye|"
    r"\s+-\s+my|"
    r"\s*,?\s*x\.\s*\.-\s*ˆ|"
    r"\s+ay\s+eS|"
    r"\s+ử(?:\s+es)?|"
    r"\s+i\s+tu|"
    r"\s+[Ỹy]|"
    r"\s+ˆ(?:\s+xs|\s+ZR)?|"
    r"\s+2\s+-ˆ|"
    r"\s+Ề|"
    r"\s+ế|"
    r"\s+(?:lo|le|Ta|mm|ch|az|Ko|MA|CV|oy|SPR\s+elle|TMMMMA|w|ñ|q)|"
    r"\s+/\.\s+7ˆ\.\s+4U|"
    r"\s+B\.\s*,\s*sẽ|"
    r"\s+rial|"
    r"\s+h|"
    r"\s+\.\s+az"
    r")$",
    re.IGNORECASE,
)


def load_manifest(channel_dir: Path) -> list[dict[str, Any]]:
    manifest = channel_dir / "text_manifest.jsonl"
    return [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]


def format_date(upload_date: str | None) -> str:
    if not upload_date or len(upload_date) != 8:
        return upload_date or ""
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def topic_from_title(title: str, channel_name: str) -> str:
    topic = re.sub(r"\s+", " ", title or "").strip()
    topic = re.sub(r"^\s*Tử\s*Vi\s*Bôn\s*Ba\s*[:,-]?\s*", "", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\s*\.\.\.$", "", topic).strip()
    if len(topic) > 120:
        topic = topic[:117].rstrip(" ,.;:-") + "..."
    return topic or channel_name


def extract_body(text_path: Path) -> str:
    text = text_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("Thời lượng:"):
            start = idx + 1
            break
    body = "\n".join(lines[start:]).strip()
    body = re.sub(r"\n?Nguồn lời thoại: Whisper local.*$", "", body, flags=re.S).strip()
    body = re.sub(r"\n?Nguồn lời thoại: OCR thumbnail/poster.*$", "", body, flags=re.S).strip()
    return body


def normalize_text(text: str, source: str = "") -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[Ñï|_\\.,;: -]+", "", text).strip()
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    for _ in range(2):
        for pattern, replacement in PHRASE_FIXES:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    for wrong, right in COMMON_WORD_FIXES.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text)
    text = re.sub(r"\b(à|ờ|ừ|ừm|ạ)\b\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(a|ơ)\s+(?=[a-zà-ỹ])", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(đúng không|em hiểu không|đấy|nhá|nha)\b[,.]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(các bạn|anh em mình)\b", "người nghe", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d)\s+(\d{2})\b", r"\1\2", text)
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    text = re.sub(r"([,.?!:;])([^\s])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()
    if source == "ocr_thumbnail":
        for _ in range(3):
            text = OCR_LEADING_JUNK.sub("", text).strip()
            text = OCR_TRAILING_JUNK.sub("", text).strip()
        text = re.sub(r"[|_\\]+", " ", text)
        text = re.sub(r"\b(?:ey F|mực|ie|la|re 1|x1|lv|z1|A|Í|š|l|mo DĐ|mat at|eels|els|mm m|os m|HNMMWMAA|HNMWWMAA|TMMWWMAM|HN dV MẶ|HMWWEA|Ws|Vs|NÌ|NỈ|HP|Nee|Ne|NZ|NS|Nv|N|SỈ|NU|XÃ|eae|ae|th|ck a3|ad|ny|ial|ram rap|oe|DĐ)\b", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"^[0-9\s%+.,;:/()\-]+", "", text).strip()
        text = re.sub(r"\s+[0-9\s%+.,;:/()\-]+$", "", text).strip()
        text = re.sub(r"\s+\b(?:m|ae|th|ad|ay|ú|é|Ẳ|ủ|nl|NHI|mm|co|do|ra|bs|se|tn|ah|MM|MẶ|O|a3|P|È|y|x|ck|NLS|F|Ws|Vs)\b(?:\s+\b(?:m|ae|th|ad|ay|ú|é|Ẳ|ủ|nl|NHI|mm|co|do|ra|bs|se|tn|ah|MM|MẶ|O|a3|P|È|y|x|ck|NLS|F|Ws|Vs)\b)*\s*$", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"\s*[-–]\s*$", "", text).strip()
        text = re.sub(r"^[^A-Za-zÀ-ỹ0-9]+", "", text).strip()
        text = re.sub(r"\s+", " ", text).strip(" .,:;|-")
        for _ in range(2):
            text = OCR_LEADING_JUNK.sub("", text).strip()
            text = OCR_TRAILING_JUNK.sub("", text).strip()
    text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compact_text(text: str) -> str:
    return re.sub(r"\s*\n+\s*", " ", text).strip()


def has_research_content(text: str, source: str) -> bool:
    compact = compact_text(text)
    if source == "ocr_thumbnail":
        return len(compact) >= 8
    if len(compact) < 20:
        return False
    if source == "whisper_local":
        lowered = compact.lower()
        return len(compact) >= 100 and any(term in lowered for term in DOMAIN_TERMS)
    return True


def channel_name(rows: list[dict[str, Any]], fallback: str) -> str:
    for row in rows:
        if row.get("channel"):
            return str(row["channel"])
    return fallback


def needs_review(record: dict[str, Any]) -> bool:
    if not record["has_transcript"]:
        return False
    if record["transcript_source"] != "ocr_thumbnail":
        return False
    text = record["text"]
    if record["video_id"] in OCR_TEXT_OVERRIDES:
        return False
    if len(text) < 10:
        return True
    suspicious_patterns = [
        r"\b(?:omy|ounce|atin|eel|Buy|NLS|vee|ras|geet|rial|ale|aft|ave)\b",
        r"[ˆÿñÐ]",
        r"\.\s*,|\.\s*\.-",
        r"\b(?:lả|Thé|Phuc|Thiền|chống|tải:\s*\.)\b",
        r"^(?:he|et|wit|xe|ip|os|VaR|Vie|hes|bu|be)\b",
        r"\s(?:lo|le|Ta|mm|ch|az|Ko|MA|CV|oy|SPR|elle)$",
    ]
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in suspicious_patterns)


def write_quality_report(channel_slug: str, records: list[dict[str, Any]]) -> None:
    final_dir = TRANSCRIPT_ROOT / channel_slug / "final"
    review = [record for record in records if needs_review(record)]
    missing = [record for record in records if not record["has_transcript"]]
    lines = [
        f"# Quality report - {channel_slug}",
        "",
        "Ghi chú: `review` là OCR poster có khả năng còn lỗi dấu/ký tự rác, nên kiểm ảnh gốc nếu dùng làm dữ liệu huấn luyện hoặc trích dẫn.",
        "",
        f"- ok: {len(records) - len(review) - len(missing)}",
        f"- review: {len(review)}",
        f"- missing: {len(missing)}",
        "",
        "## Review items",
    ]
    if review:
        for record in review:
            lines.append(
                f"{record['idx']:03d}. {record['date']} | {record['video_id']} | {record['text']}"
            )
    else:
        lines.append("Không còn mục OCR bị gắn cờ review theo bộ kiểm tra hiện tại.")
    if missing:
        lines.extend(["", "## Missing items"])
        for record in missing:
            lines.append(f"{record['idx']:03d}. {record['date']} | {record['video_id']} | {record['title']}")
    (final_dir / "quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_clean_file(channel_slug: str, output_name: str | None = None) -> Path:
    channel_dir = TRANSCRIPT_ROOT / channel_slug
    final_dir = channel_dir / "final"
    final_dir.mkdir(exist_ok=True)
    rows = load_manifest(channel_dir)
    rows.sort(key=lambda row: (row.get("upload_date") or "", row.get("id") or ""))
    display_name = channel_name(rows, channel_slug)
    output_path = channel_dir / (output_name or f"{channel_slug}_research_clean.txt")

    parts = [
        f"# {display_name} - bản lời thoại sạch",
        "",
        f"Cập nhật bản sạch: {datetime.now(timezone.utc).isoformat()}",
        f"Tổng số video: {len(rows)}",
        "",
        "Ghi chú: bản này đã bỏ metadata kỹ thuật lặp, chuẩn hóa các lỗi caption phổ biến và giữ một dòng nguồn cho từng video.",
        "",
        "---",
        "",
    ]

    missing = 0
    video_records: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        text_path_value = row.get("text_path")
        text_path = ROOT / text_path_value if text_path_value else channel_dir / "text" / f"{row['id']}.txt"
        title = row.get("title") or row.get("description") or row["id"]
        topic = topic_from_title(title, display_name)
        date = format_date(row.get("upload_date"))
        duration = row.get("duration_string") or row.get("duration") or ""
        url = row.get("webpage_url") or row.get("url") or ""
        source = row.get("transcript_source") or ("subtitle" if row.get("subtitle_path") else "text")

        parts.append(f"## {idx:03d}. {date} - {topic}")
        parts.append("")
        parts.append(f"Nguồn: {url} | Thời lượng: {duration} | Transcript: {source}")
        parts.append("")
        clean_body = ""
        if text_path.exists():
            if source == "ocr_thumbnail" and row["id"] in OCR_TEXT_OVERRIDES:
                clean_body = OCR_TEXT_OVERRIDES[row["id"]]
            else:
                clean_body = normalize_text(extract_body(text_path), source)
            if has_research_content(clean_body, source):
                parts.append(clean_body)
            else:
                clean_body = ""
                parts.append("[Không nhận diện được lời thoại rõ ràng.]")
        else:
            missing += 1
            parts.append("[Chưa có lời thoại.]")
        video_records.append(
            {
                "idx": idx,
                "date": date,
                "title": topic,
                "video_id": row["id"],
                "url": url,
                "duration": duration,
                "has_transcript": bool(clean_body),
                "transcript_source": source,
                "chars": len(compact_text(clean_body)),
                "text": compact_text(clean_body),
            }
        )
        parts.append("")
        parts.append("---")
        parts.append("")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    (channel_dir / "videos.json").write_text(json.dumps(video_records, ensure_ascii=False, indent=1), encoding="utf-8")
    (final_dir / "transcripts.txt").write_text("\n".join(parts), encoding="utf-8")
    (final_dir / "videos.json").write_text(json.dumps(video_records, ensure_ascii=False, indent=1), encoding="utf-8")

    index_lines = [
        f"# {display_name} - mục lục bản sạch",
        "",
        f"Tổng số video: {len(video_records)}",
        f"Có lời thoại: {sum(1 for record in video_records if record['has_transcript'])}",
        "",
    ]
    for record in video_records:
        index_lines.append(
            f"{record['idx']:03d}. {record['date']} | {record['duration']} | {record['title']} | {record['transcript_source']} | {record['video_id']}"
        )
    (final_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    write_quality_report(channel_slug, video_records)
    print(f"Wrote {output_path} ({len(rows)} videos, missing text files: {missing})")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channels", nargs="+", help="Channel folder slug(s), e.g. huytuantuvi")
    parser.add_argument("--output-name", default=None, help="Use only with one channel")
    args = parser.parse_args()
    if args.output_name and len(args.channels) != 1:
        parser.error("--output-name can only be used with one channel")
    for channel in args.channels:
        build_clean_file(channel, args.output_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
