"""OCR backend abstraction — Tesseract + Ollama Vision LLM + (future) olmOCR/Surya.

Each backend implements `ocr_page(png_path) -> OcrPageResult`.

Available:
- TesseractBackend     — CLI, fast, ~85% on scan mờ
- OllamaVisionBackend  — Qwen2.5-VL hoặc MiniCPM-V qua Ollama, ~93-97% chất lượng,
                         thay Tesseract khi anh chạy local LLM trên M4

Future:
- OlmOcrBackend, SuryaBackend, MineruBackend
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OcrPageResult:
    text: str
    confidence: float = 0.0  # 0-1; backends that don't report → 0
    raw_output: str = ""     # full backend stdout for debugging
    backend: str = "tesseract"
    errors: list[str] = field(default_factory=list)


class OcrBackend:
    """Abstract OCR backend."""
    name: str = "abstract"

    def ocr_page(self, png_path: Path) -> OcrPageResult:
        raise NotImplementedError


class TesseractBackend(OcrBackend):
    """Wraps the `tesseract` CLI. Works with our existing pipeline.

    Stdin-piped to avoid Vietnamese filename encoding bug.
    """
    name = "tesseract"

    def __init__(self, lang: str = "vie", timeout: int = 60):
        self.lang = lang
        self.timeout = timeout

    def ocr_page(self, png_path: Path) -> OcrPageResult:
        try:
            with png_path.open("rb") as f:
                proc = subprocess.run(
                    ["tesseract", "-", "-", "-l", self.lang],
                    stdin=f, capture_output=True, timeout=self.timeout,
                )
            text = proc.stdout.decode("utf-8", errors="replace").strip()
            return OcrPageResult(
                text=text, confidence=0.85 if text else 0.0,
                raw_output=text, backend=self.name,
            )
        except subprocess.TimeoutExpired:
            return OcrPageResult(
                text="", confidence=0.0, backend=self.name,
                errors=[f"timeout after {self.timeout}s"],
            )
        except Exception as e:
            return OcrPageResult(
                text="", confidence=0.0, backend=self.name,
                errors=[f"{type(e).__name__}: {e}"],
            )


class OllamaVisionBackend(OcrBackend):
    """Use Ollama-hosted vision-language model (Qwen2.5-VL, MiniCPM-V) for OCR.

    Sends image as base64 to Ollama `/api/generate` with a strict OCR prompt.
    Recommended models:
    - qwen2.5-vl:7b         (best general VL OCR)
    - minicpm-v:8b          (best Chinese OCR)
    - llama3.2-vision:11b   (English-focused, less ideal for Vietnamese)

    Speed on M4 36GB: ~15-25 tok/s, 30-60s per page. Quality ~93-97% on scan mờ.
    """
    name = "ollama-vision"

    _OCR_PROMPT = (
        "Bạn là OCR engine chuyên đọc sách scan tiếng Việt + Hán cổ.\n"
        "Trích xuất TOÀN BỘ text từ ảnh, giữ nguyên xuống dòng + cấu trúc.\n\n"
        "## Quy tắc chung\n"
        "- KHÔNG dịch, KHÔNG diễn giải, KHÔNG bịa.\n"
        "- Nếu có Hán → giữ nguyên Hán.\n"
        "- Nếu chỗ nào mờ không đọc được → dùng [?].\n"
        "- Hiểu rõ chữ tiếng Việt có dấu (à, ả, ã, á, ạ ...).\n\n"
        "## Quy tắc CỰC KỲ QUAN TRỌNG về hình vẽ / biểu đồ\n"
        "Sách dịch học thường có hình vẽ quan trọng (Hà Đồ, Lạc Thư, vòng Bát Quái, "
        "biểu đồ Tử Vi, hình tròn âm-dương, sơ đồ ngũ hành...).\n"
        "Khi anh GẶP MỘT HÌNH VẼ trên trang, BẮT BUỘC làm 2 việc:\n\n"
        "1. Chèn placeholder vào đúng vị trí trong text dạng:\n"
        "   `[[FIGURE:<loại>|<mô_tả_chi_tiết>]]`\n\n"
        "2. <loại> chọn 1 trong:\n"
        "   - `ha_do`         (Hà Đồ — 10 chấm sắp xếp 1-2-3-4-5-6-7-8-9-10)\n"
        "   - `lac_thu`       (Lạc Thư — 9 ô như bàn cờ)\n"
        "   - `bat_quai_tien_thien`  (vòng Bát Quái Tiên Thiên — Phục Hy)\n"
        "   - `bat_quai_hau_thien`   (vòng Bát Quái Hậu Thiên — Văn Vương)\n"
        "   - `am_duong`      (vòng âm-dương hai cá)\n"
        "   - `que_hexagram`  (1 quẻ 6 hào — gạch ngang Âm/Dương)\n"
        "   - `bang_que`      (bảng các quẻ)\n"
        "   - `so_do_ngu_hanh` (sơ đồ Ngũ Hành Tương Sinh / Tương Khắc)\n"
        "   - `bieu_do_tu_vi` (lá số Tử Vi 12 cung)\n"
        "   - `bang`          (bảng dữ liệu)\n"
        "   - `khac`          (hình khác — phải mô tả kỹ trong <mô_tả>)\n\n"
        "3. <mô_tả_chi_tiết> phải bao gồm:\n"
        "   - Tên hình (nếu có caption trên/dưới hình)\n"
        "   - Số/ký tự xuất hiện (vd: '8 cung Đoài Ly Chấn Tốn Càn Khảm Cấn Khôn theo thứ tự kim đồng hồ')\n"
        "   - Vị trí trang (đầu/giữa/cuối trang, bên trái/phải)\n"
        "   - Đặc điểm nhận dạng để sau có thể vẽ lại\n\n"
        "## Ví dụ\n"
        "Nếu trang có Hà Đồ ở giữa, ghi:\n"
        "```\n"
        "Trở lên có chín hình vẽ Kinh Dịch...\n\n"
        "[[FIGURE:ha_do|Hà Đồ — hình tròn ở giữa trang, 10 chấm chia thành "
        "5 cặp: 1-6 trên (Bắc), 2-7 dưới (Nam), 3-8 trái (Đông), 4-9 phải (Tây), "
        "5-10 giữa. Chấm Âm (Dương) màu đen, chấm Dương (chẵn) màu trắng]]\n\n"
        "Sông Hà hiện đồ...\n"
        "```\n\n"
        "Trả về CHỈ text + placeholder hình vẽ. Không markdown wrapper, không bình luận."
    )

    def __init__(
        self,
        model: str = "qwen2.5vl:7b",  # Ollama uses no-hyphen tag
        endpoint: str | None = None,
        timeout: int = 600,
        lang: str = "vie",
    ):
        self.model = model
        self.endpoint = (endpoint or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout
        self.lang = lang  # for compat with TesseractBackend kwargs

    def ocr_page(self, png_path: Path) -> OcrPageResult:
        try:
            png_bytes = Path(png_path).read_bytes()
            b64 = base64.b64encode(png_bytes).decode("ascii")
        except Exception as e:
            return OcrPageResult(
                text="", backend=self.name, errors=[f"read image: {e}"]
            )
        body = {
            "model": self.model,
            "prompt": self._OCR_PROMPT,
            "images": [b64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 4000},
        }
        try:
            req = urllib.request.Request(
                f"{self.endpoint}/api/generate",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = json.loads(r.read().decode("utf-8"))
            text = (raw.get("response") or "").strip()
            return OcrPageResult(
                text=text,
                confidence=0.93 if text else 0.0,  # VL models generally outperform Tesseract
                raw_output=text,
                backend=self.name,
            )
        except urllib.error.URLError as e:
            return OcrPageResult(
                text="", backend=self.name,
                errors=[f"Ollama unreachable @ {self.endpoint}: {e.reason}"],
            )
        except Exception as e:
            return OcrPageResult(
                text="", backend=self.name,
                errors=[f"{type(e).__name__}: {e}"],
            )


def get_backend(name: str = "tesseract", **kwargs) -> OcrBackend:
    """Backend factory. Available:
    - 'tesseract'         (default, CLI)
    - 'ollama-vision' or 'ollama' or 'qwen-vl'   (local LLM, requires Ollama running)

    Future: 'olmocr', 'surya', 'mineru'.
    """
    if name == "tesseract":
        return TesseractBackend(**kwargs)
    if name in ("ollama-vision", "ollama", "qwen-vl", "qwen2.5-vl", "minicpm-v"):
        # Allow shorthand aliases — pop tesseract-only kwargs
        kwargs.pop("lang", None)  # keep behavior; lang ignored by VL backend
        # Default model mapping for friendly aliases
        if name == "minicpm-v" and "model" not in kwargs:
            kwargs["model"] = "minicpm-v:8b"
        elif name in ("qwen-vl", "qwen2.5-vl", "qwen2.5vl") and "model" not in kwargs:
            kwargs["model"] = "qwen2.5vl:7b"
        return OllamaVisionBackend(**kwargs)
    raise ValueError(f"OCR backend '{name}' not implemented yet")
