"""Lớp giới-tính-hoá DÙNG CHUNG cho tình duyên (Tử Bình + Tử Vi).

Mục tiêu: **Nữ = flagship đọc sâu** (giữ nguyên 女命骨髓赋 + Trích Thiên Tủy Ch.6),
**Nam = mirror ĐÚNG cơ học** — KHÔNG duplicate toàn bộ tri thức, chỉ ánh-xạ
(thập-thần phối ngẫu, cơ chế khắc thê, cô-thần/quả-tú, từ vựng) sang đối xứng nam.

CƠ HỌC GIỚI TÍNH (ground thật):
─────────────────────────────────────────────────────────────────────────────
SAO PHỐI NGẪU (Tử Bình thập thần):
  • NỮ → 官杀 (Quan Sát):  正官 Chính Quan = chồng chính · 七杀 Thất Sát = chồng
    mạnh / tình nhân. (Ngũ hành KHẮC nhật chủ.)
  • NAM → 财 (Tài):        正财 Chính Tài = vợ chính · 偏财 Thiên Tài = vợ lẽ /
    người tình. (Ngũ hành nhật chủ KHẮC.)

KHẮC PHỐI NGẪU + CHẾ HOÁ:
  • NỮ:  KẺ KHẮC = 伤官 Thương Quan (phụ: 食神 Thực Thần) khắc 官 (Quan).
         BỊ KHẮC = 正官 Chính Quan (官).
         CHẾ HOÁ = 印 Ấn khắc Thương · 财 Tài thông quan (Thương→Tài→Quan).
  • NAM:  KẺ KHẮC = 劫财 Kiếp Tài + 比肩 Tỷ Kiên (Tỷ Kiếp) khắc 财 (Tài).
          BỊ KHẮC = 正财 Chính Tài (财).
          CHẾ HOÁ = 食伤 Thực Thương hoá Tỷ Kiếp sinh Tài (比劫→食伤→财) ·
                    官杀 Quan Sát chế Tỷ Kiếp.

CÔ ĐƠN (thần sát):  NỮ → 寡宿 Quả Tú · NAM → 孤辰 Cô Thần.

CHUNG cả 2 giới: 日支 = cung phối ngẫu · đào hoa 子午卯酉 · cung Phu Thê Tử Vi
(chính tinh mô tả PHỐI NGẪU — nữ=chồng, nam=vợ) · phác hoạ = giới NGƯỢC user.
─────────────────────────────────────────────────────────────────────────────

⚠️ PARADIGM (Iron Rule #4/#6/#8): KHÔNG bói; mệnh là ĐỘNG TỪ; context-aware scrub.
Nữ = flagship đọc sâu; Nam = mirror ĐÚNG cơ học (财/khắc thê), KHÔNG nông hơn
nhưng KHÔNG BAO GIỜ phán 'tái hôn / khắc chồng' cho nam (term_map đảo hết).
"""
from __future__ import annotations

import re
from typing import Optional

__all__ = [
    "is_male",
    "is_female",
    "norm_gender",
    "phu_the_thap_than",
    "khac_phoi_ngau",
    "co_than_qua_tu",
    "term_map",
    "apply_gender",
    "apply_gender_clause_aware",
    "has_opposite_gender_marker",
    "phoi_ngau_label",
    "gioi_phoi_ngau",
    "cau_hoi_gender",
]


# ──────────────────────────────────────────────────────────────────────────
# Chuẩn hoá giới tính
# ──────────────────────────────────────────────────────────────────────────
_MALE_TOKENS = {"nam", "male", "m", "man", "trai", "boy", "ông", "anh"}
_FEMALE_TOKENS = {"nu", "nữ", "female", "f", "woman", "gái", "girl", "bà", "chị", "cô"}


def norm_gender(gender: Optional[str]) -> str:
    """Chuẩn hoá về 'nam' / 'nu'. Mặc định (None/lạ) → 'nu' (flagship)."""
    g = (gender or "").strip().lower()
    if g in _MALE_TOKENS:
        return "nam"
    return "nu"


def is_male(gender: Optional[str]) -> bool:
    return norm_gender(gender) == "nam"


def is_female(gender: Optional[str]) -> bool:
    return norm_gender(gender) == "nu"


# ──────────────────────────────────────────────────────────────────────────
# Thập thần phối ngẫu
# ──────────────────────────────────────────────────────────────────────────
def phu_the_thap_than(gender: Optional[str]) -> list[str]:
    """Thập thần đại diện PHỐI NGẪU.

    Nữ → ['Chính Quan', 'Thất Sát']  (官杀)
    Nam → ['Chính Tài', 'Thiên Tài'] (财)
    """
    if is_male(gender):
        return ["Chính Tài", "Thiên Tài"]
    return ["Chính Quan", "Thất Sát"]


def khac_phoi_ngau(gender: Optional[str]) -> dict:
    """Cơ chế khắc + chế hoá phối ngẫu, đối xứng theo giới.

    Trả dict:
      ke_khac:  thập thần KẺ KHẮC phối ngẫu (str chính, có hán + ghi chú phụ)
      bi_khac:  thập thần BỊ KHẮC (= sao phối ngẫu) (str)
      che_hoa:  list[str] đường chế hoá
      + key máy đọc: ke_khac_list / bi_khac_list / han
    """
    if is_male(gender):
        return {
            "ke_khac": "Tỷ Kiếp (劫财 Kiếp Tài + 比肩 Tỷ Kiên)",
            "bi_khac": "Chính Tài (财)",
            "che_hoa": [
                "Thực Thương hóa Tỷ Kiếp sinh Tài (比劫→食伤→财)",
                "Quan Sát chế Tỷ Kiếp (官杀 chế 比劫)",
            ],
            "ke_khac_list": ["Kiếp Tài", "Tỷ Kiên"],
            "bi_khac_list": ["Chính Tài", "Thiên Tài"],
            "han": {"ke_khac": "比劫", "bi_khac": "财"},
        }
    return {
        "ke_khac": "Thương Quan (伤官, phụ: 食神 Thực Thần)",
        "bi_khac": "Chính Quan (官)",
        "che_hoa": [
            "Ấn khắc Thương (印克伤官)",
            "Tài thông quan (财 thông Thương→Tài→Quan)",
        ],
        "ke_khac_list": ["Thương Quan", "Thực Thần"],
        "bi_khac_list": ["Chính Quan", "Thất Sát"],
        "han": {"ke_khac": "伤官", "bi_khac": "官"},
    }


def co_than_qua_tu(gender: Optional[str]) -> str:
    """Thần sát cô đơn theo giới: nữ → 'Quả Tú' · nam → 'Cô Thần'."""
    return "Cô Thần" if is_male(gender) else "Quả Tú"


# ──────────────────────────────────────────────────────────────────────────
# Term-map: nữ là CANONICAL, nam là biến thể (chỉ nam có map, nữ rỗng)
# ──────────────────────────────────────────────────────────────────────────
# Thứ tự khai báo = thứ tự ưu tiên thay (DÀI trước NGẮN để 'người chồng' không
# bị 'chồng' nuốt mất). apply_gender sort lại theo độ dài key giảm dần.
_MALE_TERM_MAP: dict[str, str] = {
    "người chồng": "người vợ",
    "người phụ nữ": "người đàn ông",
    "khắc chồng": "khắc vợ",
    "khắc phu": "khắc thê",
    "lấy chồng": "lấy vợ",
    "sao chồng": "sao vợ",
    "phu tinh": "thê tinh",
    "phụ nữ": "đàn ông",
    "đàn bà": "đàn ông",
    "chồng": "vợ",
    "官杀": "财",
}


def term_map(gender: Optional[str]) -> dict[str, str]:
    """dict ánh xạ từ-vựng nữ→nam. Nữ (canonical) → {} (rỗng, không đổi gì)."""
    if is_male(gender):
        return dict(_MALE_TERM_MAP)
    return {}


def _case_preserve(src_match: str, repl: str) -> str:
    """Giữ kiểu hoa/thường của cụm gốc khi thay (Chồng→Vợ, CHỒNG→VỢ)."""
    if src_match.isupper() and len(src_match) > 1:
        return repl.upper()
    if src_match[:1].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


def apply_gender(text: Optional[str], gender: Optional[str]) -> str:
    """Áp term_map lên text theo giới.

    - Nữ: trả NGUYÊN VĂN (canonical, flagship — KHÔNG đụng vào).
    - Nam: thay cụm theo term_map, DÀI-trước-NGẮN, case-insensitive,
      giữ kiểu hoa/thường của cụm gốc.
    """
    if text is None:
        return ""
    tm = term_map(gender)
    if not tm:
        return text
    out = text
    # DÀI trước NGẮN: 'người chồng' phải thay trước 'chồng'.
    for key in sorted(tm, key=len, reverse=True):
        repl = tm[key]
        # 官杀 / hán tự: không có word-boundary trong regex \b cho CJK → thay thẳng.
        if re.search(r"[A-Za-zÀ-ỹ]", key):
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            out = pattern.sub(lambda m, r=repl: _case_preserve(m.group(0), r), out)
        else:
            out = out.replace(key, repl)
    return out


# ──────────────────────────────────────────────────────────────────────────
# Clause-aware masculinization — KHÔNG đụng vào mệnh đề tagged-NỮ tường minh
# ──────────────────────────────────────────────────────────────────────────
# Dấu hiệu chủ ngữ mệnh đề là NỮ TƯỜNG MINH (source citation Tử Vi / 女命骨髓赋).
# Khi đọc cho NAM, các mệnh đề này là TRÍCH DẪN GỐC mô tả phái nữ — phải giữ
# NGUYÊN VĂN nữ, KHÔNG masculinize (nếu không → 'nữ nên lấy vợ' = vỡ nghĩa).
_FEMALE_MARKER = re.compile(
    r"\(\s*nữ[^)]*\)"          # '(nữ)', '(nữ mệnh)'
    r"|nữ\s+mệnh"               # 'nữ mệnh'
    r"|nữ\s+nên"               # 'nữ nên lấy chồng …'
    r"|女命",                   # 女命骨髓赋 …
    re.IGNORECASE,
)

# Tách mệnh đề: ngăn cách bằng ';' '。' hoặc xuống dòng. Giữ delimiter để ghép lại
# nguyên trạng (không nuốt dấu).
_CLAUSE_SPLIT = re.compile(r"([;；。\n]+)")


def has_opposite_gender_marker(text: Optional[str]) -> bool:
    """True nếu text chứa dấu hiệu chủ ngữ NỮ tường minh (source citation)."""
    if not text:
        return False
    return bool(_FEMALE_MARKER.search(text))


def apply_gender_clause_aware(text: Optional[str], gender: Optional[str]) -> str:
    """Như apply_gender nhưng BỎ QUA mệnh đề tagged-NỮ tường minh khi đọc NAM.

    Dùng cho block reconcile.tuvi_doc_bang (bảng tra Tử Vi) — text TRỘN: vừa có
    mệnh đề trung tính (mô tả cung Phu Thê → đảo sang vợ/财 cho nam ĐÚNG) vừa có
    mệnh đề TRÍCH DẪN GỐC phái nữ ('(nữ mệnh) → chồng là trụ cột', '女命骨髓赋',
    'nữ nên lấy chồng lớn tuổi'). Mệnh đề nữ tường minh = GIỮ NGUYÊN, chỉ đảo các
    mệnh đề còn lại. Nữ (flagship) → trả nguyên văn.
    """
    if text is None:
        return ""
    if not is_male(gender):
        return text
    parts = _CLAUSE_SPLIT.split(text)
    out = []
    for seg in parts:
        # delimiter segment (chỉ gồm ; 。 \n) → giữ nguyên
        if _CLAUSE_SPLIT.fullmatch(seg):
            out.append(seg)
        elif has_opposite_gender_marker(seg):
            out.append(seg)  # mệnh đề nữ tường minh: GIỮ NGUYÊN văn nữ
        else:
            out.append(apply_gender(seg, "nam"))
    return "".join(out)


# ──────────────────────────────────────────────────────────────────────────
# Nhãn phối ngẫu + giới của phối ngẫu (= giới NGƯỢC user)
# ──────────────────────────────────────────────────────────────────────────
def phoi_ngau_label(gender: Optional[str]) -> str:
    """Gọi phối ngẫu của user thế nào: nữ → 'chồng' · nam → 'vợ'."""
    return "vợ" if is_male(gender) else "chồng"


def gioi_phoi_ngau(gender: Optional[str]) -> str:
    """Giới của phối ngẫu = NGƯỢC user. Dùng cho phác hoạ chân dung.

    nữ → 'nam' (vẽ người chồng) · nam → 'nu' (vẽ người vợ).
    """
    return "nu" if is_male(gender) else "nam"


def cau_hoi_gender(cau_hoi_nu: str, gender: Optional[str]) -> str:
    """Sinh biến thể câu hỏi theo giới từ câu hỏi gốc (viết cho NỮ).

    Ví dụ: 'chồng thế nào' --nam--> 'vợ thế nào';
           'khắc chồng' --nam--> 'khắc vợ'.
    Nữ giữ nguyên.
    """
    return apply_gender(cau_hoi_nu, gender)
