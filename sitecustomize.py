"""Project specific interpreter customisations.

Pytest and the standalone CLI executables run directly from the source tree
without installing the package.  Python automatically imports ``sitecustomize``
(if available on the import path) during start-up, so we use this hook to extend
``PATH`` with the repository's ``bin`` directory.  This makes the lightweight
``transrapport-docs`` shim discoverable for subprocesses during tests and local
usage, faithfully mimicking the behaviour of an installed console script.
"""
from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_BIN_DIR = _REPO_ROOT / "bin"

if _BIN_DIR.exists():
    current_path = os.environ.get("PATH", "")
    path_entries = current_path.split(os.pathsep) if current_path else []

    bin_str = str(_BIN_DIR)
    if bin_str not in path_entries:
        os.environ["PATH"] = os.pathsep.join([bin_str, *path_entries]) if path_entries else bin_str
