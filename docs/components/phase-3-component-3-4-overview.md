# Phase 3 Component 3.4 — Spawn Manager & Enemy Waves

## Overview
Component 3.4 adds timed enemy spawning to combat while preserving existing asteroid spawning behavior. Enemies are spawned from screen edges, capped per level, and mixed by archetype using level-driven difficulty parameters.

## What Was Implemented

### 1) Difficulty model updates
- **File**: `app/src/config/game_config.py`
- Added `aggressive_ratio: float = 0.0` to `DifficultyParams`.
- Retained default enemy-off behavior for backward compatibility.

- **File**: `app/src/config/difficulty_tables.py`
- Extended `get_difficulty_params(level)` with Phase 3 enemy progression:
  - Levels **1-5**: enemies disabled.
  - Levels **6+**: enemies enabled with scaling:
    - `enemy_count_max`: 1 → 3 (L10) → 5 (L15) → 8 (L20+)
    - `enemy_spawn_interval`: 8.0s at L6 to 3.0s by L20+
    - `aggressive_ratio`: 0.0 at L6, 0.3 by L10, 0.5 by L15, 0.7 by L25+
    - `enemy_aggression`: 0.3 at L6 to 0.9 by L25+
- Updated `get_difficulty()` to propagate `aggressive_ratio`.

### 2) Spawn manager enemy API
- **File**: `app/src/managers/spawn_manager.py`
- Added enemy spawn state:
  - `_enemy_spawn_timer: float`
  - `_enemy_spawn_active: bool`
- Added methods:
  - `update_enemy_spawning(...) -> list[EnemyShip]`
  - `_get_spawn_edge_position(...) -> tuple[float, float, float, float]`
  - `_select_archetype(...) -> EnemyArchetype`
  - `reset_enemy_spawning() -> None`
- Behavior:
  - No spawning when disabled.
  - Interval timer-based spawn attempts.
  - Enforces `enemy_count_max` cap.
  - Spawns one enemy per eligible interval.
  - Chooses BASIC/AGGRESSIVE using `aggressive_ratio`.
  - Spawns 50px off-screen with inward velocity toward center + jitter.

### 3) Combat loop integration
- **File**: `app/src/states/combat.py`
- Added `_spawn_enemies()` call in `_physics_step()`.
- Added `reset_enemy_spawning()` at combat start and on level advance.
- New enemies are appended to `entity_manager.enemies`.

## Testing

### New tests
- **File**: `tests/test_spawn_manager_enemies.py`
- Covers:
  - disabled spawning
  - interval timing
  - cap enforcement
  - edge spawn position + inward velocity
  - archetype weighting by `aggressive_ratio`
  - timer reset behavior
  - 30-second simulation sanity check

### Updated tests
- `tests/test_asteroid_system.py`
- `tests/test_difficulty.py`
- `tests/test_config.py`
- `tests/test_combat_phase_state.py`

These updates align existing assumptions with Phase 3 behavior (enemies enabled from level 6 onward).

## Design Notes
- Interval spawning was chosen over multi-enemy wave bursts for predictable pacing and minimal integration risk.
- Enemy spawning remains independent of asteroid clear conditions; level transitions still key off asteroid completion.
- Existing Phase 2 asteroid spawning and collision flows are preserved.
