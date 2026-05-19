"""Seed Master + Tier-1..5 consultants + initial concept queue.

Idempotent — chạy nhiều lần ok (UPSERT by name_zh + tier).
"""
from __future__ import annotations

from engine.yi_wiki.models import (
    Author,
    ConceptIndex,
    Method,
    Work,
    TIER_MASTER,
    TIER_MASTER_TEACHER,
    TIER_DIRECT_DISCIPLE,
    TIER_CONTEMPORARY,
    TIER_MINH_THANH,
    TIER_MODERN,
)
from engine.yi_wiki.store import get_store


def seed_authors() -> dict[str, int]:
    """Seed lineage 5-tier. Return {name_zh: author_id} for cross-refs."""
    s = get_store()
    ids: dict[str, int] = {}

    # ── Tier 0: MASTER ────────────────────────────────────────────────────
    ids["邵雍"] = s.upsert_author(Author(
        name_vi="Thiệu Ung (Khang Tiết)",
        name_zh="邵雍",
        tier_in_lineage=TIER_MASTER,
        era="tống-bắc",
        birth_year=1011, death_year=1077,
        worldview_school="tiên-thiên-tâm-pháp",
        foundational_axioms=[
            "Tâm là gốc, Số là biểu hiện",
            "Quan vật ngoại → vật nội ↔ tâm",
            "Tiên Thiên Đồ làm tâm pháp",
        ],
        hermeneutic_style="Quan vật ngoại → vật nội ↔ tâm",
        bio_summary=(
            "Đại dịch học, đại triết gia Bắc Tống. Cùng thời Phú Bật, Tư Mã Quang, "
            "Nhị Trình. Tổ tổ của khoa Mai Hoa Dịch Số. Để lại 5+ tác phẩm."
        ),
    ))

    # ── Tier 1: Thầy ──────────────────────────────────────────────────────
    ids["李之才"] = s.upsert_author(Author(
        name_vi="Lý Chi Tài",
        name_zh="李之才",
        tier_in_lineage=TIER_MASTER_TEACHER,
        era="tống-bắc",
        worldview_school="đồ-thư-phái",
        bio_summary="Thầy của Thiệu Ung. Đồ Thư phái — truyền Tiên Thiên Đồ.",
    ))

    # ── Tier 2: Đệ tử trực tiếp ───────────────────────────────────────────
    ids["邵伯溫"] = s.upsert_author(Author(
        name_vi="Thiệu Bá Ôn",
        name_zh="邵伯溫",
        tier_in_lineage=TIER_DIRECT_DISCIPLE,
        era="tống-bắc",
        bio_summary="Con trai Thiệu Ung. Bổ chú Hoàng Cực Kinh Thế.",
    ))
    ids["張行成"] = s.upsert_author(Author(
        name_vi="Trương Hành Thành",
        name_zh="張行成",
        tier_in_lineage=TIER_DIRECT_DISCIPLE,
        era="tống-nam",
        bio_summary="Kế thừa Hoàng Cực Kinh Thế thời Nam Tống.",
    ))

    # ── Tier 3: Cùng thời / kế thừa rẽ nhánh ──────────────────────────────
    ids["朱熹"] = s.upsert_author(Author(
        name_vi="Chu Hy",
        name_zh="朱熹",
        tier_in_lineage=TIER_CONTEMPORARY,
        era="tống-nam",
        birth_year=1130, death_year=1200,
        worldview_school="lý-học",
        bio_summary="Đại nho. Đặt Tiên Thiên Đồ vào Chu Dịch Bản Nghĩa.",
    ))
    ids["程頤"] = s.upsert_author(Author(
        name_vi="Trình Di (Y Xuyên)",
        name_zh="程頤",
        tier_in_lineage=TIER_CONTEMPORARY,
        era="tống-bắc",
        birth_year=1033, death_year=1107,
        worldview_school="lý-học",
        bio_summary="Nhị Trình. Bạn cùng thời Thiệu Ung. 1206 mentions trong Kinh Dịch VN.",
    ))
    ids["程顥"] = s.upsert_author(Author(
        name_vi="Trình Hạo (Minh Đạo)",
        name_zh="程顥",
        tier_in_lineage=TIER_CONTEMPORARY,
        era="tống-bắc",
        birth_year=1032, death_year=1085,
        worldview_school="lý-học",
        bio_summary="Nhị Trình anh. Bạn cùng thời Thiệu Ung.",
    ))
    ids["蔡元定"] = s.upsert_author(Author(
        name_vi="Sai Nguyên Định",
        name_zh="蔡元定",
        tier_in_lineage=TIER_CONTEMPORARY,
        era="tống-nam",
        bio_summary="Đệ tử Chu Hy.",
    ))

    # ── Tier 4: Truyền thừa Minh-Thanh ────────────────────────────────────
    ids["來知德"] = s.upsert_author(Author(
        name_vi="Lai Tri Đức",
        name_zh="來知德",
        tier_in_lineage=TIER_MINH_THANH,
        era="minh",
        bio_summary="Mai Hoa Tân pháp đời Minh.",
    ))

    # ── Tier 5: Hiện đại + dịch giả ───────────────────────────────────────
    ids["邵伟华"] = s.upsert_author(Author(
        name_vi="Thiệu Vĩ Hoa",
        name_zh="邵伟华",
        tier_in_lineage=TIER_MODERN,
        era="hiện-đại",
        birth_year=1936,
        bio_summary="Phục hưng Mai Hoa & Tự Bình hiện đại TQ. Có 2 sách trong thư viện.",
    ))
    ids["NGO_TAT_TO"] = s.upsert_author(Author(
        name_vi="Ngô Tất Tố",
        name_zh="",
        tier_in_lineage=TIER_MODERN,
        era="hiện-đại",
        worldview_school="dịch-giả-vn",
        bio_summary="Dịch giả Kinh Dịch Trọn Bộ — bridge ngữ VN.",
    ))
    ids["ONG_VAN_TUNG"] = s.upsert_author(Author(
        name_vi="Ông Văn Tùng",
        name_zh="",
        tier_in_lineage=TIER_MODERN,
        era="hiện-đại",
        worldview_school="dịch-giả-vn",
        bio_summary="Dịch giả Mai Hoa Dịch Số VN (NXB Văn Hóa Thông Tin, 1995).",
    ))
    ids["PHUONG_LUU"] = s.upsert_author(Author(
        name_vi="Phương Lưu",
        name_zh="",
        tier_in_lineage=TIER_MODERN,
        era="hiện-đại",
        worldview_school="học-giả-vn",
        bio_summary="GS-TS, viết lời tựa bản VN Mai Hoa Dịch Số (10/10/1994).",
    ))

    return ids


def seed_works(author_ids: dict[str, int]) -> dict[str, int]:
    """Seed 5 tác phẩm chính của Thiệu Ung."""
    s = get_store()
    master = author_ids["邵雍"]
    works: dict[str, int] = {}

    works["梅花易數"] = s.upsert_work(Work(
        author_id=master,
        title_vi="Mai Hoa Dịch Số",
        title_zh="梅花易數",
        role="method",
        corpus_id="mai-hoa-dich-so-thieu-khang-tiet",
        is_canonical=True,
        notes="Đại kỳ thư thứ 2 sau Chu Dịch. 5 quyển. Đã restored 672/672 trang.",
    ))
    works["皇極經世"] = s.upsert_work(Work(
        author_id=master,
        title_vi="Hoàng Cực Kinh Thế",
        title_zh="皇極經世",
        role="cosmology",
        corpus_id=None,
        is_canonical=True,
        notes="CHỜ ANH TÌM. Cosmology + chu kỳ vũ trụ.",
    ))
    works["觀物內外篇"] = s.upsert_work(Work(
        author_id=master,
        title_vi="Quan Vật Nội Ngoại Thiên",
        title_zh="觀物內外篇",
        role="philosophy",
        corpus_id=None,
        is_canonical=True,
        notes="CHỜ ANH TÌM. Triết học quan vật.",
    ))
    works["伊川擊壤集"] = s.upsert_work(Work(
        author_id=master,
        title_vi="Y Xuyên Kích Nhưỡng Tập",
        title_zh="伊川擊壤集",
        role="poetry",
        corpus_id=None,
        notes="Thơ ngộ đạo của Thiệu.",
    ))
    works["先天圖傳"] = s.upsert_work(Work(
        author_id=master,
        title_vi="Tiên Thiên Đồ Truyện",
        title_zh="先天圖傳",
        role="diagrams",
        corpus_id=None,
        notes="Diagrams Tiên Thiên.",
    ))
    return works


def seed_concept_queue(author_ids: dict[str, int]):
    """Seed concept queue từ trang 1-10 đã đọc. Anchor first_seen."""
    s = get_store()
    CORPUS = "mai-hoa-dich-so-thieu-khang-tiet"

    concepts = [
        # Cosmology / trường phái
        dict(canonical_vi="Tiên Thiên Tâm Pháp", canonical_zh="先天心法",
             short_note="Worldview Thiệu Ung — tâm pháp dựa trên Tiên Thiên Đồ.",
             first_seen_page=5),
        dict(canonical_vi="Bắc Tống", canonical_zh="北宋",
             short_note="Triều đại 960-1127. Bối cảnh Thiệu Ung.",
             first_seen_page=5),
        # Tam đại kỳ thư
        dict(canonical_vi="Chu Dịch", canonical_zh="周易",
             aliases=["Kinh Dịch"],
             short_note="Đại kỳ thư thứ 1. Đã có trong thư viện (Ngô Tất Tố dịch).",
             first_seen_page=5),
        dict(canonical_vi="Ma Y tướng thuật", canonical_zh="麻衣相術",
             short_note="Đại kỳ thư thứ 3, Ma Y đạo giả. CHƯA có trong thư viện.",
             first_seen_page=5),
        # Trang 7-8: Method trụ cột Quyển 3
        dict(canonical_vi="Thể Dụng", canonical_zh="體用",
             short_note="Trụ cột Mai Hoa — Thể là gốc, Dụng là biểu hiện.",
             first_seen_page=7),
        dict(canonical_vi="Thể dụng hỗ biến chi quyết", canonical_zh="體用互變之訣",
             short_note="Pp biến hoá quẻ qua Thể-Dụng. Quyển 3.",
             first_seen_page=8),
        dict(canonical_vi="Thể dụng sinh khắc chi quyết", canonical_zh="體用生剋之訣",
             short_note="Pp sinh khắc Thể-Dụng. Quyển 3.",
             first_seen_page=8),
        dict(canonical_vi="Thể dụng suy vượng chi quyết", canonical_zh="體用衰旺之訣",
             short_note="Pp suy vượng Thể-Dụng. Quyển 3.",
             first_seen_page=8),
        dict(canonical_vi="Chiêm bốc khắc ứng chi quyết", canonical_zh="占卜剋應之訣",
             short_note="Pp khắc ứng (predictive correspondence). Quyển 3.",
             first_seen_page=8),
        # Method bói
        dict(canonical_vi="Quan mai chiêm quyết", canonical_zh="觀梅占訣",
             short_note="Pp gốc đặt tên sách. Quyển 3.",
             first_seen_page=8),
        dict(canonical_vi="Chiêm bốc huyền cơ", canonical_zh="占卜玄機",
             short_note="Quyển 2 mở đầu — cơ chế bói.",
             first_seen_page=7),
        # Concept trừu tượng Q4-5
        dict(canonical_vi="Tướng tự tâm", canonical_zh="相自心",
             short_note="\"Tướng từ tâm\" — Quyển 4. ⭐ Liên quan động tâm.",
             first_seen_page=8),
        dict(canonical_vi="Dịch lý huyền vi", canonical_zh="易理玄微",
             short_note="Quyển 5.", first_seen_page=8),
        dict(canonical_vi="Cách vật chương", canonical_zh="格物章",
             short_note="Quyển 5.", first_seen_page=8),
        dict(canonical_vi="Vật lý luận", canonical_zh="物理論",
             short_note="Quyển 5.", first_seen_page=8),
        dict(canonical_vi="Bát quái biện", canonical_zh="八卦辨",
             short_note="Quyển 5.", first_seen_page=8),
        dict(canonical_vi="Lục thân", canonical_zh="六親",
             short_note="6 mối quan hệ — Quyển 5.", first_seen_page=8),
        # Q1 - foundational
        dict(canonical_vi="Bát quái tượng lệ", canonical_zh="八卦象例",
             short_note="Quyển 1 — quy tắc tượng của 8 quẻ.",
             first_seen_page=7),
        dict(canonical_vi="Ngũ hành sinh khắc", canonical_zh="五行生剋",
             short_note="Quyển 1 — pp sinh khắc 5 hành.",
             first_seen_page=7),
        dict(canonical_vi="Bát cung sở thuộc", canonical_zh="八宮所屬",
             short_note="Quyển 1 — quẻ thuộc cung nào.",
             first_seen_page=7),
        dict(canonical_vi="Quái khí suy", canonical_zh="卦氣衰",
             short_note="Quyển 1 — suy vượng quái khí.",
             first_seen_page=7),
        dict(canonical_vi="Thập thiên can", canonical_zh="十天干",
             short_note="Quyển 1 — 10 thiên can.",
             first_seen_page=7),
        dict(canonical_vi="Thập nhị địa chi", canonical_zh="十二地支",
             short_note="Quyển 1 — 12 địa chi.",
             first_seen_page=7),
        dict(canonical_vi="Chiêm pháp", canonical_zh="占法",
             short_note="Quyển 1 — pp bói gốc.",
             first_seen_page=7),
        dict(canonical_vi="Ngoạn pháp", canonical_zh="玩法",
             short_note="Quyển 1 — pp \"ngoạn\" (đọc).",
             first_seen_page=7),
        # Tài liệu khác
        dict(canonical_vi="Almanach Những nền văn minh thế giới",
             canonical_zh="",
             short_note="NXB VHTT 1977 — trích dẫn đánh giá bản dịch Ông Văn Tùng.",
             first_seen_page=10),
    ]

    cids: dict[str, int] = {}
    for c in concepts:
        cid = s.upsert_concept(ConceptIndex(
            canonical_vi=c["canonical_vi"],
            canonical_zh=c.get("canonical_zh", ""),
            aliases=c.get("aliases", []),
            short_note=c.get("short_note", ""),
            first_seen_corpus=CORPUS,
            first_seen_page=c["first_seen_page"],
        ))
        cids[c["canonical_vi"]] = cid
    return cids


def seed_methods(author_ids: dict[str, int]):
    """Seed các Method placeholder từ TOC — body sẽ extract khi đọc đến."""
    s = get_store()
    master = author_ids["邵雍"]
    methods: dict[str, int] = {}

    method_specs = [
        # Quyển 3 trụ cột
        ("Thể dụng hỗ biến chi quyết", "體用互變之訣", "biến_hoá"),
        ("Thể dụng sinh khắc chi quyết", "體用生剋之訣", "đọc"),
        ("Thể dụng suy vượng chi quyết", "體用衰旺之訣", "đọc"),
        ("Chiêm bốc khắc ứng chi quyết", "占卜剋應之訣", "ứng_kỳ"),
        ("Quan mai chiêm quyết", "觀梅占訣", "bốc"),
        # Quyển 1
        ("Chiêm pháp", "占法", "bốc"),
        ("Ngoạn pháp", "玩法", "đọc"),
    ]
    for name_vi, name_zh, domain in method_specs:
        mid = s.upsert_method(Method(
            author_id=master,
            name_vi=name_vi,
            name_zh=name_zh,
            domain=domain,
            notes="PLACEHOLDER — body sẽ extract khi đọc đến quyển tương ứng.",
        ))
        methods[name_zh] = mid
    return methods


def main():
    print("🌌 Seeding YI-Wiki Master-Apprentice…")
    aids = seed_authors()
    print(f"  ✅ Authors: {len(aids)}")
    wids = seed_works(aids)
    print(f"  ✅ Works:   {len(wids)}")
    cids = seed_concept_queue(aids)
    print(f"  ✅ Concepts queued: {len(cids)}")
    mids = seed_methods(aids)
    print(f"  ✅ Methods (placeholder): {len(mids)}")

    from engine.yi_wiki.store import get_store
    print(f"\n📊 Stats: {get_store().stats()}")


if __name__ == "__main__":
    main()
