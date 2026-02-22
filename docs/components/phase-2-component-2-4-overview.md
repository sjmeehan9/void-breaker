# Phase 2 Component 2.4 Overview — Projectile System & Collision Detection

## Summary
Component 2.4 delivers the complete projectile/combat collision backbone for Phase 2:

- Player-fired `Projectile` entities with velocity and max-range expiry
- Fire cooldown enforcement on `PlayerShip`
- Ship invulnerability timer to avoid repeated contact damage
- `CollisionSystem` with ghost sprites for wrap-around seam collisions
- Projectile-vs-asteroid and ship-vs-asteroid collision response
- `ScoreManager` asteroid point accumulation

## Implemented Files
- `app/src/entities/projectile.py`
- `app/src/entities/player_ship.py` (updated)
- `app/src/physics/engine.py` (updated)
- `app/src/physics/collisions.py`
- `app/src/managers/score_manager.py`
- `app/src/config/game_config.py` (added `CollisionConfig`)
- Package exports updated in:
  - `app/src/entities/__init__.py`
  - `app/src/physics/__init__.py`
  - `app/src/managers/__init__.py`

## Design Notes
- Ghost sprite generation is edge-aware and corner-aware (including diagonal ghosts).
- Ghosts are never added to persistent entity collections; they exist only during collision checks.
- `check_all()` uses pair-specific methods to keep extension points clear for Phase 3 enemy collisions.
- `PlayerShip.tick_cooldowns()` remains available and delegates to `update_cooldown()` for backward compatibility.

## Test Coverage Added
`tests/test_projectile_collisions.py` validates:
- projectile direction/speed movement
- projectile expiry at max range
- fire cooldown behavior
- projectile->asteroid destruction/splitting
- ship->asteroid damage
- ghost creation/cleanup lifecycle
- seam collision correctness (right-edge projectile hitting left-edge asteroid)
- score increments by asteroid size

## Validation
- `pytest -q tests/test_projectile_collisions.py tests/test_asteroid_system.py tests/test_player_ship_physics.py`
- `black --check app/src tests`
- `isort --check-only app/src tests`
