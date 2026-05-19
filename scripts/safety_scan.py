from __future__ import annotations

from pathlib import Path

BANNED_PHRASES = [
    "định mệnh",
    "dinh menh",
    "hung/cát",
    "hung cat",
    "bệnh chắc chắn",
    "benh chac chan",
    "tai họa",
    "tai hoa",
    "chẩn đoán",
    "chan doan",
]

SCAN_ROOTS = [Path("api"), Path("core"), Path("engine"), Path("collectors"), Path("client/webapp/src")]
EXTENSIONS = {".py", ".vue", ".js", ".ts", ".css", ".html", ".md"}


def main() -> int:
    failures: list[str] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in EXTENSIONS or not path.is_file():
                continue
            text = path.read_text(errors="ignore").lower()
            for phrase in BANNED_PHRASES:
                if phrase in text:
                    failures.append(f"{path}: {phrase}")
    if failures:
        print("Banned copy found:")
        print("\n".join(failures))
        return 1
    print("Safety scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

