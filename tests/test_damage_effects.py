"""Focused tests for damage-feedback visual effects."""

from __future__ import annotations

import random
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import PhysicsConfig
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.rendering.damage_effects import DamageEffects
from asterax.app.src.rendering.particle_system import ParticleSystem

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


def _make_ship() -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=640.0,
        center_y=480.0,
        physics_config=PhysicsConfig(),
    )


def test_damage_flash_restores_original_color_after_duration() -> None:
    """Damage flash should return ship color to its pre-flash value."""
    ship = _make_ship()
    ship.color = (200, 210, 220)
    effects = DamageEffects()

    effects.trigger_damage_flash(ship)
    effects.update(0.25)

    assert tuple(ship.color)[:3] == (200, 210, 220)


def test_trigger_explosion_spawns_enemy_particle_count_in_expected_range() -> None:
    """Enemy explosion should spawn 5-10 particles per effect profile."""
    particles = arcade.SpriteList()
    effects = DamageEffects(rng=random.Random(1))

    effects.trigger_explosion((100.0, 120.0), "medium", particles)

    assert 5 <= len(particles) <= 10


def test_damage_particles_expire_after_lifetime() -> None:
    """Damage-effect particles should be removed after lifetime elapses."""
    particles = arcade.SpriteList()
    effects = DamageEffects(rng=random.Random(2))
    particle_system = ParticleSystem(particles=particles)
    effects.trigger_destruction_sequence((100.0, 120.0), particles)

    particle_system.update(1.0)

    assert len(particles) == particle_system.max_particles
    assert sum(1 for sprite in particles if sprite.alpha > 0) == 0
