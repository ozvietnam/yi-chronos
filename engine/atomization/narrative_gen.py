"""Narrative generator — Lớp 1 "Chuyện về anh" bằng LLM thay template cứng.

Input: output của render_3_layer (warnings + cross-school atoms).
Output: narrative Việt thuần ~400-600 chữ, cá nhân hóa, IRON RULE #6 enforced.

Cost-aware: DeepSeek chat (~$0.003/call) + cache SQLite theo hash lá số —
cùng lá số chỉ gọi LLM 1 lần.

Built 2026-06-10 (Anh chọn option 2).
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

# Iron Rule #6: Tử Vi = đọc đồng dạng, KHÔNG predict cứng
SYSTEM_PROMPT = """Bạn là người kể chuyện lá số Tử Vi theo trường phái "đọc đồng dạng" của Trần Đoàn.

NGUYÊN TẮC SẮT (vi phạm = output bị loại):
1. KHÔNG tiên tri: cấm "anh sẽ giàu/nghèo/thành công/thất bại", cấm "năm X sẽ xảy ra Y".
2. Dùng giọng PHẢN CHIẾU: "lá số phản chiếu...", "cấu trúc này thường thấy ở người...", "sách cổ ghi nhận xu hướng...".
3. Mệnh chỉ chi phối 7 phần, 3 phần do người — luôn chừa cửa cho nỗ lực cá nhân.
4. CHỈ dùng dữ kiện được cung cấp (warnings + trích sách) — KHÔNG bịa thêm sao, cung, hay luận đoán ngoài input.
5. Khi các hệ phái nói khác nhau, nêu cả hai góc nhìn thay vì chọn một.

VĂN PHONG: Việt thuần ấm áp, xưng "anh/chị" theo giới tính, 400-600 chữ, 3-4 đoạn.
Đoạn 1: bậc tuổi + cấu trúc nền (Can-Chi, 3 vòng). Đoạn 2-3: nét nổi bật nhất từ các sao chính
(dựa trích sách). Đoạn cuối: cảnh báo paradigm nếu có (Nhân Cung...) + lời nhắc 7/3."""


def _laso_cache_key(la_so_input: dict) -> str:
    """Hash lá số input → cache key ổn định."""
    core = {
        "can": la_so_input.get("can"),
        "chi": la_so_input.get("chi"),
        "menh": la_so_input.get("menh_palace"),
        "than": la_so_input.get("than_palace"),
        "cuc": la_so_input.get("cuc"),
        "gender": la_so_input.get("gender"),
        "ct": la_so_input.get("chinh_tinh_per_palace"),
    }
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _ensure_cache_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS narrative_cache (
            cache_key TEXT PRIMARY KEY,
            narrative TEXT NOT NULL,
            model TEXT,
            created_at INTEGER NOT NULL
        )
    """)


def _compose_user_prompt(three_layer: dict, la_so_input: dict) -> str:
    """Compose prompt từ render_3_layer output — chỉ feed dữ kiện thật."""
    from engine.tu_vi.viet_names import vi_can, vi_chi, vi_star, vi_palace

    gender_vi = "nam" if la_so_input.get("gender") == "M" else "nữ"
    parts = [
        f"## Lá số: năm {vi_can(la_so_input['can'])} {vi_chi(la_so_input['chi'])}, "
        f"giới tính {gender_vi}, Mệnh tại {vi_chi(la_so_input['menh_palace'])}, "
        f"Thân tại {vi_chi(la_so_input['than_palace'])}",
        "",
        "## Dữ kiện paradigm (engine tính):",
    ]
    for w in three_layer.get("warnings", []):
        parts.append(f"- [{w['type']}] {w['msg']}")

    parts.append("")
    parts.append("## Trích sách theo sao × cung (chọn lọc, tối đa 2/sao):")
    count = 0
    for palace, pdata in (three_layer.get("lop_3_sach_co", {}).get("per_palace") or {}).items():
        # Chỉ lấy palace chức năng quan trọng (menh, tai_bach, quan_loc, phu_the, phuc_duc)
        if palace not in ("menh", "tai_bach", "quan_loc", "phu_the", "phuc_duc", "thien_di"):
            continue
        for star, cv in pdata.get("cross_views", {}).items():
            shown = 0
            for school, atoms in cv.get("schools", {}).items():
                for a in atoms[:1]:  # 1 atom / school
                    if shown >= 2 or count >= 18:
                        break
                    vt = a.get("viet_thuan") or ""
                    if vt:
                        parts.append(
                            f"- {vi_star(star)} × {vi_palace(palace)} ({school}): {vt[:200]}"
                        )
                        shown += 1
                        count += 1

    # Tổ hợp cung Mệnh (tam phương tứ chính / giáp / mượn sao) — chống luận máy móc
    menh_chi = la_so_input.get("menh_palace")
    th = (three_layer.get("lop_3_sach_co", {}).get("to_hop_per_palace") or {}).get(menh_chi)
    if th and th.get("total_atoms"):
        t = th["to_hop"]
        parts.append("")
        parts.append(
            f"## Tổ hợp cung Mệnh (tam phương tứ chính: "
            f"{', '.join(vi_chi(c) for c in t['tu_chinh']['tu_chinh'])}):"
        )
        if t["muon_sao"]["vo_chinh_dieu"] and t["muon_sao"]["borrowed_from"]:
            parts.append(
                f"- Mệnh vô chính diệu, mượn sao từ {vi_chi(t['muon_sao']['borrowed_from'])}: "
                f"{', '.join(vi_star(s) for s in t['muon_sao']['stars'])}"
            )
        shown_th = 0
        for school, atoms in th.get("schools", {}).items():
            for a in atoms[:1]:
                if shown_th >= 4:
                    break
                vt = a.get("viet_thuan") or a.get("source_quote") or ""
                if vt:
                    parts.append(f"- ({school}, {'/'.join(a.get('relations', []))}): {vt[:200]}")
                    shown_th += 1

    parts.append("")
    parts.append("Viết narrative 'Chuyện về anh/chị' theo nguyên tắc đã cho.")
    return "\n".join(parts)


def generate_narrative(three_layer: dict, la_so_input: dict, force: bool = False) -> dict:
    """Generate (hoặc lấy cache) narrative Lớp 1.

    Returns: {narrative, cached, model}
    """
    cache_key = _laso_cache_key(la_so_input)

    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_cache_table(conn)
        if not force:
            row = conn.execute(
                "SELECT narrative, model FROM narrative_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
            if row:
                return {"narrative": row[0], "cached": True, "model": row[1]}

        # LLM call — multi-provider fallback (cost-aware chain, key nào sống dùng key đó)
        from engine.ai.registry import get_registry

        registry = get_registry()
        provider = registry.first_configured(
            ["minimax", "gemini", "openrouter", "anthropic", "deepseek"]
        )
        user_prompt = _compose_user_prompt(three_layer, la_so_input)
        resp = provider.chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            # Reasoning models (MiniMax-M2) tiêu tokens cho <think> trước khi trả lời
            # → phải cho trần cao, nếu không đáp án bị cắt rỗng.
            max_tokens=4000,
        )
        narrative = (resp.content or "").strip()
        model = f"{resp.provider}:{resp.model}"
        if not narrative:
            raise RuntimeError(
                f"LLM {model} trả về rỗng (reasoning tokens cạn?) — không cache"
            )

        conn.execute(
            "INSERT OR REPLACE INTO narrative_cache (cache_key, narrative, model, created_at) VALUES (?, ?, ?, ?)",
            (cache_key, narrative, model, int(time.time())),
        )
        conn.commit()
        return {"narrative": narrative, "cached": False, "model": model}
    finally:
        conn.close()
