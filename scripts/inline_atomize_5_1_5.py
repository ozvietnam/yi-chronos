"""Inline atomize Section 5.1.5 — Thiên Đồng ở Cung Mệnh (p517-520)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

CHUNK_TEXT = """### 5.1.5. Thiên Đồng ở cung Mệnh (Thân)

Thiên Đồng ở 12 cung đều có khuyết điểm, cổ nhân nói "Thiên Đồng vào 12 cung đều là phúc trạch" — nó có thể khắc phục khuyết điểm. Ở cung Mệnh, chủ về tay trắng làm nên. Thiên Đồng chủ về tâm trạng, có sao phụ tá tụ hội chưa chắc cát lợi, dễ vì thành tựu nhỏ mà an vui không tiến thủ.

Thiên Đồng thuần túy là sao tĩnh thần, ưa được kích phát, mới có tâm thần phản chấn. Gặp sát tinh và Hóa Kỵ có lúc lại chủ về trải qua gian nguy sau mới được thu hoạch lợi ích. Gặp sát hình trùng trùng + Thiên Hình/Thiên Hư/Đại Hao/Âm Sát + Thiên Đồng Hóa Kỵ → nên đề phòng bệnh tinh thần, tâm lý mất quân bình.

Thiên Đồng-Thái Âm Tý/Ngọ: ở cung Tý tốt hơn, vì ở cung Ngọ thì Thái Âm lạc hãm, gây ảnh hưởng tâm trạng không ổn định. Gặp sát tinh → bệnh thần kinh, nội tiết mất quân bình, âm hư. Ở cung Ngọ gặp Kình Dương đồng độ → cách "Mã đầu đới tiễn". Người sinh năm Bính (Thiên Đồng Hóa Lộc) tốt hơn người sinh năm Mậu (Thái Âm Hóa Quyền). Người sinh năm Mậu phải trải qua gian nguy, người Bính sau lập nghiệp thì nhiều phúc.

Thiên Đồng-Cự Môn Sửu/Mùi: Cự Môn là ám tỉnh, ảnh hưởng sắc thái tâm trạng Thiên Đồng. Thiên Đồng Hóa Kỵ → tâm chí bạc nhược, nỗi đau khổ thầm kín. Cự Môn Hóa Kỵ → nỗi đau do mệnh tạo tự gây ra. Hóa Lộc → tài lộc đổi dào nhưng vẫn có đau khổ thầm kín. Cần Cự Môn Hóa Quyền hoặc hội Hóa Khoa/Quyền mới ổn định tâm trạng.

Thiên Đồng-Thiên Lương Dần/Thân thành cách "Cơ Nguyệt Đồng Lương", ổn định hơn Thiên Cơ-Thái Âm. Thiên Đồng (tâm trạng) + Thiên Lương (nguyên tắc) khó tránh mâu thuẫn. Hóa Lộc/Quyền → cát lợi; Hóa Khoa → sang quý thanh cao nhưng không giàu. Chủ về bất lợi trong hôn nhân, đặc biệt khi cung Phu Thê có Cự Môn Hóa Kỵ.

Thiên Đồng độc tọa Mão/Dậu, đối nhau Thái Âm. Trường hợp Thái Âm ở cung Dậu (Thiên Đồng ở Mão) thì tốt hơn. Người sinh năm Đinh, Cự Môn Hóa Kỵ ở Tài Bạch → dùng lời nói để kiếm tiền, không thì thành thị phi. Thiên Đồng ở Dậu + Thái Âm Hóa Kỵ → dễ thất chí, nhiều mặc cảm tự ti. Thiên Đồng ở Mão + Thái Âm Hóa Kỵ → chủ về thủ đoạn.

Thiên Đồng ở Thìn/Tuất, đối nhau Cự Môn. Cung Tuất + Cự Môn Hóa Kỵ kích phát → cục "phản bối" gian khổ sáng lập sự nghiệp. Thiên Đồng ở Thìn → đời thuận lợi nhưng ít "qua cơn mưa trời lại sáng" để thành sự nghiệp lớn. Cung Thìn dễ độc đoán, có thành kiến → không nên hợp tác với người khác."""


ATOMIC_DATA = [
    {
        "question": "Thiên Đồng có tính chất gì cốt lõi? Tại sao 'ưa được kích phát'?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Đồng",
            "tinh_chat": ["phúc trạch", "tĩnh thần", "tâm trạng"],
            "ua": "kích phát",
            "anh_huong": "tay trắng làm nên",
            "aspect": "tong_quan",
        },
        "from_category": "Thiên Đồng — Bản chất tĩnh thần cần kích phát",
        "from_template": "Tính chất gốc của sao X? Tại sao cần kích phát?",
        "source_quote": "Thiên Đồng ở 12 cung đều có khuyết điểm, cổ nhân nói 'Thiên Đồng vào 12 cung đều là phúc trạch' — nó có thể khắc phục khuyết điểm. Ở cung Mệnh, chủ về tay trắng làm nên. Thiên Đồng thuần túy là sao tĩnh thần, ưa được kích phát, mới có tâm thần phản chấn. Gặp sát tinh và Hóa Kỵ có lúc lại chủ về trải qua gian nguy sau mới được thu hoạch lợi ích.",
        "commentary": {
            "han_viet": "Phúc trạch = phúc đức + ơn lành (lan tỏa). Tĩnh thần = tinh thần yên tĩnh, không động. Kích phát = bị kích thích để phát ra (như ngòi nổ). Tâm thần phản chấn = trí lực dội ngược trở lại (như sóng dội).",
            "viet_thuan": "Thiên Đồng là sao 'phúc' nhưng có khuyết điểm ở mọi cung — nó tự khắc phục được. Mệnh có Thiên Đồng → 'tay trắng làm nên' (không thừa kế, tự xây). Vì Thiên Đồng quá 'tĩnh', nếu không bị kích thích → an phận, không tiến thủ. Khi gặp sát tinh hoặc Hóa Kỵ → tưởng xấu nhưng lại tốt: gian nguy buộc phải vùng dậy, sau đó mới được lợi ích thực sự.",
            "nguyen_ly": "Thiên Đồng thuộc Thủy, Dương — Thủy tĩnh (như hồ nước, không chảy). Cần 'sóng' (kích phát) mới động, sóng = sát tinh, Hóa Kỵ, biến cố. Đây là paradigm ngược với Tử Vi (cần phụ tá yên tĩnh hỗ trợ): Thiên Đồng cần SÓNG ĐẢY. Người Mệnh Thiên Đồng có cuộc đời 'hồ ao bình lặng' nếu không có gì kích — sẽ chìm trong an vui nhỏ; bị kích → bùng lên thành sự nghiệp.",
            "vi_du_doi_song": "Người Mệnh Thiên Đồng nếu sống thuận lợi từ nhỏ (cha mẹ lo đầy đủ) thường không có động lực tiến thủ — bằng lòng với mức trung bình. Nhưng nếu trải qua biến cố (mất việc, ly hôn, bệnh tật, thất bại lớn) → bùng dậy mạnh mẽ → xây sự nghiệp lớn. Lịch sử có nhiều CEO khởi nghiệp sau khi gặp 'biến cố cuộc đời'.",
            "iron_rule_warning": "'Cần kích phát' KHÔNG có nghĩa phải tìm khổ. Là paradigm nhận thức — mệnh tạo Thiên Đồng nên ý thức rằng 'an phận nhỏ' là cạm bẫy. Có thể chủ động đặt mục tiêu lớn, học tập, thử thách bản thân — kích phát chủ động thay vì chờ biến cố.",
        },
    },
    {
        "question": "Thiên Đồng gặp sát hình trùng trùng + Hóa Kỵ — cảnh báo sức khỏe gì?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Đồng",
            "sao_xau_dong_do": ["Thiên Hình", "Thiên Hư", "Đại Hao", "Âm Sát"],
            "hoa": "Thiên Đồng Hóa Kỵ",
            "canh_bao": ["bệnh tinh thần", "tâm lý mất quân bình"],
            "aspect": "canh_bao",
        },
        "from_category": "Thiên Đồng — Cảnh báo tâm thần khi sát kị nặng",
        "from_template": "Sao X + sát Y + Hóa Kỵ → cảnh báo gì?",
        "source_quote": "Thiên Đồng gặp các sao sát, hình trùng trùng, chủ về tâm thần rối rắm khó xử. Nếu gặp thêm các tạp diệu Thiên Hình, Thiên Hư, Đại Hao, Âm Sát, mà bản thân Thiên Đồng lại hóa làm sao Kỵ, thì nên để phòng bệnh tinh thần, hay tâm lý mất quân bình mà gây ra bệnh hoạn.",
        "commentary": {
            "han_viet": "Sát hình trùng trùng = nhiều sao xấu (sát + hình) đè nặng. Trùng = lập đi lập lại. Tạp diệu = sao tạp (Thiên Hình hình phạt + Thiên Hư trống rỗng + Đại Hao mất mát + Âm Sát ám sát). Tâm lý mất quân bình = mất cân bằng tâm lý.",
            "viet_thuan": "Mệnh Thiên Đồng khi gặp NHIỀU sát tinh + Thiên Hình + Thiên Hư + Đại Hao + Âm Sát + chính Thiên Đồng Hóa Kỵ → cần đề phòng bệnh tâm thần / rối loạn tâm lý nghiêm trọng. Đây là cảnh báo CỤ THỂ về sức khỏe tinh thần — không phải bệnh thể chất.",
            "nguyen_ly": "Thiên Đồng = sao tâm trạng/cảm xúc/trí nhớ. Khi bị sát tinh đè + Hóa Kỵ ám + Thiên Hư/Đại Hao rút khí + Âm Sát đe dọa → hệ tâm lý mất nền tảng. Là paradigm 'gốc khí tinh thần bị xói mòn'.",
            "vi_du_doi_song": "Người Mệnh Thiên Đồng có cấu hình xấu này có thể trải qua: trầm cảm, rối loạn lo âu, mất ngủ kinh niên, panic attack, ám ảnh, hoặc rối loạn bipolar. Cần đi khám tâm lý/tâm thần sớm khi có dấu hiệu, không phải 'chuyện tâm linh'.",
            "iron_rule_warning": "Đây là cảnh báo Y TẾ THỰC SỰ — Iron Rule #6 đặc biệt nhấn: mệnh tạo có dấu hiệu trầm cảm/lo âu thì PHẢI đi khám bác sĩ, không phải 'tu dưỡng tâm' đơn thuần. Lá số chỉ ra nguy cơ → người hành động bằng cách tìm trợ giúp chuyên khoa.",
        },
    },
    {
        "question": "Thiên Đồng-Thái Âm Tý/Ngọ — tại sao Tý tốt hơn Ngọ? Cách 'Mã đầu đới tiễn' là gì?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Đồng", "Thái Âm"],
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "uu_tien": "Tý",
            "cach_cuc": "Mã đầu đới tiễn",
            "dieu_kien": "cung Ngọ + Kình Dương đồng độ",
            "nam_sinh_uu": "Bính (Thiên Đồng Hóa Lộc)",
            "nam_sinh_kem": "Mậu (Thái Âm Hóa Quyền + Thiên Cơ Hóa Kỵ)",
            "aspect": "modifiers",
        },
        "from_category": "Đồng-Âm Tý/Ngọ — Cách Mã đầu đới tiễn + năm sinh",
        "from_template": "Combo X-Y tại chi Z — chi nào ưu hơn, cách cục đặc biệt?",
        "source_quote": "Thiên Đồng, Thái Âm đồng độ ở hai cung Tý hoặc Ngọ, ở cung Tý thì tốt hơn, vì ở cung Ngọ thì Thái Âm lạc hãm. Thiên Đồng, Thái Âm ở cung Ngọ, gặp cát tinh, nhưng có Kình Dương đồng độ, gọi là 'Mã đầu đới tiễn'. Người sinh năm Bính, Thiên Đồng Hóa Lộc, tốt hơn người sinh năm Mậu, Thái Âm Hóa Quyền (ắt cũng gặp Thiên Cơ Hóa Kỵ).",
        "commentary": {
            "han_viet": "Mã đầu đới tiễn = đầu ngựa đeo mũi tên (chữ Hán: 馬頭帶箭). Hình tượng: con ngựa đang chạy + có mũi tên đâm trên đầu → tốc độ + vũ khí → mạnh mẽ nhưng nguy hiểm. Cách cục cổ điển trong Tử Vi. Bính/Mậu = thiên can năm sinh, quyết định Tứ Hóa.",
            "viet_thuan": "Combo Thiên Đồng + Thái Âm tại Mệnh Tý hoặc Ngọ — cung Tý tốt hơn vì cung Ngọ là Hỏa, Thái Âm (Thủy) lạc hãm → cảm xúc bất ổn. Cung Ngọ + Kình Dương đồng cung → cách 'Mã đầu đới tiễn' (đầu ngựa đeo tên) — biểu tượng tốc độ + nguy hiểm. Người sinh năm Bính có Thiên Đồng Hóa Lộc → cát; người Mậu có Thái Âm Hóa Quyền KÈM Thiên Cơ Hóa Kỵ → phải gian nguy lập nghiệp.",
            "nguyen_ly": "Cung Tý (Thủy) cộng hưởng Thái Âm Thủy → mát mềm. Cung Ngọ (Hỏa) → Thái Âm Thủy bị Hỏa thiêu → khô cảm xúc. Kình Dương (Kim sát) ở Ngọ + Thiên Đồng-Thái Âm → tạo cách 'Mã đầu đới tiễn' — Kim chặt + Hỏa thiêu = tốc độ chiến + nguy hiểm. Năm Bính Hóa Lộc cho Thiên Đồng → tăng phúc; Mậu Hóa Quyền Thái Âm nhưng kèm Thiên Cơ Hóa Kỵ → quyền có nhưng bị động chuyển ám.",
            "vi_du_doi_song": "Người Mệnh Đồng-Âm Tý + cát tinh thường có cuộc sống êm ả, công việc ổn định, gia đình hài hòa. Người Mệnh Đồng-Âm Ngọ + Kình Dương cách 'Mã đầu đới tiễn' thường lập sự nghiệp nhanh + rủi ro cao — nghệ thuật, quân sự, công an, hoặc nghề có yếu tố 'tốc độ + nguy hiểm'. Người sinh Mậu phải trải qua phá sản/thất bại để lên lại.",
            "iron_rule_warning": "Cách 'Mã đầu đới tiễn' không phải định mệnh xấu — là cách quý nếu hành đúng ngạch (võ nghiệp, ngành có tốc độ). Phải xem thêm Tứ Hóa năm sinh + sao phụ tá để định cát/hung cuối cùng.",
        },
    },
    {
        "question": "Thiên Đồng-Cự Môn Sửu/Mùi — tại sao có 'đau khổ thầm kín'? Cần Hóa gì để giải?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Đồng", "Cự Môn"],
            "cung": "Mệnh",
            "chi": ["Sửu", "Mùi"],
            "tinh_chat_Cu_Mon": "ám tinh",
            "anh_huong": "đau khổ thầm kín",
            "Thien_Dong_Hoa_Ky": "tâm chí bạc nhược",
            "Cu_Mon_Hoa_Ky": "nỗi đau do mệnh tạo tự gây",
            "Hoa_Loc": "tài lộc nhưng vẫn đau khổ thầm kín",
            "can_co_de_giai": ["Cự Môn Hóa Quyền", "Hóa Khoa", "Hóa Quyền"],
            "aspect": "modifiers",
        },
        "from_category": "Đồng-Cự Sửu/Mùi — Đau khổ thầm kín",
        "from_template": "Combo X-Y tại chi Z — nỗi khổ + cách giải?",
        "source_quote": "Thiên Đồng, Cự Môn ở hai cung Sửu hoặc Mùi, Cự Môn là ám tỉnh, ảnh hưởng đến sắc thái tâm trạng của Thiên Đồng. Thiên Đồng Hóa Kỵ → tâm chí bạc nhược. Cự Môn Hóa Kỵ sẽ chủ về nỗi đau khổ thầm kín trong đời người thường là do bản thân mệnh tạo chủ động gây ra. Hóa Lộc thì tài lộc đổi dào, nhưng vẫn không tránh được có nỗi đau khổ thầm kín. Cần phải Cự Môn Hóa Quyền, hoặc hội các sao Hóa Khoa, Hóa Quyền mới chủ về tâm trạng ổn định.",
        "commentary": {
            "han_viet": "Ám tỉnh 暗星 = sao tối (ám muội, lời ra tiếng vào, ẩn dấu). Tâm chí bạc nhược = ý chí mỏng manh. Đau khổ thầm kín = nỗi đau giữ trong lòng, không nói ra. Tự gây = do chính mệnh tạo tạo ra.",
            "viet_thuan": "Combo Thiên Đồng (tâm trạng) + Cự Môn (ám tinh) tại Mệnh Sửu/Mùi → cấu hình mang 'đau khổ thầm kín' bẩm sinh. Nếu Thiên Đồng Hóa Kỵ → ý chí mỏng, dễ chán nản. Nếu Cự Môn Hóa Kỵ → nỗi đau do chính mệnh tạo tự tạo ra (qua quyết định sai, lời nói tổn thương). Có Hóa Lộc tuy giàu nhưng nội tâm vẫn buồn. Phải cần Cự Môn Hóa Quyền hoặc hội Hóa Khoa/Quyền → tâm trạng ổn định.",
            "nguyen_ly": "Thiên Đồng Thủy + Cự Môn Thủy/Mộc (đa hành). Sửu/Mùi Thổ → khắc Thủy → cả 2 sao bị 'tiết'. Cự Môn 'ám' (vô hình) đè nặng Thiên Đồng (tâm trạng) → tạo 'đau thầm'. Hóa Quyền/Khoa cho Cự Môn → biến ám thành 'nội lực kiểm soát' → ổn.",
            "vi_du_doi_song": "Người Mệnh Đồng-Cự Sửu/Mùi thường có 'nỗi buồn không tên' từ nhỏ — không lý do rõ vẫn cảm thấy thiếu, lạc lõng, hay tự ti dù người ngoài thấy ổn. Nếu có Cự Môn Hóa Kỵ → quyết định sai làm tổn thương mình + người thân, sau hối nhưng đã muộn. Nếu Cự Môn Hóa Quyền → biết sử dụng tài ăn nói tốt (luật sư, MC, tư vấn) → có vị trí, ổn tâm.",
            "iron_rule_warning": "'Đau khổ thầm kín' KHÔNG phải định mệnh u sầu cả đời. Là xu hướng bẩm sinh — mệnh tạo nhận thức + chủ động chăm sóc tâm lý (thiền, trị liệu tâm lý, kết nối cộng đồng) hoàn toàn có thể vượt qua. Iron Rule #6.",
        },
    },
    {
        "question": "Thiên Đồng-Thiên Lương Dần/Thân khác Thiên Cơ-Thái Âm thế nào? Tại sao bất lợi hôn nhân?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Đồng", "Thiên Lương"],
            "cung": "Mệnh",
            "chi": ["Dần", "Thân"],
            "cach_cuc": "Cơ Nguyệt Đồng Lương (chính cách)",
            "uu_hon_voi": "Thiên Cơ-Thái Âm (cùng cách Cơ-Nguyệt-Đồng-Lương)",
            "mau_thuan_noi_bo": ["Thiên Đồng (tâm trạng)", "Thiên Lương (nguyên tắc)"],
            "canh_bao_hon_nhan": "bất lợi (đặc biệt khi Phu Thê Cự Môn Hóa Kỵ)",
            "aspect": "modifiers",
        },
        "from_category": "Đồng-Lương Dần/Thân — Cách chính + bất lợi hôn nhân",
        "from_template": "Combo X-Y chi Z — cách cục + ưu nhược?",
        "source_quote": "Thiên Đồng, Thiên Lương đồng độ ở hai cung Dần hoặc Thân, thành cách 'Cơ Nguyệt Đồng Lương'. Kết cấu này ổn định hơn Thiên Cơ, Thái Âm thủ mệnh thành cách 'Cơ Nguyệt Đồng Lương'. Thiên Đồng chủ về tâm trạng, Thiên Lương chủ về nguyên tắc, hai sao đồng cung khó tránh mâu thuẫn, xung đột. Thiên Đồng, Thiên Lương ở hai cung Dần hoặc Thân, chủ về bất lợi trong hôn nhân, cung phu thê là Cự Môn Hóa Kỵ thì càng đúng.",
        "commentary": {
            "han_viet": "Cơ Nguyệt Đồng Lương = 4 sao Thiên Cơ + Thái Âm + Thiên Đồng + Thiên Lương (chính cách Tử Vi). Khi Mệnh có 2 trong 4 sao này đồng cung → 'thành cách'. Ổn định hơn = bền hơn về vận trình.",
            "viet_thuan": "Combo Thiên Đồng + Thiên Lương tại Dần/Thân là chính cách 'Cơ Nguyệt Đồng Lương' (cách công chức/ổn định). KHÁC với Thiên Cơ-Thái Âm cùng cách — Đồng-Lương ổn định hơn nhiều. NHƯNG: Thiên Đồng (cảm xúc/tâm trạng) + Thiên Lương (nguyên tắc/cô độc) là 2 sao khác bản chất → khó tránh mâu thuẫn nội tâm. Hôn nhân bất lợi, đặc biệt khi cung Phu Thê có Cự Môn Hóa Kỵ.",
            "nguyen_ly": "Thiên Đồng Thủy + Thiên Lương Mộc Thổ → Thủy sinh Mộc, Mộc khắc Thổ. Nội bộ tương khắc-sinh phức tạp. Tâm trạng (Thiên Đồng) muốn linh hoạt vs Nguyên tắc (Thiên Lương) muốn cố định → xung đột. Hôn nhân cần linh hoạt + cam kết — combo này khó cân bằng cả 2.",
            "vi_du_doi_song": "Người Mệnh Đồng-Lương Dần/Thân thường làm tốt công chức/giáo viên/nhà nghiên cứu (ổn định + có nguyên tắc) NHƯNG hôn nhân thường có mâu thuẫn lớn — vợ/chồng cảm thấy 'người này khô nguyên tắc' (nhìn từ tình cảm) hoặc 'người này quá emotional' (nhìn từ nguyên tắc). Dễ ly thân, ly hôn, hoặc sống xa nhau dù còn quan hệ.",
            "iron_rule_warning": "'Bất lợi hôn nhân' = xu hướng, KHÔNG phải định mệnh ly hôn. Mệnh tạo Đồng-Lương ý thức trước có thể chọn bạn đời tương thích (người không quá emotional cũng không quá rigid) + đầu tư communication → tránh được.",
        },
    },
    {
        "question": "Thiên Đồng độc tọa Mão/Dậu khác nhau ra sao? Cảnh báo Thái Âm Hóa Kỵ đối cung?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Đồng",
            "cung": "Mệnh",
            "chi": ["Mão", "Dậu"],
            "doi_cung": "Thái Âm",
            "uu_tien": "Dậu (Thái Âm ở Dậu tốt hơn)",
            "Dau_voi_Thai_Am_Hoa_Ky": "thất chí, mặc cảm tự ti",
            "Mao_voi_Thai_Am_Hoa_Ky": "thủ đoạn",
            "Dinh_nam": "Cự Môn Hóa Kỵ Tài Bạch → dùng lời nói kiếm tiền",
            "aspect": "modifiers",
        },
        "from_category": "Thiên Đồng Mão/Dậu — Phân biệt cát/hung",
        "from_template": "Sao X độc tọa chi Y vs chi Z — đối cung khác nhau?",
        "source_quote": "Thiên Đồng độc tọa ở hai cung Mão hoặc Dậu, đối nhau với Thái Âm. Trường hợp Thái Âm ở cung Dậu thì tốt hơn. Thiên Đồng ở cung Dậu, nếu đối cung là Thái Âm Hóa Kỵ, thì dễ thất chí, hoặc nhiều mặc cảm tự ti. Thiên Đồng ở cung Mão, đối cung là Thái Âm Hóa Kỵ, sẽ chủ về thủ đoạn.",
        "commentary": {
            "han_viet": "Đối nhau = ở 2 cung đối diện trên lá số. Thất chí = mất ý chí (không còn động lực). Mặc cảm tự ti = cảm giác kém cỏi so với người khác. Thủ đoạn = dùng mưu mẹo (xấu nghĩa).",
            "viet_thuan": "Mệnh Thiên Đồng tại Mão hoặc Dậu, đối cung luôn là Thái Âm. Khi Thái Âm ở Dậu (Thiên Đồng ở Mão) → tốt hơn vì Thái Âm Dậu nhập miếu. Nếu đối cung Thái Âm Hóa Kỵ: Thiên Đồng ở Dậu → thất chí, mặc cảm tự ti (hướng vào trong). Thiên Đồng ở Mão → thủ đoạn (hướng ra ngoài, dùng mưu). Năm Đinh có Cự Môn Hóa Kỵ ở Tài Bạch → kiếm tiền bằng lời nói (luật sư, môi giới, MC), không thì sẽ vướng thị phi.",
            "nguyen_ly": "Mão Mộc + Thiên Đồng Thủy → Thủy sinh Mộc (động cảm xúc + biến tư duy). Dậu Kim + Thiên Đồng Thủy → Kim sinh Thủy (vững vàng). Đối cung Thái Âm Hóa Kỵ rút khí cảm xúc → Mão xuất ra thành 'thủ đoạn' (Mộc động kim mưu); Dậu rút vào thành 'thất chí' (Kim Thủy trầm).",
            "vi_du_doi_song": "Người Mệnh Thiên Đồng Mão + Thái Âm Hóa Kỵ đối thường thông minh nhưng dùng trí cho mục đích không sạch (cãi quyền lợi, manipulate). Người Mệnh Thiên Đồng Dậu + Thái Âm Hóa Kỵ → hay buồn vô cớ, so sánh mình với người khác, nghĩ mình kém. Năm Đinh + Cự Hóa Kỵ Tài → thành luật sư/môi giới thành công, hoặc vướng thị phi nếu không nắn tài năng đúng hướng.",
            "iron_rule_warning": "'Thủ đoạn' và 'mặc cảm' là xu hướng tâm lý — không phải định mệnh. Mệnh tạo nhận thức được có thể chủ động tu dưỡng: Mão → dùng trí cho việc lành, không manipulate; Dậu → tự yêu mình, không so sánh với người khác.",
        },
    },
    {
        "question": "Thiên Đồng ở Thìn vs Tuất khác nhau ra sao? Cách 'phản bối' là gì?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Đồng",
            "cung": "Mệnh",
            "chi": ["Thìn", "Tuất"],
            "doi_cung": "Cự Môn",
            "Tuat_voi_Cu_Mon_Hoa_Ky": "cục 'phản bối' — gian khổ sáng lập sự nghiệp",
            "Thin_thuan_loi": "đời thuận lợi nhưng ít 'qua cơn mưa trời lại sáng' để thành sự nghiệp lớn",
            "Thin_canh_bao": "dễ độc đoán, có thành kiến → không nên hợp tác",
            "aspect": "modifiers",
        },
        "from_category": "Thiên Đồng Thìn/Tuất — Phản bối + độc đoán",
        "from_template": "Sao X chi Y vs chi Z — cách cục đặc biệt + cảnh báo?",
        "source_quote": "Thiên Đồng ở hai cung Thìn hoặc Tuất, đối nhau với Cự Môn, cũng có đặc tính của 'Thiên Đồng, Cự Môn'. Thiên Đồng ở cung Tuất ưa đối cung là Cự Môn Hóa Kỵ kích phát, gọi là cục 'phản bối', chủ về gian khổ sáng lập sự nghiệp. Thiên Đồng ở cung Thìn, đối cung là Cự Môn Hóa Kỵ, cho nên không thành cục 'phản bối', đời người khá thuận lợi toại ý, nhưng lại ít tính chất 'qua cơn mưa trời lại sáng' để thành sự nghiệp lớn. Thiên Đồng ở cung Thìn, thông thường dễ độc đoán, có thành kiến.",
        "commentary": {
            "han_viet": "Phản bối 反背 = quay lưng + đối lập (chữ Hán). Trong Tử Vi, cách 'phản bối' = cấu hình tưởng xấu nhưng lại tốt (kích phát đảo ngược). 'Qua cơn mưa trời lại sáng' = trải qua gian khó thành công. Độc đoán = tự quyết một mình, không nghe ai. Thành kiến = định kiến cố thủ.",
            "viet_thuan": "Combo Thiên Đồng + Cự Môn đối cung tại Thìn/Tuất khác nhau rõ: Cung Tuất + Cự Môn Hóa Kỵ đối cung → cách 'phản bối' (xấu hóa tốt) → gian khổ sáng lập sự nghiệp lớn. Cung Thìn + Cự Môn Hóa Kỵ đối cung → KHÔNG thành cách phản bối → đời thuận lợi nhưng KHÔNG có biến cố để bùng dậy → khó làm việc lớn. Thiên Đồng Thìn còn có khuyết điểm độc đoán, thành kiến → không nên hợp tác với người khác.",
            "nguyen_ly": "Tuất Thổ khô + Cự Môn Hóa Kỵ đối → khí xấu kích phát Thiên Đồng Thủy tĩnh → 'phản bối' = nước trong đất khô bùng lên thành suối nguồn. Thìn Thổ ẩm + Cự Môn Hóa Kỵ đối → không 'khô' để kích, chỉ là 'ẩm' tiếp tục → êm nhưng không bùng. Đây là nguyên lý kích phát Thiên Đồng cần 'điều kiện đối lập đủ mạnh'.",
            "vi_du_doi_song": "Người Mệnh Thiên Đồng Tuất + Cự Hóa Kỵ đối thường có cuộc đời gian khổ tuổi trẻ (bố mẹ ly hôn, gia đình nghèo, vướng tù tội) nhưng sau 30 vùng dậy thành đạt lớn (founder doanh nghiệp, leader). Người Mệnh Thiên Đồng Thìn + Cự Hóa Kỵ → đời êm ấm nhưng cảm thấy 'không có dấu ấn lớn', sự nghiệp ở mức trung bình. Thiên Đồng Thìn thêm tính độc đoán → khó hợp tác → nên làm việc cá nhân (writer, artist, consultant).",
            "iron_rule_warning": "'Phản bối' không phải định mệnh — là cơ hội năng lượng. Mệnh tạo Thiên Đồng Tuất + biến cố lớn phải CHỦ ĐỘNG bùng dậy, không cam chịu. Thiên Đồng Thìn thuận lợi cũng không phải xấu — có thể chọn cuộc sống bình yên thay vì sự nghiệp lớn.",
        },
    },
    {
        "question": "Thiên Đồng-Cự Môn Sửu/Mùi với Đà La đồng độ — phát mạnh khi nào?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Đồng", "Cự Môn"],
            "cung": "Mệnh",
            "chi": ["Sửu", "Mùi"],
            "sao_dong_do": "Đà La",
            "anh_huong": "buồn phiền, phải trải sóng gió lớn mới phát mạnh",
            "nam_uu": "đến cung hạn Thất Sát",
            "nu_uu": "đến cung hạn Liêm Trinh-Thiên Phủ",
            "aspect": "timing_dai_van",
        },
        "from_category": "Đồng-Cự + Đà La — Vận phát theo giới tính",
        "from_template": "Combo X-Y + sát Z → vận phát khi nào theo giới tính?",
        "source_quote": "Hễ 'Thiên Đồng, Cự Môn' đồng độ với Đà La, là chủ về buồn phiền, đời người ắt phải trải qua sóng gió lớn mới phát mạnh. Về vận phát mạnh, nam mệnh nên đến cung hạn Thất Sát, nữ mệnh nên đến cung hạn 'Liêm Trinh, Thiên Phủ'.",
        "commentary": {
            "han_viet": "Đà La 陀羅 = 1 trong 4 sát tinh (Kình, Đà, Hỏa, Linh) — tính chất 'kéo lê, dai dẳng' (như đá nặng kéo). Buồn phiền = lo âu kéo dài. Sóng gió lớn = biến cố lớn. Cung hạn = cung đại vận/lưu niên.",
            "viet_thuan": "Combo Đồng-Cự tại Sửu/Mùi + Đà La đồng cung → cuộc đời buồn phiền kéo dài, phải trải sóng gió lớn mới bùng phát. Tuy nhiên vận phát khác theo giới: NAM → đến cung hạn Thất Sát (sao võ) thì phát mạnh; NỮ → đến cung hạn Liêm Trinh-Thiên Phủ (kho tài + sang quý) thì phát.",
            "nguyen_ly": "Đà La 'kéo dai' áp lên Đồng-Cự đã sẵn 'đau thầm' → tăng đau dài. Nhưng năng lượng tích tụ lâu cần cú nổ. Cú nổ khác theo giới: Nam cần sát khí (Thất Sát = võ chiến) để chuyển đau thành lực; Nữ cần kho ấm (Liêm-Phủ = tài + quý) để chuyển đau thành ổn định.",
            "vi_du_doi_song": "Người Đồng-Cự Sửu/Mùi + Đà La nam thường trải qua sự nghiệp lận đận đến 30-40, sau đó vào đại vận Thất Sát → khởi nghiệp/CEO/chiến binh ngành đó bùng phát. Nữ thường trải qua hôn nhân/tài chính khó khăn đến 30-40, sau đó vào đại vận Liêm-Phủ → có vị trí cao quý + tài chính ổn.",
            "iron_rule_warning": "'Phát mạnh' là cơ hội năng lượng — không phải đảm bảo thành công. Cần kết hợp với hành động cụ thể: nam sẵn sàng 'chiến' khi vận đến; nữ sẵn sàng 'nhận trách nhiệm cao' khi vận đến.",
        },
    },
]


def persist():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    book = "trung-chau-tu-vi-dau-so-2"

    for page in [517, 518, 519, 520]:
        conn.execute(
            "UPDATE chunks_v2 SET section_id='5.1.5' WHERE book_corpus_id=? AND page_start=?",
            (book, page),
        )

    existing = conn.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=517",
        (book,),
    ).fetchone()
    chunk_id = existing[0] if existing else None
    if chunk_id:
        conn.execute("UPDATE chunks_v2 SET text=?, section_id=? WHERE chunk_id=?",
                     (CHUNK_TEXT, "5.1.5", chunk_id))
        conn.execute("DELETE FROM atom_commentaries WHERE atom_id IN (SELECT atom_id FROM atomic_questions WHERE chunk_id=?)", (chunk_id,))
        conn.execute("DELETE FROM atomic_questions WHERE chunk_id=?", (chunk_id,))
        conn.execute("DELETE FROM chunk_classifications WHERE chunk_id=?", (chunk_id,))
        print(f"📦 Cleaned chunk_id={chunk_id} for 5.1.5")
    conn.commit()

    cur = conn.execute(
        """INSERT INTO chunk_classifications
           (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
            format_style, knowledge_categories_json, extracted_by, confidence)
           VALUES (?, 1, 0, 1, 1, 1, 'nguyen_ly', ?, 'claude-inline', 0.95)""",
        (chunk_id, json.dumps([
            "Thiên Đồng — bản chất tĩnh thần cần kích phát",
            "Thiên Đồng — cảnh báo bệnh tâm thần",
            "Đồng-Âm Tý/Ngọ — Mã đầu đới tiễn",
            "Đồng-Cự Sửu/Mùi — đau khổ thầm kín",
            "Đồng-Lương Dần/Thân — cách chính + bất lợi hôn",
            "Thiên Đồng Mão/Dậu — thủ đoạn / mặc cảm",
            "Thiên Đồng Thìn/Tuất — cách phản bối",
            "Đồng-Cự + Đà La — vận phát theo giới tính",
        ], ensure_ascii=False)),
    )
    cc_id = int(cur.lastrowid)
    conn.commit()

    n = 0
    for atom_data in ATOMIC_DATA:
        cur = conn.execute(
            """INSERT INTO atomic_questions
               (chunk_id, cc_id, question_text, question_lang, from_category, from_template,
                subject_identifiers, source_quote, confidence, founder_verified,
                extracted_by, section_id)
               VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, 0.95, 0, 'claude-inline', '5.1.5')""",
            (
                chunk_id, cc_id,
                atom_data["question"],
                atom_data["from_category"],
                atom_data["from_template"],
                json.dumps(atom_data["subject_identifiers"], ensure_ascii=False),
                atom_data["source_quote"],
            ),
        )
        atom_id = int(cur.lastrowid)
        n += 1

        c = atom_data["commentary"]
        conn.execute(
            """INSERT INTO atom_commentaries
               (atom_id, han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song,
                iron_rule_warning, extracted_by, confidence, founder_verified)
               VALUES (?, ?, ?, ?, ?, ?, 'claude-inline', 0.95, 0)""",
            (atom_id, c.get("han_viet"), c.get("viet_thuan"), c.get("nguyen_ly"),
             c.get("vi_du_doi_song"), c.get("iron_rule_warning")),
        )

    conn.execute("UPDATE chunks_v2 SET atom_q_str=? WHERE chunk_id=?",
                 ("\n".join(a["question"] for a in ATOMIC_DATA), chunk_id))
    conn.commit()
    conn.execute("INSERT INTO atomic_questions_fts(atomic_questions_fts) VALUES('rebuild')")
    conn.commit()

    print(f"✅ {n} atoms + {n} commentaries inserted for 5.1.5")
    n_total = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE section_id='5.1.5'").fetchone()[0]
    print(f"📊 DB section 5.1.5: {n_total} atoms")
    conn.close()


if __name__ == "__main__":
    print("═" * 70)
    print("EM TỰ XỬ LÝ Section 5.1.5 — Thiên Đồng ở Cung Mệnh")
    print("8 atoms (bản chất, cảnh báo, Đồng-Âm, Đồng-Cự, Đồng-Lương, Mão/Dậu, Thìn/Tuất, Đà La)")
    print("═" * 70)
    persist()
