# Component 5.10 — Practice/Training Mode

## Summary

Added a low-stakes practice mode accessible from the main menu with configurable toggles for asteroids-only, infinite shields, and reduced asteroid count. Practice mode reuses `CombatPhaseState` with explicit flags.

## Key Deliverables

- **PracticeConfigState**: toggle UI with keyboard navigation and combat launch wiring.
- Toggles: `asteroids_only` (disables enemy spawning), `infinite_shields` (suppresses damage), `reduced_count` (halves asteroid count).
- Practice combat skips shop transitions and auto-advances levels.
- Non-lethal respawn on practice death instead of game-over flow.
- Game-over screen skips leaderboard/name-entry for practice runs.
- HUD displays "PRACTICE" label during practice mode.

## Files Created

- `app/src/states/practice_config.py` — practice configuration state
- `tests/test_practice_mode.py` — practice param building and game-over flow tests

## Files Modified

- `app/src/states/main_menu.py` — added "Practice" menu option
- `app/src/states/combat.py` — practice flags, enemy suppression, infinite shields, respawn
- `app/src/states/game_over.py` — `is_practice` support, skip leaderboard
- `app/src/rendering/hud.py` — "PRACTICE" label rendering
- `app/src/config/game_config.py` — `GameState.is_practice` flag

## Design Decisions

- Practice reuses `CombatPhaseState` with flags to avoid duplicating combat systems.
- Shop transitions intentionally skipped during practice.
- "Play Again" from practice game-over returns to practice config, not regular game.
