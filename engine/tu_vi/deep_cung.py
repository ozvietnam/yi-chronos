"""Luận SÂU 1 cung (−10 xu, cache vĩnh viễn) — yêu cầu AppChat #3 (2026-06-24).

Luồng: cache (đã mua cung này → KHÔNG trừ lại) → trừ 10 xu ví trung tâm → sinh LLM (deepseek-chat,
non-reasoning tin cậy) → lưu (cache) → trả {interpretation, xu_balance, cached}. Lỗi LLM → HOÀN xu.
Cache invalidate khi knowledge_version bump (sách/lăng kính mới → luận lại MIỄN PHÍ, không trừ lần 2).
Đọc đồng dạng (mệnh là động từ) — không predict cát/hung.
"""
from __future__ import annotations

import json
import logging
import time

from sqlalchemy import text

from engine.db import is_postgres, session_scope

logger = logging.getLogger("yi.deep_cung")

DEEP_CUNG_XU = 10

# cung_key canonical → tên Việt (12 cung chức năng)
CUNG_KEYS = {
    "menh": "Mệnh", "huynh_de": "Huynh Đệ", "phu_the": "Phu Thê", "tu_tuc": "Tử Tức",
    "tai_bach": "Tài Bạch", "tat_ach": "Tật Ách", "thien_di": "Thiên Di", "no_boc": "Nô Bộc",
    "quan_loc": "Quan Lộc", "dien_trach": "Điền Trạch", "phuc_duc": "Phúc Đức", "phu_mau": "Phụ Mẫu",
}


def _cached(user_id: int, cung_key: str):
    """Cache vĩnh viễn theo (user, cung) — chỉ vô hiệu khi knowledge_version bump (luận lại free)."""
    cutoff = 0
    try:
        from engine.system_meta import knowledge_version_updated_at
        cutoff = knowledge_version_updated_at()
    except Exception:
        pass
    with session_scope(service=True) as conn:
        row = conn.execute(text(
            """SELECT result_json FROM user_castings WHERE user_id=:u AND method='deep_cung'
               AND question=:q AND created_at>=:c ORDER BY id DESC LIMIT 1"""),
            {"u": user_id, "q": cung_key, "c": cutoff}).fetchone()
    if not row:
        return None
    rj = row[0]
    return rj if isinstance(rj, dict) else (json.loads(rj) if rj else None)


def _store(user_id: int, cung_key: str, interp: str) -> None:
    from engine.algo_version import algo_version
    payload = {"interpretation": interp, "cung_key": cung_key}
    res_expr = "CAST(:res AS JSONB)" if is_postgres() else ":res"
    with session_scope(service=True) as conn:
        conn.execute(text(
            f"""INSERT INTO user_castings (user_id, method, subject_person_key, question,
                    result_json, verdict, tags, note, algo_version, created_at)
                VALUES (:uid,'deep_cung','self',:q,{res_expr},NULL,'deep_cung',NULL,:av,:now)"""),
            {"uid": user_id, "q": cung_key, "res": json.dumps(payload, ensure_ascii=False),
             "av": algo_version("tu_vi"), "now": int(time.time())})


def _generate(person: dict, cung_key: str) -> str:
    """Sinh luận sâu 1 cung qua LLM (deepseek-chat) — bám sao thực tế trong cung + đọc đồng dạng."""
    from engine.ai.agents import run_agent
    from engine.ai.council import _get_agent_provider
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.per_cung_reading import per_cung_star_reading
    birth = person["birth_datetime_local"]
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    gender = person.get("gender") or "nam"
    cung_vi = CUNG_KEYS[cung_key]
    ls = cast_la_so_from_birth(birth_datetime_local=birth, timezone=tz, gender=gender)
    this_cung = next((c for c in per_cung_star_reading(ls) if c["cung"] == cung_vi), None)
    chart = {"birth_datetime_local": birth, "gender": gender, "timezone": tz,
             "tu_vi_cung_can_luan": this_cung, "menh_cung": ls.get("menh_branch")}
    provider, model = _get_agent_provider("tu_vi")
    try:
        from engine.ai.council import sage_model
        model = sage_model(provider, model)
    except Exception:
        from engine.ai.council import _SAGE_FAST_MODEL
        model = _SAGE_FAST_MODEL.get(provider.name, model)
    q = (f"Luận SÂU cung {cung_vi} cho người này (các sao thực tế trong cung đã cho ở chart). "
         f"Nêu: ý nghĩa tổ hợp sao trong cung, cung này VẬN HÀNH thế nào trong đời (mệnh là động từ — "
         f"cách dùng cái tính, không phải án định), gợi mở + lời khuyên thực tế. Đọc đồng dạng, KHÔNG "
         f"phán trước cát/hung cứng. ~250–400 chữ, văn xuôi tiếng Việt.")
    resp = run_agent(agent_id="tu_vi", provider=provider, model=model, question=q,
                     chart_data=chart, round_label="deep_cung", challenges=None, max_tokens=1500)
    return resp.content or ""


def deep_cung_reading(user_id: int, person: dict, cung_key: str) -> dict:
    """Trả {interpretation, xu_balance, cached} | {insufficient, need, have} | {error}."""
    if cung_key not in CUNG_KEYS:
        return {"error": "invalid_cung"}
    from engine import xu_wallet
    cached = _cached(user_id, cung_key)
    if cached and cached.get("interpretation"):
        return {"interpretation": cached["interpretation"],
                "xu_balance": xu_wallet.get_balance(user_id), "cached": True}
    spend = xu_wallet.spend(user_id, DEEP_CUNG_XU, f"deep_cung:{cung_key}")
    if not spend["ok"]:
        return {"insufficient": True, "need": DEEP_CUNG_XU, "have": spend.get("have", 0)}
    try:
        interp = _generate(person, cung_key)
    except Exception as e:
        xu_wallet.grant(user_id, DEEP_CUNG_XU, f"refund_deep_cung:{cung_key}")
        logger.info("deep_cung generate lỗi → hoàn xu: %s", str(e)[:120])
        return {"error": "generation_failed"}
    if not interp or len(interp.strip()) < 30:
        xu_wallet.grant(user_id, DEEP_CUNG_XU, f"refund_deep_cung:{cung_key}")
        return {"error": "empty_answer"}
    _store(user_id, cung_key, interp)
    return {"interpretation": interp, "xu_balance": spend["balance"], "cached": False}
