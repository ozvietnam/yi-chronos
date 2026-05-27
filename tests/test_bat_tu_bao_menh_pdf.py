"""Tests for engine.bat_tu.bao_menh_pdf — PDF Báo Mệnh generation."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from engine.bat_tu.bao_menh_pdf import (
    compose_bao_menh_html,
    generate_bao_menh_pdf,
)


def test_compose_html_returns_string():
    html = compose_bao_menh_html(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert isinstance(html, str)
    assert len(html) > 5000  # comprehensive content


def test_html_contains_all_sections():
    html = compose_bao_menh_html(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    expected_sections = [
        "Luận Giải Tổng Hợp",
        "Lưu Niên",
        "Hôn Nhân",
        "Sự Nghiệp",
        "Tài Vận",
        "Sức Khỏe",
        "Hà Lạc",
    ]
    for sec in expected_sections:
        assert sec in html, f"Missing section: {sec}"


def test_html_contains_paradigm():
    html = compose_bao_menh_html(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert "KHÔNG dự đoán" in html


def test_html_contains_founder_pillars():
    html = compose_bao_menh_html(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    # Founder Tứ Trụ: Mậu Thìn / Đinh Tỵ / Giáp Tuất / Giáp Tý
    assert "Mậu" in html and "Thìn" in html
    assert "Đinh" in html and "Tỵ" in html
    assert "Giáp" in html
    assert "Tuất" in html


def test_pdf_generation_bytes():
    pdf_bytes = generate_bao_menh_pdf(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 50_000  # comprehensive PDF


def test_pdf_save_to_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_bao_menh.pdf"
        pdf_bytes = generate_bao_menh_pdf(
            birth_datetime_local="1988-06-05T23:30",
            timezone="Asia/Ho_Chi_Minh",
            gender="nam",
            output_path=out_path,
        )
        assert out_path.exists()
        assert out_path.read_bytes()[:4] == b"%PDF"
        assert out_path.stat().st_size > 50_000


def test_female_chart_works():
    html = compose_bao_menh_html(
        birth_datetime_local="1995-08-15T14:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    assert isinstance(html, str)
    assert len(html) > 5000


def test_explicit_current_age():
    html = compose_bao_menh_html(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
        current_age=50,  # explicit override
    )
    assert isinstance(html, str)
