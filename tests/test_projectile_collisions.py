"""Unit tests for projectile behavior and collision resolution."""

from __future__ import annotations

import random
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import AsteroidSize, PhysicsConfig
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.projectile import Projectile
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


class DummyEntityManager:
    """Minimal entity manager used by collision tests."""

    def __init__(self, player_ship: PlayerShip) -> None:
        self.player_ship = player_ship
        self.asteroids = arcade.SpriteList(use_spatial_hash=True)
        self.player_projectiles = arcade.SpriteList()


def _make_ship(center_x: float = 640.0, center_y: float = 480.0) -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=center_x,
        center_y=center_y,
        physics_config=PhysicsConfig(),
    )


def test_projectile_moves_in_facing_direction_at_speed() -> None:
    """Projectile should move up when angle is zero."""
    projectile = Projectile(
        center_x=100.0,
        center_y=100.0,
        angle=0.0,
        speed=800.0,
        max_range=600.0,
        damage=1.0,
    )

    projectile.update(0.25)

    assert projectile.center_x == pytest.approx(100.0)
    assert projectile.center_y == 300.0


def test_projectile_expires_after_max_range() -> None:
    """Projectile should remove itself when range is exhausted."""
    projectile = Projectile(
        center_x=100.0,
        center_y=100.0,
        angle=0.0,
        speed=800.0,
        max_range=600.0,
        damage=1.0,
    )
    projectiles = arcade.SpriteList()
    projectiles.append(projectile)

    projectile.update(0.75)

    assert projectile not in projectiles


def test_fire_cooldown_prevents_rapid_firing() -> None:
    """Player ship should only fire when cooldown has elapsed."""
    ship = _make_ship()
    projectiles = arcade.SpriteList()

    first = ship.fire(projectiles)
    second = ship.fire(projectiles)
    ship.update_cooldown(0.2)
    third = ship.fire(projectiles)

    assert first is not None
    assert second is None
    assert third is not None
    assert len(projectiles) == 2


def test_projectile_asteroid_collision_destroys_and_splits_asteroid() -> None:
    """Projectile collision should destroy parent asteroid and spawn children."""
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
        100.0, 100.0, angle=0.0, speed=800.0, max_range=600.0, damage=1.0
    )
    entity_manager.asteroids.append(asteroid)
    entity_manager.player_projectiles.append(projectile)

    collision_system = CollisionSystem()
    score_manager = ScoreManager()
    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=object(),
        spawn_manager=SpawnManager(rng=random.Random(3)),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert projectile not in entity_manager.player_projectiles
    assert all(a.asteroid_size is AsteroidSize.MEDIUM for a in entity_manager.asteroids)
    assert 2 <= len(entity_manager.asteroids) <= 3
    assert score_manager.score == 20


def test_ship_asteroid_collision_reduces_shields() -> None:
    """Ship should take configured collision damage on asteroid contact."""
    ship = _make_ship(200.0, 200.0)
    entity_manager = DummyEntityManager(ship)
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=200.0,
        center_y=200.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(4),
    )
    entity_manager.asteroids.append(asteroid)

    collision_system = CollisionSystem()
    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=object(),
        spawn_manager=SpawnManager(rng=random.Random(4)),
        score_manager=ScoreManager(),
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert ship.shields == 75.0


def test_ghost_sprite_created_for_edge_entity_and_cleaned_up() -> None:
    """Entities near screen edges should produce temporary ghosts only."""
    ship = _make_ship(50.0, 50.0)
    entity_manager = DummyEntityManager(ship)
    projectile = Projectile(
        1278.0, 200.0, angle=0.0, speed=800.0, max_range=600.0, damage=1.0
    )
    entity_manager.player_projectiles.append(projectile)

    collision_system = CollisionSystem()
    ghost_projectile_map, _, _, _ = collision_system._create_ghost_sprites(
        entity_manager, 1280.0, 960.0
    )

    assert ghost_projectile_map
    collision_system._cleanup_ghost_sprites()
    assert collision_system._ghost_sprites == []


def test_edge_wrap_ghost_collision_hits_across_screen_seam() -> None:
    """Projectile near right edge should collide with asteroid near left edge via ghost."""
    ship = _make_ship(300.0, 300.0)
    entity_manager = DummyEntityManager(ship)
    projectile = Projectile(
        1279.0, 480.0, angle=90.0, speed=0.0, max_range=600.0, damage=1.0
    )
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=1.0,
        center_y=480.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(7),
    )
    entity_manager.player_projectiles.append(projectile)
    entity_manager.asteroids.append(asteroid)
    score_manager = ScoreManager()

    CollisionSystem().check_all(
        entity_manager=entity_manager,
        game_state=object(),
        spawn_manager=SpawnManager(rng=random.Random(7)),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert projectile not in entity_manager.player_projectiles
    assert asteroid not in entity_manager.asteroids
    assert score_manager.score == 100


import pytest
