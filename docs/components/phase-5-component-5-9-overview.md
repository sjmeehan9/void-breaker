# Component 5.9 — Difficulty Presets Integration

## Summary

Implemented three difficulty presets (Casual, Classic, Hard) with multiplicative modifiers applied over Phase 3 tier-based difficulty scaling. New Game now prompts for difficulty selection with persisted settings.

## Key Deliverables

- **DifficultyPreset** enum and **DifficultyMultipliers** dataclass in `difficulty_tables.py`.
- Preset multipliers: Casual (0.7× asteroids, 0.6× aggression, 1.5× currency, 1.4× spawn interval), Classic (1.0×), Hard (1.4× asteroids, 1.3× aggression, 0.7× currency, 0.7× spawn interval).
- **DifficultyScaler** class with `apply_preset()` and `for_level()` methods.
- Main menu New Game sub-prompt for difficulty selection with persisted default.
- Combat runtime applies preset-adjusted parameters per level.
- High score entries include difficulty field with backward-compatible "classic" default.

## Files Modified

- `app/src/config/difficulty_tables.py` — preset definitions, multiplier application
- `app/src/managers/difficulty_scaler.py` — scaler class
- `app/src/states/main_menu.py` — difficulty selection sub-prompt
- `app/src/states/combat.py` — preset-aware spawning and damage/currency multipliers
- `app/src/persistence/schemas.py` — backward-compatible difficulty field

## Design Decisions

- Multiplicative presets preserve Phase 3 difficulty curve while shifting baseline.
- Enemy aggression multiplier applied to both `enemy_aggression` and `aggressive_ratio`.
- Currency multiplier integrated through collision drop override for consistency.
