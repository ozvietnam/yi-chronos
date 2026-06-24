"""Tests cho engine.tinh_duyen.cham_cap — CHẤM CẤP ĐỘ thử thách hôn nhân (nữ mệnh).

Kiểm: schema chuẩn + cấp 1-5 hợp lệ + tín hiệu THẬT (không bịa) + lộ trình theo cấp
+ nguyên tắc vàng đính kèm + grounding _nguon + PARADIGM (ngôn ngữ XÂY DỰNG, KHÔNG
lời-phán-vào-người) + tích hợp vào read_tinh_duyen (key 'chan_doan_cap_do').
"""
from __future__ import annotations

import json

import pytest

from engine.bat_tu.cast import cast_bat_tu
from engine.tinh_duyen.cham_cap import METHOD_ID, cham_cap_do
from engine.tinh_duyen.quy_trinh import build_quy_trinh_day_du
from engine.tu_vi.from_birth import cast_la_so_from_birth

# 5 lá NỮ trải tuổi / cấu trúc khác nhau.
_BIRTHS = [
    "1988-06-05T23:30",
    "2009-05-10T08:00",
    "1985-11-02T10:00",
    "1995-07-07T06:00",
    "1990-08-20T14:00",
]

# Cụm lời-PHÁN-VÀO-NGƯỜI TUYỆT ĐỐI cấm trong output chấm cấp (paradigm).
_FORBIDDEN_PERSON = (
    "em sẽ khắc chồng", "số cô quả", "chắc chắn ly hôn", "số em khắc",
    "sẽ không lấy được chồng", "chắc chắn khổ", "số em là",
)

_REQUIRED_KEYS = {
    "method_id", "gender", "cap_do", "ten_cap", "muc_do_thu_thach",
    "do_thay_doi_duoc", "phan_loai", "tin_hieu_kich_hoat", "lo_trinh",
    "nguyen_tac_vang", "_nguon",
}


def _run(birth: str) -> dict:
    ls = cast_la_so_from_birth(
        birth_datetime_local=birth, timezone="Asia/Ho_Chi_Minh", gender="nữ")
    bt = cast_bat_tu(
        birth_datetime_local=birth, timezone="Asia/Ho_Chi_Minh", gender="nữ")
    qt = build_quy_trinh_day_du(la_so=ls, bat_tu_state=bt, gender="nữ", as_of_year=2026)
    return cham_cap_do(qt, ls, bt, gender="nữ")


@pytest.fixture(params=_BIRTHS)
def res(request):
    return _run(request.param), request.param


# --------------------------------------------------------------------------- #
def test_method_id(res):
    r, _ = res
    assert r["method_id"] == METHOD_ID == "cham_cap_do_nu_menh_v1"


def test_schema_du_khoa(res):
    r, birth = res
    assert _REQUIRED_KEYS.issubset(r.keys()), \
        f"{birth}: thiếu khóa {_REQUIRED_KEYS - set(r.keys())}"


def test_cap_do_trong_1_5(res):
    r, birth = res
    assert 1 <= r["cap_do"] <= 5, f"{birth}: cap_do ngoài [1,5]: {r['cap_do']}"
    assert r["ten_cap"], f"{birth}: ten_cap rỗng"
    assert r["muc_do_thu_thach"].endswith("/5")


def test_tin_hieu_kich_hoat_la_list(res):
    r, birth = res
    assert isinstance(r["tin_hieu_kich_hoat"], list)
    # Mỗi tín hiệu phải là string mô tả YẾU TỐ thật (không rỗng).
    for t in r["tin_hieu_kich_hoat"]:
        assert isinstance(t, str) and t.strip(), f"{birth}: tín hiệu rỗng"


def test_lo_trinh_co_hanh_dong_cu_the(res):
    r, birth = res
    assert isinstance(r["lo_trinh"], list) and r["lo_trinh"], \
        f"{birth}: lộ trình rỗng — phải có hành động cụ thể"
    for b in r["lo_trinh"]:
        assert isinstance(b, str) and b.strip()


def test_nguyen_tac_vang_dinh_kem(res):
    """nguyen_tac_vang BẮT BUỘC đính kèm (TIỀM NĂNG, không phải án)."""
    r, birth = res
    nv = r["nguyen_tac_vang"]
    assert isinstance(nv, dict) and nv.get("tuyen_bo"), f"{birth}: thiếu nguyen_tac_vang"
    assert "động từ" in nv["tuyen_bo"].lower()


def test_nguon_grounded(res):
    r, birth = res
    assert r["_nguon"], f"{birth}: thiếu _nguon (grounding)"


def test_phan_loai_hop_le(res):
    r, _ = res
    assert r["phan_loai"] in {"rèn được", "rèn + chọn khôn", "chọn khôn là chính"}


# --------------------------------------------------------------------------- #
# PARADIGM — ngôn ngữ XÂY DỰNG, KHÔNG lời-phán-vào-người
# --------------------------------------------------------------------------- #
def test_khong_loi_phan_vao_nguoi(res):
    """Lời-PHÁN-VÀO-NGƯỜI chỉ được phép xuất hiện trong KHUNG BIỆN-CHÍNH (nguyên tắc
    vàng QUOTE chúng để CẤM — Iron Rule #5 'tiếc dê tiếc lễ'); KHÔNG được là verdict trần."""
    from engine.tinh_duyen.reading import _in_prohibition_frame

    r, birth = res

    def walk(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                yield from walk(v)

    for s in walk(r):
        low = s.lower()
        hits = [w for w in _FORBIDDEN_PERSON if w in low]
        if hits:
            assert _in_prohibition_frame(low), \
                f"{birth}: verdict phán-vào-người TRẦN (không biện-chính): {hits} | {s[:120]}"


def test_user_facing_fields_sach_tuyet_doi(res):
    """Các field NGƯỜI ĐỌC THẤY TRỰC TIẾP (tin_hieu_kich_hoat, lo_trinh, ten_cap, mo_ta)
    TUYỆT ĐỐI sạch lời-phán-vào-người (kể cả trong khung biện-chính — đây là lời khuyên
    cho user, không phải meta-guidance cho engine)."""
    r, birth = res
    user_blob = " ".join([
        r.get("ten_cap", ""), r.get("mo_ta", ""),
        " ".join(r.get("tin_hieu_kich_hoat") or []),
        " ".join(r.get("lo_trinh") or []),
    ]).lower()
    hits = [w for w in _FORBIDDEN_PERSON if w in user_blob]
    assert hits == [], f"{birth}: field người-đọc-thấy lọt verdict: {hits}"


def test_duoc_goi_ten_khai_niem_phan_tich(res):
    """Ngôn ngữ XÂY DỰNG: ĐƯỢC gọi tên cấu trúc như khái niệm ('thử thách N/5',
    'cấu trúc', 'áp lực') — đây là điểm phân biệt với fortune-telling."""
    r, _ = res
    blob = json.dumps(r, ensure_ascii=False).lower()
    # 'mức độ thử thách N/5' luôn có (muc_do_thu_thach).
    assert "/5" in r["muc_do_thu_thach"]
    # Có ít nhất một từ khái-niệm-phân-tích trong toàn khối.
    assert any(k in blob for k in ("cấu trúc", "áp lực", "thử thách", "khí "))


# --------------------------------------------------------------------------- #
# Tính phân biệt: lá lành → cấp thấp; lá có Cô Thần đơn lẻ KHÔNG bị thổi lên L4/L5
# --------------------------------------------------------------------------- #
def test_co_than_don_le_khong_thoi_len_cao():
    """1 Cô Thần/Quả Tú đơn lẻ (support) KHÔNG được tự đẩy lên L4/L5 (chống thổi phồng)."""
    r = _run("1995-07-07T06:00")  # lá có Cô Thần đơn lẻ ở cung phối ngẫu
    assert r["cap_do"] <= 3, \
        f"Cô Thần đơn lẻ bị thổi lên cấp {r['cap_do']} (phải ≤3 theo nguyên tắc an toàn)"


def test_la_lanh_ra_cap_thap():
    """Lá có cung Phu Thê đắc + Thương Quan hài hoà → cấp THẤP (1-2)."""
    r = _run("1985-11-02T10:00")
    assert r["cap_do"] <= 2


def test_cap_cao_can_core_signal():
    """KHÔNG lá nào ra L4/L5 mà thiếu tín hiệu CORE cấu trúc (đọc qua _factors)."""
    for birth in _BIRTHS:
        r = _run(birth)
        if r["cap_do"] >= 4:
            f = r["_factors"]
            core_bt = (f["tq_vuong"] and not f["co_che_hoa"] and f["quan_nhuoc"])
            core_tv = (f["pt_so_sat"] >= 1 and f["khoc_hu"]) or (
                f["tu_sat_o_phu_the"] and f["pt_hoa_ky"] and f["pt_so_sat"] >= 2)
            assert core_bt or core_tv, \
                f"{birth}: L{r['cap_do']} nhưng thiếu core signal cấu trúc"


# --------------------------------------------------------------------------- #
# Issue V2 #1 — ĐỐI CHIẾU CHÉO Tử Vi ⇔ Bát Tự (chống thổi phồng khi 2 phái lệch)
# --------------------------------------------------------------------------- #
def test_doi_chieu_cheo_field_co_mat():
    """Mọi kết quả có field doi_chieu_cheo (None nếu không dị biệt, dict nếu hạ cấp)."""
    for birth in _BIRTHS:
        r = _run(birth)
        assert "doi_chieu_cheo" in r, f"{birth}: thiếu field doi_chieu_cheo"
        dc = r["doi_chieu_cheo"]
        assert dc is None or isinstance(dc, dict)


def test_doi_chieu_cheo_ha_cap_khi_2_phai_di_biet():
    """Bát Tự đẩy L4 (TQ vượng-không-chế + Quan nhược) NHƯNG Tử Vi lành rõ → HẠ 1 cấp."""
    from engine.tinh_duyen.cham_cap import _reconcile_cheo
    f = {
        "tq_vuong": True, "tq_cuc_vuong": False, "co_che_hoa": False,
        "quan_nhuoc": True, "quan_cuc_nhuoc": False, "than_vuong": False,
        "thuong_quan": 2.5,
        "pt_co_dac": True, "pt_so_sat": 0, "pt_hoa_ky": False,
        "co_than_qua_tu": [], "khoc_hu": [], "tu_sat_o_phu_the": [],
    }
    new, note = _reconcile_cheo(4, f)
    assert new == 3, "phải hạ L4 → L3 khi Bát Tự nặng nhưng Tử Vi lành rõ"
    assert note and note["phai_day_cap_cao"] == "bat_tu"
    assert note["phai_bao_lanh"] == "tu_vi"
    # _nguon + cap_truoc/sau được cham_cap_do gắn ở tầng tích hợp (không ở helper).


def test_doi_chieu_cheo_tang_tich_hop_gan_nguon_va_cap(monkeypatch):
    """Qua cham_cap_do đầy đủ: dị biệt → cap_do hạ + cờ có _nguon + cap_truoc/sau + bằng chứng."""
    import engine.tinh_duyen.cham_cap as mod
    f_dibiet = {
        "tq_vuong": True, "tq_cuc_vuong": False, "co_che_hoa": False,
        "quan_nhuoc": True, "quan_cuc_nhuoc": False, "than_vuong": False,
        "thuong_quan": 2.5,
        "pt_co_dac": True, "pt_so_sat": 0, "pt_hoa_ky": False,
        "co_than_qua_tu": [], "khoc_hu": [], "tu_sat_o_phu_the": [],
        "pt_chinh_tinh": ["Thiên Tướng"], "sao_phu_the_lanh_dac": ["Thiên Tướng"],
        "pt_sat_tinh": [],
        # các key detector khác cần (không kích hoạt — set rỗng/False).
        "sao_cuong_bien_ham": [], "sao_tinh_cam_ham": [],
    }
    monkeypatch.setattr(mod, "_extract_factors", lambda *a, **k: f_dibiet)
    r = mod.cham_cap_do({}, {}, {}, gender="nữ")
    assert r["cap_do"] == 3, "L4 (BT) + TV lành rõ → hạ về L3"
    dc = r["doi_chieu_cheo"]
    assert dc and dc["cap_truoc_doi_chieu"] == 4 and dc["cap_sau_doi_chieu"] == 3
    assert dc.get("_nguon") and "reconcile" in dc["_nguon"].lower()
    # Vẫn giữ bằng chứng THẬT của cấp gốc (gắn nhãn 'đã hạ cấp').
    assert any("đã hạ" in t for t in r["tin_hieu_kich_hoat"])


def test_doi_chieu_cheo_KHONG_ha_khi_2_phai_hoi_tu():
    """Cả 2 phái cùng nặng (HỘI TỤ) → KHÔNG hạ cấp (kết luận chắc)."""
    from engine.tinh_duyen.cham_cap import _reconcile_cheo
    f = {
        "tq_vuong": True, "tq_cuc_vuong": False, "co_che_hoa": False,
        "quan_nhuoc": True, "quan_cuc_nhuoc": False, "than_vuong": False,
        "thuong_quan": 2.5,
        "pt_co_dac": False, "pt_so_sat": 2, "pt_hoa_ky": False,
        "co_than_qua_tu": [], "khoc_hu": ["Thiên Hư"], "tu_sat_o_phu_the": [],
    }
    new, note = _reconcile_cheo(4, f)
    assert new == 4 and note is None, "hội tụ 2 phái → giữ nguyên cấp"


def test_doi_chieu_cheo_chi_cham_cap_cao():
    """Đối chiếu chéo CHỈ áp cho cấp ≥4 (L1-L3 rèn được, không cần hạ)."""
    from engine.tinh_duyen.cham_cap import _reconcile_cheo
    f = {"tq_vuong": False, "tq_cuc_vuong": False, "co_che_hoa": True,
         "quan_nhuoc": False, "quan_cuc_nhuoc": False, "than_vuong": False,
         "thuong_quan": 1.0, "pt_co_dac": True, "pt_so_sat": 0, "pt_hoa_ky": False,
         "co_than_qua_tu": [], "khoc_hu": [], "tu_sat_o_phu_the": []}
    new, note = _reconcile_cheo(3, f)
    assert new == 3 and note is None


# --------------------------------------------------------------------------- #
# Issue V2 #3 — detector L4 'thân vượng lấn Quan' dùng nhat_chu_tag (factor có sẵn)
# --------------------------------------------------------------------------- #
def test_than_vuong_lan_quan_la_core_L4():
    """nhat_chu strong + Quan nhược + TQ vượng-không-chế → core L4 'thân vượng lấn Quan'."""
    from engine.tinh_duyen.cham_cap import _signals_L4
    f = {"than_vuong": True, "quan_nhuoc": True, "tq_vuong": True, "co_che_hoa": False,
         "thuong_quan": 2.0, "pt_so_sat": 0, "khoc_hu": [], "pt_sat_tinh": [],
         "co_than_qua_tu": [], "pt_hoa_ky": False}
    core, _ = _signals_L4(f)
    assert any("VƯỢNG lấn" in c for c in core), "detector thân-vượng không fire"


def test_than_vuong_nhung_quan_du_manh_KHONG_fire():
    """Thân vượng NHƯNG Quan không nhược → KHÔNG phải lấn (chống bắn rộng)."""
    from engine.tinh_duyen.cham_cap import _signals_L4
    f = {"than_vuong": True, "quan_nhuoc": False, "tq_vuong": True, "co_che_hoa": False,
         "thuong_quan": 2.0, "pt_so_sat": 0, "khoc_hu": [], "pt_sat_tinh": [],
         "co_than_qua_tu": [], "pt_hoa_ky": False}
    core, _ = _signals_L4(f)
    assert not any("VƯỢNG lấn" in c for c in core)


# --------------------------------------------------------------------------- #
# Issue V2 #2 — ngưỡng số học được ghi rõ là QUY ƯỚC ENGINE (không thẩm quyền cổ)
# --------------------------------------------------------------------------- #
def test_nguong_so_hoc_ghi_ro_quy_uoc_engine(res):
    r, birth = res
    nq = r["_factors"].get("_nguong_quy_uoc_engine")
    assert isinstance(nq, dict), f"{birth}: thiếu _nguong_quy_uoc_engine trong _factors"
    assert "quy ước" in nq.get("_ghi_chu", "").lower()
    assert "thẩm quyền cổ" in nq.get("_ghi_chu", "").lower()
    # Mốc số phải lộ ra để truy vết.
    for k in ("thuong_quan_vuong", "thuong_quan_cuc_vuong", "quan_nhuoc_duoi"):
        assert k in nq


def test_nguong_quy_uoc_co_trong_json():
    """JSON cham_cap_do ghi rõ ngưỡng là quy ước engine, _nguon ground khái niệm."""
    from engine.tinh_duyen import knowledge_loader as kb
    data = kb.get("cham_cap_do")
    nq = data["_meta"].get("nguong_so_hoc_la_quy_uoc_engine")
    assert nq and "không phải con số có thẩm quyền cổ" in nq["_mo_ta"].lower()


# --------------------------------------------------------------------------- #
# Tích hợp vào read_tinh_duyen — key 'chan_doan_cap_do' + giữ key cũ
# --------------------------------------------------------------------------- #
def test_tich_hop_vao_read_tinh_duyen():
    from engine.tinh_duyen import read_tinh_duyen
    out = read_tinh_duyen("1988-06-05T23:30", gender="nữ", as_of_year=2026)
    assert "chan_doan_cap_do" in out, "thiếu key chan_doan_cap_do trong read_tinh_duyen"
    cc = out["chan_doan_cap_do"]
    assert 1 <= cc["cap_do"] <= 5
    assert cc["lo_trinh"] and cc["tin_hieu_kich_hoat"] is not None
    # Các key CŨ vẫn còn (không vỡ contract).
    for k in ("quy_trinh_day_du", "cung_phu_the_tuvi", "stage", "personality"):
        assert k in out, f"read_tinh_duyen mất key cũ: {k}"


def test_narrate_prompt_co_cham_cap():
    """system-prompt narrate phải nhúng CHẨN ĐOÁN CẤP ĐỘ + lộ trình."""
    from engine.cross_paradigm.narrate import _build_system_prompt
    from engine.tinh_duyen import read_tinh_duyen
    out = read_tinh_duyen("1988-06-05T23:30", gender="nữ", as_of_year=2026)
    sp = _build_system_prompt({"gender": "nữ"}, out)
    assert "CHẨN ĐOÁN CẤP ĐỘ" in sp
    assert "LỘ TRÌNH" in sp
    assert "mệnh là động từ" in sp.lower()
    # KHÔNG hướng dẫn phán-vào-người (chính prompt cấm các cụm này).
    assert "KHÔNG phán-vào-người" in sp or "không phán-vào-người" in sp.lower()
