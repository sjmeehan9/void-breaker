# Phase 3 Component 3.6 — Difficulty Scaling & Balance Overview

## Summary
Component 3.6 replaces formula-only difficulty tuning with a tier-based interpolation system that is easier to balance and explicitly capped for fairness. The implementation now defines fixed tuning breakpoints and interpolates intermediate levels, while preserving existing difficulty mode multipliers (`casual`, `classic`, `hard`).

## What Was Implemented

### Tiered Difficulty Model
- Added `DIFFICULTY_TIERS` in `app/src/config/difficulty_tables.py` at levels:
  - `1`, `5`, `10`, `15`, `20`, `25`, `30`
- Each tier includes:
  - asteroid density/speed
  - enemy spawn controls (enabled, cap, interval, aggression, aggressive ratio)
  - currency economy values (drop chance and base value)

### Interpolation Helpers
- Added `_interpolate()` scalar helper.
- Added `_interpolate_params()` to produce per-level `DifficultyParams` between adjacent tier boundaries.
- Integer fields (`asteroid_count`, `enemy_count_max`, `currency_value_base`) are rounded from interpolated values.

### Difficulty Caps and Entry Point
- `get_difficulty_params(level)` now:
  - clamps input to level range `1..30`
  - returns exact tier values at breakpoint levels
  - interpolates between breakpoints for all in-between levels
  - returns level-30 values for all levels above 30 (fairness cap)

### Early Enemy Activation Bridge
- Added enemy-field bridge behavior in the 5→10 transition so levels `6+` spawn enemies immediately with practical values.
- This avoids inheriting level-5 sentinel values (`enemy_spawn_interval=99`) after enemy spawning activates.

## Files Updated
- `app/src/config/difficulty_tables.py`
- `tests/test_difficulty.py`
- `tests/test_asteroid_system.py`
- `tests/test_config.py`

## Test Coverage Added/Adjusted
- Exact tier-value assertions for levels 1 and 30.
- Interpolation assertion for level 7.
- Enemy-spawn threshold assertion (`<=5` off, `>=6` on).
- Level-cap assertion (`50 == 30` values).
- Monotonic progression checks for asteroid and enemy counts.
- Global bounds checks across levels 1–50.
- Existing asteroid/config tests aligned to new level-1 and level-30 targets.

## Result
Difficulty progression is now:
- smoother to tune,
- explicitly balanced across early/mid/late game,
- and capped at level 30 to remain intense but fair in endless play.
