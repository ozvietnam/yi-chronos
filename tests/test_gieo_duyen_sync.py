"""Bridge Gieo Duyên → /api/sync cho AppChat (2026-06-25).

Kiểm: 7 route đăng ký + core web TÁI DÙNG đúng (Iron #1, không luận lại) +
sub-flow engine import được. Bridge wrapper (service-key + person lookup) test
end-to-end trên prod với tài khoản đã sync (cần DB) — đây test phần luận lõi.
"""
import asyncio


def test_sync_routes_registered():
    from api import sync as S
    paths = {r.path for r in S.router.routes}
    for p in ["/api/sync/duyen", "/api/sync/duyen-tho", "/api/sync/hop-hon",
              "/api/sync/so-sanh-duyen", "/api/sync/tinh-duyen/phac-hoa",
              "/api/sync/tinh-duyen/gieo-que", "/api/sync/tinh-duyen/narrate"]:
        assert p in paths, f"thiếu route {p}"


def test_duyen_core_reused():
    from api.tu_vi_3layer import DuyenInput, duyen_ca_nhan_endpoint
    r = asyncio.run(duyen_ca_nhan_endpoint(
        DuyenInput(birth="1988-06-05T23:30:00", gender="nam")))
    assert "chan_dung_nua_kia" in r and "tuoi_hop" in r and "nam_co_duyen" in r
    assert r.get("chan_dung_nua_kia", {}).get("chinh_tinh")


def test_hop_hon_core_reused():
    from api.tu_vi_3layer import HopHonInput, hop_hon
    r = asyncio.run(hop_hon(HopHonInput(
        birth1="1988-06-05T23:30:00", gender1="nam",
        birth2="1990-03-15T08:00:00", gender2="nữ")))
    assert "diem_tong" in r and isinstance(r["diem_tong"], (int, float))


def test_so_sanh_core_extracted():
    """Tách _so_sanh_duyen_core khỏi route /so-sanh-duyen — dùng chung web + sync."""
    from api.tu_vi_3layer import SoSanhInput, _so_sanh_duyen_core
    r = asyncio.run(_so_sanh_duyen_core(SoSanhInput(
        me={"birth": "1988-06-05T23:30:00", "gender": "nam", "ten": "A"},
        others=[{"birth": "1990-03-15T08:00:00", "gender": "nữ", "ten": "B"}])))
    assert "xep_hang" in r and len(r["xep_hang"]) == 1


def test_gieo_que_deterministic():
    from engine.tinh_duyen.gieo_que_quyet_dinh import gieo_que_tinh_duyen
    q = gieo_que_tinh_duyen("Có nên tiến tới với người này?", [3, 5, 7])
    assert "que_chinh" in q and q.get("bon_buoc")


def test_subflow_engine_imports():
    from engine.cross_paradigm import service as cps
    from engine.cross_paradigm.narrate import narrate_tinh_duyen
    assert hasattr(cps, "run_phac_hoa_phoi_ngau")
    assert hasattr(cps, "run_tinh_duyen")
    assert callable(narrate_tinh_duyen)


# ── Batch 2 (2026-06-25): display.sections[] cho AppChat data-driven renderer ──
_VALID_KINDS = {"cap_do", "qa", "prose_list", "pairs", "timeline", "list",
                "collapsible", "narration", "cta", "cta_gieo_que", "refs"}


def _assert_sections(disp: dict):
    secs = disp["sections"]
    assert secs, "sections rỗng"
    for s in secs:
        assert all(k in s for k in ("id", "icon", "title", "kind")), f"thiếu field: {s}"
        assert s["kind"] in _VALID_KINDS, f"kind lạ (app không render được): {s['kind']}"


def test_display_builders_valid_kinds():
    """Adapter raw → display.sections[] CHỈ dùng kind app hỗ trợ."""
    from api.tu_vi_3layer import (DuyenInput, HopHonInput, SoSanhInput,
                                  _so_sanh_duyen_core, duyen_ca_nhan_endpoint, hop_hon)
    from engine.tinh_duyen.duyen_display import (build_duyen_display, build_gieo_que_display,
                                                 build_hop_hon_display, build_so_sanh_display)
    from engine.tinh_duyen.gieo_que_quyet_dinh import gieo_que_tinh_duyen
    d = asyncio.run(duyen_ca_nhan_endpoint(DuyenInput(birth="1988-06-05T23:30:00", gender="nam")))
    _assert_sections(build_duyen_display(d))
    h = asyncio.run(hop_hon(HopHonInput(birth1="1988-06-05T23:30:00", gender1="nam",
                                        birth2="1990-03-15T08:00:00", gender2="nữ")))
    _assert_sections(build_hop_hon_display(h))
    s = asyncio.run(_so_sanh_duyen_core(SoSanhInput(
        me={"birth": "1988-06-05T23:30:00", "gender": "nam", "ten": "A"},
        others=[{"birth": "1990-03-15T08:00:00", "gender": "nữ", "ten": "B"}])))
    _assert_sections(build_so_sanh_display(s))
    _assert_sections(build_gieo_que_display(gieo_que_tinh_duyen("Có nên?", [3, 5, 7])))


def test_display_action_base_parametrized():
    """CTA URL theo action_base — web /api/cross-paradigm (KHÔNG vỡ), app /api/sync."""
    from engine.tinh_duyen.display import build_display
    ro = {"input": {"gender": "nam"}}
    sync = build_display(ro, "nam", action_base="/api/sync/tinh-duyen")
    web = build_display(ro, "nam")

    def _cta(disp, sid):
        for x in disp["sections"]:
            if x["id"] == sid:
                return x.get("action") or x.get("fetch_action")

    assert _cta(sync, "phac_hoa") == "/api/sync/tinh-duyen/phac-hoa"
    assert _cta(web, "phac_hoa") == "/api/cross-paradigm/tinh-duyen/phac-hoa"
    assert _cta(sync, "gieo_que") == "/api/sync/tinh-duyen/gieo-que"
    assert _cta(sync, "loi_thay") == "/api/sync/tinh-duyen/narrate"


def test_so_sanh_request_accepts_app_shape():
    """Bug app 2026-06-25: so-sanh-duyen nhận `nguoi_khac` (alias) + `birth` object lồng
    (giống partner_birth) → trước bỏ qua/validation-fail → 0 người → thiếu xep_hang.
    Giờ parse đủ người (+ backward-compat `others` + birth chuỗi phẳng)."""
    from api.sync import SoSanhSyncRequest
    req = SoSanhSyncRequest(firebase_uid="x", ten_self="Anh", nguoi_khac=[
        {"birth": {"datetime_local": "1995-06-15 10:30", "gender": "nu",
                   "timezone": "Asia/Ho_Chi_Minh"}, "gender": "nu", "ten": "A"},
        {"birth": {"datetime_local": "1990-03-20 14:00", "gender": "nu"}, "ten": "B"},
    ])
    assert len(req.others) == 2
    assert req.others[0].birth.datetime_local == "1995-06-15 10:30"
    assert req.others[0].birth.gender == "nu"
    r2 = SoSanhSyncRequest(firebase_uid="x", others=[
        {"birth": "1995-06-15 10:30", "gender": "nu", "ten": "A"}])
    assert len(r2.others) == 1 and r2.others[0].birth.datetime_local == "1995-06-15 10:30"
