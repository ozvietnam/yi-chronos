"""Engine Kỳ Môn Độn Giáp (奇門遁甲) — trường phái thứ 6 của YI-Chronos.

Tổ sư: Lưu Bá Ôn (1311-1375).
Paradigm: ĐỌC ĐỒNG DẠNG, không predict (Iron Rule #4 + #6).

Core engine vendor từ kentang2017/kinqimen (MIT), wrap + dịch TQ→Việt.
"""

from .cast import cast
from .wiki import WIKI, get_concept, list_categories

__all__ = ["cast", "WIKI", "get_concept", "list_categories"]
