"""Module Librarian — introspects all engines + builds knowledge index.

YI-Hermes uses this to answer "Mai Hoa khác gì Liên Hoa?" without hallucinating.

Strategy:
1. Walk `engine/` and `core/` directories.
2. For each subpackage, read its `__init__.py` docstring + module-level docstrings.
3. Detect public API (what's in `__all__`).
4. Aggregate into a static JSON index, refreshed on demand.
"""

from __future__ import annotations

import importlib
import inspect
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# Modules that YI-Hermes should know about (in Vietnamese, user-facing context).
KNOWN_MODULES: dict[str, dict] = {
    "engine.mai_hoa_implicit": {   # not a real package, NNTT lives in core
        "name_vi": "Mai Hoa Dịch Số",
        "icon": "🌸",
        "school": "đông",
        "intro_vi": (
            "Phép gieo quẻ Thiệu Khang Tiết — dùng Niên-Nguyệt-Nhật-Thời + quan sát "
            "hiện tượng. Output: Quẻ Chánh + Hổ + Biến + 5 quẻ phái sinh."
        ),
        "primary_files": ["core/yi64/derivations/mai_hoa_nntt.py"],
        "primary_use": "Quan sát hiện tượng + gieo quẻ thời điểm cụ thể",
    },
    "engine.luc_hao": {
        "name_vi": "Lục Hào Văn Vương",
        "icon": "☷",
        "school": "đông",
        "intro_vi": (
            "Phép gieo 3 xu → 6 hào. Chọn Dụng Thần theo lục thân, đánh giá vượng/suy "
            "qua nguyệt-nhật-tuần-không-phá. Có lớp Kinh Phòng (8 cung + Najia + 伏神 + 28-tú)."
        ),
        "primary_files": ["engine/luc_hao/cast.py", "engine/luc_hao/jingfang.py"],
        "primary_use": "Câu hỏi cụ thể có/không, timing ngắn hạn",
    },
    "engine.lien_hoa": {
        "name_vi": "Liên Hoa Độn Pháp",
        "icon": "☘",
        "school": "đông",
        "intro_vi": (
            "Gieo bằng 2 số tâm ý → 5/9/13 Không Thời Sự liên hoàn. Tách hoàn toàn "
            "khỏi Mai Hoa. Có luận sự đầy đủ (vận đời / tài lộc / hôn nhân / nhà cửa / "
            "sức khỏe / xuất hành) + deeper layer (4 domain bổ sung)."
        ),
        "primary_files": ["engine/lien_hoa/cast.py", "engine/lien_hoa/luan_su.py"],
        "primary_use": "Câu chuyện theo chuỗi phase, đa lĩnh vực",
    },
    "engine.tu_vi": {
        "name_vi": "Tử Vi Đẩu Số (Bắc Phái)",
        "icon": "🔮",
        "school": "đông",
        "intro_vi": (
            "An sao 14 chính tinh + 6 phụ tinh + 7 sát tinh + Tứ Hóa vào 12 cung. "
            "Đại Vận 12 cycles + Tiểu Hạn + Lưu Trú Sao năm. Có interpretation engine + "
            "schema 14 chính tinh tích cực/tiêu cực."
        ),
        "primary_files": [
            "engine/tu_vi/an_sao.py",
            "engine/tu_vi/chinh_tinh.py",
            "engine/tu_vi/interpretation.py",
            "engine/tu_vi/luu_tru.py",
        ],
        "primary_use": "Vận lớn 10-năm, từng giai đoạn đời",
    },
    "engine.bat_tu": {
        "name_vi": "Bát Tự Tử Bình",
        "icon": "🪙",
        "school": "đông",
        "intro_vi": (
            "Tứ Trụ (Năm/Tháng/Ngày/Giờ) + Thập Thần + Ngũ Hành cân bằng + Vòng Trường "
            "Sinh + 15 Thần Sát + Dụng Thần + Cách Cục + Đại Vận (tiết khí 3-day rule)."
        ),
        "primary_files": [
            "engine/bat_tu/cast.py",
            "engine/bat_tu/dung_than.py",
            "engine/bat_tu/cach_cuc.py",
        ],
        "primary_use": "Gốc rễ ngũ hành cá nhân, cân bằng năng lượng",
    },
    "engine.ha_lac": {
        "name_vi": "Hà Lạc Lý Số",
        "icon": "⭐",
        "school": "đông",
        "intro_vi": (
            "Từ Tứ Trụ → 2 quẻ Tiên thiên + Hậu thiên + 12 hào ~84 năm cuộc đời. "
            "Sách Học Năng 1974 + Chen Tuan lineage. Differentiator (Kabala có nhắc "
            "nhưng không ship)."
        ),
        "primary_files": ["engine/ha_lac/cast.py", "engine/ha_lac/quai_assembly.py"],
        "primary_use": "Bản chất bẩm sinh vs cách vận hành đời người",
    },
    "engine.western_astro": {   # collection of western files
        "name_vi": "Chiêm Tinh Phương Tây",
        "icon": "♈",
        "school": "tây",
        "intro_vi": (
            "Bản đồ sao natal (10 hành tinh + aspects + dignity), Transits, "
            "Progressions, Solar/Lunar Returns, Eclipses, Solar Arc. Frame tâm lý "
            "Jung + chiêm tinh hiện đại."
        ),
        "primary_files": [
            "engine/sky.py", "engine/life_timeline.py",
            "engine/transit_timeline.py", "engine/progressions.py",
        ],
        "primary_use": "Tâm lý nội tâm, khung Jung + transit timing",
    },
}


@dataclass(frozen=True)
class ModuleSummary:
    """One module / school summary for the librarian index."""

    key: str
    name_vi: str
    icon: str
    school: str
    intro_vi: str
    primary_files: list[str]
    primary_use: str
    docstring_extract: str = ""    # first paragraph of __init__.py docstring
    public_symbols: list[str] = None  # type: ignore[assignment]

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["public_symbols"] is None:
            d["public_symbols"] = []
        return d


def _try_import(module_path: str) -> str:
    """Try to import a module + return its docstring excerpt (first paragraph)."""
    try:
        mod = importlib.import_module(module_path)
        doc = inspect.getdoc(mod) or ""
        # First paragraph
        if "\n\n" in doc:
            doc = doc.split("\n\n", 1)[0]
        return doc[:500]
    except Exception:
        return ""


def _try_public_symbols(module_path: str) -> list[str]:
    """Get __all__ exports if available."""
    try:
        mod = importlib.import_module(module_path)
        if hasattr(mod, "__all__"):
            return list(mod.__all__)
        # Fall back to public attributes
        return [name for name in dir(mod) if not name.startswith("_")][:20]
    except Exception:
        return []


@lru_cache(maxsize=1)
def _build_index() -> dict[str, ModuleSummary]:
    """Walk known modules, attempt to extract real docstrings + symbols."""
    out: dict[str, ModuleSummary] = {}
    for key, meta in KNOWN_MODULES.items():
        docstring = ""
        symbols: list[str] = []
        # Try import (only for real packages — engine.* without _implicit suffix).
        if not key.endswith("_implicit") and not key.endswith("_astro"):
            docstring = _try_import(key)
            symbols = _try_public_symbols(key)
        out[key] = ModuleSummary(
            key=key,
            name_vi=meta["name_vi"],
            icon=meta["icon"],
            school=meta["school"],
            intro_vi=meta["intro_vi"],
            primary_files=list(meta["primary_files"]),
            primary_use=meta["primary_use"],
            docstring_extract=docstring,
            public_symbols=symbols,
        )
    return out


class ModuleLibrarian:
    """Public interface for the module index."""

    def list_modules(self) -> list[dict]:
        """All known modules sorted by school (Đông first, then Tây)."""
        idx = _build_index()
        out = list(idx.values())
        out.sort(key=lambda m: (0 if m.school == "đông" else 1, m.name_vi))
        return [m.to_dict() for m in out]

    def get(self, key: str) -> ModuleSummary | None:
        return _build_index().get(key)

    def find_by_name_vi(self, name_substr: str) -> list[ModuleSummary]:
        """Search by Vietnamese name (case-insensitive substring)."""
        needle = name_substr.lower()
        return [
            m for m in _build_index().values()
            if needle in m.name_vi.lower()
        ]

    def schools_summary(self) -> dict:
        """Quick summary by school (đông vs tây) for chat answers."""
        idx = _build_index()
        dong = [m.name_vi for m in idx.values() if m.school == "đông"]
        tay = [m.name_vi for m in idx.values() if m.school == "tây"]
        return {
            "dong": dong,
            "tay": tay,
            "total": len(idx),
            "summary_vi": (
                f"YI-CHRONOS hiện có {len(idx)} trường phái: "
                f"Đông phương ({len(dong)}) gồm {', '.join(dong)}. "
                f"Tây phương ({len(tay)}) gồm {', '.join(tay)}."
            ),
        }


_librarian: ModuleLibrarian | None = None


def get_librarian() -> ModuleLibrarian:
    global _librarian
    if _librarian is None:
        _librarian = ModuleLibrarian()
    return _librarian
