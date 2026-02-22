"""HUD text rendering helpers with value caching."""

from __future__ import annotations

import arcade


class HUDRenderer:
    """Draw HUD text and cache changing value labels."""

    def __init__(self, window_width: int, window_height: int) -> None:
        """Store dimensions and initialise text cache."""
        self._window_width = window_width
        self._window_height = window_height
        self._value_cache: dict[
            tuple[str, float, float],
            tuple[int | float, arcade.Text],
        ] = {}

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        color: tuple[int, int, int] = arcade.color.WHITE,
        font_size: int = 14,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
    ) -> None:
        """Draw arbitrary HUD text at the specified location."""
        arcade.draw_text(
            text=text,
            start_x=x,
            start_y=y,
            color=color,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
        )

    def draw_value(self, label: str, value: int | float, x: float, y: float) -> None:
        """Draw a cached `Label: Value` text object, rebuilding only on changes."""
        key = (label, x, y)
        cached = self._value_cache.get(key)

        if cached is None or cached[0] != value:
            text = arcade.Text(
                text=f"{label}: {value}",
                x=x,
                y=y,
                color=arcade.color.WHITE,
                font_size=14,
                anchor_x="left",
                anchor_y="baseline",
            )
            self._value_cache[key] = (value, text)
        self._value_cache[key][1].draw()
