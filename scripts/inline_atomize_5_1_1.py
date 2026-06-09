"""Inline atomize Section 5.1.1 — em (Claude) tự xử lý.

Anh chốt 2026-06-09: "việc quan trọng KHÔNG dùng minimal". LM Studio models nhỏ
(Qwen3-30b, GLM Z1, Gemma 4) FAIL test cơ bản — 2/3 sai ngũ hành Tử Vi.

→ Em CHÍNH LÀ LLM đang chạy. Em đọc chunk + sinh atomic + 4-layer commentary trực tiếp.

Section 5.1.1 — Tử Vi ở Cung Mệnh (trang p503-505 Trung Châu Q2).
Em sinh atoms grounded từ TEXT THỰC, KHÔNG bịa.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


# ═══════════════════════════════════════════════════════════════════
# CHUNK p503 — Section 5.1.1 mở đầu (Tử Vi độc tọa Tý/Ngọ + Tử-Phá)
# ═══════════════════════════════════════════════════════════════════
CHUNK_503_TEXT = """## 5.1. Cung Mệnh (Thân)

### 5.1.1. Tử Vi ở cung mệnh (thân)

Tử Vi độc tọa ở hai cung Tý hoặc Ngọ, nếu là trường hợp "bách quan triều củng" thì ưa đến đại hạn hay lưu niên được Hóa Lộc, Hóa Quyền, Hóa Khoa. Nếu Tử Vi Hóa Quyền hoặc Hóa Khoa ở nguyên cục mà không có "bách quan triều củng", thì ưa đến đại hạn hoặc lưu niên có các sao Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt, Tả Phụ, Hữu Bật hội hợp.

Nếu nguyên cục vốn là cách cục "tại địa cô quân", đến niên hạn dù được Hóa Lộc, Hóa Quyền, Hóa Khoa, thì cát lợi cũng nhỏ, e rằng chỉ là nhất thời đắc ý. Nếu nguyên cục vốn là cách cục "vô đạo cô quân", lại đến niên hạn có các sao sát, kỵ tụ tập, thường chủ về tai họa, mà phần nhiều là tự chuốc lấy.

Phàm là Tử Vi tọa mệnh đều ưa đến cung hạn Thiên Phủ hay Thiên Tướng tọa thủ, ưa nhất là cung hạn Tử Vi độc tọa ở Tý hoặc Ngọ.

Tử Vi độc tọa ở hai cung Tý hoặc Ngọ ưa có Lộc Tồn đồng độ. Có điều, Tử Vi "tại dã cô quân" thì phần nhiều chủ về ích khí, hay nghi kỵ. Đến niên hạn có các sao sát, kỵ, hình cùng chiếu, phần nhiều chủ về oán trách, thị phi, thường còn gây nên họa kiện tụng.

Phàm là Tử Vi tọa mệnh đều không ưa đến cung hạn Thiên Cơ hay Thiên Lương tọa thủ, có Cự Môn đồng độ, gặp Hóa Kỵ thì càng tệ. Tử Vi độc tọa ở hai cung Tý hoặc Ngọ, gặp cung hạn Thiên Cơ sẽ chủ về phá tán, thất bại; gặp cung hạn Thiên Lương sẽ chủ về có tai ách, nhưng tai ách chỉ là một phen hú vía; gặp cung hạn Cự Môn sẽ chủ về gặp rắc rối khó xử về tình cảm, có cát hóa thì có thể giải quyết, gặp các sao sát, hình thì ứng nghiệm.

"Tử Vi, Phá Quân" thủ mệnh, tối kỵ là cách cục "tại dã cô quân", đến vận hạn Thiên Cơ, Thiên Lương, hay Cự Môn, thường là vận trình có tính then chốt của cuộc đời. Nếu cung hạn gặp các sao sát, kỵ, hình hội chiếu, chủ về dễ xảy ra sự cố, thường có thể ảnh hưởng đến cả cuộc đời; cũng không nên đến niên hạn Thái Dương Hóa Kỵ, thường dẫn đến thị phi, oán trách."""


# ═══════════════════════════════════════════════════════════════════
# EM (Claude) SINH ATOMIC Q + COMMENTARY 4 LỚP từ chunk
# Grounded từ TEXT THỰC, paradigm Iron Rule #6, knowledge của Claude
# ═══════════════════════════════════════════════════════════════════

ATOMIC_DATA = [
    {
        # Atom 1: Bách quan triều củng → niên hạn nào cát
        "question": "Tử Vi độc tọa Tý/Ngọ trong cách 'bách quan triều củng' ưa đến đại hạn hay lưu niên nào?",
        "subject_identifiers": {
            "sao_chinh": "Tử Vi",
            "cung": "Mệnh",
            "chi": ["Tý", "Ngọ"],
            "variant": "Tử Vi độc tọa",
            "cach_cuc": "bách quan triều củng",
            "aspect": "timing_dai_van",
        },
        "from_category": "Tử Vi Mệnh — Bách quan triều củng + niên hạn cát",
        "from_template": "Cách cục X tại Mệnh thì ưa niên hạn nào?",
        "source_quote": "Tử Vi độc tọa ở hai cung Tý hoặc Ngọ, nếu là trường hợp 'bách quan triều củng' thì ưa đến đại hạn hay lưu niên được Hóa Lộc, Hóa Quyền, Hóa Khoa.",
        "commentary": {
            "han_viet": "Bách quan = 100 quan lại; triều củng = chầu vây quanh. Bách quan triều củng = Mệnh có Tử Vi + đủ bộ Lộc Tồn, Thiên Mã, Văn Xương, Văn Khúc, Tả Phụ, Hữu Bật, Khôi Việt hội hợp — như vua được trăm quan vây quanh.",
            "viet_thuan": "Khi Tử Vi tại Mệnh (cung Tý hoặc Ngọ) có đủ sao phụ tá vây quanh (gọi là cách 'bách quan triều củng'), mệnh tạo sẽ phát huy mạnh nhất khi gặp đại vận/lưu niên có Hóa Lộc (sao tài lộc), Hóa Quyền (sao quyền lực), Hóa Khoa (sao danh tiếng). Đây là cách cao quý nhất của Tử Vi.",
            "nguyen_ly": "Tử Vi thuộc Thổ, Âm — là Đế tinh trung tâm. Một mình Tử Vi như vua đơn độc, cần được vây quanh bởi tá tinh (phụ tinh hỗ trợ). Khi đủ bộ → khí năng đầy đủ → niên hạn có thêm Tứ Hóa cát (Lộc/Quyền/Khoa) sẽ làm phát huy tối đa. Thiếu bộ → khí năng hư rỗng → cát hóa cũng không phát hết.",
            "vi_du_doi_song": "Một người Mệnh Tử Vi tại Tý hoặc Ngọ với bộ phụ tinh đầy đủ thường có dáng vẻ uy nghi, được nhiều người quý mến, giúp đỡ. Khi đến giai đoạn vận lớn (đại vận 10 năm) gặp Hóa Lộc/Quyền/Khoa — đây là thời điểm họ phát triển sự nghiệp + danh tiếng + tài chính cao nhất trong đời. KHÔNG có nghĩa chắc chắn giàu sang — phản chiếu xu hướng năng lượng vũ trụ thuận lợi cho phát huy bản chất Tử Vi.",
            "iron_rule_warning": "Đoạn này KHÔNG nói chắc chắn người Tử Vi Mệnh sẽ giàu hay quyền lực — chỉ phản chiếu rằng KHI cấu hình lá số có 'bách quan triều củng' THÌ niên hạn có Tứ Hóa cát là cơ hội phát huy. Xu hướng vũ trụ, không phán cát/hung cứng. Iron Rule #6 — đọc đồng dạng.",
        },
    },
    {
        # Atom 2: Tử Vi Hóa Quyền/Khoa không có bách quan → cần sao phụ
        "question": "Tử Vi Hóa Quyền hay Hóa Khoa ở nguyên cục mà không có 'bách quan triều củng' thì ưa đến niên hạn nào?",
        "subject_identifiers": {
            "sao_chinh": "Tử Vi",
            "cung": "Mệnh",
            "hoa": ["Hóa Quyền", "Hóa Khoa"],
            "thieu": "bách quan triều củng",
            "phu_tinh_can": ["Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật"],
            "aspect": "timing_dai_van",
        },
        "from_category": "Tử Vi Hóa cát thiếu bộ — bổ sung niên hạn",
        "from_template": "Tử Vi Hóa cát thiếu bộ phụ tá → niên hạn nào bổ sung?",
        "source_quote": "Nếu Tử Vi Hóa Quyền hoặc Hóa Khoa ở nguyên cục mà không có 'bách quan triều củng', thì ưa đến đại hạn hoặc lưu niên có các sao Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt, Tả Phụ, Hữu Bật hội hợp.",
        "commentary": {
            "han_viet": "Hóa Quyền = sao biến hóa thành quyền lực; Hóa Khoa = sao biến hóa thành khoa giáp/danh tiếng. Văn Xương + Văn Khúc = bộ Văn tinh; Thiên Khôi + Thiên Việt = bộ Khôi Việt quý nhân; Tả Phụ + Hữu Bật = bộ phụ tá. Đây là 6 sao quan trọng vây Tử Vi.",
            "viet_thuan": "Nếu Tử Vi tại Mệnh đã có Hóa Quyền hoặc Hóa Khoa nhưng thiếu bộ phụ tá vây quanh, thì niên hạn nào có Văn Xương Văn Khúc (sao trí tuệ/văn chương), Thiên Khôi Thiên Việt (quý nhân giúp đỡ), Tả Phụ Hữu Bật (cộng sự đắc lực) hội hợp — đó là lúc bù khuyết, mệnh tạo sẽ phát huy được sức mạnh của Hóa Quyền/Khoa.",
            "nguyen_ly": "Tử Vi cần BỘ — không chỉ có Hóa cát đơn lẻ. Hóa Quyền/Khoa chỉ là 'phẩm chất' bên trong, cần 'người chung quanh' (phụ tinh) hỗ trợ thì mới biểu hiện ra được. Niên hạn cung cấp cái thiếu — nguyên lý 'cộng hưởng năng lượng'.",
            "vi_du_doi_song": "Người Tử Vi Hóa Quyền tại Mệnh là người có năng lực lãnh đạo bẩm sinh nhưng nếu thiếu bộ phụ tinh thì khó được nhìn nhận. Vào năm gặp Văn Xương/Văn Khúc hội (vd. năm thi cử, năm có cơ hội học hỏi), năng lực đó được thể hiện qua trí tuệ + văn chương. Vào năm gặp Khôi Việt (năm gặp quý nhân, được đề bạt), năng lực được nâng đỡ. Vào năm gặp Tả Hữu (có cộng sự giỏi), năng lực được nhân lên.",
            "iron_rule_warning": "Niên hạn 'ưa' không có nghĩa 'chắc chắn tốt'. Đây là điều kiện cần để tiềm năng được kích hoạt, không phải lời hứa thành công.",
        },
    },
    {
        # Atom 3: Tại địa cô quân vs vô đạo cô quân
        "question": "Phân biệt cách cục 'tại địa cô quân' và 'vô đạo cô quân' của Tử Vi như thế nào?",
        "subject_identifiers": {
            "sao_chinh": "Tử Vi",
            "cach_cuc": ["tại địa cô quân", "vô đạo cô quân"],
            "aspect": "modifiers",
        },
        "from_category": "Tử Vi Mệnh — Phân biệt 2 loại cô quân",
        "from_template": "Phân biệt các loại cô quân của Tử Vi?",
        "source_quote": "Nếu nguyên cục vốn là cách cục 'tại địa cô quân', đến niên hạn dù được Hóa Lộc, Hóa Quyền, Hóa Khoa, thì cát lợi cũng nhỏ, e rằng chỉ là nhất thời đắc ý. Nếu nguyên cục vốn là cách cục 'vô đạo cô quân', lại đến niên hạn có các sao sát, kỵ tụ tập, thường chủ về tai họa.",
        "commentary": {
            "han_viet": "Cô quân = vua đơn độc. Tại địa = đứng trên đất (vẫn có thực quyền nhưng cô độc); Vô đạo = không có đường đi (mất phương hướng, ác hóa); Tại dã = ở chỗ hoang dã (xa kinh đô, không phụ tá). 3 mức độ cô quân khác nhau.",
            "viet_thuan": "Tử Vi cần phụ tinh vây quanh để phát huy 'đế khí'. Nếu thiếu, có 3 dạng cô quân: 'Tại địa cô quân' nhẹ nhất (vẫn có Lộc Tồn hoặc 1-2 phụ tinh), 'Tại dã cô quân' nặng hơn (hoàn toàn thiếu phụ tinh), 'Vô đạo cô quân' nặng nhất (thiếu phụ tinh + gặp sát kỵ hình). Mức độ cô quân quyết định cách niên hạn sau này tác động.",
            "nguyen_ly": "Đế tinh không phụ tá → mất nội lực vận hành. Tại địa = còn đất đứng (còn cơ hội); Tại dã = lưu lạc (cơ hội nhỏ); Vô đạo = lệch hướng + sát kỵ ác hóa (tự chuốc tai họa). Càng cô độc, càng dễ tự ý quyết định sai → 'tự chuốc lấy' tai họa = paradigm Trung Châu emphasis Xu Cát Tị Hung (hậu thiên chủ động xoay chuyển).",
            "vi_du_doi_song": "Một người Tử Vi Mệnh không có bộ phụ tinh, khi quyết định lớn (đầu tư, kết hôn, đổi nghề) thường tự quyết một mình, không hỏi ý kiến — đây là biểu hiện 'cô quân'. Mức nhẹ ('tại địa'): vẫn nghe lời khuyên một số trường hợp. Mức nặng ('vô đạo'): cứng đầu, nóng nảy ra quyết định, không lắng nghe → tự chuốc rắc rối trong vận hạn xấu.",
            "iron_rule_warning": "Sách dùng 'thường chủ về tai họa' — KHÔNG phải 'chắc chắn tai họa'. Đây là xu hướng, không phải định mệnh. Mệnh tạo Vô đạo cô quân nếu sớm nhận thức + tu dưỡng (Xu Cát Tị Hung paradigm Trung Châu) hoàn toàn có thể tránh.",
        },
    },
    {
        # Atom 4: Tử Vi ưa Thiên Phủ/Thiên Tướng niên hạn
        "question": "Tại sao Tử Vi tọa mệnh đều ưa đến cung hạn Thiên Phủ hay Thiên Tướng tọa thủ?",
        "subject_identifiers": {
            "sao_chinh": "Tử Vi",
            "cung": "Mệnh",
            "nien_han_uu_tien": ["Thiên Phủ", "Thiên Tướng"],
            "aspect": "timing_dai_van",
        },
        "from_category": "Tử Vi Mệnh — Niên hạn Thiên Phủ/Tướng",
        "from_template": "Tại sao Tử Vi ưa đến niên hạn Thiên Phủ/Thiên Tướng?",
        "source_quote": "Phàm là Tử Vi tọa mệnh đều ưa đến cung hạn Thiên Phủ hay Thiên Tướng tọa thủ, ưa nhất là cung hạn Tử Vi độc tọa ở Tý hoặc Ngọ.",
        "commentary": {
            "han_viet": "Thiên Phủ = kho tiền (sao chủ tài/dự trữ); Thiên Tướng = quan ấn (sao chủ quyền/điều hành). Tử Vi gặp Phủ Tướng triều viên = vua có kho tiền + quan ấn = cách phú quý song toàn.",
            "viet_thuan": "Tử Vi là Đế tinh, cần Thiên Phủ làm kho và Thiên Tướng làm quan để cai trị. Khi đại vận hoặc lưu niên đi vào cung có Thiên Phủ hoặc Thiên Tướng → mệnh tạo Tử Vi được bổ sung tài lực + quyền lực — đây là vận tốt nhất.",
            "nguyen_ly": "Tam cách Tử-Phủ-Tướng là cấu trúc đầy đủ của 'triều đình' trong Tử Vi: Tử Vi (vua) + Thiên Phủ (kho tiền) + Thiên Tướng (quan ấn). Khi vận đi qua thành viên triều đình → tạo thành tam giác cộng hưởng. 'Ưa nhất' Tử Vi độc tọa Tý/Ngọ vì khi vận quay về Mệnh chính = chu kỳ vũ trụ hoàn thành 1 vòng.",
            "vi_du_doi_song": "Người Tử Vi Mệnh khi đến đại vận có Thiên Phủ thủ thường gặp cơ hội tài chính lớn (tiết kiệm, đầu tư, kế thừa). Khi đến đại vận có Thiên Tướng thủ thường được giao trọng trách điều hành (lên chức, làm leader). Mức độ tùy thuộc bộ phụ tinh + Tứ Hóa cụ thể trong đại vận đó.",
            "iron_rule_warning": "'Ưa' không bằng 'chắc chắn tốt'. Phải xem thêm sát kỵ hình của đại vận. Iron Rule #6: paradigm Trung Châu nhấn mạnh kết hợp Tứ Hóa + sao phụ + cảnh quan tam phương tứ chính, không chỉ một cung đơn.",
        },
    },
    {
        # Atom 5: Tử Vi ưa Lộc Tồn đồng độ
        "question": "Vì sao Tử Vi độc tọa Tý/Ngọ ưa có Lộc Tồn đồng độ?",
        "subject_identifiers": {
            "sao_chinh": "Tử Vi",
            "chi": ["Tý", "Ngọ"],
            "sao_dong_do_uu_tien": "Lộc Tồn",
            "aspect": "modifiers",
        },
        "from_category": "Tử Vi Mệnh — Lộc Tồn đồng độ",
        "from_template": "Vì sao Tử Vi ưa Lộc Tồn đồng độ?",
        "source_quote": "Tử Vi độc tọa ở hai cung Tý hoặc Ngọ ưa có Lộc Tồn đồng độ. Có điều, Tử Vi 'tại dã cô quân' thì phần nhiều chủ về ích khí, hay nghi kỵ.",
        "commentary": {
            "han_viet": "Lộc Tồn = sao tài lộc bền vững (khác Hóa Lộc — Hóa Lộc là tài lộc động, Lộc Tồn là tài lộc tĩnh). Ích khí = giữ khí (kiểm soát cảm xúc); nghi kỵ = đa nghi.",
            "viet_thuan": "Tử Vi rất ưa có Lộc Tồn đồng cung (cùng cung Mệnh) — Lộc Tồn mang ý nghĩa của cải bền vững, ổn định. Tử Vi (vua) + Lộc Tồn (kho lộc cố định) = nguyên cục giàu khí tài. Nhưng nếu Tử Vi vẫn 'tại dã cô quân' (thiếu phụ tinh khác), thì dù có Lộc Tồn vẫn mang tính cách hay nghi ngờ + giữ khí trong người.",
            "nguyen_ly": "Lộc Tồn có tính chất 'cố thủ' (giữ tài bền) — phù hợp với Đế tinh Tử Vi cần ổn định nội lực. Nhưng Lộc Tồn không phải phụ tinh vây quanh — không thay thế được 'bách quan'. Nên Tử Vi + Lộc Tồn vẫn có thể là 'tại dã cô quân' nếu thiếu Tả Hữu Xương Khúc Khôi Việt.",
            "vi_du_doi_song": "Người Mệnh Tử Vi tại Tý/Ngọ + Lộc Tồn thường có tài chính ổn định cả đời (không phá tán). Nhưng nếu thiếu bạn đồng hành (thiếu phụ tinh), họ thường cẩn trọng quá mức trong các mối quan hệ — kiểm soát cảm xúc rất kỹ, hay nghi ngờ động cơ người khác. Càng có nhiều thì càng giữ kỹ — chứ không phát.",
            "iron_rule_warning": "'Nghi kỵ' không phải xấu vĩnh viễn — đây là xu hướng tính cách cần ý thức để cân bằng. Iron Rule #6: lá số phản chiếu tendency, mệnh tạo có thể tu dưỡng để bớt nghi kỵ.",
        },
    },
    {
        # Atom 6: Tử-Phá thủ mệnh + cô quân kỵ Cơ/Lương/Cự
        "question": "Tử Vi-Phá Quân thủ mệnh trong cách 'tại dã cô quân' kỵ những vận hạn nào?",
        "subject_identifiers": {
            "sao_chinh": ["Tử Vi", "Phá Quân"],
            "combo": "Tử Vi + Phá Quân thủ mệnh",
            "cach_cuc": "tại dã cô quân",
            "nien_han_ky": ["Thiên Cơ", "Thiên Lương", "Cự Môn", "Thái Dương Hóa Kỵ"],
            "aspect": "timing_canh_bao",
        },
        "from_category": "Tử-Phá Mệnh — Cảnh báo vận hạn",
        "from_template": "Combo X-Y thủ mệnh + cách cục Z → kỵ vận hạn nào?",
        "source_quote": "'Tử Vi, Phá Quân' thủ mệnh, tối kỵ là cách cục 'tại dã cô quân', đến vận hạn Thiên Cơ, Thiên Lương, hay Cự Môn, thường là vận trình có tính then chốt của cuộc đời. Nếu cung hạn gặp các sao sát, kỵ, hình hội chiếu, chủ về dễ xảy ra sự cố, thường có thể ảnh hưởng đến cả cuộc đời; cũng không nên đến niên hạn Thái Dương Hóa Kỵ.",
        "commentary": {
            "han_viet": "Tử-Phá = Tử Vi đồng cung Phá Quân (combo lưỡng cực — Đế tinh + Phá tinh). Then chốt cuộc đời = bước ngoặt quan trọng. Thái Dương Hóa Kỵ = sao Thái Dương biến hóa thành Kỵ (thị phi, oán trách).",
            "viet_thuan": "Khi Tử Vi đồng cung Phá Quân thủ Mệnh + cách 'tại dã cô quân' (thiếu phụ tinh) → đây là cấu hình nhạy cảm. Đại vận hoặc lưu niên đi qua các cung Thiên Cơ, Thiên Lương, Cự Môn = bước ngoặt cuộc đời. Nếu vận đó gặp thêm sát/kỵ/hình → dễ xảy ra biến cố ảnh hưởng cả đời (mất việc, hôn nhân đổ vỡ, kiện tụng lớn). Cũng tránh năm Thái Dương Hóa Kỵ — dẫn đến thị phi, oán trách.",
            "nguyen_ly": "Tử-Phá là 'Đế chiêu Phá' — vừa muốn cai trị vừa muốn phá đổ → bản chất mâu thuẫn. Khi thiếu phụ tinh → mâu thuẫn không được tiết chế. Vận Thiên Cơ (động/đổi/biến) + Thiên Lương (ấm tinh nhưng cô khắc) + Cự Môn (thị phi/khẩu thiệt) đều là sao có tính 'biến động/lời tiếng' — kích hoạt mâu thuẫn Tử-Phá. Thái Dương Hóa Kỵ làm tăng ác khí oán trách.",
            "vi_du_doi_song": "Người Tử-Phá Mệnh không có bộ phụ tinh thường có cuộc đời biến động (đổi nghề nhiều lần, hôn nhân không ổn, ngộ chuyện thị phi). Vào năm vận đi qua cung Cự Môn — đặc biệt dễ vướng mâu thuẫn lời tiếng, kiện tụng, bị hiểu lầm. Vào năm Thái Dương Hóa Kỵ — bị mất uy tín, tiếng xấu lan. Cần đặc biệt cẩn trọng các thời điểm đó.",
            "iron_rule_warning": "Sách dùng 'thường', 'có thể', 'dễ xảy ra' — KHÔNG nói chắc chắn. Mệnh tạo Tử-Phá biết trước có thể chủ động tránh: không ra quyết định lớn vào năm Cự Môn, tránh tranh chấp vào năm Thái Dương Hóa Kỵ. Iron Rule #6 paradigm Trung Châu Xu Cát Tị Hung — hậu thiên hành động xoay chuyển vận.",
        },
    },
]


def persist_to_db():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")

    # Step 1: Create or update chunks_v2 for p503 with section_id="5.1.1"
    book = "trung-chau-tu-vi-dau-so-2"
    page = 503
    existing = conn.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=?",
        (book, page),
    ).fetchone()
    if existing:
        chunk_id = existing[0]
        conn.execute(
            "UPDATE chunks_v2 SET section_id=?, text=? WHERE chunk_id=?",
            ("5.1.1", CHUNK_503_TEXT, chunk_id),
        )
        print(f"📦 Updated chunk_id={chunk_id} (p503) → section_id=5.1.1")
    else:
        cur = conn.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, page_start, page_end, text, section_id)
               VALUES (?, ?, ?, ?, ?)""",
            (book, page, page, CHUNK_503_TEXT, "5.1.1"),
        )
        chunk_id = int(cur.lastrowid)
        print(f"📦 Inserted new chunk_id={chunk_id} (p503) section_id=5.1.1")
    conn.commit()

    # Step 2: Create chunk_classification
    cc_existing = conn.execute(
        "SELECT cc_id FROM chunk_classifications WHERE chunk_id=?",
        (chunk_id,),
    ).fetchone()
    if cc_existing:
        cc_id = cc_existing[0]
        # Clear old atoms for clean re-insert
        conn.execute("DELETE FROM atom_commentaries WHERE atom_id IN (SELECT atom_id FROM atomic_questions WHERE chunk_id=?)", (chunk_id,))
        conn.execute("DELETE FROM atomic_questions WHERE chunk_id=?", (chunk_id,))
        print(f"🧹 Cleared old atoms for chunk_id={chunk_id}")
    else:
        cur = conn.execute(
            """INSERT INTO chunk_classifications
               (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
                format_style, knowledge_categories_json, extracted_by, confidence)
               VALUES (?, 0, 0, 1, 1, 1, 'nguyen_ly', ?, 'claude-inline', 0.95)""",
            (chunk_id, json.dumps([
                "Tử Vi độc tọa Tý/Ngọ — bách quan triều củng + niên hạn",
                "Cô quân 3 loại (tại địa, tại dã, vô đạo)",
                "Tử Vi ưa Lộc Tồn đồng độ",
                "Tử Vi ưa Thiên Phủ/Thiên Tướng niên hạn",
                "Tử-Phá thủ mệnh + tại dã cô quân — cảnh báo vận hạn",
            ], ensure_ascii=False)),
        )
        cc_id = int(cur.lastrowid)
    conn.commit()

    # Step 3: Insert atoms + commentaries
    n_atoms = 0
    for atom_data in ATOMIC_DATA:
        cur = conn.execute(
            """INSERT INTO atomic_questions
               (chunk_id, cc_id, question_text, question_lang, from_category, from_template,
                subject_identifiers, source_quote, confidence, founder_verified,
                extracted_by, section_id)
               VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, 0.95, 0, 'claude-inline', '5.1.1')""",
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
        n_atoms += 1

        # Commentary 4 layers
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

    # Update chunks_v2.atom_q_str
    atom_q_str = "\n".join(a["question"] for a in ATOMIC_DATA)
    conn.execute("UPDATE chunks_v2 SET atom_q_str=? WHERE chunk_id=?", (atom_q_str, chunk_id))
    conn.commit()
    print(f"✅ Inserted {n_atoms} atoms + {n_atoms} commentaries (4 layers each)")

    # Verify
    n_atoms_db = conn.execute(
        "SELECT COUNT(*) FROM atomic_questions WHERE section_id='5.1.1'"
    ).fetchone()[0]
    n_comm_db = conn.execute(
        "SELECT COUNT(*) FROM atom_commentaries ac "
        "JOIN atomic_questions aq ON aq.atom_id=ac.atom_id "
        "WHERE aq.section_id='5.1.1'"
    ).fetchone()[0]
    print(f"\n📊 DB verify section 5.1.1:")
    print(f"   atoms: {n_atoms_db}")
    print(f"   commentaries: {n_comm_db}")
    conn.close()


if __name__ == "__main__":
    print("═" * 70)
    print("EM (Claude) TỰ XỬ LÝ Section 5.1.1 — Tử Vi ở Cung Mệnh")
    print("Anh chốt 2026-06-09: việc quan trọng KHÔNG dùng minimal")
    print("═" * 70)
    print()
    persist_to_db()
