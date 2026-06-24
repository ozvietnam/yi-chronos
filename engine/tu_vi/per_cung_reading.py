"""Luận TỪNG CUNG theo SAO (deterministic, free) — yêu cầu AppChat #2 (2026-06-24).

App than: mỗi cung chỉ ghi định nghĩa CHUNG của cung, KHÔNG nhắc sao đang tọa thủ → "nông".
Đây trả: mỗi cung kèm chính tinh thực tế + nghĩa sao (concept_dict Q1) + câu luận-theo-sao 2-3 dòng.
Đọc đồng dạng — phản chiếu cấu trúc, không predict. Bản LLM văn xuôi sâu = trả phí (#3 deep-cung).
"""
from __future__ import annotations


def per_cung_star_reading(ls: dict) -> list[dict]:
    """ls = cast_la_so(_from_birth). Trả list 12 cung: {cung, chi, chinh_tinh:[{sao,nghia}], phu_tinh, luan_sao}."""
    from engine.tu_vi import concept_dict
    chinh = ls.get("chinh_tinh") or {}
    phu = {**(ls.get("phu_tinh") or {}), **(ls.get("sat_tinh") or {})}

    def _nghia(s: str) -> str:
        try:
            return (concept_dict.lookup(s) or {}).get("definition") or ""
        except Exception:
            return ""

    out: list[dict] = []
    for p in (ls.get("palaces") or []):
        idx = p.get("branch_index")
        if idx is None:
            continue
        ct = [s for s, i in chinh.items() if i % 12 == idx % 12]
        pt = [s for s, i in phu.items() if i % 12 == idx % 12]
        sao_nghia = [{"sao": s, "nghia": _nghia(s)[:170]} for s in ct]
        name = p.get("name")
        if ct:
            body = " ".join(sn["nghia"] for sn in sao_nghia if sn["nghia"])
            kem = f" (kèm {', '.join(pt)})" if pt else ""
            luan = f"{name} có {', '.join(ct)}{kem}." + (f" {body}" if body else "")
        else:
            kem = f", có {', '.join(pt)}" if pt else ""
            luan = f"{name} vô chính diệu{kem} — mượn sao cung xung chiếu để luận."
        out.append({"cung": name, "chi": p.get("branch"),
                    "chinh_tinh": sao_nghia, "phu_tinh": pt, "luan_sao": luan.strip()})
    return out
