"""API router — Thiết Bản Thần Số tra cứu điều văn (tầng A).

Public read-only (dữ liệu sách cổ, không chứa thông tin người dùng).
Design: docs/design/engine-hoang-cuc-thiet-ban-2026-06-10.md
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from engine.thiet_ban import METHOD_ID, SOURCE_REF
from engine.thiet_ban import verses as V

router = APIRouter(prefix="/api/thiet-ban", tags=["thiet-ban"])


class LapSoRequest(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    gender: str = Field("nam", description="nam | nữ")
    timezone: str = "Asia/Ho_Chi_Minh"
    max_age: int = Field(80, ge=1, le=108)


@router.post("/lap-so")
def thiet_ban_lap_so(req: LapSoRequest) -> dict:
    """Lập số Thiết Bản TỪ GIỜ SINH (本命 + 流年 từng tuổi) — TẤT ĐỊNH, không giờ hỏi.

    Đọc cái ĐÃ ĐỊNH (THỂ) để hiểu cái nền; 考刻 tới 15 phút cần lục thân (gia đạo)."""
    from engine.thiet_ban.lap_so import lap_thiet_ban_so, luu_nien_chain
    try:
        ban_menh = lap_thiet_ban_so(req.birth_datetime_local, req.gender, req.timezone)
        luu_nien = luu_nien_chain(req.birth_datetime_local, req.gender, req.max_age, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi lập số: {e}")
    return {"status": "ok", "method": METHOD_ID, "source": SOURCE_REF,
            "ban_menh": ban_menh, "luu_nien": luu_nien}


class KaoKhacRequest(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    cha_chi: str | None = Field(None, description="ĐỊA CHI năm sinh CHA (vd 'Thìn'), tuỳ chọn")
    me_chi: str | None = Field(None, description="ĐỊA CHI năm sinh MẸ, tuỳ chọn")
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/kao-khac")
def thiet_ban_kao_khac(req: KaoKhacRequest) -> dict:
    """考刻 乾坤流度数法: 年柱 → 父母爻 → dự đoán sinh tiêu cha/mẹ (考刻 初刻).

    Cấp sinh tiêu cha/mẹ (gia đạo) → đối chiếu để xác nhận sơ-khắc / báo cần dò khắc sâu.
    Đây là phép LỤC THÂN — đọc cái ĐÃ ĐỊNH, KHÔNG bói; sơ-khắc lệch thì cần dò ±khắc."""
    from engine.thiet_ban.kao_khac import kao_khac_from_birth
    try:
        r = kao_khac_from_birth(req.birth_datetime_local, req.cha_chi, req.me_chi, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 考刻: {e}")
    return {"status": "ok", "method": "考时定刻·乾坤流度数法", "source": SOURCE_REF, **r}


class BirthOnlyRequest(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/quai-trung")
def thiet_ban_quai_trung(req: BirthOnlyRequest) -> dict:
    """卦中取数法 (太玄): 年月→quẻ1, 日时→quẻ2 (先天 mod-8) → 4 条文 (图解 cặp kiểm 4/4)."""
    from engine.thiet_ban.bat_quai_lan import quai_trung_thu_so
    try:
        rows = quai_trung_thu_so(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 卦中取数: {e}")
    return {"status": "ok", "method": "卦中取数法 (太玄)", "source": SOURCE_REF, "dieu_van": rows}


class NguyenHoiRequest(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/nguyen-hoi-van-the")
def thiet_ban_nguyen_hoi(req: NguyenHoiRequest) -> dict:
    """元会运世法: 元-会-运-世 (太玄) → 2 基本数 → 8 条文. TẤT ĐỊNH theo giờ sinh.

    Nối khung Nguyên-Hội-Vận-Thế của Thiệu Ung (Hoàng Cực). 基本数 là SƠ; chốt cuối
    qua 考刻 (±30 đối chiếu đời). Đọc cái ĐÃ ĐỊNH, KHÔNG bói."""
    from engine.thiet_ban.nguyen_hoi_van_the import nguyen_hoi_van_the
    try:
        r = nguyen_hoi_van_the(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 元会运世: {e}")
    return {"status": "ok", "method": "元会运世法(一)", "source": SOURCE_REF, **r}


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
