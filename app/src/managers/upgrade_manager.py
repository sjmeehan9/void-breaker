"""Upgrade-level tracking and stat recalculation manager."""

from __future__ import annotations

from asterax.app.src.config.game_config import GameState, ShipState
from asterax.app.src.config.upgrade_definitions import (
    UPGRADE_DEFINITIONS,
    UpgradeDefinition,
    get_upgrade_cost,
)


class UpgradeManager:
    """Apply upgrades, enforce caps, and keep effective ship stats in sync."""

    def __init__(
        self,
        ship_state: ShipState,
        game_state: GameState,
        upgrade_definitions: list[UpgradeDefinition] | None = None,
    ) -> None:
        """Initialise manager with mutable ship and game state references."""
        self.ship_state = ship_state
        self.game_state = game_state
        self._definitions = upgrade_definitions or UPGRADE_DEFINITIONS
        self._definitions_by_id = {
            definition.id: definition for definition in self._definitions
        }
        self._levels = {
            definition.id: int(
                max(
                    0,
                    getattr(self.ship_state, f"{definition.id}_level", 0),
                )
            )
            for definition in self._definitions
        }
        self.recalculate_all_stats()

    def apply_upgrade(self, upgrade_id: str) -> bool:
        """Apply a purchasable upgrade and recalculate effective stats."""
        definition = self._definitions_by_id.get(upgrade_id)
        if definition is None:
            return False
        if definition.id == "repairs":
            self.apply_repair(definition.effect_per_level)
            return True
        if not self.can_upgrade(upgrade_id):
            return False
        self._levels[upgrade_id] += 1
        level_attr = f"{upgrade_id}_level"
        if hasattr(self.ship_state, level_attr):
            setattr(self.ship_state, level_attr, self._levels[upgrade_id])
        self.recalculate_all_stats()
        return True

    def get_effective_stat(self, stat_key: str) -> float:
        """Return effective stat values used by gameplay systems."""
        stat_map = {
            "fire_rate": float(self.ship_state.effective_fire_rate),
            "damage": float(self.ship_state.effective_damage),
            "projectile_speed": float(self.ship_state.effective_projectile_speed),
            "spread": float(self.ship_state.effective_projectile_count),
            "max_shields": float(self.ship_state.effective_max_shields),
            "thrust": float(self.ship_state.effective_thrust),
            "turn_rate": float(self.ship_state.effective_turn_rate),
            "magnet_radius": float(self.ship_state.effective_magnet_radius),
            "currency_protection": float(self.get_level("economy_protection")),
            "score_multiplier": self.get_score_multiplier(),
        }
        return stat_map.get(stat_key, 0.0)

    def recalculate_all_stats(self) -> None:
        """Recompute all effective fields from base ship stats and upgrades."""
        previous_max_shields = float(self.ship_state.effective_max_shields)
        self.ship_state.effective_thrust = float(self.ship_state.base_thrust)
        self.ship_state.effective_turn_rate = float(self.ship_state.base_turn_rate)
        self.ship_state.effective_fire_rate = float(self.ship_state.base_fire_rate)
        self.ship_state.effective_projectile_speed = float(
            self.ship_state.base_projectile_speed
        )
        self.ship_state.effective_projectile_range = float(
            self.ship_state.base_projectile_range
        )
        self.ship_state.effective_damage = float(self.ship_state.base_damage)
        self.ship_state.effective_max_shields = float(self.ship_state.base_shields)
        self.ship_state.effective_magnet_radius = float(
            self.ship_state.base_magnet_radius
        )
        self.ship_state.effective_projectile_count = 1

        for definition in self._definitions:
            level = self.get_level(definition.id)
            if level <= 0 or definition.id in {"repairs", "score_bonus"}:
                continue
            increment = level * definition.effect_per_level
            if definition.stat_key == "fire_rate":
                self.ship_state.effective_fire_rate += increment
            elif definition.stat_key == "damage":
                self.ship_state.effective_damage += increment
            elif definition.stat_key == "projectile_speed":
                self.ship_state.effective_projectile_speed += increment
            elif definition.stat_key == "spread":
                self.ship_state.effective_projectile_count += int(increment)
            elif definition.stat_key == "max_shields":
                self.ship_state.effective_max_shields += increment
            elif definition.stat_key == "thrust":
                self.ship_state.effective_thrust += increment
            elif definition.stat_key == "turn_rate":
                self.ship_state.effective_turn_rate += increment
            elif definition.stat_key == "magnet_radius":
                self.ship_state.effective_magnet_radius += increment
            elif definition.stat_key == "currency_protection":
                self.ship_state.economy_protection_level = int(level > 0)

        delta_shields = self.ship_state.effective_max_shields - previous_max_shields
        self.game_state.max_shields = self.ship_state.effective_max_shields
        self.game_state.shields = min(
            self.game_state.max_shields,
            self.game_state.shields + max(0.0, delta_shields),
        )

    def get_cost(self, upgrade_id: str) -> int:
        """Return the next purchase cost for a given upgrade."""
        definition = self._definitions_by_id.get(upgrade_id)
        if definition is None:
            return 0
        return get_upgrade_cost(definition, self.get_level(upgrade_id))

    def can_upgrade(self, upgrade_id: str) -> bool:
        """Return whether the given upgrade can still gain levels."""
        definition = self._definitions_by_id.get(upgrade_id)
        if definition is None or definition.id == "repairs":
            return definition is not None
        return self.get_level(upgrade_id) < definition.max_level

    def get_level(self, upgrade_id: str) -> int:
        """Return the current level for an upgrade id."""
        return int(self._levels.get(upgrade_id, 0))

    def get_all_levels(self) -> dict[str, int]:
        """Return a snapshot of all tracked upgrade levels."""
        return dict(self._levels)

    def set_levels(self, levels: dict[str, int]) -> None:
        """Bulk-restore upgrade levels and recompute effective stats."""
        for definition in self._definitions:
            if definition.id == "repairs":
                self._levels[definition.id] = 0
                continue
            level = max(0, min(definition.max_level, int(levels.get(definition.id, 0))))
            self._levels[definition.id] = level
            level_attr = f"{definition.id}_level"
            if hasattr(self.ship_state, level_attr):
                setattr(self.ship_state, level_attr, level)
        self.recalculate_all_stats()

    def apply_repair(self, amount: float) -> None:
        """Restore shields immediately, capped to current max shields."""
        self.game_state.shields = min(
            self.game_state.max_shields,
            self.game_state.shields + max(0.0, amount),
        )

    def get_score_multiplier(self) -> float:
        """Return the active score multiplier from score bonus levels."""
        definition = self._definitions_by_id.get("score_bonus")
        if definition is None:
            return 1.0
        return 1.0 + (self.get_level("score_bonus") * definition.effect_per_level)
