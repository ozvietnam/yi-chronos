"""6 mức Cát-Hung trong Chu Dịch (Cao Hạnh - Kinh dịch cổ kinh kim chú).

Paradigm Thiệu Vĩ Hoa p61-62: KHÔNG chỉ có "cát" và "hung" — có 6 cấp độ:
Cát → Lận → Lệ → Hối → Cữu → Hung.

Engine LLM phê mệnh nên dùng 6 mức này, không gộp chung.
"""
from __future__ import annotations

SAU_MUC = {
    "Cát": {
        "cap": 1,
        "nghia": "Phúc tường (tốt lành), thiện, việc có kết quả thiện",
        "sub": {
            "Sơ Cát": "Cát giai đoạn đầu",
            "Trung Cát": "Cát giai đoạn giữa",
            "Chung Cát": "Cát giai đoạn cuối",
            "Đại Cát": "Phúc tường rất to",
            "Nguyên Cát": "Đại cát + nguồn",
            "Trinh Cát": "Chiêm cát, được quẻ đoán cát",
        },
    },
    "Lận": {
        "cap": 2,
        "nghia": "Khó khăn, gian nan (mượn chữ 'lân')",
        "sub": {
            "Tiểu Lận": "Gặp tiểu nhân hoặc sự việc khó khăn",
            "Chung Lận": "Cuối cùng khó khăn",
            "Trinh Lận": "Quẻ bói gặp khó khăn",
        },
    },
    "Lệ": {
        "cap": 3,
        "nghia": "Nguy, nguy hiểm",
        "sub": {
            "Hữu Lệ": "Có nguy hiểm",
            "Trinh Lệ": "Việc trong quẻ có nguy hiểm",
        },
    },
    "Hối": {
        "cap": 4,
        "nghia": "Thế khó khăn, quẫn bức, lo lắng",
        "sub": {
            "Hữu Hối": "Thế khó khăn",
            "Hối Hữu Hối": "Khó khăn dẫn đến khó khăn",
            "Vô Hối": "Không khó khăn",
            "Hối Vong": "Trước đây có hối, nay mất",
        },
    },
    "Cữu": {
        "cap": 5,
        "nghia": "Tai hoạn nhẹ (nặng hơn Hối, nhẹ hơn Hung)",
        "sub": {
            "Vi Cữu": "Sẽ thành tai hoạn",
            "Phi Cữu": "Không có tai hoạn",
            "Hà Cữu": "Không đến nỗi tai hoạn",
            "Vô Cữu": "Không có tai hoạn",
        },
    },
    "Hung": {
        "cap": 6,
        "nghia": "Tai họa lớn, ác, kết quả hung",
        "sub": {
            "Chung Hung": "Kết quả cuối cùng là hung",
            "Hữu Hung": "Có tai ương",
            "Trinh Hung": "Quẻ bói này hung",
        },
    },
}

# Color code cho UI (cấp thấp = xanh, cao = đỏ)
COLOR_CODE = {
    "Cát": "#16a34a",   # green
    "Lận": "#2563eb",   # blue
    "Lệ":  "#ea580c",   # orange
    "Hối": "#eab308",   # yellow
    "Cữu": "#db2777",   # pink
    "Hung":"#dc2626",   # red
}


def get_muc(name: str) -> dict | None:
    return SAU_MUC.get(name)


def get_color(name: str) -> str:
    return COLOR_CODE.get(name, "#666666")


def compare_muc(a: str, b: str) -> int:
    """So sánh 2 mức (return cấp a - cấp b). Âm = a nhẹ hơn."""
    ca = SAU_MUC.get(a, {}).get("cap", 0)
    cb = SAU_MUC.get(b, {}).get("cap", 0)
    return ca - cb


__all__ = ["SAU_MUC", "COLOR_CODE", "get_muc", "get_color", "compare_muc"]
