# 06 - Scholarly Specification v1.0 (64-Que Multi-Method)

## 1. Document Status

- `spec_id`: `yi64_scholarly_spec_v1`
- `status`: `draft-ready-for-implementation`
- `scope`: multi-method generation and traceable output for 64 quẻ
- `intended_use`: research-grade standard to be translated into production engine contracts

## 2. Normative References

Core in-repo references:
- `docs/research/64-que/01-problem-model.md`
- `docs/research/64-que/02-method-taxonomy.md`
- `docs/research/64-que/03-normalized-pipeline.md`
- `docs/research/64-que/04-validation-protocol.md`
- `docs/research/64-que/05-conflict-policy.md`

Existing system baseline:
- `docs/rulesets/bac_phai_v1.md`
- `data/seeds/hexagrams_master.json`
- `data/seeds/hexagram_texts_ngotatto.json`

## 3. Core Requirements

## R1. Canonical Data Model
System must implement canonical objects:
- HexagramIdentity
- LineState
- PrimaryHexagram
- TransformRule
- DerivedHexagrams
- ContextVector
- MethodProfileRef
- TraceRecord

## R2. Method Profile Governance
- every active method must have complete profile documentation.
- profile changes must be versioned.
- source provenance is mandatory.

## R3. Normalized Execution Pipeline
System must execute:
1. ParseInput
2. SelectMethodProfile
3. GeneratePrimaryHexagram
4. ResolveMovingLines
5. BuildDerivedHexagrams
6. EmitTraceableResult

## R4. Explainability by Construction
- all results must include method/ruleset identity and trace.
- no silent defaults at branch points.

## R5. Multi-Mode Conflict Handling
System must support:
- SingleSchoolMode
- ParallelSchoolMode
- ConsensusHintMode

and classify conflict types/severity explicitly.

## R6. Validation Compliance
System quality gate must cover:
- deterministic layer
- distribution layer (for stochastic methods)
- cross-method comparative layer

## 4. Canonical Output Specification (Minimum)

Every invocation must return:
- `request_meta`:
  - request id, timestamp, normalized context hash
- `method_meta`:
  - method id, family, school id, ruleset id, version
- `primary_result`:
  - primary hexagram identity
  - line states
  - moving lines
- `derived_result`:
  - transformed hexagram
  - optional derived forms
- `trace_meta`:
  - trace id
  - stage summary
  - warning list
- `confidence_envelope`:
  - rule confidence
  - source confidence
  - input confidence
  - optional interpretation confidence
- `conflict_meta` (if applicable)

## 5. Non-Functional Requirements

## 5.1 Reproducibility
- deterministic methods: exact output replay from same normalized input.
- stochastic methods: exact replay from same input + seed + draw trace.

## 5.2 Auditability
- trace must preserve stage-level evidence.
- provenance links must be machine-readable.

## 5.3 Extensibility
- adding new methods should not require changing canonical output contract.
- method-specific fields should live in namespaced extension objects.

## 6. Blueprint Translation Guidance (for Implementation Team)

Suggested implementation modules:
- `core/yi64/model.py` (canonical dataclasses/schemas)
- `core/yi64/method_registry.py` (method profile resolution)
- `core/yi64/pipeline.py` (stage orchestration)
- `core/yi64/transforms.py` (transform rule engine)
- `core/yi64/conflict.py` (conflict classification and output modes)
- `core/yi64/validation/` (layered validation tools)

Suggested documentation modules:
- `docs/research/64-que/method-profiles/` (one file per method)
- `docs/research/64-que/golden-cases/` (validation fixtures catalog)

## 7. Conformance Levels

## Level L1 (Foundational)
- canonical model implemented
- at least one method fully traceable
- deterministic validation active

## Level L2 (Comparative)
- at least one method in each family
- conflict policy implemented
- cross-method comparative reports enabled

## Level L3 (Research-grade)
- distribution checks in CI
- consensus hint mode enabled
- provenance completeness and confidence scoring enforced

## 8. Acceptance Checklist

A release may be declared compliant with v1.0 only if:
1. all mandatory output fields are present,
2. all active methods have profile + provenance,
3. deterministic and invariant tests pass,
4. stochastic methods pass distribution tolerance,
5. conflict metadata appears whenever multi-method results diverge.

## 9. Versioning and Change Control

Change categories:
- `patch`: wording or non-contract clarifications
- `minor`: backward-compatible contract additions
- `major`: breaking contract/model changes

Any major change requires:
- migration notes
- updated golden cases
- comparative impact report.

## 10. Deliverable Summary

This v1.0 scholarly spec turns the original high-level research plan into an implementation-ready standard while keeping:
- school neutrality,
- traceable reasoning,
- scientific validation discipline,
- long-term method extensibility.
