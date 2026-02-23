# Phase 3 Component 3.5 — Damage Feedback & Visual Effects Overview

## Summary
Component 3.5 introduces combat feedback polish for player and enemy damage events. The implementation adds a new rendering-layer helper (`DamageEffects`) and wires it into the combat loop to deliver:

- Player hit feedback (red/white flash + `player_hit` SFX)
- Player invulnerability visual flicker (alpha oscillation) during the protection window
- Enemy destruction bursts (particles + `enemy_explode` SFX)
- Player destruction burst with a delayed game-over transition (0.8s)

## Implementation Scope

### New Module
- `app/src/rendering/damage_effects.py`
  - `DamageEffects.trigger_damage_flash(sprite)`
  - `DamageEffects.trigger_invulnerability(ship, duration)`
  - `DamageEffects.trigger_explosion(position, size, particle_list)`
  - `DamageEffects.trigger_destruction_sequence(position, particle_list)`
  - `DamageEffects.update(dt)`

### Combat Integration
- `app/src/states/combat.py`
  - Instantiates `DamageEffects`
  - Updates damage effects each physics step
  - Applies player hit effects/sound through `_apply_player_damage()`
  - Emits enemy destruction effects in `_handle_enemy_destroyed()`
  - Adds `0.8s` delay before game-over state switch when shields reach zero

### Player Invulnerability Behavior
- `app/src/entities/player_ship.py`
  - Adds `is_invulnerable` property
  - Uses config-defined invulnerability duration
  - Provides explicit `update_invulnerability(dt)` timer advancement

### Config & Rendering Updates
- `app/src/config/game_config.py`
  - `invulnerability_duration` set to `0.75` seconds
- `app/src/rendering/particle_system.py`
  - Particle update loop now supports any particle implementing `update_particle(dt)`

## Test Coverage Added
- `tests/test_damage_effects.py`
  - Flash restoration
  - Explosion particle count range
  - Particle expiry/removal
- `tests/test_player_ship_physics.py`
  - Damage ignored during invulnerability
  - Invulnerability expiry after configured duration
- `tests/test_enemy_projectile_collisions.py`
  - Combat hit feedback + invulnerability gate behavior
- `tests/test_combat_phase_state.py`
  - Delayed game-over transition timing behavior

## Notes
- Effects are sprite-based and particle-list based to stay consistent with existing rendering architecture.
- Audio playback in combat now uses a guarded helper to avoid failures in headless test execution.
