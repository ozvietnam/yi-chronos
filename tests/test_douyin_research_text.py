from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "douyin_channel_research"))

from douyin_research.text import clean_vtt, deterministic_clean, slugify_channel


def test_slugify_channel_user_url():
    assert slugify_channel("https://www.douyin.com/user/abc?from=foo") == "user-abc"


def test_clean_vtt_removes_timestamps_and_duplicates():
    raw = """WEBVTT

1
00:00:00.000 --> 00:00:01.000
你好

2
00:00:01.000 --> 00:00:02.000
你好

3
00:00:02.000 --> 00:00:03.000
今天讲紫微斗数
"""
    assert clean_vtt(raw) == "你好 今天讲紫微斗数"


def test_deterministic_clean_removes_social_boilerplate():
    assert deterministic_clean("记得关注，今天讲紫微斗数 #douyin") == "今天讲紫微斗数"
