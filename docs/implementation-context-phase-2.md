# Phase 2 Implementation Context

## Component 2.1 — Human Setup & Asset Preparation
- **Status**: Completed
- **What was built**: All placeholder visual and audio assets required for Phase 2 gameplay. Sprites are simple geometric shapes (triangle ship, irregular-polygon asteroids, dot projectile, diamond currency pickup, dot explosion particle) generated via a Pillow script. Sound stubs were provided as real `.wav` files by the developer.
- **Key files created**:
  - `assets/sprites/ship.png` — 32×32 white triangle pointing upward (RGBA)
  - `assets/sprites/asteroid_large.png` — 68×68 irregular grey circle (RGBA)
  - `assets/sprites/asteroid_medium.png` — 44×44 irregular grey circle (RGBA)
  - `assets/sprites/asteroid_small.png` — 24×24 irregular grey circle (RGBA)
  - `assets/sprites/projectile_player.png` — 8×8 cyan dot (RGBA)
  - `assets/sprites/currency_pickup.png` — 16×16 gold diamond (RGBA)
  - `assets/sprites/explosion_particle.png` — 6×6 orange-white dot (RGBA)
  - `scripts/generate_placeholder_sprites.py` — Pillow-based sprite generator
  - `scripts/verify_assets.py` — automated asset verification script
- **Sound files present** (provided by developer):
  - `assets/sounds/fire.wav`, `explode_small.wav`, `explode_medium.wav`, `explode_large.wav`, `hit.wav`, `pickup_currency.wav`, `level_clear.wav`, `game_over.wav`, `player_hit.wav`
- **Design decisions**: Used Pillow script generation rather than manual image editing for reproducibility and ease of regeneration. Ship sprite points upward (90° in Arcade coords) per solution design thrust calculation convention. Asteroids use seeded randomized polygon vertices for irregular edges. All sprites include small padding for visual clarity.
- **Deviations**: Asteroid sprite sizes include 4px padding (68/44/24 instead of exact 64/40/20) for drawing margin — functionally equivalent since Arcade uses sprite `width`/`height` properties that match the image dimensions. Developer's `.wav` files are stereo/varying formats rather than strictly mono 16-bit PCM, but Arcade handles all standard WAV formats.

## Component 2.2 — Player Ship Entity & Physics
- **Status**: Completed
- **What was built**: Implemented a production `PlayerShip` entity with inertial movement primitives (thrust, rotation, natural drag, brake drag, speed cap), shield tracking, and cooldown ticking. Added a shared wrap-around utility and a thin `PhysicsEngine` that reads held actions from `InputManager` and applies fixed-step simulation updates.
- **Key files created**:
  - `app/src/entities/player_ship.py` — ship entity implementation with explicit `velocity_x`/`velocity_y`
  - `app/src/physics/wrap.py` — `wrap_entity()` single source of truth for screen-edge wrapping
  - `app/src/physics/engine.py` — per-tick orchestration for ship movement + wrapping
  - `tests/test_player_ship_physics.py` — focused unit tests for all core physics requirements
- **Key files modified**:
  - `app/src/entities/__init__.py` — exports `PlayerShip`
  - `app/src/physics/__init__.py` — exports `PhysicsEngine` and `wrap_entity`
  - `app/src/config/game_config.py` — added `PhysicsConfig` and singleton `PHYSICS_CONFIG`
  - `app/src/states/combat.py` — replaced stub-only behavior with active ship spawn/update/draw integration while preserving existing transition shortcuts
- **Design decisions**:
  - Kept movement state explicit on the entity (`velocity_x`/`velocity_y`) instead of `change_x`/`change_y` to avoid conflicts with Arcade physics helpers and to keep tests deterministic.
  - Added a dedicated `PhysicsConfig` dataclass for gameplay physics constants without forcing unrelated Phase 1 config migrations.
  - Wired physics through `PhysicsEngine` now (ship-only) to provide an extension point for asteroid/projectile integration in components 2.3 and 2.4.
- **Validation executed**:
  - `pytest -q tests/test_player_ship_physics.py` (7 passed)
  - `pytest -q` (48 passed)
  - `black --check app/src` and `isort --check-only app/src` (pass after formatting `physics/engine.py`)
  - `python scripts/evals.py` (pass)
- **Deviations**:
  - `PhysicsConfig` uses the component-spec defaults (`base_fire_rate=5.0`, `base_projectile_range=600.0`) while existing `GameConfig` ship defaults remain unchanged for backward compatibility with prior phase assumptions. Future components can migrate remaining consumers to `PhysicsConfig`.
