"""Unit tests for insurance tier management and retention behavior."""

from __future__ import annotations

from asterax.app.src.config.game_config import InsuranceState, InsuranceTier
from asterax.app.src.managers.insurance_manager import InsuranceManager


class _CurrencyStub:
    """Currency test double with spend/deduct and can-spend semantics."""

    def __init__(self, balance: int) -> None:
        self.balance = balance

    def can_spend(self, amount: int) -> bool:
        return self.balance >= amount

    def deduct(self, amount: int) -> bool:
        if amount > self.balance:
            return False
        self.balance -= amount
        return True


class _UpgradeStub:
    """Upgrade test double exposing level snapshot and bulk set APIs."""

    def __init__(self, levels: dict[str, int]) -> None:
        self.levels = dict(levels)
        self.last_set_levels: dict[str, int] | None = None

    def get_all_levels(self) -> dict[str, int]:
        return dict(self.levels)

    def set_levels(self, levels: dict[str, int]) -> None:
        self.last_set_levels = dict(levels)


def test_set_tier_updates_insurance_state_fields() -> None:
    """Changing tiers should keep state tier/cost/retention in sync."""
    manager = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))

    manager.set_tier(InsuranceTier.BASIC)
    assert manager.get_tier() is InsuranceTier.BASIC
    assert manager.insurance_state.cost_per_level == 50
    assert manager.insurance_state.retention_fraction == 0.5

    manager.set_tier(InsuranceTier.PREMIUM)
    assert manager.insurance_state.cost_per_level == 150
    assert manager.insurance_state.retention_fraction == 1.0


def test_get_tier_cost_scales_with_level() -> None:
    """Tier costs should scale by 10 percent per level."""
    manager = InsuranceManager(InsuranceState(), _CurrencyStub(0), _UpgradeStub({}))

    assert manager.get_tier_cost(InsuranceTier.BASIC, 1) == 55
    assert manager.get_tier_cost(InsuranceTier.BASIC, 5) == 75
    assert manager.get_tier_cost(InsuranceTier.BASIC, 10) == 100
    assert manager.get_tier_cost(InsuranceTier.BASIC, 20) == 150

    assert manager.get_tier_cost(InsuranceTier.PREMIUM, 1) == 165
    assert manager.get_tier_cost(InsuranceTier.PREMIUM, 10) == 300


def test_deduct_level_cost_spends_when_affordable() -> None:
    """Recurring insurance cost should deduct currency when balance allows."""
    currency = _CurrencyStub(balance=300)
    manager = InsuranceManager(InsuranceState(), currency, _UpgradeStub({}))
    manager.set_tier(InsuranceTier.BASIC)

    assert manager.deduct_level_cost(current_level=10)
    assert currency.balance == 200
    assert manager.get_tier() is InsuranceTier.BASIC
    assert manager.last_lapse_message is None


def test_deduct_level_cost_downgrades_when_unaffordable() -> None:
    """Insurance should lapse to OFF when recurring cost cannot be paid."""
    currency = _CurrencyStub(balance=20)
    manager = InsuranceManager(InsuranceState(), currency, _UpgradeStub({}))
    manager.set_tier(InsuranceTier.PREMIUM)

    assert not manager.deduct_level_cost(current_level=5)
    assert manager.get_tier() is InsuranceTier.OFF
    assert currency.balance == 20
    assert manager.last_lapse_message is not None


def test_calculate_retained_upgrades_by_tier_and_skip_repairs() -> None:
    """Retention should match active tier fraction and exclude repairs."""
    levels = {"weapon_fire_rate": 3, "defense_shields": 4, "repairs": 2}
    upgrades = _UpgradeStub(levels)
    manager = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)

    manager.set_tier(InsuranceTier.OFF)
    assert manager.calculate_retained_upgrades() == {
        "weapon_fire_rate": 0,
        "defense_shields": 0,
    }

    manager.set_tier(InsuranceTier.BASIC)
    assert manager.calculate_retained_upgrades() == {
        "weapon_fire_rate": 1,
        "defense_shields": 2,
    }

    manager.set_tier(InsuranceTier.PREMIUM)
    assert manager.calculate_retained_upgrades() == {
        "weapon_fire_rate": 3,
        "defense_shields": 4,
    }


def test_apply_retention_passes_calculated_levels_to_upgrade_manager() -> None:
    """Applying retention should forward retained levels via set_levels()."""
    upgrades = _UpgradeStub({"weapon_fire_rate": 5, "repairs": 1})
    manager = InsuranceManager(InsuranceState(), _CurrencyStub(0), upgrades)
    manager.set_tier(InsuranceTier.BASIC)

    manager.apply_retention()

    assert upgrades.last_set_levels == {"weapon_fire_rate": 2}
