"""Soạn luận giải — paradigm ĐỌC ĐỒNG DẠNG, KHÔNG predict.

Lấy ý nghĩa từ number_meanings.json + karmic_debt.json.
Lớp plain_* = tiếng người thường đọc được (không jargon Decoz/Cheiro).
"""
from __future__ import annotations

from .constants import karmic_meanings, number_meanings


CORE_PLAIN_ROLE = {
    "life_path": (
        "Số Đường Đời",
        "việc chính dài hạn của đời này — bạn vận hành tốt nhất khi sống đúng khí này",
    ),
    "expression": (
        "Số Sứ Mệnh",
        "cách bạn hiện diện ra đời qua tên khai sinh — người khác thường thấy mặt này trước",
    ),
    "soul_urge": (
        "Số Linh Hồn",
        "điều bạn thật sự muốn ở bên trong (qua nguyên âm trong tên)",
    ),
    "personality": (
        "Số Nhân Cách",
        "lớp vỏ bên ngoài — ấn tượng đầu khi người ta gặp bạn",
    ),
    "birthday": (
        "Số Ngày Sinh",
        "khí ngày sinh riêng — gần gũi, cụ thể hơn Đường Đời",
    ),
    "maturity": (
        "Số Trưởng Thành",
        "hướng hợp lưu Đường Đời + Sứ Mệnh, lộ rõ hơn sau tuổi ~35",
    ),
}


def _meaning(value: int) -> dict | None:
    return number_meanings().get(str(value))


def describe_number(value: int) -> dict:
    m = _meaning(value)
    if not m:
        return {
            "value": value,
            "archetype_vi": f"Số {value}",
            "plain_vi": "",
            "practice_vi": "",
            "note": "Chưa có dữ liệu.",
        }
    return {
        "value": value,
        "archetype_vi": m.get("archetype_vi", ""),
        "keywords": m.get("keywords", []),
        "strengths": m.get("strengths", ""),
        "shadow": m.get("shadow", ""),
        "plain_vi": m.get("plain_vi", ""),
        "practice_vi": m.get("practice_vi", ""),
        "master_note_vi": m.get("master_note_vi", ""),
        "dong_dang": m.get("dong_dang", ""),
        "is_master": m.get("is_master", False),
    }


def interpret_core(core: dict) -> dict:
    out: dict[str, dict] = {}
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        node = core[key]
        out[key] = {
            "name_vi": node["name_vi"],
            **describe_number(node["value"]),
        }
    return out


def _karmic_where(core: dict, key: str, kd: int) -> str:
    """Giải thích bài học kèm xuất hiện từ đâu — tiếng thường."""
    node = core.get(key) or {}
    raw = node.get("raw")
    if raw == kd:
        return f"Tổng trước khi rút gọn = {kd} → rút về {node.get('value')}."
    parts = node.get("parts") or []
    for pt in parts:
        if pt.get("karmic_debt") == kd:
            return (
                f"Phần tên «{pt.get('part')}» cộng chữ cái = {kd} "
                f"(rút về {pt.get('reduced')}) — gắn vào {node.get('name_vi', key)}."
            )
    steps = node.get("steps") or []
    if kd in steps:
        return f"Trong các bước rút gọn {steps} có số {kd}."
    return f"Xuất hiện trên {node.get('name_vi', key)}."


def collect_karmic(core: dict) -> list[dict]:
    debts: list[dict] = []
    seen: set[int] = set()
    km = karmic_meanings()
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        if key not in core:
            continue
        kd = core[key].get("karmic_debt")
        if not kd or kd in seen:
            continue
        seen.add(kd)
        info = km.get(str(kd), {})
        base_plain = info.get("plain_vi") or info.get("this_life", "")
        core_val = core[key].get("value")
        reduces = info.get("reduces_to")
        where = _karmic_where(core, key, kd)
        # Nợ từ phần tên / bước trung gian ≠ số cốt lõi đã rút → nói rõ ngữ cảnh
        if (
            base_plain
            and reduces is not None
            and core_val is not None
            and int(core_val) != int(reduces)
            and core[key].get("raw") != kd
        ):
            plain = f"Trên {core[key]['name_vi']} = {core_val}: {where} {base_plain}"
        else:
            plain = base_plain
        debts.append(
            {
                "number": kd,
                "source": core[key]["name_vi"],
                "source_key": key,
                "reduces_to": reduces,
                "core_value": core_val,
                "where_vi": where,
                "label_vi": "Bài học kèm",
                "theme_vi": info.get("theme_vi", ""),
                "plain_vi": plain,
                "practice_vi": info.get("practice_vi", ""),
                "avoid_vi": info.get("avoid_vi", ""),
                "this_life": info.get("this_life", ""),
                "dong_dang": info.get("dong_dang", ""),
            }
        )
    return debts


def compose_plain_summary(core: dict, cycles: dict | None = None) -> dict:
    """Tóm tắt tiếng người thường — đọc được trong ~30 giây. Luôn có cho mọi lá số."""
    debts = collect_karmic(core)
    debt_by_key = {d["source_key"]: d for d in debts}
    core_cards: list[dict] = []
    bullets: list[str] = []
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday"):
        node = core.get(key) or {}
        value = node.get("value")
        if value is None:
            continue
        role_name, role_hint = CORE_PLAIN_ROLE[key]
        desc = describe_number(value)
        arch = desc.get("archetype_vi") or f"Số {value}"
        plain = (desc.get("plain_vi") or "").strip()
        practice = (desc.get("practice_vi") or "").strip()
        master_note = (desc.get("master_note_vi") or "").strip()
        core_cards.append(
            {
                "role": key,
                "role_label": role_name,
                "role_hint": role_hint,
                "value": value,
                "archetype_vi": arch,
                "plain_vi": plain,
                "practice_vi": practice,
                "master_note_vi": master_note,
                "is_master": bool(desc.get("is_master")),
                "shadow_vi": desc.get("shadow") or "",
            }
        )
        if plain:
            bullets.append(f"{role_name} = {value} ({arch}): {plain}")
        else:
            strengths = (desc.get("strengths") or "").rstrip(".")
            shadow = (desc.get("shadow") or "").rstrip(".")
            bullets.append(
                f"{role_name} = {value} ({arch}): {role_hint}. "
                f"Khi thuận: {strengths}. Dễ lệch khi: {shadow}."
            )
        if master_note:
            bullets.append(f"→ Lưu ý số chủ {value}: {master_note}")
        if key in debt_by_key:
            d = debt_by_key[key]
            bullets.append(f"→ Bài học kèm {d['number']} trên {role_name}: {d['plain_vi']}")

    py = (cycles or {}).get("personal_year") or {}
    if py.get("value") is not None:
        py_desc = describe_number(py["value"])
        py_plain = (py_desc.get("plain_vi") or "").strip()
        if py_plain:
            bullets.append(
                f"Năm cá nhân {py.get('target_year')} = {py['value']} "
                f"({py_desc.get('archetype_vi', '')}): khí năm nay để quan-sát — "
                f"{py_plain} (không phải lời đoán được/mất)."
            )
        else:
            bullets.append(
                f"Năm cá nhân {py.get('target_year')} = {py['value']} "
                f"({py_desc.get('archetype_vi', '')}): khí năm nay để quan-sát — "
                f"không phải lời đoán được/mất."
            )

    practice = None
    if debts:
        pick = next((d for d in debts if d.get("source_key") == "life_path"), debts[0])
        practice = pick.get("practice_vi") or None

    if not practice:
        lp_val = core.get("life_path", {}).get("value")
        if lp_val is not None:
            practice = (describe_number(lp_val).get("practice_vi") or "").strip() or None

    if not practice:
        practice = (
            "Tuần này chọn 1 việc nhỏ đúng khí Đường Đời "
            f"(số {core.get('life_path', {}).get('value', '?')}) và làm cho xong — "
            "chỉ một việc."
        )

    return {
        "title_vi": "Tóm tắt dễ hiểu",
        "intro_vi": (
            "Đọc số như đọc bản đồ cấu trúc — không phải lời tiên tri. "
            "Mỗi số nói 'bạn vận hành tốt khi…' và 'dễ lệch khi…'."
        ),
        "bullets": bullets,
        "core_cards": core_cards,
        "one_practice_vi": practice,
        "how_to_use_vi": (
            "Cách dùng: lấy Đường Đời làm trục chính; "
            "Sứ Mệnh / Linh Hồn / Nhân Cách / Ngày Sinh là góc nhìn bổ sung. "
            "Nếu có «bài học kèm», đó là chỗ cần luyện thêm — không phải lời nguyền. "
            "Phần «Việc nhỏ tuần này» là cách xử lý tính (mệnh là động từ)."
        ),
        "karmic_intro_vi": (
            "«Bài học kèm» không phải án kiếp trước. "
            "Nghĩa là: bạn vẫn mang khí số đã rút, nhưng cần luyện thêm một thói quen cụ thể."
            if debts
            else None
        ),
    }


PARADIGM_NOTE = (
    "Thần Số ở đây đọc cấu trúc qua số — không bói tốt/xấu. "
    "Câu hỏi đúng: 'cấu trúc này mời bạn quan-sát và luyện điều gì?', "
    "không phải 'tương lai sẽ ra sao'."
)


def compose_reading(core: dict, cycles: dict | None = None, extended: dict | None = None) -> dict:
    reading: dict = {
        "paradigm_note": PARADIGM_NOTE,
        "core": interpret_core(core),
        "karmic_debts": collect_karmic(core),
        "plain_summary": compose_plain_summary(core, cycles),
    }
    if extended:
        att = extended.get("attitude")
        if att:
            reading["attitude"] = describe_number(att["value"])
        lessons = extended.get("karmic_lessons") or {}
        if lessons.get("values"):
            reading["karmic_lessons"] = [
                {"number": n, **describe_number(n)} for n in lessons["values"]
            ]
        passion = extended.get("hidden_passion") or {}
        if passion.get("values"):
            reading["hidden_passion"] = [
                {"number": n, **describe_number(n)} for n in passion["values"]
            ]
        bridges = extended.get("bridges") or {}
        reading["bridges"] = {
            k: {"value": v["value"], "name_vi": v["name_vi"], **describe_number(v["value"])}
            for k, v in bridges.items()
        }
    if cycles:
        reading["cycles_hint"] = (
            "Chu kỳ (Đỉnh Vận / Thử Thách / Năm–Tháng–Ngày Cá Nhân) "
            "là khí giai đoạn để quan-sát — không predict được-mất."
        )
        py = cycles.get("personal_year")
        if py:
            reading["personal_year"] = {
                "target_year": py["target_year"],
                **describe_number(py["value"]),
            }
    return reading
