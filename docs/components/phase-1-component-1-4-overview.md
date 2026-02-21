# Phase 1 Component 1.4 Overview: Persistence Layer

## Summary
Component 1.4 delivers a production-ready persistence layer for settings and high scores. The implementation introduces typed schemas, versioned JSON payloads, and atomic file writes so persistence is durable and safe against partial-write corruption.

## Delivered Scope
- Added `GameSettings` and `HighScoreEntry` dataclasses in `app/src/persistence/schemas.py`.
- Added schema version constants: `SETTINGS_VERSION` and `HIGH_SCORES_VERSION`.
- Implemented `PersistenceManager` in `app/src/persistence/persistence_manager.py` with:
  - platform-appropriate user data directory resolution via `platformdirs.user_data_dir("VoidBreaker", appauthor=False)`
  - injectable `base_dir` override for deterministic tests
  - `load_settings` / `save_settings`
  - `load_high_scores` / `save_high_scores`
  - atomic save path using `tempfile.NamedTemporaryFile` + `os.replace`
  - warning-based fallback behavior for missing files, corrupt JSON, invalid payloads, and future schema versions
  - high-score write capping to 100 entries
- Exported `PersistenceManager` from `app/src/persistence/__init__.py`.
- Added `app/config/settings_defaults.yaml` as human-readable reference defaults.

## Validation
- Added `tests/test_persistence.py` covering:
  - default settings schema values
  - dataclass dict serialisation round-trips
  - missing-file defaults
  - settings save/load round-trip
  - corrupt JSON fallback
  - missing-key default behavior
  - future-version fallback
  - high-score save/load round-trip
  - empty high-score default
  - atomic-write no-temp-file behavior

## Integration Notes
This layer is now the single persistence entry point for later components (input, audio, settings UI, high score screen), consistent with the phase persistence pattern.
