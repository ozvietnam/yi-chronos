"""API router — Hoàng Cực Kinh Thế tầng thời cuộc (Nguyên-Hội-Vận-Thế).

Public read-only. Paradigm đọc đồng dạng — không predict (Iron Rule #4/#6).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from engine.hoang_cuc import METHOD_ID, SOURCE_REF
from engine.hoang_cuc.cast import cast_hoang_cuc
from engine.hoang_cuc.khoi_so import year_que_method
from engine.hoang_cuc.nam_que_svg import nam_que_strip_svg
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


@router.get("/nam-que")
def hoang_cuc_nam_que(year: int = Query(...)) -> dict:
    """Quẻ-năm theo PHÉP 经世 (year_que_method) — hệ duy nhất, mọi năm."""
    try:
        return {"status": "ok", "year": year, "nam_que": year_que_method(year)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nam-que-strip.svg")
def hoang_cuc_nam_que_strip(birth: int = Query(..., ge=1900, le=2103),
                            now: int = Query(2026)) -> Response:
    """SVG dải năm-quẻ cá nhân hoá theo năm sinh (đánh dấu năm `now`)."""
    svg = nam_que_strip_svg(birth, now)
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=86400"})


@router.get("/do-nam.svg")
def hoang_cuc_do_nam(birth: str = Query(..., description="YYYY-MM-DD HH:MM"),
                     gender: str = Query("nam"), year: int = Query(2026)) -> Response:
    """ĐỒ NĂM — lá số lưu niên (3 lớp: năm-quẻ + Đại Vận + tứ hóa năm). SVG."""
    from engine.tu_vi.do_nam_svg import do_nam_svg
    try:
        svg = do_nam_svg(str(birth).replace("T", " "), gender or "nam", year)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=3600"})
