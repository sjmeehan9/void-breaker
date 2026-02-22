# Phase 1 Component 1.7 Overview: Audio Manager Skeleton & Rendering Foundation

## Summary
Component 1.7 delivers the foundational audio/rendering infrastructure required before gameplay entities are introduced in later phases.

## Delivered Scope
- Added `app/src/audio/audio_manager.py`:
  - `AudioManager` loads `.wav` files from `assets/sounds`.
  - Missing/empty sound directories are handled as non-fatal no-ops.
  - `play()` applies `master_volume * sfx_volume` (or explicit override), clamps to `[0.0, 1.0]`, and safely handles backend/playback errors.
  - `update_settings()` swaps runtime settings references.
  - `play_music()` exists as a stable API entry point for future streamed music support.
- Added `app/src/rendering/starfield.py`:
  - `StarfieldRenderer` builds deterministic static stars using seeded RNG (`42`).
  - Star geometry is precomputed once into a `ShapeElementList` and drawn each frame as a batched background layer.
- Added `app/src/rendering/hud.py`:
  - `HUDRenderer.draw_text()` wraps one-off text rendering.
  - `HUDRenderer.draw_value()` caches `arcade.Text` by label/position and only rebuilds when value changes.
- Updated `app/src/window.py`:
  - Window defaults now source width/height/title from `GAME_CONFIG`.
  - Instantiates `AudioManager`, `StarfieldRenderer`, and `HUDRenderer`.
  - Draw pipeline now renders starfield before active state visuals.

## Test Coverage
- Added `tests/test_audio_rendering.py` to cover:
  - Audio manager init with empty directory.
  - Missing-sound playback no-op behavior.
  - Settings update affecting subsequent playback volume.
  - Starfield deterministic generation and star-count correctness.
  - HUD draw-text call-through behavior.
  - HUD value-cache reuse for unchanged label/value pairs.
- Updated `tests/test_window.py`:
  - Verifies new subsystem initialization order.
  - Verifies starfield draw occurs between window clear and state draw.

## Deviations
- No functional deviations from the component spec.
