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

        Background music is not implemented in the current release scope.
        This method is intentionally a no-op to keep the public API stable.
        """
        del name

    def play_fire(self) -> None:
        """Play the player-fire sound effect."""
        self.play("fire")

    def play_hit(self) -> None:
        """Play the player-hit sound effect."""
        if "player_hit" in self._sounds:
            self.play("player_hit")
            return
        self.play("hit")

    def play_explosion(self, size: str) -> None:
        """Play asteroid explosion sound for the provided size.

        Args:
            size: Explosion size label ("small", "medium", or "large").
        """
        normalized_size = size.lower().strip()
        if normalized_size not in {"small", "medium", "large"}:
            normalized_size = "small"
        self.play(f"explode_{normalized_size}")

    def play_enemy_explode(self) -> None:
        """Play the enemy destruction sound effect."""
        self.play("enemy_explode")

    def play_enemy_fire(self) -> None:
        """Play the enemy fire sound effect when available."""
        self.play("enemy_fire")

    def play_pickup_currency(self) -> None:
        """Play the currency pickup sound effect."""
        self.play("pickup_currency")

    def play_pickup_buff(self) -> None:
        """Play the buff pickup sound effect."""
        self.play("pickup_buff")

    def play_shop_purchase(self) -> None:
        """Play successful shop purchase confirmation sound."""
        self.play("shop_purchase")

    def play_shop_denied(self) -> None:
        """Play denied shop interaction sound."""
        self.play("shop_denied")

    def play_level_clear(self) -> None:
        """Play level clear transition sound."""
        self.play("level_clear")

    def play_game_over(self) -> None:
        """Play the game-over sound effect."""
        self.play("game_over")

    def play_menu_nav(self) -> None:
        """Play menu navigation cursor movement sound."""
        self.play("menu_nav")

    def play_menu_select(self) -> None:
        """Play menu selection confirm sound."""
        self.play("menu_select")

    def play_shield_low(self) -> None:
        """Play low-shield warning sound when available."""
        self.play("shield_low")

    def play_insurance_deduct(self) -> None:
        """Play insurance deduction sound when level transition cost is charged."""
        self.play("insurance_deduct")

    def update_settings(self, settings: GameSettings) -> None:
        """Update settings reference used for subsequent playback."""
        self._settings = settings
