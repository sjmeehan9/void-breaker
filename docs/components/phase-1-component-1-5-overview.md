# Phase 1 Component 1.5 Overview: Input Manager

## Summary
Component 1.5 adds a dedicated `InputManager` that tracks currently-held keys and resolves action bindings from persisted settings.

## Delivered Scope
- Added `app/src/input/input_manager.py` with:
  - `KEY_NAME_MAP` for required key names (arrows, SPACE/SHIFT/ESCAPE/ENTER/BACKSPACE/TAB, A-Z, KEY_0..KEY_9).
  - `InputManager` methods: `on_key_press`, `on_key_release`, `is_action_held`, `get_binding`, `update_bindings`.
  - Default action bindings: rotate_left/rotate_right/thrust/fire/brake/special/pause.
  - Warning + fallback to action defaults when settings contain invalid key names.
- Updated `app/src/input/__init__.py` to export `InputManager`.
- Updated `app/src/window.py` to:
  - load settings via `PersistenceManager`,
  - initialize `InputManager` from those settings,
  - route key events through `InputManager` before `StateMachine`.

## Test Coverage
- Added `tests/test_input.py` covering:
  - key press/release tracking in `keys_held`,
  - `is_action_held` behavior,
  - default `get_binding` resolution,
  - dynamic remap via `update_bindings`,
  - invalid-key fallback with warning,
  - required `KEY_NAME_MAP` entries.
- Updated `tests/test_window.py` to verify:
  - init order includes persistence load and input manager setup,
  - key events go to input manager first, then state machine.

## Design Notes
- Key bindings remain persisted as strings in settings (`GameSettings`) for readability and portability.
- `on_key_release` uses `discard()` to avoid `KeyError` during focus-loss edge cases.
- Event ordering guarantees held-key state is current before states process the key event.

## Deviations
None.
