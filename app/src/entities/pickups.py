"""Pickup entities used during combat."""

from __future__ import annotations

import math
import random
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import CURRENCY_CONFIG

PICKUP_SPRITE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "sprites" / "currency_pickup.png"
)


class CurrencyPickup(arcade.Sprite):
    """Currency pickup that drifts and expires after a timeout."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        value: int = CURRENCY_CONFIG.pickup_value,
        lifetime: float = CURRENCY_CONFIG.pickup_lifetime,
        drift_speed_range: tuple[
            float, float
        ] = CURRENCY_CONFIG.pickup_drift_speed_range,
        rng: random.Random | None = None,
    ) -> None:
        """Initialize pickup movement and value metadata."""
        super().__init__(
            str(PICKUP_SPRITE_PATH), scale=1.1, center_x=center_x, center_y=center_y
        )
        randomizer = rng if rng is not None else random
        angle = randomizer.uniform(0.0, 2.0 * math.pi)
        speed = randomizer.uniform(*drift_speed_range)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.value = value
        self.lifetime_remaining = lifetime

    def update(self, dt: float) -> None:
        """Advance position and remove pickup when its lifetime expires."""
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt
        self.lifetime_remaining -= dt
        if self.lifetime_remaining <= 0.0:
            self.kill()
