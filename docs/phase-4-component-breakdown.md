# Phase 4: Shop & Economy System — Component Breakdown

Version: 1.0
Date: 2026-02-20
Owner: Tech Lead (Phase 4)

---

## Phase Context

Phase 4 implements VoidBreaker's primary market differentiators: the fly-through shop and the insurance system. After this phase, the complete core game loop is functional — fight, collect currency, shop for upgrades, fight harder, repeat.

**Dependencies from prior phases (do not re-implement):**

- Phase 1 delivered: state machine, persistence layer, input manager, `GameState` / `ShipState` / `InsuranceState` / `DifficultyParams` dataclasses, `AudioManager`, `game_config.py`, `upgrade_definitions.py` (static data), `difficulty_tables.py`, HUD text rendering utility
- Phase 2 delivered: `PlayerShip` entity with inertial physics, `EntityManager` with typed `SpriteList` collections, `CombatPhase` state with level completion logic, `SpawnManager`, `GameState.currency` field, `ScoreManager`, wrap-around physics, collision system
- Phase 3 delivered: enemy ships, enemy projectiles, expanded collision system, `DifficultyParams` tuning for 30+ levels, damage feedback effects, full combat loop

**Contracts to Phase 5 (what this phase exposes):**

- `UpgradeManager` — Phase 5 may display upgrade levels in the HUD
- `CurrencyManager` — Phase 5 wires currency display into HUD
- `InsuranceManager` — Phase 5's game over screen reports insurance tier used
- `ShopPhase` state — Phase 5 adds audio triggers and particle effects to shop node purchases

---

## Component Summary

| ID | Name | Owner | Effort | Priority | Key Files |
|----|------|-------|--------|----------|-----------|
| 4.1 | Human Setup & Shop Assets | Human | 2h | Must-have | `assets/sprites/shop/`, `assets/sounds/` |
| 4.2 | Shop Phase State & Layout | AI Agent | 6h | Must-have | `states/shop.py`, `states/__init__.py` |
| 4.3 | Shop Node Entities & Interaction | AI Agent | 6h | Must-have | `entities/shop_node.py`, `entities/__init__.py` |
| 4.4 | Upgrade Manager & Stat Application | AI Agent | 8h | Must-have | `managers/upgrade_manager.py`, `config/upgrade_definitions.py` |
| 4.5 | Insurance Manager & Death Retention | AI Agent | 6h | Must-have | `managers/insurance_manager.py` |
| 4.6 | Currency Manager & Economy Flow | AI Agent | 4h | Must-have | `managers/currency_manager.py` |
| 4.7 | Ship Re-Centring & Purchase Flow Polish | AI Agent | 4h | Must-have | `states/shop.py`, `entities/shop_node.py` |
| 4.8 | E2E Testing & Documentation | AI Agent | 6h | Must-have | `tests/test_upgrades.py`, `tests/test_insurance.py`, `tests/test_currency.py`, `tests/test_shop.py`, `docs/` |

**File ownership matrix (serialisation constraints):**

| File | Created by | Modified by | Constraint |
|------|-----------|-------------|------------|
| `void-breaker/app/src/states/shop.py` | 4.2 | 4.7 | 4.7 must wait for 4.2 |
| `void-breaker/app/src/entities/shop_node.py` | 4.3 | 4.7 | 4.7 must wait for 4.3 |
| `void-breaker/app/src/managers/upgrade_manager.py` | 4.4 | — | No conflict |
| `void-breaker/app/src/managers/insurance_manager.py` | 4.5 | — | No conflict |
| `void-breaker/app/src/managers/currency_manager.py` | Phase 2.5 (created) | 4.6 (REWRITE) | Phase 2.5 must be complete before 4.6. Phase 4 replaces Phase 2's basic implementation with the full CurrencyManager (adding `deduct()`, `can_spend()`, `CurrencyRunStats`, validation, run tracking) |
| `void-breaker/app/src/config/upgrade_definitions.py` | Phase 1 (created) | 4.4 (populated with full definitions) | 4.4 owns the data content |
| `void-breaker/app/src/entities/__init__.py` | Phase 2 (created) | 4.3 (adds ShopNode export) | Append-only, safe |
| `void-breaker/app/src/managers/__init__.py` | Phase 2 (created) | 4.4, 4.5, 4.6 (add exports) | Append-only, safe |
| `void-breaker/app/src/states/__init__.py` | Phase 1 (created) | 4.2 (registers ShopPhase) | Append-only, safe |

**Parallelisation:** Components 4.4, 4.5, and 4.6 can run in parallel (no shared files). Component 4.3 can run in parallel with 4.4/4.5/4.6. Component 4.7 depends on 4.2, 4.3, 4.4, 4.5, and 4.6. Component 4.8 depends on all prior components.

---

## Components

---

#### Component: 4.1 - Human Setup & Shop Assets

**Priority**: Must-have

**Estimated Effort**: 2 hours

**Owner**: Human

**Dependencies**:
- Phase 2 component 2.1: Asset directory structure already established under `assets/sprites/` and `assets/sounds/`

**Features**:
- Create placeholder shop node orb sprites (6 colours) — Human
- Create "Continue" node sprite — Human
- Create `shop_purchase.wav` placeholder — Human
- Create `shop_denied.wav` placeholder — Human

**Description**:
Creates all placeholder visual and audio assets required by the shop phase. Placeholder sprites are simple coloured circle/orb images (can be flat-filled circles with a slight glow or gradient). Audio placeholders are short .wav files (can be simple tones or silent stubs). These are intentionally minimal — Phase 5.1 replaces them with final art.

**Acceptance Criteria**:
- [ ] Six orb sprite files exist at `assets/sprites/shop/`: `orb_weapon.png` (red), `orb_defense.png` (blue), `orb_mobility.png` (green), `orb_economy.png` (gold), `orb_repair.png` (white), `orb_insurance.png` (purple)
- [ ] A "Continue" node sprite exists at `assets/sprites/shop/node_continue.png`
- [ ] `assets/sounds/shop_purchase.wav` exists (16-bit PCM mono, under 500KB)
- [ ] `assets/sounds/shop_denied.wav` exists (16-bit PCM mono, under 500KB)
- [ ] All sprites are 64x64 pixels minimum (Arcade renders them scaled)
- [ ] All files load without errors via `arcade.load_texture()` and `arcade.load_sound()`

**Technical Details**:
- **Files to Create**:
  - `assets/sprites/shop/orb_weapon.png`
  - `assets/sprites/shop/orb_defense.png`
  - `assets/sprites/shop/orb_mobility.png`
  - `assets/sprites/shop/orb_economy.png`
  - `assets/sprites/shop/orb_repair.png`
  - `assets/sprites/shop/orb_insurance.png`
  - `assets/sprites/shop/node_continue.png`
  - `assets/sounds/shop_purchase.wav`
  - `assets/sounds/shop_denied.wav`
- **Key Functions/Classes**: N/A (asset creation only)
- **Human/AI Agent**: All items are Human tasks — these require visual/audio creation tooling outside the codebase
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: Image editor (e.g., GIMP, Photoshop, or programmatic generation via Pillow). Audio editor (e.g., Audacity, bfxr, or programmatic generation via pydub/numpy)

**Detailed Implementation Requirements**:
- **Orb sprites (`assets/sprites/shop/orb_*.png`)**: Each file should be a 64x64 or 128x128 PNG with a transparent background and a filled circle in the designated colour. The colours must be visually distinct: red (#E74C3C), blue (#3498DB), green (#2ECC71), gold (#F1C40F), white (#ECF0F1), purple (#9B59B6). A slight outer glow or soft edge is recommended for visual appeal but not required for placeholders. Consistent sizing across all orbs is mandatory — the shop layout code uses uniform sprite dimensions.
- **Continue node sprite (`assets/sprites/shop/node_continue.png`)**: A 64x64 or 128x128 PNG showing a right-pointing arrow or chevron, bright green or white, with a transparent background. This sprite must be visually distinct from the category orbs so the player immediately recognises it as the "exit shop" action.
- **Audio files (`assets/sounds/shop_purchase.wav`, `assets/sounds/shop_denied.wav`)**: 16-bit PCM mono WAV files. `shop_purchase.wav` should be a short (0.2-0.5s) positive/confirming tone (ascending pitch or cash register sound). `shop_denied.wav` should be a short (0.2-0.3s) negative/error tone (descending pitch or soft buzz). Both files must match the format used by the existing audio stubs from Phase 2.1 (16-bit PCM mono).

**Test Requirements**:
- [ ] Manual testing: Verify all sprites load in an Arcade window without errors
- [ ] Manual testing: Verify all sounds play via `AudioManager.play()` without errors
- [ ] Manual testing: Verify orb colours are visually distinct against a dark background

**Definition of Done**:
- [ ] All 7 sprite files and 2 audio files created and placed in correct directories
- [ ] Assets load without errors in Arcade
- [ ] Documentation created: `docs/components/phase-4-component-4-1-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)

**Notes**:
These are placeholder assets. The retro-minimalist aesthetic means simple geometric shapes are acceptable and even appropriate. Phase 5.1 will replace these with polished versions. The critical requirement is correct file format and directory placement so that subsequent AI Agent components can reference them by path.

---

#### Component: 4.2 - Shop Phase State & Layout

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 4.1: Shop assets must exist for sprite loading (orb textures, continue node texture)
- Phase 1 (1.3): State machine infrastructure — `ShopPhase` stub state exists and must be replaced with full implementation
- Phase 2 (2.7): `CombatPhase` state — must transition to `ShopPhase` on level clear
- Phase 1 (1.5): `InputManager` — ship controls during shop phase
- Phase 1 (1.6): `GameState`, `ShipState` — state passed into shop phase

**Features**:
- Replace `ShopPhase` stub with full implementation — AI Agent
- Generate circular node layout around playfield centre — AI Agent
- Ship physics retained in shop (thrust/rotation) — AI Agent
- Wrap-around disabled in shop phase — AI Agent
- CombatPhase -> ShopPhase transition on level clear — AI Agent
- ShopPhase -> CombatPhase transition on "Continue" — AI Agent

**Description**:
Implements the `ShopPhase` game state that activates between combat levels. The shop presents upgrade nodes in a circular layout around the centre of the playfield. The player's ship starts at the centre and can fly freely using the same thrust/rotation controls from combat, but wrap-around is disabled (ship is clamped to screen bounds). The phase manages transitions in both directions: entering from `CombatPhase` and exiting back to `CombatPhase` with incremented difficulty.

**Acceptance Criteria**:
- [ ] `ShopPhase` replaces the stub from Phase 1 and integrates into the state machine
- [ ] On entering shop, the ship is placed at the playfield centre with zero velocity
- [ ] Ship responds to thrust and rotation controls within the shop
- [ ] Ship does not wrap at screen edges during shop phase (clamped to bounds)
- [ ] Shop nodes are arranged in a circle around the centre (radius configurable)
- [ ] Transition from `CombatPhase` to `ShopPhase` occurs on level clear
- [ ] Transition from `ShopPhase` to `CombatPhase` occurs when the player collides with the "Continue" node or presses Enter
- [ ] On exiting shop, the next combat level starts with incremented difficulty

**Technical Details**:
- **Files to Create/Modify**:
  - **Create**: `void-breaker/app/src/states/shop.py` (replaces stub)
  - **Modify**: `void-breaker/app/src/states/__init__.py` (register `ShopPhase`)
  - **Modify**: `void-breaker/app/src/states/combat.py` (add transition to `ShopPhase` on level clear)
- **Key Functions/Classes**:
  - `ShopPhase` class with state protocol methods (`on_enter`, `on_exit`, `on_update`, `on_draw`, `on_key_press`, `on_key_release`)
  - `ShopPhase._generate_node_layout()` — calculates node positions in a circle
  - `ShopPhase._clamp_ship_to_bounds()` — replaces wrap-around during shop
  - `ShopPhase._check_continue_transition()` — detects continue node collision or Enter key
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade` (SpriteList, Sprite, check_for_collision)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/states/shop.py`**: This is the core shop state. The `on_enter()` method receives the current `GameState` and `ShipState`, places the player ship at `(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)` with velocity zeroed, and calls `_generate_node_layout()` to create `ShopNode` entities arranged in a circle. The circle radius should be approximately 35-40% of the smaller screen dimension so all nodes are reachable without excessive travel. Nodes are evenly spaced around the circle (360 / node_count degrees apart). The "Continue" node is placed at the bottom of the circle (6 o'clock position) or slightly outside the ring. The `on_update(dt)` method applies ship physics (thrust, rotation from `InputManager`) but replaces the wrap logic with clamping: `ship.center_x = clamp(ship.center_x, 0, SCREEN_WIDTH)` and similarly for y. The `on_draw()` method renders the background (starfield), all shop nodes, the player ship, and a HUD overlay showing current currency. The shop phase must also draw text labels on each node (name, level, cost) — this can use `arcade.draw_text()` positioned relative to each node's centre. The `on_exit()` method cleans up shop node entities and prepares the game state for the next combat level (increment `GameState.current_level`, deduct insurance cost via `InsuranceManager` if active).

- **File: `void-breaker/app/src/states/combat.py` (modification)**: In the `CombatPhase` class, the level-clear check (all asteroids destroyed) currently transitions to the next combat level directly. Modify this to transition to `ShopPhase` instead. The transition should pass the current `GameState` and `ShipState` to the shop. After the shop, the `ShopPhase.on_exit()` increments the level and the state machine transitions back to `CombatPhase`. The combat -> shop transition should also play the `level_clear` sound via `AudioManager`.

**Test Requirements**:
- [ ] Unit tests: `ShopPhase` initialises correctly with ship at centre
- [ ] Unit tests: `_generate_node_layout()` produces correct node positions for N nodes in a circle
- [ ] Unit tests: Ship clamp logic prevents position outside screen bounds
- [ ] Integration tests: CombatPhase -> ShopPhase -> CombatPhase transition cycle works
- [ ] Manual testing: Ship controls feel responsive in shop phase
- [ ] Manual testing: All nodes visible and reachable from centre

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-2-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing combat phase functionality
- [ ] Core application still launches and runs post-implementation

**Notes**:
The shop layout should be configurable. Store the circle radius and node positions in `game_config.py` as a `ShopLayoutConfig` dataclass or similar. This allows Phase 5 to adjust the layout for visual polish without modifying `shop.py` logic. The number of nodes is determined by the number of upgrade categories + insurance + continue = approximately 12-14 nodes. Ensure the circle is large enough that adjacent nodes do not overlap (minimum spacing of 2x node sprite width between centres).

---

#### Component: 4.3 - Shop Node Entities & Interaction

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 4.1: Shop orb sprites must exist for texture loading
- 4.2: `ShopPhase` state must exist for node placement and collision checking (but `ShopNode` entity class itself is independent)
- Phase 1 (1.6): `UpgradeDefinition` dataclass from `config/upgrade_definitions.py`
- Phase 2: `EntityManager`, `arcade.Sprite` base class patterns

**Features**:
- `ShopNode` entity class extending `arcade.Sprite` — AI Agent
- Category-coloured orb rendering — AI Agent
- Text labels (name, level/max, cost) — AI Agent
- Pulsing highlight animation on affordable nodes — AI Agent
- Dimmed/crossed indicator on unaffordable or maxed nodes — AI Agent
- Purchase collision logic (deduct currency, apply upgrade, re-centre) — AI Agent
- Denied collision feedback (sound, slight visual shake) — AI Agent

**Description**:
Implements the `ShopNode` entity — a purchasable upgrade node rendered as a coloured orb with text labels. Each node references an `UpgradeDefinition` and calculates its current cost based on the player's current upgrade level. Nodes provide visual feedback on affordability (pulsing if affordable, dimmed if not) and handle the purchase interaction when the player ship collides with them.

**Acceptance Criteria**:
- [ ] `ShopNode` entity renders the correct category-coloured orb sprite
- [ ] Each node displays a text label showing: upgrade name, current level / max level, and cost
- [ ] Affordable nodes pulse with a subtle highlight animation
- [ ] Unaffordable nodes are visually dimmed (reduced alpha or desaturated)
- [ ] Max-level nodes show a "MAX" indicator instead of cost
- [ ] Collision with an affordable node triggers: currency deduction, upgrade application, purchase sound
- [ ] Collision with an unaffordable/maxed node triggers: denied sound, no state change
- [ ] The "Continue" node is a special `ShopNode` variant with no upgrade — collision triggers phase transition

**Technical Details**:
- **Files to Create/Modify**:
  - **Create**: `void-breaker/app/src/entities/shop_node.py`
  - **Modify**: `void-breaker/app/src/entities/__init__.py` (add `ShopNode` export)
- **Key Functions/Classes**:
  - `ShopNode(arcade.Sprite)` — main entity class
  - `ShopNode.__init__(upgrade_definition, current_level, texture_path)` — initialises with upgrade reference
  - `ShopNode.calculate_cost(current_level) -> int` — returns cost for next level: `int(base_cost * (cost_scaling ** current_level))`
  - `ShopNode.can_purchase(currency, current_level) -> bool` — checks affordability and max level
  - `ShopNode.update_visual_state(currency, current_level)` — updates pulsing/dimming based on current state
  - `ShopNode.on_draw_label()` — renders text label below the node sprite
  - `ContinueNode(ShopNode)` — subclass for the "Continue" node with distinct behaviour
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade` (Sprite, draw_text, load_texture)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/entities/shop_node.py`**: The `ShopNode` class extends `arcade.Sprite`. The constructor takes an `UpgradeDefinition` (or `None` for the Continue node), loads the appropriate orb texture from `assets/sprites/shop/` based on the upgrade's category, and stores the upgrade reference. The `calculate_cost()` method implements the cost formula: `int(base_cost * (cost_scaling ** current_level))` where `current_level` is the player's current level for this upgrade (0 = not purchased, cost is `base_cost`; level 1 = cost is `base_cost * cost_scaling`; etc.). The `can_purchase()` method returns `True` only if `currency >= calculate_cost(current_level)` AND `current_level < max_level`. The `update_visual_state()` method is called each frame to adjust the node's visual presentation: if affordable, the node's `alpha` oscillates between 200 and 255 on a sine wave (period ~1 second) to create a subtle pulse; if unaffordable, `alpha` is set to 100 (dimmed); if at max level, `alpha` is 150 with no pulse. The `on_draw_label()` method uses `arcade.draw_text()` to render three lines of text below the sprite: the upgrade name (white, 12pt), the level indicator ("Lv {current}/{max}" or "MAX", 10pt), and the cost ("{cost}c" or "---" if maxed, gold colour, 10pt). For the `ContinueNode` subclass, the texture is `node_continue.png`, no cost/level labels are shown, and the label simply reads "Continue" or "Next Level". The continue node pulses continuously (always "affordable").

- **File: `void-breaker/app/src/entities/__init__.py` (modification)**: Add `ShopNode` and `ContinueNode` to the module's public exports. This is an append-only change — do not modify existing exports.

**Test Requirements**:
- [ ] Unit tests: `ShopNode.calculate_cost()` returns correct values for levels 0-5 with known base_cost and cost_scaling
- [ ] Unit tests: `ShopNode.can_purchase()` returns `True` when affordable and below max, `False` otherwise
- [ ] Unit tests: `ContinueNode` always reports as purchasable (it's a free action)
- [ ] Unit tests: `update_visual_state()` sets correct alpha for affordable/unaffordable/maxed states
- [ ] Manual testing: Labels are readable against the dark background
- [ ] Manual testing: Pulse animation is visible but not distracting

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-3-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing entity system
- [ ] Core application still launches and runs post-implementation

**Notes**:
The `ShopNode` class should be designed for reuse — Phase 5 may add animations, particle effects on purchase, and refined label rendering. Keep the visual methods (pulse, dim, label) as separate methods that Phase 5 can override or extend. The cost formula `int(base_cost * (cost_scaling ** current_level))` means costs grow geometrically. With a `cost_scaling` of 1.5 and `base_cost` of 100, costs would be: 100, 150, 225, 337, 506. Ensure this is well-tested since balance depends on it.

---

#### Component: 4.4 - Upgrade Manager & Stat Application

**Priority**: Must-have

**Estimated Effort**: 8 hours

**Owner**: AI Agent

**Dependencies**:
- Phase 1 (1.6): `ShipState` dataclass with base stats and upgrade level fields, `UpgradeDefinition` dataclass, `UpgradeCategory` enum, `upgrade_definitions.py` (structure created in Phase 1)
- Phase 1 (1.6): `GameState` dataclass with `shields` and `max_shields` fields

**Features**:
- `UpgradeManager` class tracking all upgrade levels — AI Agent
- Effective stat calculation from base + upgrades — AI Agent
- Max level enforcement — AI Agent
- Cost scaling calculation — AI Agent
- Weapon fire rate upgrade — AI Agent
- Weapon damage upgrade — AI Agent
- Weapon projectile speed upgrade — AI Agent
- Weapon spread upgrade — AI Agent
- Defense shields upgrade — AI Agent
- Mobility thrust upgrade — AI Agent
- Mobility turn rate upgrade — AI Agent
- Economy magnet radius upgrade — AI Agent
- Economy currency protection upgrade — AI Agent
- Repairs (shield restore) — AI Agent
- Score bonus multiplier upgrade (optional, per brief item 13) — AI Agent
- Full upgrade definitions data in `upgrade_definitions.py` — AI Agent

**Description**:
Implements the `UpgradeManager` — the central system for tracking purchased upgrades, calculating their effect on ship stats, and enforcing upgrade constraints. This component also populates `upgrade_definitions.py` with the complete set of upgrade definitions (data only — the dataclass structure was created in Phase 1). The `UpgradeManager` is the authority on what upgrades the player has and what effective stats the ship should use.

**Acceptance Criteria**:
- [ ] `UpgradeManager` tracks upgrade levels for all 11 upgrade types (10 categories + score bonus)
- [ ] `apply_upgrade(upgrade_id)` increments the level and recalculates effective stats
- [ ] `get_effective_stat(stat_key) -> float` returns base + (level * effect_per_level)
- [ ] `get_cost(upgrade_id) -> int` returns the correct cost for the next level using geometric scaling
- [ ] `can_upgrade(upgrade_id) -> bool` returns `False` when at max level
- [ ] Repairs upgrade is a one-shot action (restores shields, does not track a permanent level)
- [ ] Score bonus multiplier is tracked and exposed for `ScoreManager` to apply
- [ ] All 11 upgrade definitions exist in `upgrade_definitions.py` with balanced values
- [ ] `recalculate_all_stats()` updates all effective stat fields on `ShipState`

**Technical Details**:
- **Files to Create/Modify**:
  - **Create**: `void-breaker/app/src/managers/upgrade_manager.py`
  - **Modify**: `void-breaker/app/src/config/upgrade_definitions.py` (populate with full upgrade data)
  - **Modify**: `void-breaker/app/src/managers/__init__.py` (add `UpgradeManager` export)
- **Key Functions/Classes**:
  - `UpgradeManager.__init__(ship_state, game_state, upgrade_definitions)` — initialises with references to mutable state
  - `UpgradeManager.apply_upgrade(upgrade_id: str) -> bool` — applies an upgrade, returns `True` on success
  - `UpgradeManager.get_effective_stat(stat_key: str) -> float` — returns computed effective value
  - `UpgradeManager.recalculate_all_stats()` — recalculates all effective stats on `ShipState`
  - `UpgradeManager.get_cost(upgrade_id: str) -> int` — cost for next level
  - `UpgradeManager.can_upgrade(upgrade_id: str) -> bool` — checks max level
  - `UpgradeManager.get_level(upgrade_id: str) -> int` — current level for an upgrade
  - `UpgradeManager.get_all_levels() -> dict[str, int]` — snapshot of all upgrade levels
  - `UpgradeManager.set_levels(levels: dict[str, int])` — bulk set levels (used by insurance retention)
  - `UpgradeManager.apply_repair(amount: float)` — restores shields (special case, not a levelled upgrade)
  - `UpgradeManager.get_score_multiplier() -> float` — returns 1.0 + (score_bonus_level * effect_per_level)
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: None (pure Python logic operating on dataclasses)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/managers/upgrade_manager.py`**: The `UpgradeManager` holds a reference to the `ShipState` (to read base stats and write effective stats), the `GameState` (to read/write shields for repairs), and the list of `UpgradeDefinition` objects (loaded from `upgrade_definitions.py`). Internally, it maintains a `dict[str, int]` mapping `upgrade_id` to current level (all starting at 0). The `apply_upgrade()` method: (1) looks up the `UpgradeDefinition` by `upgrade_id`, (2) checks `current_level < max_level`, (3) increments the level, (4) calls `recalculate_all_stats()`. For the "repairs" upgrade specifically, `apply_repair()` restores shields by a fixed amount (defined in the repair `UpgradeDefinition.effect_per_level` field) capped at `max_shields` — repairs do NOT increment a persistent level. The `recalculate_all_stats()` method iterates all upgrade definitions, computes `base_value + (current_level * effect_per_level)` for each stat key, and writes the result to the corresponding `effective_*` field on `ShipState`. The mapping from `stat_key` to `ShipState` field is direct: e.g., `stat_key="thrust"` maps to `ShipState.effective_thrust = ShipState.base_thrust + (level * effect_per_level)`. For defense shields, the upgrade increases `max_shields` (and current shields by the same delta, so the player immediately gains the new shield capacity). For the score bonus multiplier, the upgrade level is stored but does not modify `ShipState` — instead, `get_score_multiplier()` returns the multiplier for `ScoreManager` to apply. The `set_levels()` method is used by the insurance system to restore upgrade levels after death — it bulk-sets levels and calls `recalculate_all_stats()`.

- **File: `void-breaker/app/src/config/upgrade_definitions.py`**: Phase 1 created the `UpgradeDefinition` dataclass and `UpgradeCategory` enum. This component populates the module with the actual upgrade data. Define a list `ALL_UPGRADES: list[UpgradeDefinition]` containing the following entries (values are starting points for balance tuning):

  | id | category | name | max_level | base_cost | cost_scaling | effect_per_level | stat_key |
  |----|----------|------|-----------|-----------|--------------|------------------|----------|
  | `weapon_fire_rate` | WEAPON | "Fire Rate" | 5 | 80 | 1.5 | 0.5 | `fire_rate` |
  | `weapon_damage` | WEAPON | "Damage" | 5 | 100 | 1.5 | 0.3 | `damage` |
  | `weapon_speed` | WEAPON | "Shot Speed" | 5 | 60 | 1.4 | 50.0 | `projectile_speed` |
  | `weapon_spread` | WEAPON | "Spread Shot" | 3 | 200 | 2.0 | 1.0 | `spread` |
  | `defense_shields` | DEFENSE | "Shields" | 5 | 120 | 1.6 | 25.0 | `max_shields` |
  | `mobility_thrust` | MOBILITY | "Thrust" | 5 | 80 | 1.4 | 60.0 | `thrust` |
  | `mobility_turn` | MOBILITY | "Turn Rate" | 5 | 60 | 1.3 | 30.0 | `turn_rate` |
  | `economy_magnet` | ECONOMY | "Magnet" | 5 | 100 | 1.5 | 30.0 | `magnet_radius` |
  | `economy_protection` | ECONOMY | "Protection" | 1 | 300 | 1.0 | 1.0 | `currency_protection` |
  | `repairs` | REPAIR | "Repairs" | 99 | 50 | 1.3 | 30.0 | `shields` |
  | `score_bonus` | ECONOMY | "Score Bonus" | 3 | 250 | 2.0 | 0.25 | `score_multiplier` |

  The `repairs` entry has `max_level=99` as a sentinel — it is not a levelled upgrade. The `apply_repair()` method handles it as a one-shot shield restore. The `economy_protection` upgrade is binary (level 0 = currency can be destroyed, level 1 = protected). The `weapon_spread` adds extra projectiles per level (level 1 = 2 shots, level 2 = 3 shots, level 3 = 4 shots).

**Test Requirements**:
- [ ] Unit tests: `apply_upgrade()` increments level and recalculates stats correctly
- [ ] Unit tests: `get_cost()` returns correct geometric scaling values for levels 0-5
- [ ] Unit tests: `can_upgrade()` returns `False` at max level
- [ ] Unit tests: `apply_repair()` restores shields capped at `max_shields`
- [ ] Unit tests: `set_levels()` bulk-restores levels and recalculates stats
- [ ] Unit tests: `get_score_multiplier()` returns correct multiplier based on score_bonus level
- [ ] Unit tests: Defense shields upgrade increases both `max_shields` and current `shields`
- [ ] Unit tests: All 11 upgrade definitions load without errors
- [ ] Programmatically executable: Cost scaling produces non-negative, non-zero integers for all valid levels

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-4-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing combat mechanics (ship stats at level 0 match pre-Phase-4 behaviour)
- [ ] Core application still launches and runs post-implementation

**Notes**:
The `stat_key` values in upgrade definitions MUST match the `ShipState` field naming convention. If Phase 1/2 used different field names on `ShipState`, the `recalculate_all_stats()` method must use a mapping dict rather than direct attribute access. Use `getattr`/`setattr` with a validation check against known fields to prevent silent typo bugs. The `weapon_spread` upgrade is special — it does not modify a single float stat but rather tells the projectile system to fire N projectiles in a spread pattern. The `UpgradeManager.get_level("weapon_spread")` return value is used by the firing logic in `PlayerShip.fire()` to determine projectile count.

---

#### Component: 4.5 - Insurance Manager & Death Retention

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- Phase 1 (1.6): `InsuranceState` dataclass with `tier`, `cost_per_level`, `retention_fraction` fields
- Phase 1 (1.6): `InsuranceTier` enum (OFF, BASIC, PREMIUM)
- 4.4: `UpgradeManager` — insurance retention requires reading and setting upgrade levels

**Features**:
- `InsuranceManager` class — AI Agent
- Three insurance tiers: OFF, BASIC, PREMIUM — AI Agent
- Recurring cost deduction per level transition — AI Agent
- Upgrade retention calculation on death — AI Agent
- Insurance purchase/change in shop — AI Agent
- Auto-downgrade to OFF if player cannot afford insurance cost — AI Agent

**Description**:
Implements the `InsuranceManager` — the system that manages the player's insurance tier, deducts recurring insurance costs at each level transition, and calculates which upgrades are retained when the player dies. Insurance is VoidBreaker's strategic risk/reward mechanic: spending currency on insurance reduces available funds for upgrades but protects investment on death.

**Acceptance Criteria**:
- [ ] `InsuranceManager` tracks the current `InsuranceTier` (OFF, BASIC, PREMIUM)
- [ ] Insurance tier can be changed in the shop (upgrade or downgrade)
- [ ] At each level transition, the insurance cost is deducted from currency via `CurrencyManager`
- [ ] If the player cannot afford the insurance cost at level transition, insurance downgrades to OFF
- [ ] On death with BASIC insurance: 50% of upgrade levels are retained (each upgrade level rounded down)
- [ ] On death with PREMIUM insurance: 100% of upgrade levels are retained
- [ ] On death with OFF insurance: 0% of upgrade levels retained (fresh start)
- [ ] Retained upgrade levels are applied via `UpgradeManager.set_levels()`
- [ ] Insurance cost scales with level number (higher levels = more expensive insurance)

**Technical Details**:
- **Files to Create/Modify**:
  - **Create**: `void-breaker/app/src/managers/insurance_manager.py`
  - **Modify**: `void-breaker/app/src/managers/__init__.py` (add `InsuranceManager` export)
- **Key Functions/Classes**:
  - `InsuranceManager.__init__(insurance_state, currency_manager, upgrade_manager)` — initialises with references
  - `InsuranceManager.set_tier(tier: InsuranceTier)` — changes insurance tier
  - `InsuranceManager.get_tier() -> InsuranceTier` — returns current tier
  - `InsuranceManager.get_tier_cost(tier: InsuranceTier, current_level: int) -> int` — returns cost for a tier at a given game level
  - `InsuranceManager.deduct_level_cost(current_level: int) -> bool` — deducts insurance cost at level transition, returns `False` and downgrades if unaffordable
  - `InsuranceManager.calculate_retained_upgrades() -> dict[str, int]` — calculates retained levels based on tier
  - `InsuranceManager.apply_retention()` — applies retained upgrades to `UpgradeManager` after death
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: None (pure Python logic; depends on `CurrencyManager` and `UpgradeManager` interfaces)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/managers/insurance_manager.py`**: The `InsuranceManager` holds a reference to the `InsuranceState` dataclass (which stores `tier`, `cost_per_level`, and `retention_fraction`), the `CurrencyManager` (for deducting costs), and the `UpgradeManager` (for reading/setting upgrade levels). The tier costs are defined as constants or a config dataclass:

  | Tier | Base Cost Per Level | Retention Fraction |
  |------|--------------------|--------------------|
  | OFF | 0 | 0.0 |
  | BASIC | 50 | 0.5 |
  | PREMIUM | 150 | 1.0 |

  The `get_tier_cost()` method calculates the actual cost: `base_cost_per_level * (1 + current_level * 0.1)` — insurance becomes more expensive in later levels (10% increase per level). This ensures insurance is a meaningful ongoing expense that scales with game progression. The `deduct_level_cost()` method is called by the `ShopPhase.on_exit()` during the shop-to-combat transition. It checks if the player can afford the insurance cost (via `CurrencyManager.can_spend(amount)`) — if yes, deducts it; if no, sets the tier to OFF and logs a warning message for the HUD to display ("Insurance lapsed — cannot afford premium"). The `calculate_retained_upgrades()` method reads all current upgrade levels via `UpgradeManager.get_all_levels()`, then for each upgrade: `retained_level = int(current_level * retention_fraction)`. For BASIC (0.5 retention), a level-3 upgrade retains level 1 (`int(3 * 0.5) = 1`), a level-4 retains level 2, etc. For PREMIUM (1.0 retention), all levels are kept as-is. The repairs "upgrade" is excluded from retention — it is a one-shot action with no persistent level. The `apply_retention()` method calls `UpgradeManager.set_levels(retained_levels)` to restore the retained upgrades, which triggers `recalculate_all_stats()`.

**Test Requirements**:
- [ ] Unit tests: `set_tier()` correctly updates the `InsuranceState`
- [ ] Unit tests: `get_tier_cost()` returns correct scaled cost for levels 1, 5, 10, 20
- [ ] Unit tests: `deduct_level_cost()` deducts from currency when affordable
- [ ] Unit tests: `deduct_level_cost()` downgrades to OFF when unaffordable
- [ ] Unit tests: `calculate_retained_upgrades()` with BASIC tier retains 50% (rounded down) for various level combinations
- [ ] Unit tests: `calculate_retained_upgrades()` with PREMIUM tier retains 100%
- [ ] Unit tests: `calculate_retained_upgrades()` with OFF tier retains 0%
- [ ] Unit tests: Repairs upgrade is excluded from retention
- [ ] Programmatically executable: Full cycle — set tier, deduct cost, die, check retention

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-5-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing functionality
- [ ] Core application still launches and runs post-implementation

**Notes**:
The insurance cost deduction happens at the **shop-to-combat transition**, not during the shop phase itself. This is an important timing distinction — the player sees their insurance cost deducted when they leave the shop (pressing Continue), giving them one last chance to downgrade their tier before the cost hits. The `InsuranceManager` does NOT handle the game-over/restart flow directly — the `GameOver` state (Phase 5) will call `InsuranceManager.apply_retention()` when initiating a new run after death. For Phase 4, the retention logic is testable via unit tests even if the GameOver screen integration happens later. The `InsuranceManager.calculate_retained_upgrades()` must be a pure function of the current state — it reads upgrade levels and returns a dict without side effects, so the `GameOver` state can preview what would be retained before committing.

---

#### Component: 4.6 - Currency Manager & Economy Flow

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- Phase 1 (1.6): `GameState` dataclass with `currency` field
- Phase 1 (1.6): `RunStats` dataclass (for cumulative tracking)
- Phase 2 (2.5): Currency pickup collection already awards currency to `GameState.currency` — `CurrencyManager` wraps this

**Features**:
- `CurrencyManager` class centralising all currency operations — AI Agent
- Earn operation (from pickups) — AI Agent
- Spend operation (shop purchases) with validation — AI Agent
- Deduct operation (insurance per-level cost) with validation — AI Agent
- Cumulative tracking for run summary (total earned, total spent) — AI Agent
- Balance validation (cannot go negative) — AI Agent

**Description**:
Implements the `CurrencyManager` — the single authority for all currency transactions in a run. All currency operations (earning from pickups, spending in the shop, insurance deductions) flow through this manager. It validates that balances never go negative and tracks cumulative statistics for the game-over run summary.

**Acceptance Criteria**:
- [ ] All currency modifications go through `CurrencyManager` (no direct `GameState.currency` writes outside this manager)
- [ ] `earn(amount)` increases currency and tracks cumulative earned
- [ ] `spend(amount) -> bool` decreases currency if affordable, returns `False` if not
- [ ] `can_spend(amount) -> bool` checks affordability without modifying state
- [ ] `deduct(amount) -> bool` decreases currency (for insurance), returns `False` if unaffordable
- [ ] Currency balance never goes negative
- [ ] `get_balance() -> int` returns current currency
- [ ] `get_run_stats() -> tuple[int, int]` returns (total_earned, total_spent)

**Technical Details**:
- **Files to Create/Modify**:
  - **Rewrite**: `void-breaker/app/src/managers/currency_manager.py` (refactors and replaces the basic `currency_manager.py` created in Phase 2.5. Phase 2.5 must be complete before 4.6. Phase 2's collision handlers that reference `GameState.currency` directly will be updated by this component to use `CurrencyManager` methods)
  - **Modify**: `void-breaker/app/src/managers/__init__.py` (add `CurrencyManager` export)
- **Key Functions/Classes**:
  - `CurrencyManager.__init__(game_state)` — initialises with reference to `GameState`
  - `CurrencyManager.earn(amount: int)` — adds currency, updates `total_earned`
  - `CurrencyManager.spend(amount: int) -> bool` — spends if affordable, updates `total_spent`
  - `CurrencyManager.can_spend(amount: int) -> bool` — checks without modifying
  - `CurrencyManager.deduct(amount: int) -> bool` — deducts (for insurance), updates `total_spent`
  - `CurrencyManager.get_balance() -> int` — returns `GameState.currency`
  - `CurrencyManager.get_run_stats() -> CurrencyRunStats` — returns cumulative stats
  - `CurrencyRunStats` — dataclass with `total_earned: int`, `total_spent: int`
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: None (pure Python logic operating on `GameState`)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/managers/currency_manager.py`**: The `CurrencyManager` wraps all access to `GameState.currency`. It holds a reference to the `GameState` and maintains two internal counters: `_total_earned: int = 0` and `_total_spent: int = 0`. The `earn()` method adds the given amount to `GameState.currency` and increments `_total_earned`. The `spend()` method checks `GameState.currency >= amount` — if yes, deducts and increments `_total_spent`, returning `True`; if no, returns `False` without modification. The `deduct()` method behaves identically to `spend()` but is a semantic alias for insurance deductions (both track spending). The `can_spend()` method is a read-only check returning `GameState.currency >= amount`. All amount parameters must be validated as positive integers — passing zero or negative amounts should raise a `ValueError`. The `get_run_stats()` method returns a `CurrencyRunStats` dataclass for the game-over summary. The `CurrencyManager` also exposes a `reset()` method called at the start of a new run to zero out `GameState.currency` and both tracking counters. Integration note: Phase 2's currency pickup collection code (in `CombatPhase` or `CollisionSystem`) currently writes directly to `GameState.currency` — this must be refactored to call `CurrencyManager.earn()` instead. This is the only cross-file modification: the collision handler that awards currency from pickups must be updated to use the manager.

- **File: `void-breaker/app/src/managers/__init__.py` (modification)**: Add `CurrencyManager` and `CurrencyRunStats` to the public exports.

**Test Requirements**:
- [ ] Unit tests: `earn()` increases balance and tracks total
- [ ] Unit tests: `spend()` returns `True` and deducts when affordable
- [ ] Unit tests: `spend()` returns `False` and does not modify state when unaffordable
- [ ] Unit tests: `can_spend()` is read-only (balance unchanged)
- [ ] Unit tests: Balance never goes negative after any sequence of operations
- [ ] Unit tests: `get_run_stats()` returns correct cumulative values after mixed earn/spend
- [ ] Unit tests: `earn(0)` and `earn(-1)` raise `ValueError`
- [ ] Unit tests: `reset()` zeroes balance and tracking counters
- [ ] Programmatically executable: Full economy cycle — earn 500, spend 200, spend 400 (should fail), check balance = 300

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-6-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing currency pickup collection (Phase 2 collision handler refactored to use `CurrencyManager`)
- [ ] Core application still launches and runs post-implementation

**Notes**:
The refactoring of Phase 2's direct `GameState.currency` writes is a cross-component dependency. The collision handler in `physics/collisions.py` or `states/combat.py` that currently does `game_state.currency += pickup.value` must be changed to `currency_manager.earn(pickup.value)`. This is a small, targeted change but must be tested to ensure no regression in currency pickup behaviour. The `CurrencyManager` is intentionally simple — it is a thin wrapper with validation. Do not add complex logic here (e.g., currency multipliers belong in `UpgradeManager`, not here).

---

#### Component: 4.7 - Ship Re-Centring & Purchase Flow Polish

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 4.2: `ShopPhase` state must exist (this component modifies it)
- 4.3: `ShopNode` entities must exist (this component integrates purchase collision flow)
- 4.4: `UpgradeManager` must exist (called on purchase)
- 4.5: `InsuranceManager` must exist (insurance node purchase)
- 4.6: `CurrencyManager` must exist (currency deduction on purchase)

**Features**:
- Smooth ship interpolation to centre after purchase (0.3s) — AI Agent
- Invulnerability during interpolation (no node collisions) — AI Agent
- "Continue" node transition to next combat phase — AI Agent
- Optional Enter key shortcut for "Continue" — AI Agent
- Purchase flow orchestration (collision -> validate -> deduct -> apply -> re-centre) — AI Agent
- Insurance node handling in shop — AI Agent

**Description**:
Polishes the complete shop purchase flow by implementing the ship re-centring mechanic and integrating all manager components into a cohesive interaction. When the player collides with a shop node, the system validates the purchase, deducts currency, applies the upgrade, plays audio feedback, and smoothly returns the ship to the centre. This component ties together everything built in 4.2-4.6 into the final shop experience.

**Acceptance Criteria**:
- [ ] After a successful purchase, the ship interpolates smoothly to the playfield centre over 0.3 seconds
- [ ] During re-centring interpolation, node collisions are disabled (no accidental purchases)
- [ ] The interpolation is visually smooth (linear or ease-out curve)
- [ ] The "Continue" node collision triggers: play level_clear sound, transition to `CombatPhase`
- [ ] Pressing Enter during the shop phase is equivalent to colliding with the "Continue" node
- [ ] The full purchase flow works end-to-end: collision -> `CurrencyManager.spend()` -> `UpgradeManager.apply_upgrade()` -> `AudioManager.play('shop_purchase')` -> re-centre
- [ ] Denied flow works: collision on unaffordable/maxed node -> `AudioManager.play('shop_denied')` -> no state change, no re-centre
- [ ] Insurance node works: collision -> `CurrencyManager.spend(insurance_change_cost)` -> `InsuranceManager.set_tier()` -> re-centre
- [ ] After re-centring, node visual states update (purchased node may now be dimmed if maxed)

**Technical Details**:
- **Files to Create/Modify**:
  - **Modify**: `void-breaker/app/src/states/shop.py` (add re-centring logic, purchase flow, Enter key handling)
  - **Modify**: `void-breaker/app/src/entities/shop_node.py` (add collision response method if not already present)
- **Key Functions/Classes**:
  - `ShopPhase._handle_node_collision(node: ShopNode)` — orchestrates the purchase flow
  - `ShopPhase._start_recentre()` — begins the interpolation to centre
  - `ShopPhase._update_recentre(dt)` — updates interpolation each frame
  - `ShopPhase._is_recentring() -> bool` — returns whether ship is mid-interpolation
  - `ShopPhase._handle_continue()` — transitions to next combat phase
  - `ShopPhase.on_key_press()` — handles Enter key for continue shortcut
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade` (for collision detection), `math` (for interpolation)

**Detailed Implementation Requirements**:
- **File: `void-breaker/app/src/states/shop.py` (modification)**: Add a re-centring state machine within `ShopPhase`. New instance variables: `_recentre_active: bool = False`, `_recentre_elapsed: float = 0.0`, `_recentre_duration: float = 0.3`, `_recentre_start_x: float`, `_recentre_start_y: float`. The `_start_recentre()` method captures the ship's current position as the start point and sets `_recentre_active = True`. The `_update_recentre(dt)` method is called from `on_update()` when re-centring is active: it increments `_recentre_elapsed`, calculates a normalized progress `t = min(_recentre_elapsed / _recentre_duration, 1.0)`, applies an ease-out curve `t_eased = 1.0 - (1.0 - t) ** 2`, and interpolates the ship position: `ship.center_x = _recentre_start_x + (centre_x - _recentre_start_x) * t_eased`. When `t >= 1.0`, re-centring completes: set `_recentre_active = False`, snap ship to exact centre, zero ship velocity. During re-centring, the collision check in `on_update()` is skipped (the `if _recentre_active: return` guard at the top of the collision section). The `_handle_node_collision()` method is the central purchase orchestrator. When a collision is detected (via `arcade.check_for_collision_with_list(ship, shop_nodes)`), it identifies the collided node, checks if re-centring is active (skip if so), then branches: for a `ContinueNode`, call `_handle_continue()`; for a regular `ShopNode`, check `node.can_purchase(currency_manager.get_balance(), upgrade_manager.get_level(node.upgrade_id))` — if `True`, call `currency_manager.spend(node.calculate_cost(...))`, `upgrade_manager.apply_upgrade(node.upgrade_id)`, `audio_manager.play('shop_purchase')`, then `_start_recentre()`; if `False`, call `audio_manager.play('shop_denied')` only. For the insurance node, the purchase changes the insurance tier via `InsuranceManager.set_tier()` (cycling OFF -> BASIC -> PREMIUM -> OFF, or a direct tier based on the node). After any successful purchase, call `update_visual_state()` on all nodes to refresh affordability indicators. The Enter key handler in `on_key_press()` calls `_handle_continue()` directly.

- **File: `void-breaker/app/src/entities/shop_node.py` (modification)**: Ensure the `ShopNode` has an `upgrade_id` property that returns the `UpgradeDefinition.id`. Add a `is_insurance_node: bool` property. Add a `is_continue_node: bool` property (always `False` for `ShopNode`, `True` for `ContinueNode`). These properties let `ShopPhase._handle_node_collision()` branch on node type without `isinstance` checks.

**Test Requirements**:
- [ ] Unit tests: Re-centring interpolation reaches exact centre at t=1.0
- [ ] Unit tests: Re-centring blocks node collisions during the interpolation window
- [ ] Unit tests: Ease-out curve produces correct values at t=0, 0.5, 1.0
- [ ] Unit tests: `_handle_node_collision()` calls correct manager methods in sequence for a purchase
- [ ] Unit tests: `_handle_node_collision()` plays denied sound and does not modify state for unaffordable node
- [ ] Unit tests: Enter key triggers `_handle_continue()`
- [ ] Integration tests: Full purchase cycle — collide with node, verify currency deducted, upgrade applied, ship re-centred
- [ ] Manual testing: Re-centring animation feels smooth and natural
- [ ] Manual testing: No accidental double-purchases possible during re-centring

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-4-component-4-7-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-4.md` (max 100 lines for this component)
- [ ] No regression in existing shop state functionality
- [ ] Core application is still working post-implementation

**Notes**:
The 0.3-second re-centring duration is from the solution-design.md spec. This should be stored in `game_config.py` rather than hardcoded, so Phase 5 can tune it. The ease-out curve (`1 - (1-t)^2`) provides a smooth deceleration into the centre position — it is fast at the start and slow near the target, which feels natural. If playtesters find 0.3s too fast or too slow, the value is trivially adjustable. The insurance node interaction in the shop is unique — unlike other upgrades which have discrete levels, insurance cycles through three tiers. Consider implementing the insurance node as three separate nodes (OFF, BASIC, PREMIUM) in the layout, where only the "upgrade" option is highlighted (e.g., if currently OFF, the BASIC node pulses; if currently BASIC, the PREMIUM node pulses). Alternatively, a single insurance node that cycles tiers on each collision. The single-node approach is simpler and recommended for v1.0 — each collision cycles to the next tier.

---

#### Component: 4.8 - E2E Testing & Documentation

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 4.2, 4.3, 4.4, 4.5, 4.6, 4.7: All shop and economy components must be implemented
- Phase 3: Full combat system must be functional for end-to-end testing

**Features**:
- Unit tests for shop node interaction — AI Agent
- Unit tests for upgrade application — AI Agent
- Unit tests for insurance retention — AI Agent
- Unit tests for currency transactions — AI Agent
- Unit tests for cost scaling — AI Agent
- Integration tests for full shop cycle — AI Agent
- Integration tests for combat -> shop -> combat loop — AI Agent
- E2E test scenario: multi-level run with shop usage — AI Agent
- Documentation: component overviews for 4.2-4.7 — AI Agent
- Documentation: `implementation-context-phase-4.md` — AI Agent
- Coverage verification: 30%+ on new modules — AI Agent

**Description**:
Provides comprehensive test coverage for all Phase 4 components and creates all required documentation. Tests focus on verifiable game logic (no rendering tests). The E2E test scenario validates the full game loop including shop interaction, upgrade effects, insurance retention, and currency flow.

**Acceptance Criteria**:
- [ ] All unit tests from components 4.2-4.7 pass
- [ ] Integration test: combat phase clears -> shop phase activates -> player purchases upgrade -> stats change -> continue -> combat phase starts with higher difficulty
- [ ] Integration test: player purchases insurance, plays 3 levels (insurance cost deducted each level), dies, upgrades retained per tier
- [ ] Integration test: player attempts purchase with insufficient currency, is denied, balance unchanged
- [ ] Integration test: cost scaling is correct across 5 upgrade levels for all upgrade types
- [ ] Test coverage is 30%+ on `managers/upgrade_manager.py`, `managers/insurance_manager.py`, `managers/currency_manager.py`, `states/shop.py`, `entities/shop_node.py`
- [ ] Documentation exists for all components

**Technical Details**:
- **Files to Create/Modify**:
  - **Create**: `void-breaker/tests/test_upgrades.py`
  - **Create**: `void-breaker/tests/test_insurance.py`
  - **Create**: `void-breaker/tests/test_currency.py`
  - **Create**: `void-breaker/tests/test_shop.py`
  - **Create**: `docs/components/phase-4-component-4-2-overview.md`
  - **Create**: `docs/components/phase-4-component-4-3-overview.md`
  - **Create**: `docs/components/phase-4-component-4-4-overview.md`
  - **Create**: `docs/components/phase-4-component-4-5-overview.md`
  - **Create**: `docs/components/phase-4-component-4-6-overview.md`
  - **Create**: `docs/components/phase-4-component-4-7-overview.md`
  - **Create**: `docs/implementation-context-phase-4.md`
  - **Modify**: `void-breaker/tests/conftest.py` (add fixtures for UpgradeManager, InsuranceManager, CurrencyManager, ShopPhase)
- **Key Functions/Classes**:
  - `conftest.py`: `upgrade_manager_fixture`, `insurance_manager_fixture`, `currency_manager_fixture`, `shop_phase_fixture`, `sample_upgrade_definitions`, `sample_game_state`, `sample_ship_state`
  - `test_upgrades.py`: Test classes for `UpgradeManager` covering all upgrade types, cost scaling, max level, stat recalculation
  - `test_insurance.py`: Test classes for `InsuranceManager` covering all tiers, cost deduction, retention calculation
  - `test_currency.py`: Test classes for `CurrencyManager` covering earn/spend/deduct/validation
  - `test_shop.py`: Test classes for `ShopPhase` and `ShopNode` covering layout, collision, re-centring, continue node
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `pytest`, `pytest-cov`

**Detailed Implementation Requirements**:
- **File: `void-breaker/tests/test_upgrades.py`**: Organise tests into logical groups. `TestUpgradeApplication`: test that `apply_upgrade()` increments level, recalculates stats, and returns `True`; test that applying at max level returns `False`. `TestCostScaling`: parametrized test that verifies `get_cost()` for all 11 upgrades at levels 0-5. `TestStatRecalculation`: test that `recalculate_all_stats()` produces `effective_X = base_X + (level * effect_per_level)` for each stat. `TestRepairs`: test that `apply_repair()` restores shields capped at `max_shields`. `TestScoreMultiplier`: test that `get_score_multiplier()` returns correct values. `TestSetLevels`: test that `set_levels()` bulk-restores and recalculates. All tests should use pytest fixtures that create `ShipState` and `GameState` with known base values.

- **File: `void-breaker/tests/test_insurance.py`**: `TestInsuranceTiers`: test set/get tier. `TestCostDeduction`: parametrized test for `deduct_level_cost()` at various game levels and tiers. `TestCostDeductionFailure`: test that unaffordable deduction downgrades to OFF. `TestRetentionCalculation`: parametrized test with varied upgrade levels, verifying BASIC retains `int(level * 0.5)`, PREMIUM retains all, OFF retains zero. `TestRetentionExcludesRepairs`: test that the repairs "upgrade" is excluded. `TestApplyRetention`: test that `apply_retention()` calls `UpgradeManager.set_levels()` with correct retained levels.

- **File: `void-breaker/tests/test_currency.py`**: `TestEarn`: test earn adds to balance and tracks total. `TestSpend`: test spend succeeds/fails correctly. `TestCanSpend`: test read-only check. `TestDeduct`: test deduction for insurance. `TestValidation`: test that non-positive amounts raise `ValueError`. `TestRunStats`: test cumulative tracking after mixed operations. `TestReset`: test that reset zeroes everything.

- **File: `void-breaker/tests/test_shop.py`**: `TestShopNodeCost`: test `calculate_cost()` for various levels. `TestShopNodeAffordability`: test `can_purchase()` with various currency/level combinations. `TestShopLayout`: test `_generate_node_layout()` produces correct positions for N nodes in a circle. `TestRecentring`: test interpolation math produces correct positions at t=0, 0.5, 1.0. `TestPurchaseFlow`: integration test mocking managers to verify the full purchase sequence (collision -> spend -> apply -> recentre). `TestDeniedFlow`: test that unaffordable collision triggers denied sound only.

- **File: `docs/implementation-context-phase-4.md`**: Maximum 800 lines total (100 per component max). Summarise: what was built, key design decisions, patterns established, integration points with other phases, known limitations, and upgrade balance values chosen.

**Test Requirements**:
- [ ] `pytest -q --cov=void-breaker/app/src/managers --cov=void-breaker/app/src/states/shop --cov=void-breaker/app/src/entities/shop_node --cov-report=term-missing` reports 30%+ coverage
- [ ] All tests pass: `pytest void-breaker/tests/test_upgrades.py void-breaker/tests/test_insurance.py void-breaker/tests/test_currency.py void-breaker/tests/test_shop.py -v`
- [ ] No test requires an Arcade window or GPU (all logic-only tests)
- [ ] Tests run in under 10 seconds total

**Definition of Done**:
- [ ] All tests written and passing
- [ ] 30%+ coverage on Phase 4 modules
- [ ] `docs/components/phase-4-component-4-2-overview.md` through `phase-4-component-4-7-overview.md` created
- [ ] `docs/implementation-context-phase-4.md` created
- [ ] `black --check` and `isort --check-only` pass on all test files
- [ ] No TODO/FIXME in any test or documentation file
- [ ] Core application still launches and full game loop (combat -> shop -> combat) works

**Notes**:
Test fixtures should create minimal `GameState` and `ShipState` instances with known values, avoiding dependency on Arcade's window system. The `UpgradeManager`, `InsuranceManager`, and `CurrencyManager` are pure logic classes that operate on dataclasses — they do not require Arcade to test. The `ShopPhase` tests may need to mock the state machine and entity manager, but should NOT create an Arcade window. Use the same fixture patterns established in Phase 2 (`conftest.py`). If Phase 2 fixtures do not exist yet (parallel development), create them fresh and document the pattern in `conftest.py` docstrings so other phase tests stay consistent.

---

## Dependency Graph

```
4.1 (Human Setup)
 |
 +---> 4.2 (Shop Phase State)
 |       |
 |       +---> 4.7 (Re-Centring & Polish)
 |                    |
 +---> 4.3 (Shop Nodes) ----> 4.7
 |                              |
 +---> 4.4 (Upgrade Manager) -> 4.7 ---> 4.8 (E2E Testing)
 |                              |
 +---> 4.5 (Insurance Manager)-> 4.7
 |                              |
 +---> 4.6 (Currency Manager) -> 4.7
```

**Parallelisable groups after 4.1:**
- Group A: 4.2, 4.3, 4.4, 4.5, 4.6 (all independent)
- Group B: 4.7 (depends on Group A)
- Group C: 4.8 (depends on all)

---

## Balance & Tuning Notes

The upgrade costs and effects in component 4.4 are starting values. The following design principles guided the initial balance:

1. **Early upgrades are cheap, late upgrades are expensive**: Geometric scaling (1.3x-2.0x) ensures early levels are accessible and late levels require meaningful currency investment.
2. **Weapon upgrades are moderately priced**: Fire rate and damage are the most impactful upgrades and are priced accordingly (80-100 base cost).
3. **Economy upgrades are expensive one-time investments**: Magnet (100 base) and protection (300 flat) are priced high because they compound over the entire run.
4. **Insurance scales with game progression**: The 10% per-level cost increase means insurance becomes a genuine burden in late game, forcing players to decide whether the protection is worth the escalating cost.
5. **Repairs are intentionally cheap but scale**: At 50 base cost with 1.3x scaling, early repairs are affordable. Repeated repairs become expensive, discouraging repair-spam as a substitute for skill.
6. **Score bonus is a luxury**: At 250 base cost with 2.0x scaling, the score multiplier is expensive and trades direct power for points. Only relevant for score chasers.

These values will be tuned during Phase 4 playtesting and can be adjusted in `config/upgrade_definitions.py` without code changes.
