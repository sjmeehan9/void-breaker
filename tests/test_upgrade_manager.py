"""Unit tests for the Phase 4 upgrade manager."""

from __future__ import annotations

from asterax.app.src.config.game_config import GameState, ShipState
from asterax.app.src.config.upgrade_definitions import UPGRADE_DEFINITIONS
from asterax.app.src.managers.upgrade_manager import UpgradeManager


def test_apply_upgrade_increments_level_and_recalculates_stats() -> None:
    """Applying an upgrade should increase level and effective stat values."""
    manager = UpgradeManager(ShipState(), GameState())

    assert manager.apply_upgrade("weapon_fire_rate")

    assert manager.get_level("weapon_fire_rate") == 1
    assert manager.ship_state.weapon_fire_rate_level == 1
    assert (
        manager.get_effective_stat("fire_rate")
        == manager.ship_state.base_fire_rate + 0.5
    )


def test_get_cost_uses_geometric_scaling() -> None:
    """Upgrade costs should follow base_cost * cost_scaling^level."""
    manager = UpgradeManager(ShipState(), GameState())

    assert manager.get_cost("weapon_fire_rate") == 80
    manager.apply_upgrade("weapon_fire_rate")
    assert manager.get_cost("weapon_fire_rate") == 120
    manager.apply_upgrade("weapon_fire_rate")
    assert manager.get_cost("weapon_fire_rate") == 180


def test_can_upgrade_false_at_max_level() -> None:
    """Max-level upgrades should report as non-upgradable."""
    manager = UpgradeManager(ShipState(), GameState())
    manager.set_levels({"economy_protection": 1})

    assert not manager.can_upgrade("economy_protection")


def test_apply_repair_caps_at_max_shields() -> None:
    """Repair application should not exceed max shields."""
    game_state = GameState(shields=95.0, max_shields=100.0)
    manager = UpgradeManager(ShipState(), game_state)

    manager.apply_upgrade("repairs")

    assert game_state.shields == 100.0


def test_set_levels_bulk_restores_and_updates_stats() -> None:
    """Bulk level restoration should update ship and game-state stats."""
    game_state = GameState(shields=60.0, max_shields=100.0)
    manager = UpgradeManager(ShipState(), game_state)

    manager.set_levels({"defense_shields": 2, "mobility_turn": 3})

    assert manager.get_level("defense_shields") == 2
    assert manager.ship_state.effective_max_shields == 150.0
    assert game_state.max_shields == 150.0
    assert game_state.shields == 110.0
    assert (
        manager.ship_state.effective_turn_rate
        == manager.ship_state.base_turn_rate + 90.0
    )


def test_get_score_multiplier_from_score_bonus_level() -> None:
    """Score multiplier should increase from score bonus upgrade levels."""
    manager = UpgradeManager(ShipState(), GameState())
    manager.set_levels({"score_bonus": 2})

    assert manager.get_score_multiplier() == 1.5


def test_upgrade_definitions_include_all_component_entries() -> None:
    """The upgrade catalog should include all required Phase 4.4 upgrades."""
    upgrade_ids = {definition.id for definition in UPGRADE_DEFINITIONS}
    assert len(UPGRADE_DEFINITIONS) == 11
    assert {
        "weapon_fire_rate",
        "weapon_damage",
        "weapon_speed",
        "weapon_spread",
        "defense_shields",
        "mobility_thrust",
        "mobility_turn",
        "economy_magnet",
        "economy_protection",
        "repairs",
        "score_bonus",
    }.issubset(upgrade_ids)
