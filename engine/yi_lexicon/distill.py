"""Distill knowledge from kanban council results into YI-Lexicon.

After each council session completes, this module:
1. Reads the arbiter synthesis + sage outputs
2. Sends to LLM with the extraction prompt
3. YOLO-merges new concepts/mappings into the lexicon (auto-accept)
4. Queues items in `distill_queue` for anh review

Triggered by:
- API endpoint after council marks done
- Manual via `distill_from_council(root_id)`
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

from .ingestion import _EXTRACTION_SYSTEM_PROMPT, _merge_extracted
from .store import bootstrap_db


@dataclass
class DistillResult:
    root_id: str
    concepts_added: int
    mappings_added: int
    contextual_added: int
    errors: list[str]


def distill_from_council(
    root_id: str,
    *,
    llm_provider=None,
    model: str = "deepseek-v4-pro",
) -> DistillResult:
    """Read a completed kanban council session + distill knowledge into lexicon.

    Disables auto_distill in the snapshot call to avoid recursive trigger.
    """
    bootstrap_db()
    from engine.ai.kanban_council import load_session, session_snapshot

    session = load_session(root_id)
    if not session:
        return DistillResult(root_id=root_id, concepts_added=0, mappings_added=0,
                             contextual_added=0, errors=["session not found"])

    snap = session_snapshot(session, harvest=False, auto_distill=False)
    if not snap["progress"]["complete"]:
        return DistillResult(root_id=root_id, concepts_added=0, mappings_added=0,
                             contextual_added=0, errors=["council not complete"])

    # Collect all text outputs (sage + arbiter)
    chunks: list[str] = []
    for tag, sage in snap["sages"].items():
        if sage.get("result"):
            chunks.append(f"## Sage {tag}\n\n{sage['result']}")
    arb_result = snap["arbiter"].get("result")
    if arb_result:
        chunks.append(f"## Arbiter synthesis\n\n{arb_result}")

    if not chunks:
        return DistillResult(root_id=root_id, concepts_added=0, mappings_added=0,
                             contextual_added=0, errors=["no sage outputs"])

    if llm_provider is None:
        try:
            from engine.ai.registry import get_registry
            llm_provider = get_registry().first_configured(
                preferred_order=["deepseek", "zai", "anthropic"]
            ) or None
        except Exception:
            pass
    if llm_provider is None:
        return DistillResult(root_id=root_id, concepts_added=0, mappings_added=0,
                             contextual_added=0, errors=["no LLM provider"])

    source_tag = f"council:{root_id}"
    total = {"concepts": 0, "mappings": 0, "contextual": 0}
    errors: list[str] = []
    combined = "\n\n---\n\n".join(chunks)

    try:
        messages = [
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"## Output từ council {root_id}:\n\n{combined}\n\n"
                "Trích xuất concepts + mappings mới phát hiện được từ phân tích của các sage. "
                "Bỏ qua kết luận về user cụ thể — chỉ giữ ánh xạ symbolic chung."
            )},
        ]
        response = llm_provider.chat(messages=messages, model=model, max_tokens=4000)
        content = response.content if hasattr(response, "content") else str(response)
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            extracted = json.loads(json_match.group(0))
            merged = _merge_extracted(extracted, source_tag=source_tag)
            total.update(merged)
        else:
            errors.append("no JSON in LLM output")
    except Exception as e:
        errors.append(str(e))

    return DistillResult(
        root_id=root_id,
        concepts_added=total["concepts"],
        mappings_added=total["mappings"],
        contextual_added=total["contextual"],
        errors=errors,
    )
