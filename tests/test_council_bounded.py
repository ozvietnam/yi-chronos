"""Council KHÔNG treo vì sage chậm — _run_round_parallel có deadline chung + bỏ sage quá hạn."""
import time

from engine.ai import council
from engine.ai.agents import AgentResponse


def test_slow_sage_does_not_hang_round(monkeypatch):
    """1 sage ngủ 10s + deadline 1s → vòng trả sau ~1s (KHÔNG chờ 10s); sage chậm = error timeout."""
    monkeypatch.setattr(council, "SAGE_TIMEOUT_S", 1)

    def run_one(aid, round_label, challenges):
        if aid == "slow":
            time.sleep(10)
        return AgentResponse(agent_id=aid, agent_name_vi=aid, provider="m", model="m", content="ok")

    t = time.time()
    out = council._run_round_parallel(["fast", "slow"], run_one, "1", None)
    dt = time.time() - t

    assert dt < 4, f"phải bounded ~1s, thực {dt:.1f}s"
    by = {r.agent_id: r for r in out}
    assert by["fast"].content == "ok"
    assert by["slow"].error and "timeout" in by["slow"].error


def test_all_fast_sages_complete(monkeypatch):
    monkeypatch.setattr(council, "SAGE_TIMEOUT_S", 5)

    def run_one(aid, round_label, challenges):
        return AgentResponse(agent_id=aid, agent_name_vi=aid, provider="m", model="m", content=f"{aid}-ok")

    out = council._run_round_parallel(["a", "b", "c"], run_one, "1", None)
    assert len(out) == 3 and all(not r.error for r in out)
