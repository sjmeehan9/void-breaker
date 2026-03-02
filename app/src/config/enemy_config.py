"""Enemy archetype configuration models and factory helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from asterax.app.src.utils.paths import get_asset_path


class EnemyArchetype(str, Enum):
    """Supported enemy archetypes for Phase 3 combat."""

    BASIC = "basic"
    AGGRESSIVE = "aggressive"


@dataclass(frozen=True, slots=True)
class EnemyConfig:
    """Per-archetype combat and behaviour tuning values."""

    sprite_path: Path
    speed: float
    turn_rate: float
    fire_rate: float
    health: float
    point_value: int
    accuracy: float
    telegraph_duration: float
    spawn_grace_period: float
    projectile_speed: float
    projectile_damage: float
    currency_drop_chance: float
    buff_drop_chance: float
    projectile_sprite_path: Path = field(
        default_factory=lambda: get_asset_path("sprites", "projectile_enemy.png")
    )

    @property
    def fire_cooldown(self) -> float:
        """Return seconds between shots derived from fire rate."""
        return 1.0 / self.fire_rate


def get_basic_config() -> EnemyConfig:
    """Return default configuration values for the Basic enemy archetype."""
    return EnemyConfig(
        sprite_path=get_asset_path("sprites", "enemy_basic.png"),
        speed=60.0,
        turn_rate=45.0,
        fire_rate=0.4,
        health=1.0,
        point_value=200,
        accuracy=0.6,
        telegraph_duration=0.4,
        spawn_grace_period=1.0,
        projectile_speed=250.0,
        projectile_damage=15.0,
        currency_drop_chance=0.5,
        buff_drop_chance=0.05,
    )


def get_aggressive_config() -> EnemyConfig:
    """Return default configuration values for the Aggressive archetype."""
    return EnemyConfig(
        sprite_path=get_asset_path("sprites", "enemy_aggressive.png"),
        speed=120.0,
        turn_rate=90.0,
        fire_rate=0.8,
        health=2.0,
        point_value=500,
        accuracy=0.85,
        telegraph_duration=0.3,
        spawn_grace_period=1.0,
        projectile_speed=350.0,
        projectile_damage=20.0,
        currency_drop_chance=0.7,
        buff_drop_chance=0.1,
    )
