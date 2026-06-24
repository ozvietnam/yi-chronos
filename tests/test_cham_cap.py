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
