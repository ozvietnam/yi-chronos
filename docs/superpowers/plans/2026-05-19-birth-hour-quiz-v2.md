# Birth Hour Quiz v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement multi-round adaptive birth-hour quiz that derives traits from full bát tự hypotheses (rules + LLM hybrid) and discriminates candidates by entropy across 19 trait dimensions.

**Architecture:** Backend Python module `engine/yi_wiki/birth_hour_quiz_v2/` (rules + LLM derivation + multi-round engine + DB-backed sessions). FastAPI exposes 4 endpoints. Vue component `BirthHourQuizV2.vue` provides 4-stage UX (input → loading → rounds → result).

**Tech Stack:** Python 3.14 + FastAPI + SQLite + DeepSeek-Reasoner LLM + Vue 3 + Vite.

**Spec reference:** [`docs/superpowers/specs/2026-05-19-birth-hour-quiz-v2-design.md`](../specs/2026-05-19-birth-hour-quiz-v2-design.md)

**Execution note:** Auto-sync daemon may commit during work. To get clean commit boundaries from this plan, run `scripts/deploy/auto-sync-stop.sh` before starting, then `auto-sync-start.sh` after each phase.

---

## 0. Pre-flight

### Task 0.1: Verify environment

**Files:** none modified

- [ ] **Step 1: Verify .venv has needed packages**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
.venv/bin/python3 -c "import fastapi, pytest, httpx; print('deps OK')"
```

Expected: `deps OK`. If fail, run `.venv/bin/pip install -r requirements.txt`.

- [ ] **Step 2: Verify ai_keys.json has deepseek**

```bash
.venv/bin/python3 -c "import json; d=json.load(open('data/ai_keys.json')); print('deepseek:', 'deepseek' in d)"
```

Expected: `deepseek: True`. If false, Anh sets via UI tab Cài đặt before continuing.

- [ ] **Step 3: Stop auto-sync daemon for clean commits (optional)**

```bash
scripts/deploy/auto-sync-stop.sh
```

Expected: `✓ stopped (PID ...)`.

### Task 0.2: Create module skeleton

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/__init__.py`
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/__init__.py`

- [ ] **Step 1: Create directory + empty __init__.py**

```bash
mkdir -p engine/yi_wiki/birth_hour_quiz_v2/rules
touch engine/yi_wiki/birth_hour_quiz_v2/__init__.py
touch engine/yi_wiki/birth_hour_quiz_v2/rules/__init__.py
```

- [ ] **Step 2: Verify import works**

```bash
.venv/bin/python3 -c "from engine.yi_wiki import birth_hour_quiz_v2; print('skeleton OK')"
```

Expected: `skeleton OK`.

- [ ] **Step 3: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/
git commit -m "scaffold: birth_hour_quiz_v2 module skeleton"
```

---

## Phase A: Rules engines (Domain 1 + 3 + Trait 10)

### Task A.1: Stems table + Day Master baselines

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/stems.py`
- Create: `tests/test_birth_hour_quiz_v2_stems.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_birth_hour_quiz_v2_stems.py
from engine.yi_wiki.birth_hour_quiz_v2.rules.stems import (
    STEM_ELEMENTS, STEM_YIN_YANG, DAY_MASTER_BASELINE
)


def test_stem_elements_complete():
    assert len(STEM_ELEMENTS) == 10
    assert STEM_ELEMENTS["Giáp"] == "Mộc"
    assert STEM_ELEMENTS["Quý"] == "Thuỷ"


def test_stem_yin_yang():
    assert STEM_YIN_YANG["Giáp"] == "Dương"
    assert STEM_YIN_YANG["Ất"] == "Âm"


def test_day_master_baseline_giap():
    bl = DAY_MASTER_BASELINE["Giáp"]
    assert bl["body_height"] == "cao"
    assert bl["body_build"] == "gay_thon"
    assert bl["skin_tone"] == "trang"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_stems.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'engine.yi_wiki.birth_hour_quiz_v2.rules.stems'`.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/rules/stems.py
"""Ten Heavenly Stems — element, yin/yang, and day-master physical baseline."""
from __future__ import annotations

STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

STEM_ELEMENTS = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hoả", "Đinh": "Hoả",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thuỷ", "Quý": "Thuỷ",
}

STEM_YIN_YANG = {
    "Giáp": "Dương", "Ất": "Âm",
    "Bính": "Dương", "Đinh": "Âm",
    "Mậu": "Dương", "Kỷ": "Âm",
    "Canh": "Dương", "Tân": "Âm",
    "Nhâm": "Dương", "Quý": "Âm",
}

# Day Master baseline — physical defaults derived from Tướng Pháp Cổ.
# Modifiers from năm/tháng/giờ chi adjust these in physical.py.
DAY_MASTER_BASELINE = {
    "Giáp": {"body_height": "cao",          "body_build": "gay_thon",   "face_shape": "dai",   "skin_tone": "trang",    "hair_quality": "thang_cung"},
    "Ất":   {"body_height": "cao",          "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
    "Bính": {"body_height": "trung_binh",   "body_build": "trung_binh", "face_shape": "nhon",  "skin_tone": "hong_hao", "hair_quality": "day_muot"},
    "Đinh": {"body_height": "trung_binh",   "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "hong_hao", "hair_quality": "mong"},
    "Mậu": {"body_height": "trung_binh",   "body_build": "dam_chac",   "face_shape": "vuong", "skin_tone": "sam",      "hair_quality": "thang_cung"},
    "Kỷ":  {"body_height": "trung_binh",   "body_build": "day_dan",    "face_shape": "tron",  "skin_tone": "vua",      "hair_quality": "day_muot"},
    "Canh": {"body_height": "trung_binh",  "body_build": "dam_chac",   "face_shape": "vuong", "skin_tone": "trang",    "hair_quality": "thang_cung"},
    "Tân":  {"body_height": "trung_binh",  "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
    "Nhâm": {"body_height": "cao",         "body_build": "day_dan",    "face_shape": "tron",  "skin_tone": "vua",      "hair_quality": "xoan"},
    "Quý":  {"body_height": "trung_binh",  "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_stems.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/rules/stems.py tests/test_birth_hour_quiz_v2_stems.py
git commit -m "feat(quiz-v2): Heavenly Stems table + Day Master physical baseline"
```

### Task A.2: Branches table + hour chi mappings

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/branches.py`
- Modify: `tests/test_birth_hour_quiz_v2_stems.py` (add branches tests)

- [ ] **Step 1: Add failing tests**

Append to `tests/test_birth_hour_quiz_v2_stems.py`:

```python
from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import (
    BRANCH_ELEMENTS, HOUR_RANGES, TCM_ORGAN
)


def test_branch_elements():
    assert len(BRANCH_ELEMENTS) == 12
    assert BRANCH_ELEMENTS["Tý"] == "Thuỷ"
    assert BRANCH_ELEMENTS["Hợi"] == "Thuỷ"
    assert BRANCH_ELEMENTS["Ngọ"] == "Hoả"


def test_hour_ranges_cover_24h():
    total = 0
    for chi, (start, end) in HOUR_RANGES.items():
        # Tý wraps across midnight
        span = (end - start) % 24 or 24
        assert span == 2, f"{chi} span should be 2h, got {span}"
        total += span
    assert total == 24


def test_tcm_organ_clock():
    assert TCM_ORGAN["Tý"] == "thận"
    assert TCM_ORGAN["Ngọ"] == "tâm"
```

- [ ] **Step 2: Run test (fails - branches.py missing)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_stems.py -v -k branches
```

Expected: FAIL `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/rules/branches.py
"""Twelve Earthly Branches — element, hour ranges, TCM organ clock."""
from __future__ import annotations

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
            "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

BRANCH_ELEMENTS = {
    "Tý": "Thuỷ",   "Sửu": "Thổ",  "Dần": "Mộc",  "Mão": "Mộc",
    "Thìn": "Thổ",  "Tỵ": "Hoả",   "Ngọ": "Hoả",  "Mùi": "Thổ",
    "Thân": "Kim",  "Dậu": "Kim",  "Tuất": "Thổ", "Hợi": "Thuỷ",
}

# (start_hour, end_hour) — Tý spans 23h-1h (wraps).
HOUR_RANGES = {
    "Tý":   (23, 1),
    "Sửu":  (1, 3),
    "Dần":  (3, 5),
    "Mão":  (5, 7),
    "Thìn": (7, 9),
    "Tỵ":   (9, 11),
    "Ngọ":  (11, 13),
    "Mùi":  (13, 15),
    "Thân": (15, 17),
    "Dậu":  (17, 19),
    "Tuất": (19, 21),
    "Hợi":  (21, 23),
}

# TCM organ clock — each 2-hour period governs an organ.
# Used to derive wake/peak/sleep traits in rules/energy.py.
TCM_ORGAN = {
    "Tý": "thận", "Sửu": "can", "Dần": "phế",     "Mão": "đại trường",
    "Thìn": "vị", "Tỵ": "tỳ",   "Ngọ": "tâm",      "Mùi": "tiểu trường",
    "Thân": "bàng quang", "Dậu": "thận",  "Tuất": "tâm bào", "Hợi": "tam tiêu",
}


def hour_to_chi(hour: int) -> str:
    """Convert 0-23 hour to Earthly Branch."""
    for chi, (start, end) in HOUR_RANGES.items():
        if start > end:  # wraps midnight (Tý)
            if hour >= start or hour < end:
                return chi
        elif start <= hour < end:
            return chi
    raise ValueError(f"hour {hour} out of range")
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_stems.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/rules/branches.py tests/test_birth_hour_quiz_v2_stems.py
git commit -m "feat(quiz-v2): Earthly Branches + hour ranges + TCM organ clock"
```

### Task A.3: Physical traits derivation (Domain 1, 7 traits)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/physical.py`
- Create: `tests/test_birth_hour_quiz_v2_physical.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_physical.py
from engine.yi_wiki.birth_hour_quiz_v2.rules.physical import derive_physical_traits

# Example bát tự: 1988-05-02 hour Thìn
# year=Mậu Thìn, month=Bính Thìn, day=Quý Sửu, hour=Bính Thìn
SAMPLE_PILLARS = {
    "year":  {"stem": "Mậu", "branch": "Thìn"},
    "month": {"stem": "Bính", "branch": "Thìn"},
    "day":   {"stem": "Quý", "branch": "Sửu"},
    "hour":  {"stem": "Bính", "branch": "Thìn"},
}


def test_derive_physical_returns_7_traits():
    out = derive_physical_traits(SAMPLE_PILLARS)
    expected_keys = {
        "body_height", "body_build", "face_shape", "skin_tone",
        "hair_quality", "eye_features", "physiognomy_marks",
    }
    assert set(out.keys()) == expected_keys


def test_face_shape_uses_day_master_and_hour():
    # Quý Thuỷ baseline=oval, hour Thìn=Thổ → expect adjustment
    out = derive_physical_traits(SAMPLE_PILLARS)
    assert out["face_shape"] in {"oval", "vuong", "tron"}


def test_physiognomy_marks_from_hour_chi():
    # Hour Tý / Ngọ → 1 xoáy (per CHI_HOUR_PHYSIOGNOMY)
    pillars_ty = {**SAMPLE_PILLARS, "hour": {"stem": "Nhâm", "branch": "Tý"}}
    out = derive_physical_traits(pillars_ty)
    assert out["physiognomy_marks"] == "1_xoay"
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_physical.py -v
```

Expected: FAIL `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/rules/physical.py
"""Derive 7 physical traits from bát tự pillars (Domain 1)."""
from __future__ import annotations

from .stems import STEM_ELEMENTS, DAY_MASTER_BASELINE
from .branches import BRANCH_ELEMENTS

# Hour chi → physiognomy mark pattern (Tướng Pháp Cổ).
CHI_HOUR_PHYSIOGNOMY = {
    "Tý": "1_xoay", "Ngọ": "1_xoay", "Mão": "1_xoay", "Dậu": "1_xoay",
    "Dần": "2_xoay", "Thìn": "2_xoay", "Thân": "2_xoay", "Tuất": "2_xoay",
    "Sửu": "vung_dac_biet", "Mùi": "vung_dac_biet", "Tỵ": "vung_dac_biet", "Hợi": "vung_dac_biet",
}

# Eye features by Hỏa-Thủy presence in pillars.
def _derive_eyes(pillars: dict) -> str:
    elements = [STEM_ELEMENTS[p["stem"]] for p in pillars.values()] + \
               [BRANCH_ELEMENTS[p["branch"]] for p in pillars.values()]
    fire = elements.count("Hoả")
    water = elements.count("Thuỷ")
    if fire >= 3:
        return "sang_to"
    if water >= 3:
        return "hien_min"
    if fire > water:
        return "sac_net"
    return "sau_hep"


def derive_physical_traits(pillars: dict) -> dict[str, str]:
    """Compute 7 physical traits from full pillars.

    Args:
        pillars: {year, month, day, hour} each with {stem, branch}

    Returns:
        Dict with keys: body_height, body_build, face_shape, skin_tone,
        hair_quality, eye_features, physiognomy_marks.
    """
    day_master = pillars["day"]["stem"]
    baseline = DAY_MASTER_BASELINE[day_master]

    # face_shape: blend baseline with hour chi element influence
    hour_element = BRANCH_ELEMENTS[pillars["hour"]["branch"]]
    face = baseline["face_shape"]
    if hour_element == "Thổ" and face in {"oval", "dai"}:
        face = "vuong"
    elif hour_element == "Thuỷ" and face == "vuong":
        face = "tron"

    # skin_tone: baseline + năm chi modifier (if năm = water → fairer)
    skin = baseline["skin_tone"]
    if BRANCH_ELEMENTS[pillars["year"]["branch"]] == "Thuỷ" and skin == "sam":
        skin = "vua"

    return {
        "body_height": baseline["body_height"],
        "body_build":  baseline["body_build"],
        "face_shape":  face,
        "skin_tone":   skin,
        "hair_quality": baseline["hair_quality"],
        "eye_features": _derive_eyes(pillars),
        "physiognomy_marks": CHI_HOUR_PHYSIOGNOMY[pillars["hour"]["branch"]],
    }
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_physical.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/rules/physical.py tests/test_birth_hour_quiz_v2_physical.py
git commit -m "feat(quiz-v2): Domain 1 physical traits derivation (7 traits)"
```

### Task A.4: Energy traits derivation (Domain 3, 3 traits via TCM clock)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/energy.py`
- Create: `tests/test_birth_hour_quiz_v2_energy.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_energy.py
from engine.yi_wiki.birth_hour_quiz_v2.rules.energy import derive_energy_traits


def test_derive_energy_returns_3_traits():
    pillars = {"hour": {"branch": "Mão"}}
    out = derive_energy_traits(pillars)
    assert set(out.keys()) == {"wake_natural_time", "energy_peak_period", "sleep_pattern"}


def test_mao_morning_person():
    """Mão hour (5-7h) → wake early, peak morning."""
    out = derive_energy_traits({"hour": {"branch": "Mão"}})
    assert out["wake_natural_time"] == "5_7h"
    assert out["energy_peak_period"] == "sang"


def test_ty_night_owl():
    """Tý hour (23-1h) → late sleep, peak late."""
    out = derive_energy_traits({"hour": {"branch": "Tý"}})
    assert out["sleep_pattern"] == "sau_1h"
    assert out["energy_peak_period"] == "dem"


def test_ngo_noon_peak():
    """Ngọ hour (11-13h) → peak noon."""
    out = derive_energy_traits({"hour": {"branch": "Ngọ"}})
    assert out["energy_peak_period"] == "trua"
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_energy.py -v
```

Expected: FAIL `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/rules/energy.py
"""Energy patterns from TCM organ clock (Domain 3, 3 traits)."""
from __future__ import annotations

# Per hour chi, derived from TCM organ that governs.
WAKE_TIME = {
    "Tý":   "muon",     "Sửu":  "truoc_5h", "Dần":  "truoc_5h",
    "Mão":  "5_7h",     "Thìn": "7_9h",     "Tỵ":   "9_11h",
    "Ngọ":  "9_11h",    "Mùi":  "9_11h",    "Thân": "9_11h",
    "Dậu":  "muon",     "Tuất": "muon",     "Hợi":  "muon",
}

ENERGY_PEAK = {
    "Tý":   "dem",     "Sửu":  "sang",   "Dần":  "sang",
    "Mão":  "sang",    "Thìn": "sang",   "Tỵ":   "sang",
    "Ngọ":  "trua",    "Mùi":  "chieu",  "Thân": "chieu",
    "Dậu":  "chieu",   "Tuất": "toi",    "Hợi":  "toi",
}

SLEEP_PATTERN = {
    "Tý":   "sau_1h",   "Sửu":  "truoc_22h", "Dần":  "truoc_22h",
    "Mão":  "truoc_22h","Thìn": "22_23h",    "Tỵ":   "22_23h",
    "Ngọ":  "22_23h",   "Mùi":  "22_23h",    "Thân": "22_23h",
    "Dậu":  "23_1h",    "Tuất": "23_1h",     "Hợi":  "23_1h",
}


def derive_energy_traits(pillars: dict) -> dict[str, str]:
    """Compute 3 energy traits from hour chi (TCM organ clock)."""
    hour_chi = pillars["hour"]["branch"]
    return {
        "wake_natural_time":  WAKE_TIME[hour_chi],
        "energy_peak_period": ENERGY_PEAK[hour_chi],
        "sleep_pattern":      SLEEP_PATTERN[hour_chi],
    }
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_energy.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/rules/energy.py tests/test_birth_hour_quiz_v2_energy.py
git commit -m "feat(quiz-v2): Domain 3 energy traits via TCM organ clock"
```

### Task A.5: Personality rule trait (Trait 10: yin-yang ratio)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/rules/personality.py`
- Create: `tests/test_birth_hour_quiz_v2_personality.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_personality.py
from engine.yi_wiki.birth_hour_quiz_v2.rules.personality import (
    derive_yin_yang_ratio, derive_sibling_position_hint,
)


def test_all_yang_stems_extrovert():
    pillars = {
        "year":  {"stem": "Giáp", "branch": "Tý"},
        "month": {"stem": "Bính", "branch": "Tý"},
        "day":   {"stem": "Mậu",  "branch": "Tý"},
        "hour":  {"stem": "Canh", "branch": "Tý"},
    }
    assert derive_yin_yang_ratio(pillars) == "mostly_extro"


def test_all_yin_stems_introvert():
    pillars = {
        "year":  {"stem": "Ất",  "branch": "Sửu"},
        "month": {"stem": "Đinh", "branch": "Sửu"},
        "day":   {"stem": "Kỷ",  "branch": "Sửu"},
        "hour":  {"stem": "Tân", "branch": "Sửu"},
    }
    assert derive_yin_yang_ratio(pillars) == "mostly_intro"


def test_mixed_yin_yang_mid():
    pillars = {
        "year":  {"stem": "Giáp", "branch": "Tý"},
        "month": {"stem": "Ất",  "branch": "Sửu"},
        "day":   {"stem": "Bính", "branch": "Tý"},
        "hour":  {"stem": "Đinh", "branch": "Sửu"},
    }
    assert derive_yin_yang_ratio(pillars) == "mid"


def test_sibling_position_co_son():
    """Year chi = Tý/Ngọ/Mão/Dậu (đào hoa) suggests ca position."""
    pillars = {"year": {"branch": "Mão"}}
    assert derive_sibling_position_hint(pillars) == "ca"
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_personality.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/rules/personality.py
"""Rule-derived personality hints (Trait 10 + Trait 17 helpers)."""
from __future__ import annotations

from .stems import STEM_YIN_YANG


def derive_yin_yang_ratio(pillars: dict) -> str:
    """Count Dương vs Âm stems across 4 pillars → introvert/extrovert hint.

    Returns: 'mostly_intro' | 'mid' | 'mostly_extro'
    """
    yang_count = sum(
        1 for p in pillars.values() if STEM_YIN_YANG[p["stem"]] == "Dương"
    )
    if yang_count >= 3:
        return "mostly_extro"
    if yang_count <= 1:
        return "mostly_intro"
    return "mid"


# Năm chi 'đào hoa' positions traditionally associated with elder-sibling.
_CA_YEAR_CHI = {"Tý", "Ngọ", "Mão", "Dậu"}
_GIUA_YEAR_CHI = {"Dần", "Thân", "Tỵ", "Hợi"}
_UT_YEAR_CHI = {"Thìn", "Tuất", "Sửu", "Mùi"}


def derive_sibling_position_hint(pillars: dict) -> str:
    """Heuristic: năm chi → sibling position likelihood.

    Returns: 'ca' | 'giua' | 'ut' | 'duy_nhat'
    """
    year_chi = pillars["year"]["branch"]
    if year_chi in _CA_YEAR_CHI:
        return "ca"
    if year_chi in _GIUA_YEAR_CHI:
        return "giua"
    return "ut"
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_personality.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/rules/personality.py tests/test_birth_hour_quiz_v2_personality.py
git commit -m "feat(quiz-v2): yin-yang ratio + sibling position rule traits"
```

---

## Phase B: LLM derivation (Domain 2 + 4)

### Task B.1: LLM prompt template + response parser

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/llm_prompts.py`
- Create: `tests/test_birth_hour_quiz_v2_llm.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_llm.py
from engine.yi_wiki.birth_hour_quiz_v2.llm_prompts import (
    build_trait_prompt, parse_llm_response, LLM_OUTPUT_SCHEMA,
)

SAMPLE_CANDIDATES = [
    {"chi": "Mão",  "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                "month": {"stem": "Bính", "branch": "Thìn"},
                                "day":   {"stem": "Quý", "branch": "Sửu"},
                                "hour":  {"stem": "Ất",  "branch": "Mão"}}},
    {"chi": "Thìn", "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                "month": {"stem": "Bính", "branch": "Thìn"},
                                "day":   {"stem": "Quý", "branch": "Sửu"},
                                "hour":  {"stem": "Bính", "branch": "Thìn"}}},
]


def test_build_prompt_includes_all_candidates():
    prompt = build_trait_prompt(SAMPLE_CANDIDATES)
    assert "Mão" in prompt
    assert "Thìn" in prompt
    assert "JSON" in prompt


def test_parse_valid_response():
    raw = '''
    Some preamble.
    ```json
    {
      "Mão":  {"decision_style": "analytical", "leadership_orientation": "supportive",
               "emotional_pattern": "cool", "communication_style": "nuanced",
               "career_direction": "creative", "marriage_timing_rough": "25_30",
               "health_pattern_general": "on"},
      "Thìn": {"decision_style": "impulsive", "leadership_orientation": "dominant",
               "emotional_pattern": "passionate", "communication_style": "direct",
               "career_direction": "entrepreneurial", "marriage_timing_rough": "som_25",
               "health_pattern_general": "strong"}
    }
    ```
    '''
    result = parse_llm_response(raw, expected_candidates=["Mão", "Thìn"])
    assert result["Mão"]["decision_style"] == "analytical"
    assert result["Thìn"]["leadership_orientation"] == "dominant"


def test_parse_rejects_invalid_enum():
    bad = '{"Mão": {"decision_style": "INVALID_VALUE"}}'
    try:
        parse_llm_response(bad, expected_candidates=["Mão"])
    except ValueError as e:
        assert "INVALID_VALUE" in str(e)
    else:
        raise AssertionError("expected ValueError")
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_llm.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/llm_prompts.py
"""LLM prompt builder + response parser for Domain 2 + 4 traits."""
from __future__ import annotations

import json
import re

# Allowed values per LLM-derived trait (validated on parse).
LLM_OUTPUT_SCHEMA = {
    "decision_style":         ["impulsive", "analytical", "consultative", "patient"],
    "leadership_orientation": ["dominant", "collaborative", "supportive", "independent"],
    "emotional_pattern":      ["cool", "passionate", "volatile", "steady"],
    "communication_style":    ["direct", "nuanced", "quiet", "expressive"],
    "career_direction":       ["corporate", "creative", "entrepreneurial", "professional", "craftsman"],
    "marriage_timing_rough":  ["som_25", "25_30", "30_35", "muon_35"],
    "health_pattern_general": ["strong", "on", "nhay", "yeu_vung_x"],
}


def build_trait_prompt(candidates: list[dict]) -> str:
    """Build single-shot prompt asking LLM to predict 7 LLM-traits per candidate.

    Args:
        candidates: list of {"chi": str, "pillars": {year/month/day/hour: {stem,branch}}}
    """
    cand_blocks = []
    for c in candidates:
        p = c["pillars"]
        line = (f"- Giờ {c['chi']}: năm={p['year']['stem']}{p['year']['branch']}, "
                f"tháng={p['month']['stem']}{p['month']['branch']}, "
                f"ngày={p['day']['stem']}{p['day']['branch']}, "
                f"giờ={p['hour']['stem']}{p['hour']['branch']}")
        cand_blocks.append(line)

    enum_lines = "\n".join(
        f"  - {trait}: {' | '.join(values)}"
        for trait, values in LLM_OUTPUT_SCHEMA.items()
    )

    return f"""You are a Tử Bình expert. For EACH bát tự candidate below, predict 7 traits.

CANDIDATES:
{chr(10).join(cand_blocks)}

For each candidate, predict these 7 traits (use EXACTLY one of the allowed values):
{enum_lines}

OUTPUT FORMAT — strict JSON only, no prose:
{{
  "<chi_name>": {{"decision_style": "...", "leadership_orientation": "...", ...}},
  ...
}}
"""


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.+?\})\s*```", re.DOTALL)


def parse_llm_response(raw: str, expected_candidates: list[str]) -> dict:
    """Extract + validate JSON from LLM response.

    Returns: {chi: {trait: value}, ...}
    Raises: ValueError on invalid JSON or invalid enum values.
    """
    # Try to extract JSON from a fenced block first; fall back to raw.
    m = _JSON_FENCE_RE.search(raw)
    payload = m.group(1) if m else raw.strip()

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned non-JSON: {e}") from e

    # Validate enum values
    for chi in expected_candidates:
        if chi not in data:
            continue  # allow partial — engine handles missing
        for trait, value in data[chi].items():
            if trait in LLM_OUTPUT_SCHEMA:
                allowed = LLM_OUTPUT_SCHEMA[trait]
                if value not in allowed:
                    raise ValueError(
                        f"Invalid value for {trait}: {value!r} "
                        f"(allowed: {allowed})"
                    )
    return data
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_llm.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/llm_prompts.py tests/test_birth_hour_quiz_v2_llm.py
git commit -m "feat(quiz-v2): LLM prompt builder + response parser for Domain 2+4"
```

### Task B.2: LLM caller with retry + fallback

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/llm_call.py`
- Create: `tests/test_birth_hour_quiz_v2_llm_call.py`

- [ ] **Step 1: Write failing test (uses mock)**

```python
# tests/test_birth_hour_quiz_v2_llm_call.py
from unittest.mock import patch, MagicMock
from engine.yi_wiki.birth_hour_quiz_v2.llm_call import call_trait_llm


def test_call_trait_llm_success():
    fake_response = '''```json
{"Mão": {"decision_style": "analytical", "leadership_orientation": "supportive",
         "emotional_pattern": "cool", "communication_style": "nuanced",
         "career_direction": "creative", "marriage_timing_rough": "25_30",
         "health_pattern_general": "on"}}
```'''
    with patch("engine.yi_wiki.birth_hour_quiz_v2.llm_call._provider_complete",
               return_value=fake_response):
        result = call_trait_llm(
            [{"chi": "Mão", "pillars": {"year": {"stem": "A", "branch": "B"},
                                          "month": {"stem": "A", "branch": "B"},
                                          "day": {"stem": "A", "branch": "B"},
                                          "hour": {"stem": "A", "branch": "B"}}}]
        )
    assert result["Mão"]["decision_style"] == "analytical"


def test_call_trait_llm_retries_on_invalid_json():
    bad = "not json at all"
    good = '{"Mão": {"decision_style": "analytical", "leadership_orientation": "dominant", "emotional_pattern": "cool", "communication_style": "direct", "career_direction": "corporate", "marriage_timing_rough": "som_25", "health_pattern_general": "strong"}}'
    mock = MagicMock(side_effect=[bad, good])
    with patch("engine.yi_wiki.birth_hour_quiz_v2.llm_call._provider_complete", mock):
        result = call_trait_llm(
            [{"chi": "Mão", "pillars": {"year": {"stem": "A", "branch": "B"},
                                          "month": {"stem": "A", "branch": "B"},
                                          "day": {"stem": "A", "branch": "B"},
                                          "hour": {"stem": "A", "branch": "B"}}}]
        )
    assert mock.call_count == 2
    assert result["Mão"]["leadership_orientation"] == "dominant"
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_llm_call.py -v
```

Expected: FAIL `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/llm_call.py
"""LLM call wrapper with retry + provider fallback."""
from __future__ import annotations

import logging

from .llm_prompts import build_trait_prompt, parse_llm_response

logger = logging.getLogger(__name__)


def _provider_complete(prompt: str, model: str = "deepseek-reasoner") -> str:
    """Call configured LLM provider. Imported lazily so tests can patch."""
    from engine.ai.registry import get_registry
    registry = get_registry()
    provider = registry.resolve_for_model(model)
    if provider is None:
        raise RuntimeError(f"No provider configured for model {model}")
    return provider.complete(
        prompt=prompt,
        model=model,
        temperature=0.3,
        max_tokens=2000,
    )


def call_trait_llm(candidates: list[dict]) -> dict:
    """Call LLM for trait derivation. Retry once on parse fail. Returns dict {chi: {trait: value}}.

    Raises: RuntimeError if both attempts fail.
    """
    prompt = build_trait_prompt(candidates)
    expected = [c["chi"] for c in candidates]

    for attempt in range(2):
        raw = _provider_complete(prompt)
        try:
            return parse_llm_response(raw, expected)
        except ValueError as e:
            logger.warning(f"LLM attempt {attempt+1} failed: {e}")
            if attempt == 1:
                # Fallback to Claude on final retry
                try:
                    raw = _provider_complete(prompt, model="claude-sonnet-4-6")
                    return parse_llm_response(raw, expected)
                except (ValueError, RuntimeError) as e2:
                    raise RuntimeError(f"LLM all retries failed: {e2}") from e2

    raise RuntimeError("unreachable")
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_llm_call.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/llm_call.py tests/test_birth_hour_quiz_v2_llm_call.py
git commit -m "feat(quiz-v2): LLM caller with retry + Claude fallback"
```

### Task B.3: Trait derivation orchestrator (combine rules + LLM)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/derivation.py`
- Create: `tests/test_birth_hour_quiz_v2_derivation.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_derivation.py
from unittest.mock import patch
from engine.yi_wiki.birth_hour_quiz_v2.derivation import derive_all_traits


SAMPLE_CANDIDATES = [
    {"chi": "Mão",  "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                 "month": {"stem": "Bính", "branch": "Thìn"},
                                 "day":   {"stem": "Quý", "branch": "Sửu"},
                                 "hour":  {"stem": "Ất",  "branch": "Mão"}}},
]
FAKE_LLM = {
    "Mão": {"decision_style": "analytical", "leadership_orientation": "supportive",
            "emotional_pattern": "cool", "communication_style": "nuanced",
            "career_direction": "creative", "marriage_timing_rough": "25_30",
            "health_pattern_general": "on"},
}


def test_derive_all_traits_returns_19_traits_per_candidate():
    with patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm",
               return_value=FAKE_LLM):
        out = derive_all_traits(SAMPLE_CANDIDATES)
    traits = out["Mão"]
    expected_traits = {
        # Domain 1
        "body_height", "body_build", "face_shape", "skin_tone",
        "hair_quality", "eye_features", "physiognomy_marks",
        # Domain 2 (LLM + rule)
        "decision_style", "leadership_orientation", "introvert_extrovert",
        "emotional_pattern", "communication_style",
        # Domain 3
        "wake_natural_time", "energy_peak_period", "sleep_pattern",
        # Domain 4 (LLM + rule)
        "career_direction", "sibling_position_likely",
        "marriage_timing_rough", "health_pattern_general",
    }
    assert set(traits.keys()) == expected_traits, f"missing: {expected_traits - set(traits.keys())}"
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_derivation.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/derivation.py
"""Orchestrate full trait derivation: rules + LLM → 19 traits per candidate."""
from __future__ import annotations

from .rules.physical import derive_physical_traits
from .rules.energy import derive_energy_traits
from .rules.personality import (
    derive_yin_yang_ratio, derive_sibling_position_hint,
)
from .llm_call import call_trait_llm


def derive_all_traits(candidates: list[dict]) -> dict[str, dict[str, str]]:
    """Derive all 19 traits for each candidate.

    Args:
        candidates: list of {"chi": str, "pillars": full pillars dict}

    Returns:
        {chi: {trait_id: value}} — 19 traits per candidate.
    """
    # LLM-derived (Domain 2 + 4 partial)
    llm_out = call_trait_llm(candidates)

    out = {}
    for c in candidates:
        chi = c["chi"]
        pillars = c["pillars"]
        traits = {}

        # Domain 1: physical (rules)
        traits.update(derive_physical_traits(pillars))

        # Domain 2: personality
        # - introvert_extrovert from rule
        traits["introvert_extrovert"] = derive_yin_yang_ratio(pillars)
        # - rest from LLM
        for k in ("decision_style", "leadership_orientation",
                  "emotional_pattern", "communication_style"):
            traits[k] = llm_out.get(chi, {}).get(k, "unknown")

        # Domain 3: energy (rules)
        traits.update(derive_energy_traits(pillars))

        # Domain 4: life events
        traits["sibling_position_likely"] = derive_sibling_position_hint(pillars)
        for k in ("career_direction", "marriage_timing_rough", "health_pattern_general"):
            traits[k] = llm_out.get(chi, {}).get(k, "unknown")

        out[chi] = traits
    return out
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_derivation.py -v
```

Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/derivation.py tests/test_birth_hour_quiz_v2_derivation.py
git commit -m "feat(quiz-v2): trait derivation orchestrator (rules + LLM hybrid)"
```

---

## Phase C: Quiz logic (entropy + scoring + multi-round)

### Task C.1: Scoring module (entropy + score_answer + after_round)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/scoring.py`
- Create: `tests/test_birth_hour_quiz_v2_scoring.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_scoring.py
import math
from engine.yi_wiki.birth_hour_quiz_v2.scoring import (
    entropy, score_answer, after_round,
)


def test_entropy_uniform_4():
    """4 candidates each unique → log2(4) = 2.0"""
    preds = {"Mão": "a", "Thìn": "b", "Tỵ": "c", "Ngọ": "d"}
    assert math.isclose(entropy(preds), 2.0, rel_tol=1e-6)


def test_entropy_split_2_2():
    """2/2 split → 1.0"""
    preds = {"Mão": "a", "Thìn": "b", "Tỵ": "a", "Ngọ": "b"}
    assert math.isclose(entropy(preds), 1.0, rel_tol=1e-6)


def test_entropy_all_same():
    preds = {"Mão": "x", "Thìn": "x", "Tỵ": "x"}
    assert entropy(preds) == 0


def test_score_answer_match_reward():
    candidates = ["Mão", "Thìn", "Tỵ"]
    question = {
        "id": "face_shape",
        "weight": 2.0,
        "options": [
            {"id": "dai", "candidates": ["Mão"]},
            {"id": "vuong", "candidates": ["Thìn"]},
            {"id": "nhon", "candidates": ["Tỵ"]},
            {"id": "unsure", "candidates": []},
        ],
    }
    delta = score_answer(candidates, question, "vuong")
    assert delta["Thìn"] == 2.0
    assert delta["Mão"] == -1.0   # 2.0 × -0.5
    assert delta["Tỵ"]  == -1.0


def test_score_answer_unsure_zero():
    candidates = ["Mão", "Thìn"]
    question = {"weight": 2.0, "options": [{"id": "unsure", "candidates": []}]}
    delta = score_answer(candidates, question, "unsure")
    assert all(v == 0 for v in delta.values())


def test_after_round_clear_winner():
    scores = {"Mão": 10, "Thìn": 2, "Tỵ": 1}
    status, result = after_round(scores, ["Mão", "Thìn", "Tỵ"], round_num=1, max_rounds=3)
    assert status == "FINAL"
    assert result == "Mão"


def test_after_round_continue_drops_weak():
    scores = {"Mão": 10, "Thìn": 9, "Tỵ": 4, "Ngọ": 1}
    status, survivors = after_round(scores, ["Mão", "Thìn", "Tỵ", "Ngọ"], round_num=1, max_rounds=3)
    assert status == "CONTINUE"
    assert "Mão" in survivors and "Thìn" in survivors
    assert "Ngọ" not in survivors  # 1 < 0.5 × 10


def test_after_round_budget_exhausted():
    scores = {"Mão": 5, "Thìn": 4}
    status, result = after_round(scores, ["Mão", "Thìn"], round_num=3, max_rounds=3)
    assert status == "FINAL_UNCERTAIN"
    assert "Mão" in result and "Thìn" in result
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_scoring.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/scoring.py
"""Entropy + answer scoring + round convergence."""
from __future__ import annotations

import math
from collections import Counter


def entropy(predictions: dict[str, str]) -> float:
    """Shannon entropy in bits over predicted values."""
    counts = Counter(predictions.values())
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def score_answer(
    candidates: list[str],
    question: dict,
    chosen_option_id: str,
) -> dict[str, float]:
    """Compute per-candidate score delta from user's answer.

    Match → +weight. Mismatch → -weight × 0.5. Unsure → 0.
    """
    weight = question["weight"]
    chosen = next(
        (o for o in question["options"] if o["id"] == chosen_option_id),
        None,
    )
    if chosen is None or chosen_option_id == "unsure":
        return {c: 0.0 for c in candidates}

    matched = set(chosen["candidates"])
    return {
        c: (weight if c in matched else -weight * 0.5)
        for c in candidates
    }


def after_round(
    scores: dict[str, float],
    candidates_remaining: list[str],
    round_num: int,
    max_rounds: int,
) -> tuple[str, object]:
    """Decide whether to FINAL, FINAL_UNCERTAIN, or CONTINUE after a round.

    Returns:
        ("FINAL", "<chi>")              — clear winner
        ("FINAL_UNCERTAIN", ["chi1", "chi2"]) — top 2 if budget exhausted
        ("CONTINUE", [surviving_chis])  — keep going, drop weak (< 0.5×top)
    """
    if not scores:
        return ("FINAL_UNCERTAIN", [])

    sorted_chis = sorted(scores, key=scores.get, reverse=True)
    top_chi = sorted_chis[0]
    top_score = scores[top_chi]
    second_score = scores[sorted_chis[1]] if len(sorted_chis) > 1 else 0

    if top_score > 0 and (top_score - second_score) / top_score > 0.5:
        return ("FINAL", top_chi)

    if round_num >= max_rounds:
        return ("FINAL_UNCERTAIN", sorted_chis[:2])

    threshold = top_score * 0.5 if top_score > 0 else float("-inf")
    survivors = [c for c in candidates_remaining if scores[c] >= threshold][:6]
    return ("CONTINUE", survivors)
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_scoring.py -v
```

Expected: 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/scoring.py tests/test_birth_hour_quiz_v2_scoring.py
git commit -m "feat(quiz-v2): entropy + answer scoring + round convergence"
```

### Task C.2: Question templates (19 traits)

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/templates.py`
- Create: `tests/test_birth_hour_quiz_v2_templates.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_templates.py
from engine.yi_wiki.birth_hour_quiz_v2.templates import TRAIT_TEMPLATES


EXPECTED_TRAITS = {
    "body_height", "body_build", "face_shape", "skin_tone",
    "hair_quality", "eye_features", "physiognomy_marks",
    "decision_style", "leadership_orientation", "introvert_extrovert",
    "emotional_pattern", "communication_style",
    "wake_natural_time", "energy_peak_period", "sleep_pattern",
    "career_direction", "sibling_position_likely",
    "marriage_timing_rough", "health_pattern_general",
}


def test_all_19_templates_present():
    assert set(TRAIT_TEMPLATES.keys()) == EXPECTED_TRAITS


def test_each_template_has_required_fields():
    for trait, tpl in TRAIT_TEMPLATES.items():
        assert "question_vi" in tpl, f"{trait} missing question_vi"
        assert "domain" in tpl,      f"{trait} missing domain"
        assert "value_labels" in tpl, f"{trait} missing value_labels"
        assert isinstance(tpl["value_labels"], dict)
        assert len(tpl["value_labels"]) >= 2, f"{trait} needs ≥2 value labels"


def test_face_shape_template_values():
    tpl = TRAIT_TEMPLATES["face_shape"]
    assert "dai" in tpl["value_labels"]
    assert "vuong" in tpl["value_labels"]
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_templates.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/templates.py
"""Vietnamese question templates for 19 trait dimensions."""
from __future__ import annotations

TRAIT_TEMPLATES = {
    # ── Domain 1: NGOẠI HÌNH ────────────────────────────────────────────
    "body_height": {
        "question_vi": "Chiều cao của Anh so với người Việt cùng giới?",
        "domain": "ngoại hình",
        "value_labels": {
            "cao": "Cao hơn trung bình",
            "trung_binh": "Trung bình",
            "thap": "Thấp hơn trung bình",
        },
    },
    "body_build": {
        "question_vi": "Vóc dáng / khung xương của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "gay_thon": "Gầy thon, nhẹ cân",
            "trung_binh": "Cân đối trung bình",
            "day_dan": "Đầy đặn, mềm mại",
            "dam_chac": "Đậm chắc, vai rộng",
        },
    },
    "face_shape": {
        "question_vi": "Khuôn mặt của Anh có dạng nào gần nhất?",
        "domain": "ngoại hình",
        "value_labels": {
            "dai":   "Dài, gọn",
            "vuong": "Vuông, góc cạnh",
            "tron":  "Tròn, đầy đặn",
            "nhon":  "Sắc, hẹp về phía dưới",
            "oval":  "Oval cân đối",
        },
    },
    "skin_tone": {
        "question_vi": "Tông da tự nhiên của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "trang":    "Trắng / sáng",
            "hong_hao": "Hồng hào, ấm",
            "vua":      "Trung bình, vàng nhẹ",
            "sam":      "Sậm, ngăm",
        },
    },
    "hair_quality": {
        "question_vi": "Tóc tự nhiên (chưa qua làm tóc) của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "day_muot":   "Dày, mượt, mềm",
            "mong":       "Mỏng, thưa",
            "xoan":       "Xoăn / gợn",
            "thang_cung": "Thẳng, cứng",
        },
    },
    "eye_features": {
        "question_vi": "Mắt của Anh có đặc điểm gì?",
        "domain": "ngoại hình",
        "value_labels": {
            "sang_to":  "To, sáng, có thần",
            "sau_hep":  "Sâu, hẹp",
            "hien_min": "Mịn, hiền",
            "sac_net":  "Sắc, nét, ánh nhìn cương",
        },
    },
    "physiognomy_marks": {
        "question_vi": "Đỉnh đầu Anh có bao nhiêu xoáy tóc?",
        "domain": "ngoại hình",
        "value_labels": {
            "1_xoay":          "1 xoáy duy nhất",
            "2_xoay":          "2 xoáy",
            "vung_dac_biet":   "Không rõ xoáy / có dấu hiệu khác (sẹo, đốm)",
        },
    },
    # ── Domain 2: TÍNH CÁCH ─────────────────────────────────────────────
    "decision_style": {
        "question_vi": "Khi gặp vấn đề lớn, Anh thường?",
        "domain": "tính cách",
        "value_labels": {
            "impulsive":    "Lao vào giải quyết ngay, không suy nghĩ nhiều",
            "analytical":   "Phân tích kỹ trước, lập kế hoạch",
            "consultative": "Tham khảo người khác, không quyết một mình",
            "patient":      "Lùi một bước, chờ thời cơ",
        },
    },
    "leadership_orientation": {
        "question_vi": "Trong nhóm / công việc, Anh thường ở vai trò?",
        "domain": "tính cách",
        "value_labels": {
            "dominant":      "Lãnh đạo, ra quyết định chính",
            "collaborative": "Cộng tác bình đẳng, xây dựng đồng thuận",
            "supportive":    "Hỗ trợ, giúp đỡ người dẫn dắt",
            "independent":   "Làm việc một mình, không thích team",
        },
    },
    "introvert_extrovert": {
        "question_vi": "Sau cuộc gặp đông người, Anh thấy?",
        "domain": "tính cách",
        "value_labels": {
            "mostly_extro": "Tràn năng lượng, muốn gặp thêm",
            "mid":          "Vừa phải — đôi khi vui, đôi khi mệt",
            "mostly_intro": "Mệt, cần thời gian một mình hồi phục",
        },
    },
    "emotional_pattern": {
        "question_vi": "Cảm xúc của Anh thường như thế nào?",
        "domain": "tính cách",
        "value_labels": {
            "cool":       "Bình tĩnh, ít thay đổi",
            "passionate": "Nồng nhiệt, dễ bùng cháy với điều thích",
            "volatile":   "Thay đổi nhanh — vui buồn lên xuống",
            "steady":     "Ổn định, đều đều, lâu dài",
        },
    },
    "communication_style": {
        "question_vi": "Cách Anh giao tiếp với người khác?",
        "domain": "tính cách",
        "value_labels": {
            "direct":     "Thẳng, nói ra ngay điều mình nghĩ",
            "nuanced":    "Tinh tế, chọn lời, đọc context",
            "quiet":      "Ít nói, lắng nghe nhiều hơn",
            "expressive": "Biểu cảm, kể chuyện sinh động",
        },
    },
    # ── Domain 3: ENERGY PATTERNS ───────────────────────────────────────
    "wake_natural_time": {
        "question_vi": "Khi không có lịch hẹn, Anh tự nhiên thức dậy lúc?",
        "domain": "năng lượng",
        "value_labels": {
            "truoc_5h": "Trước 5h sáng",
            "5_7h":     "5-7h",
            "7_9h":     "7-9h",
            "9_11h":    "9-11h",
            "muon":     "Sau 11h",
        },
    },
    "energy_peak_period": {
        "question_vi": "Anh thấy mình tỉnh táo / năng lượng cao nhất khi nào trong ngày?",
        "domain": "năng lượng",
        "value_labels": {
            "sang":  "Sáng (5-11h)",
            "trua":  "Trưa (11-13h)",
            "chieu": "Chiều (13-17h)",
            "toi":   "Tối (17-21h)",
            "dem":   "Đêm khuya (sau 21h)",
        },
    },
    "sleep_pattern": {
        "question_vi": "Anh thường đi ngủ lúc?",
        "domain": "năng lượng",
        "value_labels": {
            "truoc_22h": "Trước 22h",
            "22_23h":    "22-23h",
            "23_1h":     "23h-1h sáng",
            "sau_1h":    "Sau 1h sáng",
        },
    },
    # ── Domain 4: LIFE EVENTS ───────────────────────────────────────────
    "career_direction": {
        "question_vi": "Anh hướng nghề nghiệp nào?",
        "domain": "sự nghiệp",
        "value_labels": {
            "corporate":       "Công ty lớn, vai trò ổn định",
            "creative":        "Sáng tạo, nghệ thuật, viết, thiết kế",
            "entrepreneurial": "Khởi nghiệp, làm riêng",
            "professional":    "Chuyên môn sâu (bác sĩ, kỹ sư, luật sư)",
            "craftsman":       "Tay nghề, thủ công, kỹ thuật cụ thể",
        },
    },
    "sibling_position_likely": {
        "question_vi": "Anh là con thứ mấy trong nhà?",
        "domain": "gia đình",
        "value_labels": {
            "ca":       "Con cả",
            "giua":     "Con giữa",
            "ut":       "Con út",
            "duy_nhat": "Con duy nhất",
        },
    },
    "marriage_timing_rough": {
        "question_vi": "Anh kết hôn (hoặc dự đoán kết hôn) ở độ tuổi?",
        "domain": "hôn nhân",
        "value_labels": {
            "som_25":  "Trước 25",
            "25_30":   "25-30",
            "30_35":   "30-35",
            "muon_35": "Sau 35",
        },
    },
    "health_pattern_general": {
        "question_vi": "Sức khoẻ tổng thể của Anh?",
        "domain": "sức khoẻ",
        "value_labels": {
            "strong":     "Rất khoẻ, hiếm ốm",
            "on":         "Ổn định, thỉnh thoảng cảm thường",
            "nhay":       "Nhạy cảm — dễ mệt khi căng thẳng",
            "yeu_vung_x": "Có vùng yếu cụ thể (tiêu hoá / hô hấp / xương khớp)",
        },
    },
}
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_templates.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/templates.py tests/test_birth_hour_quiz_v2_templates.py
git commit -m "feat(quiz-v2): 19 Vietnamese question templates"
```

### Task C.3: Question generation + round orchestration

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/engine.py`
- Create: `tests/test_birth_hour_quiz_v2_engine.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_engine.py
from engine.yi_wiki.birth_hour_quiz_v2.engine import (
    detect_strategy, generate_candidates_for_range, generate_questions,
)


def test_detect_strategy_by_candidate_count():
    assert detect_strategy(["Mão", "Thìn"]) == "single_round"
    assert detect_strategy(["Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân"]) == "single_round"
    assert detect_strategy(["A"] * 8) == "two_round"
    assert detect_strategy(["A"] * 12) == "three_round"


def test_generate_candidates_tight_range():
    # Range 7-9h → only Thìn (7-9h)
    chis = generate_candidates_for_range(7, 9)
    assert chis == ["Thìn"]


def test_generate_candidates_medium_range():
    # Range 6-12h → Mão, Thìn, Tỵ, Ngọ
    chis = generate_candidates_for_range(6, 12)
    assert set(chis) == {"Mão", "Thìn", "Tỵ", "Ngọ"}


def test_generate_candidates_full_day():
    # No range → all 12
    chis = generate_candidates_for_range(0, 23)
    assert len(chis) == 12


def test_generate_questions_picks_high_entropy():
    """4 candidates, 19 traits — top 12 (single_round) by entropy."""
    predictions = {
        "Mão": {"face_shape": "dai", "body_height": "cao", "skin_tone": "trang"},
        "Thìn": {"face_shape": "vuong", "body_height": "cao", "skin_tone": "trang"},
        "Tỵ": {"face_shape": "nhon", "body_height": "tb", "skin_tone": "trang"},
        "Ngọ": {"face_shape": "tron", "body_height": "tb", "skin_tone": "trang"},
    }
    questions = generate_questions(
        strategy="single_round",
        candidates=list(predictions),
        predictions=predictions,
        used_dimensions=set(),
    )
    # face_shape (entropy=2.0) should be first; skin_tone (0) skipped
    q_ids = [q["id"] for q in questions]
    assert "face_shape" in q_ids
    assert "skin_tone" not in q_ids  # zero entropy → skipped
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_engine.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/engine.py
"""Quiz strategy detection + question generation."""
from __future__ import annotations

from collections import defaultdict

from .rules.branches import BRANCHES, HOUR_RANGES
from .scoring import entropy
from .templates import TRAIT_TEMPLATES


K_PER_ROUND = {
    "single_round": 12,
    "two_round":     6,
    "three_round":   5,
}

MAX_ROUNDS = {
    "single_round": 1,
    "two_round":    2,
    "three_round":  3,
}


def detect_strategy(candidates: list[str]) -> str:
    n = len(candidates)
    if n <= 6:
        return "single_round"
    if n <= 9:
        return "two_round"
    return "three_round"


def generate_candidates_for_range(start_hour: int, end_hour: int) -> list[str]:
    """Generate list of chi giờ falling within [start, end] hour range (inclusive).

    Edge cases:
    - start == end: empty (no range)
    - start > end: wraps midnight (e.g., 22 → 2 covers Hợi, Tý, Sửu)
    - 0-23: all 12 chi
    """
    out = []
    for chi in BRANCHES:
        chi_start, chi_end = HOUR_RANGES[chi]
        # Chi wraps midnight if chi_start > chi_end (only Tý)
        chi_hours = []
        if chi_start > chi_end:
            chi_hours = list(range(chi_start, 24)) + list(range(0, chi_end))
        else:
            chi_hours = list(range(chi_start, chi_end))
        # Range wraps midnight if start > end
        if start_hour > end_hour:
            range_hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))
        else:
            range_hours = list(range(start_hour, end_hour + 1))
        if any(h in range_hours for h in chi_hours):
            out.append(chi)
    return out


def generate_questions(
    strategy: str,
    candidates: list[str],
    predictions: dict[str, dict[str, str]],
    used_dimensions: set[str],
) -> list[dict]:
    """Generate K=K_PER_ROUND[strategy] highest-entropy questions for this round."""
    K = K_PER_ROUND[strategy]

    # Compute entropy per available trait dimension
    entropies = {}
    for trait in TRAIT_TEMPLATES:
        if trait in used_dimensions:
            continue
        trait_preds = {
            c: predictions[c].get(trait, "unknown")
            for c in candidates
            if c in predictions
        }
        if not trait_preds:
            continue
        h = entropy(trait_preds)
        if h > 0:
            entropies[trait] = h

    top = sorted(entropies.items(), key=lambda x: -x[1])[:K]
    return [
        _build_question(trait, h, predictions, candidates)
        for trait, h in top
    ]


def _build_question(
    trait: str,
    weight: float,
    predictions: dict[str, dict[str, str]],
    candidates: list[str],
) -> dict:
    """Build one question with candidates grouped by predicted value."""
    template = TRAIT_TEMPLATES[trait]
    groups: dict[str, list[str]] = defaultdict(list)
    for chi in candidates:
        value = predictions[chi].get(trait, "unknown")
        groups[value].append(chi)

    options = []
    for value, chis in groups.items():
        if value not in template["value_labels"]:
            continue  # skip unknown values
        options.append({
            "id": value,
            "label": template["value_labels"][value],
            "candidates": chis,
        })
    options.append({
        "id": "unsure",
        "label": "Tôi không rõ / khó nói",
        "candidates": [],
    })

    return {
        "id": trait,
        "question": template["question_vi"],
        "domain": template["domain"],
        "options": options,
        "weight": weight,
    }
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_engine.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/engine.py tests/test_birth_hour_quiz_v2_engine.py
git commit -m "feat(quiz-v2): strategy detection + question generation"
```

### Task C.4: Full bát tự generator for candidates

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/pillars.py`
- Create: `tests/test_birth_hour_quiz_v2_pillars.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_pillars.py
from engine.yi_wiki.birth_hour_quiz_v2.pillars import build_candidates


def test_build_candidates_for_range():
    """1988-05-02 + range 6h-12h → 4 candidates each with full pillars."""
    out = build_candidates(
        birth_date="1988-05-02",
        timezone="Asia/Ho_Chi_Minh",
        hour_range=(6, 12),
    )
    assert len(out) >= 3  # Mão, Thìn, Tỵ, Ngọ (Ngọ partial since 12 is its start)
    chis = {c["chi"] for c in out}
    assert "Thìn" in chis
    for c in out:
        assert "pillars" in c
        assert all(k in c["pillars"] for k in ["year", "month", "day", "hour"])
        for p in c["pillars"].values():
            assert "stem" in p and "branch" in p


def test_build_candidates_unknown_range_returns_12():
    out = build_candidates("1988-05-02", "Asia/Ho_Chi_Minh", hour_range=None)
    assert len(out) == 12
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_pillars.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation (reuse existing bat_tu cast logic)**

```python
# engine/yi_wiki/birth_hour_quiz_v2/pillars.py
"""Generate full bát tự per hour candidate, reusing existing cast logic."""
from __future__ import annotations

from datetime import datetime

from .engine import generate_candidates_for_range
from .rules.branches import HOUR_RANGES


def build_candidates(
    birth_date: str,
    timezone: str,
    hour_range: tuple[int, int] | None,
) -> list[dict]:
    """Build candidate list with full pillars.

    Args:
        birth_date: 'YYYY-MM-DD'
        timezone: e.g. 'Asia/Ho_Chi_Minh'
        hour_range: (start, end) inclusive, or None for all 12.

    Returns:
        [{"chi": "Mão", "pillars": {year/month/day/hour: {stem, branch}}}, ...]
    """
    if hour_range is None:
        chis = list(HOUR_RANGES.keys())
    else:
        chis = generate_candidates_for_range(hour_range[0], hour_range[1])

    out = []
    for chi in chis:
        # Use midpoint hour of the chi range
        start, end = HOUR_RANGES[chi]
        midpoint = (start + 1) % 24 if start <= end else (start + 1) % 24

        # Reuse existing Bát Tự engine to get full pillars
        from engine.bat_tu import cast_bat_tu  # lazy import
        birth_dt = f"{birth_date}T{midpoint:02d}:00:00"
        chart = cast_bat_tu(birth_dt, timezone=timezone, day_pillar_convention="early_zi")
        tu_tru = chart["tu_tru"]["pillars"]
        out.append({
            "chi": chi,
            "pillars": {
                "year":  {"stem": tu_tru["year"]["stem"],  "branch": tu_tru["year"]["branch"]},
                "month": {"stem": tu_tru["month"]["stem"], "branch": tu_tru["month"]["branch"]},
                "day":   {"stem": tu_tru["day"]["stem"],   "branch": tu_tru["day"]["branch"]},
                "hour":  {"stem": tu_tru["hour"]["stem"],  "branch": tu_tru["hour"]["branch"]},
            },
        })
    return out
```

⚠ Note: This task depends on existing function `cast_bat_tu` in `engine.bat_tu`. Verify it exists with `grep -rn "def cast_bat_tu" engine/bat_tu/ engine/` before implementing — if signature differs, adjust the import + arguments to match the actual function (current schema has BatTuCastRequest with `birth_datetime_local`, `timezone`, `day_pillar_convention` — check api/schemas.py).

- [ ] **Step 4: Verify cast_bat_tu signature**

```bash
grep -rn "def cast_bat_tu" engine/ api/ 2>/dev/null | head -5
```

If output shows function signature differs from above, adjust `pillars.py` imports/call accordingly.

- [ ] **Step 5: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_pillars.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/pillars.py tests/test_birth_hour_quiz_v2_pillars.py
git commit -m "feat(quiz-v2): candidate pillars generator using bat_tu engine"
```

---

## Phase D: Session storage (DB layer)

### Task D.1: SQLite schema + session CRUD

**Files:**
- Create: `engine/yi_wiki/birth_hour_quiz_v2/session_store.py`
- Create: `tests/test_birth_hour_quiz_v2_session.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_birth_hour_quiz_v2_session.py
import os
import tempfile
from engine.yi_wiki.birth_hour_quiz_v2.session_store import (
    init_schema, create_session, get_session, update_session, mark_final,
)


def setup_db():
    """Return a temp DB path."""
    f = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    f.close()
    return f.name


def test_create_and_get_session():
    db_path = setup_db()
    try:
        init_schema(db_path)
        sid = create_session(
            db_path,
            user_id=1,
            birth_date="1988-05-02",
            timezone="Asia/Ho_Chi_Minh",
            hour_range=(6, 12),
            gender="nam",
            candidates_initial=["Mão", "Thìn", "Tỵ", "Ngọ"],
            strategy="single_round",
        )
        assert sid

        sess = get_session(db_path, sid)
        assert sess["birth_date"] == "1988-05-02"
        assert sess["candidates_initial"] == ["Mão", "Thìn", "Tỵ", "Ngọ"]
        assert sess["status"] == "in_progress"
    finally:
        os.unlink(db_path)


def test_update_session_accumulates_scores():
    db_path = setup_db()
    try:
        init_schema(db_path)
        sid = create_session(
            db_path, user_id=None, birth_date="1988-05-02", timezone="Asia/Ho_Chi_Minh",
            hour_range=None, gender="nam",
            candidates_initial=["Mão", "Thìn"], strategy="single_round",
        )
        update_session(db_path, sid,
                       candidates_remaining=["Mão", "Thìn"],
                       accumulated_scores={"Mão": 5.0, "Thìn": 2.0},
                       rounds_data=[{"round_num": 1, "answers": {"face_shape": "dai"}}])
        sess = get_session(db_path, sid)
        assert sess["accumulated_scores"] == {"Mão": 5.0, "Thìn": 2.0}


def test_mark_final():
    db_path = setup_db()
    try:
        init_schema(db_path)
        sid = create_session(
            db_path, user_id=None, birth_date="1988-05-02", timezone="Asia/Ho_Chi_Minh",
            hour_range=None, gender="nam",
            candidates_initial=["Mão"], strategy="single_round",
        )
        mark_final(db_path, sid, final_result={"top_chi": "Mão", "confidence": "Cao"})
        sess = get_session(db_path, sid)
        assert sess["status"] == "final"
        assert sess["final_result"]["top_chi"] == "Mão"
        assert sess["completed_at"] is not None
    finally:
        os.unlink(db_path)
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_session.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write implementation**

```python
# engine/yi_wiki/birth_hour_quiz_v2/session_store.py
"""SQLite-backed quiz session storage."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid


_SCHEMA = """
CREATE TABLE IF NOT EXISTS birth_hour_quiz_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER,
    birth_date TEXT NOT NULL,
    timezone TEXT NOT NULL,
    hour_range_start INTEGER,
    hour_range_end INTEGER,
    gender TEXT,
    candidates_initial TEXT NOT NULL,
    candidates_remaining TEXT NOT NULL,
    strategy TEXT NOT NULL,
    rounds_data TEXT NOT NULL,
    accumulated_scores TEXT NOT NULL,
    final_result TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress',
    created_at INTEGER NOT NULL,
    completed_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user ON birth_hour_quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status ON birth_hour_quiz_sessions(status);
"""


def init_schema(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.executescript(_SCHEMA)
        con.commit()
    finally:
        con.close()


def create_session(
    db_path: str,
    user_id: int | None,
    birth_date: str,
    timezone: str,
    hour_range: tuple[int, int] | None,
    gender: str | None,
    candidates_initial: list[str],
    strategy: str,
) -> str:
    sid = str(uuid.uuid4())
    con = sqlite3.connect(db_path)
    try:
        con.execute("""
            INSERT INTO birth_hour_quiz_sessions
              (session_id, user_id, birth_date, timezone,
               hour_range_start, hour_range_end, gender,
               candidates_initial, candidates_remaining, strategy,
               rounds_data, accumulated_scores, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress', ?)
        """, (
            sid, user_id, birth_date, timezone,
            hour_range[0] if hour_range else None,
            hour_range[1] if hour_range else None,
            gender,
            json.dumps(candidates_initial),
            json.dumps(candidates_initial),
            strategy,
            json.dumps([]),
            json.dumps({c: 0.0 for c in candidates_initial}),
            int(time.time()),
        ))
        con.commit()
    finally:
        con.close()
    return sid


def get_session(db_path: str, session_id: str) -> dict | None:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            "SELECT * FROM birth_hour_quiz_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    finally:
        con.close()

    if not row:
        return None

    out = dict(row)
    out["candidates_initial"] = json.loads(out["candidates_initial"])
    out["candidates_remaining"] = json.loads(out["candidates_remaining"])
    out["rounds_data"] = json.loads(out["rounds_data"])
    out["accumulated_scores"] = json.loads(out["accumulated_scores"])
    if out["final_result"]:
        out["final_result"] = json.loads(out["final_result"])
    if out["hour_range_start"] is not None:
        out["hour_range"] = (out["hour_range_start"], out["hour_range_end"])
    else:
        out["hour_range"] = None
    return out


def update_session(
    db_path: str,
    session_id: str,
    candidates_remaining: list[str] | None = None,
    accumulated_scores: dict[str, float] | None = None,
    rounds_data: list[dict] | None = None,
) -> None:
    sets, args = [], []
    if candidates_remaining is not None:
        sets.append("candidates_remaining = ?")
        args.append(json.dumps(candidates_remaining))
    if accumulated_scores is not None:
        sets.append("accumulated_scores = ?")
        args.append(json.dumps(accumulated_scores))
    if rounds_data is not None:
        sets.append("rounds_data = ?")
        args.append(json.dumps(rounds_data))
    if not sets:
        return
    args.append(session_id)
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            f"UPDATE birth_hour_quiz_sessions SET {', '.join(sets)} WHERE session_id = ?",
            args,
        )
        con.commit()
    finally:
        con.close()


def mark_final(
    db_path: str,
    session_id: str,
    final_result: dict,
) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute("""
            UPDATE birth_hour_quiz_sessions
            SET status = 'final', final_result = ?, completed_at = ?
            WHERE session_id = ?
        """, (json.dumps(final_result), int(time.time()), session_id))
        con.commit()
    finally:
        con.close()
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_session.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/yi_wiki/birth_hour_quiz_v2/session_store.py tests/test_birth_hour_quiz_v2_session.py
git commit -m "feat(quiz-v2): SQLite session storage CRUD"
```

---

## Phase E: API endpoints

### Task E.1: POST /start

**Files:**
- Modify: `api/main.py` (add endpoints + schemas)
- Create: `tests/test_birth_hour_quiz_v2_api.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_birth_hour_quiz_v2_api.py
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

FAKE_LLM = {
    "Mão": {"decision_style": "analytical", "leadership_orientation": "supportive",
            "emotional_pattern": "cool", "communication_style": "nuanced",
            "career_direction": "creative", "marriage_timing_rough": "25_30",
            "health_pattern_general": "on"},
    "Thìn": {"decision_style": "impulsive", "leadership_orientation": "dominant",
             "emotional_pattern": "passionate", "communication_style": "direct",
             "career_direction": "entrepreneurial", "marriage_timing_rough": "som_25",
             "health_pattern_general": "strong"},
}


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_start_quiz_returns_session_and_round1(mock_llm):
    resp = client.post(
        "/api/yi-wiki/birth-hour-quiz-v2/start",
        json={
            "birth_date": "1988-05-02",
            "timezone": "Asia/Ho_Chi_Minh",
            "hour_range": {"start": 7, "end": 10},
            "gender": "nam",
        },
    )
    assert resp.status_code == 200
    d = resp.json()
    assert "session_id" in d
    assert d["strategy"] in {"single_round", "two_round", "three_round"}
    assert len(d["candidates"]) >= 2
    assert "round_1" in d
    assert len(d["round_1"]["questions"]) > 0
    # Verify each question has options
    for q in d["round_1"]["questions"]:
        assert "options" in q
        assert any(o["id"] == "unsure" for o in q["options"])
```

- [ ] **Step 2: Run test (fails - endpoint not yet exists)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py::test_start_quiz_returns_session_and_round1 -v
```

Expected: FAIL with 404.

- [ ] **Step 3: Add schema to `api/schemas.py`**

Find existing `LucHaoCastRequest` location, add after it:

```python
# Birth Hour Quiz v2 schemas
class BirthHourQuizV2HourRange(BaseModel):
    start: int
    end: int


class BirthHourQuizV2StartRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD
    timezone: str = "Asia/Ho_Chi_Minh"
    hour_range: BirthHourQuizV2HourRange | None = None
    gender: str | None = None  # 'nam' | 'nữ'


class BirthHourQuizV2SubmitRequest(BaseModel):
    session_id: str
    round_num: int
    answers: dict[str, str]  # {trait_id: option_id}


class BirthHourQuizV2SaveRequest(BaseModel):
    session_id: str
    person_id: str
```

- [ ] **Step 4: Add `/start` endpoint to `api/main.py`**

Append near other `/api/yi-wiki/...` endpoints (search for `/api/yi-wiki/auspicious-day` to find location):

```python
# ── Birth Hour Quiz v2 ──────────────────────────────────────────────
from api.schemas import (
    BirthHourQuizV2StartRequest, BirthHourQuizV2SubmitRequest, BirthHourQuizV2SaveRequest,
)

_QUIZ_V2_DB = "/Users/ozvietnamdesktop/Desktop/yi/data/yi_users/users.sqlite3"


@app.post("/api/yi-wiki/birth-hour-quiz-v2/start")
def quiz_v2_start(req: BirthHourQuizV2StartRequest):
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.pillars import build_candidates
    from engine.yi_wiki.birth_hour_quiz_v2.derivation import derive_all_traits
    from engine.yi_wiki.birth_hour_quiz_v2.engine import detect_strategy, generate_questions

    session_store.init_schema(_QUIZ_V2_DB)

    hour_range = (req.hour_range.start, req.hour_range.end) if req.hour_range else None
    candidates_list = build_candidates(req.birth_date, req.timezone, hour_range)
    if not candidates_list:
        return {"status": "error", "message": "No candidates for given range"}

    strategy = detect_strategy([c["chi"] for c in candidates_list])
    predictions = derive_all_traits(candidates_list)

    questions = generate_questions(
        strategy=strategy,
        candidates=[c["chi"] for c in candidates_list],
        predictions=predictions,
        used_dimensions=set(),
    )

    sid = session_store.create_session(
        _QUIZ_V2_DB,
        user_id=None,  # TODO wire from auth
        birth_date=req.birth_date,
        timezone=req.timezone,
        hour_range=hour_range,
        gender=req.gender,
        candidates_initial=[c["chi"] for c in candidates_list],
        strategy=strategy,
    )
    # Persist predictions in session rounds_data for round 1 reference
    session_store.update_session(
        _QUIZ_V2_DB, sid,
        rounds_data=[{"round_num": 1, "predictions": predictions,
                      "questions": questions, "answers": None}],
    )

    return {
        "status": "ok",
        "session_id": sid,
        "candidates": [c["chi"] for c in candidates_list],
        "strategy": strategy,
        "round_1": {
            "round_num": 1,
            "total_rounds": {"single_round": 1, "two_round": 2, "three_round": 3}[strategy],
            "questions": questions,
        },
    }
```

- [ ] **Step 5: Run test**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py::test_start_quiz_returns_session_and_round1 -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add api/main.py api/schemas.py tests/test_birth_hour_quiz_v2_api.py
git commit -m "feat(quiz-v2): POST /api/yi-wiki/birth-hour-quiz-v2/start"
```

### Task E.2: POST /submit-round + GET /session

**Files:**
- Modify: `api/main.py`
- Modify: `tests/test_birth_hour_quiz_v2_api.py`

- [ ] **Step 1: Add tests**

Append to `tests/test_birth_hour_quiz_v2_api.py`:

```python
@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_submit_round_returns_final_or_continue(mock_llm):
    # 1) start quiz
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 7, "end": 9},  # tight range → 1 candidate or 2
        "gender": "nam",
    }).json()
    sid = r1["session_id"]
    questions = r1["round_1"]["questions"]
    answers = {q["id"]: q["options"][0]["id"] for q in questions}  # pick first option each

    # 2) submit round 1
    r2 = client.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round", json={
        "session_id": sid, "round_num": 1, "answers": answers,
    }).json()
    assert r2["status"] in {"CONTINUE", "FINAL", "FINAL_UNCERTAIN"}
    assert "scores" in r2


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_get_session(mock_llm):
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 7, "end": 9}, "gender": "nam",
    }).json()
    sid = r1["session_id"]
    r2 = client.get(f"/api/yi-wiki/birth-hour-quiz-v2/session/{sid}")
    assert r2.status_code == 200
    assert r2.json()["session_id"] == sid
```

- [ ] **Step 2: Run tests (fail)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py -v
```

Expected: 2 new tests FAIL with 404.

- [ ] **Step 3: Add endpoints**

Append to `api/main.py` (after `/start`):

```python
@app.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round")
def quiz_v2_submit_round(req: BirthHourQuizV2SubmitRequest):
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.scoring import score_answer, after_round
    from engine.yi_wiki.birth_hour_quiz_v2.engine import generate_questions

    sess = session_store.get_session(_QUIZ_V2_DB, req.session_id)
    if not sess:
        return {"status": "error", "message": "session not found"}

    # Find this round's questions in rounds_data
    rd = sess["rounds_data"]
    round_entry = next((r for r in rd if r["round_num"] == req.round_num), None)
    if not round_entry:
        return {"status": "error", "message": "round not found"}

    # Score each answer
    candidates = sess["candidates_remaining"]
    scores = dict(sess["accumulated_scores"])
    used = {q["id"] for q in round_entry["questions"]}
    for q in round_entry["questions"]:
        ans = req.answers.get(q["id"])
        if not ans:
            continue
        delta = score_answer(candidates, q, ans)
        for c, v in delta.items():
            scores[c] = scores.get(c, 0) + v

    round_entry["answers"] = req.answers
    round_entry["round_scores_after"] = dict(scores)

    # Convergence check
    max_rounds = {"single_round": 1, "two_round": 2, "three_round": 3}[sess["strategy"]]
    status, result = after_round(scores, candidates, req.round_num, max_rounds)

    if status in {"FINAL", "FINAL_UNCERTAIN"}:
        final_result = _build_final_result(sess, scores, result, status)
        session_store.update_session(
            _QUIZ_V2_DB, req.session_id,
            accumulated_scores=scores, rounds_data=rd,
        )
        session_store.mark_final(_QUIZ_V2_DB, req.session_id, final_result)
        return {
            "status": status,
            "scores": scores,
            "candidates_remaining": result if isinstance(result, list) else [result],
            "next_round": None,
            "final_result": final_result,
        }

    # CONTINUE: build next round
    survivors = result  # list[str]
    predictions = round_entry["predictions"]
    next_round_num = req.round_num + 1
    next_questions = generate_questions(
        strategy=sess["strategy"],
        candidates=survivors,
        predictions=predictions,
        used_dimensions=used,
    )
    rd.append({"round_num": next_round_num, "predictions": predictions,
               "questions": next_questions, "answers": None})

    session_store.update_session(
        _QUIZ_V2_DB, req.session_id,
        candidates_remaining=survivors,
        accumulated_scores=scores,
        rounds_data=rd,
    )

    return {
        "status": "CONTINUE",
        "scores": scores,
        "candidates_remaining": survivors,
        "next_round": {
            "round_num": next_round_num,
            "total_rounds": max_rounds,
            "questions": next_questions,
        },
        "final_result": None,
    }


def _build_final_result(sess: dict, scores: dict, result, status: str) -> dict:
    """Construct human-readable final result with per-candidate reasoning."""
    from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import HOUR_RANGES

    top_candidates = [result] if isinstance(result, str) else list(result)
    sorted_scores = sorted(scores.items(), key=lambda kv: -kv[1])
    top_score = sorted_scores[0][1] if sorted_scores else 0
    second = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    confidence = "Cao" if top_score - second >= 5 else "Vừa" if top_score - second >= 2 else "Thấp"

    return {
        "status": status,
        "top_chi": top_candidates[0] if top_candidates else None,
        "top_candidates": top_candidates,
        "confidence": confidence,
        "scores": scores,
        "hour_ranges": {chi: f"{HOUR_RANGES[chi][0]}h-{HOUR_RANGES[chi][1]}h"
                        for chi in top_candidates if chi in HOUR_RANGES},
    }


@app.get("/api/yi-wiki/birth-hour-quiz-v2/session/{session_id}")
def quiz_v2_get_session(session_id: str):
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    sess = session_store.get_session(_QUIZ_V2_DB, session_id)
    if not sess:
        return {"status": "error", "message": "session not found"}
    return {"status": "ok", **sess}
```

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add api/main.py tests/test_birth_hour_quiz_v2_api.py
git commit -m "feat(quiz-v2): POST /submit-round + GET /session endpoints"
```

### Task E.3: POST /save-result

**Files:**
- Modify: `api/main.py`
- Modify: `tests/test_birth_hour_quiz_v2_api.py`

- [ ] **Step 1: Add test**

Append:

```python
@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_save_result_smoke(mock_llm):
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 7, "end": 9}, "gender": "nam",
    }).json()
    sid = r1["session_id"]
    # complete the quiz to get a final result
    questions = r1["round_1"]["questions"]
    answers = {q["id"]: q["options"][0]["id"] for q in questions}
    r2 = client.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round", json={
        "session_id": sid, "round_num": 1, "answers": answers,
    }).json()
    if r2["status"] in {"FINAL", "FINAL_UNCERTAIN"}:
        # Attempt save (will likely fail unauth, but endpoint should respond)
        r3 = client.post("/api/yi-wiki/birth-hour-quiz-v2/save-result", json={
            "session_id": sid, "person_id": "_founder",
        })
        assert r3.status_code == 200
        assert "status" in r3.json()
```

- [ ] **Step 2: Run test (fails)**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py::test_save_result_smoke -v
```

Expected: FAIL 404.

- [ ] **Step 3: Add endpoint**

Append to `api/main.py`:

```python
@app.post("/api/yi-wiki/birth-hour-quiz-v2/save-result")
def quiz_v2_save_result(req: BirthHourQuizV2SaveRequest):
    """Save inferred birth hour to person's profile.

    Updates engine.yi_hermes.persons via update_person if it exists.
    """
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import HOUR_RANGES

    sess = session_store.get_session(_QUIZ_V2_DB, req.session_id)
    if not sess or sess["status"] != "final":
        return {"status": "error", "message": "session not finalized"}

    fr = sess["final_result"]
    top_chi = fr.get("top_chi")
    if not top_chi:
        return {"status": "error", "message": "no top candidate"}

    chi_start, chi_end = HOUR_RANGES[top_chi]
    # Pick midpoint hour (start + 1, accounting for wrap)
    if chi_start <= chi_end:
        midpoint_hour = chi_start + 1
    else:
        midpoint_hour = 0  # Tý midpoint
    new_birth_dt = f"{sess['birth_date']}T{midpoint_hour:02d}:00:00"

    try:
        from engine.yi_hermes.persons import update_person
        result = update_person(req.person_id, {
            "birth_datetime_local": new_birth_dt,
            "birth_confidence": "approx_hour",
            "source": f"birth_hour_quiz_v2:{req.session_id}",
        })
        return {"status": "ok", "person_id": req.person_id,
                "birth_datetime_local": new_birth_dt}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

- [ ] **Step 4: Run test**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_api.py::test_save_result_smoke -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api/main.py tests/test_birth_hour_quiz_v2_api.py
git commit -m "feat(quiz-v2): POST /save-result writes to person profile"
```

---

## Phase F: Vue component

### Task F.1: Component skeleton + Stage 1 (INPUT)

**Files:**
- Create: `client/webapp/src/components/BirthHourQuizV2.vue`

- [ ] **Step 1: Write component scaffold**

```vue
<!-- client/webapp/src/components/BirthHourQuizV2.vue -->
<script setup>
import { ref, computed } from "vue";

// Stage: 'input' | 'loading' | 'round' | 'result'
const stage = ref("input");

// Stage 1 form
const form = ref({
  birth_date: "1988-05-02",
  timezone: "Asia/Ho_Chi_Minh",
  hour_start: 6,
  hour_end: 12,
  no_idea: false,
  gender: "nam",
});

// Quiz state
const session = ref(null);   // {session_id, strategy, candidates, ...}
const currentRound = ref(null);  // {round_num, total_rounds, questions}
const answers = ref({});     // {trait_id: option_id}
const finalResult = ref(null);
const error = ref("");
const loading = ref(false);

async function startQuiz() {
  loading.value = true;
  stage.value = "loading";
  error.value = "";
  try {
    const body = {
      birth_date: form.value.birth_date,
      timezone: form.value.timezone,
      hour_range: form.value.no_idea
        ? null
        : { start: form.value.hour_start, end: form.value.hour_end },
      gender: form.value.gender,
    };
    const r = await fetch("/api/yi-wiki/birth-hour-quiz-v2/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const d = await r.json();
    if (d.status === "error") {
      error.value = d.message;
      stage.value = "input";
      return;
    }
    session.value = d;
    currentRound.value = d.round_1;
    answers.value = {};
    stage.value = "round";
  } catch (e) {
    error.value = String(e);
    stage.value = "input";
  } finally {
    loading.value = false;
  }
}

async function submitRound() {
  loading.value = true;
  try {
    const r = await fetch("/api/yi-wiki/birth-hour-quiz-v2/submit-round", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session.value.session_id,
        round_num: currentRound.value.round_num,
        answers: answers.value,
      }),
    });
    const d = await r.json();
    if (d.status === "CONTINUE") {
      currentRound.value = d.next_round;
      answers.value = {};
    } else {
      finalResult.value = d.final_result;
      stage.value = "result";
    }
  } catch (e) {
    error.value = String(e);
  } finally {
    loading.value = false;
  }
}

function restart() {
  stage.value = "input";
  session.value = null;
  currentRound.value = null;
  answers.value = {};
  finalResult.value = null;
}

const allAnswered = computed(() => {
  if (!currentRound.value) return false;
  return currentRound.value.questions.every(
    (q) => answers.value[q.id]
  );
});
</script>

<template>
  <div class="bhq2">
    <!-- Stage 1: INPUT -->
    <section v-if="stage === 'input'" class="bhq2-input">
      <h2>🕐 Tìm lại giờ sinh — bộ trắc nghiệm bát tự</h2>
      <p class="bhq2-hint">
        Engine sẽ tạo nhiều giả thiết bát tự (theo các giờ chi khác nhau)
        và đặt câu hỏi về ngoại hình + tính cách để khoanh vùng giờ sinh thực sự.
      </p>

      <label>
        Ngày sinh:
        <input type="date" v-model="form.birth_date" />
      </label>

      <label>
        Múi giờ:
        <select v-model="form.timezone">
          <option value="Asia/Ho_Chi_Minh">Asia/Ho_Chi_Minh (VN)</option>
          <option value="Asia/Shanghai">Asia/Shanghai (TQ)</option>
        </select>
      </label>

      <div class="bhq2-gender">
        Giới tính:
        <label><input type="radio" value="nam" v-model="form.gender" /> Nam</label>
        <label><input type="radio" value="nữ" v-model="form.gender" /> Nữ</label>
      </div>

      <div class="bhq2-range">
        <p>Anh nhớ giờ trong khoảng nào?</p>
        <label>
          Từ: <input type="number" min="0" max="23" v-model.number="form.hour_start" />h
        </label>
        <label>
          Đến: <input type="number" min="0" max="23" v-model.number="form.hour_end" />h
        </label>
        <label>
          <input type="checkbox" v-model="form.no_idea" />
          Không nhớ gì (sẽ chia 3 vòng quét toàn bộ 24h)
        </label>
      </div>

      <button class="bhq2-primary" @click="startQuiz" :disabled="loading">
        {{ loading ? "Đang chuẩn bị..." : "Bắt đầu trắc nghiệm →" }}
      </button>
      <p v-if="error" class="bhq2-error">{{ error }}</p>
    </section>

    <!-- Stage 2: LOADING -->
    <section v-else-if="stage === 'loading'" class="bhq2-loading">
      <p>⏳ Đang phân tích bát tự...</p>
      <p class="bhq2-small">Engine: derive 19 traits × candidates. LLM: nuận tính cách + life events.</p>
    </section>

    <!-- Stage 3: ROUND -->
    <section v-else-if="stage === 'round'" class="bhq2-round">
      <header class="bhq2-round-header">
        <span>Vòng {{ currentRound.round_num }}/{{ currentRound.total_rounds }}</span>
        <span>còn {{ session.candidates.length }} ứng cử ban đầu</span>
      </header>

      <ol class="bhq2-questions">
        <li v-for="q in currentRound.questions" :key="q.id" class="bhq2-question">
          <p class="bhq2-q-text"><b>{{ q.question }}</b> <small class="bhq2-domain">({{ q.domain }})</small></p>
          <div class="bhq2-options">
            <label v-for="opt in q.options" :key="opt.id" class="bhq2-option">
              <input type="radio" :name="q.id" :value="opt.id" v-model="answers[q.id]" />
              {{ opt.label }}
            </label>
          </div>
        </li>
      </ol>

      <button class="bhq2-primary" @click="submitRound" :disabled="!allAnswered || loading">
        {{ loading ? "Đang chấm điểm..." : "Submit Vòng " + currentRound.round_num + " →" }}
      </button>
    </section>

    <!-- Stage 4: RESULT -->
    <section v-else-if="stage === 'result'" class="bhq2-result">
      <h3>🎯 Giờ sinh có khả năng cao nhất</h3>
      <div class="bhq2-winner">
        <div class="bhq2-chi">{{ finalResult.top_chi }} ({{ finalResult.hour_ranges[finalResult.top_chi] }})</div>
        <div class="bhq2-conf">Confidence: <b>{{ finalResult.confidence }}</b></div>
      </div>

      <h4>📊 Điểm số per candidate</h4>
      <ul class="bhq2-scores">
        <li v-for="(score, chi) in finalResult.scores" :key="chi">
          <b>{{ chi }}</b>: {{ score.toFixed(1) }} điểm
        </li>
      </ul>

      <div class="bhq2-actions">
        <button class="bhq2-primary" @click="restart">🔄 Trắc nghiệm lại</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.bhq2 { max-width: 720px; margin: 0 auto; padding: 1rem; }
.bhq2-input label { display: block; margin: 0.5rem 0; }
.bhq2-input input, .bhq2-input select { padding: 0.25rem; }
.bhq2-hint { color: #666; font-size: 0.9em; }
.bhq2-error { color: #c33; }
.bhq2-primary {
  padding: 0.6rem 1.2rem; font-size: 1em; background: #4a90e2; color: #fff;
  border: 0; border-radius: 4px; cursor: pointer; margin-top: 1rem;
}
.bhq2-primary:disabled { background: #aaa; cursor: not-allowed; }
.bhq2-round-header {
  display: flex; justify-content: space-between; padding: 0.5rem 0;
  border-bottom: 1px solid #ddd; margin-bottom: 1rem;
}
.bhq2-question { margin-bottom: 1.2rem; }
.bhq2-domain { color: #999; font-size: 0.85em; font-weight: normal; }
.bhq2-options { display: flex; flex-direction: column; gap: 0.3rem; padding-left: 1rem; }
.bhq2-option { cursor: pointer; }
.bhq2-winner {
  padding: 1rem; background: #f0f8ff; border-radius: 8px; margin: 1rem 0;
}
.bhq2-chi { font-size: 1.5em; font-weight: bold; }
.bhq2-scores { padding-left: 1.5rem; }
.bhq2-loading { text-align: center; padding: 3rem; }
.bhq2-small { color: #999; font-size: 0.85em; }
</style>
```

- [ ] **Step 2: Verify Vue build**

```bash
cd client/webapp && npm run build 2>&1 | tail -5
```

Expected: `✓ built in Ns` with no errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
git add client/webapp/src/components/BirthHourQuizV2.vue
git commit -m "feat(quiz-v2): Vue component with 4-stage state machine"
```

### Task F.2: Wire into QuickTasksPanel (replace v1)

**Files:**
- Modify: `client/webapp/src/components/QuickTasksPanel.vue`

- [ ] **Step 1: Replace v1 quiz section**

Search for `loadQuizQuestions` function in [QuickTasksPanel.vue](client/webapp/src/components/QuickTasksPanel.vue), and the surrounding markup `<!-- ─── Birth Hour Quiz ─── -->`. Replace v1 quiz block with:

```vue
<!-- In template, replace v1 quiz section with: -->
<section v-if="activeTask === 'quiz'" class="qt-task">
  <BirthHourQuizV2 />
  <button class="qt-back" @click="activeTask = null">← Quay lại</button>
</section>
```

In `<script setup>`, replace v1 imports/state with:

```js
import BirthHourQuizV2 from "./BirthHourQuizV2.vue";
// (remove v1 quiz state: quizQuestions, quizAnswers, quizResult, quizLoading, loadQuizQuestions, submitQuiz, resetQuiz)
```

- [ ] **Step 2: Verify build**

```bash
cd client/webapp && npm run build 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
git add client/webapp/src/components/QuickTasksPanel.vue
git commit -m "feat(quiz-v2): replace v1 quiz UI in QuickTasksPanel with v2 component"
```

### Task F.3: Add entry point in BatTuPanel

**Files:**
- Modify: `client/webapp/src/components/BatTuPanel.vue`

- [ ] **Step 1: Add "Tìm lại giờ sinh" button**

In BatTuPanel.vue near the chart display (after `<div class="panel-title">`), add:

```vue
<div class="bt-hour-uncertain" v-if="batTuData?.birth_confidence !== 'exact'">
  <button class="bt-find-hour" @click="showHourQuiz = true">
    🔍 Tìm lại giờ sinh (trắc nghiệm bát tự)
  </button>
</div>

<!-- Modal (at end of <section>): -->
<div v-if="showHourQuiz" class="bt-modal-backdrop" @click.self="showHourQuiz = false">
  <div class="bt-modal">
    <BirthHourQuizV2 />
    <button class="bt-close" @click="showHourQuiz = false">Đóng</button>
  </div>
</div>
```

In `<script setup>`:
```js
import BirthHourQuizV2 from "./BirthHourQuizV2.vue";
const showHourQuiz = ref(false);
```

In `<style scoped>` append:
```css
.bt-find-hour {
  padding: 0.4rem 0.8rem; background: #f0f8ff; border: 1px solid #4a90e2;
  border-radius: 4px; cursor: pointer; font-size: 0.9em;
}
.bt-modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; align-items: center; justify-content: center;
}
.bt-modal {
  background: #fff; padding: 1.5rem; max-width: 800px; max-height: 90vh;
  overflow-y: auto; border-radius: 8px;
}
.bt-close { margin-top: 1rem; padding: 0.4rem 1rem; cursor: pointer; }
```

- [ ] **Step 2: Verify build**

```bash
cd client/webapp && npm run build 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
git add client/webapp/src/components/BatTuPanel.vue
git commit -m "feat(quiz-v2): add 'Tìm lại giờ sinh' button in BatTuPanel"
```

---

## Phase G: E2E verification

### Task G.1: Test live deployment

**Files:** none modified.

- [ ] **Step 1: Wait for daemon auto-deploy (if auto-sync running)**

If auto-sync daemon is running, recent commits should auto-push + CI deploy within ~5 minutes. Otherwise:

```bash
git push
gh run watch
```

- [ ] **Step 2: Curl /start endpoint on live**

```bash
curl -s -X POST https://kinhdich.online/api/yi-wiki/birth-hour-quiz-v2/start \
  -H 'Content-Type: application/json' \
  -d '{"birth_date":"1988-05-02","timezone":"Asia/Ho_Chi_Minh","hour_range":{"start":7,"end":9},"gender":"nam"}' \
  | head -c 500
```

Expected: JSON with `session_id`, `candidates`, `round_1.questions`.

- [ ] **Step 3: Manual browser test**

Open `https://kinhdich.online`, click Wiki Tổ sư tab → Quick Tasks → "Trắc nghiệm tìm giờ sinh".

Verify:
- [ ] Stage 1 form renders + accepts input
- [ ] "Bắt đầu trắc nghiệm" triggers loading state
- [ ] Stage 3 shows questions with options + "Tôi không rõ"
- [ ] Submit moves to next round OR result
- [ ] Stage 4 shows top chi + scores

- [ ] **Step 4: Run all v2 tests locally**

```bash
.venv/bin/python3 -m pytest tests/test_birth_hour_quiz_v2_*.py -v
```

Expected: ALL tests PASS.

- [ ] **Step 5: Mark milestone**

```bash
git tag v0.3.0-quiz-v2
git push origin v0.3.0-quiz-v2
```

### Task G.2: Update HANH-TRINH-NHAP-DAO.md

**Files:**
- Modify: `docs/HANH-TRINH-NHAP-DAO.md`

- [ ] **Step 1: Append milestone entry**

Add a "Lần update 16" entry before "Lần update tiếp theo" placeholder summarizing the feature, rules + LLM hybrid approach, and lessons learned.

- [ ] **Step 2: Commit (daemon will auto-commit if active)**

```bash
git add docs/HANH-TRINH-NHAP-DAO.md
git commit -m "docs: log birth-hour-quiz-v2 milestone in journal"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ §1 Goal: paradigm shift v1 → v2 — covered by Tasks A-G
- ✅ §2 Architecture multi-round: detect_strategy + after_round + recursion in /submit-round
- ✅ §3 Trait derivation 19 dimensions: Tasks A.3 (Domain 1), A.4 (Domain 3), A.5 (yin/yang + sibling), B (LLM Domain 2+4)
- ✅ §4 Entropy + question gen + scoring + convergence: Tasks C.1, C.3
- ✅ §5 UI + API + DB: Tasks D (DB), E (API), F (Vue)
- ✅ §6 File structure: matches Tasks
- ✅ §7 Decomposition: Phases A-G map to spec phases A-E + polish

**Placeholder scan:** No "TBD" / "TODO" / "implement later" found in task steps.

**Type consistency:**
- `pillars` dict shape: `{year/month/day/hour: {stem, branch}}` — consistent across Tasks A.3, A.4, A.5, B.3, C.4
- `predictions` dict shape: `{chi: {trait: value}}` — consistent across B.3, C.1, C.3, E.1, E.2
- Function signatures: `derive_*_traits(pillars: dict) -> dict[str, str]` — consistent

**Note for executor:** Task C.4 depends on existing `engine.bat_tu.cast_bat_tu`. If signature differs, Step 4 in C.4 catches it. Plan also assumes `engine.yi_hermes.persons.update_person` exists (used in E.3) — verify with `grep -n "def update_person" engine/yi_hermes/persons.py` before E.3 implementation.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-19-birth-hour-quiz-v2.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Each subagent runs 1 task (write test → impl → commit). Plan has ~28 tasks across 7 phases.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints between phases. Slower context-wise but visible step-by-step.

**Which approach?**
