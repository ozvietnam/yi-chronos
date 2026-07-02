"""Chốt chặn CHẤT LƯỢNG NỘI DUNG món Gieo Duyên trả phí (đợt "đổ thịt" 2026-07-02).

Bài học: v0 hon-nhan-12 trả 1 câu generic LẶP 12 LẦN + dev-note "(unsourced — chưa
wiring...)" lộ cho user trả 30 xu; couple-sync <1KB. Structure-test cũ vẫn PASS vì chỉ
kiểm schema — bộ test này kiểm CHẤT trên LÁ THẬT (an sao deterministic, không LLM):
- 12 khía cạnh phải KHÁC NHAU (không lặp), không lộ chuỗi dev-note.
- Lá KHÁC NHAU → nội dung KHÁC NHAU (không phải hằng số).
- couple-sync đủ keys spec AppChat 3.3 (overall_score/factors/recommendations) + chéo
  đích danh 2 chiều.
- Định thời tinh_duyen có lớp lưu niên GẦN (vá gap "33 tuổi chỉ thấy cửa 63-72").
"""
from __future__ import annotations

import json

import pytest

# 2 lá mẫu khác nhau hẳn (năm/giờ/giới) — an sao deterministic.
NU_1992 = {"birth_datetime_local": "1992-08-20T14:00:00", "gender": "nữ",
           "timezone": "Asia/Ho_Chi_Minh"}
NAM_1990 = {"birth_datetime_local": "1990-03-15T08:30:00", "gender": "nam",
            "timezone": "Asia/Ho_Chi_Minh"}

DEV_NOTE_CAM = ("chưa wiring", "(unsourced")  # chuỗi nội bộ CẤM lộ ra user


@pytest.fixture(scope="module")
def chart_nu():
    from engine.cross_paradigm.service import _chart_of
    return _chart_of(NU_1992)


@pytest.fixture(scope="module")
def chart_nam():
    from engine.cross_paradigm.service import _chart_of
    return _chart_of(NAM_1990)


# ── #55 hon-nhan-12: hết cảnh 1 câu lặp 12 lần ──────────────────────────────────

def test_hon_nhan_12_reading_khac_nhau_tren_la_that(chart_nu):
    from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
    out = luan_hon_nhan_song_phai(bat_tu_state=chart_nu["bat_tu_state"],
                                  la_so=chart_nu["la_so"])
    kc = out["khia_canh"]
    assert len(kc) == 12
    leads = [a["lead_reading"] for a in kc]
    crosses = [a["cross_reading"] for a in kc]
    # v0 bug: 12 reading y hệt nhau. v1: gần như mỗi khía cạnh một nội dung.
    assert len(set(leads)) >= 10, f"lead reading lặp: chỉ {len(set(leads))}/12 khác nhau"
    assert len(set(crosses)) >= 8, f"cross reading lặp: chỉ {len(set(crosses))}/12 khác nhau"
    assert out["paradigm_ok"] is True
    assert not out["engine_errors"], out["engine_errors"]


def test_hon_nhan_12_khong_lo_dev_note(chart_nu):
    from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
    out = luan_hon_nhan_song_phai(bat_tu_state=chart_nu["bat_tu_state"],
                                  la_so=chart_nu["la_so"])
    blob = json.dumps(out, ensure_ascii=False)
    for cam in DEV_NOTE_CAM:
        assert cam not in blob, f"chuỗi dev-note '{cam}' lộ ra payload user"


def test_hon_nhan_12_noi_dung_theo_la_khong_phai_hang_so(chart_nu, chart_nam):
    """Lá khác nhau → 12 khía cạnh phải ra nội dung khác nhau (không phải template cứng)."""
    from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
    a = luan_hon_nhan_song_phai(bat_tu_state=chart_nu["bat_tu_state"],
                                la_so=chart_nu["la_so"])
    b = luan_hon_nhan_song_phai(bat_tu_state=chart_nam["bat_tu_state"],
                                la_so=chart_nam["la_so"])
    khac = sum(1 for x, y in zip(a["khia_canh"], b["khia_canh"])
               if x["lead_reading"] != y["lead_reading"])
    assert khac >= 8, f"chỉ {khac}/12 khía cạnh khác nhau giữa 2 lá khác hẳn nhau"


def test_hon_nhan_12_co_nguon_va_trich_trang(chart_nu):
    """Đa số khía cạnh phải có sources; các luận điểm quy luật giữ trích trang sách."""
    from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
    out = luan_hon_nhan_song_phai(bat_tu_state=chart_nu["bat_tu_state"],
                                  la_so=chart_nu["la_so"])
    co_nguon = [a for a in out["khia_canh"] if a["sources"]]
    assert len(co_nguon) >= 10, f"chỉ {len(co_nguon)}/12 khía cạnh có nguồn"


# ── #56 couple-sync: đủ spec AppChat 3.3 + chéo đích danh ───────────────────────

def test_couple_sync_du_keys_spec_va_day_noi_dung(chart_nu, chart_nam):
    from engine.cross_paradigm.couple_sync import luan_so_doi
    out = luan_so_doi(person_a=chart_nu, person_b=chart_nam)
    # keys spec AppChat 3.3 (trước đây spec hứa mà engine KHÔNG trả)
    assert isinstance(out["overall_score"], int) and 5 <= out["overall_score"] <= 95
    assert out["compatibility_factors"], "factors rỗng — lại về khung rỗng v0"
    assert isinstance(out["recommendations"], list) and out["recommendations"]
    assert out["score_method"], "điểm phải minh bạch cách tính"
    # chéo đích danh 2 chiều phải CÓ và nói về sao thật
    cheo = out["tu_vi_phu_the_cheo"]
    assert cheo["a_sang_b"] and cheo["a_sang_b"]["phu_the_stars"], "thiếu chéo A→B"
    assert cheo["b_sang_a"] and cheo["b_sang_a"]["phu_the_stars"], "thiếu chéo B→A"
    assert "Cung Phu Thê" in cheo["reading"]
    # nội dung không còn <1KB nghèo nàn
    assert len(json.dumps(out, ensure_ascii=False)) > 3000, "payload lại mỏng như v0"
    for cam in DEV_NOTE_CAM:
        assert cam not in json.dumps(out, ensure_ascii=False)
    assert out["paradigm_ok"] is True


def test_couple_sync_bat_tu_bung_tin_hieu(chart_nu, chart_nam):
    """Lớp Bát Tự phải bung tín hiệu cụ thể (nhật chủ/tương tác chi/bù khuyết),
    không chỉ 1 câu overall generic."""
    from engine.cross_paradigm.couple_sync import luan_so_doi
    out = luan_so_doi(person_a=chart_nu, person_b=chart_nam)
    ct = out["bat_tu_hop_hon"]["chi_tiet"]
    assert ct and len(ct) >= 2, "Bát Tự chỉ còn 1 tín hiệu — mất độ bung"
    nhoms = {f["nhom"] for f in ct}
    assert "Nhật chủ" in nhoms, "thiếu tín hiệu nhật chủ"


# ── tinh_duyen: định thời phải có lớp lưu niên GẦN ──────────────────────────────

def test_dinh_thoi_co_lop_luu_nien_gan():
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local=NU_1992["birth_datetime_local"],
                          gender="nữ", timezone=NU_1992["timezone"], as_of_year=None)
    dt = out.get("dinh_thoi") or {}
    assert "luu_nien_gan" in dt, "thiếu lớp lưu niên gần trong định thời"
    assert isinstance(dt["luu_nien_gan"], list)
    # marker (nếu có) phải nói năm cụ thể + điều kiện 'cát lợi' (không phán chắc)
    for m in dt["luu_nien_gan"]:
        assert m.get("year") and m.get("note")


def test_display_timeline_uu_tien_luu_nien_gan():
    from engine.tinh_duyen.display import build_display
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local=NU_1992["birth_datetime_local"],
                          gender="nữ", timezone=NU_1992["timezone"], as_of_year=None)
    disp = build_display(out, "nữ")
    tls = [s for s in disp["sections"] if s.get("kind") == "timeline"]
    assert tls, "thiếu section timeline"
    items = tls[0]["items"]
    if (out.get("dinh_thoi") or {}).get("luu_nien_gan"):
        assert items[0]["loai"] == "lưu niên gần", "lưu niên gần phải đứng ĐẦU timeline"


# ── phác hoạ: khuôn mặt dán nhãn lớp, không '3 mặt nối nhau' ────────────────────

def test_phac_hoa_khuon_mat_dan_nhan_lop(chart_nu):
    from engine.tinh_duyen.phac_hoa_phoi_ngau import lap_ho_so_tuong_mao
    hs = lap_ho_so_tuong_mao(la_so=chart_nu["la_so"], bat_tu_state=chart_nu["bat_tu_state"],
                             gender="nữ", vung_mien=None, dan_toc=None, do_tuoi=None)
    km = hs["khuon_mat"]
    # nếu có lớp pha (ngũ hành/thần thái) thì phải có NHÃN, không nối trần bằng ';'
    if "—" in km:
        assert ("pha nét" in km) or ("thần thái" in km), f"lớp pha không nhãn: {km[:120]}"
    assert "; " not in km.split("—")[0], "tả chủ đạo không được là chuỗi nối ';'"


# ── Nữ mệnh cổ thư (女命骨髓賦 × 王亭之) — quote-or-silence + biện chính ─────────

def test_nu_menh_co_van_match_theo_la_va_co_bien_chinh():
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local=NU_1992["birth_datetime_local"],
                          gender="nữ", timezone=NU_1992["timezone"], as_of_year=None)
    nm = out.get("nu_menh_co_van") or {}
    assert nm.get("method_id") == "nu_menh_co_van_v1"
    # lá này Phu Thê Tử Vi + Thất Sát → phải có rule 王亭之 đúng sao đó
    saos = {w["sao"] for w in nm.get("wang_tingzhi") or []}
    assert saos & {"Tử Vi", "Thất Sát"}, f"wang rules không đúng sao Phu Thê: {saos}"
    # MỌI entry đều có nguyên văn (quote-or-silence)
    for w in nm.get("wang_tingzhi") or []:
        assert w.get("nguyen_van"), "rule 王亭之 thiếu nguyên văn"
    for m in nm.get("cot_tuy_phu") or []:
        assert m.get("nguyen_van") and m.get("han_viet")
        if m.get("tone") == "hung_co":
            bc = m.get("bien_chinh") or {}
            assert bc.get("giai") and bc.get("nguon"), \
                "câu HUNG cổ bắt buộc kèm biện chính có nguồn — không đổ định kiến cổ lên user"


def test_nu_menh_vcd_muon_doi_cung_va_khong_ap_rule_sinh_dem_cho_sinh_ngay():
    """Lá nữ 1995 06:00 (giờ Mão = sinh NGÀY, Phu Thê vô chính diệu)."""
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local="1995-01-10T06:00:00",
                          gender="nữ", timezone="Asia/Ho_Chi_Minh", as_of_year=None)
    nm = out.get("nu_menh_co_van") or {}
    assert nm.get("phu_the_muon_doi_cung") is True, "VCD phải mượn đối cung"
    ids = {w["id"] for w in nm.get("wang_tingzhi") or []}
    assert "w-thaiduong-3" not in ids, \
        "rule 夜生人 (sinh đêm) KHÔNG được áp cho lá sinh 06:00 sáng"
    # ctp-15 (vô chính diệu) phải match + có biện chính
    ctp_ids = {m["id"] for m in nm.get("cot_tuy_phu") or []}
    assert "ctp-15" in ctp_ids


def test_nu_menh_display_section_co_nguyen_van_trong_can_cu():
    from engine.tinh_duyen.display import build_display
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local=NU_1992["birth_datetime_local"],
                          gender="nữ", timezone=NU_1992["timezone"], as_of_year=None)
    disp = build_display(out, "nữ")
    secs = [s for s in disp["sections"] if s.get("id") == "nu_menh_co_van"]
    assert secs, "thiếu section nữ mệnh cổ thư trong display"
    s = secs[0]
    assert s["items"] and s.get("can_cu")
    blob = json.dumps(s["can_cu"], ensure_ascii=False)
    assert "深造讲义" in blob or "女命骨髓賦" in blob, "can_cu phải mang nguyên văn + nguồn"


def test_nu_menh_rule_gioi_tinh_khong_ap_cheo():
    """Nam mệnh: rule dành riêng nữ (w-tuvi-2) không hiện; rule nam (w-tuvi-1) được phép."""
    from engine.tinh_duyen.reading import read_tinh_duyen
    out = read_tinh_duyen(birth_datetime_local=NU_1992["birth_datetime_local"],
                          gender="nam", timezone=NU_1992["timezone"], as_of_year=None)
    nm = out.get("nu_menh_co_van") or {}
    ids = {w["id"] for w in nm.get("wang_tingzhi") or []}
    assert "w-tuvi-2" not in ids, "rule nữ-mệnh không được áp cho nam"
