from core.yi64 import (
    ContextVector,
    MethodFamily,
    MethodProfileRef,
    MethodRegistry,
    MotionState,
    NormalizedRequest,
    Polarity,
    TransformRule,
    Yi64Pipeline,
)
from core.yi64.model import LineState


def _make_line_states() -> list[LineState]:
    return [
        LineState(line_position=1, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=2, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=3, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=4, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=5, polarity=Polarity.YANG, motion=MotionState.STATIC),
        LineState(line_position=6, polarity=Polarity.YANG, motion=MotionState.STATIC),
    ]


def test_yi64_pipeline_returns_traceable_result():
    profile = MethodProfileRef(
        method_id="ganzhi_term_seed_v1",
        method_family=MethodFamily.TIME_SPACE_MAPPED,
        school_id="bac_phai",
        ruleset_id="bac_phai_v1",
        source_refs=("docs/rulesets/bac_phai_v1.md",),
    )
    registry = MethodRegistry()
    registry.register(profile)
    pipeline = Yi64Pipeline(
        registry=registry,
        transform_rule=TransformRule(
            rule_id="line_flip_standard",
            description="Flip all moving lines",
            version="1.0.0",
        ),
    )
    request = NormalizedRequest(
        context_vector=ContextVector(
            datetime_local="2026-05-08T19:00:00+07:00",
            timezone="Asia/Ho_Chi_Minh",
        ),
        method_profile_ref=profile,
        payload={"line_states": _make_line_states()},
    )

    result = pipeline.run(request)

    assert result.primary_hexagram.hexagram_identity.name_vi == "Kiền"
    assert result.primary_hexagram.moving_lines == ()
    assert result.derived_hexagrams.transformed_hexagram is not None
    assert len(result.trace_record.steps) == 6
