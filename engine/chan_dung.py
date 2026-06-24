"""Chân Dung khách hàng — tổng hợp DETERMINISTIC "khách LÀ AI" từ 3 lá số.

Paradigm (Iron Rule #4/#8): ĐỌC ĐỒNG DẠNG, mệnh là ĐỘNG TỪ — KHÔNG predict cát/hung,
KHÔNG "anh sẽ thành công/thất bại". Chỉ phản chiếu cấu trúc tâm-thiên-thân + cách VẬN HÀNH.

Tái dùng (Iron Rule #1, không viết lại):
- Bát Tự  → engine.yi_wiki.life_overview.generate_life_overview (nhật chủ + STEM_PROFILE + ngũ hành + dụng thần)
- Tử Vi   → engine.tu_vi.from_birth.cast_la_so_from_birth + concept_dict (nghĩa sao Quyển 1)
- Nội tâm → engine.tu_vi.from_birth.cast_chieu_dom_from_birth (18 Phi Tinh Bắc phái)

Bản LLM văn xuôi SÂU (chi tiết) = sản phẩm TRẢ PHÍ (Luận Sâu 99xu / Hỏi Hội Đồng). Đây là bản
nền MIỄN PHÍ, nhanh, tin cậy — vừa cho khách thấy "chân dung" vừa làm bệ phóng tới sản phẩm sâu.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("yi.chan_dung")


def _bat_tu(birth_iso: str, gender: str, name: str) -> tuple[dict, dict]:
    """Cốt cách + hướng dẫn từ Bát Tự — 1 lần gọi generate_life_overview, tách 2 phần.
    Trả (cot_cach, huong_dan). Lỗi → ({}, {})."""
    try:
        from engine.yi_wiki.life_overview import generate_life_overview
        g = "nam" if (gender or "nam") in ("nam", "M", "male") else "nu"
        ov = generate_life_overview(birth_iso, gender=g, name=name or "Quý khách")
        dm = ov.get("section_2_day_master") or {}
        sp = dm.get("stem_profile") or {}
        tt = ov.get("section_1_tu_tru") or {}
        fav = ov.get("section_9_favorable") or {}
        career = ov.get("section_6_career") or {}
        health = ov.get("section_8_health") or {}
        advice = ov.get("section_10_advice") or {}
        thua = tt.get("thua_hanh") or []
        thieu = tt.get("thieu_hanh") or []
        hnotes = health.get("health_notes") or {}
        suc_khoe = [{"hanh": h, "note": hnotes[h]} for h in (list(thua) + list(thieu)) if h in hnotes]
        cot_cach = {
            "nhat_chu": sp.get("label") or f"{dm.get('nhat_chu', '')} {dm.get('nhat_chu_hanh', '')}".strip(),
            "hinh_anh": sp.get("image"),
            "tinh_cach": sp.get("personality"),
            "ngu_hanh": tt.get("hanh_count") or {},
            "thieu_hanh": thieu, "thua_hanh": thua,
            "favorable": fav.get("favorable") or {},
        }
        huong_dan = {
            "su_nghiep": career.get("candidates") or [],
            "dung_hanh": career.get("dung_hanh"),
            "suc_khoe": suc_khoe[:3],
            "loi_khuyen": (advice.get("key_principles") or [])[:5],
        }
        return cot_cach, huong_dan
    except Exception as e:
        logger.info("chan_dung bat_tu lỗi: %s", str(e)[:120])
        return {}, {}


def _tu_vi_menh(birth_iso: str, gender: str, tz: str) -> dict:
    """Mệnh từ Tử Vi — chính tinh tại Mệnh + mệnh chủ/thân chủ + cục + tứ hóa, bám nghĩa sách."""
    try:
        from engine.tu_vi.from_birth import cast_la_so_from_birth
        ls = cast_la_so_from_birth(birth_datetime_local=birth_iso, timezone=tz, gender=gender)
        menh_idx = ls.get("menh_index")
        chinh = ls.get("chinh_tinh") or {}
        tai_menh = [s for s, idx in chinh.items() if idx == menh_idx]

        from engine.tu_vi import concept_dict
        def _nghia(term):
            try:
                e = concept_dict.lookup(term)
                return (e or {}).get("definition") or ""
            except Exception:
                return ""

        # Cách cục NAMED + đại vận HIỆN TẠI (tinh hoa: engine đã tính, surface lên)
        cach_cuc, dai_van = [], None
        try:
            import datetime
            from engine.tu_vi import cach_cuc_dict
            from engine.tu_vi.cach_cuc_named import match_named_cach_cucs
            from engine.tu_vi.la_so_input_builder import build_la_so_input
            by = int(birth_iso[:4])
            lsi = build_la_so_input(ls, gender, birth_year=by, now_year=datetime.datetime.now().year)
            matched = match_named_cach_cucs(lsi) or []
            for c in matched[:6]:
                ten = c.get("ten")
                nghia = ""
                try:
                    e = cach_cuc_dict.lookup_by_name(ten)
                    nghia = ((e or {}).get("y_nghia") or "")[:240]
                except Exception:
                    pass
                cach_cuc.append({"ten": ten, "loai": c.get("loai"),
                                 "dieu_kien": c.get("dieu_kien"), "y_nghia": nghia})
            dai_van = lsi.get("dai_van_hien_tai")
        except Exception as e:
            logger.info("chan_dung cách cục lỗi: %s", str(e)[:120])
        return {
            "menh_cung": ls.get("menh_branch"),
            "than_cung": ls.get("than_branch"),
            "cuc": ls.get("cuc_name"),
            "menh_chu": ls.get("menh_chu"),
            "than_chu": ls.get("than_chu"),
            "chinh_tinh_tai_menh": [{"sao": s, "nghia": _nghia(s)} for s in tai_menh],
            "tu_hoa": ls.get("tu_hoa") or {},
            "cach_cuc": cach_cuc,
            "dai_van_hien_tai": dai_van,
        }
    except Exception as e:
        logger.info("chan_dung tu_vi lỗi: %s", str(e)[:120])
        return {}


def _noi_tam(birth_iso: str, gender: str, tz: str) -> dict:
    """Nội tâm từ Chiếu Đởm Kinh (18 Phi Tinh) — phản chiếu phần tâm hồn sâu.
    CÓ NGHĨA: ngũ hành từng phi tinh + polarity cung Mệnh (dương→phúc trọng tai khinh /
    âm→phúc khinh tai trọng, theo polarity_rule sách Q4)."""
    try:
        from engine.tu_vi.from_birth import cast_chieu_dom_from_birth
        cd = cast_chieu_dom_from_birth(birth_datetime_local=birth_iso, timezone=tz, gender=gender)
        stars = cd.get("stars") or {}
        menh = cd.get("menh_branch")
        tai_menh = [name for name, chi in stars.items() if chi == menh]
        # metadata: ngũ hành phi tinh + dương/âm cung Mệnh (đọc đồng dạng — không predict)
        nh_map, duong, am, pol = {}, [], [], ""
        try:
            import json
            import pathlib
            d = json.loads(pathlib.Path("data/tu_vi/chieu_dom_kinh_18_phi_tinh.json")
                           .read_text(encoding="utf-8"))
            for grp in ("phi_tinh_9_duong", "phi_tinh_9_am"):
                for s in (d.get(grp) or []):
                    if s.get("name_vi"):
                        nh_map[s["name_vi"]] = s.get("ngu_hanh")
            duong = d.get("duong_palaces") or []
            am = d.get("am_palaces") or []
            pol = (d.get("polarity_rule") or {}).get("rule") or ""
        except Exception:
            pass
        cung_pol = "dương" if menh in duong else ("âm" if menh in am else None)
        return {
            "menh_cung": menh,
            "cung_polarity": cung_pol,
            "polarity_note": pol,
            "phi_tinh_tai_menh": [{"sao": s, "ngu_hanh": nh_map.get(s)} for s in tai_menh],
            "paradigm": cd.get("paradigm_note"),
        }
    except Exception as e:
        logger.info("chan_dung noi_tam lỗi: %s", str(e)[:120])
        return {}


def _ha_lac(birth_iso: str, gender: str, tz: str, age: int) -> dict:
    """Cung đường đời (Hà Lạc Lý Số) — 2 quẻ Tiên/Hậu Thiên + giai đoạn 12 hào. Deterministic, đọc đồng dạng."""
    try:
        from engine.ha_lac.cast import cast_ha_lac
        from engine.ha_lac.luan_giai import compose_ha_lac_luan_giai
        g = "nam" if (gender or "nam") in ("nam", "M", "male") else "nữ"
        hl = compose_ha_lac_luan_giai(
            cast_ha_lac(birth_datetime_local=birth_iso, timezone=tz, gender=g), current_age=age)
        tt = hl.get("tien_thien_luan") or {}
        ht = hl.get("hau_thien_luan") or {}
        return {
            "overview": hl.get("overview"),
            "tien_thien": tt.get("name_vi"), "hau_thien": ht.get("name_vi"),
            "giai_doan_hien_tai": hl.get("bo_huong_stage"),
            "closing": hl.get("closing"),
        }
    except Exception as e:
        logger.info("chan_dung ha_lac lỗi: %s", str(e)[:120])
        return {}


def _duyen(birth_iso: str, gender: str, tz: str, age: int) -> dict:
    """Đường tình duyên (Tử Vi) — chân dung nửa kia + xu hướng + cách vận hành. Deterministic."""
    try:
        from engine.tu_vi.duyen import chan_dung_nua_kia, duyen_ca_nhan
        from engine.tu_vi.from_birth import cast_la_so_from_birth
        from engine.tu_vi.la_so_input_builder import build_la_so_input
        ls = cast_la_so_from_birth(birth_datetime_local=birth_iso, timezone=tz, gender=gender)
        lsi = build_la_so_input(ls, gender, birth_year=int(birth_iso[:4]))
        g = "M" if (gender or "nam") in ("nam", "M", "male") else "F"
        nk = chan_dung_nua_kia(lsi)
        ca = duyen_ca_nhan(lsi, age, g)
        return {
            "nua_kia": {"chinh_tinh": nk.get("chinh_tinh"), "mo_ta": nk.get("mo_ta"),
                        "con_giap_hop": nk.get("con_giap_hop"), "loi_khuyen": nk.get("loi_khuyen")},
            "xu_huong": ca.get("xu_huong"),
            "tin_hieu": ca.get("tin_hieu"),
            "cach_van_hanh": ca.get("cach_van_hanh"),
        }
    except Exception as e:
        logger.info("chan_dung duyen lỗi: %s", str(e)[:120])
        return {}


def _than_so(name: str, birth_iso: str) -> dict:
    """Thần Số học — 6 con số cốt lõi (lăng kính tâm lý phương Tây, đọc đồng dạng). Deterministic."""
    try:
        from engine.than_so.core_numbers import compute_core
        from engine.than_so.interpretation import compose_reading
        y, m, d = int(birth_iso[:4]), int(birth_iso[5:7]), int(birth_iso[8:10])
        core = (compose_reading(compute_core(name or "Quý khách", d, m, y)).get("core") or {})

        def _n(k):
            e = core.get(k) or {}
            return {"value": e.get("value"), "archetype": e.get("archetype_vi"),
                    "dong_dang": e.get("dong_dang")}
        return {k: _n(k) for k in ("life_path", "expression", "soul_urge",
                                   "personality", "birthday", "maturity")}
    except Exception as e:
        logger.info("chan_dung than_so lỗi: %s", str(e)[:120])
        return {}


# Sản phẩm tốt nhất dẫn từ chân dung (bệ phóng) — đọc xong muốn sâu hơn thì lên đây.
BEST_PRODUCTS = [
    {"key": "deep", "icon": "📜", "ten": "Luận Sâu Trọn Đời",
     "mo_ta": "Bản luận văn xuôi đầy đủ cả đời — cốt cách, sự nghiệp, tài lộc, tình duyên, hậu vận.",
     "xu": 99, "cta": "Xem luận sâu"},
    {"key": "council", "icon": "⚖️", "ten": "Hỏi Hội Đồng (luận sâu)",
     "mo_ta": "5+ thầy đa trường phái đối biện 1 câu hỏi lớn của bạn → tổng hợp.",
     "xu": 5, "cta": "Hỏi Hội Đồng"},
    {"key": "duyen", "icon": "💞", "ten": "Gieo Duyên",
     "mo_ta": "Soi đường tình duyên, chân dung nửa kia, hợp tuổi, năm có duyên.",
     "xu": 30, "cta": "Xem duyên"},
]


def build_chan_dung(person: dict) -> dict:
    """Chân dung deterministic của 1 person. person cần birth_datetime_local + gender (+ name, timezone).
    Trả {ok, name, birth, cot_cach, menh, noi_tam, products, paradigm_note}."""
    birth = (person or {}).get("birth_datetime_local")
    if not birth:
        return {"ok": False, "reason": "missing_birth"}
    gender = (person or {}).get("gender") or "nam"
    tz = (person or {}).get("timezone") or "Asia/Ho_Chi_Minh"
    name = (person or {}).get("name") or "Quý khách"
    import datetime
    try:
        age = datetime.datetime.now().year - int(birth[:4]) + 1   # tuổi mụ (cho Hà Lạc + duyên)
    except Exception:
        age = None
    cot_cach, huong_dan = _bat_tu(birth, gender, name)
    return {
        "ok": True,
        "name": name,
        "birth": birth,
        "gender": gender,
        "cot_cach": cot_cach,
        "menh": _tu_vi_menh(birth, gender, tz),
        "noi_tam": _noi_tam(birth, gender, tz),
        "huong_dan": huong_dan,
        "ha_lac": _ha_lac(birth, gender, tz, age),
        "duyen": _duyen(birth, gender, tz, age),
        "than_so": _than_so(name, birth),
        "products": BEST_PRODUCTS,
        "paradigm_note": "Chân dung này ĐỌC ĐỒNG DẠNG — phản chiếu cấu trúc của bạn, không phán "
                         "trước cát/hung. Mệnh là cách VẬN HÀNH cái tính trời cho, không phải án định sẵn.",
    }


if __name__ == "__main__":   # test thực nghiệm với lá số founder
    import json
    r = build_chan_dung({"birth_datetime_local": "1988-06-05T23:30:00", "gender": "nam",
                         "name": "Founder", "timezone": "Asia/Ho_Chi_Minh"})
    print(json.dumps(r, ensure_ascii=False, indent=2)[:2500])
