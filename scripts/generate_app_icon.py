"""Generate the macOS app iconset and .icns file for VoidBreaker.

This script creates all required PNG sizes in a macOS .iconset folder using
Pillow, then invokes `iconutil` to produce `assets/icon.icns`.

Usage:
    source .venv/bin/activate
    python scripts/generate_app_icon.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICONSET_DIR = ASSETS_DIR / "VoidBreaker.iconset"
ICNS_PATH = ASSETS_DIR / "icon.icns"

# Required iconset entries and corresponding pixel dimensions.
ICONSET_SPECS: tuple[tuple[str, int], ...] = (
    ("icon_16x16.png", 16),
    ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32),
    ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128),
    ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256),
    ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512),
    ("icon_512x512@2x.png", 1024),
)


def _render_master_icon(size: int = 1024) -> Image.Image:
    """Render the master app icon image.

    The icon theme is a retro neon shard/ship motif over a dark radial-space
    backdrop to match VoidBreaker's visual style.

    Args:
        size: Output size in pixels.

    Returns:
        A square RGBA Pillow image.
    """
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    center = size // 2
    radius = int(size * 0.47)

    # Radial dark-space background approximation via concentric circles.
    for step in range(18, 0, -1):
        ratio = step / 18
        r = int(8 + 18 * ratio)
        g = int(12 + 28 * ratio)
        b = int(22 + 46 * ratio)
        alpha = int(235)
        current_radius = int(radius * ratio)
        draw.ellipse(
            (
                center - current_radius,
                center - current_radius,
                center + current_radius,
                center + current_radius,
            ),
            fill=(r, g, b, alpha),
        )

    # Subtle glow ring.
    ring_outer = int(size * 0.44)
    ring_inner = int(size * 0.38)
    draw.ellipse(
        (center - ring_outer, center - ring_outer, center + ring_outer, center + ring_outer),
        outline=(90, 185, 255, 155),
        width=max(4, size // 128),
    )
    draw.ellipse(
        (center - ring_inner, center - ring_inner, center + ring_inner, center + ring_inner),
        outline=(40, 120, 215, 120),
        width=max(3, size // 170),
    )

    # Stylized player-ship shard.
    ship = [
        (center, int(size * 0.16)),
        (int(size * 0.27), int(size * 0.79)),
        (center, int(size * 0.67)),
        (int(size * 0.73), int(size * 0.79)),
    ]
    draw.polygon(ship, fill=(220, 235, 255, 255), outline=(120, 190, 255, 255))

    # Cockpit stripe.
    cockpit = [
        (center, int(size * 0.24)),
        (int(size * 0.45), int(size * 0.47)),
        (int(size * 0.55), int(size * 0.47)),
    ]
    draw.polygon(cockpit, fill=(0, 255, 255, 245))

    # Inner accent line.
    draw.line(
        [(center, int(size * 0.20)), (center, int(size * 0.63))],
        fill=(140, 245, 255, 170),
        width=max(3, size // 220),
    )

    # Engine flame.
    flame_outer = [
        (int(size * 0.465), int(size * 0.70)),
        (center, int(size * 0.90)),
        (int(size * 0.535), int(size * 0.70)),
    ]
    flame_inner = [
        (int(size * 0.48), int(size * 0.71)),
        (center, int(size * 0.84)),
        (int(size * 0.52), int(size * 0.71)),
    ]
    draw.polygon(flame_outer, fill=(255, 120, 40, 230))
    draw.polygon(flame_inner, fill=(255, 230, 100, 240))

    # Apply slight glow pass for small-size readability.
    glow = image.filter(ImageFilter.GaussianBlur(radius=max(1, size // 180)))
    composite = Image.alpha_composite(glow, image)

    return composite


def _write_iconset(master: Image.Image) -> None:
    """Write all required iconset PNG files from a master icon.

    Args:
        master: High-resolution source icon image.
    """
    ICONSET_DIR.mkdir(parents=True, exist_ok=True)
    for filename, size in ICONSET_SPECS:
        resized = master.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(ICONSET_DIR / filename, format="PNG")


def _build_icns() -> None:
    """Create .icns from the generated iconset using iconutil."""
    cmd = [
        "iconutil",
        "-c",
        "icns",
        str(ICONSET_DIR),
        "-o",
        str(ICNS_PATH),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        details = stderr or stdout or "iconutil failed without output"
        raise RuntimeError(f"Failed to build .icns: {details}")


def main() -> None:
    """Generate iconset PNGs and build assets/icon.icns."""
    master = _render_master_icon()
    _write_iconset(master)
    _build_icns()
    print(f"Generated iconset at: {ICONSET_DIR}")
    print(f"Generated icon file at: {ICNS_PATH}")


if __name__ == "__main__":
    main()
