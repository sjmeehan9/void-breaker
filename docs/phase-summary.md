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
