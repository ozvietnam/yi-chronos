"""Luận sâu Mai Hoa — gọi LLM với citation Kinh Dịch nguyên văn (RAG).

Khác `interpret.py` (thuần tính toán Thể-Dụng + Quái Khí + Tam Yếu):
- Endpoint này build prompt cho LLM với context = citation Kinh Dịch tương ứng
- LLM sinh phê quẻ sâu theo paradigm "đồng dạng + Tam Tài + quan-vật-trace-tính"
- KHÔNG predict cát hung tĩnh (Iron Rule #4 Mai Hoa)

Routing strategy:
1. Cast result → 2 bát quái (upper + lower) → load citation gốc nếu có
   (Càn → 01-kien.md, Khôn → 02-khon.md...)
2. Intent (gia trạch/cầu danh/...) → load tâm-phap file phù hợp
3. Hào động (1-6) → có thể có insight riêng (vd: hào 1 ⇒ Tiềm long/Lý sương)
4. Compose prompt với citations capped (max ~12k chars) để không vọng context

Source citation files: data/hermes_yi/skills/kinh-dich/{quẻ,tam-phap}/*.md
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_skills_root() -> Path:
    """Resolve kinh-dich skills folder. Prefer mounted data/, fallback embedded_data/.

    Local dev: data/hermes_yi/skills/kinh-dich/ (git-tracked, mounted)
    Production VPS: volume mount /opt/yi-chronos/data shadows data/ in image,
    nhưng /opt/yi-chronos/data có thể không có skills/. Fallback embedded_data/
    (đã COPY vào Docker image — version-controlled knowledge).
    """
    primary = _PROJECT_ROOT / "data" / "hermes_yi" / "skills" / "kinh-dich"
    if (primary / "INDEX.md").exists():
        return primary
    embedded = _PROJECT_ROOT / "embedded_data" / "hermes_yi" / "skills" / "kinh-dich"
    if (embedded / "INDEX.md").exists():
        return embedded
    # Last resort: still return primary so caller sees consistent path in
    # error messages (load returns empty body).
    return primary


_SKILLS_ROOT = _resolve_skills_root()

# 8 bát quái → quẻ thuần (cùng tên trên-dưới) → file citation
# Hiện chỉ có Càn + Khôn. Sau khi đọc tiếp sẽ có thêm.
_BAT_QUAI_TO_FILE: dict[str, str] = {
    "Càn": "quẻ/01-kien.md",
    "Khôn": "quẻ/02-khon.md",
    # Đoài, Ly, Chấn, Tốn, Khảm, Cấn → chưa có quẻ thuần citation
}

# 11 quẻ đã THÂM NHUẦN ĐẦY ĐỦ (đọc Trình Di + Chu Hy + Tiên Nho nguyên văn).
# Citation files 80-130 dòng, có trích dẫn nguyên văn → LLM luận sâu chính xác.
_DEEP_QUE_FILES: set[str] = {
    "quẻ/01-kien.md",
    "quẻ/02-khon.md",
    "quẻ/03-truan.md",
    "quẻ/04-mong.md",
    "quẻ/05-nhu.md",
    "quẻ/06-tung.md",
    "quẻ/07-su.md",        # 2026-05-27 cụm 1
    "quẻ/08-ty.md",
    "quẻ/09-tieu-suc.md",  # cụm 1
    "quẻ/10-ly.md",        # cụm 1
    "quẻ/11-thai.md",
    "quẻ/12-bi.md",
    "quẻ/13-dong-nhan.md", # 2026-05-27 cụm 2 deep
    "quẻ/14-dai-huu.md",   # cụm 2
    "quẻ/15-khiem.md",
    "quẻ/16-du.md",        # cụm 2
    "quẻ/17-tuy.md",       # cụm 2
    "quẻ/18-co.md",        # cụm 2
    "quẻ/19-lam.md",       # cụm 2
    "quẻ/20-quan.md",
    "quẻ/21-phe-hap.md",
    "quẻ/22-bi.md",
    "quẻ/23-bac.md",       # 2026-05-27 cụm 3 deep
    "quẻ/24-phuc.md",      # cụm 3
    "quẻ/25-vo-vong.md",   # cụm 3 (OCR p421-450 missing, canonical Trình Di)
    "quẻ/26-dai-suc.md",   # cụm 3
    "quẻ/27-di.md",        # cụm 3
    "quẻ/28-dai-qua.md",   # cụm 3 (OCR p476-500 missing for 6 hào)
    "quẻ/29-kham.md",      # 2026-05-27 cụm 4 (OCR p476-500 missing)
    "quẻ/30-ly-hexagram.md",  # cụm 4 (partial OCR hào 2-Thượng)
    "quẻ/31-ham.md",       # cụm 4 (full OCR p507-520)
    "quẻ/32-hang.md",      # cụm 4 (OCR p525-550 missing for 6 hào)
    "quẻ/33-don.md",       # cụm 4 (OCR p526-550 missing)
    "quẻ/34-dai-trang.md", # cụm 4 (partial OCR hào 3-Thượng)
    "quẻ/35-tan.md",       # 2026-05-27 cụm 5 (full OCR)
    "quẻ/36-minh-di.md",   # cụm 5 (full OCR)
    "quẻ/37-gia-nhan.md",  # cụm 5 (OCR p581-600 missing — canonical)
    "quẻ/38-khue.md",      # cụm 5 (OCR full p600-622)
    "quẻ/39-kien.md",      # cụm 5 (full OCR)
    "quẻ/40-giai.md",      # cụm 5 (full OCR)
    "quẻ/41-ton.md",       # 2026-05-27 cụm 6 (full OCR p636-651)
    "quẻ/42-ich.md",       # cụm 6 (full OCR p652-665)
    "quẻ/43-quai.md",      # cụm 6 (canonical Trình Di)
    "quẻ/44-cau.md",       # cụm 6 (canonical Trình Di)
    "quẻ/45-tuy-hexagram.md",  # cụm 6 (canonical)
    "quẻ/46-thang.md",     # cụm 6 (canonical)
    "quẻ/47-khon-hexagram.md", # 2026-05-27 cụm 7 (canonical Trình Di)
    "quẻ/48-tinh.md",      # cụm 7 (canonical)
    "quẻ/49-cach.md",      # cụm 7 (canonical)
    "quẻ/50-dinh.md",      # cụm 7 (canonical)
    "quẻ/51-chan.md",      # 2026-05-27 cụm 8 (canonical Trình Di)
    "quẻ/52-can-hexagram.md",  # cụm 8 (canonical)
    "quẻ/53-tiem.md",      # cụm 8 (canonical)
    "quẻ/54-qui-muoi.md",  # cụm 8 (canonical)
    "quẻ/55-phong.md",     # cụm 8 (canonical)
    "quẻ/56-lu.md",        # cụm 8 (canonical)
    "quẻ/57-ton-hexagram.md",  # 2026-05-27 cụm 9 final (canonical)
    "quẻ/58-doai.md",      # cụm 9
    "quẻ/59-hoan.md",      # cụm 9
    "quẻ/60-tiet.md",      # cụm 9
    "quẻ/61-trung-phu.md", # cụm 9 (Trung Phu = gốc "hữu phu")
    "quẻ/62-tieu-qua.md",  # cụm 9
    "quẻ/63-ky-te.md",     # cụm 9
    "quẻ/64-vi-te.md",     # cụm 9 — HOÀN THÀNH 64 quẻ
}

# 64 hexagram (upper, lower) → file citation.
# Đợt 4-6 (51 quẻ) là STUB ultra-skim — chỉ có paradigm chung, KHÔNG có trích dẫn
# nguyên văn Trình Di/Chu Hy. select_citations() SẼ KHÔNG inject stub vào prompt.
# Roadmap thâm nhuần 51 quẻ stub: ~13 phiên × 3-5 quẻ/phiên đọc Trình Di + Chu Hy thật.
_HEXAGRAM_TO_FILE: dict[tuple[str, str], str] = {
    ("Càn", "Càn"): "quẻ/01-kien.md",        # 1 Kiền
    ("Khôn", "Khôn"): "quẻ/02-khon.md",      # 2 Khôn
    ("Khảm", "Chấn"): "quẻ/03-truan.md",     # 3 Truân
    ("Cấn", "Khảm"): "quẻ/04-mong.md",       # 4 Mông
    ("Khảm", "Càn"): "quẻ/05-nhu.md",        # 5 Nhu
    ("Càn", "Khảm"): "quẻ/06-tung.md",       # 6 Tụng
    ("Khôn", "Khảm"): "quẻ/07-su.md",        # 7 Sư
    ("Khảm", "Khôn"): "quẻ/08-ty.md",        # 8 Tỵ
    ("Tốn", "Càn"): "quẻ/09-tieu-suc.md",    # 9 Tiểu Súc
    ("Càn", "Đoài"): "quẻ/10-ly.md",         # 10 Lý
    ("Khôn", "Càn"): "quẻ/11-thai.md",       # 11 Thái (đảo!)
    ("Càn", "Khôn"): "quẻ/12-bi.md",         # 12 Bĩ
    ("Càn", "Ly"): "quẻ/13-dong-nhan.md",    # 13 Đồng Nhân
    ("Ly", "Càn"): "quẻ/14-dai-huu.md",      # 14 Đại Hữu
    ("Khôn", "Cấn"): "quẻ/15-khiem.md",      # 15 Khiêm
    ("Chấn", "Khôn"): "quẻ/16-du.md",        # 16 Dự
    ("Đoài", "Chấn"): "quẻ/17-tuy.md",       # 17 Tùy
    ("Cấn", "Tốn"): "quẻ/18-co.md",          # 18 Cổ
    ("Khôn", "Đoài"): "quẻ/19-lam.md",       # 19 Lâm
    ("Tốn", "Khôn"): "quẻ/20-quan.md",       # 20 Quán
    ("Ly", "Chấn"): "quẻ/21-phe-hap.md",     # 21 Phệ Hạp (đọc raw_ocr)
    ("Cấn", "Ly"): "quẻ/22-bi.md",           # 22 Bí (đọc raw_ocr)
    # Đợt 5 — skim mode
    ("Cấn", "Khôn"): "quẻ/23-bac.md",        # 23 Bác
    ("Khôn", "Chấn"): "quẻ/24-phuc.md",      # 24 Phục
    ("Cấn", "Chấn"): "quẻ/27-di.md",         # 27 Di
    ("Đoài", "Tốn"): "quẻ/28-dai-qua.md",    # 28 Đại Quá
    ("Đoài", "Cấn"): "quẻ/31-ham.md",        # 31 Hàm
    ("Chấn", "Tốn"): "quẻ/32-hang.md",       # 32 Hằng
    ("Ly", "Khôn"): "quẻ/35-tan.md",         # 35 Tấn
    ("Khôn", "Ly"): "quẻ/36-minh-di.md",     # 36 Minh Di
    ("Khảm", "Cấn"): "quẻ/39-kien.md",       # 39 Kiển
    ("Chấn", "Khảm"): "quẻ/40-giai.md",      # 40 Giải
    ("Cấn", "Đoài"): "quẻ/41-ton.md",        # 41 Tổn
    ("Tốn", "Chấn"): "quẻ/42-ich.md",        # 42 Ích
    # Đợt 6 — hoàn thành 62/64 quẻ (2 defer: 21 Phệ Hạp + 22 Bí)
    ("Càn", "Chấn"): "quẻ/25-vo-vong.md",    # 25 Vô Vọng
    ("Cấn", "Càn"): "quẻ/26-dai-suc.md",     # 26 Đại Súc
    ("Khảm", "Khảm"): "quẻ/29-kham.md",      # 29 Khảm (thuần)
    ("Ly", "Ly"): "quẻ/30-ly-hexagram.md",   # 30 Ly (thuần)
    ("Càn", "Cấn"): "quẻ/33-don.md",         # 33 Độn
    ("Chấn", "Càn"): "quẻ/34-dai-trang.md",  # 34 Đại Tráng
    ("Tốn", "Ly"): "quẻ/37-gia-nhan.md",     # 37 Gia Nhân
    ("Ly", "Đoài"): "quẻ/38-khue.md",        # 38 Khuê
    ("Đoài", "Càn"): "quẻ/43-quai.md",       # 43 Quải
    ("Càn", "Tốn"): "quẻ/44-cau.md",         # 44 Cấu
    ("Đoài", "Khôn"): "quẻ/45-tuy-hexagram.md",  # 45 Tụy
    ("Khôn", "Tốn"): "quẻ/46-thang.md",      # 46 Thăng
    ("Đoài", "Khảm"): "quẻ/47-khon-hexagram.md",  # 47 Khốn
    ("Khảm", "Tốn"): "quẻ/48-tinh.md",       # 48 Tỉnh
    ("Đoài", "Ly"): "quẻ/49-cach.md",        # 49 Cách
    ("Ly", "Tốn"): "quẻ/50-dinh.md",         # 50 Đỉnh
    ("Chấn", "Chấn"): "quẻ/51-chan.md",      # 51 Chấn (thuần)
    ("Cấn", "Cấn"): "quẻ/52-can-hexagram.md", # 52 Cấn (thuần)
    ("Tốn", "Cấn"): "quẻ/53-tiem.md",        # 53 Tiệm
    ("Chấn", "Đoài"): "quẻ/54-qui-muoi.md",  # 54 Qui Muội
    ("Chấn", "Ly"): "quẻ/55-phong.md",       # 55 Phong
    ("Ly", "Cấn"): "quẻ/56-lu.md",           # 56 Lữ
    ("Tốn", "Tốn"): "quẻ/57-ton-hexagram.md", # 57 Tốn (thuần)
    ("Đoài", "Đoài"): "quẻ/58-doai.md",      # 58 Đoài (thuần)
    ("Tốn", "Khảm"): "quẻ/59-hoan.md",       # 59 Hoán
    ("Khảm", "Đoài"): "quẻ/60-tiet.md",      # 60 Tiết
    ("Tốn", "Đoài"): "quẻ/61-trung-phu.md",  # 61 Trung Phu
    ("Chấn", "Cấn"): "quẻ/62-tieu-qua.md",   # 62 Tiểu Quá
    ("Khảm", "Ly"): "quẻ/63-ky-te.md",       # 63 Ký Tế
    ("Ly", "Khảm"): "quẻ/64-vi-te.md",       # 64 Vị Tế (QUẺ CUỐI)
}

# Intent → tâm-phap file
_INTENT_TO_TAM_PHAP: dict[str, str] = {
    "khoi_dau": "tam-phap/khoi-dau.md",
    "cau_danh": "tam-phap/khoi-dau.md",       # cầu danh = khởi đầu
    "khiem_ton": "tam-phap/khiem-ton.md",
    "hop_tac": "tam-phap/khiem-ton.md",
    "thay_doi": "tam-phap/giao-thoa.md",
    "gia_trach": "tam-phap/giao-thoa.md",     # nhà cửa cần giao thoa
    "tat_benh": "tam-phap/dau-hieu-som.md",
    "general": "tam-phap/giao-thoa.md",       # default = giao thoa
}


def _strip_yaml_frontmatter(text: str) -> str:
    """Skip YAML frontmatter (--- ... ---) ở đầu file để chỉ giữ body."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    return text[end + 4:].lstrip()


def _load_citation_file(relpath: str) -> str:
    """Load 1 citation file từ skills/kinh-dich/. Return body (skip frontmatter).
    Trả về empty string nếu file không tồn tại — caller chịu trách nhiệm degrade."""
    f = _SKILLS_ROOT / relpath
    if not f.exists():
        return ""
    try:
        text = f.read_text(encoding="utf-8")
        return _strip_yaml_frontmatter(text)
    except Exception:
        return ""


# Tên hào trong markdown (Sơ Cửu/Lục, Cửu Nhị, ..., Thượng Cửu/Lục)
_HAO_NAMES_BY_NUM = {
    1: ["Sơ Cửu", "Sơ Lục"],
    2: ["Cửu Nhị", "Lục Nhị"],
    3: ["Cửu Tam", "Lục Tam"],
    4: ["Cửu Tứ", "Lục Tứ"],
    5: ["Cửu Ngũ", "Lục Ngũ"],
    6: ["Thượng Cửu", "Thượng Lục"],
}


def _compact_citation(body: str, moving_line: int = 0, *, max_chars: int = 4000) -> str:
    """Trích section relevant từ body markdown để giảm token LLM.

    Strategy (Phong "nhật trung tắc trắc" — đỉnh phải biết tiết):
    1. GIỮ section trước "## 6 hào" (Tóm cốt + Lời Kinh + Lời Thoán + Lời Tượng + Insight cốt)
    2. Nếu có moving_line (1-6): trong table "## 6 hào", chỉ giữ DÒNG đó + section "## Insight {hào}"
    3. SKIP "## Cross-ref" cuối (cross-quẻ network — không cần cho prompt)
    4. Truncate nếu vẫn > max_chars (giữ phần đầu).

    Args:
        body: markdown body của 1 quẻ
        moving_line: 1-6, hào động. 0 = không có (đọc cả quẻ → giữ insight chung)
        max_chars: cap cứng

    Returns:
        Compact markdown (50-70% kích thước gốc, giữ insight cốt).
    """
    if not body:
        return ""

    lines = body.split("\n")
    # Find anchors
    section_starts: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(.+)$", ln.strip())
        if m:
            section_starts.append((i, m.group(1).strip()))

    # Identify "6 hào" section + "Cross-ref" section
    hao_section_start = -1
    crossref_start = -1
    insight_starts: list[tuple[int, str, int]] = []  # (line_idx, title, hao_num)

    for idx, (line_idx, title) in enumerate(section_starts):
        title_lower = title.lower()
        if hao_section_start < 0 and "6 hào" in title_lower:
            hao_section_start = line_idx
        if crossref_start < 0 and ("cross-ref" in title_lower or "cross synthesis" in title_lower):
            crossref_start = line_idx
        # Insight {hào} sections
        if "insight" in title_lower:
            # Try detect hào: "Sơ Cửu", "Cửu Nhị" etc. in title
            for n, names in _HAO_NAMES_BY_NUM.items():
                if any(name in title for name in names):
                    insight_starts.append((line_idx, title, n))
                    break

    out: list[str] = []

    # === Part 1: Trước "## 6 hào" (giữ nguyên Lời Kinh + Lời Thoán + Lời Tượng) ===
    pre_end = hao_section_start if hao_section_start > 0 else (crossref_start if crossref_start > 0 else len(lines))
    out.extend(lines[:pre_end])

    # === Part 2: 6 hào table — chỉ giữ moving_line row ===
    if hao_section_start >= 0 and moving_line in _HAO_NAMES_BY_NUM:
        hao_end = crossref_start if crossref_start > hao_section_start else len(lines)
        # Find table within [hao_section_start, hao_end)
        table_started = False
        kept_rows: list[str] = []
        header_row = None
        sep_row = None
        names_for_hao = _HAO_NAMES_BY_NUM[moving_line]
        for i in range(hao_section_start, hao_end):
            ln = lines[i]
            if ln.strip().startswith("|"):
                if not table_started:
                    header_row = ln
                    table_started = True
                    continue
                if sep_row is None and re.match(r"^\|\s*[-:]+", ln.strip()):
                    sep_row = ln
                    continue
                # Data row — keep only if contains hào name
                if any(name in ln for name in names_for_hao):
                    kept_rows.append(ln)
            elif table_started and ln.strip() == "":
                # Table ended
                break
        if header_row and kept_rows:
            out.append("")
            out.append(f"## 6 hào (chỉ hào động {moving_line})")
            out.append("")
            out.append(header_row)
            if sep_row:
                out.append(sep_row)
            out.extend(kept_rows)

    # === Part 3: Insight section cho hào động (nếu match) ===
    if moving_line > 0:
        for (line_idx, _title, n) in insight_starts:
            if n == moving_line:
                # Find next section or crossref or end
                next_section_line = len(lines)
                for next_idx, _ in section_starts:
                    if next_idx > line_idx:
                        next_section_line = next_idx
                        break
                out.append("")
                out.extend(lines[line_idx:next_section_line])

    text = "\n".join(out)

    # === Truncate if still over budget ===
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n_(...compacted)_"
    return text


def select_citations(
    *,
    chinh_upper: str,
    chinh_lower: str,
    bien_upper: str,
    bien_lower: str,
    ho_upper: str,
    ho_lower: str,
    intent: Optional[str] = None,
    moving_line: int = 0,
    max_chars: int = 12000,
    compact: bool = True,
) -> dict:
    """Chọn citation files cho 1 lần luận sâu.

    Logic ưu tiên:
    1. Hexagram exact match cho chính/biến/hỗ (nếu có file)
    2. Bát quái match (quẻ thuần) cho upper/lower nếu hexagram chưa có
    3. Tâm-pháp file theo intent
    4. Index.md luôn load (master router context)

    Returns:
        {
            "citations": [{"path": ..., "body": ..., "reason": ...}, ...],
            "total_chars": int,
            "dropped": ["path due to limit"],
        }
    """
    seen_paths: set[str] = set()
    citations: list[dict] = []
    total = 0

    def _try_add(path: str, reason: str, hexagram_compact: bool = False, hao: int = 0) -> None:
        """Add citation. If hexagram_compact, extract relevant section per hao."""
        nonlocal total
        if not path or path in seen_paths:
            return
        body = _load_citation_file(path)
        if not body:
            return
        # COST OPTIMIZATION (Idea E 2026-05-27):
        # Quẻ markdown trung bình ~5500 chars. 3 quẻ + tâm-pháp + INDEX = 18-22k.
        # Compact: giữ Lời Kinh/Thoán/Tượng + dòng hào động + insight hào →
        # giảm ~50-60% per quẻ → tổng ~9-10k (đủ budget LLM).
        if compact and hexagram_compact:
            body = _compact_citation(body, moving_line=hao)
        if total + len(body) > max_chars:
            return
        seen_paths.add(path)
        citations.append({"path": path, "body": body, "reason": reason})
        total += len(body)

    # 1. Index master (~500 chars, always)
    _try_add("INDEX.md", "master router")

    # 2. Hexagram exact match — CHỈ inject quẻ đã THÂM NHUẦN ĐẦY ĐỦ
    # (stub files đợt 4-6 chỉ có paradigm chung, KHÔNG có trích dẫn nguyên văn
    # → KHÔNG đủ depth cho LLM luận sâu).
    # COST OPTIMIZATION: compact ALL hexagram files (chính keeps moving_line hào;
    # biến/hỗ drop hào table entirely + cross-ref → giảm ~50% total context).
    for label, upper, lower in [
        ("chính", chinh_upper, chinh_lower),
        ("biến", bien_upper, bien_lower),
        ("hỗ", ho_upper, ho_lower),
    ]:
        path = _HEXAGRAM_TO_FILE.get((upper, lower))
        if path and path in _DEEP_QUE_FILES:
            # chính: giữ hào động; biến/hỗ: drop hào table (chỉ giữ Lời Kinh/Thoán)
            hao_for_quẻ = moving_line if label == "chính" else 0
            _try_add(path, f"quẻ {label} {upper}/{lower}",
                     hexagram_compact=True, hao=hao_for_quẻ)
        elif path:
            # File tồn tại nhưng là stub → ghi nhận để UI báo user
            citations.append({
                "path": path,
                "body": "",
                "reason": f"⚠️ quẻ {label} {upper}/{lower} chưa thâm nhuần đầy đủ (stub)",
                "is_stub": True,
            })

    # 3. Bát quái thuần (fallback) cho 2 trigrams của chính quẻ
    # Vd: Quẻ Đại Hữu (Ly/Càn) chưa có file → load Càn (01-kien) làm gốc Dương
    for trig in (chinh_upper, chinh_lower, bien_upper, bien_lower):
        path = _BAT_QUAI_TO_FILE.get(trig)
        if path:
            _try_add(path, f"bát quái {trig}")

    # 4. Tâm-pháp theo intent
    if intent:
        path = _INTENT_TO_TAM_PHAP.get(intent)
        if path:
            _try_add(path, f"tâm-pháp intent={intent}")
    # Fallback intent
    _try_add("tam-phap/giao-thoa.md", "tâm-pháp default (Thái-Bĩ paradigm)")

    # Phân loại: deep (có body) vs stub (chỉ marker — KHÔNG inject prompt)
    deep_cites = [c for c in citations if not c.get("is_stub")]
    stub_cites = [c for c in citations if c.get("is_stub")]

    return {
        "citations": deep_cites,        # chỉ deep dùng cho LLM prompt
        "total_chars": total,
        "files_used": [c["path"] for c in deep_cites],
        "stubs_skipped": [c["path"] for c in stub_cites],
        "has_deep_citations": bool(deep_cites and total > 1000),
    }


def build_luan_sau_prompt(
    *,
    cast: dict,
    analyze: dict,
    citations_pack: dict,
    user_question: Optional[str] = None,
) -> str:
    """Build prompt cho LLM luận sâu Mai Hoa.

    Paradigm: Iron Rule #4 (Mai Hoa = ĐỌC ĐỒNG DẠNG, KHÔNG predict).
    """
    citation_text = "\n\n".join(
        f"### [{c['reason']}] — {c['path']}\n{c['body']}"
        for c in citations_pack["citations"]
    )

    cast_block = f"""**Kết quả gieo quẻ Mai Hoa**:
- Quẻ chính: {cast['chinh_quai']['name']} (Quẻ {cast['chinh_quai'].get('name_vi', '?')})
- Quẻ biến: {cast['bien_quai']['name']} (Quẻ {cast['bien_quai'].get('name_vi', '?')})
- Quẻ hỗ: {cast['ho_quai']['name']} (Quẻ {cast['ho_quai'].get('name_vi', '?')})
- Hào động: {cast['moving_line']} (1=hào đầu, 6=hào trên)
- Cảnh báo hỗ: {cast.get('ho_warning', 'không')}
"""

    analyze_block = f"""**Phân tích kỹ thuật** (đã computed):
- Thể-Dụng: {analyze['the_dung']['the_que']} (Thể) / {analyze['the_dung']['dung_que']} (Dụng)
- Quan hệ: {analyze['the_dung']['relationship']} → auspice: {analyze['the_dung']['auspice']}
- Mùa: {analyze['quai_khi']['season']}, Vượng: {analyze['quai_khi']['vuong']}, Suy: {analyze['quai_khi']['suy']}
- Trạng thái Thể: {analyze['quai_khi']['the_status']}
- Overall: {analyze['overall']}
- Intent: {analyze['intent']['label']} ({analyze['intent']['key']})
"""

    return f"""Bạn là **bậc trí giả Mai Hoa Dịch Số** (梅花易數), kế thừa Thiệu Khang Tiết.

## ⚠️ Paradigm BẮT BUỘC (Iron Rule #4 — KHÔNG vượt qua)

Mai Hoa = **MÔN HỌC ĐỒNG DẠNG**:
- Cấu trúc vũ trụ = cấu trúc người = cấu trúc khoảnh khắc
- Người và vũ trụ NGANG NHAU (Tam Tài)
- **Quan-vật-trace-tính** (xem vật để hiểu Tính ẩn) — KHÔNG predict cát/hung tĩnh

❌ TUYỆT ĐỐI TRÁNH (paradigm sai):
- "Quẻ này dự đoán cát/hung"
- "Anh sẽ thành công/thất bại"
- "Tương lai sẽ X"

✅ PHẢI dùng (paradigm tổ sư):
- "Khoảnh khắc anh hỏi phản chiếu cái gì lớn hơn trong vũ trụ?"
- "Tâm anh đang ở vị trí nào trong tổng thể?"
- "Vũ trụ đang nói qua khoảnh khắc này: ..."

## 📚 Citation Kinh Dịch nguyên văn (RAG context)

{citation_text}

---

## 🎯 Yêu cầu luận sâu

{cast_block}

{analyze_block}

{f'**Câu hỏi của user**: {user_question}' if user_question else ''}

Hãy viết **phê quẻ sâu** (~600-1200 chữ) theo cấu trúc:

1. **Quan vật khoảnh khắc** (~150 chữ) — khoảnh khắc gieo quẻ + tổ hợp 3 quẻ (chính/biến/hỗ) phản chiếu cái gì? Trích dẫn cụ thể từ Kinh Dịch nguyên văn ở trên.

2. **Thể-Dụng + Quái Khí** (~200 chữ) — diễn giải quan hệ Thể-Dụng theo paradigm đồng dạng, KHÔNG predict. Dẫn chứng từ citation.

3. **Hào động + biến chuyển** (~200 chữ) — hào động chỉ ra cảnh giới gì? Dẫn cụ thể "hào X quẻ Y" + insight từ Trình Di/Chu Hy nếu có trong citation.

4. **Tâm-pháp cho người hỏi** (~150 chữ) — KHÔNG kê hành động cụ thể. Chỉ ra **cảnh giới + phận tương ứng** + 1 câu thầy tổ.

5. **Cảnh báo** (~50 chữ) — nếu có ho_warning từ engine.

LƯU Ý CRITICAL:
- Trích dẫn rõ "Kinh Dịch · quẻ X · hào Y · Trình Di Truyện" nếu lấy từ citation
- KHÔNG bịa quẻ / hào không có trong citation
- KHÔNG dùng tone fortune-telling
- Viết tiếng Việt, **xưng "Anh"** với người hỏi, em là "em" / "bậc trí giả"
"""


def call_llm_luan_sau(prompt: str) -> dict:
    """Gọi LLM (chain DeepSeek → MiniMax → Ollama → Mock fallback).

    Returns:
        {"narrative": str, "provider": str, "model": str, "tokens_used": int}
    """
    from engine.ai.registry import get_registry

    registry = get_registry()
    last_error: Optional[Exception] = None
    # Provider chain: deepseek (paid quality) → minimax (fast cloud) → ollama (free local) → mock
    for provider_id in ("deepseek", "minimax", "ollama"):
        try:
            provider = registry.get(provider_id)
        except KeyError:
            continue
        # `is_configured` là @property, không phải method
        if not provider.is_configured:
            continue
        try:
            # DeepSeek V4 Pro mặc định reasoning ON → content có thể empty
            # khi model "think but doesn't write". Pass reasoning_effort=none
            # cho writing task — vẫn dùng v4-pro nhưng skip chain-of-thought.
            kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.65,
                "max_tokens": 2000,
            }
            if provider_id == "deepseek":
                kwargs["reasoning_effort"] = "none"
            response = provider.chat(**kwargs)
            # response là LLMResponse dataclass (content, provider, model,
            # prompt_tokens, completion_tokens, total_tokens, raw)
            return {
                "narrative": (response.content or "").strip(),
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.total_tokens,
            }
        except Exception as exc:
            last_error = exc
            registry.mark_unhealthy(provider_id, str(exc))
            continue
    raise RuntimeError(
        f"Tất cả provider thất bại. Last error: {last_error or 'no provider configured'}"
    )


# ============================================================================
# Hexagram Browser API helpers (2026-05-27 — feature: tra cứu trực tiếp 64 quẻ)
# ============================================================================

# Metadata cho 64 quẻ — derived từ _HEXAGRAM_TO_FILE + parse filename
# Format: {slug: {number, name_vi, name_zh, upper, lower, structure_unicode, file}}

_BAT_QUAI_UNICODE = {
    "Càn": "☰", "Khôn": "☷", "Khảm": "☵", "Ly": "☲",
    "Chấn": "☳", "Tốn": "☴", "Cấn": "☶", "Đoài": "☱",
}

_HEXAGRAM_META: list[dict] = [
    # (number, slug, name_vi, name_zh, upper, lower)
    (1, "kien", "Kiền", "乾", "Càn", "Càn"),
    (2, "khon", "Khôn", "坤", "Khôn", "Khôn"),
    (3, "truan", "Truân", "屯", "Khảm", "Chấn"),
    (4, "mong", "Mông", "蒙", "Cấn", "Khảm"),
    (5, "nhu", "Nhu", "需", "Khảm", "Càn"),
    (6, "tung", "Tụng", "訟", "Càn", "Khảm"),
    (7, "su", "Sư", "師", "Khôn", "Khảm"),
    (8, "ty", "Tỵ", "比", "Khảm", "Khôn"),
    (9, "tieu-suc", "Tiểu Súc", "小畜", "Tốn", "Càn"),
    (10, "ly", "Lý", "履", "Càn", "Đoài"),
    (11, "thai", "Thái", "泰", "Khôn", "Càn"),
    (12, "bi", "Bĩ", "否", "Càn", "Khôn"),
    (13, "dong-nhan", "Đồng Nhân", "同人", "Càn", "Ly"),
    (14, "dai-huu", "Đại Hữu", "大有", "Ly", "Càn"),
    (15, "khiem", "Khiêm", "謙", "Khôn", "Cấn"),
    (16, "du", "Dự", "豫", "Chấn", "Khôn"),
    (17, "tuy", "Tùy", "隨", "Đoài", "Chấn"),
    (18, "co", "Cổ", "蠱", "Cấn", "Tốn"),
    (19, "lam", "Lâm", "臨", "Khôn", "Đoài"),
    (20, "quan", "Quán", "觀", "Tốn", "Khôn"),
    (21, "phe-hap", "Phệ Hạp", "噬嗑", "Ly", "Chấn"),
    (22, "bi", "Bí", "賁", "Cấn", "Ly"),
    (23, "bac", "Bác", "剝", "Cấn", "Khôn"),
    (24, "phuc", "Phục", "復", "Khôn", "Chấn"),
    (25, "vo-vong", "Vô Vọng", "無妄", "Càn", "Chấn"),
    (26, "dai-suc", "Đại Súc", "大畜", "Cấn", "Càn"),
    (27, "di", "Di", "頤", "Cấn", "Chấn"),
    (28, "dai-qua", "Đại Quá", "大過", "Đoài", "Tốn"),
    (29, "kham", "Khảm (thuần)", "坎", "Khảm", "Khảm"),
    (30, "ly-hexagram", "Ly (thuần)", "離", "Ly", "Ly"),
    (31, "ham", "Hàm", "咸", "Đoài", "Cấn"),
    (32, "hang", "Hằng", "恆", "Chấn", "Tốn"),
    (33, "don", "Độn", "遯", "Càn", "Cấn"),
    (34, "dai-trang", "Đại Tráng", "大壯", "Chấn", "Càn"),
    (35, "tan", "Tấn", "晉", "Ly", "Khôn"),
    (36, "minh-di", "Minh Di", "明夷", "Khôn", "Ly"),
    (37, "gia-nhan", "Gia Nhân", "家人", "Tốn", "Ly"),
    (38, "khue", "Khuê", "睽", "Ly", "Đoài"),
    (39, "kien", "Kiển", "蹇", "Khảm", "Cấn"),
    (40, "giai", "Giải", "解", "Chấn", "Khảm"),
    (41, "ton", "Tổn", "損", "Cấn", "Đoài"),
    (42, "ich", "Ích", "益", "Tốn", "Chấn"),
    (43, "quai", "Quải", "夬", "Đoài", "Càn"),
    (44, "cau", "Cấu", "姤", "Càn", "Tốn"),
    (45, "tuy-hexagram", "Tụy", "萃", "Đoài", "Khôn"),
    (46, "thang", "Thăng", "升", "Khôn", "Tốn"),
    (47, "khon-hexagram", "Khốn", "困", "Đoài", "Khảm"),
    (48, "tinh", "Tỉnh", "井", "Khảm", "Tốn"),
    (49, "cach", "Cách", "革", "Đoài", "Ly"),
    (50, "dinh", "Đỉnh", "鼎", "Ly", "Tốn"),
    (51, "chan", "Chấn (thuần)", "震", "Chấn", "Chấn"),
    (52, "can-hexagram", "Cấn (thuần)", "艮", "Cấn", "Cấn"),
    (53, "tiem", "Tiệm", "漸", "Tốn", "Cấn"),
    (54, "qui-muoi", "Quy Muội", "歸妹", "Chấn", "Đoài"),
    (55, "phong", "Phong", "豐", "Chấn", "Ly"),
    (56, "lu", "Lữ", "旅", "Ly", "Cấn"),
    (57, "ton-hexagram", "Tốn (thuần)", "巽", "Tốn", "Tốn"),
    (58, "doai", "Đoài (thuần)", "兌", "Đoài", "Đoài"),
    (59, "hoan", "Hoán", "渙", "Tốn", "Khảm"),
    (60, "tiet", "Tiết", "節", "Khảm", "Đoài"),
    (61, "trung-phu", "Trung Phu", "中孚", "Tốn", "Đoài"),
    (62, "tieu-qua", "Tiểu Quá", "小過", "Chấn", "Cấn"),
    (63, "ky-te", "Ký Tế", "既濟", "Khảm", "Ly"),
    (64, "vi-te", "Vị Tế", "未濟", "Ly", "Khảm"),
]


def _parse_yaml_frontmatter(text: str) -> dict:
    """Trích lightweight metadata từ frontmatter — không cần PyYAML.

    Chỉ parse `description:` và `routing_keys: [...]` (đủ cho list view).
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = text[3:end]
    out: dict = {}
    # description: lấy dòng đầu của trường (có thể wrap)
    for line in fm.splitlines():
        s = line.strip()
        if s.startswith("description:"):
            out["description"] = s.split(":", 1)[1].strip()
        elif "routing_keys:" in s:
            # routing_keys: [a, b, c] — extract giữa []
            i = s.find("[")
            j = s.rfind("]")
            if i >= 0 and j > i:
                out["routing_keys"] = [k.strip() for k in s[i + 1:j].split(",") if k.strip()]
    return out


def _hexagram_slug_to_filename(slug: str, number: int) -> str:
    """Map (number, slug) → filename trong quẻ/. Format: NN-slug.md (zero-padded)."""
    return f"quẻ/{number:02d}-{slug}.md"


def list_hexagrams() -> list[dict]:
    """Liệt kê 64 quẻ với metadata cơ bản + description từ frontmatter.

    Returns:
        List 64 dict, mỗi dict có: number, slug, name_vi, name_zh, upper, lower,
        structure_unicode, file, description (parsed).
    """
    out: list[dict] = []
    for number, slug, name_vi, name_zh, upper, lower in _HEXAGRAM_META:
        filename = _hexagram_slug_to_filename(slug, number)
        # Parse description từ frontmatter
        f = _SKILLS_ROOT / filename
        description = ""
        if f.exists():
            try:
                text = f.read_text(encoding="utf-8")
                fm = _parse_yaml_frontmatter(text)
                description = fm.get("description", "")
            except Exception:
                pass
        out.append({
            "number": number,
            "slug": slug,
            "name_vi": name_vi,
            "name_zh": name_zh,
            "upper": upper,
            "lower": lower,
            "structure_unicode": _BAT_QUAI_UNICODE.get(upper, "") + _BAT_QUAI_UNICODE.get(lower, ""),
            "file": filename,
            "description": description,
            "has_deep": filename in _DEEP_QUE_FILES,
        })
    return out


def extract_loi_kinh_and_hao_brief(upper: str, lower: str, hao_num: int) -> dict:
    """Trích 'Lời Kinh' + dòng hào động + 1-2 insight cốt cho 1 quẻ.

    Output dùng cho UI LuuVanDashboard hiển thị tóm tắt mỗi vòng quẻ.

    Args:
        upper: bát quái thượng (vd "Cấn")
        lower: bát quái hạ (vd "Khôn")
        hao_num: hào động 1-6

    Returns:
        {
            "number": 23, "name_vi": "Bác", "name_zh": "剝",
            "loi_kinh": "Bác bất lợi hữu du vãng.",
            "loi_kinh_dich": "Bác không lợi có thừa đi.",
            "hao_brief": "**Lục Nhị**: Bác sàng dĩ biện, miệt trinh, hung — đẽo bằng bễ...",
            "insight_cot": "Bác xuất hiện do gốc dưới mỏng. Cứu Bác = dày cho gốc.",
            "tom_cot": "Bác = đẽo gọt rụng. 5 Âm gọt 1 Dương cuối...",
        }
    """
    file_rel = _HEXAGRAM_TO_FILE.get((upper, lower))
    if not file_rel:
        return {
            "number": 0, "name_vi": f"{upper}/{lower}", "name_zh": "?",
            "loi_kinh": "", "loi_kinh_dich": "",
            "hao_brief": "", "insight_cot": "",
            "tom_cot": "Quẻ chưa có trong corpus.",
        }
    # Find number from filename: "quẻ/23-bac.md" → 23
    import re as _re
    m = _re.match(r"quẻ/(\d+)-", file_rel)
    if not m:
        return {"number": 0, "name_vi": f"{upper}/{lower}", "name_zh": "?",
                "loi_kinh": "", "loi_kinh_dich": "", "hao_brief": "",
                "insight_cot": "", "tom_cot": ""}
    number = int(m.group(1))
    detail = get_hexagram(str(number))
    if not detail:
        return {"number": number, "name_vi": f"{upper}/{lower}", "name_zh": "?",
                "loi_kinh": "", "loi_kinh_dich": "", "hao_brief": "",
                "insight_cot": "", "tom_cot": ""}

    body = detail["body_markdown"]

    # 1) Tóm cốt = section "## Tóm cốt" (first paragraph)
    tom_cot = ""
    m1 = re.search(r"##\s+Tóm cốt\s*\n+(.+?)(?=\n##\s|\n>\s|\Z)", body, re.S)
    if m1:
        tom_cot = m1.group(1).strip()[:400]

    # 2) Lời Kinh = first blockquote with Hán + first italic line
    loi_kinh = ""
    loi_kinh_dich = ""
    m2 = re.search(r"##\s+Lời Kinh[^\n]*\n(.+?)(?=\n##\s|\Z)", body, re.S)
    if m2:
        section = m2.group(1)
        # Find Hán line (blockquote with CJK majority)
        for line in section.split("\n"):
            ls = line.strip()
            if ls.startswith("> ") and not ls.startswith("> _"):
                content = ls[2:].strip()
                cjk_count = sum(1 for ch in content if "一" <= ch <= "鿿")
                if cjk_count >= 2 and not loi_kinh:
                    loi_kinh = content
            elif ls.startswith("> _") and ls.endswith("_") and not loi_kinh_dich:
                loi_kinh_dich = ls[3:-1].strip()

    # 3) Hào động — tìm dòng table "6 hào" có tên hào tương ứng
    hao_brief = ""
    if hao_num in _HAO_NAMES_BY_NUM:
        hao_names = _HAO_NAMES_BY_NUM[hao_num]
        m3 = re.search(r"##\s+6\s+hào[^\n]*\n(.*?)(?=\n##\s|\Z)", body, re.S | re.IGNORECASE)
        if m3:
            section = m3.group(1)
            for line in section.split("\n"):
                ls = line.strip()
                if ls.startswith("|") and any(name in ls for name in hao_names):
                    # Found row — extract content (drop pipes)
                    cells = [c.strip().replace("**", "") for c in ls.strip("|").split("|")]
                    if len(cells) >= 2:
                        # cells[0] = hào name, cells[1+] = lời/tâm pháp
                        hao_brief = f"**{cells[0]}**: " + " — ".join(cells[1:])[:400]
                    break
        # Fallback: "## Insight {hào}" section
        if not hao_brief:
            for name in hao_names:
                m4 = re.search(rf"##\s+(?:Insight\s+)?{re.escape(name)}[^\n]*\n(.+?)(?=\n##\s|\Z)", body, re.S)
                if m4:
                    content = m4.group(1).strip()
                    # Take first 400 chars
                    hao_brief = f"**{name}**: {content[:400]}"
                    break

    # 4) Insight cốt — section bắt đầu "## Insight CỐT" hoặc "→ **Insight cốt"
    insight_cot = ""
    m5 = re.search(r"##\s+Insight\s+(?:CỐT|cốt)[^\n]*\n(.+?)(?=\n##\s|\Z)", body, re.S)
    if m5:
        insight_cot = m5.group(1).strip()[:400]
    else:
        # Fallback: tìm dòng "→ **Insight cốt**" trong body
        m5b = re.search(r"→\s+\*\*Insight\s+[Cc]ốt[^*]*\*\*[:\s]*(.+?)(?=\n\n|\n→|\Z)", body, re.S)
        if m5b:
            insight_cot = m5b.group(1).strip()[:400]

    return {
        "number": number,
        "name_vi": detail.get("name_vi", "?"),
        "name_zh": detail.get("name_zh", "?"),
        "loi_kinh": loi_kinh,
        "loi_kinh_dich": loi_kinh_dich,
        "hao_brief": hao_brief,
        "insight_cot": insight_cot,
        "tom_cot": tom_cot,
    }


def extract_hao_cards() -> list[dict]:
    """Extract 384 cards (64 quẻ × 6 hào) cho spaced repetition learning.

    Mỗi card = 1 hào với:
    - front: tên hào (Sơ Cửu / Lục Nhị / ...) + tên quẻ
    - back: nội dung hào (Lời + tâm pháp) parse từ table "## 6 hào"

    Returns:
        list of {card_id, hexagram_num, hexagram_name, hao_num, hao_name, front, back, lookup_key}
    """
    items = list_hexagrams()
    cards: list[dict] = []
    card_id = 0

    for h in items:
        detail = get_hexagram(str(h["number"]))
        if not detail:
            continue
        body = detail.get("body_markdown", "")
        # Find "## 6 hào" table (case-insensitive — vài file viết "6 Hào")
        m = re.search(r"##\s+6\s+hào[^\n]*\n(.*?)(?=\n##\s|\Z)", body, re.S | re.IGNORECASE)

        # Fallback: parse "## Hào XXX" sections individually (file cũ format Kiền/Khôn/Thái)
        if not m:
            hao_section_matches = list(re.finditer(
                r"##\s+(?:Hào\s+)?(Sơ Cửu|Sơ Lục|Cửu Nhị|Lục Nhị|Cửu Tam|Lục Tam|Cửu Tứ|Lục Tứ|Cửu Ngũ|Lục Ngũ|Thượng Cửu|Thượng Lục)[^\n]*\n(.*?)(?=\n##\s|\Z)",
                body, re.S
            ))
            if hao_section_matches:
                hao_order = ["Sơ Cửu", "Sơ Lục", "Cửu Nhị", "Lục Nhị", "Cửu Tam", "Lục Tam",
                             "Cửu Tứ", "Lục Tứ", "Cửu Ngũ", "Lục Ngũ", "Thượng Cửu", "Thượng Lục"]
                for sec_m in hao_section_matches:
                    hao_name_raw = sec_m.group(1).strip()
                    hao_content = sec_m.group(2).strip()
                    # Determine hao_num
                    name_to_num = {
                        "Sơ Cửu": 1, "Sơ Lục": 1, "Cửu Nhị": 2, "Lục Nhị": 2,
                        "Cửu Tam": 3, "Lục Tam": 3, "Cửu Tứ": 4, "Lục Tứ": 4,
                        "Cửu Ngũ": 5, "Lục Ngũ": 5, "Thượng Cửu": 6, "Thượng Lục": 6,
                    }
                    hao_num = name_to_num.get(hao_name_raw, 0)
                    if hao_num == 0:
                        continue
                    card_id += 1
                    cards.append({
                        "card_id": card_id,
                        "hexagram_num": h["number"],
                        "hexagram_name": h["name_vi"],
                        "hexagram_zh": h["name_zh"],
                        "hexagram_structure": h["structure_unicode"],
                        "hao_num": hao_num,
                        "hao_name": hao_name_raw,
                        "front": f"Quẻ {h['number']} {h['name_vi']} · {hao_name_raw}",
                        "back": hao_content[:1000],  # cap
                        "lookup_key": f"{h['number']}.{hao_num}",
                    })
            continue
        section = m.group(1)
        # Parse table rows. Format: | Hào | ... | ... |
        rows = []
        in_table = False
        for ln in section.split("\n"):
            ls = ln.strip()
            if ls.startswith("|"):
                if not in_table:
                    in_table = True
                    continue  # skip header
                if re.match(r"^\|\s*[-:]+", ls):
                    continue  # skip separator
                cells = [c.strip() for c in ls.strip("|").split("|")]
                rows.append(cells)
            elif in_table and ls == "":
                break

        # Map row → hào
        hao_order = ["Sơ", "Cửu Nhị", "Cửu Tam", "Cửu Tứ", "Cửu Ngũ", "Thượng"]
        hao_order_alt = ["Sơ", "Lục Nhị", "Lục Tam", "Lục Tứ", "Lục Ngũ", "Thượng"]
        for row in rows[:6]:  # cap 6
            if len(row) < 2:
                continue
            hao_name = row[0].replace("**", "").strip()
            # Determine hao number (1-6)
            hao_num = 0
            for i, name in enumerate(hao_order, 1):
                if name in hao_name:
                    hao_num = i
                    break
            if hao_num == 0:
                for i, name in enumerate(hao_order_alt, 1):
                    if name in hao_name:
                        hao_num = i
                        break
            if hao_num == 0:
                continue

            # Build front/back
            front = f"Quẻ {h['number']} {h['name_vi']} · {hao_name}"
            # Back: tất cả cells còn lại (Lời + tâm pháp)
            back_parts = []
            for cell in row[1:]:
                cell_clean = cell.replace("**", "").strip()
                if cell_clean:
                    back_parts.append(cell_clean)
            back = "\n\n".join(back_parts)

            card_id += 1
            cards.append({
                "card_id": card_id,
                "hexagram_num": h["number"],
                "hexagram_name": h["name_vi"],
                "hexagram_zh": h["name_zh"],
                "hexagram_structure": h["structure_unicode"],
                "hao_num": hao_num,
                "hao_name": hao_name,
                "front": front,
                "back": back,
                "lookup_key": f"{h['number']}.{hao_num}",  # vd "1.2" = Kiền Cửu Nhị
            })

    return cards


def build_hexagram_graph() -> dict:
    """Build cross-reference graph cho 64 quẻ.

    Edges:
    1. **Sequential** — 1→2, 2→3, ..., 63→64 (chu kỳ Kinh Dịch)
    2. **Đối ngẫu/Cặp** — quẻ đảo theo Tự quái:
       - Cặp Thái-Bĩ (11-12), Lâm-Quán (19-20), Bác-Phục (23-24), v.v.
    3. **Cùng quẻ thuần** — 8 quẻ thuần: Càn-Khôn, Khảm-Ly, Chấn-Cấn, Tốn-Đoài
    4. **Cross-ref từ frontmatter** — refs khai báo trong từng quẻ (vd Bác→Phục)

    Returns:
        {"nodes": [...], "edges": [...]}
        node = {id, number, name_vi, name_zh, upper, lower, group}
        edge = {source, target, type, label}
    """
    items = list_hexagrams()
    nodes = []
    edges = []

    # === Nodes ===
    # Group by thượng kinh (1-30) vs hạ kinh (31-64)
    for h in items:
        group = "thuong-kinh" if h["number"] <= 30 else "ha-kinh"
        # Special groups: thuần (Càn/Khôn/Khảm/Ly/Chấn/Cấn/Tốn/Đoài)
        if h["upper"] == h["lower"]:
            group = "thuan"
        nodes.append({
            "id": h["number"],
            "number": h["number"],
            "name_vi": h["name_vi"],
            "name_zh": h["name_zh"],
            "upper": h["upper"],
            "lower": h["lower"],
            "structure_unicode": h["structure_unicode"],
            "group": group,
        })

    # === Edges ===
    # 1. Sequential (64 → 1 cycle)
    for i in range(1, 65):
        nxt = (i % 64) + 1
        edges.append({"source": i, "target": nxt, "type": "sequential", "label": "tiếp"})

    # 2. Cặp Tự quái — quẻ chẵn-lẻ tiếp nhau là cặp đối ngẫu (1-2, 3-4, ..., 63-64)
    # Đa số là đối ngẫu nghĩa (Tống-Sư, Thái-Bĩ, Khiêm-Dự, ...)
    pair_labels = {
        (1, 2): "trời-đất",
        (3, 4): "khó-mở",
        (5, 6): "chờ-tranh",
        (7, 8): "đánh-gần",
        (9, 10): "chứa-bước",
        (11, 12): "thái-bĩ (giao-cách)",
        (13, 14): "đồng-hữu",
        (15, 16): "khiêm-dự",
        (17, 18): "tùy-cổ",
        (19, 20): "lâm-quán",
        (21, 22): "phệ-bí",
        (23, 24): "bác-phục",
        (25, 26): "vọng-súc",
        (27, 28): "di-đại quá",
        (29, 30): "khảm-ly (thuần)",
        (31, 32): "hàm-hằng (vợ chồng)",
        (33, 34): "độn-tráng",
        (35, 36): "tấn-minh di",
        (37, 38): "gia-khuê",
        (39, 40): "kiển-giải",
        (41, 42): "tổn-ích",
        (43, 44): "quải-cấu",
        (45, 46): "tụy-thăng",
        (47, 48): "khốn-tỉnh",
        (49, 50): "cách-đỉnh",
        (51, 52): "chấn-cấn",
        (53, 54): "tiệm-quy muội",
        (55, 56): "phong-lữ",
        (57, 58): "tốn-đoài",
        (59, 60): "hoán-tiết",
        (61, 62): "trung phu-tiểu quá",
        (63, 64): "ký tế-vị tế",
    }
    for (a, b), lbl in pair_labels.items():
        edges.append({"source": a, "target": b, "type": "pair", "label": lbl})

    # 3. Quẻ thuần — 8 quẻ thuần liên kết với nhau (1, 2, 29, 30, 51, 52, 57, 58)
    thuan_ids = [1, 2, 29, 30, 51, 52, 57, 58]
    for a in thuan_ids:
        for b in thuan_ids:
            if a < b:
                edges.append({"source": a, "target": b, "type": "thuan", "label": "thuần"})

    # 4. Cross-ref từ frontmatter (lazy — chỉ check kinh_dich refs)
    for h in items:
        detail = get_hexagram(str(h["number"]))
        if not detail:
            continue
        body = detail.get("body_markdown", "")
        # Tìm mentions của quẻ khác trong cross-ref section
        # Pattern: 'quẻ NN' or '(quẻ NN ...)' or '[NN-name]'
        crossref_section = ""
        m = re.search(r"##\s+Cross-ref[^\n]*\n(.*?)(?=\n##\s|\Z)", body, re.S)
        if m:
            crossref_section = m.group(1)
        ref_numbers = set()
        for m2 in re.finditer(r"\(quẻ\s+(\d+)\)|\[(\d+)-", crossref_section):
            n = m2.group(1) or m2.group(2)
            if n:
                ref_numbers.add(int(n))
        for ref in ref_numbers:
            if ref != h["number"] and 1 <= ref <= 64:
                # Check duplicate with sequential/pair edges
                edge_key = (min(h["number"], ref), max(h["number"], ref))
                already = any(
                    (e["source"], e["target"]) in [edge_key, (edge_key[1], edge_key[0])]
                    and e["type"] in ("sequential", "pair")
                    for e in edges
                )
                if not already:
                    edges.append({
                        "source": h["number"], "target": ref,
                        "type": "crossref", "label": "cross-ref",
                    })

    return {"nodes": nodes, "edges": edges}


def get_daily_hexagram(date_iso: str) -> dict:
    """1 quẻ/ngày — deterministic hash từ YYYY-MM-DD → 1 trong 64.

    Paradigm: KHÔNG random thật — cùng ngày = cùng quẻ (cho user check lại).

    Args:
        date_iso: 'YYYY-MM-DD'

    Returns:
        Full hexagram data (như get_hexagram) + extra:
        - daily_date: ngày input
        - daily_seed: hash debug
        - daily_excerpt: 1-2 paragraph cốt cho morning brief
    """
    # Hash đơn giản: sum (year*10000 + month*100 + day) → mod 64
    try:
        y, m, d = date_iso.split("-")
        seed = int(y) * 10000 + int(m) * 100 + int(d)
    except Exception:
        # Fallback
        import hashlib
        seed = int(hashlib.md5(date_iso.encode()).hexdigest()[:8], 16)
    # Deterministic shuffle so consecutive days don't follow 1→2→3 pattern.
    # Multiply by large prime (61) + offset → spread across 64.
    hex_num = ((seed * 61 + 7) % 64) + 1
    detail = get_hexagram(str(hex_num))
    if detail is None:
        # Should not happen — fallback to Kiền
        detail = get_hexagram("1")
    # Extract excerpt: first paragraph of "Tóm cốt" + "Insight CỐT" if found
    body = detail.get("body_markdown", "")
    excerpt = _extract_daily_excerpt(body)
    detail["daily_date"] = date_iso
    detail["daily_seed"] = seed
    detail["daily_excerpt"] = excerpt
    return detail


def _extract_daily_excerpt(body: str, max_chars: int = 800) -> str:
    """Trích 1-2 đoạn cốt từ body cho morning brief.

    Strategy:
    - Tìm section '## Tóm cốt' → giữ đoạn đầu
    - Tìm 1 blockquote đầu tiên (Lời Kinh nguyên văn)
    - Cap max_chars
    """
    lines = body.split("\n")
    out = []
    in_tom_cot = False
    found_first_quote = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("## Tóm cốt"):
            in_tom_cot = True
            continue
        if in_tom_cot:
            if s.startswith("##"):
                # Next section reached — stop
                in_tom_cot = False
                continue
            if s:
                out.append(ln)
            if len("\n".join(out)) > 400:
                in_tom_cot = False
        # First blockquote outside tom-cot (Lời Kinh)
        if not in_tom_cot and not found_first_quote and s.startswith("> ") and not s.startswith("> _"):
            found_first_quote = True
            out.append("")
            out.append(ln)
            # Also grab next 1-2 lines if they're continuation
        if found_first_quote and len("\n".join(out)) > 700:
            break

    text = "\n".join(out).strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    return text


def get_hexagram(slug_or_number: str) -> Optional[dict]:
    """Đọc 1 quẻ theo slug (vd: 'kien', 'thai') hoặc số (vd: '1', '63').

    Returns:
        {number, slug, name_vi, name_zh, upper, lower, structure_unicode,
         file, description, body_markdown, has_deep} hoặc None nếu không tìm thấy.
    """
    target_meta = None
    # Try parse số trước
    try:
        num = int(slug_or_number)
        for meta in _HEXAGRAM_META:
            if meta[0] == num:
                target_meta = meta
                break
    except ValueError:
        pass
    # Fallback: match by slug
    if target_meta is None:
        for meta in _HEXAGRAM_META:
            if meta[1] == slug_or_number:
                target_meta = meta
                break
    if target_meta is None:
        return None

    number, slug, name_vi, name_zh, upper, lower = target_meta
    filename = _hexagram_slug_to_filename(slug, number)
    f = _SKILLS_ROOT / filename
    if not f.exists():
        return None
    try:
        text = f.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = _parse_yaml_frontmatter(text)
    body = _strip_yaml_frontmatter(text)
    return {
        "number": number,
        "slug": slug,
        "name_vi": name_vi,
        "name_zh": name_zh,
        "upper": upper,
        "lower": lower,
        "structure_unicode": _BAT_QUAI_UNICODE.get(upper, "") + _BAT_QUAI_UNICODE.get(lower, ""),
        "file": filename,
        "description": fm.get("description", ""),
        "routing_keys": fm.get("routing_keys", []),
        "body_markdown": body,
        "has_deep": filename in _DEEP_QUE_FILES,
    }
