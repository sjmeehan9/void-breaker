# Phase 4 Component 4.5 — Insurance Manager & Death Retention

## Summary

Component 4.5 introduces a standalone `InsuranceManager` responsible for all insurance-specific gameplay rules: tier selection, recurring level-transition charges, and upgrade retention on death.

## Implemented Scope

- Added `InsuranceManager` in `app/src/managers/insurance_manager.py`.
- Added manager export in `app/src/managers/__init__.py`.
- Added focused test coverage in `tests/test_insurance_manager.py`.

## Core Behaviors

- **Tier ownership**: Supports `InsuranceTier.OFF`, `InsuranceTier.BASIC`, and `InsuranceTier.PREMIUM`.
- **State sync**: `set_tier()` updates `InsuranceState.tier`, `cost_per_level`, and `retention_fraction`.
- **Cost scaling**: `get_tier_cost()` applies 10% level-based growth (`base * (1 + level * 0.1)`).
- **Recurring charge**: `deduct_level_cost()` charges at level transition and auto-lapses insurance to `OFF` when unaffordable.
- **Retention logic**:
  - `OFF`: retain 0%
  - `BASIC`: retain 50% (floor)
  - `PREMIUM`: retain 100%
- **Repairs exclusion**: one-shot `repairs` upgrade is excluded from retention payloads.
- **Retention apply**: `apply_retention()` forwards retained levels via `UpgradeManager.set_levels()`.

## Integration Notes

- The manager is intentionally pure business logic and does not directly mutate shop UI.
- Currency charging uses compatibility checks so the manager can operate with both current and upcoming currency APIs (`spend`/`get_balance` and `deduct`/`can_spend`).
- Shop collision/tier-cycling wiring remains in later shop-flow components.
