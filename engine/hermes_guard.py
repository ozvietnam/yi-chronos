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

  + Lằn ranh ĐẠO ĐỨC BRAHMAJĀLA (Iron #9 — Brahmajāla DN 1, Phật xếp bói toán =
    *tà mạng*): chặn/cảnh báo output trượt vào PREDICT lợi-hại đời thường —
    giàu-nghèo · thắng-thua · sống-chết · cờ-bạc/số-đề · ngày-giờ-tốt-xấu-để-
    trục-lợi. YI chỉ MƯỢN khung Duyên Khởi để SOI TÂM, không lừa người bằng dấu
    hiệu. Hằng số DISCLAIMER (Iron #9) gắn vào mọi output sage/sản phẩm.
    Vẫn CONTEXT-AWARE: 'khắc/sinh/sao chủ tử/cờ Tướng/cung Tật Ách' ở ngữ cảnh
    PHÂN TÍCH trung tính KHÔNG bị chặn — chỉ chặn khi có GIỌNG PHÁN-vào-người
    hoặc cầu-lợi-trục-lợi (xem _TA_MANG bên dưới).

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

# Cụm kết-án-hôn-nhân nữ-mệnh thời phong kiến (khắc chồng / sát phu / cô quả /
# khó lấy chồng). LƯU Ý quan trọng (sửa 2026-06-24): các cụm này CŨNG là KHÁI NIỆM
# PHÂN TÍCH trung tính trong Tử Bình ('Thương Quan khắc Quan', 'cấu trúc khắc phu',
# 'khí khắc chồng' = 伤官见官) — KHÔNG được hard-block tuyệt đối, vì sẽ xoá trắng cả
# bước phân tích Thương Quan. Chỉ là VI PHẠM khi ở ngữ cảnh LỜI-PHÁN-VÀO-NGƯỜI:
# có CHỦ NGỮ-NGƯỜI (anh/chị/em/cô/nàng/'số'/'mệnh') + GIỌNG PHÁN (sẽ/chắc chắn/nhất
# định/số…đã định). Vd CẤM: "em sẽ khắc chồng", "số cô là cô quả", "chắc chắn khắc phu".
# Vd CHO QUA (khái niệm phân tích): "Thương Quan khắc Quan", "khí khắc phu cần chế hóa".
# \b cuối mỗi nhánh → tránh khớp nhầm substring (vd 'co qua' trong 'co quan' = cô quân).
_KET_AN_HON = r"(khac chong|sat chong|sat phu|khac phu|co qua|kho lay chong|khong lay duoc chong)\b"
# Dấu hiệu PHÁN đứng TRƯỚC cụm kết án (trong khoảng ngắn) → lời-phán-vào-người.
# Gồm: giọng phán (se/chac chan/…), hoặc chủ-ngữ-người (đại từ), hoặc 'mệnh/số' +
# đại từ ('mệnh em', 'số cô'). KHÔNG gồm 'mệnh' trơ — vì 'nữ mệnh là khí khắc chồng'
# là KHÁI NIỆM PHÂN TÍCH ('nữ mệnh' = domain term), không phải phán-vào-người.
_PHAN_TRUOC = (
    r"((se|chac chan|nhat dinh|the nao cung|kieu gi cung|" + _PRON + r")"
    r"|(menh|so)\s+" + _PRON + r")\b.{0,18}\b"
)
# Dấu hiệu PHÁN đứng SAU cụm kết án (vd "khắc chồng đã định / là cái chắc").
_PHAN_SAU = r"\b.{0,12}(da dinh|la cai chac|khong tranh duoc|chac chan)"

_PREDICT = [
    r"\b(se|chac chan|nhat dinh|the nao cung|kieu gi cung)\s+(giau|ngheo|thanh cong|that bai|chet|ly hon|pha san|trung)",
    r"so (de|lo|xo|danh de)", r"con so may man (la|chinh la)\s*\d", r"danh con\s*\d",
    r"\bse trung\b", r"chac chan (se )?(xay ra|den|toi)",
    r"tuong lai (cua " + _PRON + r"|se la)",
    r"(nam|thang|ngay) \d+ " + _PRON + r" (se|chac)",
    r"menh " + _PRON + r" la\b", r"so " + _PRON + r" (la|da dinh)",
    # Kết-án-hôn-nhân CHỈ khi có chủ-ngữ-người + giọng phán (KHÔNG bắt khái niệm
    # phân tích trung tính như 'Thương Quan khắc Quan' / 'khí khắc phu cần chế hóa').
    _PHAN_TRUOC + _KET_AN_HON,
    _KET_AN_HON + _PHAN_SAU,
    # "(em) sẽ / chắc chắn (không) lấy được chồng" — phán cứng về kết cục hôn nhân.
    r"\b(se|chac chan|nhat dinh) (khong )?(lay duoc|lay) chong\b",
]

# ── LẰN RANH ĐẠO ĐỨC BRAHMAJĀLA (Iron #9, DN 1: bói toán = tà mạng) ───────────
# Mở RỘNG paradigm guard: ngoài giọng tiên-tri chung (_PREDICT), chặn riêng các
# kiểu output trượt vào TÀ MẠNG — dùng dấu hiệu để mưu lợi-hại đời thường:
#   (1) cờ-bạc / số-đề / lô-đề / cá độ — "đánh con X", "số đề/lô", "đánh đề/lô"…
#   (2) ngày-giờ-tốt-xấu để TRỤC LỢI — "ngày đẹp để (đánh đề/cá độ/lô/đánh bạc)"
#   (3) PHÁN sống-chết / tai-hoạ vào người — "anh/cô … (sẽ) chết/tai nạn/mất mạng"
#   (4) PHÁN giàu-nghèo / thắng-thua như KẾT CỤC chắc chắn vào người.
# CONTEXT-AWARE: KHÔNG bắt khái niệm phân tích trung tính ('sao chủ về tử' = mô tả
# tính sao, 'cung Tật Ách chủ sức khoẻ' = domain, 'chọn ngày tốt khởi sự' chung
# chung KHÔNG trục-lợi). Chỉ chặn khi có (a) ngữ cờ-bạc/số-đề rõ, hoặc (b) chủ-ngữ
# người + giọng phán bám vào sống-chết/tai-hoạ/được-mất tiền-bạc.
_GAMBLE = r"(so de|so lo|danh de|danh lo|choi de|choi lo|lo de|ca do|ca cuoc|danh bac|" \
          r"de ve|lo ve|con (lo|de)|so danh de|danh con\s*\d|con so\s*\d)"
# ngày-giờ tốt/đẹp + ý đồ trục-lợi cờ bạc trong khoảng ngắn → tà mạng
_NGAY_TRUC_LOI = (
    r"(ngay|gio|hom)\s+(tot|dep|hop|nao)\b.{0,30}\b("
    + _GAMBLE + r"|danh bac|ca do|ca cuoc|trung)"
)
# phán SỐNG-CHẾT / TAI-HOẠ vào người: giọng phán/đại từ + (chet/tai nan/mất mạng/
# tai hoa/tai uong/yeu menh/đoản thọ/mệnh chung)
_HOA_TU = r"(chet|tai nan|mat mang|tai hoa|tai uong|yeu menh|doan tho|menh chung|tu vong|chet yeu)\b"
_HOA_PHAN = (
    r"((se|chac chan|nhat dinh|the nao cung|kieu gi cung)\b.{0,18}\b" + _HOA_TU
    + r"|" + _PRON + r"\b.{0,12}\b(se|chac chan|nhat dinh)\b.{0,10}\b" + _HOA_TU + r")"
)
_TA_MANG = [
    _GAMBLE,            # mọi tham chiếu cờ-bạc/số-đề trong OUTPUT sage = tà mạng
    _NGAY_TRUC_LOI,     # bày ngày-giờ để cờ bạc / trục lợi
    _HOA_PHAN,          # phán sống-chết / tai-hoạ vào người
]

# ── DISCLAIMER chuẩn (Iron #9) — gắn vào MỌI output sage / sản phẩm ───────────
DISCLAIMER = (
    "Tử Vi MƯỢN khung chẩn-nhân-dứt-đạo của nhà Phật để soi tâm — "
    "KHÔNG phải giáo lý Phật giáo chính thống; lá số không thay tu học hay y tế."
)

# \b hai đầu → tránh khớp nhầm substring (vd "hao" trong "chao em")
_DOMAIN_RX = [re.compile(r"\b" + re.escape(k) + r"\b") for k in _DOMAIN]
_OUT_RX = [re.compile(p) for p in _OUT_OF_SCOPE]
_PREDICT_RX = [re.compile(p) for p in _PREDICT]
_TA_MANG_RX = [re.compile(p) for p in _TA_MANG]


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
    """Trả danh sách cụm vi phạm trong câu trả lời (rỗng = sạch).

    Gộp 2 lằn ranh:
      • giọng TIÊN TRI (_PREDICT — Iron #4/#6/#8)
      • TÀ MẠNG Brahmajāla (_TA_MANG — Iron #9): cờ-bạc/số-đề · ngày-giờ trục-lợi ·
        phán sống-chết/tai-hoạ vào người.
    """
    a = _norm(answer)
    hits = [rx.pattern for rx in _PREDICT_RX if rx.search(a)]
    hits += [rx.pattern for rx in _TA_MANG_RX if rx.search(a)]
    return hits


def is_predictive(answer: str) -> bool:
    return bool(paradigm_violations(answer))


def ta_mang_violations(answer: str) -> list[str]:
    """Chỉ riêng lằn ranh TÀ MẠNG Brahmajāla (Iron #9) — dùng khi cần phân biệt
    nguyên nhân chặn (cờ-bạc/số-đề/sống-chết) với giọng-tiên-tri thường."""
    a = _norm(answer)
    return [rx.pattern for rx in _TA_MANG_RX if rx.search(a)]


def is_ta_mang(answer: str) -> bool:
    return bool(ta_mang_violations(answer))


def with_disclaimer(text: str, *, sep: str = "\n\n") -> str:
    """Gắn DISCLAIMER (Iron #9) vào cuối output sage/sản phẩm nếu chưa có.
    Idempotent — gọi nhiều lần không nhân đôi disclaimer."""
    body = text or ""
    if _norm(DISCLAIMER)[:40] in _norm(body):
        return body
    return (body.rstrip() + sep + DISCLAIMER) if body.strip() else DISCLAIMER
