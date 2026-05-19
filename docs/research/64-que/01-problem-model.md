# 01 - Problem Model for 64-Que Engine

## 1. Goal

Define a school-agnostic canonical model for 64-que generation so that:
- multiple methods can coexist without breaking each other,
- each output can be traced back to concrete rules and sources,
- downstream interpretation logic is separated from generation logic.

## 2. Canonical Objects

### 2.1 HexagramIdentity
- `king_wen_index`: integer in `[1..64]`
- `binary_code`: 6-bit string, bottom line first (e.g. `101010`)
- `name_vi`: canonical Vietnamese name
- `name_han`: optional Han-character name
- `upper_trigram`: canonical trigram code
- `lower_trigram`: canonical trigram code

### 2.2 LineState
Represents one line in a hexagram.
- `line_position`: integer in `[1..6]` (1 = bottom line)
- `polarity`: `yin | yang`
- `motion`: `static | moving`
- `origin_value`: optional raw method value (coin sum, yarrow count, etc.)

### 2.3 PrimaryHexagram
- `hexagram_identity`: `HexagramIdentity`
- `line_states`: array of 6 `LineState`
- `moving_lines`: sorted positions list, derived from `line_states`

### 2.4 TransformRule
Defines how to generate transformed hexagram from moving lines.
- `rule_id`: unique id (e.g. `line_flip_standard`)
- `description`: human-readable logic
- `version`: semantic version
- `deterministic`: boolean

### 2.5 DerivedHexagrams
- `transformed_hexagram`: optional `HexagramIdentity`
- `nuclear_hexagram`: optional `HexagramIdentity`
- `context_hexagrams`: optional list for school-specific derived forms

### 2.6 ContextVector
Standardized invocation context.
- `question_text`: optional user question
- `question_domain`: optional tag (`career`, `health`, etc.)
- `querent_profile`: optional object
- `datetime_local`: ISO datetime
- `timezone`: IANA timezone
- `location_ref`: optional location id
- `calendar_mode`: `solar | lunar | both`
- `school_constraints`: optional list of school ids

### 2.7 MethodProfileRef
Method metadata attached to each result.
- `method_id`: unique id
- `method_family`: `randomized_ritual | time_space_mapped | symbolic_derived`
- `school_id`: school/lineage identifier
- `ruleset_id`: applied ruleset version
- `source_refs`: citations list

### 2.8 TraceRecord
Step-by-step reproducibility evidence.
- `trace_id`: unique id
- `steps`: ordered list of step records
- `inputs_snapshot`: normalized input
- `intermediate_values`: structured map
- `decisions`: rules chosen at branch points
- `warnings`: ambiguity/assumption notes

## 3. Boundary Separation

### 3.1 Generation Layer (must be deterministic given method + input)
- input normalization
- method-specific quẻ generation
- moving-line resolution
- transformed/derived quẻ generation

### 3.2 Interpretation Layer (pluggable by school)
- line-reading policy selection
- textual interpretation mapping
- school-specific synthesis output

### 3.3 Presentation Layer
- API payload formatting
- UI rendering
- multilingual text output

## 4. Canonical Contracts

### 4.1 Input Contract (NormalizedRequest)
- all method invocations must be transformed into the same request shape
- unknown fields are ignored but logged
- missing required fields trigger explicit validation errors

### 4.2 Output Contract (NormalizedResult)
- always return:
  - primary hexagram,
  - moving lines,
  - transformed hexagram (if any),
  - method metadata,
  - trace metadata,
  - confidence envelope

## 5. Confidence Envelope

Each result contains confidence axes (not one flat score):
- `rule_confidence`: how complete and stable the applied rule set is
- `source_confidence`: quality of textual provenance
- `input_confidence`: quality and completeness of input
- `interpretation_confidence`: optional, for interpretation phase only

## 6. Controlled Vocabulary

Canonical terms:
- `que_chu` -> primary hexagram
- `hao_dong` -> moving line
- `que_bien` -> transformed hexagram
- `que_ho` -> nuclear/derived category as configured per school
- `the_dung`, `dung_than` -> interpretation-level concepts (not generation primitives)

## 7. Invariants

1. Exactly 6 lines per hexagram.
2. Line positions are always 1..6 bottom-up.
3. `moving_lines` equals indices where `motion == moving`.
4. `transformed_hexagram` is reproducible from `PrimaryHexagram + TransformRule`.
5. Result is invalid if source/method metadata is missing.

## 8. Minimal JSON Shape (Reference)

```json
{
  "request": {
    "context_vector": {},
    "method_profile_ref": {}
  },
  "result": {
    "primary_hexagram": {},
    "derived_hexagrams": {},
    "trace_record": {},
    "confidence_envelope": {}
  }
}
```

## 9. Mapping to Current Repository

- Existing core hexagram data:
  - `data/seeds/hexagrams_master.json`
  - `data/seeds/hexagram_texts_ngotatto.json`
- Existing ruleset baseline:
  - `docs/rulesets/bac_phai_v1.md`

This document upgrades the model from a single-school MVP orientation to a multi-method canonical foundation.
