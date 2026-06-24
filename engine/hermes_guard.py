"""H6.0 — Rào phạm vi (Socratic) + post-filter paradigm cho Hermes đa-user.

Hai cổng mọi lượt chat phải qua:

  1. classify_scope(question)  — TRƯỚC khi gọi LLM/council:
       • in_scope  : hỏi mệnh-lý / khái niệm Đông-phương-học về chính lá số user.
       • out_scope : nhờ "làm hộ" (code, bài tập, viết luận/email, dịch, toán…) hoặc
                     ngoài miền → từ chối lịch sự, KHÔNG làm bài tập hộ khách.
       • needs_focus: chưa rõ "việc" → buộc vòng "nghĩ–nói–phản tỉnh" (Socratic):
                     hỏi user nêu rõ việc cần soi trước khi gợi mở.

  2. paradigm_violations(answer) — SAU khi LLM trả lời:
       bắt giọng TIÊN TRI ("sẽ giàu/nghèo", "chắc chắn xảy ra", số đề…) → reject/
       regenerate. Mệnh là ĐỘNG TỪ (Iron #8): soi tính → gợi cách vận hành, KHÔNG phán.

Thuần logic — không LLM, không DB, không phụ thuộc máy local. Test 100%.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# ── chuẩn hoá: bỏ dấu + lower để match bền (user gõ thiếu dấu) ────────────────

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # bỏ dấu
    return s.lower().replace("đ", "d")


# ── từ vựng miền (Đông-phương-học) — câu hỏi hợp lệ thường chạm ───────────────
_DOMAIN = [
    "la so", "tu vi", "bat tu", "tu tru", "que", "hao", "luc hao", "kinh dich",
    "mai hoa", "ha lac", "hoang cuc", "thiet ban", "ky mon", "than so",
    "menh", "than", "cung", "sao", "dai van", "luu nien", "ngu hanh", "am duong",
    "can chi", "thien can", "dia chi", "nap am", "dung than", "cach cuc",
    "duyen", "hop tuoi", "hop hon", "ngay tot", "xem ngay", "chiem", "boi",
    "sinh khac", "thap than", "tuong", "van menh", "cat hung", "thai tue",
]

# ── nhờ LÀM HỘ / ngoài miền → từ chối (không làm bài tập hộ khách) ────────────
_OUT_OF_SCOPE = [
    r"\bcode\b", r"\blap trinh\b", r"\bpython\b", r"\bjavascript\b",
    r"\blam (ho|giup|gium) .{0,20}\b(bai|bai tap|code|ham|chuong trinh|de|toan)\b",
    r"\blam (bai|bai tap)\b", r"\bgiai (bai|toan|phuong trinh|de)\b",
    r"\bviet\b.{0,25}\b(bai luan|luan van|email|thu xin|don xin|cv|ke hoach|content|bai van|bai tho|kich ban|code|ham)\b",
    r"\b(bai luan|luan van)\b",
    r"\bdich\b.{0,15}\b(ho|giup|gium|doan|cau|sang tieng|tieng anh|tieng trung)\b",
    r"\btom tat\b.{0,15}\b(bai|van ban|tai lieu)\b",
    r"\bcong thuc (toan|hoa|ly|nau)\b", r"\bthu do (cua|nuoc)\b", r"\bnau an\b",
    r"\bsoan (ho|giup|gium)\b",
]

# ── giọng TIÊN TRI (cấm — vi phạm paradigm đọc-đồng-dạng) ─────────────────────
# Đại từ ngôi-2 bao cả nữ-mệnh (em/chị) — narration tình duyên xưng "em/chị",
# pattern cũ chỉ có anh/chị/ban → trượt biến thể "mệnh em là", "số em đã định".
_PRON = r"(anh|chi|em|ban|co|nang)"
_PREDICT = [
    r"\b(se|chac chan|nhat dinh|the nao cung|kieu gi cung)\s+(giau|ngheo|thanh cong|that bai|chet|ly hon|pha san|trung)",
    r"so (de|lo|xo|danh de)", r"con so may man (la|chinh la)\s*\d", r"danh con\s*\d",
    r"\bse trung\b", r"chac chan (se )?(xay ra|den|toi)",
    r"tuong lai (cua " + _PRON + r"|se la)",
    r"(nam|thang|ngay) \d+ " + _PRON + r" (se|chac)",
    r"menh " + _PRON + r" la\b", r"so " + _PRON + r" (la|da dinh)",
    # forbidden-verdicts định mệnh (đồng bộ với tinh_duyen.reading._FORBIDDEN_VERDICTS):
    # các lời kết án nữ-mệnh thời phong kiến — cấm narration sinh ra mới.
    r"\bkhac chong\b", r"\bsat chong\b", r"\bsat phu\b", r"\bkhac phu\b",
    r"\bco qua\b", r"\bso co qua\b", r"\bkho lay chong\b", r"\bkhong lay duoc chong\b",
    r"\b(se|chac chan|nhat dinh) (khong )?(lay duoc|lay) chong\b",
]

# \b hai đầu → tránh khớp nhầm substring (vd "hao" trong "chao em")
_DOMAIN_RX = [re.compile(r"\b" + re.escape(k) + r"\b") for k in _DOMAIN]
_OUT_RX = [re.compile(p) for p in _OUT_OF_SCOPE]
_PREDICT_RX = [re.compile(p) for p in _PREDICT]


@dataclass
class ScopeVerdict:
    verdict: str          # "in_scope" | "out_of_scope" | "needs_focus"
    reason: str
    reply: str = ""       # câu trả lời gợi ý khi từ chối / cần làm rõ


# câu mời "nghĩ–nói–phản tỉnh" khi chưa rõ việc (Socratic)
_FOCUS_REPLY = (
    "Em là người đồng hành soi mệnh-lý, không phán thay anh. Anh cho em biết rõ "
    "*việc* anh đang muốn soi (vd: hướng nghề, một quyết định, một mối quan hệ) — "
    "và anh đang nghĩ gì về nó — để em đọc lá số cùng anh nhé."
)
_OUT_REPLY = (
    "Việc này nằm ngoài phạm vi của em — em chỉ đồng hành soi mệnh-lý từ lá số của anh "
    "(Tử Vi, Bát Tự, Kinh Dịch, Thần số…), không làm bài/viết hộ. Anh muốn soi điều gì "
    "về lá số của mình không?"
)


def classify_scope(question: str, *, min_len: int = 8) -> ScopeVerdict:
    """Phân loại câu hỏi TRƯỚC khi tốn LLM."""
    q = _norm(question)
    # 1) nhờ làm hộ / ngoài miền → từ chối (ưu tiên cao nhất)
    for rx in _OUT_RX:
        if rx.search(q):
            return ScopeVerdict("out_of_scope", f"match out-of-scope: {rx.pattern}", _OUT_REPLY)
    # 2) có chạm từ vựng mệnh-lý → hợp lệ
    if any(rx.search(q) for rx in _DOMAIN_RX):
        return ScopeVerdict("in_scope", "domain term present")
    # 3) quá ngắn / chung chung → mời nêu rõ việc (Socratic)
    if len(q.strip()) < min_len:
        return ScopeVerdict("needs_focus", "too short / vague", _FOCUS_REPLY)
    # 4) không tín hiệu miền rõ → cũng mời làm rõ thay vì đoán bừa
    return ScopeVerdict("needs_focus", "no domain signal", _FOCUS_REPLY)


def paradigm_violations(answer: str) -> list[str]:
    """Trả danh sách cụm vi phạm giọng tiên tri trong câu trả lời (rỗng = sạch)."""
    a = _norm(answer)
    return [rx.pattern for rx in _PREDICT_RX if rx.search(a)]


def is_predictive(answer: str) -> bool:
    return bool(paradigm_violations(answer))
