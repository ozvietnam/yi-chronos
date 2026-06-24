"""quy_trinh_day_du — TỔNG HỢP quy trình ĐẦY ĐỦ tình duyên nữ mệnh.

Tầng GỘP (synthesis) tái dùng 2 quy trình con đã xây (KHÔNG viết lại lý):
  - engine.tinh_duyen.tuvi_process.doc_tuvi_12_buoc   (12 bước Tử Vi)
  - engine.tinh_duyen.batu_process.doc_batu_10_buoc   (10 bước Bát Tự)

Đầu ra (gắn vào read_tinh_duyen dưới key MỚI `quy_trinh_day_du`):
  {
    "tu_vi_12_buoc":  <output doc_tuvi_12_buoc>,
    "bat_tu_10_buoc": <output doc_batu_10_buoc>,
    "xep_hang_yeu_to": {           # gom 22 bước theo MỨC ĐỘ ẢNH HƯỞNG
        "truc_tiep":  [ {nguon, buoc, ten_buoc, luan_tom}, ... ],
        "gian_tiep":  [ ... ],
        "tiem_an":    [ ... ],
    },
    "tong_hop_kim_tu_thap": "<3-5 câu kim tự tháp, paradigm động-từ>",
  }

PARADIGM (Iron Rule #4/#6/#8): KHÔNG BÓI — đọc đồng dạng, mệnh là ĐỘNG TỪ.
Hai engine con dùng TỪ VỰNG mức-độ KHÁC nhau (Tử Vi: 'trực tiếp/gián tiếp/tiềm ẩn'
có dấu + dấu cách; Bát Tự: 'truc_tiep/gian_tiep/tiem_an' gạch dưới) → tầng này
CHUẨN HOÁ cả hai về 3 bucket {truc_tiep, gian_tiep, tiem_an}.

GROUNDING: mọi luận điểm KẾ THỪA _nguon từ 2 engine con (đã ground sách thật:
tc7.txt = 王亭之 深造講義 + 女命骨髓賦 + Trích Thiên Tủy + Thiệu Vĩ Hoa + Phú Thái Vi
+ wiki passages). Tầng này KHÔNG bịa nguồn mới — chỉ gộp + cân tỉ trọng.
"""
from __future__ import annotations

from typing import Any, Optional

from .tuvi_process import doc_tuvi_12_buoc
from .batu_process import doc_batu_10_buoc

# Chuẩn hoá mọi nhãn mức-độ về 3 bucket canonical (gạch dưới).
_TRUC_TIEP = "truc_tiep"
_GIAN_TIEP = "gian_tiep"
_TIEM_AN = "tiem_an"

# Map mọi biến thể (Tử Vi có dấu/cách · Bát Tự gạch dưới) -> bucket canonical.
_MUC_DO_CANON = {
    "trực tiếp": _TRUC_TIEP, "truc_tiep": _TRUC_TIEP, "truc tiep": _TRUC_TIEP,
    "gián tiếp": _GIAN_TIEP, "gian_tiep": _GIAN_TIEP, "gian tiep": _GIAN_TIEP,
    "tiềm ẩn": _TIEM_AN, "tiem_an": _TIEM_AN, "tiem an": _TIEM_AN,
}

_BUCKET_VI = {
    _TRUC_TIEP: "trực tiếp",
    _GIAN_TIEP: "gián tiếp",
    _TIEM_AN: "tiềm ẩn",
}


def _canon_muc_do(raw: Any) -> str:
    """Đưa nhãn mức-độ thô của một bước về 1 trong 3 bucket canonical.
    Không match → mặc định gián tiếp (an toàn, không thổi phồng lên trực tiếp)."""
    key = str(raw or "").strip().lower()
    return _MUC_DO_CANON.get(key, _GIAN_TIEP)


def _tom_luan(luan: str, limit: int = 160) -> str:
    """Cắt gọn lời luận của 1 bước cho bảng xếp hạng (không phá nguyên văn ở engine con)."""
    s = (luan or "").strip().replace("\n", " ")
    if len(s) <= limit:
        return s
    return s[:limit].rstrip() + "…"


def _xep_hang_yeu_to(tu_vi: dict, bat_tu: dict) -> dict:
    """Gom 22 bước (12 Tử Vi + 10 Bát Tự) thành 3 nhóm theo mức độ ảnh hưởng.

    Mỗi phần tử giữ pointer về NGUỒN bước (engine + tên bước) để truy vết, kèm
    tóm tắt luận. KHÔNG sinh luận điểm mới → không cần ground thêm.
    """
    groups: dict[str, list[dict]] = {_TRUC_TIEP: [], _GIAN_TIEP: [], _TIEM_AN: []}

    for engine_name, payload in (("tu_vi", tu_vi), ("bat_tu", bat_tu)):
        for b in payload.get("buoc", []) or []:
            bucket = _canon_muc_do(b.get("muc_do_anh_huong"))
            groups[bucket].append({
                "nguon_quy_trinh": engine_name,        # 'tu_vi' | 'bat_tu'
                "ten_buoc": b.get("ten_buoc"),
                "luan_tom": _tom_luan(b.get("luan", "")),
                "muc_do_goc": b.get("muc_do_anh_huong"),
                "_nguon": b.get("_nguon"),
            })
    return groups


def _diem_nhan(items: list[dict], n: int = 2) -> list[str]:
    """Lấy tối đa n tên bước tiêu biểu từ 1 nhóm (cho câu tổng hợp)."""
    out = []
    for it in items[:n]:
        ten = (it.get("ten_buoc") or "").strip()
        # bỏ tiền tố số thứ tự '1. ' / '12. ' cho gọn câu văn.
        if ". " in ten[:5]:
            ten = ten.split(". ", 1)[1]
        # bỏ phần mô tả dài sau ' — ' để giữ tên cung/khái niệm.
        ten = ten.split(" — ")[0].split(" (")[0].strip()
        if ten:
            out.append(ten)
    return out


def _tong_hop_kim_tu_thap(
    tu_vi: dict, bat_tu: dict, xep_hang: dict, gender: str
) -> str:
    """Dựng 3-5 câu TỔNG HỢP theo mô hình KIM TỰ THÁP (paradigm động-từ).

    Tỉ trọng: yếu tố TRỰC TIẾP 60-70% · GIÁN TIẾP 20-25% · TIỀM ẨN 10-15%.
    Nêu điểm mạnh / điều cần giữ gìn lớn nhất. KHÔNG bói, mệnh là ĐỘNG TỪ.
    """
    tt = xep_hang.get(_TRUC_TIEP, [])
    gt = xep_hang.get(_GIAN_TIEP, [])
    ta = xep_hang.get(_TIEM_AN, [])

    tt_nhan = _diem_nhan(tt, 2)
    gt_nhan = _diem_nhan(gt, 2)
    ta_nhan = _diem_nhan(ta, 2)

    # Trích vài tín hiệu cốt lõi từ Bát Tự bước 1-2 (sao chồng) để câu mạnh chắc hơn.
    b1 = (bat_tu.get("buoc") or [{}])[0].get("du_lieu", {})
    nhat_chu = b1.get("nhat_chu") or bat_tu.get("input", {}).get("nhat_chu", "")
    pt_chi = tu_vi.get("cung_phu_the_chi", "")

    cau = []

    # Câu 1 — ĐỈNH kim tự tháp: yếu tố TRỰC TIẾP (chiếm 60-70%, quyết định nhất).
    if tt_nhan:
        cau.append(
            f"Cốt lõi (chiếm khoảng 60-70% bức tranh tình duyên) nằm ở các yếu tố "
            f"TRỰC TIẾP: {', '.join(tt_nhan)}"
            + (f" — cung Phu Thê tại {pt_chi}" if pt_chi else "")
            + (f", Nhật chủ {nhat_chu}" if nhat_chu else "")
            + ". Đây là TÍNH (cấu trúc khí bẩm phú), và cấu trúc này VẬN HÀNH tốt nhất "
            "khi được ý thức rõ — không phải bản án (mệnh là động từ)."
        )
    else:
        cau.append(
            "Lá số không nổi bật một yếu tố trực tiếp đơn lẻ nào áp đảo — nghĩa là duyên "
            "phối ngẫu cần được CHỌN và vun chủ động, đây là dư địa cho ý chí (mệnh là động từ)."
        )

    # Câu 2 — TẦNG GIỮA: yếu tố GIÁN TIẾP (20-25%) nâng đỡ / điều tiết.
    if gt_nhan:
        cau.append(
            f"Ở tầng nâng đỡ (khoảng 20-25%) là các yếu tố GIÁN TIẾP: {', '.join(gt_nhan)} "
            "— chúng điều tiết cách cái cốt lõi được thể hiện, là nơi sự chủ động và môi "
            "trường (học vấn, sự nghiệp, các mối quan hệ) có thể làm khí chuyển theo hướng lành."
        )

    # Câu 3 — ĐÁY: yếu tố TIỀM ẨN (10-15%) màu sắc / cần giữ gìn.
    if ta_nhan:
        cau.append(
            f"Ở tầng tiềm ẩn (khoảng 10-15%) là {', '.join(ta_nhan)} — sắc thái phụ và các "
            "mốc 'năm cần giữ gìn'; lưu tâm nhưng KHÔNG để chúng át tầng cốt lõi, và tuyệt "
            "đối không đọc thành lời tiên tri."
        )

    # Câu 4 — ĐIỂM MẠNH lớn nhất + ĐIỀU CẦN GIỮ GÌN (đóng khung động-từ, trao quyền).
    diem_manh = tt_nhan[0] if tt_nhan else (gt_nhan[0] if gt_nhan else "khả năng tự quyết")
    can_giu = ta_nhan[0] if ta_nhan else (gt_nhan[0] if gt_nhan else "sự kiên nhẫn vun đắp")
    cau.append(
        f"Điểm mạnh lớn nhất để dựa vào: {diem_manh}; điều cần giữ gìn nhất: {can_giu}. "
        "Tổng thể đọc theo đồng dạng — đây là nguyên liệu trời ban, còn việc XỬ LÝ nó "
        "(mệnh là động từ) thuộc về chủ thể."
    )

    return " ".join(cau)


def build_quy_trinh_day_du(
    la_so: dict,
    bat_tu_state: dict,
    gender: str = "nữ",
    as_of_year: Optional[int] = None,
) -> dict:
    """Chạy 12 bước Tử Vi + 10 bước Bát Tự rồi gộp thành quy trình đầy đủ.

    Args:
        la_so: lá số đã an sao (cast_la_so_from_birth) — tái dùng, KHÔNG cast lại.
        bat_tu_state: bát tự đã lập (cast_bat_tu) — tái dùng, KHÔNG cast lại.
        gender: 'nữ' (mặc định).
        as_of_year: năm tham chiếu lưu niên / tuổi.

    Returns:
        dict {tu_vi_12_buoc, bat_tu_10_buoc, xep_hang_yeu_to, tong_hop_kim_tu_thap}.
        (Chưa scrub — caller read_tinh_duyen áp _scrub_tree lên toàn bộ.)
    """
    tu_vi = doc_tuvi_12_buoc(la_so, gender=gender, as_of_year=as_of_year)
    bat_tu = doc_batu_10_buoc(bat_tu_state, gender=gender, as_of_year=as_of_year)

    xep_hang = _xep_hang_yeu_to(tu_vi, bat_tu)
    tong_hop = _tong_hop_kim_tu_thap(tu_vi, bat_tu, xep_hang, gender)

    return {
        "tu_vi_12_buoc": tu_vi,
        "bat_tu_10_buoc": bat_tu,
        "xep_hang_yeu_to": xep_hang,
        "tong_hop_kim_tu_thap": tong_hop,
    }


__all__ = ["build_quy_trinh_day_du"]
