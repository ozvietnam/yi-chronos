"""GPS Engine — prescriptive trigger points + action recommendations.

PHILOSOPHY (per user directive Phase 3 option C):
- Output is prescriptive ("at hour X do Y").
- Gated by EXPERIMENTAL_MODE — single-user only until validated.
- Every prescription is hashed + pre-registered when persisted, immutable.
- Each recommendation tagged with rule_id + score breakdown so feedback
  can attribute hit/miss to specific rules.

The engine itself is pure (no I/O). Persistence lives in gps_storage.py.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
from zoneinfo import ZoneInfo

from core.chronos import calculate_chronos_state
from core.config import EXPERIMENTAL_MODE, runtime_mode_banner
from engine.personal_quai import (
    NatalHexagram,
    TRIGRAM_ELEMENT,
    compute_natal_hexagram,
    score_compatibility,
)
from engine.van_trong_van import HOUR_BRANCH_ORDER, VN_HOUR_MIDPOINTS


DOMAINS = (
    "decision",     # Quyết định lớn
    "work",         # Công việc / sự nghiệp
    "finance",      # Tài chính
    "relations",    # Quan hệ / giao tiếp
    "health",       # Sức khỏe / cân bằng
    "creative",     # Sáng tạo / khởi sự
)

DOMAIN_VI = {
    "decision": "Quyết định lớn",
    "work": "Công việc / sự nghiệp",
    "finance": "Tài chính",
    "relations": "Quan hệ / giao tiếp",
    "health": "Sức khỏe / cân bằng",
    "creative": "Sáng tạo / khởi sự",
}

# Element bias for each domain — the element most associated with that life area.
DOMAIN_ELEMENT_AFFINITY = {
    "decision": "kim",   # Decisive, cutting → metal
    "work": "thổ",       # Steady, structured → earth
    "finance": "kim",    # Storage, value → metal
    "relations": "thủy", # Flow, communication → water
    "health": "mộc",     # Growth, vitality → wood
    "creative": "hỏa",   # Expression, light → fire
}

# Score band → recommendation mode
def _score_band(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 65:
        return "medium_plus"
    if score >= 50:
        return "medium"
    if score >= 35:
        return "medium_minus"
    return "low"


# Rule table: (domain, score_band) → list of action templates.
ACTION_TEMPLATES = {
    "decision": {
        "high":          ["Chốt và công bố quyết định lớn", "Ký kết ràng buộc dài hạn", "Đưa quyết định vào hành động ngay"],
        "medium_plus":   ["Trình bày phương án để chốt", "Ràng buộc cam kết bằng văn bản", "Test một quyết định nhỏ trong scope tương tự"],
        "medium":        ["Chuẩn bị tài liệu cho quyết định sau", "Tham vấn 1-2 ý kiến đối lập", "Liệt kê rõ rủi ro trước khi chốt"],
        "medium_minus":  ["Chỉ chốt việc nhỏ, hoãn việc lớn", "Tăng giai đoạn kiểm tra", "Tài liệu hóa chi tiết để giảm sai số"],
        "low":           ["Hoãn quyết định lớn", "Thu thập thêm dữ liệu, không cam kết", "Đợi qua xung trong vài ngày"],
    },
    "work": {
        "high":          ["Khởi động dự án mới hoặc giai đoạn mới", "Đẩy mạnh việc đang dang dở để hoàn thành", "Chủ động phân công, mở rộng đội"],
        "medium_plus":   ["Bám lịch, tăng output ổn định", "Hoàn thiện báo cáo / tài liệu chính", "Họp đẩy tiến độ các mục lớn"],
        "medium":        ["Giữ nhịp đều, không tăng tải đột ngột", "Soát lại quy trình, dọn nợ kỹ thuật", "Lên kế hoạch cho tuần sau"],
        "medium_minus":  ["Giảm scope, ưu tiên việc cốt lõi", "Tránh giao việc mới quan trọng", "Tăng kiểm tra chất lượng"],
        "low":           ["Tránh phụ trách dự án mới", "Tập trung dọn dẹp, lưu trữ, không bùng nổ", "Một-một với người quan trọng nếu cần"],
    },
    "finance": {
        "high":          ["Đàm phán hợp đồng / chốt deal", "Triển khai đầu tư đã chuẩn bị kỹ", "Mở rộng nguồn thu mới"],
        "medium_plus":   ["Chốt khoản nhỏ, gia hạn hợp đồng", "Theo dõi cash flow, không chi phát sinh", "Đối soát số liệu tháng"],
        "medium":        ["Giữ vị trí hiện tại, không vào / ra mạnh", "Soát chi phí định kỳ", "Cập nhật ngân sách"],
        "medium_minus":  ["Hoãn cam kết tài chính lớn", "Giữ thanh khoản, không khoá vốn", "Kiểm tra rủi ro tín dụng"],
        "low":           ["Không ký hợp đồng tài chính lớn", "Không vay mới / không cho vay", "Chỉ chi cho nhu cầu đã lên kế hoạch trước"],
    },
    "relations": {
        "high":          ["Mở đối thoại quan trọng, nói thẳng", "Hòa giải tranh chấp đang treo", "Networking sự kiện chủ động"],
        "medium_plus":   ["Lắng nghe trước khi trình bày", "Củng cố quan hệ thân thiết", "Tham dự event vừa phải"],
        "medium":        ["Giữ giao tiếp định kỳ", "Trả tin nhắn đang treo", "Một bữa cà phê 1-1"],
        "medium_minus":  ["Tránh đối thoại căng nếu chưa rõ vấn đề", "Tài liệu hóa thay vì tranh luận miệng", "Giảm cuộc họp đông người"],
        "low":           ["Tránh đàm phán khi đang xung", "Không đưa quyết định ảnh hưởng nhóm", "Ưu tiên im lặng quan sát"],
    },
    "health": {
        "high":          ["Tập nặng, đẩy ngưỡng sức bền", "Bắt đầu protocol mới (diet/exercise)", "Đặt lịch khám tổng thể"],
        "medium_plus":   ["Duy trì routine cơ bản", "Tăng nhẹ cường độ tập", "Ăn uống đúng giờ"],
        "medium":        ["Giữ nhịp, không thay đổi đột ngột", "Ưu tiên ngủ đủ, hydrate", "Đi bộ nhẹ thay vì tập nặng"],
        "medium_minus":  ["Tránh hoạt động cường độ cao", "Massage / nghỉ chủ động", "Giảm caffeine, ăn nhẹ"],
        "low":           ["Nghỉ ngơi sâu, không ép sức", "Không bắt đầu protocol mới", "Tránh stress xã hội"],
    },
    "creative": {
        "high":          ["Khởi tạo dự án mới, viết bản đầu tiên", "Phát hành / công bố tác phẩm", "Brainstorm mở với đội"],
        "medium_plus":   ["Tinh chỉnh bản nháp, lần 2-3", "Lấy feedback có cấu trúc", "Lên outline cho phần tiếp"],
        "medium":        ["Làm việc đều, không tìm bứt phá", "Đọc / nạp tư liệu mới", "Sửa morph nhỏ"],
        "medium_minus":  ["Không bắt đầu dự án sáng tạo lớn", "Tập trung kỹ thuật / chỉnh sửa thay vì sáng tác", "Lưu trữ idea cho sau"],
        "low":           ["Không phát hành công khai", "Tạm dừng sáng tác lớn", "Giữ idea trong workspace cá nhân"],
    },
}


@dataclass(frozen=True)
class Trigger:
    domain: str
    domain_vi: str
    hour_branch: str             # The Vietnamese hour where this trigger fires
    hour_midpoint: int           # 24h clock representation
    score: int                   # 0..100 from compatibility (with family blending if present)
    score_band: str
    action_text: str             # The prescriptive recommendation
    action_template_index: int   # Which template was selected (0-2)
    rule_id: str                 # Stable id for accuracy attribution
    score_components: dict       # Score breakdown (for feedback attribution)
    family_overlay: tuple = ()   # tuple[BranchInteraction, ...] vs the hour branch
    family_avg_score: int = 0    # mean of per-member scores (-25..+18)
    personal_only_score: int | None = None  # Original score before family blending

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GPSDay:
    profile_hash: str
    date_local: str
    timezone: str
    day_pillar: str
    day_quai: str
    day_quai_king_wen: int
    solar_term: str
    triggers: tuple[Trigger, ...]
    composed_summary: str        # Short narrative summary
    runtime_mode: dict
    natal_snapshot: dict

    def to_dict(self) -> dict:
        return {
            "profile_hash": self.profile_hash,
            "date_local": self.date_local,
            "timezone": self.timezone,
            "day_pillar": self.day_pillar,
            "day_quai": self.day_quai,
            "day_quai_king_wen": self.day_quai_king_wen,
            "solar_term": self.solar_term,
            "triggers": [t.to_dict() for t in self.triggers],
            "composed_summary": self.composed_summary,
            "runtime_mode": self.runtime_mode,
            "natal_snapshot": self.natal_snapshot,
        }


def _profile_hash(birth_datetime_local: str, timezone: str) -> str:
    payload = f"{birth_datetime_local}|{timezone}".encode("utf-8")
    return sha256(payload).hexdigest()[:16]


def _select_action_template(domain: str, score: int, hour_branch: str) -> tuple[str, int]:
    band = _score_band(score)
    templates = ACTION_TEMPLATES[domain][band]
    # Deterministic selection: index = hour_branch position % len(templates)
    branch_idx = HOUR_BRANCH_ORDER.index(hour_branch)
    template_idx = branch_idx % len(templates)
    return templates[template_idx], template_idx


def _rule_id(domain: str, score_band: str, hour_branch: str) -> str:
    return f"gps:{domain}:{score_band}:{hour_branch}"


def _domain_score_adjustment(domain: str, natal: NatalHexagram, target_upper_element: str, target_lower_element: str) -> int:
    """Add a small element-affinity bonus for domains aligned with day's elements."""
    affinity = DOMAIN_ELEMENT_AFFINITY[domain]
    bonus = 0
    if affinity == target_upper_element:
        bonus += 4
    if affinity == target_lower_element:
        bonus += 2
    if affinity == natal.upper_element:
        bonus += 2
    return bonus


def _compose_summary(day_quai: str, top_trigger: Trigger | None) -> str:
    if top_trigger is None:
        return f"Quẻ ngày {day_quai} — không có cửa sổ kích hoạt rõ rệt trong các giờ."
    return (
        f"Quẻ ngày {day_quai}. Cửa sổ kích hoạt mạnh nhất rơi vào "
        f"giờ {top_trigger.hour_branch} ({top_trigger.hour_midpoint:02d}h) — "
        f"miền {top_trigger.domain_vi.lower()}, score {top_trigger.score}."
    )


def _blend_with_family_score(personal: int, family_avg: int) -> int:
    """Same blending used in van_trong_van: 70% personal + 30% family-normalized."""
    family_normalized = max(0, min(100, 50 + family_avg * 2))
    blended = round(personal * 0.7 + family_normalized * 0.3)
    return max(0, min(100, blended))


def compute_gps_day(
    natal: NatalHexagram,
    target_date: date,
    timezone_name: str = "Asia/Ho_Chi_Minh",
    domains: tuple[str, ...] = DOMAINS,
    min_score_for_trigger: int = 55,
    family_members: list | None = None,
) -> GPSDay:
    """Compute GPS recommendations for a specific date.

    Optional family_members: per-trigger family overlay vs hour-pillar branch.
    When provided, trigger score is blended (70% personal + 30% family).
    """
    profile_hash = _profile_hash(natal.birth_local_datetime, natal.birth_timezone)

    zone = ZoneInfo(timezone_name)
    base_dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=zone)

    # Day-level state at noon for the headline.
    noon_state = calculate_chronos_state(
        base_dt.replace(hour=12).replace(microsecond=0).isoformat(),
        timezone_name,
    )
    from core.yi64.derivations.derived_hexagrams import compute_all_derived
    from core.yi64.derivations.mai_hoa_nntt import derive_line_states
    from core.yi64.transforms import lines_to_binary, moving_lines_from_states

    day_lines = derive_line_states(noon_state)
    day_binary = lines_to_binary(day_lines)
    day_moving = moving_lines_from_states(day_lines)
    day_primary = compute_all_derived(day_binary, day_moving)["chanh"]

    # Pre-compute family overlay against day branch for whole-day baseline.
    has_family = bool(family_members)
    family_overlay_factory = None
    if has_family:
        from engine.family_system import compute_family_overlay_for_branch
        family_overlay_factory = compute_family_overlay_for_branch

    # Compute per-hour scores + per-domain triggers.
    triggers: list[Trigger] = []
    for hour_branch in HOUR_BRANCH_ORDER:
        midpoint = VN_HOUR_MIDPOINTS[hour_branch]
        slot_dt = base_dt.replace(hour=midpoint).replace(microsecond=0)
        slot_state = calculate_chronos_state(slot_dt.isoformat(), timezone_name)
        compat = score_compatibility(natal, slot_state)

        slot_lines = derive_line_states(slot_state)
        slot_binary = lines_to_binary(slot_lines)
        # Use the slot's own derivation summary for upper/lower elements.
        from core.yi64.derivations.mai_hoa_nntt import derivation_summary
        slot_summary = derivation_summary(slot_state)
        slot_upper_el = TRIGRAM_ELEMENT[slot_summary["upper_trigram"]]
        slot_lower_el = TRIGRAM_ELEMENT[slot_summary["lower_trigram"]]

        # Family overlay vs the hour-pillar branch.
        slot_hour_branch = slot_state.ganzhi.hour.split()[1] if " " in slot_state.ganzhi.hour else hour_branch
        family_overlay: tuple = ()
        family_avg = 0
        if has_family:
            family_overlay, family_avg = family_overlay_factory(
                family_members, slot_hour_branch
            )

        for domain in domains:
            domain_bonus = _domain_score_adjustment(
                domain, natal, slot_upper_el, slot_lower_el
            )
            personal_score = max(0, min(100, compat.final_score + domain_bonus))
            if has_family:
                final_score = _blend_with_family_score(personal_score, family_avg)
            else:
                final_score = personal_score

            if final_score < min_score_for_trigger:
                continue
            band = _score_band(final_score)
            action_text, template_idx = _select_action_template(
                domain, final_score, hour_branch
            )
            triggers.append(
                Trigger(
                    domain=domain,
                    domain_vi=DOMAIN_VI[domain],
                    hour_branch=hour_branch,
                    hour_midpoint=midpoint,
                    score=final_score,
                    score_band=band,
                    action_text=action_text,
                    action_template_index=template_idx,
                    rule_id=_rule_id(domain, band, hour_branch),
                    score_components={
                        "base_compatibility": compat.final_score,
                        "domain_element_bonus": domain_bonus,
                        "compatibility_breakdown": compat.to_dict(),
                    },
                    family_overlay=family_overlay,
                    family_avg_score=family_avg,
                    personal_only_score=personal_score if has_family else None,
                )
            )

    # Sort by score descending, break ties by hour branch order.
    triggers.sort(key=lambda t: (-t.score, HOUR_BRANCH_ORDER.index(t.hour_branch)))
    top = triggers[0] if triggers else None

    return GPSDay(
        profile_hash=profile_hash,
        date_local=target_date.isoformat(),
        timezone=timezone_name,
        day_pillar=noon_state.ganzhi.day,
        day_quai=day_primary.name_vi,
        day_quai_king_wen=day_primary.king_wen_index,
        solar_term=noon_state.solar_term.name_vi,
        triggers=tuple(triggers),
        composed_summary=_compose_summary(day_primary.name_vi, top),
        runtime_mode=runtime_mode_banner(),
        natal_snapshot={
            "primary_name": natal.primary_name,
            "primary_king_wen": natal.primary_king_wen,
            "upper_trigram": natal.upper_trigram,
            "lower_trigram": natal.lower_trigram,
        },
    )


def hash_gps_day(gps_day: GPSDay) -> str:
    """Stable hash of a GPS day for prediction logging."""
    import json
    canon = json.dumps(gps_day.to_dict(), sort_keys=True, ensure_ascii=False)
    return sha256(canon.encode("utf-8")).hexdigest()


def hash_trigger(trigger: Trigger, profile_hash: str, date_local: str) -> str:
    """Stable hash of a single trigger pre-registration record."""
    import json
    payload = {
        "profile_hash": profile_hash,
        "date_local": date_local,
        "domain": trigger.domain,
        "hour_branch": trigger.hour_branch,
        "score": trigger.score,
        "rule_id": trigger.rule_id,
        "action_text": trigger.action_text,
    }
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
