from __future__ import annotations

import os
import pathlib
import sys


def ensure_local_python() -> None:
    script_dir = pathlib.Path(__file__).resolve().parent
    venv_python = script_dir / ".venv" / "bin" / "python"

    if not venv_python.exists():
        return

    current = pathlib.Path(sys.executable).resolve()
    target = venv_python.resolve()
    if current == target:
        return

    os.execv(str(target), [str(target), *sys.argv])
