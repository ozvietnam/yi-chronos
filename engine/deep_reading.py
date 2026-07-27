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
from engine import xu_wallet
from engine.algo_version import algo_version
from engine.db import is_postgres, session_scope

FEATURE = "tu_vi_phe_menh_sau"
DEEP_XU = xu_wallet.XU_COST.get("deep", 99)   # giá luận sâu trọn lá số (thống nhất về XU 2026-07-27)


def _resolve(firebase_uid: str = "", person_key: str = "self", *,
             user_id: Optional[int] = None):
    """(user_id, person_dict) hoặc (None, None). Web truyền `user_id` trực tiếp (login
    session); AppChat truyền `firebase_uid` → tra user_id."""
    with session_scope(service=True) as conn:
        uid = user_id
        if uid is None:
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


def _is_owner(uid: Optional[int]) -> bool:
    """Chủ tài khoản (role='owner') luôn được luận sâu — bỏ cổng gói VIP + không trừ lượt.
    (Bug live 2026-07: owner bị 'hết lượt' vì thiếu row user_subscriptions trên prod.)"""
    if uid is None:
        return False
    try:
        with session_scope(service=True) as conn:
            row = conn.execute(
                text("SELECT role FROM users WHERE user_id=:u"), {"u": uid},
            ).fetchone()
        return bool(row and row[0] == "owner")
    except Exception:
        return False


def _latest_saved(uid: int, person_key: str) -> Optional[dict]:
    """Bản luận sâu ĐÃ LƯU gần nhất cho (user, person) khớp algo_version hiện tại →
    tái dùng, KHÔNG trừ xu, KHÔNG sinh lại (chống tính tiền 2 lần khi mở lại — Anh 2026-07-27)."""
    av = algo_version("tu_vi")
    try:
        with session_scope(service=True) as conn:
            row = conn.execute(
                text("""SELECT result_json FROM user_castings
                        WHERE user_id=:u AND subject_person_key=:pk AND method='tu_vi'
                          AND tags LIKE '%deep%' AND algo_version=:av
                        ORDER BY created_at DESC, id DESC LIMIT 1"""),
                {"u": uid, "pk": person_key, "av": av},
            ).fetchone()
    except Exception:
        return None
    if not row or not row[0]:
        return None
    try:
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    except Exception:
        return None


def get_latest(firebase_uid: str = "", person_key: str = "self", *,
               user_id: Optional[int] = None) -> Optional[dict]:
    """Trả bản luận sâu đã lưu (KHÔNG trừ tiền) cho endpoint nạp-lại khi mở panel."""
    uid, _ = _resolve(firebase_uid, person_key, user_id=user_id)
    if uid is None:
        return None
    r = _latest_saved(uid, person_key)
    if not r:
        return None
    return {"status": "done", "cached": True, "phe_menh": r.get("phe_menh"),
            "paradigm_note": r.get("paradigm_note"), "provider": r.get("provider")}


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


def precheck(firebase_uid: str = "", person_key: str = "self", *,
             user_id: Optional[int] = None) -> dict:
    """Kiểm nhanh trước khi enqueue (cho endpoint trả 404/403 sớm). Web truyền user_id."""
    uid, person = _resolve(firebase_uid, person_key, user_id=user_id)
    if uid is None:
        return {"ok": False, "code": 404, "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"ok": False, "code": 422, "reason": "missing_birth"}
    if _is_owner(uid):                                    # chủ tài khoản: luôn được
        return {"ok": True, "user_id": uid}
    if _latest_saved(uid, person_key):                   # đã luận rồi → mở lại MIỄN PHÍ
        return {"ok": True, "user_id": uid, "cached": True}
    bal = xu_wallet.get_balance(uid)                     # chưa có → cần đủ xu
    if bal < DEEP_XU:
        return {"ok": False, "code": 402, "reason": "insufficient_xu",
                "need": DEEP_XU, "have": bal}
    return {"ok": True, "user_id": uid}


def run_deep_reading(firebase_uid: str = "", person_key: str = "self", *,
                     user_id: Optional[int] = None, force: bool = False,
                     generate: Optional[Callable[[dict, int], dict]] = None) -> dict:
    """Chạy 1 lần luận sâu end-to-end. THỐNG NHẤT XU (2026-07-27):
    cache (đã luận → trả lại MIỄN PHÍ, không sinh lại) → trừ DEEP_XU (owner miễn) →
    sinh LLM → lưu user_castings → HOÀN xu nếu lỗi. force=True = luận lại (vẫn trừ xu)."""
    generate = generate or _generate
    uid, person = _resolve(firebase_uid, person_key, user_id=user_id)
    if uid is None:
        return {"status": "error", "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"status": "error", "reason": "missing_birth"}

    owner = _is_owner(uid)

    # CACHE: đã luận rồi (và không ép luận lại) → trả bản cũ, KHÔNG trừ tiền, KHÔNG sinh lại.
    if not force:
        cached = _latest_saved(uid, person_key)
        if cached:
            return {"status": "done", "cached": True,
                    "phe_menh": cached.get("phe_menh"),
                    "paradigm_note": cached.get("paradigm_note"),
                    "provider": cached.get("provider"),
                    "xu_balance": xu_wallet.get_balance(uid)}

    # TRỪ XU (owner miễn phí). Thiếu xu → dừng, KHÔNG gọi LLM.
    charged = False
    if not owner:
        sp = xu_wallet.spend(uid, DEEP_XU, f"deep_reading:{person_key}")
        if not sp.get("ok"):
            return {"status": "denied", "reason": "insufficient_xu",
                    "need": sp.get("need", DEEP_XU), "have": sp.get("have", 0)}
        charged = True

    # Đặt-chỗ ngân sách ATOMIC (cost-safety USD, tách khỏi ví xu người dùng).
    est = float(subs.FEATURE_CATALOG.get(FEATURE, {}).get("cost_estimate_usd", 0.05))
    if not llm_spend.try_charge(cost_usd=est, feature=FEATURE, model="reserve",
                                user_id=str(uid)):
        if charged:
            xu_wallet.grant(uid, DEEP_XU, f"refund_deep_reading:{person_key}")
        return {"status": "budget_exceeded"}

    def _refund():
        # hoàn khoản đặt-chỗ USD + HOÀN XU đã trừ (giữ "không tính tiền khi lỗi").
        llm_spend.record_spend(provider="reserve", cost_usd=-est, feature=FEATURE,
                               model="refund", user_id=str(uid))
        if charged:
            xu_wallet.grant(uid, DEEP_XU, f"refund_deep_reading:{person_key}")

    try:
        result = generate(person, uid)
        if not isinstance(result, dict) or result.get("status") == "error":
            _refund()
            return {"status": "error", "reason": "generation_failed",
                    "detail": (result or {}).get("message")}

        # Lưu lịch sử (H1) + trừ lượt. Nếu save/consume lỗi → except _refund() bên dưới.
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
    except Exception:
        _refund()
        raise

    # Điều chỉnh đặt-chỗ → cost THẬT provider báo (phe_menh trả cost_usd + tokens):
    # ghi delta = thật − ước lượng (có thể âm). Tránh under-count khi fallback rơi vào
    # provider đắt. record_spend nuốt lỗi → fail chỉ lệch nhẹ, không hỏng request.
    real_cost = float(result.get("cost_usd") or 0)
    if real_cost > 0:
        toks = result.get("tokens") or {}
        llm_spend.record_spend(provider=result.get("provider", "deepseek"),
                               cost_usd=real_cost - est, feature=FEATURE,
                               model=result.get("model", ""),
                               tokens_in=int(toks.get("prompt") or 0),
                               tokens_out=int(toks.get("completion") or 0),
                               user_id=str(uid))
    return {
        "status": "done", "cached": False, "casting_id": cid, "algo_version": av,
        "provider": result.get("provider"),
        "phe_menh": result.get("phe_menh"),               # nội dung luận để frontend render
        "paradigm_note": result.get("paradigm_note"),
        "xu_balance": xu_wallet.get_balance(uid),
    }
