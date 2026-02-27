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
        self._currency_flash_frames = 0
        self._last_credits_value = 0
        self._is_practice = False

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
        is_practice: bool = False,
    ) -> None:
        """Update cached combat values consumed by `draw`."""
        previous_credits = self._combat_values["credits"]
        self._combat_values["score"] = int(score)
        self._combat_values["level"] = max(1, int(level))
        self._combat_values["shields"] = int(round(shields))
        self._combat_values["max_shields"] = int(round(max_shields))
        self._combat_values["credits"] = max(0, int(credits))
        self._is_practice = bool(is_practice)
        if self._combat_values["credits"] != previous_credits:
            self._currency_flash_frames = 10
        self._last_credits_value = self._combat_values["credits"]

    def draw(self) -> None:
        """Draw the standard combat HUD overlay with lazily cached text."""
        self._draw_shields_bar()

        score_text = f"Score: {self._combat_values['score']}"
        arcade.draw_text(
            score_text,
            self._window_width / 2 + 2,
            self._window_height - 26,
            (0, 0, 0, 200),
            24,
            anchor_x="center",
            anchor_y="top",
            bold=True,
        )
        self._draw_cached_combat_text(
            cache_key="score",
            text=score_text,
            x=self._window_width / 2,
            y=self._window_height - 24.0,
            anchor_x="center",
            anchor_y="top",
            font_size=24,
            color=(255, 245, 160),
        )
        self._draw_cached_combat_text(
            cache_key="level",
            text=f"Level: {self._combat_values['level']}",
            x=self._window_width - 20.0,
            y=self._window_height - 20.0,
            anchor_x="right",
            anchor_y="top",
            font_size=20,
            color=arcade.color.WHITE,
        )
        if self._is_practice:
            self._draw_cached_combat_text(
                cache_key="practice",
                text="PRACTICE",
                x=self._window_width / 2,
                y=self._window_height - 60.0,
                anchor_x="center",
                anchor_y="top",
                font_size=18,
                color=(255, 220, 90),
            )
        else:
            self._combat_cache.pop("practice", None)
        self._draw_cached_combat_text(
            cache_key="shields",
            text=(
                f"Shields: {self._combat_values['shields']}/"
                f"{self._combat_values['max_shields']}"
            ),
            x=26.0,
            y=self._window_height - 72.0,
            anchor_x="left",
            anchor_y="top",
            font_size=18,
            color=arcade.color.WHITE,
        )
        credits_color = (
            (255, 220, 120) if self._currency_flash_frames > 0 else (255, 255, 255)
        )
        self._draw_cached_combat_text(
            cache_key="credits",
            text=f"◇ Credits: {self._combat_values['credits']}",
            x=26.0,
            y=self._window_height - 102.0,
            anchor_x="left",
            anchor_y="top",
            font_size=18,
            color=credits_color,
        )
        if self._currency_flash_frames > 0:
            self._currency_flash_frames -= 1

    def _draw_cached_combat_text(
        self,
        cache_key: str,
        text: str,
        x: float,
        y: float,
        anchor_x: str,
        anchor_y: str,
        font_size: int,
        color: tuple[int, int, int],
    ) -> None:
        cache_text = f"{text}|{font_size}|{color}"
        cached = self._combat_cache.get(cache_key)
        if cached is None or cached[0] != cache_text:
            self._combat_cache[cache_key] = (
                cache_text,
                arcade.Text(
                    text=text,
                    x=x,
                    y=y,
                    color=color,
                    font_size=font_size,
                    anchor_x=anchor_x,
                    anchor_y=anchor_y,
                ),
            )
        self._combat_cache[cache_key][1].draw()

    def _draw_shields_bar(self) -> None:
        max_shields = max(1, self._combat_values["max_shields"])
        shields_ratio = max(0.0, min(1.0, self._combat_values["shields"] / max_shields))
        if shields_ratio > 0.6:
            fill_color = (100, 220, 120)
        elif shields_ratio > 0.3:
            fill_color = (245, 210, 80)
        else:
            fill_color = (235, 90, 90)

        bar_x = 20
        bar_y = self._window_height - 58
        bar_width = 250
        bar_height = 18
        arcade.draw_lbwh_rectangle_filled(
            bar_x, bar_y, bar_width, bar_height, (25, 25, 35)
        )
        arcade.draw_lbwh_rectangle_outline(
            bar_x, bar_y, bar_width, bar_height, arcade.color.WHITE, 2
        )
        arcade.draw_lbwh_rectangle_filled(
            bar_x + 2,
            bar_y + 2,
            (bar_width - 4) * shields_ratio,
            bar_height - 4,
            fill_color,
        )
