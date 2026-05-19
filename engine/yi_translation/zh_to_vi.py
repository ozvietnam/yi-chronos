"""zh_to_vi — Dịch chữ Hán hiện đại → Việt cổ điển cho corpus Mai Hoa Dịch Số.

CHIẾN LƯỢC (theo spike test 2026-05-17):
  Primary:  DeepSeek-chat   — 2.5s/đoạn, $0.003/page, văn phong cổ điển ⭐⭐⭐⭐⭐
  Fallback: qwen2.5-coder:14b Ollama local — 12s/đoạn, FREE ⭐⭐⭐⭐

PROMPT pattern: context-aware với glossary cố định cho thuật ngữ Mai Hoa.

USE:
    from engine.yi_translation import translate_page, translate_corpus

    # 1 trang
    vi_text = translate_page(zh_text)

    # full corpus
    translate_corpus(
        corpus_path="/Users/ozvietnamdesktop/Desktop/yi/data/yi_restored/thieu-khang-tiet-tq",
        max_pages=None,
        skip_existing=True,
    )
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path

# === GLOSSARY — Mai Hoa Dịch Số thuật ngữ Hán→Việt cố định ===
# Mỗi entry: chinese → vietnamese_han_viet
TRANSLATION_GLOSSARY: dict[str, str] = {
    # Core Mai Hoa
    "梅花易数": "Mai Hoa Dịch Số",
    "邵康节": "Thiệu Khang Tiết",
    "邵雍": "Thiệu Ung",
    "易经": "Kinh Dịch",
    "周易": "Chu Dịch",
    "象数": "Tượng số",
    "象数学": "Tượng số học",
    # 8 quẻ
    "乾": "Càn",
    "坤": "Khôn",
    "震": "Chấn",
    "巽": "Tốn",
    "坎": "Khảm",
    "离": "Ly",
    "艮": "Cấn",
    "兑": "Đoài",
    "八卦": "Bát Quái",
    "先天八卦": "Tiên Thiên Bát Quái",
    "后天八卦": "Hậu Thiên Bát Quái",
    # Nạp Giáp & lục thần
    "纳甲": "Nạp Giáp",
    "纳甲法": "phép Nạp Giáp",
    "勾陈": "Câu Trần",
    "腾蛇": "Đằng Xà",
    "玄龟": "Huyền Quy",
    "玄武": "Huyền Vũ",
    "青龙": "Thanh Long",
    "白虎": "Bạch Hổ",
    "朱雀": "Chu Tước",
    "四象": "Tứ Tượng",
    "六神": "Lục Thần",
    # Persons / dynasties / classical refs
    "虞翻": "Ngu Phiên",
    "京房": "Kinh Phòng",
    "汤行易": "Thang Hành Dịch",
    "孔子": "Khổng Tử",
    "老子": "Lão Tử",
    "朱熹": "Chu Hi",
    "周文王": "Chu Văn Vương",
    "伏羲": "Phục Hy",
    "大禹": "Đại Vũ",
    # Daoism / cosmology
    "道教": "Đạo giáo",
    "真武大帝": "Chân Vũ Đại Đế",
    "玉皇大帝": "Ngọc Hoàng Đại Đế",
    "紫微垣": "Tử Vi Viên",
    "紫微斗数": "Tử Vi Đẩu Số",
    "天干": "Thiên Can",
    "地支": "Địa Chi",
    "阴阳": "Âm Dương",
    "五行": "Ngũ Hành",
    "河图": "Hà Đồ",
    "洛书": "Lạc Thư",
    # Computation
    "卦": "quẻ",
    "起卦": "khởi quẻ",
    "成卦": "thành quẻ",
    "占": "chiêm",
    "占卜": "chiêm bốc",
    "爻": "hào",
    "动爻": "động hào",
    "变爻": "biến hào",
    "本卦": "bản quẻ",
    "互卦": "hỗ quẻ",
    "变卦": "biến quẻ",
    "体卦": "thể quẻ",
    "用卦": "dụng quẻ",
    "体用": "Thể-Dụng",
    "克应": "Khắc Ứng",
    # 12 chi
    "子": "Tý",
    "丑": "Sửu",
    "寅": "Dần",
    "卯": "Mão",
    "辰": "Thìn",
    "巳": "Tị",
    "午": "Ngọ",
    "未": "Mùi",
    "申": "Thân",
    "酉": "Dậu",
    "戌": "Tuất",
    "亥": "Hợi",
}


def _glossary_prompt_section() -> str:
    """Render glossary thành text cho prompt — chỉ chọn 25-30 entries phổ biến nhất.

    Quá nhiều entries làm dilute prompt, em chọn subset core.
    """
    core = [
        "纳甲→Nạp Giáp", "勾陈→Câu Trần", "腾蛇→Đằng Xà", "玄龟→Huyền Quy",
        "玄武→Huyền Vũ", "青龙→Thanh Long", "白虎→Bạch Hổ", "朱雀→Chu Tước",
        "紫微垣→Tử Vi Viên", "紫微斗数→Tử Vi Đẩu Số",
        "虞翻→Ngu Phiên", "京房→Kinh Phòng", "邵康节→Thiệu Khang Tiết",
        "真武大帝→Chân Vũ Đại Đế", "玉皇大帝→Ngọc Hoàng Đại Đế",
        "道教→Đạo giáo", "四象→Tứ Tượng", "六神→Lục Thần",
        "卦→quẻ", "起卦→khởi quẻ", "成卦→thành quẻ", "动爻→động hào",
        "天干→Thiên Can", "地支→Địa Chi", "五行→Ngũ Hành", "阴阳→Âm Dương",
        "河图→Hà Đồ", "洛书→Lạc Thư",
        "乾→Càn", "坤→Khôn", "震→Chấn", "巽→Tốn",
        "坎→Khảm", "离→Ly", "艮→Cấn", "兑→Đoài",
        "先天八卦→Tiên Thiên Bát Quái", "后天八卦→Hậu Thiên Bát Quái",
    ]
    return ", ".join(core)


PROMPT_TEMPLATE = """Bạn là dịch giả chuyên ngành Mai Hoa Dịch Số. Nhiệm vụ: DỊCH NGHĨA tiếng Trung hiện đại sang tiếng Việt hiện đại, tự nhiên, dễ hiểu cho người Việt không biết chữ Hán.

⛔ KHÔNG ĐƯỢC PHIÊN ÂM HÁN-VIỆT TỪNG CHỮ. Đây là LỖI LỚN NHẤT cần tránh.

✅ NGUYÊN TẮC PHÂN BIỆT:
A) Văn thường (mô tả, dẫn nhập, văn xuôi hiện đại): **DỊCH NGHĨA SANG TIẾNG VIỆT HIỆN ĐẠI**
B) Thuật ngữ chuyên ngành Mai Hoa: GIỮ phiên âm Hán-Việt theo glossary
C) Tên người, địa danh cổ: phiên âm Hán-Việt

📖 GLOSSARY THUẬT NGỮ (chỉ những từ này mới giữ Hán-Việt):
{glossary}

📌 VÍ DỤ MẪU — học theo:

VÍ DỤ 1 (văn dẫn nhập — DỊCH NGHĨA):
  GỐC: 关于本书
  ĐÚNG: Về cuốn sách này
  SAI:  Quan ư thử thư  ← lỗi phiên âm

VÍ DỤ 2 (văn mô tả — DỊCH NGHĨA):
  GỐC: 北宋大儒邵康节穷究宇宙万物之数理关系，化繁复为简明
  ĐÚNG: Đại nho Thiệu Khang Tiết thời Bắc Tống nghiên cứu cùng tận quan hệ số lý giữa vạn vật trong vũ trụ, giản lược cái phức tạp thành rõ ràng
  SAI:  Bắc Tống đại nho Thiệu Khang Tiết cùng cứu vũ trụ vạn vật chi số lý quan hệ, hóa phồn phục vi giản minh  ← lỗi phiên âm

VÍ DỤ 3 (đoạn chuyên ngành — GIỮ thuật ngữ):
  GỐC: 纳甲法中引入了勾陈和腾蛇二神
  ĐÚNG: Trong phép Nạp Giáp có dẫn nhập hai vị thần Câu Trần và Đằng Xà
  GIẢI THÍCH: "Nạp Giáp / Câu Trần / Đằng Xà" giữ Hán-Việt (thuật ngữ); "trong phép / có dẫn nhập / hai vị thần" dịch nghĩa tiếng Việt thường.

VÍ DỤ 4 (tựa sách — DỊCH + giữ tên chuyên ngành):
  GỐC: 《易经》中的数学
  ĐÚNG: Toán học trong Kinh Dịch
  SAI:  Kinh Dịch trung chi toán học  ← lỗi phiên âm

VÍ DỤ 5 (định giá — DỊCH NGHĨA):
  GỐC: 定价：68元
  ĐÚNG: Giá: 68 nhân dân tệ  (hoặc: 68 tệ)
  SAI:  Định giá: 68 nguyên  ← lỗi phiên âm

🔧 FORMAT:
- Giữ NGUYÊN markdown: # ## ###, bảng |, list -, link [[...]], placeholder [[FIGURE:...]], image ![](...)
- KHÔNG để chữ Hán còn sót (trừ trong placeholder hoặc code block)
- KHÔNG kèm "Bản dịch:" header. CHỈ trả về văn dịch.

ĐOẠN GỐC:
{text}

BẢN DỊCH (tiếng Việt hiện đại tự nhiên, thuật ngữ chuyên ngành giữ Hán-Việt):"""


# === Config & state ===
@dataclass
class TranslationStats:
    pages_done: int = 0
    pages_failed: int = 0
    chunks_deepseek: int = 0
    chunks_ollama: int = 0
    total_seconds: float = 0.0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    failures: list[str] = field(default_factory=list)


def _load_deepseek_key() -> str | None:
    """Load DEEPSEEK_API_KEY từ .env.local nếu chưa set."""
    if os.environ.get("DEEPSEEK_API_KEY"):
        return os.environ["DEEPSEEK_API_KEY"]
    env_file = Path("/Users/ozvietnamdesktop/Desktop/yi/.env.local")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    os.environ["DEEPSEEK_API_KEY"] = v
                    return v
    return None


def _has_han(text: str) -> bool:
    return any("一" <= c <= "鿿" for c in text)


# Model artifacts thường gặp ở đầu output cần lọc
_ARTIFACT_HEADERS = (
    "# Dịch nghĩa",
    "## Dịch nghĩa",
    "**Dịch nghĩa**",
    "Bản dịch:",
    "BẢN DỊCH:",
    "Dịch:",
    "DỊCH:",
    "**Bản dịch:**",
)


def _strip_artifacts(text: str) -> str:
    """Lọc artifacts mở đầu mà model thi thoảng thêm tự phát."""
    text = text.strip()
    # Loại bỏ artifact header ở đầu
    for art in _ARTIFACT_HEADERS:
        if text.startswith(art):
            # Cắt artifact + dòng trống/newline kế tiếp
            text = text[len(art):].lstrip("\n\r ")
            break
    # Loại bỏ trailing ``` nếu model wrap output trong code block
    if text.startswith("```") and text.endswith("```"):
        lines = text.split("\n")
        if len(lines) >= 2:
            text = "\n".join(lines[1:-1]).strip()
    return text


def _count_han(text: str) -> int:
    return sum(1 for c in text if "一" <= c <= "鿿")


# === Providers ===
def _deepseek_call(prompt: str, *, timeout: int = 60) -> tuple[str, dict]:
    """Call DeepSeek-chat. Returns (text, usage_dict). Raises on error."""
    key = _load_deepseek_key()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY không có trong env hoặc .env.local")
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 4000,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    out = d["choices"][0]["message"]["content"]
    usage = d.get("usage", {})
    return out, usage


def _ollama_call(prompt: str, *, model: str = "qwen2.5-coder:14b", timeout: int = 300) -> str:
    """Call Ollama local. Returns text. Raises on error."""
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 2500},
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"]


# === Core translate ===
def translate_chunk(
    text: str,
    *,
    stats: TranslationStats | None = None,
    prefer: str = "deepseek",
    quiet: bool = False,
) -> str:
    """Dịch 1 chunk text. Trả về bản dịch.

    prefer = "deepseek" | "ollama".
    Nếu primary fail → tự động fallback. Nếu cả 2 fail → raise.
    """
    if not text.strip():
        return text
    # Nếu chunk không có chữ Hán nào → skip
    if not _has_han(text):
        return text

    prompt = PROMPT_TEMPLATE.format(
        glossary=_glossary_prompt_section(),
        text=text,
    )
    t0 = time.time()

    primary, fallback = (
        ("deepseek", "ollama") if prefer == "deepseek" else ("ollama", "deepseek")
    )

    last_err: Exception | None = None
    for provider in (primary, fallback):
        try:
            if provider == "deepseek":
                out, usage = _deepseek_call(prompt)
                if stats:
                    stats.chunks_deepseek += 1
                    stats.total_tokens_in += usage.get("prompt_tokens", 0)
                    stats.total_tokens_out += usage.get("completion_tokens", 0)
            else:
                out = _ollama_call(prompt)
                if stats:
                    stats.chunks_ollama += 1
            # Post-process: lọc model artifact phổ biến
            out = _strip_artifacts(out)
            dt = time.time() - t0
            if stats:
                stats.total_seconds += dt
            if not quiet:
                han_remain = _count_han(out)
                tag = "🤖" if provider == "deepseek" else "🦙"
                msg = f"  {tag} {provider} {dt:.1f}s"
                if han_remain > 0:
                    msg += f" ⚠️ {han_remain} chữ Hán sót"
                print(msg)
            return out.strip()
        except Exception as e:
            last_err = e
            if not quiet:
                print(f"  ❌ {provider} failed: {type(e).__name__}: {e}")
            continue

    if stats:
        stats.failures.append(f"chunk[{text[:30]}...]: {last_err}")
    raise RuntimeError(f"Tất cả providers fail. Last: {last_err}")


# === Chunking ===
# Chia trang thành chunks theo paragraph (\n\n) để giữ context.
# DeepSeek max tokens out = 4000, prompt ~500 tokens overhead.
# Mỗi chunk an toàn ~ 1500 chars Hán.

_CHUNK_MAX_CHARS = 1500


def _split_into_chunks(text: str, max_chars: int = _CHUNK_MAX_CHARS) -> list[str]:
    """Chia text thành chunks ~max_chars, ưu tiên ranh giới paragraph."""
    if len(text) <= max_chars:
        return [text]
    paras = text.split("\n\n")
    chunks: list[str] = []
    buf = ""
    for p in paras:
        if not buf:
            buf = p
        elif len(buf) + 2 + len(p) <= max_chars:
            buf = buf + "\n\n" + p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks


def translate_page(
    zh_text: str,
    *,
    stats: TranslationStats | None = None,
    prefer: str = "deepseek",
    quiet: bool = False,
) -> str:
    """Dịch 1 trang. Tự chia chunks nếu dài."""
    chunks = _split_into_chunks(zh_text)
    if len(chunks) == 1:
        return translate_chunk(chunks[0], stats=stats, prefer=prefer, quiet=quiet)
    out_chunks: list[str] = []
    for i, c in enumerate(chunks, 1):
        if not quiet:
            print(f"  ↳ chunk {i}/{len(chunks)} ({len(c)} chars)")
        out_chunks.append(
            translate_chunk(c, stats=stats, prefer=prefer, quiet=quiet)
        )
    return "\n\n".join(out_chunks)


# === Corpus-level ===
def translate_corpus(
    corpus_path: str | Path,
    *,
    max_pages: int | None = None,
    start_page: int = 1,
    skip_existing: bool = True,
    prefer: str = "deepseek",
    verbose: bool = True,
) -> TranslationStats:
    """Dịch toàn bộ corpus pages → corpus_path/pages_vi/.

    Args:
        corpus_path: đường dẫn root corpus (e.g., data/yi_restored/thieu-khang-tiet-tq).
        max_pages: số trang tối đa (None = all).
        start_page: bắt đầu từ trang nào (1-indexed).
        skip_existing: nếu pages_vi/page-XXXX.md đã tồn tại → skip.
        prefer: "deepseek" hoặc "ollama" làm primary.
    """
    root = Path(corpus_path)
    pages_dir = root / "pages"
    pages_vi_dir = root / "pages_vi"
    pages_vi_dir.mkdir(exist_ok=True)

    # Sort pages by number
    src_pages = sorted(pages_dir.glob("page-*.md"))
    if not src_pages:
        # Try unprefixed format
        src_pages = sorted(pages_dir.glob("[0-9]*.md"))

    if start_page > 1:
        src_pages = src_pages[start_page - 1:]
    if max_pages:
        src_pages = src_pages[:max_pages]

    stats = TranslationStats()
    print(f"🪷 Dịch {len(src_pages)} trang từ {root.name} → pages_vi/")
    print(f"   prefer={prefer}, skip_existing={skip_existing}")
    print()

    t_total = time.time()
    for i, src in enumerate(src_pages, 1):
        dst = pages_vi_dir / src.name
        if skip_existing and dst.exists():
            if verbose:
                print(f"⏭️  [{i}/{len(src_pages)}] {src.name} — đã có, skip")
            continue
        zh = src.read_text()
        if not zh.strip():
            dst.write_text("")
            stats.pages_done += 1
            continue
        try:
            if verbose:
                print(f"📖 [{i}/{len(src_pages)}] {src.name} ({len(zh)} chars Hán)")
            vi = translate_page(zh, stats=stats, prefer=prefer, quiet=not verbose)
            # Footer attribution
            footer = (
                f"\n\n---\n"
                f"*Dịch tự động bằng DeepSeek-chat + qwen2.5-coder fallback (yi_translation v1, "
                f"{time.strftime('%Y-%m-%d')}). Có thể có sai sót — anh review trước khi dùng.*\n"
            )
            dst.write_text(vi + footer)
            stats.pages_done += 1
            if verbose:
                print(f"   ✅ → {dst.name}\n")
        except Exception as e:
            stats.pages_failed += 1
            stats.failures.append(f"{src.name}: {e}")
            if verbose:
                print(f"   ❌ FAIL: {e}\n")
            continue

    stats.total_seconds = time.time() - t_total
    print(_format_stats(stats))
    return stats


def _format_stats(s: TranslationStats) -> str:
    cost_input = s.total_tokens_in * 0.27 / 1_000_000
    cost_output = s.total_tokens_out * 1.10 / 1_000_000
    cost_total = cost_input + cost_output
    return f"""
{'='*60}
📊 KẾT QUẢ DỊCH
{'='*60}
  ✅ Pages done:    {s.pages_done}
  ❌ Pages failed:  {s.pages_failed}
  🤖 DeepSeek chunks: {s.chunks_deepseek}
  🦙 Ollama chunks:   {s.chunks_ollama}
  ⏱️  Total:        {s.total_seconds/60:.1f} phút
  💰 Token cost:   ${cost_total:.4f} (in={s.total_tokens_in:,} / out={s.total_tokens_out:,})
"""
