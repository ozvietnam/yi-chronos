#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_obsidian_graph.py — DỰNG ĐỒ THỊ TRI THỨC (Knowledge Graph) cho Obsidian.

Deterministic + idempotent: xoá + tạo lại CHỈ thư mục OUT mỗi lần chạy
(KHÔNG đụng .obsidian / PDF / file khác của vault).

CẠNH (edge) CHỈ sinh từ QUAN HỆ THẬT truy được về data — TUYỆT ĐỐI KHÔNG bịa link.

Nguồn:
  • data/yi_wiki/wiki.sqlite3 · concept_index (3641)
  • data/yi_wiki/tuvibonba_ngu_uan.json (sao chính tinh: ngũ hành, gốc tham, ngũ uẩn)
  • data/yi_publishing/q1_tuvi/master/cach_cuc_index.json (cách cục → sao cấu thành)
  • data/yi_publishing/books.json (sách nguồn)
  • engine/tu_vi/an_sao.py · CHINH_TINH_NAMES (14) + PALACE_NAMES (12)

Output: '<VAULT>/🧠 Mạng Tri Thức YI/' + merge .obsidian/graph.json colorGroups.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

# ───────────────────────── PATHS ─────────────────────────
ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
DB = ROOT / "data/yi_wiki/wiki.sqlite3"
NGU_UAN = ROOT / "data/yi_wiki/tuvibonba_ngu_uan.json"
CACH_CUC = ROOT / "data/yi_publishing/q1_tuvi/master/cach_cuc_index.json"
BOOKS = ROOT / "data/yi_publishing/books.json"

VAULT = ROOT / "thư viện sách"
OUT = VAULT / "🧠 Mạng Tri Thức YI"
GRAPH_JSON = VAULT / ".obsidian/graph.json"

sys.path.insert(0, str(ROOT))
from engine.tu_vi.an_sao import CHINH_TINH_NAMES, PALACE_NAMES  # noqa: E402

# ───────────────────────── CONSTANTS ─────────────────────────
# Subfolders
F_TRIET = "00 · Nền triết"
F_PHAI = "01 · Phái"
F_TV_TINH = "02 · Tử Vi/Chính tinh"
F_TV_CUNG = "02 · Tử Vi/Cung"
F_TV_CACH = "02 · Tử Vi/Cách cục"
F_CONCEPT = "03 · Khái niệm"  # + /<school>
F_SACH = "04 · Sách nguồn"

# Ngũ Hành sinh (生) + khắc (克) — deterministic, classical (Hoàng Đế Nội Kinh / phổ thông).
NGU_HANH = ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]
SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}

# 14 chính tinh → Ngũ Hành. Canonical từ Tử Vi Đẩu Số Toàn Thư (Phú Thái Vi, Trần Đoàn —
# Iron Rule #6, author_id=135). Cross-checked với prose hyphen-form trong tuvibonba_ngu_uan.json
# nơi có (Tử Vi→Thổ, Vũ Khúc→Kim, Thái Dương→Hỏa, Thái Âm→Thủy khớp).
STAR_ELEMENT_CANON = {
    "Tử Vi": "Thổ",
    "Thiên Cơ": "Mộc",
    "Thái Dương": "Hỏa",
    "Vũ Khúc": "Kim",
    "Thiên Đồng": "Thủy",
    "Liêm Trinh": "Hỏa",
    "Thiên Phủ": "Thổ",
    "Thái Âm": "Thủy",
    "Tham Lang": "Mộc",   # Mộc-Thủy lưỡng tính, lấy Mộc làm chủ (Toàn Thư)
    "Cự Môn": "Thủy",
    "Thiên Tướng": "Thủy",
    "Thiên Lương": "Thổ",
    "Thất Sát": "Kim",
    "Phá Quân": "Thủy",
}

# Sao chủ của 12 cung (cung → chính tinh nào "tọa thủ chủ đạo" theo nghĩa cố hữu) KHÔNG
# tồn tại tĩnh (sao quay theo lá số). Vì vậy KHÔNG sinh edge cung→sao cố định (sẽ là bịa).
# Edge sao→cung CHỈ sinh khi có dữ kiện THẬT (vd Mệnh chủ/Thân chủ). Bỏ qua để an toàn.

# Ngũ Uẩn (SN 22.79) — Iron Rule #9
NGU_UAN_5 = ["Sắc", "Thọ", "Tưởng", "Hành", "Thức"]

# Color groups theo phái (merge vào graph.json)
SCHOOL_COLORS = {
    "tu_vi": ("#tu_vi", 0xE3B341),          # vàng
    "mai_hoa": ("#mai_hoa", 0x4CAF50),       # lục
    "kinh-dich": ("#kinh-dich", 0x3F7FE0),   # lam
    "phat_hoc_nen": ("#phat_hoc_nen", 0xE06CA0),  # hồng sen
    "bat_tu": ("#bat_tu", 0xE8843C),         # cam
    "tu_binh_ba_tu": ("#tu_binh_ba_tu", 0xD2691E),  # cam đậm
    "ha-lac-xuan-cang": ("#ha-lac-xuan-cang", 0x9B59B6),  # tím
    "thieu-khang-tiet": ("#thieu-khang-tiet", 0x16A085),  # ngọc
    "nen-triet": ("#nen-triet", 0x95A5A6),   # xám (nền triết)
}
# colorGroup theo type
TYPE_COLORS = {
    "#sach": 0x7F8C8D,        # sách nguồn — xám đậm
    "#cach-cuc": 0xC0392B,    # cách cục — đỏ gạch
    "#chinh-tinh": 0xF1C40F,  # chính tinh — vàng sáng
}


# ───────────────────────── HELPERS ─────────────────────────
_BAD = re.compile(r'[\\/:*?"<>|#\[\]^]')


def safe_name(name: str) -> str:
    """Sanitize cho tên file Obsidian (giữ chữ Việt + Hán, bỏ ký tự cấm)."""
    s = _BAD.sub("", name or "")
    s = s.replace("\n", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:120] if s else "_unnamed"


def yaml_list(items) -> str:
    items = [str(x) for x in items if x is not None and str(x).strip()]
    if not items:
        return "[]"
    # quote each
    return "[" + ", ".join('"' + x.replace('"', "'") + '"' for x in items) + "]"


def wl(name: str) -> str:
    """wikilink an toàn (đã sanitize tên note đích)."""
    return f"[[{safe_name(name)}]]"


def _as_text(v) -> str:
    """Coerce field (str / list / None) → stripped text."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, list):
        return " ".join(_as_text(x) for x in v).strip()
    return str(v).strip()


def parse_json_field(raw):
    if not raw:
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def norm_passage(p) -> str:
    """Chuẩn hoá passage id (int hoặc 'corpus:p27') để so co-occurrence."""
    return str(p).strip()


# ───────────────────────── NOTE WRITER ─────────────────────────
class Vault:
    def __init__(self, out: Path):
        self.out = out
        self.notes = {}          # title -> dict(meta)
        self.aliases = {}        # alias -> title (for resolve)
        self.casefold = {}       # casefold(title) -> title (macOS case-insensitive FS)
        self.link_count = 0
        self.breakdown_nodes = {}
        self.breakdown_edges = {}

    def add(self, title, subdir, *, ntype, school=None, category=None,
            aliases=None, canonical_zh=None, body_lines=None, extra_tags=None,
            disambig=None):
        orig = safe_name(title)
        title = orig
        if title in self.notes:
            # exact dup (same name): keep first (idempotent within run)
            return self.notes[title]
        # macOS filesystem is case-insensitive: 'Khắc Ứng' vs 'Khắc ứng' collide on disk.
        # Disambiguate by suffixing a stable token so every concept keeps its own node.
        if title.casefold() in self.casefold:
            suffix = f" ({disambig})" if disambig is not None else " ·2"
            title = (orig + suffix)
            # extremely rare second-collision: keep bumping
            while title in self.notes or title.casefold() in self.casefold:
                suffix = suffix + "·"
                title = orig + suffix
        tags = []
        if extra_tags:
            tags += list(extra_tags)
        tags.append(f"#{ntype}")
        if school:
            tags.append(f"#{self._school_tag(school)}")
        # dedupe tags, preserve order
        tags = list(dict.fromkeys(tags))
        rec = {
            "title": title, "subdir": subdir, "ntype": ntype,
            "school": school, "category": category,
            "aliases": list(aliases or []), "zh": canonical_zh,
            "tags": tags, "body": list(body_lines or []),
            "links": [],  # collected outgoing [[..]] for counting
        }
        self.notes[title] = rec
        self.casefold[title.casefold()] = title
        for a in rec["aliases"]:
            a = (a or "").strip()
            if a and a != title:
                self.aliases.setdefault(safe_name(a), title)
        self.breakdown_nodes[ntype] = self.breakdown_nodes.get(ntype, 0) + 1
        return rec

    @staticmethod
    def _school_tag(school):
        return (school or "").replace("+", "_").replace(" ", "_")

    def resolve(self, name):
        """Trả tên note đích nếu name là title hoặc alias đã sinh; else None."""
        s = safe_name(name)
        if s in self.notes:
            return s
        if s in self.aliases:
            return self.aliases[s]
        return None

    def link(self, rec, target, edge_type):
        """Thêm 1 wikilink [[target]] vào rec NẾU target resolve được (không gãy)."""
        resolved = self.resolve(target)
        if resolved is None:
            return False
        rec["links"].append((resolved, edge_type))
        self.link_count += 1
        self.breakdown_edges[edge_type] = self.breakdown_edges.get(edge_type, 0) + 1
        return True

    def flush(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True, exist_ok=True)
        for rec in self.notes.values():
            self._write(rec)

    def _write(self, rec):
        d = self.out / rec["subdir"]
        d.mkdir(parents=True, exist_ok=True)
        fp = d / (rec["title"] + ".md")
        fm = ["---"]
        fm.append(f"type: {rec['ntype']}")
        if rec["school"]:
            fm.append(f"school: {rec['school']}")
        if rec["category"]:
            fm.append(f'category: "{rec["category"]}"')
        al = list(rec["aliases"])
        if rec["zh"] and rec["zh"] not in al:
            al.append(rec["zh"])
        if al:
            fm.append(f"aliases: {yaml_list(al)}")
        fm.append(f"tags: {yaml_list(rec['tags'])}")
        fm.append("---")
        out = "\n".join(fm) + "\n\n"
        out += f"# {rec['title']}"
        if rec["zh"]:
            out += f"  ·  {rec['zh']}"
        out += "\n\n"
        out += "\n".join(rec["body"]).strip()
        # group links by edge type
        if rec["links"]:
            by = {}
            for tgt, et in rec["links"]:
                by.setdefault(et, []).append(tgt)
            out += "\n\n"
            for et in sorted(by):
                uniq = sorted(set(by[et]))
                out += f"\n**{et}:** " + " · ".join(wl(t) for t in uniq) + "\n"
        fp.write_text(out.rstrip() + "\n", encoding="utf-8")


# ───────────────────────── BUILD ─────────────────────────
def main():
    V = Vault(OUT)

    # ===== 1. NỀN TRIẾT =====
    triet_nodes = {
        "Âm Dương": ("Hai khí đối lập-bổ sung, gốc của mọi biến hoá. Giao thoa sinh vạn vật.", ["陰陽"]),
        "Ngũ Hành": ("Kim · Mộc · Thủy · Hỏa · Thổ — 5 trạng thái vận động, sinh-khắc-chế-hoá.", ["五行"]),
        "Ngũ Uẩn": ("Sắc–Thọ–Tưởng–Hành–Thức (SN 22.79) — bản đồ tiến trình tâm. Iron Rule #9.", ["五蘊", "Năm uẩn"]),
        "Tứ Diệu Đế": ("Khổ–Tập–Diệt–Đạo (SN 56.11) — 4 động từ soi tâm. Iron Rule #9.", ["四聖諦"]),
        "Bát Chánh Đạo": ("8 chi đạo: chánh kiến…chánh định — phác đồ hành động (Đạo đế).", ["八正道"]),
        "Duyên Khởi": ("Pháp tuỳ duyên mà sinh; không chủ thể tĩnh để đoán. Iron Rule #9.", ["緣起", "Duyên sinh"]),
        "Vô Ngã": ("Không có cái ta cố định — lý do triết học KHÔNG predict. Iron Rule #9.", ["無我"]),
    }
    for name, (note, al) in triet_nodes.items():
        V.add(name, F_TRIET, ntype="nen-triet", school="nen-triet",
              category="nền triết", aliases=al, body_lines=[note], extra_tags=["#nền-triết"])
    # 5 hành
    HANH_ZH = {"Kim": "金", "Mộc": "木", "Thủy": "水", "Hỏa": "火", "Thổ": "土"}
    for h in NGU_HANH:
        V.add(h, F_TRIET, ntype="hanh", school="nen-triet", category="ngũ hành",
              canonical_zh=HANH_ZH[h], body_lines=[f"Hành {h} — một trong Ngũ Hành."],
              extra_tags=["#ngũ-hành"])
    # 5 uẩn
    UAN_ZH = {"Sắc": "色", "Thọ": "受", "Tưởng": "想", "Hành": "行", "Thức": "識"}
    for u in NGU_UAN_5:
        V.add(f"Uẩn {u}", F_TRIET, ntype="uan", school="nen-triet", category="ngũ uẩn",
              canonical_zh=UAN_ZH[u],
              body_lines=[f"Uẩn **{u}** — một trong Ngũ Uẩn (tiến trình tâm)."],
              extra_tags=["#ngũ-uẩn"])

    # ===== 2. PHÁI HUB (MOC) từ distinct school =====
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    schools = [r["school"] for r in con.execute(
        "select school, count(*) n from concept_index "
        "where school is not null and school != '' group by school order by n desc")]
    phai_title = {}
    for sch in schools:
        n = con.execute("select count(*) c from concept_index where school=?", (sch,)).fetchone()["c"]
        t = f"Phái · {sch}"
        phai_title[sch] = t
        V.add(t, F_PHAI, ntype="phai", school=sch, category="phái",
              body_lines=[f"**MOC (Map of Content)** — hub phái `{sch}` ({n} khái niệm.)",
                          "", "Các khái niệm thuộc phái này backlink về đây."],
              extra_tags=["#phái"])

    # ===== 4-bis. SÁCH NGUỒN: distinct corpora (first_seen_corpus) = nguồn cạnh THẬT =====
    # Bổ sung title đẹp từ books.json nếu khớp.
    books_meta = {}
    try:
        bj = json.loads(BOOKS.read_text(encoding="utf-8"))
        for bk in bj.get("books", []):
            if bk.get("deleted"):
                continue
            books_meta[bk.get("book_id")] = bk
    except Exception:
        pass
    corpora_rows = con.execute(
        "select first_seen_corpus c, count(*) n from concept_index "
        "where first_seen_corpus is not null and first_seen_corpus!='' "
        "group by first_seen_corpus order by n desc").fetchall()
    corpus_title = {}
    for r in corpora_rows:
        cid = r["c"]
        meta = books_meta.get(cid)
        nice = meta.get("title_vi") if meta and meta.get("title_vi") else cid
        if nice == cid:
            # try fuzzy: book whose id startswith corpus stem
            for bid, m in books_meta.items():
                if m.get("title_vi") and (cid in bid or bid in cid):
                    nice = m["title_vi"]
                    break
        t = f"Sách · {safe_name(nice)}"
        corpus_title[cid] = t
        sch = (meta or {}).get("school") or None
        body = [f"Nguồn (corpus) `{cid}` — {r['n']} khái niệm trích từ đây."]
        if meta:
            if meta.get("hanzi_title"):
                body.append(f"Hán văn: {meta['hanzi_title']}")
            if meta.get("author"):
                body.append(f"Tác giả: {meta['author']}")
        V.add(t, F_SACH, ntype="sach", school=sch, category="sách nguồn",
              aliases=[cid], body_lines=body, extra_tags=["#sách"])

    # ===== 3. 14 CHÍNH TINH + 12 CUNG =====
    nu = json.loads(NGU_UAN.read_text(encoding="utf-8"))["records"]
    star_rec = {r["sao"]: r for r in nu if r.get("sao")}
    star_title = {}
    for s in CHINH_TINH_NAMES:
        rec = star_rec.get(s, {})
        ele = STAR_ELEMENT_CANON.get(s)
        body = []
        tg = _as_text(rec.get("tom_gon"))
        if tg:
            body.append(tg)
        gt = _as_text(rec.get("goc_tham"))
        if gt:
            body.append("")
            body.append(f"**Gốc tham:** {gt[:400]}")
        if ele:
            body.append("")
            body.append(f"**Ngũ Hành:** {ele}")
        t = f"Sao · {s}"
        star_title[s] = t
        V.add(t, F_TV_TINH, ntype="chinh-tinh", school="tu_vi", category="sao",
              aliases=[s], body_lines=body or [f"Chính tinh {s}."],
              extra_tags=["#chinh-tinh"])
    cung_title = {}
    for c in PALACE_NAMES:
        t = f"Cung · {c}"
        cung_title[c] = t
        V.add(t, F_TV_CUNG, ntype="cung", school="tu_vi", category="cung",
              aliases=[c], body_lines=[f"Cung **{c}** — một trong 12 cung địa bàn Tử Vi."],
              extra_tags=["#cung"])

    # ===== 6. CÁCH CỤC =====
    cc = json.loads(CACH_CUC.read_text(encoding="utf-8"))
    cach_recs = []
    for idx, (k, v) in enumerate(cc.items()):
        ten = v.get("ten") or k
        t = f"Cách · {safe_name(ten)}"
        body = []
        if v.get("cap_do"):
            body.append(f"**Cấp độ:** {v['cap_do']}")
        if v.get("y_nghia"):
            body.append("")
            body.append(v["y_nghia"])
        rec = V.add(t, F_TV_CACH, ntype="cach-cuc", school="tu_vi", category="cách cục",
                    body_lines=body or [ten], extra_tags=["#cách-cục"],
                    disambig=f"c{idx}")
        cach_recs.append((rec["title"], ten + " " + (v.get("dieu_kien") or "")))

    # ===== 4. 3641 CONCEPT (concept_index) =====
    concept_rows = con.execute(
        "select concept_id, canonical_vi, canonical_zh, aliases, mentioned_in_passages, "
        "short_note, first_seen_corpus, corpora, school, category from concept_index").fetchall()
    concept_title = {}
    concept_passages = {}   # title -> set(passage)
    for r in concept_rows:
        vi = (r["canonical_vi"] or "").strip()
        if not vi:
            continue
        al = parse_json_field(r["aliases"])
        body = []
        if r["short_note"]:
            body.append(r["short_note"])
        # disambig by concept_id so case-insensitive FS collisions keep distinct nodes
        rec = V.add(vi, f"{F_CONCEPT}/{r['school'] or 'khac'}", ntype="khai-niem",
                    school=r["school"], category=r["category"], aliases=al,
                    canonical_zh=r["canonical_zh"], body_lines=body or [vi],
                    disambig=f"id{r['concept_id']}")
        # map to ACTUAL written title (may be suffixed on collision)
        concept_title[r["concept_id"]] = rec["title"]
        ps = set(norm_passage(p) for p in parse_json_field(r["mentioned_in_passages"]))
        concept_passages[r["concept_id"]] = ps

    # ============================================================
    #                       CẠNH (EDGES)
    # ============================================================

    # E1. concept → [[phái]]  (school)
    for r in concept_rows:
        cid = r["concept_id"]
        if cid not in concept_title:
            continue
        rec = V.notes.get(concept_title[cid])
        sch = r["school"]
        if rec and sch in phai_title:
            V.link(rec, phai_title[sch], "thuộc-phái")

    # E2. concept → [[sách nguồn]]  (first_seen_corpus + corpora)
    for r in concept_rows:
        cid = r["concept_id"]
        if cid not in concept_title:
            continue
        rec = V.notes.get(concept_title[cid])
        if not rec:
            continue
        srcs = set()
        if r["first_seen_corpus"]:
            srcs.add(r["first_seen_corpus"])
        for cp in parse_json_field(r["corpora"]):
            srcs.add(cp)
        for cid_src in srcs:
            if cid_src in corpus_title:
                V.link(rec, corpus_title[cid_src], "trích-từ-sách")

    # E3. concept ↔ concept co-occurrence (chung mentioned_in_passages, CAP top-8)
    # Build inverted index passage -> [concept_id] (only passages shared by >=2)
    inv = {}
    for cid, ps in concept_passages.items():
        for p in ps:
            inv.setdefault(p, []).append(cid)
    co = {}  # frozenset pair -> shared count
    for p, cids in inv.items():
        if len(cids) < 2 or len(cids) > 60:  # skip hairball passages
            continue
        cids = sorted(set(cids))
        for i in range(len(cids)):
            for j in range(i + 1, len(cids)):
                key = (cids[i], cids[j])
                co[key] = co.get(key, 0) + 1
    # per-concept top-8 neighbors by shared count
    neigh = {}
    for (a, b), w in co.items():
        neigh.setdefault(a, []).append((b, w))
        neigh.setdefault(b, []).append((a, w))
    linked_pairs = set()
    for cid, lst in neigh.items():
        if cid not in concept_title:
            continue
        rec = V.notes.get(concept_title[cid])
        if not rec:
            continue
        top = sorted(lst, key=lambda x: (-x[1], x[0]))[:8]
        for other, w in top:
            if other not in concept_title:
                continue
            pair = tuple(sorted((cid, other)))
            if pair in linked_pairs:
                continue
            linked_pairs.add(pair)
            tgt = concept_title[other]
            if V.link(rec, tgt, "đồng-hiện"):
                # reciprocal
                orec = V.notes.get(concept_title[other])
                if orec:
                    V.link(orec, concept_title[cid], "đồng-hiện")

    # E4. Ngũ Hành sinh-khắc (deterministic)
    for h in NGU_HANH:
        rec = V.notes[h]
        V.link(rec, SINH[h], "sinh →")
        V.link(rec, KHAC[h], "khắc →")

    # E5. sao → [[hành]] (ngũ hành chính tinh)
    for s in CHINH_TINH_NAMES:
        ele = STAR_ELEMENT_CANON.get(s)
        rec = V.notes.get(star_title[s])
        if rec and ele:
            V.link(rec, ele, "hành của sao")

    # E6. cách cục → [[sao cấu thành]] (chính tinh xuất hiện trong tên/điều kiện)
    for t, text in cach_recs:
        rec = V.notes.get(t)
        if not rec:
            continue
        for s in CHINH_TINH_NAMES:
            if s in text:
                V.link(rec, star_title[s], "sao cấu thành")

    # E7. Nền triết nội bộ
    #   Ngũ Hành hub → 5 hành
    rec_nh = V.notes["Ngũ Hành"]
    for h in NGU_HANH:
        V.link(rec_nh, h, "gồm hành")
    #   Ngũ Uẩn hub → 5 uẩn
    rec_uan = V.notes["Ngũ Uẩn"]
    for u in NGU_UAN_5:
        V.link(rec_uan, f"Uẩn {u}", "gồm uẩn")
    #   Thọ → Hành (khe tỉnh thức SN 12.2) — chánh niệm chen vào
    V.link(V.notes["Uẩn Thọ"], "Uẩn Hành", "khe Thọ→Hành (tỉnh thức)")
    #   Bát Chánh Đạo → Tứ Diệu Đế (là Đạo đế); Tứ Diệu Đế → Duyên Khởi; Duyên Khởi → Vô Ngã
    V.link(V.notes["Bát Chánh Đạo"], "Tứ Diệu Đế", "là Đạo đế của")
    V.link(V.notes["Tứ Diệu Đế"], "Duyên Khởi", "nương lý")
    V.link(V.notes["Duyên Khởi"], "Vô Ngã", "hàm ý")
    V.link(V.notes["Duyên Khởi"], "Ngũ Uẩn", "vận hành qua")
    #   Âm Dương → Ngũ Hành
    V.link(V.notes["Âm Dương"], "Ngũ Hành", "phân hoá thành")

    # E8. sao → khái niệm gốc-tham: nếu trong goc_tham có tên 1 concept đã sinh → link.
    #   (CHỈ link khi tên concept khớp NGUYÊN VĂN trong goc_tham — truy được về data.)
    concept_names = set(n for n, rec in V.notes.items() if rec["ntype"] == "khai-niem" and len(n) >= 3)
    # build quick lookup of concept names appearing
    for s in CHINH_TINH_NAMES:
        rec_s = V.notes.get(star_title[s])
        gt = _as_text(star_rec.get(s, {}).get("goc_tham"))
        if not rec_s or not gt:
            continue
        hits = 0
        for cn in concept_names:
            if cn != s and len(cn) >= 4 and cn in gt:
                if V.link(rec_s, cn, "gốc-tham nhắc"):
                    hits += 1
            if hits >= 5:
                break

    # ===== README =====
    readme = build_readme(V)
    V.add("_README — Mạng Tri Thức YI", ".", ntype="readme",
          body_lines=[readme], extra_tags=["#readme"])

    # write all notes
    V.flush()

    # ===== merge graph.json colorGroups =====
    merge_graph_colors()

    # ===== SELF-TEST =====
    n_notes = len(V.notes)
    n_links = V.link_count
    passed, checks = self_test(V, n_notes, n_links)

    result = {
        "so_note": n_notes,
        "so_link": n_links,
        "passed": passed,
        "theo_loai": {
            "node": dict(sorted(V.breakdown_nodes.items(), key=lambda x: -x[1])),
            "edge": dict(sorted(V.breakdown_edges.items(), key=lambda x: -x[1])),
        },
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def build_readme(V) -> str:
    lines = [
        "Đồ thị tri thức (knowledge graph) sinh tự động từ wiki YI-Chronos.",
        "Sinh bởi `scripts/build_obsidian_graph.py` — deterministic, idempotent.",
        "",
        "## Cách đọc graph",
        "- Mở **Graph view** (Ctrl/Cmd+G). Mỗi chấm = 1 note. Mỗi đường = 1 quan hệ THẬT.",
        "- Bật **Groups** trong panel để thấy màu theo phái.",
        "- Folder `00 · Nền triết` = gốc Âm Dương / Ngũ Hành / Ngũ Uẩn / Phật học.",
        "- Folder `01 · Phái` = hub MOC mỗi trường phái (backlink hội tụ).",
        "- Folder `02 · Tử Vi` = 14 chính tinh + 12 cung + cách cục.",
        "- Folder `03 · Khái niệm/<phái>` = 3641 khái niệm wiki.",
        "- Folder `04 · Sách nguồn` = corpus gốc mỗi khái niệm trích ra.",
        "",
        "## Chú giải màu (theo phái)",
    ]
    for sch, (tag, col) in SCHOOL_COLORS.items():
        lines.append(f"- `{tag}` → #{col:06X} — {sch}")
    lines += [
        "",
        "## Nguồn mỗi loại cạnh (KHÔNG bịa — truy được về data)",
        "- **thuộc-phái**: concept.school → hub phái.",
        "- **trích-từ-sách**: concept.first_seen_corpus + corpora → sách nguồn.",
        "- **đồng-hiện**: 2 concept chung `mentioned_in_passages` (CAP top-8/concept).",
        "- **sinh → / khắc →**: vòng Ngũ Hành cổ điển (deterministic).",
        "- **hành của sao**: 14 chính tinh → Ngũ Hành (Toàn Thư, cross-check prose ngũ_uẩn).",
        "- **sao cấu thành**: cách cục → chính tinh xuất hiện trong tên/điều kiện.",
        "- **gốc-tham nhắc**: sao → concept có tên khớp nguyên văn trong trường `goc_tham`.",
        "- **nền triết nội bộ**: Ngũ Uẩn→5 uẩn, khe Thọ→Hành, Bát Chánh Đạo→Tứ Diệu Đế…",
    ]
    return "\n".join(lines)


def merge_graph_colors():
    """Merge (KHÔNG clobber) colorGroups vào .obsidian/graph.json."""
    if not GRAPH_JSON.exists():
        return
    try:
        g = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except Exception:
        return
    existing = g.get("colorGroups", []) or []
    # index by query to avoid dup
    by_query = {cg.get("query"): cg for cg in existing if isinstance(cg, dict)}
    def add(query, color_int):
        by_query[query] = {"query": f"tag:{query}", "color": {"a": 1, "rgb": color_int}} \
            if not query.startswith("tag:") else {"query": query, "color": {"a": 1, "rgb": color_int}}
    for sch, (tag, col) in SCHOOL_COLORS.items():
        q = f"tag:{tag}"
        by_query[q] = {"query": q, "color": {"a": 1, "rgb": col}}
    for tag, col in TYPE_COLORS.items():
        q = f"tag:{tag}"
        by_query[q] = {"query": q, "color": {"a": 1, "rgb": col}}
    g["colorGroups"] = list(by_query.values())
    GRAPH_JSON.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")


def self_test(V, n_notes, n_links):
    import random
    checks = {}
    checks["notes_gt_4000"] = n_notes > 4000
    checks["links_gt_10000"] = n_links > 10000
    # 5 random links resolve
    all_links = []
    for rec in V.notes.values():
        for tgt, et in rec["links"]:
            all_links.append(tgt)
    rng = random.Random(42)
    sample = rng.sample(all_links, min(5, len(all_links))) if all_links else []
    resolved_ok = all(t in V.notes for t in sample)
    checks["random5_resolve"] = resolved_ok
    checks["random5_sample"] = sample
    passed = checks["notes_gt_4000"] and checks["links_gt_10000"] and resolved_ok
    return passed, checks


if __name__ == "__main__":
    main()
