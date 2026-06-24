"""Mai Hoa decision helper cho TÌNH DUYÊN nữ mệnh.

gieo_que_tinh_duyen(cau_hoi, seed_numbers=None) -> dict

TÁI DÙNG hạ tầng quẻ ĐÃ KIỂM CHỨNG của hệ (KHÔNG dựng lại 64 quẻ from-scratch):
- core.hexagram        : compose_hexagram_binary / get_hexagram_by_binary / flip_line
                         (bảng King Wen 64 quẻ — Kinh Dịch Trọn Bộ Ngô Tất Tố)
- engine.luc_hao.constants.TRIGRAM_BY_NUMBER : số 1-8 -> (tên quẻ đơn, ngũ hành)
- engine.mai_hoa.the_dung_van_phuong.quan_he_the_dung : quan hệ Thể-Dụng ngũ hành
  (Thiệu Vĩ Hoa p119-128) — ở đây REFRAME sang ngôn ngữ ĐỌC ĐỒNG DẠNG.

PARADIGM (Iron Rule #4 — Mai Hoa = ĐỌC ĐỒNG DẠNG, KHÔNG predict):
- Tổ sư Thiệu Khang Tiết: Mai Hoa là MÔN QUAN-VẬT-TRACE-TÍNH, không phải predict-tool.
  Người và vũ trụ NGANG NHAU (Tam Tài). Khoảnh khắc Anh hỏi phản chiếu cái lớn hơn.
- TUYỆT ĐỐI KHÔNG: "quẻ này cát/hung", "nên/không nên cưới", "sẽ thành/bại".
- PHẢI: "khoảnh khắc Anh hỏi phản chiếu cái gì", "tâm Anh đang ở vị trí nào".
- 4 BƯỚC ĐOÁN QUẺ bắt buộc (Q3 tr.112-114):
    1. Lời quẻ + lời hào (CHỦ) — engine chỉ trỏ TÊN quẻ chính/hỗ/biến + hào động;
       chữ "lời quẻ" để sage/thầy đọc, engine KHÔNG bịa lời.
    2. Thể-Dụng + Ngũ Hành sinh khắc (đọc đồng dạng, KHÔNG cát/hung).
    3. Ngoại ứng (Khắc-Ứng) — engine KHÔNG tự bịa; BẮT BUỘC HỎI user (can_hoi_them).
    4. Tư thế thân thể — BẮT BUỘC HỎI user (can_hoi_them).
- Quy tắc TÂM: "không nghi không bói", "một việc chỉ bói một lần". Engine NHẮC,
  KHÔNG tự gieo lại.

Engine DETERMINISTIC, KHÔNG gọi LLM (lời thầy do sage narrate sau, nếu cần).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from core.hexagram import (
    compose_hexagram_binary,
    flip_line,
    get_hexagram_by_binary,
)
from engine.luc_hao.constants import TRIGRAM_BY_NUMBER
from engine.mai_hoa.the_dung_van_phuong import quan_he_the_dung

METHOD_ID = "mai_hoa_tinh_duyen_quyet_dinh_v1"
SOURCE_REF = (
    "Mai Hoa Dịch Số (图解梅花易数, Quyển 3) — Thiệu Khang Tiết; "
    "Vận Pháp Thi (tr.78) + 4 bước đoán quẻ (tr.112-114) + Tâm Dịch (tr.49,106-107)"
)

# Ngũ hành 8 quẻ đơn (chữ thường) — đồng bộ với the_dung_van_phuong.QUE_NGU_HANH
# nhưng giữ key đúng tên trong TRIGRAM_BY_NUMBER (Càn/Đoài/...).
_TRIGRAM_TO_TDV = {
    "Càn": "Càn", "Đoài": "Đoài", "Ly": "Ly", "Chấn": "Chấn",
    "Tốn": "Tốn", "Khảm": "Khảm", "Cấn": "Cấn", "Khôn": "Khôn",
}

# REFRAME bảng cat_hung của quan_he_the_dung sang ngôn ngữ ĐỌC ĐỒNG DẠNG
# (KHÔNG predict cát/hung — đọc khoảnh khắc phản chiếu TÍNH gì).
_QUAN_HE_DONG_DANG = {
    "Ngang nhau": (
        "Thể và Dụng cùng một khí — khoảnh khắc này phản chiếu một thế CÂN BẰNG: "
        "Anh/Em và việc đang hỏi đứng ngang nhau, không bên nào áp bên nào. "
        "Quan-vật: tâm đang ở thế hoà, hợp để đồng hành hơn là giành phần."
    ),
    "Thể khắc Dụng": (
        "Thể khắc Dụng — khí của Em đang CHỦ ĐỘNG hướng tới việc. Đọc đồng dạng: "
        "đây là lúc tâm Em có lực tự quyết, việc thuận theo ý mình hơn là mình theo việc. "
        "KHÔNG đọc thành 'thắng' — chỉ là TÍNH chủ động đang trội."
    ),
    "Dụng khắc Thể": (
        "Dụng khắc Thể — khí của việc/người đang ÉP lên Em. Quan-vật: khoảnh khắc này "
        "phản chiếu một áp lực ngoại cảnh lớn hơn tâm Em lúc này. Không phải 'điềm xấu' — "
        "là dấu Em cần dưỡng lực, chậm lại, để TÍNH của mình không bị cuốn."
    ),
    "Thể sinh Dụng": (
        "Thể sinh Dụng — Em đang DỐC khí cho việc/người. Đọc đồng dạng: tâm Em đang ở thế "
        "cho đi, vun đắp; hao lực là tự nhiên. Hỏi lại: việc này có xứng để Em dốc tới đâu?"
    ),
    "Dụng sinh Thể": (
        "Dụng sinh Thể — việc/người đang TRỢ lực cho Em. Quan-vật: khoảnh khắc này phản "
        "chiếu một nguồn nâng đỡ đến từ bên ngoài; tâm Em đang ở thế được nhận, được dưỡng."
    ),
    "Khác": (
        "Quan hệ Thể-Dụng trung tính — khoảnh khắc này không nghiêng hẳn về phía nào; "
        "hãy đọc kỹ lời quẻ + ngoại ứng + tư thế thân để trace về TÍNH."
    ),
}


def _norm_seed(seed_numbers: Optional[list[int]]) -> Optional[list[int]]:
    """Chuẩn hoá seed_numbers thành list int dương (>=1). None nếu không hợp lệ."""
    if not seed_numbers:
        return None
    out: list[int] = []
    for n in seed_numbers:
        try:
            v = int(n)
        except (TypeError, ValueError):
            return None
        if v < 1:
            return None
        out.append(v)
    return out or None


def _so_que(value: int) -> int:
    """Map số dương -> 1..8 (Tiên thiên quái số). Dư 0 -> 8."""
    rem = value % 8
    return rem if rem != 0 else 8


def _so_hao(value: int) -> int:
    """Map số dương -> 1..6 (hào động). Dư 0 -> 6."""
    rem = value % 6
    return rem if rem != 0 else 6


def _derive_from_numbers(seed: list[int]) -> tuple[int, int, int, dict]:
    """Mai Hoa TIÊN THIÊN (số) — từ 2-3 số user cho.

    - 2 số: thượng = số 1, hạ = số 2, hào động = (số1+số2) mod 6.
    - 3 số: thượng = số 1, hạ = số 2, hào động = số 3 mod 6.
    - >3 số: gộp dư — dùng 2 số đầu cho thượng/hạ, tổng tất cả cho hào.
    """
    if len(seed) >= 3:
        thuong = _so_que(seed[0])
        ha = _so_que(seed[1])
        hao = _so_hao(seed[2])
        cach = "3-số (thượng=số₁, hạ=số₂, hào=số₃)"
    else:  # len == 2
        thuong = _so_que(seed[0])
        ha = _so_que(seed[1])
        hao = _so_hao(seed[0] + seed[1])
        cach = "2-số (thượng=số₁, hạ=số₂, hào=tổng mod 6)"
    meta = {"phep": "tiên-thiên (số)", "cach_lap": cach, "seed_numbers": seed}
    return thuong, ha, hao, meta


def _derive_from_time(now: datetime) -> tuple[int, int, int, dict]:
    """Mai Hoa THỜI GIAN (NNTT) — đồng pháp với engine.luc_hao.mai_hoa_env.

    Thượng = (năm-chi-số + tháng + ngày) mod 8.
    Hạ     = (năm-chi-số + tháng + ngày + giờ-chi-số) mod 8.
    Hào    = (năm-chi-số + tháng + ngày + giờ-chi-số) mod 6.
    """
    year_num = ((now.year - 1984) % 12) + 1
    month_num = now.month
    day_num = now.day
    hour_num = ((now.hour + 1) // 2) % 12 + 1
    thuong = _so_que(year_num + month_num + day_num)
    ha = _so_que(year_num + month_num + day_num + hour_num)
    hao = _so_hao(year_num + month_num + day_num + hour_num)
    meta = {
        "phep": "thời-gian (NNTT)",
        "cach_lap": "thượng=(chi-năm+tháng+ngày) mod 8; hạ=+giờ; hào=tổng mod 6",
        "moc_thoi_gian": now.strftime("%Y-%m-%d %H:%M"),
        "nam_chi_so": year_num, "thang": month_num, "ngay": day_num, "gio_chi_so": hour_num,
    }
    return thuong, ha, hao, meta


def _hexagram_view(binary: str) -> dict:
    """Gói thông tin 1 quẻ kép (tên VI + King Wen + thượng/hạ + ngũ hành 2 quẻ)."""
    hx = get_hexagram_by_binary(binary)
    return {
        "ten_que": hx.name_vi,
        "ten_que_en": hx.name_en,
        "king_wen_index": hx.king_wen_index,
        "binary": hx.binary,
        "thuong_quai": hx.upper_trigram,
        "ha_quai": hx.lower_trigram,
    }


def _ho_quai_binary(binary: str) -> str:
    """Hỗ quái: thượng = hào [3,4,5], hạ = hào [2,3,4] (Mai Hoa).

    binary top-down: index0=hào6 ... index5=hào1.
    hào i (1..6) -> index 6-i.
    Hỗ thượng = (hào5, hào4, hào3); Hỗ hạ = (hào4, hào3, hào2).
    """
    def bit(hao: int) -> str:
        return binary[6 - hao]
    ho_thuong = bit(5) + bit(4) + bit(3)
    ho_ha = bit(4) + bit(3) + bit(2)
    return ho_thuong + ho_ha


def gieo_que_tinh_duyen(
    cau_hoi: str,
    seed_numbers: Optional[list[int]] = None,
    *,
    now: Optional[datetime] = None,
) -> dict:
    """Gieo 1 quẻ Mai Hoa cho câu hỏi QUYẾT ĐỊNH tình duyên (paradigm đọc đồng dạng).

    Args:
        cau_hoi: câu hỏi quyết định của user (vd 'tôi có nên cưới người này không').
        seed_numbers: 2-3 số tâm-ý user cho (tiên thiên). None -> lập theo thời gian.
        now: override thời gian (test). None -> datetime.now().

    Returns:
        dict {method_id, cau_hoi, lap_que (meta cách lập), quai_so,
              que_chinh, que_ho, que_bien, hao_dong, the_dung,
              bon_buoc (4 bước đoán quẻ), can_hoi_them (ngoại ứng + tư thế),
              tam_phap (quy tắc TÂM), _paradigm, source_ref, _disclaimer}.

    KHÔNG predict. KHÔNG chốt nên/không. Trả CẤU TRÚC quẻ + khung 4 bước để
    thầy/sage đọc đồng dạng cùng user (cần ngoại ứng + tư thế → can_hoi_them).
    """
    cau_hoi = (cau_hoi or "").strip()

    seed = _norm_seed(seed_numbers)
    if seed is not None and len(seed) >= 2:
        thuong, ha, hao_dong, lap_meta = _derive_from_numbers(seed)
    else:
        thuong, ha, hao_dong, lap_meta = _derive_from_time(now or datetime.now())
        if seed is not None:
            lap_meta["ghi_chu_seed"] = (
                "seed_numbers < 2 số hợp lệ → lập theo THỜI GIAN (NNTT)."
            )

    thuong_ten, thuong_nh = TRIGRAM_BY_NUMBER[thuong]
    ha_ten, ha_nh = TRIGRAM_BY_NUMBER[ha]

    # Quẻ chính (chánh) = thượng quái / hạ quái.
    chinh_bin = compose_hexagram_binary(thuong_ten, ha_ten)
    que_chinh = _hexagram_view(chinh_bin)

    # Quẻ hỗ (giữa).
    ho_bin = _ho_quai_binary(chinh_bin)
    que_ho = _hexagram_view(ho_bin)

    # Quẻ biến: lật hào động trên quẻ chính.
    bien_bin = flip_line(chinh_bin, hao_dong)
    que_bien = _hexagram_view(bien_bin)

    # Thể-Dụng: hào động ở quái nào -> quái đó là DỤNG, quái còn lại là THỂ.
    # (Mai Hoa: quái KHÔNG có hào động = Thể; quái CÓ hào động = Dụng.)
    hao_o_thuong = hao_dong in (4, 5, 6)
    if hao_o_thuong:
        the_ten, dung_ten = ha_ten, thuong_ten          # hào ở thượng -> thượng = Dụng
        the_vi_tri, dung_vi_tri = "hạ quái", "thượng quái"
    else:
        the_ten, dung_ten = thuong_ten, ha_ten          # hào ở hạ -> hạ = Dụng
        the_vi_tri, dung_vi_tri = "thượng quái", "hạ quái"

    qh = quan_he_the_dung(_TRIGRAM_TO_TDV[the_ten], _TRIGRAM_TO_TDV[dung_ten])
    quan_he = qh.get("quan_he", "Khác")
    the_dung = {
        "que_the": the_ten,
        "que_the_vi_tri": the_vi_tri,
        "que_dung": dung_ten,
        "que_dung_vi_tri": dung_vi_tri,
        "ngu_hanh_the": qh.get("ngu_hanh_the"),
        "ngu_hanh_dung": qh.get("ngu_hanh_dung"),
        "quan_he": quan_he,
        # REFRAME: KHÔNG surface cat_hung gốc; thay bằng đọc-đồng-dạng.
        "doc_dong_dang": _QUAN_HE_DONG_DANG.get(quan_he, _QUAN_HE_DONG_DANG["Khác"]),
    }

    quai_so = {
        "thuong_quai_so": thuong, "thuong_quai": thuong_ten, "thuong_ngu_hanh": thuong_nh,
        "ha_quai_so": ha, "ha_quai": ha_ten, "ha_ngu_hanh": ha_nh,
        "hao_dong": hao_dong,
    }

    # 4 BƯỚC ĐOÁN QUẺ (Iron Rule #4, Q3 tr.112-114).
    bon_buoc = {
        "buoc_1_loi_que_hao": {
            "ten": "Lời quẻ + lời hào (CHỦ)",
            "que_chinh": que_chinh["ten_que"],
            "que_ho": que_ho["ten_que"],
            "que_bien": que_bien["ten_que"],
            "hao_dong": hao_dong,
            "huong_doc": (
                f"Đọc lời quẻ {que_chinh['ten_que']} làm gốc; hào động thứ {hao_dong} "
                f"là chỗ khoảnh khắc đang CHUYỂN; quẻ hỗ {que_ho['ten_que']} là khí ẩn "
                f"bên trong; quẻ biến {que_bien['ten_que']} là chiều khoảnh khắc đang ngả tới. "
                "Lời quẻ/hào do thầy đọc từ Chu Dịch — engine KHÔNG bịa lời."
            ),
        },
        "buoc_2_the_dung": {
            "ten": "Thể-Dụng + Ngũ Hành (đọc đồng dạng, KHÔNG cát/hung)",
            "the_dung": the_dung,
        },
        "buoc_3_ngoai_ung": {
            "ten": "Ngoại ứng (Khắc-Ứng) — BẮT BUỘC HỎI user",
            "cau_hoi_cho_user": (
                "Lúc Anh/Em nghĩ về việc này, quanh mình có hiện tượng gì bất thường "
                "không? (tiếng động, vật rơi, người/vật xuất hiện, con vật, lời ai vừa nói…)"
            ),
            "ly_do": "Ngoại ứng là một trong 4 bước; engine KHÔNG tự bịa — phải lấy từ user.",
        },
        "buoc_4_tu_the": {
            "ten": "Tư thế thân thể lúc hỏi — BẮT BUỘC HỎI user",
            "cau_hoi_cho_user": "Lúc Anh/Em nghĩ tới việc này, đang NGỒI, ĐỨNG, ĐI, CHẠY hay NẰM?",
            "ly_do": "Tư thế động/tĩnh ảnh hưởng nhịp ứng nghiệm; cần user cung cấp.",
        },
    }

    return {
        "method_id": METHOD_ID,
        "cau_hoi": cau_hoi,
        "lap_que": lap_meta,
        "quai_so": quai_so,
        "que_chinh": que_chinh,
        "que_ho": que_ho,
        "que_bien": que_bien,
        "hao_dong": hao_dong,
        "the_dung": the_dung,
        "bon_buoc": bon_buoc,
        # Hai bước cần HỎI THÊM user (engine không tự bịa) — UI/sage phải hỏi rồi gieo tiếp.
        "can_hoi_them": [
            bon_buoc["buoc_3_ngoai_ung"]["cau_hoi_cho_user"],
            bon_buoc["buoc_4_tu_the"]["cau_hoi_cho_user"],
        ],
        "tam_phap": {
            "khong_nghi_khong_boi": "Không nghi không bói — nếu lòng Em đã rõ thì không cần quẻ.",
            "mot_viec_mot_lan": (
                "Một việc chỉ bói MỘT lần. Gieo lại cùng việc = xúc phạm thần linh "
                "(Q3 tr.49,106-107). Engine KHÔNG tự gieo lại."
            ),
            "mot_cau_mot_que": "Một câu hỏi → một phép → một quẻ.",
        },
        "_paradigm": (
            "Mai Hoa = QUAN-VẬT-TRACE-TÍNH, KHÔNG predict (Iron Rule #4). Quẻ phản chiếu "
            "khoảnh khắc Em hỏi đang ở vị trí nào trong tổng thể — KHÔNG phán cát/hung, "
            "KHÔNG chốt nên/không cưới/chia tay. Quyết định là của Em; quẻ chỉ soi tâm."
        ),
        "source_ref": SOURCE_REF,
        "_disclaimer": (
            "Engine chỉ LẬP quẻ + dựng khung 4 bước (đọc đồng dạng). Bước 3 (ngoại ứng) "
            "và bước 4 (tư thế thân) BẮT BUỘC lấy từ user — chưa có thì luận chưa trọn. "
            "Không bói thay quyết định: quẻ soi tâm, người tự chọn."
        ),
    }


__all__ = ["gieo_que_tinh_duyen", "METHOD_ID", "SOURCE_REF"]
