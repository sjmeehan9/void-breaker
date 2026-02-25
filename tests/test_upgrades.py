"""Comprehensive tests for UpgradeManager — upgrade application, cost scaling,
stat recalculation, repairs, score multiplier, and bulk level management.
"""

from __future__ import annotations

import pytest
from asterax.app.src.config.game_config import GameState, ShipState
from asterax.app.src.config.upgrade_definitions import (
    ALL_UPGRADES,
    UPGRADE_DEFINITIONS,
    UpgradeDefinition,
    get_upgrade_cost,
)
from asterax.app.src.managers.upgrade_manager import UpgradeManager

# ---------------------------------------------------------------------------
# TestUpgradeApplication
# ---------------------------------------------------------------------------


class TestUpgradeApplication:
    """Verify apply_upgrade increments levels and recalculates stats."""

    def test_apply_increments_level_and_returns_true(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """First application of a valid upgrade should succeed."""
        manager = UpgradeManager(ship_state, game_state)
        assert manager.apply_upgrade("weapon_fire_rate") is True
        assert manager.get_level("weapon_fire_rate") == 1

    def test_apply_updates_effective_stat(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Effective stat should reflect the upgrade delta after application."""
        manager = UpgradeManager(ship_state, game_state)
        base = ship_state.base_fire_rate
        manager.apply_upgrade("weapon_fire_rate")
        assert manager.get_effective_stat("fire_rate") == base + 0.5

    def test_apply_at_max_level_returns_false(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Upgrade past max level must be rejected."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"economy_protection": 1})
        assert manager.apply_upgrade("economy_protection") is False
        assert manager.get_level("economy_protection") == 1

    def test_apply_unknown_upgrade_returns_false(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """An unknown upgrade ID should not crash and should return False."""
        manager = UpgradeManager(ship_state, game_state)
        assert manager.apply_upgrade("nonexistent_upgrade") is False

    def test_apply_multiple_upgrades_accumulate(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Multiple successive applications should accumulate levels."""
        manager = UpgradeManager(ship_state, game_state)
        for _ in range(3):
            manager.apply_upgrade("weapon_fire_rate")
        assert manager.get_level("weapon_fire_rate") == 3
        expected = ship_state.base_fire_rate + (3 * 0.5)
        assert manager.get_effective_stat("fire_rate") == pytest.approx(expected)


# ---------------------------------------------------------------------------
# TestCostScaling
# ---------------------------------------------------------------------------


class TestCostScaling:
    """Verify get_cost follows base_cost * cost_scaling^level for all upgrades."""

    @pytest.mark.parametrize(
        "upgrade_id",
        [defn.id for defn in ALL_UPGRADES if defn.id != "repairs"],
        ids=[defn.id for defn in ALL_UPGRADES if defn.id != "repairs"],
    )
    def test_cost_at_levels_zero_through_five(
        self,
        upgrade_id: str,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Cost at each level should match the geometric formula."""
        manager = UpgradeManager(ship_state, game_state)
        defn = next(u for u in ALL_UPGRADES if u.id == upgrade_id)
        for level in range(min(6, defn.max_level + 1)):
            expected = int(defn.base_cost * (defn.cost_scaling**level))
            manager.set_levels({upgrade_id: level})
            assert manager.get_cost(upgrade_id) == expected, (
                f"{upgrade_id} level {level}: expected {expected}, "
                f"got {manager.get_cost(upgrade_id)}"
            )

    def test_repairs_cost_always_at_level_zero(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Repairs level is always zero in set_levels; cost returns base cost."""
        manager = UpgradeManager(ship_state, game_state)
        defn = next(u for u in ALL_UPGRADES if u.id == "repairs")
        assert manager.get_cost("repairs") == defn.base_cost

    def test_cost_of_unknown_upgrade_is_zero(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Unknown upgrade ID should return zero cost."""
        manager = UpgradeManager(ship_state, game_state)
        assert manager.get_cost("nonexistent") == 0


# ---------------------------------------------------------------------------
# TestStatRecalculation
# ---------------------------------------------------------------------------


class TestStatRecalculation:
    """Verify recalculate_all_stats produces correct effective values."""

    _STAT_UPGRADE_MAP: list[tuple[str, str, str]] = [
        ("weapon_fire_rate", "fire_rate", "base_fire_rate"),
        ("weapon_damage", "damage", "base_damage"),
        ("weapon_speed", "projectile_speed", "base_projectile_speed"),
        ("defense_shields", "max_shields", "base_shields"),
        ("mobility_thrust", "thrust", "base_thrust"),
        ("mobility_turn", "turn_rate", "base_turn_rate"),
        ("economy_magnet", "magnet_radius", "base_magnet_radius"),
    ]

    @pytest.mark.parametrize(
        ("upgrade_id", "stat_key", "base_attr"),
        _STAT_UPGRADE_MAP,
        ids=[t[0] for t in _STAT_UPGRADE_MAP],
    )
    def test_effective_equals_base_plus_level_times_effect(
        self,
        upgrade_id: str,
        stat_key: str,
        base_attr: str,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """effective_X should equal base_X + (level * effect_per_level)."""
        manager = UpgradeManager(ship_state, game_state)
        defn = next(u for u in ALL_UPGRADES if u.id == upgrade_id)
        level = 2
        manager.set_levels({upgrade_id: level})
        base_value = getattr(ship_state, base_attr)
        expected = base_value + (level * defn.effect_per_level)
        assert manager.get_effective_stat(stat_key) == pytest.approx(expected)

    def test_spread_upgrade_adds_projectile_count(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Spread upgrade should increment effective projectile count."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"weapon_spread": 2})
        assert manager.get_effective_stat("spread") == 3.0  # 1 base + 2*1

    def test_recalculate_updates_game_state_shields(
        self,
        ship_state: ShipState,
    ) -> None:
        """Shield upgrade should increase game_state.max_shields and shields."""
        gs = GameState(shields=100.0, max_shields=100.0)
        manager = UpgradeManager(ship_state, gs)
        manager.set_levels({"defense_shields": 2})
        assert gs.max_shields == pytest.approx(150.0)
        assert gs.shields == pytest.approx(150.0)


# ---------------------------------------------------------------------------
# TestRepairs
# ---------------------------------------------------------------------------


class TestRepairs:
    """Verify apply_repair restores shields capped at max_shields."""

    def test_repair_restores_shields(self) -> None:
        """Repair should add to current shields."""
        gs = GameState(shields=50.0, max_shields=100.0)
        manager = UpgradeManager(ShipState(), gs)
        manager.apply_upgrade("repairs")
        assert gs.shields == 80.0  # 50 + 30 effect

    def test_repair_caps_at_max(self) -> None:
        """Repair must not exceed max shields."""
        gs = GameState(shields=95.0, max_shields=100.0)
        manager = UpgradeManager(ShipState(), gs)
        manager.apply_upgrade("repairs")
        assert gs.shields == 100.0

    def test_repair_always_returns_true(self) -> None:
        """Repair is always purchasable regardless of level."""
        gs = GameState(shields=0.0, max_shields=100.0)
        manager = UpgradeManager(ShipState(), gs)
        for _ in range(5):
            assert manager.apply_upgrade("repairs") is True


# ---------------------------------------------------------------------------
# TestScoreMultiplier
# ---------------------------------------------------------------------------


class TestScoreMultiplier:
    """Verify get_score_multiplier returns correct values."""

    def test_no_bonus_returns_one(self, upgrade_manager: UpgradeManager) -> None:
        """Default score multiplier should be 1.0."""
        assert upgrade_manager.get_score_multiplier() == 1.0

    def test_level_one_adds_quarter(self, upgrade_manager: UpgradeManager) -> None:
        """Score bonus level 1 should produce 1.25."""
        upgrade_manager.set_levels({"score_bonus": 1})
        assert upgrade_manager.get_score_multiplier() == pytest.approx(1.25)

    def test_level_two_adds_half(self, upgrade_manager: UpgradeManager) -> None:
        """Score bonus level 2 should produce 1.5."""
        upgrade_manager.set_levels({"score_bonus": 2})
        assert upgrade_manager.get_score_multiplier() == pytest.approx(1.5)

    def test_max_level_score_bonus(self, upgrade_manager: UpgradeManager) -> None:
        """Score bonus at max level (3) should produce 1.75."""
        upgrade_manager.set_levels({"score_bonus": 3})
        assert upgrade_manager.get_score_multiplier() == pytest.approx(1.75)


# ---------------------------------------------------------------------------
# TestSetLevels
# ---------------------------------------------------------------------------


class TestSetLevels:
    """Verify set_levels bulk-restores and recalculates."""

    def test_bulk_restore_updates_all_listed_levels(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Every ID in the levels dict should be updated."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"weapon_fire_rate": 3, "defense_shields": 2})
        assert manager.get_level("weapon_fire_rate") == 3
        assert manager.get_level("defense_shields") == 2

    def test_bulk_restore_recalculates_stats(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Effective stats should reflect bulk-restored levels."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"mobility_turn": 3})
        expected = ship_state.base_turn_rate + (3 * 30.0)
        assert ship_state.effective_turn_rate == pytest.approx(expected)

    def test_bulk_clamps_to_max_level(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Levels exceeding max should be clamped."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"economy_protection": 99})
        assert manager.get_level("economy_protection") == 1  # max_level=1

    def test_repairs_excluded_from_bulk_set(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Repairs should be zeroed during bulk-set regardless of input."""
        manager = UpgradeManager(ship_state, game_state)
        manager.set_levels({"repairs": 5})
        assert manager.get_level("repairs") == 0

    def test_unlisted_levels_default_to_zero(
        self,
        ship_state: ShipState,
        game_state: GameState,
    ) -> None:
        """Omitted upgrades should be set to 0."""
        manager = UpgradeManager(ship_state, game_state)
        manager.apply_upgrade("weapon_fire_rate")
        manager.set_levels({})  # empty — resets everything
        assert manager.get_level("weapon_fire_rate") == 0


# ---------------------------------------------------------------------------
# TestUpgradeDefinitions
# ---------------------------------------------------------------------------


class TestUpgradeDefinitions:
    """Verify the upgrade definition catalog integrity."""

    def test_catalog_has_eleven_entries(self) -> None:
        """The catalog must contain exactly 11 upgrade definitions."""
        assert len(ALL_UPGRADES) == 11

    def test_all_ids_unique(self) -> None:
        """All upgrade IDs must be unique."""
        ids = [u.id for u in ALL_UPGRADES]
        assert len(ids) == len(set(ids))

    def test_compatibility_alias_matches(self) -> None:
        """UPGRADE_DEFINITIONS should be the same object as ALL_UPGRADES."""
        assert UPGRADE_DEFINITIONS is ALL_UPGRADES

    def test_get_upgrade_cost_matches_formula(self) -> None:
        """The standalone cost helper should agree with geometric formula."""
        defn = next(u for u in ALL_UPGRADES if u.id == "weapon_fire_rate")
        for level in range(6):
            expected = int(defn.base_cost * (defn.cost_scaling**level))
            assert get_upgrade_cost(defn, level) == expected
