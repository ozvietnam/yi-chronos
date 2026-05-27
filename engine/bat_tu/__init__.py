"""Bát Tự (Tứ Trụ / Tử Bình) engine package — MVP v1.

Public API:
    cast_bat_tu(*, birth_datetime_local, timezone='Asia/Ho_Chi_Minh', gender='nam')

Foundation for the upcoming Bát Tự Hà Lạc cross-module (mục 5.1 in the project plan).
"""

from .ai_chat import chat_about_chart
from .auspicious_event import pick_auspicious_dates
from .cach_cuc_extended import detect_extreme_pattern
from .cast import METHOD_ID, SOURCE_REF, cast_bat_tu
from .compatibility import analyze_compatibility
from .hon_nhan import analyze_hon_nhan
from .luan_giai import compose_luan_giai
from .luc_than import analyze_luc_than
from .luu_nien import analyze_luu_nien
from .su_nghiep import analyze_su_nghiep
from .suc_khoe import analyze_suc_khoe
from .tai_van import analyze_tai_van
from .thap_than import thap_than_of
from .tu_tru import extract_tu_tru


__all__ = [
    "METHOD_ID",
    "SOURCE_REF",
    "analyze_compatibility",
    "analyze_hon_nhan",
    "pick_auspicious_dates",
    "analyze_luu_nien",
    "analyze_su_nghiep",
    "analyze_suc_khoe",
    "analyze_tai_van",
    "cast_bat_tu",
    "compose_luan_giai",
    "detect_extreme_pattern",
    "extract_tu_tru",
    "thap_than_of",
]
