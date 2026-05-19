"""Tests for core.yi64.slugs — hexagram slug encode/decode."""

from __future__ import annotations

import pytest

from core.yi64.slugs import (
    king_wen_from_slug,
    reverse_slug_table,
    slug_for,
    slug_table,
    to_slug_segment,
)


def test_slug_table_has_64_entries():
    table = slug_table()
    assert len(table) == 64
    assert set(table.keys()) == set(range(1, 65))


def test_reverse_lookup_round_trip():
    table = slug_table()
    for kw, slug in table.items():
        assert king_wen_from_slug(slug) == kw


def test_known_slugs_match_kabala_convention():
    """Spot-check well-known hexagrams against the standard 'thượng-hạ-tên' form."""
    assert slug_for(1) == "1-thien-thien-kien"     # Càn/Càn → Kiền
    assert slug_for(2) == "2-dia-dia-khon"          # Khôn/Khôn → Khôn
    assert slug_for(3) == "3-thuy-loi-truan"        # Khảm/Chấn → Truân
    assert slug_for(11) == "11-dia-thien-thai"      # Khôn/Càn → Thái
    assert slug_for(12) == "12-thien-dia-bi"        # Càn/Khôn → Bĩ


def test_to_slug_segment_strips_vietnamese_diacritics():
    assert to_slug_segment("Thủy") == "thuy"
    assert to_slug_segment("Đại Hữu") == "dai-huu"
    assert to_slug_segment("Đoài") == "doai"
    assert to_slug_segment("Vô Vọng") == "vo-vong"


def test_king_wen_from_slug_tolerant_match():
    """Slug with leading int prefix should still resolve."""
    assert king_wen_from_slug("3-thuy-loi-truan") == 3
    assert king_wen_from_slug("3-anything-else") == 3
    assert king_wen_from_slug("3") == 3


def test_king_wen_from_slug_rejects_invalid():
    assert king_wen_from_slug("") is None
    assert king_wen_from_slug("99-x") is None
    assert king_wen_from_slug("not-a-slug") is None
    assert king_wen_from_slug(None) is None  # type: ignore[arg-type]


def test_slug_for_rejects_out_of_range():
    with pytest.raises(ValueError):
        slug_for(0)
    with pytest.raises(ValueError):
        slug_for(65)


def test_reverse_slug_table_is_bijective():
    """No two hexagrams share a slug."""
    rev = reverse_slug_table()
    assert len(rev) == 64


def test_api_hexagram_by_slug_endpoint():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)

    response = client.get("/api/hexagram-by-slug/3-thuy-loi-truan")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["king_wen_index"] == 3
    assert payload["canonical_slug"] == "3-thuy-loi-truan"
    assert payload["record"]["name_vi"] == "Truân"


def test_api_hexagram_by_slug_not_found():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)

    response = client.get("/api/hexagram-by-slug/invalid-slug")
    assert response.status_code == 200
    assert response.json()["status"] == "not_found"


def test_api_hexagram_slugs_table_endpoint():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)

    response = client.get("/api/hexagram-slugs")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    # JSON serializes int keys as strings.
    assert len(payload["slugs"]) == 64
    assert payload["slugs"]["3"] == "3-thuy-loi-truan"
