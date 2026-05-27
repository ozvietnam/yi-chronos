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
                "đại cát' — vận khí có NHIỀU đường để hồi phục khi gặp hung."
            ),
            "life_application": (
                "Anh có 'redundancy' của may mắn: 1 mặt bị hung không có nghĩa toàn "
                "đời hung. Khi 1 hướng tắc, hướng đại cát khác mở."
            ),
        })

    # ─── Insight 10: Cộng hưởng 4 TRỤC Bát Quái ───
    insights.append({
        "id": "4_truc_resonance",
        "title": "🧭 Bốn trục Bát Quái cộng hưởng — bản đồ năng lượng tổng thể",
        "cung": "4 trục (Bắc-Nam, Đông Bắc-Tây Nam, Đông-Tây, Đông Nam-Tây Bắc)",
        "category": "structural",
        "dam_lien_quote": (
            "Lạc Thư 9 cung tổ chức theo 4 trục đối xứng. Trong KMDG truyền thống, "
            "đối xứng = 'Phản Ngâm' nếu xung khắc, 'Hợp Trục' nếu cộng hưởng. "
            "(Đàm Liên Chương II pages 51-53)"
        ),
        "elements": [
            ("Trục Bắc–Nam (Khảm-Ly)", "Hình Cách + Thương môn = 2 HUNG axis (khởi binh + tổn thương)"),
            ("Trục Đông Bắc–Tây Nam (Cấn-Khôn)", "2 Tam Kỳ + Trị Phù = TRỤC CHÍNH cát (tỏa sáng + cứu cấp)"),
            ("Trục Đông–Tây (Chấn-Đoài)", "Thiên Tâm + Thiên Phụ = đại cát kép (học + lập)"),
            ("Trục Đông Nam–Tây Bắc (Tốn-Càn)", "Thiên Bồng + Thiên Anh = 2 HUNG tinh (trục yếu nhất)"),
        ],
        "paradigm": (
            "Bàn anh có 2 TRỤC CÁT MẠNH (Cấn-Khôn = tỏa sáng+cứu cấp; Chấn-Đoài = "
            "học+lập) và 2 TRỤC HUNG (Khảm-Ly = khởi binh+tổn thương; Tốn-Càn = "
            "thủy tặc+cha vắng). Cát/hung trục = 2/2 — cân bằng nhưng các trục có "
            "ý nghĩa KHÁC NHAU."
        ),
        "life_application": (
            "TRỤC CHÍNH của anh: Cấn (Đông Bắc) ↔ Khôn (Tây Nam). Tỏa sáng từ Cấn, "
            "cứu cấp từ Khôn. Đây là 2 hướng anh nên DUY TRÌ vật lý lâu dài "
            "(workspace, đầu giường, hướng làm việc).\n\n"
            "TRỤC THỨ HAI: Chấn (Đông) ↔ Đoài (Tây). Đông để học/chữa lành; Tây để "
            "phù trợ/lập danh. Tránh thấy 2 trục Bắc-Nam và Tốn-Càn là TRỤC YẾU — "
            "không bố trí 'long mạch' ở đó."
        ),
    })

    # ─── Insight 11: Cross-ref Tử Vi (Mệnh Tỵ Hỏa + Mệnh chủ Vũ Khúc Kim) ───
    ly_tinh = tinh.get("Ly", {})
    ly_than = than.get("Ly", {})
    can_mon = mon.get("Càn", {})
    insights.append({
        "id": "cross_ref_tu_vi",
        "title": "🔮 Cross-ref Tử Vi — Mệnh Tỵ Hỏa + Mệnh chủ Vũ Khúc Kim",
        "cung": "Ly (Hỏa) + Càn-Đoài (Kim)",
        "category": "structural",
        "dam_lien_quote": (
            "KMDG và Tử Vi cùng cấu trúc 9 cung Lạc Thư. Tử Vi Mệnh tại cung chi "
            "Hỏa (Tỵ) → KMDG cung Ly (Hỏa) đặc biệt. Mệnh chủ Vũ Khúc (Kim) → "
            "KMDG cung Kim (Càn Tây Bắc + Đoài Tây). Tradition Khang Tiết: 'tam "
            "tài đồng dạng — vũ trụ, người, thời khắc'."
        ),
        "elements": [
            ("Tử Vi Mệnh", "Thiên Đồng tại Tỵ (chi Tỵ = Hỏa)"),
            ("Tử Vi Mệnh chủ", "Vũ Khúc (Kim)"),
            ("KMDG cung Hỏa = Ly", f"{ly_tinh.get('tinh_vn', '?')} + Thương môn + Cửu Thiên (cấu trúc danh tiếng + tổn thương)"),
            ("KMDG cung Kim = Càn", f"Tử môn (đại hung) + Thiên Anh (hung) — KMDG nói KHÔNG cầu danh"),
            ("KMDG cung Kim = Đoài", "Cảnh môn + Thiên Phụ (đại cát) — Tây phù trợ"),
        ],
        "paradigm": (
            "TRÙNG khớp Tử Vi → KMDG: Mệnh Tỵ (Hỏa) ở KMDG = Ly cung (Hỏa) — "
            "Nhật Kỳ + Thương môn + Cửu Thiên = 'danh tiếng qua tranh đấu' (insight #4). "
            "Mệnh chủ Vũ Khúc Kim ở KMDG: 2 cung Kim (Càn + Đoài). Càn bị Tử môn/Thiên "
            "Anh = authority bị tang (insight #5). NHƯNG Đoài là Cảnh môn + Thiên Phụ "
            "(đại cát) → ÁNH SÁNG Kim của anh ở phương TÂY, không Tây Bắc. Vũ Khúc "
            "khai mở qua Đoài (vui đúng + phù trợ), KHÔNG qua Càn (cha vắng)."
        ),
        "life_application": (
            "Khi anh cần KÍCH HOẠT năng lượng Mệnh chủ Vũ Khúc (quyết định cứng + "
            "lãnh đạo): hướng TÂY (Đoài) — không phải Tây Bắc (Càn). Phương Tây có "
            "Thiên Phụ phù trợ + Cảnh môn thi đấu thắng. Phương Tây Bắc có Thiên Anh "
            "+ Tử môn — cố cầu danh phương đó = mệnh chủ bị xung.\n\n"
            "Mệnh Tỵ Hỏa ↔ Ly cung Hỏa: anh thắp sáng qua tranh đấu chính nghĩa "
            "(Thương môn + Cửu Thiên hùng dũng). Đây là CỘNG HƯỞNG Tử Vi-KMDG đặc thù."
        ),
    })

    # ─── Insight 12: Cross-ref Bát Tự (Dụng Mộc + Hỷ Thủy + Kỵ Kim) ───
    chan_tinh = tinh.get("Chấn", {})
    ton_tinh = tinh.get("Tốn", {})
    kham_than = than.get("Khảm", {})
    insights.append({
        "id": "cross_ref_bat_tu",
        "title": "💧🌳 Cross-ref Bát Tự — Dụng Mộc + Hỷ Thủy + Kỵ Kim",
        "cung": "Chấn + Tốn (Mộc) + Khảm (Thủy) + Càn/Đoài (Kim)",
        "category": "structural",
        "dam_lien_quote": (
            "KMDG 9 cung mỗi cung có ngũ hành: Khảm (Thủy), Chấn-Tốn (Mộc), Ly "
            "(Hỏa), Khôn-Cấn-Trung (Thổ), Càn-Đoài (Kim). Bát Tự dụng thần định "
            "hướng nào trong KMDG là 'thuận khí' cho người. Tradition: KMDG dùng "
            "trong context bản mệnh người."
        ),
        "elements": [
            ("Bát Tự Dụng thần", "Mộc (Tỷ Kiếp đồng loại — bổ trợ nhật chủ nhược)"),
            ("Bát Tự Hỷ thần", "Thủy (Ấn — sinh Mộc, dưỡng nhật chủ)"),
            ("Bát Tự Kỵ thần", "Kim (Quan Sát — khắc Mộc, áp lực)"),
            ("KMDG Mộc cung (Chấn)", f"Hưu môn + {chan_tinh.get('tinh_vn', '?')} (đại cát) — CỘNG HƯỞNG dụng thần"),
            ("KMDG Mộc cung (Tốn)", f"Sinh môn + {ton_tinh.get('tinh_vn', '?')} (đại hung paradox)"),
            ("KMDG Thủy cung (Khảm)", f"{kham_than.get('than_vn', '?')} + Hình Cách (Hỷ thần BỊ XUNG)"),
        ],
        "paradigm": (
            "Cross-ref Bát Tự xác nhận:\n"
            "• DỤNG MỘC ↔ KMDG Chấn (Hưu + Thiên Tâm đại cát) = anh nên hướng ĐÔNG cho "
            "y dược + học hành (mở Tỷ Kiếp đồng loại)\n"
            "• DỤNG MỘC ↔ KMDG Tốn (Sinh + Thiên Bồng paradox) = anh cần partner sáng "
            "khi mở Tốn (Đông Nam) — không solo\n"
            "• HỶ THỦY ↔ KMDG Khảm (Hình Cách đại hung) — TRỚ TRÊU: hướng Thủy là HỶ "
            "nhưng cung Khảm BỊ HÌNH CÁCH. Anh không dễ uống Thủy từ phương Bắc.\n"
            "• KỴ KIM ↔ KMDG Càn (Tử + Thiên Anh) — Kỵ thần ở cung HUNG, consistent. "
            "Tây Bắc đáng tránh kép."
        ),
        "life_application": (
            "Thực hành ngũ hành + KMDG kết hợp:\n"
            "• Bổ Dụng Mộc: ngồi face ĐÔNG (Chấn) khi học/chữa lành. Trồng cây phía Đông.\n"
            "• Bổ Hỷ Thủy nhưng tránh Hình Cách Bắc: dùng nước phía ĐÔNG NAM (Tốn — "
            "Thủy-Mộc giao thoa), NOT Bắc. Hoặc đặt bể cá ở Tốn.\n"
            "• Tránh Kỵ Kim: KHÔNG bố trí kim loại lớn ở Tây Bắc (Càn) — sẽ kép áp lực.\n"
            "Trùng khớp 3 chiều (KMDG + Bát Tự + Tử Vi) cho anh: ĐÔNG + ĐÔNG BẮC là "
            "trục tỏa sáng + năng lượng."
        ),
    })

    # ─── Insight 13: Cross-ref Kinh Dịch Bát Thuần ───
    insights.append({
        "id": "cross_ref_kinh_dich",
        "title": "📿 Cross-ref Kinh Dịch — 8 cung KMDG ↔ 8 quẻ Bát Thuần Quái",
        "cung": "Tất cả 8 cung",
        "category": "structural",
        "dam_lien_quote": (
            "KMDG 8 cung gốc từ Bát Quái Hậu Thiên (Kinh Dịch Q1, Q2, Q29, Q30, "
            "Q51, Q52, Q57, Q58 là 8 quẻ thuần). Mỗi cung KMDG = 1 quẻ thuần với "
            "paradigm cốt. Tradition Khang Tiết: 'đọc đồng dạng qua cấu trúc'."
        ),
        "elements": [
            ("Cấn (cung tỏa sáng)", "Q52 Cấn — 'thì chỉ tắc chỉ, thì hành tắc hành' — anh TỎA SÁNG khi BIẾT DỪNG ĐÚNG THỜI"),
            ("Khôn (Trị Phù cứu cấp)", "Q2 Khôn — 'lý sương kiên băng chí' — anh nhạy với 'sương' (dấu hiệu sớm) từ trục cứu cấp"),
            ("Khảm (Hình Cách)", "Q29 Tập Khảm — 'hữu phu, duy tâm hanh' — trong hiểm chỉ tâm thật vượt được"),
            ("Ly (Nhật Kỳ + Thương)", "Q30 Ly — 'hoàng ly nguyên cát' — anh TRUNG (vàng) > CỰC (đỏ) trong danh tiếng"),
            ("Chấn (Đinh + Hưu + Tâm)", "Q51 Chấn — 'bất tang chủy sưởng' — trong sấm vẫn giữ thìa rượu (giữ paradigm)"),
            ("Tốn (paradox Sinh+Bồng)", "Q57 Tốn — 'trùng tốn dĩ thân mệnh' — lệnh phải LẶP, không 1 lần đủ"),
        ],
        "paradigm": (
            "8 quẻ Bát Thuần là FRACTAL của 8 cung KMDG. Đọc đồng dạng (Iron Rule #4):\n"
            "• Cấn Q52 + 2 Tam Kỳ + Khai môn = anh 'dừng để tỏa sáng' — paradox khởi đầu\n"
            "• Khôn Q2 + Trị Phù = anh có 'lý sương' (cảm nhận dấu hiệu sớm) từ trục cứu cấp\n"
            "• Khảm Q29 + Hình Cách = anh phải 'duy tâm hanh' khi gặp khởi binh hung\n"
            "• Ly Q30 + Nhật Kỳ + Thương + Cửu Thiên = anh phải 'hoàng' (trung) không 'hồng' (cực) — "
            "danh tiếng vừa, không khoe"
        ),
        "life_application": (
            "Mỗi cung KMDG có 1 'mantra' Kinh Dịch tương ứng:\n"
            "• Cần TỎA SÁNG → niệm 'thì chỉ tắc chỉ' (Cấn) — biết dừng đúng thời\n"
            "• Cần CỨU CẤP → niệm 'lý sương kiên băng chí' (Khôn) — quan sát dấu hiệu sớm\n"
            "• Trong KHỦNG HOẢNG → niệm 'duy tâm hanh' (Khảm) — chỉ tâm thật vượt được\n"
            "• Khi DANH TIẾNG đến → niệm 'hoàng ly nguyên cát' (Ly) — trung không cực\n"
            "• Critical incident → niệm 'bất tang chủy sưởng' (Chấn) — giữ paradigm\n"
            "• Khi LỆNH/QUYẾT → niệm 'trùng tốn dĩ thân mệnh' (Tốn) — lặp nhiều lần\n"
            "Các câu mantra này KHÔNG mê tín — là PARADIGM REMINDER cho anh tự tu."
        ),
    })

    # ─── Insight 14: Trung cung Quý-Quý ĐÔI ───
    trung_thien = thien.get("Trung", {})
    trung_dia = dia.get("Trung", {})
    if trung_thien.get("can_zh") == "癸" and trung_dia.get("can_zh") == "癸":
        insights.append({
            "id": "trung_cung_quy_doi",
            "title": "💧💧 Trung cung Quý-Quý đôi — trục tinh thần Thủy âm sâu",
            "cung": "Trung cung số 5",
            "category": "structural",
            "dam_lien_quote": (
                "Trung cung là 'gửi vào Khôn số 2' (Đàm Liên page 33) vì 3 tầng "
                "dưới che lấp. Khi Trung cung có CÙNG 1 thiên can trên Thiên + Địa "
                "Bàn → cấu trúc 'gốc' đặc thù. Quý = Thủy âm (Hỷ thần của Bát Tự "
                "anh — Thủy nhuận Mộc dụng)."
            ),
            "elements": [
                ("Trung cung Thiên Bàn", "Quý 癸 (Thủy âm)"),
                ("Trung cung Địa Bàn", "Quý 癸 (Thủy âm)"),
                ("Ngũ hành", "Thủy đôi tại trục — Hỷ thần Bát Tự CỘNG HƯỞNG"),
            ],
            "paradigm": (
                "Quý 癸 Thiên + Quý 癸 Địa cùng Trung cung = trục TINH THẦN Thủy âm "
                "đôi. Trong KMDG, Trung là TRỤC bàn — nơi Thiên Cầm thường trú. "
                "Quý-Quý đôi nghĩa anh có nội tâm SÂU (Thủy âm = ẩn, sâu, dòng "
                "chảy ngầm). Đây là RARE pattern.\n\n"
                "Lực Bát Tự: Hỷ thần Thủy bị 'Hình Cách' chặn ở Khảm (phương Bắc). "
                "NHƯNG Trung cung Quý-Quý cứu — Thủy âm trong nội tâm thay vì "
                "phương Bắc bên ngoài."
            ),
            "life_application": (
                "Anh có TRỤC TINH THẦN nội tâm rất mạnh (Quý-Quý Thủy âm đôi). Đây "
                "là nơi anh tự sinh năng lượng (Hỷ thần tự nhiên). Thực hành:\n"
                "• Meditation/silence MỖI NGÀY — không phải optional, là kích trục\n"
                "• Khi mất hướng: NGỒI YÊN giữa workspace (Trung), KHÔNG đi tìm câu "
                "trả lời bên ngoài. Quý-Quý tự kích.\n"
                "• Đây cũng là gốc 'self-made authority' (Insight #5) — anh không cần "
                "cha bên ngoài vì có Thủy âm nội."
            ),
        })

    # ─── Insight 15: Tỉ lệ Bát thần cát/hung ───
    cat_than_count = sum(1 for c in than.values() if c.get("cat_hung") in {"cát", "đại cát"})
    hung_than_count = sum(1 for c in than.values() if c.get("cat_hung") in {"hung", "đại hung"})
    insights.append({
        "id": "than_ratio",
        "title": f"⚖️ Bát thần: {cat_than_count} cát / {hung_than_count} hung — anh có gì",
        "cung": "(tổng thể)",
        "category": "structural" if cat_than_count == hung_than_count else ("đại cát" if cat_than_count > hung_than_count else "hung"),
        "dam_lien_quote": (
            "8 thần KMDG: Trị Phù + Cửu Thiên + Cửu Địa + Thái Âm + Lục Hợp (5 cát) "
            "vs Đằng Xà + Câu Trần + Chu Tước (3 hung). Tỉ lệ cát/hung BẨM SINH = 5:3. "
            "Nhưng phân bố trong bàn anh có thể khác — Đàm Liên (page 43): 'mỗi cung "
            "có 1 thần đặc thù, đọc đồng dạng theo vị trí'."
        ),
        "elements": [
            ("Cát thần trong bàn", f"{cat_than_count}/5 cát thần (Trị Phù/Cửu Thiên/Cửu Địa/Thái Âm/Lục Hợp)"),
            ("Hung thần trong bàn", f"{hung_than_count}/3 hung thần (Đằng Xà/Câu Trần/Chu Tước)"),
            ("Cát thần tại đâu", ", ".join([f"{c}={t.get('than_vn', '?')}" for c, t in than.items() if t.get("cat_hung") in {"cát", "đại cát"}])),
            ("Hung thần tại đâu", ", ".join([f"{c}={t.get('than_vn', '?')}" for c, t in than.items() if t.get("cat_hung") in {"hung", "đại hung"}])),
        ],
        "paradigm": (
            f"Bàn anh có {cat_than_count} cát thần + {hung_than_count} hung thần trong "
            f"8 cung. Đây là pattern '{'cát ưu' if cat_than_count > hung_than_count else 'hung ưu' if hung_than_count > cat_than_count else 'cân bằng'}'. "
            "Cát thần BẢO VỆ + chỉ hướng; hung thần CẢNH BÁO + làm anh tăng strategic alert."
        ),
        "life_application": (
            f"Cát/hung thần ratio của anh = {cat_than_count}:{hung_than_count}. "
            f"Anh có {'NHIỀU bảo vệ' if cat_than_count > hung_than_count else 'NHIỀU cảnh báo'} hơn. "
            "Trong các quyết định lớn: identify thần ở cung target → cát thần thì DỄ "
            "đi qua, hung thần phải có strategic alert (Câu Trần = đề phòng đánh bất "
            "ngờ, Chu Tước = đề phòng mật thám, Đằng Xà = đề phòng ác mộng/lừa)."
        ),
    })

    # ─── Insight 16: Mang Chủng — sinh ngưỡng tiết khí ───
    if state.get("tiet_khi_zh") == "芒種":
        insights.append({
            "id": "mang_chung_threshold",
            "title": "🌾 Mang Chủng + Dương Cục 9 — sinh ở NGƯỠNG Dương-Âm",
            "cung": "(thời gian)",
            "category": "structural",
            "dam_lien_quote": (
                "Mang Chủng (Tiết) = 'lúa trổ đòng đầy mạch' (~6/6 hàng năm). 17 ngày "
                "sau là Hạ Chí (Trung Khí) — 'nhất âm sinh' (1 hào Âm bắt đầu, theo "
                "lý tiêu trưởng của Dịch). Dương Cục 9 = đỉnh cuối Dương Độn. Cộng "
                "hạ nguyên = cuối cycle 5 ngày. Anh sinh ở 3 lớp 'cuối Dương'."
            ),
            "elements": [
                ("Tiết khí sinh", "Mang Chủng (lúa trổ đòng đầy)"),
                ("Cách Hạ Chí", "~17 ngày (Hạ Chí = nhất âm sinh)"),
                ("Cục", "Dương 9 (đỉnh cuối) — Hạ nguyên (cuối cycle)"),
                ("Cấu trúc", "3 lớp 'cuối Dương' chồng — anh là NGƯỠNG (boundary)"),
            ],
            "paradigm": (
                "Anh sinh tại đỉnh Dương cuối cycle, 17 ngày trước khi 'nhất âm sinh'. "
                "Trong Kinh Dịch (Q24 Phục): 'thất nhật lai phục' — 7 ngày một chu kỳ "
                "âm dương tiêu trưởng. Anh sinh ngay TRƯỚC NGƯỠNG chuyển → bản thân "
                "LÀ ngưỡng = bridge giữa expansion (Dương) và introspection (Âm).\n\n"
                "Tượng Mang Chủng: lúa trổ đòng = giống mới sinh + trưởng thành chuẩn "
                "bị gặt. Anh sinh ra với 'mầm đã ra hoa, đợi thu' — cấu trúc 'lên đỉnh "
                "sớm + thu hoạch dài'."
            ),
            "life_application": (
                "Cấu trúc thời gian anh:\n"
                "• ĐẠT ĐỈNH SỚM (Dương cuối) — anh có expansion energy strong sớm trong đời\n"
                "• CHUẨN BỊ NỘI THU (sắp nhất âm sinh) — sau đỉnh, phải build foundation\n"
                "• ANH LÀ BRIDGE giữa 2 phase — vừa expansion-leader, vừa "
                "introspection-builder\n"
                "• Đời anh có CYCLE 'lên đỉnh → xuống nội thu → lên đỉnh tiếp', không "
                "phải tuyến tính. Đừng sợ giai đoạn 'xuống' — đó là Âm Độn cần thiết."
            ),
        })

    # ─── Insight 17: Trục Đông 3 cung Cấn-Chấn-Tốn HỢP LỰC ───
    if (mon.get("Cấn", {}).get("mon_zh") == "開" and
        mon.get("Chấn", {}).get("mon_zh") == "休" and
        mon.get("Tốn", {}).get("mon_zh") == "生"):
        insights.append({
            "id": "truc_dong_hop_luc",
            "title": "🌅 Trục Đông hợp lực — Khai + Hưu + Sinh (3 cát môn liên kề)",
            "cung": "Cấn (ĐB) + Chấn (Đ) + Tốn (ĐN)",
            "category": "đại cát",
            "dam_lien_quote": (
                "3 cát môn KMDG = Khai (mở đầu), Hưu (sum họp), Sinh (sinh sôi) "
                "(Đàm Liên page 38). 'Theo 3 tránh 5'. Khi 3 CÁT MÔN cùng đặt 3 cung "
                "LIÊN KỀ (Cấn-Chấn-Tốn = 3 cung Đông phía), đây là cấu trúc 'TRỤC "
                "ĐÔNG HỢP LỰC' — hiếm."
            ),
            "elements": [
                ("Cấn (Đông Bắc)", "Khai môn (đại cát) + 2 Tam Kỳ"),
                ("Chấn (Đông)", "Hưu môn (cát) + Thiên Tâm (đại cát) + Tinh Kỳ"),
                ("Tốn (Đông Nam)", "Sinh môn (đại cát) + Cửu Địa (cát)"),
                ("Tổng", "3 cát môn liên kề bao trùm PHÍA ĐÔNG"),
            ],
            "paradigm": (
                "TRỤC ĐÔNG (Cấn + Chấn + Tốn) của anh có CẢ 3 CÁT MÔN. Đây là 'TRỤC "
                "CHÍNH KÍCH HOẠT' của vận khí. Khi đứng ở cung Trung nhìn về phía "
                "Đông, anh thấy: KHAI (mở đường) → HƯU (sum họp) → SINH (sinh sôi) "
                "— trình tự sinh khí hoàn chỉnh.\n\n"
                "Cross-ref Bát Tự: Dụng Mộc + Hỷ Thủy — Mộc ở Chấn/Tốn (phía Đông), "
                "Thủy ở Khảm (phía Bắc, bị Hình Cách chặn). Vậy KÍCH MỘC + né Khảm = "
                "trục Đông là CON ĐƯỜNG tự nhiên."
            ),
            "life_application": (
                "ĐÔNG là hướng VẬN MỆNH của anh. Cụ thể:\n"
                "• Workspace face ĐÔNG (Chấn) — kích Hưu môn + Thiên Tâm\n"
                "• Lớn hơn: mua nhà / xây thì cửa chính hướng ĐÔNG\n"
                "• Du lịch / công tác: ưu tiên phía Đông (TPHCM thay vì Hà Nội?)\n"
                "• Network: kết bạn quý nhân ở phía Đông\n"
                "• Trình tự khởi sự: Cấn (Khai mở dự án) → Chấn (Hưu họp team) → Tốn "
                "(Sinh tăng trưởng) — đi tuần tự, KHÔNG nhảy bước."
            ),
        })

    # ─── Insight 18: Cycle Đại Vận KMDG (9 năm/cycle theo cung) ───
    age = 2026 - 1988
    current_cycle = (age // 9) + 1   # 1-based
    cycle_name_map = {1: "Khảm (Bắc)", 2: "Khôn (Tây Nam)", 3: "Chấn (Đông)",
                      4: "Tốn (Đông Nam)", 5: "Trung", 6: "Càn (Tây Bắc)",
                      7: "Đoài (Tây)", 8: "Cấn (Đông Bắc)", 9: "Ly (Nam)"}
    current_cung = cycle_name_map.get(current_cycle % 9 if current_cycle % 9 else 9, "?")
    next_cycle = current_cycle + 1
    next_cung = cycle_name_map.get(next_cycle % 9 if next_cycle % 9 else 9, "?")
    insights.append({
        "id": "dai_van_cycle",
        "title": f"🔄 Đại Vận KMDG — {age} tuổi (2026), cycle {current_cycle}, hiện ở cung {current_cung}",
        "cung": current_cung,
        "category": "structural",
        "dam_lien_quote": (
            "KMDG có nhiều paradigm cycle: 9 cục/cycle theo tiết khí (60 ngày), 9 năm "
            "= 1 đại vận (theo Lạc Thư 9 cung tuần hoàn). Anh sinh 1988, năm 2026 = "
            f"{age} tuổi → cycle {current_cycle} đang trú cung {current_cung}. "
            "(Tradition vận dụng KMDG cho lưu niên — Đàm Liên Chương II)"
        ),
        "elements": [
            ("Tuổi hiện tại (2026)", f"{age} tuổi"),
            ("Cycle hiện tại", f"{current_cycle} ({age - (current_cycle-1)*9} tuổi trong cycle)"),
            ("Cung trú hiện tại", current_cung),
            ("Cung tiếp theo", f"{next_cung} (từ năm {1988 + current_cycle*9})"),
        ],
        "paradigm": (
            f"Năm 2026 anh đang trú cung {current_cung} trong cycle {current_cycle} "
            f"đại vận KMDG. Cung này có cấu trúc đặc thù trong bàn sinh — đem các "
            f"insight đã đọc về cung {current_cung} áp vào năm hiện tại + năm tiếp "
            f"theo.\n\n"
            f"Đây KHÔNG predict cát/hung 2026, mà là 'context' năng lượng anh đang "
            f"vận. Cung {current_cung} của anh có sao/môn/thần gì → đó là 'tone' của "
            f"đời anh giai đoạn này."
        ),
        "life_application": (
            f"Năm 2026 và giai đoạn sắp tới của anh được color bởi cung "
            f"{current_cung}. Đọc lại insight về cung này (ở phần trên) → "
            f"áp dụng vào quyết định lớn.\n\n"
            f"Khoảng năm {1988 + current_cycle*9} anh sẽ chuyển sang cung "
            f"{next_cung} — chuẩn bị paradigm shift năng lượng."
        ),
    })

    # ─── Insight 19: Cấu trúc fingerprint tổng thể ───
    cat_mon_count = sum(1 for c in mon.values() if c.get("cat_hung") in {"cát", "đại cát"})
    hung_mon_count = sum(1 for c in mon.values() if c.get("cat_hung") in {"hung", "đại hung"})
    cat_tinh_count = sum(1 for c in tinh.values() if c.get("cat_hung") in {"cát", "đại cát"})
    hung_tinh_count = sum(1 for c in tinh.values() if c.get("cat_hung") in {"hung", "đại hung"})
    insights.append({
        "id": "fingerprint_summary",
        "title": "🧬 Fingerprint lá số anh — tổng kết cấu trúc",
        "cung": "(tổng thể)",
        "category": "structural",
        "dam_lien_quote": (
            "Mỗi lá số KMDG = 1 'dấu vân tay' năng lượng độc nhất. Trong KMDG truyền "
            "thống, 4320 bố cục lý thuyết → 1080 thực dụng → 72 canon → 18 cục Địa "
            "Bàn (Đàm Liên Chương II). Mỗi người sinh có 1 trong ~4320 'snapshot' — "
            "đọc đồng dạng = quan-sát fingerprint này."
        ),
        "elements": [
            ("Tỉ lệ Môn", f"{cat_mon_count} cát / {hung_mon_count} hung (canonical: 3 cát / 5 hung)"),
            ("Tỉ lệ Tinh", f"{cat_tinh_count} cát / {hung_tinh_count} hung (canonical: 5 cát / 4 hung)"),
            ("Tỉ lệ Thần", f"{cat_than_count} cát / {hung_than_count} hung (canonical: 5 cát / 3 hung)"),
            ("Cách cục detected", ", ".join({cc.get("name", "?") for cc in state.get("cach_cuc_detected", [])}) or "(none)"),
            ("Tam Kỳ hội tụ", "Cấn (Đông Bắc) — Bính + Ất trùng cung"),
            ("Tổng paradigm CỐT", "Trục Cấn-Khôn cát + trục Khảm-Càn cảnh báo"),
        ],
        "paradigm": (
            "Fingerprint anh có 3 trục năng lượng chính:\n"
            "1. TỎA SÁNG: Cấn (2 Tam Kỳ + Khai) → Ly (Nhật Kỳ + Cửu Thiên)\n"
            "2. CỨU CẤP: Khôn (Trị Phù) → Trung (Quý-Quý nội tâm)\n"
            "3. CẢNH BÁO: Khảm (Hình Cách) + Càn (Tử + Anh) = 2 cung HUNG đối nhau"
        ),
        "life_application": (
            "Tổng kết hành động:\n"
            "• HƯỚNG CHÍNH (luôn ưu tiên): Đông Bắc (Cấn) + Tây Nam (Khôn) + ĐÔNG\n"
            "• HƯỚNG TRÁNH (cảnh báo): Bắc (Khảm) + Tây Bắc (Càn)\n"
            "• THỰC HÀNH TRỤC: ngồi face Đông sáng, cầu cứu Tây Nam khi gấp\n"
            "• PARADIGM MANTRA: 'thì chỉ tắc chỉ' (Cấn) khi cần dừng để tỏa sáng\n"
            "• TRỤC TINH THẦN: Trung cung Quý-Quý = meditation/silence hàng ngày"
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
