from __future__ import annotations

from pathlib import Path
import re


def main() -> int:
    patterns = [
        re.compile(r"sk-[A-Za-z0-9]+"),
        re.compile(r"xoxb-[A-Za-z0-9-]+"),
        re.compile(r"-----BEGIN PRIVATE KEY-----"),
    ]

    root = Path(".")
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix in (".pyc", ".pyo"):
            continue
        if path.name == "secret_scan.py":
            continue
        if path.as_posix().endswith("scripts/verify.ps1"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if pattern.search(text):
                raise SystemExit(f"secret pattern found in {path}")

    print("SECRET_SCAN=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
