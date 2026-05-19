from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Polarity(str, Enum):
    YIN = "yin"
    YANG = "yang"


class MotionState(str, Enum):
    STATIC = "static"
    MOVING = "moving"


class MethodFamily(str, Enum):
    RANDOMIZED_RITUAL = "randomized_ritual"
    TIME_SPACE_MAPPED = "time_space_mapped"
    SYMBOLIC_DERIVED = "symbolic_derived"


@dataclass(frozen=True)
class HexagramIdentity:
    king_wen_index: int
    binary_code: str
    name_vi: str
    upper_trigram: str
    lower_trigram: str


@dataclass(frozen=True)
class LineState:
    line_position: int
    polarity: Polarity
    motion: MotionState
    origin_value: int | None = None


@dataclass(frozen=True)
class PrimaryHexagram:
    hexagram_identity: HexagramIdentity
    line_states: tuple[LineState, ...]
    moving_lines: tuple[int, ...]


@dataclass(frozen=True)
class TransformRule:
    rule_id: str
    description: str
    version: str
    deterministic: bool = True


@dataclass(frozen=True)
class DerivedHexagrams:
    transformed_hexagram: HexagramIdentity | None = None
    nuclear_hexagram: HexagramIdentity | None = None
    context_hexagrams: tuple[HexagramIdentity, ...] = ()


@dataclass(frozen=True)
class ContextVector:
    datetime_local: str
    timezone: str
    question_text: str = ""
    question_domain: str = ""
    calendar_mode: str = "solar"
    school_constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodProfileRef:
    method_id: str
    method_family: MethodFamily
    school_id: str
    ruleset_id: str
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class StageTrace:
    stage_name: str
    inputs_summary: dict[str, Any]
    outputs_summary: dict[str, Any]
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    steps: tuple[StageTrace, ...]
    inputs_snapshot: dict[str, Any]
    intermediate_values: dict[str, Any] = field(default_factory=dict)
    decisions: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConfidenceEnvelope:
    rule_confidence: float
    source_confidence: float
    input_confidence: float
    interpretation_confidence: float | None = None


@dataclass(frozen=True)
class NormalizedRequest:
    context_vector: ContextVector
    method_profile_ref: MethodProfileRef
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedResult:
    primary_hexagram: PrimaryHexagram
    derived_hexagrams: DerivedHexagrams
    trace_record: TraceRecord
    confidence_envelope: ConfidenceEnvelope
    method_profile_ref: MethodProfileRef
