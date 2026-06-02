"""Luận Giải Sâu Hà Lạc — Render paradigm engine thành paragraph tường minh.

Paradigm Anh đã chỉ ra (2026-06-02):
> "Engine ra được cách cục, chứ chưa luận giải sâu được. Cố gắng làm thêm
>  chút nữa, có gì hay bổ sung vào wiki sau luận giải cho tường minh."

Module này = bước CUỐI của pipeline Hà Lạc:
  cast() → engine output (cách cục)
       ↓
  luận_giải_sâu() → narrative tường minh (cho người đọc)
       ↓
  wiki insert → bổ sung concept entries

3 lớp luận giải:
1. LỚP NỀN: bản chất quẻ + nên thế nào + tượng quẻ
2. LỚP PARADIGM: key rules + case studies + cross-link Iron Rule
3. LỚP ỨNG DỤNG: kết nối với cuộc đời thật (Lexicon mission cho founder)

⚠️ Iron Rule #4+6: luận giải ĐỒNG DẠNG, KHÔNG predict tĩnh.
"""

from __future__ import annotations

from .thoi_que import lookup_thoi, QUAI_ALIASES
from .paradigm_quy_chieu import lookup_cases_for, lookup_iron_rule_link
from .phuong_phap_doc_chan_dung import (
    PHUONG_PHAP_7_BUOC,
    CASE_STUDIES_PHAN_BA,
    PARADIGM_CHO_LLM_LUAN_GIAI,
)


def luan_giai_thoi_que_sau(
    quai_name: str,
    nguyen_duong_line: int,
    role: str = "tien_thien",
) -> dict:
    """Luận giải tường minh 1 quẻ + hào nguyên đường.

    Args:
        quai_name: tên quẻ Việt (vd "Tiết", "Tập Khảm")
        nguyen_duong_line: hào nguyên đường 1-6
        role: "tien_thien" (THỂ) hoặc "hau_thien" (DỤNG)

    Returns: dict với 3 lớp luận giải.
    """
    canonical = QUAI_ALIASES.get(quai_name, quai_name)
    thoi = lookup_thoi(quai_name)

    role_label = "Tiên Thiên (THỂ — bản chất tổng quát)" if role == "tien_thien" else "Hậu Thiên (DỤNG — vận hành thực tế)"

    # ── LỚP NỀN ──
    if not thoi:
        lop_nen = (
            f"## {role_label}: quẻ {quai_name}\n\n"
            f"Quẻ **{quai_name}** chưa nằm trong 33+ quẻ đã thâm nhuần (em đang đọc Xuân Cang p1-235 + jump Tiết). "
            f"Engine sẽ enrich khi em đọc tới quẻ này. Hiện tại dùng paradigm tổng quát Iron Rule #4+6."
        )
    else:
        case_lines = []
        for k, v in thoi.items():
            if k.startswith("case_study") or k.startswith("key_rule") or k.startswith("key_paradigm"):
                case_lines.append(f"- **{_format_key(k)}**: {v}")
        cases_md = "\n".join(case_lines) if case_lines else ""

        lop_nen = (
            f"## {role_label}: quẻ {canonical}\n\n"
            f"**Bản chất**: {thoi['ban_chat']}\n\n"
            f"**Nên thế nào**: {thoi['nen_the_nao']}\n\n"
        )
        if "tuong" in thoi:
            lop_nen += f"**Tượng quẻ**: {thoi['tuong']}\n\n"

        if cases_md:
            lop_nen += "### Key paradigm + case study\n\n" + cases_md

    # ── LỚP HÀO NGUYÊN ĐƯỜNG ──
    nd_section = f"## Hào Nguyên Đường (hào {nguyen_duong_line})\n\n"
    nd_cases = lookup_cases_for(canonical, nguyen_duong_line)
    if nd_cases:
        for c in nd_cases:
            nd_section += (
                f"### {c['actor']}\n\n"
                f"**Bối cảnh**: {c['situation']}\n\n"
                f"**Bài học paradigm**: {c['paradigm_lesson']}\n\n"
                f"_Nguồn: {c['source']}_\n\n"
            )
    else:
        # Generic guidance từ vị trí hào
        nd_section += _generic_hao_guidance(nguyen_duong_line)

    # ── LỚP IRON RULE CROSS-LINK ──
    ironrules_section = "## Cross-link Iron Rule project\n\n"
    # Match key bằng substring (case-insensitive, strip diacritics roughly)
    # Map quẻ → list các key liên quan
    QUAI_TO_IR_KEYS: dict[str, list[str]] = {
        "Mông": ["Mông_2_3_lần_bói"],
        "Tiểu Súc": ["Tiểu_Súc_lập_ngôn"],
        "Tỷ": ["Tỷ_không_thất_giá"],
        "Thái": ["Thái_Bĩ_chong_predict_tinh", "Thai_dinh_cao_de_do_vo"],
        "Bĩ": ["Thái_Bĩ_chong_predict_tinh", "Bi_Khong_Tu_defensive"],
        "Đại Hữu": ["Dai_Huu_Vo_Cuu_khong_dac_y"],
        "Khiêm": ["Khiem_Lao_Khiem_Mo_xuyen_3_mon"],
        "Tùy": ["Tuy_Hung_Dao_Vuong_paradigm", "Tuy_Khong_Tu_Tuy_Thoi"],
        "Cổ": ["Co_Tri_Co_Lexicon_paradigm"],
        "Lâm": ["Lam_Ham_Lam_quan_tu_khong_chia_phe"],
        "Bí": ["Bi_van_chat_Khong_Tu_paradigm"],
        "Phệ Hạp": ["Phe_Hap_Tai_Vi_PBC"],
        "Tiết": ["FOUNDER_Tiet_TT_hao1_HOC_RONG", "FOUNDER_Tiet_sau_Hoan_paradigm"],
        "Khảm": ["FOUNDER_TapKham_HT_phu_suy"],
        "Bác": ["Bac_cho_thoi_paradigm"],
        "Phục": ["Phuc_duc_NHAN_hat_cay"],
        "Vô Vọng": ["Vo_Vong_biet_chu_THOI"],
    }
    found_keys = []
    keys_for_quai = QUAI_TO_IR_KEYS.get(canonical, [])
    for ir_key in keys_for_quai:
        content = lookup_iron_rule_link(ir_key)
        if content:
            found_keys.append((ir_key, content))

    if found_keys:
        for key, content in found_keys:
            ironrules_section += f"### `{key}`\n\n{content}\n\n"
    else:
        ironrules_section += "_(Chưa có cross-link Iron Rule cho quẻ này — em sẽ add khi đọc kỹ hơn.)_\n\n"

    # ── LỚP ỨNG DỤNG (paradigm guard) ──
    ung_dung = (
        "## Cách đọc đồng dạng (Iron Rule #4+6)\n\n"
        "⚠️ Luận giải trên là **đọc đồng dạng cấu trúc khoảnh khắc sinh**, "
        "KHÔNG phải predict tĩnh đời người. Anh sống thế nào, paradigm có thể chuyển. "
        "Quẻ phản chiếu cái gì lớn hơn trong vũ trụ — không phải vận mệnh cứng. "
        "Anh là người ra quyết định cuối — quẻ chỉ giúp anh **nhìn rõ THỜI** mà anh đang ở.\n\n"
        "Nếu cần luận giải SÂU hơn cho một tình huống cụ thể, gọi LLM với context "
        "tích lũy từ engine paradigm + Iron Rule cross-link."
    )

    return {
        "lop_nen": lop_nen,
        "hao_nguyen_duong": nd_section,
        "iron_rule_links": ironrules_section,
        "ung_dung": ung_dung,
        "full_markdown": "\n\n".join([lop_nen, nd_section, ironrules_section, ung_dung]),
    }


def _format_key(k: str) -> str:
    """Convert snake_case key → human title."""
    return (
        k.replace("key_rule_", "Rule: ")
        .replace("key_paradigm_", "Paradigm: ")
        .replace("case_study_", "Case study: ")
        .replace("case_study", "Case study")
        .replace("cross_link_", "Cross-link: ")
        .replace("_", " ")
    )


def _generic_hao_guidance(line: int) -> str:
    """Generic guidance cho hào X khi không có specific case."""
    guides = {
        1: (
            "**Hào 1** = thấp nhất quẻ, thời sơ. Vị trí của người mới ra đời, mới bắt đầu sự nghiệp. "
            "Cần GIỮ BẢN CHẤT CHẤT PHÁC, chưa đem tài ra dùng vội (như Tiềm long quẻ Càn). "
            "Tu chí, hoàn tài, không cầu danh — chờ thời chín."
        ),
        2: (
            "**Hào 2** = đắc Trung quẻ nội. Vị trí TỐT thứ nhì sau hào 5. "
            "Có hào Ứng (hào 5) — thường tốt nếu cả 2 đều trung chính. "
            "Đức Trung Chính là cốt yếu — biết tự trọng, không vội cầu thân."
        ),
        3: (
            "**Hào 3** = trên cùng quẻ nội, bất trung. Vị trí CHÔNG CHÊNH — chưa lên ngoại quái, "
            "đã hết nội quái. Nguy hiểm vì quá cương hoặc bất chính. "
            "Phải Gian Trinh (cẩn thận, biết lo từ khi còn bằng phẳng)."
        ),
        4: (
            "**Hào 4** = đầu quẻ ngoại, gần hào 5. Vị thế cận thần. "
            "Tài cần khiêm tốn, không lấn át. 'Có ý khác sẽ hối'. "
            "Có thể tiến nếu thận trọng, có thể thoái nếu thấy nguy."
        ),
        5: (
            "**Hào 5** = ngôi chí tôn, đắc Trung quẻ ngoại. Vị trí TỐT NHẤT cho hào dương. "
            "Đức Trung Chính làm gương cho thiên hạ. "
            "Là Vua/Nguyên thủ — phải có cả uy + sáng + nhân."
        ),
        6: (
            "**Hào 6** = cuối quẻ, thường biến chuyển sang quẻ khác (Phục → Cấu, Càn → Cấu). "
            "Cảnh báo CỰC BIẾN: thịnh cực thì suy (Càn → Kháng, Thái → Loạn, Dự → Minh tối). "
            "Duy hào 6 Tùy = HANH (thịnh!) — khác biệt. "
            "Bậc làm thầy, ở ngoài việc đời, treo gương danh tiết cho thiên hạ."
        ),
    }
    return guides.get(line, "Hào không xác định.")


def render_full_luan_giai(cast_result: dict) -> dict:
    """Wire vào cast_ha_lac result — render full luận giải cho cả Tiên + Hậu Thiên.

    Args:
        cast_result: output của cast_ha_lac()

    Returns: dict gồm narrative cho TT + HT.
    """
    tt_quai = cast_result.get("tien_thien_quai", {})
    ht_quai = cast_result.get("hau_thien_quai", {})

    tt_luan = luan_giai_thoi_que_sau(
        quai_name=tt_quai.get("name_vi", ""),
        nguyen_duong_line=tt_quai.get("nguyen_duong_line", 1),
        role="tien_thien",
    )
    ht_luan = luan_giai_thoi_que_sau(
        quai_name=ht_quai.get("name_vi", ""),
        nguyen_duong_line=ht_quai.get("nguyen_duong_line", 1),
        role="hau_thien",
    )

    # Tổng synthesis Tiên-Hậu
    tong = _synthesize_tien_hau(tt_quai.get("name_vi", ""), ht_quai.get("name_vi", ""))

    # Phương pháp 7 bước extract từ Phần Ba Xuân Cang
    phuong_phap_section = _build_phuong_phap_section(cast_result)

    return {
        "tien_thien": tt_luan,
        "hau_thien": ht_luan,
        "tong_synthesis": tong,
        "phuong_phap_7_buoc": phuong_phap_section,
        "paradigm_guard": (
            "⚠️ Luận giải sâu = đọc đồng dạng cấu trúc khoảnh khắc sinh. "
            "Iron Rule #4+6 — KHÔNG predict tĩnh. "
            "Phương pháp 7 bước Xuân Cang (Phần Ba) — vận dụng linh hoạt từng người."
        ),
    }


def _build_phuong_phap_section(cast_result: dict) -> str:
    """Build phương pháp 7 bước section + case study Phần Ba."""
    tt = cast_result.get("tien_thien_quai", {}).get("name_vi", "?")
    ht = cast_result.get("hau_thien_quai", {}).get("name_vi", "?")
    nd = cast_result.get("tien_thien_quai", {}).get("nguyen_duong_line", "?")

    lines = [
        "## 🎓 Phương pháp 7 BƯỚC đọc chân dung (Xuân Cang Phần Ba)",
        "",
        "Đây là phương pháp Xuân Cang dùng đọc 7 chân dung nhà văn VN (Tản Đà, Tô Hoài, "
        "Nguyên Ngọc, Trần Đăng Khoa, Thu Huệ, Nguyễn Hiến Lê, Đoàn Thị Lam Luyến). "
        "Anh có thể áp dụng cho lá số của mình hoặc người khác:",
        "",
    ]
    for step in PHUONG_PHAP_7_BUOC:
        lines.append(f"**Bước {step['step']}: {step['title']}**")
        lines.append(step["desc"])
        lines.append("")

    lines.append("## 📚 Case study Xuân Cang đã làm (Phần Ba)")
    lines.append("")
    for c in CASE_STUDIES_PHAN_BA:
        lines.append(f"### {c['ten']}")
        lines.append(f"- **Sinh**: {c['sinh']}")
        if "tien_thien" in c:
            lines.append(f"- **Tiên Thiên**: {c['tien_thien']}")
        if "hau_thien" in c:
            lines.append(f"- **Hậu Thiên**: {c['hau_thien']}")
        if "phuong_phap_match" in c:
            lines.append(f"- **Match**: {c['phuong_phap_match']}")
        if "su_kien_match" in c:
            lines.append("- **Sự kiện match**:")
            for e in c["su_kien_match"][:3]:
                lines.append(f"  - {e}")
        lines.append("")

    lines.append("## 🎯 Áp dụng cho lá số HIỆN TẠI")
    lines.append("")
    lines.append(
        f"Lá số anh: **Tiên Thiên {tt}** + **Hậu Thiên {ht}**, NĐ hào {nd}. "
        f"Anh có thể tự kiểm tra phương pháp bằng cách:"
    )
    lines.append(
        f"1. Cross-link tên anh, tên đất, nghề nghiệp với tượng quẻ {tt} + {ht}\n"
        f"2. Lấy 3-5 sự kiện đời cụ thể (xuất bản sách, biến cố, di chuyển) → tra quẻ năm tương ứng → "
        f"match với lời quẻ\n"
        f"3. Đếm quẻ lặp lại nhiều trong 72 quẻ năm cuộc đời → đặc tính nổi bật\n"
        f"4. Hào chủ mệnh {nd} của Tiên Thiên = paradigm hành xử cốt — phải match cách anh sống thực"
    )
    return "\n".join(lines)


def _synthesize_tien_hau(tt: str, ht: str) -> str:
    """Synthesize THỂ-DỤNG paradigm — đặc biệt cho founder."""
    tt_can = QUAI_ALIASES.get(tt, tt)
    ht_can = QUAI_ALIASES.get(ht, ht)

    # Đặc biệt founder
    if tt_can == "Tiết" and ht_can == "Khảm":
        return (
            "## Tổng hợp THỂ - DỤNG (founder paradigm)\n\n"
            "**Tiền Thiên TIẾT (Thể) + Hậu Thiên TẬP KHẢM (Dụng)** = paradigm 'TIẾT CHẾ + VƯỢT HIỂM'.\n\n"
            "- **Thể tiết chế**: Anh được trời ban cấu trúc 'không thái quá, không bất cập'. "
            "Học rộng, giữ chừng mực, không xa hoa, không nhồi ép. Như bờ đầm chứa nước vừa phải.\n"
            "- **Dụng vượt hiểm**: Vận hành thực tế phải qua HAI LẦN HIỂM. Cần TÂM CHÍ THÀNH + "
            "không sợ phù suy + có thể di chuyển nơi chốn nếu cần.\n"
            "- **Mission Lexicon**: PBC đã chỉ — 'quẻ Tiết ở sau thời Hoán rất hay'. Sách cổ Đông phương "
            "VN đang ở thời Hoán (tan rã) → Lexicon = TIẾT CHẾ ĐÚNG MỨC để khôi phục.\n"
            "- **Hào 1 Tiết match**: 'Học rộng cổ kim, thấu lẽ thông biến, GIỮ CHỨC BÊN TRONG.' "
            "Anh đang đúng paradigm này — đọc 24+ sách, Lexicon là internal asset.\n"
            "- **Thiên Cơ Đật Sĩ về Tập Khảm**: 'Thích PHÙ SUY hơn PHÙ THỊNH. Tài trí, vị tha, can đảm, "
            "dấn thân.' → Đúng cách anh build YI-Chronos: phù suy (sách cổ đang mất), không phù thịnh.\n\n"
            "**Cross-link Iron Rule #7**: Bảo vệ thành quả tích lũy (PBC bình hào 6 Thái cảnh báo 'thành "
            "sao khó, bại sao dễ'). Áp dụng cho project + cả Git workflow."
        )

    return (
        f"## Tổng hợp THỂ - DỤNG\n\n"
        f"**Tiền Thiên {tt}** (THỂ - bản chất tổng quát) **+ Hậu Thiên {ht}** (DỤNG - vận hành thực tế).\n\n"
        f"Hai quẻ kết hợp tạo paradigm xuyên suốt đời người: Thể cho biết ANH LÀ AI, Dụng cho biết "
        f"ANH VẬN HÀNH THẾ NÀO. Luận giải đầy đủ cho từng quẻ xem hai section trên."
    )
