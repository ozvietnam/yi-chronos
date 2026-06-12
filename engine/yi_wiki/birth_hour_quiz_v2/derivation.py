"""Orchestrate full trait derivation: rules + LLM → 22 traits per candidate."""
from __future__ import annotations

from .rules.physical import derive_physical_traits
from .rules.energy import derive_energy_traits
from .rules.personality import (
    derive_yin_yang_ratio, derive_sibling_position_hint,
)
from .rules.tat_ach import derive_tat_ach_traits
from .llm_call import call_trait_llm


def derive_all_traits(candidates: list[dict]) -> dict[str, dict[str, str]]:
    """Derive all 22 traits for each candidate.

    Args:
        candidates: list of {"chi": str, "pillars": full pillars dict,
                             "lunar": {month, day}, "gender": str}
        (lunar/gender optional — thiếu thì domain 5 trả "unknown")

    Returns:
        {chi: {trait_id: value}} — 22 traits per candidate.

    Trait sources:
        Domain 1 (7): rules/physical.py
        Domain 2:
          - introvert_extrovert: rules/personality.py (yin/yang)
          - 4 others: LLM
        Domain 3 (3): rules/energy.py (TCM clock)
        Domain 4:
          - sibling_position_likely: rules/personality.py
          - 3 others: LLM
        Domain 5 (3): rules/tat_ach.py — sao an theo giờ trên lá số Tử Vi
          (đối chiếu bệnh sử giữa các giờ ứng viên — Tử Vi Bôn Ba video 091)
    """
    llm_out = call_trait_llm(candidates)

    out = {}
    for c in candidates:
        chi = c["chi"]
        pillars = c["pillars"]
        traits = {}

        # Domain 1: physical (rules)
        traits.update(derive_physical_traits(pillars))

        # Domain 2: personality
        traits["introvert_extrovert"] = derive_yin_yang_ratio(pillars)
        chi_llm = llm_out.get(chi, {})
        for k in ("decision_style", "leadership_orientation",
                  "emotional_pattern", "communication_style"):
            traits[k] = chi_llm.get(k, "unknown")

        # Domain 3: energy (rules)
        traits.update(derive_energy_traits(pillars))

        # Domain 4: life events
        traits["sibling_position_likely"] = derive_sibling_position_hint(pillars)
        for k in ("career_direction", "marriage_timing_rough", "health_pattern_general"):
            traits[k] = chi_llm.get(k, "unknown")

        # Domain 5: tật ách / bệnh sử (rules — an sao Tử Vi theo giờ)
        traits.update(derive_tat_ach_traits(c))

        out[chi] = traits
    return out
