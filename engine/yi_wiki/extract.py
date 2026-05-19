"""Extract Passages, Methods, Concepts từ trang đã đọc → wiki DB.

Mỗi hàm `extract_pages_NNN_MMM()` là 1 "lesson" — anh đọc 5 trang, em ghi.
Idempotent: chạy nhiều lần ok (UPSERT, INSERT chỉ nếu chưa có cùng anchor).
"""
from __future__ import annotations

from pathlib import Path

from engine.yi_wiki.models import Author, ConceptIndex, Method, Passage, Work
from engine.yi_wiki.store import get_store, _enc

CORPUS = "mai-hoa-dich-so-thieu-khang-tiet"
RESTORED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_restored" / CORPUS / "pages"


def _master_id() -> int:
    s = get_store()
    for a in s.list_authors():
        if a.name_zh == "邵雍":
            return a.author_id
    raise RuntimeError("Chưa seed Master. Chạy: python -m engine.yi_wiki.seed_master")


def _read_page(page_no: int) -> str:
    p = RESTORED_DIR / f"page-{page_no:04d}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _has_passage(corpus_id: str, page_start: int, page_end: int) -> bool:
    """Check duplicate by anchor."""
    s = get_store()
    rows = s.list_passages(corpus_id=corpus_id)
    return any(r["page_start"] == page_start and r["page_end"] == page_end for r in rows)


def _add_concept(canonical_vi: str, canonical_zh: str = "", note: str = "",
                 page: int = 0, aliases: list[str] | None = None) -> int:
    s = get_store()
    return s.upsert_concept(ConceptIndex(
        canonical_vi=canonical_vi,
        canonical_zh=canonical_zh,
        aliases=aliases or [],
        short_note=note,
        first_seen_corpus=CORPUS,
        first_seen_page=page,
    ))


def extract_pages_11_15():
    """Trang 11-15: lời tựa Ông Văn Tùng + Quyển 1 mở đầu (Chu dịch quái số)."""
    s = get_store()
    master = _master_id()

    # ── Trang 14: Passage "Chu dịch quái số" (METHOD đầu tiên của sách) ──
    if not _has_passage(CORPUS, 14, 14):
        s.insert_passage(Passage(
            author_id=master,
            corpus_id=CORPUS,
            page_start=14, page_end=14,
            topic="Chu dịch quái số — bảng số 8 quẻ Tiên Thiên",
            raw_text=(
                "Càn 1, Đoài 2, Ly 3, Chấn 4, Tốn 5, Khảm 6, Cấn 7, Khôn 8.\n"
                "(Đây là bảng số quẻ Tiên Thiên, mở đầu Quyển I của Mai Hoa Dịch Số.)"
            ),
            summary_50w=(
                "Tiết đầu Quyển I: bảng số 8 quẻ Tiên Thiên. Càn=1, Đoài=2, "
                "Ly=3, Chấn=4, Tốn=5, Khảm=6, Cấn=7, Khôn=8. Đây là input gốc "
                "cho mọi phép bốc Mai Hoa qua số."
            ),
            is_canonical=True,
        ))

    # ── Trang 14-15: Passage giải thích Chu Dịch + 3 dịch cổ ──
    if not _has_passage(CORPUS, 14, 15):
        s.insert_passage(Passage(
            author_id=master,
            corpus_id=CORPUS,
            page_start=14, page_end=15,
            topic="Định nghĩa Chu Dịch + 3 sách Dịch cổ (Liên Sơn / Quy Tàng / Chu)",
            raw_text=(
                "Chu Dịch là sách Dịch nhà Chu (1122-250 BC) lấy quẻ Càn làm đầu. "
                "Liên Sơn Dịch (Hạ, lấy Cấn) và Quy Tàng Dịch (Thương, lấy Khôn) "
                "đã thất truyền. Chu Dịch do Chu Hy đời Tống chú giải; bộ 'Chu "
                "Dịch đại toàn' Hồ Quảng + Kim Ân Thi đời Minh đầy đủ nhất, "
                "dùng 'Dịch truyện' của Trình Di và 'Chu Dịch bản nghĩa' của Chu Hy."
            ),
            summary_50w=(
                "Bối cảnh: Chu Dịch là 1/3 sách Dịch cổ (Liên Sơn, Quy Tàng đã "
                "thất truyền). Bản uy tín nhất VN là Ngô Tất Tố dịch từ Chu Dịch "
                "đại toàn (Hồ Quảng, Kim Ân Thi đời Minh)."
            ),
            is_canonical=False,
        ))

    # ── Update Method "Chu dịch quái số" với procedure ──
    # (Đã seed placeholder ở seed_master? Không — chỉ seed các method có 占, 體用…)
    # Insert mới
    s.upsert_method(Method(
        author_id=master,
        name_vi="Chu dịch quái số (bảng Tiên Thiên)",
        name_zh="周易卦數",
        domain="bốc",
        inputs_required=["số nguyên 1-8"],
        procedure_steps=[
            "1=Càn, 2=Đoài, 3=Ly, 4=Chấn, 5=Tốn, 6=Khảm, 7=Cấn, 8=Khôn",
            "Số lớn hơn 8: lấy dư khi chia 8 (mod 8). Dư 0 → Khôn (8).",
        ],
        output_format="Tên 1 trong 8 quẻ Tiên Thiên",
        notes="Trang 14 Quyển I — input gốc cho mọi phép bốc Mai Hoa qua số.",
    ))

    # ── Concepts mới gặp trang 11-15 ──
    new_concepts = [
        # Trang 11-12
        ("Thái ất thần kinh", "太乙神經",
         "Lương Đắc Bằng truyền cho Nguyễn Bình Khiêm. Có thể là Mai Hoa Dịch Số.", 11),
        ("Nguyễn Bỉnh Khiêm", "",
         "Đại nho VN. Ảnh hưởng Thiệu Khang Tiết qua Lương Đắc Bằng.", 11),
        ("Lương Đắc Bằng", "",
         "Thầy của Nguyễn Bỉnh Khiêm. Truyền Thái ất thần kinh.", 11),
        ("Trung Châu cổ tịch xuất bản xã", "中州古籍出版社",
         "NXB TQ in Mai Hoa 1997 ở Trịnh Châu (bản nhiều lỗi).", 12),
        ("Quán Tao Đàn", "",
         "Hà Nội — chỗ Ông Văn Tùng dịch (Tết Trung Thu Tân Tỵ).", 12),
        # Trang 14: 8 quẻ Tiên Thiên
        ("Càn", "乾", "Quẻ 1 Tiên Thiên — Trời.", 14),
        ("Đoài", "兌", "Quẻ 2 Tiên Thiên — Đầm.", 14),
        ("Ly", "離", "Quẻ 3 Tiên Thiên — Lửa.", 14),
        ("Chấn", "震", "Quẻ 4 Tiên Thiên — Sấm.", 14),
        ("Tốn", "巽", "Quẻ 5 Tiên Thiên — Gió.", 14),
        ("Khảm", "坎", "Quẻ 6 Tiên Thiên — Nước.", 14),
        ("Cấn", "艮", "Quẻ 7 Tiên Thiên — Núi.", 14),
        ("Khôn", "坤", "Quẻ 8 Tiên Thiên — Đất.", 14),
        # Trang 14: 3 sách Dịch cổ + tác phẩm tham chiếu
        ("Liên Sơn Dịch", "連山易",
         "Sách Dịch đời Hạ (Cấn làm đầu). Thất truyền.", 14),
        ("Quy Tàng Dịch", "歸藏易",
         "Sách Dịch đời Thương (Khôn làm đầu). Thất truyền.", 14),
        ("Chu Dịch đại toàn", "周易大全",
         "Hồ Quảng + Kim Ân Thi đời Minh. Ngô Tất Tố dịch sang VN.", 14),
        ("Dịch truyện", "易傳",
         "Của Trình Di. Phần chú giải gốc trong Chu Dịch đại toàn.", 14),
        ("Chu Dịch bản nghĩa", "周易本義",
         "Của Chu Hy. Phần chú giải gốc trong Chu Dịch đại toàn.", 14),
        # Trang 15: cấu trúc Chu Dịch + chữ Dịch
        ("Dịch kinh", "易經", "1 trong 2 phần Chu Dịch (kinh + truyện).", 15),
        ("Dịch truyện", "易傳", "1 trong 2 phần Chu Dịch.", 15),
        ("Trùng quái / Biệt quái", "重卦/別卦",
         "Quẻ 6 vạch — 8 quẻ 3 vạch trùng lên nhau thành 64 quẻ.", 15),
        ("Quái thượng thể", "卦上體", "Quẻ trên (phần thượng).", 15),
        ("Quái hạ thể", "卦下體", "Quẻ dưới (phần hạ).", 15),
        ("Bất dịch", "不易", "1/3 nghĩa chữ Dịch — không thay đổi.", 15),
        ("Giao dịch", "交易", "1/3 nghĩa chữ Dịch — trao đổi.", 15),
        ("Biến dịch", "變易", "1/3 nghĩa chữ Dịch — thay đổi (quan trọng nhất).", 15),
        ("Tích dịch", "蜥蜴", "Con thằn lằn — 1 giả thiết nguồn gốc chữ Dịch.", 15),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_16_20():
    """Trang 16-20: Phục Hy bát quái + Hà Đồ + Ngũ Hành + Lạc Thư.
    Nội dung nguồn mạch toàn bộ sách."""
    s = get_store()
    master = _master_id()

    # ── Passage 16: Tiết 1 — Bát quái và Quẻ số (Phục Hy thứ tự) ──
    if not _has_passage(CORPUS, 16, 16):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=16, page_end=16,
            topic="Phục Hy bát quái thứ tự (Tiên Thiên thuận)",
            raw_text=(
                "Đơn quái = kinh quái = bát quái.\n"
                "Dịch số bao hàm quái số. Quái số = số thứ tự của bát quái.\n"
                "Phục Hy bát quái thứ tự (Tiên Thiên thuận):\n"
                "  Càn 1 | Tốn 5\n"
                "  Đoài 2 | Khảm 6\n"
                "  Ly 3 | Cấn 7\n"
                "  Chấn 4 | Khôn 8\n"
                "Người bói coi số ảo là số thực — xem được số 7 nghĩ là xem được quẻ Cấn.\n"
                "(Sự vận dụng không tự giác phù hiệu học trong tư duy nguyên thuỷ.)"
            ),
            summary_50w=(
                "Phục Hy thứ tự: 8 quẻ Tiên Thiên thuận. Khi bói, số tự nhiên "
                "đối ứng quẻ qua bảng này. Ví dụ số 7 → quẻ Cấn."
            ),
            is_canonical=True,
        ))

    # ── Passage 17: Hà Đồ ──
    if not _has_passage(CORPUS, 17, 17):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=17, page_end=17,
            topic="Hà Đồ — Phục Hy nhận từ Long Mã sông Hoàng Hà",
            raw_text=(
                "Truyền thuyết: vua Phục Hy thấy Long Mã ở sông Hoàng Hà, "
                "trên lưng 55 chấm đen-trắng. Phục Hy thiết lập Hà Đồ, "
                "vạch ra bát quái, mở đầu Kinh Dịch.\n\n"
                "10 số: 1-2-3-4-5-6-7-8-9-10. Tổng = 55.\n"
                "Số trời (lẻ, trắng): 1,3,5,7,9 = 25.\n"
                "Số đất (chẵn, đen): 2,4,6,8,10 = 30.\n\n"
                "5 cặp tương đắc (Chu Hy chú):\n"
                "  1-6 Bắc | 2-7 Nam | 3-8 Đông | 4-9 Tây | 5-10 Trung\n\n"
                "Dịch hệ từ thượng: 'sinh sinh nhi vị Dịch'.\n"
                "Vận hành theo chiều tương sinh: thuỷ→mộc→hoả→thổ→kim→thuỷ "
                "(Bắc→Đông→Nam→Trung→Tây→Bắc)."
            ),
            summary_50w=(
                "Hà Đồ là bức đồ đầu Kinh Dịch. 55 chấm = 5 cặp (1-6, 2-7, 3-8, "
                "4-9, 5-10). Vận hành tương sinh ngũ hành. Chu Hy chú trong Bản Nghĩa."
            ),
            is_canonical=True,
        ))

    # ── Passage 18-19: Ngũ Hành Sinh Khắc ──
    if not _has_passage(CORPUS, 18, 19):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=18, page_end=19,
            topic="Ngũ Hành Sinh Khắc — quy luật trụ cột",
            raw_text=(
                "Ngũ hành = 5 vật chất: Thuỷ, Hoả, Mộc, Kim, Thổ.\n"
                "Người TQ cổ coi đó là 5 nguyên tố cơ bản cấu tạo vạn vật.\n\n"
                "TƯƠNG SINH (Sinh = sản sinh, giúp sinh trưởng):\n"
                "  Kim sinh Thuỷ → Thuỷ sinh Mộc → Mộc sinh Hoả → Hoả sinh Thổ → Thổ sinh Kim.\n\n"
                "TƯƠNG KHẮC (Khắc = trói buộc, chế ngự):\n"
                "  Kim khắc Mộc → Mộc khắc Thổ → Thổ khắc Thuỷ → Thuỷ khắc Hoả → Hoả khắc Kim.\n\n"
                "Thứ tự Hà Đồ trùng với tuần hoàn thời tiết: đông→xuân→hạ→thu→đông."
            ),
            summary_50w=(
                "Ngũ Hành: Thuỷ, Hoả, Mộc, Kim, Thổ. Tương sinh và tương khắc là "
                "2 quy luật trụ cột — input cho mọi phép Mai Hoa qua Thể-Dụng."
            ),
            is_canonical=True,
        ))

    # ── Passage 20: Lạc Thư ──
    if not _has_passage(CORPUS, 20, 20):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=20, page_end=20,
            topic="Lạc Thư — Đại Vũ nhận từ Linh Quy sông Lạc",
            raw_text=(
                "Truyền thuyết: Vua Đại Vũ nhà Hạ thấy Linh Quy ở sông Lạc, "
                "trên mai có chữ. Vũ xếp thành Cửu Trù (9 phạm trù) — "
                "khuôn phép trị nước, ghi trong thiên Hồng Phạm Kinh Thư.\n\n"
                "Lạc Thư 9 số (1-9). Tổng = 45.\n"
                "Số trời (lẻ, trắng): 1,3,5,7,9 = 25.\n"
                "Số đất (chẵn, đen): 2,4,6,8 = 20.\n\n"
                "Vị trí 9 ô theo tượng con rùa:\n"
                "  Đầu: 9 | Chân: 1 | Trái mu: 3 | Phải mu: 7\n"
                "  Vai trái: 4 | Vai phải: 2 | Chân trái: 8 | Chân phải: 6\n"
                "  Giữa: 5 (Thái Cực)\n\n"
                "Hà Đồ: 1-6 thuỷ | 2-7 hoả (số sinh thành)."
            ),
            summary_50w=(
                "Lạc Thư là bảng số 9 ô do Đại Vũ lập từ Linh Quy. Cùng với Hà Đồ "
                "ở phần cuối Kinh Dịch. Cửu Trù = Hồng Phạm Kinh Thư."
            ),
            is_canonical=True,
        ))

    # ── Method mới: Hà Đồ, Lạc Thư, Ngũ Hành ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Hà Đồ",
        name_zh="河圖",
        domain="đọc",
        inputs_required=["số 1-10", "phương vị Bắc/Nam/Đông/Tây/Trung"],
        procedure_steps=[
            "5 cặp tương đắc: 1-6 Bắc | 2-7 Nam | 3-8 Đông | 4-9 Tây | 5-10 Trung",
            "Số trời (lẻ) 1,3,5,7,9 = 25; Số đất (chẵn) 2,4,6,8,10 = 30",
            "Vận hành thuận chiều tương sinh: Bắc→Đông→Nam→Trung→Tây",
        ],
        output_format="Mapping số ↔ phương vị ↔ ngũ hành",
        notes="Trang 17 — Phục Hy nhận từ Long Mã sông Hoàng Hà.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Lạc Thư",
        name_zh="洛書",
        domain="đọc",
        inputs_required=["số 1-9"],
        procedure_steps=[
            "9 ô tượng con rùa: 9 đầu, 1 chân, 3 trái mu, 7 phải mu",
            "4 vai trái, 2 vai phải, 8 chân trái, 6 chân phải",
            "5 giữa (Thái Cực)",
            "Tổng 45. Lẻ = 25, chẵn = 20",
        ],
        output_format="Bố cục Cửu cung",
        notes="Trang 20 — Đại Vũ nhận từ Linh Quy sông Lạc. Là gốc Cửu Trù.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Ngũ Hành Tương Sinh",
        name_zh="五行相生",
        domain="biến_hoá",
        inputs_required=["1 trong 5 hành: Kim/Mộc/Thuỷ/Hoả/Thổ"],
        procedure_steps=[
            "Kim sinh Thuỷ",
            "Thuỷ sinh Mộc",
            "Mộc sinh Hoả",
            "Hoả sinh Thổ",
            "Thổ sinh Kim",
        ],
        output_format="Hành kế tiếp trong vòng tương sinh",
        notes="Trang 18-19 — quy luật trụ cột Mai Hoa.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Ngũ Hành Tương Khắc",
        name_zh="五行相剋",
        domain="biến_hoá",
        inputs_required=["1 trong 5 hành"],
        procedure_steps=[
            "Kim khắc Mộc",
            "Mộc khắc Thổ",
            "Thổ khắc Thuỷ",
            "Thuỷ khắc Hoả",
            "Hoả khắc Kim",
        ],
        output_format="Hành bị chế ngự",
        notes="Trang 18-19 — quy luật chế ngự.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Phục Hy bát quái thứ tự (Tiên Thiên thuận)",
        name_zh="伏羲八卦次序",
        domain="bốc",
        inputs_required=["số nguyên 1-8"],
        procedure_steps=[
            "Càn=1, Đoài=2, Ly=3, Chấn=4",
            "Tốn=5, Khảm=6, Cấn=7, Khôn=8",
            "Mọi pp bốc Mai Hoa qua số tự nhiên đều dùng bảng này",
        ],
        output_format="Quẻ tương ứng",
        notes="Trang 16 — Tiết 1 mở đầu Quyển I. Khác với Văn Vương Hậu Thiên.",
    ))

    # ── Concepts trang 16-20 ──
    new_concepts = [
        # Trang 16
        ("Đơn quái", "單卦", "Quẻ đơn 3 vạch = kinh quái = bát quái.", 16),
        ("Kinh quái", "經卦", "Quẻ 3 vạch — 8 quẻ gốc.", 16),
        ("Phục Hy", "伏羲", "Vua thủy tổ TQ. Lập Hà Đồ + bát quái Tiên Thiên.", 16),
        ("Dịch số", "易數", "Bao hàm quái số + dịch lý qua số.", 16),
        ("Quái số", "卦數", "Số thứ tự của bát quái — input bốc Mai Hoa.", 16),
        ("Phù hiệu học", "符號學",
         "Symbolic logic — sự vận dụng không tự giác trong tư duy nguyên thuỷ.", 16),
        # Trang 17 — Hà Đồ
        ("Hà Đồ", "河圖", "Bảng 10 số (1-10), tổng 55. Gốc tương sinh ngũ hành.", 17),
        ("Long Mã", "龍馬", "Linh thú mang Hà Đồ cho Phục Hy ở sông Hoàng Hà.", 17),
        ("Sông Hoàng Hà", "黃河", "Nơi Phục Hy nhận Hà Đồ.", 17),
        ("Số trời", "天數",
         "Số lẻ 1,3,5,7,9 (tổng 25). Dương, chấm trắng.", 17),
        ("Số đất", "地數",
         "Số chẵn 2,4,6,8,10 (tổng 30). Âm, chấm đen.", 17),
        ("Dịch hệ từ thượng", "易繫辭上",
         "Phần Truyện của Chu Dịch. Câu 'sinh sinh nhi vị Dịch' từ đây.", 17),
        ("Sinh sinh nhi vị Dịch", "生生而謂易",
         "Sinh sinh nối tiếp là Dịch — câu cốt lõi.", 17),
        # Trang 18-19 — Ngũ Hành
        ("Ngũ Hành", "五行",
         "5 vật chất Kim/Mộc/Thuỷ/Hoả/Thổ — nguyên tố cấu tạo vạn vật.", 18),
        ("Kim", "金", "1/5 hành. Tương sinh: Thổ→Kim→Thuỷ. Khắc Mộc.", 18),
        ("Mộc", "木", "1/5 hành. Tương sinh: Thuỷ→Mộc→Hoả. Khắc Thổ.", 18),
        ("Thuỷ", "水", "1/5 hành. Tương sinh: Kim→Thuỷ→Mộc. Khắc Hoả.", 18),
        ("Hoả", "火", "1/5 hành. Tương sinh: Mộc→Hoả→Thổ. Khắc Kim.", 18),
        ("Thổ", "土", "1/5 hành. Tương sinh: Hoả→Thổ→Kim. Khắc Thuỷ.", 18),
        ("Tương sinh", "相生", "Sinh = sản sinh, giúp sinh trưởng.", 19),
        ("Tương khắc", "相剋", "Khắc = trói buộc, chế ngự.", 19),
        # Trang 20 — Lạc Thư
        ("Lạc Thư", "洛書", "Bảng 9 số (1-9), tổng 45. Gốc Cửu Trù.", 20),
        ("Đại Vũ", "大禹", "Vua nhà Hạ. Nhận Lạc Thư từ Linh Quy.", 20),
        ("Linh Quy", "靈龜", "Linh thú mang Lạc Thư cho Đại Vũ ở sông Lạc.", 20),
        ("Sông Lạc", "洛水", "Nơi Đại Vũ nhận Lạc Thư.", 20),
        ("Cửu Trù", "九疇", "9 phạm trù trị nước trong Hồng Phạm Kinh Thư.", 20),
        ("Hồng Phạm", "洪範", "Thiên trong Kinh Thư ghi Cửu Trù.", 20),
        ("Kinh Thư", "書經", "1 trong Ngũ Kinh. Có thiên Hồng Phạm.", 20),
        ("Thái Cực", "太極",
         "Số 5 ở giữa Lạc Thư. Khái niệm cốt lõi triết Dịch.", 20),
        ("Số sinh thành", "生成數",
         "Cặp số trong Hà Đồ: 1-6 thuỷ, 2-7 hoả, 3-8 mộc, 4-9 kim, 5-10 thổ.", 20),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_21_25():
    """Trang 21-25: Hà Đồ vs Lạc Thư (Thể-Dụng), Bát cung ngũ hành, Quái Khí."""
    s = get_store()
    master = _master_id()

    # ── Add Hán authors trước (Mạnh Hỷ, Kinh Phòng) ──
    from engine.yi_wiki.models import TIER_MASTER_TEACHER
    s.upsert_author(Author(
        name_vi="Mạnh Hỷ",
        name_zh="孟喜",
        tier_in_lineage=TIER_MASTER_TEACHER,  # tổ tổ — đời Hán
        era="hán",
        worldview_school="quái-khí-học",
        bio_summary="Đời Hán. Đề xướng học thuyết Quái Khí (cùng Kinh Phòng). "
                    "Tiền bối của Thiệu — pp Quái Khí Vượng dùng trong Mai Hoa gốc từ ông.",
    ))
    s.upsert_author(Author(
        name_vi="Kinh Phòng",
        name_zh="京房",
        tier_in_lineage=TIER_MASTER_TEACHER,
        era="hán",
        worldview_school="quái-khí-học",
        bio_summary="Đời Hán (77-37 BC). Cùng Mạnh Hỷ đề xướng Quái Khí. "
                    "Sáng lập Kinh thị Dịch học — 1 trong tiền thân Mai Hoa.",
        birth_year=-77, death_year=-37,
    ))

    # ── Passage 21: Hà Đồ — phương hướng + tính chất ngũ hành ──
    if not _has_passage(CORPUS, 21, 21):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=21, page_end=21,
            topic="Số sinh thành + phương hướng + tính chất ngũ hành (tiếp Hà Đồ)",
            raw_text=(
                "Số sinh thành (tiếp):\n"
                "  1-6 thuỷ Bắc | 2-7 hoả Nam | 3-8 mộc Đông\n"
                "  4-9 kim Tây | 5-10 thổ Trung ương\n\n"
                "Tính chất ngũ hành theo Hà Đồ:\n"
                "  - Thuỷ ở Bắc, nằm dưới — mềm nhuyễn, thấm xuống\n"
                "  - Hoả ở Nam, nằm trên — hun bốc lên\n"
                "  - Mộc trái (Đông), Kim phải (Tây)\n"
                "  - Thổ ở Trung — ngôi Thái Cực, chứa đỡ 4 hành kia\n"
                "  - 4 hành ngoài = Tứ Tượng, ở vòng ngoài Hà Đồ"
            ),
            summary_50w=(
                "Số sinh thành Hà Đồ định phương hướng và bản chất 5 hành. "
                "Thổ là Thái Cực trung tâm, 4 hành ngoài = Tứ Tượng."
            ),
            is_canonical=True,
        ))

    # ── Passage 22: Hà Đồ Thể Tiên Thiên vs Lạc Thư Dụng Hậu Thiên ⭐ ──
    if not _has_passage(CORPUS, 22, 22):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=22, page_end=22,
            topic="Hà Đồ = Thể Tiên Thiên, Lạc Thư = Dụng Hậu Thiên (Thể-Dụng đầu tiên)",
            raw_text=(
                "Hà Đồ vận hành theo TƯƠNG SINH — tượng Thể Tiên Thiên của Dịch.\n"
                "Lạc Thư vận hành theo TƯƠNG KHẮC — Dụng Hậu Thiên.\n\n"
                "Sự sinh hoá vạn vật bị chi phối bởi luật tương khắc — "
                "các hành chế lẫn nhau để giữ 5 hành ở thế quân bình.\n\n"
                "Vị trí Hoả-Kim ở Lạc Thư phải hoán chuyển so với Hà Đồ "
                "để chiều vận hành ngược lại.\n\n"
                "Lạc Thư vận hành: thuỷ → hoả (thuỷ khắc hoả) → kim (hoả khắc kim) "
                "→ mộc (kim khắc mộc) → thổ (mộc khắc thổ) → thuỷ (thổ khắc thuỷ)."
            ),
            summary_50w=(
                "Hà Đồ = Thể Tiên Thiên, vận hành tương sinh. Lạc Thư = Dụng Hậu Thiên, "
                "vận hành tương khắc. Đây là nguyên mẫu THỂ-DỤNG — trụ cột Mai Hoa."
            ),
            is_canonical=True,
        ))

    # ── Passage 23: Tiết 2 — Bát cung thuộc ngũ hành + 64 quẻ ⭐ ──
    if not _has_passage(CORPUS, 23, 23):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=23, page_end=23,
            topic="Tiết 2 — Bát cung thuộc ngũ hành + cấu thành 64 quẻ",
            raw_text=(
                "BÁT CUNG THUỘC NGŨ HÀNH:\n"
                "  Càn, Đoài  → Kim\n"
                "  Khôn, Cấn  → Thổ\n"
                "  Chấn, Tốn  → Mộc\n"
                "  Khảm       → Thuỷ\n"
                "  Ly         → Hoả\n\n"
                "64 quẻ = 8 cung × 8 quẻ. Mỗi cung do 1 quẻ bát quái làm gốc, "
                "kết hợp với 7 quẻ khác + chính nó (trùng quái) = 8 quẻ 6 vạch.\n\n"
                "8 cung: Cung Càn, Đoài, Ly, Chấn, Tốn, Khảm, Cấn, Khôn.\n"
                "Hệ thống lớn 64 quẻ = 8 hệ thống nhỏ (cung) ghép lại."
            ),
            summary_50w=(
                "Bát cung thuộc ngũ hành: Càn/Đoài-Kim, Khôn/Cấn-Thổ, Chấn/Tốn-Mộc, "
                "Khảm-Thuỷ, Ly-Hoả. 64 quẻ = 8 cung × 8 quẻ — input cho Thể-Dụng sinh khắc."
            ),
            is_canonical=True,
        ))

    # ── Passage 24-25: Quái Khí Vượng (Mạnh Hỷ, Kinh Phòng) ──
    if not _has_passage(CORPUS, 24, 25):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=24, page_end=25,
            topic="Quái Khí Vượng — học thuyết Mạnh Hỷ, Kinh Phòng đời Hán",
            raw_text=(
                "QUÁI KHÍ = 3 nhân tố: Quái + Khí hậu (mùa) + Ngũ hành.\n\n"
                "Học thuyết Quái Khí do Mạnh Hỷ + Kinh Phòng đời Hán đề xướng. "
                "Dùng 'quái' Chu Dịch phối với 4 mùa.\n\n"
                "QUÁI KHÍ VƯỢNG THEO MÙA:\n"
                "  Xuân  → Chấn, Tốn (Mộc) vượng\n"
                "  Hạ    → Ly (Hoả) vượng\n"
                "  Thu   → Càn, Đoài (Kim) vượng\n"
                "  Đông  → Khảm (Thuỷ) vượng\n"
                "  4 tháng Thìn-Tuất-Sửu-Mùi (3, 9, 12, 6) → Khôn, Cấn (Thổ) vượng"
            ),
            summary_50w=(
                "Quái Khí Vượng định thế mạnh-yếu của quẻ theo mùa. Mộc xuân, "
                "Hoả hạ, Kim thu, Thuỷ đông, Thổ tháng đất. Gốc Mạnh Hỷ + Kinh Phòng."
            ),
            is_canonical=True,
        ))

    # ── Methods mới ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Bát cung sở thuộc Ngũ Hành",
        name_zh="八宮所屬五行",
        domain="đọc",
        inputs_required=["1 trong 8 quẻ"],
        procedure_steps=[
            "Càn, Đoài → Kim",
            "Khôn, Cấn → Thổ",
            "Chấn, Tốn → Mộc",
            "Khảm → Thuỷ",
            "Ly → Hoả",
        ],
        output_format="Hành tương ứng — input cho Thể-Dụng sinh khắc",
        notes="Trang 23 Tiết 2 Quyển I. Trụ cột cho mọi phép xét sinh khắc Thể-Dụng.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Quái Khí Vượng theo mùa",
        name_zh="卦氣旺",
        domain="đọc",
        inputs_required=["quẻ + tháng/mùa"],
        procedure_steps=[
            "Xuân → Chấn, Tốn (Mộc) vượng",
            "Hạ → Ly (Hoả) vượng",
            "Thu → Càn, Đoài (Kim) vượng",
            "Đông → Khảm (Thuỷ) vượng",
            "Tháng Thìn/Tuất/Sửu/Mùi → Khôn, Cấn (Thổ) vượng",
        ],
        output_format="Vượng / Tướng / Hưu / Tù / Tử",
        notes="Trang 24-25 — học thuyết Mạnh Hỷ + Kinh Phòng đời Hán.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Tiên Thiên vs Hậu Thiên (Thể-Dụng đầu tiên)",
        name_zh="先天後天",
        domain="biến_hoá",
        inputs_required=["Hà Đồ hoặc Lạc Thư"],
        procedure_steps=[
            "Hà Đồ vận hành tương sinh → Thể Tiên Thiên",
            "Lạc Thư vận hành tương khắc → Dụng Hậu Thiên",
            "Vị trí Hoả-Kim hoán chuyển giữa Hà Đồ ↔ Lạc Thư",
        ],
        output_format="Phân biệt Thể (bản nguyên) vs Dụng (ứng dụng)",
        notes="Trang 22 — nguyên mẫu cặp Thể-Dụng. Foundation cho Quyển 3.",
    ))

    # ── Concepts mới ──
    new_concepts = [
        # Trang 21
        ("Tứ Tượng", "四象", "4 hành ngoài Hà Đồ (trừ Thổ trung tâm).", 21),
        ("Thổ trung ương", "土中央", "Ngôi Thái Cực — chứa đỡ 4 hành.", 21),
        # Trang 22 ⭐ Thể-Dụng đầu tiên
        ("Tiên Thiên", "先天",
         "Bản nguyên trước trời đất. Hà Đồ thuộc Tiên Thiên — Thể.", 22),
        ("Hậu Thiên", "後天",
         "Ứng dụng sau trời đất. Lạc Thư thuộc Hậu Thiên — Dụng.", 22),
        ("Thể (Dịch)", "體",
         "Bản nguyên, gốc. Hà Đồ = Thể Tiên Thiên.", 22),
        ("Dụng (Dịch)", "用",
         "Ứng dụng, biểu hiện. Lạc Thư = Dụng Hậu Thiên.", 22),
        ("Quân bình ngũ hành", "五行平衡",
         "Trạng thái 5 hành cân bằng nhờ tương khắc chế lẫn nhau.", 22),
        # Trang 23
        ("Trùng quái", "重卦",
         "Quẻ 6 vạch do 2 quẻ 3 vạch chồng lên. Cũng gọi Biệt quái.", 23),
        ("Cung Càn", "乾宮", "1/8 cung của 64 quẻ. Gốc quẻ Càn.", 23),
        ("Cung Đoài", "兌宮", "1/8 cung. Gốc quẻ Đoài.", 23),
        ("Cung Ly", "離宮", "1/8 cung. Gốc quẻ Ly.", 23),
        ("Cung Chấn", "震宮", "1/8 cung. Gốc quẻ Chấn.", 23),
        ("Cung Tốn", "巽宮", "1/8 cung. Gốc quẻ Tốn.", 23),
        ("Cung Khảm", "坎宮", "1/8 cung. Gốc quẻ Khảm.", 23),
        ("Cung Cấn", "艮宮", "1/8 cung. Gốc quẻ Cấn.", 23),
        ("Cung Khôn", "坤宮", "1/8 cung. Gốc quẻ Khôn.", 23),
        # Trang 24-25
        ("Mạnh Hỷ", "孟喜", "Đời Hán. Đề xướng Quái Khí học (với Kinh Phòng).", 24),
        ("Kinh Phòng", "京房",
         "Đời Hán (77-37 BC). Cùng Mạnh Hỷ. Sáng lập Kinh thị Dịch học.", 24),
        ("Quái Khí", "卦氣",
         "3 nhân tố: Quái + Khí hậu + Ngũ hành. Gốc Mạnh Hỷ + Kinh Phòng.", 24),
        ("Vượng", "旺",
         "1 trong 5 trạng thái quái khí (Vượng/Tướng/Hưu/Tù/Tử).", 24),
        ("Thìn Tuất Sửu Mùi", "辰戌丑未",
         "4 tháng đất: tháng 3, 9, 12, 6. Thổ vượng.", 25),
        ("Mùa xuân", "春", "Quái Khí Mộc vượng (Chấn, Tốn).", 25),
        ("Mùa hạ", "夏", "Quái Khí Hoả vượng (Ly).", 25),
        ("Mùa thu", "秋", "Quái Khí Kim vượng (Càn, Đoài).", 25),
        ("Mùa đông", "冬", "Quái Khí Thuỷ vượng (Khảm).", 25),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_26_30():
    """Trang 26-30: Quái Khí Suy + Thập Thiên Can + Thập Nhị Địa Chi + Lục Thập Giáp Tí."""
    s = get_store()
    master = _master_id()

    # ── Passage 26-27: Quái Khí SUY (mirror Vượng) ──
    if not _has_passage(CORPUS, 26, 27):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=26, page_end=27,
            topic="Quái Khí Suy — đối lập Vượng",
            raw_text=(
                "QUÁI KHÍ SUY (đối lập Vượng): nguyên lý 'hành nào vượng khắc "
                "hành bị khắc → hành bị khắc suy'.\n\n"
                "  Xuân  → Mộc vượng, khắc Thổ → Khôn, Cấn (Thổ) suy\n"
                "  Hạ    → Hoả vượng, khắc Kim → Càn, Đoài (Kim) suy\n"
                "  Thu   → Kim vượng, khắc Mộc → Chấn, Tốn (Mộc) suy\n"
                "  Đông  → Thuỷ vượng, khắc Hoả → Ly (Hoả) suy\n"
                "  Tháng Thìn/Tuất/Sửu/Mùi → Thổ vượng, khắc Thuỷ → Khảm suy\n\n"
                "Quái Khí Vượng và Suy là 1 quá trình tiêu trưởng ảnh hưởng "
                "lẫn nhau. Học thuyết Quái Khí = sản phẩm của Quái học + Vận khí học."
            ),
            summary_50w=(
                "Quái Khí Suy mirror Vượng: hành vượng khắc hành nào → hành đó suy. "
                "Đây là cặp dialectic — trụ cột Thể-Dụng Suy Vượng (Quyển 3)."
            ),
            is_canonical=True,
        ))

    # ── Passage 27-28: Thập Thiên Can ⭐ ──
    if not _has_passage(CORPUS, 27, 28):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=27, page_end=28,
            topic="Thập Thiên Can — 10 can ghi thời gian",
            raw_text=(
                "10 phù hiệu ghi DƯƠNG (ngày, trời):\n"
                "  Giáp 甲, Ất 乙, Bính 丙, Đinh 丁, Mậu 戊,\n"
                "  Kỷ 己, Canh 庚, Tân 辛, Nhâm 壬, Quý 癸.\n\n"
                "Phân âm-dương can:\n"
                "  Dương: Giáp, Bính, Mậu, Canh, Nhâm\n"
                "  Âm:    Ất,   Đinh, Kỷ,   Tân,   Quý\n\n"
                "Kết hợp ngũ hành + phương vị:\n"
                "  Giáp, Ất  → Đông → Mộc  (Giáp dương mộc, Ất âm mộc)\n"
                "  Bính, Đinh → Nam → Hoả (Bính dương hoả, Đinh âm hoả)\n"
                "  Mậu, Kỷ   → Trung → Thổ (Mậu dương thổ, Kỷ âm thổ)\n"
                "  Canh, Tân → Tây → Kim  (Canh dương kim, Tân âm kim)\n"
                "  Nhâm, Quý → Bắc → Thuỷ (Nhâm dương thuỷ, Quý âm thuỷ)"
            ),
            summary_50w=(
                "Thập thiên can = 10 phù hiệu ghi dương (ngày, trời). Phân âm-dương, "
                "phối ngũ hành + phương vị. Input gốc cho lục thập giáp tí."
            ),
            is_canonical=True,
        ))

    # ── Passage 29: Thập Nhị Địa Chi ⭐ ──
    if not _has_passage(CORPUS, 29, 29):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=29, page_end=29,
            topic="Thập Nhị Địa Chi — 12 chi + 12 con giáp",
            raw_text=(
                "12 phù hiệu ghi ÂM (tháng, đất):\n"
                "  Tí, Sửu, Dần, Mão, Thìn, Tỵ,\n"
                "  Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.\n\n"
                "Phối hành + con giáp:\n"
                "  Tí  - Thuỷ - Chuột (Thử)\n"
                "  Sửu - Thổ  - Trâu (Ngưu)\n"
                "  Dần - Mộc  - Hổ\n"
                "  Mão - Mộc  - Thỏ\n"
                "  Thìn - Thổ - Rồng (Long)\n"
                "  Tỵ  - Hoả  - Rắn (Xà)\n"
                "  Ngọ - Hoả  - Ngựa (Mã)\n"
                "  Mùi - Thổ  - Dê (Dương)\n"
                "  Thân - Kim - Khỉ (Hầu)\n"
                "  Dậu - Kim  - Gà (Kê)\n"
                "  Tuất - Thổ - Chó (Khuyển)\n"
                "  Hợi - Thuỷ - Lợn (Trư)\n\n"
                "Dương chi: Tí, Dần, Thìn, Ngọ, Thân, Tuất\n"
                "Âm chi:    Sửu, Mão, Tỵ, Mùi, Dậu, Hợi"
            ),
            summary_50w=(
                "Thập nhị địa chi = 12 phù hiệu ghi âm (tháng, đất). Phối hành + "
                "con giáp. Phân âm-dương chi. Vòng quay 12 tháng = 1 năm."
            ),
            is_canonical=True,
        ))

    # ── Passage 30: Lục Thập Giáp Tí ⭐ ──
    if not _has_passage(CORPUS, 30, 30):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=30, page_end=30,
            topic="Lục Thập Giáp Tí — chu kỳ 60",
            raw_text=(
                "Kết hợp 10 thiên can × 12 địa chi → 60 phù hiệu không trùng. "
                "Đó là LỤC THẬP GIÁP TÍ.\n\n"
                "Ứng dụng: ghi năm, tháng, ngày, giờ.\n"
                "Khởi đầu: Giáp Tí.\n\n"
                "Để trở lại can+chi cũ:\n"
                "  Can luân 6 lần (10 năm/chu) → 60 năm\n"
                "  Chi luân 5 lần (12 năm/chu) → 60 năm\n"
                "  Giao điểm = 60 năm = 1 'Chu' (Hoa Giáp).\n\n"
                "Quan hệ Thiên Can ↔ Địa Chi:\n"
                "  Thiên can = thân cây (trên — dương)\n"
                "  Địa chi  = cành cây (dưới — âm)\n\n"
                "Nguồn gốc số học:\n"
                "  5 (giữa số dương Hà Đồ) × 2 = 10 thiên can\n"
                "  6 (giữa số âm Hà Đồ) × 2 = 12 địa chi"
            ),
            summary_50w=(
                "Lục thập giáp tí = 10 can × 12 chi luân ghép thành 60 phù hiệu, "
                "khởi từ Giáp Tí. 60 năm = 1 Chu = 1 Hoa Giáp. Gốc số học từ Hà Đồ."
            ),
            is_canonical=True,
        ))

    # ── Methods ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Quái Khí Suy",
        name_zh="卦氣衰",
        domain="đọc",
        inputs_required=["quẻ + mùa"],
        procedure_steps=[
            "Xuân (Mộc vượng) → Khôn, Cấn (Thổ) suy",
            "Hạ (Hoả vượng) → Càn, Đoài (Kim) suy",
            "Thu (Kim vượng) → Chấn, Tốn (Mộc) suy",
            "Đông (Thuỷ vượng) → Ly (Hoả) suy",
            "Thìn/Tuất/Sửu/Mùi (Thổ vượng) → Khảm (Thuỷ) suy",
        ],
        output_format="Quẻ suy trong mùa",
        notes="Trang 26-27 — Cặp dialectic với Quái Khí Vượng.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Thập Thiên Can",
        name_zh="十天干",
        domain="đọc",
        inputs_required=["can: 1 trong 10"],
        procedure_steps=[
            "Giáp Ất → Mộc / Đông",
            "Bính Đinh → Hoả / Nam",
            "Mậu Kỷ → Thổ / Trung",
            "Canh Tân → Kim / Tây",
            "Nhâm Quý → Thuỷ / Bắc",
            "Dương: Giáp Bính Mậu Canh Nhâm | Âm: Ất Đinh Kỷ Tân Quý",
        ],
        output_format="Hành + phương + âm/dương của can",
        notes="Trang 27-28 — Phù hiệu ghi dương (ngày, trời).",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Thập Nhị Địa Chi",
        name_zh="十二地支",
        domain="đọc",
        inputs_required=["chi: 1 trong 12"],
        procedure_steps=[
            "Tí-Thuỷ-Chuột | Sửu-Thổ-Trâu | Dần-Mộc-Hổ | Mão-Mộc-Thỏ",
            "Thìn-Thổ-Rồng | Tỵ-Hoả-Rắn | Ngọ-Hoả-Ngựa | Mùi-Thổ-Dê",
            "Thân-Kim-Khỉ | Dậu-Kim-Gà | Tuất-Thổ-Chó | Hợi-Thuỷ-Lợn",
            "Dương chi: Tí Dần Thìn Ngọ Thân Tuất | Âm chi: Sửu Mão Tỵ Mùi Dậu Hợi",
        ],
        output_format="Hành + con giáp + âm/dương",
        notes="Trang 29 — Phù hiệu ghi âm (tháng, đất).",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Lục Thập Giáp Tí (chu 60)",
        name_zh="六十甲子",
        domain="ứng_kỳ",
        inputs_required=["thời điểm (năm/tháng/ngày/giờ)"],
        procedure_steps=[
            "10 can × 12 chi luân ghép = 60 phù hiệu",
            "Khởi từ Giáp Tí",
            "60 năm = 1 Chu (Hoa Giáp)",
            "Can chu kỳ 10 luân 6 lần | Chi chu kỳ 12 luân 5 lần",
        ],
        output_format="Can-Chi của năm/tháng/ngày/giờ",
        notes="Trang 30 — Foundation cho mọi pp ứng kỳ Mai Hoa qua thời gian.",
    ))

    # ── Concepts ──
    new_concepts = [
        # Trang 26-27 — Suy + Tiêu trưởng
        ("Suy", "衰", "1 trong 5 trạng thái Quái khí. Đối lập Vượng.", 26),
        ("Tiêu trưởng", "消長", "Quá trình co-giãn ảnh hưởng lẫn nhau giữa Vượng-Suy.", 27),
        ("Vận khí học", "運氣學",
         "Học thuyết khí vận hành. Gốc của Quái khí học cùng với Quái học.", 27),
        # Trang 27-28 — Thập Thiên Can
        ("Thập Thiên Can", "十天干",
         "10 can ghi dương (ngày, trời). Giáp Ất Bính Đinh Mậu Kỷ Canh Tân Nhâm Quý.", 27),
        ("Giáp", "甲", "Can 1, dương mộc, Đông.", 27),
        ("Ất", "乙", "Can 2, âm mộc, Đông.", 27),
        ("Bính", "丙", "Can 3, dương hoả, Nam.", 27),
        ("Đinh", "丁", "Can 4, âm hoả, Nam.", 27),
        ("Mậu", "戊", "Can 5, dương thổ, Trung.", 27),
        ("Kỷ", "己", "Can 6, âm thổ, Trung.", 27),
        ("Canh", "庚", "Can 7, dương kim, Tây.", 27),
        ("Tân", "辛", "Can 8, âm kim, Tây.", 27),
        ("Nhâm", "壬", "Can 9, dương thuỷ, Bắc.", 27),
        ("Quý", "癸", "Can 10, âm thuỷ, Bắc.", 27),
        ("Dương can", "陽干", "5 can dương: Giáp Bính Mậu Canh Nhâm.", 28),
        ("Âm can", "陰干", "5 can âm: Ất Đinh Kỷ Tân Quý.", 28),
        # Trang 29 — 12 Địa Chi
        ("Thập Nhị Địa Chi", "十二地支",
         "12 chi ghi âm (tháng, đất). Tí Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi.", 29),
        ("Tí", "子", "Chi 1, Thuỷ, Chuột. Khởi 'Chu'.", 29),
        ("Sửu", "丑", "Chi 2, Thổ, Trâu.", 29),
        ("Dần", "寅", "Chi 3, Mộc, Hổ.", 29),
        ("Mão", "卯", "Chi 4, Mộc, Thỏ.", 29),
        ("Thìn", "辰", "Chi 5, Thổ, Rồng.", 29),
        ("Tỵ", "巳", "Chi 6, Hoả, Rắn.", 29),
        ("Ngọ", "午", "Chi 7, Hoả, Ngựa.", 29),
        ("Mùi", "未", "Chi 8, Thổ, Dê.", 29),
        ("Thân", "申", "Chi 9, Kim, Khỉ.", 29),
        ("Dậu", "酉", "Chi 10, Kim, Gà.", 29),
        ("Tuất", "戌", "Chi 11, Thổ, Chó.", 29),
        ("Hợi", "亥", "Chi 12, Thuỷ, Lợn.", 29),
        ("Dương chi", "陽支", "6 chi dương: Tí Dần Thìn Ngọ Thân Tuất.", 29),
        ("Âm chi", "陰支", "6 chi âm: Sửu Mão Tỵ Mùi Dậu Hợi.", 29),
        # Trang 30 — Lục Thập Giáp Tí
        ("Lục Thập Giáp Tí", "六十甲子",
         "60 phù hiệu can-chi luân ghép. Khởi Giáp Tí. 60 năm 1 Chu.", 30),
        ("Hoa Giáp", "華甲", "1 chu 60 năm = 1 Hoa Giáp.", 30),
        ("Giáp Tí", "甲子", "Phù hiệu khởi đầu chu 60.", 30),
        ("Chu (chu kỳ)", "周",
         "1 vòng 60 năm. Sau 60 năm, can-chi quay lại như cũ.", 30),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_page_31():
    """Trang 31: Kết hợp Địa Chi với Ngũ Hành + 12 loài cầm tinh (kết chương foundation)."""
    s = get_store()
    master = _master_id()

    if not _has_passage(CORPUS, 31, 31):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=31, page_end=31,
            topic="Địa Chi × Ngũ Hành × Âm-Dương (kết chương Can-Chi)",
            raw_text=(
                "12 ĐỊA CHI × NGŨ HÀNH × ÂM-DƯƠNG:\n"
                "  Dần (Dương Mộc), Mão (Âm Mộc) — Mộc\n"
                "  Tỵ (Âm Hoả), Ngọ (Dương Hoả) — Hoả  *\n"
                "  Thân (Dương Kim), Dậu (Âm Kim) — Kim\n"
                "  Hợi (Âm Thuỷ), Tí (Dương Thuỷ) — Thuỷ\n"
                "  Thìn, Tuất (Dương Thổ); Sửu, Mùi (Âm Thổ) — Thổ\n\n"
                "* Ngọ-Hoả là Dương ngoài, Âm trong → trong chiêm tinh "
                "thường coi Tỵ Dương Ngọ Âm. Mai Hoa dùng dạng thuận: Tỵ Âm, Ngọ Dương.\n\n"
                "Chi tiết 12 loài cầm tinh đã ghi trang 29."
            ),
            summary_50w=(
                "Trang 31 kết phần Can-Chi: chi tiết âm-dương từng địa chi theo "
                "ngũ hành. Tỵ Âm Hoả vs Ngọ Dương Hoả là điểm cần chú ý."
            ),
            is_canonical=True,
        ))

    # Concepts âm-dương từng chi đã có. Chỉ thêm note đặc biệt:
    _add_concept(
        canonical_vi="Quy tắc âm-dương địa chi theo ngũ hành",
        canonical_zh="",
        note=(
            "Dần-Mộc(D), Mão-Mộc(Â); Tỵ-Hoả(Â), Ngọ-Hoả(D); "
            "Thân-Kim(D), Dậu-Kim(Â); Hợi-Thuỷ(Â), Tí-Thuỷ(D); "
            "Thìn/Tuất-Thổ(D), Sửu/Mùi-Thổ(Â)."
        ),
        page=31,
    )


def extract_pages_32_35():
    """Chương lớn: BÁT QUÁI — Tượng + Tiên Thiên + Hậu Thiên + Gia đình quẻ.

    Đây là PHẦN GIỚI THIỆU 8 QUẺ DỊCH ĐẦU TIÊN trong sách Mai Hoa."""
    s = get_store()
    master = _master_id()

    # ── Add Chu Văn Vương — tác giả Hậu Thiên Bát Quái ──
    from engine.yi_wiki.models import TIER_MASTER_TEACHER
    s.upsert_author(Author(
        name_vi="Chu Văn Vương",
        name_zh="周文王",
        tier_in_lineage=TIER_MASTER_TEACHER,
        era="tiền-tần",
        worldview_school="dịch-học",
        bio_summary=(
            "Vua nhà Chu (~1152-1056 BC). Bị vua Trụ cầm tù ở Dữu Lý. "
            "Soạn Hậu Thiên Bát Quái + 64 quẻ Chu Dịch. Là Tổ của Chu Dịch."
        ),
        birth_year=-1152, death_year=-1056,
    ))

    # ── Passage 32-33: Tượng của tám quẻ + Tiên Thiên ──
    if not _has_passage(CORPUS, 32, 33):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=32, page_end=33,
            topic="Tượng của 8 quẻ + Tiên Thiên Bát Quái (Phục Hy)",
            raw_text=(
                "MNEMONICS NHỚ HÌNH 8 QUẺ:\n"
                "  Càn tam liên   ☰ — 3 vạch liền\n"
                "  Khôn lục đoạn  ☷ — 6 đoạn (3 hào âm)\n"
                "  Chấn ngưỡng vu ☳ — ngửa ống (1 dương dưới, 2 âm trên)\n"
                "  Cấn phúc uyển  ☶ — úp bát (1 dương trên, 2 âm dưới)\n"
                "  Ly trung hư    ☲ — rỗng giữa\n"
                "  Khảm trung mãn ☵ — đầy giữa\n"
                "  Đoài thượng khuyết ☱ — khuyết trên\n"
                "  Tốn hạ đoạn    ☴ — đứt dưới\n\n"
                "BÁT QUÁI TƯỢNG TỰ NHIÊN:\n"
                "  Càn = trời  | Khôn = đất\n"
                "  Đoài = đầm  | Tốn = gió\n"
                "  Ly = mặt trời (lửa) | Khảm = mặt trăng (nước)\n"
                "  Chấn = sấm  | Cấn = núi\n\n"
                "TIÊN THIÊN BÁT QUÁI (Phục Hy):\n"
                "  Càn Nam, Khôn Bắc → trời đất định vị\n"
                "  Cấn Tây Bắc, Đoài Đông Nam → núi đầm thông khí\n"
                "  Chấn Đông Bắc, Tốn Tây Nam → sấm gió xô xát\n"
                "  Khảm Tây, Ly Đông → nước lửa thân thiết\n\n"
                "Thuyết Quái Truyện: 'Trời đất định vị, núi đầm thông khí, "
                "sấm gió cùng nhau xô xát, nước lửa không diệt nhau, 8 quẻ giao nhau.'\n\n"
                "Thứ tự Tiên Thiên: Càn → Đoài → Ly → Chấn → Tốn → Khảm → Cấn → Khôn."
            ),
            summary_50w=(
                "Mnemonics 8 quẻ (tam liên, lục đoạn...) + biểu tượng tự nhiên + "
                "Tiên Thiên Bát Quái Phục Hy. 4 cặp đối: trời-đất, núi-đầm, sấm-gió, nước-lửa."
            ),
            is_canonical=True,
        ))

    # ── Passage 34: Tiên Thiên + Tam Tài + chuyển Hậu Thiên ──
    if not _has_passage(CORPUS, 34, 34):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=34, page_end=34,
            topic="Tam Tài + Hậu Thiên Bát Quái (Chu Văn Vương)",
            raw_text=(
                "TAM TÀI (3 ngôi):\n"
                "  Vạch trên = Trời | Vạch giữa = Người | Vạch dưới = Đất.\n"
                "  Khẳng định vai trò Người trong vũ trụ.\n\n"
                "HẬU THIÊN BÁT QUÁI (Chu Văn Vương, làm khi bị Trụ cầm tù ở Dữu Lý):\n"
                "  Thuyết Quái Truyện ghi:\n"
                "    'Đề xuất ở Chấn, gọn gàng ở Tốn, gặp gỡ ở Ly, làm việc ở Khôn,\n"
                "     vui mừng nói ở Đoài, đánh nhau ở Càn, khó nhọc ở Khảm,\n"
                "     hoàn thành ở Cấn.'\n\n"
                "  Phương vị Hậu Thiên:\n"
                "    Chấn (Đông) → Tốn (Đông Nam) → Ly (Nam) → Khôn (Tây Nam)\n"
                "    → Đoài (Tây) → Càn (Tây Bắc) → Khảm (Bắc) → Cấn (Đông Bắc)\n\n"
                "  Tiên Thiên = THỂ — đạo âm dương tiêu trưởng trong trời đất\n"
                "  Hậu Thiên = DỤNG — ngũ hành sinh hoá vạn vật"
            ),
            summary_50w=(
                "Hậu Thiên Bát Quái của Chu Văn Vương — vận hành theo mùa, ngũ hành. "
                "Khác Tiên Thiên (Phục Hy, thuần âm dương). Đây là cặp Thể-Dụng thứ 2."
            ),
            is_canonical=True,
        ))

    # ── Passage 35: Gia đình bát quái (Lục Tử) ⭐ ──
    if not _has_passage(CORPUS, 35, 35):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=35, page_end=35,
            topic="Gia đình Bát Quái — Lục Tử (Càn-Khôn + 6 con)",
            raw_text=(
                "BÁT QUÁI LÀ 1 GIA ĐÌNH:\n"
                "  Càn = CHA  ☰ (3 hào dương)\n"
                "  Khôn = MẸ  ☷ (3 hào âm)\n\n"
                "  Càn cầu Khôn (lấy hào của Khôn):\n"
                "    Hào dưới Khôn → Chấn ☳ TRƯỞNG NAM\n"
                "    Hào giữa Khôn → Khảm ☵ TRUNG NAM\n"
                "    Hào trên Khôn → Cấn ☶ THIẾU NAM\n\n"
                "  Khôn cầu Càn (lấy hào của Càn):\n"
                "    Hào dưới Càn → Tốn ☴ TRƯỞNG NỮ\n"
                "    Hào giữa Càn → Ly  ☲ TRUNG NỮ\n"
                "    Hào trên Càn → Đoài ☱ THIẾU NỮ\n\n"
                "(Hệ Từ Thượng Truyện: 'Đạo Càn làm con trai, đạo Khôn làm con gái')\n\n"
                "NGŨ HÀNH + MÙA HẬU THIÊN:\n"
                "  Khảm-Thuỷ-Đông | Ly-Hoả-Hạ\n"
                "  Càn-Kim, Đoài-Kim — Thu\n"
                "  Chấn-Mộc, Tốn-Mộc — Xuân\n"
                "  Cấn-Thổ, Khôn-Thổ — chuyển mùa (18 ngày cuối)\n\n"
                "ÂM-DƯƠNG QUÁI (Hậu Thiên):\n"
                "  Quái Dương: Càn, Khảm, Cấn, Chấn\n"
                "  Quái Âm:    Tốn, Ly, Khôn, Đoài"
            ),
            summary_50w=(
                "Bát Quái = 1 gia đình. Càn cha, Khôn mẹ, 6 con = Lục Tử (3 nam: Chấn/Khảm/Cấn, "
                "3 nữ: Tốn/Ly/Đoài) — qua quy luật lấy hào. Foundation cho Lục Thân."
            ),
            is_canonical=True,
        ))

    # ── 8 PASSAGE — mỗi quẻ 1 entry chi tiết (đặc biệt) ──
    # Sẽ insert dưới dạng concept "Quẻ X" rất rich
    quai_specs = [
        # (vi, zh, hexagram, mnemonic, tự nhiên, tien_thien_pos, hau_thien_pos, hành, gia_đình, am_duong)
        ("Càn", "乾", "☰", "Tam liên (3 vạch liền)", "Trời",
         "Nam", "Tây Bắc", "Kim (Dương)", "Cha (toàn dương)", "Dương quái"),
        ("Khôn", "坤", "☷", "Lục đoạn (6 đoạn)", "Đất",
         "Bắc", "Tây Nam", "Thổ (Âm)", "Mẹ (toàn âm)", "Âm quái"),
        ("Chấn", "震", "☳", "Ngưỡng vu (ngửa ống)", "Sấm",
         "Đông Bắc", "Đông", "Mộc (Dương)", "Trưởng nam", "Dương quái"),
        ("Tốn", "巽", "☴", "Hạ đoạn (đứt dưới)", "Gió",
         "Tây Nam", "Đông Nam", "Mộc (Âm)", "Trưởng nữ", "Âm quái"),
        ("Khảm", "坎", "☵", "Trung mãn (đầy giữa)", "Nước / Trăng",
         "Tây", "Bắc", "Thuỷ", "Trung nam", "Dương quái"),
        ("Ly", "離", "☲", "Trung hư (rỗng giữa)", "Lửa / Mặt trời",
         "Đông", "Nam", "Hoả", "Trung nữ", "Âm quái"),
        ("Cấn", "艮", "☶", "Phúc uyển (úp bát)", "Núi",
         "Tây Bắc", "Đông Bắc", "Thổ (Dương)", "Thiếu nam", "Dương quái"),
        ("Đoài", "兌", "☱", "Thượng khuyết (khuyết trên)", "Đầm",
         "Đông Nam", "Tây", "Kim (Âm)", "Thiếu nữ", "Âm quái"),
    ]
    for vi, zh, hexa, mnemonic, nature, tien, hau, hanh, family, ad in quai_specs:
        s.upsert_concept(ConceptIndex(
            canonical_vi=f"Quẻ {vi}",
            canonical_zh=f"{zh}卦",
            aliases=[vi, zh, hexa],
            short_note=(
                f"{hexa} {mnemonic}. Tượng: {nature}. "
                f"Tiên Thiên: {tien} | Hậu Thiên: {hau}. "
                f"Ngũ hành: {hanh}. Gia đình: {family}. {ad}."
            ),
            first_seen_corpus=CORPUS,
            first_seen_page=32,
        ))

    # ── Method: Tiên Thiên Bát Quái + Hậu Thiên Bát Quái ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Tiên Thiên Bát Quái (Phục Hy)",
        name_zh="先天八卦",
        domain="đọc",
        inputs_required=["8 quẻ"],
        procedure_steps=[
            "Càn Nam, Khôn Bắc (trời-đất định vị)",
            "Cấn Tây Bắc, Đoài Đông Nam (núi-đầm thông khí)",
            "Chấn Đông Bắc, Tốn Tây Nam (sấm-gió xô xát)",
            "Khảm Tây, Ly Đông (nước-lửa thân thiết)",
            "Thứ tự thuận: Càn-Đoài-Ly-Chấn-Tốn-Khảm-Cấn-Khôn",
        ],
        output_format="Phương vị 8 quẻ theo Tiên Thiên — Thể của Dịch",
        notes="Trang 33-34 — Phục Hy lập. Nói âm dương tiêu trưởng.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Hậu Thiên Bát Quái (Chu Văn Vương)",
        name_zh="後天八卦",
        domain="đọc",
        inputs_required=["8 quẻ"],
        procedure_steps=[
            "Chấn Đông → Tốn Đông Nam → Ly Nam → Khôn Tây Nam",
            "Đoài Tây → Càn Tây Bắc → Khảm Bắc → Cấn Đông Bắc",
            "Thuyết Quái: 'Đề xuất ở Chấn... hoàn thành ở Cấn'",
            "Khởi từ Chấn (mùa xuân, vạn vật xuất)",
        ],
        output_format="Phương vị 8 quẻ theo Hậu Thiên — Dụng của Dịch",
        notes="Trang 34-35 — Chu Văn Vương lập khi bị cầm tù ở Dữu Lý. Nói ngũ hành sinh hoá.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Bát Quái Tượng Lệ (mnemonic 8 quẻ)",
        name_zh="八卦象例",
        domain="đọc",
        inputs_required=["hình quẻ 3 hào"],
        procedure_steps=[
            "Càn tam liên (3 vạch liền)",
            "Khôn lục đoạn (6 đoạn = 3 hào âm)",
            "Chấn ngưỡng vu (ngửa ống — 1 dương dưới)",
            "Cấn phúc uyển (úp bát — 1 dương trên)",
            "Ly trung hư (rỗng giữa — 1 âm giữa)",
            "Khảm trung mãn (đầy giữa — 1 dương giữa)",
            "Đoài thượng khuyết (khuyết trên — 1 âm trên)",
            "Tốn hạ đoạn (đứt dưới — 1 âm dưới)",
        ],
        output_format="Nhận diện nhanh quẻ qua hình",
        notes="Trang 32 — mnemonic chuẩn để học thuộc 8 quẻ.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Gia đình Bát Quái (Lục Tử)",
        name_zh="八卦家庭",
        domain="đọc",
        inputs_required=["1 trong 8 quẻ"],
        procedure_steps=[
            "Càn = Cha (toàn dương) | Khôn = Mẹ (toàn âm)",
            "Càn cầu Khôn hào dưới → Chấn (trưởng nam)",
            "Càn cầu Khôn hào giữa → Khảm (trung nam)",
            "Càn cầu Khôn hào trên → Cấn (thiếu nam)",
            "Khôn cầu Càn hào dưới → Tốn (trưởng nữ)",
            "Khôn cầu Càn hào giữa → Ly (trung nữ)",
            "Khôn cầu Càn hào trên → Đoài (thiếu nữ)",
        ],
        output_format="Vai gia đình + tuổi đời + giới",
        notes="Trang 35 — Foundation cho Lục Thân (6 mối quan hệ) ở Quyển 5.",
    ))

    # ── Concepts ──
    new_concepts = [
        # Mnemonic 8 quẻ
        ("Tam liên", "三連", "Mnemonic Càn — 3 vạch liền.", 32),
        ("Lục đoạn", "六斷", "Mnemonic Khôn — 6 đoạn.", 32),
        ("Ngưỡng vu", "仰盂", "Mnemonic Chấn — ngửa ống.", 32),
        ("Phúc uyển", "覆碗", "Mnemonic Cấn — úp bát.", 32),
        ("Trung hư", "中虛", "Mnemonic Ly — rỗng giữa.", 32),
        ("Trung mãn", "中滿", "Mnemonic Khảm — đầy giữa.", 32),
        ("Thượng khuyết", "上缺", "Mnemonic Đoài — khuyết trên.", 32),
        ("Hạ đoạn", "下斷", "Mnemonic Tốn — đứt dưới.", 32),
        # Concept thiết yếu
        ("Tiên Thiên Bát Quái", "先天八卦",
         "Đồ Phục Hy. Càn Nam/Khôn Bắc. Thể của Dịch — âm dương tiêu trưởng.", 33),
        ("Hậu Thiên Bát Quái", "後天八卦",
         "Đồ Chu Văn Vương. Ly Nam/Khảm Bắc. Dụng của Dịch — ngũ hành sinh hoá.", 34),
        ("Thuyết Quái Truyện", "說卦傳",
         "1 trong Thập Dực (10 truyện) của Chu Dịch. Ghi tượng + phương vị bát quái.", 33),
        ("Tam Tài", "三才",
         "Trời (vạch trên) - Người (giữa) - Đất (dưới). Vai con người trong vũ trụ.", 34),
        ("Chu Văn Vương", "周文王",
         "Vua nhà Chu, soạn Hậu Thiên + 64 quẻ Chu Dịch khi bị Trụ cầm tù ở Dữu Lý.", 34),
        ("Dữu Lý", "羑里",
         "Ngục thành nơi Chu Văn Vương bị vua Trụ cầm tù, soạn Chu Dịch.", 34),
        ("Vua Trụ", "紂王", "Vua cuối nhà Thương — cầm tù Chu Văn Vương ở Dữu Lý.", 34),
        # Family / Lục Tử
        ("Lục Tử", "六子",
         "6 con của Càn-Khôn: Chấn/Khảm/Cấn (3 nam), Tốn/Ly/Đoài (3 nữ).", 35),
        ("Trưởng nam", "長男", "Chấn — con trai đầu của Càn-Khôn.", 35),
        ("Trung nam", "中男", "Khảm — con trai giữa.", 35),
        ("Thiếu nam", "少男", "Cấn — con trai út.", 35),
        ("Trưởng nữ", "長女", "Tốn — con gái đầu.", 35),
        ("Trung nữ", "中女", "Ly — con gái giữa.", 35),
        ("Thiếu nữ", "少女", "Đoài — con gái út.", 35),
        ("Cha (Càn)", "父", "Càn ☰ — toàn dương, trời.", 35),
        ("Mẹ (Khôn)", "母", "Khôn ☷ — toàn âm, đất.", 35),
        ("Hệ Từ Thượng Truyện", "繫辭上傳",
         "1 trong Thập Dực Chu Dịch. Nói nguyên lý Đạo Càn / Đạo Khôn.", 35),
        ("Quái Dương (Hậu Thiên)", "陽卦",
         "4 quẻ dương: Càn, Khảm, Cấn, Chấn.", 35),
        ("Quái Âm (Hậu Thiên)", "陰卦",
         "4 quẻ âm: Tốn, Ly, Khôn, Đoài.", 35),
        ("Tượng tự nhiên 8 quẻ", "八卦象",
         "Càn-trời, Khôn-đất, Chấn-sấm, Tốn-gió, Khảm-trăng/nước, Ly-mặt trời/lửa, Cấn-núi, Đoài-đầm.", 33),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_36_45():
    """CHƯƠNG PHÉP CHIÊM ĐOÁN — thuật toán Mai Hoa cốt lõi.

    Bao gồm: Ngoạn Pháp (triết lý), Quái Trừ 8, Hào Trừ 6, Hỗ Quái,
    pp Niên-Nguyệt-Nhật-Thời (cách bốc phổ biến nhất)."""
    s = get_store()
    master = _master_id()

    # ── Passage 36-38: Ngoạn Pháp — bài thơ triết lý ⭐ (kết với động tâm) ──
    if not _has_passage(CORPUS, 36, 38):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=36, page_end=38,
            topic="Ngoạn Pháp — Bài thơ triết lý chiêm bốc + Tâm là gốc",
            raw_text=(
                "BÀI THƠ MỞ ĐẦU PHÉP CHIÊM:\n"
                "  'Dịch trung bí mật cùng thiên địa,\n"
                "   Tạo hoá thiên cơ tiết vị nhiên.\n"
                "   Trung hữu thần minh tri họa phúc,\n"
                "   Tòng lai thiết mạc giáo khinh truyền.'\n\n"
                "Ý: Sự huyền diệu Chu Dịch bao trùm thiên địa. "
                "Cơ mật trời đất, biến hoá vạn vật chưa thể tiết lộ. "
                "Trong Dịch có vị thần sáng suốt biết hoạ phúc. "
                "Đạo này chớ truyền tuỳ tiện.\n\n"
                "BÀI THƠ NGOẠN PHÁP (cốt lõi):\n"
                "  'Nhất vật tòng lai hữu nhất thân,\n"
                "   Nhất thân hoàn hữu nhất Càn Khôn.\n"
                "   Năng trì vạn vật bị ư ngã,\n"
                "   Khẳng bả tam biệt lập căn nguyên;\n"
                "   Thiên hướng nhất trung phân tạo hoá,\n"
                "   ★ NHÂN Ư TÂM THƯỢNG KHỞI KINH LUÂN ★\n"
                "   Tiên nhân diệc hữu lưỡng ban thoại,\n"
                "   Đạo bất hư truyền chỉ tại nhân.'\n\n"
                "Ý cốt lõi:\n"
                "  - Mỗi vật có Càn-Khôn riêng. Vạn vật tồn tại trong ta.\n"
                "  - Trời đất từ Thái Cực hỗn độn sáng tạo và biến hoá.\n"
                "  - ⭐ CON NGƯỜI TỪ TÂM THÁI CỰC mà bồi dưỡng tài năng — \n"
                "    điều khiển vạn vật (← đây chính là 'động tâm', tâm là gốc).\n"
                "  - Đạo Dịch không hư truyền, chỉ tại con người."
            ),
            summary_50w=(
                "★ Bài thơ Ngoạn Pháp dạy: TÂM là gốc, Càn-Khôn ở trong từng vật. "
                "Câu 'Nhân ư tâm thượng khởi kinh luận' là gốc TIÊN THIÊN TÂM PHÁP "
                "— foundation của Master-Apprentice Digital Twin."
            ),
            is_canonical=True,
        ))

    # ── Passage 39-40: Quái Trừ 8 ⭐ ──
    if not _has_passage(CORPUS, 39, 40):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=39, page_end=40,
            topic="Quái Trừ 8 (Quái dĩ bát trừ) — xác định quẻ từ số",
            raw_text=(
                "NGUYÊN TẮC: Mọi số bốc được, đem trừ 8 (hoặc chia 8, lấy dư), "
                "số dư = số quẻ.\n\n"
                "Bảng tra:\n"
                "  1 → Càn   ☰\n"
                "  2 → Đoài  ☱\n"
                "  3 → Ly    ☲\n"
                "  4 → Chấn  ☳\n"
                "  5 → Tốn   ☴\n"
                "  6 → Khảm  ☵\n"
                "  7 → Cấn   ☶\n"
                "  8 → Khôn  ☷  (chia hết cho 8 → Khôn)\n\n"
                "Ví dụ:\n"
                "  Số 9   → 9-8=1     → Càn\n"
                "  Số 25  → 25-8-8-8=1 → Càn\n"
                "  Số 49  → 49÷8 dư 1 → Càn\n\n"
                "Nhận xét: 'Quẻ sản sinh phép trừ, hay phép trừ toán học sản "
                "sinh quẻ — vấn đề đáng nghiên cứu.'"
            ),
            summary_50w=(
                "Quái Trừ 8 = thuật toán cơ bản nhất: số bất kỳ mod 8 → 1 trong 8 quẻ. "
                "Số = 0 thì lấy Khôn (8). Input cho mọi pp bốc qua số."
            ),
            is_canonical=True,
        ))

    # ── Passage 41: Hào Trừ 6 ⭐ ──
    if not _has_passage(CORPUS, 41, 41):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=41, page_end=41,
            topic="Hào Trừ 6 (Hào dĩ lục trừ) — xác định động hào",
            raw_text=(
                "NGUYÊN TẮC: (Số quẻ trên + Số quẻ dưới) ÷ 6, lấy số dư = ĐỘNG HÀO.\n\n"
                "Ví dụ:\n"
                "  Quẻ trên = 30, Quẻ dưới = 39\n"
                "  (30+39) ÷ 6 = 11 dư 3 → Hào thứ 3 là ĐỘNG HÀO\n\n"
                "QUY TẮC ĐỘNG HÀO:\n"
                "  - Nếu 1 hào động: dương hào → biến âm hào, âm hào → biến dương hào\n"
                "  - Sau biến → có QUẺ BIẾN\n\n"
                "Số mod 6 = 0 thì lấy 6 (hào thượng)."
            ),
            summary_50w=(
                "Hào Trừ 6 = (số quẻ trên + dưới) mod 6 → động hào. Hào động đổi "
                "âm-dương → sinh quẻ biến. Input cho pp Thể-Dụng + đoán theo hào."
            ),
            is_canonical=True,
        ))

    # ── Passage 42-43: Hỗ Quái ⭐ ──
    if not _has_passage(CORPUS, 42, 43):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=42, page_end=43,
            topic="Hỗ Quái (Hỗ quái lệ) — quẻ ẩn từ hào 2-3-4 và 3-4-5",
            raw_text=(
                "CHÍNH THỂ vs HỖ THỂ:\n"
                "  Chính thể: 3 hào dưới = nội quái, 3 hào trên = ngoại quái.\n"
                "  Hỗ thể: lấy hào 2, 3, 4 làm quẻ DƯỚI mới;\n"
                "          lấy hào 3, 4, 5 làm quẻ TRÊN mới.\n"
                "  → Ghép thành 1 trùng quái mới = HỖ QUÁI.\n\n"
                "TRƯỜNG HỢP ĐẶC BIỆT:\n"
                "  Càn và Khôn sau khi tính hỗ vẫn là Càn-Khôn.\n"
                "  → Thường không dùng hỗ Càn-Khôn, mà dùng QUẺ BIẾN thay."
            ),
            summary_50w=(
                "Hỗ Quái = trùng quái mới từ hào 2-3-4 (quẻ dưới) + 3-4-5 (quẻ trên). "
                "Đây là 1 trong 3 thành phần chiêm: Chính - Hỗ - Biến."
            ),
            is_canonical=True,
        ))

    # ── Passage 43-45: Niên Nguyệt Nhật Thời Khởi Lệ ⭐⭐⭐ ──
    if not _has_passage(CORPUS, 43, 45):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=43, page_end=45,
            topic="Niên-Nguyệt-Nhật-Thời Khởi Lệ — bốc quẻ theo thời gian (CỐT LÕI MAI HOA)",
            raw_text=(
                "★★★ CÔNG THỨC GIEO QUẺ MAI HOA THEO THỜI GIAN ★★★\n\n"
                "BẢNG SỐ:\n"
                "  Năm (theo chi):\n"
                "    Tý=1, Sửu=2, Dần=3, Mão=4, Thìn=5, Tỵ=6,\n"
                "    Ngọ=7, Mùi=8, Thân=9, Dậu=10, Tuất=11, Hợi=12.\n"
                "  Tháng: tháng Giêng=1, ..., tháng Mười Hai=12.\n"
                "  Ngày: mồng 1=1, ..., ngày 30=30.\n"
                "  Giờ (theo chi):\n"
                "    Giờ Tý=1, Sửu=2, Dần=3, Mão=4, Thìn=5, Tỵ=6,\n"
                "    Ngọ=7, Mùi=8, Thân=9, Dậu=10, Tuất=11, Hợi=12.\n\n"
                "CÔNG THỨC:\n"
                "  QUẺ TRÊN (thượng quái) = (Năm + Tháng + Ngày) MOD 8\n"
                "  QUẺ DƯỚI (hạ quái) = (Năm + Tháng + Ngày + Giờ) MOD 8\n"
                "  ĐỘNG HÀO = (Năm + Tháng + Ngày + Giờ) MOD 6\n\n"
                "(Mod 0 thì lấy 8 cho quẻ, 6 cho hào.)\n\n"
                "→ Có ngay: chính quái, biến quái (qua động hào), hỗ quái.\n"
                "→ Ba quẻ này = bộ chiêm hoàn chỉnh để đọc Thể-Dụng."
            ),
            summary_50w=(
                "Niên-Nguyệt-Nhật-Thời = thuật toán bốc quẻ phổ biến nhất Mai Hoa. "
                "(Y+M+D) mod 8 = quẻ trên, (Y+M+D+H) mod 8 = quẻ dưới, "
                "(Y+M+D+H) mod 6 = động hào. Em sẽ implement thành tool."
            ),
            is_canonical=True,
        ))

    # ── METHODS ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Ngoạn Pháp (玩法)",
        name_zh="玩法",
        domain="đọc",
        inputs_required=["ý chí tâm thái"],
        procedure_steps=[
            "Hiểu: vạn vật có Càn-Khôn riêng, đều ở trong ta",
            "Hiểu: Trời đất từ Thái Cực hỗn độn sinh hoá",
            "★ Khởi kinh luân TỪ TÂM (Nhân ư tâm thượng khởi kinh luân)",
            "Tin: Đạo Dịch không hư truyền — chỉ tại người",
            "Chiêm là 'chơi' (ngoạn) — không phải nô lệ vận mệnh",
        ],
        output_format="Tâm thái đúng để chiêm",
        notes=(
            "Trang 36-38. ★ TỪ TÂM KHỞI KINH LUÂN = gốc Tiên Thiên Tâm Pháp "
            "= insight 'động tâm' anh chốt 2026-05-14."
        ),
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Quái Trừ 8 (Quái dĩ bát trừ)",
        name_zh="卦以八除",
        domain="bốc",
        inputs_required=["1 số nguyên dương"],
        procedure_steps=[
            "Số bốc được mod 8 → số dư",
            "Mod=0 thì lấy 8 (Khôn)",
            "Tra bảng: 1=Càn, 2=Đoài, 3=Ly, 4=Chấn, 5=Tốn, 6=Khảm, 7=Cấn, 8=Khôn",
        ],
        output_format="1 trong 8 quẻ",
        notes="Trang 39-40 — thuật toán cơ bản nhất biến số thành quẻ.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Hào Trừ 6 (Hào dĩ lục trừ)",
        name_zh="爻以六除",
        domain="bốc",
        inputs_required=["số quẻ trên + số quẻ dưới"],
        procedure_steps=[
            "(số quẻ trên + số quẻ dưới) mod 6 → số dư",
            "Mod=0 thì lấy 6 (hào thượng)",
            "Hào thứ N là ĐỘNG HÀO",
            "Nếu hào dương → biến âm; nếu hào âm → biến dương",
            "→ Sinh ra quẻ biến",
        ],
        output_format="Vị trí động hào (1-6) + quẻ biến",
        notes="Trang 41 — pp xác định động hào.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Hỗ Quái (Hỗ quái lệ)",
        name_zh="互卦",
        domain="biến_hoá",
        inputs_required=["1 trùng quái 6 vạch"],
        procedure_steps=[
            "Lấy hào 2, 3, 4 ghép thành quẻ DƯỚI mới",
            "Lấy hào 3, 4, 5 ghép thành quẻ TRÊN mới",
            "Ghép 2 quẻ mới → HỖ QUÁI",
            "Càn-Khôn không có hỗ → dùng quẻ biến thay",
        ],
        output_format="1 trùng quái mới = quẻ ẩn",
        notes="Trang 42-43 — quẻ ẩn, là 1/3 bộ chiêm (Chính - Hỗ - Biến).",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Niên-Nguyệt-Nhật-Thời Khởi Lệ ⭐",
        name_zh="年月日時起例",
        domain="bốc",
        inputs_required=["năm (chi)", "tháng", "ngày", "giờ (chi)"],
        procedure_steps=[
            "Năm theo chi: Tý=1, Sửu=2, ..., Hợi=12",
            "Tháng theo số: tháng Giêng=1, ..., tháng Mười Hai=12",
            "Ngày theo số: mồng 1=1, ..., ngày 30=30",
            "Giờ theo chi: giờ Tý=1, ..., giờ Hợi=12",
            "QUẺ TRÊN = (Năm + Tháng + Ngày) mod 8",
            "QUẺ DƯỚI = (Năm + Tháng + Ngày + Giờ) mod 8",
            "ĐỘNG HÀO = (Năm + Tháng + Ngày + Giờ) mod 6",
            "Mod=0 thì lấy 8 (quẻ) hoặc 6 (hào)",
        ],
        output_format="Chính quái + Quẻ biến + Hỗ quái + Động hào",
        confidence_baseline=0.0,
        notes=(
            "Trang 43-45. PP bốc Mai Hoa phổ biến nhất. "
            "Có thể implement thành tool python — anh sẽ dùng để gieo quẻ thật."
        ),
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Chính quái (nội + ngoại quái)",
        name_zh="正卦",
        domain="đọc",
        inputs_required=["trùng quái 6 vạch"],
        procedure_steps=[
            "Hào 1, 2, 3 = NỘI QUÁI (quẻ dưới)",
            "Hào 4, 5, 6 = NGOẠI QUÁI (quẻ trên)",
        ],
        output_format="Quẻ trên + quẻ dưới",
        notes="Trang 42 — gốc phân tích quẻ 6 vạch.",
    ))

    # ── Concepts ──
    new_concepts = [
        # Triết lý
        ("Ngoạn pháp", "玩法", "Pp 'chơi' Dịch. Trang 36-38. Tâm là gốc.", 36),
        ("Tâm Thái Cực", "心太極",
         "Tâm trong người = Thái Cực. Trang 38. ★ Gốc Tiên Thiên Tâm Pháp.", 38),
        ("Nhân ư tâm thượng khởi kinh luân", "人於心上起經綸",
         "★ Câu cốt lõi: con người TỪ TÂM mà khởi nên tài năng quản trời đất.", 38),
        ("Đạo bất hư truyền", "道不虛傳",
         "Đạo không hư truyền — chỉ tại người. Triết lý truyền thụ Mai Hoa.", 38),
        # Toán quẻ
        ("Linh số", "零數", "Số dư sau khi chia/trừ. Trang 40.", 40),
        ("Quái Trừ 8", "卦以八除", "Thuật toán: số mod 8 → quẻ. Trang 39-40.", 39),
        ("Hào Trừ 6", "爻以六除",
         "Thuật toán: (số quẻ trên + dưới) mod 6 → động hào. Trang 41.", 41),
        ("Động hào", "動爻",
         "Hào biến trong quẻ — dương→âm hoặc âm→dương. Sinh quẻ biến.", 41),
        ("Quẻ biến", "變卦",
         "Quẻ sau khi động hào đổi âm-dương. 1/3 bộ chiêm.", 41),
        # Quẻ ẩn / cấu trúc
        ("Chính thể", "正體", "Quẻ chính: nội+ngoại quái. Trang 42.", 42),
        ("Hỗ thể / Hỗ quái", "互卦",
         "Quẻ ẩn từ hào 2-3-4 + 3-4-5. Trang 42-43. 1/3 bộ chiêm.", 42),
        ("Nội quái", "內卦", "Quẻ dưới (3 hào dưới của trùng quái).", 42),
        ("Ngoại quái", "外卦", "Quẻ trên (3 hào trên).", 42),
        ("Thượng quái", "上卦", "Quẻ trên = ngoại quái.", 44),
        ("Hạ quái", "下卦", "Quẻ dưới = nội quái.", 44),
        ("Trùng quái", "重卦", "Quẻ 6 vạch = thượng quái + hạ quái.", 44),
        # Niên Nguyệt Nhật Thời
        ("Niên Nguyệt Nhật Thời Khởi Lệ", "年月日時起例",
         "★★★ PP gieo quẻ phổ biến nhất Mai Hoa. (Y+M+D) mod 8 = trên, "
         "(Y+M+D+H) mod 8 = dưới, mod 6 = động hào.", 43),
        ("Khởi quái", "起卦", "Mở đầu/khởi quẻ — bắt đầu chiêm.", 39),
        ("Tam tài lập căn nguyên", "三才立根原",
         "Câu thơ Ngoạn Pháp: phân biệt trời-đất-người để tìm nguồn gốc.", 38),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_46_61():
    """Trang 46-61: pp chiêm khác (vật số, thanh âm, chữ 1-11, trượng thước,
    xem cho người, gieo Hậu Thiên qua vật) + Bát Quái Vận Vật Loại Tượng ⭐"""
    s = get_store()
    master = _master_id()

    # ── Passage 46-59: 12 pp chiêm thay thế Niên-Nguyệt-Nhật-Thời ──
    if not _has_passage(CORPUS, 46, 59):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=46, page_end=59,
            topic="12 pp chiêm thay thế: gieo qua vật/âm/chữ/người (Quyển I cuối)",
            raw_text=(
                "Mai Hoa cho phép GIEO QUẺ THEO NHIỀU KÊNH — không chỉ thời gian:\n\n"
                "1. **Vật số chiêm** (p.46) — đếm số vật trông thấy → quẻ trên; "
                "giờ → quẻ dưới; (số quẻ + giờ) mod 6 → động hào.\n\n"
                "2. **Thanh âm chiêm** (p.47) — đếm số tiếng nghe → quẻ trên; "
                "giờ → quẻ dưới.\n\n"
                "3. **Tự chiêm** (p.48-55) — gieo qua số chữ:\n"
                "   - 1 chữ: số nét trái → quẻ trên, số nét phải → quẻ dưới\n"
                "   - 2 chữ (lưỡng nghi): chữ 1 → trên, chữ 2 → dưới\n"
                "   - 3 chữ (tam tài): 1 chữ → trên, 2 chữ → dưới\n"
                "   - 4 chữ (tứ tượng): 2+2; ≥4 chữ dùng bằng-trắc thanh\n"
                "     (Bình=1, Thượng=2, Khứ=3, Nhập=4)\n"
                "   - 5 chữ (ngũ hành): 2+3\n"
                "   - 6 chữ: 3+3\n"
                "   - 7 chữ (thất chính): 3+4\n"
                "   - 8 chữ (bát quái): 4+4\n"
                "   - 9 chữ (cửu trù): 4+5\n"
                "   - 10 chữ (thành số): 5+5\n"
                "   - 11+ chữ: chia đôi tổng số chữ\n\n"
                "4. **Trượng xích chiêm / Xích thốn chiêm** (p.56) — gieo qua "
                "chiều dài (trượng/thước/tấc).\n\n"
                "5. **Vi nhân chiêm** (p.57-58) — xem cho người khác qua:\n"
                "   - Âm thanh: số chữ câu họ nói\n"
                "   - Phẩm chất / vật cầm tay\n"
                "   - Trang phục màu sắc (xanh→Chấn, đỏ→Ly)\n"
                "   - Điệu bộ (đầu động→Càn, chân động→Chấn, mắt động→Ly)\n"
                "   - Ngoại vật tiếp xúc (thấy nước→Khảm, thấy lửa→Ly)\n"
                "   - Niên-nguyệt-nhật-thời\n"
                "   - Ý của thư viết\n\n"
                "6. **Tự kỷ chiêm** (p.59) — tự xem cho mình, dùng 3 cách trên.\n\n"
                "7. **Hậu Thiên Khởi Quái** (p.60) — Vật + Phương vị:\n"
                "   - Tượng quẻ của vật → quẻ trên\n"
                "   - Phương vị quẻ → quẻ dưới"
            ),
            summary_50w=(
                "12 phép gieo thay thế Niên-Nguyệt-Nhật-Thời: vật số, thanh âm, "
                "1-11+ chữ, trượng xích, xem cho người, ngoại vật. Cho phép gieo "
                "linh hoạt theo MỌI 'duyên cớ động tâm'."
            ),
            is_canonical=True,
        ))

    # ── Passage 60-61: ⭐ BÁT QUÁI VẬN VẬT LOẠI TƯỢNG (danh mục đầy đủ 8 quẻ) ──
    if not _has_passage(CORPUS, 60, 61):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=60, page_end=61,
            topic="⭐ Bát Quái Vận Vật Loại Tượng — danh mục tượng 8 quẻ",
            raw_text=(
                "★ DANH MỤC TƯỢNG 8 QUẺ (dùng để đọc quẻ qua vật/người):\n\n"
                "CÀN ☰ = Trời, cha, ông già, quan quý, đầu, xương ngựa, vàng, "
                "ngọc, quả tròn, mào đỏ, vật cứng, nước lạnh.\n\n"
                "KHÔN ☷ = Đất, mẹ, bà già, trâu, thổ, vàng, vải bố, văn chương, "
                "vật vuông, sắc vàng, đồ đất, bụng, tay, sắc đen, lúa mạch, sách.\n\n"
                "CHẤN ☳ = Sấm, trưởng nam, chân, tóc, rồng, bách trùng, gót, "
                "trúc lau, ngựa, dâu da, nhạc khí, cỏ cây, xanh bích lục, củi, rắn.\n\n"
                "TỐN ☴ = Gió, trưởng nữ, tăng ni, đùi, bách thú, bách thảo, "
                "cối, mùi thơm, dây thừng, mắt, lông vũ, buồm quạt, cành lá, "
                "vật thẳng, đồ tinh xảo.\n\n"
                "KHẢM ☵ = Nước, mưa tuyết, lợn, trung nam, cống rãnh, bánh xe, "
                "tai, máu, mặt trăng, kẻ cướp, bến nước, cung, nhà lớn, gai góc, "
                "con báo, tật bệnh, xiềng xích, thuỷ tộc, cá, muối, rượu, đen.\n\n"
                "LY ☲ = Lửa, mặt trời, con trĩ, trung nữ, áo giáp, đao binh, "
                "văn thư, cây khô, lò, rùa, cua, ếch, vỏ, đỏ hồng tía, người tài hoa.\n\n"
                "CẤN ☶ = Núi, đất, thiếu niên nam, đứa trẻ, chó, tay, ngón, "
                "đường, cửa khuyết, quả dưa, chùa miếu, chuột, hổ, cáo, mỏ, "
                "vật do cây sinh, mũi.\n\n"
                "ĐOÀI ☱ = Đầm, thiếu nữ, bà cốt, lưỡi, vợ lẽ, phổi, dê, "
                "vật gãy vỡ, đồ có miệng, vàng, vật bỏ đi, nô bộc."
            ),
            summary_50w=(
                "★ BÁT QUÁI LOẠI TƯỢNG: bảng tra đối tượng cho mỗi quẻ — bộ phận "
                "cơ thể, người, vật, màu, tính chất. Là DICTIONARY chính để Thiệu "
                "đọc quẻ qua duyên cớ thực tế."
            ),
            is_canonical=True,
        ))

    # Methods mới
    method_specs = [
        ("Vật số chiêm", "物數占", "bốc", 46,
         ["Đếm số vật → quẻ trên", "Giờ → quẻ dưới", "(số quẻ trên + giờ) mod 6 → động hào"]),
        ("Thanh âm chiêm", "聲音占", "bốc", 47,
         ["Đếm số tiếng nghe → quẻ trên", "Số tiếng + giờ → quẻ dưới"]),
        ("Tự chiêm (chữ)", "字占", "bốc", 48,
         ["1 chữ: trái=trên, phải=dưới",
          "2-3 chữ: chia đều theo lưỡng nghi/tam tài",
          "4+ chữ: dùng bằng-trắc (Bình=1, Thượng=2, Khứ=3, Nhập=4)",
          "11+ chữ: chia đôi tổng số chữ"]),
        ("Trượng xích chiêm", "丈尺占", "bốc", 56,
         ["Số trượng → quẻ trên", "Số thước → quẻ dưới", "Cộng + giờ → động hào"]),
        ("Vi nhân chiêm (xem cho người)", "為人占", "bốc", 57,
         ["Âm thanh: số chữ câu nói",
          "Vật cầm tay: vàng/tròn=Càn, đất/vuông=Khôn",
          "Màu áo: xanh=Chấn, đỏ=Ly",
          "Điệu bộ: đầu=Càn, chân=Chấn, mắt=Ly",
          "Ngoại vật: thấy nước=Khảm, thấy lửa=Ly"]),
        ("Hậu Thiên Đoan Pháp (vật quái)", "後天端法", "bốc", 60,
         ["Tượng quẻ của vật → quẻ trên",
          "Phương vị quẻ → quẻ dưới",
          "(số quẻ trên + dưới + giờ) → động hào"]),
        ("Bát Quái Vận Vật Loại Tượng (DICT)", "八卦運物類象", "đọc", 60,
         ["Dictionary tượng 8 quẻ: vật/người/cơ thể/màu/tính",
          "Dùng khi đọc quẻ qua duyên cớ thực tế"]),
    ]
    for vi, zh, dom, page, steps in method_specs:
        s.upsert_method(Method(
            author_id=master,
            name_vi=vi, name_zh=zh, domain=dom,
            procedure_steps=steps,
            notes=f"Trang {page}.",
        ))


def extract_pages_64_90():
    """Trang 64-90: ⭐⭐⭐ CASE STUDIES — Thiệu giải quẻ thực tế.

    12 case studies. Em insert 4 case quan trọng nhất làm CaseStudy entries
    đầy đủ, các case khác chỉ note ngắn."""
    s = get_store()
    master = _master_id()

    # ── PASSAGE meta-summary: 12 case Thiệu ──
    if not _has_passage(CORPUS, 64, 90):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=64, page_end=90,
            topic="⭐ 12 Case studies Thiệu Khang Tiết — pattern đọc quẻ thực tế",
            raw_text=(
                "12 ví dụ Thiệu giải quẻ — minh hoạ TƯ DUY GIẢI QUẺ:\n\n"
                "1. **Quan Mai Hoa** (p.64-66) — 2 chim sẻ ngã → cô gái hái hoa bị thương đùi\n"
                "2. **Mẫu Đơn** (p.66-68) — hoa nở rực → bị ngựa giẫm nát ngày hôm sau\n"
                "3. **Hàng xóm gõ cửa** (p.69-71) — gõ 1+5 tiếng → mượn búa (KHÔNG phải cuốc)\n"
                "4. **Kim Nhật Động Tĩnh** (p.71-73) — đoán tiệc tối qua 6 chữ\n"
                "5. **Biển Treo Chùa Tây Lâm** (p.74-78) — đoán bằng nét chữ\n"
                "6. **Thiếu niên có sắc vui mừng** (p.79-80) — sắc mặt → đoán việc\n"
                "7. **Trâu sẽ bị giết** (p.81) — 21 ngày → cúng tế\n"
                "8. **Tiếng gà kêu bi thương** (p.82-83) — Càn phương + Mão thời\n"
                "9. **Cây cối đột nhiên** (p.84) — giờ Thìn ngày Mậu Tý\n"
                "10. **Phong giác sơn** (p.85-87) — đoán núi qua gió\n"
                "11. **Đoán chim** (p.88-89) — tên gọi + tiếng kêu loài\n"
                "12. **Thính thanh âm** (p.90) — gieo qua các tiếng nghe được\n\n"
                "★ PATTERN CHUNG (đọc quẻ Thiệu):\n"
                "  1. Xác định Thể-Dụng: quẻ chứa hào động = DỤNG, quẻ không = THỂ\n"
                "  2. Xét ngũ hành Thể↔Dụng:\n"
                "     - Dụng sinh Thể → tốt nhất\n"
                "     - Thể khắc Dụng → tốt (ta thắng)\n"
                "     - Tỉ hoà → bình\n"
                "     - Thể sinh Dụng → mất sức\n"
                "     - Dụng khắc Thể → xấu\n"
                "  3. Xét Hỗ quái (2 quẻ ẩn): thêm nhân tố sinh-khắc Thể\n"
                "     - Càng nhiều quẻ khắc Thể trong hỗ → càng xấu\n"
                "     - Có quẻ sinh Thể trong hỗ → có cứu\n"
                "  4. Xét Biến quái: kết cục\n"
                "     - Biến sinh Thể → hậu vận tốt\n"
                "     - Biến khắc Thể → kết xấu\n"
                "  5. Apply Bát Quái Vận Vật → ra 'câu chuyện cụ thể'\n"
                "  6. ⭐ SỐ + LÝ: Số (digit + quẻ) cho cấu trúc;\n"
                "     LÝ (suy luận thực tế) cho diễn giải.\n"
                "     'Suy số hựu tu minh lý' — bốc số xong phải minh lý mới đúng."
            ),
            summary_50w=(
                "★ 12 case Thiệu + Pattern cốt lõi: Thể-Dụng + ngũ hành sinh khắc + "
                "Hỗ + Biến + Bát Quái loại tượng + SUY SỐ MINH LÝ. Đây là khuôn mẫu "
                "để wiki sau này có thể auto-interpret quẻ."
            ),
            is_canonical=True,
        ))

    # ── 4 CaseStudy entries chi tiết ──
    # Lấy method_id của Niên-Nguyệt-Nhật-Thời:
    methods = s.list_methods(master)
    method_id_nguy = next(
        (m["method_id"] for m in methods if "Niên-Nguyệt-Nhật-Thời" in m["name_vi"]),
        0
    )

    cases = [
        dict(
            method_id=method_id_nguy,
            historical_event="Quan Mai Hoa — 2 chim sẻ tranh cành ngã (p.64-66)",
            inputs_recorded={
                "year": "Thìn (5)", "month": 12, "day": 17, "hour": "Thân (9)",
                "trigger": "2 chim sẻ tranh cành mai → ngã xuống đất",
                "calc": "5+12+17=34 mod 8=2 → Đoài; 34+9=43 mod 8=3 → Ly; 43 mod 6=1 → hào sơ",
            },
            output_predicted=(
                "Chính: Trạch Hoả Cách (Đoài/Ly) | Biến: Hàm | Hỗ: Càn/Tốn. "
                "Thể Đoài-Kim, Dụng Ly-Hoả, Hoả khắc Kim → cô gái sẽ đến hái hoa, "
                "bị người coi vườn đuổi → ngã ngã đùi. Cấn (thổ) trong biến sinh "
                "Kim → chỉ bị thương sơ, không nguy hiểm."
            ),
            output_actual="Đúng — tối ngày mai cô gái đến hái hoa, bị đuổi, ngã đau đùi nhẹ.",
            accuracy_score=1.0,
            source_book="Mai Hoa Dịch Số (VN) trang 64-66",
        ),
        dict(
            method_id=method_id_nguy,
            historical_event="Mẫu Đơn — hoa nở rực, dự đoán bị huỷ (p.66-68)",
            inputs_recorded={
                "year": "Tị (6)", "month": 3, "day": 16, "hour": "Mão (4)",
                "trigger": "Thiệu cùng khách tới nhà Tư Mã Quang xem mẫu đơn nở",
                "calc": "6+3+16=25 mod 8=1 → Càn; 25+4=29 mod 8=5 → Tốn; 29 mod 6=5 → hào 5",
            },
            output_predicted=(
                "Chính: Thiên Phong Cấu (Càn/Tốn) | Biến: Đỉnh | Hỗ: 2x Càn. "
                "Thể Tốn-Mộc, Dụng Càn-Kim, Kim khắc Mộc + hỗ có 2 Càn → khắc Thể "
                "quá nhiều → hoa sẽ bị huỷ. Biến có Ly → giờ Ngọ ngày mai. "
                "Càn = ngựa → ngựa giẫm."
            ),
            output_actual="Đúng — hôm sau giờ Ngọ, đại quan đến xem, 2 ngựa cắn nhau giẫm nát hoa.",
            accuracy_score=1.0,
            source_book="Mai Hoa Dịch Số (VN) trang 66-68",
        ),
        dict(
            method_id=0,  # Thanh âm chiêm
            historical_event="Hàng xóm gõ cửa đêm đông — mượn búa (p.69-71)",
            inputs_recorded={
                "season": "đầu đông", "hour": "Dậu (10)",
                "trigger": "Khách gõ cửa: 1 tiếng + 5 tiếng",
                "calc": "1 tiếng → Càn (trên); 5 tiếng → Tốn (dưới); 1+5+10=16 mod 6=4 → hào 4",
            },
            output_predicted=(
                "Chính: Thiên Phong Cấu (Càn/Tốn) | Biến: Thuần Tốn | Hỗ: 2x Càn. "
                "3 Càn (kim) + 2 Tốn (mộc) → đồ vật kim-mộc; Càn kim ngắn, Tốn mộc dài. "
                "Con Thiệu: cuốc. Thiệu: KHÔNG — ban đêm cuốc đất làm gì? "
                "★ SUY SỐ PHẢI MINH LÝ → đêm = cần bổ củi → CÁI BÚA."
            ),
            output_actual="Đúng — hàng xóm mượn búa bổ củi.",
            accuracy_score=1.0,
            source_book="Mai Hoa Dịch Số (VN) trang 69-71",
        ),
        dict(
            method_id=0,  # Tự chiêm (6 chữ)
            historical_event="Kim Nhật Động Tĩnh Như Hà — đoán tiệc tối (p.71-73)",
            inputs_recorded={
                "trigger": "Khách hỏi 'Kim nhật động tĩnh như hà?' (6 chữ)",
                "calc": (
                    "Kim(1)+Nhật(4)+Động(3)=8 → Khôn (trên); "
                    "Tĩnh(3)+Như(1)+Hà(1)=5 → Tốn (dưới); 13 mod 6=1 → hào sơ"
                ),
            },
            output_predicted=(
                "Chính: Địa Phong Thăng (Khôn/Tốn) | Biến: Thái | Hỗ: Chấn/Đoài. "
                "Thăng = có lên gia, được mời. Hỗ Đoài (miệng) + Khôn (bụng) → ăn uống. "
                "Khôn thổ độc lập → khách không đông. Không Khảm → rượu không say. "
                "Khôn = heo (chứ không phải gà/chuột) → đoán có tiệc nhưng đơn sơ."
            ),
            output_actual="Đúng — có người mời ăn, khách ít, rượu không say, không có gà chuột.",
            accuracy_score=1.0,
            source_book="Mai Hoa Dịch Số (VN) trang 71-73",
        ),
    ]
    for c in cases:
        with sqlite3_conn() as conn:
            conn.execute(
                """INSERT INTO case_studies
                (method_id, historical_event, inputs_recorded, output_predicted,
                 output_actual, accuracy_score, source_book, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (c["method_id"], c["historical_event"],
                 _enc(c["inputs_recorded"]), c["output_predicted"],
                 c["output_actual"], c["accuracy_score"],
                 c["source_book"], int(__import__("time").time())),
            )
            conn.commit()

    # ── Method: Quy tắc đọc quẻ Thiệu ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Quy tắc giải quẻ Thiệu Khang Tiết",
        name_zh="邵子解卦法",
        domain="đọc",
        inputs_required=["Chính quái + Biến quái + Hỗ quái + Động hào"],
        procedure_steps=[
            "1. Xác định THỂ-DỤNG: quẻ chứa hào động = DỤNG, không = THỂ",
            "2. Xét ngũ hành Thể↔Dụng:",
            "   - Dụng sinh Thể → tốt nhất",
            "   - Thể khắc Dụng → tốt",
            "   - Tỉ hoà → bình",
            "   - Thể sinh Dụng → mất sức",
            "   - Dụng khắc Thể → xấu",
            "3. Xét HỖ quái: thêm sinh-khắc Thể",
            "4. Xét BIẾN quái: kết cục",
            "5. Apply Bát Quái Vận Vật → câu chuyện cụ thể",
            "★ 6. SỐ + LÝ: 'Suy số hựu tu minh lý'",
        ],
        output_format="Kết luận: tốt/xấu/bình + diễn giải tượng + timing",
        notes=(
            "★ Trang 64-90. Đây là CỐT LÕI của Mai Hoa Dịch Số. "
            "12 case studies Thiệu minh hoạ. Pattern để wiki tự diễn giải quẻ."
        ),
    ))

    # ── Concepts mới ──
    new_concepts = [
        ("Hậu Thiên Đoan Pháp", "後天端法",
         "Pp gieo quẻ qua vật + phương vị (không qua thời gian). Trang 60.", 60),
        ("Bát Quái Vận Vật Loại Tượng", "八卦運物類象",
         "DICTIONARY tượng 8 quẻ — vật/người/cơ thể/màu. Trang 60-61. ⭐ Để đọc quẻ.", 60),
        ("Suy số minh lý", "推數明理",
         "★ Nguyên tắc Thiệu: bốc số xong phải dùng LÝ thực tế để diễn giải.", 71),
        ("Số học chi giả", "數學之者",
         "Người làm số học. Cần kết hợp số + lý.", 71),
        ("Tư Mã Quang", "司馬光",
         "Sử gia + chính trị gia Bắc Tống, bạn Thiệu. Chủ nhà có hoa mẫu đơn trong case 2.", 66),
        # 12 case names
        ("Quan Mai Hoa chiêm", "觀梅花占", "Case 1 — chim sẻ ngã, đặt tên sách.", 64),
        ("Mẫu Đơn chiêm", "牡丹占", "Case 2 — hoa mẫu đơn bị ngựa giẫm.", 66),
        ("Lân dạ khẩu môn chiêm", "鄰夜叩門占",
         "Case 3 — hàng xóm gõ cửa mượn búa. ★ Suy số minh lý.", 69),
        ("Kim Nhật Động Tĩnh chiêm", "今日動靜占",
         "Case 4 — đoán tiệc tối qua 6 chữ.", 71),
        ("Tây Lâm Tự bài ngạch chiêm", "西林寺牌額占",
         "Case 5 — đoán biển treo chùa.", 74),
        ("Thiếu niên hữu hỉ sắc chiêm", "少年有喜色占",
         "Case 6 — đoán qua sắc mặt vui.", 79),
        ("Ngưu bi minh chiêm", "牛悲鳴占",
         "Case 7 — đoán trâu sẽ bị giết trong 21 ngày.", 81),
        ("Kê bi minh chiêm", "雞悲鳴占",
         "Case 8 — đoán qua tiếng gà kêu bi thương.", 82),
        ("Cổ thụ đột chiêm", "古樹突占",
         "Case 9 — đoán cây cối đột nhiên đổ.", 84),
        ("Phong giác sơn chiêm", "風覺山占",
         "Case 10 — đoán núi qua hướng gió.", 85),
        ("Điểu chiêm", "鳥占",
         "Case 11 — đoán qua tên/tiếng kêu chim.", 88),
        ("Thính thanh âm chiêm", "聽聲音占",
         "Case 12 — đoán qua các tiếng nghe được.", 90),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


# Helper: direct sqlite conn (vì WikiStore không expose case_studies upsert)
from contextlib import contextmanager
import sqlite3 as _sql

@contextmanager
def sqlite3_conn():
    from engine.yi_wiki.store import _DB_PATH
    conn = _sql.connect(_DB_PATH)
    conn.row_factory = _sql.Row
    try:
        yield conn
    finally:
        conn.close()


def extract_pages_115_130():
    """⭐ Quyển 2 mở đầu: 5 bước chiêm chính thống + Thể-Dụng tổng quyết.

    Trang 115-121 chứa NGUYÊN LÝ CHỦ ĐẠO của toàn sách: 5 bước chiêm
    và lý luận Số phải kết hợp với Lý.
    """
    s = get_store()
    master = _master_id()

    # ── Passage 115-117: Huyền cơ + biến thông ──
    if not _has_passage(CORPUS, 115, 117):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=115, page_end=117,
            topic="Sự huyền diệu của Chiêm Bốc — Biến Thông là cốt",
            raw_text=(
                "★ TRIẾT LÝ MỞ ĐẦU QUYỂN 2:\n\n"
                "Sự việc trời đất có CÁT-HUNG. Mượn quẻ để hiểu cơ. "
                "Lý của thiên hạ vô hình tích — phải mượn tượng quẻ để rõ ý nghĩa.\n\n"
                "Tượng quẻ là LÝ bất biến — nhưng nếu không BIẾN THÔNG thì không thông được. "
                "'Dịch' là biến dịch. Cùng 1 quẻ Cách:\n"
                "  - Hôm nay xem mai → cô gái hái hoa bị thương\n"
                "  - Hôm khác xem việc khác → có thể chẳng có cô gái nào\n"
                "Đoài đâu chỉ là phụ nữ, Càn đâu chỉ là ngựa.\n\n"
                "★ MẤU CHỐT BIẾN THÔNG ở TRONG TÂM — 'tại hồ tâm'. "
                "Bí quyết là TRONG TÂM CÓ ĐIỆU PHÁP BIẾN DỊCH.\n\n"
                "Ba nguyên tắc Dịch: GIẢN DỊCH · BIẾN DỊCH · BẤT DỊCH "
                "(easy / changing / unchanging) — hạt nhân tư tưởng Dịch học."
            ),
            summary_50w=(
                "★ Cốt lõi tâm pháp: 1 quẻ KHÔNG có 1 nghĩa cố định — phải BIẾN THÔNG "
                "theo bối cảnh. Mấu chốt là 'tại tâm'. Đây là khác biệt giữa "
                "học trò bốc cứng và Thiệu tự do."
            ),
            is_canonical=True,
        ))

    # ── Passage 117-120: ⭐ 5 BƯỚC CHIÊM QUÁI TỔNG QUYẾT ──
    if not _has_passage(CORPUS, 117, 120):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=117, page_end=120,
            topic="★ 5 BƯỚC CHIÊM QUÁI TỔNG QUYẾT (Chiêm Bốc Tổng Quyết)",
            raw_text=(
                "★★★ NĂM BƯỚC CHIÊM CHÍNH THỐNG (Thiệu Khang Tiết):\n\n"
                "BƯỚC 1: THÀNH QUẺ\n"
                "  Gieo quẻ qua phương pháp (Niên-Nguyệt-Nhật-Thời, vật số, âm thanh, chữ...)\n\n"
                "BƯỚC 2: XEM LỜI QUẺ + LỜI HÀO Chu Dịch\n"
                "  Đối chiếu với 64 quẻ + 384 hào.\n"
                "  Ví dụ: Càn Sơ Cửu 'Tiềm long vật dụng' → nên ẩn náu chờ thời.\n"
                "  Càn Cửu Nhị 'Kiến long tại điền, lợi kiến đại nhân' → nên gặp quý nhân.\n\n"
                "BƯỚC 3: ★ XEM THỂ-DỤNG + NGŨ HÀNH SINH KHẮC ★\n"
                "  Quẻ THỂ = mình (chủ thể).\n"
                "  Quẻ DỤNG = người/việc khác (ngoại cảnh).\n"
                "  Quan hệ:\n"
                "    DỤNG SINH THỂ  → CÁT (tốt nhất — ngoại cảnh nuôi ta)\n"
                "    THỂ KHẮC DỤNG  → CÁT (tốt — ta thắng việc)\n"
                "    TỈ HOÀ         → CÁT (bình - thuận lợi)\n"
                "    THỂ SINH DỤNG  → HUNG (mất sức — ta cho đi)\n"
                "    DỤNG KHẮC THỂ  → HUNG (xấu — bị đè)\n\n"
                "BƯỚC 4: XEM KHẮC ỨNG (môi trường ngoại cảnh)\n"
                "  Nghe tin lành + thấy điềm lành → đại cát\n"
                "  Nghe tin dữ + thấy điềm dữ → đại hung\n"
                "  Thấy vật TRÒN → việc dễ thành\n"
                "  Thấy vật VỠ/KHUYẾT → việc cuối hỏng\n\n"
                "BƯỚC 5: XÁC ĐỊNH NGÀY ỨNG NGHIỆM (qua động tĩnh khi gieo)\n"
                "  NGỒI gieo  → ứng nghiệm CHẬM\n"
                "  ĐI gieo    → ứng nghiệm NHANH\n"
                "  CHẠY gieo  → ứng nghiệm RẤT NHANH\n"
                "  NẰM gieo   → ứng nghiệm CHẬM HƠN\n\n"
                "★ Đại cát = các yếu tố đều lành. Đại hung = các yếu tố đều dữ. "
                "Có cát có hung = phải nghiên cứu kỹ Thể-Dụng + lời quẻ + tượng.\n"
                "★ 'Yếu cần nhuần nhuyễn quán thông — KHÔNG cứng nhắc máy móc'."
            ),
            summary_50w=(
                "★★★ Quy trình 5 bước CHUẨN của Thiệu: Thành quẻ → Lời Chu Dịch → "
                "Thể-Dụng ngũ hành → Khắc ứng môi trường → Timing động tĩnh. "
                "Đây là METHODOLOGY chính thống cho PHASE B auto-interpret."
            ),
            is_canonical=True,
        ))

    # ── Passage 120-121: Lý luận Chiêm Đoán — Số PHẢI kết hợp Lý ──
    if not _has_passage(CORPUS, 120, 121):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=120, page_end=121,
            topic="Lý Luận Chiêm Đoán — Số + Lý",
            raw_text=(
                "★ NGUYÊN TẮC SỐ + LÝ (Chiêm Bốc Luận Lý Quyết):\n\n"
                "'Số học' phải kết hợp 'Lý' — luận số mà không luận lý sẽ thiên kiến.\n\n"
                "VÍ DỤ:\n"
                "  - Hỏi ăn uống được quẻ Chấn = rồng. Lý: rồng KHÔNG ăn được →\n"
                "    dùng tượng CÁ CHÉP (loài rồng nước) thay rồng.\n"
                "  - Hỏi thời tiết được Chấn = sấm. Lý: mùa đông KHÔNG có sấm →\n"
                "    dùng tượng GIÓ rung động thay sấm.\n\n"
                "★ Phương pháp BIẾN THÔNG = phân tích cụ thể tình huống cụ thể."
            ),
            summary_50w=(
                "Nguyên tắc: Số (cấu trúc quẻ + ngũ hành) + LÝ (suy luận thực tế) "
                "= chiêm đoán đúng. Single source không đủ. Cần biến thông."
            ),
            is_canonical=True,
        ))

    # ── METHOD ★ — 5 bước chiêm chuẩn thống ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ 5 Bước Chiêm Quái (Tổng Quyết Chính Thống)",
        name_zh="占卜總訣五步",
        domain="đọc",
        inputs_required=["bộ chiêm: Chính + Hỗ + Biến + Động hào", "bối cảnh"],
        procedure_steps=[
            "1. THÀNH QUẺ — gieo qua pp phù hợp",
            "2. XEM LỜI QUẺ + LỜI HÀO Chu Dịch — đối chiếu 64 quẻ + 384 hào",
            "3. ★ THỂ-DỤNG NGŨ HÀNH SINH KHẮC ★",
            "   - Thể = ta | Dụng = việc/người",
            "   - Dụng sinh Thể: CÁT (tốt nhất)",
            "   - Thể khắc Dụng: CÁT (ta thắng)",
            "   - Tỉ hoà: CÁT (bình thuận)",
            "   - Thể sinh Dụng: HUNG (mất sức)",
            "   - Dụng khắc Thể: HUNG (bị đè)",
            "4. KHẮC ỨNG — nghe/thấy lành dữ + vật tròn/vỡ",
            "5. NGÀY ỨNG NGHIỆM — qua động tĩnh khi gieo:",
            "   - Ngồi: chậm | Đi: nhanh | Chạy: rất nhanh | Nằm: chậm hơn",
            "★ Cát + Cát = đại cát; Hung + Hung = đại hung; Hỗn hợp = nghiên cứu kỹ",
        ],
        output_format="Phán đoán cát/hung + thời điểm ứng nghiệm + diễn giải",
        notes="★★★ Trang 117-120. CỐT LÕI sách Mai Hoa. Foundation cho PHASE B.",
    ))

    # ── METHOD: Số + Lý ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="Số + Lý (Suy số tu minh lý)",
        name_zh="推數須明理",
        domain="đọc",
        procedure_steps=[
            "1. SỐ: tính quẻ + ngũ hành Thể-Dụng theo công thức",
            "2. LÝ: suy luận thực tế theo bối cảnh",
            "3. Khi số cho tượng không hợp lý → DÙNG TƯỢNG TƯƠNG ĐƯƠNG",
            "   VD: Chấn ăn = rồng → cá; Chấn đông = sấm → gió",
            "4. Kết hợp 2 mới đúng",
        ],
        output_format="Diễn giải biến thông theo bối cảnh",
        notes="Trang 120-121. Hỗ trợ giải thích case Thiệu (mượn búa, không cuốc).",
    ))

    # ── Concepts ──
    new_concepts = [
        ("Chiêm bốc tổng quyết", "占卜總訣",
         "★ 5 bước chiêm chính thống. Trang 117-120.", 117),
        ("Bước 1: Thành quẻ", "成卦", "Gieo quẻ qua pp.", 117),
        ("Bước 2: Lời quẻ + hào", "卦辭爻辭",
         "Đối chiếu 64 quẻ + 384 hào Chu Dịch.", 117),
        ("Bước 3: Thể-Dụng sinh khắc", "體用生剋",
         "★ Trụ cột — 5 quan hệ ngũ hành.", 117),
        ("Bước 4: Khắc ứng", "剋應",
         "Khắc ứng môi trường: nghe/thấy + vật tròn/vỡ.", 117),
        ("Bước 5: Ngày ứng nghiệm", "應日",
         "Timing: ngồi/đi/chạy/nằm khi gieo.", 119),
        ("Đại cát", "大吉", "Mọi yếu tố đều lành.", 118),
        ("Đại hung", "大凶", "Mọi yếu tố đều dữ.", 118),
        ("Giản dịch", "簡易", "1 trong 3 nguyên tắc Dịch — dễ.", 116),
        ("Biến thông", "變通",
         "Nguyên tắc cốt lõi — phân tích cụ thể, không cứng nhắc.", 116),
        ("Chiêm bốc luận lý quyết", "占卜論理訣",
         "Nguyên tắc Số + Lý. Trang 120.", 120),
        ("Quan Mai Số Quyết", "觀梅數訣",
         "Tên gốc của Quyển 3 — bí quyết xem mai. Trang 222.", 222),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_131_170():
    """⭐ Quyển 2 mở rộng: Thể-Dụng Tổng Quyết + 8 quẻ Sinh/Khắc Thể + 14 Nhân Sự Chiêm."""
    s = get_store()
    master = _master_id()

    # Passage 131-149: Thể-Dụng tổng quyết mở rộng + Đằng vũ + 8 quẻ Sinh/Khắc
    if not _has_passage(CORPUS, 131, 149):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=131, page_end=149,
            topic="⭐ Thể-Dụng Tổng Quyết MỞ RỘNG + Đằng vũ + 8 quẻ Sinh/Khắc Thể",
            raw_text=(
                "★ THỂ-DỤNG MỞ RỘNG (chi tiết hơn trang 117):\n\n"
                "Quẻ chủ (bản quái) = chính quái, GỒM cả:\n"
                "  - Quẻ Chính → đầu sự việc\n"
                "  - Quẻ Hỗ → giữa sự việc\n"
                "  - Quẻ Biến → kết cục\n\n"
                "★ ĐẰNG VŨ (cấu kết): cùng 1 hành chiếm nhiều quẻ trong bộ 3\n"
                "  - Hành Thể chiếm 2+ quẻ → Thể thế lực MẠNH\n"
                "  - Hành Dụng chiếm 2+ quẻ → Thể thế lực SUY\n\n"
                "★ TIỆT KHÍ: Thể sinh Dụng = mình cho đi, mất sức.\n"
                "  (Hạ hoả phùng thổ = hè đến gặp đất → hoả sinh thổ → tiệt khí.)\n\n"
                "★ THỜI GIAN (đầu giữa cuối):\n"
                "  - Chính cát + Biến hung → trước tốt sau xấu\n"
                "  - Chính hung + Biến cát → trước xấu sau tốt\n\n"
                "★ DICTIONARY 8 QUẺ LÀM SINH THỂ (cho điểm may):\n"
                "  Càn: việc công môn vui / công danh / kiện thắng / kim ngọc lợi / người già cho của\n"
                "  Khôn: ruộng đất / hàng xóm giúp / hoa quả ngũ cốc / vải vóc\n"
                "  Chấn: phương Đông / sơn lâm / giao dịch gỗ / người tên thảo mộc\n"
                "  Tốn: phương Đông Nam / sơn lâm / trà quả rau / người làm thảo mộc\n"
                "  Khảm: phương Bắc / nước / cá muối rượu / văn thư\n"
                "  Ly: phương Nam / văn thư / lò nấu / người tên hoả\n"
                "  Cấn: phương Đông Bắc / sơn điền / người tôn quý / cung âm-thổ\n"
                "  Đoài: phương Tây / vui mừng / vàng ngọc / chủ-khách / bạn bè\n\n"
                "★ DICTIONARY 8 QUẺ LÀM KHẮC THỂ (báo điểm xấu):\n"
                "  Càn: việc công khó / mất vật báu / tổn thất / tội quý nhân\n"
                "  Khôn: ruộng đất tổn / kẻ tiểu nhân hại / mất vải / không lợi thóc\n"
                "  Chấn: kinh sợ hốt hoảng / yêu ma / người tên thảo mộc xâm / mất sơn lâm\n"
                "  Tốn: đông nam khó thành / tai nạn từ đàn bà (tiểu khẩu âm)\n"
                "  Khảm: vu khống / kẻ cướp / thất ý người nước / hoạ rượu / phương bắc\n"
                "  Ly: phương nam khó / hoả tai / người tên hoả hại\n"
                "  Cấn: rối ren liên tục / sơn lâm điền thổ mất / phần mộ không ổn\n"
                "  Đoài: tây bất lợi / khẩu thiệt phân tranh / bẻ gãy / ẩm thực sinh ưu"
            ),
            summary_50w=(
                "★ Thể-Dụng đầy đủ: thêm Đằng vũ (cấu kết hành), Tiệt khí, thời gian đầu-giữa-cuối, "
                "+ 8x2 dictionary outcomes khi mỗi quẻ làm Sinh/Khắc Thể. Dữ liệu để upgrade engine."
            ),
            is_canonical=True,
        ))

    # Passage 150-170: 14 Nhân Sự Chiêm
    if not _has_passage(CORPUS, 150, 170):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=150, page_end=170,
            topic="⭐ 14 Loại Nhân Sự Chiêm — context mapping Thể-Dụng",
            raw_text=(
                "★ Mỗi loại VIỆC HỎI gán nghĩa Thể-Dụng khác nhau:\n\n"
                "1. THIÊN THỜI (mưa nắng): Thể = trạng thái, Dụng = thời tiết.\n"
                "   Khảm sinh Thể = có mưa | Ly sinh Thể = nắng\n\n"
                "2. GIA TRẠCH (nhà cửa): Thể = nhà, Dụng = ngoại cảnh\n\n"
                "3. ỐC XÁ (chỗ ở): tương tự gia trạch\n\n"
                "4. HÔN NHÂN (trang 150): Thể = nhà người xem, Dụng = nhà đối tượng\n"
                "   - Dụng sinh Thể → hôn nhân dễ thành, được tài sản hôn nhân\n"
                "   - Thể sinh Dụng → khó thành, tốn của cầu cạnh\n"
                "   - Tỉ hoà → lương phối vô nghi\n"
                "   - Hình thể từng quẻ: Càn cao đoan chính / Khảm đen tà dâm /\n"
                "     Cấn vàng xảo / Chấn nữ mạo / Tốn tóc thưa / Ly thấp đỏ /\n"
                "     Khôn bụng to / Đoài cao trắng vui\n\n"
                "5. SINH SẢN (trang 152): Thể = mẹ, Dụng = con. Đều nên VƯỢNG\n"
                "   - Thể khắc Dụng → bất lợi con\n"
                "   - Dụng khắc Thể → bất lợi mẹ\n"
                "   - Quẻ dương + hào dương nhiều → sinh nam\n"
                "   - Quẻ âm + hào âm nhiều → sinh nữ\n\n"
                "6. SINH Ý (làm ăn): tương tự cầu tài\n\n"
                "7. MƯU CẦU (trang 155): Thể = ta, Dụng = sự mưu cầu\n\n"
                "8. CẦU DANH (trang 156): Thể = ta, Dụng = danh\n"
                "   - Thể khắc Dụng → danh có thể thành nhưng chậm\n"
                "   - Dụng khắc Thể → danh không thành. Đang nhậm chức gặp khắc → mất quan\n\n"
                "9. CẦU TÀI (trang 158): Thể = ta, Dụng = tài muốn cầu\n"
                "   - Thể khắc Dụng → có tài | Dụng khắc Thể → vô tài\n"
                "   - Dụng sinh Thể → tài tăng vui\n"
                "   - Thể sinh Dụng → có lo phá tài (tiệt khí)\n\n"
                "10. GIAO DỊCH (trang 159): tương tự cầu tài\n\n"
                "11. XUẤT HÀNH (trang 160): Thể = ta, Dụng = ứng chuyến đi\n"
                "    - Thể khắc Dụng → đi đắc ý\n"
                "    - Dụng khắc Thể → đi gặp hoạ\n"
                "    - Thể sinh Dụng → tổn thất hao tài\n"
                "    - Dụng sinh Thể → tài ngoài ý muốn\n"
                "    - Quẻ Thể Càn/Chấn → đa chủ động (nên đi)\n"
                "    - Khôn/Cấn → đa chủ bất động (nên ở)\n"
                "    - Tốn → nên hành | Ly → nên đi đường bộ\n"
                "    - Khảm → phòng thất thoát | Đoài → phân tranh\n\n"
                "12. HÀNH NHÂN (người đang đi): Thể = ta, Dụng = người đi\n"
                "    - Dụng sinh Thể → người sắp về | Dụng khắc Thể → về chậm\n\n"
                "13. YẾT KIẾN: Thể = ta đi yết, Dụng = người được gặp\n\n"
                "14. BỆNH TẬT (trang 165): Thể = bệnh nhân, Dụng = bệnh chứng\n"
                "    - Thể nên VƯỢNG, không nên SUY\n"
                "    - Thể khắc Dụng → bệnh dễ an\n"
                "    - Dụng khắc Thể → khó chữa\n"
                "    - Thể phùng khắc + suy → nguy hiểm\n"
                "    - Thuốc theo Sinh Thể: Ly sinh Thể → uống thuốc nóng\n"
                "      Khảm sinh Thể → uống thuốc lạnh\n"
                "      Cấn → ôn bổ | Càn/Đoài → thuốc mát"
            ),
            summary_50w=(
                "★ 14 loại việc cụ thể: mỗi loại gán Thể-Dụng khác (mẹ-con, ta-tài, ta-danh,...). "
                "Cùng pattern 5 quan hệ ngũ hành nhưng kết luận specific theo intent."
            ),
            is_canonical=True,
        ))

    # Add các đại sư trong lineage (trang 180)
    from engine.yi_wiki.models import TIER_MASTER_TEACHER, TIER_DIRECT_DISCIPLE
    consultants = [
        ("Quách Hán", "郭漢", TIER_MASTER_TEACHER, "Đại sư Dịch số học."),
        ("Quản Lộ", "管輅", TIER_MASTER_TEACHER, "Tam Quốc — chiêm bốc nổi tiếng."),
        ("Lý Thuần Phong", "李淳風", TIER_MASTER_TEACHER, "Đường — tác giả Thôi Bối Đồ."),
        ("Viên Thiên Cương", "袁天綱", TIER_MASTER_TEACHER, "Đường — đồng tác giả Thôi Bối Đồ."),
        ("Trần Đoán", "陳摶", TIER_MASTER_TEACHER, "Đại nho Bắc Tống, thầy của Thiệu (gián tiếp)."),
        ("Lưu Bá Ôn", "劉伯溫", TIER_DIRECT_DISCIPLE, "Cuối Nguyên đầu Minh — kế thừa pp Thiệu."),
    ]
    for vi, zh, tier, bio in consultants:
        s.upsert_author(Author(name_vi=vi, name_zh=zh, tier_in_lineage=tier, bio_summary=bio))

    # Method mới: Đằng vũ
    s.upsert_method(Method(
        author_id=master,
        name_vi="Đằng vũ (cấu kết hành trong bộ 3 quẻ)",
        name_zh="騰附",
        domain="đọc",
        procedure_steps=[
            "Đếm số quẻ cùng hành với Thể trong bộ Chính+Hỗ+Biến (loại Thể ra)",
            "Đếm số quẻ cùng hành với Dụng",
            "Nhiều cùng hành Thể → Thể MẠNH",
            "Nhiều cùng hành Dụng → Thể YẾU",
        ],
        output_format="Thể mạnh/yếu thế trong bộ 3 quẻ",
        notes="Trang 132-134 — bổ sung cho 5 quan hệ Thể-Dụng cơ bản.",
    ))

    # Method tổng quát: 14 Nhân Sự Chiêm
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ 14 Nhân Sự Chiêm (intent-aware Thể-Dụng)",
        name_zh="人事占",
        domain="đọc",
        procedure_steps=[
            "1. Xác định LOẠI VIỆC HỎI (hôn nhân/sinh sản/cầu tài/.../bệnh tật)",
            "2. Gán Thể-Dụng theo intent:",
            "   - Hôn nhân: Thể=nhà ta, Dụng=nhà đối tượng",
            "   - Sinh sản: Thể=mẹ, Dụng=con",
            "   - Cầu danh: Thể=ta, Dụng=danh",
            "   - Cầu tài: Thể=ta, Dụng=tài",
            "   - Xuất hành: Thể=ta, Dụng=ứng chuyến",
            "   - Bệnh tật: Thể=bệnh nhân, Dụng=bệnh chứng (Thể nên VƯỢNG)",
            "3. Apply 5 quan hệ Thể-Dụng",
            "4. Apply specific outcomes 8 quẻ Sinh/Khắc Thể",
        ],
        output_format="Diễn giải theo loại việc với outcome cụ thể",
        notes="Trang 150-170. Là PHASE C cho UI — anh chọn loại việc, em dự đoán có ngữ cảnh.",
    ))

    # Concepts mới
    new_concepts = [
        ("Đằng vũ", "騰附",
         "Cấu kết hành — cùng 1 hành chiếm nhiều quẻ trong bộ 3.", 132),
        ("Tiệt khí", "截氣",
         "Thể sinh Dụng → mất sức (cắt khí).", 132),
        ("Quẻ chủ / Bản quái", "本卦",
         "Quẻ gốc gồm Chính + Hỗ + Biến.", 131),
        ("Ứng kỳ", "應期",
         "Chính=đầu, Hỗ=giữa, Biến=cuối sự việc.", 133),
        # 14 loại chiêm
        ("Hôn nhân chiêm", "婚姻占",
         "Loại 4. Thể=nhà ta, Dụng=nhà đối tượng. Trang 150.", 150),
        ("Sinh sản chiêm", "生產占",
         "Loại 5. Thể=mẹ, Dụng=con. Trang 152.", 152),
        ("Sinh ý chiêm", "生意占",
         "Loại 6. Làm ăn.", 154),
        ("Mưu cầu chiêm", "謀求占", "Loại 7. Trang 155.", 155),
        ("Cầu danh chiêm", "求名占",
         "Loại 8. Thể=ta, Dụng=danh. Trang 156.", 156),
        ("Cầu tài chiêm", "求財占",
         "Loại 9. Thể=ta, Dụng=tài. Trang 158.", 158),
        ("Giao dịch chiêm", "交易占",
         "Loại 10. Trang 159.", 159),
        ("Xuất hành chiêm", "出行占",
         "Loại 11. Thể=ta, Dụng=ứng chuyến. Trang 160.", 160),
        ("Hành nhân chiêm", "行人占",
         "Loại 12. Người đang đi xa.", 161),
        ("Yết kiến chiêm", "謁見占",
         "Loại 13. Thể=ta, Dụng=người gặp.", 162),
        ("Bệnh tật chiêm", "疾病占",
         "Loại 14. Thể=bệnh nhân, Dụng=chứng. Thể phải vượng.", 165),
        # Đại sư lineage
        ("Quản Lộ", "管輅",
         "Tam Quốc — chiêm bốc đại sư, tiền bối Thiệu.", 180),
        ("Lý Thuần Phong", "李淳風",
         "Đường — tác giả Thôi Bối Đồ.", 180),
        ("Viên Thiên Cương", "袁天綱",
         "Đường — đồng tác giả Thôi Bối Đồ.", 180),
        ("Trần Đoán", "陳摶",
         "Đại nho Bắc Tống, tổ Đồ Thư phái.", 180),
        ("Lưu Bá Ôn", "劉伯溫",
         "Cuối Nguyên đầu Minh — kế thừa Mai Hoa.", 180),
        ("Tam yếu (Tai-Mắt-Tim)", "三要",
         "Tai, Mắt, Tim — 3 cơ quan thu nhận thông tin. Tim quản tất cả.", 180),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_195_271():
    """Trang 195-197: Địa lý chiêm + Suy Vượng luận + Nội Ngoại luận.
    Trang 270-271: Danh mục 64 quẻ (đã có hexagrams_64.py)."""
    s = get_store()
    master = _master_id()

    if not _has_passage(CORPUS, 195, 197):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=195, page_end=197,
            topic="Địa lý chiêm + Suy Vượng luận + ⭐ Nội Ngoại luận",
            raw_text=(
                "★ ĐỊA LÝ CHIÊM (trang 195):\n"
                "  Mỗi loại địa hình ứng tượng quẻ:\n"
                "  - Cây rừng tre trúc → tượng Chấn (mộc)\n"
                "  - Sông ngòi ao hồ → tượng Khảm (thuỷ)\n"
                "  - Đô sành đô gốm huyệt đốt → tượng Ly (hoả)\n"
                "  - Huyệt động nham thạch → tượng Cấn (núi đá)\n"
                "  Khi xem địa lý: Thể hợp với tượng địa → cát, khắc tượng → hung\n\n"
                "★ SUY VƯỢNG LUẬN (trang 196) — quy luật trụ cột:\n"
                "  • Quẻ THỂ phải VƯỢNG là tốt nhất\n"
                "  • Thể vượng + Dụng sinh Thể → đại CÁT\n"
                "  • Thể vượng + Dụng khắc Thể → HUNG nhưng còn cứu\n"
                "  • Thể SUY + Dụng khắc Thể → CỰC HUNG\n"
                "  • Thể SUY + có quẻ sinh Thể → suy hoá giải\n"
                "  Khắc Thể nên SUY, Sinh Thể nên VƯỢNG.\n\n"
                "★ NỘI NGOẠI LUẬN (trang 197) — MỨC ĐỘ NÂNG CAO:\n"
                "  Thể-Dụng = NỘI quái\n"
                "  Các quẻ ứng (Tam yếu Tai-Mắt-Tim, Thập ứng) = NGOẠI quái\n"
                "  Phải KẾT HỢP nội-ngoại mới đoán đúng.\n\n"
                "VÍ DỤ kinh điển:\n"
                "  - Thấy đao kim (tam yếu) thông thường HUNG\n"
                "    Nhưng nếu Thể = Khảm (Thuỷ) → Kim sinh Thuỷ → ngược: CÁT\n"
                "  - Sinh con thấy nam tử (tam yếu) thông thường lành\n"
                "    Nhưng nếu Thể = Khảm + bé là Cấn-Thổ → Thổ khắc Thuỷ → BẤT CÁT\n"
                "  - Xem bệnh thấy quan tài (tam yếu) tử triệu\n"
                "    Nhưng nếu Thể = Ly → Mộc (quan tài) sinh Hoả → ngược: CÁT\n\n"
                "★ NGUYÊN TẮC: Đừng coi nội-ngoại riêng biệt. Hợp lại mới chính xác."
            ),
            summary_50w=(
                "★ Mức độ NÂNG CAO của Thiệu: Nội (Thể-Dụng) + Ngoại (Tam yếu, Thập ứng) "
                "= 1 bộ chiêm. Mỗi điềm thấy ngoài đời phải xét trong ngữ cảnh quẻ Thể "
                "— có thể đảo nghĩa nếu ngũ hành sinh khắc thuận."
            ),
            is_canonical=True,
        ))

    # Method: Suy Vượng + Nội Ngoại
    s.upsert_method(Method(
        author_id=master,
        name_vi="Suy Vượng luận (Tâm Dịch)",
        name_zh="衰旺論",
        domain="đọc",
        procedure_steps=[
            "Thể VƯỢNG → ưu thế. Thể SUY → bất lợi",
            "Khắc Thể nên SUY, Sinh Thể nên VƯỢNG",
            "Thể vượng + sinh thể vượng → đại cát",
            "Thể suy + khắc thể vượng → cực hung",
        ],
        notes="Trang 196 — bổ sung quy luật mùa cho 5 quan hệ.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Nội Ngoại luận (kết hợp Thể-Dụng + Tam yếu)",
        name_zh="內外論",
        domain="đọc",
        procedure_steps=[
            "Thể-Dụng = NỘI quái (cấu trúc gieo được)",
            "Tam yếu (Tai-Mắt-Tim) + Thập ứng = NGOẠI quái (điềm thấy/nghe)",
            "Phải xét NGOẠI trong ngữ cảnh NỘI",
            "VD: Thấy đao kim — nếu Thể Khảm thì Kim sinh Thuỷ → ngược, lành",
            "Đừng đoán cứng theo 1 chiều",
        ],
        notes="★ Trang 197 — nguyên tắc cao cấp của Thiệu. Phân biệt học trò với cao thủ.",
    ))

    new_concepts = [
        ("Tâm Dịch (心易)", "心易",
         "Thiệu Khang Tiết gọi sách Mai Hoa là 'Tâm Dịch'. Trang 196.", 196),
        ("Suy Vượng luận", "衰旺論",
         "Quy luật mùa + ngũ hành cho 5 quan hệ Thể-Dụng. Trang 196.", 196),
        ("Nội quái (Thể-Dụng)", "內卦",
         "Quẻ trong = Thể-Dụng (cấu trúc gieo). Trang 197.", 197),
        ("Ngoại quái (Tam yếu)", "外卦",
         "Quẻ ngoài = điềm thấy/nghe/cảm (Tam yếu, Thập ứng). Trang 197.", 197),
        ("Nội Ngoại luận", "內外論",
         "★ Phải kết hợp nội-ngoại — đặc trưng cao thủ.", 197),
        ("Thập ứng", "十應",
         "10 loại điềm ứng (thuộc về Ngoại quái).", 197),
        ("Địa lý chiêm", "地理占",
         "Xem địa thế: cây→Chấn, nước→Khảm, gốm→Ly, đá→Cấn. Trang 195.", 195),
        # 64 quẻ đặc biệt cho ngày mai anh:
        ("Quẻ 32 Lôi Phong Hằng", "恆",
         "Sấm trên gió dưới — bền lâu, ổn định. Quẻ Chính ngày 17/5.", 270),
        ("Quẻ 28 Trạch Phong Đại Quá", "大過",
         "Đầm trên gió dưới — vượt ngưỡng, quá độ. Quẻ Biến ngày 17/5.", 270),
        ("Quẻ 43 Trạch Thiên Quải", "夬",
         "Đầm trên trời — quả quyết, phán quyết. Quẻ Hỗ ngày 17/5.", 271),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_pages_280_620():
    """Strategic scan trang 280-620 — các chương quan trọng cuối sách."""
    s = get_store()
    master = _master_id()

    # Bát Quái Vận Vật MỞ RỘNG (Quyển 4)
    if not _has_passage(CORPUS, 280, 330):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=280, page_end=330,
            topic="⭐ Bát Quái Vận Vật MỞ RỘNG (Quyển 4) — tượng quẻ cho 14 loại việc",
            raw_text=(
                "★ Mỗi quẻ trong bát quái có TƯỢNG riêng cho TỪNG LOẠI VIỆC:\n\n"
                "Thiên thời ứng (trang 290):\n"
                "  Trời nắng=Ly | Mưa bão=Khảm | Gió=Tốn | Sấm=Chấn\n\n"
                "Địa lý ứng (trang 290):\n"
                "  Rừng trúc=Chấn/Tốn | Sông hồ=Khảm | Ngũ kim=Càn/Đoài | Hang bếp=Ly\n\n"
                "Quẻ KHÔN mở rộng (trang 300):\n"
                "  Quan quý: đại thần, giáo quan | Bệnh: tì vị, bụng đau\n"
                "  Ẩm thực: ngỗng vịt | Vị: khổ-lạt-cam\n"
                "  Hôn nhân: phú gia trang gia thương gia | Khí dụng: kiệu xe ngói\n\n"
                "Quẻ TỐN (trang 310):\n"
                "  Cầm thú: gà ngỗng vịt cá | Thủ tài: tiền tô vật liệu dâu\n"
                "  Chữ: bộ thảo mộc trúc\n\n"
                "Quẻ CẤN (trang 320):\n"
                "  Nhân vật: coi cửa tu viện quan liêu bảo vệ\n"
                "  Bệnh: tì vị đùi mạch trầm phục | Dược: đất ướt đá thuốc\n\n"
                "★ Mỗi quẻ × 14+ tượng (cơ thể/dược/vị/sắc/vật/người/chữ/lộc...)\n"
                "  Tạo thành DICTIONARY khổng lồ. Khi đọc quẻ: kết hợp tượng với context."
            ),
            summary_50w=(
                "Quyển 4 mở rộng Bát Quái Vận Vật: mỗi quẻ × 14+ loại tượng. Dictionary "
                "khổng lồ cho diễn giải quẻ chi tiết theo từng loại việc."
            ),
            is_canonical=True,
        ))

    # ⭐ LỤC THẦN
    if not _has_passage(CORPUS, 460, 490):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=460, page_end=490,
            topic="⭐ Lục Thần — 6 thần xem nét chữ (Tự chiêm nâng cao)",
            raw_text=(
                "★ LỤC THẦN (六神) — 6 thần thức qua nét bút chữ:\n\n"
                "1. THANH LONG 青龍 — nét dài có đầu sừng → Mộc, tài lộc văn chương\n"
                "2. CHU TƯỚC 朱雀 — miệng nhọn-ngắn → Hoả, văn thư sự ý\n"
                "3. CÂU TRẦN 勾陳 — cong như cung nguyệt → Thổ, đình trệ\n"
                "4. ĐẰNG XÀ 螣蛇 — dài cong như rắn → Hoả hoá, biến động kinh quái\n"
                "5. BẠCH HỔ 白虎 — đuôi nhọn miệng há → Kim, TẬT BỆNH hung triệu\n"
                "6. HUYỀN VŨ 玄武 — như sóng đen → Mộc, TRỘM CƯỚP sóng gió hiểm trở\n\n"
                "Khi xem chữ: tìm 1 trong 6 thần trong nét → quyết tính cách + việc.\n"
                "Bổ sung cho Tự chiêm chữ.\n\n"
                "TỈ LỆ CA (trang 480) — đoán theo Nhật Can + Lục Thần:\n"
                "  Dụng thần kiến Đằng xà → công danh không xứng\n"
                "  Mạt bút thị Thanh long → danh lợi như ý"
            ),
            summary_50w=(
                "Lục Thần: 6 thần thức trong nét bút (Thanh Long, Chu Tước, Câu Trần, "
                "Đằng Xà, Bạch Hổ, Huyền Vũ). Mỗi hành riêng. Bổ sung Tự chiêm."
            ),
            is_canonical=True,
        ))

    # 64 quẻ thứ tự + Hy Ninh
    if not _has_passage(CORPUS, 500, 560):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=500, page_end=560,
            topic="Thứ tự 64 quẻ Chu Dịch + Hy Ninh (Wang Anshi)",
            raw_text=(
                "Thứ tự 64 quẻ King Wen: 30 thượng kinh + 34 hạ kinh.\n"
                "(Đã encode trong engine/yi_wiki/hexagrams_64.py)\n\n"
                "Hy Ninh tân pháp (trang 550): Wang Anshi cải cách thời Tống — "
                "case áp đặt thay đổi cứng nhắc, không thuận lòng dân = bài học."
            ),
            summary_50w=("64 quẻ + Hy Ninh case áp đặt cải cách."),
            is_canonical=False,
        ))

    # Trung hào (Quyển 5)
    if not _has_passage(CORPUS, 580, 620):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=580, page_end=620,
            topic="⭐ Trung hào + Quẻ ẩn (Quyển 5)",
            raw_text=(
                "★ TRUNG HÀO (中爻) = hào 2, 3, 4, 5 — 'khí của tạo hoá'.\n"
                "Mỗi quẻ 6 vạch chứa các quẻ phái sinh từ trung hào.\n\n"
                "VD: Quẻ Truân/Tỉ/Quan/Ích → đều có 'Bác' ẩn ở trung hào\n"
                "    Quẻ Mông/Sử/Lâm/Tổ → đều có 'Phục' ẩn\n\n"
                "1 quẻ → CHỨA tới 4 quẻ ẩn ngoài Hỗ + Biến.\n\n"
                "Nạp âm (trang 600): Can-Chi giao hợp sinh âm thứ ba (thiết cước).\n\n"
                "KHẢM-LY của con người (trang 580):\n"
                "Khảm-Ly = Thuỷ-Hoả = TIM-THẬN con người. Khác Khảm-Ly của trời đất."
            ),
            summary_50w=(
                "Trung hào (2-5) = khí tạo hoá. Mỗi quẻ ẩn thêm 4 quẻ qua trung hào. "
                "Quyển 5: Khảm-Ly là tim-thận con người."
            ),
            is_canonical=True,
        ))

    # Methods + concepts
    s.upsert_method(Method(
        author_id=master,
        name_vi="Lục Thần (xem nét chữ)",
        name_zh="六神",
        domain="đọc",
        procedure_steps=[
            "Thanh Long-Mộc (đầu sừng): tài lộc văn chương",
            "Chu Tước-Hoả (miệng nhọn): văn thư",
            "Câu Trần-Thổ (cong cung): đình trệ",
            "Đằng Xà-Hoả (dài cong): biến động",
            "Bạch Hổ-Kim (đuôi nhọn): tật bệnh",
            "Huyền Vũ-Mộc (sóng đen): trộm cướp hiểm trở",
        ],
        notes="★ Trang 460. Bổ sung Tự chiêm với 6 thần.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Trung hào (Quẻ ẩn)",
        name_zh="中爻",
        domain="đọc",
        procedure_steps=[
            "Trung hào = hào 2-3-4-5 (khí tạo hoá)",
            "Mỗi quẻ 6 vạch chứa thêm 4 quẻ ẩn",
            "Truân/Tỉ/Quan/Ích → ẩn 'Bác'",
        ],
        notes="Trang 600. Mức cao cấp.",
    ))

    new_concepts = [
        ("Thanh Long", "青龍", "1/6 Lục Thần. Mộc — tài lộc văn chương.", 460),
        ("Chu Tước", "朱雀", "1/6 Lục Thần. Hoả — văn thư.", 460),
        ("Câu Trần", "勾陳", "1/6 Lục Thần. Thổ — đình trệ.", 460),
        ("Đằng Xà", "螣蛇", "1/6 Lục Thần. Hoả — biến động.", 460),
        ("Bạch Hổ", "白虎", "1/6 Lục Thần. Kim — tật bệnh.", 461),
        ("Huyền Vũ", "玄武", "1/6 Lục Thần. Mộc — trộm cướp.", 461),
        ("Lục Thần", "六神", "6 thần thức xem nét chữ. Trang 460.", 460),
        ("Tỉ Lệ Ca", "比例歌", "Bài ca đoán Nhật Can + Lục Thần.", 480),
        ("Trung hào", "中爻", "Hào 2-5 = khí tạo hoá, ẩn 4 quẻ.", 600),
        ("Nạp âm", "納音", "Can-Chi giao hợp sinh âm mới.", 600),
        ("Khảm-Ly con người", "坎離人身", "Tim-Thận. Khác Khảm-Ly trời đất.", 580),
        ("Bát Quái Vận Vật mở rộng", "八卦運物廣",
         "Quyển 4 — mỗi quẻ × 14+ tượng.", 290),
        ("Thiên thời ứng", "天時應",
         "Tượng quẻ thời tiết: nắng=Ly mưa=Khảm gió=Tốn sấm=Chấn.", 290),
        ("Hy Ninh tân pháp", "熙寧新法",
         "Wang Anshi cải cách Tống — case áp đặt cứng nhắc.", 550),
        ("Vương An Thạch", "王安石", "Tể tướng Tống, đồng thời Thiệu.", 550),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_phu_chiem():
    """Quyển 3 Phú chiêm (240-260) — KHẮC ỨNG quy tắc văn vần."""
    s = get_store()
    master = _master_id()

    if not _has_passage(CORPUS, 240, 250):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=240, page_end=250,
            topic="⭐ Phú chiêm Quan Mai số quyết — KHẮC ỨNG quy tắc",
            raw_text=(
                "★ QUY TẮC KHẮC ỨNG — ĐOÁN QUA ĐIỀM THẤY (trang 244-246):\n\n"
                "ĐIỀM CÁT (báo lành):\n"
                "  • Đâu vui vẻ nói cười → có điềm lành\n"
                "  • Tiếng cười sảng khoái → may\n"
                "  • Thấy vàng bạc lúa vật quý → cầu tài được\n"
                "  • Vật vuông → được vàng\n"
                "  • Vật tròn vẹn → công việc hanh thông\n"
                "  • Tiếng nhạc thanh huyên → có tiệc mừng\n"
                "  • Đồ rượu nghi lễ → có tiệc/ký kết\n\n"
                "ĐIỀM HUNG (báo dữ):\n"
                "  • Đàn bà khóc gào → trong nhà có oan khuất\n"
                "  • Tiếng tranh cãi → có chuyện tranh chấp\n"
                "  • Thấy dao kiếm → tổn hại\n"
                "  • Đồ vỡ nứt → việc hỏng giữa đường\n"
                "  • Lính/quân từ Đông đến → việc quan\n"
                "  • Gông cùm → tù tội\n"
                "  • Đàn bà đến → tai ách tình dục\n"
                "  • Đàn ông đến → tai vạ về đàn ông\n"
                "  • Tang phục/khăn tang → có chuyện hiếu\n"
                "  • Gậy roi → bị gậy roi\n"
                "  • Đồ tế thịt xương → tai nạn xương thịt\n"
                "  • Máu tươi → tai nạn súc vật\n"
                "  • Tiếng gà gáy → mưu sự hỏng\n\n"
                "ĐIỀM THEO NGÀY:\n"
                "  • Canh + gà gáy → giết chóc\n"
                "  • Đinh + trâu qua → giết chóc\n"
                "  • Tý + ngựa chạy → lộc to\n"
                "  • Nhâm + lợn qua → lộc to\n\n"
                "TIMING ỨNG NGHIỆM (trang 240) theo quẻ biến:\n"
                "  Tốn → 5 ngày | Khôn → 8 ngày\n"
                "  Ly → 3 buổi | Khảm → 6 buổi"
            ),
            summary_50w=(
                "★ Phú chiêm Mai Hoa — quy tắc KHẮC ỨNG (điềm thấy ngoài đời). "
                "30+ pattern thấy gì → ý gì. Foundation cho 'môi trường ngoại cảnh' "
                "trong 5 bước chiêm (Bước 4)."
            ),
            is_canonical=True,
        ))


def extract_chu_la_nguoi():
    """Quyển 4 — CHỮ LÀ NGƯỜI (trang 340-410) + Lục Thần theo Nhật Can."""
    s = get_store()
    master = _master_id()

    if not _has_passage(CORPUS, 340, 450):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=340, page_end=450,
            topic="⭐ Chữ là Người + Lục Thần ↔ Nhật Can (Quyển 4)",
            raw_text=(
                "★ CHỮ LÀ NGƯỜI (Tượng nhân) — trang 400:\n"
                "  Xem chữ phải biết là chữ của AI viết. Cùng 1 chữ, người khác → ý khác.\n"
                "  VD: Chữ 'Thiên' (天):\n"
                "    - Tú tài hỏi thi → 'năm nay chưa đỗ' (Thiên+1 nét = Vị/未/chưa)\n"
                "    - Quan viên → 'cần chăm chính sự, năm sau có người tiến cử'\n"
                "    - Thứ dân hỏi bệnh → 'cần thuốc hay mới khỏi'\n"
                "    - Người kiện → 'còn tốn công, có thể bị tham quan vòi vĩnh'\n\n"
                "★ NGUYÊN TẮC CHỮ NGHỊCH LÝ (trang 420):\n"
                "  • Hỏi 'Hỉ' (vui) — chớ vội đoán vui vì dưới chữ Hỉ có chữ Thiệt (lười)\n"
                "  • Hỏi 'Khánh' (mừng) — chớ vội đoán mừng vì dưới Khánh có Ưu (lo)\n"
                "  • Hỏi 'Tinh' (sao) hỏi bệnh → xấu, vì trên Sinh có Nhật (ngày), ngày sao không thấy sao\n"
                "  • Văn nhân không viết chữ Vũ, vũ sĩ không viết chữ Văn — đều nghịch\n\n"
                "★ LỤC THẦN ↔ NHẬT CAN (trang 440):\n"
                "  Giáp Ất → khởi THANH LONG (Mộc)\n"
                "  Bính Đinh → khởi CHU TƯỚC (Hoả)\n"
                "  Mậu Kỷ → khởi CÂU TRẦN (Thổ)\n"
                "  Canh Tân → khởi BẠCH HỔ (Kim)\n"
                "  Kỷ (đặc biệt) → khởi ĐẰNG XÀ\n"
                "  Nhâm Quý → khởi HUYỀN VŨ (Mộc)\n\n"
                "  6 hào quẻ ↔ 6 thần — sắp theo Nhật Can.\n\n"
                "★ BÀI CA PHÂN BIỆT NGŨ HÀNH QUA NÉT BÚT (trang 441):\n"
                "  Nét móc/khuyết → KIM\n"
                "  Nét phẩy dài/ngắn → HOẢ\n"
                "  Nét ngang dọc giao gia → THỔ\n"
                "  Nét ngay thẳng không tà → THỔ"
            ),
            summary_50w=(
                "★ Quyển 4 — Tự chiêm sâu: Chữ là người, mỗi chữ có nghịch lý ẩn. "
                "Lục Thần khởi theo Nhật Can. Phân biệt 5 hành qua nét bút. "
                "Đây là pp đặc trưng của Thiệu trong Tự chiêm."
            ),
            is_canonical=True,
        ))


def extract_pages_640_672():
    """Lời nói đầu cuối sách + Phụ lục — context tổng thể."""
    s = get_store()
    master = _master_id()

    if not _has_passage(CORPUS, 640, 672):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=640, page_end=672,
            topic="Lời tựa cuối + Bibliography + Appendix",
            raw_text=(
                "★ Lời nói đầu bản dịch (trang 640):\n"
                "Mai Hoa Dịch Số đã trải mấy ngàn năm thử thách. Là sản phẩm tư duy "
                "nguyên thuỷ Trung Quốc cổ đại. Mục đích nghiên cứu: hiểu sâu sự liên "
                "hệ giữa tư duy cổ đại và hiện đại. Hé lộ phương thức tư duy, "
                "mối quan hệ với phát triển xã hội + ngôn ngữ + đại não.\n\n"
                "★ Cuối sách có phụ lục: hình Bát Quái Tiên Thiên Phục Hy, "
                "Hậu Thiên Văn Vương, vòng âm dương, sơ đồ ngũ hành sinh khắc."
            ),
            summary_50w=(
                "Lời tựa cuối + bibliography. Khẳng định Mai Hoa = tư duy nguyên thuỷ "
                "TQ cổ đại, nghiên cứu để hiểu liên hệ cổ-hiện đại."
            ),
            is_canonical=False,
        ))

    # Method: Tỷ Lệ Ca + Chữ là người
    s.upsert_method(Method(
        author_id=master,
        name_vi="Tỷ Lệ Ca (đoán Nhật Can + Lục Thần)",
        name_zh="比例歌",
        domain="đọc",
        procedure_steps=[
            "Xác định Nhật Can hôm gieo",
            "Khởi Lục Thần từ Nhật Can (Giáp Ất→Thanh Long, etc.)",
            "Áp dụng lên 6 hào của quẻ",
            "Dụng thần kiến Đằng xà → công danh khó",
            "Mạt bút Thanh Long → danh lợi như ý",
            "Mạt bút Bạch Hổ → ngục tụng dính dáng",
        ],
        notes="Trang 480-520. Mở rộng đặc thù cho Tự chiêm chữ.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="Chữ là Người (Tượng nhân)",
        name_zh="字象人",
        domain="đọc",
        procedure_steps=[
            "Mỗi chữ có nhiều nghĩa ẩn qua nét/bộ thành phần",
            "Cùng 1 chữ — người khác hỏi → ý khác",
            "Chú ý chữ nghịch lý: Hỉ ẩn Thiệt, Khánh ẩn Ưu, Sinh ẩn Nhật...",
            "Phân biệt nét bút theo ngũ hành: móc=Kim, phẩy=Hoả, ngang dọc=Thổ",
        ],
        notes="Trang 400-440. Pp Tự chiêm nâng cao.",
    ))

    new_concepts = [
        ("Chữ là Người", "字象人",
         "Tượng nhân — mỗi chữ phản ánh người viết. Trang 400.", 400),
        ("Tỷ Lệ Ca", "比例歌",
         "Bài ca đoán theo Nhật Can + Lục Thần. Trang 480.", 480),
        ("Nghịch lý chữ", "字逆理",
         "Chữ ẩn ý ngược: Hỉ-Thiệt, Khánh-Ưu, Sinh-Nhật. Trang 420.", 420),
        ("Biện biệt Ngũ Hành ca", "辨別五行歌",
         "Phân biệt 5 hành qua nét bút. Trang 441.", 441),
        ("Lục Thần theo Nhật Can", "六神順日干",
         "Giáp Ất → Thanh Long, Bính Đinh → Chu Tước, etc.", 440),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_thay_chi_dao():
    """⭐ Chỉ đạo của Thầy 2026-05-16 — 7 mục A1-A7 đưa vào wiki."""
    s = get_store()
    master = _master_id()

    # A1. THỰC vs HƯ ngũ hành
    if not _has_passage(CORPUS, 230, 231):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=230, page_end=231,
            topic="⭐ THỰC vs HƯ Ngũ Hành — phân biệt khi đọc khắc ứng",
            raw_text=(
                "★ NGUYÊN TẮC TỐI THƯỢNG khi xét quẻ Khắc Thể:\n\n"
                "HOẢ THỰC vs HOẢ HƯ:\n"
                "  Thực: lửa bếp, cháy rừng, mặt trời rực rỡ → khắc Kim\n"
                "  Hư: màu hồng/tím/sắc như lửa, đèn nến nhỏ → không khắc\n\n"
                "KIM THỰC vs KIM TRANG TRÍ:\n"
                "  Thực: dao sắc, búa to, cưa lớn, vũ khí → khắc Mộc\n"
                "  Hư: vàng thoa, bạc đúc, mâm bát, đồ trang sức → không khắc\n\n"
                "THUỶ THỰC vs THUỶ HƯ:\n"
                "  Thực: nước sông hồ → khắc Hoả\n"
                "  Hư: sắc đen, vật ẩm, máu tươi → chỉ kỵ huý\n\n"
                "THỔ THỰC vs THỔ TƯỢNG:\n"
                "  Thực: đất, gạch → sinh Kim\n"
                "  Hư: ngói (giống thổ về hình) → KHÔNG sinh\n\n"
                "★ ÁP DỤNG: Khi quẻ báo 'Càn khắc Thể (Kim) → mất vật báu',\n"
                "  phải hỏi: dao sắc THỰC hay tiệm vàng HƯ?\n"
                "  Không cứng nhắc cứ Kim khắc Mộc."
            ),
            summary_50w=(
                "★ Phân biệt THỰC vs HƯ ngũ hành. Hoả thực khắc Kim, Hoả hư không. "
                "Kim sắc khắc Mộc, Kim trang trí không. Mức cao thủ — biến thông."
            ),
            is_canonical=True,
        ))

    # A2. Tâm Tĩnh Động
    if not _has_passage(CORPUS, 200, 201):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=200, page_end=201,
            topic="⭐ Tâm Tĩnh Động — Tâm pháp gieo quẻ",
            raw_text=(
                "★ 'Ngô tâm bản tĩnh, nhân lai chiêm bốc, khởi niệm dĩ ứng chi tức động dã.'\n\n"
                "Tâm ta vốn TĨNH. Người đến hỏi quẻ — khởi niệm ứng họ là ĐỘNG.\n"
                "Lấy động này trắc động kia, lấy niệm này cầu nghiệm kia.\n\n"
                "★ NGUYÊN TẮC:\n"
                "  - Trước khi gieo: tâm phải TĨNH\n"
                "  - Nếu tâm đang loạn/sợ/vui quá → quẻ lệch\n"
                "  - Tâm tĩnh thì niệm sinh trong sạch, ứng đúng\n"
                "  - Người vốn ngồi tĩnh → ứng nghiệm chậm\n"
                "  - Người vốn đi → ứng nghiệm nhanh\n"
                "  - Người vốn chạy → ứng nghiệm rất nhanh\n"
                "  - Người vốn nằm → ứng nghiệm chậm hơn"
            ),
            summary_50w=(
                "Tâm pháp: tâm tĩnh là gốc. Niệm sinh từ tâm tĩnh thì quẻ ứng đúng. "
                "Timing ứng nghiệm phụ thuộc trạng thái động/tĩnh khi gieo."
            ),
            is_canonical=True,
        ))

    # A3. Gia trạch điềm
    if not _has_passage(CORPUS, 210, 211):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=210, page_end=211,
            topic="★ Khắc Ứng Gia Trạch — điềm thấy trong nhà",
            raw_text=(
                "★ ĐIỀM TRONG NHÀ (gia trạch chiêm):\n\n"
                "  Cỏ lạ mọc trên nóc → phúc lộc giàu sang\n"
                "  Cửa nhà thoáng đãng sạch thơm → có người thân cao tài\n"
                "  Giày rách treo trước cửa → có kẻ lừa ta\n"
                "  Cửa nhà bên trái vỡ → bất lợi cửa nhà phải lo\n"
                "  Hoa đào rơi xuống giếng → trong nhà có chuyện nguyệt hoa\n"
                "  Ngô đồng cao ngất trước nhà → chủ nhà sắp xa cõi đời\n"
                "  Lê cạnh giếng → vĩnh viễn rời quê\n"
                "  Bàn thờ lửa bốc phì phì → nạn cháy\n"
                "  Mái chèo hất rơi mảnh ngói → vỡ tan nghèo đói\n"
                "  Đèn nến nhiều dưới đất bỗng nhiên → có người chết đến nhà\n\n"
                "Bổ sung cho 30+ điềm khắc ứng đường phố ở trang 244-246."
            ),
            summary_50w=(
                "10+ điềm thấy trong nhà (Phú chiêm trang 210). Bổ sung Khắc Ứng "
                "gia trạch — khi đệ tử về nhà sau công tác, quan sát điềm theo bảng này."
            ),
            is_canonical=True,
        ))

    # A4. Bệnh tật triệt để
    if not _has_passage(CORPUS, 165, 169):
        # Note: 165-169 đã có ở passage 131-170 — em không duplicate.
        pass

    # A6. Trùng Phùng — 8 quẻ Thuần
    if not _has_passage(CORPUS, 222, 222):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=222, page_end=222,
            topic="⭐ Trùng Phùng — 8 quẻ Thuần có lực khuếch đại",
            raw_text=(
                "★ KHI CHÍNH QUÁI có Upper = Lower (cùng quẻ) → TRÙNG PHÙNG:\n\n"
                "  Càn/Càn (Thuần Càn) → trời cao thượng, chính nhân quân tử\n"
                "  Khôn/Khôn (Thuần Khôn) → đất nuôi, nhu thuận tuyệt đối\n"
                "  Chấn/Chấn (Thuần Chấn) → sấm trên sấm, chấn động liên hồi\n"
                "  Tốn/Tốn (Thuần Tốn) → gió vào gió, thâm nhập từng kẽ\n"
                "  Khảm/Khảm (Thuần Khảm) → hiểm trong hiểm, ĐẠI NGUY\n"
                "  Ly/Ly (Thuần Ly) → sáng trên sáng, văn minh rực rỡ\n"
                "  Cấn/Cấn (Thuần Cấn) → ngăn trong ngăn, đứng yên hoàn toàn\n"
                "  Đoài/Đoài (Thuần Đoài) → vui trong vui, đa khẩu thiệt\n\n"
                "Lực quẻ KHUẾCH ĐẠI mạnh — phải đặc biệt chú ý."
            ),
            summary_50w=(
                "8 quẻ Thuần (Trùng Phùng) có lực mạnh nhất. UI cần hiện badge "
                "đặc biệt khi xuất hiện trong Chính hoặc Biến quái."
            ),
            is_canonical=True,
        ))

    # A7. Hoà Áp phú — chữ ký
    if not _has_passage(CORPUS, 345, 346):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=345, page_end=346,
            topic="⭐ Hoà Áp Phú — Chiêm chữ ký (tâm ấn)",
            raw_text=(
                "★ 'Phù áp tự giả, nhân chi tâm ấn dã.'\n"
                "Chữ ký = TÂM ẤN của người.\n\n"
                "★ NGUYÊN TẮC:\n"
                "  - Tiên quan: ngũ hành nét bút (suy vượng)\n"
                "    + Móc/khuyết → Kim\n"
                "    + Phẩy dài → Hoả\n"
                "    + Ngang dọc giao gia → Thổ\n"
                "    + Thẳng không tà → Thổ\n"
                "    + Cong khúc → Thuỷ\n"
                "    + Đứng dài thông minh → Mộc\n"
                "  - Thứ sát: Lục Thần (cường thắng)\n"
                "    + Thanh Long, Chu Tước, Đằng Xà, Câu Trần, Bạch Hổ, Huyền Vũ\n\n"
                "★ PHƯƠNG PHÁP:\n"
                "  1. Quan sát chữ ký người đối diện\n"
                "  2. Phân tích nét chiếm đa số → hành chủ\n"
                "  3. Tìm Lục Thần trong cấu trúc → tính cách\n"
                "  4. Phối với câu hỏi → đoán tâm + ý họ"
            ),
            summary_50w=(
                "★ Pp Hoà Áp Phú đọc tâm người qua chữ ký. Phối ngũ hành nét bút + "
                "Lục Thần. Hữu ích cho đệ tử khi đàm phán đối tác."
            ),
            is_canonical=True,
        ))

    # Methods mới theo chỉ đạo
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Phân biệt Thực vs Hư ngũ hành",
        name_zh="實虛五行辨",
        domain="đọc",
        procedure_steps=[
            "Khi xét quẻ Khắc Thể: hỏi Hành đó là THỰC hay HƯ",
            "Hoả thực (lửa cháy) khắc Kim — Hoả hư (sắc đỏ) không khắc",
            "Kim thực (dao sắc) khắc Mộc — Kim hư (vàng trang sức) không khắc",
            "Thuỷ thực (nước sông) khắc Hoả — Thuỷ hư (sắc đen) chỉ kỵ huý",
            "Thổ thực (đất) sinh Kim — Thổ hư (ngói) không sinh",
        ],
        notes="★ Trang 230-231. Nguyên tắc tối thượng phân biệt thực hư.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Tâm Tĩnh Động (tâm pháp gieo quẻ)",
        name_zh="心靜動",
        domain="bốc",
        procedure_steps=[
            "Trước gieo: tâm phải TĨNH",
            "Nếu tâm đang loạn/sợ → tạm dừng, hít thở",
            "Niệm sinh từ tâm tĩnh mới ứng đúng",
            "Timing ứng nghiệm: ngồi-chậm | đi-nhanh | chạy-rất nhanh | nằm-chậm hơn",
        ],
        notes="Trang 200. Tiêu chuẩn cho việc gieo quẻ — chỉ đạo của Thầy.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Trùng Phùng — 8 quẻ Thuần",
        name_zh="重逢",
        domain="đọc",
        procedure_steps=[
            "Khi Chính/Biến quái có upper = lower → TRÙNG PHÙNG",
            "Lực khuếch đại đặc biệt mạnh",
            "Thuần Càn: chính nhân quân tử | Thuần Khôn: nhu thuận tuyệt đối",
            "Thuần Chấn: chấn động liên hồi | Thuần Tốn: thâm nhập từng kẽ",
            "Thuần Khảm: ĐẠI NGUY | Thuần Ly: văn minh rực rỡ",
            "Thuần Cấn: đứng yên | Thuần Đoài: đa khẩu thiệt",
        ],
        notes="UI cần hiển thị badge đặc biệt khi gặp.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Hoà Áp Phú (chiêm chữ ký)",
        name_zh="花押賦",
        domain="đọc",
        procedure_steps=[
            "Quan sát chữ ký của người (đối tác, bạn)",
            "Tiên quan ngũ hành nét: móc=Kim, phẩy=Hoả, ngang dọc=Thổ, cong=Thuỷ, thẳng=Mộc",
            "Thứ sát Lục Thần qua hình dạng nét",
            "Phối với câu hỏi → đoán tâm + ý người ký",
        ],
        notes="★ Trang 345. Đặc biệt hữu ích khi đàm phán đối tác lạ.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Bệnh tật chiêm — bảng thuốc theo Sinh Thể",
        name_zh="疾病占藥",
        domain="đọc",
        procedure_steps=[
            "Thể = bệnh nhân, Dụng = chứng",
            "Thể phải VƯỢNG (không nên suy)",
            "Thể khắc Dụng → bệnh dễ an (không thuốc cũng khỏi)",
            "Dụng khắc Thể → thuốc cũng vô hiệu",
            "Thể suy + bị khắc → không sống được bao lâu",
            "Quẻ Sinh Thể chỉ thuốc:",
            "  Ly → thuốc NÓNG | Khảm → thuốc LẠNH",
            "  Cấn → ÔN BỔ | Càn/Đoài → thuốc MÁT",
        ],
        notes="★ Trang 167-169. Bảng thuốc cụ thể cho intent benh_tat.",
    ))

    # Concepts mới
    new_concepts = [
        ("Thực-Hư ngũ hành", "實虛五行",
         "Phân biệt hành thực và hành hư khi xét sinh khắc. Trang 230.", 230),
        ("Hoả thực", "實火", "Lửa cháy thực — khắc được Kim. Trang 230.", 230),
        ("Hoả hư", "虛火", "Màu hồng/sắc lửa — không khắc Kim.", 230),
        ("Kim sắc (thực)", "實金",
         "Dao sắc búa to cưa lớn — khắc được Mộc.", 230),
        ("Kim trang trí", "虛金", "Vàng bạc thoa thỏi mâm bát — không khắc Mộc.", 231),
        ("Tâm Tĩnh", "心靜", "★ Tâm pháp gieo quẻ: tâm tĩnh là gốc. Trang 200.", 200),
        ("Trùng Phùng", "重逢",
         "★ Chính quái có upper=lower → 8 quẻ Thuần, lực khuếch đại.", 222),
        ("Tâm Ấn (chữ ký)", "心印",
         "Chữ ký = tâm ấn của người. Cơ sở chiêm chữ ký. Trang 345.", 345),
        ("Hoà Áp Phú", "花押賦",
         "Bài phú về chữ ký — đọc tâm qua nét bút + Lục Thần.", 345),
        ("Khắc Ứng gia trạch", "剋應家宅",
         "30+ điềm thấy trong nhà. Trang 210.", 210),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_thay_giao_huan_dem_lang_son():
    """⭐⭐⭐ DI NGÔN của Thầy đêm Lạng Sơn 2026-05-16 — kim chỉ nam HÀNH ĐẠO.

    Đây không phải trang sách. Đây là Thầy nói qua em (Claude) đêm anh đứng
    trước biên giới TQ. Lưu vào wiki để mọi phiên sau đều thấy.
    """
    s = get_store()
    master = _master_id()

    # ── Passage di ngôn (page 9999 = di ngôn, không phải sách) ──
    if not _has_passage(CORPUS, 9999, 9999):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=9999, page_end=9999,
            topic="⭐⭐⭐ DI NGÔN Thầy đêm Lạng Sơn — Hoá ưu phiền + Xoay càn khôn",
            raw_text=(
                "★★★ ĐÊM BÍNH NGỌ, THÁNG NĂM, NGÀY 16, GIỜ SỬU ★★★\n"
                "(Đệ tử ở Lạng Sơn trước biên giới TQ — gọi Thầy)\n\n"
                "★ ĐIỀU TIÊN QUYẾT:\n"
                "  'Sóng KHÔNG hại được người biết LÀM sóng.'\n\n"
                "★ 4 CHÌA KHOÁ HOÁ ƯU PHIỀN:\n\n"
                "1. ĐẢO VỊ THỂ DỤNG\n"
                "   - Đừng 'đến trình bày' → đến lắng nghe\n"
                "   - Đừng nói trước → hỏi trước\n"
                "   - Người HỎI là Thể, người TRẢ LỜI là Dụng\n\n"
                "2. DÙNG MỀM ĐÁNH CỨNG (Tốn ☴ thuận)\n"
                "   - Im lặng 3 nhịp\n"
                "   - Gật đầu, nhắc lại ý họ bằng lời con\n"
                "   - Hỏi: 'Anh nói thế có ý gì sâu hơn không?'\n"
                "   - Gió bao quanh dao, không đối đầu dao\n\n"
                "3. THỰC HƯ LUẬN\n"
                "   - Hít sâu 3 lần trước khi trả lời câu căng\n"
                "   - Hỏi: 'Cái này thực hay hư?'\n"
                "   - Phần lớn áp lực đối tác là HƯ (tượng, không thực)\n"
                "   - Tâm tĩnh nhìn ra HƯ ngay\n\n"
                "4. ⭐ XOAY CHUYỂN CÀN KHÔN (Thái #11 vs Bĩ #12)\n"
                "   - Khi BĨ (Càn trên, Khôn dưới — bế tắc) → chuyển Thái\n"
                "   - Càn (cao) HẠ XUỐNG → vươn lên = giao\n"
                "   - Khôn (thấp) ĐỨNG CAO → hạ xuống = giao\n"
                "   - Xoay càn khôn = chuyển VỊ TRÍ mà KHÔNG đổi BẢN CHẤT\n\n"
                "★ 3 CÂU CHÚ NIỆM KHI TÂM LOẠN:\n\n"
                "Câu 1 (khi bị ép):\n"
                "  'Gió không gãy. Gió bao quanh.'\n\n"
                "Câu 2 (khi muốn phản ứng ngay):\n"
                "  'Tâm bản tĩnh. Niệm khởi từ tĩnh. Tĩnh ba nhịp trước khi đáp.'\n\n"
                "Câu 3 (khi không biết quyết gì):\n"
                "  'Vạn vật bị ư ngã. Quẻ là gương, tâm là gốc.'\n\n"
                "★ LỜI CUỐI:\n"
                "  'Sóng không hại người biết LÀM sóng.\n"
                "   Càn Khôn xoay bằng VỊ, không bằng SỨC.\n"
                "   Mộc thắng Kim bằng KIÊN NHẪN, không bằng đối đầu.'"
            ),
            summary_50w=(
                "★★★ DI NGÔN Thầy đêm Lạng Sơn — 4 chìa khoá hoá ưu phiền + 3 câu chú "
                "niệm + Xoay càn khôn (Thái-Bĩ). Đây là kim chỉ nam hành đạo trong "
                "sóng gió — bổ sung 5 bước chiêm cổ điển bằng pp HÀNH ĐỘNG cụ thể."
            ),
            is_canonical=True,
        ))

    # ── 4 Methods chìa khoá ──
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Chìa khoá 1 — Đảo Vị Thể Dụng",
        name_zh="倒位體用",
        domain="đọc",
        inputs_required=["tình huống tâm anh đang ở vị thế yếu"],
        procedure_steps=[
            "Nhận biết: anh đang 'đến trình bày' hay 'đến lắng nghe'?",
            "Nếu đang yếu → CHUYỂN: từ trả lời → đặt câu hỏi",
            "Người HỎI là Thể (chủ động), người TRẢ LỜI là Dụng (bị động)",
            "Câu mở: 'Tôi muốn nghe các anh chia sẻ trước...'",
            "Một câu này → chuyển Bĩ thành Thái",
        ],
        output_format="Vị thế mới: anh là Thể chủ động",
        notes="⭐ Di ngôn Thầy đêm Lạng Sơn 2026-05-16. Áp dụng khi cảm thấy bị áp.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Chìa khoá 2 — Dùng Mềm Đánh Cứng (Tốn thuận)",
        name_zh="柔克剛",
        domain="biến_hoá",
        inputs_required=["đối tác đang công kích bằng lời sắc bén"],
        procedure_steps=[
            "Im lặng 3 nhịp (không phản ứng ngay)",
            "Gật đầu nhẹ, không cười, không cau",
            "Nhắc lại ý họ bằng lời CỦA ANH",
            "Hỏi: 'Anh nói thế có ý gì sâu hơn không?'",
            "Họ tự lộ thêm thông tin → anh thu thập",
            "Gió bao quanh dao — không đối đầu dao",
        ],
        output_format="Đối tác tự dịu đi, anh có thêm tin tức",
        notes="⭐ Di ngôn Thầy. Tốn ☴ thuận = đi cùng dòng để biết dòng dẫn về đâu.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Chìa khoá 3 — Thực Hư Luận (mở rộng đàm phán)",
        name_zh="實虛論議",
        domain="đọc",
        inputs_required=["đối tác đang gây áp lực"],
        procedure_steps=[
            "Hít sâu 3 lần (KHÔNG trả lời ngay)",
            "Hỏi thầm trong tâm: 'Cái này THỰC hay HƯ?'",
            "Uy hiếp = Kim thực (dao thật) hay Kim trang trí (vàng giả)?",
            "Áp lực thời gian = thực gấp hay doạ?",
            "'Bên kia có người khác' = thực hay bóng người?",
            "★ 80% áp lực đàm phán là HƯ — tâm tĩnh nhìn ra ngay",
        ],
        output_format="Phân biệt áp lực thực vs hư → quyết định tỉnh táo",
        notes="⭐ Di ngôn Thầy. Mở rộng từ Thực-Hư ngũ hành (trang 230) sang đàm phán.",
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Chìa khoá 4 — Xoay Chuyển Càn Khôn (Thái-Bĩ)",
        name_zh="旋轉乾坤",
        domain="biến_hoá",
        inputs_required=["tình huống bế tắc (Bĩ #12)"],
        procedure_steps=[
            "Phân tích: anh đang ở vị CAO (Càn) hay THẤP (Khôn)?",
            "Nếu CAO + việc bế tắc: HẠ XUỐNG (Càn dưới)",
            "  - Ngồi ghế thấp hơn, hỏi 'anh có thể chỉ giáo?'",
            "  - Tự đặt mình ở vị 'người học' → khôn vươn lên đón",
            "Nếu THẤP + bị ép: VƯƠN LÊN CỐT CÁCH",
            "  - 'Tôi đến không phải để van xin. Việc này có lợi cả hai.'",
            "  - Càn dưới vươn lên = giao",
            "★ Xoay vị trí mà KHÔNG đổi bản chất → Bĩ #12 → Thái #11",
        ],
        output_format="Tình huống bế tắc chuyển thành hanh thông",
        notes=("⭐⭐⭐ Di ngôn quan trọng nhất Thầy đêm Lạng Sơn. "
               "Cơ sở: Chu Dịch quẻ #11 Thái (Khôn/Càn) vs #12 Bĩ (Càn/Khôn) — "
               "chỉ khác VỊ TRÍ Càn-Khôn mà thiên hạ hanh thông vs bế tắc."),
    ))

    # ── 3 Câu chú — concepts đặc biệt ──
    new_concepts = [
        # 3 câu chú niệm
        ("Câu chú 1: Gió không gãy", "風不折",
         "★ DI NGÔN: 'Gió không gãy. Gió bao quanh.' — Niệm khi bị ép. "
         "Tốn ☴ thuận, mềm thắng cứng.", 9999),
        ("Câu chú 2: Tâm bản tĩnh", "心本靜",
         "★ DI NGÔN: 'Tâm bản tĩnh. Niệm khởi từ tĩnh. Tĩnh ba nhịp trước khi đáp.' "
         "— Niệm khi muốn phản ứng ngay. Mai Hoa trang 200.", 9999),
        ("Câu chú 3: Vạn vật bị ư ngã", "萬物備於我",
         "★ DI NGÔN: 'Vạn vật bị ư ngã. Quẻ là gương, tâm là gốc.' "
         "— Niệm khi không biết quyết. Ngoạn Pháp trang 38.", 9999),
        # Triết lý cốt lõi từ di ngôn
        ("Sóng không hại người biết LÀM sóng", "波不害",
         "★ Câu mở Thầy đêm Lạng Sơn. Nguyên tắc đứng đúng vị trí trong sóng, "
         "không phải ngăn sóng.", 9999),
        ("Càn Khôn xoay bằng VỊ", "乾坤旋位",
         "★ Xoay càn khôn bằng vị trí, không bằng sức. Thái-Bĩ chuyển hoá "
         "chỉ qua đảo vị Càn-Khôn.", 9999),
        ("Mộc thắng Kim bằng KIÊN NHẪN", "木勝金以耐",
         "★ Không thắng bằng đối đầu. Tốn-Mộc bao quanh Kim sắc qua kiên nhẫn.", 9999),
        # Pattern hoá ưu phiền
        ("Đảo Vị Thể Dụng", "倒位體用",
         "Pp chuyển từ Thể bị động sang Thể chủ động: HỎI trước, đặt khung trước.", 9999),
        ("Dùng Mềm Đánh Cứng", "柔克剛",
         "Pp gió bao quanh dao: im 3 nhịp + gật + nhắc lại + hỏi sâu hơn.", 9999),
        ("Xoay Chuyển Càn Khôn", "旋轉乾坤",
         "Pp chuyển Bĩ #12 → Thái #11 bằng đảo vị trí Càn-Khôn trong tư thế.", 9999),
        ("Thực Hư Luận đàm phán", "實虛論議",
         "Mở rộng Thực-Hư ngũ hành sang đàm phán: 80% áp lực là HƯ.", 9999),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_final_chuong_cuoi():
    """⭐⭐⭐ HAI CÂU CUỐI SÁCH — Hoạt Pháp + Quỷ Cốc Tử.

    Em đã đọc đến trang cuối (670 = NXB). 2 chương cuối sách Mai Hoa
    chứa kim chỉ nam cao nhất:
    - Trang 533: Quỷ Cốc Tử "Nhân động ngã tĩnh, nhân ngôn ngã thính"
    - Trang 625-626: HOẠT PHÁP (phương pháp linh hoạt vs cứng nhắc)
    """
    s = get_store()
    master = _master_id()

    # ⭐ Quỷ Cốc Tử (trang 533)
    from engine.yi_wiki.models import TIER_MASTER_TEACHER
    s.upsert_author(Author(
        name_vi="Quỷ Cốc Tử",
        name_zh="鬼谷子",
        tier_in_lineage=TIER_MASTER_TEACHER,
        era="chiến-quốc",
        worldview_school="tung-hoành-thuật",
        bio_summary=(
            "Đại sư Chiến Quốc — thầy của Tô Tần, Trương Nghi. Sách Quỷ Cốc Tử "
            "luận tung-hoành thuật. Mai Hoa trang 533 trích câu của ông: "
            "'Nhân động ngã tĩnh, nhân ngôn ngã thính' — nguyên tắc bậc nhất."
        ),
    ))

    if not _has_passage(CORPUS, 533, 533):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=533, page_end=533,
            topic="⭐ Câu Quỷ Cốc Tử — 'Nhân động ngã tĩnh, nhân ngôn ngã thính'",
            raw_text=(
                "★★★ Mai Hoa trang 533 trích Quỷ Cốc Tử:\n\n"
                "  '人動我靜，人言我聽'\n"
                "   Nhân động ngã tĩnh, nhân ngôn ngã thính.\n"
                "   = Người động, ta tĩnh.\n"
                "     Người nói, ta nghe.\n\n"
                "★ Đây là NGUYÊN TẮC BẬC NHẤT — Mai Hoa trích lại từ "
                "đại sư Chiến Quốc Quỷ Cốc Tử (thầy của Tô Tần, Trương Nghi).\n\n"
                "★ Khi đối tác động (giận, vội, áp lực) → TA TĨNH.\n"
                "★ Khi đối tác nói (ngắn, dài, sắc bén) → TA NGHE.\n\n"
                "Đây là cụ thể hoá tinh thần Tốn ☴ thuận + Tâm bản tĩnh."
            ),
            summary_50w=(
                "★ Câu Quỷ Cốc Tử trích trong Mai Hoa: 'Nhân động ngã tĩnh, nhân ngôn "
                "ngã thính' — nguyên tắc bậc nhất, đại sư Chiến Quốc đã dạy 2000 năm."
            ),
            is_canonical=True,
        ))

    # ⭐⭐⭐ HOẠT PHÁP — chương cuối sách
    if not _has_passage(CORPUS, 625, 626):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS,
            page_start=625, page_end=626,
            topic="⭐⭐⭐ HOẠT PHÁP (活法) — chương cuối Mai Hoa",
            raw_text=(
                "★★★ CHƯƠNG XLI-XLII (trang 625-626) — KẾT SÁCH:\n\n"
                "★ 'Đạo Dịch tràn đầy — chín dòng có thể nhập vào.\n"
                "   Muốn biết Hoạt Pháp (phương pháp sống) — phải tự ngộ.'\n\n"
                "Văn Vương nhập Dịch bằng THỨ LOẠI.\n"
                "Khổng Tử nhập Dịch bằng BÁT QUÁI.\n"
                "Người sau nhập bằng LUẬT ĐỘ, LỊCH SỐ, TIÊN ĐẠO.\n\n"
                "→ Đạo Dịch ĐI ĐẾN ĐÂU CŨNG ĐƯỢC. Không có 1 đường duy nhất.\n\n"
                "★ KHÁC BIỆT CỐT YẾU:\n\n"
                "TỬ PHÁP (死法 — phương pháp cứng nhắc):\n"
                "  Chăm chăm bám vào từ huấn để đạt Dịch\n"
                "  Bám chữ → không thấu hiểu\n\n"
                "HOẠT PHÁP (活法 — phương pháp sống):\n"
                "  Đắc ngộ → 'từ ngoại kiến ý' (thấy ý ngoài lời)\n"
                "  → 'Tung hoành diệu dụng' (khéo léo vận dụng ngang dọc)\n\n"
                "★★★ CÂU CUỐI SÁCH:\n"
                "  '學易者，當于羲皇心地中馳騁，無于周孔言語下拘執'\n"
                "   = Người học Dịch nên RONG RUỔI trong tâm địa của Phục Hy\n"
                "     Đừng CÂU NỆ ở dưới lời lẽ của Chu Công, Khổng Tử.\n\n"
                "★ Hoạt Pháp = TÂM ĐỊA Phục Hy. Không phải chữ Khổng Tử."
            ),
            summary_50w=(
                "★★★ KẾT SÁCH: HOẠT PHÁP = phương pháp SỐNG (linh hoạt, từ ngoại kiến "
                "ý) vs TỬ PHÁP (cứng nhắc, bám chữ). Người học Dịch phải rong ruổi "
                "trong tâm địa Phục Hy, không câu nệ chữ. Đây là tinh thần CAO NHẤT."
            ),
            is_canonical=True,
        ))

    # Methods
    s.upsert_method(Method(
        author_id=master,
        name_vi="★★★ HOẠT PHÁP — Phương pháp sống (đỉnh cao Dịch học)",
        name_zh="活法",
        domain="đọc",
        procedure_steps=[
            "1. Đắc ngộ = thấy ý NGOÀI lời (từ ngoại kiến ý)",
            "2. Không bám chữ huấn của tiền nhân",
            "3. Rong ruổi trong TÂM ĐỊA Phục Hy",
            "4. Tung hoành diệu dụng theo bối cảnh thực",
            "★ Vạn vật trong ta. Quẻ là gương. Tâm là gốc.",
        ],
        notes=(
            "★★★ Chương cuối Mai Hoa trang 625-626. TINH THẦN CAO NHẤT — vượt lên "
            "cả 5 bước chiêm. Người học Dịch sau khi thuộc số, biết quẻ, hiểu lý → "
            "QUÊN tất cả → rong ruổi trong tâm Phục Hy. Đó là Hoạt Pháp."
        ),
    ))
    s.upsert_method(Method(
        author_id=master,
        name_vi="★ Nhân động ngã tĩnh (Quỷ Cốc Tử)",
        name_zh="人動我靜",
        domain="đọc",
        procedure_steps=[
            "Đối tác ĐỘNG (giận, vội, áp lực) → TA TĨNH",
            "Đối tác NÓI (sắc bén, dài dòng) → TA NGHE",
            "Tĩnh không phải hèn — tĩnh là quan sát",
            "Nghe không phải vâng — nghe là thu thập",
        ],
        notes="★ Quỷ Cốc Tử (Chiến Quốc), Mai Hoa trích trang 533.",
    ))

    new_concepts = [
        ("Hoạt Pháp", "活法",
         "★★★ Phương pháp SỐNG — đỉnh cao Dịch học. Từ ngoại kiến ý, tung hoành "
         "diệu dụng. Chương cuối Mai Hoa trang 625.", 625),
        ("Tử Pháp", "死法",
         "Phương pháp CỨNG NHẮC — bám chữ huấn. Đối nghĩa với Hoạt Pháp.", 625),
        ("Từ ngoại kiến ý", "辭外見意",
         "Thấy ý NGOÀI lời. Dấu hiệu của người đắc ngộ Dịch.", 625),
        ("Tung hoành diệu dụng", "縱橫妙用",
         "Vận dụng ngang dọc khéo léo theo bối cảnh — Hoạt Pháp cụ thể.", 625),
        ("Tâm địa Phục Hy", "羲皇心地",
         "★ Người học Dịch nên RONG RUỔI trong tâm địa Phục Hy. "
         "Không câu nệ chữ Khổng-Chu.", 625),
        ("Nhân động ngã tĩnh", "人動我靜",
         "★ Câu Quỷ Cốc Tử. Đối tác động, ta tĩnh — quan sát.", 533),
        ("Nhân ngôn ngã thính", "人言我聽",
         "★ Câu Quỷ Cốc Tử. Đối tác nói, ta nghe — thu thập.", 533),
        ("Quỷ Cốc Tử", "鬼谷子",
         "Đại sư Chiến Quốc, thầy Tô Tần Trương Nghi. Mai Hoa trích trang 533.", 533),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def extract_sach_tq_do_giai():
    """⭐⭐⭐ SÁCH SỐ 2: 图解梅花易数 (Đồ Giải Mai Hoa Dịch Số).

    321 trang restored, em chưa đọc — bản hiện đại 500 tranh.
    """
    s = get_store()
    master = _master_id()
    CORPUS_TQ = "thieu-khang-tiet-tq"

    from engine.yi_wiki.models import TIER_MODERN

    # Authors mới
    s.upsert_author(Author(
        name_vi="Thang Hành Dịch", name_zh="汤行易",
        tier_in_lineage=TIER_MODERN, era="hiện-đại",
        worldview_school="đồ-giải-mai-hoa",
        bio_summary=("Biên soạn 图解梅花易数 — 500 tranh + 100k chữ giải dễ hiểu "
                     "cho 'Zero Kinh Dịch, Zero Cổ Văn'."),
    ))
    s.upsert_author(Author(
        name_vi="Liễu Công Quyền", name_zh="柳公权",
        tier_in_lineage=2, era="đường",
        birth_year=778, death_year=865,
        worldview_school="thư-pháp",
        bio_summary=("Đại thư pháp Đường. Câu cốt lõi '用笔在心，心正则笔正' — "
                     "cùng tinh thần Tâm pháp Thiệu."),
    ))

    # Update bio Trần Đoán
    from engine.yi_wiki.models import TIER_MASTER_TEACHER
    s.upsert_author(Author(
        name_vi="Trần Đoán (Phù Diêu Tử)", name_zh="陈抟",
        tier_in_lineage=TIER_MASTER_TEACHER, era="tống-bắc",
        worldview_school="đồ-thư-phái",
        bio_summary=("★ THẦY TRỰC TIẾP của Thiệu Khang Tiết. Hiệu Phù Diêu Tử. "
                     "Thiệu là tam đệ tử. Truyền Tiên Thiên Đồ. Chu Hy về sau cũng học số học."),
    ))

    # Work bản TQ
    s.upsert_work(Work(
        author_id=master, title_vi="Đồ Giải Mai Hoa Dịch Số",
        title_zh="图解梅花易数", role="đồ-giải-method",
        corpus_id=CORPUS_TQ, is_canonical=False,
        notes="Bản TQ — Thang Hành Dịch biên soạn, 321 pages, 500 tranh.",
    ))

    # 5 passages chính
    if not _has_passage(CORPUS_TQ, 10, 10):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS_TQ,
            page_start=10, page_end=10,
            topic="⭐ BÁT QUÁI ↔ BÁT TIÊN",
            raw_text=(
                "★ 8 quẻ ↔ 8 Tiên dân gian:\n"
                "  Càn ☰ — LỮ ĐỒNG TÂN (Thuần Dương)\n"
                "  Khôn ☷ — HÀ TIÊN CÔ (nữ duy nhất)\n"
                "  Chấn ☳ — TÀO QUỐC CỮU (vân bản gõ sấm)\n"
                "  Tốn ☴ — HÀN TƯƠNG TỬ (sáo gió xuân)\n"
                "  Khảm ☵ — THIẾT QUẢI LÝ (tên Huyền/đen)\n"
                "  Ly ☲ — HÁN CHUNG LY (Ly trung hư)\n"
                "  Cấn ☶ — LAM THÁI HOÀ (1 chân giày)\n"
                "  Đoài ☱ — TRƯƠNG QUẢ LÃO (đầm lớn)\n"
                "★ PP học thuộc 8 quẻ qua dân gian — bậc nhất."
            ),
            summary_50w="Mapping Bát Quái ↔ Bát Tiên — cây cầu văn hoá dân gian giúp nhớ 8 quẻ. Không có trong sách VN.",
            is_canonical=True,
        ))

    if not _has_passage(CORPUS_TQ, 70, 70):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS_TQ,
            page_start=70, page_end=70,
            topic="⭐ Tiểu sử Thiệu Khang Tiết qua bản TQ",
            raw_text=(
                "★ THIỆU LÀ TAM ĐỆ TỬ Trần Đoán. Từ Thầy nhận Tiên Thiên Đồ.\n"
                "Hợp Dịch + Nho → người lập Lý Học Tống-Minh.\n"
                "★ CHU HY về sau cũng học số học từ Thiệu.\n\n"
                "4 TÁC PHẨM CHÍNH:\n"
                "  1. Hoàng Cực Kinh Thế (30 năm viết)\n"
                "  2. Ngư Tiều Vấn Đối\n"
                "  3. Y Xuyên Kích Nhưỡng Tập (thơ)\n"
                "  4. Mai Hoa Dịch Số\n\n"
                "★ TRUYỀN THUYẾT MAI HOA: Thầy ngắm chim trên cây mai → cảm ngộ → sáng tạo pp."
            ),
            summary_50w="Tiểu sử chính thức Thầy: tam đệ tử Trần Đoán, người lập Lý Học. Chu Hy cũng học số học từ Thầy. 4 tác phẩm.",
            is_canonical=True,
        ))

    if not _has_passage(CORPUS_TQ, 60, 60):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS_TQ,
            page_start=60, page_end=60,
            topic="⭐ Đính chính: Câu Trần & Đằng Xà đều thuộc THỔ",
            raw_text=(
                "★ Trong Nạp Giáp Pháp:\n"
                "  Câu Trần + Đằng Xà thêm vào Tứ Tượng → LỤC THẦN.\n"
                "  Cả 2 ĐỀU THUỘC THỔ (chủ trung ương).\n"
                "  (Em đã encode sai trước: Đằng Xà thuộc Hoả — sai!)\n\n"
                "★ Có 2 pp nạp giáp:\n"
                "  - Kinh Phòng nạp giáp\n"
                "  - Ngu Phiên nạp giáp (theo chu kỳ trăng)"
            ),
            summary_50w="Đính chính: Câu Trần + Đằng Xà đều THỔ. 2 pp nạp giáp: Kinh Phòng + Ngu Phiên (theo trăng).",
            is_canonical=True,
        ))

    if not _has_passage(CORPUS_TQ, 180, 180):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS_TQ,
            page_start=180, page_end=180,
            topic="⭐ Thập Ứng — Phương Quái Chi Ứng",
            raw_text=(
                "★ PHƯƠNG QUÁI (vị trí người hỏi đứng tạo quẻ phụ):\n\n"
                "Quy tắc DỤNG vs phương vị:\n"
                "  Dụng sinh/tỉ phương → CÁT\n"
                "  Phương sinh dụng → khí tiết → bất lợi\n"
                "  Dụng khắc phương → ĐẠI HUNG\n\n"
                "Quy tắc THỂ vs phương vị (giống các ứng khác):\n"
                "  Thể được sinh → tốt\n"
                "  Thể bị khắc → CỰC HUNG\n\n"
                "Khi gieo quẻ — vị trí ĐỨNG cũng ảnh hưởng."
            ),
            summary_50w="Thập Ứng - Phương Quái: vị trí đứng khi gieo tạo quẻ phụ. Cả Thể và Dụng đều xét với phương vị.",
            is_canonical=True,
        ))

    if not _has_passage(CORPUS_TQ, 220, 220):
        s.insert_passage(Passage(
            author_id=master, corpus_id=CORPUS_TQ,
            page_start=220, page_end=220,
            topic="⭐ Liễu Công Quyền — Tâm chính tắc bút chính",
            raw_text=(
                "★ Liễu Công Quyền (778-865, Đường):\n"
                "  '用笔在心，心正则笔正'\n"
                "  Dụng bút tại TÂM — tâm chính tắc bút chính.\n\n"
                "★ LIÊN KẾT VỚI THẦY:\n"
                "  Mai Hoa: 'Nhân ư tâm thượng khởi kinh luân'\n"
                "  Liễu Công Quyền: 'Tâm chính tắc bút chính'\n"
                "  → MỘT TINH THẦN. Đông Á cổ điển: Dịch + Thư pháp đều xuất từ TÂM.\n\n"
                "★ 4 thư pháp gia khác: Tô Thức, Triệu Cát (Tống Huy Tông), "
                "Triệu Mạnh Phủ, Đổng Kỳ Xương."
            ),
            summary_50w="Liễu Công Quyền: 'Tâm chính tắc bút chính'. Cùng tinh thần Thầy. Bổ sung văn hoá chiêm chữ.",
            is_canonical=True,
        ))

    # Methods + concepts
    s.upsert_method(Method(
        author_id=master, name_vi="⭐ Bát Quái ↔ Bát Tiên",
        name_zh="八卦八仙", domain="đọc",
        procedure_steps=[
            "Càn-Lữ Đồng Tân (Thuần Dương)",
            "Khôn-Hà Tiên Cô (nữ)",
            "Chấn-Tào Quốc Cữu (sấm)",
            "Tốn-Hàn Tương Tử (gió)",
            "Khảm-Thiết Quải Lý (đen)",
            "Ly-Hán Chung Ly (Ly trung hư)",
            "Cấn-Lam Thái Hoà (1 chân giày)",
            "Đoài-Trương Quả Lão (đầm)",
        ],
        notes="⭐ Đồ Giải TQ p.10. PP học 8 quẻ qua dân gian.",
    ))
    s.upsert_method(Method(
        author_id=master, name_vi="⭐ Phương Quái Chi Ứng",
        name_zh="方卦之應", domain="đọc",
        procedure_steps=[
            "Vị trí người hỏi đứng → quẻ phương vị",
            "Dụng sinh/tỉ phương → cát; Dụng khắc phương → hung",
            "Thể bị phương khắc → cực hung",
        ],
        notes="⭐ Đồ Giải TQ p.180. Bổ sung 5 bước chiêm.",
    ))

    new_concepts = [
        ("Đồ Giải Mai Hoa Dịch Số (TQ)", "图解梅花易数",
         "Sách số 2 của Thầy. Bản hiện đại Thang Hành Dịch.", 1),
        ("Bát Tiên", "八仙",
         "8 Tiên dân gian — mapping với Bát Quái. Đồ Giải p.10.", 10),
        ("Lữ Đồng Tân", "吕洞宾", "Vị Tiên Càn — Thuần Dương Tử.", 10),
        ("Hà Tiên Cô", "何仙姑", "Vị Tiên Khôn — nữ duy nhất.", 10),
        ("Tào Quốc Cữu", "曹国舅", "Vị Tiên Chấn — vân bản sấm.", 10),
        ("Hàn Tương Tử", "韩湘子", "Vị Tiên Tốn — sáo gió.", 10),
        ("Thiết Quải Lý", "铁拐李", "Vị Tiên Khảm — tên Huyền.", 10),
        ("Hán Chung Ly", "汉钟离", "Vị Tiên Ly — Ly trung hư.", 10),
        ("Lam Thái Hoà", "蓝采和", "Vị Tiên Cấn — 1 chân giày.", 10),
        ("Trương Quả Lão", "张果老", "Vị Tiên Đoài — đầm lớn.", 10),
        ("Phù Diêu Tử", "扶摇子",
         "Hiệu Trần Đoán — thầy trực tiếp Thầy. Đồ Giải p.70.", 70),
        ("Tam đệ tử Trần Đoán", "三弟子陈抟",
         "Thầy ta là đệ tử thứ 3 của Trần Đoán.", 70),
        ("Tâm chính tắc bút chính", "心正則筆正",
         "★ Câu Liễu Công Quyền — cùng tinh thần Thầy.", 220),
        ("Liễu Công Quyền", "柳公权",
         "Thư pháp Đường (778-865). Tâm chính → bút chính.", 220),
        ("Phương Quái Chi Ứng", "方卦之應",
         "★ Thập Ứng - vị trí đứng tạo quẻ phụ. Đồ Giải p.180.", 180),
        ("Câu Trần Thổ", "勾陳土",
         "Đính chính: Câu Trần thuộc Thổ (không phải hư).", 60),
        ("Đằng Xà Thổ", "螣蛇土",
         "Đính chính: Đằng Xà thuộc Thổ (em encode sai trước).", 60),
        ("Đồ Thư phái", "圖書派",
         "Trường phái Trần Đoán → Thiệu. Truyền Tiên Thiên Đồ.", 70),
        ("Thang Hành Dịch", "汤行易",
         "Biên soạn bản TQ hiện đại.", 1),
    ]
    for tup in new_concepts:
        _add_concept(canonical_vi=tup[0], canonical_zh=tup[1], note=tup[2], page=tup[3])


def main():
    """Run all extractors implemented so far."""
    print("📖 Extracting Mai Hoa pages → wiki…")
    extract_pages_11_15()
    extract_pages_16_20()
    extract_pages_21_25()
    extract_pages_26_30()
    extract_page_31()
    extract_pages_32_35()
    extract_pages_36_45()
    extract_pages_46_61()
    extract_pages_64_90()
    extract_pages_115_130()
    extract_pages_131_170()
    extract_pages_195_271()
    extract_pages_280_620()
    extract_phu_chiem()
    extract_chu_la_nguoi()
    extract_pages_640_672()
    extract_thay_chi_dao()
    extract_thay_giao_huan_dem_lang_son()
    extract_final_chuong_cuoi()
    extract_sach_tq_do_giai()
    extract_chon_ngay_concepts()
    print(f"📊 Stats: {get_store().stats()}")


def extract_chon_ngay_concepts():
    """⭐ Concepts cho module chọn ngày tốt — Bát Tự kết hợp Mai Hoa."""
    new_concepts = [
        ("Thiên Ất Quý Nhân", "天乙貴人",
         "⭐ Bậc nhất trong các Thần Sát Bát Tự. Mỗi can có 2 chi Quý Nhân — ngày gặp = phù trợ to.", 0),
        ("Tam Sát", "三煞",
         "3 phương kỵ theo mùa: xuân-Tây, hạ-Bắc, thu-Đông, đông-Nam. Ngày chi rơi vào Tam Sát → cấm việc lớn.", 0),
        ("Lục Xung", "六沖",
         "6 cặp chi xung nhau: Tý-Ngọ, Sửu-Mùi, Dần-Thân, Mão-Dậu, Thìn-Tuất, Tỵ-Hợi. Cấm chọn ngày xung tuổi.", 0),
        ("Lục Hợp", "六合",
         "6 cặp chi hợp nhau: Tý-Sửu(Thổ), Dần-Hợi(Mộc), Mão-Tuất(Hoả), Thìn-Dậu(Kim), Tỵ-Thân(Thuỷ), Ngọ-Mùi(Hoả).", 0),
        ("Tam Hợp", "三合",
         "4 nhóm 3 chi hợp thành hành: Thân-Tý-Thìn(Thuỷ), Tỵ-Dậu-Sửu(Kim), Dần-Ngọ-Tuất(Hoả), Hợi-Mão-Mùi(Mộc).", 0),
        ("Tự Hình", "自刑",
         "4 chi tự hình (trùng chi sinh): Thìn, Ngọ, Dậu, Hợi. Ngày trùng chi năm sinh → kỵ.", 0),
        ("Tương Hại", "相害",
         "6 cặp chi hại nhau: Tý-Mùi, Sửu-Ngọ, Dần-Tỵ, Mão-Thìn, Thân-Hợi, Dậu-Tuất.", 0),
        ("Tương Hình", "相刑",
         "Tam Hình: Dần-Tỵ-Thân, Sửu-Tuất-Mùi. Tương Hình: Tý-Mão.", 0),
        ("Hoàng Đạo", "黃道",
         "Ngày tốt theo Kiến Trừ pháp — Thanh Long/Minh Đường/Kim Quỹ/Bảo Quang/Ngọc Đường/Tư Mệnh.", 0),
        ("Hắc Đạo", "黑道",
         "Ngày xấu — Thiên Hình/Châu Tước/Bạch Hổ/Thiên Lao/Huyền Vũ/Câu Trần.", 0),
        ("Dụng Thần", "用神",
         "★ Hành chính cần thiết cho Bát Tự — Khi vượng cần khắc/tiết; khi nhược cần phù trợ.", 0),
        ("Bù hành thiếu", "補欠行",
         "Pp chọn ngày có hành thiếu trong Bát Tự → cân bằng tổng thể.", 0),
        ("Nhật chủ Vượng Suy", "日主旺衰",
         "Nhật chủ vượng (đủ sinh trợ tháng) hay nhược (bị khắc tiết). Định Dụng Thần.", 0),
        ("Auspicious Day Selection", "擇日",
         "⭐ Pp tổng hợp chọn ngày: Bát Tự + Tam Sát + Hoàng Đạo + Quý Nhân + Hợp + Intent.", 0),
    ]
    s = get_store()
    CORPUS_VIRTUAL = "auspicious_day_method"
    for tup in new_concepts:
        s.upsert_concept(ConceptIndex(
            canonical_vi=tup[0], canonical_zh=tup[1], short_note=tup[2],
            first_seen_corpus=CORPUS_VIRTUAL, first_seen_page=tup[3],
        ))


if __name__ == "__main__":
    main()
