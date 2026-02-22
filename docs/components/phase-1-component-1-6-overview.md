# Phase 1 Component 1.6 Overview: Game Config & Data Models

## Summary
Component 1.6 establishes the authoritative configuration/data-model layer used by gameplay systems and later managers.

## Delivered Scope
- Added `app/src/config/game_config.py` with:
  - `GameConfig` frozen dataclass and `GAME_CONFIG` singleton.
  - Required enums: `GamePhase`, `AsteroidSize`, `EnemyArchetype`, `UpgradeCategory`, `InsuranceTier`.
  - Core run-state dataclasses: `GameState`, `ShipState`, `InsuranceState`, `DifficultyParams`, `LevelStats`, `RunStats`.
  - `ShipState.recalculate_effective_stats()` to recompute effective stats from upgrade levels.
- Added `app/src/config/upgrade_definitions.py` with:
  - `UpgradeDefinition` dataclass.
  - Full `UPGRADE_DEFINITIONS` catalog (weapon/defense/mobility/economy/repair).
  - Helpers: `get_upgrade_cost()` and `get_upgrade_by_id()`.
- Added `app/src/config/difficulty_tables.py` with procedural `get_difficulty(level, base)` scaling and mode multipliers.
- Updated `app/src/config/__init__.py` to export the config/model API.

## Test Coverage
- Added `tests/test_config.py` covering:
  - `GAME_CONFIG` defaults.
  - Upgrade definition integrity and geometric cost scaling.
  - Difficulty scaling across representative levels and extreme-level clamp behavior.
  - Relative difficulty mode behavior (casual vs classic vs hard).
  - Default dataclass construction for all required models.
  - `ShipState` effective-stat recalculation.
  - Enum member completeness.

## Design Notes
- Difficulty values are generated formulaically (no hardcoded table), enabling infinite-level progression tuning.
- Upgrade application is definition-driven, so future upgrades can be added by extending the static definition list.
- `ShipState` tracks both base and effective values to keep runtime mutation isolated from immutable defaults.

## Deviations
- None functionally; implementation includes explicit effective fields for shield capacity and projectile count to model specified upgrade effects directly.
