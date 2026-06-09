"""Inline atomize Section 5.1.2 — Thiên Cơ ở Cung Mệnh (p506-509).

Em (Claude) tự xử lý. 6 variants Thiên Cơ × Cung Mệnh.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

# Combine chunks 506-509 thành 1 chunk lớn (em đọc nguyên section)
CHUNK_TEXT = """### 5.1.2. Thiên Cơ ở cung Mệnh (Thân)

Thiên Cơ độc tọa ở hai cung Tý hoặc Ngọ, rất ưa Hóa Quyền. Thiên Cơ Hóa Quyền lại ưu hơn Cự Môn Hóa Quyền. Hóa Quyền thì vững vàng, cho nên tốt hơn Hóa Lộc, Hóa Lộc phấn nhiễu nóng nảy, trôi nổi bất định.

Thiên Cơ độc tọa hai cung Tý hoặc Ngọ, nếu đổi cung là Cự Môn Hóa Quyền, ở thời hiện đại có thể chỉ là người phân phối, nhà phát hành trong giới làm ăn kinh doanh, không chủ về là người vạch kế sách hay quản lý. Thiên Cơ Hóa Quyền, thì có thể là người vạch kế sách ở phía sau.

Thiên Cơ độc tọa hai cung Tý hoặc Ngọ rất kỵ đồng độ với Hỏa Tinh, Linh Tinh; chủ về lúc bé đã rời xa cha mẹ, hoặc cảnh ngộ của cha mẹ bị biến động thay đổi, ảnh hưởng đến phúc ấm của mệnh tạo lúc còn bé.

Thiên Cơ độc tọa thủ mệnh ở hai cung Tý hoặc Ngọ, Thái Âm chủ cung thân, chủ về mệnh tạo ngày đêm bôn ba bận rộn, thường làm việc ban đêm, hoặc đến tối vẫn cần phải suy nghĩ kế hoạch.

Thiên Cơ, Thái Âm đồng độ ở hai cung Dần hoặc Thân là chính cách "Cơ Nguyệt Đồng Lương". Ở cung Thân, Thiên Lương ở cung Tý ưu hơn Thiên Lương ở cung Ngọ, cho nên oán trách, thị phi ít hơn.

Thiên Cơ, Cự Môn đồng độ hai cung Mão hoặc Dậu, cần phải gặp sao lộc mới cát; rất kỵ có Hỏa Tinh, Linh Tinh cùng bay đến, chủ về khinh bạc, phóng đãng, thiếu trang trọng, phá phách.

Nam mệnh Cự Môn Hóa Lộc: Chủ về chồng già lấy vợ trẻ; Thiên Cơ Hóa Lộc: Thì phần nhiều là tái hôn. Nữ mệnh Cự Môn Hóa Lộc: Cũng nên lấy người lớn tuổi; Thiên Cơ Hóa Lộc: Phần nhiều đều có khiếm khuyết đáng tiếc trong hôn nhân.

Thiên Cơ, Thiên Lương đồng độ hai cung Thìn hoặc Tuất, chủ về có tay nghề, ở thời hiện đại cũng có thể định là nhân tài chuyên nghiệp; không thích hợp làm việc trong chính giới hay kinh doanh buôn bán. Là thiên cách "Cơ Nguyệt Đồng Lương", cần phải dùng miệng lưỡi để kiếm tiền.

Thiên Cơ ở hai cung Tị hoặc Hợi, cuộc đời gặp nhiều rắc rối khó xử về tình cảm. Nữ mệnh không nên Hóa Kỵ hoặc có sao kỵ hội chiếu; gặp thêm sát tinh, chủ về hình khắc, sinh li, hoặc làm nhị phòng, tì thiếp. Gặp các sao phụ, tá cát, thì có thể phú quý, thích hợp làm những công việc mang tính phục vụ công chúng, đặc biệt về truyền thông hay thông tấn, báo chí."""


ATOMIC_DATA = [
    {
        "question": "Thiên Cơ độc tọa Tý/Ngọ ưa Hóa Quyền hay Hóa Lộc hơn? Tại sao?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Cơ",
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "variant": "Thiên Cơ độc tọa",
            "hoa_uu_tien": "Hóa Quyền",
            "aspect": "modifiers",
        },
        "from_category": "Thiên Cơ Mệnh — Hóa Quyền vs Hóa Lộc",
        "from_template": "Sao X tại cung Y ưa Hóa nào hơn?",
        "source_quote": "Thiên Cơ độc tọa ở hai cung Tý hoặc Ngọ, rất ưa Hóa Quyền. Thiên Cơ Hóa Quyền lại ưu hơn Cự Môn Hóa Quyền. Hóa Quyền thì vững vàng, cho nên tốt hơn Hóa Lộc, Hóa Lộc phấn nhiễu nóng nảy, trôi nổi bất định.",
        "commentary": {
            "han_viet": "Hóa Quyền = sao biến hóa thành quyền lực, tính chất 'vững vàng'; Hóa Lộc = sao biến hóa thành tài lộc, tính chất 'động'. Phấn nhiễu = ồn ào, nóng nảy. Trôi nổi bất định = không có chỗ đứng ổn.",
            "viet_thuan": "Thiên Cơ là sao thông minh, hay tính toán, vốn đã 'động'. Khi gặp Hóa Quyền, năng lượng được kiềm chế, vững vàng → tốt hơn. Khi gặp Hóa Lộc, năng lượng bị thêm 'động' nữa → thành quá nhiều ý tưởng, nóng nảy, không ổn. Đặc biệt Thiên Cơ Hóa Quyền tốt hơn cả Cự Môn Hóa Quyền — vì Thiên Cơ là 'mưu thần', cần Quyền để biến mưu thành quyết.",
            "nguyen_ly": "Thiên Cơ thuộc Mộc, Âm — bản chất 'động chuyển' (mộc sinh trưởng, biến hóa). Hóa Quyền thuộc Mộc cương, có khả năng định hướng. Mộc gặp Mộc cương → vững. Hóa Lộc thuộc Thổ động (động sinh tài) — Mộc gặp Thổ động → càng động, mất ổn định. Đây là nguyên lý ngũ hành tương quan: cần Bổ Khuyết, không cần Tăng Cường cái đã có.",
            "vi_du_doi_song": "Người Mệnh Thiên Cơ Tý/Ngọ có tư duy nhanh, hay nghĩ kế. Nếu có thêm Hóa Quyền — họ có khả năng kiên định với kế hoạch, đưa ý tưởng thành hành động cụ thể. Nếu chỉ có Hóa Lộc — họ có nhiều ý tưởng nhưng dễ bỏ dở giữa chừng, đi từ dự án này sang dự án khác.",
            "iron_rule_warning": "'Vững vàng' không có nghĩa chắc chắn thành công. Đây là xu hướng tính cách + cách năng lượng vận hành. Mệnh tạo vẫn có thể chủ động chọn hành động (Xu Cát Tị Hung).",
        },
    },
    {
        "question": "Thiên Cơ độc tọa Tý/Ngọ với Cự Môn Hóa Quyền đối cung có nghĩa nghề nghiệp gì?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Cơ",
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "doi_cung_sao": "Cự Môn",
            "hoa_doi_cung": "Hóa Quyền",
            "aspect": "dinh_huong",
        },
        "from_category": "Thiên Cơ Mệnh — Định hướng nghề (vai trò sau-trước)",
        "from_template": "Sao X tại Mệnh với sao Y đối cung Hóa Z → nghề gì?",
        "source_quote": "Thiên Cơ độc tọa hai cung Tý hoặc Ngọ, nếu đổi cung là Cự Môn Hóa Quyền, ở thời hiện đại có thể chỉ là người phân phối, nhà phát hành trong giới làm ăn kinh doanh, không chủ về là người vạch kế sách hay quản lý. Thiên Cơ Hóa Quyền, thì có thể là người vạch kế sách ở phía sau.",
        "commentary": {
            "han_viet": "Vạch kế sách = lập chiến lược (strategist); phân phối/phát hành = distribute (operational). Một trong một ngoài = một bên trong/sau, một bên ngoài/trước.",
            "viet_thuan": "Mệnh Thiên Cơ Tý/Ngọ, nếu Cự Môn Hóa Quyền ở đối cung → mệnh tạo thiên về 'người phân phối, phát hành' — vận hành phía trước, hoạt động trong giới kinh doanh nhưng KHÔNG phải người ra chiến lược. Nếu chính Thiên Cơ ở Mệnh được Hóa Quyền → mệnh tạo trở thành 'người vạch kế sách ở phía sau' — strategist không xuất hiện trên front line.",
            "nguyen_ly": "Mệnh là 'mình', Đối cung là 'thế giới'. Hóa Quyền ở đâu = quyền lực biểu hiện ở đó. Khi Thiên Cơ (Mệnh) chỉ là không Hóa, mà Cự Môn (Đối) Hóa Quyền → quyền lực ở thế giới bên ngoài, mệnh tạo bị 'kéo ra' làm front-line. Khi Thiên Cơ Hóa Quyền → quyền lực ở chính mình, mệnh tạo giữ vị thế back-office strategist.",
            "vi_du_doi_song": "Người Thiên Cơ Tý/Ngọ + Cự Môn Hóa Quyền đối cung thường làm đại lý phân phối hàng hóa, sales chính trong công ty — gần khách hàng, gặp người trực tiếp. Người Thiên Cơ Hóa Quyền tại Mệnh thường làm chiến lược marketing, R&D, lập kế hoạch — ít gặp khách, làm việc với data và ý tưởng.",
            "iron_rule_warning": "Đây là xu hướng vai trò, không phải định mệnh. Mệnh tạo có thể chọn 'đẩy ra' hoặc 'rút về' tùy điều kiện sống.",
        },
    },
    {
        "question": "Thiên Cơ độc tọa Tý/Ngọ kỵ Hỏa Tinh/Linh Tinh đồng độ ra sao?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Cơ",
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "sao_ky_dong_do": ["Hỏa Tinh", "Linh Tinh"],
            "aspect": "modifiers",
            "anh_huong": "phúc ấm lúc bé",
        },
        "from_category": "Thiên Cơ Mệnh — Kỵ Hỏa-Linh đồng độ",
        "from_template": "Sao X tại Mệnh + sát tinh Y đồng độ → ảnh hưởng gì?",
        "source_quote": "Thiên Cơ độc tọa hai cung Tý hoặc Ngọ rất kỵ đồng độ với Hỏa Tinh, Linh Tinh; chủ về lúc bé đã rời xa cha mẹ, hoặc cảnh ngộ của cha mẹ bị biến động thay đổi, ảnh hưởng đến phúc ấm của mệnh tạo lúc còn bé.",
        "commentary": {
            "han_viet": "Hỏa Tinh, Linh Tinh = 2 sát tinh đầu trong 'Tứ sát' (Kình, Đà, Hỏa, Linh). Hỏa = bùng nổ, Linh = âm hỏa âm thầm. Phúc ấm = ấm cúng của gia đình.",
            "viet_thuan": "Khi Mệnh có Thiên Cơ tại Tý/Ngọ và gặp Hỏa Tinh hoặc Linh Tinh cùng cung → tuổi thơ mệnh tạo thường có sự cố lớn trong gia đình: hoặc cha mẹ bị biến động (ly hôn, mất việc, bệnh tật), hoặc bản thân phải sống xa cha mẹ sớm (đi học xa, được nuôi bởi ông bà). Ảnh hưởng kéo dài, làm 'phúc ấm' không trọn.",
            "nguyen_ly": "Thiên Cơ Mộc Âm vốn cần được nuôi dưỡng ổn định. Hỏa-Linh = sát tinh Hỏa khắc Mộc. Mộc bé bị Hỏa thiêu → 'mầm cây gặp nắng gắt'. Mầm cây = phúc ấm; Hỏa = biến động ngoại lai. Tuổi thơ là giai đoạn 'mầm cây' phát triển, gặp khắc tinh → tổn thương sớm.",
            "vi_du_doi_song": "Người Thiên Cơ Mệnh + Hỏa Tinh đồng cung thường có ký ức tuổi thơ về sự kiện đột ngột — chuyển nhà, cha mẹ ly hôn, mất 1 trong cha/mẹ, hoặc bản thân phải sang nhà ông bà sớm. Người Thiên Cơ + Linh Tinh đồng cung có thể không có sự kiện 'đột ngột' nhưng có không khí gia đình âm trầm, lạnh lẽo — cha mẹ không hòa thuận, hoặc 1 trong 2 vắng mặt cảm xúc.",
            "iron_rule_warning": "'Chủ về' = xu hướng phản chiếu. Mệnh tạo dù gặp tuổi thơ khó khăn không có nghĩa cả đời thiếu phúc — Iron Rule #6 nhấn paradigm 'đọc đồng dạng', tuổi thơ là 1 chương, không phải toàn bộ.",
        },
    },
    {
        "question": "Tại sao Thiên Cơ-Thái Âm đồng độ Dần/Thân là chính cách 'Cơ Nguyệt Đồng Lương' và cung Thân tốt hơn cung Dần?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Cơ", "Thái Âm"],
            "cung": "Mệnh",
            "chi": ["Dần", "Thân"],
            "cach_cuc": "Cơ Nguyệt Đồng Lương",
            "uu_tien_chi": "Thân",
            "aspect": "modifiers",
        },
        "from_category": "Thiên Cơ-Thái Âm — Chính cách Cơ-Nguyệt-Đồng-Lương",
        "from_template": "Combo X-Y tại chi Z là cách cục gì? Tại sao chi A tốt hơn chi B?",
        "source_quote": "Thiên Cơ, Thái Âm đồng độ ở hai cung Dần hoặc Thân là chính cách 'Cơ Nguyệt Đồng Lương'. Ở cung Thân, Thiên Lương ở cung Tý ưu hơn Thiên Lương ở cung Ngọ, cho nên oán trách, thị phi ít hơn.",
        "commentary": {
            "han_viet": "Cơ Nguyệt Đồng Lương = Thiên Cơ + Thái Âm + Thiên Đồng + Thiên Lương (Nguyệt = Mặt Trăng = Thái Âm). 4 sao này thuộc nhóm cách cục cố định (chính cách). Oán trách + thị phi = lời ra tiếng vào, mâu thuẫn lời nói.",
            "viet_thuan": "Khi Mệnh có Thiên Cơ + Thái Âm cùng cung tại Dần hoặc Thân → mệnh tạo thuộc cách cục cổ điển 'Cơ Nguyệt Đồng Lương' — thiên về làm việc ổn định, lương bổng (như công chức, văn phòng). Cung Thân (đối diện Dần) tốt hơn vì khi tam phương tứ chính, Thiên Lương sẽ rơi vào cung Tý — Thiên Lương ở Tý ổn định hơn ở Ngọ → ít oán trách, ít thị phi.",
            "nguyen_ly": "Cách cục Cơ Nguyệt Đồng Lương là chuỗi 4 sao trên 4 cung Đẩu (Cơ-Nguyệt-Đồng-Lương). Khi Cơ + Nguyệt đồng cung → 1 ngôi nhà đã 'gọn'. Cung Thân → Tý là cung Bắc, thuộc Thuỷ, Thiên Lương Mộc tại Tý có thuỷ dưỡng → ấm tinh phát huy ấm. Cung Dần → Ngọ là cung Nam, thuộc Hỏa, Thiên Lương Mộc tại Ngọ bị Hỏa thiêu → ấm tinh hư khô → khẩu thiệt tăng.",
            "vi_du_doi_song": "Người Mệnh Cơ-Nguyệt Thân thường làm công chức/văn phòng/giáo viên ổn định, có lương đều, ít mâu thuẫn với đồng nghiệp. Người Mệnh Cơ-Nguyệt Dần cùng cách cục nhưng dễ vướng vào lời ra tiếng vào, hay bị hiểu lầm tại nơi làm việc. Cùng cách cục nhưng vị trí khác → trải nghiệm khác.",
            "iron_rule_warning": "'Ưu hơn' không có nghĩa 'chắc chắn tốt'. Phải kết hợp Tứ Hóa + sao phụ tá + sát tinh để định cát hung cụ thể.",
        },
    },
    {
        "question": "Thiên Cơ-Cự Môn đồng độ Mão/Dậu thì điều kiện cát/kỵ là gì?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Cơ", "Cự Môn"],
            "cung": "Mệnh",
            "chi": ["Mão", "Dậu"],
            "sao_can_co": "sao Lộc",
            "sao_ky": ["Hỏa Tinh", "Linh Tinh"],
            "aspect": "modifiers",
        },
        "from_category": "Thiên Cơ-Cự Môn — Điều kiện cát/kỵ",
        "from_template": "Combo X-Y tại Mão/Dậu → cần sao gì, kỵ sao gì?",
        "source_quote": "Thiên Cơ, Cự Môn đồng độ hai cung Mão hoặc Dậu, cần phải gặp sao lộc mới cát; rất kỵ có Hỏa Tinh, Linh Tinh cùng bay đến, chủ về khinh bạc, phóng đãng, thiếu trang trọng, phá phách.",
        "commentary": {
            "han_viet": "Sao Lộc = Lộc Tồn hoặc Hóa Lộc — sao tài/an định. Khinh bạc = coi thường, hời hợt; phóng đãng = không tự kiềm chế; thiếu trang trọng = không nghiêm túc.",
            "viet_thuan": "Combo Thiên Cơ + Cự Môn tại Mệnh Mão hoặc Dậu cần có sao Lộc (Lộc Tồn hoặc Hóa Lộc) để có nền ổn định mới phát huy mặt cát. Nếu gặp Hỏa Tinh hoặc Linh Tinh — tính cách trở thành khinh bạc, phóng đãng, ít nghiêm túc, dễ phá phách (việc gì cũng bỏ dở, quan hệ không gìn giữ).",
            "nguyen_ly": "Thiên Cơ Mộc + Cự Môn Thủy → Thuỷ sinh Mộc (Thiên Cơ được nuôi dưỡng), nhưng Cự Môn tính 'ám' (ám muội, lời tiếng) → Mộc bị ám khí. Cần Lộc (Thổ động hoặc Kim) làm 'điểm tựa thực tế' để Mộc không bị Thuỷ ám cuốn trôi. Hỏa-Linh = sát Hỏa thiêu Mộc + đốt Thuỷ → mọi thứ bốc cháy hỗn loạn → khinh bạc phóng đãng.",
            "vi_du_doi_song": "Người Mệnh Cơ-Cự Mão/Dậu + Lộc Tồn thường giỏi tài chính, có tài ăn nói thuyết phục — làm sales, broker, môi giới với phong thái nghiêm túc. Cùng combo + Hỏa Tinh dễ trở thành con nói nhiều mà việc bỏ dở, quan hệ ngắn hạn, lạm dùng lời để lừa dối.",
            "iron_rule_warning": "Tính cách 'phóng đãng' là xu hướng do năng lượng — không phải số phận. Mệnh tạo ý thức được + có môi trường tốt + tu dưỡng → có thể tránh.",
        },
    },
    {
        "question": "Thiên Cơ-Cự Môn Mão/Dậu nam/nữ mệnh hôn nhân khác nhau ra sao?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Cơ", "Cự Môn"],
            "cung": "Mệnh",
            "chi": ["Mão", "Dậu"],
            "hoa": ["Cự Môn Hóa Lộc", "Thiên Cơ Hóa Lộc"],
            "gioi_tinh_split": True,
            "aspect": "hon_nhan",
        },
        "from_category": "Thiên Cơ-Cự Môn — Hôn nhân nam/nữ split",
        "from_template": "Combo X-Y tại Mão/Dậu — nam vs nữ Hóa Lộc khác nhau gì về hôn nhân?",
        "source_quote": "Nam mệnh Cự Môn Hóa Lộc: Chủ về chồng già lấy vợ trẻ; Thiên Cơ Hóa Lộc: Thì phần nhiều là tái hôn. Nữ mệnh Cự Môn Hóa Lộc: Cũng nên lấy người lớn tuổi; Thiên Cơ Hóa Lộc: Phần nhiều đều có khiếm khuyết đáng tiếc trong hôn nhân.",
        "commentary": {
            "han_viet": "Khiếm khuyết đáng tiếc = chữ Hán 'di hám' — nuối tiếc + thiếu sót. Tái hôn = kết hôn lần thứ hai (cưới lại).",
            "viet_thuan": "Người Mệnh Cơ-Cự Mão/Dậu, tùy giới tính và Hóa Lộc rơi vào sao nào sẽ có vận hôn nhân khác: Nam mệnh + Cự Môn Hóa Lộc → có xu hướng cưới vợ trẻ hơn nhiều (chồng già vợ trẻ). Nam mệnh + Thiên Cơ Hóa Lộc → thường tái hôn (kết hôn lần 2). Nữ mệnh + Cự Môn Hóa Lộc → nên lấy chồng lớn tuổi. Nữ mệnh + Thiên Cơ Hóa Lộc → thường có khiếm khuyết đáng tiếc trong hôn nhân (chia tay, mất bạn đời, sống xa).",
            "nguyen_ly": "Cự Môn 'ám' + Hóa Lộc 'động tài' = sức hút mạnh với người 'khác thế hệ' (chênh tuổi). Thiên Cơ 'động chuyển' + Hóa Lộc 'thêm động' = hôn nhân không ổn định, dễ thay đổi. Giới tính ảnh hưởng cách thể hiện: nam ý chí chủ động hơn (chọn vợ trẻ), nữ thụ động hơn (lấy chồng già hoặc chấp nhận khiếm khuyết).",
            "vi_du_doi_song": "Một người nam Mệnh Cơ-Cự + Cự Hóa Lộc thường gặp duyên với người ít tuổi hơn — kết hôn với người kém 5-10 tuổi không hiếm. Một người nữ Mệnh Cơ-Cự + Thiên Cơ Hóa Lộc có thể trải qua một mối nghiêm túc nhưng dở dang (đính hôn rồi chia tay, hoặc cưới rồi sống xa do hoàn cảnh), khó tránh nuối tiếc.",
            "iron_rule_warning": "Đây là xu hướng năng lượng, KHÔNG phải định mệnh. Mệnh tạo biết trước có thể tránh tình huống (vd. nữ mệnh Thiên Cơ Hóa Lộc nên chậm rãi trong chọn bạn đời, không vội cưới khi chưa chắc).",
        },
    },
    {
        "question": "Thiên Cơ-Thiên Lương Thìn/Tuất nên làm nghề gì? Tại sao không hợp chính giới/kinh doanh?",
        "subject_identifiers": {
            "sao_chinh": ["Thiên Cơ", "Thiên Lương"],
            "cung": "Mệnh",
            "chi": ["Thìn", "Tuất"],
            "cach_cuc": "thiên cách Cơ Nguyệt Đồng Lương",
            "nghe_phu_hop": "nhân tài chuyên nghiệp (tay nghề)",
            "nghe_khong_phu_hop": ["chính giới", "kinh doanh buôn bán"],
            "aspect": "dinh_huong",
        },
        "from_category": "Thiên Cơ-Thiên Lương — Định hướng nghề (chuyên môn)",
        "from_template": "Combo X-Y tại chi Z — nên/không nên nghề gì?",
        "source_quote": "Thiên Cơ, Thiên Lương đồng độ hai cung Thìn hoặc Tuất, chủ về có tay nghề, ở thời hiện đại cũng có thể định là nhân tài chuyên nghiệp; không thích hợp làm việc trong chính giới hay kinh doanh buôn bán, nếu không, phúc không được lâu dài, vận tốt thường chỉ trong chớp mắt.",
        "commentary": {
            "han_viet": "Nhân tài chuyên nghiệp = professional/specialist (người có chuyên môn sâu một lĩnh vực). Chính giới = political circle. Phúc không được lâu dài = thành công không bền.",
            "viet_thuan": "Mệnh Thiên Cơ + Thiên Lương Thìn/Tuất có khiếu chuyên môn cao (nghiên cứu, kỹ thuật, y học, học thuật, design...). Nếu lao vào chính trị hoặc kinh doanh buôn bán → có thể đạt thành công ngắn hạn nhưng KHÔNG bền — vận tốt như 'chớp mắt' rồi tàn.",
            "nguyen_ly": "Thiên Cơ Mộc + Thiên Lương Mộc Thổ = 2 sao 'tĩnh tâm chuyên sâu' (Mộc tịnh dưỡng, Lương ấm tinh giảm cô). Khi tập trung 1 chuyên môn → 2 sao cộng hưởng đào sâu kiến thức. Khi đi vào chính giới (đa quan hệ, đa biến) hoặc kinh doanh (đa rủi ro, đa cạnh tranh) → môi trường biến động vượt khả năng cộng hưởng 2 sao tĩnh → mệt mỏi + mất phúc.",
            "vi_du_doi_song": "Người Mệnh Cơ-Lương Thìn/Tuất phù hợp làm bác sĩ chuyên khoa, kỹ sư phần mềm chuyên về 1 mảng, nhà nghiên cứu, giáo viên đại học, kế toán trưởng, kiến trúc sư. Nếu nhảy sang làm chính trị (nghị viên, lãnh đạo đảng phái) hoặc start-up kinh doanh tự do → dù ban đầu thành công cũng dễ kiệt sức + thất bại sau vài năm.",
            "iron_rule_warning": "'Phúc không được lâu dài' = xu hướng cảnh báo. Mệnh tạo nếu vẫn muốn theo chính giới/kinh doanh có thể bổ sung bộ phụ tá tốt + tu dưỡng tâm lý để giảm thiểu — không phải định mệnh.",
        },
    },
    {
        "question": "Thiên Cơ Tị/Hợi nữ mệnh kỵ Hóa Kỵ ra sao? Phụ tá cát thì sao?",
        "subject_identifiers": {
            "sao_chinh": "Thiên Cơ",
            "cung": "Mệnh",
            "chi": ["Tỵ", "Hợi"],
            "gioi_tinh": "nữ",
            "hoa_ky": "Hóa Kỵ",
            "phu_ta_cat": ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"],
            "nghe_phu_hop": ["truyền thông", "thông tấn", "báo chí"],
            "aspect": "modifiers",
        },
        "from_category": "Thiên Cơ Tị/Hợi — Nữ mệnh kỵ vs cát",
        "from_template": "Sao X tại Mệnh chi Y, nữ mệnh Hóa Kỵ vs phụ tá cát?",
        "source_quote": "Thiên Cơ ở hai cung Tị hoặc Hợi, cuộc đời gặp nhiều rắc rối khó xử về tình cảm. Nữ mệnh không nên Hóa Kỵ hoặc có sao kỵ hội chiếu; gặp thêm sát tinh, chủ về hình khắc, sinh li, hoặc làm nhị phòng, tì thiếp. Gặp các sao phụ, tá cát, thì có thể phú quý, thích hợp làm những công việc mang tính phục vụ công chúng, đặc biệt về truyền thông hay thông tấn, báo chí.",
        "commentary": {
            "han_viet": "Hình khắc = bị tổn hại do người thân; sinh li = sống xa cách (chưa chết); nhị phòng = vợ thứ hai (thê thiếp); tì thiếp = nàng hầu/tiểu phòng. Phục vụ công chúng = serve the public.",
            "viet_thuan": "Nữ mệnh Thiên Cơ Tị/Hợi cuộc đời gặp nhiều rắc rối tình cảm. Nếu gặp Hóa Kỵ hoặc sao kỵ chiếu + sát tinh → có thể chịu hình khắc (tổn thương do bạn đời/người thân), sinh ly (xa cách), hoặc duyên phận trắc trở (làm vợ thứ hai, người thứ ba). Nhưng nếu gặp đủ bộ phụ tá cát (Tả-Hữu-Xương-Khúc-Khôi-Việt) → có thể đạt phú quý qua nghề phục vụ công chúng — đặc biệt truyền thông, báo chí, thông tấn.",
            "nguyen_ly": "Thiên Cơ Mộc Âm + chi Tỵ Hỏa hoặc Hợi Thủy. Tỵ Hỏa thiêu Mộc; Hợi Thủy nhiều Mộc trôi nổi → cả 2 đều khó cho Thiên Cơ. Hóa Kỵ thuộc Thủy uất → càng đẩy Thiên Cơ vào ám khí. Nữ mệnh thuộc Âm tính → nhạy cảm với tổn thương cảm xúc hơn. Phụ tá cát cung cấp 'cộng đồng' và 'tài năng diễn đạt' → chuyển khổ thành công cụ phục vụ — phù hợp truyền thông/báo chí (nghề lấy nhạy cảm + tài nói + duyên với công chúng).",
            "vi_du_doi_song": "Nữ mệnh Thiên Cơ Tị/Hợi + Hóa Kỵ + sát tinh thường vướng vào tình tay ba, yêu phải người đã kết hôn, hoặc kết hôn rồi chồng có người khác, hoặc phải chấp nhận làm 'vai phụ' trong quan hệ. Cùng vị trí + Tả-Hữu-Xương-Khúc-Khôi-Việt → trở thành nhà báo, MC truyền hình, copywriter giỏi, content creator có influence, broadcaster — biến nhạy cảm thành tài năng giao tiếp với công chúng.",
            "iron_rule_warning": "'Làm nhị phòng/tì thiếp' là thuật ngữ cổ — thời hiện đại có thể đọc là 'gặp khó khăn duyên phận', 'không kết hôn chính thức', 'mối quan hệ không cân bằng'. Iron Rule #6: phản chiếu xu hướng năng lượng, không định mệnh cứng. Mệnh tạo ý thức + chọn người + môi trường có thể tránh được.",
        },
    },
]


def persist():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")

    book = "trung-chau-tu-vi-dau-so-2"
    # Section 5.1.2 cover p506-509. Em insert 1 chunk synthesized.
    # Find existing chunks p506-509 và mark section_id
    for page in range(506, 510):
        conn.execute(
            "UPDATE chunks_v2 SET section_id='5.1.2' WHERE book_corpus_id=? AND page_start=?",
            (book, page),
        )

    # Insert 1 'synth' chunk represent toàn section
    existing = conn.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=506 AND section_id='5.1.2'",
        (book,),
    ).fetchone()
    if existing:
        chunk_id = existing[0]
        # Update text to synth content
        conn.execute(
            "UPDATE chunks_v2 SET text=?, section_id=? WHERE chunk_id=?",
            (CHUNK_TEXT, "5.1.2", chunk_id),
        )
        # Clear old atoms for clean insert
        conn.execute("DELETE FROM atom_commentaries WHERE atom_id IN (SELECT atom_id FROM atomic_questions WHERE chunk_id=?)", (chunk_id,))
        conn.execute("DELETE FROM atomic_questions WHERE chunk_id=?", (chunk_id,))
        conn.execute("DELETE FROM chunk_classifications WHERE chunk_id=?", (chunk_id,))
        print(f"📦 Cleaned chunk_id={chunk_id} (p506) for 5.1.2 re-insert")
    else:
        cur = conn.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, page_start, page_end, text, section_id)
               VALUES (?, 506, 509, ?, '5.1.2')""",
            (book, CHUNK_TEXT),
        )
        chunk_id = int(cur.lastrowid)
        print(f"📦 New chunk_id={chunk_id} section 5.1.2")
    conn.commit()

    # Classification
    cur = conn.execute(
        """INSERT INTO chunk_classifications
           (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
            format_style, knowledge_categories_json, extracted_by, confidence)
           VALUES (?, 0, 0, 1, 1, 1, 'nguyen_ly', ?, 'claude-inline', 0.95)""",
        (chunk_id, json.dumps([
            "Thiên Cơ Tý/Ngọ — Hóa Quyền vs Hóa Lộc",
            "Thiên Cơ Tý/Ngọ — đối cung Cự Môn",
            "Thiên Cơ kỵ Hỏa Linh đồng độ",
            "Cơ-Nguyệt Dần/Thân — chính cách",
            "Cơ-Cự Mão/Dậu — điều kiện",
            "Cơ-Cự — gender split hôn nhân",
            "Cơ-Lương Thìn/Tuất — chuyên môn",
            "Thiên Cơ Tị/Hợi — nữ mệnh",
        ], ensure_ascii=False)),
    )
    cc_id = int(cur.lastrowid)
    conn.commit()

    # Insert atoms + commentaries
    n = 0
    for atom_data in ATOMIC_DATA:
        cur = conn.execute(
            """INSERT INTO atomic_questions
               (chunk_id, cc_id, question_text, question_lang, from_category, from_template,
                subject_identifiers, source_quote, confidence, founder_verified,
                extracted_by, section_id)
               VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, 0.95, 0, 'claude-inline', '5.1.2')""",
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
            (
                atom_id,
                c.get("han_viet"),
                c.get("viet_thuan"),
                c.get("nguyen_ly"),
                c.get("vi_du_doi_song"),
                c.get("iron_rule_warning"),
            ),
        )

    conn.execute("UPDATE chunks_v2 SET atom_q_str=? WHERE chunk_id=?",
                 ("\n".join(a["question"] for a in ATOMIC_DATA), chunk_id))
    conn.commit()

    # Rebuild FTS to include new atoms
    conn.execute("INSERT INTO atomic_questions_fts(atomic_questions_fts) VALUES('rebuild')")
    conn.commit()

    print(f"✅ {n} atoms + {n} commentaries (4 layers) inserted for section 5.1.2")
    n_total = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE section_id='5.1.2'").fetchone()[0]
    print(f"📊 DB section 5.1.2: {n_total} atoms total")
    conn.close()


if __name__ == "__main__":
    print("═" * 70)
    print("EM TỰ XỬ LÝ Section 5.1.2 — Thiên Cơ ở Cung Mệnh")
    print("6 variants × 8 atomic Q × 4-layer commentary")
    print("═" * 70)
    persist()
