#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enrich_obsidian_notes.py — BƠM THỊT nội dung thật vào note Obsidian.

POST-PROCESSOR (KHÔNG rmtree, KHÔNG dựng lại vault). Với mỗi note đã tồn tại
trong vault '🧠 Mạng Tri Thức YI', chèn/REPLACE đúng 1 mục:

    ## 📚 Nội dung (từ kho tri thức)

đặt TRƯỚC mọi mục link (giữ nguyên frontmatter + body tóm tắt + các mục
[[thuộc-phái]]/[[trích-từ-sách]]/[[đồng-hiện]]/[[hành của sao]]/[[sao cấu
thành]] + ## 🔗 Gần nghĩa).

Idempotent: dùng marker comment để khoanh vùng mục đã bơm, regex thay nguyên
mục cũ → chạy lại KHÔNG nhân đôi.

Nguồn nội dung theo frontmatter `type`:
  • chinh-tinh : engine.tu_vi.ngu_uan.get_star_v3 → 8 lớp + top-15 atom của sao
  • khai-niem  : retriever.search_atom_fts(canonical_vi) → top-15 atom + commentary
  • cach-cuc   : cach_cuc_index.json → định nghĩa + sao cấu thành + ý nghĩa

AN TOÀN:
  • Chỉ ghi trong OUT (vault). KHÔNG đụng file ngoài vault.
  • Đọc TÊN THẬT từ đĩa (macOS case-insensitive — không tin Path.exists).
  • KHÔNG sửa link đã có.
  • Nếu DB lỗi → thoát sạch (exit code != 0, không ghi gì).
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

VAULT = PROJECT_ROOT / "thư viện sách" / "🧠 Mạng Tri Thức YI"
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
CACH_CUC_INDEX = (
    PROJECT_ROOT / "data" / "yi_publishing" / "q1_tuvi" / "master" / "cach_cuc_index.json"
)

# Marker bao quanh mục bơm — dùng để regex thay idempotent.
BEGIN_MARK = "<!-- KHO-TRI-THUC:BEGIN -->"
END_MARK = "<!-- KHO-TRI-THUC:END -->"
SECTION_HEADING = "## 📚 Nội dung (từ kho tri thức)"

# Các dòng "mục link" — mục bơm phải đặt TRƯỚC dòng đầu tiên khớp một trong số này.
LINK_LINE_RE = re.compile(
    r"^(?:\*\*(?:thuộc-phái|trích-từ-sách|đồng-hiện|hành của sao|sao cấu thành|"
    r"Ngũ Hành|Cấp độ)\b|## 🔗|## 📚)"
)

ATOM_LIMIT = 15  # số atom bơm tối đa mỗi note concept / sao


# ─────────────────────────── helpers chung ───────────────────────────

def trunc(text: str | None, n: int) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def parse_frontmatter(content: str) -> dict:
    """Lấy field đơn giản trong frontmatter YAML (không cần PyYAML)."""
    fm: dict = {}
    if not content.startswith("---"):
        return fm
    end = content.find("\n---", 3)
    if end == -1:
        return fm
    block = content[3:end]
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def get_heading(content: str) -> str:
    m = re.search(r"^# (.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def canonical_from_note(content: str, fm: dict) -> str:
    """Tên canonical để tra kho.

    Sao: bỏ tiền tố 'Sao · '. Cách cục: bỏ 'Cách · '. Khái niệm: dùng heading.
    Ưu tiên aliases nếu có.
    """
    aliases = fm.get("aliases", "")
    if aliases:
        m = re.search(r'"([^"]+)"', aliases)
        if m:
            return m.group(1).strip()
    h = get_heading(content)
    for pref in ("Sao · ", "Cách · ", "Cung · "):
        if h.startswith(pref):
            return h[len(pref):].strip()
    return h.strip()


# ─────────────────────── render: chinh-tinh (8 lớp) ───────────────────────

def render_star(name: str, star, atoms_md: str) -> str | None:
    """8 lớp get_star_v3 + top atom. Render gọn bằng callout foldable."""
    if star is None:
        return None
    lines: list[str] = []

    def callout(title: str, body: str, fold: str = "-"):
        if not body or not str(body).strip():
            return
        lines.append(f"> [!note]{fold} {title}")
        for para in str(body).split("\n"):
            for sub in (para.splitlines() or [""]):
                lines.append(f"> {sub}")
        lines.append("")

    has_v3 = star.get("_has_v3")
    if not has_v3:
        lines.append(
            "> [!info] Sao này chưa có chân dung 8 lớp đầy đủ trong kho "
            "(chỉ có dữ liệu ngũ uẩn nền). Bơm phần đang có."
        )
        lines.append("")

    # ① Căn cơ âm dương / ngũ hành
    callout("① Căn cơ — âm dương / ngũ hành", star.get("l1_am_duong_ngu_hanh"))
    # ② Gốc tham
    callout("② Gốc tham", star.get("l2_goc_tham"))
    # ③ Ngũ uẩn 5 bước
    l3 = star.get("l3_ngu_uan")
    if l3:
        lines.append("> [!abstract]- ③ Ngũ uẩn — 5 bước")
        if isinstance(l3, list):
            for i, step in enumerate(l3, 1):
                if not isinstance(step, dict):
                    continue
                buoc = step.get("buoc") or f"Bước {i}"
                lines.append(f"> **{i}. {buoc}**")
                if step.get("mo_ta"):
                    lines.append(f"> {trunc(step['mo_ta'], 900)}")
                if step.get("khi_thuan"):
                    lines.append(f"> · _Khí thuận:_ {trunc(step['khi_thuan'], 400)}")
                if step.get("khi_ket"):
                    lines.append(f"> · _Khí kẹt:_ {trunc(step['khi_ket'], 400)}")
                lines.append(">")
        elif isinstance(l3, dict):
            # bản 5 uẩn cũ {sac, tho, tuong, hanh, thuc}
            order = [
                ("sac", "Sắc"), ("tho", "Thọ"), ("tuong", "Tưởng"),
                ("hanh", "Hành"), ("thuc", "Thức"),
            ]
            for key, lab in order:
                v = l3.get(key)
                if not v:
                    continue
                if isinstance(v, dict):
                    v = v.get("mo_ta") or json.dumps(v, ensure_ascii=False)
                lines.append(f"> **{lab}:** {trunc(v, 600)}")
                lines.append(">")
        lines.append("")
    # ④ Khí vượng-suy
    l4 = star.get("l4_khi_vuong_suy")
    if isinstance(l4, dict):
        body = []
        if l4.get("dac_dia"):
            body.append("**Đắc địa:** " + trunc(l4["dac_dia"], 700))
        if l4.get("ham_dia"):
            body.append("**Hãm địa:** " + trunc(l4["ham_dia"], 700))
        if l4.get("active_text"):
            body.append("**Đang ứng:** " + trunc(l4["active_text"], 400))
        callout("④ Khí vượng — suy", "\n".join(body))
    # ⑤ Theo đời người
    l5 = star.get("l5_theo_doi_nguoi")
    if isinstance(l5, dict):
        body = []
        for key, lab in [("nho", "Nhỏ"), ("thieu_nien", "Thiếu niên"),
                         ("trung_nien", "Trung niên"), ("ve_gia", "Về già")]:
            if l5.get(key):
                body.append(f"**{lab}:** " + trunc(l5[key], 500))
        callout("⑤ Theo đời người", "\n".join(body))
    # ⑥ Khe tỉnh thức + hướng tu tập
    body6 = []
    if star.get("l6_khe_tinh_thuc"):
        body6.append("**Khe tỉnh thức:** " + trunc(star["l6_khe_tinh_thuc"], 700))
    if star.get("l6_duong_ra"):
        body6.append("**Hướng tu tập:** " + trunc(star["l6_duong_ra"], 700))
    callout("⑥ Khe tỉnh thức + Hướng tu tập", "\n".join(body6))
    # ⑦ Ví dụ sống
    l7 = star.get("l7_vi_du_song")
    if l7:
        if isinstance(l7, (list, tuple)):
            l7 = "\n".join(f"- {trunc(x, 500)}" for x in l7)
        else:
            l7 = trunc(l7, 1200)
        callout("⑦ Ví dụ sống", l7)
    # ⑧ Căn cứ
    callout("⑧ Căn cứ", trunc(star.get("l8_can_cu"), 1200))

    if atoms_md:
        lines.append("### Trích kho — atom liên quan")
        lines.append("")
        lines.append(atoms_md)

    return "\n".join(lines).rstrip()


# ─────────────────── render: khai-niem (atom + commentary) ───────────────────

def fetch_dang_son(conn: sqlite3.Connection, atom_ids: list[int]) -> dict[int, dict]:
    """Lấy dang_son_applied + cross_school_notes trực tiếp (retriever bỏ qua
    dang_son). Chỉ commentary founder_verified >= 0 (≡ council)."""
    out: dict[int, dict] = {}
    if not atom_ids:
        return out
    qmarks = ",".join("?" * len(atom_ids))
    sql = (
        "SELECT atom_id, dang_son_applied, cross_school_notes, iron_rule_warning "
        "FROM atom_commentaries "
        f"WHERE atom_id IN ({qmarks}) AND founder_verified >= 0"
    )
    def _s(v):
        return str(v).strip() if v is not None else ""
    for r in conn.execute(sql, atom_ids):
        out[r[0]] = {
            "dang_son": _s(r[1]),
            "cross_school": _s(r[2]),
            "iron": _s(r[3]),
        }
    return out


def render_atoms(infos, extra: dict[int, dict]) -> str:
    """Render list atom → markdown. Ưu tiên atom có commentary (đã sort ở
    caller). Mỗi atom: câu hỏi + commentary fields + nguồn."""
    blocks: list[str] = []
    for a in infos:
        parts: list[str] = []
        q = (a.atom_question or "").strip()
        parts.append(f"**{trunc(q, 220)}**" if q else "**(atom)**")
        comm = a.commentary or {}
        ex = extra.get(a.atom_id, {})
        if comm.get("viet_thuan"):
            parts.append(f"- **Việt thuần:** {trunc(comm['viet_thuan'], 700)}")
        if comm.get("nguyen_ly"):
            parts.append(f"- **Nguyên lý:** {trunc(comm['nguyen_ly'], 700)}")
        # cross_school: ưu tiên bản trong commentary (retriever đã parse), fallback DB raw
        csn = comm.get("cross_school_notes") or ex.get("cross_school")
        if csn:
            if isinstance(csn, (list, dict)):
                csn = json.dumps(csn, ensure_ascii=False)
            parts.append(f"- **Đối chiếu phái:** {trunc(csn, 600)}")
        if ex.get("dang_son"):
            parts.append(f"- **Đằng Sơn:** {trunc(ex['dang_son'], 600)}")
        iron = comm.get("iron_rule_warning") or ex.get("iron")
        if iron:
            parts.append(f"- ⚠️ {trunc(iron, 400)}")
        if a.source_quote:
            parts.append(f"- _nguồn:_ {trunc(a.source_quote, 280)}")
        blocks.append("\n".join(parts))
    return "\n\n".join(blocks)


def _atom_sort_key(a):
    """Ưu tiên: có commentary sâu trước, founder_verified cao trước, score."""
    comm = a.commentary or {}
    has_deep = 1 if (comm.get("viet_thuan") or comm.get("nguyen_ly")) else 0
    return (-has_deep, -(a.founder_verified or 0), -(a.retrieval_score or 0))


# ─────────────────── render: cach-cuc (index json) ───────────────────

def render_cach_cuc(name: str, idx: dict) -> str | None:
    """Tra cach_cuc_index.json theo tên (khớp linh hoạt). Render định nghĩa +
    cấp độ + ý nghĩa + nguồn."""
    rec = idx.get(name)
    if rec is None:
        # khớp lỏng: strip dấu cách / so khớp không phân biệt hoa thường
        norm = name.lower().strip()
        for k, v in idx.items():
            if k.lower().strip() == norm:
                rec = v
                break
    if rec is None:
        return None
    lines: list[str] = []
    if rec.get("cap_do"):
        lines.append(f"**Cấp độ:** {rec['cap_do']}")
        lines.append("")
    dk = rec.get("dieu_kien") or rec.get("ten")
    if dk:
        lines.append(f"**Điều kiện / định nghĩa:** {trunc(dk, 500)}")
        lines.append("")
    if rec.get("y_nghia"):
        lines.append(f"**Ý nghĩa:** {trunc(rec['y_nghia'], 900)}")
        lines.append("")
    srcs = rec.get("sources") or []
    if srcs:
        bits = []
        for s in srcs[:4]:
            pg = s.get("page")
            bc = trunc(s.get("bang_chung"), 120)
            bits.append(f"tr.{pg}: {bc}" if pg else bc)
        lines.append("_nguồn:_ " + " · ".join(b for b in bits if b))
    return "\n".join(lines).rstrip() or None


# ─────────────────────────── ghép & ghi note ───────────────────────────

def build_section(inner: str) -> str:
    return (
        f"{BEGIN_MARK}\n{SECTION_HEADING}\n\n{inner}\n{END_MARK}"
    )


SECTION_BLOCK_RE = re.compile(
    re.escape(BEGIN_MARK) + r".*?" + re.escape(END_MARK) + r"\n?",
    re.DOTALL,
)


def inject(content: str, section: str) -> str:
    """Chèn/replace mục bơm. Idempotent qua marker. Đặt TRƯỚC dòng link đầu."""
    # 1. Xoá mục bơm cũ (nếu có) → tránh nhân đôi.
    content = SECTION_BLOCK_RE.sub("", content)

    lines = content.split("\n")
    # Tìm vị trí chèn: dòng đầu tiên là "mục link". Nếu không có → cuối file.
    insert_at = len(lines)
    # bỏ qua frontmatter khi quét
    in_fm = False
    fm_done = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm and not fm_done:
            if line.strip() == "---":
                fm_done = True
            continue
        if LINK_LINE_RE.match(line):
            insert_at = i
            break

    block = section.rstrip() + "\n"
    # đảm bảo có dòng trắng phân cách trước & sau
    before = lines[:insert_at]
    after = lines[insert_at:]
    # gọt trailing blank của before
    while before and before[-1].strip() == "":
        before.pop()
    new_lines = before + ["", block.rstrip(), ""] + after
    out = "\n".join(new_lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    if not out.endswith("\n"):
        out += "\n"
    return out


# ─────────────────────────── main ───────────────────────────

def iter_notes():
    """Đọc TÊN THẬT từ đĩa (rglob), chỉ trong vault, chỉ .md."""
    for p in sorted(VAULT.rglob("*.md")):
        yield p


def main() -> int:
    if not VAULT.is_dir():
        print(f"ERR: vault không tồn tại: {VAULT}", file=sys.stderr)
        return 2
    if not DB_PATH.exists():
        print(f"ERR: DB không tồn tại: {DB_PATH}", file=sys.stderr)
        return 2

    # Load cach cuc index (không bắt buộc thành công cho sao/concept).
    try:
        cach_cuc_idx = json.loads(CACH_CUC_INDEX.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"WARN: không đọc được cach_cuc_index: {e}", file=sys.stderr)
        cach_cuc_idx = {}

    # Mở DB + retriever — nếu lỗi thoát sạch.
    try:
        from engine.atomization.retriever import ChunkAtomRetriever
        from engine.tu_vi.ngu_uan import get_star_v3
        retriever = ChunkAtomRetriever()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1 FROM atom_commentaries LIMIT 1")
    except Exception as e:  # noqa: BLE001
        print(f"ERR: DB / engine lỗi — thoát sạch, không ghi gì: {e}", file=sys.stderr)
        return 3

    counts = {"chinh-tinh": 0, "khai-niem": 0, "cach-cuc": 0,
              "skip": 0, "no-content": 0, "error": 0}
    written = 0

    for path in iter_notes():
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            counts["error"] += 1
            continue
        # chỉ ghi trong VAULT (đã đảm bảo bởi rglob)
        try:
            path.resolve().relative_to(VAULT.resolve())
        except ValueError:
            continue

        fm = parse_frontmatter(content)
        ntype = fm.get("type", "")
        if ntype not in ("chinh-tinh", "khai-niem", "cach-cuc"):
            counts["skip"] += 1
            continue

        canonical = canonical_from_note(content, fm)
        if not canonical:
            counts["skip"] += 1
            continue

        inner: str | None = None
        try:
            if ntype == "chinh-tinh":
                star = get_star_v3(canonical)
                # top-15 atom của sao
                infos = retriever.search_atom_fts(canonical, limit=25)
                infos.sort(key=_atom_sort_key)
                infos = infos[:ATOM_LIMIT]
                ids = [a.atom_id for a in infos]
                extra = fetch_dang_son(conn, ids)
                atoms_md = render_atoms(infos, extra) if infos else ""
                inner = render_star(canonical, star, atoms_md)
                if inner is None:
                    inner = ("Chưa có chân dung sao trong kho cho sao này.\n\n"
                             + (atoms_md or ""))
                counts["chinh-tinh"] += 1

            elif ntype == "khai-niem":
                infos = retriever.search_atom_fts(canonical, limit=25)
                infos.sort(key=_atom_sort_key)
                infos = infos[:ATOM_LIMIT]
                if not infos:
                    inner = "_Chưa có atom trong kho cho khái niệm này._"
                    counts["no-content"] += 1
                else:
                    ids = [a.atom_id for a in infos]
                    extra = fetch_dang_son(conn, ids)
                    inner = render_atoms(infos, extra)
                    counts["khai-niem"] += 1

            elif ntype == "cach-cuc":
                inner = render_cach_cuc(canonical, cach_cuc_idx)
                if inner is None:
                    inner = "_Chưa có dữ liệu cách cục trong kho cho mục này._"
                    counts["no-content"] += 1
                else:
                    counts["cach-cuc"] += 1
        except Exception as e:  # noqa: BLE001
            counts["error"] += 1
            print(f"WARN: lỗi xử lý {path.name}: {e}", file=sys.stderr)
            continue

        if not inner or not inner.strip():
            inner = "_Chưa có nội dung trong kho._"

        section = build_section(inner.strip())
        new_content = inject(content, section)
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            written += 1

    conn.close()
    print(json.dumps({"written": written, **counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
