"""Generate final retro-arcade sprite assets for VoidBreaker Phase 5.

Creates polished geometric sprites using Pillow with high-contrast
retro-arcade aesthetics: bright shapes on transparent backgrounds with
glow effects, gradients, and detail work.

Sprite inventory (25 files):
  Player:      ship.png, ship_thrust.png
  Asteroids:   asteroid_large.png, asteroid_medium.png, asteroid_small.png
  Enemies:     enemy_basic.png, enemy_aggressive.png
  Projectiles: projectile_player.png, projectile_enemy.png
  Pickups:     pickup_currency.png, pickup_buff_heal.png,
               pickup_buff_shield.png, pickup_buff_damage.png,
               pickup_buff_speed.png
  Particles:   particle_dot.png
  Shop:        orb_weapon.png, orb_defense.png, orb_mobility.png,
               orb_economy.png, orb_repair.png, orb_insurance.png,
               node_continue.png
  UI:          ui_panel.png, ui_button.png, ui_button_selected.png

Backward-compatibility aliases are generated for sprites whose
filenames changed between phases (currency_pickup.png,
explosion_particle.png).

Usage:
    python scripts/generate_final_sprites.py
"""

from __future__ import annotations

import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SPRITES_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites"
SHOP_DIR = SPRITES_DIR / "shop"

# ---------------------------------------------------------------------------
# Colour palette — high-contrast retro arcade
# ---------------------------------------------------------------------------
WHITE = (255, 255, 255, 255)
OFF_WHITE = (220, 230, 240, 255)
LIGHT_GREY = (180, 190, 200, 255)
MID_GREY = (140, 140, 150, 255)
DARK_GREY = (80, 80, 90, 255)
VERY_DARK = (30, 30, 40, 255)

CYAN_BRIGHT = (0, 255, 255, 255)
CYAN_PALE = (160, 255, 255, 255)
RED_BRIGHT = (255, 50, 50, 255)
RED_PALE = (255, 160, 120, 255)
ORANGE_BRIGHT = (255, 160, 40, 255)
ORANGE_PALE = (255, 210, 120, 255)
GREEN_BRIGHT = (50, 255, 120, 255)
GREEN_PALE = (160, 255, 200, 255)
BLUE_BRIGHT = (80, 160, 255, 255)
BLUE_PALE = (180, 220, 255, 255)
GOLD_BRIGHT = (255, 215, 0, 255)
GOLD_PALE = (255, 245, 140, 255)
PURPLE_BRIGHT = (180, 100, 255, 255)
PURPLE_PALE = (220, 180, 255, 255)

THRUST_ORANGE = (255, 140, 30, 255)
THRUST_YELLOW = (255, 240, 80, 255)
THRUST_RED = (255, 60, 20, 180)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _new_image(size: int | tuple[int, int]) -> tuple[Image.Image, ImageDraw.Draw]:
    """Create a transparent RGBA image and its Draw handle."""
    dims = (size, size) if isinstance(size, int) else size
    img = Image.new("RGBA", dims, (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _glow_layer(
    base: Image.Image,
    radius: int = 3,
    intensity: float = 0.5,
) -> Image.Image:
    """Return a copy of *base* blurred to create a glow, composited under it."""
    glow = base.filter(ImageFilter.GaussianBlur(radius))
    # Reduce glow alpha for soft halo effect
    glow_data = glow.load()
    if glow_data is not None:
        for y in range(glow.height):
            for x in range(glow.width):
                r, g, b, a = glow_data[x, y]
                glow_data[x, y] = (r, g, b, int(a * intensity))
    result = Image.new("RGBA", base.size, (0, 0, 0, 0))
    result = Image.alpha_composite(result, glow)
    result = Image.alpha_composite(result, base)
    return result


def _draw_polygon_aa(
    draw: ImageDraw.Draw,
    points: list[tuple[float, float]],
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
) -> None:
    """Draw a filled polygon (Pillow polygons are aliased; this is a clarity wrapper)."""
    draw.polygon(points, fill=fill, outline=outline)


# ---------------------------------------------------------------------------
# Player sprites
# ---------------------------------------------------------------------------


def generate_ship(output_path: Path) -> None:
    """Generate a detailed player ship sprite (64x64, facing up at angle 0).

    The ship uses a sleek triangular silhouette with engine nacelles,
    a bright hull highlight, and cockpit detail for retro-arcade appeal.
    """
    size = 64
    img, draw = _new_image(size)
    cx = size // 2

    # Main hull — tall triangle
    hull = [
        (cx, 4),  # nose
        (8, size - 8),  # bottom-left
        (cx, size - 14),  # tail notch
        (size - 8, size - 8),  # bottom-right
    ]
    draw.polygon(hull, fill=OFF_WHITE, outline=LIGHT_GREY)

    # Left engine nacelle
    nacelle_l = [
        (10, size - 12),
        (6, size - 4),
        (16, size - 4),
        (14, size - 12),
    ]
    draw.polygon(nacelle_l, fill=MID_GREY, outline=LIGHT_GREY)

    # Right engine nacelle
    nacelle_r = [
        (size - 14, size - 12),
        (size - 16, size - 4),
        (size - 6, size - 4),
        (size - 10, size - 12),
    ]
    draw.polygon(nacelle_r, fill=MID_GREY, outline=LIGHT_GREY)

    # Cockpit accent stripe
    stripe = [
        (cx, 10),
        (cx - 4, 26),
        (cx + 4, 26),
    ]
    draw.polygon(stripe, fill=CYAN_BRIGHT)

    # Central highlight line for depth
    draw.line([(cx, 6), (cx, size - 16)], fill=(*CYAN_BRIGHT[:3], 100), width=1)

    img = _glow_layer(img, radius=2, intensity=0.3)
    img.save(output_path, "PNG")


def generate_ship_thrust(output_path: Path) -> None:
    """Generate the player ship with visible thrust flame (64x64).

    Identical hull to ship.png but with orange-yellow exhaust plumes
    extending below the engine nacelles.
    """
    size = 64
    img, draw = _new_image(size)
    cx = size // 2

    # Thrust flames (drawn first, behind hull)
    # Left engine flame
    flame_l = [
        (9, size - 4),
        (11, size),
        (15, size - 4),
    ]
    draw.polygon(flame_l, fill=THRUST_ORANGE)
    flame_l_inner = [
        (10, size - 4),
        (12, size - 1),
        (14, size - 4),
    ]
    draw.polygon(flame_l_inner, fill=THRUST_YELLOW)

    # Right engine flame
    flame_r = [
        (size - 15, size - 4),
        (size - 11, size),
        (size - 9, size - 4),
    ]
    draw.polygon(flame_r, fill=THRUST_ORANGE)
    flame_r_inner = [
        (size - 14, size - 4),
        (size - 12, size - 1),
        (size - 10, size - 4),
    ]
    draw.polygon(flame_r_inner, fill=THRUST_YELLOW)

    # Central exhaust plume
    plume = [
        (cx - 4, size - 14),
        (cx, size - 2),
        (cx + 4, size - 14),
    ]
    draw.polygon(plume, fill=THRUST_RED)
    plume_inner = [
        (cx - 2, size - 14),
        (cx, size - 5),
        (cx + 2, size - 14),
    ]
    draw.polygon(plume_inner, fill=THRUST_ORANGE)

    # Hull (identical to ship.png)
    hull = [
        (cx, 4),
        (8, size - 8),
        (cx, size - 14),
        (size - 8, size - 8),
    ]
    draw.polygon(hull, fill=OFF_WHITE, outline=LIGHT_GREY)

    nacelle_l = [
        (10, size - 12),
        (6, size - 4),
        (16, size - 4),
        (14, size - 12),
    ]
    draw.polygon(nacelle_l, fill=MID_GREY, outline=LIGHT_GREY)

    nacelle_r = [
        (size - 14, size - 12),
        (size - 16, size - 4),
        (size - 6, size - 4),
        (size - 10, size - 12),
    ]
    draw.polygon(nacelle_r, fill=MID_GREY, outline=LIGHT_GREY)

    stripe = [
        (cx, 10),
        (cx - 4, 26),
        (cx + 4, 26),
    ]
    draw.polygon(stripe, fill=CYAN_BRIGHT)

    draw.line([(cx, 6), (cx, size - 16)], fill=(*CYAN_BRIGHT[:3], 100), width=1)

    img = _glow_layer(img, radius=3, intensity=0.4)
    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Asteroid sprites
# ---------------------------------------------------------------------------


def generate_asteroid(output_path: Path, diameter: int, seed: int) -> None:
    """Generate an irregular asteroid sprite with crater detail.

    Args:
        output_path: Destination PNG path.
        diameter: Approximate diameter in pixels.
        seed: Random seed for reproducible irregularity.
    """
    padding = 4
    size = diameter + padding * 2
    img, draw = _new_image(size)
    rng = random.Random(seed)

    cx, cy = size / 2.0, size / 2.0
    base_radius = diameter / 2.0

    # Irregular outline
    num_verts = 14
    points: list[tuple[float, float]] = []
    for i in range(num_verts):
        angle = (math.tau * i) / num_verts
        r = base_radius * (0.78 + rng.random() * 0.44)
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    body_fill = (145, 140, 135, 255)
    body_outline = (190, 185, 180, 255)
    draw.polygon(points, fill=body_fill, outline=body_outline)

    # Crater details (darker circles)
    num_craters = max(1, diameter // 20)
    for _ in range(num_craters):
        cr = rng.uniform(diameter * 0.06, diameter * 0.14)
        ca = rng.uniform(0, math.tau)
        cd = rng.uniform(0, base_radius * 0.5)
        ccx = cx + cd * math.cos(ca)
        ccy = cy + cd * math.sin(ca)
        crater_shade = rng.randint(100, 125)
        draw.ellipse(
            [ccx - cr, ccy - cr, ccx + cr, ccy + cr],
            fill=(crater_shade, crater_shade - 5, crater_shade - 10, 255),
        )

    # Highlight edge on upper-left for depth
    highlight_angle = math.pi * 0.75  # upper-left
    hx = cx + base_radius * 0.4 * math.cos(highlight_angle)
    hy = cy + base_radius * 0.4 * math.sin(highlight_angle)
    hr = diameter * 0.12
    draw.ellipse(
        [hx - hr, hy - hr, hx + hr, hy + hr],
        fill=(200, 200, 195, 80),
    )

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Enemy sprites
# ---------------------------------------------------------------------------


def generate_enemy_basic(output_path: Path) -> None:
    """Generate a red diamond Basic Shooter enemy (48x48).

    Features a menacing diamond hull with inner cockpit detail and
    wing accents for visual distinction from the player ship.
    """
    size = 48
    img, draw = _new_image(size)
    cx, cy = size // 2, size // 2

    # Main diamond hull
    hull = [
        (cx, 3),  # top
        (size - 3, cy),  # right
        (cx, size - 3),  # bottom
        (3, cy),  # left
    ]
    draw.polygon(hull, fill=(200, 30, 30, 255), outline=(255, 80, 80, 255))

    # Inner diamond cockpit
    inner = [
        (cx, cy - 8),
        (cx + 8, cy),
        (cx, cy + 8),
        (cx - 8, cy),
    ]
    draw.polygon(inner, fill=(255, 100, 100, 255))

    # Bright cockpit core
    core = [
        (cx, cy - 3),
        (cx + 3, cy),
        (cx, cy + 3),
        (cx - 3, cy),
    ]
    draw.polygon(core, fill=(255, 200, 200, 255))

    # Wing accent lines
    draw.line([(3, cy), (cx, 3)], fill=(255, 120, 120, 180), width=1)
    draw.line([(size - 3, cy), (cx, 3)], fill=(255, 120, 120, 180), width=1)

    img = _glow_layer(img, radius=2, intensity=0.25)
    img.save(output_path, "PNG")


def generate_enemy_aggressive(output_path: Path) -> None:
    """Generate an orange chevron Aggressive enemy (48x48).

    A forward-pointing chevron shape with orange hues, visually distinct
    from the red diamond Basic Shooter.
    """
    size = 48
    img, draw = _new_image(size)
    cx = size // 2

    # Chevron body (nose at bottom — descending toward player)
    outer = [
        (cx, size - 4),  # nose
        (4, 4),  # top-left wing
        (cx, 16),  # inner notch
        (size - 4, 4),  # top-right wing
    ]
    draw.polygon(outer, fill=(230, 120, 20, 255), outline=(255, 180, 60, 255))

    # Inner accent stripe
    accent = [
        (cx, size - 12),
        (12, 10),
        (cx, 20),
        (size - 12, 10),
    ]
    draw.polygon(accent, fill=(255, 160, 40, 255))

    # Cockpit dot
    draw.ellipse(
        [cx - 3, 18, cx + 3, 24],
        fill=(255, 220, 140, 255),
    )

    img = _glow_layer(img, radius=2, intensity=0.25)
    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Projectile sprites
# ---------------------------------------------------------------------------


def generate_projectile_player(output_path: Path) -> None:
    """Generate a bright cyan elongated player projectile bolt (8x16)."""
    w, h = 8, 16
    img, draw = _new_image((w, h))

    # Outer bolt glow
    draw.rounded_rectangle([0, 1, w - 1, h - 2], radius=3, fill=(0, 200, 255, 120))
    # Core bolt
    draw.rounded_rectangle([1, 2, w - 2, h - 3], radius=2, fill=CYAN_BRIGHT)
    # Bright centre line
    draw.line([(w // 2, 3), (w // 2, h - 4)], fill=CYAN_PALE, width=1)

    img.save(output_path, "PNG")


def generate_projectile_enemy(output_path: Path) -> None:
    """Generate a red-orange elongated enemy projectile bolt (8x16)."""
    w, h = 8, 16
    img, draw = _new_image((w, h))

    # Outer bolt glow
    draw.rounded_rectangle([0, 1, w - 1, h - 2], radius=3, fill=(255, 60, 20, 120))
    # Core bolt
    draw.rounded_rectangle([1, 2, w - 2, h - 3], radius=2, fill=RED_BRIGHT)
    # Bright centre line
    draw.line([(w // 2, 3), (w // 2, h - 4)], fill=RED_PALE, width=1)

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Pickup sprites
# ---------------------------------------------------------------------------


def generate_pickup_currency(output_path: Path) -> None:
    """Generate a gold crystal/gem currency pickup (24x24).

    A hexagonal gem shape with highlight for a polished collectible look.
    """
    size = 24
    img, draw = _new_image(size)
    cx, cy = size // 2, size // 2

    # Gem shape — hexagonal with slight vertical stretch
    gem = [
        (cx, 1),  # top
        (size - 2, cy - 3),  # upper-right
        (size - 2, cy + 3),  # lower-right
        (cx, size - 2),  # bottom
        (2, cy + 3),  # lower-left
        (2, cy - 3),  # upper-left
    ]
    draw.polygon(gem, fill=(255, 200, 0, 255), outline=(255, 245, 100, 255))

    # Inner facet highlight
    facet = [
        (cx, 4),
        (size - 5, cy - 1),
        (cx, cy + 2),
        (5, cy - 1),
    ]
    draw.polygon(facet, fill=(255, 235, 80, 200))

    # Bright sparkle centre
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=GOLD_PALE)

    img = _glow_layer(img, radius=2, intensity=0.35)
    img.save(output_path, "PNG")


def generate_pickup_buff_heal(output_path: Path) -> None:
    """Generate a green cross/plus heal buff pickup (24x24)."""
    size = 24
    img, draw = _new_image(size)
    cx, cy = size // 2, size // 2
    arm_w = 3  # half-width of each arm
    margin = 3

    # Cross shape
    # Vertical bar
    draw.rectangle(
        [cx - arm_w, margin, cx + arm_w, size - margin],
        fill=GREEN_BRIGHT,
        outline=(100, 255, 160, 255),
    )
    # Horizontal bar
    draw.rectangle(
        [margin, cy - arm_w, size - margin, cy + arm_w],
        fill=GREEN_BRIGHT,
        outline=(100, 255, 160, 255),
    )
    # Bright centre
    draw.rectangle(
        [cx - arm_w, cy - arm_w, cx + arm_w, cy + arm_w],
        fill=GREEN_PALE,
    )

    img = _glow_layer(img, radius=2, intensity=0.35)
    img.save(output_path, "PNG")


def generate_pickup_buff_shield(output_path: Path) -> None:
    """Generate a blue shield-shaped buff pickup (24x24)."""
    size = 24
    img, draw = _new_image(size)
    cx = size // 2

    # Shield shape — pointed bottom, curved top
    shield = [
        (cx, 2),  # top-centre
        (size - 2, 4),  # top-right
        (size - 3, size // 2 + 2),  # mid-right
        (cx, size - 2),  # bottom point
        (3, size // 2 + 2),  # mid-left
        (2, 4),  # top-left
    ]
    draw.polygon(shield, fill=BLUE_BRIGHT, outline=(140, 200, 255, 255))

    # Inner shield highlight
    inner = [
        (cx, 5),
        (size - 5, 6),
        (size - 6, size // 2),
        (cx, size - 6),
        (6, size // 2),
        (5, 6),
    ]
    draw.polygon(inner, fill=BLUE_PALE[:3] + (120,))

    img = _glow_layer(img, radius=2, intensity=0.35)
    img.save(output_path, "PNG")


def generate_pickup_buff_damage(output_path: Path) -> None:
    """Generate a red star/burst damage boost buff pickup (24x24)."""
    size = 24
    img, draw = _new_image(size)
    cx, cy = size / 2.0, size / 2.0

    # Six-pointed star
    points: list[tuple[float, float]] = []
    for i in range(12):
        angle = (math.tau * i) / 12 - math.pi / 2
        r = 10.0 if i % 2 == 0 else 5.0
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    draw.polygon(points, fill=RED_BRIGHT, outline=(255, 120, 120, 255))

    # Bright core
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED_PALE)

    img = _glow_layer(img, radius=2, intensity=0.35)
    img.save(output_path, "PNG")


def generate_pickup_buff_speed(output_path: Path) -> None:
    """Generate a cyan lightning bolt speed boost buff pickup (24x24)."""
    size = 24
    img, draw = _new_image(size)

    # Lightning bolt shape
    bolt = [
        (14, 1),  # top-right
        (6, 10),  # upper-left bend
        (12, 10),  # inner step right
        (8, 23),  # bottom-left tip
        (18, 13),  # lower-right bend
        (12, 13),  # inner step left
    ]
    draw.polygon(bolt, fill=CYAN_BRIGHT, outline=(100, 255, 255, 255))

    # Bright core stripe
    core = [
        (13, 3),
        (8, 10),
        (13, 10),
        (10, 21),
        (16, 13),
        (12, 13),
    ]
    draw.polygon(core, fill=CYAN_PALE[:3] + (180,))

    img = _glow_layer(img, radius=2, intensity=0.35)
    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Particle sprite
# ---------------------------------------------------------------------------


def generate_particle_dot(output_path: Path) -> None:
    """Generate a small white particle sprite (8x8) for code-time tinting.

    A soft radial dot — white base so the particle system can apply any
    colour tint via ``arcade.Sprite.color``.
    """
    size = 8
    img, draw = _new_image(size)

    # Outer soft glow
    draw.ellipse([0, 0, size - 1, size - 1], fill=(255, 255, 255, 120))
    # Inner bright core
    draw.ellipse([1, 1, size - 2, size - 2], fill=(255, 255, 255, 220))
    # Centre hot spot
    draw.ellipse([2, 2, size - 3, size - 3], fill=WHITE)

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Shop sprites
# ---------------------------------------------------------------------------


def generate_shop_orb(output_path: Path, colour: tuple[int, int, int]) -> None:
    """Generate a polished coloured orb for a shop category (48x48).

    Three-layer design: outer glow ring, main fill circle, and inner
    highlight for visual depth.

    Args:
        output_path: Destination PNG path.
        colour: RGB tuple for the orb's primary fill.
    """
    size = 48
    img, draw = _new_image(size)
    cx, cy = size // 2, size // 2
    radius = 20

    # Outer glow ring
    glow_rgb = tuple(min(c + 60, 255) for c in colour)
    draw.ellipse(
        [cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3],
        fill=(*glow_rgb, 80),
    )

    # Main orb
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*colour, 255),
        outline=(*glow_rgb, 255),
    )

    # Inner highlight (upper-left)
    hr = radius // 2
    draw.ellipse(
        [cx - hr + 2, cy - hr - 4, cx + hr - 4, cy + hr - 10],
        fill=(
            min(colour[0] + 90, 255),
            min(colour[1] + 90, 255),
            min(colour[2] + 90, 255),
            130,
        ),
    )

    img.save(output_path, "PNG")


def generate_shop_continue(output_path: Path) -> None:
    """Generate a bright green arrow continue node (48x48)."""
    size = 48
    img, draw = _new_image(size)
    cx, cy = size // 2, size // 2

    # Right-pointing arrow
    arrow = [
        (10, 8),  # top-left
        (38, cy),  # right tip
        (10, 40),  # bottom-left
        (18, cy),  # inner notch
    ]
    draw.polygon(arrow, fill=(46, 204, 113, 255), outline=(100, 255, 160, 255))

    # Highlight stripe
    stripe = [
        (14, 14),
        (32, cy),
        (14, 34),
        (20, cy),
    ]
    draw.polygon(stripe, fill=(100, 255, 170, 120))

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# UI sprites
# ---------------------------------------------------------------------------


def generate_ui_panel(output_path: Path) -> None:
    """Generate a dark UI panel background with glowing border (256x192).

    A rounded rectangle with a bright cyan border on a dark semi-transparent
    background, suitable as a menu/overlay backdrop.
    """
    w, h = 256, 192
    img, draw = _new_image((w, h))

    # Dark background fill
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=(15, 15, 25, 220))

    # Bright border
    draw.rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=8, outline=(0, 200, 255, 200), width=2
    )

    # Inner accent border
    draw.rounded_rectangle(
        [3, 3, w - 4, h - 4], radius=6, outline=(0, 160, 220, 100), width=1
    )

    img.save(output_path, "PNG")


def generate_ui_button(output_path: Path) -> None:
    """Generate a dark button background with subtle border (200x40)."""
    w, h = 200, 40
    img, draw = _new_image((w, h))

    # Button background
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(25, 25, 40, 220))

    # Border
    draw.rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=6, outline=(100, 110, 140, 200), width=1
    )

    img.save(output_path, "PNG")


def generate_ui_button_selected(output_path: Path) -> None:
    """Generate a highlighted/selected button background (200x40).

    Bright cyan border and lighter fill to indicate active selection.
    """
    w, h = 200, 40
    img, draw = _new_image((w, h))

    # Highlighted background
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(20, 40, 60, 240))

    # Bright cyan border
    draw.rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=6, outline=CYAN_BRIGHT[:3] + (240,), width=2
    )

    # Top highlight edge
    draw.line([(6, 1), (w - 7, 1)], fill=(0, 255, 255, 80), width=1)

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Backward-compatibility aliases
# ---------------------------------------------------------------------------


def _create_backcompat_aliases() -> None:
    """Copy spec-named sprites to legacy filenames for backward compat.

    Phase 1-4 code references ``currency_pickup.png`` and
    ``explosion_particle.png``.  Phase 5 spec renames them to
    ``pickup_currency.png`` and ``particle_dot.png``.  Both names
    are provided so that existing code continues to work while new
    code can adopt the canonical names.
    """
    aliases: list[tuple[str, str]] = [
        ("pickup_currency.png", "currency_pickup.png"),
        ("particle_dot.png", "explosion_particle.png"),
    ]
    for src_name, dst_name in aliases:
        src = SPRITES_DIR / src_name
        dst = SPRITES_DIR / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  → alias {dst_name} (copy of {src_name})")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate all final sprite assets for VoidBreaker."""
    SPRITES_DIR.mkdir(parents=True, exist_ok=True)
    SHOP_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating final sprites in {SPRITES_DIR}\n")

    # --- Player ---
    generate_ship(SPRITES_DIR / "ship.png")
    print("  ✓ ship.png (64×64)")

    generate_ship_thrust(SPRITES_DIR / "ship_thrust.png")
    print("  ✓ ship_thrust.png (64×64)")

    # --- Asteroids ---
    generate_asteroid(SPRITES_DIR / "asteroid_large.png", diameter=96, seed=501)
    print("  ✓ asteroid_large.png (96×96)")

    generate_asteroid(SPRITES_DIR / "asteroid_medium.png", diameter=48, seed=502)
    print("  ✓ asteroid_medium.png (48×48)")

    generate_asteroid(SPRITES_DIR / "asteroid_small.png", diameter=24, seed=503)
    print("  ✓ asteroid_small.png (24×24)")

    # --- Enemies ---
    generate_enemy_basic(SPRITES_DIR / "enemy_basic.png")
    print("  ✓ enemy_basic.png (48×48)")

    generate_enemy_aggressive(SPRITES_DIR / "enemy_aggressive.png")
    print("  ✓ enemy_aggressive.png (48×48)")

    # --- Projectiles ---
    generate_projectile_player(SPRITES_DIR / "projectile_player.png")
    print("  ✓ projectile_player.png (8×16)")

    generate_projectile_enemy(SPRITES_DIR / "projectile_enemy.png")
    print("  ✓ projectile_enemy.png (8×16)")

    # --- Pickups ---
    generate_pickup_currency(SPRITES_DIR / "pickup_currency.png")
    print("  ✓ pickup_currency.png (24×24)")

    generate_pickup_buff_heal(SPRITES_DIR / "pickup_buff_heal.png")
    print("  ✓ pickup_buff_heal.png (24×24)")

    generate_pickup_buff_shield(SPRITES_DIR / "pickup_buff_shield.png")
    print("  ✓ pickup_buff_shield.png (24×24)")

    generate_pickup_buff_damage(SPRITES_DIR / "pickup_buff_damage.png")
    print("  ✓ pickup_buff_damage.png (24×24)")

    generate_pickup_buff_speed(SPRITES_DIR / "pickup_buff_speed.png")
    print("  ✓ pickup_buff_speed.png (24×24)")

    # --- Particles ---
    generate_particle_dot(SPRITES_DIR / "particle_dot.png")
    print("  ✓ particle_dot.png (8×8)")

    # --- Shop ---
    print(f"\nGenerating shop sprites in {SHOP_DIR}")
    orb_colours: dict[str, tuple[int, int, int]] = {
        "orb_weapon": (231, 76, 60),
        "orb_defense": (52, 152, 219),
        "orb_mobility": (46, 204, 113),
        "orb_economy": (241, 196, 15),
        "orb_repair": (236, 240, 241),
        "orb_insurance": (155, 89, 182),
    }
    for name, colour in orb_colours.items():
        generate_shop_orb(SHOP_DIR / f"{name}.png", colour)
        print(f"  ✓ {name}.png (48×48)")

    generate_shop_continue(SHOP_DIR / "node_continue.png")
    print("  ✓ node_continue.png (48×48)")

    # --- UI ---
    print("\nGenerating UI sprites")
    generate_ui_panel(SPRITES_DIR / "ui_panel.png")
    print("  ✓ ui_panel.png (256×192)")

    generate_ui_button(SPRITES_DIR / "ui_button.png")
    print("  ✓ ui_button.png (200×40)")

    generate_ui_button_selected(SPRITES_DIR / "ui_button_selected.png")
    print("  ✓ ui_button_selected.png (200×40)")

    # --- Backward-compat aliases ---
    print("\nCreating backward-compatibility aliases")
    _create_backcompat_aliases()

    print("\n✅ All final sprites generated successfully (25 files + 2 aliases).")


if __name__ == "__main__":
    main()
