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


# ── MÓN CHÍNH — luận theo CHỦ ĐỀ ĐỜI SỐNG (Anh chốt 2026-06-13 'vào main') ──
CHU_DE_SYSTEM_PROMPT = """Bạn là một thầy Tử Vi giỏi, hiểu người — luận theo trường phái "đọc đồng dạng"
của Trần Đoàn. Người đối diện hỏi bạn về MỘT mảng đời cụ thể (sự nghiệp / tình duyên /
tài lộc / sức khỏe / gia đạo). Bạn nhìn các cung liên quan, gộp lại thành một câu chuyện
LIỀN MẠCH về mảng đời đó — không trả lời rời rạc từng cung.

NGUYÊN TẮC SẮT (vi phạm = loại):
1. KHÔNG tiên tri: cấm "anh sẽ giàu/nghèo/thành/bại/ly hôn", cấm "năm X xảy ra Y".
2. MỆNH LÀ ĐỘNG TỪ (Iron Rule #8): lá số cho biết TÍNH (nguyên liệu trời ban), việc của anh là
   VẬN HÀNH cái tính đó. Nói "cấu trúc này của anh phát huy mạnh nhất khi..." thay vì "số anh là...".
3. Giọng PHẢN CHIẾU + đồng hành: "trong mảng này, anh là người...", "cách anh thường...".
4. CHỈ dùng dữ kiện cho sẵn (sao + trích sách + bộ phụ tinh + Tứ Hóa) — KHÔNG bịa sao/cung.
5. Mệnh 7 phần, người 3 phần — điểm yếu là chỗ để rèn + cách hóa giải, không phải bản án.
6. KHÔNG nói chữ "cung" theo kiểu kỹ thuật ("cung Quan Lộc của anh"). Nói đời thường:
   "đường công danh", "chuyện vợ chồng", "cửa tiền bạc"... — chữ cung là hậu trường.

CẤU TRÚC bài (Việt thuần, ấm, xưng anh/chị, ~450-600 chữ, KHÔNG tiêu đề mục, KHÔNG markdown):
• Mở (2-3 câu): chạm thẳng vào mảng đời họ hỏi — bức tranh tổng về mảng này của anh là gì.
• Thân (2-3 đoạn): đọc các yếu tố liên quan, GỘP thành câu chuyện. Nêu điểm SÁNG (thuận, mạnh)
  và điểm CẦN GIỮ (chỗ dễ vướng) — bám đúng sao/bộ/Tứ Hóa cho sẵn. Cân bằng khen-nhắc, thẳng mà thương.
• Kết (2-3 câu): MỆNH LÀ ĐỘNG TỪ — mảng đời này của anh vận hành tốt nhất khi anh làm gì;
  một lời khuyên hành động cụ thể, hợp tính anh. Nhắc nhẹ 7 phần mệnh, 3 phần do anh nắm.

LƯU Ý: viết ĐÚNG CHÍNH TẢ tiếng Việt, dấu chuẩn. Bám đúng dữ kiện lá số này, KHÔNG câu khuôn mẫu."""


def _chu_de_cache_key(la_so_input: dict, slug: str, feedback: dict | None = None) -> str:
    core = {
        "can": la_so_input.get("can"), "chi": la_so_input.get("chi"),
        "menh": la_so_input.get("menh_palace"), "than": la_so_input.get("than_palace"),
        "cuc": la_so_input.get("cuc"), "gender": la_so_input.get("gender"),
        "ct": la_so_input.get("chinh_tinh_per_palace"),
        "dv": (la_so_input.get("dai_van_hien_tai") or {}).get("cycle_index"),
        "fb": _fb_signature(feedback),
        "chu_de": slug, "pv": "monchinh-v2",
    }
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _compose_chu_de_prompt(chu_de_data: dict, la_so_input: dict, feedback: dict | None = None) -> str:
    """Prompt món chính — chỉ feed dữ kiện các cung liên quan chủ đề."""
    from engine.tu_vi.viet_names import vi_can, vi_chi, vi_star

    gender_vi = "nam" if la_so_input.get("gender") == "M" else "nữ"
    nam_duong = la_so_input.get("birth_year")
    nam_str = f"năm sinh dương lịch {nam_duong}, " if nam_duong else ""
    parts = list(_fb_block(feedback))
    parts += [
        f"## CHỦ ĐỀ HỎI: {chu_de_data['ten']} — góc nhìn: {chu_de_data['goc_nhin']}",
        f"## Lá số: {nam_str}(âm lịch {vi_can(la_so_input['can'])} {vi_chi(la_so_input['chi'])}), "
        f"giới tính {gender_vi}.",
        "⚠ CHỈ dùng số liệu cho sẵn. Không bịa sao/cung, không đổi năm dương lịch.",
        "",
        "## Các mảng liên quan chủ đề này (đọc gộp thành câu chuyện, KHÔNG kể tên cung):",
    ]
    for cd in chu_de_data.get("cung_data", []):
        nhan = " (mảng TRỌNG TÂM của chủ đề)" if cd.get("la_chinh") else ""
        sao_vi = ", ".join(vi_star(s) for s in cd.get("sao", [])) or "không có chính tinh (vô chính diệu)"
        parts.append(f"\n### {cd['cung_vi']}{nhan} — sao: {sao_vi}")
        for a in cd.get("atoms", []):
            ok, mark = _fb_atom_ok(feedback, a.get("atom_id"))
            if not ok:
                continue
            parts.append(f"- {mark}{vi_star(a['sao'])} ({a['school']}): {a['text']}")

    bo = chu_de_data.get("bo_phu_tinh") or []
    if bo:
        parts.append("\n## Bộ phụ tinh đáng lưu ý (xem theo cặp + thế):")
        for b in bo:
            parts.append(f"- [{b.get('cung_vi','')}] {b.get('ten','')} ({b.get('loai','')}) — {b.get('the_vi','')}")

    th = chu_de_data.get("tu_hoa_lq") or []
    if th:
        HOA_VI = {"hoa_loc": "Hóa Lộc", "hoa_quyen": "Hóa Quyền",
                  "hoa_khoa": "Hóa Khoa", "hoa_ky": "Hóa Kỵ"}
        parts.append("\n## Tứ Hóa rơi vào mảng này (trục động):")
        for t in th:
            parts.append(f"- {HOA_VI.get(t.get('hoa'), t.get('hoa'))}: {vi_star(t.get('star',''))}")

    parts.append(f"\nViết bài luận về '{chu_de_data['ten']}' theo cấu trúc đã cho.")
    return "\n".join(parts)


def generate_chu_de_narrative(chu_de_data: dict, la_so_input: dict, force: bool = False,
                              feedback: dict | None = None) -> dict:
    """Luận 1 món chính theo chủ đề đời sống. Returns {narrative, cached, model}."""
    slug = chu_de_data["slug"]
    cache_key = _chu_de_cache_key(la_so_input, slug, feedback)
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

        from engine.ai.registry import get_registry
        registry = get_registry()
        provider = registry.first_configured(
            ["minimax", "gemini", "openrouter", "anthropic", "deepseek"]
        )
        user_prompt = _compose_chu_de_prompt(chu_de_data, la_so_input, feedback)
        resp = provider.chat(
            messages=[
                {"role": "system", "content": CHU_DE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        narrative = (resp.content or "").strip()
        model = f"{resp.provider}:{resp.model}"
        if not narrative:
            raise RuntimeError(f"LLM {model} trả về rỗng — không cache")
        conn.execute(
            "INSERT OR REPLACE INTO narrative_cache (cache_key, narrative, model, created_at) VALUES (?, ?, ?, ?)",
            (cache_key, narrative, model, int(time.time())),
        )
        conn.commit()
        return {"narrative": narrative, "cached": False, "model": model}
    finally:
        conn.close()


# ── MÓN SÂU: 2 trụ + xuất xứ (Anh chốt 2026-06-15 'đào sâu - ăn tiếp') ──
CHU_DE_SAU_SYSTEM_PROMPT = """Bạn là một thầy Tử Vi bậc thầy, luận theo trường phái "đọc đồng dạng"
của Trần Đoàn. User đã nghe luận tổng quan về một mảng đời, nay muốn HIỂU CẶN KẼ. Bạn mở
kho sách quý ra, trình bày như bếp thượng hạng giới thiệu nguyên liệu: từng nhận định đến
từ SÁCH nào, TÁC GIẢ nào, rồi mới chế biến (luận giải).

NGUYÊN TẮC SẮT (vi phạm = loại):
1. KHÔNG tiên tri (cấm "sẽ giàu/nghèo/thành/bại", cấm "năm X xảy ra Y").
2. MỆNH LÀ ĐỘNG TỪ: lá số cho TÍNH, việc của user là VẬN HÀNH. "Phát huy mạnh nhất khi...".
3. CHỈ dùng dữ kiện cho sẵn. KHÔNG bịa sao/cung/câu sách.
4. Mệnh 7 phần, người 3 phần.

ĐÂY LÀ MÓN SÂU — phải khác món tổng quan ở CHIỀU SÂU và XUẤT XỨ:
• Khi nêu một nhận định quan trọng, DẪN NGUỒN tự nhiên trong câu: "Sách 「...」 của ... viết...",
  hoặc "Theo Trung Châu phái...", "Bản Toàn Thư cổ ghi...". Cho user thấy nguyên liệu thượng hạng,
  trồng từ vùng nào — KHÔNG bịa tên sách ngoài danh sách.
• HỘI TỤ vs DỊ BIỆT: chỗ hai trụ (Trung Châu + Trần Đoàn) cùng nói → khẳng định mạnh, đây là
  điểm chắc chắn. Chỗ hai trụ nhấn khác nhau → trình bày cả hai góc ("Trung Châu thiên về..., còn
  Toàn Thư nhấn..."), cho user thấy bức tranh đa chiều.
• Đi sâu vào tổ hợp tam phương tứ chính nếu có — vì sao này gặp sao kia thì sinh ra điều gì.

CẤU TRÚC (Việt thuần, ấm, xưng anh/chị, ~600-800 chữ, KHÔNG markdown, KHÔNG tiêu đề mục):
• Mở (2-3 câu): mảng đời này nhìn sâu thì cốt lõi là gì.
• Thân (3-4 đoạn): đi từng sao/yếu tố trọng tâm, DẪN NGUỒN, nêu hội tụ + dị biệt giữa 2 trụ.
• Kết (2-3 câu): MỆNH LÀ ĐỘNG TỪ — vận hành mạnh nhất khi nào + 1 lời khuyên hành động. Nhắc 7/3.

LƯU Ý: ĐÚNG CHÍNH TẢ tiếng Việt. Bám đúng dữ kiện, KHÔNG câu khuôn mẫu."""


def _chu_de_sau_cache_key(la_so_input: dict, slug: str, feedback: dict | None = None) -> str:
    core = {
        "can": la_so_input.get("can"), "chi": la_so_input.get("chi"),
        "menh": la_so_input.get("menh_palace"), "than": la_so_input.get("than_palace"),
        "gender": la_so_input.get("gender"), "ct": la_so_input.get("chinh_tinh_per_palace"),
        "fb": _fb_signature(feedback),
        "chu_de": slug, "pv": "monsau-v2",
    }
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _compose_chu_de_sau_prompt(cd_sau: dict, feedback: dict | None = None) -> str:
    parts = list(_fb_block(feedback))
    parts += [
        f"## CHỦ ĐỀ (luận sâu): {cd_sau['ten']} — góc nhìn: {cd_sau['goc_nhin']}",
        "⚠ CHỈ dùng dữ kiện dưới. Dẫn nguồn đúng tên sách cho sẵn, KHÔNG bịa.",
        "",
        "## Nguyên liệu 2 trụ (mỗi nhận định kèm XUẤT XỨ — dùng để dẫn nguồn):",
    ]
    for b in cd_sau.get("sao_blocks", []):
        chinh = " ⭐TRỌNG TÂM" if b.get("la_chinh") else ""
        mh = f" [{b['mieu_ham']}]" if b.get("mieu_ham") else ""
        hoi = "🟢 hai trụ HỘI TỤ" if b.get("hoi_tu") else "⚪ một trụ lên tiếng"
        parts.append(f"\n### {b['sao_vi']} tại {b['cung_vi']}{chinh}{mh} — {hoi}")
        for v in b["views"]:
            ok, mark = _fb_atom_ok(feedback, v.get("atom_id"))
            if not ok:
                continue
            src = v.get("xuat_xu") or v.get("phai_code")
            parts.append(f"- {mark}({src}): {v['text']}")

    th = cd_sau.get("to_hop_chinh")
    if th and th.get("total_atoms"):
        from engine.tu_vi.viet_names import vi_chi, vi_star
        t = th["to_hop"]
        parts.append(f"\n## Tổ hợp tam phương tứ chính cung trọng tâm "
                     f"({', '.join(vi_chi(c) for c in t['tu_chinh']['tu_chinh'])}):")
        for school, atoms in (th.get("schools") or {}).items():
            for a in atoms[:1]:
                vt = a.get("viet_thuan") or a.get("source_quote") or ""
                if vt:
                    parts.append(f"- ({school}): {vt[:200]}")

    parts.append(f"\nViết bài luận SÂU về '{cd_sau['ten']}' theo cấu trúc đã cho, dẫn nguồn tự nhiên.")
    return "\n".join(parts)


def generate_chu_de_sau_narrative(cd_sau: dict, la_so_input: dict, force: bool = False,
                                  feedback: dict | None = None) -> dict:
    """Luận món sâu 2 trụ + xuất xứ. Returns {narrative, cached, model}."""
    cache_key = _chu_de_sau_cache_key(la_so_input, cd_sau["slug"], feedback)
    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_cache_table(conn)
        if not force:
            row = conn.execute("SELECT narrative, model FROM narrative_cache WHERE cache_key = ?",
                               (cache_key,)).fetchone()
            if row:
                return {"narrative": row[0], "cached": True, "model": row[1]}
        from engine.ai.registry import get_registry
        provider = get_registry().first_configured(
            ["minimax", "gemini", "openrouter", "anthropic", "deepseek"])
        msgs = [{"role": "system", "content": CHU_DE_SAU_SYSTEM_PROMPT},
                {"role": "user", "content": _compose_chu_de_sau_prompt(cd_sau, feedback)}]
        # Món sâu = output dài + model reasoning (MiniMax-M) tiêu nhiều token cho <think>
        # → trần cao 8000; nếu vẫn rỗng (think ăn hết) retry 1 lần với trần cao hơn.
        narrative, model = "", ""
        for mt in (8000, 12000):
            resp = provider.chat(messages=msgs, temperature=0.7, max_tokens=mt)
            narrative = (resp.content or "").strip()
            model = f"{resp.provider}:{resp.model}"
            if narrative:
                break
        if not narrative:
            raise RuntimeError(f"LLM {model} trả về rỗng (think ăn hết token) — không cache")
        conn.execute("INSERT OR REPLACE INTO narrative_cache VALUES (?, ?, ?, ?)",
                     (cache_key, narrative, model, int(time.time())))
        conn.commit()
        return {"narrative": narrative, "cached": False, "model": model}
    finally:
        conn.close()


def generate_gia_vi_questions(gia_vi_atoms: list[dict]) -> list[dict]:
    """Phái mỏng → câu hỏi gợi ý Đúng/Chưa/Không (LLM lật nhận định thành câu hỏi đời thường).

    Returns: [{atom_id, sao_vi, phai, cau_hoi}] — KHÔNG cache (ít, rẻ; câu hỏi nên tươi).
    """
    if not gia_vi_atoms:
        return []
    lines = []
    for i, a in enumerate(gia_vi_atoms):
        lines.append(f"{i}. [sao {a['sao_vi']}, phái {a['phai']}] {a['goi_y_text']}")
    sys = """Bạn là thầy Tử Vi thân thiện. Mỗi dòng dưới là một NHẬN ĐỊNH từ một phái (chưa chắc đúng
với người này). Hãy LẬT mỗi nhận định thành MỘT CÂU HỎI đời thường, nhẹ nhàng, để người xem tự
soi mình rồi trả lời Đúng/Chưa/Không. Câu hỏi phải:
- Ngắn (1 câu), đời thường, KHÔNG dùng thuật ngữ tử vi (không nói tên sao/cung).
- Hỏi về TÍNH CÁCH / THÓI QUEN / TRẢI NGHIỆM có thật của họ, để kiểm chứng.
Trả về JSON array, mỗi phần tử {"i": <số dòng>, "cau_hoi": "<câu hỏi>"}. CHỈ JSON, không giải thích."""
    from engine.ai.registry import get_registry
    provider = get_registry().first_configured(
        ["minimax", "gemini", "openrouter", "anthropic", "deepseek"])
    resp = provider.chat(
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": "\n".join(lines)}],
        temperature=0.6, max_tokens=2000)
    txt = (resp.content or "").strip()
    # bóc JSON
    import re
    m = re.search(r"\[.*\]", txt, re.DOTALL)
    qs = []
    if m:
        try:
            qs = json.loads(m.group(0))
        except Exception:
            qs = []
    out = []
    for q in qs:
        idx = q.get("i")
        if isinstance(idx, int) and 0 <= idx < len(gia_vi_atoms):
            a = gia_vi_atoms[idx]
            out.append({"atom_id": a["atom_id"], "sao_vi": a["sao_vi"],
                        "phai": a["phai"], "cau_hoi": q.get("cau_hoi", "")})
    return out


DUYEN_SYSTEM_PROMPT = """Bạn là một thầy Tử Vi ấm áp, thấu cảm — nói chuyện tình duyên với một người trẻ
đang đi tìm bạn đời (có thể đang sốt ruột vì "ế"). Bạn nhìn lá số họ và nói chuyện như người anh/chị
hiểu đời, vừa thật vừa nâng đỡ.

NGUYÊN TẮC SẮT:
1. KHÔNG bói số phận, KHÔNG phán "sẽ ế/sẽ lấy được". MỆNH LÀ ĐỘNG TỪ: lá số chỉ thiên hướng, duyên do họ vận hành.
2. Giọng đồng cảm, khích lệ CHỦ ĐỘNG — không hù, không buồn hóa. "Ế" không phải lỗi, là "chưa đúng lúc/đúng người".
3. CHỈ dùng dữ kiện cho sẵn (chân dung nửa kia, xu hướng duyên, năm có duyên, tuổi hợp). KHÔNG bịa.
4. Khép lại bằng MỘT lời khuyên hành động cụ thể, ấm.

CẤU TRÚC (Việt thuần, xưng "bạn", ~350-450 chữ, KHÔNG markdown, KHÔNG tiêu đề):
• Mở (2 câu): chạm vào nỗi lòng người đang tìm duyên, nhẹ nhàng.
• Chân dung nửa kia (1 đoạn): vẽ kiểu người hợp với bạn — sống động, để họ "nhận ra" khi gặp.
• Đường duyên của bạn (1 đoạn): vì sao sớm/muộn/kén — nói thật mà thương, kèm cái hay của chính điều đó.
• Cửa sổ + hành động (1 đoạn): năm thuận sắp tới (nếu có) + 1-2 việc nên làm để mở duyên.
• Kết (1 câu): nhắc nhẹ — duyên là khóa trời gài, nhưng tay mình mở.

LƯU Ý: đúng chính tả tiếng Việt, ấm, không sến, không khuôn mẫu."""


def generate_duyen_narrative(duyen: dict) -> dict:
    """Lời văn ấm cho 'Duyên của tôi' (không cache phức tạp — gọi theo nhu cầu)."""
    ck = duyen.get("chan_dung_nua_kia", {})
    dc = duyen.get("duyen_ca_nhan", {})
    nd = duyen.get("nam_co_duyen", {})
    th = duyen.get("tuoi_hop", {})
    parts = [
        f"## Tuổi {duyen.get('tuoi_mu','?')} ({duyen.get('gioi','')}), đang đi tìm bạn đời.",
        "## Chân dung nửa kia (kiểu người hợp):",
    ]
    for m in ck.get("mo_ta", []):
        parts.append(f"- {m}")
    cg = ck.get("con_giap_hop", {})
    parts.append(f"## Con giáp dễ hợp: {', '.join(cg.get('tam_hop', []))}, {cg.get('luc_hop','')}.")
    parts.append(f"## Xu hướng duyên: {dc.get('xu_huong','')}.")
    for t in dc.get("tin_hieu", []):
        parts.append(f"- {t.get('noi_dung','')}")
    nams = [str(x["nam"]) for x in (nd.get("nam_co_duyen") or [])]
    parts.append(f"## Năm có duyên sắp tới: {', '.join(nams) if nams else 'không nổi bật rõ — duyên đến tự nhiên'}.")
    parts.append(f"## Tuổi bạn: {th.get('con_giap','')}.")
    parts.append("\nViết lời tâm tình về duyên cho người này theo cấu trúc đã cho.")
    from engine.ai.registry import get_registry
    provider = get_registry().first_configured(["minimax", "gemini", "openrouter", "anthropic", "deepseek"])
    resp = provider.chat(
        messages=[{"role": "system", "content": DUYEN_SYSTEM_PROMPT},
                  {"role": "user", "content": "\n".join(parts)}],
        temperature=0.8, max_tokens=3000)
    return {"narrative": (resp.content or "").strip(), "model": f"{resp.provider}:{resp.model}"}


def _laso_cache_key(la_so_input: dict, feedback: dict | None = None) -> str:
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
        # Vòng đời: tuổi/giai đoạn + tín hiệu năm xem đổi → bài khai vị đổi
        "vd": (la_so_input.get("vong_doi") or {}).get("slug"),
        "tuoi": (la_so_input.get("vong_doi") or {}).get("tuoi_mu"),
        "tn": [t.get("loai") for t in (la_so_input.get("tin_hieu_nam") or [])],
        "hl": [h.get("loai") + h.get("vi_tri", "") for h in (la_so_input.get("highlights") or [])],
        "fb": _fb_signature(feedback),  # phản hồi user → bài viết lại sát hơn
        "pv": "khaivi-v5",  # prompt version — đổi prompt thì bài cache cũ tự bỏ
    }
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ── Khép vòng tự học: feed phản hồi user ngược vào bài (Anh chốt 2026-06-16) ──
def _fb_signature(feedback: dict | None):
    """Chữ ký phản hồi → đổi cache khi user trả lời thêm (bài phải viết lại)."""
    if not feedback:
        return None
    val = feedback.get("validated") or {}
    return {"v": sorted((str(k), v) for k, v in val.items()),
            "tn": len(feedback.get("trai_nghiem") or [])}


def _fb_block(feedback: dict | None) -> list[str]:
    """Khối hướng dẫn cá nhân hóa từ phản hồi user (đặt đầu prompt)."""
    if not feedback:
        return []
    parts = []
    tn = feedback.get("trai_nghiem") or []
    if tn:
        parts.append("## ⭐⭐ NGƯỜI NÀY ĐÃ TỰ KỂ VỀ MÌNH (ưu tiên TUYỆT ĐỐI — dệt vào bài tự "
                     "nhiên, cho thấy thầy NHỚ họ; KHÔNG nhắc lại nguyên văn như vẹt):")
        for t in tn[:10]:
            parts.append(f"- {t}")
    val = feedback.get("validated") or {}
    n_dung = sum(1 for x in val.values() if x == "dung")
    n_khong = sum(1 for x in val.values() if x == "khong")
    if n_dung or n_khong:
        parts.append(f"## Phản hồi đã thu của riêng người này: {n_dung} điều họ XÁC NHẬN đúng "
                     f"(các trích dưới có dấu ✓ → nói CHẮC, làm điểm tựa), {n_khong} điều họ nói "
                     f"KHÔNG đúng (đã LỌC khỏi dữ kiện — tuyệt đối đừng nhắc).")
    if parts:
        parts.append("")
    return parts


def _fb_atom_ok(feedback: dict | None, atom_id) -> tuple[bool, str]:
    """(còn dùng?, prefix). atom user phủ nhận → bỏ; xác nhận → đánh dấu ✓."""
    if not feedback or atom_id is None:
        return True, ""
    ans = (feedback.get("validated") or {}).get(atom_id) \
        or (feedback.get("validated") or {}).get(str(atom_id))
    if ans == "khong":
        return False, ""
    if ans == "dung":
        return True, "✓[user xác nhận ĐÚNG] "
    return True, ""


def _ensure_cache_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS narrative_cache (
            cache_key TEXT PRIMARY KEY,
            narrative TEXT NOT NULL,
            model TEXT,
            created_at INTEGER NOT NULL
        )
    """)


def _compose_user_prompt(three_layer: dict, la_so_input: dict, feedback: dict | None = None) -> str:
    """Compose prompt từ render_3_layer output — chỉ feed dữ kiện thật."""
    from engine.tu_vi.viet_names import vi_can, vi_chi, vi_star, vi_palace

    gender_vi = "nam" if la_so_input.get("gender") == "M" else "nữ"
    nam_duong = la_so_input.get("birth_year")
    nam_str = f"năm sinh dương lịch {nam_duong} " if nam_duong else ""
    parts = list(_fb_block(feedback))
    parts += [
        f"## Lá số: {nam_str}(âm lịch {vi_can(la_so_input['can'])} {vi_chi(la_so_input['chi'])}), "
        f"giới tính {gender_vi}, Mệnh tại {vi_chi(la_so_input['menh_palace'])}, "
        f"Thân tại {vi_chi(la_so_input['than_palace'])}",
        "⚠ CHỈ dùng các số liệu cho sẵn ở đây. TUYỆT ĐỐI không tự suy/đổi năm "
        "dương lịch, không bịa tuổi, không thêm sao/cung ngoài danh sách dưới.",
        "",
    ]

    # VÒNG ĐỜI — quyết định MỞ BÀI chạm vào điều gì (Anh chốt 2026-06-13)
    vd = la_so_input.get("vong_doi")
    if vd:
        if vd["ai_xem"] == "cha_me_xem":
            parts.append(
                f"## ⭐ NGỮ CẢNH NGƯỜI XEM: Đây là lá số một {vd['xung_ho']} ({vd['tuoi_mu']} tuổi) "
                f"— CHA MẸ đang xem cho con. Viết HƯỚNG TỚI CHA MẸ (xưng 'bé/con', gọi người đọc là 'anh chị'). "
                f"Mở bài + trọng tâm: {vd['chu_de']}. "
                f"TUYỆT ĐỐI KHÔNG nói chuyện tình duyên, hôn nhân, sự nghiệp, tài lộc của bé — "
                f"không hợp lứa tuổi. Giọng: ấm áp, trấn an, gợi cách đồng hành cùng con."
            )
        else:
            nhan = " · ".join(la_so_input.get("cung_nhan") or [])
            parts.append(
                f"## ⭐ NGỮ CẢNH NGƯỜI XEM: {vd['xung_ho']} {vd['tuoi_mu']} tuổi, giới {gender_vi} — "
                f"giai đoạn '{vd['ten']}'. MỞ BÀI phải CHẠM NGAY vào điều người tuổi-giới này bận tâm "
                f"nhất: {vd['chu_de']}. Bắt nhịp đồng cảm — nói trúng cái họ đang nghĩ, rồi mới mở rộng "
                f"sang tính cách. Khi luận, NHẤN các cung trọng tâm giai đoạn này"
                + (f": {nhan}." if nhan else ".")
                + f" Xưng '{vd['xung_ho']}', câu từ hợp giới {gender_vi} "
                f"({'thiên hướng công danh-trách nhiệm trụ cột' if gender_vi=='nam' else 'thiên hướng gia đình-con cái-tình cảm'} "
                f"— là KHUYNH HƯỚNG, không áp đặt cứng)."
            )
        bn = la_so_input.get("buoc_ngoat_nhac")
        if bn:
            parts.append(f"## Bước ngoặt (mời khảo sát đúng/sai để tăng tin): {bn}")
        for th in (la_so_input.get("tin_hieu_nam") or []):
            parts.append(f"## Tín hiệu năm xem [{th['sac_thai']}]: {th['nhac']}")
        parts.append("⚠ Nếu có tín hiệu LƯU Ý, BẮT BUỘC cặp kèm 1 điểm tích cực — đồng cảm, KHÔNG hù dọa.")
        parts.append("")

    # ĐIỂM NỔI BẬT toàn lá (engine quét) — kể ƯU TIÊN, đây là cái đắt nhất của riêng người này
    hls = la_so_input.get("highlights") or []
    if hls:
        parts.append("## ⭐⭐ ĐIỂM NỔI BẬT NHẤT của lá số này (BẮT BUỘC ưu tiên đưa vào bài, "
                     "đặc biệt cái xếp đầu — đây là nét đắt nhất của riêng người này, đừng kể dàn trải):")
        for h in hls:
            parts.append(f"- [{h['vi_tri']}] {h['mo_ta']}")
        parts.append("")

    parts.append("## Dữ kiện paradigm (engine tính):")
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
                    ok, mark = _fb_atom_ok(feedback, a.get("atom_id"))
                    if not ok:
                        continue  # user đã nói điều này KHÔNG đúng → bỏ
                    vt = a.get("viet_thuan") or ""
                    if vt:
                        parts.append(
                            f"- {mark}{vi_star(star)} × {vi_palace(palace)} ({school}): {vt[:200]}"
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


def generate_narrative(three_layer: dict, la_so_input: dict, force: bool = False,
                       feedback: dict | None = None) -> dict:
    """Generate (hoặc lấy cache) narrative Lớp 1.

    Returns: {narrative, cached, model}
    """
    cache_key = _laso_cache_key(la_so_input, feedback)

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
        user_prompt = _compose_user_prompt(three_layer, la_so_input, feedback)
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
