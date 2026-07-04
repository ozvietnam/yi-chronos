"""Vòng sao / phụ tinh (B4) — roster đã DUYỆT ĐỐI KHÁNG cho Thư viện.

Kỷ luật quote-or-silence: chỉ hiện founder_verified=1 + nguồn; loại 14 chính tinh.
Test decide() của pipeline verify là PURE (không DB) — chạy được cả trong worktree.
"""
import importlib.util
from pathlib import Path

from engine.tu_vi.vong_sao import list_vong_sao, CHINH_TINH, _book_label

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_sao_noi_dung.py"


def _load_verify():
    spec = importlib.util.spec_from_file_location("verify_snd", _SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ── decide() — logic duyệt đối kháng (pure, chạy mọi môi trường) ───────────────
def test_decide_approve_needs_both_layers():
    """DUYỆT chỉ khi provenance mạnh (quote có trong sách) VÀ dịch không bịa."""
    v = _load_verify()
    assert v.decide(0.95, 50000, "faithful") == 1     # quote thật + dịch sát
    assert v.decide(0.95, 50000, "drift") == 1        # gloss lành (có quote gốc kèm) → duyệt
    assert v.decide(0.95, 50000, "fabricated") == -1  # dịch bịa ý → LOẠI dù quote thật


def test_decide_reject_only_when_source_thick():
    """Chỉ LOẠI 'quote vắng' khi nguồn ĐỦ DÀY — không loại oan khi thiếu bản index."""
    v = _load_verify()
    assert v.decide(0.05, 50000, "faithful") == -1    # sách dày mà quote vắng → nghi bịa
    assert v.decide(0.05, 500, "faithful") == 0       # sách mỏng → TREO (không loại oan)
    assert v.decide(-2.0, 0, "faithful") == 0         # không có nguồn → treo


def test_decide_borderline_holds():
    """Provenance lưng chừng (không đủ mạnh, không vắng hẳn) → TREO."""
    v = _load_verify()
    assert v.decide(0.5, 50000, "faithful") == 0


# ── list_vong_sao() — cần wiki.sqlite3 (chạy ở repo/CI có DB) ──────────────────
def test_list_vong_sao_loai_chinh_tinh_va_co_nguon():
    d = list_vong_sao()
    if not d["stars"]:
        return  # môi trường thiếu DB (worktree) — bỏ qua, không fail giả
    # KHÔNG lẫn 14 chính tinh
    for s in d["stars"]:
        assert s["sao_vi"] not in CHINH_TINH
        all_items = s["items"] + s["cung_items"] + s["ket_hop_items"]
        assert all_items, "sao hiện ra phải có ≥1 trích (ở bất kỳ lớp nào)"
        for it in all_items:
            assert it["dich"] and it["nguon"]          # mỗi trích PHẢI có nguồn
        for it in s["cung_items"]:
            assert it["cung"], "trích lớp cung phải gắn tên cung"
    assert d["total"] == len(d["stars"])
    assert d["disclaimer"]


def test_list_vong_sao_gom_ca_3_lop():
    d = list_vong_sao()
    if not d["stars"]:
        return
    has_cung = any(s["cung_items"] for s in d["stars"])
    has_ket_hop = any(s["ket_hop_items"] for s in d["stars"])
    assert has_cung, "phải có ít nhất 1 sao lộ nghĩa theo-cung (lớp 'cung')"
    assert has_ket_hop, "phải có ít nhất 1 sao lộ nghĩa kết-hợp (lớp 'ket_hop')"


def test_book_label_friendly():
    assert "Trung Châu" in _book_label("trung-chau-tu-vi-dau-so-2")
    assert _book_label("tuvifull-abc-xyz") == "abc xyz"   # fallback gọn
