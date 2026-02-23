# Component 3.3 — Enemy Projectile System & Expanded Collisions Overview

## Summary

Component 3.3 connects Phase 3 enemy AI output to core combat: enemies now exist as managed render/update entities, enemy-fired projectiles are tracked independently, and enemy-related collision pairs are resolved with the same seam-safe ghost wrapping used in Phase 2 asteroid collisions.

## What Was Implemented

- **Enemy collections in EntityManager**
  - Added `enemies: arcade.SpriteList[EnemyShip]`
  - Added `enemy_projectiles: arcade.SpriteList[Projectile]`
  - Added `clear_enemies()` and wired it into `clear_all()`
  - Updated render order to: asteroids -> pickups -> particles -> enemies -> enemy projectiles -> player projectiles -> player

- **Projectile ownership formalized**
  - Added `ProjectileOwner` enum (`PLAYER`, `ENEMY`) in `app/src/entities/projectile.py`
  - Added `owner` field on `Projectile` constructor (default `PLAYER`)
  - Updated `EnemyShip` to tag spawned shots as `ProjectileOwner.ENEMY`

- **Expanded collision APIs**
  - Added to `CollisionSystem`:
    - `check_player_vs_enemy_projectiles()`
    - `check_player_projectiles_vs_enemies()`
    - `check_player_vs_enemies()`
    - `check_all_combat()`
  - Added reusable seam-aware helper for source-vs-list collisions that checks:
    - direct collisions
    - source ghosts vs real targets
    - real source vs target ghosts
    - source ghosts vs target ghosts

- **Combat loop integration**
  - Added `CombatPhaseState._update_enemies(dt, screen_width, screen_height)`:
    - updates enemy AI
    - wraps enemies
    - spawns enemy projectiles from `try_fire()`
    - updates/wraps enemy projectiles and removes expired shots
  - Added `CombatPhaseState._process_enemy_collisions(...)`:
    - enemy projectile hit -> player damage + projectile removal
    - player projectile hit enemy -> enemy damage, projectile removal, destruction handling
    - player/enemy body collision -> damage to both, enemy destruction handling
  - Added `_handle_enemy_destroyed()` for score/stat updates and enemy removal

## Testing

- Added `tests/test_enemy_projectile_collisions.py` covering:
  - wrap-around ghost collision for player vs enemy projectile
  - player projectile vs enemy collision detection
  - combat-side enemy projectile spawn + lifetime expiry
  - combat-side enemy/player collision processing (damage, cleanup, score)
- Updated `tests/test_entity_manager_rendering.py` to validate enemy list initialization, draw order, and clear behavior.

Targeted collision/combat tests pass in the sandbox.
