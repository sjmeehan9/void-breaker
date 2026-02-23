"""Generate placeholder geometric sprites for gameplay.

Creates simple geometric shape sprites using Pillow:
- Ship: white triangle pointing upward (~32x32)
- Asteroids: irregular grey circles in 3 sizes (~64, ~40, ~20)
- Projectile (player): cyan dot (~8x8)
- Currency pickup: gold diamond (~16x16)
- Explosion particle: bright orange-white dot (~6x6)
- Enemy Basic: red diamond (64x64)
- Enemy Aggressive: orange chevron/arrow (64x64)
- Projectile (enemy): red-orange dot (8x8)
- Shop orbs: coloured circles in 6 category colours (64x64)
- Shop continue node: green right-pointing arrow (64x64)

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
SHOP_DIR = SPRITES_DIR / "shop"


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


def generate_enemy_basic(output_path: Path) -> None:
    """Generate a red diamond-shaped Basic Shooter enemy sprite (64x64).

    Visually distinct from the player ship (white triangle) — uses a red
    diamond shape to clearly signal an enemy entity.
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    # Diamond shape: top, right, bottom, left
    points = [
        (cx, 4),  # top
        (size - 4, cy),  # right
        (cx, size - 4),  # bottom
        (4, cy),  # left
    ]
    draw.polygon(points, fill=(200, 30, 30, 255), outline=(255, 80, 80, 255))

    # Small centre cockpit detail
    inner = [
        (cx, cy - 6),
        (cx + 6, cy),
        (cx, cy + 6),
        (cx - 6, cy),
    ]
    draw.polygon(inner, fill=(255, 100, 100, 255))

    img.save(output_path, "PNG")


def generate_enemy_aggressive(output_path: Path) -> None:
    """Generate an orange chevron/arrow Aggressive enemy sprite (64x64).

    Uses a chevron (V-arrow) shape with orange hues to differentiate from
    the red diamond of the Basic Shooter archetype.
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = size // 2
    # Chevron pointing downward (nose toward player)
    outer = [
        (cx, size - 6),  # nose (bottom-centre)
        (6, 6),  # top-left wing tip
        (cx, 20),  # inner notch
        (size - 6, 6),  # top-right wing tip
    ]
    draw.polygon(outer, fill=(230, 120, 20, 255), outline=(255, 180, 60, 255))

    # Inner accent stripe for visual interest
    accent = [
        (cx, size - 16),
        (16, 14),
        (cx, 24),
        (size - 16, 14),
    ]
    draw.polygon(accent, fill=(255, 160, 40, 255))

    img.save(output_path, "PNG")


def generate_enemy_projectile(output_path: Path) -> None:
    """Generate a small red-orange enemy projectile sprite (8x8).

    Clearly distinguishable from the cyan player projectile by colour.
    """
    size = 8
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Red-orange dot with bright core
    draw.ellipse([1, 1, size - 2, size - 2], fill=(255, 80, 30, 255))
    # Bright yellow-orange core
    draw.ellipse([2, 2, size - 3, size - 3], fill=(255, 200, 100, 255))

    img.save(output_path, "PNG")


def generate_shop_orb(output_path: Path, colour: tuple[int, int, int]) -> None:
    """Generate a coloured circle orb sprite for a shop category (64x64).

    A filled circle with a soft outer glow ring on a transparent background.

    Args:
        output_path: Where to save the PNG.
        colour: RGB tuple for the orb fill colour.
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    radius = 26

    # Outer glow ring (lighter, semi-transparent)
    glow_r, glow_g, glow_b = (
        min(colour[0] + 60, 255),
        min(colour[1] + 60, 255),
        min(colour[2] + 60, 255),
    )
    draw.ellipse(
        [cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3],
        fill=(glow_r, glow_g, glow_b, 80),
    )

    # Main orb circle
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*colour, 255),
        outline=(glow_r, glow_g, glow_b, 255),
    )

    # Inner highlight for depth
    highlight_r = radius // 2
    draw.ellipse(
        [cx - highlight_r + 4, cy - highlight_r - 4,
         cx + highlight_r - 2, cy + highlight_r - 10],
        fill=(
            min(colour[0] + 80, 255),
            min(colour[1] + 80, 255),
            min(colour[2] + 80, 255),
            120,
        ),
    )

    img.save(output_path, "PNG")


def generate_shop_continue(output_path: Path) -> None:
    """Generate a bright green right-pointing arrow for the continue node (64x64).

    Visually distinct from the coloured category orbs so the player
    immediately recognises it as the 'exit shop' action.
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # Right-pointing chevron/arrow
    arrow_points = [
        (14, 10),   # top-left
        (50, cy),   # right tip
        (14, 54),   # bottom-left
        (24, cy),   # inner notch
    ]
    draw.polygon(arrow_points, fill=(46, 204, 113, 255), outline=(100, 255, 160, 255))

    img.save(output_path, "PNG")


def main() -> None:
    """Generate all placeholder sprites."""
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

    generate_enemy_basic(SPRITES_DIR / "enemy_basic.png")
    print("  ✓ enemy_basic.png (64x64)")

    generate_enemy_aggressive(SPRITES_DIR / "enemy_aggressive.png")
    print("  ✓ enemy_aggressive.png (64x64)")

    generate_enemy_projectile(SPRITES_DIR / "projectile_enemy.png")
    print("  ✓ projectile_enemy.png (8x8)")

    # --- Shop sprites ---
    SHOP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating shop sprites in {SHOP_DIR}")

    orb_colours: dict[str, tuple[int, int, int]] = {
        "orb_weapon": (231, 76, 60),      # red   #E74C3C
        "orb_defense": (52, 152, 219),     # blue  #3498DB
        "orb_mobility": (46, 204, 113),    # green #2ECC71
        "orb_economy": (241, 196, 15),     # gold  #F1C40F
        "orb_repair": (236, 240, 241),     # white #ECF0F1
        "orb_insurance": (155, 89, 182),   # purple #9B59B6
    }
    for name, colour in orb_colours.items():
        generate_shop_orb(SHOP_DIR / f"{name}.png", colour)
        print(f"  ✓ {name}.png (64x64)")

    generate_shop_continue(SHOP_DIR / "node_continue.png")
    print("  ✓ node_continue.png (64x64)")

    print("\nAll placeholder sprites generated successfully.")


if __name__ == "__main__":
    main()
