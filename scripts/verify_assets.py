"""Verify all placeholder assets exist and are valid."""

from __future__ import annotations

import wave
from pathlib import Path

from PIL import Image

SPRITES_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites"
SOUNDS_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"


def main() -> None:
    """Run asset verification checks."""
    print("=== SPRITE VERIFICATION ===")
    expected_sprites = {
        "ship.png": 32,
        "asteroid_large.png": 68,
        "asteroid_medium.png": 44,
        "asteroid_small.png": 24,
        "projectile_player.png": 8,
        "currency_pickup.png": 16,
        "explosion_particle.png": 6,
        "enemy_basic.png": 64,
        "enemy_aggressive.png": 64,
        "projectile_enemy.png": 8,
    }
    all_ok = True
    for name, expected_dim in expected_sprites.items():
        path = SPRITES_DIR / name
        if path.exists():
            img = Image.open(path)
            mode = img.mode
            w, h = img.size
            ok = mode == "RGBA" and w == expected_dim and h == expected_dim
            status = "OK" if ok else "MISMATCH"
            if not ok:
                all_ok = False
            print(f"  {status}: {name} - {w}x{h} {mode}")
        else:
            all_ok = False
            print(f"  MISSING: {name}")

    print()
    print("=== SOUND VERIFICATION ===")
    expected_sounds = [
        "fire.wav",
        "explode_small.wav",
        "explode_medium.wav",
        "explode_large.wav",
        "hit.wav",
        "pickup_currency.wav",
        "level_clear.wav",
        "game_over.wav",
        "enemy_fire.wav",
        "enemy_explode.wav",
        "player_hit.wav",
    ]
    for name in expected_sounds:
        path = SOUNDS_DIR / name
        if path.exists():
            try:
                with wave.open(str(path), "rb") as wf:
                    ch = wf.getnchannels()
                    sw = wf.getsampwidth()
                    fr = wf.getframerate()
                    nf = wf.getnframes()
                    dur = nf / fr
                    print(f"  OK: {name} - {ch}ch, {sw*8}-bit, {fr}Hz, {dur:.2f}s")
            except Exception as e:
                all_ok = False
                print(f"  ERROR: {name} - {e}")
        else:
            all_ok = False
            print(f"  MISSING: {name}")

    print()
    if all_ok:
        print("All asset checks passed.")
    else:
        print("Some checks failed!")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
