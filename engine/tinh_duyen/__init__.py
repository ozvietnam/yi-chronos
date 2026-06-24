"""engine.tinh_duyen — xem tình duyên NỮ MỆNH (deterministic, đa phái).

Mở rộng engine con cross_paradigm.hon_nhan_song_phai bằng kho tri thức
6 JSON (Tử Vi cung Phu Thê + Bát Tự 官杀/日支 + reconcile + cách cục +
personality + life-stage). Engine KHÔNG bói, KHÔNG gọi LLM.
"""

from __future__ import annotations

from .reading import METHOD_ID, read_tinh_duyen

__all__ = ["read_tinh_duyen", "METHOD_ID"]
