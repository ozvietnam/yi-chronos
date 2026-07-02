"""#55 — Hợp nhất SONG PHÁI Bát Tự (THỂ 體) ↔ Tử Vi (DỤNG 用): hôn nhân/gia đình.

Bát Tự = THỂ (năng lượng ngũ hành/thập thần, tiên thiên, "bạn LÀ AI").
Tử Vi  = DỤNG (tinh diệu × 12 cung, hậu thiên, "bạn VẬN HÀNH/ TRẢI QUA điều gì").
Cao thủ THAM ĐOÁN (参断): đồng-tham (cùng hướng → tin cao) vs dị-tham (lệch → giữ CẢ
HAI, thận trọng — kept_all, Iron #3). Mệnh là ĐỘNG TỪ (Iron #8); đọc đồng dạng KHÔNG
predict (Iron #4/#6) — mọi prose qua `hermes_guard.paradigm_violations`.

v1 (2026-07-02, "đổ thịt"): mỗi khía cạnh trích TÍN HIỆU RIÊNG từ output thật của
2 engine con — Bát Tự `analyze_hon_nhan` (cung_phoi/partner_star/special_stars/
timing_suggestions) + Tử Vi `chiem_phu_the_v4` (56 quy luật Trung Châu có trích trang,
lưu niên markers, cross-bind Phúc Đức, panorama) + lá số (sao theo cung) + thập thần.
Thiếu tín hiệu riêng → degrade về hướng TỔNG của engine (v0); vẫn trống → câu
quote-or-silence NGƯỜI-ĐỌC-ĐƯỢC (không lộ ghi chú dev, không bịa — Iron feedback
`quote-or-silence`). Concord tính THEO TỪNG khía cạnh (hết cảnh 12 ô cùng 1 nhãn).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any, Callable, Optional

from engine.cross_paradigm._common import (  # primitive liên-phái dùng chung
    CONCORD_DI, CONCORD_DONG, CONCORD_MOT,
    concord as _concord, norm as _norm, reframe_check as _reframe_check,
)

# Engine con — import ở module level để test monkeypatch được (spec: "mock engine con").
from engine.bat_tu.hon_nhan import analyze_hon_nhan
from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4

# Ma trận 12 khía cạnh (issue #55). lead = phái DẪN luận chính; phái kia cross-check.
ASPECTS: list[dict] = [
    {"id": 1,  "ten": "Tính cách/khí chất phối ngẫu",          "lead": "tu_vi"},
    {"id": 2,  "ten": "Chất lượng hôn nhân tổng thể",          "lead": "tu_vi"},
    {"id": 3,  "ten": "Ứng kỳ (khoảng kích hoạt quan hệ)",     "lead": "tu_vi"},
    {"id": 4,  "ten": "Năng lượng tương tác hợp/khắc",         "lead": "bat_tu"},
    {"id": 5,  "ten": "'Cao thấp'/lực của Thê tinh",           "lead": "bat_tu"},
    {"id": 6,  "ten": "Hợp đôi (hai người)",                   "lead": "bat_tu"},
    {"id": 7,  "ten": "Điểm căng quan hệ (xa cách/biến động)", "lead": "tu_vi"},
    {"id": 8,  "ten": "Con cái — cách nuôi dưỡng/truyền tính", "lead": "tu_vi"},
    {"id": 9,  "ten": "Cha mẹ / anh chị em",                   "lead": "bat_tu"},
    {"id": 10, "ten": "Tâm lý/EQ hôn nhân (khí số)",           "lead": "tu_vi"},
    {"id": 11, "ten": "Tài sản chung / kinh tế gia đình",      "lead": "bat_tu"},
    {"id": 12, "ten": "Định khắc giờ sinh (định bàn)",         "lead": "tu_vi"},
]

# Câu quote-or-silence NGƯỜI ĐỌC ĐƯỢC (thay dev-note "(unsourced — chưa wiring...)")
FALLBACK_USER = ("Lá của bạn không kích hoạt tín hiệu riêng cho khía cạnh này — "
                 "hệ chỉ luận khi có nguồn, không suy đoán thêm.")

SRC_TRUNG_CHAU = ("Tử Vi Bắc phái Trung Châu (Vương Đình Chỉ) — bộ 56 quy luật chiêm "
                  "Phu Thê v4; trích trang ghi ngay trong từng luận điểm")
SRC_NUA_KIA = ("Kho chân dung chính tinh cung Phu Thê (YI tổng hợp Toàn Thư + Trung "
               "Châu — dùng chung món Duyên)")


# ── hướng TỔNG mỗi engine (fallback khi khía cạnh không có tín hiệu riêng) ───────
_BT_NEG = ("cang", "xung", "khac", "hung", "ky", "hao", "pha", "yeu", "tan", "kiep")
_BT_POS = ("thuan", "tot", "cat", "on", "vuong", "manh", "dep", "hop", "vien")


def _dir_bat_tu(out: Optional[dict]) -> Optional[str]:
    if not out:
        return None
    label = _norm(str((out.get("overall") or {}).get("label", "")))
    if any(k in label for k in _BT_NEG):
        return "cang"
    if any(k in label for k in _BT_POS):
        return "thuan"
    if out.get("warnings"):
        return "cang"
    return "thuan" if out.get("overall") else None


def _dir_tu_vi(out: Optional[dict]) -> Optional[str]:
    if not out:
        return None
    # Bất kỳ rule Q* nào "hit" (vd Hóa Kỵ/Sát/Tuần Triệt ở Phu Thê) → điểm căng.
    if any(isinstance(v, dict) and v.get("hit") for v in out.values()):
        return "cang"
    return "thuan" if out else None


def _reading_bat_tu(out: Optional[dict]) -> str:
    if not out:
        return ""
    ov = (out.get("overall") or {}).get("narrative")
    cp = (out.get("cung_phoi") or {}).get("trait_narrative")
    return str(ov or cp or "")


def _reading_tu_vi(out: Optional[dict]) -> str:
    if not out:
        return ""
    if out.get("phu_the_tong_quan"):
        return str(out["phu_the_tong_quan"])
    notes = [v.get("note") for v in out.values() if isinstance(v, dict) and v.get("note")]
    return " · ".join(str(n) for n in notes if n)


def _sources_of(out: Optional[dict], school: str) -> list[str]:
    if not out:
        return []
    if school == "bat_tu" and out.get("source_ref"):
        return [str(out["source_ref"])]
    src = out.get("sources") or out.get("source_ref")
    return [str(src)] if src else []


def _read_dir_src(out, school):
    if school == "bat_tu":
        return _reading_bat_tu(out), _dir_bat_tu(out), _sources_of(out, "bat_tu")
    return _reading_tu_vi(out), _dir_tu_vi(out), _sources_of(out, "tu_vi")


# ── helpers wiring per-khía-cạnh ─────────────────────────────────────────────────

def _g(d: Any, *path, default=None):
    """Getter an toàn xuyên dict lồng nhau — engine con thiếu field không được gây sập."""
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def _slug(star: str) -> str:
    s = unicodedata.normalize("NFD", star or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower().replace("đ", "d").strip().replace(" ", "_")


def _nua_kia(star: str) -> str:
    """Chân dung chính tinh (kho NUA_KIA của món Duyên — tái dùng Iron #1)."""
    try:
        from engine.tu_vi.duyen import NUA_KIA
        return NUA_KIA.get(_slug(star), "")
    except Exception:  # noqa: BLE001 — kho thiếu không được sập
        return ""


def _stars_at_palace(la_so: dict, palace_name: str) -> list[str]:
    """Sao (chính + phụ + sát) đóng tại 1 cung, từ map sao→branch_index của lá số."""
    idx = None
    for p in (la_so or {}).get("palaces") or []:
        if isinstance(p, dict) and p.get("name") == palace_name:
            idx = p.get("branch_index")
            break
    if idx is None:
        return []
    stars: list[str] = []
    for key in ("chinh_tinh", "phu_tinh", "sat_tinh"):
        m = la_so.get(key)
        if isinstance(m, dict):
            stars += [s for s, i in m.items() if i == idx]
    return stars


def _age_now(bat_tu_state: dict) -> Optional[int]:
    try:
        birth = datetime.fromisoformat(str(bat_tu_state.get("birth_datetime_local")))
        return datetime.now().year - birth.year + 1  # tuổi mụ (khớp đại vận an sao)
    except Exception:  # noqa: BLE001
        return None


def _join(parts: list) -> str:
    return " · ".join(str(p).strip() for p in parts if p and str(p).strip())


def _phoi_label(gender: Optional[str]) -> str:
    g = _norm(str(gender or ""))
    if g in ("nu", "nữ", "female", "f"):
        return "chồng"
    if g in ("nam", "male", "m"):
        return "vợ"
    return "bạn đời"


# ── builders per-khía-cạnh: trả (lead_reading, lead_dir, cross_reading, cross_dir,
#    extra_sources). Field nào None → dùng fallback tổng của engine tương ứng. ──────

def _asp1_tinh_cach(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    phoi = ctx["phoi"]
    stars = _g(tv, "chinh_tinh", default=[]) or []
    parts = []
    if stars:
        parts.append(f"Cung Phu Thê ({_g(tv, 'cung_phu_the', 'branch', default='?')}) "
                     f"tọa {' + '.join(stars)}")
        for s in stars[:2]:
            desc = _nua_kia(s)
            if desc:
                parts.append(f"{s}: {desc}")
    hoa = _g(tv, "quy_luat_v2", "1_tu_hoa_at_chinh_tinh", default={}) or {}
    for h, star in hoa.items():
        parts.append(f"Hóa {h} nhập chính tinh {star} — khí chất {phoi} có thêm sắc {h.lower()}")
    p7 = _g(tv, "quy_luat_v2", "7_thai_duong_thai_am_mieu_ham", "paradigm")
    if p7:
        parts.append(str(p7))
    lead = _join(parts)
    lead_dir = None
    if lead:
        lead_dir = "cang" if (_g(tv, "luc_sat_trong_cung") or _g(tv, "hoa_ki_trong_cung")) else "thuan"

    ps = _g(bt, "partner_star", default={}) or {}
    cparts = []
    if ps.get("main_star"):
        fam = _g(ctx["state"], "thap_than_family_map", ps["main_star"], default="")
        cparts.append(f"Sao {phoi} theo Tứ trụ: {ps['main_star']}"
                      + (f" ({fam})" if fam else "")
                      + (f", phụ {ps['secondary_star']}" if ps.get("secondary_star") else ""))
    tn = _g(bt, "cung_phoi", "trait_narrative")
    if tn:
        cparts.append(str(tn))
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": "thuan" if cross else None,
            "src": [SRC_NUA_KIA, SRC_TRUNG_CHAU] if lead else []}


def _asp2_chat_luong(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    pano = _g(tv, "panorama_hon_nhan", default={}) or {}
    lead = ""
    lead_dir = None
    if pano.get("summary"):
        lead = str(pano["summary"])
        net = pano.get("net")
        if isinstance(net, (int, float)):
            lead_dir = "thuan" if net > 0 else ("cang" if net < 0 else
                       ("thuan" if (pano.get("score_cat") or 0) >= (pano.get("score_hung") or 0)
                        else "cang"))
    ov = _g(bt, "overall", default={}) or {}
    cross = _join([ov.get("narrative"),
                   f"nhãn tổng: {ov.get('label')}" if ov.get("label") else ""])
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": _dir_bat_tu(bt) if cross else None,
            "src": [SRC_TRUNG_CHAU] if lead else []}


def _asp3_ung_ky(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    markers = _g(tv, "quy_luat_v2", "9_luu_nien_markers", default=[]) or []
    cur_year = datetime.now().year
    upcoming = [m for m in markers if isinstance(m, dict) and (m.get("year") or 0) >= cur_year][:3]
    parts = [str(m.get("note") or f"{m.get('year')}: {', '.join(m.get('triggers') or [])}")
             for m in upcoming]
    # đại vận hiện tại (khung 10 năm) từ chain
    age = _age_now(ctx["state"])
    chain = _g(tv, "quy_luat_v2", "8_dai_van_phu_the_chain", default=[]) or []
    if age is not None:
        for w in chain:
            if isinstance(w, dict) and (w.get("start_age") or 0) <= age <= (w.get("end_age") or -1):
                sao = " + ".join(w.get("phu_the_chinh_tinh") or []) or "vô chính diệu"
                parts.insert(0, f"Đại vận hiện tại ({w['start_age']}-{w['end_age']} tuổi): "
                                f"Phu Thê đại vận tại {w.get('phu_the_branch')} — {sao}")
                break
    lead = _join(parts)
    cross = _g(bt, "timing_suggestions", "narrative", default="") or ""
    return {"lead": lead, "lead_dir": "thuan" if upcoming else None,
            "cross": str(cross),
            "cross_dir": "thuan" if _g(bt, "timing_suggestions", "favorable_cycles") else None,
            "src": [SRC_TRUNG_CHAU] if lead else []}


def _asp4_nang_luong(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    cp = _g(bt, "cung_phoi", default={}) or {}
    parts = []
    if cp.get("trait_narrative"):
        parts.append(str(cp["trait_narrative"]))
    tang = cp.get("tang_can") or []
    if tang:
        parts.append("tàng can: " + ", ".join(
            f"{t.get('stem')}={t.get('thap_than')}" for t in tang if isinstance(t, dict)))
    inter = cp.get("interactions_with_other_pillars")
    if isinstance(inter, list):
        parts.append("Cung Phối bị hợp/xung kéo bởi: " + ", ".join(map(str, inter))
                     if inter else "Cung Phối không bị trụ khác hợp/xung kéo — khí phối ổn định")
    lead = _join(parts)
    lead_dir = None
    if lead:
        lead_dir = "cang" if (inter and any("xung" in _norm(str(x)) for x in inter)) else "thuan"

    cparts = []
    p12 = _g(tv, "quy_luat_v3", "12_xuong_khuc_chia_re_cat", default={}) or {}
    if p12.get("detected"):
        cparts.append(str(p12.get("paradigm")))
    ls_cung = _g(tv, "luc_sat_trong_cung", default=None)
    hk = _g(tv, "hoa_ki_trong_cung", default=None)
    if isinstance(ls_cung, list) and isinstance(hk, list):
        if not ls_cung and not hk:
            cparts.append("Cung Phu Thê không bị lục sát / Hóa Kỵ đóng")
        else:
            cparts.append("Trong cung có: " + ", ".join(map(str, ls_cung + hk)))
    cross = _join(cparts)
    cross_dir = None
    if cross:
        cross_dir = "cang" if (ls_cung or hk) else "thuan"
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross, "cross_dir": cross_dir,
            "src": [SRC_TRUNG_CHAU] if cross else []}


def _asp5_luc_phoi_tinh(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    phoi = ctx["phoi"]
    ps = _g(bt, "partner_star", default={}) or {}
    parts = []
    if ps.get("main_star"):
        vis, hid = ps.get("visible_positions") or [], ps.get("hidden_positions") or []
        parts.append(f"Sao {phoi} ({ps['main_star']}) xuất hiện {ps.get('total_count', 0)} chỗ"
                     + (f" — lộ: {', '.join(vis)}" if vis else "")
                     + (f" — tàng: {', '.join(hid)}" if hid else ""))
        if not vis and hid:
            parts.append(f"{ps['main_star']} chỉ TÀNG không LỘ — lực {phoi} kín, "
                         "bền ở tầng sâu nhưng cần thời gian mới hiện rõ")
    lead = _join(parts)
    lead_dir = None
    if ps:
        lead_dir = "thuan" if (ps.get("total_count") or 0) > 0 else "cang"

    p19 = _g(tv, "quy_luat_v3", "19_tu_vi_phu_the_tai_da_co_quan", default={}) or {}
    cross = str(p19.get("paradigm") or "") if p19.get("detected") else ""
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": ("thuan" if p19.get("is_cat") else "cang") if cross else None,
            "src": [SRC_TRUNG_CHAU] if cross else []}


def _asp6_hop_doi(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    phoi = ctx["phoi"]
    cp = _g(bt, "cung_phoi", default={}) or {}
    parts = []
    tang_tt = [t.get("thap_than") for t in (cp.get("tang_can") or []) if isinstance(t, dict)]
    phoi_star = {"chồng": ("Chính Quan", "Thất Sát"), "vợ": ("Chính Tài", "Thiên Tài")}.get(phoi)
    if phoi_star and any(t in phoi_star for t in tang_tt):
        hit = [t for t in tang_tt if t in phoi_star]
        parts.append(f"{'/'.join(hit)} (biểu tượng người {phoi}) tàng ngay TẠI Cung Phối — "
                     f"cấu trúc 'phu tinh về cung', truyền thống Tứ trụ đọc là gắn bó có gốc")
    if cp.get("has_dao_hoa_in_chart") is False and cp.get("dao_hoa_chi"):
        parts.append(f"Đào Hoa ({cp['dao_hoa_chi']}) không nhập tứ trụ — duyên thiên về "
                     "kênh nghiêm túc, ít kiểu say nắng xã giao")
    elif cp.get("has_dao_hoa_in_chart"):
        parts.append("Đào Hoa nhập tứ trụ — sức hút quan hệ rõ, cần bến đỗ minh bạch")
    lead = _join(parts)

    cparts = []
    to_hop = _g(tv, "to_hop_doi")
    if to_hop:
        cparts.append(f"Tổ hợp đôi cung Phu Thê: {str(to_hop).replace('_', ' ')}")
    p12 = _g(tv, "quy_luat_v3", "12_xuong_khuc_chia_re_cat", default={}) or {}
    if p12.get("detected"):
        cparts.append(str(p12.get("paradigm")))
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": "thuan" if lead else None,
            "cross": cross,
            "cross_dir": ("thuan" if p12.get("detected") else None) if cross else None,
            "src": [SRC_TRUNG_CHAU] if cross else []}


def _asp7_diem_cang(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    canh_bao = _g(tv, "panorama_hon_nhan", "all_canh_bao", default=[]) or []
    parts = [str(c) for c in canh_bao]
    # cửa sổ đại vận có cảnh báo (đi TRƯỚC để user chăm quan hệ chủ động — mệnh là động từ)
    age = _age_now(ctx["state"])
    for w in _g(tv, "quy_luat_v2", "8_dai_van_phu_the_chain", default=[]) or []:
        if isinstance(w, dict) and w.get("canh_bao") and (age is None or (w.get("end_age") or 0) >= age):
            parts.append(f"Giai đoạn {w.get('start_age')}-{w.get('end_age')} tuổi: "
                         + "; ".join(map(str, w["canh_bao"]))
                         + " → giai đoạn nên CHỦ ĐỘNG chăm quan hệ, không phó mặc")
    lead = _join(parts)
    lead_dir = ("cang" if canh_bao else ("thuan" if _g(tv, "panorama_hon_nhan") else None))

    cparts = []
    for name, st in (_g(bt, "special_stars", default={}) or {}).items():
        if isinstance(st, dict) and st.get("polarity") == "dữ":
            cparts.append(f"{name} ({st.get('pillar', '?')}): {st.get('description', '')} — "
                          "đọc là khuynh hướng cần bù đắp bằng kết nối chủ động, không phải án")
    for wmsg in _g(bt, "warnings", default=[]) or []:
        cparts.append(str(wmsg))
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": "cang" if cross else ("thuan" if bt else None),
            "src": [SRC_TRUNG_CHAU] if lead else []}


def _asp8_con_cai(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    parts = []
    p57 = _g(tv, "quy_luat_v3", "57_da_la_cung_luc_than", default={}) or {}
    if p57.get("detected") and p57.get("palace") == "Tử Tức":
        parts.append(str(p57.get("paradigm")))
    p21 = _g(tv, "quy_luat_v3", "21_thien_co_thai_am_tu_tuc", default={}) or {}
    if p21.get("detected"):
        parts.append(str(p21.get("paradigm")))
    tt_stars = _stars_at_palace(ctx["la_so"], "Tử Tức")
    if tt_stars:
        parts.append(f"Cung Tử Tức tọa: {', '.join(tt_stars)}")
    lead = _join(parts)
    lead_dir = None
    if parts:
        lead_dir = "cang" if (p57.get("detected") or p21.get("detected")) else "thuan"

    dist = _g(ctx["state"], "thap_than_distribution", default={}) or {}
    vis = (dist.get("visible") or {})
    hid = (dist.get("hidden") or {})
    con_tinh = {"Thực Thần": vis.get("Thực Thần", 0) + hid.get("Thực Thần", 0),
                "Thương Quan": vis.get("Thương Quan", 0) + hid.get("Thương Quan", 0)}
    tot = sum(con_tinh.values())
    cross = ""
    if dist:
        if tot:
            desc = ", ".join(f"{k}×{v}" for k, v in con_tinh.items() if v)
            an = " (phần lớn tàng — khí con cái nằm tầng sâu)" if not (
                vis.get("Thực Thần") or vis.get("Thương Quan")) else ""
            cross = f"Sao con cái theo Tứ trụ (Thực/Thương): {desc}{an}"
        else:
            cross = ("Thực/Thương không hiện trong tứ trụ — khí con cái không lộ ở bàn gốc, "
                     "thường xét thêm đại vận (hệ không suy đoán thay)")
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": ("thuan" if tot else "cang") if cross else None,
            "src": [SRC_TRUNG_CHAU] if lead else []}


def _asp9_cha_me(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    dist = _g(ctx["state"], "thap_than_distribution", default={}) or {}
    vis, hid = dist.get("visible") or {}, dist.get("hidden") or {}
    fam_map = _g(ctx["state"], "thap_than_family_map", default={}) or {}
    parts = []
    for tt in ("Chính Ấn", "Thiên Ấn", "Thiên Tài", "Tỷ Kiên", "Kiếp Tài"):
        n = (vis.get(tt) or 0) + (hid.get(tt) or 0)
        if n and fam_map.get(tt):
            parts.append(f"{tt}×{n} ({fam_map[tt]})")
    lead = ("Khí lục thân trong tứ trụ: " + ", ".join(parts)) if parts else ""

    cparts = []
    p72 = _g(tv, "quy_luat_v3", "72_phuong_cac_menh", default={}) or {}
    if p72.get("detected"):
        cparts.append(str(p72.get("paradigm")))
    for cung in ("Phụ Mẫu", "Huynh Đệ"):
        st = _stars_at_palace(ctx["la_so"], cung)
        if st:
            cparts.append(f"Cung {cung}: {', '.join(st)}")
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": "thuan" if parts else None,
            "cross": cross,
            "cross_dir": ("thuan" if p72.get("is_cat") else "thuan") if cross else None,
            "src": ([SRC_TRUNG_CHAU] if cross else [])}


def _asp10_tam_ly(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    cb = _g(tv, "cross_bind_phuc_duc", default={}) or {}
    parts = []
    pd_stars = (cb.get("phuc_duc_chinh_tinh") or []) + (cb.get("phuc_duc_phu_tinh") or [])
    if pd_stars:
        parts.append(f"Phúc Đức (gốc tâm lý hôn nhân) tọa: {', '.join(pd_stars)}")
    for msg in (cb.get("canh_bao_cross") or []):
        if "Phúc Đức" in str(msg):
            parts.append(str(msg))
    for msg in (cb.get("diem_cat_cross") or []):
        if "Phúc Đức" in str(msg):
            parts.append(str(msg))
    p6 = _g(tv, "quy_luat_v2", "6_menh_chu_anh_huong", default={}) or {}
    if p6.get("paradigm"):
        parts.append(f"Mệnh chủ {p6.get('menh_chu')}: {p6['paradigm']}")
    lead = _join(parts)
    lead_dir = None
    if lead:
        lead_dir = "cang" if any("⚠" in str(m) or "cảnh báo" in _norm(str(m))
                                 for m in (cb.get("canh_bao_cross") or [])) else "thuan"

    dt = _g(ctx["state"], "dung_than", default={}) or {}
    cross = ""
    if dt.get("strength_tag"):
        tag = str(dt["strength_tag"])
        tag_vi = {"balanced": "cân bằng", "strong": "vượng", "weak": "nhược"}.get(tag, tag)
        cross = (f"Nhật chủ {tag_vi} — nội lực cảm xúc trong hôn nhân "
                 + ("có sức đàn hồi, ít cực đoan" if tag == "balanced" else
                    "mạnh, cần chừa chỗ cho bạn đời" if tag == "strong" else
                    "cần được bồi đắp, nên chọn môi trường nâng đỡ"))
    return {"lead": lead, "lead_dir": lead_dir, "cross": cross,
            "cross_dir": ("thuan" if dt.get("strength_tag") in ("balanced", "strong") else "cang")
                         if cross else None,
            "src": [SRC_TRUNG_CHAU] if lead else []}


def _asp11_tai_san(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    dist = _g(ctx["state"], "thap_than_distribution", default={}) or {}
    vis, hid = dist.get("visible") or {}, dist.get("hidden") or {}
    tai = {"Chính Tài": (vis.get("Chính Tài") or 0) + (hid.get("Chính Tài") or 0),
           "Thiên Tài": (vis.get("Thiên Tài") or 0) + (hid.get("Thiên Tài") or 0)}
    parts = []
    if any(tai.values()):
        parts.append("Tài tinh: " + ", ".join(f"{k}×{v}" for k, v in tai.items() if v))
    tang_tt = [t.get("thap_than") for t in (_g(bt, "cung_phoi", "tang_can", default=[]) or [])
               if isinstance(t, dict)]
    if "Chính Tài" in tang_tt or "Thiên Tài" in tang_tt:
        parts.append("Tài tinh tàng ngay tại Cung Phối — tiền bạc và hôn nhân đi chung một cửa, "
                     "minh bạch tài chính là giữ hôn nhân")
    dt = _g(ctx["state"], "dung_than", default={}) or {}
    if dt.get("dung_than_element"):
        parts.append(f"Dụng thần {dt['dung_than_element']} — kinh tế gia đình thuận khi "
                     f"sinh hoạt/nghề nghiệp đi theo hành này")
    lead = _join(parts)

    cparts = []
    q17 = _g(tv, "quy_luat_v4", "Q17_loc_hop_uyen_uong", default={}) or {}
    if q17.get("loc_ton_at_phu_the"):
        cparts.append("Lộc Tồn tọa Phu Thê — khí lộc đi cùng hôn nhân (giữ được khi vun chung)")
    hung_tai = []
    for qk in ("Q22_vu_khuc_ki_tai_bach", "Q25_vu_khuc_ki_dien_trach"):
        q = _g(tv, "quy_luat_v4", qk, default={}) or {}
        if q.get("detected"):
            hung_tai.append(str(q.get("paradigm") or qk))
    if hung_tai:
        cparts += hung_tai
    elif _g(tv, "quy_luat_v4"):
        cparts.append("Không có Vũ Khúc Hóa Kỵ đóng Tài Bạch/Điền Trạch — tài khố không bị phá cách")
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": "thuan" if lead else None,
            "cross": cross,
            "cross_dir": ("cang" if hung_tai else "thuan") if cross else None,
            "src": [SRC_TRUNG_CHAU] if cross else []}


def _asp12_dinh_gio(ctx) -> dict:
    tv, bt = ctx["tv"], ctx["bt"]
    # Sao an theo GIỜ sinh (Xương/Khúc...) đóng ở cung hôn nhân → cục diện NHẠY giờ sinh
    hour_stars = {"Văn Xương", "Văn Khúc"}
    parts = []
    in_phu_the = [s for s in ((_g(tv, "phu_tinh", default=[]) or [])
                              + (_g(tv, "chinh_tinh", default=[]) or [])) if s in hour_stars]
    pd_stars = _g(tv, "cross_bind_phuc_duc", "phuc_duc_phu_tinh", default=[]) or []
    in_phuc_duc = [s for s in pd_stars if s in hour_stars]
    if in_phu_the or in_phuc_duc:
        cho = _join([f"Phu Thê có {', '.join(in_phu_the)}" if in_phu_the else "",
                     f"Phúc Đức có {', '.join(in_phuc_duc)}" if in_phuc_duc else ""])
        parts.append(f"{cho} — đây là sao an theo GIỜ sinh: cục diện hôn nhân của lá này "
                     "NHẠY với giờ; nếu giờ sinh nhớ áng chừng, nên kiểm lại (lệch 1 canh giờ "
                     "là đổi bàn)")
    lead = _join(parts)

    cparts = []
    for name, st in (_g(bt, "special_stars", default={}) or {}).items():
        if isinstance(st, dict) and st.get("pillar") == "hour":
            cparts.append(f"{name} đóng ở TRỤ GIỜ ({st.get('description', '')}) — "
                          "cùng một nhắc: nghiệm lại giờ sinh giúp bàn này chắc hơn")
    cross = _join(cparts)
    return {"lead": lead, "lead_dir": "cang" if lead else None,
            "cross": cross, "cross_dir": "cang" if cross else None,
            "src": [SRC_TRUNG_CHAU] if lead else []}


_BUILDERS: dict[int, Callable[[dict], dict]] = {
    1: _asp1_tinh_cach, 2: _asp2_chat_luong, 3: _asp3_ung_ky, 4: _asp4_nang_luong,
    5: _asp5_luc_phoi_tinh, 6: _asp6_hop_doi, 7: _asp7_diem_cang, 8: _asp8_con_cai,
    9: _asp9_cha_me, 10: _asp10_tam_ly, 11: _asp11_tai_san, 12: _asp12_dinh_gio,
}


def luan_hon_nhan_song_phai(*, bat_tu_state: dict, la_so: dict) -> dict[str, Any]:
    """Hợp nhất Bát Tự ↔ Tử Vi → 12 khía cạnh hôn nhân + cờ đồng/dị-tham.

    An toàn: 1 engine lỗi → khía cạnh phái đó `unsourced`/`một_phía`, KHÔNG sập;
    lỗi ghi vào `engine_errors` (minh bạch). Mọi reading qua paradigm guard.
    Tín hiệu per-khía-cạnh (v1) — thiếu thì degrade về hướng tổng, rồi mới tới
    câu quote-or-silence người-đọc-được.
    """
    engine_errors: list[str] = []
    try:
        bt_out = analyze_hon_nhan(bat_tu_state)
    except Exception as e:  # noqa: BLE001 — engine con lỗi không được làm sập orchestrator
        bt_out, _ = None, engine_errors.append(f"bat_tu: {e}")
    try:
        tv_out = chiem_phu_the_v4(la_so)
    except Exception as e:  # noqa: BLE001
        tv_out, _ = None, engine_errors.append(f"tu_vi: {e}")

    out_by_school = {"bat_tu": bt_out, "tu_vi": tv_out}
    gender = (bat_tu_state or {}).get("gender") or (bt_out or {}).get("gender")
    ctx = {"bt": bt_out, "tv": tv_out, "state": bat_tu_state or {},
           "la_so": la_so or {}, "phoi": _phoi_label(gender)}

    khia_canh: list[dict] = []
    all_paradigm_ok = True

    for asp in ASPECTS:
        lead_s = asp["lead"]
        cross_s = "tu_vi" if lead_s == "bat_tu" else "bat_tu"

        # 1) tín hiệu RIÊNG của khía cạnh (v1)
        spec: dict = {}
        try:
            spec = _BUILDERS[asp["id"]](ctx) or {}
        except Exception as e:  # noqa: BLE001 — builder hỏng 1 khía cạnh không sập cả bàn
            engine_errors.append(f"aspect_{asp['id']}: {e}")

        # builder trả theo vai lead/cross của KHÍA CẠNH; map về trường phái
        spec_by_school = ({lead_s: (spec.get("lead"), spec.get("lead_dir")),
                           cross_s: (spec.get("cross"), spec.get("cross_dir"))})

        # 2) fallback hướng tổng của engine (v0) cho phía còn trống
        glob_lead, glob_lead_dir, lead_src0 = _read_dir_src(out_by_school[lead_s], lead_s)
        glob_cross, glob_cross_dir, cross_src0 = _read_dir_src(out_by_school[cross_s], cross_s)

        lead_reading = spec_by_school[lead_s][0] or glob_lead
        lead_dir = spec_by_school[lead_s][1] or glob_lead_dir
        cross_reading = spec_by_school[cross_s][0] or glob_cross
        cross_dir = spec_by_school[cross_s][1] or glob_cross_dir

        ok_l, fl_l = _reframe_check(lead_reading)
        ok_c, fl_c = _reframe_check(cross_reading)
        paradigm_ok = ok_l and ok_c
        all_paradigm_ok = all_paradigm_ok and paradigm_ok

        sources = list(dict.fromkeys(lead_src0 + cross_src0 + (spec.get("src") or [])))
        cc = _concord(lead_dir, cross_dir)
        khia_canh.append({
            "id": asp["id"],
            "ten": asp["ten"],
            "lead_school": lead_s,
            "lead_reading": lead_reading or FALLBACK_USER,
            "cross_reading": cross_reading or FALLBACK_USER,
            "concord": cc,
            "note": ("dị-tham: giữ CẢ HAI quan điểm, thận trọng" if cc == CONCORD_DI else ""),
            "sources": sources,
            "unsourced": not sources,
            "paradigm_ok": paradigm_ok,
            "paradigm_flags": (fl_l + fl_c) or None,
        })

    return {
        "method_id": "hon_nhan_song_phai_v1",
        "paradigm": "Đọc đồng dạng, KHÔNG predict. Bát Tự=THỂ, Tử Vi=DỤNG; mệnh là động từ.",
        "khia_canh": khia_canh,
        "paradigm_ok": all_paradigm_ok,
        "engine_errors": engine_errors,
    }
