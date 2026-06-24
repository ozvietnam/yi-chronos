"""Lớp dịch vụ cho orchestrator liên-phái (#55 hôn nhân song phái + #56 so đôi).

Nối engine LÕI (`hon_nhan_song_phai`, `couple_sync` — đã test với mock) vào hạ tầng
thật: dựng chart từ giờ sinh (tái dùng `cast_bat_tu` + `cast_la_so_from_birth`,
KHÔNG cast lại tay), TRỪ 30 XU qua ví TRUNG TÂM (`engine.xu_wallet`), cache "một việc
một lần" (Iron #4 — cùng input trong TTL → KHÔNG trừ lại), HOÀN xu khi engine lỗi.

Giá 30 xu/lượt — Anh chốt (#55 cmt 2026-06-19, #56). Mọi cộng/trừ xu THẬT nằm ở ví
trung tâm để không double-charge giữa AppChat ↔ web (xu_wallet docstring).
"""
from __future__ import annotations

import json as _json
import time
from typing import Any, Callable, Optional

from sqlalchemy import text

from engine import xu_wallet
from engine.db import session_scope

GIA_XU = 30  # giá đã chốt (#55/#56) — luận liên-phái sâu
GIA_XU_PHAC_HOA = 50  # phác hoạ chân dung phối ngẫu — GEN ẢNH tốn tiền THẬT → giá cao hơn
CACHE_TTL_SEC = 86400  # "một việc một lần" (Iron #4): cùng input/ngày → trả lại cũ


# ── dựng chart từ giờ sinh (tái dùng engine cast — KHÔNG tính tay) ────────────

def _chart_of(person: dict) -> dict:
    """person {birth_datetime_local, gender, timezone} → {bat_tu_state, la_so}.

    Resilient: 1 phái cast lỗi → phái đó None (engine LÕI tự hạ xuống unsourced/
    một_phía, KHÔNG sập — đã test). Caller phải đã validate có giờ sinh."""
    birth = person.get("birth_datetime_local")
    gender = person.get("gender") or "nam"
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    out: dict = {"bat_tu_state": None, "la_so": None}
    try:
        from engine.bat_tu.cast import cast_bat_tu
        out["bat_tu_state"] = cast_bat_tu(
            birth_datetime_local=birth, timezone=tz, gender=gender)
    except Exception:
        pass
    try:
        from engine.tu_vi.from_birth import cast_la_so_from_birth
        out["la_so"] = cast_la_so_from_birth(
            birth_datetime_local=birth, timezone=tz, gender=gender)
    except Exception:
        pass
    return out


# ── cache "một việc một lần" (Iron #4) — tái dùng user_castings, KHÔNG bảng mới ─

def _cached(uid: int, method: str, sig: str, ttl: int = CACHE_TTL_SEC):
    """(casting_id, result) nếu cùng (user, method, chữ ký input) trong TTL, else (None, None).

    Tự vô hiệu khi knowledge_version bump (sách/lăng kính mới) — như hermes_service."""
    cutoff = int(time.time()) - ttl
    try:
        from engine.system_meta import knowledge_version_updated_at
        cutoff = max(cutoff, knowledge_version_updated_at())
    except Exception:
        pass
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("""SELECT id, result_json FROM user_castings
                    WHERE user_id=:u AND method=:m AND question=:q AND created_at>=:c
                    ORDER BY id DESC LIMIT 1"""),
            {"u": uid, "m": method, "q": sig[:500], "c": cutoff},
        ).fetchone()
    if not row:
        return None, None
    rj = row[1]
    data = rj if isinstance(rj, (dict, list)) else (_json.loads(rj) if rj else {})
    return row[0], data


def _save(uid: int, method: str, sig: str, result: dict) -> Optional[int]:
    """Lưu vào lịch sử (user_castings) — vừa là cache, vừa là H1/H2 history."""
    from engine.algo_version import algo_version
    av = algo_version(method)
    with session_scope(service=True) as conn:
        return conn.execute(
            text("""INSERT INTO user_castings
                    (user_id, method, question, result_json, verdict, algo_version, created_at)
                    VALUES (:u,:m,:q,:r,:v,:av,:now) RETURNING id"""),
            {"u": uid, "m": method, "q": sig[:500],
             "r": _json.dumps(result, ensure_ascii=False),
             "v": "paradigm_ok" if result.get("paradigm_ok", True) else "paradigm_flag",
             "av": av, "now": int(time.time())},
        ).scalar()


def _charge_and_run(uid: int, method: str, sig: str,
                    run_fn: Callable[[], dict],
                    gia_xu: int = GIA_XU) -> dict[str, Any]:
    """Cache → (miss) trừ `gia_xu` → chạy engine → lưu. Hoàn xu nếu engine lỗi.

    Trả dict result của engine + {charged_xu, xu_balance, cached, casting_id}.
    Thiếu xu → {status:'insufficient_xu', need, have, gia_xu} (caller mời nạp)."""
    cid, cached = _cached(uid, method, sig)
    if cached is not None:
        cached = dict(cached)
        cached.update({"cached": True, "charged_xu": 0, "casting_id": cid,
                       "gia_xu": gia_xu})
        return cached

    r = xu_wallet.spend(uid, gia_xu, f"cross_paradigm_{method}")
    if not r["ok"]:
        return {"status": "insufficient_xu", "need": r["need"], "have": r["have"],
                "gia_xu": gia_xu}

    try:
        result = run_fn()
    except Exception:
        # Engine lỗi sau khi đã trừ → HOÀN xu (tiền: không nuốt — xu_wallet docstring).
        xu_wallet.grant(uid, gia_xu, f"refund_cross_paradigm_{method}")
        raise

    result = dict(result)
    casting_id = _save(uid, method, sig, result)
    result.update({"cached": False, "charged_xu": gia_xu, "xu_balance": r["balance"],
                   "casting_id": casting_id, "gia_xu": gia_xu})
    return result


# ── entry points: #55 (1 lá, 12 khía cạnh) + #56 (2 lá, so đôi) ───────────────

def run_hon_nhan_song_phai(uid: int, person: dict) -> dict[str, Any]:
    """#55 — hợp nhất Bát Tự↔Tử Vi cho MỘT lá (12 khía cạnh). Trừ 30 xu (cache Iron #4)."""
    from engine.cross_paradigm.hon_nhan_song_phai import luan_hon_nhan_song_phai
    chart = _chart_of(person)
    sig = f"hon_nhan_song_phai:{person.get('birth_datetime_local')}:{person.get('gender')}"
    return _charge_and_run(
        uid, "cross_paradigm_hon_nhan", sig,
        lambda: luan_hon_nhan_song_phai(
            bat_tu_state=chart["bat_tu_state"], la_so=chart["la_so"]),
    )


def run_tinh_duyen(uid: int, person: dict) -> dict[str, Any]:
    """Xem TÌNH DUYÊN nữ mệnh (engine làm giàu từ kho 6 JSON). Trừ 30 xu (cache Iron #4).

    Tối ưu cho NỮ mệnh; nếu gender không phải nữ vẫn chạy nhưng gắn note. KHÔNG cast
    tay (read_tinh_duyen tự lập lá số + bát tự). Caller phải đã validate có giờ sinh."""
    from engine.tinh_duyen.reading import read_tinh_duyen
    birth = person.get("birth_datetime_local")
    gender = person.get("gender") or "nữ"
    tz = person.get("timezone") or "Asia/Ho_Chi_Minh"
    sig = f"tinh_duyen:{birth}:{gender}"
    note = None if (gender or "").strip().lower() in ("nữ", "nu", "female", "f", "") \
        else "Engine tối ưu cho NỮ mệnh — kết quả với giới tính khác chỉ tham khảo."
    out = _charge_and_run(
        uid, "cross_paradigm_tinh_duyen", sig,
        lambda: read_tinh_duyen(
            birth_datetime_local=birth,
            gender=gender,
            timezone=tz,
            as_of_year=None,
        ),
    )
    if note and out.get("status") != "insufficient_xu":
        out["nu_menh_note"] = note
    return out


def run_phac_hoa_phoi_ngau(uid: int, person: dict,
                           vung_mien: Optional[str] = None,
                           dan_toc: Optional[str] = None,
                           do_tuoi: Optional[str] = None,
                           gen_anh: bool = True) -> dict[str, Any]:
    """Phác hoạ CHÂN DUNG BIỂU TƯỢNG người phối ngẫu (đọc đồng dạng — Iron #4/#6/#8).

    Trừ 50 xu (gen ảnh tốn tiền THẬT). Cache "một việc một lần" (Iron #4). Hồ sơ luôn
    grounded vào bảng #4 + 形性赋; ảnh là graceful (không key → image_b64=None + note).
    """
    from engine.tinh_duyen.phac_hoa_phoi_ngau import (
        lap_ho_so_tuong_mao, build_prompt_anh, ve_anh_phoi_ngau)
    chart = _chart_of(person)
    gender = person.get("gender") or "nữ"
    sig = (f"phac_hoa:{person.get('birth_datetime_local')}:{gender}"
           f":{vung_mien or ''}:{dan_toc or ''}:{do_tuoi or ''}")

    def _run() -> dict:
        ho_so = lap_ho_so_tuong_mao(
            la_so=chart["la_so"], bat_tu_state=chart["bat_tu_state"],
            gender=gender, vung_mien=vung_mien, dan_toc=dan_toc, do_tuoi=do_tuoi)
        prompt = build_prompt_anh(ho_so, vung_mien, dan_toc, do_tuoi)
        anh = (ve_anh_phoi_ngau(ho_so, vung_mien, dan_toc, do_tuoi, prompt=prompt)
               if gen_anh else {"image_b64": None, "image_path": None,
                                "note": "không yêu cầu tạo ảnh"})
        return {
            "method_id": "phac_hoa_phoi_ngau_v1",
            "paradigm_ok": True,
            "ho_so": ho_so,
            "prompt": prompt,
            "image_b64": anh.get("image_b64"),
            "image_path": anh.get("image_path"),
            "image_note": anh.get("note"),
            "disclaimer": ho_so["_disclaimer"],
        }

    return _charge_and_run(
        uid, "cross_paradigm_phac_hoa", sig, _run, gia_xu=GIA_XU_PHAC_HOA)


def run_couple_sync(uid: int, person_a: dict, person_b: dict) -> dict[str, Any]:
    """#56 — so đôi đích danh 2 lá (Bát Tự hợp hôn + Tử Vi Phu Thê chéo). Trừ 30 xu."""
    from engine.cross_paradigm.couple_sync import luan_so_doi
    chart_a = _chart_of(person_a)
    chart_b = _chart_of(person_b)
    sig = (f"couple_sync:{person_a.get('birth_datetime_local')}:{person_a.get('gender')}"
           f"|{person_b.get('birth_datetime_local')}:{person_b.get('gender')}")
    return _charge_and_run(
        uid, "cross_paradigm_couple_sync", sig,
        lambda: luan_so_doi(person_a=chart_a, person_b=chart_b),
    )
