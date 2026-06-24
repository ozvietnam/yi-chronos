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
from pathlib import Path
from typing import Callable, Optional

from sqlalchemy import text

from engine import hermes_guard as guard
from engine import llm_spend
from engine import ratelimit
from engine import subscriptions as subs
from engine import xu_wallet
from engine.algo_version import algo_version
from engine.db import is_postgres, session_scope
from engine.deep_reading import _resolve  # tái dùng uid→(user_id, person)

FEATURE = "hermes_council"
FREE_DAILY_COUNCIL = 3          # FREE tier: council 3 lượt/ngày (premium đa-sage)
FREE_DAILY_QUICK = 10           # FREE tier: trả lời nhanh 1-sage 10 lượt/ngày (rẻ, hằng ngày)
QUICK_EST_USD = 0.01            # 1 lần gọi LLM 1 sage — rẻ hơn council nhiều
_DAY = 86400
# Chi phí xu theo loại (ví TRUNG TÂM ở YI — khớp AppChat). Sau khi hết free/ngày
# (không có gói VIP) → tiêu xu thay vì denied cứng. Xem engine/xu_wallet.py.
_XU_KIND = {"quick_free": "quick", "council_free": "council"}


CACHE_TTL_SEC = 86400          # "một việc một lần" (Iron #4): cùng câu/ngày → trả lại cũ


def _person_of(user_id: int, person_key: str = "self") -> Optional[dict]:
    """Lấy person của user (web auth — đã có user_id, không cần firebase_uid)."""
    with session_scope(service=True) as conn:
        p = conn.execute(
            text("""SELECT name, gender, birth_datetime_local, timezone
                    FROM user_persons WHERE user_id=:u AND person_key=:pk"""),
            {"u": user_id, "pk": person_key},
        ).fetchone()
    if not p:
        return None
    return {"name": p[0], "gender": p[1], "birth_datetime_local": p[2],
            "timezone": p[3] or "Asia/Ho_Chi_Minh"}


def _resolve_entry(firebase_uid: Optional[str], user_id: Optional[int], person_key: str):
    """Web (user_id trực tiếp) hoặc AppChat service (firebase_uid → user_id)."""
    if user_id is not None:
        return user_id, _person_of(user_id, person_key)
    return _resolve(firebase_uid, person_key)


def _cached(uid: int, method: str, question: str, ttl: int = CACHE_TTL_SEC):
    """Exact-dedup theo (user, method, câu hỏi) trong TTL → tái dùng kết quả đã lưu
    (user_castings). Iron #4 'một việc một lần' + cắt chi phí LLM. Trả (casting_id, data)
    hoặc (None, None). Dùng chính storage lịch sử — KHÔNG bảng mới."""
    import json as _j
    cutoff = int(time.time()) - ttl
    # ADR 3-tầng §3: cache T3 tự vô hiệu khi knowledge_version bump (sách/lăng kính
    # mới được duyệt) — entry tạo TRƯỚC lần bump cuối = luận bằng kiến thức CŨ → miss
    # ⇒ lần hỏi sau luận lại với kiến thức mới. KHÔNG để lỗi version phá cache chính.
    try:
        from engine.system_meta import knowledge_version_updated_at
        cutoff = max(cutoff, knowledge_version_updated_at())
    except Exception:
        pass
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("""SELECT id, result_json FROM user_castings
                    WHERE user_id=:u AND method=:m AND question=:q AND created_at>=:c
                    ORDER BY id DESC LIMIT 1"""),
            {"u": uid, "m": method, "q": question[:500], "c": cutoff},
        ).fetchone()
    if not row:
        return None, None
    rj = row[1]
    data = rj if isinstance(rj, (dict, list)) else (_j.loads(rj) if rj else {})
    return row[0], data


def _gate(uid: int, free_key: str, free_limit: int) -> dict:
    """Quyết quyền + THU PHÍ: 'paid' (gói VIP) → 'free' (còn lượt free/ngày) →
    'xu' (hết free → tiêu xu từ ví TRUNG TÂM) → 'denied' (hết free + không đủ xu).

    Free tier dùng ratelimit (Redis đa-worker / in-memory dev). 'paid' KHÔNG trừ lượt
    gói ở đây (consume_use sau khi serve). 'xu' đã TRỪ xu (atomic) ngay tại đây →
    caller phải HOÀN (xu_wallet.grant) nếu sau đó vượt ngân sách / LLM lỗi.

    Trả {tier, reason?, xu_cost?, xu_balance?, need?, have?}."""
    if subs.check_access(uid, FEATURE)["allowed"]:
        return {"tier": "paid"}
    if ratelimit.allow(f"{free_key}:{uid}", free_limit, _DAY):
        return {"tier": "free"}
    # hết lượt free → tiêu xu (ví trung tâm)
    kind = _XU_KIND.get(free_key, "quick")
    cost = xu_wallet.XU_COST[kind]
    r = xu_wallet.spend(uid, cost, f"hermes_{kind}")
    if r["ok"]:
        return {"tier": "xu", "xu_cost": cost, "xu_balance": r["balance"]}
    return {"tier": "denied", "reason": "insufficient_xu",
            "xu_cost": cost, "need": r["need"], "have": r["have"]}

# tag sage → thư mục profile (đồng bộ engine/ai/kanban_council.SAGES_BY_TAG)
SAGE_PROFILE = {
    "mai_hoa": "mai-hoa-sage", "luc_hao": "luc-hao-sage", "lien_hoa": "lien-hoa-sage",
    "tu_vi": "tu-vi-sage", "bat_tu": "bat-tu-sage", "ha_lac": "ha-lac-sage",
    "than_so": "than-so-sage", "western": "chiem-tinh-sage",
}


# agent_id council (ALL_PROMPT_IDS) → thư mục profile chứa SOUL sâu
_SOUL_SYNC = {
    "tu_vi": "tu-vi-sage", "bat_tu": "bat-tu-sage", "mai_hoa": "mai-hoa-sage",
    "luc_hao": "luc-hao-sage", "ha_lac": "ha-lac-sage", "lien_hoa": "lien-hoa-sage",
    "western": "chiem-tinh-sage", "than_so": "than-so-sage", "orchestrator": "yi-orchestrator",
}
_PROFILES_DIR = Path(__file__).resolve().parent.parent / "data" / "hermes_yi" / "profiles"


def sync_souls_from_profiles() -> dict:
    """Bơm SOUL.md sâu (profiles/*/SOUL.md — nguồn chân lý, đã track) vào
    prompt_overrides → council (qua get_prompt) dùng đúng SOUL chuyên sâu thay persona
    mỏng. Idempotent → gọi lúc khởi động worker. Trả {agent_id: số ký tự đã sync}."""
    from engine.ai import prompt_store
    synced: dict[str, int] = {}
    for agent_id, d in _SOUL_SYNC.items():
        f = _PROFILES_DIR / d / "SOUL.md"
        if f.exists():
            content = f.read_text(encoding="utf-8").strip()
            if content:
                prompt_store.set_prompt(agent_id, content)
                synced[agent_id] = len(content)
    return synced


def _build_chart_data(person: dict) -> dict:
    """Cast facts thật từ giờ sinh (engine — sage chỉ LUẬN, không tự tính). Resilient:
    cast lỗi → vẫn trả phần birth tối thiểu (council/mock vẫn chạy)."""
    birth = person.get("birth_datetime_local")
    gender = person.get("gender") or "nam"
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    chart: dict = {"birth_datetime_local": birth, "gender": gender, "timezone": tz}
    try:
        from engine.bat_tu.cast import cast_bat_tu
        chart["bat_tu"] = cast_bat_tu(birth_datetime_local=birth, timezone=tz, gender=gender)
    except Exception:
        pass
    try:
        # FIX 2026-06-19: trước đây gọi cast_la_so(birth_datetime_local=...) SAI signature
        # → tu_vi luôn raise âm thầm → sage luận thiếu lá số. Dùng helper convert đúng.
        from engine.tu_vi.from_birth import cast_la_so_from_birth
        chart["tu_vi"] = cast_la_so_from_birth(birth_datetime_local=birth, timezone=tz, gender=gender)
    except Exception:
        pass
    try:
        # Chiếu Đởm Kinh (Bắc phái / 18 Phi Tinh) — cho sage chieu_dom đọc nội tâm.
        from engine.tu_vi.from_birth import cast_chieu_dom_from_birth
        chart["chieu_dom"] = cast_chieu_dom_from_birth(birth_datetime_local=birth, timezone=tz, gender=gender)
    except Exception:
        pass
    return chart


def build_user_context(uid: int, person: Optional[dict] = None, query_hint: str = "") -> str:
    """Bối cảnh RIÊNG của user cho sage — 'Hermes biết rõ từng người'. MỌI user đều có
    (founder chỉ là một user, KHÔNG đặc cách). Lấy từ DB cô lập theo user_id (RLS).

    PSEUDONYMIZE (PDPL): KHÔNG đưa tên/uid/sđt/email vào — chỉ giờ sinh (chart cần) +
    ký ức (facts/summaries do user tự chia sẻ qua chat). resilient: lỗi → context rỗng."""
    parts: list[str] = []
    if person and person.get("birth_datetime_local"):
        parts.append(f"- Giờ sinh: {person['birth_datetime_local']} · giới tính: "
                     f"{person.get('gender', '?')}")
    try:
        from engine.yi_hermes import memory
        mem = memory.build_memory_context(str(uid), query_hint=query_hint)
        if mem:
            parts.append(mem)
    except Exception:
        pass
    return "Bối cảnh người hỏi (ẩn danh):\n" + "\n".join(parts) if parts else ""


def _real_consult(question: str, person: dict, uid: int,
                  explicit_agents: Optional[list] = None) -> dict:
    """Bọc council in-process sẵn có (sages dùng SOUL sâu qua prompt_overrides).
    explicit_agents (tùy chọn) = danh sách tag sage user CHỌN — None thì Trọng tài tự định tuyến."""
    from engine.ai.council import consult_council
    chart = _build_chart_data(person)
    ctx = build_user_context(uid, person, query_hint=question)
    if ctx:
        chart["user_context"] = ctx       # sage thấy bối cảnh riêng user (đã pseudonymize)
    # LUẬN SÂU TỐI ĐA (Anh chốt 2026-06-24): council chạy ngầm async → KHÔNG tiếc thời gian,
    # cần CHI TIẾT nhất có thể. Bật đủ 3 vòng Socratic (phản biện + bảo vệ) → tổng hợp sâu.
    res = consult_council(question=question, chart_data=chart, persist=False,
                          explicit_agents=explicit_agents, skip_challenge=False)
    pu = res.get("providers_used") or {}     # dict {agent: provider} | đôi khi list
    if isinstance(pu, dict):
        provider = pu.get("orchestrator") or next(iter(pu.values()), "deepseek")
    else:
        provider = (list(pu) or ["deepseek"])[0]
    return {
        "synthesis": res.get("final_synthesis") or "",
        "agents": res.get("agents_consulted") or [],
        "provider": provider,
        "cost_usd": float(res.get("cost_usd") or 0),
        "raw": res,
    }


def precheck(firebase_uid: str, question: str, person_key: str = "self") -> dict:
    """Kiểm nhanh ở endpoint TRƯỚC khi enqueue (phản hồi tức thì, không tốn worker).
    - scope: out_of_scope/needs_focus → trả reply ngay (KHÔNG enqueue, KHÔNG tốn LLM).
    - 404 chưa sync · 422 thiếu giờ sinh · 403 không có quyền (gói)."""
    sv = guard.classify_scope(question)
    if sv.verdict != "in_scope":
        return {"ok": False, "scope": sv.verdict, "reply": sv.reply, "reason": sv.reason}
    uid, person = _resolve(firebase_uid, person_key)
    if uid is None:
        return {"ok": False, "code": 404, "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"ok": False, "code": 422, "reason": "missing_birth"}
    access = subs.check_access(uid, FEATURE)
    if not access["allowed"]:
        # không có gói → còn lượt FREE/ngày thì cho qua (peek, KHÔNG trừ; worker mới trừ)
        if ratelimit.remaining(f"council_free:{uid}", FREE_DAILY_COUNCIL, _DAY) <= 0:
            return {"ok": False, "code": 403, "reason": "no_subscription_and_free_exhausted"}
    return {"ok": True, "user_id": uid}


def run_council(firebase_uid: str, question: str, person_key: str = "self", *,
                user_id: Optional[int] = None, explicit_agents: Optional[list] = None,
                consult: Optional[Callable[[str, dict, int], dict]] = None) -> dict:
    """Chạy 1 lượt Hội Đồng. KHÔNG idempotent → task gọi phải at-most-once.
    Web: truyền user_id (đã đăng nhập). AppChat service: truyền firebase_uid."""
    # 0) Cổng RẺ: rào phạm vi Socratic (chưa tốn gì)
    sv = guard.classify_scope(question)
    if sv.verdict != "in_scope":
        return {"status": sv.verdict, "reply": sv.reply, "reason": sv.reason}

    consult = consult or _real_consult
    if explicit_agents and consult is _real_consult:   # user CHỌN sage → truyền qua (giữ chữ ký 3-arg cho stub test)
        _ea = explicit_agents
        consult = lambda q, p, u: _real_consult(q, p, u, explicit_agents=_ea)
    uid, person = _resolve_entry(firebase_uid, user_id, person_key)
    if uid is None:
        return {"status": "error", "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"status": "error", "reason": "missing_birth"}

    # "Một việc một lần" (Iron #4): cùng câu trong ngày → trả lại cũ, KHÔNG tốn LLM/tiền
    cid_c, cached = _cached(uid, "hermes_council", question)
    if cached:
        return {"status": "done", "cached": True, "casting_id": cid_c,
                "synthesis": cached.get("synthesis"), "agents": cached.get("agents"),
                "voices": cached.get("voices") or [],
                "paradigm_ok": cached.get("paradigm_ok", True)}

    g = _gate(uid, "council_free", FREE_DAILY_COUNCIL)
    tier = g["tier"]
    if tier == "denied":
        return {"status": "denied", "reason": g.get("reason"),
                "xu_cost": g.get("xu_cost"), "have": g.get("have")}

    def _refund_xu():
        # 'xu' đã trừ ở _gate → hoàn lại nếu không serve được (budget/LLM lỗi)
        if tier == "xu":
            xu_wallet.grant(uid, g["xu_cost"], "refund_hermes_council")

    # reserve ngân sách atomic (P0-5) — vượt cap → từ chối, không gọi LLM
    est = float(subs.FEATURE_CATALOG.get(FEATURE, {}).get("cost_estimate_usd", 0.08))
    if not llm_spend.try_charge(cost_usd=est, feature=FEATURE, model="reserve",
                                user_id=str(uid)):
        _refund_xu()
        return {"status": "budget_exceeded"}

    def _refund():
        llm_spend.record_spend(provider="reserve", cost_usd=-est, feature=FEATURE,
                               model="refund", user_id=str(uid))
        _refund_xu()

    try:
        result = consult(question, person, uid)
        if not isinstance(result, dict) or not result.get("synthesis"):
            _refund()
            return {"status": "error", "reason": "council_failed"}

        # post-filter paradigm: synthesis KHÔNG được mang giọng tiên tri
        violations = guard.paradigm_violations(result.get("synthesis", ""))
        paradigm_ok = not violations

        av = algo_version("tu_vi")
        _raw = result.get("raw") if isinstance(result.get("raw"), dict) else {}
        voices = [{"agent_id": v.get("agent_id"), "name": v.get("agent_name_vi"),
                   "content": v.get("content")}
                  for v in (_raw.get("round_1_outputs") or [])
                  if isinstance(v, dict) and v.get("content") and not v.get("error")]
        payload = {"synthesis": result.get("synthesis"), "agents": result.get("agents"),
                   "voices": voices, "paradigm_ok": paradigm_ok, "violations": violations}
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
        # gói → trừ lượt gói; free → đã đếm ở _gate (ratelimit), không trừ gói
        usage = subs.consume_use(uid, FEATURE) if tier == "paid" else {"ok": False}
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
        "status": "done", "casting_id": cid, "algo_version": av, "tier": tier,
        "agents": result.get("agents"), "paradigm_ok": paradigm_ok,
        "synthesis": result.get("synthesis"), "voices": voices,
        "remaining_uses": usage.get("remaining_uses") if usage.get("ok") else None,
        "free_remaining": (ratelimit.remaining(f"council_free:{uid}", FREE_DAILY_COUNCIL, _DAY)
                           if tier == "free" else None),
        "xu_cost": g.get("xu_cost") if tier == "xu" else None,
        "xu_balance": g.get("xu_balance") if tier == "xu" else None,
    }


# ─── Đường TRẢ LỜI NHANH 1-sage (everyday, rẻ — bổ trợ council premium) ───────

def _real_quick(question: str, person: dict, uid: int) -> dict:
    """1 sage liên quan nhất trả lời (1 lần gọi LLM) — dùng SOUL sâu + chart facts +
    bối cảnh user (pseudonymized). Rẻ hơn council nhiều."""
    from engine.ai.agents import run_agent
    from engine.ai.council import _get_agent_provider
    from engine.ai.kanban_council import select_sages
    sage = (select_sages(question) or ["tu_vi"])[0]
    chart = _build_chart_data(person)
    ctx = build_user_context(uid, person, query_hint=question)
    if ctx:
        chart["user_context"] = ctx
    provider, model = _get_agent_provider(sage)
    resp = run_agent(agent_id=sage, provider=provider, model=model,
                     question=question, chart_data=chart, round_label="quick", challenges=None)
    toks = {"prompt": getattr(resp, "prompt_tokens", 0), "completion": getattr(resp, "completion_tokens", 0)}
    return {"answer": resp.content or "", "sage": sage,
            "provider": getattr(resp, "provider", "deepseek"), "cost_usd": 0.0, "tokens": toks}


def precheck_quick(firebase_uid: str, question: str, person_key: str = "self") -> dict:
    """Như precheck nhưng cho đường nhanh (free cap riêng quick_free)."""
    sv = guard.classify_scope(question)
    if sv.verdict != "in_scope":
        return {"ok": False, "scope": sv.verdict, "reply": sv.reply, "reason": sv.reason}
    uid, person = _resolve(firebase_uid, person_key)
    if uid is None:
        return {"ok": False, "code": 404, "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"ok": False, "code": 422, "reason": "missing_birth"}
    if not subs.check_access(uid, FEATURE)["allowed"]:
        if ratelimit.remaining(f"quick_free:{uid}", FREE_DAILY_QUICK, _DAY) <= 0:
            return {"ok": False, "code": 403, "reason": "no_subscription_and_free_exhausted"}
    return {"ok": True, "user_id": uid}


def run_quick(firebase_uid: str, question: str, person_key: str = "self", *,
              user_id: Optional[int] = None,
              answer: Optional[Callable[[str, dict, int], dict]] = None) -> dict:
    """1 lượt trả lời nhanh 1-sage. KHÔNG idempotent → task at-most-once.
    Web: truyền user_id. AppChat service: truyền firebase_uid."""
    sv = guard.classify_scope(question)
    if sv.verdict != "in_scope":
        return {"status": sv.verdict, "reply": sv.reply, "reason": sv.reason}

    answer = answer or _real_quick
    uid, person = _resolve_entry(firebase_uid, user_id, person_key)
    if uid is None:
        return {"status": "error", "reason": "not_synced"}
    if not person or not person.get("birth_datetime_local"):
        return {"status": "error", "reason": "missing_birth"}

    cid_c, cached = _cached(uid, "hermes_quick", question)   # "một việc một lần" (Iron #4)
    if cached:
        return {"status": "done", "cached": True, "casting_id": cid_c,
                "sage": cached.get("sage"), "answer": cached.get("answer"),
                "paradigm_ok": cached.get("paradigm_ok", True)}

    g = _gate(uid, "quick_free", FREE_DAILY_QUICK)
    tier = g["tier"]
    if tier == "denied":
        return {"status": "denied", "reason": g.get("reason"),
                "xu_cost": g.get("xu_cost"), "have": g.get("have")}

    def _refund_xu():
        if tier == "xu":
            xu_wallet.grant(uid, g["xu_cost"], "refund_hermes_quick")

    est = QUICK_EST_USD
    if not llm_spend.try_charge(cost_usd=est, feature="hermes_quick", model="reserve",
                                user_id=str(uid)):
        _refund_xu()
        return {"status": "budget_exceeded"}

    def _refund():
        llm_spend.record_spend(provider="reserve", cost_usd=-est, feature="hermes_quick",
                               model="refund", user_id=str(uid))
        _refund_xu()

    try:
        result = answer(question, person, uid)
        if not isinstance(result, dict) or not result.get("answer"):
            _refund()
            return {"status": "error", "reason": "answer_failed"}

        violations = guard.paradigm_violations(result.get("answer", ""))
        av = algo_version("tu_vi")
        payload = {"answer": result.get("answer"), "sage": result.get("sage"),
                   "paradigm_ok": not violations, "violations": violations}
        res_expr = "CAST(:res AS JSONB)" if is_postgres() else ":res"
        with session_scope(service=True) as conn:
            cid = conn.execute(
                text(f"""INSERT INTO user_castings
                        (user_id, method, subject_person_key, question, result_json,
                         verdict, tags, note, algo_version, created_at)
                        VALUES (:uid,'hermes_quick',:pk,:q,{res_expr},:vd,'quick',NULL,:av,:now)
                        RETURNING id"""),
                {"uid": uid, "pk": person_key, "q": question[:500],
                 "res": json.dumps(payload, ensure_ascii=False),
                 "vd": "paradigm_flag" if violations else None,
                 "av": av, "now": int(time.time())},
            ).scalar()
        usage = subs.consume_use(uid, FEATURE) if tier == "paid" else {"ok": False}
    except Exception:
        _refund()
        raise

    # H6 (#39) — vòng ký ức "càng dùng càng hiểu": chưng cất summary phiên này để
    # build_memory_context phiên sau có ngữ cảnh. Lightweight (KHÔNG thêm LLM call →
    # giữ quick tier rẻ); fact-distillation sâu (LLM) để dành tier deep (#38).
    # Lỗi memory KHÔNG được làm hỏng câu trả lời.
    try:
        from engine.yi_hermes import memory
        ans = (result.get("answer") or "")
        memory.add_summary(
            user_id=str(uid),
            summary=f"[Hỏi nhanh] {question[:160]} → {ans[:240]}",
            session_id=cid,
        )
    except Exception:
        pass

    real_cost = float(result.get("cost_usd") or 0)
    if real_cost > 0:
        llm_spend.record_spend(provider=result.get("provider", "deepseek"),
                               cost_usd=real_cost - est, feature="hermes_quick",
                               user_id=str(uid))
    return {
        "status": "done", "casting_id": cid, "tier": tier, "sage": result.get("sage"),
        "paradigm_ok": not violations, "answer": result.get("answer"),
        "free_remaining": (ratelimit.remaining(f"quick_free:{uid}", FREE_DAILY_QUICK, _DAY)
                           if tier == "free" else None),
        "xu_cost": g.get("xu_cost") if tier == "xu" else None,
        "xu_balance": g.get("xu_balance") if tier == "xu" else None,
    }
