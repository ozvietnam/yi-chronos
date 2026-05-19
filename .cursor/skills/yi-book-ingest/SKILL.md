---
name: yi-book-ingest
description: Ingest Kinh Dich source books into normalized seeds with provenance and coverage audit. Use when the user asks to read books, extract 64-hexagram data, enrich interpretations, or update source coverage.
disable-model-invocation: true
---
# Yi Book Ingest

## Goal

Convert book content into structured seeds safely and repeatably:

- `data/seeds/hexagram_texts_ngotatto.json`
- `data/seeds/hexagram_insights_tam_thien.json`
- related coverage artifacts under `data/cache/`.

## Workflow

Use this checklist:

```text
Book ingest checklist
- [ ] Confirm source file path and source_ref text
- [ ] Extract text safely (prefer deterministic CLI/tools first)
- [ ] Map to 64 quẻ schema with king_wen_index
- [ ] Preserve provenance (source_book, source_ref)
- [ ] Run coverage audit (count, missing)
- [ ] Run tests
- [ ] Write session handoff note
```

## Data Rules

- Never write free-form output into seeds.
- Every record must include `name_vi` and stable source fields.
- Keep deterministic IDs (`king_wen_index`) as the join key.
- If ambiguity exists, keep best candidate + mark for later review in handoff.

## Validation Commands

```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/test_hexagram_texts.py -q
```

```bash
curl -s http://127.0.0.1:8000/api/hexagram-auto-audit
```

## Output Contract

When ingest is done, report:

1. Updated files.
2. Coverage delta (before -> after).
3. Remaining missing/conflict list.
4. Exact source attribution used.
