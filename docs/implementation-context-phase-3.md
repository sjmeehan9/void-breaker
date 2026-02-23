# Phase 3 Implementation Context

## Component 3.1 — Human Setup & Enemy Assets
- **Status**: Completed
- **What was built**: All placeholder visual and audio assets required for Phase 3 enemy combat. Three new sprite files were generated via Pillow (extending the existing `scripts/generate_placeholder_sprites.py` script). Three sound effect `.wav` files were provided by the developer prior to this component.
- **Key files created**:
  - `assets/sprites/enemy_basic.png` — 64×64 red diamond shape (RGBA), visually distinct from player ship
  - `assets/sprites/enemy_aggressive.png` — 64×64 orange chevron/arrow shape (RGBA), distinct from Basic Shooter
  - `assets/sprites/projectile_enemy.png` — 8×8 red-orange dot (RGBA), distinct from cyan player projectile
- **Key files modified**:
  - `scripts/generate_placeholder_sprites.py` — added `generate_enemy_basic()`, `generate_enemy_aggressive()`, `generate_enemy_projectile()` functions and updated `main()` to invoke them
  - `scripts/verify_assets.py` — added Phase 3 sprites and sounds to verification checks
- **Sound files present** (provided by developer):
  - `assets/sounds/enemy_fire.wav`, `assets/sounds/enemy_explode.wav`, `assets/sounds/player_hit.wav`
- **Design decisions**: Extended existing Pillow sprite generation script rather than creating a separate Phase 3 script, maintaining a single source of truth for all placeholder assets. Enemy sprites use red/orange colour palette to visually distinguish from player (white) and asteroids (grey). Basic Shooter uses a diamond shape while Aggressive uses a chevron/arrow to differentiate the two archetypes. Enemy projectile is red-orange vs player's cyan for clear friend/foe distinction.
- **Deviations**: Developer-provided `.wav` files are stereo rather than strictly mono 16-bit PCM as specified, but Arcade handles all standard WAV formats without issue (consistent with Phase 2 sound handling).

## Component 3.2 — Enemy Ship Entities & AI
- **Status**: Completed
- **What was built**: Added a new enemy-configuration module and a new `EnemyShip` entity implementing archetype-specific movement, aiming, telegraphed firing, spawn grace handling, damage/death behaviour, and destruction reward metadata.
- **Key files created**:
  - `app/src/config/enemy_config.py` — `EnemyArchetype` (BASIC/AGGRESSIVE), `EnemyConfig` dataclass, and `get_basic_config()` / `get_aggressive_config()` factories with spec-aligned defaults.
  - `app/src/entities/enemy_ship.py` — `EnemyShip` Arcade sprite subclass with steering AI, jittered pursuit, telegraph windup, cooldown logic, aiming (basic direct aim and aggressive lead prediction), and projectile spawn.
  - `tests/test_enemy_ship.py` — focused unit tests for configs, instantiation, movement, spawn grace, cooldown/telegraph transitions, damage handling, and archetype aim behaviour.
- **Design decisions**: Kept enemy tuning isolated in `config/enemy_config.py` to avoid expanding the existing Phase 2 `game_config.py` contract before wave spawning/collision integration (3.3/3.4). Implemented telegraphing as alpha flashing (allowed by spec) rather than scale pulsing to avoid runtime variability in `arcade.Sprite.scale` representation. Enemy projectile texture is overridden to `assets/sprites/projectile_enemy.png` when a shot is created.
- **Deviations**: `Projectile` in Phase 2 does not yet expose a typed owner enum field despite Phase 3 notes; `EnemyShip` currently annotates ownership as `projectile.owner = \"enemy\"` for immediate compatibility until Component 3.3 formalises enemy projectile ownership in the shared projectile/collision pipeline.

## Component 3.3 — Enemy Projectile System & Expanded Collisions
- **Status**: Completed
- **What was built**: Integrated enemy entities into the combat loop with dedicated enemy projectile management, three new collision pair checks (including seam ghost-wrap support), and combat resolution for player damage, enemy damage/destruction, score updates, and projectile cleanup.
- **Key files modified**:
  - `app/src/managers/entity_manager.py` — added `enemies` and `enemy_projectiles` SpriteLists, updated draw order, added `clear_enemies()`, and ensured `clear_all()` clears enemy collections
  - `app/src/entities/projectile.py` — added typed `ProjectileOwner` enum and `owner` field to projectile constructor
  - `app/src/entities/enemy_ship.py` — switched enemy-fired projectiles to `ProjectileOwner.ENEMY`
  - `app/src/physics/collisions.py` — added:
    - `check_player_vs_enemy_projectiles()`
    - `check_player_projectiles_vs_enemies()`
    - `check_player_vs_enemies()`
    - `check_all_combat()`
    - shared seam-aware ghost collision helper for new sprite/list pairs
  - `app/src/states/combat.py` — added `_update_enemies()`, `_process_enemy_collisions()`, and `_handle_enemy_destroyed()`, wired both into fixed-step physics loop, and clear enemy lists on enter/level advance
- **Key tests added/updated**:
  - `tests/test_enemy_projectile_collisions.py` — validates ghost-wrap collision for player vs enemy projectile, player projectile vs enemy collision pairs, enemy projectile spawn/expiry in combat update, and enemy collision resolution (damage + cleanup + score)
  - `tests/test_entity_manager_rendering.py` — validates enemy SpriteList initialization, draw z-order, and clear behavior including enemy collections
- **Design decisions**: Kept existing Phase 2 `CollisionSystem.check_all()` behavior unchanged for asteroid/pickup flows, then layered enemy collision processing through new dedicated methods and `CombatPhaseState._process_enemy_collisions()` to minimize regression risk.
- **Deviations**: None from component requirements.

## Component 3.4 — Spawn Manager & Enemy Waves
- **Status**: Completed
- **What was built**: Extended `SpawnManager` with timed enemy spawning logic, per-level enemy configuration via difficulty tables, and screen-edge spawn positioning. Enemies spawn at configurable intervals during combat, respecting count caps and level-specific archetype ratios. Early levels (1-5) have no enemies, mid levels (6-15) introduce Basic Shooters then Aggressive enemies, and late levels (16+) feature frequent aggressive waves.
- **Key files modified**:
  - `app/src/config/game_config.py` — added `aggressive_ratio: float = 0.0` field to `DifficultyParams` dataclass
  - `app/src/config/difficulty_tables.py` — updated `get_difficulty_params()` with enemy spawn parameters: levels 1-5 have `enemy_spawn_enabled=False`, level 6+ enabled with progressive scaling of `enemy_count_max` (1→3→5→8), `enemy_spawn_interval` (8.0s→3.0s), `aggressive_ratio` (0.0→0.3→0.5→0.7), and `enemy_aggression` (0.3→0.9); updated `get_difficulty()` to propagate `aggressive_ratio`
  - `app/src/managers/spawn_manager.py` — added `_enemy_spawn_timer` and `_enemy_spawn_active` attributes; added methods: `update_enemy_spawning()` (interval-based spawn with cap enforcement), `_get_spawn_edge_position()` (off-screen spawn with inward velocity), `_select_archetype()` (weighted archetype selection), `reset_enemy_spawning()` (timer reset for level start)
  - `app/src/states/combat.py` — added `_spawn_enemies()` method called in `_physics_step()`; added `reset_enemy_spawning()` calls in `on_enter()` and `_advance_level()`
- **Key tests added**:
  - `tests/test_spawn_manager_enemies.py` — 8 focused tests covering: no spawn when disabled, no spawn before interval, spawn after interval when under cap, no spawn at cap, edge position validation (off-screen + inward velocity), archetype selection respects `aggressive_ratio` statistically, timer reset, and 30-second integration test
  - Updated `tests/test_asteroid_system.py`, `tests/test_config.py`, `tests/test_difficulty.py`, `tests/test_combat_phase_state.py` to reflect Phase 3 enemy spawning enabled from level 6+
- **Design decisions**: 
  - Enemy spawn positioning uses random edge selection (top/bottom/left/right) with off-screen margin (50px) and velocity vector aimed at screen center with randomness (±200px horizontal, ±100px vertical for top/bottom; ±100px horizontal, ±200px vertical for left/right) to create natural inward movement and variety.
  - Archetype selection uses simple probabilistic selection (`random() < aggressive_ratio`) rather than complex weighted pools for clarity and determinism in tests.
  - Spawn interval timer is unconditional (always advances when enabled) but spawn only occurs when under cap, allowing natural spawn behavior without complex state tracking.
  - Enemy spawning is independent of asteroid spawning (both run in same `_physics_step()`) to maintain Phase 2 asteroid behavior unchanged.
- **Deviations**: None from component requirements. All acceptance criteria met: spawn manager supports enemies alongside asteroids, spawning disabled for levels 1-5, enemies spawn at screen edges moving inward, spawn interval decreases with level, aggressive enemies introduced via `aggressive_ratio`, count cap enforced, `DifficultyParams` includes all enemy fields.

## Component 3.5 — Damage Feedback & Visual Effects
- **Status**: Completed
- **What was built**: Added a dedicated damage-effects subsystem for player hit flash/flicker and burst-style explosion particles, then integrated it into combat damage and enemy death flows. Player damage now triggers `player_hit` sound + visual feedback, enemy destruction triggers particle burst + `enemy_explode`, and player death plays a larger destruction burst with a 0.8s transition delay.
- **Key files created**:
  - `app/src/rendering/damage_effects.py` — `DamageEffects` implementation for damage flash, invulnerability flicker, enemy explosion bursts, and player destruction bursts.
  - `tests/test_damage_effects.py` — focused tests for flash restoration, particle spawn counts, and particle expiry via `ParticleSystem`.
- **Key files modified**:
  - `app/src/entities/player_ship.py` — switched to config-driven invulnerability duration (`GAME_CONFIG.invulnerability_duration`), added `is_invulnerable` property, and added explicit `update_invulnerability(dt)`.
  - `app/src/config/game_config.py` — set `invulnerability_duration` to `0.75` seconds for spec-aligned fairness window.
  - `app/src/states/combat.py` — integrated `DamageEffects` update loop, enemy explosion hooks, player hit feedback hooks, invulnerability update call, and 0.8-second delayed game-over transition with destruction sequence.
  - `app/src/rendering/particle_system.py` — generalized particle update logic to support additional particle types exposing `update_particle(dt)`.
  - `app/src/rendering/__init__.py` — exported `DamageEffects`.
  - `tests/test_player_ship_physics.py` — added invulnerability behavior tests.
  - `tests/test_enemy_projectile_collisions.py` — added combat-level test for hit audio + invulnerability gating.
  - `tests/test_combat_phase_state.py` — added delay test for player-destruction transition.
- **Design decisions**:
  - Kept changes additive and localized: particle ownership/rendering remains with existing `EntityManager` + `ParticleSystem`, while `DamageEffects` only manages effect state and particle emission.
  - Avoided changing existing collision contracts by adding post-collision shield-delta feedback for asteroid hits and explicit `_apply_player_damage()` for enemy-driven hits.
  - Added `_play_sound()` guard in combat to keep tests and headless flows stable when no Arcade window is active.
- **Deviations**:
  - The implementation applies player damage flash directly to ship sprite tint (red/white alternation) rather than full-screen tint, matching existing sprite-centric rendering architecture and avoiding unrelated rendering-pipeline changes.

## Component 3.6 — Difficulty Scaling & Balance
- **Status**: Completed
- **What was built**: Replaced the procedural level-scaling formula with a tiered interpolation model in `difficulty_tables.py`, covering calibrated breakpoints at levels 1, 5, 10, 15, 20, 25, and 30 with a hard cap at level 30. Added focused tests that verify exact tier values, interpolation behaviour, spawn thresholds, cap behaviour, monotonic progression, and numeric bounds.
- **Key files modified**:
  - `app/src/config/difficulty_tables.py` — added `DIFFICULTY_TIERS`, `_interpolate_params()`, and capped `get_difficulty_params()` flow; preserved `get_difficulty()` mode multipliers
  - `tests/test_difficulty.py` — expanded from one broad test to targeted acceptance-style checks for 3.6 requirements
  - `tests/test_asteroid_system.py` — aligned level-1 and level-30 expectations with the new 3.6 difficulty curve
  - `tests/test_config.py` — updated late-game enemy spawn interval floor expectation to match the level-30 cap (`2.5s`)
- **Design decisions**:
  - Implemented tier-based interpolation to keep balancing editable at a few key breakpoints rather than 30 hardcoded rows.
  - Added a level-6 enemy-activation bridge for enemy-specific fields so enemies begin spawning immediately after level 5 without inheriting the level-5 sentinel interval (`99s`).
  - Returned cloned `DifficultyParams` objects for exact tier hits to avoid accidental shared-instance mutation.
- **Deviations**:
  - The level-5 tier keeps `enemy_spawn_interval=99` as specified, but interpolation uses a level-6 bridge (`8.0s`, enemy count starts at 1) so levels 6-9 remain playable and aligned with Phase 3.4 spawn expectations.

## Component 3.7 — Buff Pickups (Optional)
- **Status**: Completed
- **What was built**: Added optional enemy-dropped buff pickups and timed buff effect management. Combat now supports HEAL (instant 25% shield restore), DAMAGE_BOOST (1.5x projectile damage for 8s), and SPEED_BOOST (1.4x thrust for 8s), with non-stacking refresh behavior and automatic expiry.
- **Key files created**:
  - `app/src/entities/buff_pickup.py` — `BuffType` enum and `BuffPickup` sprite with per-type generated textures, bobbing animation, and lifetime expiry
  - `app/src/managers/buff_manager.py` — `BuffManager` handling apply/update/expiry/clear for timed buffs and instant heal
  - `tests/test_buff_pickups.py` — focused tests for pickup lifecycle, buff manager behavior, duration refresh semantics, and combat drop/collection flow
- **Key files modified**:
  - `app/src/entities/player_ship.py` — added effective damage/thrust properties and temporary buff apply/remove methods used by fire/thrust calculations
  - `app/src/managers/entity_manager.py` — added `buff_pickups` SpriteList, draw ordering, and clear handling
  - `app/src/physics/collisions.py` — added player-vs-buff-pickup seam-aware collision pair and exposed it in `check_all_combat()`
  - `app/src/states/combat.py` — added `BuffManager` lifecycle wiring, enemy buff-drop rolls, buff pickup updates, collection handling, and sound fallback (`pickup_buff` if present else `pickup_currency`)
  - `tests/test_entity_manager_rendering.py` — updated clear and draw-order expectations for buff pickup rendering layer
- **Design decisions**:
  - Kept buffs fully isolated to `BuffManager` to avoid mutating `GameState` or adding new run-state fields before Phase 4.
  - Implemented same-type buff refresh by replacing timer/magnitude entry (single active entry per type), matching “no stacking” requirement.
  - Used seam-aware collision reuse in `CollisionSystem` to keep pickup collection reliable near wrap edges.
  - Used runtime sound fallback selection to guarantee a collection cue without requiring a new asset.
- **Deviations**:
  - Buff pickup visuals use procedurally generated coloured circles (Arcade textures) instead of authored sprite files to keep this optional component asset-light while remaining visually distinct.
