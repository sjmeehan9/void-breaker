# Phase 2 Component 2.7 Overview — Combat Phase State & Level Progression

## Summary
Component 2.7 delivers the playable Phase 2 combat lifecycle by replacing stubbed states with integrated game-loop behavior:

- `CombatPhaseState` now wires entity, physics, collision, spawn, score, currency, particle, and HUD systems together.
- A fixed-timestep accumulator (`1/60s`, capped frame time) is used for deterministic simulation updates.
- Level clear detection (`asteroid` list empty) advances to the next level, clears transient entities, and respawns scaled asteroid waves.
- Ship shield depletion triggers a `GameOverState` transition with run-summary payload (score/level/currency totals).
- `GameOverState` now renders run summary text and persists qualifying high scores through `PersistenceManager`.
- HUD now displays cached combat overlay text for score, level, shields, and credits using lazy `arcade.Text` regeneration.

## Implemented Files
- `app/src/states/combat.py`
- `app/src/states/game_over.py`
- `app/src/rendering/hud.py`
- `tests/test_combat_phase_state.py`
- `docs/implementation-context-phase-2.md`

## Key Design Choices
- Kept lower-level managers unchanged and performed orchestration in combat state methods to keep the change surgical.
- Added a dedicated `RunSummary` dataclass in `game_over.py` to keep render/persistence fields explicit and typed.
- Preserved prior HUD utility methods and layered combat HUD behavior without breaking existing rendering tests.

## Validation
- `python -m pytest -q tests/test_combat_phase_state.py tests/test_audio_rendering.py tests/test_window.py`
- `python -m black --check app/src tests`
- `python -m isort --check-only app/src tests`
- `python -m pytest -q`
- `python scripts/evals.py`
