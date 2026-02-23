"""Entity spawning utilities for combat phases."""

from __future__ import annotations

import math
import random

from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.enemy_config import (
    EnemyArchetype,
    get_aggressive_config,
    get_basic_config,
)
from asterax.app.src.config.game_config import AsteroidSize, DifficultyParams
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.enemy_ship import EnemyShip


class SpawnManager:
    """Spawn gameplay entities for a given level configuration."""

    def __init__(self, rng: random.Random | None = None) -> None:
        """Initialize spawn manager with optional deterministic RNG."""
        self._rng = rng if rng is not None else random.Random()
        self._enemy_spawn_timer = 0.0
        self._enemy_spawn_active = False

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

    def update_enemy_spawning(
        self,
        dt: float,
        current_enemy_count: int,
        difficulty_params: DifficultyParams,
        screen_width: float,
        screen_height: float,
    ) -> list[EnemyShip]:
        """Spawn enemies at interval if enabled and under count cap.

        Args:
            dt: Physics delta time in seconds.
            current_enemy_count: Number of enemies currently alive.
            difficulty_params: Level difficulty configuration.
            screen_width: Viewport width for edge positioning.
            screen_height: Viewport height for edge positioning.

        Returns:
            List containing a single newly spawned enemy, or empty list if no spawn.
        """
        if not difficulty_params.enemy_spawn_enabled:
            return []

        self._enemy_spawn_timer += dt
        if self._enemy_spawn_timer < difficulty_params.enemy_spawn_interval:
            return []

        self._enemy_spawn_timer = 0.0
        if current_enemy_count >= difficulty_params.enemy_count_max:
            return []

        archetype = self._select_archetype(difficulty_params)
        if archetype == EnemyArchetype.BASIC:
            config = get_basic_config()
        else:
            config = get_aggressive_config()

        x, y, vx, vy = self._get_spawn_edge_position(
            speed=config.speed,
            screen_width=screen_width,
            screen_height=screen_height,
        )

        enemy = EnemyShip(
            archetype=archetype,
            config=config,
            center_x=x,
            center_y=y,
            rng=self._rng,
        )
        enemy.velocity_x = vx
        enemy.velocity_y = vy
        return [enemy]

    def _get_spawn_edge_position(
        self,
        speed: float,
        screen_width: float,
        screen_height: float,
    ) -> tuple[float, float, float, float]:
        """Generate random edge spawn position with inward velocity.

        Args:
            speed: Enemy movement speed magnitude.
            screen_width: Viewport width.
            screen_height: Viewport height.

        Returns:
            Tuple of (x, y, vx, vy) where position is just off-screen
            and velocity is directed inward toward screen center with randomness.
        """
        edge = self._rng.choice(["top", "bottom", "left", "right"])
        center_x = screen_width / 2.0
        center_y = screen_height / 2.0

        if edge == "top":
            x = self._rng.uniform(0.0, screen_width)
            y = screen_height + 50.0
            target_x = center_x + self._rng.uniform(-200.0, 200.0)
            target_y = center_y + self._rng.uniform(-100.0, 100.0)
        elif edge == "bottom":
            x = self._rng.uniform(0.0, screen_width)
            y = -50.0
            target_x = center_x + self._rng.uniform(-200.0, 200.0)
            target_y = center_y + self._rng.uniform(-100.0, 100.0)
        elif edge == "left":
            x = -50.0
            y = self._rng.uniform(0.0, screen_height)
            target_x = center_x + self._rng.uniform(-100.0, 100.0)
            target_y = center_y + self._rng.uniform(-200.0, 200.0)
        else:  # right
            x = screen_width + 50.0
            y = self._rng.uniform(0.0, screen_height)
            target_x = center_x + self._rng.uniform(-100.0, 100.0)
            target_y = center_y + self._rng.uniform(-200.0, 200.0)

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0.0:
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed
        else:
            vx = speed
            vy = 0.0

        return (x, y, vx, vy)

    def _select_archetype(self, difficulty_params: DifficultyParams) -> EnemyArchetype:
        """Select enemy archetype weighted by aggressive_ratio.

        Args:
            difficulty_params: Level difficulty configuration.

        Returns:
            AGGRESSIVE with probability aggressive_ratio, otherwise BASIC.
        """
        if self._rng.random() < difficulty_params.aggressive_ratio:
            return EnemyArchetype.AGGRESSIVE
        return EnemyArchetype.BASIC

    def reset_enemy_spawning(self) -> None:
        """Reset enemy spawn timer for a new level or combat phase start."""
        self._enemy_spawn_timer = 0.0
        self._enemy_spawn_active = True
