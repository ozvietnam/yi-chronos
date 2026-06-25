"""PHA A — Trích định nghĩa CANON cho TOÀN BỘ vocabulary user-facing
của sản phẩm tình duyên (gieo duyên / hôn nhân nữ + nam mirror).

NGUỒN GROUND-TRUTH (thứ tự ưu tiên neo, chống drift):
  1. concept_dict  — engine.tu_vi.concept_dict.lookup(term) → {term,kind,definition,
                     first_page,occurrences}. 686 concept Q1 Tử Vi (Phú Thái Vi).
                     => dinh_nghia_canon CHO SAO / CUNG / HÓA Tử Vi.
  2. wiki concept_index (data/yi_wiki/wiki.sqlite3) — canonical_vi/canonical_zh/
     aliases/short_note/category/school. => short_note + nguồn cho Thập Thần
     (Bát Tự, school=tu_binh_ba_tu), Cô Thần/Quả Tú, đào hoa tinh, lý-thuật.
  3. passages_fts — text gốc sách (raw_text). => passages_trich (1-2 câu + page).

NGUYÊN TẮC NEO: mọi bản thuần-Việt phải DERIVE từ dinh_nghia_canon, GIỮ ĐỦ nét,
KHÔNG rơi nét, KHÔNG tự thêm nét. Mỗi term GẮN nguồn (page / passage_id). Thập
Thần không có trong concept_dict q1 → ground bằng wiki; thiếu hẳn → flag.

Output: engine/yi_lexicon/_vocab_canon.json
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from engine.tu_vi import concept_dict

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
WIKI = ROOT / "data/yi_wiki/wiki.sqlite3"
KNOW = ROOT / "engine/tinh_duyen/knowledge"
OUT = ROOT / "engine/yi_lexicon/_vocab_canon.json"

# ───────────────────────────────────────────────────────────────────────────
# 1) GOM TERM — tên Hán-Việt + Hán + loại, từ 5 nguồn user-facing
# ───────────────────────────────────────────────────────────────────────────
# (han_viet, han, loai, nguon_gom)  — loai ∈ sao|cung|thap_than|ly_thuat|can_chi|hoa
TERMS: list[tuple[str, str, str, str]] = []


def _add(hv, han, loai, src):
    TERMS.append((hv, han, loai, src))


def gom_terms():
    pt = json.loads((KNOW / "tuvi_phuthe.json").read_text())
    # 14 chính tinh phối ngẫu
    name_map = {
        "tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương",
        "vu_khuc": "Vũ Khúc", "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh",
        "thien_phu": "Thiên Phủ", "thai_am": "Thái Âm", "tham_lang": "Tham Lang",
        "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng", "thien_luong": "Thiên Lương",
        "that_sat": "Thất Sát", "pha_quan": "Phá Quân",
    }
    for k, v in pt["chinh_tinh_phu_the"].items():
        if k.startswith("_"):
            continue
        _add(name_map.get(k, k), v.get("ten_han", ""), "sao", "tuvi_phuthe.chinh_tinh_phu_the")
    # 7 đào hoa tinh
    dh_map = {
        "thien_dieu": "Thiên Diêu", "ham_tri": "Hàm Trì", "moc_duc": "Mộc Dục",
        "dai_hao": "Đại Hao", "hong_loan": "Hồng Loan", "thien_hi": "Thiên Hỉ",
        "xuong_khuc": "Xương Khúc",
    }
    han_dh = {
        "thien_dieu": "天姚", "ham_tri": "咸池", "moc_duc": "沐浴", "dai_hao": "大耗",
        "hong_loan": "红鸾", "thien_hi": "天喜", "xuong_khuc": "文昌文曲",
    }
    for k, v in pt["dao_hoa_tinh"].items():
        if k.startswith("_"):
            continue
        _add(dh_map.get(k, k), han_dh.get(k, ""), "sao", "tuvi_phuthe.dao_hoa_tinh")
    # 4 tứ hóa phu thê
    hoa_map = {"hoa_loc": "Hóa Lộc", "hoa_quyen": "Hóa Quyền", "hoa_khoa": "Hóa Khoa", "hoa_ky": "Hóa Kỵ"}
    han_hoa = {"hoa_loc": "化禄", "hoa_quyen": "化权", "hoa_khoa": "化科", "hoa_ky": "化忌"}
    for k in pt["tu_hoa_phu_the"]:
        if k.startswith("_"):
            continue
        _add(hoa_map.get(k, k), han_hoa.get(k, ""), "hoa", "tuvi_phuthe.tu_hoa_phu_the")
    # 6 sát tinh phu thê
    sat_map = {
        "kinh_duong": "Kình Dương", "da_la": "Đà La", "hoa_tinh": "Hỏa Tinh",
        "linh_tinh": "Linh Tinh", "dia_khong": "Địa Không", "dia_kiep": "Địa Kiếp",
    }
    han_sat = {
        "kinh_duong": "擎羊", "da_la": "陀罗", "hoa_tinh": "火星", "linh_tinh": "铃星",
        "dia_khong": "地空", "dia_kiep": "地劫",
    }
    for k in pt["sat_tinh_phu_the"]:
        if k.startswith("_"):
            continue
        _add(sat_map.get(k, k), han_sat.get(k, ""), "sao", "tuvi_phuthe.sat_tinh_phu_the")

    # plain_glossary.is_jargon (ten_sao + thap_than + ly_thuat + can_chi)
    pg = json.loads((KNOW / "plain_glossary.json").read_text())["is_jargon"]
    seen_hv = {t[0] for t in TERMS}
    for hv in pg["ten_sao"]:
        if hv not in seen_hv:
            _add(hv, "", "sao", "plain_glossary.is_jargon.ten_sao"); seen_hv.add(hv)
    # thập thần — mang Hán nếu biết
    tt_han = {
        "Chính Quan": "正官", "Thiên Quan": "偏官", "Quan Sát": "官杀", "Thất Sát": "七杀",
        "Thương Quan": "伤官", "Thực Thần": "食神", "食伤": "食伤", "Thực Thương": "食伤",
        "Chính Tài": "正财", "Thiên Tài": "偏财", "财": "财",
        "Chính Ấn": "正印", "Thiên Ấn": "偏印", "Ấn Tinh": "印", "ấn tinh": "印",
        "Tỷ Kiên": "比肩", "Kiếp Tài": "劫财", "Tỷ Kiếp": "比劫",
        "Chính Quan Thất Sát": "官杀", "官杀": "官杀",
    }
    for hv in pg["thap_than"]:
        if hv not in seen_hv:
            _add(hv, tt_han.get(hv, hv if _is_han(hv) else ""), "thap_than",
                 "plain_glossary.is_jargon.thap_than"); seen_hv.add(hv)
    for hv in pg["ly_thuat"]:
        if hv not in seen_hv:
            _add(hv, hv if _is_han(hv) else "", "ly_thuat",
                 "plain_glossary.is_jargon.ly_thuat"); seen_hv.add(hv)
    for hv in pg["can_chi"]:
        if hv not in seen_hv:
            _add(hv, "", "can_chi", "plain_glossary.is_jargon.can_chi"); seen_hv.add(hv)

    # gender_lens.py — thập thần phối ngẫu + khắc + Cô Thần/Quả Tú (đảm bảo có mặt)
    for hv, han in [("Cô Thần", "孤辰"), ("Quả Tú", "寡宿")]:
        if hv not in seen_hv:
            _add(hv, han, "thap_than", "gender_lens.co_than_qua_tu"); seen_hv.add(hv)
        else:  # đã có → đánh dấu Hán
            for i, t in enumerate(TERMS):
                if t[0] == hv and not t[1]:
                    TERMS[i] = (t[0], han, "thap_than", t[3] + "+gender_lens")


def _is_han(s: str) -> bool:
    return any("一" <= ch <= "鿿" for ch in s)


# ───────────────────────────────────────────────────────────────────────────
# Curated fallback — định nghĩa Tử Bình CHUẨN TỐI THIỂU cho Thập Thần + nét cấu
# trúc cho lý-thuật vốn không có concept (đại vận / cung / Tuần Triệt). Đây là
# nguồn cấp 4 (sau concept_dict / wiki concept_index / passages). GẮN nguồn rõ
# (đạo lý Tử Bình kinh điển / quy ước an sao Tử Vi) — KHÔNG phải "bịa".
# Mỗi entry GIỮ ĐỦ nét canon, không thêm nét không có cơ sở.
# ───────────────────────────────────────────────────────────────────────────
_CURATED_THAP_THAN = {
    # composite / alias — derive từ cặp đơn đã có nguồn wiki tu_binh_ba_tu
    "Quan Sát": ("官杀", "Gộp Chính Quan (正官) + Thất Sát (七杀) — nhóm thập thần KHẮC "
                 "Nhật chủ; ở nữ mệnh đại diện PHỐI NGẪU (chồng). Chính Quan = ràng buộc "
                 "chính đáng/danh phận; Thất Sát = áp lực mạnh/uy quyền."),
    "官杀": ("官杀", "Quan Sát — gộp Chính Quan + Thất Sát; thập thần khắc Nhật chủ, nữ "
             "mệnh = sao chồng."),
    "Chính Quan Thất Sát": ("官杀", "Chính Quan + Thất Sát = nhóm Quan Sát (官杀); khắc "
                            "Nhật chủ, nữ mệnh là sao phối ngẫu."),
    "Tỷ Kiếp": ("比劫", "Gộp Tỷ Kiên (比肩) + Kiếp Tài (劫财) — thập thần ĐỒNG loại với "
                "Nhật chủ; chủ anh em/bằng hữu/cạnh tranh. Ở nam mệnh, Tỷ Kiếp KHẮC Tài "
                "(财) nên là kẻ khắc vợ."),
    "食伤": ("食伤", "Gộp Thực Thần (食神) + Thương Quan (伤官) — thập thần do Nhật chủ "
             "SINH ra; chủ tài năng, biểu đạt, sáng tạo. Nữ mệnh Thương Quan khắc Chính "
             "Quan (sao chồng)."),
    "Thực Thương": ("食伤", "Thực Thần + Thương Quan = nhóm Thực Thương (食伤); Nhật chủ "
                    "sinh ra, chủ sáng tạo/biểu đạt; nữ mệnh khắc sao chồng."),
    "Thiên Quan": ("偏官", "Thiên Quan = tên khác của Thất Sát (七杀) khi đã có chế hóa; "
                   "khắc Nhật chủ khác âm dương, chủ uy quyền, áp lực, quyết đoán."),
    "Thiên Ấn": ("偏印", "Thiên Ấn (偏印, tục danh Kiêu Thần) — sinh Nhật chủ khác âm "
                 "dương; chủ học thuật lệch/tài lẻ, tư duy độc đáo nhưng dễ cô."),
    "Ấn Tinh": ("印", "Ấn (印) — gộp Chính Ấn + Thiên Ấn; thập thần SINH Nhật chủ, chủ "
                "che chở, học vấn, nương tựa; trong khắc-chế hôn nhân, Ấn chế Thương Quan."),
    "ấn tinh": ("印", "Ấn (印) — thập thần sinh Nhật chủ; chủ che chở, học vấn; Ấn chế "
                "Thương Quan trong cơ chế bảo vệ sao chồng."),
    "财": ("财", "Tài (财) — gộp Chính Tài + Thiên Tài; thập thần Nhật chủ KHẮC, chủ tiền "
           "của; ở nam mệnh đại diện PHỐI NGẪU (vợ)."),
}

# Biến thể chính tả → tên canonical trong concept_dict/wiki (tránh flag oan)
_ALIAS_NORM = {
    "Thiên Hỉ": "Thiên Hỷ",
    "Thiên Dao": "Thiên Diêu",
    "Tả Phù": "Tả Phụ",
}

# Cụm cách / idiom Hán trong plain_glossary (kết cấu nâng cao) — curated từ phú cổ
_CURATED_IDIOM = {
    "刑忌夹印": "Hình-Kỵ giáp Ấn — Thiên Hình + Hóa Kỵ kẹp Thiên Tướng (ấn tinh); kết cấu "
               "ép khiến người dễ mất chí / nhu nhược, cần giữ chính kiến.",
    "财荫夹印": "Tài-Ấm giáp Ấn — Hóa Lộc/Lộc Tồn + Thiên Lương (ấm) kẹp Thiên Tướng; "
               "kết cấu nâng đỡ, nhưng nếu không thuận cũng làm Thiên Tướng dựa dẫm.",
    "羊陀夹忌": "Kình-Đà giáp Kỵ — Kình Dương + Đà La kẹp một cung có Hóa Kỵ; kết cấu rất "
               "xấu, năm/vận đó cần giữ gìn.",
    "羊陀夹武曲": "Kình-Đà giáp Vũ Khúc — Kình + Đà kẹp Vũ Khúc (nhất là khi Vũ Khúc hóa "
                 "Kỵ); kết cấu cương khắc nặng, đại kỵ với hôn nhân.",
    "桃花犯主": "Đào hoa phạm chủ — Tham Lang (đào hoa) đồng cung Tử Vi (chủ tinh); sắc "
               "thái tình dục đậm, cần Thiên Hình/Không diệu để thành 'thanh bạch'.",
    "泛水桃花": "Phiếm thủy đào hoa — Tham Lang ở Tý gặp Kình Dương (hoặc ở Hợi gặp Đà La); "
               "cách đào hoa nặng, sức hút mạnh cần định hướng.",
    "风流采杖": "Phong lưu thải trượng — Tham Lang ở Dần gặp Đà La (hoặc hội Thiên Hình "
               "Kình Dương); cách đào hoa, phong lưu đa tình.",
    "红杏出墙": "Hồng hạnh xuất tường — cụm đào hoa (天姚沐浴咸池大耗) tụ ở cung Phu/Phúc cộng "
               "hôn nhân bất như ý; cổ nói dễ sinh tình ngoài hôn nhân — đọc là dấu hiệu "
               "cần chăm sóc quan hệ, KHÔNG phán định.",
}

_CURATED_LY_THUAT = {
    "đại vận": "Giai đoạn ~10 năm trong lá số (大運); mỗi đại vận lần lượt quản một cung, "
               "đọc cát-hung động theo thời. (Quy ước an sao Tử Vi Đẩu Số.)",
    "lưu niên": "Năm cụ thể đang xét (流年); chồng lên đại vận để định thời sự kiện.",
    "lưu nguyệt": "Tháng cụ thể đang xét (流月); tầng định thời nhỏ hơn lưu niên.",
    "tiểu hạn": "Vận trong năm (小限) — an theo tuổi, một tầng định thời song song lưu niên.",
    "cung Phu Thê": "Cung vợ/chồng trong 12 cung (夫妻宫) — mô tả phối ngẫu và quan hệ hôn nhân.",
    "cung Mệnh": "Cung gốc của lá số (命宫) — trục chính mô tả bản thân.",
    "cung Phúc": "Cung Phúc Đức (福德宫) — đời sống tinh thần, hưởng thụ, tâm tính.",
    "cung Tài": "Cung Tài Bạch (财帛宫) — tiền của, cách kiếm-giữ tiền.",
    "cung Quan": "Cung Quan Lộc / Sự Nghiệp (官禄宫) — công danh, sự nghiệp.",
    "Tuần": "Tuần Không (旬空) — một trục 'không' làm yếu/đình hoãn lực sao trong cung nó án ngữ.",
    "Triệt": "Triệt Lộ (截路) — trục 'chặn' làm sao trong cung bị cắt/đảo lực, tựa rào chắn.",
    "Tuần Triệt": "Hai trục Tuần Không + Triệt Lộ — đều làm gián đoạn/biến chất lực sao án ngữ.",
    "Sát Phá Lang": "Trục Thất Sát–Phá Quân–Tham Lang (杀破狼) — bộ ba chủ BIẾN ĐỘNG, "
                    "khai phá, thay cũ đổi mới.",
    "杀破狼": "Sát Phá Lang — Thất Sát + Phá Quân + Tham Lang; trục biến động, khai phá.",
    "cô quân": "Cô Quân (孤君) — Tử Vi thiếu Tả Phụ Hữu Bật phụ tá: vị chủ đứng một mình, dễ cô.",
    "bách quan triều củng": "Bách Quan Triều Củng (百官朝拱) — Tử Vi được nhiều cát tinh/phụ "
                            "tinh vây quanh trợ giúp, cách quý hiển.",
    "Bách Quan Triều Củng": "Bách Quan Triều Củng (百官朝拱) — Tử Vi được nhiều cát/phụ tinh "
                            "vây quanh, cách quý.",
    "Kình-Đà giáp": "Kình Dương + Đà La kẹp hai bên một cung (羊陀夹) — kết cấu ép, làm xấu "
                    "lực sao bị kẹp.",
    "Kình Đà giáp": "Kình Dương + Đà La kẹp hai bên một cung (羊陀夹) — kết cấu ép.",
    "trung tính": "Sắc thái không thiên cát cũng không thiên hung — phải xét bối cảnh sao hội tụ.",
    "đắc": "Sao đóng ở vị trí thuận, phát huy được lực (đắc địa).",
    "tường hòa": "Khí ôn hòa, an ổn (祥和) — trạng thái lành của sao như Thiên Phủ.",
    "chính tinh": "14 sao chính (chính diệu) — trục mô tả cốt lõi của một cung.",
    "chính diệu": "Cách gọi khác của chính tinh — 14 sao chính.",
    "phụ tinh": "Sao phụ trợ (Tả Phụ Hữu Bật Xương Khúc Khôi Việt…) — tăng/giảm lực chính tinh.",
    "tạp diệu": "Sao lẻ/tạp (天刑 天姚 大耗…) — đọc theo cụm, không phán độc lập.",
    "không diệu": "Địa Không + Địa Kiếp (空劫) — chủ trống trải, hao tổn; cũng chế hóa đào hoa.",
    "lưu Kình": "Kình Dương theo năm lưu (流羊) — sát cương xuất hiện ở năm đang xét.",
    "lưu Đà": "Đà La theo năm lưu (流陀) — sát dây dưa xuất hiện ở năm đang xét.",
    "lưu Lộc": "Lộc Tồn / Hóa Lộc theo năm lưu — lộc khí của năm đang xét.",
    "cương khắc": "Khí quá cứng dẫn tới xung khắc lục thân (刚克) — cần xét MỨC độ, không kết án.",
    "cô khắc": "Khuynh hướng cô độc/khó gần do sao cương liệt (孤克).",
    "cương liệt": "Tính cứng mạnh, quyết liệt (刚烈) — như Vũ Khúc, Thất Sát.",
    "sát cương": "Sát tinh mang khí cứng (Kình Dương) — chủ hình thương tranh chấp.",
    "sát hỏa": "Sát tinh thuộc hỏa (Hỏa Tinh, Linh Tinh) — chủ nóng gấp, biến cố nhanh.",
    "sát âm": "Sát tinh trầm/âm (Đà La) — chủ dây dưa, uất kết ngầm.",
    "gặp sát": "Hội/đồng cung với sát tinh — tăng sắc thái xung khắc, cần giữ gìn.",
    "hội sát": "Sát tinh chiếu tới từ tam phương tứ chính — như gặp sát.",
    "sát-kỵ": "Sát tinh cộng Hóa Kỵ — cụm tín hiệu cần lưu tâm nhất (không phải bản án).",
    "sát kỵ": "Sát tinh cộng Hóa Kỵ — cụm cần lưu tâm.",
    "trung cách": "Cách cục mức trung — không thượng cũng không hạ.",
    "thuộc hạ cách": "Cách cục mức thấp theo phú cổ — đọc lại theo bối cảnh, không kết án.",
    "đồng độ": "Hai sao cùng một cung (同度) — như đồng cung.",
    "đồng triền": "Hai sao cùng vận hành/đóng một cung (同躔).",
    "hội chiếu": "Sao chiếu tới một cung từ tam phương tứ chính (会照).",
    "giáp cung": "Hai cung kề hai bên kẹp vào cung giữa (夹宫) — ảnh hưởng cung bị kẹp.",
    "thân vượng": "Nhật chủ mạnh (Bát Tự) — đủ lực gánh Tài/Quan.",
    "thân nhược": "Nhật chủ yếu (Bát Tự) — cần Ấn/Tỷ trợ lực.",
    "Quan nhược": "Sao Quan (chồng, nữ mệnh) yếu lực — cần sinh trợ.",
    "Quan vượng": "Sao Quan mạnh lực.",
    "Tài thông quan": "Tài (财) làm cầu nối Thương Quan → Tài → Quan, hóa giải Thương khắc Quan.",
    "Ấn chế": "Ấn (印) khắc chế Thương Quan, bảo vệ sao Quan (chồng).",
    "thông quan": "Một hành/thập thần làm cầu nối hóa giải hai bên khắc nhau (通关).",
}


# ───────────────────────────────────────────────────────────────────────────
# 2) Lookup mỗi term qua concept_dict + wiki concept_index + passages_fts
# ───────────────────────────────────────────────────────────────────────────
def wiki_concept(conn, hv: str, han: str) -> dict | None:
    cur = conn.cursor()
    rows = []
    if hv:
        rows = cur.execute(
            "SELECT canonical_vi,canonical_zh,aliases,short_note,category,school,"
            "first_seen_corpus,first_seen_page FROM concept_index "
            "WHERE canonical_vi=? COLLATE NOCASE LIMIT 1", (hv,)).fetchall()
    if not rows and han:
        rows = cur.execute(
            "SELECT canonical_vi,canonical_zh,aliases,short_note,category,school,"
            "first_seen_corpus,first_seen_page FROM concept_index "
            "WHERE canonical_zh=? LIMIT 1", (han,)).fetchall()
    if not rows and han:
        rows = cur.execute(
            "SELECT canonical_vi,canonical_zh,aliases,short_note,category,school,"
            "first_seen_corpus,first_seen_page FROM concept_index "
            "WHERE aliases LIKE ? OR canonical_zh LIKE ? LIMIT 1",
            (f"%{han}%", f"%{han}%")).fetchall()
    if not rows:
        return None
    r = rows[0]
    return {
        "canonical_vi": r[0], "canonical_zh": r[1], "aliases": r[2],
        "short_note": (r[3] or "").strip(), "category": r[4], "school": r[5],
        "first_seen_corpus": r[6], "first_seen_page": r[7],
    }


def _han_in(raw: str, han: str) -> bool:
    """Hán xuất hiện trong raw, có chuẩn hoá vài biến thể giản↔phồn thường gặp."""
    if not han:
        return False
    variants = {han}
    for s, t in (("红", "紅"), ("鸾", "鸞"), ("贞", "貞"), ("贪", "貪"),
                 ("军", "軍"), ("罗", "羅"), ("铃", "鈴"), ("阴", "陰"),
                 ("阳", "陽"), ("机", "機"), ("门", "門"), ("禄", "祿"),
                 ("权", "權"), ("杀", "殺")):
        variants |= {v.replace(s, t) for v in list(variants)}
        variants |= {v.replace(t, s) for v in list(variants)}
    return any(v in raw for v in variants)


def _need_cross_confirm(hv: str, loai: str) -> bool:
    """True nếu term dễ khớp bừa → cần Hán cross-confirm. Sao tên riêng ≥2 âm tiết
    (Hồng Loan…) KHÔNG cần; thập thần / lý-thuật / can-chi / 1 âm tiết → cần."""
    if loai == "sao" and len(hv.split()) >= 2:
        return False
    return True


def passages_for(conn, hv: str, han: str, loai_hint: str = "") -> list[dict]:
    """Trích passage gốc — CHỈ giữ khi neo CHẮC để tránh nhiễu off-topic.

    Quy tắc chống nhiễu (term chung như 'Chính Quan', 'Ấn' khớp bừa corpus
    Mai Hoa/Kinh Dịch):
      • match Hán (han) → giữ (chính xác nhất).
      • match Hán-Việt → CHỈ giữ khi snippet CÓ chứa Hán form (cross-confirm),
        nếu term không có Hán thì yêu cầu Hán-Việt là cụm ≥2 âm tiết (riêng biệt).
    """
    cur = conn.cursor()
    out = []
    queries = []  # (q, is_han)
    has_han = bool(han and _is_han(han) and len(han) <= 4)
    if has_han:
        queries.append((han, True))
    if hv:
        queries.append((hv, False))
    seen_ids = set()
    for q, is_han in queries:
        try:
            rows = cur.execute(
                "SELECT p.passage_id,p.page_start,p.corpus_id,p.raw_text "
                "FROM passages_fts f JOIN passages p ON p.passage_id=f.rowid "
                "WHERE passages_fts MATCH ? LIMIT 6", (q,)).fetchall()
        except sqlite3.OperationalError:
            continue
        for pid, page, corpus, raw in rows:
            if pid in seen_ids:
                continue
            # Cross-confirm cho match Hán-Việt khi term là token chung (1 âm tiết hoặc
            # thập thần/lý-thuật Bát Tự dễ khớp bừa corpus Mai Hoa/Kinh Dịch).
            # Sao tên riêng ≥2 âm tiết (Hồng Loan, Thiên Tướng…) đủ phân biệt → giữ.
            if not is_han and _need_cross_confirm(hv, loai_hint) \
                    and not _han_in(raw, han):
                continue
            seen_ids.add(pid)
            snippet = _snippet(raw, han if has_han else hv)
            out.append({"passage_id": pid, "page": page, "corpus": corpus,
                        "trich": snippet, "match_q": q, "neo": "han" if is_han else "han_viet"})
            if len(out) >= 3:
                return out
    return out


def _snippet(raw: str, key: str, width: int = 90) -> str:
    raw = raw.strip()
    idx = raw.find(key) if key else -1
    if idx < 0:
        return raw[:width].replace("\n", " ").strip()
    start = max(0, idx - 20)
    end = min(len(raw), idx + width)
    seg = raw[start:end].replace("\n", " ").strip()
    return ("…" if start > 0 else "") + seg + ("…" if end < len(raw) else "")


def build():
    gom_terms()
    conn = sqlite3.connect(f"file:{WIKI}?mode=ro", uri=True)

    out_terms = []
    n_cd = n_wiki = n_curated = n_flag = 0
    seen = set()
    for hv, han, loai, src in TERMS:
        if hv in seen:
            continue
        seen.add(hv)

        lookup_hv = _ALIAS_NORM.get(hv, hv)
        cd = concept_dict.lookup(lookup_hv)
        wk = wiki_concept(conn, lookup_hv, han)
        ps = passages_for(conn, lookup_hv, han, loai)

        dinh_nghia_canon = ""
        canon_src = ""
        curated_used = False
        if cd and cd.get("definition"):
            dinh_nghia_canon = cd["definition"]
            canon_src = f"concept_dict:Q1 Phú Thái Vi tr.{cd.get('first_page')}"
            n_cd += 1
        elif wk and wk["short_note"]:
            dinh_nghia_canon = wk["short_note"]
            cp = wk.get("first_seen_corpus") or ""
            pg = wk.get("first_seen_page")
            canon_src = f"wiki concept_index:{cp}" + (f" tr.{pg}" if pg else "")
            n_wiki += 1
        elif hv in _CURATED_THAP_THAN:
            han2, defn = _CURATED_THAP_THAN[hv]
            if not han:
                han = han2
            dinh_nghia_canon = defn
            canon_src = "curated:định nghĩa Tử Bình chuẩn tối thiểu (派 tu_binh_ba_tu)"
            curated_used = True
            n_curated += 1
        elif hv in _CURATED_LY_THUAT:
            dinh_nghia_canon = _CURATED_LY_THUAT[hv]
            canon_src = "curated:quy ước an sao Tử Vi / đạo lý Tử Bình"
            curated_used = True
            n_curated += 1
        elif hv in _CURATED_IDIOM:
            dinh_nghia_canon = _CURATED_IDIOM[hv]
            canon_src = "curated:cụm cách Phú Thái Vi / Trung Châu phái (王亭之)"
            curated_used = True
            n_curated += 1

        flag = None
        if not dinh_nghia_canon:
            if loai == "thap_than":
                flag = "cần nguồn Bát Tự (Tử Bình) — chưa có trong concept_dict/wiki/curated"
            else:
                flag = "thiếu nguồn canon (concept_dict / wiki / curated)"
            n_flag += 1

        out_terms.append({
            "han_viet": hv,
            "han": han,
            "loai": loai,
            "nguon_gom": src,
            "co_concept_dict": bool(cd),
            "tu_curated": curated_used,
            "dinh_nghia_canon": dinh_nghia_canon,
            "canon_nguon": canon_src,
            "concept_dict": cd,  # {term,kind,definition,first_page,occurrences} | None
            "short_note": (wk or {}).get("short_note", "") or None,
            "wiki": ({
                "canonical_vi": wk["canonical_vi"], "canonical_zh": wk["canonical_zh"],
                "aliases": wk["aliases"], "category": wk["category"],
                "school": wk["school"], "first_seen_page": wk["first_seen_page"],
            } if wk else None),
            "passages_trich": ps,
            "flag": flag,
        })

    conn.close()

    doc = {
        "_meta": {
            "ten": "Bảng từ vựng CANON — sản phẩm tình duyên (gieo duyên + hôn nhân nam/nữ)",
            "muc_dich": "Neo định nghĩa CHUẨN cho mọi term user-facing, chống drift dịch "
                        "thuần-Việt. Mọi bản thuần-Việt phải DERIVE từ dinh_nghia_canon, "
                        "giữ đủ nét, không rơi/thêm nét. Gắn nguồn (concept_dict page / "
                        "wiki passage_id).",
            "nguon_ground_truth": [
                "1. concept_dict (engine.tu_vi.concept_dict) — 686 concept Q1 Tử Vi, "
                "DICT_PATH=data/yi_publishing/q1_tuvi/master/concepts_index.json",
                "2. wiki concept_index (data/yi_wiki/wiki.sqlite3) — short_note + school",
                "3. passages_fts — raw_text gốc sách (trích 1-3 câu)",
            ],
            "paradigm": "Iron Rule #4/#6/#8 — đọc đồng dạng, mệnh là ĐỘNG TỪ, không "
                        "predict; gender (chồng/vợ, 官杀/财) ở tầng product (gender_lens).",
            "nguon_gom_term": [
                "tuvi_phuthe.json (14 chính tinh + 7 đào hoa + 4 tứ hóa + 6 sát tinh)",
                "plain_glossary.json is_jargon (ten_sao + thap_than + ly_thuat + can_chi)",
                "gender_lens.py (官杀/财 phối ngẫu, khắc phu/thê, Cô Thần/Quả Tú)",
            ],
            "ngay_tao": "2026-06-25",
        },
        "thong_ke": {
            "tong_term": len(out_terms),
            "co_concept_dict": n_cd,
            "chi_wiki": n_wiki,
            "curated_tu_binh_quy_uoc": n_curated,
            "thieu_nguon_flag": n_flag,
        },
        "terms": out_terms,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2))
    return doc


if __name__ == "__main__":
    d = build()
    s = d["thong_ke"]
    print(json.dumps(s, ensure_ascii=False))
    print("\n=== 3 ví dụ ===")
    egs = [t for t in d["terms"] if t["dinh_nghia_canon"]][:3]
    for t in egs:
        ps = t["passages_trich"][0]["trich"] if t["passages_trich"] else "(không có passage)"
        print(f"\n• {t['han_viet']} ({t['han']}) [{t['loai']}]")
        print(f"  canon: {t['dinh_nghia_canon']}")
        print(f"  nguồn: {t['canon_nguon']}")
        print(f"  passage: {ps}")
    print("\n=== FLAGS (thiếu nguồn) ===")
    for t in d["terms"]:
        if t["flag"]:
            print(f"  [{t['loai']}] {t['han_viet']} — {t['flag']}")
