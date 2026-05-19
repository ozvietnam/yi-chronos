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
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _cache_dir(person_key: str) -> Path:
    d = CACHE_ROOT / person_key
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_load(person_key: str, kind: str) -> Optional[dict]:
    f = _cache_dir(person_key) / f"{kind}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def _cache_save(person_key: str, kind: str, data: dict) -> Path:
    f = _cache_dir(person_key) / f"{kind}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return f


def _cast_chart(birth: str, gender: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Cast Tử Vi lá số — uses core.chronos for lunar conversion (same as API /tu-vi/cast)."""
    from .an_sao import cast_la_so
    from core.chronos import calculate_chronos_state
    from datetime import datetime as _dt

    chronos = calculate_chronos_state(birth, timezone)
    d_str, m_str, _y = chronos.almanac.lunar_date.split("/")
    lunar_month = int(m_str)
    lunar_day = int(d_str)
    local_dt = _dt.fromisoformat(birth)
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
        cached = None if self.force else _cache_load(self.person.person_key, "cach_cuc")
        if cached:
            return cached

        from engine.yi_publishing.translator import get_deepseek_client
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
        try:
            cach_cucs = json.loads(resp.choices[0].message.content)['cach_cucs']
        except Exception as e:
            logger.warning(f"cach_cuc parse fail: {e}")
            cach_cucs = []

        data = {
            "person_key": self.person.person_key,
            "person_name": self.person.name,
            "generated_at": int(time.time()),
            "cost_usd": round(cost, 6),
            "cach_cucs": cach_cucs,
        }
        _cache_save(self.person.person_key, "cach_cuc", data)
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
        cached = None if self.force else _cache_load(self.person.person_key, key)
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
        _cache_save(self.person.person_key, key, data)
        return data

    # ── 3. Đại Vận annotations ──────────────────────────────────────────────

    SYSTEM_DV = """Bạn là chuyên gia Tử Vi Đẩu Số viết phân tích Đại Vận (10 năm).

Output JSON: {
  "tong_quan": "<60-90 từ>",
  "co_hoi": [...] (3),
  "thach_thuc": [...] (3),
  "loi_khuyen": "<50-80 từ>"
}"""

    def dai_van_annotate(self) -> dict:
        cached = None if self.force else _cache_load(self.person.person_key, "dai_van")
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
        _cache_save(self.person.person_key, "dai_van", data)
        return data

    # ── 4. Lưu Niên (5 years window) ────────────────────────────────────────

    SYSTEM_LN = """Bạn là chuyên gia Tử Vi Đẩu Số viết LƯU NIÊN (vận năm).

Output JSON: {
  "chu_de": "<1 câu>",
  "tong_quan": "<60-90 từ>",
  "linh_vuc_quan_tam": [...],
  "thoi_diem_can_chu_y": [...],
  "loi_khuyen": "<60-80 từ>",
  "cat_hung_overall": "cát đa số / cát hung lẫn / cảnh báo"
}"""

    def luu_nien(self, start_year: int, end_year: int) -> dict:
        cache_key = f"luu_nien_{start_year}_{end_year}"
        cached = None if self.force else _cache_load(self.person.person_key, cache_key)
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
        _cache_save(self.person.person_key, cache_key, data)
        return data

    # ── 5. Lưu Nguyệt (12 tháng âm 1 năm) ───────────────────────────────────

    SYSTEM_LNG = """Bạn là chuyên gia Tử Vi viết LƯU NGUYỆT (vận tháng).

Output JSON: {
  "chu_de": "<1 câu>",
  "tinh_chat": "<60-80 từ>",
  "viec_lam": [...] (2-3),
  "viec_tranh": [...] (2-3),
  "cat_hung": "cát / cát hung lẫn / cảnh báo"
}"""

    def luu_nguyet(self, year: int) -> dict:
        cache_key = f"luu_nguyet_{year}"
        cached = None if self.force else _cache_load(self.person.person_key, cache_key)
        if cached:
            return cached

        from .an_sao import tieu_han_for_age
        ls = self.la_so
        birth_year = int(self.person.birth_datetime_local[:4])
        age = year - birth_year + 1
        th_idx = tieu_han_for_age(ls['year_branch'], self.person.gender, age)

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

        # Solar month range — rough estimate for year 2026 (recalc per year in real)
        # For simplicity store branch + palace + stars; UI maps to solar dates
        for thang in range(1, 13):
            br_idx = (th_idx + (thang - 1)) % 12
            br = BRANCHES[br_idx]
            palace = branch_to_palace.get(br, '?')
            stars = branch_to_stars.get(br, [])

            user_p = f"""{ctx}

NĂM {year}, THÁNG {thang} ÂM:
- Tiểu Hạn năm: {BRANCHES[th_idx]}
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
        _cache_save(self.person.person_key, cache_key, data)
        return data

    # ── 6. Phú Thái Vi match ────────────────────────────────────────────────

    def phu_match(self) -> dict:
        """Score all Phú Thái Vi passages by relevance to chart."""
        cached = None if self.force else _cache_load(self.person.person_key, "phu_match")
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
        _cache_save(self.person.person_key, "phu_match", data)
        return data

    # ── 7. Phú readings (top N personalized) ────────────────────────────────

    SYSTEM_PHU_READ = """Bạn là chuyên gia Tử Vi đọc sâu Phú Thái Vi áp dụng vào lá số CỤ THỂ.

Cho 1 câu Phú + LÁ SỐ. Viết 3-5 câu đọc sâu áp dụng vào lá số đó.

Output JSON: {"reading": "..."}"""

    def phu_reading(self, top_n: int = 5) -> dict:
        cached = None if self.force else _cache_load(self.person.person_key, f"phu_reading_top{top_n}")
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
        _cache_save(self.person.person_key, f"phu_reading_top{top_n}", data)
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
