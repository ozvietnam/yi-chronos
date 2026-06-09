"""Inline atomize Section 5.1.3 — Thái Dương ở Cung Mệnh (p510-512)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

CHUNK_TEXT = """### 5.1.3. Thái Dương ở cung mệnh (thân)

Thái Dương ở cung mệnh nhập miếu hay lạc hãm có liên quan đến việc sinh vào ban ngày hay sinh vào ban đêm. Nếu nhập miếu mà còn là người sinh vào ban ngày thì rất tốt, người sinh vào ban đêm là kế đó; lạc hãm mà còn là người sinh vào ban đêm thì rất hung, người sinh vào ban ngày hơi giảm hung.

Thái Dương ở cung mệnh, cần phải lưu ý Cự Môn ở cung độ nào, và có sát tinh hay không. Nếu Cự Môn kèm có sát tinh, Thái Dương ở cung miếu vượng thì còn được; nếu Thái Dương ở cung lạc hãm (tệ nhất là người sinh vào ban đêm), ắt sẽ bị Cự Môn "ám".

Thái Dương ở cung mệnh còn cần phải lưu ý Thiên Lương ở cung độ nào. Cự Môn tính "ám", Thiên Lương tính "cô độc". Hễ Thái Dương nhập mệnh là đã bất lợi về người thân phái nam, nếu Thiên Lương lại có Cô Thần, Quả Tú, Thiên Hình và sát tinh đồng độ (ngại nhất là Hỏa Tinh, Linh Tinh), sẽ chủ về hình khắc.

Thái Dương lạc hãm, Hóa Kỵ, lại đồng độ với Hỏa Tinh, Linh Tinh: Người sinh vào ban đêm phần nhiều chủ về tuổi trẻ khắc cha, vẫn niên mất con. Nếu là người sinh vào ban ngày, lục thân phái nam cũng bất lợi.

Thái Dương ở cung Tý hoặc Ngọ: Nếu Hóa Lộc — Lúc trẻ bất lợi, trung niên có thể phát vượt lên. Nếu Hóa Kỵ — Thì tuổi trẻ tự lập, đến trung niên vẫn phải đề phòng phá tán, thất bại.

Thái Dương ở hai cung Sửu hoặc Mùi, cần phải gặp các sao phụ, tá cát tụ tập mới tốt; không gặp các sao phụ, tá, dù không có sát tinh cũng chỉ bình bình; nếu gặp sát tinh mà không có sao cát, thì không ổn định, sự nghiệp không có nền tảng, hoặc không giữ một nghề.

Thái Dương ở hai cung Dần hoặc Thân, thích hợp làm việc cho công ty, làm việc cho người khác; chỉ trong tình hình có các sao phụ, tá cát tụ tập, mà còn được "bách quan triều củng", mới chủ về có thể tự mình phát triển, nhưng sự nghiệp vẫn cần phải có sắc thái phục vụ. Phần nhiều chủ về bất lợi trong hôn nhân, nên kết hôn muộn. Dễ mắc bệnh tiểu đường, cổ nhân gọi là bệnh "tiêu khát".

Thái Dương ở hai cung Mão hoặc Dậu, trường hợp cấu tạo thành cách cục "Dương Lương Xương Lộc" là tốt nhất. Ở cung Mão thì thanh danh khá lớn; ở cung Dậu thì chỉ có thanh danh trong phạm vi nhất định.

"Thái Dương, Thiên Lương" thủ mệnh là người khéo nói chuyện, suy nghĩ cẩn thận; ở cung Dậu thì cường khí. Dù gặp cát tinh, cũng chủ về rời xa quê hương mà thành gia nghiệp, nhưng ắt sẽ được cha mẹ che chở.

Thái Dương ở cung Thìn, Thái Âm ở cung Tuất, là cục "Nhật Nguyệt toàn bích". Nếu gặp các sao phụ, tá cát và cát hóa, chủ về phú quý; nhưng nếu Thái Dương ở Tuất, Thái Âm ở cung Thìn, thì đây là "Nhật Nguyệt thất huy" (Thái Dương, Thái Âm mất sáng), chủ về cuộc đời biến thiên bất định."""


ATOMIC_DATA = [
    {
        "question": "Thái Dương ở Cung Mệnh nhập miếu vs lạc hãm — vai trò sinh ban ngày/ban đêm khác nhau ra sao?",
        "subject_identifiers": {
            "sao_chinh": "Thái Dương",
            "cung": "Mệnh",
            "trang_thai": ["nhập miếu", "lạc hãm"],
            "thoi_sinh": ["ban ngày", "ban đêm"],
            "aspect": "modifiers",
        },
        "from_category": "Thái Dương Mệnh — Miếu/hãm × sinh ngày/đêm",
        "from_template": "Sao X tại Mệnh — trạng thái Y × yếu tố Z?",
        "source_quote": "Thái Dương ở cung mệnh nhập miếu hay lạc hãm có liên quan đến việc sinh vào ban ngày hay sinh vào ban đêm. Nếu nhập miếu mà còn là người sinh vào ban ngày thì rất tốt, người sinh vào ban đêm là kế đó; lạc hãm mà còn là người sinh vào ban đêm thì rất hung, người sinh vào ban ngày hơi giảm hung.",
        "commentary": {
            "han_viet": "Nhập miếu = sao ở vị trí mạnh nhất (như vua ngồi đúng ngôi); Lạc hãm = sao ở vị trí yếu (như vua bị giam); Cát/hung phụ thuộc trạng thái sao tại cung đứng.",
            "viet_thuan": "Thái Dương là Mặt Trời — năng lượng dương cực mạnh. Nếu Thái Dương ở vị trí miếu (mạnh) trên lá số người sinh ban ngày → đúng giờ Mặt Trời chiếu sáng → CỰC TỐT. Người sinh ban đêm + Thái Dương nhập miếu → vẫn tốt nhưng kém hơn (Mặt Trời ban đêm không phát huy hết). Ngược lại Thái Dương lạc hãm (yếu) + sinh ban đêm → CỰC HUNG (Mặt Trời tắt lịm). Lạc hãm + sinh ban ngày → đỡ hơn 1 chút (ban ngày bù sáng).",
            "nguyen_ly": "Thái Dương thuộc Hỏa, Dương — bản chất là ánh sáng. Trạng thái sao trên lá số (miếu/hãm) tương tác với thời sinh (ngày/đêm tự nhiên) tạo 4 tổ hợp: miếu+ngày = ánh sáng đầy đủ (best); miếu+đêm = năng lượng vẫn có nhưng ít cộng hưởng; hãm+ngày = năng lượng thiếu nhưng bù từ tự nhiên; hãm+đêm = năng lượng thiếu + tự nhiên cũng tối (worst). Đây là cộng hưởng âm-dương: nội (lá số) phải hợp ngoại (tự nhiên).",
            "vi_du_doi_song": "Người Mệnh Thái Dương nhập miếu sinh giờ Ngọ/Mùi (giữa ngày) thường có tính cách rạng rỡ, được nhiều người yêu mến, dễ thành công trong nghề lãnh đạo/giáo viên/công chúng. Người Mệnh Thái Dương lạc hãm sinh giờ Tý/Sửu (đêm khuya) thường có nội tâm trầm, dễ mệt mỏi, cần nỗ lực gấp đôi để được công nhận.",
            "iron_rule_warning": "'Rất hung' KHÔNG có nghĩa định mệnh xấu. Là xu hướng năng lượng — mệnh tạo Thái Dương hãm + sinh đêm có thể chủ động: chọn nghề sáng đèn (truyền hình ban đêm), môi trường ánh sáng tốt, tu dưỡng tâm lý positive → cân bằng được.",
        },
    },
    {
        "question": "Thái Dương Mệnh tại sao bất lợi với người thân phái nam? Thiên Lương đồng độ với Cô Thần/Quả Tú/Thiên Hình thì sao?",
        "subject_identifiers": {
            "sao_chinh": "Thái Dương",
            "cung": "Mệnh",
            "anh_huong": "bất lợi nam thân (cha, chồng, con trai, anh em)",
            "sao_lien_quan": "Thiên Lương",
            "sao_dong_do_xau": ["Cô Thần", "Quả Tú", "Thiên Hình", "Hỏa Tinh", "Linh Tinh"],
            "aspect": "canh_bao",
        },
        "from_category": "Thái Dương Mệnh — Bất lợi nam thân + Thiên Lương xấu",
        "from_template": "Sao X tại Mệnh ảnh hưởng quan hệ Y? Sao Z xấu ra sao?",
        "source_quote": "Hễ Thái Dương nhập mệnh là đã bất lợi về người thân phái nam, nếu Thiên Lương lại có Cô Thần, Quả Tú, Thiên Hình và sát tinh đồng độ (ngại nhất là Hỏa Tinh, Linh Tinh), sẽ chủ về hình khắc.",
        "commentary": {
            "han_viet": "Hình khắc = bị tổn hại do người thân (đau, mất, xa cách). Cô Thần = sao cô độc; Quả Tú = sao ít bạn; Thiên Hình = sao hình phạt. Lục thân = 6 mối quan hệ thân (cha mẹ, vợ chồng, con cái, anh chị em).",
            "viet_thuan": "Người Mệnh Thái Dương thường gặp khó với người thân phái nam — cha xa cách, chồng/anh em có vấn đề, con trai khó nuôi. Nếu Thiên Lương trong lá số đồng cung với các sao 'cô độc' (Cô Thần, Quả Tú) và 'hình phạt' (Thiên Hình) + sát tinh (đặc biệt Hỏa-Linh) → khả năng tổn thương lục thân nam càng cao.",
            "nguyen_ly": "Thái Dương đại biểu cho 'người cha' / 'người nam quý' trong gia đình (vua, ông, bố). Khi Thái Dương ở Mệnh = trong người mệnh tạo đã có 'tia sáng cha' — đối ứng với cha bên ngoài bị 'lu mờ' (nguyên lý hỗ trợ-bù trừ). Thiên Lương là 'ấm tinh' (sao bảo bọc) — nếu Thiên Lương cũng yếu (gặp Cô-Quả-Hình) → ấm không còn → lục thân nam càng dễ hư.",
            "vi_du_doi_song": "Người Mệnh Thái Dương thường có ký ức cha thiếu vắng (cha mất sớm, cha bệnh, cha ly hôn, cha ở xa, cha lãnh đạm). Tự bản thân lại có thể trở thành 'người cha thay thế' trong gia đình. Nếu Thiên Lương + Cô-Quả-Hình → có thể mất anh em, mất con trai sớm. KHÔNG phải luôn xảy ra — phụ thuộc vào tổng thể lá số.",
            "iron_rule_warning": "'Hình khắc' không có nghĩa CHẮC CHẮN người thân chết. Là cảnh báo xu hướng — mệnh tạo biết trước có thể chủ động giữ liên lạc, quan tâm, hạn chế xung đột với người thân nam để giảm thiểu. Iron Rule #6.",
        },
    },
    {
        "question": "Thái Dương Sửu/Mùi điều kiện cát hung là gì?",
        "subject_identifiers": {
            "sao_chinh": "Thái Dương",
            "cung": "Mệnh",
            "chi": ["Sửu", "Mùi"],
            "can_co": "phụ tá cát tụ tập",
            "khong_co": "bình bình",
            "co_sat_tinh_khong_cat": "sự nghiệp không nền tảng",
            "aspect": "modifiers",
        },
        "from_category": "Thái Dương Sửu/Mùi — Điều kiện cát/hung",
        "from_template": "Sao X tại chi Y cần điều kiện gì?",
        "source_quote": "Thái Dương ở hai cung Sửu hoặc Mùi, cần phải gặp các sao phụ, tá cát tụ tập mới tốt; không gặp các sao phụ, tá, dù không có sát tinh cũng chỉ bình bình; nếu gặp sát tinh mà không có sao cát, thì không ổn định, sự nghiệp không có nền tảng, hoặc không giữ một nghề.",
        "commentary": {
            "han_viet": "Phụ tá cát = Tả Phụ + Hữu Bật + Văn Xương + Văn Khúc + Thiên Khôi + Thiên Việt. Tụ tập = nhiều sao cùng tụ. Bình bình = trung bình, không cao không thấp.",
            "viet_thuan": "Cung Sửu/Mùi là 'cung Thổ' — Thái Dương Hỏa ở đây bị Thổ làm 'tiết khí' (Hỏa sinh Thổ → Hỏa hao). Nên cần ĐỦ BỘ phụ tá cát (Tả-Hữu-Xương-Khúc-Khôi-Việt) để bù khí. Nếu chỉ có 1-2 sao phụ tá → vẫn 'bình bình' (không khá). Nếu có sát tinh mà không có cát → sự nghiệp không nền tảng, dễ đổi nghề liên tục.",
            "nguyen_ly": "Thái Dương Hỏa Dương tại Sửu (Thổ Âm) hoặc Mùi (Thổ Âm) → Hỏa sinh Thổ thì Hỏa tiêu hao. Cần năng lượng bù — đó là vai trò của BỘ phụ tá cát. Khác với Thái Dương tại Ngọ (Hỏa) → đồng khí, không cần bù.",
            "vi_du_doi_song": "Người Mệnh Thái Dương Sửu/Mùi nếu có đủ bộ Tả-Hữu-Xương-Khúc-Khôi-Việt thường thành đạt trong nghề cần 'ánh sáng + bộ phận hỗ trợ' (giáo viên đại học có đội ngũ TA, lãnh đạo có team mạnh, CEO có đồng sự giỏi). Cùng vị trí mà thiếu phụ tá + sát tinh → dễ làm nhiều nghề trong đời, không có 'nghề chính'.",
            "iron_rule_warning": "'Bình bình' không phải xấu — chỉ là không đột phá. Mệnh tạo Sửu/Mùi thiếu bộ vẫn có cuộc sống ổn định nếu chấp nhận quy mô vừa phải.",
        },
    },
    {
        "question": "Thái Dương Dần/Thân nên làm nghề gì? Tại sao bất lợi hôn nhân + bệnh tiểu đường?",
        "subject_identifiers": {
            "sao_chinh": "Thái Dương",
            "cung": "Mệnh",
            "chi": ["Dần", "Thân"],
            "nghe_phu_hop": ["công ty", "phục vụ", "làm cho người khác"],
            "canh_bao_suc_khoe": "bệnh tiểu đường (tiêu khát)",
            "canh_bao_hon_nhan": "kết hôn muộn",
            "aspect": "dinh_huong",
        },
        "from_category": "Thái Dương Dần/Thân — Nghề + hôn nhân + sức khỏe",
        "from_template": "Sao X tại chi Y nên làm gì, tránh gì, sức khỏe?",
        "source_quote": "Thái Dương ở hai cung Dần hoặc Thân, thích hợp làm việc cho công ty, làm việc cho người khác; chỉ trong tình hình có các sao phụ, tá cát tụ tập, mà còn được 'bách quan triều củng', mới chủ về có thể tự mình phát triển. Phần nhiều chủ về bất lợi trong hôn nhân, nên kết hôn muộn. Dễ mắc bệnh tiểu đường, cổ nhân gọi là bệnh 'tiêu khát'.",
        "commentary": {
            "han_viet": "Tiêu khát = chữ Hán cổ chỉ bệnh tiểu đường (khát + tiêu nhiều). Bách quan triều củng = đủ bộ phụ tá vây quanh. Sắc thái phục vụ = work serves others (service-oriented).",
            "viet_thuan": "Mệnh Thái Dương Dần/Thân nên làm công ty/tổ chức (làm cho người khác) thay vì tự kinh doanh. Chỉ khi có đủ bộ phụ tá VÀ thêm 'bách quan triều củng' (vây quanh hỗ trợ) → mới phát triển độc lập được, nhưng vẫn cần 'sắc thái phục vụ' (sản phẩm/dịch vụ phục vụ cộng đồng). Hôn nhân thường trắc trở → nên kết hôn muộn. Dễ mắc tiểu đường (ăn nhiều, khát nước, mau đói).",
            "nguyen_ly": "Dần (Mộc) + Thân (Kim) là 2 cung trục tứ Mã (di động). Thái Dương Hỏa tại Dần Mộc → Mộc sinh Hỏa (vượng). Tại Thân Kim → Hỏa khắc Kim (chiến). Cả 2 đều mang tính 'biến động'. Hôn nhân cần ổn định → bất lợi. Tiểu đường = bệnh chuyển hóa đường, liên quan tỳ-tỳ + tâm-hỏa — Thái Dương Hỏa quá vượng → tiêu hao chất ngọt trong cơ thể.",
            "vi_du_doi_song": "Người Mệnh Thái Dương Dần thường làm tốt trong công ty lớn (sếp/CEO của tổ chức công), không hợp tự khởi nghiệp 1 mình. Người Mệnh Thái Dương Thân thường tốt nhất trong nghề service: tư vấn, dịch vụ, giáo dục. Cả 2 thường có vấn đề hôn nhân sớm (chia tay trong tuổi 20-25), kết hôn lại ở tuổi 30+. Cần kiểm tra đường máu định kỳ từ tuổi 30.",
            "iron_rule_warning": "Bệnh tiểu đường là 'xu hướng tiềm ẩn' theo paradigm, KHÔNG phải định mệnh. Mệnh tạo nhận thức được + chế độ ăn lành + vận động → hoàn toàn phòng tránh.",
        },
    },
    {
        "question": "Cách cục 'Dương Lương Xương Lộc' của Thái Dương Mão/Dậu là gì? Mão vs Dậu khác nhau ra sao?",
        "subject_identifiers": {
            "sao_chinh": "Thái Dương",
            "cung": "Mệnh",
            "chi": ["Mão", "Dậu"],
            "cach_cuc": "Dương Lương Xương Lộc",
            "sao_can_co": ["Thái Dương", "Thiên Lương", "Văn Xương", "Lộc Tồn hoặc Hóa Lộc"],
            "khac_biet": {"Mão": "thanh danh khá lớn", "Dậu": "thanh danh trong phạm vi nhất định"},
            "aspect": "modifiers",
        },
        "from_category": "Thái Dương Mão/Dậu — Cách Dương Lương Xương Lộc",
        "from_template": "Cách cục X ở chi Y vs chi Z khác nhau ra sao?",
        "source_quote": "Thái Dương ở hai cung Mão hoặc Dậu, trường hợp cấu tạo thành cách cục 'Dương Lương Xương Lộc' là tốt nhất. Ở cung Mão thì thanh danh khá lớn; ở cung Dậu thì chỉ có thanh danh trong phạm vi nhất định, công chúng ít người biết.",
        "commentary": {
            "han_viet": "Dương Lương Xương Lộc = 4 sao Thái Dương + Thiên Lương + Văn Xương + (Lộc Tồn hoặc Hóa Lộc). Thanh danh = danh tiếng. Cấu tạo thành = gather lại được.",
            "viet_thuan": "Cách 'Dương Lương Xương Lộc' là 1 trong cách quý của Tử Vi — yêu cầu 4 sao Thái Dương + Thiên Lương + Văn Xương + Lộc cùng kết hợp. Khi đủ 4 sao tại Mệnh Mão hoặc Dậu → mệnh tạo có 'thanh danh' (nổi tiếng + được kính trọng). Cung Mão → thanh danh LỚN (cả nước biết tới); cung Dậu → thanh danh GIỚI HẠN (cộng đồng nhỏ biết).",
            "nguyen_ly": "Mão thuộc Mộc Dương — đông phương rạng sáng (Mặt Trời mọc). Thái Dương tại Mão = Mặt Trời mới mọc → ánh sáng đi xa, thanh danh lan rộng. Dậu thuộc Kim Âm — tây phương Mặt Trời lặn (Thái Dương tại Dậu = Mặt Trời sắp lặn) → ánh sáng yếu, lan gần. Cùng cách cục nhưng vị trí Mặt Trời trong ngày khác → hiệu ứng khác.",
            "vi_du_doi_song": "Người Mệnh Thái Dương Mão + cách Dương Lương Xương Lộc thường thành đạt nổi tiếng quy mô quốc gia/quốc tế: chính khách lớn, nhà văn nổi tiếng, giáo sư đại học hàng đầu, doanh nhân được biết rộng rãi. Người Mệnh Thái Dương Dậu + cách này thường nổi tiếng trong lĩnh vực hẹp: chuyên gia ngành, leader địa phương, KOL trong cộng đồng chuyên biệt.",
            "iron_rule_warning": "'Thanh danh' là xu hướng năng lượng + cơ hội — mệnh tạo phải chủ động xây dựng (học tập, công việc, networking). Cách cục là 'điều kiện thuận', không phải 'đảm bảo thành công'.",
        },
    },
    {
        "question": "Thái Dương-Thiên Lương đồng cung có tính cách + định hướng gì? Cung Dậu khác Mão ra sao?",
        "subject_identifiers": {
            "sao_chinh": ["Thái Dương", "Thiên Lương"],
            "cung": "Mệnh",
            "tinh_cach": "khéo nói chuyện, suy nghĩ cẩn thận",
            "chi_dau_cuong_khi": "Dậu",
            "anh_huong": "rời xa quê hương thành gia nghiệp, được cha mẹ che chở",
            "aspect": "tong_quan",
        },
        "from_category": "Thái Dương-Thiên Lương — Tính cách + định hướng",
        "from_template": "Combo X-Y thủ mệnh — tính cách + định hướng?",
        "source_quote": "'Thái Dương, Thiên Lương' thủ mệnh là người khéo nói chuyện, suy nghĩ cẩn thận; ở cung Dậu thì cường khí. 'Thái Dương, Thiên Lương' dù gặp cát tinh, cũng chủ về rời xa quê hương mà thành gia nghiệp, nhưng ắt sẽ được cha mẹ che chở.",
        "commentary": {
            "han_viet": "Cường khí = khí lực mạnh, tính cách quyết liệt. Rời xa quê hương = di chuyển đi xa lập nghiệp. Cha mẹ che chở = được phụ ấm bảo trợ (dù xa).",
            "viet_thuan": "Người Mệnh Thái Dương + Thiên Lương khéo ăn nói, suy nghĩ kỹ lưỡng. Cung Dậu (tây) thêm cường khí — tính quyết liệt hơn. Cả 2 chi (Mão và Dậu) đều chủ về 'rời quê lập nghiệp' — di chuyển đi xa nhà gốc để thành công, NHƯNG vẫn được cha mẹ ủng hộ/giúp đỡ từ xa.",
            "nguyen_ly": "Thái Dương = uy nghi + tia sáng; Thiên Lương = ấm tinh + cô độc + 'lão'. 2 sao = 'lão thầy giáo' archetype (vừa cương vừa ôn). Cương + cẩn → khéo nói, suy nghĩ kỹ. Cô độc + ấm = cần di chuyển đi xa nhưng vẫn 'ấm' từ cha mẹ (paradox: rời quê nhưng vẫn được ấm).",
            "vi_du_doi_song": "Người Mệnh Dương-Lương thường là giáo viên giỏi, MC duyên dáng, nhà tư vấn được nghe theo. Họ thường rời quê đi du học, làm việc ở thành phố lớn/nước ngoài, nhưng vẫn giữ liên lạc thường xuyên với cha mẹ — không phải đoạn tuyệt. Cha mẹ thường gửi tiền, thăm con, hỗ trợ tinh thần.",
            "iron_rule_warning": "'Rời xa quê hương' không có nghĩa BUỘC phải di chuyển. Là xu hướng — mệnh tạo có thể chọn ở lại quê nếu môi trường + cơ hội cho phép, nhưng paradigm chỉ ra rằng di chuyển phù hợp hơn.",
        },
    },
    {
        "question": "Cách 'Nhật Nguyệt toàn bích' vs 'Nhật Nguyệt thất huy' khác nhau thế nào?",
        "subject_identifiers": {
            "sao_chinh": ["Thái Dương", "Thái Âm"],
            "cung": "Mệnh / Thân",
            "cach_cuc_cat": "Nhật Nguyệt toàn bích",
            "cach_cuc_hung": "Nhật Nguyệt thất huy",
            "vi_tri_cat": {"Thái Dương": "Thìn", "Thái Âm": "Tuất"},
            "vi_tri_hung": {"Thái Dương": "Tuất", "Thái Âm": "Thìn"},
            "aspect": "modifiers",
        },
        "from_category": "Nhật Nguyệt toàn bích vs thất huy — Đối lập",
        "from_template": "Cách cục X vs Y — phân biệt vị trí + ý nghĩa?",
        "source_quote": "Thái Dương ở cung Thìn, Thái Âm ở cung Tuất, là cục 'Nhật Nguyệt toàn bích'. Nếu gặp các sao phụ, tá cát và cát hóa, chủ về phú quý; nhưng nếu Thái Dương ở Tuất, Thái Âm ở cung Thìn, thì đây là 'Nhật Nguyệt thất huy' (Thái Dương, Thái Âm mất sáng), chủ về cuộc đời biến thiên bất định.",
        "commentary": {
            "han_viet": "Nhật = Mặt Trời = Thái Dương; Nguyệt = Mặt Trăng = Thái Âm. Toàn bích = trọn vẹn sáng (cả 2 đều sáng). Thất huy = mất sáng (cả 2 đều mất sáng). Phú quý = giàu sang. Biến thiên bất định = không ổn, luôn thay đổi.",
            "viet_thuan": "2 cách cục đối nhau qua vị trí Thái Dương-Thái Âm: 'Nhật Nguyệt toàn bích' = Thái Dương Thìn (đông nam, Mặt Trời mọc lên cao) + Thái Âm Tuất (tây bắc, Mặt Trăng tròn). 2 sao đều sáng tỏa → cách quý (cần thêm phụ tá cát + cát hóa để thành phú quý). 'Nhật Nguyệt thất huy' = Thái Dương Tuất (Mặt Trời lặn) + Thái Âm Thìn (Mặt Trăng mới sinh) → cả 2 đều yếu → cuộc đời bất định.",
            "nguyen_ly": "Thìn = vị trí Mặt Trời mọc lên cao (sáng dần); Tuất = vị trí Mặt Trời lặn (tối dần). Thái Âm ngược lại: Tuất = trăng vừa lên (sáng); Thìn = trăng vừa lặn (tối). Khi vị trí Thái Dương + Thái Âm = đối nhau theo 'chiều sáng' → Toàn bích. Đối nhau 'chiều tối' → Thất huy. Đây là paradigm vũ trụ luận: âm-dương cân bằng (toàn bích) vs âm-dương cùng yếu (thất huy).",
            "vi_du_doi_song": "Người Mệnh Nhật Nguyệt toàn bích + đủ phụ tá thường thành công cả 'mặt sáng' (sự nghiệp công khai) lẫn 'mặt tinh tế' (gia đình, cảm xúc, nội tâm). Người Mệnh Nhật Nguyệt thất huy thường có cuộc sống biến động: đổi nghề nhiều, quan hệ thay đổi, di chuyển nhiều, không có 'chỗ neo' lâu dài. Tâm trạng cũng dao động mạnh.",
            "iron_rule_warning": "'Biến thiên bất định' là xu hướng — KHÔNG phải định mệnh xấu. Một số người Nhật Nguyệt thất huy chọn nghề phù hợp với 'biến động' (du lịch, freelancer, nghệ sĩ lưu diễn) lại thành công lớn nhờ embrace được năng lượng. Iron Rule #6.",
        },
    },
]


def persist():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    book = "trung-chau-tu-vi-dau-so-2"

    # Mark pages 510-512 với section_id="5.1.3"
    for page in [510, 511, 512]:
        conn.execute(
            "UPDATE chunks_v2 SET section_id='5.1.3' WHERE book_corpus_id=? AND page_start=?",
            (book, page),
        )

    # Use chunk p510 as anchor for section 5.1.3
    existing = conn.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=510",
        (book,),
    ).fetchone()
    chunk_id = existing[0] if existing else None
    if chunk_id:
        conn.execute("UPDATE chunks_v2 SET text=?, section_id=? WHERE chunk_id=?",
                     (CHUNK_TEXT, "5.1.3", chunk_id))
        conn.execute("DELETE FROM atom_commentaries WHERE atom_id IN (SELECT atom_id FROM atomic_questions WHERE chunk_id=?)", (chunk_id,))
        conn.execute("DELETE FROM atomic_questions WHERE chunk_id=?", (chunk_id,))
        conn.execute("DELETE FROM chunk_classifications WHERE chunk_id=?", (chunk_id,))
        print(f"📦 Cleaned chunk_id={chunk_id} (p510) for section 5.1.3")
    conn.commit()

    cur = conn.execute(
        """INSERT INTO chunk_classifications
           (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
            format_style, knowledge_categories_json, extracted_by, confidence)
           VALUES (?, 1, 0, 1, 1, 1, 'nguyen_ly', ?, 'claude-inline', 0.95)""",
        (chunk_id, json.dumps([
            "Thái Dương Mệnh — miếu/hãm × sinh ngày/đêm",
            "Thái Dương Mệnh — bất lợi nam thân + Thiên Lương xấu",
            "Thái Dương Sửu/Mùi — cần phụ tá cát",
            "Thái Dương Dần/Thân — phục vụ + bệnh tiểu đường + hôn nhân muộn",
            "Thái Dương Mão/Dậu — cách Dương Lương Xương Lộc",
            "Thái Dương-Thiên Lương — khéo nói + rời quê + ấm cha mẹ",
            "Nhật Nguyệt toàn bích vs thất huy",
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
               VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, 0.95, 0, 'claude-inline', '5.1.3')""",
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

    print(f"✅ {n} atoms + {n} commentaries inserted for section 5.1.3")
    n_total = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE section_id='5.1.3'").fetchone()[0]
    print(f"📊 DB section 5.1.3: {n_total} atoms total")
    conn.close()


if __name__ == "__main__":
    print("═" * 70)
    print("EM TỰ XỬ LÝ Section 5.1.3 — Thái Dương ở Cung Mệnh")
    print("7 atoms (miếu/hãm, nam thân, Sửu/Mùi, Dần/Thân, Mão/Dậu, Dương-Lương, Nhật Nguyệt)")
    print("═" * 70)
    persist()
