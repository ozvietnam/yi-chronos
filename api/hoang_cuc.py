"""API router — Hoàng Cực Kinh Thế tầng thời cuộc (Nguyên-Hội-Vận-Thế).

Public read-only. Paradigm đọc đồng dạng — không predict (Iron Rule #4/#6).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from engine.hoang_cuc import METHOD_ID, SOURCE_REF
from engine.hoang_cuc.cast import cast_hoang_cuc
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year, timeline

router = APIRouter(prefix="/api/hoang-cuc", tags=["hoang-cuc"])


@router.get("/the-cuc")
def hoang_cuc_the_cuc(year: int = Query(..., ge=-64815, le=64784),
                      atoms: bool = Query(True)) -> dict:
    """Định vị 1 năm trong chu kỳ Nguyên-Hội-Vận-Thế + atoms trích từ sách."""
    try:
        return {"status": "ok", **cast_hoang_cuc(year, with_atoms=atoms)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/timeline")
def hoang_cuc_timeline(start: int = Query(...), end: int = Query(...)) -> dict:
    """Dải mốc THẾ trong [start..end] cho UI trục thời gian (tối đa 3000 năm/lần)."""
    if end < start:
        raise HTTPException(status_code=400, detail="end < start")
    if end - start > 3000:
        raise HTTPException(status_code=400, detail="Tối đa 3000 năm mỗi lần")
    try:
        return {"status": "ok", "method": METHOD_ID, "source": SOURCE_REF,
                "marks": timeline(start, end)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
