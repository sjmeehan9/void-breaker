"""Entity spawning utilities for combat phases."""

from __future__ import annotations

import math
import random

from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.game_config import AsteroidSize
from asterax.app.src.entities.asteroid import Asteroid


class SpawnManager:
    """Spawn gameplay entities for a given level configuration."""

    def __init__(self, rng: random.Random | None = None) -> None:
        """Initialize spawn manager with optional deterministic RNG."""
        self._rng = rng if rng is not None else random.Random()

    def spawn_level_asteroids(
        self,
        level: int,
        player_position: tuple[float, float],
        screen_width: float,
        screen_height: float,
    ) -> list[Asteroid]:
        """Spawn initial large asteroids for the start of a level."""
        params = get_difficulty_params(level)
        asteroids: list[Asteroid] = []

        for _ in range(params.asteroid_count):
            position = self._random_position_away_from_player(
                player_position=player_position,
                screen_width=screen_width,
                screen_height=screen_height,
                minimum_distance=150.0,
            )
            speed = self._rng.uniform(
                params.asteroid_speed_min, params.asteroid_speed_max
            )
            angle = self._rng.uniform(0.0, math.tau)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            rotation_speed = self._rng.uniform(30.0, 120.0)
            asteroids.append(
                Asteroid(
                    size=AsteroidSize.LARGE,
                    center_x=position[0],
                    center_y=position[1],
                    velocity=velocity,
                    rotation_speed=rotation_speed,
                    rng=self._rng,
                )
            )

        return asteroids

    def spawn_child_asteroids(self, parent: Asteroid) -> list[Asteroid]:
        """Create child asteroids from a destroyed parent asteroid."""
        return parent.split()

    def _random_position_away_from_player(
        self,
        player_position: tuple[float, float],
        screen_width: float,
        screen_height: float,
        minimum_distance: float,
    ) -> tuple[float, float]:
        """Generate random position far enough from player spawn.

        Raises:
            RuntimeError: If no valid spawn position is found.
        """
        for _ in range(100):
            x = self._rng.uniform(0.0, screen_width)
            y = self._rng.uniform(0.0, screen_height)
            if math.dist((x, y), player_position) >= minimum_distance:
                return (x, y)

        raise RuntimeError("Unable to find valid asteroid spawn position")
