#!/usr/bin/env python3
"""Build data/yi_lexicon/concept_ngu_hanh_map.json — GROUNDED ngũ hành map.

Mỗi gán hành PHẢI có nguồn. 4 nguồn theo thứ tự ưu tiên:
 (1) CANONICAL TỬ VI sao→hành (engine/tu_vi chính tinh + chiếu đởm phi tinh)
 (2) PRIMITIVE: can/chi/quái/hành (ontology_nen)
 (3) QUẺ→QUÁI→HÀNH (64 quẻ → hành 2 quái, ontology)
 (4) TRÍCH TƯỜNG MINH: short_note pattern rõ ('thuộc hành X', '(hành X)', 'hành <X>')

KHÔNG gán hành cho thập thần Bát Tự (category='thap_than').
"""
from __future__ import annotations
import json, re, sqlite3, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hexagrams_king_wen import HEX  # glyph -> (upper zh trigram, lower zh trigram)

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
WIKI = ROOT / "data/yi_wiki/wiki.sqlite3"
ONTO = ROOT / "data/yi_lexicon/ontology_nen.json"
CHINH = ROOT / "data/tu_vi/chinh_tinh.json"
PHI = ROOT / "data/tu_vi/chieu_dom_kinh_18_phi_tinh.json"
OUT = ROOT / "data/yi_lexicon/concept_ngu_hanh_map.json"

HANH_CANON = {"kim": "Kim", "mộc": "Mộc", "mộc": "Mộc", "thủy": "Thủy",
              "thuỷ": "Thủy", "hỏa": "Hỏa", "hoả": "Hỏa", "thổ": "Thổ"}

def norm_hanh(s: str) -> list[str]:
    """'kim / hỏa' -> ['Kim','Hỏa']. Trả [] nếu không nhận ra."""
    out = []
    for part in re.split(r"[/,;]| và | hoặc ", s.strip().lower()):
        p = part.strip()
        if p in HANH_CANON and HANH_CANON[p] not in out:
            out.append(HANH_CANON[p])
    return out

def nfc(s): return unicodedata.normalize("NFC", s) if s else s

# ---------------------------------------------------------------------------
# Build canonical sao -> hành lookup (by Vietnamese name + Chinese name)
# ---------------------------------------------------------------------------
sao_hanh: dict[str, dict] = {}   # name_vi -> {hanh, am_duong, nguon}
sao_hanh_zh: dict[str, dict] = {}

# (1a) 14 chính tinh
cj = json.loads(CHINH.read_text(encoding="utf-8"))
for s in cj["stars"]:
    h = norm_hanh(s["ngu_hanh"])
    if not h:
        continue
    ad = {"âm": "Âm", "dương": "Dương"}.get(s.get("am_duong", "").strip().lower())
    rec = {"hanh": h, "am_duong": ad,
           "nguon": f"engine/tu_vi canonical (data/tu_vi/chinh_tinh.json, ngu_hanh='{s['ngu_hanh']}')"}
    sao_hanh[nfc(s["ten_vi"])] = rec
    if s.get("ten_zh"):
        sao_hanh_zh[nfc(s["ten_zh"])] = rec

# (1b) 18 phi tinh Chiếu Đởm (Bắc phái canonical)
pj = json.loads(PHI.read_text(encoding="utf-8"))
for grp in ("phi_tinh_9_duong", "phi_tinh_9_am"):
    for s in pj.get(grp, []):
        h = norm_hanh(s["ngu_hanh"])
        if not h:
            continue
        ad = {"âm": "Âm", "dương": "Dương"}.get(s.get("polarity", "").strip().lower())
        rec = {"hanh": h, "am_duong": ad,
               "nguon": f"engine/tu_vi canonical (data/tu_vi/chieu_dom_kinh_18_phi_tinh.json, {s.get('source_ref','')})"}
        # don't overwrite a chính-tinh mapping
        sao_hanh.setdefault(nfc(s["name_vi"]), rec)
        if s.get("name_zh"):
            sao_hanh_zh.setdefault(nfc(s["name_zh"]), rec)

print(f"[canonical] sao_hanh(vi)={len(sao_hanh)} sao_hanh(zh)={len(sao_hanh_zh)}")

# ---------------------------------------------------------------------------
# Ontology primitives
# ---------------------------------------------------------------------------
onto = json.loads(ONTO.read_text(encoding="utf-8"))
can = onto["thien_can"]      # name -> {ngu_hanh, am_duong, zh}
chi = onto["dia_chi"]
quai = onto["bat_quai"]      # name -> {ngu_hanh, am_duong, zh}
que64 = onto["que_64"]       # name -> {ngu_hanh_thuong, ngu_hanh_ha, zh, ...}
hanh5 = onto["ngu_hanh"]     # Kim/Mộc/... -> {...}

# zh alias maps for primitives
can_by_zh = {nfc(v["zh"]): k for k, v in can.items()}
chi_by_zh = {nfc(v["zh"]): k for k, v in chi.items()}
quai_by_zh = {nfc(v["zh"]): k for k, v in quai.items()}
que_by_zh = {nfc(v["zh"]): k for k, v in que64.items()}

# trigram zh -> (vi name, hành) from ontology bát quái
QUAI_VI = {nfc(v["zh"]): k for k, v in quai.items()}        # 乾 -> Càn
QUAI_HANH = {nfc(v["zh"]): v["ngu_hanh"] for k, v in quai.items()}  # 乾 -> Kim

# ---------------------------------------------------------------------------
# Iterate concepts
# ---------------------------------------------------------------------------
con = sqlite3.connect(WIKI)
con.row_factory = sqlite3.Row
rows = con.execute(
    "SELECT concept_id, canonical_vi, canonical_zh, aliases, short_note, category, school "
    "FROM concept_index").fetchall()

result: dict[str, dict] = {}
stats = {"canonical_sao": 0, "primitive": 0, "que_quai": 0, "tuong_minh": 0,
         "skipped_thapthan": 0, "no_hanh": 0}
NAP_HANH = None  # set later

# tường minh patterns on short_note
# e.g. "thuộc hành Thủy", "(hành Hỏa)", "hành Hỏa,", "thuộc Kim", "Sao Hỏa,"
HANH_WORD = r"(Kim|Mộc|Thủy|Thuỷ|Hỏa|Hoả|Thổ)"
# Multi-hành: "Kim+Hỏa", "Kim/Hỏa", "Kim, Hỏa", "Kim và Hỏa"
HANH_MULTI = HANH_WORD + r"(?:\s*[+/]\s*|\s*,\s*|\s+và\s+)" + HANH_WORD
PAT_EXPLICIT = [
    # multi-hành sau "ngũ hành" / "thuộc hành" / "hành" — ưu tiên bắt cả 2
    re.compile(r"ngũ\s*hành\s*[:：]?\s*" + HANH_MULTI, re.IGNORECASE),
    re.compile(r"thuộc\s+hành\s+" + HANH_MULTI, re.IGNORECASE),
    re.compile(r"\bhành\s+" + HANH_MULTI, re.IGNORECASE),
    # single-hành
    re.compile(r"thuộc\s+hành\s+" + HANH_WORD, re.IGNORECASE),
    re.compile(r"\(\s*hành\s+" + HANH_WORD + r"\s*\)", re.IGNORECASE),
    re.compile(r"\bhành\s+" + HANH_WORD + r"\b", re.IGNORECASE),
    re.compile(r"ngũ\s*hành\s*[:：]\s*" + HANH_WORD, re.IGNORECASE),
]

# Leading "Sao <Hành>," — chỉ áp dụng cho category sao (mô tả hành của sao ở đầu note)
PAT_SAO_LEAD = re.compile(r"^\s*Sao\s+" + HANH_WORD + r"\s*[,\.]", re.IGNORECASE)


# Concepts mô tả QUAN HỆ sinh-khắc (không phải thực thể mang hành) — KHÔNG gán.
_REL_NAME = re.compile(
    r"^(Tương\s+sinh|Tương\s+khắc|Sinh|Khắc|Chế hóa|Chế hoá|Tỉ Hoà|Tỷ hoà|"
    r"Tỉ Hòa|Tỷ Hòa|.*\b(sinh|khắc)\b.*)$", re.IGNORECASE)


def hanh_from_note(note: str, name_vi: str, is_sao: bool = False) -> tuple[list[str], str] | None:
    """Return ([hành], matched_sentence) only if pattern RÕ. Else None."""
    if not note:
        return None
    # Bỏ qua concept là QUAN HỆ ngũ hành (sinh/khắc/chế hóa) — hành không thuộc về nó
    if _REL_NAME.match(name_vi.strip()):
        return None
    if is_sao:
        m = PAT_SAO_LEAD.match(note)
        if m:
            h = HANH_CANON.get(m.group(1).lower())
            if h:
                return [h], note[:note.find(".", 0) if note.find(".") != -1 else 60].strip()
    for pat in PAT_EXPLICIT:
        m = pat.search(note)
        if m:
            hs = []
            for g in m.groups():
                if g:
                    hh = HANH_CANON.get(g.lower())
                    if hh and hh not in hs:
                        hs.append(hh)
            if hs:
                # capture surrounding sentence for citation
                start = note.rfind(".", 0, m.start()) + 1
                end = note.find(".", m.end())
                end = end if end != -1 else len(note)
                sent = note[start:end].strip()
                return hs, sent
    return None

for r in rows:
    cid = r["concept_id"]
    vi = nfc(r["canonical_vi"] or "")
    zh = nfc(r["canonical_zh"] or "")
    cat = (r["category"] or "").strip()
    note = r["short_note"] or ""
    key = f"{cid}:{vi}"

    # SKIP thập thần Bát Tự — hành phụ thuộc nhật chủ
    if cat == "thap_than":
        stats["skipped_thapthan"] += 1
        continue

    rec = None

    # (1) canonical sao  — only for category sao / sao-like
    if cat in ("sao", "thần sát", "than_sat"):
        cand = sao_hanh.get(vi) or (sao_hanh_zh.get(zh) if zh else None)
        if cand:
            rec = {"hanh": cand["hanh"], "am_duong": cand.get("am_duong"),
                   "nguon": cand["nguon"]}
            stats["canonical_sao"] += 1

    # (2) primitive: thiên can / địa chi / bát quái / hành
    if rec is None:
        if cat == "thien_can" and (vi in can or zh in can_by_zh):
            name = vi if vi in can else can_by_zh[zh]
            d = can[name]
            rec = {"hanh": [d["ngu_hanh"]], "am_duong": d.get("am_duong"),
                   "nguon": f"ontology_nen.thien_can[{name}]"}
            stats["primitive"] += 1
        elif cat == "dia_chi" and (vi in chi or zh in chi_by_zh):
            name = vi if vi in chi else chi_by_zh[zh]
            d = chi[name]
            rec = {"hanh": [d["ngu_hanh"]], "am_duong": d.get("am_duong"),
                   "nguon": f"ontology_nen.dia_chi[{name}]"}
            stats["primitive"] += 1
        elif vi in hanh5 or (cat in ("ngu_hanh", "ngũ hành") and vi in hanh5):
            rec = {"hanh": [vi], "am_duong": None,
                   "nguon": f"ontology_nen.ngu_hanh[{vi}] (chính nó là hành)"}
            stats["primitive"] += 1
        # bát quái primitive (8) — match exactly to ontology name/zh
        elif vi in quai or (zh and zh in quai_by_zh):
            name = vi if vi in quai else quai_by_zh[zh]
            d = quai[name]
            rec = {"hanh": [d["ngu_hanh"]], "am_duong": d.get("am_duong"),
                   "nguon": f"ontology_nen.bat_quai[{name}]"}
            stats["primitive"] += 1

    # (3) quẻ (64) -> 2 quái -> hành (nạp quái)
    #   a) category 'que' uses King Wen single-glyph zh -> HEX table -> 2 trigrams
    #   b) ontology que_64 (Bát Cung names/zh) for any other quẻ concept
    if rec is None and cat in ("que", "quẻ", "hà-lạc-quẻ"):
        glyph = zh if zh in HEX else None
        if glyph:
            up, lo = HEX[glyph]              # upper, lower trigram zh
            up_vi, lo_vi = QUAI_VI[up], QUAI_VI[lo]
            up_h, lo_h = QUAI_HANH[up], QUAI_HANH[lo]
            hs = [up_h] + ([lo_h] if lo_h != up_h else [])
            rec = {"hanh": hs, "am_duong": None,
                   "nguon": f"nạp quái (quẻ King Wen {glyph}: "
                            f"thượng={up_vi}/{up_h}, hạ={lo_vi}/{lo_h}; "
                            f"hành quái ← ontology_nen.bat_quai)"}
            stats["que_quai"] += 1
    if rec is None:
        qname = None
        if vi in que64:
            qname = vi
        elif zh and zh in que_by_zh:
            qname = que_by_zh[zh]
        if qname:
            d = que64[qname]
            hs = []
            for hh in (d.get("ngu_hanh_thuong"), d.get("ngu_hanh_ha")):
                if hh and hh not in hs:
                    hs.append(hh)
            if hs:
                rec = {"hanh": hs, "am_duong": None,
                       "nguon": f"nạp quái (ontology_nen.que_64[{qname}]: "
                                f"thượng={d.get('thuong_quai')}/{d.get('ngu_hanh_thuong')}, "
                                f"hạ={d.get('ha_quai')}/{d.get('ngu_hanh_ha')})"}
                stats["que_quai"] += 1

    # (4) tường minh từ short_note
    if rec is None:
        got = hanh_from_note(note, vi, is_sao=(cat in ("sao", "thần sát", "than_sat")))
        if got:
            hs, sent = got
            rec = {"hanh": hs, "am_duong": None,
                   "nguon": f"trích short_note: \"{sent}\""}
            stats["tuong_minh"] += 1

    if rec is None:
        stats["no_hanh"] += 1
        continue

    rec = {"concept_id": cid, "canonical_vi": vi, "canonical_zh": zh or None,
           "category": cat, "school": r["school"],
           "hanh": rec["hanh"], "am_duong": rec.get("am_duong"),
           "nguon": rec["nguon"]}
    result[key] = rec

total = len(rows)
have = len(result)
OUT.write_text(json.dumps({
    "_meta": {
        "generated": "build_hanh_map.py",
        "total_concepts": total,
        "concepts_with_hanh": have,
        "skipped_thap_than": stats["skipped_thapthan"],
        "breakdown": stats,
        "nguon_rule": "1=canonical sao (chinh_tinh+chieu_dom phi tinh), "
                      "2=primitive (ontology can/chi/quái/hành), "
                      "3=quẻ→nạp quái, 4=trích short_note tường minh. "
                      "Thập thần Bát Tự BỎ QUA (hành phụ thuộc nhật chủ).",
    },
    "concepts": result,
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\nTOTAL concepts={total}  with_hanh={have}")
print("breakdown:", json.dumps(stats, ensure_ascii=False))
print("OUT:", OUT)
