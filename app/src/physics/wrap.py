"""Wrap-around helpers for entities leaving the screen bounds."""

from __future__ import annotations

import arcade


def wrap_entity(entity: arcade.Sprite, width: float, height: float) -> None:
    """Wrap an entity to the opposite edge when it exits bounds.

    Args:
        entity: Sprite-like object with left/right/top/bottom bounds.
        width: Screen width in pixels.
        height: Screen height in pixels.
    """
    if entity.right < 0:
        entity.left = width
    elif entity.left > width:
        entity.right = 0

    if entity.top < 0:
        entity.bottom = height
    elif entity.bottom > height:
        entity.top = 0
