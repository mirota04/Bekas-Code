from __future__ import annotations

import os
import pathlib
import sys

VENV_PYTHON_RELATIVE = (".venv", "bin", "python")


def ensure_local_python() -> None:
    script_dir = pathlib.Path(__file__).resolve().parent
    venv_python = script_dir.joinpath(*VENV_PYTHON_RELATIVE)

    if not venv_python.exists():
        return

    current = pathlib.Path(sys.executable).resolve()
    target = venv_python.resolve()
    if current == target:
        return

    os.execv(str(target), [str(target), *sys.argv])
