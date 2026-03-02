"""Core game configuration constants and run-time data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final, Protocol

from asterax.app.src.utils.paths import get_asset_path


class GamePhase(str, Enum):
    """Top-level game phase identifiers."""

    COMBAT = "combat"
    SHOP = "shop"
    GAME_OVER = "game_over"


class AsteroidSize(str, Enum):
    """Asteroid size categories used for spawning and splitting."""

    LARGE = "large"
    MEDIUM = "medium"
    SMALL = "small"


class EnemyArchetype(str, Enum):
    """Enemy behavior archetypes."""

    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    SNIPER = "sniper"


class UpgradeCategory(str, Enum):
    """Upgrade categories shown in the shop."""

    WEAPON = "weapon"
    DEFENSE = "defense"
    MOBILITY = "mobility"
    ECONOMY = "economy"
    REPAIR = "repair"


class InsuranceTier(str, Enum):
    """Insurance retention tiers."""

    OFF = "off"
    BASIC = "basic"
    PREMIUM = "premium"


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Immutable tuning constants shared across the game."""

    physics_dt: float = 1.0 / 60.0
    max_frame_time: float = 0.25
    target_fps: int = 60
    window_width: int = 1280
    window_height: int = 960
    window_title: str = "VoidBreaker"
    natural_drag: float = 0.3
    brake_drag: float = 3.0
    max_ship_speed: float = 600.0
    base_thrust: float = 400.0
    base_turn_rate: float = 240.0
    base_fire_rate: float = 3.0
    base_projectile_speed: float = 800.0
    base_projectile_range: float = 500.0
    base_damage: float = 1.0
    base_shields: float = 100.0
    invulnerability_duration: float = 0.75
    shop_recentre_duration: float = 0.3
    currency_pickup_lifetime: float = 10.0
    max_high_scores: int = 100
    max_player_projectiles: int = 15
    max_particles: int = 300


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    """Mutable-logic physics and combat constants for entities."""

    natural_drag: float = 0.3
    brake_drag: float = 3.0
    max_ship_speed: float = 600.0
    base_thrust: float = 400.0
    base_turn_rate: float = 240.0
    base_fire_rate: float = 5.0
    base_projectile_speed: float = 800.0
    base_projectile_range: float = 600.0
    base_damage: float = 1.0
    max_shields: float = 100.0


@dataclass(frozen=True, slots=True)
class AsteroidConfig:
    """Configuration values used by the asteroid entity system."""

    large_sprite: Path = field(
        default_factory=lambda: get_asset_path("sprites", "asteroid_large.png")
    )
    medium_sprite: Path = field(
        default_factory=lambda: get_asset_path("sprites", "asteroid_medium.png")
    )
    small_sprite: Path = field(
        default_factory=lambda: get_asset_path("sprites", "asteroid_small.png")
    )
    large_scale: float = 1.0
    medium_scale: float = 1.0
    small_scale: float = 1.0
    point_values: dict[AsteroidSize, int] = field(
        default_factory=lambda: {
            AsteroidSize.LARGE: 20,
            AsteroidSize.MEDIUM: 50,
            AsteroidSize.SMALL: 100,
        }
    )
    currency_drop_chances: dict[AsteroidSize, float] = field(
        default_factory=lambda: {
            AsteroidSize.LARGE: 0.2,
            AsteroidSize.MEDIUM: 0.35,
            AsteroidSize.SMALL: 0.5,
        }
    )
    child_count_range: tuple[int, int] = (2, 3)
    child_speed_multiplier_range: tuple[float, float] = (1.2, 1.5)


@dataclass(frozen=True, slots=True)
class CollisionConfig:
    """Configuration for collision response values."""

    ship_asteroid_damage: float = 25.0


@dataclass(frozen=True, slots=True)
class CurrencyConfig:
    """Configuration values used for currency pickup behavior."""

    pickup_value: int = 10
    pickup_lifetime: float = 10.0
    pickup_drift_speed_range: tuple[float, float] = (10.0, 30.0)


@dataclass(frozen=True, slots=True)
class ShopLayoutConfig:
    """Configuration values used to generate shop node layouts."""

    radius_fraction_of_min_dimension: float = 0.36


class UpgradeEffectDefinition(Protocol):
    """Protocol for upgrade definitions consumed by `ShipState`."""

    id: str
    effect_per_level: float
    stat_key: str


@dataclass(slots=True)
class LevelStats:
    """Per-level statistics tracked during combat."""

    asteroids_destroyed: int = 0
    enemies_destroyed: int = 0
    currency_collected: int = 0
    damage_taken: float = 0.0


@dataclass(slots=True)
class RunStats:
    """Cumulative statistics tracked across the full run."""

    asteroids_destroyed: int = 0
    enemies_destroyed: int = 0
    currency_collected: int = 0
    damage_taken: float = 0.0
    levels_completed: int = 0
    currency_spent: int = 0
    upgrades_purchased: int = 0


@dataclass(slots=True)
class DifficultyParams:
    """Difficulty parameters generated per level."""

    asteroid_count: int = 4
    asteroid_speed_min: float = 50.0
    asteroid_speed_max: float = 150.0
    enemy_spawn_enabled: bool = False
    enemy_count_max: int = 0
    enemy_spawn_interval: float = 10.0
    enemy_aggression: float = 0.0
    aggressive_ratio: float = 0.0
    currency_drop_chance: float = 0.4
    currency_value_base: int = 10


@dataclass(slots=True)
class InsuranceState:
    """Insurance selection and retention behavior for the current run."""

    tier: InsuranceTier = InsuranceTier.OFF
    cost_per_level: int = 0
    retention_fraction: float = 0.0


@dataclass(slots=True)
class ShipState:
    """Ship physics, upgrades, and effective combat statistics."""

    position: tuple[float, float] = (0.0, 0.0)
    velocity: tuple[float, float] = (0.0, 0.0)
    angle: float = 0.0
    angular_velocity: float = 0.0

    base_thrust: float = 400.0
    base_turn_rate: float = 240.0
    base_fire_rate: float = 3.0
    base_projectile_speed: float = 800.0
    base_projectile_range: float = 500.0
    base_damage: float = 1.0
    base_shields: float = 100.0
    base_magnet_radius: float = 0.0

    weapon_fire_rate_level: int = 0
    weapon_damage_level: int = 0
    weapon_speed_level: int = 0
    weapon_spread_level: int = 0
    defense_shields_level: int = 0
    mobility_thrust_level: int = 0
    mobility_turn_level: int = 0
    economy_magnet_level: int = 0
    economy_protection_level: int = 0
    score_bonus_level: int = 0

    effective_thrust: float = 400.0
    effective_turn_rate: float = 240.0
    effective_fire_rate: float = 3.0
    effective_projectile_speed: float = 800.0
    effective_projectile_range: float = 500.0
    effective_damage: float = 1.0
    effective_max_shields: float = 100.0
    effective_magnet_radius: float = 0.0
    effective_projectile_count: int = 1

    def recalculate_effective_stats(
        self,
        upgrade_definitions: list[UpgradeEffectDefinition],
    ) -> None:
        """Recompute effective stats using purchased upgrade levels.

        Args:
            upgrade_definitions: Available upgrades with stat-key mappings.
        """
        self.effective_thrust = self.base_thrust
        self.effective_turn_rate = self.base_turn_rate
        self.effective_fire_rate = self.base_fire_rate
        self.effective_projectile_speed = self.base_projectile_speed
        self.effective_projectile_range = self.base_projectile_range
        self.effective_damage = self.base_damage
        self.effective_max_shields = self.base_shields
        self.effective_magnet_radius = self.base_magnet_radius
        self.effective_projectile_count = 1

        for definition in upgrade_definitions:
            level_name = f"{definition.id}_level"
            level = max(0, int(getattr(self, level_name, 0)))
            if level == 0:
                continue

            if definition.stat_key in {"shields", "score_multiplier"}:
                continue

            increment = definition.effect_per_level * level
            if definition.stat_key == "fire_rate":
                self.effective_fire_rate += increment
            elif definition.stat_key == "damage":
                self.effective_damage += increment
            elif definition.stat_key == "projectile_speed":
                self.effective_projectile_speed += increment
            elif definition.stat_key == "spread":
                self.effective_projectile_count += int(increment)
            elif definition.stat_key == "max_shields":
                self.effective_max_shields += increment
            elif definition.stat_key == "thrust":
                self.effective_thrust += increment
            elif definition.stat_key == "turn_rate":
                self.effective_turn_rate += increment
            elif definition.stat_key == "magnet_radius":
                self.effective_magnet_radius += increment


@dataclass(slots=True)
class GameState:
    """Top-level mutable state for a single run."""

    current_level: int = 1
    score: int = 0
    currency: int = 0
    shields: float = 100.0
    max_shields: float = 100.0
    is_paused: bool = False
    is_practice: bool = False
    phase: GamePhase = GamePhase.COMBAT
    level_stats: LevelStats = field(default_factory=LevelStats)
    run_stats: RunStats = field(default_factory=RunStats)
    insurance: InsuranceState = field(default_factory=InsuranceState)


GAME_CONFIG: Final[GameConfig] = GameConfig()
PHYSICS_CONFIG: Final[PhysicsConfig] = PhysicsConfig()
ASTEROID_CONFIG: Final[AsteroidConfig] = AsteroidConfig()
COLLISION_CONFIG: Final[CollisionConfig] = CollisionConfig()
CURRENCY_CONFIG: Final[CurrencyConfig] = CurrencyConfig()
SHOP_LAYOUT_CONFIG: Final[ShopLayoutConfig] = ShopLayoutConfig()
