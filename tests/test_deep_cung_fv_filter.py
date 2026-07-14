"""doc_tien_trinh._pull CHỈ trả nội dung ĐÃ DUYỆT ĐỐI KHÁNG (founder_verified=1).

Đóng lỗ liêm chính route trả phí deep_cung (2026-07-03): trước lọc, route có thể
trưng dòng bịa (fv=-1). Sau lọc → chỉ dùng nội dung quote-có-trong-sách + dịch-không-bịa.
"""
import sqlite3

from engine.tu_vi.doc_tien_trinh import _pull, _DB_DEFAULT


def _has_db() -> bool:
    try:
        sqlite3.connect(f"file:{_DB_DEFAULT}?mode=ro", uri=True).execute(
            "SELECT 1 FROM sao_noi_dung LIMIT 1")
        return True
    except Exception:
        return False


def test_pull_chi_tra_founder_verified_1():
    """Mọi trích _pull trả về PHẢI ứng với 1 dòng sao_noi_dung founder_verified=1."""
    if not _has_db():
        return  # môi trường thiếu DB
    conn = sqlite3.connect(f"file:{_DB_DEFAULT}?mode=ro", uri=True)
    cur = conn.cursor()
    # lấy vài sao có cả dòng verified và dòng bị loại để test có ý nghĩa
    saos = [r[0] for r in conn.execute(
        "SELECT DISTINCT sao_vi FROM sao_noi_dung WHERE lop='def' AND founder_verified=1 LIMIT 12")]
    assert saos, "phải có sao verified để test"
    checked = 0
    for sao in saos:
        for item in _pull(cur, sao, "def"):
            # dich trả về phải khớp 1 dòng fv=1 (KHÔNG phải fv=-1/0)
            fv = conn.execute(
                "SELECT founder_verified FROM sao_noi_dung "
                "WHERE sao_vi=? AND lop='def' AND dich_thuan_viet=? LIMIT 1",
                (sao, item["dich"])).fetchone()
            assert fv is not None and fv[0] == 1, f"{sao}: _pull trả dòng fv={fv}"
            checked += 1
    assert checked > 0, "phải kiểm được ít nhất 1 trích"


def test_pull_bo_qua_sao_chi_co_dong_bi_loai():
    """Sao chỉ toàn dòng fv!=1 → _pull trả [] (không rò dòng bịa/treo)."""
    if not _has_db():
        return
    conn = sqlite3.connect(f"file:{_DB_DEFAULT}?mode=ro", uri=True)
    cur = conn.cursor()
    # tìm 1 sao def mà KHÔNG có dòng verified nào (nếu có)
    row = conn.execute(
        """SELECT sao_vi FROM sao_noi_dung WHERE lop='def' AND dich_thuan_viet!=''
           GROUP BY sao_vi HAVING SUM(founder_verified=1)=0 LIMIT 1""").fetchone()
    if not row:
        return  # mọi sao đều có ≥1 verified — không có ca này để test, bỏ qua
    assert _pull(cur, row[0], "def") == []
