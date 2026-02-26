# Phase 5 Component 5.3 — How-to-Play & High Scores Screens

**Status**: Completed  
**Owner**: AI Agent  
**Date**: 2026-02-27

## Summary

Component 5.3 replaces both informational screen stubs with production implementations. The How-to-Play screen now renders dynamic control bindings from the active `InputManager`, explains the core combat-to-shop gameplay loop, documents insurance behavior, and includes concise play tips with vertical scrolling. The High Scores screen now loads persistent leaderboard entries, sorts by descending score, displays a top-10 table with rank/name/score/level/difficulty/date, supports empty-state messaging, and allows difficulty filter cycling when multiple difficulty buckets are present.

## Delivered Files

- `app/src/states/how_to_play.py` — full `HowToPlayState` implementation with:
  - `on_enter()` scroll reset and content bounds calculation
  - `on_draw()` multi-section instructional layout rendered with `MenuRenderer` title style
  - `_build_controls_text()` driven by live input bindings
  - Escape/Backspace/pause-key return to `MainMenuState`
  - Up/Down scrolling for long content
- `app/src/states/high_scores.py` — full `HighScoresState` implementation with:
  - `_load_scores()` from persistence and descending score sort
  - `_current_filter` and `_cycle_filter()` support for `all/casual/classic/hard`
  - top-10 leaderboard table rendering and re-ranked filtered rows
  - empty leaderboard fallback message
  - Escape/Backspace/pause-key return to `MainMenuState`
- `tests/test_how_to_play.py` — unit coverage for dynamic controls text and back navigation
- `tests/test_high_scores.py` — unit coverage for score sorting, difficulty filtering, and empty-state behavior

## Validation

- `black --check app/src/states/how_to_play.py app/src/states/high_scores.py tests/test_how_to_play.py tests/test_high_scores.py`
- `isort --check-only app/src/states/how_to_play.py app/src/states/high_scores.py tests/test_how_to_play.py tests/test_high_scores.py`
- `pytest -q tests/test_how_to_play.py tests/test_high_scores.py`

All targeted checks passed.

## Notes

- Difficulty filter controls are visible and active only when loaded scores include more than one difficulty value.
- How-to-Play control labels are generated from active key bindings, so updates from settings remapping automatically reflect here.