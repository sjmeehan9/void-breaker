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

---

## Phase 3 Overview

Phase 3 delivered the full enemy combat expansion: two enemy ship archetypes (Basic Shooter, Aggressive) with steering AI and telegraphed attacks, enemy projectile management, three new collision pairs with seam-aware ghost sprites, timed enemy spawning at screen edges, damage feedback effects (flash, invulnerability flicker, explosion particles, destruction sequence), tiered difficulty scaling across 30 levels with interpolation, and optional buff pickups (HEAL, DAMAGE_BOOST, SPEED_BOOST) dropped by destroyed enemies. After this phase the combat experience is feature-complete — players face both asteroids and enemies with smoothly escalating challenge.

## Components Delivered

### Component 3.1 — Human Setup & Enemy Assets
- **What was built:** Placeholder enemy sprites (Basic Shooter diamond, Aggressive chevron, enemy projectile dot) generated via Pillow, plus developer-provided `.wav` sound effects for enemy fire, enemy explosion, and player hit.
- **Key files:** `assets/sprites/enemy_basic.png`, `assets/sprites/enemy_aggressive.png`, `assets/sprites/projectile_enemy.png`, `assets/sounds/enemy_fire.wav`, `assets/sounds/enemy_explode.wav`, `assets/sounds/player_hit.wav`
- **Design decisions:** Extended existing Pillow sprite generation script. Red/orange palette for enemies distinguishes from player (white) and asteroids (grey).

### Component 3.2 — Enemy Ship Entities & AI
- **What was built:** `EnemyShip` entity with BASIC and AGGRESSIVE archetypes, steering AI with jittered pursuit, telegraphed firing (alpha flash), spawn grace period, lead-prediction aiming for aggressive enemies, and `EnemyConfig` dataclass with factory functions.
- **Key files:** `app/src/entities/enemy_ship.py`, `app/src/config/enemy_config.py`, `tests/test_enemy_ship.py`
- **Design decisions:** Enemy config isolated in its own module to keep Phase 2 `game_config.py` contract stable. Telegraph uses alpha flash rather than scale pulse.

### Component 3.3 — Enemy Projectile System & Expanded Collisions
- **What was built:** Enemy/enemy-projectile SpriteLists in EntityManager, `ProjectileOwner` enum on Projectile, three new collision pairs (player vs enemy projectiles, player projectiles vs enemies, player vs enemies), seam-aware ghost collision support, and combat state integration.
- **Key files:** `app/src/managers/entity_manager.py`, `app/src/physics/collisions.py`, `app/src/states/combat.py`, `app/src/entities/projectile.py`, `tests/test_enemy_projectile_collisions.py`
- **Design decisions:** Kept existing Phase 2 `check_all()` unchanged, layered enemy collision processing through dedicated methods.

### Component 3.4 — Spawn Manager & Enemy Waves
- **What was built:** Extended SpawnManager with timed enemy spawning, screen-edge positioning with inward velocity, archetype selection via `aggressive_ratio`, count cap enforcement. DifficultyParams extended with enemy fields.
- **Key files:** `app/src/managers/spawn_manager.py`, `app/src/config/difficulty_tables.py`, `app/src/config/game_config.py`, `tests/test_spawn_manager_enemies.py`
- **Design decisions:** Interval-based spawning (not wave-based) for simplicity. Enemy spawning independent of asteroid spawning.

### Component 3.5 — Damage Feedback & Visual Effects
- **What was built:** `DamageEffects` class for player hit flash/flicker, enemy explosion particles, and player destruction burst. PlayerShip extended with config-driven invulnerability (0.75s). Combat state wired with audio feedback and 0.8s game-over delay.
- **Key files:** `app/src/rendering/damage_effects.py`, `app/src/entities/player_ship.py`, `app/src/states/combat.py`, `tests/test_damage_effects.py`
- **Design decisions:** Damage flash applied to sprite tint rather than full-screen tint. Invulnerability prevents all damage sources.

### Component 3.6 — Difficulty Scaling & Balance
- **What was built:** Tier-based interpolation system with breakpoints at levels 1, 5, 10, 15, 20, 25, 30. Level-30 cap prevents infinite scaling. Level-6 bridge for enemy activation. All tier values match spec.
- **Key files:** `app/src/config/difficulty_tables.py`, `tests/test_difficulty.py`
- **Design decisions:** Interpolation between tiers rather than 30 hardcoded rows. Cloned DifficultyParams for exact tier hits to avoid shared-instance mutation.

### Component 3.7 — Buff Pickups (Optional)
- **What was built:** `BuffPickup` entity (HEAL, DAMAGE_BOOST, SPEED_BOOST) with procedural textures, bobbing animation, and lifetime expiry. `BuffManager` for apply/update/expiry/clear with non-stacking refresh semantics. PlayerShip extended with effective damage/thrust properties.
- **Key files:** `app/src/entities/buff_pickup.py`, `app/src/managers/buff_manager.py`, `app/src/entities/player_ship.py`, `tests/test_buff_pickups.py`
- **Design decisions:** Buffs isolated to BuffManager. Same-type refresh replaces timer. Runtime sound fallback for collection cue.

### Component 3.8 — E2E Testing & Documentation
- **What was built:** Multi-level combat integration test, implementation context documentation, and component overview. Existing Phase 3 test modules validated all required unit scopes.
- **Key files:** `tests/test_combat_phase_state.py`, `docs/implementation-context-phase-3.md`, `docs/components/phase-3-component-3-8-overview.md`
- **Design decisions:** Focused integration test on stability and enemy-system activity rather than visual rendering.

## Architecture & Integration

Phase 3 layered the enemy combat system on top of the Phase 2 core loop. `CombatPhaseState._physics_step()` now orchestrates asteroid collisions, enemy spawning, enemy AI updates, enemy collision processing, buff pickup management, invulnerability tracking, damage effects, and particle updates in a deterministic sequence. `CollisionSystem` gained four new collision pair methods (including buff pickups) using the same seam-aware ghost sprite pattern from Phase 2. `EntityManager` manages five additional SpriteLists (enemies, enemy_projectiles, buff_pickups) with stable z-order rendering. The tier-based difficulty system in `difficulty_tables.py` provides smooth interpolation across 30 levels with a hard cap, replacing the procedural formula from Phase 2.

## Deviations from Spec

- Enemy projectile texture is overridden at fire time rather than using a separate `EnemyProjectile` subclass, keeping the single `Projectile` class approach.
- Developer-provided `.wav` files are stereo rather than strictly mono 16-bit PCM; Arcade handles all standard WAV formats.
- Damage flash applied to sprite tint (red/white alternation) rather than full-screen tint, matching existing sprite-centric rendering.
- Buff pickup visuals use procedurally generated coloured circles instead of authored sprite files.
- Level-5 tier keeps `enemy_spawn_interval=99` as sentinel; a level-6 bridge ensures smooth enemy activation.

## Dependencies & Configuration

- **No new runtime dependencies** added beyond Phase 2 (`arcade`, `platformdirs`, `pyyaml`).
- **New config module:** `app/src/config/enemy_config.py` with `EnemyArchetype`, `EnemyConfig`, factory functions.
- **Extended configs:** `DifficultyParams` gained enemy fields; `GameConfig` gained `invulnerability_duration`.
- **New asset files:** 3 enemy sprites, 3 sound effects (provided in Phase 3.1).

## Known Limitations

- Enemy-vs-asteroid collisions intentionally disabled (enemies fly through asteroids).
- Enemy projectile-vs-asteroid collisions disabled for performance.
- Buff indicators not yet rendered on HUD (deferred to Phase 5).
- High-score initials still default to "AAA" (Phase 5).

## Phase Readiness

All eight components passed formatting checks (`black`, `isort`), 141 focused unit tests (`pytest`), quality evals (`scripts/evals.py`), and 89% overall code coverage. Phase 3 is complete and provides the full combat experience for Phase 4 (Economy & Progression).

---

## Phase 4 Overview

Phase 4 delivered VoidBreaker's signature feature set: the fly-through shop phase, upgrade manager, insurance mechanic, and currency economy. After this phase, the complete core game loop is functional — fight, collect currency, shop for upgrades via ship-to-node collision, fight harder, repeat. The shop introduces meaningful strategic decisions each level through upgrade investment, insurance risk/reward, and currency management.

## Components Delivered

### Component 4.1 — Human Setup & Shop Assets
- **What was built:** Seven placeholder shop sprites (six category orbs + continue arrow) generated via Pillow, plus two developer-provided `.wav` sound effects.
- **Key files:** `assets/sprites/shop/orb_weapon.png`, `orb_defense.png`, `orb_mobility.png`, `orb_economy.png`, `orb_repair.png`, `orb_insurance.png`, `assets/sprites/shop/node_continue.png`, `scripts/generate_placeholder_sprites.py`
- **Design decisions:** Extended the existing Pillow generation script. Orbs use a three-layer glow design for visual depth.

### Component 4.2 — Shop Phase State & Layout
- **What was built:** Replaced the Phase 1 shop stub with `ShopPhaseState` — circular node layout, ship centring on entry, thrust/rotation movement with screen-edge clamping (no wrap), and bidirectional combat↔shop transitions.
- **Key files:** `app/src/states/shop.py`, `app/src/states/combat.py`, `app/src/config/game_config.py` (`ShopLayoutConfig`)
- **Design decisions:** Layout radius and continue-node offset centralised in `ShopLayoutConfig`. Used lightweight view models in 4.2 to avoid blocking on the 4.3 entity implementation.

### Component 4.3 — Shop Node Entities & Interaction
- **What was built:** `ShopNode` and `ContinueNode` entity classes with geometric cost scaling, purchasability checks, per-frame affordability/max-state alpha rendering, text labels (name, level, cost), and collision-based purchase/denied flow.
- **Key files:** `app/src/entities/shop_node.py`, `app/src/entities/__init__.py`
- **Design decisions:** Insurance kept as a non-purchasable placeholder in 4.3 to defer tier-cycling logic to 4.5/4.7. Denied feedback uses dimming + bounce; crossed-out icon deferred to polish pass.

### Component 4.4 — Upgrade Manager & Stat Application
- **What was built:** `UpgradeManager` tracking all 11 upgrade levels, cost scaling, one-shot repairs, score multiplier, and effective stat recalculation on `ShipState`/`GameState`. Full upgrade catalog populated in `upgrade_definitions.py`.
- **Key files:** `app/src/managers/upgrade_manager.py`, `app/src/config/upgrade_definitions.py`
- **Design decisions:** `UPGRADE_DEFINITIONS` kept as compatibility alias to `ALL_UPGRADES`. Repairs excluded from level retention by manager behaviour.

### Component 4.5 — Insurance Manager & Death Retention
- **What was built:** `InsuranceManager` with tier configs (OFF/BASIC/PREMIUM), per-level cost scaling (10% increase per level), automatic lapse-to-OFF on unaffordable deductions, and upgrade retention calculation/application.
- **Key files:** `app/src/managers/insurance_manager.py`
- **Design decisions:** Compatibility helpers bridge both current `CurrencyManager` API (`spend`/`get_balance`) and planned Phase 4.6 API (`can_spend`/`deduct`).

### Component 4.6 — Currency Manager & Economy Flow
- **What was built:** Rewrote `CurrencyManager` as single authority for currency: `earn()`, `spend()`, `deduct()`, `can_spend()`, `CurrencyRunStats`, optional `GameState` backing store, and strict positive-integer validation.
- **Key files:** `app/src/managers/currency_manager.py`, `app/src/physics/collisions.py`, `app/src/states/combat.py`
- **Design decisions:** `game_state` parameter optional for backward compatibility. `deduct()` delegates to `spend()` for a single deduction path.

### Component 4.7 — Ship Re-Centring & Purchase Flow Polish
- **What was built:** Smooth quadratic ease-out ship re-centring (0.3s), collision lockout during interpolation, manager-driven purchase orchestration (currency → upgrade → audio → re-centre), insurance-tier cycling, and unified Continue flow (node collision or Enter key).
- **Key files:** `app/src/states/shop.py`, `app/src/entities/shop_node.py`
- **Design decisions:** Single insurance node cycling tiers (OFF → BASIC → PREMIUM → OFF) per v1.0 recommendation. Insurance cost charged on tier changes and recurring deductions on Continue transition.

### Component 4.8 — E2E Testing & Documentation
- **What was built:** 105 new tests across `test_upgrades.py` (30), `test_insurance.py` (28), and `test_shop.py` (47), plus conftest fixtures and component overview docs.
- **Key files:** `tests/test_upgrades.py`, `tests/test_insurance.py`, `tests/test_shop.py`, `tests/conftest.py`
- **Design decisions:** `test_currency.py` coverage from 4.6 reused rather than duplicated.

## Architecture & Integration

Phase 4 layered the economy system on top of the Phase 3 combat loop. `CombatPhaseState` now transitions to `ShopPhaseState` on level clear instead of advancing directly. `ShopPhaseState` owns a circular `ShopNode` layout and delegates purchases through `CurrencyManager.spend()` → `UpgradeManager.apply_upgrade()` → `ShipState.recalculate_effective_stats()`, with `InsuranceManager.deduct_level_cost()` called on Continue transition. The re-centring state machine inside `ShopPhaseState` prevents double-purchases via collision lockout. `GameOver` receives run summary data including `CurrencyRunStats` for post-run display.

## Deviations from Spec

- Denied node feedback uses dimming + bounce + sound without an explicit crossed-out icon overlay — deferred to visual polish.
- Insurance interaction uses single-node tier cycling rather than three separate nodes, following the spec's recommended v1.0 approach.
- `test_currency.py` was delivered by component 4.6 and reused for 4.8 rather than being created separately.

## Dependencies & Configuration

- **No new runtime dependencies** beyond Phases 1–3.
- **New config entries:** `ShopLayoutConfig`/`SHOP_LAYOUT_CONFIG` in `game_config.py`; `score_bonus_level` on `GameConfig`.
- **New modules:** `managers/upgrade_manager.py`, `managers/insurance_manager.py`, `entities/shop_node.py`.
- **Asset files added:** 7 shop sprites in `assets/sprites/shop/`, 2 sound effects pre-existing from developer.

## Known Limitations

- Shop node denied feedback lacks a crossed-out icon (visual polish only).
- No animated shop node entrance/exit — nodes appear instantly.
- Insurance tier cycling is unidirectional (OFF → BASIC → PREMIUM → OFF); no direct downgrade path.
- High-score initials still default to "AAA" (deferred to Phase 5).

## Phase Readiness

All eight components passed formatting checks, 177+ focused unit tests, quality evals (`scripts/evals.py`), and module coverage of 82–100% on Phase 4 code. Phase 4 is complete and provides the full economy loop for Phase 5 (Polish & UX).

---

## Phase 5 Overview

Phase 5 transformed VoidBreaker from a functional game into a polished, release-quality experience. It delivered all remaining UI screens (main menu, how-to-play, settings, high scores, game over with name entry), the pause system, practice/training mode, complete audio integration (17 sound effects with wrapper methods), a pooled particle system (300 hard cap), visual polish (level transitions, screen shake, colorblind palette, HUD improvements), three difficulty presets (Casual/Classic/Hard), and comprehensive E2E testing. After this phase, a new player can navigate the entire game without external documentation.

## Components Delivered

### Component 5.1 — Human Setup & Final Assets
- **What was built:** 25 final sprite assets via Pillow script, 17 developer-provided `.wav` sound effects, one font file (`game_font.ttf`), backward-compatibility alias sprites, and updated verification script.
- **Key files:** `scripts/generate_final_sprites.py`, `scripts/verify_assets.py`, `assets/sprites/` (25 PNGs), `assets/sounds/` (17 WAVs), `assets/fonts/game_font.ttf`
- **Design decisions:** New generation script preserves the original placeholder generator for reference. Backward-compat copies (`currency_pickup.png`, `explosion_particle.png`) avoid breaking Phase 1–4 code.

### Component 5.2 — Main Menu & Navigation System
- **What was built:** Full `MainMenuState` with five-option keyboard navigation, wrap logic, fade transitions, audio cues, selection persistence across state returns, and reusable `MenuRenderer` module.
- **Key files:** `app/src/states/main_menu.py`, `app/src/rendering/menu_renderer.py`
- **Design decisions:** List-driven options model for easy extension by 5.10. Class-level index persistence for sub-screen return behaviour.

### Component 5.3 — How-to-Play & High Scores Screens
- **What was built:** `HowToPlayState` with dynamic controls table from active key bindings, gameplay/insurance guidance, scrolling. `HighScoresState` with top-10 leaderboard, descending score sort, difficulty filter cycling, and empty-state messaging.
- **Key files:** `app/src/states/how_to_play.py`, `app/src/states/high_scores.py`
- **Design decisions:** Key-label display via `InputManager` key map reversal keeps controls synchronized with remapped settings.

### Component 5.4 — Settings Screen & Accessibility
- **What was built:** Full settings interface with key remapping (capture mode + duplicate resolution), volume sliders (0.1 step), toggles (fire mode, autofire, colorblind), multi-option cycling (screen shake, difficulty), immediate persistence, hot-application, and reset-to-defaults.
- **Key files:** `app/src/states/settings_screen.py`, `app/src/input/input_manager.py` (added `UNBOUND` support)
- **Design decisions:** Duplicate-key handling clears previous action to `UNBOUND` rather than swapping.

### Component 5.5 — Game Over Screen & High Score Entry
- **What was built:** Three-phase game-over flow: run summary (score, level, enemies/asteroids destroyed, currency earned/spent, insurance tier), conditional top-10 name entry (3–10 alphanumeric characters), and post-run options (Play Again / Return to Menu).
- **Key files:** `app/src/states/game_over.py`
- **Design decisions:** Strict top-10 qualification (score > 10th place). Replay routes through `GameInitState` for clean run reset.

### Component 5.6 — Pause System
- **What was built:** Full overlay pause menu (Resume, Restart Run, Settings, Exit to Menu) that freezes combat/shop updates. Settings opened from pause returns to pause via `pop_state()`. Overlay semantics corrected in state machine.
- **Key files:** `app/src/states/pause.py`, `app/src/states/state_machine.py`, `app/src/states/combat.py`, `app/src/states/shop.py`
- **Design decisions:** `push_state()`/`pop_state()` no longer call `on_exit()`/`on_enter()` on underlying states, preserving exact run state.

### Component 5.7 — Audio Integration & Particle Effects
- **What was built:** 15+ wrapper methods on `AudioManager` (e.g., `play_fire`, `play_explosion(size)`, `play_shop_purchase`), and a pooled particle system with 300 hard cap, pre-allocated sprites, oldest-particle recycling, and five effect types (explosion, thrust, sparkle, damage flash, purchase burst).
- **Key files:** `app/src/audio/audio_manager.py`, `app/src/rendering/particle_system.py`, `app/src/states/combat.py`, `app/src/physics/collisions.py`
- **Design decisions:** Pooled sprites permanently resident in `SpriteList` to prevent per-frame allocation churn. Backward-compatible fallback to `audio_manager.play(name)` for test stubs.

### Component 5.8 — Visual Polish & Transitions
- **What was built:** `TransitionEffect` (fade/hold/fade level overlays), `ScreenShake` (off/low/medium with decay), colorblind palette tinting, HUD shield bar with threshold colouring, centred score with shadow, credits-change flash, and shop node scale pulse (1.0–1.15).
- **Key files:** `app/src/rendering/transitions.py`, `app/src/rendering/hud.py`, `app/src/window.py`, `app/src/entities/shop_node.py`, `app/src/entities/player_ship.py`
- **Design decisions:** Colorblind mode via runtime sprite tinting avoids asset duplication. Shake reset-on-trigger (no accumulation).

### Component 5.9 — Difficulty Presets Integration
- **What was built:** `DifficultyPreset` enum (Casual/Classic/Hard), `DifficultyMultipliers` dataclass, `DifficultyScaler.apply_preset()`, New Game difficulty sub-prompt with persisted selection, and preset-aware combat spawning/damage/currency.
- **Key files:** `app/src/config/difficulty_tables.py`, `app/src/managers/difficulty_scaler.py`, `app/src/states/main_menu.py`, `app/src/states/combat.py`
- **Design decisions:** Presets are multiplicative over Phase 3 tier interpolation, preserving existing tuning while shifting baseline.

### Component 5.10 — Practice/Training Mode
- **What was built:** Practice menu option, `PracticeConfigState` with toggles (asteroids only, infinite shields, reduced count), practice-aware combat (shop bypass, non-lethal respawn, enemy suppression), leaderboard skip, and HUD `PRACTICE` indicator.
- **Key files:** `app/src/states/practice_config.py`, `app/src/states/main_menu.py`, `app/src/states/combat.py`, `app/src/states/game_over.py`, `app/src/rendering/hud.py`
- **Design decisions:** Reuses `CombatPhaseState` with explicit flags to avoid duplicating combat systems.

### Component 5.11 — E2E Testing & Documentation
- **What was built:** Nine dedicated test files (`test_phase5_*.py`) covering menus, settings, pause, game over, audio wiring, particle pooling, difficulty presets, practice mode, and a logic-level E2E session path. Final component documentation.
- **Key files:** `tests/test_phase5_menus.py`, `test_phase5_settings.py`, `test_phase5_pause.py`, `test_phase5_game_over.py`, `test_phase5_audio.py`, `test_phase5_particles.py`, `test_phase5_difficulty.py`, `test_phase5_practice.py`, `test_phase5_e2e.py`
- **Design decisions:** All tests headless and state/manager-focused. Audio coverage at wrapper-method mapping level.

## Architecture & Integration

Phase 5 completed the UI and polish layer atop the Phase 4 economy loop. `MainMenuState` now drives the full navigation tree (New Game with difficulty selection, Practice, How to Play, Settings, High Scores, Quit). `PauseState` operates as a true overlay via `push_state()`/`pop_state()`, freezing underlying combat/shop updates without `on_exit()`/`on_enter()` side effects. `AudioManager` wrapper methods are wired into combat, collision, shop, and menu flows. The pooled `ParticleSystem` integrates into both `CombatPhaseState` and `ShopPhaseState` draw pipelines. `TransitionEffect` and `ScreenShake` are managed by `CombatPhaseState` and `VoidBreakerWindow` respectively. Difficulty presets apply multiplicatively at combat init via `DifficultyScaler`, and practice mode reuses `CombatPhaseState` with flag-driven behaviour overrides.

## Deviations from Spec

- `shield_low.wav` deferred per spec notes (17 sounds present instead of the optional 18th).
- Sound assets are stereo/varying formats rather than strictly mono 16-bit PCM; Arcade handles all standard WAV formats.
- State machine overlay semantics updated so `push_state()`/`pop_state()` no longer invoke `on_exit()`/`on_enter()` on underlying states — a refinement of the Phase 1 overlay design.

## Dependencies & Configuration

- **No new runtime dependencies** beyond Phases 1–4.
- **New modules:** `rendering/menu_renderer.py`, `rendering/transitions.py`, `managers/difficulty_scaler.py`, `states/practice_config.py`.
- **New config entries:** `DifficultyPreset`, `DifficultyMultipliers`, `DIFFICULTY_PRESET_MULTIPLIERS` in `difficulty_tables.py`; `GameState.is_practice` flag.
- **Asset files:** 25 final sprites, 17 sound effects, 1 font file.

## Known Limitations

- `shield_low.wav` sound effect deferred (optional per spec).
- No background music support (deferred to post-v1.0 per phase plan).
- Colorblind mode uses sprite tinting which may produce imperfect results on non-greyscale base textures.
- Practice mode skips shop phase entirely — no shop practice available.

## Phase Readiness

All eleven components passed formatting checks (`black`, `isort`), 343 focused unit tests (`pytest`), quality evals (`scripts/evals.py`), and 79% overall code coverage. Phase 5 is complete and provides the polished, release-quality game for Phase 6 (Packaging & Release).
