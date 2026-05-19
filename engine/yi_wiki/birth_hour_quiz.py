"""Birth Hour Quiz — Trắc nghiệm xác định giờ sinh (chi giờ).

Tiền đề:
  Theo Bát Tự cổ truyền, giờ sinh ảnh hưởng tính cách + tướng mạo cụ thể.
  Khi đệ tử KHÔNG nhớ giờ sinh, em hỏi 8 câu trắc nghiệm về:
    - Cơ thể (xoáy tóc, dáng)
    - Tính cách (hướng nội / hướng ngoại)
    - Thói quen (thức dậy tự nhiên, năng lượng cao điểm)
    - Anh chị em (số người, vai trò)
  → Mapping 12 chi giờ → score cao nhất = giờ likely.

Phương pháp này phổ biến trong các sách Tử Vi + Tử Bình VN-TQ.
"""
from __future__ import annotations

from dataclasses import dataclass


# 12 chi giờ với mô tả
CHI_HOURS = {
    "Tý":   {"range": "23h-1h",   "label": "Giờ Tý (Chuột)",
             "trait": "Thông minh đêm, sao Bắc Đẩu, thường có 1 xoáy đỉnh đầu", "hanh": "Thuỷ"},
    "Sửu":  {"range": "1h-3h",    "label": "Giờ Sửu (Trâu)",
             "trait": "Cần cù kiên nhẫn, ngủ sớm dậy sớm, ổn định", "hanh": "Thổ"},
    "Dần":  {"range": "3h-5h",    "label": "Giờ Dần (Hổ)",
             "trait": "Mạnh mẽ độc lập, lãnh đạo bẩm sinh, thẳng tính", "hanh": "Mộc"},
    "Mão":  {"range": "5h-7h",    "label": "Giờ Mão (Mèo/Thỏ)",
             "trait": "Cẩn trọng nhân hậu, dáng cao thon, da trắng", "hanh": "Mộc"},
    "Thìn": {"range": "7h-9h",    "label": "Giờ Thìn (Rồng)",
             "trait": "Khởi đầu mạnh, dáng to khoẻ, thường được người trọng", "hanh": "Thổ"},
    "Tỵ":   {"range": "9h-11h",   "label": "Giờ Tỵ (Rắn)",
             "trait": "Tinh tế khôn ngoan, thâm trầm, có chiều sâu", "hanh": "Hoả"},
    "Ngọ":  {"range": "11h-13h",  "label": "Giờ Ngọ (Ngựa)",
             "trait": "Nhiệt huyết nóng tính, không thích ngồi yên, năng lượng cao", "hanh": "Hoả"},
    "Mùi":  {"range": "13h-15h",  "label": "Giờ Mùi (Dê)",
             "trait": "Hiền lành nghệ sĩ, thích đẹp, hơi do dự", "hanh": "Thổ"},
    "Thân": {"range": "15h-17h",  "label": "Giờ Thân (Khỉ)",
             "trait": "Nhanh nhẹn linh hoạt, học nhanh, thông minh xã hội", "hanh": "Kim"},
    "Dậu":  {"range": "17h-19h",  "label": "Giờ Dậu (Gà)",
             "trait": "Chính xác kỷ luật, ngăn nắp, đúng giờ", "hanh": "Kim"},
    "Tuất": {"range": "19h-21h",  "label": "Giờ Tuất (Chó)",
             "trait": "Trung thành chân thật, bảo vệ người thân, có nguyên tắc", "hanh": "Thổ"},
    "Hợi":  {"range": "21h-23h",  "label": "Giờ Hợi (Lợn)",
             "trait": "Bình lặng phúc hậu, dáng đầy đặn, hưởng thụ cuộc sống", "hanh": "Thuỷ"},
}

# Câu hỏi trắc nghiệm — mỗi câu có 4 lựa chọn,
# mỗi lựa chọn gán điểm cho 3 chi giờ liên quan
QUESTIONS = [
    {
        "id": "wake_natural",
        "question": "Khi không có lịch hẹn, anh thường tự nhiên thức dậy vào khoảng nào?",
        "options": [
            {"id": "a", "label": "Trước 5h sáng — thức rất sớm",
             "scores": {"Dần": 3, "Mão": 2, "Sửu": 1}},
            {"id": "b", "label": "5h-8h — bình minh",
             "scores": {"Mão": 3, "Thìn": 3, "Dần": 1}},
            {"id": "c", "label": "8h-11h — sáng muộn",
             "scores": {"Thìn": 2, "Tỵ": 3, "Mùi": 1}},
            {"id": "d", "label": "Sau 11h — gần trưa hoặc trưa",
             "scores": {"Ngọ": 3, "Mùi": 2, "Tý": 1}},
        ],
    },
    {
        "id": "energy_peak",
        "question": "Năng lượng / tỉnh táo cao nhất của anh thường vào giờ nào trong ngày?",
        "options": [
            {"id": "a", "label": "Sáng sớm (5h-9h)",
             "scores": {"Mão": 2, "Thìn": 3, "Dần": 2}},
            {"id": "b", "label": "Giữa sáng tới trưa (9h-13h)",
             "scores": {"Tỵ": 3, "Ngọ": 3}},
            {"id": "c", "label": "Chiều (13h-17h)",
             "scores": {"Mùi": 2, "Thân": 3, "Dậu": 1}},
            {"id": "d", "label": "Tối / đêm khuya (sau 19h)",
             "scores": {"Tuất": 2, "Hợi": 3, "Tý": 3}},
        ],
    },
    {
        "id": "personality",
        "question": "Tính cách của anh gần với hình ảnh nào nhất?",
        "options": [
            {"id": "a", "label": "Mạnh mẽ, lãnh đạo, độc lập (Hổ/Rồng)",
             "scores": {"Dần": 3, "Thìn": 3, "Ngọ": 1}},
            {"id": "b", "label": "Khôn ngoan tinh tế, suy nghĩ sâu (Rắn/Khỉ)",
             "scores": {"Tỵ": 3, "Thân": 3, "Tý": 1}},
            {"id": "c", "label": "Hiền lành nhân hậu, cẩn trọng (Thỏ/Dê)",
             "scores": {"Mão": 3, "Mùi": 3, "Hợi": 1}},
            {"id": "d", "label": "Trung thành kỷ luật, đúng giờ (Chó/Gà/Trâu)",
             "scores": {"Tuất": 3, "Dậu": 3, "Sửu": 2}},
        ],
    },
    {
        "id": "body_shape",
        "question": "Vóc dáng / khuôn mặt của anh có đặc điểm gì?",
        "options": [
            {"id": "a", "label": "Cao, dáng thon, mặt dài",
             "scores": {"Mão": 3, "Dần": 2, "Tỵ": 1}},
            {"id": "b", "label": "To khoẻ, vai rộng, dáng đầy đặn",
             "scores": {"Thìn": 3, "Tuất": 2, "Sửu": 1}},
            {"id": "c", "label": "Trung bình cân đối, mặt tròn",
             "scores": {"Ngọ": 2, "Mùi": 2, "Hợi": 2}},
            {"id": "d", "label": "Nhỏ nhanh nhẹn, mặt sắc",
             "scores": {"Thân": 3, "Dậu": 3, "Tý": 1}},
        ],
    },
    {
        "id": "siblings_position",
        "question": "Trong nhà anh là con thứ mấy / có anh chị em không?",
        "options": [
            {"id": "a", "label": "Con cả / con duy nhất, có vai trò chỉ huy",
             "scores": {"Dần": 2, "Thìn": 2, "Ngọ": 2}},
            {"id": "b", "label": "Con giữa, hoà giải, đa năng",
             "scores": {"Mão": 2, "Mùi": 2, "Thân": 2}},
            {"id": "c", "label": "Con út, được cưng chiều",
             "scores": {"Tỵ": 2, "Dậu": 2, "Hợi": 2}},
            {"id": "d", "label": "Không có anh chị em",
             "scores": {"Tý": 2, "Sửu": 2, "Tuất": 2}},
        ],
    },
    {
        "id": "challenge",
        "question": "Khi gặp khó khăn lớn, phản ứng đầu tiên của anh là?",
        "options": [
            {"id": "a", "label": "Lao vào giải quyết ngay — không suy nghĩ nhiều",
             "scores": {"Dần": 3, "Ngọ": 2, "Thìn": 2}},
            {"id": "b", "label": "Phân tích kỹ trước, lập kế hoạch",
             "scores": {"Tỵ": 2, "Dậu": 3, "Sửu": 2}},
            {"id": "c", "label": "Tham khảo người khác, không quyết một mình",
             "scores": {"Mùi": 3, "Hợi": 2, "Mão": 2}},
            {"id": "d", "label": "Lùi 1 bước, chờ thời cơ",
             "scores": {"Tuất": 2, "Thân": 2, "Tý": 2}},
        ],
    },
    {
        "id": "sleep_pattern",
        "question": "Giờ đi ngủ của anh thường là?",
        "options": [
            {"id": "a", "label": "Trước 22h — ngủ sớm",
             "scores": {"Mão": 2, "Thìn": 2, "Sửu": 2}},
            {"id": "b", "label": "22h-23h — bình thường",
             "scores": {"Tỵ": 2, "Mùi": 2, "Dậu": 2}},
            {"id": "c", "label": "23h-1h sáng — hơi muộn",
             "scores": {"Ngọ": 2, "Tuất": 2, "Hợi": 2}},
            {"id": "d", "label": "Sau 1h sáng — rất khuya",
             "scores": {"Tý": 3, "Dần": 2, "Thân": 1}},
        ],
    },
    {
        "id": "hair_whorl",
        "question": "Anh có bao nhiêu xoáy tóc trên đỉnh đầu?",
        "options": [
            {"id": "a", "label": "1 xoáy duy nhất",
             "scores": {"Tý": 3, "Ngọ": 3, "Mão": 2, "Dậu": 2}},
            {"id": "b", "label": "2 xoáy",
             "scores": {"Dần": 2, "Thìn": 2, "Thân": 2, "Tuất": 2}},
            {"id": "c", "label": "Không có xoáy rõ / khó nhận biết",
             "scores": {"Sửu": 2, "Mùi": 2, "Hợi": 2, "Tỵ": 2}},
        ],
    },
]


@dataclass
class QuizResult:
    scores: dict[str, int]
    top3: list[tuple[str, int]]
    most_likely: str
    confidence: str
    interpretation: dict


def analyze_quiz(answers: dict[str, str]) -> QuizResult:
    """Phân tích đáp án.

    Args:
        answers: {question_id: option_id} — vd {"wake_natural": "b", "energy_peak": "a", ...}
    """
    scores = {chi: 0 for chi in CHI_HOURS}

    for q in QUESTIONS:
        qid = q["id"]
        chosen_id = answers.get(qid)
        if not chosen_id:
            continue
        opt = next((o for o in q["options"] if o["id"] == chosen_id), None)
        if not opt:
            continue
        for chi, pts in opt["scores"].items():
            scores[chi] += pts

    # Top 3
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    top3 = sorted_scores[:3]

    if not top3 or top3[0][1] == 0:
        return QuizResult(
            scores=scores, top3=top3,
            most_likely="(không đủ dữ liệu)",
            confidence="N/A",
            interpretation={},
        )

    most_likely = top3[0][0]
    top_score = top3[0][1]
    runner_up = top3[1][1] if len(top3) > 1 else 0

    # Confidence
    if top_score - runner_up >= 5:
        confidence = "Cao"
    elif top_score - runner_up >= 2:
        confidence = "Vừa"
    else:
        confidence = "Thấp — cần thêm dữ liệu"

    return QuizResult(
        scores=scores, top3=top3,
        most_likely=most_likely,
        confidence=confidence,
        interpretation=CHI_HOURS[most_likely],
    )


def get_questions() -> list[dict]:
    """Return all questions (without scoring details — for UI)."""
    return [
        {
            "id": q["id"],
            "question": q["question"],
            "options": [{"id": o["id"], "label": o["label"]} for o in q["options"]],
        }
        for q in QUESTIONS
    ]


if __name__ == "__main__":
    # Test: giả lập đáp án của bạn anh sinh giờ Thìn 1988
    answers = {
        "wake_natural": "b",      # 5h-8h
        "energy_peak": "a",       # sáng sớm
        "personality": "a",       # mạnh mẽ
        "body_shape": "b",        # to khoẻ
        "siblings_position": "a", # con cả
        "challenge": "a",         # lao vào
        "sleep_pattern": "a",     # trước 22h
        "hair_whorl": "b",        # 2 xoáy
    }
    r = analyze_quiz(answers)
    print(f"Most likely: {r.most_likely} ({r.interpretation['range']})")
    print(f"Confidence: {r.confidence}")
    print(f"Top 3:")
    for chi, sc in r.top3:
        print(f"  • {chi:5} ({CHI_HOURS[chi]['range']:10}) score={sc}")
