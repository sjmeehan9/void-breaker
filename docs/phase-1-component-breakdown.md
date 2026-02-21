# Phase 1: Foundation & Project Skeleton — Component Breakdown

Version: 1.0
Date: 2026-02-20
Owner: Tech Lead (Phase 1)

---

## Phase Overview

Phase 1 establishes the complete development environment, project structure, packaging configuration, and foundational systems that all subsequent phases depend on. It delivers a running Arcade window with a functional state machine shell, persistence layer, settings system, input management, audio skeleton, starfield background, and HUD text rendering. No gameplay yet — this phase produces the architectural scaffold.

**Canonical launch command**: `python -m asterax.app.src.main`

**Phase 1 establishes the following contracts consumed by all later phases:**

- **Directory structure**: Exactly as specified in solution-design.md.
- **State machine protocol**: `on_enter()`, `on_exit()`, `on_update(delta_time)`, `on_draw()`, `on_key_press(key, modifiers)`, `on_key_release(key, modifiers)`.
- **Config pattern**: All tuning parameters live in `game_config.py` as frozen dataclasses. Phases 2-5 add parameters here (serialisation constraint).
- **Persistence pattern**: `PersistenceManager` is the sole interface for reading/writing JSON files. Phases 2+ use it — they do not re-implement file I/O.
- **Input pattern**: `InputManager` holds key-held state and routes events to the active state. States never read `arcade.key` directly for continuous actions.
- **Audio pattern**: `AudioManager.play(name)` is the sole interface for triggering sounds. Graceful no-op on missing files.

---

## Component Summary

| ID | Name | Priority | Effort | Owner | Dependencies |
|----|------|----------|--------|-------|-------------|
| 1.1 | Human Setup & Environment | Must-have | 2h | Human | None |
| 1.2 | Project Structure & Entry Point | Must-have | 4h | AI Agent | 1.1 |
| 1.3 | State Machine | Must-have | 6h | AI Agent | 1.2 |
| 1.4 | Persistence Layer | Must-have | 5h | AI Agent | 1.2 |
| 1.5 | Input Manager | Must-have | 4h | AI Agent | 1.3, 1.4 |
| 1.6 | Game Config & Data Models | Must-have | 5h | AI Agent | 1.2 |
| 1.7 | Audio Manager Skeleton & Rendering Foundation | Must-have | 5h | AI Agent | 1.2, 1.4, 1.6 |
| 1.8 | E2E Testing & Documentation | Must-have | 5h | AI Agent | 1.2-1.7 |

**Parallelisation note**: Components 1.3, 1.4, and 1.6 can execute in parallel after 1.2 completes. Component 1.5 requires both 1.3 and 1.4. Component 1.7 requires 1.2, 1.4, and 1.6. Component 1.8 depends on all prior components.

---

## File Ownership Matrix

This matrix declares every file created or modified per component. Components sharing a file are serialisation constraints and cannot run in parallel.

| File | 1.1 | 1.2 | 1.3 | 1.4 | 1.5 | 1.6 | 1.7 | 1.8 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|
| `pyproject.toml` | C | | | | | | | |
| `.env/.env.local` | C | | | | | | | |
| `.env/.env.example` | C | | | | | | | |
| `.env/.env.test` | C | | | | | | | |
| `.python-version` | C | | | | | | | |
| `asterax/app/src/__init__.py` | | C | | | | | | |
| `asterax/app/src/main.py` | | C | | | | | | |
| `asterax/app/src/window.py` | | C | | | | M | | |
| `asterax/app/src/states/__init__.py` | | C | M | | | | | |
| `asterax/app/src/states/base_state.py` | | | C | | | | | |
| `asterax/app/src/states/state_machine.py` | | | C | | | | | |
| `asterax/app/src/states/main_menu.py` | | | C | | | | | |
| `asterax/app/src/states/combat.py` | | | C | | | | | |
| `asterax/app/src/states/shop.py` | | | C | | | | | |
| `asterax/app/src/states/game_over.py` | | | C | | | | | |
| `asterax/app/src/states/pause.py` | | | C | | | | | |
| `asterax/app/src/states/how_to_play.py` | | | C | | | | | |
| `asterax/app/src/states/high_scores.py` | | | C | | | | | |
| `asterax/app/src/states/settings_screen.py` | | | C | | | | | |
| `asterax/app/src/persistence/__init__.py` | | | | C | | | | |
| `asterax/app/src/persistence/persistence_manager.py` | | | | C | | | | |
| `asterax/app/src/persistence/schemas.py` | | | | C | | | | |
| `asterax/app/src/input/__init__.py` | | | | | C | | | |
| `asterax/app/src/input/input_manager.py` | | | | | C | | | |
| `asterax/app/src/config/__init__.py` | | | | | | C | | |
| `asterax/app/src/config/game_config.py` | | | | | | C | | |
| `asterax/app/src/config/upgrade_definitions.py` | | | | | | C | | |
| `asterax/app/src/config/difficulty_tables.py` | | | | | | C | | |
| `asterax/app/src/audio/__init__.py` | | | | | | | C | |
| `asterax/app/src/audio/audio_manager.py` | | | | | | | C | |
| `asterax/app/src/rendering/__init__.py` | | | | | | | C | |
| `asterax/app/src/rendering/hud.py` | | | | | | | C | |
| `asterax/app/src/rendering/starfield.py` | | | | | | | C | |
| `asterax/app/src/entities/__init__.py` | | C | | | | | | |
| `asterax/app/src/physics/__init__.py` | | C | | | | | | |
| `asterax/app/src/managers/__init__.py` | | C | | | | | | |
| `asterax/app/config/settings_defaults.yaml` | | | | C | | | | |
| `asterax/assets/sprites/.gitkeep` | | C | | | | | | |
| `asterax/assets/sounds/.gitkeep` | | C | | | | | | |
| `asterax/assets/fonts/.gitkeep` | | C | | | | | | |
| `asterax/scripts/evals.py` | | C | | | | | | |
| `asterax/tests/__init__.py` | | C | | | | | | |
| `asterax/tests/conftest.py` | | | | | | | | C |
| `asterax/tests/test_state_machine.py` | | | | | | | | C |
| `asterax/tests/test_persistence.py` | | | | | | | | C |
| `asterax/tests/test_input.py` | | | | | | | | C |
| `asterax/tests/test_config.py` | | | | | | | | C |
| `asterax/tests/test_audio.py` | | | | | | | | C |
| `docs/implementation-context-phase-1.md` | | | | | | | | C |
| `docs/components/` | | | | | | | | C |

Legend: **C** = Creates, **M** = Modifies

**Serialisation constraints**:
- `asterax/app/src/window.py`: Created by 1.2, modified by 1.7 (to wire starfield/HUD). Component 1.7 must run after 1.2.
- `asterax/app/src/states/__init__.py`: Created by 1.2 (empty/minimal), modified by 1.3 (exports all states). Component 1.3 must run after 1.2.

---

## Component Specifications

---

#### Component: 1.1 - Human Setup & Environment

**Priority**: Must-have

**Estimated Effort**: 2 hours

**Owner**: Human

**Dependencies**:
- None — this is the first component

**Features**:
- Create Python 3.13+ virtual environment — Human
- Install Arcade 3.x and all dev dependencies — Human
- Configure `pyproject.toml` with editable install and package metadata — Human
- Create `.env` files (`.env.local`, `.env.example`, `.env.test`) — Human
- Verify Black, isort, mypy, and pytest all pass on empty project — Human

**Description**:
Sets up the development environment so that all subsequent AI Agent components can execute in a functioning Python workspace. This component isolates every manual/human action required for Phase 1. After completion, `pip install -e .` must work and all dev tooling must pass on an empty project skeleton.

**Acceptance Criteria**:
- [ ] Python 3.13+ virtual environment exists at `.venv/` and activates via `source .venv/bin/activate`
- [ ] `pip install -e .` succeeds with Arcade 3.x, platformdirs, pytest, pytest-cov, black, isort, mypy installed
- [ ] `black --check asterax/` passes (empty project has no files to check, or a minimal `__init__.py`)
- [ ] `isort --check-only asterax/` passes
- [ ] `mypy asterax/` passes with no errors
- [ ] `pytest` runs and reports 0 collected (no tests yet)
- [ ] `.env/.env.local`, `.env/.env.example`, and `.env/.env.test` files exist

**Technical Details**:
- **Files to Create/Modify**:
  - `pyproject.toml` (create)
  - `.env/.env.local` (create)
  - `.env/.env.example` (create)
  - `.env/.env.test` (create)
  - `.python-version` (create — contains `3.13`)
- **Key Functions/Classes**: N/A — configuration only
- **Human/AI Agent**: Entirely Human
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: Python 3.13+, arcade (3.3.x), platformdirs, pytest, pytest-cov, black, isort, mypy, pyyaml

**Detailed Implementation Requirements**:

- **File: `pyproject.toml`**: Must define the `asterax` package with `packages = [{include = "asterax"}]` so that `pip install -e .` makes the package importable. Use `[build-system]` with `setuptools` or `hatchling`. Under `[project]`, set `name = "voidbreaker"`, `version = "0.1.0"`, `requires-python = ">=3.13"`, and list all runtime dependencies (`arcade>=3.3,<4`, `platformdirs>=4.0`, `pyyaml>=6.0`). Under `[project.optional-dependencies]`, list dev dependencies: `pytest>=8.0`, `pytest-cov>=5.0`, `black>=24.0`, `isort>=5.13`, `mypy>=1.10`. Configure `[tool.black]` with `line-length = 88`, `target-version = ["py313"]`. Configure `[tool.isort]` with `profile = "black"`. Configure `[tool.mypy]` with `python_version = "3.13"`, `strict = true`, `warn_return_any = true`, `warn_unused_configs = true`. Configure `[tool.pytest.ini_options]` with `testpaths = ["asterax/tests"]`, `pythonpath = ["."]`.

- **File: `.env/.env.local`**: Minimal environment file. Can contain `VOIDBREAKER_ENV=local` as a placeholder. This file is gitignored and holds local-only overrides.

- **File: `.env/.env.example`**: Template showing expected environment variables. Contains commented examples: `# VOIDBREAKER_ENV=local`.

- **File: `.env/.env.test`**: Test environment configuration. Contains `VOIDBREAKER_ENV=test`.

- **File: `.python-version`**: Single line containing `3.13`. Used by pyenv and similar tools.

**Test Requirements**:
- [ ] Manual verification: `source .venv/bin/activate && pip install -e .` succeeds
- [ ] Manual verification: `python -c "import arcade; print(arcade.version)"` prints 3.x
- [ ] Manual verification: `black --check asterax/` exits 0
- [ ] Manual verification: `isort --check-only asterax/` exits 0
- [ ] Manual verification: `pytest` exits 0 with 0 tests collected

**Definition of Done**:
- [ ] Virtual environment created and dependencies installed
- [ ] `pyproject.toml` configured with correct package definition and all tools
- [ ] All dev tools pass on empty project
- [ ] Documentation created: `docs/components/phase-1-component-1-1-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`

**Notes**:
- The human must have Python 3.13+ installed on their system. If using pyenv, `pyenv install 3.13` first.
- Arcade 3.3.x requires OpenGL 3.3+ support. All modern macOS hardware supports this.
- The `.venv/` directory should be added to `.gitignore` if a `.gitignore` does not already exist.
- Create a `.gitignore` at the repo root with standard Python ignores (`.venv/`, `__pycache__/`, `*.pyc`, `.mypy_cache/`, `.pytest_cache/`, `dist/`, `build/`, `*.egg-info/`).

---

#### Component: 1.2 - Project Structure & Entry Point

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 1.1: Virtual environment and `pyproject.toml` must exist

**Features**:
- Create full directory structure per solution-design.md — AI Agent
- Implement `main.py` entry point with `python -m` support — AI Agent
- Create Arcade `Window` subclass with fixed-timestep accumulator loop — AI Agent
- Create `__init__.py` files for all packages — AI Agent
- Create placeholder `.gitkeep` files for asset directories — AI Agent
- Create `scripts/evals.py` skeleton — AI Agent
- Verify window opens and renders a blank frame — AI Agent

**Description**:
Creates the complete directory tree and the application shell. The entry point `main.py` creates an Arcade `Window` subclass (`VoidBreakerWindow`) that implements the fixed-timestep accumulator pattern from solution-design.md. On launch, the window opens and renders a cleared (black) frame at 60fps. This component establishes the structural foundation every other component builds on.

**Acceptance Criteria**:
- [ ] `python -m asterax.app.src.main` opens an Arcade window (1280x960, titled "VoidBreaker")
- [ ] The window renders a black screen at ~60fps
- [ ] Fixed-timestep accumulator runs with `PHYSICS_DT = 1/60` and `MAX_FRAME_TIME = 0.25`
- [ ] All directories from solution-design.md exist with `__init__.py` files
- [ ] `scripts/evals.py` runs without errors on the new codebase
- [ ] Closing the window exits the application cleanly

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/__init__.py` (create)
  - `asterax/app/__init__.py` (create)
  - `asterax/app/src/__init__.py` (create)
  - `asterax/app/src/main.py` (create)
  - `asterax/app/src/window.py` (create)
  - `asterax/app/src/states/__init__.py` (create — minimal, exports nothing yet)
  - `asterax/app/src/entities/__init__.py` (create — empty)
  - `asterax/app/src/physics/__init__.py` (create — empty)
  - `asterax/app/src/managers/__init__.py` (create — empty)
  - `asterax/app/src/audio/__init__.py` (create — empty)
  - `asterax/app/src/persistence/__init__.py` (create — empty)
  - `asterax/app/src/rendering/__init__.py` (create — empty)
  - `asterax/app/src/input/__init__.py` (create — empty)
  - `asterax/app/src/config/__init__.py` (create — empty)
  - `asterax/app/config/` (create directory)
  - `asterax/app/docs/` (create directory)
  - `asterax/assets/sprites/.gitkeep` (create)
  - `asterax/assets/sounds/.gitkeep` (create)
  - `asterax/assets/fonts/.gitkeep` (create)
  - `asterax/scripts/evals.py` (create)
  - `asterax/tests/__init__.py` (create — empty)
- **Key Functions/Classes**:
  - `main()` in `main.py` — creates window, calls `arcade.run()`
  - `VoidBreakerWindow(arcade.Window)` in `window.py` — the application window
  - `VoidBreakerWindow.on_update(delta_time)` — fixed-timestep accumulator
  - `VoidBreakerWindow.on_draw()` — clears and renders
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: arcade (already installed via 1.1)

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/main.py`**: The entry point for the entire application. Must contain a `main()` function that instantiates `VoidBreakerWindow` and calls `arcade.run()`. The module must include an `if __name__ == "__main__"` guard that calls `main()`. The `main()` function signature should accept no arguments and return `None`. This file must be importable as a module (for `python -m asterax.app.src.main`) and executable directly. Keep this file minimal — its sole responsibility is to bootstrap the window and start the event loop. Do not initialise subsystems here; that is the window's responsibility.

- **File: `asterax/app/src/window.py`**: Contains the `VoidBreakerWindow` class inheriting from `arcade.Window`. The constructor sets window dimensions (default `1280x960`), title `"VoidBreaker"`, and calls `super().__init__()`. Initialise an `accumulator: float = 0.0` instance variable. Define constants `PHYSICS_DT: Final[float] = 1.0 / 60.0` and `MAX_FRAME_TIME: Final[float] = 0.25` at module level. The `on_update(delta_time)` method implements the fixed-timestep accumulator pattern: cap `delta_time` to `MAX_FRAME_TIME`, add to accumulator, and run `_physics_step(PHYSICS_DT)` in a while loop while accumulator >= `PHYSICS_DT`. The `_physics_step(dt)` method is a stub that will later delegate to the active state. The `on_draw()` method calls `self.clear()` to render a black frame. Add `on_key_press(key, modifiers)` and `on_key_release(key, modifiers)` stubs that will later delegate to the state machine. The window must call `self.set_update_rate(1/60)` in the constructor to target 60fps.

- **File: `asterax/scripts/evals.py`**: The evaluation script required by `copilot.instructions.md`. Must check: (1) all `.py` files under `asterax/app/src/` have no `TODO` or `FIXME` comments, (2) all public functions and classes have docstrings. The script must exit with code 0 if all checks pass and code 1 if any fail, printing a summary of violations. Use `ast` module to parse Python files and inspect docstrings. Use simple string search for TODO/FIXME.

**Test Requirements**:
- [ ] Manual verification: `python -m asterax.app.src.main` opens a window
- [ ] Manual verification: Window displays a black screen
- [ ] Manual verification: Closing the window exits cleanly (no exceptions)
- [ ] Programmatic: `python asterax/scripts/evals.py` exits 0

**Definition of Done**:
- [ ] All directories and `__init__.py` files exist per solution-design.md
- [ ] Entry point launches Arcade window successfully
- [ ] Fixed-timestep accumulator is implemented correctly
- [ ] `evals.py` passes
- [ ] No regression in tooling (`black --check`, `isort --check-only`, `mypy` pass)
- [ ] Documentation created: `docs/components/phase-1-component-1-2-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`

**Notes**:
- The `set_update_rate(1/60)` call is critical. Without it, Arcade defaults to 60fps but actual behaviour varies by platform. Explicit setting ensures consistent frame timing.
- The window should NOT be resizable in Phase 1. Fixed 1280x960 simplifies rendering logic. Fullscreen support comes in Phase 5 (Settings).
- All `__init__.py` files for packages that are not yet implemented should be empty (or contain only a module-level docstring). Do not add placeholder imports.
- The accumulator pattern must handle the case where `delta_time` is 0 (can happen on the first frame on some platforms).

---

#### Component: 1.3 - State Machine

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 1.2: Project structure and window must exist

**Features**:
- Define `GameState` protocol with all required methods — AI Agent
- Implement `StateMachine` manager with push/pop/switch transitions — AI Agent
- Create stub states for all nine game states — AI Agent
- Implement state stack for overlay states (Pause, Settings) — AI Agent
- Wire state machine into `VoidBreakerWindow` update/draw/input loop — AI Agent
- Verify keyboard-driven transitions between all states — AI Agent

**Description**:
Implements the core state machine architecture that governs all game behaviour. Every frame, the window delegates `on_update`, `on_draw`, `on_key_press`, and `on_key_release` to the currently active state. The state machine supports both `switch` (replace the active state) and `push`/`pop` (for overlay states like Pause). All nine states from solution-design.md are created as stub implementations that render their name on screen and transition to other states via keyboard shortcuts.

**Acceptance Criteria**:
- [ ] `GameState` Protocol is defined with `on_enter()`, `on_exit()`, `on_update(delta_time: float)`, `on_draw()`, `on_key_press(key: int, modifiers: int)`, `on_key_release(key: int, modifiers: int)`
- [ ] `StateMachine` supports `switch_state(state)`, `push_state(state)`, and `pop_state()` operations
- [ ] All nine stub states exist: MainMenu, CombatPhase, ShopPhase, GameOver, Pause, HowToPlay, HighScores, SettingsScreen, GameInit
- [ ] Application starts in `MainMenu` state
- [ ] Pressing designated keys transitions between states (e.g., `1` = New Game -> GameInit -> CombatPhase, `2` = HowToPlay, `3` = HighScores, `4` = SettingsScreen, `Q` = Quit)
- [ ] Pause overlay pushes on top of CombatPhase and ShopPhase, pop restores underlying state
- [ ] Each stub state renders its name as text on screen (e.g., "MainMenu" in white text)
- [ ] No state leaks — `on_exit()` is always called before `on_enter()` of the new state

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/app/src/states/base_state.py` (create)
  - `asterax/app/src/states/state_machine.py` (create)
  - `asterax/app/src/states/main_menu.py` (create)
  - `asterax/app/src/states/combat.py` (create)
  - `asterax/app/src/states/shop.py` (create)
  - `asterax/app/src/states/game_over.py` (create)
  - `asterax/app/src/states/pause.py` (create)
  - `asterax/app/src/states/how_to_play.py` (create)
  - `asterax/app/src/states/high_scores.py` (create)
  - `asterax/app/src/states/settings_screen.py` (create)
  - `asterax/app/src/states/game_init.py` (create)
  - `asterax/app/src/states/__init__.py` (modify — re-export all state classes and protocol)
- **Key Functions/Classes**:
  - `GameState` (Protocol) in `base_state.py`
  - `BaseState` (abstract base implementing `GameState`) in `base_state.py`
  - `StateMachine` in `state_machine.py`
  - `StateMachine.switch_state(state: GameState)` — replaces active state
  - `StateMachine.push_state(state: GameState)` — pushes overlay
  - `StateMachine.pop_state()` — removes top overlay, resumes previous
  - `StateMachine.update(delta_time: float)` — delegates to top state
  - `StateMachine.draw()` — draws all states in stack (bottom to top) for transparent overlays
  - `StateMachine.on_key_press(key, modifiers)` — delegates to top state
  - `StateMachine.on_key_release(key, modifiers)` — delegates to top state
  - `MainMenuState`, `CombatPhaseState`, `ShopPhaseState`, `GameOverState`, `PauseState`, `HowToPlayState`, `HighScoresState`, `SettingsScreenState`, `GameInitState` — all stub state classes
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: arcade (for key constants, text rendering in stubs)

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/states/base_state.py`**: Define a `GameState` Protocol class with methods: `on_enter(self) -> None`, `on_exit(self) -> None`, `on_update(self, delta_time: float) -> None`, `on_draw(self) -> None`, `on_key_press(self, key: int, modifiers: int) -> None`, `on_key_release(self, key: int, modifiers: int) -> None`. Below the protocol, define `BaseState` as an abstract class implementing `GameState` with a constructor that accepts a reference to the `StateMachine` instance (`self.state_machine: StateMachine`). Provide default no-op implementations for all protocol methods. Subclasses override only what they need. Import `TYPE_CHECKING` and forward-reference `StateMachine` to avoid circular imports.

- **File: `asterax/app/src/states/state_machine.py`**: The `StateMachine` class holds a `_stack: list[GameState]` for state management. `switch_state(state)` calls `on_exit()` on the current top state (if any), clears the stack, pushes the new state, and calls `on_enter()`. `push_state(state)` calls `on_exit()` on the current top state (for pause semantics — the underlying state "pauses"), pushes the new state, and calls `on_enter()`. `pop_state()` calls `on_exit()` on the top state, removes it, and calls `on_enter()` on the newly-revealed top state. The `update(delta_time)` method calls `on_update(delta_time)` on the top state only. The `draw()` method iterates the entire stack from bottom to top, calling `on_draw()` on each state — this allows overlay states like Pause to render on top of the game state beneath them. `on_key_press` and `on_key_release` delegate to the top state only. Property `current_state` returns the top of the stack. The machine must handle the case where the stack is empty gracefully (no-op).

- **File: `asterax/app/src/states/main_menu.py`**: `MainMenuState(BaseState)` renders "VoidBreaker - Main Menu" centred on screen using `arcade.draw_text()`. `on_key_press` handles: `arcade.key.KEY_1` or `arcade.key.ENTER` -> switch to `GameInitState`, `arcade.key.KEY_2` -> switch to `HowToPlayState`, `arcade.key.KEY_3` -> switch to `HighScoresState`, `arcade.key.KEY_4` -> switch to `SettingsScreenState`, `arcade.key.Q` -> `arcade.close_window()`. Also render a legend of these controls below the title.

- **File: `asterax/app/src/states/game_init.py`**: `GameInitState(BaseState)` renders "Initializing..." on screen. In `on_enter()`, immediately transition to `CombatPhaseState` (placeholder logic — in Phase 2 this will initialise run state). For Phase 1, this is effectively a pass-through state demonstrating the transition chain.

- **File: `asterax/app/src/states/combat.py`**: `CombatPhaseState(BaseState)` renders "Combat Phase (stub)" on screen. `on_key_press` handles: `arcade.key.ESCAPE` -> push `PauseState`, `arcade.key.N` -> switch to `ShopPhaseState` (placeholder for "level clear"), `arcade.key.G` -> switch to `GameOverState` (placeholder for "shields depleted").

- **File: `asterax/app/src/states/shop.py`**: `ShopPhaseState(BaseState)` renders "Shop Phase (stub)" on screen. `on_key_press` handles: `arcade.key.ESCAPE` -> push `PauseState`, `arcade.key.ENTER` -> switch to `CombatPhaseState` (placeholder for "continue to next level").

- **File: `asterax/app/src/states/game_over.py`**: `GameOverState(BaseState)` renders "Game Over (stub)" on screen. `on_key_press` handles: `arcade.key.ENTER` or `arcade.key.ESCAPE` -> switch to `MainMenuState`.

- **File: `asterax/app/src/states/pause.py`**: `PauseState(BaseState)` renders a semi-transparent overlay with "PAUSED" text. `on_key_press` handles: `arcade.key.ESCAPE` -> `pop_state()` (resume), `arcade.key.R` -> switch to `GameInitState` (restart run), `arcade.key.M` -> switch to `MainMenuState` (exit to menu). This is an overlay state — it is always pushed, never switched to directly.

- **File: `asterax/app/src/states/how_to_play.py`**: `HowToPlayState(BaseState)` renders "How to Play (stub)" with placeholder control descriptions. `on_key_press` handles: `arcade.key.ESCAPE` or `arcade.key.BACKSPACE` -> switch to `MainMenuState`.

- **File: `asterax/app/src/states/high_scores.py`**: `HighScoresState(BaseState)` renders "High Scores (stub)" on screen. `on_key_press` handles: `arcade.key.ESCAPE` or `arcade.key.BACKSPACE` -> switch to `MainMenuState`.

- **File: `asterax/app/src/states/settings_screen.py`**: `SettingsScreenState(BaseState)` renders "Settings (stub)" on screen. `on_key_press` handles: `arcade.key.ESCAPE` or `arcade.key.BACKSPACE` -> switch to `MainMenuState`.

- **File: `asterax/app/src/states/__init__.py`**: Re-export all state classes and the `GameState` protocol. Example: `from asterax.app.src.states.base_state import BaseState, GameState` and similarly for all concrete states.

**Test Requirements**:
- [ ] Unit tests: `StateMachine.switch_state()` calls `on_exit()` then `on_enter()` in correct order
- [ ] Unit tests: `StateMachine.push_state()` preserves underlying state in stack
- [ ] Unit tests: `StateMachine.pop_state()` calls `on_exit()` on popped state and `on_enter()` on revealed state
- [ ] Unit tests: `draw()` calls `on_draw()` on all states in stack (bottom to top)
- [ ] Unit tests: `update()` and `on_key_press()` only delegate to top state
- [ ] Unit tests: Empty stack operations are no-ops (no exceptions)
- [ ] Manual testing: Keyboard transitions between all states work correctly

**Definition of Done**:
- [ ] All nine state classes implemented with stub rendering and keyboard transitions
- [ ] State machine supports switch, push, and pop operations correctly
- [ ] Application starts in MainMenu and all transitions work
- [ ] Pause overlay correctly overlays on combat and shop states
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-1-component-1-3-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`
- [ ] No regression in existing functionality

**Notes**:
- The `GameState` Protocol is the contract consumed by all subsequent phases. Phase 2 replaces `CombatPhaseState` stub with the real implementation, Phase 4 replaces `ShopPhaseState`, etc. The protocol methods must not change after Phase 1.
- Stub states use `arcade.draw_text()` for rendering. This requires no assets and is sufficient for verifying transitions.
- The `PauseState.on_draw()` should draw a semi-transparent rectangle over the full window before drawing "PAUSED" text, so the underlying state (combat/shop) is visible but dimmed.
- Circular import risk: `BaseState` references `StateMachine` and `StateMachine` references `GameState`. Use `from __future__ import annotations` and `TYPE_CHECKING` to resolve.
- The `GameInitState` immediately transitioning to `CombatPhaseState` is intentional for Phase 1. Phase 2 will add ship class selection and run state initialisation.

---

#### Component: 1.4 - Persistence Layer

**Priority**: Must-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 1.2: Project structure must exist

**Features**:
- Implement `PersistenceManager` class with JSON read/write — AI Agent
- Implement atomic save using `tempfile` + `os.replace` — AI Agent
- Implement schema versioning with migration support — AI Agent
- Implement corrupt-file fallback to defaults — AI Agent
- Create `GameSettings` and `HighScoreEntry` dataclasses in `schemas.py` — AI Agent
- Resolve storage path using `platformdirs` — AI Agent
- Create `settings_defaults.yaml` with default values — AI Agent

**Description**:
Implements the complete persistence layer for reading and writing JSON files (settings and high scores) to the platform-appropriate user data directory. Uses atomic writes to prevent corruption, schema versioning for future-proofing, and graceful fallback to defaults on corrupt/missing files. This component is consumed by every subsequent phase that needs to persist data.

**Acceptance Criteria**:
- [ ] `PersistenceManager.load_settings()` returns `GameSettings` with defaults on first run (no file exists)
- [ ] `PersistenceManager.save_settings(settings)` writes `settings.json` to `~/Library/Application Support/VoidBreaker/`
- [ ] Settings file survives simulated crash (atomic write via `tempfile` + `os.replace`)
- [ ] Loading a corrupt settings file (invalid JSON, missing keys) falls back to defaults and logs a warning
- [ ] `PersistenceManager.load_high_scores()` returns empty list on first run
- [ ] `PersistenceManager.save_high_scores(entries)` atomically writes `high_scores.json`
- [ ] Both files include a `"version"` field matching the current schema version
- [ ] Loading a file with a future version logs a warning and falls back to defaults

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/app/src/persistence/__init__.py` (modify — export `PersistenceManager`)
  - `asterax/app/src/persistence/persistence_manager.py` (create)
  - `asterax/app/src/persistence/schemas.py` (create)
  - `asterax/app/config/settings_defaults.yaml` (create)
- **Key Functions/Classes**:
  - `PersistenceManager` — main class
  - `PersistenceManager.__init__(base_dir: Path | None = None)` — resolves storage directory
  - `PersistenceManager.load_settings() -> GameSettings`
  - `PersistenceManager.save_settings(settings: GameSettings) -> None`
  - `PersistenceManager.load_high_scores() -> list[HighScoreEntry]`
  - `PersistenceManager.save_high_scores(entries: list[HighScoreEntry]) -> None`
  - `GameSettings` dataclass in `schemas.py`
  - `HighScoreEntry` dataclass in `schemas.py`
  - `SETTINGS_VERSION: Final[int] = 1`
  - `HIGH_SCORES_VERSION: Final[int] = 1`
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None (JSON file-based persistence)
- **API Endpoints**: None
- **Dependencies**: `platformdirs`, `json` (stdlib), `tempfile` (stdlib), `pathlib` (stdlib), `logging` (stdlib), `pyyaml`

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/persistence/schemas.py`**: Define `GameSettings` as a dataclass matching the schema from solution-design.md. Fields: `master_volume: float = 0.8`, `music_volume: float = 0.5`, `sfx_volume: float = 1.0`, `key_rotate_left: str = "LEFT"`, `key_rotate_right: str = "RIGHT"`, `key_thrust: str = "UP"`, `key_fire: str = "SPACE"`, `key_brake: str = "DOWN"`, `key_special: str = "LSHIFT"`, `key_pause: str = "ESCAPE"`, `fire_mode: str = "hold"`, `autofire: bool = False`, `colorblind_mode: bool = False`, `screen_shake: str = "medium"`, `difficulty: str = "classic"`, `fullscreen: bool = False`, `resolution: tuple[int, int] = (1280, 960)`. Store key bindings as string names (e.g., `"LEFT"`, `"SPACE"`) rather than Arcade integer constants — this keeps the JSON human-readable and decouples persistence from Arcade's key code values. Define a `to_dict()` method that serialises the dataclass to a JSON-compatible dict and a `from_dict(data: dict) -> GameSettings` classmethod that deserialises with defaults for missing keys. Define `HighScoreEntry` as a dataclass with fields: `name: str`, `score: int`, `level_reached: int`, `difficulty: str`, `enemies_destroyed: int`, `currency_collected: int`, `currency_spent: int`, `date: str`. Provide corresponding `to_dict()` and `from_dict()` methods. Define module-level constants `SETTINGS_VERSION: Final[int] = 1` and `HIGH_SCORES_VERSION: Final[int] = 1`.

- **File: `asterax/app/src/persistence/persistence_manager.py`**: `PersistenceManager.__init__` resolves the base directory: if `base_dir` is provided, use it (for testing); otherwise use `platformdirs.user_data_dir("VoidBreaker", appauthor=False)`. Create the directory if it does not exist (`Path.mkdir(parents=True, exist_ok=True)`). Store as `self._base_dir`. File paths: `self._settings_path = self._base_dir / "settings.json"`, `self._high_scores_path = self._base_dir / "high_scores.json"`. The `load_settings()` method: if file does not exist, return `GameSettings()` (defaults). If file exists, read JSON, check `"version"` field. If version matches `SETTINGS_VERSION`, call `GameSettings.from_dict(data)`. If version is higher than `SETTINGS_VERSION`, log a warning and return defaults. If JSON is invalid or keys are missing, catch exceptions, log a warning, and return defaults. The `save_settings(settings)` method: construct dict with `{"version": SETTINGS_VERSION, **settings.to_dict()}`, write to a `tempfile.NamedTemporaryFile` in the same directory (to ensure same filesystem for `os.replace`), then `os.replace(temp_path, self._settings_path)`. This ensures atomicity — the file is either fully written or not modified at all. Same pattern for `load_high_scores()` and `save_high_scores(entries)`, using `{"version": HIGH_SCORES_VERSION, "entries": [e.to_dict() for e in entries]}`. Use Python's `logging` module (`logger = logging.getLogger(__name__)`) for all warnings.

- **File: `asterax/app/config/settings_defaults.yaml`**: A YAML file containing the default settings values. This serves as documentation and can be used as a reference for the defaults in `GameSettings`. Contents mirror the `GameSettings` defaults: `master_volume: 0.8`, `music_volume: 0.5`, etc. The `PersistenceManager` does NOT read this file at runtime — it exists purely as a human-readable reference. The authoritative defaults are the field defaults on the `GameSettings` dataclass.

**Test Requirements**:
- [ ] Unit tests: `GameSettings()` returns correct defaults for all fields
- [ ] Unit tests: `GameSettings.to_dict()` and `GameSettings.from_dict()` round-trip correctly
- [ ] Unit tests: `HighScoreEntry.to_dict()` and `HighScoreEntry.from_dict()` round-trip correctly
- [ ] Unit tests: `PersistenceManager.load_settings()` returns defaults when no file exists
- [ ] Unit tests: `PersistenceManager.save_settings()` + `load_settings()` round-trips correctly
- [ ] Unit tests: Loading corrupt JSON (invalid syntax) falls back to defaults
- [ ] Unit tests: Loading JSON with missing keys uses defaults for missing fields
- [ ] Unit tests: Loading JSON with future version falls back to defaults
- [ ] Unit tests: `save_high_scores()` + `load_high_scores()` round-trips correctly
- [ ] Unit tests: Atomic write — verify no partial files on disk after save
- [ ] Integration test: PersistenceManager works with `tmp_path` fixture (pytest)

**Definition of Done**:
- [ ] `PersistenceManager` fully implemented with atomic writes and schema versioning
- [ ] `GameSettings` and `HighScoreEntry` dataclasses match solution-design.md schemas
- [ ] Corrupt file and version mismatch handling tested
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-1-component-1-4-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`
- [ ] No regression in existing functionality

**Notes**:
- Key bindings are stored as string names (`"LEFT"`, `"SPACE"`) in JSON, not as integer key codes. The `InputManager` (component 1.5) is responsible for mapping these strings to `arcade.key` constants. This decouples persistence from Arcade.
- The `base_dir` parameter in the constructor is critical for testability. All tests must pass a `tmp_path` directory to avoid polluting the user's actual settings.
- `os.replace()` is atomic on POSIX systems (macOS, Linux). On Windows (future), it is also atomic as of Python 3.3+.
- The high score list should be capped at a reasonable maximum (e.g., 100 entries) to prevent unbounded file growth. Apply the cap in `save_high_scores()` before writing.
- Schema migration: for version 1, no migration is needed. The infrastructure is in place so that when version 2 is introduced (in a later phase), a `_migrate_settings_v1_to_v2(data)` function can be added.

---

#### Component: 1.5 - Input Manager

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 1.3: State machine must exist (to route input to active state)
- 1.4: Persistence layer must exist (to load key bindings from settings)

**Features**:
- Implement `InputManager` with key-held set tracking — AI Agent
- Load configurable key bindings from persisted settings — AI Agent
- Map string key names to Arcade key constants — AI Agent
- Provide default bindings matching solution-design.md — AI Agent
- Wire into `VoidBreakerWindow` key events — AI Agent
- Route input events to the active state via the state machine — AI Agent

**Description**:
Implements the input layer that captures keyboard events, maintains a set of currently-held keys, and provides configurable key bindings. The `InputManager` translates between string key names (stored in settings JSON) and Arcade integer key constants. States query the `InputManager.keys_held` set for continuous actions (thrust, rotation) and receive discrete events (`on_key_press`, `on_key_release`) for one-shot actions (fire in tap mode, menu navigation).

**Acceptance Criteria**:
- [ ] `InputManager.keys_held` accurately tracks which keys are currently pressed
- [ ] `InputManager.get_binding(action: str) -> int` returns the Arcade key constant for a named action
- [ ] Default bindings match solution-design.md: LEFT=rotate_left, RIGHT=rotate_right, UP=thrust, SPACE=fire, DOWN=brake, LSHIFT=special, ESCAPE=pause
- [ ] Bindings load from `GameSettings` on `InputManager` construction
- [ ] `InputManager.update_bindings(settings: GameSettings)` refreshes bindings without restart
- [ ] Key press/release events flow through `InputManager` to the active state
- [ ] `InputManager.is_action_held(action: str) -> bool` returns whether the key for a named action is held

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/app/src/input/__init__.py` (modify — export `InputManager`)
  - `asterax/app/src/input/input_manager.py` (create)
- **Key Functions/Classes**:
  - `InputManager.__init__(settings: GameSettings)`
  - `InputManager.keys_held: set[int]` — set of currently pressed Arcade key codes
  - `InputManager.on_key_press(key: int, modifiers: int) -> None` — adds to `keys_held`
  - `InputManager.on_key_release(key: int, modifiers: int) -> None` — removes from `keys_held`
  - `InputManager.is_action_held(action: str) -> bool` — checks if the bound key for an action is held
  - `InputManager.get_binding(action: str) -> int` — returns Arcade key code for a named action
  - `InputManager.update_bindings(settings: GameSettings) -> None` — reloads bindings from settings
  - `KEY_NAME_MAP: dict[str, int]` — module-level mapping of string names to `arcade.key` constants
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: arcade (for key constants), `GameSettings` from persistence schemas

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/input/input_manager.py`**: Define a module-level `KEY_NAME_MAP: dict[str, int]` that maps human-readable string key names (as stored in `settings.json`) to `arcade.key` integer constants. Must include at minimum: `"LEFT"`, `"RIGHT"`, `"UP"`, `"DOWN"`, `"SPACE"`, `"LSHIFT"`, `"RSHIFT"`, `"ESCAPE"`, `"ENTER"`, `"BACKSPACE"`, `"TAB"`, and all letter keys `"A"` through `"Z"`, plus number keys `"KEY_1"` through `"KEY_9"` and `"KEY_0"`. The `InputManager` class constructor accepts a `GameSettings` instance and builds an internal `_bindings: dict[str, int]` mapping action names (`"rotate_left"`, `"rotate_right"`, `"thrust"`, `"fire"`, `"brake"`, `"special"`, `"pause"`) to their resolved Arcade key codes using `KEY_NAME_MAP`. The `keys_held: set[int]` attribute is a public set. `on_key_press(key, modifiers)` adds `key` to `keys_held`. `on_key_release(key, modifiers)` discards `key` from `keys_held`. `is_action_held(action)` looks up the key code for the action in `_bindings` and checks membership in `keys_held`. `get_binding(action)` returns the key code from `_bindings`. `update_bindings(settings)` rebuilds `_bindings` from the provided settings — used when the player remaps keys in the Settings screen (Phase 5). If a key name from settings is not found in `KEY_NAME_MAP`, log a warning and use the default binding for that action.

**Test Requirements**:
- [ ] Unit tests: `on_key_press` adds key to `keys_held`, `on_key_release` removes it
- [ ] Unit tests: `is_action_held` returns True when bound key is held, False otherwise
- [ ] Unit tests: `get_binding` returns correct Arcade key code for default bindings
- [ ] Unit tests: `update_bindings` changes active bindings
- [ ] Unit tests: Invalid key name in settings falls back to default with warning
- [ ] Unit tests: `KEY_NAME_MAP` contains all expected key mappings

**Definition of Done**:
- [ ] `InputManager` fully implemented with key tracking, configurable bindings, and action queries
- [ ] Wired into `VoidBreakerWindow` key events
- [ ] Default bindings match solution-design.md
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-1-component-1-5-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`
- [ ] No regression in existing functionality

**Notes**:
- The `InputManager` does NOT send events to states directly. The `VoidBreakerWindow` calls `InputManager.on_key_press()` first (to update `keys_held`), then calls `StateMachine.on_key_press()` to route the event to the active state. The state can then query `InputManager.is_action_held()` during its `on_update()` for continuous actions.
- Phase 5 will add a key remapping UI in `SettingsScreenState`. The `update_bindings()` method exists to support that without restarting the application.
- Using `discard()` rather than `remove()` for `on_key_release` prevents `KeyError` if a release event fires without a preceding press (can happen if the window loses focus while a key is held).

---

#### Component: 1.6 - Game Config & Data Models

**Priority**: Must-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 1.2: Project structure must exist

**Features**:
- Create `game_config.py` with all physics tuning parameters — AI Agent
- Create `upgrade_definitions.py` with all upgrade definitions — AI Agent
- Create `difficulty_tables.py` with per-level scaling parameters — AI Agent
- Create `GameState`, `ShipState`, `InsuranceState`, `DifficultyParams`, `LevelStats`, `RunStats` data models — AI Agent
- Create enumerations for game phases, asteroid sizes, enemy types, upgrade categories, insurance tiers — AI Agent
- Verify all models instantiate with sensible defaults — AI Agent

**Description**:
Centralises all game configuration, tuning parameters, and data models into the `config/` package. This is the single source of truth for every numeric constant, upgrade definition, and difficulty scaling parameter in the game. All subsequent phases reference these definitions — they never hardcode tuning values. This component also defines the core data models (`GameState`, `ShipState`, etc.) used by the game logic layer.

**Acceptance Criteria**:
- [ ] `GameConfig` dataclass contains all physics parameters from solution-design.md (PHYSICS_DT, MAX_FRAME_TIME, NATURAL_DRAG, BRAKE_DRAG, MAX_SHIP_SPEED, BASE_THRUST, BASE_TURN_RATE, etc.)
- [ ] All upgrade definitions from solution-design.md are present in `UPGRADE_DEFINITIONS: list[UpgradeDefinition]`
- [ ] Difficulty table provides `get_difficulty(level: int) -> DifficultyParams` for levels 1-30+
- [ ] `GameState`, `ShipState`, `InsuranceState`, `DifficultyParams`, `LevelStats`, `RunStats` all instantiate with defaults
- [ ] All enumerations (`GamePhase`, `AsteroidSize`, `EnemyArchetype`, `UpgradeCategory`, `InsuranceTier`) are defined
- [ ] `game_config.py` exports a single `GAME_CONFIG` instance for use throughout the codebase

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/app/src/config/__init__.py` (modify — export key classes and constants)
  - `asterax/app/src/config/game_config.py` (create)
  - `asterax/app/src/config/upgrade_definitions.py` (create)
  - `asterax/app/src/config/difficulty_tables.py` (create)
- **Key Functions/Classes**:
  - `GameConfig` (frozen dataclass) — all physics/gameplay constants
  - `GAME_CONFIG: Final[GameConfig]` — singleton instance
  - `UpgradeDefinition` (dataclass) — static upgrade definition
  - `UpgradeCategory` (Enum) — WEAPON, DEFENSE, MOBILITY, ECONOMY, REPAIR
  - `UPGRADE_DEFINITIONS: Final[list[UpgradeDefinition]]`
  - `DifficultyParams` (dataclass) — per-level parameters
  - `get_difficulty(level: int, base: str = "classic") -> DifficultyParams`
  - `GamePhase` (Enum) — COMBAT, SHOP, GAME_OVER
  - `AsteroidSize` (Enum) — LARGE, MEDIUM, SMALL
  - `EnemyArchetype` (Enum) — BASIC, AGGRESSIVE, SNIPER
  - `InsuranceTier` (Enum) — OFF, BASIC, PREMIUM
  - `GameState` (dataclass) — top-level mutable run state
  - `ShipState` (dataclass) — ship physics and upgrade state
  - `InsuranceState` (dataclass) — insurance within a run
  - `LevelStats` (dataclass) — per-level statistics
  - `RunStats` (dataclass) — cumulative run statistics
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: None (stdlib only — `dataclasses`, `enum`)

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/config/game_config.py`**: Define a `@dataclass(frozen=True)` class `GameConfig` with the following fields and their defaults from solution-design.md: `physics_dt: float = 1.0 / 60.0`, `max_frame_time: float = 0.25`, `target_fps: int = 60`, `window_width: int = 1280`, `window_height: int = 960`, `window_title: str = "VoidBreaker"`, `natural_drag: float = 0.3`, `brake_drag: float = 3.0`, `max_ship_speed: float = 600.0`, `base_thrust: float = 400.0`, `base_turn_rate: float = 240.0`, `base_fire_rate: float = 3.0` (shots/sec), `base_projectile_speed: float = 800.0`, `base_projectile_range: float = 500.0` (pixels), `base_damage: float = 1.0`, `base_shields: float = 100.0`, `invulnerability_duration: float = 1.0` (seconds after taking damage), `shop_recentre_duration: float = 0.3` (seconds), `currency_pickup_lifetime: float = 10.0` (seconds), `max_high_scores: int = 100`, `max_player_projectiles: int = 15`, `max_particles: int = 300`. Export a module-level `GAME_CONFIG: Final[GameConfig] = GameConfig()`. Also define all Enum types in this file: `GamePhase`, `AsteroidSize`, `EnemyArchetype`, `UpgradeCategory`, `InsuranceTier`. Define `GameState`, `ShipState`, `InsuranceState`, `LevelStats`, and `RunStats` dataclasses matching solution-design.md. `ShipState` includes all base stats, all upgrade levels (defaulting to 0), and all effective stats (computed from base + upgrades). Include a `recalculate_effective_stats(upgrade_definitions)` method on `ShipState` that recomputes effective values based on current upgrade levels — this method is called by `UpgradeManager` (Phase 4) after any upgrade purchase. `LevelStats` tracks per-level metrics: `asteroids_destroyed: int = 0`, `enemies_destroyed: int = 0`, `currency_collected: int = 0`, `damage_taken: float = 0.0`. `RunStats` tracks cumulative metrics: same fields as `LevelStats` plus `levels_completed: int = 0`, `currency_spent: int = 0`, `upgrades_purchased: int = 0`.

- **File: `asterax/app/src/config/upgrade_definitions.py`**: Define the `UpgradeDefinition` dataclass with fields: `id: str`, `category: UpgradeCategory`, `name: str`, `description: str`, `max_level: int`, `base_cost: int`, `cost_scaling: float`, `effect_per_level: float`, `stat_key: str`. Define `UPGRADE_DEFINITIONS: Final[list[UpgradeDefinition]]` containing all upgrades from solution-design.md: weapon_fire_rate (max 5, base cost 50, scaling 1.5, +0.5 shots/sec/level), weapon_damage (max 5, base cost 60, scaling 1.5, +0.3/level), weapon_speed (max 3, base cost 40, scaling 1.4, +100 px/s/level), weapon_spread (max 3, base cost 100, scaling 2.0, +1 projectile/level), defense_shields (max 5, base cost 50, scaling 1.5, +25 max shields/level), mobility_thrust (max 5, base cost 40, scaling 1.4, +60 px/s^2/level), mobility_turn (max 3, base cost 30, scaling 1.3, +30 deg/s/level), economy_magnet (max 3, base cost 60, scaling 1.5, +50 px radius/level), economy_protection (max 1, base cost 150, scaling 1.0, currency becomes indestructible), repair (max 99, base cost 30, scaling 1.2, restores 25 shields/purchase). Include a helper `get_upgrade_cost(definition: UpgradeDefinition, current_level: int) -> int` that returns `int(definition.base_cost * (definition.cost_scaling ** current_level))`. Include a helper `get_upgrade_by_id(upgrade_id: str) -> UpgradeDefinition | None` for lookup.

- **File: `asterax/app/src/config/difficulty_tables.py`**: Define a function `get_difficulty(level: int, base: str = "classic") -> DifficultyParams` that returns difficulty parameters for the given level and base difficulty. For "classic" difficulty: asteroid_count starts at 4 (level 1) and increases by ~1 per level (capped at 20 for late game), asteroid_speed_min starts at 50 and increases by 5/level (capped at 200), asteroid_speed_max starts at 150 and increases by 8/level (capped at 400), enemy_spawn_enabled is False for levels 1-5 and True from level 6+, enemy_count_max starts at 1 (level 6) and increases by 1 every 3 levels (capped at 10), enemy_spawn_interval starts at 10s and decreases by 0.3/level (min 3s), enemy_aggression starts at 0.2 and increases by 0.03/level (capped at 0.9), currency_drop_chance starts at 0.4 and decreases by 0.005/level (min 0.2), currency_value_base starts at 10 and increases by 2/level. For "casual" difficulty: multiply asteroid count by 0.7, enemy aggression by 0.6, currency drop by 1.3. For "hard": multiply asteroid count by 1.3, enemy aggression by 1.3, currency drop by 0.7. Use `min()`/`max()` clamping to keep all values within sensible bounds. The function should compute values procedurally (formulaic) rather than using a lookup table, to support arbitrarily high levels.

**Test Requirements**:
- [ ] Unit tests: `GAME_CONFIG` has correct default values for all physics constants
- [ ] Unit tests: All `UpgradeDefinition` entries have valid fields (non-empty id, positive costs, positive max_level)
- [ ] Unit tests: `get_upgrade_cost()` returns correct values for level 0, 1, and max
- [ ] Unit tests: `get_difficulty()` returns sensible values for levels 1, 5, 10, 20, 50
- [ ] Unit tests: `get_difficulty()` values are clamped within bounds for extreme levels (100+)
- [ ] Unit tests: "casual" difficulty is easier than "classic", "hard" is harder
- [ ] Unit tests: All data model dataclasses instantiate with defaults (no required arguments)
- [ ] Unit tests: `ShipState.recalculate_effective_stats()` correctly applies upgrade levels
- [ ] Unit tests: All enums have expected members

**Definition of Done**:
- [ ] All config dataclasses implemented with correct defaults from solution-design.md
- [ ] All upgrade definitions complete with cost scaling
- [ ] Difficulty table produces sensible scaling for 30+ levels
- [ ] All data models instantiate correctly
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-1-component-1-6-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`
- [ ] No regression in existing functionality

**Notes**:
- `game_config.py` is a serialisation constraint: Phase 2+ components will add parameters to it. File ownership is component 1.6 for creation. Later phases should add new fields to `GameConfig` or to the data model dataclasses as needed.
- The `frozen=True` on `GameConfig` ensures tuning constants cannot be accidentally mutated at runtime. If Phase 2 needs a mutable copy for testing, it should use `dataclasses.replace()`.
- The difficulty formulae are starting points. Phase 3 will refine them during playtesting. The key constraint is that the function is procedural — it must work for any level number, not just a fixed range.
- `ShipState.recalculate_effective_stats()` needs to accept the upgrade definitions list to compute stat bonuses. The formula for each effective stat is: `base_stat + (upgrade_level * effect_per_level)`. The `repair` upgrade is special — it does not have a persistent stat; it applies a one-time shield restoration in the shop (handled by Phase 4's UpgradeManager).

---

#### Component: 1.7 - Audio Manager Skeleton & Rendering Foundation

**Priority**: Must-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 1.2: Project structure and window must exist
- 1.4: Persistence layer must exist (AudioManager reads volume settings from `GameSettings`)
- 1.6: Game config must exist (for window dimensions, rendering constants)

**Features**:
- Implement `AudioManager` with sound loading and volume-controlled playback — AI Agent
- Graceful no-op on missing sound files (no assets exist yet) — AI Agent
- Create starfield background renderer (pre-rendered to texture) — AI Agent
- Implement basic HUD text rendering utility — AI Agent
- Wire AudioManager and starfield into `VoidBreakerWindow` — AI Agent

**Description**:
Implements the audio playback infrastructure and the foundational rendering systems (starfield background and HUD text). The `AudioManager` loads `.wav` files from the assets directory and plays them at volume levels controlled by `GameSettings`. It gracefully handles missing files (Phase 1 has no actual sound assets). The starfield is pre-rendered to a texture at startup for efficient per-frame drawing. The HUD renderer provides utility functions for drawing text overlays (score, shields, level, currency).

**Acceptance Criteria**:
- [ ] `AudioManager` initialises without errors even with an empty `assets/sounds/` directory
- [ ] `AudioManager.play("nonexistent_sound")` is a no-op (no exception, no error log)
- [ ] `AudioManager.play("fire")` respects `sfx_volume * master_volume` when files exist
- [ ] Starfield renders as a star-dotted background behind all game content
- [ ] Starfield is rendered once to a texture, not redrawn every frame
- [ ] `HUDRenderer.draw_text()` renders text at specified screen positions
- [ ] HUD text updates only when its displayed value changes (not every frame)
- [ ] Window now renders starfield background instead of plain black

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/app/src/audio/__init__.py` (modify — export `AudioManager`)
  - `asterax/app/src/audio/audio_manager.py` (create)
  - `asterax/app/src/rendering/__init__.py` (modify — export `StarfieldRenderer`, `HUDRenderer`)
  - `asterax/app/src/rendering/starfield.py` (create)
  - `asterax/app/src/rendering/hud.py` (create)
  - `asterax/app/src/window.py` (modify — wire starfield and HUD into draw pipeline)
- **Key Functions/Classes**:
  - `AudioManager.__init__(settings: GameSettings, sound_dir: Path)`
  - `AudioManager.play(name: str, volume_override: float | None = None) -> None`
  - `AudioManager.update_settings(settings: GameSettings) -> None`
  - `StarfieldRenderer.__init__(width: int, height: int, star_count: int = 200)`
  - `StarfieldRenderer.draw() -> None`
  - `HUDRenderer.__init__(window_width: int, window_height: int)`
  - `HUDRenderer.draw_text(text: str, x: float, y: float, ...) -> None`
  - `HUDRenderer.draw_value(label: str, value: int | float, x: float, y: float) -> None`
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: arcade (sound API, texture creation, text rendering)

**Detailed Implementation Requirements**:

- **File: `asterax/app/src/audio/audio_manager.py`**: The `AudioManager` class constructor accepts a `GameSettings` instance and a `Path` to the sounds directory. Store both as instance attributes. Initialise `self._sounds: dict[str, arcade.Sound] = {}`. In the constructor, attempt to load all `.wav` files from the sound directory using `arcade.load_sound()`. For each file found, store it keyed by its stem name (e.g., `fire.wav` -> `"fire"`). If the sound directory does not exist or is empty, log a debug message and continue (no error). If an individual file fails to load, log a warning and skip it. The `play(name, volume_override)` method: if `name` not in `self._sounds`, return immediately (no-op). Otherwise, compute `effective_volume = (volume_override or self._settings.sfx_volume) * self._settings.master_volume`, clamp to `[0.0, 1.0]`, and call `arcade.play_sound(self._sounds[name], volume=effective_volume)`. Add a separate `play_music(name)` method stub that will support streaming playback in Phase 5. The `update_settings(settings)` method replaces the internal settings reference — used when the player changes volume in the Settings screen.

- **File: `asterax/app/src/rendering/starfield.py`**: The `StarfieldRenderer` class generates a static starfield texture at initialisation. Constructor accepts `width`, `height`, and `star_count` (default 200). Use a seeded `random.Random(42)` for deterministic star placement. Generate star positions and brightnesses. Create the starfield as an `arcade.Texture` by rendering stars onto a pixel array or by using Arcade's `arcade.create_line()` / point rendering to a framebuffer. The simplest approach: create a list of `(x, y, brightness)` tuples and render them as small white points with varying alpha. Store the result in `self._texture`. If Arcade's offscreen rendering is complex, an acceptable alternative is to store the star data and render as a `arcade.ShapeElementList` of points (this is batched and nearly as fast as a texture). The `draw()` method draws the pre-computed starfield. Stars should have 2-3 brightness levels (dim, medium, bright) to create depth. Optionally, a very subtle parallax scroll can be added later, but for Phase 1 the starfield is completely static.

- **File: `asterax/app/src/rendering/hud.py`**: The `HUDRenderer` class provides convenience methods for drawing text on screen. Constructor accepts `window_width` and `window_height` for positioning calculations. Implement `draw_text(text, x, y, color=arcade.color.WHITE, font_size=14, anchor_x="left", anchor_y="baseline")` wrapping `arcade.draw_text()`. Implement `draw_value(label, value, x, y)` that formats and draws a label-value pair (e.g., "Score: 1234"). Implement a simple caching mechanism: maintain a dict of `{(label, value): arcade.Text}` objects. Use `arcade.Text` (Arcade 3.x's cached text object) to avoid re-creating text geometry every frame. When the value changes, update the `arcade.Text` object. This is critical for performance at 60fps — `arcade.draw_text()` is expensive if called with new strings every frame, but `arcade.Text.draw()` is cheap.

- **File: `asterax/app/src/window.py` (modifications)**: After the `StateMachine` is wired in (component 1.3), add `StarfieldRenderer` and `HUDRenderer` initialisation in the `VoidBreakerWindow.__init__()`. In `on_draw()`, call `starfield.draw()` before delegating to the state machine's draw. The `AudioManager` should also be initialised here and stored as an instance attribute accessible to states. Pass `AudioManager`, `StarfieldRenderer`, and `HUDRenderer` to states that need them via the `StateMachine` or as window attributes. Note: the exact wiring pattern depends on how component 1.3 structures state access to shared resources. The simplest approach is to store these on the window instance and have `BaseState` hold a reference to the window.

**Test Requirements**:
- [ ] Unit tests: `AudioManager` initialises without errors with empty sound directory
- [ ] Unit tests: `AudioManager.play("nonexistent")` does not raise
- [ ] Unit tests: `AudioManager.update_settings()` updates volume for subsequent plays
- [ ] Unit tests: `StarfieldRenderer` generates deterministic star positions (seeded RNG)
- [ ] Unit tests: `StarfieldRenderer` generates the correct number of stars
- [ ] Unit tests: `HUDRenderer.draw_text()` can be called without errors (mock arcade context if needed)
- [ ] Unit tests: HUD caching — same label/value does not recreate text object

**Definition of Done**:
- [ ] `AudioManager` fully implemented with graceful missing-file handling
- [ ] `StarfieldRenderer` renders a static starfield background
- [ ] `HUDRenderer` provides cached text rendering utilities
- [ ] All three systems wired into `VoidBreakerWindow`
- [ ] Tests written and passing
- [ ] Documentation created: `docs/components/phase-1-component-1-7-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`
- [ ] No regression in existing functionality
- [ ] Core application is still working post component implementation

**Notes**:
- Arcade 3.x has significantly changed its text rendering API. Use `arcade.Text` objects for cached rendering, not `arcade.draw_text()` in the hot path. `arcade.draw_text()` is fine for stub states (component 1.3) that render a few static strings, but the HUD must use `arcade.Text` for performance.
- The `AudioManager` must NOT crash if pyglet/OpenAL is unavailable (e.g., in a headless test environment). Wrap `arcade.load_sound()` and `arcade.play_sound()` in try/except blocks that log and continue.
- The starfield seed (42) ensures reproducible visuals across runs. This is a minor detail but helps with visual regression testing.
- When modifying `window.py`, preserve the existing fixed-timestep accumulator and state machine delegation from components 1.2 and 1.3. Only add starfield/HUD/audio initialisation and starfield draw call.

---

#### Component: 1.8 - E2E Testing & Documentation

**Priority**: Must-have

**Estimated Effort**: 5 hours

**Owner**: AI Agent

**Dependencies**:
- 1.2, 1.3, 1.4, 1.5, 1.6, 1.7: All prior components must be complete

**Features**:
- Create pytest `conftest.py` with shared fixtures — AI Agent
- Write unit tests for state machine transitions — AI Agent
- Write unit tests for persistence round-trip, corrupt file handling, schema versioning — AI Agent
- Write unit tests for input manager key tracking and bindings — AI Agent
- Write unit tests for config defaults and difficulty scaling — AI Agent
- Write unit tests for audio manager initialisation — AI Agent
- Run full test suite and verify 30%+ coverage on implemented modules — AI Agent
- Create `implementation-context-phase-1.md` with component summaries — AI Agent
- Create component overview docs for each component — AI Agent

**Description**:
The final component writes the comprehensive test suite for all Phase 1 modules and produces all required documentation. Tests are written using pytest with fixtures defined in `conftest.py`. The test suite must achieve 30%+ code coverage on all implemented modules. Documentation includes component overview files for each of the 8 components and the phase implementation context document.

**Acceptance Criteria**:
- [ ] `pytest` passes with 0 failures
- [ ] Code coverage >= 30% on `asterax/app/src/` modules (measured by `pytest --cov=asterax/app/src`)
- [ ] `conftest.py` provides reusable fixtures: `game_settings`, `persistence_manager` (with `tmp_path`), `input_manager`, `game_config`, `game_state`
- [ ] State machine tests cover: switch, push, pop, empty stack, draw-all-in-stack
- [ ] Persistence tests cover: round-trip, corrupt file, missing file, future version
- [ ] Input tests cover: key press/release tracking, action held query, binding lookup, rebinding
- [ ] Config tests cover: default values, difficulty scaling, upgrade cost calculation
- [ ] Audio tests cover: initialisation with missing directory, play with missing sound
- [ ] `docs/implementation-context-phase-1.md` exists with summaries of all 8 components
- [ ] `docs/components/phase-1-component-1-X-overview.md` exists for each component (1.1 through 1.8)
- [ ] `scripts/evals.py` passes (no TODO/FIXME, all public functions have docstrings)

**Technical Details**:
- **Files to Create/Modify**:
  - `asterax/tests/conftest.py` (create)
  - `asterax/tests/test_state_machine.py` (create)
  - `asterax/tests/test_persistence.py` (create)
  - `asterax/tests/test_input.py` (create)
  - `asterax/tests/test_config.py` (create)
  - `asterax/tests/test_audio.py` (create)
  - `docs/implementation-context-phase-1.md` (create)
  - `docs/components/phase-1-component-1-1-overview.md` (create)
  - `docs/components/phase-1-component-1-2-overview.md` (create)
  - `docs/components/phase-1-component-1-3-overview.md` (create)
  - `docs/components/phase-1-component-1-4-overview.md` (create)
  - `docs/components/phase-1-component-1-5-overview.md` (create)
  - `docs/components/phase-1-component-1-6-overview.md` (create)
  - `docs/components/phase-1-component-1-7-overview.md` (create)
  - `docs/components/phase-1-component-1-8-overview.md` (create)
- **Key Functions/Classes**: pytest fixtures and test functions
- **Human/AI Agent**: Entirely AI Agent
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: pytest, pytest-cov

**Detailed Implementation Requirements**:

- **File: `asterax/tests/conftest.py`**: Define the following shared fixtures. `game_settings() -> GameSettings`: returns a `GameSettings()` with all defaults. `persistence_manager(tmp_path) -> PersistenceManager`: returns a `PersistenceManager(base_dir=tmp_path)` so tests write to a temporary directory. `input_manager(game_settings) -> InputManager`: returns an `InputManager(game_settings)`. `game_config() -> GameConfig`: returns the `GAME_CONFIG` singleton. `game_state() -> GameState`: returns a `GameState` with default values. `mock_state_machine() -> StateMachine`: returns a `StateMachine` instance for testing state transitions without a window.

- **File: `asterax/tests/test_state_machine.py`**: Test `switch_state`: verify `on_exit` called on old state, `on_enter` called on new state (use mock/spy states). Test `push_state`: verify underlying state's `on_exit` is called, new state's `on_enter` is called, stack depth increases. Test `pop_state`: verify popped state's `on_exit` is called, revealed state's `on_enter` is called, stack depth decreases. Test `draw`: verify all states in stack have `on_draw` called (bottom to top order). Test `update` and `on_key_press`: verify only top state receives calls. Test empty stack: verify all operations are no-ops without exceptions. Test double-pop: verify popping an empty stack is a no-op. Use simple test double classes that record method calls.

- **File: `asterax/tests/test_persistence.py`**: Test `load_settings` with no file: returns defaults. Test `save_settings` + `load_settings` round-trip: all fields match. Test corrupt JSON file: returns defaults (write garbage bytes to the settings path, then load). Test missing keys in JSON: returns defaults for missing fields, preserves present fields. Test future version: returns defaults (write JSON with `"version": 999`). Test `save_high_scores` + `load_high_scores` round-trip. Test empty high scores: returns empty list. Test high scores capping (if implemented): save 200 entries, load, verify capped to max. Test atomic write: verify settings file exists and is valid after save (no temp file remnants). All tests use the `persistence_manager` fixture with `tmp_path`.

- **File: `asterax/tests/test_input.py`**: Test `on_key_press` adds to `keys_held`. Test `on_key_release` removes from `keys_held`. Test `on_key_release` with unheld key does not raise. Test `is_action_held` returns True when bound key is held. Test `is_action_held` returns False when bound key is not held. Test `get_binding` returns correct Arcade key code for default bindings. Test `update_bindings` with new settings changes the active binding. Test invalid key name in settings logs warning and uses default.

- **File: `asterax/tests/test_config.py`**: Test `GAME_CONFIG` has expected default values (spot-check physics constants). Test all `UpgradeDefinition` entries have valid fields. Test `get_upgrade_cost` returns expected values at different levels. Test `get_difficulty` returns sensible values for levels 1, 5, 10, 20, 50. Test `get_difficulty` values are clamped for extreme levels. Test "casual" is easier than "classic" on key metrics (asteroid count, enemy aggression). Test "hard" is harder than "classic". Test all dataclass models instantiate with defaults. Test all enums have expected members.

- **File: `asterax/tests/test_audio.py`**: Test `AudioManager` initialises without errors when sound directory is empty. Test `AudioManager` initialises without errors when sound directory does not exist. Test `AudioManager.play("nonexistent")` does not raise. Test `AudioManager.update_settings()` stores new settings. Note: actual sound playback cannot be tested without a display/audio context. Tests verify construction and method calls, not actual audio output.

- **File: `docs/implementation-context-phase-1.md`**: Summarise each of the 8 components in Phase 1 with: what was built, key patterns established, important file locations, and any decisions made during implementation. Maximum 100 lines per component. Total document should be a concise reference for Phase 2+ developers.

- **File: `docs/components/phase-1-component-1-X-overview.md`** (one per component): Brief overview of the component: purpose, files created/modified, key classes/functions, patterns established, and notes for future phases.

**Test Requirements**:
- [ ] All test files execute via `pytest` without failures
- [ ] `pytest --cov=asterax/app/src --cov-report=term-missing` shows >= 30% coverage
- [ ] `python asterax/scripts/evals.py` exits 0
- [ ] `black --check asterax/` exits 0
- [ ] `isort --check-only asterax/` exits 0

**Definition of Done**:
- [ ] All test files created with comprehensive test cases
- [ ] 30%+ code coverage achieved
- [ ] All documentation files created
- [ ] `evals.py`, `black`, `isort` all pass
- [ ] No regression — all tests pass, application still launches correctly
- [ ] Documentation created: `docs/components/phase-1-component-1-8-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-1.md`

**Notes**:
- Tests that require an Arcade window or audio context should be skipped or mocked. Use `unittest.mock.MagicMock` for Arcade objects that require a display context. The state machine tests should work entirely with mock state objects, not real Arcade-dependent states.
- The 30% coverage target applies to the `asterax/app/src/` directory. Pure data model files (config, schemas) are easy to test and will contribute significantly to coverage. State stubs and window code are harder to test without a display and may have lower individual coverage.
- `conftest.py` fixtures should use `@pytest.fixture` with appropriate scopes. The `persistence_manager` fixture must use `tmp_path` (function-scoped by default) to ensure test isolation.
- Documentation should be written in Markdown and be concise. Avoid repeating the full specification — reference `phase-1-component-breakdown.md` for details. Focus on what was actually built (post-implementation), decisions made, and patterns established.

---

## Cross-Phase Contracts Established by Phase 1

The following contracts are established by Phase 1 and must be honoured by all subsequent phases:

### 1. State Machine Protocol
```python
class GameState(Protocol):
    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def on_update(self, delta_time: float) -> None: ...
    def on_draw(self) -> None: ...
    def on_key_press(self, key: int, modifiers: int) -> None: ...
    def on_key_release(self, key: int, modifiers: int) -> None: ...
```
All states in Phases 2-5 must implement this protocol by extending `BaseState`.

### 2. Entry Point
`python -m asterax.app.src.main` is the canonical launch command. No other entry point.

### 3. Configuration Pattern
All tuning constants go in `asterax/app/src/config/game_config.py`. No hardcoded magic numbers in game logic modules.

### 4. Persistence Pattern
`PersistenceManager` is the sole interface for file I/O. No other module reads/writes files to the user data directory.

### 5. Input Pattern
`InputManager.keys_held` is the source of truth for continuous key state. `InputManager.is_action_held(action)` is the preferred API for checking actions. States receive discrete events via `on_key_press`/`on_key_release`.

### 6. Audio Pattern
`AudioManager.play(name)` is the sole interface for sound playback. Missing files are no-ops.

### 7. Directory Structure
Exact package layout from solution-design.md. New files in subsequent phases go into their designated packages.

### 8. Import Convention
Absolute imports only: `from asterax.app.src.config.game_config import GAME_CONFIG`. No relative imports.
