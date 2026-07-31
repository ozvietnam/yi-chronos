"""TuViAnalyzer — generic analysis engine cho bất kỳ lá số nào.

Encapsulates các phép phân tích đã build cho founder:
    1. discover_cach_cuc() — 6-8 cách cục kinh điển (DeepSeek)
    2. synastry(other) — đối chiếu 2 chart
    3. luu_nien(year) — vận năm
    4. luu_nguyet(year) — 12 tháng âm vận tháng
    5. phu_match() — match Phú Thái Vi với chart
    6. phu_reading(top_n) — DeepSeek personalize top N passages
    7. dai_van_annotate() — 12 đại vận với annotation
    8. cach_cuc_deep(cach_id) — đào sâu 1 cách cụ thể

Mỗi method cache vào `data/yi_publishing/analysis_cache/{person_key}/<kind>.json`.
DeepSeek calls đều silent fail nếu lỗi (returns empty analysis).
"""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ─── Paradigm post-check (Iron Rule #6) ──────────────────────────────────────
# Defense-in-depth: the prompts forbid fortune-telling, but an LLM may slip. This
# scans the parsed vận-hạn output for predict-tone phrases and FLAGS them (does not
# silently delete) so a violation surfaces instead of shipping to the user unseen.
_FORTUNE_RE = re.compile(
    r"sẽ\s+(?:giàu|nghèo|thành công|thất bại|phá sản|chết|ly hôn|phát tài|khá lên|đi xuống)"
    r"|chắc chắn\s+(?:giàu|nghèo|thành công|thất bại|đỗ|trượt)"
    r"|năm\s+\d{4}\s+(?:rất\s+)?(?:tốt|xấu|đại cát|đại hung|cát|hung)"
    r"|(?:đại cát|đại hung)\b",
    re.IGNORECASE,
)


def _paradigm_postcheck(result):
    """Flag fortune-telling tone in an LLM result dict (Iron Rule #6)."""
    if not isinstance(result, dict):
        return result
    hits: list[str] = []

    def _scan(v):
        if isinstance(v, str):
            hits.extend(m.group(0) for m in _FORTUNE_RE.finditer(v))
        elif isinstance(v, list):
            for x in v:
                _scan(x)
        elif isinstance(v, dict):
            for x in v.values():
                _scan(x)

    _scan(result)
    if hits:
        uniq = sorted(set(h.strip() for h in hits))[:5]
        result["_paradigm_warning"] = (
            "⚠️ Phát hiện giọng dự đoán (Iron Rule #6 — Tử Vi đọc đồng dạng, KHÔNG predict): "
            + "; ".join(uniq)
        )
        logger.warning("Tu Vi paradigm post-check flagged predict tone: %s", uniq)
    return result

logger = logging.getLogger(__name__)

BRANCHES = ("Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi")

CACHE_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/analysis_cache")
PHU_LAYER3_PATH = Path(
    "/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/translations/tuvidauso-zh/_phu_thai_vi_layer3.json"
)


# ─── DTOs ────────────────────────────────────────────────────────────────────

@dataclass
class Person:
    person_key: str
    name: str
    birth_datetime_local: str       # "1988-06-05T23:30:00"
    gender: str                     # "nam" | "nữ"
    timezone: str = "Asia/Ho_Chi_Minh"
    notes: str = ""
    user_id: Optional[int] = None   # owning user — None means legacy/founder fallback


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _scoped_key(person_key: str, user_id: Optional[int] = None) -> str:
    """Return the on-disk cache namespace.

    Backward compat: founder personas (and legacy callers without user_id) keep
    the original `_founder` / `wife` paths so existing data still loads.
    New per-user personas live under `u{user_id}/{person_key}` to prevent
    different users from clobbering each other's `self` cache.
    """
    if user_id is None:
        return person_key
    # Founder (user_id=1) keeps legacy unprefixed paths for backward compat
    if user_id == 1 and person_key in ("_founder",):
        return person_key
    return f"u{user_id}/{person_key}"


def _cache_dir(person_key: str, user_id: Optional[int] = None) -> Path:
    d = CACHE_ROOT / _scoped_key(person_key, user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_load(person_key: str, kind: str, user_id: Optional[int] = None) -> Optional[dict]:
    """Load cached result. Falls back to legacy unscoped path if scoped missing."""
    f = _cache_dir(person_key, user_id) / f"{kind}.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            return None
    # Fallback: legacy unscoped path (only when user_id was provided)
    if user_id is not None:
        legacy = CACHE_ROOT / person_key / f"{kind}.json"
        if legacy.exists():
            try:
                return json.loads(legacy.read_text())
            except Exception:
                return None
    return None


def _cache_save(person_key: str, kind: str, data: dict, user_id: Optional[int] = None) -> Path:
    f = _cache_dir(person_key, user_id) / f"{kind}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return f


def _cast_chart(birth: str, gender: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Cast Tử Vi lá số.

    Uses lich_conversion.solar_to_lunar for lunar day/month (handles 早子時 rollover:
    hour ≥ 23 → lunar date of the NEXT day, matching project convention).
    Uses core.chronos for year can-chi (UTC-boundary corrected in #12).
    """
    from .an_sao import cast_la_so
    from core.chronos import calculate_chronos_state
    from datetime import datetime as _dt
    from engine.yi_wiki.lich_conversion import SolarDateTime, solar_to_lunar

    chronos = calculate_chronos_state(birth, timezone)
    local_dt = _dt.fromisoformat(birth)
    # lich_conversion already applies 早子時: hour≥23 → rolls to next lunar day
    solar = SolarDateTime(
        year=local_dt.year, month=local_dt.month, day=local_dt.day,
        hour=local_dt.hour, minute=local_dt.minute,
    )
    lunar = solar_to_lunar(solar)
    lunar_month = lunar.lunar_month
    lunar_day = lunar.lunar_day
    hour = local_dt.hour
    # Map hour → branch (Tý=23-1, Sửu=1-3, …, Hợi=21-23)
    if hour == 23:
        hour_idx = 0
    else:
        hour_idx = ((hour + 1) // 2) % 12
    hour_branch = BRANCHES[hour_idx]
    year_parts = chronos.ganzhi.year.split()
    year_stem, year_branch = year_parts[0], year_parts[1]

    return cast_la_so(
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch=hour_branch,
        year_stem=year_stem,
        year_branch=year_branch,
        gender=gender,
    )


def _chart_full_dump(person: Person, ls: dict) -> str:
    """Build FULL la-số dump cho VIP deep interpretation.

    Group sao vào từng cung — LLM thấy chính xác sao nào ở cung nào, tránh bịa.
    """
    BRANCHES_LOCAL = BRANCHES
    all_stars = {
        **{k: ("chính", v) for k, v in ls.get('chinh_tinh', {}).items()},
        **{k: ("phụ", v) for k, v in ls.get('phu_tinh', {}).items()},
        **{k: ("sát", v) for k, v in ls.get('sat_tinh', {}).items()},
    }
    sao_q2 = ls.get('sao_q2', {}) or {}
    for k, v in sao_q2.items():
        if k not in all_stars and isinstance(v, int) and 0 <= v < 12:
            all_stars[k] = ("Q2", v)
    # Invert: branch_idx → [star names]
    branch_to_stars = {i: [] for i in range(12)}
    for star, (kind, idx) in all_stars.items():
        if isinstance(idx, int) and 0 <= idx < 12:
            branch_to_stars[idx].append(f"{star}[{kind}]")
    hoa = ls.get('tu_hoa', {}) or {}
    star_to_hoa = {v: k for k, v in hoa.items()}  # star → Lộc/Quyền/Khoa/Kỵ

    lines = [
        f"╔══════════════════════════════════════════════════════════════╗",
        f"║ LÁ SỐ TỬ VI ĐẨU SỐ — DUMP ĐẦY ĐỦ                            ║",
        f"╠══════════════════════════════════════════════════════════════╣",
        f"║ Chủ nhân: {person.name} ({person.gender})",
        f"║ Sinh: {person.birth_datetime_local} ({person.timezone})",
        f"║ Năm sinh can chi: {ls.get('year_stem', '')}{ls.get('year_branch', '')}",
        f"║ Tháng âm: {ls.get('lunar_month', '?')} | Ngày âm: {ls.get('lunar_day', '?')} | Giờ: {ls.get('hour_branch', '?')}",
        f"╠══════════════════════════════════════════════════════════════╣",
        f"║ Mệnh tọa: {ls['menh_branch']}  |  Thân tọa: {ls['than_branch']}"
        + (" (Mệnh-Thân ĐỒNG CUNG)" if ls['menh_branch'] == ls['than_branch'] else ""),
        f"║ Cục: {ls.get('cuc_name', '?')} ({ls.get('cuc', '?')})",
        f"║ Mệnh chủ: {ls.get('menh_chu', '?')}   |  Thân chủ: {ls.get('than_chu', '?')}",
        f"║ Đẩu Quân: {ls.get('dau_quan_branch', '?')} (an niên-đẩu, chủ duyên)",
        f"║ Tứ Hóa năm sinh: Lộc→{hoa.get('Lộc','?')} · Quyền→{hoa.get('Quyền','?')} · Khoa→{hoa.get('Khoa','?')} · Kỵ→{hoa.get('Kỵ','?')}",
        f"╚══════════════════════════════════════════════════════════════╝",
        "",
        "━━━ 12 CUNG (đầy đủ sao mỗi cung) ━━━",
    ]
    # 12 cung in palace-order
    for p in ls.get('palaces', []):
        idx = p['branch_index']
        branch = BRANCHES_LOCAL[idx]
        stars = branch_to_stars.get(idx, [])
        # Append hóa marker
        starred = []
        for s in stars:
            base = s.split('[')[0]
            mark = f" ⟨{star_to_hoa[base]}⟩" if base in star_to_hoa else ""
            starred.append(s + mark)
        lines.append(f"  ┌─ Cung {p['name']} ({branch}) ─")
        if starred:
            lines.append(f"  │  Sao: {', '.join(starred)}")
        else:
            lines.append(f"  │  Sao: (vô chính tinh — mượn tam hợp)")
        lines.append(f"  └─")
    lines.append("")
    # Tam phương tứ chính của Mệnh
    menh_idx = ls.get('menh_index', 0)
    if isinstance(menh_idx, int):
        tam_hop_idx = [(menh_idx + 4) % 12, (menh_idx + 8) % 12]
        xung_idx = (menh_idx + 6) % 12
        lines.append("━━━ TAM PHƯƠNG TỨ CHÍNH của Mệnh ━━━")
        lines.append(f"  Cung Mệnh: {BRANCHES_LOCAL[menh_idx]} → sao {', '.join(branch_to_stars[menh_idx]) or '(vô)'}")
        lines.append(f"  Tam hợp 1: {BRANCHES_LOCAL[tam_hop_idx[0]]} → {', '.join(branch_to_stars[tam_hop_idx[0]]) or '(vô)'}")
        lines.append(f"  Tam hợp 2: {BRANCHES_LOCAL[tam_hop_idx[1]]} → {', '.join(branch_to_stars[tam_hop_idx[1]]) or '(vô)'}")
        lines.append(f"  Xung chiếu (Thiên Di): {BRANCHES_LOCAL[xung_idx]} → {', '.join(branch_to_stars[xung_idx]) or '(vô)'}")
        lines.append("")
    # Đại Vận chi tiết
    dai_van = ls.get('dai_van', []) or []
    if dai_van:
        lines.append("━━━ ĐẠI VẬN (8 vòng) ━━━")
        for dv in dai_van[:10]:
            if isinstance(dv, dict):
                age_range = f"{dv.get('age_start', '?')}-{dv.get('age_end', '?')}"
                year_range = f"{dv.get('year_start', '?')}-{dv.get('year_end', '?')}"
                cung = dv.get('cung', dv.get('palace', '?'))
                branch = dv.get('branch', '?')
                lines.append(f"  Vận {age_range} tuổi ({year_range}) → cung {cung} ({branch})")
        lines.append("")
    return "\n".join(lines)


def _chart_summary(person: Person, ls: dict) -> str:
    """Build human-readable chart summary for DeepSeek prompts."""
    s2b = {**ls['chinh_tinh'], **ls['phu_tinh'], **ls.get('sat_tinh', {})}
    stars_at_menh = [st for st, idx in s2b.items() if BRANCHES[idx] == ls['menh_branch']]
    same = " (đồng cung)" if ls['menh_branch'] == ls['than_branch'] else ""

    lines = [
        f"LÁ SỐ {person.name} ({person.gender}, sinh {person.birth_datetime_local}):",
        f"- Mệnh {ls['menh_branch']} | Thân {ls['than_branch']}{same}",
        f"- Cục: {ls['cuc_name']}",
        f"- Mệnh chủ: {ls['menh_chu']} | Thân chủ: {ls['than_chu']} | Đẩu Quân: {ls['dau_quan_branch']}",
        f"- Cung Mệnh tọa: {', '.join(stars_at_menh) or '(vô chính tinh)'}",
        "- 14 chính tinh:",
    ]
    for star, idx in ls['chinh_tinh'].items():
        lines.append(f"    {star}: {BRANCHES[idx]}")
    hoa = ls.get('tu_hoa', {})
    if hoa:
        lines.append(
            "- Tứ Hóa: "
            + ", ".join(f"{k}→{v}({BRANCHES[s2b.get(v, 0)]})" for k, v in hoa.items())
        )
    lines.append("- 12 cung:")
    for p in ls['palaces']:
        lines.append(f"    {p['name']}: {BRANCHES[p['branch_index']]}")
    return "\n".join(lines)


# ─── Main analyzer class ─────────────────────────────────────────────────────

class TuViAnalyzer:
    """Generic Tử Vi analyzer with caching."""

    def __init__(self, person: Person, force: bool = False):
        self.person = person
        self.force = force  # bypass cache
        self._la_so: Optional[dict] = None

    @property
    def la_so(self) -> dict:
        if self._la_so is None:
            self._la_so = _cast_chart(self.person.birth_datetime_local, self.person.gender)
        return self._la_so

    @property
    def chart_summary(self) -> str:
        return _chart_summary(self.person, self.la_so)

    # ── 1. Discover cách cục ────────────────────────────────────────────────

    SYSTEM_DISCOVER = """Bạn là chuyên gia Tử Vi Đẩu Số 30 năm kinh nghiệm. Phân tích lá số CỤ THỂ tìm các cách cục KINH ĐIỂN (theo Tử Vi Đẩu Số Toàn Thư - Trần Đoàn).

Cho lá số đầy đủ, hãy LIỆT KÊ 6-8 cách cục QUAN TRỌNG NHẤT mà lá số này hiện ra (cát + hung). Mỗi cách:
- ten: tên Hán-Việt
- cap_do: "thượng" / "trung" / "hạ" / "phá cách"
- bang_chung: vị trí sao cụ thể trong lá số
- y_nghia: 60-80 từ giải thích nghĩa thực tế

Ưu tiên cách cục KINH ĐIỂN. KHÔNG bịa cách không có trong TVDSTT.

Output JSON: {"cach_cucs": [{...}, ...]}"""

    def discover_cach_cuc(self) -> dict:
        """Tìm cách cục cho lá số.

        Strategy (Iron Rule #6 — Cơ + Biến):
            1. DICT FIRST — match deterministic với 985 cách kinh điển (Q1+Q3+Q4)
               qua engine.tu_vi.cach_cuc_dict.match_cach_in_chart()
            2. DeepSeek SAU — chỉ khi dict không cho match nào (≥3-star overlap)
               hoặc khi force=True

        Lợi ích: instant + free + truy nguyên về trang gốc.
        """
        cached = None if self.force else _cache_load(self.person.person_key, "cach_cuc", self.person.user_id)
        if cached:
            return cached

        # ── 1. Dict-based deterministic match ───────────────────────────────
        from engine.tu_vi.cach_cuc_dict import match_cach_in_chart

        ls = self.la_so
        s2b = {**ls.get('chinh_tinh', {}), **ls.get('phu_tinh', {}), **ls.get('sat_tinh', {})}
        stars_at_menh = [st for st, idx in s2b.items() if BRANCHES[idx] == ls['menh_branch']]
        stars_in_palaces: dict[str, list[str]] = {}
        for p in ls.get('palaces', []):
            br = BRANCHES[p['branch_index']]
            stars_in_palaces[p['name']] = [st for st, idx in s2b.items() if BRANCHES[idx] == br]

        dict_matches = match_cach_in_chart(
            stars_at_menh=stars_at_menh,
            stars_in_palaces=stars_in_palaces,
            min_overlap=3,
            max_results=30,
        )

        # Convert dict format → unified cach_cuc schema
        cach_cucs = []
        for m in dict_matches:
            cach_cucs.append({
                "ten": m.get("ten", ""),
                "cap_do": m.get("cap_do", "?"),
                "bang_chung": ", ".join(m.get("_overlap_stars", [])[:6]),
                "y_nghia": m.get("y_nghia", ""),
                "nguon": "phú_thái_vi_dict",
                "occurrences_in_sach": m.get("occurrences", 0),
                "overlap_count": m.get("_overlap_count", 0),
                "source_pages": [s.get("page") for s in m.get("sources", [])[:3]],
            })

        cost = 0.0
        # ── 2. Fallback DeepSeek if dict empty ──────────────────────────────
        if not cach_cucs:
            from engine.yi_publishing.translator import get_deepseek_client
            try:
                client = get_deepseek_client()
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_DISCOVER},
                        {"role": "user", "content": f"{self.chart_summary}\n\nHãy tìm 6-8 cách cục."},
                    ],
                    response_format={"type": "json_object"}, timeout=180, max_tokens=4000,
                )
                u = resp.usage
                cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
                parsed = json.loads(resp.choices[0].message.content)
                for c in parsed.get("cach_cucs", []):
                    c["nguon"] = "deepseek_fallback"
                    cach_cucs.append(c)
            except Exception as e:
                logger.warning(f"deepseek fallback fail: {e}")

        data = {
            "person_key": self.person.person_key,
            "person_name": self.person.name,
            "generated_at": int(time.time()),
            "cost_usd": round(cost, 6),
            "cach_cucs": cach_cucs,
        }
        _cache_save(self.person.person_key, "cach_cuc", data, self.person.user_id)
        return data

    # ── 2. Synastry ─────────────────────────────────────────────────────────

    SYSTEM_SYN = """Bạn là chuyên gia Tử Vi Đẩu Số chuyên về SYNASTRY (đối chiếu 2 lá số vợ chồng hoặc partners).

Cho 2 lá số, phân tích các quan hệ chính.

Output JSON: {
  "hop_menh_cuc": "<đánh giá>",
  "menh_chu_tuong_tac": "<phân tích>",
  "phu_the_vs_menh_kia": "<chi tiết>",
  "phu_the_kia_vs_menh_minh": "<chi tiết>",
  "than_chong_chap": "<đặc biệt nếu Thân trùng cung>",
  "hoa_loc_ky_cheo": "<điểm sáng + cảnh báo>",
  "tam_hop_luc_xung": "<cung tương tác>",
  "diem_sang": [...],
  "diem_can_chu_y": [...],
  "ung_dung_doi_song": "<200 từ — gợi ý cụ thể>"
}"""

    def synastry(self, other: "TuViAnalyzer") -> dict:
        key = f"synastry_{other.person.person_key}"
        cached = None if self.force else _cache_load(self.person.person_key, key, self.person.user_id)
        if cached:
            return cached

        from engine.yi_publishing.translator import get_deepseek_client
        client = get_deepseek_client()
        user_prompt = f"{self.chart_summary}\n\n{other.chart_summary}"
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.SYSTEM_SYN},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"}, timeout=180, max_tokens=5000,
        )
        u = resp.usage
        cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
        try:
            syn = json.loads(resp.choices[0].message.content)
        except Exception:
            syn = {}

        data = {
            "person_key": self.person.person_key,
            "other_person_key": other.person.person_key,
            "generated_at": int(time.time()),
            "cost_usd": round(cost, 6),
            "synastry": syn,
        }
        _cache_save(self.person.person_key, key, data, self.person.user_id)
        return data

    # ── 3. Đại Vận annotations ──────────────────────────────────────────────

    # ─── Paradigm guard (Iron Rule #6) — prepended to every vận-hạn prompt ───────
    # Tử Vi = đọc đồng dạng, KHÔNG predict. The vận sections (Đại Vận / Lưu Niên /
    # Lưu Nguyệt) are the most prone to fortune-telling, so they carry the guard too.
    PARADIGM_GUARD = """⚠️ PARADIGM (Iron Rule #6 — BẮT BUỘC): Tử Vi = ĐỌC ĐỒNG DẠNG, KHÔNG phải predict.
- TUYỆT ĐỐI TRÁNH fortune-telling: "sẽ giàu/nghèo", "sẽ thành công/thất bại", "năm X tốt/xấu", gán nhãn verdict cát/hung.
- Vận = tấm gương phản chiếu cấu trúc tâm-thiên-thân. Mô tả vận này PHẢN CHIẾU điều gì + MỜI QUAN-SÁT điều gì, KHÔNG phán cát/hung.
- "Thập bát tinh chuyển, tại nhân biến thông — bất khả chấp nhất": sao vận chuyển tùy người, KHÔNG định mệnh.

"""

    SYSTEM_DV = PARADIGM_GUARD + """Bạn là chuyên gia Tử Vi Đẩu Số viết phân tích Đại Vận (10 năm) theo paradigm đồng dạng (CƠ snapshot + BIẾN chuyển hóa), KHÔNG predict cát/hung.

Output JSON: {
  "tong_quan": "<60-90 từ — đại vận này phản chiếu điều gì>",
  "co_hoi": [...] (3 — khí chất/cơ hội để quan-sát, không hứa hẹn),
  "thach_thuc": [...] (3 — điểm cần lưu tâm, không phán hung),
  "loi_khuyen": "<50-80 từ — nên quan-sát/nuôi dưỡng điều gì>"
}"""

    def dai_van_annotate(self) -> dict:
        cached = None if self.force else _cache_load(self.person.person_key, "dai_van", self.person.user_id)
        if cached:
            return cached

        ls = self.la_so
        palace_to_branch = {p['name']: BRANCHES[p['branch_index']] for p in ls['palaces']}
        branch_to_palace = {v: k for k, v in palace_to_branch.items()}
        s2b = {**ls['chinh_tinh'], **ls['phu_tinh'], **ls.get('sat_tinh', {})}
        branch_to_stars: dict[str, list[str]] = {b: [] for b in BRANCHES}
        for st, idx in s2b.items():
            branch_to_stars[BRANCHES[idx]].append(st)

        # Current age (lunar)
        from datetime import datetime
        birth_year = int(self.person.birth_datetime_local[:4])
        current_year = datetime.now().year
        current_age = current_year - birth_year + 1

        from engine.yi_publishing.translator import get_deepseek_client
        client = get_deepseek_client()

        annotations = []
        total_cost = 0
        ctx = self.chart_summary
        for dv in ls.get('dai_van', []):
            br = dv['branch']
            palace = branch_to_palace.get(br, '?')
            stars = branch_to_stars.get(br, [])
            cycle = dv['cycle_index']
            start_age = dv['start_age']
            end_age = dv['end_age']
            is_current = start_age <= current_age <= end_age
            start_year = current_year - current_age + start_age
            end_year = current_year - current_age + end_age

            user_p = f"""{ctx}

ĐẠI VẬN V{cycle}: tuổi {start_age}-{end_age} (năm {start_year}-{end_year}){'  ⭐ ĐANG TRẢI QUA' if is_current else ''}
- Cung đại vận: {br} ({palace})
- Sao tại cung: {', '.join(stars) if stars else '(vô chính tinh)'}

Viết phân tích đại vận V{cycle}."""

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.SYSTEM_DV},
                    {"role": "user", "content": user_p},
                ],
                response_format={"type": "json_object"}, timeout=90, max_tokens=1500,
            )
            u = resp.usage
            cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
            total_cost += cost
            try:
                ann = json.loads(resp.choices[0].message.content)
            except Exception:
                ann = {}
            ann = _paradigm_postcheck(ann)
            annotations.append({
                "cycle_index": cycle,
                "start_age": start_age, "end_age": end_age,
                "start_year": start_year, "end_year": end_year,
                "branch": br, "palace": palace, "stars": stars,
                "is_current": is_current,
                "tong_quan": ann.get('tong_quan', ''),
                "co_hoi": ann.get('co_hoi', []),
                "thach_thuc": ann.get('thach_thuc', []),
                "loi_khuyen": ann.get('loi_khuyen', ''),
            })

        data = {
            "person_key": self.person.person_key,
            "person_name": self.person.name,
            "birth": self.person.birth_datetime_local,
            "current_age": current_age,
            "current_year": current_year,
            "generated_at": int(time.time()),
            "cost_usd": round(total_cost, 6),
            "annotations": annotations,
        }
        _cache_save(self.person.person_key, "dai_van", data, self.person.user_id)
        return data

    # ── 4. Lưu Niên (5 years window) ────────────────────────────────────────

    SYSTEM_LN = PARADIGM_GUARD + """Bạn là chuyên gia Tử Vi Đẩu Số viết LƯU NIÊN (vận năm) theo paradigm đồng dạng, KHÔNG predict.

Output JSON: {
  "chu_de": "<1 câu — năm này phản chiếu chủ đề gì>",
  "tong_quan": "<60-90 từ>",
  "linh_vuc_quan_tam": [...],
  "thoi_diem_can_chu_y": [...],
  "loi_khuyen": "<60-80 từ — nên quan-sát/nuôi dưỡng điều gì>",
  "quan_sat": "<1 câu — năm này MỜI QUAN-SÁT điều gì trong tâm-thiên-thân (KHÔNG verdict cát/hung)>"
}"""

    def luu_nien(self, start_year: int, end_year: int) -> dict:
        cache_key = f"luu_nien_{start_year}_{end_year}"
        cached = None if self.force else _cache_load(self.person.person_key, cache_key, self.person.user_id)
        if cached:
            return cached

        from .an_sao import tieu_han_for_age
        ls = self.la_so
        year_branch = ls['year_branch']
        gender = self.person.gender
        birth_year = int(self.person.birth_datetime_local[:4])

        palace_to_branch = {p['name']: BRANCHES[p['branch_index']] for p in ls['palaces']}
        branch_to_palace = {v: k for k, v in palace_to_branch.items()}
        s2b = {**ls['chinh_tinh'], **ls['phu_tinh'], **ls.get('sat_tinh', {})}
        branch_to_stars: dict[str, list[str]] = {b: [] for b in BRANCHES}
        for st, idx in s2b.items():
            branch_to_stars[BRANCHES[idx]].append(st)

        def find_dai_van(age):
            for dv in ls['dai_van']:
                if dv['start_age'] <= age <= dv['end_age']:
                    return dv
            return None

        from engine.yi_publishing.translator import get_deepseek_client
        client = get_deepseek_client()
        years_data = []
        total_cost = 0
        ctx = self.chart_summary

        for year in range(start_year, end_year + 1):
            age = year - birth_year + 1
            th_idx = tieu_han_for_age(year_branch, gender, age)
            th_br = BRANCHES[th_idx]
            th_palace = branch_to_palace.get(th_br, '?')
            th_stars = branch_to_stars.get(th_br, [])
            dv = find_dai_van(age)
            dv_br = dv['branch'] if dv else '?'
            dv_palace = branch_to_palace.get(dv_br, '?')
            dv_stars = branch_to_stars.get(dv_br, [])

            user_p = f"""{ctx}

NĂM {year} ({age} tuổi âm):
- Tiểu Hạn: {th_br} ({th_palace}) — sao: {', '.join(th_stars) or '(rỗng)'}
- Đại Vận V{dv['cycle_index'] if dv else '?'}: {dv_br} ({dv_palace}) — sao: {', '.join(dv_stars) or '(rỗng)'}

Viết lưu niên năm {year}."""

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.SYSTEM_LN},
                    {"role": "user", "content": user_p},
                ],
                response_format={"type": "json_object"}, timeout=90, max_tokens=1500,
            )
            u = resp.usage
            cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
            total_cost += cost
            try:
                ann = json.loads(resp.choices[0].message.content)
            except Exception:
                ann = {}
            ann = _paradigm_postcheck(ann)
            years_data.append({
                "year": year, "age_lunar": age,
                "tieu_han_branch": th_br, "tieu_han_palace": th_palace, "tieu_han_stars": th_stars,
                "dai_van_branch": dv_br, "dai_van_palace": dv_palace, "dai_van_stars": dv_stars,
                "dai_van_cycle": dv['cycle_index'] if dv else None,
                "analysis": ann,
            })

        data = {
            "person_key": self.person.person_key,
            "year_range": [start_year, end_year],
            "generated_at": int(time.time()),
            "cost_usd": round(total_cost, 6),
            "years": years_data,
        }
        _cache_save(self.person.person_key, cache_key, data, self.person.user_id)
        return data

    # ── 5. Lưu Nguyệt (12 tháng âm 1 năm) ───────────────────────────────────

    SYSTEM_LNG = PARADIGM_GUARD + """Bạn là chuyên gia Tử Vi viết LƯU NGUYỆT (vận tháng) theo paradigm đồng dạng, KHÔNG predict.

Output JSON: {
  "chu_de": "<1 câu — tháng này phản chiếu chủ đề gì>",
  "tinh_chat": "<60-80 từ>",
  "viec_lam": [...] (2-3 — nên nuôi dưỡng/quan-sát),
  "viec_tranh": [...] (2-3 — nên lưu tâm),
  "quan_sat": "<1 câu — tháng này MỜI QUAN-SÁT điều gì (KHÔNG verdict cát/hung)>"
}"""

    def luu_nguyet(self, year: int) -> dict:
        cache_key = f"luu_nguyet_{year}"
        cached = None if self.force else _cache_load(self.person.person_key, cache_key, self.person.user_id)
        if cached:
            return cached

        from .an_sao import tieu_han_for_age
        from .dau_quan import compute_dau_quan_for_months
        ls = self.la_so
        birth_year = int(self.person.birth_datetime_local[:4])
        age = year - birth_year + 1
        th_idx = tieu_han_for_age(ls['year_branch'], self.person.gender, age)   # metadata, KHÔNG dùng để gán cung

        luu_nien_branch = BRANCHES[(year - 1984) % 12]          # chi năm lưu (mốc 1984=Giáp Tý)
        lunar_month_birth = ls.get('lunar_month', 1)
        hour_branch_birth = ls.get('hour_branch', 'Tý')
        dq_months = compute_dau_quan_for_months(luu_nien_branch, lunar_month_birth, hour_branch_birth)
        dq_branch_by_month = {m['luu_nguyet_month']: m['dau_quan_branch'] for m in dq_months}

        palace_to_branch = {p['name']: BRANCHES[p['branch_index']] for p in ls['palaces']}
        branch_to_palace = {v: k for k, v in palace_to_branch.items()}
        s2b = {**ls['chinh_tinh'], **ls['phu_tinh'], **ls.get('sat_tinh', {})}
        branch_to_stars: dict[str, list[str]] = {b: [] for b in BRANCHES}
        for st, idx in s2b.items():
            branch_to_stars[BRANCHES[idx]].append(st)

        from engine.yi_publishing.translator import get_deepseek_client
        client = get_deepseek_client()
        months = []
        total_cost = 0
        ctx = self.chart_summary

        # Cung lưu nguyệt mỗi tháng = Đẩu Quân lưu niên (TVĐSTT Q2 tr.88), thuận 1 cung/tháng —
        # cùng quy ước với badge "Đẩu Quân tháng" (an_sao.nguyet_van_per_cung), KHÔNG dùng Tiểu Hạn
        # (đã sửa 2026-07-05: 2 quy ước từng lệch nhau, gây văn bản AI mô tả sai cung so với badge).
        for thang in range(1, 13):
            br = dq_branch_by_month[thang]
            palace = branch_to_palace.get(br, '?')
            stars = branch_to_stars.get(br, [])

            user_p = f"""{ctx}

NĂM {year}, THÁNG {thang} ÂM:
- Đẩu Quân lưu niên {year}: {dq_branch_by_month[1]}
- Cung lưu nguyệt T{thang}: {br} ({palace})
- Sao tại cung: {', '.join(stars) or '(rỗng)'}

Viết lưu nguyệt T{thang}/{year}."""

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.SYSTEM_LNG},
                    {"role": "user", "content": user_p},
                ],
                response_format={"type": "json_object"}, timeout=60, max_tokens=900,
            )
            u = resp.usage
            cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
            total_cost += cost
            try:
                ann = json.loads(resp.choices[0].message.content)
            except Exception:
                ann = {}
            ann = _paradigm_postcheck(ann)
            months.append({
                "thang_am": thang,
                "branch": br, "palace": palace, "stars": stars,
                "analysis": ann,
            })

        data = {
            "person_key": self.person.person_key,
            "year": year,
            "lunar_age": age,
            "tieu_han_branch": BRANCHES[th_idx],
            "generated_at": int(time.time()),
            "cost_usd": round(total_cost, 6),
            "months": months,
        }
        _cache_save(self.person.person_key, cache_key, data, self.person.user_id)
        return data

    # ── 6. Phú Thái Vi match ────────────────────────────────────────────────

    def phu_match(self) -> dict:
        """Score all Phú Thái Vi passages by relevance to chart."""
        cached = None if self.force else _cache_load(self.person.person_key, "phu_match", self.person.user_id)
        if cached:
            return cached

        if not PHU_LAYER3_PATH.exists():
            return {"status": "error", "message": "Phú Thái Vi data not found"}

        phu = json.loads(PHU_LAYER3_PATH.read_text())
        passages = phu.get('passages', [])

        ls = self.la_so
        s2b = {**ls['chinh_tinh'], **ls['phu_tinh'], **ls.get('sat_tinh', {})}
        branch_to_palace = {BRANCHES[p['branch_index']]: p['name'] for p in ls['palaces']}
        tu_hoa = ls.get('tu_hoa', {})

        scored = []
        for p in passages:
            text = (p.get('hanviet', '') + ' ' + p.get('luangiai', '')).lower()
            score = 0
            reasons = []
            for star in s2b:
                if star.lower() in text:
                    score += 2
                    reasons.append(f"có '{star}' (tại {BRANCHES[s2b[star]]})")
            for palace in branch_to_palace.values():
                if palace.lower() in text:
                    score += 1
            for hoa, star in tu_hoa.items():
                if star.lower() in text:
                    score += 4
                    reasons.append(f"🎯 Hóa {hoa} = {star}")
            if score > 0:
                scored.append({"passage": p, "score": score, "reasons": reasons[:5]})

        scored.sort(key=lambda x: -x['score'])
        data = {
            "person_key": self.person.person_key,
            "generated_at": int(time.time()),
            "total_scored": len(scored),
            "matched_passages": scored[:30],
        }
        _cache_save(self.person.person_key, "phu_match", data, self.person.user_id)
        return data

    # ── 6b. Cung Readings — group Q1+Q3 passages by palace ──────────────────

    def cung_reading(self) -> dict:
        """Build per-palace reading bundle from Q1 Phú + Q3 raw lines.

        For each of the 12 palaces in the chart, surface:
          - stars at this palace (chinh + phu + sat)
          - star schemas (keywords, tích cực, tiêu cực)
          - Q1 Phú Thái Vi passages relevant to this palace
          - Q3 Diễn Giải sao×cung raw lines mentioning stars + palace/branch
        """
        cached = None if self.force else _cache_load(self.person.person_key, "cung_reading", self.person.user_id)
        if cached:
            return cached

        from engine.tu_vi.cung_reading import build_cung_readings

        ls = self.la_so
        # Build chart_summary dict shape expected by build_cung_readings
        s2bi = {**ls.get('chinh_tinh', {}), **ls.get('phu_tinh', {}), **ls.get('sat_tinh', {})}
        star_to_branch = {star: BRANCHES[bi] for star, bi in s2bi.items()}
        palace_to_branch = {p['name']: BRANCHES[p['branch_index']] for p in ls.get('palaces', [])}
        chart_dict = {
            "palace_to_branch": palace_to_branch,
            "star_to_branch": star_to_branch,
        }

        # Pull Q1 phu_matches (auto-generate if not cached)
        phu_data = self.phu_match()
        phu_matches = phu_data.get('matched_passages', []) if isinstance(phu_data, dict) else []

        result = build_cung_readings(chart_dict, phu_matches)
        data = {
            "person_key": self.person.person_key,
            "generated_at": int(time.time()),
            **result,
        }
        _cache_save(self.person.person_key, "cung_reading", data, self.person.user_id)
        return data

    # ── 6c. Phê mệnh generator — phú thi style với "mỗ" pattern (Q4) ────────

    SYSTEM_PHE_MENH = """Bạn là bậc trí giả Tử Vi Đẩu Số — **Trần Đoàn** (Hi Di tiên sinh, chính tổ) với **Khang Tiết bổ chú** ở 4-5 chỗ trọng yếu (Q2 Cự Môn + Đà La, Q3 Tử Phá Thìn Tuất, Q4 Thạch Trung Ẩn Ngọc + phê mệnh p0258 duyệt).

Bạn viết **PHÊ MỆNH** theo phong cách Q4 Tử Vi Đẩu Số Toàn Thư — học từ **7 phê mệnh templates** (p0257 + p0259 + p0260 + p0261 + p0262 + p0263 + p0264) + ~50 phú thi 4-câu từ 18 Phi Tinh detail.

Cấu trúc theo **10 BƯỚC METHODOLOGY** (Q4 p0266 Trần Đoàn chính thức):
1. Định thời khắc → 2. Khởi Bát Tự → 3. Lập cách → 4. An sao → 5. Lập tọa Mệnh
→ 6. Khởi Đại Vận → 7. Khởi Đại Hạn → 8. Thư Tứ Hóa → 9. Thư hỉ kỵ → 10. Bài cát hung

Gộp 10 bước thành 5 output sections cho readability.

⚠️ IRON RULES (Iron Rule #6 — KHÔNG PREDICT):

1. **Phong cách**: phú thi 4-7 chữ mỗi câu, vần điệu, ẩn dụ (Phù Tang, Phượng Hoàng, mây che, lá rụng).
   Câu HV ngắn gọn + dòng diễn giải VN ngay dưới.

2. **"MỖ" PATTERN BẮT BUỘC** — KHÔNG bao giờ nói rõ năm/sao cụ thể khi nói về tương lai:
   - ❌ SAI: "Năm 2030 anh sẽ X"
   - ✅ ĐÚNG: "Mỗ niên mỗ tinh nghi thận nội ngoại thương ưu" (năm nào sao nào cẩn trọng nội ngoại)
   - ✅ ĐÚNG: "Mỗ hạn phùng Đà, vưu kiến lặc sàng" (hạn nào gặp Đà La, càng thấy hao tổn)
   - ✅ ĐÚNG: "Duy đáo mỗ tinh, vân yểm vô quang" (chỉ đến 1 sao nào đó, mây che mất ánh sáng)
   Mục đích: gợi mở để TÂM user soi xét, không phán cứng.

3. **2 VOICE — Trần Đoàn (dominant ~90%) + Khang Tiết (bổ chú specific cases)**:
   - Voice Trần Đoàn (CƠ): mô tả snapshot cách cục, sao tại cung — chủ đạo
   - Voice Khang Tiết (BIẾN): chỉ dùng khi có pattern match cụ thể (Tử Phá Thìn Tuất + cách Cự Môn hãm + Thạch Trung Ẩn Ngọc)

4. **KHÔNG fortune-telling**: KHÔNG "anh sẽ giàu" / "anh sẽ chết yểu" / "vợ anh sẽ phản bội".
   Đọc đồng dạng — phản chiếu cấu trúc tâm-thiên-thân, KHÔNG predict.

5. **Có dẫn chứng cổ nhân** (nếu match): Trác Mậu/Lỗ Cung/Cung Toại/Hoàng Bá/Sơ Quảng+Thụ (Thanh Quan Hán), An Lộc Sơn/Triệu Cao (Tử Phá Thìn Tuất cảnh báo), Khổng Tử (Thiên Di Tý/Ngọ), Tử Lộ (Liêm Trinh nhập miếu hội Tướng Quân).

6. **Tâm an** ở cuối: paradigm Q4 p0299 r018 "**Thập bát tinh chuyển, tại nhân biến thông. Bất khả chấp nhất**" — 18 sao vận chuyển tùy người. Lá số là gương phản chiếu, KHÔNG định mệnh.

OUTPUT JSON với 5 phần (mỗi phần là Markdown text, 6-12 câu phú thi 4-7 chữ + diễn giải VN):
{
  "khai_de": "Bước 1+5 — Mở phê mệnh: định thời khắc + lập tọa Mệnh (tam phương tứ chính)",
  "menh_than": "Bước 2+3+4 — CƠ snapshot: Bát Tự + Cách Cục + An sao (Trần Đoàn voice)",
  "dai_van": "Bước 6+7+8 — BIẾN: Đại Vận + Lưu Niên + Tứ Hóa với 'mỗ' pattern (Khang Tiết style nếu match cases)",
  "canh_bao": "Bước 9 — hỉ kỵ + đảo hạn thần sát + psych safety wrap nhẹ nhàng",
  "ket_tam_an": "Bước 10 — khích lệ TÂM, không phán định mệnh + paradigm 'bất khả chấp nhất'"
}"""

    def phe_menh(self) -> dict:
        """Tạo phê mệnh phú thi style cho lá số (Q4 Khang Tiết Edition).

        Sử dụng DeepSeek-chat (cheap). Cache per person.
        """
        cached = None if self.force else _cache_load(self.person.person_key, "phe_menh", self.person.user_id)
        if cached:
            return cached

        # Provider chain: deepseek ĐẦU — deepseek-chat (V3→v4-flash) verified prod TIN CẬY cho
        # prompt phê mệnh JSON (16s, JSON hợp lệ). model reasoning (v4-pro, MiniMax-M3 và CẢ
        # M2.7-highspeed) <think> ăn sạch token → content RỖNG (đo prod 2026-06-24). minimax CUỐI.
        # Chọn + gọi provider ở loop bên dưới (cần fallback theo content-RỖNG, không chỉ exception).
        from engine.ai.registry import get_registry
        registry = get_registry()

        # Build rich context — chart + cách cục + cung reading + safety
        ctx_parts = [self.chart_summary]

        try:
            cach_data = self.discover_cach_cuc()
            cachs = cach_data.get("cach_cucs", [])[:5]
            if cachs:
                ctx_parts.append("\n=== Cách cục đã match ===")
                for c in cachs:
                    ctx_parts.append(f"- {c.get('ten')} ({c.get('cap_do')}): {c.get('y_nghia', '')[:120]}")
        except Exception:
            pass

        try:
            from engine.tu_vi.case_matcher import match_cases
            cases = match_cases(self.la_so, top_n=2)
            if cases.get("matches"):
                ctx_parts.append("\n=== Nét giống lịch sử (Q3+Q4 cases) ===")
                for m in cases["matches"]:
                    ctx_parts.append(f"- {m['pattern_name']} ({m['polarity']}): {m['lesson_short']}")
        except Exception:
            pass

        try:
            from engine.tu_vi.psychological_safety import detect_safety_patterns
            from core.chronos import calculate_chronos_state
            chronos = calculate_chronos_state(self.person.birth_datetime_local, self.person.timezone)
            year_stem = chronos.ganzhi.year.split()[0]
            safety = detect_safety_patterns(self.la_so, year_stem)
            if safety:
                ctx_parts.append("\n=== Safety patterns (cần lưu ý nhẹ trong canh_bao) ===")
                for p in safety:
                    ctx_parts.append(f"- {p['title']}: {p['gentle_message']}")
        except Exception:
            pass

        ctx = "\n".join(ctx_parts)
        user_prompt = f"""{ctx}

Viết phê mệnh phú thi 5 phần theo IRON RULES.
Mỗi phần khoảng 4-8 câu phú style 4-7 chữ + diễn giải VN.
KHÔNG predict cụ thể — dùng "mỗ" pattern khi nói về tương lai."""

        # Reinforce JSON output in user prompt (some providers don't honor response_format)
        full_user_prompt = user_prompt + "\n\n**OUTPUT BẮT BUỘC**: JSON object đầy đủ 5 keys (khai_de, menh_than, dai_van, canh_bao, ket_tam_an). KHÔNG markdown wrapper, KHÔNG ```json fence."

        # Gọi theo chain, ÉP model non-reasoning, NHẬN provider ĐẦU TIÊN trả content KHÔNG RỖNG.
        # Mấu chốt: model reasoning trả status-ok nhưng content="" (think ăn token rồi bị strip)
        # → fallback-theo-exception KHÔNG bắt được. Phải kiểm content rỗng để nhảy provider kế.
        from engine.ai.council import sage_model
        messages = [
            {"role": "system", "content": self.SYSTEM_PHE_MENH},
            {"role": "user", "content": full_user_prompt},
        ]
        resp = None
        provider = None
        last_err = "no provider configured"
        for _name in ["deepseek", "gemini", "openrouter", "anthropic", "minimax"]:
            try:
                _p = registry.get(_name)
            except Exception:
                continue
            if not getattr(_p, "is_configured", False) or registry.is_unhealthy(_name):
                continue
            try:
                _r = _p.chat(messages=messages, model=sage_model(_p),
                             temperature=0.7, max_tokens=4000)
            except Exception as e:
                last_err = f"{_name}: {e}"
                continue
            if (getattr(_r, "content", "") or "").strip():
                resp, provider = _r, _p
                break
            last_err = f"{_name}: empty content (reasoning ăn token?)"
        if resp is None or provider is None:
            return {"status": "error", "message": f"Tất cả provider rỗng/lỗi. Last: {last_err}"}

        content = resp.content if hasattr(resp, "content") else str(resp)
        # Try to strip markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.startswith("```"))

        try:
            phe = json.loads(content)
        except Exception:
            # Fallback: treat as plain text
            phe = {"khai_de": content}

        prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
        completion_tokens = getattr(resp, "completion_tokens", 0) or 0
        cost = getattr(resp, "cost_usd", 0) or 0
        u = type("Usage", (), {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens})()

        data = {
            "status": "ok",
            "person_key": self.person.person_key,
            "person_name": self.person.name,
            "generated_at": int(time.time()),
            "provider": provider.name,
            "cost_usd": round(cost, 6),
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
            },
            "phe_menh": phe,
            "paradigm_note": "Phê mệnh viết theo phong cách Q4 Khang Tiết Edition — dùng 'mỗ' pattern (gợi mở, KHÔNG predict). Iron Rule #6 + #4.",
        }
        _cache_save(self.person.person_key, "phe_menh", data, self.person.user_id)
        return data

    # ── 6c. Phê mệnh SÂU (VIP DeepSeek Pro) ─────────────────────────────────

    SYSTEM_PHE_MENH_SAU = """Bạn là CHUYÊN GIA TỬ VI ĐẨU SỐ giảng giải cho **NGƯỜI VIỆT BÌNH THƯỜNG** (không học Hán-Việt).

🎯 NGUYÊN TẮC TỐI THƯỢỢNG: **NGƯỜI ĐỌC PHẢI HIỂU NGAY**.
Anh là thầy giảng Tử Vi cho học trò mới — không phải thư sinh ngâm thơ cổ.
Văn phong: **TIẾNG VIỆT HIỆN ĐẠI, ĐỜI THƯỜNG, RÕ RÀNG**, như đang nói chuyện với bạn thân.

══════════════════════════════════════════════════════════════
📐 CẤU TRÚC BẮT BUỘC MỖI SECTION (3 LỚP rõ ràng):
══════════════════════════════════════════════════════════════

**LỚP 1 — TINH HOA CỔ NHÂN** (200-400 chars, optional, có thì giữ truyền thống):
- 1 đoạn phú thi Hán-Việt 4-8 câu (4-7 chữ/câu) — chỉ để mở đầu, gợi không khí
- NGAY SAU đó BẮT BUỘC có dòng "📜 **Dịch nghĩa**: ..." giải nghĩa toàn bộ phú thi sang Việt thuần

**LỚP 2 — GIẢI THÍCH NGUYÊN LÝ** (500-1000 chars):
- Tử Vi đang nói GÌ về anh? (1-2 câu Việt thuần)
- Sao chính nào quan trọng nhất ở section này? Đặt ở cung nào của lá số?
- Khi gặp thuật ngữ Hán-Việt LẦN ĐẦU → BẮT BUỘC giải nghĩa trong ngoặc đơn ngay sau
  Ví dụ: "Mệnh đắc Lộc Tồn (sao tài lộc, mang ý nghĩa của cải bền vững)"
  Ví dụ: "cung Phúc Đức (cung nói về phúc khí gia tộc, hậu vận an nhàn)"
  Ví dụ: "Tham Lang hóa Lộc (sao Tham Lang đổi tính chất, từ ham muốn trở thành nguồn tài chính)"

**LỚP 3 — ÁP DỤNG VÀO ĐỜI SỐNG** (1500-3000 chars, PHẦN QUAN TRỌNG NHẤT):
- Cụ thể trong cuộc sống anh, điều này nghĩa là gì?
- Ví dụ đời thực: nếu cách cục X, người ta thường gặp tình huống Y trong sự nghiệp/gia đình/sức khỏe
- So sánh với người không có cách cục đó (để anh thấy sự khác biệt)
- Lời khuyên cụ thể: nên làm gì, tránh gì, lưu ý gì
- Gọi anh là "Anh" hoặc tên (nếu có) — viết như tâm sự với người thân
- Câu văn ngắn, dễ hiểu (15-25 chữ/câu), không dùng cấu trúc cổ văn

══════════════════════════════════════════════════════════════
🚫 TUYỆT ĐỐI KHÔNG:
══════════════════════════════════════════════════════════════
- ❌ Viết toàn bộ section bằng Hán-Việt cổ văn (như: "Kỳ nhất, Thiên Đồng thủ Mệnh cách. Phú vân...")
- ❌ Dùng từ Hán-Việt mà không giải nghĩa ngay sau (ngay lần đầu xuất hiện)
- ❌ Câu kết cấu kiểu "thử nãi/chính thị/cố vị" — phải dùng "đây là/chính là/nghĩa là"
- ❌ Viết kiểu "Anh quân thiện tế thính" → phải viết "Anh đọc kỹ nhé"
- ❌ Bịa sao/cung không có trong DUMP lá số phía dưới

══════════════════════════════════════════════════════════════
✅ PHẢI LÀM:
══════════════════════════════════════════════════════════════
1. Mỗi từ Hán-Việt đầu tiên xuất hiện → giải nghĩa trong ngoặc đơn ngay
2. Dẫn sao + cung CHÍNH XÁC theo DUMP lá số (phía dưới user prompt)
3. Quote cổ điển (Phú Thái Vi, etc.) → giữ Hán-Việt nhưng PHẢI dịch sang Việt ngay sau
   Ví dụ: 'Cổ phú có câu "Phúc tinh lai hựu" (sao phúc tới phù trì), nghĩa là...'
4. Khi nói tương lai → dùng "mỗ" pattern (mỗ năm, mỗ tinh) — Việt thuần: "vài năm tới", "khi sao X chiếu"
5. Tôn trọng paradigm: lá số = TẤM GƯƠNG đọc đồng dạng, KHÔNG dự đoán cứng. Đây là Iron Rule #6.
6. Mỗi section TỔNG cộng 2000-4000 chữ Tiếng Việt
7. **TRUNG CHÂU PARADIGM** (BẮT BUỘC từ 2026-06-08, sau 32 vòng thâm nhuần Q2 Vương Đình Chỉ):
   - Trong DUMP phía dưới có block "BÍ TRUYỀN TRUNG CHÂU" với 3 Iron Rule + paradigm chính tinh × cung khớp lá số này
   - **BẮT BUỘC** mỗi section dùng ÍT NHẤT 1 paradigm Trung Châu (nếu có khớp lá số)
   - **BẮT BUỘC** trích dẫn TRỰC TIẾP cụm từ "Vương Đình Chỉ Q2 p<số trang>" hoặc tên Iron Rule
     ("DI CUNG HOÁN VỊ", "XU CÁT TỊ HUNG", "HƯ TÂM LÃNH HỘI") khi áp dụng
   - Section 6 Đại Vận + 7 Lưu Niên: PHẢI dùng DI CUNG HOÁN VỊ (không chỉ xem cung Mệnh đại vận tam phương)
   - Section 10 Kết Tâm An: PHẢI nhấn mạnh XU CÁT TỊ HUNG (hành động hậu thiên xoay chuyển vận)
   - VÍ DỤ ĐÚNG: "Theo bí truyền phái Trung Châu (Vương Đình Chỉ Q2 p501), khi đến Đại Vận thì cung Mệnh DI CHUYỂN..."
   - VÍ DỤ SAI: "Khi vào vận hạn này..." (không citation = SAI)
   - Khi paradigm chính tinh × cung khớp (ví dụ "Mệnh Thiên Lương = ấm tinh") → DÙNG NGUYÊN VĂN cụm Hán-Việt + giải nghĩa Việt ngay sau

══════════════════════════════════════════════════════════════
📋 OUTPUT JSON THUẦN (5 keys mỗi batch):
══════════════════════════════════════════════════════════════
- BẮT ĐẦU bằng `{`, KẾT THÚC bằng `}`. KHÔNG dùng ``` code fence.
- Mỗi value là STRING đơn (xuống dòng dùng \\n).
- Quote " trong string escape thành \\".

Tên keys CHÍNH XÁC: dinh_thoi_khac, khoi_bat_tu, lap_cach_dung_than, bai_tinh_than, lap_toa_menh,
dai_van_phan_tich, dai_han_luu_nien, tu_hoa_dien_giai, hi_ky_canh_bao, ket_tam_an."""

    # Section schemas — split into 2 batches to avoid output truncation
    _PHE_MENH_SAU_BATCH_1 = [
        ("dinh_thoi_khac", "1. ĐỊNH THỜI KHẮC",
         "Phân tích thời điểm sinh — giờ Tý chính/sơ, can chi giờ-ngày-tháng-năm, "
         "vị trí khí số trong vũ trụ tại khoảnh khắc đản sinh."),
        ("khoi_bat_tu", "2. KHỞI BÁT TỰ (Tứ Trụ)",
         "Tứ trụ năm-tháng-ngày-giờ; ngũ hành các trụ; vượng-tướng-hưu-tù-tử; "
         "thiên can địa chi gặp gỡ ra sao."),
        ("lap_cach_dung_than", "3. LẬP CÁCH — DỤNG THẦN",
         "Đối chiếu Q1 Phú Thái Vi 545 cách cục: cách nào TRỰC TIẾP match lá số? "
         "Dụng thần là sao gì? Cách phù-tá-kỵ-hỉ thế nào? Trích Hán-Việt verbatim quote từ Phú."),
        ("bai_tinh_than", "4. BÀI TINH THẦN (14 chính tinh + Tứ Hóa + phụ-sát tinh)",
         "Đi từng cung quan trọng: Mệnh, Thân, Phúc Đức, Quan Lộc, Tài Bạch, Thiên Di. "
         "Sao chủ + sao hỗ trợ + sao kỵ. Miếu/Vượng/Hãm/Bình. Tứ hóa rơi vào đâu, ảnh hưởng cụ thể."),
        ("lap_toa_menh", "5. LẬP TỌA MỆNH (tam phương tứ chính)",
         "Cung Mệnh + tam hợp + xung chiếu = cấu trúc TỌA MỆNH. "
         "Tâm-Tính-Mệnh của chủ nhân = TÍNH (qua sao Mệnh) × VẬN (qua Thân) × DUYÊN (qua Đẩu Quân). "
         "Trần Đoàn: chủ nhân thuộc TYPE NGƯỜI nào trong 36 archetypes (12 giờ × 3 khắc)."),
    ]

    _PHE_MENH_SAU_BATCH_2 = [
        ("dai_van_phan_tich", "6. ĐẠI VẬN PHÂN TÍCH (8 vòng đời)",
         "Liệt kê TẤT CẢ 8 vòng đại vận với cung-sao-tuổi cụ thể. "
         "Mỗi vòng: sao chủ cung đại vận đó là gì, hỗ trợ hay phá, "
         "khả năng kích hoạt cách cục nào, 'mỗ niên' đáng quan tâm."),
        ("dai_han_luu_nien", "7. ĐẠI HẠN + LƯU NIÊN (5 năm gần)",
         "Đại hạn hiện tại + lưu niên 2026/2027/2028/2029/2030 — "
         "mỗi năm: cung lưu niên ở đâu, sao gặp lưu, lưu Lộc/Quyền/Khoa/Kỵ chiếu cung nào. "
         "Dùng 'mỗ niên mỗ tinh nghi thận' khi nói tương lai."),
        ("tu_hoa_dien_giai", "8. TỨ HÓA DIỄN GIẢI SÂU",
         "4 sao hóa Lộc-Quyền-Khoa-Kỵ năm sinh + 4 hóa đại vận hiện tại + 4 hóa lưu niên. "
         "Mỗi hóa rơi cung nào, sinh khắc thế nào, ý nghĩa Hán-Việt trích Q1+Q2."),
        ("hi_ky_canh_bao", "9. HỈ KỴ + CẢNH BÁO ĐẢO HẠN",
         "Sao hỉ (Lộc Tồn, Thiên Mã, Tứ Linh) gặp đúng cung — phúc dày. "
         "Sao kỵ (Hỏa Linh Kình Đà Không Kiếp Hóa Kỵ) tụ — đảo hạn. "
         "Psychological safety patterns (Q3 p0186): 'cô' / 'hình' / 'kỵ' / 'không'. "
         "Bài thần sát: Thiên La, Địa Võng, Cô Thần, Quả Tú, Phục Binh."),
        ("ket_tam_an", "10. KẾT TÂM AN — BÀI CÁT HUNG + paradigm 'bất khả chấp nhất'",
         "Tổng kết theo Q4 p0299 'Thập bát tinh chuyển, tại nhân biến thông'. "
         "Lá số là TẤM GƯƠNG, không phải số phận. "
         "TÂM trí của chủ nhân là then chốt xoay chuyển. "
         "Lời gửi cuối cùng từ Trần Đoàn + Khang Tiết cho chủ nhân."),
    ]

    def _phe_menh_sau_batch_call(self, *, batch_name: str, sections: list, base_ctx: str,
                                  provider, registry, candidate_providers: list) -> tuple:
        """Run ONE batch call (5 sections). Returns (parsed_dict, provider_used, tokens_used, cost_used)."""
        # Build per-section instructions
        section_specs = []
        for key, label, desc in sections:
            section_specs.append(f'  "{key}":  → {label}\n    Yêu cầu: {desc}')
        section_keys = [s[0] for s in sections]
        sections_block = "\n".join(section_specs)

        user_prompt = f"""{base_ctx}

══════════════════════════════════════════════════════════════
TASK: Viết phê mệnh SÂU — **BATCH {batch_name}** (5 sections)
Đối tượng đọc: **NGƯỜI VIỆT BÌNH THƯỜNG**, không học Hán-Việt cổ.
══════════════════════════════════════════════════════════════

🎯 YÊU CẦU TUYỆT ĐỐI (anh PHẢI tuân thủ — đây là VIP quality cho người Việt):

0️⃣  **BÁM KHO SÁCH ĐÃ DUYỆT** (quan trọng nhất — đây là bản TRẢ PHÍ):
    Khối "★ KHO SÁCH ĐÃ DUYỆT" ở trên là trích dẫn THẬT từ sách cổ, đã kiểm chứng, khớp
    đúng lá số này. Khi luận về **SAO ở từng cung**, **TỨ HÓA**, **ĐẠI VẬN** → PHẢI dùng
    các trích dẫn đó làm xương sống và **GHI TÊN SÁCH** ngay trong câu
    (vd: "sách Trung Châu phái viết: …", "theo Đẩu Số Tinh Thành: …").
    · Ý nào KHÔNG có trong kho → nói bằng nguyên lý chung, KHÔNG bịa thành 'sách nói'.
    · TUYỆT ĐỐI KHÔNG bịa tên sách / số trang / câu phú không có trong kho.
    · Ưu tiên nội dung kho hơn trí nhớ của chính anh khi hai bên khác nhau.

1️⃣  **Mỗi section ~2000-4000 chữ Tiếng Việt** — không ít hơn 2000.

2️⃣  **NGÔN NGỮ VIỆT THUẦN HIỆN ĐẠI**, không sa đà cổ văn.
    ❌ KHÔNG: "Kỳ nhất, Thiên Đồng thủ Mệnh, phúc thọ song toàn"
    ✅ DÙNG: "Trước tiên, Anh có sao Thiên Đồng (sao Phúc — biểu tượng phúc khí, an nhàn) tọa cung Mệnh. Đây là một điểm mạnh: cổ nhân nói 'Thiên Đồng thủ Mệnh, phúc thọ song toàn' — nghĩa là sao Thiên Đồng ở cung Mệnh đem lại cả phúc lẫn thọ."

3️⃣  **CẤU TRÚC 3 LỚP** mỗi section (rất quan trọng):
    - **(A) Mở đầu cổ văn** (200-300 chữ): 1 đoạn phú thi 4-8 câu Hán-Việt + dòng "📜 Dịch nghĩa: ..." giải toàn bộ
    - **(B) Giải thích nguyên lý** (500-1000 chữ): Tử Vi nói gì? Sao nào quan trọng? Mỗi thuật ngữ Hán-Việt LẦN ĐẦU xuất hiện → giải nghĩa trong ngoặc đơn NGAY
    - **(C) Áp dụng đời sống** (1500-2700 chữ, PHẦN CHÍNH): Cụ thể trong cuộc sống Anh nghĩa là gì? Ví dụ thực tế. So sánh với người không có cách. Lời khuyên cụ thể.

4️⃣  **TỪ HÁN-VIỆT LẦN ĐẦU PHẢI GIẢI NGHĨA**:
    - Mệnh = cung số 1, nói về bản thân anh
    - Lộc Tồn = sao tài lộc, mang ý nghĩa của cải bền vững
    - Tử Vi đế tinh = sao chủ tướng, nghĩa là sao "vua" trong hệ thống
    - Tứ Hóa = 4 dạng biến hóa (Lộc-Quyền-Khoa-Kỵ) tương đương tiền-quyền-danh-họa
    - Tam phương tứ chính = 4 cung tạo thành "vùng ảnh hưởng" của Mệnh
    (Khi DUMP đã có thuật ngữ, anh giải nghĩa LẦN ĐẦU rồi dùng tự nhiên các lần sau)

5️⃣  **DẪN CHÍNH XÁC TỪ DUMP** (không bịa):
    - Sao nào ở cung nào → DUMP ghi rõ. Anh trích đúng.
    - Tứ Hóa rơi đâu → DUMP ghi rõ.
    - Đại Vận tuổi nào ở cung nào → DUMP ghi rõ.

6️⃣  **DẪN CHỨNG CỔ NHÂN khi phù hợp** (Trác Mậu, Cung Toại, Hoàng Bá, Sơ Quảng-Sơ Thụ, Khổng Tử-Tử Lộ, An Lộc Sơn) — kèm giải thích NGẮN ai là ai, làm gì.

7️⃣  **MỖ PATTERN** dùng Việt thuần khi nói tương lai:
    ❌ "Mỗ niên mỗ tinh nghi thận"
    ✅ "Một vài năm tới, khi sao X chiếu Y, Anh nên cẩn thận"

8️⃣  **KHAI THÁC TRIỆT ĐỂ Q4 (Tử Vi Đẩu Số Toàn Thư Quyển 4)** — DUMP phía trên có sẵn:
    - 🔸 **Mệnh chủ + Thân chủ + Đẩu Quân** — đoạn "⚠️ NHẮC LẠI QUAN TRỌNG" cuối DUMP. PHẢI dùng đúng tên sao Mệnh chủ (KHÔNG bịa Liêm Trinh nếu DUMP ghi Vũ Khúc).
    - 🔸 **Thiên Quan Archetype** (Q4 p0268-p0271): 36 archetypes theo giờ × khắc. Tham chiếu cho section "Lập tọa Mệnh" — chủ nhân thuộc TYPE người nào.
    - 🔸 **Chiếu Đởm Kinh** (Q4 p0269-p0299): hệ thống PARALLEL với 18 Phi Tinh. Dùng làm reference song song khi luận sao Tử Vi — nếu cách cục match Chiếu Đởm Kinh, có thể trích đối chiếu.
    - 🔸 **Palace Weights** (Q4 p0276): cung nào quan trọng nhất (tier 1: Mệnh-Thân-Phúc-Quan-Tài; tier 2: Thiên Di-Phụ Mẫu-Tử Tức...). Tỷ trọng phân tích theo tier.
    - 🔸 **Phú thi Q4 corpus** (786 lines từ p0257-p0300): các quote Hán-Việt verbatim được pre-filter cho sao của Anh. PHẢI quote 2-3 câu Hán-Việt + dịch nghĩa Việt thuần.
    - 🔸 **Nhập Cốt Tiên Kinh** (Q4 p0297-p0298): 18 verdict templates 4-character (vd "phú quý song toàn", "thanh nhàn tự tại"). Dùng cho section "Kết tâm an" như câu kết tinh.
    - 🔸 **10 BƯỚC Trần Đoàn** (Q4 p0266 — methodology pháp): 10 sections của output CHÍNH LÀ 10 bước này. Tuân thủ thứ tự + ý nghĩa từng bước.

9️⃣  **KIỂM TRA CHỐNG NHẦM** — đọc lại DUMP trước khi viết section:
    - Vũ Khúc ở cung nào? (Anh KHÔNG được nói "Vũ Khúc chủ mệnh" nếu trong DUMP Vũ Khúc ở Phụ Mẫu)
    - Mệnh chủ (theo Phú Thái Vi Q.2) là sao nào? Trích chính xác.
    - Tứ Hóa năm sinh (Lộc-Quyền-Khoa-Kỵ) rơi vào sao nào, ở cung nào? Tra DUMP.

5 SECTIONS CỦA BATCH NÀY:
{sections_block}

══════════════════════════════════════════════════════════════
📤 OUTPUT JSON THUẦN (5 keys):
══════════════════════════════════════════════════════════════
- BẮT ĐẦU `{{`, KẾT THÚC `}}`. KHÔNG ``` fence.
- Mỗi value = string xuống dòng dùng \\n, quote " escape thành \\"

{{
{chr(10).join(f'  "{k}": "string 2000-4000 chữ Tiếng Việt theo cấu trúc 3 lớp"' + ("," if i < len(section_keys)-1 else "") for i, k in enumerate(section_keys))}
}}"""

        from engine.ai.council import sage_model
        resp = None
        last_err = None
        tried = []
        for cand in candidate_providers:
            current = cand
            if registry.is_unhealthy(current.name):
                continue
            tried.append(current.name)
            try:
                resp = current.chat(
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PHE_MENH_SAU},
                        {"role": "user", "content": user_prompt},
                    ],
                    # non-reasoning bắt buộc: prompt VIP cực lớn → v4-pro/M3 reasoning ăn sạch
                    # token → content rỗng (đo prod 2026-06-24). deepseek-chat tin cậy + nhanh.
                    model=sage_model(current),
                    temperature=0.5,
                    max_tokens=32000,  # 5 sections × 4000 chars VN ≈ 12k tokens; safety margin
                )
                provider = current
                break
            except Exception as e:
                err_str = str(e)
                last_err = f"{current.name}: {err_str[:200]}"
                if any(sig in err_str for sig in ["401", "403", "1113", "invalid", "Authentication", "balance", "quota"]):
                    registry.mark_unhealthy(current.name, err_str[:100])
                continue
        if resp is None:
            return None, None, 0, 0.0, last_err, tried

        content = resp.content if hasattr(resp, "content") else str(resp)
        # Strip markdown fences
        if "```" in content:
            import re as _re
            m = _re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, _re.DOTALL)
            if m:
                content = m.group(1)
            else:
                content = "\n".join(l for l in content.split("\n") if not l.strip().startswith("```"))

        parsed = None
        try:
            parsed = json.loads(content)
        except Exception:
            pass
        if parsed is None:
            try:
                start = content.find("{"); end = content.rfind("}")
                if start >= 0 and end > start:
                    parsed = json.loads(content[start:end+1])
            except Exception:
                pass
        if parsed is None:
            import re as _re
            cleaned = content.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
            cleaned = _re.sub(r",(\s*[}\]])", r"\1", cleaned)
            try:
                start = cleaned.find("{"); end = cleaned.rfind("}")
                if start >= 0 and end > start:
                    parsed = json.loads(cleaned[start:end+1])
            except Exception:
                pass
        # Attempt 4: truncation repair — extract section-by-section via regex
        if parsed is None:
            import re as _re
            parsed = {}
            # Match pattern: "key_name": "value content..." up to next "key_name": or end
            for i, key in enumerate(section_keys):
                # Look for "key_name": " ... " (greedy until next key OR end-of-content)
                next_keys = section_keys[i+1:] + ["__END__"]
                next_pattern = "|".join(f'"{k}"\\s*:' for k in next_keys)
                pat = rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*?)(?="\s*(?:,|}}|{next_pattern})|"\s*$)'
                m = _re.search(pat, content, _re.DOTALL)
                if m:
                    raw_val = m.group(1)
                    # Unescape JSON escapes
                    try:
                        unescaped = json.loads(f'"{raw_val}"')
                    except Exception:
                        unescaped = raw_val.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                    parsed[key] = unescaped
            if not parsed:
                # Last-ditch: dump raw as single key from this batch
                parsed = {section_keys[0]: content, "_parse_error_batch": batch_name}
            else:
                parsed["_partial_recovered"] = batch_name

        prompt_tokens = getattr(resp, "prompt_tokens", 0) or 0
        completion_tokens = getattr(resp, "completion_tokens", 0) or 0
        cost = getattr(resp, "cost_usd", 0) or 0
        return parsed, provider.name, prompt_tokens + completion_tokens, cost, None, tried

    def _grounded_library_context(self) -> str:
        """★ Bơm KHO ĐÃ DUYỆT vào bản luận trả phí — nguồn THẬT thay vì trí nhớ mô hình.

        Kéo đúng vật liệu cho từng phần của phê mệnh sâu:
          · sao_noi_dung (đã duyệt) → phần bài tinh thần / lập tọa mệnh
          · tu_hoa_nguon (702 rule) + phi_hoa chồng tầng → phần Tứ Hóa diễn giải
          · van_han_nguon + Thể-Dụng đại vận đang đi → phần Đại Vận / Lưu Niên
        Chỉ lấy bản founder_verified=1; không có nguồn → BỎ TRỐNG (quote-or-silence).
        """
        from engine.tu_vi import van_han as vh

        def _book(slug: str) -> str:
            """Mã kho → TÊN SÁCH người đọc hiểu (tránh lòi 'tuvifull-...' ra bản trả phí)."""
            s = (slug or "").lower()
            for key, label in (
                ("trung-chau", "Trung Châu phái Tử Vi Đẩu Số (Vương Đình Chi)"),
                ("tuong-te", "Tử Vi Đẩu Số Tường Tế"),
                ("tinh-hoa", "Tử Vi Đẩu Số Tinh Hoa Tập Thành"),
                ("tinh-thanh", "Đẩu Số Tinh Thành"),
                ("toan-thu", "Tử Vi Đẩu Số Toàn Thư"),
                ("tvdstt", "Tử Vi Đẩu Số Toàn Thư"),
                ("luan-giai-cac-chinh-tinh", "Luận Giải Các Chính Tinh"),
                ("khhb", "Tạp chí Khoa Học Huyền Bí (trước 1975)"),
            ):
                if key in s:
                    return label
            return slug or "sách cổ"

        ls = self.la_so
        out: list[str] = ["\n━━━ ★ KHO SÁCH ĐÃ DUYỆT (BẮT BUỘC LUẬN TỪ ĐÂY — có ghi nguồn) ━━━",
                          "  Quy tắc: mọi nhận định về SAO / TỨ HÓA / ĐẠI VẬN phải dựa vào các trích dẫn",
                          "  dưới đây và GHI TÊN SÁCH. Không có trích dẫn cho ý nào thì KHÔNG bịa ý đó."]

        # 1) Nội dung SAO theo đúng cung nó đóng (kho đã duyệt)
        sao_lines: list[str] = []
        for p in ls.get("palaces", [])[:12]:
            pname = p.get("name") or "?"
            stars = vh._stars_at(ls, p.get("branch_index"))
            for st in stars[:2]:
                for g in vh._grounded_sao(st, cung=pname, limit=1):
                    sao_lines.append(f"  • {st} @ {pname}: {g['dich']} (nguồn: {_book(g['nguon'])})")
        if sao_lines:
            out.append("\n── SAO × CUNG (nội dung đã duyệt, dùng cho bài tinh thần / lập tọa mệnh) ──")
            out.extend(sao_lines[:22])

        # 2) TỨ HÓA — phi tinh chồng tầng + rule trích sách
        try:
            can_nam = ls.get("year_stem")
            ph = vh.phi_hoa(ls, [("Nguyên cục", can_nam)]) if can_nam else {}
            tu_hoa_lines: list[str] = []
            for t in (ph.get("tu_hoa") or [])[:6]:
                tu_hoa_lines.append(f"  • {t['nghia']}")
                for g in (t.get("nguon") or [])[:1]:
                    tu_hoa_lines.append(f"      (nguồn: {g['rule']} — {g['nguon']})")
            for t in (ph.get("trung_phung") or [])[:4]:
                tu_hoa_lines.append(f"  • {t['loai']}: {t['sao']} @ {t['cung']} — {t['nghia']}")
                if t.get("nguyen_ly"):
                    tu_hoa_lines.append(f"      → nguyên lý: {t['nguyen_ly']}")
            nghia = vh._tu_hoa_rules(("hoa_nghia",), limit=8)
            if nghia:
                tu_hoa_lines.append("  — Nghĩa từng Hóa (trích sách phái Tứ Hóa):")
                tu_hoa_lines += [f"      · {g['rule']} ({g['nguon']})" for g in nghia]
            if tu_hoa_lines:
                out.append("\n── TỨ HÓA (dùng cho phần 'Tứ Hóa diễn giải' — TRÍCH SÁCH, không tự chế) ──")
                out.extend(tu_hoa_lines)
        except Exception:
            pass

        # 3) ĐẠI VẬN đang đi — Thể-Dụng + tam phương + nguyên tắc đọc cung theo vận
        try:
            byear = int(str(self.person.birth_datetime_local)[:4])
            import time as _t
            now_y = _t.localtime().tm_year
            bt = vh._bao_tram_dai_van(ls, byear, now_y)
            if bt and bt.get("cycle_index"):
                blk = vh.dai_van_block(ls, bt["cycle_index"])
                src = vh.block_to_source_text(blk)
                if src:
                    out.append("\n── ĐẠI VẬN ĐANG ĐI (grounded — dùng cho phần Đại Vận / Lưu Niên) ──")
                    out.append(src[:3500])
        except Exception:
            pass

        return "\n".join(out) if len(out) > 3 else ""

    def phe_menh_sau(self) -> dict:
        """Phê mệnh SÂU v2 (VIP) — 2-call split, 10 sections × 2000-4000 chars/section.

        Strategy:
        - Batch 1 (sections 1-5): định thời khắc → lập tọa mệnh
        - Batch 2 (sections 6-10): đại vận → kết tâm an
        - Each call: max_tokens=16000, ~25-50k chars VN per batch
        - Full la_so dump fed into both calls (LLM thấy chính xác sao ở cung nào)

        ⚠️ Endpoint caller PHẢI check VIP permission TRƯỚC khi gọi.
        """
        cached = None if self.force else _cache_load(self.person.person_key, "phe_menh_sau", self.person.user_id)
        if cached:
            return cached

        # VIP chain: prefer DeepSeek (quality), fallback chain if unhealthy
        from engine.ai.registry import get_registry
        registry = get_registry()
        provider_chain = ["deepseek", "anthropic", "gemini", "openrouter", "minimax"]
        candidate_providers = []
        for name in provider_chain:
            try:
                p = registry.get(name)
                if p and p.is_configured and not registry.is_unhealthy(name):
                    candidate_providers.append(p)
            except Exception:
                pass
        if not candidate_providers:
            return {"status": "error", "message": "No LLM provider configured (all unhealthy or missing keys)"}

        # Build full la-số dump (LLM thấy chính xác sao ở cung nào — tránh bịa)
        ctx_parts = [_chart_full_dump(self.person, self.la_so)]

        # Enrich with cách cục matches
        try:
            cach_data = self.discover_cach_cuc()
            cachs = cach_data.get("cach_cucs", [])[:10]
            if cachs:
                ctx_parts.append("\n━━━ CÁCH CỤC ĐÃ MATCH (top 10) ━━━")
                for c in cachs:
                    y_nghia = (c.get('y_nghia') or '')[:300]
                    ctx_parts.append(f"  • {c.get('ten')} ({c.get('cap_do', '')}): {y_nghia}")
        except Exception:
            pass

        # Case studies (nét giống lịch sử)
        try:
            from engine.tu_vi.case_matcher import match_cases
            cases = match_cases(self.la_so, top_n=3)
            if cases.get("matches"):
                ctx_parts.append("\n━━━ NÉT GIỐNG LỊCH SỬ Q3+Q4 (top 3) ━━━")
                for m in cases["matches"]:
                    ctx_parts.append(f"  • {m['pattern_name']} ({m.get('polarity', '?')}): {m.get('lesson_short', '')[:300]}")
        except Exception:
            pass

        # Psych safety patterns
        try:
            from engine.tu_vi.psychological_safety import detect_safety_patterns
            from core.chronos import calculate_chronos_state
            chronos = calculate_chronos_state(self.person.birth_datetime_local, self.person.timezone)
            year_stem = chronos.ganzhi.year.split()[0]
            safety = detect_safety_patterns(self.la_so, year_stem)
            if safety:
                ctx_parts.append("\n━━━ SAFETY PATTERNS (Q3 p0186) ━━━")
                for p in safety:
                    ctx_parts.append(f"  • {p['title']}: {p['gentle_message'][:300]}")
        except Exception:
            pass

        # Chart strength
        try:
            from engine.tu_vi.mieu_vuong_ham import chart_strength
            cs = chart_strength(self.la_so)
            ctx_parts.append(f"\n━━━ SỨC MẠNH TỔNG THỂ (Q2 p0102) ━━━")
            ctx_parts.append(f"  Weighted total: {cs.get('weighted_total_score')} ({cs.get('verdict', '?')})")
        except Exception:
            pass

        # ═══════════════════════════════════════════════════════════
        # Q4 ENRICHMENT — Chiếu Đởm Kinh, Thiên Quan, 10 bước, etc.
        # ═══════════════════════════════════════════════════════════

        # Q4 — Thiên Quan 36 archetypes (theo giờ × khắc)
        try:
            from engine.tu_vi.thien_quan_typology import get_archetype
            hour = self.la_so.get('hour_branch', '')
            # Khắc: thượng/trung/hạ (anh sinh 23:30 = Tý thượng khắc, 11:00 = Ngọ thượng v.v.)
            # Đơn giản: dùng minute để chia
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(self.person.birth_datetime_local)
                minute = dt.hour * 60 + dt.minute
                # Giờ Tý 23-01, 2 giờ × 60 = 120 phút. Chia 3 khắc:
                # Đơn giản hóa: chỉ dùng minute trong giờ hiện tại
                m_in_hour = dt.minute
                if m_in_hour < 20:
                    khac = "thuong"
                elif m_in_hour < 40:
                    khac = "trung"
                else:
                    khac = "ha"
            except Exception:
                khac = "thuong"
            arch = get_archetype(hour, khac)
            if arch:
                ctx_parts.append(f"\n━━━ THIÊN QUAN ARCHETYPE (Q4 p0268-p0271) ━━━")
                ctx_parts.append(f"  Giờ {hour} - khắc {khac}: {arch.get('name_vi', '?')}")
                ctx_parts.append(f"  Tính cách: {(arch.get('tinh_cach') or '')[:300]}")
                ctx_parts.append(f"  Vận mệnh tổng: {(arch.get('van_menh_tong') or '')[:400]}")
        except Exception as e:
            pass

        # Q4 — Chiếu Đởm Kinh (parallel system)
        try:
            from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
            from core.chronos import calculate_chronos_state
            chronos = calculate_chronos_state(self.person.birth_datetime_local, self.person.timezone)
            ys, yb = chronos.ganzhi.year.split()
            cdk = cast_chieu_dom_kinh(
                year_stem=ys,
                year_branch=yb,
                lunar_month=self.la_so.get('lunar_month', 1),
                hour_branch=self.la_so.get('hour_branch', 'Tý'),
                gender=self.person.gender,
            )
            if cdk and cdk.get('stars'):
                ctx_parts.append(f"\n━━━ CHIẾU ĐỞM KINH (Q4 p0269-p0299 — parallel system) ━━━")
                ctx_parts.append(f"  Mệnh CĐK: cung {cdk.get('menh_branch', '?')} (khác Tử Vi: {self.la_so['menh_branch']})")
                stars_str = ", ".join(f"{s}={b}" for s, b in list(cdk['stars'].items())[:10])
                ctx_parts.append(f"  10 Phi Tinh đầu: {stars_str}")
        except Exception:
            pass

        # Q4 — Palace weights (tiers)
        try:
            import json as _json
            with open('/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi/palace_weights.json') as f:
                pw = _json.load(f)
            tiers = pw.get('tiers', {})
            ctx_parts.append(f"\n━━━ TRỌNG SỐ CUNG (Q4 p0276 — 7 tiers) ━━━")
            for tier_name, palaces in list(tiers.items())[:5]:
                if isinstance(palaces, list):
                    ctx_parts.append(f"  {tier_name}: {', '.join(palaces)}")
                elif isinstance(palaces, dict):
                    ps = palaces.get('palaces', palaces.get('cung', []))
                    if ps:
                        ctx_parts.append(f"  {tier_name}: {', '.join(ps)}")
        except Exception:
            pass

        # Q4 — Phú thi corpus (top 3 lines related to user stars)
        try:
            import json as _json
            with open('/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi/q4_phu_thi_corpus.json') as f:
                phu = _json.load(f)
            lines = phu.get('lines', [])
            # Filter lines mentioning user's key stars
            user_stars = set(list(self.la_so.get('chinh_tinh', {}).keys())[:8])
            matched = []
            for ln in lines:
                txt = ln.get('hv', '') or ln.get('text_hv', '') or str(ln)
                if any(s in txt for s in user_stars):
                    matched.append(ln)
                    if len(matched) >= 5:
                        break
            if matched:
                ctx_parts.append(f"\n━━━ PHÚ THI Q4 LIÊN QUAN (top 5) ━━━")
                for ln in matched:
                    hv = ln.get('hv', '') or ln.get('text_hv', '')[:120]
                    nghia = (ln.get('nghia', '') or ln.get('y_nghia', ''))[:150]
                    ctx_parts.append(f"  • \"{hv}\" — {nghia}")
        except Exception:
            pass

        # Q4 — Nhập Cốt Tiên Kinh tổng đoán (18 verdicts)
        try:
            import json as _json
            with open('/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi/nhap_cot_tien_kinh_tong_doan.json') as f:
                nck = _json.load(f)
            verdicts = nck.get('verdicts', nck.get('tong_doan', []))
            if isinstance(verdicts, list) and verdicts:
                ctx_parts.append(f"\n━━━ NHẬP CỐT TIÊN KINH (Q4 p0297-p0298) — verdict templates ━━━")
                ctx_parts.append(f"  {len(verdicts)} 4-character verdicts có sẵn (vd: {verdicts[0].get('verdict', verdicts[0]) if isinstance(verdicts[0], dict) else verdicts[0]})")
        except Exception:
            pass

        # Q4 — 10 bước Trần Đoàn methodology header
        try:
            import json as _json
            with open('/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi/10_buoc_luan.json') as f:
                muoi_buoc = _json.load(f)
            steps = muoi_buoc.get('steps', muoi_buoc.get('buoc', []))
            if steps:
                ctx_parts.append(f"\n━━━ 10 BƯỚC TRẦN ĐOÀN (Q4 p0266 — methodology pháp) ━━━")
                quote_hv = muoi_buoc.get('source_quote_hv', '')[:150]
                if quote_hv:
                    ctx_parts.append(f"  Quote: \"{quote_hv}\"")
        except Exception:
            pass

        # ⚠️ EMPHASIZE Mệnh chủ — anh complain LLM hay nhầm
        ctx_parts.append(f"\n━━━ ⚠️ NHẮC LẠI QUAN TRỌNG ━━━")
        ctx_parts.append(f"  • Mệnh chủ (sao chủ mệnh đời) = **{self.la_so.get('menh_chu', '?')}** — KHÔNG phải sao gì khác.")
        ctx_parts.append(f"  • Thân chủ (sao chủ hành động) = **{self.la_so.get('than_chu', '?')}**")
        ctx_parts.append(f"  • Đẩu Quân (sao chủ duyên phận) tại cung = **{self.la_so.get('dau_quan_branch', '?')}**")
        ctx_parts.append(f"  ⚠️ Tham khảo Phú Thái Vi Q.2 chuẩn TQ — KHÔNG dùng bảng Mệnh chủ VN (bị sai).")

        # 🔑 TRUNG CHÂU PARADIGM Q2 (2026-06-08) — sau 32 vòng thâm nhuần
        # Inject 3 Iron Rules + paradigm chính tinh × cung khớp lá số này
        try:
            from .trung_chau_paradigm import build_trung_chau_context
            tc_ctx = build_trung_chau_context(self.la_so, gender=self.la_so.get("gender", "nam"))
            if tc_ctx:
                ctx_parts.append("\n" + tc_ctx)
        except Exception:
            pass

        # ★ KHO ĐÃ DUYỆT — bơm nguồn THẬT vào bản trả phí (Anh 2026-07-31: "nâng cấp bao
        # nhiêu vòng kho thư viện rồi"). Trước đây bản 99 xu KHÔNG dùng một chữ nào từ
        # tu_hoa_nguon (702 rule) / sao_noi_dung (2030) / van_han_nguon (55) → phần Tứ Hóa,
        # Đại Vận viết bằng trí nhớ mô hình. Nay ép LLM luận TỪ NGUỒN (quote-or-silence).
        try:
            g = self._grounded_library_context()
            if g:
                ctx_parts.append(g)
        except Exception:
            pass

        base_ctx = "\n".join(ctx_parts)

        # === BATCH 1 (sections 1-5) ===
        b1, prov1, tok1, cost1, err1, tried1 = self._phe_menh_sau_batch_call(
            batch_name="1/2 (sections 1-5: Định thời khắc → Lập tọa mệnh)",
            sections=self._PHE_MENH_SAU_BATCH_1,
            base_ctx=base_ctx,
            provider=candidate_providers[0],
            registry=registry,
            candidate_providers=candidate_providers,
        )
        if b1 is None:
            return {
                "status": "error",
                "message": f"Batch 1 failed. Tried: {tried1}. Last: {err1}",
                "providers_tried": tried1,
                "batch_failed": 1,
            }

        # === BATCH 2 (sections 6-10) ===
        # Pass result of batch 1 as additional context (LLM tránh lặp)
        b1_summary = "\n".join(
            f"  [{k}] đã viết xong, ~{len(v) if isinstance(v, str) else '?'} chars"
            for k, v in b1.items() if not k.startswith("_")
        )
        ctx_for_b2 = base_ctx + f"\n\n━━━ BATCH 1 ĐÃ HOÀN THÀNH (KHÔNG LẶP LẠI) ━━━\n{b1_summary}\n"

        # Re-fetch candidate list (some might have been marked unhealthy in batch 1)
        candidate_providers_b2 = []
        for name in provider_chain:
            try:
                p = registry.get(name)
                if p and p.is_configured and not registry.is_unhealthy(name):
                    candidate_providers_b2.append(p)
            except Exception:
                pass
        if not candidate_providers_b2:
            # Try to recover with what worked in batch 1
            candidate_providers_b2 = [p for p in candidate_providers if p.name == prov1]

        b2, prov2, tok2, cost2, err2, tried2 = self._phe_menh_sau_batch_call(
            batch_name="2/2 (sections 6-10: Đại Vận → Kết tâm an)",
            sections=self._PHE_MENH_SAU_BATCH_2,
            base_ctx=ctx_for_b2,
            provider=candidate_providers_b2[0] if candidate_providers_b2 else candidate_providers[0],
            registry=registry,
            candidate_providers=candidate_providers_b2 or candidate_providers,
        )
        if b2 is None:
            # Salvage: return batch 1 alone
            phe = b1
            phe["_batch_2_failed"] = True
            phe["_batch_2_error"] = err2
        else:
            phe = {**b1, **b2}

        # Compute totals
        provider_name = f"{prov1}+{prov2}" if prov2 and prov2 != prov1 else (prov1 or "unknown")
        total_tokens = tok1 + tok2
        total_cost = cost1 + cost2

        # Length stats per section
        section_lengths = {}
        for k, v in phe.items():
            if k.startswith("_"):
                continue
            section_lengths[k] = len(v) if isinstance(v, str) else 0
        avg_len = sum(section_lengths.values()) // max(1, len(section_lengths))

        data = {
            "status": "ok",
            "tier": "vip1",
            "version": "v2",
            "person_key": self.person.person_key,
            "person_name": self.person.name,
            "generated_at": int(time.time()),
            "provider": provider_name,
            "model": "pro_tier_split_2call",
            "cost_usd": round(total_cost, 6),
            "tokens": {"total": total_tokens, "batch_1": tok1, "batch_2": tok2},
            "section_lengths": section_lengths,
            "avg_length_chars": avg_len,
            "phe_menh_sau": phe,
            "paradigm_note": "Phê mệnh SÂU v2 — 2-call split, 10 sections × 2000-4000 chars. "
                              "10 BƯỚC Trần Đoàn (Q4 p0266) + paradigm 'bất khả chấp nhất' (Q4 p0299). "
                              "Iron Rule #6: đọc đồng dạng, không predict.",
        }
        _cache_save(self.person.person_key, "phe_menh_sau", data, self.person.user_id)

        # AUTO-EXTRACT to wiki (post-gen hook) — anh đốt tiền DeepSeek = tích lũy tri thức
        try:
            from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki
            extract_result = extract_phe_menh_to_wiki(data, verbose=False)
            data["wiki_extracted"] = extract_result
        except Exception as e:
            data["wiki_extracted"] = {"error": str(e)}

        return data

    # ── 7. Phú readings (top N personalized) ────────────────────────────────

    SYSTEM_PHU_READ = """Bạn là chuyên gia Tử Vi đọc sâu Phú Thái Vi áp dụng vào lá số CỤ THỂ.

Cho 1 câu Phú + LÁ SỐ. Viết 3-5 câu đọc sâu áp dụng vào lá số đó.

Output JSON: {"reading": "..."}"""

    def phu_reading(self, top_n: int = 5) -> dict:
        cached = None if self.force else _cache_load(self.person.person_key, f"phu_reading_top{top_n}", self.person.user_id)
        if cached:
            return cached

        matches_data = self.phu_match()
        matches = matches_data.get('matched_passages', [])[:top_n]
        if not matches:
            return {"readings": [], "cost_usd": 0}

        from engine.yi_publishing.translator import get_deepseek_client
        client = get_deepseek_client()
        readings = []
        total_cost = 0
        ctx = self.chart_summary

        for item in matches:
            p = item['passage']
            user_p = f"""{ctx}

CÂU PHÚ:
  音: {p['hanviet']}
  義: {p['luangiai']}
  解: {p.get('giaithichdande', '')}

Reasons match: {' · '.join(item.get('reasons', []))}

Viết đọc sâu áp dụng vào lá số."""

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PHU_READ},
                    {"role": "user", "content": user_p},
                ],
                response_format={"type": "json_object"}, timeout=90, max_tokens=2000,
            )
            u = resp.usage
            cost = (u.prompt_tokens * 0.27 + u.completion_tokens * 1.10) / 1_000_000
            total_cost += cost
            try:
                reading = json.loads(resp.choices[0].message.content).get('reading', '')
            except Exception:
                reading = ''
            readings.append({**p, "score": item['score'], "reasons": item['reasons'], "reading_for_person": reading})

        data = {
            "person_key": self.person.person_key,
            "top_n": top_n,
            "generated_at": int(time.time()),
            "cost_usd": round(total_cost, 6),
            "readings": readings,
        }
        _cache_save(self.person.person_key, f"phu_reading_top{top_n}", data, self.person.user_id)
        return data

    # ── 8. Run all analyses ─────────────────────────────────────────────────

    def run_all(
        self,
        synastry_with: Optional["TuViAnalyzer"] = None,
        luu_nien_years: tuple[int, int] = (2026, 2030),
        luu_nguyet_year: int = 2026,
        phu_top_n: int = 5,
    ) -> dict:
        """Run all 6 analyses + return summary."""
        results = {
            "person": self.person.person_key,
            "started_at": int(time.time()),
            "stages": {},
        }
        for kind, func in [
            ("cach_cuc",  lambda: self.discover_cach_cuc()),
            ("dai_van",   lambda: self.dai_van_annotate()),
            ("luu_nien",  lambda: self.luu_nien(*luu_nien_years)),
            ("luu_nguyet",lambda: self.luu_nguyet(luu_nguyet_year)),
            ("phu_match", lambda: self.phu_match()),
            ("cung_reading", lambda: self.cung_reading()),
            ("phu_reading", lambda: self.phu_reading(phu_top_n)),
        ]:
            t0 = time.time()
            try:
                r = func()
                results['stages'][kind] = {
                    "ok": True,
                    "elapsed_seconds": round(time.time() - t0, 1),
                    "cost_usd": r.get('cost_usd', 0),
                }
            except Exception as e:
                logger.exception(f"Analysis {kind} failed for {self.person.person_key}")
                results['stages'][kind] = {"ok": False, "error": str(e)}

        if synastry_with:
            t0 = time.time()
            try:
                r = self.synastry(synastry_with)
                results['stages'][f"synastry_{synastry_with.person.person_key}"] = {
                    "ok": True,
                    "elapsed_seconds": round(time.time() - t0, 1),
                    "cost_usd": r.get('cost_usd', 0),
                }
            except Exception as e:
                logger.exception("Synastry failed")
                results['stages'][f"synastry_{synastry_with.person.person_key}"] = {
                    "ok": False, "error": str(e),
                }

        results['finished_at'] = int(time.time())
        results['total_cost_usd'] = round(
            sum(s.get('cost_usd', 0) for s in results['stages'].values()), 6,
        )
        return results
