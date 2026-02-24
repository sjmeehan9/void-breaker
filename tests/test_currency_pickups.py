"""Unit tests for currency pickup spawning, collection, and bookkeeping."""

from __future__ import annotations

import random
from pathlib import Path

import arcade
import pytest
from asterax.app.src.config.game_config import AsteroidSize, GameState, PhysicsConfig
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.pickups import CurrencyPickup
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.projectile import Projectile
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


class DummyEntityManager:
    """Minimal entity-manager surface required for collision tests."""

    def __init__(self, ship: PlayerShip) -> None:
        self.player_ship = ship
        self.asteroids = arcade.SpriteList(use_spatial_hash=True)
        self.player_projectiles = arcade.SpriteList()
        self.currency_pickups = arcade.SpriteList(use_spatial_hash=True)


def _make_ship(center_x: float = 640.0, center_y: float = 480.0) -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=center_x,
        center_y=center_y,
        physics_config=PhysicsConfig(),
    )


def test_currency_pickup_moves_by_drift_velocity() -> None:
    """Currency pickup should advance by velocity every update step."""
    pickup = CurrencyPickup(
        center_x=100.0,
        center_y=100.0,
        drift_speed_range=(20.0, 20.0),
        rng=random.Random(7),
    )
    start_x = pickup.center_x
    start_y = pickup.center_y

    pickup.update(0.5)

    assert (pickup.center_x, pickup.center_y) != (start_x, start_y)


def test_currency_pickup_expires_after_lifetime() -> None:
    """Pickup should remove itself once lifetime reaches zero."""
    pickup = CurrencyPickup(
        center_x=100.0,
        center_y=100.0,
        lifetime=1.0,
        drift_speed_range=(0.0, 0.0),
    )
    pickups = arcade.SpriteList()
    pickups.append(pickup)

    pickup.update(0.4)
    assert pickup in pickups

    pickup.update(0.7)
    assert pickup not in pickups


def test_currency_manager_earn_and_spend_rules() -> None:
    """Currency manager should track balance and reject overspend."""
    manager = CurrencyManager()
    manager.earn(25)

    assert manager.get_balance() == 25
    assert manager.spend(10) is True
    assert manager.get_balance() == 15
    assert manager.spend(20) is False
    assert manager.total_earned == 25
    assert manager.total_spent == 10


def test_asteroid_destruction_spawns_currency_pickup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Asteroid collision should spawn pickup when drop roll succeeds."""
    monkeypatch.setattr("asterax.app.src.physics.collisions.random.random", lambda: 0.0)
    ship = _make_ship(1000.0, 1000.0)
    entity_manager = DummyEntityManager(ship)
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(3),
    )
    projectile = Projectile(
        center_x=100.0,
        center_y=100.0,
        angle=0.0,
        speed=800.0,
        max_range=600.0,
        damage=1.0,
    )
    entity_manager.asteroids.append(asteroid)
    entity_manager.player_projectiles.append(projectile)

    CollisionSystem().check_all(
        entity_manager=entity_manager,
        game_state=GameState(),
        spawn_manager=SpawnManager(rng=random.Random(3)),
        score_manager=ScoreManager(),
        screen_width=1280.0,
        screen_height=960.0,
        currency_manager=CurrencyManager(),
    )

    assert len(entity_manager.currency_pickups) == 1


def test_ship_collects_pickups_and_earns_currency() -> None:
    """Ship contact with pickup should credit currency and remove pickup."""
    ship = _make_ship(200.0, 200.0)
    entity_manager = DummyEntityManager(ship)
    pickup = CurrencyPickup(
        center_x=200.0,
        center_y=200.0,
        value=12,
        drift_speed_range=(0.0, 0.0),
    )
    entity_manager.currency_pickups.append(pickup)
    game_state = GameState()
    currency_manager = CurrencyManager(game_state)

    CollisionSystem().check_all(
        entity_manager=entity_manager,
        game_state=game_state,
        spawn_manager=SpawnManager(rng=random.Random(9)),
        score_manager=ScoreManager(),
        screen_width=1280.0,
        screen_height=960.0,
        currency_manager=currency_manager,
    )

    assert len(entity_manager.currency_pickups) == 0
    assert game_state.currency == 12
    assert currency_manager.get_balance() == 12
