"""PoC Atomize v2 — TWO-PASS paradigm.

Anh chỉ ra 2026-06-09: v1 hardcode 6 câu mặc định = vi phạm paradigm bottom-up.
Mỗi chương loại nội dung khác nhau, câu hỏi mặc định cũng phải khác.

→ TWO-PASS:
  Pass 1 — Meta-Question Generation:
    Đọc chunk → phân loại archetype + format
    → LLM tự ĐỀ XUẤT knowledge_categories + question_templates_per_category
  Pass 2 — Atomic Instance Extraction:
    Cho mỗi template → extract atomic Q cụ thể có entity name + source quote

Test trên 10 chunks đa dạng: 5 Trung Châu Q2 + 5 chunks loại khác (an sao/thơ phú/
bảng lookup/chủ thể/kinh nghiệm tổ sư).

Run:
    python3 -m engine.atomization.poc_atomize_v2

Output:
    data/poc_atomize_v2_results.json
    data/poc_atomize_v2_review.md
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402
from engine.ai.providers.base import ProviderError  # noqa: E402


# ═══════════════════════════════════════════════════════════════
# PASS 1 — META-QUESTION GENERATION
# ═══════════════════════════════════════════════════════════════
PASS1_PROMPT = """# Nhiệm vụ Pass 1
Đọc đoạn văn dưới đây từ sách Tử Vi/Bát Tự/Kinh Dịch. Phân loại + ĐỀ XUẤT câu hỏi mặc định
PHÙ HỢP RIÊNG cho nội dung đoạn này.

# Bước 1 — Phân loại ARCHETYPE (boolean, overlap được)

- `is_chu_the`     (chủ thể): định nghĩa sao/cung/khái niệm gốc
- `is_cong_thuc`   (công thức): cách tính, quy tắc cố định (an sao, tra cứu)
- `is_luan_giai`   (luận giải): giải nghĩa cách cục cụ thể
- `is_to_hop`      (tổ hợp): combo sao/cung phái sinh cách mới
- `is_kinh_nghiem` (kinh nghiệm): wisdom áp dụng khi luận giải

# Bước 2 — Phân loại FORMAT STYLE

- `ket_qua`    — đưa ra kết quả phán định cứng ("đại phú", "phá tán")
- `nguyen_ly`  — chỉ ra nguyên lý + cơ chế hoạt động
- `tho_phu`    — văn vần Hán cổ / phú bình giải
- `bang_lookup` — bảng / lookup table

# Bước 3 — KNOWLEDGE CATEGORIES IN THIS CHUNK

Đoạn này nói về những MẢNG KIẾN THỨC nào? Liệt kê 2-6 categories CỤ THỂ
cho đoạn này (KHÔNG generic, phải nêu rõ chủ thể).

Ví dụ tốt:
- "định nghĩa tính cách sao Tham Lang"
- "Tham Lang đào hoa kết hợp với Riêu Mộc Cái Đào Hồng"
- "cách cục Hùng Tú Kiển Nguyên Liêm-Thất Sửu/Mùi"
- "phú thơ Vũ Khúc Nhập Hạn 8 câu Hán-Việt"

Ví dụ XẤU (quá generic):
- "luận giải sao" ❌
- "ý nghĩa cung" ❌

# Bước 4 — QUESTION TEMPLATES PER CATEGORY

Cho mỗi category ở Bước 3, ĐỀ XUẤT 3-7 LOẠI CÂU HỎI mặc định phù hợp.
Tự nghĩ theo nội dung đoạn — KHÔNG dùng template universal.

Ví dụ:
- Category "định nghĩa tính cách sao Tham Lang":
  - "Sao Tham Lang biểu trưng cá tính gì?"
  - "Tham Lang có nóng nảy không?"
  - "Tham Lang vs các sao đào hoa khác khác nhau thế nào?"
- Category "phú thơ Vũ Khúc Nhập Hạn 8 câu":
  - "Câu 1 'Thả dã nhuận thân...' nghĩa Việt là gì?"
  - "Câu phú này áp dụng khi nào?"
  - "Sao xuất hiện trong câu là gì?"

# Output JSON (KHÔNG markdown fence)
{
  "archetype": {"is_chu_the": 0|1, "is_cong_thuc": 0|1, "is_luan_giai": 0|1, "is_to_hop": 0|1, "is_kinh_nghiem": 0|1},
  "format_style": "ket_qua" | "nguyen_ly" | "tho_phu" | "bang_lookup",
  "subjects_mentioned": ["..."],
  "knowledge_categories": ["category 1", "category 2", ...],
  "question_templates_per_category": {
    "category 1": ["template Q1", "template Q2", ...],
    "category 2": [...]
  }
}

# Đoạn văn
{content}

# Output Pass 1:
"""


# ═══════════════════════════════════════════════════════════════
# PASS 2 — ATOMIC INSTANCE EXTRACTION
# ═══════════════════════════════════════════════════════════════
PASS2_PROMPT = """# Nhiệm vụ Pass 2
Cho mỗi câu hỏi TEMPLATE ở Pass 1, extract atomic question CỤ THỂ (instance)
có thể answer được bằng đoạn văn dưới.

QUY TẮC BẮT BUỘC:
1. Atomic Q phải nêu RÕ tên sao, cung, chi cụ thể. TUYỆT ĐỐI tránh đại từ.
   ✅ "Sao Tham Lang biểu trưng cá tính nóng nảy lười biếng không?"
   ❌ "Sao này có tính cách gì?"

2. Mỗi atomic Q PHẢI:
   - Trả lời được TRỰC TIẾP bằng nội dung đoạn (không cần kiến thức ngoài)
   - Có source_quote = đoạn trích nguyên văn chứa câu trả lời
   - Có subject_identifiers = JSON freeform (sao, cung, chi, hoá, ...)

3. KHÔNG bịa, không suy đoán. Bám đoạn 100%.

4. Tránh trùng lặp. Đa dạng phrasing.

# Output JSON (KHÔNG markdown fence)
{
  "atomic_questions": [
    {
      "from_template": "<template từ Pass 1>",
      "from_category": "<category từ Pass 1>",
      "question": "<atomic Q cụ thể, rõ entity>",
      "subject_identifiers": { /* freeform JSON */ },
      "source_quote": "<đoạn trích chứa câu trả lời>"
    },
    ...
  ]
}

# Pass 1 output (templates đề xuất)
{pass1_output}

# Đoạn văn
{content}

# Output Pass 2:
"""


# ═══════════════════════════════════════════════════════════════
# 10 CHUNKS đa dạng (5 Trung Châu Q2 + 5 sách khác)
# ═══════════════════════════════════════════════════════════════
SELECTED_CHUNKS = [
    # Đợt 1 — Trung Châu Q2 (luận giải nguyên lý)
    {"book": "trung-chau-tu-vi-dau-so-2", "page": 347, "expected": "luận giải case Vũ-Phá Tỵ"},
    {"book": "trung-chau-tu-vi-dau-so-2", "page": 412, "expected": "chủ thể Liêm Trinh"},
    {"book": "trung-chau-tu-vi-dau-so-2", "page": 501, "expected": "12 cung định nghĩa"},
    {"book": "trung-chau-tu-vi-dau-so-2", "page": 502, "expected": "Cô Quân Vô Đạo case"},
    {"book": "trung-chau-tu-vi-dau-so-2", "page": 575, "expected": "Thiên Cơ Tỵ/Hợi"},

    # Đợt 2 — 5 sách khác (loại khác)
    {"book": "tu-vi-dau-so-toan-thu-vu-tai-luc", "page": 50, "expected": "BẢNG cặp sao hợp chiếu"},
    {"book": "tu-vi-dau-so-toan-thu-vu-tai-luc", "page": 100, "expected": "THƠ PHÚ Vũ Khúc Nhập Hạn"},
    {"book": "tu-vi-dau-so-toan-thu-vu-tai-luc", "page": 150, "expected": "THƠ PHÚ kết quả cứng"},
    {"book": "tu-vi-ham-so", "page": 100, "expected": "CHỦ THỂ Tham Lang tính cách"},
    {"book": "tu-vi-nghiem-ly-toan-thu-thien-luong", "page": 150, "expected": "KINH NGHIỆM Thiên Lương Kim Cục"},
]

OUTPUT_JSON = PROJECT_ROOT / "data" / "poc_atomize_v2_results.json"
OUTPUT_MD = PROJECT_ROOT / "data" / "poc_atomize_v2_review.md"


@dataclass
class ChunkResultV2:
    book: str
    page: int
    expected: str
    chunk_text: str
    chunk_chars: int
    pass1_output: dict | None
    pass2_output: dict | None
    pass1_raw: str
    pass2_raw: str
    pass1_tokens: dict
    pass2_tokens: dict
    pass1_duration: float
    pass2_duration: float
    pass1_error: str | None = None
    pass2_error: str | None = None


def load_chunk(book: str, page: int) -> str:
    path = PROJECT_ROOT / "data" / "restored_books" / book / "pages" / f"p{page:04d}.md"
    return path.read_text(encoding="utf-8").strip()


def parse_json(content: str) -> tuple[dict | None, str | None]:
    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {e}"


def main() -> None:
    keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
    provider = MiniMaxProvider(api_key=keys["minimax"])
    model = "MiniMax-M2"

    print(f"🔧 Provider: {provider.name} · Model: {model}")
    print(f"📚 10 chunks đa dạng (5 Trung Châu Q2 + 5 sách khác)")
    print(f"🔀 TWO-PASS: meta-Q gen → atomic extract\n")

    results: list[ChunkResultV2] = []

    for idx, spec in enumerate(SELECTED_CHUNKS, 1):
        book, page = spec["book"], spec["page"]
        try:
            chunk = load_chunk(book, page)
        except FileNotFoundError:
            print(f"  [{idx}/10] {book}/p{page:04d}: ❌ FILE NOT FOUND")
            continue
        chars = len(chunk)
        print(f"  [{idx}/10] {book[:35]:<35}/p{page:04d}: {chars} chars · {spec['expected']}")

        # ── PASS 1 ───────────────────────────────────────────────
        pass1_msgs = [{"role": "user", "content": PASS1_PROMPT.replace("{content}", chunk)}]
        t1 = time.time()
        try:
            r1 = provider.chat(messages=pass1_msgs, model=model, temperature=0.7, max_tokens=4000)
        except ProviderError as e:
            print(f"     ❌ Pass1 fail: {e}")
            continue
        d1 = time.time() - t1
        p1_parsed, p1_err = parse_json(r1.content)
        n_cats = len(p1_parsed.get("knowledge_categories", [])) if p1_parsed else 0
        n_tmpls = sum(len(v) for v in (p1_parsed or {}).get("question_templates_per_category", {}).values())
        arch = "+".join(k.replace("is_", "") for k, v in (p1_parsed or {}).get("archetype", {}).items() if v) or "?"
        fmt = (p1_parsed or {}).get("format_style", "?")
        print(f"     Pass 1 ✅ {d1:.1f}s · {r1.prompt_tokens}+{r1.completion_tokens} tok · "
              f"{n_cats} cats · {n_tmpls} templates · [{arch}/{fmt}]")
        if p1_err:
            print(f"     Pass 1 ⚠ parse: {p1_err}")
            results.append(ChunkResultV2(
                book=book, page=page, expected=spec['expected'],
                chunk_text=chunk, chunk_chars=chars,
                pass1_output=None, pass2_output=None,
                pass1_raw=r1.content, pass2_raw="",
                pass1_tokens={"prompt": r1.prompt_tokens, "completion": r1.completion_tokens},
                pass2_tokens={"prompt": 0, "completion": 0},
                pass1_duration=d1, pass2_duration=0,
                pass1_error=p1_err,
            ))
            continue

        # ── PASS 2 ───────────────────────────────────────────────
        pass2_text = PASS2_PROMPT.replace(
            "{pass1_output}", json.dumps(p1_parsed, ensure_ascii=False, indent=2)
        ).replace("{content}", chunk)
        pass2_msgs = [{"role": "user", "content": pass2_text}]
        t2 = time.time()
        try:
            r2 = provider.chat(messages=pass2_msgs, model=model, temperature=0.7, max_tokens=8000)
        except ProviderError as e:
            print(f"     ❌ Pass2 fail: {e}")
            continue
        d2 = time.time() - t2
        p2_parsed, p2_err = parse_json(r2.content)
        n_atoms = len((p2_parsed or {}).get("atomic_questions", []))
        print(f"     Pass 2 ✅ {d2:.1f}s · {r2.prompt_tokens}+{r2.completion_tokens} tok · {n_atoms} atoms"
              + (f" · ⚠ {p2_err}" if p2_err else ""))

        results.append(ChunkResultV2(
            book=book, page=page, expected=spec['expected'],
            chunk_text=chunk, chunk_chars=chars,
            pass1_output=p1_parsed, pass2_output=p2_parsed,
            pass1_raw=r1.content, pass2_raw=r2.content,
            pass1_tokens={"prompt": r1.prompt_tokens, "completion": r1.completion_tokens},
            pass2_tokens={"prompt": r2.prompt_tokens, "completion": r2.completion_tokens},
            pass1_duration=d1, pass2_duration=d2,
            pass1_error=None, pass2_error=p2_err,
        ))

    # Save raw
    OUTPUT_JSON.write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Summary
    print("\n" + "═" * 70)
    total_atoms = sum(len((r.pass2_output or {}).get("atomic_questions", [])) for r in results)
    total_tok = sum(r.pass1_tokens["prompt"] + r.pass1_tokens["completion"]
                    + r.pass2_tokens["prompt"] + r.pass2_tokens["completion"] for r in results)
    print(f"✅ Saved {len(results)} chunks → {OUTPUT_JSON}")
    print(f"📌 Total atomic questions: {total_atoms}")
    print(f"📊 Total tokens: {total_tok}")

    # Per-archetype atom counts
    print(f"\n🔍 ARCHETYPE × FORMAT DISTRIBUTION:")
    for r in results:
        if not r.pass1_output:
            continue
        arch = "+".join(k.replace("is_", "") for k, v in r.pass1_output.get("archetype", {}).items() if v)
        fmt = r.pass1_output.get("format_style", "?")
        n_atoms = len((r.pass2_output or {}).get("atomic_questions", []))
        n_cats = len(r.pass1_output.get("knowledge_categories", []))
        print(f"  {r.book[:30]:<30} p{r.page:04d}  {arch:<35} / {fmt:<12}  {n_cats} cats → {n_atoms} atoms")


if __name__ == "__main__":
    main()
