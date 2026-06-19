"""API router — Thiết Bản Thần Số tra cứu điều văn (tầng A).

Public read-only (dữ liệu sách cổ, không chứa thông tin người dùng).
Design: docs/design/engine-hoang-cuc-thiet-ban-2026-06-10.md
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
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


@router.post("/bat-quai-gia-tac")
def thiet_ban_bat_quai_gia_tac(req: BirthOnlyRequest) -> dict:
    """八卦加则法 (thường dùng nhất): tứ trụ → 4 quẻ (干配卦上/支配卦下) → 4 条文.
    后天数×1000 + tổng địa-chi-số 6 hào − 下卦后天数. Cặp kiểm sách 2472/3384 ✓."""
    from engine.thiet_ban.bat_quai_gia_tac import bat_quai_gia_tac
    try:
        r = bat_quai_gia_tac(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 八卦加则: {e}")
    return {"status": "ok", "method": "八卦加则法", "source": SOURCE_REF, **r}


@router.post("/dai-van-so")
def thiet_ban_dai_van(req: LapSoRequest) -> dict:
    """大运取数法: 基本数(月日时年干) + mỗi đại vận(干支) → 2 条文/vận (8 đại vận)."""
    from engine.thiet_ban.van_nien import dai_van_thu_so
    try:
        r = dai_van_thu_so(req.birth_datetime_local, req.gender, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 大运取数: {e}")
    return {"status": "ok", "method": "大运取数法", "source": SOURCE_REF, **r}


class LuuNienSoRequest(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    from_age: int = Field(1, ge=1, le=120)
    to_age: int = Field(60, ge=1, le=120)
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/luu-nien-so")
def thiet_ban_luu_nien_so(req: LuuNienSoRequest) -> dict:
    """流年取数法: 基本数 + mỗi năm(干支) → 2 条文/năm (theo tuổi mụ)."""
    from engine.thiet_ban.van_nien import luu_nien_thu_so
    try:
        r = luu_nien_thu_so(req.birth_datetime_local, req.from_age, req.to_age, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 流年取数: {e}")
    return {"status": "ok", "method": "流年取数法", "source": SOURCE_REF, **r}


class _DieuVanItem(BaseModel):
    so: int
    zh: str = ""
    ngu_canh: str = ""


class LuanDieuVanRequest(BaseModel):
    items: list[_DieuVanItem] = Field(..., max_length=200)
    force: bool = False


@router.post("/luan-dieu-van")
def thiet_ban_luan_dieu_van(req: LuanDieuVanRequest, request: Request) -> dict:
    """Sage `thiet_ban` DỊCH điều văn cổ văn Hán → Việt + LỜI BÌNH (Hermes quản lý sage).

    Điều văn cố định → CACHE theo số điều (dịch 1 lần, lần sau instant). Gate đăng-nhập
    (chặn anon đốt LLM; bản dịch là tài nguyên CHUNG, cache xong mọi người hưởng).
    Paradigm Iron #6/#8: dịch trung thực + bình đọc-đồng-dạng, KHÔNG predict cát/hung."""
    from api.auth import get_current_user
    if not get_current_user(request):
        raise HTTPException(status_code=401, detail="Cần đăng nhập để sage dịch điều văn.")
    from engine.thiet_ban.luan_dieu_van import luan_dieu_van
    items = [{"so": it.so, "zh": it.zh, "ngu_canh": it.ngu_canh} for it in req.items]
    try:
        r = luan_dieu_van(items, force=req.force)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi luận điều văn: {e}")
    return {"status": "ok", "method": "thiet_ban_sage_dich", **r}


@router.post("/truoc-sau-que")
def thiet_ban_truoc_sau(req: BirthOnlyRequest) -> dict:
    """前后卦取数法: 年月→前卦, 日时→后卦 (太玄%8→后天) → 八卦加则 → 前+96×4, 后−96×4 = 8 điều.
    Cặp kiểm sách 1478/1387 ✓."""
    from engine.thiet_ban.bat_quai_gia_tac import truoc_sau_que
    try:
        r = truoc_sau_que(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 前后卦: {e}")
    return {"status": "ok", "method": "前后卦取数法", "source": SOURCE_REF, **r}


@router.post("/tien-hau-thien")
def thiet_ban_tien_hau_thien(req: LapSoRequest) -> dict:
    """先后天卦八卦加则法: 先天卦/后天卦 (河洛真数) → 八卦加则 → 先天+96×4, 后天−96×4 = 8 điều.
    Cơ chế ±96 validate cặp kiểm sách; quẻ tiên/hậu thiên từ engine ha_lac."""
    from engine.thiet_ban.bat_quai_gia_tac import tien_hau_thien_gia_tac
    try:
        r = tien_hau_thien_gia_tac(req.birth_datetime_local, req.gender, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 先后天卦: {e}")
    return {"status": "ok", "method": "先后天卦八卦加则法", "source": SOURCE_REF, **r}


@router.post("/luc-hao-can-chi")
def thiet_ban_luc_hao_can_chi(req: LapSoRequest) -> dict:
    """先后天卦六爻干支和数法 #9: 先天卦 纳甲 六爻 太玄和 → base → ±96×4 = 8 条文.
    Cặp kiểm sách: 山雷颐 → base 4245."""
    from engine.thiet_ban.bat_quai_gia_tac import luc_hao_can_chi_thu_so
    try:
        r = luc_hao_can_chi_thu_so(req.birth_datetime_local, req.gender, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 六爻干支和数: {e}")
    return {"status": "ok", "method": "六爻干支和数法", "source": SOURCE_REF, **r}


@router.post("/tien-hau-thien-thu-so")
def thiet_ban_tien_hau_thu_so(req: LapSoRequest) -> dict:
    """先后天卦取数法 #10: 先天卦/后天卦 + 互卦 → 2 基数 → ±48×{2,4,8,16} = 16 条文.
    Cặp kiểm sách: 先天基数 2111 (夬→互乾), 后天基数 9719 (睽→互既济)."""
    from engine.thiet_ban.bat_quai_gia_tac import tien_hau_thien_thu_so
    try:
        r = tien_hau_thien_thu_so(req.birth_datetime_local, req.gender, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 先后天卦取数: {e}")
    return {"status": "ok", "method": "先后天卦取数法", "source": SOURCE_REF, **r}


@router.post("/nhat-chu-hoa-que")
def thiet_ban_nhat_chu(req: BirthOnlyRequest) -> dict:
    """日主化卦取数法: chỉ 日柱 → 八卦加则 → base ±96×4 = 8 条文. Cặp kiểm 壬午→6471."""
    from engine.thiet_ban.bat_quai_gia_tac import nhat_chu_hoa_que
    try:
        r = nhat_chu_hoa_que(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 日主化卦: {e}")
    return {"status": "ok", "method": "日主化卦取数法", "source": SOURCE_REF, **r}


@router.post("/thap-nhi-tich")
def thiet_ban_thap_nhi_tich(req: BirthOnlyRequest) -> dict:
    """十二辟卦化卦取数: nguyệt chi → 辟卦 (消息) → 八卦加则 → 条文."""
    from engine.thiet_ban.bat_quai_gia_tac import thap_nhi_tich_hoa_que
    try:
        r = thap_nhi_tich_hoa_que(req.birth_datetime_local, req.timezone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi 十二辟卦: {e}")
    return {"status": "ok", "method": "十二辟卦化卦取数", "source": SOURCE_REF, **r}


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
