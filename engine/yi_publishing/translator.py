"""Translation backend — Trung → Việt batch translator via OpenRouter FREE models.

Primary: deepseek/deepseek-v4-flash:free (1M context, strong Chinese)
Fallback: google/gemma-4-31b-it:free

Cost: $0 (free tier).
Speed: ~3-5s per batch of 5-10 lines.

Translates per-region (preserving line structure) or per-line.
"""
from __future__ import annotations

import json
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# OpenRouter free models, in fallback order
FREE_TRANSLATION_MODELS = [
    "deepseek/deepseek-v4-flash:free",   # 1M context, strong CJK
    "google/gemma-4-31b-it:free",        # 262K context, multilingual
    "google/gemma-4-26b-a4b-it:free",    # 262K context
]

# MiniMax middle tier — Coding Plan (prepaid tokens, no per-call cost to anh)
# sk-cp-* keys use api.minimax.io OpenAI-style chat completions.
MINIMAX_TRANSLATION_MODELS = [
    "MiniMax-M2",   # reasoning model — may emit <think> blocks (stripped post-hoc)
]
MINIMAX_URL = "https://api.minimax.io/v1"

# Paid escalation — DeepSeek NATIVE API (not via OpenRouter).
# Cheap ($0.27/M in, $1.10/M out) but premium quality for CJK.
PAID_TRANSLATION_MODELS = [
    "deepseek-chat",  # V3 — best balance for translation
]

OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEEPSEEK_NATIVE_URL = "https://api.deepseek.com/v1"

# LM Studio local — OpenAI-compatible @ localhost:1234/v1 (no auth)
# Anh đã thay Ollama bằng LM Studio + cài Gemma 4 (2026-05-31)
import os as _os_lms
LMSTUDIO_URL = _os_lms.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1")
LMSTUDIO_TRANSLATION_MODELS = [
    "google/gemma-4-e4b",   # Gemma 4 8B variant — anh đã pull
]

_CLIENT = None              # OpenRouter client (free chain)
_MINIMAX_CLIENT = None      # MiniMax Coding Plan client (middle tier)
_DEEPSEEK_CLIENT = None     # DeepSeek native client (paid fallback)
_LMSTUDIO_CLIENT = None     # LM Studio local client (free, top of chain)


def _get_api_key() -> str:
    """Load OpenRouter key."""
    import os
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key
    keys_path = Path("/Users/ozvietnamdesktop/Desktop/yi/data/ai_keys.json")
    if keys_path.exists():
        keys = json.loads(keys_path.read_text())
        v = keys.get("openrouter")
        if isinstance(v, str):
            return v
    raise RuntimeError("OpenRouter API key not found")


def _get_deepseek_key() -> Optional[str]:
    """Load DeepSeek native key from env or ai_keys.json. Returns None if not set."""
    import os
    key = os.getenv("DEEPSEEK_API_KEY")
    if key:
        return key
    keys_path = Path("/Users/ozvietnamdesktop/Desktop/yi/data/ai_keys.json")
    if keys_path.exists():
        keys = json.loads(keys_path.read_text())
        v = keys.get("deepseek")
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            return v.get("api_key")
    return None


def get_client():
    global _CLIENT
    if _CLIENT is None:
        from openai import OpenAI
        _CLIENT = OpenAI(
            base_url=OPENROUTER_URL,
            api_key=_get_api_key(),
            default_headers={
                "HTTP-Referer": "https://yi-chronos.local",
                "X-Title": "YI-CHRONOS Publishing",
            },
        )
    return _CLIENT


def get_deepseek_client():
    """Lazy-init DeepSeek native client. Raises if key not configured."""
    global _DEEPSEEK_CLIENT
    if _DEEPSEEK_CLIENT is None:
        key = _get_deepseek_key()
        if not key:
            raise RuntimeError(
                "DeepSeek API key not configured. "
                "Add 'deepseek' to data/ai_keys.json or set DEEPSEEK_API_KEY env."
            )
        from openai import OpenAI
        _DEEPSEEK_CLIENT = OpenAI(
            base_url=DEEPSEEK_NATIVE_URL,
            api_key=key,
        )
    return _DEEPSEEK_CLIENT


def _get_minimax_key() -> Optional[str]:
    """Load MiniMax key from env or ai_keys.json. Returns None if not configured."""
    import os
    key = os.getenv("MINIMAX_API_KEY")
    if key:
        return key
    keys_path = Path("/Users/ozvietnamdesktop/Desktop/yi/data/ai_keys.json")
    if keys_path.exists():
        keys = json.loads(keys_path.read_text())
        v = keys.get("minimax")
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            return v.get("api_key")
    return None


def get_minimax_client():
    """Lazy-init MiniMax client (OpenAI-compatible). Raises if key not configured."""
    global _MINIMAX_CLIENT
    if _MINIMAX_CLIENT is None:
        key = _get_minimax_key()
        if not key:
            raise RuntimeError(
                "MiniMax API key not configured. "
                "Add 'minimax' to data/ai_keys.json or set MINIMAX_API_KEY env."
            )
        from openai import OpenAI
        _MINIMAX_CLIENT = OpenAI(
            base_url=MINIMAX_URL,
            api_key=key,
        )
    return _MINIMAX_CLIENT


def has_minimax_fallback() -> bool:
    """Check if MiniMax middle tier is available."""
    return _get_minimax_key() is not None


def get_lmstudio_client():
    """Lazy-init LM Studio local client (OpenAI-compatible). No real auth needed."""
    global _LMSTUDIO_CLIENT
    if _LMSTUDIO_CLIENT is None:
        from openai import OpenAI
        _LMSTUDIO_CLIENT = OpenAI(
            base_url=LMSTUDIO_URL,
            api_key="lm-studio",  # dummy — LM Studio không check
        )
    return _LMSTUDIO_CLIENT


def has_lmstudio() -> bool:
    """Check LM Studio @ localhost:1234 is reachable. Cached weakly."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(f"{LMSTUDIO_URL}/models")
        with urllib.request.urlopen(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def has_paid_fallback() -> bool:
    """Check if paid DeepSeek fallback is available without trying to call it."""
    return _get_deepseek_key() is not None


SYSTEM_PROMPT_BASE = """Bạn là dịch giả chuyên Đông phương học, mạnh về Dịch học (Kinh Dịch, Mai Hoa Dịch Số) và Tử Vi Đẩu Số của các tổ sư Thiệu Khang Tiết, Trần Đoàn.

Quy tắc dịch:
1. Dịch CHÍNH XÁC từ Trung văn sang tiếng Việt, giữ nghĩa nguyên văn.
2. Thuật ngữ Đông phương GIỮ NGUYÊN dạng Hán-Việt:
   - Dịch học: Bát Quái, Càn, Khôn, Khảm, Ly, Chấn, Tốn, Cấn, Đoài, Hà Đồ, Lạc Thư, Tiên Thiên, Hậu Thiên, Thái Cực, Lưỡng Nghi, Tứ Tượng, Thể-Dụng, Ngũ Hành.
   - Tử Vi Đẩu Số (紫微斗数): Tử Vi, Thiên Phủ, Thiên Cơ, Thái Dương, Vũ Khúc, Thiên Đồng, Liêm Trinh, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân, Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc, Lộc Tồn, Thiên Mã, Hoá Lộc, Hoá Quyền, Hoá Khoa, Hoá Kỵ.
   - 12 cung: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ.
   - Đại Vận, Tiểu Hạn, Lưu Niên; Thiên Bàn, Địa Bàn; chính tinh, phụ tinh, hung tinh, cát tinh.
   - Thiên Can, Địa Chi: Giáp, Ất, Bính, Đinh… / Tý, Sửu, Dần, Mão…
3. Tên người, sách Trung văn → Hán-Việt (邵雍 = Thiệu Ung, hiệu Khang Tiết; 陈抟 = Trần Đoàn; 紫微斗数全书 = Tử Vi Đẩu Số Toàn Thư; 易经 = Kinh Dịch; 梅花易数 = Mai Hoa Dịch Số).
4. Câu Việt phải tự nhiên, KHÔNG dịch máy móc word-by-word.
5. KHÔNG thêm giải thích, KHÔNG comment — CHỈ trả về bản dịch.
6. TUYỆT ĐỐI KHÔNG được trả lại nguyên văn Trung văn. MỌI ký tự Hán PHẢI được Việt hoá (trừ tên riêng để trong ngoặc).
7. Output PHẢI có đúng số dòng yêu cầu, không thừa không thiếu.
8. CẨN THẬN dấu thanh và nguyên âm ư/ương/ưởng/ướng:
   - thường (常, ordinary) ≠ thượng (上, upper) ≠ thương (商/伤, merchant/sorrow) ≠ thưởng (赏, reward)
   - hướng (向, direction) ≠ hưởng (享, enjoy) ≠ hương (香, fragrance/village)
   - dương (阳, yang) ≠ dưỡng (养, nurture) ≠ đường (堂/路, hall/road)
   - cường (强, strong) ≠ cương (纲, principle) ≠ cường (倞, light)
   Chọn đúng theo ngữ cảnh; KHÔNG bao giờ viết "uong/huong/duong" không dấu.

Output format: JSON object {"translations": ["bản dịch dòng 1", "bản dịch dòng 2", ...]}"""

SYSTEM_PROMPT_TABLE = """Bạn là dịch giả chuyên Đông phương học. Đoạn dưới đây là MỘT BẢNG ĐỐI ỨNG (table) tách dòng — thường chứa nhiều cặp khái niệm Dịch học nối nhau qua dấu phẩy/chấm phẩy/Trung văn (，；).

Quy tắc đặc biệt cho bảng:
1. Dịch TỪNG cặp/cụm thuật ngữ một, GIỮ NGUYÊN cấu trúc phân cách (，→",", ；→";").
2. Mỗi quẻ giữ Hán-Việt: 乾→Càn, 坤→Khôn, 震→Chấn, 巽→Tốn, 坎→Khảm, 离→Ly, 艮→Cấn, 兑→Đoài.
3. Khái niệm sau "为/表示" là VAI TRÒ/Ý NGHĨA — phải dịch sang Việt (vd: 君父→vua-cha, 农夫→nông dân).
4. TUYỆT ĐỐI KHÔNG được trả lại Trung văn nguyên xi. Mỗi ký tự Hán phải Việt hoá.
5. Giữ đúng số dòng.

Output format: JSON object {"translations": [...]}"""

SYSTEM_PROMPT_TOC = """Bạn là dịch giả chuyên Đông phương học. Đoạn dưới đây là MỤC LỤC (table of contents) của sách.

Quy tắc đặc biệt cho mục lục:
1. Mỗi dòng thường có dạng: <tên chương>/<số trang> hoặc <tên chương>：<phụ đề>/<số trang>.
2. Dịch phần <tên chương> và <phụ đề> sang tiếng Việt tự nhiên.
3. GIỮ NGUYÊN số trang (vd: /1-8, /IO, /18) y nguyên ở cuối.
4. Chương số dùng định dạng Việt: "第壹章" → "Chương 1", "第贰章" → "Chương 2", "第叁章" → "Chương 3"…
5. Dấu phân cách Trung văn "：" → ":" trong tiếng Việt.
6. TUYỆT ĐỐI KHÔNG để nguyên ký tự Hán nào.
7. Giữ đúng số dòng.

Ví dụ:
  Input:  "第壹章易学的秘密：乾坤万物有数理"
  Output: "Chương 1 — Bí mật của Dịch học: Càn Khôn vạn vật đều có số lý"

  Input:  "大千世界中的八卦/1-8"
  Output: "Bát Quái trong thế giới mênh mông/1-8"

Output format: JSON object {"translations": [...]}"""

# Backwards-compat alias
SYSTEM_PROMPT = SYSTEM_PROMPT_BASE


# ─── 2-LAYER PROMPT: Hán-Việt + Luận giải ───────────────────────────────────
# Anh's directive 2026-05-19:
# - Dịch Hán-Việt 1:1 (giữ thuật ngữ chuyên môn để tra wiki) — đã làm tốt
# - THÊM lớp 2: luận giải nghĩa dễ hiểu cho bá tánh (giữ thuật ngữ chính
#   trong ngoặc Hán-Việt, viết tiếng Việt hiện đại)
# - Dùng chapter context để dịch nhất quán
# - Đây là format chuẩn cho XUẤT BẢN SÁCH

# LAYER 3 — "Giải thích dân dã" — KHÔNG dùng jargon, viết cho người chưa biết Tử Vi
SYSTEM_PROMPT_LAYER3_DANDA = """Bạn là người KỂ LẠI sách cổ điển cho người mới học Tử Vi (chưa biết gì về Tử Vi Đẩu Số). Đây KHÔNG phải dịch chuyên môn — đây là GIẢI THÍCH ĐƠN GIẢN.

ĐỐI TƯỢNG: người Việt phổ thông, KHÔNG biết Tử Vi là gì, lần đầu nghe các thuật ngữ.

QUY TẮC TUYỆT ĐỐI:
1. KHÔNG dùng thuật ngữ chuyên môn nguyên Hán-Việt. Mọi từ chuyên môn phải DỊCH NGHĨA hoặc thay bằng từ thường dân.
   - "Hóa Lộc" → "sao tài lộc" (kèm chú: "trong Tử Vi gọi là Hóa Lộc")
   - "Thiên Mã" → "sao 'di chuyển/đi xa'"
   - "Tuần Không Vong" → "vùng trống rỗng vô nghĩa, làm gì cũng không ra kết quả"
   - "Khôi Việt" → "2 sao quý nhân tốt lành"
   - "Tả Phụ Hữu Bật" → "2 sao trợ tá hai bên"
   - "Văn Xương Văn Khúc" → "2 sao học vấn/văn chương"
   - "Kình Dương Đà La" → "2 sao tổn thương/sát khí"
   - "Tử Vi" → "sao vua/lãnh đạo (sao chính của hệ thống)"
   - "Mệnh cung" → "cung Mệnh (vị trí trung tâm trong lá số, đại diện cho bản thân)"
   - "Đại Hạn" → "vận lớn 10 năm"
   - "Tiểu Hạn" → "vận từng năm"
   - "Đẩu Quân" → "sao chỉ tháng sinh"
   - "Tứ Hóa" → "4 sao biến hóa (Lộc/Quyền/Khoa/Kỵ)"

2. Viết NGẮN GỌN, TRỰC TIẾP. Mỗi câu Hán → 1-2 câu Việt thường dân.

3. NÊU RÕ HẬU QUẢ THỰC SỰ: "thì sẽ thế nào trong đời thực".
   - "Lộc phùng xung phá, cát xứ tàng hung" → "Nếu sao tài lộc bị các sao xấu phá → kể cả ở vị trí tốt cũng ẩn họa. Nói cách khác: tưởng giàu nhưng dễ mất."
   - "Mã ngộ không vong" → "Sao đi-xa gặp vùng trống → cả đời chạy vạy nhiều mà không kết quả."

4. KHÔNG nói "Hóa", "Sát", "Cát", "Hung" mà KHÔNG GIẢI NGHĨA.

5. KHÔNG meta-commentary. Chỉ giải nghĩa câu Phú đó.

Output JSON: {"translations": [{"giaithichdande": "..."}, ...]}"""


SYSTEM_PROMPT_TWO_LAYER = """BẠN LÀ DỊCH GIẢ + BIÊN TẬP HỌC THUẬT chuyên Đông phương học cổ điển — Tử Vi Đẩu Số (紫微斗数), Mai Hoa Dịch Số (梅花易数), Kinh Dịch (易经), Bát Tự, Phong Thủy.

ĐỐI TƯỢNG ĐỌC: người Việt yêu Dịch học / Tử Vi, có thể biết một số chữ Hán-Việt nhưng cần luận giải nghĩa lý chuyên sâu. KHÔNG phải trẻ em, KHÔNG phải người mới biết.

VĂN PHONG BẮT BUỘC:
- Học thuật, trang trọng, nghiêm túc — như sách kinh điển dịch sang Việt văn (vd lối Ngô Tất Tố dịch Kinh Dịch).
- TUYỆT ĐỐI KHÔNG dịch thành: văn xuôi đơn giản, truyện kể, "kể chuyện cho bé nghe", văn nói, văn báo chí, phong cách self-help.
- KHÔNG diễn xuôi quá tự do (vd "ta hãy cùng tìm hiểu...", "bạn sẽ thấy rằng...").
- Giữ giọng văn cổ điển Đông phương: nghiêm tịnh, súc tích, sâu xa.

────────────────────────────────────────────────
LỚP 1 — `hanviet`: bản Hán-Việt đối chiếu 1:1
────────────────────────────────────────────────
- Phiên âm Hán-Việt từng chữ, giữ NGUYÊN thứ tự + cấu trúc câu cổ.
- Dấu câu giữ nguyên (，→",", 。→".", ；→";", ：→":").
- Tên người, sách, địa danh: theo cách đọc Hán-Việt chuẩn.

────────────────────────────────────────────────
LỚP 2 — `luangiai`: luận giải nghĩa học thuật
────────────────────────────────────────────────
- Diễn nghĩa câu Hán thành Việt văn HỌC THUẬT — trôi chảy nhưng vẫn cô đọng và nghiêm túc.
- Có thể bổ sung CHỦ NGỮ, BỔ NGỮ tiếng Việt khi câu Hán cô đọng (vd: 禄逢冲破 → "Hóa Lộc khi gặp xung phá...").
- Có thể tách 1 câu Hán dài thành 2 mệnh đề Việt nhỏ — nhưng KHÔNG biến thành đoạn văn dài.
- Nếu thuật ngữ chuyên môn lần đầu xuất hiện trong batch, có thể chú thích NGẮN trong ngoặc đơn (≤ 8 chữ): vd "Hóa Lộc (sao tài)", "Đẩu Quân (sao tháng)".
- KHÔNG thêm "câu chuyện hóa": KHÔNG viết "khi gặp tình huống này thì...", "trong cuộc đời chúng ta...", "bạn cần lưu ý rằng..."

────────────────────────────────────────────────
GLOSSARY — GIỮ NGUYÊN HÁN-VIỆT (cả trong hanviet VÀ luangiai)
────────────────────────────────────────────────
[Bát Quái]: Càn, Khôn, Khảm, Ly, Chấn, Tốn, Cấn, Đoài.
[Kinh Dịch]: Tiên Thiên, Hậu Thiên, Thái Cực, Lưỡng Nghi, Tứ Tượng, Hà Đồ, Lạc Thư, Thể-Dụng.
[Ngũ Hành]: Kim, Mộc, Thủy, Hỏa, Thổ; tương sinh, tương khắc.
[14 chính tinh Tử Vi]: Tử Vi, Thiên Cơ, Thái Dương, Vũ Khúc, Thiên Đồng, Liêm Trinh, Thiên Phủ, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân.
[Phụ tinh]: Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt.
[Sát tinh]: Kình Dương, Đà La, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp, Lộc Tồn.
[12 cung]: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ.
[Tứ Hóa]: Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ.
[Hạn]: Đại Hạn, Tiểu Hạn, Đồng Hạn, Đẩu Quân, Lưu niên.
[Thiên Can]: Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý.
[Địa Chi]: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.
[Tên nhân vật]: 邵雍=Thiệu Ung (hiệu Khang Tiết), 陈抟=Trần Đoàn (hiệu Hi Di), 程颐=Trình Di, 程颢=Trình Hạo, 朱熹=Chu Hi.
[Tên sách + phú]: 紫微斗数全书=Tử Vi Đẩu Số Toàn Thư, 太微赋=Thái Vi Phú, 形性赋=Hình Tính Phú, 斗数骨髓赋=Đẩu Số Cốt Tủy Phú.

→ Các thuật ngữ này GIỮ NGUYÊN trong cả hanviet VÀ luangiai. KHÔNG dịch thành tiếng Việt phổ thông (vd KHÔNG được viết "sao Tài" thay "Hóa Lộc", KHÔNG được viết "cung Số mệnh" thay "Mệnh cung").

────────────────────────────────────────────────
QUY TẮC ĐẦU RA
────────────────────────────────────────────────
1. TUYỆT ĐỐI KHÔNG trả lại nguyên Trung văn không dịch — mọi ký tự Hán phải Hán-Việt hoá.
2. Output ĐÚNG số dòng yêu cầu, không thừa không thiếu.
3. Cẩn thận ư/ương/ưởng/ướng: thường ≠ thượng ≠ thương ≠ thưởng; hướng ≠ hưởng ≠ hương; dương ≠ dưỡng ≠ đường.
4. Khi gặp tên sao/thuật ngữ phức tạp lần đầu, chú thích trong ngoặc đơn ngắn gọn.
5. KHÔNG meta-commentary ("trong sách này", "tác giả nói rằng", "đoạn này có ý...") — chỉ DỊCH NGHĨA câu đó.

────────────────────────────────────────────────
VÍ DỤ CHUẨN
────────────────────────────────────────────────
Input:  "斗数至玄至微，理旨易明，虽设问于百篇之中，犹有言而未尽。"
Output:
  hanviet: "Đẩu số chí huyền chí vi, lý chỉ dị minh, tuy thiết vấn ư bách thiên chi trung, do hữu ngôn nhi vị tận."
  luangiai: "Đẩu Số vốn chí huyền chí vi, song lý chỉ vẫn có thể làm sáng tỏ; dẫu đã đặt vấn đề trong cả trăm bài, lời lẽ vẫn chưa thể cùng tận."

Input:  "禄逢冲破，吉处藏凶；马遇空亡，终身奔走。"
Output:
  hanviet: "Lộc phùng xung phá, cát xứ tàng hung; Mã ngộ không vong, chung thân bôn tẩu."
  luangiai: "Hóa Lộc gặp xung phá thì chỗ cát ẩn chứa điềm hung; Thiên Mã gặp Tuần Không Vong thì trọn đời phải bôn tẩu."

Input:  "紫微星坐命，主富贵荣华。"
Output:
  hanviet: "Tử Vi tinh tọa Mệnh, chủ phú quý vinh hoa."
  luangiai: "Sao Tử Vi tọa thủ cung Mệnh, chủ về phú quý và vinh hoa."

────────────────────────────────────────────────
FORMAT OUTPUT (BẮT BUỘC)
────────────────────────────────────────────────
JSON object: {
  "translations": [
    {"hanviet": "…", "luangiai": "…"},
    {"hanviet": "…", "luangiai": "…"},
    …
  ]
}"""


def _detect_content_kind(lines: list[str]) -> str:
    """Heuristic: classify a batch of lines as 'toc' / 'table' / 'normal'.

    'toc' if >40% of non-empty lines contain typical TOC markers (/数字 or 第..章)
    'table' if >40% lines have ≥2 occurrences of CJK comma/semicolon
    """
    import re
    non_empty = [l for l in lines if (l or "").strip()]
    if not non_empty:
        return "normal"

    toc_pat = re.compile(r"(第[壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十]+章)|(/[\dIVXLCDM]+(-[\dIVXLCDM]+)?$)")
    toc_count = sum(1 for l in non_empty if toc_pat.search(l))

    # Table heuristic: many CJK enumeration marks (、) OR semicolons,
    # AND mentions of multiple trigram names in the same line.
    trigrams = ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]
    table_count = 0
    for l in non_empty:
        sep_count = l.count("、") + l.count("；") + l.count("，")
        trigram_count = sum(1 for t in trigrams if t in l)
        if sep_count >= 4 and trigram_count >= 2:
            table_count += 1
        elif sep_count >= 6:  # heavy enumerate even without trigrams
            table_count += 1

    ratio_toc = toc_count / len(non_empty)
    ratio_table = table_count / len(non_empty)

    if ratio_toc >= 0.4:
        return "toc"
    if ratio_table >= 0.4:
        return "table"
    return "normal"


def translate_lines(
    lines: list[str],
    *,
    model: Optional[str] = None,
    context: str = "",
    timeout: int = 180,             # tăng timeout cho batch lớn
    kind: str = "auto",
    allow_paid_fallback: bool = False,
    max_lines_per_call: Optional[int] = None,  # auto: 50 for paid, 25 for free
    two_layer: bool = False,        # produce {hanviet, luangiai} per line
) -> dict:
    """
    Translate Trung văn sang tiếng Việt 2 lớp (Hán-Việt + luận giải).

    DeepSeek paid hỗ trợ 128K input context + 8K output. Send lớn batch
    để giữ context chương — kết quả nhất quán hơn.
    """
    # Decide chunk size by provider intent
    if max_lines_per_call is None:
        wants_paid = (
            (model in PAID_TRANSLATION_MODELS)
            or (model and model.startswith("deepseek-"))
            or allow_paid_fallback
        )
        # Paid DeepSeek can do 8K output → safely fit ~50 lines × 2-layer
        # Free chain limited to 4K output → 25 lines safe
        if two_layer:
            max_lines_per_call = 30 if wants_paid else 15  # 2-layer output ~2x
        else:
            max_lines_per_call = 50 if wants_paid else 25
    """Translate list of Chinese lines to Vietnamese (batch).

    Args:
        lines: list of source text strings
        model: specific model ID (default: try free models in order)
        context: optional surrounding context (e.g. paragraph topic)
        kind: content kind — picks the right system prompt.
              'auto' auto-detects via heuristics.

    Returns: dict with translations, model_used, elapsed_seconds, kind
    """
    if not lines:
        return {"translations": [], "model_used": None, "elapsed_seconds": 0, "kind": kind}

    # Auto-chunk if too many lines — split into smaller batches & recursively translate
    if len(lines) > max_lines_per_call:
        all_translations = []
        total_elapsed = 0.0
        total_cost = 0.0
        used_model = None
        used_provider = None
        last_kind = kind
        chunk_size = max_lines_per_call
        for chunk_start in range(0, len(lines), chunk_size):
            chunk = lines[chunk_start:chunk_start + chunk_size]
            sub_result = translate_lines(
                chunk,
                model=model,
                context=context,
                timeout=timeout,
                kind=kind,
                allow_paid_fallback=allow_paid_fallback,
                max_lines_per_call=chunk_size + 1,  # avoid infinite recursion
                two_layer=two_layer,
            )
            all_translations.extend(sub_result["translations"])
            total_elapsed += sub_result.get("elapsed_seconds", 0)
            total_cost += sub_result.get("cost_usd", 0) or 0
            used_model = sub_result.get("model_used") or used_model
            used_provider = sub_result.get("provider") or used_provider
            last_kind = sub_result.get("kind") or last_kind
        return {
            "translations": all_translations,
            "model_used": used_model,
            "provider": used_provider,
            "elapsed_seconds": total_elapsed,
            "lines_count": len(lines),
            "kind": last_kind,
            "cost_usd": round(total_cost, 6),
            "chunked": True,
        }

    # Resolve kind
    if kind == "auto":
        kind = _detect_content_kind(lines)

    # Pick system prompt — 2-layer takes priority over kind-specific
    if two_layer:
        sys_prompt = SYSTEM_PROMPT_TWO_LAYER
    elif kind == "toc":
        sys_prompt = SYSTEM_PROMPT_TOC
    elif kind == "table":
        sys_prompt = SYSTEM_PROMPT_TABLE
    else:
        sys_prompt = SYSTEM_PROMPT_BASE

    client = get_client()

    # Build user prompt
    numbered = "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
    if two_layer:
        user_prompt = f"""Dịch {len(lines)} dòng Trung văn sau theo format 2 LỚP (hanviet + luangiai).

{f"Bối cảnh chương đang dịch: {context}" if context else ""}

Các dòng cần dịch:
{numbered}

Trả về JSON: {{"translations": [{{"hanviet": "...", "luangiai": "..."}}, ...]}} với đúng {len(lines)} dòng.
Tuyệt đối không trả lại nguyên Trung văn. Mỗi câu phải có ĐỦ 2 lớp.
Luận giải phải viết Việt hiện đại mượt mà, người đọc không cần biết Hán vẫn hiểu."""
    else:
        user_prompt = f"""Dịch {len(lines)} dòng Trung văn sau sang tiếng Việt.

{f"Bối cảnh: {context}" if context else ""}

Các dòng cần dịch:
{numbered}

Trả về JSON: {{"translations": ["dòng 1 dịch", "dòng 2 dịch", ...]}} với đúng {len(lines)} dòng.
KHÔNG được trả lại nguyên Trung văn — mỗi ký tự Hán phải Việt hoá."""

    # Build candidate list: [explicit model] OR [free chain] (+ MiniMax middle) (+ paid fallback if enabled)
    # Tier order: free OpenRouter (rẻ nhất) → MiniMax (anh has Coding Plan = prepaid) → DeepSeek paid ($)
    if model:
        # Auto-route: if explicit model is a paid DeepSeek name, use native
        if model in PAID_TRANSLATION_MODELS or model.startswith("deepseek-"):
            models_to_try = [(model, "deepseek-native")]
        elif model in MINIMAX_TRANSLATION_MODELS or model.startswith("MiniMax-"):
            models_to_try = [(model, "minimax")]
        elif model in LMSTUDIO_TRANSLATION_MODELS or model.startswith("google/gemma-") or model.startswith("lmstudio:"):
            models_to_try = [(model.replace("lmstudio:", ""), "lmstudio")]
        else:
            models_to_try = [(model, "openrouter")]
    elif two_layer and allow_paid_fallback and has_paid_fallback():
        # 2-layer (luangiai) cần output dài (~5-8K) — vượt cap 4K của free.
        # PAID-FIRST: tránh waste time retry free chain.
        # Free chỉ làm fallback nếu paid lỗi.
        models_to_try = [(m, "deepseek-native") for m in PAID_TRANSLATION_MODELS]
        if has_minimax_fallback():
            models_to_try.extend([(m, "minimax") for m in MINIMAX_TRANSLATION_MODELS])
        models_to_try.extend([(m, "openrouter") for m in FREE_TRANSLATION_MODELS])
    else:
        # Single-layer: LM Studio LOCAL first (free, $0, no rate limit) → free OpenRouter → MiniMax → DeepSeek paid
        models_to_try = []
        if has_lmstudio():
            models_to_try.extend([(m, "lmstudio") for m in LMSTUDIO_TRANSLATION_MODELS])
        models_to_try.extend([(m, "openrouter") for m in FREE_TRANSLATION_MODELS])
        if has_minimax_fallback():
            models_to_try.extend([(m, "minimax") for m in MINIMAX_TRANSLATION_MODELS])
        if allow_paid_fallback and has_paid_fallback():
            models_to_try.extend([(m, "deepseek-native") for m in PAID_TRANSLATION_MODELS])

    last_error = None

    for m, provider in models_to_try:
        try:
            t0 = time.time()
            logger.info(f"Translating {len(lines)} lines [{kind}] with {m} via {provider}...")
            # Pick client per provider
            if provider == "deepseek-native":
                active_client = get_deepseek_client()
            elif provider == "minimax":
                active_client = get_minimax_client()
            elif provider == "lmstudio":
                active_client = get_lmstudio_client()
            else:
                active_client = client
            # Generous max_tokens — DeepSeek-chat supports 8K; MiniMax-M2 ~8K;
            # OpenRouter free caps ~4K; LM Studio Gemma 4 e4b context 8K (safe 3K out).
            if provider in ("deepseek-native", "minimax"):
                max_out = 8000
            elif provider == "lmstudio":
                max_out = 3000  # gemma-4-e4b local cap
            else:
                max_out = 4000
            # LM Studio chỉ chấp nhận json_schema / text — không json_object
            if provider == "lmstudio":
                if two_layer:
                    item_schema = {
                        "type": "object",
                        "properties": {
                            "hanviet": {"type": "string"},
                            "luangiai": {"type": "string"},
                        },
                        "required": ["hanviet", "luangiai"],
                    }
                else:
                    item_schema = {"type": "string"}
                rf = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "translations_response",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "translations": {
                                    "type": "array",
                                    "items": item_schema,
                                    "minItems": len(lines),
                                    "maxItems": len(lines),
                                },
                            },
                            "required": ["translations"],
                            "additionalProperties": False,
                        },
                    },
                }
            else:
                rf = {"type": "json_object"}

            response = active_client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=rf,
                timeout=timeout,
                max_tokens=max_out,
            )
            elapsed = time.time() - t0
            content = response.choices[0].message.content
            # MiniMax-M2 (reasoning) prepends <think>...</think> + may wrap in ```json``` markdown
            # LM Studio Gemma 4 sometimes wraps in ```json``` too
            if provider in ("minimax", "lmstudio") and content:
                import re as _re
                content = _re.sub(r"<think>.*?</think>\s*", "", content, flags=_re.DOTALL | _re.IGNORECASE).strip()
                # Strip markdown code fence
                content = _re.sub(r"^```(?:json)?\s*\n?", "", content)
                content = _re.sub(r"\n?```\s*$", "", content).strip()

            # Parse JSON with multi-stage fallback
            translations = []
            try:
                parsed = json.loads(content)
                translations = parsed.get("translations", []) or []
            except json.JSONDecodeError:
                # Stage 2: regex extract first {...} blob then re-parse
                import re
                match = re.search(r'\{.*"translations".*\}', content, re.S)
                if match:
                    try:
                        parsed = json.loads(match.group(0))
                        translations = parsed.get("translations", []) or []
                    except json.JSONDecodeError:
                        match = None  # fall through to repair
                if not translations:
                    # Stage 3: json-repair (handles truncated, trailing commas, etc.)
                    try:
                        import json_repair
                        repaired = json_repair.repair_json(content, return_objects=True)
                        if isinstance(repaired, dict):
                            translations = repaired.get("translations", []) or []
                        elif isinstance(repaired, list):
                            translations = repaired
                        if translations:
                            logger.info(f"JSON repaired: got {len(translations)} translations")
                    except Exception as repair_err:
                        logger.warning(f"json-repair failed: {repair_err}")
                if not translations:
                    raise json.JSONDecodeError(
                        f"All JSON parse strategies failed. Raw: {content[:200]}",
                        content, 0,
                    )

            if len(translations) != len(lines):
                logger.warning(
                    f"Got {len(translations)} translations but expected {len(lines)}. "
                    f"Padding/truncating."
                )
                # Pad with empties or truncate
                empty_pad = {"hanviet": "", "luangiai": ""} if two_layer else ""
                while len(translations) < len(lines):
                    translations.append(empty_pad)
                translations = translations[: len(lines)]

            # In 2-layer mode, derive the "hanviet" string for quality check
            # so the existing gate logic still works.
            def _tgt_text(t):
                if two_layer:
                    if isinstance(t, dict):
                        return (t.get("hanviet") or "").strip()
                    return ""
                return (t or "").strip()

            # QUALITY GATE — fall through to next model if output is clearly broken
            non_empty_src = [l for l in lines if (l or "").strip()]
            if non_empty_src:
                empty_outputs = sum(
                    1 for src, tgt in zip(lines, translations)
                    if (src or "").strip() and not _tgt_text(tgt)
                )
                identical = sum(
                    1 for src, tgt in zip(lines, translations)
                    if (src or "").strip() and (src or "").strip() == _tgt_text(tgt)
                )
                broken_ratio = (empty_outputs + identical) / max(len(non_empty_src), 1)
                if broken_ratio > 0.4:
                    logger.warning(
                        f"Quality gate FAIL on {m}: "
                        f"{empty_outputs} empty + {identical} identical / "
                        f"{len(non_empty_src)} non-empty source "
                        f"(broken_ratio={broken_ratio:.2f}). Falling back to next model."
                    )
                    last_error = RuntimeError(
                        f"quality_gate_fail (broken_ratio={broken_ratio:.2f})"
                    )
                    continue  # try next model

            # Pull token usage (for cost tracking)
            usage_info = None
            try:
                u = response.usage
                if u:
                    usage_info = {
                        "prompt_tokens": getattr(u, "prompt_tokens", 0),
                        "completion_tokens": getattr(u, "completion_tokens", 0),
                        "total_tokens": getattr(u, "total_tokens", 0),
                    }
            except Exception:
                pass

            # Cost estimate (DeepSeek native: $0.27/M in + $1.10/M out — V3 base)
            cost_usd = 0.0
            if provider == "deepseek-native" and usage_info:
                cost_usd = (
                    usage_info["prompt_tokens"] * 0.27 / 1_000_000
                    + usage_info["completion_tokens"] * 1.10 / 1_000_000
                )

            return {
                "translations": translations,
                "model_used": m,
                "provider": provider,
                "elapsed_seconds": elapsed,
                "lines_count": len(lines),
                "kind": kind,
                "usage": usage_info,
                "cost_usd": round(cost_usd, 6),
            }
        except Exception as e:
            last_error = e
            logger.warning(f"Model {m} ({provider}) failed: {type(e).__name__}: {str(e)[:200]}")
            continue

    raise RuntimeError(f"All translation models failed. Last error: {last_error}")


def translate_page_lines(
    all_lines: list[dict],
    *,
    context: str = "",
    model: Optional[str] = None,
    allow_paid_fallback: bool = False,
    two_layer: bool = False,
) -> dict:
    """Translate ALL lines of a page in ONE API call (avoids rate limits).

    Args:
        all_lines: list of dicts with 'line_id' + 'source_text'
        context: optional page-level context (chapter title, topic)
        two_layer: if True, return {hanviet, luangiai} dict per line.

    Returns:
        translations_by_line_id:
          - single-layer: {line_id: vi_text}
          - 2-layer:      {line_id: {"hanviet": ..., "luangiai": ...}}
        stats: dict with elapsed_seconds, model_used, lines, cost_usd
    """
    # Filter empty source
    non_empty = [l for l in all_lines if l.get("source_text", "").strip()]
    if not non_empty:
        return {"translations_by_line_id": {}, "stats": {"lines": 0}}

    # Group lines by region_type → content kind
    # Each line may have a 'region_type' (title/text/list/table) — we use it
    # to bias the kind classifier, but final kind is decided by content heuristic
    # over the GROUP of lines.
    groups = {}  # kind -> list of line dicts (preserve original ordering inside group)
    for line in non_empty:
        rtype = (line.get("region_type") or "").lower()
        if rtype == "table":
            kind = "table"
        elif rtype == "title" and (line.get("source_text", "").startswith("目录")
                                   or "章" in line.get("source_text", "")):
            kind = "toc"
        else:
            # Heuristic per-line; final group decision is by majority
            kind = "normal"
        groups.setdefault(kind, []).append(line)

    # For 'normal' bucket, re-detect TOC/table by content heuristic per group
    if "normal" in groups:
        texts = [l["source_text"] for l in groups["normal"]]
        detected = _detect_content_kind(texts)
        if detected != "normal":
            # Move the whole bucket
            groups.setdefault(detected, []).extend(groups.pop("normal"))

    out = {}
    total_elapsed = 0.0
    model_used = None
    provider_used = None
    kinds_used = []
    total_cost_usd = 0.0
    total_tokens = {"prompt": 0, "completion": 0}

    for kind, lines_in_group in groups.items():
        source_texts = [l["source_text"] for l in lines_in_group]
        result = translate_lines(
            source_texts,
            context=context,
            model=model,
            kind=kind,
            allow_paid_fallback=allow_paid_fallback,
            two_layer=two_layer,
        )
        translations = result["translations"]
        for line, vi in zip(lines_in_group, translations):
            if line.get("line_id"):
                out[line["line_id"]] = vi
        total_elapsed += result.get("elapsed_seconds", 0)
        model_used = result.get("model_used") or model_used
        provider_used = result.get("provider") or provider_used
        total_cost_usd += result.get("cost_usd", 0) or 0
        u = result.get("usage") or {}
        total_tokens["prompt"] += u.get("prompt_tokens", 0) or 0
        total_tokens["completion"] += u.get("completion_tokens", 0) or 0
        kinds_used.append(f"{kind}:{len(lines_in_group)}")

    return {
        "translations_by_line_id": out,
        "stats": {
            "lines": len(non_empty),
            "elapsed_seconds": total_elapsed,
            "model_used": model_used,
            "provider": provider_used,
            "kinds": ",".join(kinds_used),
            "cost_usd": round(total_cost_usd, 6),
            "tokens": total_tokens,
        },
    }


def check_translation_quality(
    source_zh: str,
    target_vi: str,
) -> list[dict]:
    """Quality heuristics — return list of warnings (each {level, code, msg}).

    Levels: 'error' (must fix), 'warn' (review), 'info' (FYI)
    """
    warnings = []
    src = (source_zh or "").strip()
    tgt = (target_vi or "").strip()

    if not src:
        return warnings  # empty source — no check

    if not tgt:
        warnings.append({
            "level": "error",
            "code": "empty_translation",
            "msg": "Nguồn có chữ nhưng bản dịch rỗng",
        })
        return warnings

    # 1. Untranslated CJK chars in output (Vietnamese should rarely have CJK)
    import re
    cjk_in_target = re.findall(r"[一-鿿]", tgt)
    if len(cjk_in_target) > 3:
        # Allow 3 chars for proper noun / quote (e.g. 《易经》)
        warnings.append({
            "level": "warn",
            "code": "cjk_remainder",
            "msg": f"Bản dịch còn {len(cjk_in_target)} ký tự Hán chưa được Việt hoá",
        })

    # 2. Translation identical to source (model returned source verbatim)
    if tgt == src:
        warnings.append({
            "level": "error",
            "code": "identical_to_source",
            "msg": "Bản dịch trùng nguồn — chưa dịch",
        })

    # 3. Length ratio sanity (Vietnamese typically 1.5-3x length of Chinese)
    if len(src) >= 5:
        ratio = len(tgt) / max(len(src), 1)
        if ratio < 0.5:
            warnings.append({
                "level": "warn",
                "code": "too_short",
                "msg": f"Bản dịch quá ngắn so với nguồn (ratio={ratio:.2f}, expect ≥0.8)",
            })
        elif ratio > 6:
            warnings.append({
                "level": "warn",
                "code": "too_long",
                "msg": f"Bản dịch quá dài (ratio={ratio:.2f}, có thể hallucinate)",
            })

    # 4. Output contains noise/refusal markers
    refusal_markers = [
        "I cannot", "I can't", "I'm unable", "không thể dịch",
        "Sorry", "as an AI", "I am an AI",
    ]
    for marker in refusal_markers:
        if marker.lower() in tgt.lower():
            warnings.append({
                "level": "error",
                "code": "refusal",
                "msg": f"Bản dịch chứa từ chối/lỗi model ('{marker}')",
            })
            break

    return warnings


def check_page_quality(
    lines_with_translation: list[dict],
) -> dict:
    """Aggregate quality check across page lines.

    Args:
        lines_with_translation: list of dicts with 'line_id', 'source_text', 'text_vi'

    Returns: dict with per-line warnings + summary
    """
    per_line = []
    error_count = 0
    warn_count = 0

    for item in lines_with_translation:
        warnings = check_translation_quality(
            item.get("source_text", ""),
            item.get("text_vi", ""),
        )
        if warnings:
            per_line.append({
                "line_id": item.get("line_id"),
                "source_preview": (item.get("source_text", "") or "")[:40],
                "target_preview": (item.get("text_vi", "") or "")[:60],
                "warnings": warnings,
            })
            for w in warnings:
                if w["level"] == "error":
                    error_count += 1
                elif w["level"] == "warn":
                    warn_count += 1

    return {
        "total_lines": len(lines_with_translation),
        "lines_with_issues": len(per_line),
        "error_count": error_count,
        "warn_count": warn_count,
        "issues": per_line,
        "fit_score": round(
            100 * (1 - len(per_line) / max(len(lines_with_translation), 1)),
            1,
        ),
    }


def translate_region(region: dict, context: str = "") -> dict:
    """Translate all lines in a region.

    region: dict with 'lines' list (each having 'source_text', 'line_id')

    Returns dict mapping line_id → translation
    """
    lines = region.get("lines", [])
    if not lines:
        return {"translations_by_line_id": {}, "stats": {"lines": 0}}

    source_texts = [l.get("source_text", "") for l in lines]
    # Skip empty lines
    non_empty_indices = [i for i, t in enumerate(source_texts) if t.strip()]
    non_empty_texts = [source_texts[i] for i in non_empty_indices]

    if not non_empty_texts:
        return {"translations_by_line_id": {}, "stats": {"lines": 0}}

    result = translate_lines(non_empty_texts, context=context)
    translations = result["translations"]

    # Map back to line_ids
    out = {}
    for idx, vi in zip(non_empty_indices, translations):
        line = lines[idx]
        line_id = line.get("line_id")
        if line_id:
            out[line_id] = vi

    return {
        "translations_by_line_id": out,
        "stats": {
            "lines": len(non_empty_texts),
            "elapsed_seconds": result["elapsed_seconds"],
            "model_used": result["model_used"],
        },
    }
