"""Mai Hoa environmental Thể-Dụng analysis from a chronos state."""

from __future__ import annotations

from typing import Any

from .constants import ELEMENT_CONTROLS, ELEMENT_GENERATES, TRIGRAM_BY_NUMBER


def _mai_hoa_environment(chronos_state) -> dict[str, Any]:
    local_dt = chronos_state.local_datetime
    if isinstance(local_dt, str):
        year = int(local_dt[0:4])
        month = int(local_dt[5:7])
        day = int(local_dt[8:10])
        hour = int(local_dt[11:13])
    else:
        year = local_dt.year
        month = local_dt.month
        day = local_dt.day
        hour = local_dt.hour

    year_num = ((year - 1984) % 12) + 1
    hour_num = ((hour + 1) // 2) % 12 + 1

    upper_num = (year_num + month + day) % 8 or 8
    lower_num = (year_num + month + day + hour_num) % 8 or 8
    moving_num = (year_num + month + day + hour_num) % 6 or 6

    upper_name, upper_element = TRIGRAM_BY_NUMBER[upper_num]
    lower_name, lower_element = TRIGRAM_BY_NUMBER[lower_num]
    if ELEMENT_GENERATES[upper_element] == lower_element:
        relation = "Thể sinh Dụng (hao lực cho sự việc)"
        relation_tag = "draining"
    elif ELEMENT_GENERATES[lower_element] == upper_element:
        relation = "Dụng sinh Thể (được trợ lực)"
        relation_tag = "supportive"
    elif ELEMENT_CONTROLS[upper_element] == lower_element:
        relation = "Thể khắc Dụng (chủ động kiểm soát)"
        relation_tag = "controlling"
    elif ELEMENT_CONTROLS[lower_element] == upper_element:
        relation = "Dụng khắc Thể (áp lực ngoại cảnh)"
        relation_tag = "pressure"
    else:
        relation = "Đồng hành (thế cân bằng)"
        relation_tag = "neutral"

    return {
        "year_num": year_num,
        "month_num": month,
        "day_num": day,
        "hour_num": hour_num,
        "upper_trigram_num": upper_num,
        "lower_trigram_num": lower_num,
        "moving_line_num": moving_num,
        "upper_trigram": upper_name,
        "lower_trigram": lower_name,
        "upper_element": upper_element,
        "lower_element": lower_element,
        "relation": relation,
        "relation_tag": relation_tag,
    }
