"""Asteroid entity definitions with splitting behavior."""

from __future__ import annotations

import math
import random
from typing import Any

import arcade
from asterax.app.src.config.game_config import ASTEROID_CONFIG, AsteroidSize


class Asteroid(arcade.Sprite):
    """Drifting asteroid that can split into smaller child asteroids."""

    def __init__(
        self,
        size: AsteroidSize,
        center_x: float,
        center_y: float,
        velocity: tuple[float, float],
        rotation_speed: float,
        rng: random.Random | None = None,
    ) -> None:
        """Initialize an asteroid with movement and size metadata.

        Args:
            size: Asteroid size tier.
            center_x: Initial horizontal position in pixels.
            center_y: Initial vertical position in pixels.
            velocity: Initial velocity vector in pixels/second.
            rotation_speed: Rotation speed in degrees/second.
            rng: Optional random generator for deterministic tests.
        """
        sprite_path, sprite_scale = _sprite_for_size(size)
        super().__init__(
            str(sprite_path),
            scale=sprite_scale,
            center_x=center_x,
            center_y=center_y,
        )
        self.asteroid_size = size
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]
        self.rotation_speed = rotation_speed
        self._rng = rng if rng is not None else random.Random()

    @property
    def point_value(self) -> int:
        """Return score points awarded when this asteroid is destroyed."""
        return ASTEROID_CONFIG.point_values[self.asteroid_size]

    @property
    def currency_drop_chance(self) -> float:
        """Return chance of spawning currency when destroyed."""
        return ASTEROID_CONFIG.currency_drop_chances[self.asteroid_size]

    def update(self, dt: float) -> None:
        """Advance asteroid position and rotation.

        Args:
            dt: Fixed simulation step in seconds.
        """
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt
        self.angle += self.rotation_speed * dt

    def split(self) -> list[Asteroid]:
        """Create child asteroids when this asteroid is destroyed."""
        next_size = _next_size(self.asteroid_size)
        if next_size is None:
            return []

        child_count = self._rng.randint(*ASTEROID_CONFIG.child_count_range)
        parent_speed = math.hypot(self.velocity_x, self.velocity_y)
        parent_angle = math.atan2(self.velocity_y, self.velocity_x)
        children: list[Asteroid] = []

        for _ in range(child_count):
            spread_degrees = self._rng.uniform(-60.0, 60.0)
            child_speed_multiplier = self._rng.uniform(
                *ASTEROID_CONFIG.child_speed_multiplier_range
            )
            child_angle = parent_angle + math.radians(spread_degrees)
            child_speed = max(1.0, parent_speed * child_speed_multiplier)
            child_velocity = (
                math.cos(child_angle) * child_speed,
                math.sin(child_angle) * child_speed,
            )
            child_rotation_speed = self._rng.uniform(30.0, 120.0)
            children.append(
                Asteroid(
                    size=next_size,
                    center_x=self.center_x,
                    center_y=self.center_y,
                    velocity=child_velocity,
                    rotation_speed=child_rotation_speed,
                    rng=self._rng,
                )
            )

        return children

    def on_destroyed(self) -> dict[str, Any]:
        """Return split and scoring data used by collision handling."""
        return {
            "point_value": self.point_value,
            "currency_drop_chance": self.currency_drop_chance,
            "children": self.split(),
        }


def _next_size(size: AsteroidSize) -> AsteroidSize | None:
    """Resolve the next smaller asteroid size.

    Args:
        size: Current asteroid size.

    Returns:
        Next size tier, or None for smallest asteroids.
    """
    if size is AsteroidSize.LARGE:
        return AsteroidSize.MEDIUM
    if size is AsteroidSize.MEDIUM:
        return AsteroidSize.SMALL
    return None


def _sprite_for_size(size: AsteroidSize) -> tuple[str, float]:
    """Resolve sprite path and scale for an asteroid size tier."""
    if size is AsteroidSize.LARGE:
        return str(ASTEROID_CONFIG.large_sprite), ASTEROID_CONFIG.large_scale
    if size is AsteroidSize.MEDIUM:
        return str(ASTEROID_CONFIG.medium_sprite), ASTEROID_CONFIG.medium_scale
    return str(ASTEROID_CONFIG.small_sprite), ASTEROID_CONFIG.small_scale
