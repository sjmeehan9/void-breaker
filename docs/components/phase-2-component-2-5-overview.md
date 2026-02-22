# Phase 2 Component 2.5 Overview — Currency Pickups & Collection

## Summary
Component 2.5 introduces the full currency pickup loop for combat:

- Asteroid destruction now performs a probability-based currency drop roll.
- Successful rolls spawn drifting `CurrencyPickup` entities at asteroid death positions.
- Pickups expire after a configurable lifetime and wrap at screen edges.
- Ship contact collects pickups, updates `GameState.currency`, and credits `CurrencyManager`.
- Currency accounting now supports earn/spend/reset with total earned/spent tracking.

## Implemented Files
- `app/src/entities/pickups.py`
- `app/src/managers/currency_manager.py`
- `app/src/physics/collisions.py` (updated)
- `app/src/physics/engine.py` (updated)
- `app/src/config/game_config.py` (added `CurrencyConfig` + `CURRENCY_CONFIG`)
- `app/src/entities/__init__.py` and `app/src/managers/__init__.py` (exports)
- `tests/test_currency_pickups.py`

## Design Notes
- `CurrencyPickup` constructor supports RNG injection for deterministic tests.
- Collision integration is backward compatible: `CollisionSystem.check_all()` accepts optional currency/audio managers.
- Pickup spawning is localized to `_spawn_currency_pickup()` for minimal coupling and easy extension in later phases.

## Validation
- `pytest -q tests/test_currency_pickups.py tests/test_projectile_collisions.py tests/test_config.py`
- `black app/src tests`
- `isort app/src tests`
