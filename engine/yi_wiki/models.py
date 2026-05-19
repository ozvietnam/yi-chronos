"""YI-Wiki dataclasses.

Schema từ design doc (wiki-master-apprentice.md §5).
Tâm-aware fields (interaction_log, tam_note) là điểm khác biệt với wiki thường —
anh chốt 2026-05-14: "Cầm chuột bấm và suy nghĩ là động tâm rồi".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ─── Lineage tiers ──────────────────────────────────────────────────────────
TIER_MASTER = 0          # Thiệu Khang Tiết (duy nhất)
TIER_MASTER_TEACHER = 1  # Lý Chi Tài
TIER_DIRECT_DISCIPLE = 2 # Thiệu Bá Ôn, Trương Hành Thành
TIER_CONTEMPORARY = 3    # Chu Hy, Trình Di, Sai Nguyên Định
TIER_MINH_THANH = 4      # Lai Tri Đức, Vương Khôi Vận
TIER_MODERN = 5          # Thiệu Vĩ Hoa, dịch giả VN

TIER_NAMES = {
    0: "Tổ sư",
    1: "Thầy của Tổ sư",
    2: "Đệ tử trực tiếp",
    3: "Cùng thời / kế thừa rẽ nhánh",
    4: "Truyền thừa Minh-Thanh",
    5: "Hậu duệ hiện đại",
}


# ─── Domain enum cho Method ─────────────────────────────────────────────────
METHOD_DOMAINS = ("bốc", "đọc", "ứng_kỳ", "biến_hoá", "khác")


@dataclass
class Author:
    """Tác giả trong lineage. Anchor cho mọi Passage/Method/CaseStudy."""
    author_id: int = 0  # 0 = chưa save
    name_vi: str = ""
    name_zh: str = ""
    tier_in_lineage: int = 5
    era: str = ""               # 'tống-bắc', 'tống-nam', ...
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    worldview_school: str = ""  # 'tiên-thiên-tâm-pháp', 'lý-học', ...
    foundational_axioms: list[str] = field(default_factory=list)
    hermeneutic_style: str = ""
    works: list[int] = field(default_factory=list)   # work_id list
    bio_summary: str = ""
    teachers: list[int] = field(default_factory=list)  # author_id of teachers
    disciples: list[int] = field(default_factory=list)
    created_at: int = 0


@dataclass
class Passage:
    """Đoạn văn nguyên vẹn từ một work. KHÔNG fragment."""
    passage_id: int = 0
    author_id: int = 0
    corpus_id: str = ""          # link to corpus_books.corpus_id
    page_start: int = 0
    page_end: int = 0
    raw_text: str = ""
    topic: str = ""
    summary_50w: str = ""
    concepts_mentioned: list[int] = field(default_factory=list)
    related_passages: list[int] = field(default_factory=list)
    is_canonical: bool = True
    created_at: int = 0


@dataclass
class Method:
    """Phương pháp hành đạo (bốc / đọc / ứng kỳ / biến hoá)."""
    method_id: int = 0
    author_id: int = 0
    name_vi: str = ""
    name_zh: str = ""
    domain: str = "khác"
    inputs_required: list[str] = field(default_factory=list)
    procedure_steps: list[str] = field(default_factory=list)
    output_format: str = ""
    source_passages: list[int] = field(default_factory=list)
    derived_from: list[int] = field(default_factory=list)  # method_id parents
    case_studies: list[int] = field(default_factory=list)
    confidence_baseline: float = 0.0  # 0 = unknown
    notes: str = ""
    created_at: int = 0


@dataclass
class CaseStudy:
    """Trường hợp lịch sử Thiệu (hoặc đệ tử) ứng dụng method."""
    case_id: int = 0
    method_id: int = 0
    historical_event: str = ""
    inputs_recorded: dict = field(default_factory=dict)
    output_predicted: str = ""
    output_actual: str = ""
    accuracy_score: float = 0.0
    source_book: str = ""        # tên sách + page
    created_at: int = 0


@dataclass
class Prediction:
    """Prediction anh thực sự gieo qua wiki — tâm-aware capture."""
    pred_id: int = 0
    timestamp: int = 0           # precise — moment of động tâm
    user_intent: str = ""
    user_context: dict = field(default_factory=dict)
    # ⭐ Tâm capture (insight anh chốt 2026-05-14)
    interaction_log: list[dict] = field(default_factory=list)
    tam_note: str = ""
    # Chain method + consultant
    method_chain: list[int] = field(default_factory=list)
    consultants_invoked: list[int] = field(default_factory=list)
    predicted_outcome: str = ""
    predicted_timing: str = ""
    # Review
    review_reminder_at: int = 0
    actual_outcome: Optional[str] = None
    learning_notes: str = ""
    created_at: int = 0


@dataclass
class ConceptIndex:
    """REVERSE LOOKUP — concept → passages. Không phải atomic dictionary."""
    concept_id: int = 0
    canonical_vi: str = ""
    canonical_zh: str = ""
    aliases: list[str] = field(default_factory=list)
    mentioned_in_passages: list[int] = field(default_factory=list)
    short_note: str = ""           # 1-2 câu — KHÔNG là định nghĩa đầy đủ
    # KHÔNG có is_consensus — học trò chưa đủ thẩm quyền phân loại
    first_seen_corpus: str = ""
    first_seen_page: int = 0
    created_at: int = 0


@dataclass
class Work:
    """Tác phẩm của Author. Link sang corpus_books nếu đã restored."""
    work_id: int = 0
    author_id: int = 0
    title_vi: str = ""
    title_zh: str = ""
    year_composed: Optional[int] = None
    role: str = ""                # 'method', 'philosophy', 'cosmology', ...
    corpus_id: Optional[str] = None  # NULL nếu chưa có trong thư viện
    is_canonical: bool = True
    notes: str = ""
    created_at: int = 0
