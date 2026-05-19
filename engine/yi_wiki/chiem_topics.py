"""Mai Hoa — 11 chiêm chuyên đề (Q2 Chiêm bốc huyền cơ).

Source: Mai Hoa Dịch Số Quyển 2 — Chiêm bốc huyền cơ
Bookflow: thâm nhuần 2026-05-19, master ở data/yi_publishing/mai_hoa_thamnhuan/master/

Mỗi chiêm có:
    - keywords: từ user_question để detect topic
    - description: 1 câu mô tả chiêm
    - the_dung_focus: trong chiêm này, Thể đại diện cho ai, Dụng đại diện cho ai
    - special_rules: list[str] các quy tắc riêng (vd "Hôn nhân: Khảm-Ly → vợ chồng hòa hợp")
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChiemTopic:
    code: str
    name_vi: str
    name_han_viet: str
    keywords: list[str]
    description: str
    the_dung_focus: str
    special_rules: list[str]


# 11 chiêm — Q2 mục lục
CHIEM_TOPICS: dict[str, ChiemTopic] = {
    "thien_thoi": ChiemTopic(
        code="thien_thoi", name_vi="Hỏi thời tiết", name_han_viet="Thiên thời chiêm",
        keywords=["thời tiết", "mưa", "nắng", "bão", "trời", "mưa hay nắng", "thiên thời",
                  "có mưa không", "có nắng không"],
        description="Hỏi về thời tiết, khí hậu, mưa/nắng/gió/bão",
        the_dung_focus="Thể = người hỏi, Dụng = trời (hiện tượng thời tiết)",
        special_rules=[
            "Càn/Đoài (Kim) chủ trời quang, không mưa",
            "Khảm (Thuỷ) chủ mưa, sông nước",
            "Ly (Hoả) chủ nắng nóng, hạn",
            "Tốn (Mộc) chủ gió",
            "Chấn (Sấm) chủ sấm chớp",
            "Khôn/Cấn (Thổ) chủ âm u, mây",
        ],
    ),
    "gia_trach": ChiemTopic(
        code="gia_trach", name_vi="Hỏi nhà ở", name_han_viet="Gia trạch chiêm",
        keywords=["nhà", "nhà cửa", "nơi ở", "gia trạch", "mua nhà", "sửa nhà", "chuyển nhà",
                  "phong thuỷ nhà", "đất xây nhà"],
        description="Hỏi về nhà ở, đất đai, nơi cư trú, phong thủy",
        the_dung_focus="Thể = người ở (chủ nhà), Dụng = ngôi nhà / đất",
        special_rules=[
            "Thể vượng + Dụng sinh Thể → nhà tốt, ở yên",
            "Dụng khắc Thể → nhà bất lợi, có người hại",
            "Quẻ có Khảm (nước) ở Thể → nhà gần nước, ẩm",
            "Quẻ có Ly (lửa) ở Dụng → cảnh báo hỏa hoạn",
            "Tỷ hoà → nhà bình thường, không thay đổi",
        ],
    ),
    "hon_nhan": ChiemTopic(
        code="hon_nhan", name_vi="Hỏi hôn nhân", name_han_viet="Hôn nhân chiêm",
        keywords=["hôn nhân", "kết hôn", "lấy chồng", "lấy vợ", "vợ chồng", "tình duyên",
                  "ly hôn", "ly thân", "kết duyên", "phối ngẫu"],
        description="Hỏi về hôn nhân, vợ chồng, tình duyên",
        the_dung_focus="Thể = mình (người hỏi), Dụng = đối phương (vợ/chồng)",
        special_rules=[
            "Thể-Dụng tỷ hoà → vợ chồng hòa hợp",
            "Dụng sinh Thể → đối phương đến với mình, nhiệt thành",
            "Thể sinh Dụng → mình theo đuổi đối phương",
            "Thể khắc Dụng → mình thắng (làm chủ)",
            "Dụng khắc Thể → đối phương lấn át",
            "Khảm-Ly (Trung nam + Trung nữ) → cặp đôi vượng",
            "Càn-Khôn → cặp chồng vợ đại biểu (cha mẹ)",
        ],
    ),
    "sinh_san": ChiemTopic(
        code="sinh_san", name_vi="Hỏi sinh con", name_han_viet="Sinh sản chiêm",
        keywords=["sinh con", "có con", "thai", "có thai", "sinh nở", "trẻ em",
                  "khó sinh", "nam hay nữ"],
        description="Hỏi về sinh nở, con cái, thai nhi",
        the_dung_focus="Thể = mẹ, Dụng = con (thai)",
        special_rules=[
            "Dụng sinh Thể → mẹ khỏe, con bình an",
            "Thể khắc Dụng → khó nuôi con / hại con",
            "Dụng khắc Thể → mẹ vất vả",
            "Quẻ dương (Càn/Chấn/Khảm/Cấn) ở Dụng → có thể là nam",
            "Quẻ âm (Khôn/Tốn/Ly/Đoài) ở Dụng → có thể là nữ",
        ],
    ),
    "cau_danh": ChiemTopic(
        code="cau_danh", name_vi="Hỏi học hành công danh", name_han_viet="Cầu danh chiêm",
        keywords=["công danh", "thi cử", "học hành", "khoa cử", "tốt nghiệp", "đỗ đạt",
                  "thăng chức", "thi đại học", "thi công chức", "danh vọng"],
        description="Hỏi về thi cử, công danh, học hành",
        the_dung_focus="Thể = người hỏi, Dụng = công danh / kỳ thi / chức vụ",
        special_rules=[
            "Thể vượng + Dụng sinh Thể → đỗ cao, công danh hanh thông",
            "Ly (Hoả) ở Thể vượng → văn chương phát đạt",
            "Càn ở Thể → công danh đại quý",
            "Dụng khắc Thể → thi rớt / tổn danh",
            "Thể khắc Dụng → tự mình lấy được, nhưng phải nỗ lực",
        ],
    ),
    "giao_dich": ChiemTopic(
        code="giao_dich", name_vi="Hỏi mua bán kinh doanh", name_han_viet="Giao dịch chiêm",
        keywords=["mua bán", "kinh doanh", "buôn bán", "giao dịch", "lãi", "lỗ",
                  "đầu tư", "khách hàng", "deal", "ký hợp đồng", "trading"],
        description="Hỏi về mua bán, kinh doanh, giao dịch tài chính",
        the_dung_focus="Thể = người hỏi (mình), Dụng = đối tác giao dịch / tài lộc",
        special_rules=[
            "Dụng sinh Thể → tài lộc đến, có lợi",
            "Thể vượng + tỷ hoà → giao dịch thành nhưng bình ổn",
            "Thể khắc Dụng → ép giá thắng, nhưng đối tác bất mãn",
            "Dụng khắc Thể → bị ép giá, có thiệt hại",
            "Càn-Đoài (Kim) ở Thể vượng → tài kim, tiền cứng",
            "Khảm (Thủy) ở Dụng → tiền lưu động, dễ vào dễ ra",
        ],
    ),
    "xuat_hanh": ChiemTopic(
        code="xuat_hanh", name_vi="Hỏi đi xa", name_han_viet="Xuất hành chiêm",
        keywords=["đi xa", "xuất hành", "đi công tác", "đi du lịch", "ra nước ngoài",
                  "chuyển nơi", "đi học xa"],
        description="Hỏi về việc đi xa, di chuyển, xuất ngoại",
        the_dung_focus="Thể = người đi, Dụng = nơi đến / đường đi",
        special_rules=[
            "Dụng sinh Thể → đi gặp may, nơi đến tốt",
            "Tỷ hoà → đi bình an, không gì đặc biệt",
            "Dụng khắc Thể → đi gặp trở ngại / nguy hiểm",
            "Quẻ có Thiên Mã / sao Mã → thuận đi",
            "Khảm (Thủy) → cẩn thận đường thủy",
            "Chấn (Mộc) → đi nhanh, công tác",
        ],
    ),
    "that_vat": ChiemTopic(
        code="that_vat", name_vi="Hỏi mất đồ", name_han_viet="Thất vật chiêm",
        keywords=["mất", "mất đồ", "thất lạc", "rơi", "bị trộm", "mất ví", "mất xe",
                  "tìm thấy được không"],
        description="Hỏi về đồ vật mất, có tìm thấy được không",
        the_dung_focus="Thể = người mất, Dụng = vật mất",
        special_rules=[
            "Dụng sinh Thể → vật trở về với mình",
            "Tỷ hoà → vật ở quanh quẩn, tìm sẽ thấy",
            "Thể khắc Dụng → có thể thu hồi nhưng phải tìm",
            "Dụng khắc Thể → khó tìm lại",
            "Quẻ có Khôn → đồ ở dưới đất / trong nhà",
            "Quẻ có Càn → đồ ở nơi cao / chỗ chủ",
        ],
    ),
    "tat_benh": ChiemTopic(
        code="tat_benh", name_vi="Hỏi bệnh tật", name_han_viet="Tật bệnh chiêm",
        keywords=["bệnh", "ốm", "đau", "sức khỏe", "tật", "chữa bệnh", "có khỏi",
                  "khám bệnh", "phẫu thuật"],
        description="Hỏi về bệnh tật, sức khỏe, chữa trị",
        the_dung_focus="Thể = người bệnh, Dụng = bệnh tật",
        special_rules=[
            "Thể vượng + Dụng suy → khỏi nhanh",
            "Dụng sinh Thể → có người chăm sóc, thuốc tốt",
            "Tỷ hoà + Thể vượng → bệnh nhẹ, tự khỏi",
            "Dụng khắc Thể → bệnh nặng, cần điều trị tích cực",
            "Thể suy + Dụng vượng → cảnh báo, cần chuyên gia",
            "Ly (Hỏa) ở Dụng → bệnh nóng, tim, đầu",
            "Khảm (Thủy) ở Dụng → bệnh thận, tiết niệu",
            "Tốn (Mộc) ở Dụng → bệnh gan, gió",
            "Cấn/Khôn (Thổ) ở Dụng → bệnh tì vị, đường tiêu hóa",
        ],
    ),
    "quan_tung": ChiemTopic(
        code="quan_tung", name_vi="Hỏi kiện tụng", name_han_viet="Quan tụng chiêm",
        keywords=["kiện tụng", "tòa án", "kiện cáo", "thưa kiện", "tranh chấp pháp lý",
                  "thắng kiện", "luật sư"],
        description="Hỏi về kiện tụng, tranh chấp, pháp lý",
        the_dung_focus="Thể = mình (nguyên đơn / bị đơn), Dụng = đối phương / tòa",
        special_rules=[
            "Thể khắc Dụng → mình thắng",
            "Dụng khắc Thể → mình thua",
            "Dụng sinh Thể → có quý nhân hỗ trợ",
            "Thể sinh Dụng → mình tốn tiền cho việc kiện",
            "Tỷ hoà → hòa giải, không kiện đến cùng",
            "Quẻ có hung sát → tổn thân, kiện kéo dài",
        ],
    ),
    "phan_mo": ChiemTopic(
        code="phan_mo", name_vi="Hỏi mồ mả", name_han_viet="Phần mộ chiêm",
        keywords=["mồ mả", "phần mộ", "chôn cất", "phong thủy mộ", "âm trạch",
                  "ông bà", "tổ tiên", "cải mả"],
        description="Hỏi về mồ mả, phong thủy âm trạch, tổ tiên",
        the_dung_focus="Thể = con cháu, Dụng = phần mộ / tổ tiên",
        special_rules=[
            "Dụng sinh Thể → mộ phù trợ con cháu, phát phúc",
            "Tỷ hoà → mộ yên ổn",
            "Thể khắc Dụng → con cháu phải tu sửa mộ",
            "Dụng khắc Thể → mộ bất lợi cho con cháu, cần cải táng",
            "Quẻ có Khôn (đất) vượng → đất tốt",
            "Cấn (núi) → mộ tựa núi, vững",
        ],
    ),
}


def detect_topic(question: str) -> Optional[ChiemTopic]:
    """Detect 1 trong 11 chiêm topics từ user_question.

    Returns ChiemTopic nếu match, None nếu không match (dùng generic).
    """
    if not question:
        return None
    q = question.lower()
    # Score by keyword count
    scores = {code: sum(1 for kw in t.keywords if kw in q) for code, t in CHIEM_TOPICS.items()}
    top_code = max(scores, key=scores.get)
    if scores[top_code] == 0:
        return None
    return CHIEM_TOPICS[top_code]


def interpret_by_topic(
    question: str,
    the_que: str,
    dung_que: str,
    relationship: str,
    auspice: str,
) -> dict:
    """Diễn giải Thể-Dụng theo topic detected từ câu hỏi.

    Args:
        question: câu hỏi user
        the_que: tên Thể quái (vd "Càn")
        dung_que: tên Dụng quái
        relationship: "dung_sinh_the" | "the_khac_dung" | ... (từ TheDungAnalysis)
        auspice: "cát" | "hung" | "bình"

    Returns:
        dict {
            "topic_detected": Optional[str],
            "topic_name": str,
            "topic_advice": str,           # advice cụ thể cho chiêm này
            "applicable_rules": list[str], # special rules apply cho lá số này
        }
    """
    topic = detect_topic(question)
    if not topic:
        return {
            "topic_detected": None,
            "topic_name": "Chiêm chung (không phân loại)",
            "topic_advice": "",
            "applicable_rules": [],
        }

    # Identify which special_rules có thể apply
    applicable = []
    text_to_scan = f"{the_que} {dung_que} {relationship} {auspice}".lower()
    for rule in topic.special_rules:
        rl = rule.lower()
        # Apply nếu rule mention sao đang ở chart hoặc relationship trùng
        if the_que.lower() in rl or dung_que.lower() in rl:
            applicable.append(rule)
        elif relationship.replace("_", " ") in rl.replace("→", "→"):
            applicable.append(rule)

    # Build advice
    advice_parts = [
        f"Topic detected: **{topic.name_han_viet}** — {topic.description}",
        f"Trong chiêm này: {topic.the_dung_focus}",
    ]
    if applicable:
        advice_parts.append("Quy tắc áp dụng cho lá số này:")
        for r in applicable[:4]:
            advice_parts.append(f"  • {r}")
    else:
        advice_parts.append(f"Quy tắc chung: xét Thể-Dụng theo auspice = {auspice}")

    return {
        "topic_detected": topic.code,
        "topic_name": topic.name_han_viet,
        "topic_description": topic.description,
        "topic_advice": "\n".join(advice_parts),
        "applicable_rules": applicable,
        "the_dung_focus": topic.the_dung_focus,
    }


def list_all_topics() -> list[dict]:
    """List all 11 chiêm topics for UI / API."""
    return [
        {
            "code": t.code,
            "name_vi": t.name_vi,
            "name_han_viet": t.name_han_viet,
            "description": t.description,
            "keywords": t.keywords,
            "the_dung_focus": t.the_dung_focus,
        }
        for t in CHIEM_TOPICS.values()
    ]


if __name__ == "__main__":
    import json
    # Smoke test
    tests = [
        ("Anh có nên mua nhà mới năm nay không?", "Càn", "Khôn", "the_khac_dung", "cát"),
        ("Vợ chồng em gần đây hay cãi vã, có hợp không?", "Ly", "Khảm", "dung_khac_the", "hung"),
        ("Con em bệnh nặng, có khỏi được không?", "Khôn", "Ly", "dung_sinh_the", "cát"),
        ("Em định mở quán cà phê, làm ăn được không?", "Càn", "Đoài", "ti_hoa", "bình"),
        ("Em mất ví, có tìm lại được không?", "Khôn", "Cấn", "ti_hoa", "bình"),
        ("Trời ngày mai có mưa không?", "Càn", "Khảm", "the_khac_dung", "cát"),
    ]
    for q, th, du, rel, ausp in tests:
        r = interpret_by_topic(q, th, du, rel, ausp)
        print(f"\nQ: {q}")
        print(f"  → {r['topic_name']} (applicable: {len(r['applicable_rules'])} rules)")
        for rl in r['applicable_rules'][:2]:
            print(f"     • {rl}")
