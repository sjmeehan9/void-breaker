"""Generate placeholder geometric sprites for Phase 2 gameplay.

Creates simple geometric shape sprites using Pillow:
- Ship: white triangle pointing upward (~32x32)
- Asteroids: irregular grey circles in 3 sizes (~64, ~40, ~20)
- Projectile: cyan dot (~8x8)
- Currency pickup: gold diamond (~16x16)
- Explosion particle: bright orange-white dot (~6x6)

All sprites are RGBA PNGs with transparent backgrounds.

Usage:
    python scripts/generate_placeholder_sprites.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

SPRITES_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites"


def generate_ship(output_path: Path) -> None:
    """Generate a white triangle ship sprite pointing upward (32x32).

    The sprite's default forward direction points upward (90 degrees in
    Arcade's coordinate system). The solution design uses
    ``ship.angle + 90`` in the thrust calculation, which expects the
    sprite nose to point up.
    """
    size = 32
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Triangle pointing upward: top-centre, bottom-left, bottom-right
    cx, cy = size // 2, size // 2
    points = [
        (cx, 2),  # nose (top)
        (4, size - 4),  # bottom-left
        (size - 4, size - 4),  # bottom-right
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))

    # Small engine notch at the bottom centre for visual interest
    notch = [
        (cx - 3, size - 4),
        (cx, size - 8),
        (cx + 3, size - 4),
    ]
    draw.polygon(notch, fill=(0, 0, 0, 0))

    img.save(output_path, "PNG")


def generate_asteroid(output_path: Path, diameter: int, seed: int) -> None:
    """Generate an irregular grey circle asteroid sprite.

    Args:
        output_path: Where to save the PNG.
        diameter: Approximate diameter in pixels.
        seed: Random seed for reproducible irregularity.
    """
    padding = 2
    size = diameter + padding * 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rng = random.Random(seed)
    cx, cy = size / 2.0, size / 2.0
    base_radius = diameter / 2.0

    # Generate irregular polygon vertices around a circle
    num_vertices = 12
    points: list[tuple[float, float]] = []
    for i in range(num_vertices):
        angle = (2 * math.pi * i) / num_vertices
        # Vary radius by ±20%
        r = base_radius * (0.80 + rng.random() * 0.40)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))

    # Grey fill with slightly lighter outline
    draw.polygon(points, fill=(160, 160, 160, 255), outline=(200, 200, 200, 255))

    img.save(output_path, "PNG")


def generate_projectile(output_path: Path) -> None:
    """Generate a small cyan dot projectile sprite (8x8)."""
    size = 8
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Bright cyan dot with soft edge
    draw.ellipse([1, 1, size - 2, size - 2], fill=(0, 255, 255, 255))
    # Bright core
    draw.ellipse([2, 2, size - 3, size - 3], fill=(200, 255, 255, 255))

    img.save(output_path, "PNG")


def generate_currency_pickup(output_path: Path) -> None:
    """Generate a gold/yellow diamond-shaped currency pickup sprite (16x16)."""
    size = 16
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    # Diamond shape: top, right, bottom, left
    points = [
        (cx, 1),  # top
        (size - 2, cy),  # right
        (cx, size - 2),  # bottom
        (1, cy),  # left
    ]
    draw.polygon(points, fill=(255, 215, 0, 255), outline=(255, 255, 100, 255))

    img.save(output_path, "PNG")


def generate_explosion_particle(output_path: Path) -> None:
    """Generate a small orange-white explosion particle sprite (6x6)."""
    size = 6
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer orange glow
    draw.ellipse([0, 0, size - 1, size - 1], fill=(255, 160, 50, 255))
    # Inner bright white-yellow core
    draw.ellipse([1, 1, size - 2, size - 2], fill=(255, 255, 200, 255))

    img.save(output_path, "PNG")


def main() -> None:
    """Generate all placeholder sprites for Phase 2."""
    SPRITES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating sprites in {SPRITES_DIR}")

    generate_ship(SPRITES_DIR / "ship.png")
    print("  ✓ ship.png (32x32)")

    generate_asteroid(SPRITES_DIR / "asteroid_large.png", diameter=64, seed=101)
    print("  ✓ asteroid_large.png (~64px)")

    generate_asteroid(SPRITES_DIR / "asteroid_medium.png", diameter=40, seed=202)
    print("  ✓ asteroid_medium.png (~40px)")

    generate_asteroid(SPRITES_DIR / "asteroid_small.png", diameter=20, seed=303)
    print("  ✓ asteroid_small.png (~20px)")

    generate_projectile(SPRITES_DIR / "projectile_player.png")
    print("  ✓ projectile_player.png (8x8)")

    generate_currency_pickup(SPRITES_DIR / "currency_pickup.png")
    print("  ✓ currency_pickup.png (16x16)")

    generate_explosion_particle(SPRITES_DIR / "explosion_particle.png")
    print("  ✓ explosion_particle.png (6x6)")

    print("\nAll placeholder sprites generated successfully.")


if __name__ == "__main__":
    main()
