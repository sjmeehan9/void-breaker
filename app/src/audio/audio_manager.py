"""Audio manager for sound-effect loading and playback."""

from __future__ import annotations

import logging
from pathlib import Path

import arcade
from asterax.app.src.persistence.schemas import GameSettings

logger = logging.getLogger(__name__)


class AudioManager:
    """Load and play sound effects based on persisted volume settings."""

    def __init__(self, settings: GameSettings, sound_dir: Path) -> None:
        """Initialise audio state and load available sound files."""
        self._settings = settings
        self._sound_dir = sound_dir
        self._sounds: dict[str, arcade.Sound] = {}
        self._load_sounds()

    def _load_sounds(self) -> None:
        """Load `.wav` files from the configured sounds directory."""
        if not self._sound_dir.exists() or not self._sound_dir.is_dir():
            logger.debug("Sound directory missing; skipping load: %s", self._sound_dir)
            return

        sound_files = sorted(self._sound_dir.glob("*.wav"))
        if not sound_files:
            logger.debug("No sound files found in %s", self._sound_dir)
            return

        for sound_path in sound_files:
            try:
                self._sounds[sound_path.stem] = arcade.load_sound(str(sound_path))
            except Exception as exc:
                logger.warning("Failed to load sound '%s': %s", sound_path.name, exc)

    def play(self, name: str, volume_override: float | None = None) -> None:
        """Play a loaded sound by name using effective master/SFX volume."""
        sound = self._sounds.get(name)
        if sound is None:
            return

        base_volume = (
            self._settings.sfx_volume if volume_override is None else volume_override
        )
        effective_volume = max(
            0.0, min(1.0, base_volume * self._settings.master_volume)
        )
        try:
            arcade.play_sound(sound, volume=effective_volume)
        except Exception as exc:
            logger.warning("Failed to play sound '%s': %s", name, exc)

    def play_music(self, name: str) -> None:
        """Play background music track by name.

        Phase 5 will add streamed music playback support. Until then, this method is
        intentionally a no-op to keep the public API stable for caller integration.
        """
        del name

    def update_settings(self, settings: GameSettings) -> None:
        """Update settings reference used for subsequent playback."""
        self._settings = settings
