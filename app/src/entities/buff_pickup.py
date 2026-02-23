"""Buff pickup entities for optional temporary combat effects."""

from __future__ import annotations

import math
from enum import Enum

import arcade


class BuffType(str, Enum):
    """Supported buff pickup types."""

    HEAL = "heal"
    DAMAGE_BOOST = "damage_boost"
    SPEED_BOOST = "speed_boost"


class BuffPickup(arcade.Sprite):
    """Collectible pickup that grants an instant or temporary combat buff."""

    _TEXTURE_SCALE = 0.7
    _TEXTURE_DIAMETER = 28
    _LIFETIME_SECONDS = 10.0
    _BOB_AMPLITUDE = 3.0
    _BOB_FREQUENCY_HZ = 2.0
    _COLOR_BY_TYPE: dict[BuffType, arcade.Color] = {
        BuffType.HEAL: arcade.color.SPRING_GREEN,
        BuffType.DAMAGE_BOOST: arcade.color.ORANGE_RED,
        BuffType.SPEED_BOOST: arcade.color.DODGER_BLUE,
    }
    _TEXTURES: dict[BuffType, arcade.Texture] = {}

    def __init__(
        self,
        buff_type: BuffType,
        magnitude: float,
        duration: float,
        center_x: float,
        center_y: float,
        lifetime: float = _LIFETIME_SECONDS,
    ) -> None:
        """Initialise buff metadata, texture, and animation state."""
        texture = self._TEXTURES.get(buff_type)
        if texture is None:
            texture = arcade.make_circle_texture(
                self._TEXTURE_DIAMETER,
                self._COLOR_BY_TYPE[buff_type],
            )
            self._TEXTURES[buff_type] = texture

        super().__init__(
            texture, scale=self._TEXTURE_SCALE, center_x=center_x, center_y=center_y
        )
        self.buff_type = buff_type
        self.magnitude = magnitude
        self.duration = duration
        self.lifetime_remaining = lifetime
        self._bob_elapsed = 0.0
        self._base_center_y = center_y

    def update(self, dt: float) -> None:
        """Advance lifetime and bob animation, removing when lifetime expires."""
        self.lifetime_remaining -= dt
        if self.lifetime_remaining <= 0.0:
            self.kill()
            return

        self._bob_elapsed += dt
        bob_offset = self._BOB_AMPLITUDE * math.sin(
            math.tau * self._BOB_FREQUENCY_HZ * self._bob_elapsed
        )
        self.center_y = self._base_center_y + bob_offset
