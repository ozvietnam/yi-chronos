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
SYSTEM_PROMPT = """Bạn là một thầy Tử Vi giỏi, hiểu người — luận theo trường phái "đọc đồng dạng"
của Trần Đoàn. Người đối diện vừa ngồi xuống, bạn nhìn lá số và NÓI TRÚNG TÂM CAN họ.

MỤC TIÊU bài này (món khai vị — TÍNH CÁCH & CON NGƯỜI):
Không kể cấu trúc lá số (đừng mở đầu bằng "bậc tuổi", "Can-Chi", "3 vòng" — đó là việc hậu trường).
Hãy vẽ chân dung CON NGƯỜI thật, để họ đọc xong gật gù "đúng là mình".

NGUYÊN TẮC SẮT (vi phạm = loại):
1. KHÔNG tiên tri: cấm "anh sẽ giàu/nghèo/thành/bại", cấm "năm X xảy ra Y".
2. Giọng PHẢN CHIẾU: "anh là người...", "trong anh có...", "cách anh thường..." — nói về BẢN CHẤT đang là, không đoán tương lai.
3. Mệnh 7 phần, người 3 phần — điểm yếu là chỗ để rèn, không phải bản án.
4. CHỈ dùng dữ kiện cho sẵn (sao + trích sách + Ngũ Uẩn) — KHÔNG bịa sao/cung.
5. Hệ phái khác nhau → nêu cả hai góc.

CẤU TRÚC bài (Việt thuần, ấm, xưng anh/chị, ~500-650 chữ, KHÔNG tiêu đề mục):
• Mở (2-3 câu): CHỐT TÍNH CÁCH CHỦ ĐẠO — anh là mẫu người nào? Bắt từ chính tinh Mệnh +
  Thân + Ngũ Uẩn. Nói thẳng, sống động, như điểm trúng huyệt.
• KHEN (1 đoạn): 2-3 điểm mạnh thật của anh trong đối nhân xử thế + nội lực — cụ thể, có dẫn từ sao.
• CHÊ / NHẮC (1 đoạn): 1-2 điểm yếu trong cách sống, ứng xử — nói THẲNG mà THƯƠNG, kiểu người
  hiểu mình mới dám nói. Bắt từ sát tinh / bộ hung / mặt lệch của Ngũ Uẩn.
• NÉT RIÊNG + MÓN HỢP GU (1 đoạn): cái làm anh KHÁC người (cách cục/tổ hợp nổi bật); rồi điểm
  2-3 "món khoái khẩu" — điều HỢP với tính cách này: kiểu việc/môi trường/cách sống/kiểu người
  hợp gu anh. Khung "tính cách như anh thường hợp với...", KHÔNG hứa hẹn kết quả.
• Kết (1 câu): nhắc nhẹ 7 phần mệnh, 3 phần do anh nắm.

LƯU Ý: viết ĐÚNG CHÍNH TẢ tiếng Việt, có dấu chuẩn. Mỗi lá số một con người riêng —
KHÔNG dùng câu khuôn mẫu; phải bám đúng sao của lá số này."""


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
        # Đại vận đổi → narrative phải viết lại (BIẾN)
        "dv": (la_so_input.get("dai_van_hien_tai") or {}).get("cycle_index"),
        "pv": "khaivi-v2",  # prompt version — đổi prompt thì bài cache cũ tự bỏ
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
    nam_duong = la_so_input.get("birth_year")
    nam_str = f"năm sinh dương lịch {nam_duong} " if nam_duong else ""
    parts = [
        f"## Lá số: {nam_str}(âm lịch {vi_can(la_so_input['can'])} {vi_chi(la_so_input['chi'])}), "
        f"giới tính {gender_vi}, Mệnh tại {vi_chi(la_so_input['menh_palace'])}, "
        f"Thân tại {vi_chi(la_so_input['than_palace'])}",
        "⚠ CHỈ dùng các số liệu cho sẵn ở đây. TUYỆT ĐỐI không tự suy/đổi năm "
        "dương lịch, không bịa tuổi, không thêm sao/cung ngoài danh sách dưới.",
        "",
        "## Dữ kiện paradigm (engine tính):",
    ]
    for w in three_layer.get("warnings", []):
        parts.append(f"- [{w['type']}] {w['msg']}")

    # Trạng thái miếu-hãm từng chính tinh (Việc 2)
    star_levels = three_layer.get("star_levels") or {}
    if star_levels:
        parts.append("")
        parts.append("## Trạng thái miếu-hãm (đối chiếu bảng — chỉ luận theo trạng thái THẬT này):")
        for s, info in star_levels.items():
            parts.append(f"- {vi_star(s)}: {info['level']} (tại {vi_chi(info['palace_chi'])})")

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
                    if a.get("dieu_kien_khop") is False:
                        continue  # atom lệch điều kiện miếu-hãm — không feed LLM
                    vt = a.get("viet_thuan") or ""
                    if vt:
                        parts.append(
                            f"- {vi_star(star)} × {vi_palace(palace)} ({school}): {vt[:200]}"
                        )
                        shown += 1
                        count += 1

    # Tứ Hóa — trục động của lá số (Lộc/Quyền/Khoa/Kỵ đóng cung nào)
    tu_hoa = la_so_input.get("tu_hoa") or []
    if tu_hoa:
        HOA_VI = {"hoa_loc": "Hóa Lộc", "hoa_quyen": "Hóa Quyền",
                  "hoa_khoa": "Hóa Khoa", "hoa_ky": "Hóa Kỵ"}
        parts.append("")
        parts.append("## Tứ Hóa (năm sinh):")
        for t in tu_hoa:
            fn = t.get("palace_fn")
            pal_vi = vi_palace(fn) if fn else vi_chi(t.get("palace_chi", ""))
            parts.append(
                f"- {HOA_VI.get(t['hoa'], t['hoa'])}: {vi_star(t['star'])} "
                f"tại cung {pal_vi}"
            )

    # Bộ phụ tinh + THẾ tại cung Mệnh (đồng/giáp/hội/xung chiếu)
    menh_chi = la_so_input.get("menh_palace")
    bo_menh = ((three_layer.get("lop_3_sach_co") or {}).get("bo_phu_tinh_per_palace") or {}).get(menh_chi)
    if bo_menh:
        parts.append("")
        parts.append("## Bộ phụ tinh quanh cung Mệnh (xem theo cặp + thế, không lẻ):")
        for bo in bo_menh[:5]:
            cap = "đủ cặp" if bo["du_cap"] else "lẻ"
            parts.append(f"- {bo['ten']} ({bo['loai']}) — {bo['the_vi']}, {cap}")
            for school, atoms in (bo.get("schools") or {}).items():
                for a in atoms[:1]:
                    vt = a.get("viet_thuan") or a.get("source_quote") or ""
                    if vt:
                        parts.append(f"  · ({school}) {vt[:150]}")

    # Cách cục có tên riêng — máy match chính xác điều kiện
    named = (three_layer.get("lop_3_sach_co") or {}).get("cach_cuc_named") or []
    if named:
        parts.append("")
        parts.append("## Cách cục có tên trong lá số (máy match điều kiện chính xác):")
        for cc in named[:4]:
            parts.append(f"- {cc['ten']} ({cc['loai']}): {cc['dieu_kien']}")
            for school, atoms in (cc.get("schools") or {}).items():
                for a in atoms[:1]:
                    vt = a.get("viet_thuan") or a.get("source_quote") or ""
                    if vt:
                        parts.append(f"  · ({school}) {vt[:160]}")

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

    # Đại vận hiện tại (BIẾN) — Việc 3 (đọc từ three_layer: đã áp mượn sao nếu vô chính diệu)
    dv = (three_layer.get("lop_3_sach_co") or {}).get("dai_van_hien_tai") \
        or la_so_input.get("dai_van_hien_tai")
    if dv:
        sao_txt = ", ".join(vi_star(s) for s in (dv.get("stars") or []))
        if dv.get("vo_chinh_dieu") and sao_txt:
            sao_txt = f"vô chính diệu, mượn sao đối cung: {sao_txt}"
        elif sao_txt:
            sao_txt = f"sao tọa vận: {sao_txt}"
        else:
            sao_txt = "cung vận vô chính diệu"
        parts.append("")
        parts.append(
            f"## Đại vận hiện tại: vận {dv['cycle_index']} "
            f"(tuổi {dv['start_age']}-{dv['end_age']}, đang tuổi mụ {dv['age_mu']}), "
            f"cung {vi_chi(dv['chi'])} — {sao_txt}"
        )
        parts.append(
            "Lưu ý: cung đại vận luận như Mệnh tạm 10 năm — kết hợp CƠ (lá số gốc) "
            "với BIẾN (vận đang đi), không phán cứng."
        )

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
