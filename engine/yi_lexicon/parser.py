"""Observation parser — turns free-text "quan vật" into structured symbolic context.

Input:  "9h sáng em ra đường gặp 2 chiếc lá rơi"
Output: ObservationContext with:
        - tokens recognized
        - mappings per token (concept → bat_quai/ngu_hanh/...)
        - aggregated dimension counts (Mộc 2, Hỏa 1, ...)
        - candidate Mai Hoa quẻ if numbers present
        - generated narrative summary for LLM prompt enrichment

Philosophy (anh, 2026-05-12):
> "trước đọc sách tìm quy luật, giờ vẫn sách ấy, mở rộng từ điển,
>  biến thuật ngữ thành đơn giản dễ hiểu với người dùng."

The parser is intentionally simple in v1 — regex + keyword matching against the
lexicon. LLM-based parsing for ambiguous cases is left to `distill.py` / council.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field

from .core_seed import NUMBER_TO_QUAI
from .store import (
    Concept,
    Mapping,
    get_concept,
    mappings_for,
    search_concepts,
)


@dataclass
class TokenMatch:
    """One concept matched in the input text."""
    token: str
    concept_id: int
    canonical_vi: str
    concept_type: str
    mappings: list[Mapping] = field(default_factory=list)
    position: int = 0      # offset in original text

    def to_dict(self) -> dict:
        d = asdict(self)
        d["mappings"] = [m.to_dict() if hasattr(m, "to_dict") else m for m in self.mappings]
        return d


@dataclass
class ObservationContext:
    """Full symbolic interpretation of an observation."""
    text: str
    tokens: list[TokenMatch]
    numbers_extracted: list[int]
    time_context: str | None = None        # e.g. "9h sáng" if detected
    # Aggregated counts per dimension
    bat_quai_distribution: dict = field(default_factory=dict)
    ngu_hanh_distribution: dict = field(default_factory=dict)
    am_duong_distribution: dict = field(default_factory=dict)
    # Candidate Mai Hoa hexagram (if numbers present)
    mai_hoa_candidate: dict | None = None
    # Narrative for LLM
    narrative_summary: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tokens"] = [t.to_dict() for t in self.tokens]
        return d


# ─── Tokenization ────────────────────────────────────────────────────────────


_NUMBER_RE = re.compile(r"(\d+)")
_TIME_RE = re.compile(
    r"\b(\d{1,2})\s*(?:h|giờ|:)\s*(\d{0,2})?\s*(sáng|trưa|chiều|tối|đêm|am|pm)?",
    re.IGNORECASE,
)
# Vietnamese number words → int
_VI_NUMBER_WORDS: dict[str, int] = {
    "một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5,
    "sáu": 6, "bảy": 7, "tám": 8, "chín": 9, "mười": 10,
    "mười một": 11, "mười hai": 12,
}

# Common Vietnamese stopwords to ignore as candidate tokens
_STOPWORDS = {
    "là", "thì", "mà", "và", "hoặc", "thấy", "có", "không", "được", "đã",
    "đang", "sẽ", "rồi", "ngay", "vẫn", "đều", "cũng", "mỗi", "này", "đó",
    "cái", "chiếc", "con", "vào", "với", "cho", "của", "từ", "đến", "tại",
    "trên", "dưới", "trong", "ngoài", "ra", "vô", "đi", "lại", "qua",
    "anh", "em", "tôi", "ta", "mình", "ấy", "rất", "thật", "quá",
    "thì", "lúc", "khi", "phút", "giây", "nha", "nhé", "à", "ơi",
    # Numbers (handled separately)
    "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười",
}


def _normalize_text(text: str) -> str:
    """Lower + remove punctuation (keep Vietnamese diacritics)."""
    # Keep word chars + Vietnamese diacritics (Unicode letter category)
    return re.sub(r"[^\w\sÀ-ỹ]", " ", text.lower())


def _extract_numbers(text: str) -> list[int]:
    """Find all numeric mentions in text — both Arabic digits AND Vietnamese number words."""
    out: list[int] = []
    out.extend(int(n) for n in _NUMBER_RE.findall(text))
    text_lower = text.lower()
    # Multi-word phrases first (longer matches)
    for phrase, val in sorted(_VI_NUMBER_WORDS.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower):
            out.append(val)
    return out


def _extract_time(text: str) -> str | None:
    """Find time-of-day mention: '9h sáng', '21:30', etc."""
    m = _TIME_RE.search(text.lower())
    if m:
        return m.group(0).strip()
    return None


def _gen_ngrams(tokens: list[str], min_n: int = 1, max_n: int = 3) -> list[tuple[str, int]]:
    """Generate n-grams from token list. Returns [(ngram_text, start_index), ...]."""
    out: list[tuple[str, int]] = []
    for n in range(max_n, min_n - 1, -1):  # longer first
        for i in range(len(tokens) - n + 1):
            out.append((" ".join(tokens[i : i + n]), i))
    return out


# ─── Mai Hoa quẻ candidate from numbers ─────────────────────────────────────


def _mai_hoa_candidate(numbers: list[int], hour: int | None = None) -> dict | None:
    """Build a candidate Mai Hoa hexagram from observation numbers.

    Classical formula (quan vật khởi quẻ Mai Hoa):
      - Upper trigram = (sum_of_first_number_group) mod 8 (0→8)
      - Lower trigram = (upper_total + hour_branch_rank) mod 8
      - Moving line   = (upper_total + lower_total + hour_branch_rank) mod 6

    Simplified for v1: just map numbers → quẻ via NUMBER_TO_QUAI table.
    """
    if not numbers:
        return None

    NUMBER_QUAI_MAP = dict(NUMBER_TO_QUAI)   # 1..8

    # Take first 1 or 2 numbers as upper/lower
    if len(numbers) >= 2:
        n1, n2 = numbers[0], numbers[1]
    else:
        n1 = numbers[0]
        n2 = numbers[0]   # repeat as fallback

    upper_idx = (n1 - 1) % 8 + 1   # ensure 1..8
    lower_idx = (n2 - 1) % 8 + 1
    upper_quai = NUMBER_QUAI_MAP.get(upper_idx, "Càn")
    lower_quai = NUMBER_QUAI_MAP.get(lower_idx, "Càn")

    # Moving line
    if hour is not None:
        moving_line = ((n1 + n2 + hour) - 1) % 6 + 1
    else:
        moving_line = ((n1 + n2) - 1) % 6 + 1

    return {
        "upper_quai": upper_quai,
        "lower_quai": lower_quai,
        "moving_line": moving_line,
        "source_numbers": numbers[:2],
        "hour_branch_rank": hour,
        "note": (
            f"Sơ bộ Mai Hoa: trên {upper_quai} ({upper_idx}) — dưới {lower_quai} ({lower_idx}), "
            f"hào động {moving_line}. Cần `engine.mai_hoa.cast` để compose tên quẻ chính + hổ + biến."
        ),
    }


# ─── Public API ──────────────────────────────────────────────────────────────


def interpret_observation(text: str, *, schools: list[str] | None = None) -> ObservationContext:
    """Parse free-text observation into symbolic context.

    Args:
        text: Vietnamese free-text. E.g. "9h sáng em gặp 2 chiếc lá rơi"
        schools: filter mappings to these schools (default: all)

    Returns:
        ObservationContext with tokens, aggregated dimensions, mai_hoa candidate,
        and narrative summary ready to inject into LLM prompt.
    """
    # 1. Extract structured signals first
    numbers = _extract_numbers(text)
    time_str = _extract_time(text)

    # 2. Tokenize for n-gram lexicon matching
    normalized = _normalize_text(text)
    tokens_raw = [t for t in normalized.split() if t and t not in _STOPWORDS]

    # 3. Match n-grams to lexicon (longer first, dedupe overlapping)
    matches: list[TokenMatch] = []
    used_positions: set[int] = set()
    ngrams = _gen_ngrams(tokens_raw, min_n=1, max_n=3)
    for ngram, pos in ngrams:
        if pos in used_positions:
            continue
        if ngram in _STOPWORDS:
            continue
        # Direct lookup
        concept = get_concept(canonical_vi=ngram)
        if not concept:
            # Try title-case variant (for symbols like "càn", "tỵ", ...)
            concept = get_concept(canonical_vi=ngram.title())
        if not concept:
            # Last resort: FTS search top hit
            hits = search_concepts(ngram, schools=schools, limit=1)
            concept = hits[0] if hits else None

        if concept and concept.concept_id:
            tm = TokenMatch(
                token=ngram,
                concept_id=concept.concept_id,
                canonical_vi=concept.canonical_vi,
                concept_type=concept.concept_type,
                mappings=mappings_for(concept.concept_id, school=schools[0] if schools else None),
                position=pos,
            )
            matches.append(tm)
            # Mark all positions covered by this n-gram as used
            ngram_len = len(ngram.split())
            for offset in range(ngram_len):
                used_positions.add(pos + offset)

    # 4. Aggregate dimensions
    bat_quai_dist: Counter = Counter()
    ngu_hanh_dist: Counter = Counter()
    am_duong_dist: Counter = Counter()
    for m in matches:
        for mp in m.mappings:
            if mp.dim_type == "bat_quai":
                bat_quai_dist[mp.dim_value] += mp.strength
            elif mp.dim_type == "ngu_hanh":
                ngu_hanh_dist[mp.dim_value] += mp.strength
            elif mp.dim_type == "am_duong":
                am_duong_dist[mp.dim_value] += mp.strength

    # 5. Mai Hoa candidate (if numbers present)
    hour_rank = None
    if time_str:
        hm = re.match(r"(\d{1,2})", time_str)
        if hm:
            hr = int(hm.group(1))
            # Map hour to giờ Chi rank (Tý=1 starting 23:00)
            # Simplified: hour 0=Tý(1), 1=Sửu(2)? Actually:
            #   23-01 = Tý (rank 1), 01-03 = Sửu (rank 2), ..., 21-23 = Hợi (12)
            if hr == 23 or hr == 0 or hr < 1:
                hour_rank = 1
            else:
                hour_rank = (hr + 1) // 2 + 1  # rough mapping
                if hour_rank > 12:
                    hour_rank = hour_rank % 12 or 12

    mai_hoa = _mai_hoa_candidate(numbers, hour=hour_rank)

    # 6. Build narrative summary for LLM
    narrative_parts: list[str] = []
    if matches:
        narrative_parts.append(
            f"Phát hiện {len(matches)} ý niệm: " +
            ", ".join(f"{m.token}→{m.canonical_vi}" for m in matches[:6])
        )
    if ngu_hanh_dist:
        nh_str = ", ".join(f"{k} {v:.1f}" for k, v in ngu_hanh_dist.most_common())
        narrative_parts.append(f"Ngũ hành nổi: {nh_str}")
    if bat_quai_dist:
        bq_str = ", ".join(f"{k} {v:.1f}" for k, v in bat_quai_dist.most_common())
        narrative_parts.append(f"Bát quái nổi: {bq_str}")
    if am_duong_dist:
        ad_str = ", ".join(f"{k} {v:.1f}" for k, v in am_duong_dist.most_common())
        narrative_parts.append(f"Âm dương: {ad_str}")
    if mai_hoa:
        narrative_parts.append(
            f"Mai Hoa sơ bộ: {mai_hoa['upper_quai']} trên / {mai_hoa['lower_quai']} dưới, "
            f"hào động {mai_hoa['moving_line']}"
        )
    if time_str:
        narrative_parts.append(f"Thời gian: {time_str}")
    if numbers:
        narrative_parts.append(f"Số phát hiện: {numbers}")

    narrative = " | ".join(narrative_parts) if narrative_parts else "(không phát hiện ý niệm nào — cần mở rộng lexicon)"

    return ObservationContext(
        text=text,
        tokens=matches,
        numbers_extracted=numbers,
        time_context=time_str,
        bat_quai_distribution=dict(bat_quai_dist),
        ngu_hanh_distribution=dict(ngu_hanh_dist),
        am_duong_distribution=dict(am_duong_dist),
        mai_hoa_candidate=mai_hoa,
        narrative_summary=narrative,
    )
