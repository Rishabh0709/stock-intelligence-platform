"""Cross-platform Phase 1 quality gate.

Run from the project root:
    python scripts/quality_gate.py
"""

from __future__ import annotations

import compileall
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    compiled = all(
        compileall.compile_dir(PROJECT_ROOT / directory, quiet=1, force=True)
        for directory in ("src", "dashboard", "migrations", "scripts")
    )
    if not compiled:
        print("FAILED: source compilation")
        return 1

    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-t",
        ".",
        "-v",
    ]
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode:
        return result.returncode

    print("PASS: compilation and complete isolated test suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
