"""Wire API gieo quẻ tình duyên: route đăng ký + endpoint gọi engine trả quẻ +
paradigm-safe (Iron #4 — đọc đồng dạng, KHÔNG cát/hung).

Test ở tầng API: override require_caller (không cần session/key thật) → kiểm tra
endpoint gọi engine.tinh_duyen.gieo_que_quyet_dinh.gieo_que_tinh_duyen và KHÔNG
charge xu (không đụng ví). Engine deterministic nên gọi thật được, không mock.
"""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from api.cross_paradigm import router as cp_router
from api.service_auth import require_caller


def _client() -> TestClient:
    """App tối giản chỉ mount cross_paradigm router + override auth (caller giả)."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(cp_router)
    app.dependency_overrides[require_caller] = lambda: {
        "source": "session", "user_id": "1", "is_owner": False,
    }
    return TestClient(app)


# ── 1) Route đăng ký ─────────────────────────────────────────────────────────
def test_route_gieo_que_dang_ky():
    paths = {r.path for r in cp_router.routes}
    assert "/api/cross-paradigm/tinh-duyen/gieo-que" in paths


# ── 2) Gọi trả quẻ ───────────────────────────────────────────────────────────
def test_gieo_que_tra_que_seed():
    c = _client()
    r = c.post("/api/cross-paradigm/tinh-duyen/gieo-que",
               json={"cau_hoi": "tôi có nên tiến tới với người này không",
                     "seed_numbers": [7, 3, 5]})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["method_id"] == "mai_hoa_tinh_duyen_quyet_dinh_v1"
    # Đủ cấu trúc quẻ + khung 4 bước (đọc đồng dạng).
    for k in ("que_chinh", "que_ho", "que_bien", "the_dung", "bon_buoc",
              "can_hoi_them", "tam_phap"):
        assert k in out, f"thiếu block {k}"
    assert out["que_chinh"]["ten_que"], "phải có tên quẻ chính"
    assert 1 <= out["hao_dong"] <= 6
    # Bước 3 + 4 phải HỎI THÊM user (ngoại ứng + tư thế).
    assert len(out["can_hoi_them"]) == 2


def test_gieo_que_thieu_cau_hoi_422():
    c = _client()
    r = c.post("/api/cross-paradigm/tinh-duyen/gieo-que",
               json={"cau_hoi": "   "})
    assert r.status_code == 422


def test_gieo_que_khong_seed_lap_theo_thoi_gian():
    c = _client()
    r = c.post("/api/cross-paradigm/tinh-duyen/gieo-que",
               json={"cau_hoi": "duyên này nên giữ hay buông"})
    assert r.status_code == 200, r.text
    assert r.json()["lap_que"]["phep"].startswith("thời-gian")


# ── 3) Paradigm KHÔNG cát/hung (Iron #4) ─────────────────────────────────────
def test_gieo_que_paradigm_khong_cat_hung():
    c = _client()
    r = c.post("/api/cross-paradigm/tinh-duyen/gieo-que",
               json={"cau_hoi": "tôi có nên cưới người này không",
                     "seed_numbers": [1, 2]})
    assert r.status_code == 200, r.text
    out = r.json()
    # Bỏ cau_hoi (input user echo) — chỉ soi TEXT engine SINH RA.
    out_no_q = {k: v for k, v in out.items() if k != "cau_hoi"}
    blob = json.dumps(out_no_q, ensure_ascii=False).lower()
    # KHÔNG predict / KHÔNG phán cát-hung-thắng-bại trong output máy.
    for cam in ("dự đoán", "sẽ thành", "sẽ bại", "điềm tốt", "điềm xấu",
                "chắc chắn cưới", "không nên cưới", "nên cưới"):
        assert cam not in blob, f"output rò ngôn ngữ predict cấm: '{cam}'"
    # PHẢI có khung paradigm đọc đồng dạng (Iron #4).
    assert "_paradigm" in out and "predict" in out["_paradigm"].lower()
    assert "đồng dạng" in blob, "output phải nhắc paradigm đọc đồng dạng"
    assert out["the_dung"].get("doc_dong_dang"), "Thể-Dụng phải reframe đọc đồng dạng"
