"""Persistence manager for settings and high scores."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

from asterax.app.src.persistence.schemas import (
    HIGH_SCORES_VERSION,
    SETTINGS_VERSION,
    GameSettings,
    HighScoreEntry,
)
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)
_MAX_HIGH_SCORE_ENTRIES = 100


class PersistenceManager:
    """Read and write persistent game data as versioned JSON files."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialise storage paths for settings and high score files."""
        resolved_dir = (
            base_dir
            if base_dir is not None
            else Path(user_data_dir("VoidBreaker", appauthor=False))
        )
        resolved_dir.mkdir(parents=True, exist_ok=True)

        self._base_dir = resolved_dir
        self._settings_path = self._base_dir / "settings.json"
        self._high_scores_path = self._base_dir / "high_scores.json"

    def load_settings(self) -> GameSettings:
        """Load settings from disk, falling back to defaults when needed."""
        payload = self._load_json(self._settings_path)
        if payload is None:
            return GameSettings()

        version = payload.get("version")
        if not isinstance(version, int):
            logger.warning("Settings file missing valid version; using defaults.")
            return GameSettings()

        if version > SETTINGS_VERSION:
            logger.warning(
                "Settings schema version %s is newer than supported %s; using defaults.",
                version,
                SETTINGS_VERSION,
            )
            return GameSettings()

        try:
            return GameSettings.from_dict(payload)
        except (TypeError, ValueError) as exc:
            logger.warning(
                "Failed to parse settings file; using defaults. Error: %s", exc
            )
            return GameSettings()

    def save_settings(self, settings: GameSettings) -> None:
        """Persist settings to disk using an atomic replace."""
        payload = {"version": SETTINGS_VERSION, **settings.to_dict()}
        self._atomic_write_json(self._settings_path, payload)

    def load_high_scores(self) -> list[HighScoreEntry]:
        """Load high score entries from disk or return an empty list."""
        payload = self._load_json(self._high_scores_path)
        if payload is None:
            return []

        version = payload.get("version")
        if not isinstance(version, int):
            logger.warning(
                "High scores file missing valid version; returning empty list."
            )
            return []

        if version > HIGH_SCORES_VERSION:
            logger.warning(
                "High scores schema version %s is newer than supported %s; returning empty list.",
                version,
                HIGH_SCORES_VERSION,
            )
            return []

        entries_data = payload.get("entries", [])
        if not isinstance(entries_data, list):
            logger.warning(
                "High scores entries field is invalid; returning empty list."
            )
            return []

        entries: list[HighScoreEntry] = []
        try:
            for entry_data in entries_data:
                if not isinstance(entry_data, dict):
                    raise TypeError("entry is not an object")
                entries.append(HighScoreEntry.from_dict(entry_data))
        except (TypeError, ValueError, KeyError) as exc:
            logger.warning(
                "Failed to parse high scores file; returning empty list. Error: %s", exc
            )
            return []

        return entries

    def save_high_scores(self, entries: list[HighScoreEntry]) -> None:
        """Persist high score entries using an atomic replace."""
        capped_entries = entries[:_MAX_HIGH_SCORE_ENTRIES]
        payload = {
            "version": HIGH_SCORES_VERSION,
            "entries": [entry.to_dict() for entry in capped_entries],
        }
        self._atomic_write_json(self._high_scores_path, payload)

    def _load_json(self, path: Path) -> dict[str, object] | None:
        """Return decoded JSON from path, or None when missing/invalid."""
        if not path.exists():
            return None

        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to read %s; using defaults. Error: %s", path, exc)
            return None

        if not isinstance(payload, dict):
            logger.warning("Expected JSON object in %s; using defaults.", path)
            return None

        return payload

    def _atomic_write_json(self, path: Path, payload: dict[str, object]) -> None:
        """Write JSON atomically by replacing the destination file."""
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._base_dir,
                delete=False,
            ) as temp_file:
                json.dump(payload, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_path = Path(temp_file.name)
            os.replace(temp_path, path)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
