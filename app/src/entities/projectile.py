"""Projectile entity used by player and enemy weapons."""

from __future__ import annotations

import math
from enum import Enum
from pathlib import Path

import arcade

PROJECTILE_SPRITE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "sprites" / "projectile_player.png"
)


class ProjectileOwner(str, Enum):
    """Projectile ownership identifiers used for collision routing."""

    PLAYER = "player"
    ENEMY = "enemy"


class Projectile(arcade.Sprite):
    """A fast-moving projectile with finite travel range."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        angle: float,
        speed: float,
        max_range: float,
        damage: float,
        owner: ProjectileOwner = ProjectileOwner.PLAYER,
    ) -> None:
        """Initialize projectile movement state.

        Args:
            center_x: Initial horizontal position in pixels.
            center_y: Initial vertical position in pixels.
            angle: Facing direction in degrees.
            speed: Travel speed in pixels/second.
            max_range: Maximum travel distance before expiration.
            damage: Damage applied on collision.
            owner: Source entity type that fired this projectile.
        """
        super().__init__(
            str(PROJECTILE_SPRITE_PATH), center_x=center_x, center_y=center_y
        )
        angle_radians = math.radians(angle + 90.0)
        self.velocity_x = math.cos(angle_radians) * speed
        self.velocity_y = math.sin(angle_radians) * speed
        self.speed = speed
        self.max_range = max_range
        self.damage = damage
        self.owner = owner
        self.distance_traveled: float = 0.0

    def update(self, dt: float) -> None:
        """Advance projectile and expire when max range is reached.

        Args:
            dt: Simulation delta time in seconds.
        """
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt
        self.distance_traveled += self.speed * dt
        if self.distance_traveled >= self.max_range:
            self.kill()
