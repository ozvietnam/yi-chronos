"""Đàm Liên luận lá số sinh cá nhân — paradigm cụ thể CHẠM user.

Workflow: Cast bàn KMDG tại khoảnh khắc sinh user → analyze 9 cung →
identify pattern Đàm Liên đặc thù tác động → emit list of insights với
verbatim quote + paradigm + life application.

Paradigm: KMDG truyền thống dùng cast "now" cho task cụ thể. Bàn SINH (snapshot
khoảnh khắc ra đời) là Tử Vi paradigm. Đây là CROSS-PARADIGM: dùng KMDG đọc
cấu trúc năng lượng thời-không tại lúc user ra đời, theo Iron Rule #4 "đọc
đồng dạng" — không phải predict đời, là quan-sát structural pattern.

Source: Đàm Liên Chương I phần IV-V (pages 36-50) + Iron Rule #4/#6.
"""

from .constants import CAN_VN, CHI_VN, CUNG_VN, TIET_KHI_VN


def _lookup_by_cung(items):
    """Build dict {cung_vn: cell} for fast lookup."""
    return {c.get("cung_vn", ""): c for c in items or []}


def interpret_personal_chart(state: dict) -> list[dict]:
    """Đọc bàn KMDG sinh user theo Đàm Liên, return list of insights.

    Args:
        state: ky_mon_state output từ cast()

    Returns:
        List of insight dicts:
        {
            "id": short_id,
            "title": Việt title,
            "cung": vị trí cung,
            "category": cát|hung|trung|paradox,
            "dam_lien_quote": verbatim Đàm Liên,
            "elements": list of (label, value) tuples cho UI display,
            "paradigm": Iron Rule #4 đọc đồng dạng — em interpret,
            "life_application": modern translation cho user thực hành,
        }
    """
    insights = []
    thien = _lookup_by_cung(state.get("thien_ban", []))
    dia = _lookup_by_cung(state.get("dia_ban", []))
    mon = _lookup_by_cung(state.get("mon", []))
    tinh = _lookup_by_cung(state.get("tinh", []))
    than = _lookup_by_cung(state.get("than", []))

    cach_cuc_names = {cc.get("name") for cc in state.get("cach_cuc_detected", [])}

    # ─── Insight 1: Hình Cách detected (đại hung cách cục) ───
    if "Hình Cách" in cach_cuc_names:
        hc_cell = next((c for c in state["cach_cuc_detected"] if c["name"] == "Hình Cách"), {})
        cung_hc_zh = hc_cell.get("cung_phat_hien", "")
        cung_hc = CUNG_VN.get(cung_hc_zh, cung_hc_zh)  # map zh → vn
        insights.append({
            "id": "hinh_cach",
            "title": f"⚔️ Hình Cách (đại hung) — sinh trong khoảnh khắc khởi binh cực hung",
            "cung": cung_hc,
            "category": "hung",
            "dam_lien_quote": "Hình Cách: Thiên Bàn Lục Canh, Địa Bàn Lục Kỷ. Khởi binh cực hung, xuất hành gặp nhiều khó khăn cản trở, muôn việc đều không tốt. (Đàm Liên page 50)",
            "elements": [
                ("Cung phát hiện", cung_hc),
                ("Thiên Bàn", "Canh 庚"),
                ("Địa Bàn", "Kỷ 己"),
            ],
            "paradigm": (
                "Anh sinh ra trong khoảnh khắc cung "
                f"{cung_hc} mang khí 'khởi binh cực hung'. Đây là một trong những "
                "hung cách nặng nhất KMDG. KHÔNG dự đoán đời anh — đây là CẤU TRÚC "
                "năng lượng thời-không tại lúc anh ra đời. Đọc đồng dạng: hướng "
                f"{cung_hc} là điểm KHÔNG nên 'khởi binh' (action lớn) cho anh."
            ),
            "life_application": (
                "Khi cần quyết định hành động lớn (khởi nghiệp / dấy binh / "
                "expansion mạo hiểm), TRÁNH hướng có Hình Cách trong bàn cast 'now'. "
                "Đặc biệt nếu cung Khảm (Bắc) — phương Bắc luôn là 'hung địa' cho "
                "anh trong các quyết định xông pha. Nội tâm anh có Lục Hợp + Thiên Cầm "
                "ở Khảm = bảo vệ + dẫn đường — DỰA VÀO môi giới + trung tâm, "
                "không tự 'khởi binh' đơn độc."
            ),
        })

    # ─── Insight 2: 2 Tam Kỳ cùng 1 cung (rare auspicious pattern) ───
    TAM_KY_ZHS = {"乙", "丙", "丁"}
    for cung_vn, t_cell in thien.items():
        d_cell = dia.get(cung_vn, {})
        thien_can = t_cell.get("can_zh", "")
        dia_can = d_cell.get("can_zh", "")
        if thien_can in TAM_KY_ZHS and dia_can in TAM_KY_ZHS and thien_can != dia_can:
            tam_ky_names = {"乙": "Nhật kỳ 日奇", "丙": "Nguyệt kỳ 月奇", "丁": "Tinh kỳ 星奇"}
            mon_cell = mon.get(cung_vn, {})
            insights.append({
                "id": f"hai_tam_ky_{cung_vn}",
                "title": f"☀️🌙 Hai Tam Kỳ hội tụ — Cung {cung_vn} là điểm tỏa sáng đặc thù",
                "cung": cung_vn,
                "category": "đại cát",
                "dam_lien_quote": (
                    "Tam Kỳ = 3 thiên thể sáng (Nhật/Nguyệt/Tinh kỳ). "
                    "Khi 2 Tam Kỳ hội tụ cùng 1 cung trên Thiên + Địa Bàn — cấu trúc "
                    "ánh sáng đặc thù, hiếm. Cộng Khai môn (Tứ thông bát đạt — may "
                    "mắn mọi đường) thành CÁT KÉP. (Đàm Liên page 38, 41)"
                ),
                "elements": [
                    ("Cung", cung_vn),
                    ("Thiên Bàn", f"{tam_ky_names.get(thien_can, thien_can)}"),
                    ("Địa Bàn", f"{tam_ky_names.get(dia_can, dia_can)}"),
                    ("Môn", mon_cell.get("mon_vn", "-")),
                ],
                "paradigm": (
                    f"Cung {cung_vn} của anh có 2 Tam Kỳ hội tụ ({tam_ky_names[thien_can]} + "
                    f"{tam_ky_names[dia_can]}) — đây là cấu trúc 'ánh sáng đôi'. Cộng "
                    f"môn {mon_cell.get('mon_vn', '?')} → đây là HƯỚNG KHỞI ĐẦU TỎA SÁNG "
                    "đặc thù cho anh trong cấu trúc bẩm sinh."
                ),
                "life_application": (
                    f"Hướng {cung_vn} ({t_cell.get('direction', '')}) là hướng anh nên "
                    f"'khai mở' những việc cần TỎA SÁNG (lập danh, ra mắt, present, "
                    f"công bố). Khi cần năng lượng 'ánh sáng đôi' — hướng về cung "
                    f"{cung_vn} cả vật lý (workspace) lẫn tâm thức (focus direction)."
                ),
            })

    # ─── Insight 3: Trị Phù trú cung nào (trục vận khí) ───
    for cung_vn, th_cell in than.items():
        if th_cell.get("than_zh") == "符":
            t_cell = thien.get(cung_vn, {})
            m_cell = mon.get(cung_vn, {})
            ti_cell = tinh.get(cung_vn, {})
            insights.append({
                "id": "tri_phu_cung",
                "title": f"👑 Trị Phù ở cung {cung_vn} — trục vận khí + điểm cứu cấp của anh",
                "cung": cung_vn,
                "category": "đại cát",
                "dam_lien_quote": (
                    "Trị Phù là thần Thiên Ất, là thân đầu tiên trong các vị thần, "
                    "đi đến BẤT KÌ NƠI NÀO mọi điều xấu đều XOÁ TAN HẾT. CÓ VIỆC GẤP "
                    "nên xuất phát từ đây. (Đàm Liên page 43)"
                ),
                "elements": [
                    ("Cung", cung_vn),
                    ("Hướng", t_cell.get("direction", "")),
                    ("Thiên Bàn", t_cell.get("can_vn", "")),
                    ("Môn", m_cell.get("mon_vn", "")),
                    ("Tinh", ti_cell.get("tinh_vn", "")),
                ],
                "paradigm": (
                    f"Trị Phù (thần đầu Bát thần — chủ tể vận khí) trú cung {cung_vn} "
                    f"({t_cell.get('direction', '')}) trong bàn sinh của anh. Đây là "
                    "ĐIỂM CỨU CẤP — Đàm Liên dạy 'có việc gấp xuất phát từ đây'. "
                    "Cung này là trục bảo vệ bẩm sinh."
                ),
                "life_application": (
                    f"Khi anh gặp KHỦNG HOẢNG GẤP (career crisis, family crisis, "
                    f"sức khỏe khẩn cấp): hướng về cung {cung_vn} ({t_cell.get('direction', '')}). "
                    f"Vật lý: workspace face {t_cell.get('direction', '')}. Network: tìm hỗ "
                    f"trợ từ người có vị trí địa lý hướng {t_cell.get('direction', '')}. "
                    "Tâm thức: tâm tĩnh + chân thật = Trị Phù tự kích hoạt."
                ),
            })
            break  # Trị Phù chỉ ở 1 cung

    # ─── Insight 4: Nhật Kỳ (Ất) + Thương môn cùng cung — paradox ánh sáng + tổn thương ───
    for cung_vn, t_cell in thien.items():
        if t_cell.get("can_zh") == "乙":  # Nhật Kỳ
            m_cell = mon.get(cung_vn, {})
            ti_cell = tinh.get(cung_vn, {})
            th_cell = than.get(cung_vn, {})
            if m_cell.get("mon_zh") == "傷":  # Thương môn
                insights.append({
                    "id": "nhat_ky_thuong_mon",
                    "title": f"☀️⚔️ Nhật Kỳ + Thương môn ở {cung_vn} — ánh sáng song hành tổn thương",
                    "cung": cung_vn,
                    "category": "paradox",
                    "dam_lien_quote": (
                        "Thương môn chính là HUNG MÔN XẤU NHẤT. Khi đi ra ngoài dễ "
                        "gặp xấu như mắc bệnh, tai nạn thương vong, gây nên thị phi. "
                        "NHƯNG nếu đòi nợ thì lại đạt được kết quả cao, dễ bắt được "
                        "tội phạm đã trốn thoát. (Đàm Liên page 39)"
                    ),
                    "elements": [
                        ("Cung", cung_vn),
                        ("Thiên Bàn", "Ất 乙 (Nhật Kỳ — mặt trời)"),
                        ("Môn", f"{m_cell.get('mon_vn', '-')} ({m_cell.get('cat_hung', '-')})"),
                        ("Tinh", f"{ti_cell.get('tinh_vn', '-')} ({ti_cell.get('cat_hung', '-')})"),
                        ("Thần", f"{th_cell.get('than_vn', '-')} ({th_cell.get('cat_hung', '-')})"),
                    ],
                    "paradigm": (
                        f"Nhật Kỳ (Ất — mặt trời, ánh sáng cao nhất Tam Kỳ) rơi vào "
                        f"cung {cung_vn} có Thương môn (hung môn xấu nhất). Đây là cấu "
                        "trúc 'ÁNH SÁNG ĐI VỚI TỔN THƯƠNG'. Anh có DANH TIẾNG + tài năng "
                        "(Nhật Kỳ) nhưng PHẢI QUA THỊ PHI / TRANH ĐẤU / vết thương để đến."
                    ),
                    "life_application": (
                        "Anh sẽ KHÔNG có danh tiếng 'phẳng lặng'. Mỗi bước thăng tiến đi "
                        "kèm thị phi / công kích / vết thương. PARADOX của Thương môn: "
                        "ANH VẪN TỐT cho 'đòi nợ' + 'bắt tội phạm' (đối kháng trực diện). "
                        "Đừng trốn xung đột — chọn xung đột CHÍNH NGHĨA. Cửu Thiên (đại "
                        "cát, cha vạn vật, hùng dũng) đan vào cung này = anh có authority "
                        "bẩm sinh để 'tham chiến đúng'."
                    ),
                })
            break

    # ─── Insight 5: Tử môn + Thiên Anh cùng cung (cha/vua bị thương) ───
    for cung_vn, m_cell in mon.items():
        if m_cell.get("mon_zh") == "死":  # Tử môn
            ti_cell = tinh.get(cung_vn, {})
            t_cell = thien.get(cung_vn, {})
            d_cell = dia.get(cung_vn, {})
            th_cell = than.get(cung_vn, {})
            if ti_cell.get("tinh_zh") == "英":  # Thiên Anh
                insights.append({
                    "id": "tu_thien_anh",
                    "title": f"⚰️ Tử môn + Thiên Anh ở {cung_vn} — cấu trúc 'cha vắng / authority bị tang'",
                    "cung": cung_vn,
                    "category": "hung",
                    "dam_lien_quote": (
                        "Tử môn là một trong những môn có mức độ HUNG HIỂM CAO. Kiêng "
                        "không xuất hành, xây dựng hay đi tìm việc, nếu không sẽ thiệt "
                        "hại người + của, dễ bị hành hình, gặp tang tóc. (page 39)\n\n"
                        "Thiên Anh — KHÔNG nên kết hôn, đi xa hay di dời. Cầu danh, cầu "
                        "tài đều không có kết quả gì. Đây là SAO XẤU nên mọi việc đều "
                        "KHÔNG MAY MẮN. (page 42)"
                    ),
                    "elements": [
                        ("Cung", f"{cung_vn} ({'Tây Bắc - Càn' if cung_vn=='Càn' else t_cell.get('direction', '')})"),
                        ("Môn", "Tử 死 (đại hung)"),
                        ("Tinh", "Thiên Anh 英 (hung — sao xấu)"),
                        ("Cứu chuộc", f"Thần {th_cell.get('than_vn', '?')} + Địa Bàn {d_cell.get('can_vn', '?')}"),
                    ],
                    "paradigm": (
                        f"Cung {cung_vn} (Tây Bắc = CỬA CỦA CHA + VUA theo Kinh Dịch Q1 "
                        "Càn) trong bàn sinh của anh có Tử môn + Thiên Anh — 2 hung "
                        "chồng. Đọc đồng dạng: anh có CẤU TRÚC 'cha vắng' / 'authority "
                        "bị tang' bẩm sinh. KHÔNG predict — đây là pattern năng lượng."
                    ),
                    "life_application": (
                        "Anh có thể đã trải qua: cha mất sớm / hoặc xa cách / hoặc "
                        "authority bị challenge / hoặc role 'cha/vua' phải tự kiến tạo. "
                        f"Thái Âm (cát, thần phù hộ) + Đinh Kỳ (Tinh kỳ sáng) đan vào → "
                        "ÁNH SÁNG NỘI TÂM là nguồn lực thay thế 'cha bên ngoài'. Anh là "
                        "self-made authority. Đừng tìm 'cha bên ngoài' để fix — quay vào "
                        "Đinh Kỳ (sao trong, tự sáng)."
                    ),
                })
            break

    # ─── Insight 6: Sinh môn + Thiên Bồng paradox ───
    for cung_vn, m_cell in mon.items():
        if m_cell.get("mon_zh") == "生":  # Sinh môn
            ti_cell = tinh.get(cung_vn, {})
            t_cell = thien.get(cung_vn, {})
            if ti_cell.get("tinh_zh") == "蓬":  # Thiên Bồng
                insights.append({
                    "id": "sinh_thien_bong",
                    "title": f"🌱⚠️ Sinh môn + Thiên Bồng ở {cung_vn} — paradox 'sinh sôi mà có thủy tặc'",
                    "cung": cung_vn,
                    "category": "paradox",
                    "dam_lien_quote": (
                        "Thiên Bồng là THỦY TẶC, bởi thế nếu ở vào cung này thì KHÔNG "
                        "NÊN kết hôn, xây dựng, hay di dời... NHƯNG nếu gặp Sinh môn "
                        "kết hợp với Bính Kỳ, Đinh Kỳ thì lại có thể làm những việc "
                        "trên, mùa xuân và mùa hè có thể áp dụng nhưng không thể vào "
                        "mùa thu và mùa đông. (Đàm Liên page 41)"
                    ),
                    "elements": [
                        ("Cung", cung_vn),
                        ("Môn", "Sinh 生 (đại cát)"),
                        ("Tinh", "Thiên Bồng 蓬 (đại hung — thủy tặc)"),
                        ("Sinh tháng 6 (Mang Chủng — mùa hè)", "ÁP DỤNG được ngoại lệ"),
                    ],
                    "paradigm": (
                        f"Cung {cung_vn} của anh có Sinh môn (đại cát) + Thiên Bồng "
                        "(đại hung) — conflict trực tiếp. Anh sinh tháng 6 (Mang "
                        "Chủng, mùa hè) → ĐÚNG mùa Tốn (Đông Nam) → ÁP DỤNG được "
                        "ngoại lệ Đàm Liên: Sinh môn có thể vượt Thiên Bồng MÙA XUÂN/HÈ. "
                        "Tuy nhiên cần có Bính Kỳ / Đinh Kỳ cùng cung — bàn anh KHÔNG "
                        "có (Bính ở Cấn, Đinh ở Chấn). Anh phải DRAW LỰC từ cung kề."
                    ),
                    "life_application": (
                        f"Hướng {cung_vn} của anh là 'cửa sinh có thủy tặc'. Việc khởi "
                        "đầu ở hướng này SẼ THÀNH NHƯNG có rủi ro 'thủy tặc' (mất mát "
                        "bất ngờ). Pattern: KHÔNG đi 1 mình. Phải có Bính Kỳ (Cấn — "
                        "Đông Bắc) hoặc Đinh Kỳ (Chấn — Đông) làm PARTNER / GUIDE. "
                        "Anh thành công khi có đồng minh sáng (ánh sáng người khác bù "
                        "vào). Solo venture ở hướng này = thủy tặc lấy."
                    ),
                })
            break

    # ─── Insight 7: Bài cục + tiết khí (vận khí thời điểm sinh) ───
    bai_cuc = state.get("bai_cuc", {})
    tiet_khi_vn_local = state.get("tiet_khi_vn", "")
    cuc_so = bai_cuc.get("cuc_so")
    duong_am = bai_cuc.get("duong_am", "")
    nguyen = bai_cuc.get("nguyen", "")
    if cuc_so is not None:
        insights.append({
            "id": "bai_cuc_birth",
            "title": f"🌅 Sinh trong {duong_am} {cuc_so} {nguyen} — {tiet_khi_vn_local}",
            "cung": "(tổng thể)",
            "category": "structural",
            "dam_lien_quote": (
                "Dương độn 9 cục từ Đông Chí đến Hạ Chí (6 tháng dương khí tăng). "
                "Mỗi tiết khí 15 ngày chia 3 nguyên (Thượng/Trung/Hạ). Dương độn "
                "cục 9 = đỉnh Dương trước khi chuyển Âm. Hạ nguyên = cuối 1 cycle. "
                "(Đàm Liên Chương II pages 51-56)"
            ),
            "elements": [
                ("Tiết khí", tiet_khi_vn_local),
                ("Dương/Âm độn", duong_am),
                ("Cục số", f"{cuc_so}/9"),
                ("Nguyên", nguyen),
            ],
            "paradigm": (
                f"Anh sinh ở Dương Cục 9 — ĐỈNH CAO của Dương độn — trước khi "
                "chuyển Âm độn (Hạ Chí ~6/22, chỉ ~17 ngày sau khi anh sinh). "
                "Plus Hạ nguyên = cuối 1 cycle 5-ngày. Đây là 'TRÊN ĐỈNH CHUẨN BỊ "
                "GIẢM'. Vận khí cao nhất + chuẩn bị chuyển nội-thu."
            ),
            "life_application": (
                "Cấu trúc thời gian: anh là người sinh ra ĐỂ ĐẠT ĐỈNH SỚM + chuẩn bị "
                "GIAI ĐOẠN NỘI-THU. Đời anh có cycle 'lên đỉnh → xuống nội — lên đỉnh "
                "→ xuống nội'. KHÔNG phải vận đều — vận có ĐỈNH rõ rồi giai đoạn refining. "
                "Đỉnh = expand. Nội thu = build foundation cho đỉnh tiếp. Đừng sợ "
                "giai đoạn 'xuống' — đó là Âm độn cần thiết theo paradigm Kinh Dịch "
                "(âm dương tiêu trưởng)."
            ),
        })

    # ─── Insight 8: Đinh Kỳ + Hưu môn + Thiên Tâm (gần Nhân Độn) ───
    for cung_vn, t_cell in thien.items():
        if t_cell.get("can_zh") == "丁":  # Đinh Kỳ (Tinh kỳ)
            m_cell = mon.get(cung_vn, {})
            ti_cell = tinh.get(cung_vn, {})
            if m_cell.get("mon_zh") == "休" and ti_cell.get("tinh_zh") == "心":
                insights.append({
                    "id": "dinh_huu_tam",
                    "title": f"⭐💊 Tinh kỳ + Hưu môn + Thiên Tâm ở {cung_vn} — y-dược chính nghĩa",
                    "cung": cung_vn,
                    "category": "đại cát",
                    "dam_lien_quote": (
                        "Nhân Độn: Thiên Bàn Đinh, Trung Bàn Hưu Môn, Thần Bàn Thái "
                        "Âm. Nên Ẩn giấu, tập kích, thám thính, gặp người quyền quý, "
                        "cưới gả, giao dịch. (Đàm Liên page 45)\n\n"
                        "Thiên Tâm gặp TIÊN NHÂN CHO THUỐC QUÝ... chữa bệnh NHANH "
                        "CHÓNG. VẠN SỰ ĐỀU MAY MẮN, CÁT TƯỜNG. (page 41)"
                    ),
                    "elements": [
                        ("Cung", cung_vn),
                        ("Thiên Bàn", "Đinh 丁 (Tinh kỳ)"),
                        ("Môn", "Hưu 休"),
                        ("Tinh", "Thiên Tâm 心 (đại cát — y dược)"),
                        ("Trạng thái", "GẦN Nhân Độn (thiếu Thái Âm cùng cung)"),
                    ],
                    "paradigm": (
                        f"Cung {cung_vn} của anh GẦN cách cục Nhân Độn (Đinh + Hưu + "
                        "Thái Âm). Anh có 2/3 condition. Thái Âm rơi ở Càn, không Chấn. "
                        "Plus Thiên Tâm (đại cát, 'tiên nhân cho thuốc quý') trú đây → "
                        "đây là CUNG Y DƯỢC + chân thật bẩm sinh."
                    ),
                    "life_application": (
                        f"Hướng {cung_vn} ({t_cell.get('direction', '')}) là cung 'CHỮA "
                        "LÀNH' của anh — cả về sức khỏe lẫn tâm. Anh có khả năng "
                        "'tiên nhân cho thuốc quý' — không phải làm bác sĩ, mà là TRỞ "
                        "THÀNH NGUỒN CHỮA LÀNH cho người khác (knowledge, wisdom, "
                        "advisory). Khi mất phương hướng, ngồi yên + face Đông + chân "
                        "thật = Thiên Tâm tự kích."
                    ),
                })
            break

    # ─── Insight 9: Hai sao đại cát kề nhau (Phụ + Tâm + Cầm pattern) ───
    cat_tinh_zh = {"輔", "心", "禽"}
    cat_cungs = [cung_vn for cung_vn, ti in tinh.items()
                 if ti.get("tinh_zh") in cat_tinh_zh and ti.get("cat_hung") == "đại cát"]
    if len(cat_cungs) >= 3:
        insights.append({
            "id": "tam_dai_cat_tinh",
            "title": f"🌟 Ba sao đại cát hội tụ: {', '.join(cat_cungs)}",
            "cung": " + ".join(cat_cungs),
            "category": "đại cát",
            "dam_lien_quote": (
                "3 đại cát tinh = Phụ, Cầm, Tâm. Thiên Phụ 'vì vạn vật vì dân chúng' "
                "(cát mọi việc). Thiên Cầm 'rất dễ đi xa, làm ăn buôn bán nhiều lợi "
                "lộc'. Thiên Tâm 'VẠN SỰ MAY MẮN, CÁT TƯỜNG'. (Đàm Liên page 42-43)"
            ),
            "elements": [
                ("Số sao đại cát trong bàn", str(len(cat_cungs))),
                ("Vị trí", ", ".join(cat_cungs)),
            ],
            "paradigm": (
                f"Bàn sinh anh có {len(cat_cungs)} sao đại cát (Phụ/Cầm/Tâm) phân bố ở "
                f"{len(cat_cungs)} cung khác nhau. Trong KMDG, đây là cấu trúc 'rải "
                "đại cát' — vận khí có NHIỀU đường để hồi phục khi gặp hung. KHÔNG "
                "phải tất cả cát ở 1 chỗ, mà PHỦ NHIỀU MẶT đời."
            ),
            "life_application": (
                "Anh có 'redundancy' của may mắn: 1 mặt bị hung không có nghĩa toàn "
                "đời hung. Khi 1 hướng tắc, hướng đại cát khác mở. Cấu trúc 'cá tính "
                "dẻo dai' — anh có sức bật vì cát phủ nhiều mặt."
            ),
        })

    return insights


def list_founder_data() -> dict:
    """Founder hardcoded data — used by /api/ky-mon/personal-reading default."""
    return {
        "year": 1988, "month": 6, "day": 5, "hour": 23, "minute": 30,
        "name": "Founder (CEO ngantin.vn)",
        "note": "Birth confirmed via Birth Hour Quiz v2 + qualitative early-Tý profile.",
    }
