# Phase Plan: VoidBreaker (Asterax Tribute)

## Overview

VoidBreaker is implemented in six incremental phases, each building on the previous and delivering a testable vertical slice. The approach is foundation-first: Phase 1 establishes the project skeleton, dev tooling, and core architectural patterns (state machine, persistence, config). Phase 2 delivers a playable core game loop (ship, asteroids, collisions, level completion). Subsequent phases layer on combat depth, the signature shop/economy system, UI polish, and finally packaging for distribution. Each phase isolates human setup tasks in its first component and concludes with E2E testing and documentation.

## Summary

- **Number of Phases**: 6 phases
- **Number of Components**: 49 components

---

## Phase 1: Foundation & Project Skeleton

### Phase Overview

**Overview**: Establishes the complete development environment, project structure, packaging configuration, and foundational systems that all subsequent phases depend on. Delivers a running Arcade window with a functional state machine shell, persistence layer, settings system, input management, and a static starfield background. No gameplay yet -- this phase produces the architectural scaffold.

**Objective**: A developer can clone the repo, run a single command, and see a windowed application cycling through stub states (main menu, placeholder combat, placeholder shop, game over) with settings persisted to disk and keyboard input routed to the active state.

**Dependencies**: None -- this is the starting phase.

### Phase Key Deliverables

- **Project skeleton**: `pyproject.toml` with editable install, directory structure matching solution-design.md, virtual environment, dev tooling (Black, isort, mypy, pytest)
- **Arcade application shell**: Window creation, fixed-timestep game loop, state machine with transitions and overlay stack
- **Persistence layer**: JSON read/write for settings and high scores with schema versioning, atomic writes, and platform-appropriate storage path (`~/Library/Application Support/VoidBreaker/`)
- **Input manager**: Keyboard event capture with key-held tracking, remappable bindings loaded from settings
- **Game config system**: Centralised tuning parameters in `game_config.py`, upgrade definitions in `upgrade_definitions.py`, difficulty tables in `difficulty_tables.py`
- **Audio manager skeleton**: Sound loading infrastructure and volume-controlled playback API (no actual sound assets yet -- uses placeholder stubs)
- **Rendering foundation**: Static starfield background texture, basic HUD text rendering, screen clear/draw pipeline

### Phase Components

- **1.1 Human Setup & Environment**: Create Python 3.13+ virtual environment, install Arcade 3.x and dev dependencies, configure `pyproject.toml` with editable install, set up `.env` files, verify `black --check`, `isort --check-only`, `mypy`, and `pytest` all pass on an empty project
- **1.2 Project Structure & Entry Point**: Create full directory structure per solution-design.md, implement `main.py` entry point, create Arcade `Window` subclass in `window.py` with fixed-timestep accumulator loop, verify window opens and renders a blank frame
- **1.3 State Machine**: Implement state machine with `on_enter()`, `on_exit()`, `on_update()`, `on_draw()`, `on_key_press()`, `on_key_release()` protocol. Create stub states for MainMenu, CombatPhase, ShopPhase, GameOver, Pause (overlay), HowToPlay, HighScores, SettingsScreen. Implement state stack for overlays. Verify transitions between all states via keyboard shortcuts
- **1.4 Persistence Layer**: Implement `PersistenceManager` with JSON read/write, atomic save (tempfile + os.replace), schema versioning, corrupt-file fallback to defaults. Create `GameSettings` and `HighScoreEntry` dataclasses. Resolve storage path using `platformdirs` or `pathlib` platform detection. Verify round-trip save/load for settings and high scores
- **1.5 Input Manager**: Implement `InputManager` with key-held set tracking, configurable key bindings loaded from persisted settings, default bindings matching solution-design.md. Wire into state machine so each state receives input events. Verify key press/release routing to active state
- **1.6 Game Config & Data Models**: Create `game_config.py` with all physics tuning parameters as a dataclass, `upgrade_definitions.py` with all upgrade definitions, `difficulty_tables.py` with per-level scaling parameters. Create `GameState`, `ShipState`, `InsuranceState`, `DifficultyParams` data models. Verify all models instantiate with defaults
- **1.7 Audio Manager Skeleton & Rendering Foundation**: Implement `AudioManager` with sound loading from asset directory, volume-controlled `play()` method respecting master/sfx volume settings. Create starfield background renderer (pre-rendered texture). Implement basic HUD text rendering utility. Verify audio manager loads without errors (no actual .wav files needed yet -- graceful no-op on missing files)
- **1.8 E2E Testing & Documentation**: Write pytest fixtures for game state, persistence, input, and config. Write unit tests for persistence round-trip, settings defaults, state machine transitions. Run full test suite and verify 30%+ coverage on implemented modules. Update `implementation-context-phase-1.md` with component summaries

### Phase Acceptance Criteria

- [ ] `pip install -e .` succeeds and `python -m asterax.app.src.main` launches an Arcade window
- [ ] State machine transitions between all stub states via keyboard input without errors
- [ ] Settings file is created at `~/Library/Application Support/VoidBreaker/settings.json` on first launch and survives application restart
- [ ] High scores file is created and supports atomic write (no corruption on simulated crash)
- [ ] `black --check`, `isort --check-only`, and `pytest` all pass
- [ ] All physics constants, upgrade definitions, and difficulty parameters are centralised in `config/` dataclasses
- [ ] Fixed-timestep accumulator runs at 60fps target with no frame drops on idle

---

## Phase 2: Core Game Loop

### Phase Overview

**Overview**: Delivers the minimum playable game: a ship with inertial physics, asteroids that spawn/split/wrap, projectiles, collision detection, currency drops, basic scoring, level completion, game over, and high score recording. The player can fly, shoot, destroy asteroids, collect currency, clear a level, advance to the next level (no shop yet -- straight to next combat phase), die, and record a high score. This is the critical "is it fun?" milestone.

**Objective**: A complete combat loop where a player can play through multiple levels of increasing difficulty, accumulate score, die when shields reach zero, and see their score on the high score table. Ship handling must feel inertial, responsive, and satisfying.

**Dependencies**: Phase 1 complete (state machine, persistence, input, config, window).

### Phase Key Deliverables

- **Player ship entity**: Sprite with inertial physics (thrust, rotation, drag, speed cap, brake), wrap-around movement, shield/hull state, damage feedback (flash, brief invulnerability)
- **Asteroid system**: Three sizes (large/medium/small), splitting on destruction, random velocity/rotation, wrap-around, point values, currency drop chance
- **Projectile system**: Player-fired projectiles with lifetime/range, wrap-around, collision with asteroids
- **Collision system**: Player-asteroid, projectile-asteroid collisions using Arcade spatial hashing. Ghost sprite approach for wrap-around edge cases
- **Currency pickups**: Spawned from destroyed asteroids, collectible by contact, visual identity, optional lifetime timeout
- **Scoring**: Points per asteroid size, score accumulation, level tracking
- **Level progression**: Level start spawns asteroids per difficulty table, level clears when all asteroids destroyed, next level increases difficulty parameters
- **Game over flow**: Shields reach zero triggers game over state, run summary display, high score entry if qualified, return to main menu
- **Entity manager**: Typed SpriteList collections for all entity types with batch rendering

### Phase Components

- **2.1 Human Setup & Asset Preparation**: Create placeholder sprite assets (geometric shapes) for ship, asteroids (3 sizes), projectiles, and currency pickups. Create placeholder sound effect stubs (.wav files -- can be silent or simple tones). Establish asset directory structure under `assets/sprites/` and `assets/sounds/`
- **2.2 Player Ship Entity & Physics**: Implement `PlayerShip` extending `arcade.Sprite` with inertial physics model from solution-design.md (thrust, rotation, natural drag, brake drag, speed cap). Wire to `InputManager` for rotation, thrust, brake controls. Implement wrap-around positioning. Verify ship responds to input with correct inertial behaviour
- **2.3 Asteroid System**: Implement `Asteroid` entity with three sizes (LARGE, MEDIUM, SMALL), random velocity and rotation, wrap-around. Implement splitting logic (large splits into 2-3 medium, medium splits into 2-3 small, small is destroyed). Configure point values and currency drop chances per size. Implement `SpawnManager` for level-start asteroid placement. Verify asteroids spawn, move, wrap, and split correctly
- **2.4 Projectile System & Collision Detection**: Implement `Projectile` entity with velocity, lifetime/range, wrap-around. Implement fire action on ship with cooldown based on fire rate config. Implement `CollisionSystem` using Arcade's `check_for_collision_with_list()` with spatial hashing on asteroid SpriteList. Implement ghost sprite approach for wrap-around edge collisions. Handle projectile-asteroid collision (damage, split, destroy, score). Handle ship-asteroid collision (damage, feedback). Verify all collision pairs resolve correctly
- **2.5 Currency Pickups & Collection**: Implement `CurrencyPickup` entity spawned on asteroid destruction (probability from config). Pickups drift with slight velocity, have visual identity (distinct colour/shape), and optional lifetime timeout. Collection on ship contact awards currency to `GameState`. Verify currency spawns, is collectible, and accumulates
- **2.6 Entity Manager & Rendering Pipeline**: Implement `EntityManager` with typed `SpriteList` collections (player, asteroids, player_projectiles, currency_pickups). Implement draw order (background, asteroids, pickups, projectiles, ship). Integrate with starfield background from Phase 1. Implement basic particle effects for explosions (simple sprite burst). Verify all entities render correctly with proper z-ordering
- **2.7 Combat Phase State & Level Progression**: Implement `CombatPhase` state replacing stub from Phase 1. Wire entity manager, physics, collisions, and spawning into the update loop. Implement level completion check (all asteroids destroyed). On level clear, increment level, scale difficulty per `difficulty_tables.py`, spawn new asteroids. Implement game over trigger (shields <= 0). Wire to `GameOver` state with run summary and high score entry. Implement basic HUD (shields bar, score, level, currency)
- **2.8 E2E Testing & Documentation**: Write tests for physics (thrust, drag, wrap), collisions (projectile-asteroid, ship-asteroid, edge cases), asteroid splitting, scoring, currency drops, difficulty scaling. Run E2E scenario: launch game, play through 3+ levels, die, verify high score recorded. Verify 30%+ coverage. Update `implementation-context-phase-2.md`

### Phase Acceptance Criteria

- [ ] Player ship responds to keyboard input with inertial physics (thrust builds velocity, ship drifts when thrust released, drag gradually slows)
- [ ] Ship, asteroids, and projectiles all wrap correctly at screen edges
- [ ] Large asteroids split into medium, medium into small, small are destroyed on projectile impact
- [ ] Currency pickups spawn from destroyed asteroids and are collected on ship contact
- [ ] Score accumulates correctly per asteroid size destroyed
- [ ] Level clears when all asteroids are destroyed; next level spawns more/faster asteroids
- [ ] Game over triggers when shields reach zero; run summary displays score, level reached, currency collected
- [ ] High score is recorded to `high_scores.json` and persists across application restarts
- [ ] Collision detection works correctly at screen edges (ghost sprite approach)
- [ ] Game runs at stable 60fps with 30+ asteroids on screen

---

## Phase 3: Combat Expansion (Enemies, Spawning, Difficulty)

### Phase Overview

**Overview**: Adds the full combat system: enemy ships (two archetypes minimum), enemy projectiles, the spawn manager for timed enemy waves, damage feedback effects, and refined difficulty scaling. After this phase, the combat experience is feature-complete: players face both asteroids and enemies, with escalating challenge across levels.

**Objective**: Enemy ships appear from mid-levels onward, fire projectiles at the player, and escalate in frequency and aggression. The difficulty curve supports 30+ minutes of skilled play with smooth scaling and no sudden impossible spikes.

**Dependencies**: Phase 2 complete (ship, asteroids, projectiles, collisions, level progression).

### Phase Key Deliverables

- **Enemy ship entities**: Two archetypes (Basic Shooter and Aggressive) with distinct AI behaviour, firing patterns, health, point values, and drop tables
- **Enemy projectile system**: Enemy-fired projectiles with collision against player ship
- **Spawn manager expansion**: Timed enemy spawning with per-level configuration, enemy count caps, spawn intervals
- **Expanded collision system**: Player vs enemy projectiles, player projectiles vs enemies, ship-enemy collision
- **Damage feedback**: Screen flash, hit sound, brief invulnerability window on player damage. Enemy damage/destruction effects
- **Difficulty scaling refinement**: Tuned difficulty tables for asteroid count/speed, enemy spawn rate/aggression, currency drop rates across 30+ levels
- **Buff pickups** (optional): Rare drops from enemies providing temporary buffs (heal, shield, damage boost, speed boost)

### Phase Components

- **3.1 Human Setup & Enemy Assets**: Create placeholder sprite assets for two enemy ship archetypes (Basic Shooter, Aggressive) and enemy projectiles. Create placeholder sound effects for enemy fire, enemy explosion, and player hit. Place assets in `assets/sprites/` and `assets/sounds/`
- **3.2 Enemy Ship Entities & AI**: Implement `EnemyShip` entity extending `arcade.Sprite` with archetype-based configuration (BASIC, AGGRESSIVE). Basic Shooter: slow movement, low fire rate, simple targeting. Aggressive: faster movement, higher fire rate, more aggressive tracking. Both wrap at screen edges. Implement health, point values, and destruction logic. Verify both archetypes behave distinctly
- **3.3 Enemy Projectile System & Expanded Collisions**: Implement enemy-fired `Projectile` entities (owner=ENEMY). Add enemy projectile SpriteList to EntityManager. Expand `CollisionSystem` with: player vs enemy projectiles (damage player), player projectiles vs enemies (damage enemy), player vs enemy ships (damage both). Verify all new collision pairs
- **3.4 Spawn Manager & Enemy Waves**: Expand `SpawnManager` to handle timed enemy spawning during combat phases. Configure per-level: enemy spawn enabled/disabled (off for early levels), max enemy count, spawn interval, aggression factor. Enemies spawn at screen edges, moving inward. Implement enemy count cap to prevent overwhelming the player. Verify enemies spawn according to difficulty configuration
- **3.5 Damage Feedback & Visual Effects**: Implement player damage feedback: screen flash/tint, hit sound effect, brief invulnerability window (0.5-1 second) with visual flashing. Implement enemy destruction effects (explosion particles, sound). Implement player ship destruction sequence for game over. Verify all feedback effects trigger on correct events
- **3.6 Difficulty Scaling & Balance**: Refine `difficulty_tables.py` with tuned values for 30+ levels. Early levels (1-5): asteroids only, teaching fundamentals. Mid levels (6-15): enemies introduced, upgrade decisions matter. Late levels (16+): intense but fair, high asteroid density and aggressive enemies. Playtest and adjust curves. Verify difficulty parameters progress smoothly
- **3.7 Buff Pickups (Optional)**: Implement `BuffPickup` entity with types: HEAL (restore shields), DAMAGE_BOOST (temporary), SPEED_BOOST (temporary). Rare drops from enemy destruction. Duration-based effects tracked in `GameState`. Verify buff effects apply and expire correctly
- **3.8 E2E Testing & Documentation**: Write tests for enemy AI behaviour, enemy spawning, all new collision pairs, difficulty scaling across 30 levels, buff effects. Run E2E scenario: play through 15+ levels with enemies, verify combat feels challenging but fair. Verify 30%+ coverage on new modules. Update `implementation-context-phase-3.md`

### Phase Acceptance Criteria

- [ ] Basic Shooter enemies appear from configured level onward with slow, predictable firing patterns
- [ ] Aggressive enemies appear at higher levels with faster movement and higher fire rates
- [ ] Enemy projectiles damage the player; player projectiles destroy enemies
- [ ] Enemy spawn rate and aggression scale with level number per difficulty tables
- [ ] Player receives clear damage feedback (flash, sound, brief invulnerability) on hit
- [ ] Enemy destruction plays explosion effects and awards points
- [ ] Difficulty curve supports 30+ minutes of skilled play without sudden impossible spikes
- [ ] Enemy count is capped per level to maintain performance and fairness
- [ ] All collision pairs (player-enemy, player-enemy_projectile, projectile-enemy) work correctly including at screen edges

---

## Phase 4: Shop & Economy System

### Phase Overview

**Overview**: Implements VoidBreaker's signature feature set: the between-level fly-through shop, the upgrade system, the insurance mechanic, and the currency economy. After this phase, the complete core game loop is functional: fight, collect currency, shop for upgrades, fight harder, repeat. This is the phase that differentiates VoidBreaker from every competitor.

**Objective**: After each combat level, the player enters a shop phase where they pilot their ship into floating upgrade nodes to purchase improvements. Upgrades apply immediately and affect gameplay. Insurance can be purchased to retain upgrades on death. The currency economy creates meaningful decisions each level.

**Dependencies**: Phase 3 complete (full combat system, enemies, scoring, currency accumulation).

### Phase Key Deliverables

- **Shop phase state**: Fly-through shop with circular node layout, ship piloting, node collision/purchase interaction
- **Shop node entities**: Coloured orbs with labels showing upgrade name, level, cost, affordability indicators
- **Upgrade manager**: Applies purchased upgrades to ship stats, tracks upgrade levels, enforces max levels, calculates costs with scaling
- **Insurance manager**: Three tiers (OFF, BASIC, PREMIUM), recurring cost per level, upgrade retention logic on death
- **Currency manager**: Tracks spending, validates purchases, handles insurance deductions at level transitions
- **Ship re-centring**: Smooth interpolation back to centre after purchase with brief invulnerability to prevent accidental double-purchases
- **Shop UI**: Current currency display, item costs, upgrade levels, affordable/maxed indicators, "Continue" node to advance

### Phase Components

- **4.1 Human Setup & Shop Assets**: Create placeholder sprite assets for shop nodes (coloured orbs per category: red=weapons, blue=defense, green=mobility, gold=economy, white=repairs, purple=insurance). Create "Continue" node asset. Create shop purchase and shop denied sound effect placeholders. Place assets in `assets/sprites/` and `assets/sounds/`
- **4.2 Shop Phase State & Layout**: Implement `ShopPhase` state replacing stub from Phase 1. Generate circular node layout around playfield centre per solution-design.md. Player ship starts at centre. Ship retains physics from combat phase (thrust, rotation, wrap disabled in shop). Implement transition from CombatPhase to ShopPhase on level clear and from ShopPhase back to CombatPhase on "Continue" node collision or key press. Verify shop state activates after level clear and returns to combat
- **4.3 Shop Node Entities & Interaction**: Implement `ShopNode` entity extending `arcade.Sprite` with upgrade definition reference, cost calculation, purchase state. Render nodes with category-coloured orbs, text labels (name, "Lv X/Y", cost). Visual indicators: pulsing highlight on affordable, dimmed/crossed on unaffordable or maxed. On ship-node collision: check affordability, deduct currency, apply upgrade, play sound, trigger re-centre. Denied collision: play denied sound, slight bounce. Verify node rendering and purchase interaction
- **4.4 Upgrade Manager & Stat Application**: Implement `UpgradeManager` that tracks all upgrade levels, calculates effective stats from base stats + upgrade bonuses, enforces max levels. Upgrade categories: weapon fire rate, weapon damage, weapon speed, weapon spread, defense shields, mobility thrust, mobility turn, economy magnet, economy protection, repairs (restore shields). Include score bonus multiplier as an optional upgrade (purchasable score multiplier that trades currency for points, per brief item 13). Recalculate effective stats on any upgrade change. Verify upgrades modify ship behaviour (e.g., increased fire rate after purchasing weapon fire rate upgrade)
- **4.5 Insurance Manager & Death Retention**: Implement `InsuranceManager` with three tiers: OFF (retain nothing, no cost), BASIC (retain 50% of upgrade levels rounded down, moderate cost per level), PREMIUM (retain all upgrades, high cost per level). Insurance cost deducted at each level transition. On game over with insurance: calculate retained upgrades, apply to restart state. Insurance node in shop allows tier change. Verify insurance cost deduction and upgrade retention on death
- **4.6 Currency Manager & Economy Flow**: Implement `CurrencyManager` centralising all currency operations: earn (pickups), spend (shop purchases), deduct (insurance per-level cost). Validate all transactions (cannot spend more than available). Track cumulative earned/spent for run summary. Wire currency display into HUD. Verify economy flow across a full run (earn in combat, spend in shop, insurance deducted per level)
- **4.7 Ship Re-Centring & Purchase Flow Polish**: Implement smooth ship interpolation back to centre over 0.3 seconds after purchase. During interpolation, disable node collisions (brief invulnerability). Implement "Continue" node at bottom of layout that transitions to next combat phase. Optional: add key shortcut (e.g., Enter) as alternative to flying to Continue node. Verify re-centring prevents accidental double-purchases and Continue node works
- **4.8 E2E Testing & Documentation**: Write tests for shop node interaction, upgrade application, insurance retention, currency transactions, cost scaling. Run E2E scenario: play level, enter shop, purchase upgrades, verify stats change, continue to next level, die with insurance, verify retention. Verify 30%+ coverage on new modules. Update `implementation-context-phase-4.md`

### Phase Acceptance Criteria

- [ ] Shop phase activates after each combat level clear with circular node layout
- [ ] Player can pilot ship into nodes to purchase upgrades; currency is deducted correctly
- [ ] Purchased upgrades visibly affect gameplay (faster fire rate, more shields, etc.)
- [ ] Unaffordable and maxed-out nodes are visually distinct and deny purchase with feedback
- [ ] Ship re-centres after purchase with brief invulnerability preventing double-purchases
- [ ] Insurance tiers work correctly: OFF retains nothing, BASIC retains ~50%, PREMIUM retains all
- [ ] Insurance cost is deducted at each level transition
- [ ] "Continue" node (or key press) transitions back to combat with increased difficulty
- [ ] Full game loop works: combat -> shop -> combat -> ... -> death -> high score
- [ ] Currency balance is never negative; all transactions are validated

---

## Phase 5: Polish & UX

### Phase Overview

**Overview**: Transforms the functional game into a polished, release-quality experience. Implements all UI screens (main menu, how-to-play, settings, high scores, game over summary), the pause system, Practice/Training mode, complete audio (sound effects for all events), particle effects (explosions, thrust trail, pickup sparkle), visual polish (damage flash, level transitions, screen shake), and accessibility features (colorblind mode, screen shake toggle, difficulty presets).

**Objective**: A new player can launch the game, navigate menus, understand controls from "How to Play", adjust settings, play through the full game loop with satisfying audio-visual feedback, pause/resume, die with a polished game over sequence, and view their high score on the leaderboard -- all without consulting external documentation.

**Dependencies**: Phase 4 complete (full game loop with shop, upgrades, insurance, economy).

### Phase Key Deliverables

- **Main menu**: New Game, How to Play, Settings, High Scores, Quit -- navigable by keyboard with visual feedback
- **How-to-Play screen**: Controls reference, gameplay explanation, tips
- **Settings screen**: Key remapping, volume sliders (master, music, SFX), visual options (colorblind mode, screen shake), difficulty presets, fire mode toggle
- **High scores screen**: Leaderboard display with name, score, level, difficulty, date
- **Game over screen**: Run summary (score, level, enemies destroyed, currency earned/spent), high score entry with initials input
- **Pause system**: Instant freeze overlay on combat/shop with resume, restart, settings, exit to menu
- **Complete audio**: All sound effects from solution-design.md catalogue loaded and triggered on correct events
- **Particle effects**: Explosions (3 sizes), thrust trail, pickup collection sparkle, damage flash, purchase confirmation
- **Visual polish**: Level transition effects (fade or brief text overlay), HUD polish, shop node animations
- **Accessibility**: Colorblind palette option, screen shake settings (off/low/medium), difficulty presets (casual/classic/hard)
- **Practice/Training mode**: Low-stakes sandbox accessible from main menu with toggles for asteroids only, no enemies, infinite shields

### Phase Components

- **5.1 Human Setup & Final Assets**: Create or source all remaining game assets: sprite art for ship, asteroids, enemies, projectiles, pickups, shop nodes, UI elements (buttons, panels, icons). Create all sound effects from the solution-design.md audio catalogue (16 distinct sounds). Create font assets. Place all final assets in `assets/` subdirectories. This is the largest human task -- all visual and audio identity is established here
- **5.2 Main Menu & Navigation System**: Replace main menu stub with full implementation: New Game, How to Play, Settings, High Scores, Quit. Keyboard navigation with visual highlight/selection feedback. Menu transition animations. Wire all menu options to their respective states. Verify all menu paths work and return correctly
- **5.3 How-to-Play & High Scores Screens**: Implement How-to-Play screen with controls diagram, gameplay explanation (combat, shop, insurance), and tips. Implement High Scores screen displaying persistent leaderboard entries sorted by score, showing name, score, level reached, difficulty, and date. Filter by difficulty if multiple presets are active. Verify both screens display correctly and return to menu
- **5.4 Settings Screen & Accessibility**: Implement Settings screen with: key remapping UI (select action, press new key), volume controls (master, music, SFX -- display as bars or numeric), fire mode toggle (hold/tap), autofire toggle, colorblind mode toggle, screen shake setting (off/low/medium), difficulty preset selection (casual/classic/hard). All changes persist immediately via PersistenceManager. Verify all settings apply and persist across restarts
- **5.5 Game Over Screen & High Score Entry**: Implement Game Over screen with run summary: final score, level reached, enemies destroyed, asteroids destroyed, currency collected, currency spent, insurance tier used. If score qualifies for leaderboard, display initials entry (3-10 character input). Save high score entry. Transition to main menu. Verify summary data is accurate and high score saves correctly
- **5.6 Pause System**: Implement Pause as a state stack overlay that freezes all game logic (combat and shop). Pause menu: Resume, Restart Run, Settings, Exit to Menu. Pause triggered by configured key (default: Escape). Verify pause freezes all entities and timers, resume restores state exactly, restart works, and exit returns to menu cleanly
- **5.7 Audio Integration & Particle Effects**: Integrate all sound effects with game events: fire, hit/damage, explosion (3 sizes), enemy explosion, pickup currency, pickup buff, shop purchase, shop denied, level clear, game over, menu navigate, menu select. Implement particle system: explosion particles (size-scaled), ship thrust trail, pickup collection sparkle, damage impact flash, shop purchase confirmation burst. Verify all audio triggers match events and particles render without frame drops
- **5.8 Visual Polish & Transitions**: Implement level transition effect (brief fade or "Level X" text overlay between levels). Polish HUD layout and readability. Add screen shake on damage (respecting settings). Add ship damage flash effect. Polish shop node pulsing/glow animations. Implement colorblind-friendly palette swap affecting all entity colours. Verify visual polish across the full game loop
- **5.9 Difficulty Presets Integration**: Implement three difficulty presets modifying `DifficultyParams`: Casual (fewer asteroids, slower enemies, more currency drops, reduced damage), Classic (default tuning as balanced in Phase 3), Hard (more asteroids, faster/more aggressive enemies, reduced currency drops, increased damage). Selection in settings and on new game. Separate high score leaderboards per difficulty. Verify each preset produces a distinctly different gameplay experience
- **5.10 Practice/Training Mode**: Implement Practice/Training mode accessible from main menu. Low-stakes sandbox for learning controls and mechanics. Configurable toggles: asteroids only (no enemies), infinite shields (cannot die), reduced asteroid count. Reuses CombatPhase state with modified `DifficultyParams` (enemies disabled, shields set to infinite or very high, currency and scoring optional). No high score recording in practice mode. Verify practice mode launches with correct parameters, toggles work, and player can return to main menu
- **5.11 E2E Testing & Documentation**: Test all UI screens navigate correctly. Test settings persist and apply. Test pause freeze/resume. Test audio triggers for all events. Test particle effects do not cause frame drops at peak entity count. Test practice mode launches and toggles work. Run full E2E scenario: launch, navigate menus, adjust settings, start game, play 5+ levels, use shop, pause/resume, die, enter high score, verify leaderboard. Verify 30%+ coverage. Update `implementation-context-phase-5.md`

### Phase Acceptance Criteria

- [ ] All menu screens (main menu, how-to-play, settings, high scores, game over) are fully functional and navigable by keyboard
- [ ] Settings changes (volume, controls, visual options, difficulty) persist across application restarts
- [ ] Key remapping works for all bindable actions
- [ ] Pause instantly freezes all game logic and resume restores state perfectly
- [ ] All 16 sound effects from the audio catalogue trigger on correct events
- [ ] Particle effects (explosions, thrust trail, pickup sparkle) render without frame drops
- [ ] Game over screen shows accurate run summary and allows high score entry
- [ ] Colorblind mode and screen shake settings visibly affect the game
- [ ] Three difficulty presets produce distinctly different gameplay experiences
- [ ] Practice/Training mode is accessible from main menu with working toggles (asteroids only, infinite shields)
- [ ] A new player can navigate the entire game without external documentation

---

## Phase 6: Packaging & Release

### Phase Overview

**Overview**: Prepares VoidBreaker for distribution as a standalone macOS application. Produces a PyInstaller-built `.app` bundle wrapped in a DMG disk image. Covers final QA, performance validation, cross-platform smoke testing, and all release documentation. After this phase, a non-developer user can download a DMG, drag the app to Applications, and play.

**Objective**: A distributable macOS `.app` bundle that launches, runs the full game at 60fps, persists data correctly, and looks/sounds polished. DMG creation, README, and basic release documentation are complete.

**Dependencies**: Phase 5 complete (all gameplay, UI, audio, and visual polish).

### Phase Key Deliverables

- **PyInstaller build configuration**: `VoidBreaker.spec` file with all hidden imports, data file mappings, Info.plist entries, and macOS-specific settings
- **macOS .app bundle**: Standalone application that runs without Python installed on the target machine
- **DMG disk image**: Drag-to-install disk image with VoidBreaker.app and Applications alias
- **Application icon**: `.icns` file for macOS dock/Finder display
- **Final QA**: Full game playthrough on clean macOS install, performance validation at peak entity count, persistence verification after app bundle launch
- **Release documentation**: README with installation instructions, system requirements, controls reference, known issues

### Phase Components

- **6.1 Human Setup & Release Preparation**: Create application icon (`.icns` format). Finalise product name in all user-facing strings (window title, menu, about, file paths). Review all placeholder assets and confirm final versions are in place. Verify no TODO/FIXME comments remain in codebase (run `scripts/evals.py`). Confirm licensing compliance (all assets original)
- **6.2 PyInstaller Configuration & Build**: Create `VoidBreaker.spec` with: hidden imports for Arcade/pyglet modules, data file mappings for all assets (sprites, sounds, fonts), macOS Info.plist entries (bundle identifier, version, minimum OS version), `.icns` icon reference, `--windowed` and `--onedir` flags. Build the `.app` bundle. Verify it launches on the build machine without errors
- **6.3 DMG Creation & Distribution Packaging**: Create DMG disk image containing `VoidBreaker.app` and an alias to `/Applications`. Configure DMG background and layout. Document code signing and notarisation steps for future use (not required for v1.0 local distribution). Verify DMG mounts and drag-to-install works
- **6.4 Performance Validation**: Profile the packaged application at peak entity count (100 asteroids, 10 enemies, 15 player projectiles, 20 enemy projectiles, 40 pickups, 300 particles). Verify stable 60fps. Verify no memory leaks over 30+ minute sessions. Test on minimum target hardware (macOS 13+ Ventura). Document performance characteristics
- **6.5 Final QA & Cross-Platform Smoke Test**: Full playthrough of packaged `.app` on clean macOS install (no development tools). Verify: game launches, settings persist, high scores persist, all audio plays, all visual effects render, shop works, insurance works, all menus navigate correctly, game over and high score entry work. Optional: smoke test on Windows/Linux via PyInstaller cross-build (not blocking for v1.0). Document any known issues
- **6.6 Release Documentation & E2E Verification**: Write README.md with: installation instructions, system requirements (macOS 13+, Apple Silicon or Intel), controls reference, gameplay overview. Run final `scripts/evals.py` and full pytest suite on packaged source. Verify all tests pass. Create `phase-6-summary.md`. Tag release in version control

### Phase Acceptance Criteria

- [ ] `VoidBreaker.app` launches on macOS 13+ (Ventura) without Python installed on the target machine
- [ ] All game assets (sprites, sounds, fonts) are bundled correctly and load from the `.app` bundle
- [ ] Persistence works from the bundled app (settings and high scores save to `~/Library/Application Support/VoidBreaker/`)
- [ ] DMG disk image mounts, displays VoidBreaker.app and Applications alias, and drag-to-install works
- [ ] Game runs at stable 60fps during peak combat (100+ on-screen entities)
- [ ] No TODO/FIXME comments remain in delivered code; `scripts/evals.py` passes
- [ ] Full game loop works in packaged app: launch -> menu -> play -> shop -> die -> high score -> restart
- [ ] README.md documents installation, system requirements, and controls

---

## Cross-Cutting Concerns

### Testing Strategy

- **E2E Testing Scenarios**: The following critical user journeys must be verified programmatically or via structured manual playthrough at the end of each phase:
  1. **Full game loop**: Launch -> Main Menu -> New Game -> Play 5+ levels (combat + shop each level) -> Die -> Game Over summary -> High Score entry -> Return to menu -> Verify high score persists on restart
  2. **Shop purchase flow**: Enter shop -> Fly to upgrade node -> Purchase -> Verify stats change -> Fly to second node -> Purchase -> Verify currency deducted -> Fly to Continue -> Verify next level starts
  3. **Insurance retention**: Purchase Premium insurance -> Play 3 levels -> Die -> Verify all upgrades retained in new run context
  4. **Settings persistence**: Change key bindings, volume, difficulty, visual settings -> Restart application -> Verify all settings loaded correctly
  5. **Edge cases**: Wrap-around collision at screen corners, currency exactly zero then attempt purchase, max-level upgrade then attempt purchase, game over with no currency collected

- **Unit Testing**: pytest with fixtures. Target 30% coverage minimum. Focus on deterministic game logic: physics calculations, collision detection, upgrade stat calculations, insurance retention, currency transactions, difficulty parameter scaling, persistence round-trip, schema migration, corrupt file recovery. Rendering is NOT unit tested.

- **Integration Testing**: Key integration points tested via pytest with mock Arcade window or headless entity management:
  - Full combat phase (spawn asteroids, simulate actions, verify level completion)
  - Shop purchase flow (enter shop, purchase upgrade, verify state change, exit)
  - Game over flow (shields to zero, verify trigger, check high score save)
  - Settings persistence (change, re-init, verify loaded)

- **Performance Testing**: Profile at Phase 6 with peak entity counts. Target: stable 60fps (16.67ms frame budget). Verify no memory leaks over 30+ minute sessions. Document frame time breakdown per subsystem.

### Documentation Requirements

- **Developer Context Documentation**: Each phase produces `implementation-context-phase-X.md` summarising what was built, key decisions made, and patterns established.
- **Code Documentation**: Google-style docstrings on all public functions, classes, and modules per `copilot.instructions.md`. Inline comments only where logic is non-obvious.
- **API Documentation**: Not applicable (no external API). Internal module interfaces documented via type hints and docstrings.
- **Architecture Decision Records**: Key decisions (physics tuning values, shop layout algorithm, insurance cost scaling) documented in implementation context files.
- **User Documentation**: README.md with installation, controls, and gameplay overview. In-game "How to Play" screen. No external manual required.
- **Deployment Documentation**: PyInstaller build instructions in README. Code signing and notarisation steps documented for future use.

### Quality Gates

- **Code Review**: All PRs require 1+ review (agent or human).
- **Automated Tests**: `pytest` must pass before merge. `black --check` and `isort --check-only` must pass.
- **Code Coverage**: 30% minimum on implemented modules (pytest --cov).
- **Evals**: `scripts/evals.py` must pass (no TODO/FIXME, all public functions have docstrings).
- **Performance**: No frame rate regression below 60fps at peak entity count after any phase.

### DevOps & Deployment

- **Environment**: Local macOS development with Python 3.13+ virtual environment. No cloud infrastructure.
- **Testing**: `pytest -q --cov=void-breaker/app/src --cov-report=term-missing` for unit/integration tests. Manual structured playthroughs for E2E.
- **Build**: PyInstaller 6.x for macOS `.app` bundle. DMG creation via `hdiutil` or `create-dmg`.
- **Distribution**: DMG disk image for local distribution. No App Store or notarisation required for v1.0.
- **Monitoring**: Not applicable (offline game). Performance profiling during Phase 6 QA.

---

## Dependencies & External Factors/Risks

| Risk | Impact | Likelihood | Mitigation | Affected Phases |
|------|--------|------------|------------|-----------------|
| Ship physics feel wrong (too floaty/stiff) | High | Medium | All physics constants centralised in `game_config.py`. Iterate during Phase 2 playtesting. Build physics tuning into dev loop early. | Phase 2 |
| Fly-through shop interaction is confusing | High | Medium | Clear visual feedback (pulsing nodes, cost labels, colour coding). Re-centring prevents confusion. Fallback: add keyboard shortcut to purchase highlighted node. | Phase 4 |
| Asset creation bottleneck | Medium | High | Use minimalist retro aesthetic (geometric shapes, vector-style sprites). Phase 1-4 use placeholder assets. Final assets created in Phase 5.1 as a dedicated human task. | Phase 5 |
| Arcade library limitation blocks a feature | Medium | Low | Arcade 3.x is mature. Fallback: drop to pyglet directly for specific features. | All phases |
| Wrap-around collision edge cases | Medium | Medium | Ghost sprite approach with comprehensive unit tests. Test corner cases explicitly. | Phase 2-3 |
| Insurance system balance problems | Medium | Medium | Insurance costs scale aggressively with tier and level. All parameters in config for tuning. Playtest in Phase 4. | Phase 4 |
| PyInstaller macOS bundle fails on specific OS versions | Medium | Low | Test on macOS 13+ (Ventura and later). Pin PyInstaller version. Document minimum OS in Info.plist. | Phase 6 |
| Difficulty curve too steep or flat | Medium | Medium | Parameterised difficulty scaling in `difficulty_tables.py`. Playtest across skill levels during Phase 3. Difficulty presets in Phase 5 provide safety valve. | Phase 3, 5 |

## Change Management

- **Phase plan updates**: Owned by Technical Business Analyst. Changes require Lead Coordinator approval if they affect phase boundaries, component count, or dependencies.
- **Component scope changes**: Tech Lead agents may propose component scope adjustments during breakdown. Changes that affect cross-phase dependencies must be escalated to TBA for phase plan revision.
- **Requirement changes**: If playtesting reveals fundamental issues (e.g., fly-through shop does not work), the brief may need updating. This triggers phase plan revision.
- **Feature deferral**: Optional features (ship classes, challenge variants, background music, buff pickups) may be deferred from v1.0 without affecting phase structure. Deferral decisions are documented in the relevant phase's implementation context.

## Open Questions

1. **Product name finalisation**: "VoidBreaker" is used throughout this plan. Final name should be confirmed before Phase 5 (asset creation) and Phase 6 (packaging). The competitor analysis flagged a potential conflict with the Steam title "VOID/BREAKER" -- this should be resolved before Phase 5.1.
2. **Ship classes**: Marked as "recommended, optional" in the brief. Architecture supports them (base stats in `ShipState` vary per class). Recommend deferring to post-v1.0 unless Phase 2 playtesting reveals the default ship feel is insufficient.
3. **Background music**: Marked as optional. `AudioManager` supports it. Recommend deferring to post-v1.0 unless suitable music assets are available by Phase 5.1.
4. **Challenge variants**: "No shop", "double enemies", etc. Architecturally trivial but add testing/UI scope. Recommend deferring to post-v1.0.
5. **Autofire**: Brief lists as both a setting and potential upgrade. Recommend implementing as a setting only (simpler) for v1.0, per solution-design.md recommendation.
