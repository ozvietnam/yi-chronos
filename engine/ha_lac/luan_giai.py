"""Bát Tự Hà Lạc — luận giải tổng hợp (synthesizer).

Paradigm (Iron Rule #4+6): Hà Lạc KHÔNG dự đoán "anh sẽ giàu". Hà Lạc đọc
**cấu trúc 2 quẻ + 12 hào trajectory** → giúp tri mệnh, biết mình ở giai đoạn nào
trong tổng thể 84-90 năm cuộc đời.

Source: Học Năng, _Bát Tự Hà Lạc Lược Khảo_, Saigon 1974.

Algorithm:
1. Tiên thiên quái → đọc nghĩa quẻ + nguyên đường (cốt mệnh)
2. Hậu thiên quái → đọc nghĩa quẻ + nguyên đường (vận dụng)
3. So sánh Tiên ↔ Hậu (sinh/khắc/trùng lặp → narrative)
4. 12 hào trajectory → highlight giai đoạn nguyên đường
5. Current stage (theo current_age) → đang ở giai đoạn nào
6. Cross-ref với Kinh Dịch (2 quẻ thuộc 64 quẻ classical)
7. Bổ Hướng cho giai đoạn hiện tại
"""

from __future__ import annotations

# Trigram → element mapping (cho so sánh Tiên-Hậu sinh/khắc)
TRIGRAM_TO_ELEMENT: dict[str, str] = {
    "Càn":  "kim",
    "Đoài": "kim",
    "Ly":   "hỏa",
    "Chấn": "mộc",
    "Tốn":  "mộc",
    "Khảm": "thủy",
    "Cấn":  "thổ",
    "Khôn": "thổ",
}

# Element relations
ELEMENT_GENERATES = {
    "mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc",
}
ELEMENT_CONTROLS = {
    "mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc",
}

# Position labels theo phase Tiên thiên (đời đầu - giữa)
TIEN_PHASE_LABELS = {
    1: "Tuổi thiếu thời / hạt giống bẩm sinh",
    2: "Tuổi vào đời / mở rộng học vấn",
    3: "Tuổi lập thân / xây nền nghiệp",
    4: "Tuổi thành nhân / hôn nhân + xây gia đình",
    5: "Tuổi viên mãn / đỉnh cao sự nghiệp đời đầu",
    6: "Tuổi chuyển giao / kết thúc giai đoạn Tiên thiên",
}

# Position labels theo phase Hậu thiên (đời giữa - cuối)
HAU_PHASE_LABELS = {
    1: "Tuổi tái khởi / khởi đầu vận dụng",
    2: "Tuổi cải mệnh / điều chỉnh hướng",
    3: "Tuổi đẩy mạnh / phát triển bền vững",
    4: "Tuổi truyền lại / chuyển giao thế hệ",
    5: "Tuổi đạt đạo / chiêm nghiệm",
    6: "Tuổi an dưỡng / kết thúc quỹ đạo",
}


METHOD_ID = "bat_tu_ha_lac_luan_giai_v1"
SOURCE_REF = "Học Năng, _Bát Tự Hà Lạc Lược Khảo_, Saigon 1974."


def _compose_overview(ha_lac_state: dict, address: str = "bạn") -> str:
    """Lead paragraph paradigm. `address` = đại từ xưng hô (mặc định trung tính 'bạn'
    cho mọi user; trang founder có thể truyền 'Anh')."""
    tien = ha_lac_state["tien_thien_quai"]
    hau = ha_lac_state["hau_thien_quai"]
    span = ha_lac_state["lifespan_span"]
    return (
        f"**Tiên Thiên Quái** = {tien['name_vi']} (quẻ {tien['king_wen_index']}, "
        f"thượng {tien['upper_trigram']} / hạ {tien['lower_trigram']}) — **cốt mệnh** của {address}. "
        f"**Hậu Thiên Quái** = {hau['name_vi']} (quẻ {hau['king_wen_index']}, "
        f"thượng {hau['upper_trigram']} / hạ {hau['lower_trigram']}) — **cách vận dụng** thực tế. "
        f"Cuộc đời chia thành **12 hào** ~ {span['total_years']} năm (hào dương 9 năm, hào âm 6 năm). "
        f"Mục đích Hà Lạc: KHÔNG dự đoán kết quả — phản chiếu cấu trúc 2 quẻ + đường đi 12 giai đoạn → tri mệnh."
    )


def _luan_quai(quai: dict, role: str, phase_labels: dict[int, str]) -> dict:
    """Luận 1 quẻ (Tiên hoặc Hậu) — meaning + nguyên đường role."""
    nd_line = quai["nguyen_duong_line"]
    nd_phase = phase_labels.get(nd_line, "")
    return {
        "role": role,
        "name_vi": quai["name_vi"],
        "king_wen": quai["king_wen_index"],
        "upper_trigram": quai["upper_trigram"],
        "lower_trigram": quai["lower_trigram"],
        "upper_element": TRIGRAM_TO_ELEMENT[quai["upper_trigram"]],
        "lower_element": TRIGRAM_TO_ELEMENT[quai["lower_trigram"]],
        "nguyen_duong_line": nd_line,
        "nguyen_duong_phase": nd_phase,
        "narrative": (
            f"{role} = **{quai['name_vi']}** (quẻ {quai['king_wen_index']}, "
            f"{quai['upper_trigram']} trên {quai['lower_trigram']} dưới). "
            f"Nguyên Đường rơi vào **hào {nd_line}** — giai đoạn chủ chốt: {nd_phase}."
        ),
    }


def _compare_tien_hau(tien: dict, hau: dict) -> dict:
    """So sánh Tiên ↔ Hậu: sinh/khắc/trùng lặp + ngũ hành thượng quái."""
    tien_upper_el = TRIGRAM_TO_ELEMENT[tien["upper_trigram"]]
    hau_upper_el = TRIGRAM_TO_ELEMENT[hau["upper_trigram"]]
    if tien["king_wen_index"] == hau["king_wen_index"]:
        return {
            "pattern": "trùng lặp",
            "narrative": (
                f"Tiên thiên = Hậu thiên = **{tien['name_vi']}** — "
                f"cuộc đời thuần khí, đặc tính bẩm sinh và vận dụng cùng 1 hướng. "
                f"Hiếm gặp."
            ),
        }
    if tien_upper_el == hau_upper_el:
        pattern = "tỷ hòa"
        rel = f"Cả hai thượng quái cùng hành {tien_upper_el.title()} → tỷ hòa, vận thuận."
    elif ELEMENT_GENERATES[tien_upper_el] == hau_upper_el:
        pattern = "Tiên sinh Hậu"
        rel = (
            f"Thượng quái Tiên ({tien_upper_el.title()}) → sinh Hậu ({hau_upper_el.title()}) → "
            f"vận thuận, cốt mệnh nuôi dưỡng cách vận dụng."
        )
    elif ELEMENT_GENERATES[hau_upper_el] == tien_upper_el:
        pattern = "Hậu sinh Tiên (nghịch)"
        rel = (
            f"Thượng quái Hậu ({hau_upper_el.title()}) → sinh Tiên ({tien_upper_el.title()}) → "
            f"vận dụng quay lại nuôi cốt mệnh, nghịch nhưng có ích."
        )
    elif ELEMENT_CONTROLS[tien_upper_el] == hau_upper_el:
        pattern = "Tiên khắc Hậu"
        rel = (
            f"Thượng quái Tiên ({tien_upper_el.title()}) khắc Hậu ({hau_upper_el.title()}) → "
            f"cốt mệnh cản trở cách vận dụng. Cần ý thức điều chỉnh."
        )
    elif ELEMENT_CONTROLS[hau_upper_el] == tien_upper_el:
        pattern = "Hậu khắc Tiên"
        rel = (
            f"Thượng quái Hậu ({hau_upper_el.title()}) khắc Tiên ({tien_upper_el.title()}) → "
            f"cách vận dụng đi ngược cốt mệnh, áp lực + đột phá."
        )
    else:
        pattern = "trung tính"
        rel = (
            f"Thượng quái Tiên ({tien_upper_el.title()}) ↔ Hậu ({hau_upper_el.title()}) "
            f"không tương tác trực tiếp ngũ hành."
        )
    return {
        "pattern": pattern,
        "tien_upper_el": tien_upper_el,
        "hau_upper_el": hau_upper_el,
        "narrative": rel,
    }


def _find_current_stage(trajectory: list[dict], current_age: int) -> dict | None:
    """Tìm stage hiện tại theo tuổi."""
    if current_age is None:
        return None
    for st in trajectory:
        if st["age_start"] <= current_age <= st["age_end"]:
            return st
    return None


def _luan_trajectory(ha_lac_state: dict, current_age: int | None, address: str = "bạn") -> dict:
    """Luận giải 12 hào trajectory."""
    traj = ha_lac_state["decade_trajectory"]
    nd_tien_line = ha_lac_state["tien_thien_quai"]["nguyen_duong_line"]
    nd_hau_line = ha_lac_state["hau_thien_quai"]["nguyen_duong_line"]
    current = _find_current_stage(traj, current_age)

    # Add phase_label to each stage
    stages_enriched = []
    for st in traj:
        is_tien = st["hexagram"] == "tien"
        phase_labels = TIEN_PHASE_LABELS if is_tien else HAU_PHASE_LABELS
        stages_enriched.append({
            **st,
            "phase_label": phase_labels.get(st["line_position"], ""),
            "is_current": (current is not None and st["stage_index"] == current["stage_index"]),
        })
    if current:
        cur_label_set = TIEN_PHASE_LABELS if current["hexagram"] == "tien" else HAU_PHASE_LABELS
        current_phase_label = cur_label_set.get(current["line_position"], "")
        current_narrative = (
            f"Tuổi {current_age} → {address} đang ở **giai đoạn {current['stage_index']}/12**: "
            f"{current['label']}. {current_phase_label}. "
            f"Khí của giai đoạn này = {('Dương dài 9 năm' if current['polarity'] == 'yang' else 'Âm ngắn 6 năm')}"
            + (". **Nguyên Đường** — giai đoạn chủ chốt!" if current["is_nguyen_duong"] else ".")
        )
    else:
        current_narrative = (
            f"Tuổi {current_age} chưa vào quỹ đạo 12 hào (dưới 1) "
            "hoặc đã qua hết (trên 84-90)."
            if current_age is not None else
            "Không biết current_age — chỉ hiển thị toàn quỹ đạo."
        )

    return {
        "stages": stages_enriched,
        "current": current,
        "current_narrative": current_narrative,
        "nguyen_duong_tien": nd_tien_line,
        "nguyen_duong_hau": nd_hau_line,
        "summary_narrative": (
            f"12 hào ~ {ha_lac_state['lifespan_span']['total_years']} năm. "
            f"Nguyên Đường Tiên thiên = hào {nd_tien_line} "
            f"({TIEN_PHASE_LABELS.get(nd_tien_line, '')}). "
            f"Nguyên Đường Hậu thiên = hào {nd_hau_line} "
            f"({HAU_PHASE_LABELS.get(nd_hau_line, '')})."
        ),
    }


def _bo_huong_for_stage(current_stage: dict | None, comparison: dict, address: str = "bạn") -> str:
    """Bổ hướng cho giai đoạn hiện tại."""
    if not current_stage:
        return (
            "Chưa xác định giai đoạn hiện tại. Nhìn vào quỹ đạo 12 hào, "
            f"xem hào nào sắp tới gần tuổi {address}."
        )
    is_tien = current_stage["hexagram"] == "tien"
    upper_el = comparison["tien_upper_el"] if is_tien else comparison["hau_upper_el"]
    if current_stage.get("is_nguyen_duong"):
        return (
            f"Đang ở **Nguyên Đường** ({'Tiên thiên' if is_tien else 'Hậu thiên'}) — "
            f"giai đoạn QUAN TRỌNG NHẤT của quẻ. Bổ Hướng: tập trung khí {upper_el.title()} "
            f"(thuộc thượng quái), làm việc có hành quan trọng nhất đời. "
            f"Đây là 6-9 năm 'cốt' của vận."
        )
    return (
        f"Đang ở giai đoạn {'Tiên thiên' if is_tien else 'Hậu thiên'} bình thường. "
        f"Bổ Hướng: theo khí thượng quái = {upper_el.title()}. "
        f"Chú ý chuyển giao khi sang hào tiếp theo."
    )


def compose_ha_lac_luan_giai(ha_lac_state: dict, current_age: int | None = None,
                             address: str = "bạn") -> dict:
    """Synthesize Bát Tự Hà Lạc analysis with paradigm-aligned narrative.

    Args:
        ha_lac_state: Output of `cast_ha_lac(...)`.
        current_age: Optional. Used to identify current stage in trajectory.
        address: Đại từ xưng hô user (mặc định trung tính 'bạn' — đúng cho mọi giới
            & tuổi trên surface đa-user như Chân Dung / API. Trang founder có thể
            truyền 'Anh'. Bug 2026-06-26: trước đây hardcode 'Anh' → gọi bé gái 16t
            là 'Anh' trên trang Chân Dung.)

    Returns:
        Structured dict for API + UI.
    """
    if "tien_thien_quai" not in ha_lac_state:
        raise ValueError("ha_lac_state must contain 'tien_thien_quai' key")

    tien_luan = _luan_quai(
        ha_lac_state["tien_thien_quai"], "Tiên Thiên Quái — cốt mệnh", TIEN_PHASE_LABELS
    )
    hau_luan = _luan_quai(
        ha_lac_state["hau_thien_quai"], "Hậu Thiên Quái — vận dụng", HAU_PHASE_LABELS
    )
    comparison = _compare_tien_hau(
        ha_lac_state["tien_thien_quai"], ha_lac_state["hau_thien_quai"]
    )
    trajectory_luan = _luan_trajectory(ha_lac_state, current_age, address)
    bo_huong = _bo_huong_for_stage(trajectory_luan.get("current"), comparison, address)

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Bát Tự Hà Lạc KHÔNG dự đoán anh sẽ X năm Y. "
            "Phản chiếu cấu trúc 2 quẻ Kinh Dịch (Tiên thiên + Hậu thiên) + "
            "12 hào trajectory ~84-90 năm. Mục đích: tri mệnh, biết mình ở đâu "
            "trong tổng thể → chọn cách đi qua."
        ),
        "overview": _compose_overview(ha_lac_state, address),
        "tien_thien_luan": tien_luan,
        "hau_thien_luan": hau_luan,
        "comparison": comparison,
        "trajectory_luan": trajectory_luan,
        "bo_huong_stage": bo_huong,
        "lifespan": ha_lac_state["lifespan_span"],
        "notes": ha_lac_state.get("notes", []),
        "closing": (
            "Hà Lạc = phái VN-specific (Học Năng 1974) kết hợp Hà Đồ + Lạc Thư + Tứ Trụ + Kinh Dịch. "
            "Tiên thiên = MỆNH (cố kết). Hậu thiên = VẬN (lưu biến). "
            "Cuộc đời = 12 hào, mỗi hào 6-9 năm. Tri mệnh thì không lo."
        ),
    }
