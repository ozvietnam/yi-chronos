from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .model import (
    ConfidenceEnvelope,
    DerivedHexagrams,
    LineState,
    MethodProfileRef,
    MotionState,
    NormalizedRequest,
    NormalizedResult,
    Polarity,
    PrimaryHexagram,
    StageTrace,
    TraceRecord,
    TransformRule,
)
from .registry import MethodRegistry
from .transforms import (
    binary_to_hexagram_identity,
    line_flip_transform,
    lines_to_binary,
    moving_lines_from_states,
)


class Yi64PipelineError(RuntimeError):
    pass


@dataclass
class Yi64Pipeline:
    registry: MethodRegistry
    transform_rule: TransformRule

    def run(self, request: NormalizedRequest) -> NormalizedResult:
        traces: list[StageTrace] = []

        parsed_request = self._parse_input(request, traces)
        profile = self._select_method_profile(parsed_request.method_profile_ref, traces)
        primary = self._generate_primary_hexagram(parsed_request.payload["line_states"], traces)
        moving_lines = self._resolve_moving_lines(primary.line_states, traces)
        derived = self._build_derived_hexagrams(primary, moving_lines, traces)
        trace_record = self._emit_traceable_result(parsed_request, traces)

        confidence = ConfidenceEnvelope(
            rule_confidence=0.8,
            source_confidence=0.8,
            input_confidence=0.9,
        )
        return NormalizedResult(
            primary_hexagram=PrimaryHexagram(
                hexagram_identity=primary.hexagram_identity,
                line_states=primary.line_states,
                moving_lines=moving_lines,
            ),
            derived_hexagrams=derived,
            trace_record=trace_record,
            confidence_envelope=confidence,
            method_profile_ref=profile,
        )

    def _parse_input(self, request: NormalizedRequest, traces: list[StageTrace]) -> NormalizedRequest:
        if "line_states" not in request.payload:
            raise Yi64PipelineError("payload.line_states is required")
        traces.append(
            StageTrace(
                stage_name="ParseInput",
                inputs_summary={"payload_keys": sorted(request.payload.keys())},
                outputs_summary={"line_state_count": len(request.payload["line_states"])},
            )
        )
        return request

    def _select_method_profile(
        self, method_profile_ref: MethodProfileRef, traces: list[StageTrace]
    ) -> MethodProfileRef:
        if not self.registry.has(method_profile_ref.method_id):
            raise Yi64PipelineError(f"method not registered: {method_profile_ref.method_id}")
        profile = self.registry.get(method_profile_ref.method_id)
        traces.append(
            StageTrace(
                stage_name="SelectMethodProfile",
                inputs_summary={"method_id": method_profile_ref.method_id},
                outputs_summary={"resolved_method_id": profile.method_id},
            )
        )
        return profile

    def _generate_primary_hexagram(
        self, line_states: list[LineState], traces: list[StageTrace]
    ) -> PrimaryHexagram:
        if len(line_states) != 6:
            raise Yi64PipelineError("exactly 6 line_states required")
        binary_code = lines_to_binary(line_states)
        identity = binary_to_hexagram_identity(binary_code)
        moving_lines = moving_lines_from_states(line_states)
        traces.append(
            StageTrace(
                stage_name="GeneratePrimaryHexagram",
                inputs_summary={"line_state_count": len(line_states)},
                outputs_summary={"binary_code": binary_code, "king_wen_index": identity.king_wen_index},
            )
        )
        return PrimaryHexagram(
            hexagram_identity=identity,
            line_states=tuple(line_states),
            moving_lines=moving_lines,
        )

    def _resolve_moving_lines(
        self, line_states: tuple[LineState, ...], traces: list[StageTrace]
    ) -> tuple[int, ...]:
        moving_lines = moving_lines_from_states(line_states)
        traces.append(
            StageTrace(
                stage_name="ResolveMovingLines",
                inputs_summary={},
                outputs_summary={"moving_lines": list(moving_lines)},
            )
        )
        return moving_lines

    def _build_derived_hexagrams(
        self,
        primary_hexagram: PrimaryHexagram,
        moving_lines: tuple[int, ...],
        traces: list[StageTrace],
    ) -> DerivedHexagrams:
        transformed_binary = line_flip_transform(primary_hexagram.hexagram_identity.binary_code, moving_lines)
        transformed = binary_to_hexagram_identity(transformed_binary)
        traces.append(
            StageTrace(
                stage_name="BuildDerivedHexagrams",
                inputs_summary={"moving_lines": list(moving_lines), "rule_id": self.transform_rule.rule_id},
                outputs_summary={"transformed_binary": transformed_binary},
            )
        )
        return DerivedHexagrams(transformed_hexagram=transformed)

    def _emit_traceable_result(
        self, request: NormalizedRequest, traces: list[StageTrace]
    ) -> TraceRecord:
        trace = TraceRecord(
            trace_id=f"trace_{uuid4().hex}",
            steps=tuple(traces)
            + (
                StageTrace(
                    stage_name="EmitTraceableResult",
                    inputs_summary={"method_id": request.method_profile_ref.method_id},
                    outputs_summary={"step_count": len(traces) + 1},
                ),
            ),
            inputs_snapshot={"context": request.context_vector.__dict__, "payload": request.payload},
        )
        return trace


def demo_line_states() -> list[LineState]:
    """Convenience helper for quick local smoke tests."""
    return [
        LineState(line_position=1, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=2, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=3, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=4, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=5, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=6, polarity=Polarity.YANG, motion=MotionState.STATIC),
    ]
