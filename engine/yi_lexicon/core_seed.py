"""Core seed for YI-Lexicon — bedrock concepts that never need re-extraction.

Sources (manually verified, all canonical 易经 + 五行 + 干支):
- 易经 — 周易 (Kinh Dịch — Chu Dịch)
- 滴天髓 (Tích Thiên Tủy)
- 三命通會 (Tam Mệnh Thông Hội)
- Mai Hoa Dịch Số — Thiệu Khang Tiết
- Hoàng Đế Nội Kinh (organ/element correspondences)

Idempotent: safe to run multiple times. Skips entries already in DB.
"""

from __future__ import annotations

from .store import add_concept, add_mapping, bootstrap_db


# ─── ÂM DƯƠNG ────────────────────────────────────────────────────────────────

AM_DUONG = [
    # (vi, zh, en, type, aliases, dim_type, dim_value, reasoning_vi)
    ("dương", "陽", "yang", "concept", ["dương khí", "Yang"],
     "am_duong", "dương", "Nguyên lý cương — sáng, động, mạnh, ngoài, nóng, trên, nam"),
    ("âm", "陰", "yin", "concept", ["âm khí", "Yin"],
     "am_duong", "âm", "Nguyên lý nhu — tối, tĩnh, mềm, trong, lạnh, dưới, nữ"),
    ("bố", "父", "father", "relation", ["cha", "ba", "phụ thân"],
     "am_duong", "dương", "Phụ là dương, đại diện trời, quyết đoán, ngoài"),
    ("mẹ", "母", "mother", "relation", ["má", "mẫu thân"],
     "am_duong", "âm", "Mẫu là âm, đại diện đất, ôn nhu, trong"),
    ("trên", "上", "upper", "concept", ["thượng"],
     "am_duong", "dương", "Vị trí trên thuộc dương"),
    ("dưới", "下", "lower", "concept", ["hạ"],
     "am_duong", "âm", "Vị trí dưới thuộc âm"),
    ("sáng", "明", "bright", "phenomenon", ["sang", "ban ngày"],
     "am_duong", "dương", "Ánh sáng thuộc dương"),
    ("tối", "暗", "dark", "phenomenon", ["đen", "ban đêm"],
     "am_duong", "âm", "Bóng tối thuộc âm"),
    ("trời", "天", "heaven", "concept", ["thiên"],
     "am_duong", "dương", "Trời = dương cực"),
    ("đất", "地", "earth", "concept", ["địa"],
     "am_duong", "âm", "Đất = âm cực"),
    ("nam", "男", "male", "concept", ["đàn ông", "nam giới"],
     "am_duong", "dương", "Phái nam thuộc dương"),
    ("nữ", "女", "female", "concept", ["đàn bà", "phụ nữ"],
     "am_duong", "âm", "Phái nữ thuộc âm"),
]


# ─── NGŨ HÀNH ────────────────────────────────────────────────────────────────

NGU_HANH_BASE = [
    # element_vi, element_zh, element_en, color, direction, season, organ, taste, sound, animal
    ("mộc", "木", "wood", "xanh lá", "đông", "xuân", "gan/mật", "chua", "âm gốc", "rồng/cọp"),
    ("hỏa", "火", "fire", "đỏ", "nam", "hạ", "tim/tiểu trường", "đắng", "âm 'chỉ'", "phượng hoàng/chim"),
    ("thổ", "土", "earth", "vàng", "trung tâm", "tứ quý / cuối mỗi mùa", "tỳ/dạ dày", "ngọt", "âm 'cung'", "kỳ lân/trâu"),
    ("kim", "金", "metal", "trắng", "tây", "thu", "phổi/đại trường", "cay", "âm 'thương'", "hổ trắng/bạch hổ"),
    ("thủy", "水", "water", "đen/xanh dương", "bắc", "đông", "thận/bàng quang", "mặn", "âm 'vũ'", "rùa/cá"),
]


def _seed_ngu_hanh_full() -> None:
    """Bootstrap mọi mappings cho 5 hành (màu, hướng, mùa, tạng, vị, ...)."""
    for elem_vi, elem_zh, elem_en, color, direction, season, organ, taste, sound, animal in NGU_HANH_BASE:
        # Concept "hành Mộc" itself
        elem_concept = add_concept(
            canonical_vi=elem_vi.title(),
            canonical_zh=elem_zh, canonical_en=elem_en,
            concept_type="concept",
            aliases=[elem_vi, f"hành {elem_vi}"],
            schools=["common"], source="seed:core",
            confidence=1.0,
            notes=f"Một trong 5 hành (Ngũ Hành). Tương sinh tiếp theo / tương khắc next.",
        )
        # Self-mapping to ngu_hanh
        add_mapping(elem_concept.concept_id, "ngu_hanh", elem_vi,
                    strength=1.0, source="seed:core", confidence=1.0,
                    reasoning_vi=f"Đây CHÍNH LÀ hành {elem_vi}")

        # Color → element
        for color_token in color.split("/"):
            color_token = color_token.strip()
            c = add_concept(color_token, concept_type="color",
                            schools=["common"], source="seed:core", confidence=1.0,
                            notes=f"Màu {color_token} thuộc hành {elem_vi}")
            add_mapping(c.concept_id, "ngu_hanh", elem_vi,
                        reasoning_vi=f"Màu {color_token} là biểu tượng truyền thống của hành {elem_vi}",
                        source="seed:core", confidence=0.9)

        # Direction → element
        d = add_concept(direction, concept_type="place",
                        aliases=[f"hướng {direction}"], schools=["common"],
                        source="seed:core", confidence=1.0,
                        notes=f"Hướng {direction} thuộc hành {elem_vi}")
        add_mapping(d.concept_id, "ngu_hanh", elem_vi,
                    reasoning_vi=f"Hướng {direction} là phương vị truyền thống của hành {elem_vi}",
                    source="seed:core", confidence=0.95)

        # Season → element
        s = add_concept(season, concept_type="time",
                        aliases=[f"mùa {season}"], schools=["common"],
                        source="seed:core", confidence=1.0)
        add_mapping(s.concept_id, "ngu_hanh", elem_vi,
                    reasoning_vi=f"Mùa {season} là mùa của hành {elem_vi}",
                    source="seed:core", confidence=0.9)

        # Organ → element
        for org in organ.split("/"):
            org = org.strip()
            o = add_concept(org, concept_type="object",
                            aliases=["tạng " + org], schools=["common"],
                            source="seed:core", confidence=1.0,
                            notes=f"Tạng {org} thuộc hành {elem_vi}")
            add_mapping(o.concept_id, "ngu_hanh", elem_vi,
                        reasoning_vi=f"Hoàng Đế Nội Kinh: tạng {org} ứng hành {elem_vi}",
                        source="seed:core", confidence=0.85)

        # Taste → element
        t = add_concept(f"vị {taste}", concept_type="concept",
                        aliases=[taste], schools=["common"],
                        source="seed:core", confidence=1.0)
        add_mapping(t.concept_id, "ngu_hanh", elem_vi,
                    reasoning_vi=f"Vị {taste} thuộc hành {elem_vi}",
                    source="seed:core", confidence=0.85)


# ─── BÁT QUÁI ────────────────────────────────────────────────────────────────

BAT_QUAI = [
    # name_vi, name_zh, symbol, element, family_role, nature_image, attribute_vi
    ("Càn", "乾", "☰", "kim", "phụ (cha)", "thiên (trời)", "cương kiện, vận hành"),
    ("Khôn", "坤", "☷", "thổ", "mẫu (mẹ)", "địa (đất)", "thuận, chứa đựng, nhu"),
    ("Chấn", "震", "☳", "mộc", "trưởng nam", "lôi (sấm)", "động, khởi, kích phát"),
    ("Tốn", "巽", "☴", "mộc", "trưởng nữ", "phong (gió)", "thuận, nhập, mềm len lỏi"),
    ("Khảm", "坎", "☵", "thủy", "trung nam", "thủy (nước)", "hiểm, sâu, ưu lo"),
    ("Ly", "離", "☲", "hỏa", "trung nữ", "hỏa (lửa)", "sáng, đẹp, lệ thuộc"),
    ("Cấn", "艮", "☶", "thổ", "thiếu nam", "sơn (núi)", "tĩnh, dừng, vững"),
    ("Đoài", "兌", "☱", "kim", "thiếu nữ", "trạch (đầm)", "vui vẻ, miệng, hỉ duyệt"),
]


def _seed_bat_quai() -> None:
    for name_vi, name_zh, sym, elem, family, image, attr in BAT_QUAI:
        c = add_concept(
            canonical_vi=name_vi,
            canonical_zh=name_zh,
            concept_type="symbol",
            aliases=[sym, image, f"quẻ {name_vi}"],
            schools=["mai_hoa", "lien_hoa", "luc_hao", "ha_lac", "common"],
            source="seed:core",
            confidence=1.0,
            notes=f"Bát quái {name_vi} ({name_zh}): {image}, đại diện {family}, "
                  f"thuộc {elem}, tính chất {attr}",
        )
        # Map to bat_quai dim
        add_mapping(c.concept_id, "bat_quai", name_vi,
                    reasoning_vi=f"{name_vi} là một trong 8 quẻ",
                    source="seed:core", confidence=1.0)
        # Map to ngu_hanh
        add_mapping(c.concept_id, "ngu_hanh", elem,
                    reasoning_vi=f"Quẻ {name_vi} thuộc hành {elem}",
                    source="seed:core", confidence=1.0)


# ─── THIÊN CAN ───────────────────────────────────────────────────────────────

THIEN_CAN = [
    # vi, zh, element, polarity
    ("Giáp", "甲", "mộc", "dương"),
    ("Ất", "乙", "mộc", "âm"),
    ("Bính", "丙", "hỏa", "dương"),
    ("Đinh", "丁", "hỏa", "âm"),
    ("Mậu", "戊", "thổ", "dương"),
    ("Kỷ", "己", "thổ", "âm"),
    ("Canh", "庚", "kim", "dương"),
    ("Tân", "辛", "kim", "âm"),
    ("Nhâm", "壬", "thủy", "dương"),
    ("Quý", "癸", "thủy", "âm"),
]


def _seed_thien_can() -> None:
    for vi, zh, elem, polarity in THIEN_CAN:
        c = add_concept(
            canonical_vi=vi, canonical_zh=zh,
            concept_type="symbol",
            aliases=[f"can {vi}"],
            schools=["bat_tu", "ha_lac", "luc_hao", "common"],
            source="seed:core", confidence=1.0,
            notes=f"Thiên Can {vi} ({zh}): hành {elem}, dương âm = {polarity}",
        )
        add_mapping(c.concept_id, "thien_can", vi, source="seed:core", confidence=1.0)
        add_mapping(c.concept_id, "ngu_hanh", elem, source="seed:core", confidence=1.0,
                    reasoning_vi=f"Can {vi} thuộc hành {elem}")
        add_mapping(c.concept_id, "am_duong", polarity, source="seed:core", confidence=1.0,
                    reasoning_vi=f"Can {vi} là can {polarity}")


# ─── ĐỊA CHI ─────────────────────────────────────────────────────────────────

DIA_CHI = [
    # vi, zh, animal_vi, animal_zh, element, polarity, hour_range, month
    ("Tý", "子", "chuột", "鼠", "thủy", "dương", "23:00-01:00", "11"),
    ("Sửu", "丑", "trâu", "牛", "thổ", "âm", "01:00-03:00", "12"),
    ("Dần", "寅", "hổ", "虎", "mộc", "dương", "03:00-05:00", "1"),
    ("Mão", "卯", "mèo/thỏ", "兔", "mộc", "âm", "05:00-07:00", "2"),
    ("Thìn", "辰", "rồng", "龍", "thổ", "dương", "07:00-09:00", "3"),
    ("Tỵ", "巳", "rắn", "蛇", "hỏa", "âm", "09:00-11:00", "4"),
    ("Ngọ", "午", "ngựa", "馬", "hỏa", "dương", "11:00-13:00", "5"),
    ("Mùi", "未", "dê", "羊", "thổ", "âm", "13:00-15:00", "6"),
    ("Thân", "申", "khỉ", "猴", "kim", "dương", "15:00-17:00", "7"),
    ("Dậu", "酉", "gà", "雞", "kim", "âm", "17:00-19:00", "8"),
    ("Tuất", "戌", "chó", "狗", "thổ", "dương", "19:00-21:00", "9"),
    ("Hợi", "亥", "lợn", "豬", "thủy", "âm", "21:00-23:00", "10"),
]


def _seed_dia_chi() -> None:
    for vi, zh, animal_vi, animal_zh, elem, polarity, hour_range, month in DIA_CHI:
        c = add_concept(
            canonical_vi=vi, canonical_zh=zh,
            concept_type="symbol",
            aliases=[f"chi {vi}", animal_vi, animal_zh, f"giờ {vi}", f"tháng {vi}"],
            schools=["bat_tu", "tu_vi", "mai_hoa", "lien_hoa", "luc_hao", "common"],
            source="seed:core", confidence=1.0,
            notes=f"Địa Chi {vi} ({zh}): con {animal_vi}, hành {elem}, "
                  f"{polarity}, giờ {hour_range}, tháng âm lịch {month}",
        )
        add_mapping(c.concept_id, "dia_chi", vi, source="seed:core", confidence=1.0)
        add_mapping(c.concept_id, "ngu_hanh", elem, source="seed:core", confidence=1.0,
                    reasoning_vi=f"Chi {vi} ({animal_vi}) thuộc hành {elem}")
        add_mapping(c.concept_id, "am_duong", polarity, source="seed:core", confidence=1.0)


# ─── NUMBER mappings (for Mai Hoa quan vật khởi quẻ) ─────────────────────────

# Số → quẻ (Tiên thiên bát quái — Phục Hi)
# 1=Càn 2=Đoài 3=Ly 4=Chấn 5=Tốn 6=Khảm 7=Cấn 8=Khôn
NUMBER_TO_QUAI = [
    (1, "Càn"), (2, "Đoài"), (3, "Ly"), (4, "Chấn"),
    (5, "Tốn"), (6, "Khảm"), (7, "Cấn"), (8, "Khôn"),
]


def _seed_numbers() -> None:
    # Numbers 1-12 (covers hours/months) + 0
    for n in range(0, 13):
        c = add_concept(
            canonical_vi=str(n),
            concept_type="number",
            aliases=[f"số {n}"],
            schools=["common", "mai_hoa", "lien_hoa"],
            source="seed:core", confidence=1.0,
            notes=f"Số {n}",
        )
        # Số chẵn = âm, lẻ = dương (cổ điển)
        if n > 0:
            add_mapping(c.concept_id, "am_duong",
                        "âm" if n % 2 == 0 else "dương",
                        reasoning_vi=("Chẵn thuộc âm" if n % 2 == 0 else "Lẻ thuộc dương"),
                        source="seed:core", confidence=1.0)

    # Tiên thiên: 1-8 map sang quẻ
    for num, quai in NUMBER_TO_QUAI:
        c = add_concept(canonical_vi=str(num), concept_type="number",
                        source="seed:core", confidence=1.0)
        add_mapping(c.concept_id, "bat_quai", quai,
                    reasoning_vi=f"Tiên thiên Phục Hi: số {num} = quẻ {quai}",
                    source="seed:core", confidence=1.0,
                    school="mai_hoa")


# ─── Common phenomena / objects / actions (Mai Hoa quan vật vocab) ──────────

COMMON_PHENOMENA = [
    # vi, zh, en, type, schools, mappings = [(dim_type, dim_value, reasoning_vi)]
    ("lá", "葉", "leaf", "object", ["common", "mai_hoa"],
     [("ngu_hanh", "mộc", "Lá là phần của cây, thuộc Mộc"),
      ("am_duong", "âm", "Lá nhỏ mềm thuộc âm")]),
    ("rơi", "落", "fall", "phenomenon", ["common", "mai_hoa"],
     [("bat_quai", "Khôn", "Rơi xuống → hạ giáng → Khôn (đất, hạ vị)"),
      ("am_duong", "âm", "Hạ xuống thuộc âm"),
      ("khac", "kết thúc", "Rơi gợi ý sự kết thúc / suy thoái")]),
    ("bay", "飛", "fly", "phenomenon", ["common", "mai_hoa"],
     [("bat_quai", "Tốn", "Bay theo gió → Tốn (phong, di chuyển)"),
      ("am_duong", "dương", "Lên cao thuộc dương")]),
    ("vỡ", "破", "break", "phenomenon", ["common", "mai_hoa"],
     [("khac", "tan rã", "Vỡ gợi ý phá vỡ, tan rã"),
      ("am_duong", "âm", "Phá huỷ thuộc âm")]),
    ("gặp", "遇", "meet", "action", ["common", "mai_hoa", "lien_hoa"],
     [("khac", "duyên ngộ", "Gặp gỡ là duyên — cần xét cụ thể đối tượng gặp")]),
    ("đường", "路", "road", "place", ["common"],
     [("khac", "lộ trình", "Đường là lộ trình, hành trình")]),
    ("hoa", "花", "flower", "object", ["common", "mai_hoa"],
     [("ngu_hanh", "mộc", "Hoa thuộc cây cối, hành Mộc"),
      ("am_duong", "âm", "Hoa mỏng manh, thuộc âm")]),
    ("nước", "水", "water", "object", ["common", "mai_hoa"],
     [("ngu_hanh", "thủy", "Nước CHÍNH LÀ Thủy"),
      ("bat_quai", "Khảm", "Nước là tượng Khảm")]),
    ("lửa", "火", "fire", "object", ["common", "mai_hoa"],
     [("ngu_hanh", "hỏa", "Lửa CHÍNH LÀ Hỏa"),
      ("bat_quai", "Ly", "Lửa là tượng Ly")]),
    ("đá", "石", "stone", "object", ["common", "mai_hoa"],
     [("ngu_hanh", "thổ", "Đá thuộc Thổ"),
      ("bat_quai", "Cấn", "Đá núi → Cấn")]),
    ("sách", "書", "book", "object", ["common"],
     [("ngu_hanh", "mộc", "Sách (giấy) thuộc Mộc"),
      ("khac", "tri thức", "Sách = tri thức / quý nhân học vấn")]),
    ("xe", "車", "vehicle", "object", ["common"],
     [("ngu_hanh", "kim", "Xe (máy móc) thuộc Kim"),
      ("khac", "di chuyển", "Xe = phương tiện di chuyển")]),
    ("mưa", "雨", "rain", "phenomenon", ["common", "mai_hoa"],
     [("ngu_hanh", "thủy", "Mưa là nước rơi, thuộc Thủy"),
      ("am_duong", "âm", "Mưa làm ẩm, thuộc âm")]),
    ("gió", "風", "wind", "phenomenon", ["common", "mai_hoa"],
     [("bat_quai", "Tốn", "Gió CHÍNH LÀ Tốn"),
      ("am_duong", "dương", "Gió động, thuộc dương")]),
    ("sấm", "雷", "thunder", "phenomenon", ["common", "mai_hoa"],
     [("bat_quai", "Chấn", "Sấm CHÍNH LÀ Chấn"),
      ("am_duong", "dương", "Sấm kích động, dương")]),
    ("núi", "山", "mountain", "object", ["common", "mai_hoa"],
     [("bat_quai", "Cấn", "Núi CHÍNH LÀ Cấn"),
      ("ngu_hanh", "thổ", "Núi đất thuộc Thổ")]),
    ("đầm", "澤", "marsh", "object", ["common", "mai_hoa"],
     [("bat_quai", "Đoài", "Đầm CHÍNH LÀ Đoài"),
      ("ngu_hanh", "thủy", "Đầm nước thuộc Thủy")]),
    ("chim", "鳥", "bird", "object", ["common", "mai_hoa"],
     [("bat_quai", "Ly", "Chim bay sáng → Ly (lửa, sáng)"),
      ("am_duong", "dương", "Chim bay cao, dương")]),
    ("cá", "魚", "fish", "object", ["common"],
     [("bat_quai", "Khảm", "Cá ở nước → Khảm"),
      ("ngu_hanh", "thủy", "Cá thuộc Thủy")]),
]


def _seed_common_phenomena() -> None:
    for vi, zh, en, ctype, schools, mappings in COMMON_PHENOMENA:
        c = add_concept(
            canonical_vi=vi, canonical_zh=zh, canonical_en=en,
            concept_type=ctype, schools=schools,
            source="seed:phenomena", confidence=0.9,
        )
        for dim_type, dim_value, reasoning in mappings:
            add_mapping(c.concept_id, dim_type, dim_value,
                        reasoning_vi=reasoning,
                        source="seed:phenomena", confidence=0.85)


# ─── Master bootstrap ────────────────────────────────────────────────────────


def seed_all() -> dict:
    """Seed all bedrock concepts. Idempotent."""
    bootstrap_db()
    # Âm Dương
    for vi, zh, en, ctype, aliases, dim_type, dim_value, reasoning in AM_DUONG:
        c = add_concept(
            canonical_vi=vi, canonical_zh=zh, canonical_en=en,
            concept_type=ctype, aliases=aliases,
            schools=["common"], source="seed:core", confidence=1.0,
        )
        add_mapping(c.concept_id, dim_type, dim_value,
                    reasoning_vi=reasoning, source="seed:core", confidence=1.0)

    _seed_ngu_hanh_full()
    _seed_bat_quai()
    _seed_thien_can()
    _seed_dia_chi()
    _seed_numbers()
    _seed_common_phenomena()

    from .store import stats
    return stats()
