---
name: yi-memory-handoff
description: Preserve session memory for YI project by writing actionable handoff logs with current status, blockers, and next steps. Use at the end of major work blocks or when the user asks for summary/handoff.
disable-model-invocation: true
---
# Yi Memory Handoff

## Goal

Make the next session executable immediately without re-discovery.

## Handoff File Standard

Create/update a dated file under `docs/`:

- `docs/session-handoff-YYYY-MM-DD.md`

## Required Sections

```text
- What was completed
- Current system status (including key metrics)
- Open tasks and blockers
- Exact next 3 steps (ordered)
- Quick verification commands
- Source/provenance notes if data changed
```

## Rules

- Write concrete file paths and endpoint names.
- Include command snippets that were actually used.
- Keep it short and operational; avoid narrative text.
- Do not include secrets or private keys.

## End-of-Session Quick Template

```markdown
## Completed
- ...

## Current status
- ...

## Next steps
1. ...
2. ...
3. ...

## Verify
```bash
...
```
```
