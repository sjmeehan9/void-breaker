# Phase 5: Polish & UX — Component Breakdown

Version: 1.0
Date: 2026-02-20
Owner: Tech Lead (Phase 5)
Status: Complete

---

## Phase Overview

Phase 5 transforms VoidBreaker from a functional game into a polished, release-quality experience. It implements all remaining UI screens (main menu, how-to-play, settings, high scores, game over), the pause system, practice/training mode, complete audio integration (all 16 sound effects), particle effects, visual polish, accessibility features, and difficulty presets. After this phase, a new player can launch the game, navigate menus, understand controls, adjust settings, play through the full game loop with satisfying audio-visual feedback, pause/resume, die with a polished game over sequence, and view their high score on the leaderboard -- all without consulting external documentation.

**Dependencies**: Phase 4 complete (full game loop with shop, upgrades, insurance, economy).

**Cross-Phase Contracts (Phase 5 depends on from Phase 4)**:
- Full game loop: CombatPhase -> ShopPhase -> CombatPhase -> ... -> GameOver is functional
- `PersistenceManager` exists with JSON read/write, atomic save, schema versioning
- `AudioManager` exists with `play()` method and placeholder sound loading
- `UpgradeManager`, `InsuranceManager`, `CurrencyManager`, `ScoreManager` all exist and are functional
- `InputManager` exists with configurable key bindings
- `GameState`, `ShipState`, `DifficultyParams`, `HighScoreEntry`, `GameSettings` dataclasses exist
- `EntityManager` with typed `SpriteList` collections exists
- Stub states exist for: `MainMenuState`, `HowToPlayState`, `HighScoresState`, `SettingsScreen`, `GameOver` (basic), `Pause`
- `difficulty_tables.py` exists with per-level scaling parameters

**What Phase 5 delivers to Phase 6**:
- Complete, polished game ready for packaging
- All assets final (no placeholders remain)
- All UI screens functional and navigable
- `scripts/evals.py` passes (no TODO/FIXME)

---

## Component Summary

| Component | Name | Owner | Effort | Priority | Key Files |
|-----------|------|-------|--------|----------|-----------|
| 5.1 | Human Setup & Final Assets | Human | 8 hours | Must-have | `assets/sprites/*`, `assets/sounds/*`, `assets/fonts/*` |
| 5.2 | Main Menu & Navigation System | AI Agent | 6 hours | Must-have | `states/main_menu.py`, `rendering/menu_renderer.py` |
| 5.3 | How-to-Play & High Scores Screens | AI Agent | 4 hours | Must-have | `states/how_to_play.py`, `states/high_scores.py` |
| 5.4 | Settings Screen & Accessibility | AI Agent | 6 hours | Must-have | `states/settings_screen.py` |
| 5.5 | Game Over Screen & High Score Entry | AI Agent | 5 hours | Must-have | `states/game_over.py` |
| 5.6 | Pause System | AI Agent | 4 hours | Must-have | `states/pause.py` |
| 5.7 | Audio Integration & Particle Effects | AI Agent | 7 hours | Must-have | `audio/audio_manager.py`, `rendering/particle_system.py` |
| 5.8 | Visual Polish & Transitions | AI Agent | 5 hours | Should-have | `rendering/transitions.py`, `rendering/hud.py` |
| 5.9 | Difficulty Presets Integration | AI Agent | 4 hours | Must-have | `config/difficulty_tables.py`, `persistence/schemas.py` |
| 5.10 | Practice/Training Mode | AI Agent | 4 hours | Should-have | `states/main_menu.py`, `states/combat.py` |
| 5.11 | E2E Testing & Documentation | AI Agent | 6 hours | Must-have | `tests/test_phase5_*.py`, `docs/implementation-context-phase-5.md` |

**Serialisation constraints**: Components 5.2 and 5.10 both modify `states/main_menu.py`. Component 5.10 must execute after 5.2. Components 5.7 and 5.8 both modify `rendering/particle_system.py` -- 5.8 must execute after 5.7. Component 5.9 modifies `config/difficulty_tables.py` which is read by 5.10 -- 5.10 must execute after 5.9.

---

## Components

---

### Component: 5.1 - Human Setup & Final Assets

**Priority**: Must-have

**Estimated Effort**: 8 hours

**Owner**: Human

**Dependencies**:
- Phase 4 complete: all gameplay functional with placeholder assets
- No internal Phase 5 dependencies -- this is the gating component

**Features**:
- Create all final sprite assets -- Human
- Create all 16 sound effect .wav files -- Human
- Source or create font assets -- Human
- Organise assets into correct directory structure -- Human
- Verify all assets load without errors in Arcade -- Human

**Description**:
This is the largest human task in the entire project. All remaining game art, all 16 sound effects from the solution-design.md audio catalogue, and font assets must be created or sourced. Every placeholder asset used in Phases 1-4 is replaced with a final, original asset. This component gates all subsequent Phase 5 work -- audio integration (5.7) and visual polish (5.8) cannot proceed meaningfully without real assets.

**Acceptance Criteria**:
- [ ] All sprite assets listed below exist in `assets/sprites/` as PNG files
- [ ] All 16 sound effects listed below exist in `assets/sounds/` as 16-bit PCM mono WAV files (under 500KB each)
- [ ] At least one font file exists in `assets/fonts/` suitable for HUD, menus, and UI text
- [ ] All assets are original (no copied art, audio, or branding from any existing game)
- [ ] Assets load without errors when the game launches (manual verification)
- [ ] Visual style is high-contrast retro arcade: dark background, bright ships/projectiles/pickups

**Technical Details**:
- **Files to Create**:
  - `assets/sprites/ship.png` -- Player ship sprite (facing up at angle 0). Recommended size: 64x64 px with transparency.
  - `assets/sprites/ship_thrust.png` -- Player ship with thrust flame visible (same dimensions as ship.png).
  - `assets/sprites/asteroid_large.png` -- Large asteroid. Recommended: 96x96 px.
  - `assets/sprites/asteroid_medium.png` -- Medium asteroid. Recommended: 48x48 px.
  - `assets/sprites/asteroid_small.png` -- Small asteroid. Recommended: 24x24 px.
  - `assets/sprites/enemy_basic.png` -- Basic Shooter enemy ship. Recommended: 48x48 px.
  - `assets/sprites/enemy_aggressive.png` -- Aggressive enemy ship (visually distinct from basic). Recommended: 48x48 px.
  - `assets/sprites/projectile_player.png` -- Player projectile. Recommended: 8x16 px, bright colour. File renamed from Phase 2 placeholder `projectile.png` -- all Phase 2 code references must be updated to use `projectile_player.png` at this point.
  - `assets/sprites/projectile_enemy.png` -- Enemy projectile (visually distinct from player). Recommended: 8x16 px, contrasting colour.
  - `assets/sprites/pickup_currency.png` -- Currency pickup (crystal/gem shape). Recommended: 24x24 px, gold/yellow.
  - `assets/sprites/pickup_buff_heal.png` -- Heal buff pickup. Recommended: 24x24 px, green.
  - `assets/sprites/pickup_buff_shield.png` -- Shield buff pickup. Recommended: 24x24 px, blue.
  - `assets/sprites/pickup_buff_damage.png` -- Damage boost buff pickup. Recommended: 24x24 px, red.
  - `assets/sprites/pickup_buff_speed.png` -- Speed boost buff pickup. Recommended: 24x24 px, cyan.
  - `assets/sprites/shop/orb_weapon.png` -- Shop node orb: weapons (red). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/orb_defense.png` -- Shop node orb: defense (blue). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/orb_mobility.png` -- Shop node orb: mobility (green). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/orb_economy.png` -- Shop node orb: economy (gold). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/orb_repair.png` -- Shop node orb: repairs (white). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/orb_insurance.png` -- Shop node orb: insurance (purple). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/shop/node_continue.png` -- Shop "Continue" node (arrow or distinct shape). Recommended: 48x48 px. Replaces Phase 4 placeholder.
  - `assets/sprites/particle_dot.png` -- Small particle sprite for explosion/thrust/sparkle effects. Recommended: 8x8 px, white (tinted by code).
  - `assets/sprites/ui_panel.png` -- UI background panel for menus/overlays. 9-slice or fixed size.
  - `assets/sprites/ui_button.png` -- Button background for menu items. Recommended: 200x40 px.
  - `assets/sprites/ui_button_selected.png` -- Selected/highlighted button variant.
  - `assets/sounds/fire.wav` -- Player fire: short, punchy laser/blaster sound.
  - `assets/sounds/hit.wav` -- Player hit/damage: sharp impact sound.
  - `assets/sounds/explode_small.wav` -- Small asteroid explosion: quick pop.
  - `assets/sounds/explode_medium.wav` -- Medium asteroid explosion: mid-range boom.
  - `assets/sounds/explode_large.wav` -- Large asteroid explosion: deep boom.
  - `assets/sounds/enemy_explode.wav` -- Enemy destruction: distinct from asteroid explosions.
  - `assets/sounds/pickup_currency.wav` -- Currency collection: bright, satisfying chime.
  - `assets/sounds/pickup_buff.wav` -- Buff pickup: power-up sound.
  - `assets/sounds/shop_purchase.wav` -- Shop purchase: cash register or confirm tone.
  - `assets/sounds/shop_denied.wav` -- Shop denied: soft buzz or error tone.
  - `assets/sounds/level_clear.wav` -- Level clear: fanfare or ascending tone.
  - `assets/sounds/game_over.wav` -- Game over: descending tone.
  - `assets/sounds/menu_nav.wav` -- Menu navigation: subtle click.
  - `assets/sounds/menu_select.wav` -- Menu selection: confirm tone.
  - `assets/sounds/shield_low.wav` -- Shield low warning: repeating alert tone.
  - `assets/sounds/insurance_deduct.wav` -- Insurance cost deducted: subtle cash register variant.
  - `assets/fonts/game_font.ttf` -- Primary game font (retro/pixel style or clean sans-serif). Used for HUD, menus, all UI text.
- **Key Functions/Classes**: N/A (asset creation, not code)
- **Human/AI Agent**: Entirely Human. AI Agents cannot create visual art or audio assets.
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: None (external tools for art/audio creation are at human discretion)

**Detailed Implementation Requirements**:
- **Sprite assets**: All sprites must be PNG files with transparency (alpha channel). The retro aesthetic means simple, geometric shapes are appropriate -- vector-style or pixel-art style both work. High contrast against dark backgrounds is mandatory. Ship sprite must face "up" (angle 0 in Arcade) so rotation works correctly. All sprite sizes are recommendations; the code will use `scale` to normalise if needed.
- **Sound assets**: All sounds must be 16-bit PCM mono WAV files. Keep each file under 500KB for fast loading. Sounds should be short (0.1-2 seconds) except `level_clear.wav` and `game_over.wav` which may be up to 3 seconds. Synthesis tools (sfxr, Bfxr, ChipTone) are recommended for retro-appropriate sounds. The 16 sounds listed correspond exactly to the audio catalogue in solution-design.md section "Sound Effect Catalogue", with two additional sounds (`shield_low.wav` and `insurance_deduct.wav`) identified during Phase 5 breakdown for complete coverage.
- **Font assets**: At minimum one TTF or OTF font file. Must be licensed for free use (OFL, public domain, or similar). Arcade supports TTF fonts via `arcade.load_font()`. A retro/pixel font is preferred for aesthetic consistency but a clean sans-serif works as a fallback.

**Test Requirements**:
- [ ] Manual testing: Launch game, verify all sprites render without pink/missing texture boxes
- [ ] Manual testing: Trigger each sound event, verify each of the 16 sounds plays audibly and is distinct
- [ ] Manual testing: Verify font renders correctly for HUD text, menu text, and score display

**Definition of Done**:
- [ ] All asset files listed above exist in their respective directories
- [ ] Assets are original (no IP violations)
- [ ] Game launches without asset-loading errors
- [ ] Documentation created: `docs/components/phase-5-component-5-1-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md`

**Notes**:
This component gates all other Phase 5 components. Components 5.2-5.6 can proceed with the existing placeholder assets if necessary (they are primarily code/logic), but 5.7 (audio integration) and 5.8 (visual polish) require real assets to be meaningful. The human should prioritise sound effects first (needed for 5.7) and sprite polish second (needed for 5.8). Font can use a freely available retro font as a quick win.

The audio catalogue specifies 14 named sounds in solution-design.md. This breakdown adds `shield_low.wav` and `insurance_deduct.wav` as two additional sounds to reach 16 total, covering the "shield low warning" and "insurance cost deduction" events that are not explicitly named in the solution-design audio table but are implied by the gameplay systems. If the stakeholder considers only the 14 from the solution-design table as canonical, `shield_low.wav` and `insurance_deduct.wav` can be deferred.

---

### Component: 5.2 - Main Menu & Navigation System

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: Final font asset and UI sprites (can proceed with placeholder assets if 5.1 is incomplete)
- Phase 1: State machine with stub `MainMenuState`
- Phase 1: `InputManager` with key bindings
- Phase 1: `AudioManager` with `play()` method

**Features**:
- Full main menu screen replacing stub -- AI Agent
- Keyboard-driven menu navigation with visual highlight -- AI Agent
- Menu transition animations (fade in/out) -- AI Agent
- Wire all menu options to target states -- AI Agent
- Menu sound effects (navigate, select) -- AI Agent

**Description**:
Replaces the Phase 1 stub `MainMenuState` with a fully functional main menu. The menu displays the game title and five options (New Game, How to Play, Settings, High Scores, Quit) navigable by keyboard (Up/Down to move, Enter/configured key to select). Visual feedback highlights the currently selected option. Menu transitions use a brief fade effect. The menu is the first screen a player sees and sets the tone for the entire experience.

**Acceptance Criteria**:
- [ ] Main menu displays game title and five options: New Game, How to Play, Settings, High Scores, Quit
- [ ] Up/Down arrow keys (or configured keys) move selection highlight between options
- [ ] Enter/configured select key activates the highlighted option
- [ ] "New Game" transitions to game initialisation (difficulty selection if 5.9 is complete, otherwise directly to CombatPhase)
- [ ] "How to Play" transitions to HowToPlayState
- [ ] "Settings" transitions to SettingsScreen
- [ ] "High Scores" transitions to HighScoresState
- [ ] "Quit" exits the application
- [ ] Menu navigation plays `menu_nav.wav`; menu selection plays `menu_select.wav`
- [ ] Returning from any sub-screen restores the main menu with the previous selection preserved

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/main_menu.py` -- Full implementation replacing stub
  - CREATE: `asterax/app/src/rendering/menu_renderer.py` -- Menu rendering utilities (text layout, highlight, title). New file -- no prior phase creates this.
- **Key Functions/Classes**:
  - `MainMenuState` class: `on_enter()`, `on_exit()`, `on_update(dt)`, `on_draw()`, `on_key_press(key, modifiers)`
  - `MainMenuState._menu_options: list[tuple[str, str]]` -- List of (display_text, target_state_name) pairs
  - `MainMenuState._selected_index: int` -- Currently highlighted option index
  - `MainMenuState._navigate(direction: int)` -- Move selection up (-1) or down (+1) with wrapping
  - `MainMenuState._select()` -- Activate current selection, trigger state transition
  - `MenuRenderer.draw_title(text: str, x: float, y: float)` -- Render game title with styling
  - `MenuRenderer.draw_menu_options(options: list[str], selected: int, x: float, y: float, spacing: float)` -- Render option list with highlight on selected
- **Human/AI Agent**: AI Agent implements all code. Human provides font/sprite assets in 5.1.
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade` (text rendering, key constants)

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/main_menu.py`**: Replace the stub implementation with a complete `MainMenuState`. The state stores a list of menu options as `(display_text, target_state_name)` tuples and tracks the currently selected index. `on_enter()` resets any transition animation state and optionally starts a fade-in. `on_key_press()` handles Up/Down for navigation (wrapping at boundaries) and Enter for selection, playing `menu_nav` and `menu_select` sounds via the `AudioManager`. `_select()` reads the target state name from the current option and calls the state machine's transition method. The "Quit" option calls `arcade.close_window()` or `self.window.close()`. `on_draw()` delegates to `MenuRenderer` for title and option rendering. The state should store `_previous_selection` so that returning from a sub-screen preserves the user's last menu position -- set this in `on_enter()` if a return flag is present, otherwise reset to 0.

- **File: `asterax/app/src/rendering/menu_renderer.py`**: Provide utility functions/class for rendering menu screens consistently across all UI states (main menu, pause, settings). `draw_title()` renders the game title ("VoidBreaker" or whatever the final name is) centred near the top of the screen using the game font at a large size. `draw_menu_options()` renders a vertical list of text options, highlighting the selected one with a distinct colour (e.g., bright yellow vs dim white) and optionally a cursor indicator ("> " prefix or underline). Spacing between options should be configurable. This renderer is reused by the pause menu (5.6) and settings screen (5.4), so keep the API generic. Consider using `arcade.Text` objects cached on the class for performance rather than creating new text objects each frame.

**Test Requirements**:
- [ ] Unit tests: `MainMenuState` initialises with 5 menu options
- [ ] Unit tests: Navigation wraps correctly (down from last item goes to first, up from first goes to last)
- [ ] Unit tests: Selection triggers correct state transition for each menu option
- [ ] Manual testing: Menu renders correctly with proper layout and readability
- [ ] Manual testing: Navigation and selection sounds play on correct actions

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-2-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The "New Game" option's behaviour depends on whether 5.9 (difficulty presets) is complete. If 5.9 is not yet implemented, "New Game" transitions directly to CombatPhase with default (classic) difficulty. If 5.9 is complete, "New Game" first presents a difficulty selection prompt. Implement "New Game" with a configurable hook: check if difficulty selection is enabled (a flag or the existence of difficulty presets), and branch accordingly. This prevents rework when 5.9 lands.

Component 5.10 (Practice Mode) adds a "Practice" option to this menu. Design the `_menu_options` list to be easily extensible -- 5.10 will append to it.

---

### Component: 5.3 - How-to-Play & High Scores Screens

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: Font asset (can proceed with placeholder)
- 5.2: `MenuRenderer` utilities for consistent text rendering
- Phase 1: `PersistenceManager` for loading high scores
- Phase 1: `HighScoreEntry` dataclass

**Features**:
- How-to-Play screen with controls diagram -- AI Agent
- How-to-Play gameplay explanation (combat, shop, insurance) -- AI Agent
- High Scores screen with persistent leaderboard display -- AI Agent
- Leaderboard sorted by score, filtered by difficulty -- AI Agent
- Navigation back to main menu from both screens -- AI Agent

**Description**:
Implements two informational screens accessible from the main menu. The How-to-Play screen teaches new players the controls, core gameplay loop (combat, collect currency, shop for upgrades), and the insurance mechanic. The High Scores screen displays the persistent local leaderboard sorted by score descending, showing player name/initials, score, level reached, difficulty, and date. If difficulty presets are active (5.9), the leaderboard can be filtered by difficulty.

**Acceptance Criteria**:
- [ ] How-to-Play screen displays all control bindings (rotate, thrust, fire, brake, pause) reading from current `InputManager` bindings
- [ ] How-to-Play screen explains the core loop: combat -> collect currency -> shop upgrades -> next level
- [ ] How-to-Play screen explains the insurance mechanic briefly
- [ ] High Scores screen displays up to 10 entries sorted by score descending
- [ ] Each entry shows: rank, name/initials, score, level reached, difficulty, date
- [ ] High Scores screen shows "No scores yet" when the leaderboard is empty
- [ ] Both screens return to the main menu on Escape or a "Back" key press
- [ ] If difficulty presets are active, High Scores can filter by difficulty (all / casual / classic / hard)

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/how_to_play.py` -- Full implementation replacing stub
  - MODIFY: `asterax/app/src/states/high_scores.py` -- Full implementation replacing stub
- **Key Functions/Classes**:
  - `HowToPlayState` class: `on_enter()`, `on_draw()`, `on_key_press()`
  - `HowToPlayState._build_controls_text() -> list[str]` -- Generates control descriptions from current InputManager bindings
  - `HowToPlayState._gameplay_sections: list[tuple[str, str]]` -- Static content: (heading, body) pairs
  - `HighScoresState` class: `on_enter()`, `on_draw()`, `on_key_press()`
  - `HighScoresState._load_scores()` -- Loads from PersistenceManager, sorts by score descending
  - `HighScoresState._current_filter: str` -- "all" | "casual" | "classic" | "hard"
  - `HighScoresState._cycle_filter(direction: int)` -- Left/Right keys cycle difficulty filter
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `PersistenceManager`, `InputManager`, `MenuRenderer` from 5.2

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/how_to_play.py`**: Replace the stub with a multi-section informational screen. Section 1 ("Controls") dynamically reads key bindings from the `InputManager` and displays them as a two-column layout: action name on the left, bound key on the right. This ensures the How-to-Play screen always reflects the player's current bindings, even after remapping. Section 2 ("Gameplay") explains the core loop in 3-4 short paragraphs: "Destroy asteroids and enemies to earn currency. Collect currency crystals by flying over them. Between levels, fly into shop nodes to purchase upgrades. Upgrades improve your weapons, defense, mobility, and economy." Section 3 ("Insurance") explains: "Purchase insurance in the shop to protect your upgrades. Basic insurance retains half your upgrades on death. Premium retains all." Section 4 ("Tips") provides 2-3 short tips. Render using `MenuRenderer` for consistent styling. Escape or a dedicated key returns to MainMenu. If content is too long for one screen, implement simple page scrolling (Up/Down to scroll, or multiple pages with Left/Right).

- **File: `asterax/app/src/states/high_scores.py`**: Replace the stub with a leaderboard display. `on_enter()` loads scores from `PersistenceManager` and sorts by score descending. Display the top 10 entries in a table-style layout with columns: Rank (#), Name, Score, Level, Difficulty, Date. If the leaderboard is empty, display "No scores yet -- start a new game!" centred on screen. If difficulty presets are active (check for the existence of multiple difficulty values in stored scores), display a filter indicator at the top (e.g., "Showing: All | [Left/Right to filter]") and allow Left/Right keys to cycle through "all", "casual", "classic", "hard". When filtered, only scores matching the selected difficulty are shown and re-ranked. Escape returns to MainMenu.

**Test Requirements**:
- [ ] Unit tests: `HowToPlayState._build_controls_text()` returns correct strings for default key bindings
- [ ] Unit tests: `HighScoresState._load_scores()` sorts by score descending
- [ ] Unit tests: Difficulty filter correctly filters entries
- [ ] Unit tests: Empty leaderboard produces "No scores yet" state
- [ ] Manual testing: Both screens render correctly and are readable
- [ ] Manual testing: Escape returns to main menu from both screens

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-3-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The How-to-Play screen content is static text (except for key bindings which are dynamic). Keep the text concise -- players want to start playing quickly, not read a manual. Use short paragraphs and bullet points. The High Scores screen should handle the case where `high_scores.json` does not yet exist gracefully (PersistenceManager already returns defaults in this case).

---

### Component: 5.4 - Settings Screen & Accessibility

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: Font asset (can proceed with placeholder)
- 5.2: `MenuRenderer` utilities for consistent rendering
- Phase 1: `PersistenceManager` for reading/writing settings
- Phase 1: `InputManager` for current key bindings
- Phase 1: `GameSettings` dataclass

**Features**:
- Key remapping UI (select action, press new key) -- AI Agent
- Volume controls (master, music, SFX) displayed as bars -- AI Agent
- Fire mode toggle (hold/tap) -- AI Agent
- Autofire toggle -- AI Agent
- Colorblind mode toggle -- AI Agent
- Screen shake setting (off/low/medium) -- AI Agent
- Difficulty preset selection (casual/classic/hard) -- AI Agent (linked to 5.9)
- Immediate persistence of all changes -- AI Agent

**Description**:
Implements the full Settings screen accessible from the main menu and from the pause menu. All game settings are exposed as interactive controls: key remapping, volume sliders, toggle switches, and multi-option selectors. Every change is persisted immediately via `PersistenceManager` so settings survive application restarts. The screen uses a scrollable list of setting categories (Controls, Audio, Visual, Gameplay) with keyboard navigation.

**Acceptance Criteria**:
- [ ] Settings screen displays all configurable options grouped by category
- [ ] Key remapping: player selects an action, screen shows "Press a key...", the next keypress is captured and bound
- [ ] Duplicate key bindings are prevented (if a key is already bound, the old binding is cleared with a warning)
- [ ] Volume controls (master, music, SFX): Left/Right adjusts in 10% increments, displayed as a visual bar
- [ ] Fire mode: toggle between "Hold to Fire" and "Tap to Fire"
- [ ] Autofire: toggle on/off
- [ ] Colorblind mode: toggle on/off
- [ ] Screen shake: cycle through Off / Low / Medium
- [ ] Difficulty preset: cycle through Casual / Classic / Hard (functional after 5.9)
- [ ] All changes are written to `settings.json` immediately on change
- [ ] Escape returns to the previous screen (main menu or pause menu) with all changes saved
- [ ] "Reset to Defaults" option restores all settings to defaults

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/settings_screen.py` -- Full implementation replacing stub
- **Key Functions/Classes**:
  - `SettingsScreenState` class: `on_enter()`, `on_exit()`, `on_update(dt)`, `on_draw()`, `on_key_press(key, modifiers)`
  - `SettingsScreenState._settings_items: list[SettingItem]` -- Ordered list of all configurable settings
  - `SettingItem` dataclass: `name: str`, `category: str`, `type: SettingType` (TOGGLE, SLIDER, KEYBIND, MULTI_OPTION), `current_value`, `options` (for multi-option), `key_in_settings: str`
  - `SettingsScreenState._selected_index: int` -- Currently highlighted setting
  - `SettingsScreenState._is_rebinding: bool` -- True when waiting for key input during remapping
  - `SettingsScreenState._rebinding_action: str` -- Which action is being rebound
  - `SettingsScreenState._adjust_setting(direction: int)` -- Left/Right modifies the current setting
  - `SettingsScreenState._toggle_setting()` -- Enter toggles a boolean setting
  - `SettingsScreenState._start_rebind()` -- Enter on a keybind setting enters rebind mode
  - `SettingsScreenState._complete_rebind(key: int)` -- Captures the new key, updates InputManager and persists
  - `SettingsScreenState._save_settings()` -- Writes current state to PersistenceManager
  - `SettingsScreenState._reset_to_defaults()` -- Restores all settings to factory defaults
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `PersistenceManager`, `InputManager`, `AudioManager` (for volume preview), `MenuRenderer` from 5.2

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/settings_screen.py`**: Replace the stub with a full settings interface. The screen is organised as a vertical list of settings, each rendered as a row with the setting name on the left and the current value/control on the right. Categories (Controls, Audio, Visual, Gameplay) are rendered as non-selectable header rows with distinct styling. Up/Down navigates between settings. Left/Right adjusts value-based settings (volume, multi-option). Enter toggles boolean settings or initiates key rebinding. Key remapping uses a modal sub-state: when `_is_rebinding` is True, the screen displays "Press a key for [Action]..." overlay text and the next `on_key_press()` call (excluding Escape, which cancels) captures the key. If the key is already bound to another action, that action's binding is cleared and a brief warning is shown (e.g., "[Key] was unbound from [Action]"). After rebinding, `InputManager.rebind(action, new_key)` is called and settings are persisted. Volume controls display as `[=====     ] 50%` style bars. All changes call `_save_settings()` immediately, which serialises the current `GameSettings` to JSON via `PersistenceManager.save_settings()`. A "Reset to Defaults" item at the bottom of the list, when selected, restores all settings to their default values (from `GameSettings` defaults), updates the `InputManager`, and persists. The `_return_to` attribute tracks whether to return to the main menu or the pause menu on exit.

**Test Requirements**:
- [ ] Unit tests: `_adjust_setting()` correctly increments/decrements volume in 0.1 steps, clamped to 0.0-1.0
- [ ] Unit tests: `_toggle_setting()` flips boolean values
- [ ] Unit tests: Key rebinding updates `InputManager` and clears duplicate bindings
- [ ] Unit tests: `_reset_to_defaults()` restores all settings to default values
- [ ] Unit tests: Settings round-trip through PersistenceManager (save then load produces identical values)
- [ ] Manual testing: Volume changes are audible immediately (play a test sound on adjust)
- [ ] Manual testing: Key remapping works for all bindable actions and persists across restart

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-4-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The Settings screen must be accessible from both the main menu (5.2) and the pause menu (5.6). Use the `_return_to` attribute to determine where Escape navigates back to. The `SettingsScreenState.on_enter()` should accept a parameter (or read from context) indicating the return destination.

Difficulty preset selection in this screen is a display-only stub until 5.9 is implemented. After 5.9, selecting a difficulty preset modifies the `DifficultyParams` baseline. The UI for selecting difficulty is built here; the backend logic is wired in 5.9.

The colorblind mode toggle sets a flag that is read by the rendering layer (5.8). Screen shake setting is read by the damage feedback system (5.8). These settings take effect only after their respective rendering components are implemented, but the toggle UI and persistence work immediately.

---

### Component: 5.5 - Game Over Screen & High Score Entry

**Priority**: Must-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: Font asset (can proceed with placeholder)
- 5.2: `MenuRenderer` utilities
- Phase 1: `PersistenceManager` for saving high scores
- Phase 2: Basic `GameOver` state (replaced by this component)
- Phase 4: `UpgradeManager`, `InsuranceManager`, `CurrencyManager` for run summary data

**Features**:
- Run summary display (score, level, enemies/asteroids destroyed, currency) -- AI Agent
- Insurance tier used display -- AI Agent
- High score qualification check -- AI Agent
- Initials/name entry UI (keyboard input, 3-10 characters) -- AI Agent
- Save to persistent leaderboard -- AI Agent
- Transition to main menu -- AI Agent

**Description**:
Replaces the basic Phase 2 `GameOver` state with a polished game over screen. Displays a comprehensive run summary showing the player's final score, level reached, enemies destroyed, asteroids destroyed, currency earned, currency spent, and the insurance tier they used. If the player's score qualifies for the top 10 leaderboard, an initials entry prompt appears. After entry (or if the score does not qualify), the screen offers "Return to Menu" or "Play Again" options.

**Acceptance Criteria**:
- [ ] Game over screen displays: final score, level reached, enemies destroyed, asteroids destroyed, currency earned, currency spent, insurance tier
- [ ] All summary data is accurate (matches actual run statistics)
- [ ] If score qualifies for top 10, initials entry prompt appears
- [ ] Initials entry accepts 3-10 alphanumeric characters via keyboard
- [ ] Enter confirms initials; Backspace deletes last character
- [ ] High score is saved to `high_scores.json` via PersistenceManager after initials entry
- [ ] If score does not qualify, a message indicates this ("Score does not qualify for leaderboard")
- [ ] After summary/entry, menu offers "Play Again" and "Return to Menu"
- [ ] "Play Again" starts a new game; "Return to Menu" goes to MainMenuState
- [ ] `game_over.wav` plays on entering the game over screen

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/game_over.py` -- Full implementation replacing Phase 2 basic version
- **Key Functions/Classes**:
  - `GameOverState` class: `on_enter()`, `on_exit()`, `on_update(dt)`, `on_draw()`, `on_key_press(key, modifiers)`
  - `GameOverState._run_summary: RunSummary` -- Dataclass or dict containing all run stats
  - `GameOverState._qualifies_for_leaderboard: bool` -- Checked on enter
  - `GameOverState._entering_name: bool` -- True when in initials entry mode
  - `GameOverState._name_buffer: str` -- Characters entered so far
  - `GameOverState._check_qualification() -> bool` -- Compares score against current top 10
  - `GameOverState._submit_high_score()` -- Creates `HighScoreEntry`, saves via PersistenceManager
  - `GameOverState._phase: str` -- "summary" | "name_entry" | "options" (sub-state tracking)
  - `RunSummary` dataclass: `score: int`, `level_reached: int`, `enemies_destroyed: int`, `asteroids_destroyed: int`, `currency_earned: int`, `currency_spent: int`, `insurance_tier: str`
- **Human/AI Agent**: AI Agent
- **Database Changes**: None (writes to existing high_scores.json)
- **API Endpoints**: None
- **Dependencies**: `PersistenceManager`, `RunStats` from `GameState`, `InsuranceManager`, `MenuRenderer`

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/game_over.py`**: Replace the Phase 2 basic game over screen with a multi-phase screen. The state progresses through three sub-phases: "summary" (display run stats), "name_entry" (if qualified, capture initials), and "options" (Play Again / Return to Menu). `on_enter()` receives the run summary data from the `GameState.run_stats` (which must be accumulated during gameplay by the combat phase -- score, enemies destroyed, asteroids destroyed are tracked by `ScoreManager`; currency earned/spent by `CurrencyManager`; insurance tier by `InsuranceManager`). The summary phase renders all stats in a clean two-column layout (label: value). After a brief delay or keypress, if the score qualifies (top 10 by score), transition to name_entry. In name_entry, display "Enter your name:" with the current buffer and a blinking cursor. Accept A-Z, 0-9, and Backspace. Minimum 3 characters required; Enter is ignored until 3 characters are entered. Maximum 10 characters. On Enter with valid name, create a `HighScoreEntry` with all fields populated (score, level, difficulty from current `GameSettings.difficulty`, enemies_destroyed, currency stats, ISO 8601 date from `datetime.now().isoformat()`), save via `PersistenceManager.save_high_score(entry)`, and transition to "options". The options phase shows "Play Again" and "Return to Menu" with keyboard navigation identical to main menu. Play `game_over.wav` on `on_enter()`.

**Test Requirements**:
- [ ] Unit tests: `_check_qualification()` returns True when score exceeds the 10th entry, False otherwise
- [ ] Unit tests: `_check_qualification()` returns True when fewer than 10 entries exist
- [ ] Unit tests: Name buffer accepts only alphanumeric characters and limits to 10
- [ ] Unit tests: `_submit_high_score()` creates a correctly populated `HighScoreEntry`
- [ ] Unit tests: Run summary data is accurately reflected (mock `GameState.run_stats`)
- [ ] Manual testing: Full game over flow from death through summary, name entry, and menu return

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-5-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The `RunSummary` dataclass may already exist as `RunStats` in the `GameState` from Phase 2. If so, extend it with any missing fields (insurance_tier, currency_earned, currency_spent) rather than creating a duplicate. Check the Phase 2 implementation for the existing structure.

The "Play Again" option should start a completely fresh run (reset all state) using the same difficulty setting. It should not carry over any state from the previous run (even with insurance -- insurance only applies within a run, not across runs per the brief: "every run starts completely fresh").

---

### Component: 5.6 - Pause System

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 5.2: `MenuRenderer` utilities
- 5.4: Settings screen (accessible from pause menu)
- Phase 1: State machine with overlay stack support

**Features**:
- Pause overlay state that freezes all game logic -- AI Agent
- Pause menu (Resume, Restart Run, Settings, Exit to Menu) -- AI Agent
- Triggered by configured pause key (default: Escape) -- AI Agent
- Freeze/resume all entities, timers, and spawners -- AI Agent
- Visual overlay (semi-transparent background darken) -- AI Agent

**Description**:
Implements the pause system as a state stack overlay that can activate during both CombatPhase and ShopPhase. When triggered, all game logic (entity updates, physics, spawning, timers) freezes instantly. A semi-transparent overlay darkens the game view, and a pause menu appears with four options: Resume, Restart Run, Settings, Exit to Menu. Resume restores the game state exactly as it was. Restart begins a new run. Settings opens the SettingsScreen (which returns to the pause menu, not the main menu). Exit to Menu discards the current run and returns to MainMenuState.

**Acceptance Criteria**:
- [ ] Pressing the pause key (default: Escape) during combat or shop activates the pause overlay
- [ ] All game logic freezes immediately on pause (entities stop moving, timers stop, spawners stop)
- [ ] Resume restores game state exactly (no position jumps, no timer skips, no lost entities)
- [ ] Restart Run starts a completely fresh run (confirmation prompt recommended but not required)
- [ ] Settings opens the SettingsScreen, which returns to the pause menu on exit
- [ ] Exit to Menu returns to MainMenuState, discarding the current run
- [ ] The game world is visible behind the pause overlay (darkened/dimmed)
- [ ] Pause menu is navigable by keyboard (Up/Down, Enter)
- [ ] Pressing the pause key again while paused resumes the game (shortcut for Resume)

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/pause.py` -- Full implementation replacing stub
  - MODIFY: `asterax/app/src/states/combat.py` -- Add pause trigger on key press (minor modification)
  - MODIFY: `asterax/app/src/states/shop.py` -- Add pause trigger on key press (minor modification)
- **Key Functions/Classes**:
  - `PauseState` class: `on_enter()`, `on_exit()`, `on_update(dt)`, `on_draw()`, `on_key_press(key, modifiers)`
  - `PauseState._menu_options: list[tuple[str, str]]` -- [(display_text, action_name)]
  - `PauseState._selected_index: int`
  - `PauseState._resume()` -- Pops pause state from stack, resumes underlying state
  - `PauseState._restart()` -- Clears state stack, initialises new game
  - `PauseState._open_settings()` -- Pushes SettingsScreen onto stack with return_to=pause
  - `PauseState._exit_to_menu()` -- Clears state stack, transitions to MainMenuState
  - `PauseState._draw_overlay()` -- Renders semi-transparent dark rectangle over game view
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: State machine overlay stack (Phase 1), `MenuRenderer` (5.2), `InputManager` (Phase 1)

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/pause.py`**: Replace the stub with a full overlay state. The pause state is pushed onto the state stack (not a state transition), so the underlying state (CombatPhase or ShopPhase) remains on the stack and does not receive `on_exit()`. Since the pause state is an overlay, `on_draw()` must first call the underlying state's `on_draw()` to render the game world, then draw a semi-transparent dark rectangle (e.g., `arcade.draw_lrtb_rectangle_filled()` with RGBA `(0, 0, 0, 150)` covering the full window), then draw the pause menu on top. The underlying state's `on_update()` is NOT called while paused -- the state machine must skip update calls for states below an overlay. `on_enter()` records the paused state for Resume to return to. Menu navigation uses the same pattern as MainMenuState (Up/Down, Enter, wrapping). Resume pops the PauseState from the stack. Restart clears the stack and pushes a fresh game init. Settings pushes `SettingsScreenState` with `return_to="pause"`. Exit clears the stack and pushes MainMenuState. Pressing the pause key (Escape) while in the pause menu calls `_resume()` as a shortcut.

- **File: `asterax/app/src/states/combat.py`** (minor modification): In `on_key_press()`, add a check for the pause key. When pressed, push `PauseState` onto the state stack. This is a 3-5 line change. Example: `if key == self.input_manager.get_key("pause"): self.state_machine.push_state(PauseState(...))`.

- **File: `asterax/app/src/states/shop.py`** (minor modification): Same as combat.py -- add pause key check in `on_key_press()` to push PauseState. 3-5 line change.

**Test Requirements**:
- [ ] Unit tests: Pushing PauseState does not call underlying state's `on_exit()`
- [ ] Unit tests: Resume pops PauseState and underlying state receives updates again
- [ ] Unit tests: Restart clears the state stack and initialises a fresh game
- [ ] Unit tests: Exit to menu clears the stack and transitions to MainMenuState
- [ ] Manual testing: Pause during combat freezes all entities; resume restores them exactly
- [ ] Manual testing: Pause during shop freezes ship and nodes; resume restores
- [ ] Manual testing: Settings accessed from pause returns to pause menu (not main menu)

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-6-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The state machine's overlay stack must prevent `on_update()` calls from reaching states below the overlay. Verify this behaviour exists in the Phase 1 state machine implementation. If it does not, add a `blocks_update: bool = True` flag to the PauseState that the state machine checks before propagating updates. The `on_draw()` call must still propagate to the underlying state so the game world is visible behind the overlay.

The fixed-timestep accumulator in the game loop must not accumulate time while paused. If the accumulator continues accumulating during pause, resuming will cause a burst of physics steps to "catch up". Ensure the accumulator is frozen or reset on resume. Check the Phase 1 implementation of the game loop for how `is_paused` is handled -- the solution-design.md shows `if self.is_paused: return` at the top of `on_update()`, which may already handle this.

---

### Component: 5.7 - Audio Integration & Particle Effects

**Priority**: Must-have

**Estimated Effort**: 7 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: All 16 sound effect WAV files must exist in `assets/sounds/`
- Phase 1: `AudioManager` skeleton with `play()` method
- Phase 2: Basic explosion particle effects (to be expanded)
- Phase 2-4: All game events that need sound triggers (combat, shop, pickups, level clear, game over)

**Features**:
- Wire all 16 sound effects to correct game events -- AI Agent
- Explosion particle system (3 size variants) -- AI Agent
- Ship thrust trail particles -- AI Agent
- Currency pickup sparkle particles -- AI Agent
- Damage flash effect -- AI Agent
- Shop purchase confirmation burst -- AI Agent
- Particle pooling with 300 hard cap -- AI Agent

**Description**:
Integrates all sound effects with their corresponding game events and implements the full particle effects system. Sound effects are triggered at the exact moment of each event (fire, hit, explosion, pickup, purchase, level clear, game over, menu navigation). The particle system uses a pooling approach with pre-allocated particle sprites, supporting five distinct effect types: explosions (small/medium/large), thrust trail, pickup sparkle, damage flash, and purchase burst. The particle count is hard-capped at 300 to maintain 60fps performance.

**Acceptance Criteria**:
- [ ] All 16 sound effects trigger on their correct game events (see mapping below)
- [ ] Sound volume respects current master and SFX volume settings
- [ ] Explosion particles scale with asteroid/enemy size (small: 5-10 particles, medium: 10-20, large: 20-30)
- [ ] Thrust trail emits particles continuously while thrust is active
- [ ] Currency pickup produces a brief sparkle effect on collection
- [ ] Damage flash produces an impact effect at the damage point
- [ ] Shop purchase produces a brief confirmation burst at the node
- [ ] Total particle count never exceeds 300 (hard cap enforced)
- [ ] Particle system does not cause frame drops at peak (300 particles + full entity load)
- [ ] Particles have finite lifetimes (0.2-1.5 seconds) and are recycled via pooling

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/audio/audio_manager.py` -- Add event-specific convenience methods, verify all sounds load
  - MODIFY: `asterax/app/src/rendering/particle_system.py` -- Full implementation replacing Phase 2 basic version
  - MODIFY: `asterax/app/src/states/combat.py` -- Wire sound triggers to combat events
  - MODIFY: `asterax/app/src/states/shop.py` -- Wire sound triggers to shop events
  - MODIFY: `asterax/app/src/states/game_over.py` -- Wire game_over sound (may already be done in 5.5)
  - MODIFY: `asterax/app/src/entities/player_ship.py` -- Wire fire sound, thrust particle emission
  - MODIFY: `asterax/app/src/entities/asteroid.py` -- Wire explosion sound on destroy
  - MODIFY: `asterax/app/src/entities/enemy_ship.py` -- Wire enemy_explode sound on destroy
  - MODIFY: `asterax/app/src/physics/collisions.py` -- Wire hit sound on ship damage, pickup sounds on collection
- **Key Functions/Classes**:
  - `AudioManager.play_fire()` -- Plays `fire.wav`
  - `AudioManager.play_hit()` -- Plays `hit.wav`
  - `AudioManager.play_explosion(size: str)` -- Plays `explode_small/medium/large.wav` based on size
  - `AudioManager.play_enemy_explode()` -- Plays `enemy_explode.wav`
  - `AudioManager.play_pickup(type: str)` -- Plays `pickup_currency.wav` or `pickup_buff.wav`
  - `AudioManager.play_shop_purchase()` -- Plays `shop_purchase.wav`
  - `AudioManager.play_shop_denied()` -- Plays `shop_denied.wav`
  - `AudioManager.play_level_clear()` -- Plays `level_clear.wav`
  - `AudioManager.play_game_over()` -- Plays `game_over.wav`
  - `AudioManager.play_menu_nav()` -- Plays `menu_nav.wav`
  - `AudioManager.play_menu_select()` -- Plays `menu_select.wav`
  - `ParticleSystem` class: manages pooled particles
  - `ParticleSystem.__init__(max_particles: int = 300)` -- Pre-allocates particle pool
  - `ParticleSystem.emit_explosion(x, y, size: str, color: tuple)` -- Spawns explosion particles
  - `ParticleSystem.emit_thrust(x, y, angle: float)` -- Spawns thrust trail particle
  - `ParticleSystem.emit_sparkle(x, y)` -- Spawns pickup sparkle
  - `ParticleSystem.emit_damage_flash(x, y)` -- Spawns damage impact effect
  - `ParticleSystem.emit_purchase_burst(x, y)` -- Spawns purchase confirmation
  - `ParticleSystem.update(dt: float)` -- Updates all active particles, recycles expired ones
  - `ParticleSystem.draw()` -- Draws all active particles via SpriteList batch draw
  - `Particle` dataclass: `sprite: arcade.Sprite`, `velocity_x/y: float`, `lifetime: float`, `max_lifetime: float`, `active: bool`
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade` (Sound, SpriteList), all entity and collision modules from Phases 2-4

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/audio/audio_manager.py`**: Extend the Phase 1 skeleton with convenience methods for each sound event. Each method calls `self.play(sound_name)` internally. The convenience methods provide a clean API for game code (e.g., `audio.play_explosion("large")` instead of `audio.play("explode_large")`). Verify that `_load_all_sounds()` successfully loads all 16 WAV files from `assets/sounds/`. If a sound file is missing, log a warning and continue (graceful degradation, matching Phase 1 behaviour). Add `play_explosion(size: str)` that maps "small"/"medium"/"large" to the corresponding file stem. All other methods are simple wrappers. Ensure volume is applied correctly: `effective_volume = sfx_volume * master_volume`.

- **File: `asterax/app/src/rendering/particle_system.py`**: Replace the Phase 2 basic explosion particles with a full pooled particle system. Pre-allocate `max_particles` (default 300) `Particle` objects, each containing an `arcade.Sprite` using the `particle_dot.png` texture. All sprites are added to a single `SpriteList` for batch rendering but are hidden (alpha=0 or moved off-screen) when inactive. `emit_*()` methods activate particles from the pool by setting their position, velocity (randomised within a cone for explosions, backward from ship angle for thrust), colour tint, lifetime, scale, and `active=True`. If the pool is exhausted, the oldest active particle is recycled. `update(dt)` iterates all active particles: update position (`x += vx * dt`), decrement lifetime, apply fade (alpha decreases as lifetime approaches 0), deactivate expired particles. `draw()` calls `self.sprite_list.draw()` which batch-renders all visible particles in one GPU call. Effect specifications: Explosion small: 8 particles, speed 50-150 px/s, lifetime 0.3-0.6s, colour from asteroid tint. Explosion medium: 15 particles, speed 80-200, lifetime 0.4-0.8s. Explosion large: 25 particles, speed 100-250, lifetime 0.5-1.0s. Thrust trail: 1 particle per frame while thrusting, speed 30-80 opposite to ship heading, lifetime 0.2-0.4s, colour blue-white. Pickup sparkle: 6 particles, speed 20-60 radial, lifetime 0.3-0.5s, colour gold. Damage flash: 4 particles, speed 40-100, lifetime 0.15-0.3s, colour red-white. Purchase burst: 10 particles, speed 30-80 radial, lifetime 0.3-0.6s, colour matching node category.

- **Sound trigger wiring** (modifications to combat.py, shop.py, collisions.py, entities): Each game event that requires audio is already handled by a callback or method. Add `audio_manager.play_*()` calls at the point of each event. Fire: in `PlayerShip.fire()` or the combat state's fire handler. Hit: in the collision handler for ship damage. Explosion: in `Asteroid.on_destroyed()` and `EnemyShip.on_destroyed()`, passing the size. Pickup: in the collision handler for currency and buff collection. Shop purchase/denied: in `ShopNode.on_purchased()` and the denied handler. Level clear: in the combat state's level completion check. Game over: in `GameOverState.on_enter()`. Menu nav/select: already wired in 5.2. These are small (1-3 line) additions to existing methods.

**Test Requirements**:
- [ ] Unit tests: `AudioManager` loads all 16 sound files without error (mock filesystem with test WAV files)
- [ ] Unit tests: `play_explosion("large")` calls `play("explode_large")` with correct volume
- [ ] Unit tests: `ParticleSystem` pre-allocates exactly `max_particles` particles
- [ ] Unit tests: `emit_explosion()` activates the correct number of particles per size
- [ ] Unit tests: `update()` deactivates particles whose lifetime has expired
- [ ] Unit tests: Pool exhaustion recycles oldest particle (not crash)
- [ ] Unit tests: Total active particles never exceeds `max_particles`
- [ ] Manual testing: All 16 sounds play at correct events during a full game session
- [ ] Manual testing: Particle effects are visually satisfying and do not cause frame drops
- [ ] Programmatic test: Spawn 300 particles, update for 2 seconds, verify all deactivated and recycled

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-7-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The particle pooling approach is critical for performance. Do NOT create and destroy `arcade.Sprite` objects per particle per frame -- this causes GC pressure and frame drops. Pre-allocate all sprites once, add them to a SpriteList, and toggle visibility/position. The SpriteList batch draws all sprites in one GPU call regardless of how many are active.

Sound effect playback should be fire-and-forget. Arcade's `play_sound()` returns a media player instance that can be used for volume control or stopping, but for short SFX we do not need to track them. If multiple sounds play simultaneously (e.g., explosion + pickup), Arcade handles mixing via OpenAL.

This component modifies many files across the codebase (8 files listed). Coordinate carefully with 5.5 (game_over.py), 5.6 (combat.py, shop.py), and 5.8 (particle_system.py) to avoid merge conflicts. 5.7 should be implemented before 5.8 since 5.8 adds additional visual polish on top of the particle system created here.

---

### Component: 5.8 - Visual Polish & Transitions

**Priority**: Should-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1: Final sprite assets for visual polish
- 5.7: Particle system must exist (this component extends it)
- 5.4: Colorblind mode and screen shake settings must be persisted
- Phase 2: HUD renderer exists (to be polished)

**Features**:
- Level transition effects (fade + "Level X" overlay) -- AI Agent
- HUD layout polish and readability improvements -- AI Agent
- Screen shake on damage (respecting off/low/medium setting) -- AI Agent
- Ship damage flash effect (sprite tint) -- AI Agent
- Shop node pulsing/glow animation -- AI Agent
- Colorblind-friendly palette swap -- AI Agent

**Description**:
Adds visual polish across the entire game. Level transitions use a brief fade-to-black with a "Level X" text overlay. The HUD is refined for readability with consistent positioning, colour coding, and icon usage. Screen shake provides visceral feedback on damage, with intensity controlled by settings. Colorblind mode applies an alternative colour palette to all entity sprites, ensuring the game is accessible to players with colour vision deficiency.

**Acceptance Criteria**:
- [ ] Level transitions show a brief "Level X" overlay (1-2 seconds) between combat phases
- [ ] Transition uses a fade effect (fade out, show level text, fade in)
- [ ] HUD elements (shields, score, level, currency) are clearly positioned and readable
- [ ] Screen shake activates on player damage, intensity matches setting (off: no shake, low: subtle, medium: noticeable)
- [ ] Screen shake does not persist (returns to stable within 0.3-0.5 seconds)
- [ ] Ship flashes red/white briefly on taking damage (sprite tint)
- [ ] Shop nodes pulse/glow when affordable (scale oscillation or alpha pulse)
- [ ] Colorblind mode toggle changes entity colours to a distinguishable palette
- [ ] All visual effects work correctly across the full game loop

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/rendering/transitions.py` -- Full implementation (level transition effects)
  - MODIFY: `asterax/app/src/rendering/hud.py` -- Polish layout, add icons, improve readability
  - MODIFY: `asterax/app/src/rendering/particle_system.py` -- Add damage flash as sprite tint (minor extension)
  - MODIFY: `asterax/app/src/states/combat.py` -- Integrate screen shake and level transition
  - MODIFY: `asterax/app/src/entities/shop_node.py` -- Add pulsing animation
  - MODIFY: `asterax/app/src/entities/player_ship.py` -- Add damage flash tint
  - MODIFY: `asterax/app/src/window.py` -- Screen shake viewport offset
- **Key Functions/Classes**:
  - `TransitionEffect` class: manages fade and text overlay
  - `TransitionEffect.start_level_transition(level: int)` -- Begins fade-out, text display, fade-in sequence
  - `TransitionEffect.update(dt: float) -> bool` -- Updates transition state, returns True when complete
  - `TransitionEffect.draw()` -- Renders overlay (black rect with alpha + text)
  - `TransitionEffect.is_active: bool` -- True while transition is playing
  - `ScreenShake` class or function: `trigger(intensity: str)`, `update(dt)`, `get_offset() -> tuple[float, float]`
  - `ColorblindPalette` -- Mapping of default colours to colorblind-safe alternatives
  - `apply_colorblind_palette(sprites: SpriteList, enabled: bool)` -- Swaps entity colour tints
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `arcade`, `GameSettings.screen_shake`, `GameSettings.colorblind_mode`

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/rendering/transitions.py`**: Implement `TransitionEffect` as a self-contained animation controller. The level transition sequence is: (1) fade out over 0.3s (draw a black rectangle with alpha increasing from 0 to 255), (2) hold for 0.8s (full black + "Level X" text centred in white), (3) fade in over 0.3s (alpha decreasing from 255 to 0). Total duration: ~1.4 seconds. The `start_level_transition(level)` method records the target level and starts the timer. `update(dt)` advances the timer and calculates the current phase and alpha. `draw()` renders the overlay rectangle and text. The CombatPhase calls `start_level_transition()` when a level clears and waits until `is_active` is False before spawning the next level's entities. During the transition, no game logic runs (entities are frozen).

- **File: `asterax/app/src/rendering/hud.py`**: Polish the Phase 2 HUD. Position elements consistently: shields bar at top-left (coloured bar: green > yellow > red based on percentage), score at top-centre (large text), level at top-right, currency at top-left below shields (with a small currency icon if available). Use `arcade.Text` objects cached on the HUD class, updated only when values change (lazy rendering per solution-design.md optimisation strategy). Add visual polish: shields bar has a border/outline, score has a slight text shadow for readability, currency amount flashes briefly when it changes.

- **File: `asterax/app/src/window.py`** (screen shake): Implement screen shake as a viewport offset. When triggered, apply a random offset to the camera/viewport position (`self.camera.move()` or manual offset in draw coordinates) that decays exponentially over 0.3-0.5 seconds. Intensity levels: "off" = no offset, "low" = max 3px offset, "medium" = max 8px offset. Read the `screen_shake` setting from `GameSettings`. The `ScreenShake` class tracks current intensity, applies random x/y offsets each frame, and decays toward zero. Reset to zero when shake is complete.

- **Colorblind palette**: Define a `ColorblindPalette` dict mapping default entity colours to deuteranopia-safe alternatives (e.g., red -> orange, green -> blue, using a well-known colourblind palette). When `GameSettings.colorblind_mode` is True, apply colour tints to entity sprites during rendering setup. This can be done by setting `sprite.color` on each entity's sprite to the palette-mapped colour. Apply on state enter and when the setting is toggled.

- **Shop node pulsing**: In `ShopNode.on_update(dt)`, if the node is affordable, oscillate `self.scale` between 1.0 and 1.15 using a sine wave (`1.0 + 0.15 * sin(time * 3.0)`). If not affordable or maxed, keep scale at 1.0 and set `self.alpha` to 128 (dimmed).

**Test Requirements**:
- [ ] Unit tests: `TransitionEffect` progresses through fade-out, hold, fade-in phases with correct timing
- [ ] Unit tests: `ScreenShake.get_offset()` returns (0, 0) when setting is "off"
- [ ] Unit tests: `ScreenShake.get_offset()` decays to near-zero after 0.5 seconds
- [ ] Unit tests: Screen shake intensity scales correctly ("low" max 3px, "medium" max 8px)
- [ ] Unit tests: Colorblind palette maps all entity colours to distinguishable alternatives
- [ ] Manual testing: Level transition looks smooth and text is readable
- [ ] Manual testing: Screen shake feels impactful at "medium" and subtle at "low"
- [ ] Manual testing: Shop nodes visibly pulse when affordable, dim when not

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-8-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
Screen shake must not accumulate. If the player takes damage twice in rapid succession, the shake should reset to peak intensity, not add on top of the previous shake. Implement this by setting `self.current_intensity = max_intensity` on each trigger rather than `self.current_intensity += max_intensity`.

The colorblind palette should use established colourblind-safe palettes (e.g., IBM Design colorblind palette, or Wong 2011 palette). A simple implementation is sprite colour tinting -- Arcade supports `sprite.color = (r, g, b)` which tints the sprite texture. For white or greyscale base textures this works as a full colour replacement; for coloured textures it multiplies, which may need testing.

---

### Component: 5.9 - Difficulty Presets Integration

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 5.2: Main menu "New Game" flow (difficulty selection hook)
- 5.4: Settings screen difficulty selector (UI exists, backend wired here)
- 5.5: Game over screen records difficulty in high score entry
- Phase 1: `DifficultyParams` dataclass and `difficulty_tables.py`
- Phase 3: Tuned difficulty scaling (base values)

**Features**:
- Three difficulty presets (Casual, Classic, Hard) modifying DifficultyParams -- AI Agent
- Difficulty selection on New Game -- AI Agent
- Separate leaderboards per difficulty -- AI Agent
- Settings screen difficulty selector wired to backend -- AI Agent
- Difficulty affects gameplay parameters (asteroid count, enemy aggression, currency, damage) -- AI Agent

**Description**:
Implements three difficulty presets that modify the base `DifficultyParams` used for level scaling. Casual reduces challenge (fewer asteroids, slower enemies, more currency, less damage). Classic uses the default tuning from Phase 3. Hard increases challenge (more asteroids, aggressive enemies, less currency, more damage). Difficulty is selected when starting a new game and stored in settings. High scores are recorded with the difficulty setting and the leaderboard can be filtered by difficulty (implemented in 5.3, data structure added here).

**Acceptance Criteria**:
- [ ] Three presets exist: Casual, Classic, Hard
- [ ] Casual: asteroid count multiplier 0.7, enemy aggression multiplier 0.6, currency drop chance multiplier 1.5, damage received multiplier 0.7
- [ ] Classic: all multipliers 1.0 (unchanged from Phase 3 tuning)
- [ ] Hard: asteroid count multiplier 1.4, enemy aggression multiplier 1.3, currency drop chance multiplier 0.7, damage received multiplier 1.3
- [ ] New Game prompts for difficulty selection (or uses setting default)
- [ ] Selected difficulty modifies `DifficultyParams` before combat starts
- [ ] High score entries include the difficulty field
- [ ] Leaderboard entries can be filtered by difficulty (data support -- UI already in 5.3)
- [ ] Difficulty selection persists in settings

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/config/difficulty_tables.py` -- Add difficulty preset multipliers
  - MODIFY: `asterax/app/src/managers/difficulty_scaler.py` -- Apply preset multipliers to base params
  - MODIFY: `asterax/app/src/states/main_menu.py` -- Add difficulty selection sub-prompt on New Game
  - MODIFY: `asterax/app/src/persistence/schemas.py` -- Ensure HighScoreEntry includes difficulty field
- **Key Functions/Classes**:
  - `DifficultyPreset` enum: `CASUAL`, `CLASSIC`, `HARD`
  - `DIFFICULTY_PRESET_MULTIPLIERS: dict[DifficultyPreset, DifficultyMultipliers]` -- Multiplier sets per preset
  - `DifficultyMultipliers` dataclass: `asteroid_count: float`, `enemy_aggression: float`, `currency_drop_chance: float`, `damage_received: float`, `enemy_spawn_interval: float`
  - `DifficultyScaler.apply_preset(base_params: DifficultyParams, preset: DifficultyPreset) -> DifficultyParams` -- Applies multipliers to base parameters
  - `MainMenuState._show_difficulty_selection()` -- Sub-prompt before starting new game
- **Human/AI Agent**: AI Agent
- **Database Changes**: None (JSON field addition to high score entries)
- **API Endpoints**: None
- **Dependencies**: `DifficultyParams`, `DifficultyScaler`, `PersistenceManager`

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/config/difficulty_tables.py`**: Add `DifficultyPreset` enum and `DifficultyMultipliers` dataclass. Define `DIFFICULTY_PRESET_MULTIPLIERS` as a dict mapping each preset to its multiplier set. Casual multipliers reduce challenge: `asteroid_count=0.7`, `enemy_aggression=0.6`, `currency_drop_chance=1.5`, `damage_received=0.7`, `enemy_spawn_interval=1.4` (slower spawns). Classic is all 1.0. Hard increases challenge: `asteroid_count=1.4`, `enemy_aggression=1.3`, `currency_drop_chance=0.7`, `damage_received=1.3`, `enemy_spawn_interval=0.7` (faster spawns). These multipliers are applied to the per-level base parameters from the existing difficulty tables -- they do not replace the level scaling, they modify its baseline.

- **File: `asterax/app/src/managers/difficulty_scaler.py`**: Add `apply_preset()` method that takes the base `DifficultyParams` for a given level (from the existing difficulty table lookup) and multiplies relevant fields by the preset multipliers. Return a new `DifficultyParams` instance with modified values. Floor asteroid_count to at least 1. Clamp enemy_aggression to 0.0-1.0 range after multiplying. This method is called by the CombatPhase when initialising each level.

- **File: `asterax/app/src/states/main_menu.py`**: Modify the "New Game" action to show a brief difficulty selection sub-prompt before starting the game. This can be a simple overlay with three options (Casual / Classic / Hard) and a description line for each. The currently selected difficulty (from settings) is pre-highlighted. After selection, store the choice in `GameSettings.difficulty` (persist via PersistenceManager) and proceed to game init. Alternatively, the difficulty can default to the settings value and skip the prompt -- implement the prompt but make it skippable (Enter on the pre-selected default proceeds immediately).

- **File: `asterax/app/src/persistence/schemas.py`**: Verify that `HighScoreEntry` includes a `difficulty: str` field. If it was already added in Phase 1 (per the solution-design.md data model), no change is needed. If not, add it with a default of `"classic"` for backward compatibility with any existing entries. The high scores screen (5.3) already supports filtering by this field.

**Test Requirements**:
- [ ] Unit tests: `apply_preset()` with CASUAL produces lower asteroid counts and higher currency drop chance
- [ ] Unit tests: `apply_preset()` with CLASSIC returns unmodified parameters
- [ ] Unit tests: `apply_preset()` with HARD produces higher asteroid counts and lower currency drop chance
- [ ] Unit tests: `apply_preset()` clamps values correctly (asteroid_count >= 1, aggression 0.0-1.0)
- [ ] Unit tests: High score entries include difficulty field
- [ ] Manual testing: Casual gameplay is noticeably easier than Classic
- [ ] Manual testing: Hard gameplay is noticeably harder than Classic
- [ ] Manual testing: Difficulty selection persists across restarts

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-9-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
The multiplier approach is intentional -- it allows the Phase 3 difficulty curve (which was carefully tuned for 30+ levels) to be preserved while shifting its baseline up or down. A multiplicative approach is more robust than replacing the entire difficulty table per preset.

Difficulty presets do NOT affect the shop prices or upgrade effectiveness. They only affect combat parameters (asteroid/enemy spawning, damage, currency drops). This keeps the shop balanced across all difficulties.

---

### Component: 5.10 - Practice/Training Mode

**Priority**: Should-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 5.2: Main menu (Practice option is added to menu)
- 5.9: `DifficultyPreset` and `DifficultyMultipliers` (Practice mode uses modified DifficultyParams)
- Phase 2: `CombatPhase` state (Practice mode reuses it)
- Phase 1: `GameState` dataclass

**Features**:
- Practice mode accessible from main menu -- AI Agent
- Configurable toggles: asteroids only, no enemies, infinite shields, reduced count -- AI Agent
- Reuses CombatPhase with modified DifficultyParams -- AI Agent
- No high score recording in practice mode -- AI Agent
- Infinite lives / respawn after death -- AI Agent
- Return to main menu from practice mode -- AI Agent

**Description**:
Implements a low-stakes sandbox mode for learning controls and mechanics. Accessible from the main menu as a "Practice" option. Before entering practice, the player sees a configuration screen with toggles for: asteroids only (no enemies), infinite shields (cannot die), and reduced asteroid count. Practice mode reuses the existing `CombatPhase` state with modified `DifficultyParams` that reflect the toggle settings. No high scores are recorded. No insurance cost is deducted. The player can return to the main menu at any time via the pause menu.

**Acceptance Criteria**:
- [ ] "Practice" option appears in the main menu (after "New Game")
- [ ] Practice configuration screen shows toggles for: Asteroids Only, Infinite Shields, Reduced Count
- [ ] Asteroids Only: disables all enemy spawning
- [ ] Infinite Shields: shields never decrease (or are set to an extremely high value and auto-replenish)
- [ ] Reduced Count: asteroid count multiplied by 0.5 (half the normal amount)
- [ ] Practice mode uses the CombatPhase state with modified DifficultyParams
- [ ] No high score is recorded when the player dies or exits practice mode
- [ ] No insurance cost is deducted during practice mode
- [ ] Pause menu in practice mode allows returning to main menu
- [ ] Practice mode is visually indicated (e.g., "PRACTICE" text on HUD)

**Technical Details**:
- **Files to Create/Modify**:
  - MODIFY: `asterax/app/src/states/main_menu.py` -- Add "Practice" option to menu
  - CREATE: `asterax/app/src/states/practice_config.py` -- Practice mode configuration screen
  - MODIFY: `asterax/app/src/states/combat.py` -- Accept `is_practice: bool` flag, skip score recording
  - MODIFY: `asterax/app/src/states/game_over.py` -- Skip high score entry in practice mode
  - MODIFY: `asterax/app/src/rendering/hud.py` -- Display "PRACTICE" indicator when in practice mode
- **Key Functions/Classes**:
  - `PracticeConfigState` class: `on_enter()`, `on_draw()`, `on_key_press()`
  - `PracticeConfigState._toggles: dict[str, bool]` -- Toggle states: `asteroids_only`, `infinite_shields`, `reduced_count`
  - `PracticeConfigState._toggle_item(key: str)` -- Flips a toggle
  - `PracticeConfigState._start_practice()` -- Builds modified DifficultyParams and starts CombatPhase
  - `PracticeConfigState._build_practice_params() -> DifficultyParams` -- Creates DifficultyParams with toggles applied
  - `CombatPhase.__init__(..., is_practice: bool = False)` -- Flag to suppress score recording
  - `GameOverState.__init__(..., is_practice: bool = False)` -- Flag to skip high score entry
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `CombatPhase`, `DifficultyParams`, `MainMenuState`, `GameOverState`

**Detailed Implementation Requirements**:
- **File: `asterax/app/src/states/practice_config.py`**: New state for practice mode configuration. Displays a screen with the heading "Practice Mode" and three toggleable options, each showing its current state as [ON] or [OFF]. Up/Down navigates between toggles; Enter or Space flips the selected toggle. A "Start Practice" button at the bottom launches the practice session. `_build_practice_params()` creates a `DifficultyParams` by taking the Level 1 base params and applying modifications: if `asteroids_only`, set `enemy_spawn_enabled=False` and `enemy_count_max=0`; if `infinite_shields`, this is handled by setting a flag on `GameState` (shields are set to 999999 and damage is suppressed); if `reduced_count`, multiply `asteroid_count` by 0.5 (minimum 1). The modified params and `is_practice=True` flag are passed to the CombatPhase when it initialises.

- **File: `asterax/app/src/states/main_menu.py`**: Add "Practice" to the `_menu_options` list, positioned after "New Game". When selected, transition to `PracticeConfigState`. This is a 2-3 line change (append to the options list and add the state mapping).

- **File: `asterax/app/src/states/combat.py`**: Accept an `is_practice: bool = False` parameter. When `is_practice` is True: (1) do not record score to the leaderboard on game over, (2) do not deduct insurance costs, (3) on death, either respawn the ship (reset shields to full, brief invulnerability) instead of triggering game over, or trigger a simplified game over that skips high score entry. The respawn approach is preferred -- set shields to `max_shields` and grant 2 seconds of invulnerability. If `infinite_shields` is active, damage is suppressed entirely. Display "PRACTICE" on the HUD.

- **File: `asterax/app/src/states/game_over.py`**: Accept `is_practice: bool = False`. When True, skip the high score qualification check and name entry phase. Display the run summary but with a note: "Practice Mode -- Score not recorded." Proceed directly to the options phase (Play Again / Return to Menu). "Play Again" in practice mode should return to the practice config screen, not start a regular game.

- **File: `asterax/app/src/rendering/hud.py`**: When `GameState.is_practice` is True, display "PRACTICE" text in a distinct colour (e.g., bright yellow) at the top-centre of the screen, above or alongside the score.

**Test Requirements**:
- [ ] Unit tests: `_build_practice_params()` with all toggles off returns default Level 1 params
- [ ] Unit tests: `_build_practice_params()` with `asteroids_only=True` sets enemy spawn disabled
- [ ] Unit tests: `_build_practice_params()` with `reduced_count=True` halves asteroid count
- [ ] Unit tests: CombatPhase with `is_practice=True` does not record high scores
- [ ] Unit tests: GameOverState with `is_practice=True` skips name entry
- [ ] Manual testing: Practice mode launches with correct toggle effects
- [ ] Manual testing: Infinite shields prevents death
- [ ] Manual testing: Player can return to main menu from practice via pause

**Definition of Done**:
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-5-component-5-10-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-5.md` (max 100 lines)
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
Practice mode reuses the CombatPhase rather than creating a separate game state. This is intentional -- it keeps the code DRY and ensures practice mode benefits from all combat improvements. The only differences are the modified DifficultyParams and the `is_practice` flag.

The "infinite shields" toggle does not literally set shields to infinity (which could cause floating-point issues). Instead, it either suppresses damage entirely (`take_damage()` becomes a no-op) or sets shields to a very high value (999999) and resets them each frame. The suppression approach is cleaner.

Practice mode does not include the shop phase -- the player stays in combat indefinitely. Levels still progress (asteroid count increases) but no shop appears between levels. This simplifies the practice experience and avoids confusion about upgrades in a training context. If the stakeholder wants shop practice, this can be added later.

---

### Component: 5.11 - E2E Testing & Documentation

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 5.1 through 5.10: All Phase 5 components must be complete
- All prior phases: Full game must be functional

**Features**:
- E2E tests for all UI screens -- AI Agent
- E2E tests for settings persistence -- AI Agent
- E2E tests for pause freeze/resume -- AI Agent
- E2E tests for audio triggers -- AI Agent
- Performance test for particle system at peak load -- AI Agent
- E2E test for practice mode -- AI Agent
- Full game loop E2E test -- AI Agent
- Phase 5 documentation -- AI Agent

**Description**:
The final component of Phase 5. Writes comprehensive E2E tests covering all new functionality, verifies no regressions in Phases 1-4 functionality, and produces all required documentation. Tests cover UI navigation, settings persistence, pause system, audio triggers, particle performance, practice mode, and the complete game loop from launch to high score entry. Documentation includes component overviews and the phase implementation context document.

**Acceptance Criteria**:
- [ ] All UI screens (main menu, how-to-play, settings, high scores, game over, pause) navigate correctly
- [ ] Settings persist across simulated application restarts
- [ ] Pause freezes all game logic; resume restores state exactly
- [ ] All audio triggers fire on correct events (verified via mock/spy on AudioManager.play)
- [ ] Particle system maintains 60fps with 300 particles + full entity load
- [ ] Practice mode launches with correct parameters and does not record high scores
- [ ] Full game loop E2E: launch -> menu -> new game -> play 5+ levels -> shop each level -> die -> game over -> high score entry -> verify leaderboard -> return to menu
- [ ] All existing Phase 1-4 tests still pass (no regressions)
- [ ] pytest coverage is 30%+ on all Phase 5 modules
- [ ] `scripts/evals.py` passes (no TODO/FIXME, all public functions have docstrings)
- [ ] All documentation files are created

**Technical Details**:
- **Files to Create/Modify**:
  - CREATE: `asterax/tests/test_phase5_menus.py` -- Tests for main menu, how-to-play, high scores navigation
  - CREATE: `asterax/tests/test_phase5_settings.py` -- Tests for settings screen, persistence, key remapping
  - CREATE: `asterax/tests/test_phase5_pause.py` -- Tests for pause system freeze/resume
  - CREATE: `asterax/tests/test_phase5_game_over.py` -- Tests for game over screen and high score entry
  - CREATE: `asterax/tests/test_phase5_audio.py` -- Tests for audio trigger wiring
  - CREATE: `asterax/tests/test_phase5_particles.py` -- Tests for particle system pooling and performance
  - CREATE: `asterax/tests/test_phase5_difficulty.py` -- Tests for difficulty presets
  - CREATE: `asterax/tests/test_phase5_practice.py` -- Tests for practice mode
  - CREATE: `asterax/tests/test_phase5_e2e.py` -- Full game loop E2E test
  - CREATE: `docs/implementation-context-phase-5.md` -- Phase implementation context
  - CREATE: `docs/components/phase-5-component-5-1-overview.md` through `phase-5-component-5-11-overview.md` -- Component overviews
- **Key Functions/Classes**:
  - Test fixtures: `game_state`, `audio_manager_mock`, `persistence_manager_mock`, `state_machine`, `particle_system`
  - Test classes: `TestMainMenu`, `TestHowToPlay`, `TestHighScores`, `TestSettings`, `TestGameOver`, `TestPause`, `TestAudioTriggers`, `TestParticleSystem`, `TestDifficultyPresets`, `TestPracticeMode`, `TestFullGameLoop`
- **Human/AI Agent**: AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: pytest, all Phase 5 modules

**Detailed Implementation Requirements**:
- **Test files**: Each test file focuses on a specific area of Phase 5 functionality. Tests operate on game logic objects without requiring an Arcade window (headless testing). Use `unittest.mock.patch` or `pytest.monkeypatch` to mock Arcade rendering and sound calls. Test fixtures in `conftest.py` provide pre-configured `GameState`, `PersistenceManager` (using temp directories), `InputManager` (with default bindings), and `AudioManager` (mocked).

- **File: `asterax/tests/test_phase5_menus.py`**: Test `MainMenuState` has 5 options (6 with practice mode). Test navigation wraps correctly. Test each option triggers the correct state transition. Test `HowToPlayState` builds correct controls text from InputManager. Test `HighScoresState` sorts by score, filters by difficulty, handles empty leaderboard.

- **File: `asterax/tests/test_phase5_settings.py`**: Test volume adjustment in 0.1 increments with clamping. Test toggle operations for boolean settings. Test key remapping updates InputManager. Test duplicate key detection clears old binding. Test reset to defaults. Test settings round-trip (save, reload, compare).

- **File: `asterax/tests/test_phase5_pause.py`**: Test PauseState does not call underlying state's on_exit. Test resume pops PauseState. Test that underlying state's on_update is not called while paused. Test restart clears state stack. Test exit to menu transitions correctly.

- **File: `asterax/tests/test_phase5_game_over.py`**: Test run summary data accuracy. Test qualification check against top 10. Test name buffer accepts alphanumeric only, respects 3 char minimum and 10 char max. Test high score entry is saved correctly. Test practice mode skips name entry.

- **File: `asterax/tests/test_phase5_audio.py`**: Test that each game event calls the correct AudioManager method. Mock AudioManager and simulate: fire event -> `play_fire()` called, asteroid destroyed -> `play_explosion(size)` called, etc. Verify all 16 sounds are mapped.

- **File: `asterax/tests/test_phase5_particles.py`**: Test pool pre-allocates exactly max_particles. Test emit methods activate correct number of particles. Test update deactivates expired particles. Test pool exhaustion recycles oldest. Test active count never exceeds max.

- **File: `asterax/tests/test_phase5_difficulty.py`**: Test apply_preset with each preset produces expected parameter modifications. Test value clamping. Test multipliers are multiplicative (not additive).

- **File: `asterax/tests/test_phase5_practice.py`**: Test practice params with each toggle. Test CombatPhase with is_practice does not record scores. Test GameOverState with is_practice skips name entry.

- **File: `asterax/tests/test_phase5_e2e.py`**: Integration test simulating a full game session. Create all managers, initialise state machine, simulate key presses to navigate menu, start game, play through multiple levels (simulate combat by directly destroying asteroids), enter shop, purchase upgrade, continue, die (set shields to 0), verify game over screen, enter initials, verify high score saved, return to menu.

- **File: `docs/implementation-context-phase-5.md`**: Summarise all 11 components in max 100 lines per component. Document key decisions: particle pooling approach, screen shake implementation, colorblind palette choice, practice mode design (reuses CombatPhase), difficulty preset multiplier approach. Note any deviations from the original phase plan.

- **Component overview files**: One per component (11 total) in `docs/components/`. Each file is a brief (50-100 lines) summary of what was built, how it works, and any important implementation details or gotchas.

**Test Requirements**:
- [ ] All test files listed above are created and pass
- [ ] pytest coverage is 30%+ on Phase 5 modules
- [ ] All Phase 1-4 tests still pass (no regressions)
- [ ] `scripts/evals.py` passes
- [ ] `black --check` and `isort --check-only` pass on all Phase 5 code

**Definition of Done**:
- [ ] All E2E tests written and passing
- [ ] 30%+ code coverage on Phase 5 modules
- [ ] No regressions in Phase 1-4 tests
- [ ] `scripts/evals.py` passes (no TODO/FIXME, all public functions have docstrings)
- [ ] `black --check` and `isort --check-only` pass
- [ ] Documentation created: `docs/components/phase-5-component-5-11-overview.md`
- [ ] Documentation created: `docs/implementation-context-phase-5.md`
- [ ] All 11 component overview files created in `docs/components/`
- [ ] Core application is still working post component implementation

**Notes**:
E2E tests that require an Arcade window (rendering, actual sound playback) should be marked with `@pytest.mark.manual` or similar and documented as requiring manual execution. The automated test suite should be fully headless.

The `conftest.py` for Phase 5 tests should extend (not duplicate) the existing test fixtures from earlier phases. Import shared fixtures and add Phase 5-specific ones.

Run the full validation sequence before considering Phase 5 complete:
```bash
source .venv/bin/activate
black --check asterax/app/src/
isort --check-only asterax/app/src/
pytest -q --cov=asterax/app/src --cov-report=term-missing
python scripts/evals.py
```

---

## File Ownership Matrix

This matrix declares which component creates or modifies each file. Components sharing a file CANNOT be parallelised -- they must be sequenced.

| File | Created By | Modified By | Serialisation Notes |
|------|-----------|-------------|---------------------|
| `assets/sprites/*` | 5.1 | -- | Human only |
| `assets/sounds/*` | 5.1 | -- | Human only |
| `assets/fonts/*` | 5.1 | -- | Human only |
| `states/main_menu.py` | Phase 1 | **5.2**, **5.9**, **5.10** | 5.2 first, then 5.9 or 5.10 (serialised) |
| `states/how_to_play.py` | Phase 1 | **5.3** | Independent |
| `states/high_scores.py` | Phase 1 | **5.3** | Independent |
| `states/settings_screen.py` | Phase 1 | **5.4** | Independent |
| `states/game_over.py` | Phase 2 | **5.5**, **5.7**, **5.10** | 5.5 first, then 5.7 or 5.10 (serialised) |
| `states/pause.py` | Phase 1 | **5.6** | Independent |
| `states/combat.py` | Phase 2 | **5.6**, **5.7**, **5.8**, **5.10** | 5.6 first, then 5.7, then 5.8, then 5.10 |
| `states/shop.py` | Phase 4 | **5.6**, **5.7** | 5.6 first, then 5.7 |
| `states/practice_config.py` | **5.10** | -- | New file |
| `audio/audio_manager.py` | Phase 1 | **5.7** | Independent |
| `rendering/particle_system.py` | Phase 2 | **5.7**, **5.8** | 5.7 first, then 5.8 |
| `rendering/transitions.py` | -- | **5.8** | Independent (new implementation) |
| `rendering/hud.py` | Phase 2 | **5.8**, **5.10** | 5.8 first, then 5.10 |
| `rendering/menu_renderer.py` | **5.2** | -- | New file created by 5.2 |
| `config/difficulty_tables.py` | Phase 1 | **5.9** | Independent |
| `managers/difficulty_scaler.py` | Phase 3 | **5.9** | Independent |
| `persistence/schemas.py` | Phase 1 | **5.9** | Independent |
| `entities/player_ship.py` | Phase 2 | **5.7**, **5.8** | 5.7 first, then 5.8 |
| `entities/asteroid.py` | Phase 2 | **5.7** | Independent |
| `entities/enemy_ship.py` | Phase 3 | **5.7** | Independent |
| `entities/shop_node.py` | Phase 4 | **5.8** | Independent |
| `physics/collisions.py` | Phase 2 | **5.7** | Independent |
| `window.py` | Phase 1 | **5.8** | Independent |
| `tests/test_phase5_*.py` | **5.11** | -- | All new files |
| `docs/implementation-context-phase-5.md` | **5.11** | -- | New file |
| `docs/components/phase-5-component-5-*-overview.md` | **5.11** | -- | New files |

## Parallelisation Guide

Based on the file ownership matrix, the following parallelisation is possible:

**Can run in parallel** (no shared files):
- 5.3 (How-to-Play & High Scores) -- independent files
- 5.4 (Settings Screen) -- independent file

**Must be serialised** (shared files):
- 5.2 -> 5.9 -> 5.10 (all modify `main_menu.py`)
- 5.5 -> 5.7 -> 5.10 (all modify `game_over.py`)
- 5.6 -> 5.7 -> 5.8 -> 5.10 (all modify `combat.py`)
- 5.6 -> 5.7 (both modify `shop.py`)
- 5.7 -> 5.8 (both modify `particle_system.py`, `player_ship.py`)
- 5.8 -> 5.10 (both modify `hud.py`)
- 5.11 runs last (depends on all others)

**Recommended execution order**:
1. **5.1** (Human -- gates everything, but code components can start with placeholders)
2. **5.2** (Main Menu -- provides MenuRenderer used by others)
3. **5.3** and **5.4** in parallel (independent files, both depend on 5.2's MenuRenderer)
4. **5.5** and **5.6** in parallel (independent files, both depend on 5.2's MenuRenderer)
5. **5.7** (depends on 5.5 and 5.6 completing their modifications to combat.py, shop.py, game_over.py)
6. **5.8** (depends on 5.7's particle system)
7. **5.9** (depends on 5.2's main_menu.py changes)
8. **5.10** (depends on 5.2, 5.9, and 5.8 for shared files)
9. **5.11** (last -- tests and documents everything)

---

## Cross-Phase Dependency Verification

Before Phase 5 begins, verify these Phase 4 deliverables exist and are functional:

- [ ] `CombatPhase` state is fully implemented with level completion, spawning, scoring
- [ ] `ShopPhase` state is fully implemented with node interaction, purchases, re-centring
- [ ] `UpgradeManager` correctly applies upgrades and tracks levels
- [ ] `InsuranceManager` correctly handles tiers and retention
- [ ] `CurrencyManager` correctly tracks earning, spending, and validation
- [ ] `PersistenceManager` reads/writes settings.json and high_scores.json
- [ ] `InputManager` supports configurable key bindings
- [ ] `AudioManager` has `play()` method and gracefully handles missing files
- [ ] `GameState.run_stats` (or `RunStats`) tracks enemies destroyed, asteroids destroyed, currency earned/spent
- [ ] State machine supports overlay stack (push/pop states) with update blocking
- [ ] `DifficultyParams` dataclass and `difficulty_tables.py` exist with per-level scaling
- [ ] All stub states exist and can be transitioned to without errors

---

End of Phase 5 Component Breakdown.
