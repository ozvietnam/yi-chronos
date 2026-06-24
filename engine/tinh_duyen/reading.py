"""read_tinh_duyen — engine DETERMINISTIC xem tình duyên NỮ MỆNH.

Đây là engine MỞ RỘNG (không lặp lại) engine con
`engine.cross_paradigm.hon_nhan_song_phai.luan_hon_nhan_song_phai`:
- engine con cho FOUNDATION v0 (12 khía cạnh, lead_reading có thể '(unsourced)')
- engine NÀY tự LÀM GIÀU từ kho tri thức 6 JSON (đó là giá trị chính):
  personality theo Mệnh chính tinh, cung Phu Thê Tử Vi grounded _nguon,
  Bát Tự hôn nhân (官杀 + 日支 + đào hoa), reconcile 8 chủ đề, cách cục,
  định thời mức đại-vận, life-stage theo tuổi.

PARADIGM (Iron Rule #4/#6/#8): KHÔNG BÓI — đọc đồng dạng, mệnh là động từ.
KHÔNG gọi LLM (sage narrate sau). KHÔNG phán 'sẽ ly hôn / số cô quả';
định thời diễn đạt 'năm cần giữ gìn'. Mọi luận điểm bám _nguon từ kho tri thức.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from engine.bat_tu.cast import cast_bat_tu
from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
from engine.hermes_guard import paradigm_violations
from engine.tu_vi.from_birth import cast_la_so_from_birth

from . import gender_lens as GL
from . import knowledge_loader as kb
from .cau_hoi_router import tra_loi_cau_hoi_tuoi
from .cham_cap import cham_cap_do
from .quy_trinh import build_quy_trinh_day_du

METHOD_ID = "tinh_duyen_nu_menh_v1"

_DISCLAIMER = (
    "Engine đọc đồng dạng — KHÔNG bói, KHÔNG phán định mệnh. "
    "Lá số/bát tự cho biết TÍNH (nguyên liệu trời ban); 'mệnh' là việc XỬ LÝ tính đó "
    "(mệnh là động từ — Iron Rule #8). Các mốc 'định thời' chỉ là 'năm khí được kích hoạt' "
    "hoặc 'năm cần giữ gìn', KHÔNG phải lời tiên tri."
)

# 12 địa chi theo thứ tự index 0..11 (Tý ở 0).
_BRANCHES = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
]

# 官杀 = sao chồng ở nữ mệnh.
_QUAN_SAT = ("Chính Quan", "Thất Sát")

# Đào hoa cát (kích hoạt hỉ sự) dùng cho định thời.
_DAO_HOA_KICH_HOAT = ("Hồng Loan", "Thiên Hỉ")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_nu(gender: str) -> bool:
    """True nếu giới tính là NỮ (engine mặc định nữ mệnh)."""
    g = (gender or "").strip().lower()
    return g in ("nữ", "nu", "female", "f", "")


def _parse_birth(birth_datetime_local: str) -> datetime:
    """Parse 'YYYY-MM-DDTHH:MM' (cho phép thiếu phút / có giây)."""
    s = birth_datetime_local.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Fallback: chỉ lấy phần ngày.
    return datetime.strptime(s[:10], "%Y-%m-%d")


def _thieu_gio_sinh(birth_datetime_local: str) -> bool:
    """True nếu input KHÔNG mang thành phần giờ (chỉ ngày) → cung phụ thuộc giờ
    tính theo giờ Tý mặc định, độ tin cậy thấp."""
    return "T" not in birth_datetime_local and ":" not in birth_datetime_local


def _calc_age(birth: datetime, as_of_year: Optional[int]) -> int:
    """Tuổi (mụ-độc-lập, theo năm dương) tại as_of_year (mặc định năm hiện tại)."""
    year = as_of_year if as_of_year else datetime.now().year
    age = year - birth.year
    # Nếu chưa tới sinh nhật trong năm tham chiếu thì trừ 1 (xấp xỉ tuổi thật).
    if as_of_year is None:
        today = datetime.now()
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
    return max(age, 0)


def _stars_at(index_map: dict, branch_index: int) -> list[str]:
    """Các sao (key) có branch_index == branch_index."""
    return [s for s, i in index_map.items() if i == branch_index]


def _opposite(branch_index: int) -> int:
    return (branch_index + 6) % 12


# Nhóm sao trên lá số chứa {tên_sao: branch_index} (để tra vị trí 1 sao).
_STAR_GROUPS = ("chinh_tinh", "phu_tinh", "sao_q2", "sat_tinh", "sao_le")


def _star_index(la_so: dict, star: str) -> Optional[int]:
    """Tra branch_index của 1 sao trên TẤT CẢ nhóm (chinh + phụ + q2 + sát + lẻ).

    Tứ Hóa thường rơi vào PHỤ TINH (Tả/Hữu/Xương/Khúc) — không chỉ ở chinh_tinh.
    """
    if not star:
        return None
    for grp in _STAR_GROUPS:
        g = la_so.get(grp)
        if isinstance(g, dict) and star in g:
            return g[star]
    return None


# Từ khoá kết án đạo đức / phán định mệnh trong lời cổ — engine KHÔNG surface raw,
# phải reframe sang ngôn ngữ đọc-đồng-dạng (Iron Rule #4/#6/#8).
_KEYWORDS_KET_AN = (
    "dâm", "xướng", "kỹ nữ", "kỹ", "hạ tiện", "tiện", "làm lẽ", "thiếp", "hầu",
    "tôi tớ", "tớ", "phân ly", "cô độc", "cô đơn", "cô khắc", "cô quả",
    "khắc chồng", "khắc phu", "khắc tử", "sát phu", "mưu hại", "góa", "quả phụ",
    "bất hài", "ngoài giá thú", "lận đận", "bần", "nghèo hèn",
)

# Câu phú rõ ràng góc nhìn NAM (vô nghĩa/sai cho nữ mệnh) → loại khỏi output nữ.
_KEYWORDS_NAM_PHU = ("thê tài", "đắc thê", "thê hiền", "vượng thê", "thê thiếp")


# --------------------------------------------------------------------------- #
# HÀNG RÀO CỨNG — 2 TẦNG: kết-án vô-giá-trị (LUÔN chặn) + khái-niệm-phân-tích
# --------------------------------------------------------------------------- #
# Iron Rule #4/#6/#8 + CLAUDE.md. Sửa 2026-06-25 sau khi phát hiện hàng rào thô
# (substring) XÓA TRẮNG cả bước phân tích Thương Quan: tên bước "3. Thương Quan
# (gốc khắc phu)" + toàn bộ luận bị thay placeholder → mất phân tích quan trọng nhất.
#
# TẦNG (a) — KẾT ÁN ĐẠO ĐỨC vô giá trị phân tích: LUÔN chặn (substring), vì đây là
# lời sỉ nhục/kết án thời phong kiến, không mang nội dung mệnh-lý gì để giữ.
_FORBIDDEN_CONDEMNATION = (
    "làm gái", "dâm xướng", "dâm tiện", "dâm đãng", "kỹ nữ",
    "làm thiếp", "làm lẽ", "hạ tiện", "mưu hại",
    "đắc thê tài", "thê hiền",
)

# TẦNG (b) — KHÁI NIỆM PHÂN TÍCH ('khắc phu/khắc chồng/sát phu/khắc tử/hình phu/
# khắc quan'): KHÔNG hard-block nữa. Đây là thuật ngữ Tử Bình (伤官见官) cần để
# luận thật. Chỉ chặn KHI ở ngữ cảnh LỜI-PHÁN-VÀO-NGƯỜI (chủ ngữ-người + giọng
# phán) — việc đó để engine.hermes_guard.paradigm_violations (đã tinh chỉnh
# context-aware 2026-06-25) bắt. Liệt kê ở đây chỉ để tài liệu hoá ý đồ.
_ANALYTIC_CONCEPTS = (
    "khắc phu", "khắc chồng", "sát phu", "khắc tử", "hình phu", "khắc quan",
)

# Bản trung tính thay thế khi một string surface vi phạm (paradigm-safe).
_SCRUB_REPLACEMENT = (
    "[lời cổ mang sắc thái kết án thời phong kiến đã được lược — đọc đồng dạng: "
    "đây là một TÍNH (cấu trúc khí), không phải bản án; cấu trúc này VẬN HÀNH tốt "
    "nhất khi được ý thức và chăm sóc (Iron Rule #8)]"
)


# Khung PHỦ ĐỊNH / BIỆN-CHÍNH: khi cụm cấm nằm SAU 1 dấu hiệu bác-bỏ trong cùng câu
# ('KHÔNG phán ...', 'không phải số ...', 'cấm ...', 'bác bỏ ...', 'KHÔNG: "..."'),
# string là LỜI DẶN / BIỆN CHÍNH (Iron Rule #5 — tiếc dê tiếc lễ: giữ nguyên văn cổ
# kèm bác bỏ), KHÔNG phải verdict phán-vào-người → KHÔNG scrub.
# CHỈ những marker BÁC-BỎ rõ ràng (đứng đầu mệnh đề phủ định verdict). KHÔNG gồm
# 'tránh'/'thay vì' trơ vì chúng có thể nằm trong câu củng cố verdict ('không tránh
# được'). Mục tiêu: miễn scrub cho disclaimer/biện-chính, KHÔNG miễn cho verdict trá hình.
_PROHIBITION_MARKERS = (
    "không phán", "không phải", "không nói", "không đọc thành", "không có",
    "không nghĩa", "không bao giờ", "không kết án", "không được",
    "cấm ", "đừng ", "bác bỏ", "biện chính", "không: ", "không:'",
    "tuyệt đối không", "phải tránh", "đề phòng",
)


def _in_prohibition_frame(low: str) -> bool:
    """True nếu string mang dấu hiệu rõ ràng là LỜI DẶN/BIỆN-CHÍNH (bác bỏ verdict),
    chứ không phải phát ngôn verdict. Dùng để miễn scrub cho disclaimer/guidance."""
    return any(m in low for m in _PROHIBITION_MARKERS)


def _has_forbidden(text: str) -> bool:
    """True nếu text vi phạm hàng rào cứng cuối:
      (a) chứa cụm KẾT ÁN đạo đức vô giá trị (LUÔN chặn), HOẶC
      (b) dính giọng TIÊN TRI / lời-phán-vào-người (paradigm_violations —
          context-aware: 'khắc phu' khái-niệm KHÔNG dính, 'em sẽ khắc chồng' dính).

    NGOẠI LỆ (sửa 2026-06-25): nếu string nằm trong KHUNG PHỦ ĐỊNH/BIỆN-CHÍNH
    ('KHÔNG phán …', 'không phải số …', 'bác bỏ …') thì đây là LỜI DẶN dạy engine/
    sage KHÔNG được nói verdict — KHÔNG scrub (nếu không, disclaimer tự huỷ chính nó,
    đúng class bug đã xoá trắng bước Thương Quan).
    """
    if not text:
        return False
    low = text.lower()
    in_frame = _in_prohibition_frame(low)
    if any(v in low for v in _FORBIDDEN_CONDEMNATION):
        # Kết án đạo đức: chỉ miễn khi rõ là biện-chính bác bỏ; ngược lại LUÔN chặn.
        if not in_frame:
            return True
    # Tầng 2: hermes_guard bắt giọng tiên tri + lời-phán-vào-người (đã context-aware
    # nên KHÔNG xoá nhầm khái niệm phân tích trung tính 'Thương Quan khắc Quan').
    if paradigm_violations(text) and not in_frame:
        return True
    return False


def _scrub(text: str) -> str:
    """Quét 1 string: nếu chứa BẤT KỲ từ cấm nào thì thay bằng bản trung tính,
    ngược lại trả nguyên. Đây là primitive lá của hàng rào cứng."""
    if isinstance(text, str) and _has_forbidden(text):
        return _SCRUB_REPLACEMENT
    return text


def _scrub_tree(obj: Any, counter: list[int]) -> Any:
    """Đệ quy qua dict/list/str, áp _scrub lên MỌI string lá.
    counter[0] += số string bị thay thế (cờ caution)."""
    if isinstance(obj, str):
        scrubbed = _scrub(obj)
        if scrubbed is not obj and scrubbed != obj:
            counter[0] += 1
        return scrubbed
    if isinstance(obj, dict):
        return {k: _scrub_tree(v, counter) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_scrub_tree(v, counter) for v in obj]
    return obj


def _apply_gender_tree(obj: Any, gender: str) -> Any:
    """Đệ quy đảo từ-vựng giới (GL.apply_gender) lên MỌI string lá của 1 block.

    CHỈ áp cho NAM (nữ flagship trả nguyên văn). Dùng cho các block MÔ TẢ PHỐI NGẪU
    (cung Phu Thê Tử Vi, batu_hon_nhan, personality.cach_yeu…) nơi text là ngữ cảnh
    DANH TỪ phối ngẫu — KHÔNG chứa động từ 'chồng' (chất đống). Với block có verb-trap
    (vd tuvi 12 bước 'xếp lên lưu niên') đã xử lý riêng tại nguồn.
    """
    if GL.is_female(gender):
        return obj
    if isinstance(obj, str):
        return GL.apply_gender(obj, "nam")
    if isinstance(obj, dict):
        return {k: _apply_gender_tree(v, gender) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_apply_gender_tree(v, gender) for v in obj]
    return obj


def _count_quan_sat(thap_than_distribution: dict) -> dict:
    """Đếm 官杀 (Chính Quan + Thất Sát) từ visible + hidden."""
    visible = thap_than_distribution.get("visible", {}) or {}
    hidden = thap_than_distribution.get("hidden", {}) or {}
    out = {}
    total = 0
    for name in _QUAN_SAT:
        v = int(visible.get(name, 0))
        h = int(hidden.get(name, 0))
        out[name] = {"visible": v, "hidden": h, "total": v + h}
        total += v + h
    out["tong_quan_sat"] = total
    return out


# --------------------------------------------------------------------------- #
# (d) STAGE
# --------------------------------------------------------------------------- #
def _pick_stage(age: int) -> dict:
    stages = kb.get("life_stages")["stages"]
    chosen = None
    for st in stages:
        if st["tuoi_min"] <= age <= st["tuoi_max"]:
            chosen = st
            break
    if chosen is None:
        # Ngoài biên: clamp vào chặng đầu/cuối.
        chosen = stages[0] if age < stages[0]["tuoi_min"] else stages[-1]
    return {
        "tuoi": age,
        "chua_du_tuoi": age < stages[0]["tuoi_min"],
        "stage_id": chosen["id"],
        "tuoi_min": chosen["tuoi_min"],
        "tuoi_max": chosen["tuoi_max"],
        "moi_truong": chosen.get("moi_truong"),
        "tam_ly_cot_loi": chosen.get("tam_ly_cot_loi"),
        "cau_hoi_chinh": chosen.get("cau_hoi_chinh"),
        "nhu_cau": chosen.get("nhu_cau"),
        "giong_van": chosen.get("giong_van"),
        "do_sau": chosen.get("do_sau"),
        "goi": chosen.get("goi"),
        "gia_xu_goi_y": chosen.get("gia_xu_goi_y"),
        "_nguon": chosen.get("_nguon"),
    }


# --------------------------------------------------------------------------- #
# (e) PERSONALITY
# --------------------------------------------------------------------------- #
def _personality(menh_chinh_tinh: list[str], nhat_chu: str, thap_than: dict, muon_doi_cung: bool = False) -> dict:
    pdict = kb.get("personality")
    profiles = []
    for star in menh_chinh_tinh:
        key = kb.name_to_key(star)
        entry = pdict.get(key)
        if not entry:
            continue
        profiles.append({
            "sao": star,
            "ten_han": entry.get("ten_han"),
            "khi_chat": entry.get("khi_chat"),
            "cach_yeu": entry.get("cach_yeu"),
            "khau_vi_giao_tiep": entry.get("khau_vi_giao_tiep"),
            "doi_chieu_batu_thap_than": entry.get("doi_chieu_batu_thap_than"),
            "_nguon": entry.get("_nguon"),
        })
    return {
        "menh_chinh_tinh": menh_chinh_tinh,
        "vo_chinh_dieu": muon_doi_cung or len(menh_chinh_tinh) == 0,
        "muon_sao_doi_cung": muon_doi_cung,
        "profiles": profiles,
        "doi_chieu_batu": {
            "nhat_chu": nhat_chu,
            "thap_than_distribution": thap_than,
        },
    }


# --------------------------------------------------------------------------- #
# (f) CUNG PHU THÊ TỬ VI
# --------------------------------------------------------------------------- #
def _cung_phu_the_tuvi(la_so: dict, phu_the_idx: int) -> dict:
    tp = kb.get("tuvi_phuthe")
    chinh_map = tp["chinh_tinh_phu_the"]
    dao_map = tp["dao_hoa_tinh"]
    sat_map = tp["sat_tinh_phu_the"]
    hoa_map = tp["tu_hoa_phu_the"]

    chinh_tinh = _stars_at(la_so["chinh_tinh"], phu_the_idx)
    muon_doi_cung = False
    if not chinh_tinh:
        # Vô chính diệu cung Phu Thê -> mượn sao đối cung (index ±6).
        chinh_tinh = _stars_at(la_so["chinh_tinh"], _opposite(phu_the_idx))
        muon_doi_cung = True

    # sao_phu_q2: TOÀN BỘ sao phụ Q2 toạ cung Phu Thê (gồm cả không-đào-hoa
    # như Thiên Mã/Phượng Các). dao_hoa CHỈ giữ sao thực sự là đào hoa (lọc qua
    # dao_hoa_tinh dict) để không gây hiểu nhầm cho sage/UI.
    sao_phu_q2 = _stars_at(la_so["sao_q2"], phu_the_idx)
    dao_hoa = [s for s in sao_phu_q2 if kb.name_to_key(s) in dao_map]
    sat = _stars_at(la_so["sat_tinh"], phu_the_idx)
    # Tứ Hóa nhập Phu: hoá nào mà sao mang hoá đó toạ cung Phu Thê.
    # Tra trên TẤT CẢ nhóm sao (hoá hay rơi vào phụ tinh Tả/Hữu/Xương/Khúc).
    tu_hoa_nhap_phu = [
        {"hoa": h, "sao": star}
        for h, star in la_so["tu_hoa"].items()
        if _star_index(la_so, star) == phu_the_idx
    ]

    # Ghép tri thức grounded _nguon.
    chinh_tinh_luan = []
    for star in chinh_tinh:
        entry = chinh_map.get(kb.name_to_key(star))
        if entry:
            chinh_tinh_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "tinh_chat_phoi_ngau": entry.get("tinh_chat_phoi_ngau"),
                "cat_hung": entry.get("cat_hung"),
                "dieu_can_chu_y": entry.get("dieu_can_chu_y"),
                "_nguon": entry.get("_nguon"),
            })

    dao_hoa_luan = []
    for star in dao_hoa:
        entry = dao_map.get(kb.name_to_key(star))
        if entry:
            dao_hoa_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "y_nghia_duyen": entry.get("y_nghia_duyen"),
                "_nguon": entry.get("_nguon"),
            })

    sat_luan = []
    for star in sat:
        entry = sat_map.get(kb.name_to_key(star))
        if entry:
            sat_luan.append({
                "sao": star,
                "ten_han": entry.get("ten_han"),
                "y_nghia": entry.get("y_nghia"),
                "_nguon": entry.get("_nguon"),
            })

    # Tứ Hóa nhập Phu -> tra theo hoa_loc/hoa_quyen/hoa_khoa/hoa_ky.
    _hoa_key = {"Lộc": "hoa_loc", "Quyền": "hoa_quyen", "Khoa": "hoa_khoa", "Kỵ": "hoa_ky"}
    tu_hoa_luan = []
    for item in tu_hoa_nhap_phu:
        entry = hoa_map.get(_hoa_key.get(item["hoa"], ""))
        if entry:
            tu_hoa_luan.append({
                "hoa": item["hoa"],
                "sao": item["sao"],
                "ten_han": entry.get("ten_han"),
                "y_nghia": entry.get("y_nghia"),
                "_nguon": entry.get("_nguon"),
            })

    return {
        "phu_the_branch_index": phu_the_idx,
        "phu_the_branch": _BRANCHES[phu_the_idx],
        "muon_sao_doi_cung": muon_doi_cung,
        "chinh_tinh": chinh_tinh,
        "sao_phu_q2": sao_phu_q2,
        "dao_hoa": dao_hoa,
        "sat_tinh": sat,
        "tu_hoa_nhap_phu": tu_hoa_nhap_phu,
        "chinh_tinh_luan": chinh_tinh_luan,
        "dao_hoa_luan": dao_hoa_luan,
        "sat_tinh_luan": sat_luan,
        "tu_hoa_luan": tu_hoa_luan,
    }


# --------------------------------------------------------------------------- #
# (g) BÁT TỰ HÔN NHÂN
# --------------------------------------------------------------------------- #
def _trang_thai_quan_sat(quan_sat_count: dict) -> str:
    """Trả đúng key trong batu_hon_nhan.phu_tinh.trang_thai_quan_sat:
    'vo_quan' | 'nhuoc' | 'vuong' | 'quan_sat_hon_tap'.
    """
    total = quan_sat_count.get("tong_quan_sat", 0)
    if total == 0:
        return "vo_quan"   # 官杀 không hiện
    chinh_quan = quan_sat_count.get("Chính Quan", {}).get("total", 0)
    that_sat = quan_sat_count.get("Thất Sát", {}).get("total", 0)
    # Cả Chính Quan lẫn Thất Sát cùng hiện = 官杀混杂 (hỗn tạp).
    if chinh_quan > 0 and that_sat > 0:
        return "quan_sat_hon_tap"
    if total >= 3:
        return "vuong"
    return "nhuoc"


def _batu_hon_nhan(bat_tu_state: dict, quan_sat_count: dict) -> dict:
    bk = kb.get("batu_hon_nhan")
    day = bat_tu_state["tu_tru"]["pillars"]["day"]
    nhat_chi = day["branch"]
    nhat_chu = bat_tu_state["tu_tru"]["day_master"]["stem"]

    # Trạng thái 官杀.
    trang_thai = _trang_thai_quan_sat(quan_sat_count)
    tt_dict = bk["phu_tinh"].get("trang_thai_quan_sat", {})
    trang_thai_luan = tt_dict.get(trang_thai) or tt_dict.get("nhuoc")

    # 日支 phối ngẫu cung.
    dia_chi_map = bk["phoi_ngau_cung"].get("y_nghia_dia_chi", {})
    phoi_ngau_luan = dia_chi_map.get(nhat_chi)

    # Đào hoa tứ chi (Tý/Mão/Ngọ/Dậu).
    dao_hoa_chi = nhat_chi in ("Tý", "Mão", "Ngọ", "Dậu")

    return {
        "nhat_chu": nhat_chu,
        "nhat_chi": nhat_chi,
        "phu_tinh_la": list(_QUAN_SAT),
        "quan_sat_count": quan_sat_count,
        "trang_thai_quan_sat": trang_thai,
        "trang_thai_luan": trang_thai_luan,
        "phoi_ngau_cung_luan": phoi_ngau_luan,
        "nhat_chi_la_dao_hoa": dao_hoa_chi,
        "to_hop_then_chot": bk.get("to_hop_then_chot"),
        "_nguon": bk["phu_tinh"].get("_nguon_goc"),
    }


# --------------------------------------------------------------------------- #
# (h) RECONCILE
# --------------------------------------------------------------------------- #
def _reconcile(base: dict) -> list[dict]:
    rec = kb.get("reconcile")["chu_de"]
    # KHÔNG ghép base['khia_canh'] vào chu_de theo INDEX: hai taxonomy khác hẳn
    # (12 khía cạnh vs 8 chủ đề) → ghép theo vị trí là vô nghĩa, lệch ngữ nghĩa.
    out = []
    for cd in rec:
        out.append({
            "chu_de": cd.get("chu_de"),
            "tuvi_doc_bang": cd.get("tuvi_doc_bang"),
            "batu_doc_bang": cd.get("batu_doc_bang"),
            "khi_HOI_TU": cd.get("khi_HOI_TU"),
            "khi_DI_BIET": cd.get("khi_DI_BIET"),
            "phai_uu_tien": cd.get("phai_uu_tien"),
            "_nguon": cd.get("_nguon"),
        })
    return out


# --------------------------------------------------------------------------- #
# (i) CÁCH CỤC
# --------------------------------------------------------------------------- #
def _cung_index_by_name(la_so: dict, cung_name: str) -> Optional[int]:
    """Tra branch_index của 1 cung theo tên ('Mệnh', 'Phu Thê', ...)."""
    if cung_name == "Mệnh":
        return la_so["menh_index"]
    for p in la_so["palaces"]:
        if p.get("name") == cung_name:
            return p.get("branch_index")
    return None


def _all_stars_at(la_so: dict, branch_index: int) -> set[str]:
    """Tất cả sao tọa 1 cung — gồm cả phu_tinh (Văn Xương/Khúc/Tả/Hữu/Khôi/Việt)
    và sao_le; nếu thiếu sẽ bỏ sót ~23 cách tham chiếu các sao phụ này.
    """
    found = set()
    for grp in _STAR_GROUPS:
        g = la_so.get(grp, {})
        if isinstance(g, dict):
            found.update(_stars_at(g, branch_index))
    return found


def _co_tu_khoa(*texts: str) -> bool:
    blob = " ".join(t for t in texts if t)
    return any(kw in blob for kw in _KEYWORDS_KET_AN)


def _la_nam_phu(*texts: str) -> bool:
    blob = " ".join(t for t in texts if t)
    return any(kw in blob for kw in _KEYWORDS_NAM_PHU)


# Sát tinh / dấu hiệu hãm → điều kiện phụ để 1-sao-cách HUNG mới được kích hoạt
# (tránh bắn quá rộng: chỉ có mặt 1 sao là gắn 'cô độc/phân ly').
_SAT_TINH_HO_TRO = (
    "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh",
    "Địa Không", "Địa Kiếp", "Thiên Hình",
)


def _cach_cuc(la_so: dict, gender: str = "nữ") -> list[dict]:
    cc = kb.get("cach_cuc")["cach_cuc"]
    phu_the_idx = la_so["palaces"][2]["branch_index"]
    is_nu = _is_nu(gender)
    hits = []
    for c in cc:
        dk = c.get("dieu_kien_phat_hien", {}) or {}
        sao_req = dk.get("sao") or []
        if not sao_req:
            continue

        # LOẠI mục góc nhìn NAM khỏi output NỮ MỆNH (field gioi_tinh trong dict).
        if is_nu and c.get("gioi_tinh") == "nam":
            continue

        cung = dk.get("cung", "Mệnh")
        idx = _cung_index_by_name(la_so, cung)
        if idx is None:
            continue
        present = _all_stars_at(la_so, idx)
        if not all(s in present for s in sao_req):
            continue

        cat_hung = c.get("cat_hung")
        y_nghia = c.get("y_nghia_duyen") or ""   # raw cổ — CHỈ để truy vết, KHÔNG surface
        han_tu = c.get("han_tu") or ""            # raw cổ — CHỈ để truy vết, KHÔNG surface
        bien_chinh = c.get("bien_chinh") or ""    # bản đọc-đồng-dạng — SURFACE field này

        # Lọc phú rõ ràng góc nhìn NAM (vô nghĩa cho nữ mệnh) — phòng dict thiếu
        # gioi_tinh nhưng câu vẫn rõ là góc nhìn nam.
        if is_nu and _la_nam_phu(y_nghia, han_tu):
            continue

        is_judgmental = _co_tu_khoa(y_nghia, han_tu)

        # Cách 1-sao mang nghĩa kết án: yêu cầu thêm điều kiện phụ (có sát tinh /
        # hãm địa tại cung) mới kích hoạt — tránh bắn quá rộng.
        if len(sao_req) == 1 and (cat_hung == "hung" or is_judgmental):
            co_sat = bool(present & set(_SAT_TINH_HO_TRO))
            ham_dia = "hãm" in han_tu or "hãm" in y_nghia
            if not (co_sat or ham_dia):
                continue

        # --- REFRAME paradigm (Iron Rule #4/#6/#8): KHÔNG surface raw lời kết án.
        require_bien_chinh = (cat_hung == "hung") or is_judgmental
        if cat_hung == "hung":
            cat_hung_out = "diem_can_chu_y"
        elif cat_hung == "cat":
            cat_hung_out = "the_manh"
        else:
            cat_hung_out = "trung_tinh"

        # SURFACE = bien_chinh (đã reframe trong dict). Nếu dict thiếu bien_chinh,
        # fallback: với mục an toàn dùng y_nghia, với mục cần biện chính dùng câu
        # vận hành chung — TUYỆT ĐỐI KHÔNG surface raw kết án.
        if bien_chinh:
            doc_dong_dang = bien_chinh
        elif not require_bien_chinh:
            doc_dong_dang = y_nghia
        else:
            doc_dong_dang = (
                "Đây là một TÍNH (cấu trúc khí bẩm phú), KHÔNG phải bản án. "
                "Đọc đồng dạng thì cấu trúc này VẬN HÀNH tốt nhất khi được ý thức "
                "và chăm sóc — mệnh là việc xử lý tính, không phải số phận đã định "
                "(Iron Rule #8)."
            )

        van_hanh = doc_dong_dang if require_bien_chinh else None

        hits.append({
            "ten_cach": c.get("ten_cach"),
            "cung": cung,
            "gioi_tinh": c.get("gioi_tinh", "chung"),
            "uu_tien_phu_the": (idx == phu_the_idx),  # cách ở Phu Thê liên quan hơn
            "sao_khop": sao_req,
            # bien_chinh = field SURFACE chính (đọc đồng dạng).
            "bien_chinh": doc_dong_dang,
            "cat_hung": cat_hung_out,
            "van_hanh": van_hanh,
            "require_bien_chinh": require_bien_chinh,
            # raw cổ KHÔNG surface ra UI; chỉ giữ pointer nguồn để truy vết.
            "_nguon": c.get("_nguon"),
        })
    # Ưu tiên cách ở cung Phu Thê lên đầu (bài toán hôn nhân).
    hits.sort(key=lambda h: not h["uu_tien_phu_the"])
    return hits


# --------------------------------------------------------------------------- #
# (j) ĐỊNH THỜI
# --------------------------------------------------------------------------- #
def _dai_van_hien_tai(la_so: dict, age: int) -> Optional[dict]:
    for dv in la_so.get("dai_van", []):
        if dv.get("start_age", 0) <= age <= dv.get("end_age", 0):
            return dv
    return None


# Tầm hữu dụng đời người cho định thời (tránh báo mốc tuổi 100+).
_DINH_THOI_TUOI_TRAN = 75


def _trong_tam_huu_dung(dv: dict, age: int) -> bool:
    """Chỉ giữ đại vận trong tầm hữu dụng: đã/đang/sắp tới (≤ age+30) và
    bắt đầu trước trần tuổi đời người (~75). Tránh mốc tuổi 100+ vô nghĩa.
    """
    start = dv.get("start_age", 0)
    return start <= age + 30 and start <= _DINH_THOI_TUOI_TRAN


def _dinh_thoi(la_so: dict, age: int, phu_the_idx: int) -> dict:
    tp_dinh = kb.get("tuvi_phuthe").get("dinh_thoi", {})
    dv_hien_tai = _dai_van_hien_tai(la_so, age)
    dai_van = [dv for dv in la_so.get("dai_van", []) if _trong_tam_huu_dung(dv, age)]

    # Năm KÍCH HOẠT (mức đại-vận): đại vận có cung đi qua nơi có Hồng Loan / Thiên Hỉ.
    kich_hoat_sao = {
        s: i for s, i in la_so["sao_q2"].items() if s in _DAO_HOA_KICH_HOAT
    }
    nam_kich_hoat = []
    for dv in dai_van:
        bi = dv.get("branch_index")
        touched = [s for s, i in kich_hoat_sao.items() if i == bi]
        if touched:
            nam_kich_hoat.append({
                "cycle_index": dv.get("cycle_index"),
                "branch": dv.get("branch"),
                "start_age": dv.get("start_age"),
                "end_age": dv.get("end_age"),
                "sao_kich_hoat": touched,
                "dien_dat": "đại vận có khí hỉ sự / duyên được kích hoạt",
            })

    # Năm CẦN GIỮ GÌN (mức đại-vận): đại vận đi qua cung Phu Thê mà nơi đó có
    # Hóa Kỵ nhập hoặc Kình Dương toạ -> năm cần chăm sóc (KHÔNG phán ly hôn).
    # Hóa Kỵ tra trên TẤT CẢ nhóm sao (hoá hay rơi vào phụ tinh).
    ky_star = la_so["tu_hoa"].get("Kỵ")
    ky_idx = _star_index(la_so, ky_star) if ky_star else None
    kinh_idx = la_so["sat_tinh"].get("Kình Dương")
    nam_giu_gin = []
    for dv in dai_van:
        bi = dv.get("branch_index")
        reasons = []
        if bi == phu_the_idx and ky_idx == phu_the_idx:
            reasons.append(f"Hóa Kỵ ({ky_star}) tại cung Phu Thê")
        if bi == phu_the_idx and kinh_idx == phu_the_idx:
            reasons.append("Kình Dương tại cung Phu Thê")
        # CHỈ báo khi có Kỵ/Kình thực sự (không fire chỉ vì index trùng cung Phu Thê).
        if reasons:
            nam_giu_gin.append({
                "cycle_index": dv.get("cycle_index"),
                "branch": dv.get("branch"),
                "start_age": dv.get("start_age"),
                "end_age": dv.get("end_age"),
                "ly_do": reasons,
                "dien_dat": "năm cần GIỮ GÌN / chăm sóc quan hệ (không phải tiên tri ly tán)",
            })

    return {
        "muc_do": "dai_van",
        "dai_van_hien_tai": dv_hien_tai,
        "nam_kich_hoat": nam_kich_hoat,
        "nam_can_giu_gin": nam_giu_gin,
        "phuong_phap": tp_dinh.get("phuong_phap"),
        "bien_chinh_hien_dai": tp_dinh.get("bien_chinh_hien_dai"),
        "_nguon": tp_dinh.get("_ghi_chu"),
    }


# --------------------------------------------------------------------------- #
# (k) NARRATION BRIEF — gộp giọng cho chặng 3 (sage narrate)
# --------------------------------------------------------------------------- #
def _narration_brief(stage: dict, personality: dict, cach_cuc: list[dict]) -> dict:
    """Gộp giọng (stage + Mệnh chính tinh) + cờ must-reframe để sage chỉ đọc 1 brief,
    không phải tự ráp nhiều nguồn → giảm rủi ro narrate sai paradigm.
    """
    nen, tranh = [], []
    for p in personality.get("profiles", []):
        kv = p.get("khau_vi_giao_tiep") or {}
        nen.extend(kv.get("nen", []) or [])
        tranh.extend(kv.get("tranh", []) or [])
    # Khử trùng giữ thứ tự.
    nen = list(dict.fromkeys(nen))
    tranh = list(dict.fromkeys(tranh))

    must_reframe = [
        c["ten_cach"] for c in cach_cuc if c.get("require_bien_chinh")
    ]
    return {
        "giong_uu_tien_stage": stage.get("giong_van"),
        "giong_tu_menh_chinh_tinh": [
            {"sao": p["sao"], "khau_vi": p.get("khau_vi_giao_tiep")}
            for p in personality.get("profiles", [])
        ],
        "uu_tien_giong": (
            "Khi giọng chặng-tuổi và khẩu vị sao xung nhau: ƯU TIÊN giọng CHẶNG TUỔI "
            "(stage.giong_van) làm khung an toàn, dùng khẩu vị sao để tô màu chi tiết."
        ),
        "nen": nen,
        "tranh": tranh,
        "must_reframe_refs": must_reframe,
        "canh_bao_paradigm": (
            "Mọi cách trong must_reframe_refs BẮT BUỘC reframe (đọc đồng dạng, mệnh là "
            "động từ) — KHÔNG đọc nguyên văn lời cổ kết án. KHÔNG phán-vào-người (cấm mọi "
            "lời tiên tri định mệnh hướng thẳng vào chủ thể). Định thời chỉ là 'năm cần "
            "giữ gìn', không phải tiên tri."
        ),
    }


# --------------------------------------------------------------------------- #
# Sources gom lại
# --------------------------------------------------------------------------- #
_SOURCE_META_KEYS = (
    "nguon", "nguon_chinh", "nguon_goc", "nguon_da_dung",
    "_nguon", "sach", "title",
)


def _collect_sources() -> list[str]:
    out = []
    for key in ("tuvi_phuthe", "batu_hon_nhan", "reconcile", "personality",
                "cach_cuc", "life_stages"):
        block = kb.get(key)
        meta = block.get("_meta", {})
        src = None
        for mk in _SOURCE_META_KEYS:
            if meta.get(mk):
                src = meta[mk]
                break
        # batu_hon_nhan: _meta thiếu key nguồn rõ → lấy phu_tinh._nguon_goc.
        if not src and key == "batu_hon_nhan":
            src = block.get("phu_tinh", {}).get("_nguon_goc")
        if isinstance(src, (list, tuple)):
            src = "; ".join(str(x) for x in src)
        out.append(f"{key}: {src}" if src else key)
    return out


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def read_tinh_duyen(
    birth_datetime_local: str,
    gender: str = "nữ",
    timezone: str = "Asia/Ho_Chi_Minh",
    as_of_year: Optional[int] = None,
) -> dict:
    """Đọc tình duyên nữ mệnh — trả DỮ LIỆU CẤU TRÚC (sage narrate sau).

    Args:
        birth_datetime_local: 'YYYY-MM-DDTHH:MM' giờ địa phương.
        gender: mặc định 'nữ' (engine cho nữ mệnh).
        timezone: IANA tz.
        as_of_year: năm tham chiếu để tính tuổi/chặng (None = năm hiện tại).

    Returns:
        dict với các khoá: method_id, input, stage, personality,
        cung_phu_the_tuvi, batu_hon_nhan, song_phai_reconcile, cach_cuc,
        dinh_thoi, narration_brief, quy_trinh_day_du, chan_doan_cap_do,
        base_12_khia_canh, paradigm_ok, sources, _disclaimer.
        (quy_trinh_day_du = {tu_vi_12_buoc, bat_tu_10_buoc, xep_hang_yeu_to,
        tong_hop_kim_tu_thap}; chan_doan_cap_do = {cap_do 1-5, ten_cap,
        do_thay_doi_duoc, phan_loai, tin_hieu_kich_hoat, lo_trinh,
        nguyen_tac_vang, _nguon}; cau_hoi_tuoi = list[{cau_hoi, he_tra_loi,
        tra_loi, can_gieo_que, can_la_so_doi, do_tin, section_nguon, tan_suat}]
        — KEY MỚI, các key cũ giữ nguyên 100%.)
    """
    # (a) Lập lá số + bát tự.
    la_so = cast_la_so_from_birth(
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        gender=gender,
    )
    bat_tu_state = cast_bat_tu(
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        gender=gender,
    )

    # (b) FOUNDATION từ engine con.
    base = luan_hon_nhan_song_phai(bat_tu_state=bat_tu_state, la_so=la_so)

    # (c) Trích xuất chỉ số then chốt.
    phu_the_idx = la_so["palaces"][2]["branch_index"]
    menh_chinh_tinh = _stars_at(la_so["chinh_tinh"], la_so["menh_index"])
    menh_muon_doi_cung = False
    if not menh_chinh_tinh:
        # Vô chính diệu cung Mệnh -> mượn chính tinh đối cung (Thiên Di) đọc tính cách.
        menh_chinh_tinh = _stars_at(la_so["chinh_tinh"], _opposite(la_so["menh_index"]))
        menh_muon_doi_cung = True
    nhat_chu = bat_tu_state["tu_tru"]["day_master"]["stem"]
    quan_sat_count = _count_quan_sat(bat_tu_state.get("thap_than_distribution", {}))

    # (d) STAGE theo tuổi.
    birth = _parse_birth(birth_datetime_local)
    age = _calc_age(birth, as_of_year)
    stage = _pick_stage(age)

    # (e) PERSONALITY.
    personality = _personality(
        menh_chinh_tinh, nhat_chu,
        bat_tu_state.get("thap_than_distribution", {}),
        muon_doi_cung=menh_muon_doi_cung,
    )

    # (f) CUNG PHU THÊ TỬ VI.
    cung_phu_the = _cung_phu_the_tuvi(la_so, phu_the_idx)

    # (g) BÁT TỰ HÔN NHÂN.
    batu = _batu_hon_nhan(bat_tu_state, quan_sat_count)

    # (h) RECONCILE 8 chủ đề.
    reconcile = _reconcile(base)

    # (i) CÁCH CỤC.
    cach_cuc = _cach_cuc(la_so, gender=gender)

    # (j) ĐỊNH THỜI.
    dinh_thoi = _dinh_thoi(la_so, age, phu_the_idx)

    # (k) NARRATION BRIEF cho chặng 3.
    narration_brief = _narration_brief(stage, personality, cach_cuc)

    # (l) QUY TRÌNH ĐẦY ĐỦ — gộp 12 bước Tử Vi + 10 bước Bát Tự + xếp hạng yếu tố
    #     theo mức độ ảnh hưởng + tổng hợp kim tự tháp (paradigm động-từ). Tái dùng
    #     la_so + bat_tu_state đã cast ở trên (KHÔNG cast lại). KHÔNG gọi LLM.
    quy_trinh_day_du = build_quy_trinh_day_du(
        la_so=la_so, bat_tu_state=bat_tu_state, gender=gender, as_of_year=as_of_year,
    )

    # (m) CHẨN ĐOÁN CẤP ĐỘ — đọc factor từ quy_trinh + áp cham_cap_do.json → CẤP
    #     1-5 + lộ trình. Ngôn ngữ XÂY DỰNG (gọi tên độ khó như khái niệm + chấm cấp
    #     + chỉ lối), KHÔNG phán-vào-người. KEY MỚI 'chan_doan_cap_do' — GIỮ mọi key cũ.
    chan_doan_cap_do = cham_cap_do(
        quy_trinh_day_du=quy_trinh_day_du,
        la_so=la_so,
        bat_tu_state=bat_tu_state,
        gender=gender,
    )

    # --- LĂNG KÍNH GIỚI (gender_lens) cho NAM: đảo từ-vựng phối ngẫu (chồng→vợ, sao
    # chồng→sao vợ, khắc phu→khắc thê, 官杀→财) trên các block MÔ TẢ PHỐI NGẪU. Nữ
    # (flagship) giữ nguyên. quy_trinh_day_du + chan_doan_cap_do ĐÃ giới-tính-hoá ở
    # engine con (tuvi/batu_process + cham_cap) → KHÔNG áp lại tránh double-transform.
    if GL.is_male(gender):
        cung_phu_the = _apply_gender_tree(cung_phu_the, gender)
        batu = _apply_gender_tree(batu, gender)
        personality = _apply_gender_tree(personality, gender)
        reconcile = _apply_gender_tree(reconcile, gender)
        cach_cuc = _apply_gender_tree(cach_cuc, gender)
        dinh_thoi = _apply_gender_tree(dinh_thoi, gender)
        narration_brief = _apply_gender_tree(narration_brief, gender)

    # --- HÀNG RÀO CỨNG CUỐI CÙNG (defense-in-depth): scrub MỌI string surface.
    # Áp lên TẤT CẢ block đưa ra ngoài (cach_cuc, cung_phu_the_tuvi, batu,
    # personality, reconcile, stage, dinh_thoi, narration_brief, base). Nếu BẤT
    # KỲ string nào còn chứa từ cấm → thay bằng bản trung tính + bật cờ caution.
    _n = [0]
    stage = _scrub_tree(stage, _n)
    personality = _scrub_tree(personality, _n)
    cung_phu_the = _scrub_tree(cung_phu_the, _n)
    batu = _scrub_tree(batu, _n)
    reconcile = _scrub_tree(reconcile, _n)
    cach_cuc = _scrub_tree(cach_cuc, _n)
    dinh_thoi = _scrub_tree(dinh_thoi, _n)
    narration_brief = _scrub_tree(narration_brief, _n)
    _base_kc = base.get("khia_canh", [])
    if GL.is_male(gender):
        _base_kc = _apply_gender_tree(_base_kc, gender)
    base_khia_canh = _scrub_tree(_base_kc, _n)
    # Hàng rào cứng áp luôn lên DỮ LIỆU MỚI (12+10 bước + xếp hạng + tổng hợp).
    quy_trinh_day_du = _scrub_tree(quy_trinh_day_du, _n)
    # Hàng rào cứng áp luôn lên CHẨN ĐOÁN CẤP ĐỘ (lộ trình + nguyên tắc vàng).
    chan_doan_cap_do = _scrub_tree(chan_doan_cap_do, _n)

    # (n) CÂU HỎI THEO TUỔI — rút câu trả lời cho bộ câu hỏi TOP của nhóm tuổi từ
    #     các block ĐÃ SCRUB ở trên (KHÔNG bịa luận mới). Câu QUYẾT ĐỊNH nhị nguyên
    #     → flag gieo quẻ Mai Hoa; câu cần lá số người kia → flag so-sánh-duyên.
    #     KEY MỚI 'cau_hoi_tuoi' — GIỮ mọi key cũ + API.
    _reading_for_router = {
        "input": {"tuoi": age, "gio_sinh_thieu": _thieu_gio_sinh(birth_datetime_local)},
        "stage": stage,
        "personality": personality,
        "cung_phu_the_tuvi": cung_phu_the,
        "batu_hon_nhan": batu,
        "song_phai_reconcile": reconcile,
        "cach_cuc": cach_cuc,
        "dinh_thoi": dinh_thoi,
        "quy_trinh_day_du": quy_trinh_day_du,
        "chan_doan_cap_do": chan_doan_cap_do,
    }
    # router ĐÃ scrub field 'tra_loi' (text tự ráp). KHÔNG _scrub_tree cả list ở đây:
    # field 'cau_hoi' là CHÍNH câu hỏi của user (vd 'Tôi có khắc chồng không?') — đây là
    # khái-niệm-phân-tích hợp lệ, KHÔNG được thay placeholder (nếu không UI hiển thị câu
    # hỏi thành '[lời cổ … đã được lược]'). Chỉ scrub field 'tra_loi' (defense-in-depth).
    cau_hoi_tuoi = tra_loi_cau_hoi_tuoi(_reading_for_router, age=age, gender=gender)
    for _item in cau_hoi_tuoi:
        _item["tra_loi"] = _scrub_tree(_item.get("tra_loi"), _n)
    scrubbed_count = _n[0]

    return {
        "method_id": METHOD_ID,
        "input": {
            "birth_datetime_local": birth_datetime_local,
            "gender": gender,
            "timezone": timezone,
            "as_of_year": as_of_year,
            "tuoi": age,
            "gio_sinh_thieu": _thieu_gio_sinh(birth_datetime_local),
            "menh_branch": la_so.get("menh_branch"),
            "phu_the_branch": _BRANCHES[phu_the_idx],
        },
        "stage": stage,
        "personality": personality,
        "cung_phu_the_tuvi": cung_phu_the,
        "batu_hon_nhan": batu,
        "song_phai_reconcile": reconcile,
        "cach_cuc": cach_cuc,
        "dinh_thoi": dinh_thoi,
        "narration_brief": narration_brief,
        # KEY MỚI: quy trình đầy đủ (12 bước Tử Vi + 10 bước Bát Tự + xếp hạng + tổng hợp).
        "quy_trinh_day_du": quy_trinh_day_du,
        # KEY MỚI: chẩn đoán CẤP ĐỘ thử thách (1-5) + lộ trình (ngôn ngữ xây dựng).
        "chan_doan_cap_do": chan_doan_cap_do,
        # KEY MỚI: bộ câu hỏi TOP theo tuổi + câu trả lời rút từ section (paradigm-safe).
        "cau_hoi_tuoi": cau_hoi_tuoi,
        "base_12_khia_canh": base_khia_canh,
        "paradigm_ok": bool(base.get("paradigm_ok", True)),
        # Cờ caution: số string đã bị scrub vì chứa từ cấm (0 = sạch hoàn toàn).
        "scrub_caution_count": scrubbed_count,
        "sources": _collect_sources(),
        "_disclaimer": _DISCLAIMER,
    }


__all__ = ["read_tinh_duyen", "METHOD_ID"]
