"""Timeline narrative engine — 6 derived hexagrams as a story arc.

Per project framing rule (deep-research-report.md): describe STATE, not
prediction. Each hexagram in the spread takes a fixed narrative role:

    Chánh (本) — surface situation, what shows up
    Hỗ (互)   — hidden interior dynamics
    Biến (變) — direction of movement (via moving line)
    Giao (錯) — opposing / repressed face
    Phục (綜) — reverse-angle view (how others read it)
    Bao (包)  — outermost frame / context envelope

The narrative is a deterministic composition: same chronos input ⇒
same narrative bytes. No LLM, no random copy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.chronos import ChronosState
from core.hexagram import get_hexagram_by_binary
from core.yi64.derivations.derived_hexagrams import compute_all_derived
from core.yi64.derivations.mai_hoa_nntt import (
    METHOD_ID,
    SOURCE_REF,
    derivation_summary,
    derive_line_states,
)
from core.yi64.transforms import lines_to_binary, moving_lines_from_states


ROLE_LABEL = {
    "chanh": "Mặt nổi",
    "ho": "Động lực ẩn",
    "bien": "Hướng biến chuyển",
    "giao": "Mặt đối lập",
    "phuc": "Góc nhìn ngược",
    "bao": "Khung bao",
}

ROLE_DESCRIPTION = {
    "chanh": "Trạng thái đang hiển hiện trên bề mặt — điều người trong cuộc nhận thức trực tiếp.",
    "ho": "Động lực chạy ngầm bên trong (lấy từ 4 hào giữa) — chưa lộ ra nhưng đang đẩy diễn biến.",
    "bien": "Sau khi hào động chuyển, trạng thái đi về đâu — không phải lời tiên tri, là vector hướng dịch.",
    "giao": "Mặt đối nghịch hoàn toàn (lật toàn bộ 6 hào) — phần đang bị nén, không nói ra.",
    "phuc": "Lật chiều đọc lên-xuống — cách bên ngoài / đối phương / người quan sát có thể đang đọc tình huống.",
    "bao": "Khung bao xa nhất (hào 1 + hào 6 triplicated) — bối cảnh lớn ôm lấy tình huống.",
}

# State-only one-liners for each hexagram name. State, not prediction.
HEXAGRAM_STATE_PHRASES = {
    "Kiền": "năng lượng dương cương phát ra liên tục, không có chất giữ",
    "Khôn": "chất chứa, dung hòa, không phát ra mà tiếp nhận",
    "Truân": "khởi đầu nghẽn nhẹ, chất nẩy mầm chưa thông",
    "Mông": "non, mịt, cần được dẫn",
    "Nhu": "đợi đúng thời, chưa đến lúc tiến",
    "Tụng": "tranh luận, đối đầu logic",
    "Sư": "tập hợp lực lượng, có kỷ luật bên trong",
    "Tỷ": "thân cận, hợp lưu vào trung tâm",
    "Tiểu Súc": "chất giữ nhỏ, dồn nhẹ",
    "Lý": "bước đi cẩn trọng trên ranh giới",
    "Thái": "thông suốt, trên dưới giao thoa thuận",
    "Bĩ": "tắc, trên dưới không thông",
    "Đồng Nhân": "đồng minh, giao lưu mở",
    "Đại Hữu": "sở hữu lớn, sáng tỏ",
    "Khiêm": "hạ thấp đúng lúc để giữ",
    "Dự": "vui hứng, dễ buông",
    "Tùy": "thuận theo, nương theo dòng",
    "Cổ": "bê trễ, có cái đang mục cần sửa",
    "Lâm": "tiếp cận gần, sắp đến",
    "Quán": "quan sát từ trên xuống",
    "Phệ Hạp": "cắn nghiến, trừ chướng ngại",
    "Bí": "trang sức, làm đẹp bề mặt",
    "Bác": "rụng rớt, lột bỏ phần ngoài",
    "Phục": "quay về, mầm mới khởi",
    "Vô Vọng": "không vọng động, theo lẽ tự nhiên",
    "Đại Súc": "tích lũy lớn, dồn năng lượng",
    "Di": "nuôi dưỡng, ăn uống dưỡng thân",
    "Đại Quá": "vượt mức, gánh nặng",
    "Tập Khảm": "rủi ro chồng chất, hiểm liền hiểm",
    "Ly": "sáng rõ, bám víu vào nguồn sáng",
    "Hàm": "cảm ứng, hai bên rung động",
    "Hằng": "bền lâu, giữ nhịp",
    "Độn": "lùi đúng lúc, rút khỏi nguy",
    "Đại Tráng": "mạnh mẽ, cương kiện đẩy lên",
    "Tấn": "tiến lên rõ ràng",
    "Minh Di": "ánh sáng bị che, dấu mình",
    "Gia Nhân": "nội bộ gia đình, tổ chức trong nhà",
    "Khuê": "lệch hướng, nhìn nhau khác cách",
    "Kiển": "trở ngại, chân què",
    "Giải": "tháo gỡ, sau khó khăn",
    "Tổn": "bớt cái thừa để bù cái thiếu",
    "Ích": "thêm, tăng có lợi",
    "Quải": "dứt khoát, quyết liệt",
    "Cấu": "gặp gỡ bất ngờ",
    "Tụy": "tụ họp, gom lại",
    "Thăng": "tiến lên đều, thăng tiến",
    "Khốn": "kẹt, cùng đường",
    "Tỉnh": "giếng, nguồn nuôi không di chuyển",
    "Cách": "thay đổi cách mạng, cải tổ",
    "Đỉnh": "vạc nấu, kết tinh giá trị",
    "Chấn": "sấm động, kích phát đột ngột",
    "Cấn": "dừng đúng, bất động",
    "Tiệm": "tiến từ từ, từng bước",
    "Quy Muội": "trở về vị trí em gái, lệch danh phận",
    "Phong": "thịnh, đỉnh điểm",
    "Lữ": "khách lữ hành, không cố định",
    "Tốn": "thẩm thấu, len lỏi",
    "Đoài": "đối thoại, hòa duyệt",
    "Hoán": "tan rã, phân tán",
    "Tiết": "tiết chế, có chừng mực",
    "Trung Phu": "thành tín bên trong",
    "Tiểu Quá": "vượt mức nhỏ",
    "Ký Tế": "đã hoàn thành, chỉnh tề",
    "Vị Tế": "chưa hoàn thành, còn dở",
}


@dataclass(frozen=True)
class NarrativeSegment:
    role_key: str          # chanh | ho | bien | giao | phuc | bao
    role_label: str
    role_description: str
    hexagram_name: str
    hexagram_king_wen: int
    hexagram_binary: str
    state_phrase: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TimelineNarrative:
    method_id: str
    source_ref: str
    derivation: dict
    segments: tuple[NarrativeSegment, ...]
    composed_text: str

    def to_dict(self) -> dict:
        return {
            "method_id": self.method_id,
            "source_ref": self.source_ref,
            "derivation": self.derivation,
            "segments": [s.to_dict() for s in self.segments],
            "composed_text": self.composed_text,
        }


def _state_phrase(name_vi: str) -> str:
    return HEXAGRAM_STATE_PHRASES.get(name_vi, "trạng thái đặc trưng của quẻ này")


def _segment(role_key: str, primary_binary: str, derived) -> NarrativeSegment:
    hx = get_hexagram_by_binary(derived.binary_code)
    return NarrativeSegment(
        role_key=role_key,
        role_label=ROLE_LABEL[role_key],
        role_description=ROLE_DESCRIPTION[role_key],
        hexagram_name=hx.name_vi,
        hexagram_king_wen=hx.king_wen_index,
        hexagram_binary=hx.binary,
        state_phrase=_state_phrase(hx.name_vi),
    )


def _compose_text(segments: tuple[NarrativeSegment, ...]) -> str:
    """Compose a single-paragraph narrative from segments. Pure state, no advice."""
    by_role = {s.role_key: s for s in segments}
    parts = [
        f"Mặt nổi đang là quẻ {by_role['chanh'].hexagram_name} — {by_role['chanh'].state_phrase}.",
        f"Bên dưới, động lực ẩn là {by_role['ho'].hexagram_name} ({by_role['ho'].state_phrase}).",
        f"Hào động cho thấy hướng biến chuyển sang {by_role['bien'].hexagram_name} — {by_role['bien'].state_phrase}.",
        f"Mặt đối lập đang bị nén là {by_role['giao'].hexagram_name} ({by_role['giao'].state_phrase}).",
        f"Người bên ngoài có thể đang đọc tình huống dưới dạng {by_role['phuc'].hexagram_name} — {by_role['phuc'].state_phrase}.",
        f"Khung bao cảnh đặt tất cả vào {by_role['bao'].hexagram_name} ({by_role['bao'].state_phrase}).",
    ]
    return " ".join(parts)


def build_narrative(state: ChronosState) -> TimelineNarrative:
    line_states = derive_line_states(state)
    primary_binary = lines_to_binary(line_states)
    moving = moving_lines_from_states(line_states)
    derived = compute_all_derived(primary_binary, moving)

    segments = tuple(
        _segment(role_key, primary_binary, derived[role_key])
        for role_key in ("chanh", "ho", "bien", "giao", "phuc", "bao")
    )
    composed = _compose_text(segments)
    return TimelineNarrative(
        method_id=METHOD_ID,
        source_ref=SOURCE_REF,
        derivation=derivation_summary(state),
        segments=segments,
        composed_text=composed,
    )
