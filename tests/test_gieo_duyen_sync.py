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
