"""Xuất xứ nguyên liệu — 'trồng từ vùng nào' (Anh chốt 2026-06-15).

Món sâu cao cấp phải trình bày như bếp thượng hạng: mỗi câu trích biết rõ từ
SÁCH nào, TÁC GIẢ nào, THỜI ĐẠI nào, TRƯỜNG PHÁI nào, TRANG mấy. Atom đã có
book_corpus_id + page_start; bảng này map corpus → nhãn xuất xứ đẹp.
"""
from __future__ import annotations

# corpus_id → metadata "vùng trồng"
CORPUS_PROVENANCE = {
    "trung-chau-tu-vi-dau-so-2": {
        "ten_sach": "Tử Vi Đẩu Số (Trung Châu phái)", "ten_han": "中州派紫微斗數",
        "tac_gia": "Vương Đình Chi", "thoi_dai": "hiện đại (Hồng Kông)",
        "phai": "Trung Châu", "phai_code": "trung_chau", "tru": True,
        "vung": "Trung Châu phái — dòng chính tông Hồng Kông, trọng tinh hệ + cung độ",
    },
    "tu-vi-dau-so-toan-thu-vu-tai-luc": {
        "ten_sach": "Tử Vi Đẩu Số Toàn Thư (bản Vũ Tài Lục)", "ten_han": "紫微斗數全書",
        "tac_gia": "Trần Đoàn (Hi Di) — Vũ Tài Lục dịch", "thoi_dai": "đời Tống (cổ điển)",
        "phai": "Trần Đoàn", "phai_code": "tran_doan", "tru": True,
        "vung": "Toàn Thư — kinh điển gốc của Tử Vi, lời phú cô đọng",
    },
    "tu-vi-dau-so-toan-thu-zh": {
        "ten_sach": "Tử Vi Đẩu Số Toàn Thư (cổ văn, bản dịch Trung)", "ten_han": "紫微斗數全書",
        "tac_gia": "Trần Đoàn (Hi Di)", "thoi_dai": "đời Tống (cổ văn)",
        "phai": "Trần Đoàn (cổ văn)", "phai_code": "tran_doan_zh", "tru": True,
        "vung": "Toàn Thư cổ văn — nguyên bản Hán, các bài phú sao×cung",
    },
    "tu-vi-ham-so": {
        "ten_sach": "Tử Vi Hàm Số", "ten_han": "",
        "tac_gia": "Nguyễn Phát Lộc", "thoi_dai": "1972 (Sài Gòn)",
        "phai": "Hàm Số", "phai_code": "ham_so", "tru": False,
        "vung": "Hàm Số — phái Việt cận đại, hệ thống hóa theo công thức",
    },
    "tu-vi-nghiem-ly-toan-thu-thien-luong": {
        "ten_sach": "Tử Vi Nghiệm Lý Toàn Thư", "ten_han": "",
        "tac_gia": "Cụ Thiên Lương", "thoi_dai": "hiện đại (Việt Nam)",
        "phai": "Thiên Lương", "phai_code": "thien_luong", "tru": False,
        "vung": "Thiên Lương — nghiệm lý từ thực chứng lá số đời thực",
    },
    "tuvi-bon-ba-tiktok": {
        "ten_sach": "Tử Vi Bôn Ba (quán chiếu Ngũ Uẩn)", "ten_han": "",
        "tac_gia": "Tử Vi Bôn Ba", "thoi_dai": "2026 (đương đại VN)",
        "phai": "Ngũ Uẩn", "phai_code": "tu_vi_bon_ba", "tru": False,
        "vung": "Đương đại VN — soi lá số qua lăng kính Ngũ Uẩn nhà Phật",
    },
}

# Hai trụ chính (dày + đối chiếu được trên mọi sao)
TRU_CHINH = {"trung_chau", "tran_doan", "tran_doan_zh"}
# Gia vị (mỏng → lật thành câu hỏi thay vì khẳng định)
GIA_VI = {"ham_so", "thien_luong", "tu_vi_bon_ba"}


def provenance(corpus_id: str | None) -> dict | None:
    """corpus_id → metadata xuất xứ (None nếu không rõ)."""
    if not corpus_id:
        return None
    return CORPUS_PROVENANCE.get(corpus_id)


def nhan_xuat_xu(corpus_id: str | None, page: int | None = None) -> str:
    """Nhãn ngắn 'trồng từ vùng nào' cho 1 atom: 「Sách」 — Tác giả (thời đại) tr.X."""
    p = provenance(corpus_id)
    if not p:
        return ""
    s = f"「{p['ten_sach']}」 — {p['tac_gia']} ({p['thoi_dai']})"
    if page:
        s += f", tr.{page}"
    return s


def la_tru(phai_code: str | None) -> bool:
    return phai_code in TRU_CHINH
