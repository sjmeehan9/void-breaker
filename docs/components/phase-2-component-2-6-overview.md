# Phase 2 Component 2.6 Overview — Entity Manager & Rendering Pipeline

## Summary
Component 2.6 introduces the shared rendering/data-ownership layer for combat entities:

- Added `EntityManager` as the single owner of typed gameplay SpriteLists (`asteroids`, `player_projectiles`, `currency_pickups`, `particles`) plus active player ship.
- Added deterministic draw ordering via `EntityManager.draw()` with optional starfield integration (`background -> asteroids -> pickups -> particles -> projectiles -> ship`).
- Added focused add/remove helpers and clear helpers (`clear_projectiles`, `clear_all`) to avoid ad-hoc SpriteList manipulation.
- Added `ParticleSystem` for short-lived explosion bursts with per-size particle counts, radial velocity, alpha fade, and automatic expiry cleanup.
- Wired explosion spawning into asteroid-destruction collision flow through an optional `particle_system` parameter on `CollisionSystem.check_all()`.

## Implemented Files
- `app/src/managers/entity_manager.py` (new)
- `app/src/rendering/particle_system.py` (new)
- `app/src/managers/__init__.py` (export update)
- `app/src/rendering/__init__.py` (export update)
- `app/src/physics/collisions.py` (particle spawn hook)
- `tests/test_entity_manager_rendering.py` (new)

## Design Notes
- Kept collision integration backward compatible by making particle-system injection optional.
- Preserved existing `player_ship` access pattern through a property alias while exposing the component-spec `player` field.
- Stored particle sprites in the manager-owned `particles` list so Phase 2.7 can render/update through a single integration point.

## Validation
- `python -m pytest -q tests/test_entity_manager_rendering.py tests/test_projectile_collisions.py`
- `python -m black --check app/src tests`
- `python -m isort --check-only app/src tests`
