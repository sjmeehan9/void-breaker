# Phase 1 Component 1.3 Overview: State Machine

## Summary
Component 1.3 establishes the finite state machine foundation for VoidBreaker. The implementation introduces a formal `GameState` contract, a stack-based `StateMachine`, and nine concrete stub states that render placeholders and support keyboard-driven transitions.

## Delivered Scope
- Added `GameState` protocol and `BaseState` in `app/src/states/base_state.py`.
- Added `StateMachine` in `app/src/states/state_machine.py` with:
  - `switch_state(state)` for full replacement transitions.
  - `push_state(state)` / `pop_state()` for overlays (pause semantics).
  - Delegation methods for update/draw/input.
  - Safe no-op behavior when the state stack is empty.
- Implemented nine state stubs:
  - `MainMenuState`
  - `GameInitState`
  - `CombatPhaseState`
  - `ShopPhaseState`
  - `GameOverState`
  - `PauseState`
  - `HowToPlayState`
  - `HighScoresState`
  - `SettingsScreenState`
- Wired `VoidBreakerWindow` to instantiate the state machine, start in `MainMenuState`, and delegate update/draw/key events.
- Updated `app/src/states/__init__.py` exports for protocol, machine, and all concrete state classes.

## Transition Behavior
- Main menu shortcuts:
  - `1`/`Enter` -> `GameInit` -> `Combat`
  - `2` -> `How To Play`
  - `3` -> `High Scores`
  - `4` -> `Settings`
  - `Q` -> Close window
- Combat shortcuts:
  - `Escape` -> push `Pause`
  - `N` -> `Shop`
  - `G` -> `Game Over`
- Shop shortcuts:
  - `Escape` -> push `Pause`
  - `Enter` -> `Combat`
- Pause shortcuts:
  - `Escape` -> pop overlay (resume)
  - `R` -> restart via `GameInit`
  - `M` -> `Main Menu`

## Validation
- Added `tests/test_state_machine.py` for stack semantics, transition ordering, and delegation.
- Extended `tests/test_window.py` to validate state-machine bootstrap and event delegation from `VoidBreakerWindow`.
