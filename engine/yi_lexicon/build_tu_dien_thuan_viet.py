# -*- coding: utf-8 -*-
"""Builder TỪ ĐIỂN thuần-Việt CÓ NEO — PHA B.

Đọc engine/yi_lexicon/_vocab_canon.json (NEO ground-truth) + _thuan_viet_mapping.py
(bản DERIVE thuần-Việt giữ đủ nét) → ghi engine/yi_lexicon/tu_dien_thuan_viet.json.

Mỗi entry trong tu_dien:
  {
    han, han_viet, loai,
    dinh_nghia_canon,   # nguyên văn canon (ground-truth)
    net_canon[],        # các NÉT tách từ canon
    thuan_viet,         # câu đời thường GIỮ ĐỦ net_canon (không rơi/không bịa)
    nguon,              # concept_dict page / wiki passage id (lấy từ canon)
    can_review          # True nếu thiếu nguồn HOẶC chưa có bản thuần-Việt derive
  }

NGUYÊN TẮC NEO: thuan_viet PHẢI derive từ dinh_nghia_canon, giữ đủ nét. Term nào
chưa có trong _thuan_viet_mapping → can_review=True (net_canon tách thô theo dấu phẩy,
thuan_viet để rỗng chờ Anh duyệt) — KHÔNG bịa.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANON_PATH = HERE / "_vocab_canon.json"
OUT_PATH = HERE / "tu_dien_thuan_viet.json"


def _derive_nguon(term: dict) -> str | None:
    """Nguồn = canon_nguon (đã gắn sẵn trong canon). Bổ sung passage_id nếu có.

    KHÔNG bịa nguồn — chỉ lấy cái canon đã neo.
    """
    parts: list[str] = []
    cn = (term.get("canon_nguon") or "").strip()
    if cn:
        parts.append(cn)
    # đính kèm passage_id thật (nếu có) để truy ngược raw_text gốc sách
    pids = [str(p["passage_id"]) for p in (term.get("passages_trich") or []) if p.get("passage_id") is not None]
    if pids:
        parts.append("passages:" + ",".join(pids[:5]))
    return " | ".join(parts) if parts else None


def _split_raw_nets(dinh_nghia: str) -> list[str]:
    """Tách thô nét theo dấu phẩy/chấm phẩy — fallback cho term chưa được derive tay."""
    body = dinh_nghia.strip()
    # bỏ tiền tố mô tả loại sao thường gặp để lấy phần nét
    body = re.sub(r"^(Sao|Một sao|Một hung tinh|Sao hung|Sao ác|Sao hóa|Sao sát tinh|Chỉ|Trạng thái)\b[^,]*?(chủ về|chủ|:)\s*", "", body)
    raw = re.split(r"[,;]", body)
    return [r.strip().rstrip(".") for r in raw if r.strip().rstrip(".")]


def build() -> dict:
    canon = json.loads(CANON_PATH.read_text(encoding="utf-8"))
    # import mapping (tránh lỗi nếu chạy như script vs module)
    try:
        from engine.yi_lexicon._thuan_viet_mapping import MAP
    except ModuleNotFoundError:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "_thuan_viet_mapping", HERE / "_thuan_viet_mapping.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        MAP = mod.MAP

    tu_dien: dict[str, dict] = {}
    n_review = 0

    for t in canon["terms"]:
        name = t["han_viet"]
        nguon = _derive_nguon(t)
        mapped = MAP.get(name)

        if mapped:
            net_canon = list(mapped["net_canon"])
            thuan_viet = mapped["thuan_viet"]
            # can_review chỉ True nếu KHÔNG có nguồn (bản dịch đã có người derive)
            can_review = nguon is None
        else:
            net_canon = _split_raw_nets(t["dinh_nghia_canon"])
            thuan_viet = ""  # chưa derive → KHÔNG bịa
            can_review = True  # cần Anh duyệt bản thuần-Việt

        if can_review:
            n_review += 1

        entry = {
            "han": t.get("han"),
            "han_viet": name,
            "loai": t.get("loai"),
            "dinh_nghia_canon": t["dinh_nghia_canon"],
            "net_canon": net_canon,
            "thuan_viet": thuan_viet,
            "nguon": nguon,
            "can_review": can_review,
        }
        # last-write-wins theo thứ tự canon (các biến thể chữ thường/hoa cùng tên han_viet hiếm)
        tu_dien[name] = entry

    out = {
        "_meta": {
            "ten": "Từ điển thuần-Việt CÓ NEO — sản phẩm tình duyên (gieo duyên + hôn nhân)",
            "muc_dich": (
                "Dịch mọi term user-facing sang tiếng Việt đời thường mà GIỮ ĐỦ NÉT của định nghĩa "
                "canon — chống drift (rơi nét / tự bịa nét). Hạ tầng TÁI DÙNG cho mọi sản phẩm."
            ),
            "cach_dung": (
                "from engine.yi_lexicon.tu_dien_loader import tra_thuan_viet, load_tu_dien; "
                "tra_thuan_viet('Thiên Tướng') → entry. Lấy entry['thuan_viet'] để hiển thị; "
                "entry['net_canon'] để QA giữ đủ nét; entry['nguon'] để truy ngược sách."
            ),
            "nguyen_tac_neo": [
                "thuan_viet DERIVE TỪ dinh_nghia_canon — GIỮ ĐỦ mọi nét trong net_canon, KHÔNG rơi, KHÔNG thêm nét không nguồn.",
                "Mỗi term GẮN nguon (concept_dict page / wiki passage id). KHÔNG bịa nguồn.",
                "Drift đã bắt: Thiên Tướng canon='ấn tín, QUYỀN HÀNH, bảo vệ' (bản cũ rơi 'quyền hành'); "
                "Liêm Trinh canon='THAM VỌNG, sắc đẹp' (bản cũ tự thêm 'giằng xé lý-tình').",
                "Paradigm Iron #4/#6/#8: đọc đồng dạng, mệnh là ĐỘNG TỪ, KHÔNG predict. Gender (chồng/vợ) ở tầng product.",
            ],
            "neo_tu": "engine/yi_lexicon/_vocab_canon.json (dinh_nghia_canon = ground-truth)",
            "ngay_tao": str(date.today()),
        },
        "thong_ke": {
            "tong_term": len(tu_dien),
            "co_thuan_viet": sum(1 for e in tu_dien.values() if e["thuan_viet"]),
            "can_review": n_review,
        },
        "tu_dien": tu_dien,
    }
    return out


def main() -> None:
    out = build()
    OUT_PATH.write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    st = out["thong_ke"]
    print(
        f"WROTE {OUT_PATH} | tong_term={st['tong_term']} "
        f"co_thuan_viet={st['co_thuan_viet']} can_review={st['can_review']}"
    )


if __name__ == "__main__":
    main()
