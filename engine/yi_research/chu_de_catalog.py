"""Chủ Đề Catalog — quản trị 30+ sách Đông phương theo CHỦ ĐỀ thay vì tuyến tính.

Paradigm Anh duyệt (2026-06-02 đêm):
- VÒNG 1: trinh sát chiều rộng (đầu + cuối + TOC + dense passages)
- VÒNG 2: index hóa (wiki concept_index — 3463 concepts có sẵn)
- VÒNG 3: chủ đề luận sâu — module này TRỢ GIÚP vòng 3

Khi anh hỏi 1 chủ đề ("Tiết khí Bát Tự") → tra catalog → trả về list
(sách, page range, ghi chú) liên quan → đọc CHỈ phần đó.

Nguồn: NHL paradigm — tổng hợp 15+ cuốn theo chủ đề (1979 viết Kinh Dịch).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass(frozen=True)
class SachRef:
    """1 reference đến sách + page range cho 1 chủ đề."""

    corpus_id: str                    # folder name in data/restored_books/
    title_short: str                  # human-friendly title
    author: str                       # tác giả
    page_range: tuple[int, int] | None = None  # (start, end). None = toàn sách
    note: str = ""                    # ghi chú tại sao chủ đề này có trong sách
    priority: int = 3                 # 1=must-read, 2=secondary, 3=optional

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ChuDe:
    """1 chủ đề + list các sách reference."""

    id: str
    ten: str
    truong_phai: str                  # bát tự / tử vi / hà lạc / mai hoa / kmđg / cross
    mo_ta: str
    refs: tuple[SachRef, ...]
    related_concepts: tuple[str, ...] = field(default_factory=tuple)  # cross-link wiki concepts

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ten": self.ten,
            "truong_phai": self.truong_phai,
            "mo_ta": self.mo_ta,
            "refs": [r.to_dict() for r in self.refs],
            "related_concepts": list(self.related_concepts),
        }


# ────────────────────────────────────────────────────────────────────────────
# 30+ CHỦ ĐỀ CỐT YẾU
# Mỗi chủ đề có 3-7 sách + page range cụ thể
# ────────────────────────────────────────────────────────────────────────────

CATALOG: tuple[ChuDe, ...] = (
    # ── 1. NỀN TẢNG TƯỢNG SỐ ──────────────────────────────────────────────
    ChuDe(
        id="ha_do_lac_thu",
        ten="Hà Đồ + Lạc Thư",
        truong_phai="nen-tang",
        mo_ta="Cơ sở tượng số toàn bộ Dịch học. Hà Đồ = số sinh-thành. Lạc Thư = ma phương 9 cung.",
        refs=(
            SachRef("ha-do-trong-van-minh-dai-viet", "Hà Đồ trong văn minh Đại Việt", "?", priority=1, note="Sách chính"),
            SachRef("kinh-dich-va-he-nhi-phan", "Kinh Dịch và Hệ Nhị Phân", "Hoàng Tuấn", priority=1, note="Góc khoa học"),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (3, 25), priority=1, note="Số Can Chi theo Hà Đồ Lạc Thư"),
            SachRef("dich-hoc-tinh-hoa-nguyen-duy-can", "Dịch học Tinh hoa", "Nguyễn Duy Cần", priority=2),
        ),
        related_concepts=("Hà Đồ", "Lạc Thư", "9 cung Lạc Thư"),
    ),
    ChuDe(
        id="bat_quai_tuong",
        ten="Bát Quái + Tượng Quẻ",
        truong_phai="nen-tang",
        mo_ta="8 quẻ đơn + tượng + hành + phương + mùa. Cơ sở cho mọi trường phái.",
        refs=(
            SachRef("bi-an-cua-bat-quai", "Bí Ẩn của Bát Quái", "Vương Ngọc Đức et al.", priority=1, note="Tổng hợp 499p"),
            SachRef("kinh-dich-va-he-nhi-phan", "Kinh Dịch và Hệ Nhị Phân", "Hoàng Tuấn", priority=1),
            SachRef("dich-hoc-tinh-hoa-nguyen-duy-can", "Dịch học Tinh hoa", "Nguyễn Duy Cần", priority=2),
        ),
        related_concepts=("Càn", "Khôn", "Khảm", "Ly", "Chấn", "Tốn", "Cấn", "Đoài"),
    ),
    ChuDe(
        id="he_nhi_phan",
        ten="Hệ Nhị Phân + Khoa học hiện đại",
        truong_phai="nen-tang",
        mo_ta="Kinh Dịch ↔ binary code. Leibniz, IT, DNA. Góc khoa học hiện đại — Hoàng Tuấn.",
        refs=(
            SachRef("kinh-dich-va-he-nhi-phan", "Kinh Dịch và Hệ Nhị Phân", "Hoàng Tuấn", priority=1, note="Sách chính 842p"),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=1),
        ),
        related_concepts=("nhị phân", "binary", "tượng nhị phân"),
    ),

    # ── 2. KINH DỊCH (64 quẻ + 384 hào) ───────────────────────────────────
    ChuDe(
        id="kinh_dich_64_que",
        ten="64 quẻ Dịch + 384 hào (Chu Dịch)",
        truong_phai="kinh-dich",
        mo_ta="Toàn bộ 64 quẻ x 6 hào — paradigm gốc Đông phương.",
        refs=(
            SachRef("kinh-dich-tron-bo-ngo-tat-to", "Kinh Dịch Trọn Bộ", "Ngô Tất Tố", priority=1, note="⭐⭐ Bản dịch CỐT TV — 1.6M chars, full 64 quẻ + Trình Di + Chu Hy + Phan Bội Châu"),
            SachRef("dich-hoc-tinh-hoa-nguyen-duy-can", "Dịch học Tinh hoa", "Nguyễn Duy Cần", priority=1),
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Bát Tự Hà Lạc & Quỹ Đạo Đời Người", "Xuân Cang", (76, 415), priority=1, note="Phần II 64 quẻ"),
            SachRef("chu-dich-voi-du-doan-hoc", "Chu Dịch với Dự Đoán Học", "Thiệu Vĩ Hoa", priority=2, note="798p kinh điển TQ"),
            SachRef("nhap-mon-chu-dich-du-doan-hoc", "Nhập môn Chu Dịch", "Thiệu Vĩ Hoa?", priority=2),
        ),
    ),
    ChuDe(
        id="am_duong_ngu_hanh",
        ten="Học thuyết Âm Dương Ngũ Hành",
        truong_phai="nen-tang",
        mo_ta="Triết học gốc Đông phương — Âm Dương + Ngũ Hành sinh khắc. Cốt cho mọi engine.",
        refs=(
            SachRef("hoc-thuyet-am-duong-ngu-hanh-le-van-suu", "Học Thuyết Âm Dương Ngũ Hành", "Lê Văn Sửu", priority=1, note="⭐⭐ Triết học gốc — đã restore, nhưng CID encoding, cần OCR ảnh phục hồi"),
            SachRef("bi-an-cua-bat-quai", "Bí Ẩn Bát Quái", "Vương Ngọc Đức et al.", priority=2),
            SachRef("dich-hoc-tinh-hoa-nguyen-duy-can", "Dịch học Tinh hoa", "Nguyễn Duy Cần", priority=2),
        ),
        related_concepts=("âm dương", "ngũ hành", "sinh khắc"),
    ),
    ChuDe(
        id="thai_bi_paradigm",
        ten="Thái-Bĩ paradigm (đảo vị giao thoa)",
        truong_phai="kinh-dich",
        mo_ta="Thái = Khôn trên Càn dưới = đảo vị giao thoa. Bĩ = Càn trên Khôn dưới = đúng vị cách tuyệt.",
        refs=(
            SachRef("kinh-dich-tron-bo-ngo-tat-to", "Kinh Dịch", "Ngô Tất Tố", note="Quẻ 11 + 12"),
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (123, 133), priority=1, note="PBC phụ chú cực đắt"),
        ),
        related_concepts=("Thái", "Bĩ", "đảo vị giao thoa"),
    ),
    ChuDe(
        id="vi_te_hy_vong",
        ten="Vị Tế (quẻ 64) — paradigm HY VỌNG VÔ CÙNG",
        truong_phai="kinh-dich",
        mo_ta="Kinh Dịch KẾT bằng Vị Tế (chưa thành) → hy vọng tiền đồ vô cùng. PBC paradigm cốt.",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (406, 415), priority=1, note="PBC bình quẻ Vị Tế"),
            SachRef("kinh-dich-tron-bo-ngo-tat-to", "Kinh Dịch", "Ngô Tất Tố", priority=2),
        ),
        related_concepts=("Vị Tế", "Ký Tế", "4 quẻ tuần hoàn"),
    ),

    # ── 3. BÁT TỰ / TỨ TRỤ ────────────────────────────────────────────────
    ChuDe(
        id="vuong_suy_bat_tu",
        ten="Vượng-Suy Nhật Chủ (Bát Tự)",
        truong_phai="bat-tu",
        mo_ta="Strong-Weak day master. Phân tích Mộc-Hỏa-Thổ-Kim-Thủy của Nhật Chủ.",
        refs=(
            SachRef("trich-thien-tuy-binh-chu-nham-thiet-tieu", "Trích Thiên Tủy bình chú", "Nhậm Thiết Tiều", priority=1, note="20 lý lẽ điên đảo"),
            SachRef("du-doan-tu-tru-thieu-vy-hoa", "Dự đoán Tứ trụ", "Thiệu Vĩ Hoa", priority=1),
            SachRef("du-doan-theo-tu-tru-thieu-vy-hoa-ban-dep", "Dự đoán Tứ trụ (bản đẹp)", "Thiệu Vĩ Hoa", priority=2),
            SachRef("chu-dich-voi-du-doan-hoc", "Chu Dịch với Dự đoán học", "Thiệu Vĩ Hoa", priority=2),
            SachRef("tu-thu-binh-giai", "Tử Thư Bình Giải", "?", priority=2),
        ),
        related_concepts=("vượng suy", "nhật chủ", "thông căn", "hư phù"),
    ),
    ChuDe(
        id="cach_dung_than",
        ten="Cách Dụng Thần (Bát Tự)",
        truong_phai="bat-tu",
        mo_ta="Quan Sát + Thương Quan + Tài + Ấn + Tỷ — 10 thần Lục Thân. Cách cục.",
        refs=(
            SachRef("trich-thien-tuy-binh-chu-nham-thiet-tieu", "Trích Thiên Tủy", "Nhậm Thiết Tiều", priority=1, note="Cách cục TTT"),
            SachRef("du-doan-tu-tru-thieu-vy-hoa", "Dự đoán Tứ trụ", "Thiệu Vĩ Hoa", priority=1),
            SachRef("du-bao-theo-tu-binh", "Dự báo theo Tứ Bình", "?", priority=2),
            SachRef("tu-thu-binh-giai", "Tử Thư Bình Giải", "?", priority=2),
        ),
        related_concepts=("dụng thần", "cách cục", "lục thân"),
    ),
    ChuDe(
        id="thong_can_nap_am",
        ten="Thông Căn + Nạp Âm (Bát Tự)",
        truong_phai="bat-tu",
        mo_ta="Thông căn = Thiên Can có gốc ở Địa Chi. Nạp âm = 60 Giáp Tý theo hành.",
        refs=(
            SachRef("can-chi-thong-luan", "Can Chi Thông Luận", "?", priority=1, note="352p chuyên đề"),
            SachRef("trich-thien-tuy-binh-chu-nham-thiet-tieu", "Trích Thiên Tủy", "Nhậm Thiết Tiều", priority=1),
            SachRef("hoang-lich", "Hoàng Lịch", "?", priority=2),
        ),
        related_concepts=("thông căn", "nạp âm", "60 Giáp Tý"),
    ),

    # ── 4. HÀ LẠC ──────────────────────────────────────────────────────────
    ChuDe(
        id="tien_thien_hau_thien_que",
        ten="Tiên Thiên + Hậu Thiên quẻ (Hà Lạc)",
        truong_phai="ha-lac",
        mo_ta="THỂ (Tiên Thiên) + DỤNG (Hậu Thiên). Cách derive 2 quẻ cốt mệnh từ Tứ Trụ.",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (1, 75), priority=1, note="Phần I lý thuyết"),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=1, note="14 bước Hoàng Tuấn"),
            SachRef("nguyen-ly-chon-ngay-theo-bat-tu-ha-lac", "Nguyên lý chọn ngày theo Bát Tự Hà Lạc", "?", priority=2),
        ),
        related_concepts=("Tiên Thiên", "Hậu Thiên", "Quẻ Bản Mệnh"),
    ),
    ChuDe(
        id="menh_hop_cach",
        ten="Mệnh Hợp Cách 10 tiêu chuẩn (Hà Lạc)",
        truong_phai="ha-lac",
        mo_ta="10 tiêu chuẩn đánh giá quẻ Tiên Thiên: tên quẻ, hào NĐ, yểm trợ, số ÂD, mệnh×quẻ...",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (48, 60), priority=1, note="10 tiêu chuẩn"),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=2),
        ),
        related_concepts=("Mệnh hợp cách", "10 tiêu chuẩn"),
    ),
    ChuDe(
        id="hoa_cong_nguyen_khi",
        ten="Hóa Công + Thiên/Địa Nguyên Khí (Hà Lạc)",
        truong_phai="ha-lac",
        mo_ta="3 ưu tiên năng lượng Trời Đất: Hóa Công (mùa), TNK (Can năm), ĐNK (Chi năm).",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (37, 47), priority=1),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=1),
        ),
    ),
    ChuDe(
        id="phan_loai_nhan_hoc",
        ten="Paradigm 'Phân loại nhân học cổ' (Hoàng Tuấn)",
        truong_phai="ha-lac",
        mo_ta="Hà Lạc + Tử Vi = MÔN PHÂN LOẠI NHÂN HỌC CỔ. Answer 'tại sao hàng triệu người cùng lá số?'",
        refs=(
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (5, 25), priority=1),
            SachRef("kinh-dich-va-he-nhi-phan", "Kinh Dịch và Hệ Nhị Phân", "Hoàng Tuấn", priority=2),
        ),
    ),
    ChuDe(
        id="nien_menh_dac_the",
        ten="Niên Mệnh + Đắc Thể (Hà Lạc nâng cao)",
        truong_phai="ha-lac",
        mo_ta="Niên Mệnh (nạp âm 60 Giáp Tý) × Quẻ Tiên Thiên (sinh nhập/xuất). Đắc Thể = Niên Mệnh × Quẻ cung Thiên Can.",
        refs=(
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (65, 72), priority=1, note="⭐ Paradigm độc đắc Hoàng Tuấn"),
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", priority=2),
        ),
        related_concepts=("niên mệnh", "đắc thể", "nạp âm", "sinh nhập"),
    ),
    ChuDe(
        id="chan_dung_ha_lac",
        ten="Chân dung Hà Lạc thực tế (7 nhà văn VN)",
        truong_phai="ha-lac",
        mo_ta="7 case study Xuân Cang Phần Ba: Tản Đà, Tô Hoài, Nguyên Ngọc, TĐKhoa, Thu Huệ, NHL, ĐTLL.",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (420, 583), priority=1, note="Phần III"),
        ),
    ),

    # ── 5. TỬ VI ───────────────────────────────────────────────────────────
    ChuDe(
        id="an_sao_tu_vi",
        ten="An sao Tử Vi Đẩu Số (108 sao)",
        truong_phai="tu-vi",
        mo_ta="An 12 cung Mệnh-Thân + 14 chính tinh + phụ tinh + Tứ Hóa.",
        refs=(
            SachRef("tu-vi-dau-so-toan-thu-vu-tai-luc", "Tử Vi Đẩu Số Toàn Thư", "Vũ Tài Lục", priority=1),
            SachRef("tu-vi-ham-so", "Tử Vi Hàm Số", "?", priority=2),
            SachRef("tu-vi-nghiem-ly-toan-thu-thien-luong", "Tử Vi Nghiệm Lý", "Thiên Lương", priority=2),
            SachRef("sach-tu-vi-vo-long", "Tử Vi Vô Long", "?", priority=2),
            SachRef("lap-va-giai-tu-vi", "Lập và Giải Tử Vi", "?", priority=2),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=2, note="Chương Tử Vi của Hoàng Tuấn"),
        ),
        related_concepts=("Tử Vi", "108 sao", "12 cung"),
    ),
    ChuDe(
        id="cach_cuc_tu_vi",
        ten="Cách Cục Tử Vi (Phú Thái Vi)",
        truong_phai="tu-vi",
        mo_ta="545 cách cục kinh điển từ Phú Thái Vi Quyển 1 Toàn Thư. Mệnh chủ vs Thân chủ.",
        refs=(
            SachRef("tu-vi-dau-so-toan-thu-vu-tai-luc", "Tử Vi Đẩu Số Toàn Thư", "Vũ Tài Lục", priority=1),
            SachRef("tu-vi-nghiem-ly-toan-thu-thien-luong", "Tử Vi Nghiệm Lý", "Thiên Lương", priority=2),
        ),
        related_concepts=("cách cục", "545 cách", "Phú Thái Vi"),
    ),
    ChuDe(
        id="dai_van_luu_nien_tv",
        ten="Đại Vận + Lưu Niên Tử Vi (Đẩu Quân)",
        truong_phai="tu-vi",
        mo_ta="Đẩu Quân lưu nguyệt + Đại Vận 10 năm + Lưu Niên + Lưu Tháng.",
        refs=(
            SachRef("tu-vi-dau-so-toan-thu-vu-tai-luc", "Tử Vi Đẩu Số Toàn Thư", "Vũ Tài Lục", priority=1),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", priority=2),
        ),
    ),

    # ── 6. MAI HOA DỊCH SỐ ──────────────────────────────────────────────────
    ChuDe(
        id="mai_hoa_tam_yeu",
        ten="Mai Hoa Tam Yếu + 11 chiêm",
        truong_phai="mai-hoa",
        mo_ta="Thể-Dụng-Hỗ tam yếu. Quan vật → trace tính.",
        refs=(
            SachRef("khong-minh-than-toan-384-que", "Khổng Minh 384 quẻ", "?", priority=2),
        ),
        related_concepts=("Thể Dụng Hỗ", "Khang Tiết", "Mai Hoa"),
    ),
    ChuDe(
        id="bat_nghi_bat_boc",
        ten="Bất nghi bất bốc (Iron Rule #4)",
        truong_phai="mai-hoa",
        mo_ta="Không nghi không bói. 1 việc bói 1 lần. Trình Di chú quẻ Mông xác nhận gốc.",
        refs=(
            SachRef("kinh-dich-tron-bo-ngo-tat-to", "Kinh Dịch", "Ngô Tất Tố", note="Quẻ Mông Trình Di chú"),
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (92, 93), priority=1, note="Trích Mông"),
        ),
    ),

    # ── 7. KỲ MÔN ĐỘN GIÁP ──────────────────────────────────────────────────
    ChuDe(
        id="kmdg_co_ban",
        ten="Kỳ Môn Độn Giáp cơ bản",
        truong_phai="kmdg",
        mo_ta="9 cung + 8 môn + 9 tinh + 8 thần. Thuật chiêm cổ TQ.",
        refs=(
            SachRef("ki-mon-don-giap", "Kỳ Môn Độn Giáp", "TQ", priority=1, note="367p"),
        ),
    ),

    # ── 8. CROSS-CUTTING (xuyên trường phái) ────────────────────────────────
    ChuDe(
        id="duc_nang_thang_so",
        ten="ĐỨC NĂNG THẮNG SỐ (Iron Rule #4+6)",
        truong_phai="cross",
        mo_ta="Số chỉ là XÁC SUẤT. ĐỨC + TÀI + Ý CHÍ + THỜI CƠ thay đổi số. 4 nguồn cổ độc lập xác nhận.",
        refs=(
            SachRef("kinh-dich-tron-bo-ngo-tat-to", "Kinh Dịch (quẻ Mông Trình Di)", "Ngô Tất Tố", priority=1),
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang (PBC Thái-Bĩ)", "Xuân Cang", (123, 133), priority=1),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số (Hoàng Tuấn p37)", "Hoàng Tuấn", (35, 40), priority=1),
        ),
    ),
    ChuDe(
        id="khong_minh_7_cach",
        ten="Khổng Minh 7 cách phối hợp đánh giá người",
        truong_phai="cross",
        mo_ta="Tâm Tướng > Ngoại Tướng. 7 tiêu chí: chí hướng, đúng-sai, kiến thức, đức dũng, liêm chính, chữ tín, tâm tính.",
        refs=(
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (9, 11), priority=1, note="Trích Khổng Minh"),
        ),
    ),
    ChuDe(
        id="tiet_khi_lich",
        ten="Tiết khí + Lịch Can Chi",
        truong_phai="cross",
        mo_ta="24 tiết khí + chuyển dương → âm Can Chi. Quan trọng cho cả Bát Tự + Tử Vi + Hà Lạc.",
        refs=(
            SachRef("bat-tu-ha-lac-va-quy-dao-doi-nguoi", "Hà Lạc Xuân Cang", "Xuân Cang", (584, 608), priority=1, note="Phụ lục Tiết khí"),
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (26, 50), priority=1, note="Số mùa cụ thể"),
            SachRef("hoang-lich", "Hoàng Lịch", "?", priority=2),
            SachRef("can-chi-thong-luan", "Can Chi Thông Luận", "?", priority=2),
        ),
        related_concepts=("tiết khí", "24 tiết", "lịch can chi"),
    ),
    ChuDe(
        id="vi_nhan_nghich_so",
        ten="Paradigm vĩ nhân nghịch số",
        truong_phai="cross",
        mo_ta="Hemingway, Van Gogh, Beethoven, Lobachevsky đều nghịch số mà lỗi lạc. Nghịch số chưa chắc xấu.",
        refs=(
            SachRef("ly-thuyet-tuong-so-hoang-tuan", "Lý Thuyết Tượng Số", "Hoàng Tuấn", (35, 37), priority=1),
        ),
    ),
)


# ────────────────────────────────────────────────────────────────────────────
# LOOKUP API
# ────────────────────────────────────────────────────────────────────────────

def get_chu_de(chu_de_id: str) -> ChuDe | None:
    """Lookup chủ đề by ID."""
    for c in CATALOG:
        if c.id == chu_de_id:
            return c
    return None


def search_chu_de(keyword: str) -> list[ChuDe]:
    """Search chủ đề by keyword (in name, mo_ta, or related_concepts)."""
    kw = keyword.lower().strip()
    results = []
    for c in CATALOG:
        if (
            kw in c.ten.lower()
            or kw in c.mo_ta.lower()
            or any(kw in rc.lower() for rc in c.related_concepts)
            or kw in c.id.lower()
        ):
            results.append(c)
    return results


def list_chu_de_by_truong_phai(truong_phai: str) -> list[ChuDe]:
    """List all chủ đề of 1 trường phái."""
    return [c for c in CATALOG if c.truong_phai == truong_phai]


def get_sach_referenced() -> set[str]:
    """All corpus_id used in catalog."""
    return {ref.corpus_id for c in CATALOG for ref in c.refs}


def get_summary_stats() -> dict:
    """Stats về catalog."""
    truong_phai_counts: dict[str, int] = {}
    for c in CATALOG:
        truong_phai_counts[c.truong_phai] = truong_phai_counts.get(c.truong_phai, 0) + 1
    return {
        "total_chu_de": len(CATALOG),
        "total_refs": sum(len(c.refs) for c in CATALOG),
        "by_truong_phai": truong_phai_counts,
        "total_sach_referenced": len(get_sach_referenced()),
    }


def render_chu_de_markdown(chu_de: ChuDe) -> str:
    """Render 1 chủ đề thành markdown để LLM hoặc UI render."""
    lines = [
        f"# {chu_de.ten}",
        f"_Trường phái_: **{chu_de.truong_phai}** | _ID_: `{chu_de.id}`",
        "",
        chu_de.mo_ta,
        "",
        "## Sách reference (theo priority)",
        "",
    ]
    for ref in sorted(chu_de.refs, key=lambda r: r.priority):
        p_label = {1: "🥇 Must-read", 2: "🥈 Secondary", 3: "🥉 Optional"}.get(ref.priority, "")
        page_str = f" p{ref.page_range[0]}-{ref.page_range[1]}" if ref.page_range else " (toàn sách)"
        note_str = f" — _{ref.note}_" if ref.note else ""
        lines.append(f"- {p_label} **{ref.title_short}**{page_str} ({ref.author}){note_str}")
        lines.append(f"  `corpus: {ref.corpus_id}`")
    if chu_de.related_concepts:
        lines.append("")
        lines.append("## Related concepts (cross-link wiki)")
        lines.append(", ".join(f"`{rc}`" for rc in chu_de.related_concepts))
    return "\n".join(lines)
