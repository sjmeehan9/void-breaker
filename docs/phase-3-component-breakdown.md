# Phase 3: Combat Expansion — Component Breakdown

Version: 1.0
Date: 2026-02-20
Owner: Tech Lead (Phase 3)

---

## Phase Overview

Phase 3 adds the full enemy combat system to VoidBreaker: two enemy ship archetypes (Basic Shooter, Aggressive), enemy projectiles, expanded collision detection, timed enemy spawning with wave management, damage feedback effects, refined difficulty scaling for 30+ levels, and optional buff pickups. After this phase the combat experience is feature-complete — players face both asteroids and enemies with smoothly escalating challenge.

**Dependencies**: Phase 2 complete (PlayerShip, Asteroid, Projectile, CollisionSystem, SpawnManager, EntityManager, CombatPhase state, DifficultyParams, GameState, currency pickups, level progression).

**Cross-Phase Serialisation Constraints**: Phase 3 extends several files originally created in Phase 2. These are explicitly noted per component. Components sharing files with Phase 2 outputs cannot be parallelised with late-running Phase 2 components.

---

## Component Summary

| ID | Name | Effort | Owner | Priority | Serialisation Constraints |
|----|------|--------|-------|----------|---------------------------|
| 3.1 | Human Setup & Enemy Assets | 2-3 hours | Human | Must-have | None |
| 3.2 | Enemy Ship Entities & AI | 6-8 hours | AI Agent | Must-have | None (new files only) |
| 3.3 | Enemy Projectile System & Expanded Collisions | 4-6 hours | AI Agent | Must-have | `managers/entity_manager.py`, `physics/collisions.py`, `states/combat.py` (shared with Phase 2) |
| 3.4 | Spawn Manager & Enemy Waves | 4-6 hours | AI Agent | Must-have | `managers/spawn_manager.py`, `config/difficulty_tables.py`, `config/game_config.py` (shared with Phase 2) |
| 3.5 | Damage Feedback & Visual Effects | 4-6 hours | AI Agent | Must-have | `entities/player_ship.py`, `states/combat.py` (shared with Phase 2) |
| 3.6 | Difficulty Scaling & Balance | 3-4 hours | AI Agent | Must-have | `config/difficulty_tables.py` (shared with 3.4) |
| 3.7 | Buff Pickups (Optional) | 3-4 hours | AI Agent | Nice-to-have | `managers/entity_manager.py`, `physics/collisions.py`, `states/combat.py` (shared with 3.3) |
| 3.8 | E2E Testing & Documentation | 4-6 hours | AI Agent | Must-have | All Phase 3 files (runs after all other components) |

---

## Component Dependency Graph

```
3.1 (Human: assets)
 |
 v
3.2 (EnemyShip entity + AI)
 |
 +---> 3.3 (Enemy projectiles + expanded collisions)
 |      |
 |      +---> 3.5 (Damage feedback & effects)
 |      |
 |      +---> 3.7 (Buff pickups, optional)
 |
 +---> 3.4 (Spawn manager + enemy waves)
        |
        +---> 3.6 (Difficulty scaling & balance)
                |
                +---> 3.8 (E2E testing & documentation)
```

**Parallelisation opportunities**: Components 3.3 and 3.4 can run in parallel after 3.2 completes (they modify different files except that both touch `states/combat.py` — see serialisation notes). Component 3.5 depends on 3.3. Component 3.6 depends on 3.4. Component 3.7 depends on 3.3. Component 3.8 runs last.

**Serialisation warning**: Components 3.3 and 3.4 both modify `states/combat.py` (adding enemy update calls and spawn calls respectively). If parallelised, one agent must merge the other's changes. Recommend running 3.3 first, then 3.4, to avoid merge conflicts.

---

## Components

---

#### Component: 3.1 — Human Setup & Enemy Assets

**Priority**: Must-have

**Estimated Effort**: 2-3 hours

**Owner**: Human

**Dependencies**:
- Phase 2 complete: asset directory structure exists at `void-breaker/assets/sprites/` and `void-breaker/assets/sounds/`

**Features**:
- Create placeholder enemy ship sprites (Basic Shooter, Aggressive) — Human
- Create placeholder enemy projectile sprite — Human
- Create placeholder sound effects (enemy fire, enemy explosion, player hit) — Human
- Verify assets load via Arcade's `arcade.load_texture()` and `arcade.load_sound()` — Human

**Description**:
Creates all visual and audio placeholder assets required for enemy combat. These are intentionally simple geometric shapes and basic waveform sounds — final art is deferred to Phase 5.1. All subsequent Phase 3 components depend on these assets being present in the correct directories.

**Acceptance Criteria**:
- [ ] `void-breaker/assets/sprites/enemy_basic.png` exists — a simple geometric shape (e.g., red triangle or diamond), 64x64px, transparent background
- [ ] `void-breaker/assets/sprites/enemy_aggressive.png` exists — a visually distinct geometric shape (e.g., red/orange chevron or arrow), 64x64px, transparent background
- [ ] `void-breaker/assets/sprites/projectile_enemy.png` exists — a small coloured dot or dash (e.g., red/orange), 8x8px or 16x4px, transparent background
- [ ] `void-breaker/assets/sounds/enemy_fire.wav` exists — short percussive sound, 16-bit PCM mono WAV, under 100KB
- [ ] `void-breaker/assets/sounds/enemy_explode.wav` exists — brief explosion sound distinct from asteroid explosions, 16-bit PCM mono WAV, under 200KB
- [ ] `void-breaker/assets/sounds/player_hit.wav` exists — sharp impact sound for player damage, 16-bit PCM mono WAV, under 100KB
- [ ] All assets load without errors when passed to `arcade.load_texture()` / `arcade.load_sound()`

**Technical Details**:
- **Files to Create**:
  - `void-breaker/assets/sprites/enemy_basic.png`
  - `void-breaker/assets/sprites/enemy_aggressive.png`
  - `void-breaker/assets/sprites/projectile_enemy.png`
  - `void-breaker/assets/sounds/enemy_fire.wav`
  - `void-breaker/assets/sounds/enemy_explode.wav`
  - `void-breaker/assets/sounds/player_hit.wav`
- **Dependencies**: None beyond a basic image editor and audio tool (e.g., Audacity, sfxr, or any waveform generator)

**Detailed Implementation Requirements**:
- **Sprites**: Use simple geometric shapes with bright colours against transparent backgrounds. The Basic Shooter should be visually distinct from the Aggressive archetype (different shape, slightly different colour hue). Enemy projectiles should be clearly distinguishable from player projectiles (different colour — e.g., red/orange for enemy vs cyan/white for player). All sprites should be PNG with alpha channel. Keep sizes consistent with the player ship and asteroid sprites from Phase 2 (roughly 32-64px).
- **Sounds**: Use simple synthesized tones or waveforms. Enemy fire should sound distinctly different from player fire (lower pitch, different timbre). Enemy explosion should be distinct from asteroid explosions (shorter, more metallic). Player hit should be a sharp, attention-grabbing impact. All files must be 16-bit PCM mono WAV format per solution-design.md audio specifications.

**Test Requirements**:
- [ ] Manual testing: open each PNG in an image viewer, confirm it renders correctly with transparency
- [ ] Manual testing: play each WAV in an audio player, confirm it produces audible sound
- [ ] Manual testing: verify file sizes are reasonable (sprites under 50KB, sounds under 200KB)

**Definition of Done**:
- [ ] All 6 asset files created and placed in correct directories
- [ ] Assets are original (not copied from any existing game)
- [ ] Asset formats match solution-design.md specifications (PNG with alpha, 16-bit PCM mono WAV)
- [ ] No regression in existing functionality (Phase 2 assets unchanged)

**Notes**:
These are placeholder assets only. Final art and audio will be created in Phase 5.1. The goal is functional — not beautiful. Simple geometric shapes and synthesized tones are perfectly acceptable. AI Agent components will reference these files by exact path, so the naming convention above must be followed precisely.

---

#### Component: 3.2 — Enemy Ship Entities & AI

**Priority**: Must-have

**Estimated Effort**: 6-8 hours

**Owner**: AI Agent

**Dependencies**:
- 3.1: Enemy sprite assets must exist
- Phase 2: `arcade.Sprite` subclass pattern established by `PlayerShip` and `Asteroid` entities

**Features**:
- `EnemyShip` entity class extending `arcade.Sprite` — AI Agent
- `EnemyArchetype` enum (BASIC, AGGRESSIVE) — AI Agent
- `EnemyConfig` dataclass for per-archetype configuration — AI Agent
- Basic Shooter AI behaviour (slow movement, low fire rate, simple aim-at-player targeting) — AI Agent
- Aggressive AI behaviour (faster movement, higher fire rate, leading-shot prediction) — AI Agent
- Health, point values, destruction logic — AI Agent
- Wrap-around movement — AI Agent
- Attack telegraph (visual windup before firing) — AI Agent

**Description**:
Implements the `EnemyShip` entity with two distinct archetypes. Each archetype has its own movement speed, fire rate, targeting accuracy, health, and point value. Enemies use simple state-based AI: they move toward the player, telegraph their attacks with a brief visual windup, then fire. The AI is deliberately "fair" — enemies never fire instantly on spawn and always give the player time to react.

**Acceptance Criteria**:
- [ ] `EnemyShip` class instantiates with BASIC or AGGRESSIVE archetype
- [ ] Basic Shooter moves slowly (50-80 px/s), fires every 2-3 seconds, aims at the player's current position
- [ ] Aggressive enemy moves faster (100-150 px/s), fires every 1-1.5 seconds, aims with slight leading prediction
- [ ] Enemies wrap at screen edges identically to asteroids and player ship
- [ ] Enemies have health (Basic: 1 hit, Aggressive: 2 hits from base-damage projectile)
- [ ] Enemies award points on destruction (Basic: 200, Aggressive: 500 — configurable via `EnemyConfig`)
- [ ] Enemies telegraph attacks with a visual indicator (brief colour flash or sprite scale pulse 0.3-0.5s before firing)
- [ ] Enemies do NOT fire within the first 1.0 second after spawning (grace period)

**Technical Details**:
- **Files to Create**:
  - `void-breaker/app/src/entities/enemy_ship.py`
  - `void-breaker/app/src/config/enemy_config.py`
- **Files to Modify**: None (new files only — no serialisation constraint)
- **Key Functions/Classes**:
  - `EnemyArchetype(Enum)` — BASIC, AGGRESSIVE
  - `EnemyConfig(dataclass)` — speed, fire_rate, fire_cooldown, health, point_value, accuracy, telegraph_duration, spawn_grace_period
  - `EnemyShip(arcade.Sprite)` — the entity class
    - `__init__(archetype, config, player_ref)` — loads correct sprite, sets stats from config
    - `update_ai(dt, player_position)` — movement + targeting logic
    - `try_fire(dt)` -> `Projectile | None` — returns a new enemy projectile if cooldown expired and telegraph complete
    - `take_damage(amount)` -> `bool` — returns True if destroyed
    - `on_destroyed()` — cleanup, returns point value and drop roll result
    - `_move_toward_player(dt, player_position)` — movement AI
    - `_calculate_aim(player_position, player_velocity)` — targeting with optional leading
    - `_update_telegraph(dt)` — visual windup state management
- **Dependencies**: `arcade` library, `Projectile` class from Phase 2

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/entities/enemy_ship.py`**: Implement `EnemyShip` as a subclass of `arcade.Sprite`. The constructor accepts an `EnemyArchetype` enum and an `EnemyConfig` dataclass, loads the appropriate sprite texture (`enemy_basic.png` or `enemy_aggressive.png`), and initialises internal state: current health, fire cooldown timer, telegraph timer, spawn grace timer, and a boolean `is_telegraphing`. The `update_ai()` method is called each physics step with delta time and the player's current position. It handles movement (constant velocity toward the player with slight randomness to avoid perfectly predictable paths), spawn grace countdown, telegraph state management, and fire cooldown. Movement uses a simple "steer toward player" approach: compute the angle to the player, rotate the enemy's velocity vector toward that angle at a limited turn rate (prevents instant snapping). The `try_fire()` method checks if the fire cooldown has expired, initiates a telegraph if not already telegraphing (set `is_telegraphing = True`, reset telegraph timer), and once the telegraph duration elapses, creates and returns a new `Projectile` with `owner=ENEMY`. During the telegraph, the enemy sprite should pulse (scale oscillation between 1.0 and 1.15) or flash (alternate alpha between 255 and 180) to clearly signal the impending attack to the player. The `_calculate_aim()` method for BASIC archetype simply aims at the player's current position. For AGGRESSIVE, it adds a leading component: `predicted_position = player_position + player_velocity * lead_time`, where `lead_time` is proportional to distance / projectile_speed. The `take_damage()` method decrements health and returns whether the enemy is destroyed. Wrap-around is handled externally by the same `wrap_entity()` function used for all entities in Phase 2's `physics/wrap.py`.

- **File: `void-breaker/app/src/config/enemy_config.py`**: Define the `EnemyArchetype` enum and `EnemyConfig` dataclass. Provide factory functions `get_basic_config()` and `get_aggressive_config()` that return pre-configured `EnemyConfig` instances with default values. The config includes: `speed` (pixels/second), `turn_rate` (degrees/second for steering), `fire_rate` (shots per second), `fire_cooldown` (1/fire_rate, computed), `health` (hit points), `point_value` (score awarded), `accuracy` (0.0 to 1.0, used for aim scatter), `telegraph_duration` (seconds of visual windup before firing), `spawn_grace_period` (seconds after spawn before AI activates firing), `projectile_speed` (pixels/second for enemy projectiles), `projectile_damage` (damage per hit), `currency_drop_chance` (probability of dropping currency on death), `buff_drop_chance` (probability of dropping a buff on death — used by component 3.7). Default values: Basic = {speed: 60, turn_rate: 45, fire_rate: 0.4, health: 1, point_value: 200, accuracy: 0.6, telegraph_duration: 0.4, spawn_grace_period: 1.0, projectile_speed: 250, projectile_damage: 15.0, currency_drop_chance: 0.5, buff_drop_chance: 0.05}. Aggressive = {speed: 120, turn_rate: 90, fire_rate: 0.8, health: 2, point_value: 500, accuracy: 0.85, telegraph_duration: 0.3, spawn_grace_period: 1.0, projectile_speed: 350, projectile_damage: 20.0, currency_drop_chance: 0.7, buff_drop_chance: 0.1}.

**Test Requirements**:
- [ ] Unit test: `EnemyShip` instantiation with BASIC and AGGRESSIVE configs
- [ ] Unit test: `update_ai()` moves enemy toward a known player position
- [ ] Unit test: `try_fire()` respects cooldown timing (does not fire before cooldown expires)
- [ ] Unit test: `try_fire()` respects spawn grace period (does not fire in first 1.0 second)
- [ ] Unit test: `take_damage()` reduces health and returns correct destroyed status
- [ ] Unit test: BASIC targeting aims at player's current position (within accuracy scatter)
- [ ] Unit test: AGGRESSIVE targeting leads the player's velocity
- [ ] Unit test: telegraph state transitions (idle -> telegraphing -> fire -> cooldown -> idle)

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-2-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing functionality
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings

**Notes**:
- The `EnemyShip` does NOT add itself to any `SpriteList` — that is managed by the `SpawnManager` (component 3.4) and `EntityManager` (component 3.3).
- The `try_fire()` method returns a `Projectile` instance but does NOT add it to any `SpriteList` — the caller (combat update loop in component 3.3) is responsible for adding it to the enemy projectiles list.
- Enemy movement AI should include a small random offset (jitter) to prevent enemies from stacking on identical paths. Add a random angle perturbation of +/- 10 degrees to the steering angle each update.
- The `Projectile` class from Phase 2 already supports an `owner` field distinguishing PLAYER from ENEMY projectiles. Reuse it — do not create a separate `EnemyProjectile` class.

---

#### Component: 3.3 — Enemy Projectile System & Expanded Collisions

**Priority**: Must-have

**Estimated Effort**: 4-6 hours

**Owner**: AI Agent

**Dependencies**:
- 3.2: `EnemyShip` entity and `try_fire()` method must exist
- Phase 2: `EntityManager`, `CollisionSystem`, `Projectile` entity, `CombatPhase` state

**Features**:
- Enemy projectile SpriteList in `EntityManager` — AI Agent
- Enemy firing integration in combat update loop — AI Agent
- Player vs enemy projectiles collision — AI Agent
- Player projectiles vs enemy ships collision — AI Agent
- Player ship vs enemy ships collision — AI Agent
- Ghost sprite wrap-around collision for all new pairs — AI Agent

**Description**:
Integrates enemy ships and their projectiles into the existing entity management and collision detection systems. Adds three new collision pairs to `CollisionSystem` and wires enemy update/firing into the `CombatPhase` update loop. This is the critical integration component that connects enemy AI to the gameplay.

**Acceptance Criteria**:
- [ ] `EntityManager` has `enemies: arcade.SpriteList` and `enemy_projectiles: arcade.SpriteList` attributes
- [ ] Enemy projectiles appear when enemies fire and travel at the configured speed
- [ ] Enemy projectiles damage the player on collision (player shields reduced by `projectile_damage`)
- [ ] Player projectiles destroy enemies (reduce enemy health, destroy when health <= 0)
- [ ] Player ship colliding with an enemy ship damages both (player takes collision damage, enemy takes collision damage)
- [ ] All new collision pairs work correctly at screen edges via ghost sprite approach
- [ ] Enemy projectiles have a maximum lifetime/range and are removed when expired
- [ ] Destroyed enemies are removed from the `enemies` SpriteList

**Technical Details**:
- **Files to Modify**:
  - `void-breaker/app/src/managers/entity_manager.py` — add `enemies` and `enemy_projectiles` SpriteLists **[SERIALISATION CONSTRAINT: shared with Phase 2]**
  - `void-breaker/app/src/physics/collisions.py` — add 3 new collision check methods **[SERIALISATION CONSTRAINT: shared with Phase 2]**
  - `void-breaker/app/src/states/combat.py` — add enemy update and firing to the update loop **[SERIALISATION CONSTRAINT: shared with Phase 2, also modified by 3.4 and 3.5]**
- **Files to Modify (minor)**:
  - `void-breaker/app/src/entities/projectile.py` — ensure `owner` field supports ENEMY value (may already exist from Phase 2 design)
- **Key Functions/Classes**:
  - `EntityManager.enemies: arcade.SpriteList` — new attribute
  - `EntityManager.enemy_projectiles: arcade.SpriteList` — new attribute
  - `EntityManager.clear_enemies()` — removes all enemies and enemy projectiles (for level transitions)
  - `CollisionSystem.check_player_vs_enemy_projectiles()` -> `list[tuple[PlayerShip, Projectile]]`
  - `CollisionSystem.check_player_projectiles_vs_enemies()` -> `list[tuple[Projectile, EnemyShip]]`
  - `CollisionSystem.check_player_vs_enemies()` -> `list[tuple[PlayerShip, EnemyShip]]`
  - `CombatPhase._update_enemies(dt)` — iterates enemies, calls `update_ai()`, handles `try_fire()` results
  - `CombatPhase._process_enemy_collisions()` — processes results from new collision checks
- **Dependencies**: `arcade`, `EnemyShip` from 3.2, `Projectile` from Phase 2, `wrap_entity` from Phase 2

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/managers/entity_manager.py`**: Add two new SpriteList attributes to the `EntityManager.__init__()` method: `self.enemies = arcade.SpriteList()` and `self.enemy_projectiles = arcade.SpriteList()`. Note: `enemies` does NOT use spatial hashing because enemy positions change every frame (dynamic entities). Add `self.enemies` and `self.enemy_projectiles` to the draw order — enemies should render after asteroids but before the player ship, and enemy projectiles should render after enemies but before player projectiles. This ensures the player ship is always visually on top. Add a `clear_enemies()` method that calls `self.enemies.clear()` and `self.enemy_projectiles.clear()` — used during level transitions. Update any existing `clear_all()` or reset method to also clear these new lists.

- **File: `void-breaker/app/src/physics/collisions.py`**: Add three new public methods to `CollisionSystem`. Each method follows the same pattern as existing collision checks from Phase 2: use `arcade.check_for_collision_with_list()` for sprite-vs-list checks. `check_player_vs_enemy_projectiles()` checks the player sprite against the enemy_projectiles SpriteList. `check_player_projectiles_vs_enemies()` iterates the player_projectiles SpriteList and checks each against the enemies SpriteList. `check_player_vs_enemies()` checks the player sprite against the enemies SpriteList. All three methods must support the ghost sprite wrap-around approach from Phase 2 — if the player or any enemy/projectile is within one sprite-width of a screen edge, create a temporary ghost at the wrapped position and include it in collision checks. Each method returns a list of collision pairs for the caller to process. Add a new `check_all_combat()` method (or extend the existing `check_all()`) that calls all collision methods including the new ones, returning a comprehensive collision result object.

- **File: `void-breaker/app/src/states/combat.py`**: In the `CombatPhase.physics_step()` (or equivalent update method), add two new calls: `self._update_enemies(dt)` and `self._process_enemy_collisions()`. The `_update_enemies()` method iterates all enemies in `self.entity_manager.enemies`, calls `enemy.update_ai(dt, player_position)`, then calls `enemy.try_fire(dt)` — if it returns a `Projectile`, add that projectile to `self.entity_manager.enemy_projectiles`. Also update all enemy projectiles for lifetime expiry (remove expired ones). The `_process_enemy_collisions()` method calls the three new collision check methods from `CollisionSystem` and handles results: player hit by enemy projectile -> call `player.take_damage(projectile.damage)`, remove projectile; player projectile hits enemy -> call `enemy.take_damage(projectile.damage)`, remove projectile, if enemy destroyed call `enemy.on_destroyed()`, award points, remove enemy; player collides with enemy -> damage both, remove enemy if destroyed. Wrap all enemies using the same `wrap_entity()` function used for other entities.

**Test Requirements**:
- [ ] Unit test: `EntityManager` has `enemies` and `enemy_projectiles` SpriteLists
- [ ] Unit test: collision detection for player vs enemy projectile at various positions
- [ ] Unit test: collision detection for player projectile vs enemy at various positions
- [ ] Unit test: collision detection for player vs enemy ship at various positions
- [ ] Unit test: wrap-around ghost collision at screen edges for all new pairs
- [ ] Unit test: enemy projectile lifetime expiry and removal
- [ ] Integration test: enemy fires projectile, projectile collides with player, player takes damage

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-3-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing Phase 2 functionality (player-asteroid, projectile-asteroid collisions still work)
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings

**Notes**:
- **Critical serialisation constraint**: This component modifies `entity_manager.py`, `collisions.py`, and `combat.py` which are all created in Phase 2. Ensure Phase 2 is fully complete and merged before starting this component.
- The `enemies` SpriteList intentionally does NOT use `use_spatial_hash=True` because enemy positions change every frame. Spatial hashing is only beneficial for static or semi-static entities (asteroids, shop nodes).
- Enemy-vs-asteroid collisions are intentionally NOT implemented. Enemies fly through asteroids — this simplifies AI and prevents enemies from being destroyed by asteroids before the player can engage them.
- Enemy projectile-vs-asteroid collisions are disabled by default (per solution-design.md) for performance reasons.
- The collision damage for player-vs-enemy-ship contact should be significant (25-30 damage) to discourage ramming as a strategy and emphasize the shooting mechanic.

---

#### Component: 3.4 — Spawn Manager & Enemy Waves

**Priority**: Must-have

**Estimated Effort**: 4-6 hours

**Owner**: AI Agent

**Dependencies**:
- 3.2: `EnemyShip` entity and `EnemyConfig`
- Phase 2: `SpawnManager` (asteroid spawning), `DifficultyParams`, `difficulty_tables.py`

**Features**:
- Expand `SpawnManager` with enemy spawning logic — AI Agent
- Per-level enemy spawn configuration (enabled/disabled, count, interval, aggression) — AI Agent
- Screen-edge spawn positioning — AI Agent
- Enemy count cap enforcement — AI Agent
- Wave/interval-based spawning during combat — AI Agent
- Expand `DifficultyParams` with enemy fields — AI Agent

**Description**:
Extends the existing `SpawnManager` to handle timed enemy spawning during combat phases. Enemies are spawned at screen edges and move inward toward the play area. The spawn rate, enemy type mix, and maximum count are all controlled by the difficulty tables, scaling per level. Early levels (1-5) have no enemies. Mid levels (6-15) introduce Basic Shooters, then Aggressive enemies. Late levels (16+) feature frequent, aggressive enemy waves.

**Acceptance Criteria**:
- [ ] `SpawnManager` supports enemy spawning alongside existing asteroid spawning
- [ ] Enemy spawning is disabled for levels 1-5 (configurable via difficulty tables)
- [ ] Enemies spawn at random screen-edge positions, moving inward
- [ ] Enemy spawn interval decreases as levels increase (enemies appear more frequently)
- [ ] Aggressive enemies are introduced at a configurable level (default: level 10)
- [ ] Enemy count cap prevents more than `max_enemy_count` enemies on screen simultaneously
- [ ] `DifficultyParams` includes all enemy-related fields (spawn_enabled, count_max, spawn_interval, aggression, archetype_mix)

**Technical Details**:
- **Files to Modify**:
  - `void-breaker/app/src/managers/spawn_manager.py` — add enemy spawning methods **[SERIALISATION CONSTRAINT: shared with Phase 2]**
  - `void-breaker/app/src/config/difficulty_tables.py` — add enemy parameters to difficulty table entries **[SERIALISATION CONSTRAINT: shared with Phase 2, also modified by 3.6]**
  - `void-breaker/app/src/config/game_config.py` — add enemy fields to `DifficultyParams` **[SERIALISATION CONSTRAINT: shared with Phase 2]**
  - `void-breaker/app/src/states/combat.py` — add spawn manager enemy update call **[SERIALISATION CONSTRAINT: shared with 3.3 and 3.5]**
- **Key Functions/Classes**:
  - `DifficultyParams` extended fields: `enemy_spawn_enabled`, `enemy_count_max`, `enemy_spawn_interval`, `enemy_aggression`, `aggressive_ratio` (proportion of aggressive vs basic enemies)
  - `SpawnManager.update_enemy_spawning(dt, current_enemy_count)` -> `list[EnemyShip]` — returns newly spawned enemies
  - `SpawnManager._get_spawn_edge_position()` -> `tuple[float, float, float, float]` — returns (x, y, vx, vy) for screen-edge spawn with inward velocity
  - `SpawnManager._select_archetype(difficulty_params)` -> `EnemyArchetype` — weighted random selection based on `aggressive_ratio`
  - `SpawnManager.reset_enemy_spawning()` — reset timers for new level
- **Dependencies**: `EnemyShip` and `EnemyConfig` from 3.2, `random` module

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/managers/spawn_manager.py`**: Add an `_enemy_spawn_timer: float` attribute initialised to 0.0 and an `_enemy_spawn_active: bool` flag. The new `update_enemy_spawning()` method is called each physics step during combat. It checks `difficulty_params.enemy_spawn_enabled` — if False, returns an empty list immediately. If True, it increments the timer by `dt`. When the timer exceeds `difficulty_params.enemy_spawn_interval`, it resets the timer and checks whether `current_enemy_count < difficulty_params.enemy_count_max`. If the cap is not reached, it creates a new `EnemyShip` with an archetype selected by `_select_archetype()` and positions it using `_get_spawn_edge_position()`. The `_get_spawn_edge_position()` method randomly selects one of four screen edges (top, bottom, left, right), places the enemy just off-screen on that edge at a random position along the edge, and assigns an initial velocity vector pointing inward (toward screen centre with some randomness). The velocity magnitude should be the enemy's configured speed. The `_select_archetype()` method uses `difficulty_params.aggressive_ratio` as the probability of spawning an AGGRESSIVE enemy, otherwise spawns BASIC. Add `reset_enemy_spawning()` that resets the timer and is called at each level start.

- **File: `void-breaker/app/src/config/difficulty_tables.py`**: Extend each level's `DifficultyParams` entry with enemy-specific fields. Levels 1-5: `enemy_spawn_enabled=False`. Level 6+: `enemy_spawn_enabled=True`, `enemy_count_max` starts at 1 and increases to 3 by level 10, then to 5 by level 15, then caps at 8 for level 20+. `enemy_spawn_interval` starts at 8.0 seconds at level 6 and decreases to 3.0 seconds by level 20+. `aggressive_ratio` starts at 0.0 (all basic) at level 6, increases to 0.3 by level 10, 0.5 by level 15, 0.7 by level 25+. `enemy_aggression` is a global multiplier (0.0 to 1.0) that scales enemy fire rate and accuracy — starts at 0.3 at level 6 and reaches 0.9 by level 25+. Note: these are initial values; component 3.6 will refine them for balance.

- **File: `void-breaker/app/src/config/game_config.py`**: Add the following fields to the `DifficultyParams` dataclass: `enemy_spawn_enabled: bool = False`, `enemy_count_max: int = 0`, `enemy_spawn_interval: float = 10.0`, `enemy_aggression: float = 0.0`, `aggressive_ratio: float = 0.0`. These fields have sensible defaults (no enemies) so that existing Phase 2 code using `DifficultyParams` continues to work without modification.

- **File: `void-breaker/app/src/states/combat.py`**: In the combat update loop (same area modified by 3.3), add a call to `self.spawn_manager.update_enemy_spawning(dt, len(self.entity_manager.enemies))`. For each returned `EnemyShip`, add it to `self.entity_manager.enemies`. At the start of each new level (in the level transition logic), call `self.spawn_manager.reset_enemy_spawning()`.

**Test Requirements**:
- [ ] Unit test: `SpawnManager.update_enemy_spawning()` returns no enemies when `enemy_spawn_enabled=False`
- [ ] Unit test: enemy spawns after `spawn_interval` seconds when enabled and under cap
- [ ] Unit test: no enemy spawns when at `enemy_count_max` cap
- [ ] Unit test: `_get_spawn_edge_position()` returns positions just off-screen with inward velocity
- [ ] Unit test: `_select_archetype()` respects `aggressive_ratio` (statistical test over many iterations)
- [ ] Unit test: `reset_enemy_spawning()` resets timer to 0
- [ ] Integration test: run spawn manager over simulated 30 seconds, verify enemy count and types match difficulty params

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-4-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing asteroid spawning functionality
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings

**Notes**:
- **Critical serialisation constraint**: This component modifies `spawn_manager.py`, `difficulty_tables.py`, `game_config.py`, and `combat.py` — all shared with Phase 2. Phase 2 must be complete before starting.
- `combat.py` is also modified by 3.3 — these components should be sequenced (3.3 first, then 3.4) or carefully merged.
- Enemy spawning uses a simple interval timer, not wave-based spawning. This keeps the implementation straightforward. Wave patterns (e.g., "3 enemies at once every 15 seconds") can be added as a refinement in a future phase if needed.
- The level completion condition from Phase 2 (all asteroids destroyed) remains unchanged in Phase 3. Enemies do NOT need to be destroyed to complete a level — they are continuous pressure during the asteroid-clearing objective. Surviving enemies are cleared when the level transitions.

---

#### Component: 3.5 — Damage Feedback & Visual Effects

**Priority**: Must-have

**Estimated Effort**: 4-6 hours

**Owner**: AI Agent

**Dependencies**:
- 3.3: Enemy collision system must be wired up (player can take damage from enemies)
- Phase 2: `PlayerShip.take_damage()`, `particle_system.py` (if exists), `AudioManager`

**Features**:
- Player damage flash/tint effect — AI Agent
- Player invulnerability window after taking damage (0.5-1.0 second) — AI Agent
- Player visual flashing during invulnerability — AI Agent
- Enemy destruction explosion particles — AI Agent
- Enemy destruction sound effect integration — AI Agent
- Player ship destruction sequence on game over — AI Agent
- Player hit sound effect integration — AI Agent

**Description**:
Implements all visual and audio feedback for combat damage. When the player takes damage, the ship briefly flashes red and becomes invulnerable for a short window (preventing instant-kill from multiple simultaneous collisions). When enemies are destroyed, they produce explosion particles and a distinct sound. When the player's shields reach zero, a destruction sequence plays before transitioning to game over.

**Acceptance Criteria**:
- [ ] Player ship visually flashes red/white when taking damage (3-4 rapid colour alternations over 0.2 seconds)
- [ ] Player is invulnerable for 0.75 seconds after taking damage (configurable)
- [ ] During invulnerability, the player ship visually flickers (alpha oscillation between 255 and 80)
- [ ] `player_hit.wav` plays when the player takes damage
- [ ] Enemy destruction spawns explosion particles (5-10 sprites expanding outward, fading over 0.3-0.5 seconds)
- [ ] `enemy_explode.wav` plays when an enemy is destroyed
- [ ] Player destruction on game over plays a larger explosion sequence (15-20 particles) before state transition
- [ ] Invulnerability prevents all damage (asteroid, enemy projectile, enemy collision) during the window
- [ ] Invulnerability does NOT prevent the player from firing or moving

**Technical Details**:
- **Files to Create**:
  - `void-breaker/app/src/rendering/damage_effects.py`
- **Files to Modify**:
  - `void-breaker/app/src/entities/player_ship.py` — add invulnerability state, damage flash **[SERIALISATION CONSTRAINT: shared with Phase 2]**
  - `void-breaker/app/src/states/combat.py` — integrate damage effects, invulnerability check **[SERIALISATION CONSTRAINT: shared with 3.3 and 3.4]**
  - `void-breaker/app/src/rendering/particle_system.py` — add enemy explosion emitter (if particle system exists from Phase 2; otherwise create it)
- **Key Functions/Classes**:
  - `DamageEffects` class (in `damage_effects.py`):
    - `trigger_damage_flash(sprite)` — starts the red flash effect on a sprite
    - `trigger_invulnerability(ship, duration)` — starts the invulnerability window with flicker
    - `trigger_explosion(position, size, particle_list)` — spawns explosion particles at a position
    - `trigger_destruction_sequence(position, particle_list)` — larger explosion for ship death
    - `update(dt)` — updates all active effects (flash timers, invulnerability countdown, particle lifetimes)
  - `PlayerShip` extensions:
    - `is_invulnerable: bool` — property, True during invulnerability window
    - `invulnerability_timer: float` — countdown timer
    - `take_damage(amount)` — modified to check invulnerability first, trigger effects if damage applies
- **Dependencies**: `arcade`, `AudioManager` from Phase 1, `EnemyShip` from 3.2

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/rendering/damage_effects.py`**: Implement a `DamageEffects` class that manages all combat visual effects. It maintains a list of active effects, each with a timer and a target sprite reference. `trigger_damage_flash()` adds an effect that rapidly alternates the target sprite's `color` property between `(255, 0, 0)` (red) and `(255, 255, 255)` (white) 3-4 times over 0.2 seconds, then restores the original colour. `trigger_invulnerability()` starts a timer (default 0.75 seconds) and adds an effect that oscillates the sprite's `alpha` between 255 and 80 at ~8Hz until the timer expires, then restores full alpha. `trigger_explosion()` creates 5-10 small particle sprites at the given position with random outward velocities (100-200 px/s in random directions) and a lifetime of 0.3-0.5 seconds. Each particle starts with full alpha and fades to 0 over its lifetime. Particles use a small solid-colour sprite (4x4 or 8x8 pixels) with a colour matching the destroyed entity (orange/yellow for enemies). `trigger_destruction_sequence()` is a larger version with 15-20 particles, higher velocity (150-300 px/s), and a 0.5-0.8 second lifetime. The `update(dt)` method advances all active effects, removes expired effects, and updates particle positions and alpha values. Particles that have expired their lifetime are removed from the provided SpriteList.

- **File: `void-breaker/app/src/entities/player_ship.py`**: Add `_invulnerability_timer: float = 0.0` and `_is_invulnerable: bool = False` attributes. Add a read-only `is_invulnerable` property. Modify `take_damage()` to check `self._is_invulnerable` first — if True, return immediately without applying damage. If False, apply the damage, then set `_is_invulnerable = True` and `_invulnerability_timer = INVULNERABILITY_DURATION` (default 0.75 seconds, defined in `game_config.py`). Add an `update_invulnerability(dt)` method that decrements the timer and clears the flag when expired. This method must be called each physics step from the combat update loop.

- **File: `void-breaker/app/src/states/combat.py`**: In the collision processing logic (from 3.3), add an invulnerability check before applying damage: only call `player.take_damage()` if `not player.is_invulnerable`. After damage is applied, call `self.damage_effects.trigger_damage_flash(player)` and `self.damage_effects.trigger_invulnerability(player, INVULNERABILITY_DURATION)`. In the enemy destruction handler, call `self.damage_effects.trigger_explosion(enemy.position, "medium", self.entity_manager.particles)` and `self.audio_manager.play("enemy_explode")`. When the player's shields reach zero, call `self.damage_effects.trigger_destruction_sequence(player.position, self.entity_manager.particles)` and delay the game over transition by 0.8 seconds (the destruction animation duration) before switching to the GameOver state. Add `self.damage_effects.update(dt)` to the update loop. Add `self.player.update_invulnerability(dt)` to the update loop.

**Test Requirements**:
- [ ] Unit test: `PlayerShip.take_damage()` does not reduce shields when `is_invulnerable` is True
- [ ] Unit test: `PlayerShip.take_damage()` reduces shields and activates invulnerability when `is_invulnerable` is False
- [ ] Unit test: invulnerability timer expires after configured duration
- [ ] Unit test: `DamageEffects.trigger_explosion()` creates the correct number of particles
- [ ] Unit test: particle lifetimes expire and particles are removed after their duration
- [ ] Unit test: damage flash effect restores original sprite colour after completion
- [ ] Manual testing: take damage from enemy projectile, observe red flash and invulnerability flicker
- [ ] Manual testing: destroy an enemy, observe explosion particles and sound

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-5-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing functionality
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings
- [ ] Core application is still working post component implementation

**Notes**:
- The invulnerability window is critical for fairness — without it, a player could lose all shields in a single frame from multiple simultaneous collisions (e.g., enemy projectile + asteroid at the same time).
- The destruction sequence delay (0.8s before game over) gives the player visual closure and prevents jarring instant transitions.
- Particle sprites should be simple solid-colour squares created programmatically via `arcade.make_soft_square_texture()` or `arcade.make_circle_texture()` — no additional asset files needed.
- The damage flash and invulnerability effects apply to the player ship only. Enemy damage is handled by simple destruction — enemies do not have invulnerability windows.
- If Phase 2 did not implement a particle system, this component creates a basic one. The particle approach here is simple sprite-based (not a GPU particle emitter) — it adds sprites to a SpriteList and updates their position/alpha each frame.

---

#### Component: 3.6 — Difficulty Scaling & Balance

**Priority**: Must-have

**Estimated Effort**: 3-4 hours

**Owner**: AI Agent

**Dependencies**:
- 3.4: `DifficultyParams` enemy fields and basic difficulty table entries must exist
- Phase 2: existing difficulty scaling for asteroids

**Features**:
- Refined difficulty curves for 30+ levels — AI Agent
- Balanced asteroid + enemy scaling — AI Agent
- Early/mid/late game progression tuning — AI Agent
- Currency economy balancing across difficulty curve — AI Agent

**Description**:
Refines `difficulty_tables.py` with carefully tuned values for 30+ levels, creating a smooth difficulty curve that supports 30+ minutes of skilled play. The curve has three phases: early game (levels 1-5) with asteroids only to teach fundamentals, mid game (levels 6-15) introducing enemies and forcing upgrade decisions, and late game (levels 16-30+) with intense but fair combat. The tuning ensures no sudden impossible spikes and that the currency economy supports meaningful shop decisions.

**Acceptance Criteria**:
- [ ] `difficulty_tables.py` contains tuned parameters for at least 30 levels
- [ ] Levels 1-5: asteroids only, increasing count from 3 to 8, no enemies
- [ ] Levels 6-10: enemies introduced (Basic Shooters only), asteroid count 8-12, enemy count 1-3
- [ ] Levels 11-15: Aggressive enemies introduced (20-30% ratio), asteroid count 12-18, enemy count 3-5
- [ ] Levels 16-25: high intensity (40-70% aggressive ratio), asteroid count 15-25, enemy count 5-7
- [ ] Levels 26-30+: maximum intensity with caps (asteroid count capped at 30, enemy count capped at 8)
- [ ] Asteroid speed scales gradually (not abruptly) across all levels
- [ ] Currency drop chance and value scale to maintain economy viability at higher levels
- [ ] A level-30 DifficultyParams can be read and all values are within documented ranges

**Technical Details**:
- **Files to Modify**:
  - `void-breaker/app/src/config/difficulty_tables.py` — full rewrite of table values **[SERIALISATION CONSTRAINT: shared with 3.4]**
- **Files to Create**: None
- **Key Functions/Classes**:
  - `get_difficulty_params(level: int)` -> `DifficultyParams` — main function, returns params for any level
  - `_interpolate_params(level, tier_start, tier_end, start_params, end_params)` — smooth interpolation between tier boundaries
  - `DIFFICULTY_TIERS` — dict defining parameter breakpoints at key levels (1, 5, 10, 15, 20, 25, 30)
- **Dependencies**: `DifficultyParams` dataclass from `game_config.py`

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/config/difficulty_tables.py`**: Implement `get_difficulty_params(level)` as the single entry point for difficulty configuration. Instead of a flat list of 30+ hardcoded entries, use a tier-based interpolation system. Define `DIFFICULTY_TIERS` as a dictionary mapping level numbers to `DifficultyParams` instances at key breakpoints: levels 1, 5, 10, 15, 20, 25, and 30. For any level between breakpoints, use linear interpolation between the two nearest tiers. For levels above 30, use the level-30 values (difficulty caps — the game does not become infinitely harder, preventing unfairness). The tier values should be:

  **Level 1**: asteroid_count=3, asteroid_speed_min=30, asteroid_speed_max=80, enemy_spawn_enabled=False, enemy_count_max=0, enemy_spawn_interval=99, enemy_aggression=0.0, aggressive_ratio=0.0, currency_drop_chance=0.4, currency_value_base=10.

  **Level 5**: asteroid_count=8, asteroid_speed_min=40, asteroid_speed_max=120, enemy_spawn_enabled=False, enemy_count_max=0, enemy_spawn_interval=99, enemy_aggression=0.0, aggressive_ratio=0.0, currency_drop_chance=0.4, currency_value_base=12.

  **Level 10**: asteroid_count=12, asteroid_speed_min=50, asteroid_speed_max=160, enemy_spawn_enabled=True, enemy_count_max=3, enemy_spawn_interval=6.0, enemy_aggression=0.4, aggressive_ratio=0.2, currency_drop_chance=0.35, currency_value_base=15.

  **Level 15**: asteroid_count=18, asteroid_speed_min=60, asteroid_speed_max=200, enemy_spawn_enabled=True, enemy_count_max=5, enemy_spawn_interval=4.5, enemy_aggression=0.6, aggressive_ratio=0.4, currency_drop_chance=0.35, currency_value_base=18.

  **Level 20**: asteroid_count=22, asteroid_speed_min=70, asteroid_speed_max=230, enemy_spawn_enabled=True, enemy_count_max=6, enemy_spawn_interval=3.5, enemy_aggression=0.75, aggressive_ratio=0.55, currency_drop_chance=0.30, currency_value_base=22.

  **Level 25**: asteroid_count=27, asteroid_speed_min=75, asteroid_speed_max=250, enemy_spawn_enabled=True, enemy_count_max=7, enemy_spawn_interval=3.0, enemy_aggression=0.85, aggressive_ratio=0.65, currency_drop_chance=0.30, currency_value_base=25.

  **Level 30**: asteroid_count=30, asteroid_speed_min=80, asteroid_speed_max=270, enemy_spawn_enabled=True, enemy_count_max=8, enemy_spawn_interval=2.5, enemy_aggression=0.9, aggressive_ratio=0.7, currency_drop_chance=0.28, currency_value_base=28.

  The `_interpolate_params()` helper performs linear interpolation on all numeric fields of `DifficultyParams` between two tier boundary values, clamping booleans (enemy_spawn_enabled flips from False to True at the transition from tier 5 to tier 10 — use a threshold: if interpolated value >= 0.5, enable). Integer fields (asteroid_count, enemy_count_max) should be rounded to the nearest integer after interpolation.

**Test Requirements**:
- [ ] Unit test: `get_difficulty_params(1)` returns level-1 values exactly
- [ ] Unit test: `get_difficulty_params(30)` returns level-30 values exactly
- [ ] Unit test: `get_difficulty_params(7)` returns interpolated values between level-5 and level-10 tiers
- [ ] Unit test: levels 1-5 have `enemy_spawn_enabled=False`
- [ ] Unit test: levels 6+ have `enemy_spawn_enabled=True`
- [ ] Unit test: `get_difficulty_params(50)` returns level-30 values (cap)
- [ ] Unit test: `asteroid_count` is monotonically non-decreasing from level 1 to 30
- [ ] Unit test: `enemy_count_max` is monotonically non-decreasing from level 6 to 30
- [ ] Unit test: all numeric values are within reasonable ranges (no negatives, no values exceeding documented maximums)

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-6-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing asteroid-only difficulty scaling (levels 1-5 should behave identically to Phase 2)
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings

**Notes**:
- The tier-based interpolation approach is chosen over 30+ hardcoded entries because it is easier to tune — change one breakpoint value and all intermediate levels adjust automatically.
- Currency economy values (drop chance, value base) decrease slightly at higher levels. This is intentional — at higher levels, enemies also drop currency (via enemy `currency_drop_chance` in `EnemyConfig`), so total currency availability remains viable. The decreasing asteroid drops prevent currency inflation.
- The difficulty cap at level 30 is a deliberate design choice. Beyond level 30, the game is still challenging but does not become arbitrarily harder. This follows the requirement of "intense but fair" late-game difficulty.
- These values are starting points for playtesting. The parameterised approach makes it easy to adjust during Phase 5 when difficulty presets (Casual/Classic/Hard) are implemented.

---

#### Component: 3.7 — Buff Pickups (Optional)

**Priority**: Nice-to-have

**Estimated Effort**: 3-4 hours

**Owner**: AI Agent

**Dependencies**:
- 3.3: `EntityManager` with enemies SpriteList, `CollisionSystem` for pickup collection, `CombatPhase` update loop
- 3.2: `EnemyShip.on_destroyed()` (for drop rolls)

**Features**:
- `BuffPickup` entity with HEAL, DAMAGE_BOOST, SPEED_BOOST types — AI Agent
- Rare drops from enemy destruction — AI Agent
- Duration-based buff tracking — AI Agent
- Buff effect application and expiry — AI Agent
- Buff collection collision — AI Agent
- Visual distinction from currency pickups — AI Agent

**Description**:
Implements optional buff pickups that rarely drop from destroyed enemies. Buffs provide temporary benefits: HEAL restores shields instantly, DAMAGE_BOOST increases weapon damage for a duration, SPEED_BOOST increases ship speed for a duration. Buff effects are tracked as timers and automatically expire. Buffs add tactical depth to combat without being required for progression.

**Acceptance Criteria**:
- [ ] `BuffPickup` entity renders with a visually distinct sprite per buff type
- [ ] Buff pickups drop from destroyed enemies based on `buff_drop_chance` in `EnemyConfig`
- [ ] HEAL buff restores 25% of max shields on collection (configurable)
- [ ] DAMAGE_BOOST buff increases weapon damage by 50% for 8 seconds (configurable)
- [ ] SPEED_BOOST buff increases thrust by 40% for 8 seconds (configurable)
- [ ] Active buff durations are tracked and buffs expire automatically
- [ ] Only one buff of each type can be active at a time (collecting the same type refreshes the duration)
- [ ] Buff pickups have a lifetime (10 seconds) and disappear if not collected
- [ ] Buff collection plays a distinct sound (`pickup_buff.wav` if available, or reuse `pickup_currency.wav`)

**Technical Details**:
- **Files to Create**:
  - `void-breaker/app/src/entities/buff_pickup.py`
  - `void-breaker/app/src/managers/buff_manager.py`
- **Files to Modify**:
  - `void-breaker/app/src/managers/entity_manager.py` — add `buff_pickups: arcade.SpriteList` **[SERIALISATION CONSTRAINT: shared with Phase 2 and 3.3]**
  - `void-breaker/app/src/physics/collisions.py` — add player vs buff pickups collision check **[SERIALISATION CONSTRAINT: shared with Phase 2 and 3.3]**
  - `void-breaker/app/src/states/combat.py` — add buff pickup collision handling, buff updates **[SERIALISATION CONSTRAINT: shared with 3.3, 3.4, 3.5]**
  - `void-breaker/app/src/entities/player_ship.py` — add methods for applying/removing buff stat modifications **[SERIALISATION CONSTRAINT: shared with Phase 2 and 3.5]**
- **Key Functions/Classes**:
  - `BuffType(Enum)` — HEAL, DAMAGE_BOOST, SPEED_BOOST
  - `BuffPickup(arcade.Sprite)` — entity with `buff_type`, `magnitude`, `duration`, `lifetime_remaining`
  - `BuffManager` — tracks active buffs, applies/removes stat modifications
    - `apply_buff(buff_type, magnitude, duration, ship)` — activates a buff
    - `update(dt, ship)` — decrements timers, removes expired buffs, restores stats
    - `get_active_buffs()` -> `list[tuple[BuffType, float]]` — returns active buffs with remaining duration
    - `clear_all()` — removes all active buffs (for level transitions or game over)
  - `PlayerShip.apply_damage_boost(multiplier)` / `remove_damage_boost()`
  - `PlayerShip.apply_speed_boost(multiplier)` / `remove_speed_boost()`
- **Dependencies**: `arcade`, `EnemyShip` from 3.2, `EnemyConfig` from 3.2

**Detailed Implementation Requirements**:

- **File: `void-breaker/app/src/entities/buff_pickup.py`**: Implement `BuffPickup` as a subclass of `arcade.Sprite`. The constructor takes a `BuffType`, `magnitude` (float), `duration` (seconds for timed buffs, 0 for instant like HEAL), and a position. Use `arcade.make_circle_texture()` or a procedurally generated texture with a distinct colour per type: green for HEAL, red/orange for DAMAGE_BOOST, cyan/blue for SPEED_BOOST. The pickup has a `lifetime_remaining` (default 10 seconds) that decrements each update. When lifetime expires, the pickup removes itself from its parent SpriteList. Add a gentle bobbing animation (sinusoidal y-offset of +/- 3 pixels at 2Hz) to visually distinguish from static debris. Default magnitudes: HEAL = 0.25 (restore 25% of max shields), DAMAGE_BOOST = 1.5 (50% more damage), SPEED_BOOST = 1.4 (40% more thrust).

- **File: `void-breaker/app/src/managers/buff_manager.py`**: Implement `BuffManager` to track active buffs. Internally, maintain a dictionary mapping `BuffType` to a tuple of `(remaining_duration, magnitude)`. `apply_buff()` adds or refreshes a buff entry. For HEAL, it is instant — directly call `ship.shields = min(ship.shields + magnitude * ship.max_shields, ship.max_shields)` and do not store it as an active buff. For DAMAGE_BOOST and SPEED_BOOST, store the buff and call the appropriate `PlayerShip` method to apply the stat modification. `update(dt)` decrements all active buff timers and calls the removal method on the ship when a buff expires. `get_active_buffs()` returns active buff data for HUD display (Phase 5 will render buff indicators). `clear_all()` removes all buffs and restores ship stats — called on game over.

- **File: `void-breaker/app/src/entities/player_ship.py`**: Add `_damage_boost_active: bool = False`, `_damage_boost_multiplier: float = 1.0`, `_speed_boost_active: bool = False`, `_speed_boost_multiplier: float = 1.0`. Modify the `effective_damage` property (or wherever effective stats are calculated) to multiply by `_damage_boost_multiplier` when the boost is active. Similarly modify `effective_thrust`. Add `apply_damage_boost(multiplier)`, `remove_damage_boost()`, `apply_speed_boost(multiplier)`, `remove_speed_boost()` methods that set/clear these attributes.

- **File: `void-breaker/app/src/states/combat.py`**: In the enemy destruction handler, after `enemy.on_destroyed()`, roll for buff drop using `enemy_config.buff_drop_chance`. If successful, randomly select a `BuffType` (weighted: HEAL 40%, DAMAGE_BOOST 30%, SPEED_BOOST 30%) and create a `BuffPickup` at the enemy's position, adding it to `self.entity_manager.buff_pickups`. Add a collision check for player vs buff_pickups in the collision processing. On collection, call `self.buff_manager.apply_buff()` with the pickup's type, magnitude, and duration, then remove the pickup. Add `self.buff_manager.update(dt, self.player)` to the update loop.

**Test Requirements**:
- [ ] Unit test: `BuffPickup` creation with each buff type
- [ ] Unit test: `BuffPickup` lifetime expiry and self-removal
- [ ] Unit test: `BuffManager.apply_buff()` for HEAL — shields increase correctly, capped at max
- [ ] Unit test: `BuffManager.apply_buff()` for DAMAGE_BOOST — stat modification applied
- [ ] Unit test: `BuffManager.update()` expires timed buffs and restores stats
- [ ] Unit test: applying the same buff type refreshes duration (does not stack)
- [ ] Unit test: `BuffManager.clear_all()` removes all active buffs
- [ ] Manual testing: destroy an enemy, observe buff pickup spawn, collect it, verify effect

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-3-component-3-7-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-3.md` (max 100 lines for this component)
- [ ] No regression in existing functionality
- [ ] `black --check` and `isort --check-only` pass
- [ ] All public functions have Google-style docstrings
- [ ] Core application is still working post component implementation

**Notes**:
- This component is **optional** (Nice-to-have). If Phase 3 is running behind schedule, skip this component. The game is fully functional without buff pickups — they add depth but are not required for the core loop.
- Buff effects are intentionally simple: HEAL is instant, the others are flat multipliers with durations. No stacking, no complex interactions.
- The `buff_drop_chance` values in `EnemyConfig` (0.05 for Basic, 0.1 for Aggressive) mean buff drops are rare — roughly 1 in 20 Basic enemy kills, 1 in 10 Aggressive kills. This keeps them feeling special.
- Do NOT add currency fields to `GameState` in this component — that is Phase 4's responsibility. Buff tracking is handled entirely by `BuffManager`.
- The `buff_pickups` SpriteList in `EntityManager` does not need spatial hashing (few entities, dynamic positions).

---

#### Component: 3.8 — E2E Testing & Documentation

**Priority**: Must-have

**Estimated Effort**: 4-6 hours

**Owner**: AI Agent

**Dependencies**:
- All preceding Phase 3 components (3.1 through 3.7 if implemented, or 3.1 through 3.6 if 3.7 is skipped)

**Features**:
- Unit tests for enemy AI behaviour — AI Agent
- Unit tests for enemy spawning logic — AI Agent
- Unit tests for all new collision pairs — AI Agent
- Unit tests for difficulty scaling across 30 levels — AI Agent
- Unit tests for buff effects (if 3.7 implemented) — AI Agent
- Integration tests for full combat with enemies — AI Agent
- Coverage verification (30%+ on new modules) — AI Agent
- `implementation-context-phase-3.md` documentation — AI Agent

**Description**:
The final Phase 3 component writes comprehensive tests for all new functionality, runs coverage analysis, and produces implementation documentation. Tests focus on deterministic game logic (AI, spawning, collisions, difficulty parameters, buff effects) rather than rendering. The goal is 30%+ code coverage on all new Phase 3 modules and verification that the full combat experience works end-to-end.

**Acceptance Criteria**:
- [ ] Unit tests exist for `EnemyShip` AI (movement, targeting, firing, telegraph)
- [ ] Unit tests exist for `SpawnManager` enemy spawning (interval, cap, edge positioning, archetype selection)
- [ ] Unit tests exist for all three new collision pairs (player vs enemy projectiles, player projectiles vs enemies, player vs enemy ships)
- [ ] Unit tests exist for wrap-around ghost collisions on new pairs
- [ ] Unit tests exist for `DifficultyParams` interpolation across 30 levels
- [ ] Unit tests exist for damage feedback (invulnerability window, timer expiry)
- [ ] If component 3.7 was implemented: unit tests exist for buff pickup creation, collection, effect application, and expiry
- [ ] Integration test: simulate a multi-level combat session with enemies, verify no crashes
- [ ] `pytest --cov` shows 30%+ coverage on all new Phase 3 modules
- [ ] `implementation-context-phase-3.md` is created with summaries of all implemented components

**Technical Details**:
- **Files to Create**:
  - `void-breaker/tests/test_enemy_ship.py`
  - `void-breaker/tests/test_enemy_spawning.py`
  - `void-breaker/tests/test_enemy_collisions.py`
  - `void-breaker/tests/test_difficulty_scaling.py`
  - `void-breaker/tests/test_damage_effects.py`
  - `void-breaker/tests/test_buff_pickups.py` (if 3.7 implemented)
  - `docs/implementation-context-phase-3.md`
  - `docs/components/phase-3-component-3-8-overview.md`
- **Files to Modify**: None (test-only and documentation-only)
- **Key Functions/Classes**:
  - pytest fixtures: `enemy_basic`, `enemy_aggressive`, `spawn_manager`, `collision_system`, `difficulty_params`, `damage_effects`, `buff_manager`
  - Test functions following `test_<feature>_<scenario>` naming convention
- **Dependencies**: `pytest`, `pytest-cov`, all Phase 3 modules

**Detailed Implementation Requirements**:

- **File: `void-breaker/tests/test_enemy_ship.py`**: Test `EnemyShip` creation with both archetypes. Test `update_ai()` moves the enemy toward a known player position (verify distance decreases over multiple steps). Test `try_fire()` respects cooldown (call repeatedly, verify fire rate matches config). Test `try_fire()` respects spawn grace period (verify no fire in first 1.0 second). Test `take_damage()` reduces health correctly and returns True when destroyed. Test BASIC targeting accuracy (aim at current player position +/- accuracy scatter). Test AGGRESSIVE targeting leads the player (with a moving player position, verify the aim point is ahead of the player). Test telegraph state machine transitions (idle -> telegraphing -> fire -> cooldown -> idle cycle).

- **File: `void-breaker/tests/test_enemy_spawning.py`**: Test `SpawnManager.update_enemy_spawning()` returns empty list when disabled. Test enemies spawn after the configured interval. Test enemy count cap is enforced. Test `_get_spawn_edge_position()` produces positions just off-screen on all four edges. Test `_select_archetype()` produces expected distribution over many iterations (chi-squared or simple ratio check). Test `reset_enemy_spawning()` resets the timer.

- **File: `void-breaker/tests/test_enemy_collisions.py`**: Create test fixtures with positioned sprites. Test player-vs-enemy-projectile collision detects overlap. Test player-projectile-vs-enemy collision detects overlap. Test player-vs-enemy collision detects overlap. Test all three pairs at screen edges using the ghost sprite approach — place entities near edges and verify collision detection works across the wrap boundary. Test that collisions produce the correct results (damage applied, entities removed as expected).

- **File: `void-breaker/tests/test_difficulty_scaling.py`**: Test `get_difficulty_params()` for levels 1, 5, 10, 15, 20, 25, 30. Verify exact values at tier breakpoints. Test interpolation between tiers (level 7 should be between level-5 and level-10 values). Test level > 30 returns level-30 values. Test monotonicity of key parameters across all levels (asteroid_count non-decreasing, enemy_count_max non-decreasing). Test enemy_spawn_enabled transition (False for levels 1-5, True for 6+). Test all values are within sane ranges.

- **File: `void-breaker/tests/test_damage_effects.py`**: Test invulnerability prevents damage. Test invulnerability timer expires after configured duration. Test explosion particle creation (correct count). Test particle lifetime expiry.

- **File: `void-breaker/tests/test_buff_pickups.py`** (if 3.7 implemented): Test `BuffPickup` creation per type. Test lifetime expiry. Test `BuffManager.apply_buff()` for HEAL (shields increase, capped at max). Test DAMAGE_BOOST application and expiry (stat modified, then restored). Test SPEED_BOOST application and expiry. Test same-type buff refresh (duration reset, not stacked). Test `clear_all()` removes all buffs.

- **File: `docs/implementation-context-phase-3.md`**: Create a structured document with one section per implemented component (max 100 lines per component, max ~700 lines total). Each section includes: component ID and name, what was built, key files created/modified, key design decisions, patterns established, and any gotchas for future phases. Include a summary section at the top listing all components and their status. Note any deviations from the component breakdown specifications.

**Test Requirements**:
- [ ] All test files pass with `pytest -q`
- [ ] `pytest --cov=void-breaker/app/src --cov-report=term-missing` shows 30%+ coverage on all new Phase 3 modules
- [ ] No test requires a live Arcade window (all tests use mock/fixture-based entity creation)
- [ ] `docs/implementation-context-phase-3.md` exists and is complete

**Definition of Done**:
- [ ] All test files created and passing
- [ ] Coverage target met (30%+ on new modules)
- [ ] `docs/implementation-context-phase-3.md` created with all component summaries
- [ ] `docs/components/phase-3-component-3-8-overview.md` created
- [ ] `black --check` and `isort --check-only` pass on test files
- [ ] `scripts/evals.py` passes (no TODO/FIXME in delivered code)
- [ ] Full test suite (including Phase 1 and Phase 2 tests) still passes — no regressions
- [ ] Core application is still working post component implementation

**Notes**:
- Tests should NOT require an Arcade window or OpenGL context. Create entity instances directly by setting position, velocity, and other attributes without loading textures. Use `arcade.Sprite()` with no texture or a mock texture for collision testing.
- If `arcade.Sprite()` requires a texture for collision bounds, use `arcade.make_soft_square_texture()` to create a simple test texture programmatically.
- The integration test ("simulate a multi-level combat session") can be a simplified version that creates entities, runs update loops, and verifies no exceptions — it does not need to render anything.
- Prioritise test coverage on the most complex logic: enemy AI targeting, spawn manager timing, collision edge cases, and difficulty interpolation. Simple getters/setters do not need dedicated tests.

---

## File Ownership Summary

This table lists every file Phase 3 creates or modifies and which components touch it. Components sharing files cannot be fully parallelised.

| File | Created/Modified | Components | Serialisation Notes |
|------|-----------------|------------|---------------------|
| `void-breaker/assets/sprites/enemy_basic.png` | Created | 3.1 | Human only |
| `void-breaker/assets/sprites/enemy_aggressive.png` | Created | 3.1 | Human only |
| `void-breaker/assets/sprites/projectile_enemy.png` | Created | 3.1 | Human only |
| `void-breaker/assets/sounds/enemy_fire.wav` | Created | 3.1 | Human only |
| `void-breaker/assets/sounds/enemy_explode.wav` | Created | 3.1 | Human only |
| `void-breaker/assets/sounds/player_hit.wav` | Created | 3.1 | Human only |
| `void-breaker/app/src/entities/enemy_ship.py` | Created | 3.2 | No conflict |
| `void-breaker/app/src/config/enemy_config.py` | Created | 3.2 | No conflict |
| `void-breaker/app/src/managers/entity_manager.py` | Modified | 3.3, 3.7 | Phase 2 origin. 3.3 adds enemies + enemy_projectiles. 3.7 adds buff_pickups. Sequence: 3.3 before 3.7. |
| `void-breaker/app/src/physics/collisions.py` | Modified | 3.3, 3.7 | Phase 2 origin. 3.3 adds 3 collision pairs. 3.7 adds 1 collision pair. Sequence: 3.3 before 3.7. |
| `void-breaker/app/src/states/combat.py` | Modified | 3.3, 3.4, 3.5, 3.7 | Phase 2 origin. Most-modified file. Sequence: 3.3 -> 3.4 -> 3.5 -> 3.7. |
| `void-breaker/app/src/entities/projectile.py` | Modified (minor) | 3.3 | Phase 2 origin. Ensure ENEMY owner value exists. |
| `void-breaker/app/src/managers/spawn_manager.py` | Modified | 3.4 | Phase 2 origin. Adds enemy spawning alongside asteroids. |
| `void-breaker/app/src/config/difficulty_tables.py` | Modified | 3.4, 3.6 | Phase 2 origin. 3.4 adds initial enemy values. 3.6 refines all values. Sequence: 3.4 before 3.6. |
| `void-breaker/app/src/config/game_config.py` | Modified | 3.4 | Phase 2 origin. Adds enemy fields to DifficultyParams. |
| `void-breaker/app/src/rendering/damage_effects.py` | Created | 3.5 | No conflict |
| `void-breaker/app/src/entities/player_ship.py` | Modified | 3.5, 3.7 | Phase 2 origin. 3.5 adds invulnerability. 3.7 adds buff stats. Sequence: 3.5 before 3.7. |
| `void-breaker/app/src/rendering/particle_system.py` | Modified/Created | 3.5 | May be created in Phase 2 or 3.5. |
| `void-breaker/app/src/entities/buff_pickup.py` | Created | 3.7 | No conflict (optional component) |
| `void-breaker/app/src/managers/buff_manager.py` | Created | 3.7 | No conflict (optional component) |
| `void-breaker/tests/test_enemy_ship.py` | Created | 3.8 | No conflict |
| `void-breaker/tests/test_enemy_spawning.py` | Created | 3.8 | No conflict |
| `void-breaker/tests/test_enemy_collisions.py` | Created | 3.8 | No conflict |
| `void-breaker/tests/test_difficulty_scaling.py` | Created | 3.8 | No conflict |
| `void-breaker/tests/test_damage_effects.py` | Created | 3.8 | No conflict |
| `void-breaker/tests/test_buff_pickups.py` | Created | 3.8 | No conflict (if 3.7 implemented) |
| `docs/implementation-context-phase-3.md` | Created | 3.8 | No conflict |
| `docs/components/phase-3-component-3-2-overview.md` | Created | 3.2 | No conflict |
| `docs/components/phase-3-component-3-3-overview.md` | Created | 3.3 | No conflict |
| `docs/components/phase-3-component-3-4-overview.md` | Created | 3.4 | No conflict |
| `docs/components/phase-3-component-3-5-overview.md` | Created | 3.5 | No conflict |
| `docs/components/phase-3-component-3-6-overview.md` | Created | 3.6 | No conflict |
| `docs/components/phase-3-component-3-7-overview.md` | Created | 3.7 | No conflict (optional) |
| `docs/components/phase-3-component-3-8-overview.md` | Created | 3.8 | No conflict |

---

## Recommended Execution Order

Given serialisation constraints, the recommended sequential execution order is:

1. **3.1** (Human) — assets
2. **3.2** (AI Agent) — enemy entity + AI (new files only, no conflicts)
3. **3.3** (AI Agent) — enemy projectiles + collisions (modifies Phase 2 files)
4. **3.4** (AI Agent) — spawn manager + waves (modifies Phase 2 files, also touches combat.py after 3.3)
5. **3.5** (AI Agent) — damage feedback (modifies combat.py after 3.3 and 3.4, modifies player_ship.py)
6. **3.6** (AI Agent) — difficulty balance (refines difficulty_tables.py after 3.4)
7. **3.7** (AI Agent, optional) — buff pickups (modifies entity_manager, collisions, combat, player_ship after 3.3 and 3.5)
8. **3.8** (AI Agent) — testing + documentation (last, after everything else)

**Limited parallelisation**: 3.5 and 3.6 can potentially run in parallel after 3.4 completes, as they modify different files (3.5 modifies `damage_effects.py`, `player_ship.py`, `combat.py`; 3.6 modifies only `difficulty_tables.py`). However, both modify `combat.py` indirectly — 3.5 adds damage effect calls to combat.py. If an agent orchestrator can handle merges, these two are parallelisable; otherwise, sequence them.

---

## Cross-Phase Dependencies — Explicit Contracts

### Phase 2 -> Phase 3 (What We Extend)

| Phase 2 Module | What Phase 3 Does | Constraint |
|----------------|-------------------|-----------|
| `managers/entity_manager.py` | Adds `enemies`, `enemy_projectiles`, `buff_pickups` SpriteLists | Phase 2 must be complete |
| `physics/collisions.py` | Adds 3-4 new collision check methods | Phase 2 must be complete |
| `managers/spawn_manager.py` | Adds enemy spawning alongside asteroid spawning | Phase 2 must be complete |
| `config/game_config.py` | Adds enemy fields to `DifficultyParams` dataclass | Phase 2 must be complete |
| `config/difficulty_tables.py` | Adds enemy parameters, refines all values for 30 levels | Phase 2 must be complete |
| `states/combat.py` | Adds enemy update, spawn, collision, damage, buff calls to update loop | Phase 2 must be complete |
| `entities/player_ship.py` | Adds invulnerability state, buff stat modifiers | Phase 2 must be complete |

### Phase 3 -> Phase 4 (What We Provide)

| Phase 3 Output | Phase 4 Usage |
|----------------|---------------|
| `DifficultyParams` with enemy fields | Phase 4 may reference currency drop rates for economy balancing |
| `GameState` (unmodified by Phase 3) | Phase 4 extends with currency accumulation — Phase 3 intentionally does NOT add currency fields to GameState |
| Complete combat loop (enemies + asteroids) | Phase 4 uses full combat as the input for economy validation |
| `EnemyShip.on_destroyed()` drop logic | Phase 4's economy depends on enemy kill rewards being consistent |
| `BuffManager` (if implemented) | Phase 4 may integrate buff effects with shop upgrade interactions |

### What Phase 3 Does NOT Touch

- `GameState` currency fields — left to Phase 2/4
- Shop phase — Phase 4
- Insurance system — Phase 4
- Upgrade manager — Phase 4
- Persistence layer — no changes needed
- Audio manager internals — only calls `play()`, does not modify

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-20 | Tech Lead (Phase 3) | Initial Phase 3 component breakdown |
