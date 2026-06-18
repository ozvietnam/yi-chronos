"""Đọc sâu cung Phúc Đức + Nô Bộc (Anh duyệt Q2/Q3, 2026-06-17).

Bám cổ văn Toàn Thư tr.84-89 (đã đọc vòng 5) + góc dân gian Việt đã ingest wiki
(atom 19201 Phúc Đức↔mộ phần · 19202 Nô Bộc↔lứa đôi). Giữ NGUYÊN NGHĨA cổ, KHÔNG
nhẹ hóa (Anh chốt); góc Việt gắn cờ nguồn rõ. Đọc đồng dạng, không predict.
"""
from __future__ import annotations

_SAO_VI = {"tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương", "vu_khuc": "Vũ Khúc",
           "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh", "thien_phu": "Thiên Phủ",
           "thai_am": "Thái Âm", "tham_lang": "Tham Lang", "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng",
           "thien_luong": "Thiên Lương", "that_sat": "Thất Sát", "pha_quan": "Phá Quân"}
SAT = {"kinh_duong", "da_la", "hoa_tinh", "linh_tinh", "dia_khong", "dia_kiep"}

# Phúc Đức per chính tinh (Toàn Thư tr.84-85, nguyên nghĩa)
PHUC = {
    "tu_vi": "hưởng phúc an lạc; cùng Thiên Phủ suốt đời tốt lành; cùng Phá Quân lo nghĩ buồn phiền",
    "thien_co": "cùng Tử Vi hưởng phúc; lao tâm khi gặp Cự Môn",
    "thai_duong": "hoạ trung gặp phúc; cùng Thái Âm vui sướng; cùng Cự Môn lo phiền",
    "vu_khuc": "nhập miếu an nhiên hưởng phúc, hãm địa lo phiền; cùng Phá Quân bôn tẩu",
    "thien_dong": "an ổn sung sướng; cùng Thiên Lương thanh nhàn; cùng Thái Âm hưởng phúc",
    "liem_trinh": "đắc địa cứu bĩ lúc bí lại thông; cùng Thiên Đồng vừa phúc vừa thọ",
    "thien_phu": "an tĩnh hưởng phúc; cùng Tử Vi an dật",
    "thai_am": "miếu hưởng phúc êm; hãm thêm sát thì lao phiền",
    "tham_lang": "lao tâm khổ tứ; cùng Tử Vi mãn niên nhàn tản; cùng Liêm Trinh phận mỏng",
    "cu_mon": "lao lực bất an; cùng Thiên Đồng hưởng phúc; cùng Thái Dương vui buồn thất thường",
    "thien_tuong": "an dật hưởng phúc hữu thọ; cùng Tử Vi khoái lạc; cùng Thái Dương phúc thọ song toàn",
    "thien_luong": "thanh nhàn hưởng phúc, có thọ",
    "that_sat": "nhập miếu hưởng phúc, hãm + sát lao tâm phí lực (cổ văn: nữ Mệnh Thất Sát đơn thủ Phúc Đức → làm nô tỳ/kỹ nữ)",
    "pha_quan": "lao tâm phí lực; cùng Tử Vi an lạc; thêm sát thì nhiễu buồn lo",
}
# Nô Bộc per chính tinh (Toàn Thư tr.88-89, nguyên nghĩa)
NO = {
    "tu_vi": "đắc lực, kẻ dưới sinh tài; gặp sát chỉ toàn bọn láo khoét, dễ chiêu oán phản bội",
    "thien_co": "miếu vượng chủ, hãm cung oán chủ; gặp sát gặp loại phản phúc khó chơi",
    "thai_duong": "nhập miếu vượng chủ (nhiều người theo); gặp Cự Môn dễ bị oán; sát → luôn bị phản",
    "vu_khuc": "miếu địa 'hô một tiếng trăm người thưa'; cùng Thất Sát bội chủ",
    "thien_dong": "đắc lực; cùng Thái Âm càng hay; gặp sát phản chủ",
    "liem_trinh": "đắc địa nhất hô bách ứng; hãm gia nhân hay phản; cùng Thất Sát bội chủ",
    "thien_phu": "nhất hô bách nặc; cùng Tử Vi giúp chủ",
    "thai_am": "miếu nhiều kẻ hầu người hạ; cùng Thái Dương càng hay",
    "tham_lang": "cùng Vũ Khúc chẳng giúp ích việc gì",
    "cu_mon": "thường khẩu thiệt với kẻ dưới",
    "thien_tuong": "có người giúp việc đắc lực",
    "thien_luong": "nhiều gia nhân; cùng Thiên Đồng thuộc hạ biết bảo vệ chủ",
    "that_sat": "khi lăng chủ, gia nhân rình rập trộm cướp; cùng Vũ Khúc phản chủ",
    "pha_quan": "nhập miếu gia nhân đắc lực, hãm chiêu oán bội chủ; gặp sát nguy hiểm",
}


def _cung(ls, fn_key):
    fn = ls.get("fn_to_chi") or {}
    raw = fn.get(fn_key)
    sao = (ls.get("chinh_tinh_per_palace") or {}).get(raw) or []
    phu = []
    for src in ("phu_tinh_per_palace", "vong_sao_per_palace"):
        phu += (ls.get(src) or {}).get(raw) or []
    chi = raw
    co_sat = bool(set(phu) & SAT)
    return chi, sao, co_sat


def doc_phuc_duc(ls: dict) -> dict:
    """Cung Phúc Đức: phúc phận (Toàn Thư) + góc dân gian Việt (mộ phần tổ tiên, cờ nguồn)."""
    chi, sao, co_sat = _cung(ls, "phuc_duc")
    luan = [f"{_SAO_VI.get(s, s)}: {PHUC[s]}" for s in sao if s in PHUC]
    if not sao:
        luan.append("Phúc Đức vô chính diệu — phúc phận tự tạo, nương tam phương; xét sao phụ + đối cung.")
    if co_sat:
        luan.append("⚠ Có sát tinh (Tứ Sát) ở Phúc Đức — cổ văn: dễ lao tâm, phúc phận hao; cần tu tâm tích đức để chuyển.")
    return {
        "chi": chi, "chinh_tinh": [_SAO_VI.get(s, s) for s in sao],
        "luan_co_van": luan,
        "goc_dan_gian_viet": {
            "noi_dung": "Phú nôm VN (Tử Vi Áo Bí – Việt Viêm Tử) cho rằng cung Phúc Đức liên hệ PHẦN MỘ ông cha "
                        "(phúc ấm tổ tiên, phong thủy mộ phần). Vũ Tài Lục lưu ý: Trần Đoàn (Toàn Thư) KHÔNG nói "
                        "tới liên hệ này — nên xem là góc dân gian Việt bổ sung, không phải gốc cổ.",
            "nguon": "Việt Viêm Tử – Tử Vi Áo Bí, tr.86 (atom wiki 19201, cờ kinh_nghiem_vn)",
        },
        "paradigm": "Đọc đồng dạng, không predict. Phúc Đức = nơi quan-sát phúc phận + đức tổ tiên, để TU, không phán giàu nghèo.",
    }


def doc_no_boc(ls: dict) -> dict:
    """Cung Nô Bộc: bạn bè/kẻ dưới/đối tác (Toàn Thư) + góc dân gian Việt (lứa đôi, cờ nguồn)."""
    chi, sao, co_sat = _cung(ls, "no_boc")
    luan = [f"{_SAO_VI.get(s, s)}: {NO[s]}" for s in sao if s in NO]
    if not sao:
        luan.append("Nô Bộc vô chính diệu — quan hệ kẻ dưới/đối tác không định hình rõ; xét đối cung (Huynh Đệ) + sao phụ.")
    if co_sat:
        luan.append("⚠ Có sát tinh ở Nô Bộc — cổ văn: kẻ dưới/bạn bè dễ phản, lường gạt; chọn người + giữ ranh giới kỹ.")
    return {
        "chi": chi, "chinh_tinh": [_SAO_VI.get(s, s) for s in sao],
        "luan_co_van": luan,
        "goc_dan_gian_viet": {
            "noi_dung": "Phú nôm VN cho rằng cung Nô Bộc liên quan cả cuộc sống LỨA ĐÔI: Đào Hồng/Phụ Bật ở Nô → "
                        "chính thê thứ thiếp; Hóa Quyền ở Nô → vợ lẽ cướp quyền chính thê. Toàn Thư KHÔNG nói liên "
                        "quan này — góc dân gian Việt bổ sung.",
            "nguon": "Phú nôm tiền nhân Việt, tr.89 (atom wiki 19202, cờ kinh_nghiem_vn)",
        },
        "paradigm": "Đọc đồng dạng, không predict. Nô Bộc = quan-sát quan hệ kẻ dưới/đối tác (và theo VN: cả lứa đôi), để ứng xử, không phán định.",
    }
