# 02 - Method Taxonomy and Method Profiles

## 1. Taxonomy Objectives

- Provide a uniform classification for many quẻ-generation methods.
- Keep method differences explicit instead of hidden in code.
- Enable side-by-side comparison and future expansion.

## 2. Method Family Classification

## 2.1 Family A: RandomizedRitual
Methods where randomness is part of ritual mechanics.

Typical examples:
- three-coin method and variants,
- yarrow-stalk style methods and simplifications,
- stochastic ritual variants used in local schools.

Core characteristics:
- probabilistic line generation,
- reproducibility requires seed + draw log,
- validation must include distribution-level tests.

## 2.2 Family B: TimeSpaceMapped
Methods where quẻ is derived from time-space variables.

Typical examples:
- Mai Hoa style mappings (datetime, number extraction),
- cyclical time mappings (can-chi, term cycles),
- school-specific temporal projection systems.

Core characteristics:
- deterministic mapping from normalized time context,
- strong dependence on calendar conventions,
- timezone/calendar conversion is part of correctness.

## 2.3 Family C: SymbolicDerived
Methods where quẻ is derived from symbolic transforms.

Typical examples:
- text-to-number mappings (name, phrase, event code),
- object-count and symbolic encoding methods,
- folk variants based on codified numerology.

Core characteristics:
- deterministic but high variance in transformation rules,
- high ambiguity risk without strict rule declarations,
- source citation is mandatory.

## 3. School Layer

Each method is attached to a school/lineage:
- `school_id`: e.g. `bac_phai`, `mai_hoa_branch_x`, `folk_variant_y`
- `school_scope`: `strict | broad | mixed`
- `school_priority`: local ranking if multiple methods are available

Rule:
- `method_id` is unique globally.
- `method_id` can map to one primary school and optional compatible schools.

## 4. Method Profile Template (One-page Standard)

Each method must be documented with this schema:

1) **Metadata**
- `method_id`
- `method_name`
- `family`
- `school_id`
- `status`: `active | experimental | deprecated`
- `version`

2) **Input Contract**
- required fields
- optional fields
- normalization rules
- invalid input conditions

3) **Algorithm Steps**
- deterministic step sequence
- branch conditions
- moving-line derivation logic
- transformed-hexagram logic

4) **Output Contract**
- mandatory output fields
- optional school-specific fields
- nullability policy

5) **Ambiguity Notes**
- known interpretation/generation ambiguities
- default resolution policy
- override hooks

6) **Source Provenance**
- primary references
- secondary references
- confidence notes on source quality

7) **Validation Hints**
- deterministic tests
- stochastic/distribution tests (if applicable)
- regression fixture requirements

## 5. Comparison Matrix (Required Fields)

All methods are compared on common dimensions:
- family
- school
- deterministic flag
- required context depth
- randomness dependency
- transformed-hexagram policy
- interpretation coupling level
- source confidence tier
- implementation readiness

## 6. Initial Method Inventory (Bootstrapping Set)

This initial set is enough for v1 research baseline:
- `coin_three_standard_v1` (RandomizedRitual)
- `yarrow_simplified_v1` (RandomizedRitual)
- `maihoa_time_number_v1` (TimeSpaceMapped)
- `ganzhi_term_seed_v1` (TimeSpaceMapped; aligns with current MVP spirit)
- `symbolic_text_hash_v1` (SymbolicDerived, research-only)

Note:
- methods can be activated independently of interpretation school.
- activation policy is controlled by conflict policy document.

## 7. Example Method Profile (Compact)

### Method ID
`coin_three_standard_v1`

### Family
`randomized_ritual`

### Input Contract
- required:
  - `draw_count = 6`
  - `coin_faces` (`heads`, `tails`)
  - `line_order = bottom_up`
- optional:
  - `rng_seed` (for replay simulation)
  - `ritual_notes`

### Step Logic
1. For each of 6 lines, toss 3 coins.
2. Map face sum to `LineState` polarity + motion.
3. Build primary hexagram from line polarity.
4. Flip moving lines to derive transformed hexagram.

### Output Contract
- `primary_hexagram`
- `line_states[6]`
- `moving_lines`
- `transformed_hexagram`
- `draw_trace`

### Ambiguity Notes
- coin-face scoring variant may differ by school.
- default uses declared scoring table in ruleset.

### Source Provenance
- source refs required before status can be `active`.

### Validation Hints
- line count always equals 6.
- transformed hexagram is deterministic from line states.
- distribution test needed across large simulation set.

## 8. Governance Rules

1. No method can be `active` without a complete profile.
2. No profile can omit source provenance.
3. Any changed algorithm step requires version bump.
4. Backward compatibility must be declared at output contract level.
5. Deprecated methods remain runnable for replay if historical traces depend on them.
