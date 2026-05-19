from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class InteractionSignalRequest(BaseModel):
    hold_duration_ms: int
    move_event_count: int
    path_length_px: float
    release_timestamp_ms: int


class CalculateRequest(BaseModel):
    datetime_local: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"
    question_text: str | None = None
    interaction_signal: InteractionSignalRequest | None = None


class PersonalProfileRequest(BaseModel):
    birth_datetime_local: str
    timezone: str
    location_ref: str | None = None
    birth_precision: Literal["exact", "approx", "unknown"] = "exact"
    gender_optional: str | None = None


class FeedbackRequest(BaseModel):
    prompt_id: str
    response_enum: Literal["matched", "partly", "false", "unknown"]
    confidence_enum: str = "unsure"
    tags: list[str] = []
    free_text_optional: str | None = None


class CalendarConvertRequest(BaseModel):
    datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    source_calendar: Literal["solar", "lunar"]
    is_leap_month: bool = False


class CompareBasicRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    location_ref: str | None = None


class LucHaoCastRequest(BaseModel):
    datetime_local: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"
    question_text: str
    interaction_signal: InteractionSignalRequest


class LucHaoSaveCaseRequest(BaseModel):
    question_text: str
    timezone: str = "Asia/Ho_Chi_Minh"
    luc_hao_state: dict
    interaction_signal: InteractionSignalRequest


class LucHaoFeedbackRequest(BaseModel):
    case_id: str
    result_enum: Literal["matched", "partly", "false", "unknown"]
    confidence_enum: Literal["high", "medium", "low", "unsure"] = "unsure"
    event_summary: str
    resolved_at_local: str | None = None
    tags: list[str] = []


class LienHoaCastRequest(BaseModel):
    question_text: str
    number_right_hand: int
    number_left_hand: int
    gender: Literal["nam", "nữ"] = "nam"


class BatTuCastRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: Literal["nam", "nữ"] = "nam"


class HaLacCastRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: Literal["nam", "nữ"] = "nam"


class AiProviderKeyRequest(BaseModel):
    api_key: str


class AiProviderNotesRequest(BaseModel):
    """Notes về provider — phân loại plan, ghi chú thanh toán/quota..."""
    plan_type: str | None = None     # 'coding_plan' | 'api_pay_per_token' | 'free_tier' | 'local'
    notes: str | None = None         # free-form text


class AiProviderTestRequest(BaseModel):
    """Test 1 call ngắn tới provider để verify key + measure latency."""
    model: str | None = None
    prompt: str = "Trả lời bằng 1 từ: 'OK'"


class AiPromptUpdateRequest(BaseModel):
    content: str


class YiHermesContextSchema(BaseModel):
    active_tab: str = ""
    active_person_id: str = ""
    active_person_name: str = ""
    active_person_birth: str = ""
    chart_data_excerpt: dict = {}
    user_gender: str = "nam"


class YiHermesChatRequest(BaseModel):
    user_message: str
    context: YiHermesContextSchema | None = None
    history: list[dict] = []   # list of {role, content, intent?, tokens_used?}


class YiHermesGlossaryUpsertRequest(BaseModel):
    term_vi: str
    term_zh: str = ""
    module: str
    short_def: str
    long_def: str
    example: str = ""
    see_also: list[str] = []


class YiHermesSoulUpdateRequest(BaseModel):
    """Partial update to user's Soul profile."""
    tone: str | None = None
    verbosity: str | None = None
    focus_schools: list[str] | None = None
    greeting_style: str | None = None
    tabu_topics: list[str] | None = None
    preferred_language: str | None = None
    addressing: dict | None = None
    notes: str | None = None


class YiHermesFactAddRequest(BaseModel):
    """Add a new fact about user to Memory."""
    fact: str
    category: str = "other"
    confidence: float = 0.8
    notes: str = ""


class YiHermesSummaryAddRequest(BaseModel):
    summary: str
    key_topics: list[str] = []
    chart_data_hash: str = ""


# ─── Person + Relationship API schemas ──────────────────────────────────────


class PersonCreateRequest(BaseModel):
    """Create a new Person profile."""
    name: str
    person_id: str | None = None
    aliases: list[str] = []
    nickname: str | None = None
    gender: str | None = None
    birth_datetime_local: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"
    day_pillar_convention: str = "late_zi"
    birth_confidence: str = "unknown"
    source: str = "manual"
    relationship_to_founder: str | None = None
    layers: dict | None = None


class PersonUpdateRequest(BaseModel):
    """Patch top-level fields of a person."""
    name: str | None = None
    aliases: list[str] | None = None
    nickname: str | None = None
    gender: str | None = None
    birth_datetime_local: str | None = None
    timezone: str | None = None
    day_pillar_convention: str | None = None
    birth_confidence: str | None = None
    relationship_to_founder: str | None = None


class PersonLayerUpdateRequest(BaseModel):
    """Merge a patch into one layer of a person (career/health/physiognomy/...)."""
    layer: str
    patch: dict
    confidence: str = "medium"


class PersonNoteRequest(BaseModel):
    body: str
    source: str = "manual"
    confidence: str = "medium"
    layer_hint: str | None = None


class RelationshipCreateRequest(BaseModel):
    from_person_id: str
    to_person_id: str
    rel_type: str
    closeness: float = 0.5
    since: str | None = None
    context: str | None = None
    quality: str = "neutral"
    frequency: str = "monthly"
    trust: str = "medium"
    notes: str | None = None
    bidirectional: bool = True


class DyadAnalysisRequest(BaseModel):
    """Compute cosmology compatibility between 2 persons."""
    person_a_id: str
    person_b_id: str
    cache_in_relationship: bool = True   # write back into relationships.cosmology_compat


# ─── YI-Lexicon API schemas ─────────────────────────────────────────────────


class LexiconConceptCreateRequest(BaseModel):
    """Manually add a concept (mostly anh review/edit; ingest uses LLM)."""
    canonical_vi: str
    concept_type: str = "other"
    canonical_zh: str | None = None
    canonical_en: str | None = None
    aliases: list[str] = []
    schools: list[str] = ["common"]
    confidence: float = 0.7
    notes: str | None = None


class LexiconMappingCreateRequest(BaseModel):
    concept_id: int
    dim_type: str
    dim_value: str
    strength: float = 1.0
    reasoning_vi: str | None = None
    reasoning_zh: str | None = None
    school: str = "common"
    confidence: float = 0.7


class LexiconInterpretRequest(BaseModel):
    text: str
    schools: list[str] | None = None


class LexiconCorpusRegisterRequest(BaseModel):
    name: str
    file_path: str
    author: str | None = None
    school: str | None = None
    language: str = "vi"
    notes: str | None = None


class LexiconIngestRequest(BaseModel):
    corpus_id: int
    max_chunks: int | None = None    # None = ingest all


class LexiconDistillRequest(BaseModel):
    root_id: str                     # kanban council root id


class LexiconResolveItemRequest(BaseModel):
    status: str                      # 'approved' | 'rejected'
    reviewer_note: str = ""


class LexiconResolveConflictRequest(BaseModel):
    """Anh resolves a conflict group between mappings."""
    primary_mapping_id: int | None = None
    status: str = "resolved"          # 'resolved' | 'kept_all' | 'dismissed'
    anh_note: str = ""


class YiHermesContentUpdateRequest(BaseModel):
    """Update project manifest or founder profile."""
    content: str


class AiCouncilRequest(BaseModel):
    """Hội Đồng consultation request."""
    question: str
    chart_data: dict
    chart_summary: dict | None = None
    explicit_agents: list[str] | None = None
    parallel: bool = True
    skip_challenge: bool = False
    persist: bool = True


class AiKanbanCouncilRequest(BaseModel):
    """Kanban-based council consultation (durable, async).

    Engine pre-cast happens server-side when `birth` or `event` is provided
    — sages receive JSON output and DO NOT recompute.
    """
    question: str
    chart_context: dict | None = None
    sages: list[str] | None = None
    soul_key: str = "_anon"
    # Optional auto-precast inputs — server calls engine cast functions
    birth: dict | None = None
    event: dict | None = None
    # Or skip auto-precast and supply precomputed JSON directly:
    precast_data: dict[str, dict] | None = None


class AiCritiqueResolveRequest(BaseModel):
    """Mark a sage-suggested engine critique as resolved or dismissed."""
    resolution: str
    action: str = "resolve"  # "resolve" | "dismiss"


class TuViCastRequest(BaseModel):
    """Cast a Tử Vi lá số from lunar birth info.

    Two input modes:
    1. Direct: provide lunar_month + lunar_day + hour_branch + year_stem + year_branch + gender.
    2. Convenient: provide birth_datetime_local (will be converted to lunar via core.chronos).

    Optional `target_year` triggers lưu trú sao (transit) computation.
    """
    birth_datetime_local: str | None = None
    timezone: str = "Asia/Ho_Chi_Minh"
    lunar_month: int | None = None
    lunar_day: int | None = None
    hour_branch: str | None = None
    year_stem: str | None = None
    year_branch: str | None = None
    gender: Literal["nam", "nữ"] = "nam"
    target_year: int | None = None
    include_interpretation: bool = True


# ── Birth Hour Quiz v2 schemas ─────────────────────────────────────────
class BirthHourQuizV2HourRange(BaseModel):
    start: int
    end: int


class BirthHourQuizV2StartRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD
    timezone: str = "Asia/Ho_Chi_Minh"
    hour_range: BirthHourQuizV2HourRange | None = None
    gender: Literal["nam", "nữ"] = "nam"


class BirthHourQuizV2SubmitRequest(BaseModel):
    session_id: str
    round_num: int
    answers: dict[str, str]  # {trait_id: option_id}


class BirthHourQuizV2SaveRequest(BaseModel):
    session_id: str
    person_id: str

