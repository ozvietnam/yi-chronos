"""Luận sâu Pythagoras — khung READ → GAP → IMPROVE (không predict).

Nguyên lý thư viện: data/than_so/master/interpretation_principles.json
Journal: docs/design/than-so-thu-vien-tham-nhuan.md
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from .core_numbers import reduce_number
from .interpretation import describe_number
from .library import resolve_cheiro_birth


def reduce_single(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


_DATA = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master"


@lru_cache(maxsize=1)
def _nine_year_arc() -> dict[str, str]:
    data = json.loads((_DATA / "cycles.json").read_text(encoding="utf-8"))
    return data["personal_year_month_day"]["nine_year_arc"]


@lru_cache(maxsize=1)
def _principles() -> dict:
    return json.loads((_DATA / "interpretation_principles.json").read_text(encoding="utf-8"))


# Vai trò từng chỉ số — bám nguyên lý Balliett/Cheiro/Campbell
_ROLE: dict[str, dict[str, str]] = {
    "life_path": {
        "lens": "xương sống Decoz (tháng+ngày+năm Method A) — bài học dài hạn",
        "gap_q": "Anh đang ép đời theo khuôn nào khác với khí Đường Đời?",
        "improve": "Mỗi tuần 1 việc nhỏ đúng khí Đường Đời; bỏ 1 việc chỉ vì 'phải'.",
        "source": "decoz",
    },
    "expression": {
        "lens": "rung động tên khai sinh (Balliett/Decoz) — cách anh hiện diện ra đời",
        "gap_q": "Anh đang giấu hay phô tài năng lệch với Sứ Mệnh?",
        "improve": "Làm 1 sản phẩm/việc công khai đúng Sứ Mệnh trong 30 ngày.",
        "source": "balliett+decoz",
    },
    "soul_urge": {
        "lens": "khát vọng linh hồn qua nguyên âm (Balliett) — động lực thật",
        "gap_q": "Điều anh thật sự muốn đang bị lịch nuốt không?",
        "improve": "Đặt 1 ranh giới bảo vệ khát vọng Linh Hồn mỗi tuần.",
        "source": "balliett",
    },
    "personality": {
        "lens": "lớp vỏ người khác thấy trước (phụ âm)",
        "gap_q": "Lớp vỏ Nhân Cách đang giúp hay che khuất Linh Hồn?",
        "improve": "Điều chỉnh 1 thói quen giao tiếp cho khớp hơn với bên trong.",
        "source": "decoz",
    },
    "birthday": {
        "lens": (
            "Key ngày sinh (Cheiro Ch.XV) — rung động vật chất thân thiết nhất; "
            "khác Life Path Decoz (không gộp tháng/năm vào đây)"
        ),
        "gap_q": "Anh có đang bỏ quên khí ngày sinh vì chỉ nhìn Đường Đời?",
        "improve": (
            "Neo 1 việc/tuần đúng khí Ngày Sinh (Cheiro: tập trung vào số của mình — Ch.XXIV)."
        ),
        "source": "cheiro+decoz",
    },
    "maturity": {
        "lens": "hợp lưu Đường Đời + Sứ Mệnh — lộ rõ sau ~35",
        "gap_q": "Anh đang vội 'trưởng thành' theo chuẩn ngoài hay theo số này?",
        "improve": "Viết 1 câu sứ mệnh nửa sau đời khớp Số Trưởng Thành.",
        "source": "decoz",
    },
    "attitude": {
        "lens": "phản xạ tức thì trước sự việc (tháng + ngày)",
        "gap_q": "Phản xạ Thái Độ đang cứu hay đang làm căng quan hệ?",
        "improve": "Trước quyết định nóng: thở 3 nhịp, hỏi 'Thái Độ này phục vụ gì?'.",
        "source": "decoz",
    },
}


def _series(n: int) -> str | None:
    r = reduce_number(n, keep_master=False)
    if r in (1, 4):
        return "1-4"
    if r in (2, 7):
        return "2-7"
    return None


def _name_birth_harmony(birth_day_value: int, expression_value: int) -> dict:
    """Cheiro Ch.XIV — hòa/lệch Name↔Birth; YI không khuyên đổi tên."""
    bd = reduce_number(birth_day_value, keep_master=False)
    ex = reduce_number(expression_value, keep_master=False)
    same = bd == ex
    s_bd, s_ex = _series(bd), _series(ex)
    series_link = bool(s_bd and s_bd == s_ex)
    if same:
        band = "aligned"
        read = (
            f"Birth Day {birth_day_value} và Expression {expression_value} cùng rút về {bd}: "
            "hai rung động cùng pha (Cheiro Ch.XIV). Dễ neo một số để tập trung."
        )
        gap = "Anh có đang ỷ vào sự cùng pha mà không còn quan-sát?"
        improve = (
            f"Giữ neo số {bd}: mỗi tuần 1 việc đúng khí — "
            "tập trung (Cheiro Ch.XXIV), không tán loạn chỉ số."
        )
    elif series_link:
        band = "series_affinity"
        read = (
            f"Birth Day {birth_day_value} (series {s_bd}) và Expression {expression_value} "
            f"(series {s_ex}): cùng họ 1–4 hoặc 2–7 (Cheiro Ch.I) — cảm thông nội bộ, chưa phải trùng số."
        )
        gap = "Anh đang kỳ vọng hai mặt phải giống hệt thay vì bổ sung?"
        improve = "Cho mỗi mặt một việc riêng trong tuần; đừng ép một số nuốt số kia."
    else:
        band = "offset"
        read = (
            f"Birth Day {birth_day_value}→{bd} lệch Expression {expression_value}→{ex}: "
            "Cheiro gọi là muddle khi Name↔Birth không cùng rung. "
            "YI đọc đây là GAP quan-sát — KHÔNG khuyên đổi tên để cầu may."
        )
        gap = (
            "Chỗ nào trong đời anh đang 'lộn số' — quyết định theo tên công chúng "
            "hay theo khí ngày sinh?"
        )
        improve = (
            f"Chọn MỘT neo tạm 7 ngày (Birth Day {bd} hoặc Expression {ex}), "
            "làm 1 việc đúng neo; ghi nhật ký chỗ căng — mệnh là động từ xử lý lệch pha."
        )
    care_48 = bd in (4, 8) or ex in (4, 8)
    out = {
        "band": band,
        "birth_day_root": bd,
        "expression_root": ex,
        "series_birth": s_bd,
        "series_expression": s_ex,
        "read": read,
        "gap": gap,
        "improve": improve,
        "source": "cheiro-book-of-numbers Ch.XIV (tone YI đồng dạng)",
    }
    if care_48:
        out["four_eight_note"] = (
            "Có mặt 4 hoặc 8: Cheiro cảnh báo đừng chồng thêm môi trường cùng khí. "
            "YI: hỏi anh có đang tự chất kỷ luật/cách biệt vào nhà–việc không — không dọa xui."
        )
        out["gap"] = out["gap"] + " " + out["four_eight_note"]
    return out


def _inclusion_deep(inclusion: dict) -> dict:
    missing = inclusion.get("missing") or []
    dominant = inclusion.get("dominant") or []
    return {
        "provenance": inclusion.get("provenance"),
        "read": (
            "Bảng Bao Hàm (Campbell): tần suất chữ-số trong tên là bản đồ tập luyện — "
            f"thiếu {missing or 'không'}; trội {dominant or 'không'}."
        ),
        "gap": (
            "Anh đang sợ số thiếu như 'nghiệp' hay đang tránh số trội vì nó quá mạnh?"
        ),
        "improve": (
            (
                f"Thiếu {missing}: chọn 1 số, luyện 1 thói quen thuộc khí đó trong 14 ngày. "
                if missing
                else "Không thiếu 1–9: quan-sát cân bằng thay vì tìm 'lỗ hổng'."
            )
            + (
                f"Trội {dominant}: cho một kênh biểu đạt chính đáng, tránh để ám ảnh chiếm lịch."
                if dominant
                else ""
            )
        ),
        "missing": missing,
        "dominant": dominant,
    }


def _cheiro_birth_layers(day: int, month: int, year: int) -> dict:
    d = reduce_number(day, keep_master=False)
    m = reduce_number(month, keep_master=False)
    y = reduce_number(year, keep_master=False)
    cheiro = resolve_cheiro_birth(d)
    day_node: dict = {
        "raw": day,
        "value": d,
        "role_vi": "Key cá nhân / vật chất thân thiết",
    }
    if cheiro:
        day_node["cheiro"] = {
            "planet_vi": cheiro["planet_vi"],
            "archetype_vi": cheiro["archetype_vi"],
            "keywords": cheiro["keywords"],
            "conflict_with_decoz": cheiro["conflict_with_decoz"],
            "cheiro_vs_decoz": cheiro["cheiro_vs_decoz"],
        }
    return {
        "source": "cheiro-book-of-numbers Ch.XV + Ch.III–XI",
        "note": (
            "Cheiro tách Ngày (cá nhân) · Tháng (chung) · Năm (dòng lớn) — "
            "KHÔNG cộng ba lớp. Decoz Life Path là khung khác (Iron Rule #3)."
        ),
        "day": day_node,
        "month": {"raw": month, "value": m, "role_vi": "Việc chung / bối cảnh"},
        "year": {"raw": year, "value": y, "role_vi": "Dòng lớn hơn của thời đoạn sinh"},
        "read": (
            f"Cheiro: Ngày {day}→{d}"
            + (f" ({cheiro['planet_vi']}: {cheiro['archetype_vi']})" if cheiro else "")
            + f"; tháng→{m}; năm→{y}. "
            "Ba lớp riêng — đừng gộp thành một 'số mệnh' kiểu tắt."
        ),
        "gap": "Anh đang bỏ lớp Ngày vì chỉ nhìn Life Path Decoz (đã gộp tháng+năm)?",
        "improve": f"Tuần này neo khí Ngày {d} trong 1 quyết định nhỏ — tập trung (Ch.XXIV).",
    }


def _enrich_birthday_dual_lens(node: dict) -> dict:
    """Birthday: Cheiro Birth + Decoz — present BOTH khi conflict (#3)."""
    cheiro = resolve_cheiro_birth(node["value"])
    if not cheiro:
        return node
    decoz_arch = node.get("archetype_vi", "")
    node["cheiro_birth"] = cheiro
    node["decoz_lens"] = {
        "archetype_vi": decoz_arch,
        "keywords": node.get("keywords") or [],
        "note": "Decoz Birthday Number (từ number_meanings) — khung khác Cheiro.",
    }
    conflict = cheiro["conflict_with_decoz"]
    if conflict:
        node["read"] = (
            f"Ngày Sinh = {node['value']}. "
            f"Cheiro ({cheiro['planet_vi']}): {cheiro['archetype_vi']}. "
            f"Decoz: {decoz_arch}. "
            f"Hai khung lệch — giữ BOTH (#3): {cheiro['cheiro_vs_decoz']} "
            f"Key Cheiro = vật chất thân thiết nhất; đừng gộp vào Life Path."
        )
        node["gap"] = (
            f"Anh đang chỉ nghe một trường (Cheiro hoặc Decoz) cho số {node['value']}? "
            f"{node.get('gap', '')}"
        ).strip()
        node["archetype_vi"] = (
            f"Cheiro: {cheiro['archetype_vi']} · Decoz: {decoz_arch}"
        )
    else:
        node["read"] = (
            f"Ngày Sinh = {node['value']} — Cheiro {cheiro['planet_vi']}: "
            f"{cheiro['archetype_vi']}. "
            f"(Decoz cùng hướng: {decoz_arch}.) "
            f"Đây là Key ngày sinh thân thiết nhất — khác Life Path đã gộp tháng/năm."
        )
        node["archetype_vi"] = cheiro["archetype_vi"]
    node["keywords"] = list(
        dict.fromkeys((cheiro.get("keywords") or []) + (node.get("keywords") or []))
    )
    node["source_principle"] = "cheiro+decoz"
    return node


def _deep_one(role_key: str, value: int, name_vi: str) -> dict:
    desc = describe_number(value)
    role = _ROLE.get(
        role_key,
        {
            "lens": "một mặt cấu trúc số",
            "gap_q": "Mặt này đang lệch chỗ nào trong đời sống?",
            "improve": "Quan-sát 7 ngày rồi chọn 1 điều chỉnh nhỏ.",
            "source": "",
        },
    )
    strengths = desc.get("strengths") or ""
    shadow = desc.get("shadow") or ""
    return {
        "role": role_key,
        "name_vi": name_vi,
        "value": value,
        "archetype_vi": desc.get("archetype_vi", ""),
        "source_principle": role.get("source", ""),
        "read": (
            f"{name_vi} = {value} ({desc.get('archetype_vi', '')}). "
            f"Đây là {role['lens']}. "
            f"Khi vận hành tốt: {strengths} "
            f"{desc.get('dong_dang') or ''}"
        ).strip(),
        "gap": (f"Bóng của số {value}: {shadow} {role['gap_q']}").strip(),
        "improve": role["improve"],
        "keywords": desc.get("keywords", []),
        "is_master": desc.get("is_master", False),
    }


def compose_deep_reading(
    core: dict,
    extended: dict | None = None,
    cycles: dict | None = None,
    *,
    birth_day: int | None = None,
    birth_month: int | None = None,
    birth_year: int | None = None,
) -> dict:
    """Trả deep_core + layers nguyên lý thư viện + cycle guidance."""
    deep_core = {}
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        node = core[key]
        deep_core[key] = _deep_one(key, node["value"], node["name_vi"])
    deep_core["birthday"] = _enrich_birthday_dual_lens(deep_core["birthday"])

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
                    "read": (
                        f"Số {n} thiếu trong tên (Campbell Inclusion) — "
                        "phẩm chất chưa được 'tập' qua chữ cái khai sinh; không phải án nghiệp."
                    ),
                    "gap": f"Đời có kéo anh vào tình huống đòi hỏi phẩm chất số {n} mà anh né?",
                    "improve": f"Chủ động luyện 1 thói quen thuộc khí số {n} mỗi tuần.",
                    "provenance": "campbell-your-days-are-numbered",
                }
                for n in lessons["values"]
            ]
        passion = extended.get("hidden_passion") or {}
        if passion.get("values"):
            deep_ext["hidden_passion"] = [
                {
                    "number": n,
                    **describe_number(n),
                    "read": (
                        f"Số {n} trội trong tên (Campbell) — đam mê/ám ảnh nổi; "
                        "dùng có ý thức kẻo chiếm hết lịch."
                    ),
                    "gap": "Đam mê này đang được nuôi lành hay bị đè / bị phóng đại?",
                    "improve": f"Cho số {n} một kênh biểu đạt chính đáng trong tháng.",
                    "provenance": "campbell-your-days-are-numbered",
                }
                for n in passion["values"]
            ]
        if extended.get("inclusion_table"):
            deep_ext["inclusion"] = _inclusion_deep(extended["inclusion_table"])
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

    bd_val = core["birthday"]["value"]
    if birth_day is not None:
        bd_val = reduce_number(birth_day)
    harmony = _name_birth_harmony(bd_val, core["expression"]["value"])

    layers: dict = {
        "name_birth_harmony": harmony,
        "principle_ids": [p["id"] for p in _principles().get("principles") or []],
        "reading_steps": _principles().get("reading_steps") or [],
        "forbid": _principles().get("forbid_user_facing") or [],
        "journal": "docs/design/than-so-thu-vien-tham-nhuan.md",
    }
    if birth_day is not None and birth_month is not None and birth_year is not None:
        layers["cheiro_birth_layers"] = _cheiro_birth_layers(birth_day, birth_month, birth_year)

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
            e, y = duality["essence"], duality["personal_year"]
            cycle_guidance["duality"] = {
                "essence": e,
                "personal_year": y,
                "read": (
                    f"Duality năm này: Essence {e} × Năm cá nhân {y}. "
                    f"Essence = khí từ chữ cái tên theo tuổi; Năm CN = khí từ ngày sinh + năm lịch. "
                    f"Đọc chung: {arc.get(str(e), f'số {e}')} gặp {arc.get(str(y), f'số {y}')}."
                ),
                "gap": "Anh đang chỉ nghe một phía (tên hoặc ngày sinh) và bỏ phía kia?",
                "improve": (
                    "Khi lập kế hoạch tháng: hỏi cả Essence (tên–tuổi) và Năm cá nhân (ngày sinh)."
                ),
                "actions": list(dict.fromkeys(_year_actions(e)[:1] + _year_actions(y)[:2])),
            }
        essence = cycles.get("essence")
        if essence:
            cycle_guidance["essence"] = {
                "value": essence["value"],
                "read": f"Essence tuổi hiện tại = {essence['value']} (từ Transit tên).",
                "improve": f"Quan-sát chủ đề số {essence['value']} trong các quyết định lớn năm nay.",
            }
        timeline = cycles.get("transit_timeline") or []
        if timeline:
            cycle_guidance["transit_timeline_hint"] = (
                f"Timeline Transit/Essence {len(timeline)} tuổi tới — "
                "quan-sát chữ cái đổi và Essence đổi, không đoán cát/hung."
            )
        pinnacles = cycles.get("pinnacles") or []
        if pinnacles:
            cycle_guidance["pinnacles"] = [
                {
                    "index": p["index"],
                    "value": p["value"],
                    "age_range": p.get("age_range"),
                    "read": (
                        f"Đỉnh {p['index']} = {p['value']} (tuổi {p.get('age_range', '?')}): "
                        f"môi trường / cơ hội bên ngoài của giai đoạn. "
                        f"{arc.get(str(reduce_single(p['value'])), '')}"
                    ),
                    "improve": _year_actions(reduce_single(p["value"]))[:2],
                }
                for p in pinnacles
            ]
        challenges = cycles.get("challenges") or []
        if challenges:
            cycle_guidance["challenges"] = [
                {
                    "index": c["index"],
                    "value": c["value"],
                    "main": bool(c.get("main")),
                    "read": (
                        f"Thử thách {c['index']}{' (Chính)' if c.get('main') else ''} = {c['value']}: "
                        f"bài học nội tâm cần rèn — không phải án. "
                        f"{'Đây là thử thách xuyên suốt đời.' if c.get('main') else ''}"
                    ),
                    "improve": (
                        f"Khi căng: hỏi 'Thử thách {c['value']} đang dạy gì?' rồi chọn 1 hành vi nhỏ ngược bóng."
                    ),
                }
                for c in challenges
            ]
        ycal = cycles.get("personal_year_calendar") or []
        if ycal:
            cycle_guidance["personal_year_calendar_hint"] = (
                f"Chuỗi {len(ycal)} năm cá nhân tới — đọc khí từng năm, không đoán thắng/thua."
            )

    return {
        "method": "READ→GAP→IMPROVE",
        "disclaimer": (
            "Thần Số ở YI MƯỢN khung soi tâm (Balliett/Campbell/Cheiro/Decoz) — "
            "không phải lời tiên tri. Lá số không thay tu học hay y tế. "
            "Không chẩn bệnh theo số; không tư vấn cá cược / xổ số."
        ),
        "core": deep_core,
        "extended": deep_ext,
        "cycles": cycle_guidance,
        "layers": layers,
        "synthesis": {
            "read": harmony["read"],
            "gap": harmony["gap"],
            "improve": harmony["improve"],
            "steps": layers["reading_steps"],
        },
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
    return [f"(Tháng) {a}" for a in _year_actions(n)[:2]]
