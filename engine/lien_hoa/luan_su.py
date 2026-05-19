"""Luận sự — interpretation layer for Liên Hoa Độn Pháp.

Source: 'Liên Hoa Độn Pháp' (LIENHOADON.pdf), chương II "Hướng dẫn vận dụng"
p.30-58. The book's interpretation is structured around:

1. Phân bố Chủ sự — count of TA / H / P / C / Q / T across KTS.
2. Mệnh cung TA — what lục thân occupies Hổ quái at TA side.
3. Dạng Chánh quái Tiên đề — TA/T (Tài sự), TA/Q (Quan sự), etc.
4. 5 LĨNH VỰC ỨNG DỤNG:
   - Giàu nghèo (chủ yếu xem T)
   - Hôn nhân (Nam: T cư Mệnh; Nữ: Q cư Mệnh = thành)
   - Nhà cửa (dạng P/TA mặt đường lớn; Q/TA ngõ hẽm)
   - Sức khỏe (Q nhiều = bệnh nặng; P cư Mệnh = qua khỏi)
   - Xuất hành / kiện tụng (Q ở đâu = phương hại)
5. Vận đời (số đợt độn → ổn định vs thăng trầm):
   - 1 đợt (5 KTS, hào 3/6): TA bất biến, trước sau như một
   - 2 đợt (9 KTS, hào 1/4): có biến
   - 3 đợt (13 KTS, hào 2/5): nhiều đa đoan, thăng trầm

Framing rule: output is STATE description + classical interpretation từ sách.
Per blueprint, không dùng tone "tiên tri tuyệt đối". Mọi conclusion có note
"theo sách Liên Hoa Độn Pháp" để rõ provenance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import LUC_THAN_NAMES


# ---------- Helpers ----------

def chu_su_distribution(khong_thoi_list: list[dict]) -> dict[str, int]:
    """Count occurrences of each chủ sự across the spread."""
    counts = {"TA": 0, "H": 0, "P": 0, "C": 0, "Q": 0, "T": 0}
    for kt in khong_thoi_list:
        counts[kt["chu_su"]] = counts.get(kt["chu_su"], 0) + 1
    return counts


def menh_cung_lt_of(kts: dict) -> str:
    """Get lục thân tag of Mệnh cung (Hổ quái at TA side) of one KTS."""
    idx = 2 if kts["ta_side"] == "upper" else 3
    return kts["tagged"][idx]["luc_than"]


def truoc_menh_lt_of(kts: dict) -> str:
    """Trước Mệnh cung = đơn quái còn lại của Hổ (ở side đối diện TA)."""
    idx = 3 if kts["ta_side"] == "upper" else 2
    return kts["tagged"][idx]["luc_than"]


def chanh_dang_of(kts: dict) -> str:
    """Dạng Chánh quái: TA/<lt of SỰ side>."""
    su_idx = 0 if kts["su_side"] == "upper" else 1
    su_lt = kts["tagged"][su_idx]["luc_than"]
    return f"TA/{su_lt}"


# ---------- Interpretations per domain ----------

@dataclass(frozen=True)
class DomainReading:
    domain: str                 # "wealth" | "marriage" | "house" | "health" | "travel" | "life_arc"
    domain_vi: str
    verdict: str                # short label e.g. "Thành", "Bất thành", "Giàu", "Hao tổn"
    explanation: str            # full reasoning
    evidence: list[str]         # bullet points referencing KTS / lục thân

    def to_dict(self) -> dict:
        return asdict(self)


def interpret_marriage(spread: dict) -> DomainReading:
    """Hôn nhân — sách p.37-38."""
    gender = spread.get("gender", "nam")
    tien_de = spread["khong_thoi"][0]
    menh_lt = menh_cung_lt_of(tien_de)
    truoc_menh = truoc_menh_lt_of(tien_de)

    expected = "T" if gender == "nam" else "Q"
    expected_name = LUC_THAN_NAMES[expected]
    counter_name = LUC_THAN_NAMES[expected]

    evidence: list[str] = []
    evidence.append(f"Mệnh cung TA: {LUC_THAN_NAMES.get(menh_lt, menh_lt)}")
    if truoc_menh != menh_lt:
        evidence.append(f"Trước Mệnh cung: {LUC_THAN_NAMES.get(truoc_menh, truoc_menh)}")

    if menh_lt == "TA" and truoc_menh == "TA":
        return DomainReading(
            domain="marriage",
            domain_vi="Hôn nhân",
            verdict="Độc thân / tu hành",
            explanation=(
                "Mệnh cung trong-ngoài chỉ TA với TA — tượng độc thân, làm sư / làm ni, phải đạo. "
                "Sách trang 38."
            ),
            evidence=evidence,
        )
    if menh_lt == expected:
        return DomainReading(
            domain="marriage",
            domain_vi="Hôn nhân",
            verdict="Thành — hợp cách",
            explanation=(
                f"{expected_name} cư Mệnh — đúng lý {('Nam có vợ' if gender == 'nam' else 'Nữ có chồng')}. "
                "Sách trang 37: 'Lý Nam trưởng thành đã có vợ thì TÀI phải CƯ MỆNH TA NAM' / "
                "'Lý gái lớn đã có chồng thì QUAN phải CƯ MỆNH TA NỮ'."
            ),
            evidence=evidence,
        )
    if truoc_menh == expected:
        return DomainReading(
            domain="marriage",
            domain_vi="Hôn nhân",
            verdict="Thành nhưng có sự bất ngờ",
            explanation=(
                f"{expected_name} áng trước Mệnh cung — không cư trực tiếp nhưng vẫn có dấu hiệu, "
                "có thể do duyên đến muộn hoặc qua trung gian."
            ),
            evidence=evidence,
        )
    return DomainReading(
        domain="marriage",
        domain_vi="Hôn nhân",
        verdict="Bất thành / bất thường",
        explanation=(
            f"Mệnh cung không có {expected_name} — sự bất thành. Cẩn trọng xét nguyên do: "
            "ly dị, chết, đi xa lâu năm, ở vậy tu hành, hoặc số phận không có vợ/chồng. "
            "Sách trang 37."
        ),
        evidence=evidence,
    )


def interpret_wealth(spread: dict) -> DomainReading:
    """Giàu nghèo — chủ yếu xem T (Tài), C (Tử/hao), P (Phụ/quý nhân)."""
    counts = chu_su_distribution(spread["khong_thoi"])
    t = counts["T"]
    c = counts["C"]
    p = counts["P"]
    q = counts["Q"]

    evidence = [
        f"Chủ sự Tài (T): {t}",
        f"Chủ sự Phụ (P): {p}",
        f"Chủ sự Tử (C, hao): {c}",
        f"Chủ sự Quan (Q, áp lực): {q}",
    ]

    if t >= 2 and p >= 1 and c <= 1:
        return DomainReading(
            domain="wealth",
            domain_vi="Tài lộc",
            verdict="Vượng tài",
            explanation=f"{t} không thời Tài + {p} Phụ ủng hộ, ít hao tổn → vận tài lộc thuận.",
            evidence=evidence,
        )
    if t == 0 and p == 0 and (c >= 2 or q >= 2):
        return DomainReading(
            domain="wealth",
            domain_vi="Tài lộc",
            verdict="Hao tổn / khốn cùng",
            explanation=(
                f"Vắng bóng Tài và Phụ, lại có {c} không thời chi hao + {q} không thời áp lực → "
                "không có cơ may thu hồi vốn. (Sách trang 32: thí dụ ông A mở quán cà phê thất bại)."
            ),
            evidence=evidence,
        )
    if t >= 1:
        return DomainReading(
            domain="wealth",
            domain_vi="Tài lộc",
            verdict="Có thu nhập nhưng có hao",
            explanation=f"{t} Tài + {c} Tử → có lợi nhưng phải chi ra song song.",
            evidence=evidence,
        )
    if c >= 2 and t == 0:
        return DomainReading(
            domain="wealth",
            domain_vi="Tài lộc",
            verdict="Hao nhiều, không có cơ may",
            explanation=f"{c} không thời chi hao mà không có Tài → hao tổn.",
            evidence=evidence,
        )
    return DomainReading(
        domain="wealth",
        domain_vi="Tài lộc",
        verdict="Trung tính",
        explanation="Phân bố lục thân cân bằng — chưa thấy tín hiệu mạnh về tài.",
        evidence=evidence,
    )


def interpret_house(spread: dict) -> DomainReading:
    """Nhà cửa — sách p.50-53. Dạng P/TA = mặt đường, Q/TA = ngõ hẻm."""
    tien_de = spread["khong_thoi"][0]
    dang = chanh_dang_of(tien_de)
    evidence = [f"Dạng Chánh quái Tiên đề: {dang}"]

    if dang == "TA/P":
        return DomainReading(
            domain="house",
            domain_vi="Nhà cửa",
            verdict="Nhà mặt đường",
            explanation=(
                "Dạng P/TA → TA có nhà ở mặt đường. Nếu P vượng thì đường lớn, sầm uất. Sách p.50."
            ),
            evidence=evidence,
        )
    if dang == "TA/Q":
        return DomainReading(
            domain="house",
            domain_vi="Nhà cửa",
            verdict="Nhà trong ngõ hẽm",
            explanation=(
                "Dạng Q/TA → TA có nhà trong hẻm. Nếu Q vượng thì đường nhỏ thêm nhỏ. Sách p.50."
            ),
            evidence=evidence,
        )
    # Nếu Tiên đề không cho biết, scan các KTS TA khác để tìm dạng P/TA.
    for kt in spread["khong_thoi"]:
        if kt["chu_su"] == "TA" and kt["index"] > 1:
            sub_dang = chanh_dang_of(kt)
            if sub_dang == "TA/P":
                evidence.append(f"KTS {kt['index']} ({kt['label']}) có dạng P/TA")
                return DomainReading(
                    domain="house",
                    domain_vi="Nhà cửa",
                    verdict="Có giai đoạn nhà mặt đường",
                    explanation=(
                        f"Tiên đề chưa rõ, nhưng KTS {kt['index']} ({kt['label']}) "
                        "có dạng P/TA → giai đoạn này TA có nhà mặt đường. Sách p.51-52."
                    ),
                    evidence=evidence,
                )
    return DomainReading(
        domain="house",
        domain_vi="Nhà cửa",
        verdict="Chưa rõ vị trí",
        explanation=(
            f"Tiên đề dạng {dang} — chưa cho biết mặt đường hay ngõ hẽm. "
            "Cần xét thêm các KTS TA khác trong chuỗi."
        ),
        evidence=evidence,
    )


def interpret_health(spread: dict) -> DomainReading:
    """Sức khỏe — Q nhiều = bệnh, P cư Mệnh = qua khỏi (sách p.49)."""
    counts = chu_su_distribution(spread["khong_thoi"])
    q = counts["Q"]
    p = counts["P"]
    tien_de = spread["khong_thoi"][0]
    menh_lt = menh_cung_lt_of(tien_de)

    evidence = [
        f"Chủ sự Quan (Q, bệnh/tai): {q}",
        f"Chủ sự Phụ (P, quý nhân/thuốc): {p}",
        f"Mệnh cung TA: {LUC_THAN_NAMES.get(menh_lt, menh_lt)}",
    ]

    if q >= 2 and menh_lt == "P":
        return DomainReading(
            domain="health",
            domain_vi="Sức khỏe",
            verdict="Có bệnh nhưng qua khỏi",
            explanation=(
                f"{q} không thời Quan (bệnh/tai) nhưng P cư Mệnh — sách p.49: "
                "'trường hợp bệnh khốn mà Mệnh được P cư thì nguy khốn ắt qua'."
            ),
            evidence=evidence,
        )
    if q >= 2 and p == 0:
        return DomainReading(
            domain="health",
            domain_vi="Sức khỏe",
            verdict="Bệnh nặng, ít cơ may",
            explanation=f"{q} không thời Quan + không có Phụ Mẫu hỗ trợ → tình trạng nguy.",
            evidence=evidence,
        )
    if menh_lt == "C":
        return DomainReading(
            domain="health",
            domain_vi="Sức khỏe",
            verdict="Hao sức",
            explanation="Tử cư Mệnh — sách p.48: 'không lợi cho sức khỏe, không lợi kinh doanh'.",
            evidence=evidence,
        )
    if q == 0 and (menh_lt == "P" or menh_lt == "TA"):
        return DomainReading(
            domain="health",
            domain_vi="Sức khỏe",
            verdict="Bình ổn",
            explanation="Không có Quan + Mệnh có Phụ hoặc TA — tình trạng sức khỏe ổn.",
            evidence=evidence,
        )
    return DomainReading(
        domain="health",
        domain_vi="Sức khỏe",
        verdict="Trung tính",
        explanation="Phân bố cân bằng — không tín hiệu rõ về sức khỏe.",
        evidence=evidence,
    )


def interpret_life_arc(spread: dict) -> DomainReading:
    """Vận đời — số đợt độn → ổn định vs thăng trầm. Sách p.54."""
    dot = spread["dot_count"]
    kt_count = spread["khong_thoi_count"]
    ta_kts = [kt for kt in spread["khong_thoi"] if kt["chu_su"] == "TA"]
    evidence = [
        f"{dot} đợt độn → {kt_count} không thời sự",
        f"Có {len(ta_kts)} KTS với chủ sự TA (tại KTS số {[k['index'] for k in ta_kts]})",
    ]

    if dot == 1:
        return DomainReading(
            domain="life_arc",
            domain_vi="Vận đời",
            verdict="Ổn định / ít biến",
            explanation=(
                "Hào động 3 hoặc 6 → 1 đợt độn → TA bất biến nhanh — "
                "'người sang sang mãi, người bần bần cùng hoài' (sách p.54). "
                "Cuộc đời ít thay đổi vận lớn."
            ),
            evidence=evidence,
        )
    if dot == 2:
        return DomainReading(
            domain="life_arc",
            domain_vi="Vận đời",
            verdict="Có biến giữa đời",
            explanation=(
                "Hào động 1 hoặc 4 → 2 đợt độn → TA có biến đổi đáng kể giữa giai đoạn 1 và 2."
            ),
            evidence=evidence,
        )
    return DomainReading(
        domain="life_arc",
        domain_vi="Vận đời",
        verdict="Nhiều thăng trầm",
        explanation=(
            "Hào động 2 hoặc 5 → 3 đợt độn → 13 không thời, 'nhiều đa đoan đưa đẩy TA thăng trầm' "
            "(sách p.54). Cuộc đời có nhiều giai đoạn biến chuyển lớn."
        ),
        evidence=evidence,
    )


def interpret_travel_safety(spread: dict) -> DomainReading:
    """Xuất hành — Q là phương hiểm. Sách p.56-57."""
    q_kts = [kt for kt in spread["khong_thoi"] if kt["chu_su"] == "Q"]
    p_kts = [kt for kt in spread["khong_thoi"] if kt["chu_su"] == "P"]

    evidence = []
    for kt in q_kts:
        evidence.append(f"KTS {kt['index']} ({kt['label']}): Quan cư — phương hại")
    for kt in p_kts:
        evidence.append(f"KTS {kt['index']} ({kt['label']}): Phụ cư — phương lợi")

    if not q_kts and p_kts:
        return DomainReading(
            domain="travel",
            domain_vi="Xuất hành",
            verdict="An toàn",
            explanation="Không có Quan, có Phụ — đường đi thuận lợi, gặp quý nhân.",
            evidence=evidence,
        )
    if q_kts and not p_kts:
        return DomainReading(
            domain="travel",
            domain_vi="Xuất hành",
            verdict="Hiểm nguy",
            explanation=(
                f"Có {len(q_kts)} KTS Quan cư — TA nhập vào những phương này dễ gặp hại. Sách p.56."
            ),
            evidence=evidence,
        )
    if q_kts and p_kts:
        return DomainReading(
            domain="travel",
            domain_vi="Xuất hành",
            verdict="Có lợi có hại — tránh phương Q",
            explanation=(
                f"{len(q_kts)} KTS Quan + {len(p_kts)} KTS Phụ — đi về phương P thì lợi, "
                "đi về phương Q thì gặp hại."
            ),
            evidence=evidence,
        )
    return DomainReading(
        domain="travel",
        domain_vi="Xuất hành",
        verdict="Trung tính",
        explanation="Không có tín hiệu rõ — đi đâu cũng vừa phải.",
        evidence=evidence,
    )


# ---------- Top-level luận compose ----------

@dataclass(frozen=True)
class LuanSu:
    chu_su_counts: dict[str, int]
    menh_cung_lt: str                # Lục thân tag of Mệnh cung Tiên đề
    menh_cung_lt_name: str
    chanh_dang_tien_de: str          # e.g. "TA/T"
    domain_readings: list[DomainReading]
    composed_summary: str            # 2-3 sentences

    def to_dict(self) -> dict:
        return {
            "chu_su_counts": self.chu_su_counts,
            "menh_cung_lt": self.menh_cung_lt,
            "menh_cung_lt_name": self.menh_cung_lt_name,
            "chanh_dang_tien_de": self.chanh_dang_tien_de,
            "domain_readings": [r.to_dict() for r in self.domain_readings],
            "composed_summary": self.composed_summary,
        }


def luan_su(spread: dict) -> LuanSu:
    """Top-level interpreter — runs all 6 domain readings + composes summary."""
    counts = chu_su_distribution(spread["khong_thoi"])
    tien_de = spread["khong_thoi"][0]
    menh_lt = menh_cung_lt_of(tien_de)
    chanh_dang = chanh_dang_of(tien_de)

    readings = [
        interpret_life_arc(spread),
        interpret_wealth(spread),
        interpret_marriage(spread),
        interpret_house(spread),
        interpret_health(spread),
        interpret_travel_safety(spread),
    ]

    # Composed summary — 2-3 sentences.
    gender_phrase = "TA Nam" if spread.get("gender") == "nam" else "TA Nữ"
    summary_parts = [
        f"{gender_phrase}, quẻ Tiên đề {tien_de['chanh']['name_vi']} dạng {chanh_dang}, "
        f"Mệnh cung TA có {LUC_THAN_NAMES.get(menh_lt, menh_lt)} cư.",
        f"Tổng {spread['khong_thoi_count']} không thời, phân bố chủ sự: "
        + ", ".join(f"{LUC_THAN_NAMES.get(k, k)}={v}" for k, v in counts.items() if v > 0)
        + ".",
        f"Vận đời {readings[0].verdict.lower()}, tài lộc {readings[1].verdict.lower()}, "
        f"hôn nhân {readings[2].verdict.lower()}.",
    ]
    composed = " ".join(summary_parts)

    return LuanSu(
        chu_su_counts=counts,
        menh_cung_lt=menh_lt,
        menh_cung_lt_name=LUC_THAN_NAMES.get(menh_lt, menh_lt),
        chanh_dang_tien_de=chanh_dang,
        domain_readings=readings,
        composed_summary=composed,
    )
