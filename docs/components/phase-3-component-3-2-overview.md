# Component 3.2 — Enemy Ship Entities & AI Overview

## Summary

Component 3.2 introduces the first enemy combat entities for Phase 3. The implementation adds two archetype-driven enemy profiles (Basic and Aggressive), plus an `EnemyShip` sprite entity with movement AI, telegraphed attacks, timed firing logic, and destruction metadata for score/drop systems.

## What Was Implemented

- **Archetype config module**: `app/src/config/enemy_config.py`
  - `EnemyArchetype`: `BASIC`, `AGGRESSIVE`
  - `EnemyConfig` dataclass with speed, turn rate, fire rate/cooldown, health, points, accuracy, telegraph duration, spawn grace period, projectile stats, and drop chances
  - Factory helpers:
    - `get_basic_config()` (slow movement, lower fire rate, 1 HP, 200 points)
    - `get_aggressive_config()` (faster movement, higher fire rate, 2 HP, 500 points)

- **Enemy entity**: `app/src/entities/enemy_ship.py`
  - `EnemyShip` extends `arcade.Sprite`
  - Steering movement toward player with bounded turn rate and ±10° jitter
  - `try_fire()` attack flow:
    - respects spawn grace period
    - starts telegraph windup
    - flashes alpha during telegraph
    - emits projectile after telegraph and starts cooldown
  - Aiming logic:
    - Basic: current-position aim
    - Aggressive: lead prediction using player velocity and projectile speed
  - `take_damage()` returns destroyed state
  - `on_destroyed()` returns score/drop metadata for managers

## Testing

- Added `tests/test_enemy_ship.py` covering:
  - config defaults/factories
  - archetype instantiation
  - movement toward player
  - spawn grace and cooldown constraints
  - telegraph state transitions
  - damage/death behaviour
  - basic vs aggressive targeting differences

All focused tests for this component pass in the sandbox.
