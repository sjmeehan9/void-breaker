# Component 2.2 Overview — Player Ship Entity & Physics

## Summary
Component 2.2 delivers the first playable combat control layer by implementing the player ship entity, inertial movement physics, and shared wrap-around behavior. The previous combat placeholder now spawns and updates a controllable ship every fixed-timestep update.

## Implemented Scope
- `PlayerShip` entity with explicit physics state (`velocity_x`, `velocity_y`)
- Inertial movement primitives:
  - `apply_thrust(dt)`
  - `apply_rotation(dt, direction)`
  - `apply_drag(dt)`
  - `apply_brake(dt)`
  - `cap_speed()`
  - `update_position(dt)`
- Shield and damage model:
  - `shields` initialized from config max
  - `take_damage(amount) -> bool` returns death state at depletion
- Cooldown ticking for future projectile system integration (`fire_cooldown_remaining`)
- Shared wrap utility `wrap_entity(entity, width, height)` for all edge cases
- `PhysicsEngine` orchestration for reading held actions from `InputManager` and applying fixed-step ship simulation

## Files
### Created
- `app/src/entities/player_ship.py`
- `app/src/physics/wrap.py`
- `app/src/physics/engine.py`
- `tests/test_player_ship_physics.py`

### Modified
- `app/src/config/game_config.py`
- `app/src/entities/__init__.py`
- `app/src/physics/__init__.py`
- `app/src/states/combat.py`
- `docs/implementation-context-phase-2.md`

## Design Notes
- Movement uses explicit ship-owned velocity fields instead of Arcade's `change_x/change_y` for deterministic logic and testability.
- Physics constants are grouped in new `PhysicsConfig` (`PHYSICS_CONFIG`) to isolate gameplay tuning from broader window/app constants.
- The combat state integration remains intentionally minimal (ship + movement + shortcuts) so subsequent components can add asteroids/projectiles/collisions incrementally without reworking control flow.

## Verification
- Targeted tests for component behavior passed:
  - thrust direction and acceleration
  - natural drag deceleration
  - brake vs natural drag strength
  - speed cap enforcement
  - rotation rate correctness
  - all four wrap-edge transitions
  - damage/death threshold logic
- Project checks passed:
  - `pytest -q`
  - `black --check app/src`
  - `isort --check-only app/src`
  - `python scripts/evals.py`

## Notable Compatibility Choice
- `PhysicsConfig` uses the Component 2.2 spec defaults (`base_fire_rate=5.0`, `base_projectile_range=600.0`) while existing legacy defaults in `GameConfig` remain unchanged to avoid regressions for earlier-phase consumers. Subsequent components should source ship physics from `PHYSICS_CONFIG`.
