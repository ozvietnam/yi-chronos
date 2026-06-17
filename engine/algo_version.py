"""Algo-version contract (H3) — nguồn sự thật version cho freshness §5bis.

Vì sao tồn tại: AppChat cache diễn giải mệnh lý kèm `algoVersion`; khi YI nâng cấp
engine giữa tuần, version đổi → AppChat tự refetch → user thấy bản luận mới
("mỗi tuần một khám phá"). Hợp đồng đó chỉ chạy nếu YI có **một** version ổn định,
nhẹ, và **theo từng môn** (một môn bump không kéo môn khác refetch oan).

Nguồn gốc: KHÔNG bịa version mới — kế thừa `core.config.ALGORITHM_VERSION` (version
engine toàn cục) + ráp thêm version per-method. Khi đổi LOGIC DIỄN GIẢI của 1 môn,
bump đúng entry trong METHOD_ALGO_VERSIONS.
"""
from __future__ import annotations

import time as _time

from core.config import ALGORITHM_VERSION, ZIWEI_RULESET_ID

# Version diễn giải theo từng môn. Bump entry tương ứng khi engine môn đó đổi cách
# luận (an sao/cách cục/sinh khắc/lưu vận…) đủ để bản cache cũ cần tính lại.
METHOD_ALGO_VERSIONS: dict[str, str] = {
    "tu_vi": "tu_vi-1",
    "bat_tu": "bat_tu-1",
    "ha_lac": "ha_lac-1",
    "luc_hao": "luc_hao-1",
    "mai_hoa": "mai_hoa-1",
    "lien_hoa": "lien_hoa-1",
    "couple_match": "couple_match-1",  # gieo duyên (G1–G4)
}


def algo_version(method: str | None = None) -> str:
    """Composite version cho 1 reading. Method lạ / None → version engine toàn cục.

    Vd: algo_version("tu_vi") -> "mvp-0.1.0+tu_vi-1".
    """
    comp = METHOD_ALGO_VERSIONS.get(method) if method else None
    return f"{ALGORITHM_VERSION}+{comp}" if comp else ALGORITHM_VERSION


def version_info() -> dict:
    """Payload cho GET /api/version — AppChat so sánh để quyết refetch."""
    return {
        "algo_version": ALGORITHM_VERSION,
        "ziwei_ruleset": ZIWEI_RULESET_ID,
        "methods": dict(METHOD_ALGO_VERSIONS),
        "server_time": int(_time.time()),
    }
