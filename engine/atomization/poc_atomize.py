"""PoC Atomize — Trung Châu Q2 — paradigm bottom-up.

Anh chốt 2026-06-09: KHÔNG khóa cứng schema trước khi đọc. Mỗi đoạn cần phân loại
5 archetype (chủ thể / công thức / luận giải / tổ hợp / kinh nghiệm) + 3 format
(kết quả / nguyên lý / thơ phú). Schema EMERGE từ data thực sau khi atomize.

Run:
    python3 -m engine.atomization.poc_atomize

Output:
    data/poc_atomize_results.json
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


# ── PROMPT — Atomic Tagging port tiếng Việt Tử Vi (paradigm bottom-up) ──
ATOMIZE_PROMPT = """# Nhiệm vụ
Đọc đoạn văn dưới đây trích từ sách Tử Vi Đẩu Số (Trung Châu phái — Vương Đình Chỉ).
Phân tích đoạn này theo paradigm BOTTOM-UP — KHÔNG khóa cứng trước.

# Bước 1 — Phân loại ARCHETYPE (đoạn này thuộc loại gì, có thể overlap)

- `is_chu_the` (chủ thể): định nghĩa sao/cung/khái niệm gốc (vd. "Tử Vi là Đế tinh")
- `is_cong_thuc` (công thức): cách tính, quy tắc cố định (vd. an Tử Vi theo cục số)
- `is_luan_giai` (luận giải): giải nghĩa cách cục cụ thể (vd. "Tử-Phá Mệnh thì...")
- `is_to_hop` (tổ hợp): combo sao/cung phái sinh cách mới (vd. Liêm-Thất Sửu/Mùi)
- `is_kinh_nghiem` (kinh nghiệm): wisdom áp dụng khi luận giải

# Bước 2 — Phân loại FORMAT STYLE

- `ket_qua` — đưa ra kết quả phán định cứng ("đại phú", "phá tán")
- `nguyen_ly` — chỉ ra nguyên lý + cơ chế hoạt động
- `tho_phu` — văn vần Hán cổ / phú bình giải

# Bước 3 — Extract identifiers (FREEFORM, KHÔNG khóa schema)

Tự nhận diện trong đoạn này có gì: sao chính, cung, chi, combo, hoá khí,
năm sinh can/chi, giới tính, đại vận, lưu niên, school, ...
Liệt kê chỉ NHỮNG GÌ THỰC SỰ XUẤT HIỆN trong đoạn — không bịa thêm.

# Bước 4 — Sinh ATOMIC QUESTIONS

Liệt kê tất cả câu hỏi mà đoạn này TRẢ LỜI ĐƯỢC.

QUY TẮC BẮT BUỘC:
1. Mỗi câu hỏi nêu RÕ tên sao, cung, chi cụ thể. TUYỆT ĐỐI tránh đại từ
   ("nó", "mệnh tạo", "người này", "vị này").
2. Đa dạng góc hỏi:
   - Tính chất GỐC của sao X?
   - Tính chất GỐC của cung Y?
   - Nguyên lý VẬN HÀNH của combo Z?
   - Bản chất LÕI của (X+Y+Z)?
   - Điều kiện hình thành cách cục W?
   - Hệ quả khi gặp tứ sát/lục cát?
3. KHÔNG suy đoán ngoài nội dung đoạn. Bám sách 100%.

# Output JSON
{
  "archetype": {
    "is_chu_the": 0 or 1,
    "is_cong_thuc": 0 or 1,
    "is_luan_giai": 0 or 1,
    "is_to_hop": 0 or 1,
    "is_kinh_nghiem": 0 or 1
  },
  "format_style": "ket_qua" | "nguyen_ly" | "tho_phu",
  "subjects": ["Tử Vi", "Phá Quân", ...],
  "formulas": ["..."],
  "meanings": ["..."],
  "combos": ["..."],
  "experiences": ["..."],
  "poem_text": null or "...",
  "atomic_questions": [
    {
      "question": "...?",
      "subject_identifiers": { /* freeform JSON, chỉ điền field xuất hiện */ },
      "source_quote": "..."
    },
    ...
  ]
}

# Đoạn văn cần phân tích
{content}

# Output JSON của em (KHÔNG markdown fence, JSON thuần):
"""


# ── 10 trang Trung Châu Q2 đa dạng archetype + format ──
SELECTED_PAGES = [
    101,  # Phá Quân + sát kị (luận giải, kết quả)
    175,  # Phân tích cung (chủ thể + tổ hợp)
    250,  # Bảng 4 cung (công thức + bảng)
    347,  # Vũ-Phá Tỵ case study (luận giải + kinh nghiệm)
    358,  # Mệnh đồng độ Lưu Niên (kinh nghiệm)
    412,  # Liêm Trinh mẫn cảm/thiết thực (chủ thể + tổ hợp)
    461,  # Tử-Sát + xu cát tị hung (nguyên lý + kinh nghiệm)
    501,  # 12 cung định nghĩa (chủ thể + công thức)
    502,  # Cô Quân Vô Đạo (luận giải + kinh nghiệm)
    575,  # Thiên Cơ Tỵ/Hợi (luận giải)
]

BOOK_DIR = PROJECT_ROOT / "data" / "restored_books" / "trung-chau-tu-vi-dau-so-2"
OUTPUT_FILE = PROJECT_ROOT / "data" / "poc_atomize_results.json"


@dataclass
class ChunkResult:
    page: int
    chunk_text: str
    chunk_chars: int
    llm_provider: str
    llm_model: str
    parsed: dict
    raw_response: str
    prompt_tokens: int
    completion_tokens: int
    duration_sec: float
    parse_error: str | None = None


def load_chunk(page: int) -> str:
    """Load page markdown content."""
    page_str = f"p{page:04d}.md"
    path = BOOK_DIR / "pages" / page_str
    return path.read_text(encoding="utf-8").strip()


def build_messages(chunk_text: str) -> list[dict]:
    prompt = ATOMIZE_PROMPT.replace("{content}", chunk_text)
    return [{"role": "user", "content": prompt}]


def parse_json_response(content: str) -> tuple[dict | None, str | None]:
    """Try parse LLM JSON output, return (parsed_dict, error_msg)."""
    raw = content.strip()
    # Strip markdown fence if any
    if raw.startswith("```"):
        lines = raw.split("\n")
        # remove first line (```json or ```)
        lines = lines[1:]
        # remove last ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {e}"


def main() -> None:
    # Load API key
    keys_path = PROJECT_ROOT / "data" / "ai_keys.json"
    keys = json.loads(keys_path.read_text())
    api_key = keys.get("minimax")
    if not api_key:
        print("ERROR: MiniMax API key missing in data/ai_keys.json")
        sys.exit(1)

    provider = MiniMaxProvider(api_key=api_key)
    model = "MiniMax-M2"  # Paid plan Anh đã chi — fast cloud reasoning
    temperature = 0.7  # PIKE-RAG paper §A.3 — atomizing diversity

    print(f"🔧 Provider: {provider.name} · Model: {model} · T={temperature}")
    print(f"📚 Book: Trung Châu Q2 · {len(SELECTED_PAGES)} pages\n")

    results: list[ChunkResult] = []
    total_tokens = {"prompt": 0, "completion": 0}

    for idx, page in enumerate(SELECTED_PAGES, 1):
        try:
            chunk = load_chunk(page)
        except FileNotFoundError:
            print(f"  [{idx}/{len(SELECTED_PAGES)}] p{page:04d}: ❌ FILE NOT FOUND")
            continue

        chars = len(chunk)
        print(f"  [{idx}/{len(SELECTED_PAGES)}] p{page:04d}: {chars} chars → atomize...", end="", flush=True)

        messages = build_messages(chunk)
        t_start = time.time()
        try:
            response = provider.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=8000,  # bump để JSON không bị cắt (4 chunks failed run đầu)
            )
        except ProviderError as e:
            print(f" ❌ {e}")
            continue
        duration = time.time() - t_start

        parsed, parse_err = parse_json_response(response.content)
        n_atoms = len(parsed.get("atomic_questions", [])) if parsed else 0
        archetypes = (
            [k.replace("is_", "") for k, v in parsed.get("archetype", {}).items() if v]
            if parsed
            else []
        )
        archetypes_str = "+".join(archetypes) if archetypes else "?"
        fmt = parsed.get("format_style", "?") if parsed else "?"
        status = "✅" if parsed else f"⚠ {parse_err}"
        print(
            f" {status} {duration:.1f}s · "
            f"{response.prompt_tokens}+{response.completion_tokens} tok · "
            f"{n_atoms} atoms · [{archetypes_str}/{fmt}]"
        )

        results.append(
            ChunkResult(
                page=page,
                chunk_text=chunk,
                chunk_chars=chars,
                llm_provider=provider.name,
                llm_model=model,
                parsed=parsed or {},
                raw_response=response.content,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                duration_sec=duration,
                parse_error=parse_err,
            )
        )
        total_tokens["prompt"] += response.prompt_tokens
        total_tokens["completion"] += response.completion_tokens

    # Save full results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "═" * 60)
    print(f"✅ Saved {len(results)} chunks → {OUTPUT_FILE}")
    print(f"📊 Total tokens: {total_tokens['prompt']}+{total_tokens['completion']} = "
          f"{sum(total_tokens.values())}")
    print(f"💰 Cost: MiniMax paid plan (Anh đã chi Token Plan, không hóa đơn phát sinh)")
    print(f"⏱  Total duration: {sum(r.duration_sec for r in results):.1f}s\n")

    # Summary atomic Q counts + archetype distribution
    total_atoms = sum(len(r.parsed.get("atomic_questions", [])) for r in results)
    print(f"📌 Total atomic questions: {total_atoms}")
    archetype_counts = {}
    format_counts = {}
    for r in results:
        for k, v in r.parsed.get("archetype", {}).items():
            if v:
                archetype_counts[k] = archetype_counts.get(k, 0) + 1
        fmt = r.parsed.get("format_style")
        if fmt:
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
    print(f"📌 Archetype distribution: {archetype_counts}")
    print(f"📌 Format distribution: {format_counts}")

    # Field discovery (Phase B emergence preview)
    field_counts = {}
    for r in results:
        for atom in r.parsed.get("atomic_questions", []):
            ids = atom.get("subject_identifiers", {})
            for k in ids.keys():
                field_counts[k] = field_counts.get(k, 0) + 1
    print(f"\n🔍 Subject identifier fields discovered (top 15):")
    for k, v in sorted(field_counts.items(), key=lambda x: -x[1])[:15]:
        coverage = v / max(total_atoms, 1) * 100
        marker = "🌟" if coverage > 80 else ("🟢" if coverage > 50 else "🟡")
        print(f"   {marker} {k}: {v}/{total_atoms} ({coverage:.0f}%)")


if __name__ == "__main__":
    main()
