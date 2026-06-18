"""H6.0 slice 2 — Council đa-user (orchestration).

Vòng 1 (ô chat user): scope guard → resolve user → gate gói → reserve ngân sách →
council (đa-sage, in-process, chạy ở worker q_hermes) → post-filter paradigm →
lưu lịch sử → consume. Mirror engine/deep_reading.py (đã chứng minh ở H5).

- Cổng RẺ trước (scope guard slice 1): out_of_scope / needs_focus → trả NGAY,
  KHÔNG resolve, KHÔNG tính tiền, KHÔNG gọi LLM.
- `consult` tiêm được (test = stub) → không cần LLM/Mac/wiki-DB để test orchestration.
- Persona SOUL sâu (profiles/*/SOUL.md) dùng ở bản council thật — nâng dần (follow-up).
"""
from __future__ import annotations

import json
import time
from typing import Callable, Optional

from sqlalchemy import text

from engine import hermes_guard as guard
from engine import llm_spend
from engine import subscriptions as subs
from engine.algo_version import algo_version
from engine.db import is_postgres, session_scope
from engine.deep_reading import _resolve  # tái dùng uid→(user_id, person)

FEATURE = "hermes_council"

# tag sage → thư mục profile (đồng bộ engine/ai/kanban_council.SAGES_BY_TAG)
SAGE_PROFILE = {
    "mai_hoa": "mai-hoa-sage", "luc_hao": "luc-hao-sage", "lien_hoa": "lien-hoa-sage",
    "tu_vi": "tu-vi-sage", "bat_tu": "bat-tu-sage", "ha_lac": "ha-lac-sage",
    "than_so": "than-so-sage", "western": "chiem-tinh-sage",
}


def _real_consult(question: str, person: dict, uid: int) -> dict:
    """Bọc council in-process sẵn có. (Nâng dùng SOUL sâu = follow-up.)"""
    from engine.ai.council import consult_council
    chart = {"birth_datetime_local": person.get("birth_datetime_local"),
             "gender": person.get("gender")}
    res = consult_council(question=question, chart_data=chart, persist=False)
    return {
        "synthesis": res.get("final_synthesis") or "",
        "agents": res.get("agents_consulted") or [],
        "provider": (res.get("providers_used") or ["deepseek"])[0],
        "cost_usd": float(res.get("cost_usd") or 0),
        "raw": res,
    }


def run_council(firebase_uid: str, question: str, person_key: str = "self", *,
                consult: Optional[Callable[[str, dict, int], dict]] = None) -> dict:
    """Chạy 1 lượt Hội Đồng. KHÔNG idempotent → task gọi phải at-most-once."""
    # 0) Cổng RẺ: rào phạm vi Socratic (chưa tốn gì)
    sv = guard.classify_scope(question)
    if sv.verdict != "in_scope":
        return {"status": sv.verdict, "reply": sv.reply, "reason": sv.reason}

    consult = consult or _real_consult
    uid, person = _resolve(firebase_uid, person_key)
    if uid is None:
        return {"status": "error", "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"status": "error", "reason": "missing_birth"}

    access = subs.check_access(uid, FEATURE)
    if not access["allowed"]:
        return {"status": "denied", "reason": access["reason"]}

    # reserve ngân sách atomic (P0-5) — vượt cap → từ chối, không gọi LLM
    est = float(subs.FEATURE_CATALOG.get(FEATURE, {}).get("cost_estimate_usd", 0.08))
    if not llm_spend.try_charge(cost_usd=est, feature=FEATURE, model="reserve",
                                user_id=str(uid)):
        return {"status": "budget_exceeded"}

    def _refund():
        llm_spend.record_spend(provider="reserve", cost_usd=-est, feature=FEATURE,
                               model="refund", user_id=str(uid))

    try:
        result = consult(question, person, uid)
        if not isinstance(result, dict) or not result.get("synthesis"):
            _refund()
            return {"status": "error", "reason": "council_failed"}

        # post-filter paradigm: synthesis KHÔNG được mang giọng tiên tri
        violations = guard.paradigm_violations(result.get("synthesis", ""))
        paradigm_ok = not violations

        av = algo_version("tu_vi")
        payload = {"synthesis": result.get("synthesis"), "agents": result.get("agents"),
                   "paradigm_ok": paradigm_ok, "violations": violations}
        res_expr = "CAST(:res AS JSONB)" if is_postgres() else ":res"
        with session_scope(service=True) as conn:
            cid = conn.execute(
                text(f"""INSERT INTO user_castings
                        (user_id, method, subject_person_key, question, result_json,
                         verdict, tags, note, algo_version, created_at)
                        VALUES (:uid,'hermes_council',:pk,:q,{res_expr},:vd,'council',NULL,:av,:now)
                        RETURNING id"""),
                {"uid": uid, "pk": person_key, "q": question[:500],
                 "res": json.dumps(payload, ensure_ascii=False),
                 "vd": "paradigm_flag" if violations else None,
                 "av": av, "now": int(time.time())},
            ).scalar()
        usage = subs.consume_use(uid, FEATURE)
    except Exception:
        _refund()
        raise

    # điều chỉnh đặt-chỗ → cost thật (nếu council báo)
    real_cost = float(result.get("cost_usd") or 0)
    if real_cost > 0:
        llm_spend.record_spend(provider=result.get("provider", "deepseek"),
                               cost_usd=real_cost - est, feature=FEATURE,
                               user_id=str(uid))
    return {
        "status": "done", "casting_id": cid, "algo_version": av,
        "agents": result.get("agents"), "paradigm_ok": paradigm_ok,
        "synthesis": result.get("synthesis"),
        "remaining_uses": usage.get("remaining_uses") if usage.get("ok") else None,
    }
