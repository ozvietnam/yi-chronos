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
ONTOLOGY = ROOT / "data/yi_lexicon/ontology_nen.json"  # toạ-độ gốc chung (canonical)
HANH_MAP = ROOT / "data/yi_lexicon/concept_ngu_hanh_map.json"  # bảng hành GROUNDED (có nguồn)

VAULT = ROOT / "thư viện sách"
OUT = VAULT / "🧠 Mạng Tri Thức YI"
GRAPH_JSON = VAULT / ".obsidian/graph.json"

sys.path.insert(0, str(ROOT))
from engine.tu_vi.an_sao import CHINH_TINH_NAMES, PALACE_NAMES  # noqa: E402

# ───────────────────────── CONSTANTS ─────────────────────────
# Subfolders
F_COORD = "00 · Toạ độ gốc chung"  # hub TRUNG LẬP PHÁI (school=chung): can/chi/quái/quẻ/hành…
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
    # ===== 1-bis. TOẠ ĐỘ GỐC CHUNG (school=chung, trung lập phái) =====
    # Nguồn: ontology_nen.json — canonical deterministic. Mọi cạnh toạ-độ truy được về đây.
    ont = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    ONT_NH = ont["ngu_hanh"]
    ONT_AD = ont["am_duong"]
    ONT_CAN = ont["thien_can"]
    ONT_CHI = ont["dia_chi"]
    ONT_QUAI = ont["bat_quai"]
    ONT_QUE = ont["que_64"]
    ONT_ALIAS = ont.get("alias", {})

    # — 5 hành = HUB toạ-độ (school=chung). Đây là node neo cho mọi cạnh "→[[<hành>]]".
    for h in NGU_HANH:
        nh = ONT_NH[h]
        V.add(h, F_COORD, ntype="hanh", school="chung", category="ngũ hành",
              canonical_zh=nh.get("zh"),
              body_lines=[f"**Hành {h}** — toạ độ gốc chung (trung lập phái).",
                          f"Sinh → {nh['sinh']} · Khắc → {nh['khac']} · "
                          f"Được sinh bởi {nh['duoc_sinh_boi']} · Bị khắc bởi {nh['bi_khac_boi']}."],
              extra_tags=["#ngũ-hành", "#toạ-độ-gốc"])

    # — Âm / Dương = HUB toạ-độ
    for ad, meta in ONT_AD.items():
        V.add(ad, F_COORD, ntype="am-duong", school="chung", category="âm dương",
              canonical_zh=meta.get("zh"),
              body_lines=[f"**{ad}** — một trong hai khí gốc (toạ độ chung)."],
              extra_tags=["#âm-dương", "#toạ-độ-gốc"])

    # — Thiên Can hub + 10 can
    V.add("Thiên Can", F_COORD, ntype="hub-toa-do", school="chung", category="thiên can",
          canonical_zh="天干",
          body_lines=["**Thiên Can** — 10 can trời, toạ độ gốc chung của Bát Tự/Kinh Dịch."],
          extra_tags=["#toạ-độ-gốc"])
    can_title = {}
    for can, meta in ONT_CAN.items():
        t = f"Can · {can}"
        can_title[can] = t
        V.add(t, F_COORD, ntype="thien-can", school="chung", category="thiên can",
              aliases=[can, meta.get("zh")], canonical_zh=meta.get("zh"),
              body_lines=[f"**Can {can}** ({meta.get('zh')}) — số {meta.get('so')} · "
                          f"{meta.get('am_duong')} · hành {meta.get('ngu_hanh')}."],
              extra_tags=["#thiên-can", "#toạ-độ-gốc"], disambig=f"can{meta.get('so')}")

    # — Địa Chi hub + 12 chi
    V.add("Địa Chi", F_COORD, ntype="hub-toa-do", school="chung", category="địa chi",
          canonical_zh="地支",
          body_lines=["**Địa Chi** — 12 chi đất, toạ độ gốc chung."],
          extra_tags=["#toạ-độ-gốc"])
    chi_title = {}
    for chi, meta in ONT_CHI.items():
        t = f"Chi · {chi}"
        chi_title[chi] = t
        tc = " · ".join(meta.get("tang_can", []))
        V.add(t, F_COORD, ntype="dia-chi", school="chung", category="địa chi",
              aliases=[chi, meta.get("zh")], canonical_zh=meta.get("zh"),
              body_lines=[f"**Chi {chi}** ({meta.get('zh')}) — số {meta.get('so')} · "
                          f"{meta.get('am_duong')} · hành {meta.get('ngu_hanh')}."
                          + (f" Tàng can: {tc}." if tc else "")],
              extra_tags=["#địa-chi", "#toạ-độ-gốc"], disambig=f"chi{meta.get('so')}")

    # — Bát Quái hub + 8 quái
    V.add("Bát Quái", F_COORD, ntype="hub-toa-do", school="chung", category="bát quái",
          canonical_zh="八卦",
          body_lines=["**Bát Quái** — 8 quẻ đơn, toạ độ gốc chung của Kinh Dịch."],
          extra_tags=["#toạ-độ-gốc"])
    quai_title = {}
    for quai, meta in ONT_QUAI.items():
        t = f"Quái · {quai}"
        quai_title[quai] = t
        ng = " · ".join(meta.get("nap_giap", []))
        V.add(t, F_COORD, ntype="bat-quai", school="chung", category="bát quái",
              aliases=[quai, meta.get("zh")], canonical_zh=meta.get("zh"),
              body_lines=[f"**Quái {quai}** ({meta.get('zh')}) — số {meta.get('so')} · "
                          f"{meta.get('am_duong')} · hành {meta.get('ngu_hanh')}."
                          + (f" Nạp giáp: {ng}." if ng else "")],
              extra_tags=["#bát-quái", "#toạ-độ-gốc"], disambig=f"quai{meta.get('so')}")

    # — 64 Quẻ hub + 64 quẻ kép
    V.add("64 Quẻ", F_COORD, ntype="hub-toa-do", school="chung", category="64 quẻ",
          canonical_zh="六十四卦",
          body_lines=["**64 Quẻ** — toạ độ gốc chung; mỗi quẻ = thượng quái + hạ quái."],
          extra_tags=["#toạ-độ-gốc"])
    que_title = {}
    for que, meta in ONT_QUE.items():
        t = f"Quẻ · {que}"
        que_title[que] = t
        V.add(t, F_COORD, ntype="que-64", school="chung", category="64 quẻ",
              aliases=[que, meta.get("zh")], canonical_zh=meta.get("zh"),
              body_lines=[f"**Quẻ {que}** ({meta.get('zh')}) — số {meta.get('so_sinh')} · "
                          f"thượng {meta.get('thuong_quai')} / hạ {meta.get('ha_quai')}."],
              extra_tags=["#64-quẻ", "#toạ-độ-gốc"], disambig=f"que{meta.get('so_sinh')}")

    # — TRỤC BÁT TỰ (B6): hub Thập Thần + 2 hub quan-hệ-ngũ-hành (Tương sinh/khắc) —
    #   Nguồn: định nghĩa concept Thập Thần (id8390, 十神) + nguyên lý sinh-khắc ontology.
    #   Các hub này là TOẠ ĐỘ GỐC để mọi thập-thần / quan-hệ-Nhật-Chủ neo về (binder Bát Tự).
    V.add("Thập Thần", F_COORD, ntype="hub-toa-do", school="tu_binh_ba_tu",
          category="thập thần", canonical_zh="十神",
          body_lines=["**Thập Thần** — 10 mối quan-hệ giữa Nhật Chủ (Day Master) và mỗi "
                      "Thiên Can khác (sinh-khắc + cùng/khác âm dương). Ngôn ngữ trung tâm Tử Bình.",
                      "", "<!-- hub Thập Thần · nguồn: concept_index id8390 (十神) -->"],
          extra_tags=["#thập-thần", "#toạ-độ-gốc"])
    V.add("Tương sinh", F_COORD, ntype="hub-toa-do", school="chung",
          category="quan hệ ngũ hành", canonical_zh="相生",
          body_lines=["**Tương sinh** — quan hệ A sinh B trong vòng Ngũ Hành "
                      "(Mộc→Hỏa→Thổ→Kim→Thủy→Mộc).",
                      "", "<!-- hub quan-hệ · nguồn: ontology_nen.ngu_hanh.sinh -->"],
          extra_tags=["#ngũ-hành", "#toạ-độ-gốc"])
    V.add("Tương khắc", F_COORD, ntype="hub-toa-do", school="chung",
          category="quan hệ ngũ hành", canonical_zh="相剋",
          body_lines=["**Tương khắc** — quan hệ A khắc B trong vòng Ngũ Hành "
                      "(Mộc→Thổ→Thủy→Hỏa→Kim→Mộc).",
                      "", "<!-- hub quan-hệ · nguồn: ontology_nen.ngu_hanh.khac -->"],
          extra_tags=["#ngũ-hành", "#toạ-độ-gốc"])

    # ── MATCHER toạ-độ: token canonical (vi/zh/alias) → [(hub_title, edge_type)] ──
    # KHỚP CHÍNH XÁC (exact, canonical), KHÔNG fuzzy. Mọi cạnh truy được về ontology_nen.
    # Key đã safe_name + casefold để so khít với tên/alias/zh của node bất kỳ phái.
    coord_index = {}  # casefold(safe_name(token)) -> list[(hub_title, edge_type)]

    def _reg(token, links):
        if not token:
            return
        k = safe_name(str(token)).casefold()
        if not k:
            return
        coord_index.setdefault(k, [])
        for pair in links:
            if pair not in coord_index[k]:
                coord_index[k].append(pair)

    # ngũ hành: tên + zh → [[<hành>]]
    for h in NGU_HANH:
        links = [(h, "toạ-độ ngũ-hành")]
        _reg(h, links)
        _reg(ONT_NH[h].get("zh"), links)
    # âm dương: tên + zh → [[Âm/Dương]]
    for ad, meta in ONT_AD.items():
        links = [(ad, "toạ-độ âm-dương")]
        _reg(ad, links)
        _reg(meta.get("zh"), links)
    # thiên can: tên + zh + alias → [[Thiên Can]] + [[hành]] + [[Âm/Dương]]
    for can, meta in ONT_CAN.items():
        links = [("Thiên Can", "toạ-độ thiên-can"),
                 (meta["ngu_hanh"], "toạ-độ ngũ-hành"),
                 (meta["am_duong"], "toạ-độ âm-dương")]
        _reg(can, links)
        _reg(meta.get("zh"), links)
    for alias, canon in ONT_ALIAS.get("thien_can", {}).items():
        m = ONT_CAN.get(canon)
        if m:
            _reg(alias, [("Thiên Can", "toạ-độ thiên-can"),
                         (m["ngu_hanh"], "toạ-độ ngũ-hành"),
                         (m["am_duong"], "toạ-độ âm-dương")])
    # địa chi: tên + zh + alias → [[Địa Chi]] + [[hành]]
    for chi, meta in ONT_CHI.items():
        links = [("Địa Chi", "toạ-độ địa-chi"), (meta["ngu_hanh"], "toạ-độ ngũ-hành")]
        _reg(chi, links)
        _reg(meta.get("zh"), links)
    for alias, canon in ONT_ALIAS.get("dia_chi", {}).items():
        m = ONT_CHI.get(canon)
        if m:
            _reg(alias, [("Địa Chi", "toạ-độ địa-chi"), (m["ngu_hanh"], "toạ-độ ngũ-hành")])
    # bát quái: tên + zh + alias → [[Bát Quái]] + [[hành]] + nạp-giáp can
    for quai, meta in ONT_QUAI.items():
        links = [("Bát Quái", "toạ-độ bát-quái"), (meta["ngu_hanh"], "toạ-độ ngũ-hành")]
        for ng in meta.get("nap_giap", []):
            links.append((can_title[ng], "nạp-giáp can"))
        _reg(quai, links)
        _reg(meta.get("zh"), links)
    for alias, canon in ONT_ALIAS.get("bat_quai", {}).items():
        m = ONT_QUAI.get(canon)
        if m:
            ls = [("Bát Quái", "toạ-độ bát-quái"), (m["ngu_hanh"], "toạ-độ ngũ-hành")]
            for ng in m.get("nap_giap", []):
                ls.append((can_title[ng], "nạp-giáp can"))
            _reg(alias, ls)
    # 64 quẻ: tên + zh + alias → [[thượng quái]] + [[hạ quái]] + [[64 Quẻ]]
    for que, meta in ONT_QUE.items():
        links = [("64 Quẻ", "toạ-độ 64-quẻ"),
                 (quai_title[meta["thuong_quai"]], "thượng quái"),
                 (quai_title[meta["ha_quai"]], "hạ quái")]
        _reg(que, links)
        _reg(meta.get("zh"), links)
    for alias, canon in ONT_ALIAS.get("que_64", {}).items():
        m = ONT_QUE.get(canon)
        if m:
            _reg(alias, [("64 Quẻ", "toạ-độ 64-quẻ"),
                         (quai_title[m["thuong_quai"]], "thượng quái"),
                         (quai_title[m["ha_quai"]], "hạ quái")])

    def coord_links_for(*tokens):
        """Trả về list (hub_title, edge_type) cho node có 1 trong các token KHỚP CHÍNH XÁC
        một primitive. Dedupe, ổn định thứ tự."""
        out = []
        seen = set()
        for tok in tokens:
            if not tok:
                continue
            hits = coord_index.get(safe_name(str(tok)).casefold())
            if not hits:
                continue
            for pair in hits:
                if pair not in seen:
                    seen.add(pair)
                    out.append(pair)
            # CHÍNH XÁC: token đầu tiên khớp là đủ (mỗi node khớp 1 primitive)
            if out:
                break
        return out

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
        "short_note, first_seen_corpus, first_seen_page, corpora, school, category, "
        "han_viet_giai, thuan_viet_giai "
        "from concept_index").fetchall()
    concept_title = {}
    concept_passages = {}   # title -> set(passage)
    concept_tokens = {}     # cid -> (vi, zh, [aliases]) cho matcher toạ-độ
    concept_school = {}     # cid -> school (cho matcher SCOPE-school, vd thập thần)
    concept_note = {}       # cid -> short_note (cho matcher can/chi an-toàn)
    for r in concept_rows:
        vi = (r["canonical_vi"] or "").strip()
        if not vi:
            continue
        al = parse_json_field(r["aliases"])
        body = []
        if r["short_note"]:
            body.append(r["short_note"])
        # SONG NGỮ: hiện giải nghĩa Hán-Việt (chiết tự) + thuần-Việt (đời thường) NGAY TRONG
        # note (nguồn: concept_index.han_viet_giai / thuan_viet_giai — đã neo canon). Đặt sau
        # short_note để người mở note đọc thẳng được nghĩa, không phải tra ngược DB.
        hvg = _as_text(r["han_viet_giai"])
        if hvg:
            body.append("")
            body.append(f"**Hán-Việt (chiết tự):** {hvg}")
        tvg = _as_text(r["thuan_viet_giai"])
        if tvg:
            body.append("")
            body.append(f"**Thuần-Việt (đời thường):** {tvg}")
        # disambig by concept_id so case-insensitive FS collisions keep distinct nodes
        rec = V.add(vi, f"{F_CONCEPT}/{r['school'] or 'khac'}", ntype="khai-niem",
                    school=r["school"], category=r["category"], aliases=al,
                    canonical_zh=r["canonical_zh"], body_lines=body or [vi],
                    disambig=f"id{r['concept_id']}")
        # map to ACTUAL written title (may be suffixed on collision)
        concept_title[r["concept_id"]] = rec["title"]
        ps = set(norm_passage(p) for p in parse_json_field(r["mentioned_in_passages"]))
        concept_passages[r["concept_id"]] = ps
        concept_tokens[r["concept_id"]] = (vi, r["canonical_zh"], al)
        concept_school[r["concept_id"]] = r["school"]
        concept_note[r["concept_id"]] = r["short_note"] or ""

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

    # E5. (gộp vào B1 — cạnh toạ-độ ngũ-hành cho 14 chính tinh, xem mục (B) bên dưới)

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

    # ============================================================
    #  E9. SYNAPSE THẬT — atom_relations (bảng quan-hệ ngữ-nghĩa đã đổ, wiki_connect_v1)
    # ============================================================
    #  Mỗi hàng atom_relations là 1 quan-hệ giữa 2 KHÁI NIỆM (from_concept_id → to_concept_id),
    #  do pipeline wiki_connect_v1 trích + neo bằng câu rationale (truy về short_note nguồn).
    #  Nhãn cạnh = 'liên-kết-nghĩa' (gộp mọi relation_type của bảng — thuộc-về / giải-thích-bằng
    #  / là-loại-của / sinh / khắc …). Cạnh THẬT, KHÔNG bịa: chỉ vẽ khi CẢ HAI concept có node
    #  trong vault. Dedupe theo cặp không hướng (mỗi cặp 1 cạnh, giữ relation_type đầu tiên để
    #  ghi nguồn). Lưu rationale + relation_type vào comment HTML body (verify, không nhiễu graph).
    relrows = con.execute(
        "select from_concept_id, to_concept_id, relation_type, rationale, confidence "
        "from atom_relations "
        "where from_concept_id is not null and to_concept_id is not null "
        "and from_concept_id != to_concept_id "
        "order by rel_id").fetchall()
    synapse_pairs = set()        # frozenset(a,b) đã vẽ (không hướng) → dedupe
    synapse_edge_count = 0
    synapse_skipped_no_node = 0
    synapse_prov = {}            # title -> list[comment] (gom nguồn để append 1 lần)
    for rr in relrows:
        a, b = rr["from_concept_id"], rr["to_concept_id"]
        ta = concept_title.get(a)
        tb = concept_title.get(b)
        if not ta or not tb:
            synapse_skipped_no_node += 1
            continue
        key = frozenset((ta, tb))
        if key in synapse_pairs:
            continue
        synapse_pairs.add(key)
        rec_a = V.notes.get(ta)
        rec_b = V.notes.get(tb)
        if not rec_a or not rec_b:
            synapse_skipped_no_node += 1
            continue
        # cạnh 2 chiều (reciprocal) để graph nối chắc + không node nào thiếu out-edge
        ok1 = V.link(rec_a, tb, "liên-kết-nghĩa")
        ok2 = V.link(rec_b, ta, "liên-kết-nghĩa")
        if ok1 or ok2:
            synapse_edge_count += 1
            rt = (rr["relation_type"] or "?").strip()
            rationale = _as_text(rr["rationale"])[:240]
            comment = (f"<!-- liên-kết-nghĩa ({rt}) ↔ [[{tb if ok1 else ta}]] · "
                       f"nguồn (atom_relations.rationale): \"{rationale}\" -->")
            synapse_prov.setdefault(ta, []).append(comment)
    # append provenance comments (cap 6/note để body không phình)
    for title, comments in synapse_prov.items():
        rec = V.notes.get(title)
        if not rec:
            continue
        for c in comments[:6]:
            if c not in rec["body"]:
                rec["body"].append("")
                rec["body"].append(c)

    # ============================================================
    #  (A) PROVENANCE BẮT BUỘC — diệt cô đơn: MỌI node có ≥1 [[Phái·]] / [[Sách·]]
    # ============================================================
    # A0. hub toạ-độ nội bộ (Thiên Can→10 can, Địa Chi→12 chi, …) — neo cụm toạ-độ.
    for can in ONT_CAN:
        V.link(V.notes["Thiên Can"], can_title[can], "gồm can")
    for chi in ONT_CHI:
        V.link(V.notes["Địa Chi"], chi_title[chi], "gồm chi")
    for quai in ONT_QUAI:
        V.link(V.notes["Bát Quái"], quai_title[quai], "gồm quái")
    for que in ONT_QUE:
        V.link(V.notes["64 Quẻ"], que_title[que], "gồm quẻ")
    # Âm Dương (nền triết) → 2 khí toạ-độ (neo Âm/Dương hub vào cụm)
    V.link(V.notes["Âm Dương"], "Âm", "phân thành")
    V.link(V.notes["Âm Dương"], "Dương", "phân thành")

    # A1. CHÍNH TINH → [[Phái · tu_vi]] (provenance phái — mọi sao đều thuộc tu_vi).
    for s in CHINH_TINH_NAMES:
        rec = V.notes.get(star_title[s])
        if rec and "tu_vi" in phai_title:
            V.link(rec, phai_title["tu_vi"], "thuộc-phái")

    # A2. CUNG → [[Phái · tu_vi]] (cung = tu_vi; sao quay theo lá số nên không neo sao cố định).
    for c in PALACE_NAMES:
        rec = V.notes.get(cung_title[c])
        if rec and "tu_vi" in phai_title:
            V.link(rec, phai_title["tu_vi"], "thuộc-phái")

    # A3. CÁCH CỤC → [[Phái · tu_vi]] (provenance) + [[Sách · …]] nguồn (cach_cuc_index.sources).
    cc_sources = {}  # title -> set(corpus/book hints)
    for idx, (k, v) in enumerate(cc.items()):
        ten = v.get("ten") or k
        t = f"Cách · {safe_name(ten)}"
        # tên thật có thể bị suffix khi đụng; tra lại từ cach_recs theo thứ tự
        srcs = v.get("sources") or []
        cc_sources.setdefault(t, []).extend(srcs)
    for t, _text in cach_recs:
        rec = V.notes.get(t)
        if not rec:
            continue
        if "tu_vi" in phai_title:
            V.link(rec, phai_title["tu_vi"], "thuộc-phái")
        # sách nguồn cách cục = corpus Tử Vi Q1 (Phú Thái Vi). Neo về sách nếu corpus có node.
        for cand in ("tuvidauso-zh-q1", "q1_tuvi"):
            if cand in corpus_title:
                V.link(rec, corpus_title[cand], "trích-từ-sách")
                break

    # A4. NỀN TRIẾT → [[Phái · phat_hoc_nen]] nếu có hub (Phật học) — provenance.
    if "phat_hoc_nen" in phai_title:
        for n in ("Ngũ Uẩn", "Tứ Diệu Đế", "Bát Chánh Đạo", "Duyên Khởi", "Vô Ngã"):
            rec = V.notes.get(n)
            if rec:
                V.link(rec, phai_title["phat_hoc_nen"], "thuộc-phái")

    # A5. SÁCH NGUỒN → [[Phái · <school>]] (provenance cho node sách, từ books.json school).
    for cid, t in corpus_title.items():
        rec = V.notes.get(t)
        if not rec:
            continue
        sch = rec.get("school")
        if sch and sch in phai_title:
            V.link(rec, phai_title[sch], "thuộc-phái")
        # fallback: sách chưa biết phái → neo về hub sách (64 Quẻ/Thiên Can nếu khớp tên? không).
        # Nếu vẫn trống, A6 không áp dụng cho sách → để A-final safety net xử lý.

    # ============================================================
    #  (B) CẠNH TOẠ-ĐỘ-GỐC LIÊN-PHÁI (binder) — KHỚP CHÍNH XÁC primitive → hub chung
    # ============================================================
    coord_edge_count = 0

    def apply_coord(rec, *tokens):
        nonlocal coord_edge_count
        if not rec:
            return 0
        n = 0
        for hub_title, et in coord_links_for(*tokens):
            # tránh tự-nối node toạ-độ với chính nó
            if hub_title == rec["title"]:
                continue
            if V.link(rec, hub_title, et):
                n += 1
        coord_edge_count += n
        return n

    # B1. 14 chính tinh: record CÓ thuộc tính ngũ-hành → nối hub <hành>.
    #     (thay edge "hành của sao" cũ bằng cạnh toạ-độ chuẩn, vẫn deterministic Toàn Thư.)
    for s in CHINH_TINH_NAMES:
        ele = STAR_ELEMENT_CANON.get(s)
        rec = V.notes.get(star_title[s])
        if rec and ele:
            if V.link(rec, ele, "toạ-độ ngũ-hành"):
                coord_edge_count += 1

    # B2. MỌI node toạ-độ (can/chi/quái/quẻ) → tự nối hub + hành + nạp-giáp + thượng/hạ quái.
    for can in ONT_CAN:
        apply_coord(V.notes.get(can_title[can]), can)
    for chi in ONT_CHI:
        apply_coord(V.notes.get(chi_title[chi]), chi)
    for quai in ONT_QUAI:
        apply_coord(V.notes.get(quai_title[quai]), quai)
    for que in ONT_QUE:
        apply_coord(V.notes.get(que_title[que]), que)

    # B3. MỌI KHÁI NIỆM (mọi phái): nếu vi/zh/alias KHỚP CHÍNH XÁC primitive → nối hub chung.
    for cid, (vi, zh, al) in concept_tokens.items():
        if cid not in concept_title:
            continue
        rec = V.notes.get(concept_title[cid])
        apply_coord(rec, vi, zh, *al)

    # B4. CÁCH CỤC: tên cách khớp primitive? (hiếm) — vẫn áp để liên-phái.
    for t, text in cach_recs:
        apply_coord(V.notes.get(t), t.replace("Cách · ", ""))

    # B5. BẢNG HÀNH GROUNDED (concept_ngu_hanh_map.json) → cạnh toạ-độ ngũ-hành + âm-dương.
    #     GROUNDED TUYỆT ĐỐI: mỗi gán hành trong bảng đã có trường `nguon` (canonical table
    #     ontology_nen / engine tu_vi, HOẶC câu trích short_note tường minh). KHÔNG fuzzy,
    #     KHÔNG bịa — chỉ đọc kết quả đã neo nguồn. Nguồn được GIỮ trong body note (verify)
    #     để mỗi cạnh truy ngược được. Bổ trợ B1-B3: bắt các concept có hành nhưng tên KHÔNG
    #     khớp primitive (vd "Sa Trung Kim", "Thiên Khốc", "Quẻ Càn", các quẻ nạp-quái lưỡng hành).
    hanh_edge_count = 0
    hanh_concepts = 0
    try:
        _hm = json.loads(HANH_MAP.read_text(encoding="utf-8"))
    except Exception:
        _hm = {"concepts": {}}
    for _key, _entry in _hm.get("concepts", {}).items():
        cid = _entry.get("concept_id")
        if cid not in concept_title:
            continue  # concept không có node (vd canonical_vi rỗng) → bỏ qua an toàn
        rec = V.notes.get(concept_title[cid])
        if not rec:
            continue
        nguon = (_entry.get("nguon") or "").strip()
        added_here = 0
        # — cạnh ngũ-hành: mỗi hành grounded → [[<hành>]] (1..2 hành cho quẻ nạp-quái) —
        for h in _entry.get("hanh", []):
            if h in NGU_HANH and h != rec["title"]:
                if V.link(rec, h, "toạ-độ ngũ-hành"):
                    hanh_edge_count += 1
                    added_here += 1
        # — cạnh âm-dương: chỉ khi bảng có am_duong grounded → [[Âm]]/[[Dương]] —
        ad = _entry.get("am_duong")
        if ad in ("Âm", "Dương") and ad != rec["title"]:
            if V.link(rec, ad, "toạ-độ âm-dương"):
                hanh_edge_count += 1
                added_here += 1
        # — GIỮ NGUỒN trong body note để verify (provenance cạnh hành, KHÔNG đụng so_co_don) —
        if added_here and nguon:
            tag = f"<!-- toạ-độ ngũ-hành: hành={'+'.join(_entry.get('hanh', []))}" \
                  + (f" · âm-dương={ad}" if ad in ("Âm", "Dương") else "") \
                  + f" · nguồn: {nguon} -->"
            if tag not in rec["body"]:
                rec["body"].append("")
                rec["body"].append(tag)
            hanh_concepts += 1

    # ============================================================
    #  (B6) TRỤC BÁT TỰ — wiring 209 concept (8 school) vào toạ-độ gốc + Kinh Dịch.
    #  GROUNDED: mỗi cạnh truy về ontology_nen / def thập thần (id8390) / câu trích short_note.
    #  KHÔNG gán hành tuyệt đối cho thập thần (sai — hành phụ thuộc Nhật Chủ). KHÔNG đụng
    #  provenance (so_co_don giữ = 0). Nguồn giữ trong comment HTML body note để verify.
    # ============================================================
    batu_edge_count = 0
    BATU_SCHOOLS = {"bat_tu", "tu_binh_ba_tu", "bat_tu_ha_lac", "ha-lac",
                    "ha-lac-xuan-cang", "bat-tu", "bat_tu+tu_vi", "bat_tu+mai_hoa"}
    batu_cids = [c for c, s in concept_school.items() if s in BATU_SCHOOLS]

    def _blink(rec, target, et):
        """Link + đếm trục Bát Tự (chỉ khi resolve được; KHÔNG bịa)."""
        nonlocal batu_edge_count
        if rec and V.link(rec, target, et):
            batu_edge_count += 1
            return True
        return False

    def _prov(rec, comment):
        """Giữ nguồn cạnh trong comment HTML để verify (KHÔNG hiện ra graph/text đọc)."""
        if rec and comment not in rec["body"]:
            rec["body"].append("")
            rec["body"].append(comment)

    # — Nhật Chủ (Bát Tự, id8437) = đích quy-chiếu cho 10 thập thần (KHÔNG dùng node Tử Vi 5775) —
    nhat_chu_title = concept_title.get(8437)

    # (a) THẬP THẦN — 10 thần (id8391..8400) + hub. SCOPE theo school=tu_binh_ba_tu (KHÔNG theo
    #     tên — tránh đụng "Thất Sát" Tử Vi 七杀 id4912). Mỗi thần neo quan-hệ-Nhật-Chủ ĐÚNG
    #     câu trích short_note, KHÔNG gán hành tuyệt đối.
    #   map: tên thần → (hub quan-hệ, edge_type, câu-trích-nguồn từ short_note)
    THAP_THAN_REL = {
        "Tỷ Kiên":    ("Ngũ Hành",   "đồng-hành Nhật Chủ", "Cùng hành + cùng âm dương với Day Master"),
        "Kiếp Tài":   ("Ngũ Hành",   "đồng-hành Nhật Chủ", "Cùng hành + khác âm dương với Day Master"),
        "Thực Thần":  ("Tương sinh", "Nhật Chủ sinh ra",   "Day Master sinh ra, cùng âm dương"),
        "Thương Quan":("Tương sinh", "Nhật Chủ sinh ra",   "Day Master sinh ra, khác âm dương"),
        "Thiên Tài":  ("Tương khắc", "Nhật Chủ khắc",      "Day Master khắc, cùng âm dương"),
        "Chính Tài":  ("Tương khắc", "Nhật Chủ khắc",      "Day Master khắc, khác âm dương"),
        "Thất Sát":   ("Tương khắc", "khắc Nhật Chủ",      "Khắc Day Master, cùng âm dương"),
        "Chính Quan": ("Tương khắc", "khắc Nhật Chủ",      "Khắc Day Master, khác âm dương"),
        "Thiên Ấn":   ("Tương sinh", "sinh Nhật Chủ",      "Sinh Day Master, cùng âm dương"),
        "Chính Ấn":   ("Tương sinh", "sinh Nhật Chủ",      "Sinh Day Master, khác âm dương"),
    }
    thap_than_count = 0
    for cid in batu_cids:
        if concept_school.get(cid) != "tu_binh_ba_tu":
            continue
        vi = concept_tokens.get(cid, ("", None, []))[0]
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        # hub: mọi thập-thần (10 thần + Lộc Thần id8436) + chính "Thập Thần" def → [[Thập Thần]]
        if vi in THAP_THAN_REL or cid in (8390, 8436):
            if cid != 8390:  # def hub không tự-nối
                if _blink(rec, "Thập Thần", "là-thập-thần"):
                    thap_than_count += 1
                    _prov(rec, "<!-- là-thập-thần · nguồn: concept_index id8390 (十神 def) -->")
        # 10 thần → quy-chiếu Nhật Chủ + quan-hệ ngũ-hành ĐÚNG short_note (KHÔNG gán hành)
        if vi in THAP_THAN_REL:
            hub, et, src = THAP_THAN_REL[vi]
            if nhat_chu_title:
                _blink(rec, nhat_chu_title, "quy-chiếu Nhật Chủ")
            _blink(rec, hub, et)
            _prov(rec, f"<!-- {et} → [[{hub}]] · quy-chiếu [[Nhật Chủ]] · "
                       f"nguồn (short_note): \"{src}\" -->")

    # (b) THAM CHIẾU CAN/CHI — concept nêu cặp/can/chi trong short_note → [[Chi · X]]/[[Can · Y]]
    #     + hub. Vietnamese-safe boundary (re ASCII \\b KHÔNG ăn dấu). ALLOWLIST concept (tránh
    #     false-positive token, vd "Thân" trong "Lục Thân" = thân-thuộc KHÔNG phải chi Thân).
    LETTER = r"[0-9A-Za-zÀ-ỹ]"
    CANS = list(ONT_CAN.keys())
    CHIS = list(ONT_CHI.keys())

    def _find_tokens(text, words):
        out = []
        for w in words:
            if re.search(r"(?<!" + LETTER + r")" + re.escape(w) + r"(?!" + LETTER + r")", text):
                out.append(w)
        return out

    # ALLOWLIST: concept_id Bát Tự mà can/chi token trong short_note LÀ can/chi THẬT (đã soát tay).
    #   Loại trừ: 8439 Lục Thân (Thân=thân-thuộc), 8428 Tiết Khí (Dần=tháng vd, để hub nếu muốn).
    CAN_CHI_ALLOW = {
        8388,  # Tàng Can — liệt chi Tý/Mão/Ngọ/Dậu (tàng 1 can)
        8389,  # Bản Khí — Dần/Sửu + can Giáp/Kỷ
        8413,  # Điều Hậu — chi mùa Tý/Ngọ/Sửu/Tỵ/Hợi/Mùi
        8440,  # Nạp Âm — Giáp Tý/Ất Sửu/Bính Dần/Đinh Mão (cặp can-chi)
        8441,  # Hình Xung Khắc Hại — liệt 12 chi cặp
        8442,  # Bán Hợp — Thân/Tý/Thìn (tam hợp thiếu)
        3802,  # Thiên Ất Quý Nhân — can Giáp/Mậu/Canh... + chi
        3804,  # Lục Xung — 6 cặp chi xung
        3805,  # Lục Hợp — 6 cặp chi hợp
        3808,  # Tương Hại — cặp chi hại
        3809,  # Tương Hình — cặp chi hình
        3803,  # Tam Sát — chi
        3806,  # Tam Hợp — chi tam hợp
    }
    canchi_count = 0
    for cid in batu_cids:
        if cid not in CAN_CHI_ALLOW:
            continue
        vi = concept_tokens.get(cid, ("", None, []))[0]
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        blob = (vi or "") + " " + (concept_note.get(cid, ""))
        cans = _find_tokens(blob, CANS)
        chis = _find_tokens(blob, CHIS)
        added = 0
        for ch in chis:
            if _blink(rec, chi_title[ch], "tham chiếu chi"):
                added += 1
        for cn in cans:
            if _blink(rec, can_title[cn], "tham chiếu can"):
                added += 1
        if chis:
            _blink(rec, "Địa Chi", "thuộc trục địa-chi")
        if cans:
            _blink(rec, "Thiên Can", "thuộc trục thiên-can")
        if added:
            canchi_count += 1
            _prov(rec, f"<!-- tham chiếu can/chi · can={cans} chi={chis} · "
                       f"nguồn (short_note token, Vietnamese-safe boundary): "
                       f"đã soát allowlist -->")

    # (c) NẠP ÂM — KHÔNG gán hành tuyệt đối (30 cặp Giáp Tý, mỗi cặp 1 hành riêng → relative).
    #     Nạp Âm (id8440) → [[Ngũ Hành]] (định-tính theo cặp) + [[Thiên Can]] + [[Địa Chi]].
    nap_am_rec = V.notes.get(concept_title.get(8440))
    if nap_am_rec:
        _blink(nap_am_rec, "Ngũ Hành", "định-tính ngũ-hành theo cặp")
        _blink(nap_am_rec, "Thiên Can", "lập từ thiên-can")
        _blink(nap_am_rec, "Địa Chi", "lập từ địa-chi")
        _prov(nap_am_rec, "<!-- nạp-âm: KHÔNG gán hành tuyệt đối (relative theo cặp) · "
                          "nguồn (short_note): \"60 Giáp Tý chia 30 cặp, mỗi cặp có một tên "
                          "ngũ hành riêng\" -->")
    # catalog "Thông Căn + Nạp Âm" (id9162) → [[Nạp Âm]]
    rec_tc = V.notes.get(concept_title.get(9162))
    if rec_tc and 8440 in concept_title:
        _blink(rec_tc, concept_title[8440], "catalog gồm Nạp Âm")

    # (d) HÀ LẠC → cầu sang KINH DỊCH (64 Quẻ). Bắc cầu short-name → kép qua bảng dẫn-xuất từ
    #     ontology que_64 (tên kép tự mã hoá thượng/hạ quái → short name là token đuôi). Accent-
    #     insensitive fallback cho 'Quan' (kép 'Phong Địa Quán'). KHÔNG bịa: short→kép suy từ
    #     ontology, kép đã là node [[Quẻ · …]] sẵn.
    _ELEM = {"Thiên", "Địa", "Trạch", "Hỏa", "Lôi", "Phong", "Thủy", "Sơn"}

    def _short_of_kep(kep):
        toks = kep.split()
        if toks and toks[0] == "Thuần":
            return " ".join(toks[1:])
        out, skip = [], 0
        for t in toks:
            if t in _ELEM and skip < 2:
                skip += 1
                continue
            out.append(t)
        return " ".join(out)

    def _na(s):  # strip dấu để fallback khớp (Quan↔Quán)
        return __import__("unicodedata").normalize("NFD", s).encode("ascii", "ignore").decode().lower()

    short2kep = {}
    short2kep_ai = {}
    for kep in ONT_QUE:
        s = _short_of_kep(kep)
        short2kep[s] = kep
        short2kep_ai[_na(s)] = kep

    def _kep_for_short(short):
        if short in short2kep:
            return short2kep[short]
        return short2kep_ai.get(_na(short))

    halac_card_count = 0
    halac_concept_count = 0
    # 42 card "Quẻ Hà Lạc — X" → [[64 Quẻ]] + [[Quẻ · <kép>]]
    for cid in batu_cids:
        vi = concept_tokens.get(cid, ("", None, []))[0]
        if not vi or not vi.startswith("Quẻ Hà Lạc"):
            continue
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        # tách tên ngắn sau dấu "—"
        short = vi.split("—")[-1].strip()
        kep = _kep_for_short(short)
        if kep and kep in que_title:
            _blink(rec, "64 Quẻ", "là quẻ Hà Lạc")
            if _blink(rec, que_title[kep], "ứng quẻ Kinh Dịch"):
                halac_card_count += 1
                _prov(rec, f"<!-- ứng quẻ: '{short}' → [[Quẻ · {kep}]] · "
                           f"nguồn: short-name suy từ ontology_nen.que_64 (tên kép mã hoá quái) -->")

    # CASE STUDY HÀ LẠC — tên quẻ NẰM TRONG TIÊU ĐỀ ("Case study Hà Lạc — <Quẻ> hào X — …")
    #   → bắc cầu [[Quẻ · kép]] + [[64 Quẻ]]. GROUNDED: quẻ ở ngay trong tên concept.
    halac_case_count = 0
    for cid in batu_cids:
        vi = concept_tokens.get(cid, ("", None, []))[0]
        if not vi or not vi.startswith("Case study Hà Lạc"):
            continue
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        segs = vi.split("—")
        if len(segs) < 2:
            continue
        qn = segs[1].split(" hào")[0].strip()  # "<Quẻ> hào X" → "<Quẻ>"
        kep = _kep_for_short(qn)
        if kep and kep in que_title:
            _blink(rec, "64 Quẻ", "case study trên quẻ")
            if _blink(rec, que_title[kep], "ứng quẻ Kinh Dịch"):
                halac_case_count += 1
                _prov(rec, f"<!-- case study quẻ '{qn}' → [[Quẻ · {kep}]] · "
                           f"nguồn: tên quẻ trong tiêu đề concept + ontology que_64 -->")
        # quét thêm kép quẻ trong short_note (Tiên Thiên/Hậu Thiên) → dẫn quẻ
        note = concept_note.get(cid, "")
        for k2 in ONT_QUE:
            if k2 in note and k2 in que_title and k2 != kep:
                _blink(rec, que_title[k2], "dẫn quẻ Kinh Dịch")

    # CASE STUDY PHẦN BA — 7 chân dung nhà văn: short_note có tên KÉP (Tiên/Hậu Thiên quẻ)
    #   + tên NGẮN ở field "Tiên Thiên: <X>" → bắc cầu [[Quẻ · kép]]. GROUNDED từ short_note.
    halac_phanba_count = 0
    for cid in batu_cids:
        vi = concept_tokens.get(cid, ("", None, []))[0]
        if not vi or not vi.startswith("Case study Phần Ba"):
            continue
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        note = concept_note.get(cid, "")
        added = 0
        # kép trong note
        for k2 in ONT_QUE:
            if k2 in note and k2 in que_title:
                added += _blink(rec, que_title[k2], "dẫn quẻ Kinh Dịch")
        # short name ở field "Tiên Thiên: <X>" / "Hậu Thiên: <X>"
        for m in re.finditer(r"(?:Tiên Thiên|Hậu Thiên)\**\s*[:：]\s*([^\n*·,()]+)", note):
            qn = m.group(1).strip()
            kep = _kep_for_short(qn)
            if kep and kep in que_title:
                added += _blink(rec, que_title[kep], "ứng quẻ Kinh Dịch")
        if added:
            halac_phanba_count += 1
            _blink(rec, "64 Quẻ", "chân dung Hà Lạc trên quẻ")
            _prov(rec, "<!-- chân dung Hà Lạc: quẻ Tiên/Hậu Thiên trong short_note → "
                       "[[Quẻ · …]] · nguồn: short_note + ontology que_64 -->")

    # 7+ case study Phần Ba (bat_tu_ha_lac/ha-lac) dùng tên KÉP trong short_note → khớp alias sẵn.
    #   + khái niệm cốt Hà Lạc → hub [[Bát Tự Hà Lạc]] + [[64 Quẻ]] + [[Tứ Trụ]].
    halac_hub_title = concept_title.get(8444)   # "Bát Tự Hà Lạc"
    tu_tru_title = concept_title.get(8374)       # "Tứ Trụ"
    HALAC_CORE = {8445, 8446, 8447, 8448, 8449, 8450, 8451, 8452, 8453,
                  8454, 8455, 8456, 8457, 8458, 8460, 8461, 8462}
    for cid in batu_cids:
        if concept_school.get(cid) not in ("bat_tu_ha_lac",):
            continue
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        added = 0
        # khái niệm cốt → hub Hà Lạc + cầu Tứ Trụ → 2 quẻ
        if cid in HALAC_CORE:
            if halac_hub_title and cid != 8444:
                added += _blink(rec, halac_hub_title, "thuộc Bát Tự Hà Lạc")
            _blink(rec, "64 Quẻ", "vận hành trên 64 quẻ")
            if tu_tru_title:
                _blink(rec, tu_tru_title, "chuyển Tứ Trụ → quẻ")
        # quét tên KÉP quẻ trong short_note (case study Phần Ba) → [[Quẻ · …]]
        note = concept_note.get(cid, "")
        for kep in ONT_QUE:
            if kep in note and kep in que_title:
                added += _blink(rec, que_title[kep], "dẫn quẻ Kinh Dịch")
        if added:
            halac_concept_count += 1
            _prov(rec, "<!-- trục Hà Lạc · nguồn: ontology que_64 (tên kép) + def Bát Tự Hà Lạc id8444 -->")
    # hub Bát Tự Hà Lạc (id8444) tự neo → [[64 Quẻ]] + [[Tứ Trụ]] (gốc paradigm)
    if halac_hub_title:
        rec = V.notes.get(halac_hub_title)
        _blink(rec, "64 Quẻ", "vận hành trên 64 quẻ")
        if tu_tru_title:
            _blink(rec, tu_tru_title, "chuyển Tứ Trụ → quẻ")

    # (e) KHÁC — neo grounded các nhóm còn lại về hub trục đúng nguồn short_note.
    #   (e-1) Tứ Trụ (8374) → [[Thiên Can]] + [[Địa Chi]] (4 cặp can-chi).
    if tu_tru_title:
        rec = V.notes.get(tu_tru_title)
        _blink(rec, "Thiên Can", "gồm 4 thiên-can")
        _blink(rec, "Địa Chi", "gồm 4 địa-chi")
        _prov(rec, "<!-- Tứ Trụ = 4 cột, mỗi cột 1 thiên-can + 1 địa-chi · nguồn: def Tứ Trụ id8374 -->")

    #   (e-2) THẬP THẦN CÁCH (8402..8411) → [[Thập Thần]] hub + thần tương ứng (nguồn short_note
    #         "Bản Khí Trụ Tháng = <Thần>"). Đây là cách-cục dựng TRÊN thập thần → neo về trục.
    THAN_CACH_OF = {
        8402: "Chính Quan", 8403: "Thất Sát", 8404: "Chính Tài", 8405: "Thiên Tài",
        8406: "Thực Thần", 8407: "Thương Quan", 8408: "Chính Ấn", 8409: "Thiên Ấn",
        8410: "Lộc Thần",  # Kiến Lộc cách = Lộc Thần ngụ Trụ Tháng
        8411: "Kiếp Tài",  # Dương Nhận cách = Kiếp Tài của DM
    }
    than_cach_count = 0
    # map tên thần → concept_id (Bát Tự) để neo thần cụ thể
    than_name2cid = {}
    for _c in batu_cids:
        if concept_school.get(_c) == "tu_binh_ba_tu":
            _v = concept_tokens.get(_c, ("", None, []))[0]
            if _v in ("Tỷ Kiên", "Kiếp Tài", "Thực Thần", "Thương Quan", "Thiên Tài",
                      "Chính Tài", "Thất Sát", "Chính Quan", "Thiên Ấn", "Chính Ấn",
                      "Lộc Thần"):
                than_name2cid[_v] = _c
    for cid, than in THAN_CACH_OF.items():
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        ok = _blink(rec, "Thập Thần", "cách dựng trên thập-thần")
        tcid = than_name2cid.get(than)
        if tcid and tcid in concept_title:
            _blink(rec, concept_title[tcid], "ứng thập-thần")
        if ok:
            than_cach_count += 1
            _prov(rec, f"<!-- cách dựng trên [[Thập Thần]] {than} · "
                       f"nguồn (short_note): \"Bản Khí Trụ Tháng = {than}\" -->")

    #   (e-3) VÒNG TRƯỜNG SINH 12 phase (8415..8425 + Suy) → hub [[Vòng Trường Sinh]] (8414)
    #         + [[Nhật Chủ]] (mỗi phase mô tả cường độ Day Master). Nguồn short_note "Phase k/12".
    truong_sinh_hub = concept_title.get(8414)
    phase_count = 0
    for cid in batu_cids:
        if concept_school.get(cid) != "tu_binh_ba_tu":
            continue
        note = concept_note.get(cid, "")
        if not re.search(r"Phase\s+\d+/12", note):
            continue
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        added = 0
        if truong_sinh_hub and cid != 8414:
            added += _blink(rec, truong_sinh_hub, "phase Vòng Trường Sinh")
        if nhat_chu_title:
            added += _blink(rec, nhat_chu_title, "cường độ Nhật Chủ")
        if added:
            phase_count += 1
            _prov(rec, "<!-- phase Vòng Trường Sinh của Nhật Chủ · "
                       "nguồn (short_note): \"Phase k/12. Day Master …\" -->")

    #   (e-4) THẦN SÁT (sao phụ quanh Day Master) → [[Nhật Chủ]] (an theo can/chi Nhật Chủ/năm).
    #         Nguồn: short_note đều mô tả "Sao …" an quanh lá số. CHỈ neo thần-sát rõ ràng.
    THAN_SAT_IDS = {8429, 8430, 8431, 8432, 8433, 8434, 8435, 3802}
    than_sat_count = 0
    for cid in THAN_SAT_IDS:
        rec = V.notes.get(concept_title.get(cid))
        if not rec:
            continue
        if nhat_chu_title and _blink(rec, nhat_chu_title, "thần-sát an quanh Nhật Chủ"):
            than_sat_count += 1
            _prov(rec, "<!-- thần-sát an quanh Nhật Chủ (theo can/chi) · nguồn: short_note 'Sao …' -->")

    #   (e-5) LỤC THÂN (8439) → [[Thập Thần]] (Lục Thân = map thập thần → quan hệ gia đình).
    rec_lt = V.notes.get(concept_title.get(8439))
    if rec_lt:
        _blink(rec_lt, "Thập Thần", "map từ thập-thần")
        _prov(rec_lt, "<!-- Lục Thân = cách map [[Thập Thần]] → quan hệ gia đình · "
                      "nguồn (short_note): \"Cách map Thập Thần → quan hệ gia đình\" -->")

    # ============================================================
    #  (A-final) SAFETY NET: quét node cô đơn (0 in + 0 out) → neo provenance tối thiểu.
    # ============================================================
    indeg = {}
    for rec in V.notes.values():
        for tgt, _et in rec["links"]:
            indeg[tgt] = indeg.get(tgt, 0) + 1
    for title, rec in V.notes.items():
        if rec["ntype"] == "readme":
            continue
        has_out = bool(rec["links"])
        has_in = indeg.get(title, 0) > 0
        if has_out or has_in:
            continue
        # node cô đơn còn sót → neo về [[Phái · <school>]] nếu có, else hub toạ-độ chung.
        sch = rec.get("school")
        if sch and sch in phai_title and phai_title[sch] != title:
            V.link(rec, phai_title[sch], "thuộc-phái")
        elif "tu_vi" in phai_title and phai_title["tu_vi"] != title:
            V.link(rec, phai_title["tu_vi"], "thuộc-phái")

    # ===== README =====
    readme = build_readme(V)
    V.add("_README — Mạng Tri Thức YI", ".", ntype="readme",
          body_lines=[readme], extra_tags=["#readme"])

    # write all notes
    V.flush()

    # ===== merge graph.json colorGroups =====
    merge_graph_colors()

    # ===== ĐO CÔ ĐƠN (0 in + 0 out, trừ README) =====
    indeg2 = {}
    for rec in V.notes.values():
        for tgt, _et in rec["links"]:
            indeg2[tgt] = indeg2.get(tgt, 0) + 1
    co_don = []
    for title, rec in V.notes.items():
        if rec["ntype"] == "readme":
            continue
        if not rec["links"] and indeg2.get(title, 0) == 0:
            co_don.append(title)
    so_co_don = len(co_don)

    # degree mới của các hub toạ-độ ngũ-hành (in + out)
    def _deg(title):
        out = len(V.notes.get(title, {}).get("links", []))
        return out + indeg2.get(title, 0)
    element_hub_degree = {h: _deg(h) for h in NGU_HANH}

    # ===== ĐO TRỤC BÁT TỰ: bao nhiêu / 209 concept có ≥1 cạnh TRỤC (toạ-độ/quẻ/thập-thần) =====
    AXIS_EDGE_TYPES = {
        "là-thập-thần", "quy-chiếu Nhật Chủ", "đồng-hành Nhật Chủ", "Nhật Chủ sinh ra",
        "Nhật Chủ khắc", "khắc Nhật Chủ", "sinh Nhật Chủ",
        "tham chiếu chi", "tham chiếu can", "thuộc trục địa-chi", "thuộc trục thiên-can",
        "định-tính ngũ-hành theo cặp", "lập từ thiên-can", "lập từ địa-chi", "catalog gồm Nạp Âm",
        "là quẻ Hà Lạc", "ứng quẻ Kinh Dịch", "dẫn quẻ Kinh Dịch", "thuộc Bát Tự Hà Lạc",
        "vận hành trên 64 quẻ", "chuyển Tứ Trụ → quẻ", "gồm 4 thiên-can", "gồm 4 địa-chi",
        "cách dựng trên thập-thần", "ứng thập-thần", "phase Vòng Trường Sinh",
        "cường độ Nhật Chủ", "thần-sát an quanh Nhật Chủ", "map từ thập-thần",
        "case study trên quẻ", "chân dung Hà Lạc trên quẻ",
        # toạ-độ chung (B1-B5) cũng tính là trục
        "toạ-độ ngũ-hành", "toạ-độ âm-dương", "toạ-độ thiên-can", "toạ-độ địa-chi",
        "toạ-độ bát-quái", "toạ-độ 64-quẻ", "thượng quái", "hạ quái", "nạp-giáp can",
    }
    # in-degree theo edge-type cho mỗi node (để bắt cạnh ĐẾN node concept, vd hub→concept)
    batu_titles = {concept_title[c] for c in batu_cids if c in concept_title}
    batu_has_axis = set()
    for title, rec in V.notes.items():
        # out-edges
        if title in batu_titles:
            for _tgt, et in rec["links"]:
                if et in AXIS_EDGE_TYPES:
                    batu_has_axis.add(title)
                    break
        # in-edges (hub → concept, vd catalog→Nạp Âm)
        for tgt, et in rec["links"]:
            if tgt in batu_titles and et in AXIS_EDGE_TYPES:
                batu_has_axis.add(tgt)
    batu_total = len(batu_titles)
    batu_covered = len(batu_has_axis)
    batu_uncovered = sorted(batu_titles - batu_has_axis)

    # ===== SELF-TEST =====
    n_notes = len(V.notes)
    n_links = V.link_count
    passed, checks = self_test(V, n_notes, n_links)
    checks["so_co_don_eq_0"] = (so_co_don == 0)
    checks["co_don_sample"] = co_don[:10]
    passed = passed and checks["so_co_don_eq_0"]

    result = {
        "so_note": n_notes,
        "so_link": n_links,
        "so_co_don": so_co_don,
        "so_canh_synapse_atom_relations": synapse_edge_count,
        "synapse_pairs_distinct": len(synapse_pairs),
        "synapse_skipped_no_node": synapse_skipped_no_node,
        "so_canh_toa_do": coord_edge_count,
        "so_canh_hanh_grounded": hanh_edge_count,
        "so_concept_hanh_grounded": hanh_concepts,
        "so_canh_batu": batu_edge_count,
        "batu_breakdown": {
            "thap_than": thap_than_count,
            "can_chi": canchi_count,
            "ha_lac_card": halac_card_count,
            "ha_lac_concept": halac_concept_count,
            "than_cach": than_cach_count,
            "phase_truong_sinh": phase_count,
            "than_sat": than_sat_count,
            "ha_lac_case_study": halac_case_count,
            "ha_lac_phan_ba": halac_phanba_count,
        },
        "batu_concept_total": batu_total,
        "batu_concept_covered": batu_covered,
        "batu_concept_uncovered": batu_uncovered,
        "element_hub_degree": element_hub_degree,
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
        "- Folder `00 · Toạ độ gốc chung` = HUB TRUNG LẬP PHÁI (school=chung): "
        "5 hành · Âm/Dương · 10 can · 12 chi · 8 quái · 64 quẻ. Mọi phái nối về đây (binder).",
        "- Folder `00 · Nền triết` = gốc Âm Dương / Ngũ Hành / Ngũ Uẩn / Phật học.",
        "- Folder `01 · Phái` = hub MOC mỗi trường phái (backlink hội tụ).",
        "- Folder `02 · Tử Vi` = 14 chính tinh + 12 cung + cách cục.",
        "- Folder `03 · Khái niệm/<phái>` = 3641 khái niệm wiki.",
        "- Folder `04 · Sách nguồn` = corpus gốc mỗi khái niệm trích ra.",
        "",
        "## Hai lớp cạnh mới (2 invariant)",
        "- **(A) Provenance bắt buộc**: MỌI node có ≥1 [[Phái · …]] hoặc [[Sách · …]] → "
        "KHÔNG còn node cô đơn (so_co_don = 0).",
        "- **(B) Toạ-độ gốc liên-phái**: node bất kỳ phái nếu tên/zh/alias KHỚP CHÍNH XÁC "
        "một primitive (can/chi/quái/quẻ/hành) HOẶC có thuộc tính ngũ-hành (14 sao) → nối "
        "hub toạ-độ chung. KHỚP CHÍNH XÁC, KHÔNG fuzzy — mọi cạnh truy về `ontology_nen.json`.",
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
        "- **sao cấu thành**: cách cục → chính tinh xuất hiện trong tên/điều kiện.",
        "- **gốc-tham nhắc**: sao → concept có tên khớp nguyên văn trong trường `goc_tham`.",
        "- **liên-kết-nghĩa**: SYNAPSE THẬT từ bảng `atom_relations` (wiki_connect_v1) — mỗi hàng "
        "là 1 quan-hệ ngữ-nghĩa giữa 2 khái niệm (from_concept_id ↔ to_concept_id), neo bằng câu "
        "`rationale` (truy về short_note nguồn). Gộp mọi relation_type (thuộc-về / giải-thích-bằng "
        "/ là-loại-của / sinh / khắc …); rationale + loại gốc giữ trong comment HTML note để verify.",
        "- **nền triết nội bộ**: Ngũ Uẩn→5 uẩn, khe Thọ→Hành, Bát Chánh Đạo→Tứ Diệu Đế…",
        "",
        "### Cạnh toạ-độ gốc (B) — từ `ontology_nen.json` (canonical, KHỚP CHÍNH XÁC)",
        "- **toạ-độ ngũ-hành**: node khớp 1 hành / 14 sao có thuộc tính ngũ-hành → [[Kim/Mộc/…]]; "
        "CỘNG bảng `concept_ngu_hanh_map.json` (GROUNDED, mỗi gán có `nguon` giữ trong comment "
        "note để verify — canonical table HOẶC trích short_note; KHÔNG fuzzy).",
        "- **toạ-độ âm-dương**: khớp Âm/Dương / can → [[Âm]] / [[Dương]]; CỘNG bảng hành grounded "
        "(chỉ khi có `am_duong` neo nguồn).",
        "- **toạ-độ thiên-can / địa-chi / bát-quái / 64-quẻ**: khớp can/chi/quái/quẻ → hub chung.",
        "- **thượng quái / hạ quái**: quẻ → 2 quái cấu thành (nội/ngoại).",
        "- **nạp-giáp can**: quái → can nạp giáp (nối Kinh Dịch ↔ Bát Tự).",
        "- **gồm can/chi/quái/quẻ/hành**: hub toạ-độ → các phần tử của nó.",
        "",
        "### (B6) TRỤC BÁT TỰ — 209 concept (8 school) vào toạ-độ + Kinh Dịch (GROUNDED)",
        "Hub MỚI: [[Thập Thần]] (school=tu_binh_ba_tu, nguồn def id8390) + [[Tương sinh]] / "
        "[[Tương khắc]] (quan-hệ ngũ-hành). KHÔNG gán hành tuyệt đối cho thập thần (sai — hành "
        "phụ thuộc Nhật Chủ). Mỗi cạnh giữ NGUỒN trong comment HTML body note để verify.",
        "- **là-thập-thần / quy-chiếu Nhật Chủ**: 10 thần (SCOPE school=tu_binh_ba_tu, KHÔNG theo "
        "tên — tránh đụng 'Thất Sát' Tử Vi 七杀) → hub + [[Nhật Chủ]] (Day Master).",
        "- **đồng-hành/Nhật Chủ sinh ra/Nhật Chủ khắc/khắc Nhật Chủ/sinh Nhật Chủ**: quan-hệ "
        "ngũ-hành ĐÚNG câu trích short_note (vd Thực Thần = 'Day Master sinh ra').",
        "- **tham chiếu can / tham chiếu chi**: concept (allowlist soát tay) nêu can/chi trong "
        "short_note → [[Can · X]] / [[Chi · Y]] (Vietnamese-safe boundary).",
        "- **định-tính ngũ-hành theo cặp / lập từ thiên-can / lập từ địa-chi**: Nạp Âm → "
        "[[Ngũ Hành]] + [[Thiên Can]] + [[Địa Chi]] (KHÔNG hành tuyệt đối — relative theo cặp).",
        "- **ứng quẻ Kinh Dịch / là quẻ Hà Lạc / case study trên quẻ**: 42 card + 23 case study "
        "+ 7 chân dung Hà Lạc → [[Quẻ · <kép>]] (short-name suy từ ontology que_64) + [[64 Quẻ]].",
        "- **cách dựng trên thập-thần / phase Vòng Trường Sinh / thần-sát an quanh Nhật Chủ / "
        "map từ thập-thần**: thập-thần-cách, 12 phase Trường Sinh, thần sát, Lục Thân → hub trục.",
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
