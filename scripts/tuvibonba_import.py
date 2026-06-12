#!/usr/bin/env python3
"""Import corpus Tử Vi Bôn Ba (TikTok) vào hệ YI-Chronos.

Làm 3 việc (idempotent — chạy lại sẽ xóa và nạp lại corpus này):
1. Gộp ``extracted/*.json`` → dataset chuẩn ``data/yi_wiki/tuvibonba_ngu_uan.json``
   (engine/tu_vi/ngu_uan.py đọc file này cho tầng narrative).
2. Nạp wiki.sqlite3:
   - authors: thêm "Tử Vi Bôn Ba" (hiện đại VN)
   - chunks_v2: mỗi video 1 chunk, book_corpus_id = "tuvi-bon-ba-tiktok"
   - atomic_questions: atoms hạt mịn từ records (FTS tự cập nhật qua trigger)
3. In thống kê.

Chạy: .venv/bin/python3 scripts/tuvibonba_import.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data/research/tiktok_transcripts/tuvibonba"
EXTRACTED_DIR = SRC_DIR / "extracted"
VIDEOS_JSON = SRC_DIR / "videos.json"
DATASET_OUT = ROOT / "data/yi_wiki/tuvibonba_ngu_uan.json"
DB_PATH = ROOT / "data/yi_wiki/wiki.sqlite3"

CORPUS_ID = "tuvi-bon-ba-tiktok"
EXTRACTED_BY = "sub-agent-tuvibonba"
AUTHOR_NAME = "Tử Vi Bôn Ba"

UAN_LABELS = {
    "sac": "Sắc uẩn (biểu hiện ra ngoài)",
    "tho": "Thọ uẩn (cảm xúc)",
    "tuong": "Tưởng uẩn (cách nhìn nhận)",
    "hanh": "Hành uẩn (phản ứng, thói quen)",
    "thuc": "Thức uẩn (niềm tin sâu nhất)",
}

ALL_PALACES = ["menh", "phu_mau", "phuc_duc", "dien_trach", "quan_loc", "no_boc",
               "thien_di", "tat_ach", "tai_bach", "tu_tuc", "phu_the", "huynh_de"]


def canon(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    s2 = "".join(c for c in nfkd if not unicodedata.combining(c))
    return s2.lower().strip().replace(" ", "_").replace("-", "_").replace("đ", "d")


def merge_dataset() -> dict:
    records = []
    files = sorted(EXTRACTED_DIR.glob("*.json"))
    if not files:
        sys.exit(f"Không có file nào trong {EXTRACTED_DIR} — chạy extraction trước.")
    for f in files:
        try:
            batch = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"File {f.name} không parse được: {e}")
        if not isinstance(batch, list):
            sys.exit(f"File {f.name} không phải mảng JSON.")
        for rec in batch:
            rec.setdefault("school", "tu_vi_bon_ba")
            rec["_batch"] = f.stem
            records.append(rec)
    dataset = {
        "meta": {
            "school": "tu_vi_bon_ba",
            "school_label": "Tử Vi Bôn Ba (hiện đại VN — quán chiếu Ngũ Uẩn)",
            "source": "98 video TikTok @tuvibonba (2026-01-29 → 2026-06-11)",
            "built_at": int(time.time()),
            "n_records": len(records),
            "note_unverified": "Record có unverified=true là diễn giải chưa kiểm chứng — không dùng làm sự thật lịch sử.",
        },
        "records": records,
    }
    DATASET_OUT.write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ Dataset: {len(records)} records ({len(files)} batch) → {DATASET_OUT}")
    return dataset


# ─── Atom generation ──────────────────────────────────────────────────────────

def _quotes(rec: dict, *fields: str, limit: int = 3) -> str:
    """Ghép quote/nguồn cho source_quote."""
    parts = []
    for f in fields:
        v = rec.get(f)
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
    for q in (rec.get("quotes") or [])[:limit]:
        parts.append(f"“{q}”")
    return "\n".join(parts)[:2000]


def atoms_from_record(rec: dict) -> list[dict]:
    """Sinh atoms hạt mịn từ 1 record dataset. Mỗi atom:
    {question_text, source_quote, subject_identifiers, from_category, confidence}
    """
    t = rec.get("type")
    out: list[dict] = []
    base_subj = {"school_code": "tu_vi_bon_ba"}
    if rec.get("unverified"):
        base_subj["unverified"] = True

    if t == "chinh_tinh":
        sao = rec["sao"]
        s_tag = [canon(sao)]
        tom_gon = ", ".join(rec.get("tom_gon") or [])
        out.append({
            "q": f"Theo Tử Vi Bôn Ba (quán chiếu Ngũ Uẩn), bản chất gốc của sao {sao} là gì?",
            "quote": _quotes({"a": f"{sao}: {tom_gon}. {rec.get('menh_de_dinh_vi') or ''}",
                              "quotes": rec.get("quotes")}, "a"),
            "subj": {**base_subj, "star": s_tag, "palace": ["menh"]},
            "cat": "tvbb_chinh_tinh",
        })
        for key, label in UAN_LABELS.items():
            u = (rec.get("ngu_uan") or {}).get(key)
            if not u:
                continue
            if isinstance(u, str):
                u = {"mo_ta": u}
            body = ". ".join(x for x in [
                u.get("mo_ta"),
                f"Khi mạnh: {u['khi_manh']}" if u.get("khi_manh") else None,
                f"Khi lệch: {u['khi_lech']}" if u.get("khi_lech") else None,
            ] if x)
            out.append({
                "q": f"Sao {sao} qua {label} biểu hiện thế nào — khi mạnh và khi lệch ra sao?",
                "quote": body[:2000],
                "subj": {**base_subj, "star": s_tag, "palace": ["menh"], "uan": key},
                "cat": "tvbb_chinh_tinh",
            })
        if rec.get("sao_o_dau_thi"):
            out.append({
                "q": f"Sao {sao} đóng ở bất kỳ cung nào thì nơi đó nói lên điều gì?",
                "quote": rec["sao_o_dau_thi"][:2000],
                "subj": {**base_subj, "star": s_tag, "palace": ALL_PALACES},
                "cat": "tvbb_chinh_tinh",
            })
        if rec.get("can_de_phat_huy"):
            out.append({
                "q": f"Người có sao {sao} cần điều gì nhất để trở thành phiên bản tốt nhất?",
                "quote": rec["can_de_phat_huy"][:2000],
                "subj": {**base_subj, "star": s_tag, "palace": ["menh"]},
                "cat": "tvbb_chinh_tinh",
            })

    elif t == "cung":
        cung = rec["cung"]
        p_tag = [canon(cung)]
        out.append({
            "q": f"Theo Tử Vi Bôn Ba, cung {cung} thực chất là bối cảnh gì (định nghĩa lại)?",
            "quote": _quotes(rec, "dinh_nghia_lai", "debunk"),
            "subj": {**base_subj, "palace": p_tag},
            "cat": "tvbb_cung",
        })
        for key, label in UAN_LABELS.items():
            u = (rec.get("ngu_uan") or {}).get(key)
            if isinstance(u, dict):
                u = u.get("mo_ta")
            if not u:
                continue
            out.append({
                "q": f"{label} của cung {cung} nói về điều gì?",
                "quote": str(u)[:2000],
                "subj": {**base_subj, "palace": p_tag, "uan": key},
                "cat": "tvbb_cung",
            })
        if rec.get("cau_hoi_tu_van"):
            out.append({
                "q": f"Câu hỏi tự soi nào giúp hiểu cung {cung} của chính mình?",
                "quote": rec["cau_hoi_tu_van"][:2000],
                "subj": {**base_subj, "palace": p_tag},
                "cat": "tvbb_cung",
            })

    elif t in ("nguyen_ly", "quan_diem"):
        ten = rec.get("ten") or "?"
        out.append({
            "q": f"Theo Tử Vi Bôn Ba: {ten} — nội dung cốt lõi là gì?",
            "quote": _quotes(rec, "phat_bieu", "giai_thich", "lap_luan", "ap_dung", "he_qua_thuc_hanh"),
            "subj": dict(base_subj),
            "cat": f"tvbb_{t}",
        })
        for item in (rec.get("items") or []):
            iten = item.get("ten") or ""
            inoi = item.get("noi_dung") or ""
            if not (iten and inoi):
                continue
            subj = dict(base_subj)
            # Item là tên sao (mẹo nhìn nhanh, xã hội thu nhỏ...) → tag star + mọi cung
            star_c = canon(iten)
            if star_c in {canon(s) for s in [
                "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
                "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
                "Thất Sát", "Phá Quân", "Vô Chính Diệu"]}:
                subj["star"] = [star_c]
                subj["palace"] = ALL_PALACES
            out.append({
                "q": f"{ten} — phần “{iten}” nói gì?",
                "quote": inoi[:2000],
                "subj": subj,
                "cat": f"tvbb_{t}",
            })

    elif t == "ung_dung":
        ten = rec.get("ten") or "?"
        body = _quotes(rec, "tinh_huong", "co_che", "canh_bao")
        steps = rec.get("cach_lam") or []
        if steps:
            body += "\nCách làm: " + " | ".join(str(s) for s in steps)
        subj = dict(base_subj)
        # Tag sát tinh / sao nếu xuất hiện trong tên
        for star in ["Địa Kiếp", "Địa Không", "Hỏa Tinh", "Linh Tinh", "Đà La", "Kình Dương"]:
            if star.lower() in ten.lower():
                subj["star"] = [canon(star)]
                subj["palace"] = ["menh"]
        out.append({
            "q": f"Ứng dụng Tử Vi Bôn Ba: {ten} — nhận diện và cách làm?",
            "quote": body[:2000],
            "subj": subj,
            "cat": "tvbb_ung_dung",
        })

    return out


# ─── DB import ────────────────────────────────────────────────────────────────

def import_db(dataset: dict) -> None:
    videos = {v["idx"]: v for v in json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Author (idempotent)
    row = cur.execute("SELECT author_id FROM authors WHERE name_vi=?", (AUTHOR_NAME,)).fetchone()
    if row:
        author_id = row["author_id"]
    else:
        cur.execute(
            """INSERT INTO authors (name_vi, name_zh, tier_in_lineage, era, worldview_school,
               hermeneutic_style, works, bio_summary, created_at)
               VALUES (?, NULL, 5, 'hiện đại (2026)', 'tu_vi_bon_ba',
               'Tái định nghĩa khái niệm + quán chiếu Ngũ Uẩn (Phật học) vào sao và cung; chống gieo sợ hãi',
               'Kênh TikTok @tuvibonba — 98 video (2026)',
               'Trường phái Tử Vi hiện đại VN: lá số là bản đồ sống theo thời gian thực, sao = lực sống không tốt-xấu, cung = bối cảnh sống, miếu hãm = độ khó bài học. Khung phân tích Ngũ Uẩn.',
               ?)""",
            (AUTHOR_NAME, int(time.time())),
        )
        author_id = cur.lastrowid
        print(f"✅ Thêm author '{AUTHOR_NAME}' (id={author_id})")

    # Xóa corpus cũ (idempotent re-run) — atoms xóa theo cascade? FK không có ON DELETE
    old_chunk_ids = [r["chunk_id"] for r in cur.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS_ID,))]
    if old_chunk_ids:
        qs = ",".join("?" * len(old_chunk_ids))
        n_atoms = cur.execute(
            f"SELECT COUNT(*) FROM atomic_questions WHERE chunk_id IN ({qs})", old_chunk_ids
        ).fetchone()[0]
        cur.execute(f"DELETE FROM atomic_questions WHERE chunk_id IN ({qs})", old_chunk_ids)
        cur.execute("DELETE FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS_ID,))
        print(f"♻️  Xóa corpus cũ: {len(old_chunk_ids)} chunks + {n_atoms} atoms")

    # Chunks: mỗi video 1 chunk
    chunk_id_by_video: dict[int, int] = {}
    now = int(time.time())
    for idx, v in sorted(videos.items()):
        if not v["has_transcript"]:
            continue
        cur.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, author_id, page_start, page_end,
               section_path, text, summary, metadata_json, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (CORPUS_ID, author_id, idx, idx, f"video-{idx:03d}",
             v["text"], v["title"],
             json.dumps({"video_id": v["video_id"], "url": v["url"], "date": v["date"],
                         "title": v["title"], "duration": v["duration"]}, ensure_ascii=False),
             now),
        )
        chunk_id_by_video[idx] = cur.lastrowid
    print(f"✅ Nạp {len(chunk_id_by_video)} chunks (corpus {CORPUS_ID})")

    # Atoms
    n_atoms = 0
    skipped = 0
    for rec in dataset["records"]:
        vid = (rec.get("source") or {}).get("video_idx")
        chunk_id = chunk_id_by_video.get(vid)
        if chunk_id is None:
            # Nguồn không rõ video → neo vào video đầu tiên có transcript
            chunk_id = next(iter(chunk_id_by_video.values()))
            skipped += 1
        conf = 0.55 if rec.get("unverified") else 0.85
        for atom in atoms_from_record(rec):
            cur.execute(
                """INSERT INTO atomic_questions
                   (chunk_id, question_text, question_lang, from_category,
                    subject_identifiers, source_quote, confidence, extracted_by, section_id)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (chunk_id, atom["q"], "vi", atom["cat"],
                 json.dumps(atom["subj"], ensure_ascii=False), atom["quote"],
                 conf, EXTRACTED_BY, rec.get("type")),
            )
            n_atoms += 1
    conn.commit()

    total = cur.execute(
        """SELECT COUNT(*) FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id=a.chunk_id
           WHERE c.book_corpus_id=?""", (CORPUS_ID,)).fetchone()[0]
    conn.close()
    print(f"✅ Nạp {n_atoms} atoms (DB xác nhận: {total}; record thiếu nguồn video: {skipped})")


if __name__ == "__main__":
    ds = merge_dataset()
    import_db(ds)
    # Engine cache invalidation note
    print("\n→ Restart API (hoặc gọi invalidate_mapping_cache + ngu_uan.invalidate_cache) để nạp dữ liệu mới.")
