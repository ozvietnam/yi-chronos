"""API router — Thiết Bản Thần Số tra cứu điều văn (tầng A).

Public read-only (dữ liệu sách cổ, không chứa thông tin người dùng).
Design: docs/design/engine-hoang-cuc-thiet-ban-2026-06-10.md
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from engine.thiet_ban import METHOD_ID, SOURCE_REF
from engine.thiet_ban import verses as V

router = APIRouter(prefix="/api/thiet-ban", tags=["thiet-ban"])


@router.get("/stats")
def thiet_ban_stats() -> dict:
    return {"status": "ok", "method": METHOD_ID, "source": SOURCE_REF, **V.stats()}


@router.get("/verse/{seq_no}")
def thiet_ban_verse(seq_no: int) -> dict:
    if not (1 <= seq_no <= 13000):
        raise HTTPException(status_code=400, detail="seq_no ngoài phạm vi 1-13000")
    v = V.get_verse(seq_no)
    if not v:
        raise HTTPException(status_code=404, detail=f"Chưa có điều văn số {seq_no} trong bảng tra")
    return {"status": "ok", "verse": v}


@router.get("/range")
def thiet_ban_range(start: int = Query(..., ge=1), end: int = Query(..., le=13000)) -> dict:
    if end < start:
        raise HTTPException(status_code=400, detail="end < start")
    return {"status": "ok", "results": V.get_range(start, end)}


@router.get("/search")
def thiet_ban_search(q: str = Query(..., min_length=1, max_length=100),
                     limit: int = Query(20, ge=1, le=50)) -> dict:
    return {"status": "ok", **V.search(q, limit)}


@router.get("/volume/{tap}")
def thiet_ban_volume(tap: str, offset: int = Query(0, ge=0),
                     limit: int = Query(50, ge=1, le=100)) -> dict:
    if tap not in V.VOLUMES:
        raise HTTPException(status_code=400, detail=f"Tập không hợp lệ. Chọn: {V.VOLUMES}")
    return {"status": "ok", **V.get_volume(tap, offset, limit)}
