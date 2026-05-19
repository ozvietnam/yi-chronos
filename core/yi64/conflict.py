from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConflictType(str, Enum):
    GENERATION = "generation_conflict"
    DERIVATION = "derivation_conflict"
    INTERPRETATION = "interpretation_conflict"


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConflictMode(str, Enum):
    SINGLE_SCHOOL = "single_school_mode"
    PARALLEL_SCHOOL = "parallel_school_mode"
    CONSENSUS_HINT = "consensus_hint_mode"


@dataclass(frozen=True)
class ConflictMeta:
    conflict_type: ConflictType
    severity: ConflictSeverity
    methods_involved: tuple[str, ...]
    summary: str
