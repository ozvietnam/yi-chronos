# Release note - Timing Ruleset v2

Date: 2026-05-08
Scope: D05 -> D10 consolidation

## Included changes

- D05: Affliction-aware timing priorities
  - double break => recovery-by-harmony priority up
- D06: Hidden line candidates (v1)
- D07: Funnel matrix v2 tracing (`trigger_type`, `primary_rule_id`, `funnel_applied`)
- D08: Candidate projected local dates
- D09: Feedback pattern matching framework (draft rules)
- D10: Release packaging checklist completed

## Regression status

- `tests/test_luc_hao_timing.py`
- `tests/test_luc_hao_void_timing.py`
- `tests/test_luc_hao_advanced_timing.py`
- `tests/test_api.py`

All passing at release time.
