"""Kiểm chứng bằng máy các ĐỊNH LÝ DẪN XUẤT của Đằng Sơn — kế thừa, tiếp tục công trình.

Đằng Sơn (《Tử Vi Hoàn Toàn Khoa Học》 Q1, kế thừa Tạ Phồn Trị) dựng tử vi như một
chuỗi định lý BẰNG TAY. Module này lấy engine kiểm các định lý ấy trên dữ liệu
canonical (data/tu_vi/chinh_tinh.json + mieu_vuong_ham.json). Tinh thần khoa học:
luật phải TÁI TẠO được dữ liệu — chỗ nào khép kín, chỗ nào hở, báo cáo trung thực.

Định lý kiểm:
- Tam hợp = vòng ngũ-hành-SINH (tr.200)
- Độ sáng = giai đoạn Trường Sinh của hành sao tại cung (tr.243)
- Bảo toàn âm-dương tổng = 0 (tr.172) — báo cáo giới hạn dữ liệu, không ép
"""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

_DATA = Path(__file__).resolve().parents[2] / "data" / "tu_vi"

# Vòng tương SINH ngũ hành
NGU_HANH_SINH = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}

# id sao → tên hiển thị (bảng độ sáng dùng tên hiển thị)
_STAR_DISPLAY = {
    "tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương",
    "vu_khuc": "Vũ Khúc", "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh",
    "thien_phu": "Thiên Phủ", "thai_am": "Thái Âm", "tham_lang": "Tham Lang",
    "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng", "thien_luong": "Thiên Lương",
    "that_sat": "Thất Sát", "pha_quan": "Phá Quân",
}

# 12 chi theo thứ tự địa bàn
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# 12 giai đoạn Trường Sinh (thuận)
TRUONG_SINH_STAGES = [
    "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy",
    "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng",
]
# Cung khởi Trường Sinh theo hành — Đằng Sơn gom Hỏa-Thổ cùng vòng (tr.243)
_TS_START = {"hỏa": "Dần", "thổ": "Dần", "kim": "Tỵ", "thủy": "Thân", "mộc": "Hợi"}
# Sức từng giai đoạn (Đế Vượng đỉnh → Tuyệt đáy) — đường đời sinh-vượng-tử-tuyệt
_STAGE_STRENGTH = {
    "Trường Sinh": 3, "Mộc Dục": 0, "Quan Đới": 2, "Lâm Quan": 4, "Đế Vượng": 5,
    "Suy": -1, "Bệnh": -2, "Tử": -3, "Mộ": -2, "Tuyệt": -4, "Thai": -1, "Dưỡng": 1,
}


def _primary_hanh(s: str) -> str:
    """Sao đa hành ('mộc / thủy') → hành chủ (đầu)."""
    return s.split("/")[0].strip()


def _load_stars():
    d = json.loads((_DATA / "chinh_tinh.json").read_text(encoding="utf-8"))
    out = {}
    for s in d["stars"]:
        sid = s.get("id") or s.get("ten") or s.get("name")
        out[sid] = {
            "hanh": _primary_hanh(s.get("ngu_hanh", "")),
            "am_duong": s.get("am_duong"),
            "display": _STAR_DISPLAY.get(sid, sid),
        }
    return out


STARS = _load_stars()


def is_sinh_chain(hanh_list) -> bool:
    """Danh sách hành có theo thứ tự tương sinh liên tiếp không?"""
    return all(NGU_HANH_SINH.get(hanh_list[i]) == hanh_list[i + 1]
               for i in range(len(hanh_list) - 1))


def _find_sinh_order(star_ids):
    for perm in permutations(star_ids):
        hanh = [STARS[s]["hanh"] for s in perm]
        if is_sinh_chain(hanh):
            return list(perm), hanh
    return None, None


# Hai bộ tam hợp Đằng Sơn nêu đích danh (tr.200)
_TAM_HOP = {
    "Tử-Vũ-Liêm": ["tu_vi", "vu_khuc", "liem_trinh"],
    "Sát-Phá-Tham": ["that_sat", "pha_quan", "tham_lang"],
}


def verify_tam_hop():
    out = {}
    for name, ids in _TAM_HOP.items():
        order, hanh = _find_sinh_order(ids)
        out[name] = {
            "stars": ids,
            "hanh": [STARS[s]["hanh"] for s in ids],
            "is_sinh_chain": order is not None,
            "sinh_order": order,
            "sinh_order_hanh": hanh,
        }
    return out


def truong_sinh_stage(hanh: str, cung: str) -> str:
    off = (CHI.index(cung) - CHI.index(_TS_START[hanh])) % 12
    return TRUONG_SINH_STAGES[off]


def _corr(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs) ** 0.5
    vy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


def verify_brightness():
    """Độ sáng canonical có tương quan với sức Trường Sinh của hành sao tại cung không?"""
    m = json.loads((_DATA / "mieu_vuong_ham.json").read_text(encoding="utf-8"))
    scores = {k: v["score"] for k, v in m["levels"].items()}
    table = m["table"]
    xs, ys, mism = [], [], []
    for info in STARS.values():
        disp = info["display"]
        if disp not in table:
            continue
        for cung, level in table[disp].items():
            if level not in scores:
                continue
            stage = truong_sinh_stage(info["hanh"], cung)
            xs.append(_STAGE_STRENGTH[stage])
            ys.append(scores[level])
    return {"n_pairs": len(xs), "correlation": round(_corr(xs, ys), 4)}


def verify_conservation():
    """Bảo toàn tổng âm-dương=0 (tr.172) — báo cáo trung thực với dữ liệu sẵn có."""
    duong = [s for s, i in STARS.items() if i["am_duong"] == "dương"]
    am = [s for s, i in STARS.items() if i["am_duong"] == "âm"]
    return {
        "n_duong": len(duong), "n_am": len(am),
        "balanced_raw": len(duong) == len(am),
        "note": ("Âm-dương TRUYỀN THỐNG %d dương / %d âm — chưa cân. Đằng Sơn (tr.120) "
                 "dùng âm-dương theo CỘNG HƯỞNG (trái nghịch=âm, tương đồng=dương), khác "
                 "bảng truyền thống → phải trích bộ giá trị ấy mới kiểm định luật =0."
                 % (len(duong), len(am))),
    }


def full_report():
    return {
        "tam_hop": verify_tam_hop(),
        "brightness": verify_brightness(),
        "conservation": verify_conservation(),
    }
