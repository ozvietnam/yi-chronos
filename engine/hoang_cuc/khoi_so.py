"""KHỞI SỐ (起数) — cơ chế suy quẻ ẩn trong Hoàng Cực Kinh Thế.

KHÔNG phải "bí truyền không giải được": bản 今说 GIẢI rõ (Ngoại Thiên, bộ trọn
dòng 1703-1707, 8935). Năm-quẻ = THÁC BIẾN HÀO LỒNG 4 TẦNG:

    会 → 值卦 (大运)  : 60 quẻ chạy trên vòng Tiên Thiên (复→…→剥), BỎ 4 quẻ
                        thuần 乾坤坎离. 12 hội × 5 值卦 = 60.
    值卦 → 运卦        : đổi LẦN LƯỢT từng hào của 值卦 (sơ→thượng) → 6 运卦.
                        5 值卦 × 6 = 30 vận / hội.
    运卦 → 世卦        : đổi từng hào của 运卦 → 6 世卦, mỗi quẻ chủ 2 thế
                        → 12 thế / vận.
    世卦 → 年卦        : tầng năm (以运经世) — đổi hào tiếp; tầng sâu nhất.

Nguyên lý biến quái (卦变): "一贞八悔" (dòng 8935) — một quái DƯỚI (贞/bản quái)
ghép CẢ TÁM quái TRÊN (悔/biến quái) → 8 quẻ; 8 贞 × 8 悔 = 64.

Thâm ý Thiệu tử: "以四起数" (khởi số bằng bốn, dòng 3763).

Đã KIỂM (test): 复 đổi sơ→thượng = 坤·临·明夷·震·屯·颐 (khớp dòng 1705).
"""
from __future__ import annotations

# 64 quẻ theo thứ tự TIÊN THIÊN (Càn=1 toàn dương … Khôn=64 toàn âm).
XIANTIAN = (
    "乾 夬 大有 大壮 小畜 需 大畜 泰 履 兑 睽 归妹 中孚 节 损 临 同人 革 离 丰 家人 既济 贲 明夷 "
    "无妄 随 噬嗑 震 益 屯 颐 复 姤 大过 鼎 恒 巽 井 蛊 升 讼 困 未济 解 涣 坎 蒙 师 遁 咸 旅 小过 "
    "渐 蹇 艮 谦 否 萃 晋 豫 观 比 剥 坤"
).split()

PURE = {"乾", "坤", "坎", "离"}  # 4 quẻ thuần — bỏ khỏi 60 值卦

# tên Việt (mượn từ nam_que để đồng nhất)
try:
    from engine.hoang_cuc.nam_que import HEX_VI as _HEX_VI
except Exception:  # pragma: no cover
    _HEX_VI = {}
_PURE_VI = {"乾": ("Càn", 1), "坤": ("Khôn", 2), "坎": ("Khảm", 29), "离": ("Ly", 30)}


def bits_of(name: str) -> list[int]:
    """[b1..b6] dưới→trên, dương=1. (value = 63 - chỉ-số-tiên-thiên, b1 = MSB)."""
    val = 63 - XIANTIAN.index(name)
    return [(val >> (5 - i)) & 1 for i in range(6)]


def name_of(bits: list[int]) -> str:
    val = sum(b << (5 - i) for i, b in enumerate(bits))
    return XIANTIAN[64 - val - 1]


def viet_of(name: str) -> str:
    return _HEX_VI.get(name, _PURE_VI.get(name, (name, 0)))[0]


def bien_hao(name: str, hao: int) -> str:
    """Đổi 1 hào (hao: 0=sơ … 5=thượng) của quẻ → quẻ mới (phép 爻变)."""
    if not 0 <= hao <= 5:
        raise ValueError("hao phải trong 0..5 (sơ..thượng)")
    b = bits_of(name)
    b[hao] ^= 1
    return name_of(b)


def sau_bien(name: str) -> list[str]:
    """6 quẻ sinh ra khi đổi lần lượt sơ→thượng (一卦六变).

    Vd sau_bien('复') == ['坤','临','明夷','震','屯','颐'] (khớp chính văn dòng 1705).
    """
    return [bien_hao(name, h) for h in range(6)]


def trinh_hoi(name: str) -> dict:
    """Phân tích 一贞八悔: quái DƯỚI (贞/bản) + quái TRÊN (悔/biến)."""
    b = bits_of(name)
    TRI = {(1, 1, 1): "乾", (1, 1, 0): "兑", (1, 0, 1): "离", (1, 0, 0): "震",
           (0, 1, 1): "巽", (0, 1, 0): "坎", (0, 0, 1): "艮", (0, 0, 0): "坤"}
    return {"que": name, "trinh_ha": TRI[tuple(b[:3])], "hoi_thuong": TRI[tuple(b[3:])]}


# 60 值卦: vòng Tiên Thiên khởi 复 hết 剥 (chính văn dòng 1703), bỏ 4 quẻ thuần.
# Hai cung quanh hai cực: 复(tiên-thiên 32)↓夬(2) [bỏ 离19] → [bỏ cực 乾1] →
#                          姤(33)↑剥(63) [bỏ 坎46] → [bỏ cực 坤64] → về 复.
def chuoi_60_van() -> list[str]:
    seq = []
    for n in range(32, 1, -1):          # cung 1: 复 32 → 夬 2 (giảm)
        nm = XIANTIAN[n - 1]
        if nm not in PURE:
            seq.append(nm)
    for n in range(33, 64):             # cung 2: 姤 33 → 剥 63 (tăng)
        nm = XIANTIAN[n - 1]
        if nm not in PURE:
            seq.append(nm)
    return seq  # 60 quẻ, [0]=复 … [-1]=剥


def co_che() -> dict:
    """Mô tả cơ chế 4 tầng (cho UI / sách)."""
    return {
        "nguyen_ly": "一贞八悔 — 8 quái dưới × 8 quái trên = 64; 爻变 lồng 4 tầng",
        "tang": [
            {"ten": "会 → 值卦 (大运)", "phep": "60 quẻ vòng Tiên Thiên bỏ 乾坤坎离", "so": "12 hội × 5 = 60"},
            {"ten": "值卦 → 运卦", "phep": "đổi sơ→thượng (6 biến)", "so": "5 × 6 = 30 vận/hội"},
            {"ten": "运卦 → 世卦", "phep": "đổi sơ→thượng (6 biến)", "so": "6 quẻ × 2 thế = 12 thế/vận"},
            {"ten": "世卦 → 年卦", "phep": "đổi hào (tầng năm, 以运经世)", "so": "tầng sâu nhất"},
        ],
        "vi_du": {"value": "复", "sau_bien": sau_bien("复")},
        "source": "皇极经世书今说 Ngoại Thiên (dòng 1703-1707, 8935)",
    }
