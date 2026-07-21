"""Luận sâu Pythagoras — khung READ → GAP → IMPROVE (không predict).

Mỗi số: đọc cấu trúc → nhận vùng lệch → gợi ý vận hành.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from .constants import number_meanings
from .interpretation import describe_number

_DATA = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master"


@lru_cache(maxsize=1)
def _nine_year_arc() -> dict[str, str]:
    data = json.loads((_DATA / "cycles.json").read_text(encoding="utf-8"))
    return data["personal_year_month_day"]["nine_year_arc"]


# Vai trò từng chỉ số trong lá số — dùng để viết READ/GAP/IMPROVE sát ngữ cảnh
_ROLE: dict[str, dict[str, str]] = {
    "life_path": {
        "lens": "xương sống đời — bài học lớn và hướng vận hành dài hạn",
        "gap_q": "Anh đang ép đời mình đi theo khuôn nào khác với khí này?",
        "improve": "Mỗi tuần chọn 1 việc nhỏ đúng khí Đường Đời; bỏ 1 việc chỉ vì 'phải'.",
    },
    "expression": {
        "lens": "tài năng / cách anh hiện diện ra thế giới qua tên khai sinh",
        "gap_q": "Anh đang giấu hay phô phần tài năng nào lệch với Số Sứ Mệnh?",
        "improve": "Làm 1 sản phẩm/việc công khai đúng Sứ Mệnh trong 30 ngày.",
    },
    "soul_urge": {
        "lens": "khát vọng nội tâm (nguyên âm) — động lực thật",
        "gap_q": "Điều anh thật sự muốn có đang bị lịch làm việc nuốt không?",
        "improve": "Đặt 1 ranh giới bảo vệ khát vọng Linh Hồn mỗi tuần.",
    },
    "personality": {
        "lens": "lớp vỏ người khác thấy trước (phụ âm)",
        "gap_q": "Lớp vỏ Nhân Cách đang giúp hay đang che khuất Linh Hồn?",
        "improve": "Điều chỉnh 1 thói quen giao tiếp cho khớp hơn với bên trong.",
    },
    "birthday": {
        "lens": "món quà / năng khiếu đặc thù trong ngày sinh",
        "gap_q": "Năng khiếu Ngày Sinh đang được dùng hay để khô?",
        "improve": "Dành 2 giờ/tuần luyện đúng món quà Ngày Sinh.",
    },
    "maturity": {
        "lens": "hợp lưu Đường Đời + Sứ Mệnh — lộ rõ sau ~35",
        "gap_q": "Anh đang vội 'trưởng thành' theo chuẩn ngoài hay theo số này?",
        "improve": "Viết 1 câu sứ mệnh nửa sau đời khớp Số Trưởng Thành.",
    },
    "attitude": {
        "lens": "phản xạ tức thì trước sự việc (tháng + ngày)",
        "gap_q": "Phản xạ Thái Độ đang cứu hay đang làm căng quan hệ?",
        "improve": "Trước quyết định nóng: thở 3 nhịp, hỏi 'Thái Độ này phục vụ gì?'.",
    },
}


def _deep_one(role_key: str, value: int, name_vi: str) -> dict:
    desc = describe_number(value)
    role = _ROLE.get(role_key, {
        "lens": "một mặt cấu trúc số",
        "gap_q": "Mặt này đang lệch chỗ nào trong đời sống?",
        "improve": "Quan-sát 7 ngày rồi chọn 1 điều chỉnh nhỏ.",
    })
    strengths = desc.get("strengths") or ""
    shadow = desc.get("shadow") or ""
    return {
        "role": role_key,
        "name_vi": name_vi,
        "value": value,
        "archetype_vi": desc.get("archetype_vi", ""),
        "read": (
            f"{name_vi} = {value} ({desc.get('archetype_vi', '')}). "
            f"Đây là {role['lens']}. "
            f"Khi vận hành tốt: {strengths} "
            f"{desc.get('dong_dang') or ''}"
        ).strip(),
        "gap": (
            f"Bóng của số {value}: {shadow} "
            f"{role['gap_q']}"
        ).strip(),
        "improve": role["improve"],
        "keywords": desc.get("keywords", []),
        "is_master": desc.get("is_master", False),
    }


def compose_deep_reading(core: dict, extended: dict | None = None, cycles: dict | None = None) -> dict:
    """Trả deep_core + deep_extended + cycle_guidance theo READ/GAP/IMPROVE."""
    deep_core = {}
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        node = core[key]
        deep_core[key] = _deep_one(key, node["value"], node["name_vi"])

    deep_ext: dict = {}
    if extended:
        if extended.get("attitude"):
            deep_ext["attitude"] = _deep_one(
                "attitude", extended["attitude"]["value"], "Số Thái Độ"
            )
        lessons = extended.get("karmic_lessons") or {}
        if lessons.get("values"):
            deep_ext["karmic_lessons"] = [
                {
                    "number": n,
                    **describe_number(n),
                    "read": f"Số {n} thiếu trong tên — vùng chưa được 'tập' qua chữ cái khai sinh.",
                    "gap": f"Đời có thể kéo anh vào tình huống đòi hỏi phẩm chất số {n}.",
                    "improve": f"Chủ động luyện 1 thói quen thuộc khí số {n} mỗi tuần.",
                }
                for n in lessons["values"]
            ]
        passion = extended.get("hidden_passion") or {}
        if passion.get("values"):
            deep_ext["hidden_passion"] = [
                {
                    "number": n,
                    **describe_number(n),
                    "read": f"Số {n} xuất hiện nhiều nhất trong tên — đam mê/ám ảnh nổi trội.",
                    "gap": "Đam mê này đang được nuôi hay bị lịch làm việc đè?",
                    "improve": f"Cho số {n} một kênh biểu đạt chính đáng (dự án/sở thích) trong tháng.",
                }
                for n in passion["values"]
            ]
        bridges = extended.get("bridges") or {}
        for bk, bv in bridges.items():
            deep_ext[f"bridge_{bk}"] = {
                "name_vi": bv["name_vi"],
                "value": bv["value"],
                **describe_number(bv["value"]),
                "read": (
                    f"{bv['name_vi']} = {bv['value']}: khoảng cách cần bắc cầu giữa hai mặt. "
                    f"Không phải lỗi — là khoảng luyện."
                ),
                "gap": "Anh đang đứng về một phía và phủ nhận phía kia?",
                "improve": f"Mỗi tuần làm 1 việc mang khí số cầu {bv['value']} để nối hai phía.",
            }

    cycle_guidance: dict = {}
    arc = _nine_year_arc()
    if cycles:
        py = cycles.get("personal_year")
        if py:
            v = str(py["value"])
            cycle_guidance["personal_year"] = {
                "target_year": py["target_year"],
                "value": py["value"],
                "arc": arc.get(v, ""),
                "read": f"Năm cá nhân {py['target_year']} = {py['value']}: {arc.get(v, '')}.",
                "gap": "Anh đang dùng năm này như năm nào khác trong chu kỳ 9?",
                "improve": _year_actions(py["value"]),
            }
        pm = cycles.get("personal_month")
        if pm:
            cycle_guidance["personal_month"] = {
                "value": pm["value"],
                "target_year": pm["target_year"],
                "target_month": pm["target_month"],
                "arc": arc.get(str(pm["value"]), ""),
                "improve": _month_actions(pm["value"]),
            }
        duality = cycles.get("duality")
        if duality:
            cycle_guidance["duality"] = {
                "essence": duality["essence"],
                "personal_year": duality["personal_year"],
                "read": (
                    f"Duality năm này: Essence {duality['essence']} × "
                    f"Năm cá nhân {duality['personal_year']} — đọc chung, không tách."
                ),
                "improve": (
                    "Khi lập kế hoạch tháng: hỏi cả Essence (tên–tuổi) và Năm cá nhân (ngày sinh)."
                ),
            }
        essence = cycles.get("essence")
        if essence:
            cycle_guidance["essence"] = {
                "value": essence["value"],
                "read": f"Essence tuổi hiện tại = {essence['value']} (từ Transit tên).",
                "improve": f"Quan-sát chủ đề số {essence['value']} trong các quyết định lớn năm nay.",
            }

    return {
        "method": "READ→GAP→IMPROVE",
        "disclaimer": (
            "Tử Vi/Thần Số ở YI MƯỢN khung soi tâm — không phải lời tiên tri. "
            "Lá số không thay tu học hay y tế."
        ),
        "core": deep_core,
        "extended": deep_ext,
        "cycles": cycle_guidance,
    }


def _year_actions(n: int) -> list[str]:
    table = {
        1: ["Gieo 1 dự án mới", "Giảm phụ thuộc ý kiến đám đông", "Chốt 1 cam kết độc lập"],
        2: ["Nuôi quan hệ then chốt", "Kiên nhẫn với tiến độ chậm", "Lắng nghe trước khi đẩy"],
        3: ["Xuất hiện / viết / nói", "Mở mạng lưới xã hội lành", "Tránh dàn trải quá nhiều ý"],
        4: ["Xây quy trình & kỷ luật", "Dọn nợ việc / nợ tiền nhỏ", "Ưu tiên nền tảng hơn tốc độ"],
        5: ["Cho phép thay đổi có kiểm soát", "Học kỹ năng mới", "Tránh quyết định all-in bốc đồng"],
        6: ["Chăm sóc nhà / đội", "Sửa quan hệ rạn", "Biết nói không với ôm đồm"],
        7: ["Dành thời gian nội quán", "Học sâu 1 chủ đề", "Giảm ồn ào mạng xã hội"],
        8: ["Chốt thành quả vật chất có đạo đức", "Nhìn lại quyền lực đang dùng", "Công bằng với người cộng tác"],
        9: ["Hoàn tất & buông", "Tha thứ / kết thúc chu kỳ", "Dọn chỗ cho năm 1 sắp tới"],
    }
    return table.get(n, ["Quan-sát khí năm", "Chọn 1 việc đúng khí", "Bỏ 1 việc lệch khí"])


def _month_actions(n: int) -> list[str]:
    # Rút gọn từ năm — checklist tháng
    return [f"(Tháng) {a}" for a in _year_actions(n)[:2]]
