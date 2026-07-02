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
