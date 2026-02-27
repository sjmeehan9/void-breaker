# Component 5.6 — Pause System

## Summary

Replaced the Phase 1 pause stub with a full overlay pause menu that freezes all game logic underneath while remaining visually transparent (game world visible behind the dimmed overlay).

## Key Deliverables

- **PauseState** overlay with four options: Resume, Restart Run, Settings, Exit to Menu.
- Overlay push/pop semantics: underlying state's `on_update()` is blocked while paused; `on_draw()` still propagates for visual continuity.
- Pause triggered via configured pause key binding with Escape fallback.
- Settings opened from pause pushes `SettingsScreenState` with `return_to="pause"`, which pops back to the pause overlay on exit.
- Combat and shop states both support pause activation.

## Files Modified

- `app/src/states/pause.py` — full implementation
- `app/src/states/combat.py` — pause key trigger
- `app/src/states/shop.py` — pause key trigger
- `app/src/states/settings_screen.py` — pause return via `pop_state()`
- `app/src/states/state_machine.py` — overlay update semantics (top-state only)

## Files Created

- `tests/test_pause.py` — overlay lifecycle and action routing tests

## Design Decisions

- Pause/settings treated as true overlays (push/pop) to preserve run state without reinitialisation.
- Draw-through stack with top-state-only updates satisfies freeze requirements.
- Pause key lookup with Escape fallback supports lightweight test stubs.
