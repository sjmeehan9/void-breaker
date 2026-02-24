# Phase 4 Component 4.4 — Upgrade Manager & Stat Application

## Summary

Component 4.4 introduces a production `UpgradeManager` that now owns shop-upgrade state transitions and stat application logic. This replaces direct ship-stat mutation in `ShopPhaseState` with a centralized manager API that can be reused by upcoming insurance and economy components.

## Delivered Capabilities

- Tracks upgrade levels for all required upgrades, including `score_bonus`
- Enforces per-upgrade max levels (`can_upgrade`)
- Calculates geometric costs for next purchase (`get_cost`)
- Applies purchases with immediate stat propagation (`apply_upgrade`)
- Handles one-shot shield restore behavior for `repairs` without persistent levelling
- Recalculates effective ship stats from base stats + per-level effects (`recalculate_all_stats`)
- Updates both ship and run-level shield state when shield-capacity upgrades are purchased
- Exposes score multiplier for score systems (`get_score_multiplier`)
- Supports insurance retention workflows via `get_all_levels` and `set_levels`

## Key Implementation Files

- `app/src/managers/upgrade_manager.py`
- `app/src/config/upgrade_definitions.py`
- `app/src/states/shop.py`
- `app/src/config/game_config.py`
- `app/src/managers/__init__.py`
- `tests/test_upgrade_manager.py`

## Upgrade Catalog Notes

The upgrade data source now contains all 11 component-defined upgrades:

- Weapons: fire rate, damage, shot speed, spread shot
- Defense: shields
- Mobility: thrust, turn rate
- Economy: magnet, protection, score bonus
- Repair: repairs (one-shot)

`UPGRADE_DEFINITIONS` remains available as a compatibility alias to the complete `ALL_UPGRADES` catalog.

## Verification

- Targeted tests: `tests/test_upgrade_manager.py`, `tests/test_shop_node.py`, `tests/test_config.py`, `tests/test_shop_phase_state.py`
- Full suite: `156 passed`
- Evals: `python3 scripts/evals.py` passed
