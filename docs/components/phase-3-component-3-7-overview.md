# Phase 3 Component 3.7 — Buff Pickups Overview

## Summary
Component 3.7 adds optional enemy-dropped buff pickups to combat. The system introduces three pickup types, timed buff management, and combat-loop integration for spawn, collection, and expiry.

## Implemented Features
- **Buff pickup entity**
  - New `BuffType` enum: `HEAL`, `DAMAGE_BOOST`, `SPEED_BOOST`
  - New `BuffPickup` sprite with:
    - distinct per-type procedural colour texture
    - 10-second pickup lifetime
    - gentle bobbing animation
- **Buff manager**
  - New `BuffManager` with:
    - `apply_buff()` for instant/timed effects
    - `update()` for timer decay and expiry cleanup
    - `get_active_buffs()` for downstream HUD integration
    - `clear_all()` for safe teardown/reset
- **Combat integration**
  - Enemy death now rolls `buff_drop_chance` and spawns one weighted random buff pickup:
    - HEAL 40%
    - DAMAGE_BOOST 30%
    - SPEED_BOOST 30%
  - Added player-vs-buff collision pair to `CollisionSystem`
  - Buff collection applies effect via `BuffManager`, removes pickup, and plays pickup sound
- **Player stat integration**
  - `PlayerShip` now supports temporary multipliers:
    - damage multiplier influences projectile damage on fire
    - speed multiplier influences thrust acceleration

## Key Files
- `app/src/entities/buff_pickup.py` (new)
- `app/src/managers/buff_manager.py` (new)
- `app/src/entities/player_ship.py`
- `app/src/managers/entity_manager.py`
- `app/src/physics/collisions.py`
- `app/src/states/combat.py`
- `tests/test_buff_pickups.py` (new)
- `tests/test_entity_manager_rendering.py`

## Validation
- Added focused buff tests for:
  - pickup creation and expiry
  - HEAL application and cap behavior
  - DAMAGE/SPEED boost apply + expiry
  - same-type refresh semantics (non-stacking)
  - manager `clear_all()` behavior
  - combat drop + collection path
- Existing enemy collision and rendering tests remain passing with buff integration.
