from core.hexagram import (
    apply_moving_lines,
    classify_moving_lines,
    compose_hexagram_binary,
    get_hexagram_by_binary,
    get_hexagram_by_name,
    list_hexagrams,
    flip_line,
    generate_transitions,
)


def test_canonical_qian_and_kun_binary_mapping():
    assert get_hexagram_by_binary("111111").name_vi == "Kiền"
    assert get_hexagram_by_binary("000000").name_vi == "Khôn"


def test_line_flip_uses_line_one_as_bottom_line():
    assert flip_line("111111", 1) == "111110"
    assert flip_line("000000", 6) == "100000"


def test_all_hexagrams_are_unique_and_transitions_are_valid():
    hexagrams = list_hexagrams()
    binaries = {item.binary for item in hexagrams}
    ids = {item.id for item in hexagrams}

    assert len(hexagrams) == 64
    assert len(binaries) == 64
    assert len(ids) == 64

    for item in hexagrams:
        transitions = generate_transitions(item.binary)
        assert len(transitions) == 6
        assert all(get_hexagram_by_binary(binary) for binary in transitions.values())


def test_lookup_by_vietnamese_name():
    assert get_hexagram_by_name("Càn").binary == "111111"
    assert get_hexagram_by_name("Kiền").binary == "111111"
    assert get_hexagram_by_name("Khôn").binary == "000000"


def test_king_wen_index_and_binary_are_complete():
    hexagrams = list_hexagrams()
    assert len({item.king_wen_index for item in hexagrams}) == 64
    assert len({item.binary for item in hexagrams}) == 64


def test_compose_hexagram_and_moving_lines():
    assert compose_hexagram_binary("Khảm", "Chấn") == "010001"  # Truân
    assert apply_moving_lines("111111", [1, 6]) == "011110"


def test_moving_line_policy_buckets():
    assert classify_moving_lines([]) == "original_judgement"
    assert classify_moving_lines([2]) == "moving_line_texts"
    assert classify_moving_lines([1, 2, 3]) == "dual_hexagram_context"
    assert classify_moving_lines([1, 2, 3, 4]) == "transformed_focus"
    assert classify_moving_lines([1, 2, 3, 4, 5, 6]) == "fully_transformed"
