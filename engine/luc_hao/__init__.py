"""Lục Hào engine — refactored from a single 862-line file into a package.

Public API (what callers + tests import):
- InteractionSignal: pointer-signal payload
- cast_luc_hao: top-level orchestrator
- calculate_timing: ứng-kỳ funnel
- _detect_target_relation, _select_dung_than_line, _detect_hidden_line_candidates:
  internal helpers exposed for tests / debugging.

Internal modules:
- constants.py: data tables (branches, elements, harmony, void days, ...)
- casting.py: InteractionSignal + RNG-based 6-coin line derivation
- relations.py: 5-element + branch interaction + dụng-thần selection
- timing.py: ứng-kỳ candidate ranking funnel
- mai_hoa_env.py: Thể-Dụng environmental analysis
- ruler_profile.py: Tam Thiên ruler-profile composition
- cast.py: end-to-end orchestrator (cast_luc_hao)
"""

from .casting import InteractionSignal
from .cast import cast_luc_hao
from .relations import (
    _detect_hidden_line_candidates,
    _detect_target_relation,
    _select_dung_than_line,
)
from .timing import calculate_timing


__all__ = [
    "InteractionSignal",
    "cast_luc_hao",
    "calculate_timing",
    "_detect_target_relation",
    "_select_dung_than_line",
    "_detect_hidden_line_candidates",
]
