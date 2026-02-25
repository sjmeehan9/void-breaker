# Component 4.7 — Ship Re-Centring & Purchase Flow Polish

## Summary
Component 4.7 finalised the shop interaction loop by adding smooth ship re-centring after successful purchases, collision lockout during interpolation, insurance node tier-cycling purchases, and polished Continue handling.

## Implemented Behaviour
- Added a 0.3-second ease-out re-centring interpolation after successful upgrade and insurance purchases.
- Disabled node collision processing while re-centring is active to prevent accidental double-purchases.
- Routed upgrade purchases through `CurrencyManager.spend()` and `UpgradeManager.apply_upgrade()` with denied-flow handling.
- Added insurance node purchase flow: cycle tier `OFF -> BASIC -> PREMIUM -> OFF`, charge via `CurrencyManager`, then apply via `InsuranceManager.set_tier()`.
- Unified Continue flow for both node collision and Enter key shortcut via `_handle_continue()`.
- Continue flow now plays `level_clear`, applies recurring insurance deduction (`InsuranceManager.deduct_level_cost()`), then transitions to combat.
- Added node metadata properties (`upgrade_id`, `is_insurance_node`, `is_continue_node`) for explicit collision branching.

## Files Updated
- `app/src/states/shop.py`
- `app/src/entities/shop_node.py`
- `tests/test_shop_phase_state.py`
- `tests/test_shop_node.py`

## Validation
- `pytest -q tests/test_shop_node.py tests/test_shop_phase_state.py`
- `pytest -q tests/test_insurance_manager.py tests/test_currency.py`

All tests passed.
