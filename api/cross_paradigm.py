"""API authed-self cho orchestrator liên-phái (web YI-Chronos).

#55 hôn nhân song phái (1 lá, 12 khía cạnh) + #56 so đôi đích danh (2 lá). Đối ứng
kênh service-keyed AppChat ở `api/sync.py`. CÙNG lõi (`engine.cross_paradigm.service`)
→ cùng ví xu TRUNG TÂM, cùng cache "một việc một lần" (Iron #4), không double-charge.

Privacy: `require_caller` (session cookie / X-API-Key) — KHÁCH ẩn danh → 401. User chỉ
luận trên person CỦA CHÍNH MÌNH (resolve theo user_id của caller) → không IDOR.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text

from api.service_auth import require_caller
from engine.db import session_scope

router = APIRouter(tags=["cross-paradigm"])


def _person(user_id: int, person_key: str) -> Optional[dict]:
    with session_scope(service=True) as conn:
        p = conn.execute(
            text("""SELECT gender, birth_datetime_local, timezone
                    FROM user_persons WHERE user_id=:u AND person_key=:pk"""),
            {"u": user_id, "pk": person_key},
        ).fetchone()
    if not p:
        return None
    return {"gender": p[0], "birth_datetime_local": p[1],
            "timezone": p[2] or "Asia/Ho_Chi_Minh"}


class BirthInput(BaseModel):
    datetime_local: Optional[str] = None
    gender: Optional[str] = None
    timezone: str = "Asia/Ho_Chi_Minh"


class HonNhanRequest(BaseModel):
    person_key: str = "self"


@router.post("/api/cross-paradigm/hon-nhan")
def hon_nhan_self(req: HonNhanRequest,
                  caller: dict = Depends(require_caller)) -> dict:
    """#55 — hợp nhất song phái (12 khía cạnh) cho lá của chính user. Trừ 30 xu."""
    from engine.cross_paradigm import service as cps
    uid = int(caller["user_id"])
    person = _person(uid, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh — cập nhật person trước khi luận")
    out = cps.run_hon_nhan_song_phai(uid, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return out


class TinhDuyenRequest(BaseModel):
    person_key: str = "self"


@router.post("/api/cross-paradigm/tinh-duyen")
def tinh_duyen_self(req: TinhDuyenRequest,
                    caller: dict = Depends(require_caller)) -> dict:
    """Tình duyên nữ mệnh (engine làm giàu) cho lá của chính user. Trừ 30 xu (cache Iron #4)."""
    from engine.cross_paradigm import service as cps
    uid = int(caller["user_id"])
    person = _person(uid, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh — cập nhật person trước khi luận")
    out = cps.run_tinh_duyen(uid, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return out


@router.post("/api/cross-paradigm/tinh-duyen/narrate")
def tinh_duyen_narrate(req: TinhDuyenRequest,
                       caller: dict = Depends(require_caller)) -> dict:
    """Diễn đạt (sage narrate) output tình duyên đã cached — KHÔNG charge thêm.

    Đọc lại engine output qua run_tinh_duyen: nếu đã cached trong TTL (Iron #4) → trả
    bản cũ với charged_xu=0; chỉ trừ xu nếu user CHƯA từng luận (miss cache)."""
    from engine.cross_paradigm import service as cps
    from engine.cross_paradigm.narrate import narrate_tinh_duyen
    uid = int(caller["user_id"])
    person = _person(uid, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh — cập nhật person trước khi luận")
    out = cps.run_tinh_duyen(uid, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    narration = narrate_tinh_duyen(person, out)
    return {"narration": narration}


class CoupleSyncRequest(BaseModel):
    person_key: str = "self"
    partner_person_key: Optional[str] = None
    partner_birth: Optional[BirthInput] = None


@router.post("/api/couple-sync")
def couple_sync_self(req: CoupleSyncRequest,
                     caller: dict = Depends(require_caller)) -> dict:
    """#56 — so đôi đích danh 2 lá. Người thứ 2: partner_person_key (đã lưu) hoặc
    partner_birth (nhập trực tiếp, KHÔNG lưu — PDPL). Trừ 30 xu (cache Iron #4)."""
    from engine.cross_paradigm import service as cps
    uid = int(caller["user_id"])
    person_a = _person(uid, req.person_key)
    person_b = None
    if req.partner_person_key:
        person_b = _person(uid, req.partner_person_key)
    if req.partner_birth and req.partner_birth.datetime_local:
        person_b = {"gender": req.partner_birth.gender,
                    "birth_datetime_local": req.partner_birth.datetime_local,
                    "timezone": req.partner_birth.timezone}
    if not person_a or not person_a.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh của bạn (person 'self')")
    if not person_b or not person_b.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh người thứ 2 (partner_person_key hoặc partner_birth)")
    out = cps.run_couple_sync(uid, person_a, person_b)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return out
