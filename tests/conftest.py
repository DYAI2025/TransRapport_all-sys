"""Pytest configuration helpers for TransRapport tests.

The contract suite exercises the external ``transrapport-docs`` command via
``subprocess``.  When running directly from a source checkout the console script
is provided in ``bin/transrapport-docs`` and would normally be installed into the
user's ``PATH`` by the packaging process.  The tests run without installation,
so we extend ``PATH`` here to make the shim discoverable.
"""
from __future__ import annotations

import os
from pathlib import Path


def pytest_configure() -> None:
    """Ensure the CLI shim directory is available on ``PATH`` for subprocesses."""
    repo_root = Path(__file__).resolve().parent.parent
    bin_dir = repo_root / "bin"

    if not bin_dir.exists():
        return

    current_path = os.environ.get("PATH", "")
    path_entries = current_path.split(os.pathsep) if current_path else []

    bin_str = str(bin_dir)
    if bin_str not in path_entries:
        os.environ["PATH"] = os.pathsep.join([bin_str, *path_entries]) if path_entries else bin_str
