"""Seed Thần Số Học (Numerology) authors + concepts vào wiki.sqlite3.

Nguồn: Pythagoras (gốc), Cheiro (Chaldean), Hans Decoz (chuẩn tính hiện đại),
Juno Jordan (California School). Xem data/than_so/master/sources_catalog.json.

Paradigm: đọc đồng dạng (Iron Rule #4/#6) — "Vạn vật là số", KHÔNG predict.
Idempotent: chạy lại nhiều lần an toàn (INSERT OR IGNORE / merge corpora).

Run: python3 scripts/wiki_seed_than_so.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

# Bảo đảm schema tồn tại (DB có thể chưa được tạo trong môi trường mới).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.yi_wiki.store import WikiStore  # noqa: E402

DB = Path(__file__).resolve().parent.parent / "data" / "yi_wiki" / "wiki.sqlite3"
CORPUS_ID = "than-so-pythagoras"
SCHOOL = "than_so_hoc"

# ─── Authors (tier_in_lineage: 1=gốc … 5=hiện đại) ───────────────────────────
AUTHORS: list[dict] = [
    {
        "name_vi": "Pythagoras", "name_zh": "", "tier": 1, "era": "hy-lạp-cổ",
        "birth_year": -570, "death_year": -495,
        "axioms": ["Vạn vật là số (All is number).", "Vũ trụ vận hành theo tỉ lệ + hòa âm số."],
        "bio": "Triết gia-toán học Hy Lạp cổ. Nền của numerology phương Tây. "
               "Không để lại trước tác trực tiếp — tư tưởng truyền qua trường phái.",
    },
    {
        "name_vi": "Cheiro (Louis Hamon)", "name_zh": "", "tier": 2, "era": "cận-đại",
        "birth_year": 1866, "death_year": 1936,
        "axioms": ["Số 9 linh thiêng, không gán chữ.", "Coi trọng số kép (compound) trước rút gọn."],
        "bio": "Nhà chiêm số nổi tiếng, đặt nền hệ Chaldean hiện đại qua 'Cheiro's Book of Numbers' (1926).",
    },
    {
        "name_vi": "L. Dow Balliett", "name_zh": "", "tier": 2, "era": "cận-đại",
        "birth_year": 1847, "death_year": 1929,
        "axioms": ["Số = Màu = Âm: ba biểu hiện một lực (rung động).", "11 và 22 là số chủ, không rút gọn."],
        "bio": "'Tổ mẫu Numerology hiện đại' (Atlantic City, ~1908). Provenance của bảng Pythagoras, "
               "phân biệt birth/name number, nguyên âm=linh hồn. Public domain.",
    },
    {
        "name_vi": "Florence Campbell", "name_zh": "", "tier": 4, "era": "hiện-đại",
        "birth_year": None, "death_year": 1964,
        "axioms": ["Inclusion Table: đếm tần suất số 1-9 trong tên.", "Số thiếu = Karmic Lessons."],
        "bio": "Tác giả 'Your Days Are Numbered' (1931) — giáo trình numerology hiện đại đầy đủ đầu tiên.",
    },
    {
        "name_vi": "Juno Jordan", "name_zh": "", "tier": 4, "era": "hiện-đại",
        "birth_year": 1884, "death_year": 1984,
        "axioms": ["Hệ thống hóa California School of Numerology."],
        "bio": "Tác giả 'Numerology: The Romance in Your Name' (1965) — kinh điển hệ Pythagorean.",
    },
    {
        "name_vi": "Hans Decoz", "name_zh": "", "tier": 5, "era": "đương-đại",
        "birth_year": 1949, "death_year": None,
        "axioms": ["Chuẩn hóa cách tính Life Path/Pinnacle số hóa (Decoz Chartmaker)."],
        "bio": "Tác giả 'Numerology: Key To Your Inner Self' + worldnumerology.com. "
               "Công thức trong engine YI-Chronos theo chuẩn Decoz.",
    },
]

# ─── Concepts: (vi, zh/en, aliases, short_note, category, page) ───────────────
CONCEPTS: list[tuple[str, str, list[str], str, str, int | None]] = [
    ("Thần Số Học", "Numerology", ["số học", "numerology"],
     "Môn đọc cấu trúc người qua TÊN + NGÀY SINH bằng các con số. Phái chính: Pythagoras "
     "(1-9 tuần tự) + Chaldean (1-8, số 9 linh thiêng). Paradigm đồng dạng: 'Vạn vật là số' — "
     "số phản chiếu cấu trúc tâm-thiên-thân, KHÔNG bói tốt/xấu.", "paradigm", None),
    ("Số Đường Đời", "Life Path", ["số chủ đạo", "life path"],
     "Số QUAN TRỌNG NHẤT, tính từ toàn bộ ngày sinh (rút gọn riêng ngày/tháng/năm rồi cộng — "
     "chuẩn Decoz). Phản chiếu con đường + mục đích sống mời ta quan-sát.", "core_number", None),
    ("Số Sứ Mệnh", "Expression", ["destiny number", "số vận mệnh"],
     "Tính từ TẤT CẢ chữ cái trong tên đầy đủ. Tài năng thiên bẩm + hướng thể hiện.", "core_number", None),
    ("Số Linh Hồn", "Soul Urge", ["heart's desire", "số khát vọng"],
     "Tính từ NGUYÊN ÂM trong tên. Khát vọng nội tâm + động lực sâu.", "core_number", None),
    ("Số Nhân Cách", "Personality", ["personality number"],
     "Tính từ PHỤ ÂM trong tên. Ấn tượng bên ngoài, cách người khác nhìn vào.", "core_number", None),
    ("Số Trưởng Thành", "Maturity", ["realization number"],
     "= Số Đường Đời + Số Sứ Mệnh. Mục tiêu hợp nhất lộ rõ nửa sau đời.", "core_number", None),
    ("Số Chủ", "Master Numbers", ["11", "22", "33"],
     "11/22/33 — KHÔNG rút gọn. Tiềm năng cao + thử thách cao. 11 trực giác/khải thị, "
     "22 kiến tạo vĩ đại, 33 đạo sư chữa lành.", "master_number", None),
    ("Số Nợ Nghiệp", "Karmic Debt", ["13", "14", "16", "19"],
     "13/14/16/19 — vùng cấu trúc mất cân bằng cần rèn trong đời này. KHÔNG phải án phạt tiền kiếp.",
     "karmic", None),
    ("Đỉnh Vận", "Pinnacle", ["pinnacle cycles"],
     "4 giai đoạn lớn của đời (P1=M+D, P2=D+Y, P3=P1+P2, P4=M+Y). Lớp BIẾN — tương ứng Đại Vận.",
     "cycle", None),
    ("Năm Cá Nhân", "Personal Year", ["personal year"],
     "Nhịp 9 năm: tháng+ngày sinh + năm hiện tại. Tương ứng Lưu Niên — đọc 'khí giai đoạn', không predict.",
     "cycle", None),
    ("Bảng Pythagoras", "Pythagorean Chart", ["A=1..I=9"],
     "Gán chữ cái → số 1-9 tuần tự (A=1, B=2…I=9, J=1…). Bản địa hóa tiếng Việt: bỏ dấu, Đ→D, "
     "không tách ghép phụ âm.", "method", None),
    ("Bảng Chaldean", "Chaldean Chart", ["sound vibration"],
     "Gán chữ cái → số 1-8 theo rung động âm thanh; số 9 linh thiêng không gán. Dùng đối chiếu chéo.",
     "method", None),
    ("Số Kép", "Compound Numbers", ["compound", "số kép Chaldean"],
     "Cheiro: số đơn 1-9 thuộc mặt VẬT CHẤT, số kép từ 10 trở lên thuộc mặt HUYỀN/TINH THẦN. "
     "Chaldean giữ số kép TRƯỚC khi rút gọn (mang lớp nghĩa riêng). Data: chaldean_compound_numbers.json.",
     "compound_number", None),
    ("Bánh Xe Số Phận", "Wheel of Fortune (10)", ["số 10"],
     "Số kép 10 (Cheiro): danh dự, niềm tin, tự tin; thăng-trầm; tên tuổi được biết đến; kế hoạch dễ thành.",
     "compound_number", None),
    ("Tháp Bị Sét Đánh", "Tower Struck by Lightning (16)", ["số 16", "Shattered Citadel"],
     "Số kép 16 (Cheiro): cảnh báo định mệnh lạ, tai nạn, kế hoạch sụp. Đọc đồng dạng: sắc thái cấu trúc cần quan-sát, không phán cứng.",
     "compound_number", None),
    ("Ngôi Sao Của Pháp Sư", "Star of the Magi (17)", ["số 17"],
     "Số kép 17 (Cheiro): số tâm linh cao — Bình an & Tình yêu (sao 8 cánh Venus); vượt lên thử thách; tên tuổi bất tử.",
     "compound_number", None),
    ("Vương Tinh Của Sư Tử", "Royal Star of the Lion (23)", ["số 23"],
     "Số kép 23 (Cheiro): thành công, được cấp trên giúp + người quyền cao che chở. Một trong các số may nhất.",
     "compound_number", None),
    ("Vương Trượng", "The Sceptre (27)", ["số 27"],
     "Số kép 27 (Cheiro): quyền uy, sức mạnh, phần thưởng từ trí tuệ sáng tạo; nên tự thực thi ý tưởng của mình.",
     "compound_number", None),
    ("Rung Động", "Vibration", ["vibration", "số-màu-âm"],
     "Lý thuyết nền của Balliett (~1908): Số - Màu - Âm là ba biểu hiện của CÙNG một lực. "
     "Mỗi chữ cái có rung động + màu + âm riêng. Phát biểu phương Tây của paradigm đồng dạng (Iron Rule #4/#6).",
     "paradigm", None),
    ("Bảng Bao Hàm", "Inclusion Table", ["inclusion chart"],
     "Đếm mỗi chữ-số 1-9 xuất hiện bao nhiêu lần trong tên đầy đủ (Florence Campbell, 1931). "
     "Số trội = Hidden Passion; số thiếu = Karmic Lessons.",
     "method", None),
    ("Bài Học Nghiệp", "Karmic Lessons", ["số thiếu", "karmic lessons"],
     "Các số 1-9 KHÔNG xuất hiện trong tên = phẩm chất còn khuyết, cần rèn trong đời này (Campbell). "
     "Khác Karmic Debt 13/14/16/19. Paradigm: vùng cấu trúc cần quan-sát, KHÔNG dọa nghiệp báo.",
     "karmic", None),
]


def main() -> int:
    WikiStore(DB)  # đảm bảo schema (CREATE TABLE IF NOT EXISTS)
    now = int(time.time())
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 1) Authors
    author_ids: dict[str, int] = {}
    for a in AUTHORS:
        cur.execute(
            """INSERT OR IGNORE INTO authors
               (name_vi, name_zh, tier_in_lineage, era, birth_year, death_year,
                worldview_school, foundational_axioms, bio_summary, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (a["name_vi"], a["name_zh"], a["tier"], a["era"], a["birth_year"], a["death_year"],
             SCHOOL, json.dumps(a["axioms"], ensure_ascii=False), a["bio"], now),
        )
        row = cur.execute(
            "SELECT author_id FROM authors WHERE name_vi=? AND tier_in_lineage=?",
            (a["name_vi"], a["tier"]),
        ).fetchone()
        author_ids[a["name_vi"]] = row[0]

    # 2) Work canonical (Cheiro's Book of Numbers — public domain, nền Chaldean)
    cur.execute(
        """INSERT OR IGNORE INTO works
           (author_id, title_vi, title_zh, year_composed, role, corpus_id, is_canonical, notes, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (author_ids["Cheiro (Louis Hamon)"], "Cheiro's Book of Numbers", "", 1926, "author",
         CORPUS_ID, 1, "Nền hệ Chaldean. Public domain — ưu tiên tìm bản gốc (sources_catalog).", now),
    )

    # 3) Concepts (merge corpora nếu đã tồn tại)
    inserted = updated = 0
    for vi, zh, aliases, note, category, page in CONCEPTS:
        existing = cur.execute(
            "SELECT concept_id, corpora FROM concept_index WHERE canonical_vi=? AND canonical_zh=?",
            (vi, zh),
        ).fetchone()
        if existing:
            cid, old_json = existing
            corpora = json.loads(old_json) if old_json else []
            if CORPUS_ID not in corpora:
                corpora.append(CORPUS_ID)
            cur.execute(
                """UPDATE concept_index SET corpora=?,
                       short_note=CASE WHEN length(short_note)<length(?) THEN ? ELSE short_note END,
                       category=COALESCE(category,?), school=COALESCE(school,?) WHERE concept_id=?""",
                (json.dumps(corpora, ensure_ascii=False), note, note, category, SCHOOL, cid),
            )
            updated += 1
        else:
            cur.execute(
                """INSERT INTO concept_index
                   (canonical_vi, canonical_zh, aliases, short_note, first_seen_corpus,
                    first_seen_page, category, corpora, school, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (vi, zh, json.dumps(aliases, ensure_ascii=False), note, CORPUS_ID, page,
                 category, json.dumps([CORPUS_ID], ensure_ascii=False), SCHOOL, now),
            )
            inserted += 1

    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM concept_index WHERE school=?", (SCHOOL,)).fetchone()[0]
    print(f"Authors seeded: {list(author_ids.items())}")
    print(f"Concepts: +{inserted} new, ~{updated} merged. Thần Số Học total: {total}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
