"""Phase 2 entity behavior tests for splitting and pickup expiry."""

from __future__ import annotations

import random

import arcade
from asterax.app.src.config.game_config import AsteroidSize
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.pickups import CurrencyPickup


def test_asteroid_split_large_to_medium() -> None:
    """Large asteroids should split into 2-3 medium asteroids."""
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(75.0, 25.0),
        rotation_speed=10.0,
        rng=random.Random(10),
    )
    children = asteroid.split()
    assert 2 <= len(children) <= 3
    assert all(child.asteroid_size is AsteroidSize.MEDIUM for child in children)


def test_asteroid_split_medium_to_small() -> None:
    """Medium asteroids should split into 2-3 small asteroids."""
    asteroid = Asteroid(
        size=AsteroidSize.MEDIUM,
        center_x=100.0,
        center_y=100.0,
        velocity=(75.0, 25.0),
        rotation_speed=10.0,
        rng=random.Random(11),
    )
    children = asteroid.split()
    assert 2 <= len(children) <= 3
    assert all(child.asteroid_size is AsteroidSize.SMALL for child in children)


def test_asteroid_split_small_empty() -> None:
    """Small asteroids should not split into additional children."""
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=100.0,
        center_y=100.0,
        velocity=(75.0, 25.0),
        rotation_speed=10.0,
        rng=random.Random(12),
    )
    assert asteroid.split() == []


def test_currency_pickup_timeout() -> None:
    """Currency pickup should be removed after lifetime elapses."""
    pickup = CurrencyPickup(
        center_x=100.0,
        center_y=100.0,
        lifetime=1.0,
        drift_speed_range=(0.0, 0.0),
    )
    pickups = arcade.SpriteList()
    pickups.append(pickup)
    pickup.update(0.5)
    assert pickup in pickups
    pickup.update(0.6)
    assert pickup not in pickups
