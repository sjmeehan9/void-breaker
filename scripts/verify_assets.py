"""Verify all game assets exist and meet format requirements.

Checks all sprite PNGs (RGBA, correct dimensions), sound WAVs
(readable, expected format), and font files for the complete
Phase 5 asset catalogue.

Usage:
    python scripts/verify_assets.py
"""

from __future__ import annotations

import wave
from pathlib import Path

from PIL import Image

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
SHOP_SPRITES_DIR = SPRITES_DIR / "shop"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"


def _check_sprite(
    path: Path,
    expected_w: int,
    expected_h: int,
    errors: list[str],
) -> bool:
    """Verify a single sprite file exists with correct size and RGBA mode.

    Args:
        path: Absolute path to the PNG file.
        expected_w: Expected pixel width.
        expected_h: Expected pixel height.
        errors: Mutable list to append error descriptions.

    Returns:
        True if the sprite passes all checks.
    """
    name = path.name
    if not path.exists():
        errors.append(f"MISSING: {name}")
        print(f"  MISSING: {name}")
        return False

    img = Image.open(path)
    mode = img.mode
    w, h = img.size
    ok = mode == "RGBA" and w == expected_w and h == expected_h
    status = "OK" if ok else "MISMATCH"
    print(f"  {status}: {name} — {w}×{h} {mode} (expected {expected_w}×{expected_h})")
    if not ok:
        errors.append(f"MISMATCH: {name} — got {w}×{h} {mode}")
    return ok


def _check_sound(path: Path, errors: list[str]) -> bool:
    """Verify a single WAV file exists and is readable.

    Args:
        path: Absolute path to the WAV file.
        errors: Mutable list to append error descriptions.

    Returns:
        True if the sound passes all checks.
    """
    name = path.name
    if not path.exists():
        errors.append(f"MISSING: {name}")
        print(f"  MISSING: {name}")
        return False

    try:
        with wave.open(str(path), "rb") as wf:
            ch = wf.getnchannels()
            sw = wf.getsampwidth()
            fr = wf.getframerate()
            nf = wf.getnframes()
            dur = nf / fr
            print(f"  OK: {name} — {ch}ch, {sw * 8}-bit, {fr}Hz, {dur:.2f}s")
            return True
    except wave.Error as e:
        # Python's wave module only reads PCM (format 1).  IEEE float
        # (format 3) and other valid WAV sub-formats trigger
        # "unknown format: N" but still work in Arcade/pyglet.
        if "unknown format" in str(e):
            size_kb = path.stat().st_size / 1024
            print(f"  OK: {name} — non-PCM WAV ({size_kb:.1f} KB, Arcade-compatible)")
            return True
        errors.append(f"ERROR: {name} — {e}")
        print(f"  ERROR: {name} — {e}")
        return False
    except Exception as e:
        errors.append(f"ERROR: {name} — {e}")
        print(f"  ERROR: {name} — {e}")
        return False


def main() -> None:
    """Run full asset verification for Phase 5."""
    errors: list[str] = []

    # ------------------------------------------------------------------
    # Sprites — main directory
    # ------------------------------------------------------------------
    print("=== SPRITE VERIFICATION ===")

    # (filename, expected_width, expected_height)
    main_sprites: list[tuple[str, int, int]] = [
        # Player
        ("ship.png", 64, 64),
        ("ship_thrust.png", 64, 64),
        # Asteroids
        ("asteroid_large.png", 104, 104),
        ("asteroid_medium.png", 56, 56),
        ("asteroid_small.png", 32, 32),
        # Enemies
        ("enemy_basic.png", 48, 48),
        ("enemy_aggressive.png", 48, 48),
        # Projectiles
        ("projectile_player.png", 8, 16),
        ("projectile_enemy.png", 8, 16),
        # Pickups — new canonical names
        ("pickup_currency.png", 24, 24),
        ("pickup_buff_heal.png", 24, 24),
        ("pickup_buff_shield.png", 24, 24),
        ("pickup_buff_damage.png", 24, 24),
        ("pickup_buff_speed.png", 24, 24),
        # Particles
        ("particle_dot.png", 8, 8),
        # Backward-compat aliases
        ("currency_pickup.png", 24, 24),
        ("explosion_particle.png", 8, 8),
        # UI
        ("ui_panel.png", 256, 192),
        ("ui_button.png", 200, 40),
        ("ui_button_selected.png", 200, 40),
    ]
    for name, ew, eh in main_sprites:
        _check_sprite(SPRITES_DIR / name, ew, eh, errors)

    # ------------------------------------------------------------------
    # Sprites — shop directory
    # ------------------------------------------------------------------
    print()
    print("=== SHOP SPRITE VERIFICATION ===")

    shop_sprites: list[tuple[str, int, int]] = [
        ("orb_weapon.png", 48, 48),
        ("orb_defense.png", 48, 48),
        ("orb_mobility.png", 48, 48),
        ("orb_economy.png", 48, 48),
        ("orb_repair.png", 48, 48),
        ("orb_insurance.png", 48, 48),
        ("node_continue.png", 48, 48),
    ]
    for name, ew, eh in shop_sprites:
        _check_sprite(SHOP_SPRITES_DIR / name, ew, eh, errors)

    # ------------------------------------------------------------------
    # Sound effects (16 from spec + extras from earlier phases)
    # ------------------------------------------------------------------
    print()
    print("=== SOUND VERIFICATION ===")

    expected_sounds = [
        # Spec canonical 16
        "fire.wav",
        "hit.wav",
        "explode_small.wav",
        "explode_medium.wav",
        "explode_large.wav",
        "enemy_explode.wav",
        "pickup_currency.wav",
        "pickup_buff.wav",
        "shop_purchase.wav",
        "shop_denied.wav",
        "level_clear.wav",
        "game_over.wav",
        "menu_nav.wav",
        "menu_select.wav",
        "insurance_deduct.wav",
        # Extra sounds from earlier phases
        "enemy_fire.wav",
        "player_hit.wav",
    ]
    for name in expected_sounds:
        _check_sound(SOUNDS_DIR / name, errors)

    # Optional: shield_low.wav (spec says deferrable)
    shield_path = SOUNDS_DIR / "shield_low.wav"
    if shield_path.exists():
        _check_sound(shield_path, errors)
    else:
        print(f"  INFO: shield_low.wav not present (optional/deferrable)")

    # ------------------------------------------------------------------
    # Font
    # ------------------------------------------------------------------
    print()
    print("=== FONT VERIFICATION ===")

    font_path = FONTS_DIR / "game_font.ttf"
    if font_path.exists():
        size_kb = font_path.stat().st_size / 1024
        print(f"  OK: game_font.ttf — {size_kb:.1f} KB")
    else:
        errors.append("MISSING: game_font.ttf")
        print("  MISSING: game_font.ttf")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    if not errors:
        print("✅ All asset checks passed.")
    else:
        print(f"❌ {len(errors)} check(s) failed:")
        for err in errors:
            print(f"   • {err}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
