# Component 5.7 — Audio Integration & Particle Effects

## Summary

Integrated all sound effects across combat, shop, and collision flows via typed wrapper methods on `AudioManager`. Replaced the basic explosion-only particle system with a pooled, capped multi-effect `ParticleSystem` (300 particle hard cap).

## Key Deliverables

- **AudioManager wrapper methods**: `play_fire`, `play_hit`, `play_explosion(size)`, `play_enemy_explode`, `play_enemy_fire`, `play_pickup_currency`, `play_pickup_buff`, `play_shop_purchase`, `play_shop_denied`, `play_level_clear`, `play_game_over`, `play_menu_nav`, `play_menu_select`, `play_shield_low`, `play_insurance_deduct`.
- **ParticleSystem**: pooled pre-allocation with `_PooledParticle` dataclass, five emitter types (explosion, thrust, sparkle, damage flash, purchase burst), oldest-particle recycling on pool exhaustion.
- Sound triggers wired to combat events, collision handlers, shop interactions, and menu navigation.

## Files Modified

- `app/src/audio/audio_manager.py` — wrapper methods added
- `app/src/rendering/particle_system.py` — full pooled rewrite
- `app/src/states/combat.py` — thrust emission, fire/hit/level-clear/enemy-explode audio
- `app/src/physics/collisions.py` — asteroid explosion SFX, pickup sparkle, damage flash
- `app/src/states/shop.py` — purchase bursts, insurance deduction SFX

## Design Decisions

- Wrapper methods fall back to `audio_manager.play(name)` for backward compatibility with test stubs.
- Pooled sprites remain permanently in `SpriteList`; activity toggled via alpha/position to avoid per-frame sprite allocation.
