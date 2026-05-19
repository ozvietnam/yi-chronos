# Birth Hour Quiz v2 — Design Spec

**Created:** 2026-05-19
**Status:** Design approved, awaiting implementation plan
**Author:** Claude (with Anh's direction)
**Replaces:** None (v1 stays for backward compat)
**Module path:** `engine/yi_wiki/birth_hour_quiz_v2/`

---

## 1. Goal

Upgrade the existing "Trắc nghiệm tìm giờ sinh" feature ([engine/yi_wiki/birth_hour_quiz.py](../../../engine/yi_wiki/birth_hour_quiz.py)) from a naïve fixed-question scoring system to a **bát tự hypothesis comparison** engine.

**Key paradigm shift:**

| v1 (current) | v2 (this spec) |
|---|---|
| KHÔNG yêu cầu ngày sinh | Phải có ngày-tháng-năm sinh (3 trụ đã biết) |
| Chi giờ → trait CỐ ĐỊNH (Mão = "cao thon") | Bát tự đầy đủ × N candidates → traits DERIVED per candidate |
| 8 câu cố định, score chi giờ độc lập | 12-15 câu adaptive, target HIGH-DISCRIMINATION traits |
| Output: top chi giờ + confidence label | Output: top 1-2 candidates + per-candidate reasoning |
| Single round | Multi-round adaptive (1/2/3 rounds depending on initial range) |

**User benefit:** chính xác hơn (full bát tự context vs chi giờ độc lập), narrative reasoning ("nếu sinh giờ X thì... — Anh đã xác nhận điểm Y → khớp"), works for any range size from tight (2 candidates) to unknown (12 candidates).

---

## 2. Architecture overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│  - Ngày-tháng-năm sinh (year + month + day pillars known)       │
│  - Rough hour range: slider 2 đầu (vd 6h ─── 12h)               │
│    + checkbox "không nhớ gì" (default 0-23h = 12 candidates)    │
│  - Gender                                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│   CANDIDATE GENERATOR                                           │
│  Range 6h-12h → 4 candidates: Mão / Thìn / Tỵ / Ngọ             │
│  Each candidate → full bát tự via existing core.calendar +      │
│  engine.bat_tu cast logic                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│   TRAIT DERIVATION LAYER (Hybrid: Rules + LLM)                  │
│  19 traits across 4 domains. Rules deterministic for physical + │
│  energy. LLM (DeepSeek-Reasoner) for personality + life events. │
│  1 LLM call per quiz (batch all candidates).                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│   DIFF ANALYSIS + QUESTION GENERATOR                            │
│  Entropy per trait → pick top K (5-7) high-entropy traits per   │
│  round → generate questions w/ candidate-clustered options.     │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│   USER QUIZ (UI) — multi-round wizard                           │
│  Round 1 → score → if ambiguous → Round 2 → ... → FINAL         │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│   SCORING + OUTPUT                                              │
│   Top 1-2 most likely + reasoning. Option: save to user_persons.│
└─────────────────────────────────────────────────────────────────┘
```

### Multi-round strategy by range size

| Range type | # candidates | Strategy | Total questions |
|---|---|---|---|
| Tight (vd 7-9h) | 2-3 | `single_round` | up to 12 (engine picks K=12 high-entropy traits) |
| Medium (vd 6-12h) | 4-6 | `single_round` | up to 12 |
| Wide (vd 5-15h) | 7-9 | `two_round` | 6 + 6 = 12 |
| Unknown (toàn bộ) | 12 | `three_round` | 5 + 5 + 5 = 15 |

Strategy is decided by [`engine.detect_strategy(candidates)`](engine/yi_wiki/birth_hour_quiz_v2/engine.py) based on `len(candidates)`:
- ≤ 6 → `single_round`
- 7-9 → `two_round`
- ≥ 10 → `three_round`

### Convergence rule

After each round R:
1. Compute new total scores per candidate
2. If `(top - second) / top > 0.5` → STOP, return FINAL
3. If `round_num >= max_rounds` → STOP, return FINAL_UNCERTAIN (top 2 with note)
4. Otherwise: drop candidates with `score < 0.5 * top`, keep up to 6 → next round

---

## 3. Trait derivation (19 dimensions)

### Domain 1: NGOẠI HÌNH — Rules-driven (7 traits)

| # | Trait | Inputs | Values |
|---|---|---|---|
| 1 | `body_height` | Năm chi + Nhật Chủ ngũ hành | cao / trung_binh / thap |
| 2 | `body_build` | Nhật Chủ vượng/nhược | gay_thon / trung_binh / day_dan / dam_chac |
| 3 | `face_shape` | Nhật Chủ element + Giờ chi | dai / vuong / tron / nhon / oval |
| 4 | `skin_tone` | Nhật Chủ + ngũ hành balance | trang / hong_hao / vua / sam |
| 5 | `hair_quality` | Nhật Chủ + Mộc tinh trong trụ | day_muot / mong / xoan / thang_cung |
| 6 | `eye_features` | Hỏa+Thủy balance | sang_to / sau_hep / hien_min / sac_net |
| 7 | `physiognomy_marks` | Giờ chi specific (TCM clock) | 1_xoay / 2_xoay / vung_dac_biet |

**Rule source:** Tướng Pháp Cổ + Tử Bình Cổ truyền. Code at `engine/yi_wiki/birth_hour_quiz_v2/rules/physical.py`.

Day Master → body baseline (10 stems):
- Giáp Mộc: tall, thin, straight bones, light skin
- Ất Mộc: slender, flexible, soft skin, slightly tall
- Bính Hỏa: bright complexion, sharp features, medium build
- Đinh Hỏa: warm tone, oval face, slightly slim
- Mậu Thổ: stocky, broad shoulders, square face, earthy tone
- Kỷ Thổ: gentle build, round face, smooth skin
- Canh Kim: sharp features, angular, fair skin, athletic
- Tân Kim: refined, slim, fair, delicate
- Nhâm Thủy: flowing motion, full features, fair-medium
- Quý Thủy: clear skin, soft, slim

Modifiers: year chi (height), month chi (seasonal vitality), hour chi (specific physiognomy marks via TCM organ clock).

### Domain 2: TÍNH CÁCH — LLM-driven + rule hints (5 traits)

| # | Trait | Inputs | Values |
|---|---|---|---|
| 8 | `decision_style` | Thập Thần dominant | impulsive / analytical / consultative / patient |
| 9 | `leadership_orientation` | Cách Cục | dominant / collaborative / supportive / independent |
| 10 | `introvert_extrovert` | Dương/Âm tỷ lệ tứ trụ | mostly_intro / mid / mostly_extro |
| 11 | `emotional_pattern` | Thủy/Hỏa balance | cool / passionate / volatile / steady |
| 12 | `communication_style` | Thực-Thương-Quan | direct / nuanced / quiet / expressive |

**Note:** trait #10 is rule-derived (count Dương/Âm stems in 4 pillars). Others go through LLM but with rule-derived "hints" injected into prompt for grounding.

### Domain 3: ENERGY PATTERNS — Rules-driven via TCM clock (3 traits)

| # | Trait | Inputs | Values |
|---|---|---|---|
| 13 | `wake_natural_time` | Giờ chi (TCM organ governance) | truoc_5h / 5_7h / 7_9h / 9_11h / muon |
| 14 | `energy_peak_period` | Giờ chi + Hỏa/Thủy | sang / trua / chieu / toi / dem |
| 15 | `sleep_pattern` | Giờ chi (opposite hour) | truoc_22h / 22_23h / 23_1h / sau_1h |

**TCM organ clock mapping:**
- Tý (23-1h): thận → night owl, peak late, sleep late
- Sửu (1-3h): can → wake early, calm, sleep early
- Dần (3-5h): phế → wake very early, active mornings
- Mão (5-7h): đại trường → morning person, regular
- Thìn (7-9h): vị → breakfast person, morning energy
- Tỵ (9-11h): tỳ → mid-morning energy
- Ngọ (11-13h): tâm → noon peak, high passion
- Mùi (13-15h): tiểu trường → afternoon mellow
- Thân (15-17h): bàng quang → afternoon active
- Dậu (17-19h): thận → evening calm
- Tuất (19-21h): tâm bào → night settle
- Hợi (21-23h): tam tiêu → late night peaceful

Code at `engine/yi_wiki/birth_hour_quiz_v2/rules/energy.py`.

### Domain 4: LIFE EVENTS — LLM-driven + cách cục rules (4 traits)

| # | Trait | Inputs | Values |
|---|---|---|---|
| 16 | `career_direction` | Cách Cục + Tài-Quan-Ấn | corporate / creative / entrepreneurial / professional / craftsman |
| 17 | `sibling_position_likely` | Năm chi + Tỷ Kiên/Kiếp Tài | ca / giua / ut / duy_nhat |
| 18 | `marriage_timing_rough` | Quan/Sát + đại vận | som_25 / 25_30 / 30_35 / muon_35 |
| 19 | `health_pattern_general` | Nhật Chủ vượng/nhược + xung khắc | strong / on / nhay / yeu_vung_X |

**Privacy consideration:** Domain 4 traits are personal but Anh approved comprehensive scope (Section 2 brainstorm Q3).

### LLM call strategy

- **Model:** DeepSeek-Reasoner (cost ~$0.55/1M in + $2.19/1M out; ~$0.015/quiz with 4 candidates)
- **Provider fallback:** if DeepSeek fails → log `flagged_outputs` + retry with Claude Sonnet 4.6
- **Prompt structure:**
  ```
  System: You are a Tử Bình expert. For each bát tự below, predict the 9 traits listed.
          Output STRICT JSON: {chi_name: {trait_id: value}, ...}. No prose.

  User: Bát tự candidates:
        - Mão hour: {năm: Mậu Thìn, tháng: Bính Thìn, ngày: Quý Sửu, giờ: Ất Mão}
          Cách cục hint: ...
          Thập thần dominant: ...
        - Thìn hour: {...}
        - Tỵ hour: {...}
        - Ngọ hour: {...}
        
        Predict for each:
        - decision_style: impulsive | analytical | consultative | patient
        - leadership_orientation: dominant | collaborative | supportive | independent
        - emotional_pattern: cool | passionate | volatile | steady
        - communication_style: direct | nuanced | quiet | expressive
        - career_direction: corporate | creative | entrepreneurial | professional | craftsman
        - marriage_timing_rough: som_25 | 25_30 | 30_35 | muon_35
        - health_pattern_general: strong | on | nhay | yeu_vung_X
        
        Return JSON only.
  ```
- **Validation:** parse JSON, validate enum values per trait, retry once if invalid

Code at `engine/yi_wiki/birth_hour_quiz_v2/llm_prompts.py`.

---

## 4. Diff analysis + question generation

### Entropy formula

```python
def entropy(predictions: dict[str, str]) -> float:
    """
    predictions: {candidate_chi: predicted_value}
    Returns: Shannon entropy in bits
    """
    counts = Counter(predictions.values())
    total = sum(counts.values())
    return -sum((c/total) * math.log2(c/total) for c in counts.values())
```

### Selection per round

```python
# K must match strategy table in §2 so total questions stay consistent
K_PER_ROUND = {
    "single_round": 12,   # 1 round of 12 questions
    "two_round":     6,   # 2 × 6 = 12
    "three_round":   5,   # 3 × 5 = 15
}

def select_questions_for_round(
    strategy: str,
    candidates: list[str],
    predictions: dict[str, dict[str, str]],  # {chi: {trait: value}}
    used_dimensions: set[str],
) -> list[Question]:
    K = K_PER_ROUND[strategy]
    
    entropies = {}
    for trait in TRAIT_DIMENSIONS:
        if trait in used_dimensions:
            continue
        trait_predictions = {c: predictions[c][trait] for c in candidates}
        h = entropy(trait_predictions)
        if h > 0:
            entropies[trait] = h
    
    top_traits = sorted(entropies.items(), key=lambda x: -x[1])[:K]
    return [generate_question(t, predictions, candidates) for t, _ in top_traits]
```

If fewer than K traits have entropy > 0 (rare: candidates converged before budget), return what's available — engine will mark final on next submit.

### Question template format

Each trait has a Vietnamese question template at `engine/yi_wiki/birth_hour_quiz_v2/templates.py`:

```python
TRAIT_TEMPLATES = {
    "face_shape": {
        "question_vi": "Khuôn mặt của Anh có dạng nào gần nhất?",
        "domain": "ngoại hình",
        "value_labels": {
            "dai":   "Dài, gọn",
            "vuong": "Vuông, góc cạnh",
            "tron":  "Tròn, đầy đặn",
            "nhon":  "Sắc, hẹp về phía dưới",
            "oval":  "Oval cân đối",
        }
    },
    # ... 18 more templates
}
```

### Question generation

Group candidates with same predicted value into one option:

```python
def generate_question(trait, predictions, candidates):
    template = TRAIT_TEMPLATES[trait]
    groups = defaultdict(list)
    for chi in candidates:
        value = predictions[chi][trait]
        groups[value].append(chi)
    
    options = [
        {
            "id": value,
            "label": template["value_labels"][value],
            "candidates": chis,
        }
        for value, chis in groups.items()
    ]
    options.append({"id": "unsure", "label": "Tôi không rõ / khó nói", "candidates": []})
    
    return {
        "id": trait,
        "question": template["question_vi"],
        "domain": template["domain"],
        "options": options,
        "weight": entropy_value,
    }
```

### Scoring

```python
def score_answer(candidates, question, chosen_option):
    if chosen_option == "unsure":
        return {c: 0 for c in candidates}
    
    chosen = next(o for o in question["options"] if o["id"] == chosen_option)
    weight = question["weight"]
    
    delta = {}
    for c in candidates:
        if c in chosen["candidates"]:
            delta[c] = +weight        # match → reward
        else:
            delta[c] = -weight * 0.5  # mismatch → soft penalty
    return delta
```

### Convergence check (after each round)

```python
def after_round(scores, candidates_remaining, round_num, max_rounds):
    top_score = max(scores.values())
    sorted_scores = sorted(scores.values(), reverse=True)
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
    
    # Stop: clear winner
    if top_score > 0 and (top_score - second_score) / top_score > 0.5:
        return "FINAL", top_candidate(scores)
    
    # Stop: budget exhausted
    if round_num >= max_rounds:
        return "FINAL_UNCERTAIN", top_2_candidates(scores)
    
    # Continue: drop weak (< 50% of top), cap at 6
    surviving = [c for c in candidates_remaining if scores[c] >= top_score * 0.5]
    return "CONTINUE", surviving[:6]
```

---

## 5. UI + API + DB

### Entry points

1. **Replace v1 in [QuickTasksPanel.vue](../../../client/webapp/src/components/QuickTasksPanel.vue)** — main entry
2. **[BatTuPanel.vue](../../../client/webapp/src/components/BatTuPanel.vue)** — button "🔍 Tìm lại giờ sinh" when `birth_confidence !== 'exact'`
3. **PersonForm (tab Hồ sơ)** — toggle "Không nhớ chính xác giờ → mở quiz" when creating profile
4. **AuspiciousDayPanel** — banner "Để TOP 7 ngày chính xác hơn → tìm giờ sinh trước"

### Component: `BirthHourQuizV2.vue`

4-stage state machine:

**Stage 1: INPUT**
- Birth date picker (required)
- Timezone selector (default Asia/Ho_Chi_Minh)
- Gender radio
- Hour range: dual-handle slider 0-23h + checkbox "không nhớ gì"
- [Bắt đầu trắc nghiệm →]

**Stage 2: LOADING (3-5 seconds)**
- Spinner "Đang phân tích bát tự..."
- Show animation: candidates being narrowed visually

**Stage 3: ROUND N**
- Header: "Vòng X/Y · còn N ứng cử: ..."
- Progress bar across questions
- Question list (scrollable on desktop, step wizard on mobile)
- Each question: radio group + "Tôi không rõ" fallback
- [Submit Vòng N →]
- Loop until status=FINAL

**Stage 4: FINAL RESULT**
- Top 1 candidate prominently displayed (chi + range + animal icon)
- Confidence label (Cao / Vừa / Thấp)
- Per-candidate reasoning ("✓ Thìn: face vuông + leadership — khớp" / "✗ Mão: predict face dài — KHÔNG khớp")
- [💾 Lưu vào hồ sơ] [🔄 Trắc nghiệm lại]

### API endpoints (stateful)

```http
POST /api/yi-wiki/birth-hour-quiz-v2/start
  Body:
    {
      "birth_date": "1988-05-02",
      "timezone": "Asia/Ho_Chi_Minh",
      "hour_range": {"start": 6, "end": 12} | null,
      "gender": "nam" | "nữ"
    }
  Returns:
    {
      "session_id": "uuid",
      "candidates": ["Mão", "Thìn", "Tỵ", "Ngọ"],
      "strategy": "single_round" | "two_round" | "three_round",
      "round_1": {
        "round_num": 1,
        "total_rounds": 1,
        "questions": [...]
      }
    }

POST /api/yi-wiki/birth-hour-quiz-v2/submit-round
  Body:
    {
      "session_id": "uuid",
      "round_num": 1,
      "answers": {"face_shape": "vuong", "decision_style": "analytical", ...}
    }
  Returns:
    {
      "status": "CONTINUE" | "FINAL" | "FINAL_UNCERTAIN",
      "scores": {"Mão": 12, "Thìn": 38, ...},
      "candidates_remaining": ["Thìn", "Ngọ"],
      "next_round": {...} | null,
      "final_result": {...} | null
    }

GET /api/yi-wiki/birth-hour-quiz-v2/session/{session_id}
  Returns: full session state (resume)

POST /api/yi-wiki/birth-hour-quiz-v2/save-result
  Body: {"session_id": "uuid", "person_id": "_founder"}
  Effect: update user_persons.birth_datetime_local to midpoint of chi giờ
```

### Database: `birth_hour_quiz_sessions` (new table in `data/yi_users/users.sqlite3`)

```sql
CREATE TABLE birth_hour_quiz_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER,                          -- nullable for anonymous
    birth_date TEXT NOT NULL,
    timezone TEXT NOT NULL,
    hour_range_start INTEGER,                 -- nullable
    hour_range_end INTEGER,                   -- nullable
    gender TEXT,
    candidates_initial TEXT NOT NULL,         -- JSON array
    candidates_remaining TEXT NOT NULL,       -- JSON array (updates per round)
    strategy TEXT NOT NULL,                   -- 'single_round' | 'two_round' | 'three_round'
    rounds_data TEXT NOT NULL,                -- JSON history
    accumulated_scores TEXT NOT NULL,         -- JSON {chi: score}
    final_result TEXT,                        -- JSON when status=final
    status TEXT NOT NULL DEFAULT 'in_progress',  -- in_progress | final
    created_at INTEGER NOT NULL,
    completed_at INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_quiz_sessions_user ON birth_hour_quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_status ON birth_hour_quiz_sessions(status);
```

### Session retention

- Active sessions kept indefinitely
- Cleanup cron: delete `in_progress` sessions older than 7 days (no completion)
- `final` sessions kept indefinitely for audit/recall

### Backward compatibility

- v1 endpoints `/api/yi-wiki/birth-hour-quiz/{questions,analyze}` GIỮ NGUYÊN — not break QuickTasksPanel render path during transition
- v2 endpoints with `-v2/` suffix
- UI QuickTasksPanel migrates to v2 component (renders v2 only — but v1 endpoint still callable by anyone with stale link)
- Future cleanup: remove v1 after 1 month if no usage

---

## 6. File structure

**Backend:**
```
engine/yi_wiki/birth_hour_quiz_v2/
├── __init__.py                  # public API: start_quiz, submit_round, etc.
├── engine.py                    # orchestration: strategy detection, multi-round loop
├── rules/
│   ├── __init__.py
│   ├── physical.py              # Domain 1: 7 physical traits
│   ├── energy.py                # Domain 3: 3 energy traits (TCM clock)
│   └── personality.py           # Domain 2: trait 10 + hints for LLM
├── llm_prompts.py               # Domain 2 + 4 LLM prompt templates + parser
├── templates.py                 # 19 question template constants
├── scoring.py                   # entropy + score_answer + after_round
└── session_store.py             # DB persistence layer
```

**Frontend:**
```
client/webapp/src/components/
├── BirthHourQuizV2.vue          # 4-stage state machine (new)
└── (modify) QuickTasksPanel.vue # render BirthHourQuizV2 instead of v1
                  BatTuPanel.vue # add "🔍 Tìm lại giờ sinh" button
```

**API:**
```
api/main.py                       # add 4 endpoints under /api/yi-wiki/birth-hour-quiz-v2/
```

**Tests:**
```
tests/test_birth_hour_quiz_v2.py     # unit tests: rules, entropy, scoring, convergence
tests/test_birth_hour_quiz_v2_api.py # integration: endpoints + session DB
```

---

## 7. Decomposition + estimates

| Phase | Scope | Est. time |
|---|---|---|
| **A** Foundation | Rules (Domain 1, 3, partial 2) + LLM prompts (Domain 2, 4) | 3-4h |
| **B** Quiz logic | Entropy + question gen + multi-round orchestration + scoring | 2-3h |
| **C** API + DB | 4 endpoints + sessions table migration | 2h |
| **D** UI | BirthHourQuizV2.vue + entry points integration | 3-4h |
| **E** Polish | Loading anim, error states, mobile, a11y | 1-2h |

**Total: ~12-15 hours**, can split across 2-3 sessions.

---

## 8. Risks + mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM hallucinate Domain 2/4 traits | High | Medium | Strict JSON schema, retry once on parse fail, fallback Claude, log flagged outputs |
| Borderline hour conventions (early/late Zi) | Medium | Medium | Support both, default early_zi (Anh's convention) |
| Range crossing midnight (22h-2h) | Low | Medium | Detect + split into 2 segments |
| Session lost on container restart | Low | Low | DB-persisted (chosen) |
| Cost spike from spam | Low | Low | Rate limit: 1 quiz/5 min/IP, max 3/hour/user |
| Mobile UX with long question list | High | Low | Step wizard 1 question/screen on mobile |

---

## 9. Out of scope (defer to future iterations)

- Image upload (face photo analysis)
- Voice input
- Multi-language (only Vietnamese for v2 MVP)
- Social sharing of result
- Compare 2 people simultaneously
- Reverse from life events ("married age 28 → infer hour") — needs separate timing-rectification module

---

## 10. Decisions resolved during brainstorm

| Decision | Choice |
|---|---|
| Algorithm: rules vs LLM vs hybrid | **C. Hybrid** (rules for physical/energy, LLM for personality/life events) |
| Trait scope | **Comprehensive**: ngoại hình + tính cách + energy + life events (19 dimensions) |
| Multi-round strategy | **Adaptive**: 1/2/3 rounds depending on initial range size |
| LLM provider | **DeepSeek-Reasoner** (primary), Claude Sonnet fallback |
| v1 fate | **Keep endpoints** for backward compat, **UI switches to v2** |

---

## 11. Out of design (UX details to decide during implementation)

- Exact wording of 19 question templates (Anh review during implementation phase)
- Animation choreography for "narrowing candidates" visual
- Color palette for reasoning cards (✓ green / ✗ red? or more nuanced?)
- Mobile breakpoint for step wizard vs scrollable list

These are not blocking — implementer decides + Anh review on browser test.

---

**End of spec.** Next step: invoke `superpowers:writing-plans` to convert this design into a phased implementation plan.
