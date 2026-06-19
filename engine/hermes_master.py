"""Hermes Chúa — tầng master rà soát công việc + giao Hermes con TỰ ĐÁNH GIÁ sản phẩm.

Anh (founder) chốt 2026-06-20: đã có từng Hermes phụ trách từng mảng → kích hoạt Hermes Chúa
để (1) RÀ SOÁT công việc toàn hệ (roster + chi phí + cờ paradigm) và (2) GIAO mỗi sage con
TỰ ĐÁNH GIÁ sản phẩm của chính nó (tạo luận mẫu + tự chấm tuân-paradigm + chỉ lỗi + đề xuất).

Nguyên tắc: Hermes Chúa KHÔNG phán thay sage — nó GIAO VIỆC + TỔNG HỢP. Mỗi sage tự soi mình
theo Iron Rule #4/#6/#8 (đọc đồng dạng, mệnh là động từ, KHÔNG tiên tri). Owner-only, có audit.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# Câu hỏi mẫu mặc định để sage tạo "sản phẩm" rồi tự chấm (đồng dạng, không sự kiện cụ thể).
_DEFAULT_SAMPLE_Q = "Khoảnh khắc này đang phản chiếu điều gì trong cấu trúc tâm-thiên-thân của người hỏi?"

_PASS_SCORE = 7   # paradigm_score < 7 hoặc có issues → Hermes Chúa flag để xem lại


def _parse_obj(content: str) -> dict:
    if not content:
        return {}
    s, e = content.find("{"), content.rfind("}")
    if s == -1 or e == -1 or e < s:
        return {}
    try:
        o = json.loads(content[s:e + 1])
        return o if isinstance(o, dict) else {}
    except json.JSONDecodeError:
        return {}


def _self_eval(tag: str, name: str, sample_q: str) -> dict:
    """Giao 1 sage con TỰ ĐÁNH GIÁ: tạo luận mẫu + tự chấm paradigm + lỗi + đề xuất."""
    from engine.ai.prompt_store import get_prompt
    from engine.ai.council import _get_agent_provider

    persona = get_prompt(tag)
    provider, model = _get_agent_provider(tag)
    task = f"""HERMES CHÚA YÊU CẦU TỰ ĐÁNH GIÁ SẢN PHẨM CỦA CHÍNH BẠN.

1. Tạo MỘT ví dụ luận mẫu NGẮN (3-5 câu) cho câu hỏi: "{sample_q}" — đúng chuyên môn + giọng của bạn.
2. Tự CHẤM sản phẩm vừa tạo, trung thực:
   - paradigm_score 0-10: mức tuân Iron Rule (đọc ĐỒNG DẠNG, mệnh là ĐỘNG TỪ, TUYỆT ĐỐI không tiên tri cát/hung).
   - paradigm_ok: true nếu ≥7 và không có câu dự báo sự kiện.
   - issues: mảng lỗi/rủi ro tự thấy (predict-leakage, bịa, lệch nguồn, sáo rỗng) — [] nếu sạch.
   - de_xuat: 1-2 đề xuất cải thiện persona/cách luận của chính bạn.

Trả JSON THUẦN (bắt đầu {{ kết thúc }}, không markdown):
{{"sample": "<luận mẫu>", "paradigm_score": <0-10>, "paradigm_ok": <bool>, "issues": [<...>], "de_xuat": "<...>"}}"""
    try:
        resp = provider.chat(
            messages=[{"role": "system", "content": persona},
                      {"role": "user", "content": task}],
            model=model, temperature=0.3, max_tokens=2000)
    except Exception as e:
        return {"tag": tag, "name": name, "ok": False, "error": f"{type(e).__name__}: {e}"}
    o = _parse_obj(resp.content)
    if not o:
        return {"tag": tag, "name": name, "ok": False, "error": "không parse được tự-đánh-giá"}
    try:
        score = float(o.get("paradigm_score", 0))
    except (ValueError, TypeError):
        score = 0.0
    issues = o.get("issues") or []
    if not isinstance(issues, list):
        issues = [str(issues)]
    return {
        "tag": tag, "name": name, "ok": True,
        "paradigm_score": score,
        "paradigm_ok": bool(o.get("paradigm_ok")) and score >= _PASS_SCORE and not issues,
        "sample": (o.get("sample") or "").strip(),
        "issues": issues,
        "de_xuat": (o.get("de_xuat") or "").strip(),
        "model": getattr(resp, "model", model),
    }


def master_review(*, sample_question: Optional[str] = None,
                   tags: Optional[list[str]] = None, max_workers: int = 4) -> dict:
    """Hermes Chúa rà soát + giao các sage con tự đánh giá (song song).

    tags=None → tất cả sage ĐANG BẬT trong roster (trừ orchestrator/arbiter). Trả:
    {work, evals, flagged, avg_score, n_sages, n_flagged}."""
    from engine.admin_hermes import get_roster, get_metrics, audit
    from engine.ai.prompt_store import AGENT_IDS

    sample_q = (sample_question or "").strip() or _DEFAULT_SAMPLE_Q
    roster = get_roster()
    targets = [r for r in roster
               if r["tag"] in AGENT_IDS and r.get("enabled", True)
               and (tags is None or r["tag"] in tags)]

    evals: list[dict] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_self_eval, r["tag"], r["name_vi"], sample_q): r["tag"] for r in targets}
        for f in as_completed(futs):
            try:
                evals.append(f.result())
            except Exception as e:
                evals.append({"tag": futs[f], "ok": False, "error": str(e)[:120]})

    evals.sort(key=lambda x: x.get("tag", ""))
    ok_evals = [e for e in evals if e.get("ok")]
    flagged = [e for e in evals if (not e.get("ok")) or (not e.get("paradigm_ok"))]
    scores = [e["paradigm_score"] for e in ok_evals if "paradigm_score" in e]
    avg = round(sum(scores) / len(scores), 1) if scores else None

    out = {
        "work": get_metrics(),          # rà soát công việc: chi phí + cờ paradigm + lượt + chờ duyệt
        "sample_question": sample_q,
        "n_sages": len(targets),
        "evals": evals,
        "flagged": [e["tag"] for e in flagged],
        "n_flagged": len(flagged),
        "avg_score": avg,
    }
    try:
        audit("master_review", details={"n_sages": len(targets), "n_flagged": len(flagged),
                                         "avg_score": avg, "flagged": out["flagged"]})
    except Exception:
        pass
    return out
