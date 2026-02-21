# Solution Design: Retro Space Shooter (Asterax Tribute)

Version: 1.1
Date: 2026-02-18
Status: Final
Owner: Solutions Architect

---

## Overview

The Asterax Tribute is a single-player, offline, 2D arcade space shooter built with **Python 3.13+** and the **Arcade library (3.x)**. The application is structured as a finite state machine driving a fixed-timestep game loop with GPU-accelerated sprite rendering. The core architecture consists of six subsystems: a state machine controlling game phases (menu, combat, shop, game-over), an entity-component system managing ships/asteroids/enemies/projectiles/pickups, an inertial physics engine with wrap-around collision detection, a shop phase renderer with spatial node interaction, a persistence layer for high scores and settings (JSON files), and an audio manager for sound effect playback. The game targets macOS first, packaged as a standalone `.app` bundle via PyInstaller, with cross-platform portability preserved by the choice of Arcade (OpenGL + pyglet).

---

## Architecture

### System Architecture

The application follows a layered architecture with clear separation between game logic, rendering, and I/O:

```
+---------------------------------------------------------------+
|                        Application Shell                       |
|  (Window creation, event loop, fixed-timestep game loop)       |
+---------------------------------------------------------------+
|                        State Machine                           |
|  MainMenu | GameInit | CombatPhase | ShopPhase | GameOver |   |
|  Pause (overlay) | HowToPlay | HighScores | Settings          |
+---------------------------------------------------------------+
|                     Game Logic Layer                           |
|  EntityManager | PhysicsEngine | CollisionSystem |             |
|  DifficultyScaler | ScoreManager | UpgradeManager |            |
|  InsuranceManager | CurrencyManager | SpawnManager             |
+---------------------------------------------------------------+
|                     Rendering Layer                            |
|  SpriteRenderer | ParticleSystem | HUDRenderer |               |
|  ShopNodeRenderer | MenuRenderer | TransitionEffects           |
+---------------------------------------------------------------+
|                        I/O Layer                               |
|  InputManager (keyboard) | AudioManager | PersistenceManager   |
+---------------------------------------------------------------+
|                     Platform Layer                             |
|  Arcade/pyglet (OpenGL) | macOS filesystem | OpenAL audio      |
+---------------------------------------------------------------+
```

### Key Components

1. **Application Shell** (`app.py`): Creates the Arcade `Window`, initialises subsystems, and runs the main loop. Delegates all behaviour to the active state.

2. **State Machine** (`states/`): Each game state is a class implementing `on_enter()`, `on_exit()`, `on_update(delta_time)`, `on_draw()`, and `on_key_press()`/`on_key_release()`. The state machine manages transitions and maintains a state stack for overlays (pause, settings).

3. **Entity Manager** (`entities/`): Manages all game entities (ship, asteroids, enemies, projectiles, pickups, shop nodes) via typed `SpriteList` collections. Each entity type is a subclass of `arcade.Sprite` with domain-specific behaviour methods.

4. **Physics Engine** (`physics/`): Applies inertial forces (thrust, drag), updates velocities and positions, and enforces wrap-around boundary conditions. Runs at fixed timestep independent of frame rate.

5. **Collision System** (`physics/collisions.py`): Uses Arcade's built-in spatial-hashing collision detection for sprite-vs-sprite-list checks. Dispatches collision events to handlers (damage, pickup collection, shop purchase).

6. **Rendering Layer**: Leverages Arcade's GPU-accelerated `SpriteList.draw()` for entities and a custom particle system for explosions, thrust trails, and visual feedback effects.

7. **Persistence Manager** (`persistence/`): Reads/writes JSON files for high scores and settings. Located in a platform-appropriate user data directory (`~/Library/Application Support/VoidBreaker/` on macOS).

8. **Audio Manager** (`audio/`): Wraps Arcade's sound API (pyglet/OpenAL backend on macOS). Pre-loads sound effects at startup and exposes methods like `play_fire()`, `play_explosion(size)`, `play_pickup()`.

### Data Flow

```
Keyboard Input
      |
      v
InputManager --> Active State --> Game Logic (entities, physics, collisions)
                                       |
                                       v
                              State Transitions / Entity Updates
                                       |
                                       v
                              Rendering (SpriteLists, particles, HUD)
                                       |
                                       v
                              Arcade Window (OpenGL draw)
```

### State Machine Diagram

```
                    +-------------+
                    |  APP START  |
                    +------+------+
                           |
                           v
                    +------+------+
             +----->|  MAIN MENU  |<--------------------+
             |      +------+------+                     |
             |             |                            |
             |    +--------+--------+--------+          |
             |    v        v        v        v          |
             | HowToPlay Settings HighScores Quit       |
             |    |        |        |         |         |
             |    +--------+--------+         |         |
             |             |              [exit app]    |
             |             v                            |
             |      +------+------+                     |
             |      |  GAME INIT  |                     |
             |      +------+------+                     |
             |             |                            |
             |             v                            |
             |      +------+------+                     |
             |  +-->| COMBAT PHASE|--[shields=0]--+     |
             |  |   +------+------+               |     |
             |  |          |                      v     |
             |  |   [level cleared]        +------+---+ |
             |  |          |               | GAME OVER|-+
             |  |          v               +----------+
             |  |   +------+------+
             |  +---| SHOP PHASE  |
             |      +-------------+
             |
             +--- [exit to menu from Pause]

        PAUSE overlay can activate from COMBAT or SHOP
```

---

## Technology Stack

### Primary Choice: Python 3.13+ with Arcade Library 3.x

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.13+ |
| Game Framework | Arcade | 3.3.x |
| Rendering Backend | OpenGL (via pyglet) | 2.x |
| Audio Backend | OpenAL (via pyglet) | System |
| Packaging | PyInstaller | 6.x |
| Testing | pytest | 8.x |
| Formatting | Black + isort | per copilot.instructions.md |
| Type Checking | mypy (strict) | 1.x |

### Rationale

**Why Arcade over Pygame-CE:**

1. **GPU-accelerated rendering**: Arcade uses OpenGL via pyglet, offloading sprite drawing, rotation, and transparency to the GPU. This delivers 2-3x better performance for sprite-heavy scenes compared to Pygame's CPU-bound surface blitting. Critical for late-game scenarios with 50+ asteroids, multiple enemies, dozens of projectiles, and particle effects simultaneously.

2. **Built-in spatial hashing**: Arcade provides `use_spatial_hash=True` on `SpriteList`, which dramatically speeds collision detection for static or semi-static sprite groups (asteroids, shop nodes). Pygame requires implementing quadtrees or grids manually.

3. **Built-in game loop structure**: Arcade's `Window` class provides `on_update(delta_time)` and `on_draw()` separation, plus built-in keyboard event handling. Pygame requires manual event loop, clock management, and draw orchestration.

4. **Sound API**: Arcade wraps pyglet's audio with a simple `arcade.load_sound()` / `arcade.play_sound()` interface. OpenAL backend works natively on macOS.

5. **macOS packaging**: Arcade + PyInstaller produces standalone macOS `.app` bundles with full support since Arcade 2.6+.

6. **Cross-platform portability**: Arcade runs on macOS, Windows, and Linux without code changes. The same codebase can be packaged for all three platforms.

7. **Modern Python**: Arcade 3.x targets Python 3.8+ and works well with 3.13. Supports type hints, dataclasses, and modern Python idioms that align with copilot.instructions.md standards.

**Why not Pygame-CE:**

- CPU-bound rendering limits entity counts during intense late-game combat.
- No built-in spatial partitioning for collision detection.
- Requires more boilerplate for window management, event handling, and draw loops.
- Particle effects require manual implementation with CPU blitting, limiting visual fidelity at 60fps.

**Why not Godot with Python bindings:**

- Python support in Godot is via third-party bindings (godot-python), not first-class. GDScript is the primary language.
- Introduces a full game engine with its own editor, scene system, and build pipeline — heavyweight for a 2D arcade shooter.
- Mixing Python with GDScript/C++ complicates the development workflow and contradicts the copilot.instructions.md single-language standards.
- Packaging and distribution is via Godot's export system, not standard Python tooling.

**Why not a non-Python option (e.g., Bevy/Rust, Love2D/Lua):**

- copilot.instructions.md specifies Python 3.13+ or TypeScript/Node.js 24+ as the language options. Rust and Lua are outside the permitted stack.
- Python with Arcade satisfies all requirements (60fps, keyboard input, local I/O, macOS packaging) without needing to leave the Python ecosystem.

---

## Data Model

### Game State

```python
@dataclass
class GameState:
    """Top-level mutable state for a single run."""
    current_level: int                  # 1-indexed
    score: int
    currency: int
    shields: float                      # 0.0 to max_shields
    max_shields: float
    is_paused: bool
    phase: GamePhase                    # COMBAT | SHOP | GAME_OVER
    level_stats: LevelStats             # stats for current level
    run_stats: RunStats                 # cumulative stats for run summary
```

### Player Ship State

```python
@dataclass
class ShipState:
    """Ship physics and upgrade state."""
    # Physics
    position: tuple[float, float]
    velocity: tuple[float, float]
    angle: float                        # degrees, 0 = up
    angular_velocity: float

    # Base stats (before upgrades)
    base_thrust: float
    base_turn_rate: float
    base_fire_rate: float               # shots per second
    base_projectile_speed: float
    base_projectile_range: float
    base_damage: float

    # Upgrade levels (0 = no upgrade purchased)
    weapon_fire_rate_level: int
    weapon_damage_level: int
    weapon_speed_level: int
    weapon_spread_level: int
    defense_shields_level: int
    mobility_thrust_level: int
    mobility_turn_level: int
    economy_magnet_level: int
    economy_protection_level: int       # currency can't be destroyed

    # Computed effective stats (recalculated when upgrades change)
    effective_thrust: float
    effective_turn_rate: float
    effective_fire_rate: float
    effective_projectile_speed: float
    effective_projectile_range: float
    effective_damage: float
    effective_magnet_radius: float
```

### Upgrade Definition

```python
@dataclass
class UpgradeDefinition:
    """Static definition of a purchasable upgrade."""
    id: str                             # e.g. "weapon_fire_rate"
    category: UpgradeCategory           # WEAPON | DEFENSE | MOBILITY | ECONOMY | REPAIR
    name: str                           # display name
    description: str                    # short effect description
    max_level: int                      # maximum upgrade level
    base_cost: int                      # cost at level 1
    cost_scaling: float                 # multiplier per level
    effect_per_level: float             # stat increase per level
    stat_key: str                       # which ShipState field it modifies
```

### Insurance State

```python
@dataclass
class InsuranceState:
    """Insurance plan state within a run."""
    tier: InsuranceTier                 # OFF | BASIC | PREMIUM
    cost_per_level: int                 # currency deducted at each level transition
    retention_fraction: float           # 0.0 (OFF), 0.5 (BASIC), 1.0 (PREMIUM)
```

### Difficulty Parameters

```python
@dataclass
class DifficultyParams:
    """Parameters that scale per level."""
    asteroid_count: int                 # number of large asteroids at level start
    asteroid_speed_min: float
    asteroid_speed_max: float
    enemy_spawn_enabled: bool
    enemy_count_max: int
    enemy_spawn_interval: float         # seconds between spawns
    enemy_aggression: float             # 0.0 to 1.0, affects firing rate and accuracy
    currency_drop_chance: float         # probability per destroyed asteroid
    currency_value_base: int
```

### High Score Entry

```python
@dataclass
class HighScoreEntry:
    """A single high score record."""
    name: str                           # player initials/name (max 10 chars)
    score: int
    level_reached: int
    difficulty: str                     # "classic" | "casual" | "hard"
    enemies_destroyed: int
    currency_collected: int
    currency_spent: int
    date: str                           # ISO 8601 date string
```

### Settings Schema

```python
@dataclass
class GameSettings:
    """Persisted user settings."""
    # Audio
    master_volume: float                # 0.0 to 1.0
    music_volume: float
    sfx_volume: float

    # Controls
    key_rotate_left: int                # Arcade key constant
    key_rotate_right: int
    key_thrust: int
    key_fire: int
    key_brake: int
    key_special: int
    key_pause: int
    fire_mode: str                      # "hold" | "tap"
    autofire: bool

    # Visual
    colorblind_mode: bool
    screen_shake: str                   # "off" | "low" | "medium"

    # Gameplay
    difficulty: str                     # "casual" | "classic" | "hard"

    # Window
    fullscreen: bool
    resolution: tuple[int, int]
```

### Persistence File Formats

**High Scores** (`high_scores.json`):
```json
{
  "version": 1,
  "entries": [
    {
      "name": "ACE",
      "score": 142500,
      "level_reached": 23,
      "difficulty": "classic",
      "enemies_destroyed": 47,
      "currency_collected": 3200,
      "currency_spent": 2850,
      "date": "2026-02-18T14:30:00"
    }
  ]
}
```

**Settings** (`settings.json`):
```json
{
  "version": 1,
  "master_volume": 0.8,
  "music_volume": 0.5,
  "sfx_volume": 1.0,
  "key_bindings": {
    "rotate_left": "LEFT",
    "rotate_right": "RIGHT",
    "thrust": "UP",
    "fire": "SPACE",
    "brake": "DOWN",
    "special": "LSHIFT",
    "pause": "ESCAPE"
  },
  "fire_mode": "hold",
  "autofire": false,
  "colorblind_mode": false,
  "screen_shake": "medium",
  "difficulty": "classic",
  "fullscreen": false,
  "resolution": [1280, 960]
}
```

---

## Game Loop Design

### Fixed Timestep with Variable Rendering

The game uses a **fixed-timestep accumulator pattern** to decouple physics updates from rendering. This ensures deterministic physics regardless of frame rate variations.

```
TARGET_FPS = 60
PHYSICS_DT = 1.0 / 60.0  # 16.67ms fixed physics step
MAX_FRAME_TIME = 0.25     # cap to prevent spiral of death

def on_update(self, delta_time: float):
    if self.is_paused:
        return

    # Cap frame time to prevent physics explosion after lag
    frame_time = min(delta_time, MAX_FRAME_TIME)
    self.accumulator += frame_time

    while self.accumulator >= PHYSICS_DT:
        self.physics_step(PHYSICS_DT)
        self.accumulator -= PHYSICS_DT

def physics_step(self, dt: float):
    # 1. Process input state (already captured by key events)
    self.apply_input(dt)

    # 2. Update entity physics (thrust, velocity, position)
    self.physics_engine.update(dt)

    # 3. Enforce wrap-around boundaries
    self.wrap_entities()

    # 4. Run collision detection and dispatch events
    self.collision_system.check_all()

    # 5. Process collision results (damage, pickups, splits)
    self.process_collision_events()

    # 6. Update spawners (enemies, currency timeout)
    self.spawn_manager.update(dt)

    # 7. Update particles and effects
    self.particle_system.update(dt)

    # 8. Check win/loss conditions
    self.check_phase_transitions()

def on_draw(self):
    self.clear()
    # Draw in z-order: background, entities, particles, HUD
    self.draw_background()
    self.entity_manager.draw()
    self.particle_system.draw()
    self.hud.draw()
```

### Rendering Pipeline

1. **Clear** the frame buffer.
2. **Background**: Static starfield (pre-rendered to a texture for performance).
3. **Entities**: Draw each `SpriteList` in order — asteroids, pickups, enemy projectiles, enemies, player projectiles, player ship. Ordering ensures the ship is always visible on top.
4. **Particles**: Draw particle emitters (explosions, thrust trail, collection sparkle).
5. **HUD**: Draw UI elements (shields bar, score, level, currency) as overlay sprites/text.
6. **Transitions**: Fade effects between states.

### Input Handling

Input uses Arcade's event-driven key press/release system, tracked as a set of currently-held keys:

```python
def on_key_press(self, key: int, modifiers: int):
    self.keys_held.add(key)
    self.active_state.on_key_press(key, modifiers)

def on_key_release(self, key: int, modifiers: int):
    self.keys_held.discard(key)
    self.active_state.on_key_release(key, modifiers)
```

Each state reads `keys_held` during its update to apply continuous actions (thrust, rotation) and uses key press events for discrete actions (fire in tap mode, pause, menu navigation).

---

## Entity System

### Entity Hierarchy

All game entities extend `arcade.Sprite`, gaining position, angle, texture, scale, and collision support for free. Domain behaviour is added via composition and subclass methods.

```
arcade.Sprite
    |
    +-- PlayerShip
    |       Methods: apply_thrust(), apply_rotation(), fire(), take_damage(),
    |                collect_pickup(), apply_upgrade()
    |       Properties: velocity, shields, upgrade_state, fire_cooldown
    |
    +-- Asteroid
    |       Methods: split(), on_destroyed()
    |       Properties: size (LARGE|MEDIUM|SMALL), velocity, rotation_speed,
    |                   hit_points, point_value, currency_drop_chance
    |
    +-- EnemyShip
    |       Methods: update_ai(), fire(), take_damage(), on_destroyed()
    |       Properties: archetype (BASIC|AGGRESSIVE|SNIPER), velocity,
    |                   health, fire_cooldown, aggression, point_value
    |
    +-- Projectile
    |       Methods: update_lifetime()
    |       Properties: owner (PLAYER|ENEMY), velocity, damage, lifetime_remaining,
    |                   max_range
    |
    +-- CurrencyPickup
    |       Methods: update_lifetime(), attract_to(position, radius)
    |       Properties: value, lifetime_remaining, is_destructible
    |
    +-- BuffPickup
    |       Properties: buff_type (HEAL|SHIELD|DAMAGE_BOOST|SPEED_BOOST),
    |                   duration, magnitude
    |
    +-- ShopNode
            Methods: on_purchased(), can_afford(currency)
            Properties: upgrade_definition, cost, is_purchased, label_text
```

### Entity Management

Entities are grouped into typed `SpriteList` collections for efficient batch rendering and collision queries:

```python
class EntityManager:
    def __init__(self):
        self.player: PlayerShip | None = None
        self.asteroids = arcade.SpriteList(use_spatial_hash=True)
        self.enemies = arcade.SpriteList()
        self.player_projectiles = arcade.SpriteList()
        self.enemy_projectiles = arcade.SpriteList()
        self.currency_pickups = arcade.SpriteList()
        self.buff_pickups = arcade.SpriteList()
        self.shop_nodes = arcade.SpriteList(use_spatial_hash=True)
        self.particles = arcade.SpriteList()
```

Spatial hashing is enabled for asteroids (many entities, checked frequently for collisions) and shop nodes (static positions, checked against player movement). Dynamic entities (projectiles, enemies) use linear collision checks since their positions change every frame.

### Entity Lifecycle

1. **Spawn**: Entity created, configured, and added to appropriate `SpriteList`.
2. **Update**: Entity-specific logic runs each physics step (AI, lifetime countdown, magnet attraction).
3. **Collision**: Collision system detects overlaps and dispatches events.
4. **Destroy**: Entity removed from its `SpriteList`, particle effect spawned, score/currency awarded.

---

## Physics and Collision

### Inertial Physics Model

The ship uses Newtonian-style 2D physics with damping to achieve the classic Asteroids feel:

```python
# Per physics step (dt = 1/60):

# Rotation
if rotating_left:
    ship.angle += ship.effective_turn_rate * dt
if rotating_right:
    ship.angle -= ship.effective_turn_rate * dt

# Thrust (applied as force in facing direction)
if thrusting:
    thrust_x = math.cos(math.radians(ship.angle + 90)) * ship.effective_thrust
    thrust_y = math.sin(math.radians(ship.angle + 90)) * ship.effective_thrust
    ship.velocity_x += thrust_x * dt
    ship.velocity_y += thrust_y * dt

# Braking (optional retro-thrust or gentle drag increase)
if braking:
    ship.velocity_x *= (1.0 - BRAKE_DRAG * dt)
    ship.velocity_y *= (1.0 - BRAKE_DRAG * dt)

# Natural drag (very slight, preserves inertial feel)
ship.velocity_x *= (1.0 - NATURAL_DRAG * dt)
ship.velocity_y *= (1.0 - NATURAL_DRAG * dt)

# Speed cap (prevents infinite acceleration)
speed = math.hypot(ship.velocity_x, ship.velocity_y)
if speed > MAX_SHIP_SPEED:
    scale = MAX_SHIP_SPEED / speed
    ship.velocity_x *= scale
    ship.velocity_y *= scale

# Position update
ship.center_x += ship.velocity_x * dt
ship.center_y += ship.velocity_y * dt
```

Key tuning parameters (exposed in a config dataclass for easy iteration):

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `NATURAL_DRAG` | 0.3 | Slight deceleration to prevent eternal drift |
| `BRAKE_DRAG` | 3.0 | Active braking drag coefficient |
| `MAX_SHIP_SPEED` | 600.0 | Hard speed cap (pixels/second) |
| `BASE_THRUST` | 400.0 | Acceleration (pixels/second^2) |
| `BASE_TURN_RATE` | 240.0 | Rotation speed (degrees/second) |

These values are starting points; playtesting will refine them. The drag value is intentionally low to preserve the inertial/drifty feel that defines Asteroids-family games.

### Wrap-Around Boundary

All entities wrap at playfield edges:

```python
def wrap_entity(entity: arcade.Sprite, width: float, height: float):
    if entity.right < 0:
        entity.left = width
    elif entity.left > width:
        entity.right = 0
    if entity.top < 0:
        entity.bottom = height
    elif entity.bottom > height:
        entity.top = 0
```

For collision detection near edges, entities that are partially off-screen are rendered at both their actual position and their wrapped "ghost" position. This is handled by checking if an entity is within one sprite-width of an edge and, if so, temporarily creating a ghost sprite at the wrapped position for collision checks only.

### Collision Detection Strategy

Collision checks are performed using Arcade's `arcade.check_for_collision_with_list()` function, which uses axis-aligned bounding box (AABB) tests with optional spatial hashing:

| Check | Frequency | Method |
|-------|-----------|--------|
| Player vs Asteroids | Every step | Spatial hash lookup |
| Player vs Enemy Projectiles | Every step | Linear scan (few projectiles) |
| Player vs Currency Pickups | Every step | Linear scan + magnet radius |
| Player vs Buff Pickups | Every step | Linear scan (rare entities) |
| Player Projectiles vs Asteroids | Every step | Spatial hash lookup |
| Player Projectiles vs Enemies | Every step | Linear scan (few enemies) |
| Enemy Projectiles vs Asteroids | Optional | Disabled by default for performance |
| Player vs Shop Nodes | Shop phase only | Spatial hash lookup |

For wrap-around collision accuracy at screen edges, the ghost-sprite approach is used: before collision checks, any entity within one bounding-box width of an edge gets a temporary clone on the opposite side. These clones are removed after collision resolution.

### Collision Response

```python
# Asteroid hit by player projectile
def on_projectile_hits_asteroid(projectile: Projectile, asteroid: Asteroid):
    asteroid.hit_points -= projectile.damage
    projectile.kill()  # remove from SpriteList
    if asteroid.hit_points <= 0:
        spawn_explosion(asteroid.position, asteroid.size)
        award_score(asteroid.point_value)
        roll_currency_drop(asteroid)
        if asteroid.size != AsteroidSize.SMALL:
            spawn_child_asteroids(asteroid)
        asteroid.kill()

# Ship hit by asteroid or enemy projectile
def on_ship_takes_damage(ship: PlayerShip, damage: float):
    ship.shields -= damage
    spawn_damage_flash(ship)
    play_sound("hit")
    if ship.shields <= 0:
        ship.shields = 0
        trigger_game_over()
```

---

## Shop Phase Design

### Layout

The shop phase presents upgrade nodes as floating orbs arranged in a **circular layout** around the centre of the playfield. The player's ship starts at the centre and can fly freely within the playfield to reach nodes.

```
                    [Weapons: Fire Rate]
                  /                      \
     [Economy: Magnet]        [Weapons: Damage]
            |                        |
    [Repairs: Heal]    (ship)    [Defense: Shields]
            |                        |
     [Economy: Protect]       [Mobility: Thrust]
                  \                      /
                    [Insurance]

                      [CONTINUE -->]
```

### Node Interaction

1. Each `ShopNode` sprite displays its upgrade icon, name, cost, and current level.
2. When the player ship collides with a `ShopNode`:
   - If the player can afford the upgrade and it is not at max level: deduct currency, apply upgrade, play purchase sound, re-centre the ship with a brief invulnerability to prevent accidental double-purchases.
   - If the player cannot afford it or it is maxed: play a "denied" sound and bounce the ship back slightly.
3. The "Continue" node (or pressing a specific key) transitions to the next combat level.
4. Insurance nodes work identically but set the `InsuranceState` tier and deduct the recurring cost.

### Shop Node Rendering

Each node renders as:
- A coloured orb sprite matching its category (red = weapons, blue = defense, green = mobility, gold = economy, white = repairs, purple = insurance).
- A text label below showing the upgrade name, level (e.g., "Lv 2/5"), and cost.
- A visual indicator (dimmed, crossed out) if the player cannot afford it or it is maxed.
- A pulsing highlight on affordable upgrades to guide attention.

### Ship Re-centring

After a purchase, the ship is smoothly interpolated back to the centre over 0.3 seconds. During this interpolation, the ship cannot collide with other nodes (brief invulnerability window). This prevents accidental multi-purchases when nodes are close together.

---

## Persistence

### Storage Location

Files are stored in the platform-appropriate application data directory:

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/VoidBreaker/` |
| Windows (future) | `%APPDATA%/VoidBreaker/` |
| Linux (future) | `~/.local/share/VoidBreaker/` |

The path is resolved using Python's `platformdirs` library (or `pathlib` with platform detection as a fallback).

### File Format: JSON

JSON is chosen over SQLite for simplicity:

- Only two small files need persistence (high scores and settings).
- No concurrent access — single player, single process.
- Human-readable for debugging.
- No additional dependency (Python's `json` module is stdlib).

### File Operations

- **Load**: On application startup. If a file does not exist or is corrupt, fall back to defaults and log a warning.
- **Save settings**: On any settings change (immediate write).
- **Save high scores**: After a qualifying game over (atomic write using `tempfile` + `os.replace` to prevent corruption).

### Schema Versioning

Each file includes a `"version"` field. When loading, the application checks the version and applies migration logic if the schema has changed between releases. Unknown/future versions trigger a fallback to defaults with a user-visible warning.

---

## Audio Architecture

### Sound Engine

Audio uses Arcade's built-in sound API, which delegates to pyglet's media module. On macOS, pyglet uses the **OpenAL** backend (system-provided).

### Sound Effect Catalogue

| Event | File | Notes |
|-------|------|-------|
| Player fire | `fire.wav` | Short, punchy. 16-bit PCM mono. |
| Player hit/damage | `hit.wav` | Sharp impact sound. |
| Asteroid explosion (small) | `explode_small.wav` | Quick pop. |
| Asteroid explosion (medium) | `explode_medium.wav` | Mid-range boom. |
| Asteroid explosion (large) | `explode_large.wav` | Deep boom. |
| Enemy explosion | `enemy_explode.wav` | Distinct from asteroid explosions. |
| Currency pickup | `pickup_currency.wav` | Bright, satisfying chime. |
| Buff pickup | `pickup_buff.wav` | Power-up sound. |
| Shop purchase | `shop_purchase.wav` | Cash register or confirm tone. |
| Shop denied | `shop_denied.wav` | Soft buzz or error tone. |
| Level clear | `level_clear.wav` | Fanfare or ascending tone. |
| Game over | `game_over.wav` | Descending tone. |
| Menu navigate | `menu_nav.wav` | Subtle click. |
| Menu select | `menu_select.wav` | Confirm tone. |

### Audio Manager Implementation

```python
class AudioManager:
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.sounds: dict[str, arcade.Sound] = {}
        self._load_all_sounds()

    def _load_all_sounds(self):
        sound_dir = ASSET_PATH / "sounds"
        for sound_file in sound_dir.glob("*.wav"):
            self.sounds[sound_file.stem] = arcade.load_sound(sound_file)

    def play(self, name: str, volume_override: float | None = None):
        if name not in self.sounds:
            return
        volume = volume_override or self.settings.sfx_volume
        effective_volume = volume * self.settings.master_volume
        arcade.play_sound(self.sounds[name], volume=effective_volume)
```

### Audio File Format

All sound effects are stored as **16-bit PCM mono WAV files**. This format is universally supported by OpenAL on macOS and avoids codec issues. Files are kept small (under 500KB each) for fast loading.

### Music (Optional)

If background music is included, it uses Arcade's streaming playback (`arcade.load_sound()` with `streaming=True` for long files). Music is a separate volume channel and can be toggled independently.

---

## Infrastructure and Deployment

### macOS Packaging

The application is packaged as a standalone macOS `.app` bundle using **PyInstaller**:

```
VoidBreaker.app/
  Contents/
    MacOS/
      VoidBreaker           # PyInstaller bootstrap executable
    Resources/
      icon.icns             # Application icon
    Frameworks/
      ... (bundled Python, pyglet, OpenGL support)
    _internal/
      assets/               # Game assets (sprites, sounds)
      ... (Python packages)
    Info.plist              # macOS application metadata
```

### Build Process

```bash
# Build command (from project root)
pyinstaller \
  --name VoidBreaker \
  --windowed \
  --onedir \
  --icon assets/icon.icns \
  --add-data "assets:assets" \
  VoidBreaker.spec
```

A `VoidBreaker.spec` file is maintained in the repository with all PyInstaller configuration, including:
- Hidden imports for Arcade/pyglet modules.
- Data file mappings for all assets.
- macOS-specific `Info.plist` entries (bundle identifier, version, minimum OS version).

### Distribution

For v1.0, distribution is via a **DMG disk image** containing `VoidBreaker.app` and an alias to `/Applications`. No code signing or notarisation is required for initial local distribution, but the README documents the steps for future App Store or notarised distribution.

### Development Environment

```
asterax-tribute/
  void-breaker/
    app/
      src/
        __init__.py
        main.py               # Entry point
        window.py             # Arcade Window setup
        states/               # Game state classes
          __init__.py
          main_menu.py
          combat.py
          shop.py
          game_over.py
          pause.py
          how_to_play.py
          high_scores.py
          settings_screen.py
        entities/             # Entity classes
          __init__.py
          player_ship.py
          asteroid.py
          enemy_ship.py
          projectile.py
          pickups.py
          shop_node.py
        physics/              # Physics and collision
          __init__.py
          engine.py
          collisions.py
          wrap.py
        managers/             # Game subsystem managers
          __init__.py
          entity_manager.py
          spawn_manager.py
          score_manager.py
          upgrade_manager.py
          currency_manager.py
          insurance_manager.py
          difficulty_scaler.py
        audio/
          __init__.py
          audio_manager.py
        persistence/
          __init__.py
          persistence_manager.py
          schemas.py
        rendering/
          __init__.py
          hud.py
          particle_system.py
          transitions.py
          menu_renderer.py
        input/
          __init__.py
          input_manager.py
        config/
          __init__.py
          game_config.py      # All tuning parameters
          upgrade_definitions.py
          difficulty_tables.py
      config/
        settings_defaults.yaml
      docs/
    assets/
      sprites/
      sounds/
      fonts/
    scripts/
      evals.py
    tests/
      __init__.py
      test_physics.py
      test_collisions.py
      test_entities.py
      test_upgrades.py
      test_persistence.py
      test_difficulty.py
      test_scoring.py
      test_insurance.py
  pyproject.toml
```

---

## Security Design

As an offline, single-player game with no network access, the attack surface is minimal. Considerations:

1. **Local file integrity**: High score and settings files are stored in the user's home directory. No sensitive data is stored. Files use JSON with schema validation on load; malformed files are replaced with defaults rather than crashing.

2. **No network access**: The application makes zero network calls. No sockets, no HTTP, no DNS. This is enforced by simply not importing any networking libraries.

3. **Asset loading**: All assets are loaded from the bundled application directory. File paths are constructed using `pathlib` with no user-supplied path components, preventing path traversal.

4. **No code execution**: The application does not evaluate user-supplied code, scripts, or expressions. Settings and high scores are deserialised from JSON using `json.load()` (safe by default — no `eval()` or `pickle`).

---

## Scalability and Performance

### Entity Count Targets

| Entity Type | Typical Count | Maximum Count | Notes |
|-------------|--------------|---------------|-------|
| Player ship | 1 | 1 | Always present during gameplay |
| Asteroids | 10-60 | 100 | Splitting creates more; level scaling increases count |
| Enemies | 0-5 | 10 | Spawned on timer, capped per level |
| Player projectiles | 0-8 | 15 | Capped by fire rate and lifetime |
| Enemy projectiles | 0-10 | 20 | Capped by enemy count and fire rate |
| Currency pickups | 0-20 | 40 | Timeout removes old ones |
| Buff pickups | 0-2 | 5 | Rare spawns |
| Particles | 0-100 | 300 | Short-lived, aggressive cleanup |
| **Total peak** | | **~500** | Well within Arcade's 8000+ sprite capability |

### Performance Budget (per frame at 60fps = 16.67ms)

| Phase | Budget | Notes |
|-------|--------|-------|
| Input processing | <0.5ms | Key state lookup |
| Physics update | <2ms | Velocity/position for ~200 entities |
| Collision detection | <3ms | Spatial hash for asteroids; linear for others |
| Entity logic (AI, spawning) | <2ms | Enemy AI, spawn timers |
| Particle update | <1ms | Position updates, lifetime checks |
| Rendering (GPU) | <8ms | Arcade SpriteList batch draw |
| HUD/text | <1ms | Pre-cached text rendering |
| **Total** | **<17ms** | Fits within 16.67ms budget |

### Optimisation Strategies

1. **Spatial hashing** on asteroid and shop node SpriteLists for O(1) collision lookups.
2. **SpriteList batching**: All entities of the same type in a single SpriteList for one-call GPU batch rendering.
3. **Particle pooling**: Pre-allocate particle sprites and reuse them instead of creating/destroying each frame.
4. **Static background**: Starfield rendered once to a texture, drawn as a single full-screen sprite.
5. **Entity caps**: Hard limits on projectile count, pickup count, and particle count prevent runaway entity growth.
6. **Lazy text rendering**: HUD text sprites are only regenerated when the displayed value changes, not every frame.
7. **Ghost sprite caching**: Wrap-around ghost sprites for edge collision are only created for entities actually near an edge (checked with simple coordinate comparison).

---

## Testing Strategy

Per copilot.instructions.md, the project targets **30% code coverage minimum** using pytest. Testing focuses on deterministic game logic rather than rendering.

### Unit Tests

| Area | What is Tested | Approach |
|------|---------------|----------|
| Physics | Thrust, drag, speed cap, wrap-around | Feed known inputs, assert expected positions/velocities |
| Collision | AABB overlap detection, edge wrap collisions | Create sprites at known positions, verify collision results |
| Asteroid splitting | Correct child count and sizes per parent size | Destroy asteroid, count children |
| Scoring | Points per asteroid size, per enemy type, bonuses | Simulate destruction events, check score totals |
| Upgrades | Cost calculation, stat modification, max level cap | Apply upgrades, verify effective stats |
| Insurance | Tier costs, upgrade retention on death | Simulate game over with insurance, check retained state |
| Difficulty scaling | Parameter progression across levels | Iterate levels, verify parameters within expected ranges |
| Persistence | Save/load round-trip, schema migration, corrupt file handling | Write JSON, read back, compare; write garbage, verify fallback |
| Currency | Drop chance, collection, timeout, destruction | Simulate combat events, check currency state |

### Integration Tests

| Area | What is Tested |
|------|---------------|
| Full combat phase | Spawn asteroids, simulate ship actions, verify level completion |
| Shop purchase flow | Enter shop, purchase upgrade, verify state change, exit shop |
| Game over flow | Reduce shields to zero, verify game over triggers, check high score save |
| Settings persistence | Change settings, restart (re-init), verify settings loaded |

### Test Infrastructure

- Tests use `pytest` with fixtures for common setup (game state, entity manager, physics engine).
- Rendering is not tested directly; tests operate on game logic objects without an Arcade window.
- A `conftest.py` provides shared fixtures and mock objects.
- Tests are located in `void-breaker/tests/` and run with `pytest -q --cov=void-breaker/app/src --cov-report=term-missing`.

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Ship physics feel wrong (too floaty, too stiff) | High | Medium | Expose all physics constants in `game_config.py` as a single tuning dataclass. Build a physics sandbox state for rapid iteration. Playtest early and often. |
| Arcade library bug or limitation blocks a feature | Medium | Low | Arcade 3.x is mature and well-documented. Fallback: drop down to pyglet directly for the specific feature (Arcade is built on pyglet). |
| Wrap-around collision edge cases (entities at corners) | Medium | Medium | Ghost sprite approach handles all edge cases. Comprehensive unit tests for corner and edge scenarios. |
| Shop fly-through interaction is confusing | High | Medium | Clear visual feedback (pulsing nodes, cost labels, colour coding). Re-centering after purchase prevents confusion. Fallback: add keyboard shortcut to purchase highlighted node. |
| Particle effects cause frame drops at peak entity count | Low | Low | Particle count is hard-capped. Particles use simple sprite pooling, not complex GPU shaders. Budget of 300 particles is conservative for Arcade's capability. |
| PyInstaller macOS bundle fails on specific OS versions | Medium | Low | Test on macOS 13+ (Ventura and later). Pin PyInstaller version. Document minimum OS requirement in Info.plist. |
| Asset creation bottleneck (all original art/audio required) | Medium | High | Use minimalist retro aesthetic (simple geometric shapes, vector-style sprites). Procedurally generate where possible (starfield, particle effects). Synthesize audio programmatically or use simple waveform generation. |
| Insurance system creates balance problems | Medium | Medium | Make insurance costs scale aggressively with tier and level number. Playtest with insurance enabled/disabled. Expose all insurance cost parameters in config for tuning. |

---

## Open Questions

1. **Product name**: "VoidBreaker" is used as a placeholder throughout this document (matching one of the candidates in the brief). Final name selection should be confirmed before asset creation (splash screen, icon, window title).

2. **Ship classes**: The brief lists ship classes as "recommended, optional". This design supports them architecturally (base stats in `ShipState` can vary per class) but defers implementation to a later phase if scope needs trimming. The architecture does not change either way.

3. **Background music**: Marked as optional in the brief. The `AudioManager` supports it, but actual music asset creation may be deferred. The system is designed to work with or without music.

4. **Challenge variants**: "No shop", "double enemies", etc. are architecturally trivial (they modify `DifficultyParams` and disable the shop state transition) but add testing and UI scope. Recommend deferring to post-v1.0.

5. **Autofire**: Listed as both a setting and a potential purchasable upgrade. Recommend implementing as a setting only (simpler) for v1.0, with the upgrade variant as a future enhancement.

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-18 | Solutions Architect | Initial solution design |
| 1.1 | 2026-02-18 | Solutions Architect | Competitive analysis confirmed fly-through shop and insurance system are unique market differentiators with no equivalent in any competitor (Nova Drift, Asteroids But Roguelite, Void Miner, et al.). Design preserves both as first-class systems: InsuranceManager as a dedicated subsystem with tiered retention model, and Shop Phase with spatial node interaction and piloting-based purchasing. No architectural changes required. |
