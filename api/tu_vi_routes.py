"""API router — Tử Vi domain (tách từ api/main.py 2026-07-15, bước 1 bẻ monolith).

Gồm toàn bộ route /api/tu-vi/* của main.py cũ: lá số (cast), thư viện sao/cục,
vận hạn, analyzer Person-based, Q4 Chiếu Đởm Kinh, cách cục dictionary,
run-all pipeline + PDF report. Logic route GIỮ NGUYÊN từng byte so với main.py —
chỉ đổi decorator @app.<m>("/api/tu-vi/x") → @router.<m>("/x").

Import engine giữ nguyên kiểu local-import-trong-hàm như code gốc (lazy load,
tránh chậm startup).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel

from api.schemas import TuViCastRequest
from api.service_auth import require_caller, rate_limit_caller  # (#34 dual-auth)
from core.config import ALGORITHM_VERSION

router = APIRouter(prefix="/api/tu-vi", tags=["tu-vi"])

# main.py cũ dùng tên `logger` chưa từng được gán ở module level (latent NameError
# trong các nhánh except của run-all / report-pdf). Ở module này gán tử tế.
logger = logging.getLogger(__name__)


@router.get("/luu-nguyet")
def tu_vi_luu_nguyet(
    at: str,
    lat: float = 21.03,
    lon: float = 105.85,
    tz_hours: float = 7.0,
    year_start: int = 2026,
    year_end: int = 2031,
) -> dict[str, object]:
    """NHỊP THÁNG (lưu nguyệt) đa-năm: mỗi tháng âm, Tứ Hóa tháng rọi cung chức nào.

    La bàn chú-ý (Iron #4/#6/#8 — đọc đồng dạng, mệnh là động từ): cho biết cung
    nào được cấu trúc rọi sáng từng tháng, KHÔNG phải bói kết cục.

    Query params (giống /api/natal-universe):
    - at: ISO 8601 giờ sinh ĐỊA PHƯƠNG. Có offset → dùng offset; không → áp tz_hours.
    - lat, lon: nơi sinh (mặc định Hà Nội).
    - tz_hours: múi giờ nếu `at` không có offset (mặc định +7).
    - year_start, year_end: khoảng năm dương (bao gồm 2 đầu, chênh ≤ 30).
    """
    from engine.tu_vi.luu_nguyet import luu_nguyet_rhythm

    dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=tz_hours)))
    return luu_nguyet_rhythm(dt, lat, lon, year_start, year_end)

@router.get("/chinh-tinh")
def tu_vi_chinh_tinh_list() -> dict[str, object]:
    """Return all 14 chính tinh metadata + interpretation templates."""
    from engine.tu_vi import list_chinh_tinh

    return {
        "status": "ok",
        "stars": [s.to_dict() for s in list_chinh_tinh()],
    }


@router.get("/chinh-tinh/{star_id}")
def tu_vi_chinh_tinh_detail(star_id: str) -> dict[str, object]:
    """Return one chính tinh by id slug."""
    from engine.tu_vi import get_chinh_tinh

    try:
        s = get_chinh_tinh(star_id)
    except ValueError:
        return {"status": "not_found", "id": star_id}
    return {"status": "ok", "star": s.to_dict()}


@router.get("/cuc-list")
def tu_vi_cuc_list() -> dict[str, object]:
    """5 Cục (Thủy 2 · Mộc 3 · Kim 4 · Thổ 5 · Hỏa 6) cho Thư viện Tử Vi.

    GROUNDED (quote-or-silence): hành nền + tính chất element (Lê Văn Sửu) + vai
    trò cơ học dẫn-xuất-được. "Chất người từng cục" CHƯA có nguồn → chua_co_nguon.
    """
    from engine.tu_vi.than_cu import list_cuc

    return {"status": "ok", **list_cuc()}


@router.get("/than-menh")
def tu_vi_than_menh() -> dict[str, object]:
    """Quan hệ Thân↔Mệnh (đồng cung vs khác cung) cho Thư viện Tử Vi.

    ⚠️ "Mệnh" = QUAN HỆ Thân-Mệnh, KHÔNG phải tên 12 cung. GROUNDED: dùng atom ĐÃ
    DUYỆT (đồng cung = nguyên tắc Vũ Tài Lục + luận Nghiệm Lý; khác cung = 6 Thân cư).
    """
    from engine.tu_vi.than_cu import list_than_menh

    return {"status": "ok", **list_than_menh()}


@router.get("/vong-sao")
def tu_vi_vong_sao() -> dict[str, object]:
    """Vòng sao / phụ tinh (roster đầy đủ) cho Thư viện Tử Vi — B4.

    Nguồn = sao_noi_dung lớp 'def', CHỈ dòng đã DUYỆT ĐỐI KHÁNG (founder_verified=1):
    quote có trong sách + dịch không bịa ý. Loại 14 chính tinh (đã có panel riêng).
    """
    from engine.tu_vi.vong_sao import list_vong_sao

    return {"status": "ok", **list_vong_sao()}


class TuViVanHanRequest(BaseModel):
    """Vận hạn grounded — 1 tầng thời gian."""
    birth_datetime_local: str
    gender: str = "nam"
    timezone: str = "Asia/Ho_Chi_Minh"
    tang: str  # dai_van | luu_nien | luu_nguyet | tuan | *_overview | life_arc
    cycle_index: Optional[int] = None   # dai_van
    year: Optional[int] = None          # luu_nien | luu_nguyet | tuan | overview start
    year_end: Optional[int] = None      # luu_nien_overview
    month: Optional[int] = None         # luu_nguyet | tuan | luu_nhat (dương lịch)
    day: Optional[int] = None           # luu_nhat (ngày dương lịch)
    tuan: Optional[int] = None          # tuan (1 thượng · 2 trung · 3 hạ)
    want_llm: bool = True               # có sinh narrative grounded không
    # life_arc (bức tranh cuộc đời thăng trầm — đường cong KHÍ tất định)
    tu_nam: Optional[int] = None        # life_arc từ năm
    den_nam: Optional[int] = None       # life_arc đến năm
    buoc: str = "thang"                 # life_arc: "thang" | "nam"


@router.post("/van-han")
def tu_vi_van_han(request: TuViVanHanRequest, caller: dict = Depends(require_caller)) -> dict[str, object]:
    """Luận vận hạn 1 tầng (Đại Vận/Lưu Niên/Lưu Nguyệt/Tuần) — GROUNDED.

    Trả block tất định (Thể-Dụng + Tứ Hóa rọi cung + sao có nguồn) + narrative LLM
    CHỈ biên tập từ nguồn (không bịa). Thiếu nguồn → luận rỗng, KHÔNG gieo rác.
    """
    from engine.tu_vi import van_han as vh

    # BỨC TRANH CUỘC ĐỜI THĂNG TRẦM — đường cong KHÍ tất định (0-LLM, không rate-limit).
    # ⚠️ Iron #9: bản đồ KHÍ động↔tĩnh để SOI TÂM, KHÔNG bói giàu-nghèo/thắng-thua.
    if request.tang == "life_arc":
        person = {"birth_datetime_local": request.birth_datetime_local,
                  "gender": request.gender, "timezone": request.timezone}
        try:
            arc = vh.life_arc(person, request.tu_nam or 2026,
                              request.den_nam or (request.tu_nam or 2026) + 4,
                              buoc=request.buoc)
            return {"status": "ok", **arc}
        except (ValueError, KeyError) as e:
            return {"status": "error", "reason": str(e)}

    # Overview skeleton (tất định, 0-LLM) — thay nguồn cached-analyzer ungrounded của UI cũ.
    if request.tang in ("dai_van_overview", "luu_nien_overview", "luu_nguyet_overview"):
        from engine.tu_vi.from_birth import cast_la_so_from_birth
        try:
            la_so = cast_la_so_from_birth(birth_datetime_local=request.birth_datetime_local,
                                          gender=request.gender)
            if request.tang == "dai_van_overview":
                return {"status": "ok", **vh.dai_van_overview(la_so)}
            if request.tang == "luu_nguyet_overview":
                return {"status": "ok", **vh.luu_nguyet_overview(la_so, request.year or 2026)}
            start = request.year or 2026
            return {"status": "ok", **vh.luu_nien_overview(la_so, start, request.year_end or start + 4)}
        except (ValueError, KeyError) as e:
            return {"status": "error", "reason": str(e)}

    kw: dict = {}
    for k in ("cycle_index", "year", "month", "tuan", "day"):
        v = getattr(request, k)
        if v is not None:
            kw[k] = v
    if request.want_llm:
        rate_limit_caller(caller, bucket="tuvi_llm", limit=30, window_sec=3600)
    person = {"birth_datetime_local": request.birth_datetime_local,
              "gender": request.gender, "timezone": request.timezone}
    try:
        out = vh.van_han_luan(person, request.tang, want_llm=request.want_llm, **kw)
    except (ValueError, KeyError) as e:
        return {"status": "error", "reason": str(e)}
    return {"status": "ok", **out}


@router.get("/do-hinh-co")
def tu_vi_do_hinh_co() -> dict[str, object]:
    """4 đồ hình âm dương cổ (Thái cực · Tiên thiên · Hậu thiên · Hà Đồ) cho
    đồ hình tương tác. Bồi từ vòng đọc sâu Lê Văn Sửu p21-40 (2026-06-13)."""
    from engine.tu_vi.do_hinh_co import do_hinh_payload
    return {"status": "ok", **do_hinh_payload()}


@router.get("/star-profiles")
def tu_vi_star_profiles() -> dict[str, object]:
    """Hồ sơ sâu 14 chính tinh (+ Vô Chính Diệu) + kiến thức nền Âm Dương Ngũ Hành.

    Gộp 3 tầng: (1) metadata cổ truyền Q2 (hành, âm dương, hóa khí, chủ về,
    tích cực/tiêu cực); (2) profile Ngũ Uẩn 5 lớp trường phái Tử Vi Bôn Ba;
    (3) bảng miếu-vượng-đắc-hãm tại 12 chi ("độ khó bài học" theo từng đất cung).
    """
    import json as _json
    import unicodedata as _ud
    from pathlib import Path as _Path

    from engine.tu_vi import list_chinh_tinh
    from engine.tu_vi import ngu_uan as ngu_uan_mod
    from engine.tu_vi.mieu_vuong_ham import level_at
    from engine.tu_vi.ngu_hanh_nen import HANH_CHI, vong_sinh_khac

    def _slug(s: str) -> str:
        nfkd = _ud.normalize("NFD", s)
        s2 = "".join(c for c in nfkd if not _ud.combining(c))
        return s2.lower().strip().replace(" ", "_").replace("đ", "d")

    deep_dir = _Path(__file__).resolve().parents[1] / "data/yi_wiki/tu_vi_star_deep"

    def _deep_profile(star_vi: str) -> dict | None:
        """Chuyên khảo luận giải sâu đa phái (build từ atoms 6 nguồn) nếu đã có."""
        p = deep_dir / f"{_slug(star_vi)}.json"
        if not p.exists():
            return None
        try:
            return _json.loads(p.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError):
            return None

    chi_12 = list(HANH_CHI.keys())
    profiles = []
    for s in list_chinh_tinh():
        tvbb = ngu_uan_mod.get_star_profile(s.ten_vi)
        profiles.append({
            "co_ban": s.to_dict(),
            "ngu_uan": tvbb,  # None nếu dataset chưa có sao này
            # Chân dung v3 8 lớp (l1..l8) — thư viện không có vị trí cụ thể nên
            # mieu_ham_level=None → l4 trả CẢ HAI nhánh đắc/hãm, active=None.
            "v3": ngu_uan_mod.get_star_v3(s.ten_vi),  # None nếu record chưa có
            "sao_o_dau_thi": ngu_uan_mod.sao_o_dau_thi(s.ten_vi),
            "mieu_ham_12_chi": {chi: level_at(s.ten_vi, chi) for chi in chi_12},
            "luan_giai_sau": _deep_profile(s.ten_vi),  # None nếu chưa build
        })
    # Vô Chính Diệu — "tính cách thứ 15" (chỉ có trong dataset hiện đại)
    vcd = ngu_uan_mod.get_star_profile("Vô Chính Diệu")
    if vcd:
        profiles.append({
            "co_ban": {"ten_vi": "Vô Chính Diệu", "ten_zh": "無正曜",
                       "ngu_hanh": None, "am_duong": None, "hoa_khi": None,
                       "keywords": vcd.get("tom_gon") or [],
                       "tich_cuc": None, "tieu_cuc": None, "chu_ve": []},
            "ngu_uan": vcd,
            "v3": ngu_uan_mod.get_star_v3("Vô Chính Diệu"),
            "sao_o_dau_thi": ngu_uan_mod.sao_o_dau_thi("Vô Chính Diệu"),
            "mieu_ham_12_chi": {},
        })
    # Phụ tinh có chân dung v3 (Kình Dương, Văn Xương, Lộc Tồn...) — tự động
    # theo dataset (list_phu_tinh_with_v3), KHÔNG hard-code tên. Không có bảng
    # miếu-vượng-hãm 12 chi trong engine (đúng bản chất: phụ tinh an theo năm/
    # giờ sinh, không theo cục như chính tinh) → mieu_ham_12_chi rỗng, khí
    # vượng/suy nằm trong v3.khi_vuong_suy (dẫn nguồn sách, xem doc ngu_uan.py).
    from engine.tu_vi.concept_dict import lookup as _concept_lookup
    for ten in ngu_uan_mod.list_phu_tinh_with_v3():
        pv3 = ngu_uan_mod.get_star_v3(ten)
        raw = ngu_uan_mod.get_star_profile(ten) or {}
        cd = _concept_lookup(ten) or {}
        profiles.append({
            "co_ban": {"ten_vi": ten, "ten_zh": None,
                       "ngu_hanh": None, "am_duong": None,
                       "hoa_khi": cd.get("definition"),
                       "keywords": raw.get("tom_gon") or [],
                       "tich_cuc": None, "tieu_cuc": None, "chu_ve": [],
                       "is_phu_tinh": True},
            "ngu_uan": raw,
            "v3": pv3,
            "sao_o_dau_thi": ngu_uan_mod.sao_o_dau_thi(ten),
            "mieu_ham_12_chi": {},
        })
    from engine.hermes_guard import DISCLAIMER
    return {
        "status": "ok",
        "nen_tang": vong_sinh_khac(),
        "profiles": profiles,
        "paradigm_note": (
            "Sao không tốt không xấu — mỗi sao là một dạng lực sống; "
            "miếu hay hãm là độ khó của bài học tại từng đất cung, không phải lời khen chê."
        ),
        "disclaimer": DISCLAIMER,
    }


_HOUR_BRANCH_BY_HOUR = (
    "Tý", "Sửu", "Sửu", "Dần", "Dần", "Mão", "Mão",
    "Thìn", "Thìn", "Tỵ", "Tỵ", "Ngọ", "Ngọ",
    "Mùi", "Mùi", "Thân", "Thân", "Dậu", "Dậu",
    "Tuất", "Tuất", "Hợi", "Hợi", "Tý",
)


def _hour_branch_from_hour(hour: int) -> str:
    """Map 0..23 to địa chi hour."""
    return _HOUR_BRANCH_BY_HOUR[hour]


@router.post("/cast")
def tu_vi_cast(request: TuViCastRequest, caller: dict = Depends(require_caller)) -> dict[str, object]:
    """Cast a full Tử Vi lá số.

    Two input modes:
    - Direct (lunar_month + lunar_day + hour_branch + year_stem + year_branch + gender)
    - Convenient (birth_datetime_local — auto-converts via core.chronos)
    """
    from engine.tu_vi import cast_la_so

    # Resolve inputs.
    if request.birth_datetime_local:
        from core.chronos import calculate_chronos_state
        from core.true_solar_time import adjust_datetime, resolve_longitude
        from engine.yi_wiki.lich_conversion import SolarDateTime, solar_to_lunar

        # True-solar-time correction (#35): shift civil → true solar time at birth
        # longitude before lunar/ganzhi conversion. Opt-in, backward-compatible.
        _lon = resolve_longitude(
            birth_longitude=request.birth_longitude, birth_province=request.birth_province
        )
        _bdt = adjust_datetime(request.birth_datetime_local, _lon)

        chronos = calculate_chronos_state(_bdt, request.timezone)
        from datetime import datetime as _dt
        local_dt = _dt.fromisoformat(_bdt)
        # lich_conversion handles 早子時: hour≥23 → lunar day of next day (#13 fix)
        solar = SolarDateTime(
            year=local_dt.year, month=local_dt.month, day=local_dt.day,
            hour=local_dt.hour, minute=local_dt.minute,
        )
        lunar = solar_to_lunar(solar)
        lunar_month = lunar.lunar_month
        lunar_day = lunar.lunar_day
        # Hour branch from local datetime hour.
        hour_branch = _hour_branch_from_hour(local_dt.hour)
        # Year stem/branch from chronos.ganzhi.
        year_parts = chronos.ganzhi.year.split()
        year_stem = year_parts[0]
        year_branch = year_parts[1]
    else:
        # Direct mode — require all fields.
        missing = [k for k, v in {
            "lunar_month": request.lunar_month,
            "lunar_day": request.lunar_day,
            "hour_branch": request.hour_branch,
            "year_stem": request.year_stem,
            "year_branch": request.year_branch,
        }.items() if v is None]
        if missing:
            return {"status": "error", "missing_fields": missing}
        lunar_month = request.lunar_month
        lunar_day = request.lunar_day
        hour_branch = request.hour_branch
        year_stem = request.year_stem
        year_branch = request.year_branch

    result = cast_la_so(
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch=hour_branch,
        year_stem=year_stem,
        year_branch=year_branch,
        gender=request.gender,
    )

    # Optional layers.
    response: dict[str, object] = {
        "algorithm_version": ALGORITHM_VERSION,
        "input_resolved": {
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "hour_branch": hour_branch,
            "year_stem": year_stem,
            "year_branch": year_branch,
            "gender": request.gender,
        },
        "la_so": result,
    }

    if request.include_interpretation:
        from engine.tu_vi import interpret_la_so

        response["interpretation"] = interpret_la_so(result)

    # Lưu trú sao for target_year if provided.
    if request.target_year is not None and request.birth_datetime_local:
        from datetime import datetime as _dt
        from engine.tu_vi import luu_tru_for_year

        local_dt = _dt.fromisoformat(request.birth_datetime_local)
        birth_year = local_dt.year
        response["luu_tru_year"] = luu_tru_for_year(
            la_so=result,
            target_year=request.target_year,
            birth_year=birth_year,
        )

    # ── GIẢI MÃ ĐỊA BÀN: nguyệt vận (lưu nguyệt) per-cung ────────────────────────
    # Lưu nguyệt cần 1 lưu niên → mặc định NĂM HIỆN TẠI (target_year ghi đè). Tháng 1
    # khởi Đẩu Quân lưu niên, thuận. Hiện "T.x" mỗi ô như giáo cụ địa bàn.
    try:
        from datetime import datetime as _dt2
        from engine.tu_vi.an_sao import nguyet_van_per_cung
        from engine.tu_vi.luu_tru import year_to_ganzhi
        _nv_year = request.target_year or _dt2.now().year
        _, _ln_branch = year_to_ganzhi(_nv_year)
        result["nguyet_van"] = nguyet_van_per_cung(
            _ln_branch, result["lunar_month"], result["hour_branch"])
        result["nguyet_van_year"] = _nv_year
    except Exception:
        pass   # nguyệt vận là lớp phụ trợ — lỗi KHÔNG chặn lá số chính

    # ── Thân cư + Cục nền + trục Mệnh→Thân — GROUNDED, có nguồn ──────────────────
    try:
        from engine.tu_vi.than_cu import doc_cuc, doc_than_cu
        response["than_cu"] = doc_than_cu(result, limit=2)   # kèm menh_than_axis (#3)
        response["cuc_luan"] = doc_cuc(result)               # #2: Cục = ngũ hành nền
    except Exception:
        pass

    return response

# ─── Generic Tử Vi Analyzer endpoints ────────────────────────────────────────
# (Person-based: works for any person_key in founder's user_persons namespace
#  or any directly-passed birth datetime.)

class _AnalyzeRequest(BaseModel):
    """Request for generic Tử Vi analyzer."""
    # Either provide person_key (looks up from user_persons of current user)
    person_key: Optional[str] = None
    # OR provide birth directly
    birth_datetime_local: Optional[str] = None
    gender: Optional[str] = None
    name: Optional[str] = "Người"
    timezone: str = "Asia/Ho_Chi_Minh"
    # Analysis options
    luu_nien_start: int = 2026
    luu_nien_end: int = 2030
    luu_nguyet_year: int = 2026
    phu_top_n: int = 5
    force: bool = False  # bypass cache


def _resolve_person_from_request(req: _AnalyzeRequest, request: Request):
    """Resolve Person from request — either person_key (user_persons) or direct.

    Sets `user_id` on the returned Person so cache is scoped per-user, preventing
    collision when multiple users use the same `person_key` (e.g. 'self').
    """
    from engine.tu_vi.analyzer import Person
    from api.auth import get_current_user
    user = get_current_user(request)
    uid = user["user_id"] if user else None

    if req.birth_datetime_local and req.gender:
        return Person(
            person_key=req.person_key or f"adhoc_{int(time.time())}",
            name=req.name or "Người",
            birth_datetime_local=req.birth_datetime_local,
            gender=req.gender,
            timezone=req.timezone,
            user_id=uid,
        )
    if req.person_key:
        # Look up from current user's user_persons
        from api.auth import AUTH_DB
        import sqlite3
        # Legacy '_founder' shortcut now restricted to the owner — previously
        # it returned anh's hardcoded birth profile to ANY caller (including
        # guests) which let kinhdich.online be used as an oracle backed by
        # anh's personal chart. Owner-only keeps the legacy cache working
        # for anh's own browser while closing the leak.
        if req.person_key == "_founder":
            if not user or user.get("role") != "owner":
                raise HTTPException(404, "person_key not found")
            return Person(
                person_key="_founder",
                name="Anh (Founder)",
                birth_datetime_local="1988-06-05T23:30:00",
                gender="nam",
                user_id=uid,
            )
        if not user:
            raise HTTPException(401, "Login required to use person_key")
        db = sqlite3.connect(AUTH_DB)
        row = db.execute(
            "SELECT name, gender, birth_datetime_local, timezone FROM user_persons WHERE user_id=? AND person_key=?",
            (user["user_id"], req.person_key),
        ).fetchone()
        db.close()
        if not row:
            raise HTTPException(404, f"person_key '{req.person_key}' not found")
        return Person(
            person_key=req.person_key,
            name=row[0],
            gender=row[1] or "nam",
            birth_datetime_local=row[2] or "",
            timezone=row[3] or "Asia/Ho_Chi_Minh",
            user_id=uid,
        )
    raise HTTPException(400, "Must provide person_key OR birth_datetime_local+gender")


@router.post("/analyze/{kind}")
def yi_tuvi_analyze(kind: str, req: _AnalyzeRequest, request: Request) -> dict:
    """Run 1 specific Tử Vi analysis.

    kind: 'cach_cuc' | 'dai_van' | 'luu_nien' | 'luu_nguyet' | 'phu_match' | 'phu_reading' | 'cung_reading' | 'phe_menh' | 'all'
    """
    from engine.tu_vi.analyzer import TuViAnalyzer
    from fastapi import HTTPException
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person, force=req.force)

    try:
        if kind == "cach_cuc":
            return {"status": "ok", "kind": kind, **analyzer.discover_cach_cuc()}
        elif kind == "dai_van":
            return {"status": "ok", "kind": kind, **analyzer.dai_van_annotate()}
        elif kind == "luu_nien":
            return {"status": "ok", "kind": kind, **analyzer.luu_nien(req.luu_nien_start, req.luu_nien_end)}
        elif kind == "luu_nguyet":
            return {"status": "ok", "kind": kind, **analyzer.luu_nguyet(req.luu_nguyet_year)}
        elif kind == "phu_match":
            return {"status": "ok", "kind": kind, **analyzer.phu_match()}
        elif kind == "phu_reading":
            return {"status": "ok", "kind": kind, **analyzer.phu_reading(req.phu_top_n)}
        elif kind == "cung_reading":
            return {"status": "ok", "kind": kind, **analyzer.cung_reading()}
        elif kind == "phe_menh":
            return {"status": "ok", "kind": kind, **analyzer.phe_menh()}
        elif kind == "all":
            return {"status": "ok", "kind": kind, **analyzer.run_all(
                luu_nien_years=(req.luu_nien_start, req.luu_nien_end),
                luu_nguyet_year=req.luu_nguyet_year,
                phu_top_n=req.phu_top_n,
            )}
        else:
            raise HTTPException(400, f"Unknown analysis kind: {kind}")
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "kind": kind, "message": str(e)}


@router.get("/analyze/{person_key}/{kind}")
def yi_tuvi_analyze_get(person_key: str, kind: str, request: Request) -> dict:
    """GET version: load cached analysis result without running new one.

    Scoped per-user: each logged-in user only sees cache from their own namespace.
    `_founder` cache (special prefix) is owner-only.
    """
    from engine.tu_vi.analyzer import _cache_load
    from api.auth import get_current_user
    user = get_current_user(request)
    if person_key.startswith("_") and (not user or user.get("role") != "owner"):
        raise HTTPException(403, "owner-only for special person keys")
    uid = user["user_id"] if user else None
    cached = _cache_load(person_key, kind, uid)
    if cached:
        return {"status": "ok", "cached": True, "kind": kind, **cached}
    return {"status": "not_cached", "kind": kind, "message": f"No cached '{kind}' for {person_key}"}


# ─── Cách cục dictionary (từ thâm nhuần Q1) ──────────────────────────────────
@router.get("/q4/10-buoc-luan")
def yi_tuvi_10_buoc_luan() -> dict:
    """10 bước luận Tử Vi chính thức của Trần Đoàn (Q4 p0266)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/10_buoc_luan.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.get("/q4/thien-quan-archetype/{hour}/{khac}")
def yi_tuvi_thien_quan_archetype(hour: str, khac: str) -> dict:
    """Get 1 archetype Thiên Quán Phân Cung theo giờ + khắc (Q4 p0268-p0271)."""
    from engine.tu_vi.thien_quan_typology import get_archetype
    a = get_archetype(hour, khac)
    if not a:
        return {"status": "error", "message": f"No archetype for ({hour}, {khac})"}
    return {"status": "ok", "archetype": a}


@router.get("/q4/thien-quan-archetypes-all")
def yi_tuvi_thien_quan_all() -> dict:
    """List all 36 archetypes."""
    from engine.tu_vi.thien_quan_typology import list_all_archetypes
    return {"status": "ok", "total": 36, "archetypes": list_all_archetypes()}


@router.get("/q4/rectification-rules")
def yi_tuvi_rectification() -> dict:
    """Định thời khắc rules + Tiểu nhi thời khắc patterns (Q4 p0267)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/rectification_rules.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.get("/q4/chieu-dom-kinh-phi-tinh")
def yi_tuvi_chieu_dom_phi_tinh() -> dict:
    """18 Phi Tinh schema (Chiếu Đởm Kinh — paradigm khác chính thống)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_18_phi_tinh.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.post("/q4/chieu-dom-kinh/cast")
def yi_tuvi_chieu_dom_cast(req: _AnalyzeRequest, request: Request) -> dict:
    """Cast lá số Chiếu Đởm Kinh — 18 Phi Tinh parallel với main Tử Vi engine.

    Per Q4 p0272-p0273 — formula an sao riêng của CDK.
    """
    from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state
    from datetime import datetime

    person = _resolve_person_from_request(req, request)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    BRANCHES = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]

    result = cast_chieu_dom_kinh(
        year_stem=year_parts[0],
        year_branch=year_parts[1],
        lunar_month=int(m_str),
        hour_branch=hour_branch,
        gender=person.gender,
    )
    return {"status": "ok", **result}


# ─── Cung Phu Thê — Bắc phái Trung Châu (Vương Đình Chỉ) ────────────────────


@router.post("/cung-phu-the/bac-phai")
def yi_tuvi_cung_phu_the_bac_phai(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận cung Phu Thê theo BẮC PHÁI Trung Châu.

    Paradigm: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ, section 5.3).
    14 chính tinh × 12 cung Địa Chi + 24 tổ hợp đôi.

    Output: structured paradigm + markdown summary.
    Public access — không gate VIP (paradigm = lookup từ seed JSON).
    """
    from engine.tu_vi.chiem_phu_the import chiem_phu_the, chiem_phu_the_summary_text
    from engine.tu_vi.analyzer import TuViAnalyzer

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so

    # Pass gender để personalize filter gender-conditional paradigm
    gender = (person.gender or "nam").lower().strip()
    if gender not in ("nam", "nu", "nữ"):
        gender = "nam"
    result = chiem_phu_the(la_so, gender=gender)
    if "error" in result:
        return {"status": "error", "message": result["error"]}

    summary_md = chiem_phu_the_summary_text(la_so)

    # Engine v4 — Full 26 quy luật + meta panorama:
    #   v2 (Q1-9) + v3 cross-bind (Q10-13) + v4 phase 2-5 (Q14-26) + Q27 meta
    from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4
    v4_result = chiem_phu_the_v4(la_so)

    # Cross-reference panel (replace placeholder "Cần xem kèm: ..."):
    # render thật Mệnh + Phúc Đức + Đại vận hiện tại + Thái Dương/Thái Âm miếu hãm
    from engine.tu_vi.chiem_phu_the_cross_reference import build_cross_reference
    birth_year = None
    try:
        # person.birth_datetime_local thường dạng "1988-06-05 23:30"
        birth_year = int(str(person.birth_datetime_local)[:4])
    except Exception:
        pass
    cross_ref = build_cross_reference(la_so, gender=gender, birth_year=birth_year)

    # Đặc điểm BẠN ĐỜI qua sao chính diệu Phu Thê (mới 2026-06-08)
    try:
        from engine.tu_vi.phu_the_partner_traits import build_partner_traits
        partner_traits = build_partner_traits(la_so, gender=gender)
    except Exception:
        partner_traits = None

    # Khối đọc sâu Ngũ Uẩn cho đúng trục lá số đang luận:
    # Mệnh là gốc vận hành của bản thân, Phu Thê là quan hệ một-một.
    try:
        from engine.tu_vi.interpretation import interpret_la_so

        full_interpretation = interpret_la_so(la_so)
        readings = full_interpretation.get("palace_readings", [])

        def _palace_reading(name: str) -> dict | None:
            return next((r for r in readings if r.get("palace_name") == name), None)

        ngu_uan_focus = {
            "menh": _palace_reading("Mệnh"),
            "phu_the": _palace_reading("Phu Thê"),
            "school": "Tử Vi Bôn Ba — quán chiếu Ngũ Uẩn",
            "note": (
                "Đọc Mệnh để hiểu cơ chế bản thân; đọc Phu Thê để hiểu cơ chế "
                "quan hệ thân mật. Đây là bản đồ vận hành, không phải bản án."
            ),
        }
    except Exception:
        ngu_uan_focus = None

    return {
        "status": "ok",
        "person_key": person.person_key,
        "school": result["school"],
        "thay_to_su": result["thay_to_su"],
        "data": result,
        "summary_markdown": summary_md,
        "v2": v4_result,  # backward field name
        "v3": v4_result,
        "v4": v4_result,
        "cross_reference": cross_ref,
        "partner_traits": partner_traits,
        "ngu_uan_focus": ngu_uan_focus,
        "la_so": la_so,  # Full chart cho UI render 12 ô đối chiếu
    }


class _LuanCungRequest(_AnalyzeRequest):
    branch: str = ""


@router.post("/q4/cdk/luan-cung")
def yi_tuvi_cdk_luan_cung(req: _LuanCungRequest, request: Request) -> dict:
    """Luận giải sâu 1 cung CDK bằng DeepSeek V4 Pro — VIP1 gated.

    Owner bypass VIP check + không consume_use. User thường cần subscription.
    Auto-extract → wiki sau mỗi lần gen.
    """
    from engine.tu_vi.cdk_cung_analyzer import luan_cdk_cung, BRANCHES_ORDER
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    if not req.branch or req.branch not in BRANCHES_ORDER:
        return {"status": "error", "message": f"Invalid branch. Must be one of {BRANCHES_ORDER}"}

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng tính năng VIP."}

    # VIP gating (owner bypass)
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {
                "status": "error",
                "message": f"Không có quyền VIP1 — {access.get('reason', 'unknown')}",
                "vip_check": access,
            }

    person = _resolve_person_from_request(req, request)
    result = luan_cdk_cung(person, req.branch, force=req.force)

    # Consume use only on success + not owner
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        usage = consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
        result["usage_after"] = usage

    return result


@router.post("/q4/cdk/luan-noi-tam")
def yi_tuvi_cdk_luan_noi_tam(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận NỘI TÂM tổng thể bằng SAGE Chiếu Đởm Kinh (Bắc phái / 18 Phi Tinh).

    Khác luận-cung (per-cung thực dụng): đây là GIỌNG sage chieu_dom — trầm-sâu-từ-bi,
    soi cốt cách tâm hồn, chỗ khắc khoải + sức mạnh ngầm. Paradigm Iron #4/#6/#8 (đọc đồng
    dạng, KHÔNG predict, mệnh-là-động-từ). VIP1-gated, owner bypass — như luận-cung.
    """
    from engine.ai.council import _get_agent_provider, sage_model
    from engine.ai.agents import run_agent
    from engine.tu_vi.from_birth import cast_chieu_dom_from_birth
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng tính năng VIP."}
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error",
                    "message": f"Không có quyền VIP1 — {access.get('reason', 'unknown')}",
                    "vip_check": access}

    person = _resolve_person_from_request(req, request)
    try:
        chart = cast_chieu_dom_from_birth(
            birth_datetime_local=person.birth_datetime_local,
            timezone=person.timezone, gender=person.gender)
    except Exception as e:
        return {"status": "error", "message": f"Lỗi lập lá số CĐK: {e}"}

    # KHÔNG prefer_reasoning: nó đẩy MiniMax-M3 lên đầu, nhưng M3 (và deepseek-v4-pro)
    # reasoning ăn sạch max_tokens → luận RỖNG trên prompt sage (đo prod 2026-06-24).
    # Ép model non-reasoning, TIN CẬY (deepseek-chat...) qua sage_model.
    provider, model = _get_agent_provider("chieu_dom")
    model = sage_model(provider, model)
    resp = run_agent(
        agent_id="chieu_dom", provider=provider, model=model,
        question=("Hãy luận NỘI TÂM tổng thể cho lá số Chiếu Đởm Kinh này: cốt cách tâm hồn gốc, "
                  "các Phi Tinh đang lên tiếng, chỗ khắc khoải & chỗ sức mạnh ngầm, và 'mệnh là động "
                  "từ' — cấu trúc này vận hành đẹp nhất khi nào. KHÔNG tiên tri cát/hung."),
        chart_data={"chieu_dom": chart}, max_tokens=4000, temperature=0.6)

    if user.get("role") != "owner":
        consume_use(user["user_id"], "tu_vi_cdk_luan_cung")

    return {
        "status": "ok", "luan": resp.content,
        "provider": resp.provider, "model": resp.model,
        "menh_branch": chart.get("menh_branch"),
        "paradigm_note": "Sage Chiếu Đởm Kinh — đọc đồng dạng nội tâm, KHÔNG predict (Iron #4/#6/#8).",
    }


@router.post("/q4/cdk/eval-cach-cuc")
def yi_tuvi_cdk_eval_cach_cuc(req: _AnalyzeRequest, request: Request) -> dict:
    """Eval 6 cách cục Chiếu Đởm Kinh cho lá số cụ thể.

    Free endpoint — không cần VIP. Engine deterministic, no LLM call.
    """
    from engine.tu_vi.cdk_cach_cuc_matcher import evaluate_cdk_cach_cuc
    from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
    from core.chronos import calculate_chronos_state
    from datetime import datetime

    person = _resolve_person_from_request(req, request)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    _d, m_str, _y = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]
    chart = cast_chieu_dom_kinh(
        year_stem=year_parts[0], year_branch=year_parts[1],
        lunar_month=int(m_str), hour_branch=hour_branch, gender=person.gender,
    )
    return evaluate_cdk_cach_cuc(chart, hour_branch)


@router.post("/q4/cdk/luan-luu-nien")
def yi_tuvi_cdk_luan_luu_nien(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận Lưu Niên 10 năm tới. VIP1-gated."""
    from engine.tu_vi.cdk_cung_analyzer import luan_luu_nien_10_nam
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Cần VIP1 — {access.get('reason')}"}

    person = _resolve_person_from_request(req, request)
    result = luan_luu_nien_10_nam(person, num_years=10, force=req.force)
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
    return result


@router.post("/q4/cdk/luan-dai-han")
def yi_tuvi_cdk_luan_dai_han(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận chi tiết 8 vòng Đại Hạn CDK (80 năm). VIP1-gated."""
    from engine.tu_vi.cdk_cung_analyzer import luan_dai_han_8_vong
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Cần VIP1 — {access.get('reason')}"}

    person = _resolve_person_from_request(req, request)
    result = luan_dai_han_8_vong(person, force=req.force)
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
    return result


@router.post("/q4/cdk/luan-toan-bo")
def yi_tuvi_cdk_luan_toan_bo(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận TOÀN BỘ 12 cung CDK trong 1 phiên (2 batches × 6 cung song song).

    Faster than 12 per-cung calls. Persist cache per-cung for instant future lookup.
    VIP1 gated (owner bypass). Charges 1 use only (not 12).
    """
    from engine.tu_vi.cdk_cung_analyzer import luan_toan_bo_cung
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}

    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Không có quyền VIP1 — {access.get('reason')}", "vip_check": access}

    person = _resolve_person_from_request(req, request)
    result = luan_toan_bo_cung(person, force=req.force)

    # Consume 1 use only if fresh calls + not owner
    if result.get("status") == "ok" and user.get("role") != "owner" and result.get("fresh_calls", 0) > 0:
        usage = consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
        result["usage_after"] = usage

    return result


@router.get("/q4/chieu-dom-12cung-matrix")
def yi_tuvi_chieu_dom_12cung() -> dict:
    """12 cung × 18 sao matrix từ Chiếu Đởm Kinh (Q4 p0279-p0286). ~203 rules."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_12cung_x_18sao.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.get("/q4/phu-thi-corpus")
def yi_tuvi_phu_thi_corpus() -> dict:
    """Phú thi corpus — 786 lines từ Q4 dense band p0257-p0300 (training data phê mệnh)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/q4_phu_thi_corpus.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.get("/q4/nhap-cot-tien-kinh")
def yi_tuvi_nhap_cot_tien() -> dict:
    """Nhập Cốt Tiên Kinh tổng đoán 4-chữ per 18 Phi Tinh."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/nhap_cot_tien_kinh_tong_doan.json"
    return {"status": "ok", **json.loads(p.read_text())}


@router.get("/q4/chieu-dom-kinh-cach-cuc")
def yi_tuvi_chieu_dom_cach_cuc() -> dict:
    """6 cách cục mới của Chiếu Đởm Kinh."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_cach_cuc.json"
    return {"status": "ok", **json.loads(p.read_text())}

@router.post("/phe-menh-sau")
def yi_tuvi_phe_menh_sau(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận giải sâu Tử Vi (VIP DeepSeek Pro). VIP1-gated.

    Engine generates 10-section deep phê mệnh per Trần Đoàn methodology.
    """
    from api.auth import get_current_user
    from engine.subscriptions import check_access, consume_use
    from engine.tu_vi.analyzer import TuViAnalyzer

    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    user_id = user["user_id"]

    # Owner bypass — owner luôn có quyền
    if user.get("role") != "owner":
        access = check_access(user_id, "tu_vi_phe_menh_sau")
        if not access["allowed"]:
            raise HTTPException(403, f"VIP required: {access['reason']}")

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person, force=req.force)
    result = analyzer.phe_menh_sau()

    # Consume 1 use only if successful AND not owner
    if result.get("status") == "ok" and user.get("role") != "owner":
        usage = consume_use(user_id, "tu_vi_phe_menh_sau")
        result["usage"] = usage

    return result

@router.post("/safety-check")
def yi_tuvi_safety_check(req: _AnalyzeRequest, request: Request) -> dict:
    """Phát hiện psychological safety patterns trong lá số (Q1 p0027-p0028, Q3 p0186).

    KHÔNG predict — chỉ surface "dấu hiệu kích hoạt nhận thức" + self-care tips.
    """
    from engine.tu_vi.psychological_safety import detect_safety_patterns
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    year_stem = chronos.ganzhi.year.split()[0]
    patterns = detect_safety_patterns(analyzer.la_so, year_stem)
    return {
        "status": "ok",
        "year_stem": year_stem,
        "patterns_triggered": patterns,
        "note": "Đây là 'dấu hiệu kích hoạt nhận thức' theo Iron Rule #6, KHÔNG phải predict tự vẫn. Cổ nhân dùng để gợi mở chăm sóc bản thân, không phải hù dọa.",
        "hotlines": {
            "vi": "Đường Dây Cứu Sống 1800-1567 · Tâm Lý Xanh (online)",
            "vn_psychological_emergency": "Bệnh viện Tâm thần TW · cấp cứu 115",
        },
    }


@router.post("/chart-strength")
def yi_tuvi_chart_strength(req: _AnalyzeRequest, request: Request) -> dict:
    """Tính sức mạnh tổng thể lá số dựa trên Miếu Vượng Hãm (Q2 p0102).

    Mỗi chính tinh tại cung tương ứng có 1 level (miếu/vượng/đắc/bình/lạc/hãm).
    Tổng score = đánh giá tổng thể "khí thế" lá số.
    """
    from engine.tu_vi.mieu_vuong_ham import chart_strength
    from engine.tu_vi.analyzer import TuViAnalyzer
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    result = chart_strength(analyzer.la_so)
    return {"status": "ok", "source": "Q2 p0102 + p0103-p0125", **result}


@router.post("/dau-quan")
def yi_tuvi_dau_quan(req: _AnalyzeRequest, request: Request) -> dict:
    """Tính Đẩu Quân (斗君) per lưu niên + 12 tháng lưu nguyệt.

    Đẩu Quân là sao THEO TIME — đi qua các cung mỗi tháng/năm, quyết định
    cát/hung của giai đoạn đó (Q2 p0088 công thức, Q3 p0157 diễn giải).

    Returns Đẩu Quân năm + 12 tháng + diễn giải per palace.
    """
    from engine.tu_vi.dau_quan import (
        compute_dau_quan, compute_dau_quan_for_months, interpret_dau_quan, BRANCHES
    )
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so

    # Need lunar_month + hour_branch from birth
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    lunar_month = int(m_str)

    from datetime import datetime
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]

    # Year — default current
    year = req.luu_nguyet_year or 2026

    # Get year branch via Ganzhi
    from core.chronos import calculate_chronos_state as ccs
    year_chronos = ccs(f"{year}-06-15T12:00:00", "Asia/Ho_Chi_Minh")
    year_branch = year_chronos.ganzhi.year.split()[1]

    dq_year = compute_dau_quan(year_branch, lunar_month, hour_branch)
    dq_months = compute_dau_quan_for_months(year_branch, lunar_month, hour_branch)

    # Build palace lookup: branch_index → palace_name
    palace_at_branch = {p["branch_index"]: p["name"] for p in la_so["palaces"]}

    # Annotate each month with palace + interpretation
    for m in dq_months:
        bi = m["dau_quan_branch_index"]
        palace = palace_at_branch.get(bi, "?")
        m["palace"] = palace
        # Default to cát interpretation — UI shows both
        interp = interpret_dau_quan(palace, has_cat=True)
        m["interp_cat"] = interp["interpretation"]
        interp_h = interpret_dau_quan(palace, has_cat=False)
        m["interp_hung"] = interp_h["interpretation"]
        m["source_ref"] = interp["source"]

    return {
        "status": "ok",
        "year": year,
        "year_branch": year_branch,
        "lunar_month_birth": lunar_month,
        "hour_branch_birth": hour_branch,
        "dau_quan_year": {
            **dq_year,
            "palace": palace_at_branch.get(dq_year["dau_quan_branch_index"], "?"),
        },
        "dau_quan_months": dq_months,
        "paradigm_note": "Đẩu Quân (Q3 p0157) — đi qua cung X, gặp cát/hung tinh tại đó quyết định cát hung của tháng/năm. KHÔNG đọc cứng — chỉ là 1 layer trong nhiều layer (Đại Vận + Lưu Niên + Tiểu Hạn + Đẩu Quân).",
    }


@router.post("/case-studies/match")
def yi_tuvi_case_studies_match(req: _AnalyzeRequest, request: Request) -> dict:
    """Match lá số user với case studies lịch sử (Q3+Q4 Trần Đoàn + Khang Tiết).

    Trả về top 3 historical figures có nét giống pattern lá số.
    Anti-predict: dùng "mỗ" pattern, không phán "anh sẽ giống X".
    """
    from engine.tu_vi.case_matcher import match_cases
    person = _resolve_person_from_request(req, request)
    from engine.tu_vi.analyzer import TuViAnalyzer
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so
    result = match_cases(la_so, top_n=3)
    return {"status": "ok", **result}


@router.get("/cach-cuc-pho-bien")
def yi_tuvi_cach_cuc_pho_bien(limit: int = 50, cap_do: str = "") -> dict:
    """Liệt kê 545 cách cục kinh điển từ Phú Thái Vi (Q1).

    Query params:
        limit: số kết quả (default 50)
        cap_do: filter 'thượng' | 'trung' | 'hạ' | 'phá cách' | 'tạp' | '' (all)
    """
    from engine.tu_vi.cach_cuc_dict import all_entries, by_level, stats
    entries = by_level(cap_do) if cap_do else all_entries()
    # Sort by occurrences desc
    entries = sorted(entries, key=lambda x: x.get("occurrences", 0), reverse=True)[:limit]
    return {
        "status": "ok",
        "stats": stats(),
        "filter": {"cap_do": cap_do or "all", "limit": limit},
        "entries": entries,
    }


@router.get("/cach-cuc-pho-bien/{name}")
def yi_tuvi_cach_cuc_pho_bien_detail(name: str) -> dict:
    """Lookup 1 cách cục theo tên."""
    from engine.tu_vi.cach_cuc_dict import lookup_by_name
    entry = lookup_by_name(name)
    if not entry:
        raise HTTPException(404, f"Cách cục '{name}' không có trong dictionary 545 cách")
    return {"status": "ok", "entry": entry}


@router.post("/match-cach-cuc")
def yi_tuvi_match_cach_cuc(req: dict) -> dict:
    """Match cách cục cho lá số CỤ THỂ (deterministic, không cần DeepSeek runtime).

    Body: {
        "person_key": "self" (optional, sẽ tự cast lá số),
        "stars_at_menh": [...] (optional override),
        "stars_in_palaces": {palace: [stars]} (optional),
        "min_overlap": 2,
        "max_results": 30
    }
    """
    from engine.tu_vi.cach_cuc_dict import match_cach_in_chart
    matches = match_cach_in_chart(
        stars_at_menh=req.get("stars_at_menh", []),
        stars_in_palaces=req.get("stars_in_palaces", {}),
        min_overlap=req.get("min_overlap", 2),
        max_results=req.get("max_results", 30),
    )
    return {"status": "ok", "match_count": len(matches), "matches": matches}


@router.get("/concept-dict")
def yi_tuvi_concept_dict(kind: str = "", limit: int = 100) -> dict:
    """Liệt kê concepts (320 thuật ngữ) cho WikiText highlight + lookup."""
    from engine.tu_vi.concept_dict import load_concepts, by_kind, top_terms, stats as cstat
    if kind:
        entries = by_kind(kind)
    else:
        entries = list(load_concepts().values())
    entries = sorted(entries, key=lambda x: x.get("occurrences", 0), reverse=True)[:limit]
    return {
        "status": "ok",
        "stats": cstat(),
        "filter": {"kind": kind or "all", "limit": limit},
        "entries": entries,
    }

# ─── Job tracker (in-memory, simple) ──────────────────────────────────────────
_TUVI_JOBS: dict[str, dict] = {}


@router.post("/run-all/{person_key}")
def yi_tuvi_run_all(person_key: str, request: Request, background_tasks: BackgroundTasks) -> dict:
    """Trigger background full pipeline (cach_cuc + dai_van + luu_nien + luu_nguyet) for a person.

    Returns job_id immediately; UI polls /api/tu-vi/job-status/{job_id}.
    """
    from engine.tu_vi.analyzer import TuViAnalyzer, Person
    from api.auth import get_current_user, AUTH_DB
    import sqlite3, uuid

    # Resolve person (scoped per-user)
    user = get_current_user(request)
    uid = user["user_id"] if user else None
    if person_key == "_founder":
        # Owner-only: legacy founder profile was returning anh's hardcoded
        # birth to ANY caller (used to be a guest-mode oracle). Now any
        # non-owner triggering pipeline against _founder gets 404.
        if not user or user.get("role") != "owner":
            raise HTTPException(404, "person not found")
        person = Person(person_key="_founder", name="anh (Founder)",
                        birth_datetime_local="1988-06-05T23:30:00", gender="nam",
                        user_id=uid)
    else:
        if not user:
            raise HTTPException(401, "Login required")
        db = sqlite3.connect(AUTH_DB)
        row = db.execute(
            "SELECT name, gender, birth_datetime_local, timezone FROM user_persons WHERE user_id=? AND person_key=?",
            (user["user_id"], person_key),
        ).fetchone()
        db.close()
        if not row:
            raise HTTPException(404, f"person_key '{person_key}' not found")
        person = Person(person_key=person_key, name=row[0],
                        gender=row[1] or "nam",
                        birth_datetime_local=row[2] or "",
                        timezone=row[3] or "Asia/Ho_Chi_Minh",
                        user_id=user["user_id"])

    job_id = f"tuvi_{person_key}_{uuid.uuid4().hex[:8]}"
    _TUVI_JOBS[job_id] = {
        "job_id": job_id,
        "person_key": person_key,
        "person_name": person.name,
        "status": "queued",
        "progress": 0,
        "total_steps": 4,
        "current_step": "",
        "started_at": time.time(),
        "finished_at": None,
        "error": None,
        "cost_usd": 0.0,
    }

    def _run():
        job = _TUVI_JOBS[job_id]
        try:
            analyzer = TuViAnalyzer(person)
            total_cost = 0.0
            steps = [
                ("cach_cuc", lambda: analyzer.discover_cach_cuc()),
                ("dai_van", lambda: analyzer.dai_van_annotate()),
                ("luu_nien", lambda: analyzer.luu_nien(2026, 2030)),
                ("luu_nguyet", lambda: analyzer.luu_nguyet(2026)),
            ]
            job["status"] = "running"
            for i, (name, fn) in enumerate(steps, 1):
                job["current_step"] = name
                job["progress"] = i - 1
                try:
                    result = fn()
                    total_cost += result.get("cost_usd", 0) or 0
                except Exception as step_err:
                    logger.exception(f"step {name} failed: {step_err}")
                    job["error"] = f"{name}: {step_err}"
                job["progress"] = i
                job["cost_usd"] = round(total_cost, 6)
            job["status"] = "done"
            job["finished_at"] = time.time()
            job["current_step"] = ""
        except Exception as e:
            logger.exception("run_all background failed")
            job["status"] = "error"
            job["error"] = str(e)
            job["finished_at"] = time.time()

    background_tasks.add_task(_run)
    return {"status": "queued", "job_id": job_id, "person_key": person_key}


@router.get("/job-status/{job_id}")
def yi_tuvi_job_status(job_id: str) -> dict:
    job = _TUVI_JOBS.get(job_id)
    if not job:
        return {"status": "not_found", "job_id": job_id}
    return {"status": "ok", **job}


# ─── PDF Report ──────────────────────────────────────────────────────────────
@router.get("/report-pdf/{person_key}")
def yi_tuvi_report_pdf(person_key: str, request: Request):
    """Generate "Báo cáo Lá Số" PDF for a person. Special (_) keys are owner-only."""
    from fastapi.responses import FileResponse
    from engine.tu_vi.report_pdf import generate_pdf
    from api.auth import get_current_user
    user = get_current_user(request)
    if person_key.startswith("_") and (not user or user.get("role") != "owner"):
        raise HTTPException(403, "owner-only for special person keys")
    uid = user["user_id"] if user else None
    try:
        pdf_path = generate_pdf(person_key, user_id=uid)
    except Exception as e:
        logger.exception("PDF generation failed")
        raise HTTPException(500, f"PDF gen failed: {e}")
    filename = f"bao-cao-la-so-{person_key}.pdf"
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=filename)
