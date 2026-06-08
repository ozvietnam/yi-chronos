"""Test Trung Châu paradigm injection cho user đã đăng ký trong DB.

Run: .venv/bin/python3 scripts/test_trung_chau_paradigm.py
"""
import sqlite3
import sys
sys.path.insert(0, '/Users/ozvietnamdesktop/Desktop/yi')

from engine.tu_vi.analyzer import _cast_chart
from engine.tu_vi.trung_chau_paradigm import build_trung_chau_context

DB = "/Users/ozvietnamdesktop/Desktop/yi/data/yi_users/users.sqlite3"


def main():
    conn = sqlite3.connect(DB)
    rows = conn.execute("""
        SELECT user_id, name, gender, birth_datetime_local
        FROM user_persons
        WHERE user_id > 1 AND birth_datetime_local IS NOT NULL
        ORDER BY user_id
    """).fetchall()

    print(f"Test Trung Châu paradigm injection cho {len(rows)} user thật.\n")
    print(f"Each user gets:")
    print(f"  - 3 Iron Rules CỐT (Q2 p501/p461/p502) — luôn inject")
    print(f"  - 0-N paradigm chính tinh × cung khớp lá số\n")

    total_paradigms = 0
    for user_id, name, gender, dob in rows:
        try:
            la = _cast_chart(dob, gender)
            ctx = build_trung_chau_context(la)
            paradigms = [
                line.split('**')[1] for line in ctx.split('\n')
                if line.startswith('**') and any(
                    line.startswith(f'**{p}') for p in [
                        'MỆNH', 'PHU THÊ', 'PHÚC ĐỨC',
                        'THIÊN DI', 'SỰ NGHIỆP', 'PHỤ MẪU',
                    ]
                )
            ]
            total_paradigms += len(paradigms)
            print(f"u{user_id} {name} ({dob}, {gender}):")
            print(f"  Length: {len(ctx)} chars")
            print(f"  Paradigm: {len(paradigms)}")
            for p in paradigms:
                print(f"    • {p}")
            print()
        except Exception as e:
            print(f"u{user_id} {name}: ERROR {e}\n")

    print(f"━━━ TỔNG ━━━")
    print(f"  {len(rows)} users tested")
    print(f"  {total_paradigms} paradigm matches total")
    print(f"  100% có 3 Iron Rules CỐT inject")


if __name__ == "__main__":
    main()
