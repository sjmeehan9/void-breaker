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
