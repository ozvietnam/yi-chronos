"""Store phản hồi user — vòng tự học (Anh chốt 2026-06-15 'lưu để biết đúng sai + khẩu vị').

Gia vị (phái mỏng) → câu hỏi → user trả lời Đúng/Chưa/Không + kể trải nghiệm.
Lưu lại để: (1) validate lá số, (2) học khẩu vị user, (3) món sau nấu chính xác hơn.

⚠ PRIVACY (Iron Rule + memory privacy_auth_persons_gate): đây là DỮ LIỆU CÁ NHÂN.
Mọi đọc/ghi PHẢI gắn user_id và endpoint PHẢI gate self-or-owner — không lộ chéo.
DB riêng, gitignored.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = PROJECT_ROOT / "data" / "tu_vi"
DB_PATH = DB_DIR / "user_feedback.sqlite3"

ANSWERS = {"dung", "chua", "khong"}  # Đúng / Chưa rõ / Không


def _conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            chu_de TEXT,
            atom_id INTEGER,
            sao TEXT,
            cau_hoi TEXT,
            answer TEXT,
            free_text TEXT,
            created_at INTEGER NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fb_user ON user_feedback(user_id)")
    conn.commit()
    return conn


def save_feedback(user_id: str, chu_de: str | None, atom_id: int | None,
                  sao: str | None, cau_hoi: str | None,
                  answer: str | None, free_text: str | None) -> int:
    """Lưu 1 phản hồi. answer ∈ {dung,chua,khong} hoặc None (chỉ kể trải nghiệm)."""
    if not user_id:
        raise ValueError("save_feedback yêu cầu user_id (privacy)")
    if answer and answer not in ANSWERS:
        answer = None
    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO user_feedback (user_id, chu_de, atom_id, sao, cau_hoi, answer, free_text, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, chu_de, atom_id, sao, cau_hoi, answer, free_text, int(time.time())))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_feedback(user_id: str) -> list[dict]:
    """Toàn bộ phản hồi của 1 user (mới nhất trước)."""
    if not user_id:
        return []
    conn = _conn()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM user_feedback WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def validated_atoms(user_id: str) -> dict[int, str]:
    """atom_id → answer mới nhất ({dung/chua/khong}) — để món sau điều chỉnh trọng số."""
    out: dict[int, str] = {}
    for fb in get_feedback(user_id):  # đã sort mới-trước
        aid = fb.get("atom_id")
        if aid is not None and aid not in out and fb.get("answer"):
            out[aid] = fb["answer"]
    return out


def khau_vi(user_id: str) -> dict:
    """Tóm tắt khẩu vị: user quan tâm/đồng tình mảng nào, kể gì.

    Returns: {chu_de_counts, dung_count, khong_count, trai_nghiem: [free_text...]}
    """
    fbs = get_feedback(user_id)
    chu_de_counts: dict[str, int] = {}
    dung = khong = 0
    trai_nghiem = []
    for fb in fbs:
        cd = fb.get("chu_de")
        if cd:
            chu_de_counts[cd] = chu_de_counts.get(cd, 0) + 1
        if fb.get("answer") == "dung":
            dung += 1
        elif fb.get("answer") == "khong":
            khong += 1
        if fb.get("free_text"):
            trai_nghiem.append(fb["free_text"])
    return {"chu_de_counts": chu_de_counts, "dung_count": dung,
            "khong_count": khong, "trai_nghiem": trai_nghiem[:20],
            "tong_phan_hoi": len(fbs)}
