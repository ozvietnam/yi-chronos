"""Import corpus "Nguyệt Đồ Số Mệnh" (TikTok, kênh #3) vào hệ YI-Chronos.

Anh giao 2026-06-26: ĐÃI CÁT TÌM VÀNG + bổ thư viện + LÀM GIÀU ENGINE.
Ingest CHỌN LỌC (đã đãi cát: 411 clickbait bỏ, 103 video vàng → 180 record),
TÁCH school riêng `nguyet_do_so_menh`, attribution + cờ verify.

Làm (idempotent):
1. Merge 8 chunk → dataset data/yi_wiki/nguyetdosomenh_dataset.json
2. Cách cục → đối chiếu dict 1193 cách (Phú Thái Vi): khớp → verified;
   KHÔNG khớp → CÁCH MỚI (cach_moi) → xuất `CACH-CUC-MOI-candidates.md` để Anh duyệt
   bổ sung engine cach_cuc_dict (làm giàu phương pháp).
3. Nạp wiki.sqlite3: author + chunks_v2 (corpus nguyet-do-so-menh-tiktok) + atomic_questions.

8 type atom: cach_cuc, than_sat_phu_tinh, luan_giai, nap_am (verify bat_tu),
paradigm_aligned (L2), la_chan_dao_duc (L3), quan_diem (unverified).
"""
import json
import sqlite3
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data/research/tiktok_transcripts/nguyetdosomenh"
EXTRACTED_DIR = SRC_DIR / "extracted"
VIDEOS_JSON = SRC_DIR / "final/videos.json"
DATASET_OUT = ROOT / "data/yi_wiki/nguyetdosomenh_dataset.json"
NEW_CACH_OUT = SRC_DIR / "CACH-CUC-MOI-candidates.md"
DB_PATH = ROOT / "data/yi_wiki/wiki.sqlite3"
CACH_CUC_DICT = ROOT / "data/yi_publishing/q1_tuvi/master/cach_cuc_index.json"

CORPUS_ID = "nguyet-do-so-menh-tiktok"
EXTRACTED_BY = "sub-agent-nguyetdosomenh"
AUTHOR_NAME = "Nguyệt Đồ Số Mệnh"
SCHOOL = "nguyet_do_so_menh"


def norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(c.lower() for c in s if c.isalnum())


def load_cach_dict() -> list[tuple[str, dict]]:
    if not CACH_CUC_DICT.exists():
        print("⚠️  Không thấy cach_cuc_index.json — bỏ qua verify cách cục.")
        return []
    raw = json.loads(CACH_CUC_DICT.read_text(encoding="utf-8"))
    items = raw.items() if isinstance(raw, dict) else ((e.get("ten", ""), e) for e in raw)
    return [(norm(k), e) for k, e in items if k]


_CACH_DICT = load_cach_dict()


def match_cach_cuc(ten: str) -> dict | None:
    """Match theo TÊN cách (substring 2 chiều, phần trùng >=8 ký tự bỏ dấu — tránh false-positive)."""
    nt = norm(ten)
    if len(nt) < 8 or not _CACH_DICT:
        return None
    best = None
    for nk, entry in _CACH_DICT:
        if len(nk) < 8:
            continue
        shorter = nk if len(nk) <= len(nt) else nt
        if shorter in nk and shorter in nt:
            if best is None or len(shorter) > best[0]:
                best = (len(shorter), entry)
    if best:
        e = best[1]
        return {"matched_ten": e.get("ten"), "cap_do": e.get("cap_do"), "y_nghia": e.get("y_nghia")}
    return None


def merge_dataset() -> dict:
    records: list[dict] = []
    for f in sorted(EXTRACTED_DIR.glob("chunk-*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            r.setdefault("school", SCHOOL)
            records.append(r)
    n_matched = 0
    new_cach: list[dict] = []
    for r in records:
        if r.get("type") == "cach_cuc":
            m = match_cach_cuc(r.get("ten", ""))
            if m:
                r["_verified"] = True
                r["_matched_cach"] = m["matched_ten"]
                n_matched += 1
            else:
                r["_verified"] = False
                r["_cach_moi"] = True  # importer-authoritative: không khớp dict = ứng viên cách MỚI
                new_cach.append(r)
    ds = {
        "school": SCHOOL,
        "school_label": "Nguyệt Đồ Số Mệnh (hiện đại VN — Tử Vi cách cục thực hành + nạp âm dân gian)",
        "source": "103/514 video TikTok @nguyetdosomenh (đãi cát: 411 clickbait bỏ; vàng 2024 nạp âm + 2026 Tử Vi cách cục)",
        "ingest_note": "Ingest CHỌN LỌC sau khi đãi cát tìm vàng (Anh giao 2026-06-26). Trọng tâm: làm giàu "
                       "engine cach_cuc_dict bằng cách cục MỚI + luận giải thực hành. Vùng predict cứng giữ "
                       "làm lá chắn (L3). Paradigm hỗn hợp (có đoạn aligned tốt).",
        "n_cach_matched": n_matched,
        "n_cach_moi": len(new_cach),
        "records": records,
    }
    DATASET_OUT.write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")
    # Xuất danh sách CÁCH MỚI cho Anh duyệt (làm giàu engine)
    lines = ["# CÁCH CỤC MỚI — ứng viên bổ sung engine `cach_cuc_dict` (kênh #3 Nguyệt Đồ)\n",
             f"> Đãi cát tìm vàng 2026-06-26. {len(new_cach)} cách KHÔNG khớp dict 1193 cách Phú Thái Vi → ứng viên MỚI.",
             "> Anh duyệt cái nào đúng/đáng thêm → em wire vào engine.\n"]
    for r in sorted(new_cach, key=lambda x: -(len((x.get("dieu_kien") or "")))):
        s = r.get("source", {})
        lines.append(f"## {r.get('ten')}")
        lines.append(f"- **Lĩnh vực**: {r.get('linh_vuc', '?')} · **Cấp độ**: {r.get('cap_do', '?')}")
        lines.append(f"- **Điều kiện**: {r.get('dieu_kien', '?')}")
        lines.append(f"- **Ý nghĩa**: {r.get('y_nghia', '?')}")
        lines.append(f"- Nguồn: video #{s.get('video_idx')} ({s.get('date')}) {s.get('url', '')}\n")
    NEW_CACH_OUT.write_text("\n".join(lines), encoding="utf-8")
    cc = sum(1 for r in records if r.get("type") == "cach_cuc")
    print(f"✅ Merge {len(records)} record → {DATASET_OUT.name} "
          f"(cách cục {cc}: khớp dict {n_matched}, MỚI {len(new_cach)} → {NEW_CACH_OUT.name})")
    return ds


def _q(parts) -> str:
    return ". ".join(x.strip().rstrip(".") for x in parts if x)[:2000]


def _quotes(rec: dict) -> str:
    return " | ".join((rec.get("quotes") or [])[:3])[:2000]


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

    if t == "cach_cuc":
        subj = {**base, "cach": [rec.get("ten", "")], "verified": bool(rec.get("_verified"))}
        if rec.get("_matched_cach"):
            subj["matched_cach"] = rec["_matched_cach"]
        if rec.get("_cach_moi"):
            subj["cach_moi"] = True
        if rec.get("linh_vuc"):
            subj["linh_vuc"] = rec["linh_vuc"]
        vtag = ("ĐÃ khớp dict Phú Thái Vi" if rec.get("_verified")
                else "CÁCH MỚI — chưa có trong dict 1193 cách (ứng viên làm giàu engine)")
        out.append({
            "q": f"Cách cục '{rec.get('ten')}' ({rec.get('linh_vuc', '')}) trong Tử Vi: điều kiện và ý nghĩa?",
            "quote": _q([f"Điều kiện: {rec.get('dieu_kien')}", f"Ý nghĩa: {rec.get('y_nghia')}", f"[{vtag}]"]),
            "subj": subj, "cat": "ndsm_cach_cuc",
        })

    elif t == "than_sat_phu_tinh":
        out.append({
            "q": f"{rec.get('loai', 'Sao')} {rec.get('ten')} đóng cung {', '.join(rec.get('tai_cung') or []) or '...'} có ý nghĩa gì (theo Nguyệt Đồ)?",
            "quote": rec.get("y_nghia", "")[:2000],
            "subj": {**base, "star": [rec.get("ten", "")], "palace": rec.get("tai_cung") or []},
            "cat": "ndsm_than_sat",
        })

    elif t == "luan_giai":
        out.append({
            "q": f"Luận giải Nguyệt Đồ về '{rec.get('chu_de')}' ({rec.get('linh_vuc', '')}): phương pháp/luận điểm?",
            "quote": rec.get("noi_dung", "")[:2000],
            "subj": {**base, "linh_vuc": rec.get("linh_vuc")}, "cat": "ndsm_luan_giai",
        })

    elif t == "nap_am":
        entries = rec.get("entries") or []
        body = "; ".join(f"{e.get('nam')} {e.get('can_chi')}={e.get('nap_am')} ({e.get('dich')})" for e in entries)
        out.append({
            "q": "Bảng nạp âm dân gian (con giáp + tính từ) theo Nguyệt Đồ — đối chiếu engine bat_tu?",
            "quote": _q([body, rec.get("ghi_chu")]),
            "subj": {**base, "nap_am": True}, "cat": "ndsm_nap_am",
        })

    elif t == "paradigm_aligned":
        out.append({
            "q": f"[PARADIGM-ALIGNED] {rec.get('chu_de')} — insight hội tụ Iron Rule?",
            "quote": _q([rec.get("insight"), rec.get("vi_sao_aligned") and ("Vì sao trùng: " + rec["vi_sao_aligned"])]),
            "subj": {**base, "paradigm_aligned": True}, "cat": "ndsm_paradigm",
        })

    elif t == "la_chan_dao_duc":
        out.append({
            "q": f"[LÁ CHẮN ĐẠO ĐỨC — mẫu luận SAI cần TRÁNH] {rec.get('chu_de')}: sai thế nào, sage làm gì?",
            "quote": _q([rec.get("mau_luan_sai") and ("Mẫu SAI: " + rec["mau_luan_sai"]),
                         rec.get("vi_sao_sai") and ("Vì sao sai: " + rec["vi_sao_sai"]),
                         rec.get("sage_phai_lam_gi") and ("Sage làm: " + rec["sage_phai_lam_gi"])]),
            "subj": {**base, "anti_paradigm": True, "ethical_shield": True}, "cat": "ndsm_la_chan",
        })

    elif t == "quan_diem":
        out.append({
            "q": f"[QUAN ĐIỂM CHƯA KIỂM CHỨNG — Nguyệt Đồ]: nội dung và vì sao chưa kiểm chứng?",
            "quote": _q([rec.get("noi_dung"), rec.get("vi_sao_unverified") and ("Vì sao unverified: " + rec["vi_sao_unverified"])]),
            "subj": {**base, "quan_diem": True}, "cat": "ndsm_quan_diem",
        })

    if out and rec.get("quotes"):
        out[0]["quote"] = (out[0]["quote"] + "  ⟪Nguyên văn: " + _quotes(rec) + "⟫")[:2000]
    return out


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
               VALUES (?, NULL, 5, 'hiện đại (2024-2026)', ?, ?, ?, ?, ?)""",
            (AUTHOR_NAME, SCHOOL,
             "Tử Vi cách cục THỰC HÀNH (đậm cung Phu Thê/Tử Tức/Tài) + nạp âm dân gian. Phương pháp: "
             "đối chiếu Ngũ Hành bản mệnh với chính tinh cung + tam hợp. CẢNH BÁO: nhiều đoạn predict cứng.",
             "Kênh TikTok @nguyetdosomenh — 514 video (đãi cát còn 103 vàng)",
             "Trường phái Tử Vi thực hành hiện đại VN. Giàu cách cục cung Phu Thê + Tử Tức (hôn nhân, con "
             "cái, duyên xa). Đưa vào hệ CHỌN LỌC, tách school riêng, nhiều cách cục MỚI ứng viên engine.",
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

    # Chỉ nạp chunk cho video CÓ record (đãi cát: bỏ clickbait)
    vids_with_records = {int((r.get("source") or {}).get("video_idx"))
                         for r in dataset["records"] if (r.get("source") or {}).get("video_idx")}
    chunk_by_video: dict[int, int] = {}
    now = int(time.time())
    for idx in sorted(vids_with_records):
        v = videos.get(idx)
        if not v:
            continue
        cur.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, author_id, page_start, page_end,
               section_path, text, summary, metadata_json, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (CORPUS_ID, author_id, idx, idx, f"video-{idx:03d}",
             v.get("text", ""), v.get("title", ""),
             json.dumps({"video_id": v.get("video_id"), "url": v.get("url"), "date": v.get("date"),
                         "school": SCHOOL, "attribution": "Nguyệt Đồ Số Mệnh (TikTok)"}, ensure_ascii=False),
             now),
        )
        chunk_by_video[idx] = cur.lastrowid
    print(f"✅ Nạp {len(chunk_by_video)} chunks (chỉ video vàng có record; corpus {CORPUS_ID})")

    n_atoms = 0
    for rec in dataset["records"]:
        vid = (rec.get("source") or {}).get("video_idx")
        chunk_id = chunk_by_video.get(int(vid)) if vid else None
        if chunk_id is None:
            chunk_id = next(iter(chunk_by_video.values()))
        if rec.get("unverified"):
            conf = 0.5
        elif rec.get("type") == "la_chan_dao_duc":
            conf = 0.4
        elif rec.get("type") == "cach_cuc":
            conf = 0.85 if rec.get("_verified") else 0.65  # cách mới: vừa phải, chờ Anh duyệt
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
    print(f"✅ Nạp {n_atoms} atoms (DB xác nhận {total})")


if __name__ == "__main__":
    ds = merge_dataset()
    import_db(ds)
    print("\n📌 Nhớ: đăng ký school trong cross_school.py + cung_sao_mapping.py.")
