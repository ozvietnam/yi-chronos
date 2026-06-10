"""Tests engine Thiết Bản tầng A — tra cứu điều văn (đọc DB thật, read-only)."""
import pytest

from engine.thiet_ban import verses as V


def test_stats_co_du_lieu():
    s = V.stats()
    assert s["total"] >= 10000
    assert s["with_vi"] >= 8000
    assert s["seq_range"][0] >= 990 and s["seq_range"][1] <= 13000


def test_verse_1002_cross_verified():
    """Điều 1002 đã đối chiếu ảnh scan (2026-06-10)."""
    v = V.get_verse(1002)
    assert v is not None
    assert v["zh"] == "寄人廊庙何如自立门户"
    assert v["volume"] == "子集"


def test_verse_khong_ton_tai():
    assert V.get_verse(99999) is None


def test_range_gioi_han():
    rows = V.get_range(1001, 1500)
    assert len(rows) <= 50
    assert all(1001 <= r["seq_no"] <= 1500 for r in rows)


def test_search_vi_fts():
    r = V.search("huynh đệ")
    assert r["mode"] == "vi-fts"
    assert len(r["results"]) > 0


def test_search_zh_like():
    r = V.search("兄弟")
    assert r["mode"] == "zh-like"
    assert len(r["results"]) > 0
    assert all("兄弟" in x["zh"] for x in r["results"])


def test_volume_phan_trang():
    r = V.get_volume("子集", offset=0, limit=10)
    assert r["total"] > 100
    assert len(r["results"]) == 10
