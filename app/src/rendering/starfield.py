"""Static starfield background renderer."""

from __future__ import annotations

import random

import arcade

_BRIGHTNESS_LEVELS: tuple[int, int, int] = (96, 168, 255)


class StarfieldRenderer:
    """Render a deterministic static starfield background."""

    def __init__(self, width: int, height: int, star_count: int = 200) -> None:
        """Build a precomputed shape list for all stars."""
        self._width = width
        self._height = height
        self._star_count = max(0, star_count)
        self._stars: list[tuple[float, float, int]] = []
        self._stars_by_brightness: dict[int, list[tuple[float, float]]] = {
            brightness: [] for brightness in _BRIGHTNESS_LEVELS
        }

        rng = random.Random(42)
        for _ in range(self._star_count):
            x = rng.uniform(0.0, float(width))
            y = rng.uniform(0.0, float(height))
            brightness = _BRIGHTNESS_LEVELS[rng.randrange(len(_BRIGHTNESS_LEVELS))]
            self._stars.append((x, y, brightness))
            self._stars_by_brightness[brightness].append((x, y))

    def draw(self) -> None:
        """Draw the precomputed starfield."""
        for brightness, stars in self._stars_by_brightness.items():
            if not stars:
                continue
            arcade.draw_points(
                stars,
                (brightness, brightness, brightness),
                size=1,
            )
