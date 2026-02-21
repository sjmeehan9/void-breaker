"""Persistence schemas for settings and high score data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

SETTINGS_VERSION: Final[int] = 1
HIGH_SCORES_VERSION: Final[int] = 1


@dataclass(slots=True)
class GameSettings:
    """User-configurable game settings stored on disk."""

    master_volume: float = 0.8
    music_volume: float = 0.5
    sfx_volume: float = 1.0
    key_rotate_left: str = "LEFT"
    key_rotate_right: str = "RIGHT"
    key_thrust: str = "UP"
    key_fire: str = "SPACE"
    key_brake: str = "DOWN"
    key_special: str = "LSHIFT"
    key_pause: str = "ESCAPE"
    fire_mode: str = "hold"
    autofire: bool = False
    colorblind_mode: bool = False
    screen_shake: str = "medium"
    difficulty: str = "classic"
    fullscreen: bool = False
    resolution: tuple[int, int] = (1280, 960)

    def to_dict(self) -> dict[str, object]:
        """Serialise settings to a JSON-compatible dictionary."""
        settings = asdict(self)
        settings["resolution"] = list(self.resolution)
        return settings

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> GameSettings:
        """Build settings from persisted data, defaulting missing fields."""
        settings = cls()
        settings.master_volume = float(
            data.get("master_volume", settings.master_volume)
        )
        settings.music_volume = float(data.get("music_volume", settings.music_volume))
        settings.sfx_volume = float(data.get("sfx_volume", settings.sfx_volume))
        settings.key_rotate_left = str(
            data.get("key_rotate_left", settings.key_rotate_left)
        )
        settings.key_rotate_right = str(
            data.get("key_rotate_right", settings.key_rotate_right)
        )
        settings.key_thrust = str(data.get("key_thrust", settings.key_thrust))
        settings.key_fire = str(data.get("key_fire", settings.key_fire))
        settings.key_brake = str(data.get("key_brake", settings.key_brake))
        settings.key_special = str(data.get("key_special", settings.key_special))
        settings.key_pause = str(data.get("key_pause", settings.key_pause))
        settings.fire_mode = str(data.get("fire_mode", settings.fire_mode))
        settings.autofire = bool(data.get("autofire", settings.autofire))
        settings.colorblind_mode = bool(
            data.get("colorblind_mode", settings.colorblind_mode)
        )
        settings.screen_shake = str(data.get("screen_shake", settings.screen_shake))
        settings.difficulty = str(data.get("difficulty", settings.difficulty))
        settings.fullscreen = bool(data.get("fullscreen", settings.fullscreen))

        resolution_data = data.get("resolution", list(settings.resolution))
        if isinstance(resolution_data, list | tuple) and len(resolution_data) == 2:
            settings.resolution = (int(resolution_data[0]), int(resolution_data[1]))

        return settings


@dataclass(slots=True)
class HighScoreEntry:
    """Single persisted high-score entry."""

    name: str
    score: int
    level_reached: int
    difficulty: str
    enemies_destroyed: int
    currency_collected: int
    currency_spent: int
    date: str

    def to_dict(self) -> dict[str, object]:
        """Serialise high score entry to a JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> HighScoreEntry:
        """Build a high score entry from persisted data."""
        return cls(
            name=str(data["name"]),
            score=int(data["score"]),
            level_reached=int(data["level_reached"]),
            difficulty=str(data["difficulty"]),
            enemies_destroyed=int(data["enemies_destroyed"]),
            currency_collected=int(data["currency_collected"]),
            currency_spent=int(data["currency_spent"]),
            date=str(data["date"]),
        )
