"""Dịch điều văn Thiết Bản (cổ văn Hán) → Việt + lời bình, qua sage `thiet_ban`.

Điều văn CỐ ĐỊNH (tra theo số mệnh) → dịch 1 lần, CACHE theo số điều (`thiet_ban_luan`),
lần sau instant + không tốn LLM. Persona Hermes-quản-lý (`prompt_store get_prompt('thiet_ban')`),
provider qua council `_get_agent_provider` (DeepSeek-Reasoner ưu tiên cho cổ văn). Dual-driver.

Paradigm Iron #6/#8: dịch trung thực + lời bình đọc-đồng-dạng (mệnh là động từ), KHÔNG predict.
"""
from __future__ import annotations

import json
import time
from typing import Optional

from sqlalchemy import bindparam, text

from engine.db import session_scope

_DDL = """
CREATE TABLE IF NOT EXISTS thiet_ban_luan (
    so          BIGINT PRIMARY KEY,
    dich        TEXT,
    binh        TEXT,
    model       TEXT,
    created_at  BIGINT
)
"""
_CHUNK = 8   # số điều văn mỗi lần gọi LLM (tránh output truncate)


def _ensure(conn) -> None:
    conn.execute(text(_DDL))


def _cached(sos: list[int]) -> dict[int, dict]:
    if not sos:
        return {}
    with session_scope(service=True) as conn:
        _ensure(conn)
        q = text("SELECT so, dich, binh FROM thiet_ban_luan WHERE so IN :sos").bindparams(
            bindparam("sos", expanding=True))
        rows = conn.execute(q, {"sos": sos}).fetchall()
    return {int(r[0]): {"dich": r[1], "binh": r[2], "cached": True} for r in rows}


def _save(fresh: dict[int, dict]) -> None:
    if not fresh:
        return
    now = int(time.time())
    with session_scope(service=True) as conn:
        _ensure(conn)
        for so, v in fresh.items():
            conn.execute(text("DELETE FROM thiet_ban_luan WHERE so=:s"), {"s": so})
            conn.execute(text(
                "INSERT INTO thiet_ban_luan (so, dich, binh, model, created_at) "
                "VALUES (:s, :d, :b, :m, :t)"),
                {"s": so, "d": v.get("dich", ""), "b": v.get("binh", ""),
                 "m": v.get("model", ""), "t": now})


def _parse_array(content: str) -> list[dict]:
    """Tách JSON array từ output LLM (chịu được preamble/markdown fence)."""
    if not content:
        return []
    s = content.find("[")
    e = content.rfind("]")
    if s == -1 or e == -1 or e < s:
        return []
    try:
        arr = json.loads(content[s:e + 1])
        return arr if isinstance(arr, list) else []
    except json.JSONDecodeError:
        return []


def _translate_chunk(items: list[dict]) -> dict[int, dict]:
    from engine.ai.prompt_store import get_prompt
    from engine.ai.council import _get_agent_provider

    persona = get_prompt("thiet_ban")
    provider, model = _get_agent_provider("thiet_ban")
    payload = [{"so": it["so"], "zh": it["zh"], "ngu_canh": it.get("ngu_canh", "")} for it in items]
    user_msg = ("Dịch + lời bình các điều văn Thiết Bản sau. Trả JSON array thuần:\n"
                + json.dumps(payload, ensure_ascii=False))
    resp = provider.chat(
        messages=[{"role": "system", "content": persona},
                  {"role": "user", "content": user_msg}],
        model=model, temperature=0.4, max_tokens=4000)
    out: dict[int, dict] = {}
    for o in _parse_array(resp.content):
        try:
            out[int(o["so"])] = {"dich": (o.get("dich") or "").strip(),
                                 "binh": (o.get("binh") or "").strip(),
                                 "model": resp.model, "cached": False}
        except (KeyError, ValueError, TypeError):
            continue
    return out


def luan_dieu_van(items: list[dict], *, force: bool = False) -> dict:
    """items: [{so:int, zh:str, ngu_canh?:str}]. Trả {"luan": {so: {dich, binh, cached}}}.

    Chỉ dịch điều văn có `zh`. Cache theo `so`; cache-miss → gọi sage theo chunk."""
    valid = [it for it in items if it.get("zh") and it.get("so") is not None]
    sos = [int(it["so"]) for it in valid]
    result = {} if force else _cached(sos)
    todo = [it for it in valid if int(it["so"]) not in result]

    fresh_all: dict[int, dict] = {}
    n_fail = 0
    for i in range(0, len(todo), _CHUNK):
        chunk = todo[i:i + _CHUNK]
        try:
            got = _translate_chunk(chunk)
        except Exception:
            got = {}                 # 1 chunk lỗi không chặn chunk khác / phần đã cache
        if got:
            fresh_all.update(got)
        else:
            n_fail += len(chunk)
    if fresh_all:
        _save(fresh_all)
        result.update(fresh_all)
    out = {"luan": {str(k): v for k, v in result.items()},
           "translated": len(fresh_all), "from_cache": len(result) - len(fresh_all)}
    # Surface lỗi: có điều văn cần dịch nhưng KHÔNG dịch được điều nào (provider lỗi/chưa cấu
    # hình) → báo rõ để UI hiện thông báo thay vì im lặng rỗng.
    if n_fail and not fresh_all:
        out["error"] = "Sage dịch thất bại — provider LLM lỗi hoặc chưa cấu hình key. Thử lại sau."
    elif n_fail:
        out["partial_failed"] = n_fail
    return out
