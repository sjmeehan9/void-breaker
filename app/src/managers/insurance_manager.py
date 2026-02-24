"""Insurance tier management and upgrade retention logic."""

from __future__ import annotations

from dataclasses import dataclass

from asterax.app.src.config.game_config import InsuranceState, InsuranceTier


@dataclass(frozen=True, slots=True)
class _InsuranceTierConfig:
    """Static cost and retention configuration for an insurance tier."""

    base_cost_per_level: int
    retention_fraction: float


class InsuranceManager:
    """Manage insurance tier selection, recurring costs, and retention on death."""

    _TIER_CONFIG: dict[InsuranceTier, _InsuranceTierConfig] = {
        InsuranceTier.OFF: _InsuranceTierConfig(
            base_cost_per_level=0,
            retention_fraction=0.0,
        ),
        InsuranceTier.BASIC: _InsuranceTierConfig(
            base_cost_per_level=50,
            retention_fraction=0.5,
        ),
        InsuranceTier.PREMIUM: _InsuranceTierConfig(
            base_cost_per_level=150,
            retention_fraction=1.0,
        ),
    }

    def __init__(
        self,
        insurance_state: InsuranceState,
        currency_manager: object,
        upgrade_manager: object,
    ) -> None:
        """Initialise the manager with state and collaborator references."""
        self.insurance_state = insurance_state
        self.currency_manager = currency_manager
        self.upgrade_manager = upgrade_manager
        self.last_lapse_message: str | None = None
        self.set_tier(self.insurance_state.tier)

    def set_tier(self, tier: InsuranceTier) -> None:
        """Set the active insurance tier and synchronise insurance-state fields."""
        config = self._TIER_CONFIG[tier]
        self.insurance_state.tier = tier
        self.insurance_state.cost_per_level = config.base_cost_per_level
        self.insurance_state.retention_fraction = config.retention_fraction

    def get_tier(self) -> InsuranceTier:
        """Return the currently active insurance tier."""
        return self.insurance_state.tier

    def get_tier_cost(self, tier: InsuranceTier, current_level: int) -> int:
        """Return the insurance charge for a tier at the provided game level."""
        config = self._TIER_CONFIG[tier]
        level = max(0, current_level)
        return int(config.base_cost_per_level * (1 + (level * 0.1)))

    def deduct_level_cost(self, current_level: int) -> bool:
        """Deduct recurring insurance cost at a level transition when affordable."""
        tier = self.get_tier()
        cost = self.get_tier_cost(tier, current_level)
        if cost <= 0:
            self.last_lapse_message = None
            return True
        if not self._can_spend(cost):
            self.set_tier(InsuranceTier.OFF)
            self.last_lapse_message = f"Insurance lapsed — cannot afford {tier.value}"
            return False
        spent = self._deduct(cost)
        if not spent:
            self.set_tier(InsuranceTier.OFF)
            self.last_lapse_message = f"Insurance lapsed — cannot afford {tier.value}"
            return False
        self.last_lapse_message = None
        return True

    def calculate_retained_upgrades(self) -> dict[str, int]:
        """Calculate retained upgrade levels from current tier retention fraction."""
        retention_fraction = self._TIER_CONFIG[self.get_tier()].retention_fraction
        retained_levels: dict[str, int] = {}
        for upgrade_id, current_level in self.upgrade_manager.get_all_levels().items():
            if upgrade_id == "repairs":
                continue
            retained_levels[upgrade_id] = int(
                max(0, current_level) * retention_fraction
            )
        return retained_levels

    def apply_retention(self) -> None:
        """Apply retained levels to the upgrade manager after death/restart."""
        self.upgrade_manager.set_levels(self.calculate_retained_upgrades())

    def _can_spend(self, amount: int) -> bool:
        """Return whether the wired currency manager can cover the amount."""
        if hasattr(self.currency_manager, "can_spend"):
            return bool(self.currency_manager.can_spend(amount))
        if hasattr(self.currency_manager, "get_balance"):
            return bool(self.currency_manager.get_balance() >= amount)
        return bool(hasattr(self.currency_manager, "spend"))

    def _deduct(self, amount: int) -> bool:
        """Deduct currency using the best available collaborator method."""
        if hasattr(self.currency_manager, "deduct"):
            return bool(self.currency_manager.deduct(amount))
        if hasattr(self.currency_manager, "spend"):
            return bool(self.currency_manager.spend(amount))
        raise AttributeError("Currency manager must implement deduct() or spend().")
