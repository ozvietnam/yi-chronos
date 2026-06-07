"""Chiêm Cung Phu Thê — Bắc phái Trung Châu (Vương Đình Chỉ)

Input: la_so dict từ engine.tu_vi.analyzer.TuViAnalyzer
Output: luận giải cung Phu Thê có cấu trúc + raw paradigm

Paradigm: data/seeds/tuvi_cung_phu_the_trung_chau.json
Source: data/restored_books/trung-chau-tu-vi-dau-so-2/content.md section 5.3
School: Bắc phái Trung Châu — Vương Đình Chỉ

Iron Rule #6 (Tử Vi đồng dạng, không predict):
- KHÔNG trả lời "anh/chị sẽ ly hôn" — paradigm chỉ phản chiếu khuynh hướng
- Vẫn cần xem KÈM Thái Dương/Thái Âm miếu hãm + cung Mệnh + Phúc Đức + đại vận
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent
# Volume mount /opt/yi-chronos/data shadows data/ in Docker — check embedded first
_SEED_CANDIDATES = [
    _ROOT / "embedded_data" / "seeds" / "tuvi_cung_phu_the_trung_chau.json",
    _ROOT / "data" / "seeds" / "tuvi_cung_phu_the_trung_chau.json",
]
_SEED_PATH = next((p for p in _SEED_CANDIDATES if p.exists()), _SEED_CANDIDATES[-1])

# Map chính tinh tiếng Việt → key trong seed
_STAR_KEY_MAP = {
    "Tử Vi": "tu_vi",
    "Thiên Cơ": "thien_co",
    "Thái Dương": "thai_duong",
    "Vũ Khúc": "vu_khuc",
    "Thiên Đồng": "thien_dong",
    "Liêm Trinh": "liem_trinh",
    "Thiên Phủ": "thien_phu",
    "Thái Âm": "thai_am",
    "Tham Lang": "tham_lang",
    "Cự Môn": "cu_mon",
    "Thiên Tướng": "thien_tuong",
    "Thiên Lương": "thien_luong",
    "Thất Sát": "that_sat",
    "Phá Quân": "pha_quan",
}

# Map cặp Địa Chi → key vị trí trong seed (đối xứng qua tâm)
_PAIR_KEY_BY_BRANCH = {
    "Tý": "ty_ngo", "Ngọ": "ty_ngo",
    "Sửu": "suu_mui", "Mùi": "suu_mui",
    "Dần": "dan_than", "Thân": "dan_than",
    "Mão": "mao_dau", "Dậu": "mao_dau",
    "Thìn": "thin_tuat", "Tuất": "thin_tuat",
    "Tỵ": "ty_hoi", "Hợi": "ty_hoi",
}

# Map tổ hợp đôi (sorted set của 2 sao) → key trong to_hop_doi_thuong_gap
_PAIR_COMBO_MAP = {
    frozenset(["Tử Vi", "Phá Quân"]): "tu_vi_pha_quan",
    frozenset(["Tử Vi", "Thiên Phủ"]): "tu_vi_thien_phu",
    frozenset(["Tử Vi", "Tham Lang"]): "tu_vi_tham_lang",
    frozenset(["Tử Vi", "Thiên Tướng"]): "tu_vi_thien_tuong",
    frozenset(["Tử Vi", "Thất Sát"]): "tu_vi_that_sat",
    frozenset(["Vũ Khúc", "Thiên Phủ"]): "vu_khuc_thien_phu",
    frozenset(["Vũ Khúc", "Tham Lang"]): "vu_khuc_tham_lang",
    frozenset(["Vũ Khúc", "Thiên Tướng"]): "vu_khuc_thien_tuong",
    frozenset(["Vũ Khúc", "Thất Sát"]): "vu_khuc_that_sat",
    frozenset(["Vũ Khúc", "Phá Quân"]): "vu_khuc_pha_quan",
    frozenset(["Liêm Trinh", "Thiên Tướng"]): "lien_trinh_thien_tuong",
    frozenset(["Liêm Trinh", "Thất Sát"]): "lien_trinh_that_sat",
    frozenset(["Liêm Trinh", "Phá Quân"]): "lien_trinh_pha_quan",
    frozenset(["Liêm Trinh", "Thiên Phủ"]): "lien_trinh_thien_phu",
    frozenset(["Liêm Trinh", "Tham Lang"]): "lien_trinh_tham_lang",
    frozenset(["Thái Dương", "Thái Âm"]): "thai_duong_thai_am",
    frozenset(["Thái Dương", "Cự Môn"]): "thai_duong_cu_mon",
    frozenset(["Thái Dương", "Thiên Lương"]): "thai_duong_thien_luong",
    frozenset(["Thiên Cơ", "Thái Âm"]): "thien_co_thai_am",
    frozenset(["Thiên Cơ", "Cự Môn"]): "thien_co_cu_mon",
    frozenset(["Thiên Cơ", "Thiên Lương"]): "thien_co_thien_luong",
    frozenset(["Thiên Đồng", "Thái Âm"]): "thien_dong_thai_am",
    frozenset(["Thiên Đồng", "Cự Môn"]): "thien_dong_cu_mon",
    frozenset(["Thiên Đồng", "Thiên Lương"]): "thien_dong_thien_luong",
}

_seed_cache: dict[str, Any] | None = None


def _load_seed() -> dict[str, Any]:
    global _seed_cache
    if _seed_cache is None:
        with _SEED_PATH.open("r", encoding="utf-8") as f:
            _seed_cache = json.load(f)
    return _seed_cache


def _find_palace(la_so: dict, palace_name: str = "Phu Thê") -> dict | None:
    """Tìm palace dict theo tên."""
    for pal in la_so.get("palaces", []):
        if pal.get("name") == palace_name:
            return pal
    return None


def _stars_at_branch_idx(la_so: dict, branch_idx: int) -> dict[str, list[str]]:
    """Lấy chính tinh / phụ tinh / sát tinh / sao_q2 tại branch index.

    sao_q2 (Trung Châu Q2): Hồng Loan, Thiên Hỉ, Hàm Trì, Đại Hao, Thiên Diêu,
    Cô Thần, Quả Tú, Tam Thai, Bát Tọa, Thiên Khốc, Thiên Hư, Long Trì, Phượng Các
    — phục vụ detect 'Đào hoa phạm chủ' + các paradigm bổ sung.
    """
    result: dict[str, list[str]] = {
        "chinh_tinh": [], "phu_tinh": [], "sat_tinh": [], "sao_q2": [],
    }

    ct = la_so.get("chinh_tinh", {})
    for star, idx in ct.items():
        if idx == branch_idx:
            result["chinh_tinh"].append(star)

    pt = la_so.get("phu_tinh", {})
    if isinstance(pt, dict):
        for star, idx in pt.items():
            if idx == branch_idx:
                result["phu_tinh"].append(star)

    st = la_so.get("sat_tinh", {})
    if isinstance(st, dict):
        for star, idx in st.items():
            if idx == branch_idx:
                result["sat_tinh"].append(star)

    # Q2 stars (đào hoa, cô đơn, khốc hư, long phượng...)
    q2 = la_so.get("sao_q2", {})
    if isinstance(q2, dict):
        for star, idx in q2.items():
            if idx == branch_idx:
                result["sao_q2"].append(star)

    return result


def _detect_luc_sat(stars_at: dict[str, list[str]]) -> list[str]:
    """Detect 6 sát tinh trong cung."""
    LUC_SAT = {"Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"}
    all_stars = set(stars_at["phu_tinh"] + stars_at["sat_tinh"])
    return sorted(all_stars & LUC_SAT)


def _detect_hoa_ki(la_so: dict, branch_idx: int) -> list[str]:
    """Detect chính tinh nào ở branch idx đang Hóa Kỵ."""
    tu_hoa = la_so.get("tu_hoa", {})
    if not isinstance(tu_hoa, dict):
        return []
    chinh_tinh_at = [s for s, i in la_so.get("chinh_tinh", {}).items() if i == branch_idx]
    hoa_ki_star = tu_hoa.get("Hóa Kỵ") or tu_hoa.get("hoa_ki") or tu_hoa.get("ki")
    if hoa_ki_star and hoa_ki_star in chinh_tinh_at:
        return [hoa_ki_star]
    return []


def chiem_phu_the(la_so: dict, paradigm_school: str = "bac_phai_trung_chau") -> dict[str, Any]:
    """Luận cung Phu Thê theo Bắc phái Trung Châu.

    Args:
        la_so: dict từ TuViAnalyzer.la_so
        paradigm_school: hiện chỉ hỗ trợ "bac_phai_trung_chau"

    Returns:
        dict với cấu trúc:
        {
            "cung_phu_the": {"branch": "Mão", "branch_index": 3},
            "chinh_tinh": ["Tử Vi", "Tham Lang"],
            "phu_tinh": [...],
            "sat_tinh": [...],
            "luc_sat_trong_cung": [...],
            "hoa_ki_trong_cung": [...],
            "to_hop_doi": "tu_vi_tham_lang" (or None),
            "luan_giai": {
                "tong_quan": "...",
                "ban_chat_sao": [...],  # per chính tinh
                "vi_tri_paradigm": {...},  # paradigm cho cặp vị trí
                "to_hop_summary": "..." (if applicable)
            },
            "iron_rule_disclaimer": "Đọc đồng dạng, không predict...",
            "thay_to_su": [...],
            "source": "..."
        }
    """
    seed = _load_seed()

    # 1. Locate cung Phu Thê
    pal = _find_palace(la_so, "Phu Thê")
    if not pal:
        return {"error": "Không tìm thấy cung Phu Thê trong lá số"}

    branch = pal["branch"]
    branch_idx = pal["branch_index"]

    # 2. Identify stars
    stars_at = _stars_at_branch_idx(la_so, branch_idx)
    luc_sat = _detect_luc_sat(stars_at)
    hoa_ki = _detect_hoa_ki(la_so, branch_idx)

    # 3. Detect tổ hợp đôi
    chinh_set = set(stars_at["chinh_tinh"])
    to_hop_key = None
    if len(chinh_set) == 2:
        to_hop_key = _PAIR_COMBO_MAP.get(frozenset(chinh_set))

    # 4. Build luận giải
    luan_giai: dict[str, Any] = {
        "ban_chat_sao": [],
        "vi_tri_paradigm": {},
        "to_hop_summary": None,
        "tong_quan_paradigm": seed.get("paradigm_chung", {}).get("nguyen_tac_cot", []),
    }

    chinh_tinh_data = seed.get("14_chinh_tinh_phu_the", {})
    pair_key = _PAIR_KEY_BY_BRANCH.get(branch)

    for star in stars_at["chinh_tinh"]:
        key = _STAR_KEY_MAP.get(star)
        if not key or key not in chinh_tinh_data:
            continue
        star_data = chinh_tinh_data[key]

        sao_entry = {
            "ten": star,
            "ban_chat": star_data.get("ban_chat", ""),
            "co_ban": star_data.get("co_ban", ""),
        }
        luan_giai["ban_chat_sao"].append(sao_entry)

        # Vị trí cụ thể
        vi_tri = star_data.get("vi_tri", {})
        if pair_key and pair_key in vi_tri:
            luan_giai["vi_tri_paradigm"][star] = {
                "branch_pair": branch,
                "data": vi_tri[pair_key],
            }

    # 5. Tổ hợp đôi (if any)
    if to_hop_key:
        to_hop_data = seed.get("to_hop_doi_thuong_gap", {})
        luan_giai["to_hop_summary"] = {
            "key": to_hop_key,
            "noi_dung": to_hop_data.get(to_hop_key, ""),
        }

    # 6. Cảnh báo & gợi ý
    canh_bao = []
    if hoa_ki:
        for star in hoa_ki:
            if star in {"Vũ Khúc", "Thái Dương", "Liêm Trinh"}:
                canh_bao.append(
                    f"⚠ {star} Hóa Kỵ tại Phu Thê — paradigm Trung Châu CỰC KỲ BẤT LỢI. "
                    f"Cần xem kèm đại vận hiện tại + Thái Dương/Thái Âm miếu hãm."
                )
            else:
                canh_bao.append(f"⚠ {star} Hóa Kỵ tại Phu Thê — cần chú ý.")
    if luc_sat:
        canh_bao.append(
            f"⚠ Lục sát có {len(luc_sat)} sao ({', '.join(luc_sat)}) tại Phu Thê — "
            f"paradigm: hình khắc / áp lực hôn nhân."
        )

    quy_tac_doan = seed.get("quy_tac_doan_chung", [])

    return {
        "cung_phu_the": {
            "branch": branch,
            "branch_index": branch_idx,
        },
        "chinh_tinh": stars_at["chinh_tinh"],
        "phu_tinh": stars_at["phu_tinh"],
        "sat_tinh": stars_at["sat_tinh"],
        "luc_sat_trong_cung": luc_sat,
        "hoa_ki_trong_cung": hoa_ki,
        "to_hop_doi": to_hop_key,
        "luan_giai": luan_giai,
        "canh_bao": canh_bao,
        "quy_tac_doan_chung": quy_tac_doan,
        "iron_rule_disclaimer": (
            "Paradigm Bắc phái Trung Châu = đọc ĐỒNG DẠNG, KHÔNG predict tuyệt đối. "
            "Cung Phu Thê chỉ phản chiếu KHUYNH HƯỚNG hôn nhân, không phải số phận cố định. "
            "Cần xem kèm: Mệnh, Phúc Đức, đại vận hiện tại, Thái Dương/Thái Âm miếu hãm."
        ),
        "thay_to_su": seed.get("_meta", {}).get("thay_to_su", []),
        "school": paradigm_school,
        "source": seed.get("_meta", {}).get("source", ""),
    }


def chiem_phu_the_summary_text(la_so: dict) -> str:
    """Render markdown summary cho UI / API."""
    result = chiem_phu_the(la_so)
    if "error" in result:
        return f"❌ {result['error']}"

    lines = []
    cpt = result["cung_phu_the"]
    lines.append(f"# Cung Phu Thê — {cpt['branch']}")
    lines.append("")
    lines.append(f"**Trường phái**: Bắc phái Trung Châu (Vương Đình Chỉ, Trương Khai Quyển, Lục Bân Triệu)")
    lines.append("")

    if result["chinh_tinh"]:
        lines.append(f"**Chính tinh**: {', '.join(result['chinh_tinh'])}")
    else:
        lines.append("**Chính tinh**: (vô chính diệu — mượn sao đối cung)")
    if result["phu_tinh"]:
        lines.append(f"**Phụ tinh**: {', '.join(result['phu_tinh'])}")
    if result["sat_tinh"]:
        lines.append(f"**Sát tinh**: {', '.join(result['sat_tinh'])}")
    lines.append("")

    # Tổ hợp đôi
    if result["to_hop_doi"]:
        th = result["luan_giai"]["to_hop_summary"]
        lines.append(f"## Tổ hợp: **{th['key'].replace('_', ' ').title()}**")
        lines.append(f"_{th['noi_dung']}_")
        lines.append("")

    # Per-star paradigm
    for sao in result["luan_giai"]["ban_chat_sao"]:
        lines.append(f"## ⭐ {sao['ten']}")
        if sao.get("ban_chat"):
            lines.append(f"**Bản chất**: {sao['ban_chat']}")
        if sao.get("co_ban"):
            lines.append(f"**Cơ bản**: {sao['co_ban']}")
        lines.append("")

        vi_tri = result["luan_giai"]["vi_tri_paradigm"].get(sao["ten"])
        if vi_tri:
            data = vi_tri["data"]
            lines.append(f"### Tại cung {vi_tri['branch_pair']}:")
            for k, v in data.items():
                if isinstance(v, str):
                    lines.append(f"- **{k.replace('_', ' ')}**: {v}")
                elif isinstance(v, list):
                    lines.append(f"- **{k.replace('_', ' ')}**: {', '.join(map(str, v))}")
            lines.append("")

    # Cảnh báo
    if result["canh_bao"]:
        lines.append("## ⚠ Cảnh báo paradigm")
        for cb in result["canh_bao"]:
            lines.append(f"- {cb}")
        lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append(f"_{result['iron_rule_disclaimer']}_")

    return "\n".join(lines)
