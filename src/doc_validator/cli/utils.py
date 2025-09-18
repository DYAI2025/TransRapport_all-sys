"""Shared helpers for the TransRapport documentation CLI."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

_DOC_CANDIDATES: Iterable[str] = ("docs", "demo-docs", "test-docs")


def resolve_docs_root(start: Path | None = None) -> Path:
    """Return the most likely documentation root directory.

    The CLI commands operate on markdown documentation.  When run from the
    project root we prefer the dedicated ``docs`` folder (falling back to
    ``demo-docs`` or ``test-docs`` if present).  If none of these directories
    exist we operate on the supplied ``start`` directory directly.
    """

    base = start or Path.cwd()

    for candidate in _DOC_CANDIDATES:
        candidate_path = base / candidate
        if candidate_path.exists():
            return candidate_path

    return base
