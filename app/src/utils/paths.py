"""Path resolution helpers for source and PyInstaller bundle runtimes."""

from __future__ import annotations

import sys
from pathlib import Path


def get_runtime_root() -> Path:
    """Return the base root directory for the active runtime mode.

    Returns:
        The source repository root in development mode, or the PyInstaller
        extraction root when running from a frozen bundle.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[3]


def get_assets_root() -> Path:
    """Return the absolute `assets` directory for the active runtime mode."""
    return get_runtime_root() / "assets"


def get_asset_path(*parts: str) -> Path:
    """Return an absolute path inside the `assets` directory.

    Args:
        *parts: Asset path segments under the `assets` folder.

    Returns:
        The resolved absolute path to the requested asset.
    """
    return get_assets_root().joinpath(*parts)
