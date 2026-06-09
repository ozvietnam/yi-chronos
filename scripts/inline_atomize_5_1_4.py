"""Inline atomize Section 5.1.4 — Vũ Khúc ở Cung Mệnh (p513-516)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

CHUNK_TEXT = """### 5.1.4. Vũ Khúc ở cung Mệnh (thân)

Vũ Khúc là sao tiền tài; phần biệt tỉ mỉ là hành động kiếm tiền, khác với Thái Âm là kế hoạch kiếm tiền. Cho nên cổ nhân xếp Thái Âm thuộc văn, còn Vũ Khúc thuộc võ.

Vũ Khúc là sao cô quả, vì vậy không thích hợp với nữ mệnh. Dù có cuộc sống hôn nhân, cũng chủ về vợ đoạt quyền chồng. Ở thời hiện đại, thường là điểm tượng thao túng sự nghiệp của chồng, mà còn chủ về kết hôn muộn.

Vũ Khúc, Thiên Phủ ở hai cung Tý hoặc Ngọ, ở cung Ngọ tốt hơn. Cổ quyết nói: "Vũ Khúc, Thiên Phủ ở cung chủ về sống thọ", nhưng ở cung Tý lại ngại cung Phụ Mẫu là Thái Dương lạc hãm, e rằng còn nhỏ đã mồ côi. Vũ Khúc, Thiên Phủ khí rất hòa hoãn, cho nên cổ nhân cho rằng rất thích hợp với nữ mệnh. Ở thời hiện đại, bất kể nam nữ, có sao Lộc + Thiên Khôi Thiên Việt → đắc ý trong giới làm ăn kinh doanh.

Vũ Khúc, Tham Lang thủ Mệnh ở hai cung Sửu hoặc Mùi, có Hỏa Tinh hoặc Linh Tinh đồng độ là rất tốt. Ở cung Tài Bạch và cung Điền Trạch cũng cát. Cổ quyết: "Vũ Khúc, Tham Lang ở tài trạch vị, hoạnh phát tiền của." Không có cát tinh mà có sát tinh, sẽ chủ về hoạnh phát hoạnh phá. Hóa Kỵ (Vũ Khúc Hóa Kỵ nặng hơn) gặp Hỏa Linh thì chủ về thông minh, có nghề đặc biệt mưu sinh — thời hiện đại theo công nghệ, khoa học kỹ thuật.

Vũ Khúc, Thiên Tướng thủ mệnh ở hai cung Dần hoặc Thân, phần nhiều chủ về là người làm việc hưởng lương, chỉ nên làm chức phó, không nên một mình gánh vác. Có Văn Xương, Văn Khúc hội hợp → thông minh, tay nghề khéo (công nghệ, KHKT). Văn Khúc đồng độ + sao đào hoa (Thiên Diêu nặng) → trôi nổi. Tài bạch Liêm Trinh Hóa Kỵ → nên làm nghề "hung sự" (ẩm thực, y dược, ngoại khoa, hóa nghiệm, tang lễ).

Vũ Khúc, Thất Sát thủ mệnh ở cung Mão, gặp sát kị → nạn tai bất trắc, cổ quyết: "ác sát hao tù hội hợp ở cung Chấn, chủ về cây đè, sét đánh". Ở cung Dậu, vì tranh giành tiền bạc mà động võ: "Vũ Khúc, Kiếp Sát hội Kình Dương, vì tiền mà cầm đao". Tổ hợp sao có nguy cơ. Nếu không có sát kị tại bản cung, gặp sát kị ngoài bản cung → võ nghiệp lập công trạng.

Vũ Khúc độc tọa ở hai cung Thìn hoặc Tuất, gặp cát tinh nắm giữ tài chính; gặp sát tinh, là tiểu thương, tuyệt đối không nên theo võ nghiệp. Ở Thìn/Tuất ắt đối Tham Lang, tính chất tương tự "Vũ Khúc, Tham Lang" Sửu/Mùi.

Vũ Khúc, Phá Quân ở hai cung Tị hoặc Hợi, đồng độ với Hỏa Tinh, Linh Tinh, chủ về phá tổ nghiệp mà tự lập. Được cát hóa và sao cát, thì cuộc đời phần nhiều gánh vác trọng trách, hoặc thường gánh vác công việc quá mức."""


ATOMIC_DATA = [
    {
        "question": "Vũ Khúc có tính chất gì cốt lõi? Khác Thái Âm ra sao về kiếm tiền?",
        "subject_identifiers": {
            "sao_chinh": "Vũ Khúc",
            "tinh_chat": ["sao tiền tài", "võ tinh", "hành động kiếm tiền"],
            "khac_voi": "Thái Âm (văn, kế hoạch kiếm tiền)",
            "aspect": "tong_quan",
        },
        "from_category": "Vũ Khúc — Bản chất + so với Thái Âm",
        "from_template": "Tính chất gốc của sao X? So với sao Y?",
        "source_quote": "Vũ Khúc là sao tiền tài; phần biệt tỉ mỉ là hành động kiếm tiền, khác với Thái Âm là kế hoạch kiếm tiền. Cho nên cổ nhân xếp Thái Âm thuộc văn, còn Vũ Khúc thuộc võ.",
        "commentary": {
            "han_viet": "Vũ Khúc 武曲 = sao võ (cương quyết, hành động); Thái Âm 太陰 = sao Mặt Trăng (mềm, suy tính). Văn vs võ = phân biệt cổ điển Trung Hoa: văn (tri thức + kế hoạch), võ (hành động + chiến đấu).",
            "viet_thuan": "Vũ Khúc là sao chủ về tiền bạc — nhưng KHÔNG phải tiền do tính toán mà tiền do HÀNH ĐỘNG kiếm về. Thái Âm cũng là sao tài lộc nhưng thuộc 'văn' — kiếm tiền bằng kế hoạch, đầu tư, suy tính. Vũ Khúc thuộc 'võ' — kiếm tiền bằng làm việc thực tế, bán hàng, sản xuất, thực thi.",
            "nguyen_ly": "Vũ Khúc thuộc Kim, Âm — Kim mạnh ở thực hành (chặt, cắt, định hình). Thái Âm thuộc Thủy, Âm — Thủy mềm, chảy quanh, dự trữ. Cùng là Âm tinh nhưng Kim vs Thủy → hành động vs suy tính. Đây là paradigm cổ điển: cùng chủ tài nhưng method khác → người Vũ Khúc đi làm để có tiền, người Thái Âm đầu tư/tích lũy để có tiền.",
            "vi_du_doi_song": "Người Mệnh Vũ Khúc thường là doanh nhân thực hành — bán hàng trực tiếp, làm sản phẩm, lao động kiếm tiền. KHÔNG hợp nghề đầu tư phân tích lâu dài. Người Mệnh Thái Âm hợp đầu tư bất động sản, tài chính, kế hoạch dài hạn. Cùng kiếm tiền nhưng 1 người 'làm để có', 1 người 'tính để có'.",
            "iron_rule_warning": "Đây là xu hướng tính cách + method — không có nghĩa người Vũ Khúc kém tài chính hay người Thái Âm lười. Cả 2 đều có thể giàu, chỉ con đường khác.",
        },
    },
    {
        "question": "Tại sao Vũ Khúc 'là sao cô quả' và bất lợi với nữ mệnh?",
        "subject_identifiers": {
            "sao_chinh": "Vũ Khúc",
            "tinh_chat": "cô quả",
            "gioi_tinh_canh_bao": "nữ",
            "anh_huong": ["vợ đoạt quyền chồng", "thao túng sự nghiệp chồng", "kết hôn muộn"],
            "aspect": "modifiers",
        },
        "from_category": "Vũ Khúc — Cô quả với nữ mệnh",
        "from_template": "Sao X có tính chất cô quả ảnh hưởng nữ mệnh thế nào?",
        "source_quote": "Vũ Khúc là sao cô quả, vì vậy không thích hợp với nữ mệnh. Dù có cuộc sống hôn nhân, cũng chủ về vợ đoạt quyền chồng. Ở thời hiện đại, thường là điểm tượng thao túng sự nghiệp của chồng, mà còn chủ về kết hôn muộn.",
        "commentary": {
            "han_viet": "Cô quả 孤寡 = cô độc + góa bụa (lẻ loi). Đoạt quyền chồng = chiếm quyền của chồng, vợ mạnh hơn chồng. Thao túng sự nghiệp = quản lý + điều khiển nghề chồng.",
            "viet_thuan": "Vũ Khúc là sao võ — cương quyết, độc lập. Đối với nữ mệnh (xã hội cổ kỳ vọng phụ nữ 'âm thuận'), tính cương quyết này KHÔNG hợp với khuôn mẫu 'người vợ nhu'. Hiện đại tính cách Vũ Khúc nữ → tự lập + làm chủ → dễ mạnh hơn chồng, kiểm soát sự nghiệp gia đình → mâu thuẫn → kết hôn muộn (vì khó tìm bạn đời chấp nhận tính độc lập).",
            "nguyen_ly": "Vũ Khúc Kim Âm — Kim cương, Âm cô. Nữ giới trong paradigm âm-dương cổ điển = nguyên thủy Âm + nhu. Khi Mệnh có Vũ Khúc → bản chất 'Kim cương' thay 'nhu' → đi ngược âm tính tự nhiên → 'cô' (khó cộng sự âm-dương). Hiện đại không còn coi đó là 'xấu', chỉ là 'khó hợp khuôn mẫu xã hội truyền thống'.",
            "vi_du_doi_song": "Nữ mệnh Vũ Khúc thường là người 'kiếm tiền chính' trong gia đình, quyết định lớn, đứng tên sản nghiệp. Chồng thường đóng vai 'phụ' hoặc chấp nhận để vợ làm chủ. Một số người chọn không kết hôn (sự nghiệp chính), một số kết hôn muộn (30+) sau khi xây xong nền tảng độc lập.",
            "iron_rule_warning": "Cách dùng 'không thích hợp' là paradigm cổ — ngày nay nữ mệnh Vũ Khúc thường thành đạt mạnh trong sự nghiệp. KHÔNG phải xấu, chỉ là 'không hợp khuôn mẫu cổ điển'. Mệnh tạo nữ Vũ Khúc nên kết hôn với người ủng hộ tính độc lập, không tìm 'chồng truyền thống cứng nhắc'.",
        },
    },
    {
        "question": "Vũ Khúc-Thiên Phủ Tý/Ngọ — tại sao Ngọ tốt hơn Tý? Cần sao gì hợp với nữ mệnh?",
        "subject_identifiers": {
            "sao_chinh": ["Vũ Khúc", "Thiên Phủ"],
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "uu_tien": "Ngọ",
            "ly_do_Ty_kem": "cung Phụ Mẫu là Thái Dương lạc hãm",
            "sao_can_co": ["Lộc", "Thiên Khôi", "Thiên Việt"],
            "aspect": "modifiers",
        },
        "from_category": "Vũ Khúc-Thiên Phủ Tý/Ngọ — Ưu nhược + điều kiện",
        "from_template": "Combo X-Y Tý/Ngọ — chi nào tốt hơn, tại sao?",
        "source_quote": "Vũ Khúc, Thiên Phủ ở hai cung Tý hoặc Ngọ, ở cung Ngọ tốt hơn. Cổ quyết nói: 'Vũ Khúc, Thiên Phủ ở cung chủ về sống thọ', nhưng ở cung Tý lại ngại cung Phụ Mẫu là Thái Dương lạc hãm, e rằng còn nhỏ đã mồ côi. Vũ Khúc, Thiên Phủ khí rất hòa hoãn, cho nên cổ nhân cho rằng rất thích hợp với nữ mệnh. Có sao Lộc + Thiên Khôi Thiên Việt → đắc ý trong giới làm ăn kinh doanh.",
        "commentary": {
            "han_viet": "Khí hòa hoãn = năng lượng mềm dịu (không gắt). Thiên Phủ 天府 = 'kho trời' (sao chủ tiết kiệm + ổn định). Mồ côi = mất cha mẹ sớm.",
            "viet_thuan": "Mệnh Vũ Khúc + Thiên Phủ rất tốt — kết hợp 'sao võ tài' (Vũ Khúc) với 'kho tài' (Thiên Phủ) → cách 'phú quý sống thọ'. Cung Ngọ ưu hơn Tý vì khi ở Tý, cung Phụ Mẫu (1 cung lên) là Thái Dương lạc hãm (Mặt Trời tắt) → cha mẹ mất sớm hoặc xa cách. Khí 'hòa hoãn' giúp combo này hợp cả nam và nữ mệnh — đặc biệt nữ mệnh Vũ Khúc thường khó, nhưng có Thiên Phủ làm dịu → ổn. Cần thêm sao Lộc + Khôi Việt → đắc ý kinh doanh.",
            "nguyen_ly": "Vũ Khúc Kim Âm + Thiên Phủ Thổ Dương → Thổ sinh Kim (Thiên Phủ nuôi Vũ Khúc). Combo cân bằng âm-dương + tương sinh. Cung Ngọ (Hỏa cực thịnh) — Hỏa khắc Kim nhưng Thiên Phủ Thổ ở giữa làm dung hòa. Cung Tý (Thủy cực thịnh) — Kim sinh Thủy → khí Vũ Khúc rỗng đi + thêm phụ mẫu Thái Dương lạc hãm = double hung cho tuổi thơ.",
            "vi_du_doi_song": "Người Mệnh Vũ-Phủ Ngọ thường có tuổi thơ ấm no, sự nghiệp ổn định từ trẻ, có vốn cha mẹ để khởi nghiệp + sống lâu. Người Mệnh Vũ-Phủ Tý hay có cha mẹ ly hôn / mất sớm + tự lập từ nhỏ. Nữ mệnh Vũ-Phủ là cách quý — không có tính 'cô quả' nặng như Vũ Khúc đơn lẻ, hợp kinh doanh nhỏ + ổn định gia đình.",
            "iron_rule_warning": "'Mồ côi' là xu hướng cảnh báo cho Vũ-Phủ Tý, KHÔNG phải định mệnh. Phải xem thêm sát tinh + Tứ Hóa + Phụ Mẫu cụ thể.",
        },
    },
    {
        "question": "Vũ Khúc-Tham Lang Sửu/Mùi tại sao 'có Hỏa Tinh/Linh Tinh đồng độ là rất tốt'?",
        "subject_identifiers": {
            "sao_chinh": ["Vũ Khúc", "Tham Lang"],
            "cung": "Mệnh",
            "chi": ["Sửu", "Mùi"],
            "sao_uu_tien_dong_do": ["Hỏa Tinh", "Linh Tinh"],
            "cach_cuc": "Vũ Tham hoạnh phát",
            "co_quet": "Vũ Khúc Tham Lang ở tài trạch vị hoạnh phát tiền của",
            "canh_bao_khong_cat": "hoạnh phát hoạnh phá",
            "aspect": "modifiers",
        },
        "from_category": "Vũ Khúc-Tham Lang Sửu/Mùi — Hỏa Linh đồng độ",
        "from_template": "Combo X-Y tại chi Z + sao W đồng độ → cách gì?",
        "source_quote": "Vũ Khúc, Tham Lang thủ Mệnh ở hai cung Sửu hoặc Mùi, có Hỏa Tinh hoặc Linh Tinh đồng độ là rất tốt. Ở cung Tài Bạch và cung Điền Trạch cũng cát. Cổ quyết nói: 'Vũ Khúc, Tham Lang ở tài trạch vị, hoạnh phát tiền của.' Không có cát tinh mà có sát tinh, sẽ chủ về hoạnh phát hoạnh phá.",
        "commentary": {
            "han_viet": "Hoạnh phát = phát đột ngột (rủi nhưng nhanh). Hoạnh phá = phá đột ngột (lỗ nhanh). Tài trạch vị = cung Tài Bạch hoặc cung Điền Trạch. Hỏa Tinh + Linh Tinh thường là 'sát tinh' (xấu) nhưng combo với Vũ-Tham lại đặc biệt.",
            "viet_thuan": "Combo Vũ Khúc + Tham Lang tại Sửu/Mùi là cách 'Vũ Tham' — bình thường Hỏa Tinh + Linh Tinh là sát tinh xấu, NHƯNG khi đồng độ với Vũ-Tham → tạo cách 'hoạnh phát' (kiếm được tiền lớn đột ngột). Lý do: Tham Lang là sao 'ham muốn', cần Hỏa-Linh 'đốt cháy' để biến tham vọng thành hành động. Nếu KHÔNG có cát tinh (Lộc/Khôi Việt/Tả Hữu) mà chỉ có Hỏa-Linh + sát tinh khác → vẫn hoạnh phát nhưng cũng hoạnh phá (lỗ vốn).",
            "nguyen_ly": "Vũ Khúc Kim + Tham Lang Mộc Thủy → Kim khắc Mộc nhưng Thủy hỗ trợ. Hỏa Tinh + Linh Tinh = Hỏa cương + Hỏa âm → khi gặp Vũ-Tham → Hỏa luyện Kim (vũ khí sắc) + Hỏa sinh Thủy hơi (động lực) → cộng hưởng nổ ra hành động kiếm tiền nhanh. KHÁC với Hỏa-Linh ở sao khác (làm hại). Đây là exception paradigm cổ điển — 'cùng sao, vị trí khác → ý nghĩa ngược'.",
            "vi_du_doi_song": "Người Mệnh Vũ-Tham Sửu/Mùi + Hỏa Tinh thường có cú 'phát tài' đột ngột trong đời — trúng cổ phiếu, bán đất giá cao, hợp đồng lớn bất ngờ. Nhưng nếu không quản lý tốt → cũng mất nhanh. Thời hiện đại nhiều người Vũ-Tham + Hỏa Tinh giàu nhanh nhờ crypto/startup nhưng mất nhanh cũng vì các kênh đó.",
            "iron_rule_warning": "'Hoạnh phát' là xu hướng cơ hội — KHÔNG đảm bảo phát. Mệnh tạo phải có hành động (làm kinh doanh, dám đầu tư). Iron Rule #6: paradigm Xu Cát Tị Hung — hậu thiên hành động xoay chuyển. Sau khi hoạnh phát, BẮT BUỘC tiết kiệm + đa dạng hóa để tránh hoạnh phá.",
        },
    },
    {
        "question": "Vũ Khúc-Thiên Tướng Dần/Thân nên làm chức gì? Tài bạch Liêm-Phủ Hóa Kỵ thì nghề gì?",
        "subject_identifiers": {
            "sao_chinh": ["Vũ Khúc", "Thiên Tướng"],
            "cung": "Mệnh",
            "chi": ["Dần", "Thân"],
            "vai_tro": "chức phó (deputy)",
            "khong_nen": "một mình gánh vác",
            "voi_van_xuong_van_khuc": "thông minh, tay nghề khéo (KHKT)",
            "voi_van_khuc_dao_hoa": "trôi nổi không yên",
            "tai_bach_liem_phu_hoa_ky": "nghề hung sự (ẩm thực, y dược, ngoại khoa, hóa nghiệm, tang lễ)",
            "aspect": "dinh_huong",
        },
        "from_category": "Vũ-Tướng Dần/Thân — Định hướng nghề",
        "from_template": "Combo X-Y tại chi Z — vai trò + nghề?",
        "source_quote": "Vũ Khúc, Thiên Tướng thủ mệnh ở hai cung Dần hoặc Thân, phần nhiều chủ về là người làm việc hưởng lương, chỉ nên làm chức phó, không nên một mình gánh vác. Vũ Khúc, Thiên Tướng có Văn Xương, Văn Khúc hội hợp, chủ về thông minh, tay nghề khéo. Vũ Khúc, Thiên Tướng thủ mệnh, nếu cung tài bạch là Liêm Trinh, Thiên Phủ, mà Liêm Trinh Hóa Kỵ, nên làm công việc có tính hung sự để kiếm tiền.",
        "commentary": {
            "han_viet": "Hưởng lương = ăn lương cố định (không tự kinh doanh). Chức phó = vice/deputy (cấp dưới CEO/lãnh đạo). Hung sự = công việc liên quan tới máu, đau, chết, bệnh, lửa, độc, mặt tối.",
            "viet_thuan": "Mệnh Vũ-Tướng tại Dần/Thân nên làm chức phó (CFO, COO, phó giám đốc) — KHÔNG nên làm số 1 (CEO solo) vì sẽ thiếu nội lực. Nếu có Văn Xương Văn Khúc → thông minh + tay nghề khéo → hợp công nghệ, kỹ thuật, R&D. Nếu Văn Khúc + sao đào hoa (Thiên Diêu) → tính trôi nổi, không giữ một nghề. Nếu cung Tài Bạch là Liêm-Phủ + Liêm Trinh Hóa Kỵ → nên làm nghề 'hung sự' (ẩm thực, y dược, ngoại khoa, hóa nghiệm, tang lễ).",
            "nguyen_ly": "Vũ Khúc Kim + Thiên Tướng Thủy → Kim sinh Thủy nhưng Vũ Khúc bị 'tiết khí' qua Thiên Tướng (chữ 'Tướng' = quan ấn, phụ trợ). Combo này = 'tài năng phụ trợ' — đứng sau hỗ trợ lãnh đạo chính. Văn Xương-Văn Khúc thêm vào → 'tài năng kỹ thuật'. Liêm Trinh Hóa Kỵ Tài Bạch = năng lượng máu/sát/đau biến thành tiền → đó là 'hung sự'.",
            "vi_du_doi_song": "Người Mệnh Vũ-Tướng Dần/Thân thành công nhất khi làm Phó Giám đốc, Trưởng phòng kỹ thuật, Manager — KHÔNG hợp làm Founder/CEO 1 mình. Nếu tài bạch có Liêm-Phủ Hóa Kỵ → nghề hợp: bác sĩ phẫu thuật, đầu bếp ẩm thực cao cấp, kỹ sư hóa, nhà tang lễ — các nghề 'có máu/đau/chết' liên quan → kiếm tiền lớn.",
            "iron_rule_warning": "'Nên làm chức phó' không phải định mệnh không thành CEO — là xu hướng phù hợp năng lượng. Nếu mệnh tạo có team mạnh + cố vấn tốt vẫn có thể làm CEO, nhưng phải nhận thức bản thân hợp 'support' hơn 'lead solo'.",
        },
    },
    {
        "question": "Vũ Khúc-Thất Sát Mão/Dậu nguy hiểm thế nào? Cách phân biệt cát/hung?",
        "subject_identifiers": {
            "sao_chinh": ["Vũ Khúc", "Thất Sát"],
            "cung": "Mệnh",
            "chi": ["Mão", "Dậu"],
            "Mao_canh_bao": "cây đè, sét đánh (ác sát hao tù)",
            "Dau_canh_bao": "vì tiền cầm đao (Vũ Khúc Kiếp Sát hội Kình Dương)",
            "rule_an_toan": "không sát kị bản cung → ok; sát kị ngoài bản cung → võ nghiệp lập công",
            "aspect": "canh_bao",
        },
        "from_category": "Vũ Khúc-Thất Sát Mão/Dậu — Cảnh báo nguy cơ",
        "from_template": "Combo X-Y tại chi Z — nguy cơ + điều kiện an toàn?",
        "source_quote": "Vũ Khúc, Thất Sát thủ mệnh ở cung Mão, gặp các sao sát, kị sẽ chủ về nạn tai bất trắc. Cổ quyết nói: 'Các sao ác, sát, hao, tù hội hợp ở cung Chấn, chủ về cây đè, sét đánh'. Ở cung Dậu, là điểm tượng vì tranh giành tiền bạc mà động võ. Cổ quyết nói: 'Vũ Khúc, Kiếp Sát hội Kình Dương, vì tiền mà cầm đao.' Tổ hợp sao có nguy cơ. Vũ Khúc, Thất Sát ở bản cung không có các sao sát, kị, thì không sao; nếu ở ngoài bản cung mà gặp các sao sát, kị, thì thích hợp với võ nghiệp, có thể lập công trạng.",
        "commentary": {
            "han_viet": "Vũ + Sát = combo 'song võ' (Vũ Khúc võ tinh + Thất Sát võ tướng). Cung Chấn = cung Mão thuộc Mộc Đông. Hao = sao Đại Hao/Tiểu Hao (phá tài). Tù = sao Tù (gây tù tội). Kiếp Sát = sao Kiếp (mất mát). Kình Dương = sát tinh chính. Võ nghiệp = nghề quân đội, cảnh sát, an ninh.",
            "viet_thuan": "Combo Vũ Khúc + Thất Sát tại Mão hoặc Dậu là 'tổ hợp sao có nguy cơ'. Nếu thêm sát kị tại bản cung → CỰC nguy: Mão (cây đè, sét đánh — tai nạn ngoài trời); Dậu (vì tiền cầm đao — bạo lực do tranh chấp tiền). Nếu bản cung KHÔNG có sát kị → ok bình thường. Nếu sát kị nằm ở cung khác (đại vận, lưu niên) → thay vì gặp tai họa, mệnh tạo có thể chọn 'võ nghiệp' (quân đội, an ninh) để chuyển hóa năng lượng — lập công trạng.",
            "nguyen_ly": "Vũ Khúc Kim + Thất Sát Kim Hỏa → 'Kim chiến Hỏa' cực mạnh. Mão Mộc bị Kim chặt → 'cây đè'. Dậu Kim cộng hưởng Kim Vũ-Sát → quá cương → 'cầm đao'. Khi không có sát kị → cương khí được kiểm soát; có sát kị → cương khí bùng phát = bạo lực/tai nạn. Cách hóa giải = chuyển năng lượng cương sang nghề 'cương chính danh' (võ nghiệp) — đây là Xu Cát Tị Hung paradigm Trung Châu.",
            "vi_du_doi_song": "Người Mệnh Vũ-Sát Mão nếu lá số có nhiều sát kị → cẩn thận tai nạn ngoài trời (xe cộ, lũ lụt, sét, công trường). Người Mệnh Vũ-Sát Dậu + sát kị → tránh tranh chấp tài chính, hợp đồng phức tạp, dễ vướng kiện tụng hoặc xô xát. Nếu chuyển sang nghề công an, quân đội, an ninh → cương khí được kênh đúng → thành công.",
            "iron_rule_warning": "'Cây đè sét đánh' KHÔNG phải định mệnh — là cảnh báo xu hướng. Mệnh tạo Vũ-Sát + sát kị có thể tránh: cẩn thận đi xa khi thời tiết xấu, không vào nghề 'cương vô chính' (xã hội đen), chọn võ nghiệp lành mạnh. Iron Rule #6: paradigm 'đọc đồng dạng' để chủ động xoay chuyển vận.",
        },
    },
    {
        "question": "Vũ Khúc độc tọa Thìn/Tuất khác Vũ-Tham Sửu/Mùi ra sao? Khi nào nên/không nên võ nghiệp?",
        "subject_identifiers": {
            "sao_chinh": "Vũ Khúc",
            "cung": "Mệnh",
            "chi": ["Thìn", "Tuất"],
            "doi_cung": "Tham Lang",
            "similar_to": "Vũ Tham Sửu/Mùi",
            "cat_tinh": "nắm giữ tài chính",
            "sat_tinh": "tiểu thương",
            "tuyet_doi_khong_nen": "võ nghiệp (khi gặp sát tinh)",
            "aspect": "dinh_huong",
        },
        "from_category": "Vũ Khúc độc tọa Thìn/Tuất — Định hướng",
        "from_template": "Sao X độc tọa chi Y — đối cung Z, định hướng?",
        "source_quote": "Vũ Khúc độc tọa ở hai cung Thìn hoặc Tuất, gặp cát tinh cũng chủ về nắm giữ tài chính; gặp sát tinh, là tiểu thương, tuyệt đối không nên theo võ nghiệp. Vũ Khúc ở hai cung Thìn hoặc Tuất, ắt sẽ đối nhau với Tham Lang, tính chất tương tự như 'Vũ Khúc, Tham Lang' ở hai cung Sửu hoặc Mùi.",
        "commentary": {
            "han_viet": "Độc tọa = đứng một mình (không đồng cung sao chính). Nắm giữ tài chính = quản lý tiền (CFO, kế toán trưởng, treasurer). Tiểu thương = thương nhân nhỏ (chợ, cửa hàng nhỏ).",
            "viet_thuan": "Vũ Khúc độc tọa tại Thìn hoặc Tuất, đối cung luôn là Tham Lang (paradigm cố định trong an sao). Tính chất tương tự cách Vũ-Tham Sửu/Mùi nhưng yếu hơn vì 2 sao không cùng cung. Cát tinh → nắm tài chính (làm kế toán trưởng, quản lý tài sản). Sát tinh → tiểu thương (bán nhỏ, kinh doanh quy mô vừa). TUYỆT ĐỐI KHÔNG theo võ nghiệp vì độc tọa Vũ Khúc thiếu Thất Sát/Phá Quân hỗ trợ → võ nghiệp sẽ thất bại.",
            "nguyen_ly": "Thìn (Thổ ẩm) hoặc Tuất (Thổ khô) → Thổ sinh Kim Vũ Khúc, tăng tài lực. Đối cung Tham Lang → tham vọng kéo hành động Vũ Khúc. Nhưng vì 'độc tọa' (không sát/phá đồng cung) → cương khí không đủ cho võ nghiệp. Nghề phù hợp = 'quản lý tiền' (chuyên gia tài chính, kế toán).",
            "vi_du_doi_song": "Người Mệnh Vũ Khúc Thìn/Tuất + cát tinh thường làm CFO công ty lớn, kế toán trưởng, treasurer, kiểm toán cao cấp. Người Vũ Khúc Thìn/Tuất + sát tinh hợp kinh doanh nhỏ (cửa hàng vật liệu, đại lý phân phối quy mô vừa) — KHÔNG nên làm quân đội/cảnh sát (sẽ thất bại trong ngạch).",
            "iron_rule_warning": "'Tuyệt đối không nên theo võ nghiệp' là cảnh báo paradigm — không có nghĩa người Vũ Khúc Thìn/Tuất theo võ nghiệp sẽ chết. Là 'không phù hợp năng lượng' → khó tiến xa. Mệnh tạo nếu yêu thích võ nghiệp có thể chọn 'võ hành chính' (công tác hậu cần quân đội, IT quân sự) thay vì frontline.",
        },
    },
    {
        "question": "Vũ Khúc-Phá Quân Tỵ/Hợi + Hỏa Linh — cuộc đời ra sao?",
        "subject_identifiers": {
            "sao_chinh": ["Vũ Khúc", "Phá Quân"],
            "cung": "Mệnh",
            "chi": ["Tỵ", "Hợi"],
            "sao_dong_do": ["Hỏa Tinh", "Linh Tinh"],
            "to_nghiep": "phá",
            "tu_lap": "có cát hóa + sao cát → gánh vác trọng trách",
            "aspect": "tong_quan",
        },
        "from_category": "Vũ Khúc-Phá Quân Tỵ/Hợi — Phá tổ tự lập",
        "from_template": "Combo X-Y chi Z + sao W → cuộc đời ra sao?",
        "source_quote": "Vũ Khúc, Phá Quân ở hai cung Tị hoặc Hợi, đồng độ với Hỏa Tinh, Linh Tinh, chủ về phá tổ nghiệp mà tự lập. Được cát hóa và có sao cát, thì cuộc đời phần nhiều gánh vác trọng trách, hoặc thường gánh vác công việc quá mức.",
        "commentary": {
            "han_viet": "Phá tổ nghiệp = phá hỏng/mất sản nghiệp do cha mẹ để lại. Tự lập = tự mình xây dựng. Cát hóa = Hóa Lộc/Quyền/Khoa. Gánh vác trọng trách = nhận trách nhiệm lớn. Quá mức = vượt khả năng.",
            "viet_thuan": "Mệnh Vũ-Phá tại Tỵ/Hợi + Hỏa Tinh/Linh Tinh đồng độ → cuộc đời thường 'phá tổ nghiệp rồi tự lập' (mất hoặc không nhận tài sản cha mẹ, phải tự gây dựng từ con số 0). Nếu có Cát Hóa (Lộc/Quyền/Khoa) + sao cát phụ tá → cuộc đời gánh nhiều trọng trách (lãnh đạo, kéo cả gia đình + tổ chức), thường ôm việc quá mức.",
            "nguyen_ly": "Vũ Khúc Kim + Phá Quân Thủy → Kim sinh Thủy (Vũ Khúc tiêu hao). Tỵ Hỏa hoặc Hợi Thủy → Hỏa khắc Kim hoặc Thủy tăng Phá Quân. Hỏa-Linh thêm vào → cương khí + biến động cực mạnh → 'phá' năng lượng tích lũy (tổ nghiệp) buộc 'tự xây lại'. Nếu có Cát Hóa → năng lượng phá được hướng vào xây dựng đại nghiệp = 'gánh trọng trách'.",
            "vi_du_doi_song": "Người Mệnh Vũ-Phá Tỵ/Hợi + Hỏa Linh thường có chuyện gia đình lớn xảy ra trong tuổi trẻ (cha mẹ phá sản, ly hôn, mất sớm, hoặc tài sản gia đình bị tranh chấp). Sau đó họ tự gây dựng — thành công ở quy mô lớn (CEO startup, founder doanh nghiệp). Nhưng cũng dễ kiệt sức vì 'gánh quá mức' (lo cho mọi người).",
            "iron_rule_warning": "'Phá tổ nghiệp' KHÔNG có nghĩa cố ý phá hoại — là xu hướng năng lượng 'tài sản gia đình không bền'. Mệnh tạo có thể chuyển tích cực: chấp nhận 'không nhận thừa kế', tập trung tự xây — sẽ thành. 'Gánh quá mức' cũng cần ý thức nghỉ ngơi để không kiệt sức.",
        },
    },
]


def persist():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    book = "trung-chau-tu-vi-dau-so-2"

    # Mark pages 513-516 với section_id="5.1.4"
    for page in [513, 514, 515, 516]:
        conn.execute(
            "UPDATE chunks_v2 SET section_id='5.1.4' WHERE book_corpus_id=? AND page_start=?",
            (book, page),
        )

    # Use p513 as anchor
    existing = conn.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=513",
        (book,),
    ).fetchone()
    chunk_id = existing[0] if existing else None
    if chunk_id:
        conn.execute("UPDATE chunks_v2 SET text=?, section_id=? WHERE chunk_id=?",
                     (CHUNK_TEXT, "5.1.4", chunk_id))
        conn.execute("DELETE FROM atom_commentaries WHERE atom_id IN (SELECT atom_id FROM atomic_questions WHERE chunk_id=?)", (chunk_id,))
        conn.execute("DELETE FROM atomic_questions WHERE chunk_id=?", (chunk_id,))
        conn.execute("DELETE FROM chunk_classifications WHERE chunk_id=?", (chunk_id,))
        print(f"📦 Cleaned chunk_id={chunk_id} (p513) for section 5.1.4")
    conn.commit()

    cur = conn.execute(
        """INSERT INTO chunk_classifications
           (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
            format_style, knowledge_categories_json, extracted_by, confidence)
           VALUES (?, 1, 0, 1, 1, 1, 'nguyen_ly', ?, 'claude-inline', 0.95)""",
        (chunk_id, json.dumps([
            "Vũ Khúc — bản chất võ tinh, khác Thái Âm",
            "Vũ Khúc — cô quả với nữ mệnh",
            "Vũ-Phủ Tý/Ngọ — Ngọ ưu hơn, khí hòa hoãn",
            "Vũ-Tham Sửu/Mùi — Hỏa Linh hoạnh phát",
            "Vũ-Tướng Dần/Thân — chức phó, nghề hung sự",
            "Vũ-Sát Mão/Dậu — cây đè, vì tiền cầm đao",
            "Vũ Khúc độc tọa Thìn/Tuất — tài chính, không võ",
            "Vũ-Phá Tỵ/Hợi — phá tổ tự lập",
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
               VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, 0.95, 0, 'claude-inline', '5.1.4')""",
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

    print(f"✅ {n} atoms + {n} commentaries inserted for section 5.1.4")
    n_total = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE section_id='5.1.4'").fetchone()[0]
    print(f"📊 DB section 5.1.4: {n_total} atoms total")
    conn.close()


if __name__ == "__main__":
    print("═" * 70)
    print("EM TỰ XỬ LÝ Section 5.1.4 — Vũ Khúc ở Cung Mệnh")
    print("8 atoms (bản chất, cô quả nữ, Vũ-Phủ, Vũ-Tham, Vũ-Tướng, Vũ-Sát, độc tọa, Vũ-Phá)")
    print("═" * 70)
    persist()
