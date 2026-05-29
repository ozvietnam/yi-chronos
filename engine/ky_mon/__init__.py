"""Engine Kỳ Môn Độn Giáp (奇門遁甲) — trường phái thứ 6 của YI-Chronos.

Tổ sư: Lưu Bá Ôn (1311-1375).
Paradigm: ĐỌC ĐỒNG DẠNG, không predict (Iron Rule #4 + #6).

Core engine vendor từ kentang2017/kinqimen (MIT), wrap + dịch TQ→Việt.
"""

from .cast import cast
from .deep_readings import (
    COMBO_LUAN_GIAI, MON_DEEP, THAN_DEEP, TINH_DEEP,
    interpret_cell_deep, list_combo_patterns,
)
from .personal_reading import interpret_personal_chart, list_founder_data
from .tasks import TASK_PROFILES, analyze_for_task, list_tasks
from .wiki import WIKI, get_concept, list_categories

__all__ = [
    "cast", "WIKI", "get_concept", "list_categories",
    "TASK_PROFILES", "analyze_for_task", "list_tasks",
    "interpret_personal_chart", "list_founder_data",
    "MON_DEEP", "TINH_DEEP", "THAN_DEEP", "COMBO_LUAN_GIAI",
    "interpret_cell_deep", "list_combo_patterns",
]
