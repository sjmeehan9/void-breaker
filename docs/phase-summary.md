# Phase Summary

## Phase 1 Overview

Phase 1 delivered the complete development environment, project structure, and foundational subsystems for VoidBreaker. It produced a running Arcade window with a functional state machine, persistence layer, input management, centralised game configuration, audio skeleton, and starfield rendering. No gameplay was implemented — this phase established the architectural scaffold consumed by all subsequent phases.

## Components Delivered

### Component 1.1 — Human Setup & Environment
- **What was built:** Python 3.13 virtual environment, `pyproject.toml` with editable install (`setuptools`, `asterax` namespace mapping), `.env` files for local/test/example environments, and `.python-version`.
- **Key files:** `pyproject.toml`, `.env/.env.example`, `.env/.env.test`, `.python-version`
- **Design decisions:** Used `setuptools` with `package-dir` mapping `asterax` to `.` to enable `python -m asterax.app.src.main` as the canonical launch command.

### Component 1.2 — Project Structure & Entry Point
- **What was built:** Full directory scaffold, minimal `main.py` entry point, and `VoidBreakerWindow` with a fixed-timestep accumulator (`PHYSICS_DT = 1/60`, `MAX_FRAME_TIME = 0.25`). Added `scripts/evals.py` for docstring and TODO/FIXME enforcement.
- **Key files:** `app/src/main.py`, `app/src/window.py`, `scripts/evals.py`, `tests/test_main.py`, `tests/test_window.py`
- **Design decisions:** Kept `main.py` minimal (window construction + `arcade.run()` only) and isolated timing logic in `window.py`.

### Component 1.3 — State Machine
- **What was built:** `GameState` protocol, `BaseState` base class, stack-based `StateMachine` with `switch`/`push`/`pop` transitions, and nine concrete stub states (MainMenu, GameInit, Combat, Shop, GameOver, Pause, HowToPlay, HighScores, Settings). Wired into `VoidBreakerWindow` for update/draw/input delegation.
- **Key files:** `app/src/states/base_state.py`, `app/src/states/state_machine.py`, `app/src/states/main_menu.py`, `app/src/states/combat.py`, `app/src/states/shop.py`, `app/src/states/game_over.py`, `app/src/states/pause.py`, `app/src/states/how_to_play.py`, `app/src/states/high_scores.py`, `app/src/states/settings_screen.py`, `app/src/states/game_init.py`, `tests/test_state_machine.py`
- **Design decisions:** Pause implemented as a pushed overlay with dim effect. Transition imports kept local to handlers to avoid circular dependencies. GameInit acts as an immediate handoff to Combat for Phase 1.

### Component 1.4 — Persistence Layer
- **What was built:** `PersistenceManager` with JSON read/write, atomic saves (`NamedTemporaryFile` + `os.replace` + `fsync`), schema versioning, and corrupt-file fallback to defaults. `GameSettings` and `HighScoreEntry` dataclasses with `to_dict`/`from_dict` serialisation.
- **Key files:** `app/src/persistence/schemas.py`, `app/src/persistence/persistence_manager.py`, `app/config/settings_defaults.yaml`, `tests/test_persistence.py`
- **Design decisions:** Key bindings persisted as human-readable string names. High score entries capped at 100. Platform-appropriate storage path via `platformdirs`.

### Component 1.5 — Input Manager
- **What was built:** `InputManager` with key-held set tracking, configurable key bindings loaded from persisted settings, and string-to-Arcade-key-constant translation via `KEY_NAME_MAP`.
- **Key files:** `app/src/input/input_manager.py`, `tests/test_input.py`
- **Design decisions:** Used `set.discard()` on key release to avoid `KeyError` on focus loss. Events routed through `InputManager` first (to update `keys_held`), then `StateMachine`. Invalid key names log a warning and fall back to defaults.

### Component 1.6 — Game Config & Data Models
- **What was built:** Frozen `GameConfig` singleton (`GAME_CONFIG`), core enums (`GamePhase`, `AsteroidSize`, `EnemyArchetype`, `UpgradeCategory`, `InsuranceTier`), run-state dataclasses (`GameState`, `ShipState`, `InsuranceState`, `DifficultyParams`, `LevelStats`, `RunStats`), full `UPGRADE_DEFINITIONS` catalog with cost scaling, and procedural difficulty generation via `get_difficulty()`.
- **Key files:** `app/src/config/game_config.py`, `app/src/config/upgrade_definitions.py`, `app/src/config/difficulty_tables.py`, `tests/test_config.py`
- **Design decisions:** Formulaic difficulty scaling (no hardcoded table) for infinite-level support. `ShipState.recalculate_effective_stats()` driven by static upgrade definitions for reuse by later managers.

### Component 1.7 — Audio Manager Skeleton & Rendering Foundation
- **What was built:** `AudioManager` with `.wav` loading from `assets/sounds/`, volume-controlled playback, and exception-safe no-op behaviour for missing assets. `StarfieldRenderer` with deterministic seeded star generation and pre-built `ShapeElementList`. `HUDRenderer` with cached `arcade.Text` value rendering.
- **Key files:** `app/src/audio/audio_manager.py`, `app/src/rendering/starfield.py`, `app/src/rendering/hud.py`, `tests/test_audio_rendering.py`
- **Design decisions:** `play_music()` implemented as a documented no-op API for Phase 5 integration. Starfield uses `random.Random(42)` for deterministic generation. HUD values cached and refreshed only on change.

### Component 1.8 — E2E Testing & Documentation
- **What was built:** Shared pytest fixtures in `tests/conftest.py` for settings, persistence, input, config, game state, and state-machine test setup. Phase documentation finalised.
- **Key files:** `tests/conftest.py`, `docs/components/phase-1-component-1-8-overview.md`
- **Design decisions:** Reused existing focused test modules as the authoritative validation suite rather than introducing redundant integration tests.

## Architecture & Integration

Phase 1 established the layered architecture from the solution design: the application shell (`window.py`) owns the fixed-timestep loop and delegates all behaviour through the state machine. The persistence layer provides the single JSON read/write interface consumed by the input manager (for key bindings) and the window (for settings-driven initialisation). The input manager sits between raw keyboard events and the state machine, ensuring held-key state is current before states process events. The config layer centralises all tuning parameters, upgrade definitions, and difficulty scaling as frozen dataclasses, establishing the contract for gameplay systems in Phase 2+. The rendering pipeline draws starfield background before state visuals each frame.

## Deviations from Spec

- Component 1.6 added `effective_max_shields` and `effective_projectile_count` fields on `ShipState` beyond the original spec to directly model the `defense_shields` and `weapon_spread` upgrade effects. This was an additive change with no impact on other components.
- Component 1.7 implemented `AudioManager.play_music()` as a documented no-op to preserve the Phase 5 integration point without introducing placeholder exceptions. The spec did not explicitly require this method in Phase 1.

## Dependencies & Configuration

- **Runtime dependencies** (`pyproject.toml`): `arcade>=3.3,<4`, `platformdirs>=4.0`, `pyyaml>=6.0`.
- **Dev dependencies** (`pyproject.toml`): `pytest>=8.0`, `pytest-cov>=5.0`, `black>=24.0`, `isort>=5.13`, `mypy>=1.10`.
- **Config files:** `app/config/settings_defaults.yaml` (reference defaults), `.env/.env.example`, `.env/.env.test`.
- **Environment variables:** None required for Phase 1 runtime. `.env` files established for future use.

## Known Limitations

- All nine states are stubs rendering placeholder text — no gameplay logic, UI widgets, or interactive content.
- No actual sound assets exist; `AudioManager` operates in no-op mode on missing files.
- `play_music()` is a no-op; streamed music support deferred to Phase 5.
- Asset directories (`assets/sprites/`, `assets/sounds/`, `assets/fonts/`) contain only `.gitkeep` placeholders.

## Phase Readiness

All eight components passed formatting checks (`black`, `isort`), focused unit tests (`pytest`), and quality evals (`scripts/evals.py`). Phase 1 is complete and provides the architectural foundation for Phase 2 (Core Game Loop).

---

## Phase 2 Overview

Phase 2 delivered the minimum playable game loop: a player ship with inertial physics, three-tier asteroids that spawn/split/wrap, projectiles with cooldown, collision detection (including wrap-around ghost sprites), currency pickups, score accumulation, level progression with difficulty scaling, game-over flow with high-score recording, and a particle-based explosion system. After this phase a player can fly, shoot, clear levels of increasing difficulty, die, and land on the high-score table.

## Components Delivered

### Component 2.1 — Human Setup & Asset Preparation
- **What was built:** Placeholder geometric sprite assets (ship, three asteroid sizes, projectile, currency pickup, explosion particle) generated via a Pillow script, plus real `.wav` sound stubs provided by the developer.
- **Key files:** `assets/sprites/ship.png`, `assets/sprites/asteroid_large.png`, `assets/sprites/asteroid_medium.png`, `assets/sprites/asteroid_small.png`, `assets/sprites/projectile_player.png`, `assets/sprites/currency_pickup.png`, `assets/sprites/explosion_particle.png`, `scripts/generate_placeholder_sprites.py`, `scripts/verify_assets.py`
- **Design decisions:** Used a Pillow generation script for reproducibility. Asteroid sprites include 4px padding for visual margin.

### Component 2.2 — Player Ship Entity & Physics
- **What was built:** `PlayerShip` entity with inertial movement (thrust, rotation, drag, brake, speed cap), shield tracking, cooldown ticking, and a `PhysicsEngine` orchestrating per-tick simulation updates. Shared `wrap_entity()` utility for screen-edge wrapping.
- **Key files:** `app/src/entities/player_ship.py`, `app/src/physics/wrap.py`, `app/src/physics/engine.py`, `app/src/config/game_config.py` (added `PhysicsConfig`)
- **Design decisions:** Explicit `velocity_x`/`velocity_y` on the entity to avoid conflicts with Arcade physics helpers. Dedicated `PhysicsConfig` dataclass for gameplay constants.

### Component 2.3 — Asteroid System
- **What was built:** `Asteroid` entity with three size tiers, per-size score/drop metadata, movement/rotation updates, split behaviour, and level-start spawning away from the player. `SpawnManager` for level and child asteroid spawning. Difficulty tables extended with `get_difficulty_params()`.
- **Key files:** `app/src/entities/asteroid.py`, `app/src/managers/spawn_manager.py`, `app/src/config/difficulty_tables.py`, `app/src/config/game_config.py` (added `AsteroidConfig`)
- **Design decisions:** Reused existing `AsteroidSize` enum. Optional RNG injection for deterministic tests. `asteroid_size` field avoids collision with `arcade.Sprite.size`.

### Component 2.4 — Projectile System & Collision Detection
- **What was built:** `Projectile` entity with velocity and range-based expiry, ship firing with cooldown, invulnerability-aware damage handling, `CollisionSystem` with temporary ghost sprites for seam collisions, and `ScoreManager` for point accumulation.
- **Key files:** `app/src/entities/projectile.py`, `app/src/physics/collisions.py`, `app/src/managers/score_manager.py`, `app/src/entities/player_ship.py` (added `fire()`, `take_damage()`)
- **Design decisions:** Ghost sprites created/cleaned per collision check to prevent leaks. Collision handling split into pair-specific private methods for Phase 3 extensibility.

### Component 2.5 — Currency Pickups & Collection
- **What was built:** `CurrencyPickup` entity with slow random drift and timeout expiry, run-scoped `CurrencyManager` ledger, and collision/physics integration so destroyed asteroids spawn pickups and the ship collects them.
- **Key files:** `app/src/entities/pickups.py`, `app/src/managers/currency_manager.py`, `app/src/config/game_config.py` (added `CurrencyConfig`)
- **Design decisions:** Pickup spawning localized inside collision resolution. `CurrencyManager.earn()`/`spend()` reject negative values as a safety guard.

### Component 2.6 — Entity Manager & Rendering Pipeline
- **What was built:** `EntityManager` with typed `SpriteList` collections (asteroids, projectiles, pickups, particles) and stable draw-order pipeline. Sprite-based `ParticleSystem` for explosion bursts with fade-out.
- **Key files:** `app/src/managers/entity_manager.py`, `app/src/rendering/particle_system.py`
- **Design decisions:** `player` as canonical field with `player_ship` property alias for backward compatibility. Optional `background_renderer` on `EntityManager` for draw-order control.

### Component 2.7 — Combat Phase State & Level Progression
- **What was built:** Functional `CombatPhaseState` with fixed-timestep accumulation, full manager wiring, asteroid level progression, and game-over transition with run stats. `GameOverState` renders run summary and persists qualifying high scores. HUD overlay with cached `arcade.Text` for Score, Level, Shields, and Credits.
- **Key files:** `app/src/states/combat.py`, `app/src/states/game_over.py`, `app/src/rendering/hud.py`
- **Design decisions:** Physics/collision orchestrated in `CombatPhaseState._physics_step()` to avoid restructuring lower-level systems. Lightweight `RunSummary` dataclass for explicit render/persistence fields.

### Component 2.8 — E2E Testing & Documentation
- **What was built:** Six focused test modules (physics, collisions, entities, scoring, currency, difficulty) and extended shared pytest fixtures for Phase 2 gameplay systems.
- **Key files:** `tests/test_physics.py`, `tests/test_collisions.py`, `tests/test_entities.py`, `tests/test_scoring.py`, `tests/test_currency.py`, `tests/test_difficulty.py`, `tests/conftest.py`
- **Design decisions:** Kept tests additive and reused existing component behaviours. Fixtures added to `conftest.py` for Phase 3+ reuse.

## Architecture & Integration

Phase 2 layered gameplay systems on top of the Phase 1 scaffold. `CombatPhaseState` owns the per-frame loop and delegates to `PhysicsEngine` (ship, asteroids, projectiles, pickups), `CollisionSystem` (projectile-vs-asteroid, ship-vs-asteroid, ship-vs-pickup with ghost-sprite seam handling), `SpawnManager` (level-start and split-child asteroid placement), `ScoreManager`, `CurrencyManager`, and `ParticleSystem`. `EntityManager` centralises typed `SpriteList` ownership and enforces a stable draw order: starfield → asteroids → pickups → projectiles → particles → ship → HUD. On game over, `CombatPhaseState` packages a `RunSummary` and transitions to `GameOverState`, which checks high-score qualification and persists via the Phase 1 `PersistenceManager`.

## Deviations from Spec

- Asteroid sprites include 4px padding (68/44/24 instead of 64/40/20) for drawing margin — functionally equivalent.
- Developer-provided `.wav` files are stereo/varying formats rather than strictly mono 16-bit PCM; Arcade handles all standard WAV formats.
- `PhysicsConfig` carries physics defaults separately from the existing `GameConfig` ship defaults for backward compatibility; future phases can consolidate.
- `Asteroid` stores size as `asteroid_size` (not `size`) to avoid collision with `arcade.Sprite.size` property semantics.
- High-score initials entry auto-saves as "AAA" — interactive 3-character input deferred to a later phase.
- Developer provided additional sound files (`player_hit.wav`, `enemy_explode.wav`, `enemy_fire.wav`, `shop_purchase.wav`, `shop_denied.wav`) beyond the Phase 2 spec for future phase use.

## Dependencies & Configuration

- **No new runtime dependencies** added beyond Phase 1 (`arcade`, `platformdirs`, `pyyaml`).
- **Dev dependency** (`pyproject.toml`): `Pillow` used by `scripts/generate_placeholder_sprites.py` for asset generation (not a runtime dependency).
- **New config singletons** (`app/src/config/game_config.py`): `PhysicsConfig`/`PHYSICS_CONFIG`, `AsteroidConfig`/`ASTEROID_CONFIG`, `CollisionConfig`/`COLLISION_CONFIG`, `CurrencyConfig`/`CURRENCY_CONFIG`.
- **Asset directories populated:** `assets/sprites/` (7 PNG files), `assets/sounds/` (14 WAV files).

## Known Limitations

- High-score initials default to "AAA" — no interactive character-by-character entry yet.
- No shop phase between levels — combat advances directly to the next level.
- Runtime UI screenshots could not be captured in the headless sandbox; all validation was programmatic.
- Enemy collision pairs not yet present — `CollisionSystem` handles only asteroid and pickup pairs.

## Phase Readiness

All eight components passed formatting checks (`black`, `isort`), focused unit tests (`pytest`), quality evals (`scripts/evals.py`), and coverage validation. Phase 2 is complete and provides the playable core game loop for Phase 3 (Combat Depth & Enemies).
