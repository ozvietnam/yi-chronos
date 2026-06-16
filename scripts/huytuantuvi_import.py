"""Import corpus "Huy Tuấn Tử Vi" (TikTok, kênh #2) vào hệ YI-Chronos.

Anh duyệt 2026-06-17: ingest CHỌN LỌC 4 lớp, TÁCH school riêng `tu_vi_huy_tuan`
(KHÔNG trộn tu_vi_bon_ba/phái cổ), gắn attribution + cờ verify/unverified.

Làm (idempotent — chạy lại xóa + nạp lại corpus này):
1. Merge 6 file extracted/chunk-*.json → dataset data/yi_wiki/huytuantuvi_dataset.json
2. Cách cục lớp 1 → cố match dict 545 cách (cach_cuc_index.json, Phú Thái Vi):
   match → verified=true + matched_cach; không match → unverified (flag cho_doi_chieu).
3. Nạp wiki.sqlite3: author "Huy Tuấn Tử Vi" + chunks_v2 (mỗi video 1 chunk, corpus
   tu-vi-huy-tuan-tiktok) + atomic_questions (atoms theo 8 type, FTS qua trigger).

Subject_identifiers MỌI atom: {"school_code":"tu_vi_huy_tuan", "layer":N, ...}.
"""
import json
import sqlite3
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data/research/tiktok_transcripts/huytuantuvi"
EXTRACTED_DIR = SRC_DIR / "extracted"
VIDEOS_JSON = SRC_DIR / "videos.json"
DATASET_OUT = ROOT / "data/yi_wiki/huytuantuvi_dataset.json"
DB_PATH = ROOT / "data/yi_wiki/wiki.sqlite3"
CACH_CUC_DICT = ROOT / "data/yi_publishing/q1_tuvi/master/cach_cuc_index.json"

CORPUS_ID = "tu-vi-huy-tuan-tiktok"
EXTRACTED_BY = "sub-agent-huytuantuvi"
AUTHOR_NAME = "Huy Tuấn Tử Vi"
SCHOOL = "tu_vi_huy_tuan"


def norm(s: str) -> str:
    """Bỏ dấu + thường hóa + chỉ giữ chữ-số (để so cách cục)."""
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(c.lower() for c in s if c.isalnum())


# ─────────────────────────── cách cục matcher ───────────────────────────
def load_cach_dict() -> list[tuple[str, dict]]:
    """Trả [(norm_key, entry)] để match."""
    if not CACH_CUC_DICT.exists():
        print("⚠️  Không thấy cach_cuc_index.json — bỏ qua verify cách cục.")
        return []
    raw = json.loads(CACH_CUC_DICT.read_text(encoding="utf-8"))
    items = raw.items() if isinstance(raw, dict) else ((e.get("ten", ""), e) for e in raw)
    return [(norm(k), e) for k, e in items if k]


_CACH_DICT = load_cach_dict()


def match_cach_cuc(ten: str, dieu_kien: str | None) -> dict | None:
    """Match 1 cách Huy Tuấn với dict Phú Thái Vi — CHỈ theo TÊN cách (không match theo
    điều kiện để tránh trùng tên sao như 'Thiên Lương'). Yêu cầu phần trùng đủ dài (>=8 ký
    tự bỏ dấu) để loại false-positive. Tên cách Huy Tuấn có thể chứa biến thể (vd 'Hùng Tú
    Kiền Nguyên' ~ 'Hùng Túc Triêu Nguyên') nên dùng substring 2 chiều trên phần đủ dài."""
    nt = norm(ten)
    if len(nt) < 8 or not _CACH_DICT:
        return None
    best = None
    for nk, entry in _CACH_DICT:
        if len(nk) < 8:
            continue
        shorter = nk if len(nk) <= len(nt) else nt
        if shorter in nk and shorter in nt:  # phần ngắn hơn là substring của cả hai
            # ưu tiên match dài nhất (đặc trưng nhất)
            if best is None or len(shorter) > best[0]:
                best = (len(shorter), entry)
    if best:
        e = best[1]
        return {"matched_ten": e.get("ten"), "cap_do": e.get("cap_do"), "y_nghia": e.get("y_nghia")}
    return None


# ─────────────────────────── merge dataset ───────────────────────────
def merge_dataset() -> dict:
    records: list[dict] = []
    for f in sorted(EXTRACTED_DIR.glob("chunk-*.json")):
        recs = json.loads(f.read_text(encoding="utf-8"))
        for r in recs:
            r.setdefault("school", SCHOOL)
            records.append(r)
    # verify cách cục
    n_matched = 0
    for r in records:
        if r.get("type") == "cach_cuc":
            m = match_cach_cuc(r.get("ten", ""), r.get("dieu_kien"))
            if m:
                r["_verified"] = True
                r["_matched_cach"] = m["matched_ten"]
                n_matched += 1
            else:
                r["_verified"] = False
    ds = {
        "school": SCHOOL,
        "school_label": "Huy Tuấn Tử Vi (hiện đại VN — Trung Châu phái, kỹ thuật cách cục)",
        "source": "72/77 video TikTok @huytuantuvi (2025-12-21 → 2026-05-24)",
        "ingest_note": "Ingest chọn lọc 4 lớp (Anh duyệt 2026-06-17). Paradigm gốc NGƯỢC Iron Rule "
                       "(predict/định mệnh) — chỉ trích kỹ thuật + tinh thần aligned; vùng độc hại "
                       "giữ làm LÁ CHẮN (layer 3) để sage TRÁNH. Mọi atom gắn attribution + cờ verify.",
        "n_cach_matched": n_matched,
        "records": records,
    }
    DATASET_OUT.write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")
    cc = sum(1 for r in records if r.get("type") == "cach_cuc")
    print(f"✅ Merge {len(records)} record → {DATASET_OUT.name} "
          f"(cách cục {cc}, match dict Phú Thái Vi: {n_matched})")
    return ds


# ─────────────────────────── atoms ───────────────────────────
def _q(parts) -> str:
    return ". ".join(x.strip().rstrip(".") for x in parts if x)[:2000]


def _quotes(rec: dict) -> str:
    qs = rec.get("quotes") or []
    return " | ".join(qs[:3])[:2000]


def atoms_from_record(rec: dict) -> list[dict]:
    t = rec.get("type")
    layer = rec.get("layer")
    base = {"school_code": SCHOOL}
    if layer:
        base["layer"] = layer
    if rec.get("unverified"):
        base["unverified"] = True
    if rec.get("nhay_cam_flag_founder"):
        base["nhay_cam_flag_founder"] = True
    out: list[dict] = []

    if t == "chinh_tinh":
        sao = rec.get("sao", "")
        subj = {**base, "star": [sao], "palace": ["menh"]}
        out.append({
            "q": f"Theo Huy Tuấn Tử Vi, sao {sao} thủ Mệnh có bản chất và tính cách thế nào?",
            "quote": _q([rec.get("biet_danh") and f"({rec['biet_danh']})",
                         ", ".join(rec.get("tom_gon") or []), rec.get("tinh_cach"),
                         rec.get("tai_nang") and ("Tài năng: " + ", ".join(rec["tai_nang"])),
                         rec.get("uu_diem") and ("Ưu: " + rec["uu_diem"]),
                         rec.get("nhuoc_diem") and ("Nhược: " + rec["nhuoc_diem"])]),
            "subj": subj, "cat": "hty_chinh_tinh",
        })
        if rec.get("ua_sao") or rec.get("ghet_sao"):
            out.append({
                "q": f"Sao {sao} ƯA và GHÉT gặp sao/Tứ Hóa nào (theo Huy Tuấn)?",
                "quote": _q([rec.get("ua_sao") and ("Ưa: " + ", ".join(rec["ua_sao"])),
                             rec.get("ghet_sao") and ("Ghét: " + ", ".join(rec["ghet_sao"])),
                             rec.get("mieu_ham")]),
                "subj": subj, "cat": "hty_chinh_tinh",
            })
        if rec.get("nhan_dien"):
            out.append({
                "q": f"Cách nhận diện người có sao {sao} thủ Mệnh (theo Huy Tuấn)?",
                "quote": rec["nhan_dien"][:2000], "subj": subj, "cat": "hty_chinh_tinh",
            })

    elif t == "phu_tinh":
        sao = rec.get("sao", "")
        subj = {**base, "star": [sao]}
        cap = rec.get("cap_do_vi_tri") or []
        cap_txt = "; ".join(
            f"{c.get('vi_tri')}: {c.get('manh_yeu')} ({c.get('ly_do')})" for c in cap) if cap else None
        out.append({
            "q": f"Phụ tinh {sao}: bản chất, nguồn trợ lực, và cấp độ mạnh-yếu theo vị trí (theo Huy Tuấn)?",
            "quote": _q([rec.get("ban_chat"), rec.get("nguon_tro_luc"), cap_txt]),
            "subj": subj, "cat": "hty_phu_tinh",
        })
        if rec.get("thich_chinh_tinh") or rec.get("ghet_chinh_tinh"):
            out.append({
                "q": f"Phụ tinh {sao} ưa/kỵ đi cặp với chính tinh nào (theo Huy Tuấn)?",
                "quote": _q([rec.get("thich_chinh_tinh") and ("Thích: " + ", ".join(rec["thich_chinh_tinh"])),
                             rec.get("ghet_chinh_tinh") and ("Kỵ: " + ", ".join(rec["ghet_chinh_tinh"]))]),
                "subj": subj, "cat": "hty_phu_tinh",
            })
        if rec.get("ly_ngu_hanh"):
            out.append({
                "q": f"Lý ngũ hành-địa chi của {sao} (theo Huy Tuấn)?",
                "quote": rec["ly_ngu_hanh"][:2000],
                "subj": {**subj, "ngu_hanh": True}, "cat": "hty_ngu_hanh",
            })

    elif t == "cach_cuc":
        subj = {**base, "cach": [rec.get("ten", "")], "verified": bool(rec.get("_verified"))}
        if rec.get("_matched_cach"):
            subj["matched_cach"] = rec["_matched_cach"]
        if rec.get("cap_do"):
            subj["cap_do"] = rec["cap_do"]
        vtag = "ĐÃ đối chiếu Phú Thái Vi" if rec.get("_verified") else "CHƯA đối chiếu (chỉ theo Huy Tuấn)"
        out.append({
            "q": f"Cách cục '{rec.get('ten')}' trong Tử Vi: điều kiện và ý nghĩa là gì?",
            "quote": _q([f"Điều kiện: {rec.get('dieu_kien')}", f"Ý nghĩa: {rec.get('y_nghia')}",
                         f"[{vtag}]"]),
            "subj": subj, "cat": "hty_cach_cuc",
        })

    elif t == "an_sao_dinh_chinh":
        subj = {**base, "an_sao_correction": True}
        if rec.get("tuoi_can"):
            subj["tuoi_can"] = rec["tuoi_can"]
        out.append({
            "q": f"Đính chính an sao theo Huy Tuấn{(' (tuổi ' + rec['tuoi_can'] + ')') if rec.get('tuoi_can') else ''}: nội dung gì? (CẦN đối chiếu engine)",
            "quote": rec.get("noi_dung", "")[:2000], "subj": subj, "cat": "hty_an_sao",
        })

    elif t == "ngu_hanh_dia_chi":
        out.append({
            "q": "Lý ngũ hành-địa chi (nhiệt-ẩm) theo Huy Tuấn — đối chiếu engine ngu_hanh_nen?",
            "quote": _q([rec.get("noi_dung"), rec.get("cross_ref") and ("Cross-ref: " + rec["cross_ref"])]),
            "subj": {**base, "ngu_hanh": True, "cross_ref_engine": rec.get("cross_ref")},
            "cat": "hty_ngu_hanh",
        })

    elif t == "paradigm_aligned":
        out.append({
            "q": f"[PARADIGM-ALIGNED] {rec.get('chu_de')} — insight hội tụ với Iron Rule là gì?",
            "quote": _q([rec.get("insight"), rec.get("vi_sao_aligned") and ("Vì sao trùng: " + rec["vi_sao_aligned"])]),
            "subj": {**base, "paradigm_aligned": True}, "cat": "hty_paradigm",
        })

    elif t == "la_chan_dao_duc":
        out.append({
            "q": f"[LÁ CHẮN ĐẠO ĐỨC — mẫu luận SAI cần TRÁNH] {rec.get('chu_de')}: sai thế nào và sage phải làm gì?",
            "quote": _q([rec.get("mau_luan_sai") and ("Mẫu SAI: " + rec["mau_luan_sai"]),
                         rec.get("vi_sao_sai") and ("Vì sao sai: " + rec["vi_sao_sai"]),
                         rec.get("sage_phai_lam_gi") and ("Sage làm: " + rec["sage_phai_lam_gi"])]),
            "subj": {**base, "anti_paradigm": True, "ethical_shield": True}, "cat": "hty_la_chan",
        })

    elif t == "quan_diem":
        out.append({
            "q": f"[QUAN ĐIỂM CHƯA KIỂM CHỨNG của Huy Tuấn]{' [NHẠY CẢM — cần founder duyệt]' if rec.get('nhay_cam_flag_founder') else ''}: nội dung và vì sao chưa kiểm chứng?",
            "quote": _q([rec.get("noi_dung"), rec.get("vi_sao_unverified") and ("Vì sao unverified: " + rec["vi_sao_unverified"])]),
            "subj": {**base, "quan_diem": True}, "cat": "hty_quan_diem",
        })

    # đính kèm quotes nguyên văn nếu atom đầu chưa có
    if out and rec.get("quotes"):
        out[0]["quote"] = (out[0]["quote"] + "  ⟪Nguyên văn: " + _quotes(rec) + "⟫")[:2000]
    return out


# ─────────────────────────── import DB ───────────────────────────
def import_db(dataset: dict) -> None:
    videos = {int(v["idx"]): v for v in json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    row = cur.execute("SELECT author_id FROM authors WHERE name_vi=?", (AUTHOR_NAME,)).fetchone()
    if row:
        author_id = row["author_id"]
    else:
        cur.execute(
            """INSERT INTO authors (name_vi, name_zh, tier_in_lineage, era, worldview_school,
               hermeneutic_style, works, bio_summary, created_at)
               VALUES (?, NULL, 5, 'hiện đại (2026)', ?, ?, ?, ?, ?)""",
            (AUTHOR_NAME, SCHOOL,
             "Tử Vi Trung Châu phái hiện đại VN: nặng kỹ thuật cách cục/Tứ Hóa/miếu-hãm, chống mê tín. "
             "CẢNH BÁO: paradigm gốc nghiêng predict/định mệnh — hệ chỉ dùng lớp kỹ thuật + tinh thần aligned.",
             "Kênh TikTok @huytuantuvi — 77 video (2025-2026)",
             "Trường phái Tử Vi hiện đại VN. Mạnh về cách cục cổ điển + đính chính an sao + lý ngũ hành "
             "địa chi. Đưa vào hệ CHỌN LỌC 4 lớp, tách school riêng, attribution rõ.",
             int(time.time())),
        )
        author_id = cur.lastrowid
        print(f"✅ Thêm author '{AUTHOR_NAME}' (id={author_id})")

    old = [r["chunk_id"] for r in cur.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS_ID,))]
    if old:
        qs = ",".join("?" * len(old))
        na = cur.execute(f"SELECT COUNT(*) FROM atomic_questions WHERE chunk_id IN ({qs})", old).fetchone()[0]
        cur.execute(f"DELETE FROM atomic_questions WHERE chunk_id IN ({qs})", old)
        cur.execute("DELETE FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS_ID,))
        print(f"♻️  Xóa corpus cũ: {len(old)} chunks + {na} atoms")

    chunk_by_video: dict[int, int] = {}
    now = int(time.time())
    for idx, v in sorted(videos.items()):
        if str(v.get("has_transcript")).lower() not in ("true", "1"):
            continue
        cur.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, author_id, page_start, page_end,
               section_path, text, summary, metadata_json, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (CORPUS_ID, author_id, idx, idx, f"video-{idx:03d}",
             v.get("text", ""), v.get("title", ""),
             json.dumps({"video_id": v.get("video_id"), "url": v.get("url"), "date": v.get("date"),
                         "title": v.get("title"), "duration": v.get("duration"),
                         "school": SCHOOL, "attribution": "Huy Tuấn Tử Vi (TikTok)"}, ensure_ascii=False),
             now),
        )
        chunk_by_video[idx] = cur.lastrowid
    print(f"✅ Nạp {len(chunk_by_video)} chunks (corpus {CORPUS_ID})")

    n_atoms = 0
    skipped = 0
    for rec in dataset["records"]:
        vid = (rec.get("source") or {}).get("video_idx")
        chunk_id = chunk_by_video.get(int(vid)) if vid else None
        if chunk_id is None:
            chunk_id = next(iter(chunk_by_video.values()))
            skipped += 1
        # confidence: cách cục verified cao; unverified/la_chan thấp; aligned/kỹ thuật vừa-cao
        if rec.get("unverified"):
            conf = 0.5
        elif rec.get("type") == "la_chan_dao_duc":
            conf = 0.4  # thấp: đây là ví dụ-để-tránh, không phải tri thức để luận theo
        elif rec.get("type") == "cach_cuc":
            conf = 0.85 if rec.get("_verified") else 0.6
        else:
            conf = 0.8
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
    print(f"✅ Nạp {n_atoms} atoms (DB xác nhận {total}; record neo video đầu vì thiếu nguồn: {skipped})")


if __name__ == "__main__":
    ds = merge_dataset()
    import_db(ds)
    print("\n📌 Nhớ: chạy lại engine cache nếu có; đăng ký school trong cross_school.py + cung_sao_mapping.py.")
