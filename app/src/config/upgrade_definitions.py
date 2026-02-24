"""Upgrade definitions and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from asterax.app.src.config.game_config import UpgradeCategory


@dataclass(frozen=True, slots=True)
class UpgradeDefinition:
    """Static definition for a purchasable upgrade."""

    id: str
    category: UpgradeCategory
    name: str
    description: str
    max_level: int
    base_cost: int
    cost_scaling: float
    effect_per_level: float
    stat_key: str


ALL_UPGRADES: Final[list[UpgradeDefinition]] = [
    UpgradeDefinition(
        id="weapon_fire_rate",
        category=UpgradeCategory.WEAPON,
        name="Fire Rate",
        description="Increase primary weapon shots per second.",
        max_level=5,
        base_cost=80,
        cost_scaling=1.5,
        effect_per_level=0.5,
        stat_key="fire_rate",
    ),
    UpgradeDefinition(
        id="weapon_damage",
        category=UpgradeCategory.WEAPON,
        name="Damage",
        description="Increase projectile damage.",
        max_level=5,
        base_cost=100,
        cost_scaling=1.5,
        effect_per_level=0.3,
        stat_key="damage",
    ),
    UpgradeDefinition(
        id="weapon_speed",
        category=UpgradeCategory.WEAPON,
        name="Shot Speed",
        description="Increase projectile travel speed.",
        max_level=5,
        base_cost=60,
        cost_scaling=1.4,
        effect_per_level=50.0,
        stat_key="projectile_speed",
    ),
    UpgradeDefinition(
        id="weapon_spread",
        category=UpgradeCategory.WEAPON,
        name="Spread Shot",
        description="Adds an extra projectile per level.",
        max_level=3,
        base_cost=200,
        cost_scaling=2.0,
        effect_per_level=1.0,
        stat_key="spread",
    ),
    UpgradeDefinition(
        id="defense_shields",
        category=UpgradeCategory.DEFENSE,
        name="Shields",
        description="Increase maximum shields.",
        max_level=5,
        base_cost=120,
        cost_scaling=1.6,
        effect_per_level=25.0,
        stat_key="max_shields",
    ),
    UpgradeDefinition(
        id="mobility_thrust",
        category=UpgradeCategory.MOBILITY,
        name="Thrust",
        description="Increase ship acceleration.",
        max_level=5,
        base_cost=80,
        cost_scaling=1.4,
        effect_per_level=60.0,
        stat_key="thrust",
    ),
    UpgradeDefinition(
        id="mobility_turn",
        category=UpgradeCategory.MOBILITY,
        name="Turn Rate",
        description="Increase ship rotation speed.",
        max_level=5,
        base_cost=60,
        cost_scaling=1.3,
        effect_per_level=30.0,
        stat_key="turn_rate",
    ),
    UpgradeDefinition(
        id="economy_magnet",
        category=UpgradeCategory.ECONOMY,
        name="Magnet",
        description="Increase currency attraction radius.",
        max_level=5,
        base_cost=100,
        cost_scaling=1.5,
        effect_per_level=30.0,
        stat_key="magnet_radius",
    ),
    UpgradeDefinition(
        id="economy_protection",
        category=UpgradeCategory.ECONOMY,
        name="Protection",
        description="Currency pickups become indestructible.",
        max_level=1,
        base_cost=300,
        cost_scaling=1.0,
        effect_per_level=1.0,
        stat_key="currency_protection",
    ),
    UpgradeDefinition(
        id="repairs",
        category=UpgradeCategory.REPAIR,
        name="Repairs",
        description="Restore shields immediately.",
        max_level=99,
        base_cost=50,
        cost_scaling=1.3,
        effect_per_level=30.0,
        stat_key="shields",
    ),
    UpgradeDefinition(
        id="score_bonus",
        category=UpgradeCategory.ECONOMY,
        name="Score Bonus",
        description="Increase score multiplier for this run.",
        max_level=3,
        base_cost=250,
        cost_scaling=2.0,
        effect_per_level=0.25,
        stat_key="score_multiplier",
    ),
]

UPGRADE_DEFINITIONS: Final[list[UpgradeDefinition]] = ALL_UPGRADES


def get_upgrade_cost(definition: UpgradeDefinition, current_level: int) -> int:
    """Calculate current upgrade cost using geometric scaling."""

    level = max(0, current_level)
    return int(definition.base_cost * (definition.cost_scaling**level))


def get_upgrade_by_id(upgrade_id: str) -> UpgradeDefinition | None:
    """Find an upgrade definition by identifier."""

    return next((upgrade for upgrade in ALL_UPGRADES if upgrade.id == upgrade_id), None)
