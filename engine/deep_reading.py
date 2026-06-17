"""H5 — luận sâu DeepSeek (orchestration). Bọc `TuViAnalyzer.phe_menh()` sẵn có
(KHÔNG viết lại generation) + thêm các lớp P0:

  gating (subscriptions) → hard-stop ngân sách (llm_spend) → generate (LLM) →
  record_spend → lưu lịch sử (user_castings, H1) → consume_use.

Tách khỏi Celery task để test trực tiếp (generation tiêm được = mock, không cần
DeepSeek thật). Service-side theo user_id tường minh → session_scope(service=True).

Paradigm (Iron #6/#8): chỉ gửi chart facts (can-chi/sao/cung) sang LLM — KHÔNG
uid/tên/sđt (pseudonymize PDPL). phe_menh đã có paradigm guard + postcheck.
"""
from __future__ import annotations

import json
import time
from typing import Callable, Optional

from sqlalchemy import text

from engine import llm_spend
from engine import subscriptions as subs
from engine.algo_version import algo_version
from engine.db import is_postgres, session_scope

FEATURE = "tu_vi_phe_menh_sau"


def _resolve(firebase_uid: str, person_key: str):
    """(user_id, person_dict) hoặc (None, None) nếu chưa sync / không có person."""
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("SELECT user_id FROM users WHERE firebase_uid=:u"),
            {"u": firebase_uid},
        ).fetchone()
        if not row:
            return None, None
        uid = row[0]
        p = conn.execute(
            text("""SELECT name, gender, birth_datetime_local, timezone
                    FROM user_persons WHERE user_id=:u AND person_key=:pk"""),
            {"u": uid, "pk": person_key},
        ).fetchone()
    person = None
    if p:
        person = {"name": p[0], "gender": p[1],
                  "birth_datetime_local": p[2], "timezone": p[3] or "Asia/Ho_Chi_Minh"}
    return uid, person


def _generate(person: dict, user_id: int) -> dict:
    """Sinh luận sâu — bọc engine có sẵn. Chỉ chart facts đi vào LLM (pseudonymous)."""
    from engine.tu_vi.analyzer import Person, TuViAnalyzer
    pp = Person(
        person_key="self", name="",          # KHÔNG gửi tên thật sang LLM
        birth_datetime_local=person["birth_datetime_local"],
        gender=person["gender"], timezone=person.get("timezone", "Asia/Ho_Chi_Minh"),
        user_id=user_id,
    )
    return TuViAnalyzer(pp).phe_menh()


def precheck(firebase_uid: str, person_key: str = "self") -> dict:
    """Kiểm nhanh trước khi enqueue (cho endpoint trả 404/403 sớm)."""
    uid, person = _resolve(firebase_uid, person_key)
    if uid is None:
        return {"ok": False, "code": 404, "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"ok": False, "code": 422, "reason": "missing_birth"}
    access = subs.check_access(uid, FEATURE)
    if not access["allowed"]:
        return {"ok": False, "code": 403, "reason": access["reason"]}
    return {"ok": True, "user_id": uid}


def run_deep_reading(firebase_uid: str, person_key: str = "self", *,
                     generate: Optional[Callable[[dict, int], dict]] = None) -> dict:
    """Chạy 1 lần luận sâu end-to-end. KHÔNG idempotent (mỗi lần gọi = 1 lần tốn
    tiền LLM + 1 lần trừ lượt) → task gọi nó phải at-most-once (xem deepread_run).
    Chỉ record_spend + consume_use khi generation + save THÀNH CÔNG."""
    generate = generate or _generate
    uid, person = _resolve(firebase_uid, person_key)
    if uid is None:
        return {"status": "error", "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"status": "error", "reason": "missing_birth"}

    access = subs.check_access(uid, FEATURE)
    if not access["allowed"]:
        return {"status": "denied", "reason": access["reason"]}

    # Hard-stop ngân sách LLM (master plan §5) — KHÔNG gọi LLM nếu đã vượt.
    if llm_spend.over_daily_budget():
        return {"status": "budget_exceeded"}

    result = generate(person, uid)
    if not isinstance(result, dict) or result.get("status") == "error":
        # generation lỗi → KHÔNG trừ lượt/không tính tiền
        return {"status": "error", "reason": "generation_failed",
                "detail": (result or {}).get("message")}

    # Thứ tự: lưu lịch sử (H1) + trừ lượt TRƯỚC, ghi chi phí SAU. Nếu save lỗi →
    # exception thoát ra trước khi consume/record → user KHÔNG mất lượt, KHÔNG bị
    # tính tiền (chỉ mất 1 lần sinh — họ gọi lại). Tránh "charged-but-lost".
    av = algo_version("tu_vi")
    res_expr = "CAST(:res AS JSONB)" if is_postgres() else ":res"
    with session_scope(service=True) as conn:
        cid = conn.execute(
            text(f"""INSERT INTO user_castings
                    (user_id, method, subject_person_key, question, result_json,
                     verdict, tags, note, algo_version, created_at)
                    VALUES (:uid,'tu_vi',:pk,:q,{res_expr},NULL,'deep,phe_menh',NULL,:av,:now)
                    RETURNING id"""),
            {"uid": uid, "pk": person_key, "q": "Luận sâu phê mệnh (DeepSeek)",
             "res": json.dumps(result, ensure_ascii=False), "av": av,
             "now": int(time.time())},
        ).scalar()

    usage = subs.consume_use(uid, FEATURE)

    # Ghi chi phí cuối cùng. Ưu tiên cost THẬT provider báo (phe_menh trả cost_usd +
    # tokens) — fallback ước lượng catalog chỉ khi provider không báo (cost<=0).
    # Tránh under-count khi fallback rơi vào provider đắt (vd Anthropic). record_spend
    # tự nuốt lỗi → fail chỉ under-count, không hỏng request đã thành công.
    real_cost = float(result.get("cost_usd") or 0)
    cost = real_cost if real_cost > 0 else float(
        subs.FEATURE_CATALOG.get(FEATURE, {}).get("cost_estimate_usd", 0.05))
    toks = result.get("tokens") or {}
    llm_spend.record_spend(provider=result.get("provider", "deepseek"),
                           cost_usd=cost, feature=FEATURE, model=result.get("model", ""),
                           tokens_in=int(toks.get("prompt") or 0),
                           tokens_out=int(toks.get("completion") or 0),
                           user_id=str(uid))
    return {
        "status": "done", "casting_id": cid, "algo_version": av,
        "provider": result.get("provider"),
        "remaining_uses": usage.get("remaining_uses") if usage.get("ok") else None,
    }
