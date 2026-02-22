"""Unit tests for asteroid entities, spawning, and difficulty scaling."""

from __future__ import annotations

import math
import random

from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.game_config import AsteroidSize
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.managers.spawn_manager import SpawnManager


def test_asteroid_moves_by_velocity_and_rotates() -> None:
    """Asteroid update should apply velocity and rotation over delta time."""
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(50.0, -25.0),
        rotation_speed=40.0,
        rng=random.Random(1),
    )

    asteroid.update(2.0)

    assert asteroid.center_x == 200.0
    assert asteroid.center_y == 50.0
    assert asteroid.angle == 80.0


def test_large_asteroid_split_produces_medium_children() -> None:
    """Large asteroid should split into 2-3 medium asteroids."""
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(60.0, 80.0),
        rotation_speed=45.0,
        rng=random.Random(7),
    )

    children = asteroid.split()

    assert 2 <= len(children) <= 3
    assert all(child.asteroid_size is AsteroidSize.MEDIUM for child in children)


def test_medium_asteroid_split_produces_small_children() -> None:
    """Medium asteroid should split into 2-3 small asteroids."""
    asteroid = Asteroid(
        size=AsteroidSize.MEDIUM,
        center_x=100.0,
        center_y=100.0,
        velocity=(60.0, 80.0),
        rotation_speed=45.0,
        rng=random.Random(8),
    )

    children = asteroid.split()

    assert 2 <= len(children) <= 3
    assert all(child.asteroid_size is AsteroidSize.SMALL for child in children)


def test_small_asteroid_split_returns_no_children() -> None:
    """Small asteroids should not split further."""
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=100.0,
        center_y=100.0,
        velocity=(60.0, 80.0),
        rotation_speed=45.0,
        rng=random.Random(9),
    )

    assert asteroid.split() == []


def test_child_asteroid_velocities_respect_multiplier_range() -> None:
    """Child asteroid speed should follow configured split multipliers."""
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(100.0, 0.0),
        rotation_speed=45.0,
        rng=random.Random(11),
    )

    children = asteroid.split()

    for child in children:
        child_speed = math.hypot(child.velocity_x, child.velocity_y)
        assert 120.0 <= child_speed <= 150.0


def test_spawn_level_asteroids_respects_minimum_player_distance() -> None:
    """Initial asteroid spawns should be at least 150px from the player."""
    spawn_manager = SpawnManager(rng=random.Random(21))
    player_position = (640.0, 480.0)

    asteroids = spawn_manager.spawn_level_asteroids(
        level=3,
        player_position=player_position,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert asteroids
    for asteroid in asteroids:
        assert (
            math.dist((asteroid.center_x, asteroid.center_y), player_position) >= 150.0
        )


def test_difficulty_params_scale_across_levels_1_to_30() -> None:
    """Difficulty table should increase asteroid pressure as levels progress."""
    level_one = get_difficulty_params(1)
    level_ten = get_difficulty_params(10)
    level_thirty = get_difficulty_params(30)

    assert level_one.asteroid_count == 4
    assert level_thirty.asteroid_count <= 20
    assert (
        level_one.asteroid_count
        < level_ten.asteroid_count
        <= level_thirty.asteroid_count
    )
    assert level_one.asteroid_speed_min == 50.0
    assert level_one.asteroid_speed_max == 100.0
    assert level_one.asteroid_speed_max < level_thirty.asteroid_speed_max <= 350.0
    assert level_one.enemy_spawn_enabled is False
    assert level_ten.enemy_spawn_enabled is False
    assert level_thirty.enemy_spawn_enabled is False
