from engine.luc_hao import _detect_target_relation, _select_dung_than_line


def _mock_lines():
    return [
        {"line_position": 1, "luc_than": "Huynh Đệ", "moving": False},
        {"line_position": 2, "luc_than": "Phụ Mẫu", "moving": False},
        {"line_position": 3, "luc_than": "Thê Tài", "moving": False},
        {"line_position": 4, "luc_than": "Quan Quỷ", "moving": True},
        {"line_position": 5, "luc_than": "Tử Tôn", "moving": False},
        {"line_position": 6, "luc_than": "Huynh Đệ", "moving": False},
    ]


def test_detect_target_relation_finance():
    assert _detect_target_relation("Khi nào tiền tài về tài khoản?") == "Thê Tài"


def test_detect_target_relation_health():
    assert _detect_target_relation("Sức khỏe tuần này có ổn không?") == "Quan Quỷ"


def test_select_dung_than_by_domain_relation():
    line = _select_dung_than_line(_mock_lines(), "Công việc sắp tới có thuận không?")
    assert line["luc_than"] == "Quan Quỷ"


def test_select_dung_than_fallback_to_first_moving_line():
    lines = [
        {"line_position": 1, "luc_than": "Huynh Đệ", "moving": False},
        {"line_position": 2, "luc_than": "Phụ Mẫu", "moving": True},
        {"line_position": 3, "luc_than": "Huynh Đệ", "moving": False},
    ]
    line = _select_dung_than_line(lines, "Câu hỏi không có keyword")
    assert line["line_position"] == 2


def test_select_dung_than_fallback_to_line_three_when_no_moving():
    lines = [
        {"line_position": 1, "luc_than": "Huynh Đệ", "moving": False},
        {"line_position": 2, "luc_than": "Phụ Mẫu", "moving": False},
        {"line_position": 3, "luc_than": "Huynh Đệ", "moving": False},
    ]
    line = _select_dung_than_line(lines, "Câu hỏi tổng quát")
    assert line["line_position"] == 3
