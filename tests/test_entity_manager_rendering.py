"""Unit tests for EntityManager and particle rendering helpers."""

from __future__ import annotations

import random
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import AsteroidSize, PhysicsConfig
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.managers.entity_manager import EntityManager
from asterax.app.src.rendering.particle_system import ParticleSystem

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


def _make_ship(center_x: float = 640.0, center_y: float = 480.0) -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=center_x,
        center_y=center_y,
        physics_config=PhysicsConfig(),
    )


def test_entity_manager_add_asteroid_adds_to_sprite_list() -> None:
    """add_asteroid should append asteroid to managed list."""
    manager = EntityManager()
    asteroid = Asteroid(
        size=AsteroidSize.LARGE,
        center_x=100.0,
        center_y=100.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(1),
    )

    manager.add_asteroid(asteroid)

    assert asteroid in manager.asteroids


def test_entity_manager_clear_all_empties_lists_and_player() -> None:
    """clear_all should clear all managed collections."""
    manager = EntityManager()
    manager.player = _make_ship()
    manager.asteroids.append(
        Asteroid(
            size=AsteroidSize.SMALL,
            center_x=100.0,
            center_y=100.0,
            velocity=(0.0, 0.0),
            rotation_speed=0.0,
            rng=random.Random(2),
        )
    )
    manager.player_projectiles.append(arcade.Sprite())
    manager.enemy_projectiles.append(arcade.Sprite())
    manager.currency_pickups.append(arcade.Sprite())
    manager.buff_pickups.append(arcade.Sprite())
    manager.enemies.append(arcade.Sprite())
    manager.particles.append(arcade.Sprite())

    manager.clear_all()

    assert manager.player is None
    assert len(manager.asteroids) == 0
    assert len(manager.enemies) == 0
    assert len(manager.enemy_projectiles) == 0
    assert len(manager.player_projectiles) == 0
    assert len(manager.currency_pickups) == 0
    assert len(manager.buff_pickups) == 0
    assert len(manager.particles) == 0


def test_entity_manager_draw_uses_expected_z_order() -> None:
    """draw should render asteroids, pickups, particles, enemies, then projectiles."""
    manager = EntityManager()
    manager.player = _make_ship()
    draw_calls: list[str] = []
    manager.background_renderer = type(
        "BackgroundRenderer", (), {"draw": lambda self: draw_calls.append("background")}
    )()

    manager.asteroids.draw = lambda: draw_calls.append("asteroids")  # type: ignore[method-assign]
    manager.currency_pickups.draw = (  # type: ignore[method-assign]
        lambda: draw_calls.append("pickups")
    )
    manager.buff_pickups.draw = lambda: draw_calls.append("buff_pickups")  # type: ignore[method-assign]
    manager.particles.draw = lambda: draw_calls.append("particles")  # type: ignore[method-assign]
    manager.enemies.draw = lambda: draw_calls.append("enemies")  # type: ignore[method-assign]
    manager.enemy_projectiles.draw = (  # type: ignore[method-assign]
        lambda: draw_calls.append("enemy_projectiles")
    )
    manager.player_projectiles.draw = (  # type: ignore[method-assign]
        lambda: draw_calls.append("projectiles")
    )
    manager.player.draw = lambda: draw_calls.append("ship")  # type: ignore[method-assign]

    manager.draw()

    assert draw_calls == [
        "background",
        "asteroids",
        "pickups",
        "buff_pickups",
        "particles",
        "enemies",
        "enemy_projectiles",
        "projectiles",
        "ship",
    ]


def test_entity_manager_initializes_enemy_sprite_lists() -> None:
    """Entity manager should expose enemy and enemy projectile sprite lists."""
    manager = EntityManager()

    assert isinstance(manager.enemies, arcade.SpriteList)
    assert isinstance(manager.enemy_projectiles, arcade.SpriteList)


def test_particle_system_spawn_explosion_creates_expected_particle_count() -> None:
    """Explosion particle burst count should respect configured size profile."""
    particle_system = ParticleSystem(rng=random.Random(3), max_particles=300)

    particle_system.spawn_explosion((100.0, 120.0), AsteroidSize.LARGE)

    assert particle_system.max_particles == 300
    assert particle_system.active_particle_count == 25


def test_particle_system_update_removes_expired_particles() -> None:
    """Particle update should remove particles whose lifetime has elapsed."""
    particle_system = ParticleSystem(rng=random.Random(4), max_particles=12)
    particle_system.spawn_explosion((100.0, 120.0), AsteroidSize.SMALL)

    particle_system.update(2.0)

    assert particle_system.active_particle_count == 0


def test_particle_system_preallocates_pool_and_enforces_cap() -> None:
    """Particle system should preallocate sprites and never exceed configured cap."""
    particle_system = ParticleSystem(rng=random.Random(7), max_particles=6)

    assert len(particle_system.particles) == 6

    particle_system.emit_explosion(100.0, 100.0, "large")
    assert particle_system.active_particle_count == 6


def test_particle_system_recycles_when_pool_exhausted() -> None:
    """Emitting effects beyond capacity should recycle oldest active particles."""
    particle_system = ParticleSystem(rng=random.Random(8), max_particles=5)

    particle_system.emit_explosion(10.0, 20.0, "small")
    first_positions = {
        (sprite.center_x, sprite.center_y)
        for sprite in particle_system.particles
        if sprite.alpha > 0
    }

    particle_system.emit_purchase_burst(200.0, 220.0)
    second_positions = {
        (sprite.center_x, sprite.center_y)
        for sprite in particle_system.particles
        if sprite.alpha > 0
    }

    assert particle_system.active_particle_count == 5
    assert first_positions != second_positions
