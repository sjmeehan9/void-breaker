"""Reusable menu rendering utilities."""

from __future__ import annotations

import arcade


class MenuRenderer:
    """Render menu titles and option lists with consistent styling."""

    def __init__(self) -> None:
        """Initialize cached text objects for efficient redraws."""
        self._text_cache: dict[
            tuple[str, float, float, int, tuple[int, ...], str], arcade.Text
        ] = {}

    def draw_title(self, text: str, x: float, y: float) -> None:
        """Draw a centered menu title.

        Args:
            text: Title text to render.
            x: Horizontal center coordinate.
            y: Vertical center coordinate.
        """
        title = self._get_or_create_text(
            text=text,
            x=x,
            y=y,
            font_size=64,
            color=(230, 245, 255, 255),
            anchor_x="center",
        )
        glow = self._get_or_create_text(
            text=text,
            x=x,
            y=y,
            font_size=66,
            color=(90, 220, 255, 64),
            anchor_x="center",
        )
        glow.draw()
        title.draw()

    def draw_menu_options(
        self,
        options: list[str],
        selected: int,
        x: float,
        y: float,
        spacing: float,
    ) -> None:
        """Draw a vertical menu option list with selected-item highlight.

        Args:
            options: Ordered display labels for each option.
            selected: Index of the highlighted option.
            x: Horizontal center coordinate.
            y: Starting vertical coordinate for the first option.
            spacing: Vertical distance between option rows.
        """
        for index, option in enumerate(options):
            is_selected = index == selected
            text = f"> {option} <" if is_selected else option
            color = (255, 220, 80, 255) if is_selected else (205, 220, 235, 220)
            option_text = self._get_or_create_text(
                text=text,
                x=x,
                y=y - (index * spacing),
                font_size=34,
                color=color,
                anchor_x="center",
            )
            option_text.draw()

    def _get_or_create_text(
        self,
        text: str,
        x: float,
        y: float,
        font_size: int,
        color: tuple[int, ...],
        anchor_x: str,
    ) -> arcade.Text:
        """Get a cached `arcade.Text` object or create and cache a new one.

        Args:
            text: Text content to render.
            x: Text x-coordinate.
            y: Text y-coordinate.
            font_size: Text font size.
            color: RGBA color tuple.
            anchor_x: Horizontal anchor mode.

        Returns:
            Cached or newly created Arcade text object.
        """
        cache_key = (text, x, y, font_size, color, anchor_x)
        cached = self._text_cache.get(cache_key)
        if cached is not None:
            return cached

        created = arcade.Text(
            text=text,
            x=x,
            y=y,
            color=color,
            font_size=font_size,
            anchor_x=anchor_x,
        )
        self._text_cache[cache_key] = created
        return created
