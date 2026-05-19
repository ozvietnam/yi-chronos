---
name: yi-code-review
description: Review YI project changes for regression risk, source provenance integrity, and API contract safety. Use when asked to review code, review PRs, or validate release readiness.
disable-model-invocation: true
---
# Yi Code Review

## Review Priorities

Order findings by severity:

1. Runtime/API breakage risk.
2. Wrong hexagram mapping or provenance corruption.
3. Missing tests for changed behavior.
4. Performance or maintainability debt.

## Required Checks

Use this checklist:

```text
Review checklist
- [ ] API response contract unchanged or intentionally versioned
- [ ] source_ref/source_book still accurate after data edits
- [ ] 64-quẻ completeness not regressed
- [ ] tests cover changed modules
- [ ] no secret leakage (.env.local not committed)
```

## Project-Specific Hotspots

- `api/main.py` (endpoint shape and compatibility)
- `core/hexagram.py`, `core/hexagram_texts.py` (identity/provenance logic)
- `data/seeds/*.json` (coverage and source consistency)
- `client/webapp/src/components/*` (UI contract with backend fields)

## Validation Commands

```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests -q
```

```bash
cd client/webapp && npm run build
```

## Output Format

- Critical findings first.
- Then open questions/assumptions.
- Then short change summary.
