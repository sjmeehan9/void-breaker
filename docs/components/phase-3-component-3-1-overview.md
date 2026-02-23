# Phase 3 Component 3.1 — Human Setup & Enemy Assets

## Overview

Component 3.1 delivers all placeholder visual and audio assets required for Phase 3 enemy combat. These assets are consumed by all subsequent Phase 3 components (3.2–3.8).

## Sprites Created

| File | Dimensions | Description |
|------|-----------|-------------|
| `assets/sprites/enemy_basic.png` | 64×64 RGBA | Red diamond — Basic Shooter enemy archetype |
| `assets/sprites/enemy_aggressive.png` | 64×64 RGBA | Orange chevron — Aggressive enemy archetype |
| `assets/sprites/projectile_enemy.png` | 8×8 RGBA | Red-orange dot — enemy projectile |

All sprites were generated using Pillow via `scripts/generate_placeholder_sprites.py`. They use transparent backgrounds and bright colours against the dark starfield.

## Sounds Present

| File | Format | Description |
|------|--------|-------------|
| `assets/sounds/enemy_fire.wav` | Stereo, 16-bit, 44100 Hz | Enemy weapon fire |
| `assets/sounds/enemy_explode.wav` | Stereo, 16-bit, 44100 Hz | Enemy destruction explosion |
| `assets/sounds/player_hit.wav` | Stereo, 16-bit, 44100 Hz | Player damage impact |

Sound files were provided by the developer and placed in the asset directory.

## Design Decisions

- **Extended existing script** rather than creating a new one — `generate_placeholder_sprites.py` now generates all Phase 2 + Phase 3 sprites from a single entry point.
- **Colour coding** — enemies use red/orange hues; player uses white/cyan; asteroids use grey. This provides immediate visual friend/foe identification.
- **Shape differentiation** — Basic Shooter (diamond) vs Aggressive (chevron) ensures the two archetypes are visually distinguishable at gameplay speed.
- **Enemy projectile** reuses the 8×8 size of the player projectile but with a red-orange colour instead of cyan.

## Verification

The `scripts/verify_assets.py` script was updated to include all Phase 3 assets. Running it confirms all 10 sprites and 11 sounds are present and valid.
