"""#2 AppChat — luận từng cung theo sao (free) + endpoints sync gated."""
from fastapi.testclient import TestClient

from api.main import app


def test_per_cung_mentions_actual_stars():
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.per_cung_reading import per_cung_star_reading
    ls = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00",
                               timezone="Asia/Ho_Chi_Minh", gender="nam")
    r = per_cung_star_reading(ls)
    assert len(r) == 12
    menh = next((c for c in r if c["cung"] == "Mệnh"), None)
    assert menh and "Thiên Tướng" in menh["luan_sao"]   # luận NHẮC sao thực tế, không chung chung
    assert all("cung" in c and "luan_sao" in c for c in r)


def test_per_cung_endpoint_service_gated():
    c = TestClient(app)
    assert c.get("/api/sync/tu-vi/per-cung?firebase_uid=x").status_code in (401, 403, 503)


def test_transactions_endpoint_service_gated():
    c = TestClient(app)
    assert c.get("/api/sync/wallet/x/transactions").status_code in (401, 403, 503)
