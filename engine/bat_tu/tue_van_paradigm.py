"""Tuế Vận Paradigm (歲運論) — Trích Thiên Tủy Chương 28.

Paradigm Nhậm Thiết Tiều phân loại 4 quan hệ giữa Đại Vận và Lưu Niên (Tuế):

1. **CHIẾN** (戰) — khắc lẫn nhau
   - Vận khắc Tuế (vận phạt tuế) — VD: vận Bính năm Canh (Hỏa khắc Kim)
   - Tuế khắc Vận (tuế phạt vận) — VD: vận Canh năm Bính (Kim phạm Hỏa)
   - Quy tắc: hỉ thân ở Vận hay Tuế quyết định cát/hung

2. **XUNG** (沖) — đối lập 6 cặp chi (Tý-Ngọ, Sửu-Mùi, Dần-Thân, Mão-Dậu, Thìn-Tuất, Tỵ-Hợi)
   - Vận xung Tuế: Vận Tý + Tuế Ngọ → xung khử
   - Phụ thuộc đảng phái (chi nào nhiều hơn)

3. **HÒA** (和) — hợp ngũ hợp (Giáp-Kỷ, Ất-Canh, Bính-Tân, Đinh-Nhâm, Mậu-Quý)
   - Vận Ất + Tuế Canh → hợp hóa Kim
   - Cát khi hợp hóa thành Hỉ Thần

4. **TỐT/THẦN TƯƠNG ĐỒNG** (善/同) — cùng loại
   - Vận Canh + Tuế Thân = chi Lộc vượng (đồng hành)
   - Vận Canh + Tuế Tân = can trợ can (bạn bè)

⚠️ Iron Rule #4+6: Output là DỘNG LỰC KHÍ, không phải số phận tĩnh.
"""

from __future__ import annotations

from .constants import STEM_ELEMENT, BRANCH_ELEMENT


# 10 Thiên Can — ngũ hành
STEM_ORDER: list[str] = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

# 12 Địa Chi
BRANCH_ORDER: list[str] = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# 6 cặp Lục Xung
LUC_XUNG_PAIRS: set[frozenset] = {
    frozenset(["Tý", "Ngọ"]),
    frozenset(["Sửu", "Mùi"]),
    frozenset(["Dần", "Thân"]),
    frozenset(["Mão", "Dậu"]),
    frozenset(["Thìn", "Tuất"]),
    frozenset(["Tỵ", "Hợi"]),
}

# 5 cặp Ngũ Hợp Can
NGU_HOP_CAN: dict[frozenset, str] = {
    frozenset(["Giáp", "Kỷ"]): "thổ",
    frozenset(["Ất", "Canh"]): "kim",
    frozenset(["Bính", "Tân"]): "thủy",
    frozenset(["Đinh", "Nhâm"]): "mộc",
    frozenset(["Mậu", "Quý"]): "hỏa",
}


def _element_controls(a: str, b: str) -> bool:
    """Check a element controls (khắc) b."""
    pairs = [("mộc","thổ"),("thổ","thủy"),("thủy","hỏa"),("hỏa","kim"),("kim","mộc")]
    return (a.lower(), b.lower()) in pairs


def classify_van_tue(van_stem: str, van_branch: str, tue_stem: str, tue_branch: str) -> dict:
    """Phân loại quan hệ Đại Vận - Lưu Niên theo Trích Thiên Tủy Ch.28.

    Args:
        van_stem, van_branch: Đại Vận can chi
        tue_stem, tue_branch: Lưu Niên can chi

    Returns:
        dict {category, label, narrative}
    """
    van_stem_el = STEM_ELEMENT.get(van_stem, "").lower()
    tue_stem_el = STEM_ELEMENT.get(tue_stem, "").lower()

    relations = []

    # 1. CHIẾN — Stem khắc nhau
    if _element_controls(van_stem_el, tue_stem_el):
        relations.append({
            "type": "chien_van_khac_tue",
            "label": f"Vận phạt Tuế ({van_stem} {van_stem_el} khắc {tue_stem} {tue_stem_el})",
            "narrative": (
                f"**CHIẾN — Vận phạt Tuế**: Đại Vận {van_stem} ({van_stem_el}) khắc Lưu Niên "
                f"{tue_stem} ({tue_stem_el}). "
                "Tuế thường phải hàng (theo Vận). Hỉ thân nếu Vận là Dụng → cát; "
                "ngược lại = hung. Cần xem Mậu/Kỷ điều hòa hay không."
            ),
        })
    elif _element_controls(tue_stem_el, van_stem_el):
        relations.append({
            "type": "chien_tue_khac_van",
            "label": f"Tuế phạt Vận ({tue_stem} {tue_stem_el} khắc {van_stem} {van_stem_el})",
            "narrative": (
                f"**CHIẾN — Tuế phạt Vận**: Lưu Niên {tue_stem} ({tue_stem_el}) khắc Đại Vận "
                f"{van_stem} ({van_stem_el}). "
                "Vận tự hàng — cát/hung phụ thuộc Hỉ Thần."
            ),
        })

    # 2. XUNG — Chi đối lập
    pair = frozenset([van_branch, tue_branch])
    if pair in LUC_XUNG_PAIRS:
        relations.append({
            "type": "xung",
            "label": f"Vận-Tuế xung ({van_branch} ↔ {tue_branch})",
            "narrative": (
                f"**XUNG**: Đại Vận chi {van_branch} đối lập Lưu Niên chi {tue_branch}. "
                f"Theo Nhậm Thị: 'Xung là phá vậy.' Cần xét đảng phái chi nào nhiều hơn trong "
                "Tứ Trụ + can đầu trợ chi nào → quyết định bên nào thắng."
            ),
        })

    # 3. HÒA — Ngũ Hợp Can
    pair_stem = frozenset([van_stem, tue_stem])
    if pair_stem in NGU_HOP_CAN:
        hop_el = NGU_HOP_CAN[pair_stem]
        relations.append({
            "type": "hoa",
            "label": f"Vận-Tuế hợp ({van_stem}+{tue_stem} hóa {hop_el.title()})",
            "narrative": (
                f"**HÒA**: Vận {van_stem} + Tuế {tue_stem} = Ngũ Hợp Can hóa {hop_el.title()}. "
                "Theo Nhậm Thị: hợp mà có Thiên Hóa thì hỉ Kim cát; hợp mà không hội = hợp trói, "
                "không quan tâm Nhật Chủ → có thể không cát."
            ),
        })

    # 4. TỐT/TƯƠNG ĐỒNG — cùng can hoặc chi cùng hành
    if van_stem == tue_stem:
        relations.append({
            "type": "tot_can_trung",
            "label": f"Vận-Tuế can trùng ({van_stem})",
            "narrative": (
                f"**TỐT — Can trùng**: Đại Vận {van_stem} + Lưu Niên {van_stem} — như bạn bè. "
                "Cần thông căn vận vượng để cát."
            ),
        })
    if van_branch == tue_branch:
        relations.append({
            "type": "tot_chi_trung",
            "label": f"Vận-Tuế chi trùng ({van_branch})",
            "narrative": (
                f"**TỐT — Chi trùng**: Đại Vận {van_branch} + Lưu Niên {van_branch} — chi Lộc vượng "
                "tự quay về bản khí. Như người thân trong nhà."
            ),
        })
    # Cùng hành chi (khác chi nhưng cùng ngũ hành)
    van_b_el = BRANCH_ELEMENT.get(van_branch, "").lower()
    tue_b_el = BRANCH_ELEMENT.get(tue_branch, "").lower()
    if van_b_el and van_b_el == tue_b_el and van_branch != tue_branch:
        relations.append({
            "type": "tot_hanh_dong",
            "label": f"Chi cùng hành ({van_b_el.title()})",
            "narrative": (
                f"**TỐT — Chi cùng hành**: {van_branch} và {tue_branch} đều {van_b_el} — "
                "khí đồng dạng, không xung đột."
            ),
        })

    # Composite
    if not relations:
        primary = {
            "type": "binh_thuong",
            "label": "Vận-Tuế bình thường",
            "narrative": "Đại Vận và Lưu Niên không có quan hệ Chiến/Xung/Hòa/Tốt rõ rệt. Xét theo Dụng Thần riêng.",
        }
        return {"primary": primary, "all_relations": [], "source": "Trích Thiên Tủy Ch.28"}

    # Priority: chien > xung > hoa > tot
    priority_order = ["chien_van_khac_tue", "chien_tue_khac_van", "xung", "hoa", "tot_can_trung", "tot_chi_trung", "tot_hanh_dong"]
    relations.sort(key=lambda r: priority_order.index(r["type"]) if r["type"] in priority_order else 999)

    return {
        "primary": relations[0],
        "all_relations": relations,
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 28 Tuế Vận",
        "paradigm_guard": (
            "⚠️ Đây là DỘNG LỰC KHÍ giữa Đại Vận và Lưu Niên — KHÔNG predict tĩnh. "
            "Cát/hung phụ thuộc Hỉ Thần Tứ Trụ + thông căn + đảng phái chi."
        ),
    }
