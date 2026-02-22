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
        self._combat_values = {
            "score": 0,
            "level": 1,
            "shields": 100,
            "max_shields": 100,
            "credits": 0,
        }
        self._combat_cache: dict[str, tuple[str, arcade.Text]] = {}

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

    def update_combat_values(
        self,
        score: int,
        level: int,
        shields: float,
        max_shields: float,
        credits: int,
    ) -> None:
        """Update cached combat values consumed by `draw`."""
        self._combat_values["score"] = int(score)
        self._combat_values["level"] = max(1, int(level))
        self._combat_values["shields"] = int(round(shields))
        self._combat_values["max_shields"] = int(round(max_shields))
        self._combat_values["credits"] = max(0, int(credits))

    def draw(self) -> None:
        """Draw the standard combat HUD overlay with lazily cached text."""
        self._draw_cached_combat_text(
            cache_key="score",
            text=f"Score: {self._combat_values['score']}",
            x=20.0,
            y=self._window_height - 20.0,
            anchor_x="left",
            anchor_y="top",
        )
        self._draw_cached_combat_text(
            cache_key="level",
            text=f"Level: {self._combat_values['level']}",
            x=self._window_width - 20.0,
            y=self._window_height - 20.0,
            anchor_x="right",
            anchor_y="top",
        )
        self._draw_cached_combat_text(
            cache_key="shields",
            text=(
                f"Shields: {self._combat_values['shields']}/"
                f"{self._combat_values['max_shields']}"
            ),
            x=20.0,
            y=20.0,
            anchor_x="left",
            anchor_y="bottom",
        )
        self._draw_cached_combat_text(
            cache_key="credits",
            text=f"Credits: {self._combat_values['credits']}",
            x=self._window_width - 20.0,
            y=20.0,
            anchor_x="right",
            anchor_y="bottom",
        )

    def _draw_cached_combat_text(
        self,
        cache_key: str,
        text: str,
        x: float,
        y: float,
        anchor_x: str,
        anchor_y: str,
    ) -> None:
        cached = self._combat_cache.get(cache_key)
        if cached is None or cached[0] != text:
            self._combat_cache[cache_key] = (
                text,
                arcade.Text(
                    text=text,
                    x=x,
                    y=y,
                    color=arcade.color.WHITE,
                    font_size=18,
                    anchor_x=anchor_x,
                    anchor_y=anchor_y,
                ),
            )
        self._combat_cache[cache_key][1].draw()
