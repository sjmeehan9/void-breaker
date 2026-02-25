"""Comprehensive tests for InsuranceManager — tier management, cost deduction,
retention calculations, and retention application.
"""

from __future__ import annotations

import pytest
from asterax.app.src.config.game_config import (
    GameState,
    InsuranceState,
    InsuranceTier,
    ShipState,
)
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.insurance_manager import InsuranceManager
from asterax.app.src.managers.upgrade_manager import UpgradeManager

# ---------------------------------------------------------------------------
# Lightweight test doubles for isolation tests
# ---------------------------------------------------------------------------


class _CurrencyStub:
    """Minimal currency collaborator that tracks a simple balance."""

    def __init__(self, balance: int) -> None:
        self.balance = balance

    def can_spend(self, amount: int) -> bool:
        """Return whether the balance covers the amount."""
        return self.balance >= amount

    def deduct(self, amount: int) -> bool:
        """Deduct if affordable, return success."""
        if amount > self.balance:
            return False
        self.balance -= amount
        return True


class _UpgradeStub:
    """Minimal upgrade collaborator exposing level snapshot and bulk set."""

    def __init__(self, levels: dict[str, int]) -> None:
        self.levels = dict(levels)
        self.last_set_levels: dict[str, int] | None = None

    def get_all_levels(self) -> dict[str, int]:
        """Return a copy of the current upgrade levels."""
        return dict(self.levels)

    def set_levels(self, levels: dict[str, int]) -> None:
        """Record the last bulk-set call for assertion."""
        self.last_set_levels = dict(levels)


# ---------------------------------------------------------------------------
# TestInsuranceTiers
# ---------------------------------------------------------------------------


class TestInsuranceTiers:
    """Verify tier set/get and insurance-state synchronisation."""

    def test_set_get_off(self) -> None:
        """OFF tier should have zero cost and zero retention."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.OFF)
        assert mgr.get_tier() is InsuranceTier.OFF
        assert mgr.insurance_state.cost_per_level == 0
        assert mgr.insurance_state.retention_fraction == 0.0

    def test_set_get_basic(self) -> None:
        """BASIC tier should configure 50 cost and 0.5 retention."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.BASIC)
        assert mgr.get_tier() is InsuranceTier.BASIC
        assert mgr.insurance_state.cost_per_level == 50
        assert mgr.insurance_state.retention_fraction == 0.5

    def test_set_get_premium(self) -> None:
        """PREMIUM tier should configure 150 cost and 1.0 retention."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.PREMIUM)
        assert mgr.get_tier() is InsuranceTier.PREMIUM
        assert mgr.insurance_state.cost_per_level == 150
        assert mgr.insurance_state.retention_fraction == 1.0

    def test_tier_change_updates_state_fields(self) -> None:
        """Changing tier should propagate to insurance_state cost and retention."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.BASIC)
        assert mgr.insurance_state.retention_fraction == 0.5
        mgr.set_tier(InsuranceTier.PREMIUM)
        assert mgr.insurance_state.retention_fraction == 1.0
        mgr.set_tier(InsuranceTier.OFF)
        assert mgr.insurance_state.retention_fraction == 0.0


# ---------------------------------------------------------------------------
# TestCostDeduction
# ---------------------------------------------------------------------------


class TestCostDeduction:
    """Verify deduct_level_cost at various game levels and tiers."""

    @pytest.mark.parametrize(
        ("tier", "level", "expected_cost"),
        [
            (InsuranceTier.BASIC, 1, 55),
            (InsuranceTier.BASIC, 5, 75),
            (InsuranceTier.BASIC, 10, 100),
            (InsuranceTier.BASIC, 20, 150),
            (InsuranceTier.PREMIUM, 1, 165),
            (InsuranceTier.PREMIUM, 5, 225),
            (InsuranceTier.PREMIUM, 10, 300),
        ],
        ids=[
            "basic-lv1",
            "basic-lv5",
            "basic-lv10",
            "basic-lv20",
            "premium-lv1",
            "premium-lv5",
            "premium-lv10",
        ],
    )
    def test_get_tier_cost_scales_with_level(
        self,
        tier: InsuranceTier,
        level: int,
        expected_cost: int,
    ) -> None:
        """Tier cost should equal base_cost * (1 + level * 0.1)."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        assert mgr.get_tier_cost(tier, level) == expected_cost

    def test_off_tier_cost_is_zero(self) -> None:
        """OFF tier should have no recurring cost."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        assert mgr.get_tier_cost(InsuranceTier.OFF, 10) == 0

    def test_deduct_succeeds_when_affordable(self) -> None:
        """Insurance deduction should succeed and reduce balance."""
        currency = _CurrencyStub(balance=300)
        mgr = InsuranceManager(InsuranceState(), currency, _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.BASIC)
        assert mgr.deduct_level_cost(current_level=10) is True
        assert currency.balance == 200  # 300 - 100
        assert mgr.get_tier() is InsuranceTier.BASIC
        assert mgr.last_lapse_message is None

    def test_deduct_for_off_tier_is_free(self) -> None:
        """OFF tier deduction should return True with no balance change."""
        currency = _CurrencyStub(balance=50)
        mgr = InsuranceManager(InsuranceState(), currency, _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.OFF)
        assert mgr.deduct_level_cost(current_level=5) is True
        assert currency.balance == 50


# ---------------------------------------------------------------------------
# TestCostDeductionFailure
# ---------------------------------------------------------------------------


class TestCostDeductionFailure:
    """Verify unaffordable deduction triggers downgrade to OFF."""

    def test_unaffordable_downgrades_to_off(self) -> None:
        """Insurance should lapse to OFF when recurring cost is unaffordable."""
        currency = _CurrencyStub(balance=20)
        mgr = InsuranceManager(InsuranceState(), currency, _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.PREMIUM)
        assert mgr.deduct_level_cost(current_level=5) is False
        assert mgr.get_tier() is InsuranceTier.OFF
        assert currency.balance == 20  # unchanged
        assert mgr.last_lapse_message is not None

    def test_lapse_message_includes_tier_name(self) -> None:
        """The lapse message should identify which tier lapsed."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.BASIC)
        mgr.deduct_level_cost(current_level=1)
        assert mgr.last_lapse_message is not None
        assert "basic" in mgr.last_lapse_message.lower()

    def test_lapse_clears_on_next_successful_deduction(self) -> None:
        """Lapse message should clear after a successful subsequent deduction."""
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))
        mgr.set_tier(InsuranceTier.BASIC)
        mgr.deduct_level_cost(current_level=1)  # fails — lapse
        assert mgr.last_lapse_message is not None
        mgr.set_tier(InsuranceTier.OFF)
        mgr.deduct_level_cost(current_level=1)  # OFF is free
        assert mgr.last_lapse_message is None


# ---------------------------------------------------------------------------
# TestRetentionCalculation
# ---------------------------------------------------------------------------


class TestRetentionCalculation:
    """Verify retained upgrade levels by tier."""

    @pytest.mark.parametrize(
        ("tier", "input_levels", "expected"),
        [
            (
                InsuranceTier.OFF,
                {"weapon_fire_rate": 4, "defense_shields": 3},
                {"weapon_fire_rate": 0, "defense_shields": 0},
            ),
            (
                InsuranceTier.BASIC,
                {"weapon_fire_rate": 3, "defense_shields": 4},
                {"weapon_fire_rate": 1, "defense_shields": 2},
            ),
            (
                InsuranceTier.PREMIUM,
                {"weapon_fire_rate": 5, "defense_shields": 3},
                {"weapon_fire_rate": 5, "defense_shields": 3},
            ),
        ],
        ids=["off-retains-zero", "basic-retains-half", "premium-retains-all"],
    )
    def test_retention_matches_tier_fraction(
        self,
        tier: InsuranceTier,
        input_levels: dict[str, int],
        expected: dict[str, int],
    ) -> None:
        """Retained levels should equal int(level * retention_fraction)."""
        upgrades = _UpgradeStub(input_levels)
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)
        mgr.set_tier(tier)
        retained = mgr.calculate_retained_upgrades()
        for key, value in expected.items():
            assert (
                retained[key] == value
            ), f"{key}: expected {value}, got {retained[key]}"


# ---------------------------------------------------------------------------
# TestRetentionExcludesRepairs
# ---------------------------------------------------------------------------


class TestRetentionExcludesRepairs:
    """Verify that repairs are excluded from retention snapshots."""

    def test_repairs_excluded_from_all_tiers(self) -> None:
        """Repairs should never appear in retained levels regardless of tier."""
        levels = {"weapon_fire_rate": 3, "repairs": 5}
        upgrades = _UpgradeStub(levels)
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)
        for tier in InsuranceTier:
            mgr.set_tier(tier)
            retained = mgr.calculate_retained_upgrades()
            assert "repairs" not in retained


# ---------------------------------------------------------------------------
# TestApplyRetention
# ---------------------------------------------------------------------------


class TestApplyRetention:
    """Verify apply_retention forwards correct levels to the upgrade manager."""

    def test_apply_calls_set_levels_with_retained_values(self) -> None:
        """apply_retention should call upgrade_manager.set_levels with retained map."""
        upgrades = _UpgradeStub({"weapon_fire_rate": 5, "repairs": 1})
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)
        mgr.set_tier(InsuranceTier.BASIC)
        mgr.apply_retention()
        assert upgrades.last_set_levels == {"weapon_fire_rate": 2}

    def test_apply_with_premium_preserves_all_levels(self) -> None:
        """PREMIUM retention should forward all original levels."""
        levels = {"weapon_fire_rate": 4, "defense_shields": 2}
        upgrades = _UpgradeStub(levels)
        mgr = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)
        mgr.set_tier(InsuranceTier.PREMIUM)
        mgr.apply_retention()
        assert upgrades.last_set_levels == levels


# ---------------------------------------------------------------------------
# Integration: InsuranceManager with real managers
# ---------------------------------------------------------------------------


class TestInsuranceManagerIntegration:
    """Verify InsuranceManager works with real CurrencyManager and UpgradeManager."""

    def test_insurance_cycle_with_real_managers(self) -> None:
        """Full cycle: buy BASIC, deduct, verify retention, apply retention."""
        game_state = GameState(currency=1000)
        ship_state = ShipState()
        currency_mgr = CurrencyManager(game_state)
        upgrade_mgr = UpgradeManager(ship_state, game_state)
        insurance_mgr = InsuranceManager(
            game_state.insurance, currency_mgr, upgrade_mgr
        )

        # Set up some upgrades
        upgrade_mgr.set_levels({"weapon_fire_rate": 4, "defense_shields": 2})

        # Activate BASIC insurance
        insurance_mgr.set_tier(InsuranceTier.BASIC)
        assert insurance_mgr.deduct_level_cost(current_level=1) is True  # cost 55
        assert game_state.currency == 945

        # Verify retention
        retained = insurance_mgr.calculate_retained_upgrades()
        assert retained["weapon_fire_rate"] == 2  # int(4 * 0.5)
        assert retained["defense_shields"] == 1  # int(2 * 0.5)

    def test_multi_level_insurance_deduction(self) -> None:
        """Insurance cost deducted over 3 levels, then lapse on insufficient funds."""
        game_state = GameState(currency=200)
        currency_mgr = CurrencyManager(game_state)
        upgrade_mgr = UpgradeManager(ShipState(), game_state)
        insurance_mgr = InsuranceManager(
            game_state.insurance, currency_mgr, upgrade_mgr
        )

        insurance_mgr.set_tier(InsuranceTier.BASIC)

        # Level 1: cost = 55, balance -> 145
        assert insurance_mgr.deduct_level_cost(1) is True
        assert game_state.currency == 145

        # Level 2: cost = 60, balance -> 85
        assert insurance_mgr.deduct_level_cost(2) is True
        assert game_state.currency == 85

        # Level 3: cost = 65, balance -> 20
        assert insurance_mgr.deduct_level_cost(3) is True
        assert game_state.currency == 20

        # Level 4: cost = 70, unaffordable -> lapse to OFF
        assert insurance_mgr.deduct_level_cost(4) is False
        assert insurance_mgr.get_tier() is InsuranceTier.OFF
        assert game_state.currency == 20  # unchanged
