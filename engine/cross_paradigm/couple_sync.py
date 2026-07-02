"""#56 — Luận SO ĐÔI đích danh (2 lá số cụ thể): Bát Tự hợp hôn + Tử Vi Phu Thê chéo.

Khác #55 (12 khía cạnh của MỘT lá): đây so HAI người (mình + người yêu/vợ chồng).
THỂ (Bát Tự hợp hôn: bổ khuyết ngũ hành + thập thần tương hợp) × DỤNG (Tử Vi Phu Thê
chéo: sao cung Phu Thê A soi B và ngược lại) → đồng/dị-tham (kept_all, Iron #3).
Paradigm: KHÔNG "hợp/khắc → nên/không nên cưới"; đọc đồng dạng + động từ (Iron #4/#6/#8).

v1 (2026-07-02, "đổ thịt"): wire ĐỦ tín hiệu 2 engine con thay vì chỉ overall —
Bát Tự: day_master_compat + tương tác chi Cung Phối (lục hợp/xung/hại cụ thể) +
ngu_hanh_dynamics (ai bù khuyết ai, dụng thần chung) + spouse_check. Tử Vi: Phu Thê
CHÉO ĐÚNG NGHĨA (chính tinh cung Phu Thê lá A đối chiếu chính tinh MỆNH lá B và
ngược lại, chân dung từ kho NUA_KIA) + panorama 56 quy luật mỗi lá. Thêm
`overall_score` + `compatibility_factors` + `recommendations` (đúng spec AppChat 3.3)
— điểm là TỔNG HỢP MINH BẠCH từ các tín hiệu trên (score_method ghi rõ), không phán bừa.
"""
from __future__ import annotations

import unicodedata
from typing import Any, Optional

from engine.cross_paradigm._common import (
    CONCORD_DI, concord as _concord, norm as _norm, reframe_check as _reframe_check,
)

# Engine con — module-level để test monkeypatch được.
from engine.bat_tu.compatibility import analyze_compatibility
from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4

GIA_XU = 30  # giá đã chốt (issue #56) — luận 2 lá số

_NEG = ("khac", "xung", "cang", "ky", "hao", "pha", "kiep", "hung", "tuyet")
_POS = ("hop", "thuan", "tot", "cat", "on", "vuong", "bo khuyet", "tuong ho", "vien")


def _slug(star: str) -> str:
    s = unicodedata.normalize("NFD", star or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower().replace("đ", "d").strip().replace(" ", "_")


def _nua_kia(star: str) -> str:
    """Chân dung chính tinh (kho NUA_KIA món Duyên — tái dùng Iron #1)."""
    try:
        from engine.tu_vi.duyen import NUA_KIA
        return NUA_KIA.get(_slug(star), "")
    except Exception:  # noqa: BLE001
        return ""


def _stars_at(la_so: dict, palace_name: str, key: str = "chinh_tinh") -> list[str]:
    """Chính tinh đóng tại 1 cung chức năng của lá số (map sao→branch_index)."""
    idx = None
    for p in (la_so or {}).get("palaces") or []:
        if isinstance(p, dict) and p.get("name") == palace_name:
            idx = p.get("branch_index")
            break
    if idx is None:
        return []
    m = (la_so or {}).get(key)
    return [s for s, i in m.items() if i == idx] if isinstance(m, dict) else []


def _dir_compat(out: Optional[dict]) -> Optional[str]:
    """Hướng Bát Tự hợp hôn: hợp/bổ khuyết → thuan; khắc/xung → cang."""
    if not out:
        return None
    label = _norm(str((out.get("overall") or {}).get("label", "")))
    if any(k in label for k in _NEG):
        return "cang"
    if any(k in label for k in _POS):
        return "thuan"
    # nhãn trung tính → đếm tương tác chi Cung Phối (căng vs lành)
    inter = (out.get("cung_phoi") or {}).get("interactions") or []
    cang = sum(1 for i in inter if isinstance(i, dict) and "căng" in str(i.get("polarity", "")))
    lanh = sum(1 for i in inter if isinstance(i, dict) and "lành" in str(i.get("polarity", "")))
    if cang > lanh:
        return "cang"
    if lanh > cang:
        return "thuan"
    return "thuan" if out.get("overall") else None


def _pano_net(o: Optional[dict]) -> Optional[int]:
    p = (o or {}).get("panorama_hon_nhan") or {}
    n = p.get("net")
    return n if isinstance(n, (int, float)) else None


def _dir_phu_the(a_out: Optional[dict], b_out: Optional[dict]) -> Optional[str]:
    """Hướng Tử Vi: rule 'hit' (mock/legacy) HOẶC panorama net 56 quy luật (lá thật)."""
    outs = [o for o in (a_out, b_out) if o]
    if not outs:
        return None
    for o in outs:
        if any(isinstance(v, dict) and v.get("hit") for v in o.values()):
            return "cang"
    nets = [n for n in (_pano_net(o) for o in outs) if n is not None]
    if nets:
        return "cang" if sum(nets) < 0 else "thuan"
    return "thuan"


def _phu_the_reading(a_out: Optional[dict], b_out: Optional[dict]) -> str:
    parts = []
    for tag, o in (("A", a_out), ("B", b_out)):
        if o and o.get("phu_the_tong_quan"):
            parts.append(f"[{tag}] {o['phu_the_tong_quan']}")
        elif o and (o.get("panorama_hon_nhan") or {}).get("summary"):
            parts.append(f"[{tag}] {o['panorama_hon_nhan']['summary']}")
    return " · ".join(parts)


def _bat_tu_chi_tiet(bt: Optional[dict]) -> list[dict]:
    """Bung tín hiệu Bát Tự hợp hôn thành factors đọc được (mỗi cái có tone)."""
    if not bt:
        return []
    fs: list[dict] = []
    dm = bt.get("day_master_compat") or {}
    if dm.get("narrative"):
        pol = str(dm.get("polarity", ""))
        tone = "lành" if "lành" in pol else ("căng" if "căng" in pol else "trung")
        fs.append({"nhom": "Nhật chủ", "noi_dung": str(dm["narrative"]), "tone": tone})
    for i in ((bt.get("cung_phoi") or {}).get("interactions") or []):
        if isinstance(i, dict) and i.get("narrative"):
            fs.append({"nhom": "Cung Phối (chi ngày)", "noi_dung": str(i["narrative"]),
                       "tone": "căng" if "căng" in str(i.get("polarity", "")) else "lành"})
    nh = bt.get("ngu_hanh_dynamics") or {}
    helps = []
    if nh.get("a_helps_b"):
        helps.append(f"bạn bù cho người ấy hành {', '.join(map(str, nh['a_helps_b']))}")
    if nh.get("b_helps_a"):
        helps.append(f"người ấy bù cho bạn hành {', '.join(map(str, nh['b_helps_a']))}")
    if helps:
        fs.append({"nhom": "Ngũ hành bù khuyết", "noi_dung": "; ".join(helps).capitalize(),
                   "tone": "lành"})
    if nh.get("common_dung_than"):
        fs.append({"nhom": "Dụng thần", "noi_dung": "Hai người CÙNG dụng thần — nhu cầu "
                   "sâu cùng hướng, vun một đường cả hai cùng lợi", "tone": "lành"})
    sc = bt.get("spouse_check") or {}
    if sc.get("narrative"):
        tone = "lành" if (sc.get("vo_match") or sc.get("chong_match")) else "trung"
        fs.append({"nhom": "Phối tinh (Tài/Quan)", "noi_dung": str(sc["narrative"]), "tone": tone})
    return fs


def _cheo_1_chieu(tv_src: Optional[dict], la_so_dst: Optional[dict],
                  label_src: str, label_dst: str) -> Optional[dict]:
    """Phu Thê lá `src` (kiểu người src vận hành hợp) ↔ chính tinh MỆNH lá `dst`."""
    stars_pt = (tv_src or {}).get("chinh_tinh") or []
    stars_menh = _stars_at(la_so_dst or {}, "Mệnh")
    muon_doi_cung = False
    if not stars_pt:
        # Phu Thê VÔ CHÍNH DIỆU → mượn chính tinh ĐỐI CUNG (phép chuẩn; rule 5 của
        # chiêm Phu Thê v4 đã tính sẵn stars_in_doi_cung — tái dùng, không tự an lại).
        r5 = ((tv_src or {}).get("quy_luat_v2") or {}).get("5_doi_cung_vo_chinh_dieu") or {}
        stars_pt = r5.get("stars_in_doi_cung") or []
        muon_doi_cung = bool(stars_pt)
    if not stars_pt:
        return None
    trung = sorted(set(stars_pt) & set(stars_menh))
    parts = [f"Cung Phu Thê lá {label_src} "
             + (f"vô chính diệu — mượn đối cung: {' + '.join(stars_pt)}"
                if muon_doi_cung else f"tọa {' + '.join(stars_pt)}")
             + f" — kiểu khí chất {label_src} vận hành hợp"]
    desc = _nua_kia(stars_pt[0])
    if desc:
        parts.append(f"({stars_pt[0]}: {desc})")
    if stars_menh:
        parts.append(f"Mệnh {label_dst} tọa {' + '.join(stars_menh)}")
        dm = _nua_kia(stars_menh[0])
        if dm:
            parts.append(f"({stars_menh[0]}: {dm})")
        if trung:
            parts.append(f"→ TRÙNG BỘ {', '.join(trung)}: chân dung {label_src} 'chờ' "
                         f"khớp thẳng khí chất {label_dst} — kênh hiểu nhau mở sẵn")
        else:
            parts.append("→ không trùng bộ sao: hai mô tả trên là hai 'ngôn ngữ khí chất' "
                         "khác nhau — hiểu nhau được khi chịu học ngôn ngữ của nhau, "
                         "hệ không phán hợp/khắc cứng")
    else:
        parts.append(f"(Mệnh {label_dst} vô chính diệu / thiếu dữ liệu — chỉ đọc một chiều)")
    return {"reading": " · ".join(parts), "trung_bo": trung,
            "phu_the_stars": stars_pt, "menh_stars": stars_menh}


def _pano_factor(tag: str, o: Optional[dict]) -> Optional[dict]:
    p = (o or {}).get("panorama_hon_nhan") or {}
    if not p.get("summary"):
        return None
    net = p.get("net")
    return {"nhom": f"Cấu trúc Phu Thê lá {tag} (56 quy luật Trung Châu)",
            "noi_dung": str(p["summary"]),
            "tone": "lành" if (net or 0) > 0 else ("căng" if (net or 0) < 0 else "trung")}


def luan_so_doi(*, person_a: dict, person_b: dict) -> dict[str, Any]:
    """So đôi đích danh 2 lá số → Bát Tự hợp hôn + Tử Vi Phu Thê chéo + đồng/dị-tham.

    person_{a,b} = {"bat_tu_state": <cast_bat_tu out>, "la_so": <tu vi la_so>}.
    An toàn: engine con lỗi → phái đó unsourced, KHÔNG sập, ghi engine_errors.
    """
    errs: list[str] = []
    try:
        bt = analyze_compatibility(person_a.get("bat_tu_state"), person_b.get("bat_tu_state"))
    except Exception as e:  # noqa: BLE001
        bt, _ = None, errs.append(f"bat_tu: {e}")
    try:
        tv_a = chiem_phu_the_v4(person_a.get("la_so"))
        tv_b = chiem_phu_the_v4(person_b.get("la_so"))
    except Exception as e:  # noqa: BLE001
        tv_a, tv_b, _ = None, None, errs.append(f"tu_vi: {e}")

    # ── THỂ: Bát Tự hợp hôn (bung đủ tín hiệu) ───────────────────────────────────
    bt_factors = _bat_tu_chi_tiet(bt)
    bt_reading = " · ".join(f.get("noi_dung", "") for f in bt_factors) if bt_factors else \
                 (str((bt.get("overall") or {}).get("narrative", "")) if bt else "")
    bt_dir = _dir_compat(bt)
    bt_src = [str(bt["source_ref"])] if (bt and bt.get("source_ref")) else []

    # ── DỤNG: Tử Vi Phu Thê CHÉO đích danh (A↔B) ─────────────────────────────────
    cheo_ab = cheo_ba = None
    try:
        cheo_ab = _cheo_1_chieu(tv_a, person_b.get("la_so"), "bạn", "người ấy")
        cheo_ba = _cheo_1_chieu(tv_b, person_a.get("la_so"), "người ấy", "bạn")
    except Exception as e:  # noqa: BLE001 — chéo hỏng không sập cả phép
        errs.append(f"phu_the_cheo: {e}")
    cheo_parts = [c["reading"] for c in (cheo_ab, cheo_ba) if c]
    tv_reading = " ⇄ ".join(cheo_parts) if cheo_parts else _phu_the_reading(tv_a, tv_b)
    tv_dir = _dir_phu_the(tv_a, tv_b)
    tv_src = [("Tử Vi Bắc phái Trung Châu (Vương Đình Chỉ) — chiêm Phu Thê v4 + "
               "kho chân dung chính tinh (dùng chung món Duyên)")] if cheo_parts else []

    # ── factors + score + recommendations (spec AppChat 3.3) ─────────────────────
    factors: list[dict] = list(bt_factors)
    for tag, o in (("bạn", tv_a), ("người ấy", tv_b)):
        f = _pano_factor(tag, o)
        if f:
            factors.append(f)
    for c, chieu in ((cheo_ab, "Phu Thê bạn ↔ Mệnh người ấy"),
                     (cheo_ba, "Phu Thê người ấy ↔ Mệnh bạn")):
        if c and c.get("menh_stars"):
            factors.append({"nhom": f"Chéo đích danh ({chieu})",
                            "noi_dung": ("Trùng bộ " + ", ".join(c["trung_bo"])
                                         if c.get("trung_bo") else "Không trùng bộ sao — "
                                         "học 'ngôn ngữ khí chất' của nhau"),
                            "tone": "lành" if c.get("trung_bo") else "trung"})

    # Điểm tổng MINH BẠCH: cộng dồn từ tone các factor (không phải phán số mệnh).
    score = 50
    for f in factors:
        score += {"lành": 8, "căng": -8}.get(f.get("tone"), 0)
    nets = [n for n in (_pano_net(tv_a), _pano_net(tv_b)) if n is not None]
    score += sum(3 * n for n in nets)
    overall_score = max(5, min(95, score))

    recommendations: list[str] = []
    for f in factors:
        if f.get("tone") == "căng":
            recommendations.append(f"{f['nhom']}: {f['noi_dung']} → đây là chỗ nên CHỦ ĐỘNG "
                                   "chăm (nói rõ, chậm lại khi quyết định chung) — khí là "
                                   "xu hướng, cách vận hành là của hai bạn")
    if not recommendations and factors:
        recommendations.append("Các tín hiệu chính đang thuận — giữ nhịp: duy trì kênh nói "
                               "thật + vun theo hướng dụng thần chung (nếu có)")

    con = _concord(bt_dir, tv_dir)
    ok_bt, fl_bt = _reframe_check(bt_reading)
    ok_tv, fl_tv = _reframe_check(tv_reading)

    return {
        "method_id": "couple_sync_v1",
        "paradigm": ("Đọc đồng dạng, KHÔNG 'nên/không nên cưới'. Bát Tự=THỂ (hợp hôn), "
                     "Tử Vi=DỤNG (Phu Thê chéo); năng lượng hai người VẬN HÀNH thế nào."),
        "bat_tu_hop_hon": {
            "reading": bt_reading or "Chưa đủ dữ kiện có nguồn cho lớp Bát Tự — hệ không suy đoán thêm.",
            "direction": bt_dir, "sources": bt_src,
            "chi_tiet": bt_factors or None,
        },
        "tu_vi_phu_the_cheo": {
            "reading": tv_reading or "Chưa đủ dữ kiện có nguồn cho lớp Tử Vi — hệ không suy đoán thêm.",
            "direction": tv_dir, "sources": tv_src,
            "a_sang_b": cheo_ab, "b_sang_a": cheo_ba,
        },
        "concord": con,
        "note": "dị-tham: giữ CẢ HAI quan điểm, thận trọng" if con == CONCORD_DI else "",
        # spec AppChat 3.3
        "overall_score": overall_score,
        "score_method": ("50 gốc ± 8/tone tín hiệu (lành/căng) + 3×net panorama mỗi lá — "
                         "tổng hợp minh bạch từ tín hiệu có nguồn, không phải 'số phận'"),
        "compatibility_factors": factors,
        "recommendations": recommendations,
        "paradigm_ok": ok_bt and ok_tv,
        "paradigm_flags": (fl_bt + fl_tv) or None,
        "engine_errors": errs,
        "gia_xu": GIA_XU,
    }
