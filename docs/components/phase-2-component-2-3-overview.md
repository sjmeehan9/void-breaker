# Phase 2 Component 2.3 — Asteroid System Overview

## Summary

Component 2.3 introduces the asteroid gameplay backbone for combat:
- Three asteroid size tiers (`LARGE`, `MEDIUM`, `SMALL`)
- Per-size scoring and currency-drop metadata
- Deterministic-friendly split and spawn logic
- Level-based asteroid-only difficulty scaling for Phase 2

## Delivered Implementation

### 1) Asteroid Entity
- Implemented `Asteroid` in `app/src/entities/asteroid.py` as an `arcade.Sprite` subclass.
- Supports:
  - Velocity-based movement (`velocity_x`, `velocity_y`)
  - Rotation via `rotation_speed`
  - `split()` rules:
    - `LARGE -> 2..3 MEDIUM`
    - `MEDIUM -> 2..3 SMALL`
    - `SMALL -> []`
  - `on_destroyed()` payload for collision handling (`point_value`, `currency_drop_chance`, `children`).

### 2) Asteroid Configuration
- Added `AsteroidConfig` and `ASTEROID_CONFIG` in `app/src/config/game_config.py`.
- Centralized:
  - Sprite paths and scale factors per size
  - Point values: large 20, medium 50, small 100
  - Drop chances: large 0.2, medium 0.35, small 0.5
  - Split ranges: child count 2..3, speed multiplier 1.2..1.5

### 3) Spawn Manager
- Added `SpawnManager` in `app/src/managers/spawn_manager.py`.
- `spawn_level_asteroids(...)`:
  - Reads `get_difficulty_params(level)`
  - Spawns large asteroids with randomized heading/speed/rotation
  - Enforces minimum spawn distance of 150px from player position
- `spawn_child_asteroids(parent)` delegates child creation to entity split logic.

### 4) Difficulty Table Integration
- Added `get_difficulty_params(level)` to `app/src/config/difficulty_tables.py`.
- Level scaling behavior:
  - Starts at 4 asteroids, 50–100 speed
  - Increases count/speed by level with caps (20 asteroids, up to 350 max speed)
  - Keeps enemy spawning disabled for all Phase 2 levels

### 5) Physics Engine Extension
- Updated `app/src/physics/engine.py` to update and wrap asteroids when an `asteroids` collection is available on the entity manager.

## Validation
- Added focused tests in `tests/test_asteroid_system.py`:
  - Movement/rotation updates
  - Split outcomes across all size tiers
  - Child speed multiplier bounds
  - Spawn distance guarantees
  - Difficulty scaling checks (levels 1–30)
- Updated `tests/test_config.py` expectations for asteroid-only Phase 2 difficulty.
