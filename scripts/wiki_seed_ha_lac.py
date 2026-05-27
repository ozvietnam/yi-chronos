"""Seed Bát Tự Hà Lạc concepts into wiki.sqlite3.

Source: Học Năng, _Bát Tự Hà Lạc Lược Khảo_, Saigon 1974.

Bát Tự Hà Lạc = phái VN-specific (kết hợp Hà Đồ Lạc Thư + Tứ Trụ + Kinh Dịch).
Khác biệt với Tử Bình:
- Tử Bình: phân tích Tứ Trụ thành Thập Thần + Cách Cục + Dụng Thần
- Hà Lạc: chuyển Tứ Trụ → 2 quẻ Kinh Dịch (Tiên thiên + Hậu thiên) + 12 hào trajectory

Run: cd /Users/ozvietnamdesktop/Desktop/yi && .venv/bin/python3 scripts/wiki_seed_ha_lac.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "yi_wiki" / "wiki.sqlite3"
CORPUS_ID = "bat-tu-ha-lac-hoc-nang"
SCHOOL = "bat_tu_ha_lac"


CONCEPTS: list[tuple[str, str, list[str], str, str, int | None]] = [
    # ── Paradigm foundation ──────────────────────────────────────────────────
    ("Bát Tự Hà Lạc", "八字河洛", ["Hà Lạc Lý Số", "Tám Chữ Hà Lạc"],
     "Phái VN-specific kết hợp **Hà Đồ + Lạc Thư + Tứ Trụ + Kinh Dịch**. "
     "Khác Tử Bình ở chỗ chuyển Tứ Trụ → 2 quẻ Kinh Dịch (Tiên thiên + Hậu thiên) + "
     "12 hào trajectory ~ 84-90 năm cuộc đời. Sách gốc: Học Năng, _Bát Tự Hà Lạc Lược Khảo_, "
     "Saigon 1974. Cross-verified với truyền thừa Trần Đoàn (陈抟).",
     "paradigm", None),

    ("Tiên Thiên Quái", "先天卦", ["Tiên thiên hexagram", "Tiên thiên"],
     "Quẻ thứ NHẤT của Bát Tự Hà Lạc — **cốt tử mệnh** (gốc đời người). "
     "Lập từ Thiên số + Địa số rút gọn → 2 trigram qua bản đồ Lạc Thư. "
     "Phân bổ thượng/hạ theo giới tính × tuổi: Dương nam/Âm nữ → Thiên trên, Địa dưới. "
     "Tiên thiên quái không thay đổi — là MỆNH (cố kết).",
     "ha_lac_core", None),

    ("Hậu Thiên Quái", "後天卦", ["Hậu thiên hexagram", "Hậu thiên"],
     "Quẻ thứ HAI của Bát Tự Hà Lạc — **vận động dụng** (cách thức vận hành thực tế). "
     "Lập từ Tiên thiên quái + nguyên đường + chi giờ sinh. "
     "Hậu thiên là VẬN (lưu biến) — cách Anh ĐI QUA cuộc đời.",
     "ha_lac_core", None),

    ("Nguyên Đường", "元堂", ["nguyên đường hào", "moving line"],
     "Hào chủ chốt của 1 quẻ Hà Lạc — quyết định bằng chi giờ sinh. "
     "Hào nguyên đường là **giai đoạn quan trọng nhất** trong 6 hào của quẻ. "
     "Cũng dùng để derive Hậu thiên quái từ Tiên thiên quái: đảo hào nguyên đường → Hậu thiên.",
     "ha_lac_core", None),

    # ── Hà Đồ / Lạc Thư background ───────────────────────────────────────────
    ("Hà Đồ", "河圖", ["Ha Do", "He Tu", "diagram of the Yellow River"],
     "Bảng số ngọc cổ Trung Hoa, gắn liền truyền thuyết Phục Hy nhận đồ từ rồng "
     "trên sông Hoàng Hà. 10 số (1-10) chia thành sinh số (1-5) + thành số (6-10). "
     "Là gốc cho Bát Tự Hà Lạc — Thiên Can + Địa Chi quy về Hà Đồ.",
     "ha_lac_core", None),

    ("Lạc Thư", "洛書", ["Lac Thu", "Lo Shu", "Lo Shu Square"],
     "Bảng số ma phương 3x3 cổ Trung Hoa, gắn liền truyền thuyết Đại Vũ nhận thư từ rùa "
     "trên sông Lạc. 9 số (1-9) sắp xếp sao cho hàng-cột-chéo đều = 15. "
     "Mỗi số ứng 1 quái (1=Khảm, 2=Khôn, 3=Chấn, ..., 9=Ly). Là gốc lập trigram trong Hà Lạc.",
     "ha_lac_core", None),

    ("Sinh Số", "生數", [],
     "5 số đầu Hà Đồ: 1, 2, 3, 4, 5 — đại biểu cho khí 'sinh ra' của ngũ hành. "
     "1=Thủy, 2=Hỏa, 3=Mộc, 4=Kim, 5=Thổ.",
     "ha_lac_core", None),

    ("Thành Số", "成數", [],
     "5 số sau Hà Đồ: 6, 7, 8, 9, 10 — đại biểu cho khí 'thành tựu' của ngũ hành. "
     "6=Thủy thành, 7=Hỏa thành, 8=Mộc thành, 9=Kim thành, 10=Thổ thành. "
     "Mỗi sinh số + 5 = thành số tương ứng.",
     "ha_lac_core", None),

    ("Thiên Số", "天數", ["Pool of Heaven"],
     "Tổng số dương lấy từ Thiên Can + Địa Chi (sinh số nhỏ của chi) trong Tứ Trụ. "
     "Rút gọn (trừ 25 nếu > 25) → 1-9 (hoặc 5 trung cung). "
     "Mapping qua Lạc Thư → 1 trigram. Engine `number_pools.py`.",
     "ha_lac_core", None),

    ("Địa Số", "地數", ["Pool of Earth"],
     "Tổng số âm lấy từ Thiên Can + Địa Chi (thành số lớn của chi) trong Tứ Trụ. "
     "Rút gọn (trừ 30 nếu > 30) → 1-9 (hoặc 5). "
     "Mapping qua Lạc Thư → 1 trigram. Phối với Thiên số → 2 trigrams = 1 hexagram.",
     "ha_lac_core", None),

    # ── 12 hào trajectory ────────────────────────────────────────────────────
    ("Quỹ Đạo 12 Hào", "十二爻軌道", ["12-line trajectory", "decade trajectory"],
     "Cuộc đời chia thành 12 giai đoạn, mỗi giai đoạn = 1 hào (yao). "
     "6 hào đầu = Tiên thiên quái (cốt mệnh, đời đầu - giữa). "
     "6 hào sau = Hậu thiên quái (vận dụng, đời giữa - cuối). "
     "Yang yao = **9 năm**, Yin yao = **6 năm** → tổng 84-90 năm. "
     "Tên gọi tiếng Việt: 'Quỹ đạo đời người'.",
     "ha_lac_core", None),

    ("Hào Dương 9 Năm", "陽爻九年", [],
     "Hào yang (━━━━━━━) = 9 năm. Quy luật 9-6: dương trường, âm đoản.",
     "ha_lac_core", None),

    ("Hào Âm 6 Năm", "陰爻六年", [],
     "Hào yin (━━ ━━) = 6 năm. Cùng với hào dương 9 năm tạo quỹ đạo 84-90 năm chuẩn.",
     "ha_lac_core", None),

    # ── Tam Nguyên (3 cycles of 60 years) ────────────────────────────────────
    ("Tam Nguyên", "三元", ["Three Cycles", "Thượng/Trung/Hạ nguyên"],
     "3 chu kỳ 60 năm cộng lại = 180 năm. Thượng Nguyên (上元): 1864-1923. "
     "Trung Nguyên (中元): 1924-1983. Hạ Nguyên (下元): 1984-2043. "
     "Dùng để xác định nghiêm cẩn trung cung 5 (số 5 trong Lạc Thư) — "
     "tùy nguyên mà 5 quy về quái khác nhau.",
     "ha_lac_core", None),

    ("Trung Cung Năm", "中宮五", ["Five jì-gōng", "5 centre palace"],
     "Số 5 trong Lạc Thư — TRUNG CUNG, không có quái cố định. "
     "Truyền thống cổ chuẩn: tùy Tam Nguyên mà 5 → quái khác nhau. "
     "Truyền thống VN phổ thông (Học Năng): fallback Ly (yang) / Đoài (yin). "
     "Engine flag low-confidence khi gặp số 5.",
     "ha_lac_core", None),

    # ── Author + work ────────────────────────────────────────────────────────
    ("Học Năng", "学能", ["Hoc Nang"],
     "Tác giả VN của cuốn _Bát Tự Hà Lạc Lược Khảo_, Saigon 1974. "
     "Là source chính cho engine `engine/ha_lac/` trong YI-CHRONOS. "
     "Phái VN truyền thừa qua Học Năng kế thừa từ Trần Đoàn (Hi Di tiên sinh).",
     "author", None),

    # ── Comparison Tiên ↔ Hậu ────────────────────────────────────────────────
    ("Tiên-Hậu Tương Sinh", "先後相生", [],
     "Tiên thiên quái sinh Hậu thiên quái (theo ngũ hành thượng quái) → vận thuận tự nhiên, "
     "đời người trải qua hài hòa.",
     "ha_lac_pattern", None),

    ("Tiên-Hậu Tương Khắc", "先後相剋", [],
     "Tiên thiên quái khắc Hậu thiên quái → vận có khắc kỵ giữa cốt mệnh và cách vận hành. "
     "Cần ý thức điều chỉnh để hòa giải.",
     "ha_lac_pattern", None),

    ("Tiên-Hậu Trùng Lặp", "先後重複", [],
     "Tiên thiên = Hậu thiên (hai quẻ giống nhau) → cuộc đời thuần khí, "
     "đặc tính bẩm sinh và vận dụng cùng 1 hướng. Hiếm gặp.",
     "ha_lac_pattern", None),
]


def main() -> int:
    now = int(time.time())
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Add Học Năng author if not exists
    cur.execute("""
        INSERT OR IGNORE INTO authors (name_vi, name_zh, tier_in_lineage, era, worldview_school, bio_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Học Năng", "学能", 5, "hiện-đại", "bat_tu_ha_lac",
          "Tác giả VN của _Bát Tự Hà Lạc Lược Khảo_ (Saigon 1974). "
          "Truyền thừa phái Hà Lạc Lý Số VN.", now))
    hoc_nang_id = cur.execute(
        "SELECT author_id FROM authors WHERE name_vi='Học Năng'"
    ).fetchone()[0]

    # Add work
    cur.execute("""
        INSERT OR IGNORE INTO works (author_id, title_vi, title_zh, year_composed, role, corpus_id, is_canonical, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (hoc_nang_id, "Bát Tự Hà Lạc Lược Khảo", "八字河洛略考", 1974, "author",
          CORPUS_ID, 1,
          "Tài liệu gốc cho engine `engine/ha_lac/` trong YI-CHRONOS. "
          "608 trang, NXB Saigon 1974.", now))

    inserted = 0
    updated = 0
    for canonical_vi, canonical_zh, aliases, short_note, category, first_page in CONCEPTS:
        existing = cur.execute(
            "SELECT concept_id, corpora FROM concept_index WHERE canonical_vi=? AND canonical_zh=?",
            (canonical_vi, canonical_zh)
        ).fetchone()
        if existing:
            cid, old_corpora_json = existing
            try:
                old_corpora = json.loads(old_corpora_json) if old_corpora_json else []
            except json.JSONDecodeError:
                old_corpora = []
            if CORPUS_ID not in old_corpora:
                old_corpora.append(CORPUS_ID)
            cur.execute("""
                UPDATE concept_index
                SET corpora = ?,
                    short_note = CASE WHEN length(short_note) < length(?) THEN ? ELSE short_note END,
                    category = COALESCE(category, ?),
                    school = COALESCE(school, ?)
                WHERE concept_id=?
            """, (json.dumps(old_corpora, ensure_ascii=False), short_note, short_note,
                  category, SCHOOL, cid))
            updated += 1
        else:
            cur.execute("""
                INSERT INTO concept_index (canonical_vi, canonical_zh, aliases, short_note,
                                            first_seen_corpus, first_seen_page, category, corpora, school, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (canonical_vi, canonical_zh,
                  json.dumps(aliases, ensure_ascii=False),
                  short_note, CORPUS_ID, first_page, category,
                  json.dumps([CORPUS_ID], ensure_ascii=False),
                  SCHOOL, now))
            inserted += 1

    conn.commit()
    print(f"Inserted {inserted} new concepts, updated {updated} existing concepts.")
    print(f"Author Học Năng: id={hoc_nang_id}")

    total = cur.execute("SELECT COUNT(*) FROM concept_index").fetchone()[0]
    ha_lac_concepts = cur.execute(
        "SELECT COUNT(*) FROM concept_index WHERE school=?", (SCHOOL,)
    ).fetchone()[0]
    print(f"\nWiki total concepts: {total}")
    print(f"Bát Tự Hà Lạc school concepts: {ha_lac_concepts}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
