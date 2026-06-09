"""E2E Test — verify toàn bộ pipeline yi-chronos atomization.

Layers tested:
  1. Data layer (chunks, atoms, commentaries by section)
  2. Retriever (FTS search)
  3. OutputFiller (3-layer assembly + section priority)
  4. API endpoints (Workbench backend)
  5. Workbench UI (static HTML mount)
  6. Engine cũ v3/v4 (không bị phá)
  7. Decomposer (Algorithm 1 wrap)

Run:
    python3 scripts/e2e_test.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
API_BASE = "http://localhost:8001"

PASS = "✅"
FAIL = "❌"
WARN = "⚠ "

results = []


def check(name: str, ok: bool, detail: str = "") -> None:
    icon = PASS if ok else FAIL
    msg = f"{icon} {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append((name, ok, detail))


def http_get(path: str, timeout: float = 10.0) -> tuple[int, dict | None, str]:
    """Returns (status_code, json_body_or_None, raw_text)."""
    url = API_BASE + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        return e.code, None, str(e)
    except Exception as e:
        return 0, None, str(e)
    try:
        return status, json.loads(data), data
    except json.JSONDecodeError:
        return status, None, data


# ═══════════════════════════════════════════════════════════════════
# Layer 1: DATA LAYER
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 1: DATA LAYER")
print("═" * 60)

conn = sqlite3.connect(DB)

# Total counts
n_chunks = conn.execute("SELECT COUNT(*) FROM chunks_v2").fetchone()[0]
n_atoms = conn.execute("SELECT COUNT(*) FROM atomic_questions").fetchone()[0]
n_commentaries = conn.execute("SELECT COUNT(*) FROM atom_commentaries").fetchone()[0]
n_classifications = conn.execute("SELECT COUNT(*) FROM chunk_classifications").fetchone()[0]

check("chunks_v2 has data", n_chunks > 800, f"{n_chunks} chunks")
check("atomic_questions has data", n_atoms > 3000, f"{n_atoms} atoms")
check("atom_commentaries exist", n_commentaries > 0, f"{n_commentaries} commentaries 4-layer")
check("chunk_classifications exist", n_classifications > 0, f"{n_classifications} classifications")

# Section coverage
expected_sections = ["5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5"]
section_atoms = {}
for sec in expected_sections:
    n = conn.execute(
        "SELECT COUNT(*) FROM atomic_questions WHERE section_id=?", (sec,)
    ).fetchone()[0]
    section_atoms[sec] = n
    check(f"Section {sec} has atoms", n >= 6, f"{n} atoms")

# Commentaries match atoms ratio
n_atoms_with_comm = conn.execute("""
    SELECT COUNT(*) FROM atomic_questions aq
    JOIN atom_commentaries ac ON ac.atom_id = aq.atom_id
    WHERE aq.section_id IN ('5.1.1','5.1.2','5.1.3','5.1.4','5.1.5')
""").fetchone()[0]
n_atoms_in_5_1_x = sum(section_atoms.values())
check(
    "5.1.x atoms have commentaries",
    n_atoms_with_comm == n_atoms_in_5_1_x,
    f"{n_atoms_with_comm}/{n_atoms_in_5_1_x}",
)

# 4-layer commentary coverage (sample)
sample_comm = conn.execute("""
    SELECT han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song, iron_rule_warning
    FROM atom_commentaries
    JOIN atomic_questions ON atomic_questions.atom_id = atom_commentaries.atom_id
    WHERE atomic_questions.section_id='5.1.1'
    LIMIT 1
""").fetchone()
if sample_comm:
    han, viet, ngly, vidu, iron = sample_comm
    check("Layer 1 — Hán-Việt non-empty", bool(han and len(han) > 30))
    check("Layer 1 — Việt thuần non-empty", bool(viet and len(viet) > 50))
    check("Layer 2 — Nguyên lý non-empty", bool(ngly and len(ngly) > 50))
    check("Layer 3 — Ví dụ đời sống non-empty", bool(vidu and len(vidu) > 50))
    check("Iron Rule #6 warning non-empty", bool(iron and len(iron) > 30))

# Manifest exists
manifest = PROJECT_ROOT / "data/restored_books/trung-chau-tu-vi-dau-so-2/manifest.yaml"
check("manifest.yaml exists", manifest.exists(), f"{manifest.stat().st_size} bytes" if manifest.exists() else "missing")

# Engine cũ data preserved (passages KHÔNG đụng)
n_passages = conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
check("Legacy 'passages' table preserved", n_passages > 2000, f"{n_passages} rows")

conn.close()


# ═══════════════════════════════════════════════════════════════════
# Layer 2: RETRIEVER (FTS)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 2: RETRIEVER")
print("═" * 60)

sys.path.insert(0, str(PROJECT_ROOT))
from engine.atomization.retriever import ChunkAtomRetriever

retriever = ChunkAtomRetriever()
hits = retriever.search_atom_fts("bách quan triều củng", limit=5)
check("FTS search 'bách quan triều củng'", len(hits) > 0, f"{len(hits)} hits")
hits_511 = [h for h in hits if h.page_start == 503 or h.atom_id in [3451, 3452]]
check("FTS hits include section 5.1.1 atoms", len(hits_511) > 0, f"{[h.atom_id for h in hits_511]}")

hits_td = retriever.search_atom_fts("Thiên Đồng kích phát", limit=5)
check("FTS search 'Thiên Đồng kích phát'", len(hits_td) > 0, f"{len(hits_td)} hits")


# ═══════════════════════════════════════════════════════════════════
# Layer 3: OUTPUT FILLER (3-layer assembly)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 3: OUTPUT FILLER (3-layer)")
print("═" * 60)

from engine.atomization.output_filler import OutputFiller
from engine.atomization.output_template import OutputField, build_atomic_keywords

filler = OutputFiller(top_k_atoms=5)

# Test 5 sao đã insert
saved_stars = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng"]
expected_sections_map = {"Tử Vi": "5.1.1", "Thiên Cơ": "5.1.2", "Thái Dương": "5.1.3",
                          "Vũ Khúc": "5.1.4", "Thiên Đồng": "5.1.5"}

for sao in saved_stars:
    field = OutputField(
        field_id=f"Mệnh.{sao}.tong_quan",
        cung="Mệnh", sao_chinh=sao,
        variant=f"{sao} tại Mệnh", aspect="tong_quan",
        description_vi=f"Tổng quan {sao} Mệnh",
        atomic_q_keywords=build_atomic_keywords(sao, "Mệnh", "tong_quan"),
        section_priority={},
    )
    result = filler.fill_field(field)
    # Check layer 1 (viet_thuan) non-empty
    has_layer1 = bool(result.layer_1_narrative and len(result.layer_1_narrative) > 100)
    has_layer2 = bool(result.layer_2_nguyen_ly and len(result.layer_2_nguyen_ly) > 50)
    has_layer3 = len(result.layer_3_citations) >= 3
    # Check section priority — atoms should be from expected section
    exp_sec = expected_sections_map[sao]
    conn = sqlite3.connect(DB)
    atom_sections = []
    for aid in result.sources_atoms[:3]:
        row = conn.execute("SELECT section_id FROM atomic_questions WHERE atom_id=?", (aid,)).fetchone()
        if row:
            atom_sections.append(row[0])
    conn.close()
    correct_section = any(s == exp_sec for s in atom_sections)
    check(
        f"Mệnh × {sao} — Layer 1 (Chuyện về anh)",
        has_layer1,
        f"{len(result.layer_1_narrative)} chars",
    )
    check(
        f"Mệnh × {sao} — Layer 2 (Vì sao)",
        has_layer2,
        f"{len(result.layer_2_nguyen_ly)} chars",
    )
    check(
        f"Mệnh × {sao} — Layer 3 (Sách cổ)",
        has_layer3,
        f"{len(result.layer_3_citations)} citations",
    )
    check(
        f"Mệnh × {sao} — section priority hit {exp_sec}",
        correct_section,
        f"top atoms in: {atom_sections}",
    )


# ═══════════════════════════════════════════════════════════════════
# Layer 4: API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 4: API ENDPOINTS")
print("═" * 60)

# Health (engine cũ)
status, body, _ = http_get("/api/health")
check("GET /api/health", status == 200 and body and body.get("status") == "ok", str(body))

# Atomization stats
status, body, _ = http_get("/api/atomization/stats")
check(
    "GET /api/atomization/stats",
    status == 200 and body and body.get("n_atomic_questions", 0) > 3000,
    f"atoms={body.get('n_atomic_questions') if body else '?'}",
)

# Books
status, body, _ = http_get("/api/atomization/books")
check(
    "GET /api/atomization/books",
    status == 200 and isinstance(body, list) and len(body) >= 1,
    f"{len(body) if isinstance(body, list) else '?'} books",
)

# Output template stats
status, body, _ = http_get("/api/atomization/output/template-stats")
check(
    "GET /api/atomization/output/template-stats",
    status == 200 and body and body.get("total_fields", 0) > 800,
    f"{body.get('total_fields') if body else '?'} fields",
)

# Output preview for each saved star
for sao in saved_stars:
    qs = urllib.parse.urlencode({"cung": "Mệnh", "sao": sao, "aspect": "tong_quan", "top_k": 5})
    status, body, _ = http_get(f"/api/atomization/output/preview?{qs}", timeout=15)
    layer1_ok = body and len(body.get("layer_1_narrative", "")) > 100
    citations_ok = body and len(body.get("layer_3_citations", [])) >= 3
    check(
        f"GET output/preview Mệnh×{sao}",
        status == 200 and layer1_ok and citations_ok,
        f"L1={len(body.get('layer_1_narrative','')) if body else 0} chars, "
        f"L3={len(body.get('layer_3_citations',[])) if body else 0} citations",
    )

# Sections endpoint
status, body, _ = http_get("/api/atomization/books/trung-chau-tu-vi-dau-so-2/sections")
check(
    "GET /sections/trung-chau-tu-vi-dau-so-2",
    status == 200 and isinstance(body, list) and len(body) > 50,
    f"{len(body) if isinstance(body, list) else '?'} sections detected",
)

# Atom search
qs = urllib.parse.urlencode({"q": "Tử Vi bách quan"})
status, body, _ = http_get(f"/api/atomization/atom/search?{qs}")
check(
    "GET /atom/search 'Tử Vi bách quan'",
    status == 200 and isinstance(body, list) and len(body) > 0,
    f"{len(body) if isinstance(body, list) else '?'} hits",
)


# ═══════════════════════════════════════════════════════════════════
# Layer 5: WORKBENCH UI (static HTML)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 5: WORKBENCH UI")
print("═" * 60)

status, _, html = http_get("/workbench/")
check(
    "GET /workbench/ HTML",
    status == 200 and "Atomization Workbench" in html,
    f"{len(html)} bytes",
)

# Check 3-layer template in HTML
check("Workbench has LỚP 1 markup", "LỚP 1 — CHUYỆN VỀ ANH" in html)
check("Workbench has LỚP 2 markup", "LỚP 2 — VÌ SAO LẠI THẾ" in html)
check("Workbench has LỚP 3 markup", "LỚP 3 — SÁCH CỔ ĐÃ NÓI" in html)


# ═══════════════════════════════════════════════════════════════════
# Layer 6: ENGINE CŨ (không bị phá)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 6: ENGINE CŨ v3/v4")
print("═" * 60)

# Check engine v3/v4 vẫn import được
try:
    from engine.tu_vi import chiem_phu_the_v3, chiem_phu_the_v4
    check("engine.tu_vi.chiem_phu_the_v3 import OK", True)
    check("engine.tu_vi.chiem_phu_the_v4 import OK", True)
except Exception as e:
    check("engine v3/v4 import", False, str(e))

# Check chinh_tinh.json schema (engine cũ rely on)
chinh_tinh_path = PROJECT_ROOT / "data/tu_vi/chinh_tinh.json"
if chinh_tinh_path.exists():
    d = json.loads(chinh_tinh_path.read_text())
    n_stars = len(d.get("stars", []))
    check("chinh_tinh.json — 14 chính tinh schema", n_stars == 14, f"{n_stars} stars")


# ═══════════════════════════════════════════════════════════════════
# Layer 7: DECOMPOSER (Algorithm 1)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("LAYER 7: DECOMPOSER (Algorithm 1)")
print("═" * 60)

try:
    from engine.atomization.decomposer import KnowledgeAwareDecomposer
    check("Decomposer class import OK", True)
    # Don't actually invoke (would need LLM call) — just verify class structure
    d_cls = KnowledgeAwareDecomposer
    has_decompose = hasattr(d_cls, "decompose")
    check("Decomposer.decompose() method exists", has_decompose)
except Exception as e:
    check("Decomposer import", False, str(e))


# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("SUMMARY")
print("═" * 60)
n_pass = sum(1 for _, ok, _ in results if ok)
n_fail = sum(1 for _, ok, _ in results if not ok)
total = len(results)
print(f"\n  ✅ PASS: {n_pass}/{total}")
print(f"  ❌ FAIL: {n_fail}/{total}")

if n_fail > 0:
    print("\n  Failed checks:")
    for name, ok, detail in results:
        if not ok:
            print(f"    - {name}: {detail}")
    sys.exit(1)
else:
    print("\n  🎯 ALL GREEN — Pipeline E2E healthy")
    sys.exit(0)
