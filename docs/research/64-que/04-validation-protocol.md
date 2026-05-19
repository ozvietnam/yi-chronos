# 04 - Validation Protocol for Multi-Method 64-Que

## 1. Validation Goals

- Prove correctness at method level.
- Prove statistical integrity for stochastic methods.
- Quantify expected and unexpected divergence across methods/schools.
- Keep validation reproducible and auditable.

## 2. Three-Layer Validation Stack

## 2.1 Layer A: DeterministicTests
Applicable to deterministic methods or deterministic stages.

Assertions:
1. Same normalized input => same output.
2. Same input => same trace decisions.
3. Transform rule invariants always hold.

Test set:
- fixed datetime/timezone cases
- fixed symbolic input cases
- edge boundary cases (calendar boundaries, timezone offsets)

Pass criteria:
- zero mismatches on expected deterministic snapshots.

## 2.2 Layer B: DistributionTests
Applicable to stochastic methods (`RandomizedRitual` family).

Assertions:
1. Line-state frequencies converge to declared theoretical distribution.
2. Moving-line count distribution is stable within tolerance.
3. Result does not show hidden bias introduced by implementation.

Test design:
- run large simulations (N sufficiently high)
- capture:
  - per-line yin/yang rates,
  - moving/static rates,
  - hexagram frequency profile.

Statistical checks:
- confidence intervals
- goodness-of-fit style checks against declared reference distribution

Pass criteria:
- all monitored metrics remain inside tolerance thresholds.

## 2.3 Layer C: CrossMethodComparativeTests
Applicable when many methods are supported.

Assertions:
1. Same `ContextVector` can produce different outcomes by design.
2. Differences must be explainable by method rules, not implementation bugs.
3. Parallel-mode output is complete and internally consistent.

Test design:
- define curated shared scenarios (`golden comparative cases`)
- run all active methods
- evaluate:
  - output completeness,
  - trace explainability,
  - conflict classification correctness.

Pass criteria:
- no unexplained divergence,
- conflict labels match policy.

## 3. Golden Case Strategy

## 3.1 Golden Deterministic Cases
- fixed input fixtures per deterministic method
- expected normalized outputs
- expected trace fragments

## 3.2 Golden Comparative Cases
- scenario packs used across multiple methods:
  - same question context,
  - same datetime/location settings,
  - same interpretation mode constraints.

Each case stores:
- case id
- canonical input
- participating methods
- expected comparison notes (not forced same output)

## 3.3 Source Provenance Checks
For each output text link:
- source reference must exist,
- source id must resolve to registered corpus,
- missing source turns confidence axis down and emits warning.

## 4. Invariant Test List

Mandatory invariants across all methods:
1. line count = 6.
2. line positions = 1..6.
3. moving lines derived from line states exactly.
4. transformed hexagram matches declared transform rule.
5. method profile metadata always attached.
6. trace record exists and is non-empty.

## 5. Regression Policy

Triggers for full regression:
- method profile change
- transform rule change
- calendar conversion logic change
- source corpus version change (if text mapping is involved)

Regression levels:
- `quick`: deterministic smoke + invariant checks
- `standard`: quick + selected distribution checks
- `full`: all layers + comparative matrix generation

## 6. Metrics and Quality Gates

Core metrics:
- deterministic pass rate
- invariant pass rate
- stochastic distribution drift index
- comparative explainability coverage
- provenance completeness rate

Release gates:
- no critical invariant failure
- deterministic pass rate = 100% for deterministic paths
- explainability coverage above declared minimum

## 7. Reporting Contract

Validation report must include:
- `run_id`
- ruleset/method versions
- dataset version references
- summary by layer
- failed cases with trace references
- recommended action (`block`, `warn`, `accept`)

## 8. CI Integration Guidance

Suggested structure:
- `tests/validation/deterministic/`
- `tests/validation/distribution/`
- `tests/validation/comparative/`
- `tests/fixtures/golden_cases/`

Execution policy:
- quick validation on pull requests
- full validation on release candidates

## 9. Anti-Pattern List

Do not:
- treat cross-method divergence as immediate bug,
- skip trace checks when outputs look plausible,
- use distribution tests with too-small sample size,
- merge method changes without updating golden cases.
